"""Validation result models."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ValidationFailure:
    """A single validation failure."""

    message: str
    row_number: int | None = None
    column: str | None = None
    value: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable failure representation."""

        return {
            "row_number": self.row_number,
            "column": self.column,
            "value": self.value,
            "message": self.message,
        }


@dataclass(frozen=True)
class ValidationResult:
    """Result for one configured validation rule."""

    name: str
    rule_type: str
    severity: str
    total_rows: int
    failures: list[ValidationFailure] = field(default_factory=list)

    @property
    def status(self) -> str:
        """Return pass/fail status."""

        return "failed" if self.failures else "passed"

    @property
    def failure_count(self) -> int:
        """Return the number of failures."""

        return len(self.failures)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable check result representation."""

        return {
            "name": self.name,
            "type": self.rule_type,
            "severity": self.severity,
            "status": self.status,
            "total_rows": self.total_rows,
            "failure_count": self.failure_count,
            "failures": [failure.to_dict() for failure in self.failures],
        }


@dataclass(frozen=True)
class ValidationReport:
    """Validation report for a dataset/file pair."""

    dataset: str
    data_path: Path
    total_rows: int
    total_columns: int
    results: list[ValidationResult]

    @property
    def status(self) -> str:
        """Return report-level pass/fail status."""

        return "passed" if self.passed else "failed"

    @property
    def passed(self) -> bool:
        """Return whether all checks passed."""

        return all(result.status == "passed" for result in self.results)

    @property
    def failed_results(self) -> list[ValidationResult]:
        """Return only failed check results."""

        return [result for result in self.results if result.status == "failed"]

    @property
    def failed_check_count(self) -> int:
        """Return the number of failed checks."""

        return len(self.failed_results)

    @property
    def passed_check_count(self) -> int:
        """Return the number of passed checks."""

        return len(self.results) - self.failed_check_count

    @property
    def total_check_count(self) -> int:
        """Return the number of executed checks."""

        return len(self.results)

    @property
    def total_failure_count(self) -> int:
        """Return the total number of validation failures."""

        return sum(result.failure_count for result in self.results)

    @property
    def failed_checks_by_severity(self) -> dict[str, int]:
        """Return failed check counts grouped by severity."""

        counts: dict[str, int] = {}
        for result in self.failed_results:
            counts[result.severity] = counts.get(result.severity, 0) + 1
        return counts

    @property
    def failures_by_severity(self) -> dict[str, int]:
        """Return validation failure counts grouped by severity."""

        counts: dict[str, int] = {}
        for result in self.failed_results:
            counts[result.severity] = counts.get(result.severity, 0) + result.failure_count
        return counts

    def summary(self) -> dict[str, Any]:
        """Return a compact JSON-serializable report summary."""

        return {
            "status": self.status,
            "passed": self.passed,
            "total_rows": self.total_rows,
            "total_columns": self.total_columns,
            "total_checks": self.total_check_count,
            "passed_checks": self.passed_check_count,
            "failed_checks": self.failed_check_count,
            "total_failures": self.total_failure_count,
            "failed_checks_by_severity": self.failed_checks_by_severity,
            "failures_by_severity": self.failures_by_severity,
        }

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable validation report."""

        return {
            "dataset": self.dataset,
            "data_path": str(self.data_path),
            "summary": self.summary(),
            "results": [result.to_dict() for result in self.results],
        }
