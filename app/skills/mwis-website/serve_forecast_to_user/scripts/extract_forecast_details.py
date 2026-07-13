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


def _add_requested_fields(
    d: dict[str, Any],
    day_dict: dict[str, Any],
    allowed_fields: set[str],
    categories: list[str],
    mappings: dict[str, list[str]],
) -> None:
    """Helper to populate specific user requested category fields."""
    requested_fields = []
    for cat in categories:
        if cat in mappings:
            requested_fields.extend(mappings[cat])
    for r_field in requested_fields:
        if r_field in ["uk_summary", "region_headline"]:
            continue
        if r_field in allowed_fields and r_field in d and r_field not in day_dict:
            day_dict[r_field] = d[r_field]


def _add_headlines_and_metadata(
    d: dict[str, Any], day_dict: dict[str, Any], allowed_fields: set[str]
) -> None:
    """Helper to populate headers, headlines matching patterns, and trailing metadata."""
    is_index_zero = d.get("forecast_index") == 0
    if is_index_zero:
        if (
            "uk_summary" in allowed_fields
            and "uk_summary" in d
            and "uk_summary" not in day_dict
        ):
            day_dict["uk_summary"] = d["uk_summary"]
        if (
            "region_headline" in allowed_fields
            and "region_headline" in d
            and "region_headline" not in day_dict
        ):
            day_dict["region_headline"] = d["region_headline"]

    for k, v in d.items():
        if k.endswith("_headline") and k in allowed_fields and k not in day_dict:
            day_dict[k] = v

    for k, v in d.items():
        if k in allowed_fields and k not in day_dict:
            day_dict[k] = v


def _build_day_dict(
    d: dict[str, Any],
    allowed_fields: set[str],
    categories: list[str],
    mappings: dict[str, list[str]],
) -> dict[str, Any]:
    """Builds individual filtered day forecast dictionaries from input day and category mappings."""
    day_dict = {}
    if "date" in allowed_fields and "date" in d:
        day_dict["date"] = d["date"]
    if "last_updated" in allowed_fields and "last_updated" in d:
        day_dict["last_updated"] = d["last_updated"]

    _add_requested_fields(d, day_dict, allowed_fields, categories, mappings)
    _add_headlines_and_metadata(d, day_dict, allowed_fields)
    return day_dict


def _filter_region_forecast(
    f_data: dict[str, Any],
    allowed_fields: set[str],
    categories: list[str],
    mappings: dict[str, list[str]],
) -> dict[str, Any]:
    """Orchestrator of dictionary copying."""
    f_copy = {k: v for k, v in f_data.items() if k not in ["days", "outlook"]}
    if "days" in f_data:
        filtered_days = [
            _build_day_dict(d, allowed_fields, categories, mappings)
            for d in f_data["days"]
        ]
        f_copy["days"] = filtered_days

    if "outlook" in f_data and ("outlook" in allowed_fields or not categories):
        f_copy["outlook"] = f_data["outlook"]
    return f_copy


def extract_forecast_details(
    forecasts: dict[str, Any], categories: list[str]
) -> dict[str, Any]:
    """Filters forecast payload to keep only fields matching the requested categories."""
    if "full" in categories or "all" in categories:
        return forecasts
    mappings = _load_mappings()
    allowed = _get_allowed_fields(categories, mappings)
    return {
        reg: (
            _filter_region_forecast(fd, allowed, categories, mappings)
            if isinstance(fd, dict)
            else fd
        )
        for reg, fd in forecasts.items()
    }
