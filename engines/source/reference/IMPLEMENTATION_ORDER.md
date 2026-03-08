# Source Engine — Implementation Order

Claude Code reads this to know what to build, in what order.
Each task specifies: what to build, which SPEC section, what it depends on, how to test it.

**Critical rule:** contracts.py is the schema authority. Every data structure MUST use
the Pydantic models defined there. Do not create parallel data structures.

**Critical rule:** SPEC.md is the behavioral authority. Every processing decision
references a specific SPEC section. When in doubt, read the SPEC.

**v1 scope:** The first format normalizer built depends on available test data.
The architecture is format-agnostic from day one — format-specific code is isolated
in extractor modules. See `engines/source/SPEC.md` §4.A.3 for supported formats.

---

## Phase 1: Foundation (no LLM, no external services)

### Task 1: Configuration Module
**File:** `engines/source/src/config.py`
**SPEC:** §8
**Depends on:** contracts.py (enums)
**Build:**
- SourceEngineConfig dataclass with all parameters from SPEC §8
- Default values and valid ranges as defined in the table
- Load from environment variables or config file (library/config/source_engine.yaml)
- Path configuration: staging_path, frozen base path, registry paths, log path
**Test:** Config loads with defaults. Config rejects out-of-range values.

### Task 2: Logger
**File:** `engines/source/src/logger.py`
**SPEC:** §7
**Depends on:** contracts.py (SourceError, ErrorCode, ErrorSeverity), config
**Build:**
- SourceEngineLogger class
- Append-only JSONL writer at library/logs/source_engine.jsonl
- Each log entry is a SourceError model serialized to JSON
- Alert thresholds: fatal errors, >10% same warning code, human gate queue > 20
**Test:** Log entries written and readable. Alert thresholds trigger correctly.

### Task 3: Freezer
**File:** `engines/source/src/freezer.py`
**SPEC:** §4.A.2 Step 6
**Depends on:** config (paths), logger
**Build:**
- `freeze_source(staging_path, source_id) → FreezeResult`
- Compute SHA-256 for each file in staging_path
- Copy all files to library/sources/{source_id}/frozen/
- Verify frozen hashes match staging hashes
- Set chmod 0444 on frozen files
- Staging lock file (.kr_processing) creation and removal
- TOCTOU protection: record file mtimes at format detection, verify at freeze
- Move processed staging to .processed/{source_id}/
- Return: frozen_path, frozen_hash (composite), frozen_file_hashes dict
**Test:** Successful freeze with hash verification. SRC_FREEZE_COPY_CORRUPT on mismatch.
SRC_FREEZE_PERMISSION_FAILED on chmod failure. SRC_STAGING_MODIFIED on file change.

### Task 4: Registry Infrastructure
**Files:** `engines/source/src/registries/__init__.py`, `*_registry.py`, `*_store.py`
**SPEC:** §3, §4.A.2 Step 7
**Depends on:** contracts.py (registry models), config, logger
**Build:**
- Base RegistryStore class with:
  - Atomic read/write via write-ahead log pattern
  - .bak file creation before each write
  - JSON parse failure → restore from .bak
  - Orphaned pending file detection on startup
  - Pydantic model validation before every write
- SourceRegistryStore(RegistryStore) for sources.json
- WorkRegistryStore(RegistryStore) for works.json
- ScholarRegistryStore(RegistryStore) for scholars.json
- RegistryTransaction class: prepare all changes → validate all → write-ahead → apply all → cleanup
**Test:** Atomic write succeeds. Interrupted write detected and recovered. Invalid data rejected.
.bak restoration works. Concurrent access handled via lock file.

### Task 5: Format Detector
**File:** `engines/source/src/format_detector.py`
**SPEC:** §4.A.2 Step 2
**Depends on:** contracts.py (SourceFormat), config, logger
**Build:**
- `detect_format(path) → SourceFormat`
- Detection rules in priority order:
  1. Directory with numbered .htm files → SHAMELA_HTML
  2. PDF magic bytes (%PDF-) → PDF_TEXT (default; PDF_SCANNED if no text extractable)
  3. JPEG/PNG/TIFF/HEIC files → IMAGE_SCAN
  4. .doc/.docx → WORD_DOC
  5. .epub → EPUB
  6. .txt → PLAIN_TEXT
  7. Single file with owner_authored type hint → OWNER_AUTHORED
  8. Unknown → SRC_UNSUPPORTED_FORMAT
- Record file modification timestamps (for TOCTOU protection in Task 3)
**Test:** Correct detection for each fixture. SRC_UNSUPPORTED_FORMAT for unknown. Empty → SRC_EMPTY_INPUT.

### Task 6: Deduplication
**File:** `engines/source/src/deduplication.py`
**SPEC:** §4.A.7
**Depends on:** registry infrastructure (source registry), config, logger
**Build:**
- `check_exact_duplicate(file_hashes) → Optional[source_id]`
  - Compare SHA-256 against all source registry entries
- `check_work_duplicate(work_id) → Optional[list[source_id]]`
  - Check if work_id already has sources
- Force flag support for re-acquisition
**Test:** Same file twice → SRC_DUPLICATE_EXACT. Different edition → SRC_DUPLICATE_WORK.
Different work → no match. Force flag bypasses.

---

## Phase 2: Shamela Intake (format-specific, no LLM yet)

### Task 7: Shamela Metadata Extractor
**File:** `engines/source/src/extractors/shamela.py`
**SPEC:** §4.A.3 (Shamela HTML extractor)
**Depends on:** contracts.py, logger
**Build:**
- `extract_shamela_metadata(path) → dict` (sparse metadata dict)
- Parse info.html: title from <h1>, author from المؤلف, muhaqiq from المحقق,
  publisher from الناشر
- Parse content files: page count from PageNumber spans, volume structure from file stems
- Preserve shamela_book_id and shamela_category in format_specific_metadata
- Missing info.html → SRC_FORMAT_STRUCTURE_MISSING, fall back to first PageText div
- Malformed info.html → warning, extract what's possible
**Test:** html_export_minimal fixture → title, author extracted.
Missing info.html → fallback extraction. format_specific_metadata populated.

---

## Phase 3: LLM Integration

### Task 8: LLM Client Abstraction
**File:** `engines/source/src/llm_client.py` (new — not in module stubs, add it)
**SPEC:** §6 (consensus), §4.A.4 (inference)
**Depends on:** config (API keys, model providers)
**Build:**
- LLMClient class wrapping Anthropic + OpenAI APIs
- Single-call method: `infer(prompt, system) → response`
- Consensus method: `consensus_infer(prompt, system) → (response, agreement, details)`
  - Calls two models independently
  - Compares structured outputs
  - Returns agreement status
- Timeout handling, retry logic
- Cost tracking (tokens used per call)
**Test:** Mock both APIs. Agreement → accepted. Disagreement → flagged.
One model timeout → appropriate fallback per decision type.

### Task 9: Metadata Inference Engine
**File:** `engines/source/src/metadata_inference.py`
**SPEC:** §4.A.4
**Depends on:** LLM client, contracts.py, scholar registry, work registry
**Build:**
- `infer_metadata(extracted_metadata, source_text_sample, toc, library_state) → InferredMetadata`
- Structured inference prompt requesting: genre, genre_chain, structural_format,
  multi_layer, source_authority, science_scope, level, author identification
- Confidence score extraction from LLM output
- Single-LLM biographical inference confidence cap at 0.85
- needs_review_fields computation (confidence < 0.70)
- Block signal for confidence < 0.50 on critical fields
**Test:** Mock LLM with deterministic responses for each fixture.
Confidence scores populated. needs_review computed correctly.

### Task 10: Multi-Model Consensus
**File:** `engines/source/src/consensus.py`
**SPEC:** §6
**Depends on:** LLM client, contracts.py
**Build:**
- `consensus_author_id(metadata, scholar_registry) → (canonical_id, confidence, agreed)`
- `consensus_work_match(metadata, work_registry) → (work_id, confidence, agreed)`
- Author ID: disagreement → human gate (never single-model fallback)
- Work match: one model failure → accept single + needs_review
**Test:** Both agree → accept. Disagree on author → human gate.
One fails on work → accept with flag.

---

## Phase 4: Scholar and Work Identity

### Task 11: Scholar Authority Manager
**File:** `engines/source/src/scholar_authority.py`
**SPEC:** §4.A.5
**Depends on:** scholar registry store, LLM client, contracts.py, logger
**Build:**
- `find_or_create_scholar(name, metadata_hints) → ScholarAuthorityRecord`
- Name matching: normalize (strip diacritics, normalize hamza/taa marbuta),
  compare against all name_variants
- Match scoring: name + death date + school + known works
- Thresholds: >= 0.85 auto-link, 0.50-0.85 human gate, < 0.50 new record
- Progressive enrichment: check if new source adds unknown info
- Consistency checks (5 checks from §4.A.5):
  death date drift, school change, name immutability, self-reference, temporal
- record_completeness computation
**Test:** New scholar creation. Matching existing scholar. Variant name matching.
Ambiguous name → human gate. All 5 consistency checks.

### Task 12: Work Identity Manager
**File:** `engines/source/src/work_registry.py`
**SPEC:** §4.A.1, §4.A.9
**Depends on:** work registry store, scholar authority manager, contracts.py, logger
**Build:**
- `find_or_create_work(title, author_id, metadata) → WorkRegistryEntry`
- Work matching: normalized title + author canonical_id
- Thresholds: same as scholar matching
- work_id generation: wrk_{author_slug}_{title_slug}
- Placeholder works: status="referenced_not_acquired"
- `record_relationship(from_work, to_work, type, confidence)`
- Volume tracking: volumes_present, volumes_missing
**Test:** New work creation. Existing work linking. Uncertain match → human gate.
Placeholder creation. Relationship recording. Volume gap detection.

---

## Phase 5: Trust and Validation

### Task 13: Trustworthiness Evaluator
**File:** `engines/source/src/trust_evaluator.py`
**SPEC:** §4.A.8
**Depends on:** scholar registry, config (recognized muhaqiqs), contracts.py
**Build:**
- `evaluate_trust(metadata) → (TrustTier, float, list[TrustworthinessFactor], str)`
- Five factors with weights as defined in SPEC
- Recognized muhaqiq list from config
- Special cases: owner-authored, Quran, canonical hadith
- Conservative bias: uncertain → flagged
- Owner-authored validation (3 checks from SPEC)
**Test:** Classical work → verified. Unknown modern → flagged. Factor weights sum to 1.0.
Owner-authored → verified. Recognized muhaqiq scoring.

### Task 14: Human Gate Manager
**File:** `engines/source/src/human_gate.py`
**SPEC:** §5 Layer 2
**Depends on:** contracts.py (HumanGateCheckpoint), config, logger
**Build:**
- `create_checkpoint(source_id, trigger, detail, fields, values, alternatives) → checkpoint_id`
- Store checkpoints at library/human_gates/{source_id}/ as JSON
- Batch retrieval: all pending checkpoints for a source
- Resolution: mark as resolved with owner's decision
- Queue monitoring: count pending, alert if > configured threshold
**Test:** Checkpoint creation, retrieval, resolution. Queue counting. Batch retrieval.

### Task 15: Self-Validation (Layer 1)
**File:** `engines/source/src/validation.py` (new)
**SPEC:** §5 Layer 1
**Depends on:** contracts.py, all registry stores
**Build:**
- `validate_metadata_record(metadata) → list[ValidationError]`
- 5 checks:
  1. Schema compliance (Pydantic validation)
  2. Referential integrity (author → scholars.json, work → works.json)
  3. Confidence threshold (critical fields < 0.50 → block)
  4. Duplicate re-check (after inference)
  5. Consistency cross-check (genre vs format, level vs genre)
- Returns list of errors; empty list = valid
**Test:** Valid record passes. Missing reference fails. Low confidence blocks.
Inconsistent genre/format flagged.

---

## Phase 6: Enrichment

### Task 16: Enrichment Handler
**File:** `engines/source/src/enrichment.py`
**SPEC:** §2 enrichment invariants
**Depends on:** contracts.py (EnrichmentRequest), all registry stores, validation, human gate, logger
**Build:**
- `apply_enrichment(request) → EnrichmentResult`
- Check all 7 invariants before applying
- Critical field gate: author, work_id, genre, science_scope → human gate
- History preservation: record old value, engine, timestamp
- Stale-marking cascade trigger for high-impact changes
**Test:** Valid enrichment applied. Each invariant violation rejected individually.
Critical field gate triggers human gate. History preserved.

---

## Phase 7: Main Orchestrator

### Task 17: Acquisition Workflow Orchestrator
**File:** `engines/source/src/engine.py`
**SPEC:** §4.A.2 (all 9 steps)
**Depends on:** ALL previous tasks
**Build:**
- `acquire_source(staging_path, owner_hints=None) → SourceMetadata`
- Orchestrates all 9 steps in sequence
- Handles partial failures: if inference fails, still freeze and register with partial metadata
- Status tracking: update processing status at each step
- Returns completed SourceMetadata or raises with structured error
**Test:** Full end-to-end intake for html_export_minimal fixture.
Partial failure handling. Status transitions logged.

---

## Phase 8: §4.B Transformative Capabilities

### Task 18: OpenITI Enrichment
**File:** `engines/source/src/openiti_enrichment.py` (new)
**SPEC:** §4.B.1
**Depends on:** scholar authority manager, config (openiti_metadata_path)
**Build:** Query local OpenITI metadata CSV for scholar matches. Enrich death dates, known works.
**Test:** Match found → scholar record enriched. No match → graceful skip.

### Task 19: Citation Discovery Handler
**File:** `engines/source/src/citation_discovery.py` (new)
**SPEC:** §4.B.3
**Depends on:** work registry, source registry
**Build:** Process CitationDiscoveryRequest. Three outcomes: work exists, placeholder exists, new placeholder.
**Test:** Each outcome tested. Citation count incremented.

### Task 20: Gap Analysis
**File:** `engines/source/src/gap_analysis.py` (new)
**SPEC:** §4.B.4
**Depends on:** all registries, LLM client, config
**Build:** Compute ranked acquisition priority list.
**Test:** Gap detection for missing school coverage, curricular gaps.

---

## Implementation Notes for Claude Code

1. **Start with Tasks 1-6** (Foundation). These have no LLM dependency and can be fully tested.
2. **Task 7** (Shamela extractor) enables the first end-to-end test with html_export_minimal.
3. **Tasks 8-10** require API keys. Mock for unit tests; live for integration tests.
4. **Each task should produce:** implementation code + unit tests + passing test run.
5. **After Task 17 passes:** run the full intake on html_export_minimal as the first gold baseline.
6. **contracts.py is read-only for Claude Code.** If a model needs changing, flag it as a SPEC issue.
7. **Use the ABD code in engines/source/src/ (backup) as reference** for Shamela HTML parsing patterns,
   but do NOT copy its architecture. The SPEC defines the new architecture.
