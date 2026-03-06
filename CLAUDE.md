# خزانة ريان (KR) — Personal Intelligent Islamic Scholarly Library

Full specification: `VISION.md`. Decisions log: `reference/kr_decisions.md`.
Domain knowledge: `reference/DOMAIN.md`. Quality target: `reference/ENTRY_EXAMPLE.md`.

## Repository Map

- `engines/` — Seven processing engines, each with `CLAUDE.md`, `SPEC.md`, `src/`, `tests/`.
- `shared/` — Cross-engine infrastructure (consensus, validation, human_gate, feedback, user_model, scholar_authority).
- `interface/scholar/` — Scholar interface: user-facing intelligence layer consuming all engine outputs.
- `schemas/` — Inter-engine data contracts (one per pipeline boundary).
- `library/` — Knowledge product: sciences, sources, registries. This IS the user's knowledge.
- `gold/` — Hand-crafted validation baselines. Never auto-generated or auto-modified.
- `scripts/` — Utilities. `extract_vision_sections.py` for partial VISION reads.
- `reference/` — Decisions, domain primer, resources, user scenarios, session log.

## Pipeline

Phase 1 (source-format-specific):
  Source (محرك المصادر) → Normalization (محرك التطبيع)
  ─── Normalization boundary (حد التطبيع) — nothing source-specific below ───
Phase 2 (source-agnostic):
  Passaging (محرك التقطيع) → Atomization (محرك التذرير) → Excerpting (محرك الاقتطاف) → Taxonomy (محرك التصنيف) → Synthesis (محرك التوليف)
Layer 3:
  Scholar Interface (واجهة العالم) — consumes all engine and shared component outputs.

## Pre-Work Protocol

1. Read the engine's CLAUDE.md (auto-loaded on directory entry).
2. Read the engine's SPEC.md — the authoritative behavioral specification.
3. Read input/output schemas referenced in the SPEC (from `schemas/`).
4. Run existing tests. Compare counts to CLAUDE.md — update if stale.

## Post-Work Protocol

1. Run the engine's tests: `cd engines/<n> && python -m pytest tests/ -q`
2. If behavior changed → update SPEC.md in the same session.
3. If state changed (test counts, known issues) → update engine CLAUDE.md.
4. If vocabulary changed → flag for VISION.md §2 review.

## Architectural Constraints (always active)

- **Normalization boundary (§7.6).** No source-format-specific logic in Phase 2 engines.
- **Self-containment (§5.1).** Every excerpt is independently understandable.
- **Multi-model consensus (§2.2).** Content decisions use independent LLM agreement.
- **Human gates (§9).** No irreversible library change without owner approval.
- **Priority: Accuracy > Protection > Intelligence (§1.5).**
- **Text integrity (§5.1).** Excerpt primary_text is never modified by any engine.
- **Metadata is synthesis fuel (D-023).** Never strip metadata; the synthesizer needs all of it.
- **Fail-loud (D-033).** Low-confidence decisions get flags, not silent defaults.
- **ABD legacy has zero design authority (D-019).** SPECs define what to build.

## Run All Tests

```
python -m pytest engines/*/tests/ shared/*/tests/ -q
```

## Current Priorities

Milestone 1: Source engine + normalization engine (Shamela format) end-to-end.
See `NEXT.md` for the specific current task.
