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

---

## Excerpting Engine Errata

## SPEC-NOTE-4: §4.3 mid_sentence word-final heuristic produces 92% word-merge corruption — RESOLVED

**Found:** Excerpting Session 1 review (March 2026).
**Severity:** T-1 (Silent Text Corruption). Blocked Phase 2 deployment.
**Problem:** SPEC §4.3 defined mid_sentence separator as empty string `""`, with a word-final heuristic (ة, ى, tanwin, whitespace) to insert a space when the page break falls between words. Empirically measured across all 5 experiment fixture packages: 270 of 294 (92%) mid_sentence boundaries merged two separate Arabic words into garbage (e.g., "للخطأوَلِهَذَا", "كالشاهدوفتواه"). The heuristic caught only 8% of actual word boundaries because most Arabic words end with regular consonants (ن, ل, ب, د, etc.). Zero genuine mid-word splits existed in any fixture package.
**Resolution:** Changed mid_sentence separator from `""` to `" "` (always insert space). Removed the word-final heuristic entirely (_WORD_FINAL_CHARS, _TANWIN_DIACRITICS, _should_insert_space_mid_sentence). Rationale: Shamela page breaks always fall between complete words — Arabic print does not split words across pages. Empirically verified: 0/294 genuine mid-word splits. Updated SPEC §4.3 separator table and explanation. Updated all tests.
**Fixed in:** SPEC-NOTE-4 fix commit, SPEC.md §4.3, phase1_assembly.py.

## SPEC-NOTE-5: §4.3 tanwin fathah + alif (ـًا) not detected as word-final — RESOLVED (subsumed)

**Found:** Excerpting Session 1 review (March 2026).
**Severity:** Low. 1 occurrence in 294 mid_sentence boundaries across 5 fixture packages.
**Problem:** The accusative indefinite form "كتابًا" ends with alif (U+0627) as the last code point, with tanwin fathah (U+064B) as a combining character before it. The old heuristic checked only the last code point, missing this form.
**Resolution:** Subsumed by SPEC-NOTE-4 fix. The word-final heuristic was removed entirely — mid_sentence now always inserts space. This edge case no longer exists.
**Fixed in:** Same commit as SPEC-NOTE-4.

## SPEC-NOTE-6: §4.2 EXCLUDE_KEYWORDS expanded beyond SPEC list — OPEN

**Found:** Excerpting Session 1 review (March 2026).
**Severity:** Documentation. No functional impact (zero false positives, one additional true positive).
**Problem:** SPEC §4.2 lists 5 bibliography exclusion keywords (مصادر, مراجع, فهرس, ثبت المصادر, المراجع). CC's implementation expanded to 13 keywords, adding compound forms: المصادر, مصادر ومراجع, المصادر والمراجع, فهرس المصادر, فهرس المراجع, قائمة المراجع, قائمة المصادر, قائمة المصادر والمراجع. Tested against all 322 headings across 5 fixture packages: zero false positives, one additional true positive ("المصادر والمراجع" in 07_balagha).
**Status:** SPEC §4.2 should be updated to include the expanded list.

## SPEC-NOTE-7: §4.2 "word-boundary-aware" wording contradicts example — OPEN

**Found:** Excerpting Session 1 review (March 2026).
**Severity:** Documentation.
**Problem:** SPEC §4.2 says keyword matching is "word-boundary-aware" but also says "مصادر الأحكام" must NOT match. Word-boundary matching on "مصادر" WOULD match "مصادر الأحكام" (the keyword is a word within the heading). CC correctly resolves by using exact-match (full heading must equal keyword after noise stripping), which prevents the false positive.
**Status:** SPEC §4.2 should be reworded: "exact match after noise stripping" instead of "word-boundary-aware."
