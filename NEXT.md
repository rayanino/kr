# NEXT — Excerpting Engine: Fix F-R1 (isinstance re-raise list)

## Current Position

- **Phase 3.4 (Validation):** 14 triage fixes applied — 3-pass review found 1 finding (F-R1)
- **Phase 3 orchestrator:** Same
- **Output writer:** Same
- **Pipeline wrapper:** Same
- **Test baseline:** 549 passed, 2 skipped, 0 failed

## What to Do

Fix F-R1: Add `IndexError`, `ZeroDivisionError`, `StopIteration` to all three isinstance re-raise tuples.

### The Problem

The isinstance check in three catch blocks currently re-raises only `(TypeError, AttributeError, NameError, KeyError)`. Other programming bugs — `IndexError`, `ZeroDivisionError`, `StopIteration` — are caught by `except Exception`, logged as LLM/phase failures, and the pipeline continues. This violates SPEC §8 ("Every error is loud") because a code bug is misdiagnosed as an infrastructure failure.

Example: An `IndexError` in enrichment logs `"EX-M-002: LLM enrichment failed — degrading to deterministic-only: list index out of range"`. The engineer debugs the LLM API when the real fix is a one-line code change.

### Fix (3 files, 3 lines changed)

**File 1:** `engines/excerpting/src/phase3_orchestrator.py` line 120
```python
# BEFORE:
            if isinstance(exc, (TypeError, AttributeError, NameError, KeyError)):
# AFTER:
            if isinstance(exc, (TypeError, AttributeError, NameError, KeyError, IndexError, ZeroDivisionError, StopIteration)):
```

**File 2:** `engines/excerpting/src/pipeline.py` line 123
```python
# BEFORE:
            if isinstance(exc, (TypeError, AttributeError, NameError, KeyError)):
# AFTER:
            if isinstance(exc, (TypeError, AttributeError, NameError, KeyError, IndexError, ZeroDivisionError, StopIteration)):
```

**File 3:** `engines/excerpting/src/pipeline.py` line 156
```python
# BEFORE:
        if isinstance(exc, (TypeError, AttributeError, NameError, KeyError)):
# AFTER:
        if isinstance(exc, (TypeError, AttributeError, NameError, KeyError, IndexError, ZeroDivisionError, StopIteration)):
```

### New Test

Add one test to `engines/excerpting/tests/test_integration.py` in the `TestPipelineCatchesPhase3Fatal` class:

```python
def test_phase3_indexerror_propagates(self) -> None:
    """Phase 3 IndexError → pipeline re-raises (programming bug, not LLM failure)."""
    package = _make_normalized_package()
    config = ExcerptingConfig()

    with patch(
        "engines.excerpting.src.pipeline.run_phase2a"
    ) as mock_2a, patch(
        "engines.excerpting.src.pipeline.run_phase2b"
    ) as mock_2b, patch(
        "engines.excerpting.src.pipeline.run_phase3",
        side_effect=IndexError("off by one in enrichment"),
    ):
        mock_2a.return_value = {}
        mock_2b.return_value = {}

        with pytest.raises(IndexError, match="off by one"):
            run_excerpting(
                package=package,
                config=config,
                enrich_client=MagicMock(),
            )
```

## Verification

After fix:
1. `PYTHONPATH=. python -m pytest engines/excerpting/tests/ -q --tb=short` → ≥550 passed, 0 failed
2. `grep "IndexError" engines/excerpting/src/phase3_orchestrator.py` → 1 hit (isinstance line)
3. `grep "IndexError" engines/excerpting/src/pipeline.py` → 2 hits (both isinstance lines)

## Do NOT Do

1. Do NOT modify any other code.
2. Do NOT change Phase 1, Phase 2, Phase 3.1-3.3, or contracts.py.
3. Do NOT implement anything beyond what is specified here.
4. After completing the fix, commit and push.
5. Do NOT proceed to the next session.
6. Stop after this task. Do not continue to the next session.
