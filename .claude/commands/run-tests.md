Run tests and report results. If an argument is provided, run only that component's tests.

If argument is an engine name: `cd engines/$ARGUMENTS && python -m pytest tests/ -v --tb=short`
If argument is a shared component: `cd shared/$ARGUMENTS && python -m pytest tests/ -v --tb=short`
If no argument: `python -m pytest engines/*/tests/ shared/*/tests/ -v --tb=short`

After running:
1. Report: total passed, failed, errors, skipped.
2. For each failure: file path, test name, one-line summary.
3. Compare counts to the component's CLAUDE.md. Report discrepancies.
