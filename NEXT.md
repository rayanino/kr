# NEXT — Excerpting Engine: Session 5/6 Triage Fixes

## Current Position

- **Phase 3.4 (Validation):** EXISTS — CC-authored, architect-triaged, dual-reviewer audit complete
- **Phase 3 orchestrator:** EXISTS — CC-authored, architect-triaged, dual-reviewer audit complete
- **Output writer:** EXISTS — CC-authored, architect-triaged, dual-reviewer audit complete
- **Pipeline wrapper:** EXISTS — CC-authored, architect-triaged, dual-reviewer audit complete
- **Test baseline:** 540 passed, 2 skipped, 0 failed
- **Audit findings:** 27 total — 2 CRITICAL, 5 HIGH, 10 MEDIUM (see below)

## What to Do

Apply exactly the fixes listed below. Each fix has a finding ID, the file + line, what to change, and why. Do NOT improvise beyond what is specified.

Read these files before starting:
- `engines/excerpting/SPEC.md` §7.4 (lines 1893–1913) — validation checks
- `engines/excerpting/SPEC.md` §8.1 (lines 1957–1980) — error codes and severities
- `engines/excerpting/contracts.py` — ExcerptRecord, ExcerptingErrorCodes
- `engines/excerpting/tests/conftest.py` — _make_excerpt_record helper

## Fixes

### Fix 1 (CRITICAL — F-05+F-06): V-P3-2 must DROP excerpt, not just log

**File:** `engines/excerpting/src/phase3_validation.py`

**Problem:** SPEC §8.1 line 1977 defines EX-V-002 as severity ERROR with recovery "Do not produce excerpt." The code logs WARNING and keeps the excerpt. Corrupt excerpts flow to taxonomy.

**Change:**
1. Change `validate_excerpt` return type from `tuple[ExcerptRecord, list[str]]` to `tuple[Optional[ExcerptRecord], list[str]]`. Add `from typing import Optional` if not present.
2. When V-P3-2 fails (line 82), set a local flag `drop = True`.
3. At the end of the function (before the return), if `drop is True`, return `(None, errors)` instead of `(modified, errors)`.
4. Change `logger.warning` to `logger.error` for V-P3-2 (line 84).
5. In `validate_batch`, when `validate_excerpt` returns `None` as the first element, do NOT append to `validated`. Increment a `dropped_count`. Log: `logger.error("V-P3-2: Dropped %d excerpts with text integrity failure.", dropped_count)` after the loop (only if dropped_count > 0).

**Why:** A corrupt excerpt (primary_text doesn't match text_snippet) means offset handling broke. The excerpt's text is wrong. Producing it means the owner reads wrong text attributed to the wrong location.

### Fix 2 (CRITICAL — F-24): Consensus crash must not silently lose gate entries

**File:** `engines/excerpting/src/phase3_orchestrator.py` and `engines/excerpting/src/pipeline.py`

**Problem:** If `run_consensus` crashes, the tuple unpacking never completes. `result.gate_entries` stays empty. V-P3-7 sees "0 expected, 0 found" → PASS. Excerpts that should have gate entries pass without them.

**Change:**
1. In `phase3_orchestrator.py`: Remove the `try/except` block around `run_consensus` (lines 147–164 approximately). Let consensus exceptions propagate up to the caller. Keep the timing and logging lines that come AFTER the successful call.
2. In `pipeline.py`: Wrap the Phase 3 call (currently line 147: `phase3_result = run_phase3(...)`) in a try/except:
   ```python
   try:
       phase3_result: Phase3Result = run_phase3(
           chunks=chunks,
           teaching_units=grouped,
           classified=classified,
           config=config,
           enrich_client=enrich_client,
           verify_client=verify_client,
           escalation_client=escalation_client,
           source_metadata=source_metadata,
       )
   except Exception as exc:
       if isinstance(exc, (TypeError, AttributeError, NameError, KeyError)):
           raise  # Programming bugs must crash
       logger.error("Phase 3 failed for %s: %s", source_id, exc)
       result.errors.append(f"PHASE3_FATAL: {exc}")
       return result
   ```
   This means: consensus crash → Phase 3 crash → pipeline catches → returns empty result with error → source flagged for reprocessing. No silent data loss.

**Why:** If consensus fails, we don't know which excerpts need human review. Continuing means invisible uncertainty — the exact failure V-P3-7 and EX-M-008 exist to prevent. Halting is correct per SPEC §8 line 1919.

### Fix 3 (HIGH — F-12): Remove try/except from deterministic assembly

**File:** `engines/excerpting/src/phase3_orchestrator.py`

**Problem:** `build_deterministic_excerpts` is pure deterministic code. Any exception is a programming bug. The `except Exception` catches TypeErrors, logs them as warnings, and continues. Bugs become invisible.

**Change:**
1. Remove the `try/except` block around `build_deterministic_excerpts` (lines 93–103). Keep:
   ```python
   excerpts = build_deterministic_excerpts(chunk, units, segments)
   all_excerpts.extend(excerpts)
   ```
   If it raises, the exception propagates to the pipeline-level catch from Fix 2.

**Why:** SPEC §8 line 1919: "Every error is loud." A TypeError in deterministic code is a bug that must crash.

### Fix 4 (HIGH — F-15): Remove try/except from Phase 1 in pipeline

**File:** `engines/excerpting/src/pipeline.py`

**Problem:** Phase 1 is entirely deterministic. `except Exception` catches programming bugs and masks them.

**Change:**
1. Remove the `try/except` block around `run_phase1` (lines 103–108). Keep:
   ```python
   chunks, _p1_validation = run_phase1(package, config)
   ```
   If Phase 1 crashes, the exception propagates to the caller of `run_excerpting`.

**Why:** Same as Fix 3. Deterministic code bugs should crash loudly.

### Fix 5 (HIGH — F-01): V-P3-1 duplicate IDs — raise ValueError

**File:** `engines/excerpting/src/phase3_validation.py`

**Problem:** V-P3-1 emits `EX_V_002` (which belongs to V-P3-2). V-P3-1 has no SPEC-defined error code because duplicate deterministic IDs indicate a programming bug.

**Change:**
1. In `validate_batch`, replace the `if duplicate_ids:` block (lines 241–247) with:
   ```python
   if duplicate_ids:
       raise ValueError(
           f"V-P3-1: Duplicate excerpt IDs detected — "
           f"this is a bug in the ID generation algorithm: {duplicate_ids}"
       )
   ```

**Why:** Excerpt IDs are deterministic (div_id + chunk_index + unit_index). Duplicate = algorithm bug = crash.

### Fix 6 (HIGH — F-02): Consensus crash error code — subsumed by Fix 2

No separate change needed. Fix 2 removes the try/except around consensus, so the wrong `EX_M_004` code is no longer emitted.

### Fix 7 (MEDIUM — F-08): Gate queue verification must retry before halt

**File:** `engines/excerpting/src/writer.py`

**Problem:** SPEC §8.1 line 1968 says EX-M-008 recovery is "Retry write. If retry fails, halt." Code goes straight to halt with no retry.

**Change:**
1. In `verify_gate_queue`, when `missing` is non-empty (line 176), before raising:
   - Log warning: `logger.warning("V-P3-7: %d missing entries — retrying write + verify.", len(missing))`
   - Call `write_gate_queue(gate_entries, gate_path.parent)` to re-write the file
   - Re-read and re-verify using the same logic (you may extract the read+compare into a helper to avoid duplication)
   - If STILL missing after retry, THEN raise `GateQueueVerificationError`
2. Keep the immediate raise on "file does not exist" (line 131) — no retry for missing file, that's a more severe filesystem failure.

**Why:** SPEC compliance. The retry catches transient filesystem issues.

### Fix 8 (MEDIUM — F-13+F-14): Narrow enrichment exception catch

**File:** `engines/excerpting/src/phase3_orchestrator.py`

**Problem:** `except Exception` in enrichment catches programming bugs alongside LLM failures.

**Change:**
1. In the enrichment try/except (around line 128), replace `except Exception as exc:` with:
   ```python
   except Exception as exc:
       if isinstance(exc, (TypeError, AttributeError, NameError, KeyError)):
           raise  # Programming bugs must crash
   ```
   Keep the rest of the handler body unchanged (log, append error code, continue).

**Why:** Programming bugs should crash. LLM/network failures should degrade gracefully.

### Fix 9 (MEDIUM — F-16): Narrow Phase 2 exception catch in pipeline

**File:** `engines/excerpting/src/pipeline.py`

**Problem:** `except Exception` in Phase 2 catches programming bugs.

**Change:**
1. In the Phase 2 try/except (around line 127), add at the top of the except block:
   ```python
   except Exception as exc:
       if isinstance(exc, (TypeError, AttributeError, NameError, KeyError)):
           raise
   ```
   Keep the rest of the handler unchanged.

**Why:** Same as Fix 8.

### Fix 10 (MEDIUM — F-19): V-P3-9 must handle non-enum types gracefully

**File:** `engines/excerpting/src/phase3_validation.py`

**Problem:** If `model_copy` injects a raw string into `content_types`, `ct.value` raises `AttributeError` instead of emitting `EX-M-010`.

**Change:**
1. Replace the V-P3-9 block (lines 203–212) with:
   ```python
   # V-P3-9: Content type consistency
   for ct in excerpt.content_types:
       if not isinstance(ct, ScholarlyFunction):
           errors.append(ExcerptingErrorCodes.EX_M_010)
           logger.warning(
               "%s: Non-enum content type %r in %s.",
               ExcerptingErrorCodes.EX_M_010,
               ct,
               excerpt.excerpt_id,
           )
       elif ct.value not in _VALID_SCHOLARLY_FUNCTIONS:
           errors.append(ExcerptingErrorCodes.EX_M_010)
           logger.warning(
               "%s: Unknown content type %s in %s.",
               ExcerptingErrorCodes.EX_M_010,
               ct.value,
               excerpt.excerpt_id,
           )
   ```

**Why:** Defense-in-depth should catch the error, not crash with AttributeError.

### Fix 11 (LOW — F-20): Guard write_gate_queue against empty input

**File:** `engines/excerpting/src/writer.py`

**Change:**
1. At the top of `write_gate_queue` (after the docstring, before mkdir), add:
   ```python
   if not gate_entries:
       logger.info("No gate entries — skipping gate_queue.jsonl creation.")
       return output_dir / "gate_queue.jsonl"
   ```

**Why:** SPEC §2.2.1 line 379: "Present only if at least one gate was triggered."

### Fix 12 (LOW — F-22): Collect verify_gate_queue return value

**File:** `engines/excerpting/src/pipeline.py`

**Change:**
1. Change `verify_gate_queue(result.gate_entries, gate_path)` to:
   ```python
   gate_errors = verify_gate_queue(result.gate_entries, gate_path)
   result.errors.extend(gate_errors)
   ```

**Why:** Consistency with error collection pattern.

### Fix 13 (LOW — F-27): Fix misleading log message

**File:** `engines/excerpting/src/phase3_orchestrator.py`

**Change:**
1. Change the `"Phase 3 consensus: SKIPPED (no verify client)."` message to:
   ```python
   logger.info(
       "Phase 3 consensus: SKIPPED (enrich_client=%s, verify_client=%s).",
       enrich_client is not None,
       verify_client is not None,
   )
   ```

**Why:** Accuracy.

### Fix 14: Add design decision comments

**File:** `engines/excerpting/src/phase3_validation.py`

**Change:**
1. At line 180 (before V-P3-8 block), add comment:
   ```python
   # V-P3-8: Footnote relevance — remove orphan footnotes
   # DD-S56-1: Uses marker substring search (⌜ref_marker⌝ in primary_text)
   # instead of offset range check. Correct because Phase 1 assembly embeds
   # footnote markers at their positions in primary_text.
   ```
2. At line 233 (before V-P3-1 block), add comment:
   ```python
   # V-P3-1: Excerpt ID uniqueness
   # DD-S56-2: Batch-level check (exceeds SPEC's per-chunk requirement —
   # catches cross-chunk duplicates too).
   ```

## SPEC Errata

**File:** `reference/SPEC_ERRATA.md` (create if absent, append if exists)

Add:
```
### SPEC-NOTE-4: V-P3-1 has no error code
V-P3-1 (excerpt ID uniqueness) does not specify an error code in §7.4.
Resolution: V-P3-1 violation is a programming bug (IDs are deterministic).
Implementation raises ValueError instead of emitting an error code.

### SPEC-NOTE-5: V-P3-8 implementation uses substring search
SPEC §7.4 says "ref_marker offset falls within character range."
Implementation uses ⌜ref_marker⌝ substring search in primary_text.
Equivalent because Phase 1 assembly embeds markers in text at their positions.

### SPEC-NOTE-6: V-P3-1 batch scope vs per-chunk scope
SPEC §7.4 says validation runs "for a chunk." V-P3-1 runs at batch level.
Batch-level is strictly more thorough (catches cross-chunk duplicates).
```

## New Tests Required

For each behavioral change, add tests. Use `_make_excerpt_record(**overrides)` from conftest.

1. **Fix 1 (V-P3-2 drop):**
   - `validate_excerpt` returns `(None, [EX_V_002])` when primary_text[:80] != text_snippet
   - `validate_batch` excludes None entries from result list
   - Valid excerpts are NOT dropped (regression)
   - Dropped count logged correctly

2. **Fix 2 (consensus crash → Phase 3 crash):**
   - When `run_consensus` raises (mock it), `run_phase3` also raises
   - `run_excerpting` catches Phase 3 crash, returns ExcerptingResult with `"PHASE3_FATAL"` in errors and empty excerpts

3. **Fix 5 (V-P3-1 ValueError):**
   - `validate_batch` with duplicate excerpt_ids raises ValueError
   - Error message includes the duplicate IDs

4. **Fix 7 (gate queue retry):**
   - First verify fails, retry succeeds → no exception raised
   - First verify fails, retry fails → GateQueueVerificationError raised
   - File-not-found → immediate GateQueueVerificationError (no retry)

5. **Fix 10 (V-P3-9 isinstance):**
   - Inject raw string into content_types via `model_copy(update={"content_types": ["not_an_enum"]})` → EX-M-010 emitted, no crash

## Pre-Engine-Completion Items (updated)

| ID | Description | Status |
|----|------------|--------|
| PE-1 | `VerificationResult` lacks `item_index` uniqueness validator | Open |
| PE-2 | `resolution_method` mislabel for verifier abstention | Open |
| PE-3 | Dead `_find_majority` function | Open |
| PE-4 | Undocumented `alt_id` chunk matching fallback | Open |
| PE-5 | Pipeline ad-hoc error strings (F-04) | Open |
| PE-6 | processing_log.jsonl not implemented (SPEC §2.2.1) | Open |

## Verification

After all fixes:
1. `python -m pytest engines/excerpting/tests/ -v --tb=short` → ≥550 passed, 0 failed
2. `grep -c "except Exception" engines/excerpting/src/phase3_orchestrator.py` → exactly 1 (enrichment only)
3. `grep -c "except Exception" engines/excerpting/src/pipeline.py` → exactly 2 (Phase 2 + Phase 3)
4. `grep "logger.warning.*EX_V_002" engines/excerpting/src/phase3_validation.py` → 0 hits
5. `grep "EX_V_002" engines/excerpting/src/phase3_validation.py` → only in V-P3-2 block, NOT in V-P3-1
6. New test count ≥ 10 added

## Do NOT Do

1. Do NOT implement processing_log.jsonl — deferred to PE-6.
2. Do NOT modify Phase 1, Phase 2, or Phase 3.1–3.3 code (those are ACCEPTED).
3. Do NOT modify `contracts.py` unless a fix requires it.
4. Do NOT change the V-P3-8 approach (substring search is correct per DD-S56-1).
5. Do NOT add new SPEC error codes. Use ValueError for V-P3-1, descriptive strings for fatal crashes.
6. Do NOT implement anything beyond what is specified here.
7. After completing the fixes, commit and push.
8. Do NOT proceed to the next session.
9. Stop after this task. Do not continue to the next session.
