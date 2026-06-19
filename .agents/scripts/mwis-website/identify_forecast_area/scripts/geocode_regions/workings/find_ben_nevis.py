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
    # Grid search over the image area of Scotland
    for y in range(200, 800):
        for x in range(500, 1100):
            lat, lon = pixel_to_gps(x, y)
            dist = (lat - target_lat)**2 + (lon - target_lon)**2
            if dist < best_dist:
                best_dist = dist
                bx, by = x, y
    return bx, by

def main():
    bx, by = find_pixel(56.7969, -5.0036)
    print(f"Ben Nevis pixel coords: x={bx}, y={by}")
    
    # Let's sample the color at this pixel and its neighborhood
    img_path = '/home/karatay/Repositories/learning/ai/mwis_agent/.agents/skills/mwis-website/identify_forecast_area/assets/mwis-map.jpg'
    img = Image.open(img_path)
    arr = np.array(img)
    print(f"RGB at Ben Nevis: {arr[by, bx].tolist()}")
    
    # Convert to HSV
    hsv_img = img.convert('HSV')
    hsv = np.array(hsv_img)
    print(f"HSV at Ben Nevis: {hsv[by, bx].tolist()}")

if __name__ == '__main__':
    main()
