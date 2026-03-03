# Shared Infrastructure

Cross-engine infrastructure used by two or more engines. Code belongs here **only** when it serves multiple engines and does not conceptually belong to any single engine (§13.2.5). Code that serves a single engine belongs in that engine's `src/`, even if it could theoretically be reused.

## Contents
- `consensus/` — Multi-model consensus mechanism (§2.2). Used by atomization, excerpting, and taxonomy engines; potentially by the source engine for trustworthiness evaluation (§7.4). Has its own SPEC.md.
- `validation/` — Algorithmic validation tools: schema validation, structural integrity checks (§8.1 Layer 2). Has its own SPEC.md.
- `feedback/` — Feedback loop infrastructure: correction storage, pattern analysis, regression testing coordination (§2.2, §8.3). Spans all engines with human gates. Has its own SPEC.md.

## Current State
Status: Not started. ABD codebase has consensus mechanism (`tools/consensus.py`, ~1700 lines) to be restructured into `shared/consensus/src/` per §12.2.
