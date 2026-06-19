#!/usr/bin/env /usr/bin/python3
import numpy as np
from PIL import Image

def calibrate():
    img_path = '/home/karatay/Repositories/learning/ai/mwis_agent/.agents/skills/mwis-website/identify_forecast_area/assets/mwis-map.jpg'
    img = Image.open(img_path)
    arr = np.array(img)
    
    # We will look in neighborhoods of approximate coordinates:
    approx = {
        "Inverness": (860, 340),
        "Aberdeen": (1020, 380),
        "Glasgow": (730, 690),
        "Edinburgh": (880, 650),
        "Newcastle": (995, 860),
        "Carlisle": (890, 890),
        "Aberystwyth": (740, 1420),
        "Cardiff": (867, 1636),
        "London": (1290, 1635)
    }
    
    for name, (ax, ay) in approx.items():
        # Crop 60x60 neighborhood
        x0, x1 = max(0, ax-30), min(arr.shape[1], ax+30)
        y0, y1 = max(0, ay-30), min(arr.shape[0], ay+30)
        sub = arr[y0:y1, x0:x1]
        
        # In this sub-image, look for the dot. The dot is a yellow-green circle.
        # Let's print the RGB values in a small window or find the pixel with max green-ness.
        # Let's find pixel with G > 180 and R > 150.
        # Let's calculate the centroid of such pixels in the neighborhood.
        r, g, b = sub[:,:,0], sub[:,:,1], sub[:,:,2]
        mask = (g > 180) & (r > 150) & (b < 120)
        
        ys, xs = np.where(mask)
        if len(xs) > 0:
            cx = x0 + np.mean(xs)
            cy = y0 + np.mean(ys)
            print(f"{name}: exact_x={cx:.2f}, exact_y={cy:.2f}, count={len(xs)}")
        else:
            # Let's find the pixel with the highest G/B ratio or something similar
            # that represents the green/yellow dot.
            # Let's print the max G value and its location.
            max_g_idx = np.unravel_index(np.argmax(g), g.shape)
            cx = x0 + max_g_idx[1]
            cy = y0 + max_g_idx[0]
            print(f"{name} (no mask): max_g_x={cx:.2f}, max_g_y={cy:.2f}, max_g={g[max_g_idx]}")

if __name__ == '__main__':
    calibrate()
