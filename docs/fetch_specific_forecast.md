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
