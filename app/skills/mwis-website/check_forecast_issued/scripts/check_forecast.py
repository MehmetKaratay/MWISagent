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

# Ingestion status constants
STATUS_NO_UPDATE = "no_update"
STATUS_UPDATED = "updated"
STATUS_ALREADY_UPDATED = "already_updated_today"
STATUS_ERROR = "error"

# Anchor verification region and target Dcode
ANCHOR_REGION = "NW"
TARGET_NEW_DCODE = "D1"


def get_all_region_codes() -> list[str]:
    """Return the hardcoded list of 10 MWIS region codes.

    Returns:
        list[str]: Region codes.
    """
    return ["NW", "WH", "EH", "SH", "SU", "LD", "YD", "PD", "SD", "BB"]


def _format_mwis_date(dt: datetime.date) -> str:
    """Format a date like 'Monday 6th July 2026'."""
    day = dt.day
    if 11 <= day <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return dt.strftime(f"%A {day}{suffix} %B %Y")


def _load_mock_html(region_code: str, env: str) -> str:
    """Load static mock HTML from disk.

    Args:
        region_code (str): The code of the region.
        env (str): The environment string.

    Returns:
        str: Raw HTML content.
    """
    mock_file = os.path.join(MOCKS_DIR, f"{region_code}-mock.html")
    if not os.path.exists(mock_file):
        raise FileNotFoundError(f"Mock file not found: {mock_file}")
    # nosemgrep: detect-path-traversal
    with open(mock_file, encoding="utf-8") as f:
        html = f.read()

    today = datetime.datetime.now(ZoneInfo("Europe/London")).date()

    if env == "development":
        day0 = today
        day1 = today + datetime.timedelta(days=1)
        day2 = today + datetime.timedelta(days=2)
    else:  # test-new-dcode
        day0 = today - datetime.timedelta(days=1)
        day1 = today
        day2 = today + datetime.timedelta(days=1)

    html = html.replace("Monday 6th July 2026", _format_mwis_date(day0))
    html = html.replace("Tuesday 7th July 2026", _format_mwis_date(day1))
    html = html.replace("Wednesday 8th July 2026", _format_mwis_date(day2))

    return html


def fetch_and_parse_region(
    region_code: str, env: str = "production", ref_date: datetime.date | None = None
) -> dict[str, Any]:
    """Fetch and parse MWIS forecast for a given region.

    Uses mock HTML files in development mode or queries the live URL in production.

    Args:
        region_code (str): The code of the region.
        env (str): 'production', 'development', or 'test-new-dcode'.
        ref_date (date, optional): Reference date for injecting Dcodes.

    Returns:
        dict: Parsed and injected forecast dictionary.
    """
    if env in ("development", "test-new-dcode"):
        html = _load_mock_html(region_code, env)
        parsed = parse_forecast_html(html)
    else:
        url = get_forecast_url(region_code)
        parsed = get_forecast_data(url)

    if ref_date is None:
        ref_date = datetime.datetime.now(ZoneInfo("Europe/London")).date()

    return inject_d_codes(parsed, ref_date)


def _normalize_time(current_time: datetime.datetime | None) -> datetime.datetime:
    """Coerce input datetime to have timezone info (defaults to Europe/London).

    Args:
        current_time: Datetime override or None.

    Returns:
        datetime: Timezone-aware datetime.
    """
    if current_time is None:
        return datetime.datetime.now(ZoneInfo("Europe/London"))
    if current_time.tzinfo is None:
        return current_time.replace(tzinfo=datetime.UTC)
    return current_time


def _has_update_run_today(db_path: str, today_str: str) -> bool:
    """Query SQLite to verify if updates were committed today.

    Args:
        db_path (str): DB file path.
        today_str (str): Date string format YYYY-MM-DD.

    Returns:
        bool: True if already updated today, False otherwise.
    """
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT count(*) FROM forecast_cache
            WHERE date(cached_at, 'localtime') = ?;
            """,
            (today_str,),
        )
        return cursor.fetchone()[0] > 0
    finally:
        conn.close()


def _is_new_forecast_available(
    env: str, ref_date: datetime.date, current_time: datetime.datetime
) -> tuple[bool, dict[str, Any]]:
    """Determine if a new forecast has been issued for the anchor region.

    Args:
        env (str): Environment name.
        ref_date (date): Local date.
        current_time (datetime): Current check timestamp.

    Returns:
        tuple[bool, dict]: Ingestion result details.
    """
    try:
        nw_forecast = fetch_and_parse_region(ANCHOR_REGION, env, ref_date)
    except Exception as err:
        return False, {
            "status": STATUS_ERROR,
            "message": f"Failed checking NW forecast: {err}",
            "timestamp": current_time.isoformat(),
        }

    days = nw_forecast.get("days", [])
    if env == "development":
        # Always return True in development to force cache update with the rewritten fresh dates
        return True, {}

    if not days or days[0].get("Dcode") != TARGET_NEW_DCODE:
        return False, {
            "status": STATUS_NO_UPDATE,
            "message": "Forecast is not newly issued.",
            "timestamp": current_time.isoformat(),
        }

    return True, {}


def _update_all_regions_cache(
    db_path: str, env: str, ref_date: datetime.date, current_time: datetime.datetime
) -> dict[str, Any]:
    """Fetch all 10 forecasts and atomically commit to SQLite.

    Args:
        db_path (str): SQLite path.
        env (str): Environment.
        ref_date (date): Date offset.
        current_time (datetime): Timestamp.

    Returns:
        dict: Ingestion result metadata.
    """
    all_forecasts = {}
    for code in get_all_region_codes():
        try:
            all_forecasts[code] = fetch_and_parse_region(code, env, ref_date)
        except Exception as err:
            return {
                "status": STATUS_ERROR,
                "message": f"Aborting update. Failed fetching region {code}: {err}",
                "timestamp": current_time.isoformat(),
            }

    success = db_update_forecasts(all_forecasts, db_path)
    if not success:
        return {
            "status": STATUS_ERROR,
            "message": "Transaction validation/insertion failed. Rolled back.",
            "timestamp": current_time.isoformat(),
        }

    return {
        "status": STATUS_UPDATED,
        "message": "Successfully updated all 10 regions in cache.",
        "timestamp": current_time.isoformat(),
    }


def _get_cache_count(db_path: str) -> int:
    """Return the number of records currently in the forecast_cache table."""
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM forecast_cache;")
        return cursor.fetchone()[0]
    except sqlite3.OperationalError:
        return 0
    finally:
        conn.close()


def _initialize_db_and_time(
    db_path: str | None, current_time: datetime.datetime | None
) -> tuple[str, datetime.datetime]:
    """Initialize DB directory, create schema, and normalize the check time."""
    if db_path is None:
        db_path = os.getenv("MWIS_DB_PATH", DEFAULT_DB_PATH)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    db_init(db_path)
    return db_path, _normalize_time(current_time)


def _is_update_eligible(
    db_path: str, current_time: datetime.datetime
) -> tuple[bool, str]:
    """Check if the cache state and schedule allow a forecast update today."""
    if _get_cache_count(db_path) < len(get_all_region_codes()):
        return True, ""
    if not is_time_in_schedule(current_time):
        return False, STATUS_NO_UPDATE
    london_dt = current_time.astimezone(ZoneInfo("Europe/London"))
    if _has_update_run_today(db_path, london_dt.strftime("%Y-%m-%d")):
        return False, STATUS_ALREADY_UPDATED
    return True, ""


def _run_forecast_ingestion(
    db_path: str, env: str, current_time: datetime.datetime
) -> dict[str, Any]:
    """Perform check for new forecast availability and commit to cache."""
    london_dt = current_time.astimezone(ZoneInfo("Europe/London"))
    is_new, err_res = _is_new_forecast_available(env, london_dt.date(), current_time)
    if not is_new:
        return err_res
    return _update_all_regions_cache(db_path, env, london_dt.date(), current_time)


def check_forecast_issued(
    db_path: str | None = None,
    use_live_forecast: bool = False,
    current_time: datetime.datetime | None = None,
    force_update: bool = False,
) -> dict[str, Any]:
    """Deterministically check if the forecast has been newly issued and update cache."""
    db_path, current_time = _initialize_db_and_time(db_path, current_time)
    if not force_update:
        eligible, status = _is_update_eligible(db_path, current_time)
        if not eligible:
            return {
                "status": status,
                "message": "Update skipped due to schedule or previous runs.",
                "timestamp": current_time.isoformat(),
            }
    if use_live_forecast:
        env = "production"
    else:
        env = os.getenv("MWIS_ENV", "development")
        if env == "production":
            env = "development"
    return _run_forecast_ingestion(db_path, env, current_time)
