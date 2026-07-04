#!/usr/bin/env python3
# Copyright (c) 2026 Mehmet Rahmi Karatay
# Licensed under the MIT License.

"""Resolve input dates and ranges to MWIS forecast coverage codes."""

import sys
import os
import re
import json
import datetime
import parsedatetime

def get_reference_date() -> datetime.date:
    """Determine the reference date for all calculations, defaulting to today.

    Returns:
        datetime.date: The reference date.
    """
    ref_env = os.environ.get('MWIS_REFERENCE_DATE')
    if ref_env:
        try:
            return datetime.datetime.strptime(ref_env.strip(), "%Y-%m-%d").date()
        except ValueError:
            pass
    return datetime.date.today()

def parse_single_date(text: str, ref_date: datetime.date) -> datetime.date:
    """Parse a single date string using DD/MM/YYYY, DD/MM, or parsedatetime.

    Args:
        text (str): The date string to parse.
        ref_date (datetime.date): The reference date to resolve relative dates.

    Returns:
        datetime.date: The resolved date.

    Raises:
        ValueError: If the date cannot be parsed.
    """
    text = text.strip()
    
    # Try parsing DD/MM/YYYY or DD/MM
    m = re.match(r'^(\d{1,2})/(\d{1,2})(?:/(\d{4}))?$', text)
    if m:
        day = int(m.group(1))
        month = int(m.group(2))
        year = int(m.group(3)) if m.group(3) else ref_date.year
        try:
            return datetime.date(year, month, day)
        except ValueError as e:
            raise ValueError(f"Invalid date: {text}") from e

    # Fallback to parsedatetime
    cal = parsedatetime.Calendar()
    ref_dt = datetime.datetime.combine(ref_date, datetime.time.min)
    struct, flag = cal.parse(text, ref_dt.timetuple())
    if flag > 0:
        return datetime.date(struct.tm_year, struct.tm_mon, struct.tm_mday)

    raise ValueError(f"Could not parse date: '{text}'")

def resolve_query_to_dates(query: str, ref_date: datetime.date) -> list[datetime.date]:
    """Resolve a date query string (which may represent ranges) into a list of dates.

    Args:
        query (str): The date query.
        ref_date (datetime.date): Reference date.

    Returns:
        list[datetime.date]: Chronologically sorted list of unique dates.
    """
    normalized = query.lower().strip()

    # Handle "this weekend" / "weekend"
    if "weekend" in normalized:
        weekday = ref_date.weekday()  # Monday is 0, Sunday is 6
        if weekday == 4:  # Friday
            return [ref_date + datetime.timedelta(days=1), ref_date + datetime.timedelta(days=2)]
        elif weekday == 5:  # Saturday
            return [ref_date, ref_date + datetime.timedelta(days=1)]
        elif weekday == 6:  # Sunday
            return [ref_date]
        else:
            # Upcoming Saturday and Sunday
            sat = ref_date + datetime.timedelta(days=5 - weekday)
            sun = ref_date + datetime.timedelta(days=6 - weekday)
            return [sat, sun]

    # Handle "to" / "through" ranges (e.g. "04/07 to 06/07" or "today to tomorrow")
    m_range = re.split(r'\s+(?:to|through)\s+', normalized)
    if len(m_range) == 2:
        start_date = parse_single_date(m_range[0], ref_date)
        end_date = parse_single_date(m_range[1], ref_date)
        if start_date > end_date:
            start_date, end_date = end_date, start_date
        dates = []
        curr = start_date
        while curr <= end_date:
            dates.append(curr)
            curr += datetime.timedelta(days=1)
        return dates

    # Handle "and" / comma-separated lists
    parts = re.split(r'\s+and\s+|,\s*', normalized)
    dates = []
    for part in parts:
        if part.strip():
            dates.append(parse_single_date(part, ref_date))
    return sorted(list(set(dates)))

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
    else:
        return "Dfuture"

def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        sys.stderr.write("Error: Missing date query argument.\n")
        sys.exit(1)

    query = sys.argv[1]
    ref_date = get_reference_date()

    try:
        dates = resolve_query_to_dates(query, ref_date)
        if not dates:
            raise ValueError("No dates resolved.")
        
        # Map dates to codes, preserving chronological order of dates and uniqueness
        codes = []
        seen = set()
        for d in dates:
            code = map_date_to_code(d, ref_date)
            if code not in seen:
                seen.add(code)
                codes.append(code)

        print(json.dumps(codes))
        sys.exit(0)
    except Exception as e:
        sys.stderr.write(f"Error parsing date query: {e}\n")
        sys.exit(1)

if __name__ == '__main__':
    main()
