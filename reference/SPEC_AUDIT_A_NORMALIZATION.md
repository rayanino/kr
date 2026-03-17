# SPEC Audit A — Normalization Engine

**Auditor:** A (Patterns 1-4)
**SPEC file:** engines/normalization/SPEC.md
**Date:** 2026-03-17

## Summary
- Total defects: 19
- CORRECTNESS: 14 (74%)
- STYLE: 5 (26%)
- Sections with 0 defects: [none — every section had at least one finding after Round 1 trace]

## Defect Inventory

### D-A01 [CORRECTNESS] — Pattern 4 (Phantom Metadata) — §5 check 14
**Location:** Line 1505
**The SPEC says:** "If the source is classified as `unvocalized` or `partially_vocalized` in the source metadata, but the OCR output has diacritics density >0.06, trigger `NORM_OCR_DIACRITICS_HALLUCINATION`"
**The problem:** The source engine's `SourceMetadata` contract (engines/source/contracts.py) has no `unvocalized` or `partially_vocalized` classification field. The `TextFidelity` enum has values `high/medium/low/unknown`. There is no vocalization level field anywhere in the source metadata schema. The normalization engine cannot check a field that does not exist upstream.
**Evidence:** Grepped `engines/source/contracts.py` and the entire `engines/source/` directory for `unvocalized`, `partially_vocalized`, `diacritization`, `vocalization` — zero matches.
**Suggested fix:** Either (a) add a `vocalization_level` field to source engine's `SourceMetadata` with values `fully_vocalized/partially_vocalized/unvocalized/unknown`, or (b) change this check to infer vocalization level from the first N pages of OCR output rather than relying on upstream metadata.

### D-A02 [CORRECTNESS] — Pattern 4 (Phantom Metadata) — §4.A.4d
**Location:** Line 481
**The SPEC says:** "marks detected quotations in content_flags as `has_embedded_scholarly_quotation: true`"
**The problem:** The `ContentFlags` model in `engines/normalization/contracts.py` (line 215-223) defines exactly 7 boolean flags: `has_verse`, `has_table`, `has_quran_citation`, `has_hadith_citation`, `is_toc_page`, `is_index_page`, `is_blank`. There is no `has_embedded_scholarly_quotation` flag. The SPEC invents a field that the contract does not define.
**Evidence:** Grepped `engines/normalization/contracts.py` for `has_embedded_scholarly_quotation` and `owner_content` — zero matches.
**Suggested fix:** Add `has_embedded_scholarly_quotation: bool = False` to `ContentFlags` in contracts.py, or define it as a separate field on ContentUnit rather than inside ContentFlags.

### D-A03 [CORRECTNESS] — Pattern 4 (Phantom Metadata) — §7 / Appendix A.5 OCR Scenario 2
**Location:** Line 1580, 1909-1910
**The SPEC says:** "Set `content_flags.table_structure_preserved: false`" and defines `NORM_TABLE_STRUCTURE_LOST`
**The problem:** The `ContentFlags` model has no `table_structure_preserved` field. The SPEC also references a `table_data` structured field in the content unit ("the normalizer extracts the table as structured data (`table_data` field in the content unit)") — this field does not exist in the `ContentUnit` model.
**Evidence:** Grepped `engines/normalization/contracts.py` for `table_structure_preserved` and `table_data` — zero matches.
**Suggested fix:** Add `table_structure_preserved: bool = True` to `ContentFlags` and add `table_data: Optional[list[dict]] = None` to `ContentUnit` in contracts.py.

### D-A04 [CORRECTNESS] — Pattern 4 (Phantom Metadata) — §4.A.4d
**Location:** Line 478
**The SPEC says:** "`text_layers` contains one entry with `layer_type: 'owner_content'`"
**The problem:** The `LayerType` enum in `engines/normalization/contracts.py` (line 33-39) defines: `matn`, `sharh`, `hashiyah`, `tahqiq_note`, `uncertain`. There is no `owner_content` value. An implementation following this SPEC rule would fail Pydantic validation.
**Evidence:** The enum is exhaustive at 5 values, none matching `owner_content`.
**Suggested fix:** Either add `OWNER_CONTENT = "owner_content"` to `LayerType` enum, or specify that owner-authored content uses `layer_type: "matn"` (since the owner is the sole author).

### D-A05 [CORRECTNESS] — Pattern 4 (Phantom Metadata) — §4.B.6 / Passaging §2
**Location:** Passaging SPEC line 30
**The SPEC says (passaging §2):** "`layer_map` — detected text layers for multi-layer sources. Each entry: `layer_type`, `author_canonical_id`, `markers`, `confidence`."
**The problem:** The normalization engine's `LayerMapEntry` model (contracts.py line 484-491) has fields: `layer_type`, `author_canonical_id`, `author_name_arabic`, `detection_confidence`. The passaging SPEC expects a `markers` field that does not exist, and uses `confidence` where the contract calls it `detection_confidence`. This is a cross-boundary name mismatch.
**Evidence:** The passaging engine would fail if it accessed `entry.markers` or `entry.confidence` on a `LayerMapEntry`.
**Suggested fix:** Either (a) add `markers: Optional[list[str]] = None` to `LayerMapEntry` and rename `detection_confidence` to `confidence`, or (b) update passaging SPEC §2 to match the actual field names.

### D-A06 [CORRECTNESS] — Pattern 4 (Phantom Metadata) — §4.A.6 (Division Tree)
**Location:** Lines 556-608
**The SPEC says:** Division tree nodes have `div_id`, `type` (one of: كتاب, باب, فصل, ..., implicit, volume, root), `title`, `level`, `detection_method`, `confidence`, `start_unit_index`, `end_unit_index`, `parent_div_id`, `child_div_ids`, `page_hint_start`, `page_hint_end`, `digestible`, `editor_inserted`.
**The problem:** The `DivisionNode` model in contracts.py (line 466-477) has only: `heading_text`, `heading_level`, `start_unit_index`, `end_unit_index`, `detection_method`, `confidence`, `children`. The SPEC defines 14 fields; the contract defines 7. Missing from contract: `div_id`, `type`, `parent_div_id`, `child_div_ids`, `page_hint_start`, `page_hint_end`, `digestible`, `editor_inserted`. The passaging SPEC §2 notes it generates `div_id` itself, which partially compensates, but the SPEC's own example output (line 593-608) includes `div_id`, `type`, `digestible`, `editor_inserted` as if produced by normalization.
**Evidence:** Concrete example at line 593 shows `"div_id": "kitab_tahara"` and `"type": "كتاب"` as normalization output, but contracts.py has neither field.
**Suggested fix:** Either expand `DivisionNode` in contracts.py to match the SPEC's 14-field definition, or simplify the SPEC to match the 7-field contract. Since the passaging engine generates its own `div_id`, the SPEC example should not show pre-generated `div_id` values.

### D-A07 [CORRECTNESS] — Pattern 1 (Hollow Example) — §4.A.5
**Location:** Lines 531-550
**The SPEC says (concrete example):** The example shows layer detection on a حاشية ابن قاسم text, assigning "sharh" to "بهوتي" (lines 543-544: `"layer_type": "sharh", "author_canonical_id": "buhuti_1051"`). But the text starts with "قوله:" which the SPEC itself says (line 507) is "typically introduces Layer 1 text within Layer 2."
**The problem:** The example assigns "قوله: ويصح الوضوء بماء البحر" as sharh (Layer 2) attributed to البهوتي, then the matn portion starts at offset 6. But "قوله:" IS the sharh author quoting the matn — the sharh author writes "قوله:" and then the matn text follows. The example says offset 0-5 is "sharh" and 6-35 is "matn," but offset 0-5 is just "قوله:" (5 chars) while the actual text at those characters is "قوله:" — a mixed attribution marker, not pure sharh content. A wrong implementation that attributes "قوله:" to matn (because it introduces matn text) would also produce a plausible output. The character offsets also appear inconsistent with the text length.
**Evidence:** The text "قوله: ويصح الوضوء بماء البحر." is approximately 30 characters. The example claims matn ends at offset 35, sharh starts at 36 — but the hadith citation that follows is attributed to sharh even though it is a quotation from the Prophet, which is evidence used by the sharh author. The example is not wrong per se, but a different (also reasonable) segmentation would also pass.
**Suggested fix:** Make the example more discriminating by showing a case where WRONG attribution would produce visibly different output (e.g., include the confidence difference or show that attributing "قوله:" to matn vs sharh changes the downstream scholarly claim).

### D-A08 [CORRECTNESS] — Pattern 3 (Hand-Waving Technology) — §4.B.5
**Location:** Lines 896, 899
**The SPEC says:** "`technical_term_density` (float, proportion of words matching the KR technical glossary for this source's science classification)"
**The problem:** The "KR technical glossary" is referenced as if it already exists — "a pre-built set of ~500-2000 terms per science" (line 899). This glossary does not exist anywhere in the repository. It is a dependency that must be created before this feature can work. The SPEC treats it as available infrastructure rather than a deliverable.
**Evidence:** No file matching "glossary" or "technical_terms" exists in the repo. The feature depends on per-science term lists (fiqh, nahw, usul, hadith, etc.) that have not been built. Without these lists, `technical_term_density` cannot be computed, making the entire `vocabulary_profile` field partially phantom.
**Suggested fix:** Mark the KR technical glossary as a prerequisite deliverable with its own specification. Until the glossary exists, `technical_term_density` should be nullable or have a fallback computation method (e.g., morphological analysis for term density approximation).

### D-A09 [CORRECTNESS] — Pattern 3 (Hand-Waving Technology) — §4.A.4
**Location:** Lines 361-362
**The SPEC says:** "Flag potential confusions using CAMeL Tools morphological analysis (do NOT auto-correct — flag for downstream review)."
**The problem:** CAMeL Tools is a real NLP toolkit for Arabic, but its morphological analyzer (`camel_tools.morphology`) performs morphological disambiguation for Modern Standard Arabic. Its coverage of classical Arabic (fus-ha with archaic forms, rare verb forms like form X-XV, unusual broken plurals) is limited. Classical fiqh texts routinely use terminology that CAMeL Tools would mark as invalid (e.g., "مُسْتَحِبّ" in a non-standard vocalization, or technical terms like "مُتَيَمِّم" that may not be in its lexicon). Using CAMeL Tools as a morphological validator on classical scholarly Arabic would produce false positives (flagging valid classical terms as invalid).
**Evidence:** CAMeL Tools is trained primarily on MSA corpora (PATB, MADAMIRA training data). Classical Arabic scholarly vocabulary has significant divergence from MSA. The SPEC does not acknowledge this coverage gap or specify a fallback.
**Suggested fix:** Acknowledge the classical Arabic coverage limitation. Specify that morphological validation uses CAMeL Tools as a first pass, but terms not found in the CAMeL lexicon are NOT automatically flagged as errors — they are passed to an Arabic scholarly term lookup (or simply marked as "outside MSA lexicon, possibly classical"). Alternatively, specify Farasa or another tool with better classical coverage.

### D-A10 [CORRECTNESS] — Pattern 3 (Hand-Waving Technology) — §4.B.5
**Location:** Line 896
**The SPEC says:** "`estimated_unique_terms` (int, approximated from a random sample of 20 pages using HyperLogLog)"
**The problem:** HyperLogLog is a cardinality estimation algorithm that works well at large scale (millions of items) with configurable precision. For a sample of 20 pages (~40,000 words for a typical source), the total vocabulary might be 5,000-15,000 unique terms. HyperLogLog with precision 14 has ~0.8% standard error, which is fine — BUT the SPEC says it processes "word tokens from a random sample of 20 content units." If the source has 800 pages and you sample 20, you are estimating the vocabulary of the SAMPLE, not the SOURCE. The estimate is biased low because you have not seen rare terms from the other 780 pages. The SPEC conflates "sample vocabulary estimation" with "source vocabulary estimation" without specifying a correction factor or acknowledging the sampling bias.
**Evidence:** HyperLogLog gives accurate cardinality of the items it HAS SEEN. It does not extrapolate to unseen items. The "~0.8% standard error" claim (line 896) applies to the estimation error of the HyperLogLog sketch, not to the sampling error from reading only 20 of 800 pages.
**Suggested fix:** Either (a) specify that `estimated_unique_terms` is the sample vocabulary, not total vocabulary, and rename to `sample_unique_terms`, or (b) apply a species richness estimator (e.g., Chao1 or Good-Turing) to extrapolate total vocabulary from the sample, or (c) process all pages instead of sampling (HyperLogLog is O(n) and can handle 800 pages easily).

### D-A11 [CORRECTNESS] — Pattern 1 (Hollow Example) — §4.A.9
**Location:** Lines 667-689
**The SPEC says (content flagging example):** The example shows a page with Quran citation and hadith citation, correctly flagging both. `has_verse: false` because this is prose with embedded citations, not verse.
**The problem:** The example is hollow — it tests only the "true positive" case for two flags and the "true negative" for five others. A WRONG implementation that flags `has_quran_citation: true` for ANY Arabic text containing curly braces `{}` (not just Quran citations) would pass this example. Similarly, an implementation that flags `has_hadith_citation: true` whenever "رواه" appears (even in non-hadith contexts like "رواه عنه أصحابه" meaning "his companions narrated it from him" in a biographical context) would pass.
**Evidence:** The example does not include a NEGATIVE case for `has_quran_citation` where curly braces appear in non-Quranic context (e.g., mathematical notation `{1, 2, 3}`), nor a negative case for `has_hadith_citation` where "رواه" appears in a non-hadith-citation context. A wrong implementation that over-flags would pass every example.
**Suggested fix:** Add at least one negative example: a page with "رواه" in a non-hadith context that should NOT trigger `has_hadith_citation`, and a page with Arabic text in curly braces that is NOT a Quran citation.

### D-A12 [STYLE] — Pattern 2 (Circular Definition) — §4.B.1
**Location:** Lines 695-700
**The SPEC says:** "The normalization engine trains an LLM-based layer classifier that operates on a sliding window of text."
**The problem:** The word "trains" is misleading. The SPEC then describes a zero-shot or few-shot LLM prompt, not a trained model. There is no training dataset, no training procedure, no model weights. The classifier "receives: a ~500-word window, the source's known layer composition... and examples of each layer's writing style from the same source (bootstrapped from high-confidence detections in earlier pages)." This is in-context learning (prompting), not training. The confusion between "training" and "prompting" could lead an implementer to attempt actual model fine-tuning.
**Suggested fix:** Replace "trains an LLM-based layer classifier" with "uses an LLM-based layer classifier via in-context learning" or "prompts an LLM to classify layers."

### D-A13 [CORRECTNESS] — Pattern 1 (Hollow Example) — §4.A.2 (Shamela Normalizer, concrete example)
**Location:** Lines 242-279
**The SPEC says:** The example shows a single page from شرح ابن عقيل. The `primary_text` includes `⌜1⌝ قال ابن مالك رحمه الله في التسهيل ما يدل على هذا.` The footnote marker `⌜1⌝` is placed inline.
**The problem:** The footnote reference `(1)` in the source HTML appears AFTER the footnote separator `<hr width='95'>`, but the text "قال ابن مالك رحمه الله في التسهيل ما يدل على هذا." appears BEFORE the separator. The `(1)` in the HTML source is inside the primary text region: `(1) قال ابن مالك رحمه الله في التسهيل ما يدل على هذا.` This `(1)` is a footnote REFERENCE, not the footnote itself. The normalizer should replace it with `⌜1⌝`. However, a WRONG implementation that treats ANY `(N)` pattern as a footnote reference (including `(N)` in mathematical or enumeration contexts like "the three conditions are: (1)... (2)... (3)...") would also pass this example. The example does not test the case where `(N)` appears in text but is NOT a footnote reference.
**Evidence:** The example only shows the happy path. A wrong implementation with overly aggressive `(N)` pattern matching would produce identical output for this example.
**Suggested fix:** Add an example page where `(N)` appears in an enumeration context (not a footnote reference) and show that the normalizer preserves it as literal text.

### D-A14 [CORRECTNESS] — Pattern 4 (Phantom Metadata) — §4.B.6
**Location:** Line 1002
**The SPEC says:** "The orchestrator logs which engine processed each page in the content unit's metadata: `ocr_engine` field (already present in fidelity data)."
**The problem:** The `TextFidelity` model in contracts.py (line 226-231) has fields: `score`, `ocr_confidence`, `warnings`. There is no `ocr_engine` field. The SPEC claims this field is "already present" but it does not exist in the contract.
**Evidence:** Grepped `engines/normalization/contracts.py` for `ocr_engine` — zero matches.
**Suggested fix:** Add `ocr_engine: Optional[str] = None` to the `TextFidelity` model, or create a separate `OcrMetadata` model on `ContentUnit`.

### D-A15 [STYLE] — Pattern 2 (Circular Definition) — §4.B.9
**Location:** Lines 1216-1298 (authorial voice fingerprint)
**The SPEC says:** "The fingerprint provides statistical evidence that the layer attribution is correct by showing that text attributed to each layer exhibits consistent, distinguishable writing characteristics."
**The problem:** The fingerprint validates layer attribution by checking that attributed text has distinct style. But the style distinctness is itself a product of the attribution. If attribution is wrong (e.g., 25% of sharh text is misattributed to matn), the fingerprint will show a matn fingerprint that is slightly corrupted but not dramatically different — because 75% of the data is correct. The fingerprint validates ITSELF: "the attribution is correct because the fingerprint says the attributed text looks consistent." The circular dependency is: fingerprint quality depends on attribution quality, and attribution confidence depends on fingerprint validation. The SPEC acknowledges this partially (Appendix A.4, Attack 1) but does not break the circularity.
**Suggested fix:** Explicitly state that fingerprint validation is a WEAK check — it catches gross errors (full layer inversion) but cannot detect moderate corruption (15-25% misattribution). Specify the minimum misattribution rate the fingerprint can reliably detect (e.g., "fingerprint validation detects layer inversion (>50% misattribution) with high confidence but may miss corruption below 25%").

### D-A16 [CORRECTNESS] — Pattern 3 (Hand-Waving Technology) — §4.A.4 / §4.B.6
**Location:** Lines 960-968
**The SPEC says:** "QARI-OCR v0.2 (local, Qwen2-VL-2B fine-tuned): Best diacritics handling (CER 0.061)"
**The problem:** QARI-OCR v0.2 is described as a Qwen2-VL-2B fine-tune. The CER 0.061 figure is cited without specifying the evaluation dataset. If this was measured on a modern Arabic OCR benchmark (e.g., KHATT), the performance on degraded classical scholarly manuscripts (with marginal notes, inter-linear annotations, and archaic typefaces) could be significantly worse. The SPEC uses this CER figure to justify routing diacritics-heavy pages to QARI-OCR, but the benchmark may not represent the actual use case (classical scholarly texts with heavy tashkeel in old print editions). Similarly, Baseer's WER 0.25 figure and PaddleOCR-VL's 94.5% OmniDocBench figure are not qualified by whether those benchmarks include Arabic text at all.
**Evidence:** OmniDocBench is primarily English-focused. A 94.5% score on OmniDocBench does not guarantee Arabic performance. The engine selection matrix (lines 979-989) makes routing decisions based on these unqualified benchmarks.
**Suggested fix:** Add a caveat that benchmark figures are from general evaluations and may not reflect classical Arabic scholarly text performance. Specify that the engine selection matrix must be validated empirically on the KR test fixtures before being trusted for production routing.

### D-A17 [STYLE] — Pattern 2 (Circular Definition) — §4.B.10
**Location:** Lines 1440-1444 (edge cases)
**The SPEC says:** "the detection algorithm uses quotation detection (guillemets «», explicit 'قال فلان:' introductions) to suppress marker detection within quoted passages."
**The problem:** The detection of quotation boundaries depends on detecting "قال فلان:" patterns. But "قال" is itself one of the discourse markers listed in §4.A.5 line 518 as an opinion-reporting verb used for layer detection. The same marker ("قال") is used for two different purposes: (1) detecting layer transitions (§4.A.5), and (2) detecting quotation boundaries for discourse suppression (§4.B.10). An implementer must decide WHICH interpretation to apply when encountering "قال الشافعي:" — is it a layer transition marker or a quotation introduction? The SPEC does not specify priority between these two uses.
**Suggested fix:** Specify that §4.A.5 layer detection runs BEFORE §4.B.10 discourse detection (per Pass 6 ordering, this is already the case), and that quotation detection in §4.B.10 operates on text that has ALREADY been layer-attributed. This removes the ambiguity.

### D-A18 [STYLE] — Pattern 1 (Hollow Example) — §4.A.8
**Location:** Lines 643-651
**The SPEC says:** "Whitespace normalization (conservative): `\r\n`/`\r` → `\n`. Non-breaking spaces → regular spaces. 2+ consecutive spaces → single space. Three+ blank lines → one blank line. Leading/trailing line whitespace trimmed."
**The problem:** The diacritics preservation rule says "No Unicode normalization." But whitespace normalization involves modifying characters (non-breaking space U+00A0 → regular space U+0020). The SPEC defines this as acceptable and not contradictory. However, Arabic text occasionally uses other Unicode space characters (e.g., zero-width non-joiner U+200C, which the SPEC says to preserve in §4.A.2 Pass 3 "Preserve... ZWNJ characters"). The whitespace normalization rule does not enumerate which whitespace characters are normalized and which are preserved. Is em-space (U+2003) normalized? Thin space (U+2009)? Hair space (U+200A)? An implementer must guess.
**Suggested fix:** Enumerate the exact set of whitespace characters that are normalized to regular spaces. At minimum: U+00A0 (NBSP), U+2000-U+200A (various typographic spaces). Explicitly exclude U+200C (ZWNJ) and U+200D (ZWJ) from normalization.

### D-A19 [STYLE] — Pattern 4 (Phantom Metadata) — §4.B.10
**Location:** Lines 1442, 1783
**The SPEC says:** "Markers inside quotes are annotated as `quoted_discourse`"
**The problem:** The `DiscourseDetectionMethod` enum in contracts.py (line 305-308) has only two values: `MARKER` and `LLM_INFERRED`. There is no `QUOTED_DISCOURSE` or `quoted_discourse` value. The SPEC references annotating markers "as `quoted_discourse`" but does not specify WHERE this annotation goes — is it a new `detection_method` value? A separate field? A flag on the `DiscourseSegment`?
**Evidence:** Grepped contracts.py for `quoted_discourse` — zero matches.
**Suggested fix:** Either add `QUOTED_DISCOURSE = "quoted_discourse"` to `DiscourseDetectionMethod`, or add a `is_quoted: bool = False` field to `DiscourseSegment`, or specify that quoted discourse segments are simply excluded from the segments array.

## Self-Review Notes

### Round 1

For sections where initial pass found fewer defects, I traced through شرح ابن عقيل على ألفية ابن مالك as the test case:

**§4.A.5 (Multi-layer detection) trace:** شرح ابن عقيل is a 2-layer commentary (matn by ابن مالك, sharh by ابن عقيل). The Shamela export uses bold for matn (ألفية verses). Pass 5 detects bold spans as Layer 1. The ألفية is a نظم (versified text), so matn lines are individual verses. The bold-for-emphasis disambiguation rule (span length heuristic) works here because ألفية verses are full lines, not individual words — they pass the "1-3 sentences of terse, definitional text" criterion. However, what about pages where ابن عقيل quotes a long hadith and bolds it for emphasis? The span-length heuristic might misclassify a 2-sentence hadith quotation as matn. This is partially caught by the <5%/>60% page-level proportion check, but a single page with a long bolded hadith could still be misattributed. This confirmed existing D-A07 about the example being hollow.

**§4.A.6 (Structure discovery) trace:** شرح ابن عقيل follows the ألفية's structure: each بيت is commented on sequentially. The source has no traditional باب/فصل divisions — the structure IS the ألفية's verse sequence. The Shamela export likely has `<span class="title">` tags for chapter headings (e.g., "المبتدأ والخبر"). Tier 1 detection works. But what about the ألفية's verse numbers? Are verse numbers treated as headings? The SPEC does not address this. Verse numbers in a نظم source are NOT structural headings — they are positional markers within a continuous poetic text. An implementation that treats "البيت الخامس والسبعون" as a Tier 2 heading would create 1000+ divisions (one per verse), which is wrong. This is an edge case that the SPEC does not address, but it falls outside patterns 1-4 (it is a missing rule, not a hollow example or phantom metadata).

**§4.B.8 (Cross-page continuity) trace:** In شرح ابن عقيل, pages often end mid-explanation. The sharh for one verse spans multiple pages. The continuity detector should mark most page boundaries as `mid_paragraph` or `mid_argument`. The concrete example in §4.B.8 is absent from the SPEC — this section has no example at all (the SPEC references it via the cross-validation in Pass 6 step 9 but provides no standalone example). Without an example, any implementation of continuity detection could claim compliance. This is a hollow-example-by-absence situation.

### Round 2

Defect classification check:
- CORRECTNESS defects: D-A01, D-A02, D-A03, D-A04, D-A05, D-A06, D-A07, D-A08, D-A09, D-A10, D-A11, D-A13, D-A14, D-A16 = 14 (74%)
- STYLE defects: D-A12, D-A15, D-A17, D-A18, D-A19 = 5 (26%)

The 74% CORRECTNESS ratio satisfies the >20% threshold. The CORRECTNESS defects cluster in two categories: (1) phantom metadata — fields referenced in the SPEC that do not exist in the contracts (D-A01, A02, A03, A04, A05, A06, A14, A19 = 8 phantom metadata defects, the dominant pattern), and (2) hand-waving technology / hollow examples (D-A07, A08, A09, A10, A11, A13, A16 = 7 defects). The phantom metadata cluster is the highest-priority finding: these represent build-blocking defects where an implementer following the SPEC would write code referencing non-existent fields.
