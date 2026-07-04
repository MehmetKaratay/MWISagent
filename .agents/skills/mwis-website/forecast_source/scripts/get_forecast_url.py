#!/usr/bin/env python3
# Copyright (c) 2026 Mehmet Rahmi Karatay
# Licensed under the MIT License.

"""Utility script to extract the MWIS area forecast URL from a regions CSV reference."""

import os
import csv
import sys
import json
import argparse

DEFAULT_CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "resources",
    "mwis-regions.csv"
)

def validate_non_empty_query(query: str) -> str:
    """Validate that the query string is not empty.

    Args:
        query (str): The search query.

    Returns:
        str: Normalized query.
    """
    normalized = str(query).strip().lower()
    if not normalized:
        raise ValueError("Search query cannot be empty.")
    return normalized

def ensure_csv_file_exists(csv_path: str) -> None:
    """Verify the CSV file exists.

    Args:
        csv_path (str): Path to check.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Regions reference CSV not found at: {csv_path}")

def find_url_in_csv_rows(reader, normalized_query: str) -> str:
    """Find the URL matching the query from CSV rows.

    Args:
        reader (csv.DictReader): Reader for the CSV rows.
        normalized_query (str): Normalized search query.

    Returns:
        str: Matched URL.
    """
    for row in reader:
        code = row.get("RegionCode", "").strip().lower()
        name = row.get("RegionName", "").strip().lower()
        if normalized_query in (code, name):
            return row.get("Url", "").strip()
    return ""

def extract_url_from_csv(normalized_query: str, csv_path: str) -> str:
    """Extract URL from CSV file.

    Args:
        normalized_query (str): Normalized query.
        csv_path (str): CSV file path.

    Returns:
        str: Extracted URL.
    """
    with open(csv_path, mode="r", encoding="utf-8") as f:
        url = find_url_in_csv_rows(csv.DictReader(f), normalized_query)
        if url:
            return url
    raise ValueError("No matching MWIS region found.")

def get_forecast_url(query: str, csv_path: str = None) -> str:
    """Get the forecast URL for the given query.

    Args:
        query (str): Query string.
        csv_path (str, optional): CSV file path.

    Returns:
        str: Forecast URL.
    """
    path = csv_path if csv_path is not None else DEFAULT_CSV_PATH
    q_norm = validate_non_empty_query(query)
    ensure_csv_file_exists(path)
    try:
        return extract_url_from_csv(q_norm, path)
    except ValueError:
        raise ValueError(f"No matching MWIS region found for: '{query}'")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Extract MWIS forecast URL.")
    parser.add_argument("query", help="Region code or region name")
    parser.add_argument("csv_path", nargs="?", default=DEFAULT_CSV_PATH, help="Path to custom regions CSV")
    parser.add_argument("-stdout", "--stdout", action="store_true", help="Print raw URL instead of JSON")

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
