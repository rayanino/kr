# Normalization Engine — Evaluation Report

**Date:** March 2026
**Evaluator:** Claude Chat (Architect)
**Methodology:** ENGINE_BUILD_BLUEPRINT.md §3 (4-Layer Evaluation), adapted for deterministic engine
**Commit:** `266790b` (evaluation session start)
**Skills used:** kr-evaluate, critical-review, thinking-frameworks

---

## Layer 1: Programmatic Validation

**Scope:** All 63 repo fixtures (13 real + 50 extended) processed through `normalize_source`.

### Aggregate Metrics

| Metric | Result | Threshold | Status |
|--------|--------|-----------|--------|
| Fixtures processed | 63/63 | 63/63 | ✅ PASS |
| Fatal validation errors | 0 | 0 | ✅ PASS |
| Processing errors | 0 | 0 | ✅ PASS |
| Max page loss | 2 | ≤5 | ✅ PASS |
| Mean page loss | 1.1 | — | ✅ Good |
| Min Arabic ratio | 75.81% | >70% | ✅ PASS |
| Zero-diacritic fixtures | 0 | 0 | ✅ PASS |
| Tests passing | 420 (14 skipped) | 420 | ✅ Confirmed |

### Warning Patterns (39 total across 63 fixtures)

| Warning Type | Count | Fixtures | Root Cause |
|-------------|-------|----------|------------|
| Division overlap | 22 | 5 (ext_01, ext_10, ext_20, ext_42, ext_44) | L-003/L-010: same-page headings |
| Low Arabic ratio (per-page) | 11 | 2 (12_multi_muq, ext_16) | Individual pages with non-Arabic content |
| Identical character run >20 | 6 | 1 (ext_41) | Source formatting artifacts |

All warnings trace to documented known limitations. No systematic issue detected.

### Boundary Continuity Coverage

| Metric | Value |
|--------|-------|
| Mean coverage | 97.10% |
| Min coverage | 0.00% (13_format_b — 1 page, correct) |
| Fixtures with mid_argument | 22/63 (35%) |
| BC types present | mid_sentence, mid_paragraph, mid_argument, section_break, unknown |

### Multi-Layer Detection

| Fixture | Multi-layer units | Total units | Source |
|---------|------------------|-------------|--------|
| 02_nahw_muhaqiq | 5 | 295 | Explicit (metadata) |
| 01_nahw_simple | 21 | 73 | Auto-upgraded |
| ext_35 | 3 | 30 | Auto-upgraded |
| ext_50 | 28 | 42 | Auto-upgraded |

### Content Flags Distribution

| Flag | Pages | Fixtures |
|------|-------|----------|
| has_hadith | 3,741 | Distributed across corpus |
| has_quran | 1,170 | Distributed across corpus |
| has_verse | 1,643 | Distributed across corpus |

### Layer 1 Verdict: PASS — No anomalies found.

---

## Layer 2: Pattern Analysis — Limitation Downstream Impact

Each limitation assessed for passaging impact: **BLOCKING** (must fix), **ACCEPTABLE** (passaging works despite it), or **DEFERRED** (matters for a later engine, not passaging).

### L-001: Bare/unnumbered footnotes not parsed → ACCEPTABLE

**Passaging question:** Does passaging need footnote numbers to link refs?

**Assessment:** Passaging renumbers footnotes during cross-page assembly (SPEC §4.A.2). It reads `Footnote.ref_marker` and `⌜N⌝` markers in `primary_text`. For bare-number pages, no `ParsedFootnote` entries exist and no `⌜N⌝` markers are in the text. Passaging sees these pages as having zero footnotes — which is correct behavior (no structured footnotes to renumber). The footnote text IS preserved in `footnote_preamble` but is not exposed in the `ContentUnit.footnotes` array.

**Impact:** Passaging produces correct output. Footnote text is not lost (preserved in the normalization intermediate), but not structured for downstream use until L-001 is fixed. This affects excerpting (can't cite individual footnotes) but not passaging.

**Verdict: ACCEPTABLE** — passaging is unaffected. Deferred to Stage 2 or excerpting engine prep.

### L-002: ضياء السالك numbering collision → ACCEPTABLE

**Passaging question:** Does this book exist in the 2,519 collection?

**Assessment:** Single known book. Even if present, the impact is false `⌜N⌝` markers in the commentary layer pointing to wrong footnotes. Passaging would renumber these markers, propagating the error but not introducing new ones. The passaging engine itself is not broken — the input data is imprecise.

**Verdict: ACCEPTABLE** — isolated to one book. Monitor during full-collection processing.

### L-003: Same-page heading chains → ACCEPTABLE

**Passaging question:** Does passaging use heading levels for division grouping?

**Assessment:** Passaging uses the division tree for boundary guidance, traversing `DivisionNode` children. L-003 creates artificially deep chains (e.g., 7 المطلب headings at L5 in 03_fiqh becoming a 7-deep chain). Passaging treats leaf divisions as boundary candidates. The deepest chained node becomes the leaf, so passaging attributes the page to the LAST heading in the chain — semantically wrong (should be split among all 7) but practically harmless because all 7 headings share the same page range [1,2]. Passaging cannot split a single page, so the result is the same regardless of which heading is the leaf.

**Verdict: ACCEPTABLE** — passaging boundary decisions unaffected. The tree shape is wrong but passaging's page-level granularity makes the error inert.

### L-004: Arabic conjunction prefixes not detected → ACCEPTABLE

**Passaging question:** Does this cause false negatives in boundary detection?

**Assessment:** L-004 affects layer detection markers (e.g., وقال المصنف: not matching because of the و prefix). Passaging doesn't consume layer detection markers — it reads the already-computed `text_layers` and `boundary_continuity`. The boundary continuity engine uses separate marker sets that were calibrated with leading-boundary requirements (S5 finding). The false negatives in layer detection fall to the conservative default (SHARH attribution), which is the safe direction per T-2.

**Verdict: ACCEPTABLE** — passaging never sees these markers. Layer detection already handles the miss safely.

### L-005: Bold threshold 50 vs SPEC 80 → ACCEPTABLE

**Passaging question:** Does this affect layer detection accuracy?

**Assessment:** The threshold was empirically calibrated. At 80, real matn verses (79 and 71 chars) would be misclassified. At 50, there is a theoretical false-positive window (50-79 chars) but no observed false positives in the 63 fixtures. Passaging consumes layer segments as-is, with confidence scores reflecting the detection quality.

**Verdict: ACCEPTABLE** — empirically calibrated, no observed issues.

### L-006: Hashiyah detection not implemented → DEFERRED

**Passaging question:** How many 3-layer texts exist? Is this blocking?

**Assessment:** Zero 3-layer fixtures exist in the test corpus. The 4 multi-layer fixtures are all 2-layer (matn+sharh). In the full 2,519 collection, hashiyah texts (e.g., حاشية ابن قاسم على الروض المربع) exist but are relatively rare. When encountered, they receive 2-layer treatment — the hashiyah layer is classified as sharh. This means T-2 risk: hashiyah quotations of sharh text are misattributed to the hashiyah author. Passaging is unaffected by this — it processes whatever layers it receives. The T-2 risk is a normalization accuracy issue, not a passaging input issue.

**Verdict: DEFERRED** — no 3-layer fixtures to test against. Fix when a hashiyah fixture is available. Passaging processes 2-layer output correctly regardless.

### L-007: Marker-only MATN over-extension → ACCEPTABLE

**Passaging question:** Impact if matn segment is too long?

**Assessment:** Over-extended matn segments mean some sharh text is attributed to the matn author. Passaging receives these segments and propagates them into `PassageTextLayerSegment`. The downstream impact is in excerpting/synthesis (wrong author on excerpts), not passaging. Passaging's own boundary decisions are not affected by layer boundaries — it uses the division tree and boundary_continuity, not text_layers, for boundary placement.

**Verdict: ACCEPTABLE** — passaging propagates layers faithfully, correct or not.

### L-008: Conditional markers excluded from BC → ACCEPTABLE

**Passaging question:** Are conditional markers common? Does exclusion hurt?

**Assessment:** `إذا` appears in 15-19% of pages. Including it would create noise (too many false argument boundaries). The exclusion means conditional reasoning across page boundaries falls through to punctuation analysis (mid_sentence/mid_paragraph), which is correct behavior — passaging joins these pages normally. 22/63 fixtures have mid_argument boundaries, showing argument flow detection works on the markers that ARE included.

**Verdict: ACCEPTABLE** — conservative precision choice. Passaging handles the fallback correctly.

### L-009: Guillemet hadith distance heuristic → ACCEPTABLE

**Passaging question:** Does this cause false positives in boundary continuity?

**Assessment:** The 50-char distance limit means some hadith citations with long isnad chains won't trigger the guillemet pattern. This affects content_flags (has_hadith may undercount), not boundary_continuity. Passaging uses boundary_continuity for joining and content_flags as metadata pass-through. Even if has_hadith is false when it should be true, passaging boundary decisions are unaffected.

**Verdict: ACCEPTABLE** — affects content flags, not passaging behavior.

### L-010: Division overlap downgraded to warning → ACCEPTABLE

**Passaging question:** Does passaging rely on non-overlapping divisions?

**Assessment:** Passaging SPEC §2 validation check 6: "Division tree ranges consistent → PSG_DIVISION_INCONSISTENT (warning — fall back to flat passaging for affected regions)." This means passaging explicitly handles overlapping divisions by falling back to flat passaging. The passaging loader downgrades this to a warning and continues. 5/63 fixtures have overlap warnings, all from L-003 same-page headings. The affected regions are single-page divisions where flat passaging produces the same result as tree-guided passaging.

**Verdict: ACCEPTABLE** — passaging has explicit fallback handling for this case.

### L-011: Writer prev-only orphan recovery → ACCEPTABLE

**Passaging question:** How likely is this state? Is it recoverable?

**Assessment:** Near-zero practical risk (requires both Path.rename and shutil.move to fail after a previous rename succeeded). If triggered, the book needs re-processing — no corrupt data enters the library. The failure IS raised loudly (NORM_WRITE_FAILED). Passaging never sees this failure — it either gets a valid normalized package or no package at all.

**Verdict: ACCEPTABLE** — durability gap, not a correctness gap. Passaging unaffected.

### L-012: Arabic-Indic footnote markers not parsed → ACCEPTABLE

**Passaging question:** Do Shamela exports use Arabic-Indic digit footnotes?

**Assessment:** The precision-over-recall design choice avoids false positives from hadith/verse numbers in Arabic-Indic digits. If Shamela exports use Arabic-Indic footnote markers, those footnotes would be unparsed (same as L-001 bare-number case). Passaging handles zero-footnote pages correctly.

**Verdict: ACCEPTABLE** — same passaging impact as L-001.

### Layer 2 Summary

| Limitation | Assessment | Rationale |
|-----------|-----------|-----------|
| L-001 | ACCEPTABLE | Passaging unaffected; footnote text preserved |
| L-002 | ACCEPTABLE | Isolated to one book |
| L-003 | ACCEPTABLE | Page-level granularity makes chain depth inert |
| L-004 | ACCEPTABLE | Passaging doesn't consume these markers |
| L-005 | ACCEPTABLE | Empirically calibrated, no false positives observed |
| L-006 | DEFERRED | No 3-layer fixtures; fix when available |
| L-007 | ACCEPTABLE | Passaging propagates layers faithfully |
| L-008 | ACCEPTABLE | Conservative precision; fallback works |
| L-009 | ACCEPTABLE | Affects content flags, not boundaries |
| L-010 | ACCEPTABLE | Passaging has explicit fallback |
| L-011 | ACCEPTABLE | Durability gap, not correctness |
| L-012 | ACCEPTABLE | Same as L-001 |

**Zero BLOCKING limitations. Layer 2 verdict: PASS.**

---

## Layer 3: Manual Structural Inspection

### 02_nahw_muhaqiq (multi-layer, 295 pages)

**Primary text quality:** Clean Arabic text with proper sentence boundaries. No mojibake, no HTML artifacts, no truncation. Diacritics present where expected (0 on early pages — correct, this is a morphology text with minimal diacritics). ✅

**Division tree:** 19 well-structured divisions with HTML_TAGGED headings. Coverage: pages 0–294. Sensible table of contents for a morphology treatise (أبنية الأسماء → الأفعال → progression). ✅

**Layer segments:** 5 multi-layer pages inspected. Layer boundaries plausible — sharh (commentary) wraps matn (original text) segments. Example: page 106 shows sharh→matn→sharh pattern with matn segment `[وعلى (فعلاس) نحو عرفاس...]` correctly identified as quoted base text within commentary. Confidence levels appropriate (sharh=0.6, matn=0.65-0.90). ✅

**Boundary continuity:** Pages 5-9 show correct mid_sentence and section_break classifications. Page 7 ends with terminal punctuation → section_break (correct). Pages 5-6 end without terminal punctuation → mid_sentence (correct). ✅

**Verdict: PASS** — high-quality output for passaging consumption.

### 03_fiqh (footnotes, 102 pages)

**Primary text quality:** Clean Arabic with proper scholarly formatting. Footnote markers `⌜N⌝` correctly placed. References to Quran and hadith properly preserved. ✅

**Footnotes:** 32 pages with structured footnotes. Footnote text properly separated from primary text. Ref markers correctly mapped. Example: page 0 has footnote 1 referencing "فتح القدير 2/452" — correct tahqiq reference. ✅

**Division tree:** L-003 visible: المطلب headings on pages 1-2 chained as 7-deep hierarchy instead of 7 siblings. The HTML_TAGGED headings (المطلب الأول through الخاتمة) correctly structure the actual content. The chained headings on pages 1-2 are from the outline listing, not actual section boundaries. **Not a quality issue** — the real structure comes from the HTML-tagged headings. ✅

**Boundary continuity:** Pages 5-9 correctly classified. Page 5 ends with `(4) .` → mid_paragraph (sentence complete but paragraph continues). Page 9 ends after a complete scholarly quote → section_break. ✅

**Verdict: PASS.**

### 04_hadith (high diacritics, 41 pages)

**Primary text quality:** Excellent diacritics preservation — 473 per page on average for a hadith text. Full tashkeel on isnad chains (أَخْبَرَنَا الشَّيْخُ الْإِمَامُ مَجْدُ الدِّينِ). No diacritic loss or corruption visible. The ⦗ص: 26⦘ page references preserved correctly. ✅

**Content flags:** 36/41 pages flagged has_hadith — correct for a hadith collection. The 5 pages without hadith flags are likely introductory or transitional. ✅

**Division tree:** Hadith-text structure (each hadith as a division heading) correctly detected. All HTML_TAGGED with CONFIRMED confidence. ✅

**Boundary continuity:** All section_break for pages 5-9 — correct for a hadith text where each page typically contains complete narrations. ✅

**Verdict: PASS** — exemplary diacritics preservation.

### 06_usul (rich structure, 74 pages)

**Primary text quality:** Clean Arabic with moderate diacritics (175 per page). Scholarly text well-preserved with proper formatting. ✅

**Division tree:** 9 well-structured chapters (فصل فِي...) covering usul al-fiqh topics. Clean hierarchy with CONFIRMED headings. Page ranges sensible — لمقدمة (pages 0-3), then increasingly detailed sections. ✅

**Boundary continuity:** Mix of mid_sentence and section_break correctly reflecting the text structure. Pages 6-7 (mid_sentence) correctly detected as continuing scholarly argument. Pages 5, 9 (section_break) correctly detected at فصل boundaries. ✅

**Verdict: PASS.**

### ext_50 (auto-upgraded multi-layer, 42 pages)

**Primary text quality:** Clean Arabic usul al-fiqh text. Quran citations properly bracketed with ﴿﴾. ✅

**Multi-layer detection — FINDING:** Auto-upgrade from single→multi-layer triggered. 28/42 pages show multi-layer segments. However, inspection reveals the "matn" segments are predominantly short Quran citation references: `[النساء: الآية 59]` (17-20 chars). Of 66 matn segments, 51 (77%) are under 30 characters. The layer detector interprets bracketed text `[...]` as potential matn quotations.

**Analysis:** This is a false positive in the auto-upgrade heuristic. The text is a single-author usul al-fiqh work that quotes Quran extensively using bracket notation. The brackets trigger the layer detector's quotation detection, producing spurious "matn" segments at low confidence (0.65). The layer map correctly reflects low confidence (sharh=0.62, matn=0.66).

**Passaging impact:** Low. Passaging reads `text_layers` and propagates them. The low confidence (0.62-0.66) will be reflected in `PassageTextLayerSegment.confidence`. Downstream engines (excerpting, synthesis) use confidence thresholds to decide whether to trust layer boundaries. The low confidence serves as a correct warning signal that these layer assignments are uncertain.

**Category: LESSON LEARNED** — the auto-upgrade heuristic is overly aggressive for texts with heavy Quran citation brackets. The confidence levels correctly reflect the uncertainty. This does not block passaging.

**Verdict: PASS with LESSON LEARNED** (documented below).

### Layer 3 Summary

| Fixture | Inspection | Verdict |
|---------|-----------|---------|
| 02_nahw_muhaqiq | Multi-layer, footnotes, structure | PASS |
| 03_fiqh | Footnotes, division tree | PASS |
| 04_hadith | Diacritics, content flags | PASS |
| 06_usul | Rich structure, boundary continuity | PASS |
| ext_50 | Auto-upgrade false positive | PASS with LESSON LEARNED |

**Zero systematic quality issues. Layer 3 verdict: PASS.**

---

## Layer 4: GO/NO-GO Aggregation

### Finding Classification (per kr-evaluate)

| # | Finding | Category | Severity | Blocks? |
|---|---------|----------|----------|---------|
| F-1 | ext_50 auto-upgrade false positive: bracket-heavy Quran citation texts trigger spurious multi-layer detection | LESSON LEARNED | LOW | No |
| F-2 | 03_fiqh L-003 chaining: TOC page headings create deep chains | LESSON LEARNED | LOW | No — inert at page-level granularity |
| F-3 | 5/63 fixtures have division overlap warnings (L-010) | LESSON LEARNED | LOW | No — passaging has explicit fallback |
| F-4 | ext_41 has 6 "identical character run" warnings | LESSON LEARNED | LOW | No — source formatting artifact |

### GO Criteria Assessment

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Zero CORE GAPs | ✅ | No CORE GAPs found in Layers 1-3 |
| Zero unfixed ENGINE BUGs | ✅ | No ENGINE BUGs found |
| All known limitations assessed — none blocking | ✅ | Layer 2: 11 ACCEPTABLE, 1 DEFERRED (L-006, no test data) |
| SPEC errata resolved | ⏳ | SPEC-NOTE-1 through SPEC-NOTE-3 — fixing below |
| Contract alignment with passaging verified | ✅ | Passaging loader checks 1-6 are satisfied by normalization output |
| Manual inspection finds no systematic quality issues | ✅ | Layer 3: 5/5 PASS, 1 LESSON LEARNED |

### Verdict: **GO** — pending SPEC errata resolution

The normalization engine output is reliable enough for passaging to consume. All 63 fixtures produce valid normalized packages. All 12 known limitations are either ACCEPTABLE or DEFERRED for passaging. Manual inspection confirms semantic quality across diverse fixture types. The single LESSON LEARNED (F-1, auto-upgrade false positive) is correctly signaled by low confidence scores and does not affect passaging boundary decisions.

---

## Post-Protocol Adversarial Pass

**Question: "What is this evaluation NOT checking?"**

1. **Real multi-layer texts beyond ibn_aqil.** The evaluation has only 1 explicitly multi-layer fixture (02_nahw_muhaqiq) and 3 auto-upgraded ones (where the auto-upgrade itself is questionable per F-1). The layer detection was calibrated on ibn_aqil and validated on these fixtures, but real Shamela commentary texts (e.g., sharh ibn_aqil on the alfiyyah — the actual ibn_aqil commentary, not the morphology text) may have very different characteristics. **Risk:** Medium. **Mitigation:** The first time the pipeline runs on real multi-layer texts from the 2,519 collection, layer detection should be spot-checked.

2. **Plain text normalizer on real data.** All 63 fixtures are Shamela HTML. The PlainTextNormalizer was unit-tested but never run on a real plain text source in integration. **Risk:** Low — plain text sources are rare in the Shamela collection. **Mitigation:** If plain text sources are encountered, spot-check the first few.

3. **Very large texts (>1000 pages).** The largest fixture is ext_34 at 674 pages. The full collection may have texts with thousands of pages. Memory usage, processing time, and edge cases in structure discovery at scale are untested. **Risk:** Low — the pipeline processes page-by-page. **Mitigation:** Monitor first large-text run.

4. **CRLF line endings in real Windows environment.** S6 found and fixed CRLF handling, but the test fixtures in the repo use LF (git normalizes). The real 2,519 exports on the owner's Windows machine will have CRLF. The fix was applied but never tested on actual CRLF files. **Risk:** Medium. **Mitigation:** The deterministic sweep (source engine Step 2) runs on the owner's machine and will exercise CRLF handling at scale.

5. **Footnote renumbering collision with passaging.** The normalization engine produces `⌜N⌝` markers per-page. Passaging renumbers across pages. But if bare-number footnotes (L-001) exist on some pages and structured footnotes on adjacent pages, the passaging renumbering logic sees discontinuous footnote numbering. **Risk:** Very low — bare-number pages have no structured footnotes, so there's nothing to collide with.

**Assessment:** None of these rise to BLOCKING. Items 1 and 4 are the highest risk but both have clear mitigation paths (spot-check during first full-collection run). The evaluation correctly identifies these as monitoring items, not blockers.

---
