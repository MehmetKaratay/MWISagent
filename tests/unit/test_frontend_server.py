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

from unittest.mock import patch

from fastapi.testclient import TestClient

from frontend.server import app

client = TestClient(app)

@patch("subprocess.run")
def test_query_region_api(mock_run):
    """Test the /api/query_region endpoint."""
    mock_run.return_value.stdout = '{"region": "WH"}'
    mock_run.return_value.returncode = 0
    
    response = client.get("/api/query_region?q=Ben%20Nevis")
    assert response.status_code == 200
    assert response.json() == {"region": "WH"}
    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert "query_region.py" in args[-3]
    assert args[-2] == "Ben Nevis"
    assert args[-1] == "--json"

@patch("subprocess.run")
def test_query_date_api(mock_run):
    """Test the /api/query_date endpoint."""
    mock_run.return_value.stdout = '["D1"]'
    mock_run.return_value.returncode = 0
    
    response = client.get("/api/query_date?q=tomorrow")
    assert response.status_code == 200
    assert response.json() == ["D1"]
    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert "query_date.py" in args[-2]
    assert args[-1] == "tomorrow"

def test_query_region_missing_q():
    """Test the /api/query_region endpoint with missing q parameter."""
    response = client.get("/api/query_region")
    assert response.status_code == 422

def test_query_date_missing_q():
    """Test the /api/query_date endpoint with missing q parameter."""
    response = client.get("/api/query_date")
    assert response.status_code == 422
