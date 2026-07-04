# Fetch Specific Forecast Spec

This specification defines a command-line tool `query_url.py` to resolve MWIS region codes or names to forecast text URLs.

```yaml
name: fetch_specific_forecast
summary: Resolve input region codes or names to direct MWIS forecast text URLs.
inputs:
  - name: query
    type: string
    required: true
    description: "Region code (e.g., WH) or name (e.g., West Highlands)"
  - name: -stdout / --stdout
    type: flag
    required: false
    description: "If provided, outputs raw text URL directly to stdout instead of JSON"
outputs:
  - name: url
    type: string / json
    description: "By default, outputs a JSON object containing the URL (e.g. `{\"url\": \"https://...\"}`). If `-stdout` is passed, outputs raw URL string."
exit_codes:
  0: Success
  1: Invalid input, missing file, or region not found
dependencies:
  - python >= 3.10
```

## Behavior & Parsing Logic

- **Source Reference**: Mappings are loaded from `mwis-regions.csv`.
- **Query Matching**: Case-insensitive matching against `RegionCode` and `RegionName`.
- **Argument Parsing**: Uses `argparse` to handle positional and optional arguments.
- **Output Formats**:
  - Default: JSON output on stdout: `{"url": "<url_here>"}`.
  - With `-stdout` / `--stdout` flag: Raw string output on stdout: `<url_here>`.

## Examples

| Command | Expected Output (stdout) | Expected Exit Code |
| :--- | :--- | :--- |
| `python3 query_url.py "WH"` | `{"url": "https://mwis.org.uk/forecasts/scottish/west-highlands/text"}` | 0 |
| `python3 query_url.py "WH" -stdout` | `https://mwis.org.uk/forecasts/scottish/west-highlands/text` | 0 |
| `python3 query_url.py "West Highlands"` | `{"url": "https://mwis.org.uk/forecasts/scottish/west-highlands/text"}` | 0 |
| `python3 query_url.py "West Highlands" --stdout` | `https://mwis.org.uk/forecasts/scottish/west-highlands/text` | 0 |
| `python3 query_url.py "Invalid"` | *(Error msg on stderr)* | 1 |
