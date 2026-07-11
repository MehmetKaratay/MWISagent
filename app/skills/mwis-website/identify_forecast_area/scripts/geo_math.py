# MWIS Agent (c) by Mehmet Rahmi Karatay
#
# MWIS Agent is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License.
#
# You should have received a copy of the license along with this
# work.  If not, see <https://creativecommons.org/licenses/by-sa/4.0/>.

import math
from dataclasses import dataclass

# Constants
EARTH_RADIUS_KM = 111.0
CARDINAL_DIRS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
GB_LAT_MIN, GB_LAT_MAX = 49.9, 60.9
GB_LON_MIN, GB_LON_MAX = -8.6, 1.8
NI_LAT_MIN, NI_LAT_MAX = 54.0, 55.3
NI_LON_MIN, NI_LON_MAX = -8.2, -5.4


@dataclass
class Point:
    """Represents the Point logic."""

    lat: float
    lon: float


@dataclass
class Segment:
    """Represents the Segment logic."""

    start: Point
    end: Point


@dataclass
class RegionDistance:
    """Represents the RegionDistance logic."""

    code: str
    distance_km: float
    direction: str


class OutOfScopeError(Exception):
    """Represents the OutOfScopeError logic."""

    pass


class GeoMath:
    """Represents the GeoMath logic."""

    @staticmethod
    def is_in_gb(pt: Point) -> bool:
        """Determines if a point is within Great Britain bounds."""
        if not (
            GB_LAT_MIN <= pt.lat <= GB_LAT_MAX and GB_LON_MIN <= pt.lon <= GB_LON_MAX
        ):
            return False
        if (NI_LAT_MIN <= pt.lat <= NI_LAT_MAX) and (
            NI_LON_MIN <= pt.lon <= NI_LON_MAX
        ):
            return False
        return True

    @staticmethod
    def get_cardinal_direction(start: Point, target: Point) -> str:
        """Gets the cardinal direction from a start point to a target point."""
        y = math.sin(math.radians(target.lon - start.lon)) * math.cos(
            math.radians(target.lat)
        )
        x = math.cos(math.radians(start.lat)) * math.sin(
            math.radians(target.lat)
        ) - math.sin(math.radians(start.lat)) * math.cos(
            math.radians(target.lat)
        ) * math.cos(math.radians(target.lon - start.lon))
        bearing = math.degrees(math.atan2(y, x))
        bearing = (bearing + 360) % 360
        idx = round(bearing / 45) % 8
        return CARDINAL_DIRS[idx]

    @staticmethod
    def _project_point(pt: Point, scale_x: float) -> tuple[float, float]:
        """Projects a Point coordinate using dynamic scaling."""
        return pt.lon * scale_x, pt.lat * EARTH_RADIUS_KM

    @staticmethod
    def point_to_segment_distance(pt: Point, seg: Segment) -> tuple[float, Point]:
        """Computes the shortest distance from a Point to a Segment."""
        avg_lat = (pt.lat + seg.start.lat + seg.end.lat) / 3.0
        scale_x = EARTH_RADIUS_KM * math.cos(math.radians(avg_lat))
        px, py = GeoMath._project_point(pt, scale_x)
        ax, ay = GeoMath._project_point(seg.start, scale_x)
        bx, by = GeoMath._project_point(seg.end, scale_x)

        abx, aby = bx - ax, by - ay
        apx, apy = px - ax, py - ay
        ab2 = abx * abx + aby * aby
        if ab2 == 0:
            return math.sqrt(apx * apx + apy * apy), seg.start

        t = max(0.0, min(1.0, (apx * abx + apy * aby) / ab2))
        closest_lon = (ax + t * abx) / scale_x
        closest_lat = (ay + t * aby) / EARTH_RADIUS_KM
        dist = math.sqrt((px - (ax + t * abx)) ** 2 + (py - (ay + t * aby)) ** 2)
        return dist, Point(closest_lat, closest_lon)

    @staticmethod
    def point_in_polygon(pt: Point, polygon: list[list[float]]) -> bool:
        """Determines if a point is inside a polygon."""
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
    def polygon_distance(pt: Point, polygon: list[list[float]]) -> tuple[float, Point]:
        """Calculates distance from a point to a polygon boundary."""
        min_dist = float("inf")
        closest_pt = Point(0, 0)
        for i in range(len(polygon) - 1):
            seg = Segment(
                Point(polygon[i][0], polygon[i][1]),
                Point(polygon[i + 1][0], polygon[i + 1][1]),
            )
            d, c_pt = GeoMath.point_to_segment_distance(pt, seg)
            if d < min_dist:
                min_dist = d
                closest_pt = c_pt
        return min_dist, closest_pt
