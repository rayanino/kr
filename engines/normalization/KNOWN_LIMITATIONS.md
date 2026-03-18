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
