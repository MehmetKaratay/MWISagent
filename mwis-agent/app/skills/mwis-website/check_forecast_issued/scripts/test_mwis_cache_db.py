# MWIS Agent (c) by Mehmet Rahmi Karatay
#
# MWIS Agent is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License.
#
# You should have received a copy of the license along with this
# work.  If not, see <https://creativecommons.org/licenses/by-sa/4.0/>.

"""Unit tests for the SQLite forecast cache manager."""

import os
import sqlite3
import tempfile
import unittest

from mwis_cache_db import db_get_forecast, db_init, db_update_forecasts


class TestMwisCacheDb(unittest.TestCase):
    """Test suite for verifying the MWIS forecast cache database layer."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_forecasts.db")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_db_init_creates_table(self):
        """Verify db_init creates the forecast_cache table with correct schema."""
        db_init(self.db_path)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='forecast_cache';"
        )
        self.assertIsNotNone(cursor.fetchone())

        cursor.execute("PRAGMA table_info(forecast_cache);")
        columns = {col[1]: col[2] for col in cursor.fetchall()}
        self.assertIn("region_code", columns)
        self.assertIn("forecast_json", columns)
        self.assertIn("last_updated_mwis", columns)
        self.assertIn("cached_at", columns)
        conn.close()

    def test_db_get_forecast_returns_none_if_missing(self):
        """Verify db_get_forecast returns None if no entry exists."""
        db_init(self.db_path)
        self.assertIsNone(db_get_forecast("NW", self.db_path))

    def test_db_update_forecasts_inserts_and_gets_forecast(self):
        """Verify forecasts are correctly inserted and parsed back into dictionaries."""
        db_init(self.db_path)
        forecasts = {
            "NW": {
                "region": "North West Highlands",
                "days": [{"forecast_index": 0, "Dcode": "D0", "date": "Monday"}],
                "outlook": "Mild",
                "last_updated": "Mon 12PM",
            }
        }
        success = db_update_forecasts(forecasts, self.db_path)
        self.assertTrue(success)

        retrieved = db_get_forecast("NW", self.db_path)
        self.assertEqual(retrieved["region"], "North West Highlands")
        self.assertEqual(retrieved["days"][0]["Dcode"], "D0")

    def test_db_update_forecasts_atomic_rollback(self):
        """Verify that a validation failure inside db_update_forecasts triggers a rollback."""
        db_init(self.db_path)

        # Insert initial valid data
        initial_forecasts = {
            "NW": {
                "region": "North West Highlands",
                "days": [],
                "last_updated": "Mon 12PM",
            }
        }
        db_update_forecasts(initial_forecasts, self.db_path)

        # Trigger update where one region is invalid (missing 'last_updated')
        # This should abort the transaction and keep the old data intact
        bad_forecasts = {
            "NW": {
                "region": "North West Highlands Updated",
                "days": [],
                "last_updated": "Mon 1PM",
            },
            "WH": {
                "region": "West Highlands",
                "days": [],
                # missing last_updated to trigger validation failure
            },
        }
        success = db_update_forecasts(bad_forecasts, self.db_path)
        self.assertFalse(success)

        # NW should still have its initial values, not the updated ones
        retrieved = db_get_forecast("NW", self.db_path)
        self.assertEqual(retrieved["region"], "North West Highlands")
        self.assertIsNone(db_get_forecast("WH", self.db_path))


if __name__ == "__main__":
    unittest.main()
