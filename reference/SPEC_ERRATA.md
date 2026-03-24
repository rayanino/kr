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

## SPEC-NOTE-6: §4.2 EXCLUDE_KEYWORDS expanded beyond SPEC list — RESOLVED

**Found:** Excerpting Session 1 review (March 2026).
**Severity:** Documentation. No functional impact (zero false positives, one additional true positive).
**Problem:** SPEC §4.2 listed 5 bibliography exclusion keywords (مصادر, مراجع, فهرس, ثبت المصادر, المراجع). CC's implementation expanded to 13 keywords, adding compound forms. Tested against all 322 headings across 5 fixture packages: zero false positives, one additional true positive ("المصادر والمراجع" in 07_balagha).
**Resolution:** Updated SPEC §4.2 to list all 13 keywords with zero-false-positive validation note.
**Fixed in:** Phase 2 handoff prep session.

## SPEC-NOTE-7: §4.2 "word-boundary-aware" wording contradicts example — RESOLVED

**Found:** Excerpting Session 1 review (March 2026).
**Severity:** Documentation.
**Problem:** SPEC §4.2 said keyword matching is "word-boundary-aware" but also said "مصادر الأحكام" must NOT match. Word-boundary matching on "مصادر" WOULD match "مصادر الأحكام" (the keyword is a word within the heading). CC correctly resolved by using exact-match (full heading must equal keyword after noise stripping), which prevents the false positive.
**Resolution:** SPEC §4.2 reworded to "exact match after Arabic noise stripping" with explicit rationale for why word-boundary matching is insufficient.
**Fixed in:** Phase 2 handoff prep session.

## SPEC-NOTE-8: §7.1 F-DET-5 word-boundary matching overridden by DD-S3-8 — OPEN

**Found:** Excerpting Session 3 planning (March 2026).
**Severity:** CORRECTNESS. SPEC text is wrong; implementation follows DD-S3-8.
**Problem:** SPEC §7.1 F-DET-5 line 1469 says "Pattern matching uses word-boundary-aware search (the lesson from normalization engine S4/S5 — short Arabic stems produce false positives without boundary checks)." This is incorrect for evidence markers. The normalization S4/S5 lesson was about Arabic verb conjugations (genuinely different words, e.g. وذهب matching وذهبت). Evidence markers are nouns/verbs that routinely appear with Arabic proclitic prefixes (ال, و, ف, ب, ل, ك) attached directly without whitespace. Word-boundary checks reject valid matches catastrophically:
- `إجماع`: boundary check rejects 124/163 (76%) — الإجماع, بالإجماع, للإجماع are all valid
- `أخرجه`: boundary check rejects 62/503 (12%) — وأخرجه, فأخرجه are valid prefixed forms
- `رواه`: boundary check rejects 39/511 (7.6%) — only 2 genuine FPs (0.13%) from أرواه
**Empirical data:** 66 fixtures, 16.7M characters. False positive rate without boundary checks: <0.2%. False NEGATIVE rate WITH boundary checks: up to 76%.
**Resolution:** Implementation uses plain substring matching (DD-S3-8). SPEC §7.1 F-DET-5 line 1469 should be updated to: "Pattern matching uses plain substring search. Word-boundary checks are explicitly NOT used — see DD-S3-8."
**Status:** SPEC text not yet updated. Implementation correct per DD-S3-8.

## SPEC-NOTE-9: §7.1 F-DET-9 references nonexistent `author_name_arabic` field — OPEN

**Found:** Excerpting Session 3 planning (March 2026).
**Severity:** Documentation. Implementation uses available field.
**Problem:** SPEC §7.1 F-DET-9 says `resolved_name: layer_map[layer_id].author_name_arabic`. However, `TextLayerSegment` has no `author_name_arabic` field — only `author_canonical_id` (a string like "sch_XXXXX"). The scholar registry that resolves canonical IDs to Arabic display names is not yet built.
**Resolution:** Implementation uses `resolved_name=layer.author_canonical_id` as a placeholder. This will be replaced when the scholar registry provides Arabic name resolution. SPEC §7.1 F-DET-9 should be updated to reference `author_canonical_id` with a note that Arabic name resolution is deferred.
**Status:** SPEC text not yet updated. Implementation correct per DD-S3-9.

## SPEC-NOTE-10: §7.4 V-P3-1 has no error code — RESOLVED

**Found:** Session 5/6 dual-reviewer audit (March 2026).
**Severity:** Documentation.
**Problem:** V-P3-1 (excerpt ID uniqueness) does not specify an error code in §7.4.
**Resolution:** V-P3-1 violation is a programming bug (IDs are deterministic). Implementation raises ValueError instead of emitting an error code.
**Fixed in:** Session 5/6 triage fix commit.

## SPEC-NOTE-11: §7.4 V-P3-8 implementation uses substring search — RESOLVED

**Found:** Session 5/6 dual-reviewer audit (March 2026).
**Severity:** Documentation.
**Problem:** SPEC §7.4 says "ref_marker offset falls within character range." Implementation uses ⌜ref_marker⌝ substring search in primary_text.
**Resolution:** Equivalent because Phase 1 assembly embeds markers in text at their positions. Documented as DD-S56-1.
**Fixed in:** Session 5/6 triage fix commit.

## SPEC-NOTE-12: §7.4 V-P3-1 batch scope vs per-chunk scope — RESOLVED

**Found:** Session 5/6 dual-reviewer audit (March 2026).
**Severity:** Documentation.
**Problem:** SPEC §7.4 says validation runs "for a chunk." V-P3-1 runs at batch level.
**Resolution:** Batch-level is strictly more thorough (catches cross-chunk duplicates). Documented as DD-S56-2.
**Fixed in:** Session 5/6 triage fix commit.
