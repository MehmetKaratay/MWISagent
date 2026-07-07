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


def test_check_ambiguity_missing_location():
    """Test routing when location is completely missing."""
    node_input = {"locations": [], "date": "today"}
    event = _check_ambiguity_logic(node_input)
    assert event.model_dump()["actions"]["route"] == "missing_location"


def test_check_ambiguity_missing_date():
    """Test routing when date is completely missing."""
    node_input = {"locations": ["Scotland"], "date": None}
    event = _check_ambiguity_logic(node_input)
    assert event.model_dump()["actions"]["route"] == "missing_date"


def test_check_ambiguity_too_many_locations():
    """Test routing when > 5 regions are returned directly from parser."""
    node_input = {"locations": ["NW", "WH", "EH", "SD", "LD", "PD"], "date": "today"}
    event = _check_ambiguity_logic(node_input)
    assert event.model_dump()["actions"]["route"] == "too_many_locations"


def test_check_ambiguity_explicitly_ambiguous():
    """Test routing when parser explicitly flags ambiguity."""
    node_input = {"locations": ["Somewhere"], "date": "today", "is_ambiguous": True}
    event = _check_ambiguity_logic(node_input)
    assert event.model_dump()["actions"]["route"] == "missing_location"


def test_check_ambiguity_valid():
    """Test routing when all inputs are perfectly clear."""
    node_input = {"locations": ["Ben Nevis"], "date": "today"}
    event = _check_ambiguity_logic(node_input)
    assert event.model_dump()["actions"]["route"] == "no"
