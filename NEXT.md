# NEXT SESSION

## Session Type
CREATIVE (see SESSION_TYPES.md for full framework)

## Immediate Task

**Atomization engine CREATIVE session.** The passaging engine has completed all 4 refinement sessions (Creative, Precision, Hardening, Implementation Prep) and is ready for Claude Code. The atomization engine has an existing SPEC but has not gone through the refinement cycle.

## What to Read

1. `engines/atomization/SPEC.md` — The full SPEC (read ALL sections).
2. `engines/atomization/contracts.py` — Existing Pydantic models.
3. `reference/ENTRY_EXAMPLE.md` — Quality target (how atoms feed into entries).
4. `reference/USER_SCENARIOS.md` — Who benefits and how.

**Do NOT read:** VISION.md, kr_decisions.md, other engine SPECs, KNOWLEDGE_INTEGRITY.md, protocol documents.

## Definition of Done

1. Full SPEC read + quality baseline recorded (`check_spec_quality.py` + `creative_verification.py`).
2. 5-line assessment written (§4.A soundness, main gaps, §4.B evaluation, data advantage, opportunity).
3. 3–5 web searches on Arabic NLP atom-level analysis, scholarly discourse tagging, Islamic text classification.
4. 3–5 web searches on LLM capabilities for Arabic text classification, existing tools.
5. ≥3 new transformative capabilities designed for §4.B (fully specified: inputs, outputs, triggers, edge cases).
6. §4.B written with full specification of each capability.
7. RESOURCES.md updated with any new tools/libraries discovered.
8. Quality check shows improvement in creative verification score.
9. NEXT.md written (pointing to atomization PRECISION session).
10. SESSION_LOG.md updated.
11. Committed and pushed.

## Notes for Next Architect

- The atomization engine is where raw text first becomes semantically tagged — this is where scholarly intelligence enters the pipeline.
- Atom types include: definition, evidence, opinion, isnad, verse citation, etc. The SPEC should enumerate these precisely.
- The engine's unique data advantage: it sees passage text WITH structural format context, text layers, content flags — all the normalization and passaging metadata is available as classification signals.
- Key question for §4.B: what atom-level patterns reveal scholarly conventions that are invisible to a human reader scanning text? What can atom type distributions tell you about a source?
- Passaging engine contracts.py (556 lines) defines the upstream schema — the atomization engine's input.

## Pending Owner Questions

- **API keys:** Will be needed when Claude Code starts implementation. Not blocking.
