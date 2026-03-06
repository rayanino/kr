Begin a work session on the specified engine or shared component.

Component: $ARGUMENTS

Steps:
1. Read the component's CLAUDE.md for orientation and current state.
2. Read the component's SPEC.md — this is the authoritative specification.
3. Read the input/output schemas from SPEC §2 and §3 (files in `schemas/`).
4. Run existing tests: `python -m pytest <component_path>/tests/ -v --tb=short`
5. Compare test results to CLAUDE.md stated counts. Update CLAUDE.md if stale.
6. Read `NEXT.md` for current priorities and any specific instructions.
7. Summarize: current state, what works, what needs to be built next.

For engines, the component path is `engines/$ARGUMENTS`.
For shared components, the path is `shared/$ARGUMENTS`.
For the scholar interface, the path is `interface/scholar`.
