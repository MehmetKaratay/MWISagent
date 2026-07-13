---
title: Query Countries Utility
status: Approved
---

**One-line purpose**: A deterministic Python utility that reads `mwis-regions.csv` to map semantic country groupings to specific MWIS region codes, throwing an error if the mapping exceeds 5 regions.

### SECTION 1: SPEC

**Users and use cases**
- As the ADK workflow, I need to reliably convert semantic group names like "Scotland" or "English areas" into explicit MWIS region codes.
- As the ADK workflow, I need a strict guardrail that prevents fetching more than 5 regions at once to avoid API and token exhaustion.

**Requirements**
1. Read the `mwis-regions.csv` data source deterministically.
2. Accept a list of country strings (e.g., `["England", "Wales"]`).
3. Return a list of region codes (e.g., `["LD", "YD", "PD", "SD", "BB"]`).
4. Perform case-insensitive matching.
5. Explicitly raise a `ValueError` (or custom exception) if the requested combination results in more than 5 regions.

**Edge cases**
- **Unrecognized country name**: Silently ignore unmatched strings or return an empty list.
- **Duplicate country names**: Deduplicate the list to avoid duplicate region codes counting towards the 5-region limit.
- **Reset keyword filtering**: Strip any leading `"reset "` prefix from target location names before mapping to region codes.

**Acceptance criteria**
```yaml
Scenario 1: Single country request
Given: The function is called with ["Scotland"]
When: It parses the CSV
Then: It returns exactly 5 Scottish region codes.

Scenario 2: Multi-country valid request
Given: The function is called with ["England", "Wales"]
When: It parses the CSV
Then: It returns exactly 5 combined region codes.

Scenario 3: Guardrail exceeded
Given: The function is called with ["Scotland", "England"]
When: It parses the CSV and counts 8 total regions
Then: It raises an error explicitly stating that the 5-region limit was exceeded.

Scenario 4: Unrecognized country
Given: The function is called with ["Narnia"]
When: It parses the CSV
Then: It returns an empty list.
```

---

### SECTION 2: PLAN

**Stack and architecture**
- Python 3.13
- Read from standard CSV file

**Data model changes**
- None.

**API contracts**
- `get_regions_for_countries(country_names: list[str]) -> list[str]`: Throws `ValueError` if `len(regions) > 5`.

**Testing strategy**
- Unit tests (`test_query_country.py`) to verify CSV parsing, case-insensitivity, deduplication, and the strict >5 ValueError.

---

### SECTION 3: TASKS

## Task 1: Build `query_country.py` mapping utility
**What to build**: The deterministic Python script that reads `mwis-regions.csv` and implements `get_regions_for_countries`. Built using TDD.
**Files likely affected**:
- `mwis-agent/tests/unit/test_query_country.py` (create)
- `mwis-agent/app/skills/mwis-website/fetch_specific_forecast/scripts/query_country.py` (create)
**Acceptance criteria**:
1. `get_regions_for_countries(["Scotland"])` returns 5 Scottish codes.
2. `get_regions_for_countries(["Scotland", "Wales"])` raises a `ValueError`.
3. Unrecognized strings return an empty list.
4. Tests pass successfully.
**Dependencies**: none
