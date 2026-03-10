# Claude Code Task: Write `scripts/run_phase_a.py`

**Context:** Source engine validation Step 2. Run Steps 1–3 of the pipeline (format detection → extraction → hashing) on all 2,519 real Shamela books. No LLM calls. €0 cost.

**Read first:** `engines/source/CLAUDE.md`, `NEXT.md`, `engines/source/VALIDATION_PLAN.md`

---

## What the script does

Iterates every item in the owner's Shamela collection directory. For each item (single `.htm` file or multi-volume directory): detects format, extracts metadata, computes SHA-256 hashes. Catches ALL exceptions and produces structured output. No LLM inference, no staging locks, no freezing, no registration.

## Collection location

```
C:\Users\Rayane\Desktop\kr\shamela export samples
```

The script takes this as a **command-line argument** (not hardcoded):

```bash
python scripts/run_phase_a.py "C:\Users\Rayane\Desktop\kr\shamela export samples"
```

The directory contains 2,519 items: 1,932 single `.htm` files + 587 multi-volume directories (each containing numbered `.htm` files like `001.htm`, `002.htm`, plus optional `المقدمة.htm`).

## Functions to call (NOT `stage_source`)

Do NOT call `stage_source()` — it creates `.kr_processing` lock files in the source directory, which would pollute the owner's collection. Instead, call the lower-level functions directly:

1. **Format detection:** `engines.source.src.format_detection.detect_format(path)` → returns `SourceFormat` enum
2. **Metadata extraction:** `engines.source.src.extractors.extract_metadata(path, source_format)` → returns `dict[str, Any]`
3. **Hashing:** For each source file, call `engines.source.src.staging.compute_file_hash(file_path)`, then `compute_composite_hash(file_hashes_dict)`

The script must also track duplicates: build a `dict[str, list[str]]` mapping `composite_hash → [source_names]` and report any hash with more than one source.

## Output structure

### Per-book JSON: `tests/results/source_engine/phase_a/{sanitized_name}.json`

```json
{
  "source_name": "أخبار أبي القاسم الزجاجي.htm",
  "source_path_relative": "أخبار أبي القاسم الزجاجي.htm",
  "status": "success",
  "source_format": "shamela_html",
  "composite_hash": "a1b2c3...",
  "file_hashes": {"أخبار أبي القاسم الزجاجي.htm": "d4e5f6..."},
  "extracted_metadata": { ... },
  "quality_issues": [...],
  "processing_time_ms": 42,
  "error": null
}
```

On error:
```json
{
  "source_name": "بعض الكتاب.htm",
  "source_path_relative": "بعض الكتاب.htm",
  "status": "error",
  "source_format": null,
  "composite_hash": null,
  "file_hashes": null,
  "extracted_metadata": null,
  "quality_issues": null,
  "processing_time_ms": 3,
  "error": {
    "error_code": "SRC_FORMAT_STRUCTURE_MISSING",
    "severity": "fatal",
    "message": "No PageText div found ...",
    "context": {}
  }
}
```

### Filename sanitization

Arabic filenames can't be used directly as JSON output filenames on all systems. Sanitize by:
- Replace characters invalid in Windows filenames (`<>:"/\|?*`) with `_`
- Truncate to 200 characters max (before `.json` extension)
- On collision, append `_2`, `_3`, etc.
- Store the original name in `source_name` inside the JSON

### Summary: `tests/results/source_engine/phase_a/PHASE_A_SUMMARY.json`

```json
{
  "run_timestamp": "2026-03-10T...",
  "collection_path": "C:\\Users\\Rayane\\Desktop\\kr\\shamela export samples",
  "total_items": 2519,
  "successful": 2450,
  "errors": 69,
  "errors_by_code": {
    "SRC_FORMAT_STRUCTURE_MISSING": 5,
    "SRC_UNSUPPORTED_FORMAT": 12,
    "SRC_EMPTY_INPUT": 2,
    "SRC_INTERNAL_ERROR": 50
  },
  "format_counts": {
    "shamela_html": 2500,
    "plain_text": 0
  },
  "field_coverage": {
    "title_full": {"count": 2400, "pct": 96.0},
    "author_name_raw": {"count": 2350, "pct": 94.0},
    "muhaqiq_name_raw": {"count": 800, "pct": 32.0},
    "publisher": {"count": 2100, "pct": 84.0},
    "edition_raw": {"count": 1800, "pct": 72.0},
    "shamela_category": {"count": 2450, "pct": 98.0},
    "author_death_hijri": {"count": 1900, "pct": 76.0}
  },
  "multi_volume_count": 587,
  "single_file_count": 1932,
  "duplicate_groups": [
    {"hash": "abc123...", "sources": ["book_a.htm", "book_b.htm"]}
  ],
  "quality_issue_counts": {
    "content_minimal": 50,
    "page_count_mismatch": 30,
    "encoding_suspect": 0,
    "high_empty_ratio": 10,
    "truncation_with_mismatch": 5
  },
  "timing": {
    "total_seconds": 120.5,
    "avg_per_book_ms": 47.8,
    "slowest_book": {"name": "...", "ms": 3200}
  }
}
```

## Critical requirements

1. **Zero uncaught exceptions.** Every possible failure must be caught and recorded as a structured error in the per-book JSON. The script must NEVER crash mid-run — losing 1,000 results because book #1,501 hit an unexpected exception is unacceptable. Wrap EACH book's processing in its own try/except.

2. **Error codes from SPEC §7.** Use `SourceEngineError.error` attributes when catching `SourceEngineError`. For truly unexpected exceptions (not `SourceEngineError`), record as `SRC_INTERNAL_ERROR` with the exception type and message in context.

3. **Progress reporting.** Print progress every 100 books: `[100/2519] 98 ok, 2 errors (4.2s)`. Print a final summary line.

4. **No LLM calls.** The script must not import or call anything from `metadata_inference.py`, `consensus.py`, or any module that makes API calls.

5. **No filesystem side effects on the collection.** Do not create lock files, temp files, or any artifacts inside the collection directory. All output goes to `tests/results/source_engine/phase_a/`.

6. **Windows compatibility.** The script runs on Windows. Use `Path` objects throughout. Handle Arabic filenames in paths. Use `encoding="utf-8"` for all file reads/writes. Be careful with path separators.

7. **Idempotent.** If the output directory exists, clear it before starting (or overwrite). The script should be safe to re-run.

8. **Resume support (optional but nice).** If `--resume` flag is passed, skip books that already have a result JSON in the output directory. This helps if the script is interrupted mid-run.

## Testing before handoff

Run the script on the 12 existing fixtures in `tests/fixtures/shamela_real/` first:

```bash
python scripts/run_phase_a.py tests/fixtures/shamela_real --output-dir tests/results/source_engine/phase_a_fixtures
```

Verify:
- 12/12 produce `status: "success"`
- Extracted metadata matches GROUND_TRUTH.json for key fields (title_full, author_name_raw, author_death_hijri)
- No crashes, no uncaught exceptions

Also add a `--limit N` flag for testing: process only the first N items.

## Module imports needed

```python
from engines.source.src.format_detection import detect_format
from engines.source.src.extractors import extract_metadata
from engines.source.src.staging import compute_file_hash, compute_composite_hash
from engines.source.src.exceptions import SourceEngineError
from engines.source.contracts import SourceFormat
```

## Edge cases to handle

- **Items that are neither `.htm` files nor directories:** Skip with a warning (e.g., `.DS_Store`, `Thumbs.db`, desktop.ini). Record as `SRC_UNSUPPORTED_FORMAT`.
- **Empty directories:** Will be caught by `detect_format` as `SRC_EMPTY_INPUT`.
- **Non-UTF-8 files:** Will be caught by the extractor as `SRC_UNSUPPORTED_FORMAT`.
- **Very large files (20+ MB):** Should still work — hashing reads in 64KB chunks, extraction parses the full HTML. May be slow. The timing data will show this.
- **Directories with only `المقدمة.htm` and no numbered files:** Valid edge case — should detect as single-volume Shamela.
- **Hidden files (`.` prefix) inside multi-volume directories:** Already filtered by `_detect_volumes` in the extractor.

## What NOT to build

- No LLM inference
- No staging locks or TOCTOU protection
- No freezing or copying files
- No registry operations
- No scholar authority lookups
- No validation checks (those need LLM output)
- No human gate interactions
