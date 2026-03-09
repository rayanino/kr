# Session 6 Plan: Integration + Plain Text + Error Paths

**Pipeline steps:** Step 9 (Handoff) + full pipeline integration
**Depends on:** Session 5 (registration + trust + validation)

---

## Read First

1. `engines/source/SPEC_CORE.md` §4.A.2 Step 9 (Handoff) and §4.A.10 (Processing Status)
2. `engines/source/SPEC_CORE.md` §7 (Error Handling — full section, all 27 core error codes)
3. `engines/source/SPEC_CORE.md` §2.1 (Input Contract — encoding detection for plain text)
4. `engines/source/SPEC_CORE.md` §8 (Configuration — staging_lock_timeout, enrichment_cycle_timeout)
5. `engines/source/contracts.py` — `ProcessingStatus`, `ErrorCode`, `ErrorSeverity`, `SourceError`
6. `engines/source/review/STEP2_EVALUATION.md` — Step 4 blocking conditions (§3)

## Modules to Build/Complete

| File | Purpose |
|------|---------|
| `engines/source/src/engine.py` | Replace stub. Full pipeline orchestrator: coordinates Steps 1–9 in sequence. |
| `engines/source/src/config.py` | Replace stub. Load all configuration from `library/config/`. |
| `engines/source/src/logger.py` | Replace stub. Structured logging to JSONL. SourceError serialization. Alert triggers. |

## Fixtures to Test Against

**Full pipeline run on ALL 13 fixtures:**
- `tests/fixtures/shamela_real/01_nahw_simple/` through `12_multi_muq/`
- `tests/fixtures/alfiyyah_versified/` — plain text format (exercises the encoding detection + plain text extractor path)
- `tests/fixtures/GROUND_TRUTH.json` — final verification against all expected values

**Error path tests (construct specific test inputs):**
- Empty file → `SRC_EMPTY_INPUT`
- Non-Arabic file (e.g., `.pdf`) → `SRC_UNSUPPORTED_FORMAT`
- Duplicate hash → `SRC_DUPLICATE_EXACT`
- Shamela file without PageText div → `SRC_FORMAT_STRUCTURE_MISSING`
- Mock LLM failure (all retries) → human gate creation
- Mock consensus disagreement → `SRC_CONSENSUS_DISAGREEMENT`
- Registry write failure (mock) → `SRC_REGISTRY_CONFLICT`
- Orphaned staging lock → cleanup on startup

## Carry-Forward Task (from Step 2 Evaluation)

**Verify all three Step 4 blocking conditions are met:**

1. **Confidence calibration analysis complete** — thresholds confirmed or adjusted. (Should be done in Session 3. If not, do it here.)
2. **Name matching A3-1 fix implemented and tested** — token-based approach in production code. (Should be done in Session 3/4. If not, do it here.)
3. **Author-specific consensus complementarity verified** — pair confirmed or updated. (Should be done in Session 3. If not, do it here.)

If ANY blocking condition is not met, it MUST be resolved in this session before declaring the source engine complete.

## Build Steps

1. **Implement `engine.py` — full pipeline orchestrator.** Coordinates all 9 steps:
   - Step 1: Validate staging directory
   - Step 2: Detect format
   - Step 3: Detect encoding (charset_normalizer for plain text) + extract metadata
   - Step 4: Run LLM inference + consensus
   - Step 5: Compute hashes + check duplicates
   - Step 6: Freeze files
   - Step 7: Register in all 3 registries (atomic)
   - Step 8: Evaluate trust
   - Step 9: Set status → `acquired`, move staging to `.processed/`

2. **Implement `config.py`.** Load all configuration:
   - Consensus models (default pair + fallback)
   - Confidence thresholds
   - File paths (staging, library root)
   - Recognized muhaqiqs list
   - Known publishers list
   - Transliteration table
   - Genre synonyms

3. **Implement `logger.py`.** Structured logging:
   - `library/logs/source_engine.jsonl` — one JSON object per log entry
   - SourceError serialization with all fields (timestamp, source_id, error_code, severity, message, recovery_action, context)
   - Alert triggers: fatal during batch, >10% same warning, gate queue >20

4. **Plain text end-to-end.** Run the full pipeline on `alfiyyah_versified/`:
   - Encoding detection (should be UTF-8)
   - Plain text extraction (title from first line, skip preamble)
   - LLM inference (sparse metadata, most fields inferred)
   - Full registration and trust evaluation

5. **Error path testing.** Exercise every core error code that CAN fire in Stage 1. Deferred error codes (`SRC_OCR_LOW_QUALITY`, `SRC_REPO_UNAVAILABLE`, etc.) should NOT fire — verify they don't.

6. **Verify Step 4 blocking conditions.** Check all three are met. Document status.

## Done When

- [ ] Full pipeline runs on all 13 fixtures, producing valid SourceMetadata
- [ ] Plain text fixture (`alfiyyah_versified`) produces correct metadata
- [ ] All core error codes from §7 that CAN fire are tested at least once
- [ ] Deferred error codes confirmed NOT to fire
- [ ] `engine.py` orchestrates all 9 steps in correct order
- [ ] Processing status tracking works: staging → acquired
- [ ] Staging cleanup: processed files moved to `.processed/`
- [ ] Orphaned staging lock cleanup on startup
- [ ] Structured logging produces valid JSONL entries
- [ ] Configuration loading works for all config files
- [ ] Step 4 blocking conditions all verified:
  - [ ] Confidence calibration complete
  - [ ] A3-1 name matching fix verified
  - [ ] Author-specific consensus complementarity verified
- [ ] Source → Normalization boundary: metadata record validates against normalization input contract
- [ ] All tests pass (deterministic + LLM-worker + integration)
