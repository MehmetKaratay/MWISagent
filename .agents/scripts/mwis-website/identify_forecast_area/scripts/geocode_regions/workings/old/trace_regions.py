#!/usr/bin/env /usr/bin/python3
import numpy as np
from PIL import Image
import json

def trace_region_boundary(arr, name, cx, cy, h_range, s_range, v_range):
    # Convert image to HSV
    # PIL HSV conversion: H is 0-255, S is 0-255, V is 0-255
    hsv_img = Image.fromarray(arr).convert('HSV')
    hsv = np.array(hsv_img)
    
    H = hsv[:,:,0]
    S = hsv[:,:,1]
    V = hsv[:,:,2]
    
    # Create mask
    mask = (H >= h_range[0]) & (H <= h_range[1]) & \
           (S >= s_range[0]) & (S <= s_range[1]) & \
           (V >= v_range[0]) & (V <= v_range[1])
           
    # Smooth the mask to fill in text and lines
    # We can do a simple box filter using a 2D convolution
    # Create a 15x15 kernel of ones
    kernel_size = 15
    smoothed = np.zeros_like(mask, dtype=float)
    # Simple fast box blur in numpy:
    # We can use cumulative sum to do it very fast
    cumsum = np.cumsum(np.cumsum(mask.astype(float), axis=0), axis=1)
    
    # Box filter using cumsum
    k = kernel_size // 2
    h, w = mask.shape
    for y in range(k, h - k):
        for x in range(k, w - k):
            total = cumsum[y+k, x+k] - cumsum[y-k-1, x+k] - cumsum[y+k, x-k-1] + cumsum[y-k-1, x-k-1]
            smoothed[y, x] = total / (kernel_size * kernel_size)
            
    # Threshold smoothed mask at 0.1 to get filled mask
    filled_mask = smoothed > 0.1
    
    # Ray-casting from center (cx, cy)
    # We will cast rays in 36 directions (every 10 degrees)
    # and find the boundary of the filled mask.
    polygon = []
    num_rays = 48
    angles = np.linspace(0, 2*np.pi, num_rays, endpoint=False)
    
    for angle in angles:
        dx = np.cos(angle)
        dy = np.sin(angle)
        
        # Walk along the ray from center outward
        farthest_x, farthest_y = cx, cy
        for r in range(1, 1000): # Ray radius up to 1000 pixels
            rx = int(cx + r * dx)
            ry = int(cy + r * dy)
            if rx < 0 or rx >= w or ry < 0 or ry >= h:
                break
            if filled_mask[ry, rx]:
                farthest_x, farthest_y = rx, ry
            else:
                # If we hit non-mask, let's keep walking a bit to see if we re-enter (fills small gaps)
                re_enter = False
                for check_r in range(r + 1, r + 15):
                    cx_check = int(cx + check_r * dx)
                    cy_check = int(cy + check_r * dy)
                    if 0 <= cx_check < w and 0 <= cy_check < h:
                        if filled_mask[cy_check, cx_check]:
                            re_enter = True
                            break
                if not re_enter:
                    break
        polygon.append((farthest_x, farthest_y))
        
    return polygon

def main():
    img_path = '/home/karatay/Repositories/learning/ai/mwis_agent/.agents/skills/mwis-website/identify_forecast_area/assets/mwis-map.jpg'
    img = Image.open(img_path)
    arr = np.array(img)
    
    # Define ranges for H, S, V based on our sampled centers:
    # NW: [213, 85, 249] -> H around 200-225, S around 60-120, V around 200-255
    # EH: [139, 65, 243] -> H around 125-150, S around 40-90, V around 200-255
    # WH: [8, 59, 236]   -> H around 0-20 or 240-255 (due to wrap-around), S around 40-90, V around 200-255
    # SH: [130, 78, 243] -> H around 115-140, S around 50-100, V around 200-255
    # SU: [57, 105, 245] -> H around 45-70, S around 70-130, V around 200-255
    # LD: [0, 104, 251]   -> H around 245-255 or 0-10, S around 70-130, V around 200-255
    # YD: [22, 108, 245]  -> H around 15-30, S around 70-130, V around 200-255
    # PD: [35, 113, 229]  -> H around 28-42, S around 70-130, V around 200-255
    # SD: [95, 92, 234]   -> H around 80-110, S around 70-130, V around 200-255
    # BB: [55, 101, 252]  -> H around 45-65, S around 70-130, V around 200-255
    
    # For H wrap-around (like WH/LD which are close to 0/255), we can specify dual ranges or broad range.
    # Note: PIL HSV Hue is mapped to [0, 255].
    # So Red Hue is around 0 or 255.
    
    regions_settings = {
        "NW": {
            "center": (700, 200),
            "h": (200, 225), "s": (50, 120), "v": (180, 255)
        },
        "EH": {
            "center": (850, 250),
            "h": (132, 150), "s": (40, 100), "v": (180, 255)
        },
        "WH": {
            # Peach/orange: Hue around 0 to 15
            "center": (650, 450),
            "h": (0, 15), "s": (40, 90), "v": (180, 255)
        },
        "SH": {
            "center": (800, 500),
            "h": (120, 133), "s": (50, 110), "v": (180, 255)
        },
        "SU": {
            "center": (820, 750),
            "h": (50, 62), "s": (70, 140), "v": (180, 255)
        },
        "LD": {
            # Red: Hue around 245 to 255
            "center": (880, 1000),
            "h": (240, 255), "s": (70, 140), "v": (180, 255)
        },
        "YD": {
            "center": (1000, 1020),
            "h": (16, 26), "s": (70, 140), "v": (180, 255)
        },
        "PD": {
            "center": (1020, 1250),
            "h": (28, 42), "s": (70, 140), "v": (180, 255)
        },
        "SD": {
            "center": (750, 1350),
            "h": (80, 110), "s": (70, 140), "v": (180, 255)
        },
        "BB": {
            "center": (780, 1550),
            "h": (45, 59), "s": (70, 140), "v": (180, 255)
        }
    }
    
    for name, setts in regions_settings.items():
        poly = trace_region_boundary(arr, name, setts["center"][0], setts["center"][1],
                                     setts["h"], setts["s"], setts["v"])
        print(f"Traced {name}: polygon with {len(poly)} points. Center=({setts['center'][0]}, {setts['center'][1]})")

if __name__ == '__main__':
    main()
