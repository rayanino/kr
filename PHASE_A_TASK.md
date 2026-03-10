# Claude Code Task: Write `scripts/run_phase_a.py`

**Context:** Source engine validation Step 2. Run Steps 1–3 of the pipeline (format detection → extraction → hashing) on all 2,519 real Shamela books. No LLM calls. €0 cost.

**Read first:** `engines/source/CLAUDE.md`, `NEXT.md`, `engines/source/VALIDATION_PLAN.md`

---

## What the script does

Iterates every item in a given source directory. For each item (single `.htm` file or multi-volume directory): detects format, extracts metadata, computes SHA-256 hashes. Catches ALL exceptions per-item and produces structured output. No LLM inference, no staging locks, no freezing, no registration.

## CLI interface

```
python scripts/run_phase_a.py COLLECTION_DIR [--output-dir DIR] [--limit N] [--resume]
```

Arguments:
- `COLLECTION_DIR` (required, positional): Path to directory containing Shamela exports. Use `argparse`.
- `--output-dir` (optional): Output directory for results. Default: `tests/results/source_engine/phase_a/`
- `--limit N` (optional): Process only the first N items, for quick testing.
- `--resume` (optional): Skip items that already have a result JSON in the output directory. Mutually exclusive with the default behavior, which clears the output directory before starting.

The owner's full collection is at:
```
C:\Users\Rayane\Desktop\kr\shamela export samples
```

The directory contains 2,519 items: 1,932 single `.htm` files + 587 multi-volume directories (each containing numbered `.htm` files like `001.htm`, `002.htm`, plus optional `المقدمة.htm`).

## Functions to call (NOT `stage_source`)

Do NOT call `stage_source()` — it creates `.kr_processing` lock files in the source directory, which would pollute the owner's collection. Instead, call the lower-level functions directly:

1. **Format detection:** `engines.source.src.format_detection.detect_format(path)` → returns `SourceFormat` enum
2. **Metadata extraction:** `engines.source.src.extractors.extract_metadata(path, source_format)` → returns `dict[str, Any]`
3. **File collection and hashing:** Use the private `_collect_source_files` from staging.py (importing a private function in a test script is fine — this ensures hash consistency with the real pipeline). Then hash each file and compute the composite:

```python
from engines.source.src.staging import (
    compute_file_hash,
    compute_composite_hash,
    _collect_source_files,
)

files = _collect_source_files(source_path)
file_hashes = {f.name: compute_file_hash(f) for f in files}
composite_hash = compute_composite_hash(file_hashes)
```

**Why `_collect_source_files` and not a reimplementation:** It returns `[single_file]` for a file, or all non-hidden files sorted by name for a directory. If you reimplement this differently (e.g., only `.htm` files), composite hashes won't match what `stage_source` would produce, making duplicate detection unreliable.

The script must also track duplicates: build a `dict[str, list[str]]` mapping `composite_hash → [source_names]` across all processed items and report any hash with more than one source.

## Processing order per item

Run these three steps sequentially. Each step may fail independently. Capture whatever succeeds before recording the error:

```
source_format = None
file_hashes = None
composite_hash = None
extracted_metadata = None

1. detect_format(path)        → sets source_format, or records error and moves to next item
2. _collect_source_files + hash → sets file_hashes + composite_hash (can fail on I/O errors)
3. extract_metadata(path, fmt) → sets extracted_metadata (can fail on parsing errors)
```

Steps 2 and 3 are independent — extraction doesn't need hashes, hashing doesn't need metadata. If step 3 fails but step 2 succeeded, the per-book JSON should still include `file_hashes` and `composite_hash`. This ensures duplicate detection works even for books that fail extraction.

## Output structure

### Per-book JSON: `{output_dir}/{sanitized_name}.json`

On success:
```json
{
  "source_name": "أخبار أبي القاسم الزجاجي.htm",
  "source_path_relative": "أخبار أبي القاسم الزجاجي.htm",
  "status": "success",
  "source_format": "shamela_html",
  "composite_hash": "a1b2c3...",
  "file_hashes": {"أخبار أبي القاسم الزجاجي.htm": "d4e5f6..."},
  "extracted_metadata": { "...full extraction result dict as-is..." },
  "quality_issues": [],
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
  "source_format": "shamela_html",
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

**Partial progress on error:** Record whichever fields were successfully computed before the failure. If format detection succeeded but extraction failed, `source_format` should still be set (not null). If hashing completed but extraction failed, include the hashes. Only fields that were never computed should be null.

**`extracted_metadata`:** Store the FULL dict returned by `extract_metadata()`, including internal `_` prefixed keys (`_quality_issues`, `_field_source_*`, `_physical_page_count`, `_extra_card_fields`, etc.). These are valuable for debugging.

**`quality_issues`:** Pull from `extracted_metadata["format_specific_metadata"]["quality_issues"]` (the assembled output, not the internal `_quality_issues` key). This is what the real pipeline passes downstream. Default to empty list `[]` if the key is absent (many books have no quality issues).

### Filename sanitization

Arabic filenames can't be used directly as JSON output filenames on all systems. Sanitize by:
- Replace characters invalid in Windows filenames (`<>:"/\|?*`) with `_`
- Truncate to 200 characters max (before `.json` extension)
- On collision, append `_2`, `_3`, etc.
- Store the original name in `source_name` inside the JSON

### Summary: `{output_dir}/PHASE_A_SUMMARY.json`

```json
{
  "run_timestamp": "2026-03-10T...",
  "collection_path": "C:\\Users\\Rayane\\Desktop\\kr\\shamela export samples",
  "total_items": 2519,
  "processed": 2519,
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
    "muhaqiq_name_raw": {"count": 800, "pct": 32.0}
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

**`field_coverage` — DYNAMIC, not hardcoded.** For each successful extraction, iterate the result dict's top-level keys and count occurrences. Report all fields sorted by count descending. Exclude keys starting with `_` (internal) and `format_specific_metadata` (structural/always present). This ensures we discover any field the extractor produces, including ones we didn't anticipate. The numbers in the example above are illustrative placeholders.

## Critical requirements

0. **Deterministic item ordering.** Sort items from `collection_dir.iterdir()` by name before processing. This ensures `--limit N` and `--resume` are reproducible across runs, and that the output order is predictable for review.

1. **Zero uncaught exceptions.** Every possible failure must be caught and recorded as a structured error in the per-book JSON. The script must NEVER crash mid-run. Wrap EACH book's processing in its own `try/except`.

2. **Error codes from SPEC §7.** When catching `SourceEngineError`, use `exc.error.error_code.value`, `exc.error.severity.value`, `exc.error.message`, and `exc.error.context`. For truly unexpected exceptions (not `SourceEngineError`), record as `SRC_INTERNAL_ERROR` with the exception type, message, and traceback (first 500 chars) in context.

3. **Progress reporting.** Print progress every 100 books: `[100/2519] 98 ok, 2 errors (4.2s)`. Print a final one-line summary.

4. **No LLM calls.** The script must not import or call anything from `metadata_inference.py`, `consensus.py`, or any module that makes API calls.

5. **No filesystem side effects on the collection.** Do not create lock files, temp files, or any artifacts inside the collection directory. All output goes to the output directory only.

6. **Windows compatibility.** The script runs on Windows. Use `Path` objects throughout. Handle Arabic filenames in paths. Use `encoding="utf-8"` for all file reads/writes. Use `json.dumps(..., ensure_ascii=False)` to preserve Arabic in JSON output.

7. **Idempotent by default.** Without `--resume`: if the output directory exists, clear all `.json` files in it before starting. With `--resume`: keep existing result files and skip items whose sanitized name already has a result JSON present.

8. **`sys.path` setup.** Follow the pattern from `scripts/run_session6_integration.py`:
   ```python
   sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
   ```

## Testing before handoff

**Test A — fixture run:** Run the script on the existing fixtures:

```bash
python scripts/run_phase_a.py tests/fixtures/shamela_real --output-dir tests/results/source_engine/phase_a_fixtures
```

That directory contains **14 items**: 12 fixture directories + `MANIFEST.json` + `README.md`. Expected results:
- **12 items with `status: "success"`** (the 12 fixture directories)
- **2 items with `status: "error"`** and error code `SRC_UNSUPPORTED_FORMAT` (MANIFEST.json and README.md — not `.htm` files or Shamela directories)

Verify for the 12 successful fixtures:
- `extracted_metadata["title_full"]` matches `GROUND_TRUTH.json` title for each fixture
- `extracted_metadata["author_name_raw"]` is present for all except `10_no_author`
- `extracted_metadata["author_death_hijri"]` matches ground truth where present
- No `SRC_INTERNAL_ERROR` anywhere
- PHASE_A_SUMMARY.json shows `successful: 12, errors: 2`

**Test B — limit flag:** Run with `--limit 3` and verify only 3 items processed.

**Test C — resume flag:** Run with `--resume` after Test A and verify it skips all 14 items (0 new processed).

## Module imports needed

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engines.source.src.format_detection import detect_format
from engines.source.src.extractors import extract_metadata
from engines.source.src.staging import (
    compute_file_hash,
    compute_composite_hash,
    _collect_source_files,
)
from engines.source.src.exceptions import SourceEngineError
from engines.source.contracts import SourceFormat
```

## Edge cases to handle

- **Items that are neither `.htm` files nor directories:** Passed to `detect_format()` which raises `SRC_UNSUPPORTED_FORMAT`. Catch and record.
- **Empty directories:** Caught by `detect_format` as `SRC_EMPTY_INPUT`.
- **Non-UTF-8 files:** Caught by the extractor as `SRC_UNSUPPORTED_FORMAT`.
- **Very large files (20+ MB):** Should still work — hashing reads in 64KB chunks. May be slow. Timing data will show this.
- **Directories with only `المقدمة.htm` and no numbered files:** Valid edge case — `_detect_volumes` handles this.
- **Hidden files (`.` prefix) inside multi-volume directories:** Filtered by `_detect_volumes` in the extractor and by `_collect_source_files` for hashing.
- **Non-Shamela `.htm` files:** Would pass extension check but fail `_is_shamela_html` marker check → `SRC_UNSUPPORTED_FORMAT`.
- **PermissionError or OSError during file read:** Catch as `SRC_INTERNAL_ERROR` with the OS error message in context.

## What NOT to build

- No LLM inference
- No staging locks or TOCTOU protection
- No freezing or copying files
- No registry operations
- No scholar authority lookups
- No validation checks (those need LLM output)
- No human gate interactions
- No modifications to existing engine source code — the point of Phase A is to find bugs by running the code as-is
