import asyncio

from app.agent import check_physics


class MockContext:
    def __init__(self, state):
        self.state = state


async def main():
    ctx = MockContext({"needs_physics": True})
    event = await check_physics.run(context=ctx, input_data={})
    print(event.model_dump()["actions"]["route"])


asyncio.run(main())
