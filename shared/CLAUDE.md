# Shared Infrastructure

Cross-engine infrastructure used by two or more engines. Code belongs here **only** when it serves multiple engines and does not conceptually belong to any single engine (§13.2.5). Code that serves a single engine belongs in that engine's `src/`, even if it could theoretically be reused.

## Contents
- `consensus/` — Multi-model consensus mechanism (§2.2). Used by atomization, excerpting, and taxonomy engines; potentially by the source engine for trustworthiness evaluation (§7.4). Has its own SPEC.md.
- `validation/` — Algorithmic validation tools: schema validation, structural integrity checks (§8.1 Layer 2). Has its own SPEC.md.
- `feedback/` — Feedback loop infrastructure: correction storage, pattern analysis, regression testing coordination (§2.2, §8.3). Spans all engines with human gates. Has its own SPEC.md.
- `human_gate/` — Human approval gates for irreversible library changes (§9). Enforces approval workflows, logs decisions, supports appeal/override. Has its own CLAUDE.md, SPEC.md, src/, tests/.
- `user_model/` — Tracks owner's study history, demonstrated knowledge, identified gaps, current focus, preferences. Used by scholar interface and potentially by synthesizing engine for personalization. Has its own CLAUDE.md. (D-017)
- `scholar_authority/` — Canonical scholar identities, variant name mappings, biographical data, teacher-student graph, school affiliations. Single source of truth for "who is this scholar?" Used by source, excerpting, taxonomy, and synthesizing engines. Has its own CLAUDE.md. (New — no ABD equivalent)

## Current State
Status: Migrated from ABD. Code in `shared/consensus/src/consensus.py`, `shared/validation/src/cross_validate.py`, `shared/validation/src/run_all_validations.py`, `shared/human_gate/src/human_gate.py`.
