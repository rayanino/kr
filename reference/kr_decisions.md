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
