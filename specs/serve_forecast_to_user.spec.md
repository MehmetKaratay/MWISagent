---
name: serve_forecast_to_user
summary: Specification for the deterministic forecast payload filtering helper inside the serve-forecast-to-user skill.
---

# Specifications - Serve Forecast to User Filtering

This spec details the behavior and interface for filtering retrieved forecasts JSON.

## Public Interface

### `filter_forecast_payload`
- **Module Path:** `app.skills.mwis-website.serve_forecast_to_user.scripts.filter_forecast`
- **Signature:** `def filter_forecast_payload(forecasts: dict, resolved: list[str]) -> dict`
- **Arguments:**
  - `forecasts`: The dictionary containing retrieved forecast data for each region.
  - `resolved`: List of resolved date codes (e.g. `['D0', 'D1']`, `['Doutlook']`).
- **Returns:** A copy of the `forecasts` dictionary with unrequested forecast days and outlook sections pruned.

---

## Test Cases & Acceptance Criteria

### Case 1: Filter Multiple Days
- **Input:**
  - `forecasts` with a region's days having codes `D0`, `D1`, `D2`, and an `outlook` dictionary.
  - `resolved = ['D0', 'D1']`
- **Output:**
  - The region's dictionary retains only `D0` and `D1` in `"days"`.
  - `"outlook"` is omitted.

### Case 2: Filter Outlook Only
- **Input:**
  - `forecasts` with a region's days having codes `D0`, `D1`, `D2`, and an `outlook` dictionary.
  - `resolved = ['Doutlook']`
- **Output:**
  - `"days"` is empty or omitted.
  - `"outlook"` is preserved.

### Case 3: Empty Date Resolution (Full Forecast)
- **Input:**
  - `forecasts` with all sections.
  - `resolved = []`
- **Output:**
  - The `forecasts` dictionary remains completely untouched and unfiltered.

---

## Detailed Fields Extraction Specifications

### `extract_forecast_details`
- **Module Path:** `app.skills.mwis-website.serve_forecast_to_user.scripts.extract_forecast_details`
- **Signature:** `def extract_forecast_details(forecasts: dict, categories: list[str]) -> dict`
- **Arguments:**
  - `forecasts`: The dictionary containing resolved forecast data.
  - `categories`: List of query categories extracted from the user query.
- **Returns:** A copy of the `forecasts` dictionary with days and outlook filtered to only contain fields matching the requested categories.
- **CSV Configuration:** Stored in `references/category_mappings.csv` mapping categories to forecast fields.
  - If a category is `'full'`, all fields are returned.
  - If the categories list is empty (default), only headline-only fields are returned (`uk_summary`, `region_headline`, `wind_headline`, `precip_headline`, `cloud_headline`).
  - Otherwise, only returns mapped fields for matching categories (always preserving basic metadata: `date`, `forecast_index`, `last_updated`, `Dcode`).
