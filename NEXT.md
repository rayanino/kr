# NEXT SESSION

## Session Type
PRECISION (see SESSION_TYPES.md for full framework)

## Immediate Task

**Excerpting engine PRECISION session.** The CREATIVE session produced a 660-line SPEC with 5 §4.B capabilities and a 389-line contracts.py. This session: fix every vague quantifier, resolve every ambiguity, ensure every §4.A rule is machine-implementable, sync contracts.py with any SPEC changes, and run full quality checks.

## What to Read

1. `engines/excerpting/SPEC.md` — Full document. This is the target.
2. `engines/excerpting/contracts.py` — Must match SPEC §3 exactly.
3. `engines/atomization/SPEC.md` §3 — Upstream contract. Verify the excerpting engine's input contract matches atomization's output.
4. `engines/atomization/contracts.py` — Machine-readable atom schema. Verify field names match.
5. `DEEP_REASONING_PROTOCOL.md` — The Perfection Standard checklist. Run every criterion.
6. `KNOWLEDGE_INTEGRITY.md` — Verify T-2 (attribution), T-4 (context loss), T-5 (synthesis hallucination) mitigations are explicit.

**Do NOT read:** VISION.md, DOMAIN.md, reference docs (already incorporated in CREATIVE session). Do NOT do web research (PRECISION, not CREATIVE).

## Definition of Done

1. `check_spec_quality.py` produces 0 VAGUE_QUANTIFIER warnings (currently ~25).
2. Every §4.A rule has a clear pass/fail test case (mentally verifiable).
3. `contracts.py` fields match SPEC §3 field-by-field — no drift.
4. Input contract (§2) field names match `atomization/contracts.py` exactly.
5. Perfection Standard Tier 1 (all 9 criteria) pass for every section.
6. Self-audit with ≥3 structural defects found and fixed.
7. `session_quality_gate.py` passes.
8. Committed and pushed.
9. NEXT.md written (for excerpting HARDENING session).

## What the Previous Sessions Did

Source engine: CREATIVE → PRECISION → HARDENING → IMPL_PREP (complete).
Normalization engine: CREATIVE → PRECISION → HARDENING → IMPL_PREP (complete).
Passaging engine: CREATIVE → PRECISION → HARDENING (complete).
Atomization engine: CREATIVE → PRECISION → HARDENING (complete).
**Excerpting engine: CREATIVE (this session, complete).**

## Pending Owner Questions

- **API keys:** Will be needed when Claude Code starts implementation. Not blocking.
