# Step 2 LLM Inference Testing — Final Summary

**Date:** 2026-03-09
**Prompt version:** inference_v1.py draft-3 (unchanged — passed all targets on first iteration)

## Phase 1: Prompt Engineering (Sonnet 4.6)

| Metric | Target | Result |
|--------|--------|--------|
| JSON parse rate | >=95% | **100%** (13/13) |
| Enum violations | 0 | **0** |
| Multi-layer accuracy | >=85% | **100%** (13/13) |
| Model aggregate | — | 0.748 |

**Iterations needed:** 0 (passed on first run)

## Phase 2: Multi-Model Accuracy

**Original scores (string-similarity name matching):**

| Model | Provider | Parse | Enum | Aggregate | Multi-layer | Eligible |
|-------|----------|-------|------|-----------|-------------|----------|
| Opus 4.6 | Anthropic | 100% | 0 | 0.796 | 100% | YES |
| GPT-5.4 | OpenAI/OR | 100% | 0 | 0.786 | 100% | YES |
| Command A | Cohere/OR | 100% | 0 | 0.786 | 100% | YES |
| Mistral Large | Mistral/OR | 100% | 0 | 0.759 | 100% | YES |
| Gemini 3.1 Pro | Google/OR | 92% | 0 | 0.727 | 100% | YES* |

**Corrected scores (token-based semantic name matching, 2026-03-09):**

| Model | Provider | Parse | Enum | Aggregate | Multi-layer | Eligible |
|-------|----------|-------|------|-----------|-------------|----------|
| Opus 4.6 | Anthropic | 100% | 0 | **0.890** | 100% | YES |
| Command A | Cohere/OR | 100% | 0 | **0.883** | 100% | YES |
| GPT-5.4 | OpenAI/OR | 100% | 0 | **0.873** | 100% | YES |
| Mistral Large | Mistral/OR | 100% | 0 | **0.863** | 100% | YES |
| Gemini 3.1 Pro | Google/OR | 92% | 0 | **0.788** | 100% | YES* |

*Gemini: 1 timeout on alfiyyah_versified (network, not format issue). max_tokens increased from 2000 to 4000 fixed all other parse failures.

**Scoring fix:** The original `normalized_name_similarity()` used `difflib.SequenceMatcher` which penalized correct identifications when models used different name forms (e.g., "النووي" vs "يحيى بن شرف النووي"). Replaced with token-based component overlap that correctly handles Arabic scholarly name abbreviation patterns. Also enhanced `person_score`: exact death date match + any name component overlap → 1.0 (certainly same person). All models correctly identify the right scholar — the aggregate increase reflects corrected scoring, not changed predictions.

## Phase 3: Consensus Pair Selection

### Top pairs (all cross-provider, target: >=90% "at least one right")

| Pair | >=1 Right | Complementarity | Both Right |
|------|----------|-----------------|------------|
| **Gemini 3.1 + Command A** | **92.3%** | **24.2%** | 68.1% |
| **Command A + Opus 4.6** | **92.3%** | 15.4% | 76.9% |
| Mistral + Command A | 91.2% | 18.7% | 72.5% |
| Gemini 3.1 + Mistral | 90.1% | 20.9% | 69.2% |
| Mistral + Opus 4.6 | 90.1% | 12.1% | 78.0% |

### Selected pair: Command A + Opus 4.6

**Rationale:**
1. Tied at 92.3% "at least one right" — exceeds 90% target
2. Both models have 100% JSON parse rate (Gemini had 92%)
3. Higher "both right" rate (76.9% vs 68.1%) — fewer human review triggers in production
4. Reliability > complementarity for a production scholarly library

**Alternative:** Gemini 3.1 + Command A for maximum diversity (24.2% complementarity), if Gemini timeout issue is resolved with longer timeouts.

## Assumptions Resolved

- **A1 (JSON reliability):** VALIDATED. 100% parse rate on 4/5 models, 92% on Gemini (timeout). Prompt draft-3 works without any split.
- **A2 (multi-layer detection):** VALIDATED. 100% accuracy across all 5 models on all 13 fixtures.
- **A5 (consensus pair):** VALIDATED. Command A + Opus 4.6 achieves 92.3% "at least one right".

## Test runner fixes applied

1. Windows encoding: added `encoding='utf-8'` to file opens, UTF-8 stdout wrapper
2. max_tokens: increased from 2000 to 4000 (Gemini needs more for scholarly_context)
3. Error display: handle parse-error fixtures in per-fixture score printing

## Files produced

- `tests/results/phase1_20260309_181643.json` — Sonnet 4.6 results
- `tests/results/phase2_20260309_18*.json` — Per-model Phase 2 results (5 files)
- `tests/results/phase3_consensus.json` — Pair analysis and selection
- `tests/consensus_analysis.py` — Reusable consensus pair computation script
