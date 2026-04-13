# Architecture Decision: 5-Engine Pipeline (3 Remaining)

**Date:** 2026-03-22
**Decision maker:** Claude Chat (Architect)
**Status:** COMMITTED
**Supersedes:** Previous premature decision in this file (same date, committed after 10-division experiment only)

---

## Decision

KR adopts a **5-engine pipeline with 3 remaining engines.** Passaging is absorbed into the excerpting engine as an internal preprocessing phase. Atomization is absorbed into the excerpting engine as validated by the Architecture C experiment. Taxonomy and synthesis remain separate engines.

```
Source ✅ → Normalization ✅ → Excerpting → Taxonomy → Synthesis
                                (absorbs passaging + atomization)
```

D-011 transforms from "excerpt contained within passage" to "excerpt contained within division or chunk." This is STRONGER than the original: divisions are the author's own organizational structure, while passages were artificial boundaries.

## Evidence Base

This decision rests on three independent evidence sources:

### 1. Architecture C Experiment (10 divisions, 5 genres)

Validated that an LLM can identify teaching units directly from division-level text:
- Q1 PASS: Sensible boundaries in 10/10 divisions across nahw, fiqh, usul, balagha, hadith
- Q2: Two-phase (classify then group) beats single-phase in 10/10 divisions
- Q3: Cross-boundary context showed no measurable benefit; D-011 stays hard
- Full results: `EVALUATION_WORKBOOK.md`

### 2. Division Size Analysis — Full Shamela Collection (2,065,297 divisions, 17,155 books)

Validated that the vast majority of divisions need no splitting:

| Metric | Value |
|--------|-------|
| Total divisions analyzed | 2,065,297 |
| ≤ 2000w (no split needed) | 96.8% |
| ≤ 5000w (no split needed) | 99.1% |
| < 50w (need merging) | 29.1% |
| 2001-5000w (need structural split) | 2.3% |
| > 5000w (likely heading detection failures) | 0.9% |

Key finding: the 0.9% of divisions > 5000 words includes monsters of 100K-200K+ words (entire dictionary letters, full surah tafsir commentaries under one heading). These are artifacts of Shamela's sparse headings, not real divisions. The normalization engine's structure discovery produces finer divisions.

The raw Shamela analysis is a WORST CASE: the normalization engine will produce fewer tiny fragments (reducing the 29.1%) and fewer oversized divisions (reducing the 3.2%). If 96.8% holds at raw Shamela level, it will be higher after normalization.

### 3. Passaging Engine Complexity Analysis

The core passaging logic — already prototyped in `extract_divisions.py` (463 lines) — handles cross-page assembly, word counting, heading alignment, text layer rebasing, content flag aggregation. Under the simplified Architecture C (which already removed §4.B), the remaining passaging work is:

| Action | % of divisions | Complexity |
|--------|---------------|------------|
| Pass-through | 67.7% | Zero work |
| Merge tiny neighbors | 29.1% | ~30 lines |
| Split at structural markers | 3.2% | ~200 lines |

Total: ~500-800 lines of deterministic, unit-testable code. Not engine-worthy.

## Why Not a Separate Passaging Engine

An engine in KR requires: SPEC design (2-4 sessions), build (3-6 sessions), code audit (1 session), evaluation (4-8 sessions), hardening (2-4 sessions) = 12-23 sessions. This cost buys:

- An additional contract boundary (each boundary is a corruption point — 5 defects found at source→normalization)
- Independent testability of passaging (achieved equally by internal module separation)
- Separation of deterministic/LLM concerns (achieved equally by internal module separation)

It does NOT buy better knowledge quality. The splitting algorithm is identical whether in a separate engine or an internal module. The knowledge integrity threats (T-1 through T-7) are equally defended in both architectures. No steelman argument for a separate passaging engine shows it produces better knowledge.

The asymmetric risk: if absorbing passaging into excerpting fails on some edge case, we add a splitting function — cost: days. If we built a separate engine unnecessarily, cost: 1-2 months and a permanent contract boundary.

## Why Keep Taxonomy and Synthesis Separate

- Different corruption threats: T-3 (taxonomic misplacement) vs T-5 (synthesis hallucination)
- Different processing modes: taxonomy is partially deterministic; synthesis is fully LLM
- Different lifecycles: taxonomy builds incrementally; synthesis regenerates
- Zero evidence for merging: the experiment tested neither
- Lifecycle coupling (place → synthesize → discover misplacement → relocate) is handled through cross-engine coordination, not merging

## The Excerpting Engine Internal Architecture

Three cleanly separated phases:

**Phase 1 — Deterministic Preprocessing (absorbs passaging):**
- Cross-page text assembly using boundary_continuity signals
- Division-to-chunk mapping: ≤ 5000w → process directly; > 5000w → split at structural markers
- Tiny division merging: < 50w → join with adjacent sibling
- Format-specific handling: verse/commentary alignment, Q&A pair detection, مسألة blocks
- Metadata assembly: division path, text layers, content flags, footnotes
- CRLF normalization (owner is on Windows)
- Independently unit-testable, ~800 lines estimated

**Phase 2 — LLM Teaching Unit Extraction (validated by experiment):**
- Phase 2a (classify): LLM classifies segments by scholarly function
- Phase 2b (group): LLM groups into teaching units, evaluates self-containment
- Two-phase approach validated: B ≥ A in 10/10 experiment divisions
- Multi-model consensus on all classification decisions
- D-011 enforced: teaching units cannot span division/chunk boundaries

**Phase 3 — Metadata Enrichment:**
- Author attribution, school classification, topic proposal
- Cross-reference detection, hadith identification
- Consensus and human gates per reference/KNOWLEDGE_INTEGRITY.md

## Empirical Unknowns (Must Test During Excerpting Engine Evaluation)

1. **LLM performance on 2000-5000 word divisions.** Experiment maximum was 1040w. Need targeted tests.
2. **Format-specific handling.** All 10 experiment divisions were prose. Need verse, QA, commentary tests.
3. **Division structures in المغني-class works.** Experiment used small books. Need multi-volume tests.
4. **Books with empty/minimal division trees.** Not encountered in experiment. Need fallback tests.

These unknowns affect MODULE design, not architecture. They are flagged for the excerpting engine evaluation plan.

## Revision History

- **v1 (premature):** Committed Architecture C (4 remaining engines, separate passaging) after 10-division experiment. Did not challenge whether passaging needed to be a separate engine.
- **v2 (this version):** Deep adversarial review revealed passaging is not engine-worthy. Full-scale Shamela analysis (2M divisions, 17K books) confirmed 96.8% of divisions need no splitting. Architecture revised to 3 remaining engines with passaging absorbed into excerpting.
