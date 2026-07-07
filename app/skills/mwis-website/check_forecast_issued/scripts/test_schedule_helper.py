# MWIS Agent (c) by Mehmet Rahmi Karatay
#
# MWIS Agent is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License.
#
# You should have received a copy of the license along with this
# work.  If not, see <https://creativecommons.org/licenses/by-sa/4.0/>.

"""Unit tests for the forecast scheduling helper module."""

import datetime
import unittest
from zoneinfo import ZoneInfo

from schedule_helper import is_time_in_schedule


class TestScheduleHelper(unittest.TestCase):
    """Test suite for validating weather forecast checking execution schedule rules."""

    def test_outside_allowed_hours(self):
        """Verify checking is skipped outside 11:00-18:00 BST."""
        # 10:59 BST
        dt_early = datetime.datetime(
            2026, 7, 6, 10, 59, tzinfo=ZoneInfo("Europe/London")
        )
        self.assertFalse(is_time_in_schedule(dt_early))

        # 18:01 BST
        dt_late = datetime.datetime(2026, 7, 6, 18, 1, tzinfo=ZoneInfo("Europe/London"))
        self.assertFalse(is_time_in_schedule(dt_late))

    def test_hourly_intervals(self):
        """Verify checks run exactly on the hour between 11:00 and 16:00 BST."""
        for hour in [11, 12, 13, 14, 15, 16]:
            dt = datetime.datetime(
                2026, 7, 6, hour, 0, tzinfo=ZoneInfo("Europe/London")
            )
            self.assertTrue(is_time_in_schedule(dt))

        # Check off-hour times
        dt_off = datetime.datetime(2026, 7, 6, 12, 5, tzinfo=ZoneInfo("Europe/London"))
        self.assertFalse(is_time_in_schedule(dt_off))

    def test_extra_1530_check(self):
        """Verify the extra check at 15:30 BST is allowed."""
        dt = datetime.datetime(2026, 7, 6, 15, 30, tzinfo=ZoneInfo("Europe/London"))
        self.assertTrue(is_time_in_schedule(dt))

    def test_ten_minute_checks(self):
        """Verify 10-minute interval checks between 16:00 and 18:00 BST."""
        for minute in [10, 20, 30, 40, 50]:
            dt = datetime.datetime(
                2026, 7, 6, 16, minute, tzinfo=ZoneInfo("Europe/London")
            )
            self.assertTrue(is_time_in_schedule(dt))

            dt_17 = datetime.datetime(
                2026, 7, 6, 17, minute, tzinfo=ZoneInfo("Europe/London")
            )
            self.assertTrue(is_time_in_schedule(dt_17))

        # 18:00 is also a valid boundary check time
        dt_18 = datetime.datetime(2026, 7, 6, 18, 0, tzinfo=ZoneInfo("Europe/London"))
        self.assertTrue(is_time_in_schedule(dt_18))

        # An off-boundary check in the 16:00-18:00 window should fail
        dt_bad = datetime.datetime(2026, 7, 6, 16, 5, tzinfo=ZoneInfo("Europe/London"))
        self.assertFalse(is_time_in_schedule(dt_bad))


if __name__ == "__main__":
    unittest.main()
