# Design Decisions

Status: drafted by Engineer A. Engineer B confirms or amends each item before the PRs are merged.

## The seven design questions

### 1. What does one request dictionary look like?

```json
{
  "id": "A001",
  "fellow_id": "F001",
  "card_type": "visitor",
  "status": "requested",
  "approved_by": null
}
```

- `id`: `A` followed by three or more ASCII digits (`A001`, `A002`, ... `A1000`).
- `fellow_id`: non-blank text, no leading or trailing spaces.
- `card_type`: exactly `visitor`, `student` or `staff` (case-sensitive).
- `status`: `requested`, `approved`, `issued` or `returned`.
- `approved_by`: `null` while `requested`; a non-blank staff identifier in every later status.

All requests live in one dictionary keyed by ID. A dictionary gives direct lookup by ID, and a key can exist only once, so duplicates cannot occur in memory.

### 2. What does `create_request` return?

A **copy** of the new record. The stored record is never handed out, so callers cannot change it by accident.

### 3. How do functions report invalid input?

Every function raises `ValueError` with a clear message, for example `card_type must be one of: visitor, student, staff`. The CLI catches `ValueError` and shows the message, so a typo never crashes the program.

### 4. Where is the next ID generated?

In `storage.py` (`_next_id`). It takes the highest existing ID number and adds one. Because it is derived from the stored data, it stays correct after a reload and needs no separate counter that could fall out of sync. This relies on requests never being deleted.

### 5. How does Engineer B call Engineer A's storage functions?

```python
from access_cards import storage
```

| Need | Function |
|---|---|
| Read one request | `storage.get_request(request_id)` |
| List requests | `storage.list_requests()` |
| Change status or approver | `storage.update_request(request_id, status, approved_by)` |
| Save or load | `storage.save_requests(path)`, `storage.load_requests(path)` |

B never touches the internal store directly.

**Division of responsibility:**
- Engineer B owns the **transition rules** (`requested` → `approved` → `issued` → `returned`, no skipping, `returned` is final) and checks them before calling `update_request`.
- Engineer A owns **data validity**: `update_request` rejects unknown IDs, unknown statuses, and any record that would have no approver once approved.

### 6. What happens if a saved JSON file is invalid?

- `load_requests` raises `ValueError` with a message saying what is wrong and where, for example `record 3: missing keys ['status']`.
- Memory is left unchanged, and the file on disk is never modified.
- `main.py` stops with an error message instead of continuing with an empty store, so a later save cannot overwrite the damaged file.
- A **missing** file is a normal first run and is not an error. An **empty or corrupt** file is an error.

Rejected files include: invalid JSON, an empty file, a top level that is not a list, missing or extra keys, duplicate IDs, malformed IDs, invalid card types or statuses, blank fellow IDs, and an approver that does not match the status.

### 7. Which data must never change on a rejected operation?

- All five fields of every record.
- The set of records in memory (no record added, removed or replaced).
- The saved file on disk.

This holds because each function validates first, builds any change on a copy, and writes to the store in a single final step.

## Further decisions

| Decision | Choice | Reason |
|---|---|---|
| Whitespace in text fields | Rejected, not trimmed | Validation rejects; it does not silently change input. The CLI strips typed input before calling storage. |
| Card type case | Case-sensitive | One exact allowed value per type avoids ambiguity. |
| ID digits | ASCII `0-9` only, checked with `fullmatch` | `str.isdigit()` accepts other Unicode numerals, and a trailing newline would slip past `match`. |
| JSON format | List of records | `json.load` silently drops duplicate keys in an object, so duplicate IDs would go unnoticed. A list makes them detectable. |
| Saving | Write to a temporary file, then `os.replace` | A failed save never damages a previously valid file. |
| Loading | Validate everything first, replace memory last | A bad file can never wipe valid records. |
| Project layout | `access_cards/` package, `tests/`, `docs/` | Standard Python layout; standard library only. |

## Confirmed with Engineer B

- [ ] Update function name and signature
- [ ] `ValueError` for all rejected input
- [ ] Whitespace rejected; CLI strips typed input
- [ ] Data file name (`requests.json`) and list format
- [ ] Package layout and import style
- [ ] Who edits shared files (`main.py`, `README.md`, `docs/`)
