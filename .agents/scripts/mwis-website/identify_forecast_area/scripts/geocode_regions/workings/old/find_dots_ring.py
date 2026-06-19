#!/usr/bin/env /usr/bin/python3
import numpy as np
from PIL import Image

def find_dot_by_ring(name, approx_x, approx_y):
    img_path = '/home/karatay/Repositories/learning/ai/mwis_agent/.agents/skills/mwis-website/identify_forecast_area/assets/mwis-map.jpg'
    img = Image.open(img_path)
    gray = np.array(img.convert('L'), dtype=float)
    h, w = gray.shape
    
    x0 = max(0, int(approx_x) - 30)
    x1 = min(w, int(approx_x) + 30)
    y0 = max(0, int(approx_y) - 30)
    y1 = min(h, int(approx_y) + 30)
    
    best_score = -1e9
    best_x, best_y = 0, 0
    
    # Inside: r <= 4
    inside_offsets = []
    for dy in range(-4, 5):
        for dx in range(-4, 5):
            if dy*dy + dx*dx <= 16:
                inside_offsets.append((dy, dx))
                
    # Ring: 5 <= r <= 7
    ring_offsets = []
    for dy in range(-7, 8):
        for dx in range(-7, 8):
            r2 = dy*dy + dx*dx
            if 25 <= r2 <= 49:
                ring_offsets.append((dy, dx))
                
    for y in range(y0 + 7, y1 - 7):
        for x in range(x0 + 7, x1 - 7):
            inside_val = np.mean([gray[y + dy, x + dx] for dy, dx in inside_offsets])
            ring_val = np.mean([gray[y + dy, x + dx] for dy, dx in ring_offsets])
            
            # Bright yellow/green center, dark border
            score = inside_val - ring_val
            
            if score > best_score:
                best_score = score
                best_x, best_y = x, y
                
    print(f"{name}: x={best_x}, y={best_y}, score={best_score:.1f}")

def main():
    approx_coords = {
        "Inverness": (870, 310),
        "Aberdeen": (1020, 380),
        "Dundee": (950, 530),
        "Stirling": (890, 610),
        "Glasgow": (730, 710),
        "Edinburgh": (880, 650),
        "Carlisle": (890, 890),
        "Newcastle": (995, 860),
        "Aberystwyth": (740, 1420),
        "Cardiff": (867, 1636),
        "London": (1290, 1635),
    }
    
    for name, (ax, ay) in approx_coords.items():
        find_dot_by_ring(name, ax, ay)

if __name__ == '__main__':
    main()
