# DR Relay Queue — Batch 2 (Taxonomy Research Gaps from DR39)

**Generated:** 2026-04-07 (Session 14)
**Status:** READY FOR RELAY
**Source:** DR39 (Claude DR) identified 10 taxonomy tree research gaps across aqidah, sarf, balagha, and cross-science boundaries.
**Target:** Gemini DR for all prompts (Islamic scholarly domain expertise, taxonomy tree design)
**File bundle needed:** For each prompt, upload the relevant tree YAML file + `engines/taxonomy/SPEC.md` + `TAXONOMY_TREE_PROTOCOL.md`

**Relay priority:** Top-to-bottom. Prompts are grouped by science. Owner relays as capacity allows.

---

## RQ-B2-001: Gemini DR — Aqidah Tree: حجية فهم السلف vs إجماع السلف

**Priority:** HIGH
**Unblocks:** Aqidah tree v2.0 installation (5 of 7 pending decisions)
**File bundle:** Upload `library/sciences/aqidah/tree_history/aqidah_v0_2.yaml`

```
You are an expert in aqidah (Islamic creed) and the methodology of Salafi and traditional Sunni theology. I am building a taxonomy tree for aqidah to classify scholarly excerpts.

QUESTION: Is حجية فهم السلف (the authoritativeness of the Salaf's understanding) distinct enough from إجماع السلف (consensus of the Salaf) to warrant a separate leaf node in the tree?

CONTEXT:
- إجماع السلف is a recognized concept in usul al-fiqh (the consensus of the early Muslim generations as a binding proof)
- حجية فهم السلف is used in contemporary aqidah discourse, especially by Salafi scholars, to argue that the Companions' understanding of creedal matters is authoritative beyond mere consensus
- The question is whether these are two names for the same concept, or whether حجية فهم السلف captures something that إجماع does not

WHAT I NEED:
1. Are these the same concept with different names, or genuinely distinct?
2. If distinct: what scholarly content would fall under حجية فهم السلف that would NOT fall under إجماع السلف? Give real examples from classical aqidah texts.
3. If the same: which term is the canonical one to use as the leaf name?
4. Key classical and contemporary sources that discuss this distinction (with Arabic titles and author names).
```

---

## RQ-B2-002: Gemini DR — Aqidah Tree: الأسماء والصفات Proportionality

**Priority:** MEDIUM
**Unblocks:** Aqidah tree v2.0 leaf count calibration
**File bundle:** Upload `library/sciences/aqidah/tree_history/aqidah_v0_2.yaml`

```
You are an expert in aqidah taxonomy. I am calibrating the leaf count for the الأسماء والصفات (Divine Names and Attributes) branch of an aqidah taxonomy tree.

QUESTION: The current draft has 20 leaves under الأسماء والصفات. Is this proportionally correct relative to the other aqidah branches, or is it over/under-represented?

CONTEXT:
- The full aqidah tree currently has 30 leaves total (v0.2)
- Post-cold-read audit draft has 141 leaves
- الأسماء والصفات is the largest single topic in most aqidah textbooks, but the tree covers ALL of aqidah: الإيمان, القدر, النبوة, السمعيات, الفرق, etc.
- The benchmark: nahw tree has 183 leaves with careful proportionality

WHAT I NEED:
1. In canonical aqidah textbooks (العقيدة الطحاوية, لمعة الاعتقاد, الواسطية, شرح الأصفهانية), approximately what percentage of content is devoted to الأسماء والصفات vs other topics?
2. Based on that, should 20/141 leaves (14%) be adjusted? If so, to what range?
3. Are there sub-topics within الأسماء والصفات that could be collapsed (too granular) or that are missing?
```

---

## RQ-B2-003: Gemini DR — Aqidah Tree: الكهانة/العرافة vs السحر

**Priority:** MEDIUM
**Unblocks:** Aqidah tree pending decision #3
**File bundle:** Upload `library/sciences/aqidah/tree_history/aqidah_v0_2.yaml`

```
You are an expert in aqidah and Islamic legal methodology. I am building a taxonomy tree and need to decide whether الكهانة والعرافة (divination/fortune-telling) and السحر (sorcery/magic) should be separate leaf nodes or combined.

QUESTION: Are الكهانة/العرافة and السحر distinct enough in scholarly treatment to warrant separate taxonomy leaves?

WHAT I NEED:
1. In classical aqidah texts across traditions — كتاب التوحيد (Muhammad ibn Abd al-Wahhab), إحياء علوم الدين (al-Ghazali, Book of التوبة on السحر), تفسير القرطبي (on the verse of Harut and Marut), المغني (Ibn Qudamah, كتاب الردة section on السحر) — are الكهانة and السحر treated in separate chapters or as part of one discussion?
2. What is the key scholarly distinction? (e.g., السحر involves actual effect vs الكهانة is knowledge claim?)
3. Do fiqh texts (أحكام السحر, أحكام الكهانة) treat them separately with different rulings?
4. Recommendation: one leaf or two? With reasoning from the scholarly literature across multiple traditions.
```

---

## RQ-B2-004: Gemini DR — Aqidah Tree: أعمال القلوب Leaf Count

**Priority:** LOW
**Unblocks:** Aqidah tree calibration
**File bundle:** Upload `library/sciences/aqidah/tree_history/aqidah_v0_2.yaml`

```
You are an expert in aqidah and Islamic spirituality (tasawwuf/tazkiyah). The current aqidah tree draft has 6 leaves under أعمال القلوب (actions of the heart): التوكل, الخوف, الرجاء, المحبة, الإخلاص, الصبر.

QUESTION: Is 6 leaves appropriate for أعمال القلوب within an aqidah context (as opposed to a tazkiyah/tasawwuf context)?

WHAT I NEED:
1. In aqidah-specific texts (not tasawwuf), how many أعمال القلوب are typically discussed?
2. Should some of these 6 be merged (e.g., الخوف والرجاء are often paired)?
3. Are any critical ones missing that aqidah texts specifically address (e.g., الشكر, الإنابة, الخشية as distinct from الخوف)?
4. The key distinction: aqidah discusses these as matters of creed (إيمان), not as spiritual stations (مقامات). Does this affect which ones deserve leaves?
```

---

## RQ-B2-005: Gemini DR — Aqidah Tree: الطائفة المنصورة

**Priority:** LOW
**Unblocks:** Aqidah tree pending decision #5
**File bundle:** Upload `library/sciences/aqidah/tree_history/aqidah_v0_2.yaml`

```
You are an expert in aqidah. I need to decide whether الطائفة المنصورة (the Victorious Sect / Saved Sect) deserves its own leaf in an aqidah taxonomy tree.

QUESTION: Is الطائفة المنصورة a distinct enough aqidah concept to warrant a dedicated leaf node?

CONTEXT:
- The hadith "لا تزال طائفة من أمتي ظاهرين على الحق" is a foundational aqidah text
- This topic often overlaps with الفرق والمذاهب (sects and schools) and أهل السنة والجماعة (Ahl al-Sunnah)
- Some aqidah texts treat it as a major standalone topic; others embed it within the الفرق discussion

WHAT I NEED:
1. In major aqidah textbooks, is الطائفة المنصورة given its own chapter/section, or is it always embedded within الفرق?
2. What unique scholarly content would fall under this leaf that doesn't belong under الفرق?
3. Recommendation: standalone leaf, sub-leaf under الفرق, or merge? With textual evidence.
```

---

## RQ-B2-006: Gemini DR — Sarf Tree: نشأة علم الصرف وتطوره

**Priority:** MEDIUM
**Unblocks:** Sarf tree v2.1 pending decision #1
**File bundle:** Upload `library/sciences/sarf/tree_history/sarf_v1_0.yaml`

```
You are an expert in Arabic morphology (علم الصرف) and the history of Arabic linguistic sciences. I am building a taxonomy tree for sarf.

QUESTION: Does نشأة علم الصرف وتطوره (the origin and development of the science of sarf) deserve its own leaf node in a sarf taxonomy tree?

CONTEXT:
- Many sarf textbooks begin with a مقدمة that discusses the history of the science
- This content is about the science itself (meta-level), not about morphological rules
- It includes: who founded the science, key works, methodology development, relationship to nahw

WHAT I NEED:
1. In the major sarf textbooks (شرح الملوكي for Ibn Ya'ish, المنصف for Ibn Jinni, شذا العرف for al-Hamlawi), is this treated as a standalone topic or just an introductory paragraph?
2. Would a scholar studying sarf systematically need a dedicated entry for this topic, or is it always introductory context?
3. Recommendation: leaf, introductory note (not a leaf), or sub-leaf under مقدمات? With evidence.
```

---

## RQ-B2-007: Gemini DR — Sarf Tree: تصريف الأفعال vs أزمنة الفعل

**Priority:** HIGH
**Unblocks:** Sarf tree v2.1 pending decision #2 (affects tree structure)
**File bundle:** Upload `library/sciences/sarf/tree_history/sarf_v1_0.yaml`

```
You are an expert in Arabic morphology (علم الصرف). I need to determine whether two closely related sarf topics are genuinely distinct or should be merged.

QUESTION: Is تصريف الأفعال بعضها من بعض (deriving verbs from one another — e.g., form I→II→III) distinct from أزمنة الفعل (verb tenses — past/present/imperative)?

CONTEXT:
- تصريف الأفعال covers: الأبواب (verb forms I-X), derivation patterns, how to derive one form from another
- أزمنة الفعل covers: الماضي, المضارع, الأمر, and how the same root appears in different tenses
- These are related but potentially different axes: تصريف = horizontal (across forms), أزمنة = vertical (across tenses)

WHAT I NEED:
1. In classical sarf texts, are these treated as one topic or two? Cite specific chapters.
2. Could a scholarly excerpt about تصريف الأبواب be cleanly classified under one of these two leaves? Or does it always require both?
3. Recommendation: two separate leaves, merge into one, or restructure as parent/children?
```

---

## RQ-B2-008: Gemini DR — Sarf Tree: Standalone الحذف

**Priority:** LOW
**Unblocks:** Sarf tree v2.1 pending decision #3
**File bundle:** Upload `library/sciences/sarf/tree_history/sarf_v1_0.yaml`

```
You are an expert in Arabic morphology. I need to determine whether الحذف (elision/deletion in morphology) is substantial enough as a standalone concept to deserve its own leaf in a sarf taxonomy tree.

QUESTION: Is الحذف in sarf a standalone topic or is it always discussed as part of other morphological rules?

CONTEXT:
- الحذف appears in multiple sarf contexts: حذف حرف العلة (weak letter deletion), حذف همزة الوصل, حذف نون التوكيد, etc.
- Some texts treat الحذف as a unified topic; others discuss each type of deletion within the relevant morphological context

WHAT I NEED:
1. Do any classical sarf texts have a dedicated chapter for الحذف as a unified concept?
2. If a student wanted to study "all deletion rules in sarf," would they find a single place to look, or must they visit 5+ different sections?
3. Recommendation: standalone leaf that collects all deletion rules, or distribute deletion across the relevant morphological topics?
```

---

## RQ-B2-009: Gemini DR — Balagha Tree: المجاز العقلي Dual Placement

**Priority:** HIGH
**Unblocks:** Balagha tree architecture (affects branch structure)
**File bundle:** Upload `library/sciences/balagha/tree_history/balagha_v1_0.yaml`

```
You are an expert in Arabic rhetoric (علم البلاغة) and the competing organizational frameworks of the classical rhetoricians. I need to resolve a placement conflict in my balagha taxonomy tree.

QUESTION: Should المجاز العقلي (intellectual/rational metaphor) be placed under:
- (A) البيان > المجاز (al-Sakkaki's framework — places it with other forms of metaphor), OR
- (B) المعاني > أحوال الإسناد (al-Qazwini's framework — places it under sentence-level meaning because it involves attribution of an action to other than its true agent)

CONTEXT:
- السكاكي (d. 626 AH) in مفتاح العلوم treats المجاز العقلي alongside المجاز اللغوي under البيان
- القزويني (d. 739 AH) in التلخيص moves it to المعاني because the metaphor operates at the sentence level (إسناد الفعل إلى غير فاعله الحقيقي)
- Most later textbooks follow القزويني, but الإسناد المجازي is still discussed in بيان sections of some modern curricula

WHAT I NEED:
1. Which framework do the majority of classical and modern balagha textbooks follow for المجاز العقلي?
2. In a tree designed for student study (not historical accuracy), which placement produces fewer cross-reference complications?
3. If placed under المعاني, does the البيان section need a cross-reference leaf or note?
4. Concrete recommendation with scholarly justification.
```

---

## RQ-B2-010: Gemini DR — Cross-Science: Sarf/Nahw Boundary Rulings

**Priority:** HIGH
**Unblocks:** Cross-science routing rules for sarf/nahw overlap
**File bundle:** Upload `library/sciences/sarf/tree_history/sarf_v1_0.yaml` + `reference/research/nahw_v2_0_final.yaml`

```
You are an expert in Arabic grammar (nahw) and morphology (sarf) and the historical boundary between these two sciences. I am building separate taxonomy trees for nahw and sarf and need formal boundary rulings for overlapping topics.

QUESTION: What are the formal scholarly rules for drawing the boundary between nahw and sarf content?

CONTEXT:
- Classical scholars disagree on the boundary. Some define sarf as dealing with word-internal structure (بنية الكلمة) and nahw as dealing with word-final markers (إعراب) and sentence structure.
- Several topics exist in BOTH trees currently: e.g., المبني والمعرب (built/declined), التعريف والتنكير, الاشتقاق
- My nahw tree has 183 leaves (v2.0, validated). My sarf tree has 226 leaves (v1.0, unvalidated).

WHAT I NEED:
1. What is the classical scholarly definition of the boundary? (Cite Ibn Jinni's الخصائص, Sibawayh's الكتاب, or other foundational sources)
2. For the following overlap topics, which tree should own them and why:
   - المبني والمعرب
   - التعريف والتنكير
   - الاشتقاق
   - التثنية والجمع (dual and plural formation — morphological change vs syntactic role)
   - النسب (attribution — morphological suffix vs syntactic usage)
3. Should overlap topics exist in BOTH trees (with cross-references) or in ONE tree (with the other tree pointing to it)?
4. A general rule I can apply to future overlap cases.
```

---

## Relay Instructions for Owner

**Total: 10 prompts, all Gemini DR**

Each prompt needs:
1. Open a Gemini Deep Research session
2. Upload the file bundle listed under each prompt
3. Copy-paste the prompt text between the ``` markers
4. Save the response as a markdown file
5. Tell CC the file path when done

**Grouping suggestion:** The 5 aqidah prompts (RQ-B2-001 through RQ-B2-005) can be relayed together if Gemini handles them well. The sarf prompts (006-008) form a second batch. RQ-B2-009 (balagha) and RQ-B2-010 (cross-science) are highest-impact and should be prioritized.

**Priority order:** RQ-B2-010 > RQ-B2-009 > RQ-B2-007 > RQ-B2-001 > rest
