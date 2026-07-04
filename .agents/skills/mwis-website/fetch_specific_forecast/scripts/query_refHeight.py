# Copyright (c) 2026 Mehmet Rahmi Karatay
# Licensed under the MIT License.

"""CLI tool to query the reference height (RefHeight) of a region."""

import os
import sys
import json
import argparse
from typing import Optional
from query_utils import find_region_row

DEFAULT_CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "references",
    "mwis-regions.csv"
)

def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Query RefHeight for a region.")
    parser.add_argument("query", help="Region code or name")
    parser.add_argument("csv_path", nargs="?", default=DEFAULT_CSV_PATH, help="Path to regions CSV")

    args = parser.parse_args()
    try:
        row = find_region_row(args.csv_path, args.query)
        print(json.dumps({"RefHeight": row["RefHeight"].strip()}))
        sys.exit(0)
    except Exception as err:
        sys.stderr.write(f"Error: {err}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
