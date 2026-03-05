# Synthesizing Engine — محرك التوليف — Specification

## 1. Purpose and Scope

The synthesizing engine generates encyclopedic entries from placed excerpts at taxonomy leaves. An entry is the primary knowledge product of KR (D-005) — the artifact Rayane reads, memorizes, teaches from, and cites. The quality of entries directly determines the quality of Rayane's scholarship. An error in an entry is an error in Rayane's understanding (D-018).

The synthesizing engine has three responsibilities:

**Responsibility 1: Entry generation.** Given a set of placed, verified excerpts at a taxonomy leaf (or school-group within a leaf), the engine produces a complete encyclopedic article with two structurally distinct layers: a factual layer traceable to specific excerpts, and an analytical layer providing the engine's scholarly contribution — contextualization, connections, and narrative that no single excerpt contains. The engine uses three input sources: excerpt content, upstream metadata chains (D-023), and its own LLM research capability.

**Responsibility 2: Entry lifecycle management.** The engine detects when entries become stale (their underlying excerpt collection has changed), prioritizes regeneration, tracks entry versions, and produces change summaries so the scholar interface can inform Rayane what changed and why.

**Responsibility 3: Scholarly integrity enforcement.** The engine is the final quality gate before knowledge enters Rayane's understanding. It must distinguish library-grounded claims from LLM-contributed context (the traceability boundary), detect contradictions between excerpts, prevent library composition bias from distorting the scholarly landscape, and ensure every factual claim carries a verifiable physical citation.

**What is NOT this engine's responsibility.** The synthesizing engine does not extract excerpts (excerpting engine), place excerpts at leaves (taxonomy engine), present entries to the user (scholar interface), or maintain the user model (shared/user_model). It does not decide what constitutes a "science" or manage taxonomy trees. It does not perform excerpt-level corrections — those flow through the excerpting and taxonomy engines. It reads the library's stored placed excerpts; it does not participate in the real-time processing pipeline.

**Phase classification.** Phase 2 (source-agnostic, below the normalization boundary). The synthesizing engine operates on placed excerpts that carry no trace of their original source format. It is architecturally distinct from the other Phase 2 engines — it reads the library's stored excerpts, not the pipeline's intermediate processing artifacts.

**User scenarios served.** Scenario 1 (Day 1) — the engine generates entries for initial study. Scenario 2 (Active Study) — entries are regenerated when new sources add excerpts. Scenario 3 (Cross-Science) — the engine can generate cross-science comparative entries from excerpts at linked leaves. Scenario 4 (Scholarly Production) — the engine provides the factual base from which Rayane writes. Scenario 7 (Show Me the Whole Science) — entries populate the science map with content. Scenario 8 (KR Gets It Wrong) — corrections trigger regeneration with owner constraints.

---

## 2. Input Contract

The synthesizing engine receives input from two sources: the library's placed excerpt collection (its primary input), and entry lifecycle signals (staleness triggers, regeneration requests, owner corrections).

### 2.1 Placed Excerpts

The engine reads placed excerpts from `library/sciences/{science_id}/content/{leaf_path}/excerpts/`. Each placed excerpt conforms to the placed_excerpt schema defined in the taxonomy engine SPEC §3.1. The synthesizing engine validates:

**Required fields — abort generation on absence.** `excerpt_id`, `source_id`, `primary_text` (non-empty), `confirmed_leaf` (must match the leaf being synthesized), `lifecycle_stage` (must be `placed`), `verified_flagged_status` (determines whether excerpt enters the factual or critical analysis layer).

**Expected fields — degraded synthesis on absence.** `primary_author_id` (if absent, the entry cannot attribute the position to a specific scholar — the engine proceeds but marks the attribution as "unknown author"), `school` (if absent for a science that has schools, the entry notes the gap), `content_types` (if absent, the engine cannot tag the excerpt's role), `evidence_refs` (if absent, the entry cannot describe the evidence base), `self_containment_score` (if absent, all excerpts treated as equally self-contained), `placement_confidence` (if absent, all excerpts treated as equally well-placed), `processing_metadata` (if absent, no confidence-aware synthesis is possible).

**Metadata resolution.** For each excerpt, the engine resolves the full metadata chain by reference: `source_id` → source metadata record (author biography, work classification, genre, edition, trust tier, text fidelity), `primary_author_id` → scholar authority record (death dates, school affiliations, teachers, students, scholarly standing), `passage_id` → passage metadata (physical page references, division path). The engine does NOT duplicate this metadata — it reads it from the library's registries at generation time. If any registry lookup fails, the engine logs a warning and proceeds with degraded metadata (the entry will lack biographical/contextual depth for that excerpt but will still include the excerpt's factual content).

### 2.2 Taxonomy Context

For each leaf being synthesized, the engine reads:

- **Tree structure.** The science tree YAML, to determine: parent branch (for situating the topic), sibling leaves (for "what to read next" recommendations), prerequisite edges (for prerequisites section), narrative ordering (for connecting the topic to its logical neighbors), cross-science links (for cross-science references).
- **Coverage analytics.** The leaf's coverage record from `library/sciences/{science_id}/coverage.json`, including: school coverage, temporal span, source diversity, gaps, duplicate clusters, significance score, difficulty estimate.
- **SCIENCE.md configuration.** The Level 3 per-science documentation, which specifies: whether schools exist and which ones, entry format preferences, scholarly conventions, and any science-specific synthesis rules.

### 2.3 Entry Lifecycle Signals

**Staleness notifications.** When a placement, relocation, reclassification, or metadata correction occurs at a leaf, the affected entry is marked stale. The signal contains: `leaf_path`, `science_id`, `school_group` (if applicable), `trigger_type` (one of: `new_excerpt`, `excerpt_removed`, `excerpt_relocated_in`, `excerpt_relocated_out`, `metadata_correction`, `reclassification`), `trigger_excerpt_id`, `timestamp`.

**Regeneration requests.** Explicit requests to regenerate an entry, from: the scholar interface (user opens a stale entry), the batch processor (background regeneration), or the owner (manual regeneration after correction). Each request contains: `leaf_path`, `science_id`, `school_group` (if applicable), `priority` (one of: `user_initiated`, `background`, `batch`), `owner_constraints` (array of owner notes that must be respected during regeneration — these survive across regenerations and prevent recurring errors per Scenario 8).

**Owner corrections.** When the owner identifies an error in an entry (Scenario 8), the correction arrives as: `entry_id`, `correction_type` (one of: `factual_error`, `attribution_error`, `missing_position`, `misrepresentation`, `structural_feedback`), `description` (owner's explanation), `permanent_constraint` (boolean — if true, this correction becomes a permanent generation constraint at this leaf, surviving all future regenerations).

---

## 3. Output Contract

The synthesizing engine produces two categories of output: entries (the primary knowledge product) and lifecycle artifacts (version history, change summaries).

### 3.1 Entries

Each entry is written to `library/sciences/{science_id}/entries/{leaf_slug}/{entry_id}.json`, conforming to the entry schema. The schema defined in `schemas/entry.json` is superseded by this SPEC's definition — the schema file will be updated to match.

An entry contains:

- `entry_id`: string, format `ent_{science_id}_{leaf_slug}_{school_group_or_all}_v{version}`. Globally unique.
- `leaf_path`: string. Full path from root to the leaf.
- `science_id`: string.
- `school_group`: string or null. Which school this entry covers. Null if the science has no schools or schools are irrelevant to this leaf's topic.
- `generated_utc`: ISO datetime.
- `generator_config`: object. Model identifier, prompt version hash, SCIENCE.md version hash. Enables exact reproduction and regression testing.
- `source_excerpt_ids`: array of strings. Every placed, verified excerpt used in the factual layer. Minimum 1.
- `content`: object containing the entry's text layers (see §3.2).
- `citations`: array of citation objects (see §3.3). Every factual claim maps to one or more citations.
- `staleness_hash`: string. SHA-256 of the sorted source_excerpt_ids concatenated with a hash of their content. Enables staleness detection without re-reading all excerpts.
- `version`: integer ≥ 1. Incremented on each regeneration.
- `previous_version_id`: string or null. Links to the previous version for diff tracking.
- `owner_constraints`: array of strings. Permanent owner corrections applied during generation. These are inherited from the leaf's constraint store and recorded in the entry for auditability.
- `is_stale`: boolean. False at generation time; set to true by staleness detection.
- `taxonomy_version`: string. The active tree version at generation time.
- `generation_metadata`: object. `duration_seconds`, `total_excerpts_used`, `verified_excerpts`, `flagged_excerpts_referenced`, `unique_authors`, `unique_sources`, `temporal_span_hijri` (earliest to latest author death date), `confidence_summary` (distribution of upstream confidence scores), `library_grounded_claim_count`, `llm_contributed_claim_count`, `deduplication_clusters_found`.

### 3.2 Entry Content Structure

The `content` object has a defined structure that serves the owner's study needs (D-021) while maintaining the factual/analytical boundary (§6.1, §6.4):

```
content: {
  prerequisites: string,
  topic_situation: string,
  core_treatment: string,
  scholarly_positions: [
    {
      position_id: string,
      position_summary: string,
      holders: [{ scholar_id, name, death_hijri, school }],
      evidence_types: [string],
      evidence_refs: [string],
      mu_tamad_in_school: string or null,
      is_consensus: boolean,
      confidence: float
    }
  ],
  edge_cases: string or null,
  khilaf_analysis: string or null,
  temporal_narrative: string or null,
  what_next: string,
  analytical_layer: string or null,
  critical_analysis: string or null
}
```

**Language.** All entry text is in Arabic (D-032). Transliterated terms may appear parenthetically for disambiguation.

**Guarantees about entry content:**

- **Factual completeness.** Every verified excerpt at the leaf (or school-group) is represented in the entry. No excerpt is silently omitted. If an excerpt is excluded (e.g., because it is a semantic duplicate of another), the exclusion is logged in `generation_metadata.deduplication_clusters_found`.
- **Attribution accuracy.** Every scholarly position is attributed to the correct scholar(s) with correct school affiliation, death date, and work reference. Misattribution is a critical error (§6.4).
- **Traceability.** Every factual claim in `core_treatment`, `scholarly_positions`, and `edge_cases` maps to at least one entry in `citations`. The `analytical_layer` and `critical_analysis` may contain LLM-contributed context that is not citation-backed — this is by design, but is structurally separated from the factual content.
- **School isolation.** Where schools exist, each school-group entry is generated exclusively from that school's verified excerpts. No cross-school mixing in the factual layer. The analytical layer may reference other schools' positions for comparative context, clearly marked as such.

### 3.3 Citation Format

Each citation links a claim in the entry text to its source:

```
{
  citation_id: string,
  claim_text: string,
  claim_location: string,
  excerpt_ids: [string],
  source_citation: {
    source_title: string,
    author_name: string,
    edition: string,
    volume: integer or null,
    page_start: integer or null,
    page_end: integer or null
  },
  grounding_type: string   // "library_excerpt" | "library_metadata" | "llm_research"
}
```

The `grounding_type` field enforces the traceability boundary: claims in `core_treatment` and `scholarly_positions` must have `grounding_type: "library_excerpt"` or `"library_metadata"`. Claims in `analytical_layer` may have `grounding_type: "llm_research"`, signaling to the reader and the scholar interface that this claim comes from the engine's training knowledge, not from a specific excerpt.

### 3.4 Entry Version History

When an entry is regenerated, the previous version is moved to `library/sciences/{science_id}/entries/{leaf_slug}/history/{entry_id}.json`. A change summary is generated:

```
{
  change_summary_id: string,
  old_version: integer,
  new_version: integer,
  trigger: string,
  positions_added: [string],
  positions_removed: [string],
  positions_modified: [string],
  new_excerpts_incorporated: [string],
  structural_changes: string
}
```

The scholar interface uses change summaries to inform Rayane: "This entry was updated since you last studied it. Key changes: [summary]."

**Metadata pass-through (D-023).** The synthesizing engine is the terminal consumer of the metadata chain. It does not produce output consumed by downstream engines. However, entries are consumed by the scholar interface, and the entry's citation structure preserves the full provenance chain: each citation traces through excerpt → passage → normalized package → frozen source.

---

## 4. Processing Specification

### §4.A — Core Processing

#### §4.A.1 — Generation Pipeline Overview

Entry generation follows a five-phase pipeline. Each phase has distinct inputs, outputs, and failure modes. Phases are sequential; a failure in any phase produces a diagnostic entry (§4.A.8) rather than a silently degraded entry.

**Phase 1: Collection and Preparation.** Gather all placed excerpts for the target leaf/school-group. Resolve full metadata chains. Detect and cluster semantic duplicates. Compute the excerpt inventory.

**Phase 2: Scholarly Analysis.** Identify distinct scholarly positions. Classify disagreement types. Perform tahrir al-mas'ala. Check for intra-author contradictions. Detect abrogated content. Determine mu'tamad where applicable.

**Phase 3: Narrative Construction.** Build the entry's content — factual layer first (excerpt-grounded), then analytical layer (engine-contributed). Generate citations inline.

**Phase 4: Integrity Verification.** Verify traceability, school isolation, verified/flagged separation, owner constraint compliance, and grounding type consistency.

**Phase 5: Finalization.** Compute staleness hash. Record version metadata. Write entry. Generate change summary if replacing a previous version.

#### §4.A.2 — Phase 1: Collection and Preparation

The engine reads all placed excerpts at the target leaf. For sciences with schools (§6.2), it partitions excerpts by school-group and generates one entry per school-group. For sciences without schools, all excerpts form a single entry.

**Excerpt partitioning rules:**
- `verified_flagged_status == "verified"` → enters the factual layer's excerpt set.
- `verified_flagged_status == "flagged"` → enters the critical analysis excerpt set. Never mixed with verified excerpts in the factual layer.
- If a science has schools and an excerpt's `school` field is null or `"unknown"`, the excerpt is placed in an unattributed pool. The engine attempts to infer school affiliation from the scholar authority record. If inference succeeds with confidence ≥ 0.7, the excerpt joins that school-group with an annotation noting the inference. If inference fails, the excerpt is noted in generation_metadata as unattributed and excluded from per-school entries.

**Metadata chain resolution.** For each excerpt, the engine resolves:
1. Source metadata via `source_id` → `library/registries/sources.json`. Extracts: work title, genre, source authority level, trust tier, text fidelity.
2. Scholar authority via `primary_author_id` → `library/registries/scholars.json`. Extracts: full name, death dates (hijri + CE), school affiliations, teachers, students, scholarly standing.
3. Quoted scholars via `quoted_scholars` → scholar authority records. Enables tracking who cites whom.
4. Passage metadata via `passage_id`. Extracts: physical page references, division path.
5. Work relationships via source metadata → work registry. Extracts: genre chain, relationships to other works.

If any lookup fails (missing entry, corrupted data), the engine logs `SYNTH_METADATA_RESOLUTION_FAILED` with the excerpt_id and the missing reference. The excerpt is still used for its textual content but lacks metadata-driven contextualization.

**Semantic deduplication.** The engine receives duplicate cluster information from the taxonomy engine's coverage analytics. For each cluster, the engine selects a representative excerpt — preferring: (1) highest source-authority-level (primary > reference > compilation), (2) highest text-fidelity, (3) earliest author (chronological priority). Non-representative excerpts are recorded in generation_metadata but not individually cited. The representative excerpt's citation notes: "also found in [source_2], [source_3]."

**Confidence-weighted excerpt inventory.** If the mean upstream confidence across all excerpts is below 0.5, the engine prepends a quality caveat to the entry: "This entry is based on excerpts with lower-than-normal extraction confidence. Claims should be verified against primary sources."

#### §4.A.3 — Phase 2: Scholarly Analysis

This phase produces a structured analysis object consumed by Phase 3.

**Step 1: Position identification.** The LLM receives all verified excerpts with metadata (author, date, school, content type) and identifies distinct scholarly positions. A position is a specific answer to the leaf's mas'ala. The prompt instructs the LLM to distinguish: same position (different wording), different positions (same question), and different questions entirely. The output is a structured list of positions with: summary (Arabic), holders (scholar IDs + names + dates + schools), evidence types, and supporting excerpt IDs.

**Step 2: Khilaf classification.** For each pair of distinct positions on the same question, the LLM classifies the disagreement as: `lafzi` (verbal — different words, same meaning), `haqiqi` (substantive — genuinely different positions), `mu'tabar` (respected — valid evidence on each side), or `shadh` (aberrant — held by very few, rejected by the overwhelming majority). Classification is per position-pair.

**Step 3: Tahrir al-mas'ala.** The engine verifies all scholars are answering the same question. If excerpts address distinguishably different sub-questions: (a) positions are grouped by question, (b) each group is addressed separately in the entry, (c) if the distinction warrants a leaf split, the engine emits a `TAX_EVOLUTION_SIGNAL` with type `leaf_split_suggested`.

**Step 4: Intra-author contradiction detection.** For each author with multiple excerpts at the leaf, the engine compares positions. If contradictions are found: (a) check whether excerpts come from different works at different times — if so, the later position supersedes the earlier (تراجع), (b) check whether one is general and the other specific — no real contradiction, (c) if genuine and unexplained, flag in the entry with both excerpts cited.

**Step 5: Mu'tamad identification.** For sciences with schools: (a) check for explicit mu'tamad statements in excerpts, (b) check for authoritative reference works identifying the mu'tamad, (c) if not found in library, check LLM knowledge (flagged as `grounding_type: "llm_research"`), (d) if undetermined, state this explicitly in the entry.

**Step 6: Abrogation check.** For fiqh and other applicable sciences (per SCIENCE.md): check whether any cited evidence is abrogated. Uses evidence reference metadata and LLM knowledge of known abrogation instances. Abrogated content is clearly marked: "This ruling is based on [evidence], which scholars recognize as abrogated by [later evidence]."

**Step 7: Library composition bias assessment.** Examine the excerpt inventory for: school imbalance, source concentration, temporal skew. Bias signals surface as caveats in the analytical layer.

#### §4.A.4 — Phase 3: Narrative Construction

##### §4.A.4.1 — Factual Layer Construction

The factual layer is excerpt-grounded. Every claim is traceable. Construction follows a structured template adapted per science (SCIENCE.md).

**Core treatment generation.** The LLM receives the Phase 2 analysis, all verified excerpts with metadata, the content template, owner constraints, and explicit instruction to generate inline citation markers `[cit:N]` for each claim. Structured output enforcement via Instructor/Pydantic ensures schema conformance.

**Scholarly positions array.** Generated in parallel with the prose core_treatment. Each element corresponds to a Phase 2 position. Enables the scholar interface to present positions comparatively without re-parsing prose.

**Direct quotation policy.** Canonical definitions meant for memorization are quoted verbatim with explicit attribution. Explanatory content is paraphrased with citation. The decision is based on: canonical formula/definition → quote; discussion/explanation → paraphrase.

**Physical citation assembly.** From the metadata chain: excerpt → passage → source. Citation includes: source title, author name, tahqiq editor, publisher, volume, page numbers. If page numbers are unavailable, the citation notes "page reference unavailable."

##### §4.A.4.2 — Analytical Layer Construction

The analytical layer is the engine's intellectual contribution. It draws from: (1) cross-excerpt analysis (connections between positions), (2) metadata-driven context (teacher-student chains, chronological ordering — `grounding_type: "library_metadata"`), (3) LLM research (historical context, institutional dynamics — `grounding_type: "llm_research"`).

**Constraints on the analytical layer:** Must not contradict the factual layer. Must not present LLM-sourced claims as excerpt-backed. Must be structurally distinguishable. Must not add scholarly positions — positions come only from excerpts.

**Temporal narrative construction.** Using author death dates from scholar authority records, the engine arranges positions chronologically and constructs a narrative showing scholarly evolution. This temporal dimension is the engine's most distinctive contribution.

**Teacher-student chain discovery.** The engine traverses the scholar authority graph to find chains connecting scholars at this leaf. Found chains are woven into the analytical narrative. Chains from LLM knowledge are flagged as `grounding_type: "llm_research"`.

**Situating the topic.** The engine uses taxonomy context (parent branch, siblings, prerequisites, cross-science links) to generate `topic_situation` and `what_next`, fulfilling D-021 (no isolated topics).

**Prerequisite generation.** From taxonomy prerequisite edges, translated into readable Arabic.

#### §4.A.5 — Phase 4: Integrity Verification

After content generation, automated checks either block the entry (critical failures) or annotate warnings.

**Check 1: Citation completeness.** Every sentence in `core_treatment`, every element in `scholarly_positions`, and every sentence in `edge_cases` must have at least one citation. Uncited factual claims: critical failure → retry.

**Check 2: Citation validity.** Every `excerpt_id` in citations must exist in the placed excerpt collection. Invalid citation: critical failure.

**Check 3: School isolation.** For per-school entries: no excerpt from another school in `source_excerpt_ids`. Violation: critical failure.

**Check 4: Verified/flagged separation.** No flagged excerpt in the factual layer's citations. Violation: critical failure.

**Check 5: Owner constraint compliance.** LLM checks each owner constraint against the entry. Violation: retry with constraint more prominently weighted.

**Check 6: Grounding type consistency.** No `"llm_research"` claims in `core_treatment` or `scholarly_positions`. Violation: critical failure.

**Check 7: Temporal consistency.** Author death dates match scholar authority records. Mismatch: non-critical warning.

**Check 8: Content quality heuristics.** Non-critical: entry length vs excerpt count, position count matches Phase 2, all excerpts cited.

When critical checks fail, the engine retries (up to 2 retries) with the failure highlighted in the prompt. If all retries fail, a diagnostic entry is produced (§4.A.8).

#### §4.A.6 — Phase 5: Finalization

**Staleness hash.** SHA-256 of (sorted excerpt_ids joined by `|`) + `|` + SHA-256 of (concatenated excerpt primary_texts in sorted ID order).

**Version management.** First entry: version 1, null previous. Replacement: version incremented, old entry moved to history, change summary generated by comparing `scholarly_positions` arrays.

**Write to library.** Atomic write (temp file → rename).

#### §4.A.7 — Staleness Detection and Regeneration Scheduling

**Staleness detection.** On each placement, relocation, reclassification, or correction, the taxonomy engine emits a staleness signal. The synthesizing engine maintains a queue: `library/synthesis_queue/stale_entries.jsonl`.

**Priority ordering:**
1. `user_initiated` — owner opened a stale entry. Regenerated immediately (synchronous).
2. `study_focus` — leaf in owner's current curriculum (user model). Next background cycle.
3. `background` — all others. Batch during idle time.

Within priority levels: more triggering excerpts → higher; longer staleness → higher.

**Batch regeneration.** Large source processing triggers batch mode: all affected leaves queued, study-focus leaves first, remaining in batches of 20, progress tracked in `batch_status.json`, owner not blocked (stale-marked entries remain readable).

**Regeneration guarantee.** Always from scratch — full excerpt collection re-read, complete new entry. No incremental updates.

#### §4.A.8 — Diagnostic Entries

When generation fails after all retries, the engine produces a diagnostic entry:
- `is_diagnostic: true` in generation_metadata.
- Reduced `core_treatment` listing available excerpts and attributions without synthesis.
- `diagnostic_reason` explaining the failure.
- Usable but flagged; scholar interface displays with a warning.

Diagnostic entries prevent permanent gaps when synthesis encounters unhandled edge cases.

#### §4.A.9 — Per-Science Customization Hooks

SCIENCE.md (Level 3) specifies per-science configuration. The engine reads it at generation time.

**Hook 1: School handling.** `has_schools`, `school_list`, `school_entry_cardinality` ("per_school" for fiqh, "unified_with_attribution" for nahw).

**Hook 2: Evidence hierarchy.** Ordered evidence types by weight. Fiqh: quran, hadith, ijma, qiyas... Nahw: samā', qiyas, ijma_al_nahwiyyin.

**Hook 3: Mu'tamad applicability.** `has_mu_tamad: boolean`.

**Hook 4: Abrogation applicability.** `abrogation_check: boolean`.

**Hook 5: Entry format preferences.** Template reference for section ordering per science.

**Hook 6: Khilaf relevance.** `khilaf_classification: boolean`. False for tajwid.

#### §4.A.10 — Cross-Science Entry Generation

For cross-science analyses (Scenario 3), the engine generates special entries drawing from excerpts at multiple leaves across science trees (linked via `cross_science_links.json`). Cross-science entries:
- Do NOT replace per-science entries — stored at `library/cross_science/{link_id}/entry.json`.
- Factual layer represents positions from all linked sciences with clear attribution to science and leaf of origin.
- Analytical layer focuses on the connection: how a grammatical rule affects a legal interpretation.
- Citations reference multiple science trees.
- Generated on demand, not automatically.

#### §4.A.11 — Ellipsis Expansion and Level Adaptation

Arabic scholarly texts omit words understood from context. The engine expands based on the owner's level (from user model):

**Beginner.** Maximum expansion: implicit concepts made explicit, technical terms defined on first use.

**Intermediate.** Moderate expansion: core concepts assumed, connections spelled out. Terms used without definition.

**Advanced.** Minimal expansion: terse classical style preserved, original phrasing preferred for scholarly significance.

Default (no level data): intermediate. Level affects the analytical layer and edge_cases more than the factual layer.

---

### §4.B — Transformative Capabilities

#### §4.B.1 — Scholarly Consensus Mapping

**Capability:** For each position at a leaf, the engine automatically classifies its strength on a scholarly consensus spectrum: absolute consensus (إجماع قطعي), near-consensus (إجماع ظني / قول الجمهور), strong majority, weak majority, evenly disputed, and minority/aberrant. This classification synthesizes three signals: (a) the explicit claims in excerpts ("أجمع العلماء على..." — "scholars have consensus on..."), (b) the distribution of positions across sources and schools in the library (library evidence), and (c) the engine's LLM knowledge of the broader scholarly tradition beyond the library (LLM research, flagged accordingly).

**Why this is transformative.** No existing Islamic studies tool automatically maps consensus strength. A student reading classical texts encounters scattered consensus claims — but no tool integrates these claims across sources, validates them against the actual distribution of positions, or distinguishes genuine consensus from overclaimed consensus. KR can answer: "Is this really an ijma, or did one scholar claim consensus while others disagreed?"

**Input:** The `scholarly_positions` array from Phase 2 analysis, the library's full coverage data for the leaf (which schools are represented, how many sources hold each position), and the engine's LLM knowledge.

**Output:** Each position in the `scholarly_positions` array receives a `consensus_strength` field with: the classification label, the evidence for the classification (which excerpts claim consensus, what the library distribution shows), and a confidence score. The entry's analytical layer includes a consensus narrative: "This position is held by consensus according to [excerpt sources], and the library confirms no dissenting source on record. However, [if the library has limited coverage of some schools], the consensus claim cannot be verified for [school] due to limited library coverage."

**Preventing overclaimed consensus.** When an excerpt claims ijma but the library contains at least one excerpt from a recognized scholar holding a different position, the engine flags the inconsistency: "Source X claims consensus, but Scholar Y (d. NNN AH) holds a different position in [Work Z]. The consensus claim may be qualified or contested." This detection uses NLI-style comparison: the consensus claim is the premise, the dissenting position is the hypothesis, and the engine checks for contradiction.

**Technical approach.** Position identification uses the structured analysis from Phase 2. Consensus classification uses a multi-source approach: (1) regex-based detection of consensus keywords in excerpt text (أجمع، إجماع، اتفق العلماء، لا خلاف), (2) LLM classification of the strength of the consensus claim, (3) cross-checking against the library's actual position distribution. The hybrid NLI + LLM approach for contradiction detection follows the ContraDoc/ContraGen architecture: semantic similarity filtering (embedding-based) to find potentially conflicting excerpts, followed by LLM-based contradiction classification.

[NOT YET IMPLEMENTED] — Full specification provided; no code exists. Depends on: excerpting engine's evidence type tagging, taxonomy engine's coverage analytics, scholar authority model.

#### §4.B.2 — Intellectual Genealogy Reconstruction

**Capability:** The engine automatically reconstructs and visualizes the intellectual genealogy of positions at a leaf — tracing how ideas moved through teacher-student chains across centuries. Given scholars who hold positions at a leaf, the engine traverses the scholar authority model's teacher-student graph to discover chains connecting them, then narrativizes these chains in the entry.

**Why this is transformative.** Understanding WHY scholars hold certain positions requires knowing their intellectual lineage. "Ibn al-Sarraj refined Sibawayhi's definition" is more meaningful when you know al-Sarraj was a fourth-generation student of Sibawayhi through a specific chain. No existing tool reconstructs these chains automatically or integrates them into entry narratives. This makes the transmission of ideas — one of the most important aspects of Islamic scholarship — visible for the first time.

**Input:** Scholar IDs from excerpts at the leaf + the scholar authority model's teacher-student graph + the engine's LLM knowledge of well-known scholarly genealogies.

**Processing:**
1. For each pair of scholars at the leaf, the engine performs a breadth-first search in the teacher-student graph to find shortest connecting paths (up to 6 hops — beyond that, the connection is too indirect to narrativize meaningfully).
2. If no path exists in the library's graph, the engine queries its LLM knowledge for well-known chains (e.g., Sibawayhi → al-Akhfash → al-Jarmi → al-Mubarrad is a canonical Basran nahw chain). LLM-sourced chain links are flagged as `grounding_type: "llm_research"` and carry lower confidence.
3. Discovered chains are evaluated for narrative relevance: does the chain explain a transmission of ideas relevant to this leaf's topic? A chain connecting two scholars who hold the same position suggests intellectual inheritance. A chain where the student DISAGREES with the teacher suggests intellectual independence or school evolution.
4. Relevant chains are integrated into the `temporal_narrative` section of the entry.

**Output:** A `genealogy_chains` array in the entry's generation_metadata, each element containing: `chain` (ordered list of scholar IDs + names + death dates), `chain_source` ("library_graph" or "llm_research"), `narrative_relevance` (a sentence explaining why this chain matters for this topic), `position_relationship` ("inherited" — student holds teacher's position, "diverged" — student holds different position, "refined" — student modified teacher's position).

**Technical approach.** Graph traversal uses NetworkX (already cataloged in RESOURCES.md for the taxonomy engine). The scholar authority model's teacher-student links are loaded as a directed graph. BFS finds shortest paths between scholar pairs. LLM-sourced chains are validated by checking that each scholar in the chain existed in the correct chronological order (death dates must be monotonically increasing along the chain — a student cannot pre-date their teacher). Invalid chains are discarded with a warning.

[NOT YET IMPLEMENTED] — Full specification provided; no code exists. Depends on: scholar authority model with teacher-student links (source engine §4.A.5), NetworkX graph library.

#### §4.B.3 — Predictive Gap Synthesis

**Capability:** When the engine detects that a leaf has significant coverage gaps (e.g., no Maliki position, no sources from before the 5th century AH), it generates a provisional analytical note describing what the missing perspective LIKELY contains, based on the engine's LLM knowledge of the broader scholarly tradition. This note is structurally separated from the factual layer, clearly marked as gap-filling inference, and includes specific source recommendations that would fill the gap.

**Why this is transformative.** Coverage gaps are not just data gaps — they are gaps in Rayane's knowledge (D-018). Currently, when a school is missing from a leaf, the entry simply omits that perspective. But a scholar studying a topic NEEDS to know that other positions exist even if the library doesn't contain them yet. This capability makes the invisible visible: "The library has no Maliki source on this topic, but the Maliki position is known to be [X] based on [reasoning]. Acquiring [specific work] would fill this gap."

**Input:** Coverage gaps from the taxonomy engine's analytics (§4.A.6 gap descriptors), the engine's LLM knowledge, and the library's work relationship graph (which works are known but not acquired).

**Processing:**
1. For each gap of type `school`, `temporal`, or `source_diversity`: the engine queries its LLM knowledge for the likely content of the missing perspective.
2. The query is specific: "For the topic [leaf topic] in [science], what is the [school] position? Which scholars are known to hold it? In which works is it documented?"
3. The response is formatted as a provisional note, clearly labeled: "The following is the synthesizer's assessment based on its training knowledge, not on library excerpts. It should be verified against primary sources."
4. If the work relationship graph contains placeholder records for unacquired works that would fill the gap (D-027), the engine includes these as acquisition recommendations: "Acquiring [Work X] by [Author Y], which is in the library's wish list, would provide primary source coverage for this gap."

**Output:** A `gap_notes` array in the entry, each containing: `gap_type`, `gap_description`, `provisional_content` (the engine's inference about the missing perspective), `confidence`, `grounding_type: "llm_research"`, `recommended_acquisitions` (work IDs from the work registry's placeholder records).

**Constraints:** Gap notes never appear in the factual layer. They are presented by the scholar interface as "What KR thinks you're missing" — a distinct section from the verified scholarly content.

[NOT YET IMPLEMENTED] — Full specification provided; no code exists. Depends on: taxonomy engine coverage gap detection (§4.A.6), work relationship graph with placeholder records (D-027).

#### §4.B.4 — Entry Quality Self-Assessment

**Capability:** After generating an entry, the engine produces a structured self-assessment scoring the entry's quality across multiple dimensions, enabling the scholar interface to present quality indicators and enabling systematic quality improvement over time.

**Why this is transformative.** Most AI-generated content has no quality signal — the user must judge it themselves. For scholarly content, this is dangerous because errors may be subtle (a correct-sounding but inaccurate attribution, a plausible but wrong evidence classification). The self-assessment makes quality visible: "This entry has strong source diversity but limited temporal coverage, and one position's evidence base is thin."

**Dimensions assessed:**
- `source_diversity`: ratio of unique sources to positions. Higher is better.
- `temporal_coverage`: span of author death dates relative to the topic's full historical range. Wider is better.
- `school_balance`: for sciences with schools, how evenly the library covers each school's position. More balanced is better.
- `evidence_completeness`: ratio of positions with explicit evidence citations to total positions. Higher is better.
- `citation_density`: ratio of cited sentences to total sentences in the factual layer. Should be 1.0.
- `confidence_floor`: minimum upstream extraction confidence among used excerpts. Higher is better.
- `text_fidelity_distribution`: proportion of excerpts from high/medium/low fidelity sources.
- `overall_quality`: weighted composite score.

**Output:** A `quality_assessment` object in the entry's generation_metadata with scores for each dimension (0.0-1.0), plus a `quality_narrative` (one sentence summarizing the entry's quality profile for display by the scholar interface).

**Usage.** The scholar interface uses quality scores to: (a) visually indicate entry reliability (a green/yellow/red indicator), (b) prioritize which entries the owner should review, (c) identify which acquisition would most improve quality (via gap analysis), (d) track quality improvement over time as the library grows.

[NOT YET IMPLEMENTED] — Full specification provided; no code exists. No external dependencies beyond the entry's own metadata.

---

## 5. Validation and Quality

### 5.1 Self-Validation (Layer 1)

The synthesizing engine performs three categories of self-validation:

**Structural validation.** Every generated entry is validated against the entry schema before writing. Missing required fields, type mismatches, and schema violations are caught and trigger regeneration.

**Integrity checks.** The eight checks in §4.A.5 (citation completeness, citation validity, school isolation, verified/flagged separation, owner constraint compliance, grounding type consistency, temporal consistency, content quality heuristics) form the engine's internal quality gate. Critical failures block the entry; non-critical failures produce warnings.

**Anti-hallucination verification.** The factual layer is checked for claims that appear in no excerpt. The engine extracts all factual claims from the generated entry, then for each claim, verifies that at least one excerpt in the source set supports it. Claims that cannot be traced to any excerpt are flagged as potential hallucinations and removed (with the entry regenerated if the removal creates gaps). This uses the Attr-First approach from the attribution research literature: content selection before generation, not post-hoc verification.

### 5.2 Automated Checks (Layer 2)

**Regression testing with gold baselines.** For each science that has gold baseline entries (manually reviewed and approved entries for specific leaves), the engine can be run against the gold baselines to verify that updates to prompts, models, or configuration do not degrade quality. A gold baseline entry stores: the excerpts that produced it, the expected positions, the expected attributions, and the expected khilaf classifications. The regression test checks: (a) all expected positions are present, (b) all attributions match, (c) no new positions were hallucinated, (d) khilaf classifications match.

**Cross-entry consistency checks.** When multiple entries at sibling leaves are generated (e.g., all leaves under المبتدأ والخبر), the engine verifies: (a) no contradictions between sibling entries (e.g., sibling entries don't attribute the same quote to different scholars), (b) prerequisite references are consistent (if entry A says "see topic B for prerequisite X", topic B's entry should cover X).

### 5.3 Human Gate Integration

The synthesizing engine's output is ultimately consumed by the owner. Human review serves as the final quality layer.

**Trigger for human review:** (a) Any diagnostic entry (§4.A.8) triggers a review notification. (b) Any entry with overall quality assessment below 0.4 triggers a suggestion to review. (c) Any entry where the engine detected an intra-author contradiction triggers a notification explaining the contradiction and asking the owner to resolve it.

**What the human reviews:** The owner reads the entry and uses the scholar interface to: flag errors (triggers Scenario 8 correction flow), approve the entry (updates the user model with "studied" status), or request regeneration with feedback.

**What happens after review:** Approved entries are marked `owner_reviewed: true`. Corrections become permanent constraints. The correction type (factual, attribution, structural) is logged, enabling pattern detection: if the same correction type recurs across entries, the engine's prompts or processing rules may need adjustment.

---

## 6. Consensus Integration

The synthesizing engine uses multi-model consensus for a single specific decision: the scholarly analysis in Phase 2 (§4.A.3) for entries at leaves with high significance scores (≥ 0.7 per the taxonomy engine's significance scoring) or where the excerpt set is complex (≥ 10 positions identified, or ≥ 3 schools represented with disagreements).

**Consensus configuration.** Two models from different providers. Each independently performs Phase 2 analysis: position identification, khilaf classification, mu'tamad identification. Outputs are compared.

**Agreement handling:** If both models identify the same set of positions with the same khilaf classifications (allowing for minor wording differences in position summaries), the agreed-upon analysis is used.

**Disagreement handling:** If the models disagree on the number of positions, their khilaf classification, or the mu'tamad identification: (a) the more conservative analysis is used (the one that identifies more distinct positions — it's better to over-distinguish than to merge genuinely different positions), (b) the disagreement is logged in generation_metadata, (c) if the disagreement is on khilaf classification (one says lafzi, the other says haqiqi), the entry presents both classifications: "Whether this disagreement is verbal or substantive is itself debated."

**When consensus is NOT used:** Single-author leaves (only one position, no classification needed), leaves with fewer than 3 excerpts (insufficient complexity to warrant multi-model cost), and background batch regeneration (cost optimization — consensus is applied only when the owner views the entry, triggering a quality-enhanced regeneration).

---

## 7. Error Handling

### 7.1 Error Codes

| Code | Severity | Condition | Recovery |
|------|----------|-----------|----------|
| SYNTH_NO_EXCERPTS | Fatal | Leaf has no placed verified excerpts | No entry generated; leaf marked as empty |
| SYNTH_METADATA_RESOLUTION_FAILED | Warning | Registry lookup failed for excerpt | Proceed with degraded metadata |
| SYNTH_CITATION_INCOMPLETE | Fatal | Generated entry has uncited factual claims | Retry generation (up to 2 retries) |
| SYNTH_CITATION_INVALID | Fatal | Citation references non-existent excerpt | Retry generation |
| SYNTH_SCHOOL_CONTAMINATION | Fatal | Per-school entry contains cross-school excerpt | Retry generation |
| SYNTH_FLAGGED_LEAK | Fatal | Flagged excerpt in factual layer | Retry generation |
| SYNTH_GROUNDING_VIOLATION | Fatal | LLM-research claim in factual layer | Retry generation |
| SYNTH_OWNER_CONSTRAINT_VIOLATED | Fatal | Entry reproduces a corrected error | Retry with constraint more prominent |
| SYNTH_TEMPORAL_MISMATCH | Warning | Date in entry doesn't match authority record | Annotate entry; do not block |
| SYNTH_QUALITY_BELOW_THRESHOLD | Warning | Quality self-assessment below 0.4 | Generate; suggest human review |
| SYNTH_GENERATION_TIMEOUT | Fatal | LLM call exceeded timeout | Retry with smaller excerpt set or simpler prompt |
| SYNTH_ALL_RETRIES_FAILED | Fatal | All retry attempts exhausted | Produce diagnostic entry (§4.A.8) |
| SYNTH_SCHEMA_VALIDATION_FAILED | Fatal | Generated entry fails schema validation | Retry generation |
| SYNTH_STALENESS_HASH_COLLISION | Warning | Two entries have identical staleness hashes | Log for investigation; likely a bug |

### 7.2 Error Principles

**Never produce a silently wrong entry.** A visible failure (diagnostic entry with an explanation) is always better than a plausible-looking entry with hidden errors. This is D-033 (secure by design) applied to synthesis.

**Every retry is different.** When retrying after a failure, the retry prompt explicitly includes: what failed, why, and what must be different. Identical retries produce identical failures.

**Log everything.** Every LLM call, every check result, every retry is logged with: timestamp, model, prompt hash, excerpt set hash, result, and any error. This enables debugging quality issues across entries without re-running the pipeline.

**The blast radius of a synthesis error is one entry.** A bad entry at one leaf does not affect entries at other leaves. Entries are independently generated and independently verifiable. This is D-033's bounded blast radius principle.

---

## 8. Configuration

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `primary_model` | `claude-sonnet-4-20250514` | Any supported LLM | Primary model for entry generation |
| `analysis_model` | `claude-sonnet-4-20250514` | Any supported LLM | Model for Phase 2 scholarly analysis |
| `consensus_model_secondary` | `gpt-4o` | Any supported LLM (different provider) | Secondary model for consensus |
| `max_retries` | 2 | 0-5 | Retry attempts on critical check failure |
| `max_excerpts_per_entry` | 50 | 10-200 | Above this, the engine summarizes excess excerpts rather than citing each individually |
| `consensus_significance_threshold` | 0.7 | 0.0-1.0 | Significance score above which consensus is used |
| `consensus_complexity_threshold` | 10 | 1-50 | Position count above which consensus is used |
| `quality_review_threshold` | 0.4 | 0.0-1.0 | Quality score below which human review is suggested |
| `deduplication_similarity_threshold` | 0.92 | 0.8-0.99 | Embedding similarity for treating excerpts as duplicates |
| `batch_size` | 20 | 1-100 | Entries regenerated per batch cycle |
| `generation_timeout_seconds` | 120 | 30-600 | Timeout for a single LLM generation call |
| `level_default` | "intermediate" | beginner/intermediate/advanced | Default owner level when user model is unavailable |

**Per-science configuration (via SCIENCE.md):** `has_schools`, `school_list`, `school_entry_cardinality`, `evidence_hierarchy`, `has_mu_tamad`, `abrogation_check`, `entry_template`, `khilaf_classification`. These override defaults for their science.

---

## 9. Current Implementation State

**Code:** 0 lines. No code exists. No ABD equivalent existed — ABD did not have a synthesis engine.

**Tests:** 0. No tests exist.

**External tools and libraries:**
- **Instructor** (Python, MIT license): Structured output enforcement with Pydantic models. Used for ensuring LLM outputs conform to the entry content schema. `pip install instructor`.
- **DSPy** (Stanford/Databricks): Pipeline orchestration and prompt optimization. Can be used to define the synthesis pipeline declaratively and optimize prompts against gold baselines.
- **LiteLLM** (MIT license): Multi-provider LLM routing. Used for consensus (different providers for primary and secondary models) and for model switching.
- **NetworkX** (BSD license): Graph library for teacher-student chain traversal in intellectual genealogy reconstruction (§4.B.2).
- **Sentence-transformers** / Arabic embedding models: For semantic deduplication verification and consensus claim comparison.

**Known gaps between current code and this SPEC:**
- [NOT YET IMPLEMENTED] The entire engine. Everything in this SPEC is unbuilt.
- [NOT YET IMPLEMENTED] Gold baseline entries for regression testing (§5.2).
- [NOT YET IMPLEMENTED] SCIENCE.md files for per-science configuration hooks (§4.A.9). These must be written as part of Level 3 documentation.
- [NOT YET IMPLEMENTED] The owner constraint store (persistent constraints at each leaf surviving regeneration).
- [NOT YET IMPLEMENTED] The staleness queue management system.
- [NOT YET IMPLEMENTED] All four §4.B transformative capabilities.

---

## 10. Test Requirements

### 10.1 Mandatory Test Coverage

**Gold baseline generation tests.** For each supported science (starting with nahw), create at least 2 gold baseline entries: one from a simple leaf (2-3 excerpts, one school) and one from a complex leaf (7+ excerpts, multiple schools, disagreements). Tests verify: all positions present, all attributions correct, all citations valid, khilaf classification correct.

**Integrity check tests.** Each of the 8 integrity checks in §4.A.5 must have a test case with a deliberately flawed entry that the check should catch. Verify the check fires and the entry is rejected.

**School isolation tests.** Generate entries for a fiqh leaf with multiple schools. Verify no cross-school contamination.

**Verified/flagged separation tests.** Generate an entry at a leaf with both verified and flagged excerpts. Verify flagged content appears only in critical_analysis.

**Traceability boundary tests.** Verify that `core_treatment` contains only `"library_excerpt"` and `"library_metadata"` grounded claims. Inject a deliberately LLM-grounded claim into the factual layer prompt and verify the integrity check catches it.

**Staleness tests.** Add an excerpt to a leaf with an existing entry. Verify the entry is marked stale. Trigger regeneration. Verify the new entry includes the new excerpt.

**Change summary tests.** Regenerate an entry after adding a new position. Verify the change summary correctly identifies the added position.

**Diagnostic entry tests.** Force a generation failure (e.g., provide contradictory owner constraints that cannot both be satisfied). Verify a diagnostic entry is produced rather than a silent failure.

### 10.2 Regression Testing

Every change to: LLM prompts, model versions, SCIENCE.md configuration, or engine processing logic must pass the gold baseline regression tests before deployment. The gold baselines serve as ground truth — if a change causes a baseline to fail, the change is investigated before acceptance.

### 10.3 Integration Tests

**Upstream: taxonomy engine.** Verify that the synthesizing engine correctly reads placed excerpts in the format produced by the taxonomy engine. Create a test leaf with placed excerpts from the taxonomy engine's test fixtures and verify generation succeeds.

**Downstream: scholar interface.** Verify that generated entries conform to the schema expected by the scholar interface. This is primarily a schema validation test — the scholar interface reads entries from the library; the schema is the contract.

**Cross-engine: staleness signals.** Verify that when the taxonomy engine places a new excerpt, the synthesizing engine's staleness detection correctly identifies the affected entry and queues it for regeneration.
