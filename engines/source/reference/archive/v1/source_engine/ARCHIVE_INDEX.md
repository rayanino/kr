# Source Engine Archive Index

This archive preserves the previous `engines/source` iteration as historical reference.

## Authority Warning

Nothing under this archive is active authority for the new source engine.

Use archived material only to recover:

- corpus facts
- owner-confirmed heuristics
- lessons learned
- architectural reference
- obsolete implementation context

Do not implement against archived specs, prompts, code, or tests without explicit approval from the new source-engine spec.

## Trust Tiers

- `Tier A` — corpus-verified or owner-validated knowledge
- `Tier B` — lessons learned or failure memory
- `Tier C` — architectural reference
- `Tier D` — obsolete implementation snapshot

## Read First

Start with these Tier A / B files when recovering prior knowledge:

- `reference/ABD_INTAKE_SPEC.md`
- `reference/edge_cases.md`
- `review/OWNER_SANITY_CHECK_ANSWERS.md`
- `review/PHASE_A_LESSONS.md`
- `review/STEP0_RESULTS.md`
- `LESSONS.md`
- `src/extractors/shamela_html.py`
- `tests/test_deterministic.py`
- `tests/test_registries.py`
- `tests/test_validation.py`

## Anchor Passages

The highlighted anchor passages from the cleanup plan are illustrative only.
They are not a whitelist. The full archived files remain preserved here.

## Archived Tests

Archived `test_*.py` files are intentionally blocked from pytest collection by the archive-local `conftest.py`.
