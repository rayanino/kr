# Excerpting Engine — Boundary & Convention Diagnostic (Revised)

**Date:** 2026-03-31 | **Revision:** 2 (hardened through 5 adversarial passes)
**Scope:** 133 excerpts across 5 packages (ibn_aqil_v1, ibn_aqil_v3, taysir, ext_39_masala, ext_46_qa)
**Governing documents:** SPEC.md §3 (Self-Containment), §5 (Phase 2), §6 (Domain Rules), `.claude/rules/arabic-scholarly-conventions.md`

---

## Summary Statistics

| Package | Excerpts | FULL | PARTIAL | DEPENDENT | Genre |
|---------|----------|------|---------|-----------|-------|
| ibn_aqil_v1 | 19 | 17 | 2 | 0 | nahw sharh (verse-commentary) |
| ibn_aqil_v3 | 44 | 42 | 2 | 0 | nahw sharh (verse-commentary) |
| taysir | 28 | 18 | 9 | 1 | hadith sharh |
| ext_39_masala | 22 | 16 | 6 | 0 | fiqh masala (numbered rulings) |
| ext_46_qa | 20 | 16 | 4 | 0 | usul al-nahw (definitions/Q&A) |
| **TOTAL** | **133** | **109 (82%)** | **23 (17%)** | **1 (1%)** | |

Validation drops: 4 (EX-V-002: primary_text/text_snippet mismatch) — 3 in taysir, 1 in ext_46_qa.
Gate queue: taysir (1 entry, EX-G-002 DEPENDENT), ibn_aqil_v3 (12 entries, EX-G-001 — 3-model attribution disagreement confirmed by consensus verification).

---

## 1. BOUNDARY ERRORS

### B-1: Muqaddima Opening Sequence Split

**Where:** ibn_aqil_v1 div_2_000, units [0:0] and [0:1]

**What happens:** Unit [0:0] (49 words) contains bismillah + hamdala + salaat on the Prophet. Unit [0:1] (293 words) begins with "وبعد" (the sababiyyah transition) and contains the author's substantive introduction.

**Convention violated:** `arabic-scholarly-conventions.md`: "Treat the entire opening sequence (bismillah + hamdala + sababiyyah) as a single structural unit belonging to the muqaddimah." This convention applies at "position 0 of a book or volume," which this muqaddima is.

**Contrast:** ext_39_masala correctly groups the entire opening (bismillah + hamdala + أما بعد + author intro) as one 555-word unit.

**Epistemic impact:** Low. No false knowledge. The preamble is correctly labeled `editorial_note`.

**Note on scope:** A separate issue exists at the CHAPTER level — ibn_aqil_v1 div_2_001 [0:0] is a standalone 4-word bismillah ("بسم الله الرحمن الرحيم"). The convention is **silent** on chapter-level bismillah (it specifies "position 0 of a book or volume"). This is a SPEC concern (a 4-word unit has no pedagogical value per §5.3's "the smallest segment a student could study and learn something complete from"), not a convention violation.

**Proposed prompt addition:**
```
OPENING SEQUENCE RULE:
A bismillah (بسم الله الرحمن الرحيم) followed by hamdala and/or sababiyyah
(أما بعد / وبعد) must be grouped as one unit with the sequence that follows.
A standalone bismillah of fewer than 10 words is never a valid teaching unit —
merge it with the next substantive content.
```

---

### B-2: Hadith Sharh Fawa'id Separated from Parent Hadith

**Where:** taysir div_6 — units [0:8], [0:11], [0:15]; taysir div_7 — units [0:4], [0:6]

**What happens:** In hadith sharh texts, the commentary on each hadith follows a structured pattern: hadith text → gharib (vocabulary) → ijmali (overall meaning) → ikhtilaf (scholarly discussion) → fawa'id (ما يؤخذ من الحديث). The fawa'id sections are extracted as separate units and consistently marked PARTIAL because they reference "الحديث السابق."

**Evidence:** 6 of 9 PARTIAL taysir units have self-containment notes explicitly referencing the preceding hadith (e.g., "بعض الأحكام مبنية على الحديث السابق", "هذه الفوائد مبنية على حديث عثمان السابق"). 7 total units contain the "ما يؤخذ من الحديث:" marker.

**SPEC reference:** The Phase 2b prompt (§5.3.2 line 935) states: "A hadith + its chain + commentary = one unit." This rule is designed for short hadith citations within fiqh discussions, not for dedicated hadith commentaries where the "commentary" can exceed 500 words with multiple structured sections. The LLM partially follows this rule (sometimes grouping everything for short hadith) but splits when the commentary is long.

**SPEC gap:** §6 has no hadith-sharh-specific structural rule. §6.3 covers isnad atomicity and evidence-ruling binding, but not the multi-section commentary pattern.

**Epistemic impact:** Medium. The fawa'id sections are individually meaningful, but they lose their scholarly provenance — the owner reads a numbered ruling without knowing which hadith and chain of narration grounds it.

**Proposed SPEC amendment + prompt addition:** Amend line 935 to add a qualifier, then add the new rule:
```
EXISTING (line 935, amended):
- A hadith + its chain + commentary = one unit (for hadith citations embedded
  in broader discussions). For dedicated commentary sections, see the
  DERIVED BENEFITS rule below.

NEW RULE — DERIVED BENEFITS:
If a section opens with "ما يؤخذ من الحديث:" or "فوائد:" followed by
numbered items, apply the NUMBERED ITEM BOUNDARY rule to each item.
Each fawa'id item is assessed independently for self-containment.
```

Note: This rule is triggered by text-level signals ("ما يؤخذ من الحديث:"), not by `structural_format`, because the `StructuralFormat` enum has no `HADITH_COMMENTARY` value — both nahw sharh and hadith sharh are `COMMENTARY`.

---

### B-3: Position + Disagreement Split (DP-5 violation)

**Where:** taysir div_6 units [0:18] → [0:19]

**What happens:** Unit [0:18] (PARTIAL, 14 segments) presents the hadith about الغرة والتحجيل and includes Abu Hurayra's understanding about extending the ghurra. Unit [0:19] (FULL, 14 segments) discusses "الخلاف في إطالة الغرة." The LLM itself notes in [0:18]'s self-containment: "فيستحسن وصلها بالوحدة التالية."

**SPEC rule violated:** §6.1 DP-5 (Counter-argument + Original): "A counter-argument must include enough of the original argument to be understood." The scholarly disagreement in [0:19] addresses Abu Hurayra's position from [0:18].

**Epistemic impact:** Medium. The disagreement becomes abstract without the specific claim being debated.

**Proposed prompt addition (worked example):**
```
WORKED EXAMPLE — POSITION + DISCUSSION:
If a hadith commentary includes a Companion's interpretation (فهم الصحابي)
followed by a scholarly discussion evaluating that interpretation ("الخلاف في..."),
both MUST be in the same unit. The discussion section addresses the specific
interpretation — splitting them means "scholars disagreed about X" without X.
```

---

### B-4: Numbered Masala Items Merged

**Where:** ext_39_masala div_2_000_pre unit [0:11]

**What happens:** Masala items 11 (102 chars: "الوصية الجائرة باطلة مردودة") and 12 (752 chars: "ولما كان الغالب...") are merged. The "12 -" marker IS present in the text at char 102. These are distinct rulings on different topics (void bequests vs. burial according to sunnah).

**Existing rule violated:** §5.3.2 line 938 already states: "Never group unrelated content (e.g., two different مسائل) into one unit." Items 11 and 12 are different مسائل. This is a violation of an existing rule, not a missing rule.

**Why the LLM merged them:** Item 12 opens with "ولما كان الغالب" — a continuation-style conjunction rather than a clean break. The "12 -" marker is present but the conjunction obscured the boundary.

**Proposed prompt reinforcement (strengthens line 938):**
```
ADD TO GROUPING RULES (after line 938):
- Numbered items (1-, 2-, 3-... or مسألة/فائدة + numbering) are strong unit
  boundary markers. Each numbered item is presumptively a separate teaching
  unit unless it explicitly continues the same argument as the previous item
  with linking constructions (فإن..., والشرط الثاني..., etc.).
```

---

### B-5: Standalone Structural Transition (6 words)

**Where:** ext_46_qa div_3_000_pre unit [0:6]

**What happens:** A 6-word unit: "الكلام في المقدمات فيها مسائل الأولى." This section heading teaches nothing.

**SPEC context:** Line 939 permits standalone structural transitions. The result is a 6-word excerpt with zero pedagogical value for the taxonomy/synthesis pipeline.

**Proposed prompt refinement (modifies line 939):**
```
AMEND line 939:
- structural_transition segments shorter than 15 words should be grouped with
  the first substantive unit that follows. Standalone structural_transitions
  are valid only when they carry enough content to serve as meaningful section
  markers (15+ words describing the upcoming topic).
```
Note: The 15-word threshold is a starting point. Calibration during the 30-book probe may adjust it.

---

### B-6: Cross-Division Fawa'id Continuation (UPSTREAM)

**Where:** taysir div_6 unit [0:0]

**What happens:** Opens with "5- وجوب الاعتناء بأعمال القلوب" — item 5 of a numbered benefits list. Items 1-4 are in the previous division (div_7).

**Root cause:** Normalization engine division boundary falls within a running text section. The excerpting engine cannot merge across divisions (by design — D-011).

**Action:** Flag for normalization engine review during 30-book probe.

---

### B-7: Cross-Unit Definition Reference

**Where:** ext_46_qa div_5_000 unit [0:5]

**What happens:** Contains a new definition by sahib al-Badi' plus the analytical note: "ويندفع الإيراد الأخير على كلام ابن عصفور" — referencing an objection from unit [0:4]. Marked PARTIAL. The core definition stands alone; the cross-reference is supplementary.

**Assessment:** PARTIAL is the correct level. No fix needed — the self-containment notes accurately describe the dependency.

---

### B-8: Fawa'id Granularity Inconsistency (discovered in hardening)

**Where:** taysir, across div_6 and div_7

**What happens:** The LLM handles the identical structural pattern ("ما يؤخذ من الحديث: 1- ... 2- ...") with different granularity across divisions:

| Division | Unit | Fawa'id items | Words | Granularity |
|----------|------|--------------|-------|-------------|
| div_7 | [0:7] | 1 item | 65 | Per-item |
| div_7 | [0:8] | 1 item | 32 | Per-item |
| div_6 | [0:8] | 5 items | 148 | All-in-one |
| div_6 | [0:11] | 7 items | 322 | All-in-one |
| div_6 | [0:15] | 13 items | 239 | All-in-one |

In div_7, each fawa'id item is its own teaching unit. In div_6, all items are grouped into one unit. This inconsistency means:

1. The taxonomy engine receives different granularity from different hadith — some have per-faidah units, others have 13-ruling mega-units.
2. A 13-item unit cannot map cleanly to taxonomy tree leaves (one excerpt → 13 potential leaf positions).
3. The owner's study experience is inconsistent across hadith.

**This is the strongest argument for the P-2 numbered-item boundary rule.** It resolves the inconsistency: all numbered items become separate units regardless of division.

---

## 2. CONVENTION COMPLIANCE

### Violations Found

**C-1: Companions Classified as "quoted_opinion" (not narrators)**

**Where:** taysir — at least 7 instances (Abu Hurayra, A'isha, Abdullah ibn Amr, Abdullah ibn Umar)

**What happens:** When text says "عن أبي هريرة رضي الله عنه قال: قال رسول الله صلى الله عليه وسلم..." — Abu Hurayra is classified as `role: "quoted_opinion"`. In hadith convention, Companions are narrators (رواة), not opinion-holders.

**SPEC gap:** The `quoted_scholars` role enum (§2.2, line 447) has exactly 3 values: `quoted_opinion`, `classification_frame`, `refuted_position`. There is no `narrator` role. Adding one requires a SPEC §2.2 amendment.

**Epistemic impact:** Medium. Downstream synthesis may present Abu Hurayra alongside jurists as if he expressed an independent scholarly opinion.

**C-2: Hyphen in Honorific (source artifact)**

**Where:** taysir unit [0:3] — "رَضِى-الله تَعَالَى عَنْهم"

**What happens:** A hyphen appears within the رضي الله عنهم honorific. This is an OCR/encoding artifact from the Shamela source, not a legitimate Arabic text form.

**Scope:** Normalization engine issue, not excerpting.

**C-3: Footnote Markers Inline**

**Where:** 12+ excerpts across ibn_aqil and taysir (markers like ⌜1⌝, ⌜4⌝)

**What happens:** Shamela footnote markers are embedded in `primary_text`. The convention says editorial apparatus should be tagged as `layer_type: editorial`. These markers are not tagged or separated.

**Scope:** Phase 1 / normalization issue.

### Conventions Verified Correct

**Isnad Atomicity: ✓ PASSED.** Zero split isnads across all 133 excerpts. Every hadith excerpt contains a complete isnad + matn chain within a single teaching unit. The convention's processing rule ("Isnads must be kept as atomic units — never split across passages or excerpts") is satisfied. Verified by checking all `evidence_hadith` units for isnad opening formulas (عَنْ, حدثنا, أخبرنا) and confirming matn text follows within the same unit.

**Cross-Reference Preservation: ✓ PASSED.** 16 excerpts across packages contain cross-reference formulas (كما تقدم, سيأتي, etc.). All are preserved in the `primary_text` AND captured in the structured `cross_references` metadata field with target descriptions. Example: ibn_aqil_v3 [0:4] preserves "وسيأتي الكلام على بقية العشرين" in text and has a `cross_references` entry with `target_description` identifying the referenced section. The convention's processing rule ("preserve cross-reference formulas in the excerpt even if the referenced target is in a different excerpt") is satisfied.

**Scholarly Abbreviation Preservation: ✓ PASSED.** No normalization between forms detected. All packages use the full form "صلى الله عليه وسلم" consistently (no ﷺ ligature, no صلعم abbreviation). Gender/number suffixes on رضي الله preserved correctly: عنه, عنها, عنهم all appear. The convention's rule ("preserve whichever form the source uses; do NOT normalize between forms") is satisfied.

**Honorific Preservation: ✓ PASSED.** In `quoted_scholars` entries, `mention_text` preserves honorifics (e.g., "شيخ الإسلام", "الحافظ ابن حجر"), while `resolved_name` strips them for matching (e.g., "أحمد بن عبد الحليم ابن تيمية"). This matches the convention: "strip leading honorifics to get the base name for matching. But PRESERVE honorifics in the displayed/stored name."

### Borderline Findings

**Embedded Textual Variant Notes:** taysir has 2 excerpts with editorial apparatus notes embedded in commentary: "وفي الأصل: الحدث، الإيذاء" (unit [0:2]) and "كذا في نسخة العمدة لفظ مرتين" (unit [0:16]). The convention says marginal notes should be tagged as editorial. These are scholarly commentary about textual variants, not separate marginalia — borderline. Not a clear violation, but worth monitoring during the 30-book probe.

**School Attribution Without Textual Signals:** 3 taysir excerpts receive "حنبلي" school attribution (confidence 0.5-0.65) with zero school-specific terminology in the text. The attribution derives from the book's general Hanbali orientation. Low confidence appropriately reflects the uncertainty, but the convention says to detect school from terminology signals, not book-level metadata.

---

## 3. LAYER HANDLING

### L-1: Taysir All-Matn Attribution (correct but misleading naming)

All 28 taysir excerpts: `layer_id: "matn"`, `rule_applied: "LA-4"`, `coverage_pct: 1.0`.

Taysir is a sharh by al-Bassam, but the normalization engine detects only one text layer (hadith sharh doesn't use typographic matn/sharh interleaving like nahw verse-commentary). LA-4 (single layer, 100% coverage) is the correct rule. But `layer_id: "matn"` is misleading — the writing is by the commentator (al-Bassam), not the hadith compiler. The `author_id: "unknown"` is correct (no author resolution for the default single layer).

**Recommendation:** Consider renaming the default single-layer `layer_id` from "matn" to "primary" or "sole_layer," or ensure Phase 3 enrichment overrides with the source manifest's author field for single-layer texts.

### L-2: Ibn Aqil v3 LA-3 Ambiguity (correctly handled)

12 units in ibn_aqil_v3 with `rule_applied: "LA-3"` and `gate_flags: ["EX-G-001"]`.

**Trigger:** These units are LA-3 because the implementation detects **3+ text layers** (matn, sharh, plus editorial/other layers), not because of the SPEC's "<60% coverage" condition. The implementation (phase3_deterministic.py lines 234-261) applies LA-2 for exactly 2 layers (any coverage) and falls through to LA-3 for 3+ layers. Coverage values range from 0.35 to 0.78 — several units have >60% dominant coverage but are still LA-3 because of the layer count.

**EX-G-001 meaning:** These units went through Phase 3 consensus verification, and all 3 models DISAGREED on attribution. This is stronger than mere ambiguity — it's confirmed cross-model disagreement requiring human review.

**Assessment:** Correct behavior. The gate system works as designed.

### L-3: SPEC-Implementation Mismatch on LA-3 Threshold (discovered in hardening)

**What:** The SPEC §6.2 line 1281 states LA-3 triggers when "the dominant layer has <60% coverage." The implementation (phase3_deterministic.py line 234) applies LA-2 for any 2-layer case regardless of coverage. This means a 2-layer unit where the dominant layer covers only 55% gets LA-2 (confident attribution to the sharh author) rather than LA-3 (flagged for review).

**Evidence:** ibn_aqil_v3 [0:3] has `rule_applied: "LA-2"` with `coverage_pct: 0.591`. Per the SPEC, this 59.1% dominant coverage should trigger LA-3 ("dominant layer has <60% coverage"). But the implementation only checks layer count for the LA-2/LA-3 boundary.

**Epistemic impact:** A 59% sharh / 41% matn split gets a confident attribution to the sharh author without multi-model review. If the layer detection is even slightly wrong, the owner studies matn content believing it's sharh — a T-2 attribution error.

**Recommendation:** File as implementation bug for CC to fix. The LA-2 guard at line 234 should add a coverage threshold check: `if len(coverages) == 2 and top_coverage >= 0.6`.

---

## 4. GENRE DIFFERENCES

### Fiqh Masala (ext_39) — Cleanest Boundaries
Numbered masala format produces the cleanest boundaries. 16/22 FULL. Each numbered item naturally delineates a self-contained ruling with evidence. The only boundary error (B-4) is a single violated existing rule. Fiqh excerpts cite evidence (Quran, hadith) more frequently per unit — 15/22 content_types include `evidence_hadith`.

### Nahw Sharh (ibn_aqil) — Verse-Commentary Works Well
59/63 FULL across both packages. The LLM recognizes Alfiyya verse lines as topic delimiters and consistently groups verse + commentary (VC-1 satisfied — zero cases of verse separated from commentary). The challenge is layer attribution (12 LA-3 units), which is inherent to verse-commentary structure.

### Hadith Sharh (taysir) — Highest PARTIAL Rate, Needs Genre-Specific Rules
Only 18/28 FULL (64%). The multi-section commentary structure produces predictable dependencies. Key insight: the Phase 2b prompt has no hadith-sharh-specific awareness. The decontextualization rules (DP-1 through DP-6) address generic scholarly patterns but miss the numbered fawa'id pattern. The `structural_format` field can't distinguish hadith sharh from other commentary types.

### Usul al-Nahw (ext_46_qa) — Good Definition Handling
16/20 FULL. Definition sequences (multiple scholars defining "النحو") are correctly individuated. PARTIAL cases are from cross-definition references, which are inherent to the comparative style.

---

## 5. SPEC DEFECTS DISCOVERED

### SD-1: DP Rule Numbering Conflict

§6.1 defines DP-1 through DP-6 (decontextualization prevention rules). §10.5 (Domain Rule Tests) defines a **different** DP-1 through DP-6 with different names and descriptions. For example:

| Rule ID | §6.1 Definition | §10.5 Definition |
|---------|-----------------|------------------|
| DP-5 | Counter-argument + Original | Definition-example binding |
| DP-3 | Rule + Exception | Conditional endorsement |

This creates ambiguity when a review references "DP-5" without specifying which section. Recommend renumbering §10.5 test cases to avoid collision (e.g., DPT-1 through DPT-6).

### SD-2: LA-3 Implementation Gap

(Detailed in L-3 above.) The SPEC's <60% coverage condition for LA-3 is not implemented for 2-layer cases.

---

## 6. PROPOSED PROMPT IMPROVEMENTS (revised after hardening)

Priority order based on frequency × epistemic impact × SPEC consistency:

### P-1 (HIGH): Amend Hadith+Commentary Rule + Add Derived Benefits Rule

**Existing rule to amend (§5.3.2 line 935):**
```
CURRENT: "A hadith + its chain + commentary = one unit"
AMENDED: "A hadith + its chain + commentary = one unit (for hadith citations
  within broader discussions). For dedicated commentary sections, see the
  DERIVED BENEFITS rule below."
```

**New rule to add:**
```
DERIVED BENEFITS:
If a section opens with "ما يؤخذ من الحديث:" or "فوائد:" followed by
numbered items, apply the NUMBERED ITEM BOUNDARY rule to each item.
Each fawa'id item is assessed independently for self-containment.
```

**Addresses:** B-2 (fawa'id separation), B-8 (granularity inconsistency)
**SPEC note:** This amends an existing SPEC rule (line 935). Requires SPEC review.
**Cannot be conditioned on structural_format** — no `HADITH_COMMENTARY` enum value exists. Triggered by text-level signals.

### P-2 (HIGH): Reinforce Numbered Item Boundary (strengthens existing line 938)

**Context:** Line 938 already states "Never group unrelated content (e.g., two different مسائل) into one unit." The LLM violated this rule. P-2 adds explicit examples to reinforce it.

```
ADD after line 938:
- Numbered items (1-, 2-, 3-... or مسألة/فائدة + numbering) are strong unit
  boundary markers. Each numbered item is presumptively a separate teaching
  unit unless it explicitly continues the same argument as the previous item.
  A new number = a new topic, even if the conjunction (و) suggests continuation.
```

**Addresses:** B-4 (masala merging), B-8 (fawa'id inconsistency)

### P-3 (MEDIUM): Opening Sequence Rule

```
OPENING SEQUENCE:
A bismillah (بسم الله الرحمن الرحيم) followed by hamdala and/or sababiyyah
(أما بعد / وبعد) must be grouped as one unit. A standalone bismillah of
fewer than 10 words is never a valid teaching unit — merge it with the next
substantive content.
```

**Addresses:** B-1 (muqaddima split and chapter-level micro-bismillah). No conflict with existing rules.

### P-4 (MEDIUM): Structural Transition Minimum Size

```
AMEND line 939:
- structural_transition segments shorter than 15 words should be grouped with
  the first substantive unit that follows it, not left standalone.
```

**Addresses:** B-5 (6-word heading as standalone unit). Calibrate threshold during 30-book probe.

### P-5 (LOW): Add "narrator" Role to Scholar Schema

Requires SPEC §2.2 amendment: add `narrator` to the `ScholarAttribution.role` enum (currently: `quoted_opinion`, `classification_frame`, `refuted_position`). Phase 3 enrichment should classify mentions preceded by hadith transmission formulas (عن، حدثنا، أخبرنا) as `narrator`, not `quoted_opinion`.

**Addresses:** C-1 (Companions as quoted_opinion)

---

## 7. NON-EXCERPTING ISSUES

**Normalization engine:** Hyphen in honorific (C-2), footnote marker handling (C-3), cross-division fawa'id split (B-6), layer detection in hadith sharh format (L-1).

**Phase 3 enrichment — Canonical name inconsistency:** Same scholars receive different canonical names across chunks because each chunk gets independent LLM enrichment:
- الأخفش → "الأخفش الأوسط سعيد بن مسعدة" vs "سعيد بن مسعدة الأخفش الأوسط"
- المصنف → "محمد بن عبد الله بن مالك" vs "محمد بن عبد الله بن مالك الطائي"

If synthesis treats these as different scholars, the owner gets a distorted picture. Consider a post-enrichment canonical name normalization pass or a scholar registry lookup that enforces consistent naming.

**Schema naming:** `layer_id: "matn"` for single-layer sharh texts is misleading (L-1).

---

## 8. ADDITIONAL VERIFIED-CORRECT FINDINGS

The following were explicitly tested and found correct:

**No decontextualization violations in FULL excerpts.** No FULL excerpt opens with a refutation marker lacking its original position. DP-1 through DP-6 (§6.1 versions) are satisfied across all 133 excerpts (within-unit checks).

**Evidence-ruling binding (DP-4) satisfied.** No excerpt has an isolated evidence citation (evidence_quran, evidence_hadith) without an accompanying ruling or discussion.

**Epithet resolution (IR-2) correct.** المصنف consistently resolved to محمد بن عبد الله بن مالك (Ibn Malik) in the Ibn Aqil sharh context — correct per convention (المصنف = matn author in sharh).

**Description accuracy verified.** 5/5 randomly sampled `description_arabic` fields accurately summarize their excerpt content.

**Borderline C-SC-2 case (noted, not error):** ext_46_qa [0:12] (FULL) contains "الأدلة المذكورة" — a reference to previously-defined evidences. Technically "المذكور" is a C-SC-2 anaphoric reference. The reference is parenthetical; the core teaching (definition of المستدل) stands alone. FULL is a defensible classification, but a strict C-SC-2 reading could argue PARTIAL.

---

## 9. OVERALL ASSESSMENT

The excerpting engine produces **good to very good results** across 4 of 5 genres. Nahw sharh (94% of 63 excerpts FULL), fiqh masala (73% FULL), and usul al-nahw (80% FULL) all perform well.

**The systemic weakness is hadith sharh texts** (64% FULL), driven by the multi-section commentary structure and the absence of genre-specific prompt rules. This is addressable through prompt improvements P-1 and P-2, which together resolve both the fawa'id dependency pattern and the granularity inconsistency.

**No silent knowledge corruption detected.** All PARTIAL/DEPENDENT cases are correctly identified and flagged. Self-containment notes are accurate and descriptive. The gate system correctly routes the one DEPENDENT excerpt and 12 ambiguous-attribution excerpts for human review.

**Two SPEC defects discovered** (SD-1: DP numbering collision; SD-2: LA-3 implementation gap) that are unrelated to the prompt improvements but should be fixed.

**The 30-book probe should prioritize:**
1. Hadith sharh texts (multiple books) — test P-1/P-2 prompt improvements
2. Books with different muqaddima structures — test P-3
3. Mixed-layer texts — verify LA-3 threshold fix catches borderline attributions
4. Canonical name consistency across a full book (many chunks = many enrichment calls)
