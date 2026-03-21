# NEXT — Normalization Engine Transition Gate

## Current Position

- **Phase:** Step 3 → Step 5 transition (Evaluate → Prove Complete) from `reference/ENGINE_BUILD_BLUEPRINT.md`
- **Previous:** Evaluation **GO** (this session). All 4 layers passed. Zero CORE GAPs, zero ENGINE BUGs. SPEC errata (SPEC-NOTE-1 through SPEC-NOTE-3) resolved.
- **Engine state:** 420 tests passing (14 skipped), 37/51 ADV, L-001–L-012 documented. SPEC.md updated with errata fixes.

## What to Do

**Run the transition gate in a NEW session** (context degradation rules apply — do NOT gate in the same session that produced the evaluation).

### Transition Gate Procedure

1. **Skill:** `use kr-gating-transitions`
2. **Read:** `reference/protocols/QUALITY_AXIOM.md`, then `reference/ENGINE_BUILD_BLUEPRINT.md` §3 completion criteria
3. **Verify prerequisites with tool calls** (not memory):
   - [ ] Layer 1 programmatic checks run on ALL 63 fixtures → `engines/normalization/eval_layer1_results.json`
   - [ ] Layer 2 pattern analysis covers all 12 limitations → `engines/normalization/EVALUATION_REPORT.md` Layer 2
   - [ ] Layer 3 manual inspection on 5 diverse fixtures → `engines/normalization/EVALUATION_REPORT.md` Layer 3
   - [ ] Layer 4 GO verdict supported by evidence → `engines/normalization/EVALUATION_REPORT.md` Layer 4
   - [ ] SPEC errata resolved → `reference/SPEC_ERRATA.md` (all 3 RESOLVED)
   - [ ] LESSONS.md written → `engines/normalization/LESSONS.md`
   - [ ] All tests still pass → `pytest engines/normalization/tests/ -q`
   - [ ] Contract alignment with passaging verified → Evaluation Layer 2, all 12 limitations assessed
4. **Adversarial round** (R2): worst-case trace, missing-test check, "what could still be wrong?"
5. **Verdict:** APPROVED (all prerequisites met) or BLOCKED (any prerequisite unmet)

### After Gate Approval

Update NEXT.md to point to passaging engine SPEC design:
- Read `engines/passaging/SPEC.md` (existing draft)
- Read `engines/normalization/LESSONS.md` (recommendations for passaging)
- Begin Step 1 (SPEC Design) for the passaging engine per ENGINE_BUILD_BLUEPRINT.md

### Owner Action Needed

Start a new chat for the transition gate. The architect handles everything — the owner just provides the new session.

## Context

### Evaluation Summary

| Layer | Scope | Verdict |
|-------|-------|---------|
| 1: Programmatic | 63 fixtures, zero fatals | PASS |
| 2: Pattern analysis | L-001 through L-012, all assessed | PASS (0 BLOCKING) |
| 3: Manual inspection | 5 diverse fixtures, Arabic text printed | PASS (1 LESSON LEARNED) |
| 4: GO/NO-GO | All criteria met | **GO** |

### Findings (4 total, all non-blocking)

| # | Finding | Category |
|---|---------|----------|
| F-1 | ext_50 auto-upgrade false positive on bracket-heavy text | LESSON LEARNED |
| F-2 | 03_fiqh L-003 heading chains on TOC page | LESSON LEARNED |
| F-3 | 5/63 fixtures have division overlap warnings (L-010) | LESSON LEARNED |
| F-4 | ext_41 identical character run warnings | LESSON LEARNED |

### Post-Protocol Adversarial Findings (5 monitoring items)

1. Real multi-layer texts beyond ibn_aqil untested → spot-check first full-collection run
2. Plain text normalizer untested on real data → spot-check if encountered
3. Very large texts (>1000 pages) untested → monitor first large-text run
4. CRLF on actual Windows data untested → verify during deterministic sweep
5. Footnote renumbering with bare-number pages → very low risk, passaging fallback handles it
