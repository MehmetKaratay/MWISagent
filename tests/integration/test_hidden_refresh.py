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

"""Integration tests for the hidden database refresh command."""

import os
import unittest
from unittest.mock import patch

from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agent import root_agent


class TestHiddenRefresh(unittest.TestCase):
    """Test suite for the hidden database refresh command routing and execution."""

    def setUp(self):
        """Set up test environment."""
        os.environ["HIDDEN_REFRESH_COMMAND"] = "force-mwis-db-refresh"
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=root_agent,
            session_service=self.session_service,
            app_name="test",
        )

    def tearDown(self):
        """Clean up test environment."""
        if "HIDDEN_REFRESH_COMMAND" in os.environ:
            del os.environ["HIDDEN_REFRESH_COMMAND"]

    @patch("app.agent_nodes.check_forecast_issued")
    def test_hidden_refresh_command_not_eligible(self, mock_check):
        """Test that hidden command triggers prompt when refresh is not needed."""
        # Mocking check_forecast_issued to return skipped status (not eligible)
        mock_check.return_value = {
            "status": "already_updated_today",
            "message": "Update skipped due to schedule or previous runs.",
        }

        session = self.session_service.create_session_sync(
            user_id="test_user", app_name="test"
        )
        message = types.Content(
            role="user",
            parts=[types.Part.from_text(text="force-mwis-db-refresh")],
        )

        events = list(
            self.runner.run(
                new_message=message,
                user_id="test_user",
                session_id=session.id,
                run_config=RunConfig(streaming_mode=StreamingMode.SSE),
            )
        )
        self.assertTrue(len(events) > 0)

        # Confirm response prompt
        response_text = "".join(
            part.text
            for event in events
            if event.content and event.content.parts
            for part in event.content.parts
            if part.text
        )
        self.assertIn("Database refresh is not required", response_text)
        self.assertIn("Reply with 'force' to proceed", response_text)

        # Verify state is updated to await force
        session = self.session_service.get_session_sync(
            user_id="test_user", session_id=session.id, app_name="test"
        )
        self.assertTrue(session.state.get("awaiting_refresh_force"))

        # Now reply with "force" to trigger forced update
        mock_check.reset_mock()
        mock_check.return_value = {
            "status": "updated",
            "message": "Force update succeeded",
        }

        force_message = types.Content(
            role="user", parts=[types.Part.from_text(text="force")]
        )
        force_events = list(
            self.runner.run(
                new_message=force_message,
                user_id="test_user",
                session_id=session.id,
                run_config=RunConfig(streaming_mode=StreamingMode.SSE),
            )
        )
        self.assertTrue(len(force_events) > 0)

        force_response = "".join(
            part.text
            for event in force_events
            if event.content and event.content.parts
            for part in event.content.parts
            if part.text
        )
        self.assertIn("Database refresh successfully forced", force_response)
        mock_check.assert_called_once()
        self.assertTrue(mock_check.call_args[1].get("force_update"))

        # Verify state flag is reset
        session = self.session_service.get_session_sync(
            user_id="test_user", session_id=session.id, app_name="test"
        )
        self.assertFalse(session.state.get("awaiting_refresh_force"))

    @patch("app.agent_nodes.check_forecast_issued")
    def test_hidden_refresh_command_eligible(self, mock_check):
        """Test that hidden command refreshes immediately when eligible."""
        mock_check.return_value = {
            "status": "updated",
            "message": "Update succeeded",
        }

        session = self.session_service.create_session_sync(
            user_id="test_user", app_name="test"
        )
        message = types.Content(
            role="user",
            parts=[types.Part.from_text(text="force-mwis-db-refresh")],
        )

        events = list(
            self.runner.run(
                new_message=message,
                user_id="test_user",
                session_id=session.id,
                run_config=RunConfig(streaming_mode=StreamingMode.SSE),
            )
        )
        self.assertTrue(len(events) > 0)

        response_text = "".join(
            part.text
            for event in events
            if event.content and event.content.parts
            for part in event.content.parts
            if part.text
        )
        self.assertIn("Database refreshed successfully", response_text)
        mock_check.assert_called_once()
        self.assertFalse(mock_check.call_args[1].get("force_update"))
