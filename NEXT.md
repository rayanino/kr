# NEXT — Excerpting Engine Session 6: Phase 3 Orchestrator + Integration

## Current Position

- **Excerpting Phase 1:** COMPLETE. 117 tests (incl. hardening).
- **Excerpting Phase 2:** COMPLETE. 141 tests (incl. hardening).
- **Excerpting Phase 3.1:** COMPLETE. 86 tests, 637 lines. Deterministic metadata assembly.
- **Excerpting Phase 3.2:** COMPLETE. 27 tests, ~300 lines. LLM enrichment.
- **Excerpting Phase 3.3:** COMPLETE. 33 tests, ~450 lines. Consensus verification + human gates.
- **Excerpting Phase 3.4:** COMPLETE. 50 tests, ~350 lines. Validation (V-P3-1–9) + output writer.
- **Test baseline:** 488 tests passing, 0 failures (excerpting)
- **Open SPEC errata:** None

## What to Do

Implement the Phase 3 orchestrator that chains all stages, then run cross-phase integration tests. This completes the excerpting engine.

**Processing flow:**
1. Phase 3 orchestrator: deterministic → enrichment → consensus → validation → writer
2. Integration tests: full pipeline from NormalizedPackage → ExcerptRecord JSONL
3. Cross-engine boundary tests with normalization output

## Context

This is the final session for the excerpting engine. All 4 stages of Phase 3 are implemented and individually tested. Now we need the glue code that chains them together and end-to-end tests proving the full pipeline works.

Key patterns:
- **Orchestrator chains stages in order.** Each stage produces the input for the next.
- **Graceful degradation.** LLM failures degrade to deterministic-only output, not crashes.
- **Gate queue written ONCE after all processing.** V-P3-7 verifies after write.

## Read First

| File | Lines | What |
|------|-------|------|
| `engines/excerpting/SPEC.md` | §7 intro (1800–1830) | Phase 3 overall flow |
| `engines/excerpting/src/phase3_deterministic.py` | all | Stage 1: deterministic metadata |
| `engines/excerpting/src/phase3_enrichment.py` | all | Stage 2: LLM enrichment |
| `engines/excerpting/src/phase3_consensus.py` | all | Stage 3: consensus + gates |
| `engines/excerpting/src/phase3_validation.py` | all | Stage 4: validation checks |
| `engines/excerpting/src/writer.py` | all | Output writer |
| `engines/excerpting/contracts.py` | ExcerptingConfig | Configuration parameters |

## What to Build

### Module 1: `phase3_orchestrator.py`

**Function: `run_phase3(chunks, teaching_units, client, config, source_metadata) → Phase3Result`**
- Chain: deterministic → enrichment → consensus → validation → gate collection
- Handle LLM client being None (deterministic-only mode)
- Collect all gate entries across chunks
- Return validated excerpts + gate entries + error summary

### Module 2: `run_excerpting.py` (top-level orchestrator)

**Function: `run_excerpting(package, config) → ExcerptingResult`**
- Full pipeline: Phase 1 → Phase 2 → Phase 3 → Writer
- Accept NormalizedPackage as input
- Call writer at the end

### Module 3: Integration Tests

**File: `engines/excerpting/tests/test_integration.py`**

1. End-to-end: NormalizedPackage → Phase 1 → Phase 2 (mocked) → Phase 3 → JSONL
2. Deterministic-only mode (no LLM client)
3. Multi-chunk processing
4. Gate queue written and verified
5. Error accumulation across phases

**Expected total: 488 + ≥20 = ≥508 passed tests.**

## Do NOT Do

1. **Do NOT modify Phase 1, Phase 2, or Phase 3 stage code.** Only orchestration.
2. **Do NOT make real LLM calls.** Mock all LLM interactions.
3. **Do NOT modify `contracts.py`** unless you find a bug.

## Verification

1. `python -m pytest engines/excerpting/tests/ -v --tb=short` → **≥508 passed**, 0 failed
2. End-to-end test produces valid `excerpts.jsonl`
3. Gate queue round-trip verified in integration test
4. Deterministic-only mode works without LLM client
