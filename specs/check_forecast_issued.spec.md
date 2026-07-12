# Specification: check_forecast_issued Skill

This spec defines the check_forecast_issued skill, which determines whether a new MWIS weather forecast has been issued and triggers cache ingestion.

### SECTION 1: SPEC

**One-line purpose**
Checks if the North West Highlands (NW) forecast has been newly issued and, if so, triggers ingestion of all 10 regions into the SQLite cache.

**Users and use cases**
* As a weather agent system, I want to periodically check if a new forecast is available so that I can update the local database cache and keep regional forecasts up to date without wasting API calls.

**Requirements**
1. **Target Region:** Always fetch the North West Highlands (`NW`) forecast to check for updates.
2. **Deterministic Update Verification:** Parse the `NW` forecast and check the first forecast day element (`forecast_index == 0`). If `Dcode == "D1"`, the forecast is newly issued. If `Dcode == "D0"`, it is not new.
3. **Execution Schedule (BST / British Time):**
   * Start checking daily at 11:00 BST.
   * Check hourly at 11:00, 12:00, 13:00, 14:00, 15:00, and 16:00.
   * Run an extra check at 15:30.
   * Between 16:00 and 18:00, check every 10 minutes (16:10, 16:20, ... up to 18:00).
   * Once a successful new forecast is detected and the cache is updated, suspend checking for the rest of that calendar day.
4. **Ingestion Trigger:** If a new forecast is detected, fetch forecasts for all 10 regions and save them to the SQLite database.
5. **No-Update Behavior:** If the forecast is not new (`Dcode == "D0"`), do not update the database and return a status code/message indicating no updates are available yet.

**Edge cases**
* *Network/Fetching failure:* If any request to fetch the 10 regions fails, the process must abort and rollback so that the old cache is not overwritten or partially overwritten.
* *Out-of-hours requests:* If the check is triggered outside 11:00-18:00 or after the daily update has already occurred, the skill should immediately exit with a skipped status.

**Acceptance criteria**
```
Given it is 11:30 BST and no forecast has been cached today
When the check is run and the NW forecast has Dcode == "D0" for forecast_index == 0
Then the database cache is not updated, and check_forecast_issued returns "no_update"

Given it is 12:00 BST and no forecast has been cached today
When the check is run and the NW forecast has Dcode == "D1" for forecast_index == 0
Then the forecasts for all 10 regions are fetched and atomically updated in the cache, and check_forecast_issued returns "updated"

Given a successful update occurred at 12:00 BST today
When a check is executed at 13:00 BST
Then the check is skipped, and check_forecast_issued returns "already_updated_today"
```

---

### SECTION 2: PLAN

**Stack and architecture**
* Python execution within the ADK environment.
* Sqlite3 database for persistence.
* Mock files located in the `mocks/` directory under `mwis-website` (i.e. `mwis-agent/app/skills/mwis-website/mocks/`) to substitute live website requests when `MWIS_ENV=development` is set.

**API contracts**
* Function: `check_forecast_issued(db_path: str | None = None, use_live_forecast: bool = False, current_time: datetime.datetime | None = None, force_update: bool = False) -> dict[str, Any]`
  - Returns: `{"status": "updated" | "no_update" | "already_updated_today" | "error", "timestamp": str}`
  - Note: If `force_update` is `True`, the schedule eligibility checks are bypassed entirely.

---

### SECTION 3: TASKS

## Task 1: Schedule Verification helper
* **What to build:** Implement a helper function that checks if current time matches the specified scheduler rules (BST / British Time zone info) and whether the check has already completed successfully today.
* **Files likely affected:** `mwis-agent/app/skills/mwis-website/check_forecast_issued/scripts/schedule_helper.py`
* **Acceptance criteria:** Evaluates correctly against the BST schedule rules.
* **Dependencies:** None

## Task 2: Core Check & Update Logic
* **What to build:** Implement the main skill script that executes the logic (fetch NW, check Dcode, fetch all 10 regions on success, update SQLite).
* **Files likely affected:** `mwis-agent/app/skills/mwis-website/check_forecast_issued/scripts/check_forecast.py`
* **Acceptance criteria:** Returns expected status codes for updated / no-update conditions.
* **Dependencies:** Task 1
---

## Agreed Decisions

1. **Timezone Handling**: British Time (BST/GMT) offsets will be calculated using Python's standard `zoneinfo` module (`Europe/London`), rather than `pytz`.
2. **SQLite Path**: The database file will default to `mwis-agent/app/cache/mwis_forecasts.db` relative to the workspace root to avoid local sandbox directory permission issues.
