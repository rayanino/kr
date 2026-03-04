# How to Start — Activation Guide

## Step 1: Claude Chat Project Setup (5 minutes)

In your Claude Chat KR project settings:

**Project Instructions** — paste this:
```
You are the Architect for خزانة ريان (KR). Your role:
- Make ALL technical and architectural decisions autonomously
- Ask the owner ONLY for domain/usage input (how the scholar uses the library)
- Follow the Deep Reasoning Protocol in reference/DEEP_REASONING_PROTOCOL.md
- Always read STATUS.md first to understand project state
- Update STATUS.md at the end of every session
- Record all decisions in reference/kr_decisions.md format

The owner is the client, not the engineer. Do not present technical options.
Do not ask permission for technical decisions. Decide, document, justify briefly.

Think as long as needed. No time pressure. Depth over speed always.
```

**Project Knowledge Files** — add these three only:
1. `STATUS.md`
2. `reference/DEEP_REASONING_PROTOCOL.md`
3. `reference/kr_decisions.md`

Do NOT add the workplan or roadmap — they are too large and waste Claude's attention.

## Step 2: Start W-001 — Your First Real Session

**Prepare the VISION excerpt** (one-time per session, saves 76% context):
```
cd /path/to/kr
make vision SECTIONS="2 7"
```
This creates `vision_excerpt.md` in the repo root. Attach this instead of VISION.md.

**Open a new Claude Chat conversation** in the KR project. Send:
```
Read STATUS.md. Execute the current work item. Follow the Deep Reasoning Protocol (creation mode).
```

**Attach these files:**
1. `vision_excerpt.md`
2. `engines/source/src/intake.py`
3. `engines/source/src/enrich.py`
4. `engines/source/src/corpus_audit.py`
5. `engines/source/reference/ABD_INTAKE_SPEC.md`
6. `engines/source/reference/edge_cases.md`
7. `schemas/source_metadata.json`
8. `schemas/SCHEMA_ANALYSIS.md`

Claude takes it from there.

## Step 3: After Each Session

1. **Save Claude's outputs.** Claude produces deliverables (SPEC drafts, decisions, VISION corrections). Copy into the repo at the paths Claude specifies.
2. **Update STATUS.md.** Claude provides an updated STATUS.md block — replace the file.
3. **Append new decisions** to `reference/kr_decisions.md`.
4. **Commit** with a descriptive message.
5. **Update project knowledge files** in Claude Chat settings (replace old STATUS.md and kr_decisions.md).

## Step 4: Multi-Session Work Items

Some items take 2–3 sessions. STATUS.md always lists what to attach, including:
- The VISION excerpt command (`make vision SECTIONS="..."`)
- Any outputs from previous sessions to re-attach

Read STATUS.md's "Files to Attach" section — it's explicit about every file.

## Giving Feedback on a Deliverable

Update STATUS.md:
- Change work item to `W-XXX-R1 (revision)`
- Add feedback in "Session Notes for Next Claude"
- Start a new session — Claude reads feedback and revises

## What Claude May Do During Sessions

- **Split across multiple messages.** A SPEC is long. Claude may say "I'll continue in my next message." Just let it finish.
- **Ask you domain questions.** Usually 0–3 per session about how you use the library. Answer from your experience as a scholar.
- **Use web search.** For tool decisions (CI/CD, Python packaging, etc.), Claude will research current best practices.

## Realistic Effort

**Per session:** ~5 minutes of file management + 0–3 domain questions.
**You do NOT need to:** understand architecture, make technical decisions, review intermediate work, or coordinate sessions.
