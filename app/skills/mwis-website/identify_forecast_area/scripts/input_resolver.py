# MWIS Agent (c) by Mehmet Rahmi Karatay
#
# MWIS Agent is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License.
#
# You should have received a copy of the license along with this
# work.  If not, see <https://creativecommons.org/licenses/by-sa/4.0/>.

import json
import os
import urllib.parse
import urllib.request
from typing import Any

from config_loader import LOCAL_NAMES_PATH, MUNROS_PATH
from geo_math import Point

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

# Grid reference constants
GRID_ALPHABET = "ABCDEFGHJKLMNOPQRSTUVWXYZ"
GRID_SIZE_500K_M = 500000
GRID_SIZE_100K_M = 100000
GRID_COLS = 5
GRID_ROW_OFFSET_500K = 3
GRID_ROW_OFFSET_100K = 4
MAX_GRID_DIGIT_PRECISION = 5
EPSG_BNG = "epsg:27700"
EPSG_WGS84 = "epsg:4326"


class InputResolver:
    """Represents the InputResolver logic."""

    @staticmethod
    def _fetch_nominatim_data(name: str) -> dict[str, Any] | None:
        """Fetches geographical coordinates data from OSM Nominatim API."""
        params = urllib.parse.urlencode(
            {"q": name, "format": "json", "addressdetails": 1, "limit": 1}
        )
        url = f"{NOMINATIM_URL}?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode("utf-8"))
                return data[0] if data else None
        except Exception:
            return None

    @staticmethod
    def search_munros(name: str) -> str | None:
        """Searches the munros.csv file for a matching region ID."""
        if not os.path.exists(MUNROS_PATH):
            return None
        try:
            with open(MUNROS_PATH) as f:
                for line in f:
                    parts = line.strip().split(",")
                    if (
                        len(parts) >= 3
                        and parts[1].strip().lower() == name.strip().lower()
                    ):
                        return parts[2].strip()
        except Exception:
            pass
        return None

    @staticmethod
    def search_local_names(name: str) -> str | None:
        """Searches the local-names.csv file for a matching region ID."""
        if not os.path.exists(LOCAL_NAMES_PATH):
            return None
        try:
            with open(LOCAL_NAMES_PATH) as f:
                for line in f:
                    parts = line.strip().split(",")
                    if len(parts) >= 2:
                        csv_name = parts[0].strip().replace('"', "").lower()
                        if csv_name == name.strip().lower():
                            return parts[1].strip()
        except Exception:
            pass
        return None

    @staticmethod
    def query_nominatim(name: str) -> Point | None:
        """Queries OpenStreetMap Nominatim API for a location name."""
        if len(name) > 100:
            return None
        data = InputResolver._fetch_nominatim_data(name)
        if not data:
            return None
        try:
            return Point(float(data["lat"]), float(data["lon"]))
        except (KeyError, ValueError):
            return None

    @staticmethod
    def _get_grid_square_base(
        first: str, second: str
    ) -> tuple[int, int, int, int] | None:
        """Calculates BNG grid square offsets based on letter indexes."""
        try:
            f_idx = GRID_ALPHABET.index(first)
            s_idx = GRID_ALPHABET.index(second)
        except ValueError:
            return None
        e500 = ((f_idx % GRID_COLS) - 2) * GRID_SIZE_500K_M
        n500 = (GRID_ROW_OFFSET_500K - (f_idx // GRID_COLS)) * GRID_SIZE_500K_M
        e100 = (s_idx % GRID_COLS) * GRID_SIZE_100K_M
        n100 = (GRID_ROW_OFFSET_100K - (s_idx // GRID_COLS)) * GRID_SIZE_100K_M
        return e500, n500, e100, n100

    @staticmethod
    def _bng_to_wgs84(e: int, n: int) -> Point:
        """Transforms BNG (EPSG:27700) to WGS84 (EPSG:4326) coordinates."""
        from pyproj import Transformer

        transformer = Transformer.from_crs(EPSG_BNG, EPSG_WGS84, always_xy=True)
        lon, lat = transformer.transform(e, n)
        return Point(lat, lon)

    @staticmethod
    def parse_grid_reference(grid_ref: str) -> Point | None:
        """Parses an OS grid reference and converts it to WGS84 coordinates."""
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
        scale = 10 ** (MAX_GRID_DIGIT_PRECISION - len(digits) // 2)
        e = e500 + e100 + int(digits[: len(digits) // 2]) * scale
        n = n500 + n100 + int(digits[len(digits) // 2 :]) * scale
        return InputResolver._bng_to_wgs84(e, n)

    @staticmethod
    def _resolve_single_arg(arg: str) -> tuple[Point | None, str | None]:
        """Resolves a single argument to either a Point or a region code."""
        cleaned = arg.strip()
        if cleaned.lower().startswith("reset "):
            cleaned = cleaned[6:].strip()
        grid_pt = InputResolver.parse_grid_reference(cleaned)
        if grid_pt:
            return grid_pt, None
        m_code = InputResolver.search_munros(cleaned)
        if m_code:
            return None, m_code
        local_code = InputResolver.search_local_names(cleaned)
        if local_code:
            return None, local_code
        coords = InputResolver.query_nominatim(cleaned)
        if coords:
            return coords, None
        return None, None

    @staticmethod
    def resolve_args(args: list[str]) -> tuple[Point | None, str | None]:
        """Resolves command-line arguments to coordinates or a region code."""
        if len(args) == 1:
            return InputResolver._resolve_single_arg(args[0])
        if len(args) >= 2:
            try:
                return Point(float(args[0]), float(args[1])), None
            except ValueError:
                # If they are not floats, join them as a single multi-word query (e.g. ['West', 'Highlands'] -> 'West Highlands')
                joined_name = " ".join(args)
                return InputResolver._resolve_single_arg(joined_name)
        return None, None
