# Copyright (c) 2026 Mehmet Rahmi Karatay
# Licensed under the MIT License.

"""Unit tests for the query_url.py CLI tool."""

import unittest
import os
import tempfile
import subprocess
import json
import sys

# Paths to the script under test
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_PATH = os.path.join(SCRIPT_DIR, 'query_url.py')
PYTHON_EXE = sys.executable

class TestQueryUrlCLI(unittest.TestCase):
    """Test suite verifying CLI execution of query_url.py."""

    def setUp(self):
        # Create a temporary CSV file mimicking the structure of mwis-regions.csv for tests
        self.temp_dir = tempfile.TemporaryDirectory()
        self.csv_path = os.path.join(self.temp_dir.name, "test-regions.csv")
        with open(self.csv_path, "w", encoding="utf-8") as f:
            f.write("RegionCode,RegionName,RefHeight,FLorValley,Country,Url\n")
            f.write("NW,North West Highlands,900m,FL,Scotland,https://mwis.org.uk/forecasts/scottish/the-northwest-highlands/text\n")
            f.write("WH,West Highlands,900m,FL,Scotland,https://mwis.org.uk/forecasts/scottish/west-highlands/text\n")
            f.write("EH,Eastern Highlands,900m,FL,Scotland,https://mwis.org.uk/forecasts/scottish/cairngorms/text\n")

    def tearDown(self):
        self.temp_dir.cleanup()

    def run_cli(self, query: str, stdout_flag: str = None) -> subprocess.CompletedProcess:
        """Helper to execute the script in a subprocess."""
        cmd = [PYTHON_EXE, SCRIPT_PATH, query, self.csv_path]
        if stdout_flag:
            cmd.append(stdout_flag)
        return subprocess.run(cmd, capture_output=True, text=True, timeout=5)

    def test_default_json_output(self):
        """Verify default execution prints JSON-formatted URL."""
        res = self.run_cli("WH")
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout.strip())
        self.assertEqual(data, {"url": "https://mwis.org.uk/forecasts/scottish/west-highlands/text"})

    def test_stdout_flag_short(self):
        """Verify -stdout flag prints raw URL string."""
        res = self.run_cli("WH", "-stdout")
        self.assertEqual(res.returncode, 0)
        self.assertEqual(res.stdout.strip(), "https://mwis.org.uk/forecasts/scottish/west-highlands/text")

    def test_stdout_flag_long(self):
        """Verify --stdout flag prints raw URL string."""
        res = self.run_cli("WH", "--stdout")
        self.assertEqual(res.returncode, 0)
        self.assertEqual(res.stdout.strip(), "https://mwis.org.uk/forecasts/scottish/west-highlands/text")

    def test_case_insensitive_name(self):
        """Verify name resolution is case-insensitive and outputs JSON by default."""
        res = self.run_cli("north west highlands")
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout.strip())
        self.assertEqual(data, {"url": "https://mwis.org.uk/forecasts/scottish/the-northwest-highlands/text"})

    def test_invalid_region_exits_with_error(self):
        """Verify query for non-existent region outputs error on stderr and exits with 1."""
        res = self.run_cli("InvalidRegion")
        self.assertEqual(res.returncode, 1)
        self.assertIn("Error:", res.stderr)

    def test_empty_query_exits_with_error(self):
        """Verify query with empty string outputs error and exits with 1."""
        res = self.run_cli("")
        self.assertEqual(res.returncode, 1)

    def test_missing_csv_file_exits_with_error(self):
        """Verify non-existent CSV path outputs error and exits with 1."""
        cmd = [PYTHON_EXE, SCRIPT_PATH, "WH", "/nonexistent/path.csv"]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        self.assertEqual(res.returncode, 1)
        self.assertIn("Error:", res.stderr)

if __name__ == "__main__":
    unittest.main()
