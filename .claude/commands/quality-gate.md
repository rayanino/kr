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

8. **Function complexity:** Scan engine src/ for functions >50 lines:
   `python3 -c "import ast,sys,glob; [print(f'{f}:{n.lineno}: {n.name}() = {n.end_lineno-n.lineno+1} lines') for f in glob.glob(f'engines/{sys.argv[1]}/src/*.py') for n in ast.walk(ast.parse(open(f).read())) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.end_lineno-n.lineno+1>50]" $ARGUMENTS` (skip if no src/ files)
9. **Test coverage ratio:** Count SPEC rules vs test functions:
   `echo "SPEC rules: $(grep -c '§4\.' engines/$ARGUMENTS/SPEC.md 2>/dev/null || echo 0)" && echo "Test functions: $(grep -c 'def test_' engines/$ARGUMENTS/tests/*.py 2>/dev/null || echo 0)"`

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

  Complexity:      PASS | WARN (N functions >50 lines)
  Coverage ratio:  N tests / M rules = X%

  Overall: PASS | FAIL
```

Tests and type checking are blocking (FAIL = overall FAIL). Other checks are advisory.
