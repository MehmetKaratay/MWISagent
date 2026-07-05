# Parse Forecast Spec

This specification defines a Python library and CLI tool `parse_forecast.py` to fetch and parse MWIS mountain weather forecast HTML pages into structured JSON.

```yaml
name: parse_forecast
summary: Fetch MWIS region forecast HTML pages and parse them into a decoupled, structured JSON schema.
inputs:
  - name: source
    type: string
    required: true
    description: "MWIS text forecast URL (e.g. https://mwis.org.uk/...) or a local file path containing static HTML."
outputs:
  - name: forecast
    type: json
    description: "A structured JSON object containing region, daily forecast attributes, and the planning outlook."
exit_codes:
  0: Success
  1: General execution or argument error
  2: Network failure (HTTP request timeout, connection error, or status code not 200)
  3: File not found (local filesystem source path does not exist)
  4: HTML parsing error (missing critical structure, e.g. region <h1> tag or forecast days)
dependencies:
  - python >= 3.10
  - beautifulsoup4 >= 4.12.3
  - requests >= 2.31.0
```

## Behavior & Decoupled Architecture

- **Fetcher Interface**:
  - `fetch_forecast_html(source: str) -> str`: If `source` starts with `http://` or `https://`, downloads HTML via `requests.get` (with a timeout of 5 seconds). Otherwise, treats `source` as a local path and reads the file from the filesystem.
- **Parsing Logic (`parse_forecast_html`)**:
  - Extracts the region name from the `<h1>` tag.
  - Traverses the 3 forecast days mapped to divs with IDs `Forecast0`, `Forecast1`, and `Forecast2`.
  - For each day, extracts:
    - `date`: Found inside the metadata `<p>` tag (e.g., `Sunday 5th July 2026`).
    - `last_updated`: Found inside the metadata `<small>` tag.
    - `uk_summary`: Extracted from the `Summary for all mountain areas` heading row (Day 1 only).
    - `region_headline`: Extracted from the `Headline for [Region]` heading row (Day 1 only).
    - `wind_headline`: Extracted from `How windy?` heading row.
    - `wind_effect`: Extracted from `Effect of the wind on you?` heading row.
    - `precipitation`: Extracted from `How Wet?` heading row.
    - `cloud_hills`: Extracted from `Cloud on the hills?` heading row.
    - `chance_cloud_free`: Extracted from `Chance of cloud free Munros?` heading row.
    - `sun_clarity`: Extracted from `Sunshine and air clarity?` heading row.
    - `cold_temp`: Extracted from `How Cold?` heading row.
    - `freezing_level`: Extracted from `Freezing Level` heading row.
  - Extracts the text under the `Planning Outlook` heading (usually the element inside `<div class="forecast-area--planning-outlook">`).
- **Defensive Design**:
  - If any optional element is missing in the HTML, returns an empty string `""` for that field rather than raising an error, preventing page updates from breaking the tool.

## JSON Schema Example

```json
{
  "region": "Eastern Highlands",
  "days": [
    {
      "day_index": 0,
      "date": "Sunday 5th July 2026",
      "last_updated": "Sat 4th Jul 26 at 4:17PM",
      "uk_summary": "Early sunny bursts...",
      "region_headline": "A few sunny glimpses...",
      "wind_headline": "...",
      "wind_effect": "...",
      "precipitation": "...",
      "cloud_hills": "...",
      "chance_cloud_free": "...",
      "sun_clarity": "...",
      "cold_temp": "...",
      "freezing_level": "..."
    },
    ...
  ],
  "outlook": "Planning outlook text..."
}
```

---

## Design Decisions

- **Database Transition**:
  - The HTML parsing logic defined in this specification is designed to be replaceable. In the future, the backend might fetch forecast data directly from a database query instead of scraping the live MWIS HTML pages.
  - The external interface—specifically the JSON output schema, CLI arguments, and CLI exit codes—**must remain unchanged** when this transition to a database query occurs to ensure full backward compatibility.
