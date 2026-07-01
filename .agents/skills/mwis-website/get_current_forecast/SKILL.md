---
name: get-current-forecast
description: Retrieve the most recent forecast for a region and date from the Mountain Weather Information Service (MWIS) website
version: 0.0.1
license: MIT
metadata:
  author: Mehmet Rahmi Karatay
---

# Get Current Forecast
The goal of this skill is to retrieve the most recent forecast for a specific region and date range from the Mountain Weather Information Service (MWIS) website.

## When to use
 - User asks for a forecast for a mountain region in the UK

## When NOT to use
 - The user requests a forecast from a source which is not MWIS, for example "According to the Met Office what will the weather on Ben Nevis be tomorrow?"

## Workflow
 1. Use the `identify_forecast_area` skill to identify the region
 2. Use the `identify_outing_date` skill to identify the date range (today and tomorrow for now)
 3. Fetch the forecast for the region and date range using the `fetch_mwis_forecast` tool.
 4. Summarise the forecast
 5. Present the forecast to the user

## Examples
 - Input: "Snowdonia, today and tomorrow" → Output: "[A summary of the forecast for Snowdonia for today and tomorrow]"

