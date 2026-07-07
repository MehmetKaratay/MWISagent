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

import os

from fastapi import Request
from fastapi.responses import JSONResponse
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from starlette.middleware.base import BaseHTTPMiddleware


def _is_integration_test_environment() -> bool:
    """Checks if the app is running in an integration test environment."""
    return os.getenv("INTEGRATION_TEST") == "TRUE"


def _is_path_exempt_from_auth(path: str) -> bool:
    """Checks if the given path should bypass authentication."""
    exempt_prefixes = [
        "/docs",
        "/openapi.json",
        "/redoc",
        "/feedback",
        "/.well-known/agent-card",
    ]
    return (
        any(path.startswith(prefix) for prefix in exempt_prefixes)
        or "/.well-known/" in path
    )


def _extract_bearer_token(request: Request) -> str | None:
    """Extracts the Bearer token from the Authorization header."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    return auth_header.split(" ")[1]


def _verify_google_jwt_token(token: str) -> dict | JSONResponse:
    """Verifies the Google OAuth JWT token."""
    client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
    try:
        return id_token.verify_oauth2_token(
            token, google_requests.Request(), audience=client_id
        )
    except ValueError as e:
        return JSONResponse(status_code=401, content={"detail": f"Invalid token: {e}"})


class OAuthJWTValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to intercept and validate OAuth JWT tokens for secure A2A execution endpoints.
    """

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if _is_integration_test_environment() or _is_path_exempt_from_auth(path):
            return await call_next(request)

        if path.startswith("/a2a/app"):
            token = _extract_bearer_token(request)
            if not token:
                return JSONResponse(
                    status_code=401,
                    content={
                        "detail": "Missing or invalid Authorization header. Expected 'Bearer <token>'."
                    },
                )

            idinfo = _verify_google_jwt_token(token)
            if isinstance(idinfo, JSONResponse):
                return idinfo

            request.state.user = idinfo

        return await call_next(request)
