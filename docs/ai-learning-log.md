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

**What AI taught me that I did not know before:**
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


# AI Learning log

Engineer B: Nnenna Uzoezie

This log records how AI was used for learning, how each piece of advice was checked, and what was kept, changed or rejected.

## Learning cycles

### Cycle 1: What Engineer B needs to understand before coding
B1. Show a newly created request with status requested. B2. Reject requested→issued and prove status stays requested. B3. Reject approval with blank approver and preserve previous data. B4. Approve with M01, then issue and return. B5. Reject a second return and an attempt to issue a returned card. B6. Invalid menu options must display helpful feedback and let the user retry.


### Cycle 3: Writing the workflow module and its tests
- **AI provided:** `tests/test_workflow.py` and main.py (14 tests).
- **How I verified:** I ran `python3 -m unittest discover -s tests -v` myself and read each function until I could explain it.
- **What I changed or rejected:**
  - I asked for outline for workflow.py, then made some modifcations.
  - I kept the test files generated
- **Result on my machine:** 14 tests ran and all passed (`OK`).

### Cycle 4: Project structure
- **AI advised:** moving from a flat layout to an `access_cards/` package, which changes the imports in `main.py` and the tests.
- **How I verified:** I made the change and reran the tests.
- **Result:** The tests still pass from the project root. The import must be `from access_cards import storage`. Importing functions straight from `access_cards` fails, because the functions live in `storage.py`, not in `__init__.py`.

## Problems I solved

### Problem 1: the tests could not find campus

**Problem:** the tests failed with `ModuleNotFoundError: No module named campus in 2 main.py

**Investigation:** trace the problem to main.py line 2 and found out i mistakenly type campus instead of access_cards

**Fix:** corrected the name

**Lesson:** error reading from the terminal helps to rectify error

### Problem 2: `workflow.py` crashed on approve

**Problem:** approving a request crashed with `NameError: name 'ALLOWED_STATUSES' is not defined` on the line `req = ALLOWED_STATUSES[request_id]`.

**Investigation:** `ALLOWED_STATUSES` is only the list of valid status names, defined in `storage.py`. It does not hold requests, so it cannot be looked up by request ID. The code was also using it without importing it.

**Fix:** get the request with `storage.get_request(request_id)`, check its status first, then change it with `storage.update_request(...)`.

**Lesson:** one module should not reach into another module's data. Use the agreed functions, because they are where the validation lives.

## Reflection

**What AI taught me that I did not know before:**
- Validate everything first and change the data last, so a failed action leaves nothing changed.

**AI advice I verified, adjusted or rejected:**
- Adjusted: I changed the project from flat files to the `access_cards` package.
- Kept after questioning it: the JSON list format, instead of a dictionary.
- Corrected: the wrong status lookup in `workflow.py`.


## Questions I can answer in my own words


1. What is an illegal transition?

An illegal transition occurs when a record switches from its current state to a target state that breaks business logic flow rules, skipping vital operational protocols. For example, moving a card request from requested directly to issued without going through approved is illegal. It presents a severe operational vulnerability.

2. Why validate before mutation?

Validating conditions before updating data properties guarantees system integrity. If processing errors or mid-execution failures strike midway through an action, the data remains unpolluted. Mutating first and checking later forces costly rollback mechanisms and risks writing incomplete or invalid objects directly to production storage.

3. How do you keep the CLI from crashing on a typo?

• Input Isolation: Whitespace cleanup via .strip() handles text offsets, while rigid validation sets (if choice not in {...}) trap bad entries cleanly before they pass to inner execution lines.
• Global Trap Blocks: Wrapping dynamic action logic in centralized try/except bubbles absorbs unexpected edge cases safely, ensuring a bad typo drops back to the prompt loop rather than exiting the sys.exit() runtime pathway.

4. What should happen if an unknown ID is used?

The operation must fail early, reporting the failure gracefully to the presentation layer without raising execution-breaking errors or modifying neighboring records. The interface must explicitly return a message stating that the lookup identifier does not exist, then safely return the user back to the primary menu loop.

5. How do you test that an error leaves the original record unchanged?

Capture a deep copy or snapshot reference of the record object before sending it through an invalid validation transaction. Once the error triggers, compare every property field of the post-execution object directly against the original snapshot state. If any byte or value shifts on a rejected transaction, the safety invariant fails.

6. Why is a status check more reliable than merely hiding a menu option?

Hiding menu choices only patches the user interface (security through obscurity). It provides zero protection if an actor bypasses the front-end menu completely by script injections, race conditions, or unmapped API hooks. Backend state checks act as an absolute barrier; they guard the data entry line itself, making malicious or accidental state mutations impossible regardless of how a command arrives.