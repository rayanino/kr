# Phase C Hardening — Prompts for New Chat Session

Use these prompts in order. Paste Prompt 1 first, let it complete. Then use Prompts 2A-2E one at a time (each is a focused review). Finish with Prompt 3.

---

## PROMPT 1 — Context Intake

```
Start by cloning the repo, then read these files in this exact order:
1. `NEXT.md`
2. `PHASE_C_TASK_SPEC.md`
3. `PHASE_C_PREFLIGHT_AUDIT.md`
4. `PHASE_C_FINAL_SELECTION.md`
5. `engines/source/VALIDATION_PLAN.md`
6. `engines/source/CLAUDE.md`
7. `RESULT_PRESERVATION.md`
8. `scripts/phase_c_books.txt`
9. `tests/fixtures/phase_c_fixture_mappings.json`

After reading all files, give me a structured status report covering:
- What Step 3 (Phase C) is and why it matters
- What has been prepared so far (documents, pre-requisites, book selection, audit findings)
- The 2 critical bugs that were caught in self-analysis and how they were fixed
- The 5 pre-requisites Claude Code must implement before any API call
- Any concerns, gaps, or inconsistencies you notice between the documents
- What remains to be hardened before we hand this to Claude Code

Do NOT summarize superficially. Read each document carefully and identify anything that seems incomplete, contradictory, or risky. The goal of THIS session is to stress-test the preparation — find every remaining weakness before real money is spent.
```

---

## PROMPT 2A — LLM Prompt & Model Configuration Audit

This is the highest-stakes review. Everything here directly determines whether API credits produce useful data or waste.

```
Conduct a deep audit of the LLM inference chain — every component between "extracted metadata" and "structured JSON output." Read these files:

1. `engines/source/prompts/inference_v1.py` — the FULL prompt template (system + user messages)
2. `engines/source/src/metadata_inference.py` — the function that builds prompt context and calls consensus
3. `shared/consensus/src/consensus.py` — model dispatch, retry logic, agreement evaluation
4. `engines/source/src/inference_models.py` — the Pydantic schema the LLM must produce
5. `engines/source/src/consensus.py` (engine-specific) — author agreement function
6. `library/config/genre_synonyms.json` — enum synonym mapping

For each component, answer:

<audit_questions>
PROMPT TEMPLATE:
- Does every instruction in the system message actually help classification quality, or is any of it noise that wastes output tokens?
- Is the JSON schema in the user message the optimal way to communicate the expected output? Could Instructor's tool-mode schema injection replace it (saving ~700 input tokens per call)?
- Are there ambiguities in the instructions that would cause models to disagree for the WRONG reasons (prompt ambiguity vs genuine domain ambiguity)?
- The prompt says "Return ONLY a valid JSON object." But Instructor handles JSON extraction — does this instruction conflict with Instructor's mode (tool vs JSON)?

MODEL CONFIGURATION:
- Command A via OpenRouter uses `mode=instructor.Mode.JSON`. Opus 4.6 via Anthropic uses the default mode (tool use). Is this asymmetry intentional? Could it cause systematic differences in output structure between the two models?
- The `max_tokens=4000` — is this verified sufficient for the worst-case InferenceOutput? What happens if output is truncated?
- `temperature=0` is specified as a pre-requisite. Verify: does Instructor pass temperature through for both Anthropic tool mode AND OpenRouter JSON mode?

RETRY & FAILURE:
- Our retry (`MAX_RETRIES_PER_MODEL = 2`) catches ALL exceptions. Instructor's default `max_retries=0`. What happens when Instructor raises a validation error vs an API error? Are both handled correctly by our retry?
- The fallback model (GPT-5.4 via OpenRouter) — has it ever been tested with the InferenceOutput schema? What evidence do we have it will parse correctly?

CONSENSUS:
- The author_agreement_fn checks name_similarity ≥ 0.90 AND death_date ±10 years. Is 0.90 too strict for Arabic names with varying nasab lengths? Too lenient?
- When consensus disagrees, canonical_result is None and needs_human_gate is True. But the FULL pipeline continues and produces a SourceMetadata anyway — what author data goes into it when canonical_result is None?
</audit_questions>

For every issue you find: classify as BLOCKER (must fix before Phase C), WARNING (should fix, document if not), or NOTE (awareness only). Show your reasoning.
```

---

## PROMPT 2B — Result-Saving Architecture Audit

This ensures no API credit is wasted — every call's output is fully captured and reusable.

```
Audit the result-saving architecture specified in PHASE_C_TASK_SPEC.md against RESULT_PRESERVATION.md. Read both documents carefully, then read the processing flow in the task spec.

For each of the 7 output files per book (extraction.json, prompt_sent.json, llm_responses/*.json, consensus.json, result.json, ground_truth_comparison.json), verify:

<verification_checklist>
1. COMPLETENESS: Does the specified format capture EVERYTHING that RESULT_PRESERVATION.md requires? Cross-reference every bullet point in Layer 1 (Raw Artifacts) against the output structure.

2. ORDERING: The task spec says extraction.json and prompt_sent.json are saved BEFORE the API call. Trace the processing flow — is there any code path where the API call could fire before these files are written? What if detect_format() or extract_metadata() throws an exception — do we lose the partial extraction?

3. REUSABILITY: Could a future agent reconstruct the full LLM interaction from the saved files WITHOUT re-calling the API? Specifically:
   - Can you reconstruct the exact prompt from prompt_sent.json?
   - Can you reconstruct the exact model responses from llm_responses/*.json?
   - Can you re-run consensus evaluation from the saved per-model outputs?
   - Can you re-compute trust scores from result.json?

4. COST TRACKING: The spec says COST_LOG.json is updated after each book. But the actual per-book cost isn't available from acquire_source — it's an estimate. How accurate is the estimate? What if the estimate is 3x off (as Step 0 actual vs theoretical showed)?

5. MANIFEST: PHASE_C_MANIFEST.json tracks `needs_rerun` per book. What triggers `needs_rerun = true`? Is the trigger automatic or manual? What happens if a bug fix between Phase C and Phase D affects a field that wasn't saved in the manifest?

6. FAILURE RECOVERY: If the script crashes mid-book (e.g., OOM on a 45-volume encyclopedia), what is the state? Are partial files left behind? Does `--resume` correctly handle a book with extraction.json but no result.json?
</verification_checklist>

For each finding: classify as BLOCKER / WARNING / NOTE and explain the fix.
```

---

## PROMPT 2C — Script Architecture & Processing Flow Audit

```
Read PHASE_C_TASK_SPEC.md focusing on the "Script Specification" and "Processing Flow" sections. Then read the existing scripts for patterns:
- `scripts/run_session6_integration.py` — the Step 0 script (existing, working)
- `scripts/run_phase_a.py` — the Step 2 script (existing, working)

Audit the Phase C script design:

<audit_areas>
TEMP LIBRARY ISOLATION:
- The spec says each book gets its own temp library (same as Step 0). This means EMPTY scholar registries for every book. But: the pre-requisites include a _full_consensus_result capture via monkey-patching engine_mod.infer_metadata. Does the monkey-patch persist correctly across 73 sequential book runs in the same Python process? Or does it need to be re-applied per book?

MONKEY-PATCH CORRECTNESS:
- The spec says to patch `engine_mod.infer_metadata` (Approach A). Trace this through: engine.py imports infer_metadata at the TOP. So `engine_mod.infer_metadata` is a module-level reference. Patching it should work — but verify: does acquire_source call `infer_metadata(...)` or `self.infer_metadata(...)` or something else? Is there any indirection that would bypass the patch?

MULTI-VOLUME HANDLING:
- Books like الموسوعة الفقهية الكويتية (45 volumes, 87MB) and فتح الباري (14 volumes, 66MB) are LARGE. Does acquire_source handle multi-volume Shamela dirs? Does it read ALL volumes or just the first? What is the text_sample extraction for a multi-volume work — first 2000 chars of volume 1 only?

CONCURRENT CONSIDERATION:
- The spec says sequential processing. But Claude Code with Opus 4.6 has agent capabilities. Could we process books in parallel using sub-agents? What would change in the script design? What are the risks (rate limiting, cost tracking, result file collisions)?

EDGE CASE: VERY TINY BOOKS:
- الكلام على حديث الإستلقاء is 4KB. الورقة النحوية is 8KB. نصيحة لطالب الحق is 7KB. After metadata card extraction, the text_sample might be <200 characters. Is that enough for meaningful LLM inference? Should the script log a warning when text_sample is very short?

EDGE CASE: ALREADY-PROCESSED BOOKS:
- --resume skips books with result.json status "success". But what if the script ran once with a bug (e.g., the prompt context bug unfixed), produced "success" results with bad data, and the user wants to re-run? Should there be a --force flag?
</audit_areas>

For each finding: BLOCKER / WARNING / NOTE with reasoning and fix.
```

---

## PROMPT 2D — Book Selection Validation

```
Read PHASE_C_FINAL_SELECTION.md and scripts/phase_c_books.txt. Then read:
- `engines/source/contracts.py` — Genre enum, StructuralFormat enum, AuthorityLevel enum
- `tests/fixtures/GROUND_TRUTH.json` — existing ground truth
- `tests/fixtures/phase_c_fixture_mappings.json` — fixture-to-collection mapping

Validate the book selection:

<validation_questions>
1. GENRE COVERAGE: The selection doc claims all 18 Genre enum values are covered. Verify this by mapping each of the 73 books to its expected genre. Are there any genres with only 1 probe? (Single-probe genres can't distinguish "LLM got it wrong" from "LLM disagrees with my expectation.")

2. EDITION VARIANTS: The owner provided multiple editions of several works (البداية والنهاية ×2, إعلام الموقعين ×3, تفسير الطبري ×2, etc.). These are valuable but double the API cost. For which multi-edition works should we run ALL editions vs just ONE? What's the testing value of running both editions of the same work?

3. FIXTURE MAPPING: 12 of 73 books map to ground truth fixtures. But the books.txt names (from the owner's collection) may differ slightly from the fixture display_titles. The fixture_mappings.json was generated by substring matching. Verify: are all 12 mappings correct? Could any mapping be wrong (e.g., a different edition of the same title matching the wrong fixture)?

4. GROUP A HANDLING: The 14 Group A books are the fixture equivalents from the owner's COLLECTION (not the fixture directory). The task spec says fixtures are "handled separately." But the books.txt includes all Group A books. Clarify: are we running Group A through the collection path (acquire_source on the owner's .htm files) or the fixture path (acquire_source on test/fixtures/)? The former tests the real collection; the latter tests known-good data. We should do the former.

5. MISSING PROBES: Given the 73 books, are there any pipeline code paths that NO book exercises? For example: does any book test the `responds_to` or `cites` relation_types? Does any book test `attribution_status: "unknown"`? Does any book test `level: null` for a non-scholarly work? Does any book test `is_multi_layer: true` with `layers` including a `tahqiq_note` layer type?
</validation_questions>
```

---

## PROMPT 2E — Agent Team Architecture for Claude Code

This is a new design consideration. The user suggested Claude Code could use agent teams — each agent processes one book.

```
Research and design an agent team architecture for Phase C execution in Claude Code. Context: Claude Code runs with Opus 4.6 and ~1M context window. It can spawn sub-agents for parallel work.

<design_requirements>
GOAL: Process 73 books through the full source engine pipeline, capturing all diagnostic artifacts per PHASE_C_TASK_SPEC.md.

CONSTRAINTS:
- Each book requires real API calls (Opus 4.6 + Command A via OpenRouter)
- Sequential processing of 73 books takes ~60-90 minutes
- Rate limits: Anthropic has per-minute and per-day token limits; OpenRouter has per-minute limits
- Each book's result must be independently valid (no shared state between books)
- Budget ceiling: €50 (expect ~€12)
- Script runs on the OWNER'S Windows machine, not in Claude Code's container

KEY QUESTIONS:
1. Should Claude Code write a script that the owner runs (current plan), or should Claude Code RUN the script itself using the owner's API keys?
2. If the owner runs it: should the script process books sequentially or use Python asyncio/multiprocessing for parallelism?
3. If parallel: how many concurrent books? Rate limiting is the binding constraint. With 2 models per book, 2-3 concurrent books might be safe. More risks 429 errors.
4. Agent teams in Claude Code: could Claude Code spawn sub-agents where each agent REVIEWS a completed book result (after the pipeline run)? This would parallelize the review phase (currently planned as 5 books/session in Claude Chat).
5. Self-evaluation: could each book's pipeline run include an automatic LLM-based evaluation step (using a DIFFERENT model than the consensus pair) that checks whether the output looks reasonable? This catches obvious errors before human review.
</design_requirements>

Research rate limits for Anthropic API and OpenRouter, then propose an architecture. Distinguish between what Claude Code builds vs what the owner runs vs what Claude Chat reviews. Be specific about parallelism levels, rate limit safety margins, and failure handling.
```

---

## PROMPT 3 — Integration Review & Final Hardening

Use this AFTER all 2A-2E reviews are complete. It checks that everything fits together.

```
You've now reviewed every component of the Phase C preparation individually. Do a final integration check.

Read the following files one more time, looking specifically for CROSS-DOCUMENT INCONSISTENCIES:
1. `NEXT.md`
2. `PHASE_C_TASK_SPEC.md`
3. `PHASE_C_PREFLIGHT_AUDIT.md`
4. `PHASE_C_FINAL_SELECTION.md`
5. `engines/source/VALIDATION_PLAN.md`
6. `RESULT_PRESERVATION.md`
7. `scripts/phase_c_books.txt`

<integration_checks>
1. NUMBERS: Do all documents agree on: number of books (73), number of pre-requisites (5, numbered 0-4), budget estimate (~€10-12), number of fixture matches (12)?

2. FIELD NAMES: The pre-requisite 0 fix changes build_prompt_context to use muhaqiq_name_raw and edition_raw. Does the task spec's prompt_sent.json format reference these same field names? Does the extraction.json format show the correct field names?

3. FLOW CONSISTENCY: The task spec's processing flow says "detect_format() + extract_metadata() BEFORE acquire_source()". But extract_metadata() requires a source_path. The processing flow says "Copy book to temp staging" → then extract. Does the copied path match what acquire_source expects? Could there be a path mismatch between extraction and pipeline?

4. GROUND TRUTH: The fixture_mappings.json maps 12 collection books to fixture keys. The task spec's "Ground Truth Comparison" section describes the comparison format. Does the comparison function in the task spec handle the case where a collection book's extraction differs slightly from the fixture extraction (different .htm file structure, etc.)?

5. PRE-REQUISITE DEPENDENCIES: Pre-req 2 adds _full_consensus_result to MetadataInferenceResult. The processing flow's monkey-patch reads this field. But: does the monkey-patch approach (wrapping infer_metadata) actually give access to this field? The wrapper captures the RETURN VALUE of infer_metadata, which IS the MetadataInferenceResult. So yes — confirm this chain is unbroken.

6. COST: The preflight audit says Step 0 actual cost was $0.15/book. The task spec says budget ceiling €50. 73 × $0.15 = $10.95 ≈ €10. But: with temperature=0, output tokens should decrease. With the prompt context fix, input tokens increase slightly (more fields sent). Net effect on cost?

7. WHAT'S MISSING: After all reviews, is there anything that should be in the Phase C preparation but isn't? Any document that should exist but doesn't? Any test that should be specified but isn't?
</integration_checks>

Compile all findings from this review AND from Prompts 2A-2E into a single prioritized action list:
- BLOCKERS (must fix before Claude Code)
- WARNINGS (should fix, with workarounds if not)
- NOTES (awareness, fix later)

Then write the final updated PHASE_C_TASK_SPEC.md incorporating all fixes. Commit and push.
```

---

## Usage Notes

- **Prompt 1** establishes context. Let it complete fully before continuing.
- **Prompts 2A-2E** are independent reviews. You can do them in any order, but 2A (LLM audit) is highest priority since it directly protects money.
- **Prompt 2E** (agent teams) is exploratory — it might lead to architectural changes in the task spec.
- **Prompt 3** is the synthesis step. Do it LAST, after all individual reviews have surfaced their findings.
- Each prompt should take 10-20 minutes of deep analysis. Don't rush the new Claude — let it use extended thinking fully.
