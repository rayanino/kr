# NEXT SESSION

## Session Type
IMPLEMENTATION (see SESSION_TYPES.md for full framework)

## Immediate Task

**Atomization engine IMPLEMENTATION session — Phase 0 (foundation).** The atomization SPEC has completed all refinement phases and IMPLEMENTATION_PREP. Contracts verified (676L, 22 error codes, 15 review flags, 23 config params). 28 module stubs exist with SPEC docstrings. Build plan, test plan, and CLAUDE.md are ready.

Begin implementation following IMPLEMENTATION_ORDER.md Phase 0: errors.py → config.py → loader.py.

## What to Read

1. `engines/atomization/CLAUDE.md` — Engine orientation (read FIRST — it gives the full picture).
2. `engines/atomization/IMPLEMENTATION_ORDER.md` — Build plan. Follow Phase 0 strictly.
3. `engines/atomization/SPEC.md §2` (lines 34–63) — Input contract for loader.py.
4. `engines/atomization/SPEC.md §7` (lines 1027–1058) — Error handling for errors.py.
5. `engines/atomization/SPEC.md §8` (lines 1062–1100) — Configuration for config.py.
6. `engines/atomization/contracts.py` — All Pydantic models (676 lines).
7. `engines/passaging/src/errors.py` and `engines/passaging/src/config.py` — Reference implementations from passaging engine.

**Do NOT read:** VISION.md, kr_decisions.md, CREATIVE_MANDATE.md, other engine SPECs.

## Definition of Done

1. `engines/atomization/src/errors.py` implemented: structured logging to atomization_log.jsonl, error severity dispatch, source status update for fatal errors.
2. `engines/atomization/src/config.py` implemented: AtomizationConfig loading from defaults, per-science override stub.
3. `engines/atomization/src/loader.py` implemented: reads passages.jsonl, runs all 5 input validation checks (§2), NFC normalization safety net.
4. Tests for loader.py: all 5 validation checks tested (§10.9 test cases), NFC test (§10.18).
5. `check_spec_quality.py` shows no regression from 20 defects.
6. All code passes `python -m pytest engines/atomization/tests/ -q`.
7. NEXT.md written (pointing to Phase 1–2: prescreen + predetection + LLM atomizer).
8. SESSION_LOG.md updated.
9. Committed and pushed.

## Notes for Next Architect

- The contracts.py is complete — use `AtomizationErrorCode`, `ERROR_SEVERITY`, `AtomizationConfig`, and `ReviewFlag` directly. Do not redefine.
- errors.py should write to `library/sources/{source_id}/atoms/atomization_log.jsonl` as structured JSONL (timestamp, error_code, passage_id, atom_id, details, recovery).
- loader.py reads from `library/sources/{source_id}/passages/passages.jsonl`. Use the passaging engine's PassageRecord model from `engines/passaging/contracts.py` to parse input.
- NFC normalization (§2 step 5): normalize the in-memory copy only, never modify the on-disk file. Use `unicodedata.normalize('NFC', text)` — no external dependency needed.
- The passaging engine's loader.py (`engines/passaging/src/loader.py`) is the closest reference implementation, but it's also a stub. Use the passaging contracts for the input schema.
- Gold test fixtures do not exist yet. Tests for Phase 0 should use synthetic passages (created in the test files). Real gold fixtures will be needed from Phase 2 onward.

## Pending Owner Questions

- **API keys:** Will be needed when LLM-based modules (Phase 2+) start. Not blocking Phase 0.
