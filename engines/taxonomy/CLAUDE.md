# Taxonomy Engine — Build Guide

## Commands
```
test:  PYTHONPATH=. python -m pytest engines/taxonomy/tests/ -x -q --tb=short
lint:  ruff check engines/taxonomy/
```

## Architecture
See `engines/taxonomy/docs/architecture.md` for module structure and data flow.
Core SPEC: `engines/taxonomy/SPEC.md` (551 lines, core-only v1).
Contracts: `engines/taxonomy/contracts_core.py`.

## What This Engine Does (v1)
Places excerpts at leaves in existing science trees. That is its ONLY job.
No tree evolution. No coverage analytics. No cross-science links.

## Critical Constraints

### Arabic Text
- `primary_text` must survive placement **byte-identical**. After writing a placed excerpt file, re-read it and verify. This is non-negotiable (T-1 threat).
- All file I/O uses `encoding="utf-8"`. Windows cp1252 is a known silent failure.

### Provenance (D-023)
- The taxonomy engine ADDS fields to excerpts; it NEVER strips upstream fields.
- Output = `{**original_excerpt, **placement_additions}`.
- If the original excerpt has 35 fields, the output has 35 + taxonomy fields.

### Errors
- Use error codes from SPEC §6. Never silently swallow errors.
- Fatal (per excerpt): reject and log, continue batch.
- Fatal (batch): abort entire run.
- All errors logged with: timestamp, error_code, severity, excerpt_id.

### Tree Loading
- Two YAML formats exist. v1 (nahw/sarf/balagha/imlaa): `taxonomy→nodes` with id/title/children/leaf. v0 (aqidah): nested dict with `_label`/`_leaf`.
- Normalize both to `TreeNode` at load time. NEVER modify source YAML files.
- `__overview` keys in v0 format ARE real nodes (double underscore is naming, not skip signal).

### LLM Calls
- All LLM calls through `shared/llm/cli_adapter.py` (CLIInstructorAdapter).
- Model: `anthropic/claude-opus-4`. Timeout: 600s. Retries: 2.
- Response models are Pydantic v2 classes (BranchSelection, PlacementRanking).
- The adapter handles schema injection, JSON extraction, and validation.

### Routing Rules (SPEC §4.A.3)
- Teaching content: ≥0.80 → live, 0.50-0.79 → staged, <0.50 → unplaced
- Editorial (editorial_note): ≥0.85 → live, 0.50-0.84 → staged, <0.50 → unplaced
- Always-staged (structural_transition, cross_reference): NEVER live — ≥0.50 → staged, <0.50 → unplaced
- Missing/null/unknown primary_function → treated as editorial (safe default)

## Session Status
- **Session 1 DONE** (commit `25368b28`): Deterministic infrastructure — 119 tests, pyright clean
- **Session 2**: LLM adapter + prompt construction + gold baseline test

## Key Files
| File | Purpose |
|------|---------|
| `engines/taxonomy/SPEC.md` | Core v1 specification (authoritative) |
| `engines/taxonomy/contracts_core.py` | Pydantic models and dataclasses |
| `engines/taxonomy/docs/architecture.md` | Module structure |
| `engines/taxonomy/src/placer.py` | PlacementAdapter Protocol (Session 2 implements this) |
| `engines/taxonomy/src/tree_loader.py` | build_branch_view, build_leaf_view (use in prompts) |
| `shared/llm/cli_adapter.py` | LLM interface (do not modify) |
| `library/sciences/*/tree.yaml` | Science trees (do not modify) |
| `library/sciences/taxonomy_registry.yaml` | Active tree versions |
| `integration_tests/smoke_fix_20260329/*/excerpts.jsonl` | Real excerpt data for testing |
| `engines/taxonomy/tests/fixtures/gold_baseline_nahw.yaml` | 12 gold placements for accuracy test |

## Testing
- Deterministic tests: routing, validation, provenance, tree loading, input validation
- Mock LLM tests: end-to-end with deterministic LLM responses
- Real LLM tests: gold baseline (10-15 excerpts with known correct leaves)
- Always run: `PYTHONPATH=. python -m pytest engines/taxonomy/tests/ -x -q --tb=short`

## Scope Control
Do NOT implement anything beyond what NEXT.md specifies.
After completing, commit, push, and STOP.
Do NOT proceed to the next session.
