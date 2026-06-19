#!/usr/bin/env /usr/bin/python3
import numpy as np
from PIL import Image

def find_yellow_dot(name, ax, ay):
    img_path = '/home/karatay/Repositories/learning/ai/mwis_agent/.agents/skills/mwis-website/identify_forecast_area/assets/mwis-map.jpg'
    img = Image.open(img_path)
    arr = np.array(img)
    
    # We will search in a 100x100 box around ax, ay
    x0, x1 = max(0, ax-50), min(arr.shape[1], ax+50)
    y0, y1 = max(0, ay-50), min(arr.shape[0], ay+50)
    
    patch = arr[y0:y1, x0:x1]
    
    # Let's find pixels that are yellow.
    # Yellow has high R (>180), high G (>180), and low B (<150).
    # Let's use a metric: R + G - 2*B
    r, g, b = patch[:,:,0].astype(float), patch[:,:,1].astype(float), patch[:,:,2].astype(float)
    metric = r + g - 2*b
    
    # Let's print the top 5 highest metric values and their coordinates in the patch
    flat_indices = np.argsort(metric.flat)[-200:]
    ys, xs = np.unravel_index(flat_indices, metric.shape)
    
    # Group these yellow pixels into connected components to find the dot centroid
    visited = set()
    yellow_pixels = set(zip(ys, xs))
    components = []
    for y, x in yellow_pixels:
        if (y, x) not in visited:
            # BFS
            comp = []
            queue = [(y, x)]
            visited.add((y, x))
            while queue:
                cy, cx = queue.pop(0)
                comp.append((cy, cx))
                for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
                    ny, nx = cy+dy, cx+dx
                    if 0 <= ny < metric.shape[0] and 0 <= nx < metric.shape[1]:
                        if (ny, nx) in yellow_pixels and (ny, nx) not in visited:
                            visited.add((ny, nx))
                            queue.append((ny, nx))
            components.append(comp)
            
    # Filter components by size (dots are typically 10 to 100 pixels in size)
    valid_dots = []
    for comp in components:
        if 5 <= len(comp) <= 150:
            avg_y = sum(p[0] for p in comp) / len(comp)
            avg_x = sum(p[1] for p in comp) / len(comp)
            # Check if this centroid is circular or has a dark border
            # Calculate the global coordinates
            gx = x0 + avg_x
            gy = y0 + avg_y
            valid_dots.append((gx, gy, len(comp)))
            
    print(f"\n--- {name} Candidates ---")
    for gx, gy, sz in valid_dots:
        print(f"Candidate: x={gx:.2f}, y={gy:.2f}, size={sz}")

def main():
    find_yellow_dot("Inverness", 870, 310)
    find_yellow_dot("Aberdeen", 1020, 370)
    find_yellow_dot("Glasgow", 730, 710)
    find_yellow_dot("Carlisle", 890, 890)

if __name__ == '__main__':
    main()
