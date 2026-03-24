# NEXT — Excerpting Engine: Fix PE-1 through PE-6

## Current Position

- **Phase 3.4 (Validation):** ✅ ACCEPTED (14 triage fixes + F-R1 fix)
- **Phase 3 orchestrator:** ✅ ACCEPTED
- **Output writer:** ✅ ACCEPTED
- **Pipeline wrapper:** ✅ ACCEPTED
- **Test baseline:** 550 passed, 2 skipped, 0 failed
- **Pre-engine-completion items:** PE-1 through PE-6 (all Open — fix them now)

## What to Do

Apply exactly the 6 fixes listed below. Each has a finding ID, file + line, what to change, and why. Do NOT improvise beyond what is specified.

Read these files before starting:
- `engines/excerpting/contracts.py` — VerificationResult, VerificationItem
- `engines/excerpting/src/phase3_consensus.py` — consensus logic, _find_majority functions
- `engines/excerpting/src/phase3_enrichment.py` — enrichment chunk matching
- `engines/excerpting/src/writer.py` — output functions
- `engines/excerpting/src/pipeline.py` — run_excerpting orchestrator

## Fixes

### PE-1: Add item_index uniqueness validator to VerificationResult

**File:** `engines/excerpting/contracts.py`

**Problem:** `VerificationResult.items` can have duplicate `item_index` values from LLM responses. Consensus logic matches items by index — duplicates cause wrong verifications.

**Change:**
1. Add `from pydantic import model_validator` to imports (if not already present).
2. Add a `@model_validator(mode="after")` to `VerificationResult`:
```python
class VerificationResult(BaseModel):
    """Top-level verification response (SPEC §7.3.2)."""

    items: list[VerificationItem]

    @model_validator(mode="after")
    def _check_item_index_uniqueness(self) -> "VerificationResult":
        indices = [item.item_index for item in self.items]
        if len(indices) != len(set(indices)):
            dupes = [i for i in indices if indices.count(i) > 1]
            raise ValueError(
                f"Duplicate item_index values in VerificationResult: {set(dupes)}"
            )
        return self
```

**Test:** Add to `engines/excerpting/tests/test_phase3_consensus.py`:
```python
class TestVerificationResultValidator:
    """PE-1: VerificationResult rejects duplicate item_index."""

    def test_unique_indices_accepted(self) -> None:
        """Non-duplicate indices → valid."""
        result = VerificationResult(items=[
            VerificationItem(item_index=0, agrees=True, confidence=0.9, reasoning="ok"),
            VerificationItem(item_index=1, agrees=True, confidence=0.9, reasoning="ok"),
        ])
        assert len(result.items) == 2

    def test_duplicate_indices_rejected(self) -> None:
        """Duplicate item_index → ValidationError."""
        import pytest
        with pytest.raises(Exception, match="Duplicate item_index"):
            VerificationResult(items=[
                VerificationItem(item_index=0, agrees=True, confidence=0.9, reasoning="ok"),
                VerificationItem(item_index=0, agrees=False, confidence=0.8, reasoning="no"),
            ])
```
Add `VerificationResult` and `VerificationItem` to the test file imports from `engines.excerpting.contracts`.

### PE-2: Fix resolution_method mislabel for verifier abstention

**File:** `engines/excerpting/src/phase3_consensus.py`

**Problem:** Line 370: `resolution_method="all_3_disagree_gate"` fires when the verifier abstained (no alternative). It's not "all 3 disagree" — it's "no majority found."

**Change:**
1. Line 370: Change `"all_3_disagree_gate"` to `"no_majority_gate"`.

That's it. One string change.

**Test:** Add to `engines/excerpting/tests/test_phase3_consensus.py`:
```python
def test_abstention_resolution_method(self) -> None:
    """Verifier abstention + no escalation majority → no_majority_gate, not all_3_disagree_gate."""
    # This test belongs in the existing TestAuthorAttributionConsensus class
    # or a new class — place it where author attribution consensus tests live.
    pass  # Implement: mock verifier returning agrees=False, alternative=None
    # Then mock escalation returning a different value than enrichment
    # Verify resolution_method == "no_majority_gate"
```
Note: if writing this test is complex (needs full consensus mocking), skip it and document as "PE-2 label fix verified by grep" in the commit message. The label is purely diagnostic — no downstream consumer reads it.

### PE-3: Remove dead _find_majority function

**File:** `engines/excerpting/src/phase3_consensus.py`

**Problem:** `_find_majority` (line 433) is never called in production code. Only `_find_majority_flexible` (line 444, called at line 337) is used.

**Change:**
1. Delete the `_find_majority` function (lines 433–441).
2. In `engines/excerpting/tests/test_phase3_consensus.py`:
   - Remove `_find_majority` from the import line (line 29).
   - Delete the two test methods that call `_find_majority`: `test_find_majority_2_of_3` (lines 306-309) and `test_find_majority_all_different` (lines 311-312).

**Why:** Dead code is a maintenance burden and a confusion source.

### PE-4: Document alt_id chunk matching fallback

**Files:** `engines/excerpting/src/phase3_enrichment.py` and `engines/excerpting/src/phase3_consensus.py`

**Problem:** Three-level chunk ID lookup (div_id → split_id → alt_id) is undocumented.

**Change in both files:** Add comments and logging to the chunk matching block. The pattern is identical in both files — apply the same change to each.

In `phase3_enrichment.py` (around line 380):
```python
        chunk_id = exc.div_id
        if chunk_id not in chunk_map:
            # DD-PE-4: Defensive chunk ID fallback for split chunks.
            # Phase 1 may produce chunk_id as "div_id_chunk_N" for splits.
            split_id = f"{exc.div_id}_chunk_{exc.chunk_index}"
            if split_id in chunk_map:
                chunk_id = split_id
                logger.info(
                    "DD-PE-4: Using split_id fallback %s for %s.",
                    split_id, exc.excerpt_id,
                )
            else:
                alt_id = f"{exc.div_id}_{exc.chunk_index}"
                if alt_id in chunk_map:
                    chunk_id = alt_id
                    logger.warning(
                        "DD-PE-4: Using alt_id fallback %s for %s.",
                        alt_id, exc.excerpt_id,
                    )
```

Apply the identical pattern in `phase3_consensus.py` (around line 690).

**Test:** No new test needed — defensive code that should never fire under normal operation.

### PE-5: Document pipeline ad-hoc error strings

**File:** `reference/SPEC_ERRATA.md`

**Problem:** `PHASE2_FATAL`, `PHASE2_SKIPPED`, `PHASE3_FATAL` in pipeline.py are not SPEC §8.1 error codes.

**Change:** Append to `reference/SPEC_ERRATA.md`:
```markdown
## SPEC-NOTE-13: Pipeline-level error strings are not §8.1 codes — RESOLVED

**Found:** Session 4 review, PE-5 (March 2026).
**Severity:** Documentation.
**Problem:** `pipeline.py` uses `PHASE2_FATAL`, `PHASE2_SKIPPED`, `PHASE3_FATAL` as error strings in `ExcerptingResult.errors`. These are not in SPEC §8.1's error code table.
**Resolution:** These are pipeline-level operational diagnostics, not per-excerpt validation errors. SPEC §8.1 defines per-excerpt codes (EX-A-*, EX-C-*, EX-M-*, EX-V-*, EX-G-*). Pipeline failures affect the entire source and don't have per-excerpt scope. The ad-hoc strings include the exception message for debugging.
**Fixed in:** PE-5 documentation (no code change).
```

### PE-6: Implement processing_log.jsonl

**File (new function):** `engines/excerpting/src/writer.py`

**Problem:** SPEC §2.2.1 defines `processing_log.jsonl` as an output but it was never implemented.

**Change:**
1. Add to `writer.py`:
```python
def write_processing_log(
    source_id: str,
    errors: list[str],
    timings: dict[str, float],
    excerpt_count: int,
    gate_count: int,
    output_dir: Path,
) -> Path:
    """Write processing log to processing_log.jsonl (§2.2.1).

    Single JSON line with run metadata for debugging and telemetry.
    """
    import datetime

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "processing_log.jsonl"

    entry = {
        "source_id": source_id,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "excerpt_count": excerpt_count,
        "gate_count": gate_count,
        "error_count": len(errors),
        "errors": errors,
        "timings": timings,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    logger.info("Wrote processing log to %s", output_path)
    return output_path
```

2. In `pipeline.py`, add `write_processing_log` to the imports from writer.
3. At the end of `run_excerpting`, add a NEW if-block AFTER the existing `if output_dir is not None and result.excerpts:` block (line 170) and BEFORE the `logger.info("Excerpting complete...")` line (line 188). This must NOT be nested inside the existing block — the processing log should be written even when excerpt_count is 0:
```python
    # Write processing log (§2.2.1)
    if output_dir is not None:
        log_path = write_processing_log(
            source_id=source_id,
            errors=result.errors,
            timings=result.timings,
            excerpt_count=len(result.excerpts),
            gate_count=len(result.gate_entries),
            output_dir=output_dir,
        )
        result.output_paths["processing_log"] = log_path
```

**Test:** Add to `engines/excerpting/tests/test_writer.py`:
```python
class TestWriteProcessingLog:
    """PE-6: processing_log.jsonl output."""

    def test_writes_valid_jsonl(self, tmp_path) -> None:
        """Processing log contains all required fields."""
        from engines.excerpting.src.writer import write_processing_log
        import json

        path = write_processing_log(
            source_id="src_test",
            errors=["EX-M-005", "EX-M-002"],
            timings={"phase1": 0.5, "phase2": 1.2},
            excerpt_count=10,
            gate_count=2,
            output_dir=tmp_path,
        )
        assert path.exists()
        content = json.loads(path.read_text(encoding="utf-8").strip())
        assert content["source_id"] == "src_test"
        assert content["excerpt_count"] == 10
        assert content["gate_count"] == 2
        assert content["error_count"] == 2
        assert content["errors"] == ["EX-M-005", "EX-M-002"]
        assert "timestamp" in content
        assert content["timings"]["phase1"] == 0.5

    def test_empty_errors_and_timings(self, tmp_path) -> None:
        """Empty errors and timings produce valid log."""
        from engines.excerpting.src.writer import write_processing_log
        import json

        path = write_processing_log(
            source_id="src_empty",
            errors=[],
            timings={},
            excerpt_count=0,
            gate_count=0,
            output_dir=tmp_path,
        )
        content = json.loads(path.read_text(encoding="utf-8").strip())
        assert content["error_count"] == 0
        assert content["errors"] == []
```

## Verification

After all fixes:
1. `PYTHONPATH=. python -m pytest engines/excerpting/tests/ -q --tb=short` → ≥552 passed, 0 failed
2. `grep -c "_find_majority[^_]" engines/excerpting/src/phase3_consensus.py` → 0 (dead code removed)
3. `grep "no_majority_gate" engines/excerpting/src/phase3_consensus.py` → 1 hit
4. `grep "DD-PE-4" engines/excerpting/src/phase3_enrichment.py engines/excerpting/src/phase3_consensus.py` → 2+ hits per file
5. `grep "SPEC-NOTE-13" reference/SPEC_ERRATA.md` → 1 hit
6. `grep "write_processing_log" engines/excerpting/src/writer.py engines/excerpting/src/pipeline.py` → 2+ hits

## Do NOT Do

1. Do NOT modify Phase 1, Phase 2, or Phase 3.1-3.3 code (those are ACCEPTED).
2. Do NOT add new SPEC error codes — PE-5 documents the existing ad-hoc strings.
3. Do NOT change the alt_id fallback behavior — PE-4 only adds comments and logging.
4. Do NOT implement anything beyond what is specified here.
5. After completing the fixes, commit and push.
6. Do NOT proceed to the next session.
7. Stop after this task. Do not continue to the next session.
