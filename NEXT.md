# NEXT SESSION

**Written by:** Session 2026-03-06 (Autonomous system hardening — Claude Chat)
**Date:** 2026-03-06

## Immediate Task

Begin Milestone 1 implementation: source engine + normalization engine (Shamela format) end-to-end.

Start with **M1.1 — Source Engine: Data Models and Identity** (see MILESTONES.md for detailed task breakdown).

**Definition of done — this session is complete when:**
1. Source metadata dataclass defined matching SPEC §3 output contract
2. Three-tier identity model implemented: `source_id`, `work_id`, `canonical_id` (D-024)
3. Registry structures created: `sources.json`, `works.json`, `scholars.json`
4. Tests written and passing for identity generation and registry operations
5. Tests include Arabic text handling verification (real Arabic, not placeholders)
6. Engine CLAUDE.md updated with accurate state
7. Three Challenges completed before commit (CHALLENGE_PROTOCOL.md)

## Context

The preparatory phase is **complete**. All 14 SPECs written, cross-SPEC consistency verified, VISION.md at v1.2.0, Claude Code environment populated.

**CRITICAL: New protocols added this session — read these FIRST:**
- `KNOWLEDGE_INTEGRITY.md` — 7-threat model for knowledge safety. EVERY implementation session must check against these threats.
- `CHALLENGE_PROTOCOL.md` — Three Challenges (Hostile Implementer, Skeptical Scholar, Technology Maximalist) + quality gates + anti-pattern detection. Run before EVERY commit.
- `.claude/skills/arabic-text/SKILL.md` — Arabic text handling rules. Read before ANY code that touches Arabic text.
- `.claude/skills/knowledge-safety/SKILL.md` — Knowledge safety review checklist. Use when implementing processing logic.
- `.claude/skills/technology-survey/SKILL.md` — Technology survey protocol. Check BEFORE building custom code.
- `.claude/skills/scholarly-design/SKILL.md` — Transformative feature evaluation. Use for §4.B capabilities.

**Additional infrastructure (from previous enhancement session):**
- `ORCHESTRATOR.md` — Implementation session lifecycle (Orient → Plan → Build → Verify → Handoff)
- `MILESTONES.md` — Detailed task decomposition with dependencies and acceptance criteria
- `REVIEW_PROTOCOL.md` — 5 structured review types for design critique sessions
- 7 agents total: spec-reviewer, test-runner, integrity-checker, implementation-planner, code-reviewer, integration-tester, design-critic
- 12 commands total including: challenge, plan-implementation, verify-boundaries, design-review, milestone-status, generate-test-plan
- 3 scripts: decompose_spec.py, verify_metadata_flow.py, check_compliance.py
- Enhanced hooks: SessionStart (post-compaction context injection), PreToolUse (commit checks), PostToolUse (knowledge safety reminders)

**Follow `ORCHESTRATOR.md` for the implementation session lifecycle.**

## Files to Read — IN THIS ORDER

1. `ORCHESTRATOR.md` — implementation session protocol
2. `KNOWLEDGE_INTEGRITY.md` — threat model (NEW — critical)
3. `CHALLENGE_PROTOCOL.md` — quality gates (NEW — critical)
4. `.claude/skills/arabic-text/SKILL.md` — Arabic text handling (NEW)
5. `MILESTONES.md` §M1.1 — the specific task decomposition
6. `engines/source/CLAUDE.md` — orientation
7. `engines/source/SPEC.md` §1-§4.A.1 — identity model specification
8. `engines/source/SPEC.md` §3 — output contract (for dataclass design)

**Do NOT read:** VISION.md, DOMAIN.md, other engine SPECs, kr_decisions.md (not needed for M1.1).

## Implementation Notes

- ABD-era code in `engines/source/src/` has zero design authority (D-019). Read for implementation knowledge but implement from the SPEC.
- Existing tests in `engines/source/tests/` are ABD-era. New KR tests in new files (e.g., `test_identity.py`, `test_registry.py`).
- Python packaging is `_paths.py` for now. Defer pyproject.toml.
- ALL test data must use real Arabic text — see .claude/skills/arabic-text/SKILL.md.
- Source ID generation uses SHA-256 of frozen source. Ensure correct encoding handling.

## Blocked Items

- **Test data:** Verify sample Shamela directories are accessible. If not, ask owner to provide.
- **API keys:** Needed for M1.3 (metadata enrichment). Not needed for M1.1 or M1.2.

## Pending Owner Questions

None currently.

## What This Session Did

Hardened the autonomous system with knowledge integrity protocol (7-threat model), challenge protocol (Three Challenges + quality gates + anti-patterns), 4 Claude Code skills (knowledge-safety, arabic-text, technology-survey, scholarly-design), enhanced hooks (SessionStart compaction context, pre-commit checks), challenge command, and significantly strengthened self-review and session workflow in PROJECT_INSTRUCTIONS.md.

## New Decisions

None. This session was infrastructure hardening, not architectural design.
