# Questionnaire Excerpt Audit Trail (Document D)

> For every excerpt shown to the owner, this document records: excerpt ID, source, provenance, selection rationale, and edge case tested. Built BEFORE writing questions — excerpts determine what we can ask.

## Data Provenance Key

All excerpts from `campaign_20260331` unless noted:
- **Run:** campaign_20260331 (March 31, 2026)
- **Models:** Claude Opus 4.6 (classify/group/enrich), GPT-5.4 (verify), Mistral Large (escalation)
- **Prompts:** Pre-hardening (v0 prompts, before H-1 through H-8 fixes)
- **Temperature:** 0.0

**V2 smoke data** (reserved for CJ-2, CJ-3 when valid):
- **Run:** smoke_api_v2 (April 1, 2026, `taysir` failed)
- **Models:** GPT-5.4 (classify/group/enrich), Claude Opus 4.6 (verify)
- **Prompts:** Post-hardening (with H-1 through H-8 + DR-1/DR-3 fixes)
- **Current status:** `CJ-2` and `CJ-3` stay blocked until a valid comparison source exists

---

## Phase 1: Foundations

### F-3: Good Excerpt (baseline quality)
- **Excerpt ID:** `exc_src_test0001_div_src_test0001_6_004_0_0`
- **Source:** campaign_20260331/taysir/excerpts.jsonl
- **Function:** opinion_statement | **Self-containment:** FULL | **Length:** 694 chars
- **Selection rationale:** Medium-length, self-contained, clear scholarly opinion. Represents the "normal good" case — not too short, not too long, clearly one topic.
- **Edge case tested:** None — this is the baseline. Owner reacts to what "good" looks like.
- **Alternatives considered:** Other FULL rule_statements of similar length. This one chosen for clear single-topic structure.

### F-4: Problematic Excerpt
- **Excerpt ID:** `exc_src_test0001_div_src_test0001_2_020_0_16`
- **Source:** campaign_20260331/taysir/excerpts.jsonl
- **Function:** opinion_statement | **Self-containment:** DEPENDENT | **Length:** 78 chars
- **Selection rationale:** Very short (78 chars), DEPENDENT (requires external context), incomplete thought. Designed to naturally surface what the owner considers unacceptable.
- **Edge case tested:** Minimum viability — at what point is an excerpt too fragmentary to be useful?

### F-5: PARTIAL Excerpt with Context Hint
- **Excerpt ID:** `exc_src_test0001_div_src_test0001_1_002_pre_0_5`
- **Source:** campaign_20260331/taysir/excerpts.jsonl
- **Function:** editorial_note | **Self-containment:** PARTIAL | **Length:** 484 chars
- **Selection rationale:** Has a populated context_hint field that summarizes the preceding content. Tests whether the "context summary" approach satisfies the owner's self-containment requirement.
- **Edge case tested:** Self-containment gate — is a summary note sufficient, or is it still a "puzzle"?

### F-6: Rich Scholarly Arabic Text
- **Excerpt ID:** `exc_src_test0001_div_src_test0001_1_002_pre_0_12`
- **Source:** campaign_20260331/taysir/excerpts.jsonl
- **Function:** evidence_hadith | **Self-containment:** FULL | **Length:** 857 chars
- **Selection rationale:** Full hadith text with scholarly Arabic prose, diacritics, and transmission formula. Tests the "reference tool vs learning tool" question — does the owner want exact text or simplified versions?

---

## Phase 2: Dimension Deep Dives

### G-1: Very Short Excerpt
- **Excerpt ID:** `exc_src_test0001_div_src_test0001_4_000_0_1`
- **Source:** campaign_20260331/taysir/excerpts.jsonl
- **Function:** definition | **Self-containment:** FULL | **Length:** 278 chars
- **Selection rationale:** Short definition, self-contained. Tests minimum excerpt size threshold.
- **Edge case tested:** At what length does an excerpt become "noise" rather than useful knowledge?

### G-2: Very Long Excerpt
- **Excerpt ID:** `exc_src_test0001_div_src_test0001_6_000_0_12`
- **Source:** campaign_20260331/taysir/excerpts.jsonl
- **Function:** evidence_hadith | **Self-containment:** FULL | **Length:** 2351 chars
- **Selection rationale:** Longest usable excerpt in campaign data. Tests maximum excerpt size and whether it should be split.

### G-3: Numbered List
- **Excerpt ID:** `exc_src_test0001_div_src_test0001_1_002_pre_0_7`
- **Source:** campaign_20260331/taysir/excerpts.jsonl
- **Function:** opinion_statement | **Self-containment:** FULL | **Length:** 308 chars
- **Selection rationale:** Contains numbered scholarly points. Tests whether numbered items should be individual excerpts.

### G-4: Condition/Exception (Semantic Coupling)
- **Excerpt ID:** `exc_src_test0001_div_src_test0001_2_020_0_8`
- **Source:** campaign_20260331/taysir/excerpts.jsonl
- **Function:** condition_exception | **Self-containment:** PARTIAL | **Length:** 390 chars
- **Selection rationale:** An exception to a ruling. Tests semantic coupling — should exceptions stay with their rulings?

### SC-1: PARTIAL with Good Summary
- **Excerpt ID:** `exc_src_test0001_div_src_test0001_1_004_pre_0_2`
- **Source:** campaign_20260331/taysir/excerpts.jsonl
- **Function:** rule_statement | **Self-containment:** PARTIAL | **Length:** 468 chars
- **Selection rationale:** PARTIAL excerpt with context_hint that summarizes well. Tests the grey zone of self-containment.

### SC-2: Backward Reference (كما تقدم)
- **Excerpt ID:** `exc_src_test0001_div_src_test0001_6_000_0_17`
- **Source:** campaign_20260331/taysir/excerpts.jsonl
- **Function:** rule_statement | **Self-containment:** PARTIAL | **Length:** 1369 chars
- **Selection rationale:** Contains explicit backward reference to earlier content. Tests cross-reference handling.

### SC-3: Context-Dependent Transition
- **Excerpt ID:** `exc_src_test0001_div_src_test0001_4_000_0_0`
- **Source:** campaign_20260331/taysir/excerpts.jsonl
- **Function:** structural_transition | **Self-containment:** FULL | **Length:** 339 chars
- **Selection rationale:** A transition that assumes chapter context. Tests whether structural context is implicit or needs to be made explicit.

### D-1: Short Definition
- **Excerpt ID:** `exc_src_test0001_div_src_test0001_1_002_pre_0_0`
- **Source:** campaign_20260331/taysir/excerpts.jsonl
- **Function:** definition | **Self-containment:** FULL | **Length:** 252 chars
- **Edge case tested:** DR-1 threshold — when a definition is short, should it still be split from its legal counterpart?

### D-2: Definition with Connecting Sentence
- **Excerpt ID:** `exc_src_test0001_div_src_test0001_1_002_pre_0_13`
- **Source:** campaign_20260331/taysir/excerpts.jsonl
- **Function:** definition | **Self-containment:** PARTIAL | **Length:** 828 chars
- **Edge case tested:** DR-1 boundary — when an explicit sentence connects لغة and شرعا, does splitting still make sense?

### D-3: Triple Definition
- **Excerpt ID:** `exc_src_test0001_div_src_test0001_1_004_pre_0_5`
- **Source:** campaign_20260331/taysir/excerpts.jsonl
- **Function:** definition | **Self-containment:** FULL | **Length:** 448 chars
- **Edge case tested:** DR-1 extension — three definitions (لغة, اصطلاحا, مذهب-specific). One, two, or three excerpts?

### E-1: Proof Plus Explanatory Wisdom
- **Excerpt ID:** `exc_src_test0001_div_src_test0001_6_094_0_1`
- **Source:** campaign_20260331/taysir/excerpts.jsonl
- **Function:** evidence_quran | **Self-containment:** FULL | **Length:** 521 chars
- **Selection rationale:** The passage mixes proof with reflective explanation about mercy, benefit, and divine wisdom. It is no longer just an evidence-type question.
- **Edge case tested:** DR-2 boundary — should explanatory wisdom stay fused to proof material, or become a separate unit?

### E-2: Hadith as Evidence
- **Excerpt ID:** `exc_src_test0001_div_src_test0001_1_002_pre_0_4`
- **Source:** campaign_20260331/taysir/excerpts.jsonl
- **Function:** evidence_hadith | **Self-containment:** FULL | **Length:** 526 chars
- **Edge case tested:** Hadith + ruling coupling — should evidence stay with the ruling it supports?

### E-3: Multi-Type Evidence (Owner-Referenced)
- **Excerpt ID:** `exc_src_test0001_div_src_test0001_1_002_pre_0_1`
- **Source:** campaign_20260331/taysir/excerpts.jsonl
- **Function:** opinion_statement | **Self-containment:** FULL | **Length:** 619 chars
- **Selection rationale:** This is the exact excerpt the owner referenced in his feedback ("وحكمه ثابت في الكتاب والسنة والإجماع والقياس"). He already has opinions about this text. Testing whether those opinions hold under edge cases.

### K-1: Short Multi-Position Passage
- **Excerpt ID:** `exc_src_test0001_div_src_test0001_1_002_pre_0_7`
- **Source:** campaign_20260331/taysir/excerpts.jsonl
- **Function:** opinion_statement | **Self-containment:** FULL | **Length:** 308 chars
- **Note:** Same as G-3. Reused because it contains multiple scholarly positions in numbered format — tests both granularity AND khilaf handling.

### K-2: Longer Position Passage
- **Excerpt ID:** `exc_src_test0001_div_src_test0001_1_003_pre_0_13`
- **Source:** campaign_20260331/taysir/excerpts.jsonl
- **Function:** opinion_statement | **Self-containment:** PARTIAL | **Length:** 222 chars

### GN-1-fiqh: Fiqh Excerpt
- **Excerpt ID:** `exc_src_test0001_div_src_test0001_1_002_pre_0_1`
- **Source:** campaign_20260331/taysir/excerpts.jsonl
- **Function:** opinion_statement | **Length:** 619 chars | **Science:** Fiqh (hadith-fiqh sharh)

### GN-1-nahw: Nahw Excerpt
- **Excerpt ID:** `exc_src_test0001_div_src_test0001_2_001_0_11`
- **Source:** campaign_20260331/ibn_aqil_v1/excerpts.jsonl
- **Function:** rule_statement | **Length:** 315 chars | **Science:** Nahw (grammar)

### GN-1-usul: Usul Excerpt
- **Excerpt ID:** `exc_src_test0001_div_src_test0001_1_000_pre_0_0`
- **Source:** campaign_20260331/ext_46_qa/excerpts.jsonl
- **Function:** definition | **Length:** 268 chars | **Science:** Usul al-Nahw

### GN-2: Reused Grammar Example
- **Excerpt ID:** `exc_src_test0001_div_src_test0001_2_001_0_11`
- **Source:** campaign_20260331/ibn_aqil_v1/excerpts.jsonl
- **Selection rationale:** Reuses GN-1 excerpt B because the owner question is specifically about whether the example sentence (الشاهد) inside that rule must stay with the rule.
- **Edge case tested:** Whether nahw examples can be detached from the rule without destroying understanding.

### L-1: Editorial/Scholarly Note
- **Excerpt ID:** `exc_src_test0001_div_src_test0001_1_002_pre_0_3`
- **Source:** campaign_20260331/taysir/excerpts.jsonl
- **Function:** editorial_note | **Self-containment:** FULL | **Length:** 566 chars
- **Edge case tested:** Layer attribution — who is the "author" of an editorial note?

### L-2: Real Matn + Sharh Layering Example
- **Excerpt ID:** `exc_src_test0001_div_src_test0001_2_004_0_1`
- **Source:** campaign_20260331/ibn_aqil_v1/excerpts.jsonl
- **Function:** definition | **Self-containment:** FULL
- **Selection rationale:** Real mixed-layer example where the Alfiyyah matn line is immediately followed by Ibn Aqil's explanation. Tests structure, authorship, and whether explicit layer labels are required.
- **Edge case tested:** Multi-layer attribution clarity — if matn and sharh are shown together, can the owner still trust the entry without explicit labels?

### L-3: Substantive Footnote Example
- **Excerpt ID:** `exc_src_test0001_div_src_test0001_6_094_0_1`
- **Source:** campaign_20260331/taysir/excerpts.jsonl
- **Function:** evidence_quran | **Self-containment:** FULL
- **Selection rationale:** The visible excerpt contains a real footnote marker (`⌜1⌝`) and a substantive explanatory footnote on `الكظم`. The owner question also asks whether the same rule should apply to takhrij/grading notes.
- **Edge case tested:** Inline vs linked vs hidden treatment for substantive footnotes and source/grading apparatus.

### QA-1: Formal Objection and Response
- **Excerpt ID:** `exc_src_test0001_div_src_test0001_3_003_0_3`
- **Source:** campaign_20260331/ext_46_qa/excerpts.jsonl
- **Function:** refutation | **Self-containment:** FULL
- **Selection rationale:** Concrete objection/response passage, not an invented structure. The text explicitly stages the objection, proposed answer, rebuttal, and later comment.
- **Edge case tested:** Whether formal scholarly objection and response can ever be safely separated.

### M-1: Metadata Display
- **Excerpt ID:** `exc_src_test0001_div_src_test0001_6_018_0_5`
- **Source:** campaign_20260331/taysir/excerpts.jsonl
- **Function:** rule_statement | **Self-containment:** FULL | **Length:** 583 chars
- **Selection rationale:** Well-populated metadata fields. Tests what information the owner needs alongside an excerpt.

---

## Phase 3: Comparative Judgment

### CJ-1: Three Excerpting Approaches
- Uses excerpt `E-3` hypothetically split 3 ways
- No new excerpt needed — the comparison is constructed from the same text

### CJ-2: BLOCKED (before/after comparison source missing)
- Intended to compare the same passage from campaign (Opus) vs smoke_api_v2 (GPT-5.4 hardened)
- Currently blocked because the weekend `taysir` v2 run failed before valid comparison pairs were written

### CJ-3: BLOCKED (cross-book comparison source missing)
- Intended to use the closest topic matches available across 2 books
- Currently blocked because the weekend `taysir` v2 run failed before valid cross-book comparison material was assembled

### CJ-4: Metadata Sufficiency
- Uses excerpt `M-1` with metadata rendered in plain language
