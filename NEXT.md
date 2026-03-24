# NEXT — Excerpting Engine: LLM Integration Testing (Round 1)

## Current Position

- **All code complete:** 556 tests (554 passed, 2 skipped), 0 failed
- **PE-1 through PE-6:** ✅ FIXED
- **EX-A-003:** ✅ FIXED (28/28 error codes now wired)
- **Task D (completion assessment):** ✅ DONE — all SPEC checks, error codes, outputs, and exception handling verified
- **LLM Integration Test Protocol:** ✅ WRITTEN — `reference/protocols/LLM_INTEGRATION_TEST_PROTOCOL.md`
- **LLM calls tested with real models:** ❌ ZERO — this is the next step

## What to Do

Follow `reference/protocols/LLM_INTEGRATION_TEST_PROTOCOL.md` exactly.

### Phase A: Select 5 test books

Select 5 books covering the fixture selection matrix dimensions (multi-layer, single-layer, verse-commentary, hadith-heavy, fiqh-with-ikhtilaf, long divisions, short divisions, known fixtures). Document the selection with rationale.

### Phase B: Write and validate the integration run script

CC writes `scripts/run_integration_test.py` per the protocol spec. Save ALL intermediate outputs. Do NOT catch exceptions silently.

### Phase C: Run on first book, review exhaustively

Start with ONE book. Run the full pipeline. Review EVERY excerpt per protocol §C.2. This is the first time we see real LLM output — expect findings.

### Subsequent books

After the first book's findings are triaged and any CRITICAL issues fixed, proceed to books 2-5.

## Read Before Starting

1. `reference/protocols/LLM_INTEGRATION_TEST_PROTOCOL.md` — THE governing protocol
2. `engines/excerpting/SPEC.md` §5 (Phase 2 prompts), §6 (domain rules), §7 (Phase 3 enrichment)
3. `KNOWLEDGE_INTEGRITY.md` — T-1 through T-7 threats
4. `experiments/format_diversity_test/EVALUATION.md` — prior experiment methodology and findings

## Key Reminders

- The owner has ZERO Islamic knowledge. The architect is the sole domain reviewer.
- Round 1 reviews EVERY excerpt. No sampling. No shortcuts.
- Every author/school claim must be web-search verified. Do not trust the LLM's output at face value.
- Decontextualization is the #1 silent failure. Use the boundary-context structural test from protocol Appendix.
- C-7 mitigation: the same model (Opus) produces AND evaluates the output. Use mechanical checks + web search + CC adversarial audit to compensate.
