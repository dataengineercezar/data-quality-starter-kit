"""Configuration loading for the data quality starter kit."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ValidationConfig:
    """Parsed validation configuration."""

    dataset: str
    description: str
    file_type: str
    required_columns: list[str]
    rules: list[dict[str, Any]]


def load_config(config_path: str | Path) -> ValidationConfig:
    """Load a validation config from a JSON file."""

    path = Path(config_path)
    if not path.is_file():
        raise FileNotFoundError(f"Config file not found: {path}")

    with path.open("r", encoding="utf-8") as config_file:
        payload = json.load(config_file)

    if not isinstance(payload, dict):
        raise ValueError("Config file must contain a JSON object.")

    dataset = _required_string(payload, "dataset")
    description = _required_string(payload, "description")
    file_type = _required_string(payload, "file_type")
    required_columns = _required_string_list(payload, "required_columns")
    rules = _required_rule_list(payload, "rules")

    return ValidationConfig(
        dataset=dataset,
        description=description,
        file_type=file_type,
        required_columns=required_columns,
        rules=rules,
    )


def _required_string(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"Config field '{key}' must be a non-empty string.")
    return value


def _required_string_list(payload: dict[str, Any], key: str) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"Config field '{key}' must be a non-empty list.")

    if not all(isinstance(item, str) and item for item in value):
        raise ValueError(f"Config field '{key}' must contain only non-empty strings.")

    return list(value)


def _required_rule_list(payload: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = payload.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"Config field '{key}' must be a non-empty list.")

    rules: list[dict[str, Any]] = []
    for index, rule in enumerate(value, start=1):
        if not isinstance(rule, dict):
            raise ValueError(f"Rule {index} must be a JSON object.")

        for field in ("name", "type", "severity"):
            if not isinstance(rule.get(field), str) or not rule[field]:
                raise ValueError(f"Rule {index} field '{field}' must be a non-empty string.")

        rules.append(dict(rule))

    return rules
