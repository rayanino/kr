---
description: Reload work-in-progress context after /clear or at session start. Shows current branch, recent changes, and active task.
allowed-tools: Bash(git diff:*), Bash(git log:*), Bash(git status:*), Bash(cat:*), Bash(head:*), Read
---
Quickly reload project context. Do ALL of these:

1. Show current git branch and status: `git branch --show-current && git status --short`
2. Show recent commits: `git log --oneline -10`
3. Show uncommitted changes summary: `git diff --stat`
4. Read NEXT.md — it tells you the current task and what files to read.
5. If NEXT.md references an engine, read that engine's CLAUDE.md.
6. Summarize: what branch are we on, what task is active, what's the current state, what's the next action.
