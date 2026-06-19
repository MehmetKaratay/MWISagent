#!/usr/bin/env /usr/bin/python3
import numpy as np
from PIL import Image

def dump_grid(name, approx_x, approx_y, size=15):
    img_path = '/home/karatay/Repositories/learning/ai/mwis_agent/.agents/skills/mwis-website/identify_forecast_area/assets/mwis-map.jpg'
    img = Image.open(img_path)
    arr = np.array(img)
    
    # We want to dump a square grid around approx_x, approx_y
    # to find the exact circle (marked by a dark border and light center)
    x0 = int(approx_x) - size // 2
    y0 = int(approx_y) - size // 2
    
    print(f"\n=== {name} (Offset x={x0}, y={y0}) ===")
    for y in range(size):
        row_str = []
        for x in range(size):
            r, g, b = arr[y0 + y, x0 + x]
            # Print as a compact representation:
            # If it's a dark border (r, g, b < 100), print 'XX'
            # If it's the light center (r, g > 180), print '@@'
            # Else print '..'
            if r < 100 and g < 100 and b < 100:
                row_str.append("XX")
            elif r > 180 and g > 180:
                row_str.append("@@")
            else:
                row_str.append("..")
        print(" ".join(row_str))

def main():
    dump_grid("Inverness", 883, 312)
    dump_grid("Aberdeen", 1020, 386)
    dump_grid("Carlisle", 907, 906)

if __name__ == '__main__':
    main()
