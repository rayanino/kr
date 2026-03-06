# NEXT SESSION

## Session Type
PRECISION (see SESSION_TYPES.md for full framework)

## Immediate Task

**Passaging engine PRECISION session.** The passaging SPEC has been creatively rewritten with research-informed design, 6 §4.B capabilities (4 existing refined + 2 new architect-originated), Arabic examples, and comprehensive keyword/argument detection patterns. Now bring it to machine-implementable precision: run defect detection, fix ambiguities, verify all rules are implementable by Claude Code with zero clarifying questions.

## What to Read

1. `engines/passaging/SPEC.md` — the creative output from this session (643 lines). Read critically for:
   - Ambiguous rules that would require clarifying questions
   - Missing edge cases in the new capabilities (§4.B.5, §4.B.6)
   - Inconsistencies between §4.A rules and §3 output schema
   - Arabic keyword patterns that might be incomplete or overlapping
2. `engines/normalization/contracts.py` — verify that every normalization field the passaging SPEC references actually exists in the contract
3. `reference/DOMAIN.md` lines 238–277 (Arabic text challenges + format types) — verify the SPEC addresses all challenges mentioned

**Do NOT read:** VISION.md, kr_decisions.md, source engine SPEC, SESSION_LOG.md (unless you need prior session context).

## The PRECISION Work

### Defect Detection Phase
1. Run `python3 scripts/check_spec_quality.py engines/passaging/SPEC.md` (if available)
2. Systematic self-audit against the Perfection Standard (DEEP_REASONING_PROTOCOL.md):
   - Criterion #1 (Zero ambiguity): Every rule in §4.A must be implementable without clarifying questions
   - Criterion #9 (Adversarial-proof): Check the new argument detection patterns for false positives
   - Criterion #10 (Full input coverage): Verify every `structural_format` type has complete handling
   - Criterion #12 (Enumerated edge cases): Check §4.B.5 adaptation formulas for edge values
   - Criterion #13 (Testable rules): Every behavioral rule should have a clear pass/fail test

### Specific Areas to Verify
- **§4.A.4 scholarly keyword patterns:** Are the Arabic patterns complete? Do any overlap or conflict? Would the same text trigger multiple patterns incorrectly?
- **§4.A.4 isnad chain detection:** Are the isnad opening patterns comprehensive? What about `رواه` (he narrated it) without a full isnad chain?
- **§4.B.5 adaptation formulas:** Test the formulas with extreme values (technical_term_density = 0.0 and 1.0, transition_density = 0.0 and 100.0). Do they produce reasonable results?
- **§4.B.6 argument state machine:** Is the state machine deterministic? What happens when argument markers are nested (a مسألة within a larger مسألة)?
- **§2 input contract:** Verify content_census and tahqiq_topology field references match normalization contracts.py exactly
- **§3 output schema:** Do the new output fields (adaptive_params, argument_structure) need to be added to the schema?
- **§7 error handling:** Are the new error codes complete? Do all new failure modes have defined recovery?

### Defect Fixing Phase
Fix all HIGH-severity defects in the SPEC. Document each fix with the defect, the criterion violated, and the correction.

## Definition of Done

1. Self-audit completed with ≥5 defects found and fixed (if fewer found, the audit was superficial)
2. All §4.A rules pass the mental pseudocode test (can you write a function signature + pseudocode?)
3. §4.B.5 adaptation formulas tested with boundary values
4. §4.B.6 argument state machine specified as a formal state transition table
5. Passaging engine contracts.py created (Pydantic models for §3 output)
6. NEXT.md written (for passaging HARDENING session)
7. SESSION_LOG.md updated
8. Committed and pushed

## What the Previous Sessions Did

Source engine: CREATIVE → PRECISION → HARDENING → IMPL_PREP (complete).
Normalization engine: CREATIVE → PRECISION → HARDENING → IMPL_PREP (complete).
Passaging engine: Initial SPEC draft (502 lines, ABD era) → **CREATIVE session (this session)**: research-informed rewrite, 2 new §4.B capabilities (content census-driven adaptive passaging, scholarly argument boundary detection), 3+ Arabic examples, isnad chain integrity rule, Arabic sentence detection specification, expanded Q&A markers, content census integration. Score: 90/100.

## Pending Owner Questions

- **API keys:** Will be needed when Claude Code starts implementation. Not blocking.
