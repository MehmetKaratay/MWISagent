# Inject D-codes Spec

This specification defines a Python script `inject_Dcodes.py` to inject resolved MWIS coverage D-codes into a parsed forecast JSON structure.

```yaml
name: inject_Dcodes
summary: Injects resolved D-codes into the forecast days and outlook JSON structure.
inputs:
  - name: forecast_json
    type: string (JSON)
    required: true
    description: "Parsed forecast JSON matching parse_forecast output schema"
  - name: ref_date
    type: string (YYYY-MM-DD)
    required: false
    description: "Optional reference date to calibrate mapping offsets"
outputs:
  - name: updated_json
    type: string (JSON)
    description: "Forecast JSON containing D-code fields"
dependencies:
  - python >= 3.10
  - parse_Dcodes module
```

## Injection Rules

The injector reads the forecast JSON structure and transforms it as follows:

### 1. Day Objects (`"days"` Array)
For each day dictionary in the `"days"` array:
- Parse the day's `"date"` field (e.g. `"Sunday 5th July 2026"` -> resolves to date `2026-07-05`).
- Call `get_d_code_for_date(target_date, ref_date)` from `parse_Dcodes.py` to determine the D-code.
- Insert the resolved D-code as a new key-value pair under `"Dcode"`.
  - Example: `"Dcode": "D0"`

### 2. Outlook Object (`"outlook"` Property)
The root-level `"outlook"` string property is transformed into a dictionary containing:
- `"Dcode"`: Fixed to the string `"Doutlook"`.
- `"outlook"`: The original string content representing the planning outlook.
- Example structure:
  ```json
  "outlook": {
    "Dcode": "Doutlook",
    "outlook": "Settled weather returning later in the week..."
  }
  ```

---

## Example Output Structure

```json
{
  "region": "Eastern Highlands",
  "days": [
    {
      "day_index": 0,
      "date": "Sunday 5th July 2026",
      "Dcode": "D0",
      ...
    }
  ],
  "outlook": {
    "Dcode": "Doutlook",
    "outlook": "Settled weather returning..."
  }
}
```
