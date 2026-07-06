# Query Country Guardrail Documentation

The `query_country.py` utility provides deterministic mapping of geographic terms (e.g. "Scotland", "Welsh", "Peak District") to explicit MWIS region codes, while enforcing a hard safety limit of 5 regions.

## Location
`/mwis-agent/app/skills/mwis-website/fetch_specific_forecast/scripts/query_country.py`

## Usage

You can use the script programmatically in your Python code:

```python
from app.skills.mwis_website.fetch_specific_forecast.scripts.query_country import get_regions_for_countries

# 1. Single Region Lookups
regions = get_regions_for_countries(["Ben Nevis"])
print(regions)  # Output: ["WH"]

# 2. Macro-Region Expansion
regions = get_regions_for_countries(["Wales"])
print(regions)  # Output: ["SD", "BB"] (Snowdonia, Brecon Beacons)

# 3. Handling Unrecognized Inputs (graceful degradation)
regions = get_regions_for_countries(["France", "Ben Nevis"])
print(regions)  # Output: ["WH"]
```

## Guardrail: The 5-Region Cap

To prevent abuse, token exhaustion, and rate-limiting from the MWIS API backend, `get_regions_for_countries` strictly raises a `ValueError` if the evaluated request expands into more than 5 explicit MWIS regions.

```python
try:
    regions = get_regions_for_countries(["Scotland", "England"])
    # Scotland = 5 regions, England = 3 regions -> Total = 8 regions
except ValueError as e:
    print(str(e)) # Output: "Requested 8 regions. Maximum allowed is 5."
```

## Agent Integration
Within the ADK `resolve_and_fetch` node, this error is caught and safely routed to the `clarify_too_many_locations` human-in-the-loop interruption, asking the user to manually narrow down their requested areas.
