# خزانة ريان — Vision and Architecture Specification

**Version:** 1.0.1
**Status:** Active — this is the single authoritative specification for خزانة ريان.
**Date:** 2026-03-03

---

## Document Purpose and Authority

### Scope and Precedence

This document is the authoritative vision and architecture specification for خزانة ريان. It defines the application's identity, the library's structure, the vocabulary used throughout the project, the architectural boundaries governing all components, and the design principles that govern every decision.

This document defines _what_ the application is and _why_ it is designed the way it is. It does not define implementation-level specifics: exact schemas, prompt templates, algorithm internals, or code-level interfaces. Those are specified in dedicated per-component documentation (Level 2) and per-science documentation (Level 3). When per-component documentation conflicts with this document on matters of application-wide design, this document takes precedence.

When the owner issues a verbal or written instruction during a work session that contradicts this document, the instruction is treated as a proposed amendment. The implementer follows the instruction for the immediate task, but the amendment must be written back into this document before the next work session begins. If it is not written back, this document's original text governs. This prevents drift between the specification and the codebase.

### Documentation Contract

All authoritative documentation in this project — this specification, per-component specs, the CLAUDE.md, and any other governing documents — is written under the following contract. Every document in the project inherits these rules unless it explicitly states otherwise.

**Primary audience.** The primary readers of project documentation are AI agents: Claude (acting as architectural advisor and co-designer), Claude Code (the primary implementer), and any LLMs operating within the application (extraction, consensus, synthesis). Documentation structure, wording, and formatting are optimized for unambiguous machine interpretation. Human readability is valued but never at the cost of machine precision. Where a sentence could be read two ways by an AI agent, it must be rewritten until only one reading is possible.

**Normative and non-normative content.** Normative content defines binding rules, architectural constraints, structural requirements, and behavioral specifications. Non-normative content provides rationale, context, historical background, motivation, and examples. Non-normative sections and passages are explicitly marked with the label _[Non-normative]_ or are contained within a section whose heading includes the word "Rationale" or "Context." All unmarked content is normative by default.

**The no-inference rule.** When documentation is silent on a behavior, ambiguous about a requirement, or leaves a decision unspecified, implementers must not invent behavior or fill gaps with assumptions. They must stop, surface the gap, and resolve it in documentation before implementation proceeds. Silence is never permission. Ambiguity is never an invitation to guess. This rule exists because guessed behavior is the primary source of silent bugs in this project.

**The no-premature-constraint rule.** Documentation must not specify details about components, behaviors, or decisions that have not been finalized. When a design area is known but its specifics are undecided, the documentation states that the area exists and that its specification is deferred to a named future document or discussion. Stating a premature constraint is worse than stating nothing, because it creates a false sense of resolution.

**Forward references.** This document uses terms (such as "science tree," "excerpt," "leaf," "entry," "school") before their formal definitions in §2 (Glossary). These terms carry exactly the meanings defined in §2. If a reader encounters a term before its definition, the term's meaning is the one given in §2, not any informal meaning that might be inferred from context.

**Scope qualifiers.** Where it matters whether a statement describes the current state, a near-term target, or a long-term aspiration, the statement is explicitly qualified. When no qualifier is present, the statement describes the system's intended mature-state architecture — the design the system is built toward, even if early milestones implement only a subset.

**Examples.** Examples are non-normative and non-exhaustive unless explicitly stated otherwise. They illustrate intent but do not limit it.

### Versioning

This document uses semantic versioning: MAJOR.MINOR.PATCH. A MAJOR increment reflects a fundamental change to the application's identity, architecture, or core properties. A MINOR increment reflects a significant addition or modification to a section (new subsections, revised design decisions). A PATCH increment reflects clarifications, corrections, and wording improvements that do not change the design. All changes require the owner's review and approval. A changelog is maintained at the end of this document.

---

## §1 — What خزانة ريان Is

This section defines the application's identity, scope, purpose, core properties, primary knowledge products, completion model, and boundaries. It does not define the processing logic by which components operate — those details are in per-component documentation (Level 2). §6–§9 define the architectural constraints governing entries, the source pipeline, quality mechanisms, and human gates. Terms used in this section before their formal definition in §2 carry their §2 meanings exactly.

### 1.1 Identity

خزانة ريان (Khizanat Rayan) is a personal intelligent Islamic scholarly library. It is a software application that builds, maintains, and continuously expands a structured library of Islamic knowledge for its owner, ريان عبّو. The application combines autonomous knowledge discovery with intelligent processing to populate a library organized into science trees — hierarchical taxonomies of Islamic and supporting sciences — where knowledge is stored as self-contained excerpts at precise topic locations, and where synthesized encyclopedic entries make that knowledge accessible for study.

The name uses خِزانة, the classical Arabic word for a scholar's personal book collection and knowledge repository (as in خزانة الأدب by البغدادي), combined with the owner's name. It is abbreviated **KR** in code, directory names, configuration, and internal references.

The following terms identify distinct entities within the project. Their full definitions are in §2 (§2.1 for the application and library, §2.2 for processing architecture). The summaries below establish orientation; §2 is authoritative for precise meanings.

**خزانة ريان (the application):** the complete software system — all source pipeline components, all engine components, all library infrastructure, all interfaces. When documentation says "the application" or "KR," it means this entire system.

**The library (المكتبة):** the persistent, structured knowledge product that the application builds and maintains. The library contains science trees, excerpts, entries, source metadata, and coverage data. The library is the product; the pipeline and engines are machinery that feeds it. When documentation says "the library," it means this stored knowledge collection, not the application as a whole.

**The engine:** shorthand for the source-agnostic processing core — Phase 2 per §2.2. The application's processing is organized into seven individually named engines across both phases (§2.2), of which the five source-agnostic engines constitute Phase 2. When documentation says "the engine," it refers to Phase 2 collectively. When a specific engine is responsible, it is named explicitly.

**The source pipeline:** the source-format-specific components that discover, acquire, document, and normalize knowledge sources — Phase 1 per §2.2. When documentation says "the source pipeline," it means this group specifically.

**The synthesizing engine:** identified separately because it is architecturally distinct from the other Phase 2 engines (passaging, atomization, excerpting, taxonomy per §2.2) — it reads the library's stored excerpts, not the pipeline's intermediate processing artifacts. When documentation says "the synthesizing engine," it means this component specifically.

**The owner (المالك):** the single user of خزانة ريان. The application is a personal tool built for one person, and design decisions about the library's content, structure, and scholarly priorities serve the owner's scholarly development.

### 1.2 Scope

**Knowledge scope.** The library covers two tiers of sciences.

_Primary sciences_ are the Islamic and Arabic scholarly disciplines — the sciences traditionally classified as العلوم الشرعية and علوم اللغة العربية. These are the library's core identity. They receive full treatment: comprehensive taxonomy trees, full coverage tracking, and prioritized autonomous discovery. The preliminary inventory of primary sciences is in §4.3.

_Supporting sciences_ are non-Islamic disciplines included because they directly enhance understanding of primary sciences. Examples: vocal anatomy and physiology supporting علم التجويد, Roman and Persian history supporting علم السيرة النبوية, formal logic supporting علم أصول الفقه, astronomy supporting فقه المواقيت. Supporting sciences receive taxonomy trees and excerpts, but their coverage expectations and autonomous discovery priority are secondary to primary sciences. The library does not aim to become a comprehensive medical or history library — it targets the specific knowledge within supporting sciences that serves Islamic scholarship.

**Language scope.** Source material is primarily in Arabic. The library also accepts English-language sources where they contain relevant scholarly or supporting-science content. The full specification of multi-language handling — how non-Arabic excerpts are stored, whether translation is performed, how entries handle mixed-language source material — is deferred to per-component documentation for the source pipeline and synthesizing engine.

**Interconnectedness.** Islamic sciences are deeply interconnected. A single Fiqh ruling may draw on hadith evidence, Quranic exegesis, jurisprudential methodology, and linguistic analysis simultaneously. The library handles this through primary classification: each excerpt belongs to exactly one leaf in one science tree, determined by the excerpt's primary topic. Cross-references to other sciences are preserved within the excerpt's text — context mentions of other topics appear naturally in the excerpt's content. Discovery of such cross-references is a function of search over excerpt text, not of metadata-based navigation or multi-placement (per §5.3). Formal cross-reference infrastructure between science trees is a recognized future design consideration.

**Multi-science sources.** A single source may produce excerpts destined for multiple science trees. The source engine records the source's science scope in source metadata (§7.3), and the taxonomy engine places each excerpt independently at the correct leaf in the correct tree based on the excerpt's primary topic. Processing a single source may therefore populate leaves across multiple science trees in a single pipeline run.

### 1.3 Purpose

The application exists to serve its owner's development as an Islamic scholar. Its purpose is to build the most comprehensive, structured, and accurate personal scholarly library achievable, and to do so in ways that were previously impossible without the capabilities that modern AI and software provide.

The application achieves this through the following functions, listed in order of architectural centrality:

1. **Organizing the landscape of Islamic knowledge into science trees** — hierarchical taxonomies where every topic within every science has a precise, identifiable location. Science trees are living structures that evolve as new knowledge reveals finer distinctions. _(Architectural invariant: science trees are the structural foundation of the library.)_

2. **Extracting self-contained excerpts from sources and placing them at the correct leaves** — breaking down source material into independently understandable knowledge units, each attributed to its author and scholarly tradition, each placed where it belongs in the taxonomy. _(Architectural invariant: excerpts are the factual foundation of the library.)_

3. **Generating encyclopedic entries at every populated leaf** — synthesized articles that present the leaf's verified knowledge in a comprehensive, structured, deeply reasoned form. Where the science has scholarly schools, each school receives its own dedicated entry generated exclusively from that school's excerpts (per §6.2); where schools do not apply, the leaf has a single entry from all verified excerpts. Entries are the primary knowledge product that the owner studies from: they draw connections between positions, explain disagreements, contextualize opinions, and include scholarly quotes for memorization. Entries are not summaries of excerpts; they are the intellectual high-water mark of the library. _(Architectural invariant: entries are the primary study product of the library.)_

4. **Autonomously discovering and acquiring new knowledge sources** — continuously searching configured repositories and the broader internet for relevant scholarly material, acquiring it, processing it through the pipeline, and adding its excerpts to the library without requiring the owner to manually find and feed every source. _(Long-term target, incrementally built: autonomous discovery scales over milestones.)_

5. **Accepting the owner's manual input** — personal study notes, teacher lecture transcriptions, written reflections, and any other knowledge the owner encounters. Manual input enters the same source pipeline as autonomously discovered material and produces excerpts placed alongside classical scholarship. This is a source pathway within the pipeline, not a separate system. _(Architectural invariant: manual input is a first-class source type.)_

6. **Tracking coverage** — measuring how well each leaf, branch, tree, and the library as a whole is populated with verified excerpts. Coverage identifies gaps: where verified knowledge is thin, where specific scholarly schools are underrepresented, where entire sub-topics lack verified excerpts. _(Long-term target: coverage becomes actionable as the library matures.)_

### 1.4 What Makes This Possible — Technology as Enabler

_[Non-normative — this section provides rationale and context, not binding requirements.]_

The application's design rests on a premise: modern AI and software make possible what was previously impossible for an individual scholar. This premise is not incidental — it is the architectural motivation. Every major capability of the application exists because technology now enables what no human effort alone could achieve. The following are the capabilities that set this library apart from anything historically possible.

**Exhaustive source coverage.** A traditional student reads dozens, perhaps hundreds of books in a lifetime, chosen by availability and teacher recommendation. The application can process thousands of sources across every accessible repository, autonomously discovering material the owner would never have found. The result: the library's coverage of a topic reflects the breadth of the entire scholarly tradition, not just the books the owner happened to read.

**Precision placement across the entire knowledge landscape.** A traditional student accumulates knowledge sequentially, book by book, with no systematic way to see where that knowledge fits in the larger structure of a science. The application places every excerpt at a precise location in a structured taxonomy, making the entire landscape of a science visible and navigable. The owner can see — at any point — exactly what topics exist, which have coverage, and which are gaps.

**Multi-perspective awareness at every topic.** A traditional student typically studies deeply within one مذهب and may learn other schools' positions incidentally. The application systematically organizes all scholarly schools' positions at every topic, so the owner sees the full spectrum of scholarly opinion at every leaf — not just their own school.

**Encyclopedic synthesis.** No human can hold thousands of excerpts in memory and produce a comprehensive, structured article integrating all of them. The synthesizing engine can. The entries it produces — drawing connections, contextualizing disagreements, selecting quotes, structuring for comprehension — represent a level of scholarly synthesis that would take a human weeks per topic and the application produces systematically across the entire library.

**Living, evolving structure.** A traditional reference library is organized once and remains static. The application's taxonomy evolves as new knowledge reveals finer topic distinctions, redistributing excerpts and regenerating entries as the tree evolves (through the human-gated evolution process per §4.4). The library's structure improves itself.

**Continuous growth without human effort.** The library grows autonomously. New sources are discovered, acquired, processed, and placed while the owner studies. The owner's primary job is to learn from the library, review at human gates, and contribute their own notes — not to manage the acquisition pipeline.

These capabilities are not features to be added later; they are the reason the application exists. Implementation must ensure that each capability is built with the same depth and sophistication that the capability itself promises. Building a shallow version of any of these capabilities would defeat the application's purpose.

### 1.5 Core Properties

Three properties define خزانة ريان at the deepest architectural level. Every design decision, every implementation choice, and every architectural boundary serves these three properties. They are listed in strict priority order: when two properties conflict, the higher-priority property governs.

These three are the complete set of core properties. Other desirable qualities — performance, scalability, usability, developer experience — are implementation concerns that serve these properties. They are not independent core properties.

**Property 1 (highest priority): Accuracy.** Every piece of knowledge in the library must be correctly attributed, correctly placed, and correctly represented. An excerpt attributed to the wrong author, placed at the wrong leaf, representing a position the author does not hold, or missing critical context, is worse than a gap in the library — it creates misinformation that the owner may study, memorize, and teach to others. The application uses multi-model consensus, cross-validation, human gates, and feedback loops (per §2.2) to minimize errors. When the application is uncertain about any content decision, it flags for human review rather than proceeding with a best guess. The goal is not merely "few errors" but the systematic elimination of every detectable error through layered defenses.

**Property 2: Protection from error.** Human error and system error are the primary threats to the library's integrity. The architecture is designed with defense in depth: multiple independent error-catching mechanisms layered so that an error must evade all of them to enter the library undetected. This includes validated schemas that reject malformed data, consensus mechanisms that catch disagreements, human gates that require the owner's approval before high-impact state changes (taxonomy evolution, excerpt placement), intelligent verification of human inputs and decisions, feedback loops that trace errors to root causes and fix them systemically, physical separation of verified and flagged knowledge, data integrity checks (checksums, consistency verification between tree definitions and storage), and full auditability of every decision the application makes. Protection from error is not a phase or a checklist — it is a continuous property that every component, at every stage, must exhibit at all times.

**Property 3: Intelligence.** Decisions that require judgment about content, quality, relevance, scholarly context, or organizational structure are made by intelligent reasoning — currently provided by LLMs, but defined architecturally as a capability requirement, not a vendor dependency. This includes: determining what sources are relevant, evaluating trustworthiness, identifying atom boundaries and types, grouping atoms into self-contained excerpts, classifying excerpts into taxonomy leaves, detecting when taxonomy evolution is needed, generating synthesized entries, and analyzing correction patterns to improve processing rules (per §2.2's feedback loop definition). Deterministic algorithms handle mechanical tasks: schema validation, file I/O, character counting, index maintenance, reference integrity checks. When a decision has a deterministic correct answer (e.g., the text explicitly states "قال الشافعي" and the author metadata confirms the Shafi'i school), an algorithm can handle it. When a decision requires judgment, intelligent reasoning handles it. Intelligence is the foundation that makes the application capable of handling the vast diversity and nuance of Islamic scholarly content — without it, the application would be a static file organizer, not a scholarly library.

### 1.6 The Entry as Primary Knowledge Product

Encyclopedic entries are, alongside excerpts, a primary knowledge product of the library — not a convenience layer or a "nice to have" feature. The owner's primary interaction with the library is reading and studying entries. The quality of entries directly determines the quality of the owner's scholarship. This subsection establishes the entry's architectural identity; the full specification of entry generation is in §6.

**What an entry is.** An entry is a synthesized encyclopedic article at a leaf (or at a school-group within a leaf, where the science has scholarly schools). It is generated by the synthesizing engine, reading the leaf's verified excerpts as its factual foundation, and producing a comprehensive, deeply structured article.

**Entries are more than summaries.** An entry contains two distinct layers. The _factual layer_ faithfully represents all positions, attributions, and evidence present in the verified excerpts — every scholarly opinion, every piece of evidence, every attribution must be accurately reflected and traceable to specific excerpts. The _analytical layer_ is the synthesizing engine's intellectual contribution: drawing connections between positions that no single excerpt states, explaining why disagreements exist, contextualizing opinions within the broader scholarly tradition, structuring the material for comprehension, choosing when to quote a scholar directly (for memorization value) versus when to paraphrase, and providing further clarification where the excerpts alone would leave gaps. Both layers together constitute the entry.

**Entry cardinality.** At a leaf where the science has scholarly schools (مذاهب): each school that has verified excerpts at the leaf gets its own dedicated entry, generated exclusively from that school's verified excerpts. There is no cross-school entry that mixes positions from different schools. At a leaf where the science has no schools or where schools are not relevant to the topic: the leaf has a single entry generated from all verified excerpts. This cardinality model is binding on the synthesizing engine's design.

**Relationship to excerpts.** Excerpts are the factual foundation; entries are the scholarly product. The factual layer of an entry must be fully traceable to the excerpt collection — every factual claim in an entry must have a corresponding excerpt. The analytical layer is a generated intellectual contribution that may vary across regenerations (the synthesizing engine may draw different connections or structure differently when regenerated). This is acceptable and expected: the analytical layer represents the synthesizing engine's best current scholarly reasoning, not a fixed artifact.

**Staleness.** Entries become stale per §2.4's staleness definition. The application tracks staleness and flags affected entries for regeneration. Stale entries are clearly marked when displayed. Regeneration details are specified in §6 and the synthesizing engine's per-component documentation (Level 2).

**Entries and the verified/flagged separation.** The factual layer of an entry is generated exclusively from verified excerpts. The analytical layer may reference flagged content for scholarly context, and a separate critical analysis section may address flagged excerpts directly. The complete separation rules governing entry generation — including how the analytical layer references flagged content and how the critical analysis section is structured — are specified authoritatively in §6.2.

### 1.7 Completion Model

_[The terminology "minimum viable completion" is deliberately avoided — this section defines a multi-level completion model aligned with the incremental implementation strategy in §10.]_

**Per-science baseline completion:** a science is baseline-complete when every leaf in its tree has at least one verified, placed excerpt from at least one source, and every leaf with verified excerpts has a generated entry. The science is usable as a study and reference tool at this level. Baseline completion is achieved science by science, not all-at-once across the entire library. Early milestones focus on completing specific sciences rather than spreading thin across all of them.

**Per-science rich completion:** a science is richly complete when its leaves have verified excerpts from multiple sources by different authors, when all scholarly schools relevant to the science have at least one verified excerpt at every applicable leaf, and when coverage tracking shows no significant gaps. "All scholarly schools" means every school with a documented position — not just the four major Fiqh مذاهب, but also minority positions, individual scholarly opinions, and smaller schools where they exist. The goal is exhaustive coverage of the scholarly tradition's diversity, limited only by what sources are available.

**Library-wide maturity:** the library as a whole is mature when all primary sciences have achieved rich completion, supporting sciences have achieved at least baseline completion, science trees have evolved to their natural granularity through repeated evolution cycles, and the autonomous discovery system has thoroughly searched all configured repositories.

**The library is never frozen.** New sources continue to be discovered. The owner's notes continue to be added. Science trees continue to evolve. Entries continue to be regenerated as the excerpt base grows. Completion is a measure of coverage depth, not a terminal state.

**The bootstrapping cycle.** Building a science tree requires understanding the science's structure, which comes partly from studying sources. But processing sources requires a tree to place excerpts in. This is a recognized bootstrapping cycle: initial trees are built from research into major works' organizational structures, sources are processed against these trees, the processing reveals structural flaws, and taxonomy evolution corrects them. Early versions of any science's tree will have imperfections that are corrected over time. This iterative refinement is not a bug — it is the design.

### 1.8 What خزانة ريان Is Not

_[This section defines negative scope — what the application explicitly does not aim to be. These boundaries prevent scope creep and clarify the application's identity.]_

**Not a fatwa service.** The library presents scholarly positions with full attribution. It does not declare "the correct ruling is X." It records which scholars consider which position الراجح, with their reasoning, but the library itself does not adjudicate between positions. The owner forms their own scholarly conclusions.

**Not a collaborative or multi-user platform.** The application is built for one person. There is no multi-user access, no sharing system, no collaborative editing. Design decisions are made for the owner's needs alone.

**Not a publishing tool.** The library is a study and reference tool. It does not generate content for publication, produce books, or format material for distribution. The owner may use knowledge gained from the library in their teaching and writing, but the application itself is not a publishing pipeline.

**Not a replacement for human teachers and sequential study.** The library complements traditional scholarship — it does not replace studying with teachers, reading books cover-to-cover, or the personal development that comes from human scholarly relationships. It provides a structured, comprehensive reference that enhances and accelerates study.

### 1.9 Non-Negotiables and Risks

This section names the application's most critical requirements and its most dangerous failure modes. These are not design preferences — they are absolute constraints that override convenience, speed, and scope at every point in development.

**Non-negotiable: zero tolerance for silent corruption.** The gravest threat to the library is content that appears correct but is wrong — a misattributed opinion, a misplaced excerpt, an entry that misrepresents a scholarly position, a مذهب label that is subtly incorrect. Because the owner studies from the library, memorizes its entries, and may teach others based on its content, a silent error propagates far beyond the library itself. Every component, at every stage, must be designed with the assumption that silent corruption is the primary threat. This means: multi-model consensus for content decisions, algorithmic validation for structural integrity, human gates for high-impact changes, intelligent verification of human inputs, periodic integrity audits of stored data, and regression testing whenever system rules change.

**Non-negotiable: defense at every decision point.** Wherever the application makes a choice with multiple possible outcomes — which leaf to place an excerpt at, what school to attribute, where to draw excerpt boundaries, whether to trigger evolution, whether a source is trustworthy — that decision point must have a verification mechanism. The verification can be consensus, validation, human review, or a combination. No decision point with the potential to introduce error may operate without a check. This applies during production (building the library) and must not be deferred to a later testing phase. Error prevention happens at the moment of each decision, not after the fact.

**Non-negotiable: mutual verification between human and autonomous systems.** Human gates verify autonomous decisions (the owner reviews extraction, approves evolution). Equally, the application must intelligently verify human inputs — if the owner feeds in a manual note with a مذهب attribution that conflicts with the author's known school, the application flags this rather than accepting it silently. Neither the human nor the autonomous system is trusted unconditionally. Both check each other.

**Non-negotiable: data portability.** The library's data must be stored in open, documented formats that remain accessible to the owner independently of the application. The owner must never be locked into the application to access their own knowledge. If the application ceases to exist, the library's content remains fully accessible and usable. The specific storage formats are implementation decisions specified in per-component documentation (Level 2), subject to this portability constraint.

**Risk: silent behavioral drift in AI models.** The application depends on LLM behavior for content decisions. When an underlying model is updated (new version, changed behavior, different training), the application's content quality can silently change. Mitigation: gold baselines exist for validated extraction output. Whenever a model used in the application is updated, regression tests against gold baselines must run before the updated model is used in production. Degraded results block the update.

**Risk: expertise asymmetry at human gates.** The owner's expertise varies across sciences. For sciences the owner has studied deeply, human gate review is effective. For sciences the owner has barely begun studying, the owner may lack the expertise to catch subtle LLM errors. Mitigation: the application tracks the owner's declared confidence level per science (§2.5). For lower-confidence sciences, the application applies more conservative processing: more flagging, less automatic placement, explicit "pending expert review" markers on excerpts and entries.

**Risk: storage integrity degradation.** Beyond processing errors, the library's stored data can degrade over time through file corruption, interrupted writes, or bugs in file-handling code. Mitigation: periodic integrity verification — checksums on excerpt files, consistency checks between tree YAML definitions and directory structures, metadata-content agreement verification. Integrity checks run as scheduled background operations.

---

## §2 — Glossary

### 2.0 Glossary Scope and Authority

This section defines the vocabulary used throughout خزانة ريان's documentation and codebase. Every term defined here carries exactly the meaning given here. When a term appears anywhere in the project — in this specification, in per-component documentation, in code, in configuration, in logs — it carries its §2 meaning unless the context explicitly defines a local override.

**Authority hierarchy.** Per-component documentation (Level 2) and per-science documentation (Level 3) may *extend* a glossary term's definition — adding detail, constraints, or specifications relevant to that component or science. Per-component documentation must not *contradict* the glossary's definition. If contradiction arises, it is a documentation bug that must be resolved: either the glossary is updated or the component documentation is corrected. The resolution hierarchy is: specific per-component definitions extend the glossary; the glossary provides the canonical baseline; where neither covers a term, the no-inference rule applies — implementers stop and ask.

**Scope of inclusion.** This glossary defines terms that are used across multiple sections of this specification or across multiple components of the application. Terms used only within a single component's specification are defined in that component's per-component documentation. When a term migrates from single-component use to cross-component use (i.e., when it begins appearing in multiple component specifications or in this document), it is promoted to this glossary. The glossary is a living section: new terms are added when the application introduces concepts that require cross-component vocabulary.

**Organization.** Terms are grouped into categories for readability. The category groupings are non-normative organizational convenience — a term's meaning is not affected by which category it appears under. Within each category, terms are ordered by conceptual dependency: building blocks are defined before composites that reference them. All terms are equal in authority regardless of category placement.

**Language conventions.** Content that constitutes Islamic scholarly knowledge — excerpt text, entry text, taxonomy node display names — is in Arabic. Structural identifiers — filenames, directory names, code identifiers, configuration keys, log messages, documentation prose — use English or transliterated Arabic. Taxonomy node names in data files (such as tree definitions) are in Arabic because they are Arabic scholarly terms where transliteration would lose precision. Filenames derived from taxonomy node names use a safe encoding scheme defined in per-component documentation. Each glossary entry provides the Arabic term in parentheses where one exists; the English term is the canonical identifier in code and documentation.

**Definition style.** Each glossary entry contains: a definition stating what the term is, any binding invariants that are always true of it, disambiguation from adjacent terms where confusion is likely, and a forward reference to the section or document where the full specification lives. Entries do not contain process specifications, enumerated workflow steps, or implementation-level detail — those belong in the sections and documents they reference.

---

### 2.1 Core Application Ontology

**خزانة ريان (the application)** — defined in §1.1. The complete software system: all processing engines, all library infrastructure, all interfaces. Abbreviated **KR** in code and internal references. Not to be confused with the library, which is the knowledge product the application builds.

**The library** (المكتبة) — defined in §1.1. The persistent, structured knowledge product that the application builds and maintains: science trees, excerpts, entries, source metadata, and coverage data. The library is the product; the engines are machinery that feeds it. Not to be confused with the application, which is the software system that builds and maintains the library.

**The owner** (المالك) — the single user of خزانة ريان. The application is a personal tool built for one person. Design decisions about the library's content, structure, and scholarly priorities serve the owner's scholarly development. Design decisions about software architecture, code organization, and engineering methodology serve the AI agents that build and maintain the application.

---

### 2.2 Processing Architecture

This category defines the application's processing components. The application's work is organized into seven engines, grouped into two major phases separated by the normalization boundary. These engines are conceptual processing responsibilities — distinct concerns with distinct inputs, outputs, and expertise. They are not mandates for specific code organization: a single codebase module may currently implement multiple engines' responsibilities, and may be refactored over time. What matters is that the conceptual boundaries are respected: each engine's responsibility is distinct, and no engine's logic leaks into another's domain.

**Phase 1 — Knowledge Acquisition** encompasses the engines that find, acquire, and prepare knowledge sources for processing. Everything in Phase 1 is source-format-specific: the logic may vary depending on where and how the source material was obtained.

**Phase 2 — Knowledge Understanding** encompasses the engines that extract, organize, and synthesize knowledge from prepared sources. Everything in Phase 2 is source-agnostic: the logic operates on normalized content and does not know or depend on the source's original format or acquisition method.

**The normalization boundary** (حد التطبيع) — the architectural dividing line between Phase 1 and Phase 2. Everything above the boundary (the source engine and normalization engine) is source-format-specific. Everything below the boundary (the passaging, atomization, excerpting, taxonomy, and synthesizing engines) is source-agnostic. The normalization boundary is the single most important architectural constraint in the application: it ensures that adding new source types requires only Phase 1 work, and that the Phase 2 engines never accumulate source-format complexity. No source-format-specific logic, identifiers, structural markers, or assumptions may appear below the boundary. A violation of this boundary is an architectural bug regardless of how convenient it would be. Full specification in §7.

The seven engines, in processing order:

**Source engine** (محرك المصادر) — responsible for discovering, identifying, and acquiring raw knowledge sources. Operates in two modes: autonomous (proactively searching configured repositories for relevant material) and manual (accepting material directly provided by the owner). The source engine's output is a frozen raw source — an immutable copy of the original material. The source engine also maintains the source registry for deduplication and documents source metadata (provenance, author identity, scholarly context, trustworthiness evaluation). Full specification in §7.

**Normalization engine** (محرك التطبيع) — responsible for transforming raw sources from their native format into the application's universal normalized format. Each supported source format has its own normalizer — a module that understands the specific challenges of that format and produces conformant output. Normalization includes both content cleaning (stripping format-specific markup, separating footnotes from main text, handling encoding) and structure discovery (identifying headings, chapters, and the source's internal organizational hierarchy). Normalizer complexity is unlimited and self-contained: a normalizer may be thousands of lines, multi-pass, and LLM-assisted, as long as its output conforms to the universal normalized schema. The normalization engine's output is a normalized package — the artifact that crosses the normalization boundary. Full specification in §7.

**Passaging engine** (محرك التقطيع) — the first Phase 2 engine. Responsible for dividing normalized content into passages — the processing units that downstream engines operate on. Passaging is an intelligent operation: it determines where to segment the normalized text based on content, structure, and processing considerations, creating chunks that are appropriately sized and topically coherent for extraction. Passaging operates on source-agnostic normalized content; it does not know the source's original format. Not to be confused with the normalization engine's structure discovery, which identifies the source's own organizational hierarchy (headings, chapters); passaging creates processing units from that structured content. Full specification in the passaging engine's per-component documentation.

**Atomization engine** (محرك التذرير) — responsible for breaking each passage into its constituent atoms — the smallest indivisible units of text. Each atom is typed (indicating what kind of content it represents) and precisely located within its passage by character offsets. Atomization is LLM-driven: identifying where one type of content ends and another begins requires understanding of the text's meaning and scholarly conventions. Full specification in the atomization engine's per-component documentation.

**Excerpting engine** (محرك الاقتطاف) — responsible for grouping atoms into self-contained excerpts — coherent teaching units that can be independently understood. Grouping is driven entirely by the content: what atoms naturally form a complete, independently understandable treatment of a topic. The taxonomy has zero influence on grouping — you group first (what is a coherent teaching unit?), then place second (where does it belong?). The excerpting engine also enriches each excerpt with the metadata required for self-containment: author identity, scholarly context, source reference, and science-specific metadata. Not to be confused with the atomization engine, which identifies individual atoms; the excerpting engine determines which atoms belong together. Full specification in the excerpting engine's per-component documentation.

**Taxonomy engine** (محرك التصنيف) — responsible for placing excerpts at their correct locations in the library's science trees, managing taxonomy evolution when the tree structure needs to grow more granular, and tracking coverage. Placement is a classification decision requiring understanding of both the excerpt's content and the science tree's structure. The taxonomy engine also detects evolution signals, proposes structural changes, and manages the evolution lifecycle (proposal, validation, human approval, application, rollback). Full specification in §4 (science trees). Quality architecture mechanisms applicable to this engine are in §8.

**Synthesizing engine** (محرك التوليف) — responsible for generating entries (encyclopedic articles) from the excerpt collections at each leaf, and for managing entry lifecycle (staleness detection, regeneration). The synthesizing engine is architecturally distinct from the other Phase 2 engines (passaging, atomization, excerpting, taxonomy) — it reads the library's stored excerpts, not the pipeline's intermediate processing artifacts. Full specification in §6.

**Source-agnostic** (لا يعتمد على المصدر) — a property of all Phase 2 engines. A component is source-agnostic when it contains no logic that depends on or varies based on the source type, source format, or acquisition method that produced its input. Source-agnostic components operate identically regardless of whether their input originated from a book, a web article, a recorded lecture, or manual input. Not to be confused with science-agnostic.

**Science-agnostic** (لا يعتمد على العلم) — a property of the core extraction logic (passaging, atomization, excerpting). These engines' core processing algorithms do not change based on which Islamic science the content belongs to. Science-specific behavior is confined to metadata extensions (what additional metadata a particular science requires on its excerpts) and placement classification (which science tree an excerpt belongs to), not to the extraction algorithms themselves. The taxonomy engine is science-aware in its placement decisions but science-agnostic in its structural operations (evolution mechanics work the same for any science tree). The synthesizing engine is science-aware: it reads Level 3 per-science documentation (§13.1) for school handling, entry structure, and scholarly conventions specific to each science.

**Human gate** (بوابة بشرية) — a checkpoint where the application pauses and requires the owner's explicit approval before proceeding with a high-impact action — one that, if incorrect, would introduce errors into the library that may be difficult to detect after the fact. Human gates are bidirectional: the owner reviews the application's proposed actions, and the application intelligently validates the owner's inputs and decisions (per §1.9, mutual verification). Human gates exist at multiple points in the processing pipeline; the specific gate locations and their review protocols are defined in the per-component documentation for each engine. Full specification in §8.

**Multi-model consensus** (إجماع متعدد النماذج) — the mechanism by which multiple LLMs independently process the same input and their outputs are compared to detect errors and increase confidence. Agreement increases confidence; disagreement triggers investigation or escalation to a human gate. Consensus is applied to precision-critical content decisions (extraction, placement, evolution proposals) where the cost of an undetected error is high. It is not applied to mechanical operations where algorithmic validation suffices. Full specification in §8.

**Feedback loop** (حلقة التغذية الراجعة) — the general pattern by which corrections at human gates are saved, analyzed for patterns, and used to improve the application's future decisions. Specific feedback loops exist at each human gate point, each targeting the rules and prompts of the engine whose output was corrected. The scope of "improvement" is precisely bounded: the application's rules improve (prompt templates, extraction definitions, classification heuristics). Feedback loops do not involve LLM fine-tuning, autonomous architectural changes, or modifications to this specification. Full specification in §8.

**Gold baseline** (خط أساس ذهبي) — a hand-crafted, human-verified extraction output for a specific passage, serving as ground truth for regression testing. Gold baselines are created through meticulous manual work and represent the definitive correct extraction for their passage. They are used to detect quality regressions when system rules or models change. Gold baselines are never auto-generated.

**Regression testing** (اختبار الانحدار) — the process of re-running extraction on passages with known-correct outputs (gold baselines or previously approved extractions) after any system rule or model change, to verify that the change does not degrade extraction quality. Regression testing is a mandatory gate before any system rule change is applied to production. Not to be confused with general unit testing, which validates code correctness; regression testing validates content quality against established ground truth.

---

### 2.3 The Science Trees

**Science** (علم, plural: علوم) — a distinct scholarly discipline that constitutes an independent field with its own established corpus of dedicated works, its own internal structure, and its own scholarly tradition. Each science that the library covers receives its own science tree. Sciences are classified into two tiers per §1.2: primary sciences (Islamic and Arabic scholarly disciplines, receiving full treatment) and supporting sciences (non-Islamic disciplines included for their relevance to primary sciences, receiving secondary treatment). The determination of whether a candidate discipline qualifies as an independent science — rather than a chapter within a broader science — requires dedicated scholarly research per candidate. Criteria for this determination and the current inventory of recognized sciences are in §4.

**Science tree** (شجرة العلم) — the hierarchical taxonomy for one science, used by the library to organize and locate knowledge within that science. A tree data structure with exactly one root, any number of intermediate branches, and leaves at the terminal positions. Each science has exactly one active science tree at any time. Science trees are living structures: they evolve as new knowledge reveals finer topic distinctions that the current structure does not capture. The physical representation of science trees (file format, storage mechanism) is an implementation decision specified in per-component documentation; the glossary defines the logical structure only. Full specification in §4.

**Root** (الجذر) — the single top node of a science tree, named after the science. Every science tree has exactly one root. The root has no parent. For primary sciences, the root's name is the science's standard Arabic scholarly name. For supporting sciences, naming conventions are determined when the supporting science's tree is created and documented in Level 3 per-science documentation.

**Branch** (فرع, plural: فروع) — an intermediate node in a science tree. A branch has exactly one parent (the root or another branch) and one or more children (other branches or leaves). Branches group related topics into a navigable hierarchy. Different sciences may have different natural depth structures — a branch at depth 2 in one science's tree is not inherently comparable to a branch at depth 2 in another's. Per-science documentation (Level 3) may define science-specific level names as non-normative conventions within that science's tree. *[Non-normative example: in Fiqh, levels might conventionally correspond to كتاب, باب, فصل — but these are conventions within Fiqh's documentation, not universal tree vocabulary.]*

**Leaf** (ورقة, plural: أوراق) — a terminal node in a science tree. A leaf has exactly one parent (a branch or, in rare cases, the root) and has no children. Leaves are the locations where excerpts are placed and entries are generated. Each leaf represents one granular topic — the finest level of distinction that the tree currently captures for that area of the science. Any leaf may become a branch through taxonomy evolution when the content it covers is found to contain distinguishable sub-topics.

**Structural rules for science trees.** Excerpts are placed only at leaves — never at branches or the root. Entries are generated only at leaves (or at school-groups within leaves, per §2.4). Branches serve as structural groupings; they do not directly hold knowledge content. Every branch has at least one child. Every node is reachable from the root. These rules are binding on tree construction and evolution.

**Node** (عقدة) — a collective term for any position in a science tree: the root, any branch, or any leaf. "Node" is used when a statement applies equally to all structural types. When the node type matters, the specific term (root, branch, leaf) is always used. "Node" is never used when the type is known and relevant.

**Path** (المسار) — the sequence of nodes from the root to a given node, representing that node's full location within its science tree. A path uniquely identifies a node within a specific tree version; paths may change across evolution events (when the tree's structure changes). Stable identification across tree versions, if needed, requires the combination of path and tree version, or a stable node identifier — the choice of identifier strategy is specified in per-component documentation. The notation protocol for referencing nodes in documentation and communication is: `science::segment/segment/.../segment`, where the science name is followed by the path segments separated by `/`. *[Non-normative example: `الفقه::العبادات/كتاب الصلاة/باب صلاة الجماعة`.]*

**Tree version** (إصدار الشجرة) — a specific snapshot of a science tree's structure at a point in time. Every structural modification to a tree (through evolution or restructuring) creates a new version. Previous versions are retained for rollback, reproducibility, and audit. The version history allows for both incremental evolution (leaf splits) and major restructuring when the tree's fundamental organization needs correction. The one-tree invariant means there is never ambiguity about which tree version is current for a given science — not that the tree can only grow incrementally and never restructure.

**Evolution** (التطور) — the process by which a science tree's structure changes to better match the knowledge it organizes. The most common form of evolution is leaf-to-branch conversion: a leaf is found to cover distinguishable sub-topics, so it becomes a branch with new, finer leaves beneath it. Evolution may also involve branch restructuring when the tree's organization at higher levels needs correction. Evolution is LLM-driven, multi-model validated, human-gated, and fully reversible. Evolution never destroys or modifies excerpt content — it is purely a structural operation that may relocate excerpts within the tree. Full specification in §4.

**Evolution signal** (إشارة تطور) — any indication that a science tree's current structure is insufficiently granular or incorrectly organized for the knowledge it contains. *[Non-normative: the most common signal is when multiple excerpts at the same leaf cover distinguishably different sub-topics, suggesting the leaf should be split. Other signals may be identified in per-component documentation.]* An evolution signal initiates the evolution process; it is not an automatic trigger. The detection, evaluation, and response to evolution signals are specified in the taxonomy engine's per-component documentation.

---

### 2.4 Knowledge Content

**Atom** (ذرة, plural: ذرات) — the smallest indivisible unit of text within a passage, typed and located by character offsets. Atoms are the building blocks from which excerpts are composed. Each atom has a type indicating what kind of content it represents and precise character offsets locating it within its passage. Atoms are intermediate processing units — they exist during extraction but are not stored in the library as independent entities. **Atomization** is the process by which the atomization engine breaks a passage into its constituent atoms. Not to be confused with excerpts, which are composed of multiple atoms grouped into self-contained teaching units. The type taxonomy for atoms and the rules governing atomization are specified in the atomization engine's per-component documentation.

**Excerpt** (مقتطف, plural: مقتطفات) — a self-contained unit of knowledge extracted from a source, attributed to a specific author or scholar, and classified to a specific leaf in a science tree. Self-containment is the defining property: an excerpt carries everything needed for both a human reader and the synthesizing engine to fully understand what it teaches, who said it, from which scholarly tradition, and where it fits in the structure of the science. An excerpt that requires another excerpt to be understood, or that lacks attribution, is not self-contained and must be enriched before it can enter the library.

Excerpts have a lifecycle with distinct stages. A **draft excerpt** is the output of the excerpting engine — extracted, enriched with metadata, and assigned a proposed leaf, but not yet reviewed. A **reviewed excerpt** has passed human gate review and been approved. A **placed excerpt** has been accepted into the library at its assigned leaf, is discoverable when the leaf is accessed, is included in entry generation and coverage metrics, and is part of the library's permanent knowledge base. The transition from reviewed to placed is executed by the taxonomy engine, which writes the excerpt to its assigned location in the library (§13.2.6). The unqualified term "excerpt" refers to the concept across all lifecycle stages; where the stage matters, the qualified term (draft, reviewed, placed) is used. The full lifecycle specification, including what metadata an excerpt must carry and the criteria for self-containment, is in §5 and in the excerpting engine's per-component documentation.

**School** (مذهب, plural: مذاهب) — a scholarly tradition or methodological approach within a science that produces systematically different positions on topics. Schools are the primary organizing principle for knowledge within a leaf: at a leaf where the science has schools, the content is organized by school so that each school's positions are clearly visible and never mixed with another school's positions. The tree is structured by topic; the school structures the content within each topic. School is not a branching factor in the tree — it is metadata on the excerpt and an organizing principle within the leaf.

Not every science has schools. Determining which sciences have schools, which schools exist within each science, and how school affiliation is assessed for individual authors and texts is part of the Level 3 per-science research. School affiliation is not always a simple, stable attribute of an author — a single author may represent different schools on different topics or at different points in their career. The school metadata on an excerpt represents the scholarly tradition reflected in that specific text, not necessarily the author's lifelong affiliation. *[Non-normative examples: in Fiqh, well-known schools include الحنفية, المالكية, الشافعية, الحنبلية, and الظاهرية. In عقيدة: الأشاعرة, الماتريدية, أهل الأثر. In نحو: البصريون, الكوفيون, البغداديون. These examples are non-exhaustive — the full school inventory per science is in Level 3 documentation.]*

**Scholarly position** (موقف علمي) — any distinct opinion on a topic, whether it represents an entire school's established position, a dissenting view within a school, or an individual scholar's unique opinion. Scholarly positions are the broadest concept of "what a scholar thinks about a topic." Schools are one level of this; intra-school disagreements and individual opinions are others. The entry at a leaf is responsible for presenting all scholarly positions — not just school-level ones. Within a school-group's entry, intra-school disagreements and individual positions are documented with full attribution. The tree does not branch by individual scholarly position; positions are captured in entries, not in tree structure.

**School-group** (مجموعة المذهب) — the subset of placed excerpts at a leaf that belong to a single school. Where a science has schools, the school-group is the unit of entry generation: each school-group with excerpts at a leaf receives its own dedicated entry. The school-group concept exists to enforce the architectural rule that each school's entry is generated exclusively from that school's excerpts and that schools are never mixed within an entry. Not to be confused with the school itself (the scholarly tradition); a school-group is a structural partition of a specific leaf's excerpt collection.

**Entry** (مدخل, plural: مداخل) — a synthesized encyclopedic article at a leaf, generated by the synthesizing engine from the leaf's excerpt collection. Entries are a primary knowledge product of the library alongside excerpts (per §1.6). Each entry has two layers: the **factual layer**, which faithfully represents all positions, attributions, and evidence present in the source excerpts and is fully traceable to specific excerpts; and the **analytical layer**, which is the synthesizing engine's intellectual contribution — drawing connections between positions, explaining disagreements, contextualizing opinions, and structuring the material for comprehension. The analytical layer may vary across regenerations; this is expected and acceptable.

Entry cardinality: where a science has schools, each school-group at a leaf with excerpts gets its own entry. Where a science has no schools, the leaf has a single entry. Entries are generated only at leaves that have at least one verified excerpt. Leaves with zero verified excerpts have no entry. The primary entry is generated from the verified excerpt set. The analytical layer may reference flagged content for scholarly context (noting the existence of rejected positions and explaining why they are rejected), but the factual layer is generated exclusively from verified excerpts. Where flagged excerpts exist at a leaf, a separate critical analysis section may be generated to address them directly — structurally separate from the primary entry and clearly marked. Full specification in §6.

Entries become stale when their underlying excerpt collection changes (new excerpts added, excerpts removed or relocated due to evolution, excerpt metadata corrected, excerpts reclassified between verified and flagged). The application tracks staleness and flags affected entries for regeneration. Not to be confused with excerpts, which are the factual building blocks; entries are the synthesized scholarly product built from those building blocks.

**Content type** — a metadata classification on atoms and excerpts indicating what kind of scholarly content they represent (such as definitions, rules, examples, evidence, commentary). Content type is metadata — it is not a branching factor in the science tree. The tree branches by topic only. Content type may be used for filtering and display organization within a leaf, but it does not create structural divisions in the tree. The specific content type taxonomy is defined in the atomization engine's per-component documentation.

**Verified knowledge** (معرفة موثقة) — excerpts that have been classified as reliable, scholarly, and trustworthy. Verified knowledge is the primary content of the library: it is what the owner studies from, what primary entries are generated from, and what coverage metrics measure. The verified/flagged classification is a property of each individual excerpt, not only of its source. A source's trustworthiness evaluation (see §2.5) sets the default classification for all its excerpts, but individual excerpts may be reclassified — a verified source may yield individually flagged excerpts if content-level issues are detected, and the owner may override any classification. Not to be confused with flagged knowledge, from which it is structurally separated at every level of the library.

**Flagged knowledge** (معرفة مُعلَّمة) — excerpts that have been classified as unreliable, erroneous, heterodox, or otherwise untrustworthy. Flagged knowledge is structurally isolated from verified knowledge in storage, display, and synthesis. Each flagged excerpt carries a flag reason explaining why it was flagged. Flagged knowledge is retained for educational value — understanding incorrect positions is a recognized scholarly method. Flagged excerpts are never interleaved with verified excerpts, are never counted in primary coverage metrics, and are never included in the factual layer of entries. The separation between verified and flagged knowledge is absolute and enforced at every level of the application.

**Coverage** (التغطية) — a multi-dimensional measurement of how well a leaf, branch, tree, or the entire library is populated with verified excerpts. Coverage is the library's primary diagnostic tool — it tells the owner where knowledge is deep and where gaps exist, enabling targeted study and source acquisition. Coverage metrics measure verified knowledge only. Separately, the application tracks flagged content presence as a diagnostic metric — flagged presence is never combined with verified coverage but is visible as an independent indicator (e.g., "this leaf has rich verified coverage and also has flagged excerpts pending review"). The specific dimensions of coverage measurement and the criteria for classifying gaps are specified in the taxonomy engine's per-component documentation (Level 2).

**Preponderant opinion** (الراجح) — a scholar's own considered judgment on which position is most likely correct when multiple positions exist on a topic. الراجح is captured in excerpt metadata (which scholar considers which position الراجح, with their reasoning) and surfaced in entries. The library does not declare a universal الراجح — it records which scholars hold which position to be الراجح and presents this transparently. The term's applicability varies by science: it is most established in Fiqh and أصول الفقه, but analogous concepts exist in other sciences. Its use for any given science is documented in that science's Level 3 documentation.

---

### 2.5 Sources and Acquisition

**Source** (مصدر, plural: مصادر) — any raw piece of knowledge material before it enters the processing pipeline. A source can be a book, a web article, a recorded lecture, the owner's personal notes, or any other container of scholarly content relevant to the library's sciences. "Source" always refers to the raw, unprocessed material — not to the excerpts derived from it.

**Frozen source** (مصدر مجمد) — a source whose content has been cryptographically hashed at acquisition time and whose original file is never modified by any component of the application. Freezing is an integrity guarantee: all processing operates on copies or derived representations, never on the frozen original. Integrity is verifiable by hash comparison. Every source is frozen immediately upon acquisition, before any documentation or processing begins. Not to be confused with the raw source as it exists in the outside world; the frozen source is the application's immutable copy.

**Work** (مؤلَّف) — a shared identifier linking multiple sources that are volumes of the same multi-volume scholarly work. Each volume is a separate source with its own metadata, processing pipeline, and frozen copy, but all volumes of the same work share a work identifier so that the application can track them as a coherent whole. *[Non-normative: classical Islamic works are frequently multi-volume — كتاب الأم is 8 volumes, المغني is 15 volumes. Modeling each volume as a separate source keeps processing granular (volume 3 can be processed independently of volumes 1 and 2) and aligns with how repositories organize them.]*

**Source format** (صيغة المصدر) — the file or data format of a raw source: HTML, JSON, PDF, plain text, audio, video. Source format describes the technical encoding of the material. Not to be confused with source type.

**Source type** (نوع المصدر) — a specific combination of source format, source repository, and acquisition method that characterizes how a particular category of source material is obtained and what normalizer is required. *[Non-normative examples: "Shamela HTML export" is a source type (HTML format, Shamela repository, desktop-export acquisition). "KetabOnline API download" is a different source type (API payload format, KetabOnline repository, API acquisition).]* Each supported source type requires its own normalizer in the normalization engine. Adding a new source type requires only Phase 1 work (building a normalizer); the Phase 2 engines are never modified for a new source type.

**Source repository** (مستودع المصادر) — a known platform, library, or collection that contains relevant scholarly material. The application maintains a registry of known repositories for autonomous discovery. The per-component documentation for the source engine specifies which repositories are supported and how the application interfaces with each. *[Non-normative examples: المكتبة الشاملة (Shamela), KetabOnline, الدرر السنية (dorar.net).]*

**Source metadata** (بيانات المصدر الوصفية) — the structured record documenting everything known about a source: provenance, author identity, scholarly context, trustworthiness evaluation, processing status, and source characteristics. Source metadata is living — it is initially created during source intake and continues to be enriched over the source's lifetime as more information is learned from processing or external research. The full metadata schema is specified in the source engine's per-component documentation.

**Trustworthiness evaluation** (تقييم الموثوقية) — an intelligent assessment of a source's reliability, scholarly credentials, and content quality, performed during source intake, that determines the default verified/flagged classification for the source's excerpts. The evaluation considers the author's standing, the source's scholarly rigor, and the content's quality. When the evaluation is uncertain, it errs on the side of flagging (flagging a reliable source is correctable; verifying an unreliable source contaminates the library). The owner may override any evaluation. Note that trustworthiness evaluation sets the *default* classification — individual excerpts may be reclassified based on content-level issues detected during extraction or cross-validation. Full specification in §7.

**Manual input** (الإدخال اليدوي) — a source acquisition mode in which the owner directly provides knowledge material to the application: personal study notes, written reflections, teacher lecture transcriptions, or any other knowledge the owner encounters. Manual input is a source type within the source pipeline architecture — it enters the same pipeline as autonomous sources (source engine → normalization engine → Phase 2 engines), using a normalizer specific to its format that produces a normalized package identical in schema to any other normalizer's output. The Phase 2 engines then process it identically to any other source. Manual input excerpts are attributed to the owner (or to the owner's teacher, where applicable). Manual input is presumed reliable — the owner is a trusted source — but is subject to intelligent validation per §1.9 (mutual verification): the application checks for detectable errors such as attribution conflicts or factual inconsistencies with established verified content, and flags concerns for the owner's review. Not to be confused with the processing of manual input, which follows the standard pipeline; manual input is specifically the acquisition mode.

**Normalized package** (الحزمة المطبَّعة) — the complete output of the normalization engine: a set of data conforming to a universal schema that is identical regardless of which source type or normalizer produced it. The normalized package is the artifact that crosses the normalization boundary. The Phase 2 engines only ever see normalized packages — never raw or frozen sources. The specific contents and schema of the normalized package are defined in the normalization engine's per-component documentation. Not to be confused with passages, which are created by the passaging engine from the normalized package's content.

**Passage** (مقطع, plural: مقاطع) — a contiguous segment of normalized source content, created by the passaging engine, that serves as the processing unit for the atomization and excerpting engines. Each passage is appropriately sized and topically coherent for extraction. Passage boundaries are determined by the passaging engine using intelligent analysis of the normalized content — they are not simply pages, paragraphs, or structural divisions from the source. The criteria for determining passage boundaries are specified in the passaging engine's per-component documentation. Passages are source-agnostic processing units — they exist below the normalization boundary.

**Owner confidence level** (مستوى ثقة المالك) — the owner's self-declared familiarity with a science, used by the application to calibrate processing conservatism per §1.9. For sciences where the owner's expertise is lower, the application applies more conservative processing: more flagging, more mandatory human review, explicit "pending expert review" markers. The specific scale and its behavioral implications are defined in the human gate's per-component documentation.

---

*[End of §2. This glossary is a living section — terms are added as the application introduces new cross-component vocabulary, following the scope-of-inclusion rule stated in §2.0.]*

---

## §3 — The Library

§1.1 defines the library (المكتبة) as the persistent, structured knowledge product that the application builds and maintains, distinct from the application itself. §2.1 provides its glossary definition. This section specifies the library's architectural structure: what it contains, what classification rules govern its content, how content is organized within its most granular structural unit (the leaf), how the library changes over time, and how coverage is measured across its hierarchy.

---

### 3.1 Library Contents

The library contains exactly the following categories of persistent data. This inventory is the complete and closed enumeration — no other category of persistent data belongs in the library.

**Science trees** — one per science that the library covers (per §4), including all retained tree versions (per §2.3), mapping the internal organization of that science. The collection of all science trees represents the library's current understanding of the landscape of Islamic and supporting knowledge.

**Placed excerpts** — self-contained knowledge units (as defined in §2.4) that have completed the excerpt lifecycle and been accepted into the library at their assigned leaves. Placed excerpts are the library's factual foundation: entries and coverage data are derived from them.

**Entries** — synthesized encyclopedic articles (as defined in §1.6 and §2.4) generated at populated leaves by the synthesizing engine.

**Source metadata** — living records (as defined in §2.5) documenting every source that has been acquired and processed.

**Coverage data** — metrics measuring how well each level of the library's hierarchy is populated with excerpts (per §3.5).

The library does not contain intermediate processing artifacts. Atoms, draft excerpts, passages, and other transient data produced during engine processing are not part of the library's persistent data.

---

### 3.2 The Verified/Flagged Separation

§2.4 defines verified knowledge and flagged knowledge as the two tiers of the library's content classification. §1.6 and §2.4 specify how the separation applies to entry generation. This subsection specifies the library-wide enforcement rules that make the separation architectural rather than advisory.

**The separation is structural.** The verified/flagged distinction is enforced at every level of the library's infrastructure — in storage, in synthesis, in coverage measurement, and in any future presentation layer. This is not a metadata flag that components may optionally respect; it is a structural partition that every component interacting with the library must enforce. The binding access rule is: any component reading the excerpts at a leaf receives only verified excerpts by default; a separate, explicit access path to flagged excerpts at the same leaf must exist but is never the default. The specific storage layout that realizes this structural separation is defined in the taxonomy engine's per-component documentation (Level 2).

**Mixed classification within a single source.** The verified/flagged classification operates at the individual excerpt level (per §2.4), not only at the source level. This per-excerpt granularity means that the library's storage, synthesis, and coverage systems must support mixed classification within a single source's excerpts — some verified, some flagged — not just per-source classification. An engine that assumes all excerpts from a given source share a single classification is incorrect.

---

### 3.3 Content Organization Within Leaves

Leaves are the library's most granular organizational unit — the locations where excerpts are placed and entries are generated (per §2.3). A leaf's content is structurally partitioned along exactly two dimensions. These two structural partitions are the complete set — they determine how excerpts are grouped for entry generation and storage separation. No other structural partition exists within a leaf. Metadata-based filtering and display ordering within a partition (such as filtering by content type per §2.4) are not structural partitions — they do not affect entry generation boundaries or the verified/flagged access rule defined in §3.2.

**Partition 1: School-group.** Where a science has schools (§2.4), the placed excerpts at a leaf are partitioned into school-groups (§2.4). Where a science has no schools, the leaf's excerpts form a single undivided collection. Entry cardinality follows this partitioning per §1.6.

**Partition 2: Verified/flagged.** Flagged excerpts at a leaf are structurally separate from verified excerpts, per §3.2.

**Interaction between partitions.** The two partitions apply simultaneously. Where school-groups exist, each school-group contains both a verified subset and (potentially) a flagged subset. Entry generation operates within school-group boundaries (per §1.6), and the verified/flagged access rule (per §3.2) applies within each school-group. The storage layout that realizes this two-dimensional partitioning — including nesting order and access path design — is specified in the taxonomy engine's per-component documentation (Level 2). The binding constraints that the storage layout must satisfy are: (a) a school-group's verified excerpts must be efficiently accessible as a unit (for entry generation), (b) all verified excerpts at a leaf must be efficiently accessible across school-groups (for coverage measurement and cross-school study), and (c) the default access path must return only verified excerpts per §3.2.

---

### 3.4 Library Growth and Correction

The library is a living structure that grows and improves through the continuous operation of the application's engines. §1.7 defines the completion model (baseline, rich, library-wide maturity) and establishes that the library is never frozen.

The library grows through new excerpts placed by the taxonomy engine from newly processed sources, whether those sources were autonomously discovered by the source engine or manually provided by the owner. The library's structure evolves through taxonomy evolution managed by the taxonomy engine when content reveals that science trees need greater granularity (§4). The library's study products improve through entry regeneration by the synthesizing engine when excerpt collections change (§6), and through per-engine feedback loops (§2.2) that improve extraction and placement quality over time. Source metadata is enriched over time by the source engine as new information about sources is learned.

The library also changes through corrections: excerpt reclassification between verified and flagged tiers, excerpt relocation to a different leaf, and metadata corrections on placed excerpts. Corrections never remove a placed excerpt from the library — a placed excerpt that is found to be unreliable or erroneous is reclassified as flagged rather than deleted, preserving the library's complete audit trail.

Each growth and correction mechanism operates under the constraint of human gates (§2.2): no high-impact change to the library proceeds without the owner's approval or pre-configured approval policies defined in the human gate's per-component documentation (Level 2).

---

### 3.5 Coverage Hierarchy

Coverage (as defined in §2.4) is the library's primary diagnostic tool. This subsection defines the hierarchical structure of coverage measurement. The specific dimensions measured at each level, the aggregation methods, and the criteria for classifying coverage depth are specified in the taxonomy engine's per-component documentation (Level 2).

Coverage is measured at four hierarchical levels, each aggregating from the level below:

**Leaf-level coverage** is the base measurement unit — how well a single leaf is populated with excerpts, measured across dimensions defined in per-component documentation.

**Branch-level coverage** aggregates the coverage of all leaves beneath a branch, providing a diagnostic view of how well a sub-area of a science is covered.

**Tree-level coverage** aggregates across an entire science tree, providing a diagnostic view of how well the science as a whole is covered.

**Library-level coverage** aggregates across all science trees — the highest-level view of the owner's knowledge landscape.

---

---

## §4 — The Science Trees

§2.3 defines the vocabulary and structural invariants governing all science trees — root, branch, leaf, node, path, tree version, evolution, evolution signal — and defers to this section for the full specification. §1.2 defines the two-tier knowledge scope (primary and supporting sciences). §1.7 describes the bootstrapping cycle between tree construction and source processing. Together, §2.3 and this section constitute the complete specification of science trees: §2.3 provides the definitions and structural invariants; this section provides the science qualification criteria, construction principles, governance invariants for evolution, the relationship between schools and tree structure, and the inventory of sciences the library aims to cover.

**Structural independence.** Each science tree is structurally independent. No node in one tree references, depends on, or is linked to any node in another tree. Cross-science connections exist in excerpt content and metadata (per §1.2's primary classification rule), not in tree structure. This independence ensures that each tree can evolve, restructure, and roll back without affecting any other tree.

---

### 4.1 Science Qualification Criteria

§2.3 defines a science as "a distinct scholarly discipline that constitutes an independent field with its own established corpus of dedicated works, its own internal structure, and its own scholarly tradition" and states that the determination of independence "requires dedicated scholarly research per candidate." This subsection specifies the criteria that the research must evaluate.

**Scope: primary sciences.** The four criteria below govern qualification of primary sciences — the Islamic and Arabic scholarly disciplines defined in §1.2 as the library's core identity. Supporting sciences follow a different identification process described at the end of this subsection.

A candidate discipline qualifies as a primary science — and therefore receives its own science tree — when it meets all four of the following criteria:

**Criterion 1: Dedicated corpus.** The discipline has its own established body of dedicated works — scholars have written books specifically about this discipline, not merely chapters within broader works. Additionally, this corpus must be substantial enough that the discipline's knowledge cannot be adequately represented as a branch within another science's tree. Both conditions must hold: dedicated works must exist, and those works must constitute a corpus that warrants an independent tree.

**Criterion 2: Internal structure.** The discipline has recognized sub-topics, categories, and organizational principles that scholars working within it use to structure their writing and teaching. This internal structure is what the science tree will represent.

**Criterion 3: Scholarly tradition.** There are recognized authorities, foundational texts, and established methodologies within the discipline. The discipline has a history of scholarly engagement distinct from adjacent disciplines.

**Criterion 4: Referential identity.** The discipline could be referred to as "علم [name]" and this would be recognized by Islamic scholars as referring to a specific, distinct field. This is a practical test of whether the scholarly community treats the discipline as independent.

The test is not whether a topic is important, but whether it is an independent discipline. A topic can be critically important yet still be a branch within another science's tree rather than its own science. *[Non-normative example: أسباب النزول is critically important for Quranic understanding, but it is typically a chapter within علوم القرآن books rather than an independent discipline with its own extensive dedicated corpus. It would be a branch within the علوم القرآن tree. Conversely, علم التجويد has its own extensive dedicated corpus, its own internal structure, and its own scholarly tradition — it qualifies as an independent science.]*

The qualification assessment for each candidate that is accepted as a primary science is documented in that science's SCIENCE.md (Level 3 per §13.1), including the evidence considered and the reasoning behind the determination. When a candidate is evaluated and rejected — determined not to qualify as an independent science — the rejection rationale is documented in the SCIENCE.md of the broader science whose tree the candidate will become a branch within. When the assessment is ambiguous — when reasonable arguments exist for both independence and inclusion as a branch — the assessment records the ambiguity and the owner makes the final determination.

**Supporting science identification.** Supporting sciences (§1.2) are not evaluated against the four criteria above — their inclusion is driven by relevance to primary sciences, not by independent disciplinary standing. Supporting sciences are identified as the primary sciences' trees are built: each primary science's SCIENCE.md documents which supporting sciences it requires and why. Each supporting science that is accepted into the library receives its own directory (per §13.2.6) with its own SCIENCE.md documenting its tree structure and which primary sciences it serves.

---

### 4.2 Tree Construction Principles

Building a science tree is one of the most sensitive tasks in the project. A poorly structured tree causes misplaced excerpts, awkward granularity, and a degraded library experience. Tree construction is therefore a dedicated, deeply researched effort per science — it is never done casually or between other tasks. The taxonomy engine's per-component documentation (Level 2) specifies the generic tree construction workflow applicable to all sciences. Each science's SCIENCE.md (Level 3) documents the science-specific application of that workflow — the scholarly sources consulted, the structural decisions made, and the validation results for that specific tree.

The workflow proceeds through four phases, each with a defined output:

*Research phase* — output: an understanding of the science's traditional organizational frameworks, drawn from the structure of its major scholarly works and pedagogical tradition.
*Draft phase* — output: a proposed tree structure encoding that understanding.
*Validation phase* — output: an assessment of whether real scholarly content maps cleanly to the proposed tree (per the content validation principle below).
*Commitment phase* — output: the science's v1.0 tree, versioned and active.

The specific procedures within each phase are specified in the taxonomy engine's per-component documentation (Level 2). The following principles govern the process regardless of procedural specifics.

**Principle: scholarly fidelity.** A science tree's structure must reflect how the science is traditionally organized by its scholars — not an externally imposed classification scheme. The tree is built from research into the organizational frameworks used in the science's major works and pedagogical tradition. *[Non-normative example: a Fiqh tree's structure should reflect how Fiqh books are organized (by كتب and أبواب), not an arbitrary topic grouping invented by the tree builder.]*

**Principle: granularity bias.** Initial tree construction should err on the side of being too granular rather than too coarse. Restructuring overly fine sibling leaves into fewer, broader leaves is a form of evolution (branch restructuring per §2.3) subject to §4.4's governance invariants, but involves only consolidation of closely related excerpts into a broader leaf, not redistribution of excerpts across fundamentally different topics. Splitting overly coarse leaves after excerpts have been placed requires redistribution across different topics and is a more disruptive operation. This asymmetry motivates starting fine.

**Principle: content validation before commitment.** A draft tree must be validated against real scholarly content before it is committed as the science's active tree. The validation tests whether the tree's structure accommodates the content that actual sources in the science contain — whether a typical book's chapters map cleanly to the tree's leaves, whether any content falls between leaves, and whether any leaves are so broad that a single source chapter spans multiple distinguishable sub-topics within the leaf. Mismatches indicate structural problems to resolve before commitment. The specific validation protocol is specified in the taxonomy engine's per-component documentation (Level 2).

**Principle: one committed tree per science.** Once a tree is committed (becoming the science's v1.0), all subsequent structural changes happen through the formal evolution process — not through ad-hoc editing. This ensures that every structural change is versioned, validated, human-gated, and reversible per §2.3's tree version and evolution definitions.

---

### 4.3 Preliminary Science Inventory

The following is a preliminary inventory of sciences that the library aims to cover. This inventory requires dedicated research and validation before it is finalized: for each candidate, the qualification criteria in §4.1 must be evaluated and documented. Sciences may be added, removed, merged, or split during the research phase. The inventory is organized by traditional science family groupings for readability; as established in §2.3, each science is an independent tree — the family groupings are non-normative organizational convenience, not structural relationships in the library.

**Quranic Sciences Family:**
علم التفسير (Quranic exegesis), علم التجويد (Quran recitation rules), علم القراءات (variant Quranic readings), علوم القرآن (Quranic sciences — the broader discipline covering أسباب النزول, الناسخ والمنسوخ, إعجاز القرآن, غريب القرآن, إعراب القرآن, and other sub-disciplines; whether some of these warrant their own trees requires research per §4.1).

**Hadith Sciences Family:**
علم مصطلح الحديث (hadith terminology and methodology), علم الرجال والجرح والتعديل (narrator criticism), علم علل الحديث (hadith defects), علم شرح الحديث (hadith commentary), علم تخريج الأحاديث (hadith verification and source-tracing), علم غريب الحديث (rare vocabulary in hadith).

**Fiqh and Legal Sciences Family:**
علم الفقه (Islamic jurisprudence), علم أصول الفقه (principles of jurisprudence), علم القواعد الفقهية (legal maxims), علم الفرائض والمواريث (inheritance law — may be a branch within الفقه or independent; requires research per §4.1).

**Theology and Creed:**
علم العقيدة / التوحيد (Islamic theology and creed).

**Arabic Language Sciences Family:**
علم النحو (syntax), علم الصرف (morphology), علم البلاغة (rhetoric — المعاني, البيان, البديع), علم الإملاء (orthography), علم العروض والقافية (prosody and rhyme), علم فقه اللغة (philology), علم المعاجم (lexicography), علم الأدب (literature — may be too broad; requires research per §4.1).

**History and Biography:**
علم السيرة النبوية (prophetic biography), علم التاريخ الإسلامي (Islamic history), علم التراجم (biographical dictionaries — may be a branch within التاريخ or independent; requires research per §4.1).

**Ethics, Spirituality, and Conduct:**
علم التزكية والأخلاق (spiritual purification and ethics), علم الآداب الشرعية (Islamic etiquette and conduct), علم الزهد والرقائق (asceticism and heart-softeners).

**Scholarly Methodology:**
علم المنطق (logic as used in Islamic scholarship), علم آداب البحث والمناظرة (scholarly debate methodology), علم الدعوة (methodology of Islamic preaching and education).

This inventory covers primary sciences only. Supporting science identification is described in §4.1.

---

### 4.4 Evolution Governance

§2.3 defines evolution as "the process by which a science tree's structure changes to better match the knowledge it organizes" and establishes its core properties: LLM-driven, multi-model validated, human-gated, fully reversible, and purely structural (never destroys or modifies excerpt content). §2.3 also defines evolution signals as initiating the process without being automatic triggers. This subsection specifies the governance invariants that bind every evolution event — whether leaf-to-branch conversion, branch restructuring, or any other structural change — beyond what §2.3 establishes. The step-by-step evolution workflow — signal evaluation, proposal generation, validation, redistribution, human gate presentation, application or rejection — is specified in the taxonomy engine's per-component documentation (Level 2).

**Invariant: zero orphans.** After any evolution event, every excerpt placed at any leaf within the affected subtree before the evolution must have a valid placement at a leaf in the resulting tree structure. No excerpt may be left without a home. If a proposed evolution cannot achieve zero orphans, the proposal is invalid and must not proceed to the human gate.

**Invariant: excerpt non-interference.** No placed excerpt outside the evolution's scope may be relocated, modified, or invalidated. The evolution's scope is the evolved node and all its descendants in the pre-evolution tree structure. Structural changes to ancestor nodes (such as a parent gaining a branch child where it previously had a leaf child) are an expected consequence of evolution, not an interference violation — the invariant constrains excerpt placement, not tree connectivity.

**Invariant: sibling coherence.** New leaves or branches created by evolution must represent genuinely distinct sub-topics. The operational test: no single excerpt should plausibly belong to more than one sibling. If a reasonable classification of an excerpt's topic could place it at either of two proposed siblings, those siblings overlap, the proposal creates placement ambiguity, and it is invalid. The multi-model validation step must verify sibling coherence using this test.

**Invariant: entry lifecycle propagation.** Evolution affects entries at every leaf whose excerpt collection changes. Two primary scenarios require distinct handling. When a leaf is converted to a branch with new sub-leaves: entries at the pre-evolution leaf are invalidated (the node is no longer a leaf and cannot host entries per §2.3), and each new sub-leaf is queued for initial entry generation once it contains placed excerpts. When evolution relocates excerpts between existing leaves without converting any leaf to a branch: entries at each affected leaf become stale per §1.6 and are flagged for regeneration. In all cases, every leaf in the resulting tree structure that contains verified excerpts and has no current entry is queued for initial entry generation.

**Invariant: rollback completeness.** The fully reversible property stated in §2.3 means that rolling back an evolution event must restore the tree structure and the excerpt placements to their exact pre-evolution state. Rollback must not destroy any placed excerpt — including excerpts that were placed at the evolved leaves *after* the evolution but *before* the rollback. Post-evolution excerpts that cannot be placed in the pre-evolution tree structure must be returned to reviewed status (per the excerpt lifecycle in §2.4) for re-placement by the taxonomy engine. The specific rollback protocol is specified in the taxonomy engine's per-component documentation (Level 2).

---

### 4.5 Schools and Tree Structure

§2.4 establishes that schools (مذاهب) are "the primary organizing principle for knowledge within a leaf" and that "school is not a branching factor in the tree — it is metadata on the excerpt and an organizing principle within the leaf." §3.3 specifies the two structural partitions of within-leaf organization (school-group partitioning and verified/flagged separation). This subsection provides the architectural rationale for these rules and their concrete implications for tree design.

**The tree branches by topic, not by school.** A science tree's structure reflects the science's topical organization. No node in any science tree represents a school. *[Non-normative example: the Fiqh tree has topic branches (كتاب الطهارة, كتاب الصلاة) and topic leaves (أحكام المسح على الخفين). It does not have a الحنفية branch and a الشافعية branch.]*

*[Non-normative — rationale: the primary use case is studying a topic comprehensively. If the tree branched by school, the owner would need to visit separate leaf nodes — one per school — to get the full picture of a single مسألة. This defeats the purpose of a structured library. By keeping the tree topic-structured and organizing schools within each leaf, the owner visits one leaf and sees every school's position on that topic, structured and separated but accessible together for comparison.]*

**Implication for tree construction.** When building a science tree (§4.2), the tree designer must ensure that no proposed node is defined by school affiliation. A node like "الحنفية في الطهارة" is architecturally invalid — it conflates topic and school. The correct structure places "الطهارة" nodes in the tree and partitions content within those nodes by school per §3.3.

**Implication for evolution.** When the taxonomy engine proposes evolution (splitting a leaf into finer leaves), the proposed sub-leaves must represent topical distinctions, not school-based distinctions. A leaf that contains excerpts from four different schools on the same sub-topic does not need evolution — the schools are handled by within-leaf partitioning. A leaf that contains excerpts about genuinely different sub-topics (regardless of which schools discuss them) may need evolution.

---

### 4.6 Tree Physical Representation

The physical representation of science trees — file format, storage location, encoding of node names, marking of leaf versus branch nodes, and the mechanism for tracking tree versions — is an implementation decision. These details are specified in the taxonomy engine's per-component documentation (Level 2), subject to the logical structure and invariants defined in §2.3 and this section. The repository location for science tree storage is specified in §13.2.6.

---

---

## §5 — The Excerpt

§2.4 defines the excerpt as a self-contained unit of knowledge extracted from a source, attributed to a specific author or scholar, and classified to a leaf in a science tree. §2.4 establishes self-containment as the defining property, specifies the three lifecycle stages (draft, reviewed, placed), and forward-references this section for the full specification of what metadata an excerpt must carry and the criteria for self-containment. This section provides that specification: the concrete requirements that make an excerpt self-contained, the architectural rules governing excerpt creation and boundaries, the relationship between universal and science-specific metadata, and the one-excerpt-per-source-per-leaf diagnostic.

This section defines _what_ an excerpt must be and _what constraints_ govern its creation. It does not define the processing logic by which engines create excerpts — those details are in the per-component documentation (Level 2) for the atomization, excerpting, and taxonomy engines. Manual input (§2.5) produces excerpts through the same pipeline as any other source; the requirements and rules in this section apply equally to all excerpts regardless of source type.

---

### 5.1 Self-Containment Requirements

Self-containment is the excerpt's defining property (§2.4). This subsection specifies what self-containment concretely requires: the metadata fields that every excerpt must carry, the standard against which self-containment is evaluated, and the text integrity invariant that governs the excerpt's primary content.

**Self-containment standard.** An excerpt is self-contained when, given the excerpt itself and the source metadata it references (§2.5), a reader with general familiarity with the science's core concepts and standard terminology can fully understand what the excerpt teaches, who said it, from which scholarly tradition, and where it fits in the structure of the science. The standard is independence from other excerpts in the library, not independence from all prior domain knowledge. _[Non-normative example: an excerpt about أحكام المسح على الخفين need not define وضوء; it must be understandable without consulting another excerpt in the library.]_ Where a science's Level 3 documentation (SCIENCE.md, per §13.1) specifies a more precise reader competence level for that science, the Level 3 specification governs.

An excerpt that fails this standard — that requires another excerpt to be understood, or that lacks attribution, or whose scholarly context is absent — must be enriched before it can proceed through the lifecycle (§2.4).

**Required metadata.** The following metadata categories constitute the complete universal set. A fully-formed excerpt — one that has completed processing by the excerpting and taxonomy engines and is ready for human review — carries all of them. During the creation pipeline, fields may be populated at different stages by different engines: the excerpting engine populates content-derived and source-derived fields; the taxonomy engine assigns topic context during placement classification. Science-specific extensions (§5.4) add fields beyond this universal set.

**Primary text** — the complete Arabic text of the excerpt, reproduced verbatim from the frozen source (§2.5), preserving whatever diacritical marks the source text contains. Diacritics are neither stripped from nor added to the primary text. **The text integrity invariant: no component of the application may modify the primary text under any circumstances.** If the frozen source contains textual corruption (OCR artifacts, encoding errors), the corruption is preserved in the primary text. An excerpt whose primary text is corrupted to the point of materially affecting comprehension is flagged, with the flag reason describing the corruption. The correction path for corrupt source text is to acquire a better source copy and reprocess. If no better source copy is available, the owner may create a manual input excerpt (§2.5) containing the corrected text; the corrupted excerpt remains flagged.

**Derived normalized text** — a computationally processed version of the primary text, used for search, matching, and deduplication. The derived text exists alongside the primary text; it is never a replacement. The normalization operations applied to the derived text (diacritic handling, character normalization, whitespace standardization) are specified in the relevant per-component documentation (Level 2). No processing operation may modify the primary text; all computational text manipulation operates on the derived text.

**Author identification** — the author's canonical name as recorded in the source metadata (§2.5) for this excerpt's source. Detailed author information — biography, dates, geographic origin, era — is maintained in source metadata and is accessible through the excerpt's source reference. The excerpt identifies its author; it does not redundantly carry full author biographical data. If the library introduces a cross-source author registry in the future, that is a separate design consideration not specified here.

**School** — the scholarly tradition reflected in this specific text, where the science has schools (§2.4). School metadata is conditionally required: required for sciences that have schools (as determined by Level 3 per-science documentation), absent for sciences that do not. School affiliation on an excerpt represents the tradition reflected in that specific text, which may differ from the author's lifelong affiliation (§2.4). Where the science has no schools, this field is absent, not empty.

**Source reference** — a stable reference to the frozen source (§2.5) from which this excerpt was extracted, including location information sufficient to find the original text within the source (such as page number, chapter, or section, where applicable). The source reference is part of the self-containment mechanism: it connects the excerpt to the full source metadata record, which carries author biography, trustworthiness evaluation, and provenance. Self-containment is achieved through the excerpt's own fields _plus_ the source metadata accessible through this reference.

**Topic context** — the leaf path in the science tree where this excerpt is classified. For draft excerpts, this is the proposed leaf; for placed excerpts, the confirmed leaf (per §2.4's lifecycle stages). The topic context tells a reader exactly where this knowledge fits in the structure of the science.

**Content type** — a metadata classification indicating what kinds of scholarly content the excerpt contains (such as definitions, rules, examples, evidence, commentary), as defined in §2.4. The specific content type taxonomy is defined in per-component documentation (Level 2).

**Verified/flagged classification** — the excerpt's current classification per §2.4 and §3.2. Initially set from the source's trustworthiness evaluation (§2.5), which provides the default classification for the source's excerpts. Individual excerpts may be reclassified based on content-level issues detected during processing or at human review.

---

### 5.2 Excerpt Creation: Architectural Rules

Excerpt creation spans multiple engines (§2.2): the atomization engine identifies atoms within passages, the excerpting engine groups atoms into self-contained excerpts and enriches them with metadata, and the taxonomy engine places them at leaves. The processing details of each engine are specified in their respective per-component documentation (Level 2). This subsection specifies the architectural rules that govern the creation process from above — rules that bind the engines without specifying their internal logic.

**The taxonomy-independence rule.** Grouping atoms into excerpts is driven entirely by content — what atoms naturally form a complete, independently understandable treatment of a scholarly point or closely related set of points. The taxonomy has zero influence on grouping. The excerpting engine groups first (what is a coherent, self-contained excerpt?), then the taxonomy engine places second (where does this excerpt belong in the tree?). An excerpt's boundaries are never adjusted to fit a leaf's scope, and a leaf's definition never influences how the excerpting engine draws excerpt boundaries. A violation of this rule is an architectural bug.

**The completeness criterion.** A group of atoms constitutes a self-contained excerpt when it collectively provides a complete, independently understandable treatment — where "complete" means the treatment does not trail off mid-argument, omit the conclusion of a logical chain the author began, or leave a scholarly point half-stated, and "independently understandable" means a reader meeting the self-containment standard (§5.1) can understand what is being taught. Completeness is evaluated against the content itself, not against the taxonomy. The completeness criterion defines the minimum scope of an excerpt (it must not be incomplete). The maximum scope is not hard-bounded by this criterion alone; the one-excerpt-per-source-per-leaf diagnostic (§5.5) provides a soft upper signal — an excerpt covering multiple distinguishable sub-topics within a leaf is a signal for either splitting the excerpt or evolving the leaf.

**The passage containment rule.** Each excerpt is derived from atoms within a single passage. An excerpt cannot span passage boundaries. This constraint places a critical responsibility on the passaging engine: passage boundaries must not split content that constitutes a single self-contained excerpt. When a passage boundary falls within what should be a single excerpt, the result is a truncated or incomplete excerpt that fails the completeness criterion. Detection and handling of such passaging errors are specified in the passaging engine's per-component documentation (Level 2).

**The enrichment dependency.** Excerpt enrichment — populating the metadata fields specified in §5.1 — draws on three inputs: (1) the content itself (for content-derived metadata such as content type), (2) source metadata from §2.5 (for author identification, school, and source reference), and (3) the applicable science's metadata specification from Level 3 documentation (for determining which science-specific fields to populate per §5.4). This means the excerpting engine must have access to source metadata for the source being processed and must have access to the metadata specification for the relevant science. The data path by which source metadata and science metadata specifications reach the excerpting engine — whether carried through the pipeline's schema contracts or accessed via separate channels — is specified in the excerpting engine's per-component documentation (Level 2) and, where it affects inter-engine boundaries, in the relevant schema contracts (§13.4).

---

### 5.3 Excerpt Boundaries and Cross-Topic Content

The taxonomy-independence rule (§5.2) governs not only initial grouping but also boundary decisions when source content spans multiple topics. The following rules define how the excerpting and taxonomy engines handle cross-topic content. These rules are binding architectural constraints, not engine-internal logic.

**Rule 1: Context mentions are retained.** When an outside topic — a topic that has its own node elsewhere in the tree — is mentioned within an excerpt as supporting context (a brief repetition of prerequisite knowledge, a reference, a comparison), the mention stays within the excerpt. This is normal scholarly writing. The excerpt remains a single unit. The taxonomy engine places it at the leaf of its primary topic, where primary topic is determined by the excerpt's teaching intent — what the excerpt exists to teach, not which topic occupies more text or which topic the source's chapter heading names. The criteria for determining primary topic are specified in the taxonomy engine's per-component documentation (Level 2). Context mentions within an excerpt are not captured in separate cross-reference metadata — the excerpt's topic context reflects its primary topic only. Discovery of context mentions across the library is a function of search over excerpt text, not of metadata-based navigation. Formal cross-reference infrastructure between science trees is a future consideration (§1.2).

**Rule 2: Extensive independent treatments may be split.** When an outside topic is treated extensively and independently within the same text — to the degree that the treatment constitutes a self-contained excerpt on its own — the excerpting engine evaluates whether the text can be split into two self-contained excerpts without corrupting either. "Corrupting" means: removing the outside-topic portion would make the remaining text incomprehensible or incoherent, or the outside-topic portion cannot stand alone as a self-contained excerpt meeting §5.1's standard, or both. Three outcomes are possible:

(a) Both portions are self-contained after separation — the excerpting engine produces two draft excerpts, and the taxonomy engine places each at its appropriate leaf independently.

(b) The primary-topic portion is self-contained after separation, but the outside-topic portion is not — the excerpting engine produces one excerpt from the self-contained portion; the non-self-contained outside-topic portion does not produce a separate excerpt.

(c) Neither portion is self-contained after separation, or the primary-topic portion loses coherence — the excerpting engine produces a single excerpt containing the full text, and the taxonomy engine places it at the primary topic's leaf per Rule 3.

**Rule 3: Content integrity takes absolute priority over taxonomic precision.** An excerpt that covers two topics but is self-contained is always preferable to two broken excerpts that each require the other to make sense. When the excerpting engine cannot produce self-contained excerpts from a multi-topic text, the text remains a single excerpt. No amount of taxonomic benefit justifies breaking an excerpt's self-containment. This rule overrides all other considerations about excerpt boundaries.

---

### 5.4 Science-Specific Metadata Extensions

The metadata requirements in §5.1 are universal — every excerpt in every science carries them. Individual sciences may require additional metadata fields beyond the universal set, driven by the science's scholarly conventions and the kind of content it produces. These science-specific extensions do not change the universal definition — they add requirements on top of it.

**The extension pattern.** Each science's Level 3 documentation (SCIENCE.md, per §13.1) specifies what additional metadata fields that science's excerpts require, what values those fields accept, and what criteria determine their values. VISION.md establishes the pattern; Level 3 documentation provides the per-science substance. The universal metadata (§5.1) plus a science's Level 3 extensions constitute the complete metadata specification for that science's excerpts.

_[Non-normative — illustrative examples of the kinds of extensions that Level 3 documentation may specify: a Fiqh science would typically include الراجح metadata (which scholars consider which position preponderant, per §2.4), دليل references (which evidence the author cites), and indication of whether the author discusses multiple schools' positions. A تفسير science would typically include آية references identifying which verses are being discussed and the exegetical methodology employed. A مصطلح الحديث science would typically include identification of which technical term or classification methodology is under discussion. These examples are non-exhaustive and non-normative — the authoritative requirements for each science are in that science's SCIENCE.md.]_

---

### 5.5 The One-Excerpt-Per-Source-Per-Leaf Diagnostic

As a quality diagnostic (not a hard constraint), the application prefers at most one excerpt from any given source at any given leaf. When the taxonomy engine detects during placement that a second excerpt from the same source is being proposed for the same leaf, this condition is a diagnostic signal indicating that one of two situations may apply:

**The excerpts may need merging.** If the two excerpts cover the same sub-topic (expressed in two separate parts of the source), they may be candidates for merging into a single, coherent excerpt. The merge evaluation applies the same self-containment and coherence criteria as the split evaluation in §5.3: if merging would produce an incoherent excerpt (because the two text segments were written in unrelated contexts within the source), the merge is not safe and the excerpts remain separate. Merge evaluation uses the excerpting engine's criteria (content coherence, self-containment).

**The leaf may need evolution.** If the two excerpts cover distinguishably different sub-topics within the leaf's current scope, this is an evolution signal per §2.3 — the leaf may be too coarse and may need to split into finer leaves. Evolution evaluation uses the taxonomy engine's criteria (§4.4).

**Interaction with §5.3's cross-topic rule.** An excerpt placed at a leaf due to the cross-topic content integrity rule (§5.3, Rule 3 — a multi-topic excerpt that could not be safely split) is not counted as a duplicate for this diagnostic, since its presence at the leaf was driven by content integrity rather than topical match.

**Not a rejection criterion.** This diagnostic does not block placement. Legitimate cases exist where a single source produces two excerpts at the same leaf (e.g., the source discusses the same sub-topic in two unrelated sections, and the excerpts cannot be coherently merged). The diagnostic flags these cases for review per the human gate architecture (§2.2) rather than automatically rejecting them. The specific detection logic, the mechanism by which merge and evolution evaluations are triggered, and how results are presented at the human gate are specified in the taxonomy engine's and excerpting engine's per-component documentation (Level 2).

---

---

## §6 — The Entry (Synthesis)

§1.6 establishes the entry as a primary knowledge product of the library alongside excerpts — the owner's primary study artifact, from which knowledge is memorized and taught. §2.4 defines the entry's vocabulary: two layers (factual and analytical), cardinality rules (per school-group where schools exist, single where they do not), staleness triggers, and the verified/flagged separation governing entry generation. §5 specifies the excerpts that serve as the entry's factual foundation. This section specifies the entry's architectural identity at full depth: what an entry is and what it is not, how entries are structured at a leaf, when entries become stale and how staleness is resolved, and the quality bar that entries must meet.

This section defines _what_ an entry must be and _what constraints_ govern its generation and lifecycle. It does not define the generation logic — prompt design, structuring algorithms, quote selection heuristics, or formatting rules. Those details are in the synthesizing engine's per-component documentation (Level 2).

---

### 6.1 What an Entry Is

An entry (مدخل) is a synthesized encyclopedic article at a leaf (or at a school-group within a leaf), generated by the synthesizing engine (محرك التوليف) from the leaf's placed, verified excerpt collection. The entry is the library's primary study product: the artifact the owner reads, memorizes, and teaches from. The quality of entries directly determines the quality of the owner's scholarship.

**Entries are not summaries.** An entry is more than a condensation of its source excerpts. Each entry comprises two distinct layers, defined in §2.4:

The _factual layer_ faithfully represents every scholarly position, attribution, and piece of evidence present in the verified excerpts at the leaf (or school-group). Every factual claim in the entry must be traceable to one or more specific excerpts. The factual layer adds nothing that the excerpts do not contain — it is a faithful, comprehensive representation of the excerpt collection's content.

The _analytical layer_ is the synthesizing engine's intellectual contribution. It draws connections between positions that no single excerpt states, explains why disagreements exist between scholars, contextualizes opinions within the broader scholarly tradition, structures the material for comprehension and study, determines when to quote a scholar directly (for memorization value) versus when to paraphrase, and provides further clarification where the excerpts alone would leave gaps for a student. The analytical layer is what makes an entry more than the sum of its excerpts — it is the synthesized scholarly reasoning that transforms a collection of individual positions into a coherent, navigable treatment of the topic.

The analytical layer may vary across regenerations: the synthesizing engine may draw different connections, choose different organizational structures, or emphasize different aspects when regenerating from the same excerpt collection. This variability is expected and acceptable — the analytical layer represents the synthesizing engine's best current scholarly reasoning, not a fixed artifact. The factual layer, by contrast, must remain faithful to the excerpt collection regardless of regeneration.

**Relationship to excerpts.** Excerpts (§5) are the factual foundation; entries are the scholarly product. An entry without excerpts cannot exist — there is nothing to synthesize. Excerpts without entries are usable (the owner can read individual excerpts) but do not provide the comprehensive, structured overview that is the library's primary study experience. Both are co-primary knowledge products of the library (§1.6): excerpts provide granular, attributed, source-traceable knowledge units; entries provide the integrated scholarly treatment that makes that knowledge studyable.

---

### 6.2 Entry Structure at a Leaf

Entry cardinality at a leaf is determined by whether the science has scholarly schools (§2.4) for that leaf's topic, following the rules established in §1.6 and §2.4.

**When schools exist:** each school-group (§2.4) at the leaf that contains at least one verified excerpt receives its own dedicated entry. Each school-group's entry is generated exclusively from that school-group's verified excerpts. Entries from different school-groups are never mixed — the owner reads each school's treatment of the topic independently and forms their own comparative understanding. Within a school-group's entry, intra-school disagreements and individual scholarly positions (§2.4) are documented with full attribution.

**When no schools exist:** the leaf has a single entry generated from all verified excerpts at the leaf, regardless of source or author.

**When no verified excerpts exist:** the leaf has no entry. Entries are generated only at leaves (or school-groups within leaves) that contain at least one verified excerpt. A leaf populated exclusively with flagged excerpts has no primary entry.

**Entries and the verified/flagged separation.** The factual layer of an entry is generated exclusively from verified excerpts. Flagged excerpts are never included in the factual layer. The analytical layer may reference flagged content for scholarly context — noting the existence of rejected positions and explaining why they are rejected — but the factual foundation remains verified-only. Where flagged excerpts exist at a leaf, a separate critical analysis section may be generated to address them directly — structurally separate from the primary entry and clearly marked. The specific mechanics of how the analytical layer references flagged content and how the critical analysis section is structured are specified in the synthesizing engine's per-component documentation (Level 2).

*[Non-normative — rationale: the three-part model (verified-only factual layer, analytical-layer flagged references, separate critical analysis section) serves the owner's stated pedagogical goal of understanding where scholars went wrong. A student who only reads correct positions misses the scholarly method of learning from error. The structural separation ensures that the owner always knows what is verified and what is flagged.]*

---

### 6.3 Entry Staleness and Regeneration

Entries are generated artifacts: they are produced by the synthesizing engine from a specific state of the excerpt collection and stored for study. When the underlying excerpt collection changes, the stored entry no longer reflects the current state of knowledge at the leaf. The entry is then _stale_ (§2.4).

**Staleness triggers.** An entry becomes stale when any of the following changes occur at the leaf (or school-group) from which it was generated:

A new verified excerpt is placed at the leaf — from a newly processed source or from manual input. An existing excerpt's metadata is corrected in a way that affects the entry's content (author attribution, school classification, or content that was misrepresented). An excerpt is relocated to or from the leaf due to taxonomy evolution (§4.4). An excerpt is reclassified between verified and flagged — a verified excerpt becoming flagged reduces the entry's factual base; a flagged excerpt becoming verified expands it.

**Staleness tracking.** The application tracks staleness at the granularity of entry generation units: per school-group where schools exist, per leaf where they do not. A change affecting one school-group's excerpt collection makes that school-group's entry stale without affecting other school-groups' entries at the same leaf.

**Staleness visibility.** Stale entries are clearly marked when displayed. The owner always knows whether the entry being read reflects the current excerpt collection or is outdated. The specific marking mechanism is an implementation decision specified in per-component documentation (Level 2).

**Regeneration.** Stale entries are resolved through regeneration: the synthesizing engine generates a new entry from the current state of the excerpt collection, replacing the stale entry. Regeneration scheduling — whether it occurs on-demand (when the owner opens a leaf with a stale entry), as background processing, or both — is specified in the synthesizing engine's per-component documentation (Level 2). The new entry is a fresh generation, not an incremental update to the previous entry; the synthesizing engine reads the full current excerpt collection and produces a complete entry.

**Staleness from taxonomy evolution.** §4.4 specifies how evolution events propagate to entries: leaf-to-branch conversion invalidates the pre-evolution leaf's entry (the node is no longer a leaf) and queues new sub-leaves for initial entry generation; excerpt relocation between existing leaves makes entries at each affected leaf stale. These propagation rules are binding on the taxonomy engine and synthesizing engine jointly.

---

### 6.4 Entry Quality

The owner memorizes and teaches from entries. An entry that misrepresents a scholarly position, omits a perspective present in the excerpts, misattributes an opinion, or presents flagged content as verified is not merely a low-quality entry — it is a source of misinformation that may propagate through the owner's teaching to others. Entry quality is therefore subject to the same core property priority as every other component: accuracy first (§1.5), protection second, intelligence third.

**Factual-layer requirements.** The factual layer must meet the following requirements, each of which is a binding constraint on the synthesizing engine's output:

_Attribution completeness._ Every scholarly position represented in the verified excerpts must appear in the entry with correct attribution — which scholar holds the position, from which scholarly tradition, with what evidence. No excerpt's content may be silently omitted from the entry.

_Attribution accuracy._ Every attribution in the entry must faithfully represent the original scholar's position as recorded in the excerpt. Misrepresentation — however slight — is a critical error under the accuracy core property (§1.5).

_Traceability._ Every factual claim in the entry must be traceable to one or more specific excerpts. The traceability mechanism — how the entry links back to its source excerpts — is specified in the synthesizing engine's per-component documentation (Level 2).

_Preponderant opinion handling._ Where specific scholars declare a position to be الراجح (§2.4), the entry records this with attribution: which scholar considers which position الراجح, and their stated reasoning. The entry does not declare a universal الراجح — it presents each scholar's assessment transparently.

**Analytical-layer requirements.** The analytical layer is the synthesizing engine's intellectual contribution — it is expected to add scholarly value beyond what any individual excerpt states. The analytical layer is subject to less rigid constraints than the factual layer because it represents generated reasoning, not source-traceable facts. The analytical layer must not contradict the factual layer. The analytical layer must not present generated reasoning as if it were a scholar's stated position. The analytical layer must be clearly distinguishable from the factual layer in the entry's structure, so the owner always knows what is source-traceable and what is synthesized reasoning.

[OPEN QUESTION: To what extent may the synthesizing engine's analytical layer include knowledge or connections not directly stated in the source excerpts? The owner has expressed interest in the synthesizing engine adding its own scholarly connections and further clarification. The boundary between "intelligent synthesis that adds genuine value" and "unverifiable addition that the owner might mistake for source-based knowledge" needs precise specification in the synthesizing engine's per-component documentation (Level 2). This is a design question with implications for the accuracy core property.]

**Readability.** The entry must be written in clear, well-organized Arabic that a student of the science can follow. Readability is a quality requirement on the synthesizing engine's output, not a structural specification. The specific formatting, section ordering, and presentation style of entries are specified in the synthesizing engine's per-component documentation (Level 2).

---

---

## §7 — The Source Pipeline and Normalization Boundary

§2.2 defines the source pipeline as the source-format-specific components that discover, acquire, document, and normalize knowledge sources — Phase 1 of the processing architecture, comprising the source engine (محرك المصادر) and the normalization engine (محرك التطبيع). §2.2 also defines the normalization boundary (حد التطبيع) as the architectural dividing line between Phase 1 and Phase 2, and states that a violation of this boundary is an architectural bug regardless of convenience. §2.5 defines the vocabulary of sources, frozen sources, source types, source formats, source repositories, source metadata, trustworthiness evaluation, manual input, and the normalized package. This section specifies the source pipeline's architectural responsibilities in full: how knowledge sources enter the application, what the source engine and normalization engine are each responsible for, what the normalization boundary means concretely, and why it is the application's most important architectural constraint.

This section defines _what_ the source pipeline must accomplish and _what architectural constraints_ govern it. It does not define the internal processing logic of the source engine or normalization engine — adapter implementations, normalizer algorithms, metadata schemas, or discovery strategies. Those details are in the per-component documentation (Level 2) for each engine.

---

### 7.1 Pipeline Overview

The source pipeline transforms raw knowledge material from the outside world into normalized packages (§2.5) that the Phase 2 engines can process. The pipeline encompasses two engines operating in sequence: the source engine discovers, acquires, freezes, and documents sources; the normalization engine transforms frozen sources into the universal normalized format. The pipeline's output — the normalized package — crosses the normalization boundary and enters Phase 2, where it is processed identically regardless of its origin.

The source pipeline operates in two modes, both defined in §2.2 and §2.5:

_Autonomous mode:_ the source engine proactively searches configured source repositories (§2.5) for relevant material, evaluates relevance, acquires sources that pass the relevance threshold, and feeds them through the pipeline. The owner is notified at human gates (§9) where approval is required.

_Manual mode:_ the owner directly provides knowledge material — personal study notes, text content, files, references — and the source engine processes it through the same pipeline as autonomous discoveries. Manual input (§2.5) is a source type within the pipeline architecture, not a separate subsystem.

Both modes produce identical output: a normalized package conforming to the universal schema. Phase 2 engines cannot distinguish between a source that was autonomously discovered and one the owner manually provided. This indistinguishability is not incidental — it is a consequence of the normalization boundary and is architecturally required.

---

### 7.2 Source Discovery and Acquisition

The source engine (محرك المصادر) is responsible for discovering, identifying, and acquiring raw knowledge sources. §2.2 specifies its two operating modes (autonomous and manual), its output (a frozen raw source), and its additional responsibilities (source registry maintenance, source metadata creation, trustworthiness evaluation). This subsection specifies the architectural constraints governing these responsibilities.

**Freezing.** Every source is frozen immediately upon acquisition (§2.5). The frozen source is an immutable copy of the original material, cryptographically hashed at acquisition time. No subsequent component of the application — including the source engine itself during later enrichment — may modify the frozen source. All processing operates on copies or derived representations. Freezing is an integrity guarantee that enables auditability: the original source as acquired is always verifiable by hash comparison.

**Deduplication.** The source engine maintains a source registry that tracks all acquired sources with sufficient identifying information to detect duplicates across source types and repositories. A source that is available from multiple repositories is acquired once; the alternative availability may be recorded in source metadata for reference. The specific deduplication criteria and the registry's structure are specified in the source engine's per-component documentation (Level 2).

**Source discovery scope.** The source engine's autonomous discovery searches configured source repositories (§2.5). The application maintains a registry of known repositories. Adding a new repository to this registry is a configuration decision; the repository-specific interface logic (connection, search, download, rate limiting, authentication) is specified in the source engine's per-component documentation (Level 2). *[Non-normative — current known repositories include المكتبة الشاملة (Shamela), KetabOnline, الدرر السنية (dorar.net), and recorded scholarly lessons. Additional repositories to be evaluated include المكتبة الوقفية, إسلام ويب, الموسوعة الفقهية الكويتية, ملتقى أهل الحديث, and various scholarly websites.]*

**Relevance evaluation.** During autonomous discovery, the source engine evaluates whether a candidate source contains scholarly content relevant to the library's sciences (§1.2). Relevance evaluation is an intelligent operation — it requires understanding what the source contains and whether it falls within the library's knowledge scope. The specific criteria and methods for relevance evaluation are specified in the source engine's per-component documentation (Level 2).

---

### 7.3 Source Documentation and Metadata

The source engine creates and maintains a source metadata record (§2.5) for every acquired source. Source metadata is a living record: it is initially created during source acquisition and continues to be enriched over the source's lifetime as more information is learned from processing, external research, or the owner's input.

**What source metadata must document.** The following categories of information constitute the complete set of metadata concerns. The specific fields within each category, their data types, and their validation rules are specified in the source engine's per-component documentation (Level 2).

_Provenance:_ where the source came from, when it was acquired, how it was obtained (autonomous or manual), which source repository or acquisition path.

_Identity:_ the source's title, author, editor (محقق) where applicable, publisher, edition information, and work identifier (§2.5) linking volumes of multi-volume works.

_Author scholarly context:_ the author's biographical and scholarly information — the information needed for attribution and synthesis. This includes era, school affiliation (where applicable and per the science's Level 3 documentation), geographic origin, scholarly standing, and the author's position within the scholarly tradition. Author scholarly context may be sparse initially and enriched over time.

_Source characteristics:_ content type (book, article, lecture, personal note, encyclopedia entry), language, encoding, approximate content length, volume count for multi-volume works.

_Science scope:_ which science or sciences (§4) the source is relevant to. A single source may be relevant to multiple sciences — a Fiqh book may contain hadith methodology discussions, linguistic analysis, and usul al-fiqh reasoning alongside its Fiqh content. Science scope is assessed by the source engine during intake (using intelligent evaluation of the source's content and the author's scholarly domain) and recorded in source metadata. Science scope flows through the pipeline: the normalized package carries the source's science scope, enabling Phase 2 engines (particularly the excerpting engine for science-specific metadata per §5.4, and the taxonomy engine for placement) to access science identity without violating source-agnosticism — they read science scope from pipeline data, not from source-format-specific logic. Science scope may be refined during processing: the excerpting and taxonomy engines may discover that a source produces excerpts for sciences not in the original scope assessment, triggering an enrichment write-back to source metadata.

_Trustworthiness evaluation:_ the source engine's assessment of the source's reliability, as specified in §7.4.

_Processing status:_ which pipeline stages have been completed for this source and their outcomes.

**Living enrichment.** Source metadata is not a one-time capture. The normalization engine may discover encoding anomalies or structural irregularities during normalization. Phase 2 engines may discover author-specific scholarly positions during extraction. The owner may provide additional information at any human gate. External research may surface new biographical data. All enrichments are written back to the source metadata record. The mechanism by which downstream engines write back enrichments is specified in the relevant per-component documentation (Level 2).

---

### 7.4 Trustworthiness Evaluation

Trustworthiness evaluation (§2.5) is an intelligent assessment of a source's reliability, scholarly credentials, and content quality, performed by the source engine during source intake. The evaluation determines the default verified/flagged classification for the source's excerpts (§2.4, §3.2).

**Classification tiers.** The evaluation classifies the source into one of two tiers: verified (the source is judged reliable and scholarly; its excerpts default to verified knowledge) or flagged (the source fails the trustworthiness threshold; its excerpts default to flagged knowledge, with a flag reason). These are default classifications — individual excerpts may be reclassified based on content-level issues detected during Phase 2 processing or at human review (§2.4).

**Conservative bias.** When the evaluation is uncertain, it classifies the source as flagged. Flagging a reliable source is correctable — the owner can reclassify at review. Verifying an unreliable source contaminates the library's verified knowledge base, which is harder to detect and correct. This asymmetry — the cost of false verification exceeding the cost of false flagging — is an application of the core property priority (§1.5): accuracy governs when uncertainty exists.

**Evaluation factors.** The trustworthiness evaluation considers the author's scholarly standing, the source's rigor and quality, whether the source is a primary text or a secondary summary, and the source repository's editorial standards. The specific evaluation criteria, their weighting, and the threshold between verified and flagged are specified in the source engine's per-component documentation (Level 2).

**Owner override.** The owner may override any trustworthiness evaluation — manually flagging a source the source engine verified, or manually verifying a source the source engine flagged. The owner's override applies to the source's default classification; individual excerpt reclassification remains possible as specified in §2.4.

**Escalation to human gate.** When the source engine cannot reach a confident trustworthiness determination, the evaluation is escalated to a human gate (§9) where the owner makes the final determination.

---

### 7.5 Source Normalization

The normalization engine (محرك التطبيع) transforms frozen sources from their native format into the application's universal normalized format, producing a normalized package (§2.5). §2.2 specifies that each supported source format has its own normalizer — a module that understands the specific challenges of that format — and that normalizer complexity is unlimited and self-contained as long as output conforms to the universal schema.

**One normalizer per source type.** Each supported source type (§2.5) requires its own normalizer in the normalization engine. A normalizer is responsible for both content cleaning (stripping format-specific markup, separating footnotes from main text, handling encoding issues) and structure discovery (identifying headings, chapters, and the source's internal organizational hierarchy). Structure discovery is part of normalization because structural signals often exist in format-specific markup that is only available before format stripping — by including structure discovery in normalization, each normalizer uses the richest available information to determine structure.

**Output uniformity.** All normalizers produce normalized packages conforming to the same universal schema. The Phase 2 engines receive identical artifacts regardless of which normalizer produced them. The specific contents and schema of the normalized package are defined in the normalization engine's per-component documentation (Level 2). At the VISION.md level, the binding properties of the normalized package are: it is source-agnostic (carries no source-format-specific identifiers, markers, or assumptions), it is self-sufficient (carries everything the Phase 2 engines need to process the content without accessing the frozen source), and it conforms to a universal schema that is identical across all normalizers.

**Adding new source types.** Adding a new source type to the application requires building a new normalizer in the normalization engine and, where applicable, a new acquisition interface in the source engine. No Phase 2 engine is modified for a new source type. This is the practical consequence of the normalization boundary: source diversity grows in Phase 1 only.

**Metadata enrichment during normalization.** The normalization engine may discover information about the source that should be recorded in source metadata (§7.3) — encoding inconsistencies, structural irregularities, content anomalies. These discoveries are written back to the source metadata record.

---

### 7.6 The Normalization Boundary

The normalization boundary (حد التطبيع) is the architectural dividing line between Phase 1 and Phase 2, defined in §2.2 as "the single most important architectural constraint in the application." This subsection provides the full specification of what the boundary means and what it prohibits.

**The division.** Above the boundary, everything is source-format-specific. The source engine's discovery and acquisition logic may vary by source repository. The normalization engine has one normalizer per source type, each handling format-specific challenges. Below the boundary, everything is source-agnostic. The passaging engine (محرك التقطيع), atomization engine (محرك التذرير), excerpting engine (محرك الاقتطاف), taxonomy engine (محرك التصنيف), and synthesizing engine (محرك التوليف) operate on normalized packages without knowing or depending on the source's original format or acquisition method.

**What must not appear below the boundary.** No source format names or identifiers. No source-specific structural markers. No source-specific metadata conventions. No assumptions about page numbering, footnote formatting, or content structure that depend on source format. No file paths to frozen raw source files. No logic that would produce different results depending on which source type produced the normalized data. Any such appearance is an architectural bug.

**Why the boundary matters.** The normalization boundary ensures that the Phase 2 engines — the intellectual core of the application, where content understanding, extraction, placement, and synthesis happen — do not accumulate complexity as source diversity grows. Adding a new source type requires only Phase 1 work (building a normalizer and, where needed, an acquisition interface). The Phase 2 engines are never modified for a new source type. Without this boundary, every new source type would require changes throughout the entire processing pipeline, and the Phase 2 engines would become increasingly complex and fragile. The boundary makes source diversity a Phase 1 scaling problem rather than an application-wide complexity problem.

---

---

## §8 — Quality Architecture (Error Protection)

§1.5 establishes accuracy as the highest-priority core property and protection from error as the second. §1.9 names the application's non-negotiables: zero tolerance for silent corruption, defense at every decision point, and mutual verification between human and autonomous systems. §2.2 defines the architectural mechanisms that serve these properties: multi-model consensus (إجماع متعدد النماذج), human gates (بوابة بشرية), feedback loops (حلقة التغذية الراجعة), gold baselines (خط أساس ذهبي), and regression testing (اختبار الانحدار). §2.4 defines the verified/flagged separation as the content-level defense. This section specifies the quality architecture that binds these mechanisms into a coherent, layered defense: the architectural strategy for preventing, detecting, correcting, isolating, and auditing errors across the entire application.

This section defines _what_ the quality architecture must achieve and _what layers of defense_ it comprises. It does not define the internal logic of any specific validation algorithm, consensus protocol, or gate procedure. Those details are in the per-component documentation (Level 2) for each engine and in §9 (Human Gates) for gate-specific specifications.

---

### 8.1 Defense in Depth

The application's approach to error protection is defense in depth: multiple independent mechanisms, each capable of catching different types of errors, layered so that an error must evade all of them to enter the library undetected. No single mechanism is trusted to catch all errors. No single failure — of a validation check, a consensus round, a human review, or any other mechanism — permits an error to enter the library without further barriers.

Defense in depth operates through five distinct layers. Each layer is a category of error-catching capability, not a sequential step — multiple layers may operate simultaneously at any given point in the processing pipeline. The layers are ordered here by when they first engage, not by importance; all five are mandatory.

**Layer 1: Prevention.** Intelligent processing at every decision point minimizes the creation of errors in the first place. The application's seven engines (§2.2) use intelligent reasoning for content decisions — the same LLM capabilities that enable extraction, placement, and synthesis also enable careful, contextual judgment that reduces the error rate at the source. Prevention is not a separate mechanism; it is the natural consequence of using intelligent reasoning rather than brittle heuristics for content decisions.

**Layer 2: Detection.** Multiple independent detection mechanisms catch errors that were created despite prevention efforts. Detection mechanisms fall into two categories:

_Algorithmic validation_ catches mechanical errors using deterministic checks: schema conformance, reference integrity, character offset consistency, range monotonicity, and other structural invariants that can be verified without content understanding. Algorithmic validation is fast, reliable, and catches a large class of mechanical errors. The specific algorithmic checks applicable to each engine's output are specified in that engine's per-component documentation (Level 2).

_Intelligent validation_ catches content errors that require understanding: self-containment verification for excerpts (§5.1), placement validation for taxonomy assignments, attribution accuracy for metadata, cross-excerpt consistency within a passage, and cross-source consistency within a leaf. Intelligent validation is LLM-driven and applies to decisions where the correctness of an output depends on understanding the content's meaning.

_Multi-model consensus_ (§2.2) catches errors by comparing independent LLM outputs on the same input. Agreement increases confidence; disagreement triggers investigation or escalation. Consensus is applied to precision-critical content decisions where the cost of an undetected error is high — extraction, placement, evolution proposals. It is not applied to mechanical operations where algorithmic validation suffices. The specific consensus protocol — how many models participate, how agreement and disagreement are evaluated, how disagreements are resolved or escalated — is specified in per-component documentation (Level 2).

**Layer 3: Correction.** Feedback loops (§2.2) trace detected errors to root causes and fix the application's processing rules to prevent recurrence. When the owner corrects an error at a human gate (§9), the correction is recorded: what the application produced, what the owner corrected it to, and why. Corrections are analyzed for patterns — systemic issues that a single correction represents. When a systemic issue is identified, the responsible engine's processing rules (prompt templates, classification heuristics, extraction definitions) are updated. Rule updates require regression testing (§2.2) before deployment to production: previously approved outputs are re-processed to verify that the update does not degrade quality. The scope of feedback-driven improvement is precisely bounded: processing rules improve. Feedback loops do not involve LLM fine-tuning, autonomous architectural changes, or modifications to this specification.

**Layer 4: Isolation.** The two-tier content model — verified and flagged knowledge (§2.4, §3.2) — ensures that content whose reliability is uncertain or rejected is physically separated from verified knowledge at every level of the library: in storage, in synthesis, in coverage measurement, and in display. Isolation is the last line of defense: even if an individual trustworthiness evaluation is incorrect and a flagged source's excerpts should have been verified (or vice versa), the structural separation prevents contamination between tiers. The separation is enforced structurally (§3.2), not by advisory metadata that components may optionally respect.

**Layer 5: Auditability.** Every decision the application makes — extraction choices, placement decisions, trustworthiness evaluations, evolution proposals, human gate outcomes — is logged with the reasoning that produced it. When an error is discovered, the full decision chain that led to it can be reconstructed and analyzed. Auditability is not a reporting feature; it is a diagnostic capability that enables root-cause analysis for feedback loops (Layer 3) and regression testing. The specific logging format and retention policies are specified in per-component documentation (Level 2).

---

### 8.2 The Two-Tier Content Model

§2.4 defines verified knowledge and flagged knowledge. §3.2 specifies the structural enforcement of their separation at every level of the library. This subsection positions the two-tier content model within the quality architecture as a defense mechanism, not merely a content classification scheme.

**The model's defensive function.** The two-tier model exists because no trustworthiness evaluation — whether performed by the source engine (§7.4), by multi-model consensus, or by the owner at a human gate — is guaranteed to be correct. A source that appears trustworthy may contain errors. A source that appears unreliable may be scholarly and accurate. The two-tier model mitigates the consequences of incorrect evaluations: verified knowledge and flagged knowledge are structurally separated so that one tier's content cannot contaminate the other. The owner studies from verified entries (§6.2); flagged content is accessible but isolated.

**Per-excerpt granularity.** The verified/flagged classification operates at the individual excerpt level (§2.4), not only at the source level. A source's trustworthiness evaluation (§7.4) sets the default classification for the source's excerpts, but individual excerpts may be reclassified — a verified source may yield individually flagged excerpts if content-level issues are detected during extraction or cross-validation, and the owner may override any individual classification. This per-excerpt granularity means that the library's storage, synthesis, and coverage systems must support mixed classification within a single source's excerpt collection.

**Reclassification, not deletion.** Corrections never remove a placed excerpt from the library. A placed excerpt found to be unreliable is reclassified as flagged rather than deleted (per the library growth and correction rules in §3.4). This preserves the library's complete audit trail and supports the educational value of flagged knowledge — understanding where scholars went wrong is a recognized scholarly method (§6.2).

---

### 8.3 Feedback Loops and Self-Improvement

§2.2 defines feedback loops as "the general pattern by which corrections at human gates are saved, analyzed for patterns, and used to improve the application's future decisions." This subsection specifies the architectural requirements that feedback loops must satisfy.

**The correction cycle.** When the owner corrects the application's output at a human gate (§9), the feedback loop records: (a) what the responsible engine produced, (b) what the owner corrected it to, (c) the owner's reason for the correction (where provided), and (d) which engine produced the incorrect output and at which processing stage. The recording must be structured enough for pattern analysis — free-text correction notes may supplement but do not replace structured recording.

**Pattern analysis.** Feedback loops analyze accumulated corrections for systemic patterns. A systemic pattern is one where multiple corrections share a common root cause — a deficiency in an engine's processing rules that manifests repeatedly. *[Non-normative example: if eight of twenty corrections involve school misattribution in Fiqh excerpts, the pattern suggests that the excerpting engine's school identification rules for Fiqh need improvement.]* When a systemic pattern is identified, the responsible engine's processing rules are updated to address the root cause. The specific analysis methods — how patterns are detected, what threshold of occurrences constitutes a pattern, and how root causes are identified — are specified in the per-component documentation (Level 2) for each engine.

**Regression testing gate.** No processing rule update derived from feedback is applied to production without regression testing (§2.2). Regression testing re-processes passages with known-correct outputs — gold baselines (§2.2) and previously approved extractions — to verify that the rule update does not degrade quality on content that was already being handled correctly. Degraded results block the update. The specific regression testing protocol — which baselines are used, what constitutes degradation, and how borderline cases are evaluated — is specified in per-component documentation (Level 2).

**Model change regression.** §1.9 identifies silent behavioral drift in AI models as a risk. When an underlying LLM model used by any engine is updated (new version, changed behavior), regression tests against gold baselines must run before the updated model is used in production. This is a mandatory gate — not a best practice.

**Bounded scope of improvement.** The application's processing rules improve through feedback loops. Processing rules include: prompt templates, extraction definitions, classification heuristics, validation thresholds, and other configurable parameters that engines use to make content decisions. Feedback loops do not involve LLM fine-tuning, autonomous architectural changes, modifications to this specification, or changes to the library's persistent data (science trees, placed excerpts, entries). The application gets better at processing; it does not autonomously redesign itself.

---

### 8.4 Integrity Verification

§1.9 identifies storage integrity degradation as a risk: the library's stored data can degrade over time through file corruption, interrupted writes, or bugs in file-handling code. This subsection specifies the architectural requirements for integrity verification.

**Periodic integrity checks.** The application performs periodic integrity verification of the library's stored data as a scheduled background operation. Integrity checks verify: that frozen source files match their recorded hashes, that excerpt files are well-formed and their metadata is internally consistent, that tree definitions and stored excerpts are mutually consistent (every placed excerpt references a leaf that exists in the current tree version), and that source metadata records reference sources that exist. The specific checks, their scheduling, and their error-handling behavior are specified in per-component documentation (Level 2).

**Data integrity as a continuous property.** Integrity verification is not a one-time audit performed at deployment — it is a continuous property, consistent with §1.5's statement that "protection from error is not a phase or a checklist — it is a continuous property that every component, at every stage, must exhibit at all times." Integrity checks run as background operations and surface issues for the owner's attention at the appropriate severity level.

---

---

## §9 — Human Gates

§2.2 defines a human gate (بوابة بشرية) as "a checkpoint where the application pauses and requires the owner's explicit approval before proceeding with a high-impact action — one that, if incorrect, would introduce errors into the library that may be difficult to detect after the fact." §2.2 also establishes that human gates are bidirectional: the owner reviews the application's proposed actions, and the application intelligently validates the owner's inputs and decisions. §1.9 establishes mutual verification between human and autonomous systems as a non-negotiable. §2.5 defines the owner confidence level (مستوى ثقة المالك) as a calibration mechanism for human gate behavior. §8 positions human gates within the quality architecture as one of five defense layers. This section specifies the human gate architecture: what human gates are, why they exist, where they occur, and how they adapt to the owner's expertise.

This section defines _what_ human gates must achieve and _what categories of decisions_ they govern. It does not define the specific gate procedures, UI presentation, approval workflows, or decision logic for any individual gate. Those details are in the per-component documentation (Level 2) for each engine that implements a human gate.

---

### 9.1 What Human Gates Are

A human gate is a mandatory checkpoint in the application's processing pipeline where the application pauses autonomous execution and requires the owner's explicit decision before proceeding. Human gates exist at processing points where the consequence of an incorrect action — a misplaced excerpt, an invalid taxonomy evolution, a wrong trustworthiness evaluation — would be difficult to detect after the fact and could silently corrupt the library.

Human gates are not optional review opportunities. When a human gate exists at a processing point, the application must not proceed past that point without either the owner's explicit decision (approval, rejection, or modification of the proposed action) or a standing pre-approval policy that covers the specific action category. The specific set of human gates and their locations in each engine's processing flow are defined in that engine's per-component documentation (Level 2).

**Pre-configured approval policies.** For specific categories of low-risk decisions, the owner may configure pre-approval policies — standing decisions for defined categories of actions that allow the application to proceed without pausing at the human gate for actions within the policy's scope. Pre-configured policies do not remove the human gate — they constitute the owner's advance decision for a bounded category. The owner can revoke or modify any pre-configured policy at any time. The specific categories eligible for pre-approval, the format of approval policies, and the mechanism for applying them are specified in per-component documentation (Level 2).

---

### 9.2 Why Human Gates Exist

Human gates serve the quality architecture (§8) by providing a checkpoint that no automated mechanism can replace. They exist for three reasons, each independently sufficient to justify their presence.

**Reason 1: The owner is the ultimate authority on the library's content.** The library (§1.1) is the owner's personal scholarly library. Decisions about what knowledge it contains, how that knowledge is organized, and what is considered trustworthy are ultimately the owner's decisions. Automated systems — however sophisticated — execute within the boundaries that the owner sets. Human gates are the mechanism by which the owner exercises authority over the library's most consequential decisions.

**Reason 2: AI systems can be wrong.** LLM-based processing, multi-model consensus, and intelligent validation reduce errors but cannot eliminate them. Errors that survive all automated detection layers (§8.1) may still be caught by an informed human reviewer. Human gates provide this final layer of defense, consistent with §1.9's requirement that "no decision point with the potential to introduce error may operate without a check."

**Reason 3: Mutual verification is bidirectional.** §1.9 establishes that neither the human nor the autonomous system is trusted unconditionally — both check each other. When the owner provides input at a human gate (approving an action, correcting an error, providing manual input), the application intelligently validates that input. If the owner's decision conflicts with established verified content — such as a manual attribution that contradicts known author metadata, or an approval of a placement that consensus strongly disagrees with — the application flags the concern for the owner's review rather than accepting silently. The human gate is a bidirectional checkpoint: the owner verifies the application's proposals, and the application verifies the owner's decisions.

---

### 9.3 Where Human Gates Occur

Human gates occur at processing points where the consequences of an incorrect decision are high-impact and difficult to reverse or detect after the fact. The following categories describe the types of decisions that require human gates. The specific gate locations within each engine's processing flow, the information presented to the owner at each gate, and the available actions (approve, reject, modify) are specified in the per-component documentation (Level 2) for each engine.

**Trustworthiness evaluation.** When the source engine (محرك المصادر) cannot reach a confident trustworthiness determination for a source (§7.4), the evaluation is escalated to a human gate. The owner makes the final verified/flagged determination. The source engine's per-component documentation specifies the confidence threshold below which escalation occurs.

**Extraction review.** After the excerpting engine (محرك الاقتطاف) produces draft excerpts (§2.4), they are presented to the owner for review before placement. The owner can approve, flag disagreements, or request re-extraction with feedback. The specific review protocol — what the owner sees, what actions are available, how feedback is structured — is specified in the excerpting engine's per-component documentation (Level 2).

**Taxonomy evolution.** Before the taxonomy engine (محرك التصنيف) applies a proposed evolution (§4.4), the proposal is presented to the owner as a structural diff: current tree structure versus proposed tree structure, with the excerpt redistribution that would result. The owner approves, rejects, or modifies the proposal. Evolution is one of the highest-impact decisions in the application — an incorrect evolution misplaces excerpts, invalidates entries, and may require rollback (§4.4). The taxonomy engine's per-component documentation specifies the gate protocol.

**Ambiguous placement.** When the taxonomy engine is uncertain about an excerpt's correct leaf — when multiple plausible placements exist and confidence is below a threshold — the placement decision is escalated to a human gate. The owner sees the excerpt, the candidate leaves, and the engine's reasoning for each candidate. The taxonomy engine's per-component documentation specifies the confidence threshold and gate protocol.

**Large batch operations.** When autonomous discovery (§7.2) proposes processing a batch of new sources, the batch may be presented to the owner for review before processing begins. The source engine's per-component documentation specifies which batch sizes or source categories require this gate.

**Flagged content review.** Excerpts classified as flagged (§2.4) may be periodically presented to the owner for review — to confirm or reverse the flagging, to add flag reasons, or to reclassify as verified. The specific review schedule and protocol are specified in per-component documentation (Level 2).

---

### 9.4 Owner Confidence Calibration

§2.5 defines the owner confidence level (مستوى ثقة المالك) as the owner's self-declared familiarity with a science, used to calibrate processing conservatism. §1.9 identifies expertise asymmetry at human gates as a risk: for sciences the owner has studied deeply, human gate review is effective; for sciences the owner has barely begun studying, the owner may lack the expertise to catch subtle errors.

**Calibration mechanism.** The owner declares a confidence level for each science in the library. The confidence level is a self-assessment, not an external evaluation — the owner is the sole judge of their own expertise. The specific scale (its gradations and labels) and the mechanism for declaring and updating confidence levels are specified in the human gate's per-component documentation (Level 2).

**Effect on processing conservatism.** For sciences where the owner's declared confidence is lower, the application applies more conservative processing. "More conservative" means: more excerpts are flagged rather than verified at borderline cases, more placement decisions are escalated to human gates rather than proceeding autonomously, explicit "pending expert review" markers are applied to excerpts and entries, and the threshold for multi-model consensus agreement is raised (requiring stronger agreement before proceeding without escalation). The specific behavioral adjustments for each confidence level are specified in per-component documentation (Level 2).

*[Non-normative — rationale: the owner's expertise across sciences is uneven. For a science the owner has studied for years, the owner can catch subtle errors that automated systems miss — the human gate adds genuine value. For a science the owner is just beginning to explore, the owner's review may not catch errors that a specialist would. By calibrating conservatism to expertise, the application compensates: where the human gate is weaker (low-confidence sciences), the automated layers compensate with greater caution. This is a practical application of the defense-in-depth philosophy (§8.1) — when one layer is known to be less effective, other layers increase their sensitivity.]*

---

---

## §10 — Implementation Strategy

### 10.0 Scope

This section specifies the strategy for implementing خزانة ريان incrementally: the principles governing implementation order, the milestone sequence from engine validation through comprehensive coverage, and the relationship between the existing codebase and the target architecture. This section defines _what_ each milestone must achieve and _what_ success looks like. It does not define the specific implementation steps, timelines, schedules, or technical approaches for achieving any milestone — those are operational decisions made at the start of each milestone.

Terms used in this section carry their §2 meanings. Engine names refer to the seven engines defined in §2.2. The processing architecture (Phase 1, Phase 2, the normalization boundary) is defined in §2.2. The completion model (baseline, rich, library-wide maturity) is defined in §1.7.

---

### 10.1 Implementation Principles

Three principles govern the order and approach of implementation. These principles are binding constraints on implementation planning — they are not aspirations.

**Principle: Prove before expanding.** No new source type, science, automation level, or architectural capability is built until the preceding capability is proven to produce correct output validated by the owner. The Phase 2 engines must be validated on real content before autonomous source discovery is built. The normalization boundary must be demonstrated to hold with one source type before a second source type is added. One science must be fully working — excerpts placed, entries generated, owner-validated — before additional sciences are loaded. This principle prevents building on unvalidated assumptions.

**Principle: Incremental value.** Each milestone produces a usable library. The library is usable — for the sciences and sources covered so far — at the end of every milestone, not only at the eventual completion of all milestones. No milestone depends on future milestones for its value. This means every design decision must ensure the application works well at its current scale, not only at its eventual full scale.

**Principle: Preserve proven work.** The existing codebase (§10.3) contains significant validated work: extraction logic, consensus mechanisms, test suites, gold baselines, and taxonomy trees for four Arabic language sciences. This work carries forward into خزانة ريان. Proven, working code is restructured to fit the target architecture — it is not rewritten from scratch. Restructuring means placing existing code in its correct architectural home (per §13.2) and adapting interfaces to conform to the schema contracts (§13.4). It does not mean reimplementing functionality that already works.

---

### 10.2 Milestones

The following milestones define the implementation sequence. Each milestone has a goal (what it aims to demonstrate), a scope (what work it encompasses), and success criteria (how the owner and the application determine that the milestone is complete). Milestones are sequential: each milestone's success criteria must be met before the next milestone begins, per the prove-before-expanding principle.

Milestone numbering is stable — milestones are not renumbered if one is added, removed, or split. Specific quantities mentioned below (test counts, line counts, file counts) reflect approximate values at the time of writing and may have changed; they are included for orientation, not as binding specifications.

**Milestone 1: Prove the Phase 2 engines end-to-end.**

_Goal:_ Demonstrate that the Phase 2 processing pipeline works from normalized content through to placed excerpts and generated entries, for at least one science.

_Scope:_ Complete the implementation of the passaging, atomization, excerpting, taxonomy, and synthesizing engines (§2.2) to the point where they can process a normalized package and produce placed excerpts at correct leaves with generated entries. Use existing normalized content (from the current codebase's prior normalization work) as input. Validate results against one science's tree.

_Success criteria:_ A science tree populated with self-contained excerpts (meeting §5's requirements) from at least one processed source, with synthesized entries (meeting §6's requirements) at each populated leaf, validated by the owner.

_What this proves:_ The Phase 2 engines work. The extraction, placement, and synthesis pipeline can take normalized input and produce the library's primary knowledge products (excerpts and entries).

**Milestone 2: Scale with multiple sources in the same source type.**

_Goal:_ Process multiple sources of the same source type through the proven pipeline. Demonstrate multi-source convergence at leaves and school-based organization.

_Scope:_ Process additional sources through the full pipeline across multiple sciences (targeting the four Arabic language sciences from the existing codebase). Track coverage (§3.5). Demonstrate school-group organization within leaves (§3.3) where applicable. Tune extraction quality based on observed issues across diverse source content.

_Success criteria:_ Multiple science trees have meaningful coverage from multiple sources. Coverage reports identify under-served areas. School-group organization within leaves works correctly where the science has schools.

_What this proves:_ The pipeline scales across diverse content structures, multiple sciences, and different scholarly styles within a single source type.

**Milestone 3: Expand to Islamic sciences beyond Arabic language.**

_Goal:_ Add science trees for Islamic sciences (§4.3) beyond the original four Arabic language sciences. Demonstrate that the Phase 2 engines handle different types of Islamic scholarly content.

_Scope:_ Build science trees for high-priority Islamic sciences (the specific sciences determined during the dedicated tree-building research effort per §4.1 and §4.2). Process relevant sources. Validate that extraction correctly handles science-specific conventions. Implement science-specific metadata extensions (§5.4).

_Success criteria:_ At least two non-Arabic-language Islamic science trees are populated with correctly placed, correctly attributed excerpts with proper school-group organization and science-specific metadata.

_What this proves:_ The Phase 2 engines and the excerpt model (§5) work across the full breadth of Islamic sciences, not only Arabic language sciences.

**Milestone 4: Add a second source type.**

_Goal:_ Break the single-source-type assumption. Add a second supported source type. Prove the normalization boundary (§7.6) holds in practice.

_Scope:_ Build a normalizer in the normalization engine (§7.5) for a second source type. Process sources of the new type through the same Phase 2 engines. Verify identical quality.

_Success criteria:_ Sources from both source types produce indistinguishable results in the science trees. No Phase 2 engine code was modified — only Phase 1 code (the source engine and normalization engine) was added or changed.

_What this proves:_ The normalization boundary works in practice. The architecture supports multiple source types as designed in §7.

**Milestone 5: Autonomous discovery and manual input.**

_Goal:_ The source engine actively discovers material, and the owner can provide manual input. Both modes work through the same pipeline.

_Scope:_ Implement autonomous source discovery in the source engine (§7.2) for configured source repositories. Implement the manual input pathway (§2.5) through the source pipeline. Implement batch processing with human gate approval (§9). Begin coverage-driven discovery — the source engine examines which leaves are under-served and searches for sources likely to fill those gaps.

_Success criteria:_ The source engine autonomously discovers, acquires, and processes new sources that measurably improve coverage. The owner can provide manual input that produces correctly placed excerpts in the library. Both modes require the owner's approval at human gates (§9).

_What this proves:_ The application can operate autonomously and accept manual input, scaling from manual operation to supervised automation.

**Milestone 6: Full source diversity.**

_Goal:_ Support fundamentally different source types — not only different formats of books, but web content, recorded lectures, and other knowledge containers.

_Scope:_ Build normalizers for additional source types (web content from scholarly platforms, recorded lectures requiring transcription, and other source types as identified). Process these through the Phase 2 engines. Verify quality.

_Success criteria:_ Excerpts from diverse source types appear in the library alongside book-derived excerpts, with appropriate provenance in source metadata (§7.3). Quality is acceptable after owner review.

_What this proves:_ The architecture works for fundamentally different source types, validating the normalization boundary's design at full diversity.

**Milestone 7: Comprehensive coverage.**

_Goal:_ Systematic sweep of all available sources. The library approaches rich completion (§1.7) across all sciences.

_Scope:_ Continuous autonomous discovery and processing across all configured source repositories. Comprehensive coverage reporting (§3.5). Cross-source quality comparison. The owner uses the library as their primary scholarly reference.

_Success criteria:_ All science tree leaves have multi-source, multi-author coverage. Coverage reports show comprehensive coverage across all primary sciences. Supporting sciences (§1.2) have at least baseline completion (§1.7). The library is a reliable, comprehensive scholarly reference.

---

### 10.3 The Existing Codebase

خزانة ريان builds on the existing ABD codebase (repository: `abd_post_stage0_v1.5`). The repository continues as the codebase, with its structure reorganized to match the architecture defined in this specification (§13.2). The preserve-proven-work principle (§10.1) governs the transition: working code is restructured, not rewritten.

**What carries forward (restructured to fit the target architecture):**

The extraction logic (currently in `tools/extract_passages.py`, approximately 2100 lines) — the core of the atomization and excerpting engines' processing. Proven on إملاء content, with multi-model support.

The consensus mechanism (currently in `tools/consensus.py`, approximately 1700 lines) — the multi-model consensus infrastructure (§2.2). Proven with multiple LLM providers.

The test suite (approximately 1036 tests across multiple test files) — validation of existing pipeline stages.

The gold baselines (in `gold_baselines/` and `3_extraction/gold/`) — hand-crafted ground truth (§2.2) for بلاغة and إملاء extraction. These represent extensive precision work and are carried forward as the foundation of regression testing (§8.3).

The taxonomy trees (in `taxonomy/`) — science trees for four Arabic language sciences (approximately 892 leaves total). These become the first science trees in the library (§13.2.6).

The Shamela normalization tools (currently in `tools/normalize_shamela.py` and related files) — the source pipeline's first normalizer.

The intake and enrichment tools (currently in `tools/intake.py` and `tools/enrich.py`) — source acquisition and metadata enrichment logic for the source engine.

The schemas (in `schemas/`) — structural validation definitions that become the foundation of the schema contracts (§13.4).

The extraction precision rules (in `2_atoms_and_excerpts/`) — binding decisions and checklists governing extraction quality.

**What is restructured:**

The numbered-stage directory layout (`0_intake/`, `1_normalization/`, etc.) is reorganized into the engine-based architecture defined in §13.2. This is a structural reorganization, not a functional rewrite. Each existing component is placed in its correct engine directory. The prior `ARCHITECTURE.md` from the reformation branch introduced the normalization boundary concept; this specification supersedes that document as the authoritative design reference.

**What is not carried forward:**

Superseded normalization specification versions. Archive contents (`archive/`) containing retired documentation. Stale audit reports and analysis documents from early development iterations. These are retired to prevent confusion with current authoritative documentation.

---

---

## §11 — Design Principles

This section states the design principles that govern every decision in خزانة ريان's architecture and implementation. These principles are distilled from the architectural decisions established in §1–§9. When trade-offs arise, these principles are the tiebreaker. They are listed in strict priority order: when two principles conflict, the lower-numbered principle governs.

Each principle is stated as a rule that an implementing agent can apply directly — not as an aspiration. Each principle includes a brief explanation and a reference to the architectural decision it derives from. The complete set of principles is below; no principle exists outside this list.

---

### Principle 1: Accuracy Above All

Every piece of knowledge in the library must be correctly attributed, correctly placed, and correctly represented. An error in the library — a misattributed opinion, a misplaced excerpt, a corrupted text — is worse than a gap in the library, because the owner studies from, memorizes, and teaches from the library's content (§1.6). When the application is uncertain about any content decision, it flags for human review rather than proceeding with a best guess. The application uses multi-model consensus (§2.2), cross-validation, human gates (§9), feedback loops (§8.3), and regression testing (§2.2) to systematically eliminate every detectable error. Accuracy is the highest-priority core property (§1.5).

### Principle 2: Protection from Error

Human error and system error are the primary threats to the library's integrity. The architecture uses defense in depth (§8.1): multiple independent error-catching mechanisms layered so that an error must evade all of them to enter the library undetected. The two-tier content model — verified and flagged knowledge (§2.4, §3.2) — provides structural separation as a last line of defense. Every decision the application makes is auditable (§8.1, Layer 5). Every high-impact action is reversible (§4.4, rollback completeness). No single failure of any detection mechanism permits an error to enter the library without further barriers. Protection is the second-priority core property (§1.5).

### Principle 3: Intelligence at Every Content Decision

Every decision that requires judgment about content, quality, relevance, scholarly context, or organizational structure is made by intelligent reasoning — currently provided by LLMs, defined architecturally as a capability requirement, not a vendor dependency (§1.5). Content decisions include: determining source relevance and trustworthiness (§7.2, §7.4), identifying atom boundaries and types (§2.2), grouping atoms into self-contained excerpts (§5.2), classifying excerpts into taxonomy leaves (§2.2), detecting when taxonomy evolution is needed (§4.4), generating synthesized entries (§6.1), and analyzing correction patterns (§8.3). Deterministic algorithms handle mechanical tasks: schema validation, file I/O, character counting, index maintenance, reference integrity checks. When a decision has a deterministic correct answer, an algorithm handles it. When a decision requires judgment, intelligent reasoning handles it. Intelligence is the third-priority core property (§1.5).

### Principle 4: Self-Containment of Excerpts

A fully-formed excerpt — one that has completed processing by the excerpting and taxonomy engines (§2.2) — must be independently understandable (§5.1). A reader meeting the self-containment standard — or the synthesizing engine generating an entry — can read any single fully-formed excerpt and fully understand what it teaches, who said it, from which scholarly tradition, and where it fits in the structure of the science. No cross-references to other excerpts are required. Self-containment is what makes the library usable: any excerpt can be read, any leaf can be synthesized, and any entry can be studied — independently. An excerpt that fails the self-containment standard (§5.1) must be enriched before it can proceed through its lifecycle (§2.4).

### Principle 5: Living Taxonomy

Science trees are not fixed containers — they evolve as new knowledge reveals finer topic distinctions (§4.4). Evolution is a normal, expected process, not an exceptional event. The trees serve the excerpts, not the other way around: when the content demands finer granularity, the tree grows to accommodate it; when the tree's structure does not match the content's natural organization, the tree changes — the content is never distorted to fit the tree. Evolution is governed by the invariants in §4.4: zero orphans, excerpt non-interference, sibling coherence, entry lifecycle propagation, and rollback completeness.

### Principle 6: Self-Improving System

When the owner corrects an error at a human gate (§9), the correction is not merely applied — it is saved, analyzed for patterns, traced to a root cause, and used to improve the responsible engine's processing rules (§8.3). Every correction makes the application more accurate over time. Proposed rule changes require the owner's approval and regression testing (§2.2) before being applied to production. The scope of improvement is precisely bounded: processing rules improve; the application does not autonomously redesign itself, fine-tune LLMs, or modify this specification (§8.3).

### Principle 7: Source Agnosticism Below the Normalization Boundary

The Phase 2 engines (§2.2) operate identically regardless of source format, source type, or acquisition method. This is not a preference — it is a hard architectural constraint enforced by the normalization boundary (§7.6). No source-format-specific logic, identifiers, structural markers, or assumptions may appear below the boundary. A violation is an architectural bug regardless of convenience. This constraint enables the application to grow indefinitely in source diversity without accumulating complexity in the Phase 2 engines (§7.6).

### Principle 8: Normalizer Freedom Above the Normalization Boundary

Each normalizer in the normalization engine (§7.5) is free to use whatever techniques it needs — complex parsing, LLM assistance, multi-pass processing, format-specific heuristics — to produce conformant output. Normalizer complexity is unlimited and self-contained. The sole requirement is that the normalized package output conforms to the universal schema (§7.5). This freedom ensures that the quality of normalization is never compromised by artificial constraints on implementation approach.

### Principle 9: Entries as Primary Knowledge Product

Entries (§6) are a primary knowledge product of the library alongside excerpts — not a convenience layer or a summary view. The owner's primary interaction with the library is reading and studying entries. Entries have two distinct layers: the factual layer (traceable to specific excerpts) and the analytical layer (the synthesizing engine's intellectual contribution). Both layers together constitute the entry's value (§1.6, §6.1). Design decisions must give entries full architectural weight at every stage — in storage, in quality assurance, in staleness tracking, and in regeneration.

### Principle 10: Incremental Value

Every implementation milestone produces a usable library (§10.1). The library is usable — for the sciences and sources covered so far — at the end of every milestone, not only at eventual completion. No milestone depends on future milestones for its value. Every design decision must ensure the application works well at its current scale, not only at its eventual full scale.

### Principle 11: Prove Before Expanding

No new source type, science, automation level, or architectural capability is built until the preceding capability is proven to produce correct, owner-validated output (§10.1). The Phase 2 engines must be validated before autonomous discovery is built. The normalization boundary must hold with one source type before a second is added. One science must be fully working before additional sciences are loaded. This principle prevents building on unvalidated assumptions and is the primary guard against wasted implementation effort.

### Principle 12: Coverage-Driven Prioritization

Once the Phase 2 engines are proven (Milestone 1, §10.2), the choice of what to process next is driven by which taxonomy leaves need more coverage (§3.5), not by what material is easiest to acquire or what source type is most convenient to implement. The library's value comes from comprehensive, exhaustive coverage of the scholarly tradition's diversity (§1.7); coverage gaps are the application's primary concern after engine correctness is established. Coverage is natural and quality-preserving — it does not trigger quality-lowering gap-filling.

---

---

## §12 — Relationship to Current Codebase

This section specifies the relationship between خزانة ريان and the existing ABD codebase from which it evolves. It defines repository continuity, what components are preserved and how they map to the target architecture, and what changes in the transition. This section describes factual references to existing code and files; it is not a migration guide — the specific steps for restructuring are operational decisions made during Milestone 1 (§10.2).

---

### 12.1 Repository Continuity

خزانة ريان is built on top of the existing ABD codebase, not from scratch. The repository (`abd_post_stage0_v1.5`) continues as the codebase, with its structure reorganized to match the architecture defined in this specification — specifically the repository layout in §13.2 and the seven-engine processing architecture in §2.2. A new branch is created for the خزانة ريان work, preserving the current master as a reference point.

Repository continuity means: the git history is preserved, the existing tests continue to run (relocated but not deleted), and validated components continue to function during and after the restructuring. Continuity does not mean the directory layout is unchanged — it is reorganized substantially (§12.3).

---

### 12.2 What Is Preserved

The following components from the existing codebase are preserved and restructured into the target architecture. The preserve-proven-work principle (§10.1) governs: these components work, and working code is more valuable than rewritten code.

**Extraction logic** (currently in `tools/extract_passages.py`) — maps to the atomization engine (محرك التذرير) and excerpting engine (محرك الاقتطاف) under `engines/atomization/` and `engines/excerpting/` per §13.2.4. The existing code currently implements responsibilities that span both engines; separation into distinct engine directories occurs during restructuring, guided by the conceptual boundaries defined in §2.2.

**Consensus mechanism** (currently in `tools/consensus.py`) — maps to the shared consensus infrastructure under `shared/consensus/` per §13.2.5. The consensus mechanism serves multiple engines and is therefore shared infrastructure, not owned by any single engine.

**Shamela normalizer** (currently in `tools/normalize_shamela.py`) — maps to the normalization engine (محرك التطبيع) under `engines/normalization/src/normalizers/` per §13.2.4. This becomes the first normalizer in the normalization engine.

**Structure discovery** (currently in `tools/discover_structure.py`) — integrates into the normalization engine per the normalization boundary requirement (§7.6). Structure discovery is part of normalization because structural signals exist in format-specific markup that is available only before format stripping (§7.5).

**Intake and enrichment tools** (currently in `tools/intake.py` and `tools/enrich.py`) — map to the source engine (محرك المصادر) under `engines/source/` per §13.2.4. These handle source acquisition and metadata enrichment responsibilities defined in §7.2 and §7.3.

**Test suite** (all existing test files) — reorganized to co-locate with their respective engine directories under each engine's `tests/` directory per §13.2.4. Test co-location is a binding architectural constraint (§13.2.4), not a suggestion.

**Gold baselines** (in `gold_baselines/` and `3_extraction/gold/`) — map to the `gold/` directory at the repository root per §13.2.7. Gold baselines are precious project-level assets (§2.2) that serve multiple engines for regression testing.

**Schemas** (in `schemas/`) — become the foundation of the schema contracts (§13.4) in the `schemas/` directory at the repository root per §13.2.3.

**Taxonomy trees** (in `taxonomy/`) — map to `library/sciences/` per §13.2.6. The four Arabic language science trees (approximately 892 leaves total) become the first science trees in the library.

**Extraction precision rules** (in `2_atoms_and_excerpts/`) — the binding decisions and checklists governing extraction quality. These inform the SPEC.md files for the atomization and excerpting engines.

---

### 12.3 What Changes

**Directory structure.** The numbered-stage layout (`0_intake/`, `1_normalization/`, etc.) is reorganized into the engine-based architecture defined in §13.2: `engines/` for the seven processing engines, `shared/` for cross-engine infrastructure, `library/` for the knowledge product, `schemas/` for inter-engine contracts, and `gold/` for gold baselines. The restructure plan from the reformation branch provides guidance for the physical reorganization of files.

**Documentation.** All documentation is updated to reflect the خزانة ريان architecture. This specification (VISION.md) becomes the Level 0 design authority (§13.1). The existing `CLAUDE.md`, `REPO_MAP.md`, and `ARCHITECTURE.md` are replaced. A new root CLAUDE.md is created per the requirements in §13.3.2. Per-engine CLAUDE.md and SPEC.md files (§13.3.3, §13.1) are created for each engine.

**Scope expansion.** The four Arabic language science trees are now part of a larger collection that will eventually include all Islamic and supporting sciences per §4.3. The source pipeline is extended to support multiple source types (§7.5) and autonomous discovery (§7.2). The synthesizing engine (§6) is built to generate entries — a capability not present in the existing codebase.

**Application identity.** All references to "ABD," "Ilm Digest," or "ID" in code, documentation, and configuration are updated to خزانة ريان / KR.

---

---

## §13 — Documentation Architecture and Repository Layout

### 13.0 Scope

This section specifies the project's documentation architecture, the repository's physical layout, the principles governing how AI agents interact with the project's documentation and code, and the maintenance rules that keep documentation accurate over the project's lifetime. These concerns are unified in a single section because they are inseparable: a documentation decision (where a specification lives) is simultaneously a repository decision (which directory contains it) and an agent interaction decision (what context the agent receives when working on that component). Treating them as separate concerns creates the disconnections that cause agent errors.

This section defines _where_ documentation and code live and _how_ agents navigate them. It does not define the content of individual specifications — that is the responsibility of each specification document itself. It does not define exact file formats for schemas, configuration, or data — those are implementation decisions specified in the relevant per-component documentation.

---

### 13.1 Documentation Hierarchy

The project's documentation is organized into four levels. Each level serves a different function, addresses a different scope, and carries a different type of authority. The levels form a strict precedence hierarchy: when a lower-level document conflicts with a higher-level document on matters within the higher-level document's scope, the higher-level document governs.

**Level 0 — This specification (VISION.md).** The single authoritative design document for خزانة ريان. VISION.md defines the application's identity (§1), the library's structure (§3), the vocabulary used throughout the project (§2), the architectural boundaries governing all components (§2.2, §7), the design principles that govern every decision (§11), the implementation strategy (§10), and the physical layout of the repository (§13.2). VISION.md is read by every agent before any other document when architectural or design questions arise. VISION.md defines _what_ the application is and _why_ it is designed the way it is. It does not contain implementation-level specifics: exact schemas, prompt templates, algorithm internals, or code-level interfaces. Changes to VISION.md require the owner's review and approval.

**Level 1 — Root CLAUDE.md.** The operational entry point for implementing agents. The root CLAUDE.md is the first file that Claude Code loads at the start of every session — it is injected into the agent's context automatically. The root CLAUDE.md provides three things: a concise map of the repository (what directories exist and what they contain), the universally applicable rules that govern all work sessions regardless of which engine is being worked on, and a pointer to current priorities. The root CLAUDE.md does not contain engine-specific information, implementation details, or design rationale — those belong in lower-level documents. The root CLAUDE.md references VISION.md as the design authority. The design principles governing the root CLAUDE.md's content are specified in §13.3.

**Level 2 — Per-engine specifications (SPEC.md) and schema contracts.** Each of the seven engines defined in §2.2, and each cross-engine shared component, has its own SPEC.md containing the implementation-level detail that VISION.md intentionally omits: input and output schemas (by reference to the schema contracts in §13.4), processing logic, validation rules, prompt templates, edge cases, error handling, and testing requirements. SPEC.md files are authoritative for their component's implementation details. They extend the definitions and constraints established in VISION.md and §2 but do not contradict them. When a SPEC.md needs to be more specific than VISION.md about a concept defined in §2, it extends the glossary definition with component-specific detail, explicitly noting that it is an extension. The schema contracts defined in §13.4 are also Level 2 documents — they define the data boundaries between engines.

**Level 3 — Per-science documentation (SCIENCE.md).** Each science that the library covers (per §4.3) has its own SCIENCE.md containing: the scholarly rationale for the science's tree structure (applying §4.1's qualification criteria and §4.2's construction principles), science-specific excerpt metadata requirements (what additional metadata this science requires beyond the universal excerpt definition in §5), the inventory of schools within the science and how school affiliation is assessed for authors and texts (per §2.4), and any unique challenges the science presents for extraction, taxonomy, or synthesis. SCIENCE.md files are created during the dedicated tree-building research effort for each science. They extend the universal definitions in §4 (science trees) and §5 (excerpts) with science-specific detail.

**Authority flow.** Authority flows downward: VISION.md governs SPEC.md files, which govern their engine's code. Detail flows upward: when implementation reveals that a VISION.md definition is insufficient, the gap is surfaced to the owner and resolved in VISION.md — not patched locally in a SPEC.md. When a SPEC.md needs a term that is used across multiple engines, the term is promoted to §2 — it is not defined independently in multiple SPEC.md files.

---

### 13.2 Repository Layout

The repository's physical layout embodies the application's architecture. The directory structure is not incidental organization — it is architectural infrastructure that determines how agents navigate the project, what context they receive, and how effectively they can work. Every directory exists for a specific architectural reason. No directory exists for organizational convenience alone.

The canonical repository layout is:

```
kr/
├── VISION.md
├── CLAUDE.md
│
├── .claude/
│   ├── agents/
│   ├── commands/
│   └── settings.json
│
├── schemas/
│
├── engines/
│   ├── source/
│   │   ├── CLAUDE.md
│   │   ├── SPEC.md
│   │   ├── src/
│   │   └── tests/
│   ├── normalization/
│   │   ├── CLAUDE.md
│   │   ├── SPEC.md
│   │   ├── src/
│   │   │   └── normalizers/
│   │   └── tests/
│   ├── passaging/
│   │   ├── CLAUDE.md
│   │   ├── SPEC.md
│   │   ├── src/
│   │   └── tests/
│   ├── atomization/
│   │   ├── CLAUDE.md
│   │   ├── SPEC.md
│   │   ├── src/
│   │   └── tests/
│   ├── excerpting/
│   │   ├── CLAUDE.md
│   │   ├── SPEC.md
│   │   ├── src/
│   │   └── tests/
│   ├── taxonomy/
│   │   ├── CLAUDE.md
│   │   ├── SPEC.md
│   │   ├── src/
│   │   └── tests/
│   └── synthesis/
│       ├── CLAUDE.md
│       ├── SPEC.md
│       ├── src/
│       └── tests/
│
├── shared/
│   ├── CLAUDE.md
│   ├── consensus/
│   │   ├── SPEC.md
│   │   ├── src/
│   │   └── tests/
│   ├── validation/
│   │   ├── src/
│   │   └── tests/
│   └── feedback/
│       ├── SPEC.md
│       ├── src/
│       └── tests/
│
├── library/
│   ├── sciences/
│   │   └── [per science]/
│   │       ├── SCIENCE.md
│   │       ├── tree.yaml
│   │       ├── tree_history/
│   │       └── content/
│   └── sources/
│       ├── registry.yaml
│       └── frozen/
│
└── gold/
```

The following subsections define each top-level directory, its purpose, and the rules governing its contents.

#### 13.2.1 Root Files

**VISION.md** — this specification. Level 0 (§13.1). The single authoritative design document. Located at the repository root so that every agent encounters it first when exploring the project.

**CLAUDE.md** — the root operational guide. Level 1 (§13.1). Located at the repository root because Claude Code automatically loads the root CLAUDE.md at the start of every session. Its content requirements are specified in §13.3.2.

#### 13.2.2 The `.claude/` Directory

The `.claude/` directory contains Claude Code's agent infrastructure: subagent definitions, slash commands, and hook configurations. This directory is managed by Claude Code's tooling and follows Claude Code's conventions.

**`.claude/agents/`** contains subagent definition files. Subagents are specialized agent configurations with their own system prompts, tool permissions, and isolated context windows. They are used to delegate focused tasks without polluting the main agent's context. Subagent definitions are created incrementally as the project identifies recurring specialized tasks. The specific subagents to be created, their prompts, and their tool permissions are not specified in VISION.md — they are defined as the project's workflows mature. *[Non-normative: anticipated subagent categories include a research subagent for investigating science tree structures during Level 3 documentation work, a review subagent for examining extraction output at human gates, and an integrity subagent for running periodic library integrity checks. These are anticipated, not specified — they may or may not materialize as described.]*

**`.claude/commands/`** contains slash command definitions — reusable prompt templates for common workflows. Slash commands are created incrementally as the project identifies recurring operations that benefit from standardized prompting.

**`.claude/settings.json`** contains hook definitions and permission configurations. Hooks are shell commands that Claude Code runs automatically at specific lifecycle points (before or after tool use, on session start, on commit). Hooks provide mechanical enforcement of project rules — they catch violations deterministically rather than relying on the agent's instruction-following. The specific hooks to be implemented are not specified in VISION.md; they are defined in `.claude/settings.json` as the project's quality gates are established. *[Non-normative: anticipated hook categories include running tests after code changes, validating schema conformance after engine output changes, and verifying that documentation was updated alongside code changes.]*

#### 13.2.3 The `schemas/` Directory

The `schemas/` directory contains the inter-engine data contracts — the formal specifications of what each engine produces and what its downstream consumer expects. Schema contracts cover every engine-to-engine boundary in the processing pipeline; the most architecturally significant is the normalized package schema, which gives concrete, validatable form to the normalization boundary (§2.2, §7.6). Schemas are located at the repository's top level — not nested under `engines/` or under any documentation directory — because they are shared boundary definitions that belong to neither the producing engine nor the consuming engine. Their top-level placement signals their architectural importance: schemas are first-class project artifacts, not supporting documentation.

Each schema file defines the data contract for one engine-to-engine boundary. The producing engine's SPEC.md references the schema as its output specification ("this engine's output conforms to `schemas/[name]`"). The consuming engine's SPEC.md references the same schema as its input specification ("this engine's input conforms to `schemas/[name]`"). When a schema changes, both the producing and consuming engine's SPEC.md files must be reviewed. The full specification of schema contracts is in §13.4.

#### 13.2.4 The `engines/` Directory

The `engines/` directory contains all seven processing engines defined in §2.2. Each engine has its own subdirectory with a uniform internal structure: a CLAUDE.md for agent context (§13.3.3), a SPEC.md for the engine's full specification (§13.1, Level 2), a `src/` directory for source code, and a `tests/` directory for tests. This co-location principle — specification, code, and tests together in one directory — is a binding architectural constraint, not a suggestion. Co-location ensures that an agent working on an engine finds everything it needs in one place without navigating parallel directory trees.

The seven engine directories under `engines/` correspond exactly to the seven engines defined in §2.2:

`engines/source/` — the source engine (§2.2: محرك المصادر). Phase 1.
`engines/normalization/` — the normalization engine (§2.2: محرك التطبيع). Phase 1. Contains `src/normalizers/` with per-source-type normalizer modules as subdirectories (one per supported source type per §7.5).
`engines/passaging/` — the passaging engine (§2.2: محرك التقطيع). Phase 2.
`engines/atomization/` — the atomization engine (§2.2: محرك التذرير). Phase 2.
`engines/excerpting/` — the excerpting engine (§2.2: محرك الاقتطاف). Phase 2.
`engines/taxonomy/` — the taxonomy engine (§2.2: محرك التصنيف). Phase 2.
`engines/synthesis/` — the synthesizing engine (§2.2: محرك التوليف). Phase 2.

**The directory structure represents the target architecture.** §2.2 states that the seven engines are "conceptual processing responsibilities" and that "a single codebase module may currently implement multiple engines' responsibilities." An engine directory may exist before its code is fully separated from another engine's code. When this is the case, the engine's CLAUDE.md states the current implementation state explicitly — for example: "Status: shares implementation with the excerpting engine. Primary code is in `engines/excerpting/src/`." The directory exists as the engine's conceptual home and the location for its SPEC.md and CLAUDE.md even when dedicated source code has not yet been separated.

No engine directory is created for a component that is not one of the seven engines in §2.2. If the application's architecture evolves to add, remove, or merge engines, that change is first made in VISION.md §2.2 (which requires the owner's approval), and then the directory structure is updated to match.

**Test co-location and aggregate discovery.** Each engine's tests live in its own `tests/` directory, not in a centralized test directory. This ensures that tests are immediately visible when working on the engine they validate. A single command must be able to discover and run all tests across all engines — the root CLAUDE.md documents this command. The test runner's configuration (which discovers tests across `engines/*/tests/` and `shared/*/tests/`) is an implementation detail.

**Normalization boundary in the directory structure.** The normalization boundary (§2.2, §7.6) falls between `engines/normalization/` and `engines/passaging/`. This boundary is logical, not physical — there is no subdirectory separator. The boundary's enforcement is through the engine SPEC.md files, the schema contracts (§13.4), and code review. Each Phase 2 engine's CLAUDE.md states that it is a Phase 2 engine and that no source-format-specific logic may appear in its code.

#### 13.2.5 The `shared/` Directory

The `shared/` directory contains infrastructure that serves multiple engines but is not itself an engine. The inclusion criterion is strict: code belongs in `shared/` only when it is called by two or more engines and does not conceptually belong to any single engine. Code that serves a single engine belongs in that engine's `src/` directory, even if it could theoretically be reused. This criterion prevents `shared/` from becoming a dumping ground for code that lacks a clear home.

The `shared/` directory has its own CLAUDE.md that states this inclusion criterion and describes the contents of each subdirectory. Substantial shared components (those with their own processing logic and validation requirements) have their own SPEC.md.

The currently planned contents of `shared/` are:

`shared/consensus/` — the multi-model consensus mechanism defined in §2.2. This is cross-engine infrastructure called by multiple Phase 2 engines (atomization, excerpting, taxonomy) and potentially by the source engine during trustworthiness evaluation (§7.4). The consensus mechanism has its own SPEC.md because it is a substantial component with its own processing logic, configuration, and testing requirements.

`shared/validation/` — algorithmic validation tools used across engines: schema validation, structural integrity checks, reference verification, and other deterministic checks described in §8.1 (Layer 2: Detection). These are the mechanical validation counterparts to the LLM-driven intelligent validation that each engine performs internally.

`shared/feedback/` — the feedback loop infrastructure defined in §2.2 and §8.3: correction storage, pattern analysis, rule improvement proposals, and regression testing coordination. The feedback system spans all engines that have human gates (§9), making it inherently cross-engine. The feedback system has its own SPEC.md because it is a substantial component.

Additional shared components may be added as the project develops, provided they meet the inclusion criterion.

#### 13.2.6 The `library/` Directory

The `library/` directory contains the library itself — the persistent, structured knowledge product defined in §1.1 and §3.1. This is the product of the application, not its machinery. The separation between `engines/` (machinery) and `library/` (product) is a physical expression of the distinction established in §1.1 between the application and the library.

**`library/sciences/`** contains one subdirectory per science that the library covers. Each science's subdirectory contains: SCIENCE.md (Level 3 per-science documentation per §13.1), `tree.yaml` (the current science tree definition per §4), `tree_history/` (previous tree versions, retained for rollback and audit per §2.3 and §4.4), and `content/` (placed excerpts and generated entries). The internal structure of `content/` — how excerpts are organized by leaf, how entries are stored, how the verified/flagged separation (§3.2) is maintained in storage — is specified in the taxonomy engine's SPEC.md (for excerpt placement) and the synthesizing engine's SPEC.md (for entry storage). VISION.md does not specify this internal structure because it is implementation detail that may evolve as the engines are built.

**`library/sources/`** contains source metadata and frozen source files. `registry.yaml` is the source deduplication registry maintained by the source engine (§7.2). `frozen/` contains immutable copies of acquired sources (per the frozen source definition in §2.5). The internal organization of `frozen/` and the schema of `registry.yaml` are specified in the source engine's SPEC.md.

Multiple engines write to `library/`: the taxonomy engine places excerpts and manages tree evolution, the synthesizing engine generates and stores entries, the source engine stores frozen sources and metadata. This is by design — the library is the shared output of the processing pipeline. Write access conventions (which engine writes to which part of `library/`) are specified in the respective engine SPEC.md files.

#### 13.2.7 The `gold/` Directory

The `gold/` directory contains gold baselines — hand-crafted, human-verified extraction outputs defined in §2.2. Gold baselines are located at the repository's top level because they are precious project-level assets that serve multiple engines for regression testing (§8.3). They are not owned by any single engine. They are created through meticulous manual work by the owner and represent the definitive correct output for their passages.

The `gold/` directory is organized by science, with each science's subdirectory containing the gold baseline files for passages from that science's sources. The internal format of gold baseline files is specified in the relevant engine SPEC.md files (primarily the excerpting and taxonomy engines, whose output gold baselines validate).

Gold baselines are never auto-generated, never modified by automated processes, and never deleted without the owner's explicit approval. They grow slowly as the owner validates extraction output on new passages. Their value increases over time as they accumulate.

---

### 13.3 Agent Context Engineering

The primary implementer of خزانة ريان is Claude Code — an AI agent that begins each session with no memory of previous sessions and with only the content of the root CLAUDE.md as its initial project context. The effectiveness of every work session depends on how efficiently the agent acquires the context it needs for its specific task. This subsection specifies the principles that govern how context is structured and delivered to agents throughout the repository.

#### 13.3.1 The Progressive Disclosure Principle

Context is delivered to agents in layers, from general to specific, with each layer loaded only when it is relevant to the agent's current task. This is the principle of progressive disclosure, and it is the governing principle of all agent-facing documentation in the project.

The loading layers described below are distinct from the documentation levels in §13.1. Levels describe authority (Level 0 has the highest authority). Layers describe loading order (Layer 1 is loaded first). The two hierarchies are deliberately different: VISION.md is Level 0 (highest authority) but Layer 4 (loaded on demand) because agents do not need the full specification in every session — they need it when architectural questions arise. The root CLAUDE.md is Level 1 (lower authority) but Layer 1 (loaded first) because it provides the operational context that every session requires.

The layers, in order of loading:

**Layer 1 (always loaded): Root CLAUDE.md.** Provides the repository map, universally applicable rules, and current priorities. This layer is loaded automatically by Claude Code at the start of every session. Because it is always loaded, it must contain only information that is relevant to every possible task. Engine-specific information, implementation details, and design rationale do not belong in this layer.

**Layer 2 (loaded on directory entry): Engine CLAUDE.md.** When an agent enters an engine directory (e.g., `engines/atomization/`), Claude Code's recursive CLAUDE.md loading automatically injects the engine's CLAUDE.md into the agent's context. This layer provides engine-specific operational information: what this engine does, its current implementation state, required reading before working on it, how to run its tests, and its key constraints. This context supplements the root CLAUDE.md rather than replacing it — both are active simultaneously.

**Layer 3 (loaded on demand): SPEC.md and referenced documents.** When the agent needs to understand an engine's full specification, it reads the engine's SPEC.md. When it needs to understand a schema contract, it reads the relevant file in `schemas/`. When it needs science-specific context, it reads the relevant SCIENCE.md. These documents are read by the agent when its task requires them — they are not pre-loaded.

**Layer 4 (loaded on demand): VISION.md.** When the agent needs to understand architectural decisions, vocabulary definitions (§2), or cross-cutting design principles (§11), it reads the relevant section of VISION.md. VISION.md is the reference of last resort for "why is it designed this way?" questions.

This layering ensures that agents always have the context they need without being overwhelmed by irrelevant information. An agent fixing a bug in the Shamela normalizer receives the root CLAUDE.md (Layer 1) and the normalization engine's CLAUDE.md (Layer 2) automatically, then reads the normalization SPEC.md (Layer 3) if needed. It never receives the atomization engine's CLAUDE.md, the taxonomy SPEC.md, or a Fiqh SCIENCE.md — none of which are relevant to its task.

#### 13.3.2 Root CLAUDE.md Requirements

The root CLAUDE.md is the highest-leverage document in the project for agent behavior. Because it is loaded into every session, its quality directly affects every task the agent performs. The following requirements govern its content.

**Conciseness requirement.** The root CLAUDE.md must not exceed 100 lines. Shorter is better. Every line must be universally applicable — relevant to every possible work session regardless of which engine, science, or task is involved. Lines that are relevant only to specific engines or tasks belong in the engine's CLAUDE.md or in a referenced document, not in the root CLAUDE.md.

*[Non-normative — rationale: research on AI agent instruction-following demonstrates that as the number of instructions in an agent's context grows, compliance with all instructions — including the critical ones — degrades uniformly. A bloated root CLAUDE.md does not merely waste context; it actively reduces the agent's compliance with the project's most important rules. The conciseness requirement is not a stylistic preference — it is an architectural constraint that protects the quality of every work session.]*

**Required content.** The root CLAUDE.md must contain the following categories of information. Additional categories may be added only by amending this section of VISION.md — the root CLAUDE.md must not accumulate content that is not sanctioned here:

_Identity._ The application's name (خزانة ريان / KR) and a one-line description, with a reference to VISION.md for the full specification.

_Repository map._ A brief listing of top-level directories and what each contains. The map provides orientation; it does not describe contents in detail.

_Pipeline summary._ The seven-engine processing pipeline (§2.2) shown in processing order with the normalization boundary marked. This summary provides the architectural overview that agents need to understand where their current task fits in the whole.

_Pre-work protocol._ The steps an agent must follow before beginning work on any engine: enter the engine directory (triggering its CLAUDE.md to load), read the engine's SPEC.md, and read the input/output schemas referenced in the SPEC.md.

_Post-work protocol._ The steps an agent must follow after completing work on any engine: run the engine's tests, update the SPEC.md if behavior changed, update the engine's CLAUDE.md if state changed, flag vocabulary changes for §2 review.

_Architectural constraints._ The constraints that apply universally across all engines — the normalization boundary rule (§7.6), the self-containment requirement for excerpts (§5.1), the multi-model consensus requirement for content decisions (§2.2), and the human gate requirement before irreversible library changes (§9). These are brief restatements (not redefinitions) of constraints specified fully in VISION.md, serving as active reminders in the agent's context.

_Current priorities._ A pointer to or brief statement of what is currently being worked on and what is next. This section is updated frequently — after every work session that changes priorities.

**Prohibited content.** The root CLAUDE.md must not contain: engine-specific implementation details, engine-specific state or known issues (those belong in the engine's CLAUDE.md), code style guidelines (the agent learns style from existing code), design rationale (that belongs in VISION.md), or any content that is relevant to fewer than all engines.

#### 13.3.3 Engine CLAUDE.md Requirements

Each engine directory and each substantial shared component directory contains its own CLAUDE.md. This file is automatically loaded by Claude Code when an agent enters the directory. It provides the engine-specific operational context that the root CLAUDE.md omits.

**Conciseness requirement.** Engine CLAUDE.md files must not exceed 50 lines. They provide orientation and pointers, not exhaustive documentation — that is the SPEC.md's role.

**Required content.** Each engine CLAUDE.md must contain:

_Engine identity._ The engine's name (both English and Arabic per §2.2) and a one-sentence description of its responsibility, referencing its §2.2 definition.

_Required reading._ A specific list of documents the agent must read before working on this engine, with section references where applicable. This list always includes the engine's SPEC.md and its input/output schemas. It may include specific sections of VISION.md that are particularly relevant to this engine.

_Current state._ The engine's implementation status (not started, in progress, working, proven), the number of passing and failing tests, and a brief list of known issues. This section is updated after every work session that changes the engine's state.

_Commands._ The specific commands to run the engine's tests, to run the engine on sample input, and to validate the engine's output against its schema.

_Key constraints._ The two or three most critical constraints specific to this engine, briefly stated. These are not redefinitions — they are reminders that point to the authoritative statement in VISION.md or in the engine's SPEC.md.

---

### 13.4 Inter-Engine Contracts

The seven engines defined in §2.2 form a processing pipeline where each engine's output becomes the next engine's input. The data contract at each boundary — what the producing engine guarantees about its output and what the consuming engine requires of its input — must be explicitly defined, shared between both sides, and validatable. These contracts are the project's primary mechanism for ensuring that engines can be developed, tested, and improved independently without breaking the pipeline.

#### 13.4.1 Schema Contract Principles

Each engine-to-engine boundary has a schema contract stored in the `schemas/` directory (§13.2.3). A schema contract is a single document that specifies the structure, types, constraints, and invariants of the data that crosses that boundary.

**Shared ownership.** A schema contract is not owned by the producing engine or the consuming engine — it is owned by both. The producing engine's SPEC.md states: "This engine's output conforms to `schemas/[name]`." The consuming engine's SPEC.md states: "This engine's input conforms to `schemas/[name]`." When a schema contract changes, both engines' SPEC.md files must be reviewed and updated if affected.

**Single source of truth.** The schema contract in `schemas/` is the authoritative definition of the boundary data. Engine SPEC.md files reference it but do not redefine it. If a SPEC.md needs to discuss the schema for explanation purposes, it does so by reference, not by restating the schema's content.

**Validatable.** Schema contracts must be precise enough to support algorithmic validation — a tool can check whether a given data artifact conforms to the schema. This enables the `shared/validation/` tooling (§13.2.5) to automatically verify schema conformance as part of the pipeline's integrity checks (§8.4).

#### 13.4.2 Schema Contract Inventory

The following schema contracts exist, one per engine-to-engine boundary in the processing pipeline:

The **normalized package schema** defines the output of the normalization engine (محرك التطبيع) and the input to the passaging engine (محرك التقطيع). This schema is the normalization boundary (§2.2, §7.6) expressed in concrete, validatable terms. Everything above this schema is source-format-specific; everything below it is source-agnostic.

The **passage schema** defines the output of the passaging engine (محرك التقطيع) and the input to the atomization engine (محرك التذرير).

The **atoms schema** defines the output of the atomization engine (محرك التذرير) and the input to the excerpting engine (محرك الاقتطاف).

The **excerpt schema** defines the output of the excerpting engine (محرك الاقتطاف) and the input to the taxonomy engine (محرك التصنيف). This schema specifies the structure of a draft excerpt (per the excerpt lifecycle in §2.4) including all required universal metadata for self-containment (§5.1).

The **entry schema** defines the output of the synthesizing engine (محرك التوليف). This schema has no downstream consuming engine — the entry is a terminal product read by the owner.

The **placed excerpt schema** defines the format of placed excerpts as stored in the library and read by the synthesizing engine (محرك التوليف) as its input. This schema is owned jointly by the taxonomy engine (which writes placed excerpts to the library) and the synthesizing engine (which reads them for entry generation). The placed excerpt schema extends the excerpt schema (above) with confirmed placement metadata (confirmed leaf path rather than proposed path) and any post-review metadata added during the human gate process. If the placed excerpt format is identical to the draft excerpt format with only lifecycle-stage changes, this schema may be a documented extension of the excerpt schema rather than a separate file.

Additional schemas may exist for internal boundaries that are identified during engine development. The source engine's output (frozen source plus metadata) feeds the normalization engine, but this boundary is internal to Phase 1 and its schema is specified in the source engine's SPEC.md rather than in `schemas/`, because it is not a boundary that the normalization boundary principle needs to enforce.

The exact format and content of each schema contract are defined when that schema is first created during engine development. The format choice (YAML schema, JSON Schema, or another format) is an implementation decision made at creation time and documented in the schema file itself. VISION.md does not prescribe the format.

---

### 13.5 Agent Infrastructure

Beyond documentation, the project uses Claude Code's built-in infrastructure features — subagents, slash commands, and hooks — to support agent effectiveness and enforce project rules mechanically. This infrastructure lives in the `.claude/` directory (§13.2.2).

#### 13.5.1 Subagents

Subagents are specialized agent configurations that run in isolated context windows. When the main agent delegates a task to a subagent, the subagent receives only its own system prompt, the project's CLAUDE.md files, and the task-specific context — not the main agent's full conversation history. This isolation prevents context pollution: concerns from one engine's work session do not leak into another engine's work session.

Subagent definitions are created incrementally as the project identifies recurring specialized tasks. VISION.md does not specify individual subagent definitions — those are created, tested, and refined as the project's workflows mature. When a subagent definition is created, it is documented in the subagent's definition file (in `.claude/agents/`) with its name, description, intended use, and tool permissions.

#### 13.5.2 Hooks

Hooks provide mechanical enforcement of project rules. Where a rule can be checked deterministically (tests pass, schema validates, specific files were modified), a hook can enforce it without relying on the agent's instruction-following. Mechanical enforcement is more reliable than instructional compliance because it cannot be ignored, forgotten, or deprioritized by the agent.

Hook definitions are created incrementally. VISION.md does not specify individual hook implementations. The principle that governs hook creation is: when a project rule is repeatedly violated despite being documented, and when the violation can be detected deterministically, a hook should be created to enforce it. Hooks are documented in `.claude/settings.json` and their purpose is described in comments or accompanying documentation within the `.claude/` directory.

#### 13.5.3 Slash Commands

Slash commands are reusable prompt templates for common operations. They reduce the risk of inconsistent or incomplete task descriptions by packaging proven prompts into repeatable commands. Slash command definitions live in `.claude/commands/` and are created incrementally as the project identifies operations that benefit from standardized prompting.

---

### 13.6 Documentation Maintenance

Documentation that does not accurately reflect the project's current state is worse than absent documentation — it actively misleads agents into making decisions based on false assumptions. The following rules govern how documentation is maintained.

#### 13.6.1 The Contemporaneous Update Rule

When a work session changes an engine's behavior, that engine's SPEC.md is updated in the same work session. When a work session changes an engine's state (implementation status, test count, known issues), that engine's CLAUDE.md is updated in the same work session. When a work session changes the application's architecture or vocabulary, VISION.md is updated (or an update is flagged for the owner's review) in the same work session. A task is not complete until the documentation matches the code.

This rule is stated in the root CLAUDE.md's post-work protocol as an active reminder. It may additionally be enforced by a hook that detects code changes without corresponding documentation changes, if such a hook proves feasible and valuable.

#### 13.6.2 Single Source of Truth

Each piece of information has exactly one authoritative location. Other documents may reference it by explicit citation (stating where the authoritative definition lives), but they do not restate, paraphrase, or summarize it in a way that creates a second source. When two documents contain statements about the same concept, one must be an explicit reference to the other — not an independent statement.

The authoritative locations for the project's key concepts are:

Vocabulary definitions: §2.
Architectural boundaries: §2.2 (the seven engines, the normalization boundary), §13.2 (repository layout), §13.4 (schema contracts).
Engine behavior: each engine's SPEC.md.
Boundary data formats: the schema contracts in `schemas/`.
Science-specific scholarly decisions: each science's SCIENCE.md.
Current operational state: the relevant CLAUDE.md file (root for project-wide state, engine-level for engine-specific state).
Design principles: §11.

When an agent or the owner discovers that two documents contain conflicting statements about the same concept, this is a documentation bug. Resolution: identify which document is authoritative for that concept (per the hierarchy above), correct the non-authoritative document to reference the authoritative one, and verify that no other documents contain stale statements about the same concept.

#### 13.6.3 Documentation Before Implementation

For any new engine, any new shared component, or any significant change to an existing engine's behavior, the documentation is written before the code. The SPEC.md is written (or updated) first; the code is then written to conform to the SPEC.md. This forces clarity of thought: if the specification cannot describe precisely what the component should do, the component is not ready to be built.

This principle applies to new development and to significant changes. It does not apply to trivial bug fixes, minor refactoring, or exploratory work that will be reviewed and documented afterward. The threshold for "significant change" is: if the change would affect the engine's SPEC.md (new behavior, changed interface, altered invariants), the SPEC.md is updated first.

#### 13.6.4 Staleness Prevention

Stale documentation arises from three causes: code changes without documentation updates (violation of §13.6.1), documentation that restates rather than references (violation of §13.6.2), and abandoned documentation for components that no longer exist. The project prevents each cause through the following mechanisms:

The contemporaneous update rule (§13.6.1) prevents cause one. The single source of truth rule (§13.6.2) prevents cause two. For cause three: when a component is removed or substantially restructured, all documentation associated with it (SPEC.md, CLAUDE.md, SCIENCE.md, schema contracts, references from other documents) is identified and updated or removed in the same work session.

Additionally, each engine's CLAUDE.md contains a "current state" section that is inherently time-sensitive (test counts, known issues, implementation status). This section's accuracy is verified at the start of each work session on that engine: the agent runs the tests and compares the results to the stated counts. If they differ, the CLAUDE.md is updated before any other work begins.

---

*[End of §13. This section defines the project's documentation architecture and repository layout. It is a living section: as the project introduces new documentation types, new repository directories, or new agent infrastructure, this section is updated to reflect the changes.]*

---

## Changelog

- 1.0.1 (2026-03-03): Audit corrections. Fixed Phase 2 engine count (§1.1). Removed editorial markers (§1.6, §6.2). Collapsed §1.6 entry/flagged restatement into §6.2 reference (SSoT fix). Fixed five dangling "extraction engine" forward-references in §2.2 and §2.4 to point to correct engines. Fixed §1.3 entry description to reflect school-group cardinality (§6.2). Replaced "coverage subsystem" references with taxonomy engine (§2.4, §3.5). Fixed taxonomy engine §8 cross-reference label. Expanded science-agnostic definition to cover all Phase 2 engines (§2.2). Added science scope to source metadata (§7.3). Added multi-science source handling (§1.2). Specified reviewed→placed lifecycle transition agent (§2.4). Added placed excerpt schema to contract inventory (§13.4.2). Moved data portability from §1.8 to §1.9. Collapsed redundant primary text paragraph (§5.1). Fixed "extraction engines" grouping label (§1.1, §2.2). Updated stale test count (§10.3). Rewrote §1 header cross-reference claim (§1).
- 1.0.0 (2026-03-02): Initial unified specification for خزانة ريان. Assembled from phased drafts (§1–§5 from Phase 1, §6–§9 from Phase 2, §10–§13 from Phase 3). Harmonized cross-references, resolved known inconsistencies between corrected sections, and verified term consistency with §2 definitions throughout.
