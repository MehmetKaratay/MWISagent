# Specification: MWIS Region Query CLI Tool

This document defines the functional, structural, and security specifications for the Mountain Weather Information Service (MWIS) region query CLI tool (`query_region.py`).

```yaml
metadata:
  name: query_region.py
  description: CLI tool to query which MWIS forecast region a given location or coordinate belongs to.
  location: .agents/skills/mwis-website/identify_forecast_area/scripts/query_region.py
  config_file: .agents/skills/mwis-website/identify_forecast_area/assets/query_config.json
  boundaries_file: .agents/skills/mwis-website/identify_forecast_area/assets/mwis-region-boundaries.json
  munros_file: .agents/skills/mwis-website/identify_forecast_area/resources/munros.csv
```

---

## 1. Input Requirements

The tool must accept input arguments in the following formats:
- **Coordinates**: Two float numbers representing `latitude` and `longitude`.
- **Ordnance Survey Grid Reference**: A string representing an OS grid reference (e.g. `"NJ 009 020"`, `"NJ0099202017"`).
- **Location Name**: A string representing a mountain or place name (e.g. `"Ben Nevis"`, `"Keswick"`).
- **JSON Flag**: An optional `--json` argument to request structured JSON output instead of human-readable text.

---

## 2. Validation & Scope Rules

```yaml
scope_rules:
  allowed_country_code: gb
  allowed_regions:
    - England
    - Scotland
    - Wales
  excluded_regions:
    - Northern Ireland
  error_handling:
    out_of_scope:
      exit_code: 2
      message: "The requested location is out of scope of this skill. Only locations in Great Britain are supported."
```

- Every queried coordinate, parsed grid reference, or resolved place name must be checked to verify it lies inside Great Britain (England, Scotland, Wales).
- Locations in Northern Ireland or outside the UK are considered **out of scope** and must trigger the configured exit code and error message.

---

## 3. Query Logic & Distance Calculations

- **Input Parsing & Grid Reference Flow**:
  1. Determine if the input argument matches an OS grid reference format (two letters followed by an even number of digits, ignoring spaces).
  2. If it is an OS Grid Reference:
     - Parse the two letters to identify the 100km square base Easting and Northing.
     - Convert the digits to meter offsets and add to the base to get the BNG (OSGB36, EPSG:27700) coordinates.
     - Use `pyproj` to transform the BNG coordinates to WGS84 latitude and longitude (EPSG:4326).
  3. If not an OS Grid Reference, perform the Name Lookup Flow.
- **Name Lookup Flow**:
  1. Check for a case-insensitive match in `munros.csv`. If found, resolve to its designated `RegionCode` immediately.
  2. If not found in `munros.csv`, query `https://nominatim.openstreetmap.org/search` over HTTPS to resolve the name to coordinates.
- **Out-of-Area Near Boundary Calculation**:
  - If a coordinate is within Great Britain but does not fall inside any MWIS region polygon:
    - Calculate the shortest great-circle (Haversine) distance from the coordinate to the boundary line segments of each of the 10 MWIS polygons.
    - Identify the nearest region and print its name, distance (in kilometers), and cardinal direction (e.g., N, NE, E, SE) to the nearest boundary point.
    - If other regions have boundary distances within the configured `overlap_tolerance_pct` tolerance of the minimum distance, list those regions as well.

---

## 4. Configuration Schema

The file `query_config.json` must adhere to the following schema:

```yaml
config_schema:
  type: object
  properties:
    overlap_tolerance_pct:
      type: number
      description: The percentage tolerance within which multiple nearby regions are listed.
      default: 15.0
  required:
    - overlap_tolerance_pct
```

---

## 5. Security & Threat Model (STRIDE)

```yaml
stride_threats:
  - category: Spoofing
    threat: Attacker DNS-spoofs or MitM attacks the geocoding endpoint to return malicious coordinates.
    mitigation: Force secure HTTPS endpoint and ensure SSL/TLS certificate verification remains active.
  - category: Tampering
    threat: Local JSON configurations or CSV values are altered to run path traversal or disrupt logic.
    mitigation: Ensure paths are resolved strictly relative to the script directory; validate structure and types (e.g., verify tolerance percentage is a positive float).
  - category: Information Disclosure
    threat: Input formatting errors or missing files output raw stack traces, leaking system structure.
    mitigation: Wrap file operations, JSON loading, and HTTP requests in robust try-except blocks, outputting standardized clean errors.
  - category: Denial of Service
    threat: Rapid script calls get blocked by OpenStreetMap rate limits (HTTP 429), or extremely long query strings overload CPU.
    mitigation: Enforce an input length limit of 100 characters. Gracefully handle HTTP 429 and set a custom User-Agent per Nominatim guidelines.
  - category: Elevation of Privilege
    threat: Input strings run malicious shell commands or execute arbitrary Python code.
    mitigation: Do not use eval() or pass inputs to subprocess/shell wrappers. Strict typing for coordinates (float conversion) and URL parameter escaping for API queries.
```

---

## 6. Expected Test Cases

```yaml
test_cases:
  - name: Snowdon Coordinates
    inputs: [53.0685, -4.0763]
    expected:
      regions: ["SD"]
      overlap: false
  - name: Ben Nevis Name Lookup
    inputs: ["Ben Nevis"]
    expected:
      regions: ["WH"]
  - name: Carlisle Out-of-Area Boundary Check
    inputs: [54.8924, -2.9329]
    expected:
      in_scope: true
      in_area: false
      nearest: ["YD"]  # YD is nearest, directional output included
  - name: Sheffield Out-of-Area Boundary Check
    inputs: [53.3811, -1.4701]
    expected:
      in_scope: true
      in_area: false
      nearest: ["PD"]
  - name: London Distance Check
    inputs: [51.5074, -0.1278]
    expected:
      in_scope: true
      in_area: false
      nearest: ["PD"]  # Peak District or Brecon Beacons, with large distance
  - name: Paris Out-of-Scope Check
    inputs: [48.8566, 2.3522]
    expected:
      in_scope: false
      error_code: OUT_OF_SCOPE
  - name: Belfast Out-of-Scope Check (Northern Ireland)
    inputs: [54.5973, -5.9301]
    expected:
      in_scope: false
      error_code: OUT_OF_SCOPE
  - name: NJ 009 020 Grid Reference Check
    inputs: ["NJ 009 020"]
    expected:
      regions: ["EH"]
  - name: NJ 00992 02017 Grid Reference Check
    inputs: ["NJ 00992 02017"]
    expected:
      regions: ["EH"]
  - name: NJ009020 Grid Reference Check
    inputs: ["NJ009020"]
    expected:
      regions: ["EH"]
  - name: NJ0099202017 Grid Reference Check
    inputs: ["NJ0099202017"]
    expected:
      regions: ["EH"]
  - name: TL 561 571 Grid Reference Check
    inputs: ["TL 561 571"]
    expected:
      in_scope: true
      in_area: false
      nearest: ["PD"]
```

---

## 7. Clean Code Standards

To ensure maintainability and robustness, all scripts in this skill must adhere to the `python-clean-code` standard:
- **No Magic Numbers**: All configuration, scaling factors, bounding box coordinates, and other numbers must be explicitly named constants at the top of the file.
- **Maximum Arguments**: Functions should take no more than 3 arguments. Group parameters into structures (like `@dataclass`) when passing multiple related values (e.g. `Point`).
- **No Flag Arguments**: Boolean flags passed to change function behavior (e.g., `as_json`) are prohibited. Use polymorphic classes (e.g., `JsonFormatter` and `TextFormatter`) or split functions instead.
- **Single Responsibility**: Functions should do exactly one thing. For example, API fetching logic should be strictly separated from parsing and error-handling logic.
- **Well Named Functions**: Function names should make it clear what the function does, even if this means a longer function name
- **Short Functions**: Functions should be no longer than 15 line whenever possible. 20 lines maximum.
- **Type Hints**: All public and internal interfaces should be annotated with strict Python type hints.
