# NEXT SESSION

**Written by:** Session 2026-03-06 (Cross-SPEC verification + VISION corrections)
**Date:** 2026-03-06

## Immediate Task

Claude Code environment setup: populate `.claude/` directory and rewrite root CLAUDE.md for the implementation phase.

**Definition of done — this session is complete when:**
1. Root CLAUDE.md rewritten to conform to §13.3.2 requirements (≤100 lines, implementation-focused)
2. `.claude/settings.json` populated with at minimum: permission settings, any initial hooks
3. `.claude/commands/` populated with at least core slash commands for common implementation workflows
4. `.claude/agents/` populated with at least one subagent definition (if useful subagents are identified)
5. Optionally: إملاء SCIENCE.md started (minimal Level 3 doc for first science, needed for Milestone 1)
6. Changes committed and pushed

## Context

The preparatory phase is nearly complete. All 14 SPECs are written and verified:
- 7 engines: source (582L), normalization (664L), passaging (502L), atomization (580L), excerpting (559L), taxonomy (562L), synthesizing (582L)
- 6 shared components: consensus (405L), validation (406L), human_gate (413L), feedback (461L), user_model (368L), scholar_authority (462L)
- 1 interface: scholar (872L)

Cross-SPEC consistency has been verified across all 14 boundaries. VISION.md has been updated to v1.2.0 with cross-cutting corrections (§8, §9, §11, §13.2).

The last preparatory work is setting up the Claude Code development environment. This is critical infrastructure — Claude Code sessions will use the root CLAUDE.md, slash commands, and hooks on every implementation session.

## Files to Read — IN THIS ORDER

1. `VISION.md` §13.3 (Agent Context Engineering) and §13.5 (Agent Infrastructure) — these define the requirements for the .claude/ directory and root CLAUDE.md. Use: `python3 scripts/extract_vision_sections.py 13` and read §13.3 and §13.5.
2. Root `CLAUDE.md` — the current version, to understand what exists before rewriting.
3. The archived roadmap `reference/archive/kr_definitive_roadmap_v2.md` — has a section on .claude/ setup. Read only that section (search for ".claude" or "agents").
4. `STATUS.md` — for current project state to include in the CLAUDE.md.

**Context budget note:** This task is lighter than SPEC writing. No need to read all 14 SPECs. The .claude/ work is infrastructure setup, not deep architectural design. Budget should be ample.

## Decisions Needed

- **Which slash commands?** §13.5.3 says commands are created incrementally. But some are obvious for implementation: "run all tests", "validate schemas", "run engine pipeline", "check documentation consistency." Decide which commands to create now vs. which to create during implementation.
- **Which hooks?** §13.5.2 says hooks enforce rules mechanically. Obvious candidates: pre-commit hook to run tests, post-edit hook to validate schemas. Decide which hooks are worth creating before any implementation code exists.
- **Subagents?** §13.5.1 lists anticipated subagents (research, review, integrity). Decide if any are worth creating now or if they should wait for implementation experience.
- **Root CLAUDE.md content.** §13.3.2 prescribes exactly what must be in it (identity, repo map, pipeline summary, pre/post-work protocols, architectural constraints, current priorities). The current CLAUDE.md may need a complete rewrite.

## Pending Owner Questions

None.

## What This Session Did

Completed cross-SPEC consistency verification across all 14 SPECs and VISION.md. Verified all engine-to-engine boundaries (field-level check), shared component integration patterns, and terminology coherence. Found one minor gap (taxonomy provenance list missing `school_confidence`) — fixed. Applied VISION.md cross-cutting corrections: §8 (referenced actual component SPECs, added D-033), §9 (referenced human_gate SPEC), §11 (added Principles 13-15 for D-018, D-033, D-023), §13.2 (updated repo layout tree and directory descriptions for all 14 components including interface/). Updated VISION.md to v1.2.0. Updated STATUS.md.

## New Decisions

None this session. (All changes were corrections and extensions of existing decisions, not new architectural decisions.)
