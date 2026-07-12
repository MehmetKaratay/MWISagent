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


def _get_csv_path() -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.abspath(
        os.path.join(base_dir, "references", "category_mappings.csv")
    )
    if not csv_path.startswith(os.path.abspath(base_dir)):
        raise ValueError("Security Traversal Blocked")
    return csv_path


def _load_mappings() -> dict[str, list[str]]:
    csv_path = _get_csv_path()
    if not os.path.exists(csv_path):
        return {}
    with open(csv_path, encoding="utf-8") as f:  # nosemgrep: detect-path-traversal
        reader = csv.DictReader(f)
        return {
            row.get("category", "").strip(): [
                field.strip() for field in row.get("fields", "").split(",")
            ]
            for row in reader
            if row.get("category")
        }


def _get_allowed_fields(
    categories: list[str], mappings: dict[str, list[str]]
) -> set[str]:
    allowed = {"date", "forecast_index", "last_updated", "Dcode"}
    if not categories:
        allowed.update(
            [
                "uk_summary",
                "region_headline",
                "wind_headline",
                "precip_headline",
                "cloud_headline",
            ]
        )
    else:
        for cat in categories:
            if cat in mappings:
                allowed.update(mappings[cat])
    return allowed


def _filter_region_forecast(
    f_data: dict[str, Any], allowed_fields: set[str], has_categories: bool
) -> dict[str, Any]:
    f_copy = {k: v for k, v in f_data.items() if k not in ["days", "outlook"]}
    if "days" in f_data:
        f_copy["days"] = [
            {k: v for k, v in d.items() if k in allowed_fields} for d in f_data["days"]
        ]
    if "outlook" in f_data and ("outlook" in allowed_fields or not has_categories):
        f_copy["outlook"] = f_data["outlook"]
    return f_copy


def extract_forecast_details(
    forecasts: dict[str, Any], categories: list[str]
) -> dict[str, Any]:
    """Filters forecast payload to keep only fields matching the requested categories."""
    if "full" in categories:
        return forecasts
    mappings = _load_mappings()
    allowed = _get_allowed_fields(categories, mappings)
    return {
        reg: (
            _filter_region_forecast(fd, allowed, bool(categories))
            if isinstance(fd, dict)
            else fd
        )
        for reg, fd in forecasts.items()
    }
