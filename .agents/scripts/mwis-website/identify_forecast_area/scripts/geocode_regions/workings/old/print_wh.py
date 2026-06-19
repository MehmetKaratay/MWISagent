#!/usr/bin/env /usr/bin/python3
import json

def print_wh():
    path = '/home/karatay/Repositories/learning/ai/mwis_agent/.agents/skills/mwis-website/identify_forecast_area/assets/mwis-region-boundaries.json'
    with open(path) as f:
        data = json.load(f)
    poly = data["WH"]["coordinates"]
    for i, p in enumerate(poly):
        print(f"Vertex {i}: lat={p[0]:.4f}, lon={p[1]:.4f}")

if __name__ == '__main__':
    print_wh()
