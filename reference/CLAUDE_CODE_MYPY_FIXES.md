# Claude Code Prompt: Fix mypy Type Errors

## Context

`mypy engines/source/src/ --ignore-missing-imports --explicit-package-bases` reports
37 errors across 9 files. 21 are pydantic false positives (mypy doesn't understand
`Field(default=...)` as providing `__init__` defaults). The remaining 16 are real
type errors including 2 crash risks.

**Goal:** Zero mypy errors. All 511 existing tests must still pass.

---

## Strategy

1. Fix 14 real type errors with minimal code changes (Fixes 1-5, 7, 9 below).
2. Suppress 2 real-but-safe type mismatches with `# type: ignore` + comment (Fixes 6, 8).
3. Suppress the 21 pydantic false positives with `# type: ignore[call-arg]` comments.
4. Run `pytest engines/source/tests/ -v` — all 511 must pass.
5. Run `mypy engines/source/src/ --ignore-missing-imports --explicit-package-bases` — 0 errors.

---

## Fix 1 — config.py: _load_json return type (eliminates 4 errors)

**File:** `engines/source/src/config.py`
**Lines:** 81, 85, 89, 93
**Problem:** `_load_json()` returns `list | dict` but is assigned to `list[str]`,
`dict[str, dict]`, etc. `json.loads` actually returns `Any`.
**Fix:** Change the return annotation on line 53.

```python
# Line 53 — BEFORE:
def _load_json(path: Path) -> list | dict:

# Line 53 — AFTER:
from typing import Any
def _load_json(path: Path) -> Any:
```

Note: `Any` is already imported at the top of some files; check if config.py needs the import.
Actually config.py does NOT currently import `Any`. Add it to the imports.

**Why this is correct:** `json.loads` returns `Any`. The callers already assign to typed
variables which enforce the expected shape. The `list | dict` annotation was giving
false precision that mypy couldn't reconcile with the specific target types.

---

## Fix 2 — validation.py: variable retyping (eliminates 1 error)

**File:** `shared/validation/src/validation.py`
**Lines:** 66, 69
**Problem:** `current = data` types `current` as `dict[str, Any]`, then
`current = current.get(part)` assigns `Any | None` — type mismatch.
**Fix:** Declare `current` as `Any` on line 66.

```python
# Line 66 — BEFORE:
    current = data

# Line 66 — AFTER:
    current: Any = data
```

**Why this is correct:** `current` intentionally walks through heterogeneous nested
structures. `Any` is the honest type — after the first `.get()` call, it could be
anything.

---

## Fix 3 — scholar_authority.py: elif branch (eliminates 2 errors)

**File:** `shared/scholar_authority/src/scholar_authority.py`
**Lines:** 468-470
**Problem:** Two `if` branches reuse the name `merged` — first as `list`, then as
`dict`. Mypy can't prove they're mutually exclusive (both are `if`, not `if/elif`).
Line 469 assigns a `dict` to a variable mypy tracks as `list`, then line 470 calls
`.update()` on what mypy thinks is a `list`.
**Fix:** Change the second `if` to `elif` on line 468.

```python
# Line 468 — BEFORE:
            if isinstance(old_value, dict) and isinstance(new_value, dict):

# Line 468 — AFTER:
            elif isinstance(old_value, dict) and isinstance(new_value, dict):
```

**Why this is correct:** A value cannot be both `list` and `dict` at runtime. The
branches were always mutually exclusive; `elif` makes that explicit. No behavioral
change.

---

## Fix 4 — consensus.py (shared): BaseException check (eliminates 1 error)

**File:** `shared/consensus/src/consensus.py`
**Line:** 224
**Problem:** `asyncio.gather(return_exceptions=True)` returns items of type
`ModelResponse | BaseException`. The `isinstance(resp, Exception)` check on line 224
doesn't cover `BaseException` subtypes like `KeyboardInterrupt`, so the `else`
branch has type `ModelResponse | BaseException` — mypy correctly flags the append.
**Fix:** Widen to `BaseException`.

```python
# Line 224 — BEFORE:
        if isinstance(resp, Exception):

# Line 224 — AFTER:
        if isinstance(resp, BaseException):
```

**Why this is correct:** `asyncio.gather(return_exceptions=True)` can surface
`BaseException` subclasses (e.g., `KeyboardInterrupt`, `SystemExit`). The handler
wraps them as failed `ModelResponse` objects, which is the right behavior for any
exception type.

---

## Fix 5 — consensus.py (source engine): None narrowing (eliminates 2 errors)

**File:** `engines/source/src/consensus.py`
**Lines:** 109-113
**Problem:** After the None checks at lines 101 and 105, both `chain_a` and
`chain_b` are logically guaranteed non-None. But mypy can't narrow through the
`(chain_a is None) != (chain_b is None)` pattern on line 105.
**Fix:** Add an assert on line 108, before the existing comment.

The current code at lines 106-109 is:
```python
        return False, HumanGateTrigger.WORK_MATCH_UNCERTAIN.value
                                          # ← line 107 is blank
    # Both have genre chains — compare title and author   # ← line 108
    title_sim = normalized_name_similarity(                # ← line 109
```

Insert the assert between the blank line 107 and the comment on line 108:
```python
        return False, HumanGateTrigger.WORK_MATCH_UNCERTAIN.value

    assert chain_a is not None and chain_b is not None  # narrowed by lines 101-106
    # Both have genre chains — compare title and author
    title_sim = normalized_name_similarity(
```

**Why this is correct:** The None checks at lines 101 and 105 cover all cases where
either is None. If execution reaches line 108+, both must be non-None. The assert
documents this invariant and satisfies mypy.

---

## Fix 6 — scholar_registry.py: Literal assignment (eliminates 1 error)

**File:** `engines/source/src/registries/scholar_registry.py`
**Line:** 109
**Problem:** `death_date_source` parameter is `Optional[str]` but line 109 assigns
it to `ScholarAuthorityRecord.death_date_source` which is
`Optional[Literal["extraction", "author_raw_text", "inference", "absent"]]`.
**Why NOT narrow the parameter:** The caller at `engine.py:350` passes
`getattr(inference, "death_date_source", None)` which is `Optional[str]`.
Narrowing the parameter would create a new mypy error at the call site.
**Fix:** Suppress the assignment with a type: ignore comment.

```python
# Line 109 — BEFORE:
        new_record.death_date_source = death_date_source

# Line 109 — AFTER:
        new_record.death_date_source = death_date_source  # type: ignore[assignment]  # validated upstream by _determine_death_date_source()
```

**Why this is safe:** `_determine_death_date_source()` in `metadata_inference.py`
only returns one of the four literal values or None. The type mismatch is a chain
of imprecise annotations, not a real data integrity risk.

---

## Fix 7 — metadata_inference.py: return type (eliminates 2 errors)

**File:** `engines/source/src/metadata_inference.py`
**Line:** 263
**Problem:** Function `apply_confidence_caps` declares return type
`dict[str, float]` but two entries (`genre_chain_confidence` at line 301 and
`level_confidence` at line 297) are `Optional[float]`.
**Fix:** Widen the return annotation.

```python
# Line 263 — BEFORE:
) -> dict[str, float]:

# Line 263 — AFTER:
) -> dict[str, float | None]:
```

**Check downstream:** The consumer is `_build_confidence_scores` in `engine.py`
(line 146) which reads from `inference.confidence_scores` — typed as bare `dict`
(no type params) in `MetadataInferenceResult`. Since bare `dict` → `dict[Any, Any]`,
all `.get()` calls return `Any`, which is compatible with any target type. No
downstream mypy errors are introduced by this return type change.

---

## Fix 8 — metadata_inference.py: Callable variance (eliminates 1 error)

**File:** `engines/source/src/metadata_inference.py`
**Line:** 475
**Problem:** `agreement_fn` is typed `Callable[[InferenceOutput, InferenceOutput], bool]`
but `evaluate()` expects `Callable[[BaseModel, BaseModel], bool] | None`.
Mypy is correct about contravariance — `InferenceOutput` is a subtype of `BaseModel`,
but for Callable *parameters*, the subtype relationship reverses.
**Fix:** Suppress with type: ignore. A `cast()` would require 3 new imports for one line.

```python
# Line 475 — BEFORE:
        agreement_fn=agreement_fn,

# Line 475 — AFTER:
        agreement_fn=agreement_fn,  # type: ignore[arg-type]  # InferenceOutput is BaseModel; variance is safe
```

**Why this is safe:** `evaluate()` always dispatches `InferenceOutput` instances
(it uses the same `response_model`). The `BaseModel` parameter type in `evaluate()`
is just an overly-general annotation.

---

## Fix 9 — engine.py: Optional[str] gate field (eliminates 2 errors)

**File:** `engines/source/src/engine.py`
**Lines:** 611, 612
**Problem:** `gate_error.field` is `Optional[str]` (from `ValidationError.field`),
but line 611 passes it to `gate_low_confidence()` which expects `str`, and line 612
passes it to `dict.get()` which expects `str`.
**Fix:** Default before use. Add a local variable before the if/elif chain.

```python
# Before line 608 (the `if gate_error.check == "confidence_threshold":` line),
# add:
                    field_name = gate_error.field or "unknown"

# Then change lines 609-613:
# BEFORE:
                    if gate_error.check == "confidence_threshold":
                        gate_low_confidence(
                            source_id,
                            gate_error.field,
                            data_for_validation.get(gate_error.field, ""),
                            0.0,
                        )

# AFTER:
                    if gate_error.check == "confidence_threshold":
                        gate_low_confidence(
                            source_id,
                            field_name,
                            data_for_validation.get(field_name, ""),
                            0.0,
                        )
```

**Why this is correct:** If a validation check creates a gate error without
specifying a field (field=None), the current code would crash with `TypeError`
when passed to `gate_low_confidence(field: str)`. Defaulting to `"unknown"` makes
the error visible in the human gate checkpoint without crashing.

---

## Pydantic False Positives — Add type: ignore comments (eliminates 21 errors)

These are all "Missing named argument" errors where the fields have Pydantic
`Field(default=...)` or `Field(None, ...)` defaults. Mypy without the pydantic
plugin can't see these defaults. The pydantic mypy plugin has version fragility
(incompatible between pydantic v2.x and different mypy versions), so suppression
comments are the stable fix.

### scholar_registry.py — lines 99 and 147

```python
# Line 99 — add at end of line:
    new_record = ScholarAuthorityRecord(  # type: ignore[call-arg]  # Pydantic Field defaults

# Line 147 — add at end of line:
    new_record = ScholarAuthorityRecord(  # type: ignore[call-arg]  # Pydantic Field defaults
```

Both constructors provide all truly-required fields (canonical_id, canonical_name_ar,
sources_encountered_in, last_updated). The "missing" args (death_date_source,
sectarian_tradition, methodological_stance, record_completeness,
data_provenance_score, genealogy_metadata, cross_validation) all have defaults.

### work_registry_store.py — lines 46 and 69

```python
# Line 46 — add at end of line:
    return WorkRegistryEntry(  # type: ignore[call-arg]  # Pydantic Field defaults

# Line 69 — add at end of line:
    return WorkRegistryEntry(  # type: ignore[call-arg]  # Pydantic Field defaults
```

Missing `citation_count` has `Field(0, ...)` default.

### engine.py — line 183

```python
# Line 183 — add at end of line:
    return GenreChain(  # type: ignore[call-arg]  # Pydantic Field defaults
```

Missing `base_work_id` has `Field(None, ...)` default.

### engine.py — line 458

```python
# Line 458 — add at end of line:
            metadata = SourceMetadata(  # type: ignore[call-arg]  # Pydantic Field defaults
```

Missing `enrichment_tracking`, `compositional_profile`, `difficulty_prediction`,
`tahqiq_fingerprint` all have `Optional[...] = Field(None, ...)` defaults.

---

## Verification

After all fixes, run:

```bash
# 1. All tests pass
pytest engines/source/tests/ -v
# Expected: 511 passed

# 2. Zero mypy errors
mypy engines/source/src/ --ignore-missing-imports --explicit-package-bases
# Expected: Success: no issues found

# 3. Quick sanity — run the 13-fixture ground truth
pytest engines/source/tests/test_ground_truth.py -v
# Expected: all pass
```

If mypy still reports errors after all fixes, list them. Do NOT suppress real errors
with `# type: ignore` — only suppress the confirmed pydantic false positives listed
above.

---

## Summary Table

| # | File | Lines | Category | Fix |
|---|------|-------|----------|-----|
| 1 | config.py | 53 | return type | `_load_json → Any` |
| 2 | validation.py | 66 | variable type | `current: Any = data` |
| 3 | scholar_authority.py | 468 | branch logic | `if → elif` |
| 4 | consensus.py (shared) | 224 | exception type | `Exception → BaseException` |
| 5 | consensus.py (source) | 108 | None narrowing | add `assert` |
| 6 | scholar_registry.py | 109 | Literal assign | `# type: ignore[assignment]` |
| 7 | metadata_inference.py | 263 | return type | `float → float \| None` |
| 8 | metadata_inference.py | 475 | Callable variance | `# type: ignore[arg-type]` |
| 9 | engine.py | 608-613 | Optional[str] | default `field_name` |
| — | 5 files | 6 sites | pydantic | `# type: ignore[call-arg]` |
