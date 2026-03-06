# Atomization Engine — محرك التذرير — Specification

## 1. Purpose and Scope

The atomization engine breaks each passage into its constituent atoms — the smallest indivisible units of text — and classifies each atom by both structural type and scholarly function. Atomization is where raw text first becomes semantically tagged: definitions are distinguished from evidence, opinion markers from refutations, isnad chains from narrative prose. These classifications are the primary metadata contribution of this engine, flowing downstream through the excerpting engine to the synthesizer (D-023).

**What this engine does:**
- Receives passage records from the passaging engine
- Segments each passage's text into non-overlapping, exhaustive atoms
- Classifies each atom with a two-tier type: structural type (how the text is shaped) and scholarly function type (what role the text plays in scholarly discourse)
- Detects embedded content fragments (Quran quotations, hadith text, poetry citations) within atoms using both rule-based pattern matching and LLM analysis
- Preserves and propagates text layer attribution from the passaging engine
- Produces an atom stream consumed by the excerpting engine

**What is NOT this engine's responsibility:**
- Grouping atoms into excerpts (excerpting engine)
- Determining topic classification or science placement (excerpting and taxonomy engines)
- Correcting text errors or normalization issues (normalization engine)
- Determining passage boundaries (passaging engine)
- Resolving scholar identity for referenced scholars (excerpting engine, using scholar authority model)

**Phase classification:** Phase 2 (source-agnostic, below the normalization boundary). The atomization engine operates on passages produced by the passaging engine. It contains no logic that depends on source type, format, or acquisition method.

**Normalization boundary relationship:** The atomization engine operates entirely below the normalization boundary. It receives passage_text and associated metadata from passage records. It never accesses frozen sources, raw files, or normalized packages directly.

**User scenarios served (reference/USER_SCENARIOS.md):**
- Scenario 1 (study a new source): atomization produces the typed atom stream that the excerpting engine uses to build excerpts. Without atom types, the excerpting engine cannot distinguish definitions from examples from evidence — and the resulting excerpts would be semantically flat.
- Scenario 3 (research a topic): atom type metadata enables the scholar interface to filter by content type (show me only definitions, show me only evidence) within a topic's excerpt collection.
- Scenario 5 (book briefing): atom type distributions per source (ratio of definitions to examples, presence of isnad chains, density of evidence citations) contribute to the source's structural profile that the book briefing presents.
- Scenario 8 (error correction): when the owner flags an atom type as wrong, the correction feeds back into the atomization engine's prompt templates to prevent recurrence.

---

## 2. Input Contract

The atomization engine receives one input per source: the passage stream produced by the passaging engine.

**Input artifact: the passage stream.** Located at library/sources/{source_id}/passages/passages.jsonl. One JSONL record per passage, conforming to the passage schema defined in the passaging engine SPEC §3.

**Fields consumed from each passage record:**

- passage_id: string. Unique identifier for this passage. Becomes the parent reference for all atoms produced from it.
- source_id: string. Primary link to upstream metadata. Passed through to atom records unchanged.
- passage_text: string. The full assembled text of this passage. This is the text that atoms segment. Every character in passage_text must be covered by exactly one atom's anchor_span — no gaps, no overlaps.
- text_layers: array. Layer segments with layer_type, author_canonical_id, start, end, confidence. Used to attribute each atom to the correct text layer and author. If the passage is single-layer, this array contains one segment covering the full text.
- footnotes: array. Footnote records referenced within this passage. Footnotes are atomized separately from main text — each footnote becomes its own atom with source_layer: "footnote".
- structural_format: string. The format strategy applied to this passage (prose/verse/qa_pair/tabular_masala/dictionary_entry/commentary_unit). Determines which format-specific atomization rules apply.
- content_flags: object. has_verse, has_table, has_quran_citation, has_hadith_citation. Provides pre-screening hints that the engine uses to activate specialized detection logic.
- text_fidelity: object. min_score, mean_score, pages_with_warnings. Used to calibrate confidence thresholds — lower-fidelity text gets lower-confidence atom classifications.
- heading_text: string or null. If non-null, the heading text is atomized as a heading structural type atom before the main text. **Heading text is NOT part of passage_text** — it is a separate field from the passaging engine. The heading atom's anchor_span is relative to heading_text (start: 0, end: len(heading_text)), and its offset integrity invariant is: atom_text == heading_text[start:end]. The heading atom is excluded from the V-1 exhaustive coverage check over passage_text. The heading atom's sequence_in_passage is 0; main text atoms start at sequence_in_passage 1 (or 0 if heading_text is null).
- verse_info: object or null. For verse passages, contains verse line data. Used by the verse-specific atomization strategy.
- division_path: array. Hierarchical structural context. Passed through to atom records for provenance.
- review_flags: array. Machine-generated flags from passaging. If low_fidelity_content or mixed_layers is present, the atomization engine applies more conservative classification and lower confidence defaults.

**Validation on input.** Before atomizing a passage, the engine validates:
1. passage_text is non-empty.
2. passage_id matches the expected format (psg_{source_id}_{zero_padded_sequence}).
3. text_layers is non-empty and covers the full span of passage_text (union of all layer segments' [start, end) ranges equals [0, len(passage_text))).
4. structural_format is one of the recognized values.
5. passage_text is in Unicode NFC form. The normalization engine guarantees NFC output; this check is a safety net. If the text is not NFC, the engine normalizes it to NFC and recomputes text_layers offsets accordingly before proceeding. This ensures character offset counting is deterministic — combining character sequences in NFD form would create offset discrepancies between the LLM's view of the text and the engine's offset computation.

If validation fails, the passage is skipped with error ATOM_INVALID_INPUT logged with the passage_id and the specific validation failure. The atom stream for this source is produced without this passage. A review flag is added to the source's processing status.

---

## 3. Output Contract

The atomization engine produces one primary artifact per source: an atom stream.

**Primary artifact: the atom stream.** Written to library/sources/{source_id}/atoms/atoms.jsonl. One JSONL record per atom. Each record conforms to the following schema:

- schema_version: string, format atom_v{major}.{minor}. Current: atom_v2.0.
- atom_id: string, format atm_{source_id}_{zero_padded_sequence} (e.g., atm_src_00147_000042). Globally unique. Monotonically increasing within a source in reading order. Sequence numbers are assigned across the entire source, never reset between passages.
- passage_id: string. The passage this atom belongs to. Links atom to its parent passage.
- source_id: string. The source's canonical identifier. Passed through unchanged from the passage record.
- sequence_in_passage: zero-based integer. Position of this atom within its passage's atom sequence. Authoritative intra-passage ordering.

**Text and location fields:**
- atom_text: string. The verbatim text of this atom, copied exactly from passage_text[anchor_span.start : anchor_span.end]. Never edited, rewritten, or normalized. This is ground truth for all downstream processing.
- anchor_span: object with start (integer, inclusive) and end (integer, exclusive). Character offsets in Unicode codepoints within passage_text. The invariant atom_text == passage_text[start:end] must hold. Verified during self-validation.

**Type classification fields (the two-tier system):**
- structural_type: string, one of the structural type enum (§4.A.3). Describes the physical shape of the text unit.
- scholarly_function: string or null, one of the scholarly function enum (§4.A.3). Describes what role the text plays in scholarly discourse. Null only for heading and whitespace_separator structural types, which have no scholarly function.
- function_confidence: float, range [0.0, 1.0]. Confidence in the scholarly_function classification. Set to 1.0 for rule-based detections (e.g., a Quran verse confirmed against the canonical text). Set to the LLM's assessed confidence for LLM-driven classifications. Below 0.6 triggers a review flag.

**Attribution fields:**
- source_layer: string. The text layer this atom belongs to, derived from the passage's text_layers by matching this atom's character range. One of: matn, sharh, hashiyah, tahqiq, footnote. For single-layer sources, always matn.
- layer_author_id: string or null. The canonical_id of the scholar whose words this atom contains. Derived from text_layers[].author_canonical_id for the matching layer segment. Null only when the layer's author is unidentified.

**Embedded content fields:**
- embedded_refs: array of objects. Each object identifies a fragment of embedded content within this atom's text:
  - ref_type: string, one of: quran_ayah, hadith_text, poetry_line, scholarly_quote, formula.
  - span_start: integer. Start offset within atom_text.
  - span_end: integer. End offset within atom_text.
  - ref_detail: object or null. For quran_ayah: {surah: int, ayah: int, match_confidence: float}. For hadith_text: {collection: string or null, hadith_number: string or null}. For poetry_line: {poet: string or null, diwan: string or null}. For scholarly_quote: {quoted_scholar: string or null}. For formula: null.
  - detection_method: string, one of: pattern_match, canonical_lookup, llm_detected.

**Footnote linkage fields:**
- footnote_source_index: integer or null. For footnote atoms (source_layer == "footnote"), the zero-based index into the passage's footnotes array identifying which footnote this atom derives from. Null for main text atoms. Required non-null when source_layer is "footnote".
- footnote_refs: array of objects. Each object links this atom to a footnote from the passage's footnote array:
  - ref_marker: string. The footnote reference marker text (e.g., "1", matching the ⌜N⌝ marker in the passage text).
  - linked_footnote_atom_id: string or null. The atom_id of the corresponding footnote atom. Null if the footnote was not atomized (footnote text missing from passage record).

**Relationship fields:**
- atom_relations: array of objects. Typed relationships between atoms within the same passage:
  - relation_type: string, one of: illustrates (this example illustrates a definition/rule), evidences (this evidence supports a claim), conditions (this condition/exception qualifies a rule), refutes (this refutation targets a position), continues (this atom continues the previous atom's incomplete thought), responds_to (this atom responds to a scholarly position), footnote_for (this footnote atom annotates a main text atom).
  - target_atom_id: string. The atom_id of the related atom.
  - confidence: float, range [0.0, 1.0].

**Diagnostic fields:**
- classification_notes: string or null. Explanation of non-obvious classification decisions. Null for straightforward atoms. Required non-null when: the atom was reclassified during self-validation, the scholarly function confidence is below 0.7, or the structural type is bonded_cluster.
- bonded_reason: string or null. Required non-null when structural_type is bonded_cluster. Explains why multiple sentences were merged into a single atom (e.g., "condition_with_result", "isnad_chain_with_matn", "verse_with_inline_sharh").
- review_flags: array of strings. Machine-generated flags for human review. Possible values: low_function_confidence (scholarly function confidence < 0.6), ambiguous_layer (atom spans a text_layer boundary with < 0.7 confidence), possible_misattribution (text appears to be quotation but no explicit attribution marker detected, or bonded cluster spans layer boundary), offset_drift_corrected (character offset was adjusted during validation), unresolved_quran_ref (Quran fragment detected but could not be matched to a specific ayah), low_attribution_confidence (an attribution entry has confidence < attribution_confidence_threshold), mid_word_boundary (atom boundary falls within an Arabic word — V-8 violation), coverage_gap_unresolved (synthetic atom inserted to fill a coverage gap that could not be resolved after retries).

**Scholarly attribution fields (§4.B.4):**
- attributions: array of objects or null. Null when `enable_attribution_detection` is false (feature disabled — downstream engines must NOT interpret null as "no attributions detected"). Empty array [] when the feature is enabled but no attributions were detected in this atom. Non-empty array when attributions were detected. Each object identifies a scholarly attribution within this atom:
  - attributed_to: string or null. Raw scholar name, work reference, or school name as it appears in the text. Null for anonymous attributions. NOT a canonical_id — downstream resolution is the excerpting engine's responsibility.
  - attribution_type: string, one of: direct (named scholar), via_work (referenced through a work title), school_collective (attributed to a school), isnad (hadith transmission chain), anonymous (unidentified attribution), self (the source author's own position), refutation_target (position being refuted).
  - work_reference: string or null. Work title referenced (for via_work type).
  - school_scope: string or null. School name (for school_collective and anonymous with school context).
  - isnad_chain: array of strings or null. Ordered transmitter names (for isnad type). Raw names, not canonical IDs.
  - confidence: float, range [0.0, 1.0].
  - marker_text: string. The Arabic text that triggered this attribution detection (e.g., "قال الشافعي").

**Semantic fingerprint fields (§4.B.5):**
- fingerprint_text_hash: string or null. Present when `enable_text_fingerprinting` is true. SHA-256 of the normalized atom text (diacritics stripped, alef/hamza/taa marbuta normalized, particles stripped, words sorted). 64 hex characters.
- fingerprint_key_terms: array of strings or null. Present when `enable_text_fingerprinting` is true. 2-5 key Arabic terms extracted by the LLM representing the atom's conceptual core. Normalized (diacritics stripped).
- fingerprint_embedding: array of floats or null. Present when `enable_semantic_fingerprinting` is true. Semantic embedding vector, truncated to configured dimensions (default 256).

**Guarantees about the atom stream:**

- **Source-agnostic.** The atom schema is identical regardless of source type.
- **Exhaustive coverage.** Every character in passage_text is covered by exactly one main text atom's anchor_span (excluding heading atoms and footnote atoms). No gaps. No overlaps. Heading atoms cover heading_text. Footnote atoms cover their respective footnote texts, not passage_text. This is verified by self-validation.
- **Ordering.** Atoms are ordered by reading order within each passage, and passages are ordered by document order. atom_id sequence numbers are globally monotonic within a source.
- **Offset integrity.** For every main text atom, atom_text == passage_text[anchor_span.start : anchor_span.end]. For every heading atom, atom_text == heading_text[anchor_span.start : anchor_span.end]. For every footnote atom, atom_text == passage.footnotes[footnote_source_index].text[anchor_span.start : anchor_span.end]. These invariants are verified deterministically during self-validation.
- **Layer attribution completeness.** Every atom has a source_layer value. For multi-layer passages, attribution is determined by matching the atom's character range against the passage's text_layers.
- **Type completeness.** Every atom has a structural_type. Every atom except headings and whitespace separators has a scholarly_function. Every scholarly_function has a function_confidence.
- **Metadata pass-through (D-023).** Every atom carries source_id for upstream metadata access and passage_id for passage-level context. The atom type itself is NEW metadata originated by this engine. The layer attribution is carried through from normalization. embedded_refs and atom_relations are new metadata that flows to the excerpting engine and ultimately to the synthesizer.

**Metadata pass-through summary (D-023).** The atomization engine preserves upstream metadata by reference (source_id, passage_id) and adds:
- Atom boundaries and sequence ordering
- Two-tier type classification (structural + scholarly function)
- Layer attribution per atom
- Embedded content references (Quran, hadith, poetry, scholarly quotes)
- Intra-passage atom relationships
- Scholarly attribution chains per atom (§4.B.4) — who is being quoted, through what chain
- Semantic fingerprints per atom (§4.B.5) — text hash, key terms, optional embedding
- Classification confidence and review flags

**Source registry update.** Upon successful atomization of all passages for a source, the source's processing status is updated from passaged to atomized. The atom stream path is recorded.

---

## 4. Processing Specification

### §4.A — Core Processing

#### §4.A.1 — Processing Model

Atomization is per-passage, sequential, and LLM-driven with deterministic pre- and post-processing.

For each passage in the passage stream, the engine executes five phases:

1. **Pre-screen** (deterministic): Examine content_flags, structural_format, text_fidelity, and review_flags. Select the atomization strategy matching the passage's structural_format value (§4.A.7 defines one strategy per format). If text_fidelity.min_score < fidelity_escalation_threshold OR review_flags contains low_fidelity_content, lower the default function_confidence by 0.1 (floor at 0.3) and select the escalation LLM model.
2. **Rule-based pre-detection** (deterministic): Scan passage_text for high-confidence patterns: Quran quotations, hadith evidence markers, isnad chains, poetry markers, footnote reference markers. Mark detected spans with provisional type classifications. This phase runs before the LLM to provide anchoring hints.
3. **LLM atomization** (LLM-driven): Send the passage text, pre-detection hints, structural format, layer information, and few-shot examples to the LLM. The LLM identifies atom boundaries and classifies each atom by structural type and scholarly function. The LLM receives the pre-detected spans as constraints it must respect (it may refine boundaries but not ignore confirmed detections).
4. **Deterministic post-processing**: Verify offset integrity, enforce exhaustive coverage, reconcile LLM output with pre-detection results, assign atom_id values, derive source_layer from passage text_layers, resolve footnote linkages.
5. **Self-validation** (deterministic): Run the validation checks defined in §4.A.10. On failure, attempt auto-repair (up to 2 retries with error feedback to the LLM). If validation still fails after retries, produce the best available result with review flags attached.

**Parallelism.** Passages from the same source are processed sequentially to ensure monotonic atom_id assignment. Passages from different sources may be processed in parallel.

**LLM output format.** The LLM returns a structured JSON array of atom objects, each with: start (character offset), end (character offset), structural_type, scholarly_function, function_confidence, classification_notes, bonded_reason (if bonded_cluster), embedded_refs (if any), and atom_relations (if any). The engine uses the Instructor library (or DSPy with Pydantic models) to enforce schema compliance on LLM output. On schema violation, the engine retries with the validation error message appended to the prompt.

#### §4.A.2 — Atom Boundary Rules

An atom is the smallest indivisible unit of text within a passage. "Indivisible" means: splitting this atom would lose semantic coherence or break a scholarly convention. The following rules govern where atom boundaries are placed.

**Rule AB-1: One scholarly assertion per atom.** Each atom contains exactly one definition, one rule statement, one evidence citation, one example, one opinion statement, or one other scholarly assertion. If a single Arabic sentence contains two definitions ("المبتدأ هو كذا والخبر هو كذا"), those are two atoms — the boundary falls between them. Semantic granularity, not authorial packaging, determines atom boundaries.

**Rule AB-2: Bonded clusters are indivisible.** Certain multi-sentence patterns must remain in a single atom because splitting them would destroy their meaning. Bonded clusters are created when:
- **Condition + result**: "إذا كان كذا فحكمه كذا" (if X then Y). The condition and its result are one atom.
- **Isnad chain + matn**: "حدثنا فلان عن فلان عن فلان قال: ..." (the narrator chain plus the narrated text). The chain and its content are one atom. The chain boundary ends where the narrated content's scholarly assertion ends (not at the first full stop).
- **Verse + immediate sharh**: In commentary passages, when a matn verse line is immediately followed by a one-sentence explanation before the next verse, the verse + explanation form one atom.
- **Question + answer**: In Q&A format passages, each question-answer pair is one atom.
- **Enumerated items with shared predicate**: "ينقسم إلى ثلاثة أقسام: الأول كذا، والثاني كذا، والثالث كذا" (it divides into three categories: first X, second Y, third Z). The predicate and all items form one atom — splitting would orphan the categories from their organizing statement.

Every bonded cluster carries a bonded_reason explaining the trigger.

**Rule AB-3: Headings are atoms.** Division headings, chapter titles, section markers, and any text that functions as a structural label rather than scholarly content is a heading structural type atom. Headings are never merged with adjacent content atoms. If the passage has a heading_text field, that text is the first atom of the passage with structural_type: "heading".

**Rule AB-4: Footnote reference markers are not atoms.** The ⌜N⌝ markers in passage_text are part of the atom they appear in. They are not split into separate atoms. The marker's presence is recorded in footnote_refs on the atom that contains it.

**Rule AB-5: Footnotes are separate atoms.** Each footnote from the passage's footnotes array is atomized as a separate atom with source_layer: "footnote". Footnote atoms appear in the atom stream after all main text atoms for the passage. They are linked to their referencing main text atom via atom_relations with type footnote_for.

**Rule AB-6: Whitespace handling.** Ordinary whitespace (spaces, newlines, blank lines) between content atoms does not become a standalone atom — it is absorbed into the preceding atom's boundary (extending its end offset to include the whitespace). If whitespace appears before the first atom, it is absorbed into the first atom's start (the first atom's start becomes 0). However, explicit section dividers ("***", "---", ornamental separators) that the LLM identifies as intentional structural markers become whitespace_separator atoms with no scholarly_function. Whitespace_separator atoms are rare (typically 0–3 per passage). The exhaustive coverage rule still holds: all characters are assigned to exactly one atom.

**Rule AB-7: Verse lines are atoms.** In verse-format passages, each بيت (verse line) is one atom with structural_type: "verse_line". A بيت consists of two hemistichs (صدر and عجز). The hemistichs are NOT split into separate atoms — the بيت is the atomic unit. Verse numbering from verse_info is preserved in embedded_refs as metadata, not as separate atoms.

#### §4.A.3 — Atom Type Taxonomy

Atoms are classified on two independent dimensions: structural type (the physical shape of the text unit) and scholarly function (the role the text plays in scholarly discourse). This two-tier system ensures that the excerpting engine receives both structural and semantic information.

**Structural types** describe what the text looks like:

| Type | Definition | Example |
|------|-----------|---------|
| prose_sentence | A single complete Arabic sentence. The most common type. | "المبتدأ هو الاسم المرفوع العاري عن العوامل اللفظية" |
| bonded_cluster | Multiple sentences that form an indivisible unit (per AB-2). Always carries bonded_reason. | An isnad chain with its matn, a condition with its ruling. |
| heading | Text functioning as a structural label. No scholarly_function. | "باب المبتدأ والخبر" |
| verse_line | A single بيت of poetry with its two hemistichs. | "كلامُنا لفظٌ مفيدٌ كاستقِمْ *** واسمٌ وفعلٌ ثمّ حرفٌ الكَلِمْ" |
| list_item | One item in an enumeration. The organizing statement is a separate prose_sentence atom. | "الثاني: أن يكون معرفة" |
| table_cell | A single cell from a tabular structure (conjugation tables, comparison matrices). | "يَفْعَلُ" in a conjugation paradigm |
| whitespace_separator | Non-content separator absorbed into the stream for coverage completeness. No scholarly_function. Typically zero or very few per passage. | "***" section divider |

**Scholarly function types** describe what the text does in scholarly discourse:

| Type | Definition | Downstream significance |
|------|-----------|------------------------|
| definition | Defines a term, concept, or category. Identified by definitional patterns ("هو/هي" + noun, "يُعرَّف بأنه", "المراد به"). | Excerpting engine uses definitions as excerpt anchors. Synthesizer uses definitions for comparative analysis across schools. |
| rule_statement | States a grammatical, legal, or logical rule. Identified by normative language ("يجب"، "لا يجوز"، "حكمه"). | Core content for entries. Synthesizer compares rules across schools. |
| evidence_quran | A Quranic quotation used as evidence. Identified by Quran detection (§4.A.4) and evidence marker phrases ("لقوله تعالى"، "والدليل قوله تعالى"). | Excerpting engine tags excerpts with evidence type. Synthesizer distinguishes evidence-based from opinion-based positions. |
| evidence_hadith | A hadith citation used as evidence. May include an isnad chain. Identified by hadith markers ("لقول النبي ﷺ"، "لما رُوي أن"، "في الحديث"). | Excerpting engine preserves isnad as apparatus. Synthesizer can assess evidence strength. |
| evidence_ijma | A claim of scholarly consensus used as evidence ("أجمعوا على"، "بالإجماع"، "لا خلاف في"). | Synthesizer must verify consensus claims against library coverage. |
| evidence_qiyas | An analogical argument ("والقياس على كذا"، "بجامع"، "لأنه في معنى"). | Synthesizer can trace the analogy to its source case. |
| evidence_rational | A rational or logical argument not based on textual source ("لأن"، "إذ"، "بدليل العقل"). | Synthesizer uses these to explain reasoning chains. |
| opinion_statement | A scholar's position on an issue ("وذهب الحنفية إلى"، "والراجح عندي"، "اختار"، "قال"). | Core content for entries. The excerpting engine uses this to identify who holds what position. |
| refutation | A response rejecting another position ("ورُدّ بأن"، "والجواب عن هذا"، "ولا يصح"، "وأُجيب بأن"). | Synthesizer uses refutations to map the dialectical structure of scholarly debates. |
| example | An illustrative example ("نحو"، "مثل"، "كقولك"، "كما في"). | Examples illustrate definitions and rules. The illustrates relation links them to the atom they exemplify. |
| condition_exception | A qualification, exception, or condition on a rule ("إلا إذا"، "بشرط"، "ما لم"، "يُستثنى"). | Synthesizer ensures conditions and exceptions are not lost when summarizing rules. |
| cross_reference | A reference to another scholar, work, or topic ("كما ذكره في"، "وقد تقدم"، "انظر"، "قال صاحب"). | Excerpting engine flags these for resolution. Synthesizer uses them to build the citation network. |
| narration | A transmitted report (hadith matn, athar, historical account) without the narration being used as evidence. | Distinguished from evidence_hadith by context: evidence cites narration to PROVE something; narration simply reports. |
| editorial_note | Text from the tahqiq editor (variant readings, manuscript notes, editorial commentary). Layer is always tahqiq or footnote. | Excerpting engine excludes editorial notes from scholarly content but preserves them as apparatus metadata. |
| structural_transition | Meta-textual statements that organize the discourse ("ثم ننتقل إلى"، "وأما الباب الثاني"، "تنبيه"، "فائدة"). | Not scholarly content per se, but signals that help the excerpting engine determine excerpt boundaries. |
| unclassified | The LLM could not determine a scholarly function with confidence ≥ 0.3. Always triggers low_function_confidence review flag. | Human review determines the correct type. The error is visible, not silent (D-033). |

**Type assignment rules:**
- Every atom gets exactly one structural_type from the structural enum.
- Every atom except heading and whitespace_separator gets exactly one scholarly_function from the function enum, or unclassified if the LLM cannot determine one.
- The two dimensions are independent: a verse_line can have function definition (a versified definition), rule_statement (a versified rule), or example (a verse cited as a grammatical example).
- When a single atom could carry multiple scholarly functions (e.g., a sentence that both states a rule and gives an example), the PRIMARY function is assigned and the secondary function is noted in classification_notes.

#### §4.A.4 — Rule-Based Pre-Detection

Before the LLM processes a passage, deterministic pattern matching identifies high-confidence embedded content. These detections serve two purposes: they provide anchoring constraints for the LLM (preventing it from misclassifying obviously detectable content), and they supply embedded_refs data that would be difficult for the LLM to produce reliably (such as exact surah/ayah references).

**Quran detection.** The engine uses a canonical Quran text database (all 6,236 ayat) and a fuzzy matching algorithm (based on the Quran_Detector approach: matching sequences of 3+ words against the canonical text). When a match is found with confidence ≥ 0.85, the span is marked as quran_ayah in embedded_refs with the surah and ayah numbers. The engine also detects common Quran introduction phrases ("قال تعالى"، "لقوله تعالى"، "قال الله"، "في قوله") that precede quotations.

**Two-level constraint system for Quran detections:** The embedded_ref (quran_ayah in embedded_refs with surah/ayah) is a hard constraint — the LLM may not remove or reclassify a confirmed Quran fragment. The scholarly_function default is evidence_quran, but this is a soft default — the LLM may override it if the surrounding context makes clear the quotation is not being used as evidence (e.g., it appears in a tafsir as the text being explained, or as a linguistic example in a grammar text). When the LLM overrides the default scholarly_function, it must set classification_notes explaining why (e.g., "Quran verse cited as linguistic example for grammatical rule, not as legal evidence"). The embedded_ref remains regardless of the scholarly_function override.

**Hadith marker detection.** The engine scans for standard hadith introduction phrases: "حدثنا"، "أخبرنا"، "عن ... عن ... عن"، "رواه"، "في الصحيحين"، "أخرجه". When an isnad chain pattern is detected (a sequence of "عن" or "حدثنا" connecting proper names), the span is marked as containing an isnad chain. The engine does NOT attempt to resolve hadith identity at this stage — that is the excerpting engine's responsibility. The pre-detection marks the span and provides the raw isnad text for downstream processing.

**Evidence marker detection.** The engine maintains a lexicon of evidence introduction phrases for each evidence type:
- Quran evidence: "لقوله تعالى"، "والدليل قوله تعالى"، "بدليل الكتاب"
- Hadith evidence: "لقول النبي ﷺ"، "لما رُوي أن"، "والدليل من السنة"
- Consensus evidence: "أجمعوا على"، "بالإجماع"، "لا خلاف في"
- Analogical evidence: "والقياس على"، "بجامع"، "بعلة"

When a marker phrase is detected, the LLM is hinted that the following text likely has the corresponding evidence_* scholarly function. The hint is advisory — the LLM may override it if the context indicates otherwise.

**Poetry marker detection.** Verse text is identified by: the presence of verse_info in the passage record (most reliable), hemistichal structure markers, or common poetry citation phrases ("قال الشاعر"، "كقول"، "ومنه قوله"). In verse-format passages, this detection is redundant with the format-specific strategy (§4.A.7). In prose-format passages, it detects embedded poetry citations.

**Footnote marker detection.** The engine scans for ⌜N⌝ markers (D-031) in passage_text. Each detected marker is recorded with its character offset and reference number for linking to footnote atoms in post-processing.

#### §4.A.5 — LLM-Driven Type Classification

The LLM performs the core atomization work: determining atom boundaries and classifying each atom. The prompt includes:

**System prompt components:**
1. The atom boundary rules (§4.A.2), distilled to behavioral instructions.
2. The structural type and scholarly function type enums with brief definitions.
3. Format-specific rules based on structural_format (§4.A.7).
4. Layer attribution context: which layers are present in this passage and what each layer represents.

**Per-passage prompt components:**
1. The full passage_text.
2. The passage's structural_format and content_flags.
3. Pre-detection results: spans identified by rule-based detection (§4.A.4), with their provisional types. The LLM is instructed to respect these as constraints for high-confidence detections and as hints for lower-confidence ones.
4. Two few-shot examples from the gold baseline set (§10), selected by structural format match: the engine picks the two gold examples whose structural_format matches the current passage's structural_format. If fewer than two format-specific gold examples exist, the engine fills remaining slots with prose-format gold examples (prose is the most common format and provides the broadest coverage).

**LLM output requirements:**
1. Atoms must be returned as a JSON array, ordered by character offset.
2. The union of all atom spans must cover the entire passage_text with no gaps and no overlaps. (This applies to main text atoms only; footnote atoms are produced separately in §4.A.9.)
3. Each atom must have start, end, structural_type, and (unless heading/whitespace) scholarly_function with function_confidence.
4. Bonded clusters must include bonded_reason.
5. The LLM may include classification_notes for non-obvious decisions.
6. The LLM may identify atom_relations between atoms in the passage.

**Structured output enforcement.** The engine uses the Instructor library with a Pydantic model defining the expected output schema. Instructor enforces schema compliance and automatically retries (up to 2 retries) with the validation error message when the LLM produces non-conforming output.

**Model selection.** Atomization uses the configured primary LLM (default: Claude Sonnet via Anthropic API). For sources with text_fidelity.min_score < 0.5 or passages flagged with low_fidelity_content, the engine escalates to a stronger model (default: Claude Opus) for higher classification accuracy.

#### §4.A.6 — Multi-Layer Attribution

In multi-layer texts (matn/sharh/hashiyah), each atom must be attributed to the correct text layer and author. The atomization engine determines this by matching each atom's character range against the passage's text_layers array.

**Attribution algorithm:**
1. For each atom with anchor_span [start, end), find all text_layer segments that overlap with this range.
2. If exactly one layer segment covers the atom's full range, assign that layer's layer_type and author_canonical_id.
3. If the atom spans a layer boundary (its range overlaps two or more layer segments), apply the following:
   - **If the atom is NOT a bonded_cluster:** Assign the layer that covers the largest portion of the atom (majority rule). Set review_flags: ["ambiguous_layer"] and record the overlap details in classification_notes.
   - **If the atom IS a bonded_cluster:** A bonded cluster spanning a layer boundary is a high-risk misattribution scenario (T-2). Do NOT apply the majority rule — instead, assign the layer of the FIRST segment in the cluster (the scholarly convention is that the introducing voice determines attribution), set review_flags: ["ambiguous_layer", "possible_misattribution"], and record in classification_notes: which portion belongs to which layer, the bonded_reason, and why splitting would destroy meaning. This ensures human review catches the case where (e.g.) a matn quotation is bonded with its commentary explanation — the entire cluster is conservatively attributed to the first layer, and the human gate resolves the correct attribution.
4. If no layer segment covers the atom's range, or layer segments cover only part of the atom's range (a gap in text_layers), assign source_layer: "matn" as the conservative default (D-030 applies at the passage level; atoms inherit from their passage's layers). Set review_flags: ["ambiguous_layer"]. A partial coverage gap (layer segments cover some but not all of the atom's character range) is treated identically to a full gap — the conservative default applies to the entire atom. This scenario should be rare because input validation (§2 step 3) requires text_layers to cover all of passage_text; a partial gap indicates an upstream bug in the passaging engine.

**Layer type mapping.** The passage's text_layers[].layer_type values (from the normalization engine's LayerType enum) map to the atom's source_layer as follows:
- matn → source_layer: "matn"
- sharh → source_layer: "sharh"
- hashiyah → source_layer: "hashiyah"
- tahqiq_note → source_layer: "tahqiq"
- uncertain → source_layer: "matn" (conservative default per D-030). Set review_flags: ["ambiguous_layer"].

**LLM layer override.** The LLM may detect that text attributed to one layer by the normalization engine actually belongs to a different layer. The most common case: a passage in a sharh where the commentator writes "قال المصنف" and then quotes the matn author's words — the normalization engine may have classified the entire passage as Layer 2 (sharh), but the quoted words are actually Layer 1 (matn). When the LLM detects such an implicit layer transition, it marks the atom with the corrected layer and sets classification_notes explaining the override. This correction propagates to the atom's source_layer and layer_author_id fields. The review_flags: ["possible_misattribution"] flag is set for human verification.

#### §4.A.7 — Format-Specific Atomization

The passage's structural_format determines which format-specific rules supplement the universal boundary rules (§4.A.2).

**Prose format** (structural_format: "prose"). Default behavior. The LLM identifies sentence boundaries and scholarly function transitions. The primary challenge is determining where one scholarly assertion ends and another begins in flowing Arabic prose, which often uses long coordinated sentences. The LLM is instructed to split at the scholarly function level, not at the Arabic sentence level: a single Arabic sentence containing a definition, an example, and a rule becomes three atoms.

**Verse format** (structural_format: "verse"). Each بيت is one atom (Rule AB-7). The verse_info field provides verse line data that the engine uses to verify the LLM's verse boundary detection. If verse_info.verse_lines and the LLM's verse detection disagree on the number of verse lines, the engine trusts verse_info (it comes from the normalization engine's structure discovery, which has higher accuracy for verse boundaries). Commentary text interspersed between verse lines in verse-format passages is atomized as separate prose atoms attributed to the commentary author.

**Q&A format** (structural_format: "qa_pair"). Question-answer pairs are bonded clusters (Rule AB-2). The question is always a prose_sentence or bonded_cluster with scholarly function varying by context. The answer is the primary scholarly content. If a Q&A passage contains multiple sequential Q&A pairs, each pair is one atom.

**Tabular format** (structural_format: "tabular_masala"). Each table row or distinct scholarly position within the tabular structure is atomized separately. If the table has a header row, it becomes a heading atom. Individual cells within a row may become separate atoms if they contain independent scholarly assertions (e.g., in a khilaf table: each school's position is a separate opinion_statement atom).

**Dictionary format** (structural_format: "dictionary_entry"). The lemma/entry word is a heading atom. The definition body is atomized by scholarly function just like prose. Sense numbers create list_item structural types.

**Commentary format** (structural_format: "commentary_unit"). This is the most complex format because it contains interleaved text from different authors. The key rule: the matn quotation at the start of the passage is one atom with source_layer: "matn" and layer_author_id pointing to the matn author. The commentary that follows is atomized as separate atoms with source_layer: "sharh". Layer transitions marked by phrases like "قال المصنف" or "قوله" (his words) trigger layer attribution changes on subsequent atoms until the commentary resumes.

#### §4.A.8 — Character Offset Integrity

Character offsets are the foundation of atom-to-passage linkage. An offset error corrupts downstream excerpt construction. The following measures ensure offset integrity.

**Invariant.** For every main text atom (source_layer != "footnote", structural_type != "heading"): atom_text == passage_text[anchor_span.start : anchor_span.end]. For every heading atom (structural_type == "heading"): atom_text == heading_text[anchor_span.start : anchor_span.end]. For every footnote atom (source_layer == "footnote"): atom_text == passage.footnotes[footnote_source_index].text[anchor_span.start : anchor_span.end]. These are hard invariants verified by the self-validation phase on every atom of every passage.

**LLM offset correction.** LLMs frequently produce slightly incorrect character offsets, especially for Arabic text with diacritics. The post-processing phase applies a correction algorithm:
1. For each atom the LLM returns, extract the text at [start, end) from passage_text.
2. Compare the extracted text with the atom_text the LLM provided.
3. If they match exactly, no correction needed.
4. If they don't match, search for the LLM's atom_text within a ±50 character window around the LLM's reported offset in passage_text. Use fuzzy string matching (Levenshtein distance ≤ 3 characters) to handle minor diacritical differences.
5. If a match is found, correct the offsets and set review_flags: ["offset_drift_corrected"].
6. If no match is found, flag the atom with error ATOM_OFFSET_UNRESOLVABLE and include it in the atom stream with the LLM's reported offsets and atom_text, plus a review flag. The self-validation phase will detect the invariant violation.

**Coverage enforcement.** After all main text atoms are assigned, the post-processing phase checks that the union of all main text atom [start, end) ranges equals [0, len(passage_text)). If a gap exists between two adjacent atoms, the gap is absorbed into the preceding atom: its end boundary is extended to the following atom's start, AND its atom_text is updated to passage_text[atom.start : new_end]. Both the span and the text are corrected together to maintain the offset integrity invariant. If a gap exists before the first atom, the first atom's start is moved to 0 and its atom_text is updated similarly. The adjustment is logged with ATOM_COVERAGE_GAP_REPAIRED. If overlaps exist, the later atom's start is moved forward to the earlier atom's end and its atom_text is updated to passage_text[new_start : atom.end]. The adjustment is logged with ATOM_COVERAGE_OVERLAP_REPAIRED. In all cases, the review flag "offset_drift_corrected" is set on the adjusted atom.

#### §4.A.9 — Footnote Atomization

Each footnote in the passage's footnotes array is processed as a separate atom or set of atoms appended after the main text atoms.

**Processing rules:**
1. Each footnote's text field is treated as an independent mini-passage. If a footnote's text is empty or whitespace-only, no atom is produced for it — the footnote_for relation on the referencing main text atom has linked_footnote_atom_id set to null.
2. If the footnote text contains a single assertion, it becomes one atom with source_layer: "footnote" and scholarly_function determined by its content (editorial_note for tahqiq footnotes; evidence_*, cross_reference, or the LLM-determined function for substantive footnotes).
3. If the footnote text contains two or more assertions, it is split into that many footnote atoms following the standard boundary rules.
4. Footnote atoms' anchor_span values are relative to the footnote's own text, NOT to passage_text. The footnote_source_index field (integer) records which footnote in the passage's footnotes array this atom references (zero-based index). The offset integrity invariant for footnote atoms is: atom_text == passage.footnotes[footnote_source_index].text[anchor_span.start : anchor_span.end]. This is a variant of the main text invariant, using the footnote text as the reference instead of passage_text.
5. Each footnote atom is linked to the main text atom that contains the ⌜N⌝ marker via an atom_relations entry with relation_type: "footnote_for".

**Footnote type classification.** The footnote_type from the passage's footnotes array guides classification:
- editor_footnote → default scholarly function editorial_note
- source_footnote → scholarly function determined by content (usually cross_reference or evidence_*)
- unknown → LLM determines scholarly function

#### §4.A.10 — Self-Validation

After atomization of each passage, the engine runs seven automated checks. Each check either passes, triggers auto-repair, or flags for human review.

**Check V-1: Exhaustive coverage.** Verify that the union of all main text atom (source_layer != "footnote" AND structural_type != "heading") [start, end) ranges equals [0, len(passage_text)). Heading atoms are excluded because their offsets reference heading_text, not passage_text. Footnote atoms are excluded because they cover their respective footnote texts, not passage_text. If a gap or overlap is found in main text atom coverage, apply the correction algorithm from §4.A.8. If correction fails, flag ATOM_COVERAGE_VIOLATION.

**Check V-2: Offset integrity.** Verify that for every main text atom (source_layer != "footnote", structural_type != "heading"), atom_text == passage_text[anchor_span.start : anchor_span.end]. For every heading atom (structural_type == "heading"), verify atom_text == heading_text[anchor_span.start : anchor_span.end]. For every footnote atom (source_layer == "footnote"), verify atom_text == passage.footnotes[footnote_source_index].text[anchor_span.start : anchor_span.end]. Any violation is a hard failure — see failure handling below.

**Check V-3: No empty atoms.** Verify that every atom has len(atom_text) > 0. Empty atoms are removed from the stream. This should not happen if coverage is exhaustive, but is checked independently.

**Check V-4: Ordering consistency.** Verify that main text atoms are ordered by anchor_span.start within each passage. Footnote atoms follow all main text atoms, ordered by footnote_source_index then by anchor_span.start within each footnote. Verify that sequence_in_passage values are zero-based and contiguous across all atoms (main text + footnotes).

**Check V-5: Type completeness.** Verify that every atom has a structural_type. Verify that every atom except heading and whitespace_separator has a scholarly_function (which may be unclassified). Verify that every non-null scholarly_function has a function_confidence in [0.0, 1.0].

**Check V-6: Layer attribution.** For multi-layer passages, verify that every atom has a source_layer value and that the distribution of layers across atoms is plausible (e.g., a commentary passage should have both matn and sharh atoms; if all atoms are matn, flag ATOM_LAYER_DISTRIBUTION_SUSPICIOUS).

**Check V-7: Bonded cluster integrity.** Verify that every atom with structural_type: "bonded_cluster" has a non-null bonded_reason. Verify that no bonded cluster contains only a single sentence (it should be a prose_sentence instead).

**Check V-8: Word boundary integrity.** Verify that no main text atom's anchor_span.start or anchor_span.end falls in the middle of an Arabic word. Specifically: for each atom boundary offset (excluding offset 0 and offset len(passage_text)), the character immediately before the offset or immediately after the offset must be whitespace, punctuation, or a paragraph boundary. Exception: list_item and table_cell atoms may have boundaries adjacent to structural delimiters (e.g., "|" in tables) without whitespace. Violations are soft failures — set review_flags: ["mid_word_boundary"] and log a warning. This check catches LLM offset errors that split Arabic words, which would produce semantically corrupt atoms.

**On validation failure.** The engine distinguishes between hard failures and soft failures.

Hard failures (V-2: offset integrity): trigger re-atomization of the passage with the validation error included in the LLM prompt (up to 2 retries). If all retries fail, the passage is excluded from the atom stream — no atoms are written for this passage. The passage_id is recorded in the source's processing status with error ATOM_OFFSET_INTEGRITY_FAILURE, and the source is flagged for human review. An excluded passage is preferable to atoms with corrupt offsets, because corrupt offsets produce corrupt excerpts downstream (T-1 silent text corruption).

Hard failures (V-1: coverage): trigger re-atomization (up to 2 retries). If retries fail, the engine writes the atoms it has with a coverage gap marker. The gap regions are recorded as synthetic atoms with structural_type: "whitespace_separator", scholarly_function: null, and review_flags: ["coverage_gap_unresolved"]. This preserves what the LLM produced while making the gap visible. The source is flagged for human review.

Soft failures (V-3, V-5, V-6, V-7): produce review flags on the affected atoms but do not block the atom stream from being written.

### §4.B — Transformative Capabilities

#### §4.B.1 — Rhetorical Structure Analysis

**Capability:** Detect the flow of scholarly argumentation within a passage and annotate atoms with their role in the argumentation structure.

Arabic scholarly texts follow recognizable rhetorical patterns. A typical pattern in a fiqh text: (1) state the issue (تحرير المسألة), (2) present the first school's position (مذهب), (3) present their evidence (دليل), (4) present the opposing position, (5) present their evidence, (6) refute the weaker position (ردّ), (7) state the preponderant opinion (ترجيح). In a grammar text: (1) define the concept, (2) give the rule, (3) give examples, (4) state exceptions, (5) cite Sibawayhi's position, (6) note the Kufan disagreement.

These patterns are not rigid, but they are recognizable. The atomization engine detects them by analyzing the sequence of scholarly function types across atoms within a passage. When a recognized pattern is detected, each atom in the pattern receives an atom_relations entry linking it to the other atoms in the pattern with the relation types specified in the matching template (from the enum: illustrates, evidences, conditions, refutes, continues, responds_to).

**Technical approach:** After the LLM assigns scholarly function types to all atoms in a passage, a post-processing step runs a pattern matcher over the sequence of types. The matcher uses a library of rhetorical pattern templates (defined in configuration, not hardcoded). Each template specifies: a sequence of scholarly function types (with optional elements and wildcards), the specific relation types to assign between matched atoms (from the atom_relations enum: illustrates, evidences, conditions, refutes, continues, responds_to), and a pattern name.

**Example pattern: issue-opinion-evidence-refutation.**
Template: [rule_statement|opinion_statement] → [evidence_*]{1,3} → [refutation] → [evidence_*]{0,3}
When this pattern matches, the engine links: the refutation atom responds_to the first opinion atom, each evidence atom evidences the opinion it follows.

**Pattern matching is advisory, not authoritative.** Detected patterns are recorded as atom_relations with confidence scores. They inform the excerpting engine about natural grouping boundaries but do not override the excerpting engine's own grouping decisions. If the pattern matcher and the LLM's atom relations disagree, both are preserved — the excerpting engine sees both perspectives.

**Feasibility.** This capability uses sequence pattern matching over a finite set of scholarly function types — a computationally trivial operation after the LLM has classified atoms. The scholarly pattern templates require domain expertise to define (initial set during implementation, expanded via feedback loop). The LLM already handles the hard part (classifying atoms); this capability extracts structure from those classifications.

[NOT YET IMPLEMENTED] — Full specification provided. Depends on: the scholarly function type taxonomy being finalized (§4.A.3) and gold baselines for pattern validation.

#### §4.B.2 — Implicit Layer Transition Detection

**Capability:** Detect when a scholar quotes or paraphrases another scholar without explicit attribution markers, and flag these transitions as potential layer changes.

Explicit layer transitions are handled by §4.A.6 — phrases like "قال المصنف" make the layer change obvious. But many scholarly texts contain implicit transitions: the author shifts from their own commentary into paraphrasing the matn without any explicit marker. These implicit transitions are dangerous because they can cause misattribution: the matn author's position is credited to the commentator, or vice versa.

**Detection signals:** The LLM is trained to detect implicit layer transitions by watching for:
- **Register shifts:** Classical Arabic scholarly texts have distinctive register differences between matn (terse, definitional) and sharh (expansive, explanatory). A sudden shift from elaborate commentary to terse definitional language may indicate an unattributed matn quotation.
- **Terminological inconsistency:** If the matn author uses term A and the commentary author uses term B for the same concept, a switch from term B to term A mid-commentary may indicate an implicit quotation.
- **Pronoun shifts:** The commentator refers to the matn author in third person ("he said", "his position is"). A shift to first person ("I define X as") in the middle of third-person commentary may indicate an unattributed self-quotation.
- **Content that contradicts the commentary's stated position:** If the commentator has been arguing position X and suddenly text appears arguing position Y without an attribution marker, this may be an implicit quotation of the matn or of an opposing scholar.

**Output.** When the LLM detects a potential implicit layer transition, it marks the affected atom with review_flags: ["possible_misattribution"] and records the evidence in classification_notes (e.g., "Register shift from expansive sharh to terse definitional language; possible unattributed matn quotation"). The source_layer is set to the LLM's best guess, not to the passage-level default. The low-confidence flag ensures human review before the attribution enters the permanent record.

**Technical approach.** The LLM prompt for multi-layer passages includes specific instructions to watch for register shifts and terminological inconsistencies. This is LLM-native capability — the LLM's understanding of Arabic scholarly register is the detection mechanism. No specialized NLP model is needed; the general-purpose LLM with domain-specific prompting performs this detection as part of its atomization pass.

**Why this is transformative.** Implicit layer transitions are a major source of misattribution in Islamic scholarly tools. Existing tools either ignore layer structure entirely (treating everything as one author's words) or only handle explicit markers. Detecting implicit transitions prevents the most dangerous form of scholarly error: putting words in the wrong scholar's mouth. Even at moderate accuracy (60-70%), flagging potential misattributions for human review is vastly better than silent misattribution.

[NOT YET IMPLEMENTED] — Full specification provided. Depends on: multi-layer passage handling being implemented in the normalization engine, and gold baselines for multi-layer texts.

#### §4.B.3 — Atom Type Distribution Analytics

**Capability:** Compute and store a statistical profile of atom types per passage and per source, enabling downstream engines to make informed decisions and the scholar interface to characterize sources.

After atomizing all passages for a source, the engine computes an atom type distribution report:

**Per-passage statistics:**
- Total atom count, atoms per structural type, atoms per scholarly function
- Ratio of evidence atoms to opinion atoms (evidence density)
- Ratio of example atoms to definition/rule atoms (illustration density)
- Presence of isnad chains (hadith-heavy indicator)
- Count of bonded clusters by trigger type
- Mean and standard deviation of scholarly function confidence
- Count and types of review flags

**Per-source aggregate statistics:**
- All per-passage statistics aggregated (sum, mean, std dev)
- Source-level structural profile: is this source primarily definitional, evidential, argumentative, or mixed?
- Anomaly detection: passages whose type distribution deviates more than 2 standard deviations from the source mean (e.g., a suddenly evidence-heavy passage in an otherwise definition-focused text may indicate a chapter transition)

**Storage.** The distribution report is written to library/sources/{source_id}/atoms/distribution_report.json. This is a machine-readable artifact consumed by the excerpting engine (for excerpt boundary hinting), the scholar interface (for book briefing §D-022), and the quality monitoring system.

**Why this is transformative.** No existing Islamic scholarly tool characterizes sources by their argumentative structure. Knowing that a source is "85% definitional, 10% examples, 5% evidence" versus "40% opinion statements, 35% evidence, 25% refutations" tells the user and the system fundamentally different things about how to read and use that source. The excerpting engine can adjust its grouping strategy based on the distribution (evidence-dense passages warrant different excerpt boundaries than definition-dense ones). The scholar interface can recommend sources for different study needs: "for understanding the evidence debates, read Source A; for learning definitions, read Source B."

**Technical approach.** Trivial computation: iterate over atom records and count types. No LLM needed. The insight is in the data's existence and its downstream consumption, not in computational complexity.

[NOT YET IMPLEMENTED] — Full specification provided. No external dependencies beyond the atom stream itself.

#### §4.B.4 — Scholarly Attribution Chain Resolution

**Capability:** Detect and structure the nested attribution patterns within individual atoms, resolving WHO is being quoted, cited, or attributed — not just that an atom is an "opinion_statement," but whose opinion it is and through what chain of transmission.

Arabic scholarly texts use richly layered attribution that is far more complex than Western-style citation. A single atom may contain a chain like: "قال الماوردي: قال الشافعي: حدثنا مالك عن نافع عن ابن عمر عن النبي ﷺ" — al-Mawardi transmitting al-Shafi'i transmitting Malik transmitting Nafi' transmitting Ibn 'Umar transmitting the Prophet. This is NOT just metadata about "who holds this opinion" — it is a structured provenance chain where each link carries different scholarly weight.

**Attribution pattern types detected:**

| Pattern | Arabic Markers | Output |
|---------|---------------|--------|
| Direct scholar attribution | "قال X"، "ذهب X إلى"، "يرى X أن"، "عند X" | attributed_to: scholar name, type: direct |
| Work-based attribution | "في المغني"، "صاحب الهداية"، "قال في الكتاب" | attributed_to: work reference, type: via_work, requires scholar authority resolution |
| School-level attribution | "مذهب الحنفية"، "وعند الشافعية"، "الحنابلة قالوا" | attributed_to: school name, type: school_collective |
| Isnad chain attribution | "حدثنا X عن Y عن Z" (≥2 transmitters) | attribution_chain: ordered list of transmitters, type: isnad |
| Anonymous partial | "قال بعض أصحابنا"، "ذهب بعضهم"، "قيل" | attributed_to: null, type: anonymous, scope: (same_school / unspecified) |
| Reflexive (author's own) | "والراجح عندي"، "قلت"، "والصواب" | attributed_to: source_author, type: self |
| Counter-attribution (refutation target) | "ورُدّ عليه"، "وأُجيب بأن"، "ولا يصح هذا" | responds_to: preceding attributed atom, type: refutation_target |

**Processing approach:** Attribution detection runs as a sub-task within LLM atomization (§4.A.5). The LLM prompt includes attribution pattern examples and instructs the model to populate the `attributions` field on each atom. For isnad chains, the LLM segments the chain into individual transmitter names (unresolved — the scholar authority model resolves canonical identity downstream in the excerpting engine). The LLM does NOT attempt to resolve "صاحب المغني" to "ابن قدامة" — it outputs the raw reference for downstream resolution. It DOES attempt to resolve obvious cases where the attribution is unambiguous within the passage context (e.g., "قال المصنف" always refers to the matn author per source metadata).

**Output structure per atom:**
```
attributions: [
  {
    attributed_to: "الشافعي" | null,
    attribution_type: "direct" | "via_work" | "school_collective" | "isnad" | "anonymous" | "self" | "refutation_target",
    work_reference: "الأم" | null,
    school_scope: "شافعي" | null,
    isnad_chain: ["مالك", "نافع", "ابن عمر"] | null,
    confidence: 0.0-1.0,
    marker_text: "قال الشافعي في الأم"
  }
]
```

An atom may have zero attributions (e.g., a definition without attribution is the source author's own), one (the common case), or multiple (nested attribution: "قال الماوردي: قال الشافعي" produces two attribution entries, one for each layer).

**Interaction with text layers (§4.A.6).** In multi-layer texts, the attribution chain includes the layer structure. When a sharh author (Layer 2) quotes the matn author (Layer 1) using "قال المصنف," the atom's source_layer is set to "matn" AND an attribution entry records this as a Layer 2 → Layer 1 transition. When the sharh author then quotes a THIRD scholar within the commentary, that produces a separate attribution entry. The layer attribution and scholarly attribution are complementary, not redundant: layers tell you WHOSE TEXT this is physically; attributions tell you WHOSE POSITION is being described.

**Why this is transformative.** No existing Islamic studies tool structures the attribution within scholarly text. Current tools either ignore it entirely (treating all text as the source author's words) or capture it only at the book level (metadata says "the author is X"). KR's atom-level attribution enables the synthesizer to answer: "Show me all positions attributed to al-Shafi'i across the library" — gathering not just passages FROM al-Shafi'i's own books, but every time ANY author in the library QUOTES al-Shafi'i. This reconstructs a scholar's complete intellectual footprint across the entire corpus — including positions transmitted by later scholars that may not appear in the original works (because many early works are lost, known only through quotation in later texts).

**Research validation.** IslamicLegalBench (2026) showed that even the best LLMs achieve only ~67% accuracy on Islamic legal reasoning tasks, with 21% hallucination. However, attribution detection is a much more constrained task than legal reasoning — it is pattern recognition over well-defined Arabic markers, not open-ended inference. The LLM is not being asked to evaluate the strength of a legal argument; it is being asked to detect "قال X" patterns and structure them. This is closer to NER (named entity recognition) than to legal reasoning, and LLMs perform significantly better on structured extraction tasks. Expected accuracy: 80-90% for direct attributions, 60-70% for anonymous/implicit attributions (the latter requiring human review flags).

[NOT YET IMPLEMENTED] — Full specification provided. Depends on: core atomization implementation (§4.A), and scholar authority model interface for downstream resolution of raw scholar names to canonical IDs (excerpting engine responsibility).

#### §4.B.5 — Atom-Level Semantic Fingerprinting

**Capability:** Generate a normalized canonical fingerprint for each content atom that enables downstream engines to detect when the same scholarly content (definition, rule, evidence citation) appears across multiple sources — even when the wording differs slightly.

The same definition of المبتدأ appears in dozens of grammar books across 14 centuries. Sometimes word-for-word identical (because later scholars quote earlier ones). Sometimes paraphrased. Sometimes compressed or expanded. When the excerpting engine produces excerpts from 20 sources that all define المبتدأ, the taxonomy engine places them all at the same leaf, and the synthesizer encounters 20 near-duplicate definitions. Without fingerprinting, the synthesizer must rely on its own LLM judgment to detect duplicates — error-prone and opaque. With fingerprints, the synthesizer can group semantically equivalent atoms BEFORE synthesis, producing cleaner entries.

**Fingerprint generation (three-tier):**

**Tier 1 — Normalized text hash (deterministic, fast).** The atom's text is normalized by: (a) stripping all diacritics (tashkil), (b) normalizing alef variants (أ/إ/آ → ا), taa marbuta (ة → ه for matching purposes only), and hamza forms, (c) removing common particles and connectives (و، ف، ثم، لكن) from the start, (d) sorting words by Unicode codepoint order (not Arabic alphabetical order — Unicode order is deterministic and locale-independent). The resulting normalized string is SHA-256 hashed. Exact textual duplicates (modulo diacritics and orthographic variants) produce identical hashes. This tier catches verbatim quotations across sources. Output: `fingerprint_text_hash` (string, 64 hex chars).

**Tier 2 — Key term extraction (LLM-assisted, medium cost).** During atomization, the LLM extracts 2-5 key Arabic terms from each atom — the conceptual core independent of phrasing. For a definition of المبتدأ, the key terms might be: [المبتدأ، اسم، مرفوع، عوامل، ابتداء]. These are stored as `fingerprint_key_terms` (array of strings, normalized). Two atoms sharing ≥70% of their key terms are candidate semantic duplicates even if their full text differs. This tier catches paraphrases and reformulations.

**Tier 3 — Semantic embedding (model-based, highest cost).** The atom text is embedded using an Arabic semantic model (Swan-Large or Arabic-STS-Matryoshka, per RESOURCES.md). The resulting vector (truncated to 256 dimensions via Matryoshka) is stored as `fingerprint_embedding` (array of floats). Cosine similarity ≥ 0.85 between embeddings indicates strong semantic overlap. This tier catches deep paraphrases where the same concept is expressed in completely different words. Embedding computation is deferred by default — Tier 3 runs only when `enable_semantic_fingerprinting` is true in configuration, because it requires a GPU-resident embedding model.

**Fingerprint is NOT identity.** Two atoms with matching fingerprints are CANDIDATES for deduplication — not confirmed duplicates. The synthesizer or excerpting engine makes the final deduplication decision because context matters: the same definition from a 2nd-century AH source and a 7th-century AH source may be textually identical but carry different scholarly weight. Fingerprints enable detection; downstream engines decide what to do with the detection.

**Storage and downstream consumption.** Fingerprint fields are part of the atom record (§3). They are metadata that flows forward (D-023). The excerpting engine uses them to detect when multiple atoms within an excerpt are redundant. The taxonomy engine uses them to pre-group atoms at a leaf before synthesis. The synthesizer uses them to present unique content once (citing the strongest source) rather than repeating near-identical definitions from 20 sources.

**Scalability consideration.** Tier 1 (text hash) is O(1) per atom — trivially fast. Tier 2 (key terms) is part of the existing LLM call — marginal cost. Tier 3 (embedding) adds one embedding model call per atom — significant at scale. For a 15-volume work producing ~50,000 atoms, Tier 3 adds ~50,000 embedding calls. At 1000 embeddings/second (batch processing with Swan-Large on a consumer GPU), this adds ~50 seconds. Acceptable.

**Why this is transformative.** No existing Islamic studies tool detects conceptual duplicates across sources at the sub-paragraph level. The KITAB project's text reuse detection operates at 300-word chunks — too coarse to detect that two books contain the same one-sentence definition. Islamic scholarly tradition is deeply intertextual: later scholars routinely reproduce earlier scholars' exact definitions, often without attribution. Atom-level fingerprinting reveals this intertextual web at the finest meaningful granularity. Over time, as the library grows, the fingerprint database becomes a map of how scholarly concepts are transmitted, transformed, and preserved across centuries — making visible the invisible "DNA" of the Islamic intellectual tradition.

**Cross-source fingerprint index.** After atomizing a source, the engine registers all fingerprints in a source-level fingerprint manifest (`library/sources/{source_id}/atoms/fingerprint_manifest.json`). When the library has multiple sources, a background process (or the taxonomy engine) can cross-reference fingerprints across sources to build a library-wide duplicate detection index. This index is a shared resource, not owned by the atomization engine — the atomization engine produces the fingerprints; consumption is downstream.

[NOT YET IMPLEMENTED] — Full specification provided. Depends on: Arabic text normalization utilities from CAMeL Tools (Tier 1), core LLM atomization producing key terms (Tier 2), Arabic embedding model deployment (Tier 3). Tier 1 and Tier 2 can be implemented immediately; Tier 3 requires embedding model infrastructure.

---

## 5. Validation and Quality

The atomization engine's validation architecture has three layers, following the quality framework established in VISION.md §8.

**Layer 1: Self-validation (§4.A.10).** Automated checks run on every passage immediately after atomization. Seven checks covering offset integrity, coverage, typing, ordering, layer attribution, and bonded cluster integrity. This layer catches mechanical errors: wrong offsets, missing types, schema violations. Self-validation is mandatory and blocking — the atom stream is not written to disk until all hard checks pass.

**Layer 2: Cross-passage consistency checks.** After all passages for a source are atomized, the engine runs cross-passage validation:
- **Monotonic atom_id:** Verify that atom_id sequence numbers are globally monotonic across all passages.
- **Source-level layer plausibility:** If the source metadata declares the source as multi-layer (commentary), verify that at least one passage produced atoms with source_layer values from multiple layers. If all atoms are matn, either the source metadata is wrong or the layer detection failed.
- **Type distribution sanity:** Using the distribution report (§4.B.3), flag anomalies that suggest systematic classification errors (e.g., 100% of atoms classified as prose_sentence with no scholarly function variety suggests the LLM prompt was ineffective).

**Layer 3: Human gate integration.** The atomization engine does not have a dedicated human gate. Instead, human review is triggered by review flags on individual atoms. The excerpting engine's human gate reviews flagged atoms as part of excerpt review — atoms are intermediate artifacts whose classification decisions are most meaningful in the context of the excerpts they form. However, two conditions trigger source-level human review escalation:
- More than 20% of atoms in a source have review flags → source-level atomization review.
- More than 5% of atoms have scholarly_function: "unclassified" → source-level atomization review with prompt improvement task.

**What prevents errors from propagating into the library (Criterion #21):** The offset integrity invariant ensures atoms accurately represent source text. The two-tier type system ensures both structural and semantic information is captured. The confidence scores on scholarly function prevent low-confidence classifications from being silently treated as established fact (D-033, confidence laundering prevention). The review flags on ambiguous layer attributions prevent misattribution from entering the library undetected. The exhaustive coverage check ensures no text is silently dropped.

---

## 6. Consensus Integration

The atomization engine does NOT use multi-model consensus for standard atomization. This is a conscious design decision.

**Rationale:** Atom boundaries and type classifications are judgments that benefit from a single consistent perspective rather than from averaging multiple perspectives. Multi-model consensus is designed for decisions where agreement increases confidence (e.g., "is this excerpt correctly placed?"). Atom boundary placement is more analogous to annotation: different annotators may place valid boundaries in different positions, and averaging them produces worse results than letting one skilled annotator work consistently.

**Exception: escalation consensus.** When a passage fails self-validation twice and the engine escalates to a stronger model, the escalation uses a different model (e.g., if the primary model is Claude Sonnet, escalation uses Claude Opus). If both models fail, the passage is flagged for human review. This is not consensus in the multi-model agreement sense — it is escalation with a different model as a fallback strategy.

**Where consensus IS valuable for atomization content:** The excerpting engine may use consensus when deciding how to group atoms — that is a higher-stakes decision where multi-model agreement adds value. The atomization engine's job is to produce the raw typed atoms; the higher-level grouping and placement decisions are where consensus operates.

---

## 7. Error Handling

Every error the atomization engine can produce, with its code, severity, and recovery action.

| Error Code | Severity | Trigger | Recovery |
|-----------|----------|---------|----------|
| ATOM_INVALID_INPUT | Warning | Passage fails input validation (§2) | Skip passage, log reason, add source-level review flag. Processing continues with remaining passages. |
| ATOM_LLM_FAILURE | Warning | LLM call fails (timeout, API error, rate limit) | Retry with exponential backoff (up to 3 retries). If all retries fail, skip passage with ATOM_LLM_FAILURE logged. |
| ATOM_SCHEMA_VIOLATION | Warning | LLM output does not conform to expected schema | Retry with Instructor's automatic schema error feedback (up to 2 retries). If retries exhausted, attempt to salvage parseable atoms and flag remainder. |
| ATOM_OFFSET_UNRESOLVABLE | Warning | Character offset correction algorithm cannot find match within ±50 chars | Include atom with LLM's reported offsets and text. Set review flag. Offset integrity check (V-2) will catch this. |
| ATOM_COVERAGE_VIOLATION | Fatal (per-passage) | Exhaustive coverage check fails after auto-repair | Re-atomize passage from scratch (up to 2 full retries). If still failing, produce best available result with coverage gaps logged. The source is flagged for human review. |
| ATOM_OFFSET_INTEGRITY_FAILURE | Fatal (per-passage) | atom_text != passage_text[start:end] after correction | Same as ATOM_COVERAGE_VIOLATION. This is the most critical invariant. |
| ATOM_LAYER_DISTRIBUTION_SUSPICIOUS | Info | All atoms in a multi-layer passage have the same layer | Log and flag source for review. Does not block processing. |
| ATOM_HIGH_UNCLASSIFIED_RATE | Warning | >5% of source atoms have scholarly_function: "unclassified" | Flag source for human review. Suggests prompt needs improvement for this source's content type. |
| ATOM_QURAN_REF_UNRESOLVED | Info | Quran fragment detected by pattern but could not match to specific ayah | Set unresolved_quran_ref review flag on the atom. Does not block processing. |
| ATOM_ATTRIBUTION_PARSE_FAILURE | Warning | The LLM returned an attribution entry that does not conform to the ScholarlyAttribution schema (§4.B.4) | Drop the malformed attribution entry. Log the raw LLM output for debugging. Set review_flags: ["low_attribution_confidence"] on the atom. |
| ATOM_ATTRIBUTION_LOW_CONFIDENCE | Info | An attribution entry has confidence below attribution_confidence_threshold (§4.B.4) | Set review_flags: ["low_attribution_confidence"] on the atom. Does not block processing. |
| ATOM_FINGERPRINT_HASH_FAILURE | Warning | Text normalization for fingerprint hashing failed (e.g., CAMeL Tools error on malformed Unicode) (§4.B.5) | Set fingerprint_text_hash to null for this atom. Log the error. Does not block processing. |
| ATOM_FINGERPRINT_EMBEDDING_FAILURE | Warning | Embedding model call failed for Tier 3 fingerprinting (§4.B.5) | Set fingerprint_embedding to null for this atom. Log the error. Does not block processing — Tier 1 and Tier 2 fingerprints remain available. |
| ATOM_FINGERPRINT_KEY_TERMS_EMPTY | Info | The LLM returned zero key terms for an atom during Tier 2 fingerprinting (§4.B.5) | Set fingerprint_key_terms to empty array. Log a warning. Does not block processing. |
| ATOM_UNKNOWN_LAYER_TYPE | Warning | A text_layer segment has a layer_type value not in the mapping (§4.A.6) | Default to source_layer "matn". Set review_flags: ["ambiguous_layer"]. Log the unrecognized value. |

**Logging.** Every error and warning is logged to library/sources/{source_id}/atoms/atomization_log.jsonl with: timestamp, error code, passage_id, atom_id (if applicable), error details, and recovery action taken. Fatal errors additionally trigger an entry in the source's processing status.

**Principle: never lose data silently (D-033).** If the engine cannot atomize a passage correctly, it produces the best approximation it can with review flags, rather than silently dropping the passage. An imperfect atomization with visible flags is better than a missing passage with no explanation.

---

## 8. Configuration

Parameters controlling engine behavior, with defaults and valid ranges.

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| primary_llm_model | anthropic/claude-sonnet-4-5-20250929 | Any LLM via OpenRouter or direct API | Model for standard atomization |
| escalation_llm_model | anthropic/claude-opus-4-5-20250929 | Any LLM | Model for escalation retries and low-fidelity sources |
| max_retries_per_passage | 2 | 0–5 | Maximum LLM retries on validation failure |
| function_confidence_threshold | 0.6 | 0.0–1.0 | Below this threshold, low_function_confidence review flag is set |
| quran_match_confidence_threshold | 0.85 | 0.5–1.0 | Minimum confidence for canonical Quran text matching |
| quran_hard_constraint_threshold | 0.95 | 0.8–1.0 | Above this, Quran detection overrides LLM classification |
| offset_correction_window | 50 | 10–200 | Characters to search when correcting LLM offsets |
| offset_correction_max_distance | 3 | 0–10 | Maximum Levenshtein distance for offset fuzzy matching |
| unclassified_rate_warning_threshold | 0.05 | 0.01–0.20 | Fraction of unclassified atoms that triggers source-level review |
| review_flag_rate_warning_threshold | 0.20 | 0.05–0.50 | Fraction of flagged atoms that triggers source-level review |
| fidelity_escalation_threshold | 0.5 | 0.0–1.0 | text_fidelity.min_score below which the escalation model is used |
| gold_baseline_path | engines/atomization/gold/ | Any path | Directory containing gold baseline files for few-shot examples |
| enable_attribution_detection | true | true/false | Whether to run §4.B.4 scholarly attribution chain detection during LLM atomization |
| attribution_confidence_threshold | 0.5 | 0.0–1.0 | Below this threshold, low_attribution_confidence review flag is set |
| enable_text_fingerprinting | true | true/false | Whether to compute Tier 1 (text hash) and Tier 2 (key terms) fingerprints |
| enable_semantic_fingerprinting | false | true/false | Whether to compute Tier 3 (embedding) fingerprints. Requires GPU-resident embedding model. |
| fingerprint_embedding_model | Omartificial/Arabic-STS-Matryoshka | Any sentence-transformers model | Embedding model for Tier 3 fingerprinting |
| fingerprint_embedding_dimensions | 256 | 64–1024 | Matryoshka truncation dimension for Tier 3 |
| fingerprint_key_terms_count | 5 | 2–10 | Maximum number of key terms extracted per atom for Tier 2 |

**Per-science configuration hooks (Level 3 / SCIENCE.md):** Each science may define:
- Additional scholarly function types specific to that science (extending the base enum)
- Science-specific pattern detection rules (e.g., fiqh-specific isnad chain patterns vs. hadith-specific ones)
- Science-specific few-shot examples for the LLM prompt

**What is configurable vs. hardcoded:**
- Configurable: LLM models, confidence thresholds, retry counts, offset correction parameters. These are operational tuning knobs.
- Hardcoded: The atom boundary rules (§4.A.2), the two-tier type system (§4.A.3), the offset integrity invariant, the self-validation checks. These are architectural constraints that define what an atom IS. Changing them changes the engine's behavior specification, which requires a SPEC revision.

---

## 9. Current Implementation State

**Existing files:**
- engines/atomization/CLAUDE.md — 67 lines. Engine orientation document. Must be updated to match this SPEC.
- engines/atomization/SPEC.md — this document.
- engines/atomization/reference/ABD_ATOMIZATION_SPEC.md — 200 lines. ABD-era spec describing manual atomization workflow, superseded by automated tool. Useful as reference for atom boundary rules and bonded cluster triggers. Zero design authority (D-019).
- engines/atomization/reference/ABD_ZOOM_BRIEF.md — 128 lines. ABD-era zoom-in brief. Zero design authority.
- engines/atomization/src/ — empty directory.
- engines/atomization/tests/ — empty directory.

**No dedicated atomization code exists.** ABD embedded atomization logic inside engines/excerpting/src/extract_passages.py, which combines atomization + excerpting + taxonomy placement in one LLM pass. This combined approach must be decomposed: atomization is a separate engine with separate input/output contracts. The ABD code is useful as reference for understanding what Arabic scholarly text patterns look like in practice, but its architecture (single-pass combined processing) is not adopted by KR.

**Known gaps between current code and this SPEC:**
- [NOT YET IMPLEMENTED] The entire atomization engine. No code exists.
- [NOT YET IMPLEMENTED] The Quran canonical text database for rule-based detection.
- [NOT YET IMPLEMENTED] The hadith/evidence marker lexicon for rule-based detection.
- [NOT YET IMPLEMENTED] The gold baseline set for few-shot examples.
- [NOT YET IMPLEMENTED] The atom schema (schemas/atoms.json) must be rewritten to match §3 of this SPEC. The current ABD-era schema uses book_id, has only 6 structural types, and lacks the scholarly function tier entirely.
- [NOT YET IMPLEMENTED] Rhetorical structure analysis (§4.B.1).
- [NOT YET IMPLEMENTED] Implicit layer transition detection (§4.B.2).
- [NOT YET IMPLEMENTED] Atom type distribution analytics (§4.B.3).
- [NOT YET IMPLEMENTED] Scholarly attribution chain resolution (§4.B.4).
- [NOT YET IMPLEMENTED] Atom-level semantic fingerprinting (§4.B.5) — Tier 1 (text hash) and Tier 2 (key terms) can be implemented immediately; Tier 3 (embeddings) requires embedding model infrastructure.

**External tools and libraries this engine depends on:**
- **Instructor** (Python, MIT license): Structured LLM output with Pydantic schema enforcement and automatic retries. Primary tool for LLM interaction. Handles the "LLM returns valid JSON conforming to the atom schema" requirement.
- **Quran_Detector** (GitHub: SElBeltagy/Quran_Detector, Python): Identifies Quranic verse fragments (≥3 words) in text with surah/ayah identification. Used for rule-based Quran detection (§4.A.4). Custom KR wrapper needed to integrate with the atom pipeline.
- **Quranic Arabic Corpus** (corpus.quran.com): Complete morphological and syntactic annotation of all Quran text. Source for the canonical Quran text database used by the Quran detector.
- **CAMeL Tools** (NYU Abu Dhabi, MIT license): Arabic text processing utilities. Used for: Arabic sentence boundary detection as a pre-processing hint (not authoritative — LLM makes final decisions), Arabic text normalization for fuzzy matching in offset correction.
- **OpenRouter / Anthropic API / OpenAI API**: LLM providers. Atomization uses the configured primary model (via OpenRouter for flexibility, or direct Anthropic API for Claude).
- **DSPy** (Stanford, MIT license): Alternative to Instructor for structured LLM output. May be used for prompt optimization against gold baselines — DSPy's MIPROv2 optimizer can automatically tune atomization prompts to maximize classification accuracy against gold data.
- **Swan-Large or Arabic-STS-Matryoshka** (Arabic embedding models): Used by §4.B.5 Tier 3 semantic fingerprinting. Swan-Large (NYUAD) is SOTA on ArabicMTEB; Arabic-STS-Matryoshka supports efficient Matryoshka dimensionality reduction. Only required when `enable_semantic_fingerprinting` is true.
- **CAMeL Tools text normalization** (NYU Abu Dhabi, MIT license): Used by §4.B.5 Tier 1 for Arabic orthographic normalization (alef/hamza/taa marbuta normalization, diacritics stripping) before hashing. Already a project dependency.

**What each external tool handles vs. custom code:**
- Instructor/DSPy: LLM call orchestration, schema enforcement, retries.
- Quran_Detector: Quran fragment identification.
- CAMeL Tools: Arabic text processing utilities.
- Custom code: Atom boundary rule enforcement, pre-detection pattern matching (hadith markers, evidence markers), post-processing (offset correction, coverage enforcement, layer attribution), self-validation, format-specific strategies, rhetorical pattern matching, distribution analytics.

---

## 10. Test Requirements

**Gold baselines required (minimum set before production use):**
1. **Prose format, single-layer, nahw text** (e.g., from شرح ابن عقيل): 5 passages with hand-annotated atom boundaries, structural types, scholarly functions.
2. **Prose format, single-layer, fiqh text** (e.g., from المغني): 5 passages with hand-annotated atoms, including isnad chains and evidence citations.
3. **Commentary format, multi-layer** (e.g., sharh passage with matn quotation): 3 passages with hand-annotated atoms and correct layer attribution.
4. **Verse format** (e.g., from ألفية ابن مالك): 3 passages with correct verse line boundaries.
5. **Q&A format**: 2 passages with bonded question-answer pairs.
6. **Mixed evidence passage**: 2 passages containing Quran citation, hadith citation, and rational argument in the same passage.

Total: minimum 20 gold passages. Each gold passage specifies: input (passage record), expected output (atom records with all fields), and the specific boundary and classification decisions with explanations.

**Unit test requirements (what MUST be tested):**

1. **Offset integrity invariant.** For every main text atom in every gold passage, verify atom_text == passage_text[start:end]. For every footnote atom, verify atom_text == footnote_text[start:end] using the footnote identified by footnote_source_index. This is the most critical test. 20 test cases (all gold passages), plus 4 test cases specifically targeting footnote atoms.
2. **Exhaustive coverage.** For every gold passage, verify that main text atom spans (source_layer != "footnote") partition the full passage_text without gaps or overlaps. 20 test cases.
3. **Structural type accuracy.** Compare engine output structural types against gold types. Target: ≥95% exact match. 20 test cases.
4. **Scholarly function accuracy.** Compare engine output scholarly functions against gold functions. Target: ≥85% exact match (scholarly function is harder than structural type). 20 test cases.
5. **Layer attribution accuracy.** For multi-layer gold passages, verify correct source_layer assignment. Target: ≥90% exact match. 6 test cases (3 commentary passages + 3 single-layer control passages).
6. **Quran detection precision.** Verify that rule-based Quran detection produces no false positives and ≥90% recall against gold Quran citations. 6 test cases (mixed evidence passages).
7. **Bonded cluster correctness.** Verify that bonded clusters in gold passages are correctly identified and carry correct bonded_reason. Target: ≥90% precision and recall. 5 test cases.
8. **Format-specific strategy selection.** Verify that the correct format-specific rules are applied for each structural_format value. 6 test cases (one per format).
9. **Input validation.** Verify that malformed passage records (empty text, missing fields, invalid format) produce the correct error code and do not crash the engine. 5 test cases.
10. **Offset correction algorithm.** Verify that the correction algorithm finds the right match within the search window for common drift patterns (off by 1–3 characters, diacritical differences). 10 test cases.
11. **Attribution detection accuracy (§4.B.4).** For gold passages containing scholarly attributions, verify: (a) direct attributions ("قال الشافعي") are detected with correct attributed_to and attribution_type, (b) isnad chains are correctly segmented into ordered transmitter names, (c) school-level attributions ("مذهب الحنفية") produce school_collective type with correct school_scope, (d) self-attributions ("والراجح عندي") produce self type, (e) anonymous attributions ("قيل") produce anonymous type. Target: ≥85% precision and ≥80% recall for direct attributions; ≥70% precision and recall for anonymous/implicit. 8 test cases (from gold passages 2, 3, 5, 6 plus 4 additional attribution-focused test passages).
12. **Fingerprint text hash determinism (§4.B.5 Tier 1).** Verify that the same atom text always produces the same fingerprint_text_hash regardless of diacritical variation. Test with: identical text, text differing only in tashkil, text differing in alef/hamza forms, text differing in taa marbuta. 8 test cases.
13. **Fingerprint key terms relevance (§4.B.5 Tier 2).** Verify that key terms extracted for definition atoms include the defined term. Verify that key terms for evidence_quran atoms include a reference to the Quranic concept. Qualitative check — not pass/fail but logged for prompt tuning. 5 test cases.
14. **Footnote atom integrity.** Verify that footnote atoms have source_layer "footnote", non-null footnote_source_index, and that the offset invariant holds against the footnote text (not passage_text). Verify footnote_for relation links to the correct main text atom. 4 test cases.
15. **Heading atom offset integrity.** Verify that heading atoms (from heading_text field) have anchor_span relative to heading_text, not passage_text. Verify atom_text == heading_text[start:end]. Verify heading atoms are excluded from V-1 exhaustive coverage check. Verify sequence_in_passage is 0 for heading atom and main text atoms start at 1. Test with: passage with heading_text + content, passage with heading_text only (passage_text has content but heading is separate), passage with null heading_text. 3 test cases.
16. **Word boundary integrity (V-8).** Verify that no atom boundary falls mid-word. Test with: correctly segmented prose, LLM output with a mid-word split (verify review flag is set), atoms at list/table delimiters (verify exception applies). 4 test cases.
17. **Bonded cluster spanning layer boundary.** Verify that a bonded cluster whose text spans a layer transition (e.g., matn quotation bonded with sharh explanation) is attributed to the first layer segment, carries both "ambiguous_layer" and "possible_misattribution" review flags, and has classification_notes explaining the overlap. 2 test cases.
18. **Unicode NFC normalization safety net.** Verify that passage_text not in NFC form is detected and normalized before processing. Test with: NFD Arabic text with combining diacritics (verify normalization occurs and offsets are recomputed), NFC text (verify no change). 2 test cases.
19. **Passage excluded on persistent V-2 failure.** Verify that when offset integrity fails after all retries, the passage produces zero atoms (not corrupt atoms), the error is logged with ATOM_OFFSET_INTEGRITY_FAILURE, and the source is flagged for human review. 2 test cases.
20. **Coverage gap produces synthetic marker atoms.** Verify that when V-1 coverage fails after retries, the gap is filled with a synthetic whitespace_separator atom carrying "coverage_gap_unresolved" review flag. Verify the synthetic atom's offsets cover the gap precisely. 2 test cases.
21. **Passage with ONLY heading (no main content).** Verify that a passage where passage_text contains only whitespace but heading_text is non-null produces exactly one heading atom and no coverage violation. 1 test case.
22. **All atoms classified as unclassified.** Verify that when the LLM returns unclassified for every atom in a passage, ATOM_HIGH_UNCLASSIFIED_RATE is triggered at source level, and all atoms carry low_function_confidence review flags. 1 test case.
23. **Verse_info disagrees with LLM.** Verify that when verse_info.verse_lines count differs from LLM-detected verse count, the engine trusts verse_info per §4.A.7. 2 test cases.
24. **Commentary passage where ALL text is matn quotation.** Verify that V-6 flags ATOM_LAYER_DISTRIBUTION_SUSPICIOUS when a commentary_unit passage produces only matn-layer atoms with no sharh atoms. 1 test case.
25. **Passage with 100+ footnotes (scale test).** Verify that footnote atomization handles large footnote counts without atom_id gaps, and that sequence_in_passage remains contiguous across all atoms. 1 test case.

**Regression testing strategy:** Gold baselines are never modified after initial creation (they are immutable ground truth). Any change to the atomization engine's code, prompts, or configuration triggers a full regression run against all gold baselines. If any gold baseline regresses (accuracy drops), the change is rejected until the regression is resolved.

**Integration test requirements:**
- **Upstream (passaging → atomization):** Read actual passage streams produced by the passaging engine and verify that the atomization engine can process them without input validation errors. Test with at least 3 real sources.
- **Downstream (atomization → excerpting):** Verify that the atom stream produced by the atomization engine conforms to the schema expected by the excerpting engine's input contract. This requires the excerpting engine SPEC to be written first; until then, verify against the atom schema.
