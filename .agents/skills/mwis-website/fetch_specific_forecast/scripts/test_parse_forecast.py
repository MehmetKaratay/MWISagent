# Copyright (c) 2026 Mehmet Rahmi Karatay
# Licensed under the MIT License.

"""Unit tests for the parse_forecast.py parser script."""

import unittest
import os
import sys
import subprocess
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_PATH = os.path.join(SCRIPT_DIR, 'parse_forecast.py')
RESOURCES_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'tests', 'resources')
PYTHON_EXE = sys.executable

class TestParseForecast(unittest.TestCase):
    """Test suite for parsing MWIS HTML pages into JSON."""

    def test_parse_eh_static_html(self):
        """Verify parsing of Cairngorms (EH) static HTML."""
        # This will fail initially because parse_forecast.py is not yet implemented.
        from parse_forecast import parse_forecast_html
        eh_path = os.path.join(RESOURCES_DIR, 'eh-forecast.html')
        with open(eh_path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        data = parse_forecast_html(html)
        self.assertIn("Cairngorms", data["region"])
        self.assertEqual(len(data["days"]), 3)
        for day in data["days"]:
            self.assertIn("day_index", day)
            self.assertIsNotNone(day["date"])
            self.assertIsNotNone(day["last_updated"])
            self.assertIsNotNone(day["wind_mountain"])
            self.assertIsNotNone(day["wind_effect"])
            self.assertIsNotNone(day["precipitation"])
            self.assertIsNotNone(day["cloud_hills"])
            self.assertIsNotNone(day["chance_cloud_free"])
            self.assertIsNotNone(day["sun_clarity"])
            self.assertIsNotNone(day["cold_temp"])
            self.assertIsNotNone(day["freezing_level"])
        self.assertIsNotNone(data["outlook"])

    def test_cli_execution_success(self):
        """Verify successful CLI run with a local file."""
        eh_path = os.path.join(RESOURCES_DIR, 'eh-forecast.html')
        res = subprocess.run([PYTHON_EXE, SCRIPT_PATH, eh_path], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertIn("Cairngorms", data["region"])

    def test_cli_execution_file_missing(self):
        """Verify CLI exits with code 3 if local file is missing."""
        res = subprocess.run([PYTHON_EXE, SCRIPT_PATH, "nonexistent.html"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 3)

    def test_cli_execution_bad_html(self):
        """Verify CLI exits with code 4 for completely invalid HTML structure."""
        # Create temp invalid html file
        temp_file = os.path.join(RESOURCES_DIR, 'invalid.html')
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write("<html><body>Nothing here</body></html>")
        
        try:
            res = subprocess.run([PYTHON_EXE, SCRIPT_PATH, temp_file], capture_output=True, text=True)
            self.assertEqual(res.returncode, 4)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

if __name__ == '__main__':
    unittest.main()
