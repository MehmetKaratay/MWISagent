#!/usr/bin/env /usr/bin/python3
import numpy as np
from PIL import Image

def sample_sea():
    img_path = '/home/karatay/Repositories/learning/ai/mwis_agent/.agents/skills/mwis-website/identify_forecast_area/assets/mwis-map.jpg'
    img = Image.open(img_path)
    # Convert a patch in the sea to HSV
    arr = np.array(img)
    # Let's check some coordinate in the sea, e.g. x=200, y=200 (top-left)
    # or x=1500, y=500 (middle-right)
    hsv_img = img.convert('HSV')
    hsv = np.array(hsv_img)
    
    for x, y in [(200, 200), (1500, 500)]:
        print(f"Sea at ({x}, {y}): RGB={arr[y,x].tolist()} HSV={hsv[y,x].tolist()}")
        
    # Let's also check the land background (e.g. near London but not on the text or dot, say x=1200, y=1500)
    print(f"Land at (1200, 1500): RGB={arr[1500,1200].tolist()} HSV={hsv[1500,1200].tolist()}")

if __name__ == '__main__':
    sample_sea()
