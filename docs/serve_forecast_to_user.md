# Serve Forecast to User Skill

The `serve_forecast_to_user` skill encapsulates the domain-specific business rules for fetching and pruning MWIS mountain region weather forecasts.

## Core Responsibilities

1. **Forecast Retrieval Orchestration**: Coordinates the resolution of region and date parameters.
2. **Payload Pruning & Filtering**: Dynamically filters the forecast JSON dictionary payload based on user-requested day/outlook date codes to prevent downstream LLM information disclosure and prompt tampering.

---

## Design and Constraints (Third-Party Forecast Nuances)

> [!IMPORTANT]
> The detailed third-party forecaster behavior, date calibration offsets, and layout design of the live MWIS forecasts are documented in [forecast_information.md](file:///home/karatay/Repositories/weather/mwis_agent/app/skills/mwis-website/serve_forecast_to_user/references/forecast_information.md). Refer to it for details on variable publication times (11:00 AM vs 5:00 PM), freezing level valley temperature overrides, and mountain safety field priorities.

---

## Technical Implementation

### Pruning Script
The filtering logic is implemented as a deterministic Python script at [filter_forecast.py](file:///home/karatay/Repositories/weather/mwis_agent/app/skills/mwis-website/serve_forecast_to_user/scripts/filter_forecast.py).

- **Function**: `filter_forecast_payload(forecasts: dict, resolved: list[str]) -> dict`
- **Behavior**:
  - If `resolved` is empty, returns the payload unmodified (representing a "full forecast" or unrestricted date query).
  - If `resolved` contains codes (e.g., `['D0', 'D1']`), strips out unrequested days from the `"days"` array and removes the `"outlook"` dictionary.
  - If `resolved` is `['Doutlook']`, strips out `"days"` and preserves the `"outlook"`.

### Dynamic Invocation
Since the skill resides within a directory containing a hyphen (`mwis-website`), standard Python import statements cannot be used. The orchestration layer in `agent_logic.py` dynamically loads the module at runtime:

```python
# app/agent_logic.py
def load_filter_forecast() -> Any:
    path = os.path.join(
        os.path.dirname(__file__),
        "skills",
        "mwis-website",
        "serve_forecast_to_user",
        "scripts",
        "filter_forecast.py",
    )
    # ... dynamic import logic using importlib.util ...
```
