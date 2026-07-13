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

from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agent import root_agent


def test_agent_stream() -> None:
    """
    Integration test for the agent stream functionality.
    Tests that the agent returns valid streaming responses.
    """

    session_service = InMemorySessionService()

    session = session_service.create_session_sync(user_id="test_user", app_name="test")
    runner = Runner(agent=root_agent, session_service=session_service, app_name="test")

    message = types.Content(
        role="user", parts=[types.Part.from_text(text="Why is the sky blue?")]
    )

    events = list(
        runner.run(
            new_message=message,
            user_id="test_user",
            session_id=session.id,
            run_config=RunConfig(streaming_mode=StreamingMode.SSE),
        )
    )
    assert len(events) > 0, "Expected at least one message"

    has_text_content = False
    for event in events:
        if (
            event.content
            and event.content.parts
            and any(part.text for part in event.content.parts)
        ):
            has_text_content = True
            break
    assert has_text_content, "Expected at least one message with text content"


def test_agent_restricts_forecast_to_day() -> None:
    """
    Test that the agent updates state with resolved_date_codes and restricts the synthesized response
    to only the requested day if specific Dcode is asked.
    """
    session_service = InMemorySessionService()
    session = session_service.create_session_sync(user_id="test_user", app_name="test")
    runner = Runner(agent=root_agent, session_service=session_service, app_name="test")

    message = types.Content(
        role="user", parts=[types.Part.from_text(text="today forecast for Snowdon")]
    )

    events = list(
        runner.run(
            new_message=message,
            user_id="test_user",
            session_id=session.id,
            run_config=RunConfig(streaming_mode=StreamingMode.SSE),
        )
    )
    assert len(events) > 0

    # Let's inspect the final workflow state in session
    session = session_service.get_session_sync(
        user_id="test_user", session_id=session.id, app_name="test"
    )
    state = session.state
    assert "resolved_date_codes" in state
    assert "D0" in state["resolved_date_codes"]


def test_agent_restricts_forecast_to_tomorrow() -> None:
    """
    Test that the agent restricts the synthesized response to only tomorrow (D1) when tomorrow is requested.
    """
    session_service = InMemorySessionService()
    session = session_service.create_session_sync(user_id="test_user", app_name="test")
    runner = Runner(agent=root_agent, session_service=session_service, app_name="test")

    message = types.Content(
        role="user", parts=[types.Part.from_text(text="Ben Nevis cloud tomorrow")]
    )

    events = list(
        runner.run(
            new_message=message,
            user_id="test_user",
            session_id=session.id,
            run_config=RunConfig(streaming_mode=StreamingMode.SSE),
        )
    )
    assert len(events) > 0

    session = session_service.get_session_sync(
        user_id="test_user", session_id=session.id, app_name="test"
    )
    state = session.state
    assert "resolved_date_codes" in state
    assert state["resolved_date_codes"] == ["D1"]

    # Assert that forecast_data contains only one day (Day 1)
    assert "forecast_data" in state
    forecast_data = state["forecast_data"]
    for data in forecast_data.values():
        if "days" in data:
            assert (
                len(data["days"]) == 1
            ), f"Expected 1 day in forecast, got {len(data['days'])}: {data['days']}"
            assert data["days"][0]["Dcode"] == "D1"
