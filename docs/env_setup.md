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

## 3. Testing
To run the full unit and integration test suite inside the agent's virtual environment:
```bash
mwis-agent/.venv/bin/pytest mwis-agent/
```
