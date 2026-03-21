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

## L-004: Arabic conjunction prefixes not detected on transition markers

**Discovered:** Session 4 layer detection design (March 2026).
**Affected:** Multi-layer sources where markers appear with Arabic conjunction prefixes (و, ف) directly attached to the marker word.
**Behavior:** The transition marker regex uses `(?:^|\s)` as a word boundary, requiring whitespace before the marker word. Arabic conjunction prefixes (وقال المصنف:, وقوله:, فأي:) attach directly to the marker word without whitespace, so these are not detected.
**Impact:** Missed markers default to the current layer (typically commentary). Per SPEC conservative default, this is the safe direction — misattributing commentary to the commentator is less harmful than attributing it to the matn author (T-2). The missed markers do not cause misattribution of matn text.
**SPEC compliance:** Compliant — the SPEC's conservative default handles missed markers safely.
**Fix point:** Extend regex with optional Arabic prefix handling `(?:[وف])?` after validation against 20K Shamela samples to ensure no false positives from legitimate words starting with و or ف.

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

## L-008: Conditional reasoning markers excluded from boundary continuity

**Discovered:** Session 5 boundary continuity design (March 2026).
**SPEC reference:** §4.B.8 argument flow detection, D7.
**Affected:** Fiqh and usul sources where `إذا` appears in 15-19% of pages.
**Behavior:** All 3 conditional reasoning openers (`إذا`, `لو`, `إن`) and their closers (`فالحكم`, `فيجب`, `وجب`) are excluded from argument flow detection. They fire too frequently to be useful boundary markers.
**Impact:** Argument flow detection relies on evidence chains, position statements, and objection-response patterns only. Conditional reasoning across page boundaries falls through to punctuation analysis (mid_sentence/mid_paragraph).
**Fix point:** Add conditional markers with sentence-initial position requirement: only trigger when `إذا` appears at the start of a sentence (after terminal punctuation or at page start), not mid-sentence.

## L-009: Guillemet hadith distance heuristic

**Discovered:** Session 5 content flagger design (March 2026).
**SPEC reference:** §4.A.9 hadith citation detection, D8.
**Affected:** Pages where `«...»` guillemet-quoted text appears with `قال` further than 50 characters before.
**Behavior:** The pattern `قال.{0,50}«Arabic text»` requires `قال` within 50 characters before the opening guillemet. This is a design decision balancing precision (avoiding false positives from non-hadith guillemet usage) against recall (catching hadith citations with longer introductions).
**Impact:** Hadith citations introduced with long chains of narrator names (`حدثنا فلان عن فلان عن فلان قال`) where the distance exceeds 50 characters will not trigger the guillemet pattern. They may still be caught by the other 3 hadith detection patterns (ﷺ, صلى الله عليه وسلم, رواه + collector).
**Fix point:** If too tight, increase the distance to 80 characters. Monitor false positive and false negative rates on the full Shamela corpus.

## L-010: Division tree overlap downgraded from fatal to warning

**Discovered:** Session 6 validation implementation + smoke test (March 2026).
**SPEC reference:** §5 check 5 — "Sibling divisions do not overlap in their page ranges."
**Affected fixtures:** 7/50 extended fixtures (14%) — ext_01, ext_10, ext_19, ext_20, ext_26, ext_42, ext_44. All same-page heading collisions from L-003.
**Behavior:** Structure discovery produces overlapping sibling divisions when headings at different tiers share the same page, creating DivisionNodes with identical `[start, end]` ranges. Validation check 5 reports these as WARNING (NORM_DIVISION_OVERLAP) instead of FATAL.
**Impact:** Division tree metadata is advisory — content units are unaffected. The passaging engine uses `unit_index` adjacency for page joining, not the division tree. No content corruption or misattribution.
**Root cause:** L-003 (same-page same-level headings) propagates overlapping ranges into the division tree. Structure_discovery.py is frozen per NEXT.md Session 6 constraints — cannot be modified.
**SPEC compliance:** Partial deviation — SPEC asserts no overlap without specifying severity. WARNING is justified because content integrity is preserved. SPEC should explicitly classify as WARNING in §7 error code table.
**Fix point:** Structure_discovery should deduplicate headings that produce same-range divisions, or DivisionNode should support sub-page character-offset ranges. Either fix requires a SPEC-level design change.

## L-011: Writer recovery does not handle prev-only orphan state

**Discovered:** Session 6 deep review (March 2026).
**SPEC reference:** §4.A.2 lines 235-237, atomic write procedure + interrupted write recovery.
**Scenario:** If `temp_dir.rename(final_dir)` AND the `shutil.move` fallback both fail AFTER `final_dir.rename(prev_dir)` succeeded, the exception handler cleans up temp but leaves prev orphaned. `recover_interrupted_write` only checks for temp dirs — if no temp dirs exist, it returns False. The prev dir is stuck with no normalized/ and no temp to trigger recovery.
**Practical risk:** Near-zero. Requires both Path.rename and shutil.move to fail on a same-filesystem operation where a previous rename just succeeded. The failure itself IS raised as NORM_WRITE_FAILED (loud, not silent).
**Impact:** The book would need full re-processing. No corrupt data enters the library. This is a durability gap, not a correctness gap. No T-1 through T-7 threat applies.
**Fix:** Add a case in `recover_interrupted_write`: if no temp dirs AND no `normalized/` AND prev dirs exist → restore from latest prev. See CC fix instructions in Session 6 review.
