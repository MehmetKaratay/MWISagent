# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- **2026-07-05 12:57**: Implemented strict input validation (Pydantic schemas), XML prompt isolation, security skill guidelines (`.agents/skills/security/SKILL.md`), and automated test suite in `tests/test_security.py`.
- **2026-07-05 00:15**: Implemented `parse_forecast.py` HTML to JSON parser using BeautifulSoup, with comprehensive tests and mocked requests.
- **2026-07-04 22:44**: Implemented `query_fl.py` and `query_refHeight.py` CLI utilities with strict CSV schema validations.

### Changed
- **2026-07-05 15:25**: Refactored all CLI scripts to expose programmatic functions for imports, while preserving full command-line interfaces.
- **2026-07-05 13:33**: Migrated dependency and packaging configuration from `requirements.txt` to `pyproject.toml` (using setuptools backend) and updated documentation.
- **2026-07-05 13:13**: Reorganized the security skill into a dedicated `input_validation` folder under `.agents/skills/security/input_validation/` using git mv, and updated all code, tests, and documentation references.
- **2026-07-04 13:06**: Implemented `query_date.py` date resolver script with `parsedatetime` library and 12 unit tests.
- **2026-07-04 13:06**: Created `requirements.txt` to manage Python dependencies.
- **2026-07-04 12:22**: Recreated virtual environment `.venv` with working Python 3.10 and `pyproj` library to fix test errors.
