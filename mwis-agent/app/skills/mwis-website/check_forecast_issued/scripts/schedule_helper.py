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


def is_time_in_schedule(dt: datetime.datetime) -> bool:
    """Check if the provided datetime satisfies the MWIS check schedule rules.

    The check is calculated relative to BST (British Time / Europe/London).
    Schedule rules:
    - Daily checking window is 11:00 to 18:00 BST.
    - Hourly checks: 11:00, 12:00, 13:00, 14:00, 15:00, 16:00.
    - Extra check: 15:30.
    - Ten-minute checks: between 16:00 and 18:00 (every 10 minutes).

    Args:
        dt (datetime.datetime): Datetime to check.

    Returns:
        bool: True if the time matches a scheduled check time, False otherwise.
    """
    # Normalize datetime to Europe/London timezone
    bst_tz = ZoneInfo("Europe/London")
    if dt.tzinfo is None:
        # Assume native datetimes are in UTC
        dt = dt.replace(tzinfo=datetime.UTC)

    local_dt = dt.astimezone(bst_tz)
    hour = local_dt.hour
    minute = local_dt.minute

    # Enforce out-of-hours boundaries
    if hour < 11 or hour > 18 or (hour == 18 and minute > 0):
        return False

    # 10-minute check window: 16:00 to 18:00 BST
    if 16 <= hour <= 18:
        if hour == 18 and minute == 0:
            return True
        if hour == 18:
            return False
        return (minute % 10) == 0

    # Extra check time: 15:30 BST
    if hour == 15 and minute == 30:
        return True

    # Hourly check window: 11:00 to 16:00 BST (on the hour only)
    if 11 <= hour <= 16:
        return minute == 0

    return False
