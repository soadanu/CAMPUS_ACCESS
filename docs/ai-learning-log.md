# AI Learning Log

Engineer A: Solomon Adanu

This log records how AI was used for learning, how each piece of advice was checked, and what was kept, changed or rejected.

## Learning cycles

### Cycle 1: What Engineer A needs to understand before coding

- **Date:** 2026-10-14
- **I asked:** for an explanation of everything Engineer A needs before any code.
- **AI explained:** the shape of a request; why a dictionary fits; validating before changing data; validation vs. sanitization; making IDs from existing data; returning copies; saving safely; loading all-or-nothing with duplicate-ID detection; and the agreement with Engineer B.
- **How I verified:** I did not take the explanation on trust. I tested the key claims by running code: the digit check in the Python REPL (Cycle 2), the 14 unit tests (Cycle 3), and the failed-save and bad-file tests, which try to break the program on purpose.
- **Result:** The explanation held up. Each rule it described now has a test that proves it, and I can explain why each rule exists.

### Cycle 2: Non-ASCII digits in IDs

- **Date:** 2026-10-14
- **AI claimed:** `str.isdigit()` accepts non-ASCII numerals, so it is unsafe for ID checks. The brief says only digits 0-9 are allowed.
- **How I verified:** In the Python REPL I ran these checks:
  - `"٣".isdigit()` returned `True`, so `isdigit()` accepts an Arabic-Indic digit.
  - `"٣" in "0123456789"` returned `False`, so a check against the ASCII digits rejects it.
  - The pattern `A[0-9]{3,}` with `fullmatch` accepted `A001` and rejected `A٠٠١`.
  - `fullmatch` rejected `"A001\n"`, but `match` accepted it. That is why the code uses `fullmatch`.
  - In Python, `\d` also matches `٣`, so `[0-9]` must be used instead of `\d`.
- **Result:** Claim confirmed. The code uses `[0-9]` with `fullmatch`, and the tests include Arabic-Indic and full-width digit IDs.

### Cycle 3: Writing the storage module and its tests

- **Date:** 2026-10-14
- **AI provided:** `access_cards/storage.py` and `tests/test_storage.py` (14 tests).
- **How I verified:** I ran `python3 -m unittest discover -s tests -v` myself and read each function until I could explain it.
- **What I changed or rejected:**
  - I asked whether `storage.py` should be changed into a dictionary. I learned it already stores requests in a dictionary, and that B should use `storage.get_request` instead of reading the store directly.
  - I kept the JSON file as a list of records instead of a dictionary. A JSON object with a repeated key loses one entry without any error, so duplicate IDs would not be detected.
  - I asked for the standard project structure and changed the code from flat files to the `access_cards` package, updating the imports in `main.py` and the tests.
- **Result on my machine:** 14 tests ran and all passed (`OK`).

### Cycle 4: Project structure

- **Date:** 2026-10-14
- **AI advised:** moving from a flat layout to an `access_cards/` package, which changes the imports in `main.py` and the tests.
- **How I verified:** I made the change and reran the tests.
- **Result:** The tests still pass from the project root. The import must be `from access_cards import storage`. Importing functions straight from `access_cards` fails, because the functions live in `storage.py`, not in `__init__.py`.

## Problems I solved

### Problem 1: the tests could not find `storage`

**Problem:** the tests failed with `ModuleNotFoundError: No module named 'storage'`.

**Investigation:** `ls` showed the folder as `'functions '`, with a trailing space in its name. That is why `cd functions` failed and why `storage.py` was not where Python looked for it.

**Fix:** I moved the file with `git mv "functions /storage.py" storage.py` (quoting the name), then reorganized it into the `access_cards` package and reran the tests.

**Lesson:** read error messages and `ls` output carefully, because quotes can reveal a hidden space in a name. Always run the tests from the project root, and quote any path that contains a space.

### Problem 2: `workflow.py` crashed on approve

**Problem:** approving a request crashed with `NameError: name 'ALLOWED_STATUSES' is not defined` on the line `req = ALLOWED_STATUSES[request_id]`.

**Investigation:** `ALLOWED_STATUSES` is only the list of valid status names, defined in `storage.py`. It does not hold requests, so it cannot be looked up by request ID. The code was also using it without importing it.

**Fix:** get the request with `storage.get_request(request_id)`, check its status first, then change it with `storage.update_request(...)`.

**Lesson:** one module should not reach into another module's data. Use the agreed functions, because they are where the validation lives.

## Reflection

**What AI taught me that I did not know before:**  ..... 
- Validate everything first and change the data last, so a failed action leaves nothing changed.
- `isdigit()` accepts non-ASCII digits, so ID checks need `[0-9]`.
- Saving through a temporary file and `os.replace` protects a good file from a failed save.
- A JSON list can detect duplicate IDs; a JSON object cannot.
- Return copies from lookups, so other code cannot bypass the rules.

**AI advice I verified, adjusted or rejected:**
- Verified: the non-ASCII digit claim (ran it in the REPL) and the safe-save behavior (the failed-save test).
- Adjusted: I changed the project from flat files to the `access_cards` package.
- Kept after questioning it: the JSON list format, instead of a dictionary.
- Corrected: the wrong status lookup in `workflow.py`.

**What I can now explain without AI:**
- How `create_request` validates, builds a record and stores it.
- How the next ID is made, and why it stays unique after a restart.
- How `save_requests` and `load_requests` protect valid data.
- Why I return copies instead of stored records.
- How `update_request` and B's workflow rules share responsibility.

**What I would improve with another day:**
- Make the menu catch `OSError` as well as `ValueError`, so a bad file path cannot crash it.
- Tell the user when no data file is found, so a typo in the path is not mistaken for a first run.
- Add a list of authorized staff approvers.
- Add more tests for IDs past A999.

## Questions I can answer in my own words

- **Why is a dictionary appropriate here?** I can find a request directly by its ID, and an ID can only appear once as a key, so duplicates are impossible in memory.
- **How do I avoid duplicate IDs after a restart?** When the file is loaded, the next ID is the highest number found plus one, so A002 follows A001 instead of starting again at A001.
- **Why can data from a local JSON file still be unsafe?** A person can edit it by hand, a crash can leave it half written, and another program can change it. So I check every record on load and reject anything wrong.
- **What is the difference between validation and sanitization?** Validation checks input and rejects it if it is wrong. Sanitization changes the input to make it acceptable. My code mostly validates: it rejects `" F001"` instead of trimming it.
- **How would I test that a failed save does not overwrite a valid file?** Save a valid file, force the last step of saving to fail, then check the file still has its original content and no temporary file is left behind. My test does this by making `os.replace` raise an error.