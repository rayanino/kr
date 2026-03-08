# NEXT SESSION

## Context
The testing framework is complete: `reference/TESTING_FRAMEWORK.md` (~650 lines).
It defines DeepEval + pytest as the test stack, the 5a/5b/5c test patterns for every engine,
gold baseline format with tolerances, trust graduation thresholds, and the full source engine
test plan with concrete code examples.

## What the Owner Needs to Do (Before Next Session)

1. **Set up the source engine project** — follow the steps in OPEN_PROBLEMS.md "What You Should Do RIGHT NOW"
2. **Create .env file** — copy `.env.template` to `.env`, fill in API keys from project knowledge files
3. **Continue reading the source engine SPEC** (Phase 1) — write comments in `engines/source/owner-comments.md`

## What the Next Session Should Do

**If the owner has SPEC comments ready:** Start Phase 2 (comment resolution) in the source engine project.

**If the owner is still reading:** Tackle Problem 2 from OPEN_PROBLEMS.md — Claude Code Build Environment. Read `reference/TESTING_FRAMEWORK.md`, `skills/kr-build-prep/SKILL.md`, and `engines/source/SPEC.md`. Produce the Claude Code environment files listed in OPEN_PROBLEMS.md Problem 2.

**Files to read:** `OPEN_PROBLEMS.md` (roadmap), `reference/TESTING_FRAMEWORK.md` (just completed).
