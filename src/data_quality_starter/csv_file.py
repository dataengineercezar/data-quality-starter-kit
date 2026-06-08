"""CSV file inspection helpers."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CsvDataset:
    """CSV data loaded from disk."""

    path: Path
    columns: list[str]
    rows: list[dict[str, str]]

    @property
    def row_count(self) -> int:
        """Return the number of data rows."""

        return len(self.rows)

    def iter_rows_with_numbers(self) -> list[tuple[int, dict[str, str]]]:
        """Return rows with their source file line numbers."""

        return list(enumerate(self.rows, start=2))


@dataclass(frozen=True)
class CsvSummary:
    """Basic information about a CSV file."""

    path: Path
    columns: list[str]
    row_count: int


def inspect_csv(data_path: str | Path) -> CsvSummary:
    """Read a CSV header and count data rows without applying quality rules."""

    dataset = read_csv(data_path)
    return CsvSummary(
        path=dataset.path,
        columns=dataset.columns,
        row_count=dataset.row_count,
    )


def read_csv(data_path: str | Path) -> CsvDataset:
    """Read a CSV file into a small in-memory dataset."""

    path = Path(data_path)
    if not path.is_file():
        raise FileNotFoundError(f"CSV file not found: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as data_file:
        reader = csv.DictReader(data_file)
        if reader.fieldnames is None:
            raise ValueError(f"CSV file has no header row: {path}")

        columns = list(reader.fieldnames)
        rows = [dict(row) for row in reader]

    if not columns:
        raise ValueError(f"CSV file has no columns: {path}")

    return CsvDataset(path=path, columns=columns, rows=rows)
