Run all KR tests and report results. If an engine name is provided, run only that engine's tests.

If argument provided: `cd engines/$ARGUMENTS && python -m pytest tests/ -v --tb=short`
If no argument: `python -m pytest engines/*/tests/ shared/*/tests/ -v --tb=short`

After running, compare test counts against the engine's CLAUDE.md and report any discrepancies.
