# Query RefHeight Spec

This specification defines a command-line tool `query_refHeight.py` to retrieve the reference height (`RefHeight`) for a given MWIS region code or region name.

```yaml
name: query_refHeight
summary: Retrieve the RefHeight field of an MWIS region from the mwis-regions.csv database.
inputs:
  - name: query
    type: string
    required: true
    description: "Region code (e.g., WH) or name (e.g., West Highlands)"
  - name: csv_path
    type: string
    required: false
    description: "Path to a custom regions CSV database. Defaults to fetch_specific_forecast/references/mwis-regions.csv."
outputs:
  - name: RefHeight
    type: json
    description: "A JSON object containing the RefHeight value, e.g. `{\"RefHeight\": \"900m\"}`."
exit_codes:
  0: Success
  1: Invalid input, missing file, schema validation failure, or region not found
dependencies:
  - python >= 3.10
```

## Behavior & Parsing Logic

- **Shared Helper module (`query_utils.py`)**: All common behaviors (loading CSV, field normalization, row matching, and schema validation) are implemented in `query_utils.py` and imported by `query_refHeight.py`.
- **CSV Parsing and Schema Validation**:
  - `RegionCode`: `^[A-Z]{2}$`
  - `RegionName`: `^[a-zA-Z &]+$`
  - `RefHeight`: `^\d{3}m$`
  - `FLorValley`: `"FL"` or `"Valley"`
  - `Country`: `"Scotland"`, `"England"`, or `"Wales"`
  - `Url`: Starts with `"https://mwis.org.uk/forecasts/"`
  - Any failure to validate immediately aborts execution with exit code 1.
- **Query Matching**: Case-insensitive matching against `RegionCode` and `RegionName`.
- **Output**:
  - JSON format on stdout: `{"RefHeight": "<RefHeight_here>"}`.
  - Error messages printed to stderr on failure.

## Examples

| Command | Expected Output (stdout) | Expected Exit Code |
| :--- | :--- | :--- |
| `python3 query_refHeight.py "WH"` | `{"RefHeight": "900m"}` | 0 |
| `python3 query_refHeight.py "Peak District"` | `{"RefHeight": "600m"}` | 0 |
| `python3 query_refHeight.py "Invalid"` | *(Error msg on stderr)* | 1 |
