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

from google.adk.apps import App
from google.adk.workflow import START, Edge, Workflow

from app.agent_nodes import (
    ask_follow_up,
    check_ambiguity,
    check_impact,
    check_local,
    check_loop_limit,
    check_physics,
    clarify_date,
    clarify_location,
    clarify_too_many_locations,
    historic_lookup,
    local_knowledge,
    out_of_scope_msg,
    parse_input,
    process_follow_up,
    resolve_and_fetch,
    set_raw_query,
    synthesis,
    validate_coverage,
    weather_impact,
    weather_physics,
)
from app.agent_state import WorkflowState

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
