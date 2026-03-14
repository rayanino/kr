# Step 4 Bug Fix Specs — Claude Code Tasks

**Created by:** Claude Chat (Architect), Calibration Session
**Purpose:** Precise implementation specs for 4 bugs discovered during Phase C evaluation.
**Each fix is independent — can be done in any order.**

---

## FIX-C04: Author Confidence Lost During Metadata Assembly

**Priority:** HIGH — corrupts downstream trust decisions and validation gates
**Files to modify:** `engines/source/contracts.py`, `engines/source/src/engine.py`, `engines/source/src/validation.py`
**Tests to add/update:** `engines/source/tests/test_metadata_inference.py`, `engines/source/tests/test_engine.py`

### Problem

The LLM's author identification confidence is computed and capped in `metadata_inference.py:apply_confidence_caps()`, stored in the confidence dict as `{"author": <float>}`, but then silently dropped during assembly because `InferredFieldConfidence` (contracts.py:356-370) has no `author` field.

Meanwhile, `ScholarReference.confidence` (set by `scholar_registry.py:104`) is always 1.0 for new registrations (Phase C starts empty). So `result["author"]["confidence"]` is always 1.0 regardless of actual LLM confidence.

Additionally, `validation.py:87-90` checks `author.confidence` from the ScholarReference (always 1.0) against the 0.50 threshold — this check is dead code in practice.

### Data flow (current, broken)

```
LLM reports author_identification_confidence: 0.55

metadata_inference.py:277  → apply_confidence_caps() returns {"author": 0.55, "genre": 0.90, ...}
metadata_inference.py:554  → result.confidence_scores = confidence  (dict with "author" key)

engine.py:145 → _build_confidence_scores(inference) reads inference.confidence_scores
engine.py:148 → InferredFieldConfidence(genre=0.90, science_scope=..., ...)
               NO "author" field in InferredFieldConfidence → 0.55 silently dropped

engine.py:345 → lookup_or_register_author() → new record → ScholarReference(confidence=1.0)
engine.py:449 → metadata.author = author_ref  → result.json gets author.confidence = 1.0

validation.py:87 → reads author.confidence (1.0) → NEVER triggers 0.50 threshold
```

### Fix

**Step 1: Add `author` field to `InferredFieldConfidence`** (contracts.py:356-370)
```python
class InferredFieldConfidence(BaseModel):
    """..."""
    genre: float = Field(ge=0.0, le=1.0)
    science_scope: float = Field(ge=0.0, le=1.0)
    level: Optional[float] = Field(None, ge=0.0, le=1.0)
    structural_format: float = Field(ge=0.0, le=1.0)
    authority_level: float = Field(ge=0.0, le=1.0)
    multi_layer: Optional[float] = Field(None, ge=0.0, le=1.0)
    genre_chain: Optional[float] = Field(None, ge=0.0, le=1.0)
    author: float = Field(ge=0.0, le=1.0, description="LLM author identification confidence, post-caps")  # NEW
```

**Step 2: Populate `author` in `_build_confidence_scores()`** (engine.py:145-156)
```python
def _build_confidence_scores(inference: MetadataInferenceResult) -> InferredFieldConfidence:
    scores = inference.confidence_scores or {}
    return InferredFieldConfidence(
        genre=scores.get("genre", 0.5),
        science_scope=scores.get("science_scope", 0.5),
        level=scores.get("level"),
        structural_format=scores.get("structural_format", 0.5),
        authority_level=scores.get("authority_level", 0.5),
        multi_layer=scores.get("multi_layer"),
        genre_chain=scores.get("genre_chain"),
        author=scores.get("author", 0.5),  # NEW — from apply_confidence_caps()
    )
```

**Step 3: Fix validation to use InferredFieldConfidence.author** (validation.py:83-95)
```python
def _check_confidence_thresholds(data: dict[str, Any]) -> list[ValidationError]:
    errors: list[ValidationError] = []
    confidence = data.get("confidence_scores", {})

    # Author confidence now comes from InferredFieldConfidence, not ScholarReference
    checks = [
        ("confidence_scores.author", confidence.get("author")),  # CHANGED
        ("confidence_scores.genre", confidence.get("genre")),
        ("confidence_scores.science_scope", confidence.get("science_scope")),
    ]
    # ... rest unchanged
```

**Step 4: Add `author` to `_build_needs_review()`** (engine.py:225-239)
```python
def _build_needs_review(
    confidence_scores: InferredFieldConfidence,
    ...
) -> list[str]:
    ...
    for field_name in ["genre", "science_scope", "structural_format", "authority_level", "author"]:  # ADD "author"
        score = getattr(confidence_scores, field_name, None)
        ...
```

**Step 5: DO NOT CHANGE ScholarReference.confidence** — it correctly represents registry match confidence. Both values are useful: `author.confidence` (registry) and `confidence_scores.author` (LLM). Downstream consumers can choose which to use.

### Verification

After fix, run the 13 test fixtures. Check that:
- `result["confidence_scores"]["author"]` is NOT always 1.0
- `result["confidence_scores"]["author"]` matches the LLM's `author_identification_confidence` (after caps)
- `result["author"]["confidence"]` still reflects registry confidence (may still be 1.0 for new records — that's correct)
- For a book with disputed attribution, `confidence_scores.author` should be ≤ 0.70
- For any book, `confidence_scores.author` should be ≤ 0.85 (biographical inference cap)

---

## FIX-C05: Ground Truth Comparison Skipped for Gate-Abort Fixtures

**Priority:** MODERATE — reduces fixture regression coverage from 12 to 5
**Files to modify:** `scripts/run_phase_c.py`
**Tests:** Run on the 12 fixture books — all should produce GT comparison files

### Problem

GT comparison (lines 531-539) is inside the try block that only executes for success books. Gate-abort books land in the except block (line 550), which saves LLM responses but never runs GT comparison. Result: 7 of 12 fixture books get no GT comparison.

Additionally, the summary counter `gt_total` (line 765) counts `ground_truth_available` from `book_result`, but gate_abort books never set this key to True.

### Fix

**In the except block for `SourceEngineError` (after line 590, saving sanity checks), add GT comparison using LLM data:**

```python
            # Ground truth comparison for gate_abort fixtures (NEW)
            # Gate-abort books have full LLM data — compare from llm_responses
            fixture_key = fixture_mappings.get(book_name)
            if fixture_key and fixture_key in ground_truth and _captured_inference:
                # Build a pseudo-result from LLM canonical output for comparison
                canon = _captured_inference.canonical_output if hasattr(_captured_inference, 'canonical_output') else None
                if canon is None and _captured_inference:
                    # Fallback: build from raw model responses
                    canon = select_canonical_result(_captured_inference.raw_model_responses) if hasattr(_captured_inference, 'raw_model_responses') else None
                
                if canon:
                    pseudo_result = {
                        "genre": canon.genre if hasattr(canon, 'genre') else "",
                        "author": {"name_arabic": canon.author_identification.canonical_name_ar if hasattr(canon, 'author_identification') else ""},
                        "is_multi_layer": canon.is_multi_layer if hasattr(canon, 'is_multi_layer') else None,
                        "science_scope": canon.science_scope if hasattr(canon, 'science_scope') else [],
                        "structural_format": canon.structural_format if hasattr(canon, 'structural_format') else "",
                        "authority_level": canon.authority_level if hasattr(canon, 'authority_level') else "",
                        "level": canon.level if hasattr(canon, 'level') else None,
                        "attribution_status": canon.attribution_status if hasattr(canon, 'attribution_status') else "",
                        # Trust and trust_score are NOT available for gate_abort
                    }
                    comparison = compare_ground_truth(pseudo_result, ground_truth[fixture_key])
                    comparison["book"] = book_name
                    comparison["ground_truth_key"] = fixture_key
                    comparison["from_gate_abort"] = True  # Flag for downstream consumers
                    save_json(book_output / "ground_truth_comparison.json", comparison)
                    book_result["ground_truth_available"] = True
                    book_result["ground_truth_match"] = comparison["all_match"]
```

**Note:** This pseudo-result won't have trust_tier or trust_score. The GT comparison for those fields will show "actual": "" which is a known limitation. The comparison function handles missing values gracefully (empty string != expected → mismatch). Consider adding a `"source": "llm_canonical"` marker to the comparison so downstream consumers know this was from inference, not full pipeline output.

### Verification

After fix, re-run on fixtures. All 12 should produce GT comparison files. Gate-abort ones should have `"from_gate_abort": true`.

---

## FIX-C06: Sanity Check False Positives on Gate-Abort Books

**Priority:** LOW — cosmetic but misleading
**Files to modify:** `scripts/run_phase_c.py` (function `run_sanity_checks`, approx line 375)
**Tests:** Verify 0 false-positive author_name_blank errors on gate_abort books

### Problem

`run_sanity_checks` at line 382-390 checks `result_data.get("author", {}).get("name_arabic", "")`. For gate_abort books, `result_data` is the gate_abort dict which has no "author" key. Empty dict → empty name_arabic → always triggers "author_name_blank" at severity "error". All 51 gate_abort books are false positives.

### Fix

Add a guard at the top of `run_sanity_checks`:

```python
def run_sanity_checks(result_data: dict, extraction: dict, prompt_sent: dict) -> dict:
    flags = []
    status = result_data.get("status", "")
    
    # ... existing check 1 (multi_layer_no_layers) ...
    
    # 2. Author name blank — ONLY for success books (gate_abort has no author in result_data)
    if status != "gate_abort":  # NEW GUARD
        author = result_data.get("author", {})
        if isinstance(author, dict) and not author.get("name_arabic", "").strip():
            flags.append({
                "check": "author_name_blank",
                "severity": "error",
                "detail": "author.name_arabic is empty",
            })
```

### Verification

After fix, re-run. Expect:
- 0 "author_name_blank" errors (was 51)
- 32 "muhaqiq_not_in_context" info flags (unchanged)
- 22 clean books (was 22 — unchanged, because only success books were ever clean)

---

## FIX-C07: PHASE_C_LESSONS.md Factual Errors

**Priority:** MODERATE — misleads future evaluation sessions
**File to modify:** `tests/results/source_engine/phase_c/PHASE_C_LESSONS.md`

### Problem

Three claims are false:
1. "Command A (Cohere) completely unavailable" → 67/73 used Command A successfully
2. "All books fell back to single-model mode" → 0/73 single-model fallback
3. "No consensus comparison occurred for any book" → 73/73 have dual-model consensus

Additionally, 6 books used GPT-5.4 instead of Command A. This isn't mentioned.

### Fix

Replace the BUG-C03 entry and related text:

```markdown
## Bugs Found

- **[BUG-C01]** ... (unchanged)
- **[BUG-C02]** ... (unchanged)
- **[BUG-C03] RETRACTED**: Originally claimed Command A timed out on all attempts.
  This was incorrect. Actual data: 67/73 books used Command A successfully (latencies 12-47s).
  6 books used GPT-5.4 as second model. 0/73 were single-model fallback.
  73/73 have genuine dual-model consensus (67 agreed, 6 disagreed).
```

Update "What Went Wrong" section:
- Remove "No multi-model consensus" claim
- Replace with accurate description of the 6 disagreements

Update "Recommendations for Next Phase":
- Remove recommendation to "Re-run with Command A available" (it was available)
- Keep recommendation about scholar registry population (still valid)

### Verification

Read the corrected file. Cross-reference every claim against the actual consensus.json files.

---

## FIX-C08: Edition Grouping False Positive (Father/Son Works)

**Priority:** LOW — grouping is informational only
**Files to modify:** `scripts/run_phase_c.py` (function `compute_edition_groups`)
**Tests:** Verify حاشية ابن عابدين and تكملة are NOT grouped together

### Problem

`compute_edition_groups()` matches on partial title overlap ("حاشية ابن عابدين") without verifying author consistency. This groups a father's work with his son's continuation as "editions of the same work."

### Fix

After grouping by title, add an author consistency check:

```python
# After building candidate groups by title overlap...
# Split groups where authors differ significantly
from shared.scholar_authority.src.name_matching import normalized_name_similarity

for group in candidate_groups:
    authors = [get_author_name(book) for book in group["editions"]]
    if len(set(authors)) > 1:
        # Check pairwise similarity
        all_similar = True
        for i in range(len(authors)):
            for j in range(i+1, len(authors)):
                sim = normalized_name_similarity(authors[i], authors[j])
                if sim < 0.80:  # Lower than consensus threshold — generous
                    all_similar = False
                    break
        if not all_similar:
            # Split: these are different works, not editions
            group["split_reason"] = "different_authors"
            # ... remove from edition groups or flag
```

### Verification

After fix, the حاشية/تكملة pair should NOT appear as an edition group. All other groups should be unchanged.

---

## Implementation Order Recommendation

1. **FIX-C06** first (5 minutes, simplest, clears up false error noise)
2. **FIX-C07** second (10 minutes, text edit, prevents future confusion)
3. **FIX-C04** third (30 minutes, code + tests, highest impact)
4. **FIX-C05** fourth (20 minutes, depends on understanding from FIX-C04)
5. **FIX-C08** last (10 minutes, lowest priority)

Total estimated time: ~1.5 hours of Claude Code work.

After all fixes, re-run the 13 test fixtures to verify no regressions.
Do NOT re-run Phase C on the full collection — the evaluation is in progress on existing data.
