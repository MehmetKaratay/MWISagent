# Local Environment Setup Guide

Follow these steps to replicate the sandbox environment for the MWIS Weather Agent project.

---

## 1. Parent Repository Setup
The parent repository holds custom skills, specifications, and shared utilities.

* **Python Requirement:** Python >= 3.10
* **Setup Commands:**
  ```bash
  # Ensure you are at the repository root
  uv pip install -e .
  ```

---

## 2. ADK Agent App Setup (Inside `mwis-agent/`)
The interactive agent resides in the `mwis-agent/` sub-directory and runs in an isolated virtual environment.

* **Python Requirement:** Python >= 3.11 (Python 3.13 is recommended)
* **Setup Commands:**
  ```bash
  cd mwis-agent
  # Run the installer with an increased timeout for slow downloads
  UV_HTTP_TIMEOUT=1200 uvx google-agents-cli install
  ```

---

## 3. Environment Variables
Create a `.env` file inside the `mwis-agent/` directory with the following variables:

* **`GEMINI_API_KEY`**: (Required) Your Gemini API key for the LLM.
* **`GOOGLE_OAUTH_CLIENT_ID`**: (Required for API) The Google OAuth Client ID to explicitly validate the audience of incoming JWT tokens on the FastAPI server endpoints.
* **`ALLOW_ORIGINS`**: (Optional) Comma-separated list of allowed frontend domains for CORS in production.

---

## 4. Testing & Evaluation
You do **not** need to manually activate a virtual environment when running tests from a standard terminal. Our commands leverage `uv run` to automatically execute inside the isolated `.venv`.

* **Unit & Integration Tests:**
  ```bash
  mwis-agent/.venv/bin/pytest mwis-agent/
  ```
* **Automated Agent Evaluation:**
  ```bash
  make eval
  ```
  *Note on Rate Limits:* Running `make eval` executes multiple agent trajectories against the Gemini API. If using a **Free Tier** API key (`GEMINI_API_KEY`), you are limited to 5 requests per minute (RPM), which may cause `429 RESOURCE_EXHAUSTED` errors during multi-case evaluation runs. See [docs/evaluation.md](file:///home/karatay/Repositories/weather/MWISagent/docs/evaluation.md#troubleshooting--environment-setup) for workarounds and billing setup instructions.
