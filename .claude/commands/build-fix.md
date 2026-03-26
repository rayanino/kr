---
description: "Iterative error resolution — fix a failing test or type error in max 3 cycles"
allowed-tools: ["Bash(python *)", "Bash(python3 *)", "Bash(pytest *)", "Read", "Edit", "Grep", "Glob"]
---
Fix the specified failing test or error iteratively:

Arguments: $ARGUMENTS should be a failing command (e.g., "pytest engines/excerpting/tests/test_phase1_split.py::test_partition -x")

## Cycle (repeat up to 3 times)

1. **Run** the failing command and capture full output
2. **Analyze** the root cause — read source, check SPEC, trace data flow
3. **Apply** MINIMAL fix (smallest diff that addresses the root cause)
4. **Verify** by re-running the command

## Rules

- MAX 3 cycles. Each cycle MUST try a DIFFERENT approach. If cycle 1 failed with approach A, cycle 2 must try approach B — not a variation of A.
- After 3 failed cycles: STOP. Report what was tried, what failed, and what needs a different approach. Do NOT try a 4th time.
- If the fix passes: run the FULL engine test suite (`python -m pytest engines/<engine>/tests/ -x -q --tb=short`) to check for regressions.
- Prefer fixing the SOURCE over fixing the TEST. Tests guard SPEC rules and should not be weakened.
- If the error is in a SPEC rule (not the implementation), report it as SPEC-AMBIGUITY rather than changing code.
- After successful fix: run `python -m pyright <modified-files>` to verify type safety.

## Output

After each cycle, report:
```
Cycle N/3: [PASS|FAIL]
  Approach: [what was tried]
  Result: [what happened]
  Next: [what to try next | DONE | ESCALATE]
```
