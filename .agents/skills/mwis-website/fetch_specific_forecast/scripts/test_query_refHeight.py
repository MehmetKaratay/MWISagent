# Copyright (c) 2026 Mehmet Rahmi Karatay
# Licensed under the MIT License.

"""Unit tests for the query_refHeight.py CLI tool."""

import unittest
import os
import tempfile
import subprocess
import json
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_PATH = os.path.join(SCRIPT_DIR, 'query_refHeight.py')
PYTHON_EXE = sys.executable

class TestQueryRefHeightCLI(unittest.TestCase):
    """Test suite verifying CLI execution of query_refHeight.py."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.csv_path = os.path.join(self.temp_dir.name, "test-regions.csv")
        with open(self.csv_path, "w", encoding="utf-8") as f:
            f.write("RegionCode,RegionName,RefHeight,FLorValley,Country,Url\n")
            f.write("NW,North West Highlands,900m,FL,Scotland,https://mwis.org.uk/forecasts/scottish/the-northwest-highlands/text\n")
            f.write("WH,West Highlands,900m,FL,Scotland,https://mwis.org.uk/forecasts/scottish/west-highlands/text\n")
            f.write("PD,Peak District,600m,Valley,England,https://mwis.org.uk/forecasts/english/the-peak-district/text\n")

    def tearDown(self):
        self.temp_dir.cleanup()

    def run_cli(self, query, csv_path=None):
        path = csv_path if csv_path is not None else self.csv_path
        cmd = [PYTHON_EXE, SCRIPT_PATH, query, path]
        return subprocess.run(cmd, capture_output=True, text=True, timeout=5)

    def test_valid_region_code_returns_json(self):
        """Verify query with valid code returns correct JSON and exit 0."""
        res = self.run_cli("WH")
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout.strip())
        self.assertEqual(data, {"RefHeight": "900m"})

    def test_valid_region_name_case_insensitive(self):
        """Verify query with region name is case-insensitive."""
        res = self.run_cli("peak district")
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout.strip())
        self.assertEqual(data, {"RefHeight": "600m"})

    def test_invalid_region_exits_with_error(self):
        """Verify query for non-existent region exits with 1 and logs to stderr."""
        res = self.run_cli("InvalidRegion")
        self.assertEqual(res.returncode, 1)
        self.assertIn("Error:", res.stderr)

    def test_empty_query_exits_with_error(self):
        """Verify query with empty string exits with 1."""
        res = self.run_cli("")
        self.assertEqual(res.returncode, 1)
        self.assertIn("Error:", res.stderr)

    def test_missing_csv_file_exits_with_error(self):
        """Verify missing CSV path exits with 1."""
        res = self.run_cli("WH", "/nonexistent/path.csv")
        self.assertEqual(res.returncode, 1)
        self.assertIn("Error:", res.stderr)

    def test_schema_validation_failure_exits_with_error(self):
        """Verify that a malformed CSV row triggers validation failure and exits with 1."""
        bad_csv = os.path.join(self.temp_dir.name, "bad-regions.csv")
        with open(bad_csv, "w", encoding="utf-8") as f:
            f.write("RegionCode,RegionName,RefHeight,FLorValley,Country,Url\n")
            f.write("WH,West Highlands,not_a_height,FL,Scotland,https://mwis.org.uk/forecasts/scottish/west-highlands/text\n")
        res = self.run_cli("WH", bad_csv)
        self.assertEqual(res.returncode, 1)
        self.assertIn("Error:", res.stderr)

if __name__ == "__main__":
    unittest.main()
