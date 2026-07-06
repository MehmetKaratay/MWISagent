# MWIS Agent (c) by Mehmet Rahmi Karatay
#
# MWIS Agent is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License.
#
# You should have received a copy of the license along with this
# work.  If not, see <https://creativecommons.org/licenses/by-sa/4.0/>.

"""Schedule verification helper module using zoneinfo for BST checks."""

import datetime
from zoneinfo import ZoneInfo

# Scheduler constants for forecast updates (BST / British Time)
DAILY_START_HOUR = 11
DAILY_END_HOUR = 18
EXTRA_CHECK_HOUR = 15
EXTRA_CHECK_MINUTE = 30
HOURLY_WINDOW_END_HOUR = 16
TEN_MINUTELY_START_HOUR = 16
TEN_MINUTELY_END_HOUR = 18
TEN_MINUTELY_INTERVAL = 10


def _is_outside_schedule_bounds(hour: int, minute: int) -> bool:
    """Enforce daily boundaries from DAILY_START_HOUR to DAILY_END_HOUR BST."""
    if hour < DAILY_START_HOUR or hour > DAILY_END_HOUR:
        return True
    if hour == DAILY_END_HOUR and minute > 0:
        return True
    return False


def _is_ten_minutely_check(hour: int, minute: int) -> bool:
    """Check if the time falls on a 10-minute check in the late window."""
    if TEN_MINUTELY_START_HOUR <= hour <= TEN_MINUTELY_END_HOUR:
        if hour == TEN_MINUTELY_END_HOUR and minute == 0:
            return True
        if hour == TEN_MINUTELY_END_HOUR:
            return False
        return (minute % TEN_MINUTELY_INTERVAL) == 0
    return False


def _is_extra_check(hour: int, minute: int) -> bool:
    """Check if time matches the exact midday check time."""
    return hour == EXTRA_CHECK_HOUR and minute == EXTRA_CHECK_MINUTE


def _is_hourly_check(hour: int, minute: int) -> bool:
    """Check if the time falls exactly on an hour in the initial window."""
    if DAILY_START_HOUR <= hour <= HOURLY_WINDOW_END_HOUR:
        return minute == 0
    return False


def is_time_in_schedule(dt: datetime.datetime) -> bool:
    """Check if the provided datetime satisfies the MWIS check schedule rules.

    Args:
        dt (datetime.datetime): Datetime to check.

    Returns:
        bool: True if the time matches a scheduled check time, False otherwise.
    """
    bst_tz = ZoneInfo("Europe/London")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.UTC)

    local_dt = dt.astimezone(bst_tz)
    hour = local_dt.hour
    minute = local_dt.minute

    if _is_outside_schedule_bounds(hour, minute):
        return False
    if _is_ten_minutely_check(hour, minute):
        return True
    if _is_extra_check(hour, minute):
        return True
    return _is_hourly_check(hour, minute)
