#!/usr/bin/env python3
# MWIS Agent (c) by Mehmet Rahmi Karatay
#
# MWIS Agent is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License.
#
# You should have received a copy of the license along with this
# work.  If not, see <https://creativecommons.org/licenses/by-sa/4.0/>.

import json
import sys
from typing import Any

from config_loader import BoundariesLoader, ConfigLoader
from geo_math import GeoMath, Point, RegionDistance
from input_resolver import InputResolver


class RegionFinder:
    """Represents the RegionFinder logic."""

    def __init__(self, boundaries: dict[str, Any]):
        """Executes the __init__ operation.

        Args:
            boundaries: The boundaries parameter.
        """
        self.boundaries = boundaries

    def get_matching_regions(self, pt: Point) -> list[str]:
        """Executes the get_matching_regions operation.

        Args:
            pt: The pt parameter.
        Returns:
            The return value.
        """
        matches = []
        for code, info in self.boundaries.items():
            if GeoMath.point_in_polygon(pt, info["coordinates"]):
                matches.append(code)
        return sorted(set(matches))

    def _calculate_region_distances(self, pt: Point) -> list[RegionDistance]:
        """Calculates distance and direction to each region boundary.

        Args:
            pt: Query point.

        Returns:
            List of region distance mappings.
        """
        distances = []
        for code, info in self.boundaries.items():
            dist, c_pt = GeoMath.polygon_distance(pt, info["coordinates"])
            direction = GeoMath.get_cardinal_direction(pt, c_pt)
            distances.append(RegionDistance(code, dist, direction))
        return distances

    def get_nearest_regions(
        self, pt: Point, tolerance_pct: float
    ) -> list[RegionDistance]:
        """Gets the list of nearest regions within the tolerance limit.

        Args:
            pt: Query point.
            tolerance_pct: Overlap tolerance percentage.

        Returns:
            Sorted list of nearest region distances.
        """
        distances = self._calculate_region_distances(pt)
        if not distances:
            return []
        min_dist = min(d.distance_km for d in distances)
        limit = min_dist * (1.0 + tolerance_pct / 100.0)
        near = [d for d in distances if d.distance_km <= limit]
        near.sort(key=lambda x: x.distance_km)
        return near


class ResultFormatter:
    """Represents the ResultFormatter logic."""

    def format_success(self, regions: list[str], boundaries: dict[str, Any]) -> None:
        """Executes the format_success operation.

        Args:
            regions: The regions parameter.
            boundaries: The boundaries parameter.
        """
        pass

    def format_nearest(
        self, nearest: list[RegionDistance], boundaries: dict[str, Any]
    ) -> None:
        """Executes the format_nearest operation.

        Args:
            nearest: The nearest parameter.
            boundaries: The boundaries parameter.
        """
        pass

    def format_out_of_scope(self) -> None:
        """Executes the format_out_of_scope operation."""
        pass


class JsonFormatter(ResultFormatter):
    """Represents the JsonFormatter logic."""

    def format_success(self, regions: list[str], boundaries: dict[str, Any]) -> None:
        """Executes the format_success operation.

        Args:
            regions: The regions parameter.
            boundaries: The boundaries parameter.
        """
        out = {"in_scope": True, "in_area": True, "regions": regions}
        print(json.dumps(out))

    def format_nearest(
        self, nearest: list[RegionDistance], boundaries: dict[str, Any]
    ) -> None:
        """Executes the format_nearest operation.

        Args:
            nearest: The nearest parameter.
            boundaries: The boundaries parameter.
        """
        nearest_serialized = [
            {"code": reg.code, "distance": reg.distance_km, "direction": reg.direction}
            for reg in nearest
        ]
        out = {
            "in_scope": True,
            "in_area": False,
            "regions": [],
            "nearest": nearest_serialized,
        }
        print(json.dumps(out))

    def format_out_of_scope(self) -> None:
        """Executes the format_out_of_scope operation."""
        out = {
            "in_scope": False,
            "in_area": False,
            "error": "OUT_OF_SCOPE",
        }
        print(json.dumps(out))


class TextFormatter(ResultFormatter):
    """Represents the TextFormatter logic."""

    def format_success(self, regions: list[str], boundaries: dict[str, Any]) -> None:
        """Executes the format_success operation.

        Args:
            regions: The regions parameter.
            boundaries: The boundaries parameter.
        """
        names = [boundaries[code]["name"] for code in regions]
        print(f"Region(s): {', '.join(regions)} ({', '.join(names)})")
        if len(regions) > 1:
            print("Note: Overlap zone detected.")

    def format_nearest(
        self, nearest: list[RegionDistance], boundaries: dict[str, Any]
    ) -> None:
        """Executes the format_nearest operation.

        Args:
            nearest: The nearest parameter.
            boundaries: The boundaries parameter.
        """
        print("The location is not in an MWIS area.")
        print("Nearest area(s):")
        for d in nearest:
            name = boundaries[d.code]["name"]
            print(
                f"  - {d.code} ({name}): {d.distance_km:.2f} km away to the {d.direction}"
            )

    def format_out_of_scope(self) -> None:
        """Executes the format_out_of_scope operation."""
        msg = "The requested location is out of scope of this skill. Only locations in Great Britain are supported."
        print(msg, file=sys.stderr)


def _process_location(
    pt: Point, boundaries: dict[str, Any], formatter: ResultFormatter
) -> None:
    """Processes location by finding regions or formatting nearest."""
    finder = RegionFinder(boundaries)
    regions = finder.get_matching_regions(pt)
    if regions:
        formatter.format_success(regions, boundaries)
    else:
        tol = ConfigLoader.get_overlap_tolerance()
        nearest = finder.get_nearest_regions(pt, tol)
        formatter.format_nearest(nearest, boundaries)


def _serialize_nearest(nearest: list[RegionDistance]) -> list[dict]:
    """Serializes nearest regions list to dict list for JSON output."""
    return [{"code": reg.code, "distance_km": reg.distance_km} for reg in nearest]


def _find_regions_by_coords(pt: Point, boundaries: dict[str, Any]) -> dict:
    """Finds regions or nearest regions for a Point inside GB."""
    finder = RegionFinder(boundaries)
    regions = finder.get_matching_regions(pt)
    if regions:
        return {"in_scope": True, "in_area": True, "regions": regions}
    tol = ConfigLoader.get_overlap_tolerance()
    nearest = finder.get_nearest_regions(pt, tol)
    return {
        "in_scope": True,
        "in_area": False,
        "error": "NOT_IN_AREA",
        "nearest": _serialize_nearest(nearest),
    }


def find_regions_by_location(location_args: list[str]) -> dict:
    """Find regions for a given location, coordinate, or grid reference."""
    pt, munro_code = InputResolver.resolve_args(location_args)
    boundaries = BoundariesLoader.load()

    if munro_code:
        return {"in_scope": True, "in_area": True, "regions": [munro_code]}

    if pt is None or not GeoMath.is_in_gb(pt):
        return {"in_scope": False, "in_area": False, "error": "OUT_OF_SCOPE"}

    return _find_regions_by_coords(pt, boundaries)


def main():
    """Executes the main operation."""
    args = [a for a in sys.argv[1:] if a != "--json"]
    as_json = "--json" in sys.argv

    if as_json:
        data = find_regions_by_location(args)
        print(json.dumps(data))
        if not data.get("in_scope"):
            sys.exit(2)
        sys.exit(0)
    else:
        formatter = TextFormatter()
        pt, munro_code = InputResolver.resolve_args(args)
        boundaries = BoundariesLoader.load()
        if munro_code:
            formatter.format_success([munro_code], boundaries)
            sys.exit(0)
        if pt is None or not GeoMath.is_in_gb(pt):
            formatter.format_out_of_scope()
            sys.exit(2)

        finder = RegionFinder(boundaries)
        regions = finder.get_matching_regions(pt)
        if regions:
            formatter.format_success(regions, boundaries)
        else:
            tol = ConfigLoader.get_overlap_tolerance()
            nearest = finder.get_nearest_regions(pt, tol)
            formatter.format_nearest(nearest, boundaries)


if __name__ == "__main__":
    main()
