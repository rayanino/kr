# NEXT — Excerpting Engine Session 3: Phase 3 Deterministic Metadata Assembly

**STATUS: DRAFT — Requires adversarial review by architect before sending to CC.**

## Current Position

- **Excerpting Phase 1:** ACCEPTED (commit `28a188ad`). 77 tests.
- **Excerpting Phase 2:** ACCEPTED (commit `46bdb20d`). 147 tests.
- **HEAD:** `df25561f` on `master`
- **Test baseline:** 147 passed, 2 skipped (excerpting)
- **Open SPEC errata:** None
- **Phase 2 output:** `run_phase2a()` produces `dict[chunk_id → list[ClassifiedSegment]]`; `run_phase2b()` produces `dict[chunk_id → list[TeachingUnit]]`

## What to Do

Implement Phase 3 Stage 1: Deterministic Metadata Assembly (SPEC §7.1). This fills the stubs in `phase3_deterministic.py`. These are the 10 functions that compute ExcerptRecord fields from data alone — no LLM calls.

**Processing flow (§7.1):**
For each `AssembledChunk` + its `list[TeachingUnit]`:
1. For each TeachingUnit, compute 9 deterministic fields (F-DET-1 through F-DET-9)
2. Assemble a partial `ExcerptRecord` with these fields + passthrough fields from TeachingUnit
3. LLM-enriched fields (`excerpt_topic`, `school`, `takhrij_data`, etc.) are set to empty/null defaults — Session 4 fills them

## Context

Phase 3 deterministic is pure algorithmic code — no LLM, no external calls, fully testable. The hardest parts are:
- **F-DET-3 (layer attribution):** 4-rule cascade (LA-1–LA-4) with character overlap computation and layer_split_point merging
- **F-DET-5 (evidence detection):** Pattern matching for Quran (﴿...﴾), hadith (رواه, أخرجه, etc.), and ijma markers with word-boundary checking
- **F-DET-8 (footnote filtering):** Matching `⌜{ref_marker}⌝` patterns within a unit's character range

A shared `_word_to_char_range` helper is needed: F-DET-2, F-DET-3, F-DET-6, and F-DET-8 all need to convert (start_word, end_word) to character offsets. Phase 2's `_build_token_char_map` does exactly this. Import it from `phase2_classify.py` — do NOT duplicate.

## Owner Action Needed

None. This is a pure implementation session.

## Read First

| File | Lines | What |
|------|-------|------|
| `engines/excerpting/SPEC.md` | §7.1 (1397–1518) | **Governing spec for Phase 3 deterministic.** Read ALL of §7.1. |
| `engines/excerpting/SPEC.md` | §6.2 (1260–1340) | Layer Attribution rules LA-1 through LA-4 |
| `engines/excerpting/SPEC.md` | §2.2 (365–520) | ExcerptRecord output contract — the target shape |
| `engines/excerpting/contracts.py` | 87–200 | Sub-models: PageRange, AuthorAttribution, ScholarAttribution, EvidenceRef, TakhrijEntry, CrossReference, TermVariant |
| `engines/excerpting/contracts.py` | 440–530 | ExcerptRecord model fields |
| `engines/excerpting/contracts.py` | 1036–1100 | `validate_er_invariants()` — already implemented |
| `engines/excerpting/src/phase3_deterministic.py` | all | Stubs to fill (10 functions) |
| `engines/excerpting/src/phase2_classify.py` | 105–123 | `_build_token_char_map` — reuse for word→char conversion |
| `engines/excerpting/tests/conftest.py` | all | Existing factory helpers |

## What to Build

### Shared Helper

**`_word_to_char_range(assembled_text, start_word, end_word) → tuple[int, int]`**
Converts word offsets to a character range in `assembled_text`. Uses `_build_token_char_map` from phase2_classify.py.
Returns `(char_start, char_end)` where `char_start` is the first character of token `start_word` and `char_end` is one past the last character of token `end_word` (Python-style exclusive end). So `assembled_text[char_start:char_end]` gives the substring.

**Critical off-by-one detail:** `_build_token_char_map` returns spans as `(start, end)` where `end` is exclusive. So `char_start = spans[start_word][0]` and `char_end = spans[end_word][1]`. Do NOT add +1 to char_end — the span end is already exclusive.

### Function 1: `compute_excerpt_id(source_id, div_id, chunk_index, unit_index) → str` (F-DET-1)
Format: `exc_{source_id}_{div_id}_{chunk_index}_{unit_index}`
`chunk_index` comes from `chunk.split_info.chunk_index` if split_info exists, else `0`.

### Function 2: `extract_primary_text(assembled_text, start_word, end_word) → str` (F-DET-2)
Substring extraction using `_word_to_char_range`. Returns `assembled_text[char_start:char_end]`.
**CRITICAL:** This is a substring, NOT `' '.join(tokens[start:end+1])`. The difference: substring preserves internal `\n\n` paragraph breaks and multiple spaces. Split-and-rejoin collapses them. The SPEC explicitly warns about this (§7.1 F-DET-2 Note).

### Function 3: `compute_layer_attribution(assembled_text, text_layers, start_word, end_word, assembly_metadata) → AuthorAttribution` (F-DET-3)
The most complex function. Implements §7.1 F-DET-3 + §6.2 LA-1–LA-4:

Step 1: Convert word range to character range via `_word_to_char_range`.
Step 2: **Merge split layer segments.** Before computing coverage, merge consecutive `text_layers` segments with identical `(layer_type, author_canonical_id)` that are separated by offsets in `assembly_metadata.layer_split_points`. Use `layer_split_points[i].char_offset_in_assembled` to detect split boundaries. Two segments are "separated by a split point" if the first segment's end equals the split point and the second segment's start follows immediately.
Step 3: Compute each (merged) layer's character overlap with the unit range. `overlap = max(0, min(layer_end, unit_end) - max(layer_start, unit_start))`. Coverage = `overlap / unit_length`.
Step 4: Apply rules in order:
- **LA-4:** Any layer has 100% coverage → attribute to that layer.
- **LA-1:** Any layer has ≥80% coverage → attribute to that layer.
- **LA-2:** No layer has ≥80% AND exactly 2 layers → attribute to the outermost (highest layer_type level: hashiyah > sharh > matn).
- **LA-3:** No layer has ≥80% AND (3+ layers OR dominant <60%) → emit `EX-M-001` warning, return attribution for the highest-coverage layer with `rule_applied="LA-3"`.

Return: `AuthorAttribution(layer_id=..., author_id=..., coverage_pct=..., rule_applied="LA-N")`.
For `layer_id`: use the layer_type value as a string identifier (e.g., `"matn"`, `"sharh"`).
For `author_id`: use `layer.author_canonical_id` if available, else `"unknown"`.

### Function 4: `compute_content_types(segments, unit_segment_indices) → list[ScholarlyFunction]` (F-DET-4)
Collect `scholarly_function` from each ClassifiedSegment whose index is in `unit_segment_indices`. Deduplicate. Return as a list (order doesn't matter).

### Function 5: `detect_evidence_refs(primary_text) → list[EvidenceRef]` (F-DET-5)
Pattern matching for three evidence types:

**Quran (EV-1):** Scan for `﴿...﴾` delimiters (U+FD3E and U+FD3F). Extract text between them. Return `EvidenceRef(type="quran", surah=None, ayah_start=None, ayah_end=None, text_snippet=<extracted>)`. Canonical Quran lookup is deferred (DD-S3-3).

**Hadith (EV-2):** Scan for markers: `رواه`, `أخرجه`, `في الصحيحين`, `متفق عليه`, `في صحيح`, `في سنن`. Short markers (`رواه`, `أخرجه`) require word boundary. Multi-word phrases are safe without. Return `EvidenceRef(type="hadith", text_snippet=<50 chars around marker>, marker_text=<matched pattern>)`.

**Ijma (EV-3):** Scan for markers: `أجمعوا`, `إجماع`, `لا خلاف`, `اتفق العلماء`, `بالاتفاق`. Short markers (`أجمعوا`, `إجماع`, `بالاتفاق`) require word boundary. Multi-word phrases safe without. Return `EvidenceRef(type="ijma", marker_text=<matched>, text_snippet=<50 chars around marker>)`.

**Word boundary check:** A marker has a word boundary if the character before it (if any) is whitespace or start-of-text, AND the character after it (if any) is whitespace, punctuation, or end-of-text. Arabic punctuation includes: `،` `؛` `؟` `٪` `.` `,` `:` `(` `)`.

### Function 6: `compute_page_range(physical_pages, join_points, char_start, char_end) → Optional[PageRange]` (F-DET-6)
If `physical_pages` is empty, return `None`.
Use `join_points[i].char_offset_in_assembled` to determine which physical pages overlap with `[char_start, char_end)`.
Return `PageRange(volume=..., start_page=min_page, end_page=max_page)`.

### Function 7: `compute_word_offsets(start_word, end_word) → tuple[int, int]` (F-DET-7)
Trivial passthrough — returns `(start_word, end_word)`. Exists to make the field-computation pattern uniform.

### Function 8: `filter_relevant_footnotes(primary_text, assembled_text, all_footnotes, char_start, char_end) → list[Footnote]` (F-DET-8)
For each footnote in `all_footnotes`:
1. Search `assembled_text` for the pattern `⌜{footnote.ref_marker}⌝` (Unicode characters U+231C and U+231D).
2. If found AND the match position falls within `[char_start, char_end)`, the footnote is relevant.
3. If not found anywhere in `assembled_text`, log a warning (orphaned footnote marker).
Return the list of relevant footnotes.

### Function 9: `compute_quoted_scholars(text_layers, unit_char_start, unit_char_end, primary_layer) → list[ScholarAttribution]` (F-DET-9)
From the layer overlap in F-DET-3, identify layers with >0% coverage that are NOT the primary layer.
For each, create `ScholarAttribution(mention_text="[structural: {layer_type}]", resolved_name=layer.author_canonical_id, role=<computed>, confidence=1.0, source="layer_overlap")`.
Role: if the non-primary layer is MATN in a sharh unit → `"classification_frame"`. Otherwise → `"quoted_opinion"`.

### Function 10: `build_deterministic_excerpts(chunk, units, segments) → list[ExcerptRecord]` (Orchestrator)
For each TeachingUnit:
1. Compute chunk_index from `chunk.split_info`
2. Call F-DET-1 through F-DET-9
3. Assemble a partial ExcerptRecord:
   - Deterministic fields from F-DET-1–9
   - Passthrough fields from TeachingUnit: `text_snippet`, `primary_function`, `secondary_functions`, `description_arabic`, `self_containment`, `self_containment_notes`
   - `div_path` from `chunk.div_path`
   - **LLM fields set to defaults:** `excerpt_topic=[]`, `school=None`, `school_confidence=None`, `takhrij_data=None`, `terminology_variants=[]`, `cross_references=[]`, `context_hint=None`, `consensus_metadata=None`
   - **Gate/review flags:** `gate_flags=[]`, `review_flags=[]`
4. Return the list of ExcerptRecords.

**DD-S3-1: `school` field requires explicit None.**
The ExcerptRecord model has `school: Optional[str]` with NO default (DD8 Pattern 1 from contracts review). The orchestrator MUST pass `school=None` explicitly — omitting it will raise a validation error.

### Module: Tests

**File: `tests/test_phase3_deterministic.py`**

**Test categories:**

1. **F-DET-1 excerpt_id:** basic format, split chunk (chunk_index > 0), unsplit chunk (chunk_index = 0)
2. **F-DET-2 primary_text:** substring extraction preserves internal whitespace (`\n\n`), single-word unit, full-text unit
3. **F-DET-3 layer attribution:** LA-4 (100% single layer), LA-1 (≥80% dominant), LA-2 (two layers, neither ≥80%), LA-3 (three layers → EX-M-001), layer_split_point merging
4. **F-DET-4 content_types:** deduplication, single function, multiple functions
5. **F-DET-5 evidence_refs:** Quran ﴿...﴾ detection, hadith marker detection, ijma marker detection, word boundary false positive prevention, no false positives on conjugated forms
6. **F-DET-6 page_range:** single page, multi-page span, null when no pages
7. **F-DET-8 footnote_filtering:** relevant footnote included, irrelevant excluded, orphan marker warning
8. **F-DET-9 quoted_scholars:** non-primary layer detected, role computation, primary layer excluded
9. **Orchestrator:** happy path (single unit), multi-unit, school=None explicit, passthrough fields correct

**Conftest additions:**
```python
def _make_multi_layer_chunk(**overrides) -> AssembledChunk:
    """AssembledChunk with MATN + SHARH layers for attribution testing."""
    ...

def _make_chunk_with_footnotes(**overrides) -> AssembledChunk:
    """AssembledChunk with footnotes containing ⌜N⌝ markers in the text."""
    ...
```

**Expected total: 147 + ≥30 = ≥177 passed tests.**

## Design Decisions (Pre-Resolved)

**DD-S3-1: `school` field requires explicit None.**
See Function 10 above. The ExcerptRecord model requires `school` to be explicitly passed. Omitting it raises ValidationError.

**DD-S3-2: Import `_build_token_char_map` from phase2_classify.py.**
Do NOT duplicate the token-to-character mapping logic. Import `from engines.excerpting.src.phase2_classify import _build_token_char_map`. Build a `_word_to_char_range` wrapper in phase3_deterministic.py that calls it.

**DD-S3-3: Quran canonical lookup is deferred.**
F-DET-5 detects ﴿...﴾ delimiters and extracts the text, but does NOT resolve surah/ayah numbers. The canonical Quran reference data is a build-time artifact not yet available. Return `surah=None, ayah_start=None, ayah_end=None` for all Quran evidence refs.

**DD-S3-4: Evidence detection uses word boundary checks for short markers.**
Hadith markers `رواه` and `أخرجه` and ijma markers `أجمعوا`, `إجماع`, `بالاتفاق` require word-boundary checking (lesson from normalization S4/S5 — short Arabic verb stems false-positive on conjugated forms). Multi-word phrases (`في الصحيحين`, `متفق عليه`, `لا خلاف`, `اتفق العلماء`, `في صحيح`, `في سنن`) are safe without boundary checks — the multi-word match is already specific enough.

**DD-S3-5: LLM-enriched fields get safe defaults.**
The orchestrator sets all LLM-enriched fields to empty/null defaults. These are structurally valid — the ExcerptRecord model accepts them. Session 4 will populate them. The `review_flags` list does NOT include `llm_enrichment_failed` at this stage — that flag is set by Session 4 when the actual LLM call fails.

**DD-S3-6: `attribution_confidence` is None for LA-1/LA-2/LA-4, set by consensus for LA-3.**
The SPEC says: "Null for deterministic LA-1/2/4. 0.67 for 2-of-3 consensus (LA-3). 0.0 for all-3-disagree." Session 3 sets `attribution_confidence=None` for all rules. Session 4's consensus step fills it for LA-3 cases.

**DD-S3-7: Layer split point merging algorithm.**
Two consecutive text_layer segments should be merged if:
(a) They have identical `layer_type` AND `author_canonical_id`, AND
(b) There exists a `layer_split_point` in `assembly_metadata.layer_split_points` whose `char_offset_in_assembled` equals the first segment's `end` value.
After merging, the combined segment has `start` = first segment's `start`, `end` = second segment's `end`. Process all merge pairs before computing coverage.

## Do NOT Do

1. **Do NOT implement §7.2 (LLM enrichment)** — that's Session 4.
2. **Do NOT implement §7.3 (consensus verification)** — that's Session 4.
3. **Do NOT implement §7.4 (validation)** — that's Session 5.
4. **Do NOT modify `contracts.py`** unless you find a bug.
5. **Do NOT modify Phase 1 or Phase 2 code.**
6. **Do NOT implement Quran canonical lookup** in F-DET-5. Just detect delimiters.
7. **Do NOT call any LLM.** Phase 3 deterministic is pure algorithmic code.
8. **Do NOT invent error codes.** Use only codes from `ExcerptingErrorCodes`.

## Verification

1. `python -m pytest engines/excerpting/tests/ -v --tb=short` → **≥177 passed** (147 + ≥30 new), 0 failed
2. `grep -r "raise NotImplementedError" engines/excerpting/src/phase3_deterministic.py` → empty output
3. `grep -c "def test_" engines/excerpting/tests/test_phase3_deterministic.py` → ≥30
4. Layer attribution tests cover all 4 rules (LA-1–LA-4): `grep -c "LA-" engines/excerpting/tests/test_phase3_deterministic.py` → ≥4
5. Evidence detection tests include word-boundary false positive prevention
6. `grep -r "import anthropic" engines/excerpting/src/` → empty (no direct API imports)
7. `primary_text` extraction test verifies `\n\n` preservation (not split-and-rejoin)
8. All new test files import factory helpers from conftest

## After This

Session 4 will implement Phase 3 Stage 2 (§7.2 LLM enrichment) and Stage 3 (§7.3 consensus verification). That session will require real LLM calls and cross-provider consensus.
