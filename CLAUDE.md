# خزانة ريان (KR) — Personal Intelligent Islamic Scholarly Library

**Core axiom: The library IS the user's knowledge. An error here is an error in his mind. The knowledge cannot defend itself.**

Full specification: `VISION.md`. Concise context: `STEERING.md`. Decisions: `reference/kr_decisions.md`.
Domain knowledge: `reference/DOMAIN.md`. Quality target: `reference/ENTRY_EXAMPLE.md`.

## Critical Rules (always active, never violate)

1. **Knowledge safety first.** Read `KNOWLEDGE_INTEGRITY.md` — 7 threats, 5 verification layers, 6 invariants.
2. **Frozen sources are immutable.** Once frozen, the bytes never change.
3. **Primary text is never modified.** No correction, no cleanup, no normalization beyond what the SPEC explicitly allows.
4. **Every claim is traceable.** Every statement in an entry traces to a source excerpt or an explicit analytical tag.
5. **Errors fail loudly.** Never silently drop data or default on uncertain decisions. Flag everything.
6. **Human gates are not optional.** No irreversible library change without owner approval.
7. **Metadata flows forward, never deleted.** Every engine passes through ALL upstream metadata (D-023).
8. **Multi-model consensus for content decisions.** Never rely on a single LLM call for attribution, classification, or extraction.
9. **ABD legacy has zero design authority (D-019).** SPECs define what to build. Old code is reference only.
10. **Arabic text is fragile.** Read `.claude/skills/arabic-text/SKILL.md` before ANY text processing code.

## Before You Build Anything

1. Check `.claude/skills/technology-survey/SKILL.md` — search for existing tools first.
2. Read the engine's SPEC.md — it is the authoritative specification.
3. Run the Three Challenges from `CHALLENGE_PROTOCOL.md` before every commit.

## Pipeline

Phase 1: Source → Normalization ─── normalization boundary (حد التطبيع) ───
Phase 2: Passaging → Atomization → Excerpting → Taxonomy → Synthesis
Layer 3: Scholar Interface — consumes all outputs.

## Repository Map

- `engines/` — 7 engines, each with `CLAUDE.md`, `SPEC.md`, `src/`, `tests/`
- `shared/` — 6 components: consensus, validation, human_gate, feedback, user_model, scholar_authority
- `interface/scholar/` — User-facing intelligence layer
- `schemas/` — Inter-engine data contracts
- `library/` — Knowledge product. This IS the user's knowledge.
- `scripts/` — `extract_vision_sections.py`, `decompose_spec.py`, `verify_metadata_flow.py`, `check_compliance.py`, `refinement_status.py`
- `tests/integration/` — Cross-engine integration tests

## Session Protocol

- `NEXT.md` — your task. Read it first. It tells you what to read next.
- `CONTEXT_BUDGET.md` — token costs for every file. Plan your reads.
- `CREATIVE_MANDATE.md` — invention comes before review. Creative Exploration Protocol.
- `SPEC_REFINEMENT.md` — 11-step SPEC improvement cycle (Steps 0-10).
- `SILENT_FAILURES.md` — 7 patterns of output that looks right but is wrong.
- `SESSION_CONTINUITY.md` — bulletproof session handoff rules.
- `PREPARATORY_ROADMAP.md` — 7 work streams for the full preparatory phase.
- `ORCHESTRATOR.md` — implementation session lifecycle (after SPEC refinement).
- `MILESTONES.md` — task decomposition with dependencies.
- `REVIEW_PROTOCOL.md` — design review procedures.
- `CHALLENGE_PROTOCOL.md` — Three Challenges before every commit.
- `KNOWLEDGE_INTEGRITY.md` — 7-threat model for knowledge safety.

## Run All Tests

```
python -m pytest engines/*/tests/ shared/*/tests/ -q
```
