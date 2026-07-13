# Specification: SQLite Hill Database and Builder

This document defines the functional, structural, and security specifications for the database generation utility (`build_hills_db.py`) and the SQLite database (`uk_hills.db`) it constructs.

```yaml
metadata:
  name: build_hills_db.py
  description: Build and populate the SQLite database for offline mountain/hill lookups and region mapping.
  location: app/skills/mwis-website/identify_forecast_area/scripts/build_hills_db.py
  database_file: app/skills/mwis-website/identify_forecast_area/cache/uk_hills.db
  source_csv: app/skills/mwis-website/identify_forecast_area/resources/DoBIH_v18_4.csv
  local_names_csv: app/skills/mwis-website/identify_forecast_area/resources/local-names.csv
```

---

## 1. Database Schema

The database must reside at `app/skills/mwis-website/identify_forecast_area/cache/uk_hills.db` and contain two tables:

### 1.1 `hills` Table
Stores individual hill records parsed from the DoBIH database:
* **Columns**:
  * `name` (TEXT): Name of the hill.
  * `county` (TEXT): County/counties of the hill.
  * `country` (TEXT): Single-letter country code ('S' for Scotland, 'E' for England, 'W' for Wales).
  * `height` (REAL): Height of the hill in meters.
  * `mwis_region` (TEXT): Calculated MWIS region code (e.g., `'WH'`, `'SD'`) or `'notMWIS'`.
* **Indexes**: A case-insensitive index on the `name` column: `CREATE INDEX idx_hills_name ON hills(name COLLATE NOCASE)`.

### 1.2 `local_names` Table
Stores custom place name overrides and mountain range shorthand keywords:
* **Columns**:
  * `name` (TEXT): Custom place or range name (e.g., `'Cuillin'`).
  * `mwis_region` (TEXT): Corresponding MWIS region code (e.g., `'NW'`).
* **Indexes**: A case-insensitive index on the `name` column: `CREATE INDEX idx_local_names_name ON local_names(name COLLATE NOCASE)`.

---

2. **Build and Population Flow (`build_hills_db.py`)**

The script `build_hills_db.py` must run deterministically, supporting CLI parameters to configure paths:

### 2.1 CLI Interface and Defaults
* The script uses `argparse` to parse parameters:
  * `--db-path` (TEXT): Target SQLite database file path. Defaults to `app/skills/mwis-website/identify_forecast_area/cache/uk_hills.db`.
  * `--csv-path` (TEXT): Path to the source DoBIH CSV database. Defaults dynamically using globbing (see below).
* **Dynamic Glob Matching for CSV**:
  * If the `--csv-path` parameter is omitted, the script checks the `resources/` directory for any file matching the pattern `DoBIH*.csv` (using `glob.glob`).
  * If a matching CSV file exists, the script uses it as the default CSV source path.
  * If no matching file exists, the script defaults to `app/skills/mwis-website/identify_forecast_area/resources/DoBIH_v18_4.csv`.

### 2.2 Execution Steps
1. **Download source data if missing**:
   * Check if the resolved CSV path (default or overridden) exists.
   * If it does not exist, download `https://www.hill-bagging.co.uk/dobih-downloads/hillcsv.zip` using HTTPS, extract the CSV from the ZIP archive, write/rename it to the resolved CSV path, and delete the downloaded ZIP file.
2. **Database setup**:
   * Create the target directory containing the resolved database path if it does not exist.
   * Create the database at the resolved path (re-create/overwrite if it already exists).
3. **Table population**:
   * Populate the `hills` table by parsing the resolved CSV file. Resolve coordinates (`Latitude` and `Longitude`) for each row into MWIS regions using the existing boundaries configuration and `RegionFinder`. If a coordinate doesn't lie within any MWIS region, store `'notMWIS'`.
   * Populate the `local_names` table using `resources/local-names.csv`.
4. **Cleanup**:
   * If the CSV was downloaded dynamically by the script during execution, delete the CSV file to free up container space. If it was already present, preserve it.

---

## 3. Clean Code Standards

To ensure maintainability and robustness, all scripts in this skill must adhere to the `python-clean-code` standard:
- **No Magic Numbers**: All configuration, scaling factors, bounding box coordinates, and other numbers must be explicitly named constants at the top of the file.
- **Maximum Arguments**: Functions should take no more than 3 arguments. Group parameters into structures (like `@dataclass`) when passing multiple related values (e.g. `Point`).
- **No Flag Arguments**: Boolean flags passed to change function behavior are prohibited. Use polymorphic classes or split functions instead.
- **Single Responsibility**: Functions should do exactly one thing. For example, database connection handling should be strictly separated from parsing and calculation logic.
- **Well Named Functions**: Function names should make it clear what the function does, even if this means a longer function name.
- **Short Functions**: Functions should be no longer than 15 lines whenever possible. 20 lines maximum.
- **Type Hints**: All public and internal interfaces should be annotated with strict Python type hints.

---

## 4. TDD Verification Scenarios

The dedicated test file `tests/unit/test_build_hills_db.py` must verify the following scenarios:
1. **Schema Check**:
   * Verify both tables are created and contain the correct columns, types, and indexes.
2. **Deterministic Region Assignment**:
   * Verify that coordinates corresponding to known regions (e.g., WH, SD) are assigned correctly, and coordinates outside are assigned `'notMWIS'`.
3. **Local Names Parsing**:
   * Verify entries from `local-names.csv` are successfully imported into the `local_names` table.
4. **Cleanup Check**:
   * Verify that the ZIP and CSV files downloaded during script run are deleted afterwards, but pre-existing files are preserved.
