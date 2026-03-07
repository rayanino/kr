# NEXT SESSION

## Session Type
CREATIVE (see SESSION_TYPES.md for full framework)

## Immediate Task

**Normalization engine CREATIVE session.** The source engine has completed CREATIVE, PRECISION, and HARDENING. It is the first engine to be fully hardened. The normalization engine SPEC needs its first CREATIVE session — the session where transformative §4.B capabilities are invented.

Read the current normalization SPEC to understand its baseline, then design §4.B capabilities that make previously impossible scholarship possible through the normalization step. The normalization engine sits at the format-to-universal boundary — it sees structure that is lost after normalization. What intelligence can you extract from format-specific markup BEFORE it disappears?

## What to Read

1. `engines/normalization/SPEC.md` — Full current SPEC. Understand what exists, what's thin, what's missing.
2. `reference/DOMAIN.md` — Refresh domain context. Pay special attention to: multi-layer text handling (sharh/matn), Arabic text fragility, structural conventions in Islamic scholarly texts.
3. `reference/ENTRY_EXAMPLE.md` — The target quality. What normalization intelligence would improve the final entry?
4. `engines/source/SPEC.md` §3 (output contract) and §4.B — Only the output contract and transformative capabilities. Understand what the normalization engine receives as input. The source engine's §4.B capabilities (KITAB profiling, edition comparison, difficulty prediction) set the bar for creative ambition.
5. Run `python3 scripts/extract_vision_sections.py 7.3` — Normalization engine vision section.

**Do NOT read:** VISION.md whole, kr_decisions.md, other engine SPECs beyond source. This is creative work — keep context fresh.

## Definition of Done

1. ≥3 new §4.B capabilities designed (each with: inputs, outputs, triggers, edge cases, worked examples with Arabic text)
2. Each §4.B capability passes the test: "Would a world-class Islamic scholar say 'I didn't know that was possible'?"
3. §4.A rules reviewed for completeness (but NOT precision-edited — save that for next session)
4. No [NOT YET IMPLEMENTED] markings removed (nothing is built yet)
5. `check_spec_quality.py` run — 0 HIGH defects
6. `creative_verification.py` run — must NOT show SECRETARY
7. NEXT.md written (for normalization engine PRECISION session)
8. SESSION_LOG.md updated
9. Committed and pushed

## Thinking Directions (from DEEP_REASONING_PROTOCOL)

- What structural intelligence can you extract from format-specific markup that would be lost after normalization?
- What can you infer about text quality during normalization?
- Shamela HTML has PageNumber spans, volume boundaries, footnote markers, section headers — what knowledge is encoded in these structures?
- Multi-layer texts (sharh quoting matn) have typographic conventions — bold for matn, regular for sharh. Can you detect and annotate these automatically?
- Arabic typesetting conventions encode scholarly signals: inline citations, hadith chains, Quranic verses have distinctive patterns. Can you tag these during normalization?

## Pending Owner Questions

- **API keys:** Will be needed when Claude Code starts implementation. Not blocking.
