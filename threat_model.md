# STRIDE Threat Model Assessment: Clarification Flows (Date & Location)

## System Boundaries
- **Entry Points:** The ADK user interface and LLM parsing nodes.
- **Data Flow:** User input -> `parse_input` node -> `check_ambiguity` node -> `clarify_date` / `clarify_location` nodes -> `resolve_and_fetch` / `compare_regions` nodes.
- **Data Dependencies:** `mwis-regions.csv` mapping for region and country resolution.

## STRIDE Evaluation

1. **Spoofing**
   - *Threat:* A malicious actor spoofs user identities in the chat interface.
   - *Mitigation:* ADK core handles session separation. The new clarification nodes rely on `ctx.resume_inputs` using unique `interrupt_id`s tied to the session state.

2. **Tampering**
   - *Threat:* The user provides a malicious prompt injection when asked for date/location clarification.
   - *Mitigation:* Clarifications are injected as state updates. The LLM parsing logic mapping regions to `mwis-regions.csv` protects against arbitrary executable payloads passing through to backend APIs.

3. **Repudiation**
   - *Threat:* Changes in state (missing inputs to clarified inputs) are untraceable.
   - *Mitigation:* ADK automatically traces all node transitions, state updates, and `RequestInput` yields. All interactions are logged in the trace directory.

4. **Information Disclosure**
   - *Threat:* The clarification nodes leak internal state or API keys.
   - *Mitigation:* The nodes only return static, pre-defined question strings. No dynamic sensitive data is exposed to the user.

5. **Denial of Service (DoS)**
   - *Threat:* A user requests a comparison of many areas (e.g., all 10 areas) at once, exhausting API rate limits or LLM context windows.
   - *Mitigation (Applied):* A strict maximum of 5 regions per comparison is enforced at the extraction and routing layer. Bulk abstractions like "Scottish areas" correctly map to 5 regions, entirely eliminating the risk of large-scale fan-out DoS on the backend API or token overflow on the LLM.

6. **Elevation of Privilege**
   - *Threat:* Unauthenticated access to the backend `get_forecast` API through crafted inputs.
   - *Mitigation:* `get_forecast` performs only READ operations on public endpoints. No privilege elevation is possible.
