---
name: identify-forecast-area
description: Identify forecast area from a town, region name, location, mountain name, or OS Grid Reference. You will return the forecast area code unless something else is specifically requested.
version: 0.0.1
license: MIT
metadata:
  author: Mehmet Rahmi Karatay
---

# Identify Forecast Area
You will return the MWIS region that contains the location specified using `scripts/query_region.py`. If the location is not specified you will return the nearest and its direction also using `query_region.py`.

## When to use
 * You are asked to get a forcast for an unkown MWIS region
 * You are asked to get a forecast for any of the following:
   - Mountain name
   - Place name
   - OS Grid Reference

## When NOT to use
 - The region and/or region code is already specified or known
 - The forecast area code is already known

## Workflow
 1. Confirm that the MWIS region is currently unkown.
 2. Use `scripts/query_region.py` to get a deterministic answer.
 3. Return the output of the script without modifying it.

## Examples
 - "Ben Nevis" → "Region(s): WH (West Highlands)"
 - "NH 123 123" → "Region(s): NW (North West Highlands)"
 - "London" → "The location is not in an MWIS area.
Nearest area(s): \n PD (Peak District): 193.66 km away to the NW \n BB (Brecon Beacons): 203.57 km away to the W"

## Output format
 - Use `assets/template.md` etc.

## Anti-patterns to avoid
 - Avoid guessing. If you are unsure say so
