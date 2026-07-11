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

## 2. ADK Agent App Setup
The interactive agent application resides at the repository root (with core agent logic and graph code located in the `app/` directory) and runs in an isolated virtual environment.

* **Python Requirement:** Python >= 3.11 (Python 3.13 is recommended)
* **Setup Commands:**
  ```bash
  # Run the installer with an increased timeout for slow downloads
  UV_HTTP_TIMEOUT=1200 uvx google-agents-cli install
  ```

---

## 3. Environment Variables
Create a `.env` file inside the repository root directory with the following variables:

* **`GEMINI_API_KEY`**: (Required) Your Gemini API key for the LLM.
* **`GOOGLE_OAUTH_CLIENT_ID`**: (Required for API) The Google OAuth Client ID to explicitly validate the audience of incoming JWT tokens on the FastAPI server endpoints.
  * **Fallback Validation**: If verification against this client ID fails (e.g., for service-to-service calls using metadata service accounts where the audience is set to the service's own URL), validation falls back to verifying Google signatures without audience constraint (`audience=None`) to avoid 401 Unauthorized blockages in staging.
* **`ALLOW_ORIGINS`**: (Required for CORS) Comma-separated list of allowed frontend domains.
  * **No Wildcards**: Wildcard (`*`) origins are strictly forbidden by the backend to prevent CSRF-style attacks.
  * **Local Development**: You must explicitly define your local origins. Set this to: `http://localhost:8080,http://127.0.0.1:8080`
  * **Production (Future)**: When you deploy your frontend to Cloud Run in `europe-west2`, you can retrieve its domain using `gcloud run services describe <FRONTEND_SERVICE_NAME> --region europe-west2 --format="value(status.url)"` and add it to this variable.
* **`MWIS_ENV`**: Set to `development` to enable local offline HTML mock ingestion instead of fetching live weather pages.
* **`INTEGRATION_TEST`**: Set to `TRUE` to bypass authentication/OAuth JWT checks for local testing.
* **`PROJECT_ID`**: (Required for Cloud SDK config) Your Google Cloud Project ID (e.g. `gen-lang-client-0123456789`) used by automated scripts to authenticate and configure gcloud environments.

---

## 4. Testing & Evaluation
You do **not** need to manually activate a virtual environment when running tests from a standard terminal. Our commands leverage `uv run` to automatically execute inside the isolated `.venv`.

* **Unit & Integration Tests:**
  ```bash
  uv run pytest tests/unit tests/integration
  ```
* **Automated Agent Evaluation:**
  ```bash
  make eval
  ```
  *Note on Rate Limits:* Running `make eval` executes multiple agent trajectories against the Gemini API. If using a **Free Tier** API key (`GEMINI_API_KEY`), you are limited to 5 requests per minute (RPM), which may cause `429 RESOURCE_EXHAUSTED` errors during multi-case evaluation runs. See [docs/evaluation.md](file:///home/karatay/Repositories/weather/MWISagent/docs/evaluation.md#troubleshooting--environment-setup) for workarounds and billing setup instructions.
* **Google Cloud SDK Configuration:**
  Ensure you have defined `PROJECT_ID` in your `.env` file, then run the configuration target to set up your local `gcloud` active configuration profile and authenticate Application Default Credentials (ADC):
  ```bash
  make setup_gcloud
  ```

---

## 5. Pre-commit Quality Checks (Required on Fresh Install)
To ensure code styling and security policies are maintained, the repository is configured with git hooks using `pre-commit`. These hooks run the following tools automatically before every commit:
- **`end-of-file-fixer`** and **`trailing-whitespace`** to clean up text formats.
- **`ruff`** linter and formatter to check code quality and conventions.
- **`semgrep`** (Custom Local Security Scan) using local rules to run static analysis security checks.

### Setup Git Hooks:
On a fresh install, run the following commands to synchronize workspace tools/dependencies and register the git hook wrappers:
```bash
# Sync all workspace dependencies (including dev and linting tools)
uv sync --extra lint

# Register the git hooks
uvx pre-commit install
```

### Manual Verification:
You can run the checks manually on all files at any time:
```bash
uvx pre-commit run --all-files
```
