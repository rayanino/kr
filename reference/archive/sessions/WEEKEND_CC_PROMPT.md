Plan a weekend Claude Code work program for خزانة ريان (KR).

<situation>
I have ~2 days of Claude Code (CC) compute available — 20x Max plan + weekend 2x promotion, resetting Monday morning. I'm currently over 50% of weekly usage, which with the promotion means I have roughly the equivalent of a full week's compute to burn through before Monday.

CC runs autonomously on long tasks (1-3 hours each). I dispatch CC between tasks — I check in when it finishes, give it the next task, and go back to studying. You (Claude Chat) are the control tower: you plan the work, write NEXT.md directives, and I relay them to CC. I do NOT want constant back-and-forth — I'm studying for a test.

One task is ALREADY RUNNING: CC can start immediately on the normalization corpus sweep (Task A in the current NEXT.md). I need you to confirm that directive is good, then plan what comes after.
</situation>

<project_state>
Clone the repo first (`github.com/rayanino/kr`, token in project files), then read these files in order:
1. `reference/archive/sessions/WEEKEND_CC_BRIEFING.md` — full briefing I prepared (repo state, CC capabilities, budget, constraints, key files list)
2. `NEXT.md` — current CC directive (normalization + source corpus sweeps, ready to run now)
3. `engines/normalization/EVALUATION_REPORT.md` — normalization evaluation results (GO verdict)
4. `engines/normalization/LESSONS.md` — build lessons + passaging recommendations
5. `engines/normalization/KNOWN_LIMITATIONS.md` — L-001 through L-012
6. `KNOWLEDGE_INTEGRITY.md` — the 7 corruption threats (T-1 through T-7)
7. `RESULT_PRESERVATION.md` — how to persist LLM results (critical for budget discipline)
8. Source engine roadmap: `source_engine_roadmap.jsx` in project files — shows Steps 0-1 complete, Step 2 active

Read ALL of these before proposing tasks. The briefing alone is not enough — you need the evaluation report and lessons learned to design good tasks.
</project_state>

<cc_capabilities>
CC is Claude Opus 4.6, 1M context, Windows 11, Python 3.13. It has:
- 6 custom rule files in `.claude/rules/` (type hints, quality workflow with pyright+pytest+code-reviewer, Arabic digit safety, result preservation, session discipline, shared concept change guards, SPEC writing rules, testing rules)
- Persistent memory system (file-based, 50+ observations via claude-mem MCP)
- SessionStart hook that auto-loads git status, recent commits, NEXT.md
- Parallel worktree execution capability
- Access to `shamela-export-samples/` with 20,000+ Shamela .htm exports locally
</cc_capabilities>

<budget>
- LLM API spend: up to €100-150 total across both engines this weekend
- CRITICAL principle: every euro produces saved, reusable results. No test runs on loose grounds. No unsaved LLM responses. Every API call persists full structured output per RESULT_PRESERVATION.md. Bug fixes mark only affected books as needs_rerun — never blanket re-runs.
- Models: Claude Opus 4.6 (canonical ~90%), Command A via OpenRouter, GPT-5.4 fallback
- API keys: OpenRouter, Anthropic, OpenAI, Mistral — all in project files
</budget>

<constraints>
- NO new engine builds. The passaging engine requires architect involvement. This weekend is hardening only.
- CC produces reports and data, not architectural decisions. CC can fix obvious bugs with test coverage. CC cannot modify SPECs without architect review.
- Every task must have a clear NEXT.md directive that CC can follow autonomously for 1-3 hours.
- Each task commits results with a descriptive prefix (e.g., `sweep:`, `harden:`, `validate:`).
- Quality over speed. One thorough task is worth more than three shallow ones.
</constraints>

<task>
Do these things, in this order:

1. **Read all files listed in project_state.** You need the full picture before planning.

2. **Validate the current NEXT.md.** CC can start on this RIGHT NOW. Tell me: is the current directive good to go? Any adjustments needed? Give me the exact message to send CC to start.

3. **Design the full weekend task queue.** Produce a ranked list of 4-8 tasks that maximize hardening value for the source and normalization engines. For each task:
   - Title and 1-sentence purpose
   - Estimated duration
   - Estimated cost (€0 for deterministic, or LLM cost estimate)
   - What it produces (committed output files)
   - Dependencies (which tasks must finish first)
   - Why this task matters for the pipeline's reliability

4. **Write the NEXT.md for Task 2** (whatever comes after the corpus sweeps). I want it ready to paste into the repo the moment CC finishes Task 1. Follow the same structure as the current NEXT.md — CC reads it literally.

5. **Give me the dispatch protocol.** A simple checklist I follow each time CC finishes a task:
   - What to check before starting the next task
   - How to relay CC's results to you (what to paste in chat)
   - How to update NEXT.md and start CC again
</task>

<output_format>
Structure your response as:
1. **Immediate action** — what I tell CC right now (keep this short, I want to dispatch CC within 2 minutes)
2. **Weekend task queue** — the ranked plan with all details
3. **NEXT.md for Task 2** — ready to commit
4. **Dispatch protocol** — my checklist between tasks
</output_format>
