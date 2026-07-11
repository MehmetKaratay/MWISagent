# Makefile Commands Reference

This document describes the scripting and automation targets defined in the project `Makefile`.

## Environment Configuration

The Makefile dynamically reads configuration variables from the local `.env` file in the repository root:
* **`PROJECT_ID`**: The Google Cloud Project ID (e.g. `gen-lang-client-0123456789`) used by authentication and deployment targets.
* **`MWIS_ENV`**: Set to `development` to force the agent to use local offline mocks instead of live fetches during local testing.

Make sure these variables are defined in your local `.env` file before executing environment setup or deployment commands.

---

## Command Reference

### Local Development & Testing

#### `make eval`
Synthesizes multi-turn evaluation datasets and grades the agent's performance against the configured metrics. Runs in development mock mode (`MWIS_ENV=development`).

#### `make playground`
Launches the interactive local command-line developer playground to chat directly with your agent. Runs in development mock mode (`MWIS_ENV=development`).

#### `make local_deploy`
Deploys the application locally by concurrently starting the FastAPI backend API on port 8080 and the static HTML mock frontend server on port 8000 in the background.

#### `make kill_local_deploy`
Safely stops the local background servers by forcefully releasing socket bindings on port 8080 and port 8000.

---

### Cloud Integration & Deployment

#### `make setup_gcloud`
Configures your local Google Cloud SDK to target the project defined by `PROJECT_ID` in `.env`:
1. Creates or switches to a dedicated `mwis` configuration profile.
2. Sets the active project and default region (`europe-west2`).
3. Launches the web login prompts for the `gcloud` CLI and Application Default Credentials (ADC).
4. Configures the local ADC quota project to resolve potential billing or quota conflicts.

#### `make cloud_deploy`
Safely validates and deploys the agent to Vertex AI Agent Runtime:
1. **Pre-deployment Linter Audits:** Runs `pre-commit` quality checks (Ruff formatting and Semgrep security scan).
2. **Pre-deployment Verification:** Runs the complete unit and integration test suite with warnings treated as errors.
3. **Deployment:** Executes the live deployment command if all validation steps pass cleanly. If any step fails, execution halts immediately and the deployment is cancelled.
