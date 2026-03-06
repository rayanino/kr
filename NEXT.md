# NEXT SESSION

## Session Type
IMPLEMENTATION (see SESSION_TYPES.md for full framework)

## Immediate Task

**Build the source engine foundation (Tasks 1-7 from IMPLEMENTATION_ORDER.md).**

These tasks have zero LLM dependency and can be fully tested with local fixtures. They produce the core infrastructure that everything else depends on.

## What to Read

1. `engines/source/IMPLEMENTATION_ORDER.md` — the build sequence. Follow it exactly.
2. `engines/source/contracts.py` — the schema authority. Every data structure uses these models.
3. `engines/source/SPEC.md` — the behavioral authority. Reference specific sections per task.
4. `engines/source/TEST_PLAN.md` — what tests to write for each task.
5. `tests/fixtures/` — test data. Start with `html_export_minimal/` (synthetic, predictable).
6. `engines/source/DEPENDENCIES.md` — what's installed, what needs installing.

**Do NOT read:** VISION.md, other engine SPECs, CREATIVE_MANDATE.md.

**Budget:** Focus 100% on Tasks 1-7. If time remains, start Task 8 (LLM client abstraction).

## The Implementation Work

Follow IMPLEMENTATION_ORDER.md Tasks 1-7 in sequence:

1. **Config** → dataclass with SPEC §8 parameters
2. **Logger** → append-only JSONL writer using SourceError model
3. **Freezer** → SHA-256 hashing, file copy, read-only, TOCTOU protection
4. **Registry infrastructure** → atomic read/write, write-ahead log, .bak files
5. **Format detector** → identify source type from file structure
6. **Deduplication** → exact hash match + work-level matching
7. **Shamela extractor** → parse info.html + content HTML for metadata

**After completing Task 7:** run end-to-end test with html_export_minimal fixture:
- Detect format → extract metadata → freeze → register
- This validates the foundation works before adding LLM integration.

## Definition of Done

1. Tasks 1-7 implemented with passing tests
2. Each task has unit tests covering the cases in TEST_PLAN.md
3. End-to-end test: html_export_minimal → format detected → metadata extracted → frozen → registered
4. All tests pass: `pytest engines/source/tests/ -v`
5. No regression: `python3 scripts/check_spec_quality.py engines/source/SPEC.md` still ≤4 HIGH
6. NEXT.md written for next session (Tasks 8-17: LLM integration + full orchestrator)
7. SESSION_LOG.md updated
8. Committed and pushed

## What the Previous Session Did

IMPLEMENTATION_PREP session (2026-03-06):

Changes:
- **contracts.py fully rewritten** — 20+ misalignments with SPEC fixed:
  - Added 7 new enums (TextFidelity, ProcessingStatus, AcquisitionPath, ErrorCode, ErrorSeverity, HumanGateTrigger, GenreRelationType values fixed)
  - Added OWNER_OVERRIDE to TrustTier
  - Changed muhaqiq from str to ScholarReference
  - Added InferredFieldConfidence model for confidence tracking
  - Added 9 new workflow models (EnrichmentRequest, HumanGateCheckpoint, WorkRelationshipEdge, SourceError, RegistryPendingWrite, CitationDiscoveryRequest, RelevanceEvaluation, GapAnalysisItem, GenreChain.confidence)
  - Fixed StructuralFormat values, WorkRegistryEntry.genre type, added human_label to SourceRegistryEntry
  - Added format_specific_metadata, page_count, needs_review_fields to SourceMetadata
- **Directory skeleton created** — 15 module stubs with SPEC-referencing docstrings
- **TEST_PLAN.md** — 15 test sections, 90+ test cases mapped to fixtures
- **DEPENDENCIES.md** — all external dependencies verified
- **IMPLEMENTATION_ORDER.md** — 20 tasks in dependency order with build+test instructions

## Pending Owner Questions

- **API keys:** Will be needed for Tasks 8-10 (LLM integration). Not needed for Tasks 1-7. The owner should prepare: Anthropic API key, OpenAI API key (for multi-model consensus), and optionally Google Document AI credentials (for Arabic OCR on photo scans).
