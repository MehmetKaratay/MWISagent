#!/usr/bin/env /usr/bin/python3
import numpy as np
from PIL import Image

def find_all_dots():
    img_path = '/home/karatay/Repositories/learning/ai/mwis_agent/.agents/skills/mwis-website/identify_forecast_area/assets/mwis-map.jpg'
    img = Image.open(img_path)
    arr = np.array(img)
    h, w, c = arr.shape
    
    # Let's search for the yellow/green dots.
    # The dot has a yellow-green color. Let's see what is the color of the dot.
    # We saw Cardiff is at x=867, y=1636. Let's print the RGB values in a 5x5 window around it.
    print("Cardiff pixel colors at x=865-869, y=1634-1638:")
    for y in range(1634, 1639):
        row = [arr[y, x].tolist() for x in range(865, 870)]
        print(f"y={y}: {row}")
        
    # Let's see Edinburgh at x=879, y=650:
    print("\nEdinburgh pixel colors at x=877-881, y=648-652:")
    for y in range(648, 653):
        row = [arr[y, x].tolist() for x in range(877, 882)]
        print(f"y={y}: {row}")

if __name__ == '__main__':
    find_all_dots()
