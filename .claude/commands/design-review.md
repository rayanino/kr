Run a structured design review on a component or the full system.

Arguments: $ARGUMENTS (e.g., "source" or "boundaries" or "scholarly-value" or "architecture")

If an engine name (source, normalization, etc.):
  → Use kr-integrity to audit that engine's SPEC for technical defects.
  → Check: ambiguous rules, missing error paths, corruption risks, untested assumptions.

If "boundaries":
  → Run scripts/verify_metadata_flow.py and check all contract boundaries.
  → Verify D-023 metadata pass-through at every engine boundary.

If "scholarly-value":
  → Read reference/USER_SCENARIOS.md and reference/ENTRY_EXAMPLE.md.
  → Evaluate whether the current design would produce entries matching the quality target.

If "architecture":
  → Read reference/archive/STEERING.md and skills/shared/ENGINE_PROTOCOL.md.
  → Check for structural issues across the full pipeline.

For all review types:
1. Produce at least ONE concrete improvement recommendation.
2. If the review identifies a SPEC change needed, note the exact edit.
