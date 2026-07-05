# Copyright (c) 2026 Mehmet Rahmi Karatay
# Licensed under the MIT License.

"""Inject resolved D-codes into the parsed forecast JSON structure."""

import argparse
import datetime
import json
import os
import re
import sys
from typing import Any, Dict, Optional

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


def inject_d_codes(
    forecast_data: Dict[str, Any], ref_date: Optional[datetime.date] = None
) -> Dict[str, Any]:
    """Inject resolved D-codes into days array and format outlook as an object.

    Args:
        forecast_data: Parsed forecast dictionary.
        ref_date: Optional reference date to calculate offsets.

    Returns:
        Dict[str, Any]: The updated forecast dictionary.
    """
    updated = forecast_data.copy()

    # Process days array
    if "days" in updated and isinstance(updated["days"], list):
        new_days = []
        for day in updated["days"]:
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
            new_days.append(new_day)
        updated["days"] = new_days

    # Process outlook
    if "outlook" in updated:
        outlook_text = updated["outlook"]
        if isinstance(outlook_text, dict):
            # Already processed
            pass
        else:
            updated["outlook"] = {
                "Dcode": "Doutlook",
                "outlook": str(outlook_text),
            }

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


def main() -> None:
    """Main CLI entry point."""
    args = _parse_cli_args()
    ref_date = None
    if args.ref_date:
        try:
            ref_date = datetime.datetime.strptime(args.ref_date, "%Y-%m-%d").date()
        except ValueError:
            sys.stderr.write(f"Error: Invalid reference date format: {args.ref_date}\n")
            sys.exit(1)

    try:
        if args.source:
            if not os.path.exists(args.source):
                sys.stderr.write(f"Error: File not found: {args.source}\n")
                sys.exit(3)
            with open(  # nosemgrep: detect-path-traversal
                args.source, "r", encoding="utf-8"
            ) as f:
                data = json.load(f)
        else:
            data = json.load(sys.stdin)

        updated = inject_d_codes(data, ref_date)
        print(json.dumps(updated, indent=2))
        sys.exit(0)
    except Exception as err:
        sys.stderr.write(f"Error: {err}\n")
        sys.exit(2)


if __name__ == "__main__":
    main()
