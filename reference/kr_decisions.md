# KR Architectural Decisions

## Decision Format
Each decision records: what was decided, why, what alternatives were considered,
which session made it, and what documents were updated as a result.

Decisions are append-only. To supersede a decision, add a new one referencing the old.

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
