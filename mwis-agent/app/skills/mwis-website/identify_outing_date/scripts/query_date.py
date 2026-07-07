#!/usr/bin/env python3
# MWIS Agent (c) by Mehmet Rahmi Karatay
#
# MWIS Agent is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License.
#
# You should have received a copy of the license along with this
# work.  If not, see <https://creativecommons.org/licenses/by-sa/4.0/>.

"""Resolve input dates and ranges to MWIS forecast coverage codes."""

import datetime
import json
import os
import re
import sys

import parsedatetime


def get_reference_date() -> datetime.date:
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


def _parse_formatted_date(text: str, ref_year: int) -> datetime.date:
    """Parse DD/MM or DD/MM/YYYY formatted dates.

    Args:
        text (str): The date string to parse.
        ref_year (int): Year fallback if not in text.

    Returns:
        datetime.date: The parsed date.
    """
    m = re.match(r"^(\d{1,2})/(\d{1,2})(?:/(\d{4}))?$", text)
    if not m:
        raise ValueError()
    day = int(m.group(1))
    month = int(m.group(2))
    year = int(m.group(3)) if m.group(3) else ref_year
    return datetime.date(year, month, day)


def _parse_fuzzy_date(text: str, ref_date: datetime.date) -> datetime.date:
    """Parse relative/fuzzy date descriptions using parsedatetime.

    Args:
        text (str): Relative date query.
        ref_date (datetime.date): Reference date.

    Returns:
        datetime.date: The parsed date.
    """
    cal = parsedatetime.Calendar()
    ref_dt = datetime.datetime.combine(ref_date, datetime.time.min)
    struct, flag = cal.parse(text, ref_dt.timetuple())
    if flag > 0:
        return datetime.date(struct.tm_year, struct.tm_mon, struct.tm_mday)
    raise ValueError(f"Could not parse date: '{text}'")


def parse_single_date(text: str, ref_date: datetime.date) -> datetime.date:
    """Parse a single date string using DD/MM/YYYY, DD/MM, or parsedatetime.

    Args:
        text (str): The date string to parse.
        ref_date (datetime.date): Reference date.

    Returns:
        datetime.date: The resolved date.
    """
    text = text.strip()
    try:
        return _parse_formatted_date(text, ref_date.year)
    except ValueError:
        return _parse_fuzzy_date(text, ref_date)


def _resolve_weekend(ref_date: datetime.date) -> list[datetime.date]:
    """Calculate the dates for the upcoming weekend.

    Args:
        ref_date (datetime.date): Reference date.

    Returns:
        list[datetime.date]: Sat and Sun dates (or just Sun if today is Sun).
    """
    weekday = ref_date.weekday()
    if weekday == 4:
        return [
            ref_date + datetime.timedelta(days=1),
            ref_date + datetime.timedelta(days=2),
        ]
    elif weekday == 5:
        return [ref_date, ref_date + datetime.timedelta(days=1)]
    elif weekday == 6:
        return [ref_date]
    sat = ref_date + datetime.timedelta(days=5 - weekday)
    sun = ref_date + datetime.timedelta(days=6 - weekday)
    return [sat, sun]


def _resolve_range(
    start_str: str, end_str: str, ref_date: datetime.date
) -> list[datetime.date]:
    """Generate all dates between start and end query strings.

    Args:
        start_str (str): Start date query.
        end_str (str): End date query.
        ref_date (datetime.date): Reference date.

    Returns:
        list[datetime.date]: List of dates in range.
    """
    start = parse_single_date(start_str, ref_date)
    end = parse_single_date(end_str, ref_date)
    if start > end:
        start, end = end, start
    dates = []
    curr = start
    while curr <= end:
        dates.append(curr)
        curr += datetime.timedelta(days=1)
    return dates


def resolve_query_to_dates(query: str, ref_date: datetime.date) -> list[datetime.date]:
    """Resolve a date query string into a list of dates.

    Args:
        query (str): The date query.
        ref_date (datetime.date): Reference date.

    Returns:
        list[datetime.date]: Chronologically sorted list of unique dates.
    """
    normalized = query.lower().strip()
    if "weekend" in normalized:
        return _resolve_weekend(ref_date)

    m_range = re.split(r"\s+(?:to|through)\s+", normalized)
    if len(m_range) == 2:
        return _resolve_range(m_range[0], m_range[1], ref_date)

    parts = re.split(r"\s+and\s+|,\s*", normalized)
    dates = [parse_single_date(p, ref_date) for p in parts if p.strip()]
    return sorted(set(dates))


def map_date_to_code(target: datetime.date, ref_date: datetime.date) -> str:
    """Map a target date to the corresponding MWIS forecast coverage code.

    Args:
        target (datetime.date): The date to classify.
        ref_date (datetime.date): The reference date.

    Returns:
        str: The coverage code.
    """
    delta = (target - ref_date).days
    if delta < 0:
        return "Dold"
    elif delta == 0:
        return "D0"
    elif delta == 1:
        return "D1"
    elif delta == 2:
        return "D2"
    elif delta == 3:
        return "D3"
    elif 4 <= delta <= 7:
        return "Doutlook"
    return "Dfuture"


def resolve_date_query(query: str, ref_date: datetime.date | None = None) -> list[str]:
    """Resolve a query to unique chronological MWIS coverage codes.

    Args:
        query (str): Date query.
        ref_date (datetime.date, optional): Reference date. Defaults to current date.

    Returns:
        list[str]: Unique forecast codes.
    """
    reference = ref_date if ref_date is not None else get_reference_date()
    dates = resolve_query_to_dates(query, reference)
    if not dates:
        raise ValueError("No dates resolved.")
    codes = []
    seen = set()
    for d in dates:
        code = map_date_to_code(d, reference)
        if code not in seen:
            seen.add(code)
            codes.append(code)
    return codes


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        sys.stderr.write("Error: Missing date query argument.\n")
        sys.exit(1)

    try:
        codes = resolve_date_query(sys.argv[1], get_reference_date())
        print(json.dumps(codes))
        sys.exit(0)
    except Exception as e:
        sys.stderr.write(f"Error parsing date query: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
