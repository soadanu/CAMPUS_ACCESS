"""Request storage for the campus access-card manager (Engineer A).

Owns: request creation, validation, unique ID generation, read-only lookup,
controlled updates, and saving/loading to JSON.

Rules enforced here:
* Every public function validates BEFORE it touches the store.
* Failures raise ValueError and leave the store exactly as it was.
* Callers only ever receive copies, never the stored dictionaries.
* A save never overwrites a valid file with a partial one.
* A load never replaces the store unless the whole file is valid.
"""

from __future__ import annotations

import copy
import json
import os
import re
import tempfile

ALLOWED_CARD_TYPES = ("visitor", "student", "staff")
ALLOWED_STATUSES = ("requested", "approved", "issued", "returned")
REQUEST_KEYS = frozenset(
    {"id", "fellow_id", "card_type", "status", "approved_by"}
)

# [0-9] on purpose: \d would also accept non-ASCII digits such as Arabic-Indic.
_ID_PATTERN = re.compile(r"A[0-9]{3,}")

# Sentinel so update_request can tell "leave approved_by alone" from "set None".
_UNSET = object()

# The single store: {"A001": {...record...}, ...}
_requests: dict[str, dict] = {}


# --------------------------------------------------------------------------
# Validation helpers (pure: they only check, they never change anything)
# --------------------------------------------------------------------------

def _require_clean_text(value, name: str) -> str:
    """Return value if it is a non-blank string with no padding spaces."""
    if not isinstance(value, str):
        raise ValueError(f"{name} must be a string")
    if not value.strip():
        raise ValueError(f"{name} must not be blank")
    if value != value.strip():
        raise ValueError(f"{name} must not have leading or trailing spaces")
    return value


def validate_request_id(request_id) -> str:
    """Accept only IDs like A001 (letter A, then 3+ ASCII digits)."""
    if not isinstance(request_id, str):
        raise ValueError("request id must be a string")
    if not _ID_PATTERN.fullmatch(request_id):
        raise ValueError(
            f"malformed request id {request_id!r}; expected a format like A001"
        )
    return request_id


def validate_fellow_id(fellow_id) -> str:
    return _require_clean_text(fellow_id, "fellow_id")


def validate_card_type(card_type) -> str:
    if not isinstance(card_type, str):
        raise ValueError("card_type must be a string")
    if card_type not in ALLOWED_CARD_TYPES:
        raise ValueError(
            f"card_type must be one of: {', '.join(ALLOWED_CARD_TYPES)}"
        )
    return card_type


def validate_status(status) -> str:
    if not isinstance(status, str) or status not in ALLOWED_STATUSES:
        raise ValueError(
            f"status must be one of: {', '.join(ALLOWED_STATUSES)}"
        )
    return status


def validate_approver_for_status(status: str, approved_by) -> None:
    """approved_by must be None while 'requested', and nonempty afterwards."""
    if status == "requested":
        if approved_by is not None:
            raise ValueError("approved_by must be null while status is 'requested'")
    else:
        _require_clean_text(approved_by, "approved_by")


def _validate_record(record, label: str) -> None:
    """Validate a whole record. Errors are prefixed with label for clarity."""
    if not isinstance(record, dict):
        raise ValueError(f"{label}: must be an object")

    keys = set(record)
    if keys != REQUEST_KEYS:
        missing = sorted(REQUEST_KEYS - keys)
        unexpected = sorted(keys - REQUEST_KEYS)
        details = []
        if missing:
            details.append(f"missing keys {missing}")
        if unexpected:
            details.append(f"unexpected keys {unexpected}")
        raise ValueError(f"{label}: {', '.join(details)}")

    try:
        validate_request_id(record["id"])
        validate_fellow_id(record["fellow_id"])
        validate_card_type(record["card_type"])
        validate_status(record["status"])
        validate_approver_for_status(record["status"], record["approved_by"])
    except ValueError as error:
        raise ValueError(f"{label}: {error}") from None


# --------------------------------------------------------------------------
# Store operations
# --------------------------------------------------------------------------

def _next_id() -> str:
    """Highest existing number + 1. Derived from the data, so it survives reloads."""
    highest = max((int(request_id[1:]) for request_id in _requests), default=0)
    return f"A{highest + 1:03d}"


def create_request(fellow_id, card_type) -> dict:
    """Create a new request with status 'requested'. Returns a copy of it."""
    record = {
        "id": _next_id(),
        "fellow_id": validate_fellow_id(fellow_id),
        "card_type": validate_card_type(card_type),
        "status": "requested",
        "approved_by": None,
    }
    _requests[record["id"]] = record  # the only line that touches the store
    return copy.deepcopy(record)


def get_request(request_id) -> dict:
    """Read-only lookup. Returns a copy; changing it does not change the store."""
    validate_request_id(request_id)
    if request_id not in _requests:
        raise ValueError(f"unknown request id {request_id!r}")
    return copy.deepcopy(_requests[request_id])


def list_requests() -> list[dict]:
    """Copies of all requests, ordered A001, A002, ..."""
    ordered = sorted(_requests, key=lambda request_id: int(request_id[1:]))
    return [copy.deepcopy(_requests[request_id]) for request_id in ordered]


def update_request(request_id, status, approved_by=_UNSET) -> dict:
    """Controlled write path for Engineer B.

    B decides whether a transition is legal; this function guarantees the
    resulting record is valid (known status, approver present once approved).
    The change is built on a copy and swapped in only after validation passes.
    """
    validate_request_id(request_id)
    if request_id not in _requests:
        raise ValueError(f"unknown request id {request_id!r}")

    updated = copy.deepcopy(_requests[request_id])
    updated["status"] = status
    if approved_by is not _UNSET:
        updated["approved_by"] = approved_by

    _validate_record(updated, request_id)
    _requests[request_id] = updated
    return copy.deepcopy(updated)


def clear_requests() -> None:
    """Empty the store. Intended for tests and for simulating a restart."""
    _requests.clear()


# --------------------------------------------------------------------------
# Persistence
# --------------------------------------------------------------------------

def save_requests(path) -> None:
    """Write all requests to path as a JSON list, atomically.

    Data goes to a temporary file in the same folder first and replaces the
    real file only after the write succeeded, so a failure never destroys a
    previously valid file.
    """
    text = json.dumps(list_requests(), indent=2)
    directory = os.path.dirname(os.path.abspath(path))

    handle = tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=directory,
        prefix=".requests-", suffix=".tmp", delete=False,
    )
    temp_path = handle.name
    try:
        with handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    except BaseException:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise


def load_requests(path) -> int:
    """Load and validate requests from path. Returns how many were loaded.

    * Missing file: treated as a first run; the store is left unchanged, returns 0.
    * Anything invalid (bad JSON, empty file, missing keys, duplicate IDs,
      invalid values): raises ValueError and the store is left unchanged.
    * Only a fully valid file replaces the store.
    """
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return 0
    except json.JSONDecodeError as error:
        raise ValueError(f"{path} is not valid JSON: {error}") from None
    except UnicodeDecodeError:
        raise ValueError(f"{path} is not a readable UTF-8 text file") from None

    if not isinstance(data, list):
        raise ValueError(f"{path}: top level must be a list of requests")

    loaded: dict[str, dict] = {}
    for position, record in enumerate(data, start=1):
        _validate_record(record, f"record {position}")
        if record["id"] in loaded:
            raise ValueError(
                f"record {position}: duplicate request id {record['id']!r}"
            )
        loaded[record["id"]] = record

    _requests.clear()
    _requests.update(loaded)
    return len(loaded)
