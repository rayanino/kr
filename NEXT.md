# NEXT — Session 6: Validation + Writer + Plain Text Normalizer + Dispatcher Wiring

## Current position: Normalization engine build Session 6 of 7. Sessions 1-5 ✅ ACCEPTED (commit f8255e2). 256 tests passing, 22 skipped. Shamela normalize() returns NormalizedPackage end-to-end. This session adds the validation layer, disk writer, plain text normalizer, and dispatcher registry population.

## What to do: Implement §5 validation checks 1-8 + check 10, the atomic disk writer, the plain text normalizer (§4.A.4c), and wire the dispatcher registry. This makes the normalization engine a complete, callable system for two source formats.

## Context: The Shamela normalizer produces a NormalizedPackage but it is not yet validated or written to disk. The validation checks (§5) catch internal inconsistencies that would silently corrupt downstream engines. The writer atomically commits the package to disk. The plain text normalizer handles .txt files. The dispatcher routes source_format to the correct normalizer. After this session, `normalize_source()` returns a validated package, and `normalize_and_write()` validates + writes atomically.

## Owner action needed: NO — start new CC session. CC reads this file.

## Git range for review: from `f8255e2` to HEAD after build.

---

## Read First

Read these files in this exact order before writing any code.

1. `engines/normalization/CLAUDE.md` (109L) — Module orientation, build plan, critical rules.
2. `engines/normalization/SPEC.md` lines 1466–1510 — §5 validation checks 1-10. **Copy-paste every threshold.**
3. `engines/normalization/SPEC.md` lines 233–239 — Atomic write procedure + interrupted write recovery.
4. `engines/normalization/SPEC.md` lines 462–476 — §4.A.4c plain text normalizer behavioral outline.
5. `engines/normalization/src/validation.py` (101L) — Stub with all check function signatures.
6. `engines/normalization/src/writer.py` (45L) — Stub with write function signature.
7. `engines/normalization/src/dispatcher.py` (67L) — Current dispatcher, needs registry population.
8. `engines/normalization/contracts.py` (726L) — All output schema models. Focus on: `NormalizedPackage`, `ContentUnit`, `NormalizedManifest`, `BoundaryContinuity`, `BoundaryContinuityType`.
9. `engines/normalization/src/errors.py` (130L) — All error codes already defined.
10. `engines/normalization/src/normalizers/base.py` (57L) — `BaseNormalizer` interface: `normalize()` + `validate_input()`.
11. `engines/normalization/src/normalizers/shamela.py` lines 1047–1240 — `_pass6_assemble` method (current assembly without validation/write).
12. `engines/normalization/tests/conftest.py` (189L) — Shared test helpers: `_make_source_metadata()`, `_make_cleaned_page()`, `_full_pipeline()`, `_wrap_page()`, `_make_html()`, `_assert_full_coverage()`.
13. `engines/normalization/tests/test_kr_output.py` (158L) — 22 skipped tests to unskip as validation/writer/dispatcher come online.
14. `engines/source/contracts.py` lines 46–55 — `SourceFormat` enum values (SHAMELA_HTML, PLAIN_TEXT, etc.).
15. `engines/normalization/src/structure_discovery.py` lines 99–106 and 1144–1158 — `StructureResult` dataclass and `discover_structure()` signature. Plain text normalizer calls this.
16. `engines/normalization/src/content_flagger.py` line 131 — `compute_content_flags(page, is_toc_page)` signature. Plain text normalizer calls this.
17. `engines/normalization/src/boundary_continuity.py` lines 201–211 — `classify_boundary()` signature. Plain text normalizer calls this.
18. `reference/SPEC_ADVERSARY_NORMALIZATION.md` — Read the ADV cases listed in the ADV Coverage section below.

---

## What to Build

### 1. `src/validation.py` — §5 Layer 1 Validation Checks (checks 1-8, 10)

Replace the stub. Implement `validate_package()` which calls individual check functions and aggregates results. Check 9 (format-specific input validation) is already in each normalizer's `validate_input()` — do NOT re-implement it here.

**`validate_package(package: NormalizedPackage, metadata: SourceMetadata) -> ValidationResult`**

Calls checks 1-7 and 10 sequentially. Any fatal error stops processing (no point running further checks). Warnings accumulate. Returns the ValidationResult with `passed`, `warnings`, `fatal_errors`.

Individual checks — implement EXACTLY per SPEC §5 lines 1472-1505:

**Check 1 — Schema compliance (SPEC line 1472):**
- Call `model_validate()` on the manifest and each content unit (Pydantic re-validation).
- Verify `manifest.total_content_units == len(package.content_units)`. ADV-033: if mismatch, `NORM_SCHEMA_VIOLATION` (fatal).
- Fatal on any schema violation.

**Check 2 — Coverage check (SPEC line 1474):**
- Loose check: `abs(len(content_units) - metadata.page_count) / metadata.page_count > 0.10` → `NORM_PAGE_COUNT_MISMATCH` (warning).
- Handle: `metadata.page_count` may be None or 0 — skip check if so.
- ADV-028: 89 units from 100 expected → 11% → triggers warning. 91/100 → 9% → no warning. Exactly 90/100 = 10% → no warning (> not >=).
- NOTE: The tight check (exact match for Shamela) is handled inside the normalizer (see Design Decision D6-8). validate_package only runs the loose check.

**Check 3 — Text extraction verification (SPEC lines 1476-1480):**
For each content unit (skip `is_blank` pages via `content_flags.is_blank`):
- `primary_text` must be non-empty. Empty text on a non-blank page → `NORM_SCHEMA_VIOLATION` (fatal).
- Arabic character ratio: count Arabic Unicode chars (U+0600-U+06FF, U+0750-U+077F, U+FB50-U+FDFF, U+FE70-U+FEFF) and divide by total non-whitespace-non-punctuation chars. Threshold: `>= 0.70` passes, `< 0.70` flags as potentially corrupted (warning per page, not fatal). ADV-025: exactly 70% → passes.
- Identical character runs: scan for runs of `> 20` identical characters using regex `r'(.)\1{20,}'` → warning per page. ADV-029: exactly 20 → no flag. 21 → flag.
- Mojibake detection: scan for 3+ consecutive characters from `[\u00c0-\u00ff]` (Latin Extended block) → warning per page. See D6-9.

**Check 4 — Layer consistency (SPEC lines 1482-1486):**
For multi-layer sources only (check `metadata.is_multi_layer`):
- Every character in `primary_text` is covered by exactly one `text_layers` segment. Verify: first segment starts at 0, last segment ends at len(primary_text), no gaps between consecutive segments. Fatal if coverage violation found.
- Layer proportions: Calculate matn ratio = total matn chars / total chars across all pages. If matn ratio >= 0.40 AND genre is sharh/hashiyah, warning.
- Layer transitions: count transitions where `segments[i].layer_type != segments[i-1].layer_type` on each page. If any page has `> 20` transitions, warning.
- Layer `author_canonical_id` values: for each segment with a non-None author_canonical_id, verify an entry exists in the manifest's `layer_map` with matching author_canonical_id.

**Check 5 — Division tree validity (SPEC lines 1488-1492):**
- Recursive check on each `DivisionNode`: `start_unit_index <= end_unit_index`.
- Sibling divisions (nodes at the same level under the same parent): no overlap. For siblings sorted by start_unit_index, verify `sibling[i].end_unit_index < sibling[i+1].start_unit_index` (or `<=` if using inclusive end — check DivisionNode: `end_unit_index` is inclusive). Actually DivisionNode has `end_unit_index: int = Field(ge=0, description="Inclusive end")` — so siblings must not have overlapping [start, end] ranges.
- Child divisions: for each child, verify `parent.start_unit_index <= child.start_unit_index` and `child.end_unit_index <= parent.end_unit_index`.
- Full coverage: union of top-level divisions covers `[0, total_content_units - 1]`. Warning (not fatal) if gaps exist — sparse structure is valid per L-003.

**Check 6 — Footnote integrity (SPEC lines 1494-1497):**
- For each content unit: every footnote has non-empty `text` field. Empty footnote text → warning.
- Orphan footnote references: scan `primary_text` for pattern `⌜(\d+)⌝` (U+231C, digits, U+231D). For each match, check if a footnote with matching `ref_marker` exists. Log `NORM_ORPHAN_FOOTNOTE_REF` (info) for mismatches. NOT fatal.
- Footnotes with no reference marker in text: valid per SPEC. No flag needed.

**Check 7 — Unit index integrity (SPEC line 1499):**
- Extract `unit_index` from each content unit. Sort them.
- Verify sequence is exactly `0, 1, 2, ..., N-1` where `N = len(content_units)`.
- Any gap or duplicate → `NORM_UNIT_INDEX_VIOLATION` (fatal).

**Check 8 — Diacritics preservation utility (SPEC line 1501):**
- **This check is NOT called from validate_package().** It runs inside each normalizer during processing (see D6-1).
- Provide a standalone utility function in validation.py:
  ```python
  DIACRITICS_CHECK8: set[int] = set(range(0x064B, 0x0653)) | {0x0670, 0x0640}

  def check_diacritics_page(source_text: str, output_text: str) -> bool:
      """Return True if diacritics counts match. False means drift detected."""
      source_d = [c for c in source_text if ord(c) in DIACRITICS_CHECK8]
      output_d = [c for c in output_text if ord(c) in DIACRITICS_CHECK8]
      return len(source_d) == len(output_d)
  ```
  Note: DO NOT use the existing `_ARABIC_DIACRITICS` set from shamela.py — that set is broader (20 codepoints for the entity corruption canary). The check 8 set is EXACTLY per SPEC: 10 codepoints.

**Check 10 — Boundary continuity consistency (SPEC line 1505):**
For each content unit except the last:
- (a) If `boundary_continuity` is present: verify `type` is a valid `BoundaryContinuityType` value (Pydantic enforces this, but verify explicitly for packages constructed outside Pydantic).
- (b) `confidence` in range `0.0–1.0` (Pydantic enforces, verify explicitly).
- (c) If `type == BoundaryContinuityType.MID_SENTENCE`: strip trailing whitespace from `primary_text` and check last character. If last char is in terminal punctuation set `{'.', '؟', '!'}` → `NORM_CONTINUITY_INCONSISTENT` (warning). **Also mutate**: set `boundary_continuity.confidence = 0.0` on the content unit.
- (d) Last content unit: `boundary_continuity` must be `None`. If present → `NORM_CONTINUITY_INCONSISTENT` (warning).

### 2. `src/writer.py` — Atomic Disk Writer

Replace the stub. Implement `write_normalized_package()` and `recover_interrupted_write()`.

**`write_normalized_package(package, source_id, library_root) -> Path`**

Procedure (SPEC lines 235-237):
1. Compute output dir: `library_root / "sources" / source_id / "normalized"`.
2. Create temp dir: `normalized_tmp_{ISO_timestamp}/` as sibling of final dir. Use `datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')` for timestamp.
3. Write `manifest.json`: `package.manifest.model_dump_json(indent=2)`. Open with `encoding='utf-8'`. Flush and fsync the file descriptor.
4. Write `content.jsonl`: one JSON line per content unit via `cu.model_dump_json()` + `'\n'`. Flush and fsync.
5. Verify both files: check existence, non-zero size, re-parse manifest.json as JSON, re-parse first and last lines of content.jsonl as JSON.
6. Clean up old prev dirs: delete any existing `normalized_prev_*` directories.
7. If previous `normalized/` exists: rename to `normalized_prev_{timestamp}/`.
8. Atomic rename: `temp_dir.rename(final_dir)`. On failure (e.g. Windows cross-device), fall back to `shutil.move`.
9. Delete all `normalized_prev_*` directories.
10. Return `final_dir`.

On any failure: remove temp dir (use `shutil.rmtree` with `ignore_errors=True`), raise `NORM_WRITE_FAILED` (fatal). Include the original exception message.

**`recover_interrupted_write(source_id, library_root) -> bool`**

SPEC line 237 (interrupted write recovery). Call at normalizer startup.
1. Compute base dir: `library_root / "sources" / source_id`.
2. Find temp dirs: glob `normalized_tmp_*`.
3. Find prev dirs: glob `normalized_prev_*`.
4. If no temp dirs exist → return False (no recovery needed).
5. If temp exists AND `normalized/` does NOT exist AND at least one prev exists:
   - Try to validate temp: check manifest.json and content.jsonl exist, are non-zero, parse as JSON/JSONL.
   - If valid: rename temp → `normalized/`. Delete all prev dirs. Log `NORM_WRITE_RECOVERY`.
   - If invalid: parse timestamps from prev dir names. Select the one with the LATEST timestamp. Rename it to `normalized/`. Delete temp and all other prev dirs. Log `NORM_WRITE_RECOVERY`.
6. If temp exists but `normalized/` already exists → just delete the orphaned temp dir.
7. Return True if any recovery action was taken.

ADV-047: multiple prev dirs → select latest timestamp. Temp with missing content.jsonl → invalid → restore from latest prev.

### 3. `src/normalizers/plain_text.py` — Plain Text Normalizer (§4.A.4c)

New file. Implements `BaseNormalizer` for `SourceFormat.PLAIN_TEXT`.

**`PlainTextNormalizer(BaseNormalizer)`**

**`validate_input(frozen_path, metadata)`:**
- Verify frozen_path is a file ending in `.txt` OR a directory containing at least one `.txt` file.
- Verify the file is readable and has at least 1 byte.
- If no .txt files found → raise `NormalizationError(NORM_MISSING_FROZEN)`.

**`normalize(frozen_path, metadata) -> NormalizedPackage`:**

Processing steps:
1. **Read source file.** If frozen_path is a directory, concatenate all .txt files sorted by name with `'\n\n'` between them. Handle encoding: try UTF-8 first (`errors='strict'`). On UnicodeDecodeError, fall back to `charset_normalizer.detect()`. If that also fails → `NORM_ENCODING_ERROR` (warning), try UTF-8 with `errors='replace'` and set fidelity to `low`.
2. **Split into content units.** Per D6-6: split at `'\n\n'`, merge short segments, split long segments at ~2000 chars on whitespace boundaries.
3. **Assign unit_index.** Sequential 0-based.
4. **Diacritics check (§5 check 8).** For each unit, call `check_diacritics_page(source_segment, unit.primary_text)`. Since plain text has no HTML processing, the only potential drift source is encoding conversion. If drift detected → `NORM_DIACRITICS_DRIFT` (fatal).
5. **Structure discovery.** Call `discover_structure(pages, source_id, genre)` from `src/structure_discovery.py` (line 1144). Signature: `discover_structure(pages: list[CleanedPage], source_id: str, genre: Optional[Genre]) -> StructureResult`. Returns `StructureResult` with `division_tree`, `page_markers`, `quality_counts`, `overall_confidence`, `toc_page_indices`. The function needs `CleanedPage` objects — create them for each content unit segment using `_make_cleaned_page()` pattern (empty bold_spans, title_spans, etc.). Import `Genre` from `engines.source.contracts`. Structure discovery uses keyword heuristics (Tier 2) on the text content; Tier 1 (HTML) won't fire for plain text; Tier 3 (LLM) is a stub.
6. **Layer detection.** Always single-layer. For each unit, create one `TextLayerSegment(layer_type=LayerType.SHARH, start=0, end=len(primary_text), confidence=1.0)`. If `metadata.is_multi_layer` is True, still create single-layer segments but add a warning — plain text cannot detect layers from formatting. The segment `layer_type` should be `MATN` if `not metadata.is_multi_layer`, `SHARH` if `metadata.is_multi_layer` (conservative default per SPEC — commentary layer is the safe attribution for unknown).
7. **Content flags.** Call `compute_content_flags(page, is_toc_page)` from `src/content_flagger.py` (line 131). Signature: `compute_content_flags(page: CleanedPage, is_toc_page: bool) -> ContentFlags`. Pass `is_toc_page=False` for all plain text units.
8. **Boundary continuity.** Call `classify_boundary(current_page, next_page, current_markers, next_markers, is_volume_boundary)` from `src/boundary_continuity.py` (line 201). All args are `CleanedPage` or `StructuralMarkers` — use the ones from structure discovery. Set `is_volume_boundary=False` for plain text.
9. **Assemble package.** Build `ContentUnit` list and `NormalizedManifest`. Key fields:
   - `physical_page`: all fields None (no physical pages in .txt).
   - `normalizer_id`: `"kr.normalization.plain_text_v1"`.
   - `text_fidelity.score`: `TextFidelityLevel.HIGH` (default for digital text) or `LOW` if encoding fallback was used.
   - `structural_format`: from metadata, default `StructuralFormat.PROSE`.
   - `layer_map`: single entry.
   - `total_content_units`: `len(content_units)`.
   - Deferred §4.B fields: all `None`.

### 4. `src/dispatcher.py` — Registry Population + Orchestration

**Registry population** — replace the empty dict with:

```python
from engines.normalization.src.normalizers.shamela import ShamelaNormalizer
from engines.normalization.src.normalizers.plain_text import PlainTextNormalizer
from engines.source.contracts import SourceFormat

_NORMALIZER_REGISTRY: dict[SourceFormat, type[BaseNormalizer]] = {
    SourceFormat.SHAMELA_HTML: ShamelaNormalizer,
    SourceFormat.PLAIN_TEXT: PlainTextNormalizer,
}
```

**Add `normalize_and_write()` function:**

```python
def normalize_and_write(
    frozen_path: Path,
    metadata: SourceMetadata,
    library_root: Path,
) -> Path:
    """Full pipeline: normalize → validate → write atomically.

    Returns path to the written normalized/ directory.
    Raises NormalizationError on validation failure or write failure.
    """
    from engines.normalization.src.validation import validate_package
    from engines.normalization.src.writer import (
        write_normalized_package,
        recover_interrupted_write,
    )

    # Recovery check before processing
    recover_interrupted_write(metadata.source_id, library_root)

    # Normalize (includes format-specific input validation via validate_input)
    package = normalize_source(frozen_path, metadata)

    # §5 Layer 1 validation
    result = validate_package(package, metadata)
    if not result.passed:
        # Collect error messages for diagnostics
        error_msgs = "; ".join(e.message for e in result.fatal_errors)
        raise NormalizationError(
            code=NormErrorCode.SCHEMA_VIOLATION,
            message=f"§5 validation failed with {len(result.fatal_errors)} fatal error(s): {error_msgs}",
            source_id=metadata.source_id,
            recovery="Fix the normalization bug indicated by the validation errors.",
        )

    # Atomic write
    return write_normalized_package(package, metadata.source_id, library_root)
```

Keep `normalize_source()` unchanged. Keep `register_normalizer()` unchanged.

### 5. Shamela Normalizer — Check 8 Integration

Modify `engines/normalization/src/normalizers/shamela.py` with MINIMAL changes:

**(a) Add `raw_decoded_text` field to `CleanedPage` (line ~245):**
```python
raw_decoded_text: str = Field(default="", description="Tag-stripped, entity-decoded source text for §5 check 8")
```

**(b) In `_pass3_clean()`, at line 1305, capture `raw_decoded_text`:**
Line 1305 is: `text = decode_entities(strip_tags(html))`. This is the decoded primary text BEFORE footnote ref replacement (line 1311), verse marker cleanup (line 1308), and whitespace normalization (line 1321). Immediately after line 1305, add: `raw_decoded_text = text`. Then pass `raw_decoded_text=raw_decoded_text` to the CleanedPage constructor at line 1337.

**(c) Add `_verify_diacritics_preservation()` method:**
```python
def _verify_diacritics_preservation(
    self,
    cleaned: list[CleanedPage],
    package: NormalizedPackage,
) -> None:
    """§5 check 8: Verify no diacritics were lost during normalization."""
    from engines.normalization.src.validation import check_diacritics_page

    for i, page in enumerate(cleaned):
        if page.is_blank or page.is_image_only:
            continue
        # Source text = raw decoded primary HTML (footnotes already separated in Pass 2)
        source_text = page.raw_decoded_text
        # Output text = primary_text only (NOT footnotes — they pass through
        # unchanged from ParsedFootnote.text to Footnote.text, so no drift risk)
        cu = package.content_units[i]
        output_text = cu.primary_text
        if not check_diacritics_page(source_text, output_text):
            raise NormalizationError(
                code=NormErrorCode.DIACRITICS_DRIFT,
                message=(
                    f"Diacritics count mismatch on page unit_index={cu.unit_index}: "
                    f"source and output differ"
                ),
                source_id=cu.source_id,
                unit_index=cu.unit_index,
                recovery="Investigate which processing step is modifying diacritics.",
            )
```

**(d) In `normalize()` (around line 500-511), call after assembly:**
After `return self._pass6_assemble(...)`, change to:
```python
package = self._pass6_assemble(...)
self._verify_diacritics_preservation(cleaned, package)
return package
```

These are the ONLY 4 changes to shamela.py. Do NOT modify any other method.

### 6. Tests

Create three new test files + unskip relevant tests in `test_kr_output.py`.

**Test helper needed:** Add a `_make_normalized_package(**overrides)` factory to `conftest.py` that builds a minimal valid `NormalizedPackage` (1 content unit, valid manifest, contiguous unit_index). Validation and writer tests need to construct packages with specific defects — the factory provides the valid baseline, and tests override individual fields to inject the defect. Pattern: same as `_make_source_metadata()` but for the output side. Must include: valid `layer_map` (single entry), `division_tree` (single root node covering [0, N-1]), `quality_report`, `text_fidelity_summary`, and at least 1 `ContentUnit` with non-empty `primary_text`, valid `text_layers` covering [0, len), and `text_fidelity`.

**`engines/normalization/tests/test_validation.py`** (NEW FILE) — Unit tests for each check function:
- Import from conftest.py: `_make_source_metadata`, `_make_cleaned_page`, `_make_html`, `_wrap_page`, `_full_pipeline`.
- Build test packages using contract models directly (create NormalizedPackage instances with crafted content).
- For each check: at least one positive test (valid package passes) and one negative test (invalid package caught).
- Dedicated ADV tests:
  - ADV-025: Arabic ratio at exactly 70% passes (`>= 0.70`), 69% fails.
  - ADV-028: Coverage 89/100 → warning, 91/100 → passes, 90/100 → passes (> not >=).
  - ADV-029: Run of exactly 20 identical chars → no flag, 21 → flag.
  - ADV-033: `total_content_units` = 5 but 4 content units → fatal.
  - ADV-026: `mid_sentence` + terminal period → `NORM_CONTINUITY_INCONSISTENT`, confidence set to 0.0.
  - ADV-021 + ADV-045: `check_diacritics_page()` with matching counts → True, mismatched → False.
- Check 4 (layer consistency): full coverage violation → fatal. Matn ratio 0.45 in sharh → warning. 25 transitions on one page → warning.
- Check 5 (division tree): overlap → error. Child outside parent → error. Gap in coverage → warning.
- Check 6: empty footnote text → warning. Orphan `⌜3⌝` marker → info.
- Check 7 (unit index): gap (0,1,3) → fatal. Duplicate (0,1,1,2) → fatal.
- Check 10: last unit with boundary_continuity present → warning.
- **Minimum: 25 test functions.**

**`engines/normalization/tests/test_writer.py`** (NEW FILE) — Tests for atomic write and recovery:
- Use `tmp_path` pytest fixture for isolated filesystem.
- Helper: build a minimal valid NormalizedPackage using conftest factories.
- Test: write creates manifest.json + content.jsonl at `{tmp_path}/sources/{source_id}/normalized/`.
- Test: written manifest.json is valid JSON, parseable as NormalizedManifest.
- Test: content.jsonl line count == len(content_units).
- Test: each line of content.jsonl is valid JSON.
- Test: reprocessing — when `normalized/` already exists, it's renamed to `normalized_prev_*`, then deleted after new write succeeds.
- Test: write failure (make parent dir read-only) → `NORM_WRITE_FAILED` raised, no temp dir remains.
- ADV-047: Create multiple `normalized_prev_*` dirs and one invalid `normalized_tmp_*`. Call `recover_interrupted_write()`. Assert: recovery from LATEST prev. Assert: temp and all prevs cleaned up.
- Test: recovery when temp is valid → promoted to `normalized/`.
- Test: no recovery needed when no temp dirs exist → returns False.
- **Minimum: 10 test functions.**

**`engines/normalization/tests/test_plain_text.py`** (NEW FILE) — Tests for plain text normalizer:
- Test: simple .txt file produces valid NormalizedPackage (schema validates).
- Test: paragraph splitting at `\n\n` boundaries.
- Test: long paragraph (> 3000 chars) split at ~2000 char whitespace boundary.
- Test: consecutive short paragraphs (< 1000 chars each) merged.
- Test: single short text (< 1000 chars) → one content unit.
- Test: physical_page fields are all None for every unit.
- Test: structure discovery detects `باب` and `فصل` headings in plain text.
- Test: always single-layer — `text_layers` has one segment per page.
- Test: content flags: Quran bismillah detected, hadith ﷺ marker detected.
- Test: validate_input rejects non-existent path with `NORM_MISSING_FROZEN`.
- Test: validate_input rejects empty file.
- Test: normalizer_id is `"kr.normalization.plain_text_v1"`.
- **Minimum: 12 test functions.**

**`engines/normalization/tests/test_kr_output.py` — Unskip and implement:**
- `TestValidation` (5 tests): valid package passes, empty content rejected, missing manifest fields rejected, unit_index gaps detected, metadata passthrough verified (D-023: source_id preserved).
- `TestWriter` (3 tests): write creates files, interrupted write clean, files are valid JSON.
- `TestDispatcher` (2 tests): SHAMELA_HTML routes to ShamelaNormalizer, unknown format raises NORM_UNKNOWN_SOURCE_FORMAT.
- Leave skipped: `TestContentCensus`, `TestContentFlagger` (3 tests), `TestShamelaNormalizer` (8 tests) — Session 7.
- **Unskip total: 10 tests.**

---

## Design Decisions (pre-resolved — do NOT deviate)

**D6-1: Check 8 (diacritics) runs inside each normalizer, not in validate_package().**
Rationale: The normalizer has the per-page source text needed for comparison. validate_package() would need this data passed in, complicating the interface. Each normalizer implements check 8 after assembly. validate_package() handles checks 1-7 and 10 only. Provide a reusable utility `check_diacritics_page(source_text, output_text) -> bool` in validation.py for normalizers to import.

**D6-2: Dispatcher gets `normalize_and_write()` for end-to-end flow.**
`normalize_source()` stays unchanged (returns in-memory package for testability). `normalize_and_write()` adds validation + atomic write. Tests call `normalize_source()`. Production calls `normalize_and_write()`.

**D6-3: Check 8 diacritics character set is EXACTLY per SPEC (line 1501).**
```python
DIACRITICS_CHECK8: set[int] = set(range(0x064B, 0x0653)) | {0x0670, 0x0640}
```
This is: U+064B (fathatan) through U+0652 (sukun), plus U+0670 (superscript alef), plus U+0640 (tatweel/kashida). Total: 10 codepoints.
WARNING: the existing `_ARABIC_DIACRITICS` set in shamela.py (line 158) is BROADER (20 codepoints for the entity corruption canary, includes U+0653 maddah and U+0656-U+065F). Do NOT reuse it for check 8. Also it EXCLUDES U+0640 which check 8 INCLUDES. Use the SPEC-exact set.

**D6-4: Check 8 compares diacritics in primary text only (NOT footnotes).**
Pass 2 separates footnotes from primary_html BEFORE Pass 3 processes the HTML. So `raw_decoded_text` (captured in Pass 3) contains only the primary text area — no footnote body text. Footnote text passes through unchanged from `ParsedFootnote.text` to `Footnote.text` (line 1128 in shamela.py), so there is zero drift risk in the footnote path. The correct comparison is: `source = raw_decoded_text` vs `output = cu.primary_text`. Do NOT include footnote text on either side — that would cause a false positive because the source side doesn't have it.

**D6-5: Shamela normalizer saves raw decoded page text during Pass 3.**
Add `raw_decoded_text: str` field to `CleanedPage`. Populate in `_pass3_clean()` at line 1305 — immediately after `text = decode_entities(strip_tags(html))` and BEFORE verse marker cleanup (line 1308), footnote ref replacement (line 1311), or whitespace normalization (line 1321). Set `raw_decoded_text = text` right after line 1305. Pass it to the CleanedPage constructor at line 1337. Note: `raw_decoded_text` contains the primary text area only — footnotes were already separated in Pass 2.

**D6-6: Plain text content unit splitting algorithm.**
1. Split input text at double newline boundaries (`\n\n`). Single newlines are NOT unit boundaries.
2. If a resulting segment is > 3000 characters, split at the whitespace nearest to 2000 characters.
3. If consecutive segments are each < 1000 characters, merge them (join with `\n\n`).
4. Target: median unit size of 1500-2500 characters.
5. If the entire file is < 1000 characters, produce a single content unit.
6. Empty segments (whitespace only after splitting) are discarded.

**D6-7: Dispatcher registry is populated at module level via dict literal.**
Not lazy import, not a registration function call. The imports at the top of dispatcher.py bring in both normalizer classes. This is simple and explicit.

**D6-8: validate_package runs the loose coverage check only (±10% vs metadata.page_count).**
The Shamela normalizer does NOT yet implement the tight check (exact input page count vs output count). That is deferred to Session 7 integration testing. validate_package only runs the loose check. If `metadata.page_count` is None or 0, skip the check entirely (no warning, no error).

**D6-9: Mojibake detection patterns (check 3).**
Common Arabic-as-Latin-1 mojibake: sequences of `[\xc0-\xff][\x80-\xbf]` interpreted as Latin-1 produce characters like Ø, Ù, Ú adjacent to €, ©, ®, etc. Detect with regex: `r'[\u00c0-\u00ff]{3,}'` — 3+ consecutive characters from the Latin Extended block in text that should be Arabic. If detected → warning per page. This is a heuristic — false positives on intentional Latin text are acceptable (warning only, not fatal).

**D6-10: Terminal punctuation set for check 10c.**
Characters that contradict `mid_sentence`: `.` (U+002E period), `؟` (U+061F Arabic question mark), `!` (U+0021 exclamation mark). Strip trailing whitespace from primary_text before testing the last character. DO NOT include comma, semicolon, or colon — these do not end sentences.

---

## Do NOT Do

- Do NOT change `shamela.py` Passes 1-5 logic. The ONLY changes to shamela.py are: (a) add `raw_decoded_text` field to CleanedPage, (b) populate it in `_pass3_clean()`, (c) add `_verify_diacritics_preservation()` method, (d) call it after `_pass6_assemble()` in `normalize()`.
- Do NOT change `boundary_continuity.py` — it passed review clean in Session 5.
- Do NOT change `content_flagger.py` — it passed review clean in Session 5.
- Do NOT change `layer_detector.py` or `structure_discovery.py`.
- Do NOT implement §5 checks 11-14 (discourse flow, fingerprints, OCR coherence, OCR diacritics hallucination — all deferred §4.B capabilities).
- Do NOT implement §5 Layer 2 (quality report review) or Layer 3 (human gate integration).
- Do NOT implement content census (§4.B.5).
- Do NOT implement Tier 3 LLM structure discovery for plain text.
- Do NOT implement multi-layer detection for plain text (§4.B.1 dependency).
- Do NOT implement the tight coverage check in validate_package (see D6-8).
- Do NOT unskip `TestContentCensus`, `TestContentFlagger`, or `TestShamelaNormalizer` integration tests in test_kr_output.py — Session 7.
- Do NOT use `json.dumps(ensure_ascii=False)` for writing — use Pydantic's `model_dump_json()` which handles this correctly.
- Do NOT apply Unicode normalization (NFC/NFD/NFKC/NFKD) anywhere in the writer or plain text normalizer. ADV-021.

---

## ADV Coverage

Session 6 targets these adversarial cases from `reference/SPEC_ADVERSARY_NORMALIZATION.md`:

| ADV | Category | Check | What to Test |
|-----|----------|-------|-------------|
| ADV-021 (line 419) | arabic_trap | 8 | NFC normalization silently changing Arabic text — check_diacritics_page catches it |
| ADV-025 (line 541) | boundary_value | 3 | Arabic ratio at exactly 70% passes (>= 0.70), 69% fails |
| ADV-026 (line 556) | silent_corruption | 10 | mid_sentence + terminal punct → NORM_CONTINUITY_INCONSISTENT, confidence 0.0 |
| ADV-028 (line 589) | boundary_value | 2 | Coverage 89/100 → warning, 91/100 → no warning, 90/100 → no warning |
| ADV-029 (line 601) | boundary_value | 3 | Identical run at exactly 20 → no flag, 21 → flag |
| ADV-033 (line 685) | silent_corruption | 1 | total_content_units ≠ actual content unit count → fatal |
| ADV-045 (line 435) | silent_corruption | 8 | Diacritics drift detection — single diacritic difference caught |
| ADV-047 (line 657) | format_edge_case | writer | Multiple prev dirs → select latest timestamp for recovery |

Each ADV case MUST have at least one dedicated test with the exact inputs/outputs described in the adversary file.

---

## Verification

```bash
# Step 1: All existing tests pass (zero regressions)
python -m pytest engines/normalization/tests/ -v --tb=short

# Step 2: Cross-engine contracts
python tools/check_cross_engine_contracts.py
```

**Pass criteria:**
- 256 existing tests still pass (zero regressions).
- 35+ new tests pass across test_validation.py (25+), test_writer.py (10+), test_plain_text.py (12+).
- 10 previously-skipped tests in test_kr_output.py are unskipped and passing.
- Cross-engine contracts: PASS.
- All 8 ADV cases listed above have dedicated tests.
- `normalize_source()` returns validated package for both Shamela HTML and plain text.
- `normalize_and_write()` validates + writes manifest.json + content.jsonl atomically.
- `recover_interrupted_write()` handles ADV-047 scenario.
- `check_diacritics_page()` utility detects single-diacritic drift (ADV-045).

**Minimum total new test count: 47** (25 validation + 10 writer + 12 plain text). Plus 10 unskipped from test_kr_output.py = 57 total new passing tests. If you have fewer than 47 NEW tests, you missed cases.

---

## After This

Return to the architect for Session 6 review. The architect will:
1. Run all tests and verify counts.
2. Probe validation checks with constructed edge-case inputs (boundary values).
3. Verify ADV case coverage — every ADV test uses exact inputs from the adversary file.
4. Test the plain text normalizer on a real .txt fixture (will create one for the review).
5. Verify atomic write creates valid JSON/JSONL files on disk.
6. Verify check 8 diacritics comparison catches actual drift on Shamela fixture data.
7. Verify `normalize_and_write()` end-to-end flow.
8. If clean → ACCEPT → Session 7 (integration testing on all fixtures).
