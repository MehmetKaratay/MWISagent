# Automated Agent Evaluation

This project uses the Agent Development Kit (ADK) evaluation framework to test the MWIS agent's routing and response quality deterministically.

## Overview

The evaluation pipeline is defined in two key places:
- **Dataset (`mwis-agent/tests/eval/datasets/mwis_eval.json`)**: Contains the test scenarios (direct query, ambiguous query, out-of-scope location, out-of-scope date).
- **Configuration (`mwis-agent/tests/eval/eval_config.yaml`)**: Defines the metrics used to grade the agent (task success, trajectory quality, response quality, and turn count).

## Running the Tests

To minimise token usage and ensure tests are deterministic, we use static HTML caches of the MWIS website. You must trigger these tests manually.

From the root of the repository, run:
```bash
make eval
```

### Prerequisites
1. **API Key**: You must have a `GEMINI_API_KEY` defined in `mwis-agent/.env`.
2. **Google Cloud Credentials**: The ADK evaluation framework relies on Vertex AI evaluation SDKs. You must have your local application default credentials configured. If you haven't done this, run:
   ```bash
   gcloud auth application-default login
   ```

### What happens when you run the tests?
1. **Generate**: The CLI generates a conversation trajectory for each test case in the dataset. Because the `make eval` target passes `MWIS_ENV=development`, the agent will use static HTML dumps rather than performing live web fetches.
2. **Grade**: The CLI uses the Gemini API as an LLM judge to grade the generated trajectories against the metrics defined in `eval_config.yaml`.
3. **Report**: You can view the final grading results as an HTML report inside the `mwis-agent/artifacts/grade_results/` directory.

---

## Troubleshooting & Environment Setup

### Running from a Terminal (Virtual Environment Isolation)
You do **not** need to manually activate a virtual environment (`source .venv/bin/activate`) before running `make eval`. The `Makefile` invokes `uv run`, which automatically locates, manages, and executes all commands inside the isolated virtual environment (`mwis-agent/.venv`). You only need `uv` and `make` installed on your system PATH.

### Resolving `429 RESOURCE_EXHAUSTED` (Quota Exceeded) Errors
If `make eval` fails with an error resembling:
```
429 RESOURCE_EXHAUSTED: You exceeded your current quota...
Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 5, model: gemini-2.5-flash
```
**Why this happens:**
When running the full test suite, `agents-cli eval generate` executes all 4 evaluation scenarios concurrently or in rapid succession. Because each test case triggers multiple LLM agent turns (such as input parsing and response synthesis), the evaluation pipeline attempts 12+ API requests within seconds. If your `GEMINI_API_KEY` is on Google AI Studio's **Free Tier**, you are limited to **5 requests per minute (RPM)**. Exceeding this immediately aborts the evaluation.

#### How to run successfully:
1. **Option 1: Free Tier Workaround (Single Test Execution)**
   To stay under the 5 RPM Free Tier limit, test scenarios individually by creating a smaller dataset containing only 1 test case at a time, or wait 60 seconds between individual evaluation runs.
2. **Option 2: Pay-As-You-Go / Vertex AI Billing (Recommended for CI/CD)**
   Upgrade the Google AI Studio project associated with your `GEMINI_API_KEY` to Pay-As-You-Go (or use a billing-enabled Google Cloud / Vertex AI project). This raises the quota to 1000+ RPM, allowing `make eval` to execute the full test suite concurrently without rate-limiting errors.
