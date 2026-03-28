# NEXT — BLOCKING Fix: EnrichmentResult unit_index uniqueness validator

## Context

Cross-provider audit Finding 7 (BLOCKING): `apply_enrichment` builds a dict via
`{ue.unit_index: ue for ue in enrichment.enrichments}`. If the LLM returns duplicate
`unit_index` values, the dict comprehension silently keeps only the last one. This produces
WRONG metadata (wrong school, wrong topic) with zero signal — no flag, no error, no warning.

`VerificationResult` already has `_check_item_index_uniqueness` (line 669 of contracts.py).
`EnrichmentResult` does not. This is an explicit asymmetry that must be fixed.

## What to Do

### Task 1: Add uniqueness validator to EnrichmentResult

In `engines/excerpting/contracts.py`, add a `@model_validator` to `EnrichmentResult` (line 627):

```python
class EnrichmentResult(BaseModel):
    """Top-level LLM enrichment response (SPEC §7.2.4)."""

    enrichments: list[UnitEnrichment]
    total_units: int

    @model_validator(mode="after")
    def _check_unit_index_uniqueness(self) -> "EnrichmentResult":
        indices = [ue.unit_index for ue in self.enrichments]
        if len(indices) != len(set(indices)):
            dupes = [i for i in indices if indices.count(i) > 1]
            raise ValueError(
                f"Duplicate unit_index in enrichments: {set(dupes)}"
            )
        return self
```

Also add the same to `ExtractionResult` (line 641) — it has the same pattern
(`teaching_units` list with `unit_index` field):

```python
class ExtractionResult(BaseModel):
    """Phase 2b LLM grouping response (SPEC §5.3.4)."""

    teaching_units: list[TeachingUnit]
    total_units: int
    notes: Optional[str] = None

    @model_validator(mode="after")
    def _check_unit_index_uniqueness(self) -> "ExtractionResult":
        indices = [tu.unit_index for tu in self.teaching_units]
        if len(indices) != len(set(indices)):
            dupes = [i for i in indices if indices.count(i) > 1]
            raise ValueError(
                f"Duplicate unit_index in teaching_units: {set(dupes)}"
            )
        return self
```

### Task 2: Add tests for the new validators

In `engines/excerpting/tests/`, add tests that verify:

1. `EnrichmentResult` with unique `unit_index` values validates successfully
2. `EnrichmentResult` with duplicate `unit_index` raises `ValidationError`
3. Same two tests for `ExtractionResult` with `unit_index` in teaching_units
4. Verify the error message includes the duplicate index value

### Task 3: Run full test suite

```bash
python -m pytest --tb=short -q
```

Report pass/fail/skip counts. Zero failures required.

### Task 4: Commit and push

```
fix(contracts): add unit_index uniqueness validators to EnrichmentResult + ExtractionResult

BLOCKING audit finding: duplicate unit_index from LLM silently overwrites
enrichment data via dict comprehension last-wins. VerificationResult already
had _check_item_index_uniqueness (line 669); EnrichmentResult and
ExtractionResult did not. Now all three LLM response models validate
index uniqueness.
```

## Do NOT Do

- Do NOT modify any other files besides contracts.py and test files
- Do NOT add `extra='forbid'` to models (separate task, needs broader analysis)
- Do NOT add the `total_units` semantic check (separate task)
- Do NOT proceed beyond these 4 tasks
