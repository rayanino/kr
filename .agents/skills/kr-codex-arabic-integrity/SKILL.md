---
name: kr-codex-arabic-integrity
description: Use when KR work touches Arabic text, scholarly metadata, Quranic content, regex over Arabic text, or any path where silent Unicode corruption would be blocking.
---

# KR Codex Arabic Integrity

Read these files first:

1. `.claude/skills/arabic-text/SKILL.md`
2. `.claude/skills/knowledge-safety/SKILL.md`
3. `.claude/rules/arabic-scholarly-conventions.md` when the task touches scholarly phrasing or metadata

Then review the task against:

- T-1 silent text corruption
- T-2 attribution error
- T-6 metadata poisoning

Always treat these as blocking risks:

- Unicode normalization on Arabic primary text
- `.lower()`, `.upper()`, `.casefold()`, or bare `.strip()` on Arabic text
- lossy encode/decode paths
- regex patterns that silently mis-handle Arabic digits or word boundaries
