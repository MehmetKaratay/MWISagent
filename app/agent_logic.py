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
"""Core routing logic and decision functions for the MWIS agent workflow."""

from typing import Any

from google.adk.agents.context import Context
from google.adk.events.event import Event

from app.forecast_loader import (
    _get_filtered_forecasts,
    load_extract_details,  # noqa: F401
    load_filter_forecast,  # noqa: F401
    load_query_country,
    load_query_date,  # noqa: F401
    load_query_region,
)


def _check_security_logic(node_input: dict[str, Any]) -> Event:
    """Check if the input was flagged as malicious (prompt injection or commands)."""
    if node_input.get("is_malicious", False):
        return Event(output=node_input, route="malicious")
    return Event(output=node_input, route="safe")


def _resolve_contextual_shift(ctx: Context, date_val: str | None) -> str | None:
    """Helper to load resolve_shift dynamically and calculate date code shift."""
    if not date_val:
        return None
    import importlib.util
    import os

    current_codes = ctx.state.get("resolved_date_codes", [])
    current_code_val = current_codes[0] if current_codes else "D0"
    if not current_code_val:
        current_code_val = "D0"
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "skills",
        "mwis-website",
        "identify_outing_date",
        "scripts",
        "resolve_shift.py",
    )
    if os.path.exists(path):
        spec = importlib.util.spec_from_file_location("resolve_shift", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        shift_resolved = module.resolve_shift(current_code_val, date_val)
        return shift_resolved
    return date_val


def _check_ambiguity_logic(ctx: Context, node_input: dict[str, Any]) -> Event:
    """Check if the user input lacks necessary information or has too many regions."""
    # Handle LlmAgent output wrapped in output_key="parsed_info"
    parsed = node_input
    if "parsed_info" in node_input:
        parsed = node_input["parsed_info"]
        if hasattr(parsed, "model_dump"):
            parsed = parsed.model_dump()

    # Enforce strict keyword validation for is_new_query
    is_new = parsed.get("is_new_query", False)
    if is_new:
        raw_query = ctx.state.get("raw_query", "").lower()
        reset_keywords = ["reset", "clear", "restart", "new search"]
        if not any(kw in raw_query for kw in reset_keywords):
            is_new = False

    # Reset/clear memory if is_new_query is flagged
    if is_new:
        ctx.state["locations"] = []
        ctx.state["date"] = None
        ctx.state["resolved_date_codes"] = []
        ctx.state["extracted_categories"] = []

    locations = parsed.get("locations", [])
    if not locations:
        locations = ctx.state.get("locations", [])

    date_val = parsed.get("date")
    # Resolve relative shifts if matches shift keywords
    forwards = ["following day", "next day", "day after", "tomorrow"]
    backwards = ["day before", "previous day", "yesterday"]
    if date_val and any(x in date_val.lower() for x in forwards + backwards):
        date_val = _resolve_contextual_shift(ctx, date_val)
    elif not date_val:
        date_val = ctx.state.get("date")

    categories = parsed.get("extracted_categories", [])
    if not categories:
        categories = ctx.state.get("extracted_categories", [])

    ctx.state["locations"] = locations
    ctx.state["date"] = date_val
    ctx.state["extracted_categories"] = categories

    updates = {
        "locations": locations,
        "date": date_val,
        "extracted_categories": categories,
        "needs_physics": parsed.get("needs_physics", False),
        "needs_impact": parsed.get("needs_impact", False),
        "needs_local_knowledge": parsed.get("needs_local_knowledge", False),
    }

    if parsed.get("is_ambiguous", False) or not locations:
        return Event(output=node_input, route="missing_location", state=updates)
    if not date_val:
        return Event(output=node_input, route="missing_date", state=updates)

    route = "too_many_locations" if len(locations) > 5 else "no"
    return Event(output=node_input, route=route, state=updates)


def _validate_coverage_logic(ctx: Context, node_input: Any) -> Event:
    """Validate if the requested date and locations are covered by MWIS."""
    date_str = (ctx.state.get("date") or "").lower()
    if date_str == "dold" or "past" in date_str:
        return Event(output=node_input, route="dold")

    locations = ctx.state.get("locations", [])
    if any("france" in loc.lower() for loc in locations):
        return Event(output=node_input, route="out_of_scope")

    return Event(output=node_input, route="valid")


def _check_physics_logic(ctx: Context, node_input: Any) -> Event:
    """Check if the query involves weather physics (elevation, temperature gradients)."""
    if ctx.state.get("needs_physics", False):
        return Event(output=node_input, route="yes")
    return Event(output=node_input, route="no")


def _check_impact_logic(ctx: Context, node_input: Any) -> Event:
    """Check if the query involves safety impacts or hazards."""
    if ctx.state.get("needs_impact", False):
        return Event(output=node_input, route="yes")
    return Event(output=node_input, route="no")


def _check_local_logic(ctx: Context, node_input: Any) -> Event:
    """Check if the query requires local micro-knowledge."""
    if ctx.state.get("needs_local_knowledge", False):
        return Event(output=node_input, route="yes")
    return Event(output=node_input, route="no")


def _check_loop_limit_logic(ctx: Context, node_input: Any) -> Event:
    """Ensure the workflow follow-up loop doesn't spin infinitely."""
    if ctx.state.get("loop_count", 0) < 5:
        return Event(output=node_input, route="yes")
    return Event(output=node_input, route="no")


def _match_single_location(
    loc: str, get_regions_country: Any, find_regions_pt: Any
) -> list[str]:
    """Map a single natural language location name to MWIS region codes."""
    loc = loc.strip()
    if not loc:
        return []
    try:
        c_regions = get_regions_country([loc])
        if c_regions:
            return c_regions
    except ValueError:
        raise ValueError("Too many regions") from None
    pt_res = find_regions_pt([loc])
    if pt_res.get("in_scope") and pt_res.get("regions"):
        return pt_res["regions"]
    return []


def _match_regions(locations: list[str]) -> tuple[list[str], bool]:
    """Map natural language location names to MWIS region codes."""
    get_regions_country = load_query_country()
    find_regions_pt = load_query_region()
    all_regions = set()
    for loc in locations:
        try:
            all_regions.update(
                _match_single_location(loc, get_regions_country, find_regions_pt)
            )
        except ValueError:
            return [], True
    if len(all_regions) > 5:
        return [], True
    return sorted(all_regions) or ["Unknown"], False


def _resolve_and_fetch_logic(ctx: Context, node_input: Any) -> Event:
    """Core logic to resolve requested locations to regions and fetch their forecasts."""
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
