# MWIS Agent (c) by Mehmet Rahmi Karatay
#
# MWIS Agent is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License.
#
# You should have received a copy of the license along with this
# work.  If not, see <https://creativecommons.org/licenses/by-sa/4.0/>.

"""Deterministic resolver for relative date code shifts."""


def resolve_shift(current_code: str, query: str) -> str:
    """Calculate relative date shifts (forward/backward) for MWIS day codes.

    Args:
        current_code (str): The active forecast day code (e.g. 'D0', 'D1', 'D2', 'D3').
        query (str): Fuzzy user query expressing shift direction.

    Returns:
        str: The newly shifted MWIS day code.
    """
    if current_code not in ["D0", "D1", "D2", "D3"]:
        return "D0"

    norm = query.strip().lower()

    # Define forwards and backwards expressions
    forwards = ["following day", "next day", "day after", "tomorrow"]
    backwards = ["day before", "previous day", "yesterday"]

    steps = ["D0", "D1", "D2", "D3"]
    curr_idx = steps.index(current_code)

    if any(f in norm for f in forwards):
        new_idx = min(curr_idx + 1, len(steps) - 1)
        return steps[new_idx]

    if any(b in norm for b in backwards):
        new_idx = max(curr_idx - 1, 0)
        return steps[new_idx]

    return current_code
