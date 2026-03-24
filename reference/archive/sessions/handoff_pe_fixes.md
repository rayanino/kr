# Handoff — Excerpting Engine: PE-1 through PE-6 Fixes (Task C)

**Date:** 2026-03-24
**From:** Claude Chat (Architect), triage review session
**To:** Claude Chat (Architect), fresh PE-fix session
**Repo state:** commit `3b900c98`, 550 tests passing, 0 failed

---

## What Just Happened

### Triage fixes ACCEPTED
The 14 dual-reviewer audit fixes (commit `619b4ec8`) were reviewed in a full 3-pass cycle. One finding (F-R1: isinstance re-raise list incomplete) was fixed by CC (commit `7751b30d`). Final verdict: ACCEPT. 550 tests passing.

### What remains before the excerpting engine is complete
Six pre-engine-completion items (PE-1 through PE-6), documented since Session 4. All are small, focused fixes — no new architecture. After these, Task D (completion assessment) determines if the engine is ready for the owner's 30-book probe.

---

## Architect Decisions (already made — do not re-derive)

These decisions were made with full context in the current session. The next session should implement them, not revisit them.

### PE-4: alt_id chunk matching fallback → KEEP + DOCUMENT

**Decision:** Keep the defensive fallback. Add DD-PE-4 comment and `logger.warning` when any fallback fires.

**Reasoning:** Phase 1 chunk IDs are deterministic (`div_id` or `div_id_chunk_{chunk_index}` for splits). The alt_id fallback `div_id_{chunk_index}` is a third attempt that catches format mismatches between Phase 1 output and Phase 3 expectations. Removing it would turn a recoverable mismatch into a silent skip (the excerpt goes to `chunk=None`, enrichment is silently skipped). Warning-on-hit is the right balance: it works if needed, and we'll know immediately if it fires.

### PE-5: Pipeline ad-hoc error strings → DOCUMENT as SPEC-NOTE-13

**Decision:** No code changes. Add SPEC-NOTE-13 to SPEC_ERRATA.md explaining that `PHASE2_FATAL`, `PHASE2_SKIPPED`, `PHASE3_FATAL` are pipeline-level operational diagnostics, not SPEC §8.1 error codes.

**Reasoning:** SPEC §8.1 defines per-excerpt error codes (EX-A-*, EX-C-*, EX-M-*, EX-V-*, EX-G-*). Pipeline-level failures don't have per-excerpt scope — they're operational errors affecting the entire source. Creating SPEC error codes for them would blur the distinction between "this excerpt has a problem" and "this source's pipeline run failed." The ad-hoc strings are descriptive, include the exception message, and are already collected in `ExcerptingResult.errors`.

### PE-6: processing_log.jsonl → IMPLEMENT minimal version

**Decision:** Implement `write_processing_log` in writer.py. Single JSONL line per source with: source_id, timestamp, excerpt_count, gate_count, errors list, timings dict, engine_version.

**Reasoning:** SPEC §2.2.1 defines this as an output. Omitting it is a SPEC compliance gap. The implementation is ~20 lines. The log is a debugging convenience — not a downstream contract — so minimal is correct.

---

## PE Items — Full Specification

### PE-1: VerificationResult lacks item_index uniqueness validator

**File:** `engines/excerpting/contracts.py:664`
**What:** `VerificationResult.items` can have duplicate `item_index` values. If the LLM returns two items with `item_index=0`, the consensus logic silently processes the wrong verification for an excerpt.
**Fix:** Add a `@model_validator(mode="after")` to `VerificationResult` that checks `item_index` uniqueness across `items`. Raise `ValueError` if duplicates found.
**Test:** Construct a `VerificationResult` with duplicate `item_index` → `ValidationError`.

### PE-2: resolution_method mislabel for verifier abstention

**File:** `engines/excerpting/src/phase3_consensus.py:370`
**What:** When the verifier abstains (no alternative provided) and escalation produces no majority, `resolution_method="all_3_disagree_gate"` is wrong — it's "2 voted + 1 abstained, no majority." Similarly at line 381, `resolution_method="no_escalation_enrichment_kept"` is used for the no-escalation-client case, which is accurate but could be clearer.
**Fix:** Change line 370 from `"all_3_disagree_gate"` to `"no_majority_gate"`. Leave line 381 as-is (it's accurate).
**Test:** Existing tests should still pass. Add one test: mock verifier with `alternative=None` (abstention) + escalation returns different value → verify `resolution_method="no_majority_gate"`.

### PE-3: Dead _find_majority function

**File:** `engines/excerpting/src/phase3_consensus.py:433`
**What:** `_find_majority` is defined but never called in production code. Only `_find_majority_flexible` is used (line 337). Tests for `_find_majority` exist in `test_phase3_consensus.py:307-312`.
**Fix:** Remove the function. Remove its tests. Remove its import in the test file.
**Test:** Run full suite — no change expected (dead code removal).

### PE-4: Undocumented alt_id chunk matching fallback

**Files:** `engines/excerpting/src/phase3_enrichment.py:386-388`, `engines/excerpting/src/phase3_consensus.py:698-700`
**What:** Three-level chunk ID lookup (div_id → split_id → alt_id) is undocumented.
**Fix:** Add DD-PE-4 comment block above the lookup in both files. Add `logger.warning("DD-PE-4: Using alt_id fallback %s for chunk matching in %s.", alt_id, exc.excerpt_id)` when alt_id fires. Same for split_id fallback — add `logger.info` there too.
**Test:** No new test needed (defensive code that should never fire under normal operation).

### PE-5: Pipeline ad-hoc error strings

**File:** `reference/SPEC_ERRATA.md`
**What:** `PHASE2_FATAL`, `PHASE2_SKIPPED`, `PHASE3_FATAL` are not in SPEC §8.1.
**Fix:** Add SPEC-NOTE-13 documenting these as pipeline-level operational diagnostics.
**Test:** No code changes, no test changes.

### PE-6: processing_log.jsonl not implemented

**Files:** `engines/excerpting/src/writer.py` (new function), `engines/excerpting/src/pipeline.py` (call site)
**What:** SPEC §2.2.1 defines `processing_log.jsonl` but it was never implemented.
**Fix:** Add `write_processing_log(source_id, errors, timings, excerpt_count, gate_count, output_dir)` to writer.py. Call from pipeline.py at the end of `run_excerpting`, after all other processing. Single JSONL line format:
```json
{"source_id": "...", "timestamp": "ISO8601", "excerpt_count": N, "gate_count": N, "errors": [...], "timings": {...}, "engine_version": "0.1.0"}
```
**Test:** Write processing log → read back → verify all fields present and correct.

---

## Task Queue (for next session)

### Task C: CC fixes PE-1 through PE-6
NEXT.md is written with exact specifications. CC implements. Architect does targeted review (same chat is OK for small fixes — no new-chat review cycle needed).

### Task D: Completion assessment
After PE fixes are reviewed, the next-session architect assesses:
1. Are all SPEC §7.4 checks implemented and tested?
2. Are all SPEC §8.1 error codes wired up?
3. Are all SPEC §2.2.1 outputs produced?
4. What is the test-to-code ratio?
5. Are there any remaining silent failure paths?
6. Is the engine ready for the owner's 30-book probe?

### Task E: Owner 30-book probe (NON-NEGOTIABLE)
No engine is complete until the owner has personally reviewed real output on diverse books. This gate cannot be skipped by passing all automated tests.

---

## Session Start Protocol (for next chat)

1. Clone/pull repo
2. Read NEXT.md
3. `git log --oneline -5`
4. Read THIS handoff document
5. Read `reference/protocols/REVIEW_PROTOCOL.md` (for reviewing CC's PE fixes)
6. `ls /mnt/skills/user/` — pick relevant skills
7. Give CC the NEXT.md prompt
8. Review CC output (targeted — same chat OK for these small fixes)
9. If ACCEPT → proceed to Task D
10. If BLOCKED → fix and re-review

---

## Build Metrics

| Metric | Value |
|--------|-------|
| Tests passing | 550 |
| Tests skipped | 2 (Phase 2 LLM integration) |
| Impl lines (4 reviewed files) | 867 |
| SPEC errata | SPEC-NOTE-1 through SPEC-NOTE-12 |
| Known limitations | L-001 through L-012 |
| PE items remaining | 6 (all Open) |
