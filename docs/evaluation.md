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
