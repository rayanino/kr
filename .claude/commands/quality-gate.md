---
description: Run a comprehensive quality check on an engine. Usage /quality-gate <engine>. Use at session checkpoints for full validation beyond auto-hooks.
allowed-tools: Bash(python *), Bash(python3 *), Bash(pytest *), Read
---
Run ALL validation checks for engine `$ARGUMENTS` and produce a summary.

Run these checks in sequence, capturing pass/fail for each:

1. **Tests:** `python -m pytest engines/$ARGUMENTS/tests/ -v --tb=short`
2. **Type checking:** `python -m pyright engines/$ARGUMENTS/src/`
3. **SPEC value validation:** `python3 scripts/validate_spec_values.py engines/$ARGUMENTS` (skip if script missing)
4. **Pre-review checks:** `python3 scripts/pre_review_checks.py engines/$ARGUMENTS/src/*.py --engine $ARGUMENTS` (skip if script missing)
5. **Pydantic fields:** `python3 scripts/check_pydantic_fields.py engines/$ARGUMENTS/src/contracts.py` (skip if contracts.py missing)
6. **Metadata flow:** `python3 scripts/verify_metadata_flow.py` (skip if script missing)
7. **Build metrics:** `python3 scripts/update_build_metrics.py engines/$ARGUMENTS` (skip if script missing)

After all checks complete, produce a summary table:

```
=== Quality Gate: [engine] ===
  Tests:           PASS (N passed) | FAIL (N failed / M total)
  Type checking:   PASS | FAIL (N errors)
  SPEC values:     PASS | SKIPPED | FAIL
  Pre-review:      PASS | SKIPPED | FAIL (N issues)
  Pydantic:        PASS | SKIPPED | FAIL
  Metadata flow:   PASS | SKIPPED | FAIL
  Build metrics:   PASS | SKIPPED | FAIL

  Overall: PASS | FAIL
```

Tests and type checking are blocking (FAIL = overall FAIL). Other checks are advisory.
