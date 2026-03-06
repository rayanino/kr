# NEXT SESSION

## Session Type
CREATIVE (see SESSION_TYPES.md for full framework)

## Immediate Task

**Excerpting engine CREATIVE session.** The excerpting engine is the most consequential engine in the pipeline — it determines what the owner sees. A bad excerpt teaches wrong information. This session: research the domain deeply, write the excerpting SPEC from scratch, invent §4.B capabilities.

## What to Read

1. `reference/DOMAIN.md` — Full document. The excerpting section in "Design Implications" is critical. Read the "What Failure Looks Like" section for excerpting failure modes.
2. `reference/ENTRY_EXAMPLE.md` — The quality target. What excerpts must eventually produce.
3. `reference/USER_SCENARIOS.md` — Scenarios 1, 3, 5, 8 are excerpting-dependent.
4. `KNOWLEDGE_INTEGRITY.md` — T-2 (attribution), T-4 (context loss), T-5 (synthesis hallucination) all depend on excerpt quality.
5. `engines/atomization/SPEC.md` §3 — The atom stream that excerpting consumes. Read the output contract carefully.
6. `engines/atomization/contracts.py` — Machine-readable atom schema.
7. `CREATIVE_MANDATE.md` — Follow the Creative Exploration Protocol.

**Do NOT read:** VISION.md (use extract_vision_sections.py for specific sections if needed). Do NOT read source/normalization/passaging SPECs unless you need boundary contract details.

**Web research.** Research aggressively:
- How do Islamic scholars actually excerpt from texts? What constitutes a "self-contained" scholarly unit?
- What makes a good excerpt boundary vs. a bad one?
- How do existing digital Islamic studies tools (Shamela, Maktabah, Turath) handle text extraction?
- What does IslamicLegalBench (2026) say about LLM accuracy on Islamic legal tasks?
- How do scholarly citation management tools (Zotero, Mendeley) handle excerpt/annotation structures?

## Definition of Done

1. `engines/excerpting/SPEC.md` — Complete SPEC following the template in DEEP_REASONING_PROTOCOL.md
2. `engines/excerpting/contracts.py` — Pydantic models for excerpt records
3. At least 2 §4.B capabilities that are architect-originated and transformative
4. Self-audit completed with ≥3 structural defects found and fixed
5. `check_spec_quality.py` and `creative_verification.py` run
6. NEXT.md written (for excerpting PRECISION session)
7. SESSION_LOG.md updated
8. Committed and pushed

## What the Previous Sessions Did

Source engine: CREATIVE → PRECISION → HARDENING → IMPL_PREP (complete).
Normalization engine: CREATIVE → PRECISION → HARDENING → IMPL_PREP (complete).
Passaging engine: CREATIVE → PRECISION → HARDENING (complete).
Atomization engine: CREATIVE → PRECISION → **HARDENING (complete)**.

## Pending Owner Questions

- **API keys:** Will be needed when Claude Code starts implementation. Not blocking.
