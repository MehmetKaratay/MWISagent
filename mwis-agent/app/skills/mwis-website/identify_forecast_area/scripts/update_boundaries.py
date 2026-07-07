#!/usr/bin/env python3
"""
Utility script to parse GPX boundary trackpoints and regenerate the MWIS region boundaries JSON file.
"""

import glob
import json
import os
import xml.etree.ElementTree as ET
from typing import Any

# Path Configuration relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GPX_DIR = os.path.join(SCRIPT_DIR, "..", "resources", "gpx_files", "mwis_areas")
OUTPUT_JSON_PATH = os.path.join(
    SCRIPT_DIR, "..", "assets", "mwis-region-boundaries.json"
)

# Official Region Code to Name mapping
REGION_NAMES = {
    "NW": "North West Highlands",
    "EH": "Eastern Highlands",
    "WH": "West Highlands",
    "SH": "Southeastern Highlands",
    "SU": "Southern Uplands",
    "LD": "Lake District",
    "YD": "Yorkshire Dales & North Pennines",
    "PD": "Peak District",
    "SD": "Snowdonia & North Wales",
    "BB": "Brecon Beacons",
}

# Constants
XML_TRKPT_TAG = "trkpt"
LAT_ATTR = "lat"
LON_ATTR = "lon"
JSON_INDENT = 2


def _parse_trackpoint(elem: ET.Element) -> list[float] | None:
    """Docstring for _parse_trackpoint."""
    try:
        lat = float(elem.attrib[LAT_ATTR])
        lon = float(elem.attrib[LON_ATTR])
        return [lat, lon]
    except (KeyError, ValueError):
        return None


def parse_gpx_coordinates(filepath: str) -> list[list[float]]:
    """
    Parses a GPX file and extracts coordinates [lat, lon] from trackpoints (<trkpt>).
    """
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except Exception as e:
        print(f"Error parsing XML file {filepath}: {e}")
        return []

    coordinates = []
    for elem in root.iter():
        tag_local = elem.tag.split("}")[-1]
        if tag_local == XML_TRKPT_TAG:
            pt = _parse_trackpoint(elem)
            if pt:
                coordinates.append(pt)
            else:
                print(f"Skipping invalid trackpoint in {filepath}")

    return coordinates


def _process_gpx_file(filepath: str) -> tuple[str, dict[str, Any]] | None:
    """Docstring for _process_gpx_file."""
    filename = os.path.basename(filepath)
    code = os.path.splitext(filename)[0]
    if code not in REGION_NAMES:
        print(f"Skipping unknown region code/file: {filename}")
        return None
    coords = parse_gpx_coordinates(filepath)
    if not coords:
        print(f"Warning: No coordinates found in {filename}")
        return None
    return code, {"name": REGION_NAMES[code], "coordinates": coords}


def update_boundaries(gpx_dir: str, output_path: str) -> None:
    """Docstring for update_boundaries."""
    if not os.path.isdir(gpx_dir):
        print(f"Error: GPX directory does not exist at: {gpx_dir}")
        return
    gpx_files = sorted(glob.glob(os.path.join(gpx_dir, "*.gpx")))
    if not gpx_files:
        print(f"No GPX files found in: {gpx_dir}")
        return

    new_data: dict[str, Any] = {}
    for filepath in gpx_files:
        res = _process_gpx_file(filepath)
        if res:
            code, val = res
            new_data[code] = val
            print(
                f"Processed {code} ({val['name']}): {len(val['coordinates'])} coordinates"
            )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(new_data, f, indent=JSON_INDENT)


def main() -> None:
    """Docstring for main."""
    update_boundaries(GPX_DIR, OUTPUT_JSON_PATH)


if __name__ == "__main__":
    main()
