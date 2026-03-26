---
description: Compare test results between current state and a previous git ref. Usage /regression-check [ref]. Default baseline is HEAD~1. Detects new failures, recovered tests, and stability changes.
allowed-tools: Bash(python *), Bash(python3 *), Bash(pytest *), Bash(git *), Read, Glob, Grep
---
Compare test outcomes between two git states. Parse `$ARGUMENTS` as the baseline ref (default: HEAD~1).

## Procedure

### 1. Run Current Tests
```bash
python -m pytest engines/*/tests/ shared/*/tests/ -q --tb=no 2>&1 | tee /tmp/kr_regression_current.txt
```
Capture: total, passed, failed, skipped, errors. Also capture individual test names+status.

### 2. Run Baseline Tests
```bash
# Stash any uncommitted changes
git stash --include-untracked -q 2>/dev/null
STASHED=$?

# Checkout baseline
git checkout $BASELINE_REF -q 2>&1
if [ $? -ne 0 ]; then
    echo "ERROR: Cannot checkout $BASELINE_REF"
    [ $STASHED -eq 0 ] && git stash pop -q
    exit 1
fi

# Run baseline tests
python -m pytest engines/*/tests/ shared/*/tests/ -q --tb=no 2>&1 | tee /tmp/kr_regression_baseline.txt

# Return to original state
git checkout - -q
[ $STASHED -eq 0 ] && git stash pop -q 2>/dev/null
```

### 3. Compare and Report

Parse both outputs and classify each test:

```
=== Regression Check: [baseline_ref] → HEAD ===

Baseline: N passed, M failed, K skipped
Current:  N passed, M failed, K skipped
Delta:    +X passed, -Y failed

--- REGRESSIONS (was PASS, now FAIL) ---
  [test_name] (engine/module)
  [test_name] (engine/module)

--- NEW FAILURES (new test, FAIL) ---
  [test_name] (engine/module)

--- RECOVERED (was FAIL, now PASS) ---
  [test_name] (engine/module)

--- NEW TESTS (new test, PASS) ---
  [test_name] (engine/module)

--- PERSISTENT FAILURES (still FAIL) ---
  [test_name] (engine/module)

=== Verdict: STABLE | REGRESSED (N new failures) | IMPROVED (+N recovered) ===
```

## Rules
- Always restore git state exactly (checkout back, stash pop).
- If baseline checkout fails (e.g., dirty tree that can't be stashed), skip baseline comparison and just report current results with a warning.
- Group regressions by engine for targeted investigation.
- If `$ARGUMENTS` is empty, default to HEAD~1.
- If `$ARGUMENTS` is a number like `5`, interpret as HEAD~5.
- Show REGRESSIONS section first — that's the critical information.
