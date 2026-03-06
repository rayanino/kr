# Taxonomy Engine — محرك التصنيف — Specification

## 1. Purpose and Scope

The taxonomy engine manages the structural organization of all knowledge in the library. It has four responsibilities:

**Responsibility 1: Excerpt placement.** The taxonomy engine receives draft excerpts from the excerpting engine, validates or corrects the proposed leaf assignment, and transitions each excerpt to `placed` status at a confirmed leaf. Placement is the act that makes an excerpt part of the library — before placement, an excerpt is a processing artifact; after placement, it is discoverable knowledge that contributes to entries, coverage metrics, and the owner's scholarly understanding.

**Responsibility 2: Tree lifecycle management.** The taxonomy engine owns the full lifecycle of science trees: initial construction from scholarly research, ongoing evolution as new content reveals finer distinctions, and rollback when evolution proves incorrect. Each science has exactly one active tree at any time (§2.3). The tree IS the map of the science (D-021) — its structure makes the science's internal logic visible to the scholar interface.

**Responsibility 3: Coverage analytics.** The taxonomy engine computes and maintains multi-dimensional coverage metrics across every node, tree, and the library as a whole. Coverage reveals what Rayane knows and what he does not know. Because KR IS Rayane's knowledge (D-018), coverage gaps are personal knowledge gaps — the taxonomy engine is the diagnostic system that surfaces them.

**Responsibility 4: Structural knowledge graph.** Beyond the hierarchical tree, the taxonomy engine maintains three types of non-tree edges: prerequisite dependencies between topics, cross-science conceptual links, and terminology synonym mappings. These edges transform isolated trees into an interconnected scholarly knowledge map consumed by the synthesizing engine and the scholar interface.

**What is NOT this engine's responsibility.** The taxonomy engine does not extract excerpts (excerpting engine), generate entries (synthesizing engine), or present the tree to the user (scholar interface). It does not determine excerpt self-containment or perform metadata enrichment — those are excerpting engine responsibilities. It does not decide what constitutes a "science" — that is a §4.1 research decision documented in SCIENCE.md files.

**Phase classification.** Phase 2 (source-agnostic, below the normalization boundary). The taxonomy engine receives draft excerpts that carry no trace of their original source format.

**User scenarios served.** Scenario 7 ("Show Me the Whole Science") — the taxonomy engine produces every data structure the scholar interface needs to render the science map: the tree itself, prerequisite edges, narrative ordering, per-leaf coverage, scholarly landscape data. Scenario 1 ("New Source Arrives") — the engine places excerpts and updates coverage. Scenario 3 ("Cross-Science Exploration") — the engine maintains cross-science links. Scenario 8 ("KR Gets It Wrong") — the engine supports excerpt relocation and tree corrections.

---

## 2. Input Contract

The taxonomy engine receives input from two paths: draft excerpts from the excerpting engine, and tree management commands from the human gate and internal signals.

### 2.1 Draft Excerpts

Each draft excerpt arrives as a JSONL record conforming to the excerpt schema defined in the excerpting engine SPEC §3. The taxonomy engine validates the following fields on each incoming excerpt:

**Required fields — rejection on absence.** `excerpt_id` (non-empty string matching format `exc_{source_id}_{sequence}`), `source_id` (non-empty string), `passage_id` (non-empty string), `atom_ids` (non-empty array), `primary_text` (non-empty string), `science_id` (non-empty string matching a registered science), `lifecycle_stage` (must be `draft`). Absence of any required field triggers rejection with error `TAX_MISSING_REQUIRED_FIELD` and the excerpt is not processed.

**Expected fields — warning on absence.** `proposed_leaf` (string or null), `proposed_leaf_confidence` (float), `excerpt_topic` (string), `school` (string or null), `content_types` (array), `evidence_refs` (array), `primary_author_id` (string or null), `self_containment_score` (float), `review_flags` (array), `terminology_variants` (array). Absence of expected fields triggers warning `TAX_MISSING_EXPECTED_FIELD` and the excerpt proceeds with degraded placement confidence.

**Validation on `proposed_leaf`.** If `proposed_leaf` is non-null, the taxonomy engine verifies: (a) the referenced science tree exists and is active, (b) the path resolves to an existing node, (c) the resolved node is a leaf (not a branch or root). If any check fails, `proposed_leaf` is treated as null — the taxonomy engine performs independent classification. A failed `proposed_leaf` is not an error; it is normal when the excerpting engine's topic model and the taxonomy tree are misaligned.

**Validation on `science_id`.** The science must have an active tree. If no tree exists for the declared science, the excerpt is placed in a pending queue (`TAX_PENDING_NO_TREE`) and held until the tree is created. The pending queue is persistent across sessions.

### 2.2 Tree Management Commands

Tree management commands arrive from three sources:

**Evolution proposals (internal).** Generated by the taxonomy engine's own evolution signal detection (§4.A.5). These are internal data structures, not external inputs.

**Human gate decisions.** The owner's responses to placement escalations, evolution proposals, and coverage review requests. Each decision carries: `decision_id`, `gate_type` (one of `placement_review`, `evolution_review`, `coverage_review`), `decision` (one of `approve`, `reject`, `modify`), `modifications` (object or null), `reviewer_notes` (string or null), `timestamp`.

**Excerpt relocation requests.** When the owner identifies a misplaced excerpt (Scenario 8), the request specifies: `excerpt_id`, `current_leaf`, `target_leaf`, `reason`. The taxonomy engine validates that the target leaf exists and is a leaf node before proceeding.

---

## 3. Output Contract

The taxonomy engine produces four categories of output.

### 3.1 Placed Excerpts

Written to `library/sciences/{science_id}/content/{leaf_path}/excerpts/{excerpt_id}.json`. Each placed excerpt extends the draft excerpt with placement-specific fields, conforming to the placed_excerpt schema:

- `lifecycle_stage`: `placed`. Immutable once written.
- `confirmed_leaf`: string. The actual leaf path. May differ from `proposed_leaf` if the taxonomy engine reclassified.
- `placement_confidence`: float, 0.0–1.0. The taxonomy engine's confidence in this placement.
- `placed_utc`: ISO datetime. Timestamp of placement.
- `review_metadata`: object. Documents the human gate outcome (approved, approved_with_modifications, auto_approved) per §9.
- `verified_flagged_status`: `verified` or `flagged`. Inherited from source trustworthiness evaluation; may be overridden at placement.
- `taxonomy_version_at_placement`: string. The active tree version at placement time.
- `placement_reasoning`: string. A brief LLM-generated explanation of why this leaf was chosen. Supports auditability (D-033).

**Guarantees about placed excerpts:**

- **Leaf validity.** `confirmed_leaf` always resolves to a leaf in the tree version recorded in `taxonomy_version_at_placement`. If the tree evolves after placement, the excerpt's `confirmed_leaf` may reference a path that no longer exists in the current tree — the migration system (§4.A.7) handles this.
- **Uniqueness.** No two placed excerpt files share the same `excerpt_id`.
- **Provenance preservation (D-023).** All upstream metadata is preserved by reference: `source_id`, `passage_id`, `atom_ids`, `physical_pages`, `division_path`, `primary_author_id`, `quoted_scholars`, `evidence_refs`, `takhrij_data`, `content_types`, `school`, `school_confidence`, `self_containment_score`, `review_flags`, `processing_metadata`. The taxonomy engine adds placement data; it never strips upstream fields.

### 3.2 Science Tree Files

Each science tree is stored as `library/sciences/{science_id}/tree.yaml` (active version) with history in `library/sciences/{science_id}/tree_history/{science_id}_v{version}.yaml`.

The tree YAML structure encodes:

- **Node hierarchy.** Each node has: `id` (ASCII slug, unique within tree), `title` (Arabic display name), `children` (array of child nodes, empty for leaves), `leaf` (boolean, true for leaf nodes).
- **Prerequisite edges.** Stored in `library/sciences/{science_id}/prerequisites.json`. Each edge: `from_node_id` (the prerequisite topic), `to_node_id` (the dependent topic), `strength` (one of `hard`, `soft`), `rationale` (string explaining why).
- **Narrative ordering.** Encoded as the array ordering of `children` at each branch node. The first child in the array is the first topic in the pedagogical sequence. This ordering is explicit and meaningful — it is never alphabetical unless alphabetical happens to be the pedagogical order.
- **Cross-science links.** Stored in `library/sciences/cross_science_links.json`. Each link: `source_leaf` (format `{science_id}/{leaf_path}`), `target_leaf` (format `{science_id}/{leaf_path}`), `relationship_type` (one of `same_concept`, `related_concept`, `prerequisite_cross_science`, `application_of`), `confidence` (float), `description` (string).
- **Terminology synonyms.** Stored in `library/sciences/{science_id}/synonyms.json`. Each entry: `canonical_term` (the standard term used in the tree node title), `variants` (array of objects: `term` (string), `context` (string — which school, period, or author uses this variant)).

### 3.3 Coverage Analytics

Written to `library/sciences/{science_id}/coverage.json` (per-science) and `library/coverage_summary.json` (library-wide). Updated after every placement, relocation, or evolution event.

Per-leaf coverage record:
- `leaf_path`: string.
- `total_excerpts`: integer. Count of placed excerpts.
- `verified_excerpts`: integer. Count of verified (non-flagged) excerpts.
- `flagged_excerpts`: integer. Count of flagged excerpts.
- `source_count`: integer. Number of distinct sources contributing excerpts.
- `school_coverage`: object mapping school names to excerpt counts. Reveals which schools are represented.
- `evidence_type_coverage`: object mapping evidence types to counts.
- `author_diversity`: integer. Number of distinct `primary_author_id` values.
- `temporal_span`: object. `earliest_author_death` and `latest_author_death` (hijri years) from scholar authority data. Shows the chronological range of scholarship represented.
- `content_type_distribution`: object mapping content types to counts.
- `gaps`: array of gap descriptors (§4.A.6).
- `significance_score`: float, 0.0–1.0. How important this topic is within the science (§4.B.1).
- `difficulty_estimate`: float, 0.0–1.0. Estimated difficulty level (§4.B.2).
- `duplicate_clusters`: array of arrays of excerpt_ids. Groups of excerpts that are semantically near-identical (§4.A.8).

Per-branch coverage aggregates leaf-level metrics. Per-science coverage adds: total leaves, populated leaves (at least one verified excerpt), empty leaves, evolution events count.

### 3.4 Evolution Artifacts

When the taxonomy engine proposes an evolution, it produces a structured proposal:

- `proposal_id`: string, format `evo_{science_id}_{timestamp}`.
- `science_id`: string.
- `current_tree_version`: string.
- `proposed_tree_version`: string.
- `change_type`: one of `leaf_split`, `branch_restructure`, `node_rename`, `node_move`, `leaf_merge`.
- `affected_node`: string (node path in current tree).
- `proposed_structure`: object describing the new subtree.
- `excerpt_redistribution`: array of objects, each: `excerpt_id`, `current_leaf`, `proposed_leaf`, `redistribution_confidence`, `reasoning`.
- `trigger_signal`: object describing what triggered this proposal.
- `invariant_checks`: object confirming zero_orphans (bool), sibling_coherence (bool), excerpt_non_interference (bool), entry_lifecycle_propagation (bool).

Evolution proposals are written to `library/sciences/{science_id}/evolution/pending/{proposal_id}.json`. Approved proposals move to `library/sciences/{science_id}/evolution/applied/`. Rejected proposals move to `library/sciences/{science_id}/evolution/rejected/`.

**Metadata pass-through (D-023).** The taxonomy engine preserves ALL upstream metadata on every placed excerpt. It adds: `confirmed_leaf`, `placement_confidence`, `placement_reasoning`, `placed_utc`, `review_metadata`, `taxonomy_version_at_placement`, `verified_flagged_status`. These additions are the taxonomy engine's contribution to the metadata chain that flows to the synthesizer.

---

## 4. Processing Specification

### §4.A — Core Processing

#### §4.A.1 — Placement Algorithm

Placement determines which leaf an excerpt belongs at. The algorithm uses a two-stage approach: candidate generation followed by candidate ranking.

**Stage 1: Candidate generation.** The taxonomy engine generates a set of candidate leaves. Three sources contribute candidates:

(a) **Excerpting engine proposal.** If `proposed_leaf` is non-null and resolves to a valid leaf, it becomes the first candidate with its `proposed_leaf_confidence` score.

(b) **Topic-based search.** The engine uses the `excerpt_topic` text and `terminology_variants` to search the active tree for matching leaves. The search is LLM-driven: the engine calls `claude-sonnet` via Instructor with structured output schema `{candidate_leaves: [{leaf_path: str, reasoning: str}], confidence: float}` and prompt: "Given this excerpt topic: {excerpt_topic}, and this tree structure: {branch_titles_only}, identify the 3–5 most likely leaf paths where this excerpt belongs." For trees with more than 200 leaves, the search is hierarchical: first identify the correct branch (top 3), then identify the correct leaf within each candidate branch. For trees with fewer than 10 leaves, all leaves are included as candidates directly (Stage 1b is skipped).

(c) **Embedding similarity.** The engine computes a sentence embedding of `excerpt_topic` (using multilingual-e5-large or equivalent) and compares it against precomputed embeddings of all leaf titles in the science tree. The top 3 leaves by cosine similarity become additional candidates if they are not already in the candidate set. This catches terminology mismatches that LLM search might miss.

**Stage 2: Candidate ranking.** All candidates from Stage 1 are scored in a single LLM call (separate from Stage 1). The engine calls `claude-sonnet` via Instructor with structured output schema `{rankings: [{leaf_path: str, score: float, reasoning: str}]}` and prompt containing: the excerpt's `primary_text` (first 500 characters), the `excerpt_topic`, and for each candidate leaf: the leaf title, its parent branch titles, and the `excerpt_topic` values of up to 5 existing excerpts at that leaf. The LLM scores each candidate on a 0.0–1.0 scale considering: (a) does the excerpt's teaching content match the leaf's topic? (b) is there a more specific leaf that would be a better fit? (c) does the excerpt's content overlap with existing excerpts at this leaf? The highest-scoring candidate is selected.

**Placement decision rules:**

- If the top candidate scores ≥ 0.8: the excerpt is placed at that leaf after passing all §4.A.2 validation checks. If the source+science combination has a pre-approval policy (see below), placement proceeds without human gate. Otherwise, placement is queued for human gate review.
- If the top candidate scores 0.5–0.8: placement is always escalated to human gate review, regardless of pre-approval policies. The owner sees the top 3 candidates with scores and reasoning.
- If no candidate scores ≥ 0.5: the excerpt is flagged as `TAX_UNPLACEABLE` and held in a staging area. This is an evolution signal — the tree may lack the right leaf. The excerpt is not silently discarded; it is visible to the owner with an explanation.
- If two candidates score within 0.1 of each other (tie condition): escalated to human gate with both candidates presented.

**Pre-approval policies.** Per-source, per-science configuration records managed by the human gate engine. The human gate validates and stores these records after the owner approves 10+ consecutive placements from the same source in the same science without modification. Pre-approval can be revoked by the owner at any time. Pre-approval only affects the human gate step; all §4.A.2 validation checks still run.

**The excerpting engine's proposal is a hint, not a constraint.** The taxonomy engine may override `proposed_leaf` with a different leaf if its own analysis determines a better placement. When it overrides, it records: `proposed_leaf_override: true`, `proposed_leaf_original`, `override_reason`.

**Example: Placement Decision Flow.**

An excerpt arrives with:
```
excerpt_id: exc_nahw_ibnhisham_qatralnada_001_014
excerpt_topic: "أقسام الخبر: المفرد والجملة وشبه الجملة"
proposed_leaf: "nahw/mubtada_khabar/khabar_types"
proposed_leaf_confidence: 0.72
science_id: "nahw"
terminology_variants: ["أنواع الخبر", "الخبر المفرد"]
```

**Stage 1 — Candidate generation:**
- (a) Excerpting engine proposal: `nahw/mubtada_khabar/khabar_types` with confidence 0.72. Added as candidate.
- (b) Topic-based search: the LLM receives the Nahw tree's branch structure and `excerpt_topic`. It returns: `nahw/mubtada_khabar/khabar_types` (same as proposal, score 0.85), `nahw/mubtada_khabar/khabar_mufrad` (a more specific leaf, score 0.78), `nahw/jumal/jumla_khabariyya` (tangentially related, score 0.45).
- (c) Embedding similarity: top 3 by cosine = `khabar_types` (0.91), `khabar_mufrad` (0.84), `khabar_jumla` (0.79). `khabar_jumla` is new — added to candidate set.

**Stage 2 — Candidate ranking:** The LLM scores each candidate:
- `khabar_types`: 0.88 — the excerpt covers ALL three types, so the general leaf is the best fit.
- `khabar_mufrad`: 0.52 — the excerpt mentions المفرد but does not focus exclusively on it.
- `khabar_jumla`: 0.41 — only tangentially relevant.
- `jumla_khabariyya`: 0.35 — different topic entirely.

**Decision:** Top candidate `khabar_types` scores 0.88 (≥ 0.8). The source has a pre-approval policy for Nahw. Placement proceeds without human gate. Override recorded: `proposed_leaf_override: false` (the taxonomy engine confirmed the excerpting engine's proposal).

**Example: Placement Override with Escalation.**

An excerpt arrives with:
```
excerpt_id: exc_fiqh_ibnqudama_mughni_003_042
excerpt_topic: "شروط صحة البيع"
proposed_leaf: "fiqh/buyu/buyu_general"
proposed_leaf_confidence: 0.55
science_id: "fiqh"
```

**Stage 1:** Topic search identifies `fiqh/buyu/shurut_buyu` (conditions of sale) as a candidate — a more specific leaf than the proposed general leaf.

**Stage 2:** Ranking:
- `shurut_buyu`: 0.91 — exact topic match.
- `buyu_general`: 0.48 — too broad; the excerpt is specifically about conditions, not sales in general.

**Decision:** Top candidate `shurut_buyu` scores 0.91. But this is an override of the excerpting engine's proposal. Recorded: `proposed_leaf_override: true`, `proposed_leaf_original: "fiqh/buyu/buyu_general"`, `override_reason: "More specific leaf 'shurut_buyu' (conditions of sale) matches excerpt topic exactly; the proposed general leaf is too broad."` Placement proceeds at `shurut_buyu`.

#### §4.A.2 — Placement Validation

After the placement decision, before writing the placed excerpt, the taxonomy engine performs validation checks:

**One-excerpt-per-source-per-leaf diagnostic (§5.5).** If another excerpt from the same `source_id` is already placed at the same leaf, the diagnostic fires. The engine evaluates whether the two excerpts should be merged (they cover the same sub-topic in different sections of the source) or whether the leaf should evolve (they cover distinguishably different sub-topics). If the incoming excerpt has review flag `cross_topic_candidate`, it is exempt from this diagnostic per §5.5's interaction clause. The diagnostic result is recorded in the placement record but does not block placement — it may trigger a merge suggestion or evolution signal.

**Verified/flagged consistency.** If the excerpt's source has a `trust_tier` that maps to `flagged`, the excerpt receives `verified_flagged_status: flagged` unless the owner has explicitly overridden the source's trust evaluation for this excerpt. Conversely, an individually flagged excerpt from a verified source receives `flagged` status with the specific `flag_reason`. The taxonomy engine never promotes an excerpt from flagged to verified autonomously — that requires human gate review.

**Leaf capacity check.** This is purely diagnostic. When a leaf accumulates more than 30 verified excerpts, a diagnostic is logged suggesting the owner review whether the leaf is too coarse. This is NOT an evolution trigger — it is an informational signal.

**Example: One-Excerpt-Per-Source Diagnostic.**

Leaf `nahw/mubtada_khabar/khabar_types` already has a placed excerpt `exc_nahw_ibnhisham_qatralnada_001_014` from source `ibnhisham_qatralnada`. A new excerpt `exc_nahw_ibnhisham_qatralnada_001_027` from the same source is placed at the same leaf. The diagnostic fires. The engine evaluates:
- Excerpt 014 topic: "أقسام الخبر: المفرد والجملة وشبه الجملة" (types of khabar).
- Excerpt 027 topic: "تقديم الخبر على المبتدأ" (khabar preceding mubtada).
These are distinguishably different sub-topics. The diagnostic records: `"same_source_different_subtopics: true"` — this is an evolution signal (Signal 4 in §4.A.5) suggesting the leaf should split into khabar-types and khabar-ordering sub-leaves.

#### §4.A.3 — Tree Construction

Tree construction follows the four-phase workflow defined in §4.2 (Research → Draft → Validation → Commitment). The taxonomy engine specifies the procedures within each phase.

**Research phase.** For a given science, the engine receives a set of authoritative works (identified by the owner or by the source engine's work registry). The engine analyzes the tables of contents of these works — not the full text, but the structural organization: كتاب/باب/فصل/مسألة headings. The LLM synthesizes these organizational frameworks into a common structure, noting where works agree on organization and where they diverge. The output is a research report listing: the works consulted, the organizational patterns found, points of agreement, points of divergence, and a recommended structure with rationale.

The research phase also queries the scholar authority registry for the science's known scholarly tradition: which schools exist, which are the foundational works, what organizational conventions are standard. This context informs the tree design.

**Draft phase.** The engine generates a draft tree from the research report. The draft follows the granularity bias principle (§4.2): err on the side of finer distinctions. Each proposed leaf receives a title in Arabic reflecting standard scholarly terminology for that topic. Each proposed branch receives a title matching the science's conventional chapter-level terminology.

Narrative ordering is assigned during drafting: the children of each branch are ordered according to the pedagogical sequence found in the majority of consulted works. Where works disagree on ordering, the engine records the disagreement and proposes the ordering from the work considered most pedagogically sound (by the LLM's assessment, subject to owner override).

Prerequisite edges are proposed during drafting: for each leaf, the engine identifies which other leaves contain concepts that must be understood first. Hard prerequisites are concepts without which the dependent topic is incomprehensible. Soft prerequisites are concepts that improve understanding but are not strictly required.

**Validation phase.** The draft tree is validated against real content. The engine takes 3–5 representative sources in the science (chosen for breadth of coverage) and tests whether each source's chapters map cleanly to the tree's leaves. Specifically, for each chapter in each source, the engine asks: which leaf(s) would this chapter's content be placed at? Three failure modes are checked:

- **Orphan content.** A chapter covers a topic not represented by any leaf. This reveals a missing leaf.
- **Split content.** A single chapter spans 2+ distinguishable sub-topics that map to different leaves. This is expected and acceptable — it means the tree has finer granularity than the source's chapter divisions.
- **Collapsed content.** 2+ chapters from the same source all map to the same leaf. This suggests the leaf is too coarse and should be split.

Failures are recorded in the validation report. The engine proposes fixes for each failure. The owner reviews the validation report and approves the draft (with or without modifications).

**Commitment phase.** The approved tree is written as `tree.yaml` with version `v1.0`. The tree is registered in `library/sciences/taxonomy_registry.yaml`. History copy is written. Coverage analytics are initialized (all zeros). The tree is now active and ready to receive excerpts.

#### §4.A.4 — Primary Topic Determination

When an excerpt mentions 2+ topics (§5.3, Rule 1), the taxonomy engine determines the primary topic — the topic the excerpt exists to teach. The determination uses three signals:

(a) **Core atom analysis.** The excerpt's `core_atom_ids` identify which atoms are the "teaching content." The taxonomy engine examines the scholarly functions of core atoms (from atom metadata): if the majority of core atoms are `definition`, `ruling`, or `opinion_marker` atoms about Topic A, and the context atoms are about Topic B, then Topic A is primary.

(b) **Excerpt topic text.** The `excerpt_topic` field from the excerpting engine is a direct statement of what the excerpt teaches.

(c) **LLM judgment.** When signals (a) and (b) conflict, or when the determination is ambiguous, the LLM reads the excerpt's `primary_text` and the candidate leaf descriptions, then determines which topic the author intended to teach. The LLM is called via the consensus interface (§6) with model `claude-sonnet` as primary, structured output via Instructor returning `{primary_topic: str, confidence: float, reasoning: str}`. The prompt includes: "This excerpt may mention two or more topics. Determine which topic the author is primarily teaching, not merely referencing."

Primary topic determination is logged with the reasoning, supporting auditability (D-033).

**Example: Primary Topic Determination.**

An excerpt from شرح ابن عقيل على الألفية contains:
```
primary_text: "المبتدأ هو الاسم المرفوع العاري عن العوامل اللفظية... وخبره هو الجزء المتمّ الفائدة... وأصل الخبر أن يكون مفرداً نحو زيد قائم، وقد يكون جملةً نحو زيد أبوه قائم"
core_atom_ids: [atom_014, atom_015, atom_016]  # definition of mubtada, definition of khabar, khabar types
context_atom_ids: [atom_017]  # i'rab of the example sentence
excerpt_topic: "تعريف المبتدأ والخبر وأقسام الخبر"
```

The excerpt mentions both المبتدأ (subject) and الخبر (predicate). Candidate leaves: `mubtada_khabar/mubtada_definition`, `mubtada_khabar/khabar_types`.

Signal (a): Core atoms include `definition` atoms for BOTH mubtada and khabar, plus a `type_enumeration` atom for khabar types. Since 2 of 3 core atoms concern khabar (definition + types), while 1 concerns mubtada — but this is a combined definition passage where both are inseparable.

Signal (b): `excerpt_topic` says "تعريف المبتدأ والخبر وأقسام الخبر" — both topics explicitly named, with khabar types as the additional focus.

Signal (c): LLM judgment — the passage is a combined foundational definition that introduces mubtada AND khabar together; neither topic is subordinate to the other. The passage's STRUCTURE (defining mubtada first, then khabar, then elaborating khabar types) suggests the author treats them as a single unit of instruction.

**Decision:** Primary topic = `mubtada_khabar/mubtada_khabar_combined` (a leaf for combined mubtada-khabar definitions). If no such combined leaf exists, the engine places at `mubtada_khabar/mubtada_definition` (the first concept defined, per the author's ordering) and creates a cross-reference to `khabar_types`. Reasoning logged: "Combined definition passage treating المبتدأ and الخبر as inseparable unit; placed at mubtada_definition per author's ordering with cross-reference to khabar_types."

#### §4.A.5 — Evolution Signal Detection

The taxonomy engine continuously monitors for evolution signals. Five signal types are defined:

**Signal 1: Subtopic divergence.** When a leaf accumulates excerpts that cover distinguishably different sub-topics, the leaf may need to split. Detection: after every placement, the engine checks whether the new excerpt's `excerpt_topic` is semantically distinct from existing excerpts at the leaf. Semantic distinctness is measured by embedding cosine similarity: if the new excerpt's topic embedding has cosine similarity < 0.65 with the centroid of existing excerpt topics at the leaf, a divergence signal is raised. The signal is raised — not acted upon — as a candidate for evolution evaluation.

**Signal 2: Unplaceable excerpt.** When an excerpt scores < 0.5 against all candidate leaves (§4.A.1), the tree lacks the right leaf. This is a strong evolution signal — either a new leaf is needed, or an existing branch needs restructuring.

**Signal 3: Cross-source convergence.** When excerpts from 3+ different sources are placed at the same leaf and a cluster analysis reveals 2+ distinct sub-groups (by topic embedding clustering with silhouette score > 0.4), the leaf likely covers distinguishably different sub-topics.

**Signal 4: One-excerpt-per-source violation.** Per §5.5, when a second excerpt from the same source is placed at the same leaf and the two excerpts cover different sub-topics, this suggests the leaf should split.

**Signal 5: Owner feedback.** The owner may explicitly request that a leaf be split, a branch be restructured, or a node be renamed. Owner signals bypass confidence thresholds and proceed directly to proposal generation.

**Evolution evaluation.** When a signal is detected, the engine evaluates whether evolution is warranted. Not every signal leads to a proposal — a single divergence signal from one excerpt is weak. The engine accumulates signals per leaf and evaluates when: (a) 3+ independent signals point to the same leaf, or (b) a single strong signal (unplaceable excerpt, owner request) targets the leaf.

Evaluation generates a structured proposal (§3.4). The proposal must pass all four §4.4 invariants:

**Example: Evolution Signal Accumulation and Evaluation.**

Leaf `nahw/marfu'at/khabar` accumulates signals over time:
1. Signal 1 (divergence): Excerpt about "أقسام الخبر" has cosine similarity 0.42 with the centroid of existing excerpts (which are about "تعريف الخبر"). Divergence signal raised. (Accumulated signals: 1)
2. Signal 4 (one-per-source violation): Two excerpts from the same source at this leaf cover different sub-topics ("الخبر المفرد" vs "تقديم الخبر"). Signal raised. (Accumulated signals: 2)
3. Signal 1 (divergence): Another excerpt about "حذف الخبر" has cosine similarity 0.38 with centroid. Divergence signal raised. (Accumulated signals: 3 — threshold reached)

**Evaluation triggers.** The engine generates a `leaf_split` proposal: split `khabar` into `khabar_definition`, `khabar_types`, `khabar_ordering`, `khabar_deletion`. Each existing excerpt is tentatively redistributed. All four invariants are checked before presenting to the owner.
- **Zero orphans.** Every existing excerpt at the affected leaf must have a valid placement in the proposed structure.
- **Sibling coherence.** No excerpt should plausibly belong to more than one proposed sibling. Tested by LLM: for each excerpt, the LLM classifies it into one of the proposed siblings. If any excerpt receives a split classification (two siblings score within 0.15 of each other), sibling coherence fails.
- **Excerpt non-interference.** No excerpt outside the evolution scope is affected.
- **Entry lifecycle propagation.** The proposal specifies which entries are invalidated and which new entries are queued.

Proposals that fail any invariant are never presented to the owner.

#### §4.A.6 — Coverage Gap Detection

Coverage gaps are computed per leaf, per branch, and per science. A gap is a structured object describing what is missing. Gap types:

**School gap.** A science that has schools (per SCIENCE.md) has a leaf where one or more schools have zero verified excerpts. Example: a Fiqh leaf has Hanafi, Shafi'i, and Hanbali excerpts but no Maliki excerpt. The gap records: `gap_type: school`, `missing_school`, `leaf_path`.

**Source diversity gap.** A leaf's excerpts all come from a single source (or fewer than 2 sources). Scholarly reliability requires corroboration. Gap records: `gap_type: source_diversity`, `current_source_count`, `leaf_path`.

**Temporal gap.** A leaf's excerpts all come from a narrow time period (all authors within 200 hijri years of each other) when the science spans a wider period. Important topics typically have positions spanning 2+ distinct centuries. Gap records: `gap_type: temporal`, `covered_period`, `science_total_period`, `leaf_path`.

**Evidence type gap.** A leaf has positions (opinions) but no supporting evidence (no Quran, hadith, or rational argument excerpts). Scholarly positions without evidence are incomplete. Gap records: `gap_type: evidence`, `missing_evidence_types`, `leaf_path`.

**Prerequisite gap.** A leaf has excerpts, but one of its hard prerequisite topics (from the prerequisite graph) has zero excerpts. The user cannot study this topic without first studying the prerequisite, but the prerequisite is empty. Gap records: `gap_type: prerequisite`, `missing_prerequisite_leaf`, `leaf_path`.

**Empty leaf.** A leaf exists in the tree but has zero excerpts. For trees where ≥50% of leaves are empty, this is expected during early library building. The gap is reported but at low severity. Gap records: `gap_type: empty`, `leaf_path`.

Gaps are recalculated after every placement, relocation, or evolution event. They are written to the coverage analytics output (§3.3) and available to the scholar interface for display and alerting.

**Example: Gap Detection After Placement.**

Leaf `fiqh/salat/qunut` has 4 verified excerpts after a new placement:
- 2 excerpts from Hanafi sources (al-Marghinani d. 593 AH, al-Kasani d. 587 AH)
- 1 excerpt from Shafi'i source (al-Nawawi d. 676 AH)
- 1 excerpt from Hanbali source (Ibn Qudama d. 620 AH)

Gaps detected:
1. **School gap:** `{gap_type: "school", missing_school: "maliki", leaf_path: "fiqh/salat/qunut"}` — Maliki school has zero excerpts.
2. **Temporal gap:** `{gap_type: "temporal", covered_period: {start: 587, end: 676}, science_total_period: {start: 150, end: 1200}, leaf_path: "fiqh/salat/qunut"}` — all authors within a 89-year window vs. the science spanning 1050 years.
3. **Evidence gap:** No excerpts have `evidence_refs` with Quran or hadith citations — only scholarly opinions without dalil. `{gap_type: "evidence", missing_evidence_types: ["quran", "hadith"], leaf_path: "fiqh/salat/qunut"}`.

#### §4.A.7 — Evolution Application and Migration

When the owner approves an evolution proposal at the human gate, the taxonomy engine applies the change:

**Tree modification.** The tree YAML is updated with the new structure. The previous version is archived in `tree_history/`. The new version number is incremented. The taxonomy registry is updated.

**Excerpt redistribution.** Each excerpt in the proposal's redistribution plan is moved to its new leaf. The move is atomic: the placed excerpt file is written to the new leaf's directory, and the old file is removed, in a single transactional operation. If any redistribution fails (e.g., target directory creation fails), the entire evolution is rolled back.

For each redistributed excerpt:
- `confirmed_leaf` is updated to the new leaf path.
- `taxonomy_version_at_placement` is updated to the new tree version.
- `review_metadata` is updated to record the evolution event: `review_outcome: evolution_redistributed`, `evolution_proposal_id`.
- All other fields are preserved unchanged.

**Entry cascade.** Per §4.4's entry lifecycle propagation invariant: entries at leaves whose excerpt collection changed are marked stale. New leaves created by evolution with at least one verified excerpt are queued for initial entry generation. The staleness markers and generation queue are written to `library/sciences/{science_id}/entry_queue.json`, consumed by the synthesizing engine.

**Rollback.** If the owner requests rollback of an evolution, the taxonomy engine: (a) restores the previous tree version from `tree_history/`, (b) reverses all excerpt redistributions, (c) handles post-evolution excerpts — excerpts placed at the evolved leaves AFTER the evolution but BEFORE the rollback — by returning them to `reviewed` status for re-placement (per §4.4 rollback completeness invariant), (d) marks all affected entries as stale. Rollback is a human-gated operation.

**Example: Evolution Application.**

Leaf `nahw/marfu'at/khabar` is approved for split into `khabar_definition`, `khabar_types`, `khabar_ordering`. Tree version `nahw_v1_0` → `nahw_v2_0`. Three existing excerpts are redistributed:
- `exc_001` (topic: "تعريف الخبر") → `khabar_definition`, confidence 0.92
- `exc_002` (topic: "أقسام الخبر") → `khabar_types`, confidence 0.89
- `exc_003` (topic: "تقديم الخبر") → `khabar_ordering`, confidence 0.94

The engine writes the new tree YAML, archives `nahw_v1_0`, moves each excerpt file atomically, updates `taxonomy_version_at_placement` on each excerpt to `nahw_v2_0`, and queues entries at `khabar_definition`, `khabar_types`, `khabar_ordering` for initial generation. The old entry at `khabar` is marked stale.

#### §4.A.8 — Semantic Deduplication Detection

When 2+ sources quote the same hadith, or paraphrase the same well-known definition, the taxonomy engine detects the semantic overlap and signals it to the synthesizing engine. This ensures entries present redundant content once (citing the strongest source) rather than repeating it.

Detection uses embedding similarity. After placement, the engine computes the embedding of the new excerpt's `primary_text` and compares it against all existing verified excerpts at the same leaf. If cosine similarity exceeds 0.85 with any existing excerpt, the pair is flagged as a duplicate cluster. Existing clusters are extended if the new excerpt is similar to any member.

Duplicate clusters are recorded in the coverage analytics (§3.3) and attached to the leaf's metadata. The synthesizing engine reads these clusters to avoid redundant presentation. The taxonomy engine does NOT merge or remove duplicate excerpts — they remain as independent placed excerpts. Deduplication is a synthesis-time concern, not a placement-time action, because different sources may add unique context even when the core content is similar.

**Example: Duplicate Detection.**

At leaf `fiqh/tahara/nawaqid_wudu`, excerpt `exc_fiqh_nawawi_minhaj_002_008` is newly placed. Its `primary_text` includes the well-known hadith about the nullifiers of wudu. The engine computes its embedding and compares against existing excerpts. Excerpt `exc_fiqh_ibnqudama_mughni_001_015` has cosine similarity 0.91 (> 0.85 threshold) — both quote the same hadith with minor wording differences. They are grouped into duplicate cluster `["exc_fiqh_nawawi_minhaj_002_008", "exc_fiqh_ibnqudama_mughni_001_015"]`. The synthesizer will later cite the stronger source and note the other as corroboration, rather than presenting the same hadith twice.

#### §4.A.9 — Cross-Science Link Management

When the same concept appears as a leaf in 2+ science trees (e.g., الاستثناء in both Nahw and Usul), the taxonomy engine records a cross-science link. Links are never merges — each science's leaf is independent with its own excerpts and entries. Links are metadata for the synthesizer and scholar interface.

Cross-science links are detected by two mechanisms:

(a) **Title matching.** When a new leaf is created (during tree construction or evolution), the engine checks all other science trees for leaves with semantically similar titles. LLM evaluation confirms whether the concepts are genuinely related or merely share a term.

(b) **Excerpt cross-reference.** When an excerpt at a leaf explicitly references a concept from another science (detected from `excerpt_topic` or `primary_text` content), and that concept has a leaf in the other science's tree, a link is proposed.

Links are written to `cross_science_links.json` (§3.2) and are available to the scholar interface for cross-science navigation (Scenario 3).

**Example: Cross-Science Link Detection.**

During tree construction for Usul al-Fiqh, a new leaf `usul/dalalat/istithna` (exception/استثناء in legal methodology) is created. Title matching detects an existing leaf `nahw/mansubat/istithna` (exception in grammar). The LLM confirms: "The grammatical concept of istithna and the usuli concept of istithna are genuinely related — usuli scholars depend on the grammatical analysis of exception particles (إلا، غير، سوى) to derive legal rulings. The relationship is `application_of` (usul applies nahw)." Link created: `{source_leaf: "usul/dalalat/istithna", target_leaf: "nahw/mansubat/istithna", relationship_type: "application_of", confidence: 0.88}`.

#### §4.A.10 — Terminology Synonym Management

Islamic scholarly terminology varies across schools and historical periods. The taxonomy engine maintains synonym mappings so that excerpts using variant terminology are placed at the correct leaf.

When the excerpting engine provides `terminology_variants` on an excerpt, the taxonomy engine checks whether any variant maps to a different leaf title than the proposed leaf. If a variant matches a leaf title, this confirms the placement. If a variant reveals a previously unknown synonym for an existing leaf, the synonym is added to the synonyms registry after LLM verification.

New synonyms are also detected during placement: when the LLM's topic-based search (§4.A.1, Stage 1b) identifies a leaf that uses a different term than the excerpt's `excerpt_topic`, but the concepts are the same, the terminology pair is recorded.

Synonyms are stored per science (§3.2) and used in placement candidate generation — when searching for matching leaves, all known synonyms for each leaf title are included in the search.

**Example: Synonym Detection During Placement.**

An excerpt arrives with `excerpt_topic: "الفاعل المعنوي"` (semantic subject). The tree has no leaf titled "الفاعل المعنوي" but has `nahw/marfu'at/naib_fa'il` (نائب الفاعل / deputy subject). The LLM's topic search identifies `naib_fa'il` as the best match and notes: "الفاعل المعنوي is a synonym used by Basran grammarians (e.g., al-Mubarrad, Ibn al-Sarraj) for the concept standardly called نائب الفاعل." The synonym is registered: `{canonical_term: "نائب الفاعل", variants: [{term: "الفاعل المعنوي", context: "Basran grammatical tradition"}]}`. Future excerpts using "الفاعل المعنوي" will immediately match `naib_fa'il` without LLM re-evaluation.

---

### §4.B — Transformative Capabilities

#### §4.B.1 — Topic Significance Scoring

Every leaf in every science tree receives a significance score that measures how important the topic is within the science. This score is NOT a simple count of excerpts — a leaf with 50 excerpts about a minor lexical curiosity is less significant than a leaf with 5 excerpts about a foundational principle. Significance is a structural property of the science, not a measure of library coverage.

Significance is computed from four signals:

(a) **Prerequisite dependency count.** The count of other topics that depend on this one (out-degree in the prerequisite graph). A topic that is a prerequisite for 3+ others is foundational.

(b) **Cross-reference frequency.** How often excerpts at OTHER leaves reference this topic in their text (detected by the excerpting engine's `quoted_scholars` and implicit reference data, plus text search for the leaf's title and synonyms across all excerpts in the science).

(c) **Source coverage breadth.** The count of distinct authoritative works that dedicate substantial space to this topic (measured by the number of sources that contribute 2+ excerpts to this leaf). Topics that every major work addresses are significant.

(d) **LLM scholarly assessment.** The LLM is prompted: "Within the science of {science_name}, how significant is the topic of {leaf_title}? Consider: is this a foundational concept, a derived application, an edge case, or a minor detail? Rate 0.0–1.0 with reasoning." This assessment uses the LLM's broad knowledge of the science, not just library contents, to prevent corpus bias.

The four signals are combined with weights: prerequisite dependency (0.3), cross-reference frequency (0.25), source breadth (0.2), LLM assessment (0.25). The resulting score is normalized to 0.0–1.0 per science.

**Why this is transformative.** No existing Islamic scholarly tool quantifies topic significance within a science. Classical scholars implicitly know which topics are foundational — but this knowledge is tacit and takes years of study to acquire. Significance scoring makes it explicit and queryable: "Show me the 20 most significant topics in Nahw that I haven't studied." The scholar interface uses significance scores for study path optimization — ensuring the student builds foundational knowledge before derived applications. The synthesizer uses significance to calibrate entry depth — more significant topics get more thorough entries.

**Technical approach.** Prerequisite graph analysis uses NetworkX (DAG traversal, out-degree computation). Cross-reference frequency uses full-text search over the excerpt corpus (CAMeL Tools for Arabic text normalization, then exact and fuzzy matching). Source breadth is a simple database query. LLM assessment uses Instructor for structured output (score + reasoning).

[NOT YET IMPLEMENTED] — Full specification provided; no code exists. Depends on: prerequisite graph (§4.A.3), placed excerpt corpus, scholar authority registry, Instructor library.

**Example: Significance Scoring.**

Leaf `nahw/marfu'at/mubtada` (المبتدأ):
- (a) Prerequisite dependency: 8 other leaves depend on it (khabar, jumla ismiyya, ishtighal, kana wa-akhwatuha, inna wa-akhwatuha, hal, naib_fa'il, tawabi') → normalized score: 0.8
- (b) Cross-reference: 23 excerpts at other Nahw leaves reference "المبتدأ" → normalized score: 0.75
- (c) Source breadth: 6 of 7 registered Nahw sources contribute excerpts → normalized score: 0.86
- (d) LLM assessment: "المبتدأ is one of the foundational pillars of Arabic syntax. Every sentence analysis depends on it." → score: 0.95

Weighted combination: (0.8×0.3) + (0.75×0.25) + (0.86×0.2) + (0.95×0.25) = 0.24 + 0.19 + 0.17 + 0.24 = **0.84** (high significance).

#### §4.B.2 — Difficulty Estimation and Study Path Intelligence

Every leaf receives an estimated difficulty level that represents how challenging the topic is for a student. This enables the scholar interface to generate intelligent study paths — sequences of topics ordered not just by prerequisite dependencies but by cognitive load.

Difficulty is estimated from five signals:

(a) **Prerequisite depth.** The longest path from a root-adjacent node to this leaf in the prerequisite graph. Deep prerequisite chains indicate advanced topics.

(b) **Position complexity.** The number of distinct scholarly positions at this leaf. A topic with 6 competing school positions is harder to master than one with unanimous agreement.

(c) **Evidence complexity.** The types and quantity of evidence cited in excerpts at this leaf. Topics whose evidence requires hadith grading knowledge, usul al-fiqh methodology, or cross-science reasoning are more complex.

(d) **Content type distribution.** Leaves dominated by `definition` atoms are typically introductory. Leaves with high proportions of `refutation`, `exception`, and `condition` atoms are typically advanced — they deal with edge cases and scholarly debate.

(e) **Source difficulty signals.** When excerpts come from works that the source metadata classifies as advanced (mutun vs. shuruh vs. hawashi), this signals higher difficulty.

Difficulty is normalized to 0.0–1.0. The scholar interface combines difficulty with significance to generate optimal study sequences: important + easy topics first, building toward important + difficult topics. Unimportant + difficult topics are deprioritized.

**Why this is transformative.** Islamic studies curricula traditionally follow fixed book sequences. A student reads Qatr al-Nada cover-to-cover, then al-Alfiyyah. But different students have different knowledge profiles — one student may already understand most of Qatr al-Nada's content from another source. KR's difficulty estimation, combined with the user model's knowledge tracking, enables personalized study paths: "Skip topics 12–18 (you already know them from al-Ajurrumiyyah). Focus on topics 19–25 (new content, moderate difficulty). Topic 26 requires prerequisite topic 7 which you haven't mastered — study that first."

**Technical approach.** Prerequisite depth uses NetworkX's `dag_longest_path_length` starting from each node. Position complexity is a count from the excerpt corpus. Evidence and content type distributions are computed from excerpt metadata. Source difficulty comes from source metadata.

[NOT YET IMPLEMENTED] — Full specification provided; no code exists. Depends on: prerequisite graph, excerpt corpus metadata, source metadata, user model.

**Example: Difficulty Estimation.**

Leaf `nahw/mansubat/tamyiz` (التمييز / specification):
- (a) Prerequisite depth: longest path from root = 3 (marfu'at → mansubat → tamyiz) → normalized: 0.3
- (b) Position complexity: 2 positions (Basran vs. Kufan on tamyiz scope) → normalized: 0.3
- (c) Evidence complexity: hadith + Quran citations requiring basic Arabic understanding → normalized: 0.4
- (d) Content types: 60% definition + 40% condition atoms → normalized: 0.35
- (e) Source signals: excerpts from both mutun (al-Ajurrumiyyah) and shuruh (Ibn Aqil) → normalized: 0.5

Combined difficulty: **0.37** (beginner-intermediate). The scholar interface recommends studying this after mubtada/khabar (prerequisite) but before more complex mansubat like maf'ul mutlaq.

#### §4.B.3 — Corpus-Driven Tree Construction

Instead of building science trees purely from manual scholarly research (§4.A.3), the taxonomy engine can generate draft trees from computational analysis of 5+ authoritative works' structural organization. This capability accelerates tree construction for sciences with 5+ available sources.

The process:

(a) **Structural extraction.** For each authoritative work in the science (minimum 5 works spanning different periods and schools), extract the table of contents: chapter titles, section titles, sub-section titles, and their hierarchical relationships. This data comes from the normalization engine's division tree output.

(b) **Cross-work alignment.** The LLM aligns TOC entries across works, identifying: which topics appear in all works (consensus structure), which topics appear in fewer than all consulted works (disputed structure), which topics are organized differently in different works (structural disagreements), and which works introduce unique topics not found elsewhere.

(c) **Consensus tree synthesis.** From the alignment, the engine generates a draft tree that represents the consensus structure. Topics present in ≥60% of consulted works form the core structure. Topics present in <60% but ≥2 works are included as optional branches. Unique-to-one-work topics are noted in the research report but not included in the draft. The threshold is configurable.

(d) **Ordering inference.** The pedagogical sequence is inferred from the ordering of topics in the consulted works. Where works agree on ordering, that ordering is adopted. Where they disagree, the most common ordering is proposed with the alternatives documented.

**Why this is transformative.** Building a science tree for a major Islamic discipline (Fiqh has thousands of topics across 3+ organizational traditions — Hanafi, Shafi'i, and Hanbali works each structure fiqh differently) is a massive research effort. Corpus-driven construction reduces a weeks-long manual process to hours, producing a draft that reflects how scholars actually organize the discipline rather than an ad-hoc external classification. The draft still requires human validation (§4.A.3 Validation phase) and owner approval (§4.A.3 Commitment phase) — but it starts from a computationally derived scholarly consensus rather than from scratch.

**Technical approach.** TOC extraction from normalization engine's division trees. Cross-work alignment uses LLM analysis with Instructor for structured output. Sentence-transformers for title embedding similarity during alignment. NetworkX for tree structure construction and validation.

[NOT YET IMPLEMENTED] — Full specification provided; no code exists. Depends on: normalization engine's division tree output, source engine's work registry, LLM with Arabic scholarly knowledge, Instructor library.

**Example: Corpus-Driven Tree for Sarf (Morphology).**

5 registered Sarf works are analyzed:
- شذا العرف (al-Hamlawi): كتاب الأبنية → باب التصريف → باب الإعلال → باب الإبدال → باب المصادر
- المقدمة الصرفية (al-Hattab): similar structure but merges إعلال and إبدال into one chapter
- شرح التصريف العزي: starts with المجرد and المزيد before proceeding to إعلال
- تصريف الأفعال (al-Na'ma): organizes by verb form (فعل ثلاثي، رباعي) rather than by phenomenon
- النحو الوافي §morphology (Abbas Hasan): comprehensive, matches majority structure

Cross-work alignment reveals: الأبنية (patterns), التصريف (conjugation), الإعلال (vowel changes), الإبدال (consonant substitution) appear in 4/5 works (≥60% threshold). المصادر appears in 3/5. Organization-by-verb-form (from al-Na'ma) is unique to one work — noted but not included. Draft tree generated with consensus structure, Hamlawi ordering (most common), and al-Na'ma's organizational alternative documented.

#### §4.B.4 — Scholarly Disagreement Topology (خريطة الخلاف)

The taxonomy engine computes a structured disagreement map for every science that has schools (per SCIENCE.md). For each leaf, the engine classifies the scholarly state into one of five categories based on the placed excerpts and their metadata:

**Category 1: Ijma' (consensus).** All schools with positions at this leaf agree on the ruling or definition. Specifically: 3+ schools are represented (from `school` metadata on placed excerpts), and the LLM determines that no genuine position conflict exists between them. The engine sends the excerpt topics and primary texts from each school to the LLM with the prompt: "Do these excerpts from different schools express the same position, or do they contain genuine scholarly disagreement?" The LLM returns a structured response: `consensus: true/false`, `reasoning: string`. If consensus is true, the leaf is classified `ijma_detected` with confidence equal to the number of agreeing schools divided by the total known schools for the science.

**Category 2: Active khilaf (disagreement).** Two or more schools hold distinguishably different positions. The engine identifies the positions by clustering excerpts at the leaf by school affiliation, then calling the LLM (via Instructor, model `claude-sonnet` as primary with `gpt-4o` as consensus second, structured output schema: `{positions: [{schools: [str], summary: str, evidence_types: [str]}], reasoning: str}`) to summarize each school's position in one sentence and determine whether positions are genuinely different. The output per leaf is an array of `DisagreementPosition` objects, each containing: `schools` (array of school names that hold this position), `position_summary` (string, LLM-generated one-sentence summary), `evidence_types` (array of evidence types cited by this school for this position, from `evidence_refs` metadata), `earliest_scholar_date` (hijri year, from author metadata), `latest_scholar_date` (hijri year).

**Category 3: Apparent consensus (potential false consensus).** Only one school's view is represented because the library lacks other schools' sources, but the science is known to have schools (per SCIENCE.md). The leaf is classified `apparent_consensus_unverified` with a note: "Only {school} is represented. Other schools may disagree but no sources are present." This is distinct from Category 1 — Category 1 requires positive evidence of agreement from 3+ schools; Category 3 flags the absence of data rather than claiming agreement.

**Category 4: Intra-school disagreement.** Excerpts from the SAME school at this leaf express different positions. This happens when a school has internal debates (e.g., within the Hanafi school, Abu Hanifa vs. Abu Yusuf vs. Muhammad). The engine detects this when 2+ excerpts share a `school` value but the LLM determines they express different positions. The output records: `school`, `internal_positions` (array of position summaries with scholar attributions).

**Category 5: Insufficient data.** Fewer than 2 verified excerpts at the leaf, or no school metadata available. The leaf is classified `insufficient_for_disagreement_analysis`.

**Aggregation to branch and science level.** For each branch, the engine computes: `ijma_leaf_count`, `khilaf_leaf_count`, `apparent_consensus_leaf_count`, `insufficient_leaf_count`. For the science, the engine computes: percentage of leaves in each category, and a `khilaf_hotspot_list` — the top 10 branches by proportion of active khilaf leaves.

**Pattern detection across the science.** After computing per-leaf classifications, the engine identifies recurring disagreement patterns. Specifically, it examines all Category 2 leaves and groups them by which schools oppose each other. If the same school pair (e.g., Hanafi vs. Shafi'i) accounts for >40% of disagreements in the science, this pattern is recorded as a `dominant_disagreement_axis` with the school pair and a count. The engine then sends the dominant axis's leaves to the LLM with the prompt: "These {n} topics all have Hanafi-Shafi'i disagreement. Is there a common underlying methodological principle (usuli or otherwise) that drives these disagreements, or are they independent?" The LLM's response is recorded as `axis_root_cause_hypothesis` — a string that the synthesizer can use as narrative material.

**Output.** Written to `library/sciences/{science_id}/disagreement_topology.json`. Updated after every placement event that changes school representation at a leaf. The schema contains: `science_id`, `computed_utc`, `tree_version`, `per_leaf_classifications` (array), `branch_aggregations` (array), `science_summary` (object with category percentages), `khilaf_hotspots` (array), `dominant_disagreement_axes` (array with `school_pair`, `leaf_count`, `axis_root_cause_hypothesis`).

**Interaction with coverage analytics.** School gaps (§4.A.6) and disagreement topology are complementary but distinct. A school gap says "Maliki sources are missing." Disagreement topology says "Of the topics where Maliki IS represented, they disagree with the Shafi'i school 73% of the time." Coverage gaps are about what's ABSENT; disagreement topology is about what's PRESENT.

**Edge cases:**
- Sciences without schools (e.g., Tajwid, Nahw): the engine skips school-based analysis but still computes intra-science disagreement by clustering excerpts at each leaf by position content. The output uses `positional_disagreement` instead of `school_disagreement`.
- A leaf with excerpts from only one source per school: the engine computes disagreement but marks it `low_robustness` because the analysis rests on single-source evidence per school.
- A leaf where the same author changes position between works: the engine treats each work's position independently (per excerpt), and flags the author-level shift in `intra_author_shifts`.

**Why this is transformative.** No existing Islamic studies tool quantifies the topology of scholarly disagreement across an entire science. Classical ikhtilaf compilations (e.g., al-Mawsu'ah al-Fiqhiyyah, Bidayat al-Mujtahid) organize disagreements topic-by-topic but never reveal structural patterns: "80% of Hanafi-Shafi'i disagreements in worship law stem from differing positions on hadith authentication methodology." KR's disagreement topology makes these patterns visible and queryable. The synthesizer uses it to produce school-context sections in entries. The scholar interface uses it for Scenario 7's science map — showing disagreement hotspots as red regions on the tree. The student can ask: "Show me all topics where the four schools unanimously agree" — a question that would take months of manual research to answer, but KR can answer in seconds from the pre-computed topology.

**Technical approach.** LLM analysis with Instructor for structured disagreement classification per leaf. Aggregation is deterministic computation (counting, grouping). Pattern detection combines deterministic grouping with LLM analysis for root cause hypotheses. No external libraries beyond Instructor and the LLM APIs.

[NOT YET IMPLEMENTED] — Full specification provided; no code exists. Depends on: placed excerpts with school metadata, science configuration (school list), LLM with Arabic scholarly knowledge, Instructor library.

**Example: Disagreement Topology for a Fiqh Leaf.**

Leaf `fiqh/salat/qunut_fajr` has 5 verified excerpts:
- 2 Shafi'i excerpts: القنوت سنة في صلاة الصبح (qunut is sunnah in fajr prayer)
- 1 Hanafi excerpt: القنوت في الوتر لا في الصبح (qunut in witr, not fajr)
- 1 Hanbali excerpt: القنوت في النوازل فقط (qunut only during calamities)
- 1 Maliki excerpt: القنوت سنة في الصبح (same as Shafi'i)

Classification: **Category 2 (active khilaf)** — 3 distinct positions:
1. Position 1 (Shafi'i + Maliki): "Qunut is sunnah in fajr prayer permanently." Evidence: hadith of Anas.
2. Position 2 (Hanafi): "Qunut is performed in witr prayer, not fajr." Evidence: hadith interpretation differences.
3. Position 3 (Hanbali): "Qunut is only during calamities (nawazil)." Evidence: specific hadith limitations.

Aggregation: this leaf contributes to the Shafi'i-Hanafi disagreement axis. If this axis appears in >40% of fiqh worship leaves, a `dominant_disagreement_axis` pattern is detected.

#### §4.B.5 — Proactive Tree Evolution Prediction (استشراف التطور)

The taxonomy engine predicts where the science tree will need to evolve BEFORE draft excerpts are processed, using the structural organization of newly registered sources. This is architecturally distinct from §4.A.5 (reactive signal detection after placement failures) — proactive prediction uses source metadata available BEFORE excerpting begins.

**Trigger.** When a new source is registered in the source engine's work registry and has a normalization-produced division tree (the hierarchical structure of كتاب/باب/فصل/مسألة from the normalization engine's output), the taxonomy engine receives a notification containing: `source_id`, `science_id`, `division_tree` (the source's internal structural organization).

**Prediction algorithm.** The engine aligns the source's division tree against the science's active taxonomy tree. For each leaf node in the source's division tree that maps to content (i.e., it has actual text beneath it, not just structural nesting), the engine determines which taxonomy leaf it corresponds to. Alignment uses the same LLM-based topic matching as §4.A.1's Stage 1b, but operates on source SECTIONS (chapter titles + first 200 characters) rather than individual excerpts.

The engine then counts: for each taxonomy leaf, the number of distinct source sections that map to it. Three outcomes are possible per taxonomy leaf:

**One-to-one (no prediction).** Exactly one source section maps to the leaf. This is the expected case — the tree's granularity matches the source's organization. No evolution predicted.

**3+-to-one (split prediction).** Three or more source sections from the SAME source map to the same taxonomy leaf. This predicts the leaf is too coarse for this source's content. The engine generates a `split_prediction` containing: `leaf_path`, `source_id`, `mapped_section_count`, `section_titles` (the source's section titles that mapped here), `predicted_sub_topics` (the LLM's assessment of what distinct sub-topics the source sections cover), `confidence` (float 0.0–1.0, higher when more sections map to the same leaf). Confidence thresholds: ≥3 sections → 0.6 base; ≥5 sections → 0.8 base; adjusted downward by 0.1 if the source is known for unusually fine-grained organization. The threshold of 3 was chosen because 2 sections may represent the same sub-topic discussed from different angles (e.g., definition + examples), while 3+ strongly suggests genuinely distinct sub-topics.

**Unmapped sections (gap prediction).** A source section does not match any taxonomy leaf (LLM confidence < 0.4 for all candidates). This predicts a missing leaf. The engine generates a `gap_prediction` containing: `source_id`, `unmapped_section_title`, `unmapped_section_content_preview` (first 200 characters), `nearest_leaf` (the best candidate, which scored < 0.4), `predicted_topic` (LLM's characterization of what topic the section covers).

**Prediction aggregation.** Predictions from a single source are tentative. The engine accumulates predictions across sources. When 2+ sources independently generate the same split prediction for the same leaf (measured by overlap in `predicted_sub_topics` via embedding similarity ≥ 0.7), the prediction is elevated to `high_confidence_evolution_signal` — functionally equivalent to 3 reactive signals from §4.A.5, skipping the signal accumulation wait.

**Output.** Written to `library/sciences/{science_id}/evolution/predictions/{source_id}_predictions.json` per source. Aggregated predictions written to `library/sciences/{science_id}/evolution/predictions/aggregated.json`. High-confidence predictions are automatically converted to evolution proposals (§3.4) and routed to the human gate.

**Interaction with reactive evolution (§4.A.5).** Proactive predictions and reactive signals feed the same evolution evaluation pipeline. A proactive prediction counts as one signal in §4.A.5's accumulation. If a proactive split prediction is confirmed by a subsequent reactive divergence signal (§4.A.5 Signal 1) from an actual placed excerpt, the combined evidence triggers immediate evolution evaluation regardless of the `evolution_signal_accumulation` threshold.

**Owner notification.** When proactive predictions are generated for a new source, the owner is notified: "I've analyzed the structure of {source_title}. It has {n} sections that suggest your {science_name} tree needs adjustment at these leaves: {list}. Would you like to review these predictions now (before I process excerpts) or wait until excerpts confirm them?" This gives the owner the choice between preemptive tree refinement and wait-and-see.

**Edge cases:**
- Source with no division tree (e.g., a flat text with no chapters): no proactive predictions are generated. The engine relies entirely on reactive signals from §4.A.5.
- Source whose organizational style is idiosyncratic (e.g., an alphabetically organized dictionary rather than topically organized): the engine detects this by checking whether the source's section titles follow alphabetical ordering (Arabic abjad). If detected, the source is flagged `non_topical_organization` and its predictions are discounted (confidence multiplied by 0.3).
- Source in a science with no tree yet: predictions are stored but not evaluated until the tree is created. When the tree is created (§4.A.3), stored predictions are retroactively evaluated against the new tree.

**Why this is transformative.** Current taxonomy systems (including KR's §4.A.5) are reactive — they discover tree problems AFTER excerpts fail to place correctly. For a 12-volume Fiqh encyclopedia that will produce thousands of excerpts, reactive evolution means hundreds of excerpts may be placed at suboptimal leaves before the tree catches up. Proactive prediction inverts this: by analyzing the source's structure upfront, the tree can be refined BEFORE the first excerpt is processed. This is especially valuable during library bootstrapping (Scenario 1) when 5+ sources arrive at once and the initial trees are coarse. The owner experiences smooth onboarding instead of a flood of placement escalations and retrospective relocations.

**Technical approach.** Division tree alignment uses the same LLM-based topic matching as placement (§4.A.1 Stage 1b) — no new model needed. Section counting and aggregation are deterministic. Embedding similarity for cross-source prediction matching uses the same sentence-transformers model as §4.A.1 Stage 1c. Owner notification integrates with the human gate system.

[NOT YET IMPLEMENTED] — Full specification provided; no code exists. Depends on: normalization engine's division tree output, source engine's registration events, active taxonomy trees, LLM, Instructor library, sentence-transformers.

#### §4.B.6 — Scholarly Landscape Reconstruction (المشهد العلمي)

For each leaf with 2+ verified excerpts from 2+ distinct sources, the taxonomy engine constructs a **scholarly landscape** — a pre-computed, metadata-rich data structure that transforms raw excerpt metadata into the synthesizer's primary narrative fuel. The scholarly landscape answers the question: "For this topic, who said what, when, in response to whom, and how did the discourse evolve?"

This capability bridges the gap between the taxonomy engine's placed excerpts and the synthesizing engine's entries. Without it, the synthesizer must perform ad-hoc research for every entry — analyzing author dates, teacher-student chains, school affiliations, and citation patterns from scratch. The scholarly landscape pre-computes this analysis once, ensuring consistency across entries and enabling the narrative depth shown in ENTRY_EXAMPLE.md.

**Input.** For a given leaf: all placed verified excerpts, their full upstream metadata (source metadata, author metadata from the scholar authority registry, school affiliations, evidence types, content types, quoted scholars, implicit references from the excerpting engine's §4.B output).

**Landscape construction.** The engine builds five sub-structures per leaf:

**(a) Chronological position timeline.** All distinct scholarly positions at the leaf, ordered by the earliest author who held them. Each timeline entry contains: `position_id` (format `pos_{leaf_id}_{sequence}`), `position_summary` (LLM-generated one-sentence description of what this position claims), `first_known_proponent` (author with earliest death date who holds this position, from excerpt metadata), `first_known_date_hijri` (that author's death date), `subsequent_proponents` (array of {author, date, excerpt_id} for later scholars who explicitly held the same position), `school_affiliations` (which schools adopted this position), `evidence_basis` (array of evidence types cited for this position). The timeline enables the synthesizer to write: "This position was first articulated by X (d. Y AH) and later adopted by Z (d. W AH)."

Position identity is determined by semantic equivalence: two excerpts express the "same position" if the LLM judges their substantive claims to be identical despite different wording. The LLM receives both excerpts' primary text and is prompted: "Do these two excerpts express the same scholarly position on {leaf_title}, or genuinely different positions? Respond with: same_position (true/false), reasoning (string)." Excerpts from different schools that reach the same conclusion via different evidence are classified as the same position with a note: `convergent_evidence: true`.

**(b) Influence chain graph.** For each pair of scholars who address this topic, the engine determines whether an influence relationship exists. Influence is inferred from three sources, in priority order:

1. **Explicit citation.** The excerpting engine's `quoted_scholars` metadata shows that Scholar B's excerpt quotes or cites Scholar A. This is direct evidence of influence.
2. **Teacher-student relationship.** The scholar authority registry records that Scholar B studied under Scholar A (or under a chain that traces back to Scholar A). Combined with both scholars addressing the same topic, this implies transmission of ideas.
3. **Temporal + positional inference.** Scholar B (later date) holds the same position as Scholar A (earlier date) and Scholar B's school traces intellectual lineage to Scholar A. This is weak evidence — recorded with `inferred: true` and `inference_confidence` (0.0–1.0).

The influence chain is stored as a directed acyclic graph: nodes are scholars (with `scholar_id`, `name`, `death_date_hijri`, `school`), edges are influence relationships (with `type: explicit_citation | teacher_student | temporal_inference`, `confidence`, `excerpt_ids` that evidence the relationship). The synthesizer uses this graph to produce sentences like: "Ibn al-Sarraj was a student of al-Mubarrad, who was himself a student of al-Jarmi, who studied with al-Akhfash al-Awsat — Sibawayhi's own student."

**(c) Discourse evolution narrative.** The engine uses the chronological timeline and influence chain to identify discourse transitions — moments when the scholarly conversation shifted. Three transition types are detected:

- **Refinement.** Scholar B holds the same position as Scholar A but adds precision or restricts scope. Detected when the LLM judges: "B's position is a strict subset or refinement of A's position."
- **Opposition.** Scholar B explicitly argues against Scholar A's position. Detected from `quoted_scholars` with role `refuted_position`, or from the LLM's analysis of content type `refutation` atoms in B's excerpt.
- **Synthesis.** Scholar C combines elements of Scholar A's and Scholar B's competing positions into a new position. Detected when C's position shares elements with both A and B (by LLM judgment) and C's date is later than both A and B.

The transitions are recorded as an array of `DiscourseTransition` objects: `transition_type`, `from_scholar`, `to_scholar`, `description` (LLM-generated explanation of what changed and why), `excerpt_ids` (evidence).

**(d) Evidence evolution map.** For each position in the timeline, the engine tracks how the evidence basis changed over time. Early scholars may cite Quran and hadith directly; later scholars may cite earlier scholars' rulings as precedent; post-classical scholars may cite consensus (ijma') rather than original evidence. The map records: `position_id`, `evidence_by_period` (array of {`period_start_hijri`, `period_end_hijri`, `dominant_evidence_types`, `example_excerpt_id`}). Periods are determined by natural clustering of author death dates (gaps of ≥100 hijri years between clusters define period boundaries).

**(e) School positioning summary.** For each school represented at the leaf, a structured summary: `school`, `position_id` (which position this school holds), `earliest_proponent` (author + date), `latest_proponent` (author + date), `internal_unity` (boolean — false if intra-school disagreement exists per §4.B.4 Category 4), `strength_of_evidence` (the diversity and quality of evidence cited: count of distinct evidence types used). This enables the synthesizer to write school-by-school sections with temporal context.

**Output.** Written to `library/sciences/{science_id}/content/{leaf_path}/landscape.json`. Updated when: a new excerpt is placed at the leaf, an excerpt is relocated to or from the leaf, or scholar authority data is updated. The schema contains: `leaf_path`, `computed_utc`, `tree_version`, `excerpt_count` (number of verified excerpts contributing), `source_count` (number of distinct sources), `chronological_timeline` (array of positions), `influence_graph` (nodes + edges), `discourse_transitions` (array), `evidence_evolution` (array), `school_positioning` (array), `landscape_confidence` (float 0.0–1.0, based on data richness: higher when more sources, more schools, wider temporal span).

**Confidence scoring.** Landscape confidence is computed as: `min(source_diversity_score, temporal_span_score, school_coverage_score)`, where:
- `source_diversity_score`: `min(1.0, distinct_source_count / 4)` — 4+ sources gives full confidence.
- `temporal_span_score`: `min(1.0, temporal_span_hijri / 400)` — 400+ years of scholarly coverage gives full confidence.
- `school_coverage_score`: `min(1.0, represented_schools / total_schools_in_science)` — full school coverage gives full confidence. For sciences without schools, this factor is omitted.

Low-confidence landscapes (< 0.4) are still computed and stored, but marked `preliminary` — the synthesizer should note the limited evidence base in the entry.

**Edge cases:**
- Leaf with excerpts from only one author: the landscape degenerates to a single-point timeline with no influence chains. It is still useful — it records the author's position, evidence, and school affiliation.
- Leaf with excerpts from the same period only (all authors within 50 hijri years): the temporal analysis is limited, but positional and school analysis still applies. The `evidence_evolution` sub-structure is empty.
- Quoted scholars in excerpts who are not in the scholar authority registry: the engine records them with the name from the excerpt metadata and `scholar_id: null`. A human gate checkpoint is created to resolve the scholar's identity.
- Circular influence (scholar A cites B who cites A): possible when scholars are contemporaries debating each other. The influence graph remains a DAG by recording the direction of citation per excerpt, not per scholar pair. If A cites B in one excerpt and B cites A in another, both directed edges exist — this is not a cycle in the scholarly sense but a dialogue.

**Why this is transformative.** The entry example in ENTRY_EXAMPLE.md shows the target quality: temporal depth, intellectual genealogy, school context, evidence evolution, discourse narrative. Today, producing ONE such entry requires a scholar to manually research author dates, trace teacher-student chains, compare evidence across centuries, and construct a narrative — a process that takes hours per topic. KR's scholarly landscape pre-computes ALL of this from metadata, for EVERY populated leaf, automatically. The synthesizer receives a ready-made narrative scaffold and focuses on prose quality rather than research. When the library has 200 populated leaves, the scholarly landscape has pre-computed 200 temporal analyses, 200 influence graphs, and 200 discourse narratives — a research effort that would take a human scholar months, done incrementally as excerpts are placed.

The scholarly landscape also reveals knowledge the library implicitly contains but no single source explicitly states. No one source says "the Basran definition of المبتدأ was transmitted through a four-generation chain from Sibawayhi to Ibn al-Sarraj." That knowledge is COMPUTED from the intersection of teacher-student metadata, positional similarity, and temporal ordering across 2+ sources. The landscape makes implicit scholarly relationships explicit.

**Technical approach.** Position clustering uses LLM analysis with Instructor for structured output. Influence chain construction uses the scholar authority registry (graph traversal with NetworkX) combined with excerpting engine citation metadata. Discourse transition detection uses LLM classification. Period clustering for evidence evolution uses simple temporal gap analysis. All sub-structures are JSON-serializable.

[NOT YET IMPLEMENTED] — Full specification provided; no code exists. Depends on: placed excerpts with full upstream metadata, scholar authority registry, excerpting engine's quoted_scholars and implicit reference data, LLM with Arabic scholarly knowledge, Instructor library, NetworkX for influence graph.

**Example: Scholarly Landscape for `nahw/marfu'at/mubtada`.**

5 verified excerpts from 4 sources, 3 scholars:

Chronological timeline:
- Position 1 (earliest): "المبتدأ هو الاسم المجرد عن العوامل اللفظية" — first by Sibawayhi (d. 180 AH), adopted by al-Mubarrad (d. 286 AH). School: Basran.
- Position 2: "المبتدأ هو المسند إليه" — by Ibn al-Sarraj (d. 316 AH), refining Sibawayhi's definition. School: Basran.
- Position 3: "المبتدأ ما حَسُن السكوت عليه مع خبره" — by Ibn Hisham (d. 761 AH), synthesizing earlier definitions. School: Egyptian.

Influence chain: Sibawayhi → al-Mubarrad (teacher-student, confidence 1.0) → Ibn al-Sarraj (teacher-student, confidence 1.0). Ibn al-Sarraj → Ibn Hisham (temporal inference, confidence 0.6 — no direct chain but positional refinement).

Discourse transitions: [Refinement] Ibn al-Sarraj refined Sibawayhi's definition by adding المسند إليه. [Synthesis] Ibn Hisham combined grammatical and semantic criteria from both earlier definitions.

Landscape confidence: source_diversity = min(1.0, 4/4) = 1.0; temporal_span = min(1.0, 581/400) = 1.0; school_coverage = min(1.0, 2/3) = 0.67. Overall: **0.67**.

---

## 5. Validation and Quality

The taxonomy engine's output directly shapes what Rayane knows. A misplaced excerpt means Rayane encounters it in the wrong context. A missing leaf means a topic is invisible. A bad evolution orphans excerpts. Quality validation is therefore critical.

### 5.1 Self-Validation (§8 Layer 1)

**Placement validation.** After every placement decision, the engine verifies: (a) the confirmed leaf exists in the active tree, (b) the excerpt's `science_id` matches the tree's science, (c) the excerpt file was written successfully (file existence + size > 0), (d) the coverage analytics were updated. Failure of any check triggers `TAX_PLACEMENT_INTEGRITY_ERROR` (fatal — the placement is reverted and the excerpt returns to draft status).

**Tree integrity validation.** After every tree modification (construction, evolution, rollback), the engine verifies: (a) every leaf is reachable from the root, (b) no node has zero children except leaves, (c) node IDs are unique within the tree, (d) the tree is acyclic, (e) every placed excerpt's `confirmed_leaf` resolves to a leaf in the new tree. Failure triggers `TAX_TREE_INTEGRITY_ERROR` (fatal — the modification is reverted). Tree integrity uses NetworkX graph validation.

**Evolution invariant enforcement.** Before submitting an evolution proposal to the human gate, all four §4.4 invariants are verified programmatically. The zero-orphans check is performed by attempting redistribution of every affected excerpt. The sibling coherence check is performed by LLM classification of a sample of affected excerpts. Proposals that fail any invariant are never presented to the owner.

### 5.2 Automated Checks (§8 Layer 2)

**Coverage consistency.** The analytics must reflect the actual excerpt distribution. A nightly job recomputes all coverage metrics from the placed excerpt files and compares against the cached analytics. Discrepancies trigger `TAX_COVERAGE_DRIFT` (warning — the cache is rebuilt).

**Cross-version placement validity.** After a tree evolution, a batch job checks that every excerpt in the science has a `confirmed_leaf` that resolves to a leaf in the current tree version. Excerpts referencing leaves that no longer exist (due to evolution that was not properly migrated) trigger `TAX_ORPHAN_DETECTED` (fatal — the excerpt is returned to reviewed status).

**Duplicate cluster staleness.** Duplicate clusters are recomputed monthly. New excerpts placed since the last computation may have created new clusters or changed existing ones.

### 5.3 Human Gate Integration

**Placement review.** Excerpts with placement confidence < 0.8 or with ambiguous candidate rankings are presented to the owner for review. The owner sees: the excerpt's Arabic text, the proposed leaf with its full path, alternative candidates with scores, and the engine's reasoning. The owner can approve, select a different leaf, or flag the excerpt.

**Evolution review.** Evolution proposals are always human-gated (§9.3). The owner sees: a structural diff (current tree vs. proposed tree), the list of excerpts that will be redistributed with their proposed new leaves, the trigger signal that prompted the evolution, and the invariant check results. The owner can approve, reject, or modify (adjust the proposed structure).

**Severity classification.** Placement errors are WARNING severity (a single excerpt in the wrong place is correctable). Tree integrity errors are FATAL severity (structural corruption affects all excerpts). Evolution invariant failures are FATAL severity (proposal is discarded).

---

## 6. Consensus Integration

The taxonomy engine uses multi-model consensus for ONE specific decision: **leaf selection in ambiguous placement cases.**

When the placement algorithm (§4.A.1) produces a top candidate with score 0.5–0.8, or when two candidates are within 0.1 of each other, the engine runs a second LLM (from a different provider) on the same placement task. Agreement between the two models increases confidence. Disagreement maintains the lower score and triggers human gate escalation.

Consensus is NOT used for: tree construction (which is a research task requiring coherent vision, not averaging), evolution proposal generation (same reason), coverage analytics (deterministic computation), or placements scoring ≥ 0.8 (where single-model accuracy meets the quality bar).

**Consensus configuration.** Two models from different providers (e.g., Claude and GPT). Agreement threshold: both models must select the same leaf within the tree. If they select different leaves, the placement is escalated to the human gate with both models' selections presented. **Provider fallback:** if one provider is unavailable (API error after 3 retries with exponential backoff), the engine falls back to single-model placement with the available provider, but the placement confidence is capped at 0.75 (forcing human gate review for any borderline case). The fallback is logged with `TAX_CONSENSUS_DEGRADED`.

**Rationale for limited consensus.** Unlike excerpting (where self-containment judgment has profound quality implications), most taxonomy decisions are either clearly correct (score ≥ 0.8) or genuinely ambiguous (requiring human judgment). The middle band where consensus adds value — where one model is right and the other is wrong, and the right answer can be identified by agreement — is narrow. For this reason, consensus is applied selectively rather than universally.

---

## 7. Error Handling

### 7.1 Input Errors

| Error Code | Severity | Trigger | Recovery |
|---|---|---|---|
| `TAX_MISSING_REQUIRED_FIELD` | Fatal | Draft excerpt missing required field | Excerpt rejected. Logged with field name and excerpt_id. Excerpting engine notified. |
| `TAX_MISSING_EXPECTED_FIELD` | Warning | Draft excerpt missing expected field | Excerpt proceeds with degraded confidence. Warning logged. |
| `TAX_INVALID_SCIENCE` | Fatal | `science_id` not in registry | Excerpt rejected. May indicate misconfigured source metadata. |
| `TAX_PENDING_NO_TREE` | Info | Valid science but no active tree | Excerpt queued in pending. Resumed when tree is created. |
| `TAX_INVALID_PROPOSED_LEAF` | Warning | `proposed_leaf` doesn't resolve | Treated as null. Engine performs independent classification. |

### 7.2 Processing Errors

| Error Code | Severity | Trigger | Recovery |
|---|---|---|---|
| `TAX_UNPLACEABLE` | Warning | No candidate leaf scores ≥ 0.5 | Excerpt held in staging. Evolution signal generated. Owner notified. |
| `TAX_PLACEMENT_TIE` | Info | Two candidates within 0.1 | Escalated to human gate. |
| `TAX_LLM_FAILURE` | Warning | LLM call fails during placement | Retry with exponential backoff (3 attempts). If all fail, excerpt queued for retry. |
| `TAX_EMBEDDING_FAILURE` | Warning | Embedding computation fails | Placement proceeds without embedding candidates (LLM-only). |
| `TAX_PLACEMENT_INTEGRITY_ERROR` | Fatal | Post-placement validation fails | Placement reverted. Excerpt returns to draft. Alert generated. |

### 7.3 Evolution Errors

| Error Code | Severity | Trigger | Recovery |
|---|---|---|---|
| `TAX_EVOLUTION_INVARIANT_FAIL` | Fatal | Proposal fails §4.4 invariant | Proposal discarded with failure reason logged. No human gate. |
| `TAX_TREE_INTEGRITY_ERROR` | Fatal | Post-modification tree is invalid | Modification reverted from history. Alert generated. |
| `TAX_REDISTRIBUTION_FAILURE` | Fatal | Excerpt file operation fails during evolution | Entire evolution rolled back. All excerpts restored to pre-evolution state. |
| `TAX_ORPHAN_DETECTED` | Fatal | Post-evolution excerpt has invalid leaf | Excerpt returned to reviewed status. Alert generated. |
| `TAX_ROLLBACK_CONFLICT` | Warning | Rollback cannot place post-evolution excerpts | Post-evolution excerpts returned to reviewed status per §4.4 rollback completeness. |

### 7.4 Principle

Every error is logged with: timestamp, error code, severity, affected entity (excerpt_id, science_id, node_path as applicable), and recovery action taken. No error is silently swallowed. Fatal errors block further processing of the affected entity. Warnings allow processing to continue but are surfaced to the owner. The principle from D-033: a visible failure that stops processing is always preferable to an invisible error that enters the library.

---

## 8. Configuration

### 8.1 Global Parameters

| Parameter | Default | Valid Range | Description |
|---|---|---|---|
| `placement_auto_approve_threshold` | 0.8 | 0.5–1.0 | Minimum placement confidence for auto-approval (with pre-approval policy). |
| `placement_escalation_threshold` | 0.5 | 0.0–0.8 | Below this, excerpt is TAX_UNPLACEABLE. |
| `consensus_trigger_range` | [0.5, 0.8] | — | Placement confidence range that triggers multi-model consensus. |
| `candidate_tie_threshold` | 0.1 | 0.0–0.3 | Maximum score difference between top two candidates that constitutes a tie. |
| `embedding_model` | `intfloat/multilingual-e5-large` | any sentence-transformers model | Model for topic embedding similarity. |
| `duplicate_similarity_threshold` | 0.85 | 0.7–0.95 | Cosine similarity above which two excerpts are flagged as duplicates. |
| `evolution_divergence_threshold` | 0.65 | 0.4–0.8 | Cosine similarity below which a new excerpt's topic is considered divergent. |
| `evolution_signal_accumulation` | 3 | 1–10 | Number of independent signals needed before evaluating evolution. |
| `leaf_capacity_diagnostic` | 30 | 10–100 | Number of excerpts at a leaf before capacity diagnostic fires. |
| `max_hierarchical_search_leaves` | 200 | 50–1000 | Tree size above which placement search switches to hierarchical mode. |

### 8.2 Per-Science Configuration (Level 3 / SCIENCE.md)

Each science's SCIENCE.md may override:

- **School list.** Which schools exist in this science. Affects school gap detection.
- **Prerequisite edge configuration.** Whether hard prerequisites are mandatory before study (scholar interface enforcement) or advisory.
- **Evolution sensitivity.** Sciences with well-established, stable structures (e.g., Tajwid, Nahw) need higher signal thresholds before proposing evolution. Sciences with actively debated boundaries (e.g., Usul al-Fiqh sub-topics) need lower thresholds. Per-science SCIENCE.md files specify an `evolution_sensitivity` multiplier (0.5–2.0, default 1.0) applied to the global `evolution_signal_accumulation` threshold.
- **Narrative ordering authority.** Which work(s) define the canonical pedagogical sequence for this science.

### 8.3 Hardcoded Constraints (Not Configurable)

- Excerpts are placed only at leaves (§2.3 structural rule).
- Trees branch by topic, never by school (§4.5).
- Evolution is always human-gated (§9.3).
- Placed excerpts are never deleted by the taxonomy engine (they may be relocated, but never removed).
- Tree version history is never pruned (complete audit trail).

---

## 9. Current Implementation State

### 9.1 Existing Code

**`engines/taxonomy/src/evolve_taxonomy.py`** (2377 lines). ABD-era evolution tool. Capabilities:
- Signal detection: scans for unmapped excerpts, cluster signals, multi-topic signals, user signals.
- LLM-driven proposal generation with optional multi-model consensus.
- Phase B: applies approved proposals to YAML trees, redistributes excerpts, bumps version.
- Handles both v0 (nested dict) and v1 (node list) YAML formats.

**`engines/taxonomy/tests/test_evolution.py`** (109 tests). Covers evolution signal detection, proposal generation, YAML modification, redistribution.

**`library/sciences/`** — 5 science trees exist:
- Nahw: `nahw_v1_0` (active)
- Sarf: `sarf_v1_0` (active)
- Imlaa: `imlaa_v1_0` (active, evolved from v0.1)
- Aqidah: `aqidah_v0_2` (active, evolved from v0.1)
- (Balagha exists in ABD-era data but may not be migrated to current structure)

**`library/sciences/taxonomy_registry.yaml`** — registry of active tree versions.

### 9.2 Gaps Between Current Code and This SPEC

| SPEC Feature | Current State | Gap |
|---|---|---|
| Placement algorithm (§4.A.1) | Not implemented. ABD code handles evolution only; placement was done by the excerpting tool. | **Full implementation needed.** Two-stage candidate generation + ranking. |
| Tree construction (§4.A.3) | Trees were manually created. No automated construction workflow. | **Full implementation needed.** Four-phase workflow with validation. |
| Coverage analytics (§4.A.6) | Not implemented. No coverage computation exists. | **Full implementation needed.** All gap types, per-leaf metrics. |
| Cross-science links (§4.A.9) | Not implemented. | **Full implementation needed.** |
| Terminology synonyms (§4.A.10) | Not implemented. | **Full implementation needed.** |
| Prerequisite edges | Not implemented. Trees are pure hierarchy. | **Full implementation needed.** |
| Narrative ordering | Tree children are ordered but ordering is not documented as meaningful. | **Clarification needed.** Existing ordering may already be pedagogical. |
| Semantic deduplication (§4.A.8) | Not implemented. | **Full implementation needed.** |
| Placed excerpt schema | `schemas/placed_excerpt.json` exists but uses ABD-era fields. | **Schema update needed** to match this SPEC's §3.1. |
| Human gate integration | Not implemented as structured pipeline. Evolution proposals generate review artifacts (Markdown) for manual review. | **Structured pipeline needed.** |
| Topic significance (§4.B.1) | [NOT YET IMPLEMENTED] | Transformative capability. |
| Difficulty estimation (§4.B.2) | [NOT YET IMPLEMENTED] | Transformative capability. |
| Corpus-driven tree construction (§4.B.3) | [NOT YET IMPLEMENTED] | Transformative capability. |
| Scholarly disagreement topology (§4.B.4) | [NOT YET IMPLEMENTED] | Transformative capability. |
| Proactive tree evolution prediction (§4.B.5) | [NOT YET IMPLEMENTED] | Transformative capability. |
| Scholarly landscape reconstruction (§4.B.6) | [NOT YET IMPLEMENTED] | Transformative capability. |
| Multi-model consensus for placement | Not implemented for placement. Exists for evolution proposals. | **Extend to placement.** |

### 9.3 External Dependencies

From `reference/RESOURCES.md`:
- **NetworkX** — tree structure representation, DAG operations for prerequisite graph, tree integrity validation. Python, MIT license.
- **Sentence-transformers** (`intfloat/multilingual-e5-large`) — topic embedding for placement candidate generation, deduplication detection, evolution signal divergence. Python, Apache 2.0.
- **Instructor** — structured LLM output for placement decisions, evolution proposals, significance scoring. Python, MIT.
- **CAMeL Tools** — Arabic text normalization for synonym matching and topic search. Python, MIT.
- **OpenRouter / Anthropic API / OpenAI API** — LLM providers for placement, evolution, tree construction. The taxonomy engine uses LLMs heavily for classification decisions.
- **PyYAML** — reading/writing tree YAML files (already in use by existing code).

---

## 10. Test Requirements

### 10.1 Must-Test Categories

**Placement correctness.** Gold baseline: 50+ excerpts with known correct leaves (manually verified by the owner or a domain expert). The placement algorithm must achieve ≥ 85% agreement with the gold baseline on first placement (before human gate correction). Track: top-1 accuracy, top-3 accuracy (correct leaf in top 3 candidates), mean placement confidence.

**Evolution invariants.** Every §4.4 invariant must have dedicated tests: (a) zero-orphans — create an evolution that would orphan an excerpt, verify it is rejected; (b) sibling coherence — create overlapping siblings, verify rejection; (c) excerpt non-interference — verify excerpts outside scope are unaffected; (d) entry lifecycle — verify stale markers are generated for affected leaves.

**Tree integrity.** After any tree modification, the integrity validator must pass. Tests: create trees with cycles (must fail), with unreachable nodes (must fail), with duplicate IDs (must fail), with valid structure (must pass).

**Coverage accuracy.** Place a known set of excerpts and verify that all gap types are correctly detected. Test each gap type independently: school gap (place excerpts from 3 of 4 schools), temporal gap (all authors from same century), evidence gap (opinions without evidence), prerequisite gap (dependent topic populated, prerequisite empty).

**Migration correctness.** After evolution, verify that every redistributed excerpt's `confirmed_leaf` resolves correctly, that no excerpt was lost, and that coverage metrics reflect the new state.

### 10.2 Gold Baselines

**Placement baseline.** Required before v1 launch. 50 excerpts per science (minimum 2 sciences) with manually assigned leaf paths. Used for placement accuracy measurement and regression testing.

**Tree validation baseline.** For each science tree, a set of representative source chapters with expected leaf mappings. Used during tree construction validation (§4.A.3) and for regression testing after evolution.

### 10.3 Regression Testing

Any code change to the placement algorithm must pass the placement gold baseline without accuracy degradation. Any code change to the evolution system must pass all invariant tests. Any schema change must verify backward compatibility with existing placed excerpts.

### 10.4 Integration Tests

**Upstream (excerpting engine).** The taxonomy engine must verify that incoming draft excerpts conform to the excerpting engine's output contract. Minimal integration test: read a real excerpt stream from the excerpting engine's test output and process it through placement.

**Downstream (synthesizing engine).** The synthesizing engine reads placed excerpts + coverage data + tree structure. Integration test: generate a complete leaf's data package (placed excerpts + coverage record + tree path + prerequisite data) and verify the synthesizing engine can consume it without errors.
