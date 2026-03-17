# Integrity Audit — Normalization Engine (Post-Revision)

**Date:** 2026-03-17
**Auditor:** Integrity Auditor Agent
**Input:** `engines/normalization/SPEC.md` (2,051 lines), revised with 22 `[AUDIT FIX M-XX]` tags
**Source defects:** `reference/SPEC_AUDIT_COMPARISON_NORMALIZATION.md` (31 confirmed defects)
**Research:** `reference/SPEC_RESEARCH_NORMALIZATION.md` (10 defects researched)

**Verdict: CONDITIONAL PASS**

The SPEC is fit for build with the MUST-FIX items resolved during implementation (all are contract alignment, not redesign). The 22 applied fixes are correctly implemented per research recommendations. No new contradictions were introduced. Nine confirmed defects are deferred correctly (6 in §9.1 as contract alignment, 3 as SHOULD-FIX).

---

## Fix Verification

### Applied Fixes (22 total) — Verification

| Fix | Section | Correctly Applied? | New Issues? |
|-----|---------|-------------------|-------------|
| M-03 | §4.A.5 line 520 | YES. Two-factor test (>=80 chars AND no transition marker). Provisional threshold noted. | None. |
| M-04 | §4.A.5 line 524 | YES. ADVISORY ONLY, never sufficient alone. Quantitative confidence adjustments (+0.1). Ambiguous markers ("قال أبو حنيفة") explicitly excluded. Multi-model consensus required per D-041. | None. |
| M-06 | §4.B.9 line 1285 + §8 lines 1632-1633 | YES. Threshold lowered from 2.5 to 2.0 SD. Made configurable. WEAK check caveat added. Minimum 5000 words per layer. `insufficient_data` status. | None. |
| M-08 | §4.B.10 lines 1453, 1457, 1463 | YES. `school_hint` and `attribution_hint` REMOVED from discourse output. `discourse_annotation_authority: "advisory"` stated. School attribution deferred to downstream. | Minor: the `_note` fields in the concrete example (lines 1378, 1424, 1426) say "REMOVED per M-08" — these should be removed entirely from the example rather than left as `_note` comments, to avoid implementer confusion. SHOULD-FIX. |
| M-15 | §4.B.5 lines 908, 911 | YES. Sampling removed. HLL runs on ALL content units. O(1) memory noted. Standard error clarified as HLL sketch precision, not sampling error. | None. |
| M-16 | §4.A.4 line 370 | YES. CAMeL Tools MSA limitation acknowledged. OOV words receive `analysis_status: "unknown"`, NOT flagged as OCR errors. Only morphologically impossible forms flagged. Minaei-Bidgoli et al. 2026 cited. | None. |
| M-17 | §4.B.6 line 979 | YES. Benchmark caveat added. KR-internal benchmarking required before production. PaddleOCR entry updated with CER 0.79 on Arabic (ACL 2025). "NOT recommended for Arabic scholarly text" stated. | None. |
| M-18 | §4.B.6 line 1016 + §9.1 | YES. `ocr_engine` field acknowledged as needing addition to contracts.py. §9.1 lists the resolution. "Already present" claim removed. | Contract alignment still needed (§9.1). |
| M-20 | §4.B.10 line 1457 + §9.1 | YES. `is_quoted: true` approach specified for markers inside quotations. §9.1 lists contract addition. Original detection_method preserved. | Contract alignment still needed (§9.1). |
| M-21 | §4.A.3 lines 285-294 + §7 lines 1596-1597 | YES. Docling demoted from primary to structural-only for Arabic PDFs. Two-path strategy (PyMuPDF+bidi primary, OCR fallback). Two new error codes (`NORM_PDF_PARSE_FAILED`, `NORM_PDF_ARABIC_GARBLED`) with specific thresholds. GitHub issues cited. | None. Research recommendation fully followed. |
| M-22 | §4.A.2 Pass 3 line 197 + §7 line 1602 | YES. lxml backend specified as primary. html5lib as fallback. Position-based diacritic comparison (not count-based). `NORM_DIACRITICS_ENTITY_CORRUPTION` (Fatal) added. | None. Research recommendation fully followed. |
| M-23 | §7 line 1598 | YES. `NORM_ENRICHMENT_WRITEBACK_FAILED` (Warning) added. Normalization completes without write-back. Reconciliation check at next normalization. | None. |
| M-24 | §6 line 1557 | YES. Two-tier classification: pattern >= 0.85 accepted without consensus; < 0.85 requires multi-model consensus per D-041. `classification_method` and `classification_confidence` fields specified. Rationale provided (correction_note vs. variant_reading example). | None. Research recommendation fully followed. |
| M-25 | §7 lines 1599-1600 | YES. Two error codes: `NORM_VOLUME_NUMBER_UNPARSEABLE` and `NORM_VOLUME_MISMATCH`. Sequential filename fallback. Human gate triggered. | None. |
| M-26 | §4.A.4 lines 363-366 + §7 line 1601 | YES. Two-stage orientation detection (Tesseract OSD + page-level validation). 180-degree ambiguity addressed. VLM note added. `NORM_ORIENTATION_UNCERTAIN` error code with dual-processing recovery. | None. Research recommendation fully followed. |
| M-27 | §4.B.3 line 802 | YES. CamelMorph MSA specified by name. `morphological_status: "unknown"` for zero-analysis words. Only impossible forms degrade fidelity. Classical Arabic OOV rationale cited (Minaei-Bidgoli et al. 2026). | None. Research recommendation fully followed. |
| M-29 | §4.B.7 line 1116 | YES. `topology_confidence` (float) added. Derived from mean classification confidence of constituent variant_reading footnotes. `topology_reliability: "uncertain"` when < 0.85. | None. |
| M-30 | §4.A.2 Pass 2 line 192 | YES. Regex matching specified: `<hr\s+[^>]*width\s*=\s*['"]?(\d{2,3})['"]?[^>]*>` with width 80-100. Case-insensitive. Self-closing tolerated. `NORM_FOOTNOTE_SEPARATOR_ABSENT` handles missing separator. 30% threshold for `no_footnote_apparatus` flag. | None. Research recommendation fully followed. |
| M-31 | §4.B.2 line 754 + line 789 | YES. PROPOSE (not override). Source metadata NOT overwritten. Human gate required. `structural_format_proposed` field. Original value authoritative until gate resolved. | None. |
| M-32 | §4.A.2 line 236 | YES. Latest timestamp selection rule for multiple `normalized_prev_*` directories. Cleanup of older prev directories before creating new ones. | None. |
| M-33 | §7 line 1572 | YES. Empty-success case defined: HTTP 200 but <10 chars with non-blank image. Treated as `NORM_OCR_FAILED`. Retry with fallback engine. Three-condition detection specified. | None. |
| M-34 | §4.B.9 line 1287 | YES. Cross-source comparison DEFERRED to Layer 3 library-wide validation. Normalization engine stores fingerprints only (steps 1-2). Scope boundary explicitly enforced. | None. |

### Deferred to §9.1 Contract Alignment (6 defects)

These are correctly documented in §9.1 (lines 2035-2051) with specific resolution recommendations. They do not block SPEC approval — they block implementation of the specific sections that reference them.

| Defect | Phantom Field | Status |
|--------|--------------|--------|
| M-09 | `vocalization_level` on SourceMetadata | Correctly documented. Two resolution options provided. |
| M-10 | `has_embedded_scholarly_quotation` on ContentFlags | Correctly documented. Simple field addition. |
| M-11 | `table_structure_preserved` + `table_data` | Correctly documented. Both fields need addition. |
| M-12 | `OWNER_CONTENT` in LayerType enum | Correctly documented. Simple enum addition. |
| M-13 | LayerMapEntry field name alignment (`detection_confidence` vs `confidence`, missing `markers`) | Correctly documented. Cross-engine coordination needed. |
| M-14 | DivisionNode 14-field vs 7-field mismatch | Correctly documented. Marked `[OPEN]` — decision needed during implementation. |

### Not Applied, Not in §9.1 (3 defects)

| Defect | Status | Assessment |
|--------|--------|------------|
| M-01 (Whitespace Unicode enumeration) | NOT FIXED. §4.A.8 line 662 still says "Non-breaking spaces -> regular spaces" without enumerating Unicode codepoints. ZWNJ preservation is stated in Pass 3 (line 197) but not in §4.A.8. | **SHOULD-FIX.** The rule is implementable as-is because "non-breaking spaces" is clear enough and ZWNJ preservation is stated elsewhere, but explicit Unicode enumeration would prevent ambiguity. |
| M-02 (Hadith/Quran detection patterns) | NOT FIXED. §4.A.9 lines 670-671 still use the vague "عن ... قال" pattern and lack negative examples. | **SHOULD-FIX.** The flags are advisory (line 676), which limits downstream damage. But an overly aggressive implementation would generate noisy flags. |
| M-05 ("trains" vs. prompts in §4.B.1) | PARTIALLY FIXED. §4.B.1 line 708 still says "trains an LLM-based layer classifier." M-04 fix (ADVISORY ONLY) partially addresses the concern. Bootstrapping failure path still undefined. | **SHOULD-FIX.** The word "trains" is misleading for in-context learning. |

---

## MUST-FIX Findings (blocks build)

### MF-1: §9.1 M-14 DivisionNode field count mismatch — DECISION REQUIRED

**Location:** §4.A.6 line 567 (14-field SPEC example) vs `contracts.py` DivisionNode (7 fields)
**Problem:** The SPEC example at line 604 shows `div_id`, `type`, `title`, `parent_div_id`, `child_div_ids`, `page_hint_start`, `page_hint_end`, `digestible`, `editor_inserted` — none of which exist in the Pydantic model. An implementer following the SPEC example would fail at runtime.
**Severity:** Build-blocking. The division tree is a core output consumed by the passaging engine.
**Required action:** Before implementing §4.A.6, resolve the `[OPEN]` question in §9.1 M-14: expand DivisionNode to match SPEC, or simplify SPEC to match contracts.py. Recommendation: expand the model (the SPEC fields are useful; the passaging engine's §2 already generates synthetic `div_id` from these).

**Note:** The passaging engine's §2 (line 28) says it generates `div_id` from the tree during traversal. If normalization provides `div_id`, the passaging engine should use it instead. This needs coordination.

### MF-2: §9.1 M-13 LayerMapEntry cross-boundary field mismatch

**Location:** `contracts.py` LayerMapEntry has `detection_confidence`; passaging SPEC §2 line 30 expects `confidence` and `markers`.
**Problem:** The passaging engine would fail to read the layer map if field names differ.
**Severity:** Build-blocking for pipeline integration.
**Required action:** Rename `detection_confidence` to `confidence`. Add `markers: list[str] = []`. This is a contracts.py change, not a SPEC change.

### MF-3: §5 check 14 references upstream field that does not exist

**Location:** §5 line 1520 references `unvocalized` / `partially_vocalized` classification from source metadata.
**Problem:** Source engine `SourceMetadata` has no `vocalization_level` field. This validation check cannot be implemented as written.
**Severity:** Build-blocking for §5 check 14 implementation.
**Required action:** Either add `vocalization_level` to source engine contracts (requires source engine change) or change §5 check 14 to infer vocalization from the first N pages of OCR output (self-contained within normalization engine). §9.1 M-09 documents both options.

---

## SHOULD-FIX Findings (fix during build)

### SF-1: §4.A.8 whitespace normalization lacks Unicode codepoint enumeration (M-01 unfixed)

**Location:** §4.A.8 line 662
**Problem:** "Non-breaking spaces -> regular spaces" does not specify which Unicode codepoints. ZWNJ (U+200C) preservation is critical (9.5% of Shamela corpus uses it for heading detection) and is stated in §4.A.2 Pass 3 (line 197) but not in §4.A.8. Characters like thin space (U+2009), narrow NBSP (U+202F), ZWSP (U+200B), BOM (U+FEFF) have undefined behavior.
**Risk:** An implementer might normalize ZWNJ, destroying heading detection.
**Recommendation:** Add explicit enumeration: U+00A0 -> space; U+200C (ZWNJ) -> PRESERVED; U+200B (ZWSP) -> PRESERVED; U+FEFF (BOM) -> stripped at file start only; U+202F -> space; U+2000-U+200A (typographic spaces) -> space.

### SF-2: §4.A.9 content flagging patterns underspecified (M-02 unfixed)

**Location:** §4.A.9 lines 670-671
**Problem:** "عن ... قال" matches virtually any narrative Arabic text. No negative examples. No false-positive mitigation.
**Risk:** Overly aggressive `has_hadith_citation` flagging. Flags are advisory, so downstream impact is limited.
**Recommendation:** Tighten the pattern: "عن ... قال" only when preceded by narrator-chain indicators (عن + proper name + عن/قال) or followed by "رسول الله" / "النبي ﷺ". Add negative example (biographical "عن أبيه أنه قال" without prophetic attribution).

### SF-3: §4.B.1 "trains" misleading terminology (M-05 unfixed)

**Location:** §4.B.1 line 708
**Problem:** "trains an LLM-based layer classifier" implies fine-tuning or model training. The actual approach is in-context learning with bootstrapped examples.
**Recommendation:** Replace "trains" with "uses via in-context learning." Add bootstrapping failure path: if <5 high-confidence segments found in first 50 pages, skip §4.B.1 and treat source as single-layer with human gate.

### SF-4: §4.B.10 concrete example contains `_note` comments

**Location:** §4.B.10 lines 1378, 1424, 1426
**Problem:** The concrete example contains `"_note": "school_hint/attribution_hint REMOVED per M-08"` fields. These are audit commentary, not output schema. An implementer might include `_note` fields in actual output.
**Recommendation:** Remove `_note` fields from the example entirely.

### SF-5: §4.B.5 KR technical glossary prerequisite unresolved (M-07)

**Location:** §4.B.5 line 911
**Problem:** `technical_term_density` references "the KR technical glossary" which does not exist. The glossary is listed as "a pre-built set of ~500-2000 terms per science."
**Risk:** `technical_term_density` cannot be computed until the glossary exists.
**Recommendation:** Make `technical_term_density` nullable in the census. Compute it as null until the glossary is built. Add a prerequisite note.

### SF-6: §4.B.8 plain text continuity gap (M-28 unfixed)

**Location:** §4.B.8 line 1222
**Problem:** Plain text and owner-authored sources set `boundary_continuity` to null for all content units. But these sources create units at 2000-char intervals, potentially fracturing mid-sentence. The passaging engine gets zero guidance.
**Risk:** Context loss (T-4) for plain text sources.
**Recommendation:** Compute basic continuity for plain text using punctuation analysis. Character-limit splits -> `mid_paragraph` or `mid_sentence`. Paragraph-break splits -> `section_break`.

### SF-7: §4.A.5 upstream author_canonical_id trust gap (M-35)

**Location:** §4.A.5 + §5 check 4 line 1493
**Problem:** §5 check 4 verifies layer `author_canonical_id` matches source metadata, but does not verify source metadata correctness. A wrong upstream ID propagates to every layer segment.
**Risk:** Wrong author on every layer in the normalized package.
**Recommendation:** This is inherently a cross-engine concern. During build, add a note that fingerprint-based cross-source validation (§4.B.9 step 3, deferred to Layer 3) is the defense.

### SF-8: §4.A.6 partial heading text quality (M-36)

**Location:** §4.A.6 structural markers
**Problem:** OCR may partially read a heading ("باب ال..."). The heading text propagates to citations. No `heading_text_fidelity` field exists to flag partial headings.
**Recommendation:** Add `heading_text_fidelity: Optional[str]` (high/medium/low/partial) to `StructuralMarkers` in contracts.py.

### SF-9: §7 `NORM_TABLE_STRUCTURE_LOST` references phantom field

**Location:** §7 line 1595
**Problem:** Recovery action says "Set `content_flags.table_structure_preserved: false`" but this field does not exist in ContentFlags. This is part of M-11 (§9.1) but the error code references it as if it exists today.
**Risk:** Implementer confusion.
**Recommendation:** Resolve M-11 contract alignment before implementing this error code.

---

## T-Threat Coverage Matrix

| Threat | Status | Mitigation in SPEC | Gaps |
|--------|--------|-------------------|------|
| **T-1: Silent Text Corruption** | STRONG | §4.A.8 (diacritics absolute preservation), §5 check 8 (position-based diacritic comparison — fix M-22), `NORM_DIACRITICS_DRIFT` (fatal), `NORM_DIACRITICS_ENTITY_CORRUPTION` (fatal — fix M-22), semantic confusion hazard (§4.A.4), dual-OCR comparison, lxml parser specified | SF-1 (whitespace Unicode codepoints) is a minor gap. Overall T-1 protection is thorough. |
| **T-2: Attribution Error** | STRONG | §4.A.5 (multi-layer detection with 3 signal tiers), §4.B.9 (fingerprint validation — fix M-06), inversion detection thresholds (Appendix A.8), content-based inference ADVISORY ONLY (fix M-04), conservative default (below 0.50 -> commentary author), hashiyah quotation detection | SF-7 (upstream author_canonical_id trust) is a known gap deferred to Layer 3 validation. |
| **T-3: Taxonomic Misplacement** | ADEQUATE | §4.B.2 (format auto-detection — fix M-31: propose not override), §4.B.10 (discourse flow — fix M-08: school hints removed), structural format as metadata signal to downstream | Discourse flow is advisory, limiting misplacement scope. |
| **T-4: Context Loss** | STRONG | §4.B.8 (cross-page continuity), argument flow markers, signal priority rule (headings override punctuation), §4.B.10 (discourse flow with argument cycle detection), cross-validation rule (Pass 6 step 9) | SF-6 (plain text continuity gap) — null continuity for plain text sources. |
| **T-5: Synthesis Hallucination** | ADEQUATE | Not directly this engine's responsibility. Content census (§4.B.5) provides statistical signals. Discourse flow provides structure for downstream extraction. All output carries confidence scores. | No direct gap — this threat is primarily mitigated by downstream engines. |
| **T-6: Metadata Poisoning** | STRONG | D-023 metadata pass-through via source_id reference. Enrichment write-back through interface (fix M-23: failure handling). §4.B.4 footnote classification with consensus for ambiguous cases (fix M-24). Topology confidence signal (fix M-29). | MF-2 (LayerMapEntry field mismatch) could cause field-level metadata loss at the boundary. Fix before pipeline integration. |
| **T-7: Duplication and Contradiction** | ADEQUATE | §4.A.7 (`unit_index` as sole positional identifier), atomic write procedure (fix M-32: multiple prev directories), page boundary preservation, volume numbering error handling (fix M-25) | No significant gap. |

---

## Contract Alignment

### Upstream: Source Engine Output -> Normalization Engine Input

| Source Engine Field | SPEC §2 Reference | Status |
|--------------------|--------------------|--------|
| `source_id` | Line 47 | ALIGNED |
| `source_format` | Line 48 | ALIGNED. SPEC lists 8 values; source engine `SourceFormat` enum should match. |
| `work_id` | Line 49 | ALIGNED |
| `text_fidelity` | Line 50 | ALIGNED. Source engine uses categorical (high/medium/low/unknown). |
| `structural_format` | Line 51 | ALIGNED. 7 values match `StructuralFormat` enum in both contracts. |
| `is_multi_layer` | Line 52 | ALIGNED |
| `genre` | Line 53 | ALIGNED |
| `page_count` | Line 54 | ALIGNED |
| `volume_count` | Line 55 | ALIGNED |
| `vocalization_level` | §5 check 14 line 1520 | **MISALIGNED (MF-3)** — field does not exist upstream |

### Downstream: Normalization Output -> Passaging Engine Input

| Normalization Output Field | Passaging §2 Reference | Status |
|---------------------------|----------------------|--------|
| `division_tree` | Line 28 | **MISALIGNED (MF-1)** — passaging expects `DivisionNode` with 7 fields; SPEC example shows 14 fields. Passaging engine generates `div_id` synthetically, but SPEC example includes `div_id`. |
| `layer_map` | Line 30 | **MISALIGNED (MF-2)** — passaging expects `confidence` and `markers`; normalization contracts have `detection_confidence` and no `markers`. |
| `structural_format` | Line 29 | ALIGNED |
| `content_census` | Line 34 | ALIGNED |
| `tahqiq_topology` | Line 35 | ALIGNED |
| `quality_report` | Line 36 | ALIGNED |
| `boundary_continuity` | Line 40 | ALIGNED |
| `discourse_flow` | Line 41 | ALIGNED |
| `layer_fingerprints` | Line 42 | ALIGNED |
| `text_fidelity_summary` | Line 33 | ALIGNED |
| `verse_detection` | Line 31 | ALIGNED |
| `total_content_units` | Line 32 | ALIGNED |

### Internal: SPEC §4 Rules -> §3 Output

| §4 Processing Rule | §3 Output Field | Status |
|--------------------|----------------|--------|
| §4.A.2 Pass 2 footnote separation | `footnotes` array | ALIGNED |
| §4.A.2 Pass 4 structure discovery | `structural_markers` + `division_tree` | ALIGNED (pending MF-1 DivisionNode resolution) |
| §4.A.2 Pass 5 layer detection | `text_layers` | ALIGNED |
| §4.A.9 content flagging | `content_flags` | ALIGNED (7 flags; M-10/M-11 phantom fields in §9.1) |
| §4.B.2 format auto-detection | `structural_format` + `structural_format_proposed` | Minor: `structural_format_proposed` not in contracts.py manifest. Needs addition. |
| §4.B.4 footnote classification | `footnote_type` enum values | ALIGNED with `FootnoteType` enum |
| §4.B.5 content census | `content_census` | ALIGNED with `ContentCensus` model |
| §4.B.7 tahqiq topology | `tahqiq_topology` | ALIGNED with `TahqiqTopology` model |
| §4.B.8 cross-page continuity | `boundary_continuity` | ALIGNED with `BoundaryContinuity` model |
| §4.B.9 fingerprint | `layer_fingerprints` | ALIGNED with `LayerFingerprint` model |
| §4.B.10 discourse flow | `discourse_flow` | ALIGNED (pending M-20 `is_quoted` field addition) |

### Internal: §4 Processing Rules -> §7 Error Codes

Every processing step in §4 that can fail has a corresponding §7 error code. Verified by cross-referencing:

- §4.A.2 Pass 1 (page extraction) -> `NORM_MISSING_FROZEN`, `NORM_VOLUME_NUMBER_UNPARSEABLE` (fix M-25), `NORM_VOLUME_MISMATCH` (fix M-25)
- §4.A.2 Pass 2 (footnote separation) -> `NORM_FOOTNOTE_SEPARATOR_ABSENT` (fix M-30), `NORM_ORPHAN_FOOTNOTE_REF`
- §4.A.2 Pass 3 (HTML stripping) -> `NORM_DIACRITICS_ENTITY_CORRUPTION` (fix M-22), `NORM_ENCODING_ERROR`
- §4.A.2 Pass 4 (structure discovery) -> `NORM_SPARSE_STRUCTURE`
- §4.A.2 Pass 5 (layer detection) -> `NORM_LAYER_UNCERTAIN`
- §4.A.2 Pass 6 (output) -> `NORM_WRITE_FAILED`, `NORM_SCHEMA_VIOLATION`
- §4.A.3 (PDF) -> `NORM_PDF_PARSE_FAILED` (fix M-21), `NORM_PDF_ARABIC_GARBLED` (fix M-21), `NORM_NO_TEXT_LAYER`
- §4.A.4 (OCR) -> `NORM_OCR_FAILED` (fix M-33), `NORM_ORIENTATION_UNCERTAIN` (fix M-26), `NORM_OCR_API_RATE_LIMIT`, `NORM_PAGE_ORDER_CONFLICT`, `NORM_PARTIAL_PAGE`
- §4.A.8 (diacritics) -> `NORM_DIACRITICS_DRIFT`
- §4.B.2 (format) -> `NORM_FORMAT_MISMATCH`
- §4.B.8 (continuity) -> `NORM_CONTINUITY_INCONSISTENT`
- §4.B.9 (fingerprint) -> `NORM_FINGERPRINT_INVALID`, `NORM_LAYER_FINGERPRINT_INVERSION`
- §4.B.10 (discourse) -> `NORM_DISCOURSE_INCONSISTENT`
- Enrichment -> `NORM_ENRICHMENT_WRITEBACK_FAILED` (fix M-23)

**Gap found:** §4.B.4 (footnote classification) has no dedicated error code for classification failure. If the LLM fallback fails or returns unparseable output, the behavior is undefined. The footnote would presumably remain `unknown_footnote_type`, which is acceptable, but a `NORM_FOOTNOTE_CLASSIFICATION_FAILED` (info) error code should be added for logging.

### Internal: §5 Validation -> §4 Processing Claims

| §5 Check | What It Validates | Coverage |
|-----------|------------------|----------|
| 1 (Schema) | Every field in §3 output | COMPLETE |
| 2 (Coverage) | Page count vs content units | COMPLETE (tight check for deterministic sources) |
| 3 (Text extraction) | Arabic ratio, garbage detection | COMPLETE |
| 4 (Layer consistency) | Coverage, proportions, transitions, author_canonical_id | COMPLETE |
| 5 (Division tree) | Range validity, non-overlap, containment | COMPLETE |
| 6 (Footnote integrity) | Reference-footnote matching, orphan handling | COMPLETE |
| 7 (Unit index) | Contiguous zero-based sequence | COMPLETE |
| 8 (Diacritics) | Position-based comparison (non-OCR sources) | COMPLETE |
| 9 (Format-specific) | Input format validation per normalizer | COMPLETE |
| 10 (Continuity) | Boundary consistency with text | COMPLETE |
| 11 (Discourse) | Non-overlapping segments, cycle consistency | COMPLETE |
| 12 (Fingerprint) | Range validity, layer coverage | COMPLETE |
| 13 (OCR coherence) | Sentence-level plausibility | COMPLETE |
| 14 (OCR diacritics hallucination) | Diacritics density vs vocalization level | **BLOCKED (MF-3)** — upstream field missing |

---

## Internal Consistency Check

### Do any two §4 rules contradict?

**No contradictions found.** Checked:
- §4.A.5 (bold = layer) vs §4.A.5 (bold = emphasis): Resolved by two-factor test (M-03 fix). No ambiguity.
- §4.B.2 (format override) vs §6 (no consensus): Resolved by M-31 fix (propose, not override). Human gate required.
- §4.B.8 (continuity) vs §4.B.10 (discourse): Cross-validation rule (Pass 6 step 9) resolves conflicts explicitly. Two cases covered: mid_argument + cycle_complete, and incomplete cycle + section_break.
- §4.A.5 (content-based inference) vs §6 (no consensus for normalization): Resolved by M-04 fix (D-041 consensus required for content-based attribution adjustments).

### Does §5 validate everything §4 claims to produce?

**Yes, with one gap:** §4.B.4 footnote classification produces `classification_method` and `classification_confidence` fields (per M-24 fix), but §5 has no check validating these new fields. The schema check (§5 check 1) would catch missing fields if they are added to contracts.py, but no semantic validation verifies that pattern-matched footnotes have `classification_method: "pattern"` and consensus-matched have `classification_method: "consensus"`.

### Does §3 output match what §4 actually produces?

**Yes, with one addition needed:** §4.B.2 (format auto-detection, M-31 fix) produces `structural_format_proposed` as a manifest field. This field is not listed in §3 manifest schema. Needs addition to both §3 and contracts.py.

---

## Summary

**Verdict: CONDITIONAL PASS**

**3 MUST-FIX items** (all contract alignment, not redesign):
1. MF-1: DivisionNode field count mismatch — resolve `[OPEN]` in §9.1 M-14
2. MF-2: LayerMapEntry field name mismatch — rename + add `markers` in contracts.py
3. MF-3: §5 check 14 vocalization_level upstream dependency — add field or change check

**9 SHOULD-FIX items** (fix during build, none blocks architecture):
- SF-1 through SF-9 as documented above

**No new contradictions, ambiguities, or integrity risks** were introduced by the 22 applied fixes. The fixes are well-integrated and consistent with the rest of the SPEC. The research recommendations were faithfully followed for all 10 researched defects.

**One new minor gap found:** Missing `NORM_FOOTNOTE_CLASSIFICATION_FAILED` error code for §4.B.4 LLM fallback failure. And `structural_format_proposed` manifest field not in §3 or contracts.py.

The SPEC is ready for build once the 3 MUST-FIX contract alignment items are resolved. These are mechanical changes (field additions/renames in Pydantic models), not design decisions, except for MF-1 which requires a one-time decision on DivisionNode field set.
