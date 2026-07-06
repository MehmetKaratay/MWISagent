# MWIS Agent (c) by Mehmet Rahmi Karatay
#
# MWIS Agent is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License.
#
# You should have received a copy of the license along with this
# work.  If not, see <https://creativecommons.org/licenses/by-sa/4.0/>.

"""Unit and integration tests for the main forecast check & update skill logic."""

import datetime
import os
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from check_forecast import check_forecast_issued, get_all_region_codes


class TestCheckForecast(unittest.TestCase):
    """Test suite for the check_forecast_issued core logic orchestrator."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_mwis.db")
        # Ensure database is clean
        conn = sqlite3.connect(self.db_path)
        conn.close()

    def tearDown(self):
        self.temp_dir.cleanup()

    @patch("check_forecast.is_time_in_schedule")
    def test_skip_check_out_of_hours(self, mock_schedule):
        """Verify check exits early with 'skipped' if not in active schedule hours."""
        mock_schedule.return_value = False
        res = check_forecast_issued(
            db_path=self.db_path,
            env="development",
            current_time=datetime.datetime(2026, 7, 6, 9, 0),
        )
        self.assertEqual(res["status"], "no_update")

    @patch("check_forecast.is_time_in_schedule")
    def test_development_mode_no_update_if_dcode_0(self, mock_schedule):
        """Verify check returns no_update if mock NW forecast has Dcode == D0 for forecast_index == 0."""
        mock_schedule.return_value = True

        # We will mock the get_forecast_data call to return a Dcode D0 forecast
        d0_mock_data = {
            "region": "North West Highlands",
            "days": [
                {
                    "forecast_index": 0,
                    "Dcode": "D0",
                    "date": "Monday 6th July 2026",
                    "last_updated": "Sun 5th Jul 26 at 4:00PM",
                }
            ],
            "outlook": "Calm",
            "last_updated": "Sun 5th Jul 26 at 4:00PM",
        }

        with patch("check_forecast.fetch_and_parse_region", return_value=d0_mock_data):
            res = check_forecast_issued(
                db_path=self.db_path,
                env="development",
                current_time=datetime.datetime(2026, 7, 6, 12, 0),
            )
            self.assertEqual(res["status"], "no_update")

            # Check db remains empty
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='forecast_cache';"
            )
            tbl_count = cursor.fetchone()[0]
            if tbl_count > 0:
                cursor.execute("SELECT count(*) FROM forecast_cache;")
                self.assertEqual(cursor.fetchone()[0], 0)
            conn.close()

    @patch("check_forecast.is_time_in_schedule")
    def test_development_mode_updates_if_dcode_1(self, mock_schedule):
        """Verify check updates cache for all regions if mock NW forecast has Dcode == D1."""
        mock_schedule.return_value = True

        d1_mock_data = {
            "region": "North West Highlands",
            "days": [
                {
                    "forecast_index": 0,
                    "Dcode": "D1",
                    "date": "Monday 6th July 2026",
                    "last_updated": "Sun 5th Jul 26 at 4:00PM",
                }
            ],
            "outlook": "Calm",
            "last_updated": "Sun 5th Jul 26 at 4:00PM",
        }

        with patch("check_forecast.fetch_and_parse_region", return_value=d1_mock_data):
            res = check_forecast_issued(
                db_path=self.db_path,
                env="development",
                current_time=datetime.datetime(2026, 7, 6, 12, 0),
            )
            self.assertEqual(res["status"], "updated")

            # Check db contains all 10 regions
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM forecast_cache;")
            self.assertEqual(cursor.fetchone()[0], len(get_all_region_codes()))
            conn.close()

    @patch("check_forecast.is_time_in_schedule")
    def test_prevents_multiple_updates_same_day(self, mock_schedule):
        """Verify checking is immediately skipped if an update already completed today."""
        mock_schedule.return_value = True

        d1_mock_data = {
            "region": "North West Highlands",
            "days": [
                {
                    "forecast_index": 0,
                    "Dcode": "D1",
                    "date": "Monday 6th July 2026",
                    "last_updated": "Sun 5th Jul 26 at 4:00PM",
                }
            ],
            "outlook": "Calm",
            "last_updated": "Sun 5th Jul 26 at 4:00PM",
        }

        with patch("check_forecast.fetch_and_parse_region", return_value=d1_mock_data):
            # First run: triggers update
            res1 = check_forecast_issued(
                db_path=self.db_path,
                env="development",
                current_time=datetime.datetime(2026, 7, 6, 12, 0),
            )
            self.assertEqual(res1["status"], "updated")

            # Second run: same day, should skip and return already_updated_today
            res2 = check_forecast_issued(
                db_path=self.db_path,
                env="development",
                current_time=datetime.datetime(2026, 7, 6, 13, 0),
            )
            self.assertEqual(res2["status"], "already_updated_today")


if __name__ == "__main__":
    unittest.main()
