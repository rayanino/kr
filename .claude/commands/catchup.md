---
description: Reload work-in-progress context after /clear or at session start. Shows current branch, recent changes, active task, and evaluation state.
allowed-tools: Bash(git diff:*), Bash(git log:*), Bash(git status:*), Bash(cat:*), Bash(head:*), Bash(wc:*), Bash(find:*), Bash(grep:*), Bash(ls:*), Read, Glob, Grep
---
Quickly reload project context. Do ALL of these:

0. If `.claude/session_state.json` exists, read it first and report:
   - When the last session ended (timestamp)
   - Which engine was active
   - What files were modified
   - Any uncommitted changes
   Then continue with the remaining steps for live verification.

1. Show current git branch and status: `git branch --show-current && git status --short`
2. Show recent commits: `git log --oneline -10`
3. Show uncommitted changes summary: `git diff --stat`
4. Read NEXT.md — it tells you the current task and what files to read.
5. If NEXT.md references an engine, read that engine's CLAUDE.md.
6. Read `tests/results/source_engine/COST_LOG.json` if it exists — report budget status in one line (e.g., "Budget: 9.2 / 100.0 EUR").
7. Count verdicts issued: grep for `Verdict:` across `PHASE_C_SESSION*_REPORT.md` files if they exist.
8. Read `PHASE_C_ERRATA.md` first 5 lines if it exists — remind yourself of the correction titles before starting evaluation work.
9. Summarize: what branch are we on, what task is active, what's the current state, budget status, verdicts so far, what's the next action.
