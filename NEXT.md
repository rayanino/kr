# NEXT — Excerpting Engine Complete → Taxonomy Engine

## Current Position

- **Source Engine:** COMPLETE. 566 tests, 0 failures. Transition gate approved.
- **Normalization Engine:** COMPLETE. 503 tests, 0 failures. Transition gate approved.
- **Excerpting Engine:** COMPLETE. 519 tests, 0 failures. All 3 phases built + orchestrator + integration.

## Excerpting Summary

| Phase | Module | Tests | Lines |
|-------|--------|-------|-------|
| 1 — Deterministic Assembly | `phase1_assembly.py` | 117 | ~1,531 |
| 2 — LLM Classification + Grouping | `phase2_classify.py`, `phase2_group.py` | 141 | ~854 |
| 3.1 — Deterministic Metadata | `phase3_deterministic.py` | 86 | ~637 |
| 3.2 — LLM Enrichment | `phase3_enrichment.py` | 27 | ~300 |
| 3.3 — Consensus Verification | `phase3_consensus.py` | 33 | ~450 |
| 3.4 — Validation + Writer | `phase3_validation.py`, `writer.py` | 50 | ~350 |
| Orchestrator + Integration | `phase3_orchestrator.py`, `pipeline.py` | 25+ | ~300 |
| Hardening (overnight) | various | 40+ | — |
| **Total** | | **519** | **~4,850** |

## What to Do Next

The excerpting engine needs its **transition gate review** before moving to the Taxonomy engine. This includes:

1. **Cross-engine boundary validation** — verify normalization output → excerpting input contract alignment
2. **Run quality gate:** `python3 scripts/quality-gate excerpting` (if available)
3. **Update pipeline progress** in CLAUDE.md and memory

After transition gate approval, begin Taxonomy engine SPEC design.

## Pipeline Progress

```
Source ✅ → Normalization ✅ → Excerpting ✅ (pending gate) → Taxonomy → Synthesis
```
