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
- `invariant_checks`: object confirming zero_orphans (bool), sibling_coherence (bool), excerpt_non_interference (bool).

Evolution proposals are written to `library/sciences/{science_id}/evolution/pending/{proposal_id}.json`. Approved proposals move to `library/sciences/{science_id}/evolution/applied/`. Rejected proposals move to `library/sciences/{science_id}/evolution/rejected/`.

**Metadata pass-through (D-023).** The taxonomy engine preserves ALL upstream metadata on every placed excerpt. It adds: `confirmed_leaf`, `placement_confidence`, `placement_reasoning`, `placed_utc`, `review_metadata`, `taxonomy_version_at_placement`, `verified_flagged_status`. These additions are the taxonomy engine's contribution to the metadata chain that flows to the synthesizer.

---

## 4. Processing Specification

### §4.A — Core Processing

#### §4.A.1 — Placement Algorithm

Placement determines which leaf an excerpt belongs at. The algorithm uses a two-stage approach: candidate generation followed by candidate ranking.

**Stage 1: Candidate generation.** The taxonomy engine generates a set of candidate leaves. Three sources contribute candidates:

(a) **Excerpting engine proposal.** If `proposed_leaf` is non-null and resolves to a valid leaf, it becomes the first candidate with its `proposed_leaf_confidence` score.

(b) **Topic-based search.** The engine uses the `excerpt_topic` text and `terminology_variants` to search the active tree for matching leaves. The search is LLM-driven: the engine sends the excerpt topic, the tree's branch structure (titles only — not the full tree), and asks the LLM to identify the 3–5 most likely leaf paths. For trees with more than 200 leaves, the search is hierarchical: first identify the correct branch (top 3), then identify the correct leaf within each candidate branch.

(c) **Embedding similarity.** The engine computes a sentence embedding of `excerpt_topic` (using multilingual-e5-large or equivalent) and compares it against precomputed embeddings of all leaf titles in the science tree. The top 3 leaves by cosine similarity become additional candidates if they are not already in the candidate set. This catches terminology mismatches that LLM search might miss.

**Stage 2: Candidate ranking.** Each candidate leaf is scored by the LLM on a 0.0–1.0 scale, considering: (a) does the excerpt's teaching content match the leaf's topic? (b) is there a more specific leaf that would be a better fit? (c) does the excerpt's content overlap with existing excerpts at this leaf (checked by providing titles/topics of existing excerpts at the leaf)? The highest-scoring candidate is selected.

**Placement decision rules:**

- If the top candidate scores ≥ 0.8: the excerpt is placed at that leaf. If a pre-approval policy covers this source and science, placement proceeds without human gate. Otherwise, placement is queued for human gate review.
- If the top candidate scores 0.5–0.8: placement is always escalated to human gate review, regardless of pre-approval policies. The owner sees the top 3 candidates with scores and reasoning.
- If no candidate scores ≥ 0.5: the excerpt is flagged as `TAX_UNPLACEABLE` and held in a staging area. This is an evolution signal — the tree may lack the right leaf. The excerpt is not silently discarded; it is visible to the owner with an explanation.
- If two candidates score within 0.1 of each other (tie condition): escalated to human gate with both candidates presented.

**The excerpting engine's proposal is a hint, not a constraint.** The taxonomy engine may override `proposed_leaf` with a different leaf if its own analysis determines a better placement. When it overrides, it records: `proposed_leaf_override: true`, `proposed_leaf_original`, `override_reason`.

#### §4.A.2 — Placement Validation

After the placement decision, before writing the placed excerpt, the taxonomy engine performs validation checks:

**One-excerpt-per-source-per-leaf diagnostic (§5.5).** If another excerpt from the same `source_id` is already placed at the same leaf, the diagnostic fires. The engine evaluates whether the two excerpts should be merged (they cover the same sub-topic in different sections of the source) or whether the leaf should evolve (they cover distinguishably different sub-topics). If the incoming excerpt has review flag `cross_topic_candidate`, it is exempt from this diagnostic per §5.5's interaction clause. The diagnostic result is recorded in the placement record but does not block placement — it may trigger a merge suggestion or evolution signal.

**Verified/flagged consistency.** If the excerpt's source has a `trust_tier` that maps to `flagged`, the excerpt receives `verified_flagged_status: flagged` unless the owner has explicitly overridden the source's trust evaluation for this excerpt. Conversely, an individually flagged excerpt from a verified source receives `flagged` status with the specific `flag_reason`. The taxonomy engine never promotes an excerpt from flagged to verified autonomously — that requires human gate review.

**Leaf capacity check.** This is purely diagnostic. When a leaf accumulates more than 30 verified excerpts, a diagnostic is logged suggesting the owner review whether the leaf is too coarse. This is NOT an evolution trigger — it is an informational signal.

#### §4.A.3 — Tree Construction

Tree construction follows the four-phase workflow defined in §4.2 (Research → Draft → Validation → Commitment). The taxonomy engine specifies the procedures within each phase.

**Research phase.** For a given science, the engine receives a set of authoritative works (identified by the owner or by the source engine's work registry). The engine analyzes the tables of contents of these works — not the full text, but the structural organization: كتاب/باب/فصل/مسألة headings. The LLM synthesizes these organizational frameworks into a common structure, noting where works agree on organization and where they diverge. The output is a research report listing: the works consulted, the organizational patterns found, points of agreement, points of divergence, and a recommended structure with rationale.

The research phase also queries the scholar authority registry for the science's known scholarly tradition: which schools exist, which are the foundational works, what organizational conventions are standard. This context informs the tree design.

**Draft phase.** The engine generates a draft tree from the research report. The draft follows the granularity bias principle (§4.2): err on the side of finer distinctions. Each proposed leaf receives a title in Arabic reflecting standard scholarly terminology for that topic. Each proposed branch receives a title matching the science's conventional chapter-level terminology.

Narrative ordering is assigned during drafting: the children of each branch are ordered according to the pedagogical sequence found in the majority of consulted works. Where works disagree on ordering, the engine records the disagreement and proposes the ordering from the work considered most pedagogically sound (by the LLM's assessment, subject to owner override).

Prerequisite edges are proposed during drafting: for each leaf, the engine identifies which other leaves contain concepts that must be understood first. Hard prerequisites are concepts without which the dependent topic is incomprehensible. Soft prerequisites are concepts that improve understanding but are not strictly required.

**Validation phase.** The draft tree is validated against real content. The engine takes 3–5 representative sources in the science (chosen for breadth of coverage) and tests whether each source's chapters map cleanly to the tree's leaves. Specifically, for each chapter in each source, the engine asks: which leaf(s) would this chapter's content be placed at? Three failure modes are checked:

- **Orphan content.** A chapter covers a topic not represented by any leaf. This reveals a missing leaf.
- **Split content.** A single chapter spans multiple distinguishable sub-topics that map to different leaves. This is expected and acceptable — it means the tree is appropriately granular.
- **Collapsed content.** Multiple chapters from the same source all map to the same leaf. This suggests the leaf is too coarse and should be split.

Failures are recorded in the validation report. The engine proposes fixes for each failure. The owner reviews the validation report and approves the draft (with or without modifications).

**Commitment phase.** The approved tree is written as `tree.yaml` with version `v1.0`. The tree is registered in `library/sciences/taxonomy_registry.yaml`. History copy is written. Coverage analytics are initialized (all zeros). The tree is now active and ready to receive excerpts.

#### §4.A.4 — Primary Topic Determination

When an excerpt mentions multiple topics (§5.3, Rule 1), the taxonomy engine determines the primary topic — the topic the excerpt exists to teach. The determination uses three signals:

(a) **Core atom analysis.** The excerpt's `core_atom_ids` identify which atoms are the "teaching content." The taxonomy engine examines the scholarly functions of core atoms (from atom metadata): if the majority of core atoms are `definition`, `ruling`, or `opinion_marker` atoms about Topic A, and the context atoms are about Topic B, then Topic A is primary.

(b) **Excerpt topic text.** The `excerpt_topic` field from the excerpting engine is a direct statement of what the excerpt teaches.

(c) **LLM judgment.** When signals (a) and (b) conflict, or when the determination is ambiguous, the LLM reads the excerpt's `primary_text` and the candidate leaf descriptions, then determines which topic the author intended to teach. The LLM's prompt includes: "This excerpt may mention multiple topics. Determine which topic the author is primarily teaching, not merely referencing."

Primary topic determination is logged with the reasoning, supporting auditability (D-033).

#### §4.A.5 — Evolution Signal Detection

The taxonomy engine continuously monitors for evolution signals. Five signal types are defined:

**Signal 1: Subtopic divergence.** When a leaf accumulates excerpts that cover distinguishably different sub-topics, the leaf may need to split. Detection: after every placement, the engine checks whether the new excerpt's `excerpt_topic` is semantically distinct from existing excerpts at the leaf. Semantic distinctness is measured by embedding cosine similarity: if the new excerpt's topic embedding has cosine similarity < 0.65 with the centroid of existing excerpt topics at the leaf, a divergence signal is raised. The signal is raised — not acted upon — as a candidate for evolution evaluation.

**Signal 2: Unplaceable excerpt.** When an excerpt scores < 0.5 against all candidate leaves (§4.A.1), the tree lacks the right leaf. This is a strong evolution signal — either a new leaf is needed, or an existing branch needs restructuring.

**Signal 3: Cross-source convergence.** When excerpts from 3+ different sources are placed at the same leaf and a cluster analysis reveals two or more distinct sub-groups (by topic embedding clustering with silhouette score > 0.4), the leaf likely covers multiple distinguishable sub-topics.

**Signal 4: One-excerpt-per-source violation.** Per §5.5, when a second excerpt from the same source is placed at the same leaf and the two excerpts cover different sub-topics, this suggests the leaf should split.

**Signal 5: Owner feedback.** The owner may explicitly request that a leaf be split, a branch be restructured, or a node be renamed. Owner signals bypass confidence thresholds and proceed directly to proposal generation.

**Evolution evaluation.** When a signal is detected, the engine evaluates whether evolution is warranted. Not every signal leads to a proposal — a single divergence signal from one excerpt is weak. The engine accumulates signals per leaf and evaluates when: (a) 3+ independent signals point to the same leaf, or (b) a single strong signal (unplaceable excerpt, owner request) targets the leaf.

Evaluation generates a structured proposal (§3.4). The proposal must pass all four §4.4 invariants:
- **Zero orphans.** Every existing excerpt at the affected leaf must have a valid placement in the proposed structure.
- **Sibling coherence.** No excerpt should plausibly belong to more than one proposed sibling. Tested by LLM: for each excerpt, the LLM classifies it into one of the proposed siblings. If any excerpt receives a split classification (two siblings score within 0.15 of each other), sibling coherence fails.
- **Excerpt non-interference.** No excerpt outside the evolution scope is affected.
- **Entry lifecycle propagation.** The proposal specifies which entries are invalidated and which new entries are queued.

Proposals that fail any invariant are never presented to the owner.

#### §4.A.6 — Coverage Gap Detection

Coverage gaps are computed per leaf, per branch, and per science. A gap is a structured object describing what is missing. Gap types:

**School gap.** A science that has schools (per SCIENCE.md) has a leaf where one or more schools have zero verified excerpts. Example: a Fiqh leaf has Hanafi, Shafi'i, and Hanbali excerpts but no Maliki excerpt. The gap records: `gap_type: school`, `missing_school`, `leaf_path`.

**Source diversity gap.** A leaf's excerpts all come from a single source (or fewer than 2 sources). Scholarly reliability requires corroboration. Gap records: `gap_type: source_diversity`, `current_source_count`, `leaf_path`.

**Temporal gap.** A leaf's excerpts all come from a narrow time period (all authors within 200 hijri years of each other) when the science spans a wider period. Important topics typically have positions from multiple centuries. Gap records: `gap_type: temporal`, `covered_period`, `science_total_period`, `leaf_path`.

**Evidence type gap.** A leaf has positions (opinions) but no supporting evidence (no Quran, hadith, or rational argument excerpts). Scholarly positions without evidence are incomplete. Gap records: `gap_type: evidence`, `missing_evidence_types`, `leaf_path`.

**Prerequisite gap.** A leaf has excerpts, but one of its hard prerequisite topics (from the prerequisite graph) has zero excerpts. The user cannot study this topic without first studying the prerequisite, but the prerequisite is empty. Gap records: `gap_type: prerequisite`, `missing_prerequisite_leaf`, `leaf_path`.

**Empty leaf.** A leaf exists in the tree but has zero excerpts. For trees with many empty leaves, this is expected during early library building. The gap is reported but at low severity. Gap records: `gap_type: empty`, `leaf_path`.

Gaps are recalculated after every placement, relocation, or evolution event. They are written to the coverage analytics output (§3.3) and available to the scholar interface for display and alerting.

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

#### §4.A.8 — Semantic Deduplication Detection

When multiple sources quote the same hadith, or paraphrase the same well-known definition, the taxonomy engine detects the semantic overlap and signals it to the synthesizing engine. This ensures entries present redundant content once (citing the strongest source) rather than repeating it.

Detection uses embedding similarity. After placement, the engine computes the embedding of the new excerpt's `primary_text` and compares it against all existing verified excerpts at the same leaf. If cosine similarity exceeds 0.85 with any existing excerpt, the pair is flagged as a duplicate cluster. Existing clusters are extended if the new excerpt is similar to any member.

Duplicate clusters are recorded in the coverage analytics (§3.3) and attached to the leaf's metadata. The synthesizing engine reads these clusters to avoid redundant presentation. The taxonomy engine does NOT merge or remove duplicate excerpts — they remain as independent placed excerpts. Deduplication is a synthesis-time concern, not a placement-time action, because different sources may add unique context even when the core content is similar.

#### §4.A.9 — Cross-Science Link Management

When the same concept appears as a leaf in multiple science trees (e.g., الاستثناء in both Nahw and Usul), the taxonomy engine records a cross-science link. Links are never merges — each science's leaf is independent with its own excerpts and entries. Links are metadata for the synthesizer and scholar interface.

Cross-science links are detected by two mechanisms:

(a) **Title matching.** When a new leaf is created (during tree construction or evolution), the engine checks all other science trees for leaves with semantically similar titles. LLM evaluation confirms whether the concepts are genuinely related or merely share a term.

(b) **Excerpt cross-reference.** When an excerpt at a leaf explicitly references a concept from another science (detected from `excerpt_topic` or `primary_text` content), and that concept has a leaf in the other science's tree, a link is proposed.

Links are written to `cross_science_links.json` (§3.2) and are available to the scholar interface for cross-science navigation (Scenario 3).

#### §4.A.10 — Terminology Synonym Management

Islamic scholarly terminology varies across schools and historical periods. The taxonomy engine maintains synonym mappings so that excerpts using variant terminology are placed at the correct leaf.

When the excerpting engine provides `terminology_variants` on an excerpt, the taxonomy engine checks whether any variant maps to a different leaf title than the proposed leaf. If a variant matches a leaf title, this confirms the placement. If a variant reveals a previously unknown synonym for an existing leaf, the synonym is added to the synonyms registry after LLM verification.

New synonyms are also detected during placement: when the LLM's topic-based search (§4.A.1, Stage 1b) identifies a leaf that uses a different term than the excerpt's `excerpt_topic`, but the concepts are the same, the terminology pair is recorded.

Synonyms are stored per science (§3.2) and used in placement candidate generation — when searching for matching leaves, all known synonyms for each leaf title are included in the search.

---

### §4.B — Transformative Capabilities

#### §4.B.1 — Topic Significance Scoring

Every leaf in every science tree receives a significance score that measures how important the topic is within the science. This score is NOT a simple count of excerpts — a leaf with 50 excerpts about a minor lexical curiosity is less significant than a leaf with 5 excerpts about a foundational principle. Significance is a structural property of the science, not a measure of library coverage.

Significance is computed from four signals:

(a) **Prerequisite dependency count.** How many other topics depend on this one (out-degree in the prerequisite graph). A topic that is a prerequisite for many others is foundational.

(b) **Cross-reference frequency.** How often excerpts at OTHER leaves reference this topic in their text (detected by the excerpting engine's `quoted_scholars` and implicit reference data, plus text search for the leaf's title and synonyms across all excerpts in the science).

(c) **Source coverage breadth.** How many distinct authoritative works dedicate substantial space to this topic (measured by the number of sources that contribute 2+ excerpts to this leaf). Topics that every major work addresses are significant.

(d) **LLM scholarly assessment.** The LLM is prompted: "Within the science of {science_name}, how significant is the topic of {leaf_title}? Consider: is this a foundational concept, a derived application, an edge case, or a minor detail? Rate 0.0–1.0 with reasoning." This assessment uses the LLM's broad knowledge of the science, not just library contents, to prevent corpus bias.

The four signals are combined with weights: prerequisite dependency (0.3), cross-reference frequency (0.25), source breadth (0.2), LLM assessment (0.25). The resulting score is normalized to 0.0–1.0 per science.

**Why this is transformative.** No existing Islamic scholarly tool quantifies topic significance within a science. Classical scholars implicitly know which topics are foundational — but this knowledge is tacit and takes years of study to acquire. Significance scoring makes it explicit and queryable: "Show me the 20 most significant topics in Nahw that I haven't studied." The scholar interface uses significance scores for study path optimization — ensuring the student builds foundational knowledge before derived applications. The synthesizer uses significance to calibrate entry depth — more significant topics get more thorough entries.

**Technical approach.** Prerequisite graph analysis uses NetworkX (DAG traversal, out-degree computation). Cross-reference frequency uses full-text search over the excerpt corpus (CAMeL Tools for Arabic text normalization, then exact and fuzzy matching). Source breadth is a simple database query. LLM assessment uses Instructor for structured output (score + reasoning).

[NOT YET IMPLEMENTED] — Full specification provided; no code exists. Depends on: prerequisite graph (§4.A.3), placed excerpt corpus, scholar authority registry, Instructor library.

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

#### §4.B.3 — Corpus-Driven Tree Construction

Instead of building science trees purely from manual scholarly research (§4.A.3), the taxonomy engine can generate draft trees from computational analysis of multiple authoritative works' structural organization. This capability accelerates tree construction for sciences with many available sources.

The process:

(a) **Structural extraction.** For each authoritative work in the science (minimum 5 works spanning different periods and schools), extract the table of contents: chapter titles, section titles, sub-section titles, and their hierarchical relationships. This data comes from the normalization engine's division tree output.

(b) **Cross-work alignment.** The LLM aligns TOC entries across works, identifying: which topics appear in all works (consensus structure), which topics appear in some works but not others (disputed structure), which topics are organized differently in different works (structural disagreements), and which works introduce unique topics not found elsewhere.

(c) **Consensus tree synthesis.** From the alignment, the engine generates a draft tree that represents the consensus structure. Topics present in ≥60% of consulted works form the core structure. Topics present in <60% but ≥2 works are included as optional branches. Unique-to-one-work topics are noted in the research report but not included in the draft. The threshold is configurable.

(d) **Ordering inference.** The pedagogical sequence is inferred from the ordering of topics in the consulted works. Where works agree on ordering, that ordering is adopted. Where they disagree, the most common ordering is proposed with the alternatives documented.

**Why this is transformative.** Building a science tree for a major Islamic discipline (Fiqh has thousands of topics across multiple organizational traditions) is a massive research effort. Corpus-driven construction reduces a weeks-long manual process to hours, producing a draft that reflects how scholars actually organize the discipline rather than an ad-hoc external classification. The draft still requires human validation (§4.A.3 Validation phase) and owner approval (§4.A.3 Commitment phase) — but it starts from a computationally derived scholarly consensus rather than from scratch.

**Technical approach.** TOC extraction from normalization engine's division trees. Cross-work alignment uses LLM analysis with Instructor for structured output. Sentence-transformers for title embedding similarity during alignment. NetworkX for tree structure construction and validation.

[NOT YET IMPLEMENTED] — Full specification provided; no code exists. Depends on: normalization engine's division tree output, source engine's work registry, LLM with Arabic scholarly knowledge, Instructor library.

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

Consensus is NOT used for: tree construction (which is a research task requiring coherent vision, not averaging), evolution proposal generation (same reason), coverage analytics (deterministic computation), or high-confidence placements (score ≥ 0.8, where single-model accuracy is sufficient).

**Consensus configuration.** Two models from different providers (e.g., Claude and GPT). Agreement threshold: both models must select the same leaf within the tree. If they select different leaves, the placement is escalated to the human gate with both models' selections presented.

**Rationale for limited consensus.** Unlike excerpting (where self-containment judgment has profound quality implications), most taxonomy decisions are either clearly correct (high confidence) or genuinely ambiguous (requiring human judgment). The middle band where consensus adds value — where one model is right and the other is wrong, and the right answer can be identified by agreement — is narrow. For this reason, consensus is applied selectively rather than universally.

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
- **Evolution sensitivity.** Some sciences have stable, well-established structures (e.g., Tajwid). Others are actively debated (e.g., boundaries between Usul al-Fiqh sub-topics). Evolution sensitivity controls how readily the engine proposes evolution.
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
