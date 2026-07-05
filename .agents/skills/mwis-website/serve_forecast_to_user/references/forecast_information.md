# Forecast structure

## Forecast nuances

* Forecasts are issued once a day, usually between 1600 and 1700 British Time, but can be issued earlier on occasion. There is no way to predict this as it is based on human behaviour and experiences.

* The first forecast will either refer to today or tomorrow. The date of the forecast will clarify this.

* Each forecast JSON file contains a 3-day forecast and an outlook.
  - Example of stucture: [forecast_structure.json](file:///home/karatay/Repositories/weather/MWISagent/.agents/skills/mwis-website/serve_forecast_to_user/references/forecast_structure.json)

* The timespan of the outlook varies depending on confidence of the forecaster. It is usually around a 7 to 10 days ahead.

* Only the first forecast includes
 - Forecast summary for all regions
 - Forecast headline for specific region
 - Extra details

* If confidence in the whole day's forecast is particularly low, the forecast will mention this, usually in `uk_summary`, `region_headline`, or `wind_headline`.

* Sometime low confidece will only be mentioned for one field, e.g. `precip_headline` or `precip_detail`. This usually refers only to that field, except for the `wind_headline` field when it usually refers to the whole forecast.

* Each region has a reference height (RefHeight in [mwis-regions.csv](file;file:///home/karatay/Repositories/learning/ai/MWISagent/skills-mwis-website/fetch_specific_forecast/references/mwis-regions.csv)) which is usually what the temperatures and wind refers to.
  - If the forecast also includes information for a different altitude this will be made clear in the text.
  - Example: "On the highest summits" on the WH forecast refers to summits approaching the height of Ben Nevis, so around 1200 to 1350m.
  - Example: "Midslopes" refers to a region approximately half of the reference height. "Midslopes in EH" is around 400 to 600m. "Midslopes in LD" is approximate 300 to 500m.

* Most forecasts contain a freezing level in the `freezing_level` field. YD and PD use this field to refer to valley temperature.
  - Freezing levels are not usually given for YD and PD
  - Valley temps are occasionally given for other regions. This is usually mentioned in the `temp` field.

  * `*cloud*` fields refer to whether the mountain will be in cloud. The sky could be overcast but mountain cloud free.

  * `sun_clarity` refers to air visibility _out of cloud_ and to the chance of sunshine coming through the clouds.

## Forecast update timestamp
Each forecast has a 'last updated' field. This does not necessarily refer to the issue time. For example, a forecast could be issued at 1630 one day, but updated at 0730 the following day. An update usually means
 - The weather has changed
 - There was a typo

## Importance of field for mountain safety
The forecast is written in the order of importance for mountain activities: wind > rain > cloud (Cloud & Visbility) > Temp (Temp at RefHeight and either FL or ValleyTemp depending on region).

- **Last Updated vs. Issue Time**: The "Last updated" timestamp indicates when the text was last modified (e.g. for updates or typo corrections), not when the forecast cycle was initially released.
