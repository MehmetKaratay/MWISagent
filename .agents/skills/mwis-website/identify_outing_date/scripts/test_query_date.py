#!/usr/bin/env python3
# Copyright (c) 2026 Mehmet Rahmi Karatay
# Licensed under the MIT License.

"""Unit tests for the query_date.py CLI script."""

import unittest
import subprocess
import json
import os
import sys

# Paths to the script under test
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_PATH = os.path.join(SCRIPT_DIR, 'query_date.py')
PYTHON_EXE = sys.executable

class TestQueryDateCLI(unittest.TestCase):
    """Test suite for checking the functionality of the query_date.py command-line tool."""

    def run_query(self, query: str, ref_date: str = None) -> subprocess.CompletedProcess:
        """Run the query_date.py script with the given query and optional reference date.

        Args:
            query (str): The date query string to resolve.
            ref_date (str, optional): The reference date to override the system date (YYYY-MM-DD).

        Returns:
            subprocess.CompletedProcess: The result of the subprocess run.
        """
        cmd = [PYTHON_EXE, SCRIPT_PATH, query]
        env = os.environ.copy()
        if ref_date:
            env['MWIS_REFERENCE_DATE'] = ref_date
        res = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=5)
        return res

    def test_today(self):
        """Test resolving 'today' to D0."""
        res = self.run_query("today", ref_date="2026-07-04")
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertEqual(data, ["D0"])

    def test_tomorrow(self):
        """Test resolving 'tomorrow' to D1."""
        res = self.run_query("tomorrow", ref_date="2026-07-04")
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertEqual(data, ["D1"])

    def test_standard_date_formats(self):
        """Test resolving standard DD/MM and DD/MM/YYYY formats."""
        # 06/07/2026 is Day 2 relative to 2026-07-04 -> D2
        res = self.run_query("06/07", ref_date="2026-07-04")
        self.assertEqual(res.returncode, 0)
        self.assertEqual(json.loads(res.stdout), ["D2"])

        res = self.run_query("06/07/2026", ref_date="2026-07-04")
        self.assertEqual(res.returncode, 0)
        self.assertEqual(json.loads(res.stdout), ["D2"])

    def test_past_date(self):
        """Test resolving past dates to Dold."""
        res = self.run_query("03/07/2026", ref_date="2026-07-04")
        self.assertEqual(res.returncode, 0)
        self.assertEqual(json.loads(res.stdout), ["Dold"])

    def test_future_dates(self):
        """Test resolving future dates to Doutlook and Dfuture."""
        # Doutlook: 4 to 7 days out
        res = self.run_query("09/07/2026", ref_date="2026-07-04")
        self.assertEqual(res.returncode, 0)
        self.assertEqual(json.loads(res.stdout), ["Doutlook"])

        # Dfuture: 8+ days out
        res = self.run_query("15/07/2026", ref_date="2026-07-04")
        self.assertEqual(res.returncode, 0)
        self.assertEqual(json.loads(res.stdout), ["Dfuture"])

    def test_this_weekend_from_friday(self):
        """Test resolving 'this weekend' when reference date is a Friday."""
        # 2026-07-03 is Friday.
        # This weekend covers Saturday 04/07 (D1) and Sunday 05/07 (D2)
        res = self.run_query("this weekend", ref_date="2026-07-03")
        self.assertEqual(res.returncode, 0)
        self.assertEqual(json.loads(res.stdout), ["D1", "D2"])

    def test_this_weekend_from_wednesday(self):
        """Test resolving 'this weekend' when reference date is a Wednesday."""
        # 2026-07-01 is Wednesday.
        # This weekend covers Saturday 04/07 (D3) and Sunday 05/07 (Doutlook)
        res = self.run_query("this weekend", ref_date="2026-07-01")
        self.assertEqual(res.returncode, 0)
        self.assertEqual(json.loads(res.stdout), ["D3", "Doutlook"])

    def test_today_and_tomorrow(self):
        """Test resolving range 'today and tomorrow'."""
        res = self.run_query("today and tomorrow", ref_date="2026-07-04")
        self.assertEqual(res.returncode, 0)
        self.assertEqual(json.loads(res.stdout), ["D0", "D1"])

    def test_invalid_input(self):
        """Test handling of invalid input format."""
        res = self.run_query("invalid-query-string", ref_date="2026-07-04")
        self.assertEqual(res.returncode, 1)

    def test_missing_argument(self):
        """Test query_date.py when no arguments are provided."""
        cmd = [PYTHON_EXE, SCRIPT_PATH]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        self.assertEqual(res.returncode, 1)
        self.assertIn("Error:", res.stderr)

    def test_invalid_date_value(self):
        """Test a date query with invalid calendar values (e.g., 31st of February)."""
        res = self.run_query("31/02", ref_date="2026-07-04")
        self.assertEqual(res.returncode, 1)

    def test_reversed_range(self):
        """Test a date range defined in reverse order (e.g. tomorrow to today)."""
        res = self.run_query("tomorrow to today", ref_date="2026-07-04")
        self.assertEqual(res.returncode, 0)
        self.assertEqual(json.loads(res.stdout), ["D0", "D1"])

    def test_programmatic_resolve_date_query(self):
        """Verify that resolve_date_query can be imported and executed programmatically."""
        if SCRIPT_DIR not in sys.path:
            sys.path.insert(0, SCRIPT_DIR)
        from query_date import resolve_date_query
        import datetime
        ref = datetime.date(2026, 7, 4)
        self.assertEqual(resolve_date_query("today and tomorrow", ref_date=ref), ["D0", "D1"])
        with self.assertRaises(ValueError):
            resolve_date_query("invalid-query-string", ref_date=ref)

if __name__ == '__main__':
    unittest.main()
