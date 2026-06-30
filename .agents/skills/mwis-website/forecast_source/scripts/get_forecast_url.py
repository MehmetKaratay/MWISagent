#!/usr/bin/env python3
"""
Utility script to extract the MWIS area forecast URL from a regions CSV reference.
"""
import os
import csv
import sys

DEFAULT_CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "resources",
    "mwis-regions.csv"
)

def validate_non_empty_query(query: str) -> str:
    normalized = str(query).strip().lower()
    if not normalized:
        raise ValueError("Search query cannot be empty.")
    return normalized

def ensure_csv_file_exists(csv_path: str) -> None:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Regions reference CSV not found at: {csv_path}")

def find_url_in_csv_rows(reader, normalized_query: str) -> str:
    for row in reader:
        code = row.get("RegionCode", "").strip().lower()
        name = row.get("RegionName", "").strip().lower()
        if normalized_query in (code, name):
            return row.get("Url", "").strip()
    return ""

def extract_url_from_csv(normalized_query: str, csv_path: str) -> str:
    with open(csv_path, mode="r", encoding="utf-8") as f:
        url = find_url_in_csv_rows(csv.DictReader(f), normalized_query)
        if url:
            return url
    raise ValueError("No matching MWIS region found.")

def get_forecast_url(query: str, csv_path: str = None) -> str:
    path = csv_path if csv_path is not None else DEFAULT_CSV_PATH
    q_norm = validate_non_empty_query(query)
    ensure_csv_file_exists(path)
    try:
        return extract_url_from_csv(q_norm, path)
    except ValueError:
        raise ValueError(f"No matching MWIS region found for: '{query}'")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 get_forecast_url.py <regionCode_or_regionName> [custom_csv_path]", file=sys.stderr)
        sys.exit(1)

    query_input = sys.argv[1]
    custom_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        url_output = get_forecast_url(query_input, custom_path)
        print(url_output)
    except Exception as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)
