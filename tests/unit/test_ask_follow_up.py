import pytest
from google.adk.events.request_input import RequestInput

from app.agent_nodes import _ask_follow_up_logic


class MockContext:
    def __init__(self, state, resume_inputs):
        self.state = state
        self.resume_inputs = resume_inputs


@pytest.mark.asyncio
async def test_ask_follow_up_includes_forecast():
    ctx = MockContext(state={"loop_count": 0}, resume_inputs={})
    forecast = "The weather on Ben Nevis will be clear and sunny."

    # Run the generator
    generator = _ask_follow_up_logic(ctx, forecast)
    result = await anext(generator)

    assert isinstance(result, RequestInput)
    assert forecast in result.message
    assert "Do you have any follow-up questions?" in result.message
