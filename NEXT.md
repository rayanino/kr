# NEXT — Engine Build Blueprint

## Current position: Source engine COMPLETE → Create repeatable build process
## What to do: Trace the entire source engine journey and distill it into a specific, repeatable blueprint
## Context: Source engine done. 6 engines remaining. Before building anything, we need the blueprint that makes every engine build systematic instead of improvised.
## Owner action needed: YES — This is a Claude Chat session (architect + owner)

## Deliverable sequence (strict order)

### 1. Blueprint (`reference/ENGINE_BUILD_BLUEPRINT.md`)
Trace the full source engine history (git log, lesson files, evaluation
reports, bug patterns) and distill into a concrete, step-by-step recipe
for building any engine. NOT abstract protocol — specific actions,
specific quality checks, specific handoff formats.

**Critical requirement:** Every step that produces output must include a
mandatory critical self-review protocol. Minimum 2 rounds. Clear
instructions for what the review checks. No raw output accepted without
structured verification. This was learned the hard way — the source
engine's worst bugs were self-review failures.

### 2. Decision Playbook (`reference/DECISION_PLAYBOOK.md`)
Every pattern, heuristic, domain rule, and anti-pattern accumulated
during the source engine build. This is the institutional memory that
makes future agents (or Claude Chat sessions) effective without
re-learning everything from scratch.

### 3. Repo cleanup
Remove stale files, archive completed work, ensure the repo is clean
and navigable for the normalization engine project.

### After these three: discuss agent team architecture for autonomous building.

## Key source material for the Blueprint chat
- Git log: 160+ commits tracing the full journey
- `engines/source/review/PHASE_A_LESSONS.md` — deterministic phase lessons
- `tests/results/source_engine/phase_c/PHASE_C_LESSONS.md` — LLM phase lessons
- `tests/results/source_engine/phase_d/PHASE_D_LESSONS.md` — calibration lessons
- `PHASE_D_AGGREGATION_REPORT.md` — evaluation methodology
- `PHASE_D_CRITICAL_REVIEW.md` — adversarial review of results
- `PHASE_D_PATTERN_ANALYSIS.md` — systematic patterns found
- `reference/SOURCE_ENGINE_COMPLETION.md` — what the finished engine looks like
- `reference/PRE_BATCH_EXECUTION_PROTOCOL.md` — the hardening process
- `reference/PRE_BATCH_VERIFICATION_PLAN.md` — verification methodology
- `SILENT_FAILURES.md` — failure modes discovered
- `skills/shared/ENGINE_PROTOCOL.md` — the existing abstract protocol
- `KNOWLEDGE_INTEGRITY.md` — corruption threats
- `RESULT_PRESERVATION.md` — how results feed downstream

## Budget
- Spent: €30.60
- Remaining: ~€69.40
