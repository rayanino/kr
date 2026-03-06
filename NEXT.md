# NEXT SESSION

## Session Type
CREATIVE (see SESSION_TYPES.md for full framework)

## Immediate Task

**Invent transformative capabilities for the normalization engine.**

The source engine preparatory work is complete (4 sessions: CREATIVE → PRECISION → HARDENING → IMPL_PREP). Now moving to the next engine in pipeline order. Implementation will be done by Claude Code later — Claude Chat handles all preparatory/design work first.

## What to Read

1. `engines/normalization/SPEC.md` — **ALL sections.** You are building on this foundation.
2. `engines/normalization/contracts.py` — machine-readable truth for §2/§3 fields
3. `engines/source/SPEC.md` §3 only — the upstream output contract (normalization's input)
4. `reference/ENTRY_EXAMPLE.md` — the quality target
5. `reference/USER_SCENARIOS.md` — who is Rayane and what does he need?

**Do NOT read:** SPEC_REFINEMENT.md, CREATIVE_MANDATE.md, SILENT_FAILURES.md, KNOWLEDGE_INTEGRITY.md, CONTEXT_BUDGET.md, CHALLENGE_PROTOCOL.md, source engine §4 (too much context — you only need §3 for the boundary).

**Budget:** ~15K tokens on reading. ~50K tokens on web search + creative thinking. ~30K tokens on writing. ~10K tokens on handoff.

## The Creative Work (follow this sequence)

### Phase 0: GROUND (before any creative work — ~10% of budget)

1. **Read the full normalization SPEC.** As you read, note:
   - What does this engine ACTUALLY do? (What do the §4.A rules specify concretely?)
   - What feels vague or under-specified?
   - What §4.B capabilities already exist? Are they well-specified or hollow?
   - What is the normalization boundary and why does it matter?
   - What metadata does this engine produce (§3) that downstream engines consume?

2. **Run quality baseline:**
   ```
   python3 scripts/check_spec_quality.py engines/normalization/SPEC.md --verbose
   python3 scripts/creative_verification.py engines/normalization/SPEC.md
   ```
   Record: "Baseline: X high-severity defects. §4.B score: Y/100."

3. **Write a 5-line assessment** (for your own reference):
   - Core processing (§4.A) is [solid/adequate/weak] because [reason]
   - Main quality gaps: [top 3]
   - Existing §4.B: [list them, real or hollow?]
   - This engine's unique data advantage: [what does it know that nothing else does?]
   - Biggest opportunity: [what's missing that would be transformative?]

### Phase 1: Research the Problem Space (3-5 web searches)

The normalization engine converts raw source formats (Shamela HTML, PDF, Word, photos, EPUB) into a uniform normalized package. Research:
- `Arabic document parsing OCR structure detection 2025 2026`
- `PDF Arabic text extraction layout analysis scholarly`
- `Docling Arabic document understanding structured output`
- `multi-layer Islamic text detection sharh matn hashiyah`

### Phase 2: Research the Possibilities (3-5 web searches)

- `Arabic OCR comparison Mistral QARI Tesseract diacritics 2025 2026`
- `document layout analysis Arabic manuscripts columns footnotes`
- `text quality assessment automated Arabic OCR confidence`
- `structural hierarchy detection Arabic scholarly book chapter`

### Phase 3: Invent Capabilities (the core creative work)

Thinking directions for normalization:
- The normalization engine sees the RAW source format — all the formatting clues (fonts, spacing, headers, footnotes) that disappear after normalization. What intelligence can be extracted from format-specific markup BEFORE it's stripped?
- Can the engine detect multi-layer composition (sharh text vs. matn text vs. hashiyah) from visual/structural cues alone?
- Can it assess text quality DURING normalization (OCR confidence, missing pages, truncated content) and flag problems before downstream engines waste time on bad input?
- Can it detect structural patterns (chapter hierarchy, section numbering, verse markers) that help the passaging engine make better decisions?
- What does a really good normalized package look like vs. a mediocre one? Can quality be measured?

### Phase 4: Write §4.B

Full specification. Inputs, outputs, triggers, algorithms, edge cases, failure handling.

### Phase 5: Update RESOURCES.md

## Definition of Done

1. Phase 0 completed: quality baseline recorded, 5-line assessment written
2. §4.B has ≥3 new fully-specified capabilities (beyond what's already there)
3. Each capability names specific technology with version
4. Each capability has a concrete output example with real Arabic text
5. ≥8 web searches conducted
6. RESOURCES.md updated with every discovery
7. `python3 scripts/creative_verification.py engines/normalization/SPEC.md` scores ≥85/100
8. NEXT.md written for the PRECISION session (normalization engine)
9. SESSION_LOG.md updated
10. Committed and pushed

## What the Previous Sessions Did

Source engine complete (4 sessions):
- Session 1 (CREATIVE): 3 new capabilities (KITAB text reuse, edition comparison, scholarly genealogy). §4.B: 75→90.
- Session 2 (PRECISION): 41→4 HIGH defects. 12 Arabic examples. All vague language replaced.
- Session 3 (HARDENING): 9 corruption paths closed. Enrichment invariants, freeze verification, registry atomicity.
- Session 4 (IMPL_PREP): contracts.py rewritten (690L), 30 module stubs, 90+ test cases, 20-task build plan.

Source engine is now fully ready for Claude Code implementation.

## Pending Owner Questions

- **API keys:** Not needed for preparatory work. Will be needed when Claude Code starts implementation.
