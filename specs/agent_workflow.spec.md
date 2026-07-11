# Specification: ADK 2.0 Graph Workflow for MWIS Weather Agent

This spec defines the graph topology, node configurations, state management, and loopback routing rules for the MWIS weather forecast agent.

```yaml
spec_version: "2.1"
agent_framework: "google-adk>=2.0.0a0"
model: "gemini-2.5-flash"
output_type: "plain-text"
```

---

### SECTION 1: SPEC

**One-line purpose**
Provides interactive mountain weather forecast synthesis, resolving missing inputs gracefully, offering multi-region comparison (max 5 regions), and handling elevation/region adjustment loopbacks using an ADK 2.0 Graph Workflow.

**Users and use cases**
* As a hiker, I want to ask about weather forecasts in a specific UK mountain area so that I can plan my outing.
* As an active user, I want to ask follow-up questions to estimate conditions higher/lower or in a specific sub-region so that I can adapt my route safely.
* As an ADK user, I want the agent to ask me to clarify the date if I don't provide one, so that I don't accidentally receive a forecast for the wrong day.
* As an ADK user, I want the agent to ask me to clarify the location if I don't provide one, and offer a regional comparison so I can find the best weather across multiple areas.
* As an ADK user, I want to request a comparison of up to 5 explicit forecasts I choose.

**Requirements**
1. **Inputs:** Accepts free-text user query. The agent must parse and extract any relative dates (e.g. 'today', 'tomorrow', 'Saturday') or absolute dates (e.g. '11/07/2026', '11th July') in the user input.
2. **Ambiguity Handling:** Suspends execution using `RequestInput` if location or date is completely missing or ambiguous, prompting the user for clarification.
3. **Data Fetching:** Programmatically invokes the `mwis-website` scripts to parse forecast HTML and inject D-codes. It must support fetching up to 5 regions concurrently.
4. **Caching Layer:** The backend caching layer is implemented via the `check_forecast_issued` skill and the `sqlite3` database to store the 10 MWIS forecasts. The front end will have no memory layer.
5. **Conditional Routing:**
   * Run `weather_physics` if `needs_physics` is set (triggered by queries on elevation, temperature gradients, or physical causes).
   * Run `weather_impact` if `needs_impact` is set (triggered by questions on safety, hiking plans, or presence of significant hazards like high winds/heavy rain).
   * Run `local_knowledge` if `needs_local_knowledge` is set (triggered by questions on specific micro-locations).
6. **Synthesis:** Synthesizes final output in plain text. If specific date codes (like `D0` or `D1`) are resolved and present in the state under `resolved_date_codes`, the synthesized text must only contain the forecast for those specific days, omitting any other days or general outlook.
7. **Follow-Up Loop:** Prompts the user with follow-up options ("higher or lower?", "specific part of the region?") using `RequestInput` and loops back to execute the corresponding nodes.

**Edge cases & expected behavior**
* *No Location:* Suspend and yield `RequestInput` offering a comparison of up to 5 regions or a specific location.
* *No Date:* Suspend and yield `RequestInput` asking for specific date or 3-day outlook.
* *User requests >5 explicit regions:* Suspend and yield `RequestInput` reminding them of the 5-region cap and asking them to choose exactly which regions they want (Reminder: Scotland has 5, England has 3, Wales has 2).
* *LLM parser omits optional fields:* Pydantic `ParseOutput` must correctly default `date` to `None` without raising a `ValidationError`.
* *Out of Scope / Invalid:* If the location is outside the UK, or fails to resolve to a known region (maps to "Unknown"), or the date is not between D0 and Doutlook, return a service limits message. If date is Dold, route to a historic lookup placeholder.
* *Mock Forecast Environments:* In local dev, `MWIS_ENV=development` will dynamically align mock forecast dates to the current execution date to ensure they are treated as "fresh". `MWIS_ENV=test-new-dcode` will intentionally misalign dates to force a `"Dold"` (stale) scenario for testing.
* *Hazard Detection:* If forecast data contains winds > 40mph or temperatures < -5°C, dynamically override `needs_impact = True`.
* *Infinite Loops:* Cap loopback iterations at 5 to prevent DoS.

**Acceptance criteria**
```
Given a query "What is the weather like on Ben Nevis today?"
When execution starts
Then the workflow parses "Ben Nevis" and "today", fetches the West Highlands forecast, and outputs a plain-text synthesis.

Given a vague query "Is it going to rain?"
When execution starts
Then the workflow suspends at clarify_location prompting for a location.

Given a vague query "What is the weather on Ben Nevis?" (no date)
When execution starts
Then the workflow suspends at clarify_date prompting for a date.

Given a query "Compare all areas"
When execution starts
Then the workflow suspends at clarify_location stating "Only 5 regions can be compared. Which regions do you wish to choose?"
```

---

### SECTION 2: PLAN

**Stack and architecture**
* ADK 2.0 `Workflow` graph containing:
  * `parse_input` (LLM node)
  * `clarify_location` (RequestInput node)
  * `clarify_date` (RequestInput node)
  * `resolve_and_fetch` (Function node calling imported Python modules and `query_countries.py` logic)
  * `validate_coverage` (Function node checking geographical and date limits)
  * `historic_lookup` (Function node dummy historic lookup placeholder)
  * `out_of_scope_msg` (Function node returning service limit message)
  * `weather_physics` (Pass-through Function node)
  * `weather_impact` (Pass-through Function node)
  * `local_knowledge` (Pass-through Function node)
  * `synthesis` (LLM node)
  * `ask_follow_up` (RequestInput node)
  * `process_follow_up` (Function node)
* State Schema: `WorkflowState` Pydantic model.

**Mermaid Graph Topology**
```mermaid
graph TD
    START([START]) --> set_raw_query[set_raw_query: Isolates query in XML tags]
    set_raw_query --> parse_input[parse_input: LLM extracts locations/date/flags & detects attacks]
    parse_input --> check_security{Is input malicious?}

    %% Security route
    check_security -- malicious --> security_refusal[security_refusal: Returns error message]
    security_refusal --> END([END])

    check_security -- safe --> check_ambiguity{Is input vague?}

    %% Ambiguity route
    check_ambiguity -- missing_location --> clarify_location[clarify_location: RequestInput HITL]
    check_ambiguity -- missing_date --> clarify_date[clarify_date: RequestInput HITL]
    clarify_location --> resolve_and_fetch
    clarify_date --> resolve_and_fetch

    %% Clear route
    check_ambiguity -- No --> resolve_and_fetch[resolve_and_fetch: Runs query scripts & checks hazards]

    resolve_and_fetch --> validate_coverage[validate_coverage: Checks UK scope & date codes D0-Doutlook]

    validate_coverage --> check_valid{Is UK and D0-Doutlook?}

    %% Non-valid routing
    check_valid -- No (is Dold?) --> historic_lookup[historic_lookup: Dummy historic placeholder]
    check_valid -- No (other / out of scope) --> out_of_scope_msg[out_of_scope_msg: Returns service bounds message]

    historic_lookup --> END([END])
    out_of_scope_msg --> END

    %% Valid routing
    check_valid -- Yes --> check_physics{needs_physics?}

    check_physics -- Yes --> weather_physics[weather_physics: Analysis]
    check_physics -- No --> check_impact{needs_impact?}

    weather_physics --> check_impact
    check_impact -- Yes --> weather_impact[weather_impact: Hazard analysis]
    check_impact -- No --> check_local{needs_local_knowledge?}

    weather_impact --> check_local
    check_local -- Yes --> local_knowledge[local_knowledge: Micro-location analysis]
    check_local -- No --> synthesis

    local_knowledge --> synthesis[synthesis: LLM synthesizes final plain-text response]

    %% Follow-up interactive loop
    synthesis --> ask_follow_up[ask_follow_up: RequestInput for elevation/region change]
    ask_follow_up --> process_follow_up[process_follow_up: Updates state & loop count]
    process_follow_up --> check_loop_limit{loop_count < 5?}

    check_loop_limit -- Yes --> resolve_and_fetch
    check_loop_limit -- No --> END
```

**API contracts**
* `WorkflowState`:
  ```python
  class WorkflowState(BaseModel):
      raw_query: str
      locations: list[str] = Field(default_factory=list) # Replaces location
      date: Optional[str] = None
      resolved_date_codes: list[str] = Field(default_factory=list) # Track resolved date codes (e.g. D0, D1)
      region_codes: list[str] = Field(default_factory=list) # Replaces region_code
      forecast_data: Optional[dict] = None
      needs_physics: bool = False
      needs_impact: bool = False
      needs_local_knowledge: bool = False
      is_malicious: bool = False
      loop_count: int = 0
  ```
* `ParseOutput` must correctly specify `default=None` and `default=False` across all fields, and include `is_malicious: bool = False`.

**Testing strategy**
* Eval dataset under `mwis-agent/tests/` evaluating location/date extraction and synthesis accuracy.
* Unit tests validating `check_ambiguity` routing to `missing_location` and `missing_date`.
* Curl integration test under `tests/integration/test_human_agent_interaction.py` starting the dev server and sending a `curl -X POST` request for today's forecast to verify "Outlook:" section is excluded from the text output.

---

### SECTION 3: TASKS

## Task 1: Define State Schema and Nodes
* **What to build:** Implement `WorkflowState` (with `locations` array) and `ParseOutput` Pydantic models. Fix schema default bugs.
* **Files likely affected:** `mwis-agent/app/agent.py`
* **Acceptance criteria:** Code compiles, instantiating `ParseOutput()` without arguments succeeds.
* **Dependencies:** none

## Task 2: Implement Ambiguity Routing & Clarification Nodes
* **What to build:** Construct the `clarify_location` and `clarify_date` `RequestInput` nodes. Implement `check_ambiguity` to route appropriately. Handle >5 region prompts.
* **Files likely affected:** `mwis-agent/app/agent.py`
* **Acceptance criteria:** Missing inputs hit the correct clarification nodes instead of crashing.
* **Dependencies:** Task 1

## Task 3: Assemble Workflow Graph and Routing
* **What to build:** Construct the `Workflow` graph using the edges list and conditional routers. Integrate `resolve_and_fetch` with `query_countries.py` logic and `asyncio.gather`.
* **Files likely affected:** `mwis-agent/app/agent.py`
* **Acceptance criteria:** Workflow builds, `agents-cli playground` launches successfully and correctly parses/aggregates up to 5 forecasts.
* **Dependencies:** Task 2

## Task 4: Prompt Injection Security Layer
* **What to build:** Implement the `<user_input>` XML isolation in `set_raw_query`. Update `parse_input` instruction to reject system commands and set `is_malicious=True`. Add `check_security` router and `security_refusal` terminal node.
* **Files likely affected:** `mwis-agent/app/agent.py`, `mwis-agent/app/agent_nodes.py`, `mwis-agent/app/agent_logic.py`, `mwis-agent/app/agent_state.py`
* **Acceptance criteria:** Malicious prompts injected into the system are caught by `parse_input`, routed to `security_refusal`, and safely rejected without calling MWIS.
* **Dependencies:** Task 1, Task 2, Task 3

---

## Assumptions to review

1. [ASSUMPTION: We check location ambiguity before date ambiguity in routing] — Impact: MEDIUM
2. [ASSUMPTION: Capping follow-up iterations at 5 is acceptable to prevent DoS] — Impact: MEDIUM
