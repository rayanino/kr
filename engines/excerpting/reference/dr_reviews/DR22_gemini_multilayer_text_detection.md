Computational Stratigraphy in Classical Arabic Texts: Detecting and Preserving Multi-Authorial Layers


The computational processing of classical Arabic Islamic scholarship presents a profoundly unique challenge within the domain of digital humanities and natural language processing. The fundamental issue is rooted in the historical nature of knowledge transmission within the Islamic intellectual tradition, which heavily utilized a highly stratified, accretive model of authorship. A single physical page of a classical text is rarely the product of a single, isolated author. Rather, it is a complex, interleaved stack of distinct authorial layers separated by decades or even centuries.1
These layers generally include the foundational base text (Matn), an expansive pedagogical commentary (Sharh), a highly technical super-commentary (Hashiyah), marginal student glosses (Ta'liqah), and the modern editor's critical apparatus (Tahqiq).1 In the manuscript era, these texts were often woven together through a "spiral form" of layout, where expansive commentaries physically wrapped around the concise base text, utilizing the poetics of physical space to denote intellectual hierarchy.3 Modern publishing houses have standardized these spatial relationships, though their typographic conventions vary significantly.
To extract meaning, trace conceptual lineage, or train advanced language models on this corpus, a computational system must first disentangle this textual stratigraphy. The system must algorithmically determine which author is speaking in any given sentence, respecting the indivisible semantic relationships between a commentary and its base text.3 This report provides an exhaustive investigation into the typographical, linguistic, structural, and computational methodologies required to parse and preserve these multi-authorial layers, culminating in a concrete architectural blueprint for an automated excerpting pipeline.
Phase 1: Publisher Conventions and Typographical Stratigraphy
The transition from the fluid, heavily annotated layouts of traditional Arabic manuscripts to the fixed constraints of modern movable type and digital printing necessitated the invention of new visual conventions to separate scholarly layers.5 In historical sharh mamzuj (mixed commentary) manuscripts, the Matn was almost invariably written in red ink, while the Sharh was written in black, providing an immediate visual distinction for the reader.6 As modern printing presses proliferated, color differentiation was often replaced by typographic variation. Contemporary publishing houses have standardized these visual hierarchies, though their conventions vary significantly based on their editorial philosophy, target audience, and regional printing history.
Commercial and Heritage Publishers
Dar al-Kutub al-'Ilmiyyah, based in Beirut, operates as one of the most prolific publishers of classical Arabic heritage, producing thousands of volumes with a focus on rapid dissemination.8 In their publications, the Matn is almost universally distinguished from the Sharh through the use of heavy bolding or a noticeably larger font size. Furthermore, Dar al-Kutub al-'Ilmiyyah frequently places the Matn within parentheses or ornate floral brackets, effectively creating a hard visual boundary that separates the original author's words from the subsequent commentary. When a Hashiyah is present, it is typically relegated to the lower half of the page, separated by a solid horizontal line, mimicking the layout of a modern footnote but functioning as a continuous, parallel text that requires concurrent reading.
Mu'assasat al-Risalah operates with a contrasting editorial philosophy, focusing heavily on rigorous critical editions (Tahqiq) with meticulous attention to modern academic typography.9 In their editions of multi-layered texts, such as voluminous Hadith commentaries, the visual hierarchy is exceptionally clear and spacious. The Matn is often isolated in its own continuous block at the top of the page, framed by generous whitespace, while the Sharh occupies the middle sector, and the editor's Tahqiq sits strictly at the bottom.9 When the Sharh heavily quotes the Matn inline, Mu'assasat al-Risalah utilizes distinct font families rather than mere weight changes, ensuring that the visual transition between centuries of authorship is immediately apparent to the reader's eye without relying solely on punctuation.
Dar al-Fikr, operating out of Damascus and Beirut, frequently publishes multi-layered legal and theological texts where the Hashiyah is considered as critical as the Matn.3 Their layout often employs a split-page or margin-heavy design, serving as a typographical homage to the traditional manuscript style where the Hashiyah literally frames the core text.4 Dar al-Fikr also makes extensive use of the classical abbreviation system within the main body, utilizing the isolated letter "ص" (Sad) to indicate the Matn (derived from the terms Aṣl or Muṣannif) and the letter "ش" (Shin) to denote the beginning of the Sharh.6 This abbreviation system, while historically authentic, presents significant challenges for computational optical character recognition (OCR), as isolated letters are frequently misinterpreted as noise or punctuation by standard extraction algorithms.
Dar al-Salam in Cairo employs highly modern, structured formatting, heavily relying on bracket systems, bullet points, and distinct margin indentations to separate layers.3 Their approach is highly systematic, making their texts somewhat easier to parse via automated layout analysis, as the geometric boundaries of the text blocks tightly correlate with authorial transitions. The indentation levels specifically mirror the dependency hierarchy of the text, physically pushing the sub-commentary inward to indicate its reliance on the primary commentary above it.
University and Institutional Presses
University presses enforce strict, standardized guidelines that minimize typographical ambiguity and prioritize pedagogical utility over aesthetic historical continuity. The Umm al-Qura University Press in Mecca mandates exact geometric and typographic specifications for all submitted scholarly editions and peer-reviewed journals.12 Their guidelines dictate an A4 page size with a 24-point font for the main body (Matn and Sharh) and an 18-point font for the margins or footnotes (Tahqiq and Hashiyah).12 They further enforce the use of the standard Naskh font for general academic prose, reserving the specialized Othmani script strictly for the quotation of Quranic verses.12 These rigid point-size rules provide highly reliable features for computational layout detection, as a parser can safely assume that an 18-point font block belongs to a subsidiary authorial layer.
Al-Azhar University Press leans heavily on functional pedagogical utility, maintaining layouts that actively assist in the memorization and recitation practices central to traditional Islamic education.14 Because the Matn is primarily designed to be committed to memory by students, while the Sharh is designed for discursive comprehension, Al-Azhar editions visually isolate the Matn to facilitate rote learning.3 The base text is completely separated from the discursive prose of the commentary, often printed with full vocalization (diacritics) to ensure perfect pronunciation, while the subsequent Sharh is left unvocalized, signaling to the reader that it is meant for analytical reading rather than oral preservation.
The Editor's Apparatus
Across all these publishing houses, distinguishing the historical Hashiyah (authored by a classical scholar) from the modern Tahqiq (authored by the contemporary editor) poses a significant challenge for human readers and algorithms alike. Publishers generally use numeric superscript indicators for the Tahqiq, directing the reader to footnotes containing variant manuscript readings (often denoted by symbols like "خ" or "نخ" for nuskha ukhra).7 Conversely, the historical Hashiyah is usually indicated by asterisks, specific regional sigla like "ط" for Turra (in the Maghribi tradition), or by the explicit inline quotation of the Sharh without the use of superscript numbers.10 The modern editor's footnotes are structurally bound to the bottom of the page, while the Hashiyah may float in the margins or occupy a dedicated mid-page block.
Publisher Profile
	Matn/Sharh Distinction
	Hashiyah Placement
	Tahqiq/Editor Marks
	Typographic Consistency
	Dar al-Kutub al-'Ilmiyyah
	Bold font, ornate brackets, inline mixing
	Bottom half of page, separated by solid line
	Numeric footnotes
	High, commercially standardized
	Mu'assasat al-Risalah
	Distinct font families, high spatial isolation
	Separate page blocks, distinct margins
	Extensive critical footnotes
	Very High, rigorous academic standard
	Dar al-Fikr
	Abbreviations (ص, ش), inline integration
	Framing margins, wrapping text
	Parenthetical numbers
	Medium, varies by historical print run
	Dar al-Salam
	Margin indentations, systematic brackets
	Bottom block, indented
	Standard numeric footnotes
	High, modern structure
	Umm al-Qura Press
	24pt Naskh body font, bold titles
	18pt margin font
	Numeric, strict formatting
	Absolute (Rule-based guidelines)
	Phase 2: Textual Markers and Linguistic Transitions
While typographical features provide essential visual cues, they are frequently lost during the digitization and OCR processes. Therefore, computational extraction must rely heavily on the internal linguistic markers that signal authorial transitions. The Arabic scholarly tradition developed a highly specialized, formulaic vocabulary to manage the interleaving of multiple voices without losing semantic coherence. However, because Arabic is a morphologically dense language that is routinely printed without diacritics (tashkeel), these markers frequently suffer from severe heterophonic ambiguity, requiring robust contextual disambiguation.15
Matn-to-Sharh Transitions
The most ubiquitous and fundamental marker indicating a transition from the foundational base text to the commentary is the term "قوله" (qawluhu, meaning "his statement"). This functions as an inline linguistic anchor.6 The commentator extracts a specific fragment of the Matn, prefixes or suffixes it with qawluhu, and immediately follows it with their expansive explanation. Other explicit, unambiguous markers include "قال المصنف" (qala al-musannif, "the author said") and "قال رحمه الله" (qala rahimahu Allah, "he said, may God have mercy upon him"). These honorifics and attribution formulas serve to firmly delineate the boundary between the original text and the subsequent analysis.
In heavily abbreviated manuscripts and their subsequent printed descendants, single-letter sigla are heavily utilized to save space and ink. The letter "ص" (Sad, standing for Aṣl or Sāhib al-Matn) introduces the base text, while "ش" (Shin, for Sharḥ) introduces the commentary.6 Another common, unambiguous marker is the explicit word "متن" (Matn) acting as a standalone header or inline tag before a block of foundational text.
Sharh-to-Hashiyah Transitions
The transition into the super-commentary layer introduces a layer of severe referential ambiguity. The author of the Hashiyah also uses the marker "قوله" (qawluhu) to anchor their text.6 However, in this nested context, qawluhu refers to the statement of the Sharih (the commentator), not the original Musannif (the base text author). Disambiguation relies entirely on nested context tracking; a computational parser must maintain a persistent state machine that knows it is currently operating within the Hashiyah layer to correctly attribute the target of the qawluhu anchor.
When the Hashiyah author introduces their own original reasoning, synthesizes competing views, or actively counters a previously stated argument, they routinely use the first-person marker "أقول" (aqulu, "I say").6 This explicitly shifts the authorial voice to the outermost historical layer, signaling that the following text is original analysis rather than quotation. Entire sections of super-commentary are also prefaced with the explicit title "حاشية" (Hashiyah), or in the specific North African manuscript tradition, "طرة" (Turra, abbreviated as the isolated letter "ط").7
Authorial Self-Reference and Evaluation
Within any given layer, the active author must continually differentiate their own voice from the voices of the historical scholars they are quoting or refuting. The marker "قلت" (qultu, "I said") universally signifies the voice of the current layer's author, serving to break a chain of transmission or quotation. When an author evaluates competing legal, grammatical, or theological opinions, they employ specific epistemic markers indicating their authoritative preference. Phrases such as "الراجح عندي" (al-rajih 'indi, "what I consider preponderant") or "يظهر لي" (yazharu li, "what appears to me") are utilized. These epistemic markers are crucial for determining the core intellectual contribution of the specific layer, distinguishing active legal reasoning from the passive transmission of prior opinions.
Editorial Apparatus (Tahqiq) Markers
The modern editor operates strictly outside the historical text, intervening solely to resolve manuscript discrepancies, authenticate chains of transmission, or provide biographical data. Their presence is signaled by highly specific, modern academic phrases such as "في الأصل" (fi al-asl, "in the original manuscript"), "في نسخة" (fi nuskha, "in a variant copy"), or the standard abbreviation "خ/نخ" (nuskha ukhra).7 When correcting typographical errors or scribal mistakes from previous prints, the editor will note "هكذا في المطبوع" (hakadha fi al-matbu', "thus in the printed edition"). Cross-referencing to other volumes or external texts is heavily utilized, triggered by the imperative "انظر" (unzur, "see"). The editor's voice is structurally bound to the footnotes, almost exclusively utilizing numeric anchors enclosed in parentheses or brackets to link their interventions to the main text above.
The Problem of Lexical Ambiguity
The primary obstacle in relying solely on these textual markers is profound linguistic ambiguity. In Arabic, a text presented without diacritical marks (tashkeel) becomes phonologically and morphologically opaque.15 A word like qawluhu can be visually identical to other morphological forms depending on the surrounding syntactic structure, leading to heterophonic homographs.15 Furthermore, classical Arabic academic writing frequently utilizes complex rhetorical devices, nested conditional clauses, and a pro-drop syntactic structure where the subject pronoun is entirely omitted.18 This makes it extraordinarily difficult to determine whether a verb belongs to the quoting author or the quoted historical subject.18 Therefore, simplistic regex-based matching of transition formulas is mathematically insufficient; it must be coupled with deep syntactic parsing and contextual state-tracking algorithms.
Phase 3: Genre-Specific Variation and Structural Topologies
Treating all multi-layered Arabic texts identically is a fundamental architectural error that inevitably leads to catastrophic parsing failures. The logic of how layers interleave, the ratio of text to commentary, and the depth of the nested hierarchy vary drastically across structural families and academic genres. A robust computational detection pipeline must be capable of dynamically loading parsing rules based on the specific genre of the text being processed.
Fiqh (Jurisprudence) and Usul al-Fiqh (Legal Theory)
In the domain of Fiqh, the text is highly structured, rigorous, and explicitly argumentative. A paradigmatic example of this structure is Hashiyat al-Bajuri 'ala Sharh Ibn Qasim, a three-tiered text built upon the foundational Matn of Abu Shuja.20 The Matn is categorized as a mukhtasar (compendium), designed for extreme brevity and rote memorization, often presenting raw legal rulings without detailing the underlying evidence.2 The intermediate Sharh by Ibn Qasim unpacks this incredibly dense prose, providing the necessary linguistic bridges, primary scriptural evidence, and pedagogical explanations.2
The Hashiyah by al-Bajuri introduces a third level of extreme granularity, engaging in deep grammatical investigations to determine how alternate syntactic parsings of the Sharh alter the ultimate legal ruling.20 In Fiqh, the qala/aqulu interleaving is aggressive, systemic, and highly reliable. The ratio of Matn to Sharh is typically vast (often 1:10 or 1:20), as a single, compressed sentence of the base text requires pages of discursive commentary to fully contextualize.
Usul al-Fiqh (legal theory) follows a similar multi-layered structure but features much longer, sustained argumentative chains and profound philosophical digressions.22 Here, explicit transitions are less frequent, but text blocks are significantly longer, requiring computational algorithms to maintain an authorial state over thousands of tokens without the benefit of a refreshing marker.
Hadith Commentary
The structural family of Hadith commentary, exemplified by Ibn Hajar al-'Asqalani's monumental Fath al-Bari, operates on an entirely different topographical logic.24 The Matn here is not a unified authorial prose block but a Prophetic Hadith, which is itself bifurcated into an Isnad (the chronological chain of narrators) and the Matn (the actual Prophetic text or action).26 Furthermore, the overarching architectural framework is dictated by the Bab (chapter heading) instituted by the original compiler of the collection (e.g., Imam al-Bukhari).24
A computational system processing Hadith commentary faces the unique challenge of not confusing the Isnad (a sequential list of names and transmission verbs) with the scholarly commentary itself. The layer detection algorithm must track the Bab heading as the macro-structure, isolate the Isnad, protect the Prophetic Matn, and then parse the subsequent Sharh. This Sharh often critiques both the linguistic nature of the Hadith and the editorial choices of the original compiler.24 The Matn to Sharh ratio here is highly variable, but the boundaries are strictly demarcated by standardized transmission terminology (e.g., haddathana, "he narrated to us").
Nahw (Grammar) and Qira'at (Quranic Recitation)
Grammatical commentaries, such as Sharh Ibn 'Aqil on the famous Alfiyyah of Ibn Malik, are visually and structurally distinct because the Matn is composed entirely in verse (nazm).28 The base text utilizes strict Arabic poetic meter, which can be computationally detected using prosodic algorithms.30 The prose Sharh systematically explains the grammatical rules encoded within the poem, heavily relying on shawahid (poetic evidence from pre-Islamic Arabs) to prove linguistic points.28 A computational pipeline can exploit this inherent structure by running a metrical detection algorithm to instantly and flawlessly isolate the Matn verses from the prose Sharh.32
Similarly, the Qira'at family, such as the extensive commentaries on the Shatibiyyah, is anchored by a massive instructional poem (spanning 1,173 lines).23 The atomic unit of parsing in this genre must be the bayt (verse). The commentary systematically dissects each line to extract the highly technical rules of Quranic recitation, meaning the transition markers are almost exclusively tied to the sequential progression of the poem's verses rather than rhetorical prose shifts.
Tafsir (Quranic Exegesis)
Tafsir texts, such as Tafsir al-Jalalayn equipped with the Hashiyat al-Sawi, are anchored to the ultimate, immutable fixed external structure: the Quranic Ayah (verse).34 The Ayah serves as a universal anchor point that cannot be altered by the author. Layer detection in Tafsir can achieve extraordinarily high accuracy by utilizing string-matching algorithms to compare extracted text segments against a verified digitized Quranic corpus. Once the exact Ayah is identified as the Matn, the subsequent explanatory prose is categorized as the Sharh, and any further nested, philosophical, or grammatical commentary as the Hashiyah. The rigid, sequential progression from Surah to Surah and Ayah to Ayah provides a highly predictable and mathematically verifiable parsing framework.
Mantiq (Logic) and Kalam (Theology)
To complete the structural families, texts dealing with Mantiq (logic) and Kalam (theology) exhibit a highly dialectical structure similar to Usul al-Fiqh. These texts, often utilizing works like the Sharh al-Aqa'id al-Nasafiyyah with super-commentaries by al-Taftazani or al-Jurjani, rely on complex syllogistic reasoning.36 The transition markers here are less about quoting physical text and more about presenting and destroying hypothetical arguments. Markers such as "فإن قيل" (fa-in qila, "if it is said") followed by "قلنا" (qulna, "we say") dominate the Sharh layer. The computational challenge lies in tracking the boundaries of these hypothetical propositions, ensuring that a counter-argument is not mistakenly attributed to the base author.
Phase 4: Computational Approaches to Stratigraphy
To accurately detect, segment, and extract these complex historical layers, a robust, hybrid computational approach is required. This approach must draw upon recent advances in digital humanities, specifically leveraging the groundwork laid by the Open Islamicate Texts Initiative (OpenITI) and comparative algorithmic analyses of other ancient religious corpora.
Rule-Based Parsing and mARkdown Tagging
The most immediate and transparent approach to text segmentation utilizes rule-based parsing via Context-Free Grammars (CFG) and finite state machines. The OpenITI project has pioneered mARkdown, a lightweight markup language specifically designed to encode the structural, morphological, and semantic realities of right-to-left Islamicate texts without the extreme overhead of XML.38 OpenITI utilizes complex regex patterns to identify logical unit headers (### | for chapters, ### || for sections, ### $ for biographies or dictionary entries), paragraphs (#), and the modern editorial apparatus (### |EDITOR|).38
For manuscript transcriptions and multi-layer editions, OpenITI mARkdown employs distinct tags like #~# for the edited text and #*# for comments and annotations, allowing the text to be split into manageable computational arrays.39 Furthermore, the KITAB project utilizes the highly sophisticated passim algorithm to automatically detect text reuse across vast corpora.40 By stripping non-Arabic characters, chunking texts into 300-word milestones, and aligning matching sequences, passim indirectly highlights where a later author has subsumed an earlier Matn into their own Sharh, providing a computational map of intellectual lineage.40 While highly accurate when texts are pre-encoded or perfectly clean, rule-based regex systems fail dramatically on raw, unannotated OCR text due to missing punctuation, typographical noise, and homographic overlap.
Machine Learning and Sequence Labeling
To overcome the fragility of rule-based regex systems, modern Arabic NLP relies on advanced sequence labeling architectures. Specifically, models utilizing Bidirectional Long Short-Term Memory networks coupled with a Conditional Random Field layer (Bi-LSTM-CRF) have shown immense promise. The CRF layer is mathematically designed to compute the joint probability of an entire sequence of labels rather than isolated tokens, making it ideal for tracking authorial state transitions over long, complex sentences.43 If the model detects the token "قوله", the CRF ensures that the subsequent sequence of tokens is highly likely to be classified as the Matn layer, transitioning back to Sharh only when a terminating syntactic structure is probabilistically detected.
The advent of Transformer models, particularly AraBERT and MARBERT, has further revolutionized Arabic text segmentation and named entity recognition.44 By analyzing deep contextual embeddings, Transformer models can distinguish between the classical Arabic of a 7th-century Matn and the slightly more evolved classical Arabic of a 14th-century Hashiyah or a 19th-century Tahqiq. Because human language drifts morphologically, syntactically, and lexically over centuries, deep learning models can perform authorship attribution and segmentation based purely on the latent stylistic and frequency-based features of the unannotated text.46 Furthermore, advancements in Matryoshka nested embedding learning have drastically improved semantic similarity matching in Arabic, allowing models to recognize parallel textual structures even when authors employ slight dialectal or dictionary-based transcoding alterations.49
Cross-Domain Algorithmic Parallels
The profound algorithmic challenges of Arabic commentary stratigraphy are heavily mirrored in other ancient religious traditions, providing valuable, field-tested computational blueprints.
In the computational analysis of the Talmud, researchers successfully employed machine learning algorithms to analyze the complex Aramaic dialect. They proved that the algorithm could automatically detect the boundary between the Babylonian text layers and the Jerusalem text layers based solely on subtle linguistic drift, effectively confirming the intuitions of medieval commentators like Rashi.50 This confirms the viability of using stylometric machine learning to differentiate an older Matn from a newer Sharh within the same physical page.
In Sanskrit computational linguistics, ancient texts suffer from continuous string formatting without standard word boundaries due to sandhi (complex euphonic conjunctions where adjacent words merge).51 To solve this, researchers rely on GraphCRF models and highly optimized finite-state transducers to mathematically determine word and sentence boundaries before extracting the commentary layers.53 Furthermore, algorithms specifically designed to detect the structural constraints of Sanskrit poetic meter closely parallel the algorithms required to isolate Arabic nazm (verse) Matns from their surrounding prose commentaries.32
Similarly, the computational analysis of Biblical texts has successfully utilized neural embeddings and advanced statistical functions to detect chiasmus (symmetrical poetic structures) and isolate time-related textual insertions. This cross-domain success proves that deep learning architectures can capture complex structural heuristics in ancient texts with high precision, overcoming the limitations of manual human parsing.56
Phase 5: Excerpting System Design and Pipeline Architecture
Given the immense complexities of historical layout, linguistic ambiguity, genre-specific topography, and computational modeling, designing an automated excerpting system requires a robust, multi-stage pipeline architecture. The system must process raw, noisy text, assign a probabilistic layer tag to every individual token, bind indivisible text units together, and generate highly structured, machine-readable metadata.
The Indivisible Unit Principle
According to the project's foundational specifications, a Sharh passage that explicitly quotes a Matn forms an "indivisible unit." When the automated system is queried by a user to excerpt a specific section of the commentary, it must include the associated Matn quote, properly tagged and preserved. Extracting the Sharh in complete isolation strips the commentary of its target object, rendering it semantically hollow and academically useless.
This logic becomes recursive when dealing with a Hashiyah. If a user queries a passage from the super-commentary that references the commentary, which in turn references the foundational base text, the excerpting system must traverse the dependency graph and extract all three layers into a unified, tagged stack. The final output must present the Matn, the Sharh, and the Hashiyah distinctly but adjacently, maintaining their historical and intellectual context.
Pipeline Resolution and Confidence Thresholds
The pipeline must operate on a core engineering principle of "fail-soft" degradation. When the system encounters a transition marker that is highly ambiguous, or when the stylistic machine learning model returns a low-confidence score (  ), the system must not fail loudly and break the entire pipeline. Instead, it should attempt a "best guess" classification based on the last known authorial state, while explicitly flagging the extracted segment in the metadata with a exact confidence_score and a status: uncertain tag. This mechanism allows human reviewers or downstream analytical applications to handle the ambiguous excerpt appropriately, preventing silent data corruption.
Configuration Profiles
A single monolithic set of parsing rules cannot possibly succeed across the vast diversity of Islamic texts. The system requires the implementation of Publisher-Specific Profiles and Genre-Specific Profiles. Before parsing begins, the system loads a specific configuration file. If the text is published by Mu'assasat al-Risalah, the pipeline heavily weighs font-family changes and explicit line breaks. If the genre is flagged as Nahw or Qira'at, the system automatically activates the poetic meter detection module to mathematically isolate the Matn verses from the prose.
Metadata Schema
To ensure the extracted excerpt is computationally viable for future macro-analysis or distant reading, the structured output (whether JSON or XML) must append rigorous metadata to every extracted segment. The required schema must include:
* segment_id: A unique alphanumeric identifier.
* text_content: The raw Arabic string.
* layer_type: ENUM.
* author_name: The resolved, normalized name of the layer's historical author.
* author_century: The Hijri century of the author (essential for stylistic and linguistic drift models).
* dependency_id: A graph pointer to the parent text if the current layer is a commentary.
* confidence_score: A calculated float (0.0 to 1.0) indicating parsing certainty.
________________
Deliverable 1: Arabic Textual Marker Catalog
The following catalog provides the core detection vocabulary for the computational system, organized by transition type and rated for algorithmic ambiguity. It incorporates standard formulas, classical sigla, and editorial apparatus markers.
Marker (Arabic)
	Transliteration
	Transition Type
	Ambiguity Rating
	Disambiguating Context / Computational Notes
	قوله
	qawluhu
	Matn to Sharh / Sharh to Hashiyah
	High
	Requires continuous state-tracking. Refers to the layer immediately preceding the current active author. Highly susceptible to morphological overlap without diacritics.
	قال المصنف
	qala al-musannif
	Sharh quoting Matn
	Low
	Unambiguously references the original base text author. Excellent anchor point.
	قال رحمه الله
	qala rahimahu Allah
	Sharh quoting Matn
	Medium
	"May God have mercy on him" usually refers to a deceased Matn author, but occasionally refers to a past Sharih in deeply nested texts.
	ص
	Sad
	Matn begins
	Medium
	Stands for Aṣl. Highly reliable in Dar al-Fikr prints; highly prone to OCR confusion with regular letters or punctuation in poor scans.
	ش
	Shin
	Sharh begins
	Medium
	Stands for Sharh. Reliable in historical prints, prone to OCR noise.
	متن
	Matn
	Matn begins
	Low
	Explicit structural header. Easily parsed.
	حاشية
	Hashiyah
	Hashiyah begins
	Low
	Explicit structural header indicating the transition to the super-commentary layer.
	أقول
	aqulu
	Sharh/Hashiyah original thought
	Low
	"I say." Shifts voice to the current layer's active author, explicitly breaking the quoting chain.
	قلت
	qultu
	Author self-reference
	Low
	"I said." Identifies the active voice of the layer currently being parsed. Common in Hadith critique.
	الراجح عندي
	al-rajih 'indi
	Authorial evaluation
	Low
	"Preponderant to me." Signals the climax of a legal or theological argument in the active layer.
	يظهر لي
	yazharu li
	Authorial evaluation
	Low
	"What appears to me." Signals personal scholarly deduction (ijtihad).
	في الأصل
	fi al-asl
	Editorial (Tahqiq) note
	Low
	"In the original." Exclusively the voice of the modern editor discussing physical manuscript conditions.
	نسخة / خ / نخ
	nuskha / kha / nukh
	Editorial variant
	Low
	Indicates a variant manuscript reading. Usually found in footnotes, margins, or brackets.
	انظر
	unzur
	Editorial cross-reference
	High
	"See." Can be used by classical authors for internal reference or modern editors for external reference. Requires positional context (margin vs. body).
	هكذا في المطبوع
	hakadha fi al-matbu'
	Editorial note
	Low
	"Thus in the printed edition." Explicit modern editorial intervention correcting past errors.
	ط
	Turra
	Hashiyah/Gloss
	Medium
	Maghribi tradition-specific marker for a marginal gloss. Susceptible to OCR noise.
	________________
Deliverable 2: Recommended Detection Architecture
The proposed architecture utilizes a Hybrid State-Tracking & Machine Learning Pipeline. It first applies Publisher/Genre configuration rules to establish structural boundaries, then utilizes an AraBERT-CRF sequence labeler to resolve morphological ambiguities and stylistic drift, and finally applies the "Indivisible Unit" logic via a relational Dependency Graph.
Core Layer-Classification Algorithm (Pseudocode)


Python




class TextSegment:
   def __init__(self, text, start_idx, end_idx):
       self.text = text
       self.tokens = tokenize(text)
       self.layer = "UNKNOWN"
       self.dependencies =
       self.confidence = 0.0

class StratigraphyPipeline:
   def __init__(self, genre_profile, publisher_profile):
       self.genre = genre_profile
       self.publisher = publisher_profile
       # Load Transformer model with CRF layer for sequential state-tracking
       self.ml_model = load_arabert_crf_model()
       self.marker_dict = load_marker_catalog()
       self.current_state = "MATN" # Default starting state

   def parse_document(self, document_text):
       # Step 1: Pre-processing & OCR Noise Reduction based on publisher typography
       clean_text = apply_publisher_regex(document_text, self.publisher)
       
       # Step 2: Genre-Specific Structural Isolation
       if self.genre == "NAHW" or self.genre == "QIRAAT":
           # Extract poetic verses first using prosodic algorithms
           matn_blocks, prose_blocks = extract_nazm_meter(clean_text)
           return self.process_poetic_genre(matn_blocks, prose_blocks)
           
       elif self.genre == "TAFSIR":
           # Anchor text globally using verified Quranic corpus matching
           return self.process_quranic_anchors(clean_text)

       # Step 3: Sequential Processing for Fiqh/Usul/Hadith/Mantiq
       segments = split_into_sentences(clean_text)
       parsed_stack =

       for seg in segments:
           segment_obj = TextSegment(seg.text, seg.start, seg.end)
           
           # Sub-step 3a: Check for explicit, unambiguous transition markers
           transition = self.detect_transition_marker(segment_obj.tokens)
           
           if transition and not transition.is_ambiguous:
               self.update_state_machine(transition)
               segment_obj.layer = self.current_state
               segment_obj.confidence = 0.98
           else:
               # Sub-step 3b: Fallback to ML contextual embeddings for ambiguous text
               predicted_layer, conf = self.ml_model.predict_sequence(
                   segment_obj.tokens, 
                   previous_state=self.current_state
               )
               segment_obj.layer = predicted_layer
               segment_obj.confidence = conf
               self.current_state = predicted_layer # Persist state

           # Sub-step 3c: Build Indivisible Unit Dependency Graph
           if segment_obj.layer == "SHARH" and self.contains_qawluhu(segment_obj.tokens):
               parent_matn = find_last_layer(parsed_stack, "MATN")
               if parent_matn:
                   segment_obj.dependencies.append(parent_matn.id)
               
           elif segment_obj.layer == "HASHIYAH" and self.contains_qawluhu(segment_obj.tokens):
               parent_sharh = find_last_layer(parsed_stack, "SHARH")
               if parent_sharh:
                   segment_obj.dependencies.append(parent_sharh.id)
                   # Inherit Matn dependency to maintain the indivisible triad
                   segment_obj.dependencies.extend(parent_sharh.dependencies)

           parsed_stack.append(segment_obj)

       return self.package_metadata(parsed_stack)

   def extract_excerpt(self, parsed_stack, target_idx):
       # Ensures strict compliance with SPEC_section_1_1b.md (Indivisible Units)
       target_segment = parsed_stack[target_idx]
       excerpt_bundle = [target_segment]
       
       # Recursively fetch all required parent dependencies to preserve context
       for dep_id in target_segment.dependencies:
           parent_seg = get_segment_by_id(parsed_stack, dep_id)
           # Insert at beginning to maintain correct chronological reading order
           excerpt_bundle.insert(0, parent_seg) 
           
       return format_as_json_with_metadata(excerpt_bundle)

Geciteerd werk
1. Matn, Sharh, Hashiya, Taliqa, and Takmila in Islamic Intellectual History - Mâverd, geopend op april 7, 2026, http://maverd.blogspot.com/2015/02/matn-sharh-hashiya-taliqa-and-takmila.html
2. The Discursive Tradition of Commentaries (shurūḥ) – Lessons from Matn Abī Shujāʿ - Islamic Law Blog, geopend op april 7, 2026, https://islamiclaw.blog/2022/09/08/the-discursive-tradition-of-commentaries-shuruh%CC%A3-lessons-from-matn-abi-shuja%CA%BF/
3. The Calligraphic State - UC Press E-Books Collection, geopend op april 7, 2026, https://publishing.cdlib.org/ucpressebooks/view?docId=ft7x0nb56r;chunk.id=0;doc.view=print
4. Layout | Islamic Manuscript Basics - GitHub Pages, geopend op april 7, 2026, https://kislakcenter.github.io/islamicmss/layout/
5. (PDF) Overlooked: The Role of Craft in the Adoption of Typography in the Muslim Middle East - ResearchGate, geopend op april 7, 2026, https://www.researchgate.net/publication/362921510_Overlooked_The_Role_of_Craft_in_the_Adoption_of_Typography_in_the_Muslim_Middle_East
6. Arabic Manuscripts : A Vademecum for Readers / by Adam Gacek, geopend op april 7, 2026, https://mouse.digitalscholarship.nl/images/uploads/Gacek-Vademecum.pdf
7. Full text of "Arabic Manuscripts A Vademecum For Readers Handbook Of Orient", geopend op april 7, 2026, https://archive.org/stream/ArabicManuscriptsAVademecumForReadersHandbookOfOrient/Arabic-Manuscripts-a-Vademecum-for-Readers-Handbook-of-Orient_djvu.txt
8. Dar Al-Kotob Al-Ilmiyah - Wikipedia, geopend op april 7, 2026, https://en.wikipedia.org/wiki/Dar_Al-Kotob_Al-Ilmiyah
9. Some Recent (Arabic) Publications of Exceptional Quality: Review by Mawlana Abu Asim Badrul Islam - Ṭaḥāwī, geopend op april 7, 2026, https://attahawi.com/2014/11/15/some-recent-arabic-publications-of-exceptional-quality-review-by-mawlana-abu-asim-badrul-islam/
10. Abbreviations - Brill Reference Works, geopend op april 7, 2026, https://referenceworks.brill.com/display/entries/EALO/EALL-SIM-0002.xml
11. File:Cairo - Dar Al-Salam District Map.jpg - Wikimedia Commons, geopend op april 7, 2026, https://commons.wikimedia.org/wiki/File:Cairo_-_Dar_Al-Salam_District_Map.jpg
12. Standards of Thesis Printing and Layout - Deanship of Postgraduate Studies And Research - Vice-President for Graduate Studies and Scientific Research | Umm Al-Qura University, geopend op april 7, 2026, https://uqu.edu.sa/en/gs/43052
13. Author Guideline - Journal of Umm Al-Qura University for Language Sciences and Literature, geopend op april 7, 2026, https://uqu.edu.sa/en/jll/141100
14. Architecture of Al-Azhar - Muslim HeritageMuslim Heritage, geopend op april 7, 2026, https://muslimheritage.com/architecture-al-azhar/
15. Diacritics and the Resolution of Ambiguity in Reading Arabic M. Maroun A thesis submitted for the degree of PhD - Essex Research Repository, geopend op april 7, 2026, https://repository.essex.ac.uk/22078/1/Full%20thesis-Maryse%20Maroun.pdf
16. Evaluation of the ambiguity caused by the absence of diacritical marks in Arabic texts: Statistical study - ResearchGate, geopend op april 7, 2026, https://www.researchgate.net/publication/298972677_Evaluation_of_the_ambiguity_caused_by_the_absence_of_diacritical_marks_in_Arabic_texts_Statistical_study
17. Sociocultural Causes of Ambiguity in Arab Academic Writings - MDPI, geopend op april 7, 2026, https://www.mdpi.com/2304-6775/11/2/25
18. Handling Arabic Morphological and Syntactic Ambiguity within the LFG Framework with a View to Machine Translation - Mohammed Attia, geopend op april 7, 2026, https://www.mohammed-attia.com/Publications/Attia-PhD-Thesis.pdf
19. (PDF) Handling Arabic Morphological and Syntactic Ambiguity within the LFG Framework with a View to Machine Translation - ResearchGate, geopend op april 7, 2026, https://www.researchgate.net/publication/233967761_Handling_Arabic_Morphological_and_Syntactic_Ambiguity_within_the_LFG_Framework_with_a_View_to_Machine_Translation
20. The Sentences that Have no Parsing in Al-Bajuri's Footnote to the ..., geopend op april 7, 2026, https://jtuh.org/index.php/jtuh/article/view/3180
21. Hashiyat al-Bajuri 'ala Sharh Ibn Qasim al-Ghazzi li Matn Abi Shuja' • Author - ICN, geopend op april 7, 2026, https://icn.com/en-jo/product/hashiyat-al-bajuri-ala-sharh-ibn-qasim-al-ghazzi-li-matn-abi-shuja--author-ibrahim-al-bajuri--2020-1ETTKR
22. Full text of "Mustasfa min ilm al-usul, vol. I, by Ghazali" - Internet Archive, geopend op april 7, 2026, https://archive.org/stream/GAZALIMustasfaMinIlmUsulI/GAZALI__mustasfa_min_ilm_usul_I_djvu.txt
23. Transliteration of Arabic and Fársí words/names - Bahá'í Library Online, geopend op april 7, 2026, https://bahai-library.com/pdf/g/glossary_arabic_persian_transcription.pdf
24. FATH AL-BĀRĪ - by IBN HAJAR AL-ASQALANI, geopend op april 7, 2026, https://archive.org/download/137622672SelectionsFromTheFathAlBariCommentaryOnSahihAlBukhariByIbnHajarAlAsqala_201703/137622672-Selections-From-the-Fath-Al-Bari-Commentary-on-Sahih-Al-Bukhari-by-Ibn-Hajar-Al-Asqalani-Translated-by-Abdal-Hakim-Murad.pdf
25. TAFSIR SAHIH BUKHARI: FATH AL BARI | Sunnah Muakada, geopend op april 7, 2026, https://sunnahmuakada.files.wordpress.com/2014/10/fath-al-bari.pdf
26. The Impact of Different Schools of Thought on the Principles of Hadith: Criteria for Acceptance and Rejection of Narrations | `, geopend op april 7, 2026, https://assajournal.com/index.php/36/article/view/442
27. A Systematic Review on Hadith Authentication and Classification Methods - ResearchGate, geopend op april 7, 2026, https://www.researchgate.net/publication/351252055_A_Systematic_Review_on_Hadith_Authentication_and_Classification_Methods
28. Alfiyyat Ibn Malik for Arabic Nahw & Sarf - Studio Arabiya, geopend op april 7, 2026, https://studioarabiya.com/alfiyyat-ibn-malik-for-arabic-nahw-sarf/
29. Ibn 'Aqil's Commentary on Alfiyya | PDF | Grammatical Gender | Syntax - Scribd, geopend op april 7, 2026, https://www.scribd.com/document/461254303/Alfiyya-commentaries-pdf
30. Determining the meter of classical Arabic poetry using deep learning: a performance analysis - Frontiers, geopend op april 7, 2026, https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2025.1523336/full
31. (PDF) Determining the meter of classical Arabic poetry using deep learning: a performance analysis - ResearchGate, geopend op april 7, 2026, https://www.researchgate.net/publication/389520299_Determining_the_meter_of_classical_Arabic_poetry_using_deep_learning_a_performance_analysis
32. The Geometry of Arabic Poetry Rhythm (An Energy-Based Artificial Intelligence Approach to Sub-Meter Detection), geopend op april 7, 2026, https://www.ijrsp.com/pdf/issue-77/4.pdf
33. Dar Ihya al-Turath al-Arabi, Beirut - Albalagh Bookstore - Buy Islamic Books and more!, geopend op april 7, 2026, https://www.albalaghbooks.com/dar-ihya-al-turath-al-arabi-beirut/?items_per_page=128&sort_by=timestamp&sort_order=asc&layout=products_without_options
34. Hashiyat al-Sawi 'ala Tafsir al-Jalalayn • Author - ICN, geopend op april 7, 2026, https://icn.com/en-jo/product/hashiyat-al-sawi-ala-tafsir-al-jalalayn--author-al-sawi--2011-1fbefb
35. Hashiyat as-Saawy 'ala Tafsir Al-Jalaalayn, by Sheikh Ahmed as-Sawi - SifatuSafwa, geopend op april 7, 2026, https://www.sifatusafwa.com/en/entire-tafsir/hashiyat-as-saawy-ala-tafsir-al-jalaalayn-by-sheikh-ahmed-as-sawi.html
36. All New Selections - JarirBooks-Arabic Books & More, geopend op april 7, 2026, https://jarirbooksusa.com/m1000-new-selections-image-list.html
37. Dar Ihya al-Turath al-Arabi, Beirut - Albalagh Bookstore - Buy Islamic Books and more!, geopend op april 7, 2026, https://www.albalaghbooks.com/dar-ihya-al-turath-al-arabi-beirut/?sort_by=product&sort_order=asc&layout=products_without_options
38. OpenITI mARkdown - al-Raqmiyyāt, geopend op april 7, 2026, https://maximromanov.github.io/mARkdown/
39. OpenITI mARkdownMSS: Basics of the Format, geopend op april 7, 2026, https://openiti.org/mARkdownMSS/mARkdownMSS.pdf
40. Diversifying the OpenITI corpus, One Text at a Time - KITAB, geopend op april 7, 2026, https://kitab-project.org/Diversifying-the-OpenITI-corpus,-One-Text-at-a-Time/
41. KITAB Text Reuse Data - Zenodo, geopend op april 7, 2026, https://zenodo.org/records/11501559
42. Read, Hot, and Digitized: KITAB Project Brings Distant Reading to Middle Eastern Studies, geopend op april 7, 2026, https://texlibris.lib.utexas.edu/2018/10/kitab-project-brings-distant-reading-to-middle-eastern-studies/
43. Unsupervised Arabic dialect segmentation for machine translation | Natural Language Engineering | Cambridge Core, geopend op april 7, 2026, https://www.cambridge.org/core/journals/natural-language-engineering/article/unsupervised-arabic-dialect-segmentation-for-machine-translation/6889FF81C163434613A7240E5CD76AFC
44. Arabic Named Entity Recognition Using Transformer-based-CRF Model - ACL Anthology, geopend op april 7, 2026, https://aclanthology.org/2021.icnlsp-1.31.pdf
45. AraBERT: Transformer-based Model for Arabic Language Understanding - LREC, geopend op april 7, 2026, http://www.lrec-conf.org/proceedings/lrec2020/workshops/OSACT2020/pdf/2020.osact-1.2.pdf
46. A machine learning approach for Arabic text classification using N-gram frequency statistics, geopend op april 7, 2026, https://www.researchgate.net/publication/222628499_A_machine_learning_approach_for_Arabic_text_classification_using_N-gram_frequency_statistics
47. Authorship Verification for Arabic Social Media Texts Using Arabic Knowledge-Base Model (AraKB) - ACL Anthology, geopend op april 7, 2026, https://aclanthology.org/2022.wanlp-1.19.pdf
48. BERT-based Classical Arabic Poetry Authorship Attribution - ACL Anthology, geopend op april 7, 2026, https://aclanthology.org/2025.coling-main.409.pdf
49. Enhancing Semantic Similarity Understanding in Arabic NLP with Nested Embedding Learning | Request PDF - ResearchGate, geopend op april 7, 2026, https://www.researchgate.net/publication/394793128_Enhancing_Semantic_Similarity_Understanding_in_Arabic_NLP_with_Nested_Embedding_Learning
50. Rashi was right: Machine learning confirms unique status of some Talmudic tracts, geopend op april 7, 2026, https://www.timesofisrael.com/rashi-was-right-machine-learning-confirms-unique-status-of-some-talmudic-tracts/
51. Discourse Analysis of Sanskrit texts - ACL Anthology, geopend op april 7, 2026, https://aclanthology.org/W12-4701.pdf
52. Sanskrit Segmentation revisited - ACL Anthology, geopend op april 7, 2026, https://aclanthology.org/2019.icon-1.12.pdf
53. Towards Computational Processing of Sanskrit - Gallium - Inria, geopend op april 7, 2026, http://gallium.inria.fr/~huet/PUBLIC/icon.pdf
54. Building a Word Segmenter for Sanskrit Overnight - ACL Anthology, geopend op april 7, 2026, https://aclanthology.org/L18-1264.pdf
55. Proceedings of the Computational Sanskrit & Digital Humanities - ACL Anthology, geopend op april 7, 2026, https://aclanthology.org/2023.wsc-csdh.0.pdf
56. Extraction of time-related expressions using text mining with application to Hebrew - PMC, geopend op april 7, 2026, https://pmc.ncbi.nlm.nih.gov/articles/PMC10889890/
57. Computational Discovery of Chiasmus in Ancient Religious Text - ACL Anthology, geopend op april 7, 2026, https://aclanthology.org/2025.naacl-short.13.pdf
58. Computational Linguistic Analysis of the Biblical Text - Vrije Universiteit Amsterdam, geopend op april 7, 2026, https://research.vu.nl/en/publications/computational-linguistic-analysis-of-the-biblical-text/