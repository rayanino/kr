# NEXT — Excerpting Engine: Session 4 ACCEPTED → Triage Session 5/6

## Current Position

- **Phase 1 (Assembly):** ✅ ACCEPTED
- **Phase 2 (Classification + Grouping):** ✅ ACCEPTED
- **Phase 3.1 (Deterministic metadata):** ✅ ACCEPTED
- **Phase 3.2 (LLM enrichment):** ✅ ACCEPTED (Session 4 + 9 fixes)
- **Phase 3.3 (Consensus verification):** ✅ ACCEPTED (Session 4 + 9 fixes)
- **Phase 3.4 (Validation):** ⚠️ EXISTS — CC-authored, NOT reviewed
- **Phase 3 orchestrator:** ⚠️ EXISTS — CC-authored, NOT reviewed
- **Output writer:** ⚠️ EXISTS — CC-authored, NOT reviewed
- **Integration tests:** ⚠️ EXISTS — CC-authored, NOT reviewed
- **Test baseline:** 540 passed, 2 skipped, 0 failed

## What to Do

**Read the handoff document first:**
`reference/archive/sessions/handoff_session4_to_session56_triage.md`

It contains the complete task queue (A through E), CC audit prompts for dual-reviewer, and decision framework for the Session 5/6 triage.

**Immediate task: Task A** — triage CC's unauthorized Session 5/6 implementation. Decide KEEP / REJECT / HYBRID before investing review effort.

## Pre-Engine-Completion Items (tracked from Session 4 R2+R3)

| ID | Description | Status |
|----|------------|--------|
| PE-1 | `VerificationResult` lacks `item_index` uniqueness validator | Open |
| PE-2 | `resolution_method` mislabel for verifier abstention | Open |
| PE-3 | Dead `_find_majority` function | Open |
| PE-4 | Undocumented `alt_id` chunk matching fallback | Open |

These must be fixed before engine completion (Task D), regardless of triage outcome.

## Do NOT Do

- Do NOT accept Session 5/6 work without 3-pass review
- Do NOT fix PE items before the triage decision (scope depends on triage outcome)
- Do NOT start taxonomy engine until excerpting passes Task E (owner 30-book probe)
