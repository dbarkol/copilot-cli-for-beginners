# Code Review Checklist — `book_app.py`

> Review date: 2026-03-13
> Files reviewed: `book_app.py`, `books.py`, `utils.py`

## 🔴 Critical — Data Loss Risks & Crashes

- [ ] **F1 — Empty title/author persisted to disk** (`book_app.py:33-39`)
  User can press Enter through all prompts, creating `Book(title="", author="", year=0)` that is saved to `data.json`. Empty-titled books are then impossible to remove. Note: `utils.py` already implements the fix pattern (re-prompt loops) but `book_app.py` never imports it.

- [ ] **F2 — `EOFError` unhandled on all `input()` calls** (`book_app.py:76,84`)
  Eight unprotected `input()` calls. The `while True` loops in `handle_year` are particularly dangerous — they produce an infinite traceback storm when stdin is closed (piped input, CI, terminal disconnect).

- [ ] **F3 — `KeyboardInterrupt` unhandled** (`book_app.py:121-137`)
  No `try/except` around `main()`. Pressing Ctrl+C during any prompt produces a raw traceback instead of a graceful exit message.

## 🟠 High — Bugs & Incorrect Behavior

- [ ] **F4 — `remove_book()` return value silently discarded** (`book_app.py:49-51`)
  `remove_book()` returns a `bool`, but the CLI ignores it and always prints "Book removed if it existed" — giving no real feedback on success or failure.

- [ ] **F5 — Year `0` used as silent default; no range validation** (`book_app.py:37-38`)
  Blank year input silently becomes `0` and is saved as a real value. Negative years and far-future years (e.g., `999999`) are also accepted without complaint.

- [ ] **F6 — `save_books()` raises unhandled `OSError`** (`books.py:33-36`)
  Disk-full or permission errors during `save_books()` crash with an unhandled exception. Worse, the in-memory list has already been modified, leaving memory and disk out of sync for the rest of the session.

- [ ] **F7 — Inverted year range silently returns empty list** (`book_app.py:91`)
  Entering `start=2000, end=1900` returns no results with no warning that the range is backwards. The user sees "No books found" and has no hint they made an input mistake.

## 🟡 Medium — Maintainability & Robustness

- [ ] **F8 — Empty query accepted with inconsistent behavior** (`book_app.py:57,66`)
  Empty `find_by_author("")` matches nothing (or only books with a blank author). Empty `search_books("")` matches *everything* because `"" in any_string` is always `True` in Python. Neither warns the user.

- [ ] **F9 — Duplicate books added without warning** (`book_app.py:39`)
  `add_book()` appends unconditionally. The same book can be added many times, but `find_book_by_title` only returns the first match — making duplicates unreachable by `remove` or `mark_as_read`.

- [ ] **F10 — Module-level `BookCollection()` triggers I/O at import** (`book_app.py:7`)
  `collection = BookCollection()` runs `load_books()` at import time, reading `data.json` immediately. This breaks when run from a different working directory and makes the module difficult to test without monkeypatching.

- [ ] **F11 — Relative `DATA_FILE` depends on working directory** (`books.py:5`)
  `DATA_FILE = "data.json"` resolves relative to `os.getcwd()`, not the script's directory. Running `python /path/to/book_app.py list` from a different directory looks for `data.json` in the wrong place.

## 🟢 Low — Style & Minor Improvements

- [ ] **F12 — Legacy `typing.List` / `Optional` imports** (`book_app.py:2`, `books.py:3`)
  On Python 3.9+, built-in `list[Book]` and `Book | None` are valid type hints. The `from typing import List, Optional` imports are unnecessary.

- [ ] **F13 — Missing return type hints on model methods** (`books.py:17,21,33`)
  `__init__`, `load_books`, and `save_books` lack `-> None` return annotations.

- [ ] **F14 — No string length limits on user input** (`book_app.py:33-35`)
  No upper bound on title, author, or year string length. A user (or fuzzer) could paste megabytes of text that gets written to `data.json` and loaded into memory on every subsequent run.

---

**Summary:** 3 critical · 4 high · 4 medium · 3 low — **14 issues total**
