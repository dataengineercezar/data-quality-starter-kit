"""Tests for CLI behavior."""

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from data_quality_starter.cli import main  # noqa: E402


CONFIG_PATH = PROJECT_ROOT / "configs" / "customers.json"
VALID_CSV_PATH = PROJECT_ROOT / "examples" / "customers_valid.csv"
ERROR_CSV_PATH = PROJECT_ROOT / "examples" / "customers_with_errors.csv"


def _run_cli(args: list[str]) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        code = main(args)
    return code, stdout.getvalue(), stderr.getvalue()


class CliTests(unittest.TestCase):
    def test_validate_json_output_is_parseable(self) -> None:
        code, stdout, stderr = _run_cli(
            [
                "validate",
                "--data",
                str(ERROR_CSV_PATH),
                "--config",
                str(CONFIG_PATH),
                "--format",
                "json",
                "--today",
                "2026-06-07",
            ]
        )

        payload = json.loads(stdout)

        self.assertEqual(code, 1)
        self.assertEqual(stderr, "")
        self.assertEqual(payload["summary"]["status"], "failed")
        self.assertEqual(payload["summary"]["failed_checks"], 6)

    def test_validate_writes_html_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            code, stdout, stderr = _run_cli(
                [
                    "validate",
                    "--data",
                    str(VALID_CSV_PATH),
                    "--config",
                    str(CONFIG_PATH),
                    "--report-dir",
                    temp_dir,
                    "--today",
                    "2026-06-07",
                ]
            )
            report_path = Path(temp_dir) / "validation_report.html"

            self.assertEqual(code, 0)
            self.assertIn("HTML report:", stdout)
            self.assertEqual(stderr, "")
            self.assertTrue(report_path.exists())
            self.assertIn("Executive summary", report_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
