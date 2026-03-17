# NEXT — Architect Review of Agent Definitions + SPEC Adversary → Probe 2 Transition Gate

## Current position: All 16 agent definitions written. SPEC adversary run (42 test cases). Pending Architect review.
## What to do: Architect reviews CC output, then runs transition gate for Probe 2.
## Context: Probe 1 found 31 defects in normalization SPEC (22 fixed, CONDITIONAL PASS).
  The 18-agent system is now fully defined. SPEC adversary produced 42 adversarial test
  cases against the normalization SPEC. CC did a self-review (commit 9ea5394) but it was
  minimal (3 lines changed). The Architect should do a thorough independent review.
## Owner action needed: NO — this is an Architect task.

---

## Architect Review Checklist (use kr-reviewing-cc-output)

### New agent definitions to review (7 files):
1. `.claude/agents/build-prober.md` — Red Team: reviews build session diffs vs SPEC
2. `.claude/agents/spec-adversary.md` — Red Team: writes adversarial test cases from SPEC
3. `.claude/agents/verdict-adversary.md` — Red Team: re-probes VERIFIED items
4. `.claude/agents/triage-analyst.md` — Verification: automated checks, €0
5. `.claude/agents/verifier-a.md` — Verification: Playbook-guided
6. `.claude/agents/verifier-b.md` — Verification: first-principles, NO Playbook
7. `.claude/agents/consolidator.md` — Verification: compares A vs B, resolves disagreements

### SPEC adversary output to review:
8. `reference/SPEC_ADVERSARY_NORMALIZATION.md` — 42 adversarial test cases (731 lines)

### Cross-reference against:
- `reference/AGENT_ARCHITECTURE.md` §2 — does each agent match its specification?
- Knowledge-diverse N-version design — does verifier-b truly have NO Playbook access?
- Red Team independence — do agents avoid information that would compromise adversarial value?

### Legacy agents to assess:
4 agent files exist that are NOT in the architecture:
- `.claude/agents/integrity-checker.md` — possibly replaced by integrity-auditor?
- `.claude/agents/researcher.md` — possibly replaced by deep-researcher?
- `.claude/agents/result-analyst.md` — purpose unclear
- `.claude/agents/scholarly-verifier.md` — possibly pre-architecture
Decision needed: archive these or confirm they serve a purpose.

### CC self-review was minimal:
Commit 9ea5394 changed only 3 lines (consolidator.md + SPEC adversary). For 7 new agent
definitions totaling ~47K bytes, this is suspiciously light. The Architect's review should
be correspondingly thorough.

---

## After Review: Transition Gate for Probe 2 (use kr-gating-transitions)

If the review passes, check all prerequisites for the Probe 1 → Probe 2 transition:
- All 16 architecture-required agents defined (verify)
- SPEC adversary run on normalization SPEC (verify output quality)
- Probe 1 integrity audit: CONDITIONAL PASS (3 MUST-FIX items, all contract alignment)
- SPEC fixes from integrity audit applied (commits cab35d7, fd65ae3)
- All 4 architecture teams have complete agent definitions (verify)

## After Transition Gate: Write Probe 2 NEXT.md (use kr-preparing-cc-handoffs)

If transition is approved, write the build directive for the normalization engine.
See the Probe 2 plan already drafted (git log shows commit 6b7eb3c had an earlier version).
