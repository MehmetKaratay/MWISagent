# query_date.py Documentation

The `query_date.py` command-line utility resolves formatted or natural language dates and date ranges into Mountain Weather Information Service (MWIS) forecast coverage codes.

## Installation

Ensure dependencies are installed in your virtual environment:
```bash
# Install the package and its dependencies
pip install .
# Or using uv:
uv pip install .
```

## CLI Usage

Run the script from the command-line by passing a date query:
```bash
python3 query_date.py <date_query>
```

### Outputs

The script always outputs a JSON array of strings containing unique, chronologically ordered coverage codes to `stdout`.

Codes definitions:
- `Dold`: Past dates (offsets < 0 days)
- `D0`: Today (offset = 0 days)
- `D1`: Tomorrow (offset = 1 day)
- `D2`: Day 2 (offset = 2 days)
- `D3`: Day 3 (offset = 3 days)
- `Doutlook`: Mid-range outlook (offsets 4 to 7 days)
- `Dfuture`: Far-future dates (offsets >= 8 days)

### Examples

| Input Query | Today's Weekday | Output |
| :--- | :--- | :--- |
| `today` | Any | `["D0"]` |
| `tomorrow` | Any | `["D1"]` |
| `this weekend` | Friday | `["D1", "D2"]` |
| `this weekend` | Wednesday | `["D3", "Doutlook"]` |
| `today and tomorrow` | Any | `["D0", "D1"]` |
| `06/07/2026` (when reference is 04/07/2026) | Any | `["D2"]` |

## Relative Date Shifts

For conversational follow-up turns, shifts are resolved relative to the previous active code rather than absolute system time:
- Uses the `resolve_shift` helper.
- **Forwards**: `next day`, `following day`, `day after`, `tomorrow`.
- **Backwards**: `day before`, `previous day`, `yesterday`.
- Automatically clips boundaries between `D0` and `D3`.
