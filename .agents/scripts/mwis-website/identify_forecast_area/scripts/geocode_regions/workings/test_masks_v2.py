#!/usr/bin/env /usr/bin/python3
import numpy as np
from PIL import Image

def test_masks_v2():
    img_path = '/home/karatay/Repositories/learning/ai/mwis_agent/.agents/skills/mwis-website/identify_forecast_area/assets/mwis-map.jpg'
    img = Image.open(img_path)
    arr = np.array(img)
    
    R, G, B = arr[:,:,0], arr[:,:,1], arr[:,:,2]
    # Identify the sea color exactly: RGB=[203, 232, 246]
    is_sea = (R == 203) & (G == 232) & (B == 246)
    
    hsv_img = img.convert('HSV')
    hsv = np.array(hsv_img)
    H, S, V = hsv[:,:,0], hsv[:,:,1], hsv[:,:,2]
    
    # We define the ranges, allowing wrap-around for H (0-255 range in PIL)
    # PIL Hue: 0-255 corresponds to 0-360 degrees.
    # Red is around 0 / 255.
    regions_settings = {
        "NW": {"h_func": lambda h: (h >= 200) & (h <= 225), "s": (50, 120), "v": (180, 255)},
        "EH": {"h_func": lambda h: (h >= 132) & (h <= 150), "s": (50, 100), "v": (180, 255)}, # Saturation min 50 to avoid any sea leakage
        "WH": {"h_func": lambda h: (h >= 0) & (h <= 15), "s": (40, 90), "v": (180, 255)},
        "SH": {"h_func": lambda h: (h >= 120) & (h <= 133), "s": (50, 110), "v": (180, 255)},
        "SU": {"h_func": lambda h: (h >= 50) & (h <= 65), "s": (70, 140), "v": (180, 255)},
        "LD": {"h_func": lambda h: (h >= 240) | (h <= 10), "s": (70, 140), "v": (180, 255)}, # Red wrap-around
        "YD": {"h_func": lambda h: (h >= 15) & (h <= 27), "s": (70, 140), "v": (180, 255)},
        "PD": {"h_func": lambda h: (h >= 28) & (h <= 42), "s": (70, 140), "v": (180, 255)},
        "SD": {"h_func": lambda h: (h >= 80) & (h <= 110), "s": (70, 140), "v": (180, 255)},
        "BB": {"h_func": lambda h: (h >= 45) & (h <= 59), "s": (70, 140), "v": (180, 255)}
    }
    
    for name, setts in regions_settings.items():
        mask = setts["h_func"](H) & \
               (S >= setts["s"][0]) & (S <= setts["s"][1]) & \
               (V >= setts["v"][0]) & (V <= setts["v"][1]) & \
               ~is_sea
        print(f"Mask {name:2s}: count={np.sum(mask)}")

if __name__ == '__main__':
    test_masks_v2()
