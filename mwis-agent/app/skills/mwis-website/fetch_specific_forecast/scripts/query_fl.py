# Copyright (c) 2026 Mehmet Rahmi Karatay
# Licensed under the MIT License.

"""CLI tool to query the freezing level format (FLorValley) of a region."""

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


def resolve_fl(query: str, csv_path: str | None = None) -> str:
    """Resolve the FLorValley field of a region.

    Args:
        query: Region code or name.
        csv_path: Path to custom CSV. Defaults to DEFAULT_CSV_PATH.

    Returns:
        The FLorValley value ("FL" or "Valley").

    Raises:
        ValueError: If not found or validation fails.
    """
    path = csv_path if csv_path is not None else DEFAULT_CSV_PATH
    row = find_region_row(path, query)
    return row["FLorValley"].strip()


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Query FLorValley for a region.")
    parser.add_argument("query", help="Region code or name")
    parser.add_argument(
        "csv_path", nargs="?", default=DEFAULT_CSV_PATH, help="Path to regions CSV"
    )

    args = parser.parse_args()
    try:
        val = resolve_fl(args.query, args.csv_path)
        print(json.dumps({"FLorValley": val}))
        sys.exit(0)
    except Exception as err:
        sys.stderr.write(f"Error: {err}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
