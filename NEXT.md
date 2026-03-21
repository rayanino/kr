# NEXT — Normalization Engine Evaluation & Transition

## Current Position

- **Phase:** Step 3 (Evaluate) from `reference/ENGINE_BUILD_BLUEPRINT.md`
- **Previous:** Build complete — all 7 sessions ACCEPTED. Latest review at commit `59ba314`.
- **Engine state:** 420 tests passing (14 skipped), 37/51 ADV, L-001–L-012 documented, 63/63 fixtures passing integration tests with page-loss checks.
- **SPEC errata:** SPEC-NOTE-1 through SPEC-NOTE-3 pending maintenance (see `reference/SPEC_ERRATA.md`).

## What to Do

This is the **normalization engine evaluation**. Three tasks, each in its own session:

1. **Evaluation** (this session) — Assess whether the normalization engine output is reliable enough for passaging to consume.
2. **SPEC maintenance** (can be same or next session) — Fix SPEC-NOTE-1 through SPEC-NOTE-3.
3. **Transition gate** (separate session, after evaluation passes) — Formal prerequisite check via `kr-gating-transitions` before starting the passaging engine build.

### Owner Action Needed

None. The architect does all evaluation work. The owner provides a new chat.

## Read First (in this order)

1. `reference/ENGINE_BUILD_BLUEPRINT.md` §3 (Step 3: Evaluate) — the evaluation methodology
2. `engines/normalization/CLAUDE.md` — module map, build metrics
3. `engines/normalization/KNOWN_LIMITATIONS.md` — L-001 through L-012
4. `reference/SPEC_ERRATA.md` — SPEC-NOTE-1 through SPEC-NOTE-3
5. `KNOWLEDGE_INTEGRITY.md` — the 7 corruption threats (T-1 through T-7)
6. `SILENT_FAILURES.md` — the 7 silent failure patterns
7. `engines/passaging/contracts.py` — what the downstream engine expects
8. `engines/passaging/src/loader.py` — how passaging validates normalization output
9. `engines/normalization/contracts.py` — what the normalization engine produces
10. `reference/protocols/QUALITY_AXIOM.md` — the architect is the sole quality gate

## Skills to Use

- `kr-evaluate` — finding categorization (CORE GAP / ENGINE BUG / EXTENSION OPPORTUNITY / LESSON LEARNED)
- `critical-review` — self-review on the evaluation itself
- `thinking-frameworks` — multi-angle analysis for GO/NO-GO

## Evaluation Scope

The normalization engine is **entirely deterministic** — no LLM calls. This means:
- Layer 1 (Programmatic) and Layer 2 (Pattern Analysis) are the core evaluation.
- Layer 3 replaces web search with **manual structural inspection** (per Blueprint: "For engines that produce structural output, Layer 3 replaces web search with manual inspection").
- Layer 4 is GO/NO-GO aggregation.

### Layer 1: Programmatic Validation

Run quality metrics on all 63 repo fixtures. Collect per-fixture:

```python
# For each fixture, run normalize_source and collect:
{
    "name": "fixture_name",
    "content_units": N,
    "raw_page_divs": M,
    "page_loss": abs(N - M),
    "arabic_ratio": float,       # total Arabic chars / total chars
    "diacritic_count": int,
    "footnote_pages": int,       # pages with footnotes > 0
    "division_count": int,
    "layer_count": int,          # entries in layer_map
    "multi_layer_units": int,    # units with 2+ text_layers
    "boundary_continuity_coverage": float,  # % units with BC != None
    "boundary_types": set,       # distinct BC types
    "has_hadith": int,           # units with hadith flag
    "has_quran": int,            # units with quran flag
    "has_verse": int,            # units with verse flag
    "validation_warnings": list, # warning codes from §5 validation
    "validation_fatals": list,   # fatal codes (should be 0)
}
```

**What to check in aggregate:**
- Zero fatals across all fixtures
- Page loss <= 5 for every fixture (already verified by integration tests, but collect the distribution)
- Arabic ratio > 70% for all non-blank fixtures
- Warning patterns: are the same warnings firing on many fixtures? (may indicate a systematic issue)
- Diacritic preservation: any fixture showing unexpectedly low diacritics?

### Layer 2: Pattern Analysis

Analyze known limitations for downstream impact:

| Limitation | Downstream Impact Question |
|---|---|
| L-001 (bare/unnumbered footnotes) | Does passaging need footnote numbers to link refs? |
| L-002 (ضياء السالك numbering) | Does this book exist in the 2,519 collection? If yes, is it a one-off or pattern? |
| L-003 (same-page heading chains) | Does passaging use heading levels for division grouping? |
| L-004 (Arabic conjunction prefixes) | Does this cause false negatives in boundary detection? Measure on fixtures. |
| L-005 (bold threshold 50 vs 80) | Does this affect layer detection accuracy? The threshold was empirically calibrated. |
| L-006 (hashiyah not implemented) | How many 3-layer texts exist? Is this blocking for passaging? |
| L-007 (marker-only matn over-extension) | Does passaging consume layer boundaries? Impact if matn segment is too long? |
| L-008 (conditional markers excluded) | Are conditional markers common in the fixtures? |
| L-009 (guillemet hadith distance) | Does this cause false positives in boundary continuity? |
| L-010 (division overlap downgraded) | Does passaging rely on non-overlapping divisions? |
| L-011 (writer prev-only orphan) | How likely is this state? Is it recoverable? |
| L-012 (Arabic-Indic footnotes) | Do Shamela exports use Arabic-Indic digit footnotes? |

For each: assess as BLOCKING (must fix before passaging), ACCEPTABLE (passaging works correctly despite limitation), or DEFERRED (only matters for a later engine or extension).

### Layer 3: Manual Structural Inspection

Pick 5 fixtures spanning maximum diversity:
- `02_nahw_muhaqiq` — multi-layer (matn+sharh), 295 pages, muhaqiq annotations
- `03_fiqh` — footnotes (32 pages), single layer
- `04_hadith` — high diacritics (11,120), hadith flags (36/41)
- `06_usul` — rich structure (9 divisions), medium length
- One extended fixture (ext_XX) — pick the most unusual one by Layer 1 metrics

For each, run `normalize_source`, then inspect:
1. **First 3 pages**: print `primary_text` in full. Read as a human scholar would. Are sentence boundaries clean? Are diacritics intact? Any mojibake, HTML artifacts, truncation?
2. **Footnote pages** (if any): print footnotes alongside primary text. Is the separation correct? Are references properly linked (corner brackets)?
3. **Division headings**: print all headings. Do they form a sensible table of contents?
4. **Layer segments** (multi-layer only): print 2 pages showing matn+sharh. Are the boundaries in the right place?
5. **Boundary continuity**: for 5 consecutive pages, print the BC type and confidence alongside the last 30 chars of each page. Does mid_sentence at a page break look correct?

### Layer 4: GO/NO-GO

Aggregate findings. For each finding, categorize per kr-evaluate:
- CORE GAP → blocks transition
- ENGINE BUG → blocks transition
- EXTENSION OPPORTUNITY → document in LESSONS.md, does not block
- LESSON LEARNED → document, does not block

**GO criteria:**
- [ ] Zero CORE GAPs
- [ ] Zero unfixed ENGINE BUGs
- [ ] All known limitations assessed for downstream impact — none blocking
- [ ] SPEC errata (SPEC-NOTE-1 through SPEC-NOTE-3) resolved
- [ ] Contract alignment with passaging verified
- [ ] Manual inspection finds no systematic quality issues

**NO-GO triggers:**
- Any CORE GAP or ENGINE BUG found
- A known limitation assessed as BLOCKING
- Contract misalignment with passaging
- Systematic quality issue in manual inspection (e.g., diacritics dropped on >10% of fixtures)

## SPEC Maintenance (SPEC-NOTE-1 through SPEC-NOTE-3)

Fix these BEFORE the transition gate. They are in `reference/SPEC_ERRATA.md`:

1. **SPEC-NOTE-1** (§4.B.8 confidence contradiction): Update the concrete example to use 0.80 (matching the definition range), OR formally specify the blending mechanism. Recommendation: update example to 0.80 — the blending mechanism adds complexity without value for core.

2. **SPEC-NOTE-2** (§4.B.8 marker table missing `ولنا`): Add `ولنا` to the SPEC marker table under evidence chain openers. This is a simple addition — the implementation already includes it.

3. **SPEC-NOTE-3** (§5 check 4 sharh-majority): Add a comment in the SPEC noting this check is incomplete for 3-layer texts, pending L-006 resolution. No code change — the limitation is inert until hashiyah detection is implemented.

## Output

The evaluation produces:
- `engines/normalization/EVALUATION_REPORT.md` — Layer 1-4 findings, categorization, GO/NO-GO verdict
- `engines/normalization/LESSONS.md` — accumulated lessons from 7 build sessions + evaluation
- Updated `reference/SPEC_ERRATA.md` — SPEC-NOTE fixes applied (or removal after SPEC.md update)
- Updated `engines/normalization/SPEC.md` — SPEC-NOTE fixes
- Updated `NEXT.md` — transition gate directive (if GO) or fix directive (if NO-GO)

## After This

If GO: prepare a separate session for the transition gate (`kr-gating-transitions`). The transition gate formally verifies all prerequisites before starting the passaging engine SPEC design.

If NO-GO: prepare a fix directive for CC and loop back.

## Context

### Engine Architecture Summary

```
Input:  frozen source files + SourceMetadata
        ↓
        dispatcher.py → routes by source_format
        ↓
        shamela.py (6-pass) OR plain_text.py
        ↓
        structure_discovery.py → division tree
        ↓
        layer_detector.py → matn/sharh segments (multi-layer only)
        ↓
        boundary_continuity.py → cross-page signals
        ↓
        content_flagger.py → quran/hadith/verse flags
        ↓
        validation.py → §5 checks 1-10
        ↓
        writer.py → manifest.json + content.jsonl
Output: NormalizedPackage (manifest + content units)
```

### Build Metrics (final)

| Session | Focus | Tests | ADV |
|---------|-------|-------|-----|
| 1 | Contracts | 40 | — |
| 2 | Passes 1-3 | 105 | — |
| 3 | Structure discovery | 125 | — |
| 4 | Layer detection | 173 | 18/51 |
| 5 | Pass 6 (boundary, flags, assembly) | 256 | 22/51 |
| 6 | Validation, writer, plain text, dispatcher | 335 | 29/51 |
| 7 | Integration tests, ADV gap closure | 420 | 37/51 |

Implementation: ~7,797 lines. Tests: 420 passing (14 skipped). Integration: 85 tests on 63 fixtures.

### Passaging Input Contract (what it expects)

From `engines/passaging/src/loader.py`, the 6 validation checks:
1. `manifest.json` exists and is valid JSON → PSG_MANIFEST_INVALID (fatal)
2. `schema_version` recognized → PSG_SCHEMA_UNSUPPORTED (fatal)
3. `content.jsonl` exists → PSG_CONTENT_MISSING (fatal)
4. `total_content_units` matches actual count → PSG_CONTENT_COUNT_MISMATCH (warning)
5. Content units ordered by `unit_index`, no gaps → PSG_CONTENT_UNORDERED (fatal)
6. Division tree ranges consistent → PSG_DIVISION_INCONSISTENT (warning)

The normalization engine's §5 validation + integration tests already verify properties 4, 5, and 6. Properties 1-3 are verified by `normalize_and_write` tests.

### Known Limitations Quick Reference

| ID | Summary | Severity | Likely downstream impact |
|---|---|---|---|
| L-001 | Bare/unnumbered footnotes not parsed | LOW | Footnotes without numbers are rare in Shamela |
| L-002 | ضياء السالك numbering collision | LOW | Single known book |
| L-003 | Same-page heading chains | LOW | Creates deeper nesting than intended |
| L-004 | Arabic conjunction prefixes on markers | MEDIUM | May miss some boundary signals |
| L-005 | Bold threshold 50 vs SPEC 80 | LOW | Empirically calibrated, 80 would miss real matn |
| L-006 | Hashiyah detection not implemented | MEDIUM | 3-layer texts get 2-layer treatment |
| L-007 | Marker-only matn over-extension | LOW | Affects ~5 pages in 02_nahw_muhaqiq |
| L-008 | Conditional markers excluded from BC | LOW | Conservative precision choice |
| L-009 | Guillemet hadith distance heuristic | LOW | May misclassify distant guillemet pairs |
| L-010 | Division overlap downgraded to warning | MEDIUM | Passaging may receive overlapping divisions |
| L-011 | Writer prev-only orphan recovery | LOW | Requires specific failure sequence |
| L-012 | Arabic-Indic footnote markers | LOW | ASCII-only is precision-over-recall |

### SPEC Errata Quick Reference

| ID | Section | Issue | Recommended fix |
|---|---|---|---|
| SPEC-NOTE-1 | §4.B.8 | Confidence example says 0.90, definition says 0.60–0.80 | Update example to 0.80 |
| SPEC-NOTE-2 | §4.B.8 | Marker table missing `ولنا` | Add to evidence chain openers |
| SPEC-NOTE-3 | §5 check 4 | Sharh-majority check incomplete for 3-layer | Add comment, pending L-006 |
