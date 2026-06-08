"""Tests for CSV validation behavior and report serialization."""

from __future__ import annotations

from datetime import date
import json
from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from data_quality_starter.config import load_config  # noqa: E402
from data_quality_starter.csv_file import read_csv  # noqa: E402
from data_quality_starter.validator import validate_dataset  # noqa: E402


CONFIG_PATH = PROJECT_ROOT / "configs" / "customers.json"
VALID_CSV_PATH = PROJECT_ROOT / "examples" / "customers_valid.csv"
ERROR_CSV_PATH = PROJECT_ROOT / "examples" / "customers_with_errors.csv"
FIXED_TODAY = date(2026, 6, 7)


def _validate(path: Path):
    return validate_dataset(
        load_config(CONFIG_PATH),
        read_csv(path),
        today=FIXED_TODAY,
    )


class ValidationTests(unittest.TestCase):
    def test_valid_customer_file_passes_all_checks(self) -> None:
        report = _validate(VALID_CSV_PATH)

        self.assertTrue(report.passed)
        self.assertEqual(report.status, "passed")
        self.assertEqual(report.total_check_count, 7)
        self.assertEqual(report.failed_check_count, 0)
        self.assertEqual(report.total_failure_count, 0)

    def test_customer_file_with_errors_reports_expected_failures(self) -> None:
        report = _validate(ERROR_CSV_PATH)
        failed_names = {result.name for result in report.failed_results}

        self.assertFalse(report.passed)
        self.assertEqual(report.status, "failed")
        self.assertEqual(report.failed_check_count, 6)
        self.assertEqual(report.total_failure_count, 10)
        self.assertIn("critical_fields_not_null", failed_names)
        self.assertIn("email_has_valid_format", failed_names)
        self.assertIn("status_is_accepted", failed_names)
        self.assertIn("age_is_within_expected_range", failed_names)
        self.assertIn("customer_id_is_unique", failed_names)
        self.assertIn("signup_date_is_not_future", failed_names)

    def test_report_to_dict_is_json_serializable(self) -> None:
        report = _validate(ERROR_CSV_PATH)
        payload = report.to_dict()

        json.dumps(payload)

        self.assertEqual(payload["dataset"], "customers")
        self.assertEqual(payload["summary"]["status"], "failed")
        self.assertEqual(payload["summary"]["failed_checks_by_severity"]["critical"], 2)
        self.assertEqual(payload["summary"]["failures_by_severity"]["high"], 4)
        self.assertEqual(payload["results"][1]["failures"][0]["column"], "full_name")


if __name__ == "__main__":
    unittest.main()
