# NEXT — Source Engine Build Session 6

## Task

Build engine.py (pipeline orchestrator) and logger.py (structured logging), then run the full pipeline on all 13 fixtures with real LLM calls to produce integration test results and resolve the two remaining Step 4 blocking conditions.

## Context

503 tests pass across 14 test files. Every module except engine.py and logger.py is built and tested. config.py is complete (102 lines, tested). The orchestrator delegates all real work to existing modules — it is a coordinator, not a processor.

Note: Running `pytest --ignore=reference/` shows 723 passed, 22 skipped — the 503 figure was from before shared component tests were counted.

## Required Reading

1. `engines/source/SPEC_CORE.md` §4.A.2 (9-step workflow), §4.A.10 (processing status), §7 (error handling — ALL codes)
2. `engines/source/contracts.py` — SourceMetadata, SourceError, ProcessingStatus, ErrorCode
3. `engines/source/docs/architecture.md` — pipeline diagram + module map
4. `engines/source/docs/session5-contracts-audit.md` — 4 known SPEC defects, all resolved in code
5. `engines/source/src/exceptions.py` — SourceEngineError and make_error()
6. This file's "Data Flow" section below

## Environment

```bash
# API keys (set before running integration tests)
export ANTHROPIC_API_KEY="..."       # From /mnt/project/anthropic_api_key
export OPENROUTER_API_KEY="..."      # From /mnt/project/openrouter_api_key
```

## Module 1: engine.py — Pipeline Orchestrator

### Data Flow (implementation order, NOT SPEC step numbers)

```python
async def acquire_source(source_path: Path, config: SourceEngineConfig) -> SourceMetadata:
    """
    1. stage_source(source_path, config) → StagingResult
       [Steps 1-2 + hash computation from Step 5]

    2. extract_metadata(staging.source_path, staging.source_format) → dict
       [Step 3]

    3. await infer_metadata(extracted, source_format) → MetadataInferenceResult
       [Step 4 — async, makes LLM calls]

    4. check_exact_duplicate(staging.composite_hash, source_registry) → Optional[str]
       [Step 5 — if match, log SRC_DUPLICATE_EXACT, cleanup lock, return early]

    5. REGISTER AUTHOR: lookup_or_register_author(name, death_date, school, source_id)
       → (ScholarReference, Optional[gate_checkpoint_id])
       [Uses inference.author_reference dict for name_arabic and death_date_hijri.
        For school: extract from inference.canonical_output.author_identification.school_affiliations
        — pass the first value, or None if empty.
        If gate_checkpoint_id is not None, an AUTHOR_DISAMBIGUATION gate was created —
        add to the human_gate list.
        MUST happen before freeze and before register_source — the canonical_id is needed
        for work_id slug generation and for the SourceMetadata.author field.
        Import from: engines.source.src.registries.scholar_registry]

    6. REGISTER MUHAQIQ (if extracted has muhaqiq_name_raw or muhaqiq_name_clean):
       lookup_or_register_muhaqiq(name, source_id) → ScholarReference
       [From engines/source/src/registries/scholar_registry.py]

    7. freeze_source(staged_path, source_id, library_root, hashes, timestamps) → FreezeResult
       [Step 6]

    8. Assemble SourceMetadata object from staging + extraction + inference + freeze +
       author ScholarReference + muhaqiq ScholarReference
       [All fields populated except trust]

    9. evaluate_trust(author_ref, author_record, muhaqiq_name, publisher,
                      authority_level, text_fidelity, source_id,
                      recognized_muhaqiqs=..., known_publishers=...) → tuple
       [Step 8 — MUST happen BEFORE registration because SourceRegistryEntry needs trust_tier]

    10. Add trust fields to SourceMetadata. Set status = ACQUIRED.
        Create human gates for: author ambiguity, consensus disagreement, low confidence.

    11. validate_source_metadata(metadata_dict, registries) → list[ValidationError]
        [§5 Layer 1 — if blocking errors, abort]

    12. register_source(metadata, library_root, config) → None
        [Step 7 — writes metadata.json + source/work registries atomically.
         NOTE: register_source does NOT register the primary author — that
         happened in step 5. It DOES handle genre chain processing which
         may register base work authors for sharh/hashiyah relationships.]

    13. Move staging/{source} to staging/.processed/{source_id}/
        Remove staging lock. Log success.
        [Step 9]
    """
```

**IMPORTANT: Work-level duplicate detection.** `check_work_duplicate()` from `deduplication.py` is NOT called as a separate pipeline step. Work matching happens automatically inside `register_source` → `work_registry_store.build_entry()` → work_id slug collision detection. If the work_id already exists in works.json, `register_source` adds this source_id to the existing work's `source_ids` list. To log `SRC_DUPLICATE_WORK` (Info), engine.py should check BEFORE calling register_source whether the work_id already exists in the work registry. Load the work registry, generate the work_id using `text_utils.generate_work_id()`, and check if it's present. If so, log the info event — but do NOT abort. The source still gets acquired.

### Critical Implementation Notes

**Trust before registration.** The SPEC numbers trust as Step 8 and registration as Step 7, but `SourceRegistryEntry.trust_tier` is required at write time. Compute trust BEFORE calling register_source. The SourceMetadata object must be fully built (all fields including trust) before registration.

**Scholar record for trust evaluation.** `evaluate_trust()` takes `author_record: Optional[ScholarAuthorityRecord]`. Since the author was registered in step 5 (lookup_or_register_author), load the scholar record from `library/registries/scholars.json` using the `canonical_id` from the returned ScholarReference. This gives you the full `ScholarAuthorityRecord` with `death_date_hijri` that the trust evaluator needs.

**Async entry point.** `infer_metadata` is async. The top-level `acquire_source` function must be `async def`. Provide a synchronous wrapper `acquire_source_sync(path, config)` that calls `asyncio.run()` for CLI usage.

**Dedup check timing.** The composite hash is already computed by `stage_source` (in `StagingResult.composite_hash`). Dedup uses this hash — it does NOT re-hash. The dedup check must happen AFTER inference (because work_duplicate needs the author_id from inference) but BEFORE freezing (to avoid freezing a duplicate).

**Human gate accumulation.** Multiple human gates can be created per source (e.g., author ambiguity AND low confidence on genre). Collect all gate triggers during processing. If `MetadataInferenceResult.needs_human_gate` is True, create the appropriate gates from `MetadataInferenceResult.human_gate_triggers`. The source still proceeds through the pipeline — it's not blocked. Gates are advisory.

**Staging lock lifecycle.** `stage_source` creates the lock and returns `StagingResult.lock_path`. The orchestrator removes the lock in a `finally` block after successful acquisition OR after a fatal error. Never leave orphaned locks.

**Status transitions.** Set `status = ProcessingStatus.ACQUIRED` before calling `register_source`. Since `register_source` writes metadata.json, the status must be correct at that point. Do NOT set status to STAGING first and then update after — that would require a second write to metadata.json.

### Startup Cleanup

The orchestrator exposes a `startup_cleanup(config)` function:

1. **Orphaned staging locks.** Call `staging.cleanup_orphaned_locks(config.staging_path, config.staging_lock_timeout)`. Already implemented — just call it.

2. **Orphaned registrations.** Call `registries.check_orphaned_registrations(config.library_root)`. Already implemented — completes or rolls back interrupted registrations.

### Error Handling Pattern

```python
try:
    staging_result = stage_source(source_path, config)
except SourceEngineError as e:
    logger.log_error(e.error)
    raise

try:
    extracted = extract_metadata(staging_result.source_path, staging_result.source_format)
except SourceEngineError as e:
    e.error.source_id = staging_result.source_id
    logger.log_error(e.error)
    remove_staging_lock(staging_result.lock_path)
    raise
# ... etc for each step
```

Every SourceEngineError is caught, logged via logger.log_error(), and re-raised. The staging lock is cleaned up in a `finally` block. Fatal errors stop processing for this source but must not crash the process (other sources in a batch continue).

### Module Signature

```python
# engines/source/src/engine.py

async def acquire_source(
    source_path: Path,
    config: SourceEngineConfig | None = None,
) -> SourceMetadata:
    """Acquire a single source through the 9-step pipeline."""

def acquire_source_sync(
    source_path: Path,
    config: SourceEngineConfig | None = None,
) -> SourceMetadata:
    """Synchronous wrapper around acquire_source for CLI usage."""

def startup_cleanup(config: SourceEngineConfig | None = None) -> list[str]:
    """Run startup checks. Returns list of actions taken."""

async def acquire_batch(
    source_paths: list[Path],
    config: SourceEngineConfig | None = None,
) -> list[tuple[Path, SourceMetadata | SourceError]]:
    """Acquire multiple sources. Each source is independent — one failure
    does not stop the batch. Returns (path, result_or_error) tuples."""
```

### SourceMetadata Assembly

The most complex part of engine.py is assembling the SourceMetadata object from the intermediate results. Here's the field mapping:

```
From StagingResult:
  source_id            ← staging.source_id
  source_format        ← staging.source_format
  frozen_hash          ← freeze.frozen_hash  (from FreezeResult)
  frozen_path          ← str(freeze.frozen_path)
  frozen_file_hashes   ← freeze.frozen_file_hashes

From extract_metadata dict:
  title_arabic         ← extracted.get("display_title") or extracted.get("title_full") or extracted.get("title_arabic")
                          [Shamela uses "display_title", plain text uses "title_arabic" — must try both]
  publisher            ← extracted.get("publisher")
  page_count           ← extracted.get("page_count") or extracted.get("body_page_count")
  volume_count         ← extracted.get("volume_count") (parsed from volume_count_raw by Shamela extractor)
  volumes              ← [VolumeInfo(...) for v in extracted.get("volumes", [])]
  format_specific_metadata ← extracted.get("format_specific_metadata", {})

From MetadataInferenceResult:
  genre                ← Genre(inference.genre)
  structural_format    ← StructuralFormat(inference.structural_format)
  authority_level      ← AuthorityLevel(inference.authority_level)
  level                ← WorkLevel(inference.level) if inference.level else None
  science_scope        ← inference.science_scope
  is_multi_layer       ← inference.is_multi_layer
  text_layers          ← [TextLayer(**l) for l in inference.text_layers]
  attribution_status   ← AttributionStatus(inference.attribution_status)
  confidence_scores    ← InferredFieldConfidence(**inference.confidence_scores)
  text_fidelity        ← TextFidelity(inference.text_fidelity)
  needs_review_fields  ← inference.needs_review_fields
  scholarly_context    ← ScholarlyContext(**inference.canonical_output.scholarly_context.model_dump())
                          if inference.canonical_output and inference.canonical_output.scholarly_context
                          else None
  genre_chain          ← build GenreChain from inference.canonical_output.genre_chain if present

From lookup_or_register_author (step 5 in data flow):
  author               ← ScholarReference returned by lookup_or_register_author()
                          [Built from inference.author_reference dict: name_arabic, death_date_hijri.
                           The lookup call returns a ScholarReference with canonical_id assigned.
                           Import from: engines.source.src.registries.scholar_registry]

From lookup_or_register_muhaqiq (step 6 in data flow):
  muhaqiq              ← ScholarReference returned by lookup_or_register_muhaqiq()
                          if extracted has "muhaqiq_name_clean" or "muhaqiq_name_raw", else None
                          [Import from: engines.source.src.registries.scholar_registry]

From evaluate_trust (returns tuple: tier, score, factors, reason):
  trust_tier           ← trust_tier  (TrustTier enum)
  trust_score          ← trust_score (float)
  trust_factors        ← trust_factors (list[TrustworthinessFactor])
  trust_reason         ← trust_reason (str)

Generated:
  human_label          ← f"{title_short} - {author_short}" (truncated)
  work_id              ← computed by register_source (slug generation)
  title_transliterated ← None (generated during registration)
  status               ← ProcessingStatus.ACQUIRED
  intake_timestamp     ← datetime.now(UTC).isoformat()
  acquisition_path     ← AcquisitionPath.MANUAL
  text_fidelity_reason ← GENERATED BY ENGINE.PY (see note below)
  metadata_history     ← []
  enrichment_sources   ← []
```

**work_id must be set BEFORE calling register_source.** `register_source` writes `metadata.model_dump()` to metadata.json but does NOT update `metadata.work_id` — it only sets `src_entry.work_id` internally. Two approaches:

Option A (preferred): Engine.py generates the work_id itself before calling register_source:
```python
from engines.source.src.text_utils import generate_work_id
work_id = generate_work_id(author_ref.name_arabic, title_arabic, config.transliteration)
# Set on metadata before calling register_source
```

Option B: Fix register_source to update metadata before writing metadata.json. Add before the `_atomic_json_write` call in register_source:
```python
# Update metadata with the actual work_id (may differ from placeholder)
metadata_dict = metadata.model_dump(mode="json")
metadata_dict["work_id"] = actual_work_id
_atomic_json_write(metadata_path, metadata_dict)
```

Either way, the metadata.json MUST contain the real work_id, not "pending".

**text_fidelity_reason generation.** `MetadataInferenceResult` provides `text_fidelity` (the enum value) but NOT `text_fidelity_reason` (a required string on SourceMetadata). Engine.py must generate the reason:
- Base reason from format: "Shamela structured HTML — high fidelity digital text" or "Plain text — standard encoding"  
- Then check extracted `_quality_issues` list. Each quality issue can downgrade fidelity:
  - `page_count_mismatch` → downgrade to MEDIUM, append "page count mismatch detected"
  - `encoding_suspect` (U+FFFD found) → downgrade to LOW, append "encoding replacement characters detected"
  - `high_empty_ratio` → downgrade to MEDIUM, append "high empty page ratio"
- Log the corresponding error codes (SRC_PAGE_COUNT_MISMATCH, SRC_ENCODING_SUSPECT, SRC_HIGH_EMPTY_RATIO)
- The final `text_fidelity_reason` is the concatenation of all applicable reasons

## Module 2: logger.py — Structured Logging

### Design

Append-only JSONL writer to `library/logs/source_engine.jsonl`.

```python
# engines/source/src/logger.py

class SourceEngineLogger:
    """Structured JSONL logger for the source engine.

    SPEC §7: Every error is logged. Alert triggers fire on thresholds.
    """

    def __init__(self, log_path: Path | None = None):
        """Default path: library/logs/source_engine.jsonl"""

    def log_error(self, error: SourceError) -> None:
        """Append a SourceError as JSON to the log file."""

    def log_event(self, event_type: str, source_id: str | None, message: str,
                  context: dict | None = None) -> None:
        """Log a non-error event (intake start, intake success, etc.)."""

    def check_alerts(self) -> list[str]:
        """Check alert triggers against recent log entries.

        Returns list of alert messages (empty if no alerts).

        SPEC §7 alert triggers:
        1. Fatal error during batch processing
        2. >10% of sources in current batch hitting same warning code
        3. Human gate queue > 20 items
        """

    def get_batch_stats(self) -> dict:
        """Return stats for the current batch: counts by severity, by error code."""
```

### JSONL Format

Each line is a JSON object. Two types of records:

```json
{"type": "error", "timestamp": "...", "source_id": "...", "error_code": "SRC_...", "severity": "fatal", "message": "...", "recovery_action": "rejected", "context": {...}}
{"type": "event", "timestamp": "...", "source_id": "...", "event": "intake_start", "message": "Starting acquisition of ..."}
```

Error records are `SourceError.model_dump()` with a `"type": "error"` field prepended.

### Alert State

Track alert state per batch in memory:
- `_batch_error_codes: Counter[str]` — count of each warning code in current batch
- `_batch_source_count: int` — total sources attempted in current batch
- `_fatal_seen: bool` — any fatal error in current batch

`check_alerts()` reads the gate index to count pending gates for the third trigger.

## Tests for Session 6

### 6a: Engine Orchestration (deterministic — mock LLM calls)

Test the orchestrator with mocked `infer_metadata` that returns pre-built `MetadataInferenceResult` objects. These tests verify the coordination logic without making real API calls.

```
test_acquire_shamela_simple          — fixture 03_fiqh, happy path, mock returns correct metadata
test_acquire_plain_text              — fixture alfiyyah_versified, plain text path
test_acquire_exact_duplicate         — pre-populate registry with matching hash → SRC_DUPLICATE_EXACT
test_acquire_work_duplicate          — pre-populate work registry with same author+title slug → SRC_DUPLICATE_WORK info logged, source still acquired and linked to existing work_id
test_acquire_consensus_disagreement  — mock returns needs_human_gate=True → human gate created
test_acquire_low_confidence          — mock returns confidence < 0.50 → SRC_LOW_CONFIDENCE, human gate
test_acquire_staging_modified        — modify file after staging → SRC_STAGING_MODIFIED
test_acquire_empty_input             — empty directory → SRC_EMPTY_INPUT
test_acquire_unsupported_format      — .pdf file → SRC_UNSUPPORTED_FORMAT
test_acquire_batch_isolation         — batch of 3 sources, second fails → first and third succeed
test_startup_cleanup_orphaned_lock   — old lock file → cleaned up
test_startup_cleanup_orphaned_reg    — pending_registration file → completed or rolled back
test_metadata_assembly_completeness  — verify all SourceMetadata fields populated (no None where required)
test_staging_moved_to_processed      — after success, staging dir moved to .processed/
test_status_transition               — status goes STAGING → ACQUIRED
```

### 6b: Logger (deterministic)

```
test_log_error_jsonl_format          — log a SourceError, read back, verify JSON structure
test_log_event_jsonl_format          — log an event, verify format
test_append_only                     — multiple writes, verify all present
test_alert_fatal_during_batch        — log a fatal → check_alerts returns alert
test_alert_same_warning_threshold    — >10% same warning code → alert
test_alert_gate_queue_threshold      — mock >20 pending gates → alert
test_no_alerts_normal_operation      — normal batch → no alerts
```

### 6c: Error Path Coverage

For each core error code that CAN fire in Stage 1, verify it fires under the correct condition. Group by step:

| Error Code | Step | How to Trigger |
|-----------|------|---------------|
| SRC_EMPTY_INPUT | 1 | Empty staging directory |
| SRC_UNSUPPORTED_FORMAT | 2 | Non-HTM/TXT file |
| SRC_FORMAT_STRUCTURE_MISSING | 3 | .htm file without PageText div |
| SRC_ENCODING_SUSPECT | 3 | UTF-8 file with U+FFFD characters |
| SRC_PAGE_COUNT_MISMATCH | 3 | Physical page count wildly different from digital |
| SRC_CONTENT_MINIMAL | 3 | Source with <3 pages |
| SRC_HIGH_EMPTY_RATIO | 3 | Source with >25% near-empty pages |
| SRC_CONSENSUS_DISAGREEMENT | 4 | Mock two models disagreeing on author |
| SRC_LOW_CONFIDENCE | 4 | Mock confidence < 0.50 |
| SRC_AUTHOR_AMBIGUOUS | 4 | Mock ambiguous scholar match (0.50-0.85) |
| SRC_ATTRIBUTION_DISPUTED | 4 | Mock disputed attribution status |
| SRC_METADATA_INCONSISTENCY | 4 | Mock inconsistent genre/format combination |
| SRC_DUPLICATE_EXACT | 5 | Pre-populated registry with matching hash |
| SRC_DUPLICATE_WORK | 7 | Pre-populated work registry with same work_id slug → Info logged during registration |
| SRC_STAGING_MODIFIED | 6 | Modify file between staging and freeze |
| SRC_FREEZE_COPY_CORRUPT | 6 | Mock hash mismatch after copy |
| SRC_SCHEMA_VIOLATION | val | SourceMetadata with missing required field |
| SRC_MULTI_LAYER_VIOLATION | val | is_multi_layer=True but empty text_layers |
| SRC_REGISTRATION_INTERRUPTED | startup | Orphaned pending_registration file |

Deferred error codes (should NOT fire): SRC_OCR_LOW_QUALITY, SRC_REPO_UNAVAILABLE, SRC_KITAB_CACHE_MISSING, SRC_KITAB_CACHE_CORRUPT, SRC_USUL_DATA_MISSING, SRC_WIKIDATA_TIMEOUT, SRC_COMPARISON_DEFERRED, SRC_OPENITI_CACHE_CORRUPT, SRC_COMPARISON_INCONCLUSIVE.

### 6d: Full Pipeline Integration (REAL LLM calls — ~$1-2)

Run the full pipeline on all 13 fixtures + alfiyyah_versified with real API calls. Save results to `tests/results/source_engine/session6/`.

**Script: `scripts/phases/run_session6_integration.py`**

For each fixture:
1. Copy fixture to a temp staging directory
2. Call `await acquire_source(staging_path, config)`
3. Save the resulting SourceMetadata as JSON
4. Compare against `tests/fixtures/GROUND_TRUTH.json`
5. Record: genre match, author match, trust_tier match, any errors, cost

Output format per fixture (matches TESTING_PROTOCOL.md §Result Format):
```json
{
  "source_id": "src_...",
  "fixture": "03_fiqh",
  "extraction": { ... },
  "inference": { ... },
  "trust": { ... },
  "registration": { ... },
  "validation": { ... },
  "ground_truth": { "genre_match": true, "trust_match": true, "author_match": true }
}
```

Summary output: `tests/results/source_engine/session6/SESSION6_SUMMARY.json`

### 6e: Step 4 Blocking Condition Verification

**Condition 1 (CG-1) — Confidence calibration.** During the 6d integration run, extract confidence scores from each fixture's inference results. Analyze:
- Do any models produce confidence > 0.90 on fields they got wrong?
- Are the 0.50/0.70 thresholds producing reasonable gate rates?
- Document findings in `tests/results/source_engine/session6/CONFIDENCE_ANALYSIS.md`

**Condition 2 (A3-1) — Name matching.** DONE. Token-based `normalized_name_similarity()` in production. Tests confirm.

**Condition 3 (CG-5) — Author complementarity.** During the 6d integration run, compare Command A and Opus 4.6 outputs on `author_identification` specifically:
- On how many fixtures do they agree on author?
- When they disagree, who was right?
- Document findings in `tests/results/source_engine/session6/AUTHOR_COMPLEMENTARITY.md`

### 6f: Boundary Verification

After the 6d integration run, verify each produced `metadata.json` validates against the normalization engine's input expectations:

```python
# The normalization engine reads these fields from metadata.json:
NORMALIZATION_REQUIRED_FIELDS = [
    "source_id", "source_format", "work_id", "text_fidelity",
    "structural_format", "is_multi_layer", "genre", "volume_count"
]
# Verify all are present and non-null in every produced metadata.json
```

Also verify:
- `frozen/` directory exists for each source_id
- Frozen files are read-only (or marked as such)
- `source_format` value is in the normalization engine's recognized set

## Known SPEC Defects (DO NOT "FIX")

1. **Trust evaluator uses validated formula, not SPEC text.** SPEC §4.A.8 says `author_standing` requires "prior sources" for 0.90 classical tier. Implementation uses only `death_date ≤ 1000` — validated 13/13 correct. DO NOT change.

2. **TRANSLIT_MAP: إ → 'i', not 'a'.** SPEC says 'a'. Implementation correctly uses 'i'. DO NOT change.

3. **config.py is already complete.** session-6-plan.md says "Replace stub for config.py" — this is stale. DO NOT rebuild.

## Done When

- [ ] `engine.py` orchestrates all 9 steps — acquire_source() returns valid SourceMetadata
- [ ] `logger.py` writes valid JSONL, SourceError serialization works, alert triggers functional
- [ ] All 6a orchestration tests pass (mock LLM, ~15 tests)
- [ ] All 6b logger tests pass (~7 tests)
- [ ] All fireable error codes tested in 6c (~19 tests)
- [ ] All 14 fixtures produce valid SourceMetadata in 6d integration run
- [ ] Confidence calibration analysis complete (CG-1 resolved)
- [ ] Author complementarity analysis complete (CG-5 resolved)
- [ ] All produced metadata.json files pass normalization boundary check (6f)
- [ ] Staging directories moved to .processed/ after successful acquisition
- [ ] Startup cleanup handles orphaned locks and registrations
- [ ] All existing 723+ tests still pass (regression: `pytest --ignore=reference/`)

## Session Budget

LLM API cost: ~$1-2 for 14 fixtures × 2 models. Set a $5 hard ceiling. If cost exceeds this, stop and investigate.
