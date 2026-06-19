#!/usr/bin/env python3
"""
Utility script to extract the MWIS area forecast URL from a regions CSV reference.
"""
import os
import csv
import sys

DEFAULT_CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "references",
    "mwis-regions.csv"
)

def get_forecast_url(query: str, csv_path: str = None) -> str:
    """
    Looks up and returns the forecast URL for a given region code or name.

    Args:
        query (str): The region code (e.g. 'WH') or region name (e.g. 'West Highlands').
        csv_path (str, optional): Custom path to the mwis-regions.csv file.

    Returns:
        str: The URL of the forecast area.

    Raises:
        ValueError: If the query is empty or no matching region is found.
        FileNotFoundError: If the CSV reference file cannot be located.
    """
    if csv_path is None:
        csv_path = DEFAULT_CSV_PATH

    normalized_query = str(query).strip().lower()
    if not normalized_query:
        raise ValueError("Search query cannot be empty.")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Regions reference CSV not found at: {csv_path}")

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Match against RegionCode or RegionName
            code = row.get("RegionCode", "").strip().lower()
            name = row.get("RegionName", "").strip().lower()
            
            if normalized_query in (code, name):
                url = row.get("Url", "").strip()
                if url:
                    return url

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
