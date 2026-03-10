# Phase C Calibration Bugs — Engine Issues for Step 4

**Discovered:** 2026-03-10 (Calibration session)
**Scope:** Bugs in the source engine code found by examining Phase C output data.
**Action:** File for Step 4 fix cycle. None of these block Phase 2 evaluation.

---

## BUG-C04: Author Confidence Lost During Metadata Assembly

**Severity:** HIGH — corrupts downstream trust decisions
**Component:** `engines/source/src/engine.py` + `engines/source/src/metadata_inference.py`

**Root cause:** Two unrelated "author confidence" values exist in the pipeline, and the wrong one ends up in result.json.

1. **LLM confidence** (`author_identification_confidence`): The model's self-assessed confidence in its author identification. Computed in `metadata_inference.py`, capped by `apply_confidence_caps()` (max 0.85 for biographical inference), and stored in the `confidence_scores` dict as key `"author"`.

2. **Registry confidence** (`ScholarReference.confidence`): The scholar registry's match score. Set to 1.0 for every new registration in `scholar_registry.py:104` (because a new record trivially matches itself).

**Data flow:**
```
LLM reports 0.55 → apply_confidence_caps() returns {"author": 0.55, "genre": 0.90, ...}
                  → stored in MetadataInferenceResult.confidence_scores

Engine builds InferredFieldConfidence from confidence_scores
  → BUT InferredFieldConfidence has NO "author" field (contracts.py:356-370)
  → The "author" key is silently dropped

Engine builds ScholarReference via lookup_or_register_author()
  → New registration → confidence=1.0
  → This 1.0 goes into result["author"]["confidence"]
```

**Result:** Every success book has `result["author"]["confidence"] = 1.0` regardless of the LLM's actual identification confidence. The LLM's confidence survives only in `llm_responses/*.json`.

**Observed range of lost values:** 0.55 (الورقة النحوية) to 0.99 (famous books).

**Fix options:**
- A: Add "author" field to `InferredFieldConfidence` and populate from `apply_confidence_caps()`
- B: Add `inference_confidence` field to `ScholarReference` alongside the registry `confidence`
- C: Both (separate concerns: registry match confidence vs LLM identification confidence)

**Recommendation:** Option C. These are genuinely different concepts. The registry confidence answers "does this match an existing record?" The LLM confidence answers "is this identification correct?" Both are useful downstream.

---

## BUG-C05: Ground Truth Comparison Title Matching Fragile

**Severity:** MODERATE — reduces fixture regression coverage
**Component:** `scripts/run_phase_c.py` (ground truth comparison logic)

**Symptom:** 14 entries in GROUND_TRUTH.json, 11 fixture books present in Phase C, but only 5 got `ground_truth_comparison.json`. The other 6 present fixtures silently failed matching.

**Root cause:** Title matching between GROUND_TRUTH.json entry titles and Phase C directory names is too strict. Examples of failed matches:
- GT: "جزء فيه من أحاديث الإمام أيوب السختياني" vs Dir: "أحاديث أيوب السختيانى" (ى vs ي, prefix difference)
- GT: "آداب الصحبة" vs Dir: "آداب الصحبة لأبي عبد الرحمن السلمي" (suffix added)
- GT: "أبنية الأسماء والأفعال والمصادر" vs Dir: same (matched by name but no GT file produced — investigate further)

**Additionally:** `PHASE_C_SUMMARY.json` reports `"ground_truth_results": {"total_compared": 0}` despite 5 comparison files existing. The summary counter and the comparison writer use different code paths.

**Fix:** Use fuzzy title matching (normalized_name_similarity applied to titles, threshold ~0.80) for ground truth lookup. Fix summary counter to match.

---

## BUG-C06: Sanity Check False Positives on Gate-Abort Books

**Severity:** LOW — cosmetic, misleads humans reading summaries
**Component:** `scripts/run_phase_c.py:384-390`

**Symptom:** 51 "author_name_blank" errors at severity="error" in the sanity check summary. All 51 are gate_abort books.

**Root cause:** The sanity check reads `result_data.get("author", {})` and checks `name_arabic`. For gate_abort books, result.json has no `author` object → the check always fires.

**Fix:** Skip author_name_blank check when `result["status"] == "gate_abort"`.

**Corrected sanity stats:** 0 errors, 0 warnings, 32 info (muhaqiq_not_in_context). 22 clean books.

---

## BUG-C07: PHASE_C_LESSONS.md Contains False Infrastructure Claims

**Severity:** MODERATE — misleads future evaluation sessions
**Component:** `tests/results/source_engine/phase_c/PHASE_C_LESSONS.md`

**Symptom:** Claims "Command A completely unavailable", "All books fell back to single-model mode", "No consensus comparison occurred." All three claims are false.

**Reality:** 73/73 books have dual-model consensus. 67 used Command A (with latencies 12-47s), 6 used GPT-5.4.

**Root cause:** Unknown. Possibly Claude Code wrote LESSONS.md based on early test observations before the full run completed, or based on incorrect monitoring output.

**Fix:** Update LESSONS.md to reflect actual data. Replace BUG-C03 entry. Update "What Went Wrong" and "Recommendations" sections.

---

## Summary

| Bug ID | Severity | Blocks Evaluation? | Component |
|--------|----------|-------------------|-----------|
| BUG-C04 | HIGH | No (workaround: read llm_responses/) | engine.py + metadata_inference.py |
| BUG-C05 | MODERATE | No (manual evaluation covers fixtures) | run_phase_c.py |
| BUG-C06 | LOW | No (cosmetic) | run_phase_c.py |
| BUG-C07 | MODERATE | No (errata document corrects) | PHASE_C_LESSONS.md |

None of these block Phase 2 evaluation. All should be fixed in Step 4 before any re-run.
