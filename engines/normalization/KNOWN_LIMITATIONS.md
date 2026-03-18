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
