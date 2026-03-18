# NEXT — Write Session 3 handoff (Architect session)

## Current position: Session 2 COMPLETE and ACCEPTED (commit 79a4e76). Shamela Passes 1–3 implemented: 1,115 lines, 65 tests, all 10 ADV-001–010 pass, 13 real fixtures parse successfully, 4,160 pages/sec on 1,720-page multi-volume.
## What to do: Write Build Session 3 NEXT.md for Claude Code — Structure Discovery (4-tier heading detection, division tree construction).
## Context: Session 3 implements Pass 4 of the Shamela normalizer. It consumes the `title_spans`, `pagehead_text`, `starts_with_zwnj_heading`, and `primary_text` fields from Session 2's `CleanedPage` output and produces the `division_tree` (manifest) and `structural_markers` (per content unit). The ABD `discover_structure.py` (2,896 lines) provides behavioral reference. Tier 3 LLM decision is MADE: stub with clean interface (see below).
## Owner action needed: YES after — to give the Session 3 handoff to CC.

---

## Session 2 Deliverables (what's already built)

Session 2 produced `CleanedPage` objects that carry all signals Pass 4 needs:

| Field | Source | What Pass 4 does with it |
|-------|--------|--------------------------|
| `title_spans: list[str]` | Pass 1 — double-quote `<span class="title">` | Tier 1 headings (confirmed, html_tagged) |
| `pagehead_text: Optional[str]` | Pass 1 — PageHead div text | Record in `structural_markers.heading_text` |
| `starts_with_zwnj_heading: bool` | Pass 3 — double ZWNJ at line start | Tier 2 signal (high confidence) |
| `primary_text: str` | Pass 3 — cleaned text | Tier 2 keyword scanning (باب, فصل, مبحث, etc.) |
| `unit_index: int` | Pass 1 — monotonic | Division node `start_unit_index` / `end_unit_index` |

Code location: `engines/normalization/src/normalizers/shamela.py` (1,115 lines).

## Read First (in this order)

1. `engines/normalization/CLAUDE.md` (105L) — Engine orientation, module map. Session 3 row says: "Structure discovery (4-tier headings, division tree) | §4.A.6, structural_patterns.yaml".

2. `engines/normalization/SPEC.md` lines 200–207 — §4.A.2 Pass 4 overview (already read in Session 2 prep but re-read for Pass 4 specifics). Key: Tier 1 from frozen HTML, Tier 1.5 TOC, Tier 2 keyword heuristics, Tier 3 LLM, output = division tree + structural_markers.

3. `engines/normalization/SPEC.md` lines 564–654 — §4.A.6 complete structure discovery specification. This is the behavioral authority. Covers: division tree format, heading text in primary_text rules, the 4-tier confidence architecture, TOC cross-referencing, hierarchy inference rules, structure confidence scoring, concrete example.

4. `engines/normalization/reference/structural_patterns.yaml` (340L) — Arabic heading keyword patterns. Quote-style differentiator (already used by Session 2), tagged headings, keyword patterns for باب/فصل/etc., ordinal detection, ZWNJ heading patterns.

5. `reference/archive/abd_code/normalization/discover_structure.py` (2,896L) — ABD 4-tier structure discovery. MASSIVE reference. Read selectively: class architecture, Tier 1 extraction, Tier 2 keyword logic, hierarchy construction. The KR upgrade adds: DivisionNode output format, §5 validation, integration with Session 2's CleanedPage.

6. `engines/normalization/contracts.py` — `DivisionNode` (lines 483–495), `DivisionType` enum (lines 466–480), `StructuralMarkers` (lines 189–196), `HeadingConfidence` enum (lines 42–47), `HeadingDetectionMethod` enum (lines 50–57), `QualityReport.division_count_by_tier` (line 532).

7. `engines/normalization/src/normalizers/shamela.py` (1,115L) — Session 2 implementation. Session 3 adds a `_pass4_discover_structure()` method that takes `list[CleanedPage]` and returns structure data to attach to each page's `structural_markers` and a top-level `division_tree`.

8. `reference/SPEC_ADVERSARY_NORMALIZATION.md` — ADV-016 (باب in name, not heading), ADV-017 (child extends beyond parent), ADV-018 (Tier 1 + Tier 2 duplicate detection). These are mandatory tests for Session 3.

9. `reference/protocols/REVIEW_PROTOCOL.md` — Mandatory two-pass review protocol. Read before reviewing CC output.

10. `reference/protocols/PRE_HANDOFF_VERIFICATION.md` — Mandatory foundation verification before committing handoffs.

11. `reference/protocols/DECISION_DISCIPLINE.md` — Make decisions immediately, don't defer.

## Tier 3 Scoping Decision: DECIDED — Option B (stub with hook)

**Decision:** Build Tiers 1, 1.5, 2 fully. Tier 3 gets a clean interface that raises `NotImplementedError` and logs `NORM_SPARSE_STRUCTURE` when Tiers 1-2 find insufficient headings.

**Evidence:** Empirical analysis of all 13 fixtures shows zero would trigger Tier 3. Every fixture has ≥3 Tier 1 headings per 50 pages. The smallest ratio is fixture 02_nahw_muhaqiq (19 headings / 296 pages). Fixture 07_balagha has 146 Tier 1 + 34 Tier 2 headings across 288 pages. Passaging engine development needs division trees — Tiers 1-2 provide sufficient structure for all test data.

**Tier 3 hook interface** (for Session 3 to stub):
```python
def _tier3_llm_discover(
    self,
    candidates: list[HeadingCandidate],
    genre: str,
    existing_headings: list[DivisionNode],
    text_windows: list[str],
) -> list[HeadingCandidate]:
    """Tier 3: LLM semantic judgment for ambiguous headings.
    NOT YET IMPLEMENTED — stubbed with NORM_SPARSE_STRUCTURE logging."""
    raise NotImplementedError("Tier 3 LLM structure discovery")
```

## Adversarial Cases for Session 3

| ADV | Type | What it tests |
|-----|------|---------------|
| ADV-016 | arabic_trap | "باب" in scholar name, not at line start → no heading |
| ADV-017 | format_edge_case | Division tree child page range extends beyond parent |
| ADV-018 | multi_signal_conflict | Tier 1 heading also matches Tier 2 keyword → one node, not two |

## Key Complexity Notes

1. **Hierarchy inference.** كتاب > باب > فصل > مبحث > مطلب > فائدة/تنبيه/قاعدة. Ordinal sequences are siblings. Ambiguous levels need context. The ABD code has extensive logic for this — study it carefully.

2. **Division node page ranges.** Each `DivisionNode` has `start_unit_index` and `end_unit_index` (inclusive). Computing these requires knowing where the NEXT heading at the same or higher level appears. This is a two-pass problem: first detect headings, then build the tree with ranges.

3. **`structural_markers` vs `division_tree`.** Each content unit gets `structural_markers` (was a heading detected on this page?). The manifest gets `division_tree` (the full hierarchy). These must be consistent — every heading in the division tree must correspond to a `structural_markers.heading_detected = True` on the corresponding page.

4. **TOC cross-referencing (Tier 1.5).** If `is_toc_page` is detected in content_flags (from Session 5, not yet built), TOC entries can validate/promote other headings. For Session 3, TOC detection can be stubbed — it's a refinement, not the foundation.

## Do NOT Do

- Do NOT modify Session 2 code (`shamela.py` Passes 1–3) except to add the Pass 4 method call.
- Do NOT implement Pass 5 (layer detection) or Pass 6 (output assembly).
- Do NOT implement `content_flags` detection (that's Pass 6 / Session 5).
- Do NOT modify `contracts.py` unless a genuine gap is found.

## After Writing

**Before committing the handoff:** Follow `reference/protocols/PRE_HANDOFF_VERIFICATION.md` — verify every regex, trace all data flows through intermediate structures, test parser behavior empirically. Do NOT commit until verification is complete.

**When CC finishes Session 3:** Follow `reference/protocols/REVIEW_PROTOCOL.md` — mandatory two-pass review. Pass 1 structural, Pass 2 adversarial with probing scripts and fixture spot-checks. Report cumulative build metrics.

Commit the Session 3 NEXT.md. Owner gives it to CC in plan mode first, then implementation.

---

## Cumulative Build Metrics (after Session 2)

```
Implementation:  2,014 lines (shamela.py 1104, contracts.py 724, errors.py 130, base.py 56)
Tests:           1,274 lines (test_shamela_passes.py 788, test_contracts.py 486)
Test count:      106 passing, 22 skipped (placeholders for full pipeline)
Test-to-code:    0.63 ratio, 5.2 tests per 100 impl lines
ADV covered:     10/51 (ADV-001 through ADV-010, Passes 1-3)
Fixtures:        13 real + 1 hand-crafted (ibn_aqil)
Performance:     4,160 pages/sec on 1,720-page multi-volume
```

## Known Limitations (from Session 2)

See `engines/normalization/KNOWN_LIMITATIONS.md` for details:
- **L-001:** Bare-number and unnumbered footnotes classified but not parsed (105 pages across 3 fixtures). Text preserved in preamble, no data loss. Fix point: Session 5.
- **L-002:** ضياء السالك commentary numbering collision (1 book). Fix point: Session 4 (layer detection).

