# NEXT SESSION

**Written by:** Session 2026-03-06 (Claude Code environment setup)
**Date:** 2026-03-06

## Immediate Task

Begin Milestone 1 implementation: source engine + normalization engine (Shamela format) end-to-end.

Start with the **source engine** — specifically the Shamela intake path, since that's the format with existing ABD code and test data. The SPEC defines what to build; the ABD code is reference material only (D-019).

**Definition of done — this session is complete when:**
1. Source engine core module exists with Shamela intake: accepts a Shamela directory, freezes the raw files, extracts metadata, assigns source_id/work_id/canonical_id (D-024)
2. Three registries initialized: sources.json, works.json, scholars.json
3. Tests written and passing for Shamela intake path
4. Engine CLAUDE.md updated with accurate state

## Context

The preparatory phase is **complete**. All 14 SPECs written, cross-SPEC consistency verified, VISION.md at v1.2.0, Claude Code environment (.claude/) populated with settings, 7 commands, 3 agents. This is the first implementation session.

Milestone 1 target (from VISION.md §10.2): Source engine + normalization engine working end-to-end for Shamela format. One source in, normalized package out. This proves the Phase 1 pipeline.

## Files to Read — IN THIS ORDER

1. `engines/source/CLAUDE.md` — orientation (auto-loaded on directory entry).
2. `engines/source/SPEC.md` — the authoritative specification. READ FULLY before writing any code.
3. `reference/DOMAIN.md` — domain knowledge context (if not recently read).
4. ABD code for reference only: `engines/source/src/intake.py`, `engines/source/src/enrich.py`.
5. Existing tests: `engines/source/tests/` — understand what's tested today.
6. `schemas/SCHEMA_ANALYSIS.md` — notes on schema state.

**Do NOT read all 14 SPECs.** Only the source engine SPEC is needed for this session.

## Decisions Needed

- **Python packaging:** The current `_paths.py` approach works but won't scale. Decide whether to introduce `pyproject.toml` with package structure now or defer. (Recommendation: defer — get engines working first, refactor packaging after Milestone 1.)
- **Test data:** ABD tests reference Shamela data. Verify the test corpus is accessible. If not, the owner needs to provide sample Shamela directories or the test data needs to be committed (or use Git LFS).
- **API keys for LLM calls:** Source engine metadata enrichment uses LLM. Verify `.env` setup works. If not, ask the owner to configure keys.

## Pending Owner Questions

None currently. Implementation may surface domain questions about Shamela metadata fields.

## What This Session Did

Populated Claude Code environment for implementation phase:
- Rewrote root CLAUDE.md (62 lines, ≤100 limit, all §13.3.2 content categories).
- Refined `.claude/settings.json`: expanded permissions for implementation work, improved hooks.
- 7 slash commands: start-engine, run-tests, check-spec, read-vision (refined), validate-output, trace-pipeline, impl-status (new).
- 3 subagents: spec-reviewer (opus), test-runner (sonnet), integrity-checker (sonnet, new).
- Updated `_paths.py` to include user_model, scholar_authority, interface/scholar.
- Created missing src/ and tests/ directories for newer components.

## New Decisions

None. This session was infrastructure setup, not architectural design.
