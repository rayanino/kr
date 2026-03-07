# Source Engine Project — Setup Guide

## How It Works

Claude Chat clones the KR repo at the start of each chat (4 seconds), giving direct access to all SPECs, contracts, code, and documentation. This means you need very few project knowledge files — just the essentials that must be available before the clone.

## Project Knowledge Files (upload these)

**Only 2 files needed:**

1. **`Github_key`** — The GitHub personal access token. Without this, Claude can't clone. This is the one essential file.

2. **`STEERING.md`** — Concise project context (78 lines, ~1.5K tokens). Always useful as background context. Small enough to justify always-loaded.

That's it. Everything else comes from the repo.

## What Claude Reads From the Repo

After cloning, Claude reads files on demand:
- `engines/source/SPEC.md` — The source engine specification
- `engines/source/contracts.py` — Pydantic data models
- `engines/normalization/contracts.py` — Downstream contract
- `KNOWLEDGE_INTEGRITY.md` — The 7 corruption threats
- `SILENT_FAILURES.md` — The 7 silent failure patterns
- `reference/DEEP_REASONING_PROTOCOL.md` — Perfection Standard
- `reference/ENTRY_EXAMPLE.md` — Target output quality
- `CREATIVE_MANDATE.md` — Creative protocol
- `reference/RESOURCES.md` — Tool inventory
- Any other file as needed

## Owner's Comments

Write your SPEC comments using the template at `skills/shared/COMMENT_TEMPLATE.md`. Save them as a file in the repo:

```
# Option A: In the repo (recommended)
Save as: skills/source-engine-comments.md
Claude reads it directly from the repo each chat.

# Option B: In project knowledge
Upload the comments file to the project.
Claude sees it immediately without cloning.
```

Option A is better because the file is versioned, Claude can update it (mark comments as resolved), and it persists across sessions without manual management.

## Session Handoffs

When a chat gets long, Claude produces a handoff summary and commits it to:
```
skills/handoffs/source-engine-{date}.md
```
The next chat picks it up automatically from the repo.

## What About the SPEC Split?

During finalization (kr-finalize skill), you may want to split the SPEC into section files to audit one section per chat. Claude can do this split itself:
```
engines/source/spec-sections/
├── sections_1-3_contracts.md
├── section_4_processing.md
├── sections_5-7_validation.md
└── sections_8-10_config.md
```
These live in the repo, not project knowledge.

## Why So Few Project Knowledge Files?

Context window = 200K tokens. Every project knowledge file consumes part of this. With the old approach (9+ files uploaded), ~50K tokens were consumed before the conversation started. With repo access:
- Project knowledge: ~2K tokens (Github_key + STEERING.md)
- Remaining: ~198K tokens for conversation
- Files read on demand only when needed

## Creating Other Engine Projects

When you move to the next engine (normalization, etc.):
1. Create a new Claude Chat project
2. Upload the same 2 files (Github_key, STEERING.md)
3. Change the custom instructions to the engine-specific role (see SKILL_ARCHITECTURE_V2.md for examples)
4. The skills are account-wide — they work in all projects automatically
