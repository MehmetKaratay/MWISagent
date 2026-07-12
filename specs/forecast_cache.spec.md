# Specification: forecast_cache

This spec defines the SQLite forecast cache schema, atomic transactional write behavior, and development mode mock loading rules.

### SECTION 1: SPEC

**One-line purpose**
Provides a SQLite cache layer to store parsed MWIS forecasts for all 10 regions, supporting atomic cache updates and development-mode local mocks.

**Users and use cases**
* As the weather agent, I want to retrieve forecasts from the local SQLite cache instead of making HTTP requests to MWIS, so that I can reduce request latency and avoid hitting rate limits.
* As a developer, I want to load forecasts from local mock HTML files when running in development mode, so that I do not make network requests during local testing.

**Requirements**
1. **SQLite Storage:**
   - DB file path: Configurable via `MWIS_DB_PATH` environment variable. Defaults to `mwis-agent/app/cache/mwis_forecasts.db` relative to the workspace root.
   - Table name: `forecast_cache`
   - Schema:
     - `region_code` (TEXT PRIMARY KEY) - e.g., 'NW', 'WH', 'EH', 'SH', 'SU', 'LD', 'YD', 'PD', 'SD', 'BB'
     - `forecast_json` (TEXT) - Full parsed JSON structure returned by the forecast parser
     - `last_updated_mwis` (TEXT) - The `last_updated` value extracted from the parsed forecast
     - `cached_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP) - Local insertion timestamp
2. **Atomic Updates:**
   - Writes to the cache must be executed in a database transaction (`BEGIN TRANSACTION` / `COMMIT`).
   - If fetching or parsing any region's forecast fails (network error, schema mismatch, parser failure), the entire transaction must be rolled back (`ROLLBACK`), preserving the prior cache.
3. **Bypass Schedule on Incomplete Cache:**
   - If the `forecast_cache` table contains fewer than 10 entries (indicating the cache is incomplete or empty), the scheduler check (`is_time_in_schedule`) must be bypassed to force a complete cache load.
4. **Development/Mock Mode:**
   - Ingestion mode is checked via the environment variable `USE_LIVE_FORECAST` (defaulting to `"false"` locally).
   - If `USE_LIVE_FORECAST=false` (or when fetching is mock-based), the database will bypass remote network fetching. Instead, it will read mock HTML files from the relative directory `mwis-agent/app/skills/mwis-website/mocks/` and parse them.
   - If `USE_LIVE_FORECAST=true`, the database will execute live fetches.

**Edge cases**
* *Corrupt/Incomplete database files:* If the database is missing or corrupt, it must be recreated automatically on application startup.
* *Mock file missing:* In development mode, if a mock file is missing, exit with an error.

**Acceptance criteria**
```
Given a clean database initialization
When the database is created
Then the forecast_cache table is created with primary key region_code

Given a successful update of all 10 regions
When the cache transaction finishes
Then the table contains exactly 10 records and matches the parsed JSON schemas

Given a failure fetching the 5th region out of 10
When the update fails
Then the database rolls back and still contains the old 10 forecasts intact
```

---

### SECTION 2: PLAN

**Stack and architecture**
* Python `sqlite3` library.
* Environment variable configuration check for `MWIS_ENV`.

**API contracts**
* `db_init(db_path: str) -> None`
* `db_get_forecast(region_code: str) -> Optional[dict]`
* `db_update_forecasts(forecasts: dict[str, dict]) -> bool` - Returns `True` if successfully committed, otherwise `False`.

---

### SECTION 3: TASKS

## Task 1: SQLite Database Manager
* **What to build:** Write the Python module handling SQLite connections, table creation, and retrieval/insertion functions with transactional safety.
* **Files likely affected:** `mwis-agent/app/skills/mwis-website/check_forecast_issued/scripts/mwis_cache_db.py`
* **Acceptance criteria:** Successfully connects, initializes table, and handles transactional updates.
* **Dependencies:** None

## Task 2: Mock Ingestion Helper
* **What to build:** Write the function that retrieves mock HTML files in development mode and outputs them as parsed JSON structures for cache insertion.
* **Files likely affected:** `mwis-agent/app/skills/mwis-website/check_forecast_issued/scripts/mock_ingest.py`
* **Acceptance criteria:** Parses and loads all 10 mock files successfully.
* **Dependencies:** None
