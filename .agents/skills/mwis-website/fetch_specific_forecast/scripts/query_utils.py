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

VALIDATION_RULES = {
    "RegionCode": lambda val: bool(re.match(r"^[A-Z]{2}$", val)),
    "RegionName": lambda val: bool(re.match(r"^[a-zA-Z &]+$", val)),
    "RefHeight": lambda val: bool(re.match(r"^\d{3}m$", val)),
    "FLorValley": lambda val: val in ("FL", "Valley"),
    "Country": lambda val: val in ("Scotland", "England", "Wales"),
    "Url": lambda val: val.startswith("https://mwis.org.uk/forecasts/"),
}

def validate_row_schema(row: dict[str, str]) -> None:
    """Validate columns of a CSV row against schema rules.

    Args:
        row (dict[str, str]): Row dictionary.
    """
    for key, rule in VALIDATION_RULES.items():
        val = row.get(key, "").strip()
        if not rule(val):
            raise ValueError(f"Invalid {key}: '{val}'")

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
