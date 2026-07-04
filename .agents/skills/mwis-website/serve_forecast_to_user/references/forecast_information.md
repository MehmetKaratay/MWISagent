# Forecast structure

## Overview of forecast structure
* The forecast for each region is on a single URL.
* Each region has a reference height (RefHeight in [mwis-regions.csv](file;file:///home/karatay/Repositories/learning/ai/MWISagent/skills-mwis-website/fetch_specific_forecast/references/mwis-regions.csv)) which is usually what the temperatures and wind refers to.
  - If the forecast also includes information for a different altitude this will be made clear in the text. 
  - Example: "On the highest summits" on the WH forecast refers to summits approaching the height of Ben Nevis, so around 1200 to 1350m.
  - Example: "Midslopes" refers to a region approximately half of the reference height. "Midslopes in EH" is around 400 to 600m. "Midslopes in LD" is approximate 300 to 500m. 

Each page load provides a 3-day forecast and an outlook. The timespan of the outlook varies depending on confidence of the forecaster. It is usually around a 7 to 10 days ahead.

The first forecast will either refer to today or tomorrow. A new forecast is usually issued between 1600 and 1700 British Time, but can be isssued earlier on occasion. The first forecast will be for today before it is issued and for tomorrow after it is issued.

Only the first forecast includes
 - Forecast summary for all regions
 - Forecast headline for specific region

## Forecast update timestamp
Each forecast has a 'last updated' field. This does not necessarily refer to the issue time. For example, a forecast could be issued at 1630 one day, but updated at 0730 the following day. An update usually means
 - The weather has changed
 - There was a typo

## Importance of field for mountain safety
The forecast is written in the order of importance for mountain activities: wind > rain > cloud (Cloud & Visbility) > Temp (Temp at RefHeight and either FL or ValleyTemp depending on region).  

- **Last Updated vs. Issue Time**: The "Last updated" timestamp indicates when the text was last modified (e.g. for updates or typo corrections), not when the forecast cycle was initially released.
- **Altitudes**: Wind and temperatures refer to the region's reference height (`RefHeight` in CSV). Altitude variations are explicitly mentioned in the text (e.g. "On the highest summits" or "Midslopes").