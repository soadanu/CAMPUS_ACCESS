# AI Learning Log

Engineer A: Solomon Adanu

This log records how AI was used for learning, how each piece of advice was checked, and what was kept, changed or rejected. Entries marked _fill in_ must be completed in your own words after you have tried things yourself.

## Learning cycles

### Cycle 1: What Engineer A needs to understand before coding

- **Date:** 2026-10-14
- **I asked:** for an explanation of everything Engineer A needs before any code.
- **AI explained:** record shape and why a dictionary fits; validate before mutate; validation vs. sanitization; ID generation from existing data; returning copies; atomic saving; all-or-nothing loading with duplicate-ID detection; the contract with Engineer B.
- **How I verified:** _fill in (for example: read the Python docs for `json`, `os.replace` and `re.fullmatch`, and tried the mini exercises)._
- **Result:** _fill in._

### Cycle 2: Non-ASCII digits in IDs

- **Date:** 2026-10-14
- **AI claimed:** `str.isdigit()` accepts non-ASCII numerals, so it is unsafe for ID checks.
- **How I verified:** _fill in. Suggested check in the Python REPL: `"٣".isdigit()` and `"٣" in "0123456789"`, then try `A٠٠١` against the ID check._
- **Result:** _fill in._

### Cycle 3: Writing the storage module and its tests

- **Date:** 2026-10-14
- **AI provided:** `access_cards/storage.py` and `tests/test_storage.py` (14 tests).
- **How I verified:** I ran `python3 -m unittest discover -s tests -v` myself and read each function until I could explain it.
- **What I changed or rejected:** _fill in (for example, a rule I adjusted, a test I added, or a decision I disagreed with)._
- **Result on my machine:** _fill in (tests run, passed or failed)._

### Cycle 4: Project structure

- **Date:** 2026-10-14
- **AI advised:** moving from a flat layout to an `access_cards/` package, which changes the imports in `main.py` and the tests.
- **How I verified:** I made the change and reran the tests.
- **Result:** _fill in._

## A problem I solved

**Problem:** the tests failed with `ModuleNotFoundError: No module named 'storage'`.

**Investigation:** `ls` showed the folder as `'functions '`, with a trailing space in its name. That is why `cd functions` failed and why `storage.py` was not where Python looked for it.

**Fix:** I moved the file with `git mv "functions /storage.py" storage.py` (quoting the name), then reorganized it into the `access_cards` package and reran the tests.

**Lesson:** _fill in._

## Reflection

**What AI taught me that I did not know before:** _fill in._

**AI advice I verified, adjusted or rejected:** _fill in._

**What I can now explain without AI:** _fill in._

**What I would improve with another day:** _fill in._

## Questions I can answer in my own words

- Why is a dictionary appropriate here? _fill in_
- How do I avoid duplicate IDs after a restart? _fill in_
- Why can data from a local JSON file still be unsafe? _fill in_
- What is the difference between validation and sanitization? _fill in_
- How would I test that a failed save does not overwrite a valid file? _fill in_
