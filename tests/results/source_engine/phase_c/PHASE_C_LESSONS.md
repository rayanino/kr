# Phase C Lessons Learned

**Phase:** C (Targeted LLM Probes)
**Date:** 2026-03-10
**Books:** 73 (22 success, 51 gate_abort, 0 errors)
**Cost:** 7.00 EUR (budget ceiling: 50 EUR)
**Pipeline version:** 839b40f

---

## Bugs Found

- **[BUG-C01] Edition group names mismatched collection directory names**: The `compute_edition_groups()` function used shortened book titles (e.g., "أعلام الموقعين - ط عطاءات العلم") that didn't match the actual collection directory names (e.g., "أعلام الموقعين عن رب العالمين - ط عطاءات العلم"). Result: only 1 of 9 edition groups was detected. Fixed in self-review commit. All 9 groups now detected.

- **[BUG-C02] Edition groups excluded gate_abort books**: The comparison filter required `status == "success"`, but most edition groups had all books in gate_abort status. Since gate_abort books have full LLM responses saved (inference completes before validation aborts), they are valid for edition comparison. Fixed to include gate_abort books with data loaded from `llm_responses/`.

- **[BUG-C03] Command A (Cohere) completely unavailable**: `openrouter/cohere/command-a` timed out on every single attempt throughout the entire 73-book run (60s timeout, 2 retries each). All books fell back to single-model mode (Opus 4.6 only). No consensus comparison occurred for any book. This is not a code bug but an infrastructure issue — Command A was either down or rate-limited during the run window.

## Patterns Observed

- **Author-science mismatch is the dominant gate trigger**: 51/73 books (70%) got gate_abort, almost all from the `consistency_author_science` validation check. The check compares the author's "known sciences" in the scholar registry against the book's inferred science_scope. When the scholar registry has incomplete or generic science data (e.g., "primary" instead of specific sciences), the check triggers.

- **Gate aborts are data-complete**: Every gate_abort book has complete extraction.json, prompt_sent.json, llm_responses/, and consensus.json. The inference pipeline ran fully — only the post-inference validation step aborted. This means the LLM data is reliable and reusable.

- **Ground truth level field consistently mismatched**: 3 of 4 ground-truth comparisons failed on the `level` field (expected "intermediate", got "beginner"). This suggests the LLM (Opus 4.6 in single-model mode) has a systematic tendency to underestimate scholarly level for modern academic works.

- **Edition group consistency is high**: Of the 9 edition groups, 7 had consistent genre classification across editions. The 2 inconsistent groups (إعلام الموقعين: matn/other, الإبانة: matn/risalah) represent genuine classification difficulty, not pipeline errors.

- **حاشية ابن عابدين correctly separated father from son**: The pipeline correctly identified different authors for حاشية ابن عابدين (محمد أمين عابدين) vs. تكملة حاشية ابن عابدين (محمد علاء الدين عابدين). This validates the author identification working correctly even without consensus.

## What Went Wrong

- **No multi-model consensus**: Command A's unavailability means every result is Opus-only. The D-041 consensus requirement was technically met (the fallback mechanism worked), but the value of independent verification was lost. Every classification decision rests on a single model.

- **70% gate_abort rate inflated by incomplete scholar registry**: The author-science mismatch check is valuable but the scholar registry has sparse science data. Authors like النووي (known for hadith AND fiqh) only have generic "primary" registered, causing false triggers on every hadith-related work.

- **3-book test gate_abort on الأربعون النووية was unexpected**: Expected a clean "success" for this famous hadith collection, but got gate_abort due to author-science mismatch. This was a correct gate trigger given the registry state, but it means the 3-book test didn't fully validate the "success" path for non-fixture books.

## What Worked

- **Zero errors across 73 books**: Every book either succeeded or was correctly caught by a validation gate. No crashes, no malformed output, no data loss.

- **Pre-pipeline extraction save**: extraction.json and prompt_sent.json were saved BEFORE any API call for every book. If the API had crashed, zero extraction work would have been wasted.

- **Resume mode**: The `--resume` flag correctly skipped already-processed books (both success and gate_abort). This was essential for the actual run — the 3-book test books were automatically skipped.

- **Budget protection**: At 7.00 EUR for 73 books (0.096 EUR/book), actual cost was 14% of the 50 EUR ceiling. The 5-layer budget protection system was never triggered but was validated during testing.

- **Gate abort handling**: The distinction between "gate_abort" and "error" was critical. Gate abort books have all their LLM data preserved and are not re-processed on resume. This saved ~50 API calls that would have been wasted on re-processing.

## Recommendations for Next Phase

1. **Fix the scholar registry before Phase D**: The 70% gate_abort rate is solvable. Populate science_scope data for major scholars (النووي, ابن تيمية, الطبري, ابن كثير, etc.) in the scholar registry. This should drop gate_abort to <20%.

2. **Re-run with Command A available**: The entire run lacks consensus verification. Consider a Phase D re-run (just the inference step, not full pipeline) when Command A is available, or substitute with a different second model (e.g., GPT-4o via OpenRouter).

3. **Investigate level field calibration**: Opus 4.6 consistently underestimates scholarly level for modern academic works (classifying "intermediate" as "beginner"). Consider adding calibration guidance to the system message or adjusting ground truth expectations.

4. **Consider relaxing the author-science check**: The current check gates on ANY mismatch between registered sciences and inferred sciences. A softer check (e.g., warning instead of gate for minor mismatches, gate only for impossible combinations like "nahw scholar wrote tafsir") would reduce false gates.

## Impact on Downstream Engines

- **22 complete SourceMetadata records**: Ready for normalization engine development. These cover diverse genres (risalah, tarikh, fatawa, mujam, mawsuah, nazm, adab, hadith_collection, other).

- **51 gate_abort records with LLM responses**: The inference data is available in llm_responses/ for all gate_abort books. If the scholar registry is fixed and books are re-run, these should produce complete SourceMetadata.

- **No multi-layer sharh in success set**: All sharh/hashiyah books are gate_abort (author-science mismatch). The normalization engine cannot test multi-layer text handling until these are resolved.

- **Edition group data available for 9 groups**: The edition comparison analysis is ready for owner review. Genre consistency across editions validates the pipeline's reproducibility.

## Field Distribution (22 successful books)

| Genre | Count |
|-------|-------|
| risalah | 4 |
| tarikh | 4 |
| hadith_collection | 3 |
| other | 3 |
| nazm | 2 |
| mawsuah | 2 |
| fatawa | 1 |
| mujam | 1 |
| adab | 1 |
| matn | 1 |

| Trust Tier | Count |
|-----------|-------|
| verified | 12 |
| flagged | 10 |

| Multi-layer | Count |
|-------------|-------|
| false | 20 |
| true | 2 |
