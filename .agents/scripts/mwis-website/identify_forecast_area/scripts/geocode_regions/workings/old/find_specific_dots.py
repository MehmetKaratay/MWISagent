#!/usr/bin/env /usr/bin/python3
import numpy as np
from PIL import Image

def analyze():
    img_path = '/home/karatay/Repositories/learning/ai/mwis_agent/.agents/skills/mwis-website/identify_forecast_area/assets/mwis-map.jpg'
    img = Image.open(img_path)
    arr = np.array(img)
    
    approx = {
        "Inverness": (870, 330),
        "Aberdeen": (1020, 370),
        "Glasgow": (730, 710),
        "Carlisle": (890, 890),
    }
    
    for name, (ax, ay) in approx.items():
        print(f"\n--- {name} ---")
        # Let's inspect a 40x40 patch and find the dot.
        # A city dot is a small circle, typically with a black/dark border and a green/yellow/light center.
        # Let's search for a green-ish or yellow-ish color.
        # Let's print pixels in the patch that are green/yellow.
        x0, x1 = ax-30, ax+30
        y0, y1 = ay-30, ay+30
        patch = arr[y0:y1, x0:x1]
        
        # Let's find all pixels in the patch where R and G are high, B is lower.
        # Let's print the RGB values of pixels with G > 180 and R > 150.
        # If there are none, let's look for G > 150 and R > 130.
        r, g, b = patch[:,:,0], patch[:,:,1], patch[:,:,2]
        mask = (g > 180) & (r > 150)
        
        ys, xs = np.where(mask)
        if len(xs) > 0:
            cx = ax - 30 + np.mean(xs)
            cy = ay - 30 + np.mean(ys)
            print(f"Found with primary mask: x={cx:.2f}, y={cy:.2f}, count={len(xs)}")
        else:
            # Let's try a softer mask: g > 150, r > 130, b < 150
            mask2 = (g > 150) & (r > 130) & (b < 150)
            ys2, xs2 = np.where(mask2)
            if len(xs2) > 0:
                cx = ax - 30 + np.mean(xs2)
                cy = ay - 30 + np.mean(ys2)
                print(f"Found with soft mask: x={cx:.2f}, y={cy:.2f}, count={len(xs2)}")
            else:
                print("No dot found with either mask")

if __name__ == '__main__':
    analyze()
