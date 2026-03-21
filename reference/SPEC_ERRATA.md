# SPEC Errata — Known Inconsistencies

All errata resolved during normalization engine evaluation (March 2026).

## SPEC-NOTE-1: §4.B.8 mid_argument confidence contradiction — RESOLVED

**Found:** Session 5 review (March 2026).
**Resolution:** Updated concrete example confidence from 0.90 to 0.80 (matching definition range 0.60–0.80). Removed the unspecified blending mechanism ("punctuation 0.95 + argument 0.85 → blended 0.90"). Code already followed the definition range — only the SPEC example was incorrect.
**Fixed in:** Evaluation session, SPEC.md lines ~1199-1200, ~1208.

## SPEC-NOTE-2: §4.B.8 marker table missing `ولنا` — RESOLVED

**Found:** Session 5 review (March 2026).
**Resolution:** Added `ولنا` to the evidence chain opening patterns in the §4.B.8 argument flow marker table. The implementation already included `ولنا` (necessary for the SPEC's own concrete example to work).
**Fixed in:** Evaluation session, SPEC.md evidence chain row.

## SPEC-NOTE-3: §5 check 4 sharh-majority check not implemented for 3-layer texts — RESOLVED

**Found:** Session 6 deep review (March 2026).
**Resolution:** Added a note to §5 check 4 documenting the 3-layer gap and the condition for fixing it (when L-006 hashiyah detection is implemented). No code change needed — the gap is inert until 3-layer detection exists.
**Fixed in:** Evaluation session, SPEC.md §5 check 4.
