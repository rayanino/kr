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

**Before any work, read `STATUS.md` in the repo root.** It tells you: what phase the project is in, what the current work item is, what files to read, what decisions are already made.

**Coordination files in `reference/`:**
- `reference/kr_decisions.md` — all architectural decisions, numbered and permanent.
- `reference/DEEP_REASONING_PROTOCOL.md` — the Perfection Standard (23 criteria) and reasoning methodology for all documentation work.
- `reference/PREPARATORY_WORKPLAN.md` — master workplan for the preparatory phase.
- `reference/SESSION_LOG.md` — running log of sessions.
- `reference/HOW_TO_START.md` — activation guide for the owner.

**After every session:** update `STATUS.md` with what was done and what's next.

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

Following the binding project roadmap (kr_definitive_roadmap_v2.md):

**Phase 2 — Engine SPEC Writing + VISION Correction (active)**
1. Round 1: Source engine — write SPEC.md, correct VISION.md §7.1–§7.4.
2. Round 2: Normalization engine — write SPEC.md, correct VISION.md §7.5–§7.6.
3. Rounds 3–9: Remaining engines per roadmap order (passaging, atomization, excerpting, taxonomy, synthesizing, shared components, cross-cutting corrections).

**Queued**
- Phase 3: Cross-SPEC consistency verification.
- Phase 4: Owner review.
- Phase 5: Build infrastructure planning.
- Phase 6+: Engine building (Milestone 1 — prove end-to-end on إملاء, VISION.md §10.2).
