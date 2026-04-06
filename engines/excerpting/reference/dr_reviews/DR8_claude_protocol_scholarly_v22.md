# Deep scholarly review of the KR Hardening Session Protocol v2.2

The protocol protects against many engineering-level text corruption risks but **misses foundational Islamic scholarly structures that govern how classical Arabic texts actually work**. The cross-science list omits four structurally distinct disciplines whose texts cannot be excerpted correctly under the current rules. The indivisible-unit inventory covers only 5 of at least 21 unit types, leaving the excerpting engine blind to the sharḥ-matn pair — the dominant structural pattern in the entire classical Arabic scholarly corpus. The FP-13 precedence stack treats all sciences identically when the correct priority order demonstrably varies by genre. These are not edge cases. They are the mainstream of the tradition.

What follows is a ground-truth reference compiled from classical Islamic scholarly classification systems (Ibn Khaldūn's *Muqaddimah*, al-Ghazālī's *Iḥyāʾ*, Ṭāshköprüzāda's *Miftāḥ al-Saʿāda*), modern Islamic university curricula (al-Azhar, Islamic University of Madinah), digital corpus projects (OpenITI/KITAB), and the internal structures of canonical works across every major genre. The protocol is then evaluated against this ground truth across six dimensions, yielding 19 findings.

---

## 1. Scholarly ground truth

### 1.1 Complete science taxonomy with structure notes

The protocol lists eight sciences for cross-science checking: fiqh, ḥadīth, naḥw, tafsīr, uṣūl al-fiqh, ʿaqīdah, lughah/balāghah, tārīkh/sīrah. Research against Ibn Khaldūn's transmitted/rational division, al-Azhar's faculty structure, and the Islamic University of Madinah's college system reveals **four sciences with structurally distinct text formats that are entirely missing**, plus five that warrant sub-type notation.

**Sciences that must be added as separate categories:**

**Ṭabaqāt (طبقات) — Biographical dictionaries.** This is the strongest case. Ṭabaqāt texts like *Siyar Aʿlām al-Nubalāʾ* by al-Dhahabī or *Wafayāt al-Aʿyān* by Ibn Khallikān are **entry-based**, not argument-based. Each tarjamah (biographical entry) is a self-contained unit following a formulaic structure: name/nasab → birth/death → teachers → students → works → evaluative judgment → anecdotes. This is fundamentally different from every other genre in the list. Collapsing it into tārīkh (which is continuous chronological narrative) destroys the structural information the excerpting engine needs. The OpenITI/KITAB project explicitly tags tarjamah entries as distinct logical units (### $) for exactly this reason.

**Muṣṭalaḥ al-ḥadīth (مصطلح الحديث) — Hadith terminology/sciences.** Texts like *Muqaddimah Ibn al-Ṣalāḥ* (65 chapters each defining a hadith type) are technical manuals structured as definition → criteria → examples → scholarly disagreement. They contain no isnād-matn pairs. The current "ḥadīth" category presumably covers collections like Ṣaḥīḥ al-Bukhārī, whose structure (isnād-matn units arranged by kitāb/bāb) is radically different. Conflating them means the expansion template will apply isnād-matn rules to texts that contain no isnāds.

**Manṭiq (منطق) — Logic.** Texts like *al-Risālah al-Shamsiyyah* and *Īsāghūjī* proceed from terms → propositions → syllogisms. Each syllogistic chain (premise-premise-conclusion) is an indivisible logical unit unlike anything in uṣūl al-fiqh, which uses legal analogical reasoning in a different format. Logic texts were mainstays of madrasa teaching from the late thirteenth century onward and are taught as a separate prerequisite discipline at every major Islamic institution.

**Ṣarf (صرف) — Morphology.** Texts like *al-Taṣrīf al-ʿIzzī* by al-Zanjānī are organized around morphological patterns (awzān) and dominated by **paradigm tables** (jadāwil al-taṣrīf) — grid structures showing verb conjugation across all persons, genders, numbers, and tenses. This tabular structure is entirely absent from naḥw, which is rule-based discursive prose. Al-Azhar lists ṣarf separately from naḥw. A paradigm table is an indivisible visual-structural unit that naḥw excerpting rules cannot handle.

**Sciences requiring sub-type notation within existing categories:**

Farāʾiḍ (inheritance law) merges under fiqh but its mathematical worked examples and fraction tables need special handling rules. Qirāʾāt (recitation sciences) merges under tafsīr but its variant-listing and poetic-mnemonic formats are unique. ʿUlūm al-Qurʾān merges under tafsīr but is topical-encyclopedic rather than verse-by-verse. Tazkiyah/sulūk merges under ʿaqīdah but station-based and anecdote-heavy texts overlap with ṭabaqāt. Adab merges under lughah/balāghah but its anthological khabar-based structure differs from systematic rhetoric.

**Recommended expanded list:** 12 categories — the original 8 plus ṭabaqāt, muṣṭalaḥ al-ḥadīth, manṭiq, and ṣarf — with sub-type flags for farāʾiḍ, qirāʾāt, ʿulūm al-Qurʾān, tazkiyah, and adab.

### 1.2 Complete indivisible unit inventory

The protocol lists five indivisible units. Research identifies **21 total**, meaning 16 are missing. These fall into three tiers of indivisibility:

**Always indivisible (splitting is always corruption):**

- **Sharḥ-matn pair (شرح ومتن):** The commentary snippet + the base text it explains. In all three structural forms (interleaved, "he said... I say...", or "his words..."), the sharḥ uses anaphoric references ("the author's intention here...") that require the matn. Commentary literature constitutes the **majority** of classical Islamic scholarly texts. This is the most critical missing unit.
- **Suʾāl-jawāb (سؤال وجواب):** The fatwa question + answer. The jawāb's referential context ("this is permissible") is meaningless without the suʾāl specifying what "this" is. Critical circumstantial details in the question shape the ruling.
- **Tarjamah (ترجمة):** The biographical entry in ṭabaqāt literature. Separating a narrator's name from their reliability grade makes ḥadīth authentication impossible.
- **Qiyās (قياس):** The four pillars — aṣl, farʿ, ʿillah, ḥukm. Al-Āmidī (*al-Iḥkām* III, 186) defines qiyās as requiring all four. Removing any one invalidates the entire analogical argument.
- **Radd / iʿtirāḍ-jawāb (رد / اعتراض وجواب):** The opponent's position + the author's refutation. Al-Ghazālī's *Tahāfut al-Falāsifah* states 20 philosophical positions then refutes each — the refutation without the stated position is unintelligible.
- **Istishhād (استشهاد):** The poetic evidence block (verse + grammatical/rhetorical explanation + attribution). When a verse functions as proof for a grammatical rule, separating it from the rule removes the evidentiary function.
- **Takhrīj (تخريج):** The ḥadīth text + source list + grading. Separating a ḥadīth from its grading means a weak ḥadīth could be mistaken for an authentic one — catastrophic for jurisprudence.
- **Ijāzah (إجازة):** Transmission license blocks embedded in manuscripts. The licensor-licensee-text-chain is a legal-scholarly document.
- **Masʾalat al-farāʾiḍ:** Inheritance worked calculations. A partial calculation is worse than none.
- **Jadwal/taṣrīf:** Paradigm tables. A partial conjugation table is misleading.
- **Duʿāʾ/dhikr:** Supplication formulas embedded in scholarly texts. Truncation corrupts liturgical content.

**Usually indivisible (splitting is almost always corruption):**

- **Khilāf (خلاف):** The juristic disagreement register for one masʾalah. Presenting only one madhhab's position from a comparative survey misrepresents the state of the law.
- **Taqsīm (تقسيم):** Division/taxonomy trees. "X is of three types..." — splitting after type 2 means the reader has an incomplete taxonomy and may not know it.
- **Ikhtilāf al-ruwāh:** Variant readings apparatus. The base reading + variants form one textual-critical unit.

**Conditionally indivisible (splitting is corruption in specific contexts):**

- **Ijmāʿ (إجماع):** Consensus report + noted dissent. "The scholars agreed... except Ibn Ḥazm" — separating the exception transforms a qualified consensus into an absolute one.
- **Sharṭ-jawāb:** Conditional-consequence structures. "If X, then Y" — presenting only the condition leaves the ruling incomplete.

### 1.3 Natural atom analysis per major genre

Across all genres researched, the natural atom preserves the author's complete treatment of a discrete topic including all evidence and counter-evidence. The Islamic scholarly tradition demands that every assertion be traceable to its source — any excerpt separating a claim from its dalīl violates this foundational epistemological commitment.

| Genre | Natural atom | Typical size | Governing principle |
|-------|-------------|-------------|-------------------|
| **Fiqh** | Masʾalah + full khilāf + adillah + tarjīḥ | 1–5 pages | The legal question needs its evidence and scholarly debate |
| **Ḥadīth sharḥ** | Complete bāb (tarjamah heading + all ḥadīths + commentary) | 2–10 pages | Bukhārī's chapter heading IS the interpretive key (*fiqh al-Bukhārī fī tarājimih*) |
| **Naḥw** | Complete grammatical sub-topic (3–10 Alfiyyah lines + sharḥ + shawāhid) | 2–8 pages | A rule needs its conditions, exceptions, and evidentiary poetry |
| **Tafsīr** | Mufassir's own āyah-grouping (maqṭaʿ) + full commentary | 1–15 pages | The mufassir chose the grouping for thematic coherence |
| **Uṣūl al-fiqh** | Masʾalah + complete argument chain (taʿlīl + tafrīʿ) | 3–10 pages | The reasoning IS the substance |
| **ʿAqīdah** | Creedal statement + full sharḥ/defense | 1–10 pages | Matn without sharḥ is catechism without understanding |
| **Ṭabaqāt** | Individual tarjamah | 0.5–30 pages | The biography is the unit; subdivide only when very long |
| **Tazkiyah** | One manzilah (spiritual station) or one darajah within it | 2–20 pages | The interdisciplinary synthesis per station defines the genre |

A critical finding for ḥadīth sharḥ: the **bāb** is the correct atom for Ṣaḥīḥ al-Bukhārī because al-Bukhārī's tarājim al-abwāb (chapter headings) encode his jurisprudential understanding — an entire sub-discipline called *fiqh al-Bukhārī fī tarājimih* exists to decode them. Divorcing an individual ḥadīth from its bāb heading loses this interpretive framework. By contrast, in Sunan Abī Dāwūd (*ʿAwn al-Maʿbūd*), individual ḥadīths are closer to atomic because the organizational structure is simpler.

---

## 2. Evaluation findings

### Evaluation 1: Completeness of the cross-science variation section (§4.3)

**SCH-001: Ṭabaqāt missing from the science list — entry-based texts invisible to the engine**

- **Severity:** CRITICAL
- **Protocol section:** §4.3, Cross-Science Variation checklist
- **Scholarly reasoning:** Ṭabaqāt literature (biographical dictionaries like *Siyar Aʿlām al-Nubalāʾ*, *Ṭabaqāt Ibn Saʿd*, *Wafayāt al-Aʿyān*) uses an **entry-based** structure where each tarjamah is an independent, self-contained unit. No other listed science has this structure. Without ṭabaqāt in the checklist, the expansion template will treat biographical entries as sections of continuous narrative (applying tārīkh rules), potentially splitting an entry mid-biography — separating a narrator's name from their reliability assessment, which breaks ḥadīth authentication.
- **Damage cascade:** An atom designed for a ṭabaqāt text checked against only the 8 listed sciences will never encounter the rule "a tarjamah is atomic." The excerpting engine will treat biographical dictionaries as prose chapters, splitting entries at arbitrary page boundaries. For rijāl works (narrator criticism), this directly corrupts ḥadīth science.
- **Concrete example:** In *Tahdhīb al-Tahdhīb* by Ibn Ḥajar, entry #4523 for narrator "Muḥammad ibn Ibrāhīm al-Taymī" contains: his name, his teachers, a dispute about his reliability (Ibn Maʿīn says thiqah, al-Nasāʾī says laysa bihi baʾs), and a clarifying note. If the engine splits this entry between the reliability grades, one excerpt says "reliable" and another says "not problematic" — the student never sees the nuanced disagreement.
- **Proposed amendment:** Add ṭabaqāt/tarājim as a 9th science category. Add to the Cross-Science Variation checklist: "In ṭabaqāt: does this atom respect tarjamah (biographical entry) boundaries? Each entry from name-line to death-notice is atomic."
- **Confidence:** HIGH. Ṭabaqāt is universally recognized as a distinct genre. OpenITI/KITAB tags entries as atomic units.

---

**SCH-002: Muṣṭalaḥ al-ḥadīth conflated with ḥadīth collections**

- **Severity:** HIGH
- **Protocol section:** §4.3, Cross-Science Variation checklist
- **Scholarly reasoning:** The listed "ḥadīth" category presumably covers collections (Bukhārī, Muslim) with their isnād-matn structure. Muṣṭalaḥ al-ḥadīth texts (*Muqaddimah Ibn al-Ṣalāḥ*, *al-Nukat* by Ibn Ḥajar) are technical manuals structured as definition → criteria → examples → scholarly disagreement. They contain **no isnāds to preserve**. The isnād-matn integrity rule (FP-11) is irrelevant to them, while the taxonomic-definitional structure that governs them has no corresponding rule.
- **Damage cascade:** When CC encounters a muṣṭalaḥ text and checks the "ḥadīth" column in Cross-Science Variation, it will apply isnād-matn rules to text that has no isnāds and miss the definitional-taxonomic structure (e.g., "the ḥadīth ṣaḥīḥ is that which..." + its five conditions = one indivisible definitional unit).
- **Proposed amendment:** Either split "ḥadīth" into "ḥadīth collections" and "ḥadīth methodology (muṣṭalaḥ)" or add muṣṭalaḥ as a separate 10th category with note: "Technical-definitional structure. Each ḥadīth type definition + criteria + examples is atomic. Isnād-matn rules do not apply."
- **Confidence:** HIGH. Every Islamic university teaches these as separate disciplines.

---

**SCH-003: Manṭiq and ṣarf missing — unique structural patterns unaddressed**

- **Severity:** MEDIUM
- **Protocol section:** §4.3, Cross-Science Variation checklist
- **Scholarly reasoning:** Manṭiq texts contain syllogistic chains (premise-premise-conclusion) that form indivisible logical units distinct from any structure in the 8 listed sciences. Ṣarf texts are dominated by paradigm tables (jadāwil) — tabular grid structures absent from naḥw. Both are taught as separate disciplines at al-Azhar and every major Islamic institution.
- **Damage cascade:** For manṭiq: a syllogism split mid-argument (premise without conclusion) is logically meaningless. For ṣarf: a paradigm table split between rows produces a partial conjugation that may appear complete but is missing forms, misleading the student. If the library contains *Īsāghūjī*, *al-Shamsiyyah*, *al-Taṣrīf al-ʿIzzī*, or similar texts, these will be excerpted incorrectly.
- **Proposed amendment:** Add manṭiq and ṣarf to the science list. For manṭiq: "Syllogistic chains (muqaddimah kubrā + ṣughrā + natījah) are atomic. Definition-division trees must not be split." For ṣarf: "Paradigm tables (jadāwil al-taṣrīf) are atomic visual units."
- **Confidence:** MEDIUM. Impact depends on whether the library actually contains these texts. If it does, the gap is HIGH severity.

---

**SCH-004: Sciences should be grouped by text-structure type, not listed flat**

- **Severity:** MEDIUM
- **Protocol section:** §4.3, Cross-Science Variation checklist
- **Scholarly reasoning:** The current flat list treats all 8 sciences as equally different, but they cluster into structural families. **Argument-based** sciences (fiqh, uṣūl, ʿaqīdah, manṭiq) share claim-evidence-rebuttal patterns. **Narrative-based** sciences (tārīkh/sīrah, tafsīr) share chronological/sequential flow. **Entry-based** sciences (ṭabaqāt, muṣṭalaḥ) share discrete self-contained units. **Rule-based** sciences (naḥw, ṣarf) share rule-example-evidence patterns. **Commentary-structured** sciences (ḥadīth sharḥ) share matn-sharḥ layering. Grouping by structural family would help CC identify which rules actually apply.
- **Damage cascade:** Without structural grouping, CC must check each science individually against each atom. With grouping, CC can check whether an atom is in an argument-based, narrative-based, entry-based, or rule-based text and apply the appropriate structural rules immediately.
- **Proposed amendment:** Add a structural-family tag to each science: `[ARG]` argument-based, `[NAR]` narrative-based, `[ENT]` entry-based, `[RUL]` rule-based, `[COM]` commentary-structured. The expansion template should first identify the structural family, then check science-specific rules.
- **Confidence:** MEDIUM. This is an optimization that reduces CC error rate but is not strictly necessary.

---

### Evaluation 2: Completeness of the atomic integrity risk section (§4.3)

**SCH-005: Sharḥ-matn pair missing — the single most dangerous gap in the protocol**

- **Severity:** CRITICAL
- **Protocol section:** §4.3, Atomic Integrity Risk checklist
- **Scholarly reasoning:** Commentary literature (sharḥ on matn, ḥāshiya on sharḥ) constitutes the **majority** of classical Islamic scholarly texts. The entire Ḥanafī legal canon rests on layers: Tumurtāshī's *Tanwīr al-Abṣār* (matn) → al-Ḥaskafī's *al-Durr al-Mukhtār* (sharḥ) → Ibn ʿĀbidīn's *Radd al-Mukhtār* (ḥāshiya). The sharḥ embeds or cites matn text word-by-word using formulas like "qawluhu" (قوله — "his words") and then comments on it. Separating the sharḥ passage from its matn snippet renders the commentary unintelligible because every anaphoric reference ("the author's intention here," "this," "the aforementioned") loses its referent.
- **Damage cascade:** The expansion template currently has no rule preventing a boundary between a matn snippet and its corresponding sharḥ. In a three-layer text, the engine could produce an excerpt containing ḥāshiya text that says "the Shāriḥ's statement that..." with no sharḥ present, which in turn references "the author's words..." with no matn present. The student receives text that is grammatically Arabic but semantically void.
- **Concrete example:** In *Fatḥ al-Bārī*, Ibn Ḥajar writes: "قوله: باب ما جاء في المسح على الخفين — أراد بذلك..." ("His words [al-Bukhārī's]: 'Chapter on what has come regarding wiping over leather socks' — he intended by this..."). If the excerpt begins at "أراد بذلك," the student has no idea what "he intended by this" refers to.
- **Proposed amendment:** Add to Atomic Integrity Risk: "Sharḥ-matn pair: In commentary literature, the matn snippet (often introduced by قوله or marked ص) + its corresponding sharḥ (often marked ش) constitute one indivisible unit. In multi-layer texts, this extends to: matn segment + sharḥ passage + ḥāshiya passage for that segment. No boundary may fall between layers commenting on the same textual segment. The MATN defines the atomic unit; the sharḥ and ḥāshiya inherit its boundaries."
- **Confidence:** HIGH. This is not debatable — the dependency is structural and absolute.

---

**SCH-006: Suʾāl-jawāb, radd, qiyās, and khilāf structures missing**

- **Severity:** CRITICAL
- **Protocol section:** §4.3, Atomic Integrity Risk checklist
- **Scholarly reasoning:** Four argumentative structures pervade Islamic scholarly texts and are entirely absent from the indivisible-unit list:
  - **Suʾāl-jawāb:** A fatwā answer saying "this is permissible" without its question is meaningless. In *Majmūʿ al-Fatāwā* of Ibn Taymiyyah, each jawāb references specific circumstances from the suʾāl.
  - **Radd/iʿtirāḍ-jawāb:** In kalām and fiqh debate, "fa-in qīla... qulnā..." (if it is said... we say...) pairs are atomic. Al-Ghazālī's *Tahāfut* has 20 stated positions each followed by systematic refutation — the refutation without the position is unintelligible.
  - **Qiyās:** The four pillars (aṣl, farʿ, ʿillah, ḥukm) cannot be separated. The classical example: prohibition of drugs by analogy with wine requires all four components.
  - **Khilāf register:** When al-Mughnī presents all four madhāhib on one masʾalah, presenting only one madhhab's position misrepresents the state of the law.
- **Damage cascade:** These four structures are the **primary argumentative patterns** of fiqh and uṣūl texts. Without them in the checklist, the expansion template will never flag an atom that splits a question from its answer, an objection from its response, or an analogy mid-argument. Every comparative fiqh text in the library is at risk.
- **Proposed amendment:** Add four entries to Atomic Integrity Risk: (1) "Suʾāl-jawāb: In fatwā collections, the question + answer pair is atomic. Never place a boundary between suʾāl and jawāb." (2) "Radd/iʿtirāḍ-jawāb: An opponent's quoted position (often introduced by فإن قيل / قال) + the author's refutation (often introduced by قلنا / والجواب) is atomic." (3) "Qiyās: The four arkān (aṣl, farʿ, ʿillah, ḥukm) form one indivisible analogical argument." (4) "Khilāf: A complete disagreement register for one masʾalah — all madhāhib positions + evidence + tarjīḥ — is usually atomic."
- **Confidence:** HIGH for suʾāl-jawāb and radd. HIGH for qiyās. MEDIUM for khilāf (long khilāf discussions sometimes can be subdivided by position, though this is risky).

---

**SCH-007: Taqsīm (taxonomy) structures missing — silent truncation risk**

- **Severity:** HIGH
- **Protocol section:** §4.3, Atomic Integrity Risk checklist
- **Scholarly reasoning:** Classical Arabic texts frequently say "X is of three types..." (ينقسم إلى ثلاثة أقسام). If a boundary falls after type 2, the student has an incomplete taxonomy and **may not know it is incomplete** — this is exactly the "silent corruption" that FP-5 identifies as existential. In uṣūl al-fiqh, where legal consequences follow from classification (e.g., qiyās is of three types, each with different epistemic weight), a truncated taxonomy produces wrong legal reasoning.
- **Damage cascade:** The student reads "qiyās is of two types: qiyās al-awlā and qiyās al-musāwī" and never learns about qiyās al-adnā. They then encounter a qiyās al-adnā argument in practice and cannot classify it, or worse, treat it as having the same epistemic weight as qiyās al-awlā.
- **Proposed amendment:** Add to Atomic Integrity Risk: "Taqsīm (division/taxonomy): When a text divides a concept into numbered sub-categories (ينقسم إلى / وهو ثلاثة أنواع / etc.), the complete division + all sub-categories is atomic. Flag any boundary that falls within a numbered division."
- **Confidence:** HIGH. This is a universal pattern across all Islamic sciences.

---

**SCH-008: The indivisible-unit list should be hierarchical, not flat**

- **Severity:** MEDIUM
- **Protocol section:** §4.3, Atomic Integrity Risk checklist
- **Scholarly reasoning:** The current flat list implies all 5 units are equally indivisible. But research reveals three tiers: (1) **Absolutely indivisible** in all contexts (isnād-matn, sharḥ-matn, suʾāl-jawāb, qiyās); (2) **Usually indivisible** but splittable in extreme cases (khilāf registers, taqsīm trees — very long ones might be subdivided if each sub-section is self-contained); (3) **Conditionally indivisible** depending on context (ijmāʿ + dissent, sharṭ-jawāb structures). Additionally, some units are indivisible in some sciences but not others — a poetic verse (bayt) is indivisible in naḥw (where it serves as evidence) but may be decorative in adab.
- **Proposed amendment:** Restructure the Atomic Integrity Risk section into three tiers: ABSOLUTE (never split under any circumstance), STRONG (split only when the unit exceeds maximum excerpt size and natural sub-boundaries exist), and CONDITIONAL (split permitted when specific contextual conditions are met — list the conditions). Add a science-sensitivity column indicating which sciences each unit appears in.
- **Confidence:** MEDIUM. The tiering is well-supported but the exact boundary between tiers requires domain expertise to finalize.

---

### Evaluation 3: The FP-13 precedence stack (§5.4)

**SCH-009: Grammatical integrity underranked for naḥw and ṣarf texts**

- **Severity:** HIGH
- **Protocol section:** §5.4, Disagreement Resolution Hierarchy
- **Scholarly reasoning:** The current stack ranks: attribution safety > dialogue preservation > grammatical integrity > self-containment > granularity. In naḥw texts, **grammatical integrity IS the content**. When Sharḥ Ibn ʿAqīl explains a grammatical rule with its exceptions and evidentiary poetry (shawāhid), preserving the grammatical argument IS preserving the dialogue, the attribution, and the self-containment simultaneously. Ranking grammatical integrity third means that in a conflict between "preserve who said this" and "preserve the complete grammatical argument," the protocol chooses attribution over the argument — but in naḥw, the grammatical argument is the entire point.
- **Concrete scenario where the ranking produces wrong results:** An excerpt from *Sharḥ Ibn ʿAqīl* contains a grammatical rule attributed to al-Kūfiyyūn (Kufan grammarians), followed by the Baṣran counter-argument. A boundary must be placed somewhere. Under the current stack, attribution safety says: ensure each position is attributed to its school. Dialogue preservation says: keep the exchange intact. Grammatical integrity says: keep the rule + its exceptions + shawāhid together. If the excerpt is hitting maximum size, the current ranking would sacrifice grammatical integrity (dropping a shāhid verse) before sacrificing dialogue preservation — but the shāhid IS the proof of the rule. Losing it corrupts the grammar.
- **Proposed amendment:** Add a science-sensitivity modifier to FP-13: "In rule-based sciences (naḥw, ṣarf), grammatical integrity is promoted to rank 1. The rule + its conditions + evidentiary verses constitute the primary content, and all other values serve it." Alternatively, define the stack as context-dependent with a lookup: `{science_family: priority_order}`.
- **Confidence:** HIGH. The argument that grammatical integrity should always rank below attribution safety and dialogue preservation does not survive contact with actual grammar texts.

---

**SCH-010: Missing values in the precedence stack — evidential completeness and layer integrity**

- **Severity:** HIGH
- **Protocol section:** §5.4, Disagreement Resolution Hierarchy
- **Scholarly reasoning:** Two values are demonstrably missing from the stack:
  - **Evidential completeness (اكتمال الدليل):** The Islamic scholarly tradition demands that every claim (ḥukm) be accompanied by its evidence (dalīl). An excerpt that presents a ruling without its proof, or a proof without the ruling it supports, violates the epistemological foundation of the tradition. This is distinct from "self-containment" (which asks whether the excerpt makes sense alone) — evidential completeness asks whether the excerpt preserves the claim-proof bond. A self-contained excerpt could present only a scholar's conclusion with enough context to understand it, while violating evidential completeness by omitting the dalīl.
  - **Layer integrity (سلامة الطبقات):** In multi-layer texts, the matn-sharḥ-ḥāshiya dependency chain is an additional constraint. An excerpt that is self-contained, attributed correctly, and grammatically sound can still be corrupt if it contains ḥāshiya text without the sharḥ it comments on. No existing stack value captures this.
- **Proposed amendment:** Add "evidential completeness" between "grammatical integrity" and "self-containment." Add "layer integrity" between "attribution safety" and "dialogue preservation" (it is nearly as important as attribution because a ḥāshiya without its sharḥ is as misleading as a quote without its attribution).
- **Confidence:** HIGH for evidential completeness. MEDIUM for layer integrity (it may be subsumable under a more general principle).

---

**SCH-011: No scenario exists where self-containment should override attribution safety**

- **Severity:** LOW (confirming correctness)
- **Protocol section:** §5.4
- **Scholarly reasoning:** The task asks whether self-containment should ever override attribution safety. After constructing multiple scenarios, the answer is **no**. Attribution safety prevents the catastrophic error of attributing an opinion to the wrong scholar or to the author when it belongs to someone the author is refuting (FP-14, speaker-role inversion). Self-containment prevents the serious but less dangerous error of producing an excerpt that requires external context. A misattribution corrupts the reader's understanding of *who holds what position* — which in fiqh determines which school's ruling is applied, and in ʿaqīdah determines what belief is orthodox. An incomplete excerpt that correctly attributes its content merely requires the reader to seek additional context. The ranking is correct.
- **Confidence:** HIGH.

---

### Evaluation 4: The CC-before-Gemini expansion problem (§4.3 → §4.4)

**SCH-012: CC will systematically misidentify natural atoms due to lack of genre awareness**

- **Severity:** CRITICAL
- **Protocol section:** §4.3 Stage 3 (EXPANDED)
- **Scholarly reasoning:** CC drafts the full expansion including scope, exceptions, examples, and implementation hypothesis before any scholarly review. The specific error types CC will make, each requiring Islamic scholarly knowledge to detect:
  - **Wrong atom boundaries in ḥadīth sharḥ:** CC will treat the individual ḥadīth as atomic because it looks like a discrete paragraph. The scholarly knowledge that the bāb (chapter) is the correct atom — because al-Bukhārī encodes his fiqh in the tarjamah — requires understanding *fiqh al-Bukhārī fī tarājimih*, a sub-discipline CC cannot access.
  - **Missing taqsīm completeness:** CC cannot recognize that "وهو ثلاثة أقسام" demands three sub-sections be kept together because CC lacks pattern recognition for Arabic taxonomic formulas.
  - **Wrong layer attribution in multi-layer texts:** CC will not know whether "qawluhu" (قوله) introduces matn text or sharḥ text without understanding the specific commentary tradition.
  - **Fatwa question-answer separation:** CC may treat the suʾāl and jawāb as separate paragraphs because they often appear under separate headings.
- **Damage cascade:** Per anchoring bias research, Gemini's Stage 4 review will be anchored to CC's draft. If CC proposes the wrong atom (individual ḥadīth instead of bāb), Gemini must recognize this as wrong AND override CC's draft. The anchoring effect means Gemini is more likely to approve with minor modifications than to fundamentally restructure the atom definition.
- **Proposed amendment:** Add a "scholarly uncertainty flag" requirement to Stage 3. CC must mark any expansion element where it lacks domain knowledge with `[SCHOLARLY_CHECK_NEEDED]` and explicitly state what it does not know. Example: "This atom appears to be one ḥadīth + its commentary, but I cannot verify whether the bāb heading is semantically integral. [SCHOLARLY_CHECK_NEEDED: Is the bāb the correct atomic unit in this genre?]"
- **Confidence:** HIGH. The anchoring bias concern is well-established in cognitive science and directly applicable here.

---

**SCH-013: No lightweight scholarly sanity check between Stage 2 and Stage 3**

- **Severity:** HIGH
- **Protocol section:** §4.3 → §4.4 pipeline
- **Scholarly reasoning:** The current flow is: owner feedback → CC captures atom (Stage 2) → CC drafts full expansion (Stage 3) → Gemini reviews (Stage 4). The gap between capture and expansion is where CC makes structural decisions about the text without scholarly input. A lightweight "genre identification" step — where the text's science, structural family (argument/narrative/entry/rule/commentary), and layer position (matn/sharḥ/ḥāshiya) are identified before CC attempts expansion — would prevent the most damaging systematic errors.
- **Proposed amendment:** Insert a "Stage 2.5: Genre Identification" step. Before CC drafts the expansion, it must: (1) identify the science category from the expanded 12-category list; (2) identify the structural family [ARG/NAR/ENT/RUL/COM]; (3) identify the text layer (matn/sharḥ/ḥāshiya/taʿlīqa); (4) if uncertain about any of these, flag for Gemini pre-check before proceeding to Stage 3. This is lightweight (three classification decisions) but prevents the entire downstream expansion from being built on wrong structural assumptions.
- **Confidence:** HIGH.

---

### Evaluation 5: Series-specific expansion templates (F vs. G vs. SC)

**SCH-014: SC-series needs multi-layer text handling that F and G do not**

- **Severity:** HIGH
- **Protocol section:** Expansion template (uniform across series)
- **Scholarly reasoning:** SC-series (Scholarly Context) questions deal with how excerpts reference other texts, how attribution works across layers, and how self-containment interacts with argument structure. These are precisely the concerns most affected by multi-layer text complexity. When an SC-series atom touches a ḥāshiya that comments on a sharḥ that explains a matn, the expansion must specify which layer the atom operates on, what the layer dependencies are, and how the atom's self-containment interacts with each layer. F-series (Foundational) atoms deal with case judgments where the layer question is simpler — the ruling exists at one layer. G-series (Generalization) atoms abstract across cases and may need to track whether the generalization holds across layers.
- **Proposed amendment:** Add a layer-awareness section to the SC-series expansion template: "For multi-layer texts, identify: (a) which layer this atom primarily operates on; (b) what matn text is required as context for the sharḥ/ḥāshiya content; (c) whether the atom's self-containment requirement extends to including lower layers' content."
- **Confidence:** MEDIUM. The exact template design depends on the specific texts in the library, but the need for differentiation is clear.

---

**SCH-015: F-series needs explicit dalīl-ḥukm bond preservation that G-series does not**

- **Severity:** MEDIUM
- **Protocol section:** Expansion template (uniform across series)
- **Scholarly reasoning:** F-series atoms are foundational case judgments — a ḥukm (ruling) on a specific masʾalah. The primary scholarly risk is separating the ḥukm from its dalīl (evidence). G-series atoms generalize across cases — the risk shifts to incomplete induction (missing cases from the generalization). SC-series atoms contextualize — the risk is broken cross-references or lost attribution chains. A uniform template checks for all these risks equally, but each series should **emphasize** the risk most relevant to it.
- **Proposed amendment:** Add series-specific risk emphasis: F-series template adds "PRIMARY RISK: dalīl-ḥukm separation. Verify that every ruling in this atom is accompanied by at least one piece of evidence." G-series adds "PRIMARY RISK: incomplete induction. Verify that the generalization covers all the cases the author intended." SC-series adds "PRIMARY RISK: attribution chain breakage. Verify that every quoted opinion is traceable to its source scholar."
- **Confidence:** MEDIUM.

---

### Evaluation 6: Arabic text handling gaps

**SCH-016: Multi-layer text handling entirely absent from the expansion template**

- **Severity:** CRITICAL
- **Protocol section:** §4.3 expansion template
- **Scholarly reasoning:** The classical Arabic scholarly tradition operates as a layered textual ecosystem: matn (base text, often a mukhtaṣar for memorization) → sharḥ (commentary, explaining and expanding) → ḥāshiya (super-commentary, critiquing and adding evidence) → taʿlīqa (notes). In the Ḥanafī legal tradition alone, the chain runs: *Tanwīr al-Abṣār* → *al-Durr al-Mukhtār* → *Radd al-Mukhtār* (Ibn ʿĀbidīn). The layers form an **inseparable dependency chain**: the ḥāshiya references specific words in the sharḥ using "qawluhu" (قوله), which in turn references specific words in the matn. In manuscripts, these layers are distinguished by red vs. black ink, overlining, or marginal placement with sigla ص (matn) and ش (sharḥ). In modern print, they use bold/brackets for matn and footnotes for ḥāshiya.
- **Damage cascade:** Without layer-awareness, the expansion template cannot specify which layer an atom applies to. An atom targeting the ḥāshiya layer will be drafted without requiring the corresponding sharḥ text, producing excerpts that say "the Shāriḥ's statement that..." with no sharḥ present. The reader encounters a commentary on a commentary on a text, with neither the commentary nor the text included.
- **Proposed amendment:** Add a "Layer Position" field to the expansion template: "If this text has multiple layers (matn/sharḥ/ḥāshiya/taʿlīqa), specify: (a) which layer is the TARGET of this atom; (b) which LOWER layers must be included for the target layer to be intelligible; (c) whether the atom's boundary in the target layer aligns with natural boundaries in the lower layers." Add to Atomic Integrity Risk: "Multi-layer dependency: An excerpt at layer N must include the corresponding text at all layers below N, down to the matn segment that anchors the discussion."
- **Confidence:** HIGH. This is structurally necessary for any text in the sharḥ tradition, which is the majority of the corpus.

---

**SCH-017: Honorific handling unaddressed — CC will corrupt or strip them**

- **Severity:** HIGH
- **Protocol section:** §4.3 expansion template; arabic-scholarly-conventions.md (partially addresses this but the expansion template does not reference it)
- **Scholarly reasoning:** When CC drafts expansions mentioning scholars by name, it must preserve honorifics: ṣallā Allāhu ʿalayhi wa-sallam (ﷺ) for the Prophet, raḍiya Allāhu ʿanhu for Companions, raḥimahu Allāh for deceased scholars. The honorific is culturally and grammatically **bound to the name** — it is not separable metadata. Omitting the Prophet's honorific is considered sinful by many scholars (Qurʾān 33:56 commands sending blessings). The Unicode ligature ﷺ (U+FDFA) requires specific handling. Abbreviations (ص for ṣallā Allāhu ʿalayhi wa-sallam) are tolerated but criticized by major scholars including Ibn Bāz.
- **Damage cascade:** CC, lacking Islamic scholarly training, will treat honorifics as optional parenthetical text. In drafting expansion examples, CC may write "Ibn Taymiyyah said..." without "raḥimahu Allāh," producing a template that signals to the excerpting engine that honorifics are dispensable. The excerpting engine then strips them for "cleanliness," and every excerpt in the library omits a fundamental feature of Islamic scholarly etiquette.
- **Proposed amendment:** Add to the expansion template: "Honorific preservation: When this atom mentions any scholar, prophet, or companion by name, verify that all honorifics present in the source text are preserved exactly as written (full or abbreviated form). Honorifics are NOT metadata — they are integral text. The expansion must not paraphrase or omit them."
- **Confidence:** HIGH. The arabic-scholarly-conventions.md file covers this at the engine level, but the expansion template (where CC operates) does not reference it.

---

**SCH-018: Copyist-author confusion needs expansion template flagging, not just engine rules**

- **Severity:** MEDIUM
- **Protocol section:** §4.3 expansion template; arabic-scholarly-conventions.md
- **Scholarly reasoning:** The arabic-scholarly-conventions.md file documents the colophon trap (copyist vs. author confusion). But the expansion template — where CC drafts atoms — has no trigger to flag this risk. The disambiguation requires knowing that "katabahu" (كتبه) is ambiguous (could be author or copyist), "taʾlīf" (تأليف) indicates authorship, and "nasakhahu" (نسخه) or "bi-khaṭṭ" (بخطّ) indicates copying. The double-colophon trap (where an earlier colophon is copied into a later manuscript, creating two colophons with different dates and names) adds further complexity. CC cannot distinguish these formulas.
- **Proposed amendment:** Add to the expansion template's Atomic Integrity Risk section: "If this atom touches a colophon or attribution block, flag for scholarly review: does 'written by' refer to the author or the copyist? Key disambiguators: تأليف/صنّفه/جمعه = author; نسخه/بخطّ/على يد العبد الحقير = copyist; كتبه = AMBIGUOUS. Double colophons (two dates, two names) indicate copied colophon — the earlier date belongs to a prior copyist, not the author."
- **Confidence:** HIGH.

---

**SCH-019: Transmission formula handling needs explicit expansion template integration**

- **Severity:** HIGH
- **Protocol section:** §4.3 expansion template; FP-11 (sanad-matn awareness)
- **Scholarly reasoning:** FP-11 addresses isnād-matn awareness and the arabic-scholarly-conventions.md documents transmission formulas. But the expansion template does not require CC to flag when an atom touches ḥadīth content and therefore needs isnād-matn integrity checking. There are **eight ranked transmission methods**: samāʿ (hearing, strongest) → qirāʾa (reading back) → ijāza (license) → munāwala (handing over) → mukātaba (correspondence) → iʿlām (notification) → waṣiyya (bequest) → wijāda (finding, weakest). The specific formula used (ḥaddathanā vs. ʿan vs. qāla) indicates transmission strength. The formula "ʿan" (عن) is the most ambiguous — from a narrator known for tadlīs (concealment of intermediaries), it can render the ḥadīth weak. Changing ḥaddathanā to ʿan in processing would downgrade a strong transmission to an ambiguous one.
- **Damage cascade:** If the expansion template does not flag ḥadīth content for isnād-matn integrity checking, CC may draft atoms that split isnād chains (losing the connection between transmitter and transmitted), truncate transmission formulas (losing strength indicators), or treat formulas as connective tissue to be trimmed. The corrupted isnād then produces wrong ḥadīth authentication, which produces wrong legal rulings.
- **Proposed amendment:** Add to the expansion template: "Ḥadīth content trigger: If this atom contains or touches ḥadīth text (identifiable by transmission formulas: حدّثنا / أخبرنا / سمعت / عن / قال), invoke FP-11 isnād-matn integrity check. Transmission formulas are structurally integral to the isnād — they CANNOT be removed, altered, or truncated. Each formula links exactly two narrators and indicates transmission strength."
- **Confidence:** HIGH.

---

## 3. Overall scholarly assessment

**Protocol integrity score: 5/10.** The protocol is architecturally sound — its stage-based pipeline, disagreement resolution framework, and severity classification system are well-designed. The structural engineering is good. But the **Islamic scholarly content knowledge** embedded in the protocol covers roughly one-third of what it needs to cover. The science list misses four structurally distinct disciplines. The indivisible-unit inventory covers 5 of 21 types. The most common text structure in the entire classical Arabic scholarly corpus — the sharḥ-matn pair — is not in the indivisible-unit list. The expansion template has no awareness of multi-layer texts, which constitute the majority of the tradition.

**The single most dangerous scholarly gap is SCH-005: the missing sharḥ-matn pair in the Atomic Integrity Risk section.** Commentary literature is the bulk of classical Islamic scholarship. Every ḥāshiya, every sharḥ, every taʿlīqa depends on the text it comments on. Without this as a recognized indivisible unit, the excerpting engine will systematically produce excerpts where the commentary is severed from the text it explains. The student will read "the author's intention here is..." without ever seeing what "here" refers to. This is not an edge case — it is the default case for the majority of texts in a classical Islamic library.

**The single most valuable improvement is SCH-013: inserting a lightweight "Genre Identification" step (Stage 2.5) between atom capture and expansion.** Three classification decisions — science category, structural family, and text layer — would prevent the entire downstream expansion from being built on wrong structural assumptions. This is cheap to implement (three fields), dramatically reduces CC's error surface, and gives Gemini a structured framework for review rather than a free-form expansion to anchor on. Combined with SCH-012's scholarly uncertainty flags, this transforms the CC-before-Gemini problem from "CC guesses, Gemini corrects" to "CC classifies and flags uncertainty, Gemini validates and fills gaps."

### Summary of all findings by severity

| Severity | Count | Finding IDs |
|----------|-------|------------|
| CRITICAL | 5 | SCH-001, SCH-005, SCH-006, SCH-012, SCH-016 |
| HIGH | 8 | SCH-002, SCH-007, SCH-009, SCH-010, SCH-013, SCH-014, SCH-017, SCH-019 |
| MEDIUM | 5 | SCH-003, SCH-004, SCH-008, SCH-015, SCH-018 |
| LOW | 1 | SCH-011 |

The five CRITICAL findings share a common pattern: the protocol's engineering framework is correct but its Islamic scholarly content inputs are incomplete. The framework does exactly what it should — check atoms against a science list, check atoms against an indivisible-unit list, draft expansions using templates. But the science list is too short, the indivisible-unit list is too short, and the templates lack awareness of how the majority of classical Arabic scholarly texts are actually structured. Filling these content gaps within the existing framework would raise the protocol's integrity score to approximately **8/10**, with the remaining 2 points requiring live testing against actual texts from each genre to calibrate atom sizes and boundary rules.