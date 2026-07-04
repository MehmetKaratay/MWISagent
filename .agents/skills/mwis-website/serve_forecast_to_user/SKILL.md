---
name: serve-forecast-to-user
description: Retrieve the most recent forecast for a region and date from the Mountain Weather Information Service (MWIS) website
version: 0.0.1
license: MIT
metadata:
  author: Mehmet Rahmi Karatay
---

# Serve Forecast to User
The goal of this skill is to retrieve the most recent forecast for a specific region and date range from the Mountain Weather Information Service (MWIS) website.

## When to use
 - User asks for a forecast for a mountain region in the UK

## When NOT to use
 - The user requests a forecast from a source which is not MWIS, for example "According to the Met Office what will the weather on Ben Nevis be tomorrow?"

 ## Skill dependencies
  * identify_forecast_area
  * identify_forecast_date
  * fetch_mwis_forecast

## Workflow
 1. Use the `identify_forecast_area` skill to identify the region
 2. Identify the date range
    - If user does not specify a date, ask the user to provide a date or date range they are interested in. "Today", "Tomorrow", "Sunday to Wednesday", "02/07/2026" are all acceptable date formats; other identifiable dates are acceptable too.
    - If a user gives a date such as "02/07" clarify that you are interpreting this as "DD/MM/YYYY" and that this is 02nd July 2007. Allow the user to override the date specified if needed but do not proactively give them that option.
    - Use the `identify_outing_date` skill to check which forecast date(s) are available
    - If user requests a forecast that we do not have access to, for example because it is too far in the future, inform the user that we do not have access to that forecast and ask if they would like the closest available forecast instead. If they agree proceed to fetch the closest available forecast. If they do not agree, do not fetch any forecast and inform the user that you cannot help with their request
 3. Fetch the forecast for the region and date range using the `fetch_mwis_forecast` tool.
 4. Summarise the forecast
 5. Present the forecast to the user

## Examples
 - Input: "Snowdonia, today and tomorrow" → Output: "[A summary of the forecast for Snowdonia for today and tomorrow]"
