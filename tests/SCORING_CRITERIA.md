# Scoring Criteria — LLM Inference Evaluation

Defines what counts as "correct" for each LLM-inferred field when compared against GROUND_TRUTH.json.

## Field Scoring

### `genre` — Strict enum match
- **Correct (1.0):** Exact match to ground truth enum value.
- **Partial (0.5):** Value is in a defined "close synonym" set:
  - `sharh` ↔ `hashiyah` (both are commentary forms)
  - `matn` ↔ `nazm` (only when the matn is versified)
  - `risalah` ↔ `other` (boundary is genuinely ambiguous for modern works)
  - `hadith_collection` ↔ `fiqh_comparative` (for أحاديث الأحكام-type works)
- **Wrong (0.0):** Any other mismatch.
- **Rationale:** Genre drives normalization strategy (verse-aware, commentary parsing). Close synonyms cause suboptimal but recoverable downstream behavior; wrong genres cause failures.

### `science_scope` — Set overlap scoring
- **Correct (1.0):** LLM output is an exact set match (order-independent).
- **Superset (0.75):** LLM output contains all ground truth values plus extras. Superset is better than subset because extra tags are noise, not missing information.
- **Subset (0.5):** LLM output contains some but not all ground truth values. Missing a scope means the taxonomy engine won't route excerpts to that science.
- **Overlap (0.25):** At least one value in common but neither subset nor superset.
- **Disjoint (0.0):** No values in common, OR ground truth is non-empty and LLM returns empty.
- **Both empty (1.0):** If ground truth is [] and LLM returns [], that's correct.
- **Rationale:** science_scope feeds the taxonomy engine. Missing a scope is worse than adding an extra one.

### `is_multi_layer` — Boolean exact match
- **Correct (1.0):** Exact boolean match.
- **Wrong (0.0):** Mismatch.
- **Rationale:** Multi-layer detection drives normalization layer splitting. A false positive creates phantom layers; a false negative merges distinct scholarly voices. Both are serious.

### `structural_format` — Strict enum match with synonym tolerance
- **Correct (1.0):** Exact match.
- **Partial (0.5):** 
  - `prose` ↔ `mixed` (many works are primarily prose with minor mixed elements)
  - `commentary` ↔ `prose` (some shuruh are running prose, per SPEC)
- **Wrong (0.0):** Any other mismatch.

### `level` — Exact enum match with adjacency tolerance
- **Correct (1.0):** Exact match.
- **Adjacent (0.5):** One step away on the scale (beginner↔intermediate, intermediate↔advanced, advanced↔specialist).
- **Wrong (0.0):** Two or more steps away, or null vs non-null mismatch.
- **N/A handling:** If ground truth is null, any LLM output is scored as: null→1.0, any value→0.0.

### `authority_level` — Strict enum match
- **Correct (1.0):** Exact match.
- **Wrong (0.0):** Any mismatch.
- **Rationale:** authority_level feeds trust evaluation. primary/reference/modern_compilation are distinct enough that confusion indicates real misunderstanding.

### `author_identification` — Composite scoring
Author identification is scored on three sub-components, averaged:

1. **Name match (weight 0.50):** normalized_name_similarity between LLM output author name and ground truth author name. Score = raw similarity value (0.0-1.0).
2. **Death date (weight 0.30):** 
   - Both null → 1.0
   - One null, one present → 0.3 (some credit for not fabricating)  
   - Both present, exact match → 1.0
   - Both present, within ±10 years → 0.7
   - Both present, within ±50 years → 0.3
   - Both present, >50 years apart → 0.0
3. **Correct identification (weight 0.20):** Binary — did the LLM identify the right person? This is a holistic judgment: if the name and date together unambiguously point to the same historical person as the ground truth, score 1.0. Otherwise 0.0.

### `genre_chain` — Structural check (Phase 2 only)
- **Correct (1.0):** LLM detects a genre chain relationship when ground truth expects one (fixture 05, 11), with correct relation_type and recognizable base work.
- **Partial (0.5):** Detects relationship but wrong type or wrong base work.
- **Wrong (0.0):** Fails to detect a relationship that should exist, or hallucinated one that shouldn't.
- **N/A:** Fixtures where ground truth has no genre chain — LLM returning null is correct.

## Aggregate Scoring

Per-fixture score = weighted average of all applicable fields:
- genre: 0.15
- science_scope: 0.15  
- is_multi_layer: 0.15
- structural_format: 0.10
- level: 0.05
- authority_level: 0.10
- author_identification: 0.30

Per-model score = average of per-fixture scores across all fixtures.

## Pass/Fail Thresholds

- **JSON parse rate:** ≥ 95% of responses must be valid JSON (A1)
- **Enum compliance:** ≥ 90% of enum fields must use valid enum values before synonym mapping (A1)
- **Multi-layer accuracy:** ≥ 85% boolean accuracy across all fixtures (A2)
- **Per-model aggregate:** ≥ 0.70 average score to be considered for production (A5)
- **Consensus pair "at least one right":** ≥ 90% across fixtures (A5)
