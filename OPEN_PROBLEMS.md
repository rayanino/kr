# Open Problems — المشاكل المفتوحة

Last updated: 2026-03-07

## The Principle

Build → Test → Learn → Fix. Not: Research → Research → Research → Build.

The previous version of this file had 12 tasks across 4 weeks before the engine cycle could start. That's the same over-planning trap that produced 38 markdown files and zero running code in this repo. Deleted.

---

## What You Should Do RIGHT NOW

**Start the engine cycle for the source engine.** You're already in Phase 1 (reading the SPEC). When you finish your comments, move to Phase 2. Don't wait for anything else.

### Setup (15 minutes, one time)

1. Go to Settings > Capabilities > Enable **Code execution and file creation**
2. Go to Customize > Skills > Upload all 6 `kr-*.zip` files from `skills/` > Toggle them ON
3. Create a new project called "Source Engine — محرك المصادر"
4. In the project, add knowledge from GitHub:
   - Click "+" > Add from GitHub > connect to `rayanino/kr`
   - Select: `engines/source/`, `STEERING.md`, `KNOWLEDGE_INTEGRITY.md`, `SILENT_FAILURES.md`, `reference/DOMAIN.md`, `reference/ENTRY_EXAMPLE.md`, `reference/DEEP_REASONING_PROTOCOL.md`, `skills/shared/`, `NEXT.md`
5. Paste the custom instructions from `skills/source-engine-project/custom_instructions_v2.md`
6. Keep `Github_key` as a fallback knowledge file
7. Start a chat: "I have comments on the source engine SPEC. Use kr-spec-review."

That's it. You're in Phase 2.

---

## Three Research Problems (Do In Parallel With Phases 2-4)

While you're resolving comments on the source engine SPEC (which will take days to weeks), these three problems need to be solved so that Phase 5 and 6 are ready when you get there. Each is ONE deep-research chat.

### Problem 1: Claude Code Build Environment

**When to do it:** Any time during Phases 2-4. Not urgent until Phase 5.

**The question:** What is the optimal Claude Code setup for building and testing a KR engine?

**What the chat should cover:**
- CLAUDE.md design: what goes in (under 200 lines), what goes in docs/, what's wasted space
- Agent team compositions: when to use them, templates for builder/tester/reviewer
- Hooks and slash commands that improve build quality
- Session management: /compact, fresh sessions, handoff between sessions
- Memory persistence across sessions (what tools exist, what works)
- Cost management: Opus vs Sonnet per role, token budgeting
- The specific Python + Pydantic + pytest patterns that work well with Claude Code

**Output:** The complete Claude Code environment design for the source engine. Everything Claude Code needs to start building.

**Start the chat with:** "Clone the repo. Read `reference/RESEARCH_LOG.md` (findings 01, 05, 08), `reference/HONEST_PLAN.md`, and `skills/kr-build-prep/SKILL.md`. Then do deep research into Claude Code environments for complex Python projects. The goal is to produce the actual CLAUDE.md and supporting files for the source engine build."

---

### Problem 2: Testing Architecture

**When to do it:** Any time during Phases 2-4. Must be done before Phase 5.

**The question:** How exactly do we test each engine, store results, and establish trust?

**What the chat should cover:**
- 5a deterministic tests: what checks per engine, how to structure them, framework choice
- 5b LLM-as-worker isolation: how to test each engine's internal LLM calls independently, accuracy thresholds, what to do when they fail
- 5c LLM-as-evaluator: which models evaluate, what prompts/rubrics, how to measure evaluator reliability, whether this becomes an inter-engine production gate
- Test result storage format: directory structure, file format, what Claude Chat needs to see for kr-evaluate
- Regression strategy: how to prevent fixes from breaking working things
- Gold baselines: what ground truth the owner needs to provide, how to create it
- Trust graduation: concrete criteria for "this engine is trusted"
- How all of this works for the source engine specifically (first real test case)

**Output:** The testing framework design. Concrete enough that kr-build-prep can set up the test infrastructure during Phase 5.

**Start the chat with:** "Clone the repo. Read `reference/HONEST_PLAN.md` (the 5a/5b/5c framework and per-engine test specs), `reference/JUDGE_PANEL_ARCHITECTURE.md`, `reference/RESEARCH_LOG.md` (findings 02, 03, 11), and `skills/kr-evaluate/SKILL.md`. Then do deep research into testing architectures for multi-stage LLM pipelines. The goal is to produce the complete testing framework for KR, starting with the source engine."

---

### Problem 3: Repo Cleanup

**When to do it:** Low priority. Do it when you have a spare chat and want a break from SPEC work.

**The question:** Which files in this repo matter, which are junk, and what's the clean structure?

**Why it's low priority:** The repo mess doesn't block the engine cycle. Claude reads what the project knowledge tells it to. The 38 files are ugly but harmless — they sit in root and reference/ and nobody references them. The cleanup can happen any time.

**What the chat should cover:**
- Audit every .md file in root (22 files) and reference/ (16 files)
- For each: KEEP / ARCHIVE / DELETE, with reasoning
- Identify any file whose content should be merged into another
- Propose a clean directory structure
- Execute the cleanup (move, merge, delete)
- Update any cross-references in surviving files

**Start the chat with:** "Clone the repo. Read every .md file at the root level and in reference/. Many are artifacts from autonomous over-planning sessions. Audit each one: is it still needed, does it duplicate another file, should it be archived? Then execute the cleanup."

---

## Status

| Item | Status | Notes |
|------|--------|-------|
| Skills uploaded | TODO | Owner action: upload 6 zips to Customize > Skills |
| Code execution enabled | TODO | Owner action: Settings > Capabilities |
| Source engine project created | TODO | Owner action: follow setup steps above |
| Phase 1 (read SPEC) | IN PROGRESS | Owner is reading source engine SPEC |
| Phase 2 (comment resolution) | BLOCKED | Waiting on project setup |
| Problem 1 (Claude Code env) | TODO | One deep-research chat |
| Problem 2 (testing architecture) | TODO | One deep-research chat |
| Problem 3 (repo cleanup) | TODO | Low priority, any time |

---

## Files That Matter (Ignore Everything Else)

If you're lost in the repo, these are the files that actually drive the work:

**Your daily files:**
- `OPEN_PROBLEMS.md` — this file, your roadmap
- `skills/shared/ENGINE_PROTOCOL.md` — the 6-phase process per engine
- `engines/source/SPEC.md` — the source engine specification (what you're reading now)

**Claude's reference files (loaded via project knowledge):**
- `STEERING.md` — project overview
- `KNOWLEDGE_INTEGRITY.md` — 7 corruption threats
- `SILENT_FAILURES.md` — 7 silent failure patterns
- `reference/DEEP_REASONING_PROTOCOL.md` — quality standard
- `reference/DOMAIN.md` — Islamic studies domain knowledge
- `reference/ENTRY_EXAMPLE.md` — target output quality
- `reference/HONEST_PLAN.md` — the real plan (anti-over-planning)

**Everything else** is either archived session history, superseded plans, or infrastructure that Claude reads on demand. You don't need to track it.
