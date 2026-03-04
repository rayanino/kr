# خزانة ريان (KR)

A personal intelligent Islamic scholarly library. See `VISION.md` for the full specification.

## Repository Map

- `VISION.md` — authoritative Level 0 specification (1585 lines). Corrections happen during SPEC writing per engine.
- `NEXT.md` — session handoff: what to do next, which files to read.
- `STATUS.md` — project state overview.
- `schemas/` — inter-engine data contracts (one per boundary).
- `engines/` — seven processing engines. Each has `CLAUDE.md`, `SPEC.md` (when written), `src/`, `tests/`, `reference/`.
- `interface/` — user-facing intelligence layer. The scholar interface consumes all knowledge products and provides Q&A, teaching, discovery, assistance, and navigation.
- `shared/` — cross-engine infrastructure (consensus, human_gate, validation, feedback, user_model).
- `library/` — the knowledge product: science trees, excerpts, entries, source registry.
- `gold/` — validation baselines (hand-crafted, never auto-generated).
- `scripts/` — utility scripts (`extract_vision_sections.py` for VISION section extraction).
- `reference/` — coordination: decisions log (`kr_decisions.md`), reasoning protocol, resources, session log.

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

Layer 3 — Scholar Interface (user-facing):
8. **Scholar interface** (واجهة العالم) — conversational Q&A, active teaching, proactive discovery, scholarly assistance, knowledge navigation. Consumes all knowledge products. Reads/writes the user model.

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
