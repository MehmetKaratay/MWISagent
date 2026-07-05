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
from typing import Any, Dict, Optional, Tuple
import requests
from bs4 import BeautifulSoup

HEADING_MAPPING = {
    "summary for all": "uk_summary",
    "headline for": "region_headline",
    "how windy?": "wind_headline",
    "effect of the wind": "wind_effect",
    "how wet?": "precipitation",
    "cloud on the hills?": "cloud_hills",
    "chance of cloud free": "chance_cloud_free",
    "sunshine and air clarity?": "sun_clarity",
    "how cold?": "cold_temp",
    "freezing level": "freezing_level",
}


def fetch_forecast_html(source: str) -> str:
    """Fetch forecast HTML content from a URL or local file path."""
    if source.startswith("http://") or source.startswith("https://"):
        res = requests.get(source, timeout=10)
        res.raise_for_status()
        return res.text
    if not os.path.exists(source):
        raise FileNotFoundError(f"Local file not found: {source}")
    with open(source, "r", encoding="utf-8") as f:
        return f.read()


def _find_date_row(day_div: Any) -> Optional[Any]:
    """Find the row containing 'Viewing Forecast For' inside a day's container."""
    for row in day_div.find_all("div", class_="row"):
        heading_div = row.find("div", class_=lambda c: c and "col-lg-5" in c)
        if heading_div and "Viewing Forecast For" in heading_div.get_text(
            separator=" "
        ):
            return row
    for row in day_div.find_all("div", class_="row"):
        if "Viewing Forecast For" in row.get_text(separator=" "):
            return row
    return None


def _parse_date_text(content_div: Any) -> str:
    """Parse the date strong tag from the date metadata column."""
    strong_tags = content_div.find_all("strong")
    if len(strong_tags) >= 2:
        return strong_tags[1].get_text().strip()
    if len(strong_tags) == 1:
        return strong_tags[0].get_text().strip()
    return "Unknown Date"


def _parse_last_updated(content_div: Any) -> str:
    """Parse the last updated small tag from the date metadata column."""
    small_tag = content_div.find("small")
    if not small_tag:
        return ""
    last_updated = " ".join(small_tag.get_text().split())
    if last_updated.lower().startswith("last updated"):
        return last_updated[len("last updated") :].strip()
    return last_updated


def _extract_date_metadata(day_div: Any) -> Tuple[str, str]:
    """Extract the date and last updated fields from a day's forecast container."""
    row = _find_date_row(day_div)
    if not row:
        return "", ""
    content_div = row.find_all("div", class_=lambda c: c and "col" in c)[-1]
    if not content_div:
        return "", ""
    return _parse_date_text(content_div), _parse_last_updated(content_div)


def _extract_row_content(row: Any) -> Optional[Tuple[str, str]]:
    """Extract heading text and content text from a row if they exist."""
    h4 = row.find("h4")
    if not h4:
        return None
    cols = row.find_all("div", class_=lambda c: c and "col" in c)
    if len(cols) < 2:
        return None
    heading_text = h4.get_text().strip().lower()
    content_text = " ".join(cols[-1].get_text(separator=" ").split()).strip()
    return heading_text, content_text


def _parse_day_forecast(day_div: Any, idx: int) -> Dict[str, Any]:
    """Parse a single day's forecast div container."""
    date, last_updated = _extract_date_metadata(day_div)
    fields = {val: "" for val in HEADING_MAPPING.values()}
    for row in day_div.find_all("div", class_="row"):
        res = _extract_row_content(row)
        if not res:
            continue
        heading, content = res
        for heading_key, field_key in HEADING_MAPPING.items():
            if heading_key in heading:
                fields[field_key] = content
                break
    day_dict = {"day_index": idx, "date": date, "last_updated": last_updated}
    day_dict.update(fields)
    return day_dict


def _extract_region_name(soup: BeautifulSoup) -> str:
    """Extract the region name from the main <h1> tag."""
    h1 = soup.find("h1")
    if not h1:
        raise ValueError("Missing region header <h1>")
    return h1.get_text().strip()


def _extract_outlook(soup: BeautifulSoup) -> str:
    """Extract planning outlook description."""
    outlook_div = soup.find("div", class_="forecast-area--planning-outlook")
    if not outlook_div:
        return ""
    p_tag = outlook_div.find("p")
    text = p_tag.get_text() if p_tag else outlook_div.get_text()
    return " ".join(text.split()).strip()


def parse_forecast_html(html_content: str) -> Dict[str, Any]:
    """Parse MWIS forecast HTML content into a structured dictionary."""
    soup = BeautifulSoup(html_content, "html.parser")
    region = _extract_region_name(soup)
    days_data = []
    for idx in range(3):
        day_div = soup.find(id=f"Forecast{idx}")
        if not day_div:
            if idx == 0:
                raise ValueError("Missing Forecast0 container")
            continue
        days_data.append(_parse_day_forecast(day_div, idx))
    return {"region": region, "days": days_data, "outlook": _extract_outlook(soup)}


def get_forecast_data(source: str) -> Dict[str, Any]:
    """Orchestrates forecast fetching and parsing."""
    html = fetch_forecast_html(source)
    return parse_forecast_html(html)


def _parse_cli_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Parse MWIS forecast HTML to JSON.")
    parser.add_argument("source", help="URL or path to static forecast HTML")
    return parser.parse_args()


def _handle_cli_errors(err: Exception) -> int:
    """Map exceptions to appropriate CLI exit codes."""
    if isinstance(err, FileNotFoundError):
        sys.stderr.write(f"File Error: {err}\n")
        return 3
    if isinstance(err, requests.RequestException):
        sys.stderr.write(f"Network Error: {err}\n")
        return 2
    if isinstance(err, ValueError):
        sys.stderr.write(f"Parsing Error: {err}\n")
        return 4
    sys.stderr.write(f"Error: {err}\n")
    return 1


def main() -> None:
    """Main CLI entry point."""
    args = _parse_cli_args()
    try:
        data = get_forecast_data(args.source)
        print(json.dumps(data, indent=2))
        sys.exit(0)
    except Exception as err:
        sys.exit(_handle_cli_errors(err))


if __name__ == "__main__":
    main()
