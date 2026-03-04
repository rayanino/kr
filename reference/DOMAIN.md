# Domain Primer — خزانة ريان

This document gives the architect domain grounding for design decisions. Read it before starting any new engine SPEC. It grows over time as the owner provides more domain knowledge.

---

## The User

**Name:** Rayane
**Location:** Belgium (Leuven)
**Background:** Islamic studies student, non-technical. The application is built entirely for him.
**Primary madhhab:** None — studies all schools equally.
**School coverage mandate:** Equal coverage of all four Sunni madhahib plus non-madhhab scholars (Ibn Hazm, Zahiri school, contemporary salafi scholars, etc.). No school is primary or secondary. The application must never assume a default madhhab.
**Languages:** Arabic (reading scholarly texts), Dutch, French, English. The application's scholarly content is Arabic; the interface and generated analysis may use any of the owner's languages.

**Interaction model:** Living scholarly partner. Not a passive library — the application should be proactive: suggest what to study, challenge understanding, detect gaps, alert when new sources arrive. It should feel like having a tireless, infinitely knowledgeable study companion.

### Study Profile

- **Sciences currently studying:** None yet. The application IS the enabler — Rayane is waiting for KR to begin his scholarly journey. First sciences once KR is operational: Arabic language sciences (Nahw, Sarf, Balagha). Other sciences follow once the Arabic foundation is solid.
- **What "highest level of scholarship" means:** The complete scholar — encyclopedic knowledge across all schools AND original scholarly production (tarjih, tahrir, research) AND teaching mastery (ability to explain and transmit). All three, not a choice between them.
- **Study method:** Primarily self-directed but wants structured guidance from KR. No current teacher/shaykh. **KR must fill the role of both the library and the guide.** This is not optional — without structured guidance from the application, there is no structure at all.
- **Current daily study workflow:** None yet — pending KR. **[PENDING: revisit once KR is in use to refine the interaction model]**
- **Frustrations with Shamela and existing digital tools:** **[PENDING — owner to fill]**
- **What information about a book matters before starting to read it:** **[PENDING — owner to fill]**
- **Sources known to exist but not accessible digitally:** **[PENDING — owner to fill]**

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

**Minimum viable metadata (every source):**
- Title (Arabic + transliterated)
- Author (full name, nisba, birth/death dates hijri + miladi)
- Science classification (may be multiple: a book on usul al-fiqh also touches mantiq)
- Source format (Shamela, PDF, EPUB, manuscript scan, etc.)
- Acquisition date and provenance (where did the digital file come from?)

**Scholarly metadata (when available):**
- Tahqiq editor(s) and their credentials
- Publisher, city, edition number, print year
- Manuscript base (which manuscripts, their library identifiers)
- Volume/part structure (many works are multi-volume; some have different numberings across editions)
- Original composition date (hijri) and context (why the author wrote it)
- The work's genre: sharh (commentary), mukhtasar (abridgment), hashiyah (marginal note), matn (core text), nazm (versified), risalah (treatise)
- Relationships to other works: "this is a sharh of [other book]", "this is a mukhtasar of [other book]"

**Library tracking metadata:**
- Ingestion status (acquired, normalized, passaged, excerpted, placed)
- Completeness (full text or partial? which volumes?)
- Known text quality issues (OCR errors, missing pages, corrupted sections)
- Alternative editions available (and which is preferred)
- Cross-references to other sources in the library (the citation network)

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

- **No tool cross-references between books** — if al-Ghazali cites al-Juwayni, no tool links them
- **No comparative school analysis** — existing tools show books from all schools but don't compare positions
- **No gap detection** — nobody can tell you "topic X has no Maliki source in your library"
- **No scholarly genealogy** — teacher→student chains exist in tabaqat books but aren't digitized as a network
- **No metadata quality scoring** — all editions treated equally regardless of tahqiq quality
- **No contradiction detection** — if a scholar says X in one book and Y in another, nobody flags it
- **No temporal evolution** — how a position changed over centuries is invisible

These gaps are KR's competitive advantage. Every one of them should be a designed capability in one or more engine SPECs.

---

## Design Implications

When the architect designs any engine, these domain facts create concrete requirements:

**Source engine must:**
- Track tahqiq quality, not just title/author
- Know which publishers are reliable
- Understand multi-volume works and edition variants
- Detect duplicate sources (same book, different tahqiq = NOT a duplicate)
- Track book-to-book relationships (sharh→matn, mukhtasar→original)

**Normalization engine must:**
- Preserve scholarly apparatus (footnotes, variant readings, hadith references)
- Handle Arabic-specific challenges: unvocalized text, hamza variants, taa marbuta
- Not destroy metadata during format conversion

**Excerpting engine must:**
- Tag excerpts with evidence type (Quran, hadith, scholarly reasoning, ijma)
- Detect and preserve isnad chains within excerpts
- Resolve implicit references when possible, flag when not

**Taxonomy engine must:**
- Handle cross-science placement (one excerpt relevant to multiple sciences)
- Track coverage per school per topic per science

**Synthesizing engine must:**
- Generate comparative analysis across all schools (not madhhab-biased)
- Track temporal dimension (when was this position held, by whom, did it change?)
- Detect intra-author contradictions

**Scholar interface must:**
- Ground every answer in specific excerpts from specific sources — never generate unverified claims
- Handle all query types: single-school, comparative, evidence-chain, historical evolution
- Personalize based on user model: study history, knowledge gaps, current focus
- Teach through Socratic dialogue, not just information retrieval
- Be proactive: alert when new content matches study focus, detect gaps, suggest next steps
- Support scholarly production: writing assistance, footnote generation, research questions

**User model must:**
- Track engagement at the excerpt level (not just "viewed entry X")
- Distinguish between "has seen" and "has understood" (via Socratic assessment)
- Compute gaps across multiple dimensions: school, science, topic, time period
- Persist across sessions and grow more useful over time
