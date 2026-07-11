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
