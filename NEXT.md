# NEXT SESSION

## Session Type
CREATIVE (see SESSION_TYPES.md for full framework)

## Immediate Task

**Atomization engine CREATIVE session.** The atomization engine is the next engine in the pipeline after passaging. It receives passages and identifies the atomic knowledge units within them — the smallest meaningful pieces of scholarly content (definitions, rulings, evidence citations, conditions, exceptions, etc.). This session: research Arabic NLP approaches to scholarly text classification, study the Islamic scholarly discourse structure, and write the atomization SPEC from scratch with research-informed §4.B capabilities.

## What to Read

1. `reference/DOMAIN.md` — domain knowledge for atom types in Islamic scholarship. Read §4 (content types) carefully.
2. `reference/ENTRY_EXAMPLE.md` — the target entry format. Atoms are what the excerpting engine combines into excerpts, and excerpts are what the synthesizer combines into entries. Understand what atom granularity the entry format NEEDS.
3. `reference/USER_SCENARIOS.md` — which scenarios depend on atom quality.
4. `engines/passaging/SPEC.md` §3 (output contract) — this is the atomization engine's INPUT. Read carefully.
5. `engines/passaging/contracts.py` — the Pydantic schema the atomization engine receives.
6. `reference/RESOURCES.md` — external tools and libraries for Arabic NLP.
7. Web search aggressively: Arabic text classification, Islamic scholarly discourse analysis, computational approaches to fiqh text, hadith chain analysis tools, Arabic rhetorical structure theory.

**Do NOT read:** VISION.md, kr_decisions.md, source engine SPEC, normalization SPEC (except by reference from passaging contracts).

## The CREATIVE Work

### Research Phase (use web search)
1. How do existing Arabic NLP tools classify text at the sub-paragraph level?
2. What are the recognized atom types in Islamic scholarly discourse? (usul al-fiqh provides a taxonomy: hukm, dalil, qiyas components, conditions, exceptions, etc.)
3. How do Arabic rhetorical structure theory (RST) parsers work? Any available tools?
4. What computational approaches exist for hadith isnad/matn separation?
5. How do existing Islamic studies databases (islamweb, al-maktaba al-shamila, dorar.net) categorize content?

### Design Phase
- Define the atom type taxonomy (the classification system for knowledge units)
- Design the atomization strategy per passage structural_format
- Design §4.B transformative capabilities (at least 2 architect-originated)
- Consider: what can atom-level patterns reveal about a source that passages can't?

### Key Design Decisions
- What is an "atom"? Is it a sentence? A semantic unit? A functional unit in scholarly discourse?
- How fine-grained should atomization be? (Too fine = noise; too coarse = lost structure)
- Should atom type classification use consensus? (Probably yes — this is interpretive)
- How do atom types vary across sciences? (Fiqh atoms differ from hadith atoms differ from tafsir atoms)

## Definition of Done

1. Atomization SPEC draft complete (all 10 sections)
2. At least 2 §4.B transformative capabilities fully specified
3. Atom type taxonomy defined with Arabic terms and examples
4. Research findings documented in SPEC rationale sections
5. `engines/atomization/contracts.py` created with Pydantic models
6. NEXT.md written (for atomization PRECISION session)
7. SESSION_LOG.md updated
8. Committed and pushed

## What the Previous Sessions Did

Source engine: CREATIVE → PRECISION → HARDENING → IMPL_PREP (complete).
Normalization engine: CREATIVE → PRECISION → HARDENING → IMPL_PREP (complete).
Passaging engine: CREATIVE → PRECISION → **HARDENING (this session)**: 8 threats analyzed, 4 new self-validation checks, 10 new error codes, state machine completed (2 missing transitions + deadlock proof), cross-page joining hardened (tanwin, Quran citations), §4.B.6 fallback for no-subboundary case, adaptation formula bounded.

## Pending Owner Questions

- **API keys:** Will be needed when Claude Code starts implementation. Not blocking.
