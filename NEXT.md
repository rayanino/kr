# NEXT SESSION

## Session Type
HARDENING (see SESSION_TYPES.md for full framework)

## Immediate Task

**Synthesis engine HARDENING session.** The CREATIVE session produced the SPEC draft; the PRECISION session refined it to 0 genuine high-severity defects, added 9 worked examples with Arabic text, added 3 prompt templates, added §5.4 threat mapping for all 7 KNOWLEDGE_INTEGRITY.md threats, added 8 new error codes, and aligned contracts.py with the SPEC. The HARDENING session must: verify no knowledge corruption paths exist, stress-test the attribution-first pipeline design against adversarial inputs, and validate that the threat mitigations in §5.4 are complete.

## What to Read

1. `engines/synthesis/SPEC.md` §5.4 — The threat mapping to verify and stress-test.
2. `KNOWLEDGE_INTEGRITY.md` — Full threat model. Verify every threat has a synthesis-specific mitigation and every mitigation is testable.
3. `engines/synthesis/SPEC.md` §4.A.4.1 — The attribution-first pipeline. This is the primary hallucination defense. Stress-test with adversarial scenarios.
4. `engines/synthesis/SPEC.md` §7 — Error handling table. Verify every processing failure has a defined error code and recovery.
5. `engines/taxonomy/SPEC.md` §3 — Output contract. Verify the synthesis engine's §2 input expectations match exactly.

**Do NOT read:** VISION.md, DOMAIN.md. Do NOT read other engine SPECs except §3 output contracts and §4.B.6 (landscape).

## Definition of Done

1. Every T-1 through T-7 threat in §5.4 has at least one adversarial test scenario showing the mitigation works
2. At least 3 adversarial scenarios for the attribution-first pipeline (§4.A.4.1): e.g., what happens when all excerpts are low-quality, when an excerpt contradicts its own metadata, when the LLM consistently hallucinates despite entailment checks
3. Error cascade analysis: trace at least 2 failure chains from upstream error → synthesis impact → recovery
4. Verify §2 input contract matches taxonomy engine §3 output contract field-for-field
5. Verify all error codes in §7 are reachable from §4 processing rules
6. Self-audit: ≥3 structural/semantic defects found and fixed
7. NEXT.md written (for next engine SPEC or implementation prep)
8. SESSION_LOG.md updated
9. Committed and pushed

## Key Issues from PRECISION Session

- **5 false positive high-severity defects remain** in the quality script output. These are documented in SESSION_LOG.md and are genuinely false positives:
  - L 491: "how many" is a question phrase, not a vague quantifier
  - L 625: "topic-appropriate" is a compound adjective
  - L 384, 495, 535: UNVALIDATED_WRITE false positives (validation is on same line, or the match is a read not a write)
- **§5.4 threat mapping is new and untested** — the HARDENING session should verify each threat's mitigations are complete and testable
- **Prompt templates are in Arabic** — the HARDENING session should verify the templates would produce correct structured output with Instructor

## Pending Owner Questions

- **API keys:** Will be needed when Claude Code starts implementation. Not blocking.
