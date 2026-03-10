# NEXT — Prepare Source Engine Session 6

**Status:** Sessions 1–5b COMPLETE. 503 tests passing. All modules built except engine.py (orchestrator), logger.py, and error path testing.

**Task:** Use kr-build-prep to produce the Session 6 NEXT.md for Claude Code.

## What Exists

- `engines/source/session-6-plan.md` — the Session 6 scope (written during planning, needs build-prep treatment)
- `engines/source/TESTING_PROTOCOL.md` — post-build validation plan (Phase A–E, for after Session 6)
- `engines/source/docs/session5-contracts-audit.md` — known SPEC defects (4 misalignments, all resolved in code but SPEC text is locked)
- 503 passing tests across 14 test files

## What Session 6 Builds

1. `engine.py` — full pipeline orchestrator (Steps 1→9)
2. `logger.py` — structured JSONL logging with SourceError serialization
3. `config.py` — may need extension for missing parameters
4. Error path testing — exercise every §7 error code that can fire
5. Full pipeline run on ALL 13 fixtures
6. Plain text end-to-end (alfiyyah_versified)
7. Source → Normalization boundary verification
8. Step 4 blocking conditions verification

## Known Issues to Account For

1. **Trust evaluator uses validated formula, not SPEC text.** The SPEC §4.A.8 author_standing requires "prior sources" for the 0.90 classical tier, but the validated formula (13/13 correct) uses only death_date. See trust_evaluator.py module docstring and session5-contracts-audit.md Misalignment 3.

2. **TRANSLIT_MAP SPEC defect.** SPEC §4.A.1 says إ → 'a'. Implementation correctly uses إ → 'i'. Do not "fix" to match SPEC.

3. **LLM calls needed.** Session 6 runs the full pipeline including Step 4 (inference + consensus). API keys: ANTHROPIC_API_KEY, OPENROUTER_API_KEY. Cost estimate: ~$1-2 for 13 fixtures × 2 models.

## Build-Prep Deliverables Expected

Per the kr-build-prep skill: technology survey (check if any new deps needed for engine.py/logger.py), contracts audit (verify engine.py input/output matches contracts), NEXT.md for Claude Code, test specifications.
