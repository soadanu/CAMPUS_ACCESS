# Campus Access-Card Request Manager

A Python command-line application for managing campus access-card requests (visitor, student and staff). A request is created, approved by an authorized staff identifier, issued, and eventually returned. Invalid actions are rejected, and data stays correct after a restart.

Built with the Python standard library only. No third-party packages are needed.

## Team

| Role | Name | Owns |
|---|---|---|
| Engineer A | Solomon Adanu | Request creation, validation, ID generation, lookup, save and load (`storage.py`) |
| Engineer B | _name here_ | Approve, issue, return and the CLI menu (`workflow.py`) |

## Requirements

- Python 3.9 or newer

## Project structure

```
main.py                 Entry point
storage.py              Engineer A: data layer
workflow.py             Engineer B: workflow rules and CLI menu
tests/
    test_storage.py     Engineer A tests
    test_workflow.py    Engineer B tests
docs/
    design-decisions.md Design answers agreed by both engineers
    ai-learning-log.md  AI-assisted learning record
```

## Running the tests

From the project root:

```
python -m unittest discover -s tests -v
```

Tests use temporary files, so they never touch real data.

## Running the application

```
python main.py
```

Requests are saved to `requests.json` in the project root. The file is created on first save and loaded on start.

## Request format

Each request has five fields:

| Field | Description |
|---|---|
| `id` | `A001`, `A002`, ... unique, and never reused after a restart |
| `fellow_id` | Non-blank text identifying the person the card is for |
| `card_type` | `visitor`, `student` or `staff` |
| `status` | `requested`, `approved`, `issued` or `returned` |
| `approved_by` | `null` while `requested`; a non-blank staff identifier afterwards |

Workflow: `requested` → `approved` → `issued` → `returned`. No state may be skipped, and `returned` is final.

## Data layer (`storage.py`)

| Function | Purpose |
|---|---|
| `create_request(fellow_id, card_type)` | Creates the next request and returns a copy |
| `get_request(request_id)` | Read-only lookup; returns a copy |
| `list_requests()` | Copies of all requests in ID order |
| `update_request(request_id, status, approved_by)` | The only way to change a stored record |
| `save_requests(path)` | Saves all requests to JSON |
| `load_requests(path)` | Loads and validates requests from JSON |
| `clear_requests()` | Empties the store (tests and simulated restarts) |

### Guarantees

- **Failed operations change nothing.** Input is validated before the store is touched, and every failure raises `ValueError`.
- **Callers only receive copies.** Stored records cannot be modified by accident.
- **IDs stay unique across restarts.** The next ID is the highest existing number plus one.
- **ID checks are ASCII-only.** Only digits `0-9` are accepted, not other Unicode numerals.
- **Saving is atomic.** Data is written to a temporary file and swapped in only on success, so a failed save never damages a valid file.
- **Loading is all-or-nothing.** A corrupt file, empty file, missing key, duplicate ID, invalid value or inconsistent approver is rejected with a clear message. Existing records and the file on disk are left untouched.
- A missing file on load is treated as a first run, not an error.

### Design decisions

- Whitespace is rejected, not trimmed (`" F001"` is invalid). The CLI should strip typed input before calling the data layer.
- `card_type` is case-sensitive.
- `update_request` guarantees the resulting record is valid. Transition rules (which status may follow which) are enforced by `workflow.py`.

## Git workflow

- `main` is protected by convention: no direct feature pushes.
- Engineer A works on `feat/1-request-validation`, Engineer B on `feat/2-access-workflow`.
- Each engineer opens a pull request, and the other engineer reviews it and runs the tests before it is merged.
- Commit messages follow the pattern `feat: ...`, `test: ...`, `docs: ...`.
