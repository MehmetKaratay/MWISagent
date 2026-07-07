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
Unit tests for the deterministic country-to-region mapping utility.
"""

import os
import sys

import pytest

SCRIPT_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../../app/skills/mwis-website/fetch_specific_forecast/scripts",
    )
)
sys.path.append(SCRIPT_DIR)

from query_country import get_regions_for_countries  # noqa: E402


def test_get_regions_for_single_country():
    """Test extracting exactly 5 regions for Scotland."""
    regions = get_regions_for_countries(["Scotland"])
    assert len(regions) == 5
    assert all(code in regions for code in ["NW", "WH", "EH", "SH", "SU"])


def test_get_regions_case_insensitive():
    """Test extracting regions with mixed case country names."""
    regions = get_regions_for_countries(["sCoTlAnD"])
    assert len(regions) == 5


def test_get_regions_multiple_countries_valid():
    """Test extracting regions for multiple countries summing to exactly 5."""
    regions = get_regions_for_countries(["England", "Wales"])
    assert len(regions) == 5
    # England has 3 (LD, YD, PD), Wales has 2 (SD, BB)
    expected_codes = ["LD", "YD", "PD", "SD", "BB"]
    assert all(code in regions for code in expected_codes)


def test_get_regions_exceed_limit_raises_error():
    """Test that requesting > 5 regions raises a ValueError."""
    with pytest.raises(ValueError, match="Maximum of 5 regions"):
        get_regions_for_countries(["Scotland", "England"])


def test_get_regions_unrecognized_country():
    """Test extracting regions for an unknown country."""
    regions = get_regions_for_countries(["France"])
    assert regions == []


def test_get_regions_mixed_valid_invalid():
    """Test extracting regions for a mix of valid and unknown countries."""
    regions = get_regions_for_countries(["Wales", "Narnia"])
    assert len(regions) == 2
    assert "SD" in regions
    assert "BB" in regions
