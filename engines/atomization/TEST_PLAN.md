# Atomization Engine — Test Plan

Maps the 38 test cases from SPEC §10 to test fixtures, modules, and priority ordering.

---

## Priority Ordering

**P0 (critical invariants — build tests first):**
Tests 1–2 (offset integrity + coverage), 31 (attribution marker ADV-3), 35 (over-segmentation ADV-12)

**P1 (core functionality):**
Tests 3–8 (type classification, Quran, layer attribution, bonded clusters), 9 (input validation), 10 (offset correction), 14–15 (footnote + heading atoms)

**P2 (hardening defenses):**
Tests 32–34, 36–38 (ADV-5 evidence conflict, ADV-8 orphaned footnotes, ADV-10 reordering, ADV-2 commentary, NFC normalization, confidence laundering)

**P3 (§4.B capabilities):**
Tests 11–13 (attribution + fingerprinting), 26–30 (completeness, concordance, evidence quality)

**P4 (edge cases):**
Tests 16–25 (word boundaries, bonded layer span, NFC safety, persistent failure, coverage gap, heading-only, all unclassified, verse disagreement, commentary all-matn, scale)

---

## Test Category 1: Core Invariants (§10.1–2)
**Module:** `postprocessor.py`, `validator.py`
**Priority:** P0
**Fixture:** Gold passages from test data

| # | Test Case | Input | Expected | Fixture |
|---|-----------|-------|----------|---------|
| 1 | Offset integrity on 10 gold passages | 10 diverse gold passages | atom_text == passage_text[start:end] for every atom | gold passages |
| 2 | Exhaustive coverage on 10 gold passages | Same 10 passages | Union of anchor_spans = [0, len(passage_text)) for each | gold passages |

---

## Test Category 2: Type Classification (§10.3–5)
**Module:** `llm_atomizer.py`, `predetection.py`
**Priority:** P1
**Fixture:** Gold passages with expected classifications

| # | Test Case | Input | Expected | Fixture |
|---|-----------|-------|----------|---------|
| 3 | Structural type accuracy | Gold passages | ≥90% agreement with gold structural types | gold passages |
| 4 | Scholarly function accuracy | Gold passages | ≥85% agreement with gold scholarly functions | gold passages |
| 5 | Quran detection recall | Passages with known Quran citations | ≥95% recall on confirmed Quran fragments | ibn_aqil (Quran citations in sharh) |
| 6 | Bonded cluster identification | Passages with condition+result, isnad+matn patterns | Correct bonded clusters with valid bonded_reason | gold passages |
| 7 | Multi-layer attribution accuracy | Multi-layer commentary passages | ≥90% correct layer assignment | ibn_aqil |
| 8 | Embedded reference detection | Passages with Quran, hadith, poetry | Correct ref_type, span, ref_detail for each | gold passages |

---

## Test Category 3: Input Validation (§10.9)
**Module:** `loader.py`
**Priority:** P1
**Fixture:** Synthetic malformed passages

| # | Test Case | Input | Expected | Fixture |
|---|-----------|-------|----------|---------|
| 9.1 | Empty passage_text | passage_text: "" | ATOM_INVALID_INPUT, passage skipped | synthetic |
| 9.2 | Missing text_layers | text_layers: [] | ATOM_INVALID_INPUT, passage skipped | synthetic |
| 9.3 | Invalid structural_format | structural_format: "unknown" | ATOM_INVALID_INPUT, passage skipped | synthetic |
| 9.4 | Malformed passage_id | passage_id: "wrong_format" | ATOM_INVALID_INPUT, passage skipped | synthetic |
| 9.5 | text_layers gap | text_layers not covering full span | ATOM_INVALID_INPUT, passage skipped | synthetic |

---

## Test Category 4: Offset Correction (§10.10)
**Module:** `postprocessor.py`
**Priority:** P1
**Fixture:** Synthetic passages with known drift patterns

| # | Test Case | Input | Expected | Fixture |
|---|-----------|-------|----------|---------|
| 10.1 | Off-by-1 drift | LLM offset off by 1 char | Corrected to exact match | synthetic |
| 10.2 | Off-by-3 drift | LLM offset off by 3 chars | Corrected to exact match | synthetic |
| 10.3 | Diacritical difference | LLM text has diacritics, passage doesn't | Fuzzy match within Levenshtein ≤3 | synthetic |
| 10.4 | Beyond correction window | LLM offset off by 60 chars (>50 window) | ATOM_OFFSET_UNRESOLVABLE, review flag set | synthetic |
| 10.5 | Perfect match (no correction) | LLM offsets exactly correct | No correction applied, no flag | synthetic |
| 10.6 | Diacritical-only mismatch | Same text, different tashkil | Matched, offset_drift_corrected flag | synthetic |
| 10.7 | Hamza/alef normalization | اإأآ variation | Matched via fuzzy matching | synthetic |
| 10.8 | Multiple atoms needing correction | 5 atoms, 3 with drift | All 3 corrected independently | synthetic |
| 10.9 | Zero-length span from LLM | start == end | ATOM_OFFSET_UNRESOLVABLE | synthetic |
| 10.10 | Overlapping LLM spans | Two atoms overlap by 5 chars | Resolved during coverage enforcement | synthetic |

---

## Test Category 5: Attribution Detection (§10.11)
**Module:** `attribution_detection.py`, `llm_atomizer.py`
**Priority:** P3
**Fixture:** Gold passages with known attributions

| # | Test Case | Input | Expected | Fixture |
|---|-----------|-------|----------|---------|
| 11.1 | Direct attribution | "قال الشافعي" | attributed_to: "الشافعي", type: direct | gold passages 2, 3 |
| 11.2 | Isnad chain | "حدثنا فلان عن فلان" | Ordered transmitter names in isnad_chain | gold passage 5 |
| 11.3 | School attribution | "مذهب الحنفية" | type: school_collective, school_scope: "الحنفية" | gold passage 6 |
| 11.4 | Self-attribution | "والراجح عندي" | type: self | gold passage 3 |
| 11.5 | Anonymous attribution | "قيل" | type: anonymous | gold passage 6 |
| 11.6 | Via-work attribution | "ذكر في المغني" | type: via_work, work_reference: "المغني" | gold passage 2 |
| 11.7 | Refutation target | "وقال أبو حنيفة... وهذا مردود" | type: refutation_target | gold passage 6 |
| 11.8 | Attribution disabled | enable_attribution_detection: false | attributions: null (not empty []) | any passage |

---

## Test Category 6: Fingerprinting (§10.12–13)
**Module:** `fingerprinting.py`
**Priority:** P3
**Fixture:** Synthetic atom pairs with known similarity

| # | Test Case | Input | Expected | Fixture |
|---|-----------|-------|----------|---------|
| 12.1 | Identical text hash | Same text | Same fingerprint_text_hash | synthetic |
| 12.2 | Tashkil variation hash | Text ± diacritics | Same hash (diacritics stripped) | synthetic |
| 12.3 | Alef/hamza variation | اإأآ variants | Same hash (normalized) | synthetic |
| 12.4 | Taa marbuta variation | ة/ه variants | Same hash (normalized) | synthetic |
| 12.5 | Different text hash | Semantically different text | Different hash | synthetic |
| 12.6 | Hash determinism | Same text, 100 runs | Same hash every time | synthetic |
| 12.7 | Malformed Unicode | Invalid byte sequence | ATOM_FINGERPRINT_HASH_FAILURE, hash null | synthetic |
| 12.8 | Empty text hash | Empty string | ATOM_FINGERPRINT_HASH_FAILURE, hash null | synthetic |
| 13.1 | Definition key terms | Definition atom | Key terms include defined term | gold definition |
| 13.2 | Quran evidence key terms | Quran citation atom | Key terms include Quranic concept | gold quran citation |
| 13.3 | Empty key terms | LLM returns [] | ATOM_FINGERPRINT_KEY_TERMS_EMPTY, terms [] | synthetic |
| 13.4 | Key terms disabled | enable_text_fingerprinting: false | fingerprint_key_terms: null | any atom |
| 13.5 | Key terms count limit | config: fingerprint_key_terms_count: 3 | At most 3 terms returned | gold definition |

---

## Test Category 7: Footnote and Heading Integrity (§10.14–15)
**Module:** `footnote_atomizer.py`, `postprocessor.py`
**Priority:** P1
**Fixture:** Passages with footnotes and headings

| # | Test Case | Input | Expected | Fixture |
|---|-----------|-------|----------|---------|
| 14.1 | Footnote source_layer | Passage with footnotes | source_layer: "footnote" on all footnote atoms | ibn_aqil |
| 14.2 | Footnote offset integrity | Passage with footnotes | atom_text == footnote.text[start:end] | ibn_aqil |
| 14.3 | Footnote_for relation | Passage with footnotes | footnote_for links to correct main text atom | ibn_aqil |
| 14.4 | Footnote_source_index | Passage with 3 footnotes | Correct zero-based index per footnote atom | synthetic |
| 15.1 | Heading offset integrity | Passage with heading_text | anchor_span relative to heading_text, not passage_text | synthetic |
| 15.2 | Heading excluded from V-1 | Passage with heading + content | V-1 checks passage_text only, heading atom excluded | synthetic |
| 15.3 | Heading sequence_in_passage | Passage with heading | Heading is 0, main text starts at 1 | synthetic |

---

## Test Category 8: Edge Cases (§10.16–25)
**Module:** Various
**Priority:** P4
**Fixture:** Synthetic + test data

| # | Test Case | Input | Expected | Fixture |
|---|-----------|-------|----------|---------|
| 16 | Word boundary mid-word | LLM splits mid-word | V-8 mid_word_boundary review flag | synthetic |
| 17 | Bonded cluster spanning layers | Bonded cluster across matn→sharh | ambiguous_layer + possible_misattribution flags | synthetic |
| 18.1 | NFD text normalized | NFD Arabic text | Normalized to NFC, nfc_normalization_applied flag | synthetic |
| 18.2 | NFC text unchanged | NFC Arabic text | No normalization, no flag | synthetic |
| 19 | Persistent V-2 failure | Uncorrectable offsets after retries | Zero atoms, ATOM_OFFSET_INTEGRITY_FAILURE, human review | synthetic |
| 20 | Coverage gap synthetic atom | Unresolvable gap after retries | Synthetic whitespace_separator, coverage_gap_unresolved flag | synthetic |
| 21 | Heading-only passage | passage_text whitespace, heading_text non-null | One heading atom, no V-1 violation | synthetic |
| 22 | All atoms unclassified | LLM returns all "unclassified" | ATOM_HIGH_UNCLASSIFIED_RATE, low_function_confidence flags | synthetic |
| 23 | Verse_info vs LLM disagreement | verse_info: 5 lines, LLM: 4 | Engine trusts verse_info (5 verse_line atoms) | alfiyyah |
| 24 | Commentary all-matn | commentary_unit, all matn atoms | ATOM_LAYER_DISTRIBUTION_SUSPICIOUS, single_layer_in_commentary | synthetic |
| 25 | 100+ footnotes scale | Passage with 100 footnotes | No atom_id gaps, contiguous sequence_in_passage | synthetic |

---

## Test Category 9: §4.B Capabilities (§10.26–30)
**Module:** Various §4.B modules
**Priority:** P3
**Fixture:** Gold passages with known patterns

| # | Test Case | Input | Expected | Fixture |
|---|-----------|-------|----------|---------|
| 26.1 | Khilaf completeness 1.0 | Two opinions + evidence for both | completeness_ratio: 1.0 | gold khilaf |
| 26.2 | Khilaf completeness <1.0 | Two opinions, evidence for one | completeness_ratio < 1.0, gap_description set | gold khilaf |
| 26.3 | No rhetorical pattern | Narrative passage | completeness_score: null | gold narrative |
| 27.1 | Standard genus-differentia | "المبتدأ هو الاسم المرفوع" | defined_term: "المبتدأ", definition_genus: "الاسم" | gold definition |
| 27.2 | Alternate terms | "ويُسمى أيضاً المُسنَد إليه" | alternate_terms: ["المُسنَد إليه"] | gold definition |
| 27.3 | No genus-differentia | Non-standard definition form | defined_term extracted, genus null | gold definition |
| 28 | Term index production | Source with 5 definitions | term_index.json with 5 entries, correct refs | gold source |
| 29.1 | Strong hadith collection | "رواه البخاري ومسلم" | hadith_strong_collection, positive | gold hadith |
| 29.2 | Weakness flag | "وفي إسناده ضعف" | hadith_weakness_flag, negative | gold hadith |
| 29.3 | Non-evidence atom | Definition atom | evidence_quality_signals: null | gold definition |
| 30 | Detection disabled | enable_evidence_quality_detection: false | evidence_quality_signals: null | any atom |

---

## Test Category 10: Hardening Defense Tests (§10.31–38)
**Module:** `postprocessor.py`, `validator.py`
**Priority:** P2
**Fixture:** Synthetic adversarial inputs

| # | Test Case | Input | Expected | Fixture |
|---|-----------|-------|----------|---------|
| 31.1 | Attribution marker missing | marker_text not in atom_text | Attribution dropped, ATOM_ATTRIBUTION_MARKER_MISSING | synthetic |
| 31.2 | Self-attribution relaxed check | "self" type, valid non-substring marker | Passes relaxed check | synthetic |
| 32.1 | Evidence type conflict | Rule: hadith ≥0.90, LLM: evidence_rational | evidence_type_conflict flag, ATOM_EVIDENCE_TYPE_CONFLICT | synthetic |
| 32.2 | No conflict (agreement) | Rule: hadith ≥0.90, LLM: evidence_hadith | No flag | synthetic |
| 33 | Orphaned footnote marker | ⌜3⌝ with 2 footnotes | linked_footnote_atom_id: null, orphaned_footnote_marker flag | synthetic |
| 34 | Atom reordering | LLM returns reverse order | V-4 sorts by start, atom_reordering_applied flag | synthetic |
| 35.1 | Over-segmentation detected | 50 chars → 30 atoms | ATOM_OVER_SEGMENTATION, re-atomization retry | synthetic |
| 35.2 | Over-segmentation persistent | Retry also over-segments | Atoms written with over_segmented flag | synthetic |
| 36 | Commentary V-6 escalation | commentary_unit, all matn | Warning severity (not info), single_layer_in_commentary | synthetic |
| 37.1 | NFC normalization flagged | NFD text → NFC normalized | nfc_normalization_applied flag on source | synthetic |
| 37.2 | NFC text no flag | Already NFC text | No flag | synthetic |
| 38 | Confidence laundering | All atoms function_confidence 0.31 | low_function_confidence flags, ATOM_HIGH_UNCLASSIFIED_RATE | synthetic |

---

## Regression Testing Strategy

Gold baselines are immutable. Any code/prompt/config change triggers full regression against all gold baselines. Accuracy drops reject the change.

---

## Integration Tests

- **Upstream (passaging → atomization):** Process 3+ real passage streams. Zero input validation errors on well-formed passaging output.
- **Downstream (atomization → excerpting):** Atom stream validates against excerpting engine input contract (when available).

---

## Test Fixture Mapping

| Fixture | Available | Test Categories |
|---------|-----------|----------------|
| Gold prose passages | Needs creation | 1–8, 11–13, 26–30 |
| ibn_aqil_alfiyyah | ✓ | 7, 14, 15 |
| alfiyyah_versified | ✓ | 23 |
| mughni_comparative | ✓ | 16 (masala) |
| Synthetic passages | Needs creation | 9, 10, 16–25, 31–38 |
