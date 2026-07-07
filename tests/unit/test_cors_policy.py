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
Unit tests for strict CORS policy implementation.
"""

import os
from unittest.mock import patch

import pytest


def test_wildcard_cors_raises_value_error():
    """Test that setting ALLOW_ORIGINS with a wildcard raises ValueError."""
    with patch.dict(os.environ, {"ALLOW_ORIGINS": "http://localhost:8080, *"}):
        from app.cors_config import get_allow_origins

        with pytest.raises(
            ValueError, match="Wildcard \\(\\*\\) CORS origins are strictly forbidden"
        ):
            get_allow_origins()


def test_valid_cors_does_not_raise():
    """Test that valid ALLOW_ORIGINS does not raise ValueError."""
    with patch.dict(
        os.environ, {"ALLOW_ORIGINS": "http://localhost:8080,http://127.0.0.1:8080"}
    ):
        try:
            from app.cors_config import get_allow_origins

            origins = get_allow_origins()
            assert origins == ["http://localhost:8080", "http://127.0.0.1:8080"]
        except ValueError as e:
            pytest.fail(f"Unexpected ValueError raised for valid ALLOW_ORIGINS: {e}")
