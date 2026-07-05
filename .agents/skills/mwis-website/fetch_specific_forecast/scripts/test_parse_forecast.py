# Copyright (c) 2026 Mehmet Rahmi Karatay
# Licensed under the MIT License.

"""Unit tests for the parse_forecast.py parser script."""

import unittest
import os
import sys
import subprocess
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_PATH = os.path.join(SCRIPT_DIR, "parse_forecast.py")
RESOURCES_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "tests", "resources")
PYTHON_EXE = sys.executable


class TestParseForecast(unittest.TestCase):
    """Test suite for parsing MWIS HTML pages into JSON."""

    def test_parse_eh_static_html(self):
        """Verify parsing of Cairngorms (EH) static HTML."""
        # This will fail initially because parse_forecast.py is not yet implemented.
        if SCRIPT_DIR not in sys.path:
            sys.path.insert(0, SCRIPT_DIR)
        from parse_forecast import parse_forecast_html

        eh_path = os.path.join(RESOURCES_DIR, "eh-forecast.html")
        with open(eh_path, "r", encoding="utf-8") as f:
            html = f.read()

        data = parse_forecast_html(html)
        self.assertIn("Cairngorms", data["region"])
        self.assertEqual(len(data["days"]), 3)
        for day in data["days"]:
            self.assertIn("day_index", day)
            self.assertIsNotNone(day["date"])
            self.assertIsNotNone(day["last_updated"])
            self.assertIsNotNone(day["wind_headline"])
            self.assertIsNotNone(day["wind_effect"])
            self.assertIsNotNone(day["precip_headline"])
            self.assertIsNotNone(day["precip_detail"])
            self.assertIsNotNone(day["cloud_headline"])
            self.assertIsNotNone(day["cloud_detail"])
            self.assertIsNotNone(day["chance_cloud_free"])
            self.assertIsNotNone(day["sun_clarity"])
            self.assertIsNotNone(day["cold_temp"])
            self.assertIsNotNone(day["freezing_level"])
        self.assertIsNotNone(data["outlook"])

        # Detailed verification of split fields
        day0 = data["days"][0]
        self.assertEqual(day0["precip_headline"], "Rain sets in through afternoon")
        self.assertEqual(
            day0["precip_detail"],
            "Drizzly on the high tops at dawn, a few spots of light rain from the west, "
            "but several hours of largely dry conditions. Rain arrives from the west "
            "as midday approaches, spreading widely and setting in persistently through afternoon.",
        )
        self.assertEqual(day0["cloud_headline"], "Becoming extensive through afternoon")
        self.assertEqual(
            day0["cloud_detail"],
            "Bases start 700-1000m, lowest western hills but also some early breaks "
            "(though high Cairngorm plateau likely stays shrouded). Cloud fills in from "
            "the west from midday onward, bases to 500-600m near and west of Strathspey "
            "with lower ragged patches. Hills north of Ben Avon stay clear up to 800-900m until later.",
        )

    def test_cli_execution_success(self):
        """Verify successful CLI run with a local file."""
        eh_path = os.path.join(RESOURCES_DIR, "eh-forecast.html")
        res = subprocess.run(
            [PYTHON_EXE, SCRIPT_PATH, eh_path], capture_output=True, text=True
        )
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertIn("Cairngorms", data["region"])

    def test_cli_execution_file_missing(self):
        """Verify CLI exits with code 3 if local file is missing."""
        res = subprocess.run(
            [PYTHON_EXE, SCRIPT_PATH, "nonexistent.html"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 3)

    def test_cli_execution_bad_html(self):
        """Verify CLI exits with code 4 for completely invalid HTML structure."""
        # Create temp invalid html file
        temp_file = os.path.join(RESOURCES_DIR, "invalid.html")
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write("<html><body>Nothing here</body></html>")

        try:
            res = subprocess.run(
                [PYTHON_EXE, SCRIPT_PATH, temp_file], capture_output=True, text=True
            )
            self.assertEqual(res.returncode, 4)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_fetch_forecast_html_network_error(self):
        """Verify network error exits with code 2."""
        from unittest.mock import patch
        import requests
        from parse_forecast import main
        import sys

        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.RequestException("Network Error")
            with patch.object(
                sys, "argv", ["parse_forecast.py", "http://example.com/forecast"]
            ):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 2)

    def test_fetch_forecast_html_network_success(self):
        """Verify successful network fetch parses correctly."""
        from unittest.mock import patch
        from parse_forecast import main
        import sys
        from io import StringIO

        eh_path = os.path.join(RESOURCES_DIR, "eh-forecast.html")
        with open(eh_path, "r", encoding="utf-8") as f:
            html = f.read()

        with patch("requests.get") as mock_get:
            mock_resp = mock_get.return_value
            mock_resp.text = html
            mock_resp.raise_for_status.return_value = None

            with patch.object(
                sys, "argv", ["parse_forecast.py", "http://example.com/forecast"]
            ):
                with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                    with self.assertRaises(SystemExit) as cm:
                        main()
                    self.assertEqual(cm.exception.code, 0)
                    data = json.loads(mock_stdout.getvalue())
                    self.assertIn("Cairngorms", data["region"])


if __name__ == "__main__":
    unittest.main()
