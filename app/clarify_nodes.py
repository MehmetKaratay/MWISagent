# MWIS Agent (c) by Mehmet Rahmi Karatay
#
# MWIS Agent is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License.
#
# You should have received a copy of the license along with this
# work.  If not, see <https://creativecommons.org/licenses/by-sa/4.0/>.
"""Human-in-the-loop clarification nodes for the MWIS weather agent."""

from typing import Any

from google.adk.agents.context import Context
from google.adk.events.event import Event
from google.adk.events.request_input import RequestInput
from google.adk.workflow import node


@node(rerun_on_resume=False)
async def clarify_location(ctx: Context, node_input: Any) -> Event:
    """Human-in-the-loop node to clarify an unspecified or ambiguous location."""
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
    """Human-in-the-loop node to clarify an unspecified date constraint."""
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
    """Human-in-the-loop node to prompt the user to narrow down regions when requesting more than 5."""
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
