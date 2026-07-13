# MWIS Agent (c) by Mehmet Rahmi Karatay
#
# MWIS Agent is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License.
#
# You should have received a copy of the license along with this
# work.  If not, see <https://creativecommons.org/licenses/by-sa/4.0/>.

import json
import os
import sys
from typing import Any

# Path Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, "..", "assets")
RESOURCES_DIR = os.path.join(SCRIPT_DIR, "..", "resources")

CONFIG_PATH = os.path.join(ASSETS_DIR, "query_config.json")
BOUNDARIES_PATH = os.path.join(ASSETS_DIR, "mwis-region-boundaries.json")
MUNROS_PATH = os.path.join(RESOURCES_DIR, "munros.csv")
LOCAL_NAMES_PATH = os.path.join(RESOURCES_DIR, "local-names.csv")
DB_PATH = os.path.join(SCRIPT_DIR, "..", "cache", "uk_hills.db")

DEFAULT_OVERLAP_TOLERANCE_PCT = 15.0


class BoundariesLoader:
    """Represents the BoundariesLoader logic."""

    @staticmethod
    def load() -> dict[str, Any]:
        """Loads boundaries from boundaries JSON file."""
        try:
            with open(BOUNDARIES_PATH) as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading boundaries file: {e}", file=sys.stderr)
            sys.exit(1)


class ConfigLoader:
    """Represents the ConfigLoader logic."""

    @staticmethod
    def get_overlap_tolerance() -> float:
        """Loads overlap tolerance percentage from config or default."""
        if not os.path.exists(CONFIG_PATH):
            return DEFAULT_OVERLAP_TOLERANCE_PCT
        try:
            with open(CONFIG_PATH) as f:
                config = json.load(f)
                return float(
                    config.get("overlap_tolerance_pct", DEFAULT_OVERLAP_TOLERANCE_PCT)
                )
        except Exception:
            return DEFAULT_OVERLAP_TOLERANCE_PCT
