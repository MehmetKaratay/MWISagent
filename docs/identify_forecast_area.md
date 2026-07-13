# Identify Forecast Area Skill Documentation

The `identify_forecast_area` skill resolves a location (e.g. a town, mountain name, coordinates, or OS Grid Reference) into a Mountain Weather Information Service (MWIS) forecast region code.

## Component Overview

This skill utilizes the underlying python utility `query_region.py` to identify the forecast area.

- **Skill Entry Point**: `skills-mwis-website/identify_forecast_area/SKILL.md`
- **CLI Utility**: `skills-mwis-website/identify_forecast_area/scripts/query_region.py`

## CLI Usage

To run the utility manually:
```bash
python3 query_region.py <query_arguments> [--json]
```

### Input Formats

The query arguments can be:
1. **Place / Mountain Name**: E.g., `"Ben Nevis"`, `"Keswick"`.
   - **Resolution Flow**: Place name queries are resolved first by matching against `munros.csv` (case-insensitively). If unmatched, the script checks `local-names.csv` (case-insensitively). If still unmatched, the script makes an external network call to OpenStreetMap Nominatim API.
2. **Coordinates**: Two float values representing latitude and longitude:
   ```bash
   python3 query_region.py 53.0685 -4.0763
   ```
3. **OS Grid Reference**: 6-digit or 10-digit formats (with or without spaces):
   ```bash
   python3 query_region.py "NJ 009 020"
   ```

### Output Formats

By default, the script outputs human-readable strings. Pass the `--json` flag to return structured output.

#### Inside Region Example:
```bash
python3 query_region.py "Ben Nevis" --json
```
Output:
```json
{
  "in_scope": true,
  "in_area": true,
  "regions": ["WH"],
  "overlap": false
}
```

#### Out of Area / Near Boundary Example:
```bash
python3 query_region.py London --json
```
Output:
```json
{
  "in_scope": true,
  "in_area": false,
  "regions": [],
  "nearest": [
    {
      "code": "PD",
      "distance": 193.66,
      "direction": "NW"
    }
  ]
}
```

## Python API Usage

The function `find_regions_by_location(location_args: list[str]) -> dict` can be imported from `query_region.py` for direct programmatical invocation.

### Return Format for Out-of-Area locations:
```json
{
  "in_scope": true,
  "in_area": false,
  "error": "NOT_IN_AREA",
  "nearest": [
    {
      "code": "PD",
      "distance_km": 193.66,
      "direction": "NW"
    }
  ]
}
```

## Underlying Configuration Files

The behavior is governed by the assets in the skill directory:
- `assets/query_config.json`: Configures the distance overlap tolerance (`overlap_tolerance_pct`).
- `assets/mwis-region-boundaries.json`: Contains the GeoJSON-like boundary polygons for the 10 MWIS regions.
- `resources/munros.csv`: A CSV mapping of Munro mountains directly to their corresponding region codes.
- `resources/local-names.csv`: A local CSV mapping containing manual overrides and fallback local names mapped directly to region codes (e.g. "Cuillin", "Rum").

## Offline Database Cache (uk_hills.db)

For performance and offline lookup capabilities, the skill includes a deterministic builder script to construct an SQLite database cache.

### Build Utility: `build_hills_db.py`

The script `build_hills_db.py` compiles geographical records from the Database of British and Irish Hills (DoBIH) and custom local range names into an indexed SQLite database:

* **Location**: `skills-mwis-website/identify_forecast_area/scripts/build_hills_db.py`
* **Output Database**: `skills-mwis-website/identify_forecast_area/cache/uk_hills.db`

#### Build Behavior:
1. **Source Data Download**: If the large source database `DoBIH_v18_4.csv` is missing from `resources/`, the script automatically fetches the ZIP archive from the official downloads page over HTTPS, extracts the CSV, and cleans up the ZIP file.
2. **Region Calculation**: For each hill record, the script maps its latitude and longitude to MWIS forecast regions using `RegionFinder`. If no region matches, it labels the row as `'notMWIS'`.
3. **Database Insertion**: Saves the structured fields (`name`, `county`, `country`, `height`, `mwis_region`) into the database using bulk transactions, creating case-insensitive indexes on `name` for ultra-fast lookups.
4. **Cleanup**: Automatically deletes the downloaded ZIP and CSV files if they were dynamically retrieved by the script during build-time.

### Running the Builder

To rebuild or initialize the database cache manually:
```bash
python3 app/skills/mwis-website/identify_forecast_area/scripts/build_hills_db.py
```

*Note: During production deployments, this script runs automatically inside the Docker build pipeline to bake the fully compiled SQLite database directly into the container image.*
