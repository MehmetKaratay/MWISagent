# MWIS Agent (c) by Mehmet Rahmi Karatay
#
# MWIS Agent is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License.
#
# You should have received a copy of the license along with this
# work.  If not, see <https://creativecommons.org/licenses/by-sa/4.0/>.
"""Pruning raw forecast JSON payloads to match only requested forecast categories."""

import csv
import os
from typing import Any


def _load_mappings() -> dict[str, list[str]]:
    """Load category mappings from CSV file.

    Returns:
        dict[str, list[str]]: Mapped category names to list of forecast keys.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.abspath(
        os.path.join(
            base_dir,
            "references",
            "category_mappings.csv",
        )
    )
    if not csv_path.startswith(os.path.abspath(base_dir)):
        raise ValueError("Security Traversal Blocked")

    mappings = {}
    if not os.path.exists(csv_path):
        return mappings

    with open(csv_path, encoding="utf-8") as f:  # nosemgrep: detect-path-traversal
        reader = csv.DictReader(f)
        for row in reader:
            cat = row.get("category", "").strip()
            fields = [field.strip() for field in row.get("fields", "").split(",")]
            mappings[cat] = fields
    return mappings


def extract_forecast_details(
    forecasts: dict[str, Any], categories: list[str]
) -> dict[str, Any]:
    """Filters forecast payload to keep only fields matching the requested categories.

    Args:
        forecasts (dict[str, Any]): The complete forecasts dictionary.
        categories (list[str]): List of query categories.

    Returns:
        dict[str, Any]: The filtered forecasts dictionary.
    """
    if "full" in categories:
        return forecasts

    mappings = _load_mappings()

    # Determine allowed fields
    allowed_fields = {"date", "forecast_index", "last_updated", "Dcode"}
    if not categories:
        # Default to headlines only
        headline_fields = mappings.get("cloud", [])  # fallback if mappings failed
        if mappings:
            headline_fields = [
                "uk_summary",
                "region_headline",
                "wind_headline",
                "precip_headline",
                "cloud_headline",
            ]
        allowed_fields.update(headline_fields)
    else:
        for cat in categories:
            if cat in mappings:
                allowed_fields.update(mappings[cat])

    filtered = {}
    for region, f_data in forecasts.items():
        if not isinstance(f_data, dict):
            filtered[region] = f_data
            continue

        f_copy = {k: v for k, v in f_data.items() if k not in ["days", "outlook"]}
        if "days" in f_data:
            new_days = []
            for day in f_data["days"]:
                new_day = {k: v for k, v in day.items() if k in allowed_fields}
                new_days.append(new_day)
            f_copy["days"] = new_days

        if "outlook" in f_data:
            # Only keep outlook if outlook matches requested categories/fields or general summary
            # outlook is represented by the key 'outlook'
            if "outlook" in allowed_fields or not categories:
                f_copy["outlook"] = f_data["outlook"]

        filtered[region] = f_copy

    return filtered
