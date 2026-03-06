# NEXT SESSION

## Session Type
CREATIVE (see SESSION_TYPES.md for full framework)

## Immediate Task

**Passaging engine CREATIVE session.** The passaging engine has an initial SPEC draft (502 lines) written during the ABD era. It needs the full creative treatment: research what makes good passage boundaries in Arabic scholarly texts, invent transformative §4.B capabilities, and bring the SPEC to the same quality standard as the source and normalization SPECs.

## What to Read

1. `engines/passaging/SPEC.md` — the current draft. Read critically: it was written before the normalization engine SPEC was refined, so its input contract may reference outdated field names or miss new normalization output fields (content_census, tahqiq_topology, content_flags expansion).
2. `engines/normalization/contracts.py` — the upstream contract. The passaging engine consumes NormalizedPackage. Understand every field it provides.
3. `reference/DOMAIN.md` — scholarly context for what makes good passage boundaries.
4. `reference/ENTRY_EXAMPLE.md` — the quality target. Work backwards: what passage quality produces entries this good?
5. `reference/USER_SCENARIOS.md` — which scenarios depend on passage quality.

**Do NOT read:** VISION.md (use extract script if needed), normalization SPEC (you already know the output contract from contracts.py), kr_decisions.md (unless passage-related decisions exist).

## The CREATIVE Work

### Research Phase (use web search aggressively)
1. How do existing Arabic text processing tools handle passage segmentation?
2. What is the state of the art in topic segmentation for Arabic?
3. How do Islamic studies databases (Shamela, al-Maktaba al-Shamilah, Turath) segment texts?
4. What NLP techniques work for Arabic text boundary detection?
5. How do versified texts (nazm) need different passaging than prose?

### Invention Phase
The passaging engine's §4.B needs at least one capability the architect originated. Directions from DEEP_REASONING_PROTOCOL.md:
- What makes a "good" passage boundary? Can passage quality predict downstream extraction quality?
- Can the passaging engine use the normalization engine's content census to ADAPT its strategy per-source?
- Can passage boundaries be informed by the division tree structure in intelligent ways?
- Can the engine detect when a scholarly argument spans multiple pages and keep it together?

### Specification Phase
Bring the SPEC to the same quality level as normalization SPEC:
- §4.A rules precise enough for Claude Code with zero clarifying questions
- Arabic text examples for key behaviors
- Edge cases enumerated (cross-page continuity, empty pages, verse blocks)
- Every validation check specified with thresholds

## Definition of Done

1. Passaging SPEC fully rewritten with research-informed design
2. At least 2 transformative §4.B capabilities designed
3. At least 3 Arabic examples in §4.A
4. Creative verification score ≥85
5. NEXT.md written (for passaging PRECISION session)
6. SESSION_LOG.md updated
7. Committed and pushed

## What the Previous Sessions Did

Source engine: CREATIVE → PRECISION → HARDENING → IMPL_PREP (complete).
Normalization engine: CREATIVE → PRECISION → HARDENING → IMPL_PREP (complete).
Passaging engine: Initial SPEC draft exists (502 lines, ABD era). Needs full creative treatment.

## Pending Owner Questions

- **API keys:** Will be needed when Claude Code starts implementation. Not blocking.
