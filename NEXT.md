# NEXT SESSION

**Written by:** Session 2026-03-06 (Autonomous system enhancement — Claude Chat)
**Date:** 2026-03-06

## Immediate Task

Begin Milestone 1 implementation: source engine + normalization engine (Shamela format) end-to-end.

Start with **M1.1 — Source Engine: Data Models and Identity** (see MILESTONES.md for detailed task breakdown).

**Definition of done — this session is complete when:**
1. Source metadata dataclass defined matching SPEC §3 output contract
2. Three-tier identity model implemented: `source_id`, `work_id`, `canonical_id` (D-024)
3. Registry structures created: `sources.json`, `works.json`, `scholars.json`
4. Tests written and passing for identity generation and registry operations
5. Engine CLAUDE.md updated with accurate state

## Context

The preparatory phase is **complete**. All 14 SPECs written, cross-SPEC consistency verified, VISION.md at v1.2.0, Claude Code environment populated.

**New this session:** The autonomous system has been significantly enhanced:
- `ORCHESTRATOR.md` — Implementation session lifecycle protocol (Orient → Plan → Build → Verify → Handoff)
- `MILESTONES.md` — Detailed task decomposition for all milestones with dependencies and acceptance criteria
- `REVIEW_PROTOCOL.md` — 5 structured review types for design critique sessions
- 4 new agents: `implementation-planner`, `code-reviewer`, `integration-tester`, `design-critic`
- 4 new commands: `plan-implementation`, `verify-boundaries`, `design-review`, `milestone-status`, `generate-test-plan`
- 3 new scripts: `decompose_spec.py`, `verify_metadata_flow.py`, `check_compliance.py`
- Enhanced hooks: pre-commit reminder for source file changes, SPEC/schema modification alerts
- `tests/integration/` directory created for cross-engine integration tests
- Updated `PROJECT_INSTRUCTIONS.md` with implementation and review phase protocols
- Updated `CLAUDE.md` repo map and priorities

**Follow `ORCHESTRATOR.md` for the implementation session lifecycle.**

## Files to Read — IN THIS ORDER

1. `ORCHESTRATOR.md` — implementation session protocol (NEW — read this first)
2. `MILESTONES.md` §M1.1 — the specific task decomposition for this session
3. `engines/source/CLAUDE.md` — orientation
4. `engines/source/SPEC.md` §1-§4.A.1 — identity model specification
5. `engines/source/SPEC.md` §3 — output contract (for dataclass design)
6. `schemas/source_metadata.json` — current (ABD-era) schema for reference

**Do NOT read:** VISION.md, DOMAIN.md, other engine SPECs, kr_decisions.md (not needed for this task).

## Implementation Notes

- ABD-era code in `engines/source/src/` has zero design authority (D-019). Read it for implementation knowledge but implement from the SPEC.
- The existing tests in `engines/source/tests/` are ABD-era. New KR tests should be in new files (e.g., `test_identity.py`, `test_registry.py`).
- Python packaging is `_paths.py` for now. Use it for imports. Defer pyproject.toml.
- For LLM calls needed in later tasks (M1.3), `.env` must have API keys. If missing, note as blocked.

## Blocked Items

- **Test data:** Verify sample Shamela directories are accessible. If not, ask owner to provide.
- **API keys:** Needed for M1.3 (metadata enrichment). Not needed for M1.1 or M1.2.

## Pending Owner Questions

None currently.

## What This Session Did

Enhanced the autonomous system with implementation orchestration (ORCHESTRATOR.md, MILESTONES.md), design review protocol (REVIEW_PROTOCOL.md), 4 new agents, 4 new commands, 3 automation scripts, enhanced hooks, and updated project instructions. Created the infrastructure for Claude Code to work autonomously through the implementation phase and for Claude Chat to run structured design reviews.

## New Decisions

None. This session was infrastructure enhancement, not architectural design.
