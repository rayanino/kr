# NEXT SESSION

## Session Type
PRECISION (see SESSION_TYPES.md for full framework)

## Immediate Task

**Passaging engine PRECISION session.** The passaging SPEC received a Creative update integrating the normalization engine's newest capabilities (boundary_continuity §4.B.8, discourse_flow §4.B.10) and adding two new §4.B capabilities (§4.B.7 discourse-aware boundary optimization, §4.B.8 scholarly completeness forecast). This session resolves quality defects and ensures machine-implementability.

## What to Read

1. `engines/passaging/SPEC.md` — The full SPEC. Focus on the NEW sections: §4.B.6 (updated with discourse flow integration), §4.B.7 (new), §4.B.8 (new), §4.A.2 (updated with boundary_continuity), and §2 (updated input contract).
2. `engines/passaging/contracts.py` — The updated Pydantic models. Verify they match §3 exactly.
3. `DEEP_REASONING_PROTOCOL.md` — Perfection standard for defect detection.
4. Run `python3 scripts/check_spec_quality.py engines/passaging/SPEC.md` — 56 defects reported, mostly VAGUE_QUANTIFIER. Triage: many are false positives (uses of "multiple" in descriptive context), but some may be genuine precision issues.

**Do NOT read:** VISION.md, kr_decisions.md, other engine SPECs, DOMAIN.md (all context already in the SPEC).

## Definition of Done

1. `check_spec_quality.py` shows 0 HIGH defects (resolve or demonstrate false positive)
2. Every rule in §4.B.7 (discourse cost table) has a concrete Arabic example
3. Every rule in §4.B.8 (completeness forecast) has a concrete Arabic example
4. §4.B.6 signal hierarchy cross-validated: verify no case where discourse flow primary and keyword fallback produce contradictory boundaries that aren't handled
5. contracts.py matches §3 exactly — every field, every enum, every default
6. Self-audit performed: ≥3 defects found and fixed
7. `session_quality_gate.py` passes
8. NEXT.md written (for passaging HARDENING session)
9. SESSION_LOG.md updated
10. Committed and pushed

## Notes for Next Architect

- The discourse transition cost table (§4.B.7 Step 2) needs Arabic examples for at least the 0.0-cost transitions and the 0.9-cost transitions — show what text looks like at these boundaries.
- The completeness forecast (§4.B.8) dangling discourse expectations need examples showing what "position without evidence" looks like in Arabic text vs. "objection without response."
- The `evidence_*` wildcard is now documented (clarified in the fix note), but consider whether the cost table should have separate rows for each evidence type (they may have different costs in different sciences — e.g., evidence_ijma might be more important than evidence_qiyas in some contexts).
- The boundary_continuity integration in §4.A.2 added a "Character-level joining heuristics (fallback)" subheading — verify the original Rules 1-4 are still correctly numbered and referenced.
- Pre-existing defects: 40 HIGH defects mostly VAGUE_QUANTIFIER on words like "multiple" — triage carefully; most are contextually precise.

## Pending Owner Questions

- **API keys:** Will be needed when Claude Code starts implementation. Not blocking.
