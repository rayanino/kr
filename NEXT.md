# NEXT SESSION

**Written by:** Session 2026-03-05 (Claude Code environment setup)
**Date:** 2026-03-05

## Immediate Task

Begin shared/consensus SPEC — the highest-priority shared component. The consensus mechanism is used by excerpting (D-036), taxonomy (D-039), and potentially source and atomization engines.

**Definition of done — this session is complete when:**
1. shared/consensus/SPEC.md written with all 10 sections per SPEC template
2. RESOURCES.md updated with any new tools discovered during research
3. Any new decisions recorded in kr_decisions.md
4. Changes committed and pushed

## Context

All 7 engine SPECs are complete. Cross-SPEC verification done. VISION.md corrected to v1.1.0. Claude Code environment (.claude/) is now populated with agents, commands, hooks, and settings. The preparatory phase's remaining work is shared component SPECs (consensus, validation, feedback) and the first SCIENCE.md (إملاء for Milestone 1).

The consensus mechanism is referenced by multiple engine SPECs but has no standalone specification yet. Each engine SPEC describes how IT uses consensus, but the consensus component's own behavior — model selection, agreement thresholds, disagreement handling, configuration, error recovery — needs its own SPEC.

## Files to Read — IN THIS ORDER

1. `reference/DOMAIN.md` — domain context (if not recently read)
2. `shared/consensus/` — whatever exists (CLAUDE.md, any src/)
3. `engines/excerpting/SPEC.md` §6 — how excerpting uses consensus (D-036)
4. `engines/taxonomy/SPEC.md` §6 — how taxonomy uses consensus (D-039)
5. `engines/source/SPEC.md` §6 — how source uses consensus
6. `engines/atomization/SPEC.md` §6 — atomization's conscious decision NOT to use consensus
7. `VISION.md` §2.2 (consensus definition), §8 (quality architecture) — use extract_vision_sections.py
8. `reference/RESOURCES.md` — existing tool research

## Decisions Needed

- What LLM providers should the consensus mechanism support? (OpenRouter routing vs. direct provider APIs)
- Should consensus support async parallel calls or sequential with early termination?
- What's the minimum viable consensus configuration for Milestone 1?

## Pending Owner Questions

None.

## What This Session Did

Prepared the Claude Code implementation environment:
- Rewrote root CLAUDE.md per §13.3.2 (59 lines, pre/post work protocols, current priorities)
- Created .claude/settings.json with hooks (test-before-commit, test-before-push, SPEC-update reminder)
- Created 2 subagents (test-runner, spec-reviewer) and 4 slash commands (run-tests, check-spec, read-vision, start-engine)
- Trimmed 4 engine CLAUDE.md files to ≤50 lines per §13.3.3

## New Decisions

None this session (infrastructure setup only, no architectural decisions).
