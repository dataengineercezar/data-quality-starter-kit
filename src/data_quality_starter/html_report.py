"""HTML report generation for validation results."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

from data_quality_starter.result import ValidationReport


DEFAULT_REPORT_FILENAME = "validation_report.html"


def write_html_report(
    report: ValidationReport,
    output_dir: str | Path,
    *,
    filename: str = DEFAULT_REPORT_FILENAME,
    max_failure_samples: int = 5,
) -> Path:
    """Write a validation report HTML file and return its path."""

    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    report_path = directory / filename
    report_path.write_text(
        render_html_report(report, max_failure_samples=max_failure_samples),
        encoding="utf-8",
    )
    return report_path


def render_html_report(
    report: ValidationReport,
    *,
    max_failure_samples: int = 5,
) -> str:
    """Render a simple static HTML report from a validation report."""

    payload = report.to_dict()
    summary = payload["summary"]
    results = payload["results"]
    status_class = "passed" if summary["passed"] else "failed"

    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="utf-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1">',
            f"  <title>Data Quality Report - {_text(payload['dataset'])}</title>",
            f"  <style>{_css()}</style>",
            "</head>",
            "<body>",
            '  <main class="page">',
            "    <header>",
            "      <p>Data Quality Starter Kit</p>",
            f"      <h1>{_text(payload['dataset'])} validation report</h1>",
            f'      <span class="status {status_class}">{_text(summary["status"])}</span>',
            "    </header>",
            _render_executive_summary(payload),
            _render_severity_summary(summary),
            _render_results(results, max_failure_samples=max_failure_samples),
            "  </main>",
            "</body>",
            "</html>",
        ]
    )


def _render_executive_summary(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    cards = [
        ("Data file", payload["data_path"]),
        ("Rows", summary["total_rows"]),
        ("Columns", summary["total_columns"]),
        ("Checks", summary["total_checks"]),
        ("Passed checks", summary["passed_checks"]),
        ("Failed checks", summary["failed_checks"]),
        ("Total failures", summary["total_failures"]),
    ]
    return "\n".join(
        [
            '    <section class="summary">',
            "      <h2>Executive summary</h2>",
            '      <div class="summary-grid">',
            *[
                (
                    '        <div class="metric">'
                    f"<span>{_text(label)}</span>"
                    f"<strong>{_text(value)}</strong>"
                    "</div>"
                )
                for label, value in cards
            ],
            "      </div>",
            "    </section>",
        ]
    )


def _render_severity_summary(summary: dict[str, Any]) -> str:
    return "\n".join(
        [
            '    <section class="severity">',
            "      <h2>Severity summary</h2>",
            '      <div class="severity-grid">',
            "        <div>",
            "          <h3>Failed checks by severity</h3>",
            _render_count_list(summary["failed_checks_by_severity"]),
            "        </div>",
            "        <div>",
            "          <h3>Failures by severity</h3>",
            _render_count_list(summary["failures_by_severity"]),
            "        </div>",
            "      </div>",
            "    </section>",
        ]
    )


def _render_results(results: list[dict[str, Any]], *, max_failure_samples: int) -> str:
    rows = []
    for result in results:
        rows.extend(
            [
                "        <tr>",
                f"          <td>{_text(result['name'])}</td>",
                f"          <td>{_text(result['type'])}</td>",
                f"          <td>{_text(result['severity'])}</td>",
                f'          <td><span class="status {result["status"]}">{_text(result["status"])}</span></td>',
                f"          <td>{_text(result['failure_count'])}</td>",
                "        </tr>",
            ]
        )

    failures = []
    for result in results:
        if not result["failures"]:
            continue
        failures.extend(
            [
                '      <div class="check-failures">',
                f"        <h3>{_text(result['name'])}</h3>",
                "        <ul>",
                *[
                    (
                        "          <li>"
                        f"<strong>{_text(_failure_location(failure))}</strong>"
                        f" {_text(_failure_value(failure))}"
                        f" - {_text(failure['message'])}"
                        "</li>"
                    )
                    for failure in result["failures"][:max_failure_samples]
                ],
                "        </ul>",
                "      </div>",
            ]
        )

    if not failures:
        failures = ['      <p class="empty">No validation failures found.</p>']

    return "\n".join(
        [
            '    <section class="checks">',
            "      <h2>Check results</h2>",
            "      <table>",
            "        <thead>",
            "          <tr><th>Name</th><th>Type</th><th>Severity</th><th>Status</th><th>Failures</th></tr>",
            "        </thead>",
            "        <tbody>",
            *rows,
            "        </tbody>",
            "      </table>",
            "    </section>",
            '    <section class="failures">',
            "      <h2>Failure samples</h2>",
            *failures,
            "    </section>",
        ]
    )


def _render_count_list(counts: dict[str, int]) -> str:
    if not counts:
        return '          <p class="empty">None</p>'

    items = [
        f"            <li><span>{_text(key)}</span><strong>{_text(value)}</strong></li>"
        for key, value in sorted(counts.items())
    ]
    return "\n".join(["          <ul>", *items, "          </ul>"])


def _failure_location(failure: dict[str, Any]) -> str:
    parts = []
    if failure["row_number"] is not None:
        parts.append(f"row {failure['row_number']}")
    if failure["column"] is not None:
        parts.append(f"column {failure['column']}")
    return ", ".join(parts) if parts else "config"


def _failure_value(failure: dict[str, Any]) -> str:
    if failure["value"] is None:
        return ""
    return f"value={failure['value']!r}"


def _text(value: Any) -> str:
    return escape("" if value is None else str(value))


def _css() -> str:
    return """
    :root {
      color-scheme: light;
      --bg: #f6f7f9;
      --panel: #ffffff;
      --text: #1f2933;
      --muted: #657080;
      --border: #d9dee7;
      --passed: #167a3d;
      --failed: #b42318;
      --soft-passed: #e8f5ee;
      --soft-failed: #fdecec;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: Arial, Helvetica, sans-serif;
      line-height: 1.5;
    }
    .page {
      max-width: 1080px;
      margin: 0 auto;
      padding: 32px 20px 48px;
    }
    header, section {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 16px;
    }
    header p {
      margin: 0 0 4px;
      color: var(--muted);
      font-size: 14px;
    }
    h1, h2, h3 { margin: 0; }
    h1 { font-size: 30px; }
    h2 { font-size: 20px; margin-bottom: 16px; }
    h3 { font-size: 16px; margin-bottom: 8px; }
    .status {
      display: inline-block;
      margin-top: 12px;
      padding: 4px 10px;
      border-radius: 999px;
      font-size: 13px;
      font-weight: 700;
      text-transform: uppercase;
    }
    .status.passed {
      background: var(--soft-passed);
      color: var(--passed);
    }
    .status.failed {
      background: var(--soft-failed);
      color: var(--failed);
    }
    .summary-grid, .severity-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 12px;
    }
    .metric {
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 12px;
      min-width: 0;
    }
    .metric span {
      display: block;
      color: var(--muted);
      font-size: 13px;
    }
    .metric strong {
      display: block;
      margin-top: 4px;
      overflow-wrap: anywhere;
      font-size: 18px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }
    th, td {
      border-bottom: 1px solid var(--border);
      padding: 10px;
      text-align: left;
      vertical-align: top;
    }
    th {
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
    }
    ul { margin: 0; padding-left: 20px; }
    .severity li {
      display: flex;
      justify-content: space-between;
      gap: 16px;
      max-width: 260px;
      padding: 4px 0;
    }
    .check-failures {
      border-top: 1px solid var(--border);
      padding-top: 12px;
      margin-top: 12px;
    }
    .empty { color: var(--muted); margin: 0; }
    @media (max-width: 700px) {
      .page { padding: 20px 12px 36px; }
      h1 { font-size: 24px; }
      table { display: block; overflow-x: auto; }
    }
    """
