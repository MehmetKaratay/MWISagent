---
name: frontend
description: Basic front end for MWISagent using Alpine.js and Vanilla CSS, including a local dev server.
---

# Frontend Specification

A basic web frontend to provide an interactive chat experience with the MWISagent, alongside development dialogs for querying region and date scripts directly.

## SECTION 1: SPEC

**Users and use cases**
- As an end user, I want to chat with the MWISagent to get weather forecasts.
- As a developer, I want to input a location and see the direct output of `query_region.py` so I can verify the script behavior.
- As a developer, I want to input a date and see the direct output of `query_date.py` so I can verify the script behavior.

**Requirements**
1. Front end must be located entirely in `MWISagent/frontend/`.
2. Existing backend code in `MWISagent/app/` must not be touched.
3. Chat box must communicate with the agent backend via A2A protocol.
4. Two development dialogs must exist to query region and date.
5. The UI must use Vanilla CSS with a modern, sleek design (vibrant colors, dark mode support, glassmorphism, dynamic animations).
6. The UI must use a single `<h1>` element.
7. Must use Alpine.js for logic.

**Edge cases**
- ADK Backend is down: The chat should display a clear connection error.
- Script execution fails: The dev dialogs should display the error output.

**Acceptance criteria**
Given the ADK backend is running
When a user sends a message in the chat box
Then the message is sent to the backend and the response is displayed

Given the frontend dev server is running
When a developer enters a location in the region dialog
Then the output of `query_region.py` is displayed in the dialog

Given the frontend dev server is running
When a developer enters a date in the date dialog
Then the output of `query_date.py` is displayed in the dialog

## SECTION 2: PLAN

**Stack and architecture**
- **Core:** HTML and Javascript (Alpine.js).
- **Styling:** Vanilla CSS.
- **Frontend Server:** Lightweight Python FastAPI server (`frontend/server.py`) to serve static files and expose script endpoints. *(Note: This local server proxy is a temporary solution for MVP development; in the future, these scripts should be exposed as proper API calls from the main backend.)*

**Data model changes**
- None.

**API contracts**
- `GET /` (Frontend Server): Serves `index.html`.
- `GET /api/query_region?q={location}` (Frontend Server): Executes `query_region.py` via subprocess and returns JSON output.
- `GET /api/query_date?q={date}` (Frontend Server): Executes `query_date.py` via subprocess and returns JSON output.
- `POST /a2a/mwis-agent` (ADK Backend): Existing A2A chat endpoint.

**Testing strategy**
- Manual verification of UI interactions and backend communication.

## SECTION 3: TASKS

## Task 1: Create Frontend Dev Server
- **Description:** Implement `frontend/server.py` using FastAPI to serve static files and provide `/api/query_region` and `/api/query_date` endpoints via `subprocess.run`.
- **Validation:** Running `python frontend/server.py` starts a server on port 8000 that responds to the script endpoints.

## Task 2: Create Static UI Layout & Styling
- **Description:** Create `frontend/static/index.html` with Alpine.js CDN and `frontend/static/styles.css` with a premium glassmorphic design. Include the chat UI and hidden dialogs.
- **Validation:** Accessing `http://localhost:8000` displays the styled UI correctly.

## Task 3: Implement Alpine.js Logic
- **Description:** Create `frontend/static/app.js` with Alpine.js data objects to handle chat messaging (calling `http://localhost:8080/a2a/mwis-agent`) and dialog submissions (calling `/api/...`).
- **Validation:** Chat messages receive responses from the ADK agent, and dialogs return script outputs.
