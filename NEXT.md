# NEXT — Excerpting Engine: Harden LLM Integration Infrastructure

## Current Position

- **Baseline:** 554 tests passing (2 skipped), 0 failed
- **Commit:** `7582dc65` (next: harden LLM integration infrastructure)
- **Architecture audit:** Architect + CC dual review complete. All findings verified against code.
- **LLM calls tested with real models:** ❌ ZERO — this session makes the ground solid

## What to Do

Two categories of work, in order:

### Part A: Fix 9 bugs found by dual audit

These bugs MUST be fixed before any real LLM call. Each has an exact location and code pattern.

### Part B: Write integration test infrastructure

Two scripts + two test files for the LLM Integration Test Protocol (Round 1).

## Read First

1. `engines/excerpting/SPEC.md` — §5.5 (retry policy, MAX_TOKENS), §7.2 (enrichment), §7.3 (consensus)
2. `engines/excerpting/src/phase3_orchestrator.py` — Phase 3 staging (especially lines 108-165)
3. `engines/excerpting/src/phase2_classify.py` — retry loop pattern (lines 370-470)
4. `engines/excerpting/src/phase3_enrichment.py` — enrichment retry (lines 400-460)
5. `engines/excerpting/src/phase3_consensus.py` — consensus flow (lines 660-830)
6. `engines/excerpting/contracts.py` — response models (lines 587-670)
7. `reference/protocols/LLM_INTEGRATION_TEST_PROTOCOL.md` — Phase B spec
8. `experiments/architecture_test/run_tests.py` — reference client creation (lines 155-175)

## Part A: Bug Fixes

Apply FIX-9 before FIX-1 — FIX-9 removes a parameter from `run_consensus`, and FIX-1 wraps the `run_consensus` call in try/except. The order matters.

### FIX-1 (B-1): Add graceful degradation to consensus stage

**File:** `engines/excerpting/src/phase3_orchestrator.py`
**Location:** Lines 138-149 (the bare `run_consensus(...)` call — note FIX-9 changes its signature first)
**Problem:** If `run_consensus` raises any non-programming-bug exception, ALL enriched excerpts are lost. The enrichment stage (lines 108-127) has try/except with graceful degradation but the consensus stage does not, despite the comment saying "graceful degradation."
**Fix:** Wrap in try/except matching the enrichment pattern. On failure, keep enrichment-only excerpts with `"verification_skipped"` flag. Pattern:

```python
try:
    all_excerpts, gate_entries = run_consensus(
        excerpts=all_excerpts,
        chunks=chunks,
        verify_client=verify_client,  # NOTE: enrich_client removed by FIX-9
        escalation_client=escalation_client,
        config=config,
        source_metadata=source_metadata,
    )
    result.gate_entries.extend(gate_entries)
except Exception as exc:
    if isinstance(exc, (TypeError, AttributeError, NameError, KeyError,
                        IndexError, ZeroDivisionError, StopIteration)):
        raise  # Programming bugs must crash
    logger.error(
        "Consensus verification failed — degrading to enrichment-only: %s", exc,
    )
    result.errors.append(f"CONSENSUS_FAILED: {exc}")
    flagged = []
    for e in all_excerpts:
        flags = list(e.review_flags)
        if "verification_skipped" not in flags:
            flags.append("verification_skipped")
        flagged.append(e.model_copy(update={"review_flags": flags}))
    all_excerpts = flagged
```

### FIX-2 (NEW): Enable Instructor schema retry (max_retries=2)

**Files:** ALL five LLM call sites:
1. `phase2_classify.py` line 343: `max_retries=0` → `max_retries=2`
2. `phase2_group.py` line 172: `max_retries=0` → `max_retries=2`
3. `phase3_enrichment.py` line 233: `max_retries=0` → `max_retries=2`
4. `phase3_consensus.py` line 168: `max_retries=0` → `max_retries=2`
5. `phase3_consensus.py` line 419: `max_retries=0` → `max_retries=2`

**Why:** With `max_retries=0`, Instructor NEVER retries schema validation failures. At temperature=0, a fresh retry sends the identical prompt and gets the identical broken output. Retries are wasted.

With `max_retries=2`, Instructor's `handle_reask_kwargs` appends the LLM's broken response AND the Pydantic validation error to the messages, then retries. The LLM sees what it produced and what was wrong, and can self-correct. This is essential for FIX-6 (Literal types) — without it, a Literal validation error always fails.

**Semantics:** Instructor uses tenacity's `stop_after_attempt(max_retries)`. Empirically verified:
- `max_retries=0` → 1 attempt (no retry) — current behavior
- `max_retries=1` → 1 attempt (no retry) — SAME as 0, tenacity minimum
- `max_retries=2` → 2 attempts (1 retry) — what we want
- `max_retries=3` → 3 attempts (2 retries)

**Budget impact:** Our outer loop (RETRY_COUNT=2, 3 iterations) handles API errors, offset failures, coverage violations. Instructor's retry handles schema errors. Worst case: 3 outer × 2 Instructor = 6 LLM calls per chunk. But schema errors are rare with well-designed prompts (verified: all prompts match SPEC exactly), so typical is 1-2 calls. The SPEC §5.5.2 "3 attempts" refers to our outer loop iterations. Instructor's internal retry is an implementation detail of how each attempt is made.

### FIX-3 (B-10): Improve Phase 3 enrichment exception handling

**File:** `engines/excerpting/src/phase3_enrichment.py`
**Location:** `run_phase3_enrichment`, inner retry loop (line 437)
**Problem:** Catches bare `Exception` with no discrimination. No exponential backoff for API rate limits. No error codes per attempt.
**Fix:** Add `from pydantic import ValidationError` to imports. Replace the bare `except Exception` with:

```python
except ValidationError as e:
    # Defense-in-depth: with max_retries=2, Instructor handles
    # schema validation internally. This catches edge cases
    # where a ValidationError escapes Instructor's retry.
    logger.warning(
        "Phase 3 enrichment attempt %d/%d validation error for chunk %s: %s",
        attempt + 1, max_attempts, chunk_id, e,
    )

except Exception as e:
    wait_seconds = 2 ** attempt
    logger.warning(
        "Phase 3 enrichment attempt %d/%d API error for chunk %s: %s. "
        "Backing off %ds.",
        attempt + 1, max_attempts, chunk_id, str(e), wait_seconds,
    )
    time.sleep(wait_seconds)
```

Ensure `import time` is present in the file's imports.

### FIX-4 (B-12): Flag excerpts with incomplete verification

**File:** `engines/excerpting/src/phase3_consensus.py`
**Location:** `run_consensus`, the per-excerpt loop (line 787)
**Problem:** When the verifier LLM returns fewer items than requested, excerpts that needed consensus pass through unflagged — silently unverified.
**Fix:** After the `excerpt_to_vi` dict is built (around line 785), create a set of unit_indices that needed verification:

```python
units_needing_verification = {exc.unit_index for exc, _ in excerpts_with_items}

for exc in chunk_excerpts:
    vis_for_exc = excerpt_to_vi.get(exc.unit_index, [])
    if not vis_for_exc:
        if exc.unit_index in units_needing_verification:
            # Needed consensus but got no verification items — flag it
            flags = list(exc.review_flags)
            if "verification_incomplete" not in flags:
                flags.append("verification_incomplete")
            all_results.append(exc.model_copy(update={"review_flags": flags}))
        else:
            # Didn't need consensus — pass through normally
            all_results.append(exc)
        continue
```

### FIX-5 (B-2): Fix duplication path in run_consensus

**File:** `engines/excerpting/src/phase3_consensus.py`
**Location:** `run_consensus`, retry loop (around line 720)
**Problem:** If `verify_chunk` returns `None` inside the retry loop, excerpts are added to `all_results` AND then the post-loop `if verification_result is None` check adds them AGAIN with flags. Currently unreachable because `any_needs_consensus` guard catches the no-verification case first, but structurally fragile — if `_needs_consensus` behavior changes, V-P3-1 would crash with duplicate excerpt IDs.
**Fix:** Use a boolean to track whether the loop already handled the chunk:

```python
verification_result = None
loop_handled = False
for attempt in range(max_attempts):
    try:
        start_time = time.monotonic()
        vr = verify_chunk(
            chunk, chunk_excerpts, verify_client, config, source_metadata
        )
        latency = time.monotonic() - start_time

        if vr is None:
            all_results.extend(chunk_excerpts)
            loop_handled = True
            break

        verification_result = vr
        logger.info(
            "Phase 3 consensus: chunk_id=%s latency=%.1fs "
            "attempt=%d items=%d",
            chunk_id, latency, attempt + 1, len(vr[0].items),
        )
        loop_handled = True
        break

    except Exception as e:
        logger.warning(
            "Phase 3 consensus attempt %d/%d failed for chunk %s: %s",
            attempt + 1, max_attempts, chunk_id, str(e),
        )

if not loop_handled:
    # All retry attempts failed — keep enrichment-only with flag
    for exc in chunk_excerpts:
        flags = list(exc.review_flags)
        if "verification_skipped" not in flags:
            flags.append("verification_skipped")
        all_results.append(exc.model_copy(update={"review_flags": flags}))
    continue

if verification_result is None:
    # verify_chunk returned None — already added in loop
    continue

# Normal consensus resolution path continues below...
```

### FIX-6 (P-4+B-7): Validate ResolvedScholar.role with Literal type

**File:** `engines/excerpting/contracts.py`
**Location:** class `ResolvedScholar` (line 587), class `ScholarAttribution` (line 115)
**Problem:** `role` is free-form `str`. LLM can return any string ("narrator", "مؤلف", "author"). With `max_retries=2` (FIX-2), Instructor will retry once with the Literal validation error in context — the LLM sees "role must be 'quoted_opinion', 'classification_frame', or 'refuted_position'" and can self-correct.

**Fix:** Add `Literal` to the typing import on line 19:
```python
from typing import Literal, Optional
```

Change `ResolvedScholar.role` (line 593):
```python
role: Literal["quoted_opinion", "classification_frame", "refuted_position"] = Field(
    description="One of: quoted_opinion, classification_frame, refuted_position"
)
```

Change `ScholarAttribution.role` (line 124) the same way:
```python
role: Literal["quoted_opinion", "classification_frame", "refuted_position"] = Field(
    description="One of: quoted_opinion, classification_frame, refuted_position"
)
```

**Test impact:** All existing tests use valid role values (`quoted_opinion`, `classification_frame`). Verify with grep: `grep -rn 'role=' engines/excerpting/tests/` — no test uses an invalid role value.

### FIX-7 (B-6): Cross-check evidence_refs vs takhrij_data

**File:** `engines/excerpting/src/phase3_enrichment.py`
**Location:** `apply_enrichment` function (around line 280)
**Problem:** If the LLM omits `takhrij_data` for a hadith unit, it silently defaults to `[]`. No warning. Deterministic F-DET-5 detected hadith evidence markers, but the LLM found no hadith to trace.
**Fix:** BEFORE the `review_flags` list is written into the `model_copy` update dict, add:

```python
# Cross-check: F-DET-5 detected hadith but LLM found no takhrij
has_hadith_evidence = any(er.type == "hadith" for er in exc.evidence_refs)
if has_hadith_evidence and not ue.takhrij_data:
    if "hadith_evidence_no_takhrij" not in review_flags:
        review_flags.append("hadith_evidence_no_takhrij")
    logger.warning(
        "F-DET-5 detected hadith evidence but LLM enrichment returned no "
        "takhrij_data for unit %d in chunk %s.",
        exc.unit_index, exc.div_id,
    )
```

### FIX-8 (B-11): Deduplicate _LEVEL_ORDER constant

**File:** `engines/excerpting/src/phase3_consensus.py`
**Problem:** `_LEVEL_ORDER` dict defined locally in both `_resolve_self_containment` (line 452) and `_parse_self_containment` (line 508). If one is updated and the other isn't, behavior diverges silently.
**Fix:** Define once as a module-level constant near the top of the file (after imports):

```python
_SC_LEVEL_ORDER: dict[SelfContainmentLevel, int] = {
    SelfContainmentLevel.FULL: 2,
    SelfContainmentLevel.PARTIAL: 1,
    SelfContainmentLevel.DEPENDENT: 0,
}
```

Replace both local `_LEVEL_ORDER` definitions in `_resolve_self_containment` and `_parse_self_containment` with `_SC_LEVEL_ORDER`.

### FIX-9 (B-9): Remove unused enrich_client parameter

**File:** `engines/excerpting/src/phase3_consensus.py`
**Location:** `run_consensus` function signature (line 660-663)
**Problem:** `enrich_client` parameter accepted but never used in the function body.
**Fix:**
1. Remove `enrich_client: instructor.Instructor,` from the `run_consensus` signature.
2. In `engines/excerpting/src/phase3_orchestrator.py` (line ~140), remove `enrich_client=enrich_client,` from the `run_consensus(...)` call.

**Do FIX-9 BEFORE FIX-1** — FIX-1 wraps this call in try/except, so applying FIX-9 first avoids editing inside the try/except block.

## Part B: Integration Test Infrastructure

### SCRIPT-1: `scripts/run_integration_test.py`

Per the LLM Integration Test Protocol Phase B spec. Standalone script, NOT a pytest test.

**Behavior:**
1. Accept CLI args: `--package-path`, `--output-dir`, `--source-metadata` (JSON string with keys: author_name, work_title, science, source_school)
2. Load `NormalizedPackage` from the path (manifest.json + content.jsonl)
3. Create THREE Instructor clients via OpenRouter (see client creation pattern below)
4. Register logging hooks on each client (see hooks pattern below)
5. Run pipeline phases directly (NOT via `run_excerpting` — we need intermediates):
   - Phase 1: `run_phase1(package, config)` → save `phase1_chunks.json`
   - Phase 2a: `run_phase2a(chunks, enrich_client, config)` → save per-chunk `phase2a_classifications/chunk_{id}.json`
   - Phase 2b: `run_phase2b(chunks, classified, enrich_client, config)` → save per-chunk `phase2b_groupings/chunk_{id}.json`
   - Phase 3: `run_phase3(chunks, grouped, classified, config, enrich_client, verify_client, escalation_client, source_metadata)` → save excerpts + gates
   - Write: `excerpts.jsonl`, `gate_queue.jsonl`, `processing_log.jsonl`
6. Save timing per phase and per chunk to `timing.json`
7. Record git commit hash, timestamp, config dump in `run_metadata.json`
8. Output dir structure: `integration_tests/run_{timestamp}/`

**Client creation:**
```python
import instructor
import openai

def create_client(timeout: int = 120) -> instructor.Instructor:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY not set")
    return instructor.from_openai(
        openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            timeout=timeout,
        ),
        mode=instructor.Mode.JSON,
    )
```

Create three clients: `enrich_client` (for Phase 2 + Phase 3 enrichment), `verify_client` (for Phase 3 consensus), `escalation_client` (for 3-model escalation).

**Logging via Instructor hooks (NOT a wrapper class):**

The Instructor client has a native hooks API. Register hooks AFTER creating each client:

```python
import json
import time
from pathlib import Path
from typing import Any

def make_hook_logger(output_dir: Path, client_name: str):
    """Create logging hooks for an Instructor client."""
    req_dir = output_dir / "raw_llm_requests"
    resp_dir = output_dir / "raw_llm_responses"
    req_dir.mkdir(parents=True, exist_ok=True)
    resp_dir.mkdir(parents=True, exist_ok=True)

    call_counter = {"n": 0}
    call_start_time = {"t": 0.0}

    def on_request(**kwargs: Any) -> None:
        call_counter["n"] += 1
        call_start_time["t"] = time.monotonic()
        call_id = f"{client_name}_{call_counter['n']:04d}"
        entry = {
            "call_id": call_id,
            "model": kwargs.get("model"),
            "temperature": kwargs.get("temperature"),
            "max_tokens": kwargs.get("max_tokens"),
            "messages": [
                {"role": m.get("role", ""), "content": m.get("content", "")[:500]}
                for m in kwargs.get("messages", [])
            ],
        }
        path = req_dir / f"{call_id}.json"
        path.write_text(json.dumps(entry, ensure_ascii=False, indent=2))

    def on_response(response: Any) -> None:
        call_id = f"{client_name}_{call_counter['n']:04d}"
        latency = time.monotonic() - call_start_time["t"]
        entry = {
            "call_id": call_id,
            "latency_seconds": round(latency, 2),
            "model": getattr(response, "model", None),
            "usage": response.usage.model_dump() if hasattr(response, "usage") and response.usage else None,
            "finish_reason": response.choices[0].finish_reason if hasattr(response, "choices") and response.choices else None,
            "raw_content": response.choices[0].message.content[:2000] if hasattr(response, "choices") and response.choices else None,
        }
        path = resp_dir / f"{call_id}.json"
        path.write_text(json.dumps(entry, ensure_ascii=False, indent=2))

    def on_error(error: Exception) -> None:
        call_id = f"{client_name}_{call_counter['n']:04d}"
        entry = {"call_id": call_id, "error_type": type(error).__name__, "error": str(error)[:500]}
        path = resp_dir / f"{call_id}_error.json"
        path.write_text(json.dumps(entry, ensure_ascii=False, indent=2))

    return on_request, on_response, on_error

# Attach hooks:
req_hook, resp_hook, err_hook = make_hook_logger(output_dir, "enrich")
enrich_client.on("completion:kwargs", req_hook)
enrich_client.on("completion:response", resp_hook)
enrich_client.on("completion:error", err_hook)
# Repeat for verify_client and escalation_client
```

Hooks are exception-safe (Instructor swallows hook errors with a warning). They never crash the pipeline.

**MOCK mode:** Support `--mock` flag. In mock mode:
- Skip API key validation
- Use `MagicMock` clients that return plausible responses (use `_make_classification_result` etc. from conftest.py patterns)
- Still save all output files (tests the file-writing infrastructure)

**Pre-run checklist (automated, print results):**
- Validate normalized package loads
- Test API key with a 10-token call (skip in mock mode)
- Verify output directory is empty or doesn't exist
- Record and print git commit hash; warn if uncommitted changes

### SCRIPT-2: `scripts/review_helper.py`

Per the LLM Integration Test Protocol Appendix (decontextualization spot-check method).

**Behavior:**
1. Accept CLI args: `--run-dir` (integration test run directory)
2. Load `excerpts.jsonl` and `phase1_chunks.json` from the run directory
3. For each excerpt:
   a. Find the chunk (match chunk_id to div_id, or use DD-PE-4 split fallback)
   b. Map word offsets to character offsets using `_build_token_char_map` from `engines/excerpting/src/phase2_classify.py` (import it — do NOT duplicate the function)
   c. Extract 200 chars before char_start and 200 chars after char_end from `assembled_text`
4. Print formatted blocks (one per excerpt) showing: excerpt_id, div path, unit_index, function, self_containment, school, attribution info, topic keywords, 200-char pre-context, full primary_text, 200-char post-context, review_flags, gate_flags, quoted_scholars count, evidence_refs count, takhrij_data status.
5. Options:
   - `--filter FLAG_NAME` — show only excerpts with that review_flag or gate_flag
   - `--filter PARTIAL` / `--filter DEPENDENT` / `--filter FULL` — filter by self_containment
   - `--excerpt-id EXC_ID` — show single excerpt
   - `--summary` — print aggregate counts: total excerpts, counts by self_containment, counts by primary_function, gate_flag counts, review_flag counts

### TEST-1: Pydantic parsing robustness tests

**File:** `engines/excerpting/tests/test_pydantic_robustness.py`

Test cases using `model_validate` (simulates Instructor parsing):
1. `ClassificationResult` with extra unknown fields → accepted (Pydantic ignores extras by default)
2. `ClassifiedSegment` with `scholarly_function="unknown_type"` → raises (enum validation)
3. `UnitEnrichment` with `school_confidence` as string `"0.8"` → coerced to float
4. `UnitEnrichment` with `takhrij_data` key absent → defaults to `[]`
5. `UnitEnrichment` with `excerpt_topic` as empty list → accepted (V-P3-4 flags later)
6. `ResolvedScholar` with `role="narrator"` → raises `ValidationError` (Literal validation, after FIX-6)
7. `ResolvedScholar` with `confidence=1.5` → raises (ge=0.0, le=1.0)
8. `VerificationResult` with duplicate `item_index` values → raises (model_validator)
9. `EnrichmentResult` with `len(enrichments) != total_units` → document what happens (no model_validator checks this)
10. `ExtractionResult` with `notes=None` vs `notes` absent → both accepted

### TEST-2: Error recovery tests

**File:** `engines/excerpting/tests/test_error_recovery.py`

Use conftest helpers: `_make_mock_instructor_client`, `_make_assembled_chunk`, `_make_classification_result`.

1. **Single-chunk LLM failure (skip + continue):** Create 3 chunks. Mock client with `side_effect` that raises `Exception("API error")` for chunk 2 but returns valid results for chunks 1 and 3. Call `run_phase2a`. Verify: chunks 1 and 3 have classified segments in the result dict; chunk 2 is absent; logs contain chunk 2 failure.

2. **Exponential backoff on API error:** Mock client with `side_effect=[Exception("rate limit"), valid_result]`. Call `run_phase2a` on 1 chunk. Verify: result contains the chunk (succeeded on retry 2). Measure elapsed time — should be ≥2s (exponential backoff `2**0 = 1s` wait, but total ≥2s due to the sleep).

3. **Semantically invalid response → coverage retry:** Mock `classify_chunk` to return a `ClassificationResult` with a gap between segments (segment 0 covers words 0-5, segment 1 covers words 8-10, gap at 6-7). `verify_segments` should raise `ValueError`. The outer loop retries with error feedback. On retry, return a valid result. Verify: the chunk succeeds on the second attempt.

## Design Decisions

- **DD-H-1:** Instructor mode is `instructor.Mode.JSON` (validated in experiment, confirmed compatible with all three model families via OpenRouter). Do NOT use `OPENROUTER_STRUCTURED_OUTPUTS` — untested and may not work with Anthropic/Cohere via OpenRouter.
- **DD-H-2:** Use Instructor's native hooks API for response logging (`client.on("completion:kwargs", ...)`, `client.on("completion:response", ...)`). Hooks are exception-safe (Instructor swallows errors) and non-invasive (production code unchanged).
- **DD-H-3:** Integration test script calls phase functions directly (not `run_excerpting`) to save intermediates. `source_metadata` is passed explicitly via CLI, bypassing `pipeline.py`'s incomplete population (P-1 — fix deferred to a later session when source engine metadata becomes available).
- **DD-H-4:** `max_retries=2` on all Instructor calls (FIX-2). This gives Instructor exactly 1 schema retry with error context appended to messages. Instructor's `handle_reask_kwargs` includes the LLM's broken response AND the Pydantic validation error — strictly better than our old manual error feedback. Our outer loop (RETRY_COUNT=2, 3 iterations) handles API errors, offset failures, and coverage violations. Division of labor: Instructor fixes schema errors, our loop fixes everything else.
- **DD-H-5:** `ResolvedScholar.role` uses `Literal` type (FIX-6). Combined with `max_retries=2`, if the LLM returns an invalid role, Instructor retries with the validation error in context. The LLM sees "role must be 'quoted_opinion', 'classification_frame', or 'refuted_position'" and self-corrects. If it still fails, `InstructorRetryException` propagates to our outer loop as an `Exception`.
- **DD-H-6:** The `"hadith_evidence_no_takhrij"` flag (FIX-7) is informational. It surfaces the mismatch between deterministic evidence detection and LLM enrichment. The reviewer decides if the LLM missed real hadith or if F-DET-5 produced a false positive.

## Do NOT Do

- Do NOT make real LLM calls in any test. All new tests use mocked clients.
- Do NOT modify the LLM prompt text in any file. Prompts were audited and match SPEC exactly.
- Do NOT change Phase 1 assembly code. This session is Phase 2/3 + infrastructure only.
- Do NOT add the `"llm_enrichment_failed"` flag in the existing `except ValidationError` blocks in phase2_classify.py or phase2_group.py. With `max_retries=2`, these blocks are defense-in-depth — Instructor handles schema errors internally first. Keep the blocks as-is for safety but do NOT expand their logic.
- Do NOT implement anything beyond what is specified here. After completing all fixes, scripts, and tests, commit and push. Do NOT proceed to the next session.

## Verification

After all changes:

1. `python -m pytest engines/excerpting/tests/ -q --tb=short` → **554 + N new tests** passing, 0 failed (N ≈ 15-20 from TEST-1 + TEST-2)
2. Verify FIX-1: `grep -A3 'try:' engines/excerpting/src/phase3_orchestrator.py` — shows try/except around run_consensus
3. Verify FIX-2: `grep 'max_retries' engines/excerpting/src/*.py` — all show `max_retries=2`
4. Verify FIX-3: `grep 'time.sleep' engines/excerpting/src/phase3_enrichment.py` — shows backoff
5. Verify FIX-4: `grep 'verification_incomplete' engines/excerpting/src/phase3_consensus.py` — present
6. Verify FIX-5: `grep 'loop_handled' engines/excerpting/src/phase3_consensus.py` — present
7. Verify FIX-6: `grep 'Literal' engines/excerpting/contracts.py` — shows Literal on role fields
8. Verify FIX-7: `grep 'hadith_evidence_no_takhrij' engines/excerpting/src/phase3_enrichment.py` — present
9. Verify FIX-9: `grep 'enrich_client' engines/excerpting/src/phase3_consensus.py | grep -c 'def run_consensus'` — should be 0 (parameter removed)
10. `scripts/run_integration_test.py --mock --package-path experiments/format_diversity_test/packages/ibn_aqil_v1 --output-dir /tmp/test_run` → completes, output dir has: phase1_chunks.json, phase2a_classifications/, phase2b_groupings/, excerpts.jsonl, processing_log.jsonl, timing.json, run_metadata.json, raw_llm_requests/, raw_llm_responses/
11. `scripts/review_helper.py --run-dir /tmp/test_run --summary` → prints excerpt counts

## After This

- Architect reviews all changes (3-pass review per REVIEW_PROTOCOL.md) in a NEW chat
- If ACCEPTED: run integration test script with ONE real LLM call on ONE chunk to verify client wiring
- Then: Round 1 of LLM Integration Test Protocol (5 books, exhaustive review)

Stop after this task. Do not continue to the next session.
