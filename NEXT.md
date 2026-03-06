# NEXT SESSION

## Session Type
HARDENING (see SESSION_TYPES.md for full framework)

## Immediate Task

**Atomization engine HARDENING session.** The SPEC has been through CREATIVE (5 §4.B capabilities) and PRECISION (15 defects fixed, contracts synchronized, error codes added). This session: verify no knowledge corruption paths, threat + failure analysis, edge case hardening.

## What to Read

1. `engines/atomization/SPEC.md` — the full SPEC. **Read this entire document.**
2. `engines/atomization/contracts.py` — verify contracts still match after any SPEC changes.
3. `KNOWLEDGE_INTEGRITY.md` — the full threat model. Every threat must be checked against atomization.
4. `reference/DOMAIN.md` §"What Failure Looks Like" → atomization section (L602, L645-648, L741-743) — verify all failure modes are defended.

**Do NOT read:** VISION.md, kr_decisions.md, source/normalization SPECs (unless needed for boundary verification).

## The HARDENING Work

### Threat Analysis Checklist
1. **Misattribution threat (L741):** A sharh quotes the matn author with "قال المصنف" — if atomization doesn't detect the layer transition, the matn author's words are attributed to the sharh author. Verify: §4.A.6 layer attribution + §4.A.7 commentary format + §4.B.2 implicit layer detection all defend against this. Look for gaps.
2. **Silent data loss:** What happens if the LLM drops atoms from the middle of a passage? The coverage check (V-1) should catch this. Walk through the scenario: LLM returns atoms covering positions [0,50) and [80,100) but skips [50,80). Does the coverage enforcement correctly absorb the gap? Or does it silently extend an atom to cover text it shouldn't contain?
3. **Confidence laundering (D-033):** An atom classified with low confidence (0.4) flows to the excerpting engine. Does the excerpting engine see the confidence? Verify the metadata pass-through chain.
4. **Footnote offset invariant (newly fixed):** Walk through a concrete scenario: passage with 2 footnotes, footnote 1 has 2 atoms, footnote 2 has 1 atom. Verify: V-1 correctly excludes footnotes, V-2 checks footnote atoms against footnote text, V-4 orders correctly, atom_ids are monotonic.
5. **Quran detection false positive:** A text uses Quranic language in a non-Quranic context. The rule-based detection marks it as quran_ayah with confidence ≥ 0.95. Verify the "unless" clause in §4.A.4 is adequate.
6. **Atom boundary in middle of Arabic word:** Can the LLM split a word? What prevents this? Is there a check?
7. **Unicode normalization edge cases:** Arabic text with NFC vs NFD forms. Combining characters. Does character offset counting handle these?

### Failure Scenario Walk-throughs
For each scenario, trace the complete path: input → processing → validation → error handling → output.

### Edge Cases to Verify
1. Passage with ONLY a heading and no content
2. Verse-format passage where verse_info disagrees with LLM detection
3. Commentary passage where ALL text is matn quotation (no sharh)
4. Passage where the LLM classifies every atom as "unclassified"
5. Passage with 100+ footnotes (scaling)
6. Single-character passage

## Definition of Done

1. Every threat from KNOWLEDGE_INTEGRITY.md applicable to atomization is addressed
2. Every failure scenario walk-through completed
3. Edge cases added to §10 test requirements where gaps found
4. SPEC fixes committed (with re-run of check_spec_quality.py)
5. NEXT.md written (for excerpting CREATIVE session)
6. SESSION_LOG.md updated
7. Committed and pushed

## What the Previous Sessions Did

Source engine: CREATIVE → PRECISION → HARDENING → IMPL_PREP (complete).
Normalization engine: CREATIVE → PRECISION → HARDENING → IMPL_PREP (complete).
Passaging engine: CREATIVE → PRECISION → HARDENING (complete).
Atomization engine: CREATIVE → **PRECISION (this session)** → HARDENING (next).

## Pending Owner Questions

- **API keys:** Will be needed when Claude Code starts implementation. Not blocking.
