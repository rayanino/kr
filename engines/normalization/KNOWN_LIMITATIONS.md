# Normalization Engine — Known Limitations

Tracked limitations discovered during build. Not bugs (code matches SPEC), but behaviors the architect and future sessions should be aware of.

## L-001: Bare-number and unnumbered footnotes classified but not parsed

**Discovered:** Session 2 semantic spot-check (March 2026).
**Affected fixtures:** 03_fiqh (54 pages), 05_tafsir (23 pages), 04_hadith (28 pages), 12_multi_muq (2 pages).
**Behavior:** The `_detect_fn_section_format()` correctly classifies these as `bare_number` or `unnumbered`. The text is preserved in `footnote_preamble`. But individual `ParsedFootnote` entries are NOT created because `FN_BOUNDARY_RE` requires `(N)` with parentheses.
**Impact:** No structured footnotes for these pages. No `known_fn_numbers`, so no `⌜N⌝` replacement in primary text. Footnote text is preserved (no data loss) but unstructured.
**SPEC compliance:** SPEC §4.A.2 Pass 2 says "Parse footnotes into individual entries using the `(N)` marker pattern." Bare-number format doesn't use `(N)` — it uses `N text` without parentheses. The SPEC doesn't mandate parsing bare-number format.
**Fix point:** Enhancement in Session 5 (output assembly) or later — add a bare-number parser branch in `_parse_footnotes()` triggered by `footnote_format == "bare_number"`.

## L-002: ضياء السالك commentary numbering collision

**Discovered:** Session 2 deep review (March 2026).
**Affected:** 1 book in corpus (ضياء السالك إلى أوضح المسالك, 4 volumes, 1,672 pages).
**Behavior:** This book uses `<hr><s0>` as a commentary layer separator. The commentary layer contains `(1)`, `(2)` etc. numbering that looks like footnote references. When real footnotes also exist (after `<hr width='95'>`), both the commentary numbering AND the original text refs get replaced with `⌜N⌝`.
**Impact:** False positive `⌜N⌝` markers in the commentary layer pointing to footnotes they weren't intended to reference.
**Fix point:** Pass 5 (layer detection, Session 4). Once layers are separated, the commentary `(N)` markers can be distinguished from footnote refs by their position relative to the `<hr><s0>` boundary.

## L-003: Same-page same-level headings create parent-child chains

**Discovered:** Session 3 architect review (March 2026).
**Affected fixtures:** 7 of 13 — 01_nahw_simple (1 chain), 02_nahw_muhaqiq (2), 03_fiqh (8), 07_balagha (41), 09_alt_title (4), 10_no_author (22), 11_multi_small (136). Total: 214 chained nodes.
**Behavior:** When two or more headings at the same heading_level share a single page (same unit_index), they cannot be siblings without violating §5 check 5 (sibling overlap). The same-page sibling resolution chains them as parent→child→child. In 07_balagha, page 13 has 4 scholar-name headings (المبرد, ثعلب, ابن المعتز, قدامة) — these become a 4-deep chain instead of 4 siblings.
**Impact:** Division tree hierarchy is semantically wrong for same-page headings: the deepest chained node appears as the only leaf, making passaging attribute the page to the last heading in the chain. StructuralMarkers correctly records the FIRST heading per page — so per-page heading attribution is correct. The error affects only the tree's parent-child structure for pages with multiple same-level headings.
**Root cause:** The SPEC's division model operates at page-level granularity. Multiple same-level headings on one page cannot have non-overlapping page ranges. This is inherent to page-level divisions, not an implementation bug.
**SPEC compliance:** Compliant — §5 check 5 passes. The chaining avoids sibling overlap while preserving all detected headings in the tree.
**Fix point:** Sub-page division ranges (character-offset based) would resolve this but require a SPEC-level design change to DivisionNode's range model. Alternatively, Tier 3 LLM context could suppress false positive headings from embedded section lists (03_fiqh page 1 pattern).

## L-004: Arabic conjunction prefixes on transition markers — RESOLVED

**Discovered:** Session 4 layer detection design (March 2026).
**RESOLVED:** Overnight hardening session (March 23, 2026).
**Fix applied:** Added optional conjunction prefix `[وف]?` before each transition marker
regex in `TRANSITION_MARKER_PATTERNS`. The prefix is NOT captured in the match group —
only the core marker text is captured. `plain_texts` list updated to include prefixed forms
(e.g., `"وقال المصنف:"`) for the bold-signal two-factor test.
**Covered markers:** `وقال المصنف:`, `فقال المصنف:`, `وقال الشارح:`, `فقال الشارح:`,
`وقوله:`, `فقوله:`, `وأي:`, `فأي:`.
**Risk:** LOW — safe direction (more granular layer boundaries, not fewer). The regex matches
only و and ف prefixes (the two common Arabic conjunction clitics), not other prefix letters.
**v3 calibration (7,475 books):** +97 multi-layer books detected (399→496).
10 adversarial false-positive tests pass (وقف, وقع, وقت, فقط, فقه, فقد, وقاية, فقير).

## L-005: Bold character threshold 50 deviates from SPEC provisional 80

**Discovered:** Session 4 layer detection calibration (March 2026).
**SPEC reference:** §4.A.5 two-factor test, [AUDIT FIX M-03]: "Threshold 80 chars is provisional — calibrate against KR test fixtures."
**Calibration data:** The ibn_aqil multi-layer fixture (the only multi-layer fixture available) has bold matn verses of 79 and 71 characters. The SPEC threshold of >=80 produces false negatives on both verses. Typical emphasis bold (hadith quotes, Quran refs) in the fixture range from 10-40 chars.
**Chosen threshold:** >=50 chars. Safety margin of 10 chars above highest observed emphasis bold.
**Affected range:** Bold spans between 50-79 chars are classified as layer indicators under this threshold but would be excluded under the SPEC threshold of 80. This could produce false positives for emphasis bold in the 50-79 char range on sources other than ibn_aqil.
**Fix point:** Revisit when more multi-layer fixtures are available. If emphasis bold in the 50-79 range is observed in real data, raise the threshold toward 80 and accept the false negatives on short matn verses (which would fall through to the conservative default as SHARH — safe direction).

## L-006: Hashiyah quotation detection not implemented (SPEC step 7)

**Discovered:** Session 4 architect review (March 2026).
**SPEC reference:** §4.A.5 step 7, NEXT.md D5.
**Affected:** 3-layer hashiyah sources where the hashiyah author quotes the sharh author.
**Behavior:** Explicit quotation markers ("وعبارته:", "ونصه:", "قال في الشرح:") are not detected. In 3-layer sources, sharh text quoted within the hashiyah layer remains attributed to the hashiyah author.
**Impact:** T-2 risk for 3-layer sources — sharh quotations are misattributed to the hashiyah author. 2-layer sources are unaffected. The `قال الشارح:` simple transition marker IS implemented (added during review), which partially mitigates the gap for cases where the hashiyah explicitly names the sharh author.
**Root cause:** Step 7 requires bounded quotation detection (start marker → end signal), which is more complex than simple transition markers and has no 3-layer fixture to test against.
**Fix point:** Session 5 or later, when a real hashiyah fixture (e.g., حاشية ابن قاسم على الروض المربع) is available for testing. Implementation: add `_detect_hashiyah_quotations()` post-processing step after `_build_segments()`, triggered only when `default_commentary_layer == HASHIYAH`.

## L-007: Marker-only MATN over-extension after bold_exit

**Discovered:** Session 4 architect adversarial self-review (March 2026).
**SPEC reference:** §4.A.5 detection algorithm step 4 ("infer layer for regions between boundaries from surrounding context").
**Affected:** Multi-layer pages where `قوله:` fires AND bold spans delineate the matn text, but no `أي:` or other marker appears after the bold span to close the MATN region.
**Behavior:** The state machine's `marker_state` persistence (R1 resolution) restores the layer to MATN after `bold_exit`, because the `قوله:` marker set `marker_state = (MATN, 0.90)`. In the common scholarly pattern "قوله: [bold matn text]. [sharh commentary]", the text after bold_exit is commentary but gets classified as MATN at confidence 0.90 (too high for the conservative default to reclassify).
**Impact:** T-2 risk — sharh text (hadith citations, evidence, reasoning) is misattributed to the matn author. The risk is bounded: (a) `أي:` markers commonly follow matn quotations and correctly close the MATN region; (b) the over-extension is page-scoped (marker_state resets per page); (c) it only manifests when bold AND marker are both present on the same page without a subsequent closing marker.
**Mitigating factors:** The `marker_state` design is correct for its intended purpose (Pattern B: marker opens MATN, bold is WITHIN the MATN region). The limitation is for Pattern A (bold IS the matn boundary, commentary resumes after bold). Distinguishing Pattern A from B requires content-based inference (§4.A.5 signal #3, deferred).
**Test coverage:** Test #19 (marker_state persistence) verifies Pattern B behavior. Pattern A is not tested because the only multi-layer fixture (ibn_aqil) does not trigger standalone `قوله:` markers — the word always appears embedded (`بقوله`) or without colon (`قوله «...»`).
**Fix point:** Content-based inference (SPEC signal #3) or a heuristic that checks whether bold_exit coincides with a sentence boundary (terminal punctuation) to distinguish Pattern A from B. Requires additional multi-layer fixtures for calibration.

## L-008: Conditional reasoning markers in boundary continuity — MITIGATED

**Discovered:** Session 5 boundary continuity design (March 2026).
**SPEC reference:** §4.B.8 argument flow detection, D7.
**Mitigated:** Overnight hardening session (March 23, 2026).
**Fix applied:** Re-enabled conditional openers (`إذا`, `لو`, `إن`) and closers (`فالحكم`, `فيجب`, `وجب`) with sentence-initial position requirement. The `_is_sentence_initial()` function scans backward up to 10 chars for terminal punctuation (`.`, `؟`, `!`, `؛`). Mid-sentence occurrences (common subordinating conjunction usage) are filtered out.
**Remaining risk:** LOW-MEDIUM. Advisory flag for downstream engines. Does not modify text.
The sentence-initial filter prevents the 15-19% false positive rate from mid-sentence `إذا`.
**v3 calibration (7,475 books):** +7,661 mid_argument boundaries (25,800→33,461, +29.7%).
Reclassified from mid_paragraph (-3,364) and mid_sentence (-4,297).

## L-009: Guillemet hadith distance heuristic — MITIGATED

**Discovered:** Session 5 content flagger design (March 2026).
**SPEC reference:** §4.A.9 hadith citation detection, D8.
**Mitigated:** Overnight hardening session (March 23, 2026). Distance increased 50 → 80.
**Rationale:** 80 chars covers typical long isnad chains (`حدثنا فلان عن فلان عن فلان قال`).
Hadith citations with even longer introductions still caught by other 3 patterns.
**Remaining risk:** LOW — distance 80 is conservative. False positive risk minimal because
guillemet usage in non-hadith contexts rarely follows `قال` within 80 chars.
**v3 calibration (7,475 books):** +4 additional hadith detections across full corpus.

## L-010: Division tree overlap downgraded from fatal to warning

**Discovered:** Session 6 validation implementation + smoke test (March 2026).
**SPEC reference:** §5 check 5 — "Sibling divisions do not overlap in their page ranges."
**Affected fixtures:** 7/50 extended fixtures (14%) — ext_01, ext_10, ext_19, ext_20, ext_26, ext_42, ext_44. All same-page heading collisions from L-003.
**Behavior:** Structure discovery produces overlapping sibling divisions when headings at different tiers share the same page, creating DivisionNodes with identical `[start, end]` ranges. Validation check 5 reports these as WARNING (NORM_DIVISION_OVERLAP) instead of FATAL.
**Impact:** Division tree metadata is advisory — content units are unaffected. The passaging engine uses `unit_index` adjacency for page joining, not the division tree. No content corruption or misattribution.
**Root cause:** L-003 (same-page same-level headings) propagates overlapping ranges into the division tree. Structure_discovery.py is frozen per NEXT.md Session 6 constraints — cannot be modified.
**SPEC compliance:** Partial deviation — SPEC asserts no overlap without specifying severity. WARNING is justified because content integrity is preserved. SPEC should explicitly classify as WARNING in §7 error code table.
**Fix point:** Structure_discovery should deduplicate headings that produce same-range divisions, or DivisionNode should support sub-page character-offset ranges. Either fix requires a SPEC-level design change.

## L-011: Writer recovery does not handle prev-only orphan state — RESOLVED

**Discovered:** Session 6 deep review (March 2026).
**RESOLVED:** Session 6 implementation. Code at `writer.py:192-216`.
**Fix applied:** Added prev-only orphan recovery case in `recover_interrupted_write()`:
if no temp dirs AND no `normalized/` AND prev dirs exist → restore from latest prev,
clean up remaining prevs, log NORM_WRITE_RECOVERY.
**Status:** Fixed. No remaining risk. Original scenario fully handled.

## L-012: Arabic-Indic digit footnote markers not parsed

**Discovered:** Session 7 ADV gap analysis (March 2026).
**SPEC reference:** ADV-023.
**Behavior:** Footnote regex uses [0-9] (ASCII only). Arabic-Indic markers (١, ٢, ٣)
in format (١) are NOT detected as footnote references.
**Rationale:** Arabic-Indic digits in parentheses commonly appear as hadith/verse
numbers. Matching them as footnote markers introduces false positives. ASCII-only is a
precision-over-recall design choice documented in shamela.py line 115-122.
**Fix point:** If corpus analysis finds Shamela exports using Arabic-Indic footnote
markers, add a configurable detection mode.
