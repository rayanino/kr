# CC Review Checklist — Excerpting Session 4: Phase 3 LLM Enrichment + Consensus

> **This file is the review artifact.** Fill every checkbox, commit this file, THEN deliver the verdict.  
> An unfilled checklist = an incomplete review. Do NOT deliver a verdict without committing this file.  
> **REVIEW_PROTOCOL.md is the authority — NOT the kr-reviewing-cc-output skill's verdict template.**

## Pre-review
- [x] Repo pulled, commit diff read (`git diff 789d95d9..4a7f71e9`)
- [x] Handoff review doc read (`reference/archive/sessions/handoff_review_session4.md`)
- [x] REVIEW_PROTOCOL.md and QUALITY_AXIOM.md re-read

## Pass 1: Structural
- [x] Every CC-modified file opened and read **in full** (not truncated) — list files:
  - [x] `phase3_enrichment.py` — 5 functions (verified: grep -c "^def " = 5)
  - [x] `phase3_consensus.py` — 14 functions (verified: grep -c "^def " = 14)
  - [x] `test_phase3_enrichment.py` — 27 test functions (verified: grep -c "def test_" = 27)
  - [x] `test_phase3_consensus.py` — 33 test functions (verified: grep -c "def test_" = 33)
  - [x] `test_phase3_deterministic.py` — overnight hardening, not in Session 4 scope
  - **RULE 7 check:** All files read in full. No truncation issues.
- [x] All tests run: 437 passed, 2 skipped, 0 failed
- [x] SPEC cross-reference: enrichment matches §7.2.2–§7.2.5, consensus matches §7.3.1–§7.3.4
- [x] **Cross-engine boundary check:**
  - [x] `contracts.py` was NOT modified in Session 4 — no contract changes
  - [x] No new types introduced — all types pre-existed (EnrichmentResult, VerificationResult, etc.)
  - Modified types: NONE
  - Consumers checked: N/A (no contract changes)

### Pass 1 Findings

**F-1 [HIGH]: FULL→PARTIAL/DEPENDENT consensus downgrade produces invalid ExcerptRecord.**
- `_repair_context_hint()` (line 501) updates context_hint but not self_containment_notes
- FULL excerpts have self_containment_notes=None by I-ER-4
- After model_copy: PARTIAL + notes=None → violates I-ER-4
- Empirically confirmed: model_validate(updated.model_dump()) crashes
- Affects both FULL→PARTIAL and FULL→DEPENDENT paths

**F-2 [MEDIUM]: EX-G-003 over-triggers when verifier agrees with source metadata.**
- `_resolve_school()` line 290: `vi.alternative != excerpt.school` should be `vi.alternative != source_school`
- SPEC §7.3.4: "source_school conflicts with both models"
- Code: triggers when verifier ≠ enrichment, not when verifier ≠ source
- `check_gate_triggers()` (line 575) has same issue — no verifier value check
- Empirically confirmed: source=حنبلي, enrichment=شافعي, verifier=حنبلي → false trigger

**F-3 [MEDIUM]: Chunk matching via startswith false-matches similar div_ids.**
- `run_phase3_enrichment` line 377 and `run_consensus` line 644
- `cid.startswith(exc.div_id)` matches div_1 → div_10_chunk_0
- For split chunks, all excerpts assigned to first matching chunk
- Latent bug — split chunks not yet in pipeline, but will crash when they are

### Additional Observations (NOT findings — no epistemic impact)

- **Tier 1 LLM trustworthiness defenses not implemented.** Expected given Session 4 had no architect handoff. Defenses 1B, 1C, 2A from the defenses doc were mandated for Session 4 but not built. These are quality improvements, not correctness bugs. Defer decision to Round 3.
- **Context hint uses generic string instead of verifier reasoning (F-4 in Round 1 notes).** Low severity — informational loss, not data corruption. Will evaluate in Round 2 whether to elevate.
- System prompt matches §7.2.2 verbatim ✓
- User message template matches §7.2.3 ✓ 
- Provider independence: Anthropic/OpenAI/Cohere ✓
- OpenRouter routing: model strings use OpenRouter format ✓
- Retry logic: 1 + RETRY_COUNT attempts ✓
- Failure degradation: llm_enrichment_failed flag set, deterministic fields survive ✓

**→ End of Pass 1. Fix directive written in NEXT.md. CC will fix F-1, F-2, F-3.**
**→ Round 2 (adversarial) and Round 3 (verdict) will be done in a NEW CHAT after CC fixes.**

## Pass 2: Adversarial
_To be completed in new chat after CC fixes F-1, F-2, F-3._

## Pass 3: Self-verification (RULES 6-7)
_To be completed in new chat after Pass 2._

## Findings

| # | File | Finding | Fix | Fixed? |
|---|------|---------|-----|--------|
| F-1 | phase3_consensus.py:501 | FULL→PARTIAL/DEPENDENT crash: missing self_containment_notes | _repair_context_hint must set notes on downgrade | [ ] |
| F-2 | phase3_consensus.py:290,575 | EX-G-003 over-triggers: wrong condition (verifier≠enrichment instead of verifier≠source) | Fix condition in _resolve_school and check_gate_triggers | [ ] |
| F-3 | phase3_enrichment.py:377, phase3_consensus.py:644 | startswith chunk matching false-matches similar div_ids | Replace with exact match + split format fallback | [ ] |

## Fixes committed
- [ ] ALL findings above have `Fixed? [x]`
- [ ] Fix commits pushed to repo
- [ ] Tests re-run after fixes: `[N] passed`

## Verdict
_Pending Round 2 and Round 3 in new chat after fixes._

**Verdict: BLOCKED (awaiting fixes)**

## Build metrics (cumulative)
```
Implementation: ~3,745 lines (+~1,209 this session — enrichment 442 + consensus 767)
Tests: 437 passing (+60 this session — enrichment 27 + consensus 33)
Test-to-code ratio: ~5 tests per 100 impl lines
SPEC sections implemented: §4 (P1), §5 (P2), §7.1 (P3 det), §7.2 (P3 enrich), §7.3 (P3 consensus)
SPEC sections remaining: §7.4 (validation), §3 (output writer)
```
