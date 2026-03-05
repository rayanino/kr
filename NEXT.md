# NEXT SESSION

**Written by:** Session 2026-03-05 (cross-SPEC verification + VISION corrections)
**Date:** 2026-03-05

## Immediate Task

Prepare the Claude Code implementation environment: populate the `.claude/` directory and rewrite the root CLAUDE.md for implementation phase.

**Definition of done — this session is complete when ALL of these are true:**
1. Root CLAUDE.md rewritten per §13.3.2 requirements (≤100 lines, implementation-focused)
2. `.claude/settings.json` created with hook configurations
3. `.claude/commands/` populated with slash commands for common workflows
4. `.claude/agents/` populated with subagent definitions (at minimum: a test-runner agent, a review agent)
5. All engine CLAUDE.md files verified consistent with their SPECs (spot check — update if stale)
6. All changes committed and pushed

**Optional if time permits:**
- Begin shared/consensus SPEC (highest-priority shared component — used by excerpting and taxonomy engines)
- Begin إملاء SCIENCE.md (first Level 3 doc, needed for Milestone 1)

## Context

All 7 engine SPECs are complete. Cross-SPEC consistency verified. VISION.md corrected to v1.1.0. The preparatory phase's SPEC work is done. The next logical step is setting up the implementation environment so Claude Code can begin building.

The `.claude/` directory is currently empty. Per §13.2.2 and §13.5, it needs:
- Agent definitions for specialized tasks
- Slash commands for common operations
- Hook configurations for mechanical rule enforcement
- settings.json for permissions

The root CLAUDE.md needs to be rewritten from its current state (ABD-era) to conform to §13.3.2's strict requirements: ≤100 lines, identity + repo map + pipeline summary + pre/post-work protocols + architectural constraints + current priorities. No engine-specific content.

## Files to Read — IN THIS ORDER

1. `VISION.md` §13.2.2, §13.3.2, §13.3.3, §13.5 (use extract_vision_sections.py 13)
2. `CLAUDE.md` (current root CLAUDE.md — to understand what exists before rewriting)
3. `engines/source/CLAUDE.md` (example of current engine CLAUDE.md format)
4. Any one other engine CLAUDE.md (for consistency check)

## Decisions Needed

- What specific hooks are most valuable for Milestone 1? (pre-commit test runner? schema validator?)
- What slash commands would save the most time? (run-all-tests? validate-schema? lint-spec?)
- What subagents are needed for Milestone 1 vs. later milestones?

## Pending Owner Questions

None.

## What This Session Did

Cross-SPEC consistency verification across all 7 engines. Found and fixed one inconsistency: excerpting SPEC listed `primary` as a `source_layer` value not produced by atomization. VISION.md corrections: resolved §6.4 OPEN QUESTION with D-040 text. Rewrote §10.3 and §12 to align with D-019 (ABD legacy zero authority). Updated §13.2.6 library directory structure and repo layout tree to match source engine SPEC's per-source directory model and `library/registries/` structure. Updated §2 glossary: "Atom" (now reflects persistence), "Work" (now reflects three-tier identity model with work relationships). Updated SCHEMA_ANALYSIS.md. Updated STATUS.md to reflect all SPECs complete.

## New Decisions

None this session (corrections only, no new architectural decisions).
