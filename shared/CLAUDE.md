# Shared Infrastructure

Cross-engine components used by two or more engines. Code belongs here only when it serves multiple engines.

## Process

Follow `skills/shared/ENGINE_PROTOCOL.md`. Shared components are bootstrapped during the source engine's Step 3 (BUILD) — the source engine builds minimum viable implementations. Later engines extend as needed.

## Components

- **consensus/** — Multi-model LLM agreement (Instructor `from_provider()`). Used by source, atomization, excerpting, taxonomy.
- **validation/** — Schema validation, structural integrity checks. Used by all engines.
- **human_gate/** — Owner approval gates for irreversible library changes. Used by all engines.
- **feedback/** — Correction storage, pattern analysis, regression coordination. Spans all engines.
- **user_model/** — Owner's study history, knowledge gaps, preferences. Used by scholar interface (Stage 2).
- **scholar_authority/** — Canonical scholar identities, biographical data, teacher-student graph. Used by source, excerpting, taxonomy, synthesis.

## Current State

Each component has a SPEC.md (400-460 lines) but no implementation code and no contracts.py. The tracer bullet (Step 0) creates trivial stubs. The source engine's Step 3 builds minimum viable versions (see ENGINE_PROTOCOL.md engine-specific notes for method signatures). Later engines extend what exists.

Four engines (source, normalization, passaging, atomization) have pre-protocol src/ stubs — these are placeholder code from before ENGINE_PROTOCOL.md existed. The tracer bullet reconciles and uses them as starting points.
