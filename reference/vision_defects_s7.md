# VISION.md §7 Defect Ledger — From Source Engine SPEC

**Produced by:** Source Engine SPEC session, 2026-03-04
**Status:** Queued for application. Apply during cross-cutting VISION review (after all SPECs complete) or during the next session that touches VISION.md.

---

**Defect 1 (Severity: HIGH — Criterion #1 Zero Ambiguity).**
§7.2: "The source engine maintains a source registry that tracks all acquired sources with sufficient identifying information to detect duplicates."
**Problem:** "Sufficient identifying information" is unbounded. What fields constitute sufficiency?
**Correction:** "The source engine maintains a source registry that tracks all acquired sources. Deduplication uses SHA-256 hash comparison for exact duplicates and normalized author+title matching for work-level duplicates. The specific criteria are defined in the source engine SPEC §4.A.7."

**Defect 2 (Severity: MEDIUM — Criterion #2 Binary Sentences).**
§7.2: "Adding a new repository to this registry is a configuration decision."
**Problem:** Vague — not a binding rule or a marked open question.
**Correction:** "Adding a new repository requires: (1) implementing a repository interface module conforming to the source engine's repository interface contract (defined in the source engine SPEC), and (2) registering the repository in the application's configuration. No source engine core logic changes are required."

**Defect 3 (Severity: HIGH — Criterion #10 Full Input Coverage).**
§7.3: "work identifier (§2.5) linking volumes of multi-volume works."
**Problem:** §2.5 defines Work narrowly as volume-linking. The SPEC and DOMAIN.md require work_id to group ALL editions (different tahqiq, different format) of the same abstract intellectual creation, not just volumes. This is a conceptual gap, not just a wording issue.
**Correction:** Update §2.5's Work definition: "A work (مؤلَّف) is the abstract intellectual creation — the book as a scholarly contribution, independent of any particular edition or format. 'al-Mughni by Ibn Qudamah' is a work. The work identifier groups all manifestations (sources) of the same work: different tahqiq editions, different digital formats, different repository origins, and different volumes. The source identity model uses three tiers: source_id (per acquired file), work_id (per abstract work), and canonical_id (per scholar). See source engine SPEC §4.A.1."

**Defect 4 (Severity: MEDIUM — Criterion #10 Full Input Coverage).**
§7.3 is SILENT on four topics DOMAIN.md requires:
- Work-to-work relationships (sharh→matn chains)
- Author disambiguation
- Tahqiq quality criteria
- Edition variant tracking
- Source authority level (primary/reference/modern_compilation)
- Multi-layer composition detection
- Structural format classification
**Problem:** These are not contradictions but gaps. VISION §7.3 lists metadata categories; the SPEC defines fields the categories don't cover.
**Correction:** Add to §7.3's metadata categories: "_Work relationships:_ relationships to other works (commentary, abridgment, versification). See source engine SPEC §4.A.9." Add: "_Source authority level:_ primary source, reference work, or modern compilation. See source engine SPEC §4.A.4." Add: "_Multi-layer composition:_ whether the source contains text from multiple authors (e.g., matn+sharh). See source engine SPEC §4.A.4." Add: "_Structural format:_ the work's organizational format (prose, verse, Q&A, dictionary, etc.). See source engine SPEC §4.A.4."

**Defect 5 (Severity: LOW — Criterion #1 Zero Ambiguity).**
§7.4: "the source's rigor and quality" as an evaluation factor.
**Problem:** Vague. The SPEC defines 5 specific weighted factors.
**Correction:** "The evaluation considers author scholarly standing, tahqiq quality, publisher reputation, source authority level, and text fidelity — each weighted by importance. See source engine SPEC §4.A.8."

**Defect 6 (Severity: MEDIUM — Criterion #10 Full Input Coverage).**
§7.3 describes "Author scholarly context" informally. The SPEC defines a formal scholar authority model with canonical identities, name variants, biographical data, teacher-student graph, and progressive enrichment — a shared registry consumed by multiple engines.
**Problem:** VISION has no concept of the scholar authority model. It treats author data as source metadata fields, not as a shared knowledge graph.
**Correction:** Add to §7.3 or create a new subsection: "The source engine maintains a scholar authority registry — a shared knowledge graph of every scholar encountered across all sources. Each scholar has a canonical identity (canonical_id) linking their record across all sources. The registry is created by the source engine and consumed by the excerpting engine (for reference resolution) and the synthesizing engine (for biographical context in entries). See source engine SPEC §4.A.5."
