#!/usr/bin/env /usr/bin/python3
import numpy as np
from PIL import Image

# Setup transformation
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

def find_pixel(target_lat, target_lon):
    best_dist = 1e9
    bx, by = 0, 0
    for y in range(100, 1643):
        for x in range(100, 1643):
            lat, lon = pixel_to_gps(x, y)
            dist = (lat - target_lat)**2 + (lon - target_lon)**2
            if dist < best_dist:
                best_dist = dist
                bx, by = x, y
    return bx, by

def main():
    peaks = {
        "Ben Nevis": (56.7969, -5.0036, "WH"),
        "Snowdon": (53.0685, -4.0763, "SD"),
        "Scafell Pike": (54.4542, -3.2116, "LD"),
        "Pen y Fan": (51.8839, -3.4294, "BB"),
        "Cairn Gorm": (57.1162, -3.6428, "EH"),
        "Broad Law": (55.4981, -3.3503, "SU"),
        "Carn Eige": (57.2803, -5.1231, "NW")
    }
    
    img_path = '/home/karatay/Repositories/learning/ai/mwis_agent/.agents/skills/mwis-website/identify_forecast_area/assets/mwis-map.jpg'
    img = Image.open(img_path)
    arr = np.array(img)
    h, w, c = arr.shape
    
    hsv_img = img.convert('HSV')
    hsv = np.array(hsv_img)
    H, S, V = hsv[:,:,0], hsv[:,:,1], hsv[:,:,2]
    
    R, G, B = arr[:,:,0], arr[:,:,1], arr[:,:,2]
    is_sea = (R == 203) & (G == 232) & (B == 246)
    
    y_grid, x_grid = np.mgrid[0:h, 0:w]
    
    mask_nw = (H >= 190) & (H <= 235) & (S >= 50) & (S <= 120) & ~is_sea
    mask_eh = ((H >= 130) & (H <= 190) & (S >= 40) & (S <= 120) & ~is_sea)
    mask_ld = ((H >= 240) | (H <= 10)) & (S >= 70) & (S <= 140) & ~is_sea

    # Print if the peak pixel is inside the raw masks
    for name, (lat, lon, code) in peaks.items():
        bx, by = find_pixel(lat, lon)
        if code == "NW":
            print(f"{name} pixel ({bx}, {by}) in NW mask: {mask_nw[by, bx]}")
        elif code == "EH":
            print(f"{name} pixel ({bx}, {by}) in EH mask: {mask_eh[by, bx]}")
        elif code == "LD":
            print(f"{name} pixel ({bx}, {by}) in LD mask: {mask_ld[by, bx]}")

if __name__ == '__main__':
    main()
