#!/usr/bin/env python3
"""
Utility script to parse GPX boundary trackpoints and regenerate the MWIS region boundaries JSON file.
"""
import os
import json
import glob
import xml.etree.ElementTree as ET

# Path Configuration relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GPX_DIR = os.path.join(SCRIPT_DIR, '..', 'resources', 'gpx_files', 'mwis_areas')
OUTPUT_JSON_PATH = os.path.join(SCRIPT_DIR, '..', 'assets', 'mwis-region-boundaries.json')

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
    "BB": "Brecon Beacons"
}

def parse_gpx_coordinates(filepath):
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
    # Use iter to search for 'trkpt' elements regardless of XML namespace prefix
    for elem in root.iter():
        tag_local = elem.tag.split('}')[-1]
        if tag_local == 'trkpt':
            try:
                lat = float(elem.attrib['lat'])
                lon = float(elem.attrib['lon'])
                coordinates.append([lat, lon])
            except (KeyError, ValueError) as e:
                print(f"Skipping invalid trackpoint in {filepath}: {e}")
                
    return coordinates

def main():
    if not os.path.isdir(GPX_DIR):
        print(f"Error: GPX directory does not exist at: {GPX_DIR}")
        return
        
    gpx_files = glob.glob(os.path.join(GPX_DIR, "*.gpx"))
    if not gpx_files:
        print(f"No GPX files found in: {GPX_DIR}")
        return
        
    new_data = {}
    for filepath in sorted(gpx_files):
        filename = os.path.basename(filepath)
        code = os.path.splitext(filename)[0]
        
        if code not in REGION_NAMES:
            print(f"Skipping unknown region code/file: {filename}")
            continue
            
        coords = parse_gpx_coordinates(filepath)
        if not coords:
            print(f"Warning: No coordinates found in {filename}")
            continue
            
        new_data[code] = {
            "name": REGION_NAMES[code],
            "coordinates": coords
        }
        print(f"Processed {code} ({REGION_NAMES[code]}): {len(coords)} coordinates")
        
    # Write updated boundaries to assets directory
    os.makedirs(os.path.dirname(OUTPUT_JSON_PATH), exist_ok=True)
    with open(OUTPUT_JSON_PATH, 'w') as f:
        json.dump(new_data, f, indent=2)
        
    print(f"Successfully updated boundaries JSON at: {OUTPUT_JSON_PATH}")

if __name__ == "__main__":
    main()
