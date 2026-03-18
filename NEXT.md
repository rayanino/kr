# NEXT — Build Session 3: Structure Discovery (Pass 4)

## Current position: Session 2 COMPLETE and ACCEPTED (commit 6a882ca). Shamela Passes 1–3 implemented: 1,115 lines shamela.py, 724 lines contracts.py, 130 lines errors.py, 56 lines base.py. 106 tests passing, 22 skipped. All 10 ADV-001–010 pass. 13 real fixtures + 1 hand-crafted (ibn_aqil) parse successfully. 4,160 pages/sec on 1,720-page multi-volume.
## What to do: Implement Pass 4 — Structure Discovery. New module `structure_discovery.py` implementing 4-tier heading detection + division tree construction. Called from `shamela.py._pass4_discover_structure()`.
## Context: Pass 4 consumes `CleanedPage` output from Session 2 (title_spans, starts_with_zwnj_heading, primary_text, unit_index) and produces: (a) per-page `StructuralMarkers` (heading_detected, heading_text, heading_level, detection_method, confidence) for each content unit, and (b) the manifest-level `division_tree` (nested `DivisionNode` array) + `QualityReport.division_count_by_tier` and `overall_confidence`. The ABD `discover_structure.py` (2,896 lines) provides behavioral reference but uses different data structures — KR's `DivisionNode` has 9 fields (not ABD's ~18), nested `children` (not flat parent_id/child_ids), and follows SPEC §4.A.6 thresholds (not ABD's different ones).
## Owner action needed: YES after — to give Session 3 handoff to CC in plan mode, then implementation.

---

## Read First (in this order)

1. `engines/normalization/CLAUDE.md` (104L) — Engine orientation. Session 3 row: "Structure discovery (4-tier headings, division tree) | §4.A.6, structural_patterns.yaml". Module map shows `src/structure_discovery.py` as a separate module.

2. `engines/normalization/SPEC.md` lines 200–207 — §4.A.2 Pass 4 overview. Describes 4 tiers, outputs, integration point.

3. `engines/normalization/SPEC.md` lines 564–616 — §4.A.6 complete structure discovery specification. Behavioral authority for: division tree format, heading text rules, 4-tier confidence architecture, TOC cross-referencing, hierarchy inference rules, structure confidence scoring, concrete example. **This is the law — when ABD code disagrees with this, SPEC wins.**

4. `engines/normalization/SPEC.md` lines 1488–1492 — §5 check 5 division tree validity. Four invariants that `_check_division_tree()` will enforce (Session 6 implementation). Pass 4 must produce trees that satisfy these invariants NOW.

5. `engines/normalization/contracts.py` — Read these specific types:
   - `HeadingConfidence` enum (lines 42–47): `CONFIRMED`, `HIGH`, `MEDIUM`, `LOW`
   - `HeadingDetectionMethod` enum (lines 50–57): `HTML_TAGGED`, `KEYWORD_HEURISTIC`, `LLM_DISCOVERED`, `TOC_INFERRED`, `HUMAN_OVERRIDE`, `LAYOUT_DETECTED`
   - `StructuralMarkers` (lines 189–196): 5 fields, all Optional with defaults. One heading per content unit.
   - `DivisionNode` (lines 483–495): 9 fields. Nested `children: list[DivisionNode]`.
   - `DivisionType` enum (lines 466–480): 13 values including Arabic structural types.
   - `QualityReport` (lines 528–539): `division_count_by_tier` dict, `overall_confidence`.
   - `NormalizedManifest.division_tree` (line 670): `list[DivisionNode]`, top-level divisions.

6. `engines/normalization/reference/structural_patterns.yaml` (340L) — Arabic heading keyword patterns. Load with PyYAML. Key sections: `keyword_patterns` (hierarchy levels), `ordinal_patterns`, `hierarchy_rules`, `inline_division_patterns`. This file drives Tier 2 keyword detection.

7. `engines/normalization/src/normalizers/shamela.py` (1,104L) — Session 2 implementation. Read `CleanedPage` class (lines 229–259) for available fields. Read `normalize()` method (lines 460–489) for the integration point — Pass 4 replaces the `NotImplementedError` at line 484. Pass 4 receives `list[CleanedPage]` and `metadata: SourceMetadata`.

8. `reference/archive/abd_code/normalization/discover_structure.py` (2,896L) — ABD behavioral reference. Read SELECTIVELY (it's huge):
   - `HeadingCandidate` dataclass (lines 78–93) — internal intermediate structure
   - `CITATION_PREFIXES` (lines 66–71) — prevents false positive keyword detection
   - `pass1_extract_html_headings()` (lines 271–392) — Tier 1 logic. BUT: KR doesn't re-parse HTML; it uses `CleanedPage.title_spans` already extracted by Session 2. Study the dedup and ordering logic, not the HTML parsing.
   - `pass1_5_parse_toc()` (lines 404–478) — TOC dot-leader parsing.
   - `pass2_keyword_scan()` (lines 496–667) — Tier 2 keyword detection. Core algorithm to adapt. Study: line-start anchoring, citation prefix filtering, confidence assignment, dedup with Pass 1 headings, inline heading detection.
   - `build_hierarchical_tree()` (lines 1199–1451) — Tree construction with iterative range computation. Study: sibling range computation, parent-child containment validation, detachment of out-of-range children.
   - `compute_structure_confidence()` (lines 2203–2216) — ABD confidence uses DIFFERENT thresholds than SPEC. **USE SPEC THRESHOLDS (§4.A.6 lines 589–593), NOT ABD'S.**
   - `cross_reference_toc()` (lines 1458–1533) — TOC matching and heading promotion.
   - `normalize_arabic_for_match()` (lines 204–218) — Arabic text normalization for dedup (strip diacritics, normalize alef/ya for matching only).

9. `engines/normalization/src/errors.py` (130L) — Error codes. `NORM_SPARSE_STRUCTURE` (line 32, severity WARNING) is the relevant code for Tier 3 stub.

10. `reference/SPEC_ADVERSARY_NORMALIZATION.md` — Read ADV-016, ADV-017, ADV-018 (search for these IDs). These are mandatory tests for Session 3.

11. `engines/normalization/MUSTFIX_RESOLUTIONS.md` (121L) — MF-1 explains why `DivisionNode` has 9 fields (not ABD's ~18). Critical context for understanding field differences.

12. `engines/source/contracts.py` — `SourceMetadata` class. Pass 4 needs `source_id` (for div_id generation) and `genre` (passed through to structure discovery for future Tier 3). Already imported in shamela.py from Session 2.

---

## What to Build

### Deliverable 1: `engines/normalization/src/structure_discovery.py` — New module

The core structure discovery logic. Called from `shamela.py` but designed to be normalizer-agnostic in its tree-building and hierarchy inference (keyword detection is Shamela-specific).

**Internal data structure** (not in contracts.py — internal to this module):

```python
@dataclass
class HeadingCandidate:
    """Intermediate heading found by Tier 1, 1.5, or 2. Not exported."""
    heading_text: str
    unit_index: int
    detection_method: HeadingDetectionMethod  # from contracts.py enum
    confidence: HeadingConfidence  # from contracts.py enum
    keyword_type: Optional[DivisionType] = None  # parsed structural type
    keyword_raw: Optional[str] = None  # raw keyword from yaml (for non-enum types like تقسيم)
    ordinal: Optional[int] = None
    heading_level: Optional[int] = None  # assigned by _infer_hierarchy (1–10)
    document_position: int = 0  # ordering within same page (0, 1, 2...)
    is_inline: bool = False
```

**Functions to implement:**

1. `discover_structure(pages: list[CleanedPage], source_id: str, genre: Genre) -> StructureResult`
   - Orchestrator. Calls Tier 1 → Tier 1.5 → Tier 2 → dedup → hierarchy inference → tree construction → confidence scoring.
   - Returns a `StructureResult` (internal dataclass) containing: `division_tree: list[DivisionNode]`, `page_markers: dict[int, StructuralMarkers]` (keyed by unit_index), `quality_counts: dict[str, int]` (division count by tier for QualityReport), `overall_confidence: HeadingConfidence`.
   - Import `Genre` from `engines.source.contracts`.

2. `_tier1_html_tagged(pages: list[CleanedPage]) -> tuple[list[HeadingCandidate], list[int]]`
   - Extracts headings from `CleanedPage.title_spans`. Each title_span → one HeadingCandidate with `method=HTML_TAGGED`, `confidence=CONFIRMED`.
   - **CRITICAL: Strip leading ZWNJ (U+200C) from title_span text.** Session 2's Pass 1 decoded `&#8204;` entities to U+200C characters. Title spans like `\u200cالباب الأول` must become `الباب الأول` in heading_text. Invisible characters in heading_text corrupt downstream display and matching. Empirically verified: 07_balagha fixture title_spans start with U+200C.
   - Multiple title_spans per page → multiple candidates with same unit_index but incrementing document_position.
   - Detect TOC headings by exact match against فهرس/فهرس الموضوعات/المحتويات/etc. (see ABD `toc_exact_titles` set, line 368). Return TOC page unit_indices as second element.
   - Parse `keyword_type` from heading text (does it start with باب, فصل, etc.?). Also store raw keyword in `keyword_raw` for non-enum types.

3. `_tier1_5_toc_parse(pages: list[CleanedPage], toc_unit_indices: list[int]) -> list[TOCEntry]`
   - Parse dot-leader lines from TOC pages. Regex: `r"^(.+?)\s*[\.·…]{3,}\s*([٠-٩0-9]+)\s*$"` (verified).
   - Scan from first TOC page through up to 10 pages after last TOC page. Stop after 3 consecutive pages with no entries.
   - Return `TOCEntry` list (internal dataclass: title, page_number, indent_level).

4. `_tier1_5_toc_crossref(candidates: list[HeadingCandidate], toc_entries: list[TOCEntry], pages: list[CleanedPage]) -> list[HeadingCandidate]`
   - **Page number → unit_index mapping:** Build a dict from `{page.page_number_int: page.unit_index for page in pages if page.page_number_int is not None}`. For multi-volume books, key on `(volume, page_number_int)`. TOC page numbers may be Arabic-Indic digits — the TOC parser should output integers (use `arabic_to_int` from shamela.py for `٠-٩` digits, or `int()` for Western digits). When looking up a TOC page number, find the nearest `page_number_int` match if exact match is missing (page number gaps are common — 29.8% of Shamela has non-sequential numbering).
   - Match TOC entries to existing candidates by fuzzy title comparison (study ABD `_toc_match_score`, line 1534).
   - Matching entries: promote confidence to HIGH if currently MEDIUM.
   - Unmatched TOC entries: create new HeadingCandidate with `method=TOC_INFERRED`, `confidence=MEDIUM`, at the unit_index from the page number lookup.

5. `_tier2_keyword_scan(pages: list[CleanedPage], tier1_headings: list[HeadingCandidate]) -> list[HeadingCandidate]`
   - Load keyword patterns from `structural_patterns.yaml` (path: `engines/normalization/reference/structural_patterns.yaml`).
   - **YAML loading:** Study ABD `load_ordinals()` (line 220) and `load_keywords()` (line 232) for correct parsing. Ordinals use `|`-separated variants (`الأوَّل|الأول`) → split on `|`, map each variant to its ordinal integer (1-indexed by list position). Keywords span 4 hierarchy levels (`top_level`, `mid_level`, `low_level`, `supplementary`) with `keyword`, `definite_form`, `plural`, `dual` fields per entry. Build both dicts once and pass to the scan function.
   - For each page, scan each line of `primary_text` for keyword matches.
   - **Keyword regex:** `r"^(kw1|kw2|...)(?=[\s:؛\-–—]|$)"` anchored to line start, lookahead for word boundary (verified).
   - **Include both indefinite AND definite forms** (باب AND الباب, فصل AND الفصل, etc.). Build keyword list from `structural_patterns.yaml` entries.
   - **Plural/dual form mapping:** تنبيهات/تنبيهان → DivisionType.TANBIH, فوائد → DivisionType.FAIDAH, قواعد → DivisionType.QAIDAH, حواشي → None (layer marker, see below).
   - **EXCLUDE layer markers from Tier 2 heading detection:** حاشية, حواشي, شرح, الشرح are commentary LAYER markers, not structural divisions (yaml notes: "NOT a structural division in the same sense as باب/فصل — it's a commentary layer marker"). Do NOT detect these as headings. They are handled by Pass 5 (layer detection, Session 4).
   - **EXCLUDE supplementary non-structural markers:** تقاريظ (reviews), خطبة (rhetorical dedication). These may be flagged for `content_flags` (Session 5) but are not structural divisions.
   - **Indefinite كتاب strictness** (ABD STRICT_INDEFINITE pattern, line 554): Indefinite كتاب (without ال prefix) is a common Arabic noun. Only treat it as a heading if: (a) it has an ordinal (كتاب الأول), OR (b) the line is very short (≤ 20 chars). Without either signal, skip — it's likely a reference ("في كتاب كذا"), not a heading.
   - **Non-enum keywords:** تقسيم, مدخل, إعراب, مسألة, فرع, تتمة are valid structural keywords from the yaml but have no `DivisionType` enum value. Detect them with `keyword_type=None` and `keyword_raw="تقسيم"` (etc.). The hierarchy inference uses `keyword_raw` to assign levels.
   - **ZWNJ detection:** If a line starts with `\u200c\u200c` (double ZWNJ), strip the ZWNJ prefix and check the remaining text for keyword match. Confidence = HIGH for ZWNJ-prefixed keywords.
   - **Citation prefix filtering:** Before accepting a keyword match, check the PRECEDING line's tail (last 40 chars) for citation prefixes: `["قال في", "ذكر في", "كما في", "انظر", "ارجع إلى", "راجع", "في كتاب", "في باب", "في فصل", "ورد في", "جاء في", "نقل في"]`. Skip if found. (See ABD lines 626–638.)
   - **TOC line rejection:** Skip lines matching dot-leader pattern (verified regex).
   - **Confidence assignment** (follow ABD logic, lines 588–626):
     - KEYWORD + ORDINAL + `:` or `؛` → HIGH (max 120 chars)
     - KEYWORD + ORDINAL alone → HIGH (max 60 chars)
     - KEYWORD + ORDINAL + TITLE → HIGH (max 120 chars)
     - KEYWORD + `:` or `في` → MEDIUM (max 100 chars)
     - KEYWORD alone → MEDIUM (max 30 chars)
     - KEYWORD + `-` or `:` + content → MEDIUM, inline=True (max 400 chars)
   - **Dedup with Tier 1:** Build index of `(unit_index, normalized_title_prefix[:30])` from Tier 1 headings. Skip any Tier 2 match that collides. This prevents ADV-018 (duplicate heading).

6. `_tier3_llm_discover(candidates, genre, existing_headings, text_windows) -> list[HeadingCandidate]`
   - **STUB ONLY.** Raise `NotImplementedError("Tier 3 LLM structure discovery")`.
   - **Trigger condition:** Check BEFORE raising: if total candidates < `structure_llm_threshold` (default 3) AND total pages >= `structure_min_pages_for_llm` (default 50), log `NORM_SPARSE_STRUCTURE` warning with page count and candidate count. Then raise.
   - **NOTE: SPEC line 578 says "100+ pages" but §4.A.2 line 205 and the §8 config table (line 1618) say 50 pages. The config table is authoritative — use 50.**
   - The calling code must catch `NotImplementedError` and continue with Tiers 1-2 results only.

7. `_infer_hierarchy(candidates: list[HeadingCandidate]) -> list[HeadingCandidate]`
   - Assign `heading_level` (1–10) to each candidate based on keyword_type and keyword_raw. Modifies candidates in place (sets heading_level field).
   - **Complete level assignment table** (covers ALL yaml keywords):
     ```
     Level 0: volume (المجلد, الجزء) — created by volume detection, not keyword scan
     Level 1: كتاب / الكتاب
     Level 2: باب / الباب
     Level 3: فصل / الفصل, تقسيم / التقسيم
     Level 4: مبحث / المبحث, مدخل / المدخل, إعراب / الإعراب
     Level 5: مطلب / المطلب, مسألة / المسألة, فرع / الفرع
     Level 6: فائدة / فوائد, تنبيه / تنبيهات / تنبيهان, قاعدة / قواعد, تتمة
     Level 2: مقدمة (at book start, before any كتاب/باب) OR same level as preceding division (within a section)
     Level same-as-surrounding: خاتمة — same level as the divisions it concludes
     ```
     Use `keyword_type` (DivisionType enum) when available. Fall back to `keyword_raw` for non-enum types.
   - **Volume boundary detection (F-9):** Before keyword-based hierarchy, scan candidates by unit_index order. When `CleanedPage.volume` changes between consecutive pages, insert a synthetic HeadingCandidate with `keyword_type=DivisionType.VOLUME`, `heading_level=0`, `confidence=CONFIRMED`, `detection_method=HTML_TAGGED`, `heading_text=f"المجلد {volume_number}"`. Insert at the unit_index of the first page of the new volume.
   - Ordinal sequences are siblings (SPEC §4.A.6 line 585): consecutive candidates with same keyword_type and sequential ordinals → same level.
   - `implicit` (no keyword match) → assign level based on these rules IN ORDER:
     1. If the heading is between two headings of the same level, assign that level (it's a sibling).
     2. If the heading follows a heading of level N and precedes a heading of level N+1, assign level N (it's a section at the same level).
     3. If none of the above apply, assign level = (deepest level seen so far + 1), capped at 10.
     4. Fallback: level 3 (generic mid-level).
   - HTML_TAGGED headings without keyword match: same rules as `implicit` above.
   - **Post-condition:** After _infer_hierarchy completes, assert ALL candidates have `heading_level is not None`. Any candidate still at None → set `heading_level = 3` (mid-level fallback) and log a warning. This prevents a Pydantic validation crash in DivisionNode (heading_level has `ge=1, le=10` constraint — None would fail).

8. `_build_division_tree(candidates: list[HeadingCandidate], total_pages: int, source_id: str) -> list[DivisionNode]`
   - Sort candidates by (unit_index, document_position).
   - Dedup exact duplicates: same (unit_index, normalized_title_prefix[:40]).
   - Build tree using heading_level: lower level = parent, same level = sibling.
   - **Page range computation** (critical — study ABD `_compute_sibling_ranges`, lines 1352–1370):
     - Siblings: each runs from its start_unit_index to (next sibling's start - 1). Last sibling extends to parent's end.
     - Root nodes: last root extends to total_pages - 1.
     - **Iterative containment enforcement**: After computing ranges, verify children are within parent bounds. Detach any child whose start falls outside parent range. Recompute. Repeat up to 5 iterations until stable.
     - Hard invariant: `end_unit_index >= start_unit_index` always.
   - **Same-page sibling resolution:** If two candidates at the same heading_level share the same unit_index (two headings on one page at the same level), the second one becomes a CHILD of the first rather than a sibling. This prevents sibling overlap at the shared page (§5 check 5 violation). Empirically 0 occurrences across all 13 fixtures, but must be handled.
   - **Full coverage enforcement (§5 check 5):** After computing ranges, if the first root-level division's `start_unit_index > 0`, extend it to 0. This ensures pages before the first heading are covered. The SPEC concrete example (line 609) shows `start_unit_index: 0` confirming this behavior. Without this fix, pages 0 through (first_heading - 1) would violate §5 check 5 ("the tree covers the entire source").
   - Generate `div_id` in format `div_{source_id}_{depth}_{running_index}` where depth = heading_level, running_index = zero-padded sequential within that depth.
   - Map `keyword_type` → `DivisionType` enum value. `None` if no keyword match (including non-enum keywords like تقسيم — they get `division_type=None` per SPEC §4.A.6 line 568).
   - Return `list[DivisionNode]` — top-level nodes with nested children.
   - **Zero-heading fallback:** If after all tiers produce zero candidates, create a single ROOT DivisionNode: `div_id=f"div_{source_id}_0_000"`, `division_type=DivisionType.ROOT`, `heading_text="[untitled]"`, `heading_level=1`, `start_unit_index=0`, `end_unit_index=total_pages-1`, `detection_method=HeadingDetectionMethod.KEYWORD_HEURISTIC`, `confidence=HeadingConfidence.LOW`, `children=[]`. This satisfies §5 check 5 (full coverage). Fixture 13_format_b (0 title spans, 1 page) will exercise this path.

9. `_compute_confidence(divisions: list[DivisionNode], total_pages: int) -> HeadingConfidence`
   - **Use SPEC thresholds** (§4.A.6 lines 589–593), NOT ABD's:
     - Count "high-confidence" divisions: those with confidence CONFIRMED or HIGH.
     - Ratio = high_confidence_count / total_division_count.
     - ratio > 0.80 → HeadingConfidence.HIGH (overall)
     - 0.50 <= ratio <= 0.80 → HeadingConfidence.MEDIUM
     - ratio < 0.50 → HeadingConfidence.LOW
     - total divisions < 3 AND total_pages >= 50 → HeadingConfidence.MINIMAL (log NORM_SPARSE_STRUCTURE)
     - total divisions == 0 → HeadingConfidence.MINIMAL (regardless of page count)
     - total divisions == 1 AND that division is a ROOT fallback node → HeadingConfidence.MINIMAL

10. `_build_page_markers(candidates: list[HeadingCandidate]) -> dict[int, StructuralMarkers]`
    - Group candidates by unit_index.
    - For each page with >= 1 candidate: create `StructuralMarkers` from the FIRST candidate (lowest document_position) on that page.
    - `heading_detected=True`, `heading_text=candidate.heading_text`, `heading_level=candidate.heading_level`, `heading_detection_method=candidate.detection_method`, `heading_confidence=candidate.confidence`.

11. `normalize_arabic_for_match(text: str) -> str`
    - Strip diacritics (U+064B–U+0655 inclusive — covers harakat, tanwin, sukun, shadda, maddah above, hamza above, hamza below; also U+0670 superscript alef), strip tatweel/kashida (U+0640), normalize alef forms (أ/إ/آ/ٱ → ا), normalize ya (ى → ي), strip ZWNJ (U+200C)/ZWJ (U+200D), collapse whitespace. For matching/dedup only — never applied to stored text. Study ABD `normalize_arabic_for_match()` (line 204) which covers the same range.

### Deliverable 2: Integration in `shamela.py`

1. Add `_pass4_discover_structure(self, cleaned: list[CleanedPage], metadata: SourceMetadata) -> tuple[list[DivisionNode], dict[int, StructuralMarkers], dict[str, int], HeadingConfidence]`
   - Calls `structure_discovery.discover_structure()`.
   - Returns (division_tree, page_markers, division_count_by_tier, overall_confidence).

2. Update `normalize()` method (line 484): Replace `NotImplementedError` with Pass 4 call. Wire results into a local variable for use by Passes 5–6 (still NotImplementedError after Pass 4).
   ```python
   # Pass 4: Structure discovery
   division_tree, page_markers, div_counts, struct_confidence = \
       self._pass4_discover_structure(cleaned, metadata)

   # Passes 5–6: NOT YET IMPLEMENTED (Sessions 4–5)
   raise NotImplementedError(
       "Passes 5–6 not yet implemented. "
       f"Pass 4 discovered {sum(div_counts.values())} divisions "
       f"({struct_confidence.value} confidence) "
       f"from {len(cleaned)} pages."
   )
   ```

### Deliverable 3: Tests — `engines/normalization/tests/test_structure_discovery.py`

**Test strategy:** Use real fixtures to test end-to-end structure discovery. Pass fixtures through Passes 1–3 first (call the existing normalizer methods), then pass the `list[CleanedPage]` to Pass 4.

**Mandatory tests:**

1. **ADV-016 (arabic_trap):** Construct a `CleanedPage` where `primary_text` contains "باب" mid-line in a scholar name. Assert `heading_detected == False` for that page.

2. **ADV-017 (tree_validity):** After building a division tree from any real fixture, verify ALL four §5 check 5 invariants:
   - Every node: `start_unit_index <= end_unit_index`
   - Siblings: no overlapping page ranges
   - Children: contained within parent's range
   - Coverage: no unit_index gaps (every page is inside at least one division)

3. **ADV-018 (dedup):** Construct a `CleanedPage` where `title_spans=["باب الطهارة"]` AND `primary_text` starts with `باب الطهارة`. Assert exactly ONE DivisionNode with `detection_method=HTML_TAGGED`, not two.

4. **Real fixture: 07_balagha** — Run Passes 1–4 on the balagha fixture. Verify:
   - `division_tree` is non-empty
   - All DivisionNodes have valid `div_id` format
   - `overall_confidence` is `CONFIRMED` or `HIGH` (this book has 146+ Tier 1 headings)
   - Pages with multiple `title_spans` (33 pages) don't produce duplicate nodes

5. **Real fixture: 01_nahw_simple** — A simpler book. Verify basic tree structure.

6. **Multi-volume: 12_multi_muq** — Verify volume boundary handling.

7. **Keyword detection basics:** Construct pages with known keyword lines. Verify correct `DivisionType` assignment, confidence levels, and ordinal detection.

8. **Citation prefix rejection:** Construct a page with "كما في باب الصلاة" (citation, not heading). Assert no heading detected.

9. **ZWNJ heading detection:** Construct a page with `primary_text` starting with `\u200c\u200cباب الوضوء`. Assert heading detected with confidence HIGH.

10. **TOC detection and parsing:** If any fixture has a TOC (check the last few pages for فهرس/المحتويات in title_spans), verify TOC entries are parsed. If no fixture has TOC, construct a synthetic one.

11. **Empty/minimal books:** Verify that a book with <3 headings and >= 50 pages triggers `NORM_SPARSE_STRUCTURE` warning (Tier 3 stub path).

12. **Confidence scoring thresholds:** Parameterized test with known heading distributions verifying SPEC thresholds (>80% = HIGH, 50-80% = MEDIUM, <50% = LOW).

13. **ZWNJ stripping from title_spans (F-2):** Construct a page with `title_spans=["\u200cالباب الأول"]`. Assert the resulting DivisionNode has `heading_text="الباب الأول"` (no ZWNJ prefix). Assert StructuralMarkers.heading_text also lacks ZWNJ.

14. **Full coverage — pages before first heading (F-3):** Construct 20 pages where the first heading is at page 5. Assert the first root division's `start_unit_index == 0` (not 5). All pages 0-19 must be inside at least one division.

15. **Non-enum keyword detection:** Construct a page with `primary_text` starting with `التقسيم الأول`. Assert heading detected with `keyword_type=None`, `keyword_raw="تقسيم"`, `heading_level=3`.

16. **Layer marker exclusion:** Construct a page with `primary_text` starting with `حاشية` or `شرح`. Assert `heading_detected == False` (these are layer markers, not structural headings).

17. **Volume boundary detection:** Construct pages with volume changing from 1 to 2 at page 10. Assert a volume-level DivisionNode exists at page 10 with `division_type=VOLUME`, `heading_level=0`.

18. **Zero-heading fallback (F-12):** Run structure discovery on fixture 13_format_b (0 title spans, 1 page). Assert: division_tree has exactly 1 ROOT node covering page 0, `overall_confidence` is `MINIMAL`, and §5 check 5 invariants still hold.

19. **Heading level None guard (F-14):** Construct an HTML_TAGGED heading with text that matches no keyword (e.g., a scholar name used as a section title). Assert heading_level is assigned (not None) and DivisionNode construction succeeds without Pydantic validation error.

---

## Critical Design Decisions (already made — implement as specified)

### D1: StructuralMarkers records ONE heading per page
`StructuralMarkers` has singular fields (one heading_text, one heading_level, etc.). When a page has multiple headings (11.5% of balagha fixture has 2-4 title_spans per page), `StructuralMarkers` records the FIRST heading (lowest document_position). The division tree records ALL headings — it is the complete record. This matches the contract.

### D2: pagehead_text is NOT a heading source
`CleanedPage.pagehead_text` is Shamela navigation metadata (the current chapter label), not a new heading detection. It persists across consecutive pages in the same section. Do NOT use `pagehead_text` to set `heading_detected = True`. Only `title_spans` (Tier 1) and keyword/ZWNJ matches in `primary_text` (Tier 2) create headings.

### D3: Tier 3 is a stub with clean interface
Tier 3 raises `NotImplementedError`. The calling code catches it and continues with Tiers 1–2 results. Log `NORM_SPARSE_STRUCTURE` when the trigger condition is met (< 3 headings in >= 50 pages).

### D4: Tier 1.5 TOC — implement detection + parsing + basic cross-referencing
TOC pages are detected from `title_spans` matching exact titles (فهرس, فهرس الموضوعات, المحتويات, etc.). Entries are parsed via dot-leader regex. Cross-referencing promotes matching headings and creates new TOC_INFERRED candidates. Follow ABD code structure.

### D5: SPEC thresholds override ABD thresholds
ABD `compute_structure_confidence` uses 70%/30% thresholds and only counts `html_tagged`. SPEC §4.A.6 uses 80%/50% thresholds and counts both `CONFIRMED` and `HIGH`. **Follow SPEC.**

### D6: Keyword list includes both indefinite and definite forms
Load keywords from `structural_patterns.yaml` and also include definite forms (الباب, الفصل, المبحث, etc.). The yaml file has both forms documented. Build regex dynamically from yaml entries.

---

## Do NOT Do

- **Do NOT modify Passes 1–3 code** in shamela.py except to add the Pass 4 integration call in `normalize()`.
- **Do NOT modify contracts.py** unless a genuine gap is discovered (the 9-field DivisionNode and StructuralMarkers are sufficient).
  - **EXCEPTION (genuine gap): Add `MINIMAL = "minimal"` to `HeadingConfidence` enum.** SPEC §4.A.6 lines 589-593 defines four structure confidence levels: high, medium, low, minimal. The passaging SPEC (line 460) reads `structure_confidence: "minimal"` to trigger implicit structure discovery. The current enum has CONFIRMED/HIGH/MEDIUM/LOW — no MINIMAL. `QualityReport.overall_confidence` is typed as `HeadingConfidence` and must be able to represent this value. Add the enum value; it's a one-line additive change with zero risk.
- **Do NOT implement Pass 5 (layer detection)** or Pass 6 (output assembly).
- **Do NOT implement §5 validation checks** — those are Session 6. But DO ensure your output would pass §5 check 5.
- **Do NOT implement content_flags detection** — that is Session 5.
- **Do NOT implement the Tier 3 LLM** — stub only.
- **Do NOT apply Unicode normalization (NFC/NFD) to Arabic text.** The `normalize_arabic_for_match()` function is for matching/dedup only, never stored text.
- **Do NOT use ABD's `DivisionNode` fields** (parent_id, child_ids, digestible, editor_inserted, etc.). Use KR's `DivisionNode` from contracts.py (9 fields, nested children).
- **Do NOT re-parse the HTML file** for Tier 1. Session 2 already extracted `title_spans`. Use those.

---

## Verification

### Pass criteria (all must be true):

1. `pytest engines/normalization/tests/ -v` — ALL tests pass (existing + new), zero failures.
2. ADV-016, ADV-017, ADV-018 all pass as explicit named tests.
3. Tests #13–19 (from self-review findings) all pass.
4. At least 3 real fixtures produce non-empty `division_tree` with valid tree structure.
5. `div_id` format matches `div_{source_id}_{depth}_{index}` on all nodes.
6. No `StructuralMarkers` has `heading_detected=True` with `heading_text=None` (consistency).
7. For fixture 07_balagha: `overall_confidence` is `CONFIRMED` or `HIGH`.
8. For fixture 13_format_b: `overall_confidence` is `MINIMAL`, division_tree has 1 ROOT node.
9. The `normalize()` method calls Pass 4 and reaches the new `NotImplementedError` for Passes 5–6 (not the old one for Passes 4–6).
10. `NORM_SPARSE_STRUCTURE` is logged when Tier 3 trigger condition is met.
11. `HeadingConfidence.MINIMAL` exists in contracts.py enum.

### Commands to verify:

```bash
# Run all tests
cd /path/to/kr
python -m pytest engines/normalization/tests/ -v --tb=short

# Verify structure discovery on a real fixture (quick smoke test)
python -c "
from engines.normalization.src.structure_discovery import discover_structure
# ... load fixture, call discover, print summary
"
```

---

## After This

1. **Build Prober:** After CC finishes, invoke `build-prober` agent on Session 3 diff.
2. **Architect review:** Two-pass review per `reference/protocols/REVIEW_PROTOCOL.md`:
   - Pass 1: Read every file, run all tests, SPEC cross-reference.
   - Pass 2: 3–5 interaction probes (constructed edge cases), 2–3 fixture semantic spot-checks.
3. **Cumulative metrics update** (target after Session 3):
   ```
   Implementation: ~2,900-3,400 lines (shamela.py ~1,150, structure_discovery.py ~700-900, contracts.py ~730, errors.py 130, base.py 56)
   Tests: ~2,000-2,400 lines (existing 1,274 + new ~700-1,100 for 19 test categories)
   Test count: ~150-175 passing
   ADV covered: 13/51 (ADV-001–010 + ADV-016–018)
   ```

---

## Cumulative Build Metrics (after Session 2)

```
Implementation:  2,014 lines (shamela.py 1104, contracts.py 724, errors.py 130, base.py 56)
Tests:           1,274 lines (test_shamela_passes.py 788, test_contracts.py 486)
Test count:      106 passing, 22 skipped (placeholders for full pipeline)
Test-to-code:    0.63 ratio, 5.2 tests per 100 impl lines
ADV covered:     10/51 (ADV-001 through ADV-010, Passes 1-3)
Fixtures:        13 real + 1 hand-crafted (ibn_aqil)
Performance:     4,160 pages/sec on 1,720-page multi-volume
```

## Known Limitations (from Session 2)

See `engines/normalization/KNOWN_LIMITATIONS.md`:
- **L-001:** Bare-number and unnumbered footnotes classified but not parsed (105 pages, 3 fixtures). Fix: Session 5.
- **L-002:** ضياء السالك commentary numbering collision (1 book). Fix: Session 4 (layer detection).
