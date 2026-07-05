---
name: fetch-specific-forecast
description: Retrieves the source URL of a specific forecast area from the Mountain Weather Information Service (MWIS) website.
version: 0.0.1
license: MIT
metadata:
  author: Mehmet Rahmi Karatay
---

# Fetch Specific Forecast
The goal of this skill is to retrieve the source URL of a specific forecast area from the Mountain Weather Information Service (MWIS) website using a deterministic process. It uses the `mwis-regions.csv` mapping file to find the source URL.

## When to use
 - You need to retrieve the source URL of a specific forecast area from the Mountain Weather Information Service (MWIS) website.
 - You have the forecast region name or code and want to get the source URL.

## When NOT to use
 - You do not know the forecast region name or code.
 - You already know the source URL

## Workflow
 1. Use the `query_url.py` script to try to find the source URL.
 2. If the script returns a URL, return it.
 3. If the script returns an error, use your own logic to inspect `references/mwis-regions.csv` to find the source URL.

## Examples
 - Input: "WH" → Output: "https://mwis.org.uk/forecasts/scottish/west-highlands/text"
 - Input: "West Highlands" → Output: "https://mwis.org.uk/forecasts/scottish/west-highlands/text"

## Anti-patterns to avoid
 - Don't give any response that does not point to the MWIS website (https://www.mwis.org.uk)
