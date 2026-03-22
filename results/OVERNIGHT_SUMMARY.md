# Overnight Work Summary

**Date:** 2026-03-22
**Duration:** Phases 0-1 overnight, Phases 2-5 morning continuation
**Cost:** 0 EUR (all deterministic work)

---

## Phases Completed

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 0 | COMPLETE | Baseline smoke test (norm 425+14skip, source 513) |
| Phase 1 | COMPLETE | 10 edge-case fixtures + 59 regression tests |
| Phase 2 | COMPLETE | Cross-engine validation on 70 Phase E books |
| Phase 3 | COMPLETE | Deep analysis scripts (gate aborts, consensus, field coverage) |
| Phase 4 | COMPLETE | Source engine completion report + normalization transition data |
| Phase 5 | COMPLETE | Contract boundary tests (39 new tests) |

**All 5 phases completed.**

---

## Test Counts

| Engine | Before | After | Delta |
|--------|--------|-------|-------|
| Normalization | 425 passed, 14 skipped | 470 passed, 14 skipped | +45 |
| Source | 513 passed | 566 passed | +53 |
| **Total** | **938** | **1,036** | **+98** |

**Zero regressions in either engine.**

---

## Commits

| Hash | Message |
|------|---------|
| `fa09c91` | harden: Add 10 edge-case fixtures + 59 regression tests from weekend sweep |
| `bafb79a` | validate: Cross-engine normalization on 70 Phase E books |
| `89938ed` | analysis: Deep dive on 347 LLM-probed books — gate aborts, consensus, field quality |
| `3c1af83` | report: Source engine completion + normalization transition data |
| `1e64a3a` | harden: Test coverage gap analysis + 39 new contract boundary tests |

---

## Key Findings for Architect (Priority Order)

### 1. Cross-Engine Compatibility: PASS
70/70 Phase E books normalize successfully. 0 crashes. The normalization engine handles every book the source engine processes, regardless of LLM gate status.

### 2. Gate Abort Pattern: Science Scope Mismatch Dominates
67 gate aborts total, 66 (98.5%) from science_scope_mismatch. The gate is working correctly — catching cases where the scholar authority database lacks the inferred science. Consider: should science scope mismatch be a soft gate (warning) rather than hard abort?

### 3. Consensus Disagreements: Author Name is the Key Field
27 disagreements out of 347 books (7.8%). Author name is disputed in ALL 27. Science scope in 13, genre in 7. The multi-model consensus mechanism works — disagreements are caught and flagged.

### 4. Multi-Layer Detection Mismatch (9 books)
9 books where source engine LLM and normalization auto-detection disagree on multi-layer status. These need review to determine which is correct and whether the normalization auto-upgrade threshold needs tuning.

### 5. Division Overlap at 15.4%
1,148 of 7,475 books have division overlap warnings. This is advisory — content is unaffected — but passaging should be aware. See L-010.

### 6. Field Coverage Gap: Edition and Death Date
Extraction produces 0% coverage for `edition`, `muhaqiq`, and `death_date_raw`. These fields rely on LLM inference or manual entry. The extraction regex should be reviewed for missed patterns.

---

## Cross-Engine Validation Results

- 70/70 Phase E books normalize: **100% success**
- 0 crashes (source engine OK + normalization OK)
- 9 multi-layer detection disagreements
- Page loss patterns consistent with corpus baseline
- Gate abort books normalize identically to success books

---

## Analysis Highlights

### Gate Aborts (67 total)
- 66 science_scope_mismatch: LLM inferred science doesn't match scholar's known sciences
- 1 multi-layer validation issue
- Phase C had 70% abort rate (earliest probes, most obscure books)
- Phase D: 0% abort rate (broad selection)
- Phase E: 23% abort rate (edge cases)

### Consensus (27 disagreements)
- Author name: 27/27 (100%) — most contested field
- Science scope: 13/27 (48%)
- Genre: 7/27 (26%)
- Structural format: 4/27 (15%)
- is_multi_layer: 1/27 (4%)

### Field Quality
- Deterministic extraction: title 100%, author 95%, category 100%, publisher 85%
- LLM-only fields: genre, scope, layers, format, authority — all 100% on success books
- Major gap: edition (0%), muhaqiq (0%), death_date_raw (0%) from extraction

---

## Artifacts Produced

| File | Description |
|------|-------------|
| `tests/fixtures/shamela_edge_cases/edge_*.htm` | 10 new edge case fixtures |
| `engines/normalization/tests/test_edge_cases.py` | 27 edge case tests |
| `engines/source/tests/test_edge_cases.py` | 32 edge case tests |
| `engines/normalization/tests/test_contract_boundaries.py` | 18 contract boundary tests |
| `engines/source/tests/test_contract_boundaries.py` | 21 contract boundary tests |
| `results/cross_engine_validation/` | 70-book normalization sweep results |
| `results/CROSS_ENGINE_VALIDATION.md` | Cross-engine compatibility report |
| `results/GATE_ABORT_ANALYSIS.md` | Gate abort deep dive (67 books) |
| `results/CONSENSUS_ANALYSIS.md` | Consensus disagreement analysis (27 books) |
| `results/FIELD_QUALITY_MATRIX.md` | Per-field coverage matrix (347 books) |
| `results/SOURCE_ENGINE_COMPLETION_REPORT.md` | Source engine transition gate report |
| `results/NORMALIZATION_TRANSITION_DATA.md` | Normalization build + corpus data |
| `results/normalization_test_output.txt` | Full test output capture |
| `results/source_test_output.txt` | Full test output capture |
| `scripts/analyze_gate_aborts.py` | Gate abort analysis script |
| `scripts/analyze_consensus.py` | Consensus disagreement analysis script |
| `scripts/analyze_field_coverage.py` | Field coverage matrix script |
| `scripts/analyze_cross_engine.py` | Cross-engine validation analysis script |
| `scripts/create_edge_fixtures.py` | Edge case fixture creation script |
