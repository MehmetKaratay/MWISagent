# Frontend Integration Specification

This specification details the frontend integration requirements for the MWIS Agent.

---

### SECTION 1: SPEC

**One-line purpose**
Provides a secure, streaming API endpoint that allows a web-based chat frontend to interact with the MWIS agent while maintaining conversation history.

**Users and use cases**
- As a frontend developer, I want clear API endpoints and schemas so that I can build a chat UI connected to the MWIS agent.
- As an end-user, I want the agent's responses to stream word-by-word so that the interface feels fast and modern.
- As a system administrator, I want API access secured via OAuth so that malicious actors cannot spam the LLM and incur massive billing costs.

**Requirements**
1. The backend must expose a Server-Sent Events (SSE) streaming endpoint for agent chat.
2. The frontend must implement OAuth authentication (via Google Identity Platform or Firebase Auth).
3. The frontend must pass a valid JWT token in the `Authorization: Bearer` header.
4. The backend must reject unauthorized requests (401).
5. The frontend must generate and maintain a unique UUID (`session_id`) per chat session.
6. The backend must support Cross-Origin Resource Sharing (CORS) configured strictly for the frontend's deployment URL in GCP `europe-west2`.

**Edge cases**
- **Token expiration:** The frontend's JWT token expires mid-session. Expected behavior: Backend returns 401 Unauthorized; frontend catches it, refreshes the token, and retries.
- **Malformed Markdown:** The LLM returns unexpectedly formatted markdown. Expected behavior: The frontend markdown parser gracefully falls back to plain text or safely renders it without breaking the UI.

**Acceptance criteria**
```
Given a user logged into the frontend with a valid OAuth token
When they send a message to the agent's stream endpoint
Then the response streams back token-by-token and renders in Markdown

Given a request without a valid Authorization header
When it hits the backend API
Then the API returns a 401 Unauthorized error

Given an existing chat session UUID
When the user sends a follow-up message with the same session_id
Then the agent recalls the context of the previous message
```

---

### SECTION 2: PLAN

**Stack and architecture**
- **Backend:** FastAPI, Python 3.10, ADK (Agent Development Kit). Hosted on Google Cloud (`europe-west2`).
- **Frontend:** Alpine.js (as per CONTEXT.md). Hosted on Google Cloud.
- **Auth:** Google Identity Platform / Firebase Authentication.

**Data model changes**
No database schema changes required. The session memory is handled internally by ADK's `session_service`.

**API contracts**
- `POST /a2a/app/stream`
  - **Inputs:** JSON body with `message.text` and `session_id`. `Authorization: Bearer <jwt>`.
  - **Outputs:** Server-Sent Events stream (JSON-encoded chunks).
  - **Errors:** 401 Unauthorized (Invalid token), 400 Bad Request (Missing fields).

**Patterns to follow**
- RESTful API principles for error handling.
- Standard FastAPI CORS middleware configuration.

**Testing strategy**
- **Unit tests:** Not applicable for frontend integration.
- **Integration tests:** End-to-end testing of the `/a2a/app/stream` endpoint with a mocked JWT token.
- **Manual QA:** Ensure the UI correctly streams the text without visual jumping or markdown parsing failures.

**Security and performance constraints**
- **Authentication:** Strict OAuth enforcement.
- **CORS:** Must match exact frontend domain.
- **Rate Limits:** Cloud API Gateway should enforce requests-per-minute limits to prevent DoS.

---

### SECTION 3: TASKS

## Task 1: Enforce OAuth on Backend API

**What to build:** Add a FastAPI dependency to validate JWT tokens on the `/a2a/app/message` and `/a2a/app/stream` endpoints.
**Files likely affected:** `mwis-agent/app/fast_api_app.py`
**Acceptance criteria:**
1. Requests without an `Authorization` header return 401.
2. Requests with an invalid token return 401.
3. Requests with a valid Google Identity token proceed normally.
**Dependencies:** none

## Task 2: Configure CORS for GCP

**What to build:** Update the `.env` or deployment pipeline to set `ALLOW_ORIGINS` to the exact frontend URL hosted in `europe-west2`.
**Files likely affected:** `.env`, CI/CD pipelines.
**Acceptance criteria:**
1. The backend accepts preflight `OPTIONS` requests from the frontend domain.
2. The backend rejects CORS requests from unrelated domains.
**Dependencies:** Task 1

## Task 3: Build the Frontend Chat Interface (Alpine.js)

**What to build:** The web UI with a chat input, message history, and a streaming fetch reader for the SSE endpoint.
**Files likely affected:** Frontend HTML/JS files (not in backend repo yet).
**Acceptance criteria:**
1. Generates and stores a unique UUID `session_id`.
2. Sends the JWT token in the Authorization header.
3. Streams the response chunks into a Markdown-rendered chat bubble.
**Dependencies:** Task 1, Task 2

**Review checkpoint:** Before handing this off, verify that the Google Identity Platform project is created and the JWKS endpoint is available for the backend to validate tokens against.

---

## Assumptions to review

1. [ASSUMPTION: We are implementing the JWT validation inside the FastAPI application code rather than relying entirely on Cloud API Gateway for auth validation.] — Impact: HIGH
   Correct this if: You plan to offload all authentication to an external API Gateway and leave the FastAPI app unauthenticated internally.
2. [ASSUMPTION: The frontend is built with Alpine.js as per the CONTEXT.md] — Impact: MEDIUM
   Correct this if: The frontend stack has changed to React/Vue/etc.
