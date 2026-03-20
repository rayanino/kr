# SPEC Errata — Known Inconsistencies

Collected during build sessions. Fix during a dedicated SPEC maintenance pass after normalization engine build completes.

## SPEC-NOTE-1: §4.B.8 mid_argument confidence contradiction

**Found:** Session 5 review (March 2026).
**Location:** `SPEC.md` §4.B.8
**Issue:** The definition text (line ~1152) says `mid_argument` confidence range is `0.60–0.80`. The concrete example (line ~1200) says final confidence is `0.90`, describing an unspecified blending mechanism: "punctuation 0.95 + argument 0.85 → blended 0.90." This blending is not described anywhere in the SPEC.
**Implementation:** Code follows the definition range (max 0.80). This is correct — the example's 0.90 would require implementing an unspecified algorithm.
**Resolution:** Either update the example to use 0.80, or formally specify the blending mechanism and update the definition range.

## SPEC-NOTE-2: §4.B.8 marker table missing `ولنا`

**Found:** Session 5 review (March 2026).
**Location:** `SPEC.md` §4.B.8 argument flow marker table
**Issue:** The concrete example uses `ولنا حديث` as an evidence chain opener, but `ولنا` is absent from the SPEC's argument marker table. The table lists `والدليل`, `لقوله تعالى`, `ودليله`, `واحتجوا بـ`, `واستدلوا بـ` for evidence chain openers.
**Implementation:** `ولنا` was added to the implementation's evidence_chain.opening_patterns (necessary for the SPEC's own example to work).
**Resolution:** Add `ولنا` to the SPEC marker table under evidence chain openers.
