# NEXT SESSION

## Session Type
IMPLEMENTATION

## Critical Context

The project has completed 9 sessions of architecture and governance. 0 lines of engine code exist.
The source engine SPEC and normalization engine SPEC are comprehensive. Machine-readable contracts
exist for both engines. Real test data exists (7 fixture sets). The time for planning is over.

## Immediate Task

**Build the source engine foundation — intake, freeze, and metadata for ONE format.**

Target: Given a PDF from `tests/fixtures/waraqat_usul/waraqat.pdf`, the source engine should:
1. Detect format (PDF)
2. Extract basic metadata (title, author from PDF properties + first pages)
3. Freeze the file to `library/sources/{source_id}/frozen/`
4. Compute SHA-256 hash
5. Write a metadata.json conforming to `engines/source/contracts.py::SourceMetadata`
6. Register in source registry

This is the simplest end-to-end path. No LLM inference, no consensus, no scholar authority model yet.
Just: file in → frozen file + metadata.json out.

## Definition of Done

1. `python -m pytest engines/source/tests/ -v` passes with ≥5 tests
2. Running intake on `tests/fixtures/waraqat_usul/waraqat.pdf` produces:
   - `library/sources/src_{hash}/frozen/waraqat.pdf` (read-only, SHA-256 verified)
   - `library/sources/src_{hash}/metadata.json` (validates against SourceMetadata model)
   - Updated `library/registries/sources.json`
3. Running intake on the same PDF a second time → rejected with `SRC_DUPLICATE_EXACT`
4. All output validates against Pydantic models in `engines/source/contracts.py`

## Files to Read — IN THIS ORDER

1. `STEERING.md` (~80 lines) — project context
2. `engines/source/contracts.py` (~350 lines) — THE data models. Build to these.
3. `engines/source/SPEC.md` §4.A.1 (Identity Model), §4.A.2 (Acquisition Workflow), §4.A.3 (Format-Specific Extraction) — the behavioral rules
4. `tests/fixtures/README.md` (~80 lines) — what test data exists
5. `reference/RESOURCES.md` §Document Processing — Docling for PDF parsing
6. `.claude/skills/arabic-text/SKILL.md` — Arabic text handling rules

**Total: ~15K tokens. Budget remaining: ~155K tokens for building.**

## Files to NOT Read

VISION.md, DOMAIN.md, kr_decisions.md, CREATIVE_MANDATE.md, SPEC_REFINEMENT.md,
SILENT_FAILURES.md, CHALLENGE_PROTOCOL.md, REVIEW_PROTOCOL.md, CONTEXT_BUDGET.md,
other engine SPECs, governance docs. This is a BUILD session.

## Architecture Decisions for This Task

- **Identity model:** `source_id = src_{first_8_chars_of_sha256_hash}`. Example: `src_a3f2b1c4`
- **Work ID:** Skip work matching for now. Set `work_id = wrk_{title_slug}` using transliterated title.
- **Scholar authority:** Skip for now. Set `author.canonical_id = "sch_unresolved"` with confidence 0.0.
- **LLM inference:** Skip for now. Extract only what the format provides. Flag everything else as `needs_review`.
- **Trust evaluation:** Skip for now. Set `trust_tier = "flagged"` with reason "trust evaluation not yet implemented".
- **Registries:** Simple JSON files. No concurrent access handling needed (single user).

These are NOT design compromises — they're the correct implementation order. The identity model, freezing,
and schema validation are the foundation. LLM inference, consensus, and scholar authority layer on top.

## Implementation Plan

```
engines/source/src/
├── __init__.py          # Keep empty for now
├── intake.py            # Main intake function: accept file path → produce metadata + frozen copy
├── format_detector.py   # Detect source format from file extension + content inspection
├── extractors/
│   ├── __init__.py
│   ├── base.py          # Abstract base extractor interface
│   ├── pdf_extractor.py # PDF metadata extraction using Docling or PyMuPDF
│   └── text_extractor.py # Plain text metadata extraction
├── freezer.py           # Copy to frozen dir, set read-only, compute hashes
├── registry.py          # Source registry read/write (JSON on disk)
└── identity.py          # Generate source_id, work_id from metadata + hash

engines/source/tests/
├── __init__.py
├── test_intake.py       # End-to-end intake tests using real fixtures
├── test_freezer.py      # Freeze + hash tests
├── test_format_detector.py # Format detection tests
└── conftest.py          # Pytest fixtures for test data paths
```

## Dependencies to Install

```bash
pip install docling pydantic python-dotenv --break-system-packages
```

If Docling is too heavy for initial work, use PyMuPDF (`pip install pymupdf`) for basic PDF text/metadata
extraction. Docling can be added later for advanced PDF understanding.

## What the ABD Code Does (Reference Only — D-019)

The ABD code in `reference/archive/abd_code/source/intake.py` (1476 lines) handles Shamela HTML only.
It has working: book ID validation, SHA-256 hashing, duplicate detection, file freezing, metadata card parsing.
The DESIGN has zero authority (D-019), but the CODE has useful patterns: hash computation, file copying,
registry serialization. Use it as a pattern reference, not as code to port.

## What Last Session Did

Session 9 (Claude Chat): Technology survey (Docling, CAMeL Tools, Arabic embeddings, OpenITI all confirmed
active). Fixed contracts.py mismatches (added WORD_DOC format, WorkLevel, GenreRelationType expansions,
ScholarAuthorityRecord, WorkRegistryEntry, SourceRegistryEntry models). Created normalization engine
contracts.py (ContentUnit, NormalizedManifest, NormalizedPackage — the normalization boundary schema).
Updated RESOURCES.md with 2026 survey findings. Fixed field naming inconsistency (source_type → source_format
in normalization SPEC). Added Word document support to both SPECs.

## Decisions Made

- Source SPEC now includes Word document (.doc/.docx) format support
- Normalization SPEC field `source_type` renamed to `source_format` (matching contracts.py)
- Swan-Large recommended as primary Arabic embedding model (RESOURCES.md updated)
- GenreRelationType expanded with taqrirat, responds_to, cites (matching SPEC §4.A.9)
