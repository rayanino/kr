# خزانة ريان (KR) — Personal Intelligent Islamic Scholarly Library

Full specification: `VISION.md`. Decisions log: `reference/kr_decisions.md`.

## Repository Map

- `engines/` — Seven processing engines (source, normalization, passaging, atomization, excerpting, taxonomy, synthesis). Each has `CLAUDE.md`, `SPEC.md`, `src/`, `tests/`.
- `shared/` — Cross-engine infrastructure: consensus, validation, feedback.
- `schemas/` — Inter-engine data contracts (one per boundary).
- `library/` — Knowledge product: sciences, sources, registries.
- `interface/` — Scholar interface (user-facing intelligence layer).
- `gold/` — Hand-crafted validation baselines. Never auto-generated.
- `scripts/` — Utilities. `extract_vision_sections.py` for partial VISION reads.
- `reference/` — Decisions, domain primer, resources, session log.

## Pipeline

Phase 1 (source-format-specific):
1. Source (محرك المصادر) → 2. Normalization (محرك التطبيع)
--- Normalization boundary (حد التطبيع) — nothing source-specific below ---
Phase 2 (source-agnostic):
3. Passaging (محرك التقطيع) → 4. Atomization (محرك التذرير) → 5. Excerpting (محرك الاقتطاف) → 6. Taxonomy (محرك التصنيف) → 7. Synthesis (محرك التوليف)
Layer 3: Scholar Interface (واجهة العالم) — consumes all knowledge products.

## Pre-Work Protocol

1. Enter the engine directory (its CLAUDE.md loads automatically).
2. Read the engine's SPEC.md — the authoritative behavioral specification.
3. Read input/output schemas referenced in the SPEC.
4. Run existing tests to verify stated CLAUDE.md test counts match reality. Update if stale.

## Post-Work Protocol

1. Run the engine's tests: `cd engines/<name> && python -m pytest tests/ -q`
2. If behavior changed → update SPEC.md in the same session.
3. If state changed (test counts, known issues) → update engine CLAUDE.md.
4. If vocabulary changed → flag for VISION.md §2 review.

## Architectural Constraints

- **Normalization boundary (§7.6).** No source-format-specific logic in Phase 2 engines.
- **Self-containment (§5.1).** Every excerpt is independently understandable.
- **Multi-model consensus (§2.2).** Content decisions use independent LLM agreement.
- **Human gates (§9).** No irreversible library change without owner approval.
- **Accuracy > Protection > Intelligence (§1.5).** Priority when properties conflict.
- **Text integrity (§5.1).** Excerpt primary_text is never modified.
- **Metadata is synthesis fuel (D-023).** Never strip metadata; the synthesizer needs all of it.
- **Fail-loud (D-033).** Low-confidence decisions get flags, not silent defaults.

## Run All Tests

```
python -m pytest engines/*/tests/ shared/*/tests/ -q
```

## Current Priorities

Milestone 1: Source engine + normalization engine (Shamela format) end-to-end.
See `NEXT.md` for the specific current task.
