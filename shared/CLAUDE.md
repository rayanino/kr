# Shared Infrastructure

Cross-engine components used by two or more engines. Code belongs here only when it serves multiple engines (VISION.md §13.2.5).

## Components

- consensus/ — Multi-model LLM agreement (LiteLLM + Instructor). Used by source, atomization, excerpting, taxonomy.
- validation/ — Schema validation, structural integrity checks. Used by all engines.
- human_gate/ — Owner approval gates for irreversible library changes. Used by all engines.
- feedback/ — Correction storage, pattern analysis, regression coordination. Spans all engines.
- user_model/ — Owner's study history, knowledge gaps, preferences. Used by scholar interface.
- scholar_authority/ — Canonical scholar identities, biographical data, teacher-student graph. Used by source, excerpting, taxonomy, synthesis.

## Current State

ABD-era code archived to reference/archive/abd_code/. Engine src/ and tests/ directories are clean.
Each component has its own SPEC.md (authoritative) and CLAUDE.md (orientation).
All SPECs need refinement before implementation — see SPEC Refinement Status in each CLAUDE.md.
