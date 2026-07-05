---
name: serve-forecast-to-user
description: Retrieve the most recent forecast for a region and date from the Mountain Weather Information Service (MWIS) website
version: 0.0.1
license: MIT
metadata:
  author: Mehmet Rahmi Karatay
---

# Serve Forecast to User
Identify which forecast the user wants and request a JSON version of it from `fetch_specific_forecast`. Pass back to the agent who will serve it to the user.

This skills 'glues' the other skills in `MWISagent/.agent/skills/mwis-website/` together.

## When to use
 - User asks for a forecast for a mountain region in the UK

## When NOT to use
 - The user requests a forecast from a source which is not MWIS, for example "According to the Met Office what will the weather on Ben Nevis be tomorrow?"

 ## Skill dependencies
  * identify_forecast_area
  * identify_outing_date
    - Defines D0, D1, Doutlook etc.
  * fetch_specific_forecast

## Workflow
 1. Use the `identify_forecast_area` skill to identify the region
 2. Identify the date range
    - If user does not specify a date, ask the user to provide a date or date range they are interested in. "Today", "Tomorrow", "Sunday to Wednesday", "02/07/2026" are all acceptable date formats; other identifiable dates are acceptable too.
    - If a user gives a date such as "02/07" clarify that you are interpreting this as "DD/MM/YYYY" and that this is 02nd July 2007. Allow the user to override the date specified if needed but do not proactively give them that option.
    - Use the `identify_outing_date` skill to check which forecast date(s) are available
    - If user requests a forecast that we do not have access to, for example because it is too far in the future, inform the user that we do not have access to that forecast and ask if they would like the closest available forecast instead. If they agree proceed to fetch the closest available forecast. If they do not agree, do not fetch any forecast and inform the user that you cannot help with their request
  3. Fetch the forecast for the region and date range using the `fetch_specific_forecast` tool.
  4. Pass the relevant dates back to the agent:
     - Map the resolved date codes (`D0`, `D1`, `D2`, etc.) to the parsed JSON days or outlook.
     - **Date-based Calibration Rules**:
       - Because new forecasts can be issued at variable times (sometimes as early as 11:00 AM), do NOT rely on system time to determine the mapping.
       - Instead, compare the parsed `"date"` field in `days[0]` with the current system/local calendar date to calibrate:
         - **If `days[0]["date"]` is today's date**:
           - `D0` (today) maps to `days` element with `day_index == 0`
           - `D1` (tomorrow) maps to `days` element with `day_index == 1`
           - `D2` (day after tomorrow) maps to `days` element with `day_index == 2`
         - **If `days[0]["date"]` is tomorrow's date**:
           - `D1` (tomorrow) maps to `days` element with `day_index == 0`
           - `D2` (day after tomorrow) maps to `days` element with `day_index == 1`
           - `D3` (3 days ahead) maps to `days` element with `day_index == 2`
       - **Outlook Mapping**:
         - Date codes representing dates not covered by the 3 elements in the `days` array (e.g. `D3` when `days[0]` is today, or any `Doutlook` spanning offset days 4 to 7) map to the root-level `"outlook"` string field in the JSON file.
       - Always verify the `"date"` field value in each day's dictionary against your target date to ensure exact alignment.
     - **Filtering Examples**:
       - If a forecast is requested for 5 days time (`Doutlook`), only return the `outlook`.
       - If a forecast is requested only for 'Saturday' and the request is made on Thursday evening (resolving to `D2`), only return that specific day's dictionary (where `day_index` aligns with Saturday's date); ignore other days.
       - If a forecast is requested for 'Saturday to Wednesday' on a Friday (resolving to `D1, D2, D3, Doutlook`), only return those matching days and the overall outlook.

## Examples
 - Input: "Current forecast for the Cairngorms" → Output: [forecast_structure.json](file:references/forecast_structure.json)
