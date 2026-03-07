# Passaging Engine — Test Plan

Maps the 12 test categories from SPEC §10 to test fixtures and specific test cases.

---

## Test Category 1: Cross-Page Text Assembly (§10.1)
**Module:** `assembly.py`
**Fixture:** Synthetic (generated from any normalized fixture)
**Min test cases:** 12

| # | Test Case | Input | Expected | Fixture |
|---|-----------|-------|----------|---------|
| 1.1 | Mid-word page break | Unit ending with `ال` + unit starting with `كتاب` | `الكتاب` (joined) | synthetic |
| 1.2 | Mid-sentence page break | Unit ending `في` + unit starting `المسجد` | `في المسجد` (space join) | synthetic |
| 1.3 | Clean paragraph break | Unit ending `.` + unit starting new paragraph | Two paragraphs separated by `\n\n` | synthetic |
| 1.4 | Footnote renumbering | Units with markers `⌜1⌝`, `⌜1⌝` → renumbered to `⌜1⌝`, `⌜2⌝` | Sequential markers starting from 1 | synthetic |
| 1.5 | Layer rebasing | Two units each 100 chars, layer segments at unit-local offsets | Segments rebased to assembled text offsets (100-199 for second unit) | synthetic |
| 1.6 | Tanwin at page boundary | Unit ending with `كتابًا` + unit starting `في` | `كتابًا في` (space, NOT joined) | synthetic |
| 1.7 | Quran citation spanning pages | Unit ending `﴿وأقيموا` + unit starting `الصلاة﴾` | `﴿وأقيموا الصلاة﴾` (joined inside brackets) | synthetic |
| 1.8 | Unclosed Quran bracket | `﴿` with no `﴾` across entire division | Treat as regular text, PSG_ASSEMBLY_QURAN_UNCLOSED logged | synthetic |
| 1.9 | boundary_continuity mid_sentence | Continuity says mid_sentence → direct join | No space between units | synthetic |
| 1.10 | boundary_continuity division_break | Continuity says division_break → paragraph break | `\n\n` between units | synthetic |
| 1.11 | Low-confidence continuity fallback | Continuity confidence <0.7 → use character heuristics | Same result as no continuity data | synthetic |
| 1.12 | Empty content unit | Unit with empty primary_text | Skipped in assembly, no text contributed | synthetic |

---

## Test Category 2: Prose Strategy Sizing (§10.2)
**Module:** `strategies/prose.py`
**Fixture:** Synthetic division trees with known word counts
**Min test cases:** 15

| # | Test Case | Division Size | Expected Action |
|---|-----------|--------------|-----------------|
| 2.1 | Exactly at minimum (50 words) | 50 | direct |
| 2.2 | Below merge threshold | 30 | merged with sibling |
| 2.3 | In target range (500 words) | 500 | direct |
| 2.4 | Exactly at soft max (800 words) | 800 | direct |
| 2.5 | Between soft max and hard max | 1500 | direct (with review flag) |
| 2.6 | Exactly at hard max (2000 words) | 2000 | direct |
| 2.7 | Just over hard max (2001 words) | 2001 | split |
| 2.8 | Very large division | 5000 | split into 3+ passages |
| 2.9 | Nested divisions requiring recursive merge | 20+30 words at depth 3 | merged upward |
| 2.10 | Multi-level split with paragraph boundaries | 4000 words, 8 paragraphs | split at paragraph boundaries |
| 2.11 | Division with no paragraph breaks | 3000 words, no `\n\n` | split at sentence boundaries |
| 2.12 | Merge with non-adjacent sibling (skip empty) | 30 + empty + 25 words | merge the two non-empty siblings |
| 2.13 | Single tiny division (no siblings to merge) | 10 words | direct (flagged very_short) |
| 2.14 | LLM splitting threshold | 1100 words | LLM-assisted splitting attempted |
| 2.15 | Paragraph split respects sentence integrity | Split at paragraph, verify no mid-sentence | Boundary at sentence terminal |

---

## Test Category 3: Verse Strategy (§10.3)
**Module:** `strategies/verse.py`
**Fixture:** `alfiyyah_versified/`, `ibn_aqil_alfiyyah/`
**Min test cases:** 8

| # | Test Case | Fixture |
|---|-----------|---------|
| 3.1 | 100 verses across 5 divisions, no verse split | alfiyyah_versified |
| 3.2 | Commentary-on-verse with interleaved matn/sharh | ibn_aqil_alfiyyah |
| 3.3 | Verse passage at division boundary | alfiyyah_versified |
| 3.4 | Very short verse division (3 verses, ~30 words) | synthetic |
| 3.5 | Very long verse division (50 verses, ~1500 words) | synthetic |
| 3.6 | Verse numbering preserved within passage | alfiyyah_versified |
| 3.7 | Mixed verse + prose in same source | ibn_aqil_alfiyyah |
| 3.8 | Verse with no hemistichs (prose-like verse) | synthetic |

---

## Test Category 4: Format-Specific Strategy Selection (§10.4)
**Module:** `strategy.py`
**Fixture:** Synthetic manifests
**Min test cases:** 7

| # | Test Case | structural_format | Expected Strategy |
|---|-----------|-------------------|-------------------|
| 4.1 | Prose | `prose` | ProseStrategy |
| 4.2 | Verse | `verse` | VerseStrategy |
| 4.3 | Q&A | `qa_format` | QAStrategy |
| 4.4 | Tabular khilaf | `tabular_khilaf` | MasalaStrategy |
| 4.5 | Dictionary | `dictionary` | DictionaryStrategy |
| 4.6 | Commentary | `commentary` | CommentaryStrategy |
| 4.7 | Mixed (per-division) | `mixed` | Per-division selection |

---

## Test Category 5: Self-Validation (§10.5)
**Module:** `validator.py`
**Fixture:** Intentionally malformed passage streams
**Min test cases:** 9

| # | Test Case | Defect Injected | Expected Check |
|---|-----------|-----------------|----------------|
| 5.1 | Coverage gap | Remove one content unit from passages | #1 fails (fatal) |
| 5.2 | Overlap | Add same unit to two passages | #2 fails (fatal) |
| 5.3 | Size violation | Passage with 7000 words | #6 flags (warning) |
| 5.4 | Ordering violation | Swap two passages' sequence_index | #3 fails |
| 5.5 | Mid-sentence boundary | End passage mid-word | #8 flags (warning) |
| 5.6 | Broken predecessor link | Set wrong predecessor_id | #9 fails (fatal) |
| 5.7 | Lost author attribution | Remove a layer from text_layers | #10 fails (fatal) |
| 5.8 | Orphaned footnote | Footnote entry with no `⌜N⌝` in text | #11 flags (warning) |
| 5.9 | Text loss | passage_text shorter than sum of units | #4b fails (fatal) |

---

## Test Category 6: Sentence Integrity (§10.6)
**Module:** `assembly.py`, `strategies/prose.py`
**Fixture:** Synthetic Arabic texts
**Min test cases:** 6

| # | Test Case |
|---|-----------|
| 6.1 | Text with only Arabic punctuation (، ؛ .) |
| 6.2 | Text with mixed Arabic/Latin punctuation |
| 6.3 | Text with no punctuation (heuristic detection) |
| 6.4 | Quran citation at page boundary (﴿...﴾ spanning) |
| 6.5 | Sentence ending with ؟ (question mark) |
| 6.6 | Multiple consecutive short sentences |

---

## Test Category 7: Isnad Chain Preservation (§10.7)
**Module:** `strategies/prose.py`, `strategies/masala.py`
**Fixture:** Synthetic hadith texts
**Min test cases:** 4

| # | Test Case |
|---|-----------|
| 7.1 | Short isnad chain (3 narrators + matn) |
| 7.2 | Long isnad chain (7+ narrators) |
| 7.3 | Nested isnad (حدثنا X قال حدثنا Y within larger chain) |
| 7.4 | Isnad spanning page boundary |

---

## Test Category 8: Content Census Adaptation (§10.8)
**Module:** `adaptive_passaging.py`
**Fixture:** Synthetic content censuses
**Min test cases:** 4

| # | Test Case | Census Characteristic | Expected Adaptation |
|---|-----------|----------------------|---------------------|
| 8.1 | High technical term density | technical_term_density > 0.15 | Smaller target_passage_words_high |
| 8.2 | Low structural depth | structural_depth.max_depth < 2 | Lower llm_splitting_threshold |
| 8.3 | High footnote density commentary | footnote_density.mean > 5 per page | Reduced size targets, footnote_factor < 1.0 |
| 8.4 | Absent content census | null | Default config unchanged |

---

## Test Category 9: Argument Boundary Detection (§10.9)
**Module:** `arguments.py`
**Fixture:** `mughni_comparative/`, synthetic مسألة texts
**Min test cases:** 7

| # | Test Case |
|---|-----------|
| 9.1 | Standard مسألة block: claim/evidence/counter/response/conclusion |
| 9.2 | Oversized argument needing internal split at فرع boundaries |
| 9.3 | Two adjacent small مسائل that should NOT merge |
| 9.4 | Discourse flow as primary signal |
| 9.5 | Keyword fallback producing same result as discourse flow |
| 9.6 | Cross-page argument cycle via boundary_continuity mid_argument |
| 9.7 | Argument nesting depth cap (3) hit |

---

## Test Category 10: Discourse-Aware Boundary Optimization (§10.10)
**Module:** `discourse_optimization.py`
**Fixture:** Synthetic discourse flow data
**Min test cases:** 5

| # | Test Case |
|---|-----------|
| 10.1 | Two candidates with different costs → pick lower |
| 10.2 | Boundary slides ±100 words to lower-cost point |
| 10.3 | No low-cost boundary → pick best, flag high_cost_boundary |
| 10.4 | Discourse optimization does not override size constraints |
| 10.5 | Multiple viable low-cost points → pick closest to original |

---

## Test Category 11: Completeness Forecast (§10.11)
**Module:** `completeness_forecast.py`
**Fixture:** Synthetic discourse flow data
**Min test cases:** 6

| # | Test Case |
|---|-----------|
| 11.1 | Complete argument cycle → forecast "complete" |
| 11.2 | Only position segments → forecast "fragment" |
| 11.3 | Ends with objection without response → "partial_closing" |
| 11.4 | Corrective merge triggered for fragment |
| 11.5 | Authorial incompleteness distinguished from structural |
| 11.6 | Corrective merge cap (max 2) respected |

---

## Test Category 12: Boundary Continuity Integration (§10.12)
**Module:** `assembly.py`
**Fixture:** Synthetic content units with boundary_continuity
**Min test cases:** 4

| # | Test Case |
|---|-----------|
| 12.1 | mid_sentence continuity overrides final-form heuristic |
| 12.2 | division_break continuity inserts paragraph break |
| 12.3 | mid_argument continuity recorded for argument detection |
| 12.4 | Low-confidence (<0.7) triggers character heuristic fallback |

---

## Gold Baselines (§10)

| Baseline | Source | Fixture | Status |
|----------|--------|---------|--------|
| Prose sharh | شرح ابن عقيل | ibn_aqil_alfiyyah | Needs hand-verification |
| Versified | ألفية ابن مالك | alfiyyah_versified | Needs hand-verification |
| Q&A | fatwa collection | TBD — needs fixture | Missing |
| Headingless | minimal structure text | TBD — needs fixture | Missing |
| Masala-block | المغني | mughni_comparative | Needs hand-verification |

Gold baselines require: normalized package input + expected passage output + boundary annotations.

---

## Integration Tests

| Test | Upstream/Downstream | Verification |
|------|--------------------|--------------| 
| Normalization → Passaging | Read real normalization output | All manifest fields present, content units ordered |
| Passaging → Atomization | Atomization reads passage stream | Schema compatible, all required fields accessible |
