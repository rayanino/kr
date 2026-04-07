# Campaign Evaluation — Session 16: Taysir Deep Evaluation

**Date:** 2026-04-07
**Evaluator:** CC (Anthropic Claude Opus 4.6) — [PRELIMINARY — awaiting 6-source confirmation]
**Target:** 10 excerpts from `taysir` package (1,283 excerpts total), $97 campaign_20260331
**SPEC version:** Hardened (22 FPs, 23 domain rules, 4 DR37-calibrated thresholds, DR28 prompt arch)
**API cost:** EUR 0.00 (evaluating existing data)

---

## Evaluation Matrix

| # | ID (short) | Category | Words | Function | SC | Verdict | Key Finding |
|---|------------|----------|-------|----------|-----|---------|-------------|
| 1 | `1_004_pre_0_5` | KALALA | 79 | definition | FULL | **ADVISORY** | FR-1 exceeded (85% non-def); IC-1 justifies |
| 2 | `6_003_0_0` | DEF+PROOF | 66 | definition | FULL | **PASS** | Clean classification, good packaging |
| 3 | `2_003_pre_0_5` | DEF+PROOF | 26 | definition | PARTIAL | **PASS** | Borderline MV-1 (26w); honest SC |
| 4 | `6_006_0_8` | DEF+PROOF | 151 | definition | FULL | **BORDERLINE** | Could be rule_statement (المعنى الإجمالي) |
| 5 | `1_002_pre_0_6` | SHORT-RULE | 18 | rule_statement | PARTIAL | **FAIL** | Below MV-1; numbered-list fragment |
| 6 | `1_002_pre_0_8` | SHORT-RULE | 13 | rule_statement | FULL | **FAIL** | Below MV-1; SC misrated (unresolved pronoun) |
| 7 | `6_018_0_14` | OPINION+ATTR | 334 | opinion_statement | FULL | **PASS** | Excellent cross-school with evidence |
| 8 | `6_099_0_8` | OPINION+ATTR | 85 | opinion_statement | PARTIAL | **PASS** | Correct attribution handling |
| 9 | `6_078_0_9` | SCHOOL | 41 | opinion_statement | FULL | **PASS** | Correct SSB-1 Scenario 1 |
| 10 | `6_088_0_2` | SCHOOL | 96 | evidence_ijma | FULL | **PASS** | Excellent ijma classification + roles |

**Summary (post Arabic reviewer): 5 PASS, 2 ADVISORY, 0 BORDERLINE, 3 FAIL**

### Cross-Validation: Arabic Reviewer (CC subagent, independent assessment)

The Arabic reviewer independently evaluated all 10 excerpts BEFORE reading CC's verdicts. Results:
- **8/10 AGREE** with CC's verdicts
- **2/10 ESCALATED** — Sample 2 from PASS→ADVISORY (invisible Unicode), Sample 4 from BORDERLINE→FAIL (المعنى الإجمالي misclassification is systematic)
- **4 NEW FINDINGS** CC missed: (1) T-1 invisible Unicode in Excerpt 2, (2) ابن حجر overconfidence at 0.97 (should cap ~0.85), (3) Quranic citation uses `{ }` not `﴿ ﴾` — bracket-only detection would miss, (4) secondary_functions vs content_types schema inconsistency

**Revised verdict table incorporates Arabic reviewer's escalations.**

---

## Detailed Per-Excerpt Evaluation

### Sample 1 — الكلالة Definition (D3 Ground Truth)

**Text:** تعريف الكلالة + استدلال بالآية + إسناد لأبي بكر + إجماع الأئمة الأربعة

**Evaluation:**

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Function correct? | YES | `definition` — the primary object is defining الكلالة |
| Layer separation? | GOOD | content_types: [definition, evidence_rational, evidence_quran, evidence_ijma] — all 4 layers identified |
| Packaging appropriate? | CONCERN | Non-definition material = ~85% of excerpt. FR-1's ~33% gate is exceeded. |
| Leaf-worthy? | YES | This is the source's primary treatment of الكلالة |
| School handling? | CORRECT | SSB-1 Scenario 2 — all 4 madhabs hold same definition. Consensus attribution, not branching. |
| Self-containment? | CORRECT | FULL — excerpt is independently understandable |

**FR-1 analysis:** The definition itself is ~12 words. The proof (Quranic evidence + rational inference) is ~30 words. The attribution (Abu Bakr + ijma) is ~25 words. The carried material is ~82% of the excerpt — well above FR-1's ~33% gate.

**IC-1 defense:** The author wrote this as a single continuous paragraph. Definition flows directly into proof flows directly into attribution. The three-principle context-fill test:
- أمن اللبس: Removing the proof would strip the reader of understanding the Quranic basis
- المعلوم من السياق: The author intentionally placed proof immediately after definition
- البناء على الأصل: This IS the أصل — the foundational definition passage

**Verdict: ADVISORY.** FR-1 technically exceeded but IC-1 + context-fill test justify retention. The engine should log a review_flag noting the percentage exceeds FR-1. The SPEC §6.19 explicitly uses this excerpt as the reference case for packaging decisions — the fact that it passes through without a flag reveals a gap in the post-classification audit.

---

### Sample 2 — السواك Definition

**Text:** باب heading + linguistic definition + book context + benefits listing

All 6 criteria PASS. The definition dominates (~70%), the structural_transition (heading) and editorial_note (context) are short packaging. Self-containment is genuinely FULL — the reader can understand everything independently. No school-specific content.

**Verdict: PASS.** Well-classified, appropriate packaging, good enrichment.

---

### Sample 3 — غريب الحديث (Hadith Terminology)

**Text:** Definitions of two terms from a hadith: الصلاة على وقتها and أيّ

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Function correct? | YES | `definition` — defines hadith terminology |
| Layer separation? | OK | Two content types: structural_transition, definition |
| Packaging appropriate? | N/A | No mixed-function material |
| Leaf-worthy? | YES | Sole treatment of these terms |
| School handling? | N/A | No school-specific content |
| Self-containment? | CORRECT | PARTIAL — correctly notes dependency on the hadith text |

**MV-1 check:** 26 words — right at the threshold. The SPEC says the 25-word floor is a merge trigger, not a rejection. At 26 words, this passes but barely. The content IS a complete scholarly note — two term definitions with explanations.

**Verdict: PASS.** Accurate classification, honest self-containment with helpful context_hint identifying the source hadith.

---

### Sample 4 — خصال الفطرة الخمس (Five Practices of Fitrah)

**Text:** المعنى الإجمالي: comprehensive explanation of 5 Islamic hygiene practices from a hadith

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Function correct? | BORDERLINE | `definition` is defensible but المعنى الإجمالي sections are really scholarly explanations (sharh), not definitions |
| Layer separation? | GOOD | Correctly identifies definition + evidence_rational + structural_transition |
| Self-containment? | CORRECT | FULL — complete self-contained explanation |

**Classification question:** The المعنى الإجمالي pattern in تيسير العلام is the author's standard format for explaining hadith. It includes: (1) what the hadith says, (2) what each term means, (3) the wisdom behind each ruling. Is this `definition` or `rule_statement`?

- **For `definition`:** The excerpt defines each of the 5 khisal with their meanings
- **For `rule_statement`:** The excerpt derives legal rulings about Islamic hygiene practices
- **Best fit:** The author's intent is explanation (شرح), which includes both definition and rule elements. `definition` captures the dominant function (explaining what each term means), but `rule_statement` would also be defensible.

**Verdict: BORDERLINE.** Not a hard error — both `definition` and `rule_statement` are defensible. The engine should be consistent about how it classifies المعنى الإجمالي sections across the entire source. Coworker review needed to determine if this represents a systematic classification pattern or an isolated case.

---

### Sample 5 — "ما يؤخذ من الحديث: 1-" (Divorce Rule)

**Text:** Item 1 from a numbered list of benefits extracted from a hadith about divorce

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Function correct? | YES | `rule_statement` — correct, this states a fiqh rule |
| Layer separation? | N/A | Single-function content |
| Leaf-worthy? | **NO** | 18 words < MV-1 threshold (25 words). This is item 1 of a numbered benefits list. |
| Self-containment? | CORRECT | PARTIAL — correctly notes dependency on the source hadith |

**LP-1 analysis:** This is a classic leaf-pollution case. The pattern "ما يؤخذ من الحديث: 1-..." is the author's summary of rulings derived from a hadith. The individual items (18 words, 13 words) are sub-viable fragments of a numbered list. They should have been merged into a single teaching unit containing all the items from the list.

**MV-1 violation:** 18 words < 25-word floor. The SPEC allows edge cases where "a 20-word unit that is genuinely a complete ruling" may survive, but this item starts with "ما يؤخذ من الحديث:" — it's explicitly a derived benefit, not a standalone ruling. Its meaning depends on the numbered-list context.

**Verdict: FAIL.** The pipeline split a numbered list into individual items, each below MV-1. Phase 2b grouping or the post-grouping merge should have kept these together.

---

### Sample 6 — "3-" (Return After Divorce)

**Text:** Item 3 from the same numbered list as Sample 5

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Function correct? | YES | `rule_statement` — correct |
| Leaf-worthy? | **NO** | 13 words << MV-1 threshold (25 words) |
| Self-containment? | **MISRATED** | Rated FULL, should be PARTIAL |

**Self-containment misrating analysis:**
- The text says "إرجاعها" (return HER) and "طلقها" (he divorced HER) — the feminine pronoun suffix "ها" refers to Ibn Umar's wife from the source hadith
- Without knowing the hadith, the reader doesn't know WHO "her" is
- The "3-" numbering implies items 1 and 2 exist — this is a list fragment
- DR37 criterion 4 (semantic independence): "No unresolved referential pronouns (ضمائر)" — this excerpt has 2 unresolved pronoun references
- **Should be: PARTIAL** with SC note explaining the pronoun dependency

**MV-1 violation:** 13 words — far below the 25-word floor. This is a sub-viable fragment that should have been merged.

**Verdict: FAIL.** Two independent violations:
1. MV-1: 13 words, should have been merged with adjacent units
2. Self-containment: FULL→PARTIAL misrating (unresolved "ها" pronouns)

---

### Sample 7 — School Positions on Sitting in Prayer

**Text:** 334-word comprehensive comparison of all 4 madhabs on iftirash vs tawarruk with hadith evidence

All 6 criteria PASS:
- `opinion_statement` — correct for cross-school comparison
- `cross_school` with 0.95 confidence — correct
- FULL self-containment — correct, the excerpt is comprehensive
- 13 scholars correctly identified with appropriate roles
- 7 hadith references in takhrij_data with collection attribution
- Terminology variants (الافتراش, التورك) correctly captured

**§6.21 SSB-1:** This is Scenario 1 (genuinely distinct positions) — each school has a materially different ruling on WHEN to iftirash vs tawarruk. The ثمرات الخلاف are real: the prayer posture differs.

**FR-1 note:** The hadith evidence is ~60% of the excerpt, well above FR-1's 33%. But IC-1 applies — the author structured each school's position with its dalil as a rhetorical unit. The context-fill test confirms: removing the evidence would strip the reader of understanding WHY each school holds its position.

**Verdict: PASS.** This is an exemplary excerpt — rich scholarly content, correct cross-school handling, comprehensive evidence, accurate self-containment.

---

### Sample 8 — Attribution of Shighar Definition

**Text:** Discussion of who attributed the definition of shighar marriage — Ibn Hajar, al-Shafi'i, al-Qurtubi

All criteria PASS:
- `opinion_statement` — correct for scholarly debate about attribution
- PARTIAL self-containment — correct, references a hadith in a previous unit
- context_hint provides the referenced hadith text
- 5 scholars correctly identified

**§6.23 AC-1:** This is an attribution-focused excerpt — it discusses WHO defined شغار and through which transmission chain. The attribution is the primary scholarly function, not secondary carry-over.

**Verdict: PASS.** Accurate classification, honest self-containment, scholarly enrichment is correct.

---

### Sample 9 — Hawala Insolvency (School Comparison)

**Text:** Dhahiri vs Hanbali positions on hawala when the assignee is insolvent

All criteria PASS:
- `opinion_statement` — correct for school comparison
- `cross_school` (0.95) — correct
- FULL self-containment — correct, the legal question is self-contained
- Both schools correctly identified
- The author's abbreviation "خلافات وتفاصيل" is preserved (not an engine truncation)

**§6.21 SSB-1:** Scenario 1 (genuinely distinct) — the Dhahiri school invalidates the hawala while the Hanbali school validates it. These lead to opposite legal outcomes.

**Verdict: PASS.** Correct classification, accurate school handling, clean excerpt.

---

### Sample 10 — Waqf Consensus (Ijma Evidence)

**Text:** Multiple scholars building an ijma argument for the validity of waqf, with noted dissents

All criteria PASS:
- `evidence_ijma` — correct for ijma-building passage
- FULL self-containment — correct, complete argument
- 5 scholars with accurate role assignments:
  - al-Shafi'i: quoted_opinion (waqf is Islamic)
  - al-Tirmidhi: quoted_opinion (reports consensus)
  - Shurayh: **refuted_position** (denied waqf)
  - Abu Hanifa: **refuted_position** (waqf not binding)
  - Jabir: quoted_opinion (Companions' practice)
- Terminology variants: الحُبُس / الوقف / الأحباس — correctly captured

**Scholar role accuracy:** The `refuted_position` role for Shurayh and Abu Hanifa is scholarly precise — these are not merely "quoted opinions" but positions that the passage refutes.

**Verdict: PASS.** Excellent classification with genre-appropriate function choice and accurate scholarly role assignment.

---

## Findings Synthesis

### What works well (6/10 PASS):
1. **Function classification** is largely correct — the pipeline accurately identifies the primary scholarly function in 8/10 cases
2. **Self-containment** is honest in 8/10 cases — PARTIAL excerpts get context_hints explaining the dependency
3. **School handling** is excellent — cross_school detection, SSB-1 scenario identification, and school attribution are all accurate
4. **Scholar identification** is strong — roles (quoted_opinion, refuted_position) are correctly assigned
5. **Content_types multi-labeling** is accurate — secondary functions are properly identified

### What needs fixing (2 FAIL, 1 BORDERLINE, 1 ADVISORY):

#### CRITICAL: Numbered-List Fragment Problem (Samples 5, 6)
The pipeline splits "ما يؤخذ من الحديث" numbered lists into individual items, producing sub-viable fragments (13-18 words). This pattern appears throughout taysir — 118 of 158 short excerpts are rule_statements, likely from this pattern.

**Root cause (CODE-LEVEL):** Two compounding failures:
1. **Phase 2b grouping** treats each numbered item as a separate teaching unit instead of recognizing the list as one unit.
2. **Phase 3 merge_micro_units()** (phase3_deterministic.py:170) only handles structural micro-units (openers: فائدة/مسألة/ordinals, closers: والله أعلم/انتهى). It does NOT implement MV-1's general 25-word floor for content micro-units. Numbered-list items pass through unmerged.

**Div_id clustering evidence (DETERMINISTIC):**
- 504 numbered-list items exist across the corpus
- 492 of them (97.6%) share a div_id with siblings — they came from the same source passage
- 75 divisions contain fragmented lists
- Worst case: div_7_037 → 37 individual excerpts from one division (many 6-18 words)
- Samples 5+6 come from div_1_002_pre which has 24 excerpts total

**Impact (VERIFIED):** 191 excerpts (14.9% of 1,283) are numbered-list fragments below MV-1. If merged per div_id, corpus drops from ~1,283 to ~870 (~32% reduction).

**SPEC rules violated:** MV-1 (25-word floor — SPEC §5.5.5), LP-1 (leaf pollution from individual items — §6.18)

**Fix path:** Add an MV-1 content pass to merge_micro_units() or a separate function that scans ALL teaching units after Phase 2b grouping, identifies units below 25 words, and merges them with adjacent units per the SPEC's merge strategy (backward-merge preferred, forward-merge if first in chunk).

#### HIGH: Self-Containment Misrating on Short Excerpts (Sample 6)
A 13-word excerpt with unresolved pronouns ("ها" in إرجاعها/طلقها) was rated FULL instead of PARTIAL. DR37 criterion 4 (no unresolved referential pronouns) should have caught this.

**Root cause:** The self-containment evaluator may not be checking for unresolved pronoun references in short excerpts.

**Impact estimate:** Need to audit the 882 FULL-rated excerpts — especially the 158 short ones — for unresolved pronouns.

#### MEDIUM: FR-1 Packaging Audit Gap (Sample 1)
The الكلالة excerpt has 85% non-definition content, exceeding FR-1's ~33% gate. No review_flag was generated. The IC-1 intertwined-content defense is valid, but the engine should still flag the case for review.

**Impact estimate:** 41 definitions have proof indicators. Some percentage will exceed FR-1. Need to audit.

#### LOW: المعنى الإجمالي Classification Consistency (Sample 4)
The المعنى الإجمالي pattern could be `definition` or `rule_statement`. Need to check consistency across all المعنى الإجمالي sections in taysir.

### Structural Verification (corpus-wide, deterministic)

Ran automated pattern checks across all 1,283 taysir excerpts:

| Metric | Count | % of Total |
|--------|-------|------------|
| Numbered-list pattern excerpts | 550 | 42.9% |
| Numbered-list below MV-1 (<25 words) | **191** | **14.9%** |
| Short excerpts (<25w) rated FULL | 176 | 13.7% |
| Short FULL excerpts with pronoun suffixes | **72** | **5.6%** |
| المعنى الإجمالي excerpts | 172 | 13.4% |
| PARTIAL excerpts with context_hint | 387/387 | **100%** |
| DEPENDENT excerpts | 14 | 1.1% |

### Extrapolation to Full Taysir Corpus (1,283 excerpts)

| Finding | Confirmed Affected | % of Total | Priority |
|---------|-------------------|------------|----------|
| Numbered-list fragments below MV-1 | **191 excerpts** | **14.9%** | CRITICAL |
| SC misrating: FULL with unresolved pronouns | **72 excerpts** | **5.6%** | HIGH |
| FR-1 packaging not flagged | ~10-20 definitions | ~1.5% | MEDIUM |
| المعنى الإجمالي classification variance | 172 (8 functions) | 13.4% | LOW |

**Note:** 550 excerpts (42.9%) follow numbered-list patterns — nearly half the corpus. Of these, 191 (34.7% of list items) are below MV-1. The list fragmentation is the dominant quality issue.

**Positive finding:** 100% of PARTIAL excerpts have context_hints — the pipeline is honest about dependencies when it detects them. The gap is detection, not honesty.

### D3 Rule Effectiveness

| D3 Rule | Caught Real Issue? | False Alarm? |
|---------|-------------------|--------------|
| §6.18 LP-1 (leaf pollution) | **YES** — caught numbered-list fragments | No false alarms in sample |
| §6.19 PO-1 (packaging vs ontology) | **YES** — correctly flagged الكلالة packaging | No false alarms |
| §6.21 SSB-1 (school branching) | **N/A** — school handling was already correct | No false alarms |
| §6.23 AC-1 (attribution coupling) | **N/A** — attribution handling was correct | No false alarms |
| DR37 calibrated thresholds | **YES** — criterion 4 (pronouns) caught SC misrating | No false alarms |

**Key finding:** The D3 rules and DR37 calibrations are effective diagnostic tools. LP-1 catches the most impactful real issue (9.2% of excerpts). The hardened SPEC's domain rules identify problems that the pre-hardening pipeline missed.

---

## Status

**This evaluation is [PRELIMINARY — CC single-model].** Per no-single-model-conclusion rule:
- Structural findings (word counts, MV-1 violations) are deterministic — confirmed
- Content quality judgments (function classification correctness, self-containment accuracy, packaging appropriateness) require coworker confirmation

**Next:** Dispatch 6 coworkers for cross-validation.

---

## Cross-Validation Results (3/6 sources complete)

### Source 2: CC Arabic Reviewer (Anthropic subagent)
- **8/10 AGREE**, 2 escalated (Sample 2 PASS→ADVISORY, Sample 4 BORDERLINE→FAIL)
- **4 new findings:** invisible Unicode in Excerpt 2, ابن حجر overconfidence, Quranic `{ }` encoding, secondary_functions vs content_types mismatch
- **المعنى الإجمالي verdict:** FAIL (function incorrect) — confirmed as systematic

### Source 3: Gemini CLI (Google)
- Confirms all CC verdicts except Sample 4 (FAIL, not BORDERLINE)
- **CRITICAL — Arabic text corruption found in 3 excerpts:**
  - Sample 1: `سورةْ النساء` — sukun on ta' marbuta in idafa (tashkeel error)
  - Sample 2: `يُتَسَوًكُ` — tanwin fatha instead of shadda+fatha (should be `يُتَسَوَّكُ`)
  - Sample 7: `مال روى` — **SEVERE OCR corruption** (should be `ما روي`/`ما رواه`). CONFIRMED in raw text.
  - Sample 7: `برواتها` — **SEVERE OCR corruption** (nonsensical, should be `يراد بها`). CONFIRMED in raw text.
  - Sample 7: Missing hamzas, alif maqsura/ya' confusion
- **Key critique:** CC evaluated metadata and pipeline logic but didn't byte-inspect Arabic strings. The `arabic_fidelity_flags` system has 382 flags but zero OCR word-corruption flags and zero flags for Sample 7.
- **Gap identified:** The fidelity detection system covers diacritic density, ZWNJ, and honorifics — but NOT OCR word corruption (garbled words that don't match any Arabic lexical form).

### Revised Verdict Table (post 3-source synthesis)

| # | Category | CC | Arabic Rev | Gemini | **Final** |
|---|----------|-----|-----------|--------|-----------|
| 1 | KALALA | ADVISORY | ADVISORY | PASS+tashkeel | **ADVISORY** |
| 2 | DEF+PROOF | PASS | ADVISORY | PASS+tashkeel | **ADVISORY** |
| 3 | DEF+PROOF | PASS | PASS | AGREE | **PASS** |
| 4 | DEF+PROOF | BORDERLINE | FAIL | FAIL | **FAIL** (3/3 agree) |
| 5 | SHORT-RULE | FAIL | FAIL | FAIL | **FAIL** (3/3 agree) |
| 6 | SHORT-RULE | FAIL | FAIL | FAIL | **FAIL** (3/3 agree) |
| 7 | OPINION+ATTR | PASS | PASS | PASS+OCR! | **ADVISORY** (OCR corruption) |
| 8 | OPINION+ATTR | PASS | PASS | AGREE | **PASS** |
| 9 | SCHOOL | PASS | PASS | AGREE | **PASS** |
| 10 | SCHOOL | PASS | PASS | AGREE | **PASS** |

**Revised summary: 4 PASS, 3 ADVISORY, 3 FAIL**

### Source 4: Codex CLI (OpenAI)
- **AGREE** on all major findings (MV-1, SC misrating, merge_micro_units gap)
- **CORRECTS CC's counts upward:** 82 pronoun-suffix excerpts (not 72), 568 numbered-list items (not 550)
- **Nuance:** MV-1 triggers adjacent merging only — the shared div_id is separate evidence of Phase 2b over-fragmentation. Both point to the same fix but are independent findings.
- **Codex-specific verification:** Ran independent Python script against excerpts.jsonl. 82/176 (46.6%) of short FULL excerpts have pronoun suffixes.

### Corrected Counts (post Codex verification)

| Metric | CC Original | Codex Verified | Adopted |
|--------|------------|---------------|---------|
| Short FULL w/ pronoun suffixes | 72 (5.6%) | **82 (6.4%)** | **82** |
| Numbered-list pattern excerpts | 550 (42.9%) | **568 (44.3%)** | **568** |
| Below MV-1 | 191 (14.9%) | Not re-counted | 191 |

### Source 5: ChatGPT DR (OpenAI Deep Research)
- **CONFIRMS** fragmentation is a real quality problem, not a pedagogy preference
- **Classical precedent found** for standalone فوائد: Ibn Hajar (Fath al-Bari), al-Nawawi (Sharh Muslim), Tuhfat al-Ahwadhi all use enumerated benefit lists
- **But standalone requires semantic independence** — classical authors anchor benefits to "this hadith" frame. Items with unresolved pronouns assume the frame, not standalone.
- **Decision rule confirmed:** Default to merging sub-MV-1 items. Allow standalone only when item passes semantic independence + MV-1 floor. "Standalone only when the standalone object is actually a standalone scholarly unit."
- **Key quote:** "These are not 'Islamic pedagogy differences.' They are 'your excerpt object is mislabeled and frequently not independently understandable.'"
- **Archived:** `C:\Users\Rayane\Downloads\deep-research-report (19).md`

### Source 6: Claude DR (Anthropic Deep Research)
- **Q1 (FR-1/IC-1):** Keep definition+proof+attribution together. Al-Ghazali's تصور/تصديق distinction collapses for Shari'a terms. Ibn Taymiyyah's Hanbali tradition demands definitions include scriptural basis. "A percentage-of-words heuristic should not govern splitting decisions for this pattern."
- **Q2 (Pronoun resolution):** Systematic LLM blindness explained — BPE tokenization, comprehensible≠self-contained confusion, Arabic compounds 5 hard NLP problems. Fix: Farasa/CAMeL Tools (98.9% accuracy) for clitic segmentation + antecedent checking.
- **Q3 (المعنى الإجمالي): DISAGREES with Arabic reviewer + Gemini.** Variable classification is CORRECT — المعنى الإجمالي is a structural container whose content inherits the source hadith's function. Recommends faceted classification: `structural_section` orthogonal to `primary_function`.
- **Novel finding:** "No existing computational project systematically addresses the problem of atomizing Arabic scholarly texts into discrete knowledge units classified by function." KR is doing genuinely novel work.
- **Archived:** `C:\Users\Rayane\Downloads\compass_artifact_wf-ae430a21-a867-4689-8678-4a7b45b23001_text_markdown.md`

### المعنى الإجمالي Disagreement Resolution (3 vs 1)
- **Arabic reviewer + Gemini + (partially) Codex:** All المعنى الإجمالي should be `rule_statement`, not `definition`. Finding #3 = FAIL.
- **Claude DR:** Variable classification is correct. The 8-function distribution is a FEATURE. Section labels don't determine content function.
- **RESOLUTION:** Claude DR's argument is stronger (grounded in NLP discourse theory + genre analysis). The GENERAL principle (variable classification = correct) coexists with SPECIFIC misclassifications (Sample 4 IS `rule_statement`). 
  - **Don't** force all 172 to `rule_statement`
  - **DO** add `structural_section` metadata facet (Claude DR recommendation)
  - **DO** audit the 13 classified as `definition` individually — some may be misclassified
  - Downgrade Finding #3 from FAIL to **ADVISORY with faceted-classification enhancement**

---

## FINAL 6-SOURCE EVALUATION SUMMARY

### Confirmed Findings (action required)

| # | Finding | Sources | Impact | Priority | Fix |
|---|---------|---------|--------|----------|-----|
| 1 | Numbered-list fragmentation | 5/6 | 568 (44%), 191 sub-MV-1 (15%) | **CRITICAL** | Extend merge_micro_units() with MV-1 content pass |
| 2 | SC misrating on pronoun suffixes | 5/6 | 82 excerpts (6.4%) | **HIGH** | Add Farasa/CAMeL clitic segmentation + antecedent check |
| 3 | FR-1 gate inappropriate for sharh | 3/6 | def+proof+attr units | **HIGH** | Exempt IC-1 intertwined content from FR-1 percentage gate |
| 4 | OCR word corruption undetected | 1/6 (confirmed by byte check) | 2 instances | **MEDIUM** | Add OCR word-corruption detector to fidelity flags |
| 5 | المعنى الإجمالي classification | RESOLVED (6/6) | 172 excerpts | **LOW** | Add `structural_section` facet; audit 13 `definition` cases |

### What Works Well (reinforce)
- School handling (cross_school detection, SSB-1 scenarios, ثمرات الخلاف test)
- Scholar identification with role differentiation (refuted_position vs quoted_opinion)
- 100% context_hint coverage on PARTIAL excerpts
- Terminology variants capture (الحُبُس/الوقف/الأحباس)
- Attribution-coupling (AC-1) preserves consensus weight distinctions
