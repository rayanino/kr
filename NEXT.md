# NEXT — Review Session 5: Pass 6 Assembly (Content Flagging, Boundary Continuity, Output)

## Current position: Session 5 BUILD COMPLETE (commit d1f9cb3). CC implemented Pass 6: content flagger, boundary continuity, output assembly. 253 tests passing (173 existing + 80 new). 10 files changed, +1689/-190 lines.
## What to do: Review CC's Session 5 output using kr-reviewing-cc-output (3-round protocol per reference/protocols/REVIEW_PROTOCOL.md).
## Context: CC built the three deliverables described below. The review verifies correctness against SPEC, traces concrete examples through the implementation, and checks cross-engine compatibility. After ACCEPT, the Build Prober runs, then Session 6.
## Owner action needed: NO — start new Claude Chat session for review.
## Git range for review: `1329dce..d1f9cb3` (1 CC commit)

---

## Session 5 Build Instructions (what CC was asked to do — reference for reviewer)


## Read First (in this order)

1. `engines/normalization/CLAUDE.md` (108L) — Engine orientation. Session 5 row: "Pass 6 assembly (boundary continuity, flagging, output) | §4.B.8, §4.A.9, §4.A.2 Pass 6".

2. `engines/normalization/SPEC.md` lines 219–233 — §4.A.2 Pass 6 overview. Lists all enrichment steps in dependency order. **Core steps for Session 5: #1 (content flagging §4.A.9) and #7 (cross-page continuity §4.B.8). All other steps are DEFERRED — leave those manifest fields as `None`.**

3. `engines/normalization/SPEC.md` lines 660–700 — §4.A.9 Content Flagging. 7 boolean flags. Concrete example with expected output. Detection patterns for each flag.

4. `engines/normalization/SPEC.md` lines 1129–1221 — §4.B.8 Cross-Page Continuity Intelligence. Full specification: 6 boundary types, argument flow marker table, signal priority rule (heading > argument > punctuation), format-specific signals (Shamela: punctuation analysis + connectives), concrete example with expected output, edge cases. Ends at `[NOT YET IMPLEMENTED]` marker.

5. `engines/normalization/contracts.py` — Read these types:
   - `ContentFlags` (line 216): 7 boolean fields
   - `BoundaryContinuityType` (line 238): 6 enum values
   - `ContinuityDetectionMethod` (line 248): 5 enum values
   - `BoundaryContinuity` (line 257): type + confidence + detection_method + continuation_hint
   - `ContentUnit` (line 427): the output record — all fields that must be populated
   - `PhysicalPage` (line 101): volume, page_number_display, page_number_int
   - `Footnote` (line 168): the contract footnote type (vs `ParsedFootnote` internal type)
   - `FootnoteType` (line 61): enum with coarse types (tahqiq_editor, author_original, unknown)
   - `TextFidelityLevel` (line 24): enum (very_low, low, medium, high)
   - `StructuralMarkers` (line 190): heading_detected, heading_text, heading_level, etc.
   - `NormalizedManifest` (line 660): all manifest fields
   - `QualityReport` (line 529): quality metrics
   - `TextFidelitySummary` (line 521): aggregate fidelity
   - `NormalizedPackage` (line 716): manifest + content_units

6. `engines/normalization/src/normalizers/shamela.py` (1,224L) — Read:
   - `normalize()` method (lines 463–505): the NotImplementedError to replace
   - `CleanedPage` class (lines 232–265): all fields — these are Pass 6 inputs
   - `ParsedFootnote` class (lines 167–182): internal footnote type — must be converted to contract `Footnote`
   - `_pass4_discover_structure()` (lines 929–948): currently returns 4-tuple (division_tree, page_markers, div_counts, struct_confidence). **D3 adds a 5th element: toc_page_indices.** `page_markers` is a `dict[int, StructuralMarkers]` — unit_index → heading info for that page.
   - `_pass5_detect_layers()` (lines 952–1036): returns (per_page_segments `list[list[TextLayerSegment]]`, layer_map `list[LayerMapEntry]`)

7. `engines/normalization/src/structure_discovery.py` — Read:
   - `StructureResult` (line 97): note `page_markers: dict[int, StructuralMarkers]`
   - `_tier1_html_tagged()` (line 290): returns `(candidates, toc_indices)` — **toc_indices is a `list[int]` of unit_index values for TOC pages**, but it's NOT currently in StructureResult. See D3 below.
   - `TOC_EXACT_TITLES` (line 50): the frozenset of TOC heading keywords

8. `engines/normalization/src/errors.py` (130L) — Error codes. Relevant: `CONTINUITY_INCONSISTENT` (line 48, WARNING), `CONTINUITY_UNKNOWN` (line 49, INFO). No new error codes needed — these already exist.

9. `reference/SPEC_ADVERSARY_NORMALIZATION.md` — Search for these Session 5 ADV tests:
   - ADV-026 (mid_sentence with terminal punctuation — boundary continuity consistency check)
   - ADV-024 (Quran citation without standard prefix — content flagger pattern coverage)
   - ADV-050 (hadith citation with non-standard introduction — content flagger pattern coverage)
   - ADV-051 (TOC page detection — content flagger integration with structure discovery)
   ADV-024 and ADV-050 test whether the existing patterns catch non-standard introductions. The adversarial inputs in both cases contain markers that our patterns already detect (curly braces for ADV-024, ﷺ for ADV-050), so they should pass. ADV-051 tests is_toc_page via structure discovery's TOC detection. Include at least one test per ADV case.

10. `engines/normalization/tests/test_layer_detection.py` — Read the test infrastructure section (lines 66–215). Reuse `_make_source_metadata()`, `_make_cleaned_page()`, `_make_text_layers_sharh()`, `_full_pipeline()`, `_wrap_page()`, `_make_html()`. Either import from this file or extract to a shared `conftest.py`.

---

## What to Build

### Deliverable 1: `engines/normalization/src/content_flagger.py` — New module (~100-150 lines)

Compute `ContentFlags` for a `CleanedPage`. Surface-level pattern matching only (SPEC: "The normalization engine uses surface-level signals only").

**Function:**
```python
def compute_content_flags(
    page: CleanedPage,
    is_toc_page: bool,  # from structure discovery TOC detection
) -> ContentFlags:
```

**Flag detection rules:**

- `has_verse`: Use `page.has_verse` from CleanedPage (already computed by Pass 3 verse detection).
- `has_table`: Use `page.has_tables` from CleanedPage (already computed by Pass 1 table extraction).
- `has_quran_citation`: Scan `page.primary_text` for Quran citation patterns:
  - `قال تعالى` (Quran introduction formula)
  - Curly braces `{...}` containing Arabic text (Quran quotation markers in Shamela)
  - `﴿...﴾` (ornate Quran brackets)
  - Surah references: `سورة` followed by a name
  - Any ONE of these is sufficient for `True`.
- `has_hadith_citation`: Scan `page.primary_text` for hadith patterns:
  - `ﷺ` or `صلى الله عليه وسلم` (Prophet reference)
  - `رواه` followed by collector name patterns (`البخاري`, `مسلم`, `أبو داود`, `الترمذي`, `النسائي`, `ابن ماجه`, `أحمد`)
  - `«...»` guillemets containing Arabic text AND preceded by `قال` within 50 chars (hadith quotation pattern)
  - Any ONE of these is sufficient for `True`.
- `is_toc_page`: Use the `is_toc_page` parameter (from structure discovery — see D3).
- `is_index_page`: Scan `page.primary_text` first 200 chars AND `page.title_spans` for index keywords: `فهرس الأعلام`, `فهرس الأحاديث`, `فهرس الآيات`, `فهرس المصادر`, `فهرس الأبيات`. NOT `فهرس الموضوعات` (that's TOC, not index). Match if ANY keyword appears in either the first 200 chars of primary_text or in any title_span string.
- `is_blank`: Use `page.is_blank` OR `page.is_image_only` OR `len(page.primary_text.strip()) == 0`.

**Tests:** 10+ tests. Test each flag independently with constructed Arabic text. Test the SPEC concrete example (§4.A.9 lines 674–696). Test negative cases (pages without Quran/hadith). Test at least 2 real fixture pages that have Quran citations (fixture `05_tafsir` — 48 pages, most contain Quran markers) and 2 that have hadith citations (fixture `10_no_author` — 141 pages, most contain hadith patterns).

### Deliverable 2: `engines/normalization/src/boundary_continuity.py` — New module (~150-200 lines)

Classify every page boundary. Receives pairs of consecutive pages. Always returns a `BoundaryContinuity` (the assembly loop handles None for last page and blank current pages — see Deliverable 3 step 3).

**Function:**

```python
def classify_boundary(
    current_page: CleanedPage,
    next_page: CleanedPage,
    current_markers: Optional[StructuralMarkers],
    next_markers: Optional[StructuralMarkers],
    is_volume_boundary: bool,
) -> BoundaryContinuity:
```

**Detection algorithm (SPEC §4.B.8 signal priority):**

0. **Short-circuit for blank/image-only next page.** If `next_page.is_blank` or `next_page.is_image_only` → return `BoundaryContinuity(type=unknown, confidence=0.30, method=punctuation_analysis, continuation_hint="next page is blank/image-only")`. Log `NORM_CONTINUITY_UNKNOWN`. **Note:** blank/image-only CURRENT pages are handled in the assembly loop — the assembly code skips calling `classify_boundary` entirely for those pages and sets `boundary_continuity=None` directly.

1. **Check volume boundary first.** If `is_volume_boundary` is True → `division_break`, confidence 0.95, method `structural_marker`.

2. **Check structural heading.** If `next_markers` has `heading_detected=True` → `section_break`, confidence from heading_confidence mapping (confirmed/high → 0.95, medium → 0.85, low → 0.75, minimal → 0.65), method `structural_marker`. **Heading ALWAYS overrides punctuation and argument analysis** (SPEC signal priority rule).

3. **Check argument flow.** Scan last 200 chars of `current_page.primary_text` for opening markers from the SPEC table. **Match the SPECIFIC phrases listed below — not the full SPEC table.** The SPEC's conditional reasoning markers (`إذا`, `ولو أن`, `فإن كان`) are excluded from the initial implementation because they're common Arabic words that fire on 15-19% of fiqh pages as false positives (see D7). The `وذهب ... إلى` pattern means: match the word `وذهب` (the `...` in the SPEC represents a scholar name that varies).

   **Opening markers to implement:**
   - Evidence chain: `والدليل`, `لقوله تعالى`, `ودليله`, `واحتجوا بـ`, `واستدلوا بـ`, `ولنا`
   - Position statement: `وذهب`, `والمذهب أن`, `القول الأول`
   - Objection-response: `واعترض عليه بأن`, `وأُشكل عليه`, `فإن قيل`

   **Closing markers (checked on same page to cancel mid_argument):**
   - Evidence chain closers: `ونوقش بأن`, `ورُدّ بأن`, `والجواب`
   - Position statement closers: `القول الثاني`, `والراجح`, `والصحيح`
   - Objection-response closers: `فالجواب`, `قلنا`, `والجواب عنه`

   Matching is category-specific: an evidence chain opener is only cancelled by an evidence chain closer on the same page. If opener found AND no matching-category closer on the same page → `mid_argument`, method `argument_flow`, continuation_hint describes the opened marker and its category. **Confidence depends on punctuation corroboration** (SPEC §4.B.8 line 1174: "mid_argument subsumes mid_sentence when both are detected"): check last non-whitespace character of `current_page.primary_text` — if NO terminal punctuation (`.`, `۔`, `؟`, `!`, `؛`), both signals agree the content continues → confidence **0.90**. If terminal punctuation IS present (sentence ended but argument not closed), only argument signal → confidence **0.70**. This matches the SPEC concrete example (lines 1184–1212) which produces 0.90 when `ولنا حديث` + colon (no terminal punctuation) co-occur.

4. **Punctuation analysis (fallback).** Check last non-whitespace character of `current_page.primary_text`:
   - Terminal punctuation (`.`, `۔`, `؟`, `!`, `؛`) present → `mid_paragraph`, confidence 0.75, method `punctuation_analysis`.
   - No terminal punctuation → `mid_sentence`, confidence 0.90, method `punctuation_analysis`.
   - **Shamela connective boost:** After the above classification, if `next_markers` is None or `heading_detected=False`, check the first non-whitespace word of `next_page.primary_text`. If it starts with a connective (و, ف, ثم), add to `continuation_hint` (e.g., `"next page starts with connective 'و'"`) but do NOT change the type or confidence — the connective confirms the existing classification.

5. **If no signal at all** (should be rare) → `unknown`, confidence 0.30, method `punctuation_analysis`. Log `NORM_CONTINUITY_UNKNOWN`.

**Internal data:**

```python
@dataclass
class _ArgumentMarker:
    category: str  # "evidence_chain", "position_statement", "objection_response"
    opening_patterns: list[str]
    closing_patterns: list[str]
```

Populate from the opening/closing marker lists above (3 categories, NOT the SPEC's conditional category — see D7). The matching is plain-text `in` check on the last 200 chars of primary_text (no regex needed — these are fixed Arabic phrases), EXCEPT for `وذهب` which requires a word-boundary check: after finding `وذهب` via `in`, verify the next character is a space, punctuation (`.؟!؛:،`), or end of string. Without this, conjugated forms like `وذهبت` (grammar) and `وذهب عقله` (literal "his mind went") produce false positives — confirmed on real fixtures. Closing marker check scans the ENTIRE page's primary_text, not just the tail.

**Tests:** 15+ tests. Must include:
- ADV-026 (mid_sentence with terminal punctuation — construct a page ending with `.` and verify classification is NOT mid_sentence)
- SPEC concrete example (§4.B.8 lines 1184–1212: page ending with `قال:` + `ولنا حديث` → mid_argument)
- Volume boundary → division_break
- Heading at next page start → section_break (overrides punctuation)
- Argument marker opened but closed on same page → NOT mid_argument
- Plain mid-sentence (no punctuation, no markers)
- Mid-paragraph (punctuation present, no heading)
- Blank/image-only next page → `unknown` with confidence 0.30
- Each HeadingConfidence level maps to the correct float (confirmed→0.95, minimal→0.65)
- At least 2 real fixture boundary spot-checks with printed Arabic text

### Deliverable 3: Output assembly in `shamela.py` (~100-150 lines added to `normalize()`)

Replace the `NotImplementedError` at line 498 with Pass 6 that:

1. **Thread TOC page indices** — implement D3 (see Design Decisions). Build `toc_set = set(toc_indices)` for O(1) lookup in content flagger.

2. **Compute content flags** — call `compute_content_flags(page, is_toc_page=page.unit_index in toc_set)` for each page.

3. **Compute boundary continuity** — for each consecutive page pair `(cleaned[i], cleaned[i+1])`:
   - If `cleaned[i].is_blank` or `cleaned[i].is_image_only` → set `boundary_continuity = None` (no text to analyze). Do NOT call `classify_boundary`.
   - If this is the last page (no `cleaned[i+1]`) → set `boundary_continuity = None`.
   - Otherwise → call `classify_boundary(current_page=cleaned[i], next_page=cleaned[i+1], current_markers=page_markers.get(cleaned[i].unit_index), next_markers=page_markers.get(cleaned[i+1].unit_index), is_volume_boundary=(cleaned[i].volume != cleaned[i+1].volume))`.

4. **Convert `ParsedFootnote` → contract `Footnote`** for each page:
   ```python
   Footnote(
       ref_marker=str(pf.number),
       text=pf.text,
       footnote_type=FootnoteType(pf.footnote_type),
       confidence=pf.classification_confidence,
   )
   ```

5. **Assemble `ContentUnit`** for each page:
   - `source_id` = metadata.source_id
   - `unit_index` = page.unit_index
   - `physical_page` = PhysicalPage(volume=page.volume, page_number_display=page.page_number_display, page_number_int=page.page_number_int)
   - `primary_text` = page.primary_text
   - `text_layers` = per_page_segments[i] (from Pass 5)
   - `footnotes` = converted Footnote list
   - `structural_markers` = page_markers.get(page.unit_index, StructuralMarkers())
   - `content_flags` = computed ContentFlags
   - `text_fidelity` = TextFidelity(score=TextFidelityLevel.HIGH)
   - `boundary_continuity` = computed (None for last page, None for blank/image pages)
   - `verse_info` = None (verse parsing not yet implemented — extension hook exists)
   - `discourse_flow` = None (deferred §4.B.10)

6. **Assemble `NormalizedManifest`:**
   - `normalizer_id` = "kr.normalization.shamela_v2"
   - `normalization_utc` = current UTC ISO 8601 (use `datetime.now(timezone.utc).isoformat()`)
   - `division_tree` = from Pass 4
   - `layer_map` = from Pass 5
   - `structural_format` = `StructuralFormat(metadata.structural_format.value)` (note: `.value` extracts the string from the source engine's `StructuralFormat` enum to construct the normalization engine's `StructuralFormat` enum — they are separate types with identical values)
   - `text_fidelity_summary` = `TextFidelitySummary(mean_ocr_confidence=None, character_level_fidelity_estimate=None, pages_with_warnings=sum(1 for cu in content_units if cu.text_fidelity.warnings), total_pages=len(content_units))`
   - `verse_detection` = any(page.has_verse for page in cleaned)
   - `total_content_units` = len(content_units)
   - `quality_report` = computed (see below)
   - `normalization_warnings` = empty list `[]` (pipeline-level warnings are logged via error codes, not aggregated into manifest in core build)
   - Deferred optional fields = None: `content_census`, `tahqiq_topology`, `layer_fingerprints`, `discourse_flow_summary`, `structural_format_proposed`, `verse_numbering_scheme`

7. **Compute `QualityReport`:**
   - `division_count_by_tier` = div_counts from Pass 4
   - `layer_transition_count` = total within-page layer type changes across all segments (for each page's segment list, count consecutive pairs where `segments[j].layer_type != segments[j+1].layer_type`; sum across all pages. A single-layer page contributes 0. Blank pages contribute 0.)
   - `pages_with_warnings` = count of `CleanedPage` objects with non-empty `.warnings` list (normalization-level warnings like orphan refs — NOT `TextFidelity.warnings` which are always empty for Shamela)
   - `high_fidelity_pct` = 1.0 (Shamela = always high)
   - `unclassified_footnote_count` = count of footnotes with type UNKNOWN
   - `overall_confidence` = struct_confidence from Pass 4

8. **Return `NormalizedPackage(manifest=manifest, content_units=content_units)`.**

**Tests for assembly:** 7+ tests. **Fixture paths for `normalize(frozen_path, metadata)`:** ibn_aqil → `Path("engines/normalization/tests/fixtures/shamela_ibn_aqil.htm")` (single file). 01_nahw_simple → `Path("tests/fixtures/shamela_real/01_nahw_simple")` (directory, contains `book.htm`). Both work with `_resolve_input_files`.
- Full pipeline test on ibn_aqil fixture: construct metadata with `is_multi_layer=True`, `text_layers=[matn+sharh]`, `structural_format="prose"`, `source_format="shamela_html"`. Run normalize() end-to-end. Verify it returns a NormalizedPackage (not raises NotImplementedError). Verify content_units count matches expected pages (5). Verify each content_unit has full coverage text_layers.
- Full pipeline test on 01_nahw_simple (single-layer, 73 pages): construct metadata with `is_multi_layer=False`, `structural_format="prose"`, `source_format="shamela_html"`. Verify all content_units are MATN at confidence 1.0.
- Spot-check footnote conversion on a fixture with footnotes. Verify `ref_marker` is a string (not int), `footnote_type` is a valid `FootnoteType` enum member, `confidence` is a float.
- Verify manifest fields are populated correctly: `normalizer_id`, `structural_format`, `total_content_units`, `text_fidelity_summary.total_pages`, `normalization_warnings` is a list, all deferred Optional fields are None.
- Verify boundary_continuity is None for the last content_unit.
- Verify blank/image-only pages have `boundary_continuity=None` and `content_flags.is_blank=True`.
- Verify `quality_report.division_count_by_tier` matches Pass 4 output.

---

## Design Decisions (pre-resolved — do NOT defer)

**D1: Deferred Pass 6 enrichment steps.** Steps 2-6 and 8-11 from SPEC §4.A.2 Pass 6 overview are DEFERRED per CORE_EXTRACTION.md. Set the corresponding manifest fields to `None`: `content_census`, `tahqiq_topology`, `layer_fingerprints`, `discourse_flow_summary`, `structural_format_proposed`. Set `discourse_flow` to `None` on every ContentUnit. This is correct — these are all `Optional` fields.

**D2: `verse_info` field.** The `VerseInfo` contract type exists but verse line/hemistich parsing is not implemented (only `has_verse` boolean from Pass 3). Set `verse_info = None` on all ContentUnits. `has_verse` in `content_flags` is the surface-level signal.

**D3: TOC page indices threading.** Update `from dataclasses import dataclass` to `from dataclasses import dataclass, field` in `structure_discovery.py`. Add `toc_page_indices: list[int] = field(default_factory=list)` to `StructureResult` (line 99). Update `discover_structure()` to populate it from the existing `toc_indices` local variable (line 1165): set `toc_page_indices=toc_indices` in the `StructureResult(...)` constructor at line 1207. Update `_pass4_discover_structure()` in `shamela.py` to return `toc_page_indices` as a fifth element. Update the call site at `normalize()` line 488 to unpack 5 values: `_division_tree, _page_markers, div_counts, struct_confidence, toc_indices = ...`. Pass `set(toc_indices)` to the content flagger. This is a backwards-compatible addition (default empty list).

**D4: Index page detection.** Index pages (فهرس الأعلام, فهرس الأحاديث) are distinct from TOC pages (فهرس الموضوعات). Detect by keyword match in first 200 chars of primary_text. If no fixture has index pages, test with constructed text only.

**D5: Blank/image-only page assembly.** Blank and image-only pages still produce ContentUnits (SPEC completeness rule). They get: empty primary_text, empty text_layers, content_flags.is_blank=True, boundary_continuity=None (no text to analyze).

**D6: `TextFidelityLevel` for Shamela.** All Shamela pages get `TextFidelityLevel.HIGH`. This is hardcoded — Shamela is digital-born text, not OCR.

**D7: Conditional reasoning markers excluded.** The SPEC §4.B.8 argument marker table lists conditional reasoning openers: `إذا`, `ولو أن`, `فإن كان`. Empirical testing on real fixtures shows `إذا` appears in the last 200 chars of 15-19% of pages — it's a common Arabic word meaning "if/when," not a reliable argument marker. `ولو أن` and `فإن كان` are similarly common. Exclude all three from the initial implementation. Document as L-008 in KNOWN_LIMITATIONS.md. The conditional reasoning closers (`وإلا`, `فحينئذ`, `فالحكم`) are also excluded since they have no openers. Fix point: add these markers with additional context requirements (sentence-initial position, specific syntactic patterns) when real mid-argument false negative data is available.

**D8: Guillemet hadith distance heuristic.** The `«...»` guillemet + `قال` within 50 chars hadith detection pattern is a design decision, not a SPEC-mandated value. The SPEC §4.A.9 says "hadith citation patterns detected" without specifying a character distance. 50 chars is a reasonable heuristic — typical hadith introductions (`عن فلان قال: قال رسول الله ﷺ: «...»`) fit within ~40 chars between `قال` and the opening guillemet. If empirical testing shows 50 is too tight (missing valid hadith with longer isnads), increase to 80. Document in KNOWN_LIMITATIONS.md as L-009 if adjusted.

---

## Do NOT Do

- Do NOT implement §5 validation checks (Session 6).
- Do NOT implement the atomic disk writer (Session 6).
- Do NOT implement plain text normalizer (Session 6).
- Do NOT implement discourse_flow, content_census, tahqiq_topology, layer_fingerprints, structural_format auto-detection, or fine-grained footnote classification. All deferred per CORE_EXTRACTION.md.
- Do NOT change any existing Pass 1-5 logic. Pass 6 is additive only.
- Do NOT add new error codes — the existing `CONTINUITY_INCONSISTENT` and `CONTINUITY_UNKNOWN` are sufficient.

---

## Verification

```bash
# All tests pass (existing + new)
python -m pytest engines/normalization/tests/ -v

# Cross-engine contracts still consistent
python tools/check_cross_engine_contracts.py

# Full pipeline runs without NotImplementedError
python -c "
from engines.normalization.src.normalizers.shamela import ShamelaNormalizer
from pathlib import Path
# ... (construct metadata, run normalize(), print summary)
"
```

**Pass criteria:**
- 173 existing tests still pass (zero regressions)
- 32+ new tests pass (content_flagger ~10, boundary_continuity ~15, assembly ~7)
- Cross-engine contracts: PASS
- `normalize()` returns a `NormalizedPackage` for ibn_aqil fixture
- Every `ContentUnit` has full text_layer coverage (start=0, end=len(primary_text))
- Content flags on `05_tafsir` pages detect Quran citations
- SPEC §4.A.9 and §4.B.8 concrete examples traced through implementation
- ADV-026-inspired test passes (classifier never produces `mid_sentence` when terminal punctuation is present — the classifier itself should return `mid_paragraph`. The §5 post-hoc validation check is Session 6.)
- ADV-024/050/051 tests pass (non-standard Quran/hadith patterns, TOC detection)

---

## After This

**Post-build sequence (3 steps before Session 6):**

1. **Build Prober** — Owner starts a new CC session: "Run the Build Prober on Session 5. Agent: `.claude/agents/build-prober.md`. Engine: normalization. Git range: from the last commit before Session 5 to HEAD." The Build Prober maps every new function to a SPEC rule and flags deviations, improvisations, and omissions. Its report feeds the architect review.

2. **Architect review** — New Claude Chat session using kr-reviewing-cc-output (3-round protocol: Pass 1 structural, Pass 2 adversarial with SPEC example traces, Pass 3 self-verification + verdict). Build Prober report is available as input.

3. **Session 6** — §5 validation checks 1-10 + atomic writer + plain text normalizer.

**Agent architecture deviation (documented):** AGENT_ARCHITECTURE.md §2.2 prescribes test-engineer, code-reviewer, and boundary-validator as CC sub-agents during BUILD. Sessions 1–4 built successfully without sub-agents — the architect's 3-round review protocol serves the same function as code-reviewer, and tests are written alongside implementation (satisfying the test-engineer role). Sub-agent invocation will be evaluated during Probe 2 (Build Team) on a future engine. For the normalization engine build, the existing architect-supervised workflow continues.
