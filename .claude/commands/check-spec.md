Review the SPEC.md for the specified engine for consistency and completeness.

Engine: $ARGUMENTS

Steps:
1. Read `engines/$ARGUMENTS/SPEC.md` fully.
2. Verify input/output schema references exist in `schemas/`.
3. Check upstream engine's output contract matches this engine's input contract.
4. Check this engine's output contract matches downstream engine's input contract.
5. Verify all VISION.md cross-references (§N.N) and decision references (D-NNN) are valid.
6. Check §9 matches actual code in `engines/$ARGUMENTS/src/`.
7. Flag ambiguous sentences, missing edge cases, or undefined terms.

Report issues with exact quotes and suggested fixes.
