"""Command line interface for the data quality starter kit."""

from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import sys
from typing import Sequence

from data_quality_starter.config import load_config
from data_quality_starter.csv_file import read_csv
from data_quality_starter.html_report import write_html_report
from data_quality_starter.result import ValidationReport
from data_quality_starter.validator import validate_dataset


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""

    parser = argparse.ArgumentParser(
        prog="data-quality-starter",
        description="Validate CSV files with configurable data quality rules.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser(
        "validate",
        help="Load CSV and config inputs for a future validation run.",
    )
    validate_parser.add_argument("--data", required=True, type=Path, help="Path to a CSV file.")
    validate_parser.add_argument(
        "--config",
        required=True,
        type=Path,
        help="Path to a JSON validation config.",
    )
    validate_parser.add_argument(
        "--max-samples",
        type=int,
        default=3,
        help="Maximum failure samples to print per failed check.",
    )
    validate_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    validate_parser.add_argument(
        "--report-dir",
        type=Path,
        help="Optional directory where an HTML report will be written.",
    )
    validate_parser.add_argument(
        "--report-max-samples",
        type=int,
        default=5,
        help="Maximum failure samples to include per failed check in the HTML report.",
    )
    validate_parser.add_argument(
        "--today",
        type=_parse_date,
        help="Reference date for date-based checks, in YYYY-MM-DD format.",
    )
    validate_parser.set_defaults(handler=handle_validate)

    return parser


def handle_validate(args: argparse.Namespace) -> int:
    """Handle the validate command skeleton."""

    try:
        config = load_config(args.config)
        dataset = read_csv(args.data)
        report = validate_dataset(config, dataset, today=args.today)
        report_path = None
        if args.report_dir:
            report_path = write_html_report(
                report,
                args.report_dir,
                max_failure_samples=args.report_max_samples,
            )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        _print_json_report(report)
    else:
        _print_report(report, max_samples=args.max_samples)

    if report_path is not None:
        output = sys.stderr if args.format == "json" else sys.stdout
        print(f"HTML report: {report_path}", file=output)

    return 0 if report.passed else 1


def _print_json_report(report: ValidationReport) -> None:
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))


def _print_report(report: ValidationReport, *, max_samples: int) -> None:
    print("Data Quality Starter Kit")
    print(f"Dataset: {report.dataset}")
    print(f"Data file: {report.data_path}")
    print(f"Rows: {report.total_rows}")
    print(f"Columns: {report.total_columns}")
    print(f"Checks: {report.total_check_count}")
    print(f"Status: {report.status}")
    print(f"Failed checks: {report.failed_check_count}")
    print(f"Total failures: {report.total_failure_count}")

    for result in report.results:
        print(
            f"- [{result.status.upper()}] {result.name} "
            f"({result.severity}, {result.rule_type}) "
            f"failures={result.failure_count}"
        )
        for failure in result.failures[:max_samples]:
            location = _format_location(failure.row_number, failure.column)
            value = f" value={failure.value!r}" if failure.value is not None else ""
            print(f"  - {location}{value}: {failure.message}")


def _format_location(row_number: int | None, column: str | None) -> str:
    parts = []
    if row_number is not None:
        parts.append(f"row {row_number}")
    if column is not None:
        parts.append(f"column {column}")
    return ", ".join(parts) if parts else "config"


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a valid date in YYYY-MM-DD format") from exc


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI."""

    parser = build_parser()
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
