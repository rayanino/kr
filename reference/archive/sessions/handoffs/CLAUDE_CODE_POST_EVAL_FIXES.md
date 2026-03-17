# Claude Code — Post-Evaluation Fixes

## Context

Source engine validation is COMPLETE. GO verdict with 4 mandatory fixes. This prompt implements all 4 fixes in a single session. Read `PHASE_D_CRITICAL_REVIEW.md` and `PHASE_D_AGGREGATION_REPORT.md` for full context.

Budget: ~€70 remaining. This session should cost ~€0 (no API calls — all fixes are code/documentation changes).

**IMPORTANT: All references below use content-based search strings, not line numbers. Line numbers can shift. Always search for the quoted content to find the exact location.**

## Fix 1: Missing Genre Values (was "genre confidence resolution")

### Root Cause (confirmed by code investigation)

The Genre enum in `contracts.py` has 18 values. LLMs correctly produce `rihlah` and `usul_al_fiqh` for books in those genres, but these values are NOT in the enum. `validate_enum_value()` in `metadata_inference.py` silently falls back to `"other"`.

This is NOT a consensus resolution bug. The consensus module works correctly (selects whole response by author confidence). The bug is that valid LLM output is discarded by enum validation.

**Evidence from 204-book run:**
- ملء العيبة: Opus=rihlah(0.92), CA=sirah(0.90), Pipeline=other ← rihlah not in enum, so Opus's correct answer became "other"
- إعلام الموقعين (2 editions): CA=usul_al_fiqh(0.95) ← even if CA had been canonical, usul_al_fiqh not in enum, would still become "other"

### Files to Modify

1. **`engines/source/contracts.py`** — Add to Genre enum:
   - `RIHLAH = "rihlah"` (travel literature)
   - `USUL_AL_FIQH = "usul_al_fiqh"` (Islamic legal theory/methodology)

2. **`engines/source/SPEC_CORE.md`** — Search for the genre list that starts "`genre` must be one of the `Genre` enum values in contracts.py (18 values:". Update the count from 18 to 20 and add `rihlah` and `usul_al_fiqh` to the parenthetical list. Also add a note below it: "The LLM prompt and `library/config/genre_synonyms.json` must include all Genre enum values and their Arabic synonyms."

3. **`engines/source/prompts/inference_v1.py`** — Add `rihlah` and `usul_al_fiqh` to the genre enum list in the prompt's schema section. Keep them in the same alphabetical style.

4. **`library/config/genre_synonyms.json`** — Add synonyms:
   - `"رحلة": "rihlah"`
   - `"أصول الفقه": "usul_al_fiqh"`
   - `"أصول فقه": "usul_al_fiqh"`

5. **Tests** — Add to `engines/source/tests/test_metadata_inference.py` in class `TestValidateEnumValue` (NOT test_validation.py — the genre enum tests live here alongside the existing genre synonym tests):
   - Test that genre="rihlah" passes validation (no fallback) — same pattern as `test_valid_genre_passes_direct`
   - Test that genre="usul_al_fiqh" passes validation (no fallback)
   - Test that Arabic synonym "رحلة" maps to "rihlah" — same pattern as `test_arabic_synonym_منظومة_maps_to_nazm`
   - Test that Arabic synonym "أصول الفقه" maps to "usul_al_fiqh"

### What NOT to Change

Do NOT modify the consensus module (`shared/consensus/src/consensus.py`). It is working correctly. Do NOT modify `_select_canonical()` — whole-response selection by author confidence is the intended design.

## Fix 2: ERR-01 — hashiyah + ML=False Validation

### Root Cause

Check 5e in `validation.py` (search for `# 5e: Genre ↔ multi-layer`) catches `genre in ("sharh", "hashiyah") and not is_multi_layer` but only at severity="warning". For hashiyah specifically, ML=False with no layers is an internal contradiction (hashiyah requires 3 layers: matn→sharh→hashiyah). The النكت case shows this warning wasn't sufficient to surface the issue.

### Files to Modify

1. **`engines/source/src/validation.py`** — In `_check_consistency()`, check 5e (search for `# 5e:`):
   - Split the existing `else` branch (genre suggests multi-layer but no layers) into two paths:
     - When genre="hashiyah" AND is_multi_layer=False AND text_layers is empty: change severity from "warning" to "gate" and use check name `"consistency_hashiyah_no_layers"`. This is a genuine contradiction that needs human review.
     - When genre="sharh" AND is_multi_layer=False AND text_layers is empty: keep as "warning" (current behavior — sharh could be a classification boundary issue).
   - Add a comment explaining the asymmetry: hashiyah structurally requires 3 layers, so hashiyah+no_layers is always contradictory. Sharh could be a standalone work near the sharh/risalah boundary.

2. **`engines/source/src/engine.py`** — In the gate error handler (search for `# Process gate-severity errors`), add an `elif` branch for the new check name:
   ```python
   elif gate_error.check == "consistency_hashiyah_no_layers":
       gate_low_confidence(
           source_id,
           "genre",
           data_for_validation.get("genre", "hashiyah"),
           0.0,
       )
   ```
   Without this branch, the book would abort correctly but no human gate checkpoint would be created, leaving the owner unable to see why the book was gated.

3. **`engines/source/SPEC_CORE.md`** — Search for the consistency check documentation (near "hashiyah → should not be beginner") and add: "hashiyah + is_multi_layer=False with no layers triggers human gate (not just warning) because hashiyah structurally requires 3 layers."

4. **Tests** — Add to `engines/source/tests/test_validation.py` in class `TestAutoCorrectChain` (alongside the existing `test_sharh_empty_layers_no_auto_correct`):
   - Test: genre="hashiyah", is_multi_layer=False, text_layers=[] → severity="gate" with check name "consistency_hashiyah_no_layers"
   - Test: genre="sharh", is_multi_layer=False, text_layers=[] → severity="warning" (confirm existing behavior preserved — this test already exists as `test_sharh_empty_layers_no_auto_correct` but verify it still passes)

### Tafsir/ML Rule — No Change Needed

The auto-screening flagged tafsir+ML=False as suspicious, but validation.py check 5e only applies to sharh/hashiyah genres. Standalone tafsirs (one author commenting on Quran directly) should correctly have ML=False. No code change needed — the structural screening flag was a false alarm, not a validation bug.

## Fix 3: ERR-03 — Death Date Hallucination Warning

### Root Cause

Opus hallucinates death dates for modern scholars: القحطاني (+3 years), وافي (+6 years), مطلوب (+2 years). All cases: extraction has no death date, Opus infers one from domain knowledge, CA correctly abstains (None). The pipeline accepts Opus's value with no warning.

Additionally, CA fabricates precision from approximate century designations: "ت ق 4هـ" becomes specific year 400, "ت ق 6هـ" becomes 460 (wrong century).

### Files to Modify

1. **`engines/source/src/metadata_inference.py`** — Two changes:

   a) Add field to `MetadataInferenceResult` dataclass (search for `death_date_source: Optional[str]`):
   ```python
   death_date_source: Optional[str] = None  # extraction, author_raw_text, inference, absent
   death_date_single_model: bool = False     # True when only one model provided a death date
   ```

   b) After step 10b (search for `# 10b. Determine death_date_source`), add step 10c. Note: at this point in the function, `successful` is still in scope from line ~492 and `result` is the MetadataInferenceResult being built:
   ```python
   # 10c. Flag single-model death dates (ERR-03 pattern)
   # When one model provides a death_date and the other says None,
   # the date is higher-risk for hallucination.
   if len(successful) >= 2:
       death_a = successful[0].parsed.author_identification.death_date_hijri
       death_b = successful[1].parsed.author_identification.death_date_hijri
       if (death_a is None) != (death_b is None):
           result.death_date_single_model = True
   else:
       # Single model = treat death date as unverified if inferred
       result.death_date_single_model = True
   ```

   c) In step 13 (search for `# 13. Build needs_review_fields`), AFTER the existing genre/format/authority/level fallback blocks and BEFORE `result.needs_review_fields = sorted(needs_review)`, add:
   ```python
   # Flag single-model inferred death dates for owner review (ERR-03)
   if result.death_date_single_model and result.death_date_source == "inference":
       if "death_date_hijri" not in needs_review:
           needs_review.append("death_date_hijri")
   ```

2. **`engines/source/src/engine.py`** — **CRITICAL: Fix pre-existing needs_review_fields merge gap.** Search for `needs_review_fields = _build_needs_review(confidence_scores)` (line ~394). Immediately after, add:
   ```python
   # Merge inference-specific review flags (genre fallback, death date, etc.)
   # The inference builds its own needs_review list that includes flags
   # not based on confidence scores (e.g., enum fallback, single-model death dates).
   if inference.needs_review_fields:
       for f in inference.needs_review_fields:
           if f not in needs_review_fields:
               needs_review_fields.append(f)
       needs_review_fields = sorted(needs_review_fields)
   ```
   **Why this matters:** Without this merge, inference.needs_review_fields is silently discarded. The engine builds needs_review_fields only from confidence scores, losing any non-confidence-based flags. This pre-existing gap means the genre enum fallback flag (when LLM returns unknown genre → "other") was already being lost. This merge fixes that AND enables the death date flag to propagate. It's a 4-line fix that's safe (only adds fields, never removes) and forward-compatible.

3. **`engines/source/src/validation.py`** — Add a new check in `_check_consistency()`, before the `return errors` statement:
   ```python
   # 5g: Single-model death date warning
   death_date_single = data.get("death_date_single_model", False)
   death_date_source = data.get("death_date_source", "absent")
   if death_date_single and death_date_source == "inference":
       errors.append(ValidationError(
           check="single_model_death_date",
           severity="warning",
           field="author.death_date_hijri",
           message=(
               "Death date from single-model inference only (other model "
               "abstained). High risk for hallucination — needs manual verification."
           ),
           error_code="SRC_DEATH_DATE_UNVERIFIED",
           recovery="flag_needs_review",
       ))
   ```
   Note: This validation check is now REDUNDANT with the direct needs_review_fields addition in metadata_inference.py. It serves as documentation and logging only (the validation warning gets logged at line ~616 in engine.py). The actual flagging to the owner happens via needs_review_fields.

4. **`engines/source/src/engine.py`** — Search for `data_for_validation = metadata.model_dump(mode="json")`. Immediately after that line, before `validation_errors = validate_source_metadata(...)`, inject:
   ```python
   # Inject inference-only fields for validation (not in SourceMetadata schema)
   data_for_validation["death_date_source"] = getattr(inference, "death_date_source", "absent")
   data_for_validation["death_date_single_model"] = getattr(inference, "death_date_single_model", False)
   ```
   This is needed for the validation warning (check 5g) to fire. The extra keys are ignored by SourceMetadata serialization.

5. **`engines/source/SPEC_CORE.md`** — Search for "Single-LLM biographical inference cap" and add a new subsection immediately after:

   **Death date hallucination pattern (ERR-03).** Three confirmed cases in 204-book validation: Opus inferred death dates 2-6 years off for modern scholars when extraction provided no death data. Pattern: Opus supplies a specific date, CA correctly abstains (None). Additionally, CA may fabricate specific years from approximate century designations ("ت ق 4هـ" → 400 AH). Mitigation: when only one model provides a death_date and the other returns None, and the source is "inference" (not from extraction), add `SRC_DEATH_DATE_UNVERIFIED` warning to `needs_review_fields`. This flags the date for owner verification without dropping it.

6. **Tests** — Add to `engines/source/tests/test_validation.py`:
   - Test: death_date_single_model=True, death_date_source="inference" → warning with code SRC_DEATH_DATE_UNVERIFIED
   - Test: death_date_single_model=True, death_date_source="author_raw_text" → no warning (extraction confirms the date)
   - Test: death_date_single_model=False, death_date_source="inference" → no warning (both models agree)

   Add to `engines/source/tests/test_engine.py` or `engines/source/tests/test_metadata_inference.py`:
   - Test: Verify that inference.needs_review_fields propagates to the final SourceMetadata.needs_review_fields. Create an inference result with needs_review_fields=["death_date_hijri"], verify it appears in the engine's output. This tests the merge fix.

## Fix 4: ERR-02 — السراج المنير Documentation

### Root Cause

The extraction lists `author_raw = "الحافظ جلال الدين السيوطي - العلامة محمد ناصر الدين الألباني"` (classical source authors on the cover) and `muhaqiq = "عصام موسى هادي"` (the actual compiler/arranger). Neither LLM recognizes that the muhaqiq is the functional author of this derived work.

This is a data/design limitation, not a code bug. The pipeline has no "compiler" role concept — Shamela puts compilers in the muhaqiq field. A full fix would require a new LLM inference step to distinguish muhaqiq (editor of existing text) from compiler (creator of a new derived work). That's out of scope for a post-evaluation fix.

### Files to Modify

1. **`engines/source/SPEC_CORE.md`** — Add to the known limitations section:

   **Compiler-as-muhaqiq pattern (ERR-02).** Shamela may list source authors in `author_name_raw` while placing the actual compiler/arranger in `muhaqiq_name_raw`. The pipeline treats muhaqiq as an editor, not as a potential author, so it attributes the work to the source authors. Example: السراج المنير lists السيوطي and الألباني as authors, but the actual compiler is عصام موسى هادي (listed as muhaqiq). The consensus disagreement mechanism caught this case (both models picked different source authors). Extension: future compiler detection could flag books where muhaqiq is contemporary but listed authors are classical, suggesting a compilation rather than a tahqiq.

2. **`engines/source/SPEC_CORE.md`** — In the prompt engineering section, add a note that the inference prompt should be updated in a future iteration to explicitly ask: "If the author_raw lists classical scholars but the muhaqiq appears to be the actual compiler/arranger of a new derived work, identify the compiler as the functional author."

3. **`OPEN_PROBLEMS.md`** — Add the compiler detection pattern as an open problem for future work.

No code changes for this fix. It's documentation + future work scoping.

## Execution Order

1. Fix 1 first (Genre enum) — smallest change, broadest impact
2. Fix 2 (hashiyah validation) — small, self-contained
3. Fix 3 (death date warning) — touches 4 files, includes the riskiest change (needs_review merge)
4. Fix 4 (documentation) — no code, just SPEC and OPEN_PROBLEMS

After all 4: run the full test suite (`pytest engines/source/tests/ -v`). All existing tests must pass (370 test functions, some parametrized — total test count varies). New tests must pass.

## Additional Items (from strategic review)

These are small additions that make the 4 fixes more robust. Not separate fixes — they're part of the quality of implementation.

**A. Add logging to `validate_enum_value` when falling back to default.**
In `engines/source/src/metadata_inference.py`, the module already has `logger = logging.getLogger(__name__)` at the top. In the `validate_enum_value` function, just before the final `return default, True` line, add:
```python
logger.warning("Enum fallback: value '%s' not in %s and no synonym match — using default '%s'", value, enum_class.__name__, default)
```
The SPEC (search for "log a WARNING with the invalid value") explicitly requires this. It's currently missing. Without it, new missing genres in the full collection are silently swallowed.

**B. Verify normalization engine has no hardcoded genre lists.**
After adding `rihlah` and `usul_al_fiqh` to the Genre enum, run: `grep -rn "genre.*==" engines/normalization/src/ --include="*.py"` to confirm no normalization code has hardcoded genre checks that would need updating. The normalization SPEC mentions genre-specific strategies (nazm → verse-aware), but these should be driven by the Genre enum or by content analysis, not by hardcoded strings. If any hardcoded checks exist, add the new genres.

**C. Risk flag: the needs_review_fields merge (Fix 3 step 2) is the riskiest change.**
It changes a data flow pattern: inference-level flags now propagate to SourceMetadata.needs_review_fields. Existing tests mock inference with `needs_review_fields=[]`, so they should pass. But after implementation, manually verify by running the full test suite and checking if any test that asserts specific needs_review_fields content fails unexpectedly. If a test fails, the issue is the test (which was implicitly depending on the merge NOT happening), not the fix.

## After Fixes

Commit all changes. Update NEXT.md to reflect:
- 4 mandatory fixes COMPLETE
- Next: final batch through source engine → normalization engine SPEC

Do NOT re-run any pipeline books. These fixes affect future runs only. Existing Phase D results are preserved per RESULT_PRESERVATION.md.

## Resolved Domain Questions (for the record)

**التعليق على الرحيق المختوم:** Downgrade from FLAG to PLAUSIBLE. Goodreads reviews and Shamela structure confirm the text copies passages from الرحيق المختوم with interleaved corrections and annotations. Both LLMs independently said ML=True after analyzing the actual text. Genre=sharh is imprecise (ta'liq would be more accurate) but is the closest available classification. No pipeline correction needed.

**وقفة هادئة مع الطاعنين في جماعات الدعوة:** ESCALATE stands. أبو عبد الله المصري is a deliberate pseudonym (كنية) — common for authors writing on controversial intra-Salafi topics. Shamela shows exactly 2 books under this pen name. No web source reveals the real identity. Pipeline correctly assigned 0.30 confidence. No action needed.
