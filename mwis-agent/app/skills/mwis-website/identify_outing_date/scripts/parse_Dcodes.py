# MWIS Agent (c) by Mehmet Rahmi Karatay
#
# MWIS Agent is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License.
#
# You should have received a copy of the license along with this
# work.  If not, see <https://creativecommons.org/licenses/by-sa/4.0/>.

"""Resolve a target date to its MWIS forecast coverage code."""

import datetime
import os


def _get_reference_date() -> datetime.date:
    """Determine the reference date for all calculations, defaulting to today.

    Returns:
        datetime.date: The reference date.
    """
    ref_env = os.environ.get("MWIS_REFERENCE_DATE")
    if ref_env:
        try:
            return datetime.datetime.strptime(ref_env.strip(), "%Y-%m-%d").date()
        except ValueError:
            pass
    return datetime.date.today()


def get_d_code_for_date(
    target: datetime.date, ref_date: datetime.date | None = None
) -> str:
    """Resolve a target date to its MWIS forecast coverage code.

    Args:
        target: The target calendar date to resolve.
        ref_date: The reference date to calculate offsets against. Defaults to today or MWIS_REFERENCE_DATE.

    Returns:
        The matching coverage code string (e.g. 'D0', 'D1', 'Doutlook').
    """
    if ref_date is None:
        ref_date = _get_reference_date()

    delta = (target - ref_date).days
    if delta < 0:
        return "Dold"
    if 0 <= delta <= 3:
        return f"D{delta}"
    if 4 <= delta <= 7:
        return "Doutlook"
    return "Dfuture"
