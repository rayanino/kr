# Phase C Task Specification — Targeted LLM Probes

**For:** Claude Code implementation session
**Phase:** Validation Step 3 (first real LLM costs)
**Budget:** €50 ceiling (owner lifted the original €10 cap; expect ~€8–12 actual spend for 73 books at ~$0.15/book)
**Governing docs:** `VALIDATION_PLAN.md`, `RESULT_PRESERVATION.md`, `CLAUDE_CODE_MEMORY_PRINCIPLES.md`

---

## Task Summary

Write `scripts/run_phase_c.py` — a script that runs the FULL source engine pipeline (Steps 1–13) on 73 owner-selected books from the Shamela collection, captures every intermediate artifact per RESULT_PRESERVATION.md, and produces structured results ready for owner review.

The owner provided 73 unique books (after deduplication of cross-group copies) organized by test group A-H, including extras like multiple editions of key works. The collection is ~646 MB across 415 .htm files. books.txt is at `scripts/phase_c_books.txt`. Fixture-to-ground-truth mappings are at `tests/fixtures/phase_c_fixture_mappings.json`.

---

## Pre-Requisites (Claude Code does these first)

### 0. CRITICAL: Fix build_prompt_context field-name mismatches + missing fields

**File:** `engines/source/src/metadata_inference.py`, function `build_prompt_context`

**Problem:** The function that builds the `=== EXTRACTED METADATA ===` section the LLM sees has field-name mismatches. The Shamela extractor saves `muhaqiq_name_raw` and `edition_raw`, but `build_prompt_context` looks for `muhaqiq_name`/`muhaqiq` and `edition` — which don't exist. Result: **54% of books have muhaqiq data the LLM never sees, 74% have edition data the LLM never sees.** Additionally, several useful extracted fields (compiler, commentator, riwayah, edition year) are never passed to the LLM.

**Fix:** Update `build_prompt_context` to check the correct field names AND add missing useful fields:

```python
# FIX 1: Muhaqiq — check the actual field name from Shamela extraction
muhaqiq = extracted.get("muhaqiq_name_raw") or extracted.get("muhaqiq_name") or extracted.get("muhaqiq", "")
if muhaqiq:
    lines.append(f"Muhaqiq/Editor: {muhaqiq}")

# FIX 2: Edition — check the actual field name
edition = extracted.get("edition_raw") or extracted.get("edition", "")
if edition:
    lines.append(f"Edition: {edition}")

# NEW FIELDS: Add when present
compiler = extracted.get("compiler_name_raw", "")
if compiler:
    lines.append(f"Compiler: {compiler}")

commentator = extracted.get("commentator_name_raw", "")
if commentator:
    lines.append(f"Commentator: {commentator}")

riwayah = extracted.get("riwayah", "")
if riwayah:
    lines.append(f"Riwayah/Transmission: {riwayah}")

edition_year_h = extracted.get("edition_year_hijri")
edition_year_m = extracted.get("edition_year_miladi")
if edition_year_h:
    lines.append(f"Edition year (Hijri): {edition_year_h}")
if edition_year_m:
    lines.append(f"Edition year (Miladi): {edition_year_m}")
```

**Test after fix:** Run a quick sanity check: call `build_prompt_context` on a fixture extraction dict that has `muhaqiq_name_raw` (e.g., fixture 02_nahw_muhaqiq) and verify the output includes "Muhaqiq/Editor:". All existing tests must still pass.

**Why this matters:** Without this fix, every API call on the 54% of books with muhaqiq data produces results where the LLM couldn't factor in tahqiq quality. The scholarly_context.muhaqiq_reputation field will be either null or hallucinated (from text_sample alone). This wastes money because we'd have to re-run these books after fixing the prompt context.

#### 0b. Update system message to guide LLM on new metadata fields

**File:** `engines/source/prompts/inference_v1.py`, `SYSTEM_MESSAGE`

**Problem:** Pre-Req 0a adds `Compiler:`, `Commentator:`, and `Riwayah/Transmission:` to the metadata the LLM sees, but the system message says nothing about these fields. Without guidance:
- The LLM may confuse a compiler (جامع/مرتب) with the author — critical for مجموع الفتاوى where Ibn Taymiyyah is the author but Ibn Qasim is the compiler.
- The LLM may not recognize that a `Commentator:` field in the metadata card is strong evidence of multi-layer text.
- The LLM may ignore the `Riwayah/Transmission:` field entirely, losing important hadith sub-identification.

**Fix:** Add the following to `SYSTEM_MESSAGE`, after the "Tahqiq methodology" bullet in the expertise list:

```python
- Compiler vs. author distinction: a compiler (جامع/مرتب) organized existing material but is not the original author. When both Author and Compiler are present in the metadata, author_identification should identify the ORIGINAL author, not the compiler. The compiler's role may affect authority_level (modern_compilation).
- Commentator identification: a commentator (شارح/معلق) listed in the metadata card is strong evidence of multi-layer text — the commentary is a distinct textual layer above the base work.
- Riwayah/transmission chains: for hadith works, a riwayah (رواية) identifies the specific transmission path. Different riwayahs of the same base collection are distinct works with different genre_chains.
```

**Test:** Run the 2-book test. If genre/author results for the test books change in unexpected ways compared to Step 0 results, REVERT the system message change and keep only the `build_prompt_context` fix (Pre-Req 0a). The behavioral guidance is valuable but not worth introducing regressions. Document what happened.

### 1. Add temperature=0 to consensus model calls

**File:** `shared/consensus/src/consensus.py`, function `_call_model`, line ~134

**Problem:** No temperature parameter is passed. Both models use their defaults (Anthropic: 1.0, Cohere: varies). For deterministic structured JSON classification, temperature=0 is optimal — it reduces output token count, prevents hallucination in scholarly_context, and makes results reproducible.

**Fix:** Add `temperature=0` to the create() call:
```python
result = await asyncio.wait_for(
    client.create(
        messages=msgs,
        response_model=response_model,
        max_tokens=4000,
        temperature=0,   # ADD: deterministic output for structured classification
    ),
    timeout=MODEL_TIMEOUT,
)
```

**Test:** Run the 2-book test and verify temperature=0 is passed through by checking API response headers or logs. If Instructor doesn't pass temperature for a specific mode, fall back to not setting it and document the issue.

### 2. Small engine change: expose full ConsensusResult

**File:** `engines/source/src/metadata_inference.py`

**Problem:** `infer_metadata()` calls `consensus.evaluate()` which returns a `ConsensusResult` containing full `ModelResponse` objects (with the complete parsed `InferenceOutput` and `raw_response` dict for each model). But `infer_metadata` only saves summaries to `raw_model_responses` (model_id, parse_success, error). The full per-model outputs are discarded.

**Fix (2 lines):**

1. Add field to `MetadataInferenceResult`:
```python
# After line 116 (raw_model_responses field):
_full_consensus_result: Optional[Any] = None  # ConsensusResult when diagnostic capture needed
```

2. Save it in `infer_metadata` after the evaluate() call:
```python
# After line ~428 (where raw_model_responses is populated):
result._full_consensus_result = consensus_result
```

**Test:** Existing tests must still pass. The new field defaults to None and is never read by engine.py — it's purely diagnostic.

### 3. Create Format B test fixture

**Problem:** Phase A Bug 2 (colon-in-label value embedding for 64 books) was fixed in `shamela_html.py` but has no unit test fixture.

**Fix:** Create a synthetic fixture that triggers the Format B code path:
- Create `tests/fixtures/shamela_real/13_format_b/book.htm` with a Format B metadata card (value inside the `<span>` tag, not after it)
- The fixture should have at least: `الكتاب`, `المؤلف` with death date, one field using Format B layout
- Add ground truth entry in `GROUND_TRUTH.json` for `13_format_b`
- Add unit test in the appropriate test file

### 4. Create COST_LOG.json

```json
{
  "phases": {
    "0": {"books": 13, "cost_eur": 1.80, "status": "complete"},
    "A": {"books": 2519, "cost_eur": 0.00, "status": "complete"},
    "C": {"books": 0, "cost_eur": 0.00, "status": "pending"},
    "D": {"books": 0, "cost_eur": 0.00, "status": "pending"},
    "E": {"books": 0, "cost_eur": 0.00, "status": "pending"}
  },
  "total_eur": 1.80,
  "budget_ceiling_eur": 100.00
}
```

Save to: `tests/results/source_engine/COST_LOG.json`

---

## Script Specification: `scripts/run_phase_c.py`

### Usage

```bash
# Full run
python scripts/run_phase_c.py COLLECTION_DIR --books books.txt

# Single book (for testing)
python scripts/run_phase_c.py COLLECTION_DIR --book "أحكام الاضطباع والرمل في الطواف"

# Resume after interruption (skip already-processed books with status "success")
python scripts/run_phase_c.py COLLECTION_DIR --books books.txt --resume

# Force re-run of specific book (even if it already has status "success")
python scripts/run_phase_c.py COLLECTION_DIR --book "أحكام الاضطباع والرمل في الطواف" --force

# Force re-run of ALL books (ignores existing results entirely)
python scripts/run_phase_c.py COLLECTION_DIR --books books.txt --force

# Dry run (validate setup, no API calls)
python scripts/run_phase_c.py COLLECTION_DIR --books books.txt --dry-run
```

**Parameters:**
- `COLLECTION_DIR`: Path to the Shamela export directory containing all .htm book folders
- `--books FILE`: Text file listing book directory names (one per line, UTF-8)
- `--book NAME`: Single book directory name (for testing)
- `--resume`: Skip books that already have a `result.json` with `status: "success"` in the output directory. Books with `status: "error"` are re-processed (the error may have been transient). Has no effect when combined with `--force`.
- `--force`: Re-run books even if they already have `status: "success"` results. Existing result directories are overwritten. Use after fixing a pre-requisite bug that invalidates prior results. Overrides `--resume`.
- `--dry-run`: Validate environment, check all books exist, verify API keys work with a minimal test call, estimate cost, then exit. The API test call should be a trivial inference (not a real book) to confirm both Anthropic and OpenRouter keys are valid and models respond.
- `--output-dir DIR`: Override output directory (default: `tests/results/source_engine/phase_c/`)
- `--budget-eur FLOAT`: Maximum cost ceiling in EUR (default: 50.0)

### Environment Requirements

```bash
export ANTHROPIC_API_KEY="..."
export OPENROUTER_API_KEY="..."
```

Script MUST check both keys exist before starting. Exit with clear error if missing.

### Early Abort on Model Failure

If the FIRST book fails with an API error (not a parse error — an actual connectivity/auth failure), abort immediately with a clear error message. Do not proceed to book 2. This prevents burning extraction time on 72 books when the API keys are invalid or models are down.

If 3 consecutive books fail with API errors (after the first book succeeded), pause and ask for user confirmation before continuing. This catches intermittent rate-limiting without losing all progress.

### Input Format: books.txt

```
أحكام الاضطباع والرمل في الطواف
همع الهوامع في شرح جمع الجوامع
مذكرات مالك بن نبي - العفن
...
```

Each line is a directory name within COLLECTION_DIR. Lines starting with `#` are comments. Empty lines are ignored. The script MUST verify each directory exists before starting any processing.

### Book Resolution

The script locates books by matching directory names in COLLECTION_DIR. Shamela exports are structured as:
```
COLLECTION_DIR/
  أحكام الاضطباع والرمل في الطواف/
    book.htm
  همع الهوامع في شرح جمع الجوامع/
    001.htm
    002.htm
    003.htm
  ...
```

Each book is either a single `book.htm` or numbered volume files (`001.htm`, `002.htm`, ...) optionally with a `المقدمة.htm`.

If a book directory contains a single .htm file, it may or may not be named `book.htm`. Handle any .htm filename.

### Processing Flow (per book)

For each book, the script captures all intermediate artifacts before, during, and after the pipeline run:

```
PRE-PIPELINE (no API calls, safe to do first):
  1. Create isolated temp library
  2. Copy book to temp staging
  3. Stage source → staging_result
  4. Extract metadata → extracted dict  ──→ SAVE extraction.json (IMMEDIATELY)
  5. Build prompt context from extracted  ──→ SAVE prompt_sent.json (IMMEDIATELY)

PIPELINE (API calls — this is where money is spent):
  6. Run acquire_source → SourceMetadata + consensus captured via wrapper

POST-PIPELINE (save everything):
  7. Save per-model LLM responses      ──→ SAVE llm_responses/*.json
  8. Save consensus details             ──→ SAVE consensus.json
  9. Save full result                   ──→ SAVE result.json
  10. Compare with ground truth         ──→ SAVE ground_truth_comparison.json
  11. Update cost log                   ──→ UPDATE COST_LOG.json
```

**Key principle: save extraction.json and prompt_sent.json BEFORE making any API call.** If the API call crashes, we still have the extraction data and can see exactly what prompt WOULD have been sent. This means zero wasted extraction work even on failed API calls.

**CRITICAL: Use `acquire_source` for step 6.** Do NOT reimplement the pipeline. The pipeline is tested and correct. The diagnostic capture happens via the consensus wrapper (Approach A below) plus the pre-pipeline extraction save.

**Revised flow:**

```python
async def process_book(book_path, output_dir, ground_truth):
    # ── PRE-PIPELINE: capture extraction and prompt (zero cost) ──
    
    # 1. Create isolated temp library
    config = create_temp_library(...)
    
    # 1b. Configure human gate for this temp library
    #     Without this, the human_gate module uses its default _GATES_DIR
    #     (Path("library/gates") — relative to CWD). If CWD is the project
    #     root, gate checkpoints silently write to the PROJECT's gates directory
    #     instead of the temp library's, polluting permanent files. If CWD is
    #     elsewhere, it crashes with FileNotFoundError. Either way: must configure.
    from shared.human_gate.src.human_gate import configure as configure_gate
    configure_gate(gates_dir=config.library_root / "gates", auto_approve=True)
    
    # 2. Copy book to staging
    staging_path = copy_to_staging(book_path, config)
    
    # 3-4. Extract metadata DIRECTLY (no staging — staging creates a lock file
    #      that would block acquire_source later)
    #      This is read-only: just format detection + HTML parsing, zero side effects.
    #      ASSUMPTION: the .htm files are not modified between this read and
    #      acquire_source's read. Safe because the owner doesn't modify files mid-run
    #      and processing is sequential.
    from engines.source.src.format_detection import detect_format
    from engines.source.src.extractors import extract_metadata
    
    source_format = detect_format(staging_path)
    extracted = extract_metadata(staging_path, source_format)
    save_json(output_dir / "extraction.json", extracted)  # SAVE IMMEDIATELY
    
    # 5. Build and save the exact prompt the LLM will see
    from engines.source.src.metadata_inference import build_prompt_context
    from engines.source.prompts.inference_v1 import SYSTEM_MESSAGE, USER_MESSAGE_TEMPLATE
    prompt_context = build_prompt_context(extracted)
    text_sample = extracted.get("text_sample", "")[:2000]
    
    # Record which metadata fields were present/absent
    metadata_fields_check = [
        "display_title", "title_full", "author_name_raw", "author_short",
        "muhaqiq_name_raw", "publisher", "shamela_category", "edition_raw",
        "compiler_name_raw", "commentator_name_raw", "riwayah",
        "page_count", "volume_count", "source_format"
    ]
    fields_present = [f for f in metadata_fields_check if extracted.get(f)]
    fields_absent = [f for f in metadata_fields_check if not extracted.get(f)]
    
    save_json(output_dir / "prompt_sent.json", {
        "system_message": SYSTEM_MESSAGE,
        "user_message": USER_MESSAGE_TEMPLATE.format(
            prompt_context=prompt_context, text_sample=text_sample
        ),
        "prompt_context_raw": prompt_context,
        "text_sample_length": len(text_sample),
        "metadata_fields_present": fields_present,
        "metadata_fields_absent": fields_absent,
    })  # SAVE IMMEDIATELY — before any API call
    
    # ── PIPELINE: API calls happen here ──
    
    # IMPORTANT: Reset capture variable before each book to prevent data bleed
    # from previous book if this book's infer_metadata fails.
    # SEQUENTIAL ONLY — this global capture pattern breaks with concurrent
    # book processing (asyncio.gather). Phase C processes books sequentially.
    # NOTE: needs `global _captured_inference` declaration here, since the
    # variable is defined at module scope and written by _capturing_infer.
    global _captured_inference
    _captured_inference = None
    
    # 6. Run full pipeline (steps 1-13) with consensus capture wrapper active
    metadata = await acquire_source(staging_path, config)
    
    # ── POST-PIPELINE: save everything ──
    
    # 7-8. Extract and save diagnostic data from captured inference result
    if _captured_inference and _captured_inference._full_consensus_result:
        consensus_result = _captured_inference._full_consensus_result
        save_per_model_responses(consensus_result, output_dir / "llm_responses")
        save_consensus_details(consensus_result, output_dir / "consensus.json")
    
    # 9. Save full result
    save_json(output_dir / "result.json", metadata.model_dump(mode="json"))
    
    # 10. Compare with ground truth
    if book_name in ground_truth:
        comparison = compare_ground_truth(metadata, ground_truth[book_name])
        save_json(output_dir / "ground_truth_comparison.json", comparison)
```

**IMPORTANT implementation detail:** `acquire_source` doesn't expose the `MetadataInferenceResult` or `ConsensusResult`. To capture per-model LLM responses, use ONE of these approaches (choose whichever is cleanest):

**Approach A (preferred): Capture via infer_metadata wrapper.**
Monkey-patch `infer_metadata` in engine.py's namespace. This captures the full MetadataInferenceResult (which, after Pre-Req 2, contains `_full_consensus_result` with per-model responses).

**CRITICAL:** You must patch the reference in the IMPORTING module, not the defining module. Python's `from X import Y` creates a local copy — patching X.Y does NOT affect the copy.

```python
# CORRECT: patch in engine.py's namespace (where infer_metadata is called)
import engines.source.src.engine as engine_mod

_original_infer = engine_mod.infer_metadata
_captured_inference = None

async def _capturing_infer(*args, **kwargs):
    global _captured_inference
    result = await _original_infer(*args, **kwargs)
    _captured_inference = result
    return result

# Before processing each book:
engine_mod.infer_metadata = _capturing_infer

# After acquire_source returns:
if _captured_inference and _captured_inference._full_consensus_result:
    consensus_result = _captured_inference._full_consensus_result
    save_per_model_responses(consensus_result, output_dir / "llm_responses")
    save_consensus_details(consensus_result, output_dir / "consensus.json")
```

**WRONG (do NOT do this):**
```python
# WRONG: patching the source module doesn't affect metadata_inference's local reference
import shared.consensus.src.consensus as consensus_mod
consensus_mod.evaluate = _wrapper  # This WON'T be seen by metadata_inference.py!
```

**Approach B (alternative): Add diagnostic_dir parameter to acquire_source.**
Add an optional parameter that makes acquire_source save intermediates to a directory. More invasive but cleaner long-term. Only use if Approach A proves too fragile.

### Output Structure

```
tests/results/source_engine/phase_c/
  PHASE_C_MANIFEST.json           # Reusability index
  PHASE_C_SUMMARY.json            # Aggregate statistics
  {book_dir_name}/
    result.json                   # Full SourceMetadata (model_dump with mode="json")
    extraction.json               # Raw extraction dict (all fields including _internal)
    prompt_sent.json              # The actual filled prompt messages sent to LLMs (for debugging)
    llm_responses/
      command_a.json              # Full ModelResponse: model_id, parsed (InferenceOutput), raw_response, latency
      opus_4_6.json               # Same structure
      fallback.json               # Only present if fallback was triggered
    consensus.json                # Agreement details: agreed, canonical_result fields, human_gate_trigger
    ground_truth_comparison.json  # Only for books with GROUND_TRUTH.json entries
```

### Prompt Capture (prompt_sent.json)

Save the EXACT messages array sent to the LLMs, after template filling. This enables post-hoc debugging of LLM decisions without re-running:

```json
{
  "system_message": "<the full system message>",
  "user_message": "<the full user message with filled {prompt_context} and {text_sample}>",
  "prompt_context_raw": "<just the output of build_prompt_context, for quick inspection>",
  "text_sample_length": 1847,
  "metadata_fields_present": ["display_title", "author_name_raw", "muhaqiq_name_raw", "publisher", "shamela_category", "edition_raw", "page_count", "source_format"],
  "metadata_fields_absent": ["compiler_name_raw", "commentator_name_raw", "riwayah", "volume_count"]
}
```

The `metadata_fields_present/absent` arrays enable quick analysis of which books had sparse vs rich metadata — critical for interpreting confidence scores.

### Per-Model Response Format (llm_responses/command_a.json)

```json
{
  "model_id": "openrouter/cohere/command-a",
  "provider": "openrouter",
  "parse_success": true,
  "error": null,
  "latency": 3.42,
  "parsed": {
    "genre": "sharh",
    "genre_confidence": 0.95,
    "structural_format": "commentary",
    "structural_format_confidence": 0.90,
    "is_multi_layer": true,
    "multi_layer_confidence": 0.92,
    "science_scope": ["nahw"],
    "science_scope_confidence": 0.88,
    "author_identification": {
      "canonical_name_ar": "جلال الدين السيوطي",
      "known_as": ["السيوطي"],
      "death_date_hijri": 911
    },
    "author_identification_confidence": 0.97
  }
}
```

The `parsed` field is `InferenceOutput.model_dump()`. Save the FULL model output, not a subset.

### Extraction Format (extraction.json)

Save the COMPLETE extraction dict including all internal/debug fields:

```json
{
  "display_title": "...",
  "title_full": "...",
  "author_name_raw": "...",
  "author_short": "...",
  "author_death_hijri": 337,
  "author_name_clean": "...",
  "muhaqiq_name_raw": "...",
  "publisher": "...",
  "shamela_category": "...",
  "edition_raw": "...",
  "edition_year_hijri": 1408,
  "page_count": 86,
  "volume_count": null,
  "source_format": "shamela_html",
  "text_sample": "<first 2000 chars of body text>",
  "_quality_issues": [],
  "_extra_card_fields": {"تقديم": "...", "أعده للشاملة": "..."},
  "_field_source_title_full": "الكتاب",
  "_field_source_author_name_raw": "المؤلف",
  "_field_source_muhaqiq_name_raw": "المحقق"
}
```

The `_` prefixed fields are diagnostic gold — they show which HTML field labels mapped to which internal fields, what quality issues were detected, and what "extra" card data exists that wasn't mapped. Do NOT strip these.

### Consensus Details Format (consensus.json)

```json
{
  "agreed": true,
  "single_model_fallback": false,
  "needs_human_gate": false,
  "human_gate_trigger": null,
  "agreement_detail": "author_identification match: 0.95 similarity",
  "model_count": 2,
  "successful_models": ["openrouter/cohere/command-a", "anthropic/claude-opus-4-6"],
  "failed_models": []
}
```

### PHASE_C_MANIFEST.json

```json
{
  "phase": "C",
  "pipeline_version": "22a260c",  // git commit hash at time of run
  "timestamp": "2026-03-10T14:30:00Z",
  "total_books": 73,
  "books": {
    "أحكام الاضطباع والرمل في الطواف": {
      "status": "success",
      "needs_rerun": false,
      "result_path": "phase_c/أحكام الاضطباع والرمل في الطواف/result.json",
      "ground_truth_available": true,
      "ground_truth_match": true,
      "cost_estimate_eur": 0.08,
      "processing_time_seconds": 12.3
    },
    ...
  }
}
```

### PHASE_C_SUMMARY.json

```json
{
  "phase": "C",
  "pipeline_version": "22a260c",
  "timestamp": "2026-03-10T15:45:00Z",
  "total_books": 73,
  "successful": 68,
  "gate_abort": 2,
  "failed": 1,
  "gate_pending": 2,
  "total_cost_eur": 8.50,
  "avg_cost_per_book_eur": 0.12,
  "avg_processing_time_seconds": 11.5,
  "consensus_stats": {
    "agreed": 60,
    "disagreed_resolved": 8,
    "fallback_triggered": 3,
    "human_gate_triggered": 2
  },
  "field_coverage": {
    "genre": {"present": 73, "high_confidence": 65},
    "author_name": {"present": 73, "high_confidence": 58},
    "is_multi_layer": {"present": 73, "high_confidence": 68}
  },
  "ground_truth_results": {
    "total_compared": 12,
    "genre_match": 11,
    "author_match": 10,
    "trust_match": 12,
    "multi_layer_match": 12
  },
  "edition_groups": [
    {
      "work_short": "إعلام الموقعين",
      "editions": ["أعلام الموقعين - ط عطاءات العلم", "إعلام الموقعين - ط العلمية", "إعلام الموقعين - ت مشهور"],
      "genre_consistent": true,
      "author_consistent": true,
      "is_multi_layer_consistent": true,
      "muhaqiq_differs": true,
      "notes": "All 3 agree on genre, author, multi-layer. Muhaqiq varies by edition as expected."
    }
  ],
  "errors": [
    {"book": "...", "error_code": "...", "message": "..."}
  ]
}
```

### Edition Groups (edition_groups in PHASE_C_SUMMARY.json)

The 73 books include ~16 edition variants across ~8 works (e.g., 3 editions of إعلام الموقعين, 2 editions of البداية والنهاية, 2 editions of شرح العقيدة الطحاوية). The `edition_groups` array compares pipeline results across editions of the same work.

**How to compute:** After all books are processed, group result.json files by core title similarity (ignoring muhaqiq/publisher/طبعة/تحقيق suffixes). For each group, compare: `genre`, `author_identification.canonical_name_ar`, `author_identification.death_date_hijri`, `is_multi_layer`, `science_scope`, `trust_tier`. Flag any field that differs across editions. Author differences within a title group are especially valuable — they may indicate the pipeline correctly identified different authors (e.g., a work and its تكملة) or incorrectly conflated them.

**Known edition groups in books.txt** (the script should detect these automatically by comparing `author_identification` + normalized title across results, but these are the expected groupings):

| Work | Editions in books.txt |
|---|---|
| إعلام الموقعين | أعلام الموقعين - ط عطاءات العلم, إعلام الموقعين - ط العلمية, إعلام الموقعين - ت مشهور |
| البداية والنهاية | البداية والنهاية - ت التركي, البداية والنهاية - ط السعادة |
| شرح العقيدة الطحاوية | شرح العقيدة الطحاوية - ط الرسالة, شرح العقيدة الطحاوية - ط الأوقاف السعودية |
| تفسير الطبري | تفسير الطبري جامع البيان - ت التركي, تفسير الطبري جامع البيان - ط دار التربية والتراث |
| حاشية ابن عابدين | حاشية ابن عابدين = رد المحتار - ط الحلبي, تكملة حاشية ابن عابدين = قرة عيون الأخيار |
| تحفة المودود | تحفة المودود بأحكام المولود - ت الأرنؤوط, تحفة المودود بأحكام المولود - ط عطاءات العلم |
| الإبانة | الإبانة عن أصول الديانة - ت العصيمي, الإبانة عن أصول الديانة - ت فوقية |
| فتاوى اللجنة الدائمة | فتاوى اللجنة الدائمة - المجموعة الأولى, فتاوى اللجنة الدائمة - المجموعة الثانية |
| ألفية ابن مالك | ألفية ابن مالك - ت القاسم, ألفية ابن مالك - ط التعاون |

**Note:** حاشية ابن عابدين + تكملة حاشية ابن عابدين are technically different works (the تكملة is by ابن عابدين's son). If the pipeline correctly identifies different authors, they should NOT be grouped. This is itself a valuable test.

---

## Budget Protection

The script MUST implement budget protection:

1. **Pre-flight estimate:** Before any API call, estimate total cost = books_remaining × €0.15 (conservative per-book estimate). If estimated_cost + already_spent > budget_ceiling, refuse to start and print how many books can be processed within budget.

2. **Per-book tracking:** After each book, estimate the cost from model response sizes and latencies. Update a running total.

3. **Rolling check:** After every 5 books, compare running cost against budget. If projected total (running_cost / books_done × total_books) exceeds budget by >20%, print a warning and pause for user confirmation.

4. **Cost log update:** After each book (not just at the end), append to `COST_LOG.json`. If the script crashes mid-run, the cost log reflects what was actually spent.

5. **Hard ceiling:** If running_cost exceeds `--budget-eur`, stop immediately. Save all results processed so far.

### Cost Estimation

Approximate per-book cost (based on Step 0 data):
- Opus 4.6: ~€0.04/book (input ~2K tokens + system ~1K, output ~800 tokens)
- Command A via OpenRouter: ~€0.03/book
- Fallback (when triggered): ~€0.03/book
- Total per book: ~€0.07–0.10

73 books × €0.10 = €7.30 theoretical baseline.

**Updated estimate based on Step 0 actual costs:** Step 0 cost €1.80 for 13 books = ~$0.15/book (2.3× the theoretical estimate). At $0.15/book: 73 books × $0.15 = $10.95 ≈ €10. With retries (~10%): ~€11. Well within the €50 ceiling. The temperature=0 fix should reduce output verbosity and bring per-book cost closer to $0.10.

---

## Error Handling

1. **Per-book isolation:** Each book runs in its own temp library. A failure in one book MUST NOT affect others. Catch all exceptions, save error details to `result.json` with `status: "error"`, and continue to the next book.

2. **Structured errors:** When a book fails, save:
```json
{
  "status": "error",
  "error_code": "E_INFERENCE_FAILED",
  "error_message": "Both primary models failed to parse response",
  "traceback": "...",
  "partial_data": {
    "extraction_completed": true,
    "inference_completed": false
  }
}
```

3. **Gate aborts (IMPORTANT):** The engine's validation step (Step 11) raises `SourceEngineError` with `ErrorCode.LOW_CONFIDENCE` when gate-severity issues are found (disputed attribution, very low confidence, author-science mismatch). This is EXPECTED behavior for books like الفقه الأكبر — not a bug. When this happens:
   - The SourceMetadata object WAS created (Step 9) but is NOT returned (the exception aborts before Step 12).
   - The monkey-patch still captures the MetadataInferenceResult (inference happens at Step 4, before validation).
   - Save with `status: "gate_abort"` instead of `status: "error"`:
```json
{
  "status": "gate_abort",
  "error_code": "LOW_CONFIDENCE",
  "error_message": "Validation gate: 1 issue(s) require human review",
  "gate_errors": ["confidence_threshold: author confidence 0.45 < 0.50"],
  "partial_data": {
    "extraction_completed": true,
    "inference_completed": true,
    "metadata_assembled": true,
    "metadata_returned": false
  }
}
```
   The `--resume` flag should treat `gate_abort` like `success` — do NOT re-process. The LLM data is captured; the gate just means the owner needs to review it.

4. **API failures:** If both primary models fail AND the fallback fails for a single book, mark it as error and continue. If 3 consecutive books fail with API errors (not parse errors), stop the run — this likely indicates an API key or rate limit issue.

5. **Resume support:** `--resume` checks `output_dir/{book_name}/result.json` existence. If present and `status: "success"` or `status: "gate_abort"`, skip. If present and `status: "error"`, re-process (the error may have been transient). `--force` overrides `--resume` and re-processes all books regardless of existing results.

---

## Ground Truth Comparison

For the 12 collection books that match existing `GROUND_TRUTH.json` entries (the original fixtures), compare:
- `genre` (exact enum match)
- `author_name` (name similarity ≥ 0.80 using `normalized_name_similarity`)
- `trust_tier` (exact match)
- `is_multi_layer` (exact match)
- `science_scope` — **NOT strict set equality.** Step 0 showed the LLM typically returns a SUPERSET of ground truth (more specific). Use this graded comparison:
  - `exact_match`: sets are identical
  - `superset`: pipeline output contains all ground truth values plus extras (LLM more specific — likely correct)
  - `subset`: pipeline output is missing some ground truth values (LLM less specific — investigate)
  - `overlap`: some values match, some don't (partial agreement — investigate)
  - `disjoint`: no overlap (clearly wrong)
- `structural_format` (exact match)
- `authority_level` (exact match)
- `level` (exact match, null-safe)
- `attribution_status` (exact match)

For the 61 NEW books (without ground truth entries), no ground truth comparison is possible yet — the owner reviews them in Phase 3 sessions and creates new ground truth entries.

The `ground_truth_comparison.json` for matched books:
```json
{
  "book": "04_hadith",
  "ground_truth_key": "04_hadith",
  "comparisons": {
    "genre": {"expected": "hadith_collection", "actual": "hadith_collection", "match": true},
    "author_name": {"expected": "القاضي إسماعيل المالكي", "actual": "القاضي أبو إسحاق إسماعيل بن إسحاق المالكي", "match": true, "similarity": 0.88},
    "trust_tier": {"expected": "verified", "actual": "verified", "match": true},
    "science_scope": {
      "expected": ["hadith"],
      "actual": ["hadith", "ulum_al_hadith"],
      "match_type": "superset",
      "overlap": ["hadith"],
      "extra_in_actual": ["ulum_al_hadith"],
      "missing_from_actual": []
    }
  },
  "all_match": true,
  "science_match_type": "superset"
}
```

---

## Matching Fixture Books to Collection

The 12 Shamela fixtures correspond to specific books in the collection. The script needs to process the FULL collection copies, not the fixture files. Match fixtures to collection directories by `display_title` from the fixture MANIFEST.json:

| Fixture | Display Title (search for this in COLLECTION_DIR) |
|---|---|
| 01_nahw_simple | أخبار أبي القاسم الزجاجي |
| 02_nahw_muhaqiq | أبنية الأسماء والأفعال والمصادر |
| 03_fiqh | أحكام الاضطباع والرمل في الطواف |
| 04_hadith | أحاديث أيوب السختيانى |
| 05_tafsir | أنوار الهلالين في التعقبات على الجلالين |
| 06_usul | آداب الفتوى والمفتي والمستفتي |
| 07_balagha | أساليب بلاغية |
| 08_death_date | آداب الصحبة لأبي عبد الرحمن السلمي |
| 09_alt_title | أسلوب خطبة الجمعة |
| 10_no_author | البدر التمام بما صح من أدلة الأحكام |
| 11_multi_small | همع الهوامع في شرح جمع الجوامع |
| 12_multi_muq | مذكرات مالك بن نبي - العفن |

The 13th fixture (alfiyyah_versified) is a plain-text fixture, not from Shamela. It is **excluded from Phase C** — it was already validated in Step 0 and will be covered in Phase D. The two Shamela alfiyyah editions in books.txt (`ألفية ابن مالك - ت القاسم` and `ألفية ابن مالك - ط التعاون`) are NEW books without ground truth — they test whether the pipeline handles the same didactic poem from Shamela HTML format.

When writing `books.txt`, the owner uses the COLLECTION_DIR directory names. The script resolves these against the actual filesystem.

---

## Testing Before Full Run

Before the full run, validate the script on 2 books:
1. One fixture book that has ground truth (e.g., `أحكام الاضطباع والرمل في الطواف` → fixture 03_fiqh)
2. One new book without ground truth

Verify:
- [ ] All output files created in correct structure
- [ ] extraction.json contains all expected fields
- [ ] llm_responses/ contains full per-model InferenceOutput
- [ ] consensus.json contains agreement details
- [ ] result.json contains complete SourceMetadata
- [ ] ground_truth_comparison.json generated for fixture book
- [ ] COST_LOG.json updated
- [ ] Resume mode works (re-running skips the 2 already-processed books)
- [ ] Cost estimate is reasonable (€0.07–0.15 per book)

---

## Cosmetic Fixes (opportunistic)

If time permits, fix these 3 non-blocking issues from Step 1:

1. **Duplicate gate checkpoint** in validation.py — two identical checks for the same condition
2. **Empty diagnostic values** — some validation errors have `{}` context dict instead of useful diagnostic data
3. **Staging cleanup log** — `_safe_remove_lock` logs at wrong level

These are low-priority. Do them only if the Phase C script is working and tested.

---

## Definition of Done

- [ ] Pre-requisite 0a: `build_prompt_context` field-name bugs fixed (muhaqiq_name_raw, edition_raw) + 5 new fields added
- [ ] Pre-requisite 0a verified: `build_prompt_context` on fixture 02 output now includes "Muhaqiq/Editor:"
- [ ] Pre-requisite 0b: System message updated with compiler/commentator/riwayah guidance
- [ ] Pre-requisite 0b tested: 2-book test shows no regressions on genre/author fields (revert if issues)
- [ ] Pre-requisite 1: temperature=0 added to _call_model in consensus.py, verified working
- [ ] Pre-requisite 2: `_full_consensus_result` field added to MetadataInferenceResult
- [ ] Pre-requisite 3: Format B fixture created with test
- [ ] Pre-requisite 4: COST_LOG.json created
- [ ] `scripts/run_phase_c.py` exists and runs
- [ ] 2-book test run produces correct output structure (see checklist below)
- [ ] Budget protection works (tested with `--budget-eur 0.01` to force ceiling hit)
- [ ] Resume mode works (re-run skips books with status "success")
- [ ] Force mode works (`--force` re-runs books even with status "success")
- [ ] Dry-run mode works
- [ ] Human gate configured: verify a gate-triggering book (e.g., الفقه الأكبر) doesn't crash or write to project gates dir
- [ ] All existing tests still pass (768+)
- [ ] Script is committed and ready for the owner to run on the full 73-book selection

### 2-Book Test Checklist

Before the full run, validate on 2 books (one fixture with ground truth, one new):

- [ ] `extraction.json` contains all expected fields INCLUDING `_` prefixed debug fields
- [ ] `prompt_sent.json` exists and was saved BEFORE the API call (check timestamps)
- [ ] `prompt_sent.json` shows "muhaqiq_name_raw" in `metadata_fields_present` (for books that have it)
- [ ] `llm_responses/` contains full per-model InferenceOutput (all fields, not summaries)
- [ ] `consensus.json` contains agreement details
- [ ] `result.json` contains complete SourceMetadata (verifiable via Pydantic model_validate)
- [ ] `ground_truth_comparison.json` generated for fixture book and shows comparison results
- [ ] COST_LOG.json updated after each book (not just at the end)
- [ ] Resume mode works (re-running skips the 2 already-processed books)
- [ ] Force mode works (`--force` re-runs the 2 books and overwrites previous results)
- [ ] Cost estimate is reasonable (€0.07–0.15 per book)
- [ ] No data loss on API failure: if one book's API call fails, extraction.json and prompt_sent.json are still present
- [ ] Gate abort handling: if a book triggers LOW_CONFIDENCE validation gate, result.json has status "gate_abort" (not "error") and llm_responses/ are still saved
