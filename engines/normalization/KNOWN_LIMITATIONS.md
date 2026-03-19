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
