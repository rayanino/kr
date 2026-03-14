# Phase C Pre-Flight Audit — Everything That Touches Real Money

**Date:** 2026-03-10
**Auditor:** Claude Chat (Architect)
**Scope:** Every component between "owner runs script" and "API bill arrives"

---

## Cost Model

| Component | Per Book | 73 Books | % of Total |
|-----------|---------|----------|-----------|
| Command A input ($2.50/M) | $0.0075 | $0.55 | 12% |
| Command A output ($10/M) | $0.0120 | $0.88 | 19% |
| Opus 4.6 input ($5/M) | $0.0150 | $1.10 | 23% |
| Opus 4.6 output ($25/M) | $0.0300 | $2.19 | 47% |
| **Total (no retries)** | **$0.0645** | **$4.71** | |
| Retries (10% estimate) | | $0.47 | |
| Fallbacks (5% estimate) | | $0.10 | |
| **Total worst case** | | **$8.18** | |

**OpenRouter fee:** 5.5% on credit purchase. On $4-8 of OpenRouter usage (Command A + fallback), that's ~$0.30 overhead.

**Key insight:** Opus output tokens are 47% of total cost. But the absolute cost (~€5-8) is negligible. The real financial risk is having to RE-RUN due to a preventable error. A single full re-run doubles the bill.

---

## Findings — Fixes Required Before Any API Call

### FINDING 1 (CRITICAL): build_prompt_context field-name mismatches

**Status:** Specified in PHASE_C_TASK_SPEC.md Pre-Requisite 0
**Impact:** 54% of books lose muhaqiq data, 74% lose edition data
**Cost of NOT fixing:** If we discover after 73 books that the LLM never saw muhaqiq data, we'd need to re-run all 73 books = $5-10 wasted.

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

**Decision:** NOT fixing for Phase C. The waste is ~50 tokens/book × 73 books × $5/M = $0.02. Not worth the regression risk of changing text processing before a money-spending run. Document for Phase D cleanup.

### FINDING 4 (LOW): Instructor max_retries=0 (default)

**Current:** Instructor's `client.create()` is called without `max_retries`, defaulting to 0. This means if the LLM returns invalid JSON that doesn't match InferenceOutput, Instructor fails immediately.
**Our mitigation:** `_call_model` wraps the call in its own retry loop (`MAX_RETRIES_PER_MODEL = 2`), catching all exceptions. So Instructor's validation failure is caught and the call is retried.
**Difference:** Instructor's retry sends the error message back to the LLM ("field X failed because..."), helping it self-correct. Our retry just sends the original prompt again.
**Decision:** NOT changing for Phase C. Step 0 achieved 100% parse rate on 4/5 models with the current setup. Adding Instructor retries could introduce unexpected behavior (extra API calls we don't track). Document for Phase D if parse failures appear.

### FINDING 5 (INFO): Prompt structure is 68% static, 32% variable

The system message (2321 chars) + JSON schema in user message (2630 chars) + post-schema instructions (1980 chars) = ~7000 chars of IDENTICAL content sent with every API call. Only the prompt_context (~500 chars) and text_sample (~2000 chars) change per book.

**Optimization opportunity:** Anthropic prompt caching could save ~$0.65 across 73 books on the Opus 4.6 calls. However:
- Requires code changes to add cache_control headers
- Only works on Anthropic direct calls, not OpenRouter
- $0.45 savings vs engineering risk of caching bugs
- **Decision:** NOT implementing for Phase C. The savings are $0.45 on a $3-5 run. Not worth the risk. Implement for Phase E (2500 books) where savings would be ~$20.

---

## Deep Technical Audit — Money Protection (Session 2)

**Date:** 2026-03-10
**Auditor:** Claude Chat (Architect), second session
**Scope:** LLM prompt, inference orchestration, consensus, Pydantic schema, 13-step pipeline

### FINDING 6 (WARNING): System message has no guidance for new metadata fields

**Status:** Added as Pre-Req 0b in PHASE_C_TASK_SPEC.md
**Impact:** Pre-Req 0a adds Compiler, Commentator, and Riwayah fields to the metadata the LLM sees, but the system message mentions none of them. Risk: LLM confuses compiler with author (critical for مجموع الفتاوى), ignores commentator as multi-layer evidence, and discards riwayah information.
**Fix:** Add 3-line guidance to SYSTEM_MESSAGE in inference_v1.py. Test in 2-book run; revert if regressions.

### FINDING 7 (WARNING): Gate-severity validation errors abort pipeline, losing assembled metadata

**Status:** Added to PHASE_C_TASK_SPEC.md error handling section
**Impact:** When a book triggers a validation gate (disputed attribution, low confidence <0.50, author-science mismatch), engine.py Step 11 creates human gate checkpoints then RAISES `SourceEngineError(LOW_CONFIDENCE)`. The SourceMetadata object was assembled at Step 9 but never returned. Phase C books deliberately selected to trigger gates (D01, D02, G01, E02) would show status "error" despite the LLM successfully classifying them.
**Fix:** Phase C script catches LOW_CONFIDENCE specifically and saves with `status: "gate_abort"`. The monkey-patch still captures the LLM inference data. `--resume` treats gate_abort like success (no re-processing needed).

### FINDING 8 (NOTE): Schema text in user message is structurally redundant in TOOLS mode

**Status:** NOT fixing for Phase C
**Impact:** In Anthropic TOOLS mode, Instructor sends the Pydantic schema as a tool definition (~500 tokens). Our user message ALSO contains the schema structure (~680 tokens). The structural overlap is redundant. HOWEVER, the user message also contains ~490 tokens of behavioral guidance ("death_date_hijri: null if contemporary", "sectarian_tradition: default sunni", etc.) that is NOT in the Pydantic schema Field descriptions. Removing the schema text would lose this guidance.
**Cost:** ~680 redundant tokens × $5/M × 73 books = $0.25.
**Phase E note:** At 2500 books, redundancy costs ~$8.50. Worth stripping the JSON structure while keeping the IMPORTANT guidance section. This requires sending different user messages to Anthropic (TOOLS mode) vs OpenRouter (JSON mode), which introduces prompt asymmetry risk that must be tested.

### FINDING 9 (NOTE): All-null scholarly_context output tokens

**Status:** NOT fixing for Phase C
**Impact:** For obscure books, the LLM produces an all-null scholarly_context (~103 output tokens per book). At Opus output rate ($25/M): $0.0026/book. For 73 books with ~40% obscure: $0.075 wasted.
**Phase E note:** At 2500 books with ~60% obscure: ~$3.88 wasted. Could be optimized by telling the LLM to skip scholarly_context when context_richness would be "minimal", but this requires a two-pass approach (classify first, then decide whether to fill scholarly_context). Not worth the complexity.

### FINDING 10 (NOTE): Consensus log writes to hardcoded relative path

**Status:** NOT fixing for Phase C
**Impact:** `shared/consensus/src/consensus.py` line 401: `_log_consensus` writes to `Path("library/logs")` — relative to CWD, not the temp library. When Phase C runs from the project root, consensus log entries (73 books × 2 models = 146 entries) go to the project's `library/logs/consensus.jsonl`. Not data corruption — just log noise. The log is append-only and not consumed by any pipeline component.
**Phase D note:** If Phase D uses a shared registry (not isolated temp libraries), this becomes correct behavior. For isolated temp-library runs, could be fixed by passing a log_dir to evaluate() or setting CWD to the temp library root.

### VERIFIED: Monkey-patch mechanism is correct

Traced and empirically verified. Engine.py line 61: `from engines.source.src.metadata_inference import infer_metadata`. Line 301: `inference = await infer_metadata(...)`. When the Phase C script patches `engine_mod.infer_metadata = _capturing_wrapper`, the patched name lives in `engine_mod.__dict__`. When `acquire_source` (defined in engine_mod) calls `infer_metadata(...)`, Python looks up the name in the module's `__dict__` and finds the wrapper. Confirmed with empirical test: patching a module attribute IS visible to functions defined in that module.

### VERIFIED: TOCTOU risk is negligible

Pre-pipeline `detect_format()` + `extract_metadata()` and pipeline `acquire_source()` both read the same .htm files. If the owner modifies files between reads, extraction data diverges from pipeline data. This is safe because: (a) the owner doesn't modify source files during processing, (b) processing is sequential (no concurrent readers), (c) files are on local disk (no network latency window). Documented assumption in the task spec's processing flow.

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
- **Update (Session 2):** System message needs compiler/commentator/riwayah guidance (Finding 6 → Pre-Req 0b). No other prompt changes needed.

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
- [ ] Pre-Req 0a: Fix build_prompt_context (muhaqiq_name_raw, edition_raw, + 5 new fields)
- [ ] Pre-Req 0a test: build_prompt_context on fixture 02 now shows "Muhaqiq/Editor: أحمد محمد عبد الدايم"
- [ ] Pre-Req 0b: Add compiler/commentator/riwayah guidance to SYSTEM_MESSAGE
- [ ] Pre-Req 0b test: 2-book test shows no regressions on genre/author (revert if issues)
- [ ] Pre-Req 1: Add temperature=0 to _call_model in consensus.py
- [ ] Pre-Req 1 test: Verify Instructor passes temperature through (check API logs in dry-run)
- [ ] Pre-Req 2: _full_consensus_result field in MetadataInferenceResult
- [ ] Pre-Req 3: Format B fixture
- [ ] Pre-Req 4: COST_LOG.json

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
| Model deprecated mid-run | Very Low | Partial re-run | 73 books takes ~15 min — unlikely |
| Instructor version incompatibility | Low | Full re-run | Test on 2 books first |
| Rate limiting (Anthropic) | Medium | Delays | Sequential processing with natural pauses |
| Rate limiting (OpenRouter) | Medium | Delays | Sequential processing |
| Command A API down | Low | Fallback to GPT-5.4 | Consensus module handles this automatically |
| Parse failure on complex book | Medium | 1 book error | Error recorded, book marked for re-run |
| Temperature=0 breaks Instructor | Very Low | Revert change | Test in 2-book run; revert if issues |
| Prompt context fix regression | Low | Wrong metadata | Test on all 13 fixtures before full run |
| System message change (0b) regresses existing fields | Low | Revert 0b | 2-book test before full run; keep 0a even if 0b reverts |
| Gate-abort books misclassified as errors | Medium | Wasted re-runs | Script catches LOW_CONFIDENCE specifically → gate_abort status |

---

## Self-Analysis: Bugs Found in My Own Task Spec

### BUG 1 (CRITICAL): Monkey-patch targeted WRONG module

**What I wrote:** Patch `shared.consensus.src.consensus.evaluate`
**Why it's wrong:** Python's `from X import Y` copies the reference into the importing module's namespace. Patching `X.Y` does NOT affect the copy that `metadata_inference.py` already has.
**What it should be:** Patch `engines.source.src.engine.infer_metadata` — this captures the MetadataInferenceResult (which, after Pre-Req 2, contains the full ConsensusResult).
**Impact if not caught:** The Phase C script would silently produce empty llm_responses/ directories for all 73 books. We'd discover this after spending $8-11 and need to re-run.
**Status:** FIXED in task spec.

### BUG 2 (CRITICAL): Pre-pipeline extraction creates lock that blocks pipeline

**What I wrote:** Call `stage_source()` then `extract_metadata()` before `acquire_source()`
**Why it's wrong:** `stage_source()` creates a `.kr_processing` lock file with exclusive mode (`open("x")`). When `acquire_source()` internally calls `stage_source()` on the same path, it finds the lock and FAILS with a contention error.
**What it should be:** Call `detect_format()` then `extract_metadata()` directly — no staging, no lock. Extraction is read-only.
**Impact if not caught:** Every book in Phase C would crash with a lock contention error before making any API calls. $0 wasted but a full debugging session lost.
**Status:** FIXED in task spec.

### BUG 3 (MODERATE): Capture variable not reset between books

**What happens:** The monkey-patch stores `_captured_inference` in a global variable. If book N succeeds but book N+1's `infer_metadata` fails (API error), the global still holds book N's result. The post-pipeline save logic would then write book N's LLM responses into book N+1's directory — silent data corruption.
**Fix:** Explicitly set `_captured_inference = None` before each `acquire_source()` call. Added to the processing flow in the task spec.
**Impact if not caught:** On any book where inference fails, the PREVIOUS book's LLM responses get saved as this book's. During review, we'd see "correct-looking" LLM output for a book that actually failed — the most dangerous kind of silent corruption.
**Status:** FIXED in task spec.

### OBSERVATION 1: Text sample includes title page in ~17% of books

Some Shamela books have their first body page as a title/colophon page (repeating author, publisher). The text_sample correctly skips the metadata CARD but can't distinguish title-page body-divs from content body-divs. In affected books, ~300 of 2000 chars are redundant.
**Decision:** NOT fixing for Phase C. The LLM still gets ~1700 chars of actual body text. Document for Phase E optimization.

### OBSERVATION 2: Isolated temp libraries = scholar registry Case A untested

Each Phase C book gets its own empty registry. The author_agreement_fn's Case A (both models match an existing record) never fires — only Case B (name similarity) is tested. If Case A has a bug, Phase C won't catch it.
**Decision:** Correct for Phase C (independent probes). Phase D must use a shared registry.

### OBSERVATION 3: Actual cost likely ~$0.15/book, not $0.065

Step 0 cost €1.80 for 13 books = ~$0.15/book. My theoretical estimate was $0.065. The 2.3× discrepancy likely comes from Instructor schema overhead tokens and default-temperature verbosity. Updated 73-book estimate: ~$10.95 + retries ≈ ~$12 ≈ ~€11. Still well within ceiling.

---

## Additional Verified Findings (resolved, no action needed)

### VERIFIED: Consensus None-path is safe
When both models succeed but consensus disagrees (canonical_result=None), `metadata_inference.py` calls `select_canonical_result()` which picks the model with higher `author_identification_confidence`. The pipeline continues with that answer and sets `needs_human_gate=True`. No data loss, no crash. Traced through code: lines 440-448 of metadata_inference.py.

### VERIFIED: Multi-volume handling is correct
`_detect_volumes()` in shamela_html.py finds the first numbered .htm file. All metadata extraction and text_sample come from volume 1 only. This is correct — Shamela HTML metadata cards are always in the first file. For 45-volume books (الموسوعة الفقهية الكويتية), the LLM sees volume 1's introduction, which is sufficient for genre/author classification.

### VERIFIED: Temperature pass-through works
Instructor's `from_provider` creates provider-native clients. Anthropic's client accepts `temperature` natively. OpenRouter follows the OpenAI API spec which includes `temperature`. Both will receive `temperature=0` when the pre-requisite is implemented.

### LOW RISK: Instructor mode asymmetry
OpenRouter uses `instructor.Mode.JSON` (raw JSON output). Anthropic uses default mode (tool use). Both produce the same `InferenceOutput` Pydantic model, but the mechanism differs. For optional fields with defaults, Pydantic handles both "field omitted" (JSON mode) and "field present as null" (TOOLS mode). The 2-book test should verify this works in practice.

### VERIFIED: Schema double-send is harmless for Phase C
In TOOLS mode (Anthropic/Opus), Instructor sends the Pydantic schema as a tool definition. Our user message ALSO contains the schema as text (~700 tokens). This is redundant — the model sees the schema twice. Cost: 73 books × 700 tokens × $5/M = $0.26. The "Return ONLY a valid JSON object" instruction is also ignored in TOOLS mode (tool_choice forces tool calling). Neither causes parse failures — just wasted input tokens. NOT fixing for Phase C. For Phase E (2500 books), strip the user-message schema for TOOLS mode calls to save ~$8.75.

### VERIFIED: Retry logic is useful at temperature=0
Our retry uses `simplified_messages` on attempt 1 (strips LIBRARY CONTEXT section) — a different input, not identical. So even at temperature=0, the retry has a chance of producing different output. Additionally, API-level failures (timeout, 429 rate limit) are non-deterministic regardless of temperature. The retry handles both model failures and infrastructure failures correctly.

### RESOLVED: Three questions from previous session

**Q5: --force flag for re-running "success" books.**
YES — added to `PHASE_C_TASK_SPEC.md`. `--force` overrides `--resume` and re-processes all books regardless of existing results. Needed when a pre-req fix (e.g., build_prompt_context) invalidates prior results.

**Q6: Agent team architecture (sub-agents for parallel processing).**
NO — Claude Code processes books sequentially. API rate limiting is the bottleneck, not CPU. The monkey-patch capture mechanism is inherently sequential. 73 books at ~12s each = ~15 minutes.

**Q7: Edition variants — run all 73 or pick one per work.**
RUN ALL 73. The ~16 edition variants test metadata consistency, muhaqiq differentiation, and pipeline stability. The I'lam al-Muwaqqi'in triplet (3 editions) is the single most valuable probe cluster. Cost difference: ~€2.40, negligible against €50 ceiling. Edition-group consistency analysis added to `PHASE_C_SUMMARY.json`.
