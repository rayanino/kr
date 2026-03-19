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

9. `engines/normalization/KNOWN_LIMITATIONS.md` (30L) — L-002 (ضياء السالك commentary numbering collision). Note: L-002 cannot be resolved in Session 4 (requires Pass 2/3 changes). Layer separation enables the fix in principle, but the actual disambiguation happens later.

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

1. `detect_layers(page: CleanedPage, metadata: SourceMetadata, force_multi_layer: bool = False) -> LayerDetectionResult`
   - Orchestrator. Dispatches to single-layer or multi-layer path.
   - **Single-layer path** (`is_multi_layer=False` AND `force_multi_layer=False`): return one `TextLayerSegment` covering `[0, len(primary_text))` with `layer_type` from metadata (default MATN if no text_layers in metadata), `confidence=1.0`.
   - **Multi-layer path** (`is_multi_layer=True` OR `force_multi_layer=True`): run full detection algorithm.
   - NOTE: The 10-page multi-layer signal detection (ADV-015, D7) runs in `_pass5_detect_layers` BEFORE per-page calls. `detect_layers()` receives the resolved decision via `force_multi_layer`.

2. `_map_bold_to_primary(bold_spans: list[tuple[int, int, str]], primary_text: str) -> list[tuple[int, int]]`
   - Maps bold_span HTML text to primary_text character offsets.
   - For each bold_span IN ORDER: clean the html_text (`strip_tags` → `decode_entities` → `normalize_whitespace().strip()`), then `primary_text.find(cleaned, search_start)` to get start index. End = start + len(cleaned_text). Update `search_start = end` for next iteration.
   - **CRITICAL: Use sequential search with a running `search_start` offset.** Bold spans are extracted in document order from matn_html. If the same text appears twice in primary_text (e.g., a matn verse repeated in commentary), `find()` without a start offset returns the wrong occurrence. Sequential searching preserves positional correctness.
   - Returns list of (start, end) tuples in primary_text coordinates.
   - If a bold span can't be found in primary_text (rare edge case from cleaning differences), log a warning and skip it.

3. `_detect_transition_markers(primary_text: str, default_commentary_layer: LayerType) -> list[LayerBoundary]`
   - Scan primary_text for explicit transition markers (SPEC §4.A.5 signal 1).
   - `default_commentary_layer` is determined by the caller using D11 logic (SHARH for 2-layer, HASHIYAH for 3-layer). Needed because "أي:" transitions to the source's outer commentary layer, which varies by source type.
   - **char_offset semantics:** `char_offset` points to the first character AFTER the marker text (i.e., where the new layer begins). The marker text itself belongs to the PREVIOUS layer. Example: "قوله: ويصح" → if "قوله:" is at position 0, char_offset = 6 (after colon + space), and the MATN layer starts at char 6. The chars 0-5 ("قوله: ") belong to the preceding layer. **This matches the SPEC concrete example** where "قوله:" (chars 0-5) is attributed to sharh and matn starts at char 6.
   - Markers and their layer transitions:
     - `"قال المصنف"` / `"قال المصنف:"` → transition to MATN, confidence 0.90
     - `"قال الشارح"` / `"قال الشارح:"` → transition to SHARH, confidence 0.90
     - `"قوله:"` / `"قوله :"` → transition to MATN (quoting original text), confidence 0.90 (SPEC §4.A.5: explicit transition marker ≥ 0.90; concrete example confirms 0.90)
     - `"أي:"` / `"أي :"` → transition to `default_commentary_layer` (resolves to SHARH for 2-layer sources, HASHIYAH for 3-layer — see D11), confidence 0.80 (explanatory marker with lower confidence, consistent with SPEC concrete example)
     - `"وعبارته:"` / `"ونصه:"` / `"قال في الشرح:"` → hashiyah quoting sharh (3-layer sources only), confidence 0.85
   - **"أقول:" is NOT a transition marker.** SPEC says it "confirms current layer's author speaking" — it does not transition to a new layer. Do NOT create a LayerBoundary for it. Future: could be used as a confidence signal for the current layer, but implementing this requires knowing the current layer at detection time, which is a _build_segments responsibility. Deferred.
   - Return LayerBoundary for each marker found, with char_offset = first character AFTER the marker (after colon and optional space).

4. `_detect_bracket_regions(primary_text: str) -> list[tuple[int, int]]`
   - Find `[text]` regions that are potential matn markers.
   - **Exclude short brackets** (< 15 chars between `[` and `]`) — these are typically Quran verse references like `[التحريم: 5]` or editorial insertions, NOT matn markers.
   - Return list of (start, end) character offset tuples for bracket content.

5. `_classify_bold_signal(bold_regions: list[tuple[int, int]], primary_text: str, transition_markers: list[LayerBoundary]) -> tuple[str, list[tuple[int, int]]]`
   - Implements the SPEC two-factor bold classification. Returns `(classification, layer_bold_regions)`.
   - **Guard:** If `len(primary_text) == 0` or `len(bold_regions) == 0`, return `("emphasis", [])` immediately (nothing to classify).
   - Calculate `bold_percentage = sum(end - start for start, end in bold_regions) / len(primary_text)`.
   - If `bold_percentage < 0.05` → return `("emphasis", [])` (too little bold to be a layer signal).
   - If `bold_percentage > 0.60` → return `("emphasis", [])` (too much bold — emphasis, not layer).
   - For each bold region, apply the two-factor test: `char_count >= 50 AND no transition marker inside the span`. Bold regions that pass are collected into `layer_bold_regions`. **NOTE: SPEC says >=80 is "provisional — calibrate against KR test fixtures." Calibrated to 50 based on ibn_aqil data: matn verses are 71 and 79 chars (see D10). ADV-011 (87 chars) and ADV-012 (50 chars) both still work correctly at threshold 50.**
   - If ALL pass → return `("layer_indicator", layer_bold_regions)`.
   - If SOME pass, SOME fail → return `("mixed", layer_bold_regions)` (only the passing regions are in the list).
   - If NONE pass → return `("emphasis", [])`.

6. `_build_segments(primary_text: str, layer_bold_regions: list[tuple[int, int]], markers: list[LayerBoundary], brackets: list[tuple[int, int]], bold_classification: str, metadata: SourceMetadata) -> list[TextLayerSegment]`
   - The core segmentation algorithm (SPEC §4.A.5 detection algorithm steps 2–7).
   - **NOTE:** `layer_bold_regions` contains ONLY bold regions that passed the two-factor test (returned from `_classify_bold_signal`). When classification is "emphasis", this list is empty. When "mixed", it contains the subset that passed. When "layer_indicator", it contains all bold regions. Because the two-factor test excludes bold regions containing markers, `layer_bold_regions` and `markers` never overlap.
   - **Algorithm (event-based state machine, see D13 for signal priority):**
   - **Step 1:** Build a sorted event list from all signals:
     - For each bold region: `(start, "bold_enter", MATN, 0.75)` and `(end, "bold_exit", DEFAULT, 0.60)`
     - For each marker: `(char_offset, "marker", marker.to_layer, marker.confidence)`
     - For each bracket: `(start, "bracket_enter", MATN, 0.65)` and `(end, "bracket_exit", DEFAULT, 0.60)`
     - Sort events by offset. On ties: "exit" events before "enter" events at same offset (prevent zero-length segments).
   - **Step 2:** Walk the event list maintaining `current_layer` (starts as default commentary layer per D11) and `current_confidence` (starts at 0.60). For each event, emit a segment `[last_offset, event_offset)` with `current_layer` and `current_confidence`, then update state. Markers are OPEN-ENDED transitions (persist until the next event). Bold/bracket enters are BOUNDED (paired with an exit).
   - **Step 3:** After all events, emit a final segment from last_offset to `len(primary_text)` with the current layer.
   - **Step 4:** Merge adjacent segments with the same layer_type. Merged confidence = minimum of constituent confidences. Remove zero-length segments.
   - **Step 5:** Validate full coverage: every character in [0, len(primary_text)) is in exactly one segment. If not → fill with UNCERTAIN at confidence 0.30.
   - **Step 6 (conservative default, post-processing):** Scan all segments. Any MATN segment with confidence < 0.50 is reclassified to the default commentary layer (D11). This implements SPEC §4.A.5 conservative default: misattributing commentary to the commentator is less harmful than attributing explanation to the matn author.
   - Get `author_canonical_id` from `metadata.text_layers` by matching layer_type. If layer_type not in metadata.text_layers (e.g., detected but not in source metadata), use `None`.
   - NOTE: The 40% matn proportion check (SPEC §4.A.5 step 6) is a SOURCE-LEVEL aggregate check, not per-page. It runs in `_pass5_detect_layers` after all pages are processed (see Deliverable 2).
   - **Confidence values per signal type** (SPEC §4.A.5: typographic 0.60–0.85, markers ≥ 0.90): bold MATN=0.75, bracket MATN=0.65, marker=from LayerBoundary, default=0.60, gap fill=0.30.

7. `_build_layer_map(segments: list[TextLayerSegment], signals_found: list[str], metadata: SourceMetadata) -> list[LayerMapEntry]`
   - Build manifest-level layer_map from detected segments.
   - One entry per unique layer_type found.
   - `author_canonical_id` and `author_name_arabic` from `metadata.text_layers` by matching layer_type. If no match (e.g., UNCERTAIN type), both are `None`.
   - markers field lists which signals were found for that layer (e.g., "bold", "قوله:", "brackets").
   - confidence = average confidence of segments for that layer type.

### Deliverable 2: Integration in `shamela.py`

1. Add `_pass5_detect_layers(self, cleaned: list[CleanedPage], metadata: SourceMetadata) -> tuple[dict[int, list[TextLayerSegment]], list[LayerMapEntry]]`
   - **Pre-scan (ADV-015, D7):** If `metadata.is_multi_layer=False`, scan first `min(10, len(cleaned))` pages for multi-layer signals. For each page: estimate bold coverage by cleaning each bold_span's html_text (`strip_tags → decode_entities → normalize_whitespace`) and summing cleaned lengths vs `len(primary_text)`. If bold coverage >10% AND any transition marker (exact string match for "قال المصنف", "قوله:", "أي:", etc.) is found in primary_text, set `force_multi_layer=True` and log `NORM_LAYER_UNCERTAIN` warning. Otherwise `force_multi_layer=False`. **The cleaning functions are already in shamela.py (module-level) — import and use them directly.**
   - For each CleanedPage, calls `layer_detector.detect_layers(page, metadata, force_multi_layer)`.
   - Returns: `(page_layers: dict[int, list[TextLayerSegment]], layer_map: list[LayerMapEntry])`.
   - For single-layer sources (when force_multi_layer is also False), still produces one-segment-per-page output.
   - **After all pages processed (multi-layer sources only):** Calculate aggregate matn ratio: `total_matn_chars / total_primary_chars` across all pages. If ratio > `layer_matn_max_ratio` (default 0.40, from SPEC §4.A.5 step 6), log `NORM_LAYER_UNCERTAIN` warning: "Layer 1 (matn) is {ratio:.0%} of total text, exceeding {threshold:.0%} threshold — possible bulk misdetection." This is a WARNING only — segments are NOT modified (human review decides). This catches the T-2 scenario where bold-as-emphasis is misclassified as bold-as-layer across the entire source.

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

1. **ADV-011 (bold with transition marker):** Bold span >=50 chars (87 in ADV) containing "قوله:" → NOT classified as layer indicator (two-factor test fails: marker inside span). Assert confidence ≤ 0.50 or layer_type = UNCERTAIN.

2. **ADV-012 (bold at exactly 5%):** 1000-char page with exactly 50 chars bold → bold IS a layer indicator (5.0% is not <5%). At 4.9% → emphasis.

3. **ADV-013 (entire page bold):** 100% bold page with is_multi_layer=true → bold treated as emphasis. Page attributed to default commentary layer (SHARH), not MATN.

4. **ADV-014 (coverage gap):** Construct segments with a gap (chars 91–94 uncovered). Assert the code fills the gap with UNCERTAIN at confidence ≤ 0.30. Assert total coverage = len(primary_text).

5. **ADV-015 (metadata says single-layer, normalizer detects multi-layer):** Source with is_multi_layer=false but bold spans + "قوله:" markers. Assert text_layers has >1 segment. Assert NORM_LAYER_UNCERTAIN warning logged.

6. **Real fixture: ibn_aqil (multi-layer sharh).** Run Passes 1–5. Construct SourceMetadata with `is_multi_layer=True` and `text_layers=[TextLayer(layer_type="matn", author=...), TextLayer(layer_type="sharh", author=...)]`. Assert:
   - Pages 0 and 2 have bold matn verses (79, 71 chars — both ≥50 threshold). Bold passes percentage check (29.3%, 25.0%) and two-factor test (≥50 chars, no markers inside bold). First segment on these pages should be MATN with confidence 0.75.
   - Page 0 has "أي:" at offset 80 → text after "أي:" is SHARH.
   - Page 3 has "أي:" at offset 33 → text after "أي:" is SHARH. Text before "أي:" (which contains "ومعنى قوله «...»" — NOTE: this is embedded "قوله" inside a sentence, NOT a standalone "قوله:" transition marker) is SHARH (default).
   - Pages 1 and 4 have no bold and no standalone markers → entire page is SHARH (default commentary layer).
   - **All 5 pages have full coverage** (no gaps, no overlaps).
   - **IMPORTANT: Pages 1 and 3 do NOT have "قوله:" transition markers.** The word "قوله" appears embedded in commentary sentences ("بقوله", "معنى قوله") but these are NOT standalone transition markers. Only "أي:" appears as a standalone marker (pages 0, 3).

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

17. **Matn proportion validation (SPEC §4.A.5 step 6, aggregate):** Construct a multi-layer source with 5 pages where bold covers 55% of text on each page (all classified as MATN). Run `_pass5_detect_layers`. Assert `NORM_LAYER_UNCERTAIN` warning is logged mentioning "exceeding" and "40%". Assert page-level segments are NOT modified (warning only, human reviews).

18. **Conservative default (SPEC §4.A.5 post-processing):** Call `_build_segments` directly with a hand-crafted `LayerBoundary(to_layer=MATN, confidence=0.40)`. Assert the resulting segment is reclassified from MATN to the default commentary layer (SHARH). This tests the safety net: MATN segments below confidence 0.50 are conservative-defaulted to commentary.

---

## Critical Design Decisions

### D1: bold_spans offset mapping approach
bold_spans have HTML-space offsets (from Pass 1 BOLD_RE on matn_html). To get primary_text offsets: clean the bold html_text using `strip_tags → decode_entities → normalize_whitespace`, then `primary_text.find()`. **Empirically verified** on ibn_aqil: pages 0 and 2 both produce exact matches with correct primary_text offsets.

### D2: Single-layer is the common case — make it cheap
13 of 13 real fixtures have zero bold spans. Most Shamela books are single-layer. The single-layer path must be trivial: one TextLayerSegment per page, no scanning, no classification. Only enter the multi-layer path when `is_multi_layer=True` OR multi-layer signals are detected.

### D3: Bracket layer detection requires minimum length
Short brackets are overwhelmingly Quran verse references, not matn markers. 02_nahw_muhaqiq: 17 short (≤20 chars) vs 3 long. Threshold: brackets < 15 chars are excluded from layer detection. This prevents false positive MATN segments from Quran refs.

### D4: §4.B.1 content-based inference is DEFERRED
SPEC §4.A.5 signal 3 (content-based inference) is advisory only and requires multi-model consensus. CORE_EXTRACTION.md classifies §4.B.1 as DEFERRED. Session 4 implements typographic signals only (markers, bold, brackets — font size deferred per D8). Content-based inference stub logs but doesn't classify.

### D5: Hashiyah quotation detection — implement basic version
SPEC §4.A.5 step 7 describes hashiyah quoting sharh. For core build: detect explicit quotation markers ("قال الشارح:", "وعبارته:", "ونصه:", "قال في الشرح:") and reassign quoted regions from HASHIYAH to SHARH. The more complex inference (detecting where the quotation ends) uses the "أي:" and first-person assertion heuristic from SPEC — implement the basic version, mark uncertain regions.

### D6: Empty text_layers with is_multi_layer=True
When `metadata.is_multi_layer=True` but `metadata.text_layers` is empty (source engine flagged multi-layer but couldn't identify specific layers), use `author_canonical_id=None` for all segments until markers determine layer. Default layer is SHARH (commentary) per SPEC conservative default. Do NOT skip layer detection — the typographic signals may still identify layers even without metadata guidance.

### D7: Multi-layer signal detection threshold (not in SPEC — new design decision)
The SPEC says the normalizer should detect layers "even when the source engine didn't flag it" but doesn't specify how. Implementation: scan first 10 pages; if bold spans cover >10% of text on any page AND transition markers are found, treat as multi-layer. These thresholds (10 pages, 10% bold) are provisional calibration values — adjust against real multi-layer Shamela fixtures when available.

### D8: Font size signal — DEFERRED
SPEC §4.A.5 lists font size as a Shamela typographic signal. HOWEVER: 0 of 13 test fixtures have font_size_spans. The SPEC itself says "A minority of Shamela exports use <font size> tags." Without test data, implementing font size detection would be untested code. Deferred until a real fixture with font_size_spans is available. `CleanedPage.font_size_spans` is already captured by Pass 1 — the data is there when the detector is ready.

### D9: ADV-015 "enrichment write-back" scope
ADV-015 describes "writes back a multi-layer discovery to source metadata as an enrichment." The normalization engine does NOT modify source metadata (D-023 metadata pass-through). The enrichment is captured in the normalization manifest's `layer_map` field (which reflects detected layers), NOT as a source metadata write-back. The ADV's intent (detect multi-layer when metadata misses it) is fully covered; the mechanism is layer_map, not source modification.

### D10: Two-factor char threshold calibration (SPEC says "provisional — calibrate")
SPEC §4.A.5 sets the two-factor bold char threshold at >=80, marked "[AUDIT FIX M-03]" and "Threshold 80 chars is provisional — calibrate against KR test fixtures." Calibration data from ibn_aqil (only multi-layer fixture): matn verses are 79 and 71 chars. Both FAIL >=80. Typical emphasis bold (hadith/Quran quotes): 10-40 chars. **Calibrated threshold: >=50.** Safety margin: 10 chars above emphasis range. ADV-011 (87 chars, with marker) still correctly fails two-factor. ADV-012 (50 chars, no marker) correctly passes at the boundary. This calibration SHOULD be revisited when more multi-layer fixtures are available (e.g., from the 20K+ Shamela samples).

### D11: Default commentary layer determination
When `_build_segments` needs to assign the "default commentary layer" for regions with no signals, it must determine which layer is the source's outer commentary layer. Logic: from `metadata.text_layers`, find the entry with the highest layer hierarchy that is NOT tahqiq_note. Hierarchy: matn=1, sharh=2, hashiyah=3, tahqiq_note=0 (excluded — footnotes, not body text). For a 2-layer sharh (text_layers=[matn, sharh]): default=SHARH. For a 3-layer hashiyah (text_layers=[matn, sharh, hashiyah]): default=HASHIYAH. If `text_layers` is empty: default=SHARH (conservative — most Shamela multi-layer sources are sharh).

### D12: Layer map aggregation across pages
`detect_layers()` returns per-page `LayerDetectionResult` with `layer_map_entries`. The manifest needs one aggregated `layer_map`. `_pass5_detect_layers` must merge: for each unique `LayerType` across all pages, create one `LayerMapEntry` with `markers = union of all per-page markers for that type`, `confidence = mean of per-page confidences for that type`, and `author_canonical_id` / `author_name_arabic` from the first page's entry (these are constant from metadata).

### D13: Signal priority in _build_segments
When multiple signals could apply to the same character position, priority is: **markers > bold > brackets > default**. In practice, bold/marker overlap is eliminated by the two-factor test (bold regions containing markers are excluded). But if a marker appears inside a bracket region, the marker takes precedence from its char_offset forward (markers are open-ended transitions, brackets are bounded regions). The event-based state machine in _build_segments handles this naturally: a marker event overrides whatever region state was active.

---

## Do NOT Do

- **Do NOT modify Passes 1–4 code** except to add the Pass 5 integration call in `normalize()`.
- **Do NOT modify contracts.py** — all layer-related types already exist.
- **Do NOT implement §4.B.1** (content-based layer inference). Stub only.
- **Do NOT implement §4.B.9** (authorial voice fingerprints). Deferred.
- **Do NOT implement Pass 6** (output assembly).
- **Do NOT apply Unicode normalization** on Arabic text during bold text cleaning — use the same functions Pass 3 uses (strip_tags, decode_entities, normalize_whitespace).
- **Do NOT treat all brackets as matn markers** — short brackets (< 15 chars) are typically Quran verse refs.
- **Do NOT implement font_size detection** — deferred per D8 (no test fixtures available). font_size_spans data exists in CleanedPage but is not consumed by Pass 5 yet.

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
10. NORM_LAYER_UNCERTAIN logged when matn proportion exceeds 40% on a multi-layer source (test 17).

---

## After This

1. **Architect review:** Two-pass review per `reference/protocols/REVIEW_PROTOCOL.md`. Fill `REVIEW_CHECKLIST_TEMPLATE.md`, commit it, THEN deliver verdict.
2. **Cumulative metrics update** (target after Session 4):
   ```
   Implementation: ~4,000-4,500 lines (+700-1,200)
   Tests: ~2,500-2,800 lines (+600-900 for 18 test categories)
   Test count: ~145-170 passing
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
- **L-002:** ضياء السالك commentary numbering collision. Layer separation (Pass 5) makes commentary `(N)` markers distinguishable from footnote refs in PRINCIPLE — but the actual fix requires Pass 2/3 changes (footnote parsing), which Session 4 cannot modify. L-002 remains open; Session 5 or later addresses it with layer-aware footnote disambiguation.
- **L-003:** Same-page heading chaining (214 instances/7 fixtures). Inherent page-level granularity limit.
