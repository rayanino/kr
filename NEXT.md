# NEXT SESSION

## Session Type
HARDENING (see SESSION_TYPES.md for full framework)

## Immediate Task

**Atomization engine HARDENING session.** The atomization SPEC has completed CREATIVE (8 §4.B capabilities) and PRECISION (vague quantifiers fixed, 13 Arabic examples added, contracts updated, cross-references verified). The SPEC is now at 1029 lines with 18 remaining check_spec_quality.py defects (8 HIGH — 5 are false-positive "few-shot" technical terms, 3 are §4.B.2/3/4 missing examples from the CREATIVE session).

The SPEC now needs HARDENING: adversarial scenarios, failure cascade analysis, invariant verification, and knowledge integrity threat assessment.

## What to Read

1. `engines/atomization/SPEC.md` — The full SPEC (read ALL sections, especially §4.A.8, §4.A.10, §5, §7).
2. `KNOWLEDGE_INTEGRITY.md` — Threat model for knowledge corruption paths.
3. Run `python3 scripts/check_spec_quality.py engines/atomization/SPEC.md` — address any remaining real defects.

**Do NOT read:** VISION.md, kr_decisions.md, other engine SPECs, CREATIVE_MANDATE.md, protocol documents.

## Definition of Done

1. At least 10 adversarial scenarios documented (attack vector → engine behavior → knowledge impact).
2. At least 2 failure cascade analyses (single failure → what breaks downstream).
3. All knowledge integrity invariants from KNOWLEDGE_INTEGRITY.md verified against this SPEC.
4. Any defects found during hardening fixed in the SPEC.
5. Error handling table (§7) verified complete — every error code has a defined recovery, every failure mode has a defined error code.
6. `check_spec_quality.py` re-run shows no regression from current 18 defects.
7. Self-audit performed and documented.
8. NEXT.md written (pointing to atomization IMPLEMENTATION_PREP session).
9. SESSION_LOG.md updated.
10. Committed and pushed.

## Notes for Next Architect

- The 5 remaining VAGUE_QUANTIFIER flags are false positives: 3 instances of "few-shot" (ML technical term), 1 "some but not all" (precise), 1 "that many" (pronoun). Document in self-audit, do not change.
- The 3 MISSING_EXAMPLE flags for §4.B.2/3/4 are from the CREATIVE session — these capabilities have full behavioral specs but no worked Arabic examples. If time permits during HARDENING, add examples; if not, note as a gap for IMPLEMENTATION_PREP to address.
- The offset integrity invariant (§4.A.8, V-2) is the most critical knowledge safety mechanism — focus adversarial analysis here. What happens when the LLM returns offsets that are subtly wrong (e.g., off by 1 in the middle of a multi-byte Arabic character)?
- The layer attribution system (§4.A.6) has the highest misattribution risk — an incorrect layer assignment puts words in the wrong scholar's mouth. Focus threat analysis here.
- The contracts.py now includes the "incomplete_argument" review flag (added this session).

## Pending Owner Questions

- **API keys:** Will be needed when Claude Code starts implementation. Not blocking.
