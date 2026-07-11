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
Integration test using curl command to verify forecast output filtering.
"""

import json
import os
import subprocess
import time
from pathlib import Path


def test_curl_today_forecast_no_outlook():
    """Starts the dev server and hits it with curl POST to check for Outlook exclusion."""
    project_root = Path(__file__).resolve().parent.parent.parent
    server_path = project_root / "frontend" / "server.py"

    import sys

    # Start backend dev server on port 8080
    backend_proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.fast_api_app:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8080",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={
            "MWIS_ENV": "development",
            "INTEGRATION_TEST": "TRUE",
            "PATH": os.environ.get("PATH", ""),
        },
    )

    # Start frontend dev server on port 8000
    server_proc = subprocess.Popen(
        [sys.executable, str(server_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={"PORT": "8000", "PATH": os.environ.get("PATH", "")},
    )
    time.sleep(5)

    try:
        # Scenario 1: Today forecast only
        curl_cmd1 = [
            "curl",
            "-s",
            "-X",
            "POST",
            "http://localhost:8000/api/chat",
            "-H",
            "Content-Type: application/json",
            "-d",
            '{"inputs": {"input": "What is weather on Ben Nevis today?"}}',
        ]
        res1 = subprocess.run(curl_cmd1, capture_output=True, text=True)
        assert res1.returncode == 0
        out1 = json.loads(res1.stdout).get("outputs", {}).get("output", "")
        assert "No response" not in out1
        assert "Outlook:" not in out1
        # It should not contain details from tomorrow's forecast (Monday in mock data)
        assert "Monday" not in out1

        # Scenario 2: Today and tomorrow forecast
        curl_cmd2 = [
            "curl",
            "-s",
            "-X",
            "POST",
            "http://localhost:8000/api/chat",
            "-H",
            "Content-Type: application/json",
            "-d",
            '{"inputs": {"input": "What is weather on Ben Nevis today and tomorrow?"}}',
        ]
        res2 = subprocess.run(curl_cmd2, capture_output=True, text=True)
        assert res2.returncode == 0
        out2 = json.loads(res2.stdout).get("outputs", {}).get("output", "")
        assert "Outlook:" not in out2

        # Scenario 3: Next week (Outlook only)
        curl_cmd3 = [
            "curl",
            "-s",
            "-X",
            "POST",
            "http://localhost:8000/api/chat",
            "-H",
            "Content-Type: application/json",
            "-d",
            '{"inputs": {"input": "What is weather on Ben Nevis next week?"}}',
        ]
        res3 = subprocess.run(curl_cmd3, capture_output=True, text=True)
        assert res3.returncode == 0
        out3 = json.loads(res3.stdout).get("outputs", {}).get("output", "")
        assert "outlook" in out3.lower()

        # Scenario 4: Full weather forecast (No date specification)
        curl_cmd4 = [
            "curl",
            "-s",
            "-X",
            "POST",
            "http://localhost:8000/api/chat",
            "-H",
            "Content-Type: application/json",
            "-d",
            '{"inputs": {"input": "What is the full weather forecast on Ben Nevis?"}}',
        ]
        res4 = subprocess.run(curl_cmd4, capture_output=True, text=True)
        assert res4.returncode == 0
        out4 = json.loads(res4.stdout).get("outputs", {}).get("output", "")
        assert "outlook" in out4.lower()
    finally:
        server_proc.terminate()
        backend_proc.terminate()
        server_proc.wait()
        backend_proc.wait()
