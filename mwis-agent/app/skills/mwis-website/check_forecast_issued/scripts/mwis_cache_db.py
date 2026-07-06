# MWIS Agent (c) by Mehmet Rahmi Karatay
#
# MWIS Agent is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License.
#
# You should have received a copy of the license along with this
# work.  If not, see <https://creativecommons.org/licenses/by-sa/4.0/>.

"""SQLite forecast cache database manager."""

import json
import sqlite3
from typing import Any


def db_init(db_path: str) -> None:
    """Initialize the SQLite database schema if not present.

    Args:
        db_path (str): File path to the SQLite database.
    """
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS forecast_cache (
                region_code TEXT PRIMARY KEY,
                forecast_json TEXT NOT NULL,
                last_updated_mwis TEXT NOT NULL,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


def db_get_forecast(region_code: str, db_path: str) -> dict[str, Any] | None:
    """Retrieve the cached forecast dictionary for a region.

    Args:
        region_code (str): The code of the region (e.g., 'NW').
        db_path (str): File path to the SQLite database.

    Returns:
        Optional[dict]: Deserialized forecast dict or None if missing.
    """
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT forecast_json FROM forecast_cache WHERE region_code = ?;",
            (region_code,),
        )
        row = cursor.fetchone()
        if row:
            return json.loads(row[0])
        return None
    finally:
        conn.close()


def _validate_forecast_completeness(forecast: dict[str, Any]) -> None:
    """Validate a parsed forecast dictionary contains the minimum required fields.

    Args:
        forecast (dict): Forecast dictionary.
    """
    if "region" not in forecast:
        raise ValueError("Missing 'region' field.")
    if "days" not in forecast or not forecast["days"]:
        raise ValueError("Missing 'days' field.")
    if (
        "last_updated" not in forecast["days"][0]
        or not forecast["days"][0]["last_updated"]
    ):
        raise ValueError("Missing 'last_updated' field in first day.")


def db_update_forecasts(forecasts: dict[str, dict[str, Any]], db_path: str) -> bool:
    """Update all region forecasts atomically.

    All updates are wrapped in a single database transaction. If any forecast
    fails validation, the entire transaction is rolled back.

    Args:
        forecasts (dict): Map of region_code -> forecast dictionary.
        db_path (str): File path to the SQLite database.

    Returns:
        bool: True on success, False if transaction was aborted and rolled back.
    """
    conn = sqlite3.connect(db_path)
    try:
        # Validate all forecasts first before opening a transaction
        for forecast in forecasts.values():
            _validate_forecast_completeness(forecast)

        cursor = conn.cursor()
        cursor.execute("BEGIN TRANSACTION;")

        for region_code, forecast in forecasts.items():
            forecast_json = json.dumps(forecast)
            last_updated = forecast["days"][0]["last_updated"]

            cursor.execute(
                """
                INSERT INTO forecast_cache (region_code, forecast_json, last_updated_mwis, cached_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(region_code) DO UPDATE SET
                    forecast_json=excluded.forecast_json,
                    last_updated_mwis=excluded.last_updated_mwis,
                    cached_at=CURRENT_TIMESTAMP;
                """,
                (region_code, forecast_json, last_updated),
            )

        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()
