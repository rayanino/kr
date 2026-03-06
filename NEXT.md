# NEXT SESSION

## Session Type
PRECISION (see SESSION_TYPES.md for full framework)

## Immediate Task

**Source engine PRECISION session.** The source engine SPEC has completed its CREATIVE session — three new §4.B capabilities were added (§4.B.8 Cross-Validated Scholar Authority Bootstrapping, §4.B.9 Source Difficulty Prediction, §4.B.10 Tahqiq Apparatus Fingerprinting), and the total capabilities now stand at 10. The SPEC is 1140+ lines.

This PRECISION session should: make every rule in §4.A and §4.B machine-implementable (Claude Code can build with zero clarifying questions), fix all HIGH-severity defects from `check_spec_quality.py`, ensure all error codes from the new capabilities are in §7, and verify contracts.py matches the SPEC exactly.

## What to Read

1. `engines/source/SPEC.md` — Full SPEC. This is a PRECISION session — read methodically, rule by rule.
2. `engines/source/contracts.py` — Verify every model matches the SPEC output descriptions.
3. Run `python3 scripts/check_spec_quality.py engines/source/SPEC.md` — Fix all HIGH defects.
4. `KNOWLEDGE_INTEGRITY.md` §Invariants — Verify no new capability violates invariants.

**Do NOT read:** VISION.md, other engine SPECs, CREATIVE_MANDATE.md. This is precision work, not creative work.

## Definition of Done

1. All HIGH-severity defects from `check_spec_quality.py` resolved
2. Every §4.A rule has: input, output, edge case, failure handling
3. Every §4.B capability has: input, output, trigger, behavioral rules, error codes
4. All new error codes (from §4.B.8-10) added to §7 error taxonomy
5. contracts.py has models for every SPEC output — no SPEC field without a corresponding Pydantic field
6. SPEC quality check run: 0 HIGH defects
7. Self-audit: ≥3 structural/semantic defects found and fixed
8. §9 (Current Implementation State) updated to reference new capabilities as [NOT YET IMPLEMENTED]
9. NEXT.md written (for source engine HARDENING session)
10. SESSION_LOG.md updated
11. Committed and pushed

## Key Defects to Fix (from CREATIVE session quality check)

The `check_spec_quality.py` run found 15 HIGH-severity defects, concentrated in:
- Vague quantifiers ("multiple", "many", "some") — replace with specific numbers or "configurable" references
- Unbounded "etc." — enumerate or reference configuration
- Unvalidated writes — add explicit validation steps before writes in §4.B.5, §4.B.7

## Pending Owner Questions

- **API keys:** Will be needed when Claude Code starts implementation. Not blocking.
