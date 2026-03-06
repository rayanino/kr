# Excerpting Engine — محرك الاقتطاف — Specification

## 1. Purpose and Scope

The excerpting engine transforms typed atoms into self-contained excerpts — coherent teaching units that are independently understandable, correctly attributed, and enriched with all metadata the synthesizing engine needs to produce scholarly entries. This is where KR's pipeline transitions from "text processing" to "knowledge products." Every excerpt that enters the library becomes part of Rayane's knowledge; a bad excerpt is a bad piece of knowledge.

**What this engine does:**

- Receives atom streams from the atomization engine.
- Groups atoms within each passage into candidate excerpt boundaries — contiguous atom sequences that form a coherent scholarly teaching unit.
- Evaluates each candidate for self-containment: can a reader with general familiarity of the science understand what this excerpt teaches, who said it, and from which scholarly tradition, without consulting any other excerpt? (§5.1 standard)
- Enriches each excerpt with metadata: author identification, school attribution, topic classification (proposed leaf), content type, quoted scholars, evidence references, hadith identification with grading status, terminology variants, and self-containment score.
- Produces draft excerpts consumed by the taxonomy engine for placement.

**What is NOT this engine's responsibility:**

- Breaking passages into atoms. That is the atomization engine's job. The excerpting engine receives pre-classified atoms with type information and embedded content detections.
- Placing excerpts in the taxonomy tree. That is the taxonomy engine's job. The excerpting engine proposes a leaf; the taxonomy engine confirms or redirects.
- Generating entries. That is the synthesizing engine's job. The excerpting engine produces the building blocks; the synthesizer weaves them into scholarly narratives.
- Modifying primary text. The excerpt's `primary_text` is assembled verbatim from atom texts. No word is changed (D-004).

**Phase:** 2 (source-agnostic, below the normalization boundary).

**User scenarios served (reference/USER_SCENARIOS.md):**

- Scenario 2 (Day 30 — Active Study): excerpts are what Rayane reads during study. Their self-containment and metadata quality directly determine study experience.
- Scenario 3 (Day 180 — Cross-Science Insight): cross-topic excerpt detection enables the scholar interface to surface connections between sciences.
- Scenario 6 (New Book Briefing): excerpt metadata (content types, evidence density, school coverage) contributes to book briefing data.
- Scenario 7 ("Show Me the Whole Science"): excerpts placed at taxonomy leaves, with their school and content type metadata, are the data that makes "show me the whole science" possible.
- Scenario 8 (KR Gets It Wrong): excerpt-level error correction is the primary correction mechanism. When the owner flags an error, the correction targets the excerpt's metadata (attribution, school, placement), and all entries using that excerpt are marked stale.

---

## 2. Input Contract

The excerpting engine receives atom streams from the atomization engine, located at `library/sources/{source_id}/atoms/atoms.jsonl`. Processing is per-passage: the engine loads all atoms for a passage, groups them, and produces excerpt records.

**What the engine expects from upstream:**

Each atom record conforms to the atom schema (`atom_v2.0`) as defined in the atomization engine SPEC §3. The excerpting engine reads the following fields:

- `atom_id`: string. Unique identifier. Used to compose the excerpt's `atom_ids` list and for provenance.
- `passage_id`: string. Parent passage. The excerpting engine processes all atoms sharing a `passage_id` together. An excerpt's atoms must all share the same `passage_id` (passage containment rule, D-011).
- `source_id`: string. Link to upstream source metadata.
- `sequence_in_passage`: int. Ordering within passage.
- `atom_text`: string. Verbatim text. Concatenated to form the excerpt's `primary_text`.
- `anchor_span`: object (`start`, `end`). Position in `passage_text`. Used for physical page attribution.
- `structural_type`: string enum. From the 7 structural types.
- `scholarly_function`: string enum or null. From the 16 scholarly functions.
- `function_confidence`: float. Classification confidence.
- `source_layer`: string. Authorial layer (`matn`, `sharh`, `hashiyah`, `tahqiq`, `footnote`). For single-layer sources, always `matn`.
- `layer_author_id`: string or null. Author's `canonical_id` for this layer.
- `embedded_refs`: array. Detected Quran, hadith, poetry, scholarly quote references with spans.
- `atom_relations`: array. Typed relationships between atoms (illustrates, evidences, conditions, refutes, etc.).
- `bonded_reason`: string or null. If this atom is a bonded cluster, the bonding reason.
- `review_flags`: array. Atomization review flags propagated to excerpt level.
- `classification_notes`: string or null. Explanation of classification decisions.

The excerpting engine also accesses:

- **Source metadata** via `source_id` reference: author biography, school affiliations, work genre, trust tier, text fidelity, work relationships. Accessed from `library/registries/sources.json` and `library/registries/scholars.json`.
- **Passage metadata** via `passage_id` reference: `division_path`, `physical_pages`, `structural_format`, `content_flags`, `text_layers`, `verse_info`. Accessed from the passage stream.

**Validation on input:**

1. At least one atom exists for the passage. Passages with zero atoms are skipped with warning `EXCERPT_EMPTY_PASSAGE`.
2. All atoms for a passage share the same `passage_id` and `source_id`. Inconsistent IDs are fatal: `EXCERPT_ID_MISMATCH`.
3. Atoms are ordered by `sequence_in_passage`. If not, the engine sorts them before processing and logs warning `EXCERPT_ATOMS_REORDERED`.
4. Source metadata is accessible via `source_id`. If the source metadata record cannot be found, the engine continues with degraded metadata enrichment (no author biography, no school hints) and adds review flag `source_metadata_unavailable`.

---

## 3. Output Contract

The excerpting engine produces one primary artifact per source: a draft excerpt stream.

**Primary artifact: the draft excerpt stream.**

Written to `library/sources/{source_id}/excerpts/excerpts.jsonl`. One JSONL record per excerpt. Each record conforms to the excerpt schema:

- `schema_version`: string. Current: `excerpt_v2.0`.
- `excerpt_id`: string, format `exc_{source_id}_{zero_padded_sequence}` (e.g., `exc_src_00147_000012`). Globally unique. Monotonically increasing within a source in document order.
- `source_id`: string. Source reference.
- `passage_id`: string. Parent passage. All atoms in this excerpt belong to this passage.
- `lifecycle_stage`: string. Always `draft` at output. Transitions to `reviewed` and `placed` are managed by the taxonomy engine and human gate.

**Atom composition:**

- `atom_ids`: array of strings. Ordered list of ALL atom IDs composing this excerpt, including both core and context atoms. Order matches reading order.
- `core_atom_ids`: array of strings. Atom IDs that substantively address the excerpt's topic — the "teaching content." These atoms carry the excerpt's primary scholarly contribution.
- `context_atom_ids`: array of objects. Atoms included for self-containment but not core to the topic. Each object: `atom_id` (string), `role` (string enum: `prerequisite`, `evidence`, `classification_frame`, `transition`, `example`, `editorial`).

**Text fields:**

- `primary_text`: string. The complete Arabic text of the excerpt, assembled by concatenating `atom_text` from all atoms in `atom_ids` order, with a single space between non-contiguous atoms. Verbatim from frozen source — never edited (D-004). Diacritics preserved exactly.
- `derived_normalized_text`: string. Computationally normalized version for search and deduplication. Diacritics optionally stripped, Alef/Teh Marbuta normalized, whitespace standardized. Generated deterministically from `primary_text`.

**Attribution fields:**

- `primary_author_id`: string or null. `canonical_id` of the scholar whose words this excerpt primarily contains. Derived from `layer_author_id` of the core atoms' dominant layer. For multi-layer excerpts, this is the layer that contributes the most core atoms.
- `primary_author_name`: string or null. Display name of the primary author, from the scholar authority registry.
- `quoted_scholars`: array of objects. Scholars quoted or referenced within this excerpt. Each object: `canonical_id` (string or null), `name_text` (string — the name as it appears in the text), `role` (string enum: `quoted_opinion`, `cited_source`, `refuted_position`, `reported_consensus`, `teacher_reference`), `confidence` (float). Populated from `embedded_refs` of type `scholarly_quote` and from `scholarly_function: opinion_marker` atoms.
- `source_layer`: string. The dominant authorial layer for this excerpt. All atoms in a well-formed excerpt should share a layer; if they don't (mixed-layer excerpt), the dominant layer is assigned and review flag `mixed_layer_excerpt` is added.

**Classification fields:**

- `excerpt_topic`: string. A concise Arabic description of what this excerpt teaches (e.g., "تعريف المبتدأ" or "حكم صلاة الجماعة"). Generated by the LLM from the excerpt content.
- `proposed_leaf`: string or null. The proposed taxonomy leaf path (e.g., `nahw/المبتدأ_والخبر/تعريف_المبتدأ`). Null if the engine cannot determine a leaf with confidence ≥ 0.5. The taxonomy engine makes the final placement decision.
- `proposed_leaf_confidence`: float, 0.0–1.0. Confidence in the proposed leaf.
- `science_id`: string. Which science this excerpt belongs to. Inherited from source metadata `science_scope`, refined by content analysis if the source spans multiple sciences.
- `school`: string or null. The scholarly tradition reflected in this excerpt's text (not the author's lifelong affiliation). Null for sciences without schools or when school cannot be determined. When set, includes confidence.
- `school_confidence`: float or null.
- `content_types`: array of strings. Aggregated from the atoms' `scholarly_function` values, deduplicated. Describes what kinds of scholarly content this excerpt contains (e.g., `["definition", "example", "evidence_quran"]`).
- `excerpt_kind`: string enum. One of: `teaching` (scholarly content — the vast majority), `exercise` (practice material — tamrinat sections), `apparatus` (editorial/structural content — tables of contents, editor introductions).

**Evidence and reference fields:**

- `evidence_refs`: array of objects. All evidence references within this excerpt. Each object:
  - `evidence_type`: string enum. One of: `quran`, `hadith`, `ijma`, `qiyas`, `companion_statement`, `rational`, `istishab`.
  - `text_snippet`: string. A brief excerpt of the evidence text (≤100 chars) for identification.
  - `detail`: object or null. For `quran`: `{ surah: int, ayah_start: int, ayah_end: int }`. For `hadith`: `{ collection: string|null, hadith_number: string|null, grade: string|null, grade_source: string|null }`. For others: null.
  - `source_atom_id`: string. The atom containing this evidence.

- `takhrij_data`: array of objects. Hadith source-tracing data extracted from editor (tahqiq) footnotes. Each object: `hadith_ref` (string — the text identifying the hadith), `collections` (array of strings — which hadith collections contain it), `numbers` (array of strings — hadith numbers in those collections), `grade` (string or null — authenticity grade), `grade_source` (string or null — who graded it).

- `terminology_variants`: array of objects. Terms that may have different names across sources. Each object: `term_in_text` (string — the term as used in this excerpt), `standard_term` (string or null — the standardized term if known), `confidence` (float). Helps the taxonomy engine map to the correct leaf when different sources use different names for the same concept.

**Quality fields:**

- `self_containment_score`: float, 0.0–1.0. LLM-assessed score of how well this excerpt meets the self-containment standard (§5.1). Above 0.7: acceptable. 0.5–0.7: marginal, needs review. Below 0.5: deficient, likely missing context.
- `self_containment_notes`: string or null. If score < 0.7, explanation of what's missing or weak.
- `excerpt_confidence`: float, 0.0–1.0. Overall confidence in the excerpt's quality (average of boundary confidence, attribution confidence, and self-containment score).

**Source reference fields:**

- `physical_pages`: object. `volume` (int or null), `start_page` (string or null), `end_page` (string or null). Derived from the passage's `physical_pages` and the atoms' `anchor_span` positions.
- `division_path`: array. Inherited from the passage record.

**Review flags:**

- `review_flags`: array of strings. Possible values:
  - `low_self_containment`: score < 0.7.
  - `low_confidence_attribution`: primary_author or school confidence < 0.6.
  - `mixed_layer_excerpt`: atoms from multiple layers.
  - `cross_topic_candidate`: excerpt may cover multiple distinguishable topics (§5.3 signal).
  - `consensus_disagreement`: multi-model consensus produced different results (§6).
  - `evidence_ungraded`: hadith evidence detected but no grading information found.
  - `implicit_reference_unresolved`: text contains "قال بعض أصحابنا" or similar implicit reference that could not be resolved.
  - `decontextualization_risk`: excerpt contains a scholar reporting another's view — verify attribution.
  - `source_metadata_unavailable`: could not access source metadata for enrichment.
  - `llm_enrichment_failed`: LLM metadata enrichment failed; defaults applied.
  - `low_fidelity_atoms`: inherited from atom-level `low_fidelity_source` flags.
  - `duplicate_candidate`: another excerpt from the same source has very similar topic (one-excerpt-per-source-per-leaf diagnostic, §5.5).
  - `cross_source_duplicate`: semantic deduplication (§4.B.2) detected a near-duplicate in another source.
  - `argument_incomplete`: argument completeness analysis (§4.B.3) score < 0.7.
  - `passaging_boundary_suspect`: argument completeness analysis detected continuation in next passage — potential passaging error.

**Provenance fields:**

- `processing_metadata`: object. `engine_version` (string), `model_used` (string — the LLM model), `consensus_used` (bool), `processing_timestamp` (ISO datetime).

**Guarantees about the excerpt stream:**

- **Source-agnostic.** The excerpt schema is identical regardless of source type.
- **Passage containment.** Every excerpt's atoms all share the same `passage_id` (D-011).
- **Non-overlapping atoms.** No atom appears in more than one excerpt. Each atom is assigned to exactly one excerpt.
- **Exhaustive atom coverage.** Every non-heading atom is included in exactly one excerpt. Heading atoms may be excluded (they provide structural context, not excerpt content) or included as context atoms.
- **Text integrity.** `primary_text` is assembled verbatim from atom texts. No modification (D-004).
- **Attribution completeness.** Every excerpt has `primary_author_id` (or null with review flag), `source_layer`, and `science_id`.
- **Confidence propagation (D-023).** Every classification carries a confidence score. No decision is presented as certain when it is not.
- **Provenance chain.** Every excerpt carries `source_id`, `passage_id`, `atom_ids`, `physical_pages` — sufficient to trace back to the frozen source.

**Metadata pass-through (D-023).** The excerpting engine preserves all upstream metadata by reference (`source_id`, `passage_id`, `atom_ids`) and adds:

- Excerpt boundaries and atom grouping.
- Self-containment evaluation.
- Author identification and attribution.
- School classification.
- Topic classification and proposed leaf.
- Content type aggregation.
- Evidence references with hadith grading.
- Takhrij data from editor footnotes.
- Quoted scholars with roles.
- Terminology variants.
- Review flags for quality gating.

**Source registry update.** Upon successful excerpting of all passages for a source, the source's processing status is updated from `atomized` to `excerpted`. The excerpt stream path is recorded.

---

## 4. Processing Specification

### §4.A — Core Processing

#### §4.A.1 — Three-Phase Per-Passage Processing Pipeline

Each passage's atoms are processed through three sequential phases.

**Phase 1: Boundary Detection (LLM-driven).** The LLM receives all atoms for a passage (their `atom_text`, `structural_type`, `scholarly_function`, `atom_relations`, `bonded_reason`, and `embedded_refs`) and determines which atoms group together into excerpts. The LLM's output is a list of atom groups, where each group is a proposed excerpt.

Boundary detection rules:

- **Bonded atoms are never split.** Atoms sharing a `bonded_group_id` (from atomization) must stay in the same excerpt. The boundary detection phase receives these bonds as hard constraints.
- **The division hint.** If all atoms in a passage share the same `division_path` leaf, the default is one excerpt per passage unless the content clearly covers multiple distinguishable topics. If the passage covers multiple division leaves (merged siblings from passaging), each division's atoms form a natural grouping hint.
- **The atom relation hint.** `atom_relations` edges (illustrates, evidences, conditions) strongly suggest atoms that belong together. An `example` atom that `illustrates` a `definition` atom belongs in the same excerpt.
- **The scholarly function hint.** A sequence like [definition → example → example → evidence_quran → evidence_hadith] is a natural teaching unit. A break in scholarly function pattern (e.g., definition of topic A followed by definition of topic B) suggests an excerpt boundary.
- **The completeness criterion (§5.2).** Each group must be a complete treatment — not trailing off mid-argument. The LLM evaluates: "Does this group of atoms form a complete scholarly teaching unit, or is it cut off mid-thought?"

**Phase 2: Self-Containment Evaluation (LLM-driven, with consensus).** For each candidate excerpt from Phase 1, the LLM evaluates self-containment against the §5.1 standard. The evaluation prompt asks: "Given this text and the source metadata (author, work, science), can a reader with general familiarity of the science fully understand what is being taught, who said it, and from which tradition?"

The self-containment evaluation produces:
- `self_containment_score` (0.0–1.0).
- `self_containment_notes` (what's missing, if anything).
- A recommendation: `accept` (score ≥ 0.7), `enrich` (0.5–0.7, needs context atoms added), or `merge` (< 0.5, should be merged with adjacent excerpt).

If the recommendation is `enrich`, the engine attempts to add context atoms from adjacent atoms (heading atoms, prerequisite atoms from earlier in the passage) and re-evaluates. If the recommendation is `merge`, the engine merges with the most closely related adjacent excerpt and re-evaluates. Merging is attempted at most twice per original candidate to prevent unbounded growth.

This phase uses multi-model consensus (§6) for excerpts from verified sources. Two models independently evaluate self-containment. If they disagree by more than 0.2 on the score, the conservative score (lower) is used and review flag `consensus_disagreement` is added.

**Phase 3: Metadata Enrichment (LLM-driven + deterministic).** For each accepted excerpt, the engine populates all classification and attribution fields. This phase has both deterministic and LLM components:

**Deterministic enrichment:**
- `primary_author_id`: from the dominant `layer_author_id` across core atoms.
- `source_layer`: from the dominant `source_layer` across core atoms.
- `content_types`: aggregated from atoms' `scholarly_function` values.
- `evidence_refs`: assembled from atoms with evidential `scholarly_function` values and `embedded_refs`.
- `physical_pages`: computed from atoms' `anchor_span` positions mapped to passage `physical_pages`.
- `atom_ids`, `core_atom_ids`, `context_atom_ids`: finalized from Phase 1 and 2 outputs.
- `primary_text`: concatenated from `atom_text` values.
- `derived_normalized_text`: computed from `primary_text`.

**LLM enrichment:**
- `excerpt_topic`: the LLM generates a concise Arabic topic description from the excerpt text.
- `proposed_leaf`: the LLM proposes a taxonomy leaf path based on the topic and the science's known tree structure (loaded from the taxonomy tree files).
- `school`: the LLM determines school attribution from (a) the text content, (b) the author's known school affiliation from source metadata, (c) explicit school markers in the text ("عند الحنابلة", "ذهب الشافعية"). The LLM distinguishes between "the author belongs to school X" and "the author is presenting school Y's position" — these are different attribution scenarios.
- `quoted_scholars`: the LLM resolves scholar mentions from `embedded_refs` to canonical IDs where possible, using the scholar authority registry. Names like "الإمام" are resolved contextually: in a Shafi'i text, "الإمام" usually means al-Shafi'i; in a Hanbali text, Ahmad.
- `takhrij_data`: for excerpts with hadith evidence AND editor footnotes, the LLM extracts structured takhrij data from the footnotes (which collections, hadith numbers, grading).
- `terminology_variants`: the LLM identifies terms that may have alternative names in other sources.

LLM enrichment failures (timeout, validation failure after retries) do not block excerpt creation. The excerpt is produced with available deterministic metadata plus review flag `llm_enrichment_failed`. Enrichment can be retried later.

#### §4.A.2 — Decontextualization Prevention

The most dangerous excerpt error is decontextualized quotation (reference/DOMAIN.md, "Decontextualized quotation" risk): extracting "Scholar A says X" when the original text says "Scholar A reports that Scholar B says X, but Scholar A disagrees." The excerpt would misattribute X to Scholar A.

The excerpting engine prevents this through:

1. **Atom-level signals.** Atoms with `scholarly_function: opinion_marker` indicate reported positions. The excerpting engine checks: does the passage contain both a reported position AND a response/refutation? If yes, both must be in the same excerpt.

2. **LLM verification.** During Phase 2 (self-containment), the LLM is specifically prompted: "Does this excerpt contain a reported position that could be misattributed without the surrounding context? If so, is the surrounding context included?"

3. **Review flag.** If the LLM detects decontextualization risk, review flag `decontextualization_risk` is added. The human reviewer sees: "This excerpt contains Scholar A reporting Scholar B's view. Verify that the attribution is correct."

4. **Attribution metadata.** The `quoted_scholars` field explicitly distinguishes `quoted_opinion` (Scholar A states their own view) from `reported_consensus` (Scholar A reports a consensus) from `refuted_position` (Scholar A reports a position they disagree with).

#### §4.A.3 — Multi-Layer Excerpt Handling

In multi-layer sources (sharh, hashiyah), the excerpting engine must produce excerpts attributed to the correct author.

**Layer-homogeneous excerpts (preferred).** Most excerpts should contain atoms from a single layer. A commentary excerpt contains the commentator's analysis; a matn quotation within it is a context atom with role `classification_frame`, attributed to the matn author via `quoted_scholars`.

**Layer-heterogeneous excerpts (sometimes necessary).** When a commentator's explanation is inseparable from the matn text it explains — when removing the matn quotation would make the commentary unintelligible — the excerpt may contain atoms from multiple layers. In this case:

- `primary_author_id` is the commentator (the sharh author), because the excerpt's teaching contribution is the commentary, not the matn text.
- `source_layer` is `sharh` (the dominant layer).
- The matn quotation atoms are listed in `context_atom_ids` with role `classification_frame`.
- `quoted_scholars` includes the matn author with role `quoted_opinion`.
- Review flag `mixed_layer_excerpt` is added.

**Editor footnote excerpts.** Footnotes with `scholarly_function: editorial_note` are handled separately:

- If the footnote contains substantive scholarly commentary (tahqiq 'ilmi), it may form its own excerpt with `source_layer: tahqiq`, `excerpt_kind: teaching`, and `primary_author_id` set to the editor.
- If the footnote is purely bibliographic (citing sources, variant readings), it is attached as a context atom to the main text excerpt it annotates, with role `editorial`.
- If the footnote contains takhrij (hadith source tracing), the data is extracted into `takhrij_data` on the main text excerpt.

#### §4.A.4 — Evidence and Hadith Handling

The excerpting engine captures evidence references as structured metadata, enabling the synthesizer to produce evidence-aware entries ("the Hanafi position rests on Quranic evidence and analogy, while the Shafi'i position relies on hadith").

**Evidence extraction.** For each atom with an evidential `scholarly_function` (`evidence_quran`, `evidence_hadith`, `evidence_ijma`, `evidence_qiyas`, `evidence_rational`), the engine creates an `evidence_refs` entry with the evidence type and source atom ID. For Quran and hadith evidence, the engine extracts structured identification from `embedded_refs`.

**Hadith grading.** When hadith evidence is detected, the engine searches for grading information in three locations:

1. **Inline grading.** The text may state the grade explicitly: "رواه البخاري ومسلم" (mutawatir/sahih by default), "رواه الترمذي وحسّنه" (hasan per al-Tirmidhi).
2. **Editor footnotes.** Tahqiq footnotes often contain detailed hadith grading from the editor.
3. **Takhrij data.** If neither inline nor footnote grading is available, the `grade` field is null and review flag `evidence_ungraded` is added.

The engine does NOT independently assess hadith authenticity — that would be scholarly overreach. It records the grades stated in the source text and editor apparatus, with attribution to who stated the grade.

#### §4.A.5 — Implicit Reference Resolution

Islamic scholarly texts frequently use implicit references: "قال بعض أصحابنا" (some of our companions said), "الإمام" (the Imam), "صاحب الكتاب" (the author of the book), "الشيخ" (the Sheikh). These are context-dependent and can only be resolved with knowledge of the author, school, and scholarly context.

The excerpting engine attempts resolution using:

1. **Scholar authority registry.** The registry maps common epithets to canonical IDs per context: "الإمام" → al-Shafi'i in Shafi'i fiqh texts, Ahmad in Hanbali texts, Abu Hanifa in Hanafi texts.
2. **Work relationship data.** If the source is a sharh, "صاحب الكتاب" refers to the matn author (from work relationships in source metadata).
3. **LLM contextual resolution.** For ambiguous references, the LLM attempts resolution using the surrounding text and source context.

When resolution succeeds, the resolved scholar is added to `quoted_scholars` with the resolved `canonical_id` and a `confidence` score. When resolution fails, the `canonical_id` is null and review flag `implicit_reference_unresolved` is added. The unresolved reference is NEVER silently dropped — it persists in the excerpt as an indicator that a scholarly reference exists but could not be identified (D-033, fail-loud).

#### §4.A.6 — Cross-Topic Excerpt Handling (§5.3 Implementation)

When the LLM detects that a candidate excerpt covers multiple distinguishable topics, it applies the §5.3 rules:

**Rule 1 — Context mentions.** If the secondary topic is mentioned briefly as context (a reference, a comparison), the excerpt remains unified. The primary topic determines `proposed_leaf`.

**Rule 2 — Extensive independent treatments.** If the secondary topic is treated extensively:
- The LLM evaluates whether the text can be split into two self-contained excerpts (§5.3 outcome a, b, or c).
- If outcome (a): two excerpts are produced, each self-contained with its own metadata.
- If outcome (b): one excerpt is produced from the self-contained portion; the other portion is included as context atoms.
- If outcome (c): one excerpt with the full text, review flag `cross_topic_candidate`.

**Rule 3 — Content integrity priority.** A multi-topic excerpt that is self-contained is always preferable to two broken excerpts.

---

### §4.B — Transformative Capabilities

#### §4.B.1 — Argumentative Discourse Mapping

[NOT YET IMPLEMENTED]

**What this capability does:** Detects the argumentative structure pattern within each excerpt and tags where the excerpt sits in the classical Islamic scholarly argumentation sequence: مسألة (question formulation) → أقوال (position statements) → أدلة (evidence presentation) → مناقشة (discussion/refutation) → ترجيح (weighing/preference) → خلاصة (conclusion). Each excerpt receives an `argument_role` classification, and multi-atom excerpts receive an internal argument map showing which atoms play which role in the argument.

**Why this is transformative:** No existing Islamic studies tool detects argumentative structure. Shamela, Turath, and Usul.ai treat text as flat searchable content. But the synthesizer needs to know MORE than what an excerpt says — it needs to know what ROLE the excerpt plays in the scholarly discourse. An excerpt that formulates a question (مسألة) must be placed differently in the entry than an excerpt that weighs competing positions (ترجيح). The IslamicLegalBench benchmark (Elmahjub et al., Feb 2026) found that even GPT-4o achieves only 68% correctness on Islamic legal reasoning with 21% hallucination — precisely because LLMs lack awareness of argumentative structure. By providing the synthesizer with argument role metadata, KR prevents the synthesizer from confusing a scholar's presentation of an opponent's view with their own position (the decontextualization risk, but at a structural level).

**Research basis:** Legal argument mining (Habernal et al. 2024, ECHR corpus of 373 decisions with 15K annotated spans) demonstrates that domain-specific argument typologies outperform generic claim/premise models. The Sefaria project shows that biblical citation mapping across Talmudic contexts reveals whether passages serve "similar argumentative purposes or vary by tractate" (Brand 2025). Arabic scholarly texts have an even more regular argumentative structure than European legal texts — Islamic fiqh follows the mas'ala format so consistently that it is taught as a method (تحرير المسألة).

**Input:** A completed excerpt (from Phase 3, with all metadata), plus the source metadata (science, work genre, work level).

**Processing:**

1. **Argument role classification.** The LLM receives the excerpt text, its content types from §4.A, and the source's science/genre context. It classifies the excerpt into one of these argument roles:
   - `masala_formulation`: The text poses a scholarly question or defines the issue under discussion. Markers: "مسألة", "هل", "ما حكم", "اختلف العلماء في".
   - `position_statement`: The text states a scholarly position (one or more). Markers: "قال", "ذهب ... إلى", "مذهب ... أن", "القول الأول".
   - `evidence_presentation`: The text presents evidence for a position. Markers: "لقوله تعالى", "لما روى", "واحتجوا بأن", "والدليل".
   - `discussion_refutation`: The text discusses, critiques, or refutes a position. Markers: "ورُدّ بأن", "ونوقش", "ويُعترض عليه", "والجواب عن ذلك".
   - `weighing_preference`: The text evaluates positions and states a preference. Markers: "والراجح", "والصحيح", "والمعتمد", "وأقوى القولين".
   - `conclusion_summary`: The text summarizes findings or states a final rule. Markers: "والحاصل", "فتلخص", "فالقاعدة", "والخلاصة".
   - `definition_exposition`: The text defines or explains a concept (common in grammar, usul). Markers: "هو/هي", "يُعرَّف بأنه", "المراد به", "اصطلاحاً".
   - `example_application`: The text provides examples or applies a rule. Markers: "نحو", "مثاله", "كقولك", "ومن ذلك".
   - `mixed`: The text contains multiple argument roles that cannot be cleanly separated.

2. **Internal argument map (for multi-atom excerpts).** For excerpts with ≥5 core atoms, the LLM produces an internal map: which atom ranges serve which argument role. This is a list of `{atom_id_start, atom_id_end, role}` segments. For excerpts with <5 core atoms, the whole excerpt receives a single role.

3. **Per-science calibration.** The argument role vocabulary is calibrated per science:
   - **Fiqh:** Full mas'ala→tarjih sequence. All 8 roles are expected. `weighing_preference` is especially important.
   - **Nahw:** `definition_exposition` and `example_application` dominate. `position_statement` maps to grammatical school disagreements.
   - **Aqidah:** Similar to fiqh but `evidence_presentation` includes more rational (`عقلي`) arguments.
   - **Ilm al-hadith:** `position_statement` maps to hadith grading conclusions. Evidence is meta-level (evaluation of narrators).
   - **Tajwid:** Almost exclusively `definition_exposition` and `example_application` — minimal disagreement.

**Output:** Two new fields on the excerpt record:

- `argument_role`: string enum (one of the 9 values above). The excerpt's dominant argumentative function.
- `argument_role_confidence`: float, 0.0–1.0.
- `argument_map`: array of objects or null. Non-null for excerpts with ≥5 core atoms. Each object: `{ start_atom_id: string, end_atom_id: string, role: string }`. The segments cover all core atoms without overlap.

**How the synthesizer uses this:** When assembling an entry at a taxonomy leaf, the synthesizer can structure the entry as: formulation → positions → evidence → discussion → conclusion — mirroring the classical tahrir al-mas'ala format. Without this metadata, the synthesizer must infer structure from raw text, which IslamicLegalBench shows LLMs do unreliably.

**Technical approach:** LLM classification using Instructor for structured output. The prompt includes 3 few-shot examples per science (from gold baselines). The Arabic marker detection is a pre-filter: if explicit markers are present, they boost confidence; if absent, the LLM infers from content. Single-model (not consensus) — the taxonomy engine and synthesizer provide downstream validation.

#### §4.B.2 — Cross-Source Semantic Deduplication

[NOT YET IMPLEMENTED]

**What this capability does:** Detects when two excerpts from DIFFERENT sources express substantially the same scholarly content — the same definition, the same hadith, the same ruling stated in nearly identical words. Produces a `semantic_duplicates` field linking near-duplicate excerpts across sources, enabling the synthesizer to present content once (from the strongest source) rather than redundantly.

**Why this is transformative:** The KITAB project's passim algorithm detects verbatim text reuse across the OpenITI corpus of 2 billion words (splitting texts into 300-word chunks and looking for shared n-grams). But passim operates at the corpus level for digital humanities research — it doesn't produce actionable metadata for a knowledge pipeline. KR's excerpting engine needs excerpt-level semantic deduplication that catches not just verbatim copying but paraphrase and shared quotation. When 5 sources all quote "الأعمال بالنيات" in the context of wudu rules, the synthesizer should present the hadith once and cite all 5 sources, not produce 5 redundant paragraphs.

**Why this is critical for scholarly integrity:** DOMAIN.md's "Scholarly Integrity Risks" section identifies "Library composition bias" — if the library has 30 Hanbali sources and 5 Maliki sources, the synthesizer might present Hanbali positions as dominant simply because they appear more often. Deduplication metadata directly addresses this: the synthesizer knows "these 12 excerpts are 4 unique positions, each appearing in multiple sources" rather than treating 12 excerpts as 12 independent data points.

**Input:** A completed excerpt plus the fingerprint manifest from the atomization engine (§4.B.5 in atomization SPEC) for the current source and for all previously processed sources at the proposed leaf.

**Processing:**

1. **Fast pre-filter.** Using `fingerprint_text_hash` from the atomization engine's semantic fingerprint, identify atom-level text hash collisions across sources. Excerpts sharing ≥2 atom text hashes with another excerpt at the same leaf are candidate duplicates. This is O(1) lookup per hash.

2. **Semantic similarity check.** For candidates passing the pre-filter, compute embedding similarity between the excerpts' `derived_normalized_text` fields using the same embedding model as duplicate detection in §5. Threshold: cosine similarity ≥ 0.82 triggers detailed analysis.

3. **LLM deduplication judgment.** For pairs exceeding the embedding threshold, the LLM receives both excerpts with their source metadata and classifies the relationship:
   - `verbatim_duplicate`: Same text, copied from one source to another (common in Shamela where the same text may appear in multiple collections).
   - `shared_quotation`: Both sources quote the same earlier scholar or hadith. The primary content is the same but the framing differs.
   - `paraphrase`: Same scholarly content expressed differently. The underlying position, evidence, or definition is the same.
   - `related_not_duplicate`: Similar topic and some shared content, but substantively different arguments or conclusions.

4. **Primary source identification.** For `verbatim_duplicate` and `shared_quotation` pairs, the engine identifies which excerpt is from the "primary" source (the original author, the earlier chronological source, the higher-authority source based on `source_authority` metadata). The synthesizer will cite the primary source and reference the others.

**Output:** `semantic_duplicates` field on the excerpt (array of objects): `{ target_excerpt_id: string, target_source_id: string, relationship: enum(verbatim_duplicate, shared_quotation, paraphrase, related_not_duplicate), confidence: float, primary_source: string|null }`.

**Scale management:** During initial bulk loading (many sources processed at once), deduplication runs as a batch job AFTER all sources are excerpted, comparing excerpts at the same proposed leaf. During incremental processing (new source added), deduplication runs per-excerpt against the existing library. The pre-filter keeps this tractable: only excerpts sharing fingerprint hashes or at the same leaf are compared.

**Technical approach:** Atomization fingerprints (hash-based) for pre-filter. Sentence-transformers for embedding similarity. LLM with Instructor for relationship classification. The atomization engine's `fingerprint_key_terms` field is used as an additional matching signal: excerpts sharing ≥3 key terms are candidate duplicates even without hash collisions.

#### §4.B.3 — Scholarly Argument Completeness Analysis

[NOT YET IMPLEMENTED]

**What this capability does:** For excerpts that contain a scholarly argument (position + evidence), evaluates whether the argument is COMPLETE as extracted — whether all the evidence the author cited for the position is included, or whether some was left in another excerpt or lost at a passage boundary. This is a deeper analysis than self-containment: an excerpt can be self-contained (understandable) but argumentatively incomplete (missing evidence the author used).

**Why this is transformative:** The synthesizer's entry quality depends on having complete arguments. If an excerpt captures a position but only two of three pieces of evidence the author cited, the entry will present a weaker version of the argument than the author intended. Argumentative completeness analysis detects this gap before the excerpt reaches the synthesizer.

**Research basis:** Argument mining research (ArgMining 2024-2025 workshops) demonstrates that argument completeness can be detected through rhetorical markers. Arabic scholarly texts are remarkably explicit about argument structure: "ومن الأدلة أيضاً" (and among the evidence also), "الدليل الثالث" (the third evidence), "والجواب من وجوه" (the response from several angles) — these markers signal how many elements the author intends. A numbered evidence list ("الدليل الأول... الدليل الثاني...") where the excerpt ends after the second but the passage continues with the third is a detectable completeness failure.

**Input:** An excerpt with evidential content types (from §4.A.4), plus the passage context (all atoms in the passage, not just the excerpt's atoms).

**Processing:**

1. **Argument structure detection.** Using the argument role from §4.B.1 (if available), identify excerpts that are `evidence_presentation`, `discussion_refutation`, or `position_statement` — these are the argument-bearing excerpts.

2. **Completeness signal detection.** The LLM examines the excerpt and its surrounding context for:
   - **Enumeration markers:** "الوجه الأول... الوجه الثاني..." — if only some are in the excerpt, the argument is incomplete.
   - **Continuation markers:** "ومنها أيضاً" at the end of an excerpt suggests more follows.
   - **Conclusion absence:** A position + evidence sequence without a conclusion marker ("فثبت", "فدل على") may be incomplete.
   - **Cross-passage split:** If the argument continues in atoms from the NEXT passage (detected by checking whether the next passage's first atoms are continuation-type atoms), this signals a passaging boundary error.

3. **Completeness scoring.** Produces a score 0.0–1.0 where:
   - 1.0 = the argument has all its elements (position, evidence, conclusion) and no continuation markers.
   - 0.7–0.99 = the argument is substantially complete but may be missing a minor element.
   - 0.5–0.69 = the argument is detectably incomplete (explicit evidence count mismatch or missing conclusion).
   - <0.5 = the argument is severely incomplete (mid-argument truncation).

**Output:** `argument_completeness` field on the excerpt: `{ score: float, missing_elements: array of string, continuation_detected: bool, continuation_passage_id: string|null, notes: string }`.

If `continuation_detected` is true, this is also a signal to the passaging engine (via a feedback record) that the passage boundary may need adjustment.

**Technical approach:** LLM analysis with Instructor structured output. The Arabic enumeration and continuation markers are provided as a reference list in the prompt. The cross-passage check is deterministic: if the next passage's first atom has `scholarly_function` that logically continues the current excerpt's argument pattern, flag it.

#### §4.B.4 — Cross-Excerpt Scholarly Dialogue Detection

[NOT YET IMPLEMENTED]

**What this capability does:** Detects when two excerpts from different sources are part of the same scholarly dialogue — one scholar responding to another, or two scholars addressing the same mas'ala from different perspectives — even when the excerpts don't explicitly reference each other. Produces typed dialogue links: agreement, disagreement, refinement, supersession, or citation.

**Why this is transformative:** Islamic scholarly literature is a 14-century conversation. When al-Nawawi writes about المبتدأ, he is responding to positions established by Sibawayhi 500 years earlier. Currently, identifying these dialogue threads requires a scholar to read multiple sources and mentally connect them across centuries. The Sefaria project demonstrates that cross-text citation mapping at the Talmudic level reveals whether passages "consistently serve similar argumentative purposes or whether their interpretive applications vary" (Brand 2025). KR can detect these connections automatically, enabling the synthesizer to produce entries that read as scholarly dialogues rather than flat position lists — exactly the "storyline" and "narrative thread" the owner identified as missing from existing resources (DOMAIN.md, "What Doesn't Exist Yet").

**Input:** A completed excerpt (with topic, school, author, argument role from §4.B.1, and evidence references) plus the library's existing excerpt inventory at the proposed leaf.

**Processing:** When a new excerpt is placed at a leaf, the engine compares it against all existing excerpts at that leaf. The comparison uses 4 signals:

1. **Position comparison.** Using argument role metadata, identify excerpts that state positions on the same mas'ala. Do they reach the same conclusion or different ones? If different, is one responding to the other (evidenced by chronological order + similar evidence base)?

2. **Evidence comparison.** Do the excerpts cite the same evidence (same Quran verse, same hadith)? If so, do they interpret it the same way? Different interpretations of the same evidence are a strong signal of scholarly dialogue. The `evidence_refs` field enables this comparison deterministically for Quran verses (surah/ayah match) and hadith (collection/number match).

3. **Chronological ordering.** Using author death dates from the scholar authority registry, order the excerpts temporally. A later scholar who addresses the same question with the same evidence but reaches a different conclusion is almost certainly responding to the earlier position.

4. **Explicit citation check.** Does either excerpt's `quoted_scholars` reference the other excerpt's author? An explicit reference is the strongest signal.

**Output:** `dialogue_links` field on the excerpt (array of objects): `{ target_excerpt_id: string, dialogue_type: enum(agrees, disagrees, refines, supersedes, cites, shared_evidence), confidence: float, evidence: string }`.

**Scale management:** Computationally O(n) per new excerpt at a leaf with n existing excerpts. For leaves with >50 existing excerpts, the engine pre-filters by argument role and evidence overlap (deterministic) before running LLM comparison. Only active during incremental processing (new source added to existing library), not during initial bulk loading (run as batch post-processing).

**Technical approach:** Deterministic pre-filtering (evidence match, chronological window) + LLM comparison using Instructor for structured output. The LLM receives the new excerpt, its metadata, and each candidate dialogue partner with their metadata.

#### §4.B.5 — Self-Containment Repair Suggestions

[NOT YET IMPLEMENTED]

**What this capability does:** When an excerpt fails the self-containment evaluation (score < 0.7), instead of just flagging it, the engine generates specific repair suggestions: "This excerpt would be self-contained if it included a definition of [term X], which appears in [atom_id Y] of the same passage" or "This excerpt's argument is incomplete without the evidence cited in the next passage — consider whether the passaging boundary is correct."

**Why this is transformative:** Self-containment failures are currently opaque — the reviewer knows the excerpt is incomplete but not why or how to fix it. Repair suggestions turn a quality flag into an actionable improvement path. They also surface passaging errors (bad boundaries that split natural teaching units) which are otherwise invisible until a human reader notices the excerpt doesn't make sense.

**Input:** An excerpt that failed self-containment evaluation, plus the full atom context from its passage and adjacent passages.

**Processing:** The LLM analyzes what makes the excerpt non-self-contained:

- **Missing prerequisite:** A term is used without definition, but the definition appears earlier in the same passage. Repair: add the definition atom as a context atom with role `prerequisite`.
- **Incomplete argument:** The argument trails off (evidence cited but conclusion missing), and the continuation is in the next passage — suggesting a passaging boundary error. Repair: flag passaging error and suggest boundary adjustment.
- **Missing attribution:** A position is stated without saying who holds it, but the attribution appears in the preceding context. Repair: add the attribution atom as a context atom with role `classification_frame`.
- **Unresolved pronoun/reference:** The excerpt contains "هذا" (this), "ما تقدم" (what was previously mentioned), or similar deictic references that cannot be resolved from the excerpt alone. Repair: either add the referenced content as context, or generate a `self_containment_context` text field that paraphrases the missing referent.

**Output:** `repair_suggestions` field on the excerpt (array of objects): `{ suggestion_type: enum(add_context_atom, merge_with_adjacent, flag_passaging_error, flag_missing_source_context, generate_context_note), detail: string, target_atom_id: string|null, generated_context: string|null }`.

When `suggestion_type` is `generate_context_note`, the `generated_context` field contains a brief Arabic sentence (≤50 words) that the synthesizer may include as a contextual preface when presenting the excerpt. This generated context is ALWAYS marked as `grounding_type: analytical` (not source-grounded) — it is the engine's interpolation, not the author's words.

**Technical approach:** LLM analysis using the same model as self-containment evaluation, with an additional prompt asking for specific repair recommendations. The adjacent passage atoms are included in the context window to enable cross-passage suggestions.

---

## 5. Validation and Quality

**Layer 1: Self-validation.** Automated checks on every excerpt:

- **V-1: Passage containment.** All `atom_ids` belong to the same `passage_id`. Failure is fatal for the excerpt.
- **V-2: Atom uniqueness.** No atom appears in more than one excerpt within the source. Failure is fatal — indicates a boundary error.
- **V-3: Atom coverage.** Every non-heading atom in the passage appears in exactly one excerpt. Warning if atoms are missing.
- **V-4: Text integrity.** `primary_text` matches the concatenation of `atom_text` values from `atom_ids`. Failure is fatal.
- **V-5: Attribution completeness.** `primary_author_id`, `source_layer`, and `science_id` are all present. Warning if any is missing.
- **V-6: Self-containment threshold.** `self_containment_score` ≥ 0.5. Scores below 0.5 are unlikely to be useful excerpts — warning with review flag.
- **V-7: Reasonable excerpt size.** Excerpt should have between 1 and 50 atoms, and `primary_text` should be between 20 and 5000 Arabic words. Outliers get review flags.

**Layer 2: Automated cross-excerpt checks.** Run after all passages for a source are excerpted:

- **Duplicate detection.** If two excerpts from the same source have `excerpt_topic` similarity > 0.85 (measured by embedding similarity on `derived_normalized_text`), review flag `duplicate_candidate` is added to both.
- **Coverage verification.** Every non-heading, non-whitespace atom in the source's atom stream should appear in exactly one excerpt. Missing atoms are logged.
- **School consistency.** If the source is by an author with a known school affiliation, verify that the majority of excerpts' `school` values match the expected school. Anomalies get logged (not flagged — legitimate reasons exist for an author to present other schools' positions).

**Layer 3: Human gate integration.** The excerpting engine's primary human gate is the excerpt review checkpoint, managed by the taxonomy engine. Excerpts with any review flag are presented to the owner for verification during placement review. The reviewer can:

- Accept the excerpt as-is.
- Modify metadata (correct school, fix attribution, adjust topic).
- Split or merge excerpts.
- Flag the excerpt (move to flagged knowledge).
- Reject the excerpt entirely (if it's corrupt or unintelligible).

Corrections at the human gate are saved as feedback that improves future excerpting decisions (via DSPy prompt optimization against corrected examples).

**Scholarly integrity safeguards:**

- **Decontextualization prevention** (§4.A.2): explicit detection of reported positions.
- **Layer misattribution prevention** (§4.A.3): multi-layer handling with correct author attribution.
- **Editor-author conflation prevention** (§4.A.3): editor footnotes separated from original author content.
- **Hadith grading capture** (§4.A.4): evidence is never presented without its authenticity status.
- **Confidence propagation** (D-023): every decision carries a confidence score.

---

## 6. Consensus Integration

The excerpting engine uses multi-model consensus for two critical decision types:

**Self-containment evaluation.** Two models independently evaluate self-containment. Agreement threshold: if scores are within 0.2 of each other, use the average. If they disagree by more than 0.2, use the conservative (lower) score and add review flag `consensus_disagreement`.

**School attribution.** Two models independently determine school attribution. If they agree, the shared attribution is used with confidence boost (+0.1). If they disagree, the attribution is flagged as uncertain (`school_confidence` set to the lower model's confidence) and review flag `consensus_disagreement` added.

**What does NOT use consensus:** Topic classification, author identification, and evidence extraction are single-model operations. Rationale: topic classification is validated by the taxonomy engine (an independent downstream check). Author identification is primarily deterministic (from layer metadata). Evidence extraction is validated by structured reference matching (Quran verse lookup, hadith collection verification).

**Model selection.** The two consensus models should be from different providers (e.g., Claude + GPT-4) to maximize independence. Routed through OpenRouter.

---

## 7. Error Handling

**Fatal errors:**

| Error Code | Trigger | Recovery |
|---|---|---|
| `EXCERPT_EMPTY_PASSAGE` | Passage has zero atoms | Skip passage. Log. |
| `EXCERPT_ID_MISMATCH` | Atoms have inconsistent passage_id/source_id | Skip passage. Log. Fatal data integrity issue. |
| `EXCERPT_TEXT_INTEGRITY` | V-4 failed — primary_text doesn't match atoms | Discard excerpt, retry from Phase 1. After 2 retries, skip with error. |

**Warning errors:**

| Error Code | Trigger | Recovery |
|---|---|---|
| `EXCERPT_ATOMS_REORDERED` | Atoms not in sequence_in_passage order | Sort and continue. Log. |
| `EXCERPT_SOURCE_METADATA_MISSING` | Source metadata unavailable | Continue with degraded enrichment. Review flag. |
| `EXCERPT_LLM_ENRICHMENT_FAILED` | LLM metadata enrichment failed after retries | Use deterministic metadata only. Review flag. |
| `EXCERPT_LOW_SELF_CONTAINMENT` | Self-containment score < 0.5 | Excerpt produced but flagged heavily. |
| `EXCERPT_MERGE_LIMIT` | Merge attempts exceeded limit (2) | Accept as-is with low score. |
| `EXCERPT_ATOM_UNCOVERED` | Non-heading atom not assigned to any excerpt | Log the atom. Assign to nearest excerpt as context. |

**Logging:** `library/sources/{source_id}/excerpts/processing_log.jsonl`.

---

## 8. Configuration

**LLM configuration:**

- `excerpting_model`: string. Primary LLM for boundary detection and enrichment. Default: routed through OpenRouter.
- `consensus_model_2`: string. Second LLM for consensus. Default: a different provider from `excerpting_model`.
- `excerpting_temperature`: float. Default: 0.15. Range: 0.0–0.5.
- `max_retries`: int. Default: 3.

**Self-containment thresholds:**

- `self_containment_accept`: float. Score threshold for automatic acceptance. Default: 0.7. Range: 0.5–0.9.
- `self_containment_enrich`: float. Score threshold for enrichment attempt (below this, merge). Default: 0.5. Range: 0.3–0.7.
- `consensus_disagreement_threshold`: float. Score difference that triggers consensus flag. Default: 0.2. Range: 0.1–0.4.

**Excerpt size limits:**

- `max_excerpt_atoms`: int. Default: 50. Range: 20–100.
- `max_excerpt_words`: int. Default: 5000. Range: 2000–10000.
- `min_excerpt_words`: int. Default: 20. Range: 5–100.

**Enrichment configuration:**

- `school_attribution_enabled`: bool. Default: true. For sciences without schools, set to false.
- `takhrij_extraction_enabled`: bool. Default: true. Set to false if the source has no tahqiq footnotes.
- `implicit_reference_resolution_enabled`: bool. Default: true.
- `duplicate_similarity_threshold`: float. Default: 0.85. Range: 0.7–0.95.

**Per-science hooks:** Level 3 SCIENCE.md may define:
- Additional required metadata fields.
- Science-specific school lists.
- Science-specific self-containment criteria.

---

## 9. Current Implementation State

**Existing files:**

- `engines/excerpting/src/extract_passages.py` — 2288 lines. ABD-era code combining atomization + excerpting in a single pass. Must be separated: atomization logic moves to the atomization engine; excerpting logic is redesigned per this SPEC.
- `engines/excerpting/src/assemble_excerpts.py` — 1021 lines. ABD-era code for assembling excerpts from atoms. Contains useful logic for atom grouping heuristics and self-containment checks that can inform (not constrain) the KR implementation.
- `engines/excerpting/src/__init__.py` — 0 lines.
- `engines/excerpting/reference/` — 10 ABD-era reference docs. Historical reference only (D-019). Useful domain knowledge about excerpting edge cases and scholarly text patterns.
- `engines/excerpting/CLAUDE.md` — engine orientation. Must be updated to match this SPEC.
- `schemas/excerpt.json` — ABD-era excerpt schema. Must be redesigned per §3 of this SPEC. Key changes: KR three-tier ID model (source_id, not book_id), evidence_refs with hadith grading, takhrij_data, quoted_scholars with roles, terminology_variants, self-containment_score/notes, consensus metadata, removal of ABD-specific fields.

**What works today:** The ABD code can process Shamela sources through a combined atomization+excerpting pass. It produces excerpts with basic metadata (topic, author, content type) but without: school attribution, evidence grading, takhrij extraction, implicit reference resolution, self-containment scoring, multi-model consensus, or cross-topic handling per §5.3. The ABD excerpt schema uses `book_id` instead of KR's three-tier identity model.

**Known gaps:**

- No separated excerpting module. [NOT YET IMPLEMENTED]
- No multi-model consensus. [NOT YET IMPLEMENTED]
- No self-containment scoring. [NOT YET IMPLEMENTED]
- No school attribution. [NOT YET IMPLEMENTED]
- No hadith grading capture. [NOT YET IMPLEMENTED]
- No takhrij extraction. [NOT YET IMPLEMENTED]
- No implicit reference resolution. [NOT YET IMPLEMENTED]
- No decontextualization prevention. [NOT YET IMPLEMENTED]
- No cross-topic handling per §5.3. [NOT YET IMPLEMENTED]
- All §4.B capabilities. [NOT YET IMPLEMENTED]

**External dependencies:**

- **Instructor** (Python, MIT): structured LLM output for all three phases.
- **OpenRouter** (API): LLM routing for primary and consensus models.
- **DSPy** (Python, MIT): prompt optimization against gold baselines and human gate corrections.
- **CAMeL Tools** (Python, MIT): Arabic text normalization for `derived_normalized_text`.
- **Sentence-transformers** (Python): multilingual embedding models for duplicate detection and topic similarity.
- **Scholar authority registry**: shared component for scholar name resolution.

---

## 10. Test Requirements

**Gold baseline requirements:**

- Minimum 15 gold baseline passages with manually verified excerpts. These must cover:
  - Prose passages with single-topic and multi-topic content.
  - Commentary passages with multi-layer text.
  - Passages with hadith evidence and isnad chains.
  - Passages with reported positions (decontextualization test cases).
  - Passages from at least 3 different sciences.
- Each gold baseline must include: manually verified excerpt boundaries, manually assigned metadata (topic, school, author, content types), manually evaluated self-containment scores, and manually verified evidence references.

**What MUST be tested:**

1. **Passage containment (V-1).** Every test verifies all atoms in an excerpt share a `passage_id`.
2. **Atom uniqueness (V-2) and coverage (V-3).** Every test verifies no atom is in two excerpts and no non-heading atom is missing.
3. **Text integrity (V-4).** Every test verifies `primary_text` matches concatenated atom texts.
4. **Self-containment accuracy.** Against gold baselines: self-containment scores should be within ±0.15 of the gold baseline score on average.
5. **Boundary accuracy.** Against gold baselines: ≥ 80% of excerpts should match the gold baseline boundaries (measured by atom set overlap ≥ 0.8 with a gold excerpt).
6. **Attribution accuracy.** `primary_author_id` correct for ≥ 95% of excerpts. `school` correct for ≥ 85% of excerpts.
7. **Decontextualization prevention.** All gold baseline cases where a reported position exists must produce excerpts containing both the reported position and the response. Zero tolerance for misattributed reported positions.
8. **Evidence extraction completeness.** All Quran and hadith references in gold baselines must be captured in `evidence_refs`.
9. **Consensus behavior.** Test that consensus disagreement produces the expected flags and conservative scores.
10. **Error handling.** Test each error code with synthetic inputs.

**Regression testing:** Re-run all gold baselines when LLM model, prompt template, or consensus configuration changes.

**Integration tests:**
- **Upstream:** Read real atom streams and verify acceptance without schema errors.
- **Downstream:** Produce excerpt streams and verify the taxonomy engine accepts them.
- **End-to-end:** Trace one excerpt from frozen source → normalized package → passage → atoms → excerpt. Verify provenance chain.
