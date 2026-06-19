#!/usr/bin/env /usr/bin/python3
import numpy as np
from PIL import Image

def debug_peak(name, target_code, px, py, mask):
    print(f"\n=== Debug {name} ({target_code}) around ({px}, {py}) ===")
    h, w = mask.shape
    x0, x1 = max(0, px - 10), min(w, px + 10)
    y0, y1 = max(0, py - 10), min(h, py + 10)
    sub = mask[y0:y1, x0:x1]
    
    # Print the submask grid: '1' for inside mask, '0' for outside
    for r in range(sub.shape[0]):
        row = ["1" if sub[r, c] else "0" for c in range(sub.shape[1])]
        # Highlight center
        if y0 + r == py:
            row[px - x0] = "[" + row[px - x0] + "]"
        else:
            row[px - x0] = " " + row[px - x0] + " "
        print(" ".join(row))

def main():
    img_path = '/home/karatay/Repositories/learning/ai/mwis_agent/.agents/skills/mwis-website/identify_forecast_area/assets/mwis-map.jpg'
    img = Image.open(img_path)
    arr = np.array(img)
    h, w, c = arr.shape
    
    hsv_img = img.convert('HSV')
    hsv = np.array(hsv_img)
    H, S, V = hsv[:,:,0], hsv[:,:,1], hsv[:,:,2]
    
    R, G, B = arr[:,:,0], arr[:,:,1], arr[:,:,2]
    is_sea = (R == 203) & (G == 232) & (B == 246)
    
    # Create the smoothed filled masks exactly as in test_masks_v3:
    y_grid, x_grid = np.mgrid[0:h, 0:w]
    
    mask_nw = (H >= 190) & (H <= 235) & (S >= 50) & (S <= 120) & ~is_sea
    mask_eh = ((H >= 130) & (H <= 190) & (S >= 40) & (S <= 120) & ~is_sea) & (x_grid >= 740) & (y_grid <= 480)
    mask_ld = ((H >= 240) | (H <= 10)) & (S >= 70) & (S <= 140) & ~is_sea

    # Smooth them
    def smooth(mask):
        kernel_size = 15
        smoothed = np.zeros_like(mask, dtype=float)
        cumsum = np.cumsum(np.cumsum(mask.astype(float), axis=0), axis=1)
        k = kernel_size // 2
        for y in range(k, h - k):
            for x in range(k, w - k):
                total = cumsum[y+k, x+k] - cumsum[y-k-1, x+k] - cumsum[y+k, x-k-1] + cumsum[y-k-1, x-k-1]
                smoothed[y, x] = total / (kernel_size * kernel_size)
        return smoothed > 0.1

    print("Smoothing masks...")
    filled_nw = smooth(mask_nw)
    filled_eh = smooth(mask_eh)
    filled_ld = smooth(mask_ld)
    
    debug_peak("Carn Eige", "NW", 767, 388, filled_nw)
    debug_peak("Cairn Gorm", "EH", 897, 401, filled_eh)
    debug_peak("Scafell Pike", "LD", 832, 998, filled_ld)

if __name__ == '__main__':
    main()
