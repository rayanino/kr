---
description: Review branch diff for AI-generated code patterns and clean them up.
allowed-tools: Bash(git diff:*), Bash(git log:*), Read, Edit, Grep
---
Review ALL uncommitted changes (or changes since branching from master if on a feature branch) for AI-generated code patterns that reduce clarity and maintainability.

**Target patterns to find and fix:**

1. **Unnecessary try/except** — wrapping infallible operations (dict access on known keys, attribute access on typed objects, Path operations on verified paths) in try/except blocks
2. **Over-commenting** — comments that restate the code (`# increment counter` above `counter += 1`), comments explaining obvious type hints, or comments on every line of a straightforward function
3. **Defensive coding for impossible cases** — checking `if x is not None` when `x` is typed as `str` (not Optional), guarding against types that the type system already prevents
4. **Premature abstractions** — utility functions called exactly once, base classes with a single subclass, config objects for 1-2 values, factory patterns for a single product
5. **Redundant type annotations** — `x: int = 5` where inference suffices in local scope (NOT in function signatures or Pydantic fields — those stay)
6. **Over-generic error handling** — `except Exception as e: logger.error(f"Error: {e}"); raise` that adds nothing, or catch-log-reraise patterns where the log adds no context beyond the traceback
7. **Unnecessary imports** — imported names that are never used in the file
8. **Verbose conditionals** — `if x == True:` instead of `if x:`, `if len(lst) > 0:` instead of `if lst:`
9. **Dead code behind always-true/false conditions** — unreachable branches, commented-out code blocks left "for reference"
10. **Unnecessary f-strings** — `f"static string"` with no interpolation, `f"{variable}"` where `str(variable)` or just `variable` suffices

**Rules:**
- NEVER remove or modify docstrings on public functions (those are intentional)
- NEVER remove type hints from function signatures or Pydantic model fields
- NEVER touch Arabic text handling code — those "defensive" checks are intentional safety rails
- NEVER remove error handling at system boundaries (file I/O, API calls, user input)
- Preserve ALL comments that explain WHY, only remove comments that restate WHAT

**Process:**
1. Run `git diff --stat` (or `git diff master...HEAD --stat` on branches) to see changed files
2. For each changed `.py` file, read the diff hunks
3. Identify patterns from the target list above
4. For each finding, fix it directly — do not just report
5. After all fixes, run `python -m pyright` on modified files to verify no type regressions
6. Run `python -m pytest` on affected engine tests to verify no behavioral changes

If $ARGUMENTS is provided, limit the review to those specific files or directories.
