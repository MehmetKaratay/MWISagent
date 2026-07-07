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
    import subprocess
    import json
    import os
    
    agent_id = os.environ.get("AGENT_RUNTIME_ID")
    user_input = req.get("inputs", {}).get("input", "")
    
    if agent_id:
        # Remote Agent Runtime (e.g. europe-west2)
        url = f"https://europe-west2-aiplatform.googleapis.com/v1/{agent_id}"
    else:
        # Local ADK fallback
        url = "http://localhost:8080"
        
    try:
        # Use agents-cli run --mode a2a -v to get the output from the ADK app
        cmd = ["agents-cli", "run", "--url", url, "--mode", "a2a", user_input, "-v"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Parse consecutive JSON blocks from stdout
        text = result.stdout
        agent_response = "No response from agent."
        decoder = json.JSONDecoder()
        pos = 0
        
        start_idx = text.find("{")
        if start_idx != -1:
            text = text[start_idx:]
            
        while pos < len(text):
            text = text[pos:].lstrip()
            if not text:
                break
            try:
                data, index = decoder.raw_decode(text)
                pos = index
                
                if "update" in data and "status" in data["update"]:
                    status = data["update"]["status"]
                    if "message" in status and status["message"].get("role") == "agent":
                        parts = status["message"].get("parts", [])
                        if parts:
                            if "text" in parts[0]:
                                agent_response = parts[0]["text"]
                            elif "data" in parts[0] and "args" in parts[0]["data"]:
                                agent_response = parts[0]["data"]["args"].get("message", "")
            except json.JSONDecodeError:
                break
                
        return {"outputs": {"output": agent_response}}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Proxy failed: {e.stderr}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proxy failed: {e}")

# Mount static files at the root
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
