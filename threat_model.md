# STRIDE Threat Model Assessment

This document outlines the systematic STRIDE threat modeling assessment on the MWIS Agent's codebase, focusing on the date query resolution and programmatic forecast filtering architecture.

## System Boundaries & Entry Points
1. **Frontend Server (`/api/chat`)**: Receives plain-text user inputs from the web UI dashboard.
2. **Backend CLI Execution (`agents-cli run`)**: Orchestrates the ADK 2.0 `Workflow` graph.
3. **External Fetching / Caching Layer (`app/cache.py`, sqlite3 db)**: Fetches and caches region forecasts.

---

## STRIDE Evaluation

### 1. Spoofing
- **Analysis**: The API endpoints are authenticated using general Google signature validation. In local environments, mock modes are enabled using standard environment flags (`INTEGRATION_TEST=TRUE`, `MWIS_ENV=development`).
- **Mitigation**: Ensure production environments strictly enforce valid Google token verification and do not fall back to unverified defaults.

### 2. Tampering
- **Analysis**: The date query is parsed by the `parse_input` node and resolved programmatically in python via `identify_outing_date`. The forecast payload is programmatically filtered to prevent downstream LLM tampering.
- **Mitigation**: The filtering logic uses deterministic Python dictionaries (`_filter_forecasts` or `filter_forecast_payload`) preventing the user from injecting prompt payloads to reveal hidden forecast parts.

### 3. Repudiation
- **Analysis**: Backend cache lookups, database hits, and CLI executions are logged locally.
- **Mitigation**: Logs track region codes and output state but omit user personal data.

### 4. Information Disclosure
- **Analysis**: If the entire forecast payload is passed to the synthesis LLM, there is a risk of leakage/disclosure of unrequested forecasts or general outlook details if the user prompt attempts an extraction exploit.
- **Mitigation**: Programmatic day-filtering completely prunes the forecast JSON. The LLM only receives requested data, eliminating information disclosure of unrequested days.

### 5. Denial of Service
- **Analysis**: Loop count caps are set at 5 to prevent infinite loopback cycles. Forecast lookups are capped at 5 regions concurrently.
- **Mitigation**: Dict filtering runs in O(N) where N is very small, adding negligible computational overhead.

### 6. Elevation of Privilege
- **Analysis**: User inputs cannot trigger OS shell commands or modify backend database cache records directly.
- **Mitigation**: Database access is read-only for queries; updates are only performed by the structured cache loader.
