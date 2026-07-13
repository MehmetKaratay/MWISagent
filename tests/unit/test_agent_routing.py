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
"""
Unit tests for ADK workflow ambiguity routing.
"""

from app.agent_logic import _check_ambiguity_logic


class MockContext:
    def __init__(self, state=None):
        self.state = state or {}


def test_check_ambiguity_missing_location():
    """Test routing when location is completely missing."""
    node_input = {"locations": [], "date": "today"}
    ctx = MockContext()
    event = _check_ambiguity_logic(ctx, node_input)
    assert event.model_dump()["actions"]["route"] == "missing_location"


def test_check_ambiguity_missing_date():
    """Test routing when date is completely missing."""
    node_input = {"locations": ["Scotland"], "date": None}
    ctx = MockContext()
    event = _check_ambiguity_logic(ctx, node_input)
    assert event.model_dump()["actions"]["route"] == "missing_date"


def test_check_ambiguity_too_many_locations():
    """Test routing when > 5 regions are returned directly from parser."""
    node_input = {"locations": ["NW", "WH", "EH", "SD", "LD", "PD"], "date": "today"}
    ctx = MockContext()
    event = _check_ambiguity_logic(ctx, node_input)
    assert event.model_dump()["actions"]["route"] == "too_many_locations"


def test_check_ambiguity_explicitly_ambiguous():
    """Test routing when parser explicitly flags ambiguity."""
    node_input = {"locations": ["Somewhere"], "date": "today", "is_ambiguous": True}
    ctx = MockContext()
    event = _check_ambiguity_logic(ctx, node_input)
    assert event.model_dump()["actions"]["route"] == "missing_location"


def test_check_ambiguity_valid():
    """Test routing when all inputs are perfectly clear."""
    node_input = {"locations": ["Ben Nevis"], "date": "today"}
    ctx = MockContext()
    event = _check_ambiguity_logic(ctx, node_input)
    assert event.model_dump()["actions"]["route"] == "no"


def test_check_ambiguity_is_new_query_strict_validation():
    """Test that a follow-up query flagged as is_new_query without reset keywords does NOT wipe the retained date."""
    # Simulate turn 1 setting the date
    ctx = MockContext(
        state={
            "locations": ["Ben Nevis"],
            "date": "D1",
            "raw_query": "and for cairngorm?",
        }
    )

    # Turn 2: Follow-up location but LLM incorrectly flags is_new_query=True
    node_input = {"locations": ["Cairngorm"], "date": None, "is_new_query": True}
    event = _check_ambiguity_logic(ctx, node_input)

    # State should NOT have been wiped because "reset" keywords aren't in raw_query
    assert event.model_dump()["actions"]["route"] == "no"
    assert ctx.state["date"] == "D1"


def test_resolve_and_fetch_date_resolution():
    """Test that _resolve_and_fetch_logic correctly resolves date to MWIS codes."""
    from app.agent_logic import _resolve_and_fetch_logic

    class MockContext:
        def __init__(self, state):
            self.state = state

    ctx = MockContext(
        state={
            "locations": ["Ben Nevis"],
            "date": "today",
        }
    )
    event = _resolve_and_fetch_logic(ctx, None)
    state_updates = event.model_dump()["actions"]["state_delta"]
    assert "resolved_date_codes" in state_updates
    assert "D0" in state_updates["resolved_date_codes"]


def test_location_rules_prompt_extraction():
    """Verify that location names like peaks are cleanly matched to region codes."""
    from app.agent_logic import _match_regions

    regions, limit_err = _match_regions(["Ben Nevis"])
    assert not limit_err
    assert "WH" in regions
