---
name: frontend
description: Frontend for MWISagent using Alpine.js and Vanilla CSS, running as a hybrid Cloud Run service with an API chat proxy.
---

# Frontend Specification

A web frontend to provide an interactive chat experience with the MWISagent via a remote Reasoning Engine API proxy, alongside development dialogs for querying region and date scripts locally.

## SECTION 1: SPEC

**Users and use cases**
- As an end user, I want to chat with the MWISagent to get weather forecasts.
- As a developer, I want to input a location and see the direct output of `query_region.py` so I can verify the script behavior.
- As a developer, I want to input a date and see the direct output of `query_date.py` so I can verify the script behavior.

**Requirements**
1. Front end must be located entirely in `MWISagent/frontend/`.
2. Existing backend code in `MWISagent/app/` must not be touched.
3. Chat box must communicate with the remote Agent Runtime via a secure `/api/chat` proxy endpoint on the frontend server.
4. Two development dialogs must exist to query region and date using local scripts.
5. The UI must clearly indicate the development dialogs are for testing purposes.
6. The UI must use Vanilla CSS with a modern, sleek design (vibrant colors, dark mode support, glassmorphism, dynamic animations).
7. Must use Alpine.js for logic.
8. The Development Tools sidebar must only be displayed in the UI when the environment variable `MWIS_ENV` is set to `'development'`. If set to `'production'` (or any other value), it should be hidden.

**Edge cases**
- Agent Runtime is down or inaccessible: The chat should display a clear connection error.
- Script execution fails: The dev dialogs should display the error output.

**Acceptance criteria**
```
Given the frontend is deployed to Cloud Run
When a user sends a message in the chat box
Then the frontend server proxies the request to the remote Agent Runtime and returns the response

Given the frontend is deployed to Cloud Run
When a developer enters a location in the region dialog
Then the output of the local `query_region.py` is displayed in the dialog

Given the frontend is deployed to Cloud Run
When a developer enters a date in the date dialog
Then the output of the local `query_date.py` is displayed in the dialog
```

## SECTION 2: PLAN

**Stack and architecture**
- **Core:** HTML and Javascript (Alpine.js).
- **Styling:** Vanilla CSS.
- **Frontend Server:** Python FastAPI server (`frontend/server.py`) serving static files. It acts as an API gateway for chat (via `google-cloud-aiplatform` SDK) and a local executor for Dev Tools.
- **Deployment:** A single Cloud Run container built from the root `Dockerfile`, copying both `app/` and `frontend/`, overriding the entrypoint to start `frontend.server:app`.

**API contracts**
- `GET /` (Frontend Server): Serves `index.html`.
- `GET /api/config` (Frontend Server): Returns `{"mwis_env": "development" | "production"}`.
- `POST /api/chat` (Frontend Server): Accepts JSON `{ "inputs": { "input": "..." } }`, calls `ReasoningEngine.query()`, returns agent response.
- `GET /api/query_region?q={location}` (Frontend Server): Executes `query_region.py` via subprocess and returns JSON output.
- `GET /api/query_date?q={date}` (Frontend Server): Executes `query_date.py` via subprocess and returns JSON output.

**Testing strategy**
- Manual verification of UI interactions and remote backend communication.

## SECTION 3: TASKS

## Task 1: Create API Chat Proxy
- **What to build:** Add a `POST /api/chat` endpoint in `frontend/server.py` that uses a `subprocess.run(["agents-cli", "run", "--mode", "a2a"])` wrapper to query the remote Agent Runtime using `AGENT_RUNTIME_ID`. Add `google-agents-cli` to dependencies.
- **Files likely affected:** `frontend/server.py`, `pyproject.toml`
- **Acceptance criteria:** Sending a POST request to `/api/chat` successfully returns a response from the deployed Agent Runtime via the CLI wrapper.
- **Dependencies:** none

## Task 2: Update Frontend Chat Logic
- **What to build:** Update `frontend/static/app.js` to send chat messages to `/api/chat` instead of the hardcoded local A2A endpoint.
- **Files likely affected:** `frontend/static/app.js`
- **Acceptance criteria:** Chat messages sent from the UI hit the new proxy endpoint and render correctly.
- **Dependencies:** Task 1

## Task 3: Update Container Configuration
- **What to build:** Update the root `Dockerfile` to copy the `frontend/` directory into the container, so it can be deployed to Cloud Run alongside the `app/` directory. Also, `agents-cli-manifest.yaml` and `deployment_metadata.json` must be copied so the `agents-cli` wrapper functions properly.
- **Files likely affected:** `Dockerfile`
- **Acceptance criteria:** `Dockerfile` includes `COPY ./frontend ./frontend` and copies `agents-cli-manifest.yaml`.
- **Dependencies:** none
