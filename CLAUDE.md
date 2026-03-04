# خزانة ريان (KR)

A personal intelligent Islamic scholarly library. See `VISION.md` for the full specification.

## Repository Map

- `VISION.md` — authoritative Level 0 specification (1585 lines). §0–§5, §13 audited; §6–§12 pending.
- `STATUS.md` — current project state. **Read this first in every session.**
- `schemas/` — inter-engine data contracts (one per boundary).
- `engines/` — seven processing engines. Each has `CLAUDE.md`, `SPEC.md`, `src/`, `tests/`, `reference/`.
- `shared/` — cross-engine infrastructure (consensus, human_gate, validation, feedback).
- `library/` — the knowledge product: science trees, excerpts, entries, source registry.
- `gold/` — validation baselines (hand-crafted, never auto-generated).
- `scripts/` — utility scripts (`extract_vision_sections.py` for session prep).
- `reference/` — coordination: decisions log, reasoning protocol, workplan, session log.

## Processing Pipeline

Phase 1 — Knowledge Acquisition (source-format-specific):
1. **Source engine** (محرك المصادر) — discover, acquire, freeze, document sources.
2. **Normalization engine** (محرك التطبيع) — transform to universal normalized format.

--- Normalization boundary (حد التطبيع) — nothing source-format-specific below ---

Phase 2 — Knowledge Understanding (source-agnostic):
3. **Passaging engine** (محرك التقطيع) — segment normalized content into passages.
4. **Atomization engine** (محرك التذرير) — break passages into typed atoms.
5. **Excerpting engine** (محرك الاقتطاف) — group atoms into self-contained excerpts.
6. **Taxonomy engine** (محرك التصنيف) — place excerpts at correct leaves; manage evolution.
7. **Synthesizing engine** (محرك التوليف) — generate encyclopedic entries from excerpts.

## Session Protocol

Read `STATUS.md` first. It shows project state, what exists, what's missing, and suggested next work. You decide what to work on. After each session: produce deliverables, decisions, and an updated STATUS.md.

## Architectural Constraints

- **Normalization boundary.** No source-format-specific logic below the boundary. (§7.6)
- **Self-containment.** Every excerpt is independently understandable. (§5.1)
- **Multi-model consensus.** Content decisions use independent LLM agreement. (§2.2)
- **Human gates.** No irreversible library change without owner approval. (§9)
- **Accuracy > Protection > Intelligence.** Core property priority. (§1.5)
- **Entries are co-primary with excerpts.** Never downgrade entries. (§1.6, §6)
- **Text integrity.** Excerpt primary text is never modified. (§5.1)

## Run Tests
```
python -m pytest engines/*/tests/ shared/*/tests/ -q
```

## Current Priorities

Read `STATUS.md`. The preparatory phase goal: complete SPECs, perfect VISION.md, verify schemas, populate `.claude/` — so Claude Code can build from clear specifications.
