# Copyright (c) 2026 Mehmet Rahmi Karatay
# Licensed under the MIT License.

"""Helper utilities for querying MWIS region CSV databases."""

import os
import csv
import re
from typing import Optional

def validate_non_empty_query(query: str) -> str:
    """Validate and normalize query.

    Args:
        query (str): Input query.

    Returns:
        str: Normalized query.
    """
    normalized = query.strip()
    if not normalized:
        raise ValueError("Search query cannot be empty.")
    return normalized

def ensure_csv_file_exists(csv_path: str) -> None:
    """Verify CSV file exists.

    Args:
        csv_path (str): File path.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Regions reference CSV not found at: {csv_path}")

def validate_row_schema(row: dict[str, str]) -> None:
    """Validate columns of a CSV row against schema rules.

    Args:
        row (dict[str, str]): Row dictionary.
    """
    code = row.get("RegionCode", "").strip()
    name = row.get("RegionName", "").strip()
    height = row.get("RefHeight", "").strip()
    fl_val = row.get("FLorValley", "").strip()
    country = row.get("Country", "").strip()
    url = row.get("Url", "").strip()

    if not re.match(r"^[A-Z]{2}$", code):
        raise ValueError(f"Invalid RegionCode: '{code}'")
    if not re.match(r"^[a-zA-Z &]+$", name):
        raise ValueError(f"Invalid RegionName: '{name}'")
    if not re.match(r"^\d{3}m$", height):
        raise ValueError(f"Invalid RefHeight: '{height}'")
    if fl_val not in ("FL", "Valley"):
        raise ValueError(f"Invalid FLorValley: '{fl_val}'")
    if country not in ("Scotland", "England", "Wales"):
        raise ValueError(f"Invalid Country: '{country}'")
    if not url.startswith("https://mwis.org.uk/forecasts/"):
        raise ValueError(f"Invalid Url: '{url}'")

def find_region_row(csv_path: str, query: str) -> dict[str, str]:
    """Find a region row in the CSV file matching the query.

    Args:
        csv_path (str): CSV file path.
        query (str): Search query.

    Returns:
        dict[str, str]: Matched row dictionary.
    """
    ensure_csv_file_exists(csv_path)
    q_norm = validate_non_empty_query(query).lower()
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            validate_row_schema(row)
            code = row["RegionCode"].strip().lower()
            name = row["RegionName"].strip().lower()
            if q_norm in (code, name):
                return row
    raise ValueError(f"No matching MWIS region found for: '{query}'")
