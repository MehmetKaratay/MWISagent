#!/usr/bin/env /usr/bin/python3
import numpy as np
from PIL import Image

def test_masks():
    img_path = '/home/karatay/Repositories/learning/ai/mwis_agent/.agents/skills/mwis-website/identify_forecast_area/assets/mwis-map.jpg'
    img = Image.open(img_path)
    arr = np.array(img)
    
    hsv_img = img.convert('HSV')
    hsv = np.array(hsv_img)
    H, S, V = hsv[:,:,0], hsv[:,:,1], hsv[:,:,2]
    
    # Let's check the settings:
    regions_settings = {
        "NW": {"h": (200, 225), "s": (50, 120), "v": (180, 255)},
        "EH": {"h": (132, 150), "s": (40, 100), "v": (180, 255)},
        "WH": {"h": (0, 15), "s": (40, 90), "v": (180, 255)},
        "SH": {"h": (120, 133), "s": (50, 110), "v": (180, 255)},
        "SU": {"h": (50, 62), "s": (70, 140), "v": (180, 255)},
        "LD": {"h": (240, 255), "s": (70, 140), "v": (180, 255)},
        "YD": {"h": (16, 26), "s": (70, 140), "v": (180, 255)},
        "PD": {"h": (28, 42), "s": (70, 140), "v": (180, 255)},
        "SD": {"h": (80, 110), "s": (70, 140), "v": (180, 255)},
        "BB": {"h": (45, 59), "s": (70, 140), "v": (180, 255)}
    }
    
    for name, setts in regions_settings.items():
        mask = (H >= setts["h"][0]) & (H <= setts["h"][1]) & \
               (S >= setts["s"][0]) & (S <= setts["s"][1]) & \
               (V >= setts["v"][0]) & (V <= setts["v"][1])
        print(f"Mask {name:2s}: count={np.sum(mask)}")

if __name__ == '__main__':
    test_masks()
