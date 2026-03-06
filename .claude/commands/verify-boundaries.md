Verify data flow at a pipeline boundary between two adjacent engines.

Boundary: $ARGUMENTS (e.g., "source normalization" or "all")

Steps:
1. If "all": run `python3 scripts/verify_metadata_flow.py --verbose`
2. If specific boundary (two engine names):
   a. Read upstream engine's SPEC.md §3 (Output Contract).
   b. Read downstream engine's SPEC.md §2 (Input Contract).
   c. If code exists: compare actual data models in code.
   d. If integration tests exist: run them.
   e. Run `python3 scripts/verify_metadata_flow.py --boundary <upstream> <downstream> --verbose`
3. Report:
   - Schema match: does every field downstream expects exist in upstream output?
   - Metadata flow: does downstream output preserve all upstream metadata?
   - Type consistency: do field types match?
   - Missing integration tests (if any).
