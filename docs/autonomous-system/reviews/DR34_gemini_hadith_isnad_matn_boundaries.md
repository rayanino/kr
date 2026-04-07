# **Computational Architecture of Hadith Literature: Structural Patterns, Boundary Detection, and Semantic Segmentation**

The digitization and computational processing of classical Arabic Islamic texts present unique challenges in the field of Natural Language Processing (NLP) and computational linguistics. Among these texts, the hadith corpus holds unparalleled significance, functioning as the secondary foundational source of Islamic jurisprudence and theology after the Qur'an.1 Unlike conventional literary prose or historical chronicles, hadith texts are strictly bipartite, consistently consisting of a chain of human transmitters (*isnād*) and the core text or historical narrative (*matn*).1 The extraction, structural segmentation, and semantic classification of these two primary components require a highly nuanced understanding of the rigorous structural conventions established by early Islamic scholars during the compilation era.

When constructing an NLP pipeline to process this vast corpus—whether utilizing statistical methods like Hidden Markov Models (HMMs), Conditional Random Fields (CRFs), Prediction by Partial Matching (PPM), or advanced Transformer-based token classifiers—the system must accurately delineate the boundaries between the *isnād* and the *matn*.3 Furthermore, it must resolve the complexities of compound and branching transmission chains, and successfully disentangle the core historical texts from later scholarly commentaries (*sharḥ*) that are frequently interleaved with the primary source material.7 This comprehensive report provides an exhaustive structural and philological analysis of hadith architecture, specifically tailored for the development of machine-readable pipelines, sequence taggers, and intelligent excerpting engines.

## **1\. The Epistemological and Computational Architecture of Hadith**

Before delving into the specific boundary markers, it is necessary to understand the epistemological framework that necessitates this bipartite structure. The science of hadith (*'ulūm al-ḥadīth*) operates on the fundamental premise that the historical veracity of a text can only be authenticated by critically examining the unbroken continuity and the moral and intellectual reliability of the individuals who transmitted it.10 Consequently, every hadith is a composite entity. The *isnād* represents the metadata—the provenance, routing, and chronological succession of authorities—while the *matn* represents the payload or the actual instructional content.1

From a computational perspective, translating this structure into a machine-readable format is fraught with difficulties. The Arabic language is morphologically rich, highly agglutinative, and historically lacks the standardized punctuation marks (such as quotation marks, colons, or periods) that Western NLP models typically rely upon to identify sentence boundaries or quoted speech.3 In classical Arabic, specific lexical tokens, transition verbs, and morphological patterns serve the function of punctuation.12 Therefore, any pipeline designed to segment hadith must rely heavily on identifying and parsing these specific "transmission tools" (أدوات الأداء) to determine where the metadata ends and the historical payload begins.3

Recent advancements in computational studies have attempted to map these structures. For instance, the Multi-IsnadSet (MIS) project successfully modeled the *isnād* networks of *Ṣaḥīḥ Muslim* using a multi-directed graph database, representing individual narrators as nodes and transmission events as edges.1 Other approaches have utilized *n*\-gram models and bi-gram techniques to identify segmentation points with accuracy rates exceeding ninety-two percent.14 However, these systems frequently encounter failure states when confronted with the immense structural irregularities, compound chains, and ambiguous syntactic formations present across the diverse compilations of the Six Books (*Al-Kutub Al-Sittah*), which include the collections of Al-Bukhārī, Muslim, Abū Dāwūd, Al-Tirmidhī, Al-Nasā'ī, and Ibn Mājah.15

## **2\. Isnād-Matn Boundary Patterns and Transitions**

The transition from the *isnād* to the *matn* represents the most critical segmentation point in hadith processing.1 Traditional hadith scholars utilized a highly formalized vocabulary to indicate the exact nature of the information transfer between generations. For an NLP system, detecting the boundary requires mapping the topology of the sentence to identify the terminal node of the transmission chain (invariably a Companion of the Prophet) and the specific verb that initiates the core narrative.

### **2.1 Typical Isnād-to-Matn Transition Markers**

In the canonical compilations, a standard, unambiguous hadith exhibits a linear and predictable sequence. The text begins with the compiler citing his immediate teacher, followed by a chain of proper nouns connected by specific transmission verbs, culminating in the terminal narrator, who then introduces the *matn*.17

The typical boundary is signaled by a combination of a terminal transmission verb paired with a reference to the Prophet Muhammad. A sequence-labeling algorithm or an HMM chunker can identify the boundary by detecting the shift from genealogical and transmission vocabulary to conversational, instructional, or declarative prose.3

The archetypal structural formula for a standard Prophetic hadith can be modeled as follows:

\[Compiler\] \+ \+ \[Intermediate Narrators\] \+ \+ \+ \+ \+

To illustrate this standard boundary, consider the following quintessential example from the opening of *Ṣaḥīḥ Al-Bukhārī*:

**Arabic Text:**

حَدَّثَنَا الْحُمَيْدِيُّ عَبْدُ اللَّهِ بْنُ الزُّبَيْرِ، قَالَ حَدَّثَنَا سُفْيَانُ، قَالَ حَدَّثَنَا يَحْيَى بْنُ سَعِيدٍ الأَنْصَارِيُّ، قَالَ أَخْبَرَنِي مُحَمَّدُ بْنُ إِبْرَاهِيمَ التَّيْمِيُّ، أَنَّهُ سَمِعَ عَلْقَمَةَ بْنَ وَقَّاصٍ اللَّيْثِيَّ، يَقُولُ سَمِعْتُ عُمَرَ بْنَ الْخَطَّابِ ـ رضى الله عنه ـ عَلَى الْمِنْبَرِ قَالَ سَمِعْتُ رَسُولَ اللَّهِ ﷺ يَقُولُ ‏"‏ إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ... ‏"

**English Translation:** Narrated to us Al-Ḥumaydī 'Abdullāh bin Al-Zubayr, he said: narrated to us Sufyān, he said: narrated to us Yaḥyā bin Sa'īd Al-Anṣārī, he said: informed me Muḥammad bin Ibrāhīm Al-Taymī, that he heard 'Alqamah bin Waqqāṣ Al-Laythī saying: I heard 'Umar bin Al-Khaṭṭāb (may Allah be pleased with him) on the pulpit saying: I heard the Messenger of Allah ﷺ saying: "Actions are judged by intentions..." 18

**Boundary Analysis:** In this classical structure, the *isnād* relies heavily on standard transmission tools: *ḥaddathanā* (narrated to us), *akhbaranī* (informed me), and *sami'tu* (I heard).3 The absolute computational boundary occurs immediately after the final token يَقُولُ (saying) which follows رَسُولَ اللَّهِ ﷺ (the Messenger of Allah). The *matn* strictly begins at the token إِنَّمَا (Actions...). For an NLP tagger, the phrase سَمِعْتُ رَسُولَ اللَّهِ ﷺ يَقُولُ (I heard the Messenger of Allah saying) or the highly frequent أَنَّ رَسُولَ اللَّهِ ﷺ قَالَ (that the Messenger of Allah said) serves as a high-confidence delimiter separating the transmission metadata from the primary data payload.19

The following table outlines the most frequent and reliable transmission verbs that function within the *isnād* and frequently act as pre-boundary markers within the canonical collections:

| Transmission Tool (Arabic) | Transliteration | Lexical Meaning | Pipeline Role (Sequence Tagging) |
| :---- | :---- | :---- | :---- |
| حَدَّثَنَا / حَدَّثَنِي | *ḥaddathanā / ḥaddathanī* | He narrated to us / to me | High-probability *isnād* continuation marker; explicitly links two nodes via direct oral transmission.3 |
| أَخْبَرَنَا / أَخْبَرَنِي | *akhbaranā / akhbaranī* | He informed us / me | High-probability *isnād* continuation marker; generally denotes reading back to the teacher.3 |
| عَنْ | *'an* | On the authority of / From | Denotes a *mu'an'an* chain; connects nodes but lacks explicit declaration of hearing, creating potential discontinuities (*tadlīs*).13 |
| سَمِعْتُ | *sami'tu* | I heard | Terminal or intermediate marker; provides the highest level of explicit continuity and frequently precedes the Prophet's statement.20 |
| أَنَّ رَسُولَ اللَّهِ قَالَ | *anna rasūl Allāhi qāla* | That the Messenger of Allah said | Absolute boundary marker. The computational *matn* begins immediately at the subsequent token.19 |

### **2.2 Unusual and Irregular Transitions**

While the standard transitions follow a highly predictable Source \-\> Verb \-\> Target topology, the hadith corpus is replete with numerous irregular structural patterns. These anomalies frequently fool pattern-based detectors, regular expressions, and basic *n*\-gram models, leading to improper segmentation where parts of the text are misclassified.14

**A. Anecdotal or "Deed" (*Fi'lī*) Hadiths:** Not all hadiths record the direct, verbatim speech of the Prophet. A vast portion of the corpus records his physical actions, the events that occurred in his presence, his silent approvals (*taqrīr*), or descriptions of his physical characteristics (*shamā'il*). In these instances, the classic boundary marker قَالَ (he said) attributed to the Prophet is entirely absent.22

**Example from *Ṣaḥīḥ Muslim*:**

**Arabic Text:**

حَدَّثَنَا ابْنُ نُمَيْرٍ، حَدَّثَنَا أَبِي، حَدَّثَنَا عُبَيْدُ اللَّهِ، عَنْ نَافِعٍ، عَنِ ابْنِ عُمَرَ، قَالَ كَانَ لِرَسُولِ اللَّهِ ﷺ مُؤَذِّنَانِ بِلاَلٌ وَابْنُ أُمِّ مَكْتُومٍ الأَعْمَى

**English Translation:** Narrated Ibn Numayr, narrated from his father, narrated from 'Ubaydullāh, from Nāfi', from Ibn 'Umar, he said: "The Messenger of Allah ﷺ had two mu'adhdhins: Bilāl and Ibn Umm Maktūm the blind." 22

**Boundary Analysis:** Here, the transition is structurally irregular compared to verbal hadiths. The terminal narrator (Ibn 'Umar) acts as the subject of the verb قَالَ (he said), but the subsequent text كَانَ لِرَسُولِ اللَّهِ (The Messenger of Allah had...) is *already* the *matn*.22 A naive rule-based system programmed to search strictly for رَسُولَ اللَّهِ قَالَ (The Messenger of Allah said) would fail to find the trigger, potentially classifying the entire passage as *isnād* or failing to segment it entirely. The NLP pipeline must be trained on syntactic dependencies: if the terminal noun (Ibn 'Umar) is followed by قَالَ, and the subsequent clause contains a descriptive or past-continuous verb such as كَانَ (was/had) linked to the Prophet, the boundary falls immediately after the terminal narrator's قَالَ.

**B. Inverted Textual Structures and Preamble Narratives (*Maqlūb* Patterns):**

Occasionally, the *matn* is presented with a lengthy introductory contextual phrase or an anecdotal preamble provided by the narrator *before* the actual prophetic saying is quoted. This preamble sets the historical or legal stage for why the hadith is being narrated.

**Example from *Sunan Abī Dāwūd*:**

**Arabic Text:**

عَنْ عَائِشَةَ، قَالَتْ قَالَ رَسُولُ اللَّهِ ﷺ ‏ "‏ تَوَضَّئُوا مِمَّا مَسَّتِ النَّارُ ‏"‏‏.‏

**English Translation:** Narrated that 'A'ishah said: The Messenger of Allah said: "Perform ablution after (eating) that which has been changed by fire." 23

While the example above from *Sunan Ibn Mājah* / *Abī Dāwūd* appears straightforward, irregular variants of this structure often interleave a Companion's dialogue, a question from a student, or a historical event *before* the Prophet's statement.14 For instance, a narrator might state, "We were sitting in the mosque when a man entered and asked..." The pipeline must distinguish between the transmission chain (which ends when the narrator begins describing the scene) and the narrator's contextual narrative (which is technically part of the *matn*, though logically serves as a preamble). The entirety of the dialogue or scene-setting, starting immediately after the final transmission verb, constitutes the *matn* block.

**C. Appended Metadata and Commentaries (The Methodology of Al-Tirmidhī):** Imām Al-Tirmidhī introduced a unique and challenging structural complexity to his compilation, *Jāmi' Al-Tirmidhī* (also known as *Sunan Al-Tirmidhī*). He routinely appends his own critical commentary, cross-references to other Companions who narrated on the same topic, and his personal grading of the hadith's authenticity immediately *after* the *matn*.24

**Example Structural Pattern in *Jāmi' Al-Tirmidhī*:**

\[Isnād\] \-\> \[Matn\] \-\>

A pattern-based detector that simply classifies everything after the *isnād* as *matn* will erroneously include Al-Tirmidhī's jurisprudential remarks and grading (e.g., "Abū 'Īsā said: This hadith is *ḥasan ṣaḥīḥ*") as part of the Prophet's original speech.24 To process the *Sunan* of Al-Tirmidhī or Abū Dāwūd (who also includes post-textual remarks regarding weaknesses in the chain), a sophisticated NLP pipeline must deploy a secondary boundary detection module.24 This module must look for the compiler's *kunya* (e.g., قَالَ أَبُو عِيسَى \- Abū 'Īsā said) or specific terminological keywords like حَسَنٌ (good), صَحِيحٌ (authentic), or غَرِيبٌ (rare) to identify the post-*matn* transition out of the historical text and into the compiler's metadata layer.24

### **2.3 Cases of Genuine Boundary Ambiguity**

Certain morphological ambiguities make the *isnād*\-*matn* boundary genuinely unclear, causing significant challenges not only for automated systems but occasionally for human annotators and classical scholars themselves.12

**A. The Ambiguity of the Verb "Qāla" (قَالَ \- He said):** The verb قَالَ is overwhelmingly the most frequently used token in both the *isnād* and the *matn*.14 Within the *isnād*, it functions mechanically to connect a student to a teacher (e.g., *ḥaddathanī fulān, qāla: ḥaddathanā fulān*). Within the *matn*, it indicates the quoted speech of the Prophet or the dialogue of the historical actors. When consecutive narrators use قَالَ, or when a dialogue ensues, a machine-learning model (such as a tri-gram sequence tagger) may severely misclassify the transition.14

For instance, if a machine encounters the phrase قَالَ رَجُلٌ ("a man said"), a tri-gram model trained narrowly on standard collections might probabilistically classify this phrase as part of the *isnād*, because the word "said" overwhelmingly precedes narrator names in the training data.14 However, if "a man said" is part of a historical dialogue with the Prophet within the narrative, it belongs entirely to the *matn*.14 This requires deep semantic parsing, Coreference Resolution, and Named Entity Recognition (NER) to determine if the subject of "said" is a known historical transmitter found in biographical dictionaries (*kutub al-rijāl*) or an anonymous actor within the story.27

**B. The Phenomenon of *Idrāj* (Interpolated Text):** A *Mudraj* (interpolated) hadith represents the most difficult boundary ambiguity. It occurs when a narrator (often a Companion or Successor) inadvertently or intentionally fuses their own explanatory comment, legal opinion, or lexical gloss with the actual text of the Prophet, without providing a linguistic delimiter such as "and the narrator added".28 The *matn* and the narrator's commentary merge seamlessly into a single continuous string of Arabic text.29

For example, a Companion might narrate a Prophetic ruling on ablution and immediately append their own jurisprudential opinion on how to wash the feet. Because the physical text lacks a separator, an automated NLP pipeline will invariably extract the entire block—both the Prophet's words and the Companion's interpolation—as the definitive *matn*. Resolving *idrāj* cannot be accomplished via structural pattern recognition or syntax trees alone; it requires cross-document *Isnād-cum-Matn* Analysis (ICMA). By computationally comparing multiple variants of the same hadith across different collections (e.g., comparing the Bukhārī variant against the Nasā'ī variant), the system can isolate the shared exact wording of the Prophet from the anomalous additions inserted by specific regional transmitters.31

## **3\. Computational Modeling of Compound and Complex Isnāds**

Hadith literature is not a flat, linear dataset of isolated texts; it is a highly complex, interconnected, multi-directed graph.1 The MIS dataset demonstrates that a single compilation like *Ṣaḥīḥ Muslim* contains thousands of nodes representing individual narrators and tens of thousands of edges representing transmission events.1 Compilers frequently utilized compound *isnāds* to save manuscript space or to rigorously demonstrate the robust, multi-channel transmission history of a specific *matn*. An excerpting pipeline must be able to parse and model these branching graph structures without corrupting the relationship between the chains and the text.

### **3.1 Handling the *Taḥwīl* (ح) Symbol: Multiple Chains for One Matn**

To avoid the tedious repetition of rewriting the identical text of a *matn* multiple times, classical scholars—most notably Imām Muslim—employed a specific abbreviation: the Arabic letter ح (Hā'). This symbol stands for *taḥwīl* or *ḥawālah*, meaning "transfer," "shift," or "routing".19 It indicates a pivot from one chain of narrators to another parallel chain before finally presenting the single, shared *matn* at the convergence point.19

**Example of *Taḥwīl* from *Ṣaḥīḥ Muslim*:**

**Arabic Text:**

حَدَّثَنِي أَبُو الرَّبِيعِ الزَّهْرَانِيُّ، حَدَّثَنَا حَمَّادٌ يَعْنِي ابْنَ زَيْدٍ عَنْ ثَابِتٍ، وَعَبْدِ الْعَزِيزِ بْنِ صُهَيْبٍ، عَنْ أَنَسٍ؛ **ح** وَحَدَّثَنَا قُتَيْبَةُ بْنُ سَعِيدٍ، حَدَّثَنَا حَمَّادٌ، عَنْ ثَابِتٍ، وَشُعَيْبِ بْنِ الْحَبْحَابِ، عَنْ أَنَسٍ؛ **ح** وَحَدَّثَنِي قُتَيْبَةُ حَدَّثَنَا أَبُو عَوَانَةَ، عَنْ قَتَادَةَ، وَعَبْدِ الْعَزِيزِ، عَنْ أَنَسٍ أَنَّ رَسُولَ اللَّهِ ﷺ قَالَ...

**English Translation:** Narrated to me Abū al-Rabī' al-Zahrānī, narrated Hammād Ibn Zayd, from Thābit and 'Abd al-'Azīz bin Suhayb, from Anas; \*\*\*\* and narrated Qutaybah bin Sa'īd, narrated Hammād, from Thābit and Shu'ayb bin Habḥāb, from Anas; \*\*\*\* and narrated to me Qutaybah narrated Abū 'Awānah, from Qatādah, and 'Abd al-'Azīz, from Anas, that the Messenger of Allah ﷺ said... 19

**Pipeline Handling Strategy:** When the NLP pipeline encounters the ح symbol, it must absolutely **not** treat the preceding chain as a broken or defective hadith that is missing a *matn*.19 Instead, the pipeline architecture must be programmed to recognize the ح as a structural control flow operator that constructs a parallel array of *isnāds*.21

1. **Parsing Logic:** Treat ح as a boolean delimiter that saves the current *isnād* array in memory and opens a new *isnād* array for the subsequent text.19  
2. **Convergence Detection:** Continue this looping extraction process until the terminal transition marker (e.g., أَنَّ رَسُولَ اللَّهِ قَالَ) is reached, signaling the end of the metadata and the beginning of the payload.  
3. **Data Modeling:** In the graph database, this should map as a Many-to-One relationship: Many distinct *Isnād* objects (Chain A, Chain B, Chain C) are mapped to exactly One *Matn* object. They must be grouped and retrieved as one logical unit because they are contextually bound to a single historical utterance.19

### **3.2 Common Links: *Muḍṭarib* and *Mutallib* Graph Networks**

When modeling hadiths that have multiple chains across different compilations, researchers and computational tools frequently utilize *Isnād-cum-Matn* Analysis (ICMA) to trace the evolution of the text.31 This analysis often reveals a "Common Link" (مدار \- *Madār*)—a single narrator, usually operating in the mid-tier of the chain (such as a *Tābi'ī* or a Successor in the late first century AH), through whom all variants of a specific hadith funnel before branching out again to later compilers like Bukhārī and Abu Dāwūd.31

A critical issue arises when the system detects a *Muḍṭarib* (confounded or disrupted) hadith pattern. This occurs when the branching chains diverging from the Common Link fundamentally disagree on the actual text of the *matn* or the preceding sequence of narrators, and the variations are of equal strength, making scholarly reconciliation impossible.10

**Pipeline Handling Strategy:** For an NLP system managing these complex networks, the underlying data structure must support Directed Acyclic Graphs (DAGs) rather than flat tables.1

* If multiple *isnāds* are extracted from different books that share an identical *matn*, the pipeline should use entity resolution to identify the Common Link node and map the convergent and divergent paths.32  
* Crucially, when the system detects a *Muḍṭarib* pattern (i.e., the Common Link is recorded as transmitting contradictory *matn* variations through different students), the system should tag the cluster with a \<Mudtarib\_Conflict\> label. The pipeline must not attempt to artificially merge or normalize these conflicting texts, as the divergence itself is vital data for hadith criticism.38

### **3.3 Processing *Mu'allaq* (Suspended) Isnāds**

A *Mu'allaq* (suspended, hanging, or dangling) hadith is a structural anomaly where the compiler deliberately omits the beginning of the chain of transmission (from their own side), often jumping directly to a much later narrator, a Companion, or even directly quoting the Prophet himself.28 Imām Al-Bukhārī frequently utilizes this suspended structure in his chapter headings (*tarājim al-abwāb*) to establish a thematic or legal premise before proceeding to cite fully connected hadiths in the main body of the chapter.41

**Example of a Mu'allaq Structure:**

\[Compiler\] \-\> OMITTED NODES \-\> \[Companion / Historical Authority\] \-\> \[Matn\]

**Arabic Text Example:** وَقَالَ عُقَيْلٌ عَنِ ابْنِ شِهَابٍ... "And 'Uqayl said, from Ibn Shihāb..." 43

**Pipeline Handling Strategy:** A standard extraction pipeline conditioned to seek traditional initiating verbs like حَدَّثَنَا (*ḥaddathanā*) at the absolute beginning of a text block will completely fail to recognize a *mu'allaq* hadith because the foundational transmission framework is missing.41 To correctly parse *mu'allaq* chains, the NLP pipeline must recognize abrupt semantic transitions characterized by a naked verb (e.g., وَقَالَ \- "and he said", or وَيُذْكَرُ \- "and it is mentioned") followed immediately by a known historical entity.44 The system must utilize Named Entity Recognition (NER) linked to a robust biographical dictionary database (*kutub al-rijāl*) to recognize that "'Uqayl" is a transmitter, despite the absence of an introductory transmission verb.27 Upon detection, the pipeline should tag this specific chain variant with a \<Muallaq\> metadata flag to ensure it is not statistically weighed alongside fully continuous (*muttaṣil*) chains in authenticity scoring.40

## **4\. The Structural Syntax of Hadith Commentary (*Sharḥ*)**

Hadith commentaries (*sharḥ* works) represent some of the most complex and voluminous documents in classical Arabic literature. Masterpieces such as Ibn Ḥajar al-'Asqalānī's magnificent *Fatḥ al-Bārī* (a multi-volume commentary on *Ṣaḥīḥ Al-Bukhārī*) and Al-Nawawī's *Al-Minhāj* (commenting on *Ṣaḥīḥ Muslim*) do not simply list hadiths followed by a block of explanation.7 Instead, the authors heavily interleave the original hadith text with linguistic analysis, jurisprudential deductions, morphological corrections, and cross-references.46

To program a machine to reliably detect the rapid transitions between the primary sacred *matn* and the secondary scholarly *sharḥ*, the NLP pipeline must leverage the highly formalized rhetorical markers employed by medieval scholars.49

### **4.1 Delineating the Core Matn within Commentary**

Commentators rarely replicate the entire hadith in a single uninterrupted block. They segment it into logical phrases, quoting a short fragment and then immediately dissecting it. The universal, highly consistent marker for extracting the *matn* fragment within a commentary is the noun قَوْلُهُ (*qawluhu* \- "His saying").

* **Marker:** قَوْلُهُ (This is followed by the quoted text, which was often presented in traditional manuscripts with a red line drawn over it, and is printed in bold in modern typography).  
* **Pipeline Strategy:** This is a **highly consistent** and reliable marker across the genre. An NLP system should trigger a tag immediately following the token \`قَوْلُهُ\` and close the tag when it encounters the next analytical delimiter or the resumption of the commentator's voice (often signaled by قَالَ referring to a scholar).51

### **4.2 Identifying *Sharḥ al-Gharīb* (Lexical and Grammatical Notes)**

Commentators dedicate significant intellectual space to philology, explaining obscure terminology, archaic vocabulary (*gharīb al-ḥadīth*), and grammatical structures. The transition into lexical analysis is marked by specific explanatory particles.

* **Markers:** أَيْ (*ayy* \- "meaning/that is"), يُرِيدُ (*yurīdu* \- "he intends"), يَعْنِي (*ya'nī* \- "it means").  
* **Example from *Fatḥ al-Bārī*:** (قَوْلُهُ رَحْرَاحٌ) قَالَ الْخَطَّابِيُّ: الْإِنَاءُ الْوَاسِعُ الصَّحْنِ "(His saying: *Raḥrāḥ*). Al-Khaṭṭābī said: It means a vessel with a wide basin..." 51  
* **Pipeline Strategy:** When an NLP pipeline identifies أَيْ immediately following a closed *matn* quote, it should classify the subsequent clause as \<Lexical\_Gloss\>. These markers are moderately reliable but require syntactic parsing and Part-of-Speech (POS) tagging to ensure أَيْ is functioning as an explanatory particle rather than an interrogative pronoun ("which?").3

### **4.3 Identifying *Istinbāṭ* (Extraction of Legal Rulings)**

The ultimate goal of hadith commentary is jurisprudence (*fiqh*) and the derivation of law. The shift from lexical analysis to legal deduction (*istinbāṭ*) is explicitly signaled by transitional phrases that indicate utility or derivation.

* **Markers:** وَفِيهِ (*wa-fīhi* \- "and in it \[this hadith\] is evidence for..."), وَاسْتَنْبَطَ (*wa-ustanbiṭa* \- "and it is derived"), وَاسْتَدَلَّ بِهِ (*wa-ustudilla bihi* \- "and it is used as evidence by...").  
* **Example from *Fatḥ al-Bārī*:** وَفِيهِ رَدٌّ عَلَى مَنْ قَدَّرَ الْوُضُوءَ... "And in it is a refutation against those who limit the water for ablution..." 51  
* **Pipeline Strategy:** The marker وَفِيهِ operating at the beginning of a clause is a **highly reliable** indicator of a shift into \<Legal\_Extraction\>. The NLP system can safely bound this section as theological or legal commentary until a new قَوْلُهُ (returning to the next fragment of the *matn*) is detected.51

### **4.4 Identifying *Shawāhid* and *Mutāba'āt* (Cross-References)**

Scholars routinely strengthen a hadith's legal weight, or explain a variant wording, by quoting corroborating narrations from other companions (*shawāhid*) or parallel chains from the same companion (*mutāba'āt*).53

* **Markers:** وَرَوَى (*wa-rawā* \- "and it is narrated"), وَأَخْرَجَهُ (*wa-akhrajahu* \- "and it was extracted by"), وَلَهُ شَاهِدٌ (*wa-lahu shāhid* \- "and it has a supporting witness").  
* **Example from *Fatḥ al-Bārī*:** وَقَدْ رَوَى مُسْلِمٌ مِنْ حَدِيثِ عَائِشَةَ رَضِيَ اللَّهُ عَنْهَا... "And Muslim has narrated from the hadith of 'A'ishah (may Allah be pleased with her)..." 51  
* **Pipeline Strategy:** These verbs are consistent markers indicating the introduction of external textual data. An NLP system should tag this as \<Cross\_Reference\_Citation\>. However, the system must be rigorously programmed to recognize that the text following وَرَوَى contains a secondary, embedded *isnād* and *matn* that belongs to a different canonical source. Failure to isolate this will cause the pipeline to confuse the embedded quote with the primary hadith being commented upon, corrupting the database entry.51

### **4.5 Summary of Commentary Markers for Machine Detection**

| Structural Component | Arabic Marker | Transliteration | Reliability for Machine Detection | Action in NLP Pipeline |
| :---- | :---- | :---- | :---- | :---- |
| **Quoted Matn** | قَوْلُهُ | *Qawluhu* (His saying) | **Very High**. Universal convention across classical commentaries. | Open \<Matn\_Quote\> boundary.51 |
| **Lexical Gloss** | أَيْ / يَعْنِي | *Ayy / Ya'nī* (Meaning) | **Medium**. Requires POS tagging to rule out interrogative or literal verbal use. | Tag subsequent clause as \<Lexical\_Analysis\>.52 |
| **Legal Deduction** | وَفِيهِ / اسْتَدَلَّ | *Wa-fīhi / Ustudilla* (And in it / As evidence) | **High**. Exclusively marks the extraction of rulings (*istinbāṭ*). | Tag as \<Jurisprudential\_Ruling\>.51 |
| **Cross-Reference** | أَخْرَجَهُ / رَوَى | *Akhrajahu / Rawā* (Extracted by / Narrated) | **High**. Signals an external hadith insertion. | Tag as \<Shahid\_Citation\>; initialize secondary extraction module to parse embedded *isnād*.51 |

## **5\. Defining the Atomic Hadith Unit for Excerpting Engines**

When designing the data architecture and excerpting engine for an advanced NLP hadith pipeline, a fundamental philosophical and technical question arises: What constitutes a "complete" hadith unit that should never be algorithmically split or served to the user in fragments?

### **5.1 Classical Methodological Principles (*Uṣūl al-Ḥadīth*)**

According to the foundational texts of hadith methodology, most notably Ibn al-Ṣalāḥ’s 13th-century magnum opus, *Muqaddimah Ibn al-Ṣalāḥ* (Introduction to the Science of Hadith), and Al-Suyūṭī’s highly influential later commentary, *Tadrīb al-Rāwī*, a hadith is an organically bipartite construct.56 Ibn al-Ṣalāḥ, whose work laid the bedrock for all subsequent hadith criticism across 65 comprehensive chapters, makes it unequivocally clear that the *isnād* (the chain) and the *matn* (the text) are two halves of a single ontological entity.56

In traditional Islamic epistemology, a *matn* without an *isnād* is scientifically void; it cannot be authenticated, its narrators cannot be subjected to biographical evaluation (*'ilm al-rijāl*), and it cannot be utilized to derive jurisprudence.11 The intense scrutiny of the chain is what differentiates verified Prophetic statements from fabricated forgeries (*mawḍū'*). Conversely, an *isnād* without a *matn* is functionally meaningless, acting as an empty vessel. Therefore, the traditional methodological principle dictates that the minimal complete citation—the absolute atomic unit of a hadith—is **One Isnād \+ One Matn**.2

### **5.2 Structural Definitions for the Computational Pipeline**

Translating this strict classical definition into a functional computational data model requires adapting the logic to handle the complexities of textual compilation, excerpting, and user retrieval:

**A. The Baseline Atomic Unit:** In a standard query setting (e.g., a user querying a database of *Ṣaḥīḥ Al-Bukhārī* for rulings on fasting), the atomic unit that must be returned by the excerpting engine without being split is: \+ \[One Isnād\] \+ \[One Matn\] While modern readers often prefer "clean" texts, if the excerpting engine strips the *isnād* away by default to provide a streamlined reading experience, it fundamentally violates the integrity of the hadith as defined by the *muḥaddithūn* and removes the data necessary for authenticity grading.2 The *takhrij* (source attribution) serves as crucial computational metadata to anchor the unit, but the unit itself remains the chain and the text.

**B. The Compound Atomic Unit (The *Taḥwīl* Exception):** As analyzed in Section 3.1, when multiple *isnāds* converge on a single *matn* using the ح (*taḥwīl*) symbol, they function as a unified historical and structural event intended by the compiler.19 If an excerpting engine algorithmically splits these chains—presenting only one chain to the user and deleting the others to save space—it destroys the epistemological weight of the narration, which the compiler deliberately reinforced through citing multiple transmission pathways. Therefore, for texts utilizing the *taḥwīl*, the unbreakable atomic unit must be expanded to: \[All Converged Isnāds separated by ح\] \+. These must be stored in the database as a single, unbreakable payload.19

**C. The Commentary Exclusion:** While the *matn* and the *isnād* are completely inseparable, the commentary (*sharḥ*) is strictly an external, later addition. According to classical methodology, the explanations and legal derivations of scholars like Al-Nawawī or Ibn Ḥajar, though highly venerated, are fundamentally distinct from the sacred Prophetic text.8 Consequently, the NLP pipeline must treat the commentary entry as a highly structured relational layer mapped to the atomic hadith, not as part of the atomic unit itself. An intelligent excerpting engine should be architected to query and serve the atomic hadith (Isnād \+ Matn) completely independently of the *sharḥ*, while retaining the ability to overlay the commentary dynamically upon user request.9

By strictly adhering to these structural paradigms, computational models can accurately capture, segment, and preserve the deep historical and epistemological architecture of hadith literature, ensuring that modern NLP applications respect the rigorous methodologies established by classical scholars centuries ago.

#### **Geciteerd werk**

1. Multi-IsnadSet MIS for Sahih Muslim Hadith with chain of narrators, based on multiple ISNAD \- PMC, geopend op april 7, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC11096860/](https://pmc.ncbi.nlm.nih.gov/articles/PMC11096860/)  
2. Computational and natural language processing based studies of hadith literature: a survey, geopend op april 7, 2026, [https://www.researchgate.net/publication/331848759\_Computational\_and\_natural\_language\_processing\_based\_studies\_of\_hadith\_literature\_a\_survey](https://www.researchgate.net/publication/331848759_Computational_and_natural_language_processing_based_studies_of_hadith_literature_a_survey)  
3. HMM Based Part of Speech Tagging for Hadith Isnad \- IJCSNS, geopend op april 7, 2026, [http://paper.ijcsns.org/07\_book/202303/20230316.pdf](http://paper.ijcsns.org/07_book/202303/20230316.pdf)  
4. Hadith data mining and classification: a comparative analysis \- ResearchGate, geopend op april 7, 2026, [https://www.researchgate.net/publication/290222515\_Hadith\_data\_mining\_and\_classification\_a\_comparative\_analysis](https://www.researchgate.net/publication/290222515_Hadith_data_mining_and_classification_a_comparative_analysis)  
5. An example of Hadith, Isnad in black and Matan in green. \- ResearchGate, geopend op april 7, 2026, [https://www.researchgate.net/figure/An-example-of-Hadith-Isnad-in-black-and-Matan-in-green\_fig1\_350375132](https://www.researchgate.net/figure/An-example-of-Hadith-Isnad-in-black-and-Matan-in-green_fig1_350375132)  
6. Isnad AI at IslamicEval 2025: A Rule-Based System for Identifying Islamic Citation in LLM Outputs \- ACL Anthology, geopend op april 7, 2026, [https://aclanthology.org/2025.arabicnlp-sharedtasks.74.pdf](https://aclanthology.org/2025.arabicnlp-sharedtasks.74.pdf)  
7. Fath al-Bari \- Wikipedia, geopend op april 7, 2026, [https://en.wikipedia.org/wiki/Fath\_al-Bari](https://en.wikipedia.org/wiki/Fath_al-Bari)  
8. TAFSIR SAHIH BUKHARI: FATH AL BARI | Sunnah Muakada, geopend op april 7, 2026, [https://sunnahmuakada.files.wordpress.com/2014/10/fath-al-bari.pdf](https://sunnahmuakada.files.wordpress.com/2014/10/fath-al-bari.pdf)  
9. Constructing a Bilingual Hadith Corpus Using a Segmentation Tool \- ACL Anthology, geopend op april 7, 2026, [https://aclanthology.org/2020.lrec-1.415.pdf](https://aclanthology.org/2020.lrec-1.415.pdf)  
10. Hadith terminology \- Wikipedia, geopend op april 7, 2026, [https://en.wikipedia.org/wiki/Hadith\_terminology](https://en.wikipedia.org/wiki/Hadith_terminology)  
11. Problems of Interpreting the Main Types of Hadith in Terms of Their Correct Understanding \- Neliti, geopend op april 7, 2026, [https://media.neliti.com/media/publications/506284-problems-of-interpreting-the-main-types-2cdd872a.pdf](https://media.neliti.com/media/publications/506284-problems-of-interpreting-the-main-types-2cdd872a.pdf)  
12. Tracing Traditions: Automatic Extraction of Isnads from Classical Arabic Texts \- ACL Anthology, geopend op april 7, 2026, [https://aclanthology.org/2020.wanlp-1.12.pdf](https://aclanthology.org/2020.wanlp-1.12.pdf)  
13. سند (علم الحديث) \- ويكيبيديا, geopend op april 7, 2026, [https://ar.wikipedia.org/wiki/%D8%B3%D9%86%D8%AF\_(%D8%B9%D9%84%D9%85\_%D8%A7%D9%84%D8%AD%D8%AF%D9%8A%D8%AB)](https://ar.wikipedia.org/wiki/%D8%B3%D9%86%D8%AF_\(%D8%B9%D9%84%D9%85_%D8%A7%D9%84%D8%AD%D8%AF%D9%8A%D8%AB\))  
14. Text Segmentation Using N-grams to Annotate Hadith Corpus \- ACL Anthology, geopend op april 7, 2026, [https://aclanthology.org/W19-5605.pdf](https://aclanthology.org/W19-5605.pdf)  
15. IslamicMMLU: A Benchmark for Evaluating LLMs on Islamic Knowledge \- arXiv, geopend op april 7, 2026, [https://arxiv.org/pdf/2603.23750](https://arxiv.org/pdf/2603.23750)  
16. Social and Literary Structure of Isnad: A Historical Perspective \- DergiPark, geopend op april 7, 2026, [https://dergipark.org.tr/tr/download/article-file/607206](https://dergipark.org.tr/tr/download/article-file/607206)  
17. Kutub al-Sittah \- Wikipedia, geopend op april 7, 2026, [https://en.wikipedia.org/wiki/Kutub\_al-Sittah](https://en.wikipedia.org/wiki/Kutub_al-Sittah)  
18. Learn What is Isnād and Matn in Hadith with Examples, geopend op april 7, 2026, [https://mubarakacademy.online/en/what-is-isnad-and-matn/](https://mubarakacademy.online/en/what-is-isnad-and-matn/)  
19. Mining and Visualizing the Narration Tree of Hadiths (Prophetic Traditions) \- IGI Global, geopend op april 7, 2026, [https://www.igi-global.com/viewtitle.aspx?TitleId=61067](https://www.igi-global.com/viewtitle.aspx?TitleId=61067)  
20. 04 من قوله: (ثم الإسناد وهو الطريق لموصلة إلى المتن) \- موقع الشيخ ابن باز, geopend op april 7, 2026, [https://binbaz.org.sa/audios/1887/04-%D9%85%D9%86-%D9%82%D9%88%D9%84%D9%87-%D8%AB%D9%85-%D8%A7%D9%84%D8%A7%D8%B3%D9%86%D8%A7%D8%AF-%D9%88%D9%87%D9%88-%D8%A7%D9%84%D8%B7%D8%B1%D9%8A%D9%82-%D9%84%D9%85%D9%88%D8%B5%D9%84%D8%A9-%D8%A7%D9%84%D9%89-%D8%A7%D9%84%D9%85%D8%AA%D9%86](https://binbaz.org.sa/audios/1887/04-%D9%85%D9%86-%D9%82%D9%88%D9%84%D9%87-%D8%AB%D9%85-%D8%A7%D9%84%D8%A7%D8%B3%D9%86%D8%A7%D8%AF-%D9%88%D9%87%D9%88-%D8%A7%D9%84%D8%B7%D8%B1%D9%8A%D9%82-%D9%84%D9%85%D9%88%D8%B5%D9%84%D8%A9-%D8%A7%D9%84%D9%89-%D8%A7%D9%84%D9%85%D8%AA%D9%86)  
21. Artificial Intelligence for Understanding the Hadith \- White Rose eTheses Online, geopend op april 7, 2026, [https://etheses.whiterose.ac.uk/id/eprint/32802/1/Altammami\_SH\_Computing\_PhD\_2023.pdf](https://etheses.whiterose.ac.uk/id/eprint/32802/1/Altammami_SH_Computing_PhD_2023.pdf)  
22. Automating Hadith Narration Trees | PDF \- Scribd, geopend op april 7, 2026, [https://www.scribd.com/document/880394002/ITree-Automating-the-Construction-of-the-Narration-Tree-of-Hadiths-Prophetic-Traditions](https://www.scribd.com/document/880394002/ITree-Automating-the-Construction-of-the-Narration-Tree-of-Hadiths-Prophetic-Traditions)  
23. When Sahihs Disagree \- Quran Talk Blog, geopend op april 7, 2026, [https://qurantalkblog.com/2023/10/21/when-sahihs-disagree/](https://qurantalkblog.com/2023/10/21/when-sahihs-disagree/)  
24. al-Tirmidhi and his Legacy \- Islam: Tradition & Perspective \- from Imam Chris Caras, geopend op april 7, 2026, [http://www.chriscaras.com/prophets-legacy/tirmidhi-legacy/](http://www.chriscaras.com/prophets-legacy/tirmidhi-legacy/)  
25. The Six Titans of Hadith: A Comprehensive Biographical Study of the Compilers of Al-Sihah Al-Sitta \- Ghayb.com, geopend op april 7, 2026, [https://ghayb.com/the-compilers-of-al-sihah-al-sitta/](https://ghayb.com/the-compilers-of-al-sihah-al-sitta/)  
26. Abu Dawud: A Case Study in Reliability and Authenticity \- Islamic Discourse Initiative, geopend op april 7, 2026, [https://www.islamicdiscourseinitiative.com/canon/hadith/abu-dawud-a-case-study-in-reliability-and-authenticity/](https://www.islamicdiscourseinitiative.com/canon/hadith/abu-dawud-a-case-study-in-reliability-and-authenticity/)  
27. NLP Pipeline — ENC2045 Computational Linguistics \- GitHub Pages, geopend op april 7, 2026, [https://alvinntnu.github.io/NTNU\_ENC2045\_LECTURES/nlp/nlp-pipeline.html](https://alvinntnu.github.io/NTNU_ENC2045_LECTURES/nlp/nlp-pipeline.html)  
28. The Traditions of Islam : An Introduction to the Study of Hadith Literature, by Alfred Guillaume, geopend op april 7, 2026, [https://www.answering-islam.org/Books/Guillaume/Traditions/ch4.htm](https://www.answering-islam.org/Books/Guillaume/Traditions/ch4.htm)  
29. معالم في رواية الحديث الضعيف والاستشهاد به \- مجلة رواء, geopend op april 7, 2026, [https://rawaamagazine.com/%D9%85%D8%B9%D8%A7%D9%84%D9%85-%D9%81%D9%8A-%D8%B1%D9%88%D8%A7%D9%8A%D8%A9-%D8%A7%D9%84%D8%AD%D8%AF%D9%8A%D8%AB-%D8%A7%D9%84%D8%B6%D8%B9%D9%8A%D9%81-%D9%88%D8%A7%D9%84%D8%A7%D8%B3%D8%AA%D8%B4%D9%87/](https://rawaamagazine.com/%D9%85%D8%B9%D8%A7%D9%84%D9%85-%D9%81%D9%8A-%D8%B1%D9%88%D8%A7%D9%8A%D8%A9-%D8%A7%D9%84%D8%AD%D8%AF%D9%8A%D8%AB-%D8%A7%D9%84%D8%B6%D8%B9%D9%8A%D9%81-%D9%88%D8%A7%D9%84%D8%A7%D8%B3%D8%AA%D8%B4%D9%87/)  
30. ANALIZING ISNAD-CUM-MATN OF TAUḤID PHRASE ON PROPHET'S FLAG HADITH \- e-journal UIN Suka., geopend op april 7, 2026, [https://ejournal.uin-suka.ac.id/ushuluddin/alquran/article/download/2201-04/1760](https://ejournal.uin-suka.ac.id/ushuluddin/alquran/article/download/2201-04/1760)  
31. Isnad-cum-matn analysis \- Wikipedia, geopend op april 7, 2026, [https://en.wikipedia.org/wiki/Isnad-cum-matn\_analysis](https://en.wikipedia.org/wiki/Isnad-cum-matn_analysis)  
32. What is the process of using Isnad-cum-Matn analysis like when analyzing hadiths? \- Reddit, geopend op april 7, 2026, [https://www.reddit.com/r/AcademicQuran/comments/1qegu1p/what\_is\_the\_process\_of\_using\_isnadcummatn/](https://www.reddit.com/r/AcademicQuran/comments/1qegu1p/what_is_the_process_of_using_isnadcummatn/)  
33. What does the ح mean in this hedith? : r/Muslim \- Reddit, geopend op april 7, 2026, [https://www.reddit.com/r/Muslim/comments/17ucs7m/what\_does\_the\_%D8%AD\_mean\_in\_this\_hedith/](https://www.reddit.com/r/Muslim/comments/17ucs7m/what_does_the_%D8%AD_mean_in_this_hedith/)  
34. What does this ح mean?. : r/islam \- Reddit, geopend op april 7, 2026, [https://www.reddit.com/r/islam/comments/17uc831/what\_does\_this\_%D8%AD\_mean/](https://www.reddit.com/r/islam/comments/17uc831/what_does_this_%D8%AD_mean/)  
35. Understanding the Madār in Hadith Studies | PDF \- Scribd, geopend op april 7, 2026, [https://www.scribd.com/document/329269424/The-Common-Link-and-Its-Relation-to-the-Mad%C4%81r](https://www.scribd.com/document/329269424/The-Common-Link-and-Its-Relation-to-the-Mad%C4%81r)  
36. How can Hadiths with multiple chains could have been fabricated? \- Reddit, geopend op april 7, 2026, [https://www.reddit.com/r/AcademicQuran/comments/1ar3geq/how\_can\_hadiths\_with\_multiple\_chains\_could\_have/](https://www.reddit.com/r/AcademicQuran/comments/1ar3geq/how_can_hadiths_with_multiple_chains_could_have/)  
37. The Classification Of Hadith According To The Reliability And Memory Of Reporters, geopend op april 7, 2026, [https://www.islamic-awareness.org/hadith/ulum/asb7](https://www.islamic-awareness.org/hadith/ulum/asb7)  
38. A Critical Analysis of Al-Mudtarib \- ResearchGate, geopend op april 7, 2026, [https://www.researchgate.net/publication/387685207\_A\_Critical\_Analysis\_of\_Al-Mudtarib](https://www.researchgate.net/publication/387685207_A_Critical_Analysis_of_Al-Mudtarib)  
39. The Classification Of Hadith According To The Links In The Isnad \- Islamic Awareness, geopend op april 7, 2026, [https://www.islamic-awareness.org/hadith/ulum/asb2.html](https://www.islamic-awareness.org/hadith/ulum/asb2.html)  
40. Terminology of Hadith: Language That Protects Truth From Error \- Studio Arabiya, geopend op april 7, 2026, [https://studioarabiya.com/terminology-of-hadith/](https://studioarabiya.com/terminology-of-hadith/)  
41. Chain of Command \- Sciences of Hadith | Kalamullah.Com, geopend op april 7, 2026, [https://www.kalamullah.com/Books/CoC-\_Master\_Reference.pdf](https://www.kalamullah.com/Books/CoC-_Master_Reference.pdf)  
42. Muallaq Ahadith in Bukhari | White Minaret, geopend op april 7, 2026, [https://whiteminaret.org/misquotes/muallaq-ahadith-in-bukhari/](https://whiteminaret.org/misquotes/muallaq-ahadith-in-bukhari/)  
43. شروح سنن أبي داود مع نماذج لأحاديث مشروحة \- مواقع أعضاء هيئة التدريس, geopend op april 7, 2026, [http://faculty.ksu.edu.sa/ar/aalhomaidhy/course-material/197402](http://faculty.ksu.edu.sa/ar/aalhomaidhy/course-material/197402)  
44. تحقيق ال قول فيما ورد من الرو ا يات على سبيل المذاكرة في صحيح اإلمام البخاري, geopend op april 7, 2026, [https://tadween.sa/documents/researchDatabase/120k77339z.pdf](https://tadween.sa/documents/researchDatabase/120k77339z.pdf)  
45. Fath Al Bari (selectd Sections Only) : Al-Haafiz Ibn Hajar Al-'Asqalani \- Internet Archive, geopend op april 7, 2026, [https://archive.org/details/fath-al-bari-selectd-sections-only](https://archive.org/details/fath-al-bari-selectd-sections-only)  
46. fath al bari | masud.co.uk, geopend op april 7, 2026, [https://masud.co.uk/tag/fath-al-bari/](https://masud.co.uk/tag/fath-al-bari/)  
47. Segmental Analysis-Based Authorship Discrimination between the Holy Quran and Prophet's Statements | Digital Studies / Le champ numérique, geopend op april 7, 2026, [https://www.digitalstudies.org/article/id/7268/](https://www.digitalstudies.org/article/id/7268/)  
48. Sharh Arba'een an Nawawî COMMENTARY OF FORTY HADITHS OF AN NAWAWI By Dr. Jamal Ahmed Badi, geopend op april 7, 2026, [https://ahadith.co.uk/downloads/Commentary\_of\_Forty\_Hadiths\_of\_An-Nawawi.pdf](https://ahadith.co.uk/downloads/Commentary_of_Forty_Hadiths_of_An-Nawawi.pdf)  
49. Eloquence Evidences in “Fatah Al-Bari” by Al-Asqalani: شواهد الأمر البلاغية في "فتح الباري" للعسقلاني | Alorooba Research Journal, geopend op april 7, 2026, [https://www.alorooba.org/ojs/index.php/journal/article/view/4](https://www.alorooba.org/ojs/index.php/journal/article/view/4)  
50. (PDF) Stylistic Markers Of Authenticity In Ḥadīth Texts: An Integrative Framework Bridging ʿilm Al-Ḥadīth And Literary Stylistics \- ResearchGate, geopend op april 7, 2026, [https://www.researchgate.net/publication/398812734\_Stylistic\_Markers\_Of\_Authenticity\_In\_Hadith\_Texts\_An\_Integrative\_Framework\_Bridging\_ilm\_Al-Hadith\_And\_Literary\_Stylistics](https://www.researchgate.net/publication/398812734_Stylistic_Markers_Of_Authenticity_In_Hadith_Texts_An_Integrative_Framework_Bridging_ilm_Al-Hadith_And_Literary_Stylistics)  
51. 2000 فائدة فقهية وحديثية من فتح الباري للحافظ ابن ... \- المجلس العلمي, geopend op april 7, 2026, [https://majles.alukah.net/showthread.php?t=161624\&page=2](https://majles.alukah.net/showthread.php?t=161624&page=2)  
52. ﻓﺘﺢ اﻟﺒﺎري ﰲ ﴍح ﺻﺤﻴﺢ اﻟﺒﺨﺎري زﻳﻦ اﻟﺪﻳﻦ أيب اﻟﻔﺮج ﻋﺒﺪ اﻟ \- Kezana AI, geopend op april 7, 2026, [https://kezana.ai/files/1/26205](https://kezana.ai/files/1/26205)  
53. What is Meant by Mutaba'at of a Hadith?, geopend op april 7, 2026, [https://hadithanswers.com/what-is-meant-by-mutabaat-of-a-hadith/](https://hadithanswers.com/what-is-meant-by-mutabaat-of-a-hadith/)  
54. Ameer's Q & A: Shawahid (Witnesses) and Mutabaat (Follow-ups) in the science of Hadith, geopend op april 7, 2026, [https://www.hizb-ut-tahrir.info/en/index.php/qestions/jurisprudence-questions/11062.html?tmpl=component\&print=1](https://www.hizb-ut-tahrir.info/en/index.php/qestions/jurisprudence-questions/11062.html?tmpl=component&print=1)  
55. Further Branches Of Mustalah & Rijal al-Hadith: The Classification Of Hadith & Their Reporters \- Islamic Awareness, geopend op april 7, 2026, [https://www.islamic-awareness.org/hadith/ulum/ascc.html](https://www.islamic-awareness.org/hadith/ulum/ascc.html)  
56. Introduction to the Science of Hadith \- Wikipedia, geopend op april 7, 2026, [https://en.wikipedia.org/wiki/Introduction\_to\_the\_Science\_of\_Hadith](https://en.wikipedia.org/wiki/Introduction_to_the_Science_of_Hadith)  
57. An Introduction to the Science of Hadith \- E-Books, geopend op april 7, 2026, [https://ebooks.worldofislam.info/ebooks/Hadith%20&%20Sunnah/An%20Introduction%20to%20the%20Science%20of%20Hadith.pdf](https://ebooks.worldofislam.info/ebooks/Hadith%20&%20Sunnah/An%20Introduction%20to%20the%20Science%20of%20Hadith.pdf)  
58. A Brief History of Hadith Methodology (Mustalah al-Hadith) \- IslamOnline, geopend op april 7, 2026, [https://islamonline.net/en/a-brief-history-of-hadith-methodology-mustalah-al-hadith/](https://islamonline.net/en/a-brief-history-of-hadith-methodology-mustalah-al-hadith/)  
59. IRSYAD AL-HADITH SERIES 249: MAWDU' HADITH (FAKE / FABRICATED) \- Jabatan Mufti Wilayah Persekutuan, geopend op april 7, 2026, [https://muftiwp.gov.my/en/artikel/irsyad-al-hadith/2307-irsyad-al-hadith-series-249-mawdu-fake-fabricated-hadith?templateStyle=16](https://muftiwp.gov.my/en/artikel/irsyad-al-hadith/2307-irsyad-al-hadith-series-249-mawdu-fake-fabricated-hadith?templateStyle=16)  
60. The Critical Study of the Book of Ulum Al-Hadith (Muqaddimah) by Ibn Al-Salah \- Formosa Publisher, geopend op april 7, 2026, [https://journal.formosapublisher.org/index.php/ijis/article/download/13103/12578/51512](https://journal.formosapublisher.org/index.php/ijis/article/download/13103/12578/51512)  
61. Commentary on the Forty Hadith of Al-Nawawi \- Islamic Studies, geopend op april 7, 2026, [https://muqith.wordpress.com/wp-content/uploads/2015/12/commentary-on-the-forty-hadith-of-al-nawawi.pdf](https://muqith.wordpress.com/wp-content/uploads/2015/12/commentary-on-the-forty-hadith-of-al-nawawi.pdf)