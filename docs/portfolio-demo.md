# Portfolio Demo: Data Quality Starter Kit

## One-Line Pitch

Data Quality Starter Kit is a small Python project that validates customer CSV files with configurable rules and generates a simple report that business and technical users can read.

## Business Problem

Small teams often depend on CSV exports from CRM, ERP, spreadsheets or manual tools before running campaigns, reports and operational analysis. Without repeatable data quality checks, duplicated customers, invalid emails, missing fields and future dates can silently distort decisions.

## Demo Scenario

The demo validates a customer file before it is used by marketing, operations or management.

Demo inputs:

- `examples/customers_valid.csv`: clean customer CSV.
- `examples/customers_with_errors.csv`: customer CSV with realistic quality issues.
- `configs/customers.json`: validation rules for required columns, nulls, email format, accepted values, numeric range, uniqueness and future dates.

Generated output:

- `docs/demo-output/validation_report.html`

## How To Run The Demo

From the project root:

```powershell
$env:PYTHONPATH = "src"
python -B -m unittest discover -s tests -v
python -m data_quality_starter validate --data examples/customers_valid.csv --config configs/customers.json
python -m data_quality_starter validate --data examples/customers_with_errors.csv --config configs/customers.json --report-dir docs/demo-output --today 2026-06-07
python -m data_quality_starter validate --data examples/customers_with_errors.csv --config configs/customers.json --format json --today 2026-06-07
```

## Observed Result

The valid file passes all 7 configured checks with 0 failures.

The file with errors fails 6 checks and reports 10 total failures:

- missing critical fields;
- invalid email format;
- invalid status value;
- age outside the expected range;
- duplicated customer ID;
- future signup date.

The HTML report includes:

- executive summary;
- check results;
- severity summary;
- failure samples with row, column, value and message.

Demo visual:

- `docs/demo-output/validation_report.png`

![Data Quality Starter Kit report](demo-output/validation_report.png)

## Portfolio Narrative

This project shows how a small data engineering utility can turn an informal spreadsheet review into a repeatable quality gate. The implementation is intentionally lightweight: it uses Python standard library only, reads configurable JSON rules, validates CSV files, returns structured results, supports JSON output, generates an HTML report and includes automated tests.

The business value is speed and confidence. A team can see whether a file is safe enough to use before it feeds reports, campaigns or downstream analysis.

## Current MVP Boundaries

This is a local-first MVP. It does not connect to databases, cloud storage, orchestration tools or paid services. It focuses on a narrow CSV workflow that is easy to inspect, test and explain.

## Improvements Before Publication

- Decide whether to initialize Git locally before publishing.
- Add repository metadata after Git is initialized.
- Publish only after explicit approval.
