#!/usr/bin/env /usr/bin/python3
import json

def point_in_polygon(lat, lon, polygon):
    n = len(polygon)
    inside = False
    p1y, p1x = polygon[0] # lat, lon
    print(f"Point: ({lat}, {lon})")
    for i in range(n + 1):
        p2y, p2x = polygon[i % n]
        if min(p1y, p2y) < lat <= max(p1y, p2y):
            # Calculate intersection
            if p1y != p2y:
                xints = (lat - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
            else:
                xints = p1x
            is_intersect = (lon <= xints)
            print(f"  Edge {i}: ({p1y:.3f}, {p1x:.3f}) -> ({p2y:.3f}, {p2x:.3f}) | xints={xints:.3f} | intersect={is_intersect}")
            if is_intersect:
                inside = not inside
        p1y, p1x = p2y, p2x
    return inside

def main():
    path = '/home/karatay/Repositories/learning/ai/mwis_agent/.agents/skills/mwis-website/identify_forecast_area/assets/mwis-region-boundaries.json'
    with open(path) as f:
        data = json.load(f)
        
    poly = data["WH"]["coordinates"]
    inside = point_in_polygon(56.7969, -5.0036, poly)
    print("Result:", inside)

if __name__ == '__main__':
    main()
