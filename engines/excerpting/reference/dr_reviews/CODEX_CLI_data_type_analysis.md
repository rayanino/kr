# Codex CLI — Data Type Analysis for Owner Feedback Collection

**Source:** Codex CLI (`codex exec`) — schema validation, structural analysis
**Date:** 2026-04-07
**Scope:** Analyzed bundle schemas (G1-G4, SC1-SC2, F1-F8), SPEC requirements, pipeline contracts.py files, and TEAM_TRANSLATION_GUIDE.md to find unmet data dependencies.

---

## A. DATA_TYPES_NEEDED

1. **DT-01: User model / study workflow expectations** — Engine(s): all. Explicit owner study-use model that downstream engines should optimize for when deciding what is useful enough to preserve or surface. Status: PARTIAL. Evidence: TEAM_TRANSLATION_GUIDE.md#L17, NEXT.md#L53.

2. **DT-02: Quality rubric + conflict priority order** — Engine(s): excerpting, taxonomy, synthesis. Explicit hierarchy among fidelity, self-containment, granularity, and study value, plus the owner's accept/reject floor for excerpts. Status: PARTIAL. Evidence: TEAM_TRANSLATION_GUIDE.md#L18, L46, SPEC.md#L58.

3. **DT-03: Granularity + packaging policy** — Engine(s): excerpting. Owner-calibrated rules for min/max excerpt size, list handling, semantic coupling, and preferred split granularity; these drive teaching-unit boundaries. Status: PARTIAL. Evidence: G1 manifest, TEAM_TRANSLATION_GUIDE.md#L24, contracts.py#L394.

4. **DT-04: Self-containment + context-restoration policy** — Engine(s): excerpting, synthesis. Owner-calibrated rules for when PARTIAL is acceptable, what a sufficient context_hint is, and how backward references / implicit context / author-flow loss should be restored. Status: PARTIAL. Evidence: SC1 manifest, TEAM_TRANSLATION_GUIDE.md#L20, L28, contracts.py#L495.

5. **DT-05: Evidence vs ruling packaging policy** — Engine(s): excerpting, synthesis. Owner choices on per-ayah/per-proof splitting, evidence-ruling coupling, and multi-type evidence organization. Status: MISSING. Evidence: TEAM_TRANSLATION_GUIDE.md#L34, L36, SPEC.md#L46.

6. **DT-06: Khilaf / tarjih separation policy** — Engine(s): excerpting, taxonomy, synthesis. Owner rulings on short-vs-long dispute splitting, linking between positions, and whether tarjih stands separately from neutral khilaf mapping. Status: MISSING. Evidence: TEAM_TRANSLATION_GUIDE.md#L37, NEXT.md#L86, SPEC.md#L48.

7. **DT-07: Genre + layer special-case policy** — Engine(s): source, normalization, excerpting. Owner decisions on per-genre behavior and multi-layer packaging, including nahw shawahid, editor notes, and whether sharh+matn stay together or separate for study. Status: MISSING. Evidence: TEAM_TRANSLATION_GUIDE.md#L40, L42, source/contracts.py#L773, normalization/contracts.py#L675.

8. **DT-08: Study-readiness calibration** — Engine(s): excerpting, synthesis. Owner-labeled boundary between merely acceptable excerpts and directly study-ready excerpts; currently conflated inside FULL (FP-18). Status: MISSING. Evidence: SPEC.md#L69, contracts.py#L66.

9. **DT-09: Metadata + study-surface visibility policy** — Engine(s): excerpting, taxonomy, synthesis. Owner-required metadata surface and which flagged outputs must stay off the default study surface (FP-21). Status: PARTIAL. Evidence: TEAM_TRANSLATION_GUIDE.md#L45, SPEC.md#L81.

10. **DT-10: Upstream source policy** — Engine(s): source, downstream all. Owner-only rulings for flagged-source overrides, owner-authored source typing, and explicit exceptions to collection-wide assumptions. Status: PARTIAL. Evidence: source/contracts.py#L74, L632, L836.

11. **DT-11: Human-gate adjudication rubrics + case records** — Engine(s): source, excerpting. Owner decision data for unresolved author/work/school conflicts and DEPENDENT-excerpt disposition when consensus cannot settle the case. Status: MISSING. Evidence: source/contracts.py#L266, SPEC.md#L2011, L2013.

## B. PER_TYPE_DETAIL

| DT | Min Records | Difficulty | Why | Dependencies |
|----|------------|-----------|-----|-------------|
| DT-01 | 1 canonical user-model | NON_TEDIOUS | Owner answer family exists, not yet a durable artifact | None |
| DT-02 | 2 global policy records | NON_TEDIOUS | Finite policy choice, not a large exemplar set | DT-01 |
| DT-03 | 5 policy records (G-1..G-4, CJ-1) | TEDIOUS | G1 bundle = 8 decision steps, 52 explicit items, 8 nonnegotiables, 9 red-team tests | DT-01, DT-02 |
| DT-04 | 4 policy records (F-5, SC-1..SC-3) | TEDIOUS | SC1 bundle = 8 decision steps, 74 explicit items, 10 nonnegotiables, 9 red-team tests | DT-01, DT-02, DT-03 |
| DT-05 | 3 policy records (E-1..E-3) | NON_TEDIOUS | Discrete unresolved choices already named in translation guide | DT-02, DT-03, DT-04 |
| DT-06 | 3 policy records (K-1..K-3) | NON_TEDIOUS | Narrow space, explicitly enumerated in SPEC/guide | DT-02, DT-03, DT-04 |
| DT-07 | 4 policy records (GN-1..GN-2, L-1..L-2) | NON_TEDIOUS | Bounded rule choices, not broad canon-building | DT-02, DT-03, DT-04 |
| DT-08 | >=30 labeled calibration judgments | TEDIOUS | FP-18 says boundary not yet calibrated, needs empirical data | DT-01..04, DT-07 |
| DT-09 | 3 policy records | NON_TEDIOUS | Short policy surface even though FP-21 unmapped | DT-01, DT-02, DT-08 |
| DT-10 | 3 policy records | NON_TEDIOUS | Fields exist in contracts but owner policy behind them does not | DT-01 |
| DT-11 | 6 rubric records + 1/gate | TEDIOUS | Accumulates across real ambiguous sources, no single global answer | DT-02, DT-04, DT-06, DT-07, DT-10 |

## C. COLLECTION_ORDER

1. DT-01 → 2. DT-02 → 3. DT-10 (parallel with DT-02) → 4. DT-03 → 5. DT-04 → 6. DT-05 → 7. DT-06 → 8. DT-07 → 9. DT-08 → 10. DT-09 → 11. DT-11

## D. GAPS

- **TEAM_TRANSLATION_GUIDE.md does not map FP-13 through FP-22.** Pre-hardening guide.
- **No questionnaire captures:** FP-18 study-readiness, FP-19 extraction spans, FP-21 flag budget/severity, FP-22 anti-covert-excerpter, FP-15 rhetorical posture, FP-16 nesting-depth, FP-17 hub-and-spoke, human-gate rubrics.
- **FP operationalization verdict:** Only **FP-8** (khilaf/tarjih, deferred to K-1/K-2/K-3) and **FP-18** (study-readiness, deferred to 30-book probe) need owner calibration. Rest are implementable.

## E. TEDIOUS_VS_SUMMER

- **Collect now (TEDIOUS):** DT-03, DT-04, DT-08, DT-11
- **Defer to summer (NON_TEDIOUS):** DT-01, DT-02, DT-05, DT-06, DT-07, DT-09, DT-10
