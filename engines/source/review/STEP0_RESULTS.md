# Step 0 Results — 14-Fixture Integration Run

**Date:** 2026-03-10
**Status:** GO — 12/13 fixtures pass core identification. Proceed to Step 1.
**Cost:** ~$2 (two runs: first crashed on ScholarMatchResult bug, second succeeded)
**Results:** `tests/results/source_engine/session6/`

---

## Summary

| Dimension | Result |
|-----------|--------|
| Crashes | 0/13 |
| Trust tier | 13/13 correct |
| Multi-layer detection | 13/13 correct |
| Author identification (correct person) | 13/13 correct |
| Genre | 12/13 (05_tafsir: LLM said "other", GT says "risalah") |
| Science scope | 5/13 exact match (systematic over-tagging) |
| Authority level | 12/13 |
| Structural format | 11/13 |
| Level | 7/13 (5 null when GT expects a value) |

---

## Bugs Found and Fixed During Step 0

### Fixed: ScholarMatchResult→dict type mismatch (commit e607701)

`metadata_inference.py` passed `scholar_authority.lookup` directly to `make_author_agreement_fn`, but lookup returns a `ScholarMatchResult` dataclass while the agreement function expected `Callable[[str], Optional[dict]]`. Crashed all 13 fixtures. Fixed with adapter function.

### Fixed: INTERNAL_ERROR masking (commit 77b9b42)

The catch-all exception handler used `ErrorCode.FREEZE_FAILED` for all unexpected errors, masking the real error type. Changed to `INTERNAL_ERROR`.

### Fixed: Consensus gate used placeholder model IDs (commit 77b9b42)

Human gate for consensus disagreement used hardcoded "model_a"/"model_b" instead of actual model IDs from inference responses.

### Fixed: Validation auto-correction not propagated (commit 77b9b42)

Checks 5e/6b auto-corrected `is_multi_layer` in a dict copy but never wrote the change back to the SourceMetadata object.

---

## Bugs Found — For Step 1 Code Audit

### A1: Validation gate-severity errors silently ignored

`validation.py` returns 3 error types with `severity="gate"` (confidence < 0.50, author-science mismatch, multi_layer=true with empty layers). Engine.py only processes `severity="fatal"` — gate errors are logged but never converted to human gate checkpoints. SPEC §5 line 1451 requires: "confidence < 0.50 → abort write → create human gate checkpoint."

**Not triggered in Step 0** (all confidences > 0.50, empty registries). **Will matter at scale.**

### A2: Registration rollback silently passes on double corruption

`_rollback_registries` (registries/__init__.py line 285) catches `OSError` with `pass` when both .bak and main registry files are corrupt. Violates fail-loud constraint.

### A3: Scholar registry lacks file locking for author registration

`lookup_or_register_author` (Step 6) reads/writes scholars.json without file locking. Two concurrent intakes could create duplicate records for the same author. Staging lock prevents same-source concurrency but not different-source concurrency.

### A4: Name matching doesn't strip punctuation

`normalize_arabic_name` strips diacritics and definite articles but not Arabic commas (،) or other punctuation. LLM-generated full nasab names often include commas (e.g., "الزجاجي، أبو القاسم") which causes "زجاجي،" ≠ "زجاجي" token mismatch. Reduces name matching accuracy for cross-source scholar deduplication.

---

## LLM Quality Issues — For Step 3 Prompt Tuning

### Science scope over-tagging (8/13 fixtures)

LLM tags correct primary science plus tangentially related extras. Prompt lacks guidance on minimality. Worst case: fixture 12 (memoirs, non-scholarly) gets [tarikh, fikr_islami] instead of [].

### Genre edge cases (2/13 fixtures)

- 05_tafsir: تعقبات على الجلالين classified as "other" (run 2) or "tafsir" (run 1), neither matches GT "risalah"
- alfiyyah_versified: classified as "nazm" (run 2) or "matn" (run 1). Both defensible — the Alfiyyah is a versified matn.

### Level frequently null or wrong

LLM returns null level for 5 fixtures where GT expects a value. When it does return values, 2 are wrong (02: specialist vs advanced, 07: beginner vs intermediate).

### Authority level edge case (03_fiqh)

Contemporary university paper classified as "primary" instead of "modern_compilation".

---

## CG-1 Resolution: Confidence Calibration

Confidence scores exist and are usable. Range: 0.60–1.0 across all fields. No scores below 0.50. One field (08_death_date level: 0.60) would trigger needs_review.

**Calibration concern:** Science scope confidence is high (0.70–1.0) even when over-tagging. The LLM is confidently wrong. Step 3 should recalibrate after prompt tuning.

## CG-5 Resolution: Author Complementarity

Consensus pair (Opus 4.6 + Command A) correctly identified all 13 authors. Per-model breakdowns not captured in result files — would need script modification for full complementarity analysis. Deferred to Step 3.

---

## Owner Decisions

- **Full nasab names:** Owner confirmed he wants extensive, detailed full nasab forms (not shortened names). The engine's behavior is correct.
- **Alfiyyah genre:** "nazm" vs "matn" — both defensible. GT says "matn" (pedagogical role). May need prompt clarification.
