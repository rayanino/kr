# NEXT SESSION

## Context

The owner conducted a comprehensive plan review (2026-03-07) with an external Claude Chat session. Key decisions:

1. **No standalone experiments.** Validation happens per-engine during the build cycle.
2. **Build in pipeline order.** Source engine first, not atomization.
3. **Per-engine cycle:** owner reviews SPEC → discuss comments → finalize → Claude Code builds → test (5a/5b/5c) → iterate.
4. **Skills-based workflow.** 6 custom Claude Chat skills will structure the per-engine work. Architecture designed but skills not yet written.
5. **Engine-specific expert roles.** Each engine project gets a detailed domain-specialist persona in custom instructions.
6. **The autonomous prep sessions are paused.** The owner is doing focused domain review.

## Immediate Task

**Write the 6 KR custom skills and set up the source engine Claude Chat project.**

Read `reference/SKILL_ARCHITECTURE_V2.md` for the full design. The 6 skills are:
- kr-spec-review (handle owner comments on SPECs)
- kr-finalize (consolidate changes, quality audit)
- kr-build-prep (prepare for Claude Code implementation)
- kr-evaluate (review test results across 5a/5b/5c)
- kr-research (creative exploration — the CREATIVE ENGINE)
- kr-integrity (quality and corruption audit)

Each skill needs: SKILL.md (under 500 lines), optional reference files for progressive disclosure.

After writing skills: set up the source engine project with engine-specific custom instructions (bibliographic + format specialist role from the architecture doc).

## Files to Read

1. `reference/SKILL_ARCHITECTURE_V2.md` — The skill architecture design (READ FIRST)
2. `reference/HONEST_PLAN.md` — The overall plan
3. `CREATIVE_MANDATE.md` — The creative protocol (kr-research skill must encode this)
4. `KNOWLEDGE_INTEGRITY.md` — The 7 threats (kr-integrity skill must reference these)
5. `SILENT_FAILURES.md` — The 7 deception patterns (kr-integrity skill must reference these)
6. `reference/DEEP_REASONING_PROTOCOL.md` — The Perfection Standard (kr-finalize must use this)
7. `STEERING.md` — Project context for custom instructions

Do NOT read: VISION.md, individual engine SPECs, kr_decisions.md, SESSION_LOG.md.

## Definition of Done

1. 6 skill .zip files produced and ready for upload
2. Source engine custom instructions written (bibliographic specialist role + universal mandates)
3. List of project knowledge files for source engine project
4. Skills tested mentally against real scenarios
5. Everything committed to repo under `skills/` directory

## Owner Status

- Currently reading source engine SPEC and writing numbered domain comments
- Has OpenRouter API key ready
- Will create the source engine Claude Chat project after skills are ready
