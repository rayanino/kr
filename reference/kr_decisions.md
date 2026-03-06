# KR Architectural Decisions

## Decision Format
Each decision records: what was decided, why, what alternatives were considered,
which session made it, and what documents were updated as a result.

Decisions are append-only. To supersede a decision, add a new one referencing the old.

**When adding a new decision, also add a one-line entry to the table of contents below.**

## Table of Contents

| # | Title | Date |
|---|-------|------|
| D-001 | Seven engines are conceptual responsibilities | 2026-02-28 |
| D-002 | AI-first documentation | 2026-02-28 |
| D-003 | The no-inference rule | 2026-02-28 |
| D-004 | Primary text integrity is absolute | 2026-03-01 |
| D-005 | Entries are the primary knowledge product | 2026-02-28 |
| D-006 | Priority ordering — Accuracy > Protection > Intelligence | 2026-02-28 |
| D-007 | Content type is metadata, not a tree branching factor | 2026-02-28 |
| D-008 | School is the primary within-leaf organizer | 2026-02-28 |
| D-009 | Three-outcome split model for cross-topic content | 2026-02-28 |
| D-010 | Application name — خزانة ريان (Khizanat Rayan, abbreviated KR) | 2026-02-28 |
| D-011 | Passage containment rule | 2026-02-28 |
| D-012 | Documentation hierarchy | 2026-02-28 |
| D-013 | SPEC-first workflow | 2026-03-04 |
| D-014 | Authority model for Claude Chat sessions | 2026-03-04 |
| D-015 | Engine SPEC sovereignty | 2026-03-04 |
| D-016 | Scholar Interface — user-facing intelligence layer | 2026-03-04 |
| D-017 | User Model — persistent user state as shared component | 2026-03-04 |
| D-018 | Core Identity — KR is Rayane's knowledge, not a library he uses | 2026-03-04 |
| D-019 | ABD legacy code has zero design authority | 2026-03-04 |
| D-020 | Pipeline priority — critical path starts after source reception | 2026-03-04 |
| D-021 | Owner's core frustration — lack of interconnection and poor explanations | 2026-03-04 |
| D-022 | Book briefing — what the owner needs before reading any source | 2026-03-04 |
| D-023 | Metadata is synthesis fuel, not just source documentation | 2026-03-04 |
| D-024 | Three-tier source identity model (source, work, scholar) | 2026-03-04 |
| D-025 | Source engine as primary creator of scholar authority records | 2026-03-04 |
| D-026 | Text fidelity separate from scholarly trustworthiness | 2026-03-04 |
| D-027 | Work relationship graph with placeholder records for unacquired works | 2026-03-04 |
| D-028 | OCR strategy — Mistral OCR 3 primary, Qari-OCR for diacritics | 2026-03-05 |
| D-029 | Normalized package schema — source_id reference model | 2026-03-05 |
| D-030 | Multi-layer detection — conservative default to commentary author | 2026-03-05 |
| D-031 | Universal footnote reference marker format | 2026-03-05 |
| D-032 | Synthesized entries must be in Arabic | 2026-03-05 |
| D-033 | Secure by design — error prevention over error correction | 2026-03-05 |
| D-036 | Multi-model consensus for excerpting | 2026-03-05 |
| D-037 | Three-phase excerpting pipeline | 2026-03-05 |
| D-034 | Two-tier atom type system (structural type + scholarly function) | 2026-03-05 |
| D-038 | Two-stage placement algorithm with three candidate sources | 2026-03-05 |
| D-039 | Limited multi-model consensus for taxonomy (placement only, ambiguous range) | 2026-03-05 |
| D-040 | Analytical layer boundary — structured traceability via grounding_type | 2026-03-05 |
| D-041 | Consensus technology stack — LiteLLM + Instructor with parallel independent comparison | 2026-03-06 |

---

### D-001: Seven engines are conceptual responsibilities
**Decided:** 2026-02-28
**Context:** The seven engines (source, normalization, passaging, atomization, excerpting, taxonomy, synthesizing) need a relationship to code organization
**Decision:** Engines are conceptual processing responsibilities, not code organization mandates. Engine directories exist, but logic may span files or share files with adjacent engines.
**Alternatives considered:** Strict 1:1 engine-to-directory mapping → rejected (too rigid, forces artificial separation)
**Documents updated:** VISION.md §7, CLAUDE.md

### D-002: AI-first documentation
**Decided:** 2026-02-28
**Context:** Documentation needs a defined primary audience
**Decision:** Primary readers are AI agents. Documentation optimized for unambiguous machine interpretation. Human readability valued but never at cost of machine precision.
**Documents updated:** VISION.md §0 (Documentation Contract)

### D-003: The no-inference rule
**Decided:** 2026-02-28
**Context:** Implementers need guidance when documentation is silent
**Decision:** Silence is never permission. When documentation is silent or ambiguous, implementers stop, surface the gap, and resolve it in documentation before proceeding.
**Documents updated:** VISION.md §0 (Documentation Contract)

### D-004: Primary text integrity is absolute
**Decided:** 2026-03-01
**Context:** What to do when primary text (the original Arabic source text) is corrupted
**Decision:** No correction workflow exists for corrupted primary text. Corrupted text is handled via new source acquisition or manual input (Option B).
**Alternatives considered:** (A) Build a correction workflow with human verification → rejected (too much complexity, too much risk of silent corruption)
**Documents updated:** VISION.md

### D-005: Entries are the primary knowledge product
**Decided:** 2026-02-28
**Context:** Relationship between excerpts and entries needed clarification
**Decision:** Entries (LLM-generated synthesis at leaf nodes) are the primary knowledge product. Excerpts are intermediate artifacts that feed entry generation.
**Documents updated:** VISION.md §6

### D-006: Priority ordering — Accuracy > Protection > Intelligence
**Decided:** 2026-02-28
**Context:** The three core properties sometimes conflict
**Decision:** When they conflict: accuracy (correct information) takes precedence over protection (validation layers) which takes precedence over intelligence (LLM capabilities).
**Documents updated:** VISION.md §1.4, §11

### D-007: Content type is metadata, not a tree branching factor
**Decided:** 2026-02-28
**Context:** Whether content type (e.g., definition, ruling, evidence) should create separate tree branches
**Decision:** Content type is metadata on excerpts, not a structural element of science trees.
**Documents updated:** VISION.md §2, §4

### D-008: School is the primary within-leaf organizer
**Decided:** 2026-02-28
**Context:** How to organize content within a leaf node
**Decision:** School (مذهب) is the primary organizer within leaves. Each school gets its own entry at a leaf. "Scholarly position" is the broader concept.
**Documents updated:** VISION.md §4.6

### D-009: Three-outcome split model for cross-topic content
**Decided:** 2026-02-28
**Context:** How to handle passages that span multiple topics
**Decision:** Three possible outcomes: (a) excerpt placed at the more specific topic, (b) excerpt split into multiple excerpts, (c) excerpt placed at the parent node. Decision made per-case by the excerpting engine.
**Documents updated:** VISION.md §5.3

### D-010: Application name — خزانة ريان (Khizanat Rayan, abbreviated KR)
**Decided:** 2026-02-28
**Context:** Expanding from Arabic Book Digester to broader scope needed a new name
**Decision:** خزانة ريان — "Rayan's Treasury/Library." Code abbreviation: KR.
**Alternatives considered:** Several Arabic alternatives → KR chosen for classical scholarly resonance
**Documents updated:** All documents

### D-011: Passage containment rule
**Decided:** 2026-02-28
**Context:** Whether excerpts can span passage boundaries
**Decision:** Excerpts cannot span passage boundaries. An excerpt's source text must come from within a single passage.
**Documents updated:** VISION.md §5

### D-012: Documentation hierarchy
**Decided:** 2026-02-28
**Context:** Need clear authority levels for different document types
**Decision:** Level 0 (VISION.md) → Level 2 (SPEC.md per engine) → Level 3 (SCIENCE.md per science). VISION defines what/why, SPEC defines how, SCIENCE defines science-specific application.
**Documents updated:** VISION.md §13

### D-013: SPEC-first workflow
**Decided:** 2026-03-04
**Context:** Whether to audit VISION first then write SPECs, or write SPECs first then correct VISION
**Decision:** SPECs first. Deep engine understanding from SPEC writing flows back up to correct VISION passages. VISION sections have clear engine ownership.
**Alternatives considered:** VISION-first approach → rejected (can't write accurate overview without detailed understanding)
**Documents updated:** kr_definitive_roadmap_v2.md

### D-014: Authority model for Claude Chat sessions
**Decided:** 2026-03-04
**Context:** Need clear division of decision-making between Claude and the owner
**Decision:** Claude makes ALL technical/architectural decisions autonomously. Owner provides domain/usage input only. Escalation test: "Does this decision change what the end user sees?" If yes → ask owner. If no → Claude decides.
**Documents updated:** reference/DEEP_REASONING_PROTOCOL.md

### D-015: Engine SPEC sovereignty
**Decided:** 2026-03-04
**Context:** Authority relationship between VISION.md and engine SPECs
**Decision:** Within an engine's scope, its SPEC is the most authoritative document. VISION.md governs only cross-cutting rules (glossary, documentation contract, engine boundaries). The SPEC is the densest, most precise documentation and is the sole governing entity for its engine.
**Documents updated:** reference/DEEP_REASONING_PROTOCOL.md

### D-016: Scholar Interface — user-facing intelligence layer
**Decided:** 2026-03-04
**Context:** The 7 processing engines build the library but VISION.md has no concept for how the user actually interacts with it. The owner's mandate is a "living scholarly partner" — proactive, teaching, challenging, discovering. This requires a dedicated component.
**Decision:** Create `interface/scholar/` as a new top-level component (not an engine, not shared infrastructure). It sits on top of all engine outputs and provides five capability domains: Answering (Q&A grounded in library knowledge), Teaching (Socratic dialogue, study paths, spaced repetition, gap detection), Discovering (proactive alerts, contradiction detection, coverage gaps, scholarly briefings), Assisting (writing support, footnote generation, research questions), Navigating (taxonomy browsing, scholar networks, temporal views, coverage maps). Gets its own SPEC following the standard template.
**Alternatives considered:** (a) Adding interaction features to the synthesizing engine → rejected (the synthesizing engine produces entries; the interface consumes them — different responsibilities). (b) Multiple separate components (Scholar, Sentinel, Navigator, Scribe) → rejected (they all share the same knowledge products and user model; splitting them would fragment context). (c) Deferring entirely to "later" → rejected (if the architect doesn't design for user interaction now, the engines will be optimized for data processing rather than scholarly experience).
**Documents updated:** CLAUDE.md (repo map + pipeline), interface/scholar/CLAUDE.md created, shared/user_model/CLAUDE.md created.

### D-017: User Model — persistent user state as shared component
**Decided:** 2026-03-04
**Context:** The scholar interface needs to personalize every interaction based on what the user has studied, knows, and needs. This state is also useful to processing engines (e.g., alerting when new excerpts match the user's focus). It belongs in shared/ because multiple components read and write it.
**Decision:** Create `shared/user_model/` as a shared component. Tracks: study history, demonstrated knowledge, knowledge gaps, current focus, preferences, bookmarks/annotations. Read by scholar interface for personalization. Written to by scholar interface (interactions) and processing engines (new content alerts). Gets its own SPEC.
**Alternatives considered:** (a) Embedding user state in the scholar interface → rejected (processing engines also need to write to it). (b) Using external tool (mem0) as sole user model → rejected (user model must be KR-native with well-defined schema; external tools may supplement but not replace).
**Documents updated:** CLAUDE.md (repo map), shared/user_model/CLAUDE.md created.

### D-018: Core Identity — KR is Rayane's knowledge, not a library he uses
**Decided:** 2026-03-04
**Context:** The owner clarified that KR is not a tool alongside his studies — it IS the representation of his knowledge. The library's contents are what he knows; gaps are what he doesn't know; errors are errors in his understanding.
**Decision:** This is the foundational architectural principle. All design decisions must serve it. Specific consequences: (1) Quality is existential — every knowledge product must meet publishable scholarship standards because errors corrupt the user's understanding. (2) Completeness is meaningful — gaps are personal. (3) The library grows with the user. (4) Rayane's own scholarly output (tarjih, notes, research) feeds back into the library as first-class content alongside classical sources. (5) Encyclopedic completeness is the endgame.
**Alternatives considered:** Treating KR as a research tool with library-quality aspirations → rejected (undersells the application's identity and leads to designs that treat quality as a nice-to-have rather than existential).
**Documents updated:** DOMAIN.md (new "Core Identity" section), PROJECT_INSTRUCTIONS.md (design philosophy + scholarly integrity self-review), interface/scholar/CLAUDE.md (quality mandate, feedback loop), DEEP_REASONING_PROTOCOL.md (Criterion #21: Scholarly Integrity).

### D-019: ABD legacy code has zero design authority
**Decided:** 2026-03-04
**Context:** The ABD (Arabic Book Digester) codebase was migrated to the KR repo. ABD was built for a narrow purpose (processing Shamela HTML exports into excerpts) before KR was conceived. Its code works but its design decisions, scope limitations (Shamela-only), field names, architecture choices, and assumptions carry no authority in KR.
**Decision:** ABD-era code, reference docs, schemas, and decisions are treated as LEGACY — useful as implementation hints for what currently exists, but never as design constraints for what KR should be. Specifically: (1) No ABD decision is binding in KR. Any ABD-era choice can be overridden without justification. (2) KR is not limited to Shamela or any single source format. The source engine must design for ALL scholarly source types from the start. (3) ABD reference docs (ABD_INTAKE_SPEC.md, ABD_EXCERPTING_SPEC.md, etc.) describe what WAS built, not what SHOULD be built. (4) Field names, schema structures, and architectural patterns from ABD may be adopted if they're the best choice for KR, but "that's how ABD did it" is never a justification.
**Alternatives considered:** Treating ABD decisions as defaults that need explicit override → rejected (creates anchoring bias; the architect should design from first principles, not from ABD's starting point).
**Documents updated:** All engine CLAUDE.md files, PROJECT_INSTRUCTIONS.md, NEXT.md, DOMAIN.md, STATUS.md, DEEP_REASONING_PROTOCOL.md.

### D-020: Pipeline priority — critical path starts after source reception
**Decided:** 2026-03-04
**Context:** Owner clarified that the source acquisition phase (autonomous discovery, multiple file types, login-gated sources) can be expanded later. The most critical work starts when a source enters the pipeline: normalization → passaging → atomization → excerpting → taxonomy placement → synthesis. The downstream engines are what make KR transformative.
**Decision:** The source engine SPEC should define the complete source identity model and metadata architecture (these affect all downstream engines) but keep acquisition workflows minimal for v1. First version: accept files the owner provides (Shamela exports, PDFs, iPhone camera photos) + collect metadata. Autonomous discovery, multi-repository crawling, and expanded format support are documented as future capabilities (§4.B or marked [NOT YET IMPLEMENTED]) but not the design focus.
**Documents updated:** NEXT.md, DOMAIN.md.

### D-021: Owner's core frustration — lack of interconnection and poor explanations
**Decided:** 2026-03-04
**Context:** Owner identified the fundamental problems with existing Islamic scholarly tools and teaching: (1) topics explained in isolation without interconnection, no "storyline," no structural overview of a science; (2) no per-topic scholarly landscape (significance, opinions, schools); (3) poor explanations with big logical jumps, no ground-up building, no edge cases addressed, no prerequisite mapping.
**Decision:** These frustrations define the success criteria for two engines: the **taxonomy engine** must make a science's internal logic visible (topic correlation map, prerequisite dependencies, per-leaf scholarly landscape), and the **synthesizing engine** must generate entries that explain from the ground up (step-by-step, no jumps, edge cases covered, prerequisites explicit, theory mapped completely, topic situated in context). The bar is: every entry reads like the best teacher you've ever had explaining the topic.
**Documents updated:** DOMAIN.md (frustrations, taxonomy implications, synthesizing implications).

### D-022: Book briefing — what the owner needs before reading any source
**Decided:** 2026-03-04
**Context:** Owner listed everything they want to know before starting to read a book. This is not just metadata — it's the scholar interface's primary pre-reading product, assembled from source metadata + library knowledge + generated analysis.
**Decision:** The system must be able to produce a **book briefing** for any source in the library, covering: (1) author profile (biography, standing, madhhab, teachers/students, time period, other works), (2) work classification (type, science, relationship to other works), (3) scope (topics covered/not covered, theory vs practice, level), (4) physical details (pages, volumes, completeness), (5) reputation (scholarly standing, citation frequency, mu'tamad status), (6) this edition's quality (tahqiq, publisher, trustworthiness, corruption assessment), (7) study context (prerequisites, what to read next, position in learning progression), (8) comparative (how other editions differ content-wise, which is best). This requires: source engine metadata (items 1-6), taxonomy engine knowledge (item 3 scope, item 7 prerequisites), cross-source analysis (item 8), and synthesizing engine generation (assembling it all into a coherent briefing). The book briefing is a key scholar interface deliverable.
**Documents updated:** DOMAIN.md.

### D-023: Metadata is synthesis fuel, not just source documentation
**Decided:** 2026-03-04
**Context:** Owner clarified that "what I want to know about a book" (D-022) is not the same as "what the system needs as metadata." Metadata serves a deeper purpose: it is a PRIMARY INPUT to the synthesizing engine alongside excerpt content. The synthesizer doesn't just compile what excerpts say — it weaves in author biography, time period, school affiliation, work genre, teacher-student chains, historical context, and its own broad research to produce entries with scholarly depth that no single source contains. Example: an entry about الفاعل doesn't just list definitions — it contextualizes them: "Sibawayhi (d. 180 AH, Basran) defined it in al-Kitab, the earliest systematic grammar. 136 years later, Ibn al-Sarraj refined it in al-Usul after the Basran-Kufan debate had crystallized."
**Decision:** Every engine that captures or enriches metadata must design its metadata model with the synthesizer as the primary consumer. The question is not "what do we know about this source?" but "what does the synthesizer need to produce an entry with full scholarly depth?" This includes: (1) author biographical context (dates, school, teachers, students, methodology, other works), (2) work contextual data (genre, why written, relationship to other works, period), (3) historical context (what scholarly debates were active, what school dynamics existed), (4) cross-source intelligence (who cites whom, who disagrees with whom, intellectual genealogy). The synthesizer also does its own research beyond what's in the library — it adds context, connections, and analysis that no single source contains.
**Architectural consequence:** Metadata flows DOWNSTREAM through the pipeline to the synthesizer, not just UPWARD to the scholar interface. Source metadata → normalized package → passage metadata → excerpt metadata → placed excerpt metadata → ALL available to the synthesizer when generating an entry. No engine should strip or lose metadata that the synthesizer could use.
**Documents updated:** DOMAIN.md, DEEP_REASONING_PROTOCOL.md, PROJECT_INSTRUCTIONS.md.

### D-024: Three-tier source identity model (source, work, scholar)
**Decided:** 2026-03-04
**Context:** The ABD-era code uses `book_id` (owner-assigned ASCII slug) as the sole identifier. KR needs to distinguish between: a specific acquired file (source), the abstract intellectual work (work), and the scholar who created it (scholar). These three tiers serve different purposes — source_id for file integrity and deduplication, work_id for grouping editions and tracking relationships, canonical_id for scholar authority.
**Decision:** Three-tier identity model: (1) `source_id` (`src_{8_char_hash}` from frozen SHA-256) — per acquired file/set, permanent, globally unique. (2) `work_id` (`wrk_{author_slug}_{title_slug}`) — groups all editions of the same abstract work. The same work may have multiple sources. (3) `canonical_id` (`sch_{5_digit_sequence}`) — scholar identity in the centralized authority registry. The ABD-era `book_id` is preserved as `human_label` — a non-primary-key shorthand. Multi-volume works get ONE work_id; each volume may be a separate source_id if acquired separately.
**Alternatives considered:** (a) Single flat ID like ABD's book_id → rejected (can't group editions, can't track scholarly identity). (b) Two-tier (source + scholar, no work) → rejected (can't express "this is a different edition of the same work"). (c) work_id as primary key → rejected (source_id must be primary because multiple sources of the same work have different frozen files and metadata).
**Documents updated:** engines/source/SPEC.md §4.A.1, engines/source/CLAUDE.md.

### D-025: Source engine as primary creator of scholar authority records
**Decided:** 2026-03-04
**Context:** The scholar authority registry (`library/registries/scholars.json`) is a shared knowledge graph consumed by multiple engines. The source engine encounters scholars first (as authors and editors during intake). Other engines encounter scholars later (as quoted figures in text). Someone needs to own record creation.
**Decision:** The source engine is the primary creator of scholar authority records. When it identifies an author or muhaqiq during intake, it creates or enriches the record with biographical data from: source metadata extraction, LLM inference, and OpenITI enrichment. Other engines (especially excerpting) may write enrichments back. Progressive enrichment: records grow richer as more sources are processed. Scholar records include: canonical name, name variants, kunya, laqab, nisba, birth/death dates (hijri + CE), geographic data, school affiliations (per science), teachers, students, known works, scholarly standing, disambiguation notes.
**Alternatives considered:** (a) Separate scholar authority component owns all record creation → rejected (the source engine has the metadata at intake time; adding a middleman creates unnecessary coupling). (b) Each engine creates its own records → rejected (leads to fragmentation and duplicate records).
**Documents updated:** engines/source/SPEC.md §4.A.5, engines/source/CLAUDE.md.

### D-026: Text fidelity separate from scholarly trustworthiness
**Decided:** 2026-03-04
**Context:** A source's reliability has two independent dimensions. A perfectly trustworthy scholarly work (e.g., al-Mughni by a recognized muhaqiq) may have low text fidelity if acquired as iPhone photos with poor OCR. Conversely, a low-trust modern compilation may have high text fidelity because it's structured digital text. Conflating these leads to wrong trust decisions.
**Decision:** Source metadata tracks two independent signals: `text_fidelity` (quality of the text data itself — high/medium/low/unknown, determined by source type) and `trust_tier` (reliability of the scholarly content — determined by multi-factor evaluation of author standing, tahqiq quality, publisher reputation, source authority level, AND text fidelity as one input). Text fidelity affects downstream OCR confidence and normalization strategy. Trust tier affects whether excerpts default to verified or flagged knowledge.
**Alternatives considered:** Single combined "quality" score → rejected (masks important distinctions; a flagged source with high text fidelity should be processed differently from a verified source with low text fidelity).
**Documents updated:** engines/source/SPEC.md §4.A.4, §4.A.8.

### D-027: Work relationship graph with placeholder records for unacquired works
**Decided:** 2026-03-04
**Context:** Islamic scholarly works form dense relationship networks (sharh→matn, hashiyah→sharh, mukhtasar→original). These relationships are critical for the synthesizer's scholarly narratives and the scholar interface's book briefings. Many relationships point to works not yet in the library.
**Decision:** The source engine maintains a work relationship graph with 7 relationship types (sharh_of, hashiyah_on, mukhtasar_of, nazm_of, taqrirat_on, cites, responds_to). When a relationship target is not in the library, a placeholder work record is created with `status: "referenced_not_acquired"`. Placeholders exist in the work registry as known works without sources — they can accumulate citation counts, be targets of relationship edges, and serve as acquisition candidates. This enables the citation network to grow even before all referenced works are acquired.
**Alternatives considered:** (a) Only track relationships to acquired works → rejected (loses the vast majority of the scholarly network; most works reference more works than any library contains). (b) Track relationships but without placeholder records → rejected (no way to accumulate citation counts or priority-rank unacquired works).
**Documents updated:** engines/source/SPEC.md §4.A.9, §4.B.3, §4.B.4.

### D-028: OCR strategy — Mistral OCR 3 primary, Qari-OCR for Arabic diacritics
**Decided:** 2026-03-05
**Context:** The normalization engine needs OCR for scanned PDFs and iPhone photos. Arabic OCR with diacritics preservation is critical for scholarly texts.
**Decision:** Three-tier OCR strategy: (1) Mistral OCR 3 as primary engine — best multilingual document understanding, strong Arabic support, $1-2/1000 pages, 2000 pages/minute. (2) Qari-OCR v0.2 as specialized fallback for diacritically-heavy text — open-source, fine-tuned specifically for Arabic tashkeel (CER 0.061, WER 0.160 on diacritically-rich texts). (3) Dual-OCR comparison mode for low-fidelity sources — both engines process the same page, character-level alignment produces merged output with per-character confidence.
**Alternatives considered:** (a) Google Document AI only → rejected (Mistral OCR 3 outperforms on multilingual benchmarks and is cheaper). (b) Qari-OCR only → rejected (runs locally on GPU, slower for batch processing, less layout understanding than Mistral). (c) Tesseract → rejected (inadequate Arabic quality, especially for diacritics). (d) Docling OCR → rejected (Arabic support is experimental/early-stage).
**Documents updated:** engines/normalization/SPEC.md §4.A.4, reference/RESOURCES.md

### D-029: Normalized package schema redesign — source_id reference model
**Decided:** 2026-03-05
**Context:** The ABD-era normalized package schema uses `book_id` and duplicates source metadata into the manifest. The KR design uses `source_id` as the primary link and references source metadata rather than duplicating it, preventing metadata staleness.
**Decision:** The normalized package carries `source_id` as its primary link to upstream metadata. Phase 2 engines access the full source metadata record via this reference. The normalization engine does NOT duplicate source metadata into the normalized package. The manifest contains only normalization-produced metadata (division tree, layer map, fidelity summary, structural format). Content units contain only per-page processing results (text, layers, footnotes, flags, fidelity). This means enrichments to source metadata after normalization are automatically visible to Phase 2 engines without reprocessing.
**Alternatives considered:** Embedding full source metadata in the manifest → rejected (creates a staleness problem: if the source engine enriches metadata after normalization, the normalized package has stale data, and Phase 2 engines see the stale version).
**Documents updated:** engines/normalization/SPEC.md §3

### D-030: Multi-layer text detection — conservative default to commentary author
**Decided:** 2026-03-05
**Context:** When the normalization engine cannot determine which text layer a region belongs to (no typographic signals, no transition phrases), it must assign a default. The question is: default to the matn author (Layer 1) or the commentary author (Layer 2)?
**Decision:** Default to the commentary author (Layer 2). Rationale: misattributing matn text to the commentator is less harmful than the reverse. The commentator is typically explaining the matn author's position, so their words are contextually related. Misattributing commentary text to the matn author would put elaborate explanations in the mouth of an author known for terseness — a more detectable and more harmful scholarly integrity violation.
**Alternatives considered:** (a) Default to Layer 1 (matn) → rejected (more harmful error: puts verbose commentary in the mouth of terse matn authors). (b) Default to "uncertain" → rejected for regions that are clearly within the commentary body; used only for genuinely ambiguous regions.
**Documents updated:** engines/normalization/SPEC.md §4.A.5

### D-031: Universal footnote reference marker format
**Decided:** 2026-03-05
**Context:** Different source formats use different footnote reference conventions: Shamela uses `(N)`, PDFs may use superscript numbers, images may use various markers. Phase 2 engines need a single format to parse.
**Decision:** Footnote references in normalized `primary_text` use Unicode half-brackets: `⌜N⌝` (U+231C, U+231D). This is visually distinct from any source-format convention and parseable by Phase 2 engines without ambiguity. The original format-specific markers are not preserved — they are source-specific and would violate the normalization boundary.
**Alternatives considered:** (a) Strip all markers, rely on position → rejected (loses the reference-footnote link). (b) Use `[N]` → rejected (conflicts with bracket markers used for matn text in some sources). (c) Use `{{N}}` → rejected (conflicts with template syntax in some tools).
**Documents updated:** engines/normalization/SPEC.md §3

### D-032: Synthesized entries must be in Arabic
**Decided:** 2026-03-05
**Context:** Entries are the primary knowledge product — encyclopedic articles generated by the synthesizing engine at taxonomy leaves. The question was whether they should be in Arabic, English, or bilingual.
**Decision:** Entries must be in Arabic. The owner reads classical scholarly texts in Arabic, the source material is Arabic, the scholarly terminology is Arabic, and translating would lose precision. The interface and generated analysis (e.g., scholar interface explanations, study guidance) may use any of the owner's languages, but the scholarly content itself — entries, excerpts, citations — is Arabic.
**Alternatives considered:** (a) English entries → rejected (loses terminological precision, the owner reads Arabic natively). (b) Bilingual → rejected (unnecessary overhead; the scholarly substance is Arabic). (c) Per-entry language choice → rejected (adds complexity without benefit; the content is inherently Arabic).
**Documents updated:** reference/kr_decisions.md, NEXT.md (pending question resolved)

### D-033: Secure by design — error prevention over error correction
**Decided:** 2026-03-05
**Context:** The owner identified a foundational principle: KR handles sensitive information — scholarly knowledge whose corruption can change the entire understanding of a science. A single misattribution, a silent data loss, or an undetected layer confusion doesn't just produce a wrong answer — it can systematically distort how Rayane understands an entire field. Existing scholarly integrity measures (D-018, Criterion #21) address this partially, but the owner wants error PREVENTION elevated to a core architectural principle, not just error detection and correction.
**Decision:** "Secure by design" is a core architectural principle. Every engine, every data transformation, every metadata flow must be designed so that errors are structurally prevented — not just detected after the fact. Specific consequences:

1. **Immutability over mutability.** Frozen sources are never modified (already established). But this principle extends: intermediate artifacts (normalized packages, passage streams) are also write-once. Reprocessing creates new artifacts; it does not modify existing ones. This creates an audit trail and prevents silent corruption.

2. **Explicit over implicit.** Every decision the pipeline makes must be recorded with its confidence and reasoning. No engine may silently drop data, silently merge records, silently resolve an ambiguity, or silently choose a default. If a decision is made, it is logged. If data is excluded, the exclusion is recorded with a reason. The owner must be able to trace any piece of knowledge in the library back to its source through an unbroken chain of explicit, auditable decisions.

3. **Fail-loud over fail-silent.** When an engine encounters something it cannot handle correctly, it must fail visibly — flagging, warning, or stopping — rather than producing a plausible-looking but wrong result. A visible failure that stops processing is always preferable to an invisible error that enters the library. Every engine's error handling must be designed around this principle.

4. **Verification at every boundary.** Every time data crosses an engine boundary (source→normalization, normalization→passaging, etc.), the receiving engine validates what it receives against the sending engine's output contract. Schema validation is the minimum; semantic validation (does this data make sense?) is the goal. No engine trusts its input blindly.

5. **Provenance is mandatory.** Every knowledge product (excerpt, entry) must carry a complete provenance chain: which source, which page, which passage, which atoms, which engine version, which LLM model, what confidence. If provenance is broken at any point, the knowledge product is flagged as unverifiable.

6. **Corruption detection is continuous.** The system must be able to detect, at any time, whether the library's contents are consistent and uncorrupted. Hash chains from frozen sources through to placed excerpts enable integrity verification. If a hash doesn't match, something changed that shouldn't have.

7. **The blast radius of any single error must be bounded.** No single engine failure, misclassification, or data corruption should be able to cascade undetected across the entire library. Each engine's output is independently verifiable. The passage containment rule (D-011) is one instance of this principle; it extends to all engine boundaries.

**Relationship to existing decisions:** This strengthens D-018 (KR is Rayane's knowledge — corruption is personal), D-006 (Accuracy > Protection > Intelligence — accuracy is non-negotiable), D-004 (primary text integrity is absolute), and Criterion #21 (scholarly integrity). Those decisions address specific aspects; D-033 establishes the overarching principle that ALL design must serve.
**Alternatives considered:** Treating error handling as an implementation concern rather than an architectural principle → rejected (the owner correctly identifies that this must be foundational, not bolted on).
**Documents updated:** reference/kr_decisions.md, reference/DOMAIN.md (Core Identity section extended), DEEP_REASONING_PROTOCOL.md Criterion #21 note.

### D-034: Two-tier atom type system (structural type + scholarly function)
**Decided:** 2026-03-05
**Context:** The ABD-era atom schema has 6 structural types (heading, prose_sentence, bonded_cluster, verse_evidence, quran_quote_standalone, list_item) with no scholarly function classification. This means the excerpting engine receives atoms that tell it WHAT the text looks like but not WHAT ROLE the text plays in scholarly discourse. A prose_sentence could be a definition, an evidence citation, a refutation, or an example — and the excerpting engine has no way to distinguish them without re-analyzing the text.
**Decision:** Atoms are classified on two independent dimensions: structural type (7 types describing physical text shape) and scholarly function (16 types describing the text's role in scholarly discourse). The two dimensions are independent: a verse_line can have function "definition" (a versified definition) or "example" (a verse cited as evidence). This separation ensures the excerpting engine receives both structural and semantic information, enabling it to build contextually correct excerpts. Each scholarly function carries a confidence score to prevent confidence laundering (D-033).
**Alternatives considered:** (a) Single combined type enum (like ABD) → rejected (too many combinations needed — 7×16 = 112 types; and it conflates two independent dimensions). (b) No scholarly function classification at atomization, deferring entirely to excerpting → rejected (the atomization engine already has the text in context during LLM analysis; deferring would require the excerpting engine to re-analyze every atom, doubling LLM costs and losing the atomization context). (c) Hierarchical type system (structural → scholarly subtypes) → rejected (the dimensions are genuinely independent, not hierarchical).
**Documents updated:** engines/atomization/SPEC.md §4.A.3, engines/atomization/CLAUDE.md, schemas/atoms.json (to be rewritten).

### D-035: No multi-model consensus for atomization
**Decided:** 2026-03-05
**Context:** Multi-model consensus (VISION.md §8) is the mechanism for increasing confidence by having multiple LLMs independently process the same input. The question was whether atomization should use consensus for atom boundary and type decisions.
**Decision:** Atomization does NOT use multi-model consensus. Instead, it uses a single primary model with escalation to a stronger model on failure. Rationale: atom boundary placement is an annotation-like task where consistency matters more than agreement. Different models may place valid boundaries at different positions (e.g., one splits a long sentence into 3 atoms, another into 4 — both can be correct). Averaging or voting on such decisions produces worse results than letting one skilled model work consistently. Consensus IS valuable for higher-stakes decisions (excerpt grouping, taxonomy placement) where the question is binary (correct/incorrect) rather than a matter of annotation granularity.
**Alternatives considered:** (a) Full consensus on every passage → rejected (doubles/triples LLM cost for a task where consistency matters more than agreement). (b) Consensus only for multi-layer passages → considered but deferred (may revisit if layer attribution accuracy is a problem in practice).
**Documents updated:** engines/atomization/SPEC.md §6.

### D-036: Multi-model consensus for excerpting self-containment and school attribution
**Decided:** 2026-03-05
**Context:** The excerpting engine makes high-stakes decisions that directly affect library quality. Unlike atomization (where individual atom misclassification has low impact, D-035), excerpting errors propagate: a bad self-containment judgment means an incomplete excerpt enters the library; a bad school attribution means the synthesizer misrepresents a scholarly tradition. These are exactly the precision-critical content decisions that multi-model consensus (§2.2) is designed for.
**Decision:** Multi-model consensus is used for two specific excerpting decisions: (1) self-containment evaluation — two models independently score self-containment; disagreement > 0.2 triggers conservative (lower) score + review flag, (2) school attribution — two models independently determine school; disagreement triggers lower confidence + review flag. Topic classification, author identification, and evidence extraction do NOT use consensus because they have independent downstream validation (taxonomy engine validates topics; author ID is primarily deterministic from layer metadata; evidence is validated by structured reference matching).
**Alternatives considered:** (a) No consensus for excerpting → rejected (excerpting is the highest-stakes Phase 2 engine; D-035's rationale for no atomization consensus does not apply here). (b) Consensus for ALL excerpting decisions → rejected (too expensive; topic classification and author ID have independent validation paths). (c) Three-model consensus → rejected (diminishing returns; two independent models from different providers provide sufficient confidence).
**Documents updated:** engines/excerpting/SPEC.md §6, engines/excerpting/CLAUDE.md

### D-037: Three-phase excerpting pipeline (boundary → self-containment → enrichment)
**Decided:** 2026-03-05
**Context:** The excerpting engine must perform three distinct tasks: decide which atoms group together, evaluate whether each group is self-contained, and enrich each excerpt with metadata. These tasks have different inputs, different quality requirements, and different failure modes. Combining them into a single LLM pass (as ABD did) creates a monolithic operation that's hard to debug, hard to validate, and hard to optimize.
**Decision:** Three-phase pipeline: (1) Boundary Detection — LLM determines atom groups, respecting bonded constraints. (2) Self-Containment Evaluation — LLM evaluates each candidate, with consensus for verified sources. Candidates can be enriched (add context atoms) or merged if insufficient. (3) Metadata Enrichment — deterministic + LLM enrichment of all fields. Each phase can be independently validated, retried, and optimized. Phase failures are isolated: a metadata enrichment failure doesn't invalidate the boundary detection.
**Alternatives considered:** (a) Single-pass extraction (ABD approach) → rejected (monolithic, hard to debug, no independent validation per phase). (b) Two-phase (boundary+self-containment combined, then enrichment) → rejected (boundary detection and self-containment evaluation have different prompt requirements; separating them allows self-containment to trigger boundary adjustments like enrichment and merging).
**Documents updated:** engines/excerpting/SPEC.md §4.A.1, engines/excerpting/CLAUDE.md

### D-038: Two-stage placement algorithm with three candidate sources
**Decided:** 2026-03-05
**Context:** The taxonomy engine must determine which leaf an excerpt belongs at. The excerpting engine proposes a leaf, but this proposal may be wrong (the excerpting engine doesn't have the full tree context). The question is: how does the taxonomy engine make its own placement decision?
**Decision:** Two-stage algorithm. Stage 1 (candidate generation) draws from three sources: (a) the excerpting engine's proposed leaf, (b) LLM-driven topic search against the tree structure (hierarchical for trees >200 leaves), (c) embedding similarity against precomputed leaf title embeddings. Stage 2 (candidate ranking) has the LLM score each candidate 0–1 considering topic match, specificity, and overlap with existing excerpts. The multi-source approach ensures robustness: LLM search handles semantic understanding, embedding similarity catches terminology mismatches, and the excerpting engine's proposal leverages upstream context. The three-threshold system (≥0.8 auto-approve, 0.5–0.8 human gate, <0.5 unplaceable) balances automation with safety.
**Alternatives considered:** (a) Trust the excerpting engine's proposal entirely → rejected (the excerpting engine lacks full tree context; it proposes a leaf based on the excerpt's content, but the tree's actual structure may have a better fit). (b) Embedding-only approach → rejected (Arabic scholarly topic titles have complex semantic relationships that embedding similarity alone cannot capture — e.g., المبتدأ and الخبر are closely related topics with very different leaves). (c) LLM-only without embedding fallback → rejected (LLMs can miss leaves when terminology differs between the excerpt and the tree node title — embeddings catch these cases).
**Documents updated:** engines/taxonomy/SPEC.md §4.A.1, engines/taxonomy/CLAUDE.md.

### D-039: Limited multi-model consensus for taxonomy (placement only, ambiguous range)
**Decided:** 2026-03-05
**Context:** The taxonomy engine must decide whether to use multi-model consensus (§2.2) and for which decisions. Unlike excerpting (D-036, where self-containment and school attribution have high stakes), the taxonomy engine's decisions have different risk profiles: most placements are clearly correct, evolution is always human-gated, and coverage is deterministic.
**Decision:** Multi-model consensus is used only for placement decisions in the ambiguous confidence range (0.5–0.8). Two models from different providers. Agreement increases confidence; disagreement triggers human gate escalation. Consensus is NOT used for tree construction, evolution proposals, or high-confidence placements. Rationale: placement decisions in the 0.5–0.8 range are the sweet spot where a second opinion is most valuable. Below 0.5, the case is genuinely unplaceable (needs human judgment, not model averaging). Above 0.8, single-model accuracy is sufficient. Tree construction and evolution require coherent architectural vision, not averaging — consensus would produce muddled compromises.
**Alternatives considered:** (a) Consensus for all placements → rejected (doubles LLM cost for decisions where single-model confidence is high). (b) No consensus at all → rejected (the 0.5–0.8 range has genuine ambiguity where a second model can resolve tiebreakers). (c) Consensus for evolution proposals → rejected (evolution is always human-gated anyway; consensus adds cost without changing the workflow since the owner makes the final decision).
**Documents updated:** engines/taxonomy/SPEC.md §6, engines/taxonomy/CLAUDE.md.

### D-040: Analytical layer boundary — structured traceability via grounding_type
**Decided:** 2026-03-05
**Context:** VISION.md §6.4 leaves an OPEN QUESTION: "To what extent may the synthesizing engine's analytical layer include knowledge or connections not directly stated in the source excerpts?" The tension is between adding genuine scholarly value (cross-source connections, historical context, teacher-student chains) and risking unverifiable additions that the owner might mistake for source-based knowledge.
**Decision:** The analytical layer MAY include LLM-contributed knowledge and connections not in the source excerpts, subject to three structural constraints: (1) every claim in the entry carries an explicit `grounding_type` field — one of `library_excerpt` (traced to a specific excerpt), `library_metadata` (derived from upstream metadata like author dates or teacher-student links), or `llm_research` (from the engine's LLM training knowledge). (2) The factual layer (`core_treatment`, `scholarly_positions`, `edge_cases`) must contain ONLY `library_excerpt` and `library_metadata` grounded claims — never `llm_research`. (3) The `analytical_layer` section is structurally separate and may contain all three grounding types, with `llm_research` claims clearly marked. This resolves the open question by making the boundary a structural property of the output schema, not a vague guideline. The owner and scholar interface always know which claims are excerpt-backed and which are engine-contributed.
**Alternatives considered:** (a) No LLM-contributed content at all → rejected (produces flat compilations without the scholarly narrative that makes entries transformative — see ENTRY_EXAMPLE.md). (b) Allow LLM content everywhere with disclaimers → rejected (violates the accuracy core property; disclaimers are too easily ignored). (c) Post-hoc verification of all claims → rejected (computationally expensive and doesn't solve the fundamental structural problem of mixing sources).
**Documents updated:** engines/synthesis/SPEC.md §3.2, §3.3, §4.A.4.2, §4.A.5 (Check 6). VISION.md §6.4 OPEN QUESTION to be updated in next VISION correction pass.

### D-041: Consensus technology stack — LiteLLM + Instructor with parallel independent comparison
**Decided:** 2026-03-06
**Context:** The consensus component needs a technology stack for multi-model LLM dispatch, structured output extraction, and response comparison. The key architectural question: should KR use a debate/deliberation approach (models see each other's responses and iterate) or a parallel-independent approach (models process the same input independently and outputs are compared mechanically)?
**Decision:** Parallel-independent comparison using LiteLLM (provider abstraction) + Instructor (structured output extraction). Both models receive the identical prompt, produce structured responses conforming to a Pydantic schema, and a deterministic comparison strategy evaluates agreement. Models never see each other's responses. Dispatch is async-parallel via asyncio.gather for minimum latency. LiteLLM is used as a Python SDK (not proxy server) since the consensus component is a shared library, not a standalone service.
**Alternatives considered:** (a) Debate/deliberation approach (CONSENSAGENT-style) → rejected. Research (ACL 2025) shows debate-style consensus suffers from sycophancy — agents reinforce rather than critically evaluate each other's responses. For KR's use case (verifying factual/classification decisions), independent evaluation is more reliable than collaborative refinement. (b) DSPy Ensemble module → considered but rejected as the primary mechanism. DSPy's Majority voting runs the same model multiple times; KR needs different models from different providers for true independence. DSPy may be used for prompt optimization in calling engines, but not for the consensus dispatch itself. (c) OpenRouter as the sole routing layer → rejected as the primary integration. OpenRouter is a hosted service that adds latency and a dependency; LiteLLM is an in-process library that can route through OpenRouter when needed but also supports direct provider APIs. LiteLLM gives more control over fallback logic, cost tracking, and async dispatch.
**Documents updated:** shared/consensus/SPEC.md (all sections), shared/consensus/CLAUDE.md, reference/RESOURCES.md (consensus component resources section).
