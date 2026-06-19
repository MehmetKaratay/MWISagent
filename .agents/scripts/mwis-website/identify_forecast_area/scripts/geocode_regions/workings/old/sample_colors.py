#!/usr/bin/env /usr/bin/python3
import numpy as np
from PIL import Image

def sample_colors():
    img_path = '/home/karatay/Repositories/learning/ai/mwis_agent/.agents/skills/mwis-website/identify_forecast_area/assets/mwis-map.jpg'
    img = Image.open(img_path)
    arr = np.array(img)
    
    centers = {
        "NW": (680, 180),
        "EH": (840, 240),
        "WH": (620, 360),
        "SH": (800, 320),
        "SU": (820, 480),
        "LD": (880, 600),
        "YD": (1000, 600),
        "PD": (1020, 750),
        "SD": (750, 810),
        "BB": (780, 930)
    }
    
    # Wait, let's scale the centers.
    # In my previous coordinate calculations, Glasgow was at y=692, Carlisle at y=906, Cardiff at y=1613.
    # So the image y-axis goes from 0 to 1643.
    # Let's adjust the center coordinates for the 1643x1643 image:
    # NW: y ~ 200, x ~ 700
    # EH: y ~ 250, x ~ 850
    # WH: y ~ 450, x ~ 650
    # SH: y ~ 500, x ~ 800
    # SU: y ~ 750, x ~ 820
    # LD: y ~ 1000, x ~ 880
    # YD: y ~ 1020, x ~ 1000
    # PD: y ~ 1250, x ~ 1020
    # SD: y ~ 1350, x ~ 750
    # BB: y ~ 1550, x ~ 780
    centers_scaled = {
        "NW": (700, 200),
        "EH": (850, 250),
        "WH": (650, 450),
        "SH": (800, 500),
        "SU": (820, 750),
        "LD": (880, 1000),
        "YD": (1000, 1020),
        "PD": (1020, 1250),
        "SD": (750, 1350),
        "BB": (780, 1550)
    }
    
    for name, (cx, cy) in centers_scaled.items():
        # Sample 5x5 average
        patch = arr[cy-2:cy+3, cx-2:cx+3]
        mean_rgb = np.mean(patch, axis=(0,1))
        # Convert to HSV to see Hue easily
        # PIL can convert a 1x1 image
        tmp_img = Image.new('RGB', (1, 1), color=tuple(mean_rgb.astype(int)))
        hsv = tmp_img.convert('HSV').getpixel((0,0))
        print(f"{name:2s} at ({cx}, {cy}): RGB={mean_rgb.astype(int).tolist()} HSV={list(hsv)}")

if __name__ == '__main__':
    sample_colors()
