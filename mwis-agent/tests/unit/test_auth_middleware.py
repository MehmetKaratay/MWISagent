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
Unit tests for the OAuth JWT Validation Middleware.
"""

import os
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.auth_middleware import OAuthJWTValidationMiddleware

# Create a dummy FastAPI app to test the middleware
app = FastAPI()
app.add_middleware(OAuthJWTValidationMiddleware)


@app.post("/a2a/app/message")
def dummy_message():
    """Dummy secure endpoint."""
    return {"status": "success"}


@app.get("/a2a/app/.well-known/agent-card")
def dummy_agent_card():
    """Dummy public endpoint."""
    return {"status": "public"}


@app.get("/docs")
def dummy_docs():
    """Dummy docs endpoint."""
    return {"status": "docs"}


client = TestClient(app)


def test_missing_auth_header():
    """Test that missing auth header returns 401 on protected route."""
    response = client.post("/a2a/app/message")
    assert response.status_code == 401
    assert "Missing or invalid Authorization header" in response.json()["detail"]


def test_invalid_auth_header_format():
    """Test that non-Bearer auth header returns 401."""
    response = client.post("/a2a/app/message", headers={"Authorization": "Basic 1234"})
    assert response.status_code == 401


def test_exempt_paths_are_allowed():
    """Test that exempt paths bypass the authentication check."""
    response = client.get("/a2a/app/.well-known/agent-card")
    assert response.status_code == 200
    assert response.json() == {"status": "public"}

    response = client.get("/docs")
    assert response.status_code == 200


@patch("google.oauth2.id_token.verify_oauth2_token")
@patch.dict(os.environ, {"GOOGLE_OAUTH_CLIENT_ID": "test_audience"})
def test_valid_token(mock_verify):
    """Test that a valid Google JWT passes authentication."""
    mock_verify.return_value = {"sub": "12345", "email": "test@example.com"}

    response = client.post(
        "/a2a/app/message", headers={"Authorization": "Bearer valid_token"}
    )

    assert response.status_code == 200
    assert response.json() == {"status": "success"}

    # Verify it checked the audience
    mock_verify.assert_called_once()
    assert mock_verify.call_args[1].get("audience") == "test_audience"


@patch("google.oauth2.id_token.verify_oauth2_token")
def test_invalid_token(mock_verify):
    """Test that an invalid Google JWT returns 401."""
    mock_verify.side_effect = ValueError("Token used too early")

    response = client.post(
        "/a2a/app/message", headers={"Authorization": "Bearer invalid_token"}
    )

    assert response.status_code == 401
    assert "Invalid token" in response.json()["detail"]
