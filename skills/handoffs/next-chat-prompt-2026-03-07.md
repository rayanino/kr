# Prompt for Next Chat — Planning Session

Paste everything below the line into a new chat in this project.

---

Clone the repo using the Github_key file. Then read these files in this exact order before responding:

1. `OPEN_PROBLEMS.md` — the current roadmap (3 research problems + setup steps)
2. `skills/shared/ENGINE_PROTOCOL.md` — the 6-phase per-engine cycle
3. `reference/HONEST_PLAN.md` — the real plan, especially the anti-over-planning principle on line 60 and the per-engine cycle on lines 72-89
4. `skills/handoffs/claude-chat-research-2026-03-07.md` — Claude Chat optimization research already completed
5. `skills/kr-build-prep/SKILL.md` — includes the agent teams section and build orchestration options
6. `STEERING.md` — project overview

After reading all six files, here is the task:

## Context

خزانة ريان (KR) is a personal Islamic scholarly library with a 7-engine pipeline. Each engine goes through a 6-phase cycle defined in ENGINE_PROTOCOL.md. I am currently in Phase 1 for the source engine (reading the SPEC, writing domain comments).

In the previous session, we:
- Researched Claude Chat optimization (GitHub integration, skills, context management, MCPs)
- Hardened all 6 skills based on research findings
- Expanded kr-build-prep with full agent team templates and build orchestration
- Created ENGINE_PROTOCOL.md (the 6-phase per-engine workflow)
- Rewrote OPEN_PROBLEMS.md from 12 sequential tasks to 3 parallel research problems after catching ourselves falling into the over-planning trap

## My Four Concerns

These are the problems that keep me up at night. They must all be solved thoroughly before I can confidently run the engine cycle:

1. **Claude Chat environment per engine.** Each engine needs a Claude Chat project optimized for the 6-phase cycle. The project setup (knowledge files, custom instructions, skill interaction, context management) must be researched and designed so thoroughly that I have a clear, repeatable template to follow. This is the foundation — every phase runs through Claude Chat.

2. **Claude Code build environment.** People are building entire engineering teams with Claude Code agent teams, dedicated orchestration tools, memory persistence, hooks, and custom commands. I need this to be deeply researched so that when Phase 5 (build prep) produces the Claude Code environment, it produces the BEST possible environment. Maximum build quality, maximum test coverage.

3. **Testing of built engines.** This is the most critical concern. Once an engine is built, it needs exhaustive testing: tracing every input through every process to the output, isolated testing of each LLM call inside the engine to verify reliability, and testing whether independent LLMs are reliable enough to serve as quality gates between engines. The 5a/5b/5c framework in HONEST_PLAN.md is the starting point, but the full testing architecture needs to be designed.

4. **Repo structure and file connections.** The repo has 38+ markdown files, many from autonomous over-planning sessions. I've lost track of what's what. There's redundancy and pollution. The previous session downgraded this to low priority because it doesn't block the engine cycle, but it's still a real problem that affects my ability to navigate the project.

## Your Task

Critically evaluate the current plan in OPEN_PROBLEMS.md against my four concerns. Be rigorous:

- Is the current structure (3 parallel research problems) actually the right approach? Or is something missing?
- Are the research problems scoped correctly? Too broad? Too narrow? Missing a dimension?
- Is the ordering right? Does anything actually block Phase 2 that we're ignoring?
- What's the fastest path to "everything is ready for the engine cycle" without falling into the over-planning trap?
- Are there dependencies between the problems that the current plan doesn't capture?

Then produce the final version of OPEN_PROBLEMS.md — the definitive roadmap that I will follow. This is the last planning session. After this, I execute.

## Constraints

- Do not produce vague recommendations. Every task must have a concrete output and a clear "done" condition.
- Do not over-plan. The HONEST_PLAN principle applies to you too: if a problem can only be solved with real engine output, defer it to Phase 6.
- Do not split things into 12 sub-tasks again. Keep it to the minimum number of tasks that actually need separate chats.
- Research before proposing. Use web search to verify assumptions about Claude Chat projects, Claude Code agent teams, and LLM testing frameworks. Don't guess.
- The final goal: everything is ready and thoroughly designed for me to do the cycle of **create engine project → produce robust engine → go to next engine**, confidently and repeatedly, for all 7 engines.
