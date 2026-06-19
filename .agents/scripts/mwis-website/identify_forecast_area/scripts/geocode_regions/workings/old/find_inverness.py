#!/usr/bin/env /usr/bin/python3
import numpy as np
from PIL import Image

def find_inverness_dark_loop():
    img_path = '/home/karatay/Repositories/learning/ai/mwis_agent/.agents/skills/mwis-website/identify_forecast_area/assets/mwis-map.jpg'
    img = Image.open(img_path)
    arr = np.array(img)
    
    # Inverness is around x=870 to 890, y=305 to 320
    # Let's search in x from 865 to 895, y from 300 to 330
    patch = arr[300:330, 865:895]
    
    # Find dark pixels (R < 100, G < 100, B < 100)
    r, g, b = patch[:,:,0], patch[:,:,1], patch[:,:,2]
    dark_mask = (r < 100) & (g < 100) & (b < 100)
    
    # Print the coordinates of dark pixels relative to the image
    ys, xs = np.where(dark_mask)
    for y, x in zip(ys, xs):
        gx = 865 + x
        gy = 300 + y
        print(f"Dark pixel: x={gx}, y={gy}, val={patch[y, x].tolist()}")

if __name__ == '__main__':
    find_inverness_dark_loop()
