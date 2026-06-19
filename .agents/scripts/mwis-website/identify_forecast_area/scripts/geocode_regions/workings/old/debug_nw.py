#!/usr/bin/env /usr/bin/python3
import json

def point_in_polygon(lat, lon, polygon):
    n = len(polygon)
    inside = False
    p1y, p1x = polygon[0] # lat, lon
    for i in range(n + 1):
        p2y, p2x = polygon[i % n]
        if min(p1y, p2y) < lat <= max(p1y, p2y):
            if p1y != p2y:
                xints = (lat - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
            else:
                xints = p1x
            if lon <= xints:
                inside = not inside
        p1y, p1x = p2y, p2x
    return inside

def main():
    path = '/home/karatay/Repositories/learning/ai/mwis_agent/.agents/skills/mwis-website/identify_forecast_area/assets/mwis-region-boundaries.json'
    with open(path) as f:
        data = json.load(f)
        
    poly = data["NW"]["coordinates"]
    inside = point_in_polygon(57.2803, -5.1231, poly)
    print("Carn Eige inside NW:", inside)
    
    # Let's print the vertices of NW to see what they are
    for i, p in enumerate(poly[:10]):
        print(f"Vertex {i}: lat={p[0]:.4f}, lon={p[1]:.4f}")

if __name__ == '__main__':
    main()
