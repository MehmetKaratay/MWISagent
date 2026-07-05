# Copyright (c) 2026 Mehmet Rahmi Karatay
# Licensed under the MIT License.

"""Inject resolved D-codes into the parsed forecast JSON structure."""

import argparse
import datetime
import json
import os
import re
import sys
from typing import Any

# Set up path to import parse_Dcodes from identify_outing_date skill
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTING_DATE_DIR = os.path.abspath(
    os.path.join(SCRIPT_DIR, "..", "..", "identify_outing_date", "scripts")
)
if OUTING_DATE_DIR not in sys.path:
    sys.path.insert(0, OUTING_DATE_DIR)

from parse_Dcodes import get_d_code_for_date  # noqa: E402


def parse_forecast_date(date_str: str) -> datetime.date:
    """Parse MWIS forecast date format (e.g. "Sunday 5th July 2026") to date.

    Args:
        date_str: The raw forecast date string.

    Returns:
        datetime.date: The parsed date object.
    """
    clean_str = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", date_str)
    return datetime.datetime.strptime(clean_str, "%A %d %B %Y").date()


def _inject_day_d_code(
    day: dict[str, Any], ref_date: datetime.date | None
) -> dict[str, Any]:
    """Resolve and inject the Dcode field into a single day's dictionary."""
    new_day = day.copy()
    if "date" in new_day:
        try:
            target_date = parse_forecast_date(new_day["date"])
            new_day["Dcode"] = get_d_code_for_date(target_date, ref_date)
        except Exception as err:
            sys.stderr.write(
                f"Warning: Could not resolve date '{new_day.get('date')}': {err}\n"
            )
            new_day["Dcode"] = "Dunresolved"
    return new_day


def _format_outlook_object(outlook: Any) -> dict[str, Any]:
    """Transform the outlook field into a structured object."""
    if isinstance(outlook, dict):
        return outlook
    return {
        "Dcode": "Doutlook",
        "outlook": str(outlook),
    }


def inject_d_codes(
    forecast_data: dict[str, Any], ref_date: datetime.date | None = None
) -> dict[str, Any]:
    """Inject resolved D-codes into days array and format outlook as an object.

    Args:
        forecast_data: Parsed forecast dictionary.
        ref_date: Optional reference date to calculate offsets.

    Returns:
        Dict[str, Any]: The updated forecast dictionary.
    """
    updated = forecast_data.copy()
    if "days" in updated and isinstance(updated["days"], list):
        updated["days"] = [_inject_day_d_code(d, ref_date) for d in updated["days"]]
    if "outlook" in updated:
        updated["outlook"] = _format_outlook_object(updated["outlook"])
    return updated


def _parse_cli_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Inject D-codes into MWIS forecast JSON."
    )
    parser.add_argument(
        "source", nargs="?", help="Path to forecast JSON file (reads stdin if omitted)"
    )
    parser.add_argument("--ref-date", help="Override reference date (YYYY-MM-DD)")
    return parser.parse_args()


def _parse_reference_date(date_str: str | None) -> datetime.date | None:
    """Parse the reference date CLI option."""
    if not date_str:
        return None
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        sys.stderr.write(f"Error: Invalid reference date format: {date_str}\n")
        sys.exit(1)


def _load_forecast_json(source: str | None) -> dict[str, Any]:
    """Load forecast JSON data from file or stdin."""
    if not source:
        return json.load(sys.stdin)
    if not os.path.exists(source):
        sys.stderr.write(f"Error: File not found: {source}\n")
        sys.exit(3)
    with open(  # nosemgrep: detect-path-traversal
        source, encoding="utf-8"
    ) as f:
        return json.load(f)


def main() -> None:
    """Main CLI entry point."""
    args = _parse_cli_args()
    ref_date = _parse_reference_date(args.ref_date)
    try:
        data = _load_forecast_json(args.source)
        updated = inject_d_codes(data, ref_date)
        print(json.dumps(updated, indent=2))
        sys.exit(0)
    except Exception as err:
        sys.stderr.write(f"Error: {err}\n")
        sys.exit(2)


if __name__ == "__main__":
    main()
