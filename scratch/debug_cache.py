import os
import sys

sys.path.insert(0, "mwis-agent")
sys.path.insert(0, "mwis-agent/app/skills/mwis-website/check_forecast_issued/scripts")

from unittest.mock import patch

from check_forecast import check_forecast_issued

from app.cache import get_forecast

db_path = os.path.abspath("test_debug.db")
if os.path.exists(db_path):
    os.remove(db_path)

os.environ["MWIS_ENV"] = "development"

with (
    patch("check_forecast.is_time_in_schedule", return_value=True) as mock_sched,
    patch(
        "check_forecast._is_new_forecast_available", return_value=(True, {})
    ) as mock_new,
):
    res = check_forecast_issued(db_path=db_path, env="development")
    print("Orchestrator result:", res)
    forecast = get_forecast("NW", db_path=db_path)
    print("Forecast from cache:", forecast)
