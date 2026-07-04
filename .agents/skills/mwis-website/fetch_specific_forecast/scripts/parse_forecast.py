#!/usr/bin/env python3
# Copyright (c) 2026 Mehmet Rahmi Karatay
# Licensed under the MIT License.

"""
Parser module and CLI to convert MWIS text forecast HTML pages into JSON.
"""

import os
import sys
import json
import argparse
from typing import Any, Dict
import requests
from bs4 import BeautifulSoup


def fetch_forecast_html(source: str) -> str:
    """Fetch forecast HTML content from a URL or local file path.

    Args:
        source (str): URL starting with http/https, or absolute/relative file path.

    Returns:
        str: Raw HTML content.

    Raises:
        FileNotFoundError: If a local file path does not exist.
        requests.RequestException: If HTTP fetch fails.
    """
    if source.startswith("http://") or source.startswith("https://"):
        res = requests.get(source, timeout=10)
        res.raise_for_status()
        return res.text
    else:
        if not os.path.exists(source):
            raise FileNotFoundError(f"Local file not found: {source}")
        with open(source, "r", encoding="utf-8") as f:
            return f.read()


def parse_forecast_html(html_content: str) -> Dict[str, Any]:
    """Parse MWIS forecast HTML content into a structured dictionary.

    Args:
        html_content (str): The raw HTML content of the forecast.

    Returns:
        Dict[str, Any]: A dictionary following the parse_forecast specification.

    Raises:
        ValueError: If the HTML structure is fundamentally invalid.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Extract Region
    h1 = soup.find("h1")
    if not h1:
        raise ValueError("Missing region header <h1>")
    region = h1.get_text().strip()

    days_data = []
    # Loop over the three forecast days
    for idx in range(3):
        day_id = f"Forecast{idx}"
        day_div = soup.find(id=day_id)
        if not day_div:
            # Only Day 1 (Forecast0) is strictly critical
            if idx == 0:
                raise ValueError("Missing Forecast0 container")
            continue

        date = ""
        last_updated = ""
        viewing_for_row = None

        # Extract date and last_updated
        for row in day_div.find_all("div", class_="row"):
            heading_div = row.find("div", class_=lambda c: c and "col-lg-5" in c)
            if heading_div and "Viewing Forecast For" in heading_div.get_text(separator=" "):
                viewing_for_row = row
                break
        
        # Some older or different layouts might just use col-xs-12 or col-md-3 etc.
        # Let's fallback if the above didn't work but we find "Viewing Forecast For" anywhere
        if not viewing_for_row:
            for row in day_div.find_all("div", class_="row"):
                if "Viewing Forecast For" in row.get_text(separator=" "):
                    viewing_for_row = row
                    break

        if viewing_for_row:
            content_div = viewing_for_row.find_all("div", class_=lambda c: c and "col" in c)[-1]
            if content_div:
                strong_tags = content_div.find_all("strong")
                if len(strong_tags) >= 2:
                    date = strong_tags[1].get_text().strip()
                elif len(strong_tags) == 1:
                    date = strong_tags[0].get_text().strip()
                else:
                    date = "Unknown Date"
                
                small_tag = content_div.find("small")
                if small_tag:
                    last_updated = " ".join(small_tag.get_text().split())
                    # strip out "Last updated" text if present
                    if last_updated.lower().startswith("last updated"):
                        last_updated = last_updated[len("last updated"):].strip()

        fields: Dict[str, str] = {
            "uk_summary": "",
            "region_headline": "",
            "wind_mountain": "",
            "wind_effect": "",
            "precipitation": "",
            "cloud_hills": "",
            "chance_cloud_free": "",
            "sun_clarity": "",
            "cold_temp": "",
            "freezing_level": ""
        }

        # Extract remaining fields
        for row in day_div.find_all("div", class_="row"):
            # MWIS format uses an H4 for the heading inside a col-lg-5 or similar
            h4 = row.find("h4")
            if not h4:
                continue
            
            heading_text = h4.get_text().strip().lower()
            
            # The content is usually in the sibling column or the last column in the row
            cols = row.find_all("div", class_=lambda c: c and "col" in c)
            if len(cols) < 2:
                continue
            
            # Use the last col which typically contains the content
            content_div = cols[-1]
            content_text = " ".join(content_div.get_text(separator=" ").split()).strip()

            if "summary for all" in heading_text:
                fields["uk_summary"] = content_text
            elif "headline for" in heading_text:
                fields["region_headline"] = content_text
            elif "how windy?" in heading_text:
                fields["wind_mountain"] = content_text
            elif "effect of the wind" in heading_text:
                fields["wind_effect"] = content_text
            elif "how wet?" in heading_text:
                fields["precipitation"] = content_text
            elif "cloud on the hills?" in heading_text:
                fields["cloud_hills"] = content_text
            elif "chance of cloud free" in heading_text:
                fields["chance_cloud_free"] = content_text
            elif "sunshine and air clarity?" in heading_text:
                fields["sun_clarity"] = content_text
            elif "how cold?" in heading_text:
                fields["cold_temp"] = content_text
            elif "freezing level" in heading_text:
                fields["freezing_level"] = content_text

        day_dict = {
            "day_index": idx,
            "date": date,
            "last_updated": last_updated
        }
        day_dict.update(fields)
        days_data.append(day_dict)

    # Extract Planning Outlook
    outlook = ""
    outlook_div = soup.find("div", class_="forecast-area--planning-outlook")
    if outlook_div:
        p_tag = outlook_div.find("p")
        if p_tag:
            outlook = " ".join(p_tag.get_text().split()).strip()
        else:
            # Fallback if there is no p tag inside it
            outlook = " ".join(outlook_div.get_text().split()).strip()

    return {
        "region": region,
        "days": days_data,
        "outlook": outlook
    }


def get_forecast_data(source: str) -> Dict[str, Any]:
    """Orchestrates forecast fetching and parsing.

    Args:
        source (str): Source path or URL.

    Returns:
        Dict[str, Any]: Parsed forecast data dict.
    """
    html = fetch_forecast_html(source)
    return parse_forecast_html(html)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Parse MWIS forecast HTML to JSON.")
    parser.add_argument("source", help="URL or path to static forecast HTML")
    args = parser.parse_args()

    try:
        data = get_forecast_data(args.source)
        print(json.dumps(data, indent=2))
        sys.exit(0)
    except FileNotFoundError as err:
        sys.stderr.write(f"File Error: {err}\n")
        sys.exit(3)
    except requests.RequestException as err:
        sys.stderr.write(f"Network Error: {err}\n")
        sys.exit(2)
    except ValueError as err:
        sys.stderr.write(f"Parsing Error: {err}\n")
        sys.exit(4)
    except Exception as err:
        sys.stderr.write(f"Error: {err}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
