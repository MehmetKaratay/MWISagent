#!/usr/bin/env /usr/bin/python3
import numpy as np
from PIL import Image

def analyze_patch(name, center_x, center_y):
    img_path = '/home/karatay/Repositories/learning/ai/mwis_agent/.agents/skills/mwis-website/identify_forecast_area/assets/mwis-map.jpg'
    img = Image.open(img_path)
    arr = np.array(img)
    
    # We crop a 20x20 patch around the center
    x0, x1 = int(center_x) - 10, int(center_x) + 10
    y0, y1 = int(center_y) - 10, int(center_y) + 10
    patch = arr[y0:y1, x0:x1]
    
    print(f"\n--- {name} Patch (x: {x0} to {x1}, y: {y0} to {y1}) ---")
    # Let's find the circle. The dot is a yellow circle with a black border.
    # The yellow circle has high R and G (e.g., >200), and lower B (e.g., <150).
    # The black border has very low R, G, B (e.g., <50).
    # Let's print the R, G, B values of the patch to see where the yellow circle is.
    # We can print a map of (R+G)/2 - B to highlight the yellow-green color.
    yellow_intensity = (patch[:,:,0].astype(float) + patch[:,:,1].astype(float)) / 2.0 - patch[:,:,2].astype(float)
    
    # Let's find the contiguous region with yellow_intensity > 80 and print its center.
    mask = yellow_intensity > 80
    ys, xs = np.where(mask)
    if len(xs) > 0:
        cx = x0 + np.mean(xs)
        cy = y0 + np.mean(ys)
        print(f"Yellow centroid: x={cx:.2f}, y={cy:.2f}, count={len(xs)}")
    else:
        print("No yellow centroid found")
        
    # Let's find the darkest ring/circle boundary around it
    # Print the coordinates of pixels with low intensity (black border)
    gray = np.mean(patch, axis=2)
    min_y, min_x = np.unravel_index(np.argmin(gray), gray.shape)
    print(f"Darkest pixel: x={x0 + min_x}, y={y0 + min_y}, val={gray[min_y, min_x]:.1f}")

def main():
    # Let's check Inverness, Aberdeen, Glasgow, Edinburgh, Newcastle, Carlisle
    analyze_patch("Inverness", 870, 310)
    analyze_patch("Aberdeen", 1020, 370)
    analyze_patch("Glasgow", 730, 710)
    analyze_patch("Edinburgh", 880, 650)
    analyze_patch("Newcastle", 995, 860)
    analyze_patch("Carlisle", 890, 890)
    analyze_patch("Aberystwyth", 740, 1420)
    analyze_patch("Cardiff", 867, 1636)
    analyze_patch("London", 1290, 1635)

if __name__ == '__main__':
    main()
