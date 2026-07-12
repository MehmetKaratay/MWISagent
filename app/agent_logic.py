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

import importlib.util
import os
import sys
from typing import Any

from google.adk.agents.context import Context
from google.adk.events.event import Event

from app.cache import get_forecast


def _check_security_logic(node_input: dict[str, Any]) -> Event:
    """
    Check if the input was flagged as malicious (prompt injection or commands).

    Args:
        node_input: The output from the parse_input node.

    Returns:
        Event: Routing event to handle malicious inputs or proceed safely.
    """
    if node_input.get("is_malicious", False):
        return Event(output=node_input, route="malicious")
    return Event(output=node_input, route="safe")


def _check_ambiguity_logic(node_input: dict[str, Any]) -> Event:
    """
    Check if the user input lacks necessary information or has too many regions.

    Args:
        node_input: The output from the parse_input node.

    Returns:
        Event: Routing event to handle missing data, too many locations, or proceed.
    """
    locations = node_input.get("locations", [])
    date_val = node_input.get("date")
    is_ambiguous = node_input.get("is_ambiguous", False)

    updates = {
        "locations": locations,
        "date": date_val,
        "needs_physics": node_input.get("needs_physics", False),
        "needs_impact": node_input.get("needs_impact", False),
        "needs_local_knowledge": node_input.get("needs_local_knowledge", False),
    }

    if is_ambiguous or not locations:
        return Event(output=node_input, route="missing_location", state=updates)
    if not date_val:
        return Event(output=node_input, route="missing_date", state=updates)
    if len(locations) > 5:
        return Event(output=node_input, route="too_many_locations", state=updates)
    return Event(output=node_input, route="no", state=updates)


def _validate_coverage_logic(ctx: Context, node_input: Any) -> Event:
    """
    Validate if the requested date and locations are covered by MWIS.

    Args:
        ctx: Workflow context containing state.
        node_input: Previous node output.

    Returns:
        Event: Routing event for out-of-scope or historical data handling.
    """
    date_str = (ctx.state.get("date") or "").lower()
    if date_str == "dold" or "past" in date_str:
        return Event(output=node_input, route="dold")

    locations = ctx.state.get("locations", [])
    if any("france" in loc.lower() for loc in locations):
        return Event(output=node_input, route="out_of_scope")

    return Event(output=node_input, route="valid")


def _check_physics_logic(ctx: Context, node_input: Any) -> Event:
    """
    Check if the query involves weather physics (elevation, temperature gradients).

    Args:
        ctx: Workflow context containing state.
        node_input: Previous node output.

    Returns:
        Event: Routing event to the weather_physics node if needed.
    """
    if ctx.state.get("needs_physics", False):
        return Event(output=node_input, route="yes")
    return Event(output=node_input, route="no")


def _check_impact_logic(ctx: Context, node_input: Any) -> Event:
    """
    Check if the query involves safety impacts or hazards.

    Args:
        ctx: Workflow context containing state.
        node_input: Previous node output.

    Returns:
        Event: Routing event to the weather_impact node if needed.
    """
    if ctx.state.get("needs_impact", False):
        return Event(output=node_input, route="yes")
    return Event(output=node_input, route="no")


def _check_local_logic(ctx: Context, node_input: Any) -> Event:
    """
    Check if the query requires local micro-knowledge.

    Args:
        ctx: Workflow context containing state.
        node_input: Previous node output.

    Returns:
        Event: Routing event to the local_knowledge node if needed.
    """
    if ctx.state.get("needs_local_knowledge", False):
        return Event(output=node_input, route="yes")
    return Event(output=node_input, route="no")


def _check_loop_limit_logic(ctx: Context, node_input: Any) -> Event:
    """
    Ensure the workflow follow-up loop doesn't spin infinitely.

    Args:
        ctx: Workflow context containing state.
        node_input: Previous node output.

    Returns:
        Event: Routing event to continue loop if under limit, else terminate.
    """
    if ctx.state.get("loop_count", 0) < 5:
        return Event(output=node_input, route="yes")
    return Event(output=node_input, route="no")


def load_query_country() -> Any:
    """
    Dynamically load the query_country skill module to map location names to MWIS codes.

    Returns:
        Callable: The get_regions_for_countries function.
    """
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
    """
    Dynamically load the query_region skill module to map point locations to MWIS codes.

    Returns:
        Callable: The find_regions_by_location function.
    """
    path = os.path.join(
        os.path.dirname(__file__),
        "skills",
        "mwis-website",
        "identify_forecast_area",
        "scripts",
        "query_region.py",
    )
    # query_region relies on sys.path being modified or being executed from somewhere where it can import.
    # To be safe, we temporarily inject its directory to sys.path
    script_dir = os.path.dirname(path)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    spec = importlib.util.spec_from_file_location("query_region", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.find_regions_by_location


def load_query_date() -> Any:
    """Dynamically load the query_date skill module to parse date queries.

    Returns:
        Callable: The resolve_date_query function.
    """
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
    """Dynamically load the filter_forecast skill module to filter forecast payload.

    Returns:
        Callable: The filter_forecast_payload function.
    """
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
    """Dynamically load the extract_forecast_details helper script.

    Returns:
        Callable: The extract_forecast_details function.
    """
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


def _match_regions(locations: list[str]) -> tuple[list[str], bool]:
    """
    Map natural language location names to MWIS region codes.

    Args:
        locations: List of location strings.

    Returns:
        tuple: (list of matched region codes, boolean indicating if too many regions).
    """
    get_regions_country = load_query_country()
    find_regions_pt = load_query_region()

    all_regions = set()

    for loc in locations:
        loc = loc.strip()
        if not loc:
            continue

        try:
            c_regions = get_regions_country([loc])
            if c_regions:
                all_regions.update(c_regions)
                continue
        except ValueError:
            return [], True

        # Try point based logic
        pt_res = find_regions_pt([loc])
        if pt_res.get("in_scope") and pt_res.get("regions"):
            all_regions.update(pt_res["regions"])

    if len(all_regions) > 5:
        return [], True

    regions_list = sorted(all_regions)
    return regions_list or ["Unknown"], False


def _detect_hazard(forecast: dict[str, Any]) -> bool:
    """
    Detect severe weather hazards from a forecast's wind headline.

    Args:
        forecast: The raw JSON forecast dict.

    Returns:
        bool: True if a hazard like a gale or storm is detected.
    """
    if not forecast or not forecast.get("days"):
        return False
    day0_wind = forecast["days"][0].get("wind_headline", "").lower()
    return any(w in day0_wind for w in ["gale", "storm", "hurricane"])


def _fetch_all_forecasts(regions: list[str], needs_impact: bool) -> tuple[dict, bool]:
    """
    Fetch all MWIS forecasts for the requested regions.

    Args:
        regions: List of MWIS region codes.
        needs_impact: Current state of the needs_impact flag.

    Returns:
        tuple: (dict mapping regions to forecast data, updated needs_impact flag).
    """
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


def _resolve_and_fetch_logic(ctx: Context, node_input: Any) -> Event:
    """
    Core logic to resolve requested locations to regions and fetch their forecasts.

    Args:
        ctx: Workflow context containing state.
        node_input: Previous node output.

    Returns:
        Event: Routing event containing forecast payloads or redirecting if too many locations.
    """
    regions, error = _match_regions(ctx.state.get("locations", []))
    if error:
        return Event(output=node_input, route="too_many_locations")

    forecasts, needs_impact, resolved = _get_filtered_forecasts(
        regions,
        ctx.state.get("date"),
        ctx.state.get("needs_impact", False),
        ctx.state.get("extracted_categories", []),
    )

    state_updates = {
        "region_codes": regions,
        "forecast_data": forecasts,
        "needs_impact": needs_impact,
        "resolved_date_codes": resolved,
    }
    return Event(output=forecasts, state=state_updates)
