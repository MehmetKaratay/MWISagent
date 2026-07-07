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

import json
import os
import subprocess
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="MWISagent Frontend Dev Server")

# Define paths
FRONTEND_DIR = Path(__file__).parent
STATIC_DIR = FRONTEND_DIR / "static"
PROJECT_ROOT = FRONTEND_DIR.parent
REGION_SCRIPT = PROJECT_ROOT / "app" / "skills" / "mwis-website" / "identify_forecast_area" / "scripts" / "query_region.py"
DATE_SCRIPT = PROJECT_ROOT / "app" / "skills" / "mwis-website" / "identify_outing_date" / "scripts" / "query_date.py"

# Ensure static directory exists
STATIC_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/api/query_region")
def query_region(q: str = Query(..., description="The location to query")):
    """Executes the query_region script and returns its JSON output."""
    try:
        result = subprocess.run(
            [sys.executable, str(REGION_SCRIPT), q, "--json"],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Script failed: {e.stderr}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse script JSON output.")

@app.get("/api/query_date")
def query_date(q: str = Query(..., description="The date to query")):
    """Executes the query_date script and returns its JSON output."""
    try:
        result = subprocess.run(
            [sys.executable, str(DATE_SCRIPT), q],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Script failed: {e.stderr}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse script JSON output.")

# Mount static files at the root
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
