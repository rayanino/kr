# NEXT SESSION

## Session Type
CREATIVE (see SESSION_TYPES.md for full framework)

## Immediate Task

**Invent transformative capabilities for the source engine.**

This is NOT a review session. Do NOT fix defects, correct prose, or align contracts. Those are for the PRECISION session (next). This session exists for ONE purpose: make the source engine do things no Islamic studies tool has ever done.

## What to Read (ONLY these — nothing else)

1. `engines/source/SPEC.md` — but ONLY §1 (Purpose) and §4.B (Transformative). Skip everything else.
2. `reference/ENTRY_EXAMPLE.md` — the quality target. What does a great entry look like?
3. `reference/USER_SCENARIOS.md` — who is Rayane and what does he need?

**Do NOT read:** SPEC_REFINEMENT.md, CREATIVE_MANDATE.md, SILENT_FAILURES.md, KNOWLEDGE_INTEGRITY.md, contracts.py, CONTEXT_BUDGET.md, CHALLENGE_PROTOCOL.md. Those are for other session types.

**Budget:** ~15K tokens on reading. ~50K tokens on web search results. ~80K tokens on thinking and writing. ~10K tokens on NEXT.md and commit.

## The Creative Work (follow this sequence)

### Phase 1: Research the Problem Space (3-5 web searches)

Search for what scholars struggle with, what tools exist, what's missing:
- `Islamic manuscript cataloging tools digital 2025 2026`
- `Arabic text source acquisition scholarly challenges`
- `digital humanities Islamic studies what's missing`
- `al-Shamela Maktaba alternative tools source management`

Write down: What frustrates scholars? What takes weeks manually? What tools exist but are inadequate?

### Phase 2: Research the Possibilities (3-5 web searches)

Search for what's technically possible NOW:
- `LLM Arabic metadata extraction scholarly texts`
- `citation network discovery Arabic classical texts`
- `OCR Arabic manuscript diacritics 2025 2026 QARI`
- `book recommendation system scholarly domain graph`
- `OpenITI metadata author network Islamic texts`

Write down: What technologies could the source engine use that no Islamic studies tool uses today?

### Phase 3: Invent (the core work — spend most tokens here)

For each invention, answer ALL of these:
1. **Name:** What is this capability called?
2. **Technology:** What specific tool/technique makes this possible? (Name versions, libraries, APIs)
3. **Input:** What does this capability receive?
4. **Output:** What does it produce? Show a CONCRETE example with real Arabic text.
5. **Scholar impact:** What can Rayane do now that he literally couldn't before?
6. **Implementation sketch:** 5-10 sentences on how it works (not pseudocode — behavioral description)

**Minimum 3 new capabilities. Aim for 5.**

Thinking directions (don't just copy these — use them as starting points):
- The source engine processes 500 sources over a year. What PATTERNS emerge across those 500 sources that no human could see? (Citation networks? Author influence? Topic evolution? Edition quality signals?)
- When Rayane uploads iPhone photos of a book, what can the source engine INFER beyond just OCR? (Is this a well-known edition? Who is the likely muhaqiq? What other books should Rayane get next?)
- What does the source engine know about the RELATIONSHIP between sources that individual sources don't tell you? (Which authors cite each other? Which topics have competing scholarly traditions? Which editions are most reliable for which topics?)
- Can the source engine detect something about a source's QUALITY or TRUSTWORTHINESS that a student wouldn't notice but a senior scholar would? (Signs of weak tahqiq, missing isnad chains, anachronistic language suggesting forgery or error)

### Phase 4: Write §4.B

Write the full §4.B section with every capability specified precisely. Not aspirational — specified. Every capability should pass this test: "Could Claude Code build this from what I wrote, without asking me anything?"

### Phase 5: Update RESOURCES.md

For every tool, library, or dataset discovered, add it to `reference/RESOURCES.md` with: name, URL, version, what it does, Arabic support status, license, how KR would use it.

## Definition of Done

1. §4.B has ≥3 new fully-specified capabilities (beyond what's already there)
2. Each capability names specific technology with version
3. Each capability has a concrete output example with real Arabic text
4. ≥8 web searches conducted (with findings noted)
5. RESOURCES.md updated with every discovery
6. `python3 scripts/creative_verification.py engines/source/SPEC.md` scores ≥85/100
7. NEXT.md written for the PRECISION session (source engine)
8. SESSION_LOG.md updated
9. Committed and pushed

## What the Previous Sessions Did

Two hardening rounds built the autonomous system infrastructure: quality checking scripts, creative verification, session quality gates, consolidated Claude Code environment (7 commands, 4 agents, 5 skills), restructured PROJECT_INSTRUCTIONS.md. Created SESSION_TYPES.md framework splitting SPEC refinement into focused CREATIVE → PRECISION → HARDENING → IMPLEMENTATION_PREP sessions.

## Pending Owner Questions

- **API keys:** Not needed for this session (creative work doesn't require LLM calls)
