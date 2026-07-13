# Resolve Shift Spec

This specification defines a utility script `resolve_shift.py` to calculate relative date code shifts.

```yaml
name: resolve_shift
summary: Resolve relative date shifts based on active MWIS day codes.
inputs:
  - name: current_code
    type: string
    required: true
    description: "The active forecast day code (e.g. 'D0', 'D1', 'D2', 'D3')"
  - name: shift_query
    type: string
    required: true
    description: "Fuzzy user query expressing shift direction (e.g. 'following day', 'previous day', 'next day')"
outputs:
  - name: resolved_code
    type: string
    description: "The newly calculated MWIS day code"
```

## Behavior & Logic

- **Direction Detection**:
  - Matches queries implying forward progression (e.g. "following day", "next day", "day after", "tomorrow") to shift forwards.
  - Matches queries implying backward progression (e.g. "day before", "previous day", "yesterday") to shift backwards.
- **D-code Boundary Rules**:
  - Shift forward: `D0 -> D1`, `D1 -> D2`, `D2 -> D3`.
  - Shift backward: `D3 -> D2`, `D2 -> D1`, `D1 -> D0`.
  - Shifts beyond `D3` or before `D0` should clip to boundaries (e.g., trying to shift forward from `D3` returns `D3`).
  - If current code is `Doutlook` or invalid, return `D0`.

## Examples

| Current Code | Shift Query | Expected Resolved Code |
| :--- | :--- | :--- |
| `D0` | `next day` | `D1` |
| `D1` | `following day` | `D2` |
| `D2` | `previous day` | `D1` |
| `D3` | `day after` | `D3` |
