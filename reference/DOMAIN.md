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

### Critical Design Implication

**Pipeline priority: the critical path starts AFTER a source is received.** The source acquisition phase (autonomous discovery, adding new source types, expanding file format support) can be expanded later. The most important work — what makes KR transformative — begins when a source enters the pipeline: normalization, passaging, atomization, excerpting, taxonomy placement, and synthesis. The source engine's first version should provide a minimum viable acquisition path that gets sources INTO the pipeline quickly. Don't over-engineer sourcing at the expense of the downstream engines that create the actual knowledge products.

### Critical Design Implication

KR is not supplementing an existing study practice. It IS the study practice. This means:

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

These categories map to the book briefing (D-022). Some are captured at source intake, some enriched later by downstream engines or the owner.

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

**Edition-specific metadata (per source, not per work):**
- Trustworthiness assessment: is this specific print/edition credible and uncorrupted?
- Comparison to other editions: how does this edition differ content-wise from other known prints?
- Preferred edition status: is this the owner's preferred edition for this work?

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

---

## The Scholarly Landscape

### Major Digital Repositories

| Repository | Strengths | Weaknesses | Acquisition priority |
|---|---|---|---|
| **Shamela** (shamela.ws) | Largest Arabic text collection (~17K books). Structured data. | Text quality varies; many unverified prints. Old platform. | High — bulk acquisition |
| **Waqfeya** (waqfeya.net) | PDF scans of actual printed editions with tahqiq. | PDFs, not structured text. Harder to process. | High — quality editions |
| **al-Maktaba al-Shamila** (shamela.org) | Modern Shamela platform. | Overlap with shamela.ws. | Medium |
| **archive.org** | Massive. Rare manuscripts. Public domain. | Unstructured, OCR quality varies wildly. | Medium — rare sources |
| **King Saud University Digital Library** | Academic quality. Manuscripts. | Limited scope. | Low initially |
| **Qatar Digital Library** | Rare manuscripts with high-quality scans. | Limited API access. | Low initially |

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

**Normalization engine must:**
- Preserve scholarly apparatus (footnotes, variant readings, hadith references)
- Handle Arabic-specific challenges: unvocalized text, hamza variants, taa marbuta
- Not destroy metadata during format conversion
- Handle two image-based source types: (1) iPhone camera photos of physical book pages (high quality, but variable lighting/angle), (2) professionally scanned PDFs (printer/flatbed scanned — many "digital" books online are this format). Arabic OCR pipeline needed for both.

**Excerpting engine must:**
- Tag excerpts with evidence type (Quran, hadith, scholarly reasoning, ijma)
- Detect and preserve isnad chains within excerpts
- Resolve implicit references when possible, flag when not

**Taxonomy engine must:**
- Handle cross-science placement (one excerpt relevant to multiple sciences)
- Track coverage per school per topic per science
- Enable a **visual map of an entire science**: every topic, how topics correlate, which are foundational vs. derived, what depends on what. The tree IS this map — its structure must make the science's internal logic visible.
- Track **prerequisite relationships** between topics: "understanding X requires first understanding Y." These are edges in the tree that aren't parent→child but rather dependency→dependent.
- Surface the **scholarly landscape per leaf**: which schools have positions here, how many sources cover this topic, what's the significance of this topic within the science

**Synthesizing engine must:**
- Generate comparative analysis across all schools (not madhhab-biased)
- Track temporal dimension (when was this position held, by whom, did it change?)
- Detect intra-author contradictions
- **Explain from the ground up.** Every entry must build the concept step by step — not dumbed down, but maximally clear. No big logical jumps. Explicit prerequisites stated. Edge cases and common misunderstandings addressed. The standard is: a reader who meets the prerequisites should be able to fully understand the topic from the entry alone.
- **Situate every topic.** Each entry must explain WHERE this topic sits: what it connects to, why it matters, what comes before and after it in the science's logical structure. The "storyline" — the narrative thread connecting topics — must be visible.
- **Map the theory completely.** For each topic: the core rule/definition, the evidence, the different scholarly positions, the reasoning behind each position, the edge cases, and the practical implications. Nothing left implicit.

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
