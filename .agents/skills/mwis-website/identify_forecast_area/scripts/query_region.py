#!/usr/bin/env python3
import sys
import os
import json
import math
import urllib.request
import urllib.parse
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional, Any

# Path Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, '..', 'assets')
RESOURCES_DIR = os.path.join(SCRIPT_DIR, '..', 'resources')

CONFIG_PATH = os.path.join(ASSETS_DIR, 'query_config.json')
BOUNDARIES_PATH = os.path.join(ASSETS_DIR, 'mwis-region-boundaries.json')
MUNROS_PATH = os.path.join(RESOURCES_DIR, 'munros.csv')

# Constants
DEFAULT_OVERLAP_TOLERANCE_PCT = 15.0
EARTH_RADIUS_KM = 111.0
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
CARDINAL_DIRS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
GB_LAT_MIN, GB_LAT_MAX = 49.9, 60.9
GB_LON_MIN, GB_LON_MAX = -8.6, 1.8
NI_LAT_MIN, NI_LAT_MAX = 54.0, 55.3
NI_LON_MIN, NI_LON_MAX = -8.2, -5.4

@dataclass
class Point:
    lat: float
    lon: float

@dataclass
class Segment:
    start: Point
    end: Point

@dataclass
class RegionDistance:
    code: str
    distance_km: float
    direction: str

class OutOfScopeError(Exception):
    pass

class BoundariesLoader:
    @staticmethod
    def load() -> Dict[str, Any]:
        try:
            with open(BOUNDARIES_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading boundaries file: {e}", file=sys.stderr)
            sys.exit(1)

class ConfigLoader:
    @staticmethod
    def get_overlap_tolerance() -> float:
        if not os.path.exists(CONFIG_PATH):
            return DEFAULT_OVERLAP_TOLERANCE_PCT
        try:
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
                return float(config.get("overlap_tolerance_pct", DEFAULT_OVERLAP_TOLERANCE_PCT))
        except Exception:
            return DEFAULT_OVERLAP_TOLERANCE_PCT

class GeoMath:
    @staticmethod
    def is_in_gb(pt: Point) -> bool:
        if not (GB_LAT_MIN <= pt.lat <= GB_LAT_MAX and GB_LON_MIN <= pt.lon <= GB_LON_MAX):
            return False
        if (NI_LAT_MIN <= pt.lat <= NI_LAT_MAX) and (NI_LON_MIN <= pt.lon <= NI_LON_MAX):
            return False
        return True

    @staticmethod
    def get_cardinal_direction(start: Point, target: Point) -> str:
        y = math.sin(math.radians(target.lon - start.lon)) * math.cos(math.radians(target.lat))
        x = math.cos(math.radians(start.lat)) * math.sin(math.radians(target.lat)) - \
            math.sin(math.radians(start.lat)) * math.cos(math.radians(target.lat)) * math.cos(math.radians(target.lon - start.lon))
        bearing = math.degrees(math.atan2(y, x))
        bearing = (bearing + 360) % 360
        idx = round(bearing / 45) % 8
        return CARDINAL_DIRS[idx]

    @staticmethod
    def _project_point(pt: Point, scale_x: float) -> Tuple[float, float]:
        return pt.lon * scale_x, pt.lat * EARTH_RADIUS_KM

    @staticmethod
    def point_to_segment_distance(pt: Point, seg: Segment) -> Tuple[float, Point]:
        avg_lat = (pt.lat + seg.start.lat + seg.end.lat) / 3.0
        scale_x = EARTH_RADIUS_KM * math.cos(math.radians(avg_lat))
        px, py = GeoMath._project_point(pt, scale_x)
        ax, ay = GeoMath._project_point(seg.start, scale_x)
        bx, by = GeoMath._project_point(seg.end, scale_x)
        
        abx, aby = bx - ax, by - ay
        apx, apy = px - ax, py - ay
        ab2 = abx*abx + aby*aby
        if ab2 == 0:
            return math.sqrt(apx*apx + apy*apy), seg.start
            
        t = max(0.0, min(1.0, (apx*abx + apy*aby) / ab2))
        closest_lon = (ax + t * abx) / scale_x
        closest_lat = (ay + t * aby) / EARTH_RADIUS_KM
        dist = math.sqrt((px - (ax + t * abx))**2 + (py - (ay + t * aby))**2)
        return dist, Point(closest_lat, closest_lon)

    @staticmethod
    def point_in_polygon(pt: Point, polygon: List[List[float]]) -> bool:
        if len(polygon) > 1 and polygon[0] == polygon[-1]:
            polygon = polygon[:-1]
        n = len(polygon)
        inside = False
        p1y, p1x = polygon[0]
        for i in range(n):
            p2y, p2x = polygon[(i + 1) % n]
            if min(p1y, p2y) < pt.lat <= max(p1y, p2y):
                if pt.lon <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (pt.lat - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or pt.lon <= xints:
                        inside = not inside
            p1y, p1x = p2y, p2x
        return inside

    @staticmethod
    def polygon_distance(pt: Point, polygon: List[List[float]]) -> Tuple[float, Point]:
        min_dist = float('inf')
        closest_pt = Point(0, 0)
        for i in range(len(polygon) - 1):
            seg = Segment(Point(polygon[i][0], polygon[i][1]), Point(polygon[i+1][0], polygon[i+1][1]))
            d, c_pt = GeoMath.point_to_segment_distance(pt, seg)
            if d < min_dist:
                min_dist = d
                closest_pt = c_pt
        return min_dist, closest_pt

class RegionFinder:
    def __init__(self, boundaries: Dict[str, Any]):
        self.boundaries = boundaries

    def get_matching_regions(self, pt: Point) -> List[str]:
        matches = []
        for code, info in self.boundaries.items():
            if GeoMath.point_in_polygon(pt, info["coordinates"]):
                matches.append(code)
        return sorted(list(set(matches)))

    def get_nearest_regions(self, pt: Point, tolerance_pct: float) -> List[RegionDistance]:
        distances = []
        for code, info in self.boundaries.items():
            dist, c_pt = GeoMath.polygon_distance(pt, info["coordinates"])
            direction = GeoMath.get_cardinal_direction(pt, c_pt)
            distances.append(RegionDistance(code, dist, direction))
            
        if not distances:
            return []
            
        min_dist = min(d.distance_km for d in distances)
        limit = min_dist * (1.0 + tolerance_pct / 100.0)
        
        near = [d for d in distances if d.distance_km <= limit]
        near.sort(key=lambda x: x.distance_km)
        return near

class InputResolver:
    @staticmethod
    def _fetch_nominatim_data(name: str) -> Optional[Dict[str, Any]]:
        params = urllib.parse.urlencode({'q': name, 'format': 'json', 'addressdetails': 1, 'limit': 1})
        url = f"{NOMINATIM_URL}?{params}"
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data[0] if data else None
        except Exception:
            return None

    @staticmethod
    def search_munros(name: str) -> Optional[str]:
        if not os.path.exists(MUNROS_PATH):
            return None
        try:
            with open(MUNROS_PATH, 'r') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) >= 3 and parts[1].lower() == name.lower():
                        return parts[2]
        except Exception:
            pass
        return None

    @staticmethod
    def query_nominatim(name: str) -> Optional[Point]:
        if len(name) > 100:
            return None
        data = InputResolver._fetch_nominatim_data(name)
        if not data:
            return None
            
        addr = data.get('address', {})
        country_code = addr.get('country_code', '')
        state = addr.get('state', '').lower()
        
        if country_code == 'gb' and 'northern ireland' not in state:
            return Point(float(data['lat']), float(data['lon']))
        return None

    @staticmethod
    def _get_grid_square_base(first: str, second: str) -> Optional[Tuple[int, int, int, int]]:
        alphabet = "ABCDEFGHJKLMNOPQRSTUVWXYZ"
        try:
            f_idx = alphabet.index(first)
            s_idx = alphabet.index(second)
        except ValueError:
            return None
        e500 = ((f_idx % 5) - 2) * 500000
        n500 = (3 - (f_idx // 5)) * 500000
        e100 = (s_idx % 5) * 100000
        n100 = (4 - (s_idx // 5)) * 100000
        return e500, n500, e100, n100

    @staticmethod
    def parse_grid_reference(grid_ref: str) -> Optional[Point]:
        grid_ref = grid_ref.replace(" ", "").upper()
        if len(grid_ref) < 2 or not grid_ref[:2].isalpha():
            return None
        first, second, digits = grid_ref[0], grid_ref[1], grid_ref[2:]
        if len(digits) % 2 != 0 or not digits.isdigit() or not digits:
            return None
        base = InputResolver._get_grid_square_base(first, second)
        if not base:
            return None
        e500, n500, e100, n100 = base
        scale = 10 ** (5 - len(digits) // 2)
        e = e500 + e100 + int(digits[:len(digits)//2]) * scale
        n = n500 + n100 + int(digits[len(digits)//2:]) * scale
        from pyproj import Transformer
        transformer = Transformer.from_crs("epsg:27700", "epsg:4326", always_xy=True)
        lon, lat = transformer.transform(e, n)
        return Point(lat, lon)

    @staticmethod
    def resolve_args(args: List[str]) -> Tuple[Optional[Point], Optional[str]]:
        if len(args) == 1:
            grid_pt = InputResolver.parse_grid_reference(args[0])
            if grid_pt:
                return grid_pt, None
            m_code = InputResolver.search_munros(args[0])
            if m_code:
                return None, m_code
            coords = InputResolver.query_nominatim(args[0])
            if coords:
                return coords, None
        elif len(args) >= 2:
            try:
                return Point(float(args[0]), float(args[1])), None
            except ValueError:
                pass
        return None, None

class ResultFormatter:
    def format_success(self, regions: List[str], boundaries: Dict[str, Any]) -> None:
        raise NotImplementedError

    def format_nearest(self, nearest: List[RegionDistance], boundaries: Dict[str, Any]) -> None:
        raise NotImplementedError
        
    def format_out_of_scope(self) -> None:
        raise NotImplementedError

class JsonFormatter(ResultFormatter):
    def format_success(self, regions: List[str], boundaries: Dict[str, Any]) -> None:
        out = {
            "in_scope": True,
            "in_area": True,
            "regions": regions,
            "overlap": len(regions) > 1
        }
        print(json.dumps(out))

    def format_nearest(self, nearest: List[RegionDistance], boundaries: Dict[str, Any]) -> None:
        out = {
            "in_scope": True,
            "in_area": False,
            "nearest": [
                {
                    "code": d.code,
                    "distance_km": round(d.distance_km, 2),
                    "direction": d.direction
                } for d in nearest
            ]
        }
        print(json.dumps(out))
        
    def format_out_of_scope(self) -> None:
        out = {
            "in_scope": False, 
            "error": "OUT_OF_SCOPE", 
            "message": "The requested location is out of scope of this skill. Only locations in Great Britain are supported."
        }
        print(json.dumps(out))

class TextFormatter(ResultFormatter):
    def format_success(self, regions: List[str], boundaries: Dict[str, Any]) -> None:
        names = [boundaries[code]["name"] for code in regions]
        print(f"Region(s): {', '.join(regions)} ({', '.join(names)})")
        if len(regions) > 1:
            print("Note: Overlap zone detected.")

    def format_nearest(self, nearest: List[RegionDistance], boundaries: Dict[str, Any]) -> None:
        print("The location is not in an MWIS area.")
        print("Nearest area(s):")
        for d in nearest:
            name = boundaries[d.code]["name"]
            print(f"  - {d.code} ({name}): {d.distance_km:.2f} km away to the {d.direction}")
            
    def format_out_of_scope(self) -> None:
        msg = "The requested location is out of scope of this skill. Only locations in Great Britain are supported."
        print(msg, file=sys.stderr)

def _process_location(pt: Point, boundaries: Dict[str, Any], formatter: ResultFormatter) -> None:
    finder = RegionFinder(boundaries)
    regions = finder.get_matching_regions(pt)
    if regions:
        formatter.format_success(regions, boundaries)
    else:
        tol = ConfigLoader.get_overlap_tolerance()
        nearest = finder.get_nearest_regions(pt, tol)
        formatter.format_nearest(nearest, boundaries)

def main():
    args = [a for a in sys.argv[1:] if a != '--json']
    as_json = '--json' in sys.argv
    formatter = JsonFormatter() if as_json else TextFormatter()
    
    pt, munro_code = InputResolver.resolve_args(args)
    boundaries = BoundariesLoader.load()
    
    if munro_code:
        formatter.format_success([munro_code], boundaries)
        sys.exit(0)
        
    if pt is None or not GeoMath.is_in_gb(pt):
        formatter.format_out_of_scope()
        sys.exit(2)
        
    _process_location(pt, boundaries, formatter)

if __name__ == '__main__':
    main()
