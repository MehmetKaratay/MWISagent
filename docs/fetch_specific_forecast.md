# Fetch Specific Forecast Skill Documentation

The `fetch_specific_forecast` skill resolves a specific MWIS forecast region code or name (e.g., `WH` or `West Highlands`) into its corresponding direct text forecast URL, freezing level formatting (`FLorValley`), and reference height (`RefHeight`).

## Component Overview

This skill utilizes the underlying python utilities:
- **Freezing Level Query**: `skills-mwis-website/fetch_specific_forecast/scripts/query_fl.py`
- **Reference Height Query**: `skills-mwis-website/fetch_specific_forecast/scripts/query_refHeight.py`
- **Forecast URL Query**: `skills-mwis-website/fetch_specific_forecast/scripts/query_url.py`
- **Shared Helpers**: `skills-mwis-website/fetch_specific_forecast/scripts/query_utils.py`

---

## query_fl.py CLI Usage

To run the freezing level utility manually:
```bash
python3 query_fl.py <region_code_or_name> [custom_csv_path]
```

### Output Format
On success, outputs JSON indicating if the freezing level is calculated as a Freezing Level (`FL`) or Valley Temperature (`Valley`):
```bash
python3 query_fl.py "WH"
```
Output:
```json
{"FLorValley": "FL"}
```

---

## query_refHeight.py CLI Usage

To run the reference height utility manually:
```bash
python3 query_refHeight.py <region_code_or_name> [custom_csv_path]
```

### Output Format
On success, outputs JSON containing the reference height:
```bash
python3 query_refHeight.py "WH"
```
Output:
```json
{"RefHeight": "900m"}
```

---

## query_url.py CLI Usage

To run the URL utility manually:
```bash
python3 query_url.py <region_code_or_name> [custom_csv_path] [-stdout]
```

### Output Format
By default, outputs a JSON object containing the URL:
```bash
python3 query_url.py "WH"
```
Output:
```json
{"url": "https://mwis.org.uk/forecasts/scottish/west-highlands/text"}
```

---

## Underlying Configuration Files

- `references/mwis-regions.csv`: A CSV database of all 10 MWIS regions containing codes, names, countries, reference heights, freezing level calculation formats, and forecast URLs.

---

## parse_forecast.py CLI Usage

To parse an MWIS text forecast HTML page into JSON:
```bash
python3 parse_forecast.py <source>
```
The `<source>` argument can be a local file path or a URL starting with `http://` or `https://`.

### Output Format
On success, outputs a JSON object containing the parsed forecast data:
```bash
python3 parse_forecast.py tests/resources/eh-forecast.html
```
Output:
```json
{
  "region": "Cairngorms NP and Monadhliath",
  "days": [
    {
      "forecast_index": 0,
      "date": "Sunday 5th July 2026",
      "last_updated": "Sat 4th Jul 26 at 4:17PM",
      "uk_summary": "...",
      "region_headline": "...",
      "wind_headline": "...",
      "wind_effect": "...",
      "precip_headline": "...",
      "precip_detail": "...",
      "cloud_headline": "...",
      "cloud_detail": "...",
      "chance_cloud_free": "...",
      "sun_clarity": "...",
      "temp": "...",
      "freezing_level": "..."
    }
  ],
  "outlook": "Planning outlook text..."
}
```

### Exit Codes
- `0`: Success
- `1`: General Error
- `2`: Network Error (if URL fetch fails)
- `3`: File Missing Error (if local file path is invalid)
- `4`: Parsing Error (if HTML structure is invalid)
