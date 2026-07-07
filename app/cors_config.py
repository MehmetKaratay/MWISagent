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


def get_allow_origins() -> list[str]:
    """Parses and validates the ALLOW_ORIGINS environment variable."""
    allow_origins_raw = os.getenv("ALLOW_ORIGINS")
    if allow_origins_raw:
        allow_origins = [origin.strip() for origin in allow_origins_raw.split(",")]
        if "*" in allow_origins:
            raise ValueError(
                "Wildcard (*) CORS origins are strictly forbidden in production."
            )
        return allow_origins

    # Default to an empty list rather than None to prevent ADK from falling back to ["*"]
    return []
