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

Do NOT add the workplan or roadmap as project files — they are too large and would waste Claude's attention on irrelevant work items.

## Step 2: Start W-001 — Your First Real Session

Open a new Claude Chat conversation in the KR project. Send:

```
Read STATUS.md. Execute the current work item. Follow the Deep Reasoning Protocol (creation mode).
```

Then attach these files from the KR repo:
```
engines/source/src/intake.py
engines/source/src/enrich.py
engines/source/src/corpus_audit.py
engines/source/reference/ABD_INTAKE_SPEC.md
engines/source/reference/edge_cases.md
schemas/source_metadata.json
VISION.md
```

Claude takes it from there. It will read STATUS.md (which contains the full W-001 specification), load all your attachments, and begin working.

## Step 3: After Each Session

1. **Save Claude's outputs.** Claude will produce deliverables (SPEC drafts, VISION corrections, decisions). Copy these into the repo at the paths Claude specifies.
2. **Update STATUS.md.** Claude will provide an updated STATUS.md block. Replace the current STATUS.md with it.
3. **Update kr_decisions.md.** Append any new decisions Claude produced.
4. **Commit** with a descriptive message.
5. **Update the project knowledge files** in Claude Chat project settings (replace the old STATUS.md and kr_decisions.md with the new versions).
6. **Open the next session** with the same prompt. STATUS.md tells Claude what to do.

## Multi-Session Work Items

Some work items take 2–3 sessions (like W-001). When continuing:
- Attach everything STATUS.md lists under "Files to Attach This Session"
- STATUS.md will explicitly include "attach the SPEC draft from the previous session" — do this
- Use the same prompt: `Read STATUS.md. Execute the current work item. Follow the Deep Reasoning Protocol (creation mode).`

## If You Want to Give Feedback on a Deliverable

Update STATUS.md:
- Change the work item to `W-XXX-R1 (revision)`
- Add your feedback in "Session Notes for Next Claude"
- Start a new session — Claude reads the feedback and revises

## Realistic Effort Per Session

**Your effort per session:** ~5 minutes of file management (finding and attaching files, committing outputs) + answering domain questions when Claude asks (usually 0–3 questions per session about how you use the library).

**Claude's effort:** The actual deep work — reading code, researching best practices, making design decisions, writing documentation, self-auditing. This is the bulk of each session.

**You do NOT need to:** understand the architecture, make technical decisions, review intermediate work, coordinate what happens next, or read the SPECs during the process (that's what W-018 is for).
