#!/usr/bin/env /usr/bin/python3
import sys
import os
import json
import math
import urllib.request
import urllib.parse

# Path Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, '..', 'assets')
RESOURCES_DIR = os.path.join(SCRIPT_DIR, '..', 'resources')

CONFIG_PATH = os.path.join(ASSETS_DIR, 'query_config.json')
BOUNDARIES_PATH = os.path.join(ASSETS_DIR, 'mwis_region_boundaries.json') # Wait! Let's check the filename in assets: earlier it was saved to mwis-region-boundaries.json! Let's verify.
# In task-254 it was: mwis-region-boundaries.json. Let's make sure it matches.
BOUNDARIES_PATH = os.path.join(ASSETS_DIR, 'mwis-region-boundaries.json')
MUNROS_PATH = os.path.join(RESOURCES_DIR, 'munros.csv')

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {"overlap_tolerance_pct": 15.0}
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except Exception:
        return {"overlap_tolerance_pct": 15.0}

def load_boundaries():
    try:
        with open(BOUNDARIES_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading boundaries file: {e}", file=sys.stderr)
        sys.exit(1)

def is_in_gb(lat, lon):
    # Bounding box check for Great Britain (excluding Northern Ireland)
    if not (49.9 <= lat <= 60.9 and -8.6 <= lon <= 1.8):
        return False
    # Exclude Northern Ireland box
    if (54.0 <= lat <= 55.3) and (-8.2 <= lon <= -5.4):
        return False
    return True

def search_munros(name):
    if not os.path.exists(MUNROS_PATH):
        return None
    try:
        with open(MUNROS_PATH, 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) >= 3 and parts[1].lower() == name.lower():
                    return parts[2] # Return RegionCode
    except Exception:
        pass
    return None

def query_nominatim(name):
    # Character limit mitigation for DoS
    if len(name) > 100:
        return None
    params = urllib.parse.urlencode({'q': name, 'format': 'json', 'addressdetails': 1, 'limit': 1})
    url = f"https://nominatim.openstreetmap.org/search?{params}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data:
                addr = data[0].get('address', {})
                country_code = addr.get('country_code', '')
                state = addr.get('state', '').lower()
                # Check scope constraints
                if country_code == 'gb' and 'northern ireland' not in state:
                    return float(data[0]['lat']), float(data[0]['lon'])
    except Exception:
        pass
    return None

def get_cardinal_direction(lat1, lon1, lat2, lon2):
    y = math.sin(math.radians(lon2 - lon1)) * math.cos(math.radians(lat2))
    x = math.cos(math.radians(lat1)) * math.sin(math.radians(lat2)) - \
        math.sin(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.cos(math.radians(lon2 - lon1))
    bearing = math.degrees(math.atan2(y, x))
    bearing = (bearing + 360) % 360
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    idx = round(bearing / 45) % 8
    return dirs[idx]

def point_to_segment_distance_km(p_lat, p_lon, lat1, lon1, lat2, lon2):
    avg_lat = (p_lat + lat1 + lat2) / 3.0
    scale_y = 111.0
    scale_x = 111.0 * math.cos(math.radians(avg_lat))
    px, py = p_lon * scale_x, p_lat * scale_y
    ax, ay = lon1 * scale_x, lat1 * scale_y
    bx, by = lon2 * scale_x, lat2 * scale_y
    abx, aby = bx - ax, by - ay
    apx, apy = px - ax, py - ay
    ab2 = abx*abx + aby*aby
    if ab2 == 0:
        return math.sqrt(apx*apx + apy*apy), lat1, lon1
    t = max(0.0, min(1.0, (apx*abx + apy*aby) / ab2))
    closest_px = ax + t * abx
    closest_py = ay + t * aby
    closest_lon = closest_px / scale_x
    closest_lat = closest_py / scale_y
    dist = math.sqrt((px - closest_px)**2 + (py - closest_py)**2)
    return dist, closest_lat, closest_lon

def polygon_distance_km(lat, lon, polygon):
    min_dist = float('inf')
    closest_pt = (None, None)
    # Loop over all edges
    for i in range(len(polygon) - 1):
        d, c_lat, c_lon = point_to_segment_distance_km(lat, lon, polygon[i][0], polygon[i][1], polygon[i+1][0], polygon[i+1][1])
        if d < min_dist:
            min_dist = d
            closest_pt = (c_lat, c_lon)
    return min_dist, closest_pt[0], closest_pt[1]

def point_in_polygon(lat, lon, polygon):
    # Ensure not closed loop duplicates
    if len(polygon) > 1 and polygon[0] == polygon[-1]:
        polygon = polygon[:-1]
    n = len(polygon)
    inside = False
    p1y, p1x = polygon[0]
    for i in range(n):
        p2y, p2x = polygon[(i + 1) % n]
        if min(p1y, p2y) < lat <= max(p1y, p2y):
            if lon <= max(p1x, p2x):
                if p1y != p2y:
                    xints = (lat - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                if p1x == p2x or lon <= xints:
                    inside = not inside
        p1y, p1x = p2y, p2x
    return inside

def get_matching_regions(lat, lon, boundaries):
    matches = []
    for code, info in boundaries.items():
        if point_in_polygon(lat, lon, info["coordinates"]):
            matches.append(code)
    # Return sorted unique matching region codes
    return sorted(list(set(matches)))

def get_nearest_regions(lat, lon, boundaries, tolerance_pct):
    distances = {}
    for code, info in boundaries.items():
        dist, c_lat, c_lon = polygon_distance_km(lat, lon, info["coordinates"])
        direction = get_cardinal_direction(lat, lon, c_lat, c_lon)
        distances[code] = (dist, direction)
    min_code = min(distances, key=lambda k: distances[k][0])
    min_dist = distances[min_code][0]
    limit = min_dist * (1.0 + tolerance_pct / 100.0)
    # Find all within tolerance limit
    near = [(code, dist, direct) for code, (dist, direct) in distances.items() if dist <= limit]
    return sorted(near, key=lambda x: x[1])

def handle_out_of_scope(as_json):
    msg = "The requested location is out of scope of this skill. Only locations in Great Britain are supported."
    if as_json:
        print(json.dumps({"in_scope": False, "error": "OUT_OF_SCOPE", "message": msg}))
    else:
        print(msg, file=sys.stderr)
    sys.exit(2)

def print_result_json(in_scope, in_area, regions, nearest):
    out = {"in_scope": in_scope, "in_area": in_area}
    if in_area:
        out["regions"] = regions
        out["overlap"] = len(regions) > 1
    else:
        out["nearest"] = [{"code": code, "distance_km": round(dist, 2), "direction": direct} for code, dist, direct in nearest]
    print(json.dumps(out))

def print_result_text(in_area, regions, nearest, boundaries):
    if in_area:
        names = [boundaries[code]["name"] for code in regions]
        print(f"Region(s): {', '.join(regions)} ({', '.join(names)})")
        if len(regions) > 1:
            print("Note: Overlap zone detected.")
    else:
        print("The location is not in an MWIS area.")
        print("Nearest area(s):")
        for code, dist, direct in nearest:
            print(f"  - {code} ({boundaries[code]['name']}): {dist:.2f} km away to the {direct}")

def resolve_input(args):
    # Parse inputs (returns lat, lon or region_code if Munro)
    if len(args) == 1:
        # Check Munro
        m_code = search_munros(args[0])
        if m_code:
            return None, None, m_code
        # Try Nominatim
        coords = query_nominatim(args[0])
        if coords:
            return coords[0], coords[1], None
    elif len(args) >= 2:
        try:
            return float(args[0]), float(args[1]), None
        except ValueError:
            pass
    return None, None, None

def main():
    args = [a for a in sys.argv[1:] if a != '--json']
    as_json = '--json' in sys.argv
    lat, lon, munro_code = resolve_input(args)
    boundaries = load_boundaries()
    
    if munro_code:
        # If it matched Munro directly
        if as_json:
            print_result_json(True, True, [munro_code], [])
        else:
            print_result_text(True, [munro_code], [], boundaries)
        sys.exit(0)
        
    if lat is None or lon is None or not is_in_gb(lat, lon):
        handle_out_of_scope(as_json)
        
    regions = get_matching_regions(lat, lon, boundaries)
    if regions:
        if as_json:
            print_result_json(True, True, regions, [])
        else:
            print_result_text(True, regions, [], boundaries)
    else:
        config = load_config()
        tol = config.get("overlap_tolerance_pct", 15.0)
        nearest = get_nearest_regions(lat, lon, boundaries, tol)
        if as_json:
            print_result_json(True, False, [], nearest)
        else:
            print_result_text(False, [], nearest, boundaries)

if __name__ == '__main__':
    main()
