# NEXT — Excerpting Engine: CC Build Session 1 (Phase 1)

## Current Position

- Excerpting SPEC: ✅ COMPLETE (2387 lines, 12 sections)
- contracts.py: ✅ COMPLETE (1111 lines, independently reviewed)
- conftest.py: ✅ 4 factories (AssembledChunk, ClassifiedSegment, TeachingUnit, ExcerptRecord)
- Module stubs: ✅ All 9 stub files written with type signatures
- Test baseline: **0 tests** (conftest.py only, no test files)
- HEAD commit: (see `git log --oneline -3`)

## What to Do

**Build Phase 1: Deterministic Preprocessing (§4).**

Fill the stub `engines/excerpting/src/phase1_assembly.py` with implementation code. Write tests alongside code. Phase 1 is fully deterministic — no LLM calls, no external dependencies beyond the input NormalizedPackage.

This session covers all 7 steps from §4.1:
1. Division tree walking (§4.2)
2. Cross-page text assembly (§4.3)
3. Tiny division merging (§4.4)
4. Oversized division splitting (§4.5)
5. Metadata aggregation + footnote renumbering (§4.7)
6. Text layer rebasing (§4.6)
7. Heading alignment filter (§4.8)
8. Self-validation V-P1-1 through V-P1-6 (§4.9)

## Context

Phase 1 absorbs the old passaging engine's core: cross-page assembly, division merging, splitting. But unlike the old passaging, Phase 1 does NOT apply format-specific strategies — it treats all text identically. Format-aware processing is Phase 2's job (the LLM understands format natively).

The validated reference implementations in `experiments/architecture_test/extract_divisions.py` are your guide for the core algorithms. These are tested, working implementations — adapt them (don't copy blindly — the experiment operates on raw dicts, but production code uses Pydantic models).

**CRITICAL ORDER:** Step 5 (footnote renumbering) modifies `assembled_text` and therefore changes character offsets. It MUST run before step 6 (text layer rebasing). §4.1 is explicit about this ordering.

## Read First (in this order)

1. **`engines/excerpting/SPEC.md` §4** (lines 609–778) — Phase 1 specification. THE AUTHORITY.
2. **`engines/excerpting/SPEC.md` §2.3.2** (lines 136–195) — AssembledChunk fields + invariants I-AC-1 through I-AC-7.
3. **`engines/excerpting/src/phase1_assembly.py`** — Stub file with all function signatures, types, and SPEC references. Fill this.
4. **`engines/excerpting/contracts.py`** — All types used by Phase 1 (AssembledChunk, JoinPoint, AssemblyMetadata, SplitInfo, ExcerptingConfig, ExcerptingErrorCodes). Skim lines 218–360, 670–760.
5. **`engines/normalization/contracts.py`** — Upstream types consumed: NormalizedPackage (line 716), DivisionNode (line 484), ContentUnit (line 427), ContentFlags (line 216), TextLayerSegment (line 110), BoundaryContinuity (line 257), Footnote (line 168), PhysicalPage (line 101).
6. **`engines/excerpting/tests/conftest.py`** — Existing test factories. You'll ADD new ones here.
7. **`experiments/architecture_test/extract_divisions.py`** — Validated reference implementations: `find_leaf_divisions()`, `assemble_text()`, `rebase_text_layers()`, `aggregate_content_flags()`, `strip_arabic_noise()`, `arabic_word_count()`. BC_JOIN_MAP at line 27.
8. **`engines/excerpting/docs/testing.md`** — Test categories per file. Follow this structure.

Do NOT read the full 2387-line SPEC. §4 and §2.3.2 are all you need.

## What to Build

### Implementation (`engines/excerpting/src/phase1_assembly.py`)

Fill every function stub. The stub has complete type signatures and SPEC references — follow them exactly. Key implementation notes:

**§4.2 — Division tree walking:**
- Recursive walk. Leaf = empty `children` list.
- Skip criteria: all-TOC, all-index, all-blank, bibliography keywords (word-boundary-aware), empty range.
- Word-boundary matching for exclude keywords: keyword preceded by start-of-string or whitespace, followed by end-of-string or whitespace. Use `strip_arabic_noise()` on the heading before matching.
- "مصادر الأحكام" must NOT match (it's a content chapter, not bibliography).

**§4.3 — Cross-page text assembly:**
- Separator mapping in BC_SEPARATOR_MAP constant (already in stub).
- Mid-sentence word-final detection: check last char of prev unit (after stripping whitespace). Word-final indicators: taa marbuta (ة), alif maqsura (ى), tanwin diacritics (ً/ٌ/ٍ as last combining char), whitespace. If word-final → insert space. Otherwise → empty (mid-word).
- Skip content units with is_toc_page/is_index_page/is_blank (but record their unit_index in constituent_unit_indices per I-AC-4).
- Record one JoinPoint per page boundary.

**§4.4 — Tiny division merging:**
- Operate on sibling groups (same parent in division tree).
- Merge with next sibling. If no next, merge with previous.
- Size guard: combined must not exceed OVERSIZED_DIVISION_WORDS.
- Separator between merged chunks: `"\n\n"`.
- merge_history = [first_div_id, second_div_id, ...]. I-AC-6.
- Recursive: if result still tiny, merge again with next sibling.

**§4.5 — Oversized division splitting:**
- Split point priority: heading_markers > section_breaks > paragraph_breaks > sentence_boundary.
- Heading: any content unit with `structural_markers.heading_detected == true`.
- Section: `"\n\n"` nearest midpoint.
- Paragraph: `"\n\n"` nearest midpoint (same as section in practice).
- Sentence: terminal punctuation (`.` `؟` `!`) + whitespace nearest midpoint.
- Recursive: if split result still oversized, split again.
- chunk_id: `{div_id}_chunk_0`, `{div_id}_chunk_1`, etc.
- All split chunks share same constituent_unit_indices (I-AC-4).
- Text layers sliced at split point. layer_split_points recorded.

**§4.7 — Metadata aggregation:**
- Content flags: OR-aggregate. Simple boolean per flag.
- Footnotes: collect in order, dedup by ref_marker (keep first, EX-A-005 for dups).
- Footnote renumbering: if same ref_marker from different pages, renumber sequentially. Update both ⌜N⌝ in text AND ref_marker in footnotes. Record old→new map.
- **THIS MODIFIES assembled_text.** Run BEFORE text layer rebasing.

**§4.6 — Text layer rebasing:**
- For each content unit: add cumulative offset to each layer segment's start/end.
- Cumulative offset = sum of (separator length + previous unit text length).
- After rebasing: merge adjacent segments with same layer_type + author_canonical_id.
- Validate I-AC-2: union covers [0, len(assembled_text)). Use `validate_layer_coverage()` from contracts.py.
- Clamp overflowing segments (EX-A-004). Gap detection (EX-A-003).

**§4.8 — Heading alignment:**
- `strip_arabic_noise()`: remove U+200C, U+200D, U+0640, U+064B–U+0652, U+0670. Collapse whitespace.
- Check if first 30 stripped chars of heading appear in first 200 stripped chars of text.
- Sets `heading_alignment_ok`. Quality flag only — does not gate processing.

**§4.9 — Validation:**
- 6 checks. Fatal checks raise. Warning checks log.
- Use `validate_ac_invariants()` and `validate_layer_coverage()` from contracts.py.

### Tests

Write tests alongside implementation. Follow the structure in `engines/excerpting/docs/testing.md`. **Session 1 test files:**

1. `test_phase1_tree_walk.py` — 12 tests per testing.md
2. `test_phase1_assembly.py` — 9 tests
3. `test_phase1_merge.py` — 7 tests
4. `test_phase1_split.py` — 9 tests
5. `test_phase1_layers.py` — 6 tests
6. `test_phase1_metadata.py` — 7 tests
7. `test_phase1_alignment.py` — 4 tests
8. `test_phase1_validation.py` — 6 tests

**Minimum: 55 tests total.** Actual count may be higher — each test category in testing.md is a minimum.

### conftest.py additions

Add these factories to `engines/excerpting/tests/conftest.py`:

```python
def _make_content_unit(**overrides) -> ContentUnit:
    """ContentUnit with valid defaults. One per physical page."""

def _make_division_node(**overrides) -> DivisionNode:
    """DivisionNode with valid defaults."""

def _make_normalized_package(**overrides) -> NormalizedPackage:
    """Minimal valid NormalizedPackage: 1 division, 2 content units."""

def _make_division_tree(leaf_count: int) -> list[DivisionNode]:
    """Generate a division tree with specified leaf count under one root."""
```

Follow patterns from normalization conftest.py. Use real Arabic text from `_DEFAULT_AC_TEXT` for content units.

## Design Decisions (pre-resolved — do NOT re-decide)

1. **BC_SEPARATOR_MAP** is the source of truth for separator mapping. Already in the stub as a constant.
2. **Word-final detection** for mid_sentence boundaries uses taa marbuta, alif maqsura, tanwin, and whitespace. These are the SPEC-defined indicators.
3. **Merge size guard**: combined word count, NOT character count. `_count_arabic_words()` from contracts.py.
4. **Split point search**: search for `"\n\n"` nearest midpoint, NOT first occurrence. "Nearest midpoint" means: find all occurrences, pick the one whose char offset is closest to `len(text) // 2`.
5. **Footnote marker format**: `⌜N⌝` where N is the ref_marker string. The regex pattern is `r'⌜([^⌝]+)⌝'`.
6. **All LLM calls go through OpenRouter.** Not relevant for Phase 1 (no LLM calls), but do not add any LLM code.

## Do NOT Do

- Do NOT modify `contracts.py`. It was independently reviewed and accepted.
- Do NOT modify the existing `conftest.py` factories — only ADD new ones below the existing code.
- Do NOT implement Phase 2 or Phase 3 code. Phase 1 only.
- Do NOT modify the stub files for Phase 2/3 (phase2_classify.py, phase2_group.py, etc.).
- Do NOT apply Unicode normalization (NFC/NFD/NFKC/NFKD) to Arabic text. Preserve diacritics exactly.
- Do NOT delete the `tracer.py` file — it's a historical artifact, leave it.
- Do NOT read the full SPEC — only §4 and §2.3.2.

## Verification (run before committing)

```bash
# 1. All tests pass
python -m pytest engines/excerpting/tests/ -v --tb=short

# 2. Test count >= 55
python -m pytest engines/excerpting/tests/ -v --tb=short 2>&1 | grep "passed"

# 3. No import errors
python -c "from engines.excerpting.src.phase1_assembly import run_phase1; print('OK')"

# 4. Lint clean
ruff check engines/excerpting/src/phase1_assembly.py engines/excerpting/tests/

# 5. Type check on stub interface preserved
python -c "
from engines.excerpting.src.phase1_assembly import run_phase1
from engines.normalization.contracts import NormalizedPackage
from engines.excerpting.contracts import ExcerptingConfig
import inspect
sig = inspect.signature(run_phase1)
params = list(sig.parameters.keys())
assert params == ['package', 'config'], f'Unexpected params: {params}'
print('Interface preserved')
"
```

## Expected Outcome

After this session:
- `engines/excerpting/src/phase1_assembly.py` fully implemented (~800–1200 lines)
- 8 test files in `engines/excerpting/tests/` with ≥55 tests
- All tests pass
- conftest.py has 4 new factories (8 total)
- Phase 1 correctly transforms NormalizedPackage → list[AssembledChunk]

## After This

Architect reviews CC output (kr-reviewing-cc-output protocol). Then CC Session 2: Phase 2 (classification + grouping).
