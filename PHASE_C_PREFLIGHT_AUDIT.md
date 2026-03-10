# Phase C Pre-Flight Audit — Everything That Touches Real Money

**Date:** 2026-03-10
**Auditor:** Claude Chat (Architect)
**Scope:** Every component between "owner runs script" and "API bill arrives"

---

## Cost Model

| Component | Per Book | 50 Books | % of Total |
|-----------|---------|----------|-----------|
| Command A input ($2.50/M) | $0.0075 | $0.38 | 12% |
| Command A output ($10/M) | $0.0120 | $0.60 | 19% |
| Opus 4.6 input ($5/M) | $0.0150 | $0.75 | 23% |
| Opus 4.6 output ($25/M) | $0.0300 | $1.50 | 47% |
| **Total (no retries)** | **$0.0645** | **$3.23** | |
| Retries (10% estimate) | | $0.32 | |
| Fallbacks (5% estimate) | | $0.07 | |
| **Total worst case** | | **$5.61** | |

**OpenRouter fee:** 5.5% on credit purchase. On $3-6 of OpenRouter usage (Command A + fallback), that's ~$0.20 overhead.

**Key insight:** Opus output tokens are 47% of total cost. But the absolute cost (~€3-5) is negligible. The real financial risk is having to RE-RUN due to a preventable error. A single full re-run doubles the bill.

---

## Findings — Fixes Required Before Any API Call

### FINDING 1 (CRITICAL): build_prompt_context field-name mismatches

**Status:** Specified in PHASE_C_TASK_SPEC.md Pre-Requisite 0
**Impact:** 54% of books lose muhaqiq data, 74% lose edition data
**Cost of NOT fixing:** If we discover after 50 books that the LLM never saw muhaqiq data, we'd need to re-run all 50 books = $3-6 wasted.

### FINDING 2 (MODERATE): No temperature parameter set

**File:** `shared/consensus/src/consensus.py`, line 134
**Current:** `max_tokens=4000` — no temperature
**Problem:** Both models use their default temperature (Anthropic: 1.0, Cohere: varies). For structured JSON metadata classification, temperature=0 is optimal:
- Deterministic: same book twice → same output
- Less verbose: lower token count at temperature=0
- Less hallucination: no "creative" scholarly_context fabrication

**Fix:** Add `temperature=0` to the `client.create()` call in `_call_model`:
```python
result = await asyncio.wait_for(
    client.create(
        messages=msgs,
        response_model=response_model,
        max_tokens=4000,
        temperature=0,   # ← ADD THIS
    ),
    timeout=MODEL_TIMEOUT,
)
```

**Risk:** Verify Instructor passes temperature through to both Anthropic and OpenRouter backends. It should — temperature is a standard parameter. Test in dry-run.

### FINDING 3 (LOW): HTML entity residue in text_sample

**File:** `engines/source/src/text_utils.py` — `strip_tags`
**Status:** `strip_tags` correctly decodes HTML entities via `html.unescape()`. The decoded output contains invisible Unicode characters (zero-width non-joiners U+200C, non-breaking spaces U+00A0) which waste ~2-5% of text_sample tokens on non-informational characters.

**Decision:** NOT fixing for Phase C. The waste is ~50 tokens/book × 50 books × $5/M = $0.01. Not worth the regression risk of changing text processing before a money-spending run. Document for Phase D cleanup.

### FINDING 4 (LOW): Instructor max_retries=0 (default)

**Current:** Instructor's `client.create()` is called without `max_retries`, defaulting to 0. This means if the LLM returns invalid JSON that doesn't match InferenceOutput, Instructor fails immediately.
**Our mitigation:** `_call_model` wraps the call in its own retry loop (`MAX_RETRIES_PER_MODEL = 2`), catching all exceptions. So Instructor's validation failure is caught and the call is retried.
**Difference:** Instructor's retry sends the error message back to the LLM ("field X failed because..."), helping it self-correct. Our retry just sends the original prompt again.
**Decision:** NOT changing for Phase C. Step 0 achieved 100% parse rate on 4/5 models with the current setup. Adding Instructor retries could introduce unexpected behavior (extra API calls we don't track). Document for Phase D if parse failures appear.

### FINDING 5 (INFO): Prompt structure is 68% static, 32% variable

The system message (2321 chars) + JSON schema in user message (2630 chars) + post-schema instructions (1980 chars) = ~7000 chars of IDENTICAL content sent with every API call. Only the prompt_context (~500 chars) and text_sample (~2000 chars) change per book.

**Optimization opportunity:** Anthropic prompt caching could save ~$0.45 across 50 books on the Opus 4.6 calls. However:
- Requires code changes to add cache_control headers
- Only works on Anthropic direct calls, not OpenRouter
- $0.45 savings vs engineering risk of caching bugs
- **Decision:** NOT implementing for Phase C. The savings are $0.45 on a $3-5 run. Not worth the risk. Implement for Phase E (2500 books) where savings would be ~$20.

---

## Findings — Already Correct, Verified

### VERIFIED: All prompt enum values match code enums
- 18 Genre values: ✅ match
- 7 StructuralFormat values: ✅ match
- 3 AuthorityLevel values: ✅ match
- 4 WorkLevel values: ✅ match
- 7 GenreRelationType values: ✅ match
- Genre synonym mapping file: ✅ present and comprehensive

### VERIFIED: Prompt template quality
- System message: clear role definition, appropriate domain expertise listed
- Critical rules: confidence calibration guidance is good (0.50 for uncertainty, <0.80 for ambiguous author)
- Multi-layer detection rules: correctly distinguish sharh (multi-layer) from ta'aqqubat (single-layer with citations)
- scholarly_context guidance: correctly prefers null over fabrication, honest context_richness self-assessment
- **No prompt changes needed.**

### VERIFIED: Consensus mechanism
- Both models called concurrently (good — no wasted sequential latency)
- Author agreement function: name similarity ≥0.90 AND death date ±10 years (appropriate thresholds)
- Disagreement → human gate (correct — never silently pick one answer)
- Fallback model triggers only when Command A fails (correct — doesn't waste money on Opus failures)
- Canonical result selection: higher author_identification_confidence wins (sensible)

### VERIFIED: Error isolation
- Each book runs in its own temp library (tmpdir)
- Failures in one book cannot affect others
- SourceEngineError is caught and structured

---

## Pre-Flight Checklist (Claude Code must verify ALL before full run)

### Before writing any code:
- [ ] Read this document
- [ ] Read PHASE_C_TASK_SPEC.md (all pre-requisites)
- [ ] Read PHASE_C_FINAL_SELECTION.md (book list)

### Pre-Requisite fixes:
- [ ] Pre-Req 0: Fix build_prompt_context (muhaqiq_name_raw, edition_raw, + 5 new fields)
- [ ] Pre-Req 0 test: build_prompt_context on fixture 02 now shows "Muhaqiq/Editor: أحمد محمد عبد الدايم"
- [ ] Temperature fix: Add temperature=0 to _call_model in consensus.py
- [ ] Temperature test: Verify Instructor passes temperature through (check API logs in dry-run)
- [ ] Pre-Req 1: _full_consensus_result field in MetadataInferenceResult
- [ ] Pre-Req 2: Format B fixture
- [ ] Pre-Req 3: COST_LOG.json

### Script validation:
- [ ] Dry-run mode: validates environment, API keys, book paths
- [ ] Dry-run mode: makes a trivial API call to verify both keys work
- [ ] 2-book test: one fixture (03_fiqh), one new book
- [ ] 2-book test: extraction.json present with _debug fields
- [ ] 2-book test: prompt_sent.json saved BEFORE API call
- [ ] 2-book test: prompt_sent.json shows muhaqiq_name_raw in fields_present (for 03_fiqh: no muhaqiq, so it should be in fields_absent; use fixture 06_usul which has a muhaqiq)
- [ ] 2-book test: llm_responses/ has full InferenceOutput per model
- [ ] 2-book test: consensus.json has agreement details
- [ ] 2-book test: result.json validates against SourceMetadata
- [ ] 2-book test: COST_LOG.json updated per-book
- [ ] 2-book test: cost per book in expected range ($0.04-0.15)
- [ ] Resume test: re-run skips completed books
- [ ] Budget ceiling test: --budget-eur 0.01 stops after first book

### All tests pass:
- [ ] Full test suite: 768+ tests passing, 0 failures
- [ ] No regressions from temperature addition or prompt_context fix

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| API key invalid/expired | Low | Full re-run | Dry-run validates keys with test call |
| Model deprecated mid-run | Very Low | Partial re-run | 50 books takes ~30 min — unlikely |
| Instructor version incompatibility | Low | Full re-run | Test on 2 books first |
| Rate limiting (Anthropic) | Medium | Delays | Sequential processing with natural pauses |
| Rate limiting (OpenRouter) | Medium | Delays | Sequential processing |
| Command A API down | Low | Fallback to GPT-5.4 | Consensus module handles this automatically |
| Parse failure on complex book | Medium | 1 book error | Error recorded, book marked for re-run |
| Temperature=0 breaks Instructor | Very Low | Revert change | Test in 2-book run; revert if issues |
| Prompt context fix regression | Low | Wrong metadata | Test on all 13 fixtures before full run |

---

## Self-Analysis: Bugs Found in My Own Task Spec

### BUG 1 (CRITICAL): Monkey-patch targeted WRONG module

**What I wrote:** Patch `shared.consensus.src.consensus.evaluate`
**Why it's wrong:** Python's `from X import Y` copies the reference into the importing module's namespace. Patching `X.Y` does NOT affect the copy that `metadata_inference.py` already has.
**What it should be:** Patch `engines.source.src.engine.infer_metadata` — this captures the MetadataInferenceResult (which, after Pre-Req 2, contains the full ConsensusResult).
**Impact if not caught:** The Phase C script would silently produce empty llm_responses/ directories for all 50 books. We'd discover this after spending $5-7 and need to re-run.
**Status:** FIXED in task spec.

### BUG 2 (CRITICAL): Pre-pipeline extraction creates lock that blocks pipeline

**What I wrote:** Call `stage_source()` then `extract_metadata()` before `acquire_source()`
**Why it's wrong:** `stage_source()` creates a `.kr_processing` lock file with exclusive mode (`open("x")`). When `acquire_source()` internally calls `stage_source()` on the same path, it finds the lock and FAILS with a contention error.
**What it should be:** Call `detect_format()` then `extract_metadata()` directly — no staging, no lock. Extraction is read-only.
**Impact if not caught:** Every book in Phase C would crash with a lock contention error before making any API calls. $0 wasted but a full debugging session lost.
**Status:** FIXED in task spec.

### OBSERVATION 1: Text sample includes title page in ~17% of books

Some Shamela books have their first body page as a title/colophon page (repeating author, publisher). The text_sample correctly skips the metadata CARD but can't distinguish title-page body-divs from content body-divs. In affected books, ~300 of 2000 chars are redundant.
**Decision:** NOT fixing for Phase C. The LLM still gets ~1700 chars of actual body text. Document for Phase E optimization.

### OBSERVATION 2: Isolated temp libraries = scholar registry Case A untested

Each Phase C book gets its own empty registry. The author_agreement_fn's Case A (both models match an existing record) never fires — only Case B (name similarity) is tested. If Case A has a bug, Phase C won't catch it.
**Decision:** Correct for Phase C (independent probes). Phase D must use a shared registry.

### OBSERVATION 3: Actual cost likely ~$0.15/book, not $0.065

Step 0 cost €1.80 for 13 books = ~$0.15/book. My theoretical estimate was $0.065. The 2.3× discrepancy likely comes from Instructor schema overhead tokens and default-temperature verbosity. Updated 50-book estimate: ~$7.50 + retries ≈ ~$9 ≈ ~€8. Still well within ceiling.
