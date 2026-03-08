# Open Problems — المشاكل المفتوحة

Last updated: 2026-03-07 (v2 — final planning session)

## The Principle

Build → Test → Learn → Fix. Not: Research → Research → Research → Build.

---

## What You Should Do RIGHT NOW

**Start the engine cycle for the source engine.** You're already in Phase 1 (reading the SPEC). When you finish your comments, move to Phase 2. Don't wait for anything else.

### Setup (15 minutes, one time)

**Step 1 — Enable capabilities:**
- Go to Settings > Capabilities > Enable **Code execution and file creation**

**Step 2 — Upload skills:**
- Go to Customize > Skills > Upload all 6 `.zip` files from `skills/` > Toggle them ON
- The 6 zips: `kr-spec-review.zip`, `kr-integrity.zip`, `kr-finalize.zip`, `kr-build-prep.zip`, `kr-evaluate.zip`, `kr-research.zip`
- Test activation: in any chat, say "use kr-research" — if Claude says "Using kr-research" in its thinking, skills work

**Step 3 — Create the source engine project:**
1. Create a new project called "Source Engine — محرك المصادر"
2. Add knowledge from GitHub:
   - Click "+" > Add from GitHub > connect to `rayanino/kr`
   - Select: `engines/source/`, `STEERING.md`, `KNOWLEDGE_INTEGRITY.md`, `SILENT_FAILURES.md`, `reference/DOMAIN.md`, `reference/ENTRY_EXAMPLE.md`, `reference/DEEP_REASONING_PROTOCOL.md`, `skills/shared/`, `NEXT.md`
3. Paste the custom instructions from `skills/engine-project-template/source.md`
4. Keep `Github_key` as a fallback knowledge file
5. Start a chat: "I have comments on the source engine SPEC. Use kr-spec-review."

**Step 4 — Set up API keys (5 minutes, needed before Phase 5):**
You already have the keys in this project's knowledge files. Create the `.env` file:
1. Copy `.env.template` to `.env` in the repo root
2. Fill in from your project knowledge files:
   - `ANTHROPIC_API_KEY=` (from Anthropic_API_key file)
   - `OPENAI_API_KEY=` (from OpenAI_Api_Key file)
   - `MISTRAL_API_KEY=` (from Mistral_Api_Key file)
3. This isn't urgent for Phases 1-4 (SPEC work uses no code), but must be done before Phase 5

That's it. You're ready for Phase 2.

---

## When GitHub Sync Fails (Fallback)

If Claude says it can't access repo files, tell it: "Clone the repo using the Github_key file." Claude will:
1. Read the Github_key from project knowledge
2. Run `git clone` with that token
3. Access files from the local clone

This happened during a multi-week outage in late 2025. Rare, but the fallback works.

---

## Two Research Problems (Do During Phases 2-4)

While you're resolving comments on the source engine SPEC, these two problems should be solved so that Phase 5 and 6 are ready. Each is ONE deep-research chat.

### Problem 1: Testing Architecture (HIGHEST PRIORITY)

**When to do it:** During Phases 2-3. Must be done before Phase 5.

**Why it's the top priority:** This is the problem that determines whether you can TRUST an engine's output. Without a concrete testing framework, Phase 6 ("build, test, evaluate") becomes improvised. The 5a/5b/5c framework in ENGINE_PROTOCOL.md is a good conceptual model, but it needs to be turned into real test infrastructure.

**The question:** What exactly does the test suite look like for each engine, and how do results flow from Claude Code to Claude Chat?

**What the chat should investigate:**

*Framework choice:*
- DeepEval (pytest-native, LLM-as-judge metrics, component-level evaluation) — evaluate whether it fits KR's needs
- Plain pytest + custom evaluation scripts — evaluate whether the simplicity is worth the trade-off
- How to run LLM evaluation using the API keys you already have (Anthropic, OpenAI, Mistral) rather than OpenRouter

*Per-dimension design:*
- 5a deterministic: concrete pytest fixtures per engine. What checks, what assertions, what schema validation (Pydantic models already exist)
- 5b LLM-as-worker: how to isolate and test each LLM call inside an engine independently. What prompts to use, accuracy thresholds, what happens when accuracy is below threshold
- 5c LLM-as-evaluator: which model evaluates (a different one from the engine's own), what rubric, how to measure evaluator reliability. Research whether DeepEval's GEval or faithfulness metrics can handle Arabic

*Test result storage:*
- Directory structure: `engines/{engine}/test-results/{run-id}/`
- File format for results (JSON? pytest report? both?)
- What Claude Chat's kr-evaluate skill needs to see to do its analysis

*Gold baselines:*
- What the owner needs to hand-verify for the source engine (specific: which fixtures, which fields)
- Format for gold baselines: `engines/{engine}/gold/{fixture-name}.json`
- How many gold baselines are enough for the first engine (estimate: 2-3 fixtures)

*Trust graduation criteria:*
- Level 0-4 from ENGINE_PROTOCOL.md — make these measurable. What metric values define each level?

*Source engine specific:*
- What are the 5a checks for the source engine specifically?
- What LLM calls does the source engine make (metadata enrichment: science classification, author identification, trust scoring)?
- What should 5b test for each of those calls?
- What should 5c evaluate about the source engine's complete output?

**Output:** A testing framework design document (~500-800 lines) stored at `reference/TESTING_FRAMEWORK.md`. Concrete enough that kr-build-prep can set up the test infrastructure during Phase 5. Should include:
1. Framework decision (DeepEval vs. custom)
2. Directory structure
3. Gold baseline format with 1 worked example
4. Per-dimension test templates
5. Source-engine-specific test plan
6. Trust graduation thresholds

**Done condition:** A new developer (Claude Code) reading the document can set up the test infrastructure and write tests with zero clarifying questions.

**Start the chat with:** "Clone the repo. Read `skills/shared/ENGINE_PROTOCOL.md` (Phase 6 section), `reference/HONEST_PLAN.md` (the 5a/5b/5c framework), `reference/JUDGE_PANEL_ARCHITECTURE.md`, `skills/kr-evaluate/SKILL.md`, and `engines/source/SPEC.md` §5 and §10. Then do deep research into: (1) DeepEval as a testing framework for Arabic NLP pipelines, (2) pytest patterns for LLM evaluation, (3) gold baseline creation for multi-stage pipelines. The goal is to produce the complete testing framework for KR."

---

### Problem 2: Claude Code Build Environment (DO RIGHT BEFORE PHASE 5)

**When to do it:** After Phase 4 (SPEC finalized), before Phase 5 begins. NOT during Phases 2-3.

**Why it's timed this way:** The kr-build-prep skill already contains 90% of what's needed (CLAUDE.md design, agent team templates, session scoping, dev docs pattern). A research chat NOW would produce generic findings that (a) are mostly already in the skill and (b) may be outdated by the time you reach Phase 5. Agent teams shipped Feb 2026 and are still experimental — research this when you're about to USE it, not weeks before.

**The question:** Given the finalized source engine SPEC, what is the optimal Claude Code setup for building it?

**What the chat should cover:**
- Review what's already in `skills/kr-build-prep/SKILL.md` — what's still valid, what's outdated?
- Agent teams: latest state (experimental, requires Opus 4.6). Stable enough for KR? Or start with single sessions?
- CLAUDE.md for the source engine: draft the actual file (<200 lines) based on the finalized SPEC
- Cost estimate: how many Claude Code sessions for the source engine? Pro plan vs. Max plan budget
- Session scoping: what goes in session 1 (simplest path), session 2, session 3
- Hooks and commands: any Claude Code hooks that improve quality (e.g., auto-run tests on save)
- Memory/persistence: how to maintain continuity across sessions (NEXT.md pattern, session handoff)

**Output:** The actual Claude Code environment files for the source engine:
1. `engines/source/CLAUDE.md` (<200 lines)
2. `engines/source/docs/architecture.md`
3. `engines/source/docs/spec-rules.md` (key rules extracted from SPEC)
4. `engines/source/docs/testing.md` (drawn from Problem 1's framework)
5. `engines/source/session-1-plan.md` (first build session scope)
6. Updated `skills/kr-build-prep/SKILL.md` if findings changed anything

**Done condition:** You can hand these files to Claude Code and say "build session 1" and it knows exactly what to do.

**Start the chat with:** "Clone the repo. Read `skills/kr-build-prep/SKILL.md`, `engines/source/SPEC.md`, and `reference/TESTING_FRAMEWORK.md` (from Problem 1). The SPEC is finalized. Produce the actual Claude Code environment for building the source engine."

---

## One Maintenance Task (Low Priority)

### Repo Cleanup

**When to do it:** Any time you want a break from SPEC work. No deadline.

**The question:** Which files in this repo matter, which are junk, and what's the clean structure?

**Why it's low priority:** The repo mess doesn't block the engine cycle. Claude reads what the project knowledge tells it to. The 38+ files are ugly but harmless — they sit in root and reference/ and nobody references them.

**What the chat should do:**
- Audit every `.md` file in root (23 files) and `reference/` (16 files)
- For each: KEEP / ARCHIVE / DELETE, with reasoning
- Identify any file whose content should be merged into another
- Propose a clean directory structure
- Execute the cleanup (move, merge, delete)
- Update any cross-references in surviving files

**Output:** A clean repo. Fewer files. Clear structure.

**Start the chat with:** "Clone the repo. Read every `.md` file at the root level and in `reference/`. Many are artifacts from autonomous over-planning sessions. Audit each one: is it still needed, does it duplicate another file, should it be archived? Then execute the cleanup."

---

## The Claude Chat Project Template (For Engines 2-7)

When you finish the source engine and start the normalization engine, you'll need a new Claude Chat project. Here's the template — just swap the engine-specific parts:

**Project name:** `{Engine Name} — {Arabic Name}`
(e.g., "Normalization Engine — محرك التسوية")

**Project knowledge (from GitHub):**
- `engines/{engine}/` — the SPEC and all engine files
- `STEERING.md` — project overview
- `KNOWLEDGE_INTEGRITY.md` — corruption threats
- `SILENT_FAILURES.md` — silent failure patterns
- `reference/DOMAIN.md` — Islamic studies domain
- `reference/ENTRY_EXAMPLE.md` — target output quality
- `reference/DEEP_REASONING_PROTOCOL.md` — quality standard
- `skills/shared/` — ENGINE_PROTOCOL.md and other shared docs
- `NEXT.md` — current task directive

**Custom instructions:** Open the matching file from `skills/engine-project-template/` and paste everything below the `---` line. Each engine has its own ready-to-paste file — no editing needed.

**Fallback:** Keep `Github_key` in project knowledge.

This takes ~5 minutes per engine. You'll create 6 more of these over the coming months.

---

## Status

| Item | Status | Notes |
|------|--------|-------|
| Code execution enabled | TODO | Owner action: Settings > Capabilities |
| Skills uploaded | TODO | Owner action: upload 6 zips to Customize > Skills |
| Source engine project created | TODO | Owner action: follow setup steps above |
| API keys (.env file) | TODO | Owner action: copy from project knowledge files |
| Phase 1 (read SPEC) | IN PROGRESS | Owner is reading source engine SPEC |
| Phase 2 (comment resolution) | BLOCKED | Waiting on project setup |
| Problem 1 (testing architecture) | DONE | `reference/TESTING_FRAMEWORK.md` — 2026-03-08 |
| Problem 2 (Claude Code env) | TODO | One deep-research chat, right before Phase 5 |
| Repo cleanup | DONE | Root 23→16, superseded docs archived — 2026-03-08 |

---

## Files That Matter (Ignore Everything Else)

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

**Research completed (don't redo):**
- `skills/handoffs/claude-chat-research-2026-03-07.md` — Claude Chat optimization (8 findings)
- `skills/kr-build-prep/SKILL.md` — agent teams, CLAUDE.md design, build orchestration

**Everything else** is either archived session history, superseded plans, or infrastructure that Claude reads on demand. You don't need to track it.
