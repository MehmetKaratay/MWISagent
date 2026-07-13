# MWIS Agent (c) by Mehmet Rahmi Karatay
#
# MWIS Agent is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License.
#
# You should have received a copy of the license along with this
# work.  If not, see <https://creativecommons.org/licenses/by-sa/4.0/>.
"""Helper functions to load specific forecast skills dynamically and fetch forecasts."""

import importlib.util
import os
import sys
from typing import Any

from app.cache import get_forecast


def load_query_country() -> Any:
    """Dynamically load the query_country skill module."""
    path = os.path.join(
        os.path.dirname(__file__),
        "skills",
        "mwis-website",
        "fetch_specific_forecast",
        "scripts",
        "query_country.py",
    )
    spec = importlib.util.spec_from_file_location("query_country", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.get_regions_for_countries


def load_query_region() -> Any:
    """Dynamically load the query_region skill module."""
    path = os.path.join(
        os.path.dirname(__file__),
        "skills",
        "mwis-website",
        "identify_forecast_area",
        "scripts",
        "query_region.py",
    )
    script_dir = os.path.dirname(path)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    spec = importlib.util.spec_from_file_location("query_region", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.find_regions_by_location


def load_query_date() -> Any:
    """Dynamically load the query_date skill module."""
    path = os.path.join(
        os.path.dirname(__file__),
        "skills",
        "mwis-website",
        "identify_outing_date",
        "scripts",
        "query_date.py",
    )
    script_dir = os.path.dirname(path)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    spec = importlib.util.spec_from_file_location("query_date", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.resolve_date_query


def load_filter_forecast() -> Any:
    """Dynamically load the filter_forecast skill module."""
    path = os.path.join(
        os.path.dirname(__file__),
        "skills",
        "mwis-website",
        "serve_forecast_to_user",
        "scripts",
        "filter_forecast.py",
    )
    script_dir = os.path.dirname(path)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    spec = importlib.util.spec_from_file_location("filter_forecast", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.filter_forecast_payload


def load_extract_details() -> Any:
    """Dynamically load the extract_forecast_details helper script."""
    path = os.path.join(
        os.path.dirname(__file__),
        "skills",
        "mwis-website",
        "serve_forecast_to_user",
        "scripts",
        "extract_forecast_details.py",
    )
    script_dir = os.path.dirname(path)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    spec = importlib.util.spec_from_file_location("extract_forecast_details", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.extract_forecast_details


def _detect_hazard(forecast: dict[str, Any]) -> bool:
    """Detect severe weather hazards from a forecast's wind headline."""
    if not forecast or not forecast.get("days"):
        return False
    day0_wind = forecast["days"][0].get("wind_headline", "").lower()
    return any(w in day0_wind for w in ["gale", "storm", "hurricane"])


def _fetch_all_forecasts(regions: list[str], needs_impact: bool) -> tuple[dict, bool]:
    """Fetch all MWIS forecasts for the requested regions."""
    forecasts = {}
    for region in regions:
        try:
            forecast = get_forecast(region)
            forecasts[region] = forecast
            if _detect_hazard(forecast):
                needs_impact = True
        except Exception as e:
            forecasts[region] = {"error": str(e)}
    return forecasts, needs_impact


def _resolve_date_codes(date_query: str | None) -> list[str]:
    """Resolves date query into day codes like D0, D1, etc."""
    if not date_query:
        return []
    norm = date_query.strip().lower()
    if norm in ["d0", "d1", "d2", "d3", "doutlook"]:
        return [date_query.strip()]
    try:
        resolve_date_fn = load_query_date()
        return resolve_date_fn(date_query)
    except Exception:
        return []


def _get_filtered_forecasts(
    regions: list[str],
    date_query: str | None,
    needs_impact: bool,
    categories: list[str],
) -> tuple[dict, bool, list[str]]:
    """Fetches and filters forecasts for the given regions, date query, and categories."""
    forecasts, needs_impact = _fetch_all_forecasts(regions, needs_impact)
    resolved = _resolve_date_codes(date_query)
    try:
        filter_fn = load_filter_forecast()
        forecasts = filter_fn(forecasts, resolved)
    except Exception:
        pass
    try:
        extract_fn = load_extract_details()
        forecasts = extract_fn(forecasts, categories)
    except Exception:
        pass
    return forecasts, needs_impact, resolved
