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

"""Workflow nodes executing database maintenance and refresh commands."""

import os
import sys
from typing import Any

# Ensure we can import check_forecast_issued
APP_DIR = os.path.dirname(os.path.abspath(__file__))
CHECKER_SCRIPTS_DIR = os.path.join(
    APP_DIR, "skills", "mwis-website", "check_forecast_issued", "scripts"
)
if CHECKER_SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, CHECKER_SCRIPTS_DIR)

from check_forecast import check_forecast_issued  # noqa: E402
from google.adk.agents.context import Context  # noqa: E402
from google.adk.events.event import Event  # noqa: E402
from google.adk.workflow import node  # noqa: E402
from google.genai import types  # noqa: E402

from app.maintenance_logic import (  # noqa: E402
    check_refresh_response,
    route_raw_query,
)


@node
def set_raw_query(ctx: Context, node_input: Any) -> Event:
    """Isolate raw query inside tags and dynamically route if matched to commands."""
    content = ""
    if hasattr(node_input, "parts") and node_input.parts:
        content = node_input.parts[0].text

    isolated_input = f"<user_input>{content}</user_input>"
    new_content = types.Content(
        role="user", parts=[types.Part.from_text(text=isolated_input)]
    )

    hidden_cmd = os.environ.get("HIDDEN_REFRESH_COMMAND")
    is_awaiting = ctx.state.get("awaiting_refresh_force", False)
    route = route_raw_query(content, is_awaiting, hidden_cmd)

    new_state = {"raw_query": content}
    if route == "refresh_forced":
        new_state["awaiting_refresh_force"] = False

    return Event(output=new_content, route=route, state=new_state)


@node
def check_refresh(ctx: Context, node_input: Any) -> Event:
    """Node to run standard eligibility refresh check."""
    use_live = os.environ.get("USE_LIVE_FORECAST", "false").lower() == "true"
    res = check_forecast_issued(use_live_forecast=use_live)
    msg, awaiting = check_refresh_response(res.get("status", ""))
    return Event(
        content=types.Content(role="model", parts=[types.Part.from_text(text=msg)]),
        output=msg,
        state={"awaiting_refresh_force": awaiting},
    )


@node
def force_refresh(ctx: Context, node_input: Any) -> Event:
    """Node to atomically force a database refresh."""
    use_live = os.environ.get("USE_LIVE_FORECAST", "false").lower() == "true"
    check_forecast_issued(use_live_forecast=use_live, force_update=True)
    msg = "Database refresh successfully forced!"
    return Event(
        content=types.Content(role="model", parts=[types.Part.from_text(text=msg)]),
        output=msg,
        state={"awaiting_refresh_force": False},
    )
