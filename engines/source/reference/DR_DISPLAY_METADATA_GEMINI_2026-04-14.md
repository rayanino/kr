# **The Architecture of Context: Designing the Source Card for an Islamic Scholarly Digital Library**

## **Introduction: The Paradigm of Zero Knowledge Loss**

The digitization of cultural heritage, particularly within the vast and complex domain of Islamic scholarly literature, frequently suffers from a reductionist approach to metadata and contextualization.1 In a well-intentioned but flawed effort to cater to the modern reader’s diminishing attention span, many digital libraries and educational applications strip away the intricate epistemological framing, the historical context, and the nuanced bibliographical disputes that classically accompanied Islamic texts.2 The architectural vision for a personal Islamic scholarly library, conceptualized as a repository that processes Arabic scholarly books into self-contained excerpts or teaching units, must fundamentally reject this reductionism. It must operate on the core principle of "Zero Knowledge Loss," dictating that no layer of scholarly discourse, biographical nuance, structural hierarchy, or historical dispute is ever hidden, permanently compressed, or simplified to the point of inaccuracy.

When a continuous textual corpus is atomized into teaching units designed for focused study, the excerpt is violently severed from its physical and structural binding. To prevent the profound loss of context that naturally accompanies such atomization, an expertly designed digital component—the "Source Card" (بطاقة المصدر)—must persistently accompany each unit. This card functions as a dynamic, computational equivalent of the traditional scholar's introduction, providing the student with immediate, structured access to the author's identity, the text's pedagogical purpose, the work's location within the multi-layered Islamic sciences, and the precise provenance of the digital text itself.

The extensive analysis presented in this report outlines the optimal architectural framework, metadata schema, and user interface design for this Source Card. It systematically addresses the ontological requirements of the classical Islamic scholarly tradition, the epistemological demands of trust and provenance, and the user experience principles necessary to serve a beginner student without compromising the exhaustive depth required by the absolute mandate of Zero Knowledge Loss.

## **Aligning with the Islamic Scholarly Tradition**

To design an authentic and culturally resonant digital interface for Islamic texts, the architecture must first examine how texts were historically transmitted, introduced, and validated within the tradition itself. In the classical circles of knowledge, known as the *Halaqat al-'Ilm*, a scholar never simply began reading a text to their students in a vacuum. The transmission of knowledge was heavily formalized through introductory discourses known as *Muqaddimat*, which served as both an epistemological anchor and a pedagogical map for the text about to be studied.3

### **The Epistemological Function of the Muqaddimah**

The classical prefaces and introductory lectures in the Arab-Islamic heritage were not mere formalities; they possessed distinct communicative, methodological, and psychological functions.3 Literary critics and philosophers established that a proper introduction must address "The Eight Heads" (*Al-Ru'us al-Thamaniya*). These eight essential components include the purpose of the book (*Gharad*), the anticipated benefit to the student (*Manfa'ah*), the title (*Simah*), the identity and authority of the author (*Mu'allif*), the type and nature of the science (*Naw' al-'Ilm*), the rank of the science among other disciplines (*Martabah*), the structural division of the text (*Qismah*), and the specific pedagogical methods employed by the author (*Anha' Ta'limiyya*).3

Digital libraries routinely fail to capture this holistic framing, usually relegating metadata to a sterile catalog page that the user abandons the moment they open the text. The digital Source Card must act as the persistent realization of these eight heads, accompanying the reader alongside every specific excerpt. By doing so, the interface performs the function of the classical instructor, constantly orienting the student regarding the exact nature and utility of the fragment they are reading.3

### **The Ten Principles of Foundational Sciences**

In later centuries, the tradition of the scholarly introduction was further codified into "The Ten Principles" (*Al-Mabadi' al-'Asharah*). As famously encapsulated in the didactic poetry of scholars like Muhammad bin Ali Al-Sabban (d. 1206 AH), a student was required to master ten conceptual elements before initiating the study of any discipline: the definition of the field (*Hadd*), its subject matter (*Mawdu'*), its fruit or benefit (*Thamrah*), its merit (*Fadl*), its relationship to other sciences (*Nisbah*), its founder (*Wadi'*), its name (*Ism*), its foundational sources (*Istimdad*), the Islamic legal ruling on studying it (*Hukm al-Shari'*), and its core issues (*Masa'il*).5

A properly designed digital Source Card structurally mirrors these principles. When a user opens a teaching unit on jurisprudence or syntax, the card must visually and textually answer the foundational questions dictated by the Ten Principles. It must define the science, explain the benefit of reading the specific excerpt, and locate the text's authority within the broader constellation of Islamic knowledge.5

### **The Chain of Transmission and Councils of Audition**

Another critical element historically embedded in the Islamic tradition, yet almost entirely lost in modern digital libraries, is the *Sanad al-Talaqqi* (chain of reception) and the *Ijazat al-Sima'* (certificates of audition). Historically, the authority of a text was not established merely by its physical existence, but by a documented chain of who read it, to whom it was read, and the precise dates and locations of the reading.6 A text like *Sahih al-Bukhari* was validated through massive public readings where scholars documented the attendance and authorization of the transmission.8

While a digital library interface cannot replicate a living, continuous *Ijazah* between a human teacher and student, the Source Card can and must mirror this tradition by clearly displaying the "chain of verification." This involves transparently indicating which physical manuscript or verified printed edition the digital text is based upon, identifying the scholar who verified the manuscript (*Muhaqqiq*), and tracing the pedigree of the metadata itself to authoritative bibliographic encyclopedias.8

## **Architecting the Author Information Display**

The first major component of the Source Card is the author's profile. The Islamic biographical tradition, encapsulated in the vast literature of *'Ilm al-Tabaqat* (books of generations) and *Kutub al-Tarajim* (biographical dictionaries), is arguably one of the most exhaustive historical endeavors in human history.11 Scholars measured individuals by their lineage, their teachers, their geographical mobility for knowledge (*Rihlah*), and their exactitude (*Dabt*).13 The user interface of the Source Card must balance the overwhelming nature of this historical data with the cognitive limits of a beginner student.

### **Nomenclature and the Complexity of the Scholar's Name**

In classical Arabic nomenclature, a single scholar possesses a complex string of identifiers designed to ensure absolute precision and prevent the conflation of narrators. This string includes the *Ism* (the given name), the *Nasab* (the patronymic lineage stretching back multiple generations), the *Kunya* (the teknonym, typically starting with Abu or Umm), the *Laqab* (the honorific or descriptive title), and the *Nisba* (the affiliation by geography, tribe, or trade).12

Displaying this entire string by default severely degrades the user experience. The design recommendation is that the full name must not be the default display. To prevent cognitive overload, the card must default to the Display Form (الاسم المشهور)—the name by which the scholar is most famously and intuitively known, such as الإمام البخاري (Al-Imam Al-Bukhari) or شيخ الإسلام ابن تيمية (Shaykh al-Islam Ibn Taymiyyah). However, adhering strictly to the Zero Knowledge Loss mandate, a progressive disclosure mechanism must be implemented. An expansion toggle must allow the user to reveal the complete, unabridged name, satisfying the requirements of rigorous academic research and mirroring the precision of classical biographical dictionaries.12

### **Chronological Anchors and Death Dates**

The death date (تاريخ الوفاة) serves as the primary chronological anchor in Islamic historiography. The tradition categorizes scholars into generations (*Tabaqat*), and knowing a scholar's death date immediately places them in relation to the Prophet Muhammad, the early generations (*Salaf*), or specific historical eras.11

The death date must primarily be displayed in the Hijri calendar, as this is the native temporal framework of the Islamic sciences.15 However, an interface designed for a modern student with minimum traditional knowledge must bridge the cognitive gap, as many contemporary users lack an intuitive grasp of Hijri timelines. Therefore, a dual-display approach is mathematically and educationally optimal, presenting both the Hijri and Gregorian dates simultaneously to provide immediate historical context.10

### **Scholarly Standing, Titles, and Madhab Affiliation**

Islamic honorifics (الألقاب العلمية) are not mere pleasantries or generic compliments; they are rigorously earned designations that indicate a scholar's specific rank, functional role, and level of mastery within the scholarly hierarchy.16 For example, the title *Al-Hafiz* indicates an elite tier of Hadith memorization and critical mastery, implying the scholar has memorized a vast number of narrations along with their chains and defects.16 The title *Shaykh al-Islam* is a highly elevated designation granted to a paramount role model who possessed mastery across multiple branches of knowledge and had a vast following, a term that gained formal prominence in later centuries.18 The title *Al-Imam* denotes foundational leadership, most frequently applied to the absolute founders of the legal schools or unparalleled masters of a specific discipline.19

The author's highest, consensus-agreed scholarly standing must be prominently displayed as a visual badge preceding or accompanying their name. This immediate visual cue provides the student with instant context regarding the epistemological weight of the author's opinions. Furthermore, in fields such as Islamic jurisprudence (*Fiqh*) and theology (*Aqidah*), identifying a scholar's methodological school (*Madhab*) is mandatory.21 An excerpt from a Shafi'i text operates on entirely different foundational principles (*Usul*) than a Hanafi text. A dedicated metadata indicator for the Madhab must be persistently visible, ensuring the student contextualizes the ruling within its proper legal framework.21

### **Dynamically Tailored Biographical Blurbs**

The biographical blurb within the Source Card represents a critical intersection between historical data and modern computational generation. The blurb cannot be a static, generic encyclopedia entry. It must be dynamically tailored to the specific *type* of scholar, reflecting the distinct priorities that traditional *Tabaqat* literature placed on different scientific disciplines.11

Classical biographical dictionaries, often categorized as prosopography by modern historians, display little interest in the modern concept of character development; instead, they assume the subject's character is fixed and focus on their academic lineage, exactitude, and specific achievements within their field.13

For classical Hadith scholars, the blurb must heavily emphasize their *Rihlah* (arduous travels across the Islamic world to collect narrations), their rigorous criteria for accepting narrators, and the sheer volume of hadiths they memorized. The narrative focus remains strictly on their memory (*Hifz*) and their precision in transmission (*Dabt*).12 In contrast, for classical Fiqh scholars, the blurb must specify their rank within their respective legal school—whether they were an absolute independent jurist (*Mujtahid Mutlaq*), a jurist operating within the school's framework, or a standardizer of the school's opinions. It must highlight their primary teachers and explain how their specific texts are relied upon for issuing religious verdicts (*Fatwa*).21

When profiling polymaths who authored across multiple disciplines, the biographical focus must shift to highlight their prolific textual output (*Kathrat al-Tasanif*), their mastery across divergent fields (*Musharakah*), and their unique ability to synthesize prior knowledge into massive encyclopedic works.23 Modern scholars require an entirely different biographical approach. Modern biographical entries naturally lean toward institutional roles, societal impact, and the scholar's continuity with the classical tradition in the face of contemporary challenges. The blurb for a modern scholar should highlight their participation in modern fatwa councils, their academic leadership, and their specific confrontations with novel, modern legal issues (*Nawazil*).24

Finally, the library will inevitably contain texts by unknown or anonymous authors. In the medieval period, scholars sometimes found it stylistically sophisticated to omit the names of authors, assuming the educated reader would recognize the source, which creates significant attribution problems today.27 If the author is unknown, the blurb must transparently state this reality to maintain the integrity of the Zero Knowledge Loss principle. It should focus on what factual data exists: the geographical origin of the manuscript, the era estimated by paleographic analysis of the handwriting or paper, and the subsequent scholars who quoted the anonymous text.27

## **Source and Book Information Architecture**

A text in the Islamic scholarly tradition is rarely an isolated, standalone monolith; it exists within a highly structured taxonomic web of commentaries, summaries, and thematic classifications. The Source Card must visually represent this intricate taxonomy to properly orient the reader.

### **Genre, Science Classification, and Hadith Subgenres**

Classical Islamic libraries categorized texts meticulously, a practice formalized early on by bibliographers like Ibn al-Nadim in his *Fihrist*.29 The digital Source Card must display the primary science of the text. However, generic labels are insufficient. For Hadith literature in particular, simply labeling a book as "Hadith" violates the Zero Knowledge Loss principle, as the exact structural subgenre dictates how the student should interact with and derive rulings from the text.30

The Source Card must specify the distinct subgenre of the compilation. *Musannaf* and *Muwatta'* works are arranged topically by legal chapter, but unlike pure prophetic collections, they explicitly include the rulings and statements of the Companions (*Mawquf*) and the Successors (*Maqtu'*), making them hybrid texts of hadith and early jurisprudence.30 A *Musnad* is arranged fundamentally differently; it groups narrations by the name of the Companion who transmitted them, regardless of the topical subject matter, serving as a tool to ensure no narration was lost rather than as a quick reference for legal rulings.30 *Jami'* collections are comprehensive encyclopedias covering all major topics of the religion, while *Sunan* collections focus strictly on legal injunctions.30 Furthermore, the *Mustakhraj* genre represents a highly technical academic exercise where a later scholar takes an earlier collection and provides their own independent chains of transmission to the exact same hadiths, seeking to elevate the chain or find alternative wording.34 The UI must display the Science and the Specific Subgenre as distinct, hierarchical tags to educate the user on these structural differences.

### **The Textual Hierarchy of Multi-Layer Works**

Perhaps the most complex user interface challenge in Islamic digital libraries is accurately representing the commentary tradition. A massive portion of Islamic heritage consists of nested, interdependent texts: a highly condensed core text (*Matn*), a commentary on that text (*Sharh*), marginalia on the commentary (*Hashiya*), and super-marginalia or post-commentary notes (*Taqrirat* or *Ta'liqat*).2

Historically, orientalist scholarship frequently misunderstood and dismissed this commentary tradition as unoriginal or stagnant, a judgment that modern scholarship has definitively nullified by demonstrating the profound originality, debate, and evolution of thought contained within these marginal layers.2 The *Matn* is a compact text designed specifically for rote memorization, intentionally stripping away divergent opinions to provide a clean baseline. The *Sharh* literally means to "open up" or surgically expand; it unpacks the dense *Matn*, bringing in linguistic analysis, evidence, and divergent theological or legal views.2 The *Hashiya* represents micro-analysis, focusing on extreme edge cases, complex grammatical debates, and highly specific disputes that arise from the *Sharh*.36

When a user views a teaching unit extracted from a *Hashiya*, they must visually see the entire structural stack to understand the context of the fragment. The Source Card should feature a visual "Hierarchy Tree" that nests the texts. This visual nesting ensures the student immediately grasps that they are reading a highly specialized edge-case commentary, preventing them from mistaking a nuanced marginal debate for a foundational, universally agreed-upon rule.36

### **Book Significance and Bibliographic Metadata**

To fulfill the classical requirement of explaining the *Thamrah* (fruit) and *Martabah* (rank) of the book, a dedicated short blurb must explain the text's significance.3 This blurb answers critical pedagogical questions: Why did the author write it? Is it an introductory text for absolute beginners or an exhaustive reference for advanced jurists? What gap in the existing literature did it fill?

Furthermore, standard bibliographic metadata—specifically the Edition, the Investigator (*Muhaqqiq*), the Publisher, and the Publication Year—must be accessible via the expansion function.37 In the realm of classical Islamic texts, differing printed editions often alter the numbering of hadiths, the phrasing of classical texts due to reliance on different manuscripts, and the quality of the footnotes. Hiding edition metadata strips the text of its academic accountability.

## **Trust, Provenance, and the Epistemology of Disagreement**

In an era characterized by rampant digital misinformation, an Islamic library must embed its epistemology of trust directly into the user interface. The user must clearly understand the degree of certainty regarding the text's attribution to its purported author.

### **Handling Scholarly Disagreement on Authorship**

Classical texts are frequently attributed to historical scholars erroneously. This occurs through simple scribal errors, the conflation of authors with identical names, or intentional forgery known in academic circles as pseudepigraphy.28 The terminology used in the classical tradition to categorize these texts is highly precise. A text labeled *Mansub* (منسوب) is attributed to an author but requires further verification. A text labeled *Manhul* (منحول) is definitively forged or falsely attributed.41 A text categorized as *Fi Sihhati Nisbatihi Nazar* (في صحة نسبته نظر) indicates a live, unresolved dispute among verification scholars regarding its true author.41

Under the strict mandate of Zero Knowledge Loss, the library cannot simply hide a disputed book to avoid confusion, nor can it present a disputed attribution as absolute, verified fact. If a teaching unit originates from a contested text, a highly visible Trust Indicator—such as a specific warning icon—must appear directly next to the author's name. Interacting with this icon must reveal a dedicated panel detailing the dispute, presenting both sides of the academic argument, and citing the specific verification scholars who affirm or deny the attribution.9 This approach transforms a bibliographical problem into a vital educational moment for the student.

### **Provenance of Metadata**

Metadata does not materialize out of the ether; it is extracted from foundational bibliographic encyclopedias and modern computational datasets. The user must know exactly where the library obtained its facts to trust the interface.37 A "Sources of Verification" footer must exist within the expanded Source Card. This section will explicitly list the databases, classical catalogs, and digital repositories that informed the card's data points, such as Haji Khalifa's *Kashf al-Zunun* 9, Al-Zirikli’s *Al-A'lam* 10, Kahhala’s *Mu'jam al-Mu'allifin* 10, the structured YAML records of the OpenITI project 15, and the vast databases of Al-Maktaba Al-Shamila.45

## **UI/UX Design Principles for the Muslim Student**

The interface of the Source Card must be inherently Arabic-first, respecting right-to-left typography, classical Arabic ligatures, and traditional aesthetic motifs, while simultaneously adhering to modern principles of human-computer interaction to ensure usability.14

### **Progressive Disclosure**

The primary user experience principle dictating the architecture of the Source Card is "Progressive Disclosure." A student possessing minimal prior Islamic knowledge will be immediately paralyzed if confronted with dozens of dense bibliographical data points simultaneously.14 Therefore, the interface must operate across two distinct states.

The Short Form provides a quick-glance view that persists alongside the text. It displays only the absolute essentials: the Author's Display Name, Highest Title, Death Year, Book Title, Science/Genre, and a highly truncated sentence regarding the book's significance. The Expanded Form, triggered by deliberate user interaction, facilitates deep-dive research. It dims the surrounding interface and opens a comprehensive modal containing the exhaustive data: full unabridged lineage, complete layer structure, publisher metadata, detailed biographical blurbs, and the complex provenance trails.14

### **Educational Tooltips Without Assumption of Knowledge**

The card must never assume the user inherently knows what a *Mustakhraj* or a *Hashiya* entails. However, embedding long definitions directly into the primary text flow clutters the interface. Every technical classification term must feature a subtle visual cue, such as a dotted underline. Hovering over or tapping the term must invoke a brief tooltip defining the concept in plain language, thus seamlessly integrating educational scaffolding into the reading experience without patronizing the user or cluttering the visual hierarchy.30

## **Implementation Strategy: Agentic Teams vs. Deterministic Extraction**

To build this architecture at scale across thousands of volumes efficiently, the backend processing pipeline must strictly divide labor between deterministic data extraction and Large Language Model (LLM) agent generation. Relying entirely on LLMs for bibliographical data introduces unacceptable risks of hallucination, while relying purely on databases prevents the creation of fluid, tailored narratives.39

### **Deterministic Extraction**

Structured, factual metadata must be extracted deterministically via APIs or parsers from authoritative digital humanities sources.15 The data fields that must remain strictly deterministic include the full author names, death dates in both calendar systems, book titles and known aliases, all publisher and edition metadata, and the precise URIs that define the hierarchical layer structure of multi-layer works. Repositories like OpenITI provide this data cleanly through structured YAML files, which can be ingested directly into the library's database without generative interference.15

### **Generative Agent Teams**

Agentic LLM pipelines utilizing Retrieval-Augmented Generation (RAG) should be deployed exclusively for unstructured, narrative, and highly analytical tasks.39 A Biographical Agent can synthesize the tailored biographical blurbs by retrieving data from digitized *Tabaqat* literature (such as *Siyar A'lam al-Nubala'*) and formatting it according to the specific scholar type.11 A Pedagogical Agent can draft the "Book Significance" blurb by analyzing the author's original *Muqaddimah*, extracting the classical *Gharad* and *Thamrah* to explain the book's utility to the modern reader.3 Finally, a Dispute Resolution Agent can identify if a book is flagged as *Manhul* or *Mansub* across different databases, retrieving the conflicting scholarly opinions and drafting a neutral, objective summary of the debate, ensuring the Zero Knowledge Loss principle is met through balanced synthesis.40

## **Recommended Source Card Structure (Data Schema)**

The following schema defines the exhaustive structure for the Source Card, detailing the required Arabic UI field names, their functional descriptions, the origin of their data, and their behavioral state within the progressive disclosure interface.

| UI Field Name (Arabic) | Description & Purpose | Source Origin | UX Behavior State |
| :---- | :---- | :---- | :---- |
| **اسم المؤلف الشائع** | The display name or *Shuhrah* by which the scholar is best known. | Deterministic Extraction | Quick-Glance (Always Visible) |
| **اللقب العلمي** | The highest consensus-agreed academic standing (e.g., شيخ الإسلام). | Deterministic Extraction | Quick-Glance (Badge/Icon) |
| **سنة الوفاة** | The chronological anchor, displaying Hijri primary and Gregorian secondary. | Deterministic Extraction | Quick-Glance |
| **المذهب / العقيدة** | The methodological and theological school of the author. | Deterministic Extraction | Quick-Glance (Tag/Pill) |
| **البطاقة الشخصية الكاملة** | The unabridged lineage string (Ism, Nasab, Kunya, Laqab, Nisba). | Deterministic Extraction | Deep-Dive (Expanded Modal) |
| **نبذة عن المؤلف** | Tailored narrative blurb highlighting methodology, rihlah, or institutional role. | LLM Agent Synthesis | Quick-Glance (Truncated) / Deep-Dive (Full) |
| **عنوان الكتاب** | The widely recognized title of the specific text being studied. | Deterministic Extraction | Quick-Glance |
| **التصنيف العلمي** | Core science and precise subgenre. Features educational hover tooltips. | Deterministic Extraction | Quick-Glance |
| **أهمية الكتاب (الثمرة)** | Pedagogical purpose, historical rank, and utility of the book for the student. | LLM Agent Synthesis | Deep-Dive |
| **شجرة الكتاب (الطبقات)** | Visual hierarchy displaying the nested structure of Matn, Sharh, and Hashiya. | Deterministic Extraction | Quick-Glance (If nested) / Deep-Dive (Full) |
| **مؤشر التوثيق / خلاف النسبة** | Warns of disputed authorship and details the parameters of the scholarly debate. | Agent \+ Extraction | Deep-Dive (Appears only if disputed) |
| **بيانات الطبعة** | Publisher, Verification Scholar (*Muhaqqiq*), Year, and City of publication. | Deterministic Extraction | Deep-Dive |
| **مصادر التوثيق** | Bibliographic databases verifying the presented metadata. | Deterministic Extraction | Deep-Dive (Footer) |

## **Concrete Source Card Examples**

To demonstrate the architectural flexibility and resilience of this design framework, the following three examples map the schema onto radically different types of Islamic scholarly texts: a foundational Hadith collection, an intricate multi-layer commentary, and a modern pedagogical tract.

### **Example 1: Classical Hadith Collection**

**Context:** A teaching unit extracting a single, self-contained narration from *Sahih al-Bukhari*.

| Field | Content Displayed in Interface |
| :---- | :---- |
| **اسم المؤلف الشائع** | \[أمير المؤمنين في الحديث\] الإمام البخاري |
| **سنة الوفاة** | ت ٢٥٦ هـ (870 م) |
| **البطاقة الشخصية الكاملة** | أبو عبد الله محمد بن إسماعيل بن إبراهيم بن المغيرة بن بردزبة الجعفي البخاري |
| **نبذة عن المؤلف** | رحل في طلب الحديث إلى كافة حواضر العالم الإسلامي، وتميز بذاكرة حديدية ودقة متناهية (ضبط). وضع أشد الشروط صرامة لقبول الرواة، واعتبر فقهه في تراجم أبوابه دليلاً على عبقريته الاستنباطية. |
| **عنوان الكتاب** | الجامع المسند الصحيح المختصر من أمور رسول الله وسننه وأيامه (صحيح البخاري) |
| **التصنيف العلمي** | الحديث النبوي \> الجوامع *(Tooltip: كتب حديثية شاملة لأبواب الدين الثمانية)* |
| **أهمية الكتاب (الثمرة)** | أصح كتاب بعد كتاب الله بإجماع الأمة. استغرق تصنيفه ١٦ عاماً، وانتقى أحاديثه من بين ٦٠٠ ألف حديث، ليجمع فيه خلاصة السُنّة النبوية الصحيحة. |
| **شجرة الكتاب (الطبقات)** | متن مستقل |
| **بيانات الطبعة** | تحقيق: محمد زهير بن ناصر الناصر، الناشر: دار طوق النجاة، الطبعة: الأولى ١٤٢٢هـ |

### **Example 2: Multi-Layer Sharh (Commentary)**

**Context:** A teaching unit explaining a highly specific linguistic nuance, extracted from Ibn Hajar’s monumental commentary, *Fath al-Bari*.

| Field | Content Displayed in Interface |
| :---- | :---- |
| **اسم المؤلف الشائع** | \[الحافظ\] ابن حجر العسقلاني |
| **سنة الوفاة** | ت ٨٥٢ هـ (1449 م) |
| **المذهب / العقيدة** | المذهب: شافعي |
| **البطاقة الشخصية الكاملة** | أبو الفضل أحمد بن علي بن محمد بن أحمد بن حجر العسقلاني الكناني |
| **نبذة عن المؤلف** | خاتمة الحفاظ وإمام عصره بلا منازع. تميز بكثرة التصانيف والمشاركة في شتى العلوم من حديث وفقه وتاريخ. استطاع استيعاب وتركيب جهود قرون من التأليف الإسلامي ليقدم خلاصات علمية أصبحت مرجعاً لكل من جاء بعده. |
| **عنوان الكتاب** | فتح الباري بشرح صحيح البخاري |
| **التصنيف العلمي** | الحديث النبوي \> شروح الحديث |
| **أهمية الكتاب (الثمرة)** | أعظم شرح لصحيح البخاري، يمثل موسوعة شاملة في الفقه واللغة وعلوم الحديث. أمضى المؤلف في كتابته أكثر من ربع قرن، ممهداً له بمقدمة "هدي الساري" لبيان منهجه ودفع الإشكالات. |
| **شجرة الكتاب (الطبقات)** | └─ \[متن\] صحيح البخاري (البخاري) └─ **\[شرح\] فتح الباري (ابن حجر)** 📍 *أنت تقرأ هنا* |
| **بيانات الطبعة** | تحقيق: محب الدين الخطيب، الناشر: دار المعرفة \- بيروت، ١٣٧٩هـ |

### **Example 3: Modern Risalah (Tract)**

**Context:** A basic teaching unit outlining the obligatory pillars of prayer, extracted from a contemporary text.

| Field | Content Displayed in Interface |
| :---- | :---- |
| **اسم المؤلف الشائع** | \[العلامة\] الشيخ ابن باز |
| **سنة الوفاة** | ت ١٤٢٠ هـ (1999 م) |
| **المذهب / العقيدة** | المذهب: حنبلي |
| **البطاقة الشخصية الكاملة** | عبد العزيز بن عبد الله بن عبد الرحمن بن محمد بن عبد الله آل باز |
| **نبذة عن المؤلف** | من أبرز الشخصيات المؤسسية والعلمية في القرن العشرين. شغل منصب المفتي العام، وعُرف باهتمامه البالغ بالتعليم العام للأمة، وقدرته الفائقة على تيسير الفقه الكلاسيكي وتنزيله على النوازل المعاصرة بلغة سهلة ومباشرة. |
| **عنوان الكتاب** | الدروس المهمة لعامة الأمة |
| **التصنيف العلمي** | فقه عام / عقيدة \> رسالة |
| **أهمية الكتاب (الثمرة)** | رسالة مكثفة ومركزة صيغت خصيصاً لعموم المسلمين، لتأسيسهم في فروض الأعيان من عقيدة وطهارة وصلاة وأخلاق. تمثل نقطة انطلاق مثالية للمبتدئ. |
| **شجرة الكتاب (الطبقات)** | متن مستقل |
| **بيانات الطبعة** | الناشر: الرئاسة العامة لإدارات البحوث العلمية والإفتاء \- السعودية |

The comprehensive integration of traditional Islamic epistemological framing with modern computational extraction and progressive user interface design guarantees that the digital library functions not merely as a repository of text, but as a dynamic pedagogical environment. By resolutely adhering to the principle of Zero Knowledge Loss, the Source Card ensures that the modern student remains deeply and accurately anchored to the rigorous intellectual heritage of the Islamic tradition.

#### **Geciteerd werk**

1. Digital Maktaba Project: Proposing a Metadata-Driven Framework for Arabic Library Digitization \- CEUR-WS.org, geopend op april 14, 2026, [https://ceur-ws.org/Vol-3937/short13.pdf](https://ceur-ws.org/Vol-3937/short13.pdf)  
2. The Calligraphic State \- UC Press E-Books Collection, geopend op april 14, 2026, [https://publishing.cdlib.org/ucpressebooks/view?docId=ft7x0nb56r;chunk.id=0;doc.view=print](https://publishing.cdlib.org/ucpressebooks/view?docId=ft7x0nb56r;chunk.id%3D0;doc.view%3Dprint)  
3. الخطاب المقدماتي في التراث العربي \- منار الإسلام, geopend op april 14, 2026, [https://islamanar.com/arab-heritage/](https://islamanar.com/arab-heritage/)  
4. الخطاب المقدماتي عند العرب قــــراءة فـــي مقدمة الكتــــاب لعباس أرحيلــــــــــة \- موقع الكاتب والأكاديمي المغربي يوسف الإدريسي, geopend op april 14, 2026, [http://youssefelidrissi.blogspot.com/2015/04/blog-post\_48.html](http://youssefelidrissi.blogspot.com/2015/04/blog-post_48.html)  
5. 934 ( إن مبادئ كل فن عشرة ) \#همسات \#دروس\_المسجد\_الحرام \- YouTube, geopend op april 14, 2026, [https://www.youtube.com/shorts/ELrPh0hXA1A](https://www.youtube.com/shorts/ELrPh0hXA1A)  
6. اجتاهات العلماء يف التعامل مع مسائل السماع يف األزمنة الكالسيكية واملعاصرة \- DergiPark, geopend op april 14, 2026, [https://dergipark.org.tr/en/download/article-file/2846772](https://dergipark.org.tr/en/download/article-file/2846772)  
7. إجازات السماع في الدرس اللغوي \- شبكة الألوكة, geopend op april 14, 2026, [https://www.alukah.net/literature\_language/0/6550/%D8%A5%D8%AC%D8%A7%D8%B2%D8%A7%D8%AA-%D8%A7%D9%84%D8%B3%D9%85%D8%A7%D8%B9-%D9%81%D9%8A-%D8%A7%D9%84%D8%AF%D8%B1%D8%B3-%D8%A7%D9%84%D9%84%D8%BA%D9%88%D9%8A/](https://www.alukah.net/literature_language/0/6550/%D8%A5%D8%AC%D8%A7%D8%B2%D8%A7%D8%AA-%D8%A7%D9%84%D8%B3%D9%85%D8%A7%D8%B9-%D9%81%D9%8A-%D8%A7%D9%84%D8%AF%D8%B1%D8%B3-%D8%A7%D9%84%D9%84%D8%BA%D9%88%D9%8A/)  
8. طبقات الزيدية الكبرى (القسم الثالث) \- مكتبة مجالس آل محمد, geopend op april 14, 2026, [https://al-majalis.org/books/wp-content/uploads/ebooks/%D8%B7%D8%A8%D9%82%D8%A7%D8%AA-%D8%A7%D9%84%D8%B2%D9%8A%D8%AF%D9%8A%D8%A9-%D8%A7%D9%84%D9%83%D8%A8%D8%B1%D9%89-%D8%A7%D9%84%D9%82%D8%B3%D9%85-%D8%A7%D9%84%D8%AB%D8%A7%D9%84%D8%AB.html](https://al-majalis.org/books/wp-content/uploads/ebooks/%D8%B7%D8%A8%D9%82%D8%A7%D8%AA-%D8%A7%D9%84%D8%B2%D9%8A%D8%AF%D9%8A%D8%A9-%D8%A7%D9%84%D9%83%D8%A8%D8%B1%D9%89-%D8%A7%D9%84%D9%82%D8%B3%D9%85-%D8%A7%D9%84%D8%AB%D8%A7%D9%84%D8%AB.html)  
9. How (not) to mis-identify a manuscript: On scholarly lineage and transmission of errors, geopend op april 14, 2026, [https://themaydan.com/2016/10/not-mis-identify-manuscript-scholarly-lineage-transmission-errors/](https://themaydan.com/2016/10/not-mis-identify-manuscript-scholarly-lineage-transmission-errors/)  
10. الأعلام للزركلي \- تراث, geopend op april 14, 2026, [https://app.turath.io/book/12286](https://app.turath.io/book/12286)  
11. Siyar A'lam al-Nubala' \- Wikipedia, geopend op april 14, 2026, [https://en.wikipedia.org/wiki/Siyar\_A%27lam\_al-Nubala%27](https://en.wikipedia.org/wiki/Siyar_A%27lam_al-Nubala%27)  
12. THE TRANSMISSION OF IBN SAʿD'S BIOGRAPHICAL DICTIONARY KITĀB AL-ṬABAQĀT AL-KABĪR \- Lancaster University, geopend op april 14, 2026, [https://www.lancaster.ac.uk/jais/volume/docs/vol12/v12\_03\_Atassi\_056-080.pdf](https://www.lancaster.ac.uk/jais/volume/docs/vol12/v12_03_Atassi_056-080.pdf)  
13. Biographical literature (Chapter 18\) \- The New Cambridge History of Islam, geopend op april 14, 2026, [https://www.cambridge.org/core/books/new-cambridge-history-of-islam/biographical-literature/4C4CE6AD081855F055FFBAC4B5F08DDC](https://www.cambridge.org/core/books/new-cambridge-history-of-islam/biographical-literature/4C4CE6AD081855F055FFBAC4B5F08DDC)  
14. UI/UX Design of Academic Applications and Libraries at Universitas Islam Al-Azhar Based on Mobile App | Secure And Knowledge-Intelligent Research in Cybersecurity And Multimedia (SAKIRA), geopend op april 14, 2026, [https://sakira.unizar.ac.id/index.php/jurnal/article/view/52](https://sakira.unizar.ac.id/index.php/jurnal/article/view/52)  
15. OpenITI documentation \- Open Islamicate Texts Initiative, geopend op april 14, 2026, [http://openiti.org/documentation/](http://openiti.org/documentation/)  
16. Religious Titles in Islam: Understanding Roles & Ranks of Scholars \- Quran Gallery App, geopend op april 14, 2026, [https://qurangallery.app/topics/religious-titles-islam-shaykh-imam-scholar-ranks](https://qurangallery.app/topics/religious-titles-islam-shaykh-imam-scholar-ranks)  
17. The Methodology Of Al-Suyuti In His Book Tabaqat Al-Hafaz \- A Comparative Critical Study \- Elementary Education Online, geopend op april 14, 2026, [https://ilkogretim-online.org/index.php/pub/article/download/8157/7768/15530](https://ilkogretim-online.org/index.php/pub/article/download/8157/7768/15530)  
18. The Meaning of Shaykh al-Islām \- troid.org | Digital Daʿwah, geopend op april 14, 2026, [https://www.troid.org/the-meaning-of-shaykh-al-islam/](https://www.troid.org/the-meaning-of-shaykh-al-islam/)  
19. Islam Religious Leaders | Structure & Types \- Study.com, geopend op april 14, 2026, [https://study.com/academy/lesson/islamic-religious-leaders-titles-roles.html](https://study.com/academy/lesson/islamic-religious-leaders-titles-roles.html)  
20. Islamic honorifics \- Wikipedia, geopend op april 14, 2026, [https://en.wikipedia.org/wiki/Islamic\_honorifics](https://en.wikipedia.org/wiki/Islamic_honorifics)  
21. التعريف بالشافعية ومؤلفاتهم \- شبكة الألوكة, geopend op april 14, 2026, [https://www.alukah.net/sharia/0/6202/%D8%A7%D9%84%D8%AA%D8%B9%D8%B1%D9%8A%D9%81-%D8%A8%D8%A7%D9%84%D8%B4%D8%A7%D9%81%D8%B9%D9%8A%D8%A9-%D9%88%D9%85%D8%A4%D9%84%D9%81%D8%A7%D8%AA%D9%87%D9%85/](https://www.alukah.net/sharia/0/6202/%D8%A7%D9%84%D8%AA%D8%B9%D8%B1%D9%8A%D9%81-%D8%A8%D8%A7%D9%84%D8%B4%D8%A7%D9%81%D8%B9%D9%8A%D8%A9-%D9%88%D9%85%D8%A4%D9%84%D9%81%D8%A7%D8%AA%D9%87%D9%85/)  
22. طبقات الشافعية الكبرى \- المعرفة, geopend op april 14, 2026, [https://www.marefa.org/%D8%B7%D8%A8%D9%82%D8%A7%D8%AA\_%D8%A7%D9%84%D8%B4%D8%A7%D9%81%D8%B9%D9%8A%D8%A9\_%D8%A7%D9%84%D9%83%D8%A8%D8%B1%D9%89](https://www.marefa.org/%D8%B7%D8%A8%D9%82%D8%A7%D8%AA_%D8%A7%D9%84%D8%B4%D8%A7%D9%81%D8%B9%D9%8A%D8%A9_%D8%A7%D9%84%D9%83%D8%A8%D8%B1%D9%89)  
23. Makers of Islamic Civilization | Oxford Centre for Islamic Studies, geopend op april 14, 2026, [https://www.oxcis.ac.uk/makers-of-islamic-civilization](https://www.oxcis.ac.uk/makers-of-islamic-civilization)  
24. A Critical and Historical Overview of the Sīrah Genre from the Classical to the Modern Period, geopend op april 14, 2026, [https://www.mdpi.com/2077-1444/13/3/196](https://www.mdpi.com/2077-1444/13/3/196)  
25. مؤلفات عن الشيخ \- ابن باز, geopend op april 14, 2026, [https://maserah.binbaz.org.sa/categories/42/%D9%85%D9%88%D9%84%D9%81%D8%A7%D8%AA-%D8%B9%D9%86-%D8%A7%D9%84%D8%B4%D9%8A%D8%AE](https://maserah.binbaz.org.sa/categories/42/%D9%85%D9%88%D9%84%D9%81%D8%A7%D8%AA-%D8%B9%D9%86-%D8%A7%D9%84%D8%B4%D9%8A%D8%AE)  
26. نبذة مختصرة عن السيرة الذاتية لفضيلة الشيخ العلامة عبد العزيز بن عبد الله آل باز رحمه الله تعالى \- صيد الفوائد, geopend op april 14, 2026, [https://saaid.org/Warathah/1/binbaz.htm](https://saaid.org/Warathah/1/binbaz.htm)  
27. Why Medieval Arab Scholars Thought It Was Classier Not to Cite Sources, and Other Stylistic Choices, geopend op april 14, 2026, [https://arablit.org/2015/04/14/why-medieval-arab-scholars-thought-it-was-classier-not-to-cite-sources-and-other-stylistic-choices/](https://arablit.org/2015/04/14/why-medieval-arab-scholars-thought-it-was-classier-not-to-cite-sources-and-other-stylistic-choices/)  
28. Ridding Some Books from being Attributed to Al-Hafiz Abdul Ghani Al-Maqdisi \- Semantic Scholar, geopend op april 14, 2026, [https://pdfs.semanticscholar.org/fcf2/0f6df79000b4e9753776cda6aa3d42dac951.pdf](https://pdfs.semanticscholar.org/fcf2/0f6df79000b4e9753776cda6aa3d42dac951.pdf)  
29. Classification of the sciences in Islamic cultures (IEKO) \- International Society for Knowledge Organization, geopend op april 14, 2026, [https://www.isko.org/cyclo/islamic](https://www.isko.org/cyclo/islamic)  
30. أنواع المصنفات في الحديث النبوي \- إسلام ويب, geopend op april 14, 2026, [https://www.islamweb.net/ar/article/16725/%D8%A3%D9%86%D9%88%D8%A7%D8%B9-%D8%A7%D9%84%D9%85%D8%B5%D9%86%D9%81%D8%A7%D8%AA-%D9%81%D9%8A-%D8%A7%D9%84%D8%AD%D8%AF%D9%8A%D8%AB-%D8%A7%D9%84%D9%86%D8%A8%D9%88%D9%8A](https://www.islamweb.net/ar/article/16725/%D8%A3%D9%86%D9%88%D8%A7%D8%B9-%D8%A7%D9%84%D9%85%D8%B5%D9%86%D9%81%D8%A7%D8%AA-%D9%81%D9%8A-%D8%A7%D9%84%D8%AD%D8%AF%D9%8A%D8%AB-%D8%A7%D9%84%D9%86%D8%A8%D9%88%D9%8A)  
31. طرق المحدثين في التصنيف المحاضرة الثانية The second lecture, methods of modernizing classific, geopend op april 14, 2026, [https://uoanbar.edu.iq/eStoreImages/Bank/2255.pdf](https://uoanbar.edu.iq/eStoreImages/Bank/2255.pdf)  
32. أنواع تصنيف كتب الحديث (الجوامع، المسانيد، السنن، والمعاجم) | تيسير مصطلح الحديث 68, geopend op april 14, 2026, [https://www.youtube.com/watch?v=2Rta9NKbgl8](https://www.youtube.com/watch?v=2Rta9NKbgl8)  
33. منهج التصنيف عند المحدثين \- منصة محمد السادس للحديث الشريف, geopend op april 14, 2026, [https://hadithm6.ma/articles/%D9%85%D9%86%D9%87%D8%AC-%D8%A7%D9%84%D8%AA%D8%B5%D9%86%D9%8A%D9%81-%D8%B9%D9%86%D8%AF-%D8%A7%D9%84%D9%85%D8%AD%D8%AF%D8%AB%D9%8A%D9%86/%D8%A7%D9%84%D8%AA%D9%85%D9%87%D9%8A%D8%AF%D9%8A%D8%A9/%D8%A7%D9%84%D8%AF%D8%B1%D9%88%D8%B3-%D8%A7%D9%84%D8%AD%D8%AF%D9%8A%D8%AB%D9%8A%D8%A9](https://hadithm6.ma/articles/%D9%85%D9%86%D9%87%D8%AC-%D8%A7%D9%84%D8%AA%D8%B5%D9%86%D9%8A%D9%81-%D8%B9%D9%86%D8%AF-%D8%A7%D9%84%D9%85%D8%AD%D8%AF%D8%AB%D9%8A%D9%86/%D8%A7%D9%84%D8%AA%D9%85%D9%87%D9%8A%D8%AF%D9%8A%D8%A9/%D8%A7%D9%84%D8%AF%D8%B1%D9%88%D8%B3-%D8%A7%D9%84%D8%AD%D8%AF%D9%8A%D8%AB%D9%8A%D8%A9)  
34. 2- المستخرجات على الجوامع \- الخلاصة العلمية, geopend op april 14, 2026, [https://project.kholasah.com/book/%D8%A7%D9%84%D8%AA%D8%AE%D8%B1%D9%8A%D8%AC-85?t=2--%D8%A7%D9%84%D9%85%D8%B3%D8%AA%D8%AE%D8%B1%D8%AC%D8%A7%D8%AA-%D8%B9%D9%84%D9%89-%D8%A7%D9%84%D8%AC%D9%88%D8%A7%D9%85%D8%B9-9629\&ctype=%D8%A5%D8%AB%D8%B1%D8%A7%D8%A1%D8%A7%D8%AA-9069](https://project.kholasah.com/book/%D8%A7%D9%84%D8%AA%D8%AE%D8%B1%D9%8A%D8%AC-85?t=2--%D8%A7%D9%84%D9%85%D8%B3%D8%AA%D8%AE%D8%B1%D8%AC%D8%A7%D8%AA-%D8%B9%D9%84%D9%89-%D8%A7%D9%84%D8%AC%D9%88%D8%A7%D9%85%D8%B9-9629&ctype=%D8%A5%D8%AB%D8%B1%D8%A7%D8%A1%D8%A7%D8%AA-9069)  
35. كتب الحديث \- منصة محمد السادس للحديث الشريف, geopend op april 14, 2026, [https://hadithm6.ma/articles/%D9%83%D8%AA%D8%A8-%D8%A7%D9%84%D8%AD%D8%AF%D9%8A%D8%AB/%D9%85%D9%88%D8%A7%D8%B1%D8%AF](https://hadithm6.ma/articles/%D9%83%D8%AA%D8%A8-%D8%A7%D9%84%D8%AD%D8%AF%D9%8A%D8%AB/%D9%85%D9%88%D8%A7%D8%B1%D8%AF)  
36. Matn, Sharh, Hashiya, Taliqa, and Takmila in Islamic Intellectual History \- Mâverd, geopend op april 14, 2026, [http://maverd.blogspot.com/2015/02/matn-sharh-hashiya-taliqa-and-takmila.html](http://maverd.blogspot.com/2015/02/matn-sharh-hashiya-taliqa-and-takmila.html)  
37. Metadata \- How To FAIR, geopend op april 14, 2026, [https://www.howtofair.dk/how-to-fair/metadata/](https://www.howtofair.dk/how-to-fair/metadata/)  
38. Best practices for creating sharable metadata \- OCLC Support, geopend op april 14, 2026, [https://help.oclc.org/Metadata\_Services/CONTENTdm/Get\_started/best\_practices](https://help.oclc.org/Metadata_Services/CONTENTdm/Get_started/best_practices)  
39. Unlocking the Power of Metadata in Digital Asset Management \- Acquia, geopend op april 14, 2026, [https://www.acquia.com/glossary/metadata](https://www.acquia.com/glossary/metadata)  
40. The Problem of Authorship and Pseudepigraphy in Islamic Intellectual History \- JHI Blog, geopend op april 14, 2026, [https://www.jhiblog.org/2020/02/12/the-problem-of-authorship-and-pseudepigraphy-in-islamic-intellectual-history/](https://www.jhiblog.org/2020/02/12/the-problem-of-authorship-and-pseudepigraphy-in-islamic-intellectual-history/)  
41. الحاشية على قوانين الأصول‏-ج2 \- مساحة حرة | المكتبة الالكترونية, geopend op april 14, 2026, [https://www.masaha.org/book/view/3354](https://www.masaha.org/book/view/3354)  
42. إبراهيم جركس \- القرآن المنحول \[1\] \- الحوار المتمدن, geopend op april 14, 2026, [https://www.ahewar.org/debat/show.art.asp?aid=294643](https://www.ahewar.org/debat/show.art.asp?aid=294643)  
43. OpenITI \- al-Raqmiyyāt, geopend op april 14, 2026, [https://maximromanov.github.io/OpenITI/](https://maximromanov.github.io/OpenITI/)  
44. The New OpenITI Metadata Search \- KITAB, geopend op april 14, 2026, [https://kitab-project.org/The-New-OpenITI-Metadata-Search/](https://kitab-project.org/The-New-OpenITI-Metadata-Search/)  
45. شرح المكتبة الشاملة الجديدة- إصدار4 (حلقة 8/7 بيانات الكتب والمؤلفين خالد الشنيبر, geopend op april 14, 2026, [https://www.youtube.com/watch?v=j3oIhwur-Is](https://www.youtube.com/watch?v=j3oIhwur-Is)  
46. Integrating User Experience Design in Library and Information Science Education: A Mixed-Methods Study at an Omani Academic Institution \- University of Toronto Press, geopend op april 14, 2026, [https://utppublishing.com/doi/10.3138/jelis-2025-0021](https://utppublishing.com/doi/10.3138/jelis-2025-0021)  
47. Towards Conceptualization of Islamic User Interface for Islamic Website: An Initial Investigation \- ResearchGate, geopend op april 14, 2026, [https://www.researchgate.net/publication/228784566\_Towards\_Conceptualization\_of\_Islamic\_User\_Interface\_for\_Islamic\_Website\_An\_Initial\_Investigation](https://www.researchgate.net/publication/228784566_Towards_Conceptualization_of_Islamic_User_Interface_for_Islamic_Website_An_Initial_Investigation)  
48. Digital Maktaba Project: Proposing a Metadata-Driven Framework for Arabic Library Digitization \- ResearchGate, geopend op april 14, 2026, [https://www.researchgate.net/publication/389891586\_Digital\_Maktaba\_Project\_Proposing\_a\_Metadata-Driven\_Framework\_for\_Arabic\_Library\_Digitization](https://www.researchgate.net/publication/389891586_Digital_Maktaba_Project_Proposing_a_Metadata-Driven_Framework_for_Arabic_Library_Digitization)