# Extract Forecast Details Skill Utility Documentation

The `extract_forecast_details` utility prunes a resolved forecast JSON payload down to only requested weather aspects or categories.

## Component Overview

- **Script Location**: `app/skills/mwis-website/serve_forecast_to_user/scripts/extract_forecast_details.py`
- **Mapping Config**: `app/skills/mwis-website/serve_forecast_to_user/references/category_mappings.csv`

## API Usage

```python
from app.skills.mwis_website.serve_forecast_to_user.scripts.extract_forecast_details import extract_forecast_details

filtered_payload = extract_forecast_details(forecasts, categories)
```

### Parameters
- `forecasts` (dict): A dictionary containing MWIS region forecast JSON structures.
- `categories` (list[str]): A list of categories extracted from the user query.

## Category Mappings

Mappings are configured via `category_mappings.csv`:

| Category | Forecast Fields Retained | Description / Example Keywords |
|----------|--------------------------|--------------------------------|
| `cloud`  | `uk_summary`, `region_headline`, `cloud_headline`, `cloud_detail`, `chance_cloud_free` | cloud, mist, fog, overcast, shrouded, clarity, visibility |
| `wind`   | `uk_summary`, `region_headline`, `wind_headline`, `wind_effect` | wind, breezy, gale, gusts, blow, stormy |
| `wet`    | `uk_summary`, `region_headline`, `precip_headline`, `precip_detail` | rain, wet, snow, shower, drizzle, precipitation, sleet |
| `cold`   | `uk_summary`, `region_headline`, `temp`, `freezing_level` | cold, temperature, freezing, chill, frost, warm, heat |
| `sun`    | `uk_summary`, `region_headline`, `sun_clarity` | sun, sunny, sunshine |
| `full`   | All fields | full, everything, complete, detailed |

## Pruning Rules

- **Metadata Preservation**: Basic metadata (`date`, `forecast_index`, `last_updated`, `Dcode`) is always preserved in every day's dictionary.
- **Default (Headlines Only)**: If the categories list is empty, the utility retains only headline-only fields: `uk_summary`, `region_headline`, `wind_headline`, `precip_headline`, and `cloud_headline`.

### Key Ordering Rules

Day forecast output dictionary keys are deterministically sorted to prioritize user requested values:
1. `date`
2. `last_updated`
3. User-requested fields (in order of category list)
4. `uk_summary` (only if index is 0)
5. `region_headline` (only if index is 0)
6. Remaining default/headline fields (matching pattern `*_headline`)
7. Remaining allowed metadata (e.g. `forecast_index`, `Dcode`)
