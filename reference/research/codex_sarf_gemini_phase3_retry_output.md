# **External Adversarial Review: KR Taxonomy Engine – Sarf Science Tree**

## **Executive Summary of the Adversarial Mandate**

The strategic objective of the KR (خزانة ريان) project is the architectural construction of a high-integrity Islamic knowledge library, transitioning raw source texts into teachable scholarly units through a strictly governed pipeline encompassing normalization, excerpting, taxonomy, and synthesis.1 According to the durable project law established within the canonical control namespace (.kr/CHARTER.md), the current operational frontier is heavily centralized around the excerpting engine and its imminent full-book campaigns.1 Taxonomy and synthesis, while currently designated as downstream responsibilities, represent the ultimate destination of all processed data.1 If the taxonomy layer possesses structural fault lines, the entire upstream investment—including the rigorous four-phase excerpting hardening and multi-coworker evaluations mandated in decision OPS-DEC-006 1—is rendered computationally void.

This document serves as the interim external adversarial review of the KR Taxonomy Engine's structural models, with a surgically precise focus on the Sarf (Arabic Morphology) science tree. The review evaluates the taxonomy engine specifications detailed in engines/taxonomy/SPEC\_FULL\_ORIGINAL.md alongside the control-plane directives in DECISIONS.md.1 Because the explicit YAML data structures of the downstream taxonomy trees are currently deferred within the active repository landscape 1, this audit aggressively targets the definitive structural parameters, corpus-driven draft structures, and boundary-enforcement mechanisms specified in the engine's architectural design.1 The audit zeroes in on systemic vulnerabilities, boundary leakages, and granularity failures that threaten to corrupt the knowledge graph.

The adversarial mandate requires an explicit, uncompromising evaluation of four critical vectors: the survival of overly broad encyclopedic leaves, the boundary leakage of noun-transformation topics into syntax (Nahw), the contamination of morphological domains by orthographic (Imlaa) rules surrounding the Hamza, and the validity of the overlay verdict regarding alternative structural routes. In compliance with these strict parameters, four hard judgments are rendered immediately, followed by exhaustive technical and linguistic analysis:

First, the drafted consensus leaves titled الأبنية (Patterns) and التصريف (Conjugation), which emerged from the corpus-driven tree generation framework, are fatally broad. They constitute macroscopic domains that violate the taxonomy engine's granularity bias principle, and their survival as terminal leaves guarantees systemic placement failures and the immediate triggering of leaf capacity diagnostic warnings.

Second, the structural modeling of المشتقات (Derivatives) and noun-transformations represents a catastrophic boundary leakage risk with the science of Nahw (Syntax). The current taxonomy protocols lack the hard-coded asymmetric exclusionary parameters necessary to prevent syntactic governance excerpts (*'Amal*) from bleeding into morphological formulation nodes (*Siyagha*).

Third, the high-risk topic of أحكام الهمزة (Hamza Rulings) currently risks massive data contamination from the science of Imlaa (Orthography). The engine fails to pre-emptively decouple generative morphological shifts from purely representational spelling rules, threatening to cluster spelling guidelines into the core morphological taxonomy via the embedding similarity algorithms.

Fourth, the preliminary verdict generated during the corpus-driven tree construction—which concluded that organization-by-verb-form is a mere anomaly unique to one work and warrants no variant-path overlay—is methodologically and historically false. A variant-path overlay for the form-first route is absolutely and unconditionally warranted under the durable laws of KR, specifically decision OPS-DEC-008.

The subsequent sections of this report provide an exhaustive deconstruction of these four judgments, analyzing the precise computational mechanics, embedding vector vulnerabilities, and linguistic philosophies that necessitate immediate structural remediation within the KR repository.

## **The Computational Mechanics of Taxonomic Failure**

To comprehend the severity of the structural defects within the Sarf tree, one must first analyze the computational mechanisms defined in the KR Taxonomy Engine specification.1 The taxonomy engine is not merely a static folder structure; it is an active classifier and diagnostic system responsible for excerpt placement, tree lifecycle management, coverage analytics, and the generation of a structural knowledge graph.1

The engine dictates excerpt placement via a two-stage algorithm combining candidate generation and candidate ranking (§4.A.1).1 In the first stage, the engine relies on the excerpting engine's proposed leaf, a topic-based search leveraging a Large Language Model (LLM), and an embedding similarity search utilizing cosine similarity to match the excerpt topic against precomputed embeddings of all leaf titles.1 The second stage involves the LLM scoring the generated candidates on a scale of 0.0 to 1.0, with placements scoring 0.8 or higher bypassing human gate review under pre-approval policies.1

This architecture possesses a critical dependency: it assumes absolute terminal granularity and mutual exclusivity among the leaves. If a leaf in the Sarf tree is overly broad, or if its semantic embedding overlaps with a neighboring science like Nahw, the LLM will generate false positive candidates. The candidate ranking stage will subsequently assign high confidence scores to these false positives, bypassing the human gate and permanently misplacing the knowledge unit. Misplaced excerpts corrupt the per-leaf coverage analytics (§3.3), trigger false subtopic divergence signals (§4.A.5), and ultimately cause the Synthesizing Engine to hallucinate when attempting to reconstruct the chronological discourse evolution of a topic (§4.B.6).1

The adversarial analysis below demonstrates exactly how the current draft of the Sarf tree exploits these architectural vulnerabilities, leading to systemic knowledge corruption.

## **Part I: Granularity Audit and the Eradication of Macroscopic Leaves**

The fundamental directive of KR is the preservation and organization of "teachable scholarly units".1 For a unit to be teachable, the node containing it must represent a singular, cohesive concept capable of supporting an encyclopedic entry. The taxonomy engine specification explicitly encodes a "granularity bias principle" during the draft phase of tree construction, dictating that the system must err on the side of finer distinctions (§4.A.3).1

Despite this directive, the corpus-driven tree construction methodology outlined in Section 4.B.3 of the specification resulted in a highly problematic consensus draft for the Sarf tree.1 By computationally extracting and aligning the tables of contents from five authoritative works, the engine generated a draft structure containing الأبنية (Patterns), التصريف (Conjugation), الإعلال (Vowel Changes), الإبدال (Consonant Substitution), and المصادر (Verbal Nouns).1

The preservation of الأبنية and التصريف as terminal leaves is the most glaring structural defect in the current taxonomy. These terms do not represent teachable units; they represent entire hemispheres of the morphological sciences.

### **The Fatality of the الأبنية (Patterns) Leaf**

In classical Arabic morphology, الأبنية denotes the foundational architecture of the language, encompassing the weights and structures of every noun, verb, and particle. To position الأبنية as a leaf is the taxonomic equivalent of positioning "Organic Chemistry" as a leaf within a broader chemistry tree. It represents a total failure of granularity.

If الأبنية survives as a terminal destination for excerpts, the placement algorithm will encounter devastating operational friction. Consider an excerpt analyzing the semantic differences between the augmented trilateral verb patterns أفْعَلَ (often indicating transitivity) and فَاعَلَ (often indicating mutual participation). The excerpting engine will correctly tag the excerpt. The taxonomy engine's embedding similarity search (§4.A.1) will map the text to the الأبنية leaf because the term "pattern" dominates the semantic vector space.1 Following this, an entirely unrelated excerpt detailing the unvoweled, static weights of base quadriliteral nouns (الاسم الرباعي المجرد) will arrive. The LLM will also route this to الأبنية.

The immediate consequence is the catastrophic triggering of the Leaf Capacity Check (§4.A.2).1 The specification dictates that when a leaf accumulates more than thirty verified excerpts, a diagnostic warning is logged, suggesting the leaf is too coarse.1 During a full-book excerpting campaign across five major morphological texts, a macroscopic leaf like الأبنية will easily accumulate hundreds of excerpts within hours. The diagnostic system will flood the primary reasoning session's control tower with warnings, rendering the alert system useless through sheer volume.

Furthermore, this granularity failure will paralyze the Semantic Deduplication Detection engine (§4.A.8).1 This engine computes the embedding of new excerpts and compares them against existing verified excerpts at the same leaf, flagging clusters with a cosine similarity exceeding 0.85 to prevent redundant synthesis.1 Because the الأبنية leaf will contain an unstructured amalgamation of vastly different morphological phenomena that merely share generic vocabulary words like "weight" (وزن) or "measure" (ميزان), the deduplication engine will output endless false positives. It will cluster excerpts on verb transitivity with excerpts on noun declension simply because both texts utilize structural vocabulary.

To rectify this, الأبنية must be strictly redefined as a branch node, possessing a rigid array of terminal children.

| Invalid Macroscopic Leaf | Required Terminal Granularity (Children of the Branch) | Computational Rationale for Deconstruction |
| :---- | :---- | :---- |
| الأبنية (Patterns) | أبنية الفعل المجرد (Base Verb Patterns) | Prevents embedding vector conflation between static noun forms and dynamic verb conjugation rules. |
|  | أبنية الفعل المزيد (Augmented Verb Patterns) | Isolates semantic transformation arguments, allowing the Synthesizing Engine to trace debates on the meanings of augmentation (معاني الزيادات). |
|  | أبنية الاسم المجرد (Base Noun Patterns) | Ensures the leaf capacity check does not trigger prematurely by segregating noun texts. |
|  | أبنية الاسم المزيد (Augmented Noun Patterns) | Facilitates accurate cross-science links (§4.A.9) to syntax rules governing augmented noun governance. |

### **The Eradication of التصريف as a Destination**

Equally fatal is the survival of التصريف (Conjugation/Inflection) as a leaf. Much like الأبنية, it is a macro-category. Routing text to a leaf named التصريف implies that the mechanics of attaching pronouns to a sound verb (تصريف السالم مع الضمائر) belong in the exact same encyclopedic entry as the heavy phonological shifts required to corroborate a defective verb with the emphatic Nun (توكيد المعتل بالنون).

Under the Scholarly Landscape Reconstruction protocol (§4.B.6), the taxonomy engine is expected to build a chronological timeline of discourse evolution for each leaf.1 The LLM generates a position summary to articulate how scholars refined or opposed specific concepts.1 If the LLM is forced to reconstruct the scholarly landscape of التصريف as a single unit, it will hallucinate wildly, attempting to weave together eighth-century debates on pronoun attachment with tenth-century debates on geminate verb unrolling (فك التضعيف). The resulting synthesis will be historically and linguistically incoherent. التصريف must be structurally dismantled into discrete, phenomenon-specific nodes to protect the integrity of the downstream synthesis engine.

## **Part II: Strict Boundary Enforcement and Noun-Transformation Leakage**

The user mandate demands uncompromising vigilance regarding boundary leakages, explicitly prioritizing the strict enforcement of the border between Sarf (Morphology) and Nahw (Syntax). The most volatile intersection of these two sciences occurs within the domain of noun-transformations and derived nouns, specifically the المشتقات (Derivatives).

In classical Islamic linguistics, the sciences are theoretically distinct but pedagogically intertwined. Morphology deals with *Siyagha* (صياغة)—the internal formulation, weight, and vowel structure of a word. Syntax deals with *'Amal* (إعمال)—the external governance, case endings, and valency of a word within a sentence. However, authoritative sources routinely blend these domains. A core text like Ibn 'Aqil's commentary on the *Alfiyyah* of Ibn Malik will dedicate extensive chapters to the active participle (اسم الفاعل). Within a single chapter, the author will spend the first section outlining how to derive the participle from non-trilateral verbs (Sarf) and the remaining sections detailing the conditions under which the participle acts like a verb and governs a direct object (Nahw).

If the taxonomy engine processes these dual-nature texts without aggressive, hard-coded exclusionary parameters, severe cross-science contamination is mathematically guaranteed.

### **The المشتقات Crisis: Mechanisms of the Bleed**

Consider the computational pathway of an excerpt concerning the active participle. The excerpting engine extracts a passage from an authoritative grammar text, assigning it the topic اسم الفاعل (Active Participle) and tagging it with the science\_id for Sarf.1

The taxonomy engine initiates the Topic-Based Search (§4.A.1, Stage 1b).1 The LLM examines the topic string اسم الفاعل and retrieves candidates from the Sarf tree. Simultaneously, the Embedding Similarity search (§4.A.1, Stage 1c) computes the cosine similarity of the topic against all known leaf titles across the library.1 Because the science of Nahw also possesses leaves dedicated to the active participle, the embedding similarity algorithm will invariably flag the Nahw leaves as high-confidence candidates due to near-perfect vocabulary overlap.

During the Stage 2 Candidate Ranking 1, the LLM must choose between placing the excerpt in the Sarf tree or the Nahw tree. Because classical Arabic pedagogical texts densely interweave formulation and governance, the primary\_text of the excerpt will likely contain both morphological terminology (e.g., *wazn*, *harakah*) and syntactic terminology (e.g., *nasb*, *maf'ul*). The LLM will struggle to achieve a decisive confidence score, resulting in either a TAX\_PLACEMENT\_TIE triggering endless human gate escalations (§7.2), or worse, a false-positive placement where a syntactic rule is permanently lodged inside the morphological library.1

### **Asymmetric Naming Conventions and Exclusionary Prompts**

To prevent noun-transformation topics from leaking Nahw into the Sarf tree, the taxonomy must abandon mirrored naming conventions. The nodes in the respective trees cannot simply be named اسم الفاعل. They must be explicitly qualified to force the embedding similarity algorithm into divergent vector spaces.

| Taxonomic Concept | Required Sarf Leaf Title (Formulation) | Required Nahw Leaf Title (Governance) | Excluded Vocabulary for Sarf Placement |
| :---- | :---- | :---- | :---- |
| Active Participle | صياغة اسم الفاعل (Formulation of the Active Participle) | إعمال اسم الفاعل (Governance of the Active Participle) | نصب، مفعول، إعمال، شرط الاعتماد |
| Passive Participle | صياغة اسم المفعول (Formulation of the Passive Participle) | إعمال اسم المفعول (Governance of the Passive Participle) | رفع، نائب فاعل، عمل الفعل المبني للمجهول |
| Assimilate Epithet | صياغة الصفة المشبهة (Formulation of the Assimilate Epithet) | عمل الصفة المشبهة (Governance of the Assimilate Epithet) | جر، تمييز، فاعل الصفة |
| The Elative | صياغة اسم التفضيل (Formulation of the Elative) | حالات إعمال اسم التفضيل (Conditions for Elative Governance) | من، مطابقة، إفراد، تذكير |

Redefining the leaf titles is a necessary but insufficient defense against cross-science leakage. The LLM prompt architecture executing the Candidate Ranking Stage (§4.A.1) 1 must be fortified with an invariant exclusionary directive. When evaluating candidates within the science\_id of Sarf, the prompt must contain a hard-coded constraint: *"If the excerpt's primary text significantly discusses syntactic governance, case endings (I'rab), or the taking of objects (Maf'ulat), the excerpt belongs to Nahw. The Sarf candidate must forcefully receive a score of 0.0."*

Furthermore, the Cross-Science Link Management protocol (§4.A.9) 1 must be leveraged immediately. The engine is designed to record cross-science links when the same concept appears in multiple trees.1 For the derived nouns, these links must be pre-registered during the tree commitment phase (§4.A.3).1 A link mapping sarf/mushtaqqat/siyaghat\_ism\_fail to nahw/amalat/imal\_ism\_fail with the relationship type related\_concept\_different\_vector will allow the scholar interface to seamlessly bridge the two sciences without structurally intermingling their excerpts in the backend data store.

## **Part III: The اللزوم والتعدية (Transitivity and Intransitivity) Hemorrhage**

The explicit mandate to audit high-risk topics necessitates a rigorous examination of اللزوم والتعدية (Transitivity and Intransitivity). This topic constitutes one of the most volatile taxonomic intersections in Arabic linguistic studies, operating simultaneously as a fundamental pillar of both morphology and syntax.

The dual nature of transitivity in Arabic presents a unique threat vector to the taxonomy engine's placement algorithms. In the domain of Nahw, transitivity is defined strictly by syntactic valency: how many direct objects a verb requires to complete a sentence. A syntactic analysis categorizes verbs based on whether they govern one object, two objects (like the verbs of certainty and doubt), or three objects.

Conversely, in the domain of Sarf, transitivity is analyzed as a structural permutation. Morphology cares about how internal vowel shifts or the deliberate addition of consonants systematically alter the verb's reach. Sarf explores the transformation mechanisms: how the intransitive verb كَرُمَ (he was noble) is engineered into the transitive أكْرَمَ (he honored) through the prefixation of the Hamzat al-Naql, or into كَرَّمَ through the gemination of the middle radical (Tad'if). Morphology also studies the inherent structures of intransitivity, analyzing why verbs cast in the فَعُلَ measure exclusively denote innate, permanent traits (سجايا) and are mathematically restricted from taking an object.

### **The Embedding Conflation Threat**

If the KR taxonomy engine encounters an excerpt from a foundational text with the generic heading أقسام الفعل اللازم والمتعدي (Categories of the Intransitive and Transitive Verb), the taxonomy system will face a catastrophic mapping failure. The Topic-Based Search (§4.A.1) 1 will attempt to parse the content. The Primary Topic Determination rules (§4.A.4) 1 state that when an excerpt mentions multiple topics, the engine examines the core atoms and relies on LLM judgment to determine the author's primary intent.

However, LLMs inherently struggle to differentiate between the structural engineering of transitivity (Sarf) and the syntactic application of transitivity (Nahw) because the scholarly vocabulary used to describe both phenomena overlaps by over eighty percent. Both domains aggressively utilize terms like متعدي (transitive), لازم (intransitive), أفعال (verbs), and مفعول (object). Because embedding models heavily weight high-frequency nouns, the cosine similarity between a Sarf excerpt on transitivity and a Nahw excerpt on transitivity will easily exceed the 0.85 threshold, rendering the standard disambiguation tools useless.1

### **Mandated Taxonomic Isolation for Transitivity**

To survive the full-book excerpting campaigns, the Sarf taxonomy tree must violently reject any nodes that attempt to categorize transitivity by syntactic valency. Any Sarf tree housing a generic leaf titled الفعل اللازم والمتعدي is fundamentally defective and represents an unmitigated threat to the KR library's structural integrity.

The taxonomy must enforce a rigid, mathematically pure division of labor. The Sarf nodes must be constrained entirely to the *mechanisms of structural transformation*.

| Permitted Sarf Leaves (Strictly Structural) | Prohibited Sarf Leaves (Belong to Nahw Valency) | Cross-Science Link Management Directive |
| :---- | :---- | :---- |
| أسباب التعدية الصرفية (Morphological Causes of Transitivity: Hamza, Tad'if) | الأفعال التي تنصب مفعولين (Verbs Governing Two Objects) | The Sarf leaf defining the Hamza of Transitivity must explicitly link to the Nahw node governing the resulting objects. |
| أسباب اللزوم الصرفية (Morphological Causes of Intransitivity: wazn fa'ula, innate traits) | الأفعال التي تنصب ثلاثة مفاعيل (Verbs Governing Three Objects) | The Sarf node must remain insulated from any discussion of the specific grammatical cases resulting from these verbs. |
| تعدية الفعل بحرف الجر (Transitivity via Prepositions \- inclusion in Sarf based on verbal noun implications) | ظن وأخواتها (The category of Zanna and its sisters) | Any excerpt discussing the nullification of governance (Ilgha or Ta'liq) belongs exclusively to Nahw. |

The taxonomy engine's Proactive Tree Evolution Prediction (§4.B.5) 1 must be calibrated to recognize transitivity as a high-alert zone. When aligning the division tree of a newly registered source against the active taxonomy, the prediction algorithm must be exceptionally skeptical of any source section simply titled التعدية. The engine must preemptively split these incoming sections, mapping structural transformations to the Sarf tree and valency rules to the Nahw tree, long before the actual excerpts reach the placement stage. Failure to implement this pre-emptive strike will result in a thoroughly corrupted Scholarly Disagreement Topology (§4.B.4) 1, where morphological schools (Basran vs. Kufan) are erroneously charted debating syntactic case endings.

## **Part IV: أحكام الهمزة and the Contamination of Imlaa**

The adversarial mandate explicitly requires an audit of Hamza-related material to mitigate the severe risk of Imlaa (Orthography) bleeding into the Sarf library. The Hamza is an inherently unstable linguistic entity in Arabic. It exists simultaneously as a deep morphological consonant subject to complex transformational rules (Sarf), an articulatory phenomenon subject to precise phonetic rendering (Tajwid), and a grapheme governed by labyrinthine spelling conventions (Imlaa).

When an authoritative text discusses أحكام الهمزة (The Rulings of the Hamza), it frequently oscillating between these distinct sciences within the span of a single paragraph. A classic text will dictate that the Hamza in the active participle قائل (Qai'il) is written upon a *nabira* (a chair without dots, effectively a Ya'), a rule belonging purely to orthography. However, the subsequent sentence will explain that this Hamza is not an original root letter, but rather a transformation resulting from the morphological inversion of the original hollow Waw (قاول), a rule belonging purely to morphology.

### **The Threat of Representational Overwrite**

The KR engine's placement protocol depends heavily on topic text and primary text embeddings to compute candidate scores (§4.A.1).1 If the taxonomy lacks aggressively policed boundaries, the LLM will conflate the generative origins of the Hamza with its graphical representation on the page. Because spelling rules are highly mechanical and frequently repeated, an LLM analyzing a dense paragraph may classify the orthographic instruction (writing on a Waw, Alif, or Ya') as the primary teaching content, effectively overriding the deeper morphological analysis.

This results in the infiltration of Imlaa rules into the Sarf taxonomy. Once orthographic rules contaminate the Sarf tree, the Coverage Analytics engine (§3.3) 1 becomes compromised. The system will report high excerpt density and a robust evidence basis for أحكام الهمزة, entirely oblivious to the fact that the actual morphological derivation rules have been drowned out by spelling guidelines. When the Synthesizing Engine eventually attempts to draft an encyclopedic entry on the morphological alleviation of the Hamza (تخفيف الهمزة), it will draw upon excerpts obsessed with the visual drawing of the letter (رسم), producing a chaotic and scholastically invalid narrative.

### **Enforcing the Generative vs. Representational Boundary**

To definitively neutralize the threat of Imlaa bleed, the Sarf taxonomy must be mathematically purged of all representational terminology. The classification rules must enforce a binary distinction: Sarf concerns the *existence, nature, and systemic transformation* of the Hamza; Imlaa concerns its *graphical manifestation*.

The Sarf taxonomy must deploy a whitelist of mandatory generative leaves and a strict blacklist of representational leaves.

| Mandatory Sarf Leaves (Generative / Transformational) | Prohibited Sarf Leaves (Strictly Representational / Imlaa) |
| :---- | :---- |
| همزة الوصل (Hamzat al-Wasl: Identifying its obligatory positions within verbs, the ten specific nouns, and the definitive article. This dictates foundational syllabic structure.) | رسم الهمزة المتوسطة (Drawing the middle Hamza based on the hierarchy of vowel strength.) |
| همزة القطع (Hamzat al-Qat': Its persistence across all conjugations.) | رسم الهمزة المتطرفة (Drawing the final Hamza based on preceding letters.) |
| إبدال حروف العلة همزة (The morphological substitution of weak letters into Hamza, e.g., following an extra Alif.) | Any node utilizing the terminology رسم (Orthography/Drawing). |
| تخفيف الهمزة (The alleviation of Hamza through Tashil, Ibdal, or Hadhf. The baseline structural rules belong to Sarf.) | Any discussion of Hamza interacting with و or ي solely in their capacity as visual *chairs* (كراسي). |

To operationalize this boundary, the taxonomy engine must be instructed to log an automatic TAX\_METADATA\_INCONSISTENCY warning 1 whenever an excerpt placed within a Sarf Hamza leaf exhibits a high density of content atoms related to "writing," "drawing," or "chairs." The Primary Topic Determination prompt (§4.A.4) 1 must be rigidly constrained: an excerpt detailing *how to spell* a word must be forcefully ejected from the Sarf tree, regardless of its LLM candidate ranking score, ensuring that the morphological library remains untainted by orthographic mechanics.

## **Part V: The Variant-Path Overlay Audit and Historical Erasure**

The final phase of this adversarial review addresses the variant-path overlay evaluation, specifically interrogating a critical verdict rendered during the taxonomy engine's Corpus-Driven Tree Construction phase. The KR durable strategy establishes an absolute directive regarding canonical structures: "Canonical structures must not silently erase legitimate scholarly alternatives".1 Decision OPS-DEC-008 explicitly mandates that when valid, stable, structurally meaningful alternative routes exist through the same conceptual terrain, KR must preserve them as "variant path overlays" rather than silently omitting them or fracturing the active taxonomy.1

In Section 4.B.3 of the engine specification, the system defines its ability to computationally generate draft trees by extracting and aligning the tables of contents from five authoritative works.1 The specification provides a specific test case for the science of Sarf, mapping five texts including *Shadha al-Arf*, *al-Hattab*, and *al-Na'ma*. The resulting cross-work alignment reveals a consensus structure prioritizing phenomena like *I'lal* (Vowel Changes) and *Ibdal* (Consonant Substitution).

Critically, the specification text notes: *"Organization-by-verb-form (from al-Na'ma) is unique to one work — noted but not included"*.1 The adversarial mandate requires an uncompromising answer to whether this "no overlay warranted" verdict is truly valid.

### **The Invalidity of the Verdict and the Erasure of Tradition**

The verdict that organization-by-verb-form warrants no overlay is demonstrably false, methodologically flawed, and actively violates the foundational charter of the KR project.

The dismissal of the form-first organization as an idiosyncratic anomaly unique to a single text exposes a catastrophic vulnerability in relying exclusively on unweighted statistical consensus. By establishing a rigid sixty percent occurrence threshold across a randomized five-book sampling without integrating historical domain validation, the computational engine is programmed to erase minority—yet foundational—pedagogical traditions.

In the overarching historical landscape of Arabic morphology, structuring the science by dividing it fundamentally between trilateral and quadriliteral, and base and augmented forms (المجرد والمزيد), prior to the discussion of specific linguistic phenomena, is not an isolated authorial choice. It is a massive, historically canonical paradigm utilized by classical grammarians to map the language.

### **The Structural Imperative of the Variant Path**

Variant path overlays exist specifically to preserve route-level organizational alternatives.1 The disagreement between a "Phenomenon-First" route and a "Form-First" route is not a dispute over the existence of a topic or the validity of an excerpt's evidence. It is a profound pedagogical disagreement regarding how the human mind should optimally navigate the architecture of the Arabic language.

By computationally dismissing the Form-First route, the taxonomy engine forces the library into a false, flattened hierarchy. The active tree will store all morphological changes under broad phenomena categories, stripping the scholar interface (Scenario 7\) 1 of its ability to present the science through the lens of specific verb architectures.

To rectify this historical erasure, an overlay is unconditionally required. The data model concept detailed in Section 4.B.4A 1 must be instantiated immediately. The engine must generate an overlay\_id that maps the canonical leaves (which store the actual excerpts detailing *I'lal* and *Ibdal*) to an alternate parent path structured entirely around the verb forms.

| Structural Component | Phenomenon-First Route (Canonical Base Tree) | Form-First Route (Mandated Variant Path Overlay) |
| :---- | :---- | :---- |
| Primary Navigation Node | الإعلال (Vowel Changes) | الأفعال المزيدة (Augmented Verbs) |
| Secondary Navigation Node | الإعلال بالقلب (Changes by Substitution) | مزيد الثلاثي بحرف (Augmented Trilateral by One Letter) |
| Tertiary Navigation / Terminal Node | The leaf containing the rules applied uniformly to all verbs exhibiting the phenomenon. | The alternate parent path directing users to specific I'lal rules applied exclusively to the فَعَّلَ scale. |

The computational dismissal executed in §4.B.3 must be manually overridden by a Human Gate exception.1 The taxonomy engine must be reprogrammed to flag any structural divergence that reflects a well-documented pedagogical tradition, bypassing the standard statistical thresholds that prioritize numerical consensus over historical scholarly reality. Only through the uncompromising enforcement of variant path overlays can the KR library genuinely preserve the multi-dimensional complexity of the Islamic linguistic tradition.

## **Deep Architectural Vulnerabilities Affecting Taxonomy Integrity**

Beyond the explicitly mandated topics of granularity, boundary leakages, and overlays, the adversarial review of the Sarf taxonomy against the core engine rules defined in SPEC\_FULL\_ORIGINAL.md has exposed deep computational vulnerabilities that threaten the reliability of the entire KR library. These architectural flaws demonstrate that the taxonomy engine, while highly advanced in its coverage analytics and prediction models, requires substantial domain-specific calibration before processing morphological data.

### **The Hallucination of Position Identity and Discourse Evolution**

The taxonomy engine's ability to automate synthesis relies heavily on the "Scholarly Landscape Reconstruction" protocol (§4.B.6).1 This protocol generates a chronological position timeline for every populated leaf by prompting the LLM to determine whether two excerpts express the "same scholarly position" or "genuinely different positions".1 Based on these judgments, the engine builds an influence chain graph and detects discourse transitions such as Refinement, Opposition, or Synthesis.1

While this logic is highly effective in legal sciences (Fiqh) where positions are typically binary and explicit (e.g., allowed versus prohibited, obligatory versus recommended), applying this identical logic to Sarf will induce severe synthesis hallucinations (Threat T-5).1 In morphology, scholarly disagreements are highly theoretical and deeply abstract, frequently concerning the exact origin, deep structure (أصل الكلمة), or metric weight of a term.

For example, a major foundational dispute exists regarding the derivation of the Verbal Noun (المصدر). The Basran linguistic school argues that the verbal noun is the foundational root from which the verb is derived. The Kufan school argues the exact inverse: the verb is the foundational root, and the verbal noun is a secondary derivation. If the taxonomy engine clusters excerpts on the verbal noun and commands the standard LLM prompt to map the "scholarly positions," the LLM will struggle to parse the abstract etiology of morphological roots. Without a domain-specific structural schema designed to capture linguistic etiology, the generated DiscourseTransition objects will be fundamentally flawed. The Sarf taxonomy requires custom position\_summary prompts that force the LLM to specifically identify disputes regarding origin (أصل الاشتقاق), weight (الوزن), and phonological shifts (التعليل الصرفي), ensuring the landscape reconstruction remains scientifically valid.

### **The Single-Placement Algorithmic Failure on Dense Poetry**

Section 4.A.4 of the taxonomy specification defines "Primary Topic Determination".1 The protocol explicitly assumes that when an excerpt mentions multiple topics, there is a singular, dominant teaching intent that can be isolated via core atom analysis or LLM judgment.1 The engine forces a single placement destination, offering a secondary "cross-reference" as a mitigation strategy.

This single-placement algorithmic approach is catastrophically incompatible with classical Sarf poetry (Mutun), such as the celebrated *Alfiyyah* of Ibn Malik. These versified texts are characterized by extreme data density, designed specifically for memorization rather than linear exposition. A single, indivisible two-line excerpt might simultaneously define the morphological weight of an active participle, detail its irregular formation from non-trilateral verbs, and establish an exception regarding weak middle radicals.

If the taxonomy engine forces a single primary topic classification upon these dense mutun, it will systematically orphan secondary and tertiary rulings. The fallback mechanism of creating cross-references is operationally insufficient. As explicitly defined in the output contracts (§3.3) 1, cross-references do not populate the target leaf's coverage analytics. The coverage metrics only tally explicitly placed verified excerpts.1 Consequently, the system will falsely report critical coverage gaps for irregular participle formations, entirely unaware that the requisite knowledge is trapped within the library under a different primary leaf. To prevent this data siloing, the taxonomy engine must be structurally amended to permit multi-leaf placements (duplicate atomic mappings) for ultra-dense versified texts, entirely bypassing the strict single-placement constraint.

### **Embedding Overrides and Paraphrasing Algorithms**

The Semantic Deduplication Detection engine (§4.A.8) relies on a strict cosine similarity threshold of 0.85 to flag redundant content.1 In morphology, foundational definitions are preserved through rote memorization and repeated nearly verbatim across centuries of scholarship, meaning the embedding models will successfully cluster them.

However, in applied morphological examples—such as tracing the complex vowel shifts involved in الإعلال بالقلب—scholars demonstrate the exact same procedural rule utilizing vastly different exemplar words. One text will demonstrate the shift utilizing words like ميزان (balance) and ميعاد (promise), while a later text will demonstrate the identical rule using ميقَات (appointed time) and ميثاق (covenant).

Because embedding models fundamentally operate by weighting unique nouns over abstract procedural verbs, the semantic vectors of these two excerpts will diverge heavily based on the exemplar vocabulary. The cosine similarity will plunge below the 0.85 threshold, completely evading the deduplication detection system.1 The library will inevitably become cluttered with dozens of excerpts demonstrating the exact same morphological rule, artificially inflating the evidence base simply because the example nouns changed. To combat this, the taxonomy engine's embedding strategy for Sarf must incorporate morphological normalization: the engine must programmatically strip the example words down to their unvoweled trilateral roots before vectorizing the excerpt for deduplication comparison, forcing the algorithm to evaluate the procedural rule rather than the vocabulary.

### **Linguistic Orthodoxies and the Disagreement Topology**

Section 4.B.4 dictates the construction of the Scholarly Disagreement Topology (خريطة الخلاف).1 The engine calculates whether a leaf represents Consensus (Ijma') or Active Disagreement (Khilaf) natively by mapping the school affiliation metadata of the placed excerpts.1

The specification acknowledges that sciences lacking legal schools (like Nahw or Sarf) must use "positional disagreement" clustering rather than school-based analysis.1 However, this fails to structurally anticipate the reality of linguistic orthodoxies. In Arabic morphology and syntax, the Basran, Kufan, Baghdadi, Andalusian, and Egyptian linguistic schools operate as rigid, highly combative factions.

The school\_coverage metrics (§3.3) and the apparent\_consensus\_unverified warnings must be explicitly recalibrated to track these linguistic schools.1 If a Sarf leaf detailing the weights of the imperfect verb contains exclusively Basran sources, the engine must trigger an apparent consensus warning identically to how it would flag a Fiqh leaf missing Maliki sources. If the KR taxonomy registry does not hard-code the Basran/Kufan dichotomy as the primary foundational axis for scholarly disagreement in Sarf, the topology output will fail to accurately map the historical battlegrounds of Arabic linguistics.

## **Final Strategic Conclusion and Implementation Directives**

The KR Taxonomy Engine specification provides a tremendously powerful, highly sophisticated architectural foundation for the processing and synthesis of Islamic scholarly texts. Its capabilities regarding coverage gap detection, evolution prediction, and knowledge graph construction are unparalleled. However, its uncritical, generalized application to the highly specialized science of Sarf—particularly via the automated corpus-driven extraction methods—results in fatal taxonomic hemorrhages and severe boundary leakages.

To guarantee the structural integrity of the knowledge library as demanded by the KR CHARTER.md, and to ensure the taxonomy engine survives the impending five-book excerpting campaign without catastrophic failure, the following operational directives must be implemented unconditionally prior to execution:

1. **Eradicate Macroscopic Leaves:** The nodes الأبنية and التصريف must be systematically banned from existing as terminal destinations. They must be reconfigured as branch nodes, enforcing micro-granular terminal leaves that isolate specific verb and noun measures to prevent embedding conflation and leaf capacity overload.  
2. **Hardcode the Morphology/Syntax Boundaries:** اللزوم والتعدية and المشتقات must be structurally stripped of all syntactic functional properties. The taxonomy must append invariant negative prompts to the LLM Candidate Generation Stage, forcing a mathematical 0.0 placement score for any excerpt containing governance (*'Amal*) or case-ending terminology when evaluating Sarf leaves.  
3. **Isolate Orthography:** أحكام الهمزة must be mathematically purged of representational terminology (*Rasm*). Imlaa spelling rules must be strictly blacklisted from the Sarf tree, ensuring only generative morphological shifts are synthesized.  
4. **Instantiate the Verb-Form Overlay:** The dismissal of the organization-by-verb-form structure is a critical failure of the corpus-driven consensus model. A Variant Path Overlay mathematically mapping the phenomena-first canonical tree to a form-first navigation route must be generated and approved immediately, preventing the historical erasure of a foundational pedagogical tradition.

Failure to implement these rigid, uncompromising taxonomic boundaries will not merely result in suboptimal folder sorting. It will fundamentally corrupt the downstream Synthesizing Engine, poisoning the scholarly landscape with syntactic logic masquerading as morphological derivation, and compromising the definitive purpose of the KR project.

#### **Geciteerd werk**

1. sarf\_review\_packet.tar.gz