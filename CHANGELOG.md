# Changelog

## [Unreleased]
### Fixed
- Fixed 401 Unauthorized A2A errors between the frontend dashboard and backend Reasoning Engine by allowing token verification to fall back to general Google signature validation without audience restriction when configured placeholder is not present.
- Fixed live deployment HTTP 500 startup crash by enabling the Cloud Resource Manager API in the GCP project configuration, and updated the `setup_gcloud` target in the `Makefile` to automatically enable it in the future.
- Fixed Ruff C414 lint error (unnecessary list call in sorted()) in `app/agent_logic.py`.
- Fixed Ruff B904 lint errors (missing exception chaining from e) in `frontend/server.py`.
- Fixed missing Semgrep dependency on local pre-commit check environments by adding `"semgrep"` to optional dependencies in `pyproject.toml`.
- Fixed cache population issue by bypassing the scheduler check when the database contains fewer than 10 entries (incomplete or empty cache).
- Fixed mock forecast cache ingestion by dynamically rewriting static dates based on environment (`MWIS_ENV=development` and `test-new-dcode`).
- Fixed region resolution in `agent_logic.py` to correctly map specific locations (like "Ben Nevis") using `query_region.py`, defaulting to "Unknown" when out of scope.
- Added `google-agents-cli` to `pyproject.toml` dependencies.
- Fixed 500 Internal Server Error in the frontend `/api/chat` route by replacing the legacy Reasoning Engine adapter with an `agents-cli run --mode a2a` wrapper, properly aligning with ADK AgentEngine interfaces.
- Fixed `agents-cli run` failing in Cloud Run by copying `agents-cli-manifest.yaml` in the Dockerfile.
- Made the mock HTML strings strictly pass the validator tests without requiring an `html5lib` parser explicitly in tests.
- Fixed `TypeError` in `query_region.py` when outputting nearest regions in JSON format for out-of-bounds locations (e.g. London).

### Changed
- Refactored multiple long functions in `query_region.py` into helper functions under 15 lines with descriptive names and docstrings to satisfy clean code standards.
- Refactored `check_forecast_issued` in `check_forecast.py` into helper functions under 15 lines with descriptive names and docstrings.
- Replaced hardcoded `10` region count magic number with dynamic `len(get_all_region_codes())`.

### Added
- Added a local `local-names.csv` fallback query mechanism to `query_region.py` enabling fast local resolution of region codes for name lookups not present in primary third-party or munros databases.
- Added guide on setting up and running git pre-commit quality checks (Ruff linter/formatter and Semgrep scan) in `docs/env_setup.md`.
- Created `tests/eval/datasets/mwis_eval.json` with 4 test scenarios (direct, ambiguous, location out-of-scope, date out-of-scope).
- Configured ADK built-in evaluation metrics in `tests/eval/eval_config.yaml`.
- Added a `Makefile` with `eval`, `playground`, `local_deploy`, `kill_local_deploy`, and `setup_gcloud` targets.

All notable changes to this project will be documented in this file.

## [Unreleased]
### Added
- Implemented strict CORS policy enforcing exact origin matching and forbidding wildcards (`*`) via the `ALLOW_ORIGINS` environment variable.
- Added `OAuthJWTValidationMiddleware` to enforce Google OAuth JWT validation on A2A execution endpoints.
- Bypass authentication for `.well-known/agent-card` and other public endpoints.
- TDD unit tests for the OAuth middleware.
- [Frontend] Hybrid API proxy in `server.py` (`/api/chat`) to securely connect the frontend to the deployed remote Reasoning Engine using the Vertex AI SDK.
- [Frontend] Updated root `Dockerfile` to include the `frontend/` directory, allowing it to be deployed as a containerized dashboard alongside the backend `app/`.

### Changed
- Updated all non-Apache project files to use the Creative Commons Attribution-ShareAlike 4.0 International License (CC-BY-4.0).
- Refactored `fast_api_app.py` to extract `OAuthJWTValidationMiddleware` into `auth_middleware.py` and CORS configuration into `cors_config.py`, improving modularity without altering external behavior.
- Implemented Prompt Injection Defense (XML tag wrapping and system prompt rules).
- Integrated `is_malicious` state tracking. in `ParseOutput`. Added `check_security` router and `security_refusal` nodes to the workflow graph.
- Configured backend caching architecture to store 10 MWIS forecasts locally to avoid multiple redundant downstream API calls and support lazy-loading.
- **2026-07-06 23:07**: Implemented Agent multi-region forecast comparison logic (up to 5 regions), adding missing location/date routing nodes and integrating the `query_country.py` guardrail.
- **2026-07-06 19:14**: Implemented ADK 2.0 Graph Workflow in `mwis-agent/app/agent.py` to route user queries through physical weather, impact, and local knowledge nodes with a follow-up HITL loop.
- **2026-07-06 15:52**: Created check_forecast_issued weather agent caching system utilizing transactional SQLite storage and BST-aware scheduling rules, clean-code refactored into sub-15-line functions.
- **2026-07-05 20:25**: Updated `serve_forecast_to_user/SKILL.md` and `specs/query_date.spec.md` to use calendar-date calibration rather than system-clock time calibration.
- **2026-07-05 19:30**: Created `forecast_structure.json` to act as the schema reference representation for the daily JSON forecasts.
- **2026-07-05 18:22**: Renamed the forecast JSON field `cold_temp` to `temp` across all codebase files, specifications, references, and documentation.
- **2026-07-05 18:10**: Split `precipitation` into `precip_headline`/`precip_detail` and `cloud_hills` into `cloud_headline`/`cloud_detail` based on dual paragraph tag extraction in parsed HTML files.
- **2026-07-05 12:57**: Implemented strict input validation (Pydantic schemas), XML prompt isolation, security skill guidelines (`.agents/skills/security/SKILL.md`), and automated test suite in `tests/test_security.py`.
- **2026-07-05 00:15**: Implemented `parse_forecast.py` HTML to JSON parser using BeautifulSoup, with comprehensive tests and mocked requests.
- **2026-07-04 22:44**: Implemented `query_fl.py` and `query_refHeight.py` CLI utilities with strict CSV schema validations.

### Changed
- **2026-07-07 01:04**: Audited the codebase and injected over 75 missing Google-style docstrings into functions and classes across `app/` and `tests/` directories using an AST-parsing script, satisfying P3 clean code requirements without modifying interpreted code.
- **2026-07-06 23:50**: Refactored monolithic `mwis-agent/app/agent.py` into modular files (`agent_state.py`, `agent_logic.py`, `agent_nodes.py`) adhering to Clean Code principles. Extracted complex logic into sub-15-line functions and added Google-style docstrings across all agent files.
- **2026-07-06 19:07**: Fixed caching logic in `mwis-agent/app/skills/mwis-website/check_forecast_issued/scripts/mwis_cache_db.py` to correctly extract `last_updated` from the first day array element instead of root JSON.
- **2026-07-05 23:14**: Refactored CLI utility scripts to clean up type hints, simplify python duplicate removal/set conversions, and use robust subprocess arguments passing.
- **2026-07-05 15:25**: Refactored all CLI scripts to expose programmatic functions for imports, while preserving full command-line interfaces.
- **2026-07-05 13:33**: Migrated dependency and packaging configuration from `requirements.txt` to `pyproject.toml` (using setuptools backend) and updated documentation.
- **2026-07-05 13:13**: Reorganized the security skill into a dedicated `input_validation` folder under `.agents/skills/security/input_validation/` using git mv, and updated all code, tests, and documentation references.
- **2026-07-04 13:06**: Implemented `query_date.py` date resolver script with `parsedatetime` library and 12 unit tests.
- **2026-07-04 13:06**: Created `requirements.txt` to manage Python dependencies.
- **2026-07-04 12:22**: Recreated virtual environment `.venv` with working Python 3.10 and `pyproj` library to fix test errors.
