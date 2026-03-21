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

## SPEC-NOTE-3: §5 check 4 sharh-majority check not implemented for 3-layer texts

**Found:** Session 6 deep review (March 2026).
**Location:** `SPEC.md` §5 check 4 (line ~1484)
**Issue:** The SPEC says "Layer 2 (sharh) should be the majority in a sharh." Implementation only checks `matn_ratio >= 0.40`. For 2-layer texts this is equivalent (matn < 40% → sharh > 60%). For 3-layer texts (matn + sharh + hashiyah), sharh could be < 50% while matn is < 40%, and no warning fires.
**Implementation:** Only matn ratio check exists. Sharh-majority check is absent.
**Severity:** Inert until L-006 (hashiyah detection) is resolved. 3-layer layer detection is not implemented yet — all current multi-layer sources produce only matn + sharh segments.
**Resolution:** When L-006 is implemented, add a parallel check: if genre is sharh/hashiyah AND `sharh_ratio < 0.50`, warn. Requires tracking per-layer-type character counts separately.
