Review a SPEC.md for consistency with code and adjacent SPECs.

Component: $ARGUMENTS

Steps:
1. Read the component's SPEC.md fully.
2. Read the component's `src/` code (if any exists).
3. Verify §9 (Current Implementation State) matches actual code.
4. Verify the upstream engine's output matches this engine's §2 (Input Contract).
5. Verify this engine's §3 (Output Contract) matches the downstream engine's §2.
6. Spot-check 2-3 VISION.md cross-references (§N.N) and decision references (D-NNN).
7. Flag ambiguous sentences, missing edge cases, or stale implementation descriptions.

Report issues with exact quotes and suggested fixes.
