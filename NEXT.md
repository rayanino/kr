# NEXT — Source Engine Validation, Step 1: Code Audit

**Governing document:** `engines/source/VALIDATION_PLAN.md` — read this first in every new session.

**Previous step:** Step 0 COMPLETE — 12/13 fixtures pass. See `engines/source/review/STEP0_RESULTS.md` for findings.

**Current step:** Step 1 — Code Audit (Phase B). Claude Chat reads each module against the SPEC.

**What to do:** This is a Claude Chat session (not Claude Code). The architect reads each module against `SPEC_CORE.md` and traces the 6 checklist items from the validation plan, plus 4 additional bugs found in Step 0.

**Checklist (from VALIDATION_PLAN.md Step 1 + Step 0 findings):**

1. **Consensus retry flow.** Trace engine.py → metadata_inference.py → consensus.py. Does the fallback model (GPT-5.4) actually get called when both primaries fail?
2. **Registration atomicity.** What if `.bak` is also corrupt? (Step 0 finding A2: silent `pass` on double corruption.)
3. **Concurrent scholar updates.** `lookup_or_register_author` lacks file locking. (Step 0 finding A3.)
4. **Human gate auto-approve.** Does `auto_approve=True` use the same code path as real owner review?
5. **Validation check ordering.** Does Check 5e propagate before Check 6 runs? (Bug was found and fixed in Session 6 — verify the fix is complete.)
6. **Trust re-evaluation gating.** Document the extension hook for Stage 2.
7. **[NEW] Validation gate-severity errors ignored.** (Step 0 finding A1.) Engine.py only handles `severity="fatal"`, ignoring `severity="gate"` errors that should create human gate checkpoints.
8. **[NEW] Name matching punctuation bug.** (Step 0 finding A4.) `normalize_arabic_name` doesn't strip Arabic commas (،), causing token mismatches in scholar deduplication.
9. **[NEW] `validate_enrichment_passthrough` imported but never called.** D-023 passthrough validation is imported in validation.py but not wired into any check.
10. **[NEW] Integration script `level` field and author comparison.** Already fixed in commit 3d18faf. Verify correctness.

**Deliverable:** `engines/source/review/CODE_AUDIT_SESSION6.md`

**GO/NO-GO:** All findings fixed or documented as deferred-to-Stage-2 with clear rationale.

**After Step 1:** Claude Code session to implement fixes. Then Step 2 (deterministic sweep on 2,519 books).
