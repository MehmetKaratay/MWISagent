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
Unit tests for downstream ADK workflow routing nodes.
"""

from app.agent_logic import (
    _check_impact_logic,
    _check_local_logic,
    _check_loop_limit_logic,
    _check_physics_logic,
    _validate_coverage_logic,
)


class MockContext:
    def __init__(self, state=None):
        self.state = state or {}


def test_validate_coverage_dold():
    ctx = MockContext(state={"date": "dold", "locations": ["Ben Nevis"]})
    event = _validate_coverage_logic(ctx, {})
    assert event.model_dump()["actions"]["route"] == "dold"

    ctx = MockContext(state={"date": "past week", "locations": ["Ben Nevis"]})
    event = _validate_coverage_logic(ctx, {})
    assert event.model_dump()["actions"]["route"] == "dold"


def test_validate_coverage_out_of_scope():
    ctx = MockContext(state={"date": "today", "locations": ["Chamonix, France"]})
    event = _validate_coverage_logic(ctx, {})
    assert event.model_dump()["actions"]["route"] == "out_of_scope"


def test_validate_coverage_valid():
    ctx = MockContext(state={"date": "tomorrow", "locations": ["Peak District"]})
    event = _validate_coverage_logic(ctx, {})
    assert event.model_dump()["actions"]["route"] == "valid"


def test_check_physics():
    ctx = MockContext(state={"needs_physics": True})
    event = _check_physics_logic(ctx, {})
    assert event.model_dump()["actions"]["route"] == "yes"

    ctx = MockContext(state={"needs_physics": False})
    event = _check_physics_logic(ctx, {})
    assert event.model_dump()["actions"]["route"] == "no"


def test_check_impact():
    ctx = MockContext(state={"needs_impact": True})
    event = _check_impact_logic(ctx, {})
    assert event.model_dump()["actions"]["route"] == "yes"

    ctx = MockContext(state={"needs_impact": False})
    event = _check_impact_logic(ctx, {})
    assert event.model_dump()["actions"]["route"] == "no"


def test_check_local():
    ctx = MockContext(state={"needs_local_knowledge": True})
    event = _check_local_logic(ctx, {})
    assert event.model_dump()["actions"]["route"] == "yes"

    ctx = MockContext(state={"needs_local_knowledge": False})
    event = _check_local_logic(ctx, {})
    assert event.model_dump()["actions"]["route"] == "no"


def test_check_loop_limit():
    ctx = MockContext(state={"loop_count": 0})
    event = _check_loop_limit_logic(ctx, {})
    assert event.model_dump()["actions"]["route"] == "yes"

    ctx = MockContext(state={"loop_count": 4})
    event = _check_loop_limit_logic(ctx, {})
    assert event.model_dump()["actions"]["route"] == "yes"

    ctx = MockContext(state={"loop_count": 5})
    event = _check_loop_limit_logic(ctx, {})
    assert event.model_dump()["actions"]["route"] == "no"

    ctx = MockContext(state={"loop_count": 10})
    event = _check_loop_limit_logic(ctx, {})
    assert event.model_dump()["actions"]["route"] == "no"
