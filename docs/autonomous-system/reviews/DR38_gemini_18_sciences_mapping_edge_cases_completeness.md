# DR38 — Gemini DR: 18 Islamic Sciences Mapping + Edge Cases + Completeness Criteria

**Source:** Gemini Deep Research (prompt 3 of 8 — DR-DESIGN-03)
**Date:** 2026-04-07
**Topic:** Mapping DR research to 18 sciences, dangerous excerpting edge cases, scholarly completeness criteria

---

Advanced Methodological Framework for the Automated Parsing and Extraction of Classical Islamic Sciences

The ambitious scope of the Khizanat Rayan (KR) project represents a critical convergence of classical Islamic epistemology (ulum al-islamiyya) and contemporary digital humanities. The automation of knowledge extraction from classical Arabic texts requires an architecture that moves beyond rudimentary string matching and keyword recognition. The Arabic language is characterized by a highly inflected, nonconcatenative morphology, extensive dialectical variance, and a deep historical layering of vocabulary. When applied to the corpus of Islamic scholarly texts, these linguistic challenges are compounded by the complex structural conventions of the genres themselves, such as the interleaving of sacred scripture with human commentary, the rigid formulas of transmission chains, and the dialectical structures of theological treatises.

To successfully engineer an autonomous system capable of extracting structured scholarly knowledge across seven distinct engines, the foundational extraction layer must possess a profound understanding of text boundaries, stylistic shifts, and contextual dependencies. The misidentification of a boundary in a legal or theological text does not merely result in a truncated sentence; it can fundamentally alter the normative ruling or attribute heretical views to orthodox scholars. The ensuing analysis provides an exhaustive roadmap for the Deep Research (DR) generation system, mapping the distinct architectures of the eighteen primary Islamic sciences, identifying the most dangerous edge cases in automated excerpting, and establishing rigorous scholarly criteria for textual completeness based on classical methodologies.

## Mapping Deep Research to the Eighteen Islamic Sciences

### 1. Tafsir (Quranic Exegesis) / علم التفسير

**Unique Structures:** Exegetical literature is characterized by the continuous, microscopic interleaving of sacred scriptural text (matn al-Qur'an) and human commentary (sharh). This structure frequently shifts between primary scripture, linguistic parsing, historical narratives, and legal derivation, often within a single paragraph.

**Classification Challenges:** The primary challenge lies in differentiating the overarching methodological sub-genres, specifically distinguishing between narrative-based exegesis (tafsir bi-al-ma'thur), which relies heavily on transmission chains, and rational or analytical exegesis (tafsir bi-al-ra'y), which relies on syllogistic reasoning and linguistic derivation.

**Boundary Challenges:** Establishing the precise boundary of a tafsir unit is exceedingly difficult when an exegete digresses into an extensive grammatical treatise or a multi-page theological tangent before returning to the exegesis of the primary verse. The boundary must encapsulate the digression while maintaining the primary verse as the anchor.

**Cross-References:** Tafsir is an inherently encyclopedic science. It exhibits dense intertextuality, heavily referencing Lugha for root definitions, Hadith for prophetic context, Asbab al-Nuzul for historical triggers, and Balagha for rhetorical analysis.

**Top DR Questions:**
1. What sequence-labeling models and contextual embeddings (such as AraBERT or CamelBERT) are most effective for detecting the precise syntactic boundary between a Qur'anic citation and the author's immediate grammatical or theological commentary?
2. How can the pipeline computationally recognize thematic unities (munasabat) that link multiple consecutive verses into a single coherent extraction block, preventing the arbitrary fragmentation of interconnected concepts?
3. What algorithms can reliably identify and extract embedded occasions of revelation (asbab al-nuzul) and map them as metadata to the primary verse?

### 2. Hadith (Prophetic Traditions) / علم الحديث

**Unique Structures:** The classical hadith format is rigidly bipartite, consisting of the chain of human transmission (isnad) and the substantive narrative text (matn). Texts frequently chain multiple isnads to a single matn or fracture a single matn across various isnads to demonstrate corroboration (shawahid).

**Classification Challenges:** Accurately categorizing the authenticity grade (e.g., sahih, hasan, da'if) poses a challenge when the author employs non-standard, highly contextual terminology, or when the pipeline must identify specific sub-types of transmission gaps, such as mursal (missing the Companion) or mu'allaq (suspended).

**Boundary Challenges:** Identifying the precise textual pivot where the isnad terminates and the matn initiates is computationally complex, particularly when standard transmissive verbs (such as qala or haddathana) appear organically within the narrative of the matn itself, triggering false positives for boundary detectors.

**Cross-References:** There are extensive and critical linkages to Ilm al-Rijal (for the evaluation of the narrators within the chain) and Fiqh (for the extraction of legal rulings from the narrative payload).

**Top DR Questions:**
1. How can Named Entity Recognition (NER) models be optimized within a Knowledge Graph framework to avoid conflating narrator names in the isnad with historical figures mentioned within the substantive matn?
2. What statistical NLP markers reliably indicate the transition from isnad validation and structural criticism to the substantive commentary on the tradition?
3. How can the system construct multi-directed graph structures to represent the complex interactions and corroborating chains (mutaba'at) among narrators of the same hadith?

### 3. Fiqh (Jurisprudence) / علم الفقه

**Unique Structures:** Legal treatises are rigorously structured around the mas'ala (the specific legal case or issue). The discourse typically progresses systematically through the statement of the issue, the presentation of the dominant school position, the listing of dissenting views (ikhtilaf), the evidentiary proofs (adillah), and the author's preferred ruling (tarjih).

**Classification Challenges:** The system must differentiate between a binding legal verdict (fatwa), a theoretical legal exploration (fardiyyat), and the historical documentation of a rival school's obsolete or rejected position.

**Boundary Challenges:** Excerpting must capture the entirety of a mas'ala. Truncating a text before the final tarjih or failing to capture the restrictive conditioning clauses (shart) renders the extracted legal knowledge dangerously incomplete and corrupted.

**Cross-References:** Fiqh exhibits a heavy reliance on Usul al-Fiqh for methodological justification, Hadith for primary evidentiary backing, and Lugha for the semantic interpretation of contractual terminology.

**Top DR Questions:**
1. What dependency parsing architectures can successfully map conditional legal clauses and stipulations back to their corresponding foundational rulings over extended, multi-page text spans?
2. How can the system identify stylistic and syntactic markers that distinguish the author's authoritative conclusion from the preliminary listing of opposing, rejected views?
3. What stylometric features can be leveraged for the automated identification of the specific madhhab (legal school) of a given text based on its internal dialectical patterns?

### 4. Usul al-Fiqh (Principles of Jurisprudence) / علم أصول الفقه

**Unique Structures:** These texts present the theoretical frameworks of the law, heavily reliant on abstract dialectics, foundational legal maxims (qawa'id fiqhiyya), and epistemological categorizations (such as distinguishing the absolute mutlaq from the restricted muqayyad, or the general 'amm from the specific khass).

**Classification Challenges:** The NLP model must distinguish between purely linguistic principles (mabahith al-alfaz) and principles of rational deduction (such as analogical reasoning qiyas or considerations of public interest maslaha) within dense, theoretical prose.

**Boundary Challenges:** Arguments often unfold over several pages in a complex premise-objection-rebuttal format. An excerpt is epistemologically void if it captures the premise or the objection but drops the definitive scholarly rebuttal.

**Cross-References:** There is a deep and pervasive intersection with Ilm al-Kalam (theology) regarding the metaphysical nature of divine command, and Lugha for the semantics of Arabic imperatives and prohibitions.

**Top DR Questions:**
1. How can computational models track the progression of a theoretical argument across multiple paragraphs to ensure an extracted usul concept is fully resolved and not left in a state of suspended dialectic?
2. What linguistic signals differentiate a hypothetical, theoretical legal scenario used purely for illustration from an actual, applied legal ruling?
3. How can the pipeline effectively extract and categorize the five universal legal maxims (al-qawa'id al-khamsah) and their subsidiary corollaries from dense theoretical texts?

### 5. Aqidah (Creed/Theology) / علم العقيدة

**Unique Structures:** Texts in this science are characterized by highly condensed dogmatic assertions structured as articles of faith (matn), which are frequently followed by extensive, heavily layered defensive commentary (sharh) aimed at refuting heterodoxy.

**Classification Challenges:** The system faces the challenge of identifying the specific theological school (e.g., Ash'ari, Maturidi, Athari) based on subtle, highly technical terminological shifts rather than explicit sectarian declarations.

**Boundary Challenges:** Early creeds are highly concise and aphoristic; the danger lies in severing the core theological premise from its immediately following qualifiers or from the verse of the Qur'an cited to substantiate it.

**Cross-References:** Texts frequently reference Ilm al-Kalam for the rational defense of the creed, Hadith for scriptural evidence, and Tafsir for the interpretation of the divine attributes.

**Top DR Questions:**
1. What specific n-gram patterns or lexical markers reliably classify the theological affiliation of an author in unannotated, historical texts?
2. How should the extraction pipeline handle the segmentation of highly condensed, aphoristic statements common in early creedal mutun without losing the connective logic?
3. What techniques can identify when an author is quoting a heterodox view for the purpose of heresiographical documentation versus stating their own belief?

### 6. Tasawwuf (Spirituality/Sufism) / علم التصوف

**Unique Structures:** The literature is highly fluid, featuring allegorical narratives, embedded mystical poetry, spiritual aphorisms (hikam), and sequential, deeply psychological discussions of spiritual stations (maqamat) and passing states (ahwal).

**Classification Challenges:** The primary challenge is separating practical ethical instruction (tazkiyat al-nafs), which aligns closely with standard jurisprudence, from complex, esoteric metaphysical theosophy (irfan), which utilizes a highly distinct vocabulary.

**Boundary Challenges:** The frequent and sudden interjection of mystical poetry within standard prose requires an NLP system capable of handling abrupt shifts in meter, formatting, and semantic density without breaking the excerpt boundary.

**Cross-References:** Frequent citation of Hadith (often focusing specifically on traditions related to asceticism or zuhd) and Tabaqat for anecdotal precedents regarding early ascetics.

**Top DR Questions:**
1. What algorithms best manage the structural transition between normative Arabic prose and embedded, highly symbolic mystical poetry within a single narrative block?
2. How can sentiment analysis and semantic vector spaces be adapted to accurately classify the specialized, often paradoxical, emotive vocabulary used to describe spiritual states?
3. How can the system map the hierarchical progression of spiritual stations as defined by different classical authors?

### 7. Sirah (Prophetic Biography) / علم السيرة

**Unique Structures:** These texts present chronological narratives that are heavily interspersed with pre-Islamic and early Islamic poetry, extensive tribal genealogies (nasab), and highly detailed lists of battle participants and expeditions (maghazi).

**Classification Challenges:** The pipeline must distinguish rigorously authenticated historical reports (possessing full isnads) from widespread but weakly supported narrative embellishments or purely literary accounts.

**Boundary Challenges:** Events are often recounted from multiple overlapping perspectives through different chains of transmission. Determining the boundary of a single historical event when the author weaves three or four different source accounts together into a composite narrative is computationally difficult.

**Cross-References:** The science is heavily dependent on Tarikh for broader historical context and Hadith for the authentication of specific biographical episodes.

**Top DR Questions:**
1. How can timeline extraction tools map overlapping narrative accounts of the same event into a unified, chronologically structured knowledge graph?
2. What are the best practices for structuring extensive, multi-generational genealogical trees embedded within continuous narrative prose?
3. How can the system isolate and extract the poetic elements that serve as historical attestation (shawahid) without disrupting the flow of the historical narrative?

### 8. Tarikh (Islamic History) / علم التاريخ

**Unique Structures:** Classical historiography often utilizes strict annalistic structures organized rigidly by the Hijri year, containing a mix of major political milestones and concluding with the obituaries of notable figures who died that year.

**Classification Challenges:** The system must accurately separate the primary historical and political narrative from the biographical obituaries that typically conclude the entries for each specific year.

**Boundary Challenges:** Excerpting must accurately bind the extracted event to its overarching chronological marker, even if the Hijri year was declared several pages prior to the specific event being extracted.

**Cross-References:** Integrates seamlessly with Tabaqat (for the obituary sections) and Sirah (for early chronological events).

**Top DR Questions:**
1. How can the extraction engine maintain chronological state awareness when an event spans multiple pages without the author explicitly restating the Hijri year?
2. What machine learning approaches best distinguish continuous political historical narratives from the routine biographical notices appended to each annal?
3. How can the pipeline normalize and convert varying textual representations of Islamic dates and months into structured metadata?

### 9. Lugha (Arabic Language/Lexicography) / علم اللغة

**Unique Structures:** Classical dictionary formats are based heavily on triliteral or quadriliteral root systems (judhur), detailing lexical derivation, providing pre-Islamic poetic attestation (shawahid) for validation, and tracking semantic drift over time.

**Classification Challenges:** The system must differentiate the primary, literal definition of a term from its subsequent metaphorical usages or regional, dialectical variations.

**Boundary Challenges:** Ensuring an excerpt for a specific lexical word includes the root definition, the derived forms, and the critical poetic evidence without the extraction bleeding into the next alphabetical root entry.

**Cross-References:** This science is universally referenced by all textual sciences, but is especially foundational for Tafsir and Balagha.

**Top DR Questions:**
1. What structural cues and typographic formatting signals can be utilized to automate the precise segmentation of massive, unstructured lexicons into discrete, root-based entries?
2. How can the system effectively extract and link pre-Islamic poetic attestations to their corresponding semantic definitions, preserving the relationship between the proof and the definition?
3. How can cross-lingual embeddings assist in mapping classical Arabic lexicographical terms to modern semantic equivalents?

### 10. Nahw (Arabic Grammar) / علم النحو

**Unique Structures:** Grammar texts are highly technical, featuring hierarchical breakdowns of syntax, heavily reliant on the analysis of case endings (i'rab), the identification of operatives ('awamil), and the exhaustive listing of rules governing sentence structures.

**Classification Challenges:** The extraction engine must identify whether a text represents the Kufan or Basran grammatical school based on specific technical vocabulary and the methodology of analogical deduction used.

**Boundary Challenges:** Grammatical examples are intimately and inextricably tied to their governing rules; an excerpt is completely void of scholarly utility if it captures the example sentence but truncates the subsequent, detailed syntactic parsing (i'rab).

**Cross-References:** Nahw is foundational for the correct interpretation of Tafsir, Usul al-Fiqh, and Balagha.

**Top DR Questions:**
1. How can modern dependency parsers be trained to computationally map classical Arabic grammatical syntax trees directly from dense textual i'rab descriptions?
2. What are the optimal computational methods for capturing the hierarchical relationship between a macro-grammatical rule and the extensive list of micro-exceptions that invariably follows?
3. How can the pipeline preserve the structural integrity of complex conditional sentences used as grammatical examples?

### 11. Sarf (Arabic Morphology) / علم الصرف

**Unique Structures:** This science focuses strictly on word patterns (awzan), root derivations, the rules of assimilation (idgham), and phonetic transformation (i'lal), often using algebraic-like morphological templates (such as the standard fa-'a-la paradigm).

**Classification Challenges:** The system must distinguish between regular verbal and nominal conjugations and the highly irregular anomalies that require specific phonological justification.

**Boundary Challenges:** An excerpt discussing a specific morphological scale must encompass all paradigm shifts (past, present, imperative, active participle) associated with that scale to remain pedagogically and scholarly coherent.

**Cross-References:** Intimately linked to Lugha for root origins and Nahw for how morphology impacts syntactic position.

**Top DR Questions:**
1. How can morphological templates and abstract roots be represented computationally to allow for automated, highly accurate pattern-matching across diverse textual corpora?
2. What linguistic signals dictate the transition from the explanation of a general morphological rule to the discussion of weak-letter (mu'tall) anomalies?
3. What rule-based NLP techniques are best suited for automating the extraction of conjugation tables from continuous prose?

### 12. Balagha (Arabic Rhetoric) / علم البلاغة

**Unique Structures:** Classical analyses of eloquence are strictly divided into three sub-sciences: Ma'ani (semantics and word order), Bayan (figures of speech, simile, metaphor), and Badi' (rhetorical embellishments), heavily illustrated through curated poetry and Qur'anic verses.

**Classification Challenges:** The computational challenge lies in differentiating between literal intent and the highly varied, nuanced forms of metaphor (majaz), simile (tashbih), or metonymy (kinayah).

**Boundary Challenges:** An excerpt must capture the overarching rhetorical rule, the cited text serving as the example, and the specific authorial breakdown of exactly how the text demonstrates the rule.

**Cross-References:** Extremely vital to Tafsir for demonstrating the miraculous inimitability (i'jaz) of the Qur'an.

**Top DR Questions:**
1. What are the most effective digital humanities approaches for identifying, categorizing, and tagging classical Arabic rhetorical devices within large-scale, unstructured corpora?
2. How does the system handle the extraction of nested metaphors, where multiple rhetorical devices operate simultaneously within a single sentence?
3. How can the pipeline align classical rhetorical taxonomies with modern computational stylistic analysis?

### 13. Mantiq (Logic) / علم المنطق

**Unique Structures:** Texts feature rigid propositional and syllogistic structures, utilizing strict formal phrasing adapted from Hellenistic traditions into Arabic terminology.

**Classification Challenges:** Differentiating purely formal, abstract logical texts from applied logic found organically within theology or jurisprudential theory.

**Boundary Challenges:** A syllogism is entirely invalid and incomprehensible if excerpted without its final conclusion or if the conditional qualifiers of its foundational premises are inadvertently omitted during extraction.

**Cross-References:** Serves as the deep structural underpinning for Falsafa, Ilm al-Kalam, and post-classical Usul al-Fiqh.

**Top DR Questions:**
1. Can rule-based algorithms effectively parse classical Arabic texts to automatically extract formal syllogistic structures and map their logical flow to a formal conclusion?
2. What are the primary formulaic expressions that signify the initiation and resolution of a logical proof in Arabic scholarly writing?
3. How can the system detect logical fallacies explicitly identified and deconstructed by the author?

### 14. Falsafa (Philosophy) / علم الفلسفة

**Unique Structures:** Treatises are characterized by incredibly dense ontological and epistemological argumentation, the extensive use of translated or hybridized Greek terminology, and sustained dialectical reasoning.

**Classification Challenges:** Tracking the evolution of philosophical terms that diverge completely from the standard Arabic lexicon (e.g., using jawhar for substance, or 'arad for accident).

**Boundary Challenges:** Philosophical arguments are often highly protracted, spanning several pages. Identifying the semantic boundaries of a philosophical concept requires tracking specialized vocabulary across extensive spans without losing the thread of the argument.

**Cross-References:** Frequently interacts with, or is actively and aggressively refuted by, Ilm al-Kalam and Aqidah.

**Top DR Questions:**
1. How can semantic modeling map the conceptual shifts of Hellenistic terms as they were adapted and redefined within classical Arabic philosophical discourse?
2. What automated methods can track and extract the continuous, unbroken thread of a philosophical argument that spans an entire chapter or section?
3. How can the system distinguish between Neoplatonic and Aristotelian currents based on term frequency and usage patterns?

### 15. Ilm al-Kalam (Dialectical Theology) / علم الكلام

**Unique Structures:** The ubiquitous use of the dialectical "if they say... then we say" (fa-in qilu... qulna) or "he said... I say" (qala... aqulu) to structure debates against theological opponents.

**Classification Challenges:** The absolute necessity of identifying the actual position of the author versus the positions of the adversaries being quoted purely for the purpose of refutation.

**Boundary Challenges:** The absolute necessity of capturing the complete refutation. Excerpting an opponent's view and attributing it to the author results in catastrophic theological misrepresentation.

**Cross-References:** Heavy, sophisticated engagement with Mantiq, Aqidah, and Falsafa.

**Top DR Questions:**
1. What specialized sequence-labeling protocols are required to map dialectical pivot phrases and absolutely prevent the misattribution of adversarial arguments to the primary author?
2. How can NLP models map the complex dependency trees of rational proofs utilized to defend specific, nuanced creedal points?
3. What markers indicate the transition from epistemological groundwork to the refutation of specific sectarian groups?

### 16. Tabaqat (Biographical Dictionaries) / علم الطبقات

**Unique Structures:** Standardized biographical entries (tarajim) organized by historical generation (tabaqah), alphabetical order, or geographical location, forming massive encyclopedias of scholarly networks.

**Classification Challenges:** Resolving severe entity ambiguity (disambiguation) due to highly repetitive naming conventions, the widespread use of patronymics (kunya, nasab), and shared titles.

**Boundary Challenges:** Clearly demarcating where one scholar's biography ends and the next begins, especially in unpunctuated manuscripts or poorly digitized OCR texts where headers are indistinguishable from body text.

**Cross-References:** Absolutely essential for Ilm al-Rijal, Tarikh, and verifying transmission chains in virtually all other Islamic sciences.

**Top DR Questions:**
1. What are the most advanced techniques for Named Entity Recognition (NER) and entity disambiguation when parsing densely populated, highly repetitive biographical dictionaries?
2. How can the system computationally transform linear biographical text into complex, relational knowledge graphs detailing multi-generational teacher-student networks?
3. What algorithms best handle the automated extraction of bibliographic data (lists of authored books) embedded within the biographical entry?

### 17. Mustalahat al-Hadith (Hadith Terminology) / علم مصطلح الحديث

**Unique Structures:** Definitional and methodological texts outlining the precise, highly technical rules for narrator evaluation, the acceptable mechanisms of transmission (tahamul wa ada'), and the rubrics for hadith classification.

**Classification Challenges:** Differentiating between theoretical definitions of terms and the practical, historical application of those terms by early critics in narrator evaluation.

**Boundary Challenges:** Ensuring the extraction of a methodological rule includes all the author's stipulated caveats, exceptions, and conditions, which are often listed after the primary definition.

**Cross-References:** Forms the theoretical backbone applied practically in Ilm al-Rijal and Hadith commentary.

**Top DR Questions:**
1. How can terminology extraction engines be refined to capture the evolving, fluid definitions of hadith classifications across different centuries of scholarship?
2. What structural patterns indicate the synthesis of conflicting methodological rules by later synthesizers, such as Ibn Salah in his Muqaddimah?
3. How can the system map the ontological relationships between different categories of hadith weakness (e.g., the relationship between shadh and munkar)?

### 18. Ilm al-Rijal (Narrator Criticism) / علم الرجال

**Unique Structures:** Highly concentrated, dense entries evaluating the trustworthiness, memory retention, and orthodoxy of individual transmitters, utilizing a highly specialized vocabulary of disparagement and validation (jarh wa ta'dil).

**Classification Challenges:** Mapping the precise grading scale used by specific critics, as terms like da'if (weak) or thiqa (trustworthy) may carry vastly different weights depending on the strictness of the specific author.

**Boundary Challenges:** Extracting evaluations without losing the vital context of who is making the evaluation, as entries often quote multiple prior critics before the author reaches a final conclusion.

**Cross-References:** Intimately linked to Tabaqat and directly applied to Hadith isnads to determine final authenticity.

**Top DR Questions:**
1. What machine learning approaches can accurately classify the highly nuanced, context-dependent, and sometimes contradictory sentiment of jarh wa ta'dil vocabulary?
2. How can automated systems reconstruct comprehensive narrator evaluation profiles by aggregating fragmented mentions across multiple biographical sources?
3. What techniques can accurately pair a specific criticism with the specific critic when multiple opinions are listed sequentially without repeating the pronoun?

---

## Dangerous Excerpting Edge Cases for Scholarly Integrity

| Rank | Danger Category | Mechanism of Corruption | Example Context |
|------|----------------|------------------------|-----------------|
| 1 | Omission of Restrictive Clauses (Taqyid/Istithna') | Transforms a highly conditional legal ruling into an absolute, universal mandate | Fiqh texts governing transactions or punishments |
| 2 | Conflation of Opponent's View (Qawl al-Mukhalif) | Attributes heretical or opposing views directly to the orthodox author | Kalam and Usul dialectical debates |
| 3 | Severing the Abrogating Text (Nasikh) | Propagates obsolete, legally invalid rulings as current law | Tafsir and legal texts discussing historical abrogation |
| 4 | Misattribution of Preferred Ruling (Tarjih) | Confuses the global author's official stance with a quoted, rejected school's stance | Comparative Fiqh encyclopedias |
| 5 | Layer Collapse (Matn vs. Sharh) | Destroys the structural hierarchy, confusing the original source with later commentary | Super-commentaries (Hashiyah) and standard commentaries |
| 6 | Severing Context of Revelation (Asbab al-Nuzul) | Strips scriptural commands of their limiting historical triggers | Exegetical texts addressing warfare or specific treaties |
| 7 | Disconnecting Isnad from Matn | Strips the substantive text of its epistemological weight and provenance | Primary Hadith compilations |
| 8 | Severance of Anaphoric Pronouns (Idmar) | Renders the ruling useless by detaching it from its established subject | Continuous legal prose with distant referents |
| 9 | Fragmenting Syllogistic Premises | Extracts a meaningless observation instead of the intended logical proof | Mantiq and Kalam rational arguments |
| 10 | Divorcing Linguistic from Technical Definition | Misinforms the user regarding the actual applied science of the discipline | Mustalah and Usul definitional introductions |

### 1. The Omission of Restrictive Clauses (Taqyid) or Exceptions (Istithna')

**The Danger:** In Islamic jurisprudence, general statements (mutlaq) are frequently restricted by subsequent clauses (muqayyad). Cutting an excerpt before a restricting clause or an exception transforms a specific, conditional legal ruling into an absolute, universal one. This directly alters the divine law (Sharia) as presented by the jurist, representing the highest level of knowledge corruption.

**Real Example:**
«لا تبيعوا الذهب بالذهب إلا مثلا بمثل»
(Do not sell gold for gold, except like for like).

**Knowledge Corruption:** If the boundary generation terminates the extraction at "Do not sell gold for gold," the system outputs a blanket prohibition on all gold trading, completely omitting the istithna' (except like for like) which actually permits the trade under specific conditions.

**Detection & Handling:** The system must implement mandatory forward-scanning algorithms. If a primary ruling or command verb is detected, the engine must scan the subsequent tokens for restrictive particles (e.g., illa, in, bi-shart, ma lam). The boundary cannot be closed until the restrictive clause concludes.

**SPEC Rule Relation:** This requires an explicit enhancement to the boundary detection rules in SPEC.md to strictly forbid segmenting immediately preceding exclusionary, conditional, or temporal Arabic particles.

### 2. Conflation of the Opponent's View with the Author's View

**The Danger:** In dialectical texts, particularly within Ilm al-Kalam and Usul al-Fiqh, authors routinely quote heterodox or opposing views extensively—often for several paragraphs—specifically in order to systematically refute them.

**Real Example:**
«فإن قيل: القرآن مخلوق... قلنا: هذا كفر»
(If it is said: The Qur'an is created... We say: This is disbelief).

**Knowledge Corruption:** If the extraction begins at "The Qur'an is created" and the boundary cuts before the rebuttal is introduced, the system will attribute a Mu'tazilite theological doctrine directly to an orthodox Sunni author, entirely reversing the author's intended theological stance.

**Detection & Handling:** The engine must utilize advanced sequence-labeling models trained specifically on classical dialectical pivot markers (fa-in qila, qala al-mukhalif, htajja al-khasm). Any text following these markers must be structurally flagged as "Opponent View" until the definitive rebuttal pivot (qulna, al-jawab, fa-nadinuhu) is reached.

**SPEC Rule Relation:** This relates to the absolute necessity for semantic state tracking within the extraction engine; boundaries cannot arbitrarily separate a recognized dialectical premise from its structural rebuttal.

### 3. Severing the Abrogating Text (Nasikh) from the Abrogated (Mansukh)

**The Danger:** Islamic law contains rulings that were historically applied during the Prophetic era but were later abrogated by subsequent revelation or prophetic command. Texts often discuss the original ruling to provide historical context before explaining the final law.

**Real Example:**
«والذين يتوفون منكم ويذرون أزواجا وصية لأزواجهم... وهذا منسوخ بآية المواريث»
(And those of you who die and leave widows behind, a bequest for their wives... And this is abrogated by the verse of inheritance).

**Knowledge Corruption:** If a text discusses an abrogated ruling and the extraction stops before the author introduces the abrogating text, the system propagates an obsolete, legally invalid ruling as current Islamic law.

**Detection & Handling:** The system requires automated detection of abrogation terminology (nusikhat bi, wa hadha mansukh, nusikha hukmuha). The engine must ensure the excerpt captures the full evolutionary trajectory of the ruling, forcing the boundary outward to include the final legal state.

**SPEC Rule Relation:** SPEC.md must contain semantic continuity checks for terminologies indicating abrogation or supersession, preventing breaks before the nasikh is introduced.

### 4. Misattribution of the Extracted Ruling (Tarjih) in Comparative Fiqh

**The Danger:** Encyclopedic works of comparative jurisprudence, such as Ibn Qudama's Al-Mughni, exhaustively list the views of multiple schools of thought (madhhabs) before stating the author's preferred, authoritative view.

**Real Example:**
«وقال أبو حنيفة: يصح... ولنا: ما روى...»
(Abu Hanifa said: It is valid... And our proof is: What was narrated...).

**Knowledge Corruption:** An excerpting error might accurately extract Abu Hanifa's view but metadata-tag it globally as the official Hanbali stance of Ibn Qudama, fundamentally confusing the madhhabs and corrupting the legal database.

**Detection & Handling:** The classification engine must map speaker attributions to highly specific, localized textual spans. Words like wa lana (and for us) or wa al-sahih 'indana (and the correct view according to us) must trigger the attribution to the primary author, while preceding views must be tagged to their respective imams.

**SPEC Rule Relation:** Metadata generation rules within SPEC.md must link the extracted text entity strictly to the localized subject and speaker, overriding the document's global author metadata where necessary.

### 5. Failure to Differentiate Matn and Sharh Layers

**The Danger:** In extensive classical commentaries, the base text (matn) is woven directly and continuously into the commentary (sharh), often without modern punctuation or line breaks.

**Real Example:**
«(كتاب الطهارة) وهي لغة النظافة (المياه ثلاثة)...»
(Book of Purification — and it means linguistically cleanliness — Water is of three types...).

**Knowledge Corruption:** The system fails to recognize that "Book of Purification" and "Water is of three types" belong to the original author of the matn, while the linguistic definition belongs to the commentator. This destroys the structural hierarchy of the text and conflates two distinct historical voices.

**Detection & Handling:** The system must be trained to recognize traditional delimiting markers (e.g., qawluhu, ay, ya'ni) or rely on formatting cues (such as parentheses or bolding in modern digital editions) to cleanly separate and tag the distinct layers.

**SPEC Rule Relation:** This dictates the strict necessity for hierarchical layer tagging within the excerpting specification, ensuring the engine can identify text within text.

### 6-10: Additional Edge Cases

**6. Severing the Context of Revelation/Action (Asbab al-Nuzul/Wurud)** — Extracting a scriptural command without the historical context that generated it. Detection: backward-push to encompass narrative prefaces (sabab dhalika, lamma qadima).

**7. Disconnecting the Isnad from the Matn** — In a digital library focused on deep scholarly analysis, a matn without its specific isnad cannot be subjected to narrator criticism. The isnad and matn must be treated as a singular, indivisible structural unit.

**8. Severance of Anaphoric Pronoun Referents (Idmar)** — Classical Arabic heavily utilizes pronouns referring to entities established paragraphs earlier. Coreference resolution must trace pronouns back to explicit nouns, expanding boundaries backward.

**9. Fragmenting Syllogistic Premises** — Rational proofs require sequential stacking of premises. The system must recognize logical structuring particles (fa, idhan, li-anna) and refuse to place boundaries until the deductive conclusion is reached.

**10. Divorcing a Term from its Technical Definition** — In terminological texts, the linguistic and technical definitions must be co-extracted as a unified semantic block, triggered by their paired occurrence (lughatan... istilahan).

---

## Scholarly Completeness Criteria

### a) A Complete Legal Discussion (Mas'ala)

**Traditional Criteria** (per al-Shatibi's Al-Muwafaqat, Ibn Qudama's Al-Mughni):
1. **Taswir al-Mas'ala:** Precise delineation of the legal scenario
2. **Al-Aqwal/Al-Ikhtilaf:** Dominant opinions and competing positions
3. **Al-Adillah:** Evidentiary basis (Qur'an, Hadith, Qiyas, Maslaha)
4. **Wajh al-Dalalah:** How the evidence maps to the proposed ruling
5. **Al-Tarjih:** Weighing of evidence and conclusive ruling

**Machine-Detectable Signals:**
- Start: fasl, mas'ala, idha su'ila, wa amma
- Internal: qala Abu Hanifa, wa lish-Shafi'i, wa daliluna, li-qawlihi ta'ala
- End: fa-thabata bi-hadha, wa 'alayhi al-amal, followed by new fasl/mas'ala

### b) A Complete Hadith Commentary Unit

**Traditional Criteria** (per al-Suyuti's Tadrib al-Rawi, modeled in Fath al-Bari):
1. **Irad al-Hadith:** Complete isnad + matn
2. **Takhrij:** Alternate routings and corroborating chains
3. **Sharh al-Gharib/Lugha:** Philological explanation of rare words
4. **Istinbat al-Ahkam:** Extraction of jurisprudential rulings
5. **Tawjih/Daf' al-Ta'arud:** Reconciliation with contradictory texts

**Machine-Detectable Signals:**
- Start: haddathana/akhbarana + high density of Named Entities
- Internal: qawluhu... ay (linguistic), wa fihi dalil 'ala (legal extraction)
- End: shift to new isnad or explicit numbering of new hadith

### c) A Complete Tafsir Passage

**Traditional Criteria** (per al-Zarkashi's Al-Burhan fi 'Ulum al-Qur'an):
1. **Al-Ayaat:** Specific verse(s) with thematic link (munasaba)
2. **Sabab al-Nuzul:** Historical occasion of revelation
3. **Al-Tahlil al-Lughawi:** Syntactic parsing and rhetorical analysis
4. **Tafsir al-Qur'an bi-al-Qur'an:** Cross-referencing with other verses
5. **Al-Ahkam al-Mustanbata:** Legal/theological rulings extracted

**Machine-Detectable Signals:**
- Start: Qur'anic text (highly diacritized, Unicode brackets ﴿ ﴾), followed by tafsiruhu, yaqul Allah
- Internal: nazalat fi, sabab nuzuliha, kama fi qawlihi
- End: Introduction of next sequential Qur'anic verse

### d) A Complete Biographical Entry (Tarjama)

**Traditional Criteria:**
1. **Al-Ism wa al-Nasab:** Full name, patronymic, lineage
2. **Al-Wilada wa al-Wafah:** Birth and death dates
3. **Al-Rihla wa al-Shuyukh:** Travels and list of teachers
4. **Al-Talamidh:** Notable students/transmitters
5. **Al-Jarh wa al-Ta'dil:** Scholarly assessment of reliability

**Machine-Detectable Signals:**
- Start: subject name (formatted/isolated) + genealogies (ibn... ibn...)
- Internal: rawa 'an, samia min (teachers), rawa 'anhu (students), thiqa/da'if (evaluation)
- End: tuwuffiya sana, mata fi (death dates), followed by next scholar's entry
