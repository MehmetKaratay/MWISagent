# Documentation: check_forecast_issued Skill & SQLite Cache Layer

This document details the design, scheduling rules, caching layer, and development patterns for the `check_forecast_issued` weather agent skill.

---

## 1. Skill Purpose
The `check_forecast_issued` skill determines whether a new daily Mountain Weather Information Service (MWIS) forecast has been issued. If a new forecast is detected:
* All 10 UK mountain regions are fetched and parsed.
* The parsed JSON is written atomically to a local SQLite cache database.
* The agent's cache layer timestamp is updated.

---

## 2. Ingestion Update Verification
The update detection is deterministic:
1. The skill fetches the North West Highlands (`NW`) forecast.
2. The skill parses the first forecast day element (`forecast_index == 0`).
3. If the parsed day's `Dcode` is equal to `D1` (tomorrow), a new forecast is available.
4. If the parsed day's `Dcode` is equal to `D0` (today), the daily forecast has not been updated yet.

---

## 3. SQLite Database Schema
The database path is configurable via the `MWIS_DB_PATH` environment variable. It defaults to the relative workspace directory `mwis-agent/app/cache/mwis_forecasts.db`.

It contains a single table `forecast_cache`:

| Column | Type | Description |
| :--- | :--- | :--- |
| `region_code` | TEXT (PRIMARY KEY) | Unique code of the region (e.g., `NW`, `WH`, `EH`, `SH`, `SU`, `LD`, `YD`, `PD`, `SD`, `BB`) |
| `forecast_json` | TEXT | Full serialized forecast JSON structure returned by parser (including days array and outlook) |
| `last_updated_mwis` | TEXT | The `last_updated` text string extracted from the parsed forecast (e.g. `Sat 4th Jul 26 at 4:17PM`) |
| `cached_at` | TIMESTAMP | UTC timestamp when the record was inserted/updated |

### Atomic Update Transaction
All writes are wrapped in an SQL database transaction (`BEGIN TRANSACTION` / `COMMIT`). If any individual region's forecast fails to fetch or validate (e.g., due to a network timeout or parsing schema failure), the update is aborted (`ROLLBACK`), preserving the prior cache state intact.

---

## 4. Execution Schedule
The forecast checks run relative to **BST (British Time / Europe/London)**.

* **Checking Hours:** 11:00 BST to 18:00 BST.
* **Checking Cadence:**
  * Hourly checks at 11:00, 12:00, 13:00, 14:00, 15:00, and 16:00.
  * Extra check at 15:30.
  * Every 10 minutes between 16:00 and 18:00 (16:10, 16:20, ... 18:00).
* **Early Suspension:** Once a successful new forecast update is detected and committed to the SQLite database, checking is suspended for the rest of that calendar day.

---

## 5. Development Mode (Local Mocks)
When running tests or running the agent in offline environments, set the environment variable:
```bash
export MWIS_ENV=development
```
In `development` mode, the checker and parsing routines bypass the live website and read static HTML pages from the relative workspace folder:
`mwis-agent/app/skills/mwis-website/mocks/`

---

## 6. Future Upgrade Path (Incremental Check Updates)
Later versions of this skill will check regularly for minor updates to the already issued forecasts during the day.

* The database structure's `last_updated_mwis` column will store each check's update string.
* Instead of checking only for `Dcode == "D1"` at `forecast_index == 0`, a future version will compare the parsed `"last_updated"` timestamp against the cached version for each region.
* If the `"last_updated"` value changes on the MWIS page, that specific region's cache entry will be updated incrementally.
