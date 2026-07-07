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
    """Test the /api/date endpoint with missing q parameter."""
    response = client.get("/api/query_date")
    assert response.status_code == 422

@patch("os.environ.get")
@patch("requests.post")
def test_chat_api_local(mock_post, mock_getenv):
    """Test the /api/chat endpoint using local fallback."""
    mock_getenv.return_value = None
    mock_post.return_value.json.return_value = {"outputs": {"output": "hello"}}
    mock_post.return_value.raise_for_status.return_value = None
    
    response = client.post("/api/chat", json={"inputs": {"input": "hi"}})
    assert response.status_code == 200
    assert response.json() == {"outputs": {"output": "hello"}}
    mock_post.assert_called_once_with("http://localhost:8080/a2a/mwis-agent", json={"inputs": {"input": "hi"}})

@patch("os.environ.get")
@patch("vertexai.init")
@patch("vertexai.preview.reasoning_engines.ReasoningEngine")
def test_chat_api_remote(mock_reasoning_engine, mock_init, mock_getenv):
    """Test the /api/chat endpoint using remote Agent Runtime."""
    # Mock AGENT_RUNTIME_ID
    def mock_env(key, default=None):
        if key == "AGENT_RUNTIME_ID":
            return "projects/123/locations/europe-west2/reasoningEngines/456"
        return default
    mock_getenv.side_effect = mock_env
    
    mock_engine_instance = mock_reasoning_engine.return_value
    mock_engine_instance.query.return_value = {"outputs": {"output": "remote hello"}}
    
    response = client.post("/api/chat", json={"inputs": {"input": "hi"}})
    assert response.status_code == 200
    assert response.json() == {"outputs": {"output": "remote hello"}}
    mock_reasoning_engine.assert_called_once_with("projects/123/locations/europe-west2/reasoningEngines/456")
    mock_engine_instance.query.assert_called_once_with(input="hi")
