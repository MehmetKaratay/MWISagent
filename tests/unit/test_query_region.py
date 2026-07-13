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


def test_query_region_local_name_cuillin():
    """Test that querying 'Cuillin' successfully maps to 'NW' via local-names.csv."""
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
        [sys.executable, str(script_path), "Cuillin", "--json"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["in_scope"] is True
    assert data["in_area"] is True
    assert "NW" in data["regions"]


def test_query_region_local_name_rum():
    """Test that querying 'Rum' successfully maps to 'NW' via local-names.csv."""
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
        [sys.executable, str(script_path), "Rum", "--json"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["in_scope"] is True
    assert data["in_area"] is True
    assert "NW" in data["regions"]


def test_query_region_local_name_case_insensitive():
    """Test that querying local names is case-insensitive (e.g. 'cuillins' maps to 'NW')."""
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
        [sys.executable, str(script_path), "cuillins", "--json"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["in_scope"] is True
    assert data["in_area"] is True
    assert "NW" in data["regions"]


def test_query_region_nearest_serialization_includes_direction():
    """Test that find_regions_by_location nearest results serialize with the direction key."""
    sys.path.insert(
        0,
        str(
            Path(__file__).resolve().parent.parent.parent
            / "app"
            / "skills"
            / "mwis-website"
            / "identify_forecast_area"
            / "scripts"
        ),
    )
    import query_region

    res = query_region.find_regions_by_location(["London"])
    assert res["in_scope"] is True
    assert res["in_area"] is False
    assert "nearest" in res
    assert len(res["nearest"]) > 0
    assert "direction" in res["nearest"][0]


def test_query_region_database_lookups():
    """Verify that Hills resolved from the SQLite database cache yield correct locations.
    Specifically, a hill inside MWIS area (e.g. Ben Nevis) should be resolved immediately,
    and a hill outside MWIS area (e.g. a 'notMWIS' hill) should resolve coordinates offline
    and trigger the nearest MWIS area calculation.
    """
    sys.path.insert(
        0,
        str(
            Path(__file__).resolve().parent.parent.parent
            / "app"
            / "skills"
            / "mwis-website"
            / "identify_forecast_area"
            / "scripts"
        ),
    )
    import query_region

    # 1. Ben Nevis (WH region)
    res_ben = query_region.find_regions_by_location(["Ben Nevis"])
    assert res_ben["in_scope"] is True
    assert res_ben["in_area"] is True
    assert "WH" in res_ben["regions"]

    # 2. Snowdon - Yr Wyddfa (SD region)
    res_snowdon = query_region.find_regions_by_location(["Snowdon - Yr Wyddfa"])
    assert res_snowdon["in_scope"] is True
    assert res_snowdon["in_area"] is True
    assert "SD" in res_snowdon["regions"]

    # 3. Leith Hill (notMWIS, Surrey, England)
    res_leith = query_region.find_regions_by_location(["Leith Hill"])
    assert res_leith["in_scope"] is True
    assert res_leith["in_area"] is False
    assert res_leith["error"] == "NOT_IN_AREA"
    assert "nearest" in res_leith
    assert len(res_leith["nearest"]) > 0
