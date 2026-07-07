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

"""Forecast caching layer interface for the ADK Graph workflow."""

import os
import sys
from typing import Any

# Ensure we can import modules from check_forecast_issued
APP_DIR = os.path.dirname(os.path.abspath(__file__))
CHECKER_SCRIPTS_DIR = os.path.join(
    APP_DIR, "skills", "mwis-website", "check_forecast_issued", "scripts"
)
if CHECKER_SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, CHECKER_SCRIPTS_DIR)

from check_forecast import DEFAULT_DB_PATH, check_forecast_issued  # noqa: E402
from mwis_cache_db import db_get_forecast, db_init  # noqa: E402


def _ensure_db_exists(db_path: str) -> None:
    """Ensure database directory and tables exist.

    Args:
        db_path (str): Database file path.
    """
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    db_init(db_path)


def get_forecast(
    region_code: str, db_path: str = DEFAULT_DB_PATH
) -> dict[str, Any] | None:
    """Retrieve forecast from cache, triggering update check on miss.

    Args:
        region_code (str): MWIS region code.
        db_path (str): Path to SQLite database.

    Returns:
        Optional[dict]: Deserialized forecast dict.
    """
    _ensure_db_exists(db_path)
    forecast = db_get_forecast(region_code, db_path)
    if forecast is not None:
        return forecast

    # Cache miss: run update check to fetch and cache all regions
    env = os.getenv("MWIS_ENV", "production")
    check_forecast_issued(db_path=db_path, env=env)
    return db_get_forecast(region_code, db_path)
