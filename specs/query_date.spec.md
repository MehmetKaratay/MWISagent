# Query Date Spec

This specification defines a command-line tool `query_date.py` to resolve natural language and formatted dates into MWIS forecast coverage codes.

```yaml
name: query_date
summary: Resolve input dates and ranges to MWIS forecast coverage codes.
inputs:
  - name: date_query
    type: string
    required: true
    description: "Standard (DD/MM, DD/MM/YYYY) or fuzzy (today, tomorrow, this weekend, next Sunday) date/range query"
outputs:
  - name: codes
    type: array of strings
    description: "A JSON array of strings containing unique MWIS forecast codes that cover the requested date range"
    values: "See D-code value definitions in parse_Dcodes.spec.md"
exit_codes:
  0: Success
  1: Invalid input format or parse error
dependencies:
  - python >= 3.10
  - parsedatetime >= 2.6
```

## Behavior & Parsing Logic

- **Reference Time**: All calculations are relative to the current local system date.
- **D-code Mapping**: Date values are resolved to D-codes using the rules and offsets defined in [parse_Dcodes.spec.md](file:///home/karatay/Repositories/weather/MWISagent/specs/parse_Dcodes.spec.md).
- **Forecast Publication Shifts**: The mapping offset shifts are calibrated dynamically by downstream components based on the parsed JSON date fields (see [inject_Dcodes.spec.md](file:///home/karatay/Repositories/weather/MWISagent/specs/inject_Dcodes.spec.md)).
- **Fuzzy Parsing**: Employs the `parsedatetime` library to resolve relative dates.
- **DD/MM standard**: If `parsedatetime` fails or parses incorrectly, fallback to parsing as `DD/MM` (using the current system year) or `DD/MM/YYYY`.
- **Range Resolution**: For inputs spanning multiple days (e.g., "this weekend" or "today and tomorrow"):
  - Determine each distinct date in the range.
  - Resolve the coverage code for each date.
  - Return a JSON array of all unique coverage codes, ordered chronologically by the dates they represent.
- **Format**: All outputs to stdout are formatted as a JSON array of strings (e.g., `["D1", "D2"]`).
- **Relative Date Shifts**: For conversational follow-up turns, relative date shifts are resolved using the `resolve_shift` helper:
  - **Forwards**: `next day`, `following day`, `day after`, `tomorrow`.
  - **Backwards**: `day before`, `previous day`, `yesterday`.
  - Boundaries are automatically clipped between `D0` and `D3`.

## Examples

| Input Query | Today's Weekday | Resolved Date(s) | Expected Output (JSON on stdout) |
| :--- | :--- | :--- | :--- |
| `today` | Any | Today | `["D0"]` |
| `tomorrow` | Any | Tomorrow | `["D1"]` |
| `06/07` | Monday, 06/07/2026 | 06/07/2026 | `["D0"]` |
| `05/07` | Monday, 06/07/2026 | 05/07/2026 | `["Dold"]` |
| `this weekend` | Friday, 03/07/2026 | Sat 04/07 to Sun 05/07 | `["D1", "D2"]` |
| `this weekend` | Wednesday, 01/07/2026 | Sat 04/07 to Sun 05/07 | `["D3", "Doutlook"]` |
| `15/07/2026` | Saturday, 04/07/2026 | 15/07/2026 | `["Dfuture"]` |
| `today and tomorrow` | Any | Today, Tomorrow | `["D0", "D1"]` |
