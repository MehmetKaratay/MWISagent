# Specification: MWIS Agent Evaluation Test Suite

This spec defines the automated evaluation testing strategy for the MWIS Weather Agent using the ADK 2.0 framework.

```yaml
spec_version: "1.0"
agent_framework: "google-adk>=2.0.0a0"
```

---

### SECTION 1: SPEC

**One-line purpose**
Provides a repeatable, automated evaluation pipeline to test the MWIS agent's task success and workflow routing across direct, ambiguous, and out-of-scope queries.

**Users and use cases**
* As a developer, I want to automatically evaluate the agent against a fixed set of test scenarios so that I can catch regressions when modifying the workflow graph or LLM prompts.

**Requirements**
1. **Eval Dataset:** Provide a JSON dataset representing key user flows (direct hits, ambiguities, follow-ups).
2. **Out of Scope Handling:** Include explicit tests for "What was the weather like yesterday?" and "What is the weather in London?".
3. **Metrics Configuration:** Use ADK's built-in `multi_turn_task_success`, `multi_turn_trajectory_quality`, and `final_response_quality`.
4. **Custom Metrics:** Include an `agent_turn_count` metric to ensure loop limits aren't exceeded unnecessarily.
5. **On-Demand Execution:** Tests must only be executed via a manual `Makefile` command to minimize token usage.

**Edge cases & expected behavior**
* *Missing API Key:* If the `GEMINI_API_KEY` is missing during `eval grade`, the LLM judge will fail. [ASSUMPTION: User has this configured in `.env`]
* *Deterministic Data:* Testing will use static HTML files (via `MWIS_ENV=development`) to ensure the input weather data is static. This allows us to have predictable outputs for the `final_response_quality` LLM judge, making the evaluation deterministic.

**Acceptance criteria**
```
Given the mwis_eval.json dataset and eval_config.yaml
When the developer runs `make eval`
Then the ADK CLI generates a trace and grades it without crashing

Given a test case asking about the weather yesterday
When evaluated by the agent
Then the agent triggers the historic_lookup node

Given a test case asking about London
When evaluated by the agent
Then the agent triggers the out_of_scope_msg node
```

---

### SECTION 2: PLAN

**Stack and architecture**
* Framework: Google ADK 2.0 `agents-cli eval`
* Execution: Local Makefile target wrapping `eval generate` and `eval grade`

**Data model changes**
* No changes to the database schema.
* Creation of `mwis_eval.json` with canonical ADK EvaluationDataset schema.

**API contracts**
* N/A (Internal CLI commands).

**Patterns to follow**
* ADK Eval configuration standards: Use `tests/eval/eval_config.yaml` to define metrics.
* [ASSUMPTION: Using Gemini Flash for the evaluation judge to optimize speed and cost.]

**Testing strategy**
* This specification *is* the testing strategy for the agent's behavior. The output of the evaluation will act as our regression suite.

**Security and performance constraints**
* Tests invoke the Gemini API for grading; execution is limited to on-demand `make eval` to control costs.

---

### SECTION 3: TASKS

## Task 1: Create Evaluation Dataset
**What to build:** Create the `mwis_eval.json` file containing the direct query, ambiguous query, London query, and yesterday query.
**Files likely affected:** `mwis-agent/tests/eval/datasets/mwis_eval.json`
**Acceptance criteria:** JSON is well-formed according to ADK dataset schema.
**Dependencies:** none

## Task 2: Configure Eval Metrics
**What to build:** Update `eval_config.yaml` to include `multi_turn_task_success`, `multi_turn_trajectory_quality`, `final_response_quality`, and the custom `agent_turn_count`.
**Files likely affected:** `mwis-agent/tests/eval/eval_config.yaml`
**Acceptance criteria:** YAML file successfully maps to the built-in metrics and defines the custom python function.
**Dependencies:** Task 1

## Task 3: Create Makefile for On-Demand Execution
**What to build:** Add a `Makefile` with an `eval` target that runs `agents-cli eval generate` followed by `agents-cli eval grade`. It must pass `MWIS_ENV=development` to `agents-cli eval generate` so the agent uses static HTML dumps instead of live fetch.
**Files likely affected:** `Makefile` (root)
**Acceptance criteria:** Running `make eval` executes the pipeline in development mode successfully.
**Dependencies:** Task 2

---
