# NEXT SESSION

## Session Type
HARDENING (see SESSION_TYPES.md for full framework)

## Immediate Task

**Passaging engine HARDENING session.** The passaging SPEC has been through CREATIVE (research-informed rewrite) and PRECISION (16 defects found and fixed, contracts.py created, state machine formalized). Now verify no knowledge corruption paths exist: threat model the passaging engine's failure modes, verify every error produces a visible failure rather than silent data loss, and confirm the self-validation checks catch all structural invariants.

## What to Read

1. `engines/passaging/SPEC.md` — the precision-hardened SPEC (~710 lines). Read critically for:
   - Failure modes where bad boundaries could silently corrupt downstream outputs
   - Error handling completeness: every warning/fatal has a defined recovery
   - The self-validation checks (§4.A.10): are they sufficient to catch all structural invariants?
   - Argument detection (§4.B.6): can the state machine enter an invalid state?
2. `engines/passaging/contracts.py` — verify schema completeness against SPEC §3
3. `KNOWLEDGE_INTEGRITY.md` — the threat model framework. Apply it to passaging-specific threats.
4. `engines/normalization/SPEC.md` §5 (validation section only) — compare validation approach

**Do NOT read:** VISION.md, kr_decisions.md, source engine SPEC.

## The HARDENING Work

### Threat Analysis
For each passaging failure mode, answer: "What happens to the library if this goes wrong?"

Key threat vectors:
1. **Silent text loss.** Cross-page assembly drops text. Downstream never knows.
2. **Bad boundary corruption.** A split argument produces two incomplete excerpts. Both enter the library as if complete.
3. **Metadata loss.** A passage loses its `text_layers` attribution. Downstream assigns wrong author.
4. **Footnote corruption.** Renumbering maps wrong markers. Excerpts cite wrong footnotes.
5. **Argument detection false positive.** Engine keeps two unrelated مسائل together as one "argument." Oversized passage → oversized excerpt → confusing entry.
6. **Adaptation formula edge case.** Content census has extreme values. Adapted parameters produce zero-size or infinite-size targets.
7. **State machine deadlock.** Argument detector enters BODY state and never exits (no conclusion marker found, no new opening, division continues indefinitely).
8. **Cross-page joining false join.** Two separate words joined without space. Corrupts the Arabic text permanently.

For each threat: assess severity, identify existing mitigation (from SPEC), identify gaps, propose fixes.

### Validation Completeness Audit
Review §4.A.10 self-validation checks. For each structural invariant in §3 (guarantees), verify that at least one self-validation check would catch a violation. Look for unchecked invariants.

### Error Handling Completeness
Review §7 error table. For each processing step in §4.A, verify that all failure modes have defined error codes. Look for processing steps that can fail but have no error defined.

## Definition of Done

1. Threat analysis completed with ≥6 threats assessed
2. At least 2 new self-validation checks or error codes added to close gaps
3. §4.B.6 state machine verified: no deadlock states, all transitions deterministic
4. Cross-page joining rules verified: no false-join scenario uncaught
5. All §3 guarantees have corresponding validation checks
6. NEXT.md written (for atomization engine CREATIVE session)
7. SESSION_LOG.md updated
8. Committed and pushed

## What the Previous Sessions Did

Source engine: CREATIVE → PRECISION → HARDENING → IMPL_PREP (complete).
Normalization engine: CREATIVE → PRECISION → HARDENING → IMPL_PREP (complete).
Passaging engine: Initial SPEC draft → CREATIVE (research-informed rewrite, 6 §4.B capabilities) → **PRECISION (this session)**: 16 defects found and fixed, contracts.py created, state machine formalized, all §4.B output fields added to §3 schema, adaptation formulas verified with boundary values.

## Pending Owner Questions

- **API keys:** Will be needed when Claude Code starts implementation. Not blocking.
