# Weekend CC Work Program — Briefing for Planning Chat

## Situation

I have ~2 days of Claude Code compute to use (20x Max plan + weekend 2x promotion = effectively 4x normal usage). I want CC to run autonomously on long tasks that harden the two finished engines (source + normalization). I dispatch CC between tasks — I don't want constant back-and-forth (I'm studying). You (Claude Chat) are the control tower: plan the work, I dispatch CC, CC runs, I come back when it's done or stuck.

**No new engine builds.** The passaging engine build requires architect involvement. This weekend is about making the existing foundation rock-solid.

## Repo State

- **Commit:** `b2604d5` on `github.com/rayanino/kr`
- **Source engine:** Complete. 379 tests, 204 books validated with LLM. Full collection never run deterministically.
- **Normalization engine:** Complete. 420 tests (14 skipped), 63 fixtures passing. Evaluation GO at `7f81052`. SPEC errata resolved. Transition gate pending (separate session). Full collection never run.
- **Already prepared:** `scripts/normalization_corpus_sweep.py` (tested, ready to run) and `scripts/phases/run_phase_a.py` (source engine deterministic sweep, already implemented). Current NEXT.md at `b2604d5` directs CC to run both sweeps.

## CC Environment & Capabilities

CC is Claude Opus 4.6, 1M context, on Windows 11, Python 3.13. It has:

**Custom rules** (`.claude/rules/`):
- python-code.md — Type hints, Pydantic, Arabic text safety, `[0-9]` not `\d`
- quality-workflow.md — Pyright after edits, pytest after edits, code-reviewer before commit, parallel worktree execution
- regex-arabic-digits.md — `\d` matches Arabic-Indic digits; always use `[0-9]`
- result-preservation.md — Every LLM call persisted, manifest-based reuse
- session-discipline.md — One engine/session, re-read after compaction, /smart-compact proactively
- shared-concept-changes.md — Grep all consumers before modifying shared enums
- spec-writing.md — Real Arabic examples, testable rules, `[OPEN:]` markers
- testing.md — Real Arabic fixtures only, SPEC-driven tests, cross-reference Usul.ai

**Persistent memory system:** File-based at `~/.claude/projects/.../memory/`, MEMORY.md index, 50+ observations via claude-mem MCP.

**Hooks:** SessionStart loads git status, recent commits, NEXT.md automatically.

**Local data:** `shamela-export-samples/` directory with 20,000+ Shamela .htm exports (accessible, confirmed).

## Budget

- **LLM spend:** Up to €100-150 total across both engines this weekend
- **Critical constraint:** Every euro must produce saved, reusable results. No test runs on loose grounds, no unsaved LLM responses. The project has a result preservation protocol — every API call persists full structured output for downstream reuse. Bug fixes mark only affected books as `needs_rerun`. See `RESULT_PRESERVATION.md`.
- **Models available:** Claude Opus 4.6 (canonical, ~90% of calls), Command A via OpenRouter, GPT-5.4 as fallback. OpenRouter API key is in project files.

## What I Want From This Chat

Design a **ranked task queue** for CC over the weekend:
- 4-8 tasks, each running 1-3 hours autonomously
- Clear start/end criteria for each task
- Explicit handoff points where I come back to dispatch the next one
- Each task produces committed output (reports, data, test fixtures — not architectural decisions)
- Mix of €0 deterministic tasks and budget-conscious LLM tasks
- Maximize the hardening value: what gives us the most confidence in the source + normalization engines before we build passaging?

## Key Project Files to Read

When you clone the repo in the new chat, the most relevant files are:
1. `NEXT.md` — current CC directive (corpus sweeps)
2. `engines/normalization/EVALUATION_REPORT.md` — what we know about normalization quality
3. `engines/normalization/LESSONS.md` — build lessons + passaging recommendations
4. `engines/normalization/KNOWN_LIMITATIONS.md` — L-001 through L-012
5. `engines/source/LESSONS.md` — source engine lessons (if exists)
6. `reference/ENGINE_BUILD_BLUEPRINT.md` — the full methodology
7. `RESULT_PRESERVATION.md` — how to persist LLM results
8. `KNOWLEDGE_INTEGRITY.md` — the 7 corruption threats
9. `engines/source/contracts.py` — source engine output schema
10. `engines/normalization/contracts.py` — normalization output schema

## Constraints

- CC produces **reports and data**, not architectural decisions
- CC should NOT modify SPECs without architect review
- CC CAN fix bugs it finds if the fix is obvious and has test coverage
- CC CAN add test fixtures from interesting edge cases
- CC CAN run LLM-based validation (e.g., re-running source engine inference on selected books)
- The source engine roadmap (`source_engine_roadmap.jsx` in project files) shows Steps 0-1 complete, Step 2 (deterministic sweep) active, Steps 3-5 pending
