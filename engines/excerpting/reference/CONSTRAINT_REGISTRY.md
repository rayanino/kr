# Excerpting Engine — Constraint Registry

> **Purpose:** Every numeric threshold in the engine is documented here with its origin, calibration status, and risk level. New thresholds without a registry entry are not constraints — they are unvalidated assumptions.
>
> **Rule:** Before treating ANY number as a constraint, trace it here. If it's not in this registry, it has no authority.
>
> **Created:** 2026-04-07, Session 9 foundation integrity audit (3-coworker investigation after phantom 1500-word cap incident)

## HIGH Risk (quality-impacting, action required)

| ID | Constraint | Value | Location | Origin | Calibration | Action |
|----|-----------|-------|----------|--------|-------------|--------|
| CR-1 | MAX_TOKENS >4000 words | 32768 (provisional) | phase2_classify.py:147 | Code comment: "untested" | UNCALIBRATED | Test during 30-book probe |
| CR-2 | GROUP_MAX_TOKENS | Dynamic (8192/16384/32768) | phase2_group.py:_compute_group_max_tokens | Session 9: matched to CLASSIFY/ENRICH pattern | PARTIALLY CALIBRATED (largest validated: 41 units at 3111 words) | Validate >4000 word chunks |
| CR-3 | VERIFY_MAX_TOKENS | 8192 | contracts.py:823 | No documented rationale | UNCALIBRATED | Justify or scale dynamically |
| CR-4 | ~~Consensus text preview~~ | ~~1500 chars~~ → FULL | phase3_consensus.py:136,155,173 | ~~Undocumented~~ → **FIXED Session 9: sends full text** | N/A (removed) | RESOLVED |
| CR-5 | text_snippet validation | 80 characters | contracts.py:406 | Experiment design | KNOWN ISSUE (DR-29: Unicode codepoint vs grapheme) | Redesign before probe |
| CR-6 | excerpt_topic cardinality | 1-3 keywords | contracts.py:516 | Design choice, no corpus analysis | UNCALIBRATED | Corpus analysis during probe |
| CR-7 | PARTIAL/DEPENDENT boundary | C-SC-1..5 criteria | SPEC §3 | Owner defers to 30-book probe | UNCALIBRATED | Calibrate with adversarial examples |

## MEDIUM Risk (unclear basis or single-source calibration)

| ID | Constraint | Value | Location | Origin | Calibration |
|----|-----------|-------|----------|--------|-------------|
| CR-8 | TINY_DIVISION_WORDS | 50 | contracts.py:803 | Shamela corpus: 29.1% of divisions | CALIBRATED (corpus) |
| CR-9 | OVERSIZED_DIVISION_WORDS | 5000 | contracts.py:804 | Shamela corpus: 0.9% of divisions | CALIBRATED (corpus) |
| CR-10 | Heading alignment | 30 chars in 200 | SPEC §4.3 | Experiment: 40-60% rejection at 15/100, relaxed | PARTIALLY (marked "may be calibrated") |
| CR-11 | LA-1 layer dominance | 80% | SPEC §6.2, contracts.py:110 | Design: "conservative, requires clear dominance" | DESIGN CHOICE (allows per-source override to 70%) |
| CR-12 | LA-3 uncertainty | <60% dominant | SPEC §6.2 | Design choice | UNCALIBRATED (gap between 60-80% is arbitrary) |
| CR-13 | CLASSIFY_TIMEOUT | 900s | contracts.py:813 | Smoke test: 88s baseline, 10.2x safety | CALIBRATED (single test) |
| CR-14 | GROUP_TIMEOUT | 900s | contracts.py:814 | Same as CLASSIFY | CALIBRATED (single test) |
| CR-15 | VERIFY_TIMEOUT | 600s | contracts.py:816 | "Calibrated from CLI timings" | PARTIALLY (lower than LLM phases, undocumented why) |
| CR-16 | description_arabic | 5-35 words | SPEC §5.3.2 | Experiment: 10-30, relaxed per §2.3 | CALIBRATED (experiment) |
| CR-17 | Forgiving retention | 15% / ~30 words | SPEC FP-3, prompt | Session 2 hardening, linguistic reasoning | UNCALIBRATED (reasonable heuristic) |
| CR-18 | Sub-item grouping | 20 words | SPEC §5.3.2, prompt | Design rule | UNCALIBRATED (round number) |
| CR-19 | School confidence | 0.67 for 2-of-3 | contracts.py:509 | Mathematical (2/3) | DERIVED (not arbitrary) |
| CR-20 | CLASSIFY MAX_TOKENS ≤1500w | 8192 | phase2_classify.py:155 | ibn_aqil_v3 single chunk test | SINGLE-SOURCE |
| CR-21 | CLASSIFY MAX_TOKENS >1500w | 32768 | phase2_classify.py:153 | Same single chunk test | SINGLE-SOURCE |
| CR-22 | ENRICH MAX_TOKENS ≤1500w | 16384 | phase3_enrichment.py:50 | ibn_aqil_v3: 14863 tokens at 91% utilization | SINGLE-SOURCE (tight margin) |

## LOW Risk (well-justified or deterministic)

| ID | Constraint | Value | Location | Origin |
|----|-----------|-------|----------|--------|
| CR-23 | RETRY_COUNT | 2 | contracts.py:811 | Design choice (3 total attempts) |
| CR-24 | Temperature | 0.0 | contracts.py:809 | Determinism requirement (rules) |
| CR-25 | CONCURRENCY | 1 | contracts.py:832 | Safety/observability |
| CR-26 | ENRICH_TIMEOUT | 900s | contracts.py:815 | Calibrated from CLI timings |
| CR-27 | ESCALATION_TIMEOUT | 300s | contracts.py:817 | Design (shorter for tiebreaker) |
| CR-28 | Cross-reference demotion | 30 words | SPEC §5.4.3 | DR evaluation (TU-6 graded 1/5) |
| CR-29 | MV-1 sub-viable merge floor | 25 words | SPEC §5.5.5, phase3_deterministic.py:_MV1_WORD_FLOOR | DR consensus (ChatGPT 2/5 + Claude 1/5 on 5-word TU-5). Implemented Session 18. CAVEAT: isnad chains (7-12 words) are exempt via _ISNAD_MARKERS. Hadith collections may need corpus-specific calibration — 15-20 word isnads are legitimate standalone units (arabic-auditor finding 2026-04-08). |
| CR-30-38 | Layer validation, coverage invariants, gate policies | Various | contracts.py, SPEC §5.4 | Deterministic rules |

## REMOVED Constraints

| Constraint | Former Value | Removed | Reason |
|-----------|-------------|---------|--------|
| ~~Prompt word cap~~ | ~~1500 words~~ | Session 9 | **Phantom constraint.** Never formally decided. Emerged from informal note "1484/1500". Drove quality-losing 45% compression. Owner challenged. Removed permanently. |
| ~~Consensus text truncation~~ | ~~1500 chars~~ | Session 9 | Arbitrary truncation hid late evidence from verifier. Full text now sent. |

## Arabic Scholarly Constraints (PRELIMINARY — Gemini CLI audit, needs 2nd coworker)

8 of 10 Arabic-specific lists found UNSOUND by Gemini CLI. Findings are PRELIMINARY per no-single-model-conclusion rule. Full details logged in dispatch_log.jsonl (2026-04-07). Key gaps:
- Causal particle list: missing لما, حيث إن, بسبب, وعليه, ومن ثم
- Semantic dependency terms: missing الغاية, الصفة, البدل
- Verdict/tarjih terms: missing school-specific (المفتى به, الأظهر, ما به العمل)
- Q&A formulas: missing إن قلتَ/قلتُ, أورد/دفع, قوله/أقول
- Resolution: Deferred to DR28 (prompt architecture) — determines whether these go in prompt, reference document, or dynamic loading
