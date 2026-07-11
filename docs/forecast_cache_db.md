# Documentation: SQLite Cache Layer Database Schema

This document details the database schema, SQLite layout, transactional constraints, and development settings for the MWIS weather agent caching system.

---

## 1. Database Path
The SQLite database path is configurable via the `MWIS_DB_PATH` environment variable.

* **Default Location:** `mwis-agent/app/cache/mwis_forecasts.db` (relative to workspace root).
* **Automatic Creation:** The directory and database file are initialized automatically on startup if missing.

---

## 2. Table Schema: `forecast_cache`
The SQLite database has a single table structure, containing the raw ingested and parsed regional forecasts.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `region_code` | TEXT | PRIMARY KEY | Unique code of the region (e.g. `NW`, `WH`, `EH`, `SH`, `SU`, `LD`, `YD`, `PD`, `SD`, `BB`) |
| `forecast_json` | TEXT | NOT NULL | Serialized JSON forecast dictionary returned from the HTML parsing skills (containing days array and outlook) |
| `last_updated_mwis` | TEXT | NOT NULL | The `last_updated` text string extracted from the parsed forecast (e.g. `Sat 4th Jul 26 at 4:17PM`) |
| `cached_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | UTC timestamp when the row was updated or created |

---

## 3. Transactional Integrity (Atomic Updates)
Updates to the cache are handled as a single database transaction:
1. Forecasts for all 10 regions are fetched and parsed in-memory.
2. If all 10 forecasts are successfully fetched and validated, the transaction commits:
   ```sql
   BEGIN TRANSACTION;
   -- INSERT/REPLACE statements for all 10 regions
   COMMIT;
   ```
3. If any forecast fails validation (e.g., missing mandatory properties like `last_updated` or days array) or network errors arise during retrieval, the transaction is immediately rolled back:
   ```sql
   ROLLBACK;
   ```
This ensures that the database keeps the last valid cache data and is never left in a partially updated or corrupted state.

---

## 4. Incomplete Cache Bypass (Self-Healing)
If the `forecast_cache` table contains fewer than 10 entries (indicating that some or all of the regional forecasts are missing from the cache), the scheduler update checks (which restrict updates to specific time windows) are bypassed. This forces the system to immediately fetch and parse all 10 regions to guarantee database completeness on fresh deployments or clean database states.

---

## 5. Offline Development Mode
Setting the environment variable `MWIS_ENV=development` instructs the cache layer to bypass the live internet and populate the DB using static local mock HTML files located in the relative workspace folder:
`mwis-agent/app/skills/mwis-website/mocks/`
