# Makefile Specification

This specification defines the repository automation scripting targets configured in the project `Makefile`.

```yaml
name: makefile_spec
summary: Specifications for Makefile targets to handle local execution, cloud configuration, and validation checks.
targets:
  - name: eval
    description: Runs the automated evaluation generation and grading pipeline.
  - name: playground
    description: Launches the interactive agents-cli developer playground.
  - name: local_deploy
    description: Automatically starts the FastAPI backend (port 8080) and Python server (port 8000) concurrently in the background.
  - name: kill_local_deploy
    description: Cleanly terminates port bindings on port 8080 and port 8000.
  - name: setup_gcloud
    description: Configures the mwis configuration, project settings, CLI login, and ADC quota project using PROJECT_ID.
  - name: cloud_deploy
    description: Runs verification linters and tests with warnings treated as errors, then deploys to Vertex AI Agent Runtime.
  - name: cloud_deploy_dev
    description: Deploys the backend agent first, then builds and deploys the containerized frontend dashboard to Cloud Run.
```

## Behavior & Technical Requirements

### 1. Variables
- `PROJECT_ID`: Extracted dynamically at Makefile initialization from `.env` using `PROJECT_ID := $(shell grep '^PROJECT_ID=' .env | cut -d= -f2)`.

### 2. Targets

#### `eval`
- Runs `agents-cli eval generate --dataset tests/eval/datasets/mwis_eval.json` under `MWIS_ENV=development`.
- Sequentially runs `agents-cli eval grade`.

#### `playground`
- Runs `agents-cli playground` under `MWIS_ENV=development`.

#### `local_deploy`
- Runs backend FastAPI server in the background: `MWIS_ENV=development INTEGRATION_TEST=TRUE uv run uvicorn app.fast_api_app:app --host 127.0.0.1 --port 8080 > backend.log 2>&1 &`
- Runs frontend server in the background: `MWIS_ENV=development uv run python frontend/server.py > frontend.log 2>&1 &`
- Pauses briefly and echos: `Frontend URL: http://localhost:8000`.

#### `kill_local_deploy`
- Kills port 8080: `fuser -k 8080/tcp || true`
- Kills port 8000: `fuser -k 8000/tcp || true`

#### `setup_gcloud`
- Asserts `PROJECT_ID` is present in `.env`.
- Activates configuration profile `mwis` (creating it if missing).
- Configures active project to `PROJECT_ID` and region to `europe-west2`.
- Executes CLI login (`gcloud auth login`) and Application Default Credentials login (`gcloud auth application-default login`).
- Sets local ADC quota project to `PROJECT_ID`.
- Enables the Cloud Resource Manager API (`gcloud services enable cloudresourcemanager.googleapis.com`) to prevent Vertex AI Agent Runtime 500 startup crashes.

#### `cloud_deploy`
- Sequentially runs pre-deployment checks, stopping immediately if any step exits non-zero:
  1. `uvx pre-commit run --all-files`
  2. `uv run --env-file .env pytest -W error -W ignore::DeprecationWarning -W ignore::UserWarning -W ignore::starlette.util.StarletteDeprecationWarning tests/unit tests/integration`
  3. `agents-cli deploy --project $(PROJECT_ID) --no-confirm-project`

#### `cloud_deploy_dev`
- Depends on `cloud_deploy`.
- Asserts `PROJECT_ID` is present in `.env`.
- Extracts `remote_agent_runtime_id` from the updated `deployment_metadata.json`.
- Runs `gcloud run deploy mwis-agent-dashboard` pointing to the root workspace directory with the `GOOGLE_CLOUD_PROJECT` and `AGENT_RUNTIME_ID` environment variables configured to build and deploy the containerized frontend to Cloud Run.
