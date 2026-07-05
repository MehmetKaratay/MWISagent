# Copyright (c) 2026 Mehmet Rahmi Karatay
# Licensed under the MIT License.

"""Unit tests for the inject_Dcodes.py script."""

import datetime
import unittest
from inject_Dcodes import inject_d_codes, parse_forecast_date


class TestInjectDCodes(unittest.TestCase):
    """Test suite for validating Dcode injection logic in parsed forecasts."""

    def test_parse_forecast_date_ordinals(self):
        """Verify parsing forecast date strings with ordinal suffixes."""
        self.assertEqual(
            parse_forecast_date("Sunday 5th July 2026"), datetime.date(2026, 7, 5)
        )
        self.assertEqual(
            parse_forecast_date("Monday 1st August 2026"), datetime.date(2026, 8, 1)
        )
        self.assertEqual(
            parse_forecast_date("Tuesday 22nd September 2026"),
            datetime.date(2026, 9, 22),
        )

    def test_inject_d_codes_standard(self):
        """Verify Dcode fields are successfully injected into days and outlook."""
        forecast = {
            "region": "Eastern Highlands",
            "days": [
                {
                    "forecast_index": 0,
                    "date": "Sunday 5th July 2026",
                    "uk_summary": "Summary...",
                },
                {
                    "forecast_index": 1,
                    "date": "Monday 6th July 2026",
                    "uk_summary": "Summary...",
                },
            ],
            "outlook": "Outlook text...",
        }
        ref_date = datetime.date(2026, 7, 5)
        updated = inject_d_codes(forecast, ref_date)

        # Days verification
        self.assertEqual(updated["days"][0]["Dcode"], "D0")
        self.assertEqual(updated["days"][1]["Dcode"], "D1")

        # Outlook verification
        self.assertIsInstance(updated["outlook"], dict)
        self.assertEqual(updated["outlook"]["Dcode"], "Doutlook")
        self.assertEqual(updated["outlook"]["outlook"], "Outlook text...")
