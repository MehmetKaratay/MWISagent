PROJECT_ID := $(shell grep '^PROJECT_ID=' .env | cut -d= -f2)

.PHONY: eval
eval:
	MWIS_ENV=development uv run --env-file .env agents-cli eval generate --dataset tests/eval/datasets/mwis_eval.json
	uv run --env-file .env agents-cli eval grade

.PHONY: playground
playground:
	MWIS_ENV=development uv run --env-file .env agents-cli playground

.PHONY: local_deploy
local_deploy:
	@echo "Starting backend..."
	@MWIS_ENV=development INTEGRATION_TEST=TRUE uv run --env-file .env uvicorn app.fast_api_app:app --host 127.0.0.1 --port 8080 > backend.log 2>&1 &
	@echo "Starting frontend..."
	@MWIS_ENV=development uv run --env-file .env python frontend/server.py > frontend.log 2>&1 &
	@sleep 2
	@echo "Local deployment started!"
	@echo "Frontend URL: http://localhost:8000"

.PHONY: kill_local_deploy
kill_local_deploy:
	@echo "Stopping backend on port 8080..."
	@fuser -k 8080/tcp || true
	@echo "Stopping frontend on port 8000..."
	@fuser -k 8000/tcp || true
	@echo "Local deployment stopped."

.PHONY: setup_gcloud
setup_gcloud:
	@if [ -z "$(PROJECT_ID)" ]; then echo "Error: PROJECT_ID not set in .env"; exit 1; fi
	@echo "Setting up gcloud for project $(PROJECT_ID)..."
	@gcloud config configurations activate mwis 2>/dev/null || gcloud config configurations create mwis
	gcloud config set project $(PROJECT_ID)
	gcloud config set run/region europe-west2
	gcloud auth login
	gcloud auth application-default login
	gcloud auth application-default set-quota-project $(PROJECT_ID)
	gcloud services enable cloudresourcemanager.googleapis.com

.PHONY: cloud_deploy
cloud_deploy:
	@echo "Running pre-deployment validation checks..."
	uvx pre-commit run --all-files
	uv run --env-file .env pytest -W error -W ignore::DeprecationWarning -W ignore::UserWarning -W ignore::starlette.util.StarletteDeprecationWarning tests/unit tests/integration
	@echo "Deploying to live Google Cloud Agent Runtime..."
	@if [ -z "$(PROJECT_ID)" ]; then echo "Error: PROJECT_ID not set in .env"; exit 1; fi
	agents-cli deploy --project $(PROJECT_ID) --no-confirm-project
