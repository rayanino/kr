# Phase C Hardening — Prompts for New Chat Session

## How to use these prompts

4 prompts, used in order. Each is self-contained — the new Claude reads the needed files within each prompt, not everything upfront.

**Time estimate:** ~60-90 minutes total across all 4 prompts.

**If a prompt finds BLOCKERS:** Fix them before proceeding. Don't push through broken foundations.

---

## PROMPT 1 — Context Intake & Sanity Check

Goal: Establish understanding. Catch obvious inconsistencies before deep-diving.

```
Start by cloning the repo, then read these 3 documents carefully:
1. `NEXT.md` — current state and reasoning behind every decision
2. `PHASE_C_TASK_SPEC.md` — the complete implementation spec (~700 lines)
3. `PHASE_C_PREFLIGHT_AUDIT.md` — what was already audited and what was found

Then do these quick sanity checks (5 minutes, not deep analysis):

A) COUNT CHECK: How many books does NEXT.md say? How many does the task spec say? How many lines are in scripts/phase_c_books.txt (excluding comments and blanks)? Do they all agree?

B) PRE-REQ COUNT: NEXT.md lists 5 pre-requisites (0-4). The task spec has numbered sections for each. Does the numbering match? Does the Definition of Done checklist reference all 5?

C) FILE EXISTENCE: Run `ls` on every file the task spec references as input (books.txt, fixture_mappings.json, COST_LOG.json path, etc.). Do they all exist? Is COST_LOG.json supposed to be CREATED by Claude Code (pre-req 4) or should it already exist?

D) FIXTURE MAPPING: Read tests/fixtures/phase_c_fixture_mappings.json. It maps 12 collection books to fixture keys. Open tests/fixtures/GROUND_TRUTH.json and verify all 12 fixture keys exist in ground truth. Are there fixture keys in ground truth that DON'T have a collection book mapping (i.e., we're missing coverage)?

After the sanity checks, give me:
1. A 3-sentence summary of where Phase C preparation stands
2. Any inconsistencies found in the sanity checks
3. Your initial concerns about the preparation (things that feel risky or incomplete, based on your fresh reading)
```

---

## PROMPT 2 — End-to-End Trace (Script Flow + Result Saving + Failure Handling)

Goal: Trace one book through the ENTIRE processing flow. At each step: what happens on success? On failure? Is the result properly saved? This covers script architecture, result saving, and failure handling as coupled concerns.

```
Read PHASE_C_TASK_SPEC.md's "Processing Flow" section carefully. Then read the source code it references:
- `engines/source/src/engine.py` — acquire_source (the 13-step pipeline)
- `engines/source/src/metadata_inference.py` — infer_metadata + build_prompt_context
- `engines/source/src/format_detection.py` — detect_format
- `shared/consensus/src/consensus.py` — evaluate + _call_model
- `scripts/run_session6_integration.py` — the existing Step 0 script (working reference)

Now trace a SINGLE BOOK through the Phase C processing flow. Use "فتح الباري بشرح البخاري - ط السلفية" (14 volumes, 66MB) as the test case — it's the largest and most complex.

At each step, answer these questions:

<step_trace>
STEP: "Copy book to temp staging"
- فتح الباري is a DIRECTORY with 14 .htm files. How is it copied? Does shutil.copytree work? What's the temp staging path structure?

STEP: "detect_format() + extract_metadata()"
- detect_format receives a directory path. Does _detect_directory_format handle 14 .htm files correctly?
- extract_metadata for shamela_html — does it read ALL 14 volumes or just the first? What's the text_sample for a multi-volume work?
- If detect_format throws, is extraction.json still saved? (The task spec says save BEFORE API call, but format detection is before extraction.)

STEP: "Build and save prompt_sent.json"
- build_prompt_context currently has the field-name bugs (pre-req 0 not yet applied). After the fix, what fields will be present for فتح الباري? It has: title, author with death date, muhaqiq, publisher, edition, page count. Verify each field name matches what the FIXED build_prompt_context will look for.

STEP: "acquire_source(staging_path, config)"
- The task spec monkey-patches engine_mod.infer_metadata to capture MetadataInferenceResult. Trace the import chain: How does engine.py import infer_metadata? Is the patch point correct?
- فتح الباري is 14 volumes — does staging handle this? Does hashing handle this? Does freezing copy all 14 files?

STEP: "Save per-model LLM responses"
- The captured MetadataInferenceResult has _full_consensus_result (a ConsensusResult dataclass with model_responses: list[ModelResponse]). Each ModelResponse has .parsed (InferenceOutput) and .raw_response (dict). Verify: calling .parsed.model_dump() produces the JSON we want in llm_responses/opus_4_6.json.

STEP: "Save result.json"
- acquire_source returns SourceMetadata. Calling .model_dump(mode="json") should produce serializable JSON. Are there field types that don't serialize cleanly (Path, datetime, enums)?

STEP: "What if the API call fails mid-book?"
- Both models fail → ConsensusResult.needs_human_gate = True, canonical_result = None. Does acquire_source still produce SourceMetadata or raise an exception? Trace the code path in engine.py.
- If acquire_source raises SourceEngineError, is extraction.json already saved? Is prompt_sent.json already saved?
</step_trace>

Also check:
- Does the monkey-patch persist correctly across 73 sequential book runs in one Python process?
- --resume: If script crashes with extraction.json saved but no result.json, does resume correctly re-process that book?
- Should there be a --force flag to re-run books even if result.json exists with status "success"?

For each issue: BLOCKER / WARNING / NOTE with specific fix.
```

---

## PROMPT 3 — LLM Call Quality & Cost Audit

Goal: Verify every API call produces maximum useful data for its cost. The previous audit already verified enum alignment, prompt template clarity, and consensus correctness. Focus on what WASN'T checked.

```
Read these files:
- `engines/source/prompts/inference_v1.py` — the full prompt template
- `engines/source/src/inference_models.py` — the InferenceOutput Pydantic schema
- `shared/consensus/src/consensus.py` — model dispatch and Instructor usage
- `engines/source/src/metadata_inference.py` — build_prompt_context + infer_metadata
- `PHASE_C_PREFLIGHT_AUDIT.md` — what was already verified (DON'T re-audit those items)

The preflight audit already verified: all enum values match, prompt instructions are clear, consensus mechanism is correct, cost model is reasonable. Focus on these NEW areas:

<new_audit_areas>
1. INSTRUCTOR MODE ASYMMETRY:
Command A via OpenRouter uses `mode=instructor.Mode.JSON`.
Opus 4.6 via Anthropic uses the DEFAULT mode (tool use).
These are fundamentally different prompting strategies. JSON mode injects "respond in JSON" into the prompt. Tool mode converts the schema into a tool definition.
- Could this cause systematic structural differences between the two models' outputs?
- Research what Instructor actually does in each mode — check Instructor docs or source code.
- Is this asymmetry intentional and tested, or an accident?

2. WHAT HAPPENS WHEN CONSENSUS CANONICAL IS NONE:
When both models disagree on author, canonical_result = None. But acquire_source continues. What author data goes into SourceMetadata? Trace from metadata_inference.py where canonical_result is None through to engine.py's Step 9 (Assemble SourceMetadata). What does ScholarReference contain?

3. SCHOLARLY_CONTEXT COST-EFFICIENCY:
The scholarly_context section has 10 subfields. For obscure hadith juz' texts (4KB), these will be mostly null/empty. Is the LLM wasting output tokens generating empty fields? Consider: should the prompt tell the LLM to set scholarly_context to null when context_richness would be "minimal"? This could save ~200 output tokens × ~30 obscure books = ~$0.15.

4. ACTUAL TOKEN TRACKING:
Both Anthropic and OpenRouter return token usage data (prompt_tokens, completion_tokens) in API responses. Does the Phase C script capture and log these per-book? This is the ONLY way to verify cost estimates before the full run. If not specified in the task spec, it should be.

5. TEMPERATURE=0 VERIFICATION:
Pre-req 1 adds temperature=0 to _call_model. Does Instructor pass temperature through for BOTH modes (tool mode for Anthropic, JSON mode for OpenRouter)? Check Instructor docs. If one mode doesn't support temperature, what happens — error or silent ignore?
</new_audit_areas>

For each finding: BLOCKER / WARNING / NOTE.
```

---

## PROMPT 4 — Integration Review, Action List, and Commit

Goal: Synthesize all findings. Fix everything. Commit clean.

```
Review your findings from Prompts 1-3. Then do these final integration checks:

<final_checks>
1. RESULT_PRESERVATION COMPLIANCE: Read RESULT_PRESERVATION.md Layer 1 (Raw Artifacts). Cross-reference every bullet against the Phase C output structure. Is anything in Layer 1 NOT captured?

2. 2-BOOK TEST SPECIFICS: The task spec's "Testing Before Full Run" section — does it specify WHICH 2 books to test? It should be:
   - Book 1: A small fixture-matching book (e.g., أحكام الاضطباع والرمل في الطواف, 265KB → fixture 03_fiqh)
   - Book 2: A small new book WITHOUT ground truth (e.g., الفقه الأكبر, 91KB → disputed attribution)
   NOT a large multi-volume book for the initial test.

3. PARALLELISM: The owner mentioned Claude Code agent teams. The script runs on the OWNER'S Windows machine. Agent teams in Claude Code would only help with script writing (not a bottleneck). Should the Python script use asyncio for parallel book processing? Answer: probably not for 73 books — sequential is simple and debuggable. Note this as a Phase D/E optimization.

4. COMPILE THE MASTER ACTION LIST from all prompts:
   - BLOCKERS: must fix before Claude Code handoff
   - WARNINGS: should fix, with specific changes proposed
   - NOTES: document for future
   For each item: which file to change, what to change, why.

5. Apply all BLOCKER and WARNING fixes to the relevant documents. Commit and push.
</final_checks>

After committing, give me:
- Total BLOCKERS found and fixed across all prompts
- Total WARNINGS found and fixed
- Total NOTES documented
- Confidence level (1-10) that Phase C preparation is ready for Claude Code
- Any remaining concerns
```

---

## Design Notes

**Why 4 prompts, not 7:** Each prompt covers coupled concerns. The end-to-end trace (Prompt 2) exercises script flow, result saving, AND failure handling together — separating them would miss interactions. The LLM audit (Prompt 3) skips what the preflight already verified.

**Why no separate book selection prompt:** The 73 books are selected and downloaded. Re-evaluating each book's test value has marginal benefit for the cost of a full prompt.

**Why no separate agent team prompt:** The Phase C script runs on the owner's machine, not in Claude Code. Sequential processing of 73 books takes ~60-90 minutes — acceptable. Agent teams and parallelism are Phase D/E concerns.

**If early prompts find major issues:** Stop. Fix. Re-run the affected prompt. Don't build on broken foundations.
