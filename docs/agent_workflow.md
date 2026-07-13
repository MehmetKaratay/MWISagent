# ADK 2.0 Graph Workflow Documentation - MWIS Weather Agent

This document explains the runtime architecture, node actions, and state transitions of the MWIS weather agent backend.

---

## 1. Graph Visualization

```mermaid
graph TD
    START([START]) --> parse_input[parse_input: LLM extracts location/date/flags]
    parse_input --> check_ambiguity{Is input vague?}

    %% Ambiguity routes
    check_ambiguity -- missing_location --> clarify_location[clarify_location: RequestInput HITL]
    check_ambiguity -- missing_date --> clarify_date[clarify_date: RequestInput HITL]
    check_ambiguity -- too_many_locations --> clarify_too_many_locations[clarify_too_many_locations: RequestInput HITL]

    clarify_location --> resolve_and_fetch
    clarify_date --> resolve_and_fetch
    clarify_too_many_locations --> resolve_and_fetch

    %% Clear route
    check_ambiguity -- no --> resolve_and_fetch[resolve_and_fetch: Runs query scripts & checks hazards]

    resolve_and_fetch -- too_many_locations --> clarify_too_many_locations
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

---

## 2. Graph Node Specifications

### Node 1: `parse_input`
* **Type:** `LlmAgent` (model: `gemini-2.5-flash`)
* **Behavior:** Extracts `locations`, `date`, and `extracted_categories` parameters, and evaluates whether the query requires `needs_physics`, `needs_impact`, or `needs_local_knowledge` annotations. The `date` parameter extraction rules strictly require parsing relative day descriptions (e.g. "today", "tomorrow", "Saturday", "this weekend") and absolute formats (e.g. "11/07/2026", "11th July"). The `locations` parameter extraction rules require identifying and extracting any geographical place name, mountain/hill (e.g., Ben Nevis, Snowdon, Scafell Pike), valley, town, region, country, or national park name. The `extracted_categories` parameter extracts query intent categories (e.g. `cloud`, `wind`, `wet`, `cold`, `sun`, `full`).

### Node 2: `clarify_location`
* **Type:** `RequestInput` (HITL interruption)
* **Behavior:** Suspends workflow execution to request the location from the user if completely missing or ambiguous.

### Node 2b: `clarify_date`
* **Type:** `RequestInput` (HITL interruption)
* **Behavior:** Suspends workflow execution to request the date from the user if missing.

### Node 2c: `clarify_too_many_locations`
* **Type:** `RequestInput` (HITL interruption)
* **Behavior:** Suspends workflow execution and prompts the user to select up to 5 explicit regions if they ask to compare more than 5.

### Node 3: `resolve_and_fetch`
* **Type:** `FunctionNode` (determinstic Python code)
* **Behavior:**
  * Resolves `locations` (up to 5 regions max) using `query_country.py` and `query_region.py`. If a location cannot be resolved, it is mapped to `"Unknown"`.
  * Resolves user-specified `date` query into `resolved_date_codes` using the `identify_outing_date` skill.
  * If the resolved region count > 5, routes to `clarify_too_many_locations`.
  * Fetches the corresponding forecasts sequentially from the local caching layer.
  * Programmatically filters the retrieved forecast JSON payload to retain only the days or outlook matching `resolved_date_codes` (if populated) by dynamically importing and executing `filter_forecast_payload` from the `serve_forecast_to_user` skill module.
  * Programmatically prunes forecast JSON keys to retain only fields matching `extracted_categories` by dynamically importing and executing `extract_forecast_details` from the `serve_forecast_to_user` skill module.
  * Scans forecast values: if wind speed is >40mph or temperature is <-5°C in any forecast, sets `needs_impact = True`.

### Node 4: `validate_coverage`
* **Type:** `FunctionNode`
* **Behavior:** Verifies if the location lies within the 10 UK mountain areas and the date code matches `D0` to `Doutlook`.
  * Routes to `historic_lookup` if date is `Dold`.
  * Routes to `out_of_scope_msg` if out of UK boundaries or beyond the outlook range.
  * Routes to the analysis pipeline (`check_physics`) if fully valid.

### Node 5: `historic_lookup`
* **Type:** `FunctionNode` (placeholder)
* **Behavior:** Outputs the out-of-scope boundaries message.

### Node 6: `out_of_scope_msg`
* **Type:** `FunctionNode`
* **Behavior:** Returns: *"This interactive service only provides forecasts for our 10 mountain areas in the UK over the next week."*

### Nodes 7-9: Pass-Through Analysis Nodes
* **`weather_physics`:** Pass-through.
* **`weather_impact`:** Pass-through.
* **`local_knowledge`:** Pass-through.

### Node 10: `synthesis`
* **Type:** `LlmAgent` (model: `gemini-2.5-flash`)
* **Behavior:** Reads the pre-filtered forecast payload context and annotations to generate a clean, plain-text response answering the query. Because the payload was filtered programmatically, the LLM only has access to the requested days' forecasts. If specific categories (elements) were requested, they are described first in the response.

### Node 11: `ask_follow_up`
* **Type:** `RequestInput`
* **Behavior:** Prompts the user: *"Do you want to estimate conditions higher/lower on the mountain, or in a specific part of the forecast region?"*

### Node 12: `process_follow_up`
* **Type:** `FunctionNode`
* **Behavior:** Increments `loop_count` (capped at 5) and parses follow-up parameters to determine routing flags for the next loop run.

---

## 3. Contextual Memory & State Retention Rules

To support natural conversation flows, the workflow implements contextual state memory retention and resets across interaction turns:

### Memory Retention
If the user's follow-up query does not specify a location, date, or category details, the agent retains and merges the values from the previous conversation turn's state:
- **Location Memory**: Retained from `ctx.state.get("locations")` if no locations are found in the new query.
- **Category Details**: Retained from `ctx.state.get("extracted_categories")` if no categories are extracted.
- **Date Memory**: Retained from `ctx.state.get("date")` if no new date/relative shift is specified.

### Relative Date Shifting
Relative date expressions in follow-up queries (e.g., "next day", "following day", "day after", "previous day", "day before") are resolved dynamically:
- Shifting calculations are resolved relative to the current active date code (e.g. `D0` to `D3`).
- Forward shifts advance the day index (`D0 -> D1`, `D1 -> D2`, `D2 -> D3`), clipping at the upper bound `D3`.
- Backward shifts reduce the day index (`D3 -> D2`, `D2 -> D1`, `D1 -> D0`), clipping at the lower bound `D0`.
- Shifting from an invalid date or `Doutlook` defaults to `D0`.

### State Reset ("New Query")
If a query explicitly contains a state reset intent (matching keywords like "reset", "clear", "restart", or "new search"), the agent sets `is_new_query = True` and clears all memory keys (setting `locations = []`, `date = None`, `extracted_categories = []`, and `resolved_date_codes = []`) to start fresh. Simply changing the queried location or query topic without these words is treated as a continuation and does not reset the context parameters.
