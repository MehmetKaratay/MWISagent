# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Utility for mapping country names to MWIS region codes.
"""

import csv
import os

# Default path to the MWIS regions CSV file
DEFAULT_CSV_PATH = os.path.join(
    os.path.dirname(__file__), "..", "references", "mwis-regions.csv"
)


def get_regions_for_countries(
    country_names: list[str], csv_path: str = DEFAULT_CSV_PATH
) -> list[str]:
    """
    Parses mwis-regions.csv to map a list of countries or region names to their corresponding region codes.

    Args:
        country_names: A list of country or region names (e.g., ["Scotland", "Wales", "West Highlands"]).
        csv_path: Path to the mwis-regions.csv file.

    Returns:
        A deduplicated list of region codes matching the countries or region names.

    Raises:
        ValueError: If the total number of combined regions exceeds 5.
    """
    target_names = set()
    for name in country_names:
        cleaned = name.strip().lower()
        if cleaned.startswith("reset "):
            cleaned = cleaned[6:].strip()
        target_names.add(cleaned)
    matched_regions = set()

    try:
        with open(csv_path, encoding="utf-8") as f:  # nosemgrep: detect-path-traversal
            reader = csv.DictReader(f)
            for row in reader:
                country = row.get("Country", "").strip().lower()
                region_name = row.get("RegionName", "").strip().lower()
                code = row.get("RegionCode", "").strip()
                if (country in target_names or region_name in target_names) and code:
                    matched_regions.add(code)
    except FileNotFoundError:
        pass  # If the CSV doesn't exist, we return empty or let it be empty

    # Convert set to sorted list for determinism
    regions = sorted(matched_regions)

    if len(regions) > 5:
        raise ValueError(
            f"Maximum of 5 regions can be compared. Requested countries resulted in {len(regions)} regions."
        )

    return regions
