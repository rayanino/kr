# Source Engine — External Dependencies Verification

**Verified:** 2026-03-06 (IMPLEMENTATION_PREP session)
**Python:** 3.12.3
**pip:** 24.0

## Dependency Status

### Required for v1

| Dependency | Version | Status | Notes |
|-----------|---------|--------|-------|
| pydantic | 2.12.5 | ✅ Installed | Runtime validation of all contracts |
| hashlib | stdlib | ✅ Available | SHA-256 for freezing and deduplication |
| json | stdlib | ✅ Available | Registry file I/O |
| pathlib | stdlib | ✅ Available | File path management |
| difflib | stdlib | ✅ Available | Edition comparison (§4.B.6) |
| networkx | 3.6.1 | ✅ Installed | Scholarly genealogy graph (§4.B.7) |
| pytest | TBD | ⬜ Install at test time | Test framework |

### Required for non-Shamela formats

| Dependency | Version | Status | Notes |
|-----------|---------|--------|-------|
| docling | 2.77.0 | ⬜ Installable | PDF, Word doc, image parsing. ~500MB install. Install when needed. |
| camel-tools | 1.5.7 | ⬜ Installable | Arabic text normalization for name matching. Requires Rust compiler. |
| openiti | 0.1.6 | ⬜ Installable | OpenITI metadata for §4.B.1 enrichment |

### Required for LLM inference

| Dependency | Status | Notes |
|-----------|--------|-------|
| anthropic SDK | ⬜ Install at implementation | Claude API for metadata inference |
| openai SDK | ⬜ Install at implementation | GPT API for multi-model consensus |
| httpx or requests | ⬜ As needed | OpenRouter API fallback |

### External data files

| Resource | Size | Status | Notes |
|---------|------|--------|-------|
| OpenITI metadata CSV | ~50MB | ⬜ Download needed | Scholar authority bootstrapping (§4.B.1) |
| KITAB statistics CSV | ~1GB | ⬜ Download needed | Compositional profiling (§4.B.5) |
| Usul.ai authors.json | ~10MB | ⬜ Download needed | Scholar enrichment (MIT license) |

### API keys needed (for IMPLEMENTATION session)

| Service | Purpose | Status |
|---------|---------|--------|
| Anthropic API | Primary LLM for metadata inference | ⬜ Owner to provide |
| OpenAI API | Second LLM for multi-model consensus | ⬜ Owner to provide |
| Google Document AI | Arabic OCR for iPhone photos (optional) | ⬜ Optional |

## Installation Order

For v1 (Shamela-only implementation):
```bash
pip install pydantic pytest --break-system-packages
# networkx already installed
# anthropic + openai SDKs when API keys available
```

For multi-format support:
```bash
pip install docling camel-tools openiti --break-system-packages
```

## Fixture Verification

All 7 fixtures present and readable:
- waraqat_usul/waraqat.pdf ✅
- ibn_aqil_alfiyyah/vol6-9.pdf ✅
- mughni_comparative/mughni_docs.zip + .doc files ✅ (CP1256 encoding confirmed)
- alfiyyah_versified/alfiyyah.txt ✅
- photo_scan_ilm/page1-5.jpg ✅
- owner_note/study_note.txt ✅
- html_export_minimal/info.html + content.html ✅
