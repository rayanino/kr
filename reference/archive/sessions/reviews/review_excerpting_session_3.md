# CC Review Checklist — Excerpting Session 3: Phase 3 Deterministic Metadata Assembly

> Commit under review: `c14c2776` (merged at `0252c57f`)
> Review date: 2026-03-24

## Pre-review
- [x] Repo pulled, commit diff read (`git diff c14c2776^..c14c2776 --stat` → 5 files, +1447/-53)
- [x] NEXT.md re-read — requested: implement 10 F-DET functions in `phase3_deterministic.py`, 37+ tests, 2 conftest helpers, docstring fix, SPEC errata

## Pass 1: Structural
- [x] Every CC-modified file opened and read **in full** — list files:
  - [x] `engines/excerpting/src/phase3_deterministic.py` — 12 functions (verified: `grep -c "^def " → 12`)
  - [x] `engines/excerpting/tests/test_phase3_deterministic.py` — 37 test functions (verified: `grep -c "def test_" → 37`)
  - [x] `engines/excerpting/tests/conftest.py` — +142 lines, 2 new helpers (`_make_multi_layer_chunk`, `_make_chunk_with_footnotes`)
  - [x] `engines/excerpting/contracts.py` — docstring fix only (4 lines changed, all `description=` strings)
  - [x] `reference/SPEC_ERRATA.md` — +20 lines: SPEC-NOTE-8 (DD-S3-8 override), SPEC-NOTE-9 (DD-S3-9 placeholder)
  - **RULE 7 check:** Lines 245-393 of phase3_deterministic.py were truncated; requested and read before proceeding.
- [x] All tests run: `184 passed, 2 skipped, 0 failed`
- [x] SPEC cross-reference: every function traces to §7.1 F-DET-1 through F-DET-9, §6.2 LA-1 through LA-4
- [x] **Cross-engine boundary check:**
  - [x] `grep -rn` for ExcerptRecord, AuthorAttribution, EvidenceRef, ScholarAttribution, PageRange — all consumers within `engines/excerpting/` only
  - [x] `python tools/check_cross_engine_contracts.py` → result: `PASS` (normalization→excerpting imports unchanged)
  - [x] No downstream engine imports these types
  - Modified types: `ExcerptRecord` (docstring only — no structural change)
  - Consumers checked: all 7 engine contract files (no cross-engine impact)

## Pass 2: Adversarial
- [x] 10 probing scripts run with constructed inputs — findings:
  - Probe 1: SPEC example trace F-DET-1, F-DET-2, F-DET-3 → ✓ all match
  - Probe 2: F-DET-9 multi-author same-type layers → **⚠ BUG: sharh_B silently excluded**
  - Probe 3: Arabic evidence markers false positives → ✓ expected per DD-S3-8
  - Probe 4: Dedup logic and snippet clamping → ✓ all correct
  - Probe 5: Real diacritized Arabic text end-to-end → ✓ all fields correct
  - Probe 6: Page range boundary conditions (6 sub-cases) → ✓ all pass
  - Probe 7: Full orchestrator E2E multi-layer + evidence + footnotes → ✓ all 33 fields correct
  - Probe 8: Layer split point chain merge (4 sub-cases) → ✓ all correct
  - Probe 9: Whitespace edge cases (multi-space, padded, single token, paragraph) → ✓ all preserved
  - Probe 10: SPEC char_end inclusive vs exclusive convention → ✓ equivalent
- [x] 2+ fixture semantic spot-checks — printed actual Arabic text:
  - Fixture 1: Diacritized matn+sharh (constructed from ibn_aqil pattern) — extraction, layer attribution, evidence detection all correct
  - Fixture 2: Rich fiqh text with Quran ﴿﴾, hadith markers, ijma markers — all 4 evidence refs detected correctly, Quran text extracted
- [x] Cross-engine data flow: contracts.py change is docstring-only — no downstream deserialization impact
- [x] **SPEC concrete example trace (RULE 5):**
  - [x] §7.1 F-DET-1 example (`exc_12345_div_3_2_0_7`) traced → matches ✓
  - [x] §7.1 F-DET-1 split example (`exc_12345_div_3_2_1_3`) traced → matches ✓
  - [x] §7.1 F-DET-2 paragraph break preservation traced → ✓ \n\n preserved, split-rejoin differs
  - [x] §6.2 LA-1 ≥80% coverage scenario traced → ✓ SHARH 89.2%, LA-1 applied correctly
  - Divergences: none
- [x] Edge case probes with constructed inputs: 10 run, 1 finding (R2-F1)

## Pass 3: Self-verification (RULES 6-7)
- [x] Every factual claim in Passes 1-2 verified against code with tool calls:
  - [x] "184 passed, 2 skipped" — re-run pytest → confirmed
  - [x] "37 test functions" — `grep -c "def test_"` → 37 confirmed
  - [x] "12 functions" — `grep "^def "` → 12 confirmed
  - [x] "636 impl / 738 test lines" — `wc -l` → confirmed
  - [x] "No stubs" — `grep "raise NotImplementedError"` → empty confirmed
  - [x] "No LLM imports" — `grep "import anthropic\|import openai"` → empty confirmed
  - [x] "Contracts change is docstring-only" — diff shows only description strings confirmed
  - [x] "Line 480 filters by layer_type.value" — `sed -n '478,482p'` → confirmed
  - [x] "R2-F1 bug reproduction" — re-run probe with fresh script → confirmed (sch_B excluded)
- [x] Check for rationalization patterns:
  - "CC deviation adding review_flags is correct" → Verified: PARTIAL without flag raises ValidationError (I-ER-4). NECESSARY, not rationalized.
  - "Duplicate footnote .find() is correct under contract" → Verified: Phase 1 `renumber_footnotes()` guarantees unique markers per chunk. CORRECT, not rationalized.
  - "R2-F1 has zero current impact" → TRUE but code is semantically wrong vs SPEC, fix is 1 line. NOT rationalized away — classified as blocking.
- [x] Review Notes drafted — each Note verified against code before writing

## Findings

| # | File | Finding | Fix | Fixed? |
|---|------|---------|-----|--------|
| 1 | `phase3_deterministic.py:480` | F-DET-9 `compute_quoted_scholars` filters by `layer_type.value == primary_layer.layer_id` (type-class matching). Should filter by (type, author) identity per SPEC §7.1 F-DET-9 "not the primary layer." Two layers sharing a type but with different authors causes the non-primary author to be silently excluded from `quoted_scholars`. | Change line 480: add author_id check. Add one test with multi-author same-type scenario. | [ ] |

## Fixes committed
- [ ] ALL findings above have `Fixed? [x]`
- [ ] Fix commits pushed to repo
- [ ] Tests re-run after fixes: `[N] passed`
- [ ] `python tools/check_cross_engine_contracts.py` re-run after fixes → `[PASS/FAIL]`

## Verdict

**Verdict: BLOCKED**

One finding (R2-F1): F-DET-9 primary layer exclusion uses type-class matching instead of identity matching. The code is semantically wrong against the SPEC. The fix is one line + one test. See fix directive below.

## Build metrics (cumulative)
```
Implementation: ~2,536 lines (+636 this session)
Tests: 184 passing (+37 this session)
Test-to-code ratio: 5.8 per 100 lines (this session)
SPEC sections implemented: §4 (Phase 1), §5 (Phase 2), §7.1 (Phase 3 deterministic)
SPEC sections remaining: §7.2 (LLM enrichment), §7.3 (consensus), §7.4 (validation)
Known limitations: SPEC-NOTE-8 (evidence detection uses plain substring per DD-S3-8), SPEC-NOTE-9 (resolved_name uses canonical_id per DD-S3-9)
```

## Fix Directive

**File:** `engines/excerpting/src/phase3_deterministic.py`
**Line 480:** Change from:
```python
        if layer.layer_type.value == primary_layer.layer_id:
            continue
```
To:
```python
        if (layer.layer_type.value == primary_layer.layer_id
                and (layer.author_canonical_id or "unknown") == primary_layer.author_id):
            continue
```

**Test to add** in `engines/excerpting/tests/test_phase3_deterministic.py`, class `TestQuotedScholars`:
```python
    def test_multi_author_same_type_not_excluded(self) -> None:
        """Two SHARH authors — non-primary sharh author must appear in quoted_scholars."""
        text = "a" * 60
        layers = [
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_sharh_A",
                start=0, end=20, confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_sharh_B",
                start=20, end=40, confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_matn",
                start=40, end=60, confidence=1.0,
            ),
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        primary = AuthorAttribution(
            layer_id="sharh",
            author_id="sch_sharh_A",
            coverage_pct=0.33,
            rule_applied="LA-3",
        )
        result = compute_quoted_scholars(layers, 0, 60, primary, meta)
        names = [s.resolved_name for s in result]
        assert "sch_sharh_B" in names, "Non-primary sharh author must not be excluded"
        assert "sch_matn" in names, "MATN layer must still appear"
        assert "sch_sharh_A" not in names, "Primary author must be excluded"
```
