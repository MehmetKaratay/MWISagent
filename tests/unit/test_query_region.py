# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Unit tests for query_region.py debugging.
"""

import json
import subprocess
import sys
from pathlib import Path


def test_query_region_out_of_bounds_json():
    """Test that querying a location outside MWIS areas (e.g. London) with --json
    returns a valid JSON object containing the 'nearest' key with a serialized list.
    """
    project_root = Path(__file__).resolve().parent.parent.parent
    script_path = (
        project_root
        / "app"
        / "skills"
        / "mwis-website"
        / "identify_forecast_area"
        / "scripts"
        / "query_region.py"
    )

    result = subprocess.run(
        [sys.executable, str(script_path), "London", "--json"],
        capture_output=True,
        text=True,
    )

    # We expect return code 0 because it handles the out-of-bounds gracefully in JSON mode
    assert result.returncode == 0

    # It must be valid JSON
    data = json.loads(result.stdout)
    assert data["in_scope"] is True
    assert data["in_area"] is False
    assert data["error"] == "NOT_IN_AREA"
    assert "nearest" in data
    assert isinstance(data["nearest"], list)
    assert len(data["nearest"]) > 0

    # The first item should have code and distance_km
    first_nearest = data["nearest"][0]
    assert "code" in first_nearest
    assert "distance_km" in first_nearest
