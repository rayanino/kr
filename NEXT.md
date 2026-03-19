# NEXT — Build Session 4: Multi-Layer Text Detection (Pass 5)

## Current position: Session 3 COMPLETE and ACCEPTED (commit 1452e3e + review fixes through 44b7b07). Structure discovery implemented: 1,212 lines, 19 tests, 13/13 fixtures, L-003 documented. Cumulative: 3,266 impl lines, 126 tests (including cross-engine), 13/51 ADV.
## What to do: Implement Pass 5 — Multi-Layer Text Detection. New module `layer_detector.py` implementing typographic layer detection for Shamela HTML. Called from `shamela.py._pass5_detect_layers()`.
## Context: Pass 5 determines which portions of each page's text belong to which author layer (matn/sharh/hashiyah/tahqiq_note). This is the highest-integrity-risk operation — layer misattribution means the owner studies text believing it was written by the wrong author (T-2). The SPEC calls it "a scholarly integrity violation." For single-layer sources, Pass 5 produces one TextLayerSegment per page covering all text. For multi-layer sources, it uses bold spans, transition markers, and brackets to segment text into attributed regions.
## Owner action needed: YES after — to give Session 4 handoff to CC in plan mode, then implementation.

---

## Read First (in this order)

1. `engines/normalization/CLAUDE.md` (106L) — Engine orientation. Session 4 row: "Layer detection (typographic signals for Shamela) | §4.A.5".

2. `engines/normalization/SPEC.md` lines 497–562 — §4.A.5 complete multi-layer text detection specification. Behavioral authority. Covers: layer model, detection signals (markers, typographic, content-based), detection algorithm (7 steps), conservative default, concrete example. **This is the law.**

3. `engines/normalization/SPEC.md` lines 209–217 — §4.A.2 Pass 5 overview. Shamela-specific layer signals: bold, brackets, transition phrases, font size.

4. `engines/normalization/SPEC.md` lines 118 — Layer annotation coverage rule: "every character in primary_text is covered by exactly one segment." Zero gaps, zero overlaps.

5. `engines/normalization/contracts.py` — Read these types:
   - `LayerType` enum (lines 33–39): MATN, SHARH, HASHIYAH, TAHQIQ_NOTE, UNCERTAIN
   - `TextLayerSegment` (lines 110–122): layer_type, author_canonical_id, start, end (exclusive), confidence
   - `ContentUnit.text_layers` (line 444): array, every character covered by exactly one segment
   - `LayerMapEntry` (lines 503–514): layer_type, author info, confidence, markers found
   - `NormalizedManifest.layer_map` (line 675): list of LayerMapEntry for the manifest

6. `engines/normalization/src/normalizers/shamela.py` (1,131L) — Read:
   - `CleanedPage` class (lines 229–259): `bold_spans`, `font_size_spans`, `primary_text` — these are Pass 5's inputs
   - `normalize()` method (lines 460–494): Pass 5 integration point — replaces NotImplementedError at line 488
   - `BOLD_RE` (line 82), `strip_tags`, `decode_entities`, `normalize_whitespace` — needed for bold text cleaning
   - **CRITICAL: bold_spans have (start, end, html_text) where offsets are in matn_html space, NOT primary_text space.** The html_text (3rd element) contains the raw HTML inside `<b>` tags. To map to primary_text: `strip_tags(html_text)` → `decode_entities()` → `normalize_whitespace().strip()` → `primary_text.find()`. This mapping is verified to work on ibn_aqil fixture.

7. `engines/source/contracts.py` — Read:
   - `SourceMetadata.is_multi_layer` (line 773): bool flag from source engine
   - `SourceMetadata.text_layers` (line 774): list[TextLayer] — which layers are present
   - `TextLayer` model: layer_type + ScholarReference (canonical_id, name_arabic)

8. `reference/SPEC_ADVERSARY_NORMALIZATION.md` — Search for ADV-011 through ADV-015. All 5 are mandatory tests for Session 4.

9. `engines/normalization/KNOWN_LIMITATIONS.md` (30L) — L-002 (ضياء السالك commentary numbering collision). Session 4 should address this architecturally: once layers are separated, commentary-region `(N)` markers can be distinguished from footnote refs.

10. `engines/normalization/src/errors.py` (130L) — Error codes. `NORM_LAYER_UNCERTAIN` (line 31, severity WARNING) is the relevant code for low-confidence layer detection.

---

## What to Build

### Deliverable 1: `engines/normalization/src/layer_detector.py` — New module

Replace the existing stub (1,487 bytes) with the real implementation.

**Internal data structures (not exported):**

```python
@dataclass
class LayerBoundary:
    """A detected transition between layers."""
    char_offset: int  # position in primary_text
    to_layer: LayerType
    confidence: float
    signal: str  # what triggered this: "bold", "marker:قوله", "bracket", etc.

@dataclass
class LayerDetectionResult:
    """Return type from detect_layers()."""
    segments: list[TextLayerSegment]  # full coverage, no gaps
    layer_map_entries: list[LayerMapEntry]  # for manifest
    warnings: list[str]
```

**Functions to implement:**

1. `detect_layers(page: CleanedPage, metadata: SourceMetadata) -> LayerDetectionResult`
   - Orchestrator. Dispatches to single-layer or multi-layer path.
   - **Single-layer path** (`is_multi_layer=False` AND no multi-layer signals detected): return one `TextLayerSegment` covering `[0, len(primary_text))` with `layer_type` from metadata (default MATN if no text_layers in metadata), `confidence=1.0`.
   - **Multi-layer path** (`is_multi_layer=True` OR multi-layer signals detected): run full detection algorithm.
   - **Multi-layer signal detection** (for single-layer metadata override, ADV-015): scan first 10 pages for bold spans covering >10% of text AND transition markers. If both are found, treat as multi-layer even if metadata says single-layer. Log `NORM_LAYER_UNCERTAIN` warning.

2. `_map_bold_to_primary(bold_spans: list[tuple[int, int, str]], primary_text: str) -> list[tuple[int, int]]`
   - Maps bold_span HTML text to primary_text character offsets.
   - For each bold_span IN ORDER: clean the html_text (`strip_tags` → `decode_entities` → `normalize_whitespace().strip()`), then `primary_text.find(cleaned, search_start)` to get start index. End = start + len(cleaned_text). Update `search_start = end` for next iteration.
   - **CRITICAL: Use sequential search with a running `search_start` offset.** Bold spans are extracted in document order from matn_html. If the same text appears twice in primary_text (e.g., a matn verse repeated in commentary), `find()` without a start offset returns the wrong occurrence. Sequential searching preserves positional correctness.
   - Returns list of (start, end) tuples in primary_text coordinates.
   - If a bold span can't be found in primary_text (rare edge case from cleaning differences), log a warning and skip it.

3. `_detect_transition_markers(primary_text: str) -> list[LayerBoundary]`
   - Scan primary_text for explicit transition markers (SPEC §4.A.5 signal 1).
   - Markers and their layer transitions:
     - `"قال المصنف"` / `"قال المصنف:"` → transition to MATN, confidence 0.90
     - `"قال الشارح"` / `"قال الشارح:"` → transition to SHARH, confidence 0.90
     - `"قوله:"` / `"قوله :"` → transition to MATN (quoting original text), confidence 0.85
     - `"أقول:"` / `"أقول :"` → confirms current speaker, confidence 0.80
     - `"أي:"` / `"أي :"` → transition to commentary (SHARH or HASHIYAH depending on source type), confidence 0.80
     - `"وعبارته:"` / `"ونصه:"` / `"قال في الشرح:"` → hashiyah quoting sharh (3-layer sources only), confidence 0.85
   - Return LayerBoundary for each marker found, with char_offset = position in primary_text.

4. `_detect_bracket_regions(primary_text: str) -> list[tuple[int, int]]`
   - Find `[text]` regions that are potential matn markers.
   - **Exclude short brackets** (< 15 chars between `[` and `]`) — these are typically Quran verse references like `[التحريم: 5]` or editorial insertions, NOT matn markers.
   - Return list of (start, end) character offset tuples for bracket content.

5. `_classify_bold_signal(bold_regions: list[tuple[int, int]], primary_text: str, transition_markers: list[LayerBoundary]) -> str`
   - Implements the SPEC two-factor bold classification:
   - Calculate `bold_percentage = sum(end - start for start, end in bold_regions) / len(primary_text)`.
   - If `bold_percentage < 0.05` → return `"emphasis"` (too little bold to be a layer signal).
   - If `bold_percentage > 0.60` → return `"emphasis"` (too much bold — emphasis, not layer).
   - For each bold region, apply the two-factor test: `char_count >= 80 AND no transition marker inside the span`. Both conditions met → `"layer_indicator"`. Either condition fails → `"uncertain"`.
   - If ALL bold regions pass the two-factor test → return `"layer_indicator"`.
   - If ANY bold region fails → return `"mixed"` (some bold is layer, some is emphasis).

6. `_build_segments(primary_text: str, bold_regions: list[tuple[int, int]], markers: list[LayerBoundary], brackets: list[tuple[int, int]], bold_classification: str, metadata: SourceMetadata) -> list[TextLayerSegment]`
   - The core segmentation algorithm (SPEC §4.A.5 detection algorithm steps 2–6).
   - **Step 1:** Collect all boundaries: marker positions + bold region edges + bracket edges.
   - **Step 2:** Sort boundaries by character offset.
   - **Step 3:** Between consecutive boundaries, assign the layer type based on signals:
     - Inside a bold region (when bold_classification is "layer_indicator") → MATN
     - After a `"قوله:"` marker → MATN (until next non-MATN signal)
     - After a `"قال الشارح:"` or `"أي:"` marker → SHARH (or HASHIYAH for 3-layer sources)
     - Inside brackets (when brackets qualify as layer markers) → MATN
     - Default (no signal) → the source's default commentary layer (SHARH for sharh, HASHIYAH for hashiyah)
   - **Step 4:** Fill gaps — any region between 0 and len(primary_text) not covered by a boundary assignment gets the default layer.
   - **Step 5:** Merge adjacent segments with the same layer_type.
   - **Step 6:** Validate full coverage: every character in [0, len(primary_text)) is in exactly one segment. If not → fill with UNCERTAIN at confidence 0.30.
   - Get `author_canonical_id` from `metadata.text_layers` by matching layer_type.
   - **Conservative default** (SPEC §4.A.5): When confidence < 0.50, attribute to commentary (Layer 2 in sharh, Layer 3 in hashiyah), not matn. Misattributing commentary to the commentator is less harmful than attributing verbose explanation to the matn author.

7. `_build_layer_map(segments: list[TextLayerSegment], signals_found: list[str]) -> list[LayerMapEntry]`
   - Build manifest-level layer_map from detected segments.
   - One entry per unique layer_type found.
   - markers field lists which signals were found for that layer (e.g., "bold", "قوله:", "brackets").
   - confidence = average confidence of segments for that layer type.

### Deliverable 2: Integration in `shamela.py`

1. Add `_pass5_detect_layers(self, cleaned: list[CleanedPage], metadata: SourceMetadata) -> tuple[dict[int, list[TextLayerSegment]], list[LayerMapEntry]]`
   - For each CleanedPage, calls `layer_detector.detect_layers()`.
   - Returns: `(page_layers: dict[int, list[TextLayerSegment]], layer_map: list[LayerMapEntry])`.
   - For single-layer sources, still produces one-segment-per-page output.

2. Update `normalize()` method (line 488): Replace NotImplementedError with Pass 5 call.
   ```python
   # Pass 5: Multi-layer detection
   page_layers, layer_map = self._pass5_detect_layers(cleaned, metadata)

   # Pass 6: NOT YET IMPLEMENTED (Session 5)
   raise NotImplementedError(
       "Pass 6 not yet implemented. "
       f"Pass 5 detected {len(layer_map)} layers "
       f"from {len(cleaned)} pages."
   )
   ```

### Deliverable 3: Tests — `engines/normalization/tests/test_layer_detection.py`

**Mandatory tests:**

1. **ADV-011 (bold with transition marker):** Bold span >=80 chars containing "قوله:" → NOT classified as layer indicator (two-factor test fails). Assert confidence ≤ 0.50 or layer_type = UNCERTAIN.

2. **ADV-012 (bold at exactly 5%):** 1000-char page with exactly 50 chars bold → bold IS a layer indicator (5.0% is not <5%). At 4.9% → emphasis.

3. **ADV-013 (entire page bold):** 100% bold page with is_multi_layer=true → bold treated as emphasis. Page attributed to default commentary layer (SHARH), not MATN.

4. **ADV-014 (coverage gap):** Construct segments with a gap (chars 91–94 uncovered). Assert the code fills the gap with UNCERTAIN at confidence ≤ 0.30. Assert total coverage = len(primary_text).

5. **ADV-015 (metadata says single-layer, normalizer detects multi-layer):** Source with is_multi_layer=false but bold spans + "قوله:" markers. Assert text_layers has >1 segment. Assert NORM_LAYER_UNCERTAIN warning logged.

6. **Real fixture: ibn_aqil (multi-layer sharh).** Run Passes 1–5. Pages 0 and 2 have bold matn verses. Pages 1 and 3 have "قوله" markers. Assert: pages with bold → first segment is MATN, remaining is SHARH. All pages have full coverage.

7. **Single-layer passthrough:** A source with is_multi_layer=false and no layer signals. Assert one TextLayerSegment per page: [0, len(primary_text)), layer_type=MATN, confidence=1.0.

8. **Transition marker detection:** Construct a page with "قال المصنف: المبتدأ هو الاسم المرفوع". Assert MATN segment starts after the marker. Assert SHARH segment before it.

9. **Bracket detection:** Construct a page with "أي [ المبتدأ هو الاسم المرفوع ] وهو المجرد عن العوامل". Assert bracket content mapped to MATN. Assert surrounding text is SHARH.

10. **Short bracket exclusion:** Construct a page with "[التحريم: 5]" (Quran ref, 9 chars). Assert this does NOT create a MATN segment (excluded by <15 char threshold).

11. **Layer map construction:** After running on ibn_aqil, verify manifest-level layer_map has entries for MATN and SHARH with correct markers and author info.

12. **Bold span → primary_text mapping:** Construct a CleanedPage with bold_spans containing nested HTML tags. Verify the cleaned bold text is found correctly in primary_text.

13. **Multiple markers on one page:** Construct a page with both "قوله:" and "أي:" markers interleaved. Verify correct MATN/SHARH alternation with no gaps.

14. **Empty primary_text:** A page with empty primary_text → text_layers is empty list (no segments needed for zero characters).

15. **Duplicate bold text in primary_text:** Construct a page where the same text appears twice (once bold, once in commentary). Verify bold mapping assigns MATN to the correct (first) occurrence using sequential search, not both occurrences.

16. **Author canonical_id mapping:** For ibn_aqil, verify that MATN segments carry the matn author's canonical_id (from `metadata.text_layers` where `layer_type=="matn"`), and SHARH segments carry the sharh author's canonical_id.

---

## Critical Design Decisions

### D1: bold_spans offset mapping approach
bold_spans have HTML-space offsets (from Pass 1 BOLD_RE on matn_html). To get primary_text offsets: clean the bold html_text using `strip_tags → decode_entities → normalize_whitespace`, then `primary_text.find()`. **Empirically verified** on ibn_aqil: pages 0 and 2 both produce exact matches with correct primary_text offsets.

### D2: Single-layer is the common case — make it cheap
13 of 13 real fixtures have zero bold spans. Most Shamela books are single-layer. The single-layer path must be trivial: one TextLayerSegment per page, no scanning, no classification. Only enter the multi-layer path when `is_multi_layer=True` OR multi-layer signals are detected.

### D3: Bracket layer detection requires minimum length
Short brackets are overwhelmingly Quran verse references, not matn markers. 02_nahw_muhaqiq: 17 short (≤20 chars) vs 3 long. Threshold: brackets < 15 chars are excluded from layer detection. This prevents false positive MATN segments from Quran refs.

### D4: §4.B.1 content-based inference is DEFERRED
SPEC §4.A.5 signal 3 (content-based inference) is advisory only and requires multi-model consensus. CORE_EXTRACTION.md classifies §4.B.1 as DEFERRED. Session 4 implements typographic signals only (markers, bold, brackets, font size). Content-based inference stub logs but doesn't classify.

### D5: Hashiyah quotation detection — implement basic version
SPEC §4.A.5 step 7 describes hashiyah quoting sharh. For core build: detect explicit quotation markers ("قال الشارح:", "وعبارته:", "ونصه:", "قال في الشرح:") and reassign quoted regions from HASHIYAH to SHARH. The more complex inference (detecting where the quotation ends) uses the "أي:" and first-person assertion heuristic from SPEC — implement the basic version, mark uncertain regions.

### D6: Empty text_layers with is_multi_layer=True
When `metadata.is_multi_layer=True` but `metadata.text_layers` is empty (source engine flagged multi-layer but couldn't identify specific layers), use `author_canonical_id=None` for all segments until markers determine layer. Default layer is SHARH (commentary) per SPEC conservative default. Do NOT skip layer detection — the typographic signals may still identify layers even without metadata guidance.

---

## Do NOT Do

- **Do NOT modify Passes 1–4 code** except to add the Pass 5 integration call in `normalize()`.
- **Do NOT modify contracts.py** — all layer-related types already exist.
- **Do NOT implement §4.B.1** (content-based layer inference). Stub only.
- **Do NOT implement §4.B.9** (authorial voice fingerprints). Deferred.
- **Do NOT implement Pass 6** (output assembly).
- **Do NOT apply Unicode normalization** on Arabic text during bold text cleaning — use the same functions Pass 3 uses (strip_tags, decode_entities, normalize_whitespace).
- **Do NOT treat all brackets as matn markers** — short brackets (< 15 chars) are typically Quran verse refs.

---

## Verification

### Pass criteria (all must be true):

1. `pytest engines/normalization/tests/ -v` — ALL tests pass (existing + new), zero failures.
2. ADV-011, ADV-012, ADV-013, ADV-014, ADV-015 all pass as explicit named tests.
3. ibn_aqil fixture produces multi-layer text_layers with MATN and SHARH segments.
4. All 13 real fixtures produce valid text_layers (single-segment for non-multi-layer books).
5. Every TextLayerSegment array has full coverage: `segments[0].start == 0` and `segments[-1].end == len(primary_text)` and no gaps between consecutive segments.
6. `python tools/check_cross_engine_contracts.py` → PASS (no new contract changes, but verify).
7. The `normalize()` method calls Pass 5 and reaches the new NotImplementedError for Pass 6 (not "Passes 5–6").
8. For ibn_aqil pages 0 and 2: bold text mapped to MATN segments with confidence ≥ 0.60.
9. NORM_LAYER_UNCERTAIN logged when multi-layer signals detected in single-layer metadata source.

---

## After This

1. **Architect review:** Two-pass review per `reference/protocols/REVIEW_PROTOCOL.md`. Fill `REVIEW_CHECKLIST_TEMPLATE.md`, commit it, THEN deliver verdict.
2. **Cumulative metrics update** (target after Session 4):
   ```
   Implementation: ~4,000-4,500 lines (+700-1,200)
   Tests: ~2,500-2,800 lines (+600-900 for 16 test categories)
   Test count: ~145-165 passing
   ADV covered: 18/51 (ADV-001–018)
   ```

---

## Cumulative Build Metrics (after Session 3)

```
Implementation:  3,266 lines (shamela.py 1131, structure_discovery.py 1212, contracts.py 725, errors.py 130, base.py 56, tracer.py 12)
Tests:           1,919 lines + test_cross_engine.py
Test count:      126 passing (106 passes + 19 structure + 1 cross-engine), 22 skipped
ADV covered:     13/51 (ADV-001–010 + ADV-016–018)
Known limitations: L-001 (bare-number footnotes), L-002 (ضياء السالك collision), L-003 (same-page heading chaining)
```

## Known Limitations (from Sessions 2–3)

- **L-001:** Bare-number/unnumbered footnotes classified but not parsed. Fix: Session 5.
- **L-002:** ضياء السالك commentary numbering collision. Session 4 should address architecturally — once layers are separated, commentary `(N)` markers are distinguishable from footnote refs.
- **L-003:** Same-page heading chaining (214 instances/7 fixtures). Inherent page-level granularity limit.
