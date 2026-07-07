---
name: check-forecast-issued
description: Checks if a new daily weather forecast has been issued on the MWIS website and updates the SQLite cache database atomically.
version: 0.1.0
license: CC BY-SA 4.0
metadata:
  author: Mehmet Rahmi Karatay
---

# Check Forecast Issued

The goal of this skill is to verify whether the daily MWIS weather forecast has been newly updated. It performs a deterministic check by examining the forecast for the North West Highlands (`NW`) and checking if the first day's date code (`Dcode`) equals `D1` (indicating a new forecast). If true, it retrieves the forecast for all 10 regions and writes them atomically into the local SQLite cache.

## When to use
* You need to check if the daily weather forecast on the MWIS website is newly updated.
* You want to pull and cache all 10 regional forecasts to avoid redundant scrapings or API calls.
* You need to verify if checking is scheduled to run at the current time in British Time (BST).

## When NOT to use
* You only need to serve a forecast for a single region (use the `serve_forecast_to_user` or `fetch_specific_forecast` skill instead).
* You already know the forecast has not been updated today.

## Skill dependencies
* `fetch_specific_forecast`
* `identify_outing_date`

## Workflow
1. Call the `is_time_in_schedule` script to verify if the check is allowed within the daily BST schedule bounds (11:00 to 18:00 BST).
2. Query the SQLite cache database to check if a successful update was already completed today. If yes, skip further checks.
3. Fetch the `NW` region forecast and check if the day at `forecast_index == 0` has `Dcode == D1`.
4. If a new forecast is available, fetch all 10 regional forecasts (or load local mock files if `MWIS_ENV=development`).
5. Transactionally write all 10 forecasts to the SQLite `forecast_cache` table. If any fetch fails, roll back the transaction.

## Examples
* Check status output on success:
  ```json
  {
    "status": "updated",
    "message": "Successfully updated all 10 regions in cache.",
    "timestamp": "2026-07-06T12:00:00+01:00"
  }
  ```
