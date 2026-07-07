# MWIS Agent (c) by Mehmet Rahmi Karatay
#
# MWIS Agent is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License.
#
# You should have received a copy of the license along with this
# work.  If not, see <https://creativecommons.org/licenses/by-sa/4.0/>.

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

@app.post("/api/chat")
def proxy_chat(req: dict):
    """Proxies the chat request to the remote Agent Runtime or local ADK backend."""
    # Assuming input is {"inputs": {"input": "message"}}
    agent_id = os.environ.get("AGENT_RUNTIME_ID")
    if agent_id:
        try:
            import vertexai
            from vertexai.preview import reasoning_engines
            vertexai.init(project=os.environ.get("GOOGLE_CLOUD_PROJECT", "gen-lang-client-0727740856"))
            engine = reasoning_engines.ReasoningEngine(agent_id)
            user_input = req.get("inputs", {}).get("input", "")
            response = engine.query(input=user_input)
            return response
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Remote agent failed: {e}")
    else:
        # Local ADK fallback
        try:
            import requests
            resp = requests.post("http://localhost:8080/a2a/mwis-agent", json=req)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Local proxy failed: {e}")

# Mount static files at the root
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
