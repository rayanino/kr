# NEXT SESSION

## Session Type
PRECISION (see SESSION_TYPES.md for full framework)

## Immediate Task

**Excerpting engine PRECISION session.** The CREATIVE session added 3 new §4.B capabilities (§4.B.4 Mas'ala Detection, §4.B.5 Evidence Chain Reconstruction, §4.B.6 Cross-Source Resonance Detection), wrote contracts.py, added verse-format handling (§4.A.7), and expanded the output contract. Now: make every rule machine-implementable. Fix all vague quantifiers. Add worked examples with Arabic text.

## What to Read

1. `engines/excerpting/SPEC.md` — The full SPEC. This is the primary work artifact.
2. `engines/excerpting/contracts.py` — Pydantic models. Must stay in sync with §3.
3. `engines/atomization/SPEC.md` §3 — Verify all input fields consumed are still correct.
4. `engines/atomization/contracts.py` — Verify type compatibility at the boundary.

**Do NOT read:** VISION.md, DOMAIN.md, ENTRY_EXAMPLE.md — already consumed in CREATIVE session.

## Definition of Done

1. All 19 defects from `check_spec_quality.py` resolved (especially the 13 vague quantifiers and 5 missing examples)
2. §4.A.1–§4.A.7 each have at least one worked example with Arabic text showing input atoms → processing → output excerpt
3. §4.B.1 refined: the existing dialogue detection clarified with precise trigger conditions
4. `contracts.py` verified against §3 — no field mismatches
5. `check_spec_quality.py` passes with ≤5 defects (all LOW severity)
6. Self-audit completed with ≥3 structural defects found and fixed
7. NEXT.md written (for excerpting HARDENING session)
8. SESSION_LOG.md updated
9. Committed and pushed

## What the Previous Session Did

- CREATIVE session for excerpting engine
- Added §4.B.4 (Mas'ala Boundary Detection and Issue Formulation) — architect-originated
- Added §4.B.5 (Evidence Chain Reconstruction) — architect-originated, informed by argumentation mining research
- Added §4.B.6 (Cross-Source Textual Resonance Detection) — architect-originated, informed by KITAB/passim research
- Added §4.A.7 (Verse-Format Excerpt Handling)
- Wrote contracts.py (459 lines, 30+ Pydantic models)
- Updated §3 output contract with transformative capability fields
- Updated metadata pass-through list
- Research: 5 web searches covering Talmud digital tools (DICTA, Sefaria, ChavrutAI), argumentation mining (RST, GNN), Arabic NLP (ArabicNLP 2025, AbjadNLP 2026), KITAB/OpenITI text reuse, Islamic DH landscape

## Pending Owner Questions

- **API keys:** Will be needed when Claude Code starts implementation. Not blocking.
