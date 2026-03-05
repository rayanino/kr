Begin a work session on the specified engine. Follows the pre-work protocol from root CLAUDE.md.

Engine: $ARGUMENTS

Steps:
1. Read `engines/$ARGUMENTS/CLAUDE.md` for orientation.
2. Read `engines/$ARGUMENTS/SPEC.md` for the full specification.
3. Identify input/output schemas from SPEC §2 and §3, read them from `schemas/`.
4. Run existing tests: `cd engines/$ARGUMENTS && python -m pytest tests/ -v --tb=short`
5. Compare test results against CLAUDE.md stated counts. Report discrepancies.
6. Summarize: current state, known gaps, what needs to be built next.
