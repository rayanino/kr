# Domain Primer — خزانة ريان

This document gives the architect domain grounding for design decisions. Read it before starting any new engine SPEC. It grows over time as the owner provides more domain knowledge.

---

## The Core Identity

**KR is not a library Rayane uses. KR IS Rayane's knowledge.**

The library's contents are what Rayane knows. The library's gaps are what he doesn't know. An error in the library is an error in his understanding. Growing the library is growing as a scholar. This is the foundational principle from which everything else follows.

Implications that govern every design decision:

1. **Quality is existential.** A wrong attribution means Rayane "knows" something false. A misrepresented position corrupts his understanding. Verification isn't good engineering — it's the difference between scholarship and misinformation. Every excerpt must meet the standard a scholar would hold himself to. Every entry must be something Rayane could cite in his own published work.

2. **Completeness is meaningful.** A gap in the library isn't a data issue — it's a gap in Rayane's scholarship. Gap detection is personal: "Your scholarship has no coverage of the Hanafi position on this topic."

3. **The library grows as Rayane grows.** When he studies → excerpts get placed, entries generated. When he masters a topic → entries deepen, cross-references multiply. When he produces original research → his conclusions feed back into the library alongside the classical scholars. The library is alive.

4. **Scholarly standards are the foundation, not a feature.** Every attribution must be verified. Every claim must be sourced. Every position must be correctly attributed to its holder. The bar is publishable scholarship, not useful summaries.

5. **Encyclopedic completeness is the endgame.** The library should eventually represent comprehensive knowledge of every science it covers — not highlights or key points, but the complete scholarly landscape that a scholar could rely on as their sole reference.

6. **Rayane's own voice belongs in the library.** His tarjih, his notes, his research papers, his conclusions — these are knowledge too. The library is not just "what scholars said" but "what scholars said + what Rayane concludes." His scholarly voice grows alongside the classical voices.

7. **Secure by design (D-033).** Errors don't just produce wrong answers — they corrupt understanding. A misattribution in one engine can distort how an entire science is understood if it propagates undetected. Every component must be designed to PREVENT errors structurally, not just detect them after the fact. Immutable artifacts, explicit decisions, fail-loud behavior, verification at every boundary, mandatory provenance, continuous corruption detection, and bounded blast radius for any single failure. This is not a quality feature — it is an architectural principle on par with the normalization boundary.

---

## The User

**Name:** Rayane
**Location:** Belgium (Leuven)
**Background:** Islamic studies student, non-technical. The application is built entirely for him.
**Primary madhhab:** None — studies all schools equally.
**School coverage mandate:** Equal coverage of all four Sunni madhahib plus non-madhhab scholars (Ibn Hazm, Zahiri school, contemporary salafi scholars, etc.). No school is primary or secondary. The application must never assume a default madhhab.
**Languages:** Arabic (strong — reads classical scholarly texts comfortably), Dutch, French, English. The application's scholarly content is Arabic; the interface and generated analysis may use any of the owner's languages. No Arabic language scaffolding needed — the interface focuses on scholarly substance, not language support.

**Interaction model:** Living scholarly partner. Not a passive library — the application should be proactive: suggest what to study, challenge understanding, detect gaps, alert when new sources arrive. It should feel like having a tireless, infinitely knowledgeable study companion.

### Study Profile

- **Sciences currently studying:** None yet. The application IS the enabler — Rayane is waiting for KR to begin his scholarly journey. First sciences once KR is operational: Arabic language sciences (Nahw, Sarf, Balagha). Other sciences follow once the Arabic foundation is solid.
- **What "highest level of scholarship" means:** The complete scholar — encyclopedic knowledge across all schools AND original scholarly production (tarjih, tahrir, research) AND teaching mastery (ability to explain and transmit). All three, not a choice between them.
- **Study method:** Primarily self-directed but wants structured guidance from KR. No current teacher/shaykh. **KR must fill the role of both the library and the guide.** This is not optional — without structured guidance from the application, there is no structure at all.
- **Current daily study workflow:** None yet — pending KR. **[PENDING: revisit once KR is in use to refine the interaction model]**
- **Frustrations with existing books and teaching methodologies:**
  - **No interconnection.** Topics are explained in isolation. They're not linked to related topics, not situated within the science, not situated within the chapter. There's no "storyline" — no narrative thread connecting why this topic follows the previous one and leads to the next.
  - **No structural overview.** There's no way to see an entire science drawn out — all its topics, how they correlate, which topics are foundational vs. derived, what depends on what. Ideally: a visual map of the entire science showing every topic and its relationships. **This is what the taxonomy tree aims to solve.**
  - **No per-topic scholarly landscape.** For a given topic, you can't easily see: its significance, the different opinions held by different schools, who holds each opinion, what evidence supports each position, and how positions evolved over time.
  - **Poor explanations.** Existing texts don't explain topics from the ground up. There are big logical jumps. Edge cases and common misunderstandings aren't addressed. The ideal: "explain like I'm 5" clarity — every concept built step by step, with explicit prerequisites, covering edge cases, mapping out the theory logically and completely. Not dumbed down, but maximally clear. **This is what the synthesizing engine aims to solve.**
  - **No prerequisite mapping.** Books assume knowledge without telling you what you need to know first. There's no "before reading this, make sure you understand X and Y."

- **What information about a book matters before starting to read it:**
  - **Author profile:** full biography, scholarly standing, madhhab, teachers, students, time period (hijri + miladi), other major works, known positions and methodology
  - **Work classification:** type (matn, sharh, hashiyah, mukhtasar, nazm, risalah, etc.), science and subject, relationship to other works (sharh of what? mukhtasar of what?)
  - **Scope and coverage:** what topics it handles, what it does NOT handle, theory vs. practice proportion, level (beginner / intermediate / advanced / specialist)
  - **Physical details:** page count, volume count, completeness (all volumes available?)
  - **Reputation and credibility:** scholarly reputation of this work, how widely cited, whether it's considered a reference work (mu'tamad) in its school/science
  - **This specific edition:** tahqiq quality, publisher credibility, is this print trustworthy/credible/uncorrupted, how does this edition compare content-wise to other prints or other digital sources where the same book is found
  - **Study context:** what to know before reading this (prerequisite knowledge and prerequisite books), what to read next after finishing, where this book fits in the classical learning progression for its science
  - **Comparative:** how other editions/prints differ content-wise (variant readings, missing sections, additional commentary), which edition is considered best
- **Sources known to exist but not accessible digitally:** Some books only exist in physical form (e.g., editions from bookstores like صفة الصفوة with no digital counterpart). Others are behind login walls. Two manual acquisition realities: (1) physical books → owner provides high-quality iPhone camera photos of pages, (2) login-gated digital sources → owner provides manually downloaded files. Additionally, many "digital" books online are professionally scanned PDFs (scanned through printers/flatbed scanners) — these are a major source format alongside structured text exports.

### Critical Design Implications

**Pipeline priority: the critical path starts AFTER a source is received.** The source acquisition phase (autonomous discovery, adding new source types, expanding file format support) can be expanded later. The most important work — what makes KR transformative — begins when a source enters the pipeline: normalization, passaging, atomization, excerpting, taxonomy placement, and synthesis. The source engine's first version should provide a minimum viable acquisition path that gets sources INTO the pipeline quickly. Don't over-engineer sourcing at the expense of the downstream engines that create the actual knowledge products.

**KR is not supplementing an existing study practice. It IS the study practice.** This means:

1. **The scholar interface is not optional or secondary — it is the primary product.** The engines exist to feed the interface. If the engines work perfectly but the interface doesn't guide study, KR has failed.

2. **Curriculum design is a core capability.** KR must be able to generate a complete study curriculum from zero: "You want to study Arabic language sciences. Here is the sequence. Start with Nahw. Within Nahw, start with [this matn]. Here is the first excerpt. Let me test your understanding before we move to the next concept."

3. **The application must know pedagogical sequencing for Islamic sciences.** Which book do you read first in Nahw? What are the classical learning progressions (mutun → shuruh → hawashi)? This is domain knowledge the architect must research and encode.

4. **Progress tracking is essential from day one.** Since KR is the only structure, Rayane needs to see: where he is in the curriculum, what he's mastered, what's next, how far he's come. The user model must support this.

5. **The "complete scholar" goal means KR must eventually support all three modes:**
   - Learning mode: absorb and understand positions (encyclopedic)
   - Research mode: compare, analyze, produce original tarjih (scholarly production)
   - Teaching mode: practice explaining positions, generate lesson outlines (teaching mastery)

---

## Islamic Scholarly Domain Knowledge

### Source Types and Authority

Islamic scholarship has a well-defined source hierarchy that the application must understand and encode:

1. **Quran** — the absolute primary source. No scholarly disagreement on its text (only on interpretation).
2. **Hadith** — prophetic traditions. Graded by reliability: sahih (authentic), hasan (good), da'if (weak), mawdu' (fabricated). The grading methodology (ilm al-hadith) is itself a science.
3. **Athar** — statements of the Companions (sahabah) and Successors (tabi'in). Authority varies by school.
4. **Scholarly works** — the vast corpus. Authority depends on the scholar's stature, the work's genre, and whether it represents the scholar's final position (some scholars changed views over their lifetime).

### Works vs. Sources

This distinction is fundamental to the source engine's identity model:

A **work** (مُؤلَّف) is the abstract intellectual creation — the book as a scholarly contribution. "al-Mughni by Ibn Qudamah" is a work. It has one author, one original date, one place in scholarly history.

A **source** (مَصدر) is a specific physical or digital manifestation of a work. The same work can exist as multiple sources: Shu'ayb al-Arna'ut's tahqiq of al-Mughni (Dar al-Risalah, 1997) is one source. Abdullah al-Turki's tahqiq of the same text (Dar 'Alam al-Kutub, 1997) is a different source. A Shamela HTML export of al-Turki's edition is yet another source (a digital manifestation of that edition).

**Same work ≠ duplicate.** Two different tahqiq editions of the same work are NOT duplicates — they differ in footnote apparatus, variant reading choices, textual corrections, and scholarly commentary. The source engine must group sources by work but never conflate distinct editions.

**Preferred edition.** The owner may designate one edition as preferred per work (typically the one with the best tahqiq). Excerpts come from the preferred edition; others serve as cross-references for variant readings.

### Work Genre Chains

Islamic scholarly works exist in genre relationships that form chains (sometimes 4-5 levels deep):

- **Matn** (متن) — core text. Dense, often terse, meant to be memorized. Example: al-Ajurrumiyyah in Nahw.
- **Sharh** (شرح) — commentary on a matn. Expands and explains. Example: Sharh Ibn 'Aqil on Alfiyyat Ibn Malik.
- **Hashiyah** (حاشية) — marginal note on a sharh. Comments on the commentary. Example: Hashiyat al-Sabban on Sharh al-Ashmuny.
- **Ta'liqat** (تعليقات) — notes on a hashiyah, or free-standing scholarly notes.
- **Mukhtasar** (مختصر) — abridgment of a larger work. Shorter but same content.
- **Nazm** (نظم) — versified summary. The content of a prose work rendered in poetry for memorization.
- **Taqrirat** (تقريرات) — lecture notes by students capturing a teacher's oral explanations.

These chains form a tree: Ajurrumiyyah (matn) → Sharh al-Kafrawi (sharh) → Hashiyat al-'Adawi (hashiyah). The source engine must track these derivative-work relationships. When a commentary cites "the author said," it means the matn author — tracking the chain tells you exactly which work is being referenced.

### Author Identity in Islamic Scholarship

Islamic scholars have complex multi-part names that create real engineering challenges:

- **Components:** ism (given name), nasab (patronymic chain — "ibn X ibn Y"), laqab (title — "al-Imam"), kunya (teknonym — "Abu Hanifah"), nisba (attribution — geographic, tribal, or school-based — "al-Baghdadi," "al-Hanafi")
- **Multiple names:** The same scholar is known by different names in different contexts. "Ibn Hajar" in hadith scholarship usually means Ibn Hajar al-Asqalani (d. 852 AH). "Ibn Hajar" in Shafi'i fiqh might mean Ibn Hajar al-Haytami (d. 974 AH). These are two completely different scholars separated by 122 years.
- **Disambiguation:** Scholars are conventionally distinguished by death date (hijri), nisba, or their most famous work. "al-Nawawi" is unique enough. "Ibn al-Qayyim" is uniquely Ibn Qayyim al-Jawziyyah. But "al-Razi" could be multiple scholars across centuries.
- **Name normalization:** Classical texts spell names inconsistently (hamza placement, taa marbuta, defective spelling). The source engine needs a scholar authority model that maps variant spellings to canonical identities.

### The Scholar Authority Model

This is a system-wide concept, not owned by a single engine. A **scholar authority model** is a centralized registry where every scholar encountered across ALL sources is mapped to a canonical identity. This model is critical because:

- **Synthesis requires it.** The synthesizer must know that "Sibawayhi" in source A, "سيبويه" in source B, and "عمرو بن عثمان بن قنبر" in source C are the same person. Without canonical identity, the synthesizer cannot build cross-source narratives.
- **Teacher-student graph.** When the authority model records that al-Akhfash studied under Sibawayhi, and al-Jarmi studied under al-Akhfash, the synthesizer can reconstruct intellectual genealogy (see `reference/ENTRY_EXAMPLE.md`). This graph is a KNOWLEDGE PRODUCT — it enables the scholar interface to show the transmission of ideas across generations.
- **Temporal ordering.** Death dates enable chronological sorting of scholarly positions. The authority model is the single source of truth for scholar dates.
- **School tracking.** A scholar's school affiliation(s) — which may differ by science (a scholar can be Hanbali in fiqh and Ash'ari in aqidah) — live in the authority model, not duplicated per source.

**How it grows:** The source engine creates initial scholar records when processing a new source. When the excerpting engine encounters a quoted scholar within text, it links to or creates an authority record. Over time, the model becomes increasingly rich — the 100th source mentioning al-Nawawi adds details the first source didn't have.

**Where it lives architecturally:** This is a shared resource (like the taxonomy trees) that multiple engines read and write. The source engine is the primary writer. The excerpting engine adds quoted-scholar references. The synthesizing engine is the primary reader. The architect must decide: is this a separate shared component, part of the source engine, or a registry that engines access via a common interface?

### Multi-Science Sources

Many scholarly works span multiple sciences. Examples:
- **المحلى by ابن حزم** — primarily fiqh, but contains extensive usul al-fiqh methodology and hadith analysis
- **الكتاب by سيبويه** — primarily nahw, but touches on sarf and Arabic balagha
- **إحياء علوم الدين by الغزالي** — covers fiqh, aqidah, tasawwuf, and ethics simultaneously
- **المقدمة by ابن خلدون** — covers history, sociology, economics, and Islamic sciences

The source engine must tag a source with ALL sciences it covers (a list, not a single value). The excerpting engine then assigns individual excerpts to their specific science. A single source might produce excerpts placed in 5 different science trees. The metadata model must support this: `science: ["fiqh", "usul_al_fiqh", "ilm_al_hadith"]` at the source level, with per-excerpt science narrowing.

### What Makes a Source Trustworthy

For printed editions (most of what's digitally available):
- **Tahqiq quality** — who verified the text against manuscripts? A tahqiq by a known muhaqiq (e.g., Shu'ayb al-Arna'ut, Ahmad Shakir, Abdul Salam Harun) is far more valuable than an unverified commercial print.
- **Manuscript base** — how many manuscripts were consulted? Which ones? Are they identified by their library/collection?
- **Publisher reputation** — some publishers (Dar al-Risalah, Mu'assasat al-Risalah) are known for scholarly rigor; others print uncritically.
- **Edition number** — later editions may incorporate corrections.
- **Footnote apparatus** — does the tahqiq identify variant readings, explain obscure terms, verify hadith references?

For manuscripts (future capability):
- **Copyist** — who copied it, when, from what source
- **Colophon** — end note with copying date, location, chain
- **Isnad al-kitab** — the transmission chain of the book itself (some books have well-documented chains)
- **Physical condition** — lacunae, water damage, illegible sections

### Metadata the Application Must Track Per Source

These categories map to the book briefing (D-022) AND serve as synthesis fuel (D-023). The synthesizing engine consumes metadata alongside excerpt content to produce entries with scholarly depth no single source contains. Every engine that touches metadata must preserve and enrich it with the synthesizer as the primary downstream consumer.

**The key insight:** an entry about a topic is not just "what the excerpts say." It's "what the excerpts say, contextualized by who said it, when, in what scholarly tradition, in response to what debate, building on whose earlier work, and how the position evolved." This contextualization comes from METADATA, not excerpt text. Without rich metadata, the synthesizer produces flat compilations. With it, the synthesizer produces scholarly narratives with temporal depth, intellectual genealogy, and historiographical awareness.

Some are captured at source intake, some enriched later by downstream engines or the owner.

**Minimum viable metadata (every source — captured at intake):**
- Title (Arabic + transliterated)
- Author (full name, nisba, birth/death dates hijri + miladi)
- Science classification (may be multiple: a book on usul al-fiqh also touches mantiq)
- Source format (Shamela HTML, PDF scan, PDF text, EPUB, iPhone photo, etc.)
- Acquisition date and provenance (where did the digital file come from?)
- Work type / genre: matn, sharh, hashiyah, mukhtasar, nazm, risalah, taqrirat, etc.

**Scholarly metadata (when available — captured at intake or enriched later):**
- Tahqiq editor(s) and their credentials
- Publisher, city, edition number, print year
- Manuscript base (which manuscripts, their library identifiers)
- Volume/part structure (many works are multi-volume; some have different numberings across editions)
- Original composition date (hijri) and context (why the author wrote it)
- Relationships to other works: "this is a sharh of [other book]", "this is a mukhtasar of [other book]"
- Author profile: scholarly standing, madhhab, known teachers, known students, other major works, methodology
- Work reputation: mu'tamad status in its school/science, citation frequency, scholarly consensus on its value
- Work level: beginner / intermediate / advanced / specialist (may be subjective — owner can override)
- Work scope: what topics it covers, what it explicitly does NOT cover, theory vs. practice proportion
- **Source authority level:** primary source (مصدر أصلي — original scholarly content), reference work (مرجع — compiles/organizes others' work), or modern compilation (معاصر — explains classical content for modern readers). The synthesizer weights these differently — primary sources are cited directly, reference works confirm and contextualize, modern compilations fill gaps. See "Primary vs. Secondary Source Distinction" section.
- **Multi-layer composition:** does this source contain text from multiple authors? (matn/sharh/hashiyah structure) If so, which layers are present and who is the author of each layer? See "The Multi-Layer Text Problem" section.

**Edition-specific metadata (per source, not per work):**
- Trustworthiness assessment: is this specific print/edition credible and uncorrupted?
- Comparison to other editions: how does this edition differ content-wise from other known prints?
- Preferred edition status: is this the owner's preferred edition for this work?
- **Text fidelity signal:** How reliable is the actual text data? This is SEPARATE from scholarly trustworthiness — a perfectly trustworthy source may have low text fidelity if the OCR was poor. Structured digital text (Shamela exports, text-embedded PDFs) → high fidelity. Professional scans → medium fidelity (OCR errors especially with diacritics, ب/ت/ث/ن confusions, marginalia). iPhone photos → variable fidelity. This signal must flow downstream (D-023) because: the excerpting engine should flag low-fidelity excerpts for human review, the synthesizer should weight high-fidelity sources more heavily, and the scholar interface should warn when claims rest on low-fidelity text.

**Pipeline-generated metadata (added by engines during processing, flows downstream via D-023):**
- **LLM extraction confidence:** each engine that makes a content decision (atomization type, excerpt topic, school attribution, taxonomy placement) must output a confidence score alongside the decision. This is NOT text fidelity (input quality) — it's the engine's certainty about its OWN output. Low-confidence decisions get flagged for human review; the synthesizer notes uncertainty rather than stating low-confidence claims as fact.
- **Takhrij data (التخريج):** when the excerpting engine encounters hadith source tracing in tahqiq footnotes (which collection, book/chapter/number, grading), it captures this as structured metadata. The synthesizer uses it to produce evidence-aware entries.
- **Layer attribution:** which layer (matn/sharh/hashiyah/editor) each excerpt originates from. Determines which author the excerpt is attributed to.

**Library tracking metadata (computed/updated throughout pipeline):**
- Ingestion status (acquired, normalized, passaged, excerpted, placed)
- Completeness (full text or partial? which volumes?)
- Known text quality issues (OCR errors, missing pages, corrupted sections)
- Alternative editions available (and which is preferred)
- Cross-references to other sources in the library (the citation network)

**Study context metadata (computed by taxonomy/synthesizing engines, consumed by scholar interface):**
- Prerequisite knowledge: what should be understood before reading this source
- Prerequisite books: what specific works should be read first
- Recommended next: what to read after finishing this source
- Position in classical learning progression for its science

### How Scholars Reference Other Works

In classical Arabic scholarly texts, references take many forms:
- Explicit: "قال ابن قدامة في المغني" (Ibn Qudamah said in al-Mughni)
- Semi-explicit: "ذكر في المغني" (it was mentioned in al-Mughni)
- Implicit: "قال بعض العلماء" (some scholars said) — requires scholarly knowledge to resolve
- Isnad-based: "حدثنا فلان عن فلان" (so-and-so narrated to us from so-and-so) — hadith transmission chains
- Genre-based: "في المختصر" (in the Mukhtasar) — assumes the reader knows which abridgment is meant in that scholarly tradition

The application must handle ALL of these. Resolving implicit references is a transformative capability — no existing tool does this well.

### Arabic as a Processing Language

The architect must understand WHY Arabic text processing is harder than English. These aren't edge cases — they affect EVERY passage in EVERY source.

**Unvocalized text (الكتابة بدون تشكيل).** Most Arabic text is written without diacritical marks (tashkil/harakat). The word "علم" without diacritics could be: عِلْم (knowledge), عَلِمَ (he knew), عَلَّمَ (he taught), عُلِمَ (it was known), or عَلَم (flag). Context disambiguates — but an LLM processing a passage must handle this ambiguity. Classical scholarly texts sometimes ADD diacritics on ambiguous words, and tahqiq editors add them more systematically. The normalization engine must PRESERVE diacritics when present — they carry semantic weight. Stripping them is information destruction.

**Morphological density.** Arabic words encode more information than English words. A single Arabic word can be an entire sentence: "أفلم يستخرجوها" = "did they then not extract it?" (question particle + conjunction + negation + verb + subject pronoun + object pronoun). This morphological richness means that "word count" is a poor measure of content density. A 200-word Arabic passage may contain as much information as a 500-word English one. The passaging engine must calibrate passage size by semantic density, not word count.

**Ellipsis (الحذف والإضمار).** Arabic commonly omits words that are "understood from context." Classical texts are especially terse — scholars wrote for an audience that could fill in the gaps. Example: "باب الفاعل" could mean "chapter on [the definition and rules of] the [grammatical] subject" — four implicit words. This is critical for self-containment: an excerpt that is "self-contained" to a scholar who knows the conventions may NOT be self-contained to a beginner. The excerpting engine's self-containment test must consider the target audience (the owner's current level, from the user model). The synthesizing engine must EXPAND elliptical passages when generating entries for lower-level understanding.

**Technical terms (المصطلحات) vary across schools and periods.** The SAME concept often has DIFFERENT names in different schools, periods, or regions. Example: what Basran grammarians call "المفعول له" (adverbial of cause), some Kufan grammarians call "المفعول من أجله." What early hadith scholars call "الخبر" (report), later scholars distinguish into hadith (from the Prophet ﷺ) and athar (from Companions). The taxonomy engine must handle synonym mapping — different names for the same leaf. The synthesizer must note when scholars use different terminology for the same concept, so the entry doesn't present a verbal disagreement as a substantive one.

**Implicit scholarly context.** Arabic scholarly texts assume the reader knows the tradition. "قال الإمام" (the Imam said) means different scholars in different contexts: in Shafi'i fiqh, "الإمام" = al-Shafi'i. In Hanbali fiqh, "الإمام" = Ahmad ibn Hanbal. In nahw, it could mean Sibawayhi. The excerpting engine cannot resolve these references without knowing the source's school and science context — which comes from source metadata. The scholar authority model helps: given the source's school context, "الإمام" maps to a specific canonical scholar.

### Special Source Types: Quran and Hadith Collections

The Quran and the major hadith collections are NOT regular books. They have special properties that affect how every engine handles them.

**The Quran:**
- **Fixed canonical text.** There is NO textual variation in the Quran (unlike scholarly works with manuscript differences). A standard digital text exists (the Uthmani script, mushaf al-madinah). The source engine does NOT need OCR for Quran text — it should use a canonical digital source.
- **Cited everywhere.** Quran verses appear as evidence in EVERY science. When the excerpting engine encounters "قال تعالى: {وَأَقِيمُوا الصَّلَاةَ}" in a fiqh text, it must recognize this as a Quran citation and tag it with the surah/ayah reference (2:43). This enables the synthesizer to cross-reference all excerpts that cite the same verse.
- **Variant recitations (القراءات).** The Quran has 10+ accepted recitation variants that occasionally differ in ways that affect meaning (e.g., whether a word is read as active or passive voice). These variants are ALL considered valid — they're not "errors." When a fiqh ruling depends on a specific recitation variant, the synthesizer must note this.
- **Tafsir sources cite it verse by verse.** Tafsir (Quran exegesis) books are organized by verse. The passaging engine must handle this: each verse's commentary is a natural passage unit.

**Major hadith collections (الكتب الستة and others):**
- **Standard numbering.** Each hadith in the major collections (Bukhari, Muslim, Abu Dawud, Tirmidhi, Nasa'i, Ibn Majah) has a standard number. "Bukhari #6018" is a precise reference that any scholar can locate. The source metadata must capture this numbering.
- **Cross-collection identity.** The SAME hadith (same text, same meaning) appears in multiple collections with different chains. "Agreed upon" (متفق عليه) means it's in both Bukhari and Muslim. The excerpting engine will generate separate excerpts from each collection — but the synthesizer must recognize they're the SAME hadith and not present them as independent evidence. This is a form of excerpt deduplication specific to hadith.
- **Hadith = chain + text.** Every hadith has two parts: the isnad (chain of narrators) and the matn (actual text). When processing hadith collections, the atomization engine must separate these — they're fundamentally different types of content.

### Book Structures Beyond Prose

Islamic scholarly books come in several structural formats that each require different processing:

**Prose treatise (الرسالة / المتن المنثور).** Standard continuous text. Most common. Standard processing pipeline works.

**Versified text (المنظومات).** Covered in "Versified Texts" section above. Requires verse-aware processing.

**Q&A format (المسائل / الفتاوى).** Some books are structured as questions and answers: "سُئل عن رجل..." (he was asked about a man who...) followed by the answer. Each Q&A pair is a natural self-contained unit. The passaging engine must recognize this structure. The atomization engine should type the question and answer as distinct atoms. Fatwa collections (مجموع الفتاوى) are organized this way.

**Tabular/list format (الاختلاف books).** Some works catalog disagreements in a structured format: "المسألة: ... القول الأول: ... القول الثاني: ... الراجح: ..." (The issue: ... First position: ... Second position: ... Preferred: ...). These map almost directly to taxonomy entries. The excerpting engine should recognize this as pre-structured scholarly content.

**Dictionary format (المعاجم).** Lexicographic works (لسان العرب, القاموس المحيط) are organized alphabetically by root. Each entry is a self-contained unit about one word/root. The passaging engine should recognize dictionary structure and make each entry a passage.

**Commentary format (الشرح).** Covered in "Multi-Layer Text Problem" above. Requires layer-aware processing throughout.

The source engine must classify each source's structural format so downstream engines can apply format-appropriate processing strategies.

### Cross-Science Topic Overlap

A single concept can appear in MULTIPLE sciences with DIFFERENT meanings and treatments:

**Example: الاستثناء (exception/exclusion):**
- In **Nahw** (grammar): a grammatical construction with specific rules about إعراب (case marking)
- In **Usul al-fiqh** (legal theory): a legal principle for narrowing general statements — "all foods are halal EXCEPT..."  
- In **Fiqh** (applied law): specific rulings about exceptions in contracts, oaths, divorce formulas

These are NOT the same topic. The grammatical rules of الاستثناء are different from the legal rules. But they're RELATED — the grammatical analysis affects how legal exceptions are interpreted (this is exactly what Scenario 3 in USER_SCENARIOS.md describes).

**Architectural consequence:** Each science has its own taxonomy tree. الاستثناء appears as a leaf in the Nahw tree AND as a leaf in the Usul tree AND potentially in the Fiqh tree. These are SEPARATE leaves with SEPARATE excerpts. The taxonomy engine must support **cross-science links** — not merging the leaves, but recording that "nahw/الاستثناء is conceptually related to usul/الاستثناء." The synthesizer can then produce cross-science entries when requested (Scenario 3), drawing from excerpts at both leaves.

The scholar interface must understand these connections. When the owner studies الاستثناء in Nahw, KR should note: "This grammatical concept also has implications in Usul al-fiqh — would you like to see the connection?"

### What Happens When the Library Grows

The architect must design for a library that CHANGES over time. Adding, correcting, and removing content triggers cascading effects:

**Adding a new source triggers:**
1. Source engine creates source metadata + freezes file → new record in source registry
2. Normalization → passaging → atomization → excerpting produces NEW excerpts
3. Taxonomy engine places new excerpts at leaves → may trigger tree evolution proposals if no suitable leaf exists
4. At every leaf that received a new excerpt, the existing entry is now STALE (it doesn't incorporate the new evidence)
5. Synthesizing engine must regenerate entries at affected leaves
6. If the new source adds a new SCHOOL'S perspective at a leaf, entirely new per-school entries may be created

**A single 12-volume fiqh encyclopedia could add thousands of excerpts across hundreds of leaves, triggering hundreds of entry regenerations.** The architecture must handle this gracefully: batch processing, priority ordering (regenerate the owner's current study topics first), and incremental updates (regenerate only what changed, not everything).

**Correcting an excerpt triggers:**
1. Excerpt metadata updated (e.g., school attribution fixed)
2. Entry at the excerpt's leaf marked stale → regenerated
3. If the correction changes the excerpt's leaf placement, TWO leaves are affected (old and new)
4. If the correction reveals a pattern (Scenario 8), the pattern becomes a rule → ALL entries that might be affected by the pattern are marked stale

**Removing a source triggers:**
1. All excerpts from that source are removed
2. Every leaf that had excerpts from that source needs entry regeneration
3. Coverage metrics update (a leaf might drop below minimum coverage)

**Knowledge product versioning:** Entries are regenerated. The owner may have studied the OLD version. The system should track entry versions so the scholar interface can say: "This entry was updated since you last studied it. The new version includes evidence from [new source]. Key changes: [diff summary]." This is not just nice-to-have — it's how the owner keeps their knowledge current as the library grows.

**Excerpt deduplication.** Five sources may all quote the same hadith, or all paraphrase the same definition from the same original scholar. The excerpting engine will produce 5 separate excerpts. The taxonomy engine places them all at the same leaf. The synthesizer must recognize that these are REDUNDANT — it should present the content once (citing the strongest source) rather than 5 times. This requires semantic similarity detection across excerpts at the same leaf: "these 5 excerpts all say the same thing in different words."

### Science Relationships

Islamic sciences are deeply interconnected. The application must understand these relationships:
- **Usul al-fiqh** (legal theory) serves **fiqh** (law) — you can't understand rulings without understanding methodology
- **Nahw** (grammar) and **sarf** (morphology) serve everything — all sciences are transmitted in Arabic
- **Balagha** (rhetoric) serves Quran interpretation and literary analysis
- **Ilm al-hadith** (hadith methodology) serves fiqh, aqidah, tafsir — any science that relies on hadith evidence
- **Aqidah** (theology) and **fiqh** (law) sometimes overlap (e.g., issues where theological stance affects legal ruling)
- **Mantiq** (logic) serves usul al-fiqh and was controversial among scholars
- **Tafsir** (Quran exegesis) draws on virtually every other science

When the taxonomy engine places excerpts, these inter-science links matter. An excerpt about a grammatical point in Sibawayhi's al-Kitab may be relevant to a fiqh ruling that hinges on Arabic syntax.

### Core Scholarly Methodology Concepts

These concepts are essential for designing the taxonomy and synthesizing engines:

**المسألة (mas'ala — the scholarly question/issue).** This is the fundamental unit of scholarly discourse. A مسألة is a specific question on which scholars have taken positions: "Is بسملة a verse of الفاتحة?" or "Does touching a woman break wudu?" Each taxonomy leaf often corresponds to one مسألة or a cluster of tightly related ones. Understanding what constitutes a مسألة — how scholars formulate, scope, and distinguish one question from another — is essential for designing taxonomy structure.

**Evidence types (أدلة).** Islamic scholars support positions with specific types of evidence, in a recognized hierarchy. The excerpting engine must detect and tag which type of evidence an excerpt contains:
- **القرآن (Quran)** — Quranic verses, often cited by surah and ayah number
- **الحديث (Hadith)** — prophetic narrations, typically with an إسناد (chain of narrators) followed by the متن (text). The isnad is scholarly apparatus, not the position itself.
- **الإجماع (Ijma — consensus)** — claims that all scholars agree on a point. Important to detect because consensus claims are either true (and settle the issue) or contested (and the disagreement is about whether consensus actually exists).
- **القياس (Qiyas — analogy)** — reasoning by analogy from a known ruling to a new case. The excerpt will contain the أصل (base case), the فرع (new case), and the علة (shared cause).
- **قول الصحابي (companion statement)** — statement of a companion of the Prophet, which has special evidentiary weight in some methodologies.
- **عقل (rational argument)** — purely logical reasoning, especially in aqidah and usul al-fiqh.
- **استصحاب (presumption of continuity)** — the legal presumption that the status quo continues until evidence changes it.

The synthesizing engine uses evidence type tags to construct richer entries: "The Hanafi position is supported by Quranic evidence (2:228) and analogy, while the Shafi'i position relies on hadith evidence and companion statements."

**الخلاف (khilaf — scholarly disagreement).** Not all disagreements are the same. Islamic scholarly tradition distinguishes:
- **خلاف لفظي** (verbal disagreement) — scholars use different words but mean the same thing. Not a real disagreement.
- **خلاف حقيقي** (substantive disagreement) — scholars genuinely hold different positions on the same question.
- **خلاف معتبر** (respected disagreement) — a real disagreement where each side has valid evidence.
- **خلاف شاذ** (aberrant disagreement) — a position held by a scholar but rejected by the overwhelming majority.

The synthesizing engine must distinguish these types. Treating a verbal disagreement as substantive inflates the appearance of scholarly discord. Treating an aberrant position as equal to the consensus distorts the scholarly landscape.

**تحرير المسألة (tahrir al-mas'ala — precisely formulating the issue).** Before listing positions, scholars first precisely define WHAT the disagreement is about. Two scholars who appear to disagree may actually be answering different questions. The synthesizing engine must do this: before presenting positions, precisely formulate what question each scholar is answering. If their questions differ, they don't disagree — they're addressing different مسائل.

**الترجيح (tarjih — scholarly preference/weighing).** When multiple positions exist, scholars evaluate which is strongest based on evidence quality, methodological soundness, and other criteria. The synthesizing engine must eventually support this: presenting which position is strongest and why, according to which methodology. The owner's own tarjih (scholarly conclusions) are also valid entries in the library (D-018: the owner's voice belongs in the library).

**المعتمد (mu'tamad — the relied-upon position).** Within each madhhab, there is usually one position that the school officially adopts on each مسألة. This is the mu'tamad — the position that fatwa is given upon, the one students are taught, the one referenced works codify. Example: in Hanbali fiqh on a given issue, there may be 3 positions (from Ahmad, his students, and later scholars), but the mu'tamad is one specific position identified by authoritative reference works. The synthesizer must identify the mu'tamad when it exists, and distinguish it from minority positions within the same school. This is NOT the same as "majority position across all schools" — it's the authoritative position WITHIN a school.

**اجتهاد vs تقليد (ijtihad vs taqlid).** This distinction affects how the synthesizer treats sources:
- **اجتهاد** (independent scholarly reasoning) — when a scholar examines evidence directly and reaches their own conclusion. Mujtahid scholars (like the four school founders) have positions that carry independent weight.
- **تقليد** (following a school's established methodology) — when a later scholar applies the school's principles to reach a conclusion consistent with the school's framework. Most later scholars in a madhhab are muqallids.
The synthesizer should know whether a position represents original ijtihad or is derived through taqlid, because this affects how the position is weighted and presented. A mujtahid's direct evidence-based position has different scholarly character than a later muqallid's application of school methodology.

**تراجع العالم (scholar's retraction / changed position).** Some scholars changed their views over their lifetime. الشافعي had an "old" (قديم) and "new" (جديد) position on many issues after moving from Iraq to Egypt. الأشعري changed theological positions dramatically. When the library has sources from different periods of a scholar's career, the synthesizer must present the FINAL position as primary and the earlier position as historical context, not as a live alternative. The source metadata (composition date) and scholar authority model enable this.

### Hadith Methodology and Additional Scholarly Concepts

**تصحيح الأحاديث (hadith authentication).** Hadith have a grading system the synthesizer must understand:
- **صحيح** (sahih — authentic): meets all criteria of authenticity. Strongest evidence.
- **حسن** (hasan — good): minor weakness but still acceptable as evidence.
- **ضعيف** (da'if — weak): has a weakness in its chain or text. Scholars disagree on whether weak hadith can be used for secondary matters.
- **موضوع** (mawdu' — fabricated): not a real hadith. Must never be cited as evidence.

When an excerpt cites a hadith, the excerpt metadata should ideally carry the hadith's grading. This affects how the synthesizer weighs the position: a ruling based on a sahih hadith is stronger than one based on a weak hadith (within the same methodology). The source engine should capture hadith references; the excerpting engine should tag them; the synthesizer should use grading in its analysis.

**إسناد (isnad — chain of narration).** Every hadith has a chain: "A told me that B told him that C told him that the Prophet ﷺ said..." The chain's integrity determines the hadith's grade. The excerpting engine will encounter isnad chains in source texts — they are NOT the author's words, they are transmission metadata. The atomization engine must recognize isnad as a distinct atom type so it's handled correctly.

**الناسخ والمنسوخ (abrogation).** Some Quranic verses and hadith abrogate (cancel) earlier ones. A synthesizer that presents an abrogated ruling as current is producing a dangerous error. The synthesizing engine must track which rulings have been abrogated and by what evidence. This is a critical scholarly integrity requirement — not an edge case.

**الإجماع (consensus).** When qualified scholars unanimously agree on a ruling, most schools consider it binding. The synthesizer must know when consensus exists on a topic because: (1) it changes how the entry is structured (consensus topic = the entry should state the consensus and note any dissent, not present it as an open question), (2) it affects quality validation (an entry that implies scholarly disagreement on a consensus topic is wrong).

Note: the evidence type hierarchy (Quran → Hadith → Ijma → Qiyas) and school-specific weighting differences are covered in "Evidence types" above. Different schools weigh these differently — Hanafis accept more types of قياس; Zahiris reject it entirely. The synthesizing engine must know which evidence each position relies on, because evidence TYPE affects how strong a position is within its own methodology.

### The Multi-Layer Text Problem

This is one of the most critical engineering challenges in Islamic text processing. Many works in the library are NOT single-author texts — they are multi-layer compositions where different authors' words appear on the same page:

**In a hashiyah on a sharh of a matn, a SINGLE PAGE contains up to 4 layers of text:**
- **Layer 1 — Matn text** (often bold, bracketed, or preceded by "قال المصنف"): the original author's terse core text, e.g., al-Ajurrumiyyah by Ibn Ajurrum (d. 723 AH)
- **Layer 2 — Sharh text** (the main body): the commentator's explanation, e.g., al-Kafrawi's commentary (d. 1202 AH)
- **Layer 3 — Hashiyah text** (marginal notes, sometimes typeset inline): notes on the commentary, e.g., al-Adawi's marginal notes
- **Layer 4 — Tahqiq notes** (modern footnotes): the editor's scholarly apparatus, variant readings, hadith verification

**Each layer has a different author, different time period, different authority level.** When the normalization engine encounters "قال المصنف: المبتدأ هو الاسم المرفوع" — those are Ibn Ajurrum's words (Layer 1), quoted by al-Kafrawi (Layer 2). If the atomization engine doesn't recognize the layer shift, the excerpting engine will attribute Ibn Ajurrum's definition to al-Kafrawi. This is a scholarly integrity violation.

**The signals that mark layer transitions:**
- "قال المصنف" (the [matn] author said) — Layer 2 → Layer 1 transition
- "قال الشارح" (the commentator said) — Layer 3 → Layer 2 transition (in a hashiyah)
- "قوله" (his saying) — usually Layer 2 or 3 quoting the layer above
- Typographic conventions: bold, brackets, indentation, font size — format-specific but consistent within a source
- Footnote markers — Layer 4 transitions

**The normalization engine must identify these layers** using format-specific markup signals. The atomization engine must tag each atom with its layer. The excerpting engine must attribute correctly: an excerpt from Layer 1 text belongs to the matn author, even though it appears in the sharh source. The source metadata must record the full layer chain so the synthesizer knows: "this definition comes from al-Ajurrumiyyah (Layer 1), as quoted in al-Kafrawi's commentary (Layer 2), from the edition with al-Adawi's notes (Layer 3), tahqiq by so-and-so (Layer 4)."

### Per-Science Behavioral Differences

The architect must understand that different Islamic sciences have FUNDAMENTALLY different characteristics that affect how every engine processes them. This is why SCIENCE.md (Level 3) exists — it customizes engine behavior per science.

**Sciences with active schools (مذاهب):**
- **Fiqh** — 4 Sunni schools (Hanafi, Maliki, Shafi'i, Hanbali) + Zahiri + others. School identity is THE primary organizer. Entries are per-school. Every excerpt needs school attribution. The mu'tamad concept applies.
- **Aqidah** — 3+ schools (Ash'ari, Maturidi, Athari/Hanbali). School attribution critical. Some topics have consensus across schools; others are deeply divided.
- **Usul al-fiqh** — Schools exist but blur: Hanafis and Shafi'is have distinct usuli frameworks, but individual scholars may cross school lines.

**Sciences with historical (not active) schools:**
- **Nahw** — Basran and Kufan schools were real but extinct by the 5th century AH. Modern grammar follows a merged tradition (dominated by Basran foundations). School attribution matters for historical analysis but doesn't organize modern study.
- **Sarf** — Similar to Nahw. Historical Basran/Kufan distinctions exist but are not actively maintained.

**Sciences with NO scholarly disagreement:**
- **Tajwid** — The rules of Quran recitation are fixed by oral transmission. There is virtually no خلاف (disagreement). The entry structure for a Tajwid topic is: "the rule is X. Period." Different recitation modes (qira'at) exist but are considered equally valid, not competing positions.

**Sciences where evidence type dominates:**
- **Ilm al-hadith** — The science of hadith methodology. Entries here are about METHODS of authentication, not about specific rulings. The evidence hierarchy is meta-level: "how do we evaluate evidence?" rather than "what does the evidence say?"
- **Tafsir** — Quran exegesis. Entries must handle multiple dimensions: linguistic analysis, reason for revelation (سبب النزول), legal implications, theological implications. A single verse may have excerpts from grammar, fiqh, aqidah, and history.

**Why this matters for the architect:** A one-size-fits-all pipeline that treats all sciences identically will fail. The excerpting engine must know whether school attribution is mandatory (fiqh) or optional (tajwid). The taxonomy engine must know whether to create per-school branches (fiqh) or not (nahw). The synthesizing engine must know whether to present positions as competing schools (fiqh) or as historical evolution (nahw). SCIENCE.md (Level 3) encodes these differences — but the architect must design the HOOKS in each engine that Level 3 can customize.

### Versified Texts (المنظومات)

A significant portion of the Islamic scholarly corpus is in VERSE form (نظم). These are not poetry in the literary sense — they are technical content deliberately composed in meter and rhyme for memorization:

- **ألفية ابن مالك** — 1002 verses encoding all of Arabic grammar
- **تحفة الأطفال** — 61 verses on Tajwid rules
- **الجزرية** — 107 verses on Tajwid
- **لامية الأفعال** — 120 verses on Arabic morphology
- **منظومة البيقونية** — 34 verses on hadith terminology
- **الرحبية** — 175 verses on Islamic inheritance law

**These have completely different structure than prose.** Each بيت (verse/couplet) is a self-contained unit. A بيت has two hemistichs (شطر). The passaging engine must recognize verse structure and NOT split a بيت across passage boundaries. The atomization engine must treat each بيت as an atom (or pair of atoms for the two hemistichs). The excerpting engine must understand that a verse often encodes a RULE — the self-containment test is different (a single بيت may be self-contained even if it's only 10 words, because the verse IS the complete statement of the rule).

**Verse numbering matters.** Scholars reference الألفية by line number: "ألفية line 75" is a precise scholarly reference. The source metadata must capture verse numbering. The excerpting engine must preserve it.

**Commentaries ON versified texts** are prose. A single بيت may have pages of commentary. The multi-layer text problem (above) applies: the verse text (Layer 1) sits inside the prose commentary (Layer 2).

### LLM Extraction Confidence

Every content decision made by an LLM (atomization, excerpting, classification, placement) has an associated confidence level. This is SEPARATE from text fidelity (which measures how reliable the input text is). LLM confidence measures how sure the engine is about its OWN decision.

**Example:** The excerpting engine classifies an excerpt's topic as "تعريف المبتدأ" with 95% confidence. But it classifies the school attribution as "بصري" with only 60% confidence (because the text doesn't explicitly name the school — the engine inferred it from the definition style).

**This confidence signal must flow downstream as metadata (D-023):**
- Low-confidence excerpts should be flagged for human review at the taxonomy gate
- The synthesizer should weight high-confidence excerpts more heavily, or note uncertainty: "this excerpt is tentatively attributed to the Basran school based on definitional style"
- The scholar interface should distinguish "KR is confident about this" from "KR thinks this but isn't sure"
- Quality metrics should track confidence distributions: "80% of excerpts in this science are high-confidence" vs "only 40% are"

**Each engine should output a structured confidence object** alongside its primary output: what decision was made, what confidence level, and what evidence supports it. This is not optional instrumentation — it's a core metadata field that enables downstream quality control.

### التخريج (Takhrij — Hadith Source Tracing)

When a scholar cites a hadith in their work, they may cite it loosely ("the Prophet ﷺ said...") or precisely ("narrated by al-Bukhari and Muslim"). The tahqiq editor typically adds a footnote with the FULL reference: which hadith collections contain it, the book/chapter/number within each collection, and often a grading.

**This takhrij information is enormously valuable for synthesis:**
- It links a hadith citation to its original collection(s), enabling cross-source verification
- It carries grading information that affects how the synthesizer weighs evidence
- It reveals the evidence base: "the Hanafi position rests on a hadith found in Abu Dawud (graded hasan), while the Shafi'i position cites a hadith in Bukhari (sahih)"

**The excerpting engine must capture takhrij data** when it exists in the tahqiq footnotes. The source of this data is Layer 4 text (editor's notes), so the normalization engine must preserve it and the atomization engine must tag it correctly. The synthesizer consumes it to produce evidence-aware entries.

### Primary vs. Secondary Source Distinction

Not all sources in the library carry equal scholarly weight. The Islamic tradition distinguishes:

- **مصادر أصلية (primary sources)** — works where the author presents original scholarly content: their own analysis, their own positions, their own evidence evaluation. Example: الكتاب by سيبويه, المغني by ابن قدامة.
- **مراجع (reference works / secondary sources)** — works that primarily compile, organize, or summarize other scholars' work. Example: الموسوعة الفقهية (Fiqh Encyclopedia), الإنصاف by المرداوي (which catalogs Hanbali positions).
- **معاصر (modern compilations)** — contemporary works that explain classical content for modern readers. Useful for understanding but not primary scholarly evidence.

**The synthesizer must weight these differently.** A definition from سيبويه's الكتاب (primary, foundational) carries more scholarly weight than the same definition as paraphrased in a modern grammar textbook (secondary). The source metadata should classify each source's authority level. The synthesizer should cite primary sources directly and use secondary sources to confirm, contextualize, or fill gaps — not as primary evidence.


### The Owner's Voice in the Library

KR is a PERSONAL library (D-018). The owner is not just a consumer — he is a participant in the scholarly tradition. The system must support:

- **Owner tarjih:** When Rayane studies a topic and forms his own scholarly preference, that conclusion becomes part of the library (see Scenario 4 in USER_SCENARIOS.md). The owner's tarjih is stored at the relevant taxonomy leaf alongside the classical positions.
- **Owner notes:** Corrections, observations, and insights the owner adds during study. These are persistent — they survive entry regeneration and inform future synthesis.
- **Owner-originated content:** Study journal entries, research papers, and teaching materials the owner creates. These are knowledge products that belong in the library alongside extracted content.
- **Progressive expertise:** The library should reflect that the owner's understanding deepens over time. An early note might say "I don't understand this." A later note might say "Now I see why this position is stronger." Both are valuable. The timeline of the owner's scholarly development is itself a knowledge product.

---

## The Scholarly Landscape

### Scale of the Islamic Scholarly Corpus

The architect must understand the MAGNITUDE of what KR aims to process:

- **Number of extant works:** Estimated 500,000+ unique titles across all Islamic sciences. Many are multi-volume (المغني is 15 volumes, المبسوط is 30 volumes).
- **Digitally available:** ~40,000-50,000 works (Shamela alone has ~17,000). Growing rapidly.
- **Sciences:** 30+ recognized disciplines (see VISION §1.2), deeply interconnected.
- **Scholars:** Tens of thousands across 14 centuries. Major figures have 50+ works each.
- **Schools:** 4 Sunni madhahib in fiqh, 3+ major aqidah schools, 2 major grammar schools (Basra/Kufa), plus non-school-aligned scholars.
- **Time span:** From the 1st century AH (~7th century CE) to the present. 1400 years of continuous scholarly production.

This means: the source identity model must handle hundreds of thousands of entries. The taxonomy trees will have thousands of leaves per science. The scholar authority model will have tens of thousands of scholars. Design for scale from the start — what works for 10 books must work for 10,000.

### Major Digital Repositories

| Repository | Strengths | Weaknesses | Acquisition priority |
|---|---|---|---|
| **Shamela** (shamela.ws) | Largest Arabic text collection (~17K books). Structured data. | Text quality varies; many unverified prints. Old platform. | High — bulk acquisition |
| **Waqfeya** (waqfeya.net) | PDF scans of actual printed editions with tahqiq. | PDFs, not structured text. Harder to process. | High — quality editions |
| **al-Maktaba al-Shamila** (shamela.org) | Modern Shamela platform. | Overlap with shamela.ws. | Medium |
| **archive.org** | Massive. Rare manuscripts. Public domain. | Unstructured, OCR quality varies wildly. | Medium — rare sources |
| **King Saud University Digital Library** | Academic quality. Manuscripts. | Limited scope. | Low initially |
| **Qatar Digital Library** | Rare manuscripts with high-quality scans. | Limited API access. | Low initially |

### Physical Reference Preservation

Scholars cite by page, volume, and edition: "see المغني vol.3 p.245 (tahqiq al-Turki)." This is how the owner will verify KR's claims against physical books. If the pipeline strips page numbers, the owner cannot find the original text.

**Every excerpt must carry a physical citation:** the source title, author, edition (tahqiq + publisher), volume number, and page number(s). This citation is metadata that flows through the entire pipeline (D-023). The synthesizer uses it to generate proper academic citations in entries. The scholar interface uses it to tell the owner: "open your copy to volume 3, page 245."

The normalization engine must preserve page boundaries from the source. Shamela HTML usually includes page markers. PDFs have inherent pagination. iPhone photos are individual pages. The page number must survive normalization → passaging → excerpting as metadata, even though the text itself is de-paginated.

### The Traceability Boundary: Library vs. LLM Knowledge

The synthesizing engine uses three input sources (D-023): excerpts, metadata, and its own LLM research. This creates a critical distinction:

**Library-grounded claims** are statements traceable to specific excerpts from specific sources. "سيبويه defines المبتدأ as..." is grounded — it traces to excerpt X from source Y.

**LLM-contributed context** is information the synthesizer adds from its own training knowledge. "The Basran-Kufan rivalry was an institutional competition between the scholarly circles of Basra and Kufa..." is context the synthesizer provides to frame the library's excerpts.

**These must be CLEARLY DISTINGUISHED in the entry.** The factual layer (§6.4) must contain only library-grounded claims. LLM-contributed context belongs in the analytical layer or in clearly marked contextual sections. If the entry says "Scholar X held position Y," the reader (and the owner) must be able to determine: did the library tell us this (traceable to an excerpt), or did the synthesizer infer it from its training data?

This is not just about honesty — it's about reliability. LLM training data contains errors. Library excerpts, while they may have extraction errors that can be caught and corrected, come from actual scholarly texts. Mixing the two without marking the boundary means errors from either source are indistinguishable.

**The confidence hierarchy:** Library excerpt (high) > Library metadata enriched by LLM inference (medium) > Pure LLM research (lower). The entry's citations must make this hierarchy visible.

### Uncertainty Handling: When to Proceed vs. When to Stop

Not all uncertainty is equal. The architect must design engines with clear threshold rules:

**Always proceed (with flag):** Low-confidence school attribution, uncertain content type classification, ambiguous author reference that has a most-likely resolution. These produce flagged metadata that downstream engines and human reviewers can correct. Processing continues.

**Always stop (for human gate):** Potential text corruption detected, source trustworthiness uncertain (flag vs. verify), taxonomy evolution that would affect existing excerpts. These require owner input before proceeding. Content goes into a review queue.

**Context-dependent:** An unresolvable author ambiguity in a non-critical metadata field → proceed with "unknown." The same ambiguity in the primary author attribution → stop. The criticality of the decision determines whether to proceed or stop.

**The default is: proceed and flag, not stop and wait.** The owner should not be blocked from using the library because one excerpt has an uncertain school attribution. The system continues processing with the best-guess answer and a flag. The owner reviews flags at the human gate when convenient. Only irreversible decisions (taxonomy changes, source trustworthiness rulings) require stopping.

### What Doesn't Exist Yet (Opportunity for KR)

**Structural / interconnection gaps (owner's primary frustration):**
- **No topic interconnection** — topics are taught in isolation; no tool shows how topic A relates to topic B within the same science, or across sciences
- **No science-level structural map** — no way to see an entire science visualized: all topics, their correlations, prerequisite chains, foundational vs. derived concepts
- **No prerequisite tracking** — no tool tells you "before studying X, you need to understand Y and Z"
- **No narrative thread** — no "storyline" connecting topics within a chapter or science; why this topic follows the previous one

**Scholarly landscape gaps:**
- **No comparative school analysis** — existing tools show books from all schools but don't compare positions on the same topic
- **No per-topic significance** — no tool tells you whether a topic is central or peripheral, controversial or settled
- **No gap detection** — nobody can tell you "topic X has no Maliki source in your library"
- **No temporal evolution** — how a position changed over centuries is invisible

**Explanation quality gaps (owner's secondary frustration):**
- **No ground-up explanations** — existing texts make big logical jumps; no tool generates step-by-step, edge-case-covering, "explain like I'm 5" level clarity
- **No misconception mapping** — common misunderstandings aren't addressed
- **No theory mapping** — for a given topic, no tool gives you: core rule, evidence, positions, reasoning, edge cases, practical implications — all in one place

**Cross-source intelligence gaps:**
- **No tool cross-references between books** — if al-Ghazali cites al-Juwayni, no tool links them
- **No scholarly genealogy** — teacher→student chains exist in tabaqat books but aren't digitized as a network
- **No metadata quality scoring** — all editions treated equally regardless of tahqiq quality
- **No contradiction detection** — if a scholar says X in one book and Y in another, nobody flags it

These gaps are KR's reason for existing. Every one of them should be a designed capability in one or more engine SPECs.

---

## What Failure Looks Like

The architect must design validation for each engine. Understanding failure modes is essential:

**Source engine failure:** Misidentified author (attributed a work to the wrong scholar). Wrong genre classification (called a hashiyah a sharh). Duplicate not detected (two copies of the same tahqiq processed separately). Wrong work relationship (said Book A is a sharh of Book B when it's not). Every downstream engine inherits and amplifies these errors.

**Normalization failure:** Footnotes mixed into main text (editor's tahqiq notes treated as author's words). Structure discovery wrong (chapter boundary placed in the middle of a paragraph). OCR corruption (Arabic characters misread, especially ب/ت/ث/ن confusions). Diacritics stripped when they were semantically significant.

**Passaging failure:** Passage boundary splits a logical unit (half the definition in one passage, half in another). Passage too large (contains 5 unrelated topics). Passage too small (a single sentence fragment that can't be meaningfully extracted).

**Atomization failure:** Wrong atom type (classified a definition as an example). Missed atom boundary (two distinct scholarly positions merged into one atom). Isnad chain not detected (evidence chain treated as regular text).

**Excerpting failure:** NOT self-contained (excerpt references "the previous ruling" without including it). Wrong author attribution (quoted scholar attributed as the author's own position). Misclassified school. Missing metadata that makes the excerpt usable (no topic, no source reference). This is the most consequential failure — bad excerpts produce bad entries.

**Taxonomy failure:** Wrong leaf placement (excerpt about المبتدأ placed under الفاعل). Missing coverage gap detection (no flag when a school has zero representation at a leaf). Bad prerequisite chain (says topic A requires B when it doesn't, or misses a real prerequisite).

**Synthesizing failure:** Flat compilation instead of narrative (lists positions without context, dates, or intellectual genealogy). Wrong disagreement type (treats verbal disagreement as substantive). Misrepresents a position (scholar X actually held view A, not view B). Big logical jumps (assumes knowledge the reader doesn't have). Missing edge cases. **This is the ultimate failure — the entry is what the owner reads and learns from. A bad entry teaches wrong information.**

**Error propagation:** Errors cascade. A misidentified author in the source engine → wrong school attribution in excerpting → wrong school grouping in taxonomy → wrong comparative analysis in the entry. The further upstream the error, the more damage it causes and the harder it is to detect. This is why every engine must validate its output AND why the correction loop (Scenario 8) must propagate corrections back to the source of the error.

---

## Design Implications

When the architect designs any engine, these domain facts create concrete requirements:

**Source engine must:**
- **(Priority: get the identity model and metadata architecture right — these cascade to all downstream engines. Keep acquisition workflows minimal for v1.)**
- Distinguish works from sources: group sources by work, track edition provenance
- Track tahqiq quality, not just title/author
- Know which publishers are reliable
- Understand multi-volume works and edition variants
- Detect duplicate sources (same book, different tahqiq = NOT a duplicate; same tahqiq from two repositories = duplicate)
- Track work-to-work relationships (sharh→matn, mukhtasar→original, hashiyah→sharh) as a graph
- Maintain a scholar authority model: canonical identities, variant name mappings, disambiguation by death date and nisba
- Handle acquisition from ANY source type and repository, not just Shamela
- Handle manual acquisition paths as first-class citizens: (1) owner-provided scans/photographs of physical books that have no digital version, (2) owner-provided files manually downloaded from login-gated repositories. These are not edge cases — they are a primary acquisition method for sources that cannot be crawled.
- Capture enough metadata to power a **book briefing** (D-022): author biography/standing, work type and relationships, scope/level, edition quality, comparative edition data. Some of this is captured at intake; some is enriched later by downstream engines or the owner.
- **ACTIVELY infer metadata, not just record it.** Use LLM capabilities to infer metadata not explicitly stated in the source. Example: from a title page saying "شرح الآجرومية للكفراوي", infer: this is a شرح, the matn is الآجرومية by ابن آجروم (d. 723 AH), the science is nahw, the level is beginner, and الكفراوي's approximate period. Not all metadata comes from the source file — much comes from the engine's scholarly intelligence.
- **Support progressive enrichment.** When the 50th source mentioning a scholar is processed, update the scholar authority record with new information (a teacher, a work, a corrected date). Metadata is never final — it accumulates and self-corrects as the library grows.
- **Detect work relationships automatically.** When a source is identified as a sharh, record WHAT it comments on. When a source cites another work, create a relationship record. Over time, these build a citation and commentary graph across the entire library.

**Normalization engine must:**
- Preserve scholarly apparatus (footnotes, variant readings, hadith references)
- Handle Arabic-specific challenges: unvocalized text, hamza variants, taa marbuta
- Not destroy metadata during format conversion
- Handle two image-based source types: (1) iPhone camera photos of physical book pages (high quality, but variable lighting/angle), (2) professionally scanned PDFs (printer/flatbed scanned — many "digital" books online are this format). Arabic OCR pipeline needed for both.


**Passaging engine must:**
- Produce passage boundaries that respect the logical structure of Islamic scholarly texts: باب, فصل, مسألة, and paragraph-level divisions. A passage that splits a definition, a evidence chain, or a scholarly argument in half is defective — it forces the excerpting engine to either produce broken excerpts or violate the passage containment rule (§5.3).
- Use normalization metadata (division tree, heading hierarchy) to make informed boundary decisions. A heading like "فصل في أحكام المبتدأ" (chapter on rulings of the subject) is a strong boundary signal.

**Atomization engine must:**
- Recognize Islamic scholarly text patterns at the atom level: isnad chains (حدثنا فلان عن فلان), evidence markers (لقوله تعالى، لقول النبي ﷺ), opinion markers (وذهب الحنفية إلى), refutation patterns (ورُدّ بأن), example markers (نحو), and definitional statements (هو/هي + definition).
- Distinguish primary text from embedded quotations. In a sharh (commentary), "قال المصنف" introduces the matn author's words, not the commentator's. Atom type must reflect whose words these are.
- Feed the excerpting engine with enough type information to build contextually correct excerpts — the atom type IS metadata that flows to synthesis (D-023).


**Excerpting engine must:**
- Tag excerpts with evidence type (see "Evidence types" in Scholarly Methodology above: Quran, hadith, ijma, qiyas, companion statement, rational argument, istishab). An excerpt may contain multiple evidence types. This tagging feeds the synthesizer's ability to say "the Hanafi position rests on Quranic evidence and analogy, while the Shafi'i position relies on hadith."
- Detect and preserve isnad chains within excerpts — the إسناد is scholarly apparatus that proves the hadith's authenticity, not just text. It must be tagged as such so the synthesizer can distinguish "the narration" from "the chain that authenticates it."
- Detect when an author is citing, responding to, or disagreeing with another scholar — even when the other scholar is referenced indirectly ("قال بعض أصحابنا" = "some of our companions said" — this is a school-internal reference that should be flagged for resolution)
- Resolve implicit references when possible, flag when not (the scholar authority model helps: "الإمام" in a Shafi'i text usually means al-Shafi'i himself)
- Tag the excerpt's rhetorical function: is this a definition, a proof, a refutation, an exception, an example, a clarification, a condition? This shapes how the synthesizer uses it.

**Taxonomy engine must:**
- Handle cross-science placement (one excerpt relevant to multiple sciences)
- Track coverage per school per topic per science
- Enable a **visual map of an entire science**: every topic, how topics correlate, which are foundational vs. derived, what depends on what. The tree IS this map — its structure must make the science's internal logic visible.
- Track **prerequisite relationships** between topics: "understanding X requires first understanding Y." These are edges in the tree that aren't parent→child but rather dependency→dependent.
- Encode **narrative ordering** within each level of the tree: topics have a "storyline" — a logical sequence for study. This is not just alphabetical or arbitrary ordering. It's the pedagogical sequence: "after understanding المبتدأ, you study الخبر, then نواسخ المبتدأ والخبر." This ordering must be explicit in the tree structure so the synthesizer and scholar interface can present topics as a connected narrative, not isolated entries.
- Surface the **scholarly landscape per leaf**: which schools have positions here, how many sources cover this topic, what's the significance of this topic within the science

**Synthesizing engine must:**
- Generate comparative analysis across all schools (not madhhab-biased)
- Track temporal dimension (when was this position held, by whom, did it change?)
- Detect intra-author contradictions
- **Explain from the ground up.** Every entry must build the concept step by step — not dumbed down, but maximally clear. No big logical jumps. Explicit prerequisites stated. Edge cases and common misunderstandings addressed. The standard is: a reader who meets the prerequisites should be able to fully understand the topic from the entry alone.
- **"Explain like I'm 5" means maximum CLARITY, not simplification.** Don't remove complexity — make complexity navigable. A difficult concept should be explained so clearly that a reader says "now I understand why it's complex." Break compound ideas into atomic steps. Name each step. Show how each step connects to the next. This is what the best teachers do.
- **Situate every topic.** Each entry must explain WHERE this topic sits: what it connects to, why it matters, what comes before and after it in the science's logical structure. The "storyline" — the narrative thread connecting topics — must be visible.
- **Map the theory completely.** For each topic: the core rule/definition, the evidence, the different scholarly positions, the reasoning behind each position, the edge cases, and the practical implications. Nothing left implicit.
- **Use three input sources (D-023):** (1) excerpt content from placed excerpts — the primary textual evidence, (2) metadata chain from all upstream engines — author bios, dates, school affiliations, work genres, teacher-student chains, (3) LLM research capability — the synthesizer actively adds context, connections, and scholarly analysis that goes beyond what any individual source explicitly says (historical context, institutional dynamics, cross-source patterns). The metadata and LLM research are what transform a flat compilation into a scholarly narrative with temporal depth and intellectual genealogy. See `reference/ENTRY_EXAMPLE.md` for the difference.
- **Distinguish خلاف types** (see "Core Scholarly Methodology Concepts" above): verbal vs. substantive, respected vs. aberrant. Don't treat all disagreements equally.
- **تحرير المسألة first**: before presenting positions, precisely formulate what question each scholar is answering. If their questions differ, they don't disagree — they're addressing different مسائل.
- **Identify المعتمد (mu'tamad)** within each school when it exists. In fiqh entries, the mu'tamad position is the one the school officially adopts — it should be clearly distinguished from minority positions within the same school. Not all topics have a mu'tamad; where they do, the entry must say so.
- **Handle تراجع (scholar retraction).** When a scholar changed positions (e.g., الشافعي's قديم vs جديد), present the final position as primary. The earlier position is historical context, not a live alternative — unless a subsequent scholar adopted the earlier position independently.
- **Distinguish اجتهاد from تقليد** in how positions are weighted. A mujtahid's direct evidence-based conclusion has different scholarly character than a later muqallid's school-derived application.

**Scholar authority model (shared component — used by source, excerpting, taxonomy, synthesizing engines):**
- **Canonical scholar identities** — one record per historical scholar, with a stable canonical_id that all engines reference
- **Variant name mappings** — "ابن حجر" maps to TWO different scholars (al-Asqalani d.852 AH vs al-Haytami d.974 AH); context determines which. The model must handle this ambiguity.
- **Biographical data** — birth/death dates (hijri + miladi), locations, schools, teachers, students, major works, methodology
- **Teacher-student graph** — directed graph of who studied with whom. This is what enables the synthesizer to produce intellectual genealogy narratives (e.g., "Sibawayhi → al-Akhfash → al-Jarmi → al-Mubarrad → Ibn al-Sarraj" in the pipeline trace). Without this graph, the synthesizer can only list positions without showing how they're historically connected.
- **School affiliations** — per-science (a scholar can be Hanbali in fiqh and Ash'ari in aqidah and Basran in grammar)
- Initially seeded during source intake; grows automatically as more sources are processed and more scholars are encountered
- This is a SHARED knowledge graph, not per-source data. When the source engine identifies "ابن عقيل" as the author of شرح ابن عقيل, it links to the same canonical_id that the excerpting engine uses when it detects "قال ابن عقيل" in an excerpt from a different source.

**Correction and feedback loop (cross-cutting — all engines participate):**
When the owner identifies an error (see Scenario 8 in USER_SCENARIOS.md), corrections must flow through the system at the right level:
- **Entry-level:** owner flags error in a generated entry → entry regenerated with owner's note as a permanent constraint → note survives regeneration, preventing recurrence
- **Excerpt-level:** owner flags misattribution or misclassification → excerpt metadata corrected → all entries using that excerpt marked stale → entries regenerated
- **Taxonomy-level:** owner moves an excerpt to a different leaf → coverage metrics update → entries at both old and new leaves regenerated
- **Pattern-level:** if a correction reveals a SYSTEMATIC error (e.g., synthesizer consistently confuses subset/equivalence relationships), the correction becomes a RULE that applies to ALL future synthesis, not just the corrected entry
- Each correction is an investment — it improves not just one entry but the system's future behavior. Over years, these accumulated corrections make KR increasingly accurate.

**Scholar interface must:**
- Ground every answer in specific excerpts from specific sources — never generate unverified claims
- Handle all query types: single-school, comparative, evidence-chain, historical evolution
- Personalize based on user model: study history, knowledge gaps, current focus
- Teach through Socratic dialogue, not just information retrieval
- Be proactive: alert when new content matches study focus, detect gaps, suggest next steps
- Support scholarly production: writing assistance, footnote generation, research questions
- Generate a **book briefing** (D-022) for any source before the owner reads it: author profile, work classification, scope, reputation, edition quality, prerequisites, what to read next, comparative edition analysis. This is the primary pre-reading product.

**User model must:**
- Track engagement at the excerpt level (not just "viewed entry X")
- Distinguish between "has seen" and "has understood" (via Socratic assessment)
- Compute gaps across multiple dimensions: school, science, topic, time period
- Persist across sessions and grow more useful over time

---

## Scholarly Integrity Risks — Design Against These

These are errors that would undermine KR's scholarly credibility. Every engine design must actively prevent them.

**Library composition bias.** If the library has 30 Hanbali sources and 5 Maliki sources, the synthesizer might present Hanbali positions as dominant simply because they appear more often. This is a CORPUS BIAS, not a scholarly reality. The synthesizer must distinguish "this position appears in 12 sources in our library" from "this is the majority scholarly position." The synthesizer's LLM research capability (D-023) must fill gaps in library coverage when generating entries — noting when the library's representation of a school is thin.

**Modern-first bias.** Later scholars are more accessible (more digital editions, more commentary) but earlier scholars are often more foundational. If the library skews toward later works, entries might overrepresent late-period refinements and underrepresent the foundational positions they refined. The temporal dimension in metadata (author death dates) helps: the synthesizer should ensure entries cover the earliest known position on a topic, not just the most recent.

**Editor-author conflation.** Tahqiq editions have editor footnotes, variant readings, and commentary that are NOT the original author's words. If the normalization engine fails to separate editor additions from primary text, the excerpting engine will attribute the editor's analysis to the original author. This is a scholarly integrity violation — it literally puts words in a scholar's mouth. The normalization engine's structure discovery must identify and tag editorial apparatus.

**Abrogation blindness.** Presenting an abrogated ruling as current is dangerous, especially in fiqh. The synthesizer must track ناسخ ومنسوخ (abrogation) and clearly mark abrogated content. This requires either metadata tagging at the excerpt level or synthesizer-level awareness of known abrogation instances.

**Consensus misrepresentation.** Presenting a consensus (إجماع) topic as if it has live scholarly disagreement undermines the scholarly tradition. Conversely, claiming consensus when legitimate disagreement exists suppresses valid positions. The synthesizer must be careful with إجماع claims — they should be sourced and qualified ("consensus according to the four Sunni schools" vs. "including all schools").

**Decontextualized quotation.** Extracting a scholar's statement from a context where they're presenting an opponent's view (for the purpose of refuting it) and attributing it as the scholar's own position. This is a common error in superficial scholarship. The excerpting engine must capture enough context to distinguish "Scholar A says X" from "Scholar A reports that Scholar B says X, but Scholar A disagrees."

**Level conflation.** Mixing beginner-level explanations (simplified, sometimes imprecise) with specialist-level precision without marking the level. متن الآجرومية deliberately simplifies grammatical definitions for beginners — citing it alongside سيبويه's الكتاب as if they make equally precise claims is misleading. The metadata (work level) enables the synthesizer to flag when a simplified source is being used for precise definition.

**Hadith grading ignorance.** Using a weak (ضعيف) hadith as primary evidence for a ruling without noting its weakness, or failing to mention that scholars disagree on a hadith's authenticity. The metadata should carry hadith grading; the synthesizer must incorporate it.

**Silent majority.** Many scholarly positions are held by the overwhelming majority but rarely stated explicitly — because everyone agreed and there was nothing to debate. If the library only captures EXPLICIT position statements, it misses the silent consensus. The synthesizer's research capability must identify when a position is implicitly held by default.

**Retraction blindness.** Presenting a scholar's early position as current when they later retracted it. الشافعي's "old" positions (القول القديم) are explicitly superseded by his "new" positions (القول الجديد) after moving to Egypt. The source engine must track composition dates; the synthesizer must check for known retractions before citing a position.

**Mu'tamad misidentification.** Within a madhhab, incorrectly identifying which position is the mu'tamad (relied-upon). In Hanbali fiqh, the mu'tamad on many issues shifted between early period (Ahmad's direct statements) and later codification (المرداوي's الإنصاف). Presenting a non-mu'tamad position as if it's the school's official stance is misleading. The synthesizer must cross-check its mu'tamad identification against known authoritative reference works for each school.

**Layer misattribution.** In a multi-layer text (matn/sharh/hashiyah), attributing Layer 1 text to the Layer 2 author (or vice versa). If a sharh contains "قال المصنف: المبتدأ اسم ابتداء" — those are the MATN author's words, not the sharh author's. Misattributing them means putting words in the wrong scholar's mouth, across the wrong century. The normalization and atomization engines must correctly identify layers; the excerpting engine must attribute to the layer's author, not the source's author.

**Verse destruction.** Processing a versified text (نظم) with prose-oriented rules destroys the verse structure. A بيت split across two passages, or two hemistichs merged into a single atom, loses the verse numbering that scholars use for reference ("ألفية line 75") and breaks the self-contained unit structure. The passaging and atomization engines must detect verse structure and handle it differently.

**Confidence laundering.** Presenting a low-confidence extraction decision as established fact because the confidence signal was dropped somewhere in the pipeline. If the excerpting engine is only 60% sure about a school attribution, but the confidence signal doesn't flow to the synthesizer, the entry will state the attribution with the same confidence as a 99% one. Every engine must propagate confidence scores (D-023).

**Intra-source contradiction blindness.** A scholar may say one thing on page 50 and something slightly different on page 300 of the same book. This is common — scholars sometimes refine their views within a work, or address a topic differently in different contexts. The excerpting engine will capture both statements as separate excerpts. The synthesizer must detect when two excerpts from the SAME author appear to contradict and handle this: perhaps the later statement supersedes the earlier, or the apparent contradiction resolves when context is considered. Presenting both without noting the tension is misleading.

These risks are not theoretical — they are the EXACT errors that existing Islamic studies tools and LLMs routinely make. KR's value proposition is that it DOESN'T make them.
