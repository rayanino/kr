# Scholarly Reasoning Soundness Evaluation — KR Excerpting Questionnaire

**Date:** 2026-04-01
**Author:** Claude Chat (Architect), Deep Research mode
**Status:** COMPLETE — 5-phase evaluation with tool-verified evidence
**Requested by:** Claude Code, as part of Phase 0 (Owner Q&A) hardening
**Input files read:**
- `integration_tests/questionnaire/QUESTIONNAIRE_TEMPLATE.md` (232 lines, 10 sections, 30 interaction points)
- `engines/excerpting/SPEC.md` — §2.3 (enumerations), §3 (self-containment), §5.3 (Phase 2b grouping), §6 (domain rules), §7 (Phase 3 enrichment)
- `integration_tests/campaign_20260331/taysir/owner_feedback.jsonl` (2 comments)
- `integration_tests/campaign_20260331/taysir/excerpts.jsonl` (1,283 excerpts)
- `integration_tests/campaign_20260331/*/excerpts.jsonl` (5 packages, 2,303 total excerpts)
- `integration_tests/campaign_20260331/analysis/scholarly_reality_check_intra_excerpt.md`
- `integration_tests/campaign_20260331/analysis/gemini_adversarial_DR_review.md`

**Files referenced but NOT found in repo (owner listed them but they don't exist yet):**
- `integration_tests/questionnaire/OWNER_QUESTIONNAIRE.md` — does not exist; `QUESTIONNAIRE_TEMPLATE.md` is the only questionnaire file
- `integration_tests/questionnaire/QUESTIONNAIRE_EXAMPLES.md` — does not exist
- `integration_tests/questionnaire/TEAM_TRANSLATION_GUIDE.md` — does not exist

---

## Table of Contents

1. [Overall Verdict](#overall-verdict)
2. [Phase 1: Coverage Analysis](#phase-1-coverage-analysis)
3. [Phase 2: Arabic Representativeness](#phase-2-arabic-representativeness)
4. [Phase 3: Definition-Splitting and Evidence-Handling](#phase-3-definition-splitting-and-evidence-handling)
5. [Phase 4: Misleading Interactions and Owner Intuition](#phase-4-misleading-interactions-and-owner-intuition)
6. [Phase 5: Synthesis and Recommendations](#phase-5-synthesis-and-recommendations)
7. [Appendix A: SPEC Rule Coverage Map](#appendix-a-spec-rule-coverage-map)
8. [Appendix B: Campaign Data Evidence](#appendix-b-campaign-data-evidence)
9. [Appendix C: Arabic Examples for Reference](#appendix-c-arabic-examples-for-reference)
10. [Appendix D: Translation Note Accuracy Audit](#appendix-d-translation-note-accuracy-audit)

---

## Overall Verdict

The questionnaire is a well-intentioned first draft that correctly responds to the owner's two feedback comments but is **not ready for deployment**. It would produce answers that are reliable for DR-1 and DR-3 calibration in fiqh texts, unreliable for evidence handling and genre-specific behavior, and actively misleading for nahw evidence, multi-layer attribution, and the physical-splitting-vs-multi-leaf-tagging decision.

The fundamental issue is that the questionnaire was designed around the owner's two specific complaints rather than around the SPEC's full domain rule space. It answers the questions the owner already asked rather than surfacing the questions the owner doesn't yet know to ask — which is exactly what a calibration questionnaire needs to do for a student who hasn't yet studied the texts.

Eight specific recommendations are provided in Phase 5. The highest-priority additions are: (1) a multi-layer attribution section (prevents T-2 knowledge integrity violations), (2) embedded Arabic examples with split-consequence views (prevents false-binary and anchoring problems), and (3) corrected Translation notes (three of ten are inaccurate).

---

## Phase 1: Coverage Analysis

### 1.1 Interaction Count

The questionnaire has **30 interaction points** across 10 sections (the owner's task description said "35 interactions" — the discrepancy is likely from counting Translation notes as interactions). Each interaction is a lettered question (a, b, c, d) with an "Owner response:" field.

### 1.2 Section-by-Section SPEC Rule Mapping

**Section 1 — Granularity (3 questions: 1a, 1b, 1c)**

Tests the boundary between excerpts — too short vs. too long. Maps to Phase 2b grouping behavior generally but does not test any specific named SPEC rule. It is a calibration question for the LLM's grouping sensitivity. Questions 1a and 1b are well-designed for their purpose. Question 1c is a forced-choice between two bad outcomes (see Phase 4 for why this is misleading).

Translation note issue: references a "minimum excerpt length threshold" that does not exist in the SPEC. Teaching unit size is determined by LLM grouping, not a configurable threshold. The only length thresholds in the SPEC are for Phase 1 chunk merge/split (§4.4 tiny division merging; §4.5 oversized division splitting at 5,000 words), which operate on chunks, not teaching units.

**Section 2 — Self-Containment (3 questions: 2a, 2b, 2c)**

Tests C-SC-2 (Reference Resolution, via question 2c about "as mentioned earlier") and C-SC-4 (Argument Completeness, via question 2a about understanding the main point). Also touches IR-1 (Intra-source cross-reference) and IR-3 (Unresolvable references). However, it completely misses C-SC-1 (Term Resolution) — no question asks whether the owner recognizes the technical terms in an excerpt. Also misses C-SC-3 (Evidence Completeness) and C-SC-5 (Dialogue Completeness), which are deferred to later sections.

**Section 3 — Comparison Experience (2 questions: 3a, 3b)**

This is a **synthesis/taxonomy** question, NOT an excerpting question. It tests whether excerpts across sources are comparable. Maps to nothing in the excerpting SPEC — it is a downstream concern for the taxonomy and synthesis engines. The example instruction says "Pick 3 excerpts from DIFFERENT books on the SAME fiqh topic (if available in campaign data)" — but this is **literally impossible** with the campaign data, because all 5 packages use `source_id=src_test0001` (see Appendix B for verification). Including this section is not harmful, but it consumes owner attention without calibrating excerpting behavior.

Translation note issue: references "whether excerpts need to be normalized for comparability" — this is a synthesis engine concern, not excerpting.

**Section 4 — Definition Handling (3 questions: 4a, 4b, 4c)**

Directly tests **DR-1** (definition pair splitting). This section was triggered by the owner's first feedback comment, which explicitly asked for لغة/شرعا definitions to be split. Questions are well-designed: 4a tests whether combined feels complete, 4b tests companion linking, 4c tests study workflow. The Translation note correctly identifies DR-1 as the target.

However: Section 4 only tests the لغة/شرعا binary pair pattern, which constitutes only **9.5% of all definitions** in the taysir campaign (10 out of 105 — see Phase 3 for full breakdown). Does not test غريب الحديث definitions (34.3%), plain definitions (39%), or nahw/usul definitions (completely different structure).

**Section 5 — Evidence Handling (3 questions: 5a, 5b, 5c)**

Tests **DP-4** (Evidence + Ruling grouping) and probes whether **DR-2** (evidence-type splitting, currently deferred) should be reconsidered. Question 5c about well-known hadith references touches C-SC-3 (Evidence Completeness) and EV-2 (Hadith references).

Translation note issue: references "whether DR-2 (evidence-type splitting, currently deferred) should be reconsidered." DR-2 was **explicitly rejected by 3/5 cross-provider reviewers** in the campaign analysis. The Translation note would direct the team to reconsider a governance decision that has already been made. This contradicts the review outcome documented in `integration_tests/campaign_20260331/analysis/scholarly_reality_check_intra_excerpt.md` and `integration_tests/campaign_20260331/analysis/gemini_adversarial_DR_review.md`.

**Section 6 — Scholarly Debate (3 questions: 6a, 6b, 6c)**

Tests **DR-3** (khilaf preservation), **DP-1** (Position + Refutation), and **DP-5** (Counter-argument + Original). Question 6c about seeing WHO holds each position tests metadata granularity for `school` and `quoted_scholars` fields. Reasonably designed.

However: missing the aqidah genre concern (identified by Gemini's adversarial review, line 74) — in theology texts, the linguistic vs. technical meaning of terms like إيمان and كفر is often the core of the sectarian debate itself. Splitting scholarly positions about such terms into separate excerpts can neutralize the theological argument.

**Section 7 — Genre Differences (3 questions: 7a, 7b, 7c)**

Covers three genres: fiqh, nahw, hadith. Question 7b (shaahid in grammar) touches VC-1 (Verse + commentary unity). Question 7c (isnad in hadith) touches EV-2 (Hadith references).

Critical issue with 7b: calls the شاهد an "example sentence," which is scholastically misleading. In Arabic grammar, the شاهد is foundational evidence (دليل) — not an optional illustration. Web research confirmed: "الشاهد عند النحويين هو الدليل الذي يعتمد عليه في الأخذ بقاعدة ما" (the shahid in nahw is the evidence that grammarians rely on to establish a rule). See Phase 4 for full analysis.

Critical issue with 7c: binary framing ("full chain or just the content?") misses partial chains, multi-chain citation, narrator commentary, and muhaqiq/editor takhrij apparatus. Also assumes the owner knows what isnad vs matn means — he is pre-study.

No question about: masala format (QM-1 through QM-3), Q&A format (DP-2), or verse-commentary structural patterns (VC-2, VC-3).

**Section 8 — Navigation (3 questions: 8a, 8b, 8c)**

Entirely a **downstream concern** — tests cross-reference design and taxonomy/synthesis linking. Like Section 3, maps to no excerpting SPEC rule. Question 8c about hashiyah is the only place multi-layer text is mentioned, but it's a navigation question, not an attribution question.

**Section 9 — The "No Puzzle" Rule (3 questions: 9a, 9b, 9c)**

Tests the `PARTIAL` self-containment level and `context_hint` mechanism. Directly relevant to the excerpting SPEC's Phase 3 repair logic (§7). Question 9c ("Is a partial excerpt ever acceptable?") is particularly valuable — it tests the owner's self-containment absolutism, which is an area where his intuition needs calibration.

**Section 10 — Study Workflow (4 questions: 10a, 10b, 10c, 10d)**

A user-model discovery section. Question 10d about original text vs. cleaned-up summary is critical — it determines whether KR is a reference tool or a learning tool, with implications for the `primary_text` field fidelity. The other questions (10a, 10b, 10c) are synthesis/UI concerns.

### 1.3 SPEC Rules with Zero Coverage

The following SPEC domain rules are not tested by any questionnaire section. Each was verified by grep against the questionnaire template — zero matches found.

**DP-2 (Question + Answer)** — SPEC line 1258. A question and its answer must belong in the same teaching unit, including formal فإن قيل / قلنا dialogue. The campaign has 300 excerpts from `ext_46_qa` (Q&A format). No questionnaire question shows the owner a Q&A excerpt and asks whether the question and answer should stay together.

**DP-3 (Rule + Exception)** — SPEC line 1260. A rule statement and its exception (إلا إذا ...) must be in the same teaching unit. The campaign has 12 `condition_exception` primary-function excerpts in taysir and 7 in ext_39_masala. No question asks the owner whether a rule without its exception is misleading.

**DP-6 (Condition + Result)** — SPEC line 1266. A conditional statement is one semantic unit. No question tests this pattern.

**LA-1 through LA-4 (Multi-layer Attribution)** — SPEC lines 1284–1290. This is the **most dangerous gap**. The SPEC devotes an entire subsection (§6.2, lines 1272–1302) to the risk that a sharh author's commentary gets attributed to the matn author. The owner's own feedback explicitly raised attribution as a corruption concern ("I TRY TO UNDERSTAND ONE EXCERPT BASED ON ANOTHER MISMATCHED EXCERPT"). Yet no questionnaire question shows the owner a sharh excerpt and asks "Who do you think wrote this?" This is a T-2 (Attribution Error) with direct epistemic consequences.

**IR-2 (Scholar Epithet Resolution)** — SPEC line 1345. "الإمام" means Ahmad ibn Hanbal in Hanbali texts but al-Shafi'i in Shafi'i texts. The questionnaire never asks the owner about ambiguous scholarly references. This matters because the owner is a student who may not yet know these conventions.

**QM-1 through QM-3 (Masala Format)** — SPEC lines 1385–1389. 197 excerpts in `ext_39_masala` use masala-block structure. No question shows the owner a masala-formatted excerpt and asks whether each مسألة feels like a complete unit.

**EV-3 (Consensus References)** — SPEC line 1331. 20 `evidence_ijma` excerpts in taysir. No question asks the owner how consensus claims should be presented.

**C-SC-1 (Term Resolution)** — SPEC line 543. No question asks whether the owner recognizes the technical terms in an excerpt. This is particularly important because the owner is a student — his term-recognition threshold may differ from the SPEC's "general familiarity" assumption.

### 1.4 Scholarly Use Cases Not Tested

Beyond individual SPEC rules, entire scholarly text types and conventions are absent:

**Usul al-fiqh methodology.** Usul texts argue about how to derive rulings, not about specific rulings. An usul excerpt might be a multi-step logical argument about whether the general (عام) can be restricted by the specific (خاص), citing Quranic examples as methodology illustrations rather than as evidence for a ruling. The excerpting needs are fundamentally different from fiqh — an usul teaching unit is often an extended logical chain where cutting at any point destroys the argument. The questionnaire assumes a fiqh-centric model (ruling + evidence + khilaf) throughout. Notably, the `ext_46_qa` campaign package contains usul al-nahw definitions (السماع, الإجماع, القياس as grammatical methodology) — proof that usul-type content exists in the campaign but the questionnaire doesn't test it.

**Hadith grading and takhrij apparatus.** Question 7c asks only "do you want the full chain (isnad) or just the content (matn)?" — a binary that misses the real complexity. In hadith commentary texts like Taysir al-Allam, the muhaqiq (editor) adds footnotes grading hadith, listing collections, and cross-referencing narrators. The SPEC handles this at EV-2 (lines 1322–1330) with specific extraction rules, but the owner has never been asked whether he wants this information. The campaign contains 160 `evidence_hadith` excerpts and 49 `editorial_note` excerpts — the intersection (editor notes about hadith grading) is a real pattern that the questionnaire ignores.

**Tafsir (Quranic exegesis).** Tafsir texts have a distinctive structure: Quranic verse → linguistic analysis → reasons for revelation (أسباب النزول) → legal rulings derived → connections to other verses. The owner's 2,519 Shamela books almost certainly include tafsir works. No questionnaire question addresses tafsir-specific excerpting.

**Multi-layer sharh/hashiyah attribution.** The questionnaire asks about hashiyah only in Section 8c ("go deeper — commentary on a commentary?"), which is a navigation question. The real excerpting question is: when reading a hashiyah excerpt, can you tell which words are the muhasshi's (super-commentator's), which are the sharih's (commentator's), and which are the original author's? This is the LA-1 through LA-4 concern.

**Editor (muhaqiq) apparatus.** Modern Shamela editions include editor footnotes, text variant notes ("كذا في الأصل"), and cross-references. The SPEC classifies these as `editorial_note`. No question asks the owner whether editor notes should be included in excerpts, separated, or filtered out.

### 1.5 Attention Budget Analysis

Of 30 interaction points: 5 are downstream concerns (Sections 3 and 8) that calibrate taxonomy/synthesis, not excerpting — consuming ~17% of the owner's attention without excerpting engine value. 7 directly map to SPEC excerpting rules (DR-1, DP-4/DR-2, DR-3). 18 are general calibration questions (granularity, self-containment, workflow). Meanwhile, at least 9 critical SPEC rules have zero coverage, and 5 major scholarly use cases are untested.

---

## Phase 2: Arabic Representativeness

### 2.1 The No-Examples Problem

The questionnaire contains **zero Arabic text**. Every one of the 10 sections delegates example selection to the team with instructions like "Pick an excerpt with X" from the campaign JSONL. This creates three cascading problems:

**Inconsistency risk.** Different team members interpreting "pick a khilaf passage with multiple madhab positions" will select different excerpts, and the selected excerpt shapes the owner's answer. If someone picks the excellent multi-madhab discussion about نفقة البائن (alimony for irrevocably divorced women) — which has three cleanly separated positions — the owner will likely say "yes, I want all positions together." If someone picks a passage where khilaf is interleaved with evidence and counter-evidence in a single sentence (like the scholarly reality check's Test 2), the owner might react very differently. The example IS the answer.

**Anchoring bias.** Showing the owner one example per category anchors his judgment to that specific example. If the "long excerpt" is a well-structured 300-word khilaf discussion, "long" will feel useful. If it's a 300-word rambling editorial note, "long" will feel bloated. No mechanism for the owner to encounter the natural variety within each category.

**Unpresentability.** Section 1 asks the team to show short (<200 words), medium (200–500), and long (>500 words) excerpts. But the campaign data's actual distribution is severely skewed (see 2.2 below). The team literally cannot find a representative "long" excerpt.

### 2.2 Campaign Data Length Distribution

Verified by tool execution against `integration_tests/campaign_20260331/taysir/excerpts.jsonl`:

| Word count range | Count | Percentage |
|---|---|---|
| 0–50 | 578 | 45.1% |
| 51–100 | 405 | 31.6% |
| 101–150 | 158 | 12.3% |
| 151–200 | 75 | 5.8% |
| 201–300 | 51 | 4.0% |
| 301–500 | 15 | 1.2% |
| 500+ | **1** | 0.08% |

Maximum: 659 words (`exc_src_test0001_div_src_test0001_7_043_0_3`).

76.5% of excerpts are under 100 words. Only 1 excerpt exceeds 500 words. Section 1's "compare short/medium/long" comparison is structurally biased toward validating fine-grained excerpting because long excerpts barely exist in the campaign output.

### 2.3 Genre Coverage

Campaign packages and their genres:

| Package | Genre | Excerpts | Source ID |
|---|---|---|---|
| taysir | Hadith commentary (fiqh-flavored) | 1,283 | src_test0001 |
| ibn_aqil_v1 | Nahw verse-commentary | 241 | src_test0001 |
| ibn_aqil_v3 | Nahw verse-commentary | 282 | src_test0001 |
| ext_39_masala | Masala-format fiqh | 197 | src_test0001 |
| ext_46_qa | Q&A-format (usul al-nahw) | 300 | src_test0001 |

ALL packages share `source_id=src_test0001` — cross-book comparison is impossible within campaign data. Section 3's requirement for cross-book same-topic comparison cannot be answered.

Missing genre coverage: no usul al-fiqh text, no tafsir, no pure hadith collection (Sahih al-Bukhari type — as opposed to hadith commentary), no aqidah text, no rijal/narrator biography, no fatwa collection.

The "hadith excerpt" for Section 7 would come from a hadith *commentary*, not a hadith *collection*. In a hadith collection, the excerpt IS the hadith with its isnad; in a commentary, the hadith is the frame for fiqh discussion. The owner's answer about isnad handling would be anchored to commentary text, not the actual hadith collection format.

### 2.4 Section-Level Example Availability

Verified by tool execution:

**Section 2 (Self-Containment):** 387 excerpts with `context_hint`, 39 with backward references (كما تقدم etc.). Sufficient.

**Section 3 (Comparison):** Requires excerpts from different books on the same topic. **IMPOSSIBLE** with current data — all one source.

**Section 4 (Definitions):** 10 definition pairs with both لغة and شرعا markers. Sufficient for this specific type, though only 9.5% of all definitions.

**Section 5 (Evidence):** 210 rule_statements with evidence as secondary function. Sufficient.

**Section 6 (Khilaf):** 93 excerpts mentioning 2+ madhabs; 13 with `primary_function=refutation`. Sufficient.

**Section 7 (Genre):** Campaign can supply fiqh and nahw excerpts. "Hadith" would be from commentary (taysir), not a collection.

**Section 9 (Partial):** 387 PARTIAL excerpts; 14 DEPENDENT. One excellent DEPENDENT excerpt: "واختلف العلماء في حقيقة اليد التي تقطع على أقوال: وأصحها، ما ذهب إليه الجمهور،" — trails off without completing the discussion.

### 2.5 The Split/Compare Presentation Gap

Sections 4 and 6 require showing the same content first as-is, then split. This is a powerful pedagogical technique, but the questionnaire provides no guidance on HOW to create the split version. The team would need to manually construct a split alternative, which requires understanding the SPEC's domain rules. If the person constructing the split doesn't understand DR-1 or DR-3, the split version might be scholastically invalid, and the owner would be evaluating a strawman.

### 2.6 What IS Scholastically Authentic

The Arabic excerpts that do exist in the campaign are genuinely representative of their specific genres. Three verified examples:

The khilaf excerpt (`exc_..._0_24`) about نفقة البائن is a textbook اختلاف العلماء structure: three positions (Ahmad, Hanafis, Malik/al-Shafi'i), each with named proponents and cited evidence.

The refutation excerpt (`exc_..._0_2`) about الرفع من الركوع follows the classic pattern: claim → "ولكن هذا قياس فاسد" → counter-evidence. Satisfies DP-1 and is self-contained.

The DEPENDENT excerpt about اليد التي تقطع is a genuinely incomplete fragment that would make the owner feel the frustration Section 9 tries to test.

The issue is coverage breadth, not quality of what exists.

---

## Phase 3: Definition-Splitting and Evidence-Handling

### 3.1 DR-1 (Definition Pair Splitting) — Cross-Genre Verification

**Taysir definition pattern breakdown** (verified against 105 definition excerpts):

| Pattern | Count | Percentage |
|---|---|---|
| Both لغة and شرعا (definition pairs) | 10 | 9.5% |
| غريب الحديث (vocabulary explanations) | 36 | 34.3% |
| Plain definitions (no markers) | 41 | 39.0% |
| شرعا/اصطلاحا only | 12 | 11.4% |
| لغة only | 6 | 5.7% |

Section 4 focuses exclusively on the لغة/شرعا pair pattern, which is the least common type. The dominant types (غريب and plain definitions) are untested.

**Nahw definitions** use a completely different structure. Verified from ibn_aqil_v1 excerpts: nahw definitions use genus-differentia reasoning. Examples:
- "الكلام المصطلح عليه عند النحاة: عبارة عن اللفظ المفيد فائدة يحسن السكوت عليه" (Speech, as the grammarians define it: an utterance that conveys a meaning upon which silence is appropriate)
- "الكلمة: هي اللفظ الموضوع لمعنى مفرد" (A word: it is an utterance assigned to a singular meaning)

No لغة/شرعا binary exists. The "definition" IS the rule in nahw. Splitting it would split the teaching unit itself.

**Usul al-nahw definitions** from ext_46_qa are methodological concepts: السماع (reported speech), الإجماع (consensus of grammarians from Basra and Kufa), القياس (analogy in grammar). These are technical inventions with no pre-existing linguistic meaning — the لغة/شرعا split doesn't apply.

**Gemini adversarial review findings on DR-1** (from `gemini_adversarial_DR_review.md`, lines 22–31):

Gemini found DR-1 "mostly safe but not universally safe" and identified critical failure modes:
1. **Self-containment asymmetry:** The linguistic unit is usually self-contained, but the legal unit often begins with "وفي الشرع" or "واصطلاحاً" — conjunctions that grammatically reference the preceding linguistic definition.
2. **Semantic interdependence:** In many fiqh definitions, the legal definition explicitly relies on the linguistic one. Pattern: "هو المعنى اللغوي بزيادة كذا" (It is the linguistic meaning with the addition of condition X). If split, the legal definition becomes semantically hollow.
3. **Relationship statements:** Statements like "والعلاقة بينهما الجزئية" (the relationship between them is...) get placed in the legal unit under DR-1, but removing the linguistic definition text forces the reader to rely entirely on metadata cross-reference to understand the relationship.
4. **Aqidah danger:** In theology, the relationship between linguistic and technical meanings of terms (إيمان, كفر) is often the core of the sectarian debate. Splitting them neutralizes the theological argument.

**The questionnaire does NOT expose any of these findings.** Verified by grep: zero matches for "Gemini," "reject," "multi-leaf," "tagging," "alternative," "orphan," "grammatical," "fractur," "وفي الشرع" (as a splitting concern), or "فأما" (as a splitting concern) in the questionnaire template.

### 3.2 DR-2 (Evidence-Type Splitting) — Section 5 Assessment

**Evidence distribution in campaign data** (verified):
- Evidence as primary function (standalone citations): 259 excerpts
- Evidence as secondary function (woven into rulings/opinions/commentary): 358 excerpts
- **Ratio: interleaved evidence is 1.4x more common than standalone**

Section 5's binary framing ("ruling alone vs. ruling+evidence together") misses the majority case.

**Evidence type breakdown** in taysir (primary function only):
- evidence_hadith: 160
- evidence_rational: 71
- evidence_ijma: 20
- evidence_quran: 7
- evidence_qiyas: 1

Additionally: 144 rule_statements have evidence as a secondary function, and 59 evidence excerpts have rule/opinion as a secondary function.

**Gemini adversarial review findings on DR-2** (from `gemini_adversarial_DR_review.md`, lines 11–19):

Gemini analyzed the فأما orphaning problem: "فأما الكتاب فنحو {الطلاقُ مَرتَانِ} وغيرها من الآيات" — splitting this as standalone evidence produces a fragment starting with فأما, a conditional detailing particle (حرف شرط وتفصيل) that "strictly necessitates a preceding general statement (المُجْمَل)."

Gemini's verdict: "Computationally and semantically, yes, the metadata compensates... Linguistically and pedagogically, NO. Classical Arabic texts are highly cohesive. Presenting a student with a fractured sentence starting with فأما as a 'self-contained teaching unit' violates the natural flow and integrity of the language."

Gemini also noted: the ~10 word threshold for evidence substantiveness is "far too low for rational arguments, which require premises and conclusions to remain syntactically intact." And: "evidence types like Qiyas cannot be cleanly separated because the analogy itself constitutes the argument for the ruling."

**The questionnaire's Section 5 Translation note references DR-2 "reconsidering" — directly contradicting the 3/5 reviewer rejection.** DR-2 does not exist in the SPEC. It is a proposed rule from `scholarly_reality_check_intra_excerpt.md` that was deferred after cross-provider review.

### 3.3 DR-3 (Khilaf Preservation) — Section 6 Assessment

Section 6 is the best-designed section for its target domain rule. Three questions directly calibrate DR-3: all positions together (6a), individual positions separately (6b), attribution importance (6c).

**Gemini's finding on the ~800-word threshold** (lines 56–66): "The ~800-word threshold is entirely arbitrary and lacks scholarly basis." The viability of splitting depends on discursive structure (are positions cross-referencing each other?), not length. A 1,000-word passage with intertwined dialectic cannot be split; a 300-word passage with structurally independent positions can. The questionnaire could test this by showing two structurally different khilaf passages.

### 3.4 Cross-Genre Evidence Handling

The questionnaire treats evidence as "supporting material for a ruling" throughout. This is the fiqh model. Evidence works completely differently in other genres:

**Nahw:** The شاهد (evidence verse, typically poetry or Quran) is the PRIMARY TEXT being analyzed. The rule is derived FROM it, not supported BY it. Verified in ibn_aqil excerpt `exc_..._0_18`: the Alfiyya verse "والأمر إن لم يك للنون محل / فيه هو اسم نحو صه وحيهل" is the teaching frame, and the commentary explains what the verse means. Splitting verse from commentary removes the teaching's foundation. Gemini confirmed (line 70): "Splitting linguistic rules from their evidence (الشواهد) is disastrous. The entire pedagogical value of the excerpt lies in the application of the rule to the specific poetic verse or Quranic segment."

Web research confirmed the scholarly role of شواهد: "الشاهد عند النحويين هو الدليل الذي يعتمد عليه في الأخذ بقاعدة ما, ورفض أخري" (the shahid for grammarians is the evidence relied upon to establish or reject a rule). Another source: Sibawayh himself "only used شواهد for rare or disputed phenomena, not for self-evident rules like subject case-marking — the شاهد exists specifically to establish what would otherwise be contested." This is FOUNDATIONAL EVIDENCE, not an "example sentence."

**Hadith commentary (Taysir al-Allam):** The hadith IS the frame for discussion. The المعنى الإجمالي (overall meaning) explains the hadith; the ما يُستفاد (derived benefits) extracts rulings. Evidence and ruling are reversed from the fiqh model — the evidence (hadith) comes first, rulings are derived from it. Section 5's framing ("do you want the ruling first, then the evidence?") assumes the fiqh ordering.

**Usul al-fiqh:** Evidence is often a logical argument chain, not a textual citation. Gemini noted DR-2's substantive threshold (~10 words) is "far too low for rational arguments."

### 3.5 The Missing Alternative: Multi-Leaf Tagging

The most significant omission from Sections 4–5 is that the owner is never presented with the **multi-leaf tagging alternative** that Gemini recommended (lines 78–87 of the adversarial review): keep the excerpt physically intact, but tag it to multiple taxonomy leaves simultaneously. The owner would see the full passage under "تعريف الطلاق لغة" AND under "تعريف الطلاق شرعا" — same text, two navigation paths.

The owner's first feedback comment reveals his real desire is per-leaf access to content, not necessarily physical splitting: "I open the leaf in the taxonomy tree." Multi-leaf tagging achieves this without grammatical orphaning, semantic hollowing, or self-containment violations. But the questionnaire frames every choice as "together vs. separate" — a false binary.

Gemini's recommendation: "REJECTING DR-1 and DR-2, and adopting the alternative: Keep medium excerpts + Multi-leaf tagging... By keeping the excerpt intact and tagging it to multiple taxonomy leaves simultaneously, you achieve the precise granularity required for the knowledge graph without mutilating the cohesive source text."

---

## Phase 4: Misleading Interactions and Owner Intuition

### 4.1 Specifically Misleading Interactions

Four questionnaire interactions where the question framing leads toward scholastically problematic answers:

**Section 7b — "For grammar (nahw), do you want the example sentence (shaahid) inside the excerpt or separate?"**

The most misleading interaction. Calls the شاهد an "example sentence," implying it is an optional illustration. The scholarly reality is that the شاهد is foundational evidence (دليل) for a grammatical rule — the verse or line IS the authority from which the rule was derived. Presenting the choice as "inside the excerpt or separate?" implies separation is reasonable, when in fact separating a grammatical rule from its شاهد is like separating a legal ruling from the law it is based on. The owner, who hasn't studied nahw, would answer based on the "example sentence" framing.

**Section 4b — "If they were separate excerpts, would you want to see them linked? Or is separate fine?"**

Presents a false binary: physically split + linked, or physically split + unlinked. Never offers the third option (multi-leaf tagging). By framing the question as "linked or unlinked," the questionnaire teaches the owner that splitting is the default and the only question is how to manage the consequences.

**Section 5b — "Or would you prefer to see the ruling first, and tap to see the evidence separately?"**

Conflates excerpt boundaries with display/navigation design. "Tap to see the evidence" is a UI interaction (synthesis/frontend concern). But the Translation note says this answer "determines whether evidence stays within the excerpt or becomes a linked reference." The owner is being asked a UI question; the team will interpret it as an excerpting architecture decision. The owner might say "yes, I'd love to tap to see evidence" — meaning progressive disclosure in the UI — and the team interprets this as permission to physically split evidence from rulings during excerpting.

**Section 1c — "If you had to choose: would you rather excerpts are too short (missing context) or too long (covering multiple topics)?"**

A forced-choice between two bad outcomes with no "neither" option. Implicitly teaches the owner that there's an inherent tradeoff between granularity and self-containment. But the SPEC's standard (§3) explicitly aims for BOTH: fine-grained AND self-contained, with `context_hint` bridging gaps. The forced choice could make the owner accept partial excerpts he would otherwise reject.

### 4.2 Owner Intuition — Strongest Areas

Based on analysis of the two feedback comments:

**Taxonomy-driven navigation thinking.** The owner instinctively thinks in terms of taxonomy leaves and what he'll see when he opens them. His feedback: "I open the granulated leaf and get exactly what I want: a direct overview of what all that was ever said on the general ruling. I can directly compare the opinion (not yet the proofs) of every scholar that has ever spoken about this topic." Sections 8 and 10 will leverage this strength.

**Self-containment violations.** The owner immediately recognized when an excerpt starts with a "cut-off-bit" and articulated the principle: "Excerpts should be self contained, which includes answering all questions and confusions that may arise during the owner's usage of the library." He also demonstrates sensitivity to over-granularity: the sentence that could stand alone but shouldn't because it's "closely related" to the previous one. Sections 2 and 9 will get strong answers.

**Cross-excerpt corruption awareness.** The owner independently discovered the most dangerous failure mode: reading excerpt A, wanting context, navigating to the taxonomy leaf, and accidentally reading excerpt B from a different source under the same leaf. He called this "CORRUPTION in my knowledge: I TRY TO UNDERSTAND ONE EXCERPT BASED ON ANOTHER MISMATCHED EXCERPT!" This is more sophisticated than most questionnaire questions.

### 4.3 Owner Intuition — Weakest Areas

**Classical Arabic grammar and conjunctions.** The owner proposed splitting "وفي الشرع: حَل عقدة التزويج" from the preceding لغة definition without recognizing that وفي الشرع grammatically requires the preceding context. He also proposed "فأما الكتاب فنحو {الطلاقُ مَرتَانِ}" as standalone evidence without recognizing فأما is a detailing particle demanding a preceding general statement. Sections 4 and 5 never show the owner the result of splitting — the orphaned Arabic fragments that begin mid-thought.

**Genre transfer.** Both feedback comments reason from fiqh text. The owner's principles ("per evidence type," "per ayah") are calibrated for fiqh's ruling→evidence→khilaf structure. He has no demonstrated intuition about nahw (where the شاهد IS the primary text), usul (where evidence is logical argument chains), hadith science (where isnad evaluation determines everything), or aqidah (where linguistic vs. technical meaning tension IS the theological debate). Section 7 uses fiqh-centric framing that would not surface genre blindspots.

**Excerpting vs. taxonomy confusion.** The owner's first feedback: "تعريف الطلاق لغة & تعريف الطلاق شرعا should be different leafs in the taxonomy tree. But if it wasn't, then that would justify this excerpt being only one excerpt." This reveals a logical dependency: excerpt boundaries should follow taxonomy leaf boundaries. But excerpting happens BEFORE taxonomy — the excerpting engine doesn't know the taxonomy tree (by design, to avoid bias). The questionnaire doesn't surface this confusion.

**Over-granularity risk tolerance.** The owner's second feedback pushes toward extreme granularity: "Even better: X من الكتاب > آية; per ayah." But many Quranic citations in fiqh are allusive (paraphrased, partial, cited by opening words only) — they can't be cleanly isolated as per-ayah units. The owner's vision assumes citations are clean block quotes, when in practice they're woven into argumentative prose.

### 4.4 Questions That Confirm vs. Challenge the Owner

**Reconfirming existing intuition (less valuable):**
- Section 4a ("definitions together, does that feel complete?") — owner already answered NO in feedback 1
- Section 5a ("always want evidence right there?") — owner already answered "separate per type" in feedback 2
- Section 1c ("too short or too long?") — owner already answered "fine-grained" in feedback 2

**Challenging intuition (more valuable):**
- Section 9c ("Is a partial excerpt ever acceptable?") — genuinely tests self-containment absolutism
- Section 10d ("original text vs cleaned-up summary?") — could reveal new study goal information
- Section 2c ("'as mentioned earlier' without context frustrating?") — tests implicit reference tolerance not yet commented on

---

## Phase 5: Synthesis and Recommendations

### 5.1 Missing Use Cases — Complete List

**Scholarly text types not tested:**
1. Usul al-fiqh logical argumentation (where excerpts are argument chains, not ruling→evidence pairs)
2. Tafsir verse-exegesis structure (Quran→analysis→asbab al-nuzul→ruling)
3. Aqidah theological propositions (where linguistic vs. technical meaning IS the debate)
4. Hadith collection format (isnad-centric, as opposed to hadith commentary)
5. Fatwa compilation format
6. Rijal/narrator biography format

**SPEC domain rules with zero coverage:**
1. DP-2 (Question + Answer grouping)
2. DP-3 (Rule + Exception grouping)
3. DP-6 (Condition + Result grouping)
4. LA-1 through LA-4 (Multi-layer attribution) — HIGHEST PRIORITY
5. IR-2 (Scholar epithet resolution)
6. QM-1 through QM-3 (Masala format)
7. EV-3 (Consensus references)
8. C-SC-1 (Term resolution)

**Cross-cutting concerns not tested:**
1. Grammatical orphaning consequences of physical splitting
2. Multi-leaf tagging as an alternative to physical splitting
3. Editor/muhaqiq apparatus handling (editorial_note excerpts)
4. Hadith grading and takhrij metadata in editor footnotes
5. The excerpting-before-taxonomy sequencing implication
6. Over-granularity consequences (showing the owner what a 15-word micro-excerpt looks like)

### 5.2 Specific Recommendations

**Recommendation 1: Pre-select and embed Arabic examples directly in the questionnaire.**

Every section should contain the actual Arabic text the owner will read, not a "pick an excerpt" instruction. This eliminates inconsistency (different selectors pick different examples), prevents anchoring bias, and ensures representative coverage. The team should collaboratively select examples BEFORE the questionnaire goes to the owner, using campaign data plus manually constructed examples for patterns that don't exist in the campaign (cross-book comparison, long excerpts, usul text). Each example should be presented as rendered Arabic text, not JSON.

**Recommendation 2: Add a multi-layer attribution section.**

Create a new section (between current Sections 6 and 7) showing the owner a sharh excerpt and asking: "Who do you think wrote this? Can you tell which part is the original author and which part is the commentator? When you read this, whose opinion do you think you're learning?" This tests LA-1 through LA-4 and reveals whether the owner needs explicit attribution markers or can parse multi-layer text. This is the **highest-priority addition** because wrong attribution is a T-2 knowledge integrity violation.

**Recommendation 3: Replace Sections 3 (Comparison) and 8 (Navigation) with excerpting-relevant sections.**

These sections test synthesis/taxonomy/UI concerns, not excerpting. Replace them with:
- A **Q&A/masala format section** testing DP-2, QM-1–QM-3 with real examples from `ext_39_masala` and `ext_46_qa` campaign packages
- A **rule+exception section** testing DP-3, DP-6 with fiqh examples where rules and their exceptions are separated

**Recommendation 4: Show the consequences of splitting, not just the choice.**

For Sections 4 and 5, show the owner THREE versions of each excerpt:
- (a) The combined version as-is
- (b) The split version showing the actual orphaned Arabic fragments (including the dangling وفي الشرع and فأما)
- (c) The multi-leaf tagging version (same intact text, shown appearing under two different taxonomy leaves)

Let the owner react to all three rather than choosing between an abstract "together vs. separate."

**Recommendation 5: Fix the three inaccurate Translation notes.**

- Section 1 Translation: references a "minimum excerpt length threshold" that doesn't exist in the SPEC. Teaching unit size is determined by LLM grouping, not a configurable threshold. Fix: "Answer (a) informs whether the LLM's grouping prompt should be calibrated to prefer larger or smaller units. Answer (b) informs whether topic-splitting sensitivity needs adjustment. Answer (c) sets the bias direction for edge cases in the Phase 2b prompt."
- Section 5 Translation: references DR-2 "reconsidering" — contradicts the 3/5 rejection from cross-provider review. Fix: "Answers confirm or challenge the decision to defer DR-2. If the owner strongly prefers separate evidence, this would be grounds to re-open the DR-2 discussion with the full review team."
- Section 3 Translation: references excerpt normalization for comparability — a synthesis engine concern. Fix: acknowledge this section feeds the synthesis engine, not excerpting.

**Recommendation 6: Add a genre-specific evidence section that replaces Section 7b's misleading framing.**

Instead of "do you want the example sentence (shaahid) inside the excerpt or separate?":
- Show the owner a real nahw excerpt from ibn_aqil with the Alfiyya verse and its commentary, and ask: "This verse states a grammar rule, and the text after it explains the rule. Should these be together as one excerpt, or can the verse stand alone?"
- Then show a hadith commentary excerpt with the المعنى الإجمالي pattern and ask: "This explains a hadith. Should the explanation stay with the hadith text, or can it be separate?"

This tests the same underlying question without the misleading "example sentence" framing.

**Recommendation 7: Add 2–3 interactions that challenge the owner's demonstrated weaknesses.**

- Show the owner an over-granular split (a 15-word fragment that answers one micro-question) and ask: "Is this useful on its own, or would you need more context?"
- Show a passage where two topics share a grammatical conjunction (like the scholarly reality check's Test 2, where two fiqh discussions are joined by و in the same sentence) and ask: "Where would you split this?"
- Show the actual result of splitting "وفي الشرع: حَل عقدة التزويج" from its preceding لغة definition (the orphaned Arabic with dangling conjunction) and ask: "How does this read?"

These interactions surface the over-granularity tendency and the grammatical binding blindspot rather than reinforcing them.

**Recommendation 8: Explicitly address the excerpting-taxonomy sequencing.**

Add one interaction that explains: "The excerpting engine runs BEFORE the taxonomy engine — it doesn't know what leaves exist in the taxonomy tree. Given that, should excerpts be designed to fit specific taxonomy leaves, or should they be natural scholarly units that the taxonomy engine then classifies?" This surfaces the owner's confusion between excerpt structure and taxonomy structure.

### 5.3 Process Recommendation

The revised questionnaire should go through the **cross-provider review team** before the owner sees it. The team should validate:
1. Arabic examples are scholastically representative
2. Translation notes map to actual SPEC parameters
3. No interaction teaches a wrong mental model
4. All SPEC domain rules have coverage
5. The multi-leaf tagging alternative is fairly presented

---

## Appendix A: SPEC Rule Coverage Map

Complete mapping of all named SPEC domain rules to questionnaire coverage status.

### Self-Containment Criteria (§3.2)

| Rule | Description | Questionnaire Coverage |
|---|---|---|
| C-SC-1 | Term Resolution | **NOT COVERED** — no question about technical term recognition |
| C-SC-2 | Reference Resolution | Section 2c (backward references), Section 9 (context hints) |
| C-SC-3 | Evidence Completeness | Section 5c (well-known hadith) — partial |
| C-SC-4 | Argument Completeness | Section 1 (granularity), Section 6 (khilaf), Section 9 (partial) |
| C-SC-5 | Dialogue Completeness | Section 6 (scholarly debate) — partial |

### Decontextualization Prevention (§6.1)

| Rule | Description | Questionnaire Coverage |
|---|---|---|
| DP-1 | Position + Refutation | Section 6 — partial (asks about "positions" but not refutation pairs specifically) |
| DP-2 | Question + Answer | **NOT COVERED** |
| DP-3 | Rule + Exception | **NOT COVERED** |
| DP-4 | Evidence + Ruling | Section 5 — covered |
| DP-5 | Counter-argument + Original | Section 6 — partial |
| DP-6 | Condition + Result | **NOT COVERED** |

### Multi-Layer Attribution (§6.2)

| Rule | Description | Questionnaire Coverage |
|---|---|---|
| LA-1 | Single-layer dominance | **NOT COVERED** |
| LA-2 | Mixed-layer default | **NOT COVERED** |
| LA-3 | Attribution uncertainty | **NOT COVERED** |
| LA-4 | Pure matn units | **NOT COVERED** |

### Evidence Handling (§6.3)

| Rule | Description | Questionnaire Coverage |
|---|---|---|
| EV-1 | Quran references | Section 5 — partial |
| EV-2 | Hadith references | Section 7c — shallow (binary only) |
| EV-3 | Consensus references | **NOT COVERED** |

### Implicit Reference Resolution (§6.4)

| Rule | Description | Questionnaire Coverage |
|---|---|---|
| IR-1 | Intra-source cross-reference | Section 2c, Section 9 |
| IR-2 | Scholar epithet resolution | **NOT COVERED** |
| IR-3 | Unresolvable references | Section 9 — partial |

### Verse-Commentary Handling (§6.5)

| Rule | Description | Questionnaire Coverage |
|---|---|---|
| VC-1 | Verse + commentary unity | Section 7b — but with misleading "example sentence" framing |
| VC-2 | Standalone verse validity | **NOT COVERED** |
| VC-3 | Multi-verse grouping | **NOT COVERED** |

### Q&A and Masala (§6.6)

| Rule | Description | Questionnaire Coverage |
|---|---|---|
| QM-1 | Q&A pairs | **NOT COVERED** |
| QM-2 | Masala blocks | **NOT COVERED** |
| QM-3 | Cross-masala references | **NOT COVERED** |

### Domain Rules (proposed, not in SPEC)

| Rule | Status | Questionnaire Coverage |
|---|---|---|
| DR-1 | ADOPTED conditional | Section 4 — well-covered for fiqh لغة/شرعا pairs only |
| DR-2 | REJECTED 3/5 | Section 5 — Translation note incorrectly references reconsidering |
| DR-3 | ADOPTED structural | Section 6 — well-covered |

---

## Appendix B: Campaign Data Evidence

All numbers verified by tool execution against the campaign JSONL files.

### Primary Function Distribution — Taysir (1,283 excerpts)

| Function | Count |
|---|---|
| rule_statement | 556 |
| opinion_statement | 228 |
| evidence_hadith | 160 |
| definition | 105 |
| evidence_rational | 71 |
| editorial_note | 49 |
| narration | 49 |
| evidence_ijma | 20 |
| refutation | 13 |
| condition_exception | 12 |
| structural_transition | 8 |
| evidence_quran | 7 |
| cross_reference | 3 |
| evidence_qiyas | 1 |
| example | 1 |

### Self-Containment Distribution — Taysir

| Level | Count |
|---|---|
| FULL | 882 |
| PARTIAL | 387 |
| DEPENDENT | 14 |

### Metadata Presence — Taysir

| Field | Excerpts with data |
|---|---|
| context_hint | 387 |
| cross_references | 114 |
| evidence_refs | 165 |
| opinion/khilaf (primary or secondary) | 330 |

### Primary Function Distribution — Other Packages

**ext_39_masala (197 excerpts):** rule_statement: 154, evidence_hadith: 25, condition_exception: 7, structural_transition: 4, editorial_note: 3, evidence_quran: 1, refutation: 1, opinion_statement: 1, evidence_rational: 1

**ext_46_qa (300 excerpts):** rule_statement: 88, opinion_statement: 71, definition: 57, example: 37, refutation: 12, narration: 10, structural_transition: 9, editorial_note: 8, evidence_rational: 3, cross_reference: 3, evidence_hadith: 1, evidence_ijma: 1

**ibn_aqil_v1 (241 excerpts):** rule_statement: 147, definition: 37, opinion_statement: 29, condition_exception: 11, editorial_note: 8, structural_transition: 5, refutation: 2, narration: 1, example: 1

### Evidence Interleaving Measurement — Taysir

- Evidence as primary function (standalone citations): 259 excerpts
- Evidence as secondary function (woven into other teachings): 358 excerpts
- Ratio interleaved/standalone: 1.4x

---

## Appendix C: Arabic Examples for Reference

### C.1 — The Owner's Rejected Definition (Feedback 1)

Excerpt `exc_src_test0001_div_src_test0001_1_002_pre_0_0`:

```
‌‌كتاب الطلاق
الطلاق: في اللغة: حل الوثاق. مشتق من الإطلاق، وهو الترك والإرسال.
وفي الشرع: حَل عقدة التزويج، والتعريف الشرعي فَرْد من معناه اللغوي العام. قال إمام. الحرمين: هو لفظ جاهلي ورد الشرع بتقريره.
```

Owner's verdict: REJECT. Wanted two separate excerpts (تعريف الطلاق لغة and تعريف الطلاق شرعا) but with the second being self-contained and the third sentence ("والتعريف الشرعي فَرْد من معناه اللغوي العام...") grouped with the legal definition, NOT as its own excerpt.

### C.2 — The Owner's Rejected Evidence Block (Feedback 2)

Excerpt `exc_src_test0001_div_src_test0001_1_002_pre_0_1`:

```
وحكمه ثابت في الكتاب، والسنة، والإجماع، والقياس الصحيح.
فأما الكتاب فنحو {الطلاقُ مَرتَانِ} وغيرها من الآيات.
وأما السنة، فقوله صلى الله عليه وسلم: {أبغض الحلال إلى الله الطلاق} وغيره من فعله وتقريره صلى الله عليه وسلم.
والأمة مجمعة عليه، والقياس يقتضيه.
فإذا كان يتم النكاح بالعقد لمصالحه وأغراضه فإنه يفسخ ذلك العقد بالطلاق، للمقاصد الصحيحة.
```

Owner's verdict: REJECT — too broad. Wanted per-evidence-type excerpts and even per-ayah granularity.

### C.3 — A Well-Structured Khilaf Passage (Good Example for Section 6)

Excerpt `exc_src_test0001_div_src_test0001_1_002_pre_0_24` (194 words):

```
اختلاف العلماء:
اختلف العلماء هل للبائن نفقة وسكنى، زمن العدة، أو لا؟
فذهب الإمام أحمد: إلى أنه ليس لها نفقة، ولا سكنى، وهو قول علي، وابن عباس، وجابر.
وبه قال عطاء، وطاوس، والحسن، وعكرمة، وإسحاق، وأبو ثور وداود، مستدلين بحديث الباب.
وذهب الحنفية إلى أن لها النفقة والسكنى، وهو مروى عن عمر، وابن مسعود وقال به ابن أبى ليلى، وسفيان الثوري، مستدلين بما روى عن عمر: (لا ندع كتاب ربنا لقول امرأة) .
وذهب مالك، والشافعي، إلى أن لها السكنى دون النفقة، وهو مذهب عائشة، وفقهاء المدينة السبعة، ورواية عن أحمد،
```

Three cleanly separated positions with named proponents and evidence. Textbook اختلاف العلماء structure.

### C.4 — A Refutation Pattern

Excerpt `exc_src_test0001_div_src_test0001_6_020_0_2`:

```
5- زعم بعضهم أن الرفع من الركوع ركن صغير، لأنه لم يسن فيه تكرير التسبيحات كالركوع والسجود، ولكن هذا قياس فاسد، لأنه قياس في مقابلة النص فإن الذكر المشروع في الاعتدال من الركوع أطول من الذكر المشروع في الركوع، وقد أخرج ذلك مسلم في حديث ثلاثة من الصحابة.
```

Classic pattern: claim → "ولكن هذا قياس فاسد" → counter-evidence.

### C.5 — A DEPENDENT Excerpt (Good Example for Section 9)

Excerpt `exc_src_test0001_div_src_test0001_2_020_0_16`:

```
واختلف العلماء في حقيقة اليد التي تقطع على أقوال: وأصحها، ما ذهب إليه الجمهور،
```

Self-containment notes: "النص مبتور ولم يُذكر مذهب الجمهور ولا الأقوال الأخرى، فلا يمكن فهم المسألة بدون تتمة النص" (the text is truncated and the majority view and other opinions are not mentioned — the issue cannot be understood without completion).

### C.6 — A Nahw Definition (Different From Fiqh)

From ibn_aqil_v1:

```
الكلام المصطلح عليه عند النحاة: عبارة عن اللفظ المفيد فائدة يحسن السكوت عليه
```

Genus-differentia structure: "the technical definition among grammarians: an utterance that conveys a meaning upon which silence is appropriate." No لغة/شرعا binary.

### C.7 — A Nahw Verse-Commentary Pattern

From ibn_aqil_v1, excerpt `exc_..._0_18`:

```
ثم ذكر في بقية البيت أن علامة فعل الأمر قبول نون التوكيد والدلالة على الأمر بصيغته نحو اضربن واخرجن فإن دلت الكلمة على الأمر ولم تقبل نون التوكيد فهي اسم فعل وإلى ذلك أشار بقوله:
والأمر إن لم يك للنون محل … فيه هو اسم نحو صه وحيهل
فصه وحيهل اسمان وإن دلا على الأمر لعدم قبولهما نون التوكيد
```

The Alfiyya verse IS the teaching; the commentary explains it. Separating verse from commentary removes the foundation.

### C.8 — Interleaved Evidence (Multiple Types in One Passage)

Excerpt `exc_src_test0001_div_src_test0001_1_002_pre_0_10` (98 words):

```
5- الحكمة في إمساكها حتى تطهر من الحيضة الثانية، هو أن الزوج ربما واقعها في ذلك الطهر، فيحصل دوام العشرة، ولذا جاء في بعض طرق الحديث [فإذا طهرت مسها] .
وقال (ابن عبد البر) الرجعة لا تكاد تعلم صحتها إلا بالوطء لأنه المقصود في النكاح.
وأما الحكمة في المنع من طلاق الحائض، فخشية طول العدة.
وأما الحكمة في المنع من الطلاق في الطهر المجامع فيه فخشية أن تكون حاملا، فيندم الزوجان أو أحدهما.
ولو علما بالحمل لأحسنا العشرة، وحصل الاجتماع بعد الفرقة والنفرة.
وكل هذا راجع إلى قوله تعالى {فَطَلقوهُن لعدتهن} ولله في شرعه حكم وأسرار، ظاهرة وخفية.
```

Contains: rational evidence (الحكمة), scholarly opinion (ابن عبد البر), Quranic citation ({فَطَلقوهُن لعدتهن}) — all in continuous argumentative flow connected by و and ف conjunctions. Cannot be cleanly split.

### C.9 — Hadith Commentary Pattern (المعنى الإجمالي)

```
المعنى الإجمالي:
طلق عبد الله بن عمر رضي الله عنهما امرأته وهي حائض، فذكر ذلك أبوه للنبي صلى الله عليه وسلم، فتغيظ غضبا، حيث طلقها طلاقا محرما، لم يوافق السنة.
ثم أمره بمراجعْتها وإمساكها حتى تطهر من تلك الحيضة ثم تحيض أخرى ثم تطهر منها.
```

The hadith IS the frame; this section explains it. Evidence and ruling are reversed from the fiqh model.

### C.10 — Derived Benefits Pattern (ما يُستفاد)

```
ما يستفاد من الحديث:
1- ما يثبت في الرضاع من المحرمية، ومنها تحريم النكاح.
2- أنه يثبت فيه مثل ما يثبت في النسب.
فكل امرأة حرمت نسبا، حرمت من تماثلها رضاعا.
3- الذين تنشر فيهم المحرمية من أجل الرضاع، هم المرتضع وفروعه، أبناؤه وبناته ونسلهم.
```

Each numbered benefit is a separate teaching unit per the SPEC Phase 2b prompt's "Derived Benefits Rule."

---

## Appendix D: Translation Note Accuracy Audit

Each section's Translation note checked against the actual SPEC for accuracy.

| Section | Translation Note Claim | SPEC Reality | Verdict |
|---|---|---|---|
| 1 | "calibrates minimum excerpt length threshold" | No minimum teaching unit length threshold exists in SPEC. Thresholds are only for Phase 1 chunk merge/split (§4.4, §4.5). | **INACCURATE** |
| 2 | "tests current self-containment quality; identifies context_hint content; determines cross-reference resolution" | Accurately maps to §3 (self-containment), §7 (context_hint), §6.4 (IR-1 through IR-3). | ACCURATE |
| 3 | "whether excerpts need to be normalized for comparability" | Excerpt normalization for comparability is a synthesis engine concern, not excerpting. | **WRONG ENGINE** |
| 4 | "calibrate DR-1 (definition pair splitting)" | Accurately maps to DR-1 and the companion-link requirement. | ACCURATE |
| 5 | "whether DR-2 should be reconsidered" | DR-2 was explicitly rejected by 3/5 cross-provider reviewers. The note would direct the team to reconsider a closed governance decision. | **CONTRADICTS GOVERNANCE** |
| 6 | "calibrate DR-3 (khilaf preservation)" | Accurately maps to DR-3. | ACCURATE |
| 7 | "whether excerpting prompts need genre-specific behavior or one-size-fits-all" | SPEC line 629: "No format-specific strategies" — currently one-size-fits-all with `structural_format` as context. Note correctly identifies the question. | ACCURATE |
| 8 | "cross-reference design and taxonomy engine linking" | Accurately identifies this as a taxonomy/synthesis concern, but doesn't note that this means the section doesn't calibrate excerpting. | ACCURATE but misplaced |
| 9 | "whether the 'no puzzle excerpts' principle is absolute or has acceptable exceptions" | Accurately maps to §3.3 self-containment levels (FULL vs. PARTIAL vs. DEPENDENT). | ACCURATE |
| 10 | "defines the user model for the entire system; reference tool vs. learning tool" | Accurately identifies the scope of impact. | ACCURATE |

---

## Appendix E: Key Owner Feedback Principles

Extracted from the two owner feedback comments for reference. These are the owner's own words and reasoning.

### From Feedback 1 (Definition of الطلاق)

**Principle — Self-containment includes no unresolved questions:** "Excerpts should be self contained, which includes answering all questions and confusions that may arise during the owner's usage of the library."

**Principle — Opportunistic grouping over blind atomization:** "Excerpting should definitely not blindly be 'this is one self contained unit, so it's an excerpt'; no, there are many hints that hint at what atoms should form excerpts; continuous sentence, too closely related, opportunistic grouping."

**Principle — Cross-excerpt relationship awareness:** "The relationship between excerpts. Some excerpts — even though they speak about different topics — still need to be connected in some way (not talking about content, but about outer connection)."

**Principle — Cross-excerpt corruption risk:** "If I read the second excerpt, then realize I want to review the first excerpt, then open the leaf in the taxonomy tree and open another 'تعريف الطلاق لغة' from another source, then that is a CORRUPTION in my knowledge: I TRY TO UNDERSTAND ONE EXCERPT BASED ON ANOTHER MISMATCHED EXCERPT!"

**Principle — Excerpt granularity follows taxonomy:** "تعريف الطلاق لغة & تعريف الطلاق شرعا should be different leafs in the taxonomy tree. But if it wasn't, then that would justify this excerpt being only one excerpt."

### From Feedback 2 (Evidence for Divorce Ruling)

**Principle — Per-leaf access vision:** "I open the granulated leaf and get exactly what I want: a direct overview of what all that was ever said on the general ruling. I can directly compare the opinion (not yet the proofs) of every scholar that has ever spoken about this topic."

**Principle — Per-evidence-type and per-ayah granularity:** "The granularity should be: proofing, from quran, from this ayah; that is how the excerpting should be done. If there were multiple quranic verses in this excerpt, they should have produced multiple excerpts; one per quranic verse."

**Principle — Context preservation alongside granularity:** "I do not want to open the leaf that has all proofings from scholars concerning a specific ayah, then have to solve a puzzle: this excerpt belongs to this other excerpt... trying to solve puzzle of what opinion a proofing is trying to justify."

**Principle — Taxonomy-excerpting interaction uncertainty:** "I'm starting to realize: maybe we are losing excerpting potential because the taxonomy trees are not available yet... is it better to let the excerpting be done without providing any information about the taxonomy we have (for unbiased excerpting), or would it be better to deliver the taxonomy tree with?"

---

*End of report. All findings verified by tool execution against the repo. No claims from memory.*
