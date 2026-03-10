# NEXT — Source Engine Session 6: Full Pipeline Integration

**Session type:** BUILD — implement engine orchestrator, config loader, logger, plain text end-to-end, error path testing
**Pipeline steps:** Step 9 (Handoff) + full pipeline integration
**Depends on:** Session 5b (503 tests passing: all registries, trust, validation, scholar authority, human gate)

---

## What to Read

Read these files in order before writing any code:

1. `engines/source/SPEC_CORE.md` §4.A.2 — Full Acquisition Workflow (all 9 steps, lines 211–557)
2. `engines/source/SPEC_CORE.md` §4.A.2 Step 9 — Handoff (lines 531–557)
3. `engines/source/SPEC_CORE.md` §4.A.10 — Processing Status Lifecycle (lines 1400–1453)
4. `engines/source/SPEC_CORE.md` §7 — Error Handling (all 27 core error codes, lines 1576–1827)
5. `engines/source/SPEC_CORE.md` §8 — Configuration (lines 1828–1958)
6. `engines/source/SPEC_CORE.md` §2.1 — Input Contract (encoding detection for plain text, lines 58–76)
7. `engines/source/contracts.py` — `ProcessingStatus`, `ErrorCode`, `ErrorSeverity`, `SourceError`
8. `engines/source/session-6-plan.md` — This session's specific requirements
9. `engines/source/STRATEGIC_PLAN.md` — Overall project context

---

## What to Build

### Module 1: `engines/source/src/config.py` — Configuration Loader (~120 lines)

Replace the stub. Loads all configuration from `library/config/`:

**Load from files:**
- `library/config/consensus.json` — consensus model pairs, fallback models, timeout settings
- `library/config/confidence_thresholds.json` — thresholds for human gate triggers (0.70 needs_review, 0.50 blocks_write)
- `library/config/recognized_muhaqiqs.json` — list of well-known muhaqiqs for trust evaluation
- `library/config/known_publishers.json` — publisher reputation scores
- `library/config/transliteration.json` — Arabic→Latin mapping tables for slug generation
- `library/config/genre_synonyms.json` — alternative genre names and mappings

**Implement:**
- `load_config(library_root: Path) -> SourceEngineConfig`
  - Loads all config files
  - Validates structure (Pydantic)
  - Returns populated SourceEngineConfig
  - Falls back to defaults if files missing (but logs warning)
- `save_config(config: SourceEngineConfig, library_root: Path)`
  - For enrichment updates and owner customization

**Test:** `engines/source/tests/test_config.py` — already has basic tests, extend with file loading tests

---

### Module 2: `engines/source/src/logger.py` — Structured Logging (~100 lines)

Replace the stub. Structured logging to JSONL:

**Implement:**
- `setup_logger(library_root: Path) -> logging.Logger`
  - Creates `library/logs/source_engine.jsonl` if not exists
  - Returns configured logger
- `log_error(logger, error: SourceError)`
  - Serializes SourceError to JSON
  - Writes to JSONL
- `log_processing_step(logger, source_id: str, step_name: str, status: str, duration_ms: int)`
  - Tracks pipeline progression
- `check_alert_triggers(library_root: Path) -> list[str]`
  - SPEC §8 alert conditions:
    1. Fatal error during batch processing
    2. >10% same warning code in last 100 entries
    3. Human gate queue >20 pending checkpoints
  - Returns list of triggered alerts

**Test:** `engines/source/tests/test_logger.py` — create new test file

---

### Module 3: `engines/source/src/engine.py` — Full Pipeline Orchestrator (~350 lines)

Replace the stub. Coordinates all 9 steps:

**Implement `process_source(acquisition_path: Path, *, library_root: Path, config: SourceEngineConfig | None = None) -> SourceMetadata`:**

**Step 1: Validate Staging**
- Check acquisition_path exists and readable
- If directory: should contain single .htm or .txt file (raise `SRC_EMPTY_INPUT` if empty)
- Create staging lock (`.kr_processing` marker file)
- Error: `SRC_STAGING_INVALID`

**Step 2: Detect Format**
- Call `format_detection.detect_format()`
- Supported: `shamela_html`, `plain_text`
- Error: `SRC_UNSUPPORTED_FORMAT` for anything else

**Step 3: Extract Metadata + Detect Encoding**
- For plain_text: use `charset_normalizer` to detect encoding (SPEC §2.1)
- Call appropriate extractor (`shamela_html.py` or `plain_text.py`)
- Error: `SRC_FORMAT_STRUCTURE_MISSING`, `SRC_EXTRACTION_FAILED`

**Step 4: LLM Inference + Consensus**
- Call `metadata_inference.infer_metadata()`
- If consensus disagrees → create human gate checkpoint
- Error: `SRC_CONSENSUS_DISAGREEMENT`, `SRC_LLM_TIMEOUT`

**Step 5: Hash + Dedup Check**
- Call `deduplication.compute_hashes()`
- Check against source registry
- Error: `SRC_DUPLICATE_EXACT`

**Step 6: Freeze Files**
- Call `freezer.freeze_source()`
- Verify frozen_hash matches staging_hash
- Error: `SRC_FREEZE_COPY_CORRUPT`, `SRC_FREEZE_PERMISSION_FAILED`

**Step 7: Register**
- Call `registries.register_source()`
- Atomic write to all 3 registries
- Error: `SRC_REGISTRATION_INTERRUPTED`, `SRC_REGISTRY_CONFLICT`

**Step 8: Evaluate Trust**
- Call `trust_evaluator.evaluate_trust()`
- Update metadata.trust_tier and trust_score

**Step 9: Handoff**
- Set `processing_status = "acquired"`
- Move staging to `library/staging/.processed/{source_id}/` (archive)
- Write final metadata.json to `library/sources/{source_id}/metadata.json`
- Delete staging lock
- Return SourceMetadata

**Error Handling:**
- Wrap each step in try/except
- Create SourceError for failures
- Log all errors
- If fatal: clean up staging lock, move staging to `.failed/`
- Return error via raise or status field depending on severity

**Test:** `engines/source/tests/test_engine.py` — create comprehensive test file with mocked components

---

### Module 4: `engines/source/src/extractors/plain_text.py` — Plain Text Extractor (~80 lines)

Complete the implementation. SPEC §2.1 and §4.A.3 requirements:

**Implement `extract_metadata(file_path: Path) -> dict`:**
- Detect encoding using `charset_normalizer` (UTF-8, Windows-1256, ISO-8859-6)
- Read file content
- Extract title from first non-empty line
- Extract page_count (estimate: line_count / 30)
- Return dict with: title_arabic, author_name_raw (None — must be inferred), page_count, text_fidelity ("high" for UTF-8, "medium" for others)

**Test:** Use `tests/fixtures/alfiyyah_versified/alfiyyah.txt`

---

### Module 5: Startup Recovery — `engines/source/src/engine.py`

Add startup function:

**Implement `startup_recovery(library_root: Path)`:**
- Call `registries.check_orphaned_registrations()` — WAL recovery
- Check for orphaned staging locks (`.kr_processing` files older than 1 hour)
  - If found: log warning, delete lock, move staging to `.interrupted/`
- Call `logger.check_alert_triggers()` and log any alerts

Call this at the start of any batch processing script.

---

## Error Path Testing

Create `engines/source/tests/test_error_paths.py` to exercise all core error codes:

| Error Code | Test Scenario |
|------------|---------------|
| `SRC_EMPTY_INPUT` | Empty staging directory |
| `SRC_UNSUPPORTED_FORMAT` | PDF file (not supported in core) |
| `SRC_FORMAT_STRUCTURE_MISSING` | Shamela HTML without PageText div |
| `SRC_EXTRACTION_FAILED` | Malformed HTML (BeautifulSoup parse error) |
| `SRC_DUPLICATE_EXACT` | Same hash in registry |
| `SRC_FREEZE_COPY_CORRUPT` | Mock: staging_hash != frozen_hash |
| `SRC_FREEZE_PERMISSION_FAILED` | Mock: chmod fails |
| `SRC_REGISTRATION_INTERRUPTED` | Mock: FileLock timeout |
| `SRC_REGISTRY_CONFLICT` | Mock: JSON parse error on registry file |
| `SRC_LLM_TIMEOUT` | Mock: LLM request timeout |
| `SRC_CONSENSUS_DISAGREEMENT` | Mock: models return different genres |

**Deferred error codes (should NOT fire in core):**
- `SRC_OCR_LOW_QUALITY` — OCR not in core
- `SRC_REPO_UNAVAILABLE` — OpenITI enrichment not in core
- All other §4.B error codes

---

## Full Pipeline Testing

### Fixture Coverage

Run full pipeline on ALL fixtures:

**Shamela HTML (12 fixtures):**
1. `01_nahw_simple` — single-volume, simple structure
2. `02_usul_simple` — usul fiqh, tahqiq publisher
3. `03_fiqh_mukhtasar` — genre: mukhtasar
4. `04_hadith_sharh` — genre: sharh_hadith
5. `05_nahw_nazm` — genre: nazm
6. `06_usul` — multi-volume
7. `07_fiqh_risalah` — genre: risalah
8. `08_aqidah` — genre: aqidah
9. `09_mawsuah` — genre: mawsuah
10. `10_classical` — classical scholar (pre-1000 AH)
11. `11_multi_small` — multi-layer (sharh with genre_chain)
12. `12_multi_muq` — multiple muhaqiqs

**Plain Text (1 fixture):**
13. `alfiyyah_versified` — plain text, nazm genre

### Verification

For each fixture:
- ✅ Metadata extracted correctly
- ✅ LLM inference produces valid fields
- ✅ Scholar registered (or matched)
- ✅ Work registered
- ✅ Trust score computed
- ✅ Status = "acquired"
- ✅ Files frozen at `library/frozen/{source_id}/`
- ✅ Metadata at `library/sources/{source_id}/metadata.json`
- ✅ Ground truth match (if exists in `GROUND_TRUTH.json`)

### Validation Against Normalization Input Contract

After processing all fixtures:
- Load each `library/sources/{source_id}/metadata.json`
- Validate against normalization engine's input contract (check `engines/normalization/contracts.py`)
- Ensure no contract violations at the boundary

---

## Carry-Forward Tasks (from Step 2 Evaluation)

**Verify all three Step 4 blocking conditions are met:**

1. **Confidence calibration analysis complete** — thresholds confirmed or adjusted
   - Check: do models produce appropriately calibrated confidence scores?
   - If models output 0.85+ even when wrong, raise thresholds
   - If appropriately calibrated, keep SPEC values (0.70 needs_review, 0.50 blocks_write)

2. **Name matching A3-1 fix implemented and tested** — token-based approach in production code
   - Verify: `scholar_authority` uses token-based matching (not exact string match)
   - Test: author name variants should match correctly

3. **Author-specific consensus complementarity verified** — pair confirmed or updated
   - Verify: consensus pair has complementary error profiles on author identification
   - Check: "at least one got it right" rate should be high

**If ANY blocking condition is not met, it MUST be resolved in this session.**

---

## Done When

- [ ] **config.py:** Loads all 6 config files correctly, validates structure, returns SourceEngineConfig
- [ ] **logger.py:** Writes structured JSONL entries, alert triggers work
- [ ] **engine.py:** Orchestrates all 9 steps in correct order
- [ ] **plain_text.py:** Extracts metadata from `alfiyyah.txt`, detects UTF-8 encoding
- [ ] **startup_recovery:** Checks orphaned registrations and staging locks on startup
- [ ] **Error path tests:** All 11 core error codes tested, deferred codes confirmed NOT to fire
- [ ] **Full pipeline:** All 13 fixtures produce valid SourceMetadata
- [ ] **Processing status:** `acquired` status set correctly, staging moved to `.processed/`
- [ ] **Frozen files:** All sources frozen at `library/frozen/{source_id}/`
- [ ] **Metadata files:** Valid JSON at `library/sources/{source_id}/metadata.json`
- [ ] **Normalization boundary:** All metadata files validate against normalization input contract
- [ ] **Ground truth:** All fixtures with ground truth entries match expected values
- [ ] **Step 4 blocking conditions:** All 3 verified and documented
- [ ] **All tests pass:** ~550-600 total tests (503 from 5b + ~50-100 new)

---

## API Keys Required

**YES** — LLM calls for metadata inference on all 13 fixtures

Required keys (from project knowledge):
- `anthropic_api_key` — for Claude models
- `openai_api_key` — for GPT models  
- `mistral_api_key` — for Mistral models

Cost estimate: ~13 fixtures × $0.08-0.12/book × 2 models = ~$2-3 total

---

## Build Tips

1. **Start with config.py and logger.py** — pure infrastructure, no dependencies
2. **Then plain_text.py** — simple extractor, easy to test independently
3. **Then engine.py foundation** — basic orchestration without error handling
4. **Add error handling** — wrap each step, log errors, cleanup on failure
5. **Test error paths** — create test inputs that trigger each error code
6. **Full pipeline run** — process all 13 fixtures
7. **Verify blocking conditions** — check confidence calibration, name matching, consensus complementarity
8. **Final validation** — check normalization boundary, ground truth match

---

## Known Issues to Address

From STRATEGIC_PLAN Phase B (pending verification):

1. **Consensus flow:** Does timeout → retry → simplified → fallback actually work?
2. **Registration atomicity:** Does WAL rollback restore from .bak correctly?
3. **Trust re-evaluation path:** Is "prior sources" check correctly gated?
4. **Human gate auto-approve:** Does it use the same code path as real review?
5. **Scholar update consistency:** Concurrent intakes updating same scholar?
6. **Validation check ordering:** Does Check 5e auto-correction propagate to Check 6?

These should be verified during implementation and testing.

---

## After Session 6

**Next step:** Phase D (Test and Prove) — use `kr-evaluate` skill
- Run full test suite (5a deterministic + 5b LLM-worker + 5c independent review)
- Categorize all findings: CORE GAP / EXTENSION OPPORTUNITY / LESSON LEARNED
- Fix core gaps
- Document lessons in `engines/source/LESSONS.md`
- Owner sanity check on recognizable fixtures

Then: handoff to normalization engine (Phase E).
