"""Tests for validation config loading."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from data_quality_starter.config import load_config  # noqa: E402


class ConfigTests(unittest.TestCase):
    def test_loads_customer_config(self) -> None:
        config = load_config(PROJECT_ROOT / "configs" / "customers.json")

        self.assertEqual(config.dataset, "customers")
        self.assertEqual(config.file_type, "csv")
        self.assertIn("customer_id", config.required_columns)
        self.assertEqual(len(config.rules), 7)

    def test_rejects_config_missing_required_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "invalid.json"
            config_path.write_text(json.dumps({"dataset": "customers"}), encoding="utf-8")

            with self.assertRaises(ValueError):
                load_config(config_path)


if __name__ == "__main__":
    unittest.main()
