"""Tests for HTML report generation."""

from __future__ import annotations

from datetime import date
from pathlib import Path
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from data_quality_starter.config import load_config  # noqa: E402
from data_quality_starter.csv_file import read_csv  # noqa: E402
from data_quality_starter.html_report import render_html_report, write_html_report  # noqa: E402
from data_quality_starter.validator import validate_dataset  # noqa: E402


CONFIG_PATH = PROJECT_ROOT / "configs" / "customers.json"
ERROR_CSV_PATH = PROJECT_ROOT / "examples" / "customers_with_errors.csv"


def _error_report():
    return validate_dataset(
        load_config(CONFIG_PATH),
        read_csv(ERROR_CSV_PATH),
        today=date(2026, 6, 7),
    )


class HtmlReportTests(unittest.TestCase):
    def test_render_html_report_contains_summary_checks_and_failures(self) -> None:
        html = render_html_report(_error_report(), max_failure_samples=1)

        self.assertIn("<!doctype html>", html)
        self.assertIn("customers validation report", html)
        self.assertIn("Executive summary", html)
        self.assertIn("Check results", html)
        self.assertIn("Failure samples", html)
        self.assertIn("critical_fields_not_null", html)

    def test_write_html_report_creates_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = write_html_report(_error_report(), temp_dir)
            html = report_path.read_text(encoding="utf-8")

        self.assertEqual(report_path.name, "validation_report.html")
        self.assertIn("Severity summary", html)


if __name__ == "__main__":
    unittest.main()
