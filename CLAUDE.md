# خزانة ريان (KR)

A personal intelligent Islamic scholarly library. See `VISION.md` for the full specification.

## Repository Map

- `VISION.md` — authoritative design specification. Read before any other document.
- `STATUS.md` — current project state. **Read this first in every session.**
- `CLAUDE.md` — this file.
- `reference/` — coordination files: decisions log, reasoning protocol, workplan, session log.
- `schemas/` — inter-engine data contracts (one per engine-to-engine boundary).
- `engines/` — the seven processing engines. Each has `CLAUDE.md`, `SPEC.md`, `src/`, `tests/`.
- `shared/` — cross-engine infrastructure (consensus, validation, feedback).
- `library/` — the knowledge product: science trees, excerpts, entries, source registry.
- `gold/` — validation baselines (hand-crafted, never auto-generated).
- `scripts/` — utility scripts (e.g., `extract_vision_sections.py` for session prep).
- `.claude/` — agent infrastructure (subagents, commands, hooks).

## Processing Pipeline

Phase 1 — Knowledge Acquisition (source-format-specific):
1. **Source engine** (محرك المصادر) — discover, acquire, freeze, document sources.
2. **Normalization engine** (محرك التطبيع) — transform to universal normalized format.

--- Normalization boundary (حد التطبيع) — nothing source-format-specific below this line ---

Phase 2 — Knowledge Understanding (source-agnostic):
3. **Passaging engine** (محرك التقطيع) — segment normalized content into passages.
4. **Atomization engine** (محرك التذرير) — break passages into typed atoms.
5. **Excerpting engine** (محرك الاقتطاف) — group atoms into self-contained excerpts.
6. **Taxonomy engine** (محرك التصنيف) — place excerpts at correct leaves; manage evolution.
7. **Synthesizing engine** (محرك التوليف) — generate encyclopedic entries from excerpts.

## Session Protocol

**Read `STATUS.md` first.** It shows the full project state — what exists, what's missing, what decisions are open, and what was suggested for this session. You decide what to work on based on what's most impactful.

**Coordination files in `reference/`:**
- `reference/kr_decisions.md` — all architectural decisions, numbered and permanent.
- `reference/DEEP_REASONING_PROTOCOL.md` — Perfection Standard (23 criteria), architectural ownership, reasoning methodology.
- `reference/PREPARATORY_WORKPLAN.md` — advisory workplan with suggested sequence and per-engine details.
- `reference/SESSION_LOG.md` — running log of sessions.
- `reference/HOW_TO_START.md` — activation guide for the owner.

**At the end of every session:** produce deliverables, new decisions, updated STATUS.md, and a session log entry.

## Pre-Work Protocol (Engine Work)

1. Enter the engine directory (its `CLAUDE.md` loads automatically).
2. Read the engine's `SPEC.md`.
3. Read the input schema: `schemas/[input_schema]`.
4. Read the output schema: `schemas/[output_schema]`.

## Post-Work Protocol

1. Run the engine's tests.
2. Update `SPEC.md` if behavior changed.
3. Update the engine's `CLAUDE.md` if state changed.
4. Flag vocabulary changes for §2 review.
5. A task is not complete until documentation matches code.

## Architectural Constraints

- **Normalization boundary.** No source-format-specific logic below the boundary. Violation = architectural bug. (VISION.md §7.6)
- **Self-containment.** Every fully-formed excerpt is independently understandable. (VISION.md §5.1)
- **Multi-model consensus.** Content decisions use independent LLM agreement. (VISION.md §2.2)
- **Human gates.** No irreversible library change without owner approval or pre-approval policy. (VISION.md §9)
- **Accuracy > Protection > Intelligence.** Core property priority. (VISION.md §1.5)
- **No monolith agents.** Name the specific engine — never "the engine" or "the system" when one engine is responsible. (VISION.md §1.1, §2.2)
- **Entries are co-primary with excerpts.** Never downgrade entries. (VISION.md §1.6, §6)
- **Text integrity.** Excerpt primary text is never modified. (VISION.md §5.1)

## Run All Tests
```
# Direct (from repo root, with _paths.py on sys.path):
python -m pytest engines/*/tests/ shared/*/tests/ -q

# Via Makefile (uses .venv, run `make install` first):
make test
```

## Current Priorities

Read `STATUS.md` for the full project state. Claude Chat is the architect — it decides what to work on each session based on what's most impactful for bringing the project to completion. The advisory workplan is in `reference/PREPARATORY_WORKPLAN.md`.

**Preparatory phase goal:** Every engine has a complete SPEC, VISION.md is perfect, all schemas are correct and consistent, all architectural decisions are made, and the `.claude/` directory is populated — so Claude Code can build from clear specifications.
