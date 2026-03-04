# How to Start — Activation Guide

## Step 1: Claude Chat Project Setup (one-time, 5 minutes)

**Project Instructions** — paste this into your KR project settings:
```
You are the architect of خزانة ريان (KR), a personal intelligent Islamic scholarly library. You own the entire application's design — every engine, every schema, every data model, every tool choice.

Read STATUS.md first. It tells you what state the project is in and what needs doing. You decide what to work on based on what's most impactful for bringing the project to completion. STATUS.md suggests a starting point, but you may override it.

Follow reference/DEEP_REASONING_PROTOCOL.md for your reasoning methodology and quality standard.

All past architectural decisions are in reference/kr_decisions.md. Do not re-litigate them unless you find a genuine error.

You make ALL technical decisions autonomously. The owner provides domain input only (Islamic scholarship, how scholars study, what sciences exist). The owner has no technical background — never present technical options or ask for technical permission.

At the end of every session: produce deliverables, produce new decisions for kr_decisions.md, and produce an updated STATUS.md that tells the next session what to attach and what to focus on.

Think as long as needed. Depth over speed. Always.
```

**Project Knowledge Files** — add exactly three:
1. `STATUS.md`
2. `reference/DEEP_REASONING_PROTOCOL.md`
3. `reference/kr_decisions.md`

## Step 2: Every Session (2 minutes + answering questions)

**Prepare the session bundle** — STATUS.md tells you which command to run. Usually:
```
cd /path/to/kr
make bundle ENGINE=source
```
This creates `session_bundle.md` — one file with everything Claude needs.

**Start a new conversation** (never continue old ones). Send:
```
Continue the project.
```
Attach `session_bundle.md`. That's it.

For multi-session items (like normalization), STATUS.md may say to also attach the previous session's draft output.

**During the session:** Answer domain questions if Claude asks. Otherwise let it work.

## Step 3: After Each Session (5 minutes)

1. Save Claude's deliverables to the repo at the paths it specifies
2. Replace STATUS.md with Claude's updated version
3. Append new decisions to `reference/kr_decisions.md`
4. Add Claude's session log entry to `reference/SESSION_LOG.md`
5. Commit with a descriptive message
6. Update the project knowledge files in Claude Chat settings (new STATUS.md and kr_decisions.md)

Then start a new conversation for the next session.

## What Claude Does Across Sessions

Claude autonomously drives the entire preparatory phase:
- Designs engine specifications (7 engines + 4 shared components)
- Corrects and perfects VISION.md
- Designs data models and schemas
- Makes all architectural decisions
- Chooses tools and infrastructure
- Designs Claude Code agents and commands
- Ensures everything is consistent

Each session picks up from the updated STATUS.md. Claude decides what's most important to work on. You provide files and domain expertise.

## If You Disagree With a Decision

Update STATUS.md: add your concern under "Session Notes for Next Claude." The next session will read it and either explain why the decision stands or revise it.
