# ruff: noqa
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

import json
from typing import Any, Optional

from pydantic import BaseModel, Field

from google.adk.agents import LlmAgent
from google.adk.agents.context import Context
from google.adk.apps import App
from google.adk.events.event import Event
from google.adk.events.request_input import RequestInput
from google.adk.models import Gemini
from google.adk.workflow import START, Edge, Workflow, node
from google.genai import types

from app.cache import get_forecast


class WorkflowState(BaseModel):
    raw_query: str
    locations: list[str] = Field(default_factory=list)
    date: Optional[str] = None
    region_codes: list[str] = Field(default_factory=list)
    forecast_data: Optional[dict[str, Any]] = None
    needs_physics: bool = False
    needs_impact: bool = False
    needs_local_knowledge: bool = False
    loop_count: int = 0


class ParseOutput(BaseModel):
    locations: list[str] = Field(
        default_factory=list, description="The mountain or regions queried"
    )
    date: Optional[str] = Field(
        default=None,
        description="The date queried, e.g., 'today', 'tomorrow', 'Saturday'",
    )
    is_ambiguous: bool = Field(
        default=False, description="True if location or date is too vague to resolve"
    )
    needs_physics: bool = Field(
        default=False,
        description="True if the query asks about elevation, temperature gradients, or physical causes",
    )
    needs_impact: bool = Field(
        default=False,
        description="True if the query asks about safety, hiking plans, or hazards",
    )
    needs_local_knowledge: bool = Field(
        default=False,
        description="True if the query asks about specific micro-locations",
    )


parse_input = LlmAgent(
    name="parse_input",
    model=Gemini(model="gemini-2.5-flash"),
    instruction="""
    Extract locations, date, and user intent flags from the weather query.
    If no locations are provided, leave locations empty.
    If no date is provided, leave date null.
    Set is_ambiguous to True if the query is extremely vague and cannot be parsed.
    """,
    output_schema=ParseOutput,
    output_key="parsed_info",
)


def _check_ambiguity_logic(node_input: dict[str, Any]) -> Event:
    locations = node_input.get("locations", [])
    date_val = node_input.get("date")
    is_ambiguous = node_input.get("is_ambiguous", False)
    state_updates = {
        "locations": locations,
        "date": date_val,
        "needs_physics": node_input.get("needs_physics", False),
        "needs_impact": node_input.get("needs_impact", False),
        "needs_local_knowledge": node_input.get("needs_local_knowledge", False),
    }

    if is_ambiguous or not locations:
        return Event(output=node_input, route="missing_location", state=state_updates)
    if not date_val:
        return Event(output=node_input, route="missing_date", state=state_updates)
    if len(locations) > 5:
        return Event(output=node_input, route="too_many_locations", state=state_updates)

    return Event(output=node_input, route="no", state=state_updates)


@node
def check_ambiguity(ctx: Context, node_input: dict[str, Any]) -> Event:
    return _check_ambiguity_logic(node_input)


@node(rerun_on_resume=False)
async def clarify_location(ctx: Context, node_input: Any) -> Event:
    interrupt_id = f"clarify_loc_{ctx.state.get('loop_count', 0)}"
    if not ctx.resume_inputs or interrupt_id not in ctx.resume_inputs:
        yield RequestInput(
            interrupt_id=interrupt_id,
            message="Do you want a forecast for a specific location, or a comparison of up to 5 regions (e.g., 'Scottish areas')?",
        )
        return

    clarification = ctx.resume_inputs[interrupt_id]
    state_updates = {"locations": [clarification]}
    yield Event(output=clarification, state=state_updates)


@node(rerun_on_resume=False)
async def clarify_date(ctx: Context, node_input: Any) -> Event:
    interrupt_id = f"clarify_date_{ctx.state.get('loop_count', 0)}"
    if not ctx.resume_inputs or interrupt_id not in ctx.resume_inputs:
        yield RequestInput(
            interrupt_id=interrupt_id,
            message="Do you want the forecast for a specific date, or the full three-day forecast with outlook?",
        )
        return

    clarification = ctx.resume_inputs[interrupt_id]
    state_updates = {"date": clarification}
    yield Event(output=clarification, state=state_updates)


@node(rerun_on_resume=False)
async def clarify_too_many_locations(ctx: Context, node_input: Any) -> Event:
    interrupt_id = f"clarify_many_{ctx.state.get('loop_count', 0)}"
    if not ctx.resume_inputs or interrupt_id not in ctx.resume_inputs:
        yield RequestInput(
            interrupt_id=interrupt_id,
            message="Only 5 regions can be compared. Which regions do you wish to choose? (Reminder: Scotland has 5 regions, England has 3, and Wales has 2).",
        )
        return

    clarification = ctx.resume_inputs[interrupt_id]
    state_updates = {"locations": [clarification]}
    yield Event(output=clarification, state=state_updates)


import importlib.util
import os
import asyncio


def load_query_country():
    script_path = os.path.join(
        os.path.dirname(__file__),
        "skills",
        "mwis-website",
        "fetch_specific_forecast",
        "scripts",
        "query_country.py",
    )
    spec = importlib.util.spec_from_file_location("query_country", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.get_regions_for_countries


@node
def resolve_and_fetch(ctx: Context, node_input: Any) -> Event:
    locations = ctx.state.get("locations", [])

    get_regions_for_countries = load_query_country()
    try:
        matched_regions = get_regions_for_countries(locations)
    except ValueError as e:
        # > 5 regions error
        return Event(output=node_input, route="too_many_locations")

    if not matched_regions:
        matched_regions = ["NW"]  # Default if unable to resolve

    forecasts = {}
    needs_impact = ctx.state.get("needs_impact", False)

    # We fetch sequentially for simplicity or we could use asyncio, but node is sync.
    for region in matched_regions:
        try:
            forecast = get_forecast(region)
            forecasts[region] = forecast

            # Simplified hazard detection
            if forecast and forecast.get("days"):
                day0_wind = forecast["days"][0].get("wind_headline", "").lower()
                if (
                    "gale" in day0_wind
                    or "storm" in day0_wind
                    or "hurricane" in day0_wind
                ):
                    needs_impact = True
        except Exception as e:
            forecasts[region] = {"error": str(e)}

    return Event(
        output=forecasts,
        state={
            "region_codes": matched_regions,
            "forecast_data": forecasts,
            "needs_impact": needs_impact,
        },
    )


@node
def validate_coverage(ctx: Context, node_input: Any) -> Event:
    date_str = ctx.state.get("date", "")
    if date_str:
        date_str = date_str.lower()
    else:
        date_str = ""

    if date_str == "dold" or "past" in date_str:
        return Event(output=node_input, route="dold")

    # Check if any location is out of scope
    locations = ctx.state.get("locations", [])
    if any("france" in loc.lower() for loc in locations):
        return Event(output=node_input, route="out_of_scope")

    return Event(output=node_input, route="valid")


@node
def historic_lookup(ctx: Context, node_input: Any) -> Event:
    msg = "Historic lookup is not fully implemented yet, but we'd look up old forecasts here."
    return Event(
        content=types.Content(role="model", parts=[types.Part.from_text(text=msg)]),
        output=msg,
    )


@node
def out_of_scope_msg(ctx: Context, node_input: Any) -> Event:
    msg = "Sorry, that location or date is outside the UK MWIS coverage scope."
    return Event(
        content=types.Content(role="model", parts=[types.Part.from_text(text=msg)]),
        output=msg,
    )


@node
def check_physics(ctx: Context, node_input: Any) -> Event:
    if ctx.state.get("needs_physics", False):
        return Event(output=node_input, route="yes")
    return Event(output=node_input, route="no")


@node
def weather_physics(ctx: Context, node_input: Any) -> Event:
    # Pass-through node for now
    return Event(output=node_input)


@node
def check_impact(ctx: Context, node_input: Any) -> Event:
    if ctx.state.get("needs_impact", False):
        return Event(output=node_input, route="yes")
    return Event(output=node_input, route="no")


@node
def weather_impact(ctx: Context, node_input: Any) -> Event:
    # Pass-through node for now
    return Event(output=node_input)


@node
def check_local(ctx: Context, node_input: Any) -> Event:
    if ctx.state.get("needs_local_knowledge", False):
        return Event(output=node_input, route="yes")
    return Event(output=node_input, route="no")


@node
def local_knowledge(ctx: Context, node_input: Any) -> Event:
    # Pass-through node for now
    return Event(output=node_input)


synthesis = LlmAgent(
    name="synthesis",
    model=Gemini(model="gemini-2.5-flash"),
    instruction="""
    You are a mountain weather forecaster. Using the provided state containing the MWIS forecast,
    synthesize a plain-text response to the user's raw_query. Do not mention JSON or raw data structures.
    """,
)


@node(rerun_on_resume=False)
async def ask_follow_up(ctx: Context, node_input: Any) -> Event:
    interrupt_id = f"follow_up_{ctx.state.get('loop_count', 0)}"
    if not ctx.resume_inputs or interrupt_id not in ctx.resume_inputs:
        yield RequestInput(
            interrupt_id=interrupt_id,
            message="Do you have any follow-up questions? (e.g. higher/lower elevation, specific part of the region, or 'no' to finish)",
        )
        return

    reply = ctx.resume_inputs[interrupt_id]
    yield Event(output=reply)


@node
def process_follow_up(ctx: Context, node_input: Any) -> Event:
    reply = str(node_input).strip().lower()
    if reply in ["no", "none", "no thanks", "exit", "quit", "stop"]:
        # We can route to an exit, or just return and not route back.
        # But according to graph, check_loop_limit decides if we route back.
        # So we can just set loop_count high to force exit.
        new_count = 999
    else:
        new_count = ctx.state.get("loop_count", 0) + 1

    return Event(
        output=reply, state={"loop_count": new_count, "raw_query": str(node_input)}
    )


@node
def check_loop_limit(ctx: Context, node_input: Any) -> Event:
    if ctx.state.get("loop_count", 0) < 5:
        return Event(output=node_input, route="yes")
    return Event(output=node_input, route="no")


@node
def set_raw_query(ctx: Context, node_input: Any) -> Event:
    # Captures the initial raw query from START
    content = ""
    if hasattr(node_input, "parts") and node_input.parts:
        content = node_input.parts[0].text
    return Event(output=node_input, state={"raw_query": content})


edges = [
    Edge(from_node=START, to_node=set_raw_query),
    Edge(from_node=set_raw_query, to_node=parse_input),
    Edge(from_node=parse_input, to_node=check_ambiguity),
    Edge(from_node=check_ambiguity, to_node=clarify_location, route="missing_location"),
    Edge(from_node=check_ambiguity, to_node=clarify_date, route="missing_date"),
    Edge(
        from_node=check_ambiguity,
        to_node=clarify_too_many_locations,
        route="too_many_locations",
    ),
    Edge(from_node=clarify_location, to_node=resolve_and_fetch),
    Edge(from_node=clarify_date, to_node=resolve_and_fetch),
    Edge(from_node=clarify_too_many_locations, to_node=resolve_and_fetch),
    Edge(from_node=check_ambiguity, to_node=resolve_and_fetch, route="no"),
    Edge(
        from_node=resolve_and_fetch,
        to_node=clarify_too_many_locations,
        route="too_many_locations",
    ),
    Edge(from_node=resolve_and_fetch, to_node=validate_coverage),
    Edge(from_node=validate_coverage, to_node=historic_lookup, route="dold"),
    Edge(from_node=validate_coverage, to_node=out_of_scope_msg, route="out_of_scope"),
    Edge(from_node=validate_coverage, to_node=check_physics, route="valid"),
    Edge(from_node=check_physics, to_node=weather_physics, route="yes"),
    Edge(from_node=check_physics, to_node=check_impact, route="no"),
    Edge(from_node=weather_physics, to_node=check_impact),
    Edge(from_node=check_impact, to_node=weather_impact, route="yes"),
    Edge(from_node=check_impact, to_node=check_local, route="no"),
    Edge(from_node=weather_impact, to_node=check_local),
    Edge(from_node=check_local, to_node=local_knowledge, route="yes"),
    Edge(from_node=check_local, to_node=synthesis, route="no"),
    Edge(from_node=local_knowledge, to_node=synthesis),
    Edge(from_node=synthesis, to_node=ask_follow_up),
    Edge(from_node=ask_follow_up, to_node=process_follow_up),
    Edge(from_node=process_follow_up, to_node=check_loop_limit),
    Edge(from_node=check_loop_limit, to_node=resolve_and_fetch, route="yes"),
]

root_agent = Workflow(
    name="mwis_workflow",
    edges=edges,
    state_schema=WorkflowState,
)

app = App(
    root_agent=root_agent,
    name="app",
)
