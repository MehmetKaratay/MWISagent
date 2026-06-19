#!/usr/bin/env /usr/bin/python3
import json

def debug():
    path = '/home/karatay/Repositories/learning/ai/mwis_agent/.agents/skills/mwis-website/identify_forecast_area/assets/mwis-region-boundaries.json'
    with open(path) as f:
        data = json.load(f)
        
    peaks = {
        "Ben Nevis": (56.7969, -5.0036, "WH"),
        "Snowdon": (53.0685, -4.0763, "SD"),
        "Scafell Pike": (54.4542, -3.2116, "LD"),
        "Pen y Fan": (51.8839, -3.4294, "BB"),
        "Cairn Gorm": (57.1162, -3.6428, "EH"),
        "Broad Law": (55.4981, -3.3503, "SU"),
        "Carn Eige": (57.2803, -5.1231, "NW")
    }
    
    for name, (lat, lon, code) in peaks.items():
        poly = data[code]["coordinates"]
        lats = [p[0] for p in poly]
        lons = [p[1] for p in poly]
        print(f"\n{name} (Target: {code}): Peak=({lat}, {lon})")
        print(f"  Lat bounds: {min(lats):.4f} to {max(lats):.4f}")
        print(f"  Lon bounds: {min(lons):.4f} to {max(lons):.4f}")

if __name__ == '__main__':
    debug()
