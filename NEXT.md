# NEXT SESSION

## Session Type
IMPLEMENTATION_PREP (see SESSION_TYPES.md for full framework)

## Immediate Task

**Prepare the normalization engine for Claude Code implementation.** The normalization engine has completed the full SPEC refinement cycle: CREATIVE → PRECISION → HARDENING. The SPEC has 4 remaining HIGH defects (all MISSING_EXAMPLE for §4.A.3, §4.A.7, §4.B.2, §4.B.3 — these are for [NOT YET IMPLEMENTED] subsections and do not block implementation of the Shamela normalizer). The Shamela normalizer (§4.A.2) is fully specified with examples, error handling, and validated contracts.

## What to Read

1. `engines/normalization/SPEC.md` — **§4.A.1 (architecture), §4.A.2 (Shamela normalizer), §5 (validation), §7 (errors), §9 (current state).** These are the sections Claude Code needs for the Shamela normalizer upgrade.
2. `engines/normalization/contracts.py` — the Pydantic models Claude Code must use.
3. `engines/source/contracts.py` — the upstream contract (source metadata input).
4. `engines/normalization/src/` — the existing code that needs upgrading.

**Do NOT read:** VISION.md, CREATIVE_MANDATE.md, CHALLENGE_PROTOCOL.md, other engine SPECs.

## The IMPL_PREP Work (follow this sequence)

### Phase 1: Implementation order
Define which parts of the Shamela normalizer to build first. Recommended order:
1. Output schema upgrade (ABD JSONL → KR normalized package format)
2. §5 validation checks 1-9 (self-validation framework)
3. Footnote type classification (Pass 2 upgrade)
4. Multi-layer detection (Pass 5 — new capability)
5. Content flagging expansion (§4.A.9 — Quran/hadith detection)
6. Content census (§4.B.5 — post-processing statistics)

### Phase 2: Contract alignment verification
Verify source engine contracts.py → normalization contracts.py data flow. Ensure every field the normalization engine reads from source metadata exists in the source engine's output contract.

### Phase 3: Test fixtures
Verify existing test fixtures in `engines/normalization/tests/` cover the implementation order above. Identify which gold baselines are needed and whether they exist.

### Phase 4: Directory skeleton
Create the implementation directory structure Claude Code needs:
- Ensure `engines/normalization/src/` has the right module structure
- Create stub files for new modules (layer_detector.py, content_flagger.py, etc.)
- Create `engines/normalization/tests/test_kr_output.py` stub for new KR format tests

### Phase 5: Implementation brief
Write `engines/normalization/IMPL_BRIEF.md` — a concise document Claude Code reads to understand what to build, in what order, with what constraints.

## Definition of Done

1. Implementation order documented
2. Contract alignment verified (source → normalization data flow)
3. Test fixture gap analysis complete
4. Directory skeleton created
5. IMPL_BRIEF.md written for Claude Code
6. NEXT.md written (for first IMPLEMENTATION session on normalization engine)
7. SESSION_LOG.md updated
8. Committed and pushed

## What the Previous Sessions Did

Source engine complete (4 sessions): CREATIVE → PRECISION → HARDENING → IMPL_PREP.
Normalization engine session 1 (CREATIVE): 3 new §4.B capabilities (§4.B.5–§4.B.7).
Normalization engine session 2 (PRECISION): HIGH defects 46 → 6. 4 Arabic examples. Contracts updated.
Normalization engine session 3 (HARDENING, this session):
- 8 threat coverage gaps identified and patched across §4.A and §5.
- 6 new error codes, 3 new §5 validation checks, atomic write guarantee.
- 2 additional Arabic examples (§4.B.1, §4.B.4).
- Contracts expanded: 7 new FootnoteType values, 4 type-specific data models.
- HIGH defects: 6 → 4. Creative score: 90/100 maintained. SPEC: 1013 → 1073 lines.

## Pending Owner Questions

- **API keys:** Not needed for preparatory work. Will be needed when Claude Code starts implementation.
