# MWIS Agent (c) by Mehmet Rahmi Karatay
#
# MWIS Agent is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License.
#
# You should have received a copy of the license along with this
# work.  If not, see <https://creativecommons.org/licenses/by-sa/4.0/>.

"""Core orchestration script to check for new forecasts and update SQLite."""

import datetime
import os
import sqlite3
import sys
from typing import Any
from zoneinfo import ZoneInfo

# Set up paths to import other local skills
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# fetch_specific_forecast path
FETCH_SPECIFIC_DIR = os.path.abspath(
    os.path.join(SCRIPT_DIR, "..", "..", "fetch_specific_forecast", "scripts")
)
if FETCH_SPECIFIC_DIR not in sys.path:
    sys.path.insert(0, FETCH_SPECIFIC_DIR)

from inject_Dcodes import inject_d_codes  # noqa: E402
from mwis_cache_db import db_init, db_update_forecasts  # noqa: E402
from parse_forecast import get_forecast_data, parse_forecast_html  # noqa: E402
from query_url import get_forecast_url  # noqa: E402
from schedule_helper import is_time_in_schedule  # noqa: E402

DEFAULT_DB_PATH = os.path.abspath(
    os.path.join(SCRIPT_DIR, "..", "..", "..", "..", "cache", "mwis_forecasts.db")
)
MOCKS_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "mocks"))


def get_all_region_codes() -> list[str]:
    """Return the hardcoded list of 10 MWIS region codes.

    Returns:
        list[str]: Region codes.
    """
    return ["NW", "WH", "EH", "SH", "SU", "LD", "YD", "PD", "SD", "BB"]


def fetch_and_parse_region(
    region_code: str, env: str = "production", ref_date: datetime.date | None = None
) -> dict[str, Any]:
    """Fetch and parse MWIS forecast for a given region.

    Uses mock HTML files in development mode or queries the live URL in production.

    Args:
        region_code (str): The code of the region.
        env (str): 'production' or 'development'.
        ref_date (date, optional): Reference date for injecting Dcodes.

    Returns:
        dict: Parsed and injected forecast dictionary.
    """
    if env == "development":
        mock_file = os.path.join(MOCKS_DIR, f"{region_code}-mock.html")
        if not os.path.exists(mock_file):
            raise FileNotFoundError(f"Mock file not found: {mock_file}")
        # nosemgrep: detect-path-traversal
        with open(mock_file, encoding="utf-8") as f:
            html = f.read()
        parsed = parse_forecast_html(html)
    else:
        url = get_forecast_url(region_code)
        parsed = get_forecast_data(url)

    # Inject Dcodes
    if ref_date is None:
        ref_date = datetime.datetime.now(ZoneInfo("Europe/London")).date()

    return inject_d_codes(parsed, ref_date)


def check_forecast_issued(
    db_path: str | None = None,
    env: str = "production",
    current_time: datetime.datetime | None = None,
) -> dict[str, Any]:
    """Deterministically check if the forecast has been newly issued and update cache.

    Args:
        db_path (str, optional): Target SQLite DB file path.
        env (str): Environment ('production' or 'development').
        current_time (datetime, optional): Explicit override for current checking time.

    Returns:
        dict: Ingestion/check status information.
    """
    if db_path is None:
        db_path = os.getenv("MWIS_DB_PATH", DEFAULT_DB_PATH)

    # Initialize SQLite database file & schema
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    db_init(db_path)

    # Determine execution time
    if current_time is None:
        current_time = datetime.datetime.now(ZoneInfo("Europe/London"))
    else:
        if current_time.tzinfo is None:
            current_time = current_time.replace(tzinfo=datetime.timezone.utc)

    # Step 1: Verify scheduler timeline bounds
    if not is_time_in_schedule(current_time):
        return {
            "status": "no_update",
            "message": "Out of scheduled checking hours.",
            "timestamp": current_time.isoformat(),
        }

    # Step 2: Verify if update has already run today
    today_str = current_time.astimezone(ZoneInfo("Europe/London")).strftime("%Y-%m-%d")
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        # Check if we have cached records created today (in Europe/London local date)
        cursor.execute(
            """
            SELECT count(*) FROM forecast_cache
            WHERE date(cached_at, 'localtime') = ?;
            """,
            (today_str,),
        )
        already_updated = cursor.fetchone()[0]
        if already_updated > 0:
            return {
                "status": "already_updated_today",
                "message": "Forecast update has already been applied today.",
                "timestamp": current_time.isoformat(),
            }
    finally:
        conn.close()

    # Step 3: Fetch NW (North West Highlands) region to verify if it is new
    try:
        ref_date = current_time.astimezone(ZoneInfo("Europe/London")).date()
        nw_forecast = fetch_and_parse_region("NW", env, ref_date)
    except Exception as err:
        return {
            "status": "error",
            "message": f"Failed checking NW forecast: {err}",
            "timestamp": current_time.isoformat(),
        }

    # Deterministic check: check if forecast_index == 0 Dcode is D1
    days = nw_forecast.get("days", [])
    if not days:
        return {
            "status": "no_update",
            "message": "No forecast days found in parsed NW result.",
            "timestamp": current_time.isoformat(),
        }

    first_day = days[0]
    dcode = first_day.get("Dcode")

    if dcode != "D1":
        return {
            "status": "no_update",
            "message": f"Forecast is not newly issued (Dcode={dcode}).",
            "timestamp": current_time.isoformat(),
        }

    # Step 4: Fetch all 10 regions atomically
    all_forecasts = {}
    for code in get_all_region_codes():
        try:
            all_forecasts[code] = fetch_and_parse_region(code, env, ref_date)
        except Exception as err:
            return {
                "status": "error",
                "message": f"Aborting update. Failed fetching region {code}: {err}",
                "timestamp": current_time.isoformat(),
            }

    # Commit all 10 regions atomically to SQLite cache
    success = db_update_forecasts(all_forecasts, db_path)
    if not success:
        return {
            "status": "error",
            "message": "Transaction failed validation or insertion. Rolled back.",
            "timestamp": current_time.isoformat(),
        }

    return {
        "status": "updated",
        "message": "Successfully updated all 10 regions in cache.",
        "timestamp": current_time.isoformat(),
    }
