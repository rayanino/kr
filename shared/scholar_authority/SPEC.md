# Scholar Authority — سجل العلماء — Specification

## 1. Purpose and Scope

The scholar authority component maintains the canonical identity registry for every scholar encountered across all sources in the library. A scholar record is the single source of truth for the question "who is this person?" — their canonical name, variant spellings, biographical data, school affiliations, teacher-student relationships, known works, and scholarly standing. Every engine that references a scholar — source, excerpting, taxonomy, synthesizing — resolves that reference through this registry.

**What this component does.** It provides five capabilities: (1) registry management — creating, reading, updating, and querying scholar records with thread-safe concurrent access, (2) record matching — determining whether a name encountered in a source or excerpt refers to an existing scholar or a new one, using multi-signal disambiguation that handles the pervasive ambiguity of Arabic scholarly names, (3) progressive enrichment — accumulating biographical data across sources so that every new source mentioning a scholar may add details the registry didn't previously have, (4) graph maintenance — maintaining the teacher-student relationship graph as a first-class queryable data structure, not just metadata fields on individual records, and (5) external enrichment integration — querying OpenITI metadata, Wikidata, and LLM inference to bootstrap and enrich scholar records beyond what any single source provides.

**What is NOT this component's responsibility.** The scholar authority component does not create scholar records unprompted — it creates them only when called by another engine (primarily the source engine during intake, secondarily the excerpting engine when it encounters a quoted scholar). It does not decide which scholars are "important" — every scholar encountered gets a record. It does not perform text analysis or NLP — it receives structured scholar data (names, dates, affiliations) from calling engines and manages the registry. It does not manage works (the work registry is the source engine's responsibility) or sources.

**Phase classification.** The scholar authority component serves all pipeline phases. Phase 1 (source intake) is the primary write path — the source engine creates most records during intake. Phase 2 (excerpting) is a secondary write path — the excerpting engine adds quoted-scholar references. The synthesizing engine and scholar interface are the primary read paths.

**User scenarios served:**
- **Scenario 2** (Active Study): The scholar interface displays scholar profiles (biography, teachers, students, school) when the owner studies excerpts. These profiles come from this registry.
- **Scenario 3** (Cross-Science Insight): Teacher-student chains that connect scholars across sciences are stored here. The synthesizer traverses these chains to build intellectual genealogy narratives.
- **Scenario 4** (Scholarly Production): When the owner writes a research paper, the scholar interface helps with precise attribution — "which Ibn Hajar?" is answered by this registry.
- **Scenario 6** (New Book Briefing): The author profile in the book briefing (D-022) draws entirely from this registry. "Who is ابن عابدين?" is answered here: full name, dates, school, teachers, students, standing, known works.

## 2. Input Contract

The scholar authority component receives input from three calling engines through a programmatic interface (function calls, not file exchange).

**Record creation requests.** The source engine calls the creation interface with a structured scholar data payload containing: `name_arabic` (required — the Arabic name as encountered in the source), `name_variants` (optional — additional name forms extracted from the source), `kunya` (optional), `laqab` (optional), `nisba` (optional — array of nisbas), `death_date_hijri` (optional — integer), `death_date_ce` (optional — integer), `death_date_approximate` (optional — boolean), `birth_date_hijri` (optional), `birth_date_ce` (optional), `geographic_origin` (optional), `geographic_active` (optional — array), `school_affiliations` (optional — map of science → school), `teachers` (optional — array of canonical_ids or name strings), `students` (optional — array of canonical_ids or name strings), `known_works` (optional — array of work_ids or title strings), `scholarly_standing` (optional — free-text assessment), `methodology_notes` (optional), `source_of_data` (required — one of `source_extraction`, `llm_inference`, `openiti_metadata`, `wikidata`, `owner_input`, `excerpting_discovery`), and `requesting_source_id` (required — the source_id that triggered this creation). Validation: `name_arabic` must be non-empty. `source_of_data` must be a recognized value. `requesting_source_id` must be non-empty. All other fields are optional — records may start with only a name and grow richer through progressive enrichment.

**Record enrichment requests.** Any engine may call the enrichment interface with: `canonical_id` (required — the scholar to enrich), a partial scholar data payload containing only the fields to update, and `source_of_data` (required). The enrichment interface does not overwrite existing values by default — it adds to arrays (name_variants, teachers, students, known_works, nisbas) and fills empty scalar fields. If a scalar field already has a value and the enrichment provides a different value, the conflict is recorded in the scholar's `revision_history` and a human gate checkpoint is created (§7, error `SCHOLAR_FIELD_CONFLICT`).

**Record lookup requests.** Any engine may query the registry by: `canonical_id` (exact lookup), `name_arabic` (fuzzy matching against canonical name and all variants), `death_date_hijri` (range query), `school_affiliations` (filter by science+school), or combinations thereof. The lookup interface returns either a single matched record, a ranked list of candidates with match scores, or an empty result.

**Quoted-scholar discovery requests.** The excerpting engine calls this interface when it encounters a scholar reference in excerpt text. The payload contains: `name_as_cited` (required — the name as it appears in the text), `context_science` (required — the science of the source), `context_school` (optional — the school of the source), `context_century_hijri` (optional — the approximate century), and `citing_excerpt_id` (required). The component attempts to resolve the reference to an existing canonical_id. Resolution outcomes are defined in §4.A.2.

**Validation on all inputs.** Empty `name_arabic` on creation → reject with error `SCHOLAR_EMPTY_NAME`. Unrecognized `source_of_data` → reject with error `SCHOLAR_INVALID_DATA_SOURCE`. Enrichment targeting a non-existent `canonical_id` → reject with error `SCHOLAR_NOT_FOUND`. Malformed date values (negative, > 1500 for hijri) → reject with error `SCHOLAR_INVALID_DATE`.

## 3. Output Contract

The scholar authority component produces two categories of output: individual scholar records returned via the programmatic interface, and the persistent registry files on disk.

**Scholar record structure.** Every record conforms to this schema:

```
{
  "canonical_id": "sch_{5_digit_sequence}",
  "canonical_name_ar": "عمرو بن عثمان بن قنبر",
  "known_as": ["سيبويه"],
  "name_variants": ["سيبويه", "سيبويه البصري", "أبو بشر عمرو بن عثمان"],
  "kunya": "أبو بشر",
  "laqab": [],
  "nisba": ["البصري", "الفارسي"],
  "birth_date_hijri": null,
  "birth_date_ce": null,
  "death_date_hijri": 180,
  "death_date_ce": 796,
  "death_date_approximate": false,
  "era_century_hijri": 2,
  "geographic_origin": "شيراز",
  "geographic_active": ["البصرة"],
  "school_affiliations": {
    "nahw": "بصري",
    "fiqh": null,
    "aqidah": null
  },
  "teachers": ["sch_00002"],
  "students": ["sch_00003"],
  "known_works": ["wrk_sibawayhi_kitab"],
  "scholarly_standing": "founder of systematic Arabic grammar",
  "methodology_notes": null,
  "career_phases": [],
  "disambiguation_rules": [],
  "sources_encountered_in": ["src_a1b2c3d4"],
  "encounter_count": 1,
  "record_completeness": 0.65,
  "data_provenance": [
    {"field": "death_date_hijri", "source": "openiti_metadata", "timestamp": "..."}
  ],
  "revision_history": [],
  "external_ids": {
    "openiti_uri": "0180Sibawayh",
    "wikidata_qid": null
  },
  "created_at": "2026-03-04T12:00:00Z",
  "last_updated": "2026-03-04T12:00:00Z"
}
```

**Output guarantees.** (1) `canonical_id` is unique across the entire registry and never reassigned. Once a scholar receives an ID, that ID refers to that scholar permanently, even if the record is later merged with another. (2) `canonical_name_ar` is always non-empty. (3) `name_variants` always includes `canonical_name_ar` and all values from `known_as`. (4) `era_century_hijri` is always computed from `death_date_hijri` when available. (5) `record_completeness` is a float 0.0–1.0 computed from the proportion of non-null fields, weighted by field importance (death_date and school_affiliations weigh more than geographic_origin). (6) `data_provenance` traces every field to its source — this enables the synthesizer to judge metadata reliability and enables the owner to understand where biographical data came from.

**Registry files.** The persistent registry is stored at `library/registries/scholars.json` (the record array) and `library/registries/scholar_graph.json` (the teacher-student relationship graph). The graph file is a separate structure because it is queried differently from individual records — path traversal, connected components, and chain discovery are graph operations that don't map well to record-level access. Both files are written atomically (write to temp file, then rename) to prevent corruption from interrupted writes.

**Metadata pass-through (D-023).** The scholar authority component produces metadata that flows to the synthesizer. The synthesizer reads scholar records by `canonical_id` to access: full name, death dates (for chronological ordering), school affiliations (for school-grouped entries), teachers/students (for intellectual genealogy narrative), scholarly standing (for contextualizing positions), career phases (for handling retractions and position changes), and known works (for cross-referencing). The component adds `record_completeness` and `data_provenance` so the synthesizer can distinguish high-confidence biographical data from sparse, uncertain records.

## 4. Processing Specification

### §4.A — Core Processing

#### §4.A.1 — Record Creation

When a calling engine requests creation of a new scholar record, the component first checks whether the scholar already exists in the registry by running the matching algorithm (§4.A.2). The creation workflow proceeds as follows:

**Step 1: Name normalization.** The input `name_arabic` is normalized using CAMeL Tools' Arabic text normalization: Alef variants unified (أ، إ، آ → ا), Taa Marbuta/Haa unified at word boundaries (ة/ه), diacritics stripped for matching purposes (the original diacritized form is preserved in `name_variants`), and hamza variants normalized. The normalized form is used only for matching — the canonical display name retains the original Arabic spelling.

**Step 2: Candidate search.** The normalized name is compared against all existing records' normalized name variants. Initial candidates are selected using character-level trigram overlap with a minimum threshold of 0.4 (deliberately low to avoid missing matches on short names). This is a blocking step that reduces the comparison space — the full matching algorithm (§4.A.2) runs only on these candidates.

**Step 3: Full matching.** Each candidate is scored by the multi-signal matching algorithm (§4.A.2). Results fall into three ranges:
- Score ≥ 0.85: auto-match. The input is linked to the existing record. The calling engine receives the existing `canonical_id`. Any new data in the creation request is applied as enrichment (§4.A.3).
- Score 0.50–0.85: ambiguous match. A human gate checkpoint is created (gate type `SCHOLAR_DISAMBIGUATION`). The checkpoint payload contains: the new scholar data, the candidate records with scores, and the match signals that contributed to each score. The calling engine receives a provisional `canonical_id` (a new record is created) with `disambiguation_pending: true`. If the owner resolves the checkpoint by confirming a match, the provisional record is merged into the existing one (§4.A.4). If the owner confirms it's a new scholar, the provisional record becomes permanent.
- Score < 0.50: no match. A new record is created.

**Step 4: ID assignment.** New records receive a `canonical_id` in the format `sch_{5_digit_sequence}`. The sequence is monotonically increasing and never reused. The next available ID is tracked in a metadata field in `scholars.json`. ID assignment is atomic — two concurrent creation requests will never receive the same ID.

**Step 5: External enrichment.** After record creation, the component asynchronously queries external enrichment sources (§4.A.5) to fill gaps in the new record. Enrichment results are applied as updates with their respective `source_of_data` tags.

**Step 6: Persistence.** The new record is appended to `scholars.json` and any teacher-student relationships are added to `scholar_graph.json`. Both writes are atomic.

#### §4.A.2 — Record Matching and Disambiguation

Record matching determines whether a scholar name refers to an existing registry entry. This is the most critical operation in the component because a wrong match (merging two different scholars) is harder to fix than a wrong non-match (creating a duplicate). The matching algorithm therefore has a conservative bias: it prefers creating potential duplicates over merging distinct scholars.

**Matching signals.** The algorithm computes a weighted composite score from up to five signals:

**Signal 1: Name similarity (weight 0.35).** The input name is compared against all `name_variants` of the candidate record. Comparison uses the best of three string similarity metrics: (a) Jaro-Winkler distance on the full name string, (b) component-wise matching — decompose both names into ism/nasab/kunya/laqab/nisba components (using heuristic Arabic name parsing) and compare corresponding components, (c) known_as matching — exact match against the `known_as` array. The highest score among the three methods is used. Component-wise matching gets a 0.1 bonus when the death-date nisba (e.g., "البصري") matches, because nisbas are strong identity signals. Name similarity alone cannot produce an auto-match — even a perfect name match requires at least one corroborating signal, because many scholars share names.

**Signal 2: Death date proximity (weight 0.25).** If both the input and candidate have death dates, the score is computed as: `1.0 - min(abs(input_date - candidate_date) / 50, 1.0)`. Scholars with death dates within 5 years score ≥ 0.90. Scholars more than 50 years apart score 0.0. If either date is missing, this signal contributes 0.0 and its weight is redistributed to name similarity and school affiliations.

**Signal 3: School affiliation overlap (weight 0.15).** For each science where both the input and candidate have school affiliations, an exact match contributes 1.0 and a mismatch contributes 0.0. The score is the average across all shared sciences. If no shared sciences exist, this signal contributes 0.0 and its weight is redistributed. A school mismatch on a shared science is a strong negative signal — it multiplies the composite score by 0.7 because it is rare for two records of the SAME scholar to disagree on school affiliation (more likely they are different scholars).

**Signal 4: Known works overlap (weight 0.15).** The input's known works (by work_id or normalized title) are compared against the candidate's. Each matching work contributes proportionally. Even a single matching work is a strong positive signal (0.8 for one match, 1.0 for two+). If no works are available on either side, this signal contributes 0.0 and its weight is redistributed.

**Signal 5: Teacher-student overlap (weight 0.10).** If the input claims teachers or students that match the candidate's teachers or students, this is a strong corroborating signal. Any single overlap scores 1.0. If no teacher/student data is available, this signal contributes 0.0 and its weight is redistributed.

**Weight redistribution.** When a signal is unavailable (missing data), its weight is distributed proportionally to the available signals. The composite score is always normalized to 0.0–1.0 regardless of how many signals are available. However, if only name similarity is available (all other signals are missing), the maximum achievable score is capped at 0.65 — below the auto-match threshold — to prevent auto-matching on name alone.

**Disambiguation rules.** The registry may contain explicit disambiguation rules for commonly confused scholars. Each rule has the form: `{"ambiguous_name": "ابن حجر", "context_signal": {"science": "hadith"}, "resolves_to": "sch_00042", "note": "In hadith context, ابن حجر = al-Asqalani (d. 852 AH)"}`. When a lookup or match query provides context (science, century), disambiguation rules are checked first. A matching rule overrides the general matching algorithm and returns the specified `canonical_id` directly. Disambiguation rules are created by the owner (through human gate resolutions) or by the component itself when it detects a recurring ambiguity pattern.

#### §4.A.3 — Progressive Enrichment

Scholar records grow richer over time as more sources mention the same scholar. Progressive enrichment is the mechanism by which new information is incorporated into existing records without losing previous data.

**Enrichment rules by field type:**

**Array fields** (`name_variants`, `nisba`, `teachers`, `students`, `known_works`, `geographic_active`, `sources_encountered_in`): New values are appended if not already present (deduplication by exact match for IDs, normalized match for name strings). No existing values are removed.

**Empty scalar fields** (`birth_date_hijri`, `death_date_hijri`, `kunya`, `geographic_origin`, `scholarly_standing`, `methodology_notes`): A non-null enrichment value fills the empty field. The `data_provenance` array records the source of the new value.

**Occupied scalar fields:** If an enrichment provides a different value for a field that already has data, the component does NOT overwrite. Instead: (a) the conflict is recorded in `revision_history` with both values and their provenance, (b) if the conflicting field is `death_date_hijri` or `canonical_name_ar` (high-impact fields), a human gate checkpoint is created (type `SCHOLAR_FIELD_CONFLICT`), (c) for lower-impact fields (geographic_origin, methodology_notes), the conflict is logged but no checkpoint is created — the original value stands until the owner manually corrects it.

**Map fields** (`school_affiliations`): Enrichment can add new science→school mappings but cannot overwrite existing ones. A conflict (same science, different school) triggers a human gate checkpoint because school affiliation directly affects synthesis grouping.

**`encounter_count` and `sources_encountered_in`:** Updated on every enrichment call, regardless of whether any fields changed. This tracks how many sources mention this scholar — a high encounter count with a low record completeness suggests the scholar is well-known but biographical data is sparse (a signal that external enrichment should be prioritized).

**`record_completeness` recalculation.** After every enrichment, the completeness score is recomputed. Field weights: `death_date_hijri` (0.15), `school_affiliations` with at least one entry (0.15), `teachers` non-empty (0.10), `students` non-empty (0.10), `known_works` non-empty (0.10), `scholarly_standing` non-empty (0.10), `kunya` non-empty (0.05), `nisba` non-empty (0.05), `geographic_origin` non-empty (0.05), `birth_date_hijri` (0.05), `geographic_active` non-empty (0.05), `methodology_notes` non-empty (0.05). Sum of weights for non-null fields = completeness score.

#### §4.A.4 — Record Merging

When the owner or the matching algorithm determines that two records refer to the same scholar, the records must be merged. Merging is irreversible — it is always mediated by a human gate checkpoint except when one record is provisional (created during ambiguous-match resolution) and the owner confirms the match.

**Merge procedure.** Given a surviving record (the one that keeps its `canonical_id`) and a deprecated record (the one that will be absorbed):

1. All array fields from the deprecated record are merged into the surviving record (union, no duplicates).
2. Empty scalar fields in the surviving record are filled from the deprecated record.
3. Occupied scalar fields where both records have values: the surviving record's value is kept. The deprecated record's value is stored in `revision_history` with the merge event.
4. The deprecated record's `canonical_id` is added to a `merged_into` redirect table in the registry. Any engine holding the deprecated `canonical_id` will be redirected to the surviving record. The redirect is permanent — deprecated IDs are never reassigned.
5. All references to the deprecated `canonical_id` across the library (in source metadata, excerpt metadata, graph edges) are updated to the surviving `canonical_id`. This is a cascading update — the component emits a `SCHOLAR_MERGED` event that triggers reference updates in all consuming engines.
6. The deprecated record is moved to an archive section of the registry. It is not deleted — it preserves the audit trail.

**Merge direction.** When both records are permanent (not provisional), the surviving record is the one with higher `record_completeness`. If completeness is equal, the one with the lower (earlier) `canonical_id` survives.

#### §4.A.5 — External Enrichment Sources

The component integrates with three external data sources to bootstrap and enrich scholar records. External data never overwrites library-derived data — it supplements and fills gaps.

**Source 1: OpenITI Metadata (primary enrichment source).**

The OpenITI corpus organizes texts using CTS-compliant URIs that encode author death date and name slug (e.g., `0505Ghazali.IhyaCulumDin`). The component maintains a local copy of the OpenITI metadata TSV (from GitHub releases, ~50MB), indexed by normalized author name and death date for fast lookup. Matching uses: normalized Latin-script author slug compared against a transliterated version of the scholar's Arabic name (using CAMeL Tools transliteration), plus death date proximity (±25 years). When a match is found, the component extracts: confirmed death date, the full list of known works by this author in OpenITI (as title strings for work registry matching), and the CTS URI. The OpenITI URI is stored in `external_ids.openiti_uri` for future direct reference.

Update frequency: quarterly, matching OpenITI's release cycle. The metadata TSV is cached locally at `library/enrichment/openiti_metadata.tsv`. A background process checks for new releases.

**Source 2: Wikidata (supplementary enrichment).**

For scholars with sufficient identifying information (name + approximate death date), the component queries Wikidata's SPARQL endpoint to find matching entities. The query filters on: `instance_of: Q5` (human), `occupation` includes `Q13200659` (Islamic scholar) or related occupations, Arabic label or alias matches the scholar name, and `date_of_death` is within range. When a match is found, the component extracts: birth/death dates, place of birth/death, notable works (as Wikidata QIDs for future linking), teacher/student relationships (P1066 student of, P802 student), school of thought, and the Wikidata QID stored in `external_ids.wikidata_qid`.

Wikidata coverage of Islamic scholars is incomplete — many classical scholars have no Wikidata entry. The component treats Wikidata as opportunistic enrichment: useful when available but never depended on.

**Source 3: LLM Inference (bootstrapping enrichment).**

When a scholar record is created with minimal data (just a name and perhaps a death date), the component queries an LLM with a structured prompt asking for biographical details. The prompt includes the scholar name, any available context (source title, science), and instructs the model to output structured JSON with: full name components (ism, nasab, kunya, laqab, nisba), death date (hijri and CE), school affiliations per science, known teachers and students, major works, scholarly standing, and geographic activity. The LLM's training data contains substantial knowledge of well-known Islamic scholars, making this effective for the majority of scholars the owner will encounter in early library building.

LLM inference results are tagged with `source_of_data: "llm_inference"` and a confidence level. High-confidence LLM data (well-known scholars like سيبويه, ابن مالك, النووي) fills fields reliably. Low-confidence data (obscure scholars, disputed details) is stored but flagged as uncertain in `data_provenance`. The synthesizer uses provenance to decide how much weight to give biographical claims in entries.

**Enrichment priority.** When a new record is created: (1) OpenITI is queried first (fastest, most reliable for premodern scholars), (2) LLM inference runs second (fills remaining gaps), (3) Wikidata is queried last (slowest due to SPARQL endpoint latency). Results from each source are applied in order, with later sources filling only remaining gaps.

#### §4.A.6 — Teacher-Student Graph

Teacher-student relationships are stored as a directed graph separate from individual scholar records. This graph is a first-class data structure maintained by the scholar authority component, not just metadata arrays on scholar records. The rationale: graph queries (path finding, connected components, chain discovery) are fundamentally different from record lookups, and the synthesizer's intellectual genealogy narrative (see ENTRY_EXAMPLE.md) requires efficient chain traversal.

**Graph structure.** The graph is stored at `library/registries/scholar_graph.json` as an adjacency list:

```
{
  "edges": [
    {
      "from": "sch_00001",  // teacher
      "to": "sch_00003",    // student
      "relationship": "teacher_of",
      "science": "nahw",    // optional: the science context of the relationship
      "confidence": 0.95,
      "source_of_data": "openiti_metadata",
      "discovered_in_source": "src_a1b2c3d4"
    }
  ],
  "metadata": {
    "node_count": 42,
    "edge_count": 87,
    "last_updated": "2026-03-04T12:00:00Z"
  }
}
```

**Edge creation.** When a scholar record's `teachers` or `students` array is updated (during creation or enrichment), corresponding edges are created in the graph. Edges are bidirectional in meaning (if A taught B, then B studied under A) but stored as directed edges from teacher to student. Duplicate edges (same from, to, science) are not created — the existing edge's confidence is updated to the maximum of the old and new confidence values.

**Edge properties.** Each edge carries: the science context (because a scholar may have studied one science under teacher A and another under teacher B), a confidence score (LLM-inferred relationships are lower confidence than source-extracted ones), and provenance (where was this relationship discovered). The `science` field is optional — some teacher-student relationships are general (the student studied multiple sciences under the teacher) and cannot be assigned to a single science.

**Graph queries.** The component exposes three graph query interfaces:

1. **Chain discovery.** Given a scholar `canonical_id` and a direction (ancestors/descendants), return all chains up to depth N (default: 5). Returns an array of paths, each path being an ordered list of `canonical_id` values. Used by the synthesizer for intellectual genealogy: "Sibawayhi → al-Akhfash → al-Jarmi → al-Mubarrad → Ibn al-Sarraj."

2. **Connection discovery.** Given two scholar `canonical_id` values, find all paths between them up to length M (default: 6). Returns paths if connected, empty if unconnected. Used by the synthesizer when two scholars at the same leaf have a chain connection.

3. **Subgraph extraction.** Given a set of scholar `canonical_id` values, return the induced subgraph — all edges between any pair in the set. Used by the synthesizer when generating an entry that cites multiple scholars: it extracts the relationships among those specific scholars.

**Graph integrity.** Cycles in the teacher-student graph indicate data errors (a scholar cannot be their own teacher's teacher's teacher's student). The component runs cycle detection after every edge addition. If a cycle is detected, the newly added edge is flagged (not added to the graph) and a human gate checkpoint is created (type `SCHOLAR_GRAPH_CYCLE`) for the owner to resolve.

#### §4.A.7 — Career Phase Modeling

Some scholars changed positions over their lifetimes — most famously, الشافعي had a "Baghdadi" period (القول القديم) and an "Egyptian" period (القول الجديد) with significantly different rulings. The scholar authority component models career phases as structured data on the scholar record, enabling the synthesizer to handle retractions correctly (D-033: retraction blindness is a scholarly integrity risk).

**Career phase structure:**

```
{
  "phase_id": "phase_01",
  "label_ar": "القول القديم",
  "label_en": "early_baghdad",
  "start_date_hijri": null,
  "end_date_hijri": 199,
  "location": "بغداد",
  "school_affiliations": {"fiqh": "شافعي"},
  "notes": "Positions held during al-Shafi'i's time in Baghdad before his move to Egypt",
  "superseded_by": "phase_02",
  "source_of_data": "llm_inference"
}
```

**When phases are created.** Career phases are created when: (1) the source engine or LLM inference identifies that a scholar is known for having changed positions, (2) the excerpting engine encounters explicit textual markers of phase distinction (e.g., "قال في القديم... وقال في الجديد"), or (3) the owner manually creates phases through the human gate. Most scholars have no career phases — the `career_phases` array is empty by default.

**How phases are used.** The synthesizer checks `career_phases` for every scholar it cites. If a scholar has phases and an excerpt can be dated to a specific phase (via composition date of the source or explicit textual markers), the synthesizer notes which phase the position comes from and whether it was later superseded. The `superseded_by` field creates a chain: early → late, and the synthesizer presents the latest phase's positions as primary with earlier phases as historical context. If an excerpt cannot be assigned to a specific phase, the synthesizer notes the uncertainty.

#### §4.A.8 — Serving Interface

The scholar authority component exposes a read-only serving interface for consuming engines. This interface is optimized for the two most common access patterns: single-record lookup by `canonical_id` (used by the synthesizer for each excerpt it processes) and batch lookup by multiple `canonical_id` values (used by the synthesizer when generating an entry that cites many scholars).

**Single-record lookup.** Input: `canonical_id`. Output: the full scholar record. If the `canonical_id` is in the redirect table (from a merge), the redirect is followed transparently — the caller receives the surviving record. If the `canonical_id` does not exist and is not redirected, the interface returns `null` and logs a warning (this indicates a referential integrity issue).

**Batch lookup.** Input: array of `canonical_id` values. Output: map of `canonical_id` → scholar record. Redirects are followed. Missing IDs are returned as `null` entries in the map with warnings.

**Name resolution.** Input: `name_arabic` + optional context (science, century, school). Output: array of candidate records with match scores, sorted by score descending. This interface is for the excerpting engine's quoted-scholar resolution — it returns candidates, not a single answer, because the excerpting engine makes the final attribution decision.

**Graph queries.** Input: query type (chain/connection/subgraph) + parameters. Output: structured graph data (paths, subgraphs). These queries are served directly from the in-memory graph (loaded at component initialization).

**Caching.** The component maintains an in-memory cache of all scholar records (the registry is expected to be < 100MB even at scale — tens of thousands of records with ~1KB each). Cache is invalidated on any write operation. For read-heavy workloads (synthesis of many entries), the in-memory cache eliminates disk I/O per lookup.

### §4.B — Transformative Capabilities

#### §4.B.1 — Intellectual Genealogy as a Knowledge Product

**Capability:** The teacher-student graph is not just metadata for the synthesizer — it is a queryable knowledge product in its own right that enables the scholar interface to visualize and explore intellectual lineages across centuries.

**What this enables that was previously impossible:** No existing Islamic studies tool presents the full teacher-student network as an interactive, queryable graph. Tabaqat books (biographical dictionaries) list teachers and students per scholar entry, but the connections between entries must be manually traced. A researcher wanting to know "how did Sibawayhi's grammatical theory reach Ibn Malik 500 years later?" must read dozens of biographical entries and manually construct the chain. KR's graph answers this in milliseconds and visualizes the entire chain with dates, locations, and school affiliations at each node.

**Technical approach.** The graph is stored as a directed adjacency list (§4.A.6) and loaded into memory at component initialization. Chain discovery uses breadth-first search with depth limiting. Connection discovery uses bidirectional BFS. Subgraph extraction uses set intersection on adjacency lists. The graph library is pure Python using dictionary-based adjacency representation — no external graph database is needed at the expected scale (tens of thousands of nodes, hundreds of thousands of edges). If scale exceeds in-memory capacity in the future, migration to an embedded graph store (e.g., DuckDB with recursive CTEs, or NetworkX for analysis) is straightforward because the adjacency list format maps directly.

**Scholar interface integration.** The scholar interface can request: "show me the intellectual genealogy of ابن مالك" and receive a structured tree of his teachers, their teachers, and so on, back to the earliest scholars in the registry. Each node carries dates, locations, schools, and known works — enabling a visual timeline of how grammatical knowledge traveled from Basra in the 2nd century to Andalusia in the 7th century.

**Genealogy-enriched entries.** When the synthesizer processes a leaf where two or more scholars have a graph connection, it requests the connection paths and weaves them into the analytical layer. This is what produces the narrative in ENTRY_EXAMPLE.md: "Ibn al-Sarraj was a student of al-Mubarrad, who was himself a student of al-Jarmi, who studied with al-Akhfash — Sibawayhi's own student. This four-generation chain preserved and formalized Sibawayhi's original insight."

**Dependencies:** Requires the graph data structure (§4.A.6) and chain/connection queries. No external dependencies beyond Python standard library.

#### §4.B.2 — Scholarly Influence Network Analysis

**Capability:** The component computes quantitative influence metrics for scholars based on the graph structure (teacher-student edges) combined with work citation data (from the source engine's work relationship graph). These metrics enable the synthesizer and scholar interface to contextualize a scholar's importance within a specific science, century, or school.

**What this enables:** When the synthesizer generates an entry, it can say "سيبويه, the most influential Basran grammarian of the 2nd century AH" not as an LLM assertion but as a computed claim backed by graph data: Sibawayhi has the highest downstream student count in the nahw subgraph among 2nd-century scholars. The scholar interface can rank scholars by influence within a science, show how influence shifted between schools over centuries, and identify scholars who were bridges between traditions.

**Technical approach.** Three influence metrics are computed:

1. **Downstream reach.** For each scholar, count the number of unique scholars reachable by following student edges (with depth limit 10). This measures how many later scholars can trace their intellectual lineage back to this scholar. Computed using BFS from each node — expensive at scale but can be precomputed and cached, updating only when the graph changes.

2. **Citation influence.** For each scholar, count the number of works in the library that cite their works (using the work relationship graph's `cites` edges). This measures how widely referenced a scholar's writings are in the library. This metric is library-dependent — it reflects the library's composition, not absolute scholarly influence. The synthesizer must note this when using the metric: "the most cited Basran grammarian in this library" rather than "the most cited Basran grammarian in history."

3. **Bridging score.** For each scholar, compute betweenness centrality in the teacher-student graph restricted to a specific science. High betweenness indicates a scholar who connects otherwise disconnected clusters — a bridge between traditions. This identifies scholars like al-Akhfash al-Awsat, who studied under Basran Sibawayhi but also influenced Kufan-leaning scholars, serving as a bridge between the two schools.

**Precomputation.** Influence metrics are computationally expensive (especially betweenness centrality, which is O(V·E) for each node). They are computed in batch and cached at `library/registries/scholar_influence.json`. Recomputation is triggered when the graph changes by more than 10% (measured by edge count delta). For incremental changes (a few new edges), only the affected scholars' metrics are recomputed using incremental BFS.

**Dependencies:** Python standard library for BFS/DFS. NetworkX for betweenness centrality computation (already a common Python dependency, well-tested for graphs at this scale). Source engine's work relationship graph for citation data.

[NOT YET IMPLEMENTED] — Full specification provided; no code exists.

#### §4.B.3 — Automatic Disambiguation Rule Generation

**Capability:** When the component observes that the same ambiguous name is repeatedly resolved to different scholars depending on context, it automatically generates disambiguation rules that short-circuit future matching for that name.

**What this enables:** Arabic scholarly names are pervasively ambiguous. "ابن حجر" refers to al-Asqalani in hadith contexts and al-Haytami in Shafi'i fiqh contexts. "الإمام" means different scholars depending on the source's school. Manual disambiguation rules are valuable but don't scale — the library will encounter hundreds of ambiguous names. Automatic rule generation means the system learns disambiguation patterns from the owner's resolutions and applies them proactively.

**Technical approach.** The component tracks disambiguation events: every time a human gate checkpoint of type `SCHOLAR_DISAMBIGUATION` is resolved, the resolution is recorded with the ambiguous name, the resolved `canonical_id`, and the context signals (science, school, century, source). When the same ambiguous name has been resolved 3+ times with consistent context patterns (e.g., "ابن حجر" + hadith context → always resolves to sch_00042), the component generates a disambiguation rule and presents it to the owner for confirmation through a human gate checkpoint (type `SCHOLAR_DISAMBIGUATION_RULE_PROPOSAL`). If confirmed, the rule is added to the registry and future lookups with matching context are auto-resolved.

**Rule structure.** Each rule has: `ambiguous_name` (the name that triggers the rule), `context_conditions` (a set of signal→value conditions that must ALL be met), `resolves_to` (the `canonical_id` to resolve to), `confidence` (based on the consistency of historical resolutions), and `owner_confirmed` (boolean — rules only take effect after owner confirmation). Rules are stored in a `disambiguation_rules` array at the registry level (not per-scholar) for efficient lookup.

**Fallback.** Even with rules, the matching algorithm runs as a verification step — if the rule's resolution contradicts the matching algorithm's top candidate (unlikely but possible if the registry has changed since the rule was created), the conflict is flagged for human review.

**Dependencies:** No external dependencies. Uses the component's own resolution history and human gate integration.

[NOT YET IMPLEMENTED] — Full specification provided; no code exists.

## 5. Validation and Quality

The scholar authority component enforces data quality through three layers of validation.

**Layer 1: Self-validation (on every write operation).**

- **Referential integrity.** Every `canonical_id` referenced in `teachers`, `students`, and graph edges must exist in the registry (or in the redirect table). A write that would create a dangling reference is rejected with error `SCHOLAR_DANGLING_REFERENCE`.
- **Name non-emptiness.** `canonical_name_ar` must be non-empty on every record. A write that would clear it is rejected.
- **Date sanity.** `death_date_hijri` must be in range [1, 1500]. `birth_date_hijri` must be ≤ `death_date_hijri` when both are present. `death_date_ce` must be consistent with `death_date_hijri` within ±5 years (allowing for hijri-CE conversion ambiguity). Violations trigger a warning (not rejection) because source data may contain errors — the invalid date is stored with a `data_quality_flag`.
- **Graph acyclicity.** Every new edge in the teacher-student graph is checked for cycles (§4.A.6).
- **Temporal consistency.** A teacher must have a death date ≥ the student's birth date (when both are available). If a new teacher-student edge violates this, it is flagged (not rejected — biographical dates may be approximate).

**Layer 2: Automated quality checks (periodic batch validation).**

- **Duplicate detection.** A periodic sweep runs the matching algorithm (§4.A.2) on all record pairs with name similarity > 0.7 and no existing merge/disambiguation history. Potential duplicates are flagged for human review. Frequency: after every 50 new records or weekly, whichever comes first.
- **Completeness audit.** Records with `record_completeness` < 0.3 and `encounter_count` > 5 are flagged as "well-known but poorly documented" — candidates for targeted enrichment. The component queues external enrichment (§4.A.5) for these records.
- **Orphan detection.** Records with `encounter_count` == 1 and `record_completeness` < 0.2 are candidates for merge review — they may be duplicates created from a single ambiguous encounter.

**Layer 3: Human gate integration.**

The component creates human gate checkpoints for: ambiguous matches (§4.A.1), field conflicts (§4.A.3), graph cycles (§4.A.6), disambiguation rule proposals (§4.B.3), and merge proposals from duplicate detection. The owner's resolutions are recorded and used to improve future matching (via disambiguation rules and enrichment). The human gate ensures that the owner always has final authority over scholar identity — the component makes proposals and carries out decisions, but never overrides the owner on identity questions.

**Scholarly integrity safeguard.** A wrong scholar identity cascades through the entire library: if ابن حجر العسقلاني is confused with ابن حجر الهيتمي, every excerpt attributed to either scholar may be misplaced, every entry citing either may be wrong, and the teacher-student graph may contain false connections. The conservative bias in matching (§4.A.2) and the human gate for ambiguous cases are the primary defenses. Additionally, the component tracks `data_provenance` per field, so if a biographical claim is later found to be wrong (the death date came from a bad LLM inference), the correction can be precisely targeted.

## 6. Consensus Integration

This component does NOT use multi-model consensus. The rationale: scholar identity resolution is fundamentally a data matching problem, not a content analysis problem. The matching algorithm (§4.A.2) uses deterministic signals (name similarity, date proximity, school overlap) that don't benefit from multiple LLM opinions. The one LLM-dependent operation — biographical enrichment via LLM inference (§4.A.5) — uses a single model because: (a) the data is bootstrapping information (names, dates, schools) for which LLM training data is highly consistent across models, and (b) the enrichment is always tagged with its source and never overwrites library-derived data, so errors are low-impact and correctable.

If future experience reveals that LLM-inferred biographical data has significant error rates for less well-known scholars, consensus could be added specifically for the enrichment step. This would be a targeted addition, not a systemic change — the matching algorithm itself should never use consensus because it needs deterministic, reproducible results.

## 7. Error Handling

**Error codes and severity:**

| Code | Severity | Trigger | Recovery |
|------|----------|---------|----------|
| `SCHOLAR_EMPTY_NAME` | Fatal | Creation request with empty `name_arabic` | Reject request, return error to caller |
| `SCHOLAR_INVALID_DATA_SOURCE` | Fatal | Unrecognized `source_of_data` value | Reject request, return error to caller |
| `SCHOLAR_NOT_FOUND` | Warning | Enrichment/lookup targets non-existent ID | Return null, log warning |
| `SCHOLAR_INVALID_DATE` | Warning | Date outside valid range | Store with `data_quality_flag`, log warning |
| `SCHOLAR_FIELD_CONFLICT` | Info | Enrichment provides different value for occupied scalar field | Record in revision_history; create human gate checkpoint for high-impact fields |
| `SCHOLAR_DANGLING_REFERENCE` | Fatal | Write would create reference to non-existent ID | Reject write, return error |
| `SCHOLAR_GRAPH_CYCLE` | Warning | New edge would create cycle in teacher-student graph | Do not add edge, create human gate checkpoint |
| `SCHOLAR_DISAMBIGUATION` | Info | Matching score in ambiguous range (0.50–0.85) | Create provisional record + human gate checkpoint |
| `SCHOLAR_MERGE_CONFLICT` | Warning | Merge encounters conflicting scalar values | Keep surviving record's values, archive deprecated values |
| `SCHOLAR_ENRICHMENT_FAILED` | Info | External enrichment source unreachable or returned error | Log, continue without enrichment. Retry on next opportunity. |
| `SCHOLAR_TEMPORAL_INCONSISTENCY` | Warning | Teacher died before student was born | Flag edge, do not remove (dates may be approximate) |
| `SCHOLAR_WRITE_FAILED` | Fatal | Disk write failed (permission, space) | Return error to caller. No partial writes — atomic operations ensure registry consistency. |

**Logging.** All errors are logged to `library/registries/scholar_authority.log` with timestamp, error code, affected `canonical_id` (if applicable), and the full request payload. Fatal errors are also written to the pipeline-wide error log for monitoring.

**Principle: never lose data silently (D-033).** Every conflict, every ambiguity, every failed enrichment is recorded. If a record is created as a potential duplicate (ambiguous match), the ambiguity is tracked until resolved. If enrichment fails, the failure is logged so it can be retried. If a field conflict is detected, both values are preserved. The component never silently drops information or silently resolves ambiguity.

## 8. Configuration

**Matching thresholds:**
- `auto_match_threshold`: 0.85 (score above which a match is auto-confirmed). Range: [0.7, 1.0]. Raising this creates more human gate checkpoints but reduces false merges.
- `ambiguous_match_threshold`: 0.50 (score above which a match is considered ambiguous). Range: [0.3, 0.7]. Lowering this creates more human gate checkpoints for weak matches.
- `name_only_cap`: 0.65 (maximum score when only name similarity is available). Range: [0.5, 0.85]. Must be below `auto_match_threshold`.
- `blocking_trigram_threshold`: 0.4 (minimum trigram overlap for candidate selection). Range: [0.2, 0.6]. Lowering catches more candidates but increases comparison count.

**Enrichment configuration:**
- `openiti_metadata_path`: `library/enrichment/openiti_metadata.tsv`. Path to the cached OpenITI metadata file.
- `wikidata_enabled`: true. Whether to query Wikidata for enrichment. Set to false if network access is unavailable.
- `llm_enrichment_enabled`: true. Whether to use LLM inference for bootstrapping.
- `llm_enrichment_model`: Configurable (default: the pipeline's primary model). The model used for biographical inference.
- `enrichment_retry_interval_hours`: 24. How often to retry failed external enrichments.

**Graph configuration:**
- `max_chain_depth`: 10. Maximum depth for chain discovery queries.
- `max_connection_path_length`: 6. Maximum path length for connection queries.
- `influence_recompute_threshold`: 0.10. Graph change threshold (fraction of edge count) that triggers influence metric recomputation.

**Duplicate detection:**
- `duplicate_sweep_interval`: 50 (new records) or 7 (days), whichever comes first.
- `duplicate_name_similarity_threshold`: 0.7. Minimum name similarity for duplicate candidate pairs.

**Per-science configuration hooks (SCIENCE.md Level 3):** Individual SCIENCE.md files may specify: (a) which schools exist for that science (used to validate `school_affiliations` entries), (b) known ambiguous names specific to that science (seeded into disambiguation rules), (c) periodization conventions (century boundaries differ between sciences in some scholarly traditions).

## 9. Current Implementation State

**Existing files:** None. This is a new shared component with no ABD predecessor and no existing code.

**Directory structure (to be created by Claude Code):**
```
shared/scholar_authority/
├── CLAUDE.md                  # Existing orientation file
├── SPEC.md                    # This specification
├── src/
│   ├── registry.py            # Core registry (CRUD, matching, merging)
│   ├── graph.py               # Teacher-student graph (storage, queries)
│   ├── enrichment.py          # External enrichment (OpenITI, Wikidata, LLM)
│   ├── disambiguation.py      # Disambiguation rules (manual + auto-generated)
│   ├── name_normalization.py  # Arabic name normalization and comparison
│   ├── influence.py           # [NOT YET IMPLEMENTED] Influence metrics
│   └── serving.py             # Read-only serving interface + caching
└── tests/
    ├── test_registry.py
    ├── test_matching.py
    ├── test_graph.py
    ├── test_enrichment.py
    └── test_disambiguation.py
```

**Dependencies:**
- **CAMeL Tools** (from RESOURCES.md): Arabic text normalization, transliteration for OpenITI matching. `pip install camel-tools`.
- **NetworkX** (for §4.B.2 influence metrics): Graph analysis library. `pip install networkx`. Only needed for betweenness centrality computation; core graph operations use pure Python.
- **httpx** (for Wikidata SPARQL queries): Async HTTP client. `pip install httpx`. Only needed when `wikidata_enabled` is true.

**Known gaps:**
- [NOT YET IMPLEMENTED] Scholarly influence network analysis (§4.B.2) — specified but no code.
- [NOT YET IMPLEMENTED] Automatic disambiguation rule generation (§4.B.3) — specified but no code.
- [NOT YET IMPLEMENTED] Wikidata integration — specified but requires SPARQL query development and testing against live endpoint.
- OpenITI metadata TSV must be manually downloaded and placed at the configured path before the enrichment source can be used.
- The matching algorithm (§4.A.2) is specified in detail but the Arabic name decomposition heuristic (splitting a name into ism/nasab/kunya/laqab/nisba) needs implementation and testing against real scholarly name data. CAMeL Tools does not provide this specific functionality — it handles text normalization but not onomastic parsing. A custom heuristic using Arabic name patterns (ابن → nasab marker, أبو/أم → kunya marker, ال + nisba pattern → nisba) will need to be developed and validated.

## 10. Test Requirements

**Critical tests (MUST be tested):**

1. **Matching accuracy.** Create a test set of at least 20 scholar name pairs: 10 known matches (same scholar, different name forms) and 10 known non-matches (different scholars, similar names). The matching algorithm must correctly classify ≥ 18/20. Test cases must include the hardest disambiguation cases: "ابن حجر" (two scholars), "الإمام" in different contexts, scholars sharing a common nasab.

2. **Progressive enrichment.** Create a record with minimal data. Enrich it 5 times with overlapping and conflicting data. Verify: array fields accumulate correctly, empty scalars are filled, occupied scalar conflicts are recorded in revision_history, record_completeness increases monotonically, and data_provenance traces every field.

3. **Graph integrity.** Create 10 scholars with teacher-student relationships forming a tree. Verify chain discovery returns correct paths. Attempt to add an edge that creates a cycle — verify it is rejected and a human gate checkpoint is created. Verify connection discovery finds the path between any two connected scholars.

4. **Merge correctness.** Create two records for the same scholar with overlapping data. Merge them. Verify: the surviving record has the union of all data, the deprecated ID redirects correctly, all references to the deprecated ID are updated, and the deprecated record is archived.

5. **Name normalization.** Test with at least 15 Arabic name forms covering: hamza variants, taa marbuta/haa, diacritized and undiacritized forms, long names with multiple components, single-word names (laqabs). Verify normalized forms match correctly.

**Integration tests:**

6. **Source engine integration.** The source engine calls creation interface with author data from a processed source. Verify: record is created or matched, enrichment runs, the source engine receives a valid `canonical_id`.

7. **Excerpting engine integration.** The excerpting engine calls quoted-scholar resolution with a name from excerpt text + context. Verify: candidates are returned with scores, the correct scholar is the top candidate when context is sufficient.

8. **Synthesizer integration.** The synthesizer requests batch lookup of 20 scholar IDs. Verify: all records are returned with full data, redirected IDs are resolved transparently, graph queries for intellectual genealogy return correct chains.

**Gold baselines:** A gold baseline set of 50 well-known Islamic scholars (سيبويه, النووي, ابن تيمية, ابن حجر العسقلاني, etc.) with verified biographical data should be created from authoritative sources. This baseline serves dual purposes: (a) validating that the matching algorithm correctly handles the most common scholars, and (b) providing seed data for the registry during initial library setup.

**Regression testing:** Any change to the matching algorithm must be validated against the full test set of known matches and non-matches. Score changes > 0.05 on any pair require investigation and documentation.
