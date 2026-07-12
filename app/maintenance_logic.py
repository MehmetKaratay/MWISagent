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

"""Helper logic for maintenance and database refresh nodes."""


def route_raw_query(
    content: str, is_awaiting_force: bool, hidden_cmd: str | None
) -> str:
    """Determine workflow routing destination based on raw query text.

    Args:
        content (str): The raw user query text.
        is_awaiting_force (bool): True if workflow state is awaiting force reply.
        hidden_cmd (Optional[str]): Configured secret command string.

    Returns:
        str: Route name matching "refresh_forced", "refresh", or "default".
    """
    if is_awaiting_force and content.strip().lower() == "force":
        return "refresh_forced"
    if hidden_cmd and content.strip() == hidden_cmd.strip():
        return "refresh"
    return "default"


def check_refresh_response(status: str) -> tuple[str, bool]:
    """Return confirmation response message and state flag based on update status.

    Args:
        status (str): Update status returned from check_forecast_issued.

    Returns:
        tuple[str, bool]: Response text message and awaiting_refresh_force flag.
    """
    if status == "updated":
        return "Database refreshed successfully.", False
    msg = (
        "Database refresh is not required at this time because the forecast is "
        "already up-to-date. Reply with 'force' to proceed anyway."
    )
    return msg, True
