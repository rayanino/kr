# NEXT SESSION

## Session Type
HARDENING (see SESSION_TYPES.md for full framework)

## Immediate Task

**Excerpting engine HARDENING session.** The PRECISION session resolved all 28 quality defects, added 6 worked examples with Arabic text, fixed duplicate §4.B section numbering (renumbered to §4.B.1–§4.B.8), synced contracts.py with §3 (added 4 missing fields + 8 new enums), and completed self-audit with 4 structural defects fixed. Now: verify no knowledge corruption paths. Threat analysis for decontextualization, misattribution, and silent data loss.

## What to Read

1. `engines/excerpting/SPEC.md` — The full SPEC. Primary review target.
2. `engines/excerpting/contracts.py` — Verify no corruption can enter through schema gaps.
3. `KNOWLEDGE_INTEGRITY.md` — The threat model. Every threat must be addressed.
4. `engines/atomization/SPEC.md` §3, §7 — Verify upstream error handling doesn't propagate corruption.

**Do NOT read:** VISION.md, DOMAIN.md — already consumed in CREATIVE session.

## Definition of Done

1. Every knowledge corruption path in KNOWLEDGE_INTEGRITY.md has a corresponding prevention mechanism in the excerpting SPEC
2. Decontextualization prevention (§4.A.2) verified: construct 3 adversarial test cases where misattribution WOULD occur without the prevention mechanism, and verify the SPEC rules prevent each one
3. Multi-layer attribution (§4.A.3) verified: construct 2 adversarial test cases where layer misattribution WOULD occur
4. Evidence integrity (§4.A.4) verified: ensure no path exists where hadith grading is silently dropped
5. Silent data loss audit: trace every path where data could be lost without a log entry or review flag
6. Error cascade analysis: verify that upstream errors (bad atoms, missing metadata) produce visible failures, not silent corruption
7. `check_spec_quality.py` still passes with 0 defects
8. NEXT.md written (for taxonomy engine CREATIVE session or excerpting IMPLEMENTATION_PREP — whichever is more urgent)
9. SESSION_LOG.md updated
10. Committed and pushed

## What the Previous Session Did

- PRECISION session for excerpting engine
- Resolved all 28 check_spec_quality.py defects (21 vague quantifiers, 6 missing examples, 1 unbounded)
- Added 6 worked examples with Arabic text to §4.A.2–§4.A.7
- Fixed duplicate §4.B section numbering: renumbered Dialogue (→§4.B.6), Repair (→§4.B.7), Resonance (→§4.B.8)
- Fixed all cross-references in both SPEC.md and contracts.py
- Synced contracts.py: added 4 missing fields + 8 new enums
- Self-audit: 4 structural defects found and fixed

## Pending Owner Questions

- **API keys:** Will be needed when Claude Code starts implementation. Not blocking.
