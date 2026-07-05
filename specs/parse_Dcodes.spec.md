# Parse D-codes Spec

This specification defines a Python module `parse_Dcodes.py` that resolves a target date to its corresponding Mountain Weather Information Service (MWIS) forecast coverage code.

```yaml
name: parse_Dcodes
summary: Resolve a target date to its MWIS forecast coverage code.
inputs:
  - name: target
    type: datetime.date
    required: true
    description: "The target calendar date to resolve"
  - name: ref_date
    type: datetime.date
    required: false
    description: "Optional reference date (defaults to current system date or MWIS_REFERENCE_DATE environment variable)"
outputs:
  - name: code
    type: string
    description: "Resolved MWIS forecast coverage code"
    values:
      Dold: "Past dates (offset < 0 days)"
      D0: "Today (offset = 0 days)"
      D1: "Tomorrow (offset = 1 day)"
      D2: "Day 2 (offset = 2 days)"
      D3: "Day 3 (offset = 3 days)"
      Doutlook: "Fuzzy max summary (offset = 4 to 7 days)"
      Dfuture: "Future dates (offset >= 8 days)"
dependencies:
  - python >= 3.10
```

## Programmatic API

The module must expose a function with the following signature:

```python
def get_d_code_for_date(target: datetime.date, ref_date: Optional[datetime.date] = None) -> str:
    """Resolve a target date to its MWIS forecast coverage code.

    Args:
        target: The target calendar date to resolve.
        ref_date: The reference date to calculate offsets against. Defaults to today or MWIS_REFERENCE_DATE env.

    Returns:
        The matching coverage code string (e.g. 'D0', 'D1', 'Doutlook').
    """
```

## Behavior & Offset Rules

The mapping between target date offsets (defined as `(target - ref_date).days`) and D-codes is strictly defined as follows:

| Date Offset (Days) | Coverage Code | Description |
| :--- | :--- | :--- |
| `< 0` | `Dold` | Past dates / outdated forecast |
| `0` | `D0` | Today's forecast |
| `1` | `D1` | Tomorrow's forecast |
| `2` | `D2` | Day 2 forecast (day after tomorrow) |
| `3` | `D3` | Day 3 forecast (3 days ahead) |
| `4` to `7` | `Doutlook` | Planning outlook period |
| `>= 8` | `Dfuture` | Extended future date beyond coverage |
