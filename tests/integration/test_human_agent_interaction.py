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
        # Run curl POST request
        curl_cmd = [
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
        result = subprocess.run(curl_cmd, capture_output=True, text=True)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        output_text = data.get("outputs", {}).get("output", "")

        assert "No response" not in output_text
        assert "Proxy failed" not in output_text

        # Verify that the word "Outlook:" is not in the text response
        assert "Outlook:" not in output_text
    finally:
        server_proc.terminate()
        backend_proc.terminate()
        server_proc.wait()
        backend_proc.wait()
