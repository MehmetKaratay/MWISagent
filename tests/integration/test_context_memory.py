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


def test_context_memory_retention() -> None:
    """Integration test to verify contextual memory retention and category/location/date updates."""
    session_service = InMemorySessionService()
    session = session_service.create_session_sync(user_id="test_user", app_name="test")
    runner = Runner(agent=root_agent, session_service=session_service, app_name="test")

    # Turn 1: Specific category detail request
    msg1 = types.Content(
        role="user",
        parts=[types.Part.from_text(text="Is it cloudy in West Highlands today?")],
    )
    events1 = list(
        runner.run(
            new_message=msg1,
            user_id="test_user",
            session_id=session.id,
            run_config=RunConfig(streaming_mode=StreamingMode.SSE),
        )
    )
    assert len(events1) > 0

    session = session_service.get_session_sync(
        user_id="test_user", session_id=session.id, app_name="test"
    )
    assert "WH" in session.state.get("region_codes", [])
    assert "D0" in session.state.get("resolved_date_codes", [])
    assert "cloud" in session.state.get("extracted_categories", [])

    # Turn 2: Relative date shift "what about the following day?" (should retain WH, cloud, and shift date to D1)
    msg2 = types.Content(
        role="user", parts=[types.Part.from_text(text="what about the following day?")]
    )
    events2 = list(
        runner.run(
            new_message=msg2,
            user_id="test_user",
            session_id=session.id,
            run_config=RunConfig(streaming_mode=StreamingMode.SSE),
        )
    )
    assert len(events2) > 0

    session = session_service.get_session_sync(
        user_id="test_user", session_id=session.id, app_name="test"
    )
    assert "WH" in session.state.get("region_codes", [])
    assert "D1" in session.state.get("resolved_date_codes", [])
    assert "cloud" in session.state.get("extracted_categories", [])

    # Turn 3: New query context / reset (should clear memory and load Brecon Beacons, tomorrow, and empty categories)
    msg3 = types.Content(
        role="user", parts=[types.Part.from_text(text="reset Brecon Beacons tomorrow")]
    )
    events3 = list(
        runner.run(
            new_message=msg3,
            user_id="test_user",
            session_id=session.id,
            run_config=RunConfig(streaming_mode=StreamingMode.SSE),
        )
    )
    assert len(events3) > 0

    session = session_service.get_session_sync(
        user_id="test_user", session_id=session.id, app_name="test"
    )
    assert "BB" in session.state.get("region_codes", [])
    assert "D1" in session.state.get("resolved_date_codes", [])
    assert "cloud" not in session.state.get("extracted_categories", [])


def test_location_switch_retains_context() -> None:
    """Verify that shifting to a new location preserves date and category context if not explicitly reset."""
    session_service = InMemorySessionService()
    session = session_service.create_session_sync(user_id="test_user", app_name="test")
    runner = Runner(agent=root_agent, session_service=session_service, app_name="test")

    # Turn 1: Ben Nevis Cloud tomorrow
    msg1 = types.Content(
        role="user", parts=[types.Part.from_text(text="Ben Nevis Cloud tomorrow")]
    )
    events1 = list(
        runner.run(
            new_message=msg1,
            user_id="test_user",
            session_id=session.id,
            run_config=RunConfig(streaming_mode=StreamingMode.SSE),
        )
    )
    assert len(events1) > 0

    session = session_service.get_session_sync(
        user_id="test_user", session_id=session.id, app_name="test"
    )
    assert "WH" in session.state.get("region_codes", [])
    assert "D1" in session.state.get("resolved_date_codes", [])
    assert "cloud" in session.state.get("extracted_categories", [])

    # Turn 2: And for Cairngorm?
    msg2 = types.Content(
        role="user", parts=[types.Part.from_text(text="And for Cairngorm?")]
    )
    events2 = list(
        runner.run(
            new_message=msg2,
            user_id="test_user",
            session_id=session.id,
            run_config=RunConfig(streaming_mode=StreamingMode.SSE),
        )
    )
    assert len(events2) > 0

    session = session_service.get_session_sync(
        user_id="test_user", session_id=session.id, app_name="test"
    )
    assert "EH" in session.state.get("region_codes", [])
    assert "D1" in session.state.get("resolved_date_codes", [])
    assert "cloud" in session.state.get("extracted_categories", [])
