Run a structured design review on a component or the full system.

Arguments: $ARGUMENTS (e.g., "source" or "boundaries" or "scholarly-value" or "architecture")

Follow the review protocol defined in REVIEW_PROTOCOL.md:

If "source", "normalization", etc. (engine name):
  → Run Type 1: SPEC Integrity Review for that engine.

If "boundaries":
  → Run Type 2: Cross-Engine Boundary Review for all implemented boundaries.

If "scholarly-value":
  → Run Type 4: Scholarly Value Audit.
  → Read reference/USER_SCENARIOS.md and reference/ENTRY_EXAMPLE.md first.

If "architecture":
  → Run Type 5: Architecture Health Check.

If "transformative" or "capabilities":
  → Run Type 3: Transformative Capability Review.
  → Optionally specify an engine: "transformative source"

For all review types:
1. Follow the procedure in REVIEW_PROTOCOL.md exactly.
2. Use the specified output format.
3. Produce at least ONE concrete improvement recommendation.
4. If the review identifies a SPEC change needed, note the exact edit.
