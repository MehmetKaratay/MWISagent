# Forecast Source Skill Documentation

The `forecast_source` skill resolves a specific MWIS forecast region code or name (e.g., `WH` or `West Highlands`) into its corresponding direct text forecast URL on the Mountain Weather Information Service (MWIS) website.

## Component Overview

This skill utilizes the underlying python utility `get_forecast_url.py` to identify the URL.

- **Skill Entry Point**: `skills-mwis-website/forecast_source/SKILL.md`
- **CLI Utility**: `skills-mwis-website/forecast_source/scripts/get_forecast_url.py`

## CLI Usage

To run the utility manually:
```bash
python3 get_forecast_url.py <region_code_or_name> [custom_csv_path] [-stdout]
```

### Input Formats

The script accepts:
1. **Region Code** (case-insensitive): E.g., `"WH"`, `"SD"`, `"LD"`.
2. **Region Name** (case-insensitive): E.g., `"West Highlands"`, `"lake district"`.

### Optional Flags

- `-stdout` / `--stdout`: Output the raw URL string directly to `stdout` instead of a JSON object.

### Output Format

By default, on success, the script outputs a JSON object containing the URL to `stdout` and exits with code 0:
```bash
python3 get_forecast_url.py "WH"
```
Output:
```json
{"url": "https://mwis.org.uk/forecasts/scottish/west-highlands/text"}
```

With the `-stdout` or `--stdout` flag, it outputs the raw URL string directly to `stdout`:
```bash
python3 get_forecast_url.py "WH" -stdout
```
Output:
```
https://mwis.org.uk/forecasts/scottish/west-highlands/text
```

If the region is not found or the input is invalid, it prints an error message to `stderr` and exits with code 1:
```bash
python3 get_forecast_url.py "InvalidRegion"
```
Output (stderr):
```
Error: No matching MWIS region found for: 'InvalidRegion'
```

## Underlying Configuration Files

- `resources/mwis-regions.csv`: A CSV mapping database of all 10 MWIS region codes, names, countries, and direct forecast text URLs.
