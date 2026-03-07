# NEXT SESSION

## Session Type
PRECISION (see SESSION_TYPES.md for full framework)

## Immediate Task

**Atomization engine PRECISION session.** The atomization SPEC has completed its CREATIVE session: 3 new §4.B capabilities added (argument completeness scoring, terminological concordance, evidence quality signal detection), bringing total to 8 transformative capabilities. contracts.py updated and compiles.

The SPEC now needs PRECISION work: vague quantifiers replaced with exact values, worked Arabic examples added to every §4 subsection, cross-references validated, and machine-readability ensured.

## What to Read

1. `engines/atomization/SPEC.md` — The full SPEC (read ALL sections).
2. `engines/atomization/contracts.py` — Verify alignment with SPEC §3.
3. Run `python3 scripts/check_spec_quality.py engines/atomization/SPEC.md` — work through every HIGH defect.

**Do NOT read:** VISION.md, kr_decisions.md, other engine SPECs, KNOWLEDGE_INTEGRITY.md, protocol documents.

## Definition of Done

1. Every HIGH defect from `check_spec_quality.py` resolved (target: 0 HIGH defects).
2. All vague quantifiers ("multiple", "few", "some", "many") replaced with exact values or bounded ranges.
3. Worked Arabic examples added to §4.A.1 through §4.A.10 (at least one per subsection showing input → processing → output with real Arabic text).
4. Arabic examples added to §4.B.6, §4.B.7, §4.B.8 (at least one per capability).
5. All cross-references between §3 (output contract), §4 (processing), §7 (errors), §8 (config), and §10 (tests) verified for consistency.
6. contracts.py verified to match SPEC §3 exactly — every field, every type, every constraint.
7. Review flag values in §3 match exactly the values referenced in §4 and §5.
8. `check_spec_quality.py` re-run shows meaningful improvement (target: ≤10 total defects).
9. Self-audit performed and documented (per DEEP_REASONING_PROTOCOL examples).
10. NEXT.md written (pointing to atomization HARDENING session).
11. SESSION_LOG.md updated.
12. Committed and pushed.

## Notes for Next Architect

- The 3 new §4.B capabilities (§4.B.6, §4.B.7, §4.B.8) need Arabic examples most urgently — they were designed with full behavioral rules but no worked examples yet.
- The check_spec_quality.py HIGH defects are concentrated in two categories: VAGUE_QUANTIFIER (15 instances of "multiple", "few", "some", "many") and MISSING_EXAMPLE (§4 subsections needing worked examples). The vague quantifiers are ALL in §4.A — none in §4.B.
- The new "incomplete_argument" review flag value needs to be added to the review_flags documentation in §3.
- The passaging engine contracts (engines/passaging/contracts.py, 556 lines) define the upstream schema — useful for verifying the input contract examples are realistic.

## Pending Owner Questions

- **API keys:** Will be needed when Claude Code starts implementation. Not blocking.
