#!/usr/bin/env python3
# MWIS Agent (c) by Mehmet Rahmi Karatay
#
# MWIS Agent is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License.
#
# You should have received a copy of the license along with this
# work.  If not, see <https://creativecommons.org/licenses/by-sa/4.0/>.

"""Utility script to extract the MWIS area forecast URL from a regions CSV reference."""

import argparse
import json
import os
import sys

from query_utils import find_region_row

DEFAULT_CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "references",
    "mwis-regions.csv",
)


def get_forecast_url(query: str, csv_path: str | None = None) -> str:
    """Get the forecast URL for the given query.

    Args:
        query (str): Query string.
        csv_path (str, optional): CSV file path.

    Returns:
        str: Forecast URL.
    """
    path = csv_path if csv_path is not None else DEFAULT_CSV_PATH
    try:
        row = find_region_row(path, query)
        return row["Url"].strip()
    except ValueError as err:
        if "No matching MWIS region found" in str(err):
            raise ValueError(f"No matching MWIS region found for: '{query}'") from err
        raise


def resolve_url(query: str, csv_path: str | None = None) -> str:
    """Resolve the forecast URL for the given query.

    Args:
        query: Query string (RegionCode or RegionName).
        csv_path: Optional custom CSV file path.

    Returns:
        The forecast URL.
    """
    return get_forecast_url(query, csv_path)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Extract MWIS forecast URL.")
    parser.add_argument("query", help="Region code or region name")
    parser.add_argument(
        "csv_path",
        nargs="?",
        default=DEFAULT_CSV_PATH,
        help="Path to custom regions CSV",
    )
    parser.add_argument(
        "-stdout", "--stdout", action="store_true", help="Print raw URL instead of JSON"
    )

    args = parser.parse_args()
    try:
        url = get_forecast_url(args.query, args.csv_path)
        if args.stdout:
            print(url)
        else:
            print(json.dumps({"url": url}))
        sys.exit(0)
    except Exception as err:
        sys.stderr.write(f"Error: {err}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
