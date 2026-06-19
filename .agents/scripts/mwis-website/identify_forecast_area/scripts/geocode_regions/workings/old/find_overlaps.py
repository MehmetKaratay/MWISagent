#!/usr/bin/env /usr/bin/python3
import numpy as np
from PIL import Image

def find_overlap_colors():
    img_path = '/home/karatay/Repositories/learning/ai/mwis_agent/.agents/skills/mwis-website/identify_forecast_area/assets/mwis-map.jpg'
    img = Image.open(img_path)
    arr = np.array(img)
    
    # We will sample colors at several key locations:
    # 1. Ben Nevis: (743, 499) -> known to be in WH, currently cyan/SH color
    # 2. Ben Alder: (795, 460) -> overlap of EH and WH?
    # 3. Blair Atholl: (850, 480) -> SH?
    # 4. Aviemore: (890, 390) -> EH?
    # 5. Fort William: (740, 480) -> WH?
    # 6. Tyndrum: (750, 570) -> WH?
    # 7. Pitlochry: (860, 520) -> SH?
    
    locations = {
        "Ben Nevis": (743, 499),
        "Ben Alder": (795, 460),
        "Blair Atholl": (850, 480),
        "Aviemore": (890, 390),
        "Fort William": (740, 480),
        "Tyndrum": (750, 570),
        "Pitlochry": (860, 520)
    }
    
    hsv_img = img.convert('HSV')
    hsv = np.array(hsv_img)
    
    for name, (cx, cy) in locations.items():
        patch = arr[cy-1:cy+2, cx-1:cx+2]
        mean_rgb = np.mean(patch, axis=(0,1))
        h = hsv[cy, cx]
        print(f"{name:15s} at ({cx}, {cy}): RGB={mean_rgb.astype(int).tolist()} HSV={h.tolist()}")

if __name__ == '__main__':
    find_overlap_colors()
