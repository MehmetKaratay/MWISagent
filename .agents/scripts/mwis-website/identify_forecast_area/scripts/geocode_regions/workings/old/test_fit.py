#!/usr/bin/env /usr/bin/python3
import numpy as np

CITIES_GPS = {
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

CANDIDATE_3 = {
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

def fit_quadratic(candidates):
    X = []
    lat = []
    lon = []
    names = []
    for name, (gx, gy) in CITIES_GPS.items():
        if name in candidates:
            names.append(name)
            px, py = candidates[name]
            # 1, x, y, x^2, y^2, x*y
            X.append([1.0, px, py, px**2, py**2, px*py])
            lat.append(gx)
            lon.append(gy)
            
    X = np.array(X)
    lat = np.array(lat)
    lon = np.array(lon)
    
    coef_lat = np.linalg.lstsq(X, lat, rcond=None)[0]
    coef_lon = np.linalg.lstsq(X, lon, rcond=None)[0]
    
    pred_lat = X.dot(coef_lat)
    pred_lon = X.dot(coef_lon)
    
    residuals_lat = lat - pred_lat
    residuals_lon = lon - pred_lon
    dist_error = np.sqrt(residuals_lat**2 + residuals_lon**2)
    
    print(f"\n--- Quadratic Fit Report (9 Cities) ---")
    for i, name in enumerate(names):
        print(f"{name:12s}: pixel=({candidates[name][0]:.1f}, {candidates[name][1]:.1f}), err={dist_error[i]:.4f}")
    print(f"Mean residual error: {np.mean(dist_error):.5f}")
    return coef_lat, coef_lon

if __name__ == '__main__':
    fit_quadratic(CANDIDATE_3)
