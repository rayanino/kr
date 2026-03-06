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
  common_misunderstandings: string or null,
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

**Example:** §4.A.1. Generating an entry for leaf `nahw/marfu'at/mubtada/ta'rif` with 5 verified excerpts from 3 sources (الكتاب، الأصول في النحو، شرح ابن عقيل).

- *Phase 1:* Engine reads 5 excerpts. Resolves metadata: سيبويه d. 180 AH (بصري), ابن السراج d. 316 AH (بصري), ابن عقيل d. 769 AH (no school tag → inferred from scholar authority as شافعي/نحوي). Two excerpts from الكتاب and الأصول are semantically similar (both define المبتدأ as الاسم المجرد) → clustered, الكتاب excerpt selected as representative (higher source-authority: primary > reference). Inventory: 4 effective excerpts after deduplication.
- *Phase 2:* Position identification finds 2 positions: pos_1 (Basran meaning-based: المبتدأ هو الاسم المجرد عن العوامل اللفظية), pos_2 (form-based: المسند إليه). Khilaf classified as `lafzi` (verbal — same referent, different terminology). No intra-author contradictions. Mu'tamad: not applicable for nahw (per SCIENCE.md `has_mu_tamad: false`).
- *Phase 3:* Outline produces 12 planned claims. Attribution assigns each claim to specific excerpt spans. Conditioned generation produces Arabic prose with [cit:N] markers. Entailment verification passes for 11/12 claims; one claim about الكسائي's terminology fails entailment (excerpt only mentions الفراء) → claim rewritten to attribute to الفراء only.
- *Phase 4:* 8 integrity checks pass. Citation completeness: 12/12 factual sentences cited. School isolation: N/A (nahw has no per-school entries per SCIENCE.md `school_entry_cardinality: "unified_with_attribution"`).
- *Phase 5:* Staleness hash computed. Version 1. Entry written to `library/sciences/nahw/entries/marfu_at_mubtada_ta_rif/ent_nahw_mubtada_ta_rif_all_v1.json`.

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

**Scholarly landscape loading.** The engine reads the leaf's scholarly landscape from `library/sciences/{science_id}/content/{leaf_path}/landscape.json` (produced by the taxonomy engine §4.B.6). If the landscape exists: its pre-computed chronological timeline, influence chain graph, discourse transitions, evidence evolution map, and school positioning summary become the primary scaffold for Phase 2 analysis — the engine validates and supplements the landscape rather than rebuilding it. If the landscape does not exist (leaf has < 2 verified excerpts from < 2 sources, or the landscape has not yet been computed): the engine performs the scholarly analysis from scratch using only the excerpts and metadata. The `landscape_confidence` field determines how heavily the engine relies on the landscape: confidence ≥ 0.6 → landscape is the primary analysis source; 0.4–0.6 → landscape supplements the engine's own analysis; < 0.4 (marked `preliminary`) → landscape is advisory only, the engine performs independent analysis.

#### §4.A.3 — Phase 2: Scholarly Analysis

This phase produces a structured analysis object (`ScholarlyAnalysis` Pydantic model) consumed by Phase 3. When a scholarly landscape exists with confidence ≥ 0.6, the engine validates and enriches the landscape's pre-computed analysis. When no landscape exists or confidence is low, the engine performs the full analysis from excerpts.

**Step 1: Position identification.** The LLM receives: (a) a system prompt defining a "scholarly position" as a specific answer to the leaf's topic question, with 3 Arabic examples of same-position-different-wording vs genuinely-different-positions, (b) all verified excerpts formatted as `[EXCERPT {id}] Author: {name} (d. {date} AH) | School: {school} | Source: {work_title}\n{primary_text}`, (c) an instruction to return a `PositionList` Pydantic model. The `PositionList` contains an array of `ScholarlyPosition` objects, each with: `position_id` (format `pos_{sequence}`), `position_summary` (Arabic, ≤ 50 words), `holders` (array of `{scholar_id, name, death_hijri, school}`), `evidence_types` (array of evidence type strings from excerpt metadata), `supporting_excerpt_ids` (array), `is_response_to` (position_id of a position this one explicitly responds to, or null). Structured output enforced via Instructor with max 2 retries on schema failure.

**Prompt template — Position identification:**

```
SYSTEM:
أنت محلل نصوص علمية إسلامية. مهمتك: تحديد المواقف العلمية المتمايزة في مجموعة مقتطفات حول موضوع واحد.

تعريف "الموقف العلمي": جواب محدد على سؤال الورقة (أي سؤال هذا الموضوع في شجرة العلم).

قاعدة التمييز: عبارتان تعبّران عن نفس الحكم بألفاظ مختلفة = موقف واحد. عبارتان تختلفان في الحكم نفسه = موقفان متمايزان.

أمثلة:
- "المبتدأ هو الاسم المجرد عن العوامل اللفظية" و"المبتدأ هو ما ابتُدئ به" ← موقف واحد (تعريف واحد بصيغتين)
- "المبتدأ هو المسند إليه" ← موقف ثانٍ (اصطلاح كوفي مختلف عن البصري)
- "المبتدأ مرفوع بالابتداء" و"المبتدأ مرفوع بالخبر" ← موقفان (اختلاف في العامل)

أجب فقط بصيغة JSON المطلوبة. لا تضف شرحاً خارج البنية.

USER:
الموضوع: {leaf_title} ({science_name})
سؤال الورقة: {leaf_question}

المقتطفات:
{formatted_excerpts}

حدد جميع المواقف العلمية المتمايزة. لكل موقف، بيّن: ملخصه، أصحابه، أدلته، والمقتطفات الداعمة.
```

When a scholarly landscape exists: the engine pre-populates the position list from the landscape's chronological timeline and asks the LLM to validate, correct, and supplement (new excerpts may have been added since the landscape was computed). The LLM prompt explicitly states: "The following positions were previously identified. Verify them against the current excerpts and add any new positions not listed."

**Step 2: Khilaf classification.** For each pair of distinct positions on the same question, the LLM classifies the disagreement. The output is a `KhilafClassification` Pydantic model with: `position_pair` (two position_ids), `classification` (enum: `lafzi`, `haqiqi`, `mu_tabar`, `shadh`), `reasoning` (string, ≤ 100 words), `confidence` (float). When §4.B.5 (Khilaf Disambiguation Engine) is enabled, this step delegates to the full decomposition algorithm. When §4.B.5 is disabled, a simpler pairwise classification is used.

**Step 3: Tahrir al-mas'ala.** The engine verifies all scholars are answering the same question. The LLM receives all positions and explicitly formulates the question each position answers. If distinct questions are identified: (a) positions are grouped by question — each group becomes a sub-section in the entry, (b) the entry's `core_treatment` explicitly states: "Two distinct questions are addressed at this leaf: [question 1] and [question 2]", (c) if the questions are different enough to warrant separate leaves, the engine emits a `TAX_EVOLUTION_SIGNAL` to `library/sciences/{science_id}/evolution/signals/` with type `leaf_split_suggested`, the current leaf path, and the proposed split rationale.

**Step 4: Intra-author contradiction detection.** For each author with ≥ 2 excerpts at the leaf, the engine compares positions. Implementation: the LLM receives all excerpts from the same author and returns a `ContradictionCheckResult`: `author_id`, `contradictions_found` (boolean), `contradictions` (array of `{excerpt_id_a, excerpt_id_b, nature}` where `nature` is one of: `retraction` — later work supersedes earlier based on composition dates, `general_vs_specific` — one is a general rule, the other addresses a specific case, `genuine` — unexplained contradiction, `context_dependent` — both are correct in different contexts). Retraction detection requires comparing source metadata `composition_date` fields; when unavailable, author death dates provide a rough proxy (works from the same author with no date disambiguation are flagged as `undatable`).

**Step 5: Mu'tamad identification.** For sciences with schools (per SCIENCE.md): (a) text scan for explicit mu'tamad indicators in excerpts: keywords like `المعتمد`, `المذهب`, `المشهور`, `ما عليه الفتوى`, `الأصح`, `الراجح عند المتأخرين`, (b) cross-reference with known mu'tamad reference works per school (configured in SCIENCE.md: e.g., for Hanbali fiqh → الإنصاف by المرداوي; for Shafi'i fiqh → المجموع by النووي), (c) if not found in library, check LLM knowledge (flagged as `grounding_type: "llm_research"`), (d) if undetermined, the entry explicitly states: "The mu'tamad position in [school] on this topic has not been identified in the library's sources."

**Step 6: Abrogation check.** For fiqh and other applicable sciences (per SCIENCE.md configuration `abrogation_relevant: true`): (a) scan `evidence_refs` for Quran or hadith evidence, (b) check the LLM's knowledge of known abrogation instances for cited evidence, (c) if abrogation is detected, the affected position is marked: "This ruling is based on [evidence], which scholars recognize as abrogated by [later evidence]. [Number] scholars still cite it as evidence; [number] recognize the abrogation." Output: `abrogation_flags` array with `{position_id, evidence_ref, abrogated_by, confidence, grounding_type}`.

**Step 7: Library composition bias assessment.** Computed deterministically from the excerpt inventory: `school_ratio` (excerpts per school vs expected equal distribution), `source_concentration` (Herfindahl index of source_ids: HHI = Σ(s_i²) where s_i is the proportion of excerpts from source i; values > 0.25 indicate concentration; HHI = 1.0 means all excerpts from a single source; HHI = 1/N means perfect diversity across N sources), `temporal_skew` (coefficient of variation of author death dates — lower indicates temporal bias toward one period). Bias signals with values exceeding configured thresholds (§8) surface as caveats in the analytical layer: "The library's coverage of [school] on this topic is limited to [N] excerpts from [M] sources. The presentation may not fully represent the [school] position."

#### §4.A.4 — Phase 3: Narrative Construction

##### §4.A.4.1 — Factual Layer Construction (Attribution-First)

The factual layer is excerpt-grounded. Every claim is traceable. Construction uses an **attribution-first** approach: the engine selects source material BEFORE generating prose, ensuring every generated sentence is conditioned on specific excerpts rather than the LLM's parametric memory. This design is based on research showing that standard generate-then-cite approaches hallucinate up to 75% of content in multi-document synthesis (Belem et al. 2025), while decomposed attribution-first approaches significantly reduce hallucination (Slobodkin et al. 2024, FRONT framework 2024).

**Step 1: Outline generation.** The LLM receives the Phase 2 analysis and the content template (per science, from SCIENCE.md). It produces a structured outline: an ordered list of 5–30 claims the entry will make. Each outline element is a `PlannedClaim` with: `claim_text` (one-sentence description of what this claim states), `claim_type` (one of: `definition`, `position_statement`, `evidence_citation`, `example`, `edge_case`, `prerequisite_link`, `consensus_statement`, `retraction_note`), and `target_section` (which content section this claim belongs to: `core_treatment`, `scholarly_positions`, `edge_cases`, `common_misunderstandings`). The outline is a Pydantic model validated by Instructor.

**Step 2: Source span selection (attribution).** For each `PlannedClaim`, the LLM selects the specific excerpt(s) that ground it. The LLM receives the claim and ALL available excerpts, and returns a `ClaimAttribution` with: `claim_id`, `attributed_excerpt_ids` (1–5 excerpt IDs), `attributed_spans` (for each excerpt, the approximate character range within `primary_text` that supports this claim — start and end offsets), `attribution_confidence` (float 0.0–1.0). Claims where no excerpt supports the claim are classified as `grounding_type: "llm_research"` and routed to the analytical layer instead. Claims attributed with confidence < 0.5 are flagged for the analytical layer as well.

**Prompt template — Source span selection:**

```
SYSTEM:
أنت متخصص في إسناد الادعاءات العلمية إلى مصادرها النصية. لكل ادعاء مخطط، حدد المقتطف أو المقتطفات (١-٥) التي تدعمه، مع تحديد النطاق النصي التقريبي (بداية ونهاية بالأحرف) داخل النص الأصلي.

إذا لم يدعم أي مقتطف الادعاء ← اترك attributed_excerpt_ids فارغاً وضع attribution_confidence = 0.0
إذا كان الدعم جزئياً ← حدد ما يدعمه المقتطف فقط واضبط الثقة (0.0-1.0) حسب قوة الدعم.

لا تنسب ادعاءً إلى مقتطف لا يحتوي على محتواه صراحةً.

USER:
الادعاء المخطط:
  claim_id: {claim_id}
  claim_text: {claim_text}
  claim_type: {claim_type}

المقتطفات المتاحة:
{formatted_excerpts_with_char_offsets}

حدد المقتطفات الداعمة والنطاقات النصية.
```

**Step 3: Conditioned sentence generation.** For each claim with `grounding_type: "library_excerpt"`, the LLM generates the prose sentence(s) CONDITIONED ON the selected spans. The prompt provides ONLY the attributed excerpt spans (not all excerpts) and the claim description. The LLM generates the factual prose and an inline citation marker `[cit:N]`. This conditioning prevents the LLM from injecting parametric knowledge into the factual layer.

**Step 4: Entailment verification.** For each generated sentence, the engine verifies that the sentence is entailed by its attributed excerpt spans. This uses a separate LLM call (or a different model, if consensus is triggered) that receives the generated sentence and the attributed spans and returns: `entailed` (boolean), `unsupported_elements` (list of specific sub-claims not supported by the spans). Sentences that fail entailment verification are rewritten (up to 2 retries) with the unsupported elements removed or moved to the analytical layer. If all retries fail, the sentence is marked with a `weak_grounding` flag and included with a note.

**Prompt template — Entailment verification:**

```
SYSTEM:
أنت مدقق استلزام نصي. تتلقى جملة مولّدة ونصوصاً مصدرية. مهمتك: هل النص المصدري يستلزم الجملة المولّدة؟

القواعد:
- "مستلزَم" = كل ما تدّعيه الجملة المولّدة موجود في النص المصدري (صراحة أو بلازم واضح)
- "غير مستلزَم" = الجملة تحتوي على عنصر واحد على الأقل غير موجود في النص المصدري
- حدد بدقة كل عنصر غير مدعوم (أسماء علماء، تواريخ، أحكام، نسب)
- التعميم من حالة خاصة = غير مستلزَم
- إضافة سياق تاريخي غير موجود في المصدر = غير مستلزَم

USER:
الجملة المولّدة:
{generated_sentence}

النصوص المصدرية (المقتطفات المنسوبة):
{attributed_spans_text}

هل الجملة مستلزَمة من النصوص المصدرية؟ إذا لا، ما هي العناصر غير المدعومة تحديداً؟
```

**Entailment failure escalation.** If all PlannedClaims end up classified as `grounding_type: "llm_research"` (no library-grounded claims at all), the entry is classified as a diagnostic entry (§4.A.8) with reason `SYNTH_NO_GROUNDED_CLAIMS`. The entry text is still generated but carries a prominent warning: "This entry is based entirely on the synthesizer's research capability, not on library excerpts. Acquiring primary sources for this topic is recommended." This can occur at leaves with very thin excerpt coverage where the only excerpts are flagged (not verified).

**Scholarly positions array.** Generated in parallel with the prose. Each element corresponds to a Phase 2 position. The structured array enables the scholar interface to present positions comparatively without re-parsing prose. Each position's `holders`, `evidence_types`, and `mu_tamad_in_school` come from Phase 2 analysis; the `position_summary` is generated conditioned on the attributed excerpt spans for that position.

**Direct quotation policy.** Canonical definitions meant for memorization (identified by `claim_type: "definition"` and the excerpt being from a matn-genre source) are quoted verbatim in Arabic with explicit attribution and the original diacritics preserved exactly from `primary_text`. Explanatory content is paraphrased with citation. The decision rule: if the excerpt is from a matn or nazm source AND the claim type is `definition` or `position_statement` → verbatim quote. Otherwise → paraphrase.

**Physical citation assembly.** From the metadata chain: excerpt → passage → source. Citation includes: source title, author name, tahqiq editor (if known), publisher (if known), volume (if multi-volume), page numbers (from `physical_pages` in excerpt metadata). If page numbers are unavailable, the citation notes "page reference unavailable — digital source without pagination." All citations follow the academic format: `Author, Work (ed. Tahqiq, Publisher), vol:page` — e.g., `سيبويه، الكتاب (تح. عبد السلام هارون، الخانجي)، ١/٢٤٥`.

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

**Example:** §4.A.5. Entry generated for `fiqh/ibadat/salah/shurut/taharah` with 8 excerpts across Hanafi (3), Shafi'i (3), and Hanbali (2) schools. School-group entry for Hanafi:

- *Check 1 (citation completeness):* 15 sentences in `core_treatment`. Sentence 7 ("وهذا مما لا خلاف فيه") has no citation. → Critical failure. Retry prompt includes: "Sentence 7 is uncited. Either attribute it to a specific excerpt or move it to the analytical layer."
- *Check 3 (school isolation):* `source_excerpt_ids` contains `exc_shafi_034`. This excerpt belongs to the Shafi'i school, not Hanafi. → Critical failure. Retry prompt includes: "Excerpt exc_shafi_034 is a Shafi'i excerpt and must not appear in the Hanafi school-group entry."
- *Check 6 (grounding type):* `scholarly_positions[1].position_summary` contains a claim about the Maliki position not present in any excerpt. The claim's `grounding_type` is `library_excerpt` but no excerpt supports it. → Critical failure. Retry: either remove the Maliki reference or move it to the analytical layer with `grounding_type: "llm_research"`.
- *Check 7 (temporal consistency):* Entry says "ابن عابدين (ت ٩٥٢ هـ)" but scholar authority record shows death date 1252 AH. → Non-critical warning; entry annotated, not blocked.

#### §4.A.6 — Phase 5: Finalization

**Staleness hash.** SHA-256 of (sorted excerpt_ids joined by `|`) + `|` + SHA-256 of (concatenated excerpt primary_texts in sorted ID order).

**Version management.** First entry: version 1, null previous. Replacement: version incremented, old entry moved to history, change summary generated by comparing `scholarly_positions` arrays.

**Write to library.** Before writing, the engine performs a final pre-write validation: (a) the entry passes Pydantic schema validation (Entry model), (b) all `source_excerpt_ids` exist as files in the placed excerpt directory, (c) no existing entry at the target path has a higher version number (prevents accidental downgrade), (d) the staleness hash differs from the current entry's hash (prevents identical regeneration). If any pre-write check fails, the write is aborted with `SYNTH_PREWRITE_VALIDATION_FAILED` and the diagnostic includes which check failed. On success: atomic write (write to temp file → fsync → rename to final path).

**Example:** §4.A.6. Entry v2 replacing v1 at `nahw/marfu'at/mubtada/ta'rif`. Since v1, one new excerpt was placed (from أوضح المسالك by ابن هشام). Staleness hash: SHA-256 of `exc_001|exc_002|exc_003|exc_005|exc_007` + `|` + SHA-256 of concatenated primary texts. Version: 2. Previous version: `ent_nahw_mubtada_ta_rif_all_v1`. V1 entry moved to `history/ent_nahw_mubtada_ta_rif_all_v1.json`. Change summary generated by diffing `scholarly_positions` arrays: `positions_added: []`, `positions_modified: ["pos_1"]` (pos_1 now has an additional holder: ابن هشام d. 761 AH), `new_excerpts_incorporated: ["exc_007"]`, `structural_changes: "Added ابن هشام's formulation to the Basran definition section."`

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

**Example:** §4.A.8. Leaf `fiqh/mu'amalat/riba/ta'rif` has 2 verified excerpts, both from الهداية by المرغيناني. Phase 3 generation fails citation completeness 3 times (all retries exhausted) because the LLM keeps injecting claims about the Shafi'i position which has no excerpt support. Diagnostic entry produced:
```
{
  "is_diagnostic": true,
  "diagnostic_reason": "SYNTH_ALL_RETRIES_FAILED: citation completeness check failed 3 times. 
    The LLM consistently introduces Shafi'i positions not grounded in any placed excerpt.",
  "core_treatment": "الربا في اللغة: الزيادة. وفي الاصطلاح عند الحنفية: [exc_041 verbatim]. 
    وقال المرغيناني: [exc_042 verbatim].",
  "scholarly_positions": [{"position_id": "pos_1", "holders": [{"name": "المرغيناني"}], ...}]
}
```
The diagnostic entry lists excerpts with minimal synthesis (near-verbatim presentation) and flags that only the Hanafi perspective is represented. The scholar interface displays: "⚠ This entry could not be fully synthesized. It presents available excerpts without narrative integration."

#### §4.A.9 — Per-Science Customization Hooks

SCIENCE.md (Level 3) specifies per-science configuration. The engine reads it at generation time.

**Hook 1: School handling.** `has_schools`, `school_list`, `school_entry_cardinality` ("per_school" for fiqh, "unified_with_attribution" for nahw).

**Hook 2: Evidence hierarchy.** Ordered evidence types by weight. Fiqh: quran, hadith, ijma, qiyas... Nahw: samā', qiyas, ijma_al_nahwiyyin.

**Hook 3: Mu'tamad applicability.** `has_mu_tamad: boolean`.

**Hook 4: Abrogation applicability.** `abrogation_check: boolean`.

**Hook 5: Entry format preferences.** Template reference for section ordering per science.

**Hook 6: Khilaf relevance.** `khilaf_classification: boolean`. False for tajwid.

**Example:** §4.A.9. Two leaves processed with different SCIENCE.md configurations.

*Leaf: `fiqh/ibadat/salah/shurut/taharah` (Fiqh science):*
SCIENCE.md for fiqh: `has_schools: true`, `school_list: ["حنفي", "مالكي", "شافعي", "حنبلي"]`, `school_entry_cardinality: "per_school"`, `has_mu_tamad: true`, `abrogation_check: true`, `khilaf_classification: true`, `evidence_hierarchy: ["quran", "hadith", "ijma", "qiyas", "istihsan", "maslaha"]`. Engine generates 4 separate entries (one per school), each with mu'tamad identification and evidence ranked by the fiqh hierarchy.

*Leaf: `tajwid/ahkam_nun_sakinah/idgham` (Tajwid science):*
SCIENCE.md for tajwid: `has_schools: false`, `school_entry_cardinality: "unified_with_attribution"`, `has_mu_tamad: false`, `abrogation_check: false`, `khilaf_classification: false`, `evidence_hierarchy: ["qira'at_mutawatira", "scholarly_convention"]`. Engine generates 1 unified entry. Khilaf classification is skipped entirely. Evidence uses the tajwid-specific hierarchy (qira'at readings ranked above scholarly convention).

#### §4.A.10 — Cross-Science Entry Generation

For cross-science analyses (Scenario 3), the engine generates special entries drawing from excerpts at 2 or more leaves across 2 or more science trees (linked via `cross_science_links.json`). Cross-science entries:
- Do NOT replace per-science entries — stored at `library/cross_science/{link_id}/entry.json`.
- Factual layer represents positions from all linked sciences with clear attribution to science and leaf of origin.
- Analytical layer focuses on the connection: how a grammatical rule affects a legal interpretation.
- Citations reference each contributing science tree by `science_id` and `leaf_path`.
- Generated on demand (owner request or scholar interface action), not automatically.

**Example:** §4.A.10. Cross-science link between `nahw/marfu'at/mubtada` and `fiqh/usul/dalalat/mafhum_al_mukhalafa`. The grammatical definition of المبتدأ (subject) affects legal interpretation of conditional sentences. The cross-science entry's factual layer presents the nahw positions on المبتدأ with attribution to nahw scholars and excerpts, then the fiqh positions on مفهوم المخالفة with attribution to usul scholars. The analytical layer explains: "The Basran meaning-based definition of المبتدأ implies that the subject carries semantic weight beyond its syntactic position — this has consequences for how usul scholars evaluate whether a conditional sentence's unstated converse (مفهوم المخالفة) carries legal force." Each citation carries `science_id` identifying which tree grounded it.

#### §4.A.11 — Ellipsis Expansion and Level Adaptation

Arabic scholarly texts omit words understood from context. The engine expands based on the owner's level (from user model):

**Beginner.** Maximum expansion: implicit concepts made explicit, technical terms defined on first use.

**Intermediate.** Moderate expansion: core concepts assumed, connections spelled out. Terms used without definition.

**Advanced.** Minimal expansion: terse classical style preserved, original phrasing preferred for scholarly significance.

Default (no level data): intermediate. Level affects the analytical layer and edge_cases more than the factual layer.

**Example:** §4.A.11. Excerpt from الكتاب: "هذا باب المسند والمسند إليه". This terse classical formulation omits explanation.

*Beginner level:* "هذا باب المسند والمسند إليه — أي: هذا هو الباب الذي يتناول العلاقة بين المبتدأ (وهو المسند إليه، أي الاسم الذي يُحكم عليه) والخبر (وهو المسند، أي الكلام الذي يخبر عن المبتدأ). وسيبويه يعني بالمسند إليه ما يسمّيه النحاة المتأخرون: المبتدأ." — All implicit concepts explicit, technical terms defined, classical terminology mapped to later convention.

*Intermediate level:* "هذا باب المسند والمسند إليه — يعني المبتدأ والخبر. والمسند إليه هو المبتدأ في اصطلاح المتأخرين." — Core mapping provided, technical terms used without full definition.

*Advanced level:* "هذا باب المسند والمسند إليه" — Original wording preserved. No expansion. A note in the analytical layer: "سيبويه's terminology (المسند/المسند إليه) predates the standardized المبتدأ/الخبر terminology."

---

### §4.B — Transformative Capabilities

#### §4.B.1 — Scholarly Consensus Mapping

**Capability:** For each position at a leaf, the engine automatically classifies its strength on a scholarly consensus spectrum: absolute consensus (إجماع قطعي), near-consensus (إجماع ظني / قول الجمهور), strong majority, weak majority, evenly disputed, and minority/aberrant. This classification synthesizes three signals: (a) the explicit claims in excerpts ("أجمع العلماء على..." — "scholars have consensus on..."), (b) the distribution of positions across sources and schools in the library (library evidence), and (c) the engine's LLM knowledge of the broader scholarly tradition beyond the library (LLM research, flagged accordingly).

**Why this is transformative.** No existing Islamic studies tool automatically maps consensus strength. A student reading classical texts encounters scattered consensus claims — but no tool integrates these claims across sources, validates them against the actual distribution of positions, or distinguishes genuine consensus from overclaimed consensus. KR can answer: "Is this really an ijma, or did one scholar claim consensus while others disagreed?"

**Input:** The `scholarly_positions` array from Phase 2 analysis, the library's full coverage data for the leaf (which schools are represented, how many sources hold each position), and the engine's LLM knowledge.

**Output:** Each position in the `scholarly_positions` array receives a `consensus_strength` field with: the classification label, the evidence for the classification (specific excerpt IDs that claim consensus, the library's school-by-school position distribution as counts), and a confidence score. Before writing consensus data to the entry, the engine validates: (a) every cited excerpt ID exists in the placed excerpt collection, (b) the classification is consistent with the library distribution (e.g., `absolute_consensus` requires 0 dissenting positions in the library), (c) confidence scores are within [0.0, 1.0]. Validation failures produce `SYNTH_CONSENSUS_VALIDATION_FAILED` (warning) and the position's consensus field is omitted rather than written with invalid data.

The entry's analytical layer includes a consensus narrative when 2 or more positions exist: "This position is held by consensus according to [excerpt sources], and the library confirms no dissenting source on record. However, [if the library covers fewer than 3 of the science's schools], the consensus claim cannot be verified for [school] due to limited library coverage."

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
4. If the work relationship graph contains placeholder records for unacquired works that would fill the gap (D-027), the engine validates each placeholder record exists in `library/registries/works.json` before including it as an acquisition recommendation. Invalid work IDs are logged as `SYNTH_INVALID_WORK_REFERENCE` (warning) and omitted from the recommendation. Valid recommendations are included: "Acquiring [Work X] by [Author Y], which is in the library's wish list, would provide primary source coverage for this gap."

**Output:** A `gap_notes` array in the entry, each containing: `gap_type`, `gap_description`, `provisional_content` (the engine's inference about the missing perspective), `confidence`, `grounding_type: "llm_research"`, `recommended_acquisitions` (work IDs from the work registry's placeholder records).

**Constraints:** Gap notes never appear in the factual layer. They are presented by the scholar interface as "What KR thinks you're missing" — a distinct section from the verified scholarly content.

[NOT YET IMPLEMENTED] — Full specification provided; no code exists. Depends on: taxonomy engine coverage gap detection (§4.A.6), work relationship graph with placeholder records (D-027).

#### §4.B.4 — Entry Quality Self-Assessment

**Capability:** After generating an entry, the engine produces a structured self-assessment scoring the entry's quality across 7 defined dimensions (source_diversity, temporal_coverage, school_balance, evidence_completeness, citation_density, confidence_floor, text_fidelity_distribution), enabling the scholar interface to present quality indicators and enabling systematic quality improvement over time.

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

#### §4.B.5 — Khilaf Disambiguation Engine (تحرير مسألة الخلاف)

**Capability:** The engine performs automated tahrir al-mas'ala (تحرير المسألة) — the most important and most difficult task in Islamic comparative jurisprudence. When two or more scholars appear to disagree, the engine formally decomposes their positions into atomic sub-claims and determines whether they are answering the SAME question differently (genuine disagreement) or answering DIFFERENT questions (apparent disagreement). This decomposition produces a structured "disagreement map" that is fundamentally different from — and more useful than — a flat list of positions.

**Why this is transformative.** Tahrir al-mas'ala is what separates a competent scholar from a beginner. A beginner sees: "Scholar A says X. Scholar B says Y. They disagree." A skilled scholar asks: "Wait — is Scholar A answering the same question as Scholar B? What exactly is the point of disagreement? Is it about the definition, the scope, the conditions, or the ruling?" This analytical decomposition is what classical scholars like al-Nawawi, Ibn Qudamah, and al-Mardawi performed manually in their comparative fiqh works — and it takes YEARS of training to do correctly. No existing digital tool automates this. KR makes this skill available from the first day of study.

**Input:** The Phase 2 positions array, the full excerpt text for each position, the leaf's topic description, and the science's SCIENCE.md (for domain-specific disagreement conventions).

**Processing:**

1. **Atomic claim decomposition.** For each position, the LLM decomposes it into atomic sub-claims. A position like "المبتدأ هو الاسم المجرد عن العوامل اللفظية" is decomposed into: (a) المبتدأ is an اسم (shared with all), (b) it is characterized by being مجرد عن العوامل اللفظية (the distinctive Basran claim), (c) its case (رفع) is caused by الابتداء as a معنوي عامل (the theoretical framework). The decomposition uses a Pydantic schema `AtomicSubClaim` with: `claim_text` (Arabic), `claim_type` (one of: `definitional`, `conditional`, `ruling`, `scope`, `methodological`, `terminological`), `shared_by` (which positions share this sub-claim). Output enforced by Instructor.

2. **Agreement-disagreement matrix.** The engine constructs a matrix where rows are atomic sub-claims and columns are positions. Each cell is `agree`, `disagree`, or `not_addressed`. Cells where ALL positions agree identify the **common ground** — the undisputed shared foundation. Cells where positions diverge identify the **precise locus of disagreement**.

3. **Disagreement classification.** For each disagreement locus, the engine classifies it as:
   - `lafzi` (verbal): sub-claims use different terms but express the same meaning. Detection: the LLM judges semantic equivalence of the differing sub-claims. Example: calling المبتدأ "المسند إليه" vs "ما ابتُدئ به" — same concept, different term.
   - `ishtiraki` (shared-concept): scholars agree on the concept but disagree on which instances fall under it. Detection: one sub-claim is a subset of another. Example: both agree المبتدأ is مرفوع, but disagree on whether مبتدأ مؤخر counts.
   - `haqiqi` (substantive): genuinely different claims about the same thing. Detection: the sub-claims are contradictory (NLI entailment check returns `contradiction`).
   - `su'al_mukhtalif` (different question): the scholars are addressing different questions entirely — the apparent disagreement dissolves when the questions are made explicit. Detection: the `claim_type` tags differ (e.g., one is `definitional`, another is `ruling`), or the scope of the sub-claim differs.

4. **Disagreement narrative.** The engine generates a structured narrative: "The apparent disagreement between Scholar A and Scholar B is [classification]. They agree on [common ground]. The precise point of departure is [locus]. Scholar A's position addresses [question X], while Scholar B addresses [question Y]." This narrative goes into the entry's `core_treatment` as a scholarly apparatus section.

**Output:** A `khilaf_disambiguation` object stored in the entry's `generation_metadata`: `atomic_subclaims` (array), `agreement_matrix` (2D structure), `disagreement_loci` (array of `{locus, classification, evidence, confidence}`), `common_ground_summary` (string), `disambiguation_confidence` (float — lower when positions are truly ambiguous). The entry text incorporates the disambiguation results into the scholarly positions presentation, explicitly stating: "This is a verbal disagreement — both positions express the same ruling in different terminology" or "This is a substantive disagreement centered on [specific question]."

**Why this is architect-originated.** DOMAIN.md mentions خلاف types and tahrir al-mas'ala as important scholarly concepts. It does NOT specify that the synthesizer should decompose positions into atomic sub-claims, construct agreement matrices, or automate the disambiguation process. The decomposition algorithm, the agreement-matrix representation, and the four-category classification scheme (including the novel `ishtiraki` and `su'al_mukhtalif` categories beyond the traditional `lafzi`/`haqiqi` binary) are original design.

**Technical approach.** Atomic decomposition uses LLM with Instructor-enforced Pydantic output. Agreement matrix construction is deterministic once decomposition is complete. NLI-based contradiction detection for `haqiqi` classification uses the same approach as §4.B.1 (embedding similarity filtering → LLM contradiction classification). The `su'al_mukhtalif` detection compares the `claim_type` tags and the scope of each sub-claim — if positions have no overlapping sub-claim types, they are likely answering different questions.

[NOT YET IMPLEMENTED] — Full specification provided; no code exists. Depends on: Phase 2 position identification, Instructor library for structured output, LLM with Arabic scholarly knowledge.

**Example:** §4.B.5 — المبتدأ definitions disaggregated.**

*Input:* Two positions at `nahw/marfu'at/mubtada/ta'rif`:
- pos_1 (Basran): "المبتدأ هو الاسم المجرد عن العوامل اللفظية مسنداً إليه" (ابن السراج d. 316 AH)
- pos_2 (Kufan): "المبتدأ هو المسنَد إليه في الجملة الاسمية" (attributed to الكسائي's school)

*Step 1 — Atomic decomposition:*
- pos_1 sub-claims: (a) المبتدأ is an اسم [definitional, shared_by: [pos_1, pos_2]], (b) it is مجرد عن العوامل اللفظية — free from verbal operators [methodological, shared_by: [pos_1]], (c) it is مسند إليه — predicated about [definitional, shared_by: [pos_1, pos_2]], (d) its رفع is caused by الابتداء [methodological, shared_by: [pos_1]]
- pos_2 sub-claims: (a) المبتدأ is an اسم [definitional, shared_by: [pos_1, pos_2]], (b) it is المسند إليه — the thing predicated about [definitional, shared_by: [pos_1, pos_2]], (c) it occupies initial position في الجملة الاسمية [scope, shared_by: [pos_2]]

*Step 2 — Agreement matrix:*
| Sub-claim | pos_1 | pos_2 |
|-----------|-------|-------|
| المبتدأ is اسم | agree | agree |
| المبتدأ is مسند إليه | agree | agree |
| مجرد عن العوامل اللفظية | agree | not_addressed |
| رفع by الابتداء | agree | not_addressed |
| positional criterion (في الجملة) | not_addressed | agree |

Common ground: both agree المبتدأ is an اسم and is مسند إليه.
Disagreement loci: (1) pos_1 uses operator theory (العامل), pos_2 doesn't address it → `su'al_mukhtalif`; (2) pos_2 adds positional criterion, pos_1 doesn't → `ishtiraki`.

*Step 3 — Classification:* Primary classification: `su'al_mukhtalif` — pos_1 answers "what theoretical framework explains المبتدأ's case?" while pos_2 answers "how do you identify المبتدأ in a sentence?"

*Step 4 — Narrative:* "الخلاف بين البصريين والكوفيين في تعريف المبتدأ ليس خلافاً حقيقياً في المعرّف بل هو خلاف في زاوية التعريف: البصريون عرّفوه من جهة نظرية العامل (المجرد عن العوامل اللفظية)، والكوفيون عرّفوه من جهة الموقع الإعرابي (المسند إليه في الجملة). والمتفق عليه: أنه اسم مرفوع يُخبَر عنه."

#### §4.B.6 — Socratic Self-Verification and Assessment Generation

**Capability:** After generating an entry, the engine produces a structured set of comprehension questions at four cognitive levels, then uses these questions to verify the entry's own coherence AND to fuel the user model's assessment system. The questions test whether the entry actually teaches what it claims to teach — if the LLM cannot answer its own questions from the entry text alone, the entry has a coherence defect.

**Why this is transformative.** Two problems are solved simultaneously. First, hallucination detection: research shows LLMs hallucinate 17.7% of sentences in open-domain generation (self-contradiction analysis, OpenReview 2023), and up to 75% in multi-document synthesis (Belem et al. 2025). By generating questions and then attempting to answer them from the entry text, the engine catches entries that SOUND correct but contain internally inconsistent or unsupported claims. Second, assessment gap: the owner's learning depends on testing comprehension, but no existing Islamic studies tool generates topic-appropriate assessment questions. KR generates them as a byproduct of entry quality verification.

**Input:** The completed entry (post-Phase 4 integrity verification), the Phase 2 scholarly analysis, and the leaf's prerequisite and sibling data from the taxonomy.

**Processing:**

1. **Question generation at four levels.** The LLM generates 4–8 questions per entry, distributed across four cognitive levels (inspired by Bloom's taxonomy adapted for Islamic scholarly discourse):
   - **Level 1 — Recall (حفظ):** "What is the Basran definition of المبتدأ?" — tests whether the entry's core definition is memorizable. 1–2 questions. Answer must be directly extractable from the entry text.
   - **Level 2 — Recognition (تمييز):** "Which scholar first articulated this definition, and in which work?" — tests attribution retention. 1–2 questions. Answer requires connecting position to scholar to source.
   - **Level 3 — Application (تطبيق):** "In the sentence 'في الدار رجلٌ', which word is the مبتدأ, and which definition supports this analysis?" — tests whether edge cases are understood. 1–2 questions. Answer requires applying the entry's rules to a novel example.
   - **Level 4 — Comparison (موازنة):** "How does the Basran definition differ from the Kufan approach, and what underlying methodological disagreement explains this difference?" — tests deep understanding. 1–2 questions. Answer requires synthesizing 2 or more positions and understanding the intellectual context.

   Each question is a Pydantic `AssessmentQuestion` with: `question_text` (Arabic), `level` (1–4), `expected_answer` (the answer extractable from the entry), `answer_excerpt_ids` (which excerpts ground the answer), `prerequisite_knowledge` (what the student must already know to attempt this question).

2. **Self-verification round.** The engine sends each generated question BACK to the LLM with ONLY the entry text as context (no excerpts, no metadata). The LLM attempts to answer each question. The engine then compares the LLM's answer to the `expected_answer` using semantic similarity (embedding cosine > 0.8) and NLI entailment. Questions where the LLM's answer contradicts or significantly differs from the expected answer indicate an **entry coherence defect** — the entry text does not clearly communicate what it claims to.

3. **Defect resolution.** For each coherence defect:
   - If the question is Level 1 or 2 (recall/recognition): the relevant section of the entry is rewritten for clarity — the information is present but not clearly stated.
   - If the question is Level 3 (application): the entry may be missing edge case coverage. The engine checks whether the scenario in the question is addressed; if not, it adds an edge case section.
   - If the question is Level 4 (comparison): the entry may lack the connecting narrative. The engine checks whether the analytical layer adequately explains the relationship between positions.

4. **Assessment storage.** Questions that pass self-verification are stored alongside the entry at `library/sciences/{science_id}/entries/{leaf_slug}/assessment_{entry_id}.json`. The user model's assessment module reads these questions during study sessions. Questions are versioned with the entry — when the entry is regenerated, new questions are generated and old ones are archived.

**Output:** A `self_verification` object in the entry's `generation_metadata`: `questions_generated` (int), `questions_passed` (int), `coherence_defects_found` (int), `defects_resolved` (int), `verification_confidence` (float — ratio of passed to total). An `assessment_questions` array stored as a separate artifact (see above). Entry quality assessment (§4.B.4) incorporates the self-verification score: an entry where 100% of self-verification questions pass has higher quality than one where only 60% pass.

**Why this is architect-originated.** No component of VISION.md, DOMAIN.md, or the owner's requests specifies that the synthesizer should generate test questions or use them for self-verification. The dual-purpose design (quality verification + assessment fuel) and the four-level cognitive taxonomy adapted for Islamic scholarly discourse are original. The closest reference in DOMAIN.md is the mention that KR should "challenge understanding" — but the mechanism (generate questions from entry, answer from entry text, detect coherence gaps) is entirely designed here.

**Technical approach.** Question generation uses LLM with Instructor for structured output. Self-verification uses a separate LLM call (ideally a different model for diversity) with the entry text as sole context. Semantic comparison for answer verification uses the same embedding model as the taxonomy engine (Swan-Large or equivalent Arabic model from RESOURCES.md). NLI entailment check reuses the infrastructure from §4.B.1 and §4.B.5.

[NOT YET IMPLEMENTED] — Full specification provided; no code exists. Depends on: completed entry from Phases 1–4, Instructor library, embedding model for answer comparison, LLM with Arabic scholarly knowledge.

**Example:** §4.B.6 — Self-verification catches a coherence defect.**

*Entry:* `nahw/marfu'at/mubtada/ta'rif`, 5 positions, 12 citations.

*Question generation:*
- Level 1: "ما تعريف المبتدأ عند البصريين؟" → Expected answer: "الاسم المجرد عن العوامل اللفظية" (extractable from core_treatment sentence 3).
- Level 2: "من أول من صاغ هذا التعريف، وفي أي كتاب؟" → Expected: "ابن السراج في الأصول في النحو" (from scholarly_positions[0].holders + citations).
- Level 3: "في جملة 'في الدار رجلٌ'، ما المبتدأ؟ وأي تعريف يدعم هذا الإعراب؟" → Expected: "رجلٌ هو المبتدأ مؤخراً. التعريف البصري الدلالي يدعم ذلك لأنه يعرّف المبتدأ بدوره المعنوي لا بموقعه." (from edge_cases section).
- Level 4: "ما الأساس المنهجي الذي يفسّر اختلاف البصريين والكوفيين في تعريف المبتدأ؟" → Expected: "البصريون بنوا النحو على المعنى والعامل المعنوي، والكوفيون بنوه على الموقع الإعرابي." (from analytical_layer).

*Self-verification:*
- Level 1 question: LLM answers from entry text → "الاسم المجرد عن العوامل اللفظية". Cosine similarity with expected: 0.97. ✓ Pass.
- Level 2 question: LLM answers → "سيبويه في الكتاب". Expected was "ابن السراج في الأصول". Cosine similarity: 0.41. NLI: contradiction. **Coherence defect detected.** The entry attributes the operator-free definition to ابن السراج but the self-verification LLM (reading only entry text) concluded it was سيبويه. Root cause: the entry's core_treatment mentions سيبويه's earlier definition before ابن السراج's refinement, but doesn't clearly distinguish who formulated the "المجرد عن العوامل اللفظية" phrasing.
- *Defect resolution:* Entry's core_treatment is rewritten for clarity: "سيبويه (ت ١٨٠ هـ) عرّف المبتدأ بأنه «الاسم الذي بُني عليه الخبر». ثم صاغ ابن السراج (ت ٣١٦ هـ) التعريف بمصطلح العامل: «الاسم المجرد عن العوامل اللفظية» — وهذه الصياغة الأخيرة هي المعتمدة عند البصريين المتأخرين."
- Level 3, Level 4: both pass after re-verification.

*Output:* `self_verification: {questions_generated: 5, questions_passed: 4, coherence_defects_found: 1, defects_resolved: 1, verification_confidence: 1.0}`

---

## 5. Validation and Quality

### 5.1 Self-Validation (Layer 1)

The synthesizing engine performs three categories of self-validation:

**Structural validation.** Every generated entry is validated against the entry schema before writing. Missing required fields, type mismatches, and schema violations are caught and trigger regeneration.

**Integrity checks.** The eight checks in §4.A.5 (citation completeness, citation validity, school isolation, verified/flagged separation, owner constraint compliance, grounding type consistency, temporal consistency, content quality heuristics) form the engine's internal quality gate. Critical failures block the entry; non-critical failures produce warnings.

**Anti-hallucination verification.** The factual layer is checked for claims that appear in no excerpt. The engine extracts all factual claims from the generated entry, then for each claim, verifies that at least one excerpt in the source set supports it. Claims that cannot be traced to any excerpt are flagged as potential hallucinations and removed (with the entry regenerated if the removal creates gaps). This uses the Attr-First approach from the attribution research literature: content selection before generation, not post-hoc verification.

### 5.2 Automated Checks (Layer 2)

**Regression testing with gold baselines.** For each science that has gold baseline entries (manually reviewed and approved entries for specific leaves), the engine can be run against the gold baselines to verify that updates to prompts, models, or configuration do not degrade quality. A gold baseline entry stores: the excerpts that produced it, the expected positions, the expected attributions, and the expected khilaf classifications. The regression test checks: (a) all expected positions are present, (b) all attributions match, (c) no new positions were hallucinated, (d) khilaf classifications match.

**Cross-entry consistency checks.** When 2 or more entries at sibling leaves are generated (e.g., all leaves under المبتدأ والخبر), the engine verifies: (a) no contradictions between sibling entries (e.g., sibling entries don't attribute the same quote to different scholars), (b) prerequisite references are consistent (if entry A says "see topic B for prerequisite X", topic B's entry should cover X).

### 5.3 Human Gate Integration

The synthesizing engine's output is ultimately consumed by the owner. Human review serves as the final quality layer.

**Trigger for human review:** (a) Any diagnostic entry (§4.A.8) triggers a review notification. (b) Any entry with overall quality assessment below 0.4 triggers a suggestion to review. (c) Any entry where the engine detected an intra-author contradiction triggers a notification explaining the contradiction and asking the owner to resolve it.

**What the human reviews:** The owner reads the entry and uses the scholar interface to: flag errors (triggers Scenario 8 correction flow), approve the entry (updates the user model with "studied" status), or request regeneration with feedback.

**What happens after review:** Approved entries are marked `owner_reviewed: true`. Corrections become permanent constraints. The correction type (factual, attribution, structural) is logged, enabling pattern detection: if the same correction type recurs across 3+ entries, the engine's prompts or processing rules may need adjustment.

### 5.4 Threat Mapping (KNOWLEDGE_INTEGRITY.md)

The synthesizing engine is the pipeline's terminal consumer. Every upstream threat has the potential to surface as an error in the entry — which is an error in Rayane's knowledge. This section maps each threat to its synthesis-specific manifestation and prevention.

**T-1 (Silent Text Corruption) → Synthesis vector: corrupted excerpt text enters the entry verbatim.** The engine quotes canonical definitions verbatim (§4.A.4.1 direct quotation policy). If `primary_text` was corrupted upstream, the entry perpetuates the corruption. **Prevention:** (a) The engine does not modify `primary_text` — it quotes or paraphrases what it receives. Corruption is therefore traceable to the frozen source. (b) For verbatim quotes (matn definitions), the entry's citation includes `source_id` + `passage_id` + page reference, enabling the owner to spot-check against the physical book. (c) The self-verification cycle (§4.B.6) may catch corruption that creates incoherence — e.g., a corrupted definition that contradicts its own edge cases. **Residual risk:** HIGH — the engine cannot independently detect single-character corruption in Arabic text. The frozen source chain is the primary mitigation.

**T-2 (Attribution Error) → Synthesis vector: entry attributes a position to the wrong scholar or school.** This is the engine's highest-impact threat. An entry that says "قال ابن قدامة" when the excerpt is from ابن رشد corrupts Rayane's understanding of who holds which position. **Prevention:** (a) The engine reads `primary_author_id` from excerpt metadata, not from the text itself — attribution follows the upstream consensus. (b) For each scholar cited, the engine validates against the scholar authority registry: name, death date, school. Mismatches produce `SYNTH_TEMPORAL_MISMATCH` (warning). (c) The integrity check in §4.A.5 Check 3 (school isolation) prevents cross-school contamination. (d) The scholarly positions array uses structured `holders` with `scholar_id` — the scholar interface can independently verify. (e) Multi-model consensus for Phase 2 analysis (§6) provides a second opinion on attribution for high-significance leaves. **Residual risk:** MEDIUM — the engine trusts upstream attribution. If the excerpting engine misattributes and all consensus models agree, the error propagates.

**T-3 (Taxonomic Misplacement) → Synthesis vector: entry incorporates an excerpt that doesn't belong at this leaf.** The engine synthesizes whatever excerpts are placed at the leaf. A misplaced excerpt introduces irrelevant or misleading content. **Prevention:** (a) Phase 2 tahrir al-mas'ala (§4.A.3 Step 3) detects when scholars are answering different questions — this catches excerpts that address a different topic. When detected, the engine emits `TAX_EVOLUTION_SIGNAL` suggesting a leaf split. (b) The scholarly analysis may identify an excerpt whose position is entirely unrelated to the other positions — this surfaces as an outlier in the khilaf classification. (c) The engine cannot independently determine correct placement; it relies on the taxonomy engine's placement pipeline. **Residual risk:** MEDIUM — a misplaced excerpt on a closely related topic (e.g., conditions of وضوء placed under conditions of صلاة) may not be detected.

**T-4 (Context Loss) → Synthesis vector: entry paraphrases an excerpt that lacks the context needed for independent comprehension, producing a misleading claim.** An excerpt that says "والحكم كما سبق" without context yields an empty or fabricated paraphrase. **Prevention:** (a) The engine checks `self_containment_score` during Phase 1 collection (§4.A.2). Excerpts with score < 0.5 are flagged in `generation_metadata` and the LLM prompt notes their limited self-containment. (b) The attribution-first pipeline (§4.A.4.1) requires that each generated sentence be entailed by its attributed excerpt spans — an excerpt with insufficient context cannot entail a substantive claim, so the entailment check catches fabrication. (c) If all excerpts at a leaf have low self-containment, the overall entry quality drops and the quality assessment (§4.B.4) triggers human review. **Residual risk:** LOW — the entailment verification is specifically designed to catch claims that go beyond what the excerpt supports.

**T-5 (Synthesis Hallucination) → Synthesis vector: the LLM invents scholarly positions, evidence, or attributions not in any excerpt.** This is the defining threat for the synthesizing engine. **Prevention:** (a) Attribution-first pipeline (§4.A.4.1) — content selection before generation, not post-hoc citation. (b) Entailment verification (§4.A.4.1 Step 4) — every factual sentence checked against its attributed spans. (c) Grounding type enforcement (§4.A.5 Check 6) — no `"llm_research"` claims in `core_treatment` or `scholarly_positions`. (d) Socratic self-verification (§4.B.6) — questions generated from the entry are answered from the entry text; inconsistencies reveal hallucinated content. (e) The structural separation between factual and analytical layers ensures that even when LLM knowledge is used, it is confined to sections the reader knows are not excerpt-backed. **Residual risk:** MEDIUM — subtle hallucinations (e.g., correct scholar, correct school, plausible but wrong death date) may pass all checks. Multi-model consensus for high-significance leaves is the primary mitigation for these cases.

**T-6 (Metadata Poisoning) → Synthesis vector: wrong metadata produces a structurally correct but factually wrong entry.** If a source is tagged as primary (مصدر أصلي) but is actually a compilation (مصدر ثانوي), the engine gives it undue weight in deduplication (§4.A.2 — primary sources preferred). If an author's school is wrong, per-school entries contain cross-school content. **Prevention:** (a) The engine reads metadata from the library's registries, not from individual excerpts — centralized metadata is easier to audit. (b) Metadata chain resolution logs every lookup (§4.A.2) — if a suspicious pattern emerges (e.g., an author with conflicting school tags across sources), `SYNTH_METADATA_RESOLUTION_FAILED` is logged. (c) The library composition bias assessment (§4.A.3 Step 7) detects concentration in source_ids — if one "primary" source dominates, the entry notes the dependency. **Residual risk:** MEDIUM — the engine cannot independently verify metadata. It trusts the registries.

**T-7 (Duplication and Contradiction) → Synthesis vector: duplicate excerpts inflate the entry, or contradictory duplicates produce incoherent positions.** Two editions of the same passage entering the library may have slightly different text. The engine might treat them as two distinct positions when they are one. **Prevention:** (a) Semantic deduplication in Phase 1 (§4.A.2) clusters similar excerpts using the taxonomy engine's duplicate cluster data. (b) Intra-author contradiction detection (§4.A.3 Step 4) identifies when the same author appears to hold different positions. (c) The representative-selection algorithm for duplicate clusters ensures only the best-quality excerpt is cited, while others are logged. **Residual risk:** LOW — the deduplication threshold (§8, default 0.92 similarity) may miss paraphrastic duplicates below the threshold, but these would appear as two scholars holding the same position (a false positive in position count, not a knowledge error).

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
| SYNTH_PREWRITE_VALIDATION_FAILED | Fatal | Pre-write checks failed (§4.A.6) | Log which check failed; abort write |
| SYNTH_CONSENSUS_VALIDATION_FAILED | Warning | Consensus strength data failed validation | Omit consensus field from position |
| SYNTH_INVALID_WORK_REFERENCE | Warning | Gap note references non-existent work ID | Omit recommendation; log reference |
| SYNTH_ENTAILMENT_FAILED | Warning | Generated sentence not entailed by attributed spans | Rewrite (up to 2 retries); mark `weak_grounding` if all fail |
| SYNTH_NO_GROUNDED_CLAIMS | Fatal | All planned claims classified as LLM-research | Produce diagnostic entry with prominent warning |
| SYNTH_LANDSCAPE_MISMATCH | Warning | Landscape data contradicts excerpt-derived analysis | Prefer excerpt-derived analysis; log discrepancy |
| SYNTH_INSTRUCTOR_PARSE_FAILED | Fatal | LLM output failed Pydantic parsing after 2 retries | Produce diagnostic entry |
| SYNTH_POSITION_COUNT_ZERO | Fatal | Phase 2 identified 0 positions from non-empty excerpt set | Retry with explicit prompt; if persists, diagnostic entry |

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

**Code:** 0 lines of engine logic. No processing code exists.

**Contracts:** `engines/synthesis/contracts.py` — 539 lines. Defines all Pydantic models for input, output, and intermediate schemas. Models align with this SPEC as of this revision. Specific alignment notes:
- `EntryContent` model includes `common_misunderstandings` field present in contracts but not explicitly in the §3.2 schema example → added to §3.2 for consistency.
- `Citation` model uses flat fields (`excerpt_id`, `source_title`, `author_name`, `tahqiq_editor`, `publisher`, `volume`, `page_start`, `page_end`) rather than the nested `source_citation` object shown in §3.3 → contracts.py is authoritative; §3.3's nested structure is illustrative.
- `KhilafClassificationType` enum has `mu_tabar` and `shadh` for Phase 2 pairwise classification (§4.A.3 Step 2). `DisagreementLocusType` enum has `lafzi`, `ishtiraki`, `haqiqi`, `su_al_mukhtalif` for §4.B.5 full disambiguation. These are distinct enums for distinct purposes.
- `ClaimAttribution.attributed_excerpt_ids` allows `min_length=0` (for claims routed to analytical layer). This matches §4.A.4.1 Step 2 behavior.

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
- [NOT YET IMPLEMENTED] All 6 §4.B transformative capabilities.

---

## 10. Test Requirements

### 10.1 Mandatory Test Coverage

**Gold baseline generation tests.** For each supported science (starting with nahw), create at least 2 gold baseline entries: one from a simple leaf (2-3 excerpts, one school) and one from a complex leaf (7+ excerpts, 3+ schools, disagreements). Tests verify: all positions present, all attributions correct, all citations valid, khilaf classification correct.

**Integrity check tests.** Each of the 8 integrity checks in §4.A.5 must have a test case with a deliberately flawed entry that the check should catch. Verify the check fires and the entry is rejected.

**School isolation tests.** Generate entries for a fiqh leaf with 3+ schools. Verify no cross-school contamination.

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
