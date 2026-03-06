Validate an engine's output against its SPEC's output contract.

Engine: $ARGUMENTS

Steps:
1. Read the engine's SPEC.md §3 (Output Contract) for the expected output structure.
2. Read the relevant schema file from `schemas/` if referenced.
3. Find sample output files in `library/` (if any exist from test runs).
4. Check: all required fields present, types correct, metadata complete (D-023).
5. Check: metadata pass-through — does the output preserve all upstream metadata?
6. Report conformance issues with field names and expected vs. actual values.

If no output files exist yet, report what the output schema requires and what validation
checks should be written as the engine is implemented.
