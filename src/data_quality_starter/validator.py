"""Validation engine for configured CSV quality checks."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
import re
from typing import Any, Callable

from data_quality_starter.config import ValidationConfig
from data_quality_starter.csv_file import CsvDataset
from data_quality_starter.result import (
    ValidationFailure,
    ValidationReport,
    ValidationResult,
)


RuleHandler = Callable[[dict[str, Any], CsvDataset], ValidationResult]
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_dataset(
    config: ValidationConfig,
    dataset: CsvDataset,
    *,
    today: date | None = None,
) -> ValidationReport:
    """Run configured validation rules against a CSV dataset."""

    context = _ValidationContext(config=config, dataset=dataset, today=today or date.today())
    results = [context.validate_rule(rule) for rule in config.rules]
    return ValidationReport(
        dataset=config.dataset,
        data_path=dataset.path,
        total_rows=dataset.row_count,
        total_columns=len(dataset.columns),
        results=results,
    )


class _ValidationContext:
    def __init__(self, config: ValidationConfig, dataset: CsvDataset, today: date) -> None:
        self.config = config
        self.dataset = dataset
        self.today = today
        self.handlers: dict[str, RuleHandler] = {
            "required_columns": self._required_columns,
            "not_null": self._not_null,
            "email_format": self._email_format,
            "accepted_values": self._accepted_values,
            "numeric_range": self._numeric_range,
            "unique": self._unique,
            "not_future_date": self._not_future_date,
        }

    def validate_rule(self, rule: dict[str, Any]) -> ValidationResult:
        rule_type = str(rule["type"])
        handler = self.handlers.get(rule_type)
        if handler is None:
            return self._result(
                rule,
                [
                    ValidationFailure(
                        message=f"Unsupported rule type: {rule_type}",
                    )
                ],
            )

        return handler(rule, self.dataset)

    def _required_columns(
        self,
        rule: dict[str, Any],
        dataset: CsvDataset,
    ) -> ValidationResult:
        columns = _string_list(rule, "columns", fallback=self.config.required_columns)
        missing_columns = [column for column in columns if column not in dataset.columns]
        failures = [
            ValidationFailure(
                message="Required column is missing.",
                column=column,
            )
            for column in missing_columns
        ]
        return self._result(rule, failures)

    def _not_null(
        self,
        rule: dict[str, Any],
        dataset: CsvDataset,
    ) -> ValidationResult:
        columns = _string_list(rule, "columns")
        failures = self._missing_column_failures(columns)

        for row_number, row in dataset.iter_rows_with_numbers():
            for column in columns:
                if column not in dataset.columns:
                    continue
                value = row.get(column)
                if _is_blank(value):
                    failures.append(
                        ValidationFailure(
                            message="Value is required.",
                            row_number=row_number,
                            column=column,
                            value=value,
                        )
                    )

        return self._result(rule, failures)

    def _email_format(
        self,
        rule: dict[str, Any],
        dataset: CsvDataset,
    ) -> ValidationResult:
        column = _string(rule, "column")
        failures = self._missing_column_failures([column])
        if failures:
            return self._result(rule, failures)

        for row_number, row in dataset.iter_rows_with_numbers():
            value = row.get(column, "")
            if not EMAIL_PATTERN.match(value or ""):
                failures.append(
                    ValidationFailure(
                        message="Email value has an invalid format.",
                        row_number=row_number,
                        column=column,
                        value=value,
                    )
                )

        return self._result(rule, failures)

    def _accepted_values(
        self,
        rule: dict[str, Any],
        dataset: CsvDataset,
    ) -> ValidationResult:
        column = _string(rule, "column")
        accepted_values = set(_string_list(rule, "values"))
        failures = self._missing_column_failures([column])
        if failures:
            return self._result(rule, failures)

        for row_number, row in dataset.iter_rows_with_numbers():
            value = row.get(column, "")
            if value not in accepted_values:
                failures.append(
                    ValidationFailure(
                        message=f"Value must be one of: {', '.join(sorted(accepted_values))}.",
                        row_number=row_number,
                        column=column,
                        value=value,
                    )
                )

        return self._result(rule, failures)

    def _numeric_range(
        self,
        rule: dict[str, Any],
        dataset: CsvDataset,
    ) -> ValidationResult:
        column = _string(rule, "column")
        minimum = _number(rule, "min")
        maximum = _number(rule, "max")
        failures = self._missing_column_failures([column])
        if failures:
            return self._result(rule, failures)

        for row_number, row in dataset.iter_rows_with_numbers():
            raw_value = row.get(column, "")
            try:
                value = float(raw_value)
            except (TypeError, ValueError):
                failures.append(
                    ValidationFailure(
                        message="Value must be numeric.",
                        row_number=row_number,
                        column=column,
                        value=raw_value,
                    )
                )
                continue

            if value < minimum or value > maximum:
                failures.append(
                    ValidationFailure(
                        message=f"Value must be between {minimum:g} and {maximum:g}.",
                        row_number=row_number,
                        column=column,
                        value=raw_value,
                    )
                )

        return self._result(rule, failures)

    def _unique(
        self,
        rule: dict[str, Any],
        dataset: CsvDataset,
    ) -> ValidationResult:
        column = _string(rule, "column")
        failures = self._missing_column_failures([column])
        if failures:
            return self._result(rule, failures)

        first_seen_by_value: dict[str, int] = {}
        duplicate_rows_by_value: dict[str, list[int]] = defaultdict(list)
        for row_number, row in dataset.iter_rows_with_numbers():
            value = row.get(column, "")
            if _is_blank(value):
                continue
            if value in first_seen_by_value:
                duplicate_rows_by_value[value].append(row_number)
            else:
                first_seen_by_value[value] = row_number

        for value, duplicate_rows in duplicate_rows_by_value.items():
            first_row = first_seen_by_value[value]
            for row_number in duplicate_rows:
                failures.append(
                    ValidationFailure(
                        message=f"Duplicate value first seen on row {first_row}.",
                        row_number=row_number,
                        column=column,
                        value=value,
                    )
                )

        return self._result(rule, failures)

    def _not_future_date(
        self,
        rule: dict[str, Any],
        dataset: CsvDataset,
    ) -> ValidationResult:
        column = _string(rule, "column")
        date_format = _string(rule, "date_format")
        failures = self._missing_column_failures([column])
        if date_format != "YYYY-MM-DD":
            failures.append(
                ValidationFailure(
                    message="Only YYYY-MM-DD date format is supported.",
                    column=column,
                )
            )
            return self._result(rule, failures)

        if failures:
            return self._result(rule, failures)

        for row_number, row in dataset.iter_rows_with_numbers():
            raw_value = row.get(column, "")
            try:
                parsed_date = date.fromisoformat(raw_value)
            except (TypeError, ValueError):
                failures.append(
                    ValidationFailure(
                        message="Value must be a valid YYYY-MM-DD date.",
                        row_number=row_number,
                        column=column,
                        value=raw_value,
                    )
                )
                continue

            if parsed_date > self.today:
                failures.append(
                    ValidationFailure(
                        message=f"Date must not be after {self.today.isoformat()}.",
                        row_number=row_number,
                        column=column,
                        value=raw_value,
                    )
                )

        return self._result(rule, failures)

    def _missing_column_failures(self, columns: list[str]) -> list[ValidationFailure]:
        return [
            ValidationFailure(
                message="Configured column is missing from the CSV file.",
                column=column,
            )
            for column in columns
            if column not in self.dataset.columns
        ]

    def _result(
        self,
        rule: dict[str, Any],
        failures: list[ValidationFailure],
    ) -> ValidationResult:
        return ValidationResult(
            name=str(rule["name"]),
            rule_type=str(rule["type"]),
            severity=str(rule["severity"]),
            total_rows=self.dataset.row_count,
            failures=failures,
        )


def _string(rule: dict[str, Any], key: str) -> str:
    value = rule.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"Rule '{rule['name']}' field '{key}' must be a non-empty string.")
    return value


def _string_list(
    rule: dict[str, Any],
    key: str,
    *,
    fallback: list[str] | None = None,
) -> list[str]:
    value = rule.get(key, fallback)
    if not isinstance(value, list) or not value:
        raise ValueError(f"Rule '{rule['name']}' field '{key}' must be a non-empty list.")

    if not all(isinstance(item, str) and item for item in value):
        raise ValueError(f"Rule '{rule['name']}' field '{key}' must contain strings.")

    return list(value)


def _number(rule: dict[str, Any], key: str) -> float:
    value = rule.get(key)
    if not isinstance(value, int | float):
        raise ValueError(f"Rule '{rule['name']}' field '{key}' must be numeric.")
    return float(value)


def _is_blank(value: str | None) -> bool:
    return value is None or value.strip() == ""
