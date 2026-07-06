# Documentation: check_forecast_issued Checker Skill

This document details the scheduling, timeline rules, and update verification steps for the `check_forecast_issued` skill.

---

## 1. Checking Logic Purpose
The `check_forecast_issued` skill determines whether a new daily MWIS forecast has been issued. If it detects a new version, it pulls forecasts for all 10 regions and updates the cache.

* For cache database details, see the [forecast_cache_db.md](forecast_cache_db.md) documentation.

---

## 2. Ingestion Update Verification
The update detection is deterministic:
1. The checker fetches the North West Highlands (`NW`) forecast.
2. It parses the first forecast day element (`forecast_index == 0`).
3. If the parsed day's `Dcode` is equal to `D1` (tomorrow), a new forecast is available.
4. If the parsed day's `Dcode` is equal to `D0` (today), the daily forecast has not been updated yet.

---

## 3. Execution Schedule
The forecast checks run relative to **BST (British Time / Europe/London)**.

* **Checking Hours:** 11:00 BST to 18:00 BST.
* **Checking Cadence:**
  * Hourly checks at 11:00, 12:00, 13:00, 14:00, 15:00, and 16:00.
  * Extra check at 15:30.
  * Every 10 minutes between 16:00 and 18:00 (16:10, 16:20, ... 18:00).
* **Early Suspension:** Once a successful new forecast update is detected and committed to the SQLite database, checking is suspended for the rest of that calendar day.

---

## 4. Future Upgrade Path (Incremental Check Updates)
Later versions of this skill will check regularly for minor updates to the already issued forecasts during the day.

* Instead of checking only for `Dcode == "D1"` at `forecast_index == 0`, a future version will compare the parsed `"last_updated"` timestamp against the cached version for each region.
* If the `"last_updated"` value changes on the MWIS page, that specific region's cache entry will be updated incrementally.
