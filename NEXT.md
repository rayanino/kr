# NEXT — Excerpting Engine Session 3: Phase 3.1 (Deterministic Metadata Assembly)

## Current Position

- **Excerpting Phase 1:** ACCEPTED — deterministic assembly (77 tests, 1,531 lines)
- **Excerpting Phase 2:** ACCEPTED — LLM classification + grouping (72 tests, 854 lines, review findings F-1/F-2 fixed)
- **Test baseline:** 149 passed (excerpting), 503 passed (normalization), 566 passed (source)
- **Open SPEC errata:** None
- **Phase 2 output:** `run_phase2a()` produces `dict[chunk_id → list[ClassifiedSegment]]`, `run_phase2b()` produces `dict[chunk_id → list[TeachingUnit]]`

## What to Do

Implement Phase 3.1: Deterministic Metadata Assembly (SPEC §7.1). This fills the stubs in `phase3_deterministic.py`. Phase 3.1 computes 9 fields that survive even if LLM enrichment fails — they are the minimum viable ExcerptRecord.

**These functions are PURELY DETERMINISTIC — no LLM calls.**

## Context

Phase 3 has three stages: deterministic assembly (§7.1), LLM enrichment (§7.2), consensus verification (§7.3). This session implements ONLY §7.1 — the other two require human supervision.

The layer attribution algorithm (LA-1 through LA-4) is the most complex function. It computes character-level overlap between teaching units and text layer segments to determine which author wrote which unit.

## Read First

| File | Lines | What |
|------|-------|------|
| `engines/excerpting/SPEC.md` | §7.1 (1397–1518) | **Governing spec for all 9 functions** |
| `engines/excerpting/SPEC.md` | §6.2 (1261–1290) | Layer attribution rules LA-1–LA-4 |
| `engines/excerpting/SPEC.md` | §2.2 (97–165) | ExcerptRecord contract definition |
| `engines/excerpting/contracts.py` | 359–427 | ClassifiedSegment, TeachingUnit models |
| `engines/excerpting/contracts.py` | 428–520 | ExcerptRecord model (target output) |
| `engines/excerpting/contracts.py` | 726–759 | ExcerptingConfig parameters |
| `engines/excerpting/src/phase3_deterministic.py` | all | Stubs to fill (10 functions) |
| `engines/excerpting/tests/conftest.py` | all | Factory helpers |
| `engines/normalization/contracts.py` | TextLayerSegment, LayerMapEntry | Upstream types consumed by F-DET-3 |

## What to Build

### Function 1: `compute_excerpt_id(source_id, div_id, chunk_index, unit_index) → str`
Format: `exc_{source_id}_{div_id}_{chunk_index}_{unit_index}`.
For unsplit chunks: chunk_index = 0. For split: chunk_index = split_info.chunk_index.

### Function 2: `extract_primary_text(assembled_text, start_word, end_word) → str`
Split assembled_text by whitespace, record each token's char start/end. Extract substring `assembled_text[char_start:char_end+1]`. SUBSTRING, not split-rejoin — preserves \\n\\n between paragraphs.

### Function 3: `compute_layer_attribution(assembled_text, text_layers, start_word, end_word, layer_map, layer_split_points) → AuthorAttribution`
This is the MOST COMPLEX function. Algorithm:
1. Convert word offsets to char offsets (same method as F-DET-2)
2. Merge consecutive layer segments with same type+author separated by split points
3. Compute each layer's character overlap percentage
4. Apply rules: LA-4 (100%) → LA-1 (≥80%) → LA-2 (2 layers, highest wins) → LA-3 (ambiguous → EX-M-001)
Output: `{layer_id, author_id, coverage_pct, rule_applied}`

### Function 4: `compute_content_types(segments) → list[ScholarlyFunction]`
Collect scholarly_function from each segment in the unit. Deduplicate.

### Function 5: `detect_quran_verses(primary_text) → bool`
Also builds evidence_refs. Scan for ﴿...﴾, hadith markers (رواه, أخرجه, etc.), consensus markers (أجمعوا, إجماع, etc.). Word-boundary-aware matching.

### Function 6: `compute_page_range(physical_pages, start_word, end_word) → Optional[PageRange]`
Convert word→char offsets. Find overlapping physical pages via join_points. Return PageRange or None if no page data.

### Function 7: `compute_word_offsets(start_word, end_word) → tuple[int, int]`
Trivial pass-through.

### Function 8: `filter_relevant_footnotes(primary_text, all_footnotes) → list`
Search assembled_text for ⌜{ref_marker}⌝ pattern. Include footnotes whose markers fall in unit's char range.

### Function 9: `compute_segment_indices(unit) → list[int]`
Return unit.segment_indices.

### Function 10: `build_deterministic_excerpts(chunks, grouped, classified, manifest, config) → list[ExcerptRecord]`
Orchestrator: for each chunk, for each TeachingUnit, call F-DET-1 through F-DET-9, assemble ExcerptRecord with LLM fields set to None/empty.

### Tests: `tests/test_phase3_deterministic.py`
- ≥30 test functions covering all 10 functions
- Real Arabic text from tests/fixtures/
- Edge cases: single-layer, multi-layer (sharh+matn), split chunks, empty footnotes
- Quran verse detection with real ﴿...﴾ text
- Layer attribution: LA-1, LA-2, LA-3, LA-4 paths
- Use conftest factories for test data

**Expected total: 149 + ≥30 = ≥179 passed tests.**

## Design Decisions (Pre-Resolved)

**DD-S3-1: Word-to-char conversion is shared.**
Functions F-DET-2, F-DET-3, F-DET-6, F-DET-8 all need word→char mapping. Extract a helper `_word_to_char_offsets(assembled_text) → list[tuple[int,int]]` that returns (char_start, char_end) for each token.

**DD-S3-2: Evidence detection returns structured refs.**
`detect_quran_verses()` signature is misleading — it also detects hadith and consensus markers per SPEC §7.1 F-DET-5. It returns bool (has_quran) but the evidence_refs list is built as a side effect stored on the ExcerptRecord by build_deterministic_excerpts.

**DD-S3-3: Layer split point merging is critical.**
Before computing coverage in F-DET-3, consecutive layer segments with identical type+author separated by a split point MUST be merged. Failure creates false LA-3 ambiguity at split boundaries.

## Do NOT Do

1. **Do NOT implement Phase 3.2** (LLM enrichment) or Phase 3.3 (consensus).
2. **Do NOT modify contracts.py** unless you find a bug.
3. **Do NOT modify Phase 1 or Phase 2 code.** They are frozen.
4. **Do NOT make LLM calls.** This is purely deterministic.
5. **Do NOT use \\d in regex.** Use [0-9] for ASCII digits.
6. **Do NOT use .lower()/.upper()/.strip() on Arabic strings.**

## Verification

1. `python -m pyright engines/excerpting/src/phase3_deterministic.py` → 0 errors
2. `python -m pytest engines/excerpting/tests/ -v --tb=short` → **≥179 passed**, 0 failed
3. `grep -r "raise NotImplementedError" engines/excerpting/src/phase3_deterministic.py` → empty
4. Layer attribution tests cover LA-1, LA-2, LA-3, LA-4 paths
5. Quran detection tests use real ﴿...﴾ Arabic text
6. All new test files import factory helpers from conftest
