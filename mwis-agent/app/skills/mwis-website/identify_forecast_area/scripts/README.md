# MWIS Region Query CLI Tool

This directory contains the CLI query tool and its associated test suite.

## Usage Examples

The script `query_region.py` can be executed directly using Python 3.

### 1. Querying Coordinates
To find which region a coordinate falls into, supply the latitude and longitude:
```bash
python3 query_region.py 53.0685 -4.0763
```
**Output:**
```
Region(s): SD (Snowdonia & North Wales)
```

### 2. Querying in Overlap Zones
Coordinates that fall inside overlapping regions (like WH, EH, and SH) will list all matching regions:
```bash
python3 query_region.py 56.7969 -5.0036
```
**Output:**
```
Region(s): WH (West Highlands)
Note: Overlap zone detected.
```

### 3. Querying by Mountain/Location Name
Supply the location name as a string:
```bash
python3 query_region.py "Ben Nevis"
```
**Output:**
```
Region(s): WH (West Highlands)
```

If the name is not found in the local `munros.csv` database, it will automatically query the OpenStreetMap Nominatim geocoding API to resolve its coordinates:
```bash
python3 query_region.py "Keswick"
```
**Output:**
```
Region(s): LD (Lake District)
```

### 4. Locations Outside MWIS Regions (In-Scope)
If a coordinate or location is within Great Britain but does not lie inside any MWIS forecast area boundary, it outputs the nearest region(s) and their distances:
```bash
python3 query_region.py 54.8924 -2.9329
```
**Output:**
```
The location is not in an MWIS area.
Nearest area(s):
  - LD (Lake District): 16.54 km away
  - YD (Yorkshire Dales & North Pennines): 18.25 km away
```

### 5. Out of Scope Locations
Any query located outside Great Britain or in Northern Ireland is out of scope and returns exit code `2` with an error message:
```bash
python3 query_region.py "Belfast"
```
**Stderr Output:**
```
The requested location is out of scope of this skill. Only locations in Great Britain are supported.
```

### 6. JSON Formatting
Add the `--json` flag to return structured JSON format:
```bash
python3 query_region.py "Ben Nevis" --json
```
**Output:**
```json
{
  "in_scope": true,
  "in_area": true,
  "regions": ["WH"],
  "overlap": false
}
```

---

## Running the Test Suite

The test suite is built using Python's standard `unittest` framework and checks inputs, Nominatim fallbacks, scope constraints, and distance calculations.

To run the entire test suite, execute the test script directly from this directory:
```bash
python3 test_query_region.py
```
Or run it from the root of the repository:
```bash
python3 .agents/skills/mwis-website/identify_forecast_area/scripts/test_query_region.py
```
