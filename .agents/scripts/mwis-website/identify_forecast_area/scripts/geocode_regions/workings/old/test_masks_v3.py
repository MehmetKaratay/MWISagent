#!/usr/bin/env /usr/bin/python3
import numpy as np
from PIL import Image

# Known GPS calibration points
CALIBRATION_GPS = {
    "Inverness": (57.4778, -4.2247),
    "Aberdeen": (57.1497, -2.0943),
    "Glasgow": (55.8642, -4.2518),
    "Edinburgh": (55.9533, -3.1883),
    "Carlisle": (54.8924, -2.9329),
    "Newcastle": (54.9783, -1.6178),
    "Aberystwyth": (52.4153, -4.0829),
    "Cardiff": (51.4816, -3.1791),
    "London": (51.5074, -0.1278)
}

CALIBRATION_PIXELS = {
    "Inverness": (890.0, 312.0),
    "Aberdeen": (1020.0, 386.0),
    "Glasgow": (732.6, 718.1),
    "Edinburgh": (879.3, 649.7),
    "Carlisle": (907.5, 906.5),
    "Newcastle": (991.9, 861.0),
    "Aberystwyth": (748.4, 1426.4),
    "Cardiff": (866.9, 1636.4),
    "London": (1290.5, 1635.1),
}

# Coordinate transformation setup
X_mat = []
lat_arr = []
lon_arr = []
for name in CALIBRATION_GPS:
    px, py = CALIBRATION_PIXELS[name]
    lat_val, lon_val = CALIBRATION_GPS[name]
    X_mat.append([1.0, px, py, px**2, py**2, px*py])
    lat_arr.append(lat_val)
    lon_arr.append(lon_val)

X_mat = np.array(X_mat)
coef_lat = np.linalg.lstsq(X_mat, np.array(lat_arr), rcond=None)[0]
coef_lon = np.linalg.lstsq(X_mat, np.array(lon_arr), rcond=None)[0]

def pixel_to_gps(px, py):
    terms = np.array([1.0, px, py, px**2, py**2, px*py])
    lat = float(np.dot(terms, coef_lat))
    lon = float(np.dot(terms, coef_lon))
    return lat, lon

def point_in_polygon(lat, lon, polygon):
    n = len(polygon)
    inside = False
    p1y, p1x = polygon[0] # lat, lon
    for i in range(n + 1):
        p2y, p2x = polygon[i % n]
        if min(p1y, p2y) < lat <= max(p1y, p2y):
            if lon <= max(p1x, p2x):
                if p1y != p2y:
                    xints = (lat - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                if p1x == p2x or lon <= xints:
                    inside = not inside
        p1y, p1x = p2y, p2x
    return inside

def trace_region(arr, cx, cy, mask):
    # Smooth mask using cumulative sum box filter
    kernel_size = 15
    smoothed = np.zeros_like(mask, dtype=float)
    cumsum = np.cumsum(np.cumsum(mask.astype(float), axis=0), axis=1)
    k = kernel_size // 2
    h, w = mask.shape
    for y in range(k, h - k):
        for x in range(k, w - k):
            total = cumsum[y+k, x+k] - cumsum[y-k-1, x+k] - cumsum[y+k, x-k-1] + cumsum[y-k-1, x-k-1]
            smoothed[y, x] = total / (kernel_size * kernel_size)
            
    filled_mask = smoothed > 0.1
    
    polygon = []
    num_rays = 48
    angles = np.linspace(0, 2*np.pi, num_rays, endpoint=False)
    for angle in angles:
        dx = np.cos(angle)
        dy = np.sin(angle)
        farthest_x, farthest_y = cx, cy
        for r in range(1, 1000):
            rx = int(cx + r * dx)
            ry = int(cy + r * dy)
            if rx < 0 or rx >= w or ry < 0 or ry >= h:
                break
            if filled_mask[ry, rx]:
                farthest_x, farthest_y = rx, ry
            else:
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
    h, w, c = arr.shape
    
    hsv_img = img.convert('HSV')
    hsv = np.array(hsv_img)
    H, S, V = hsv[:,:,0], hsv[:,:,1], hsv[:,:,2]
    
    R, G, B = arr[:,:,0], arr[:,:,1], arr[:,:,2]
    is_sea = (R == 203) & (G == 232) & (B == 246)
    
    # Define pixel coordinate grids for spatial constraints
    y_grid, x_grid = np.mgrid[0:h, 0:w]
    
    # Custom masks for WH, EH, SH to support overlaps and spatial constraints
    # NW: purple
    mask_nw = (H >= 190) & (H <= 235) & (S >= 50) & (S <= 120) & ~is_sea
    
    # EH: blue/violet/indigo and overlaps, limited to x >= 740 and y <= 480
    mask_eh = ((H >= 130) & (H <= 190) & (S >= 40) & (S <= 120) & ~is_sea) & (x_grid >= 740) & (y_grid <= 480)
    
    # WH: peach, and also includes cyan/blue overlap area up to x <= 820
    mask_wh = (((H >= 0) & (H <= 20) & (S >= 40) & (S <= 90)) | \
               ((H >= 120) & (H <= 165) & (S >= 40) & (S <= 120) & (x_grid <= 820))) & ~is_sea
               
    # SH: cyan, and also includes overlap area starting from x >= 730
    mask_sh = (((H >= 115) & (H <= 135) & (S >= 40) & (S <= 110)) | \
               ((H >= 135) & (H <= 165) & (S >= 40) & (S <= 120) & (x_grid >= 730) & (y_grid >= 400))) & ~is_sea

    # Other regions:
    mask_su = (H >= 50) & (H <= 65) & (S >= 70) & (S <= 140) & ~is_sea
    mask_ld = ((H >= 240) | (H <= 10)) & (S >= 70) & (S <= 140) & ~is_sea
    mask_yd = (H >= 15) & (H <= 27) & (S >= 70) & (S <= 140) & ~is_sea
    mask_pd = (H >= 28) & (H <= 42) & (S >= 70) & (S <= 140) & ~is_sea
    mask_sd = (H >= 80) & (H <= 110) & (S >= 70) & (S <= 140) & ~is_sea
    mask_bb = (H >= 45) & (H <= 59) & (S >= 70) & (S <= 140) & ~is_sea

    masks = {
        "NW": (mask_nw, (700, 200)),
        "EH": (mask_eh, (850, 250)),
        "WH": (mask_wh, (650, 450)),
        "SH": (mask_sh, (800, 500)),
        "SU": (mask_su, (820, 750)),
        "LD": (mask_ld, (880, 1000)),
        "YD": (mask_yd, (1000, 1020)),
        "PD": (mask_pd, (1020, 1250)),
        "SD": (mask_sd, (750, 1350)),
        "BB": (mask_bb, (780, 1550))
    }
    
    # Tracing and validation
    peaks = {
        "Ben Nevis": (56.7969, -5.0036, "WH"),
        "Snowdon": (53.0685, -4.0763, "SD"),
        "Scafell Pike": (54.4542, -3.2116, "LD"),
        "Pen y Fan": (51.8839, -3.4294, "BB"),
        "Cairn Gorm": (57.1162, -3.6428, "EH"),
        "Broad Law": (55.4981, -3.3503, "SU"),
        "Carn Eige": (57.2803, -5.1231, "NW")
    }
    
    print("--- Tracing Masks and Running Point-In-Polygon Validation ---")
    for code, (mask, center) in masks.items():
        pixel_poly = trace_region(arr, center[0], center[1], mask)
        gps_poly = [pixel_to_gps(px, py) for px, py in pixel_poly]
        
        # Verify peaks belonging to this region
        for peak_name, (lat, lon, target_code) in peaks.items():
            if target_code == code:
                inside = point_in_polygon(lat, lon, gps_poly)
                print(f"Peak {peak_name:12s} ({lat:.4f}, {lon:.4f}) inside {code}: {inside}")

if __name__ == '__main__':
    main()
