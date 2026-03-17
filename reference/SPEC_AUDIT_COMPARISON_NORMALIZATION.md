# Audit Comparison — Normalization Engine

**Date:** 2026-03-17
**Auditor A findings:** 19 (Patterns 1-4)
**Auditor B findings:** 27 (Patterns 5-7, Threats T1-T7)
**After merge:** 35 unique defects

## Classification Summary

| Category | Count | % |
|----------|-------|---|
| BOTH_FOUND | 8 | 23% |
| A_ONLY (confirmed) | 9 | 26% |
| A_ONLY (false positive) | 2 | 6% |
| B_ONLY (confirmed) | 14 | 40% |
| B_ONLY (false positive) | 2 | 6% |

## Section-by-Section Map

| SPEC Section | Auditor A | Auditor B |
|---|---|---|
| §2 (Input) | - | - |
| §3 (Output / Enrichment) | - | D-B06 |
| §4.A.2 (Shamela, Pass 1) | - | D-B10 |
| §4.A.2 (Shamela, Pass 2) | D-A13 | D-B17 |
| §4.A.2 (Shamela, Pass 3) | - | D-B04 |
| §4.A.2 (Shamela, atomic write) | - | D-B20 |
| §4.A.3 (PDF text) | - | D-B01 |
| §4.A.4 (OCR) | D-A09, D-A16 | D-B13, D-B22 |
| §4.A.4d (Owner content) | D-A02, D-A04 | - |
| §4.A.5 (Multi-layer) | D-A05, D-A07 | D-B03, D-B11, D-B27 |
| §4.A.6 (Structure) | D-A06 | D-B12, D-B25 |
| §4.A.8 (Diacritics/whitespace) | D-A18 | D-B07 |
| §4.A.9 (Content flagging) | D-A11 | D-B08 |
| §4.B.1 (Layer intelligence) | D-A12 | D-B02 |
| §4.B.2 (Format auto-detect) | - | D-B19 |
| §4.B.3 (Fidelity mapping) | - | D-B14 |
| §4.B.4 (Footnote classification) | - | D-B09 |
| §4.B.5 (Content census) | D-A08, D-A10 | D-B18 |
| §4.B.6 (OCR orchestration) | D-A14 | - |
| §4.B.7 (Tahqiq topology) | - | D-B16 |
| §4.B.8 (Cross-page continuity) | - | D-B15 |
| §4.B.9 (Voice fingerprint) | D-A15 | D-B21, D-B23 |
| §4.B.10 (Discourse flow) | D-A17, D-A19 | D-B05, D-B26 |
| §4.A.6 / §4.B.6 (division tree) | D-A03 | - |
| §5 (Validation) | D-A01 | D-B24 |

## Merged Defect List

---

### M-01 [CORRECTNESS] — §4.A.8 / Whitespace normalization — BOTH_FOUND
**Source:** D-A18 + D-B07
**Patterns:** A: Pattern 1 (Hollow Example) / B: Pattern 6 (Missing Error Path) + T-1
**The SPEC says:** "Non-breaking spaces -> regular spaces. 2+ consecutive spaces -> single space." (line 651) and separately "Preserve asterisks, ZWNJ characters" (line 197).
**The problem:** Both auditors independently identified that the whitespace normalization rule fails to enumerate which Unicode whitespace characters are normalized vs. preserved. ZWNJ (U+200C) is used as heading marker in 9.5% of Shamela corpus; accidental normalization would corrupt headings AND primary text. Characters like thin space (U+2009), narrow no-break space (U+202F), zero-width space (U+200B), and BOM (U+FEFF) have undefined behavior.
**Suggested fix:** Enumerate the exact set: U+00A0 (NBSP) -> regular space. U+200C (ZWNJ) -> PRESERVED. U+200B (ZWSP) -> PRESERVED. U+FEFF (BOM) -> stripped only at file start. U+202F (narrow NBSP) -> regular space. All typographic spaces U+2000-U+200A -> regular space. Explicitly exclude ZWJ (U+200D) from normalization.

---

### M-02 [CORRECTNESS] — §4.A.9 / Content flagging — BOTH_FOUND
**Source:** D-A11 + D-B08
**Patterns:** A: Pattern 1 (Hollow Example) / B: Pattern 5 (Untestable Rule) + T-6
**The SPEC says:** "`has_hadith_citation`: hadith citation patterns detected ('قال النبي ﷺ', 'عن ... قال', collection references)." (line 660)
**The problem:** Both auditors flagged that hadith/Quran detection patterns are underspecified. The pattern "عن ... قال" matches almost any narrative Arabic sentence. The example only shows true positive cases; no negative examples test against false positives (e.g., "رواه" in biographical context, curly braces in non-Quranic context). A wrong implementation with overly aggressive matching would pass all examples.
**Suggested fix:** Define detection patterns precisely. Quran: "قال تعالى"/"قال الله" within 200 chars of curly-brace or guillemet text. Hadith: "قال النبي"/"قال رسول الله"/"عن النبي ﷺ" or guillemet text preceded by narrator chain, or explicit collection reference (البخاري, مسلم, etc. + number). Add negative examples to the SPEC.

---

### M-03 [CORRECTNESS] — §4.A.5 / Bold span heuristic — BOTH_FOUND
**Source:** D-A07 + D-B03
**Patterns:** A: Pattern 1 (Hollow Example) / B: Pattern 5 (Untestable Rule) + T-2
**The SPEC says:** "layer-indicating bold spans typically cover 1-3 sentences of terse, definitional text, while emphasis-bold covers individual words or phrases within longer sentences" (line 511)
**The problem:** Both auditors flagged the bold-span length heuristic as untestable/ambiguous. "Typically" is not a threshold. A matn segment of 35 characters is indistinguishable from an emphasized hadith quotation of 28 characters by length alone. A's example (D-A07) showed the concrete example is non-discriminating; B (D-B03) showed no character-count threshold exists.
**Suggested fix:** Define explicit character-count threshold (e.g., bold spans <80 chars are candidate emphasis, >=80 are candidate layer indicators), AND require cross-checking against transition marker list before classification.

---

### M-04 [CORRECTNESS] — §4.A.5 / Content-based inference signals — BOTH_FOUND
**Source:** D-A07 (partially) + D-B11
**Patterns:** A: Pattern 1 / B: Pattern 5 + T-2
**The SPEC says:** "Terse, definitional text -> likely Layer 1 (matn). Explanatory, discursive text -> likely Layer 2 (sharh). Opinion reporting verbs (قال, ذهب, يرى) -> likely Layer 2." (lines 516-518)
**The problem:** Both auditors flagged that "terse" and "explanatory, discursive" are untestable subjective criteria. Additionally, "قال" appears in BOTH layers (matn author reporting positions vs. sharh author citing matn). Using "قال" as a blanket Layer 2 signal would misclassify matn text.
**Suggested fix:** Replace subjective criteria with quantitative metrics (sentence length <15 words, information density >0.65 -> likely matn). Refine "قال" heuristic: "قال المصنف/قال الشيخ" -> Layer 2 reference to matn. "قال أبو حنيفة/قال مالك" -> ambiguous, do not use as layer signal alone. Specify that content-based inference is NEVER used alone.

---

### M-05 [STYLE] — §4.B.1 / "trains" vs. prompts — BOTH_FOUND
**Source:** D-A12 + D-B02
**Patterns:** A: Pattern 2 (Circular Definition) / B: Pattern 7 (Scope Creep) + T-2
**The SPEC says:** "The normalization engine trains an LLM-based layer classifier that operates on a sliding window of text." (line 697)
**The problem:** A flagged the misleading use of "trains" (it is in-context learning, not model training). B flagged the scope creep (NLP capabilities not specified as dependencies, bootstrapping failure path undefined, content-based layer attribution needs consensus per D-041). Both are valid concerns about the same section.
**Suggested fix:** (1) Replace "trains" with "uses via in-context learning." (2) Define bootstrapping failure: if <5 high-confidence segments found, skip §4.B.1, process as single-layer with human gate. (3) Require consensus for content-based layer inference since it is an attribution decision. (4) List NLP dependencies explicitly.

---

### M-06 [CORRECTNESS] — §4.B.9 / Fingerprint circularity and thresholds — BOTH_FOUND
**Source:** D-A15 + D-B21
**Patterns:** A: Pattern 2 (Circular Definition) / B: Pattern 5 (Untestable Rule)
**The SPEC says:** "Pages where the local fingerprint diverges by >2.5 standard deviations from the global fingerprint are flagged as potential misattribution." (line 1267)
**The problem:** A identified the circular dependency (fingerprint validates attribution which created the fingerprint). B identified the 2.5 SD threshold as unjustified and too permissive (would flag only ~0.6% of pages even with random fingerprints; 15% misattribution would be missed). Both point to the same weakness: the fingerprint is a weak validation mechanism presented as strong.
**Suggested fix:** (1) Explicitly state fingerprint validation is a WEAK check that catches gross errors (>50% misattribution) but not moderate corruption. (2) Justify the threshold empirically or make it configurable. (3) Consider a more sensitive threshold (2.0 SD) with minimum-flagging rules.

---

### M-07 [CORRECTNESS] — §4.B.5 / KR technical glossary phantom — BOTH_FOUND
**Source:** D-A08 + (D-B18 tangentially)
**Patterns:** A: Pattern 3 (Hand-Waving Technology) / B: Pattern 5 (Untestable Rule)
**The SPEC says:** "`technical_term_density` (float, proportion of words matching the KR technical glossary for this source's science classification)" (line 896) / "a pre-built set of ~500-2000 terms per science" (line 899)
**The problem:** A directly flagged that the KR technical glossary does not exist anywhere in the repository. B flagged the hardcoded thresholds (200/3000 chars) without justification. Both concern the content census having dependencies or parameters that are ungrounded.
**Suggested fix:** Mark the KR technical glossary as a prerequisite deliverable. Until it exists, `technical_term_density` should be nullable. Add justification for all hardcoded thresholds or make them configurable in section 8.

---

### M-08 [CORRECTNESS] — §4.B.10 / Discourse flow scope and quoted markers — BOTH_FOUND
**Source:** D-A17 + D-B05
**Patterns:** A: Pattern 2 (Circular Definition) / B: Pattern 7 (Scope Creep) + T-3
**The SPEC says:** "the detection algorithm uses quotation detection... to suppress marker detection within quoted passages" (line 1442) / "the excerpting engine can extract a complete argument cycle as a single excerpt because the normalization engine has already identified where the cycle starts and ends" (line ~1300)
**The problem:** A flagged the "قال" ambiguity (same marker used for layer detection and quotation detection without priority). B flagged the fundamental scope creep (discourse flow annotation is taxonomic pre-classification; `school_hint` and `attribution_hint` are attribution decisions that belong downstream). Both identify that discourse flow annotation overreaches the normalization engine's format-transformation role.
**Suggested fix:** (1) Specify processing order: §4.A.5 layer detection before §4.B.10 discourse detection. (2) Remove `school_hint` and `attribution_hint` from discourse output (these are downstream decisions). (3) Mark discourse flow as ADVISORY with `discourse_annotation_authority: "advisory"`.

---

### M-09 [CORRECTNESS] — §5 check 14 / Phantom vocalization field — A_ONLY (confirmed)
**Source:** D-A01
**Patterns:** Pattern 4 (Phantom Metadata)
**The SPEC says:** "If the source is classified as `unvocalized` or `partially_vocalized` in the source metadata, but the OCR output has diacritics density >0.06, trigger `NORM_OCR_DIACRITICS_HALLUCINATION`" (line 1505)
**The problem:** The source engine's `SourceMetadata` has no `unvocalized` / `partially_vocalized` classification field. The `TextFidelity` enum has `high/medium/low/unknown`. This check references a field that does not exist upstream.
**Investigation:** B's patterns (5-7) focus on untestable rules, missing error paths, and scope creep -- not on contract mismatches. This is squarely a phantom metadata issue (Pattern 4) outside B's scope.
**Verdict:** CONFIRMED (scope-limited). Real defect, outside B's pattern coverage.
**Suggested fix:** Add a `vocalization_level` field to source engine's `SourceMetadata` with values `fully_vocalized/partially_vocalized/unvocalized/unknown`, or change this check to infer vocalization from the first N pages of OCR output.

---

### M-10 [CORRECTNESS] — §4.A.4d / Phantom `has_embedded_scholarly_quotation` — A_ONLY (confirmed)
**Source:** D-A02
**Patterns:** Pattern 4 (Phantom Metadata)
**The SPEC says:** "marks detected quotations in content_flags as `has_embedded_scholarly_quotation: true`" (line 481)
**The problem:** The `ContentFlags` model defines exactly 7 boolean flags. `has_embedded_scholarly_quotation` does not exist in the contract.
**Investigation:** B did not audit §4.A.4d (owner content normalizer, behavioral outline). This section received less attention as it is marked [NOT YET IMPLEMENTED].
**Verdict:** CONFIRMED (scope-limited). Build-blocking phantom field.
**Suggested fix:** Add `has_embedded_scholarly_quotation: bool = False` to `ContentFlags`.

---

### M-11 [CORRECTNESS] — §7 + §4.A.6 / Phantom `table_structure_preserved` and `table_data` — A_ONLY (confirmed)
**Source:** D-A03
**Patterns:** Pattern 4 (Phantom Metadata)
**The SPEC says:** "Set `content_flags.table_structure_preserved: false`" (line 1580) / "the normalizer extracts the table as structured data (`table_data` field)" (line ~1909)
**The problem:** Neither `table_structure_preserved` nor `table_data` exist in the `ContentFlags` or `ContentUnit` contracts.
**Investigation:** B did not flag this specific contract-vs-SPEC mismatch, though B's D-B01 covers a related area (PDF parser error paths). Phantom metadata is outside B's patterns.
**Verdict:** CONFIRMED (scope-limited). Build-blocking phantom fields.
**Suggested fix:** Add both fields to contracts.py.

---

### M-12 [CORRECTNESS] — §4.A.4d / Phantom `owner_content` LayerType — A_ONLY (confirmed)
**Source:** D-A04
**Patterns:** Pattern 4 (Phantom Metadata)
**The SPEC says:** "`text_layers` contains one entry with `layer_type: 'owner_content'`" (line 478)
**The problem:** `LayerType` enum defines: `matn`, `sharh`, `hashiyah`, `tahqiq_note`, `uncertain`. No `owner_content`.
**Investigation:** Same scope limitation as M-10 (§4.A.4d, behavioral outline section).
**Verdict:** CONFIRMED (scope-limited). Pydantic validation would reject this value.
**Suggested fix:** Add `OWNER_CONTENT = "owner_content"` to `LayerType` enum.

---

### M-13 [CORRECTNESS] — §4.B.6 / Passaging contract field name mismatch — A_ONLY (confirmed)
**Source:** D-A05
**Patterns:** Pattern 4 (Phantom Metadata)
**The SPEC says (passaging §2):** "`layer_map` ... Each entry: `layer_type`, `author_canonical_id`, `markers`, `confidence`."
**The problem:** The normalization engine's `LayerMapEntry` has `detection_confidence` (not `confidence`) and lacks `markers`. Cross-boundary field name mismatch.
**Investigation:** B's patterns focus within a single SPEC, not cross-engine contract validation. This is outside B's scope.
**Verdict:** CONFIRMED (scope-limited). Would cause downstream field access failures.
**Suggested fix:** Align field names between normalization output and passaging input contracts.

---

### M-14 [CORRECTNESS] — §4.A.6 / DivisionNode 14-field vs. 7-field mismatch — A_ONLY (confirmed)
**Source:** D-A06
**Patterns:** Pattern 4 (Phantom Metadata)
**The SPEC says:** Division tree nodes have 14 fields including `div_id`, `type`, `digestible`, `editor_inserted`. The contract defines only 7 fields.
**The problem:** The SPEC's example output (line 593) shows fields like `"div_id": "kitab_tahara"` and `"type": "كتاب"` that do not exist in the `DivisionNode` Pydantic model. An implementer following the SPEC would write code accessing non-existent fields.
**Investigation:** B found D-B25 (partial heading text in OCR) in §4.A.6 but not the field count mismatch, which is a phantom metadata issue.
**Verdict:** CONFIRMED (scope-limited). Major build-blocking mismatch.
**Suggested fix:** Either expand `DivisionNode` to match SPEC's 14 fields, or simplify SPEC to match the 7-field contract.

---

### M-15 [CORRECTNESS] — §4.B.5 / HyperLogLog sampling bias — A_ONLY (confirmed)
**Source:** D-A10
**Patterns:** Pattern 3 (Hand-Waving Technology)
**The SPEC says:** "`estimated_unique_terms` (int, approximated from a random sample of 20 pages using HyperLogLog)" with "standard error ~0.8%" (line 896)
**The problem:** HyperLogLog estimates cardinality of items it HAS SEEN. Sampling 20 of 800 pages gives the sample vocabulary, not the source vocabulary. The 0.8% error claim applies to the HLL sketch precision, not the sampling error. The SPEC conflates the two.
**Investigation:** B flagged the 200/3000 char thresholds in the same section (D-B18) but not the statistical methodology error. This is a technology-specific issue (Pattern 3) outside B's patterns.
**Verdict:** CONFIRMED (scope-limited). The statistic would be systematically biased low.
**Suggested fix:** Either rename to `sample_unique_terms`, apply a species richness estimator (Chao1/Good-Turing), or process all pages (HLL is O(n), 800 pages is trivial).

---

### M-16 [CORRECTNESS] — §4.A.4 / CAMeL Tools classical Arabic coverage gap — A_ONLY (confirmed)
**Source:** D-A09
**Patterns:** Pattern 3 (Hand-Waving Technology)
**The SPEC says:** "Flag potential confusions using CAMeL Tools morphological analysis" (line 361)
**The problem:** CAMeL Tools is trained on MSA corpora. Classical Arabic scholarly vocabulary diverges significantly. Terms like "مُتَيَمِّم" or archaic verb forms may not be in its lexicon, producing false positives.
**Investigation:** B flagged a related issue in D-B14 (morphological validation in §4.B.3 using "the Arabic lexicon" without specifying which one). Both point to the same underlying gap: no classical Arabic lexicon is available. However, they target different SPEC sections (§4.A.4 vs. §4.B.3) with different consequences. D-A09 is confirmed independently.
**Verdict:** CONFIRMED. The classical Arabic coverage limitation is real and unacknowledged.
**Suggested fix:** Specify that terms not in CAMeL's lexicon receive "unknown" status (not "invalid"). Add a supplementary classical Arabic term list.

---

### M-17 [CORRECTNESS] — §4.A.4 / OCR benchmark qualification — A_ONLY (confirmed)
**Source:** D-A16
**Patterns:** Pattern 3 (Hand-Waving Technology)
**The SPEC says:** "QARI-OCR v0.2... CER 0.061" / "PaddleOCR-VL 1.5... 94.5% OmniDocBench" (lines 960-968)
**The problem:** CER figures are unqualified by evaluation dataset. OmniDocBench is primarily English-focused. The engine selection matrix makes routing decisions based on these unqualified benchmarks.
**Investigation:** B focused on error paths and scope rather than benchmark validity. This is a technology-specific concern (Pattern 3).
**Verdict:** CONFIRMED (scope-limited). Benchmarks may not represent classical Arabic scholarly text.
**Suggested fix:** Add caveat that benchmarks are general evaluations. Require empirical validation on KR test fixtures before production use.

---

### M-18 [CORRECTNESS] — §4.B.6 / Phantom `ocr_engine` field — A_ONLY (confirmed)
**Source:** D-A14
**Patterns:** Pattern 4 (Phantom Metadata)
**The SPEC says:** "the orchestrator logs which engine processed each page in the content unit's metadata: `ocr_engine` field (already present in fidelity data)" (line 1002)
**The problem:** `TextFidelity` has `score`, `ocr_confidence`, `warnings`. No `ocr_engine` field. The SPEC claims it is "already present" -- it is not.
**Investigation:** B did not audit §4.B.6 for phantom fields (focused on error paths and scope issues).
**Verdict:** CONFIRMED (scope-limited). Phantom field claimed as existing.
**Suggested fix:** Add `ocr_engine: Optional[str] = None` to `TextFidelity`.

---

### M-19 [CORRECTNESS] — §4.A.2, Pass 2 / Footnote separator exact match — A_ONLY (downgraded to STYLE)
**Source:** D-A13
**Patterns:** Pattern 1 (Hollow Example)
**The SPEC says:** The example shows `(1)` inline as footnote reference replacement. A flagged that overly aggressive `(N)` matching in enumeration contexts is not tested by the example.
**Investigation:** B's D-B17 covers the same §4.A.2 Pass 2 section but from a different angle (the `<hr>` separator exact match). A's concern about `(N)` false positives is valid but lower-severity: footnote reference matching is qualified by "matching footnote exists on the same page" (line 192), which constrains false positives. The example IS hollow (only happy path), but the SPEC's own rule partially mitigates the risk.
**Verdict:** CONFIRMED but DOWNGRADED to STYLE. The rule itself has built-in protection; the example should still include a negative case.
**Suggested fix:** Add an example with `(N)` in enumeration context showing it is preserved as literal text.

---

### M-20 [CORRECTNESS] — §4.B.10 / Phantom `quoted_discourse` annotation — A_ONLY (confirmed)
**Source:** D-A19
**Patterns:** Pattern 4 (Phantom Metadata)
**The SPEC says:** "Markers inside quotes are annotated as `quoted_discourse`" (line 1442)
**The problem:** `DiscourseDetectionMethod` enum has only `MARKER` and `LLM_INFERRED`. No `QUOTED_DISCOURSE` value exists. The SPEC does not specify where this annotation goes.
**Investigation:** B flagged §4.B.10 for scope creep (D-B05) and cost control (D-B26) but not this specific phantom annotation. Contract mismatch is outside B's patterns.
**Verdict:** CONFIRMED (scope-limited). Build-blocking: no enum value to represent this concept.
**Suggested fix:** Add `QUOTED_DISCOURSE` to enum, or add `is_quoted: bool = False` to `DiscourseSegment`.

---

### M-21 [CORRECTNESS] — §4.A.3 / No Docling parse failure error path — B_ONLY (confirmed)
**Source:** D-B01
**Patterns:** Pattern 6 (Missing Error Path) + T-1
**The SPEC says:** "Use Docling (IBM, Apache 2.0) as the primary PDF parsing backend" (line 285)
**The problem:** No error code for Docling parse failure (corrupted PDF, password-protected, unsupported version). The closest is `NORM_OCR_FAILED` which says "OCR engine returns error" -- Docling is not an OCR engine.
**Investigation:** A's Pattern 4 (phantom metadata) and Pattern 3 (hand-waving technology) would not flag a missing error path. Pattern 1 (hollow example) might catch the missing failure scenario but A focused elsewhere in §4.A.3.
**Verdict:** CONFIRMED (scope-limited). Real gap in error handling.
**Suggested fix:** Add `NORM_PDF_PARSE_FAILED` (Fatal). Define per-page recovery.

---

### M-22 [CORRECTNESS] — §4.A.2, Pass 3 / Malformed HTML entity handling — B_ONLY (confirmed)
**Source:** D-B04
**Patterns:** Pattern 6 (Missing Error Path) + T-1
**The SPEC says:** "Remove all HTML tags (preserving text content). Decode HTML entities." (line 197)
**The problem:** No handling for truncated HTML entities (e.g., `&#x064` without closing semicolon). Diacritics could be silently lost or substituted. Also: §5 check 8 uses count-based comparison, not position-based, so diacritic substitution (one replaced by another) would not be caught.
**Investigation:** A's patterns did not cover missing error paths (Pattern 6 is B's territory). The diacritics drift check weakness (count vs. position) is an independent secondary finding.
**Verdict:** CONFIRMED. Silent diacritic corruption through entity mangling is a real T-1 risk.
**Suggested fix:** Specify HTML parser backend (lxml or html5lib). Upgrade §5 check 8 from count-based to position-based diacritic comparison.

---

### M-23 [CORRECTNESS] — §3 / Enrichment write-back failure path — B_ONLY (confirmed)
**Source:** D-B06
**Patterns:** Pattern 6 (Missing Error Path) + T-6
**The SPEC says:** "These discoveries are written back to the source metadata record through the enrichment interface" (line 141)
**The problem:** No error path for write-back failure (file locked, corrupted, interface rejects update). No definition of whether normalization blocks on write-back or whether the normalized package is valid without it.
**Investigation:** A did not audit §3 output contract for error paths. Outside A's patterns.
**Verdict:** CONFIRMED (scope-limited). Undefined behavior on write-back failure.
**Suggested fix:** Add `NORM_ENRICHMENT_WRITEBACK_FAILED` (Warning). Normalization completes even if write-back fails. Add reconciliation check at next normalization.

---

### M-24 [CORRECTNESS] — §4.B.4 / Footnote classification needs consensus — B_ONLY (confirmed)
**Source:** D-B09
**Patterns:** Pattern 7 (Scope Creep) + T-6
**The SPEC says:** "Footnote classification: Single-model with pattern matching as primary, LLM as fallback" (line 1542)
**The problem:** Fine-grained footnote taxonomy (`variant_reading`, `hadith_takhrij`, `correction_note`, etc.) requires scholarly understanding. A `correction_note` misclassified as `variant_reading` tells the synthesizer manuscripts disagree when in fact the editor asserts an error. §6 explicitly exempts footnote classification from consensus despite it being a content decision.
**Investigation:** A did not audit §4.B.4 directly. A's patterns focus on phantom metadata and hollow examples, not consensus requirements.
**Verdict:** CONFIRMED. The exemption from consensus for a content decision contradicts D-041.
**Suggested fix:** Require consensus for ambiguous footnotes (pattern-match confidence <0.85). Add `classification_method` field to each footnote.

---

### M-25 [CORRECTNESS] — §4.A.2, Pass 1 / Volume number derivation failure — B_ONLY (confirmed)
**Source:** D-B10
**Patterns:** Pattern 6 (Missing Error Path) + T-7
**The SPEC says:** "process each file with its volume number derived from the filename stem" (line 190)
**The problem:** No error path for non-numeric filenames (e.g., `المجلد_الأول.htm`), duplicate volume numbers, or non-volume files. Wrong volume assignment corrupts citations.
**Investigation:** A did not audit Pass 1 for error paths. Outside A's pattern coverage.
**Verdict:** CONFIRMED (scope-limited). Citation integrity depends on correct volume numbering.
**Suggested fix:** Define filename-to-volume parsing rule. Add `NORM_VOLUME_NUMBER_UNPARSEABLE` error code. Cross-validate against content volume references.

---

### M-26 [CORRECTNESS] — §4.A.4 / Orientation detection error path — B_ONLY (confirmed)
**Source:** D-B13
**Patterns:** Pattern 6 (Missing Error Path) + T-1
**The SPEC says:** "Auto-detect orientation and rotate" (line 358)
**The problem:** A 180-degree rotation produces text with correct RTL within lines but reversed line order. Each line OCRs correctly but the scholarly argument is scrambled. No error code, no validation.
**Investigation:** A focused on OCR quality/benchmarks (D-A16) but not orientation failure. This is a missing error path outside A's patterns.
**Verdict:** CONFIRMED. Scrambled page order would not be caught by §5 check 3.
**Suggested fix:** Add `NORM_ORIENTATION_UNCERTAIN` (Warning). Validate first/last line for reversed-page indicators.

---

### M-27 [CORRECTNESS] — §4.B.3 / Classical Arabic lexicon dependency — B_ONLY (confirmed)
**Source:** D-B14
**Patterns:** Pattern 7 (Scope Creep) + T-5
**The SPEC says:** "Morphological validation: words that don't exist in the Arabic lexicon are lower-fidelity than valid words" (line ~781)
**The problem:** "The Arabic lexicon" is not specified. CAMeL Tools covers MSA primarily. Valid classical scholarly terms could be flagged as invalid, leading to artificial fidelity downgrades and unnecessary human review.
**Investigation:** Related to A's D-A09 (same underlying CAMeL Tools coverage gap), but targets a different section (§4.B.3 vs. §4.A.4) with a different consequence (fidelity scoring vs. OCR flagging). Counted as separate defect.
**Verdict:** CONFIRMED. Unspecified lexicon dependency.
**Suggested fix:** Specify lexicon source. Words not in lexicon -> `fidelity: "unknown"` (not "low"). Only morphologically impossible forms get "low".

---

### M-28 [CORRECTNESS] — §4.B.8 / Plain text continuity gap — B_ONLY (confirmed)
**Source:** D-B15
**Patterns:** Pattern 6 (Missing Error Path) + T-4
**The SPEC says:** "Non-page-based sources (plain text, owner-authored): `boundary_continuity` is null for all content units" (line ~1130)
**The problem:** Plain text units split at 2000-character intervals may fracture mid-sentence arguments. Setting continuity to null gives the passaging engine zero guidance on these boundaries.
**Investigation:** A did not audit §4.B.8 at all (no A findings in this section). Outside A's scope.
**Verdict:** CONFIRMED. Real context loss for plain text sources.
**Suggested fix:** Compute boundary_continuity for plain text using punctuation analysis. Boundaries at paragraph breaks -> `section_break`. Boundaries at character-limit splits -> `mid_paragraph`/`mid_sentence`.

---

### M-29 [CORRECTNESS] — §4.B.7 / Tahqiq topology compounds classification errors — B_ONLY (confirmed)
**Source:** D-B16
**Patterns:** Pattern 7 (Scope Creep) + T-6
**The SPEC says:** "The normalization engine extracts from the footnote apparatus a manuscript witness network" (line ~1018)
**The problem:** Topology extraction depends entirely on §4.B.4 footnote classification, which uses single-model LLM (see M-24). A misclassified footnote creates a phantom manuscript disagreement. Extracting a "manuscript witness network" from potentially unreliable classification is overreach beyond format transformation.
**Investigation:** A did not audit §4.B.7. Outside A's section coverage.
**Verdict:** CONFIRMED (scope-limited). Error compounding from upstream classification.
**Suggested fix:** Add `topology_confidence` derived from constituent footnote classification confidence. `topology_reliability: "uncertain"` when confidence <0.85.

---

### M-30 [CORRECTNESS] — §4.A.2 / Footnote separator fuzzy matching — B_ONLY (confirmed)
**Source:** D-B17
**Patterns:** Pattern 6 (Missing Error Path) + T-1
**The SPEC says:** "Split at `<hr width='95'>` to separate primary text from footnotes" (line 192)
**The problem:** Exact-match on `<hr width='95'>`. Would miss `<hr width="95">` (double quotes), `<hr width='90'>`, `<hr width='95' />` (self-closing). Appendix A.1 acknowledges the cascade but only elevates severity rather than adding fuzzy matching.
**Investigation:** A's D-A13 covered the same Pass 2 section but from the `(N)` reference angle. A did not flag the separator pattern rigidity.
**Verdict:** CONFIRMED. Simple parser variation would cause complete footnote/text conflation.
**Suggested fix:** Match any `<hr>` with width attribute between 80 and 100, regardless of quote style or self-closing.

---

### M-31 [CORRECTNESS] — §4.B.2 / Format auto-detection overrides consensus — B_ONLY (confirmed)
**Source:** D-B19
**Patterns:** Pattern 7 (Scope Creep) + T-3
**The SPEC says:** "the normalizer's detection in the manifest's `structural_format` field, with a note that it overrides the source metadata's classification. An enrichment write-back updates the source metadata." (line ~760)
**The problem:** The normalization engine overrides a consensus-validated source engine classification using single-engine heuristic analysis of only the first 20 pages. This is a confidence regression. A fiqh book with 40% Q&A in its first section could be reclassified, affecting passaging for the entire book.
**Investigation:** A did not audit §4.B.2. Outside A's section coverage.
**Verdict:** CONFIRMED. Overriding consensus with heuristic is a real confidence regression.
**Suggested fix:** Normalization should PROPOSE (not override) an alternative. Source metadata should not be overwritten without human gate. Support `mixed` classification with per-division format.

---

### M-32 [CORRECTNESS] — §4.A.2 / Atomic write multiple prev directories — B_ONLY (confirmed)
**Source:** D-B20
**Patterns:** Pattern 6 (Missing Error Path) + T-7
**The SPEC says:** "it is renamed to `normalized_prev_{timestamp}/` before the swap" (line 234) / Recovery handles "if a `normalized_prev_*` directory exists" (singular) (line 236)
**The problem:** If two interrupted reprocessing attempts leave two `normalized_prev_*` directories, recovery behavior is undefined. Could restore the wrong version.
**Investigation:** A did not audit the atomic write procedure. Outside A's patterns.
**Verdict:** CONFIRMED (scope-limited). Edge case but with data integrity risk.
**Suggested fix:** Select `normalized_prev_*` with latest timestamp. Clean up older prev directories before creating new ones.

---

### M-33 [CORRECTNESS] — §4.A.4 / OCR empty-success handling — B_ONLY (confirmed)
**Source:** D-B22
**Patterns:** Pattern 6 (Missing Error Path) + T-1
**The SPEC says:** "Send to Mistral OCR 3 via API. Parse returned Markdown..." (line 343)
**The problem:** API returns 200 OK but empty Markdown for a content-bearing page. This differs from `NORM_OCR_FAILED` (API error). An "empty success" might not trigger retry. §5 check 3 provides defense but the SPEC should define behavior proactively.
**Investigation:** A focused on benchmark quality (D-A16) and CAMeL Tools (D-A09) for OCR section, not empty-success scenarios.
**Verdict:** CONFIRMED. Defense-in-depth gap; relying solely on downstream validation.
**Suggested fix:** After OCR returns, if primary_text is empty/<10 chars AND page image has content, treat as `NORM_OCR_FAILED` and trigger retry regardless of API status.

---

### M-34 [CORRECTNESS] — §4.B.9 / Cross-source fingerprint scope creep — B_ONLY (confirmed)
**Source:** D-B23
**Patterns:** Pattern 7 (Scope Creep) + T-6
**The SPEC says:** "the engine compares this source's matn fingerprint against the author's known fingerprint from single-layer works" (line ~1209)
**The problem:** The normalization engine reads OTHER sources' normalized packages for cross-source comparison. This is a library-wide validation that exceeds per-source format transformation scope. If the reference fingerprints are contaminated, the comparison increases confidence in wrong attributions.
**Investigation:** A's D-A15 flagged fingerprint circularity in the same section but not the cross-source scope boundary violation.
**Verdict:** CONFIRMED. Cross-source comparison belongs in a separate validation layer (Layer 3 integrity check), not per-source normalization.
**Suggested fix:** Normalization engine computes and stores fingerprints. A separate library-wide validator compares across sources.

---

### M-35 [CORRECTNESS] — §4.A.5 / Upstream author_canonical_id propagation — B_ONLY (confirmed)
**Source:** D-B27
**Patterns:** Pattern 6 (Missing Error Path) + T-2
**The SPEC says:** "Start with the source metadata's layer specification" (line 521) / §5 check 4: "Layer `author_canonical_id` values match the source metadata's layer specification" (line 1478)
**The problem:** If the source engine's `author_canonical_id` is wrong, every layer segment in the normalized package carries the wrong ID. §5 check 4 ensures consistency with source metadata but NOT correctness of source metadata.
**Investigation:** A did not flag upstream trust propagation. Outside A's patterns (phantom metadata looks for fields that don't exist, not fields with wrong values).
**Verdict:** CONFIRMED (scope-limited). Consistency-not-correctness is a real gap.
**Suggested fix:** Cross-check author_canonical_id against layer fingerprint stylometric properties from other library sources. Flag `NORM_AUTHOR_FINGERPRINT_MISMATCH` on dramatic divergence.

---

### M-36 [CORRECTNESS] — §4.A.6 / Partial heading text in OCR — B_ONLY (confirmed)
**Source:** D-B25
**Patterns:** Pattern 6 (Missing Error Path) + T-4
**The SPEC says:** Structure discovery produces `heading_text` as a string. (lines 552-609)
**The problem:** When OCR partially reads a heading (e.g., "باب ال..."), the damaged text propagates to citations. The SPEC tracks heading confidence (tiers) but not heading TEXT quality.
**Investigation:** A flagged the field count mismatch (D-A06) in the same section but not text quality. Different aspects of the same section.
**Verdict:** CONFIRMED (scope-limited). Heading text corruption would propagate to all citations.
**Suggested fix:** Add `heading_text_fidelity` field (high/medium/low/partial) to structural_markers.

---

## False Positives

### FP-01 — D-B18 (sparse_page_count/dense_page_count thresholds)
**Why excluded:** The 200/3000 char thresholds are STYLE concerns (no justification provided) but they ARE testable with precise numeric values. The auditor flagged them as unjustified hardcoded values, which is valid criticism but does not rise to a distinct defect separate from the broader content census issues already captured in M-07. The suggestion to add them to §8 configuration is reasonable but is an enhancement, not a defect. Merged into M-07 as a secondary concern.

### FP-02 — D-B24 (70% Arabic character threshold)
**Why excluded:** The 70% threshold for Arabic character ratio (§5 check 3) is acknowledged by the auditor as "reasonable for pure Arabic texts" and the SPEC explicitly says flags are advisory. The concern about Maghrebi editions with French text is valid but extremely narrow. The suggested fix (exempt index/TOC pages, add per-source override) is good practice but the current rule is testable, precise, and functional. This is an enhancement suggestion, not a defect.

### FP-03 — D-B12 (ZWNJ heading marker imprecision)
**Why excluded:** The concern about "double ZWNJ at line start" being imprecise is valid as an observation, but the ABD reference documents (line 1631) define this pattern. The SPEC delegates to ABD rules for Shamela-specific patterns. The suggestion to make the SPEC self-contained is good practice but the reference chain is intact. Downgraded from defect to enhancement note.

### FP-04 — D-B26 (discourse flow LLM cost control)
**Why excluded:** The concern about missing cost control for discourse flow LLM calls is valid but overstated. Discourse flow runs as part of Pass 6 enrichment which is bounded by the source's page count. Unlike OCR (external API with per-call cost), discourse flow uses the same LLM infrastructure with existing rate limits. The suggestion to add a max-calls limit is reasonable but the absence is not a SPEC defect -- it is a missing configuration parameter. Merged conceptually with M-08 (discourse flow scope issues).

---

## One-Sided Analysis

### A_ONLY findings (11 total: 9 confirmed, 2 false positive/downgrade)

All 9 confirmed A_ONLY findings are **scope-limited** -- they fall squarely within Pattern 4 (Phantom Metadata: 8 findings) and Pattern 3 (Hand-Waving Technology: 3 findings), both of which are outside B's assigned patterns (5-7). B could not have found these without violating its pattern scope.

The 8 phantom metadata defects (M-09 through M-14, M-18, M-20) form the largest single cluster in the entire audit. They are all build-blocking: an implementer following the SPEC would write code referencing non-existent fields, causing Pydantic validation failures.

### B_ONLY findings (16 total: 14 confirmed, 2 false positive)

All 14 confirmed B_ONLY findings fall within Patterns 5-7 (Untestable Rule, Missing Error Path, Scope Creep) which are outside A's assigned patterns (1-4). The breakdown:

- **Missing error paths (Pattern 6):** 8 findings (M-21, M-22, M-25, M-26, M-30, M-32, M-33, M-36). These are systematic gaps in the SPEC's error handling -- scenarios where processing can fail but no behavior is defined. A's patterns (hollow examples, circular definitions, phantom metadata, hand-waving technology) do not cover missing error paths.

- **Scope creep (Pattern 7):** 4 findings (M-24, M-29, M-31, M-34). These identify operations where the normalization engine exceeds its format-transformation role (footnote classification requiring consensus, topology extraction, format override of consensus, cross-source fingerprint comparison). A's Pattern 2 (circular definitions) touches related territory but from a different angle (self-referential logic, not boundary violation).

- **Untestable rules / upstream trust (Pattern 5/6):** 2 findings (M-28, M-35). These identify gaps in cross-engine trust propagation.

---

## Dual-Audit Value Assessment

| Metric | Count |
|--------|-------|
| **BOTH_FOUND** (would be found by either auditor alone) | 8 |
| **A_ONLY confirmed** (unique to A's patterns, real defects) | 9 |
| **B_ONLY confirmed** (unique to B's patterns, real defects) | 14 |
| **Total unique confirmed defects** | 31 |
| **False positives total** | 4 |

### Value of the dual audit:

- A single auditor with patterns 1-4 would find: 8 (shared) + 9 (A-only) = **17 defects**
- A single auditor with patterns 5-7 would find: 8 (shared) + 14 (B-only) = **22 defects**
- The dual audit found: **31 confirmed defects**
- **Dual audit added 14 defects** that Auditor A alone would miss, and **9 defects** that Auditor B alone would miss
- The overlap (8 BOTH_FOUND = 23%) provides **confidence calibration**: these 8 are the highest-confidence defects, independently discovered through different analytical lenses

### Pattern complementarity:

The two pattern sets are highly complementary with minimal overlap:
- A's strengths: contract-vs-SPEC mismatches (phantom fields), technology feasibility analysis, example quality
- B's strengths: error path completeness, scope boundary enforcement, downstream corruption tracing
- The 8 overlaps occur where the patterns naturally converge: imprecise rules (A sees hollow examples, B sees untestable criteria) and feature specification quality (A sees missing technology, B sees scope creep)

### Defect severity distribution in merged list:
- **Build-blocking** (phantom fields, contract mismatches): 10 (32%) -- all from A
- **Error handling gaps** (undefined failure behavior): 8 (26%) -- all from B
- **Integrity risks** (scope creep, consensus bypass): 6 (19%) -- mostly from B
- **Specification quality** (imprecise rules, hollow examples): 7 (23%) -- shared and mixed
