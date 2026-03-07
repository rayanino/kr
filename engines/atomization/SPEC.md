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
5. passage_text is in Unicode NFC form. The normalization engine guarantees NFC output; this check is a safety net. If the text is not NFC, the engine normalizes it to NFC and recomputes text_layers offsets accordingly before proceeding. This ensures character offset counting is deterministic — combining character sequences in NFD form would create offset discrepancies between the LLM's view of the text and the engine's offset computation. NFC normalization is applied to the engine's in-memory copy of passage_text only — the passage file on disk is never modified. If NFC normalization changes the text, the source is flagged with review_flags: ["nfc_normalization_applied"] to alert operators that atom_text and on-disk passage_text may differ in Unicode normalization form. The offset integrity invariant (V-2) is verified against the NFC-normalized in-memory text, not the on-disk text.

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
- bonded_reason: string or null. Required non-null when structural_type is bonded_cluster. Explains why two or more sentences were merged into a single atom (e.g., "condition_with_result", "isnad_chain_with_matn", "verse_with_inline_sharh").
- review_flags: array of strings. Machine-generated flags for human review. Possible values: low_function_confidence (scholarly function confidence < 0.6), ambiguous_layer (atom spans a text_layer boundary with < 0.7 confidence), possible_misattribution (text appears to be quotation but no explicit attribution marker detected, or bonded cluster spans layer boundary), offset_drift_corrected (character offset was adjusted during validation), unresolved_quran_ref (Quran fragment detected but could not be matched to a specific ayah), low_attribution_confidence (an attribution entry has confidence < attribution_confidence_threshold), mid_word_boundary (atom boundary falls within an Arabic word — V-8 violation), coverage_gap_unresolved (synthetic atom inserted to fill a coverage gap that could not be resolved after retries), incomplete_argument (passage's rhetorical pattern is missing required components per §4.B.6 — set on all atoms in the passage when completeness_ratio < 1.0), evidence_type_conflict (rule-based pre-detection and LLM disagree on evidence type — ADV-5), orphaned_footnote_marker (footnote marker ⌜N⌝ references nonexistent footnote — ADV-8), atom_reordering_applied (atoms were reordered during V-4 correction — ADV-10), over_segmented (passage produced anomalously high atom density — ADV-12), single_layer_in_commentary (commentary_unit passage produced 100% single-layer atoms — ADV-2), nfc_normalization_applied (passage_text required NFC normalization before processing — §2 step 5).

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

**Terminological concordance fields (§4.B.7):**
- concordance_entry: object or null. Present only on atoms with scholarly_function: definition when `enable_concordance_extraction` is true. Null on non-definition atoms and when feature is disabled. Contains: defined_term (string, the Arabic term being defined), definition_genus (string or null, the broader category), definition_differentia (array of strings, distinguishing features), alternate_terms (array of strings, synonyms mentioned in the text), science_scope (string, the science this term belongs to, derived from source metadata).

**Evidence quality signal fields (§4.B.8):**
- evidence_quality_signals: array of objects or null. Present only on evidence atoms (scholarly_function in {evidence_quran, evidence_hadith, evidence_ijma, evidence_qiyas, evidence_rational}) when `enable_evidence_quality_detection` is true. Null on non-evidence atoms and when feature is disabled. Empty array when enabled but no quality signals detected. Each object: signal_type (string, one of: hadith_strong_collection, hadith_weakness_flag, hadith_chain_quality, evidence_explicit_strength, evidence_explicit_weakness, consensus_qualifier, author_tarjih_marker), signal_text (string, the Arabic text that triggered detection), quality_direction (string, one of: positive, negative, neutral), span_start (integer, start offset within atom_text), span_end (integer, end offset within atom_text), confidence (float, [0.0, 1.0]).

**Guarantees about the atom stream:**

- **Source-agnostic.** The atom schema is identical regardless of source type.
- **Exhaustive coverage.** Every character in passage_text is covered by exactly one main text atom's anchor_span (excluding heading atoms and footnote atoms). No gaps. No overlaps. Heading atoms cover heading_text. Footnote atoms cover their respective footnote texts, not passage_text. This is verified by self-validation.
- **Ordering.** Atoms are ordered by reading order within each passage, and passages are ordered by document order. atom_id sequence numbers are globally monotonic within a source.
- **Offset integrity.** For every main text atom, atom_text == passage_text[anchor_span.start : anchor_span.end]. For every heading atom, atom_text == heading_text[anchor_span.start : anchor_span.end]. For every footnote atom, atom_text == passage.footnotes[footnote_source_index].text[anchor_span.start : anchor_span.end]. These invariants are verified deterministically during self-validation.
- **Layer attribution completeness.** Every atom has a source_layer value. For multi-layer passages, attribution is determined by matching the atom's character range against the passage's text_layers.
- **Type completeness.** Every atom has a structural_type. Every atom except headings and whitespace separators has a scholarly_function. Every scholarly_function has a function_confidence.
- **Metadata pass-through (D-023).** Every atom carries source_id for upstream metadata access and passage_id for passage-level context. The atom type itself is NEW metadata originated by this engine. The layer attribution is carried through from normalization. embedded_refs and atom_relations are new metadata that flows to the excerpting engine and ultimately to the synthesizer.
- **Confidence integrity (D-033).** Downstream consumers of the atom stream MUST respect function_confidence: atoms with function_confidence below the consuming engine's confidence threshold should be treated as unclassified for that consumer's purposes. Treating low-confidence classifications as authoritative is confidence laundering (D-033) and risks propagating uncertain classifications into the permanent library record.

**Metadata pass-through summary (D-023).** The atomization engine preserves upstream metadata by reference (source_id, passage_id) and adds:
- Atom boundaries and sequence ordering
- Two-tier type classification (structural + scholarly function)
- Layer attribution per atom
- Embedded content references (Quran, hadith, poetry, scholarly quotes)
- Intra-passage atom relationships
- Scholarly attribution chains per atom (§4.B.4) — who is being quoted, through what chain
- Semantic fingerprints per atom (§4.B.5) — text hash, key terms, optional embedding
- Argument completeness scores per passage (§4.B.6) — structural gap detection in the distribution report
- Terminological concordance entries per definition atom (§4.B.7) — term, genus, differentia, alternates
- Evidence quality signals per evidence atom (§4.B.8) — author's own evaluation of cited evidence strength
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

**Example:** (§4.A.1) Input passage (prose format, single-layer nahw text from شرح ابن عقيل):

> passage_text: "المبتدأ هو الاسم المرفوع العاري عن العوامل اللفظية. نحو: زيدٌ قائمٌ."
> structural_format: "prose", content_flags: {has_verse: false, has_quran_citation: false, has_hadith_citation: false}

Phase 1 (pre-screen): structural_format is "prose" → select prose atomization strategy. text_fidelity.min_score = 0.9 (above threshold) → use primary model. No review_flags from passaging.

Phase 2 (rule-based pre-detection): No Quran markers, no hadith markers, no isnad patterns, no poetry markers detected. No pre-detection hints produced.

Phase 3 (LLM atomization): LLM receives the passage text with prose strategy instructions and two gold prose examples. LLM returns two atoms: [0, 54) "المبتدأ هو الاسم المرفوع العاري عن العوامل اللفظية." classified as prose_sentence / definition; [55, 71) "نحو: زيدٌ قائمٌ." classified as prose_sentence / example.

Phase 4 (post-processing): Verify offsets — passage_text[0:54] matches the first atom's text, passage_text[55:71] matches the second. Gap at offset 54 (space character) → absorbed into first atom, extending its end to 55. Assign atom_ids: atm_nahw_ibnaqil_alfiyyah_a3f2_00001, atm_nahw_ibnaqil_alfiyyah_a3f2_00002. Derive source_layer: "matn" for both (single-layer passage). Add atom_relation: atom 2 `illustrates` atom 1 (the example illustrates the definition).

Phase 5 (self-validation): V-1 coverage: [0,55) ∪ [55,71) = [0,71) = [0, len(passage_text)) ✓. V-2 offset integrity: both atoms pass ✓. V-3 no empty atoms ✓. V-4 ordering: start offsets monotonically increasing ✓. V-5 type completeness: both have structural_type and scholarly_function ✓. V-6 layer attribution: single-layer, N/A ✓. V-7 bonded clusters: none present ✓. V-8 word boundaries: atom 1 ends after "." (punctuation), atom 2 starts at "ن" (start of word) ✓. All checks pass — atoms written to stream.

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

**Example:** (§4.A.2) Input passage_text (fiqh text with mixed assertions):

> "يجب الوضوء لكل صلاة مكتوبة. إذا نوى المتوضئ رفع الحدث واستباحة الصلاة أجزأه ذلك. لقوله تعالى: ﴿يَا أَيُّهَا الَّذِينَ آمَنُوا إِذَا قُمْتُمْ إِلَى الصَّلَاةِ فَاغْسِلُوا وُجُوهَكُمْ﴾."

Boundary analysis applying the rules:
- Atom 1: "يجب الوضوء لكل صلاة مكتوبة." → One scholarly assertion (a rule about wudu obligation). structural_type: prose_sentence, scholarly_function: rule_statement. (AB-1)
- Atom 2: "إذا نوى المتوضئ رفع الحدث واستباحة الصلاة أجزأه ذلك." → Condition + result bonded cluster. The condition (إذا نوى) and its ruling (أجزأه) are inseparable. structural_type: bonded_cluster, scholarly_function: rule_statement, bonded_reason: "condition_with_result". (AB-2)
- Atom 3: "لقوله تعالى: ﴿يَا أَيُّهَا الَّذِينَ آمَنُوا إِذَا قُمْتُمْ إِلَى الصَّلَاةِ فَاغْسِلُوا وُجُوهَكُمْ﴾." → Quran evidence citation. The evidence marker "لقوله تعالى" + the quotation form one atom. structural_type: prose_sentence, scholarly_function: evidence_quran. (AB-1)

Three atoms, not one (even though the original is three consecutive sentences on the same topic). Each contains exactly one scholarly assertion.

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
| whitespace_separator | Non-content separator absorbed into the stream for coverage completeness. No scholarly_function. Typically 0–3 per passage. | "***" section divider |

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
- When a single atom could carry two or more scholarly functions (e.g., a sentence that both states a rule and gives an example), the PRIMARY function is assigned and the secondary function is noted in classification_notes.

**Example:** (§4.A.3) Classifying a verse line from ألفية ابن مالك used in a شرح ابن عقيل commentary passage:

> atom_text: "كلامُنا لفظٌ مفيدٌ كاستقِمْ *** واسمٌ وفعلٌ ثمّ حرفٌ الكَلِمْ"

Classification: structural_type: verse_line (it is a بيت with صدر and عجز). scholarly_function: definition (the verse defines "الكلام" and enumerates the three categories of "الكَلِم"). function_confidence: 0.95. classification_notes: "Versified definition of الكلام — also contains an example (كاستقِمْ) as secondary function."

The two tiers are independent: the structural shape is verse_line; the scholarly role is definition. A different بيت in the same poem — "بِالجَرِّ وَالتَّنوينِ وَالنِّدا وَأَلْ *** وَمُسنَدًا لِلاسمِ تَمييزٌ حَصَلْ" — would be structural_type: verse_line, scholarly_function: rule_statement (it states the signs that distinguish nouns).

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

**Example:** (§4.A.4) Input passage_text from a fiqh text:

> "والدليل على وجوب الوضوء قوله تعالى: ﴿يَا أَيُّهَا الَّذِينَ آمَنُوا إِذَا قُمْتُمْ إِلَى الصَّلَاةِ فَاغْسِلُوا وُجُوهَكُمْ﴾⌜1⌝ ولقول النبي ﷺ: لا يقبل الله صلاة أحدكم إذا أحدث حتى يتوضأ."

Pre-detection results:
1. Quran detection: The fragment "يَا أَيُّهَا الَّذِينَ آمَنُوا إِذَا قُمْتُمْ إِلَى الصَّلَاةِ فَاغْسِلُوا وُجُوهَكُمْ" matches canonical Quran text at surah 5 (المائدة), ayah 6, confidence 0.97. Marked as embedded_ref: {ref_type: quran_ayah, ref_detail: {surah: 5, ayah: 6, match_confidence: 0.97}, detection_method: canonical_lookup}. The introduction phrase "قوله تعالى" confirms this as a Quran evidence citation → soft default scholarly_function: evidence_quran.
2. Evidence marker detection: "والدليل على" detected at passage start → hint that this passage opens with an evidence argument. "ولقول النبي ﷺ" detected → hint that subsequent text is evidence_hadith.
3. Hadith marker detection: "لقول النبي ﷺ" followed by reported speech pattern → provisional hadith text span marked.
4. Footnote marker detection: ⌜1⌝ detected at character offset 118 → recorded for footnote linking in post-processing.

These hints are passed to the LLM as constraints (Quran at confidence ≥ 0.95 → hard constraint on the embedded_ref) and advisory hints (evidence markers → suggested scholarly functions).

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

**Example:** (§4.A.5) The LLM receives a passage from المغني لابن قدامة (fiqh, prose format) with one pre-detection hint (Quran fragment at positions 85–142):

> passage_text: "وذهب أبو حنيفة إلى أن مس المرأة لا ينقض الوضوء مطلقاً. واحتج بأنه ﷺ قبّل بعض نسائه ثم صلى ولم يتوضأ. ولقوله تعالى: ﴿أَوْ لَامَسْتُمُ النِّسَاءَ﴾ والمراد به الجماع."

LLM output (simplified):
```
[
  {start: 0, end: 58, structural_type: "prose_sentence", scholarly_function: "opinion_statement", function_confidence: 0.92, classification_notes: "Hanafi position on touching a woman and wudu"},
  {start: 59, end: 113, structural_type: "prose_sentence", scholarly_function: "evidence_hadith", function_confidence: 0.88},
  {start: 114, end: 159, structural_type: "prose_sentence", scholarly_function: "evidence_quran", function_confidence: 0.95, embedded_refs: [{ref_type: "quran_ayah", span_start: 19, span_end: 39, ref_detail: {surah: 4, ayah: 43}, detection_method: "canonical_lookup"}]},
  {start: 160, end: 183, structural_type: "prose_sentence", scholarly_function: "definition", function_confidence: 0.80, classification_notes: "Author's tafsir of the verse — defines المراد بـ'اللمس'"}
]
```

Post-processing reconciles the LLM's Quran embedded_ref with the pre-detection result (both agree: surah 4, ayah 43, confirming An-Nisa). Atom_relations added: atom 2 `evidences` atom 1, atom 3 `evidences` atom 1, atom 4 `continues` atom 3.

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

**Example:** (§4.A.6) Input passage from شرح ابن عقيل على ألفية ابن مالك (commentary_unit format):

> passage_text: "قال المصنف: المبتدأ هو الاسم المرفوع العاري عن العوامل اللفظية. أقول: أراد بالعوامل اللفظية ما عدا الابتداء فإن الابتداء عامل معنوي."
> text_layers: [{layer_type: "sharh", author_canonical_id: "ibn_aqil", start: 0, end: 130}]

The normalization engine classified the entire passage as sharh (Layer 2). But the LLM detects "قال المصنف:" as an explicit layer transition marker.

Attribution result:
- Atom 1: "قال المصنف:" → structural_type: structural_transition, source_layer: "sharh" (Ibn Aqil introduces the quotation), layer_author_id: "ibn_aqil".
- Atom 2: "المبتدأ هو الاسم المرفوع العاري عن العوامل اللفظية." → structural_type: prose_sentence, scholarly_function: definition. LLM override: source_layer changed from "sharh" to "matn", layer_author_id changed to "ibn_malik". review_flags: ["possible_misattribution"]. classification_notes: "LLM override: text after 'قال المصنف' is a direct matn quotation from ألفية ابن مالك."
- Atom 3: "أقول: أراد بالعوامل اللفظية ما عدا الابتداء فإن الابتداء عامل معنوي." → structural_type: prose_sentence, scholarly_function: definition. source_layer: "sharh" (Ibn Aqil resumes commentary with "أقول"), layer_author_id: "ibn_aqil".

#### §4.A.7 — Format-Specific Atomization

The passage's structural_format determines which format-specific rules supplement the universal boundary rules (§4.A.2).

**Prose format** (structural_format: "prose"). Default behavior. The LLM identifies sentence boundaries and scholarly function transitions. The primary challenge is determining where one scholarly assertion ends and another begins in flowing Arabic prose, which often uses long coordinated sentences. The LLM is instructed to split at the scholarly function level, not at the Arabic sentence level: a single Arabic sentence containing a definition, an example, and a rule becomes three atoms.

**Verse format** (structural_format: "verse"). Each بيت is one atom (Rule AB-7). The verse_info field provides verse line data that the engine uses to verify the LLM's verse boundary detection. If verse_info.verse_lines and the LLM's verse detection disagree on the number of verse lines, the engine trusts verse_info (it comes from the normalization engine's structure discovery, which has higher accuracy for verse boundaries). Commentary text interspersed between verse lines in verse-format passages is atomized as separate prose atoms attributed to the commentary author.

**Q&A format** (structural_format: "qa_pair"). Question-answer pairs are bonded clusters (Rule AB-2). The question is always a prose_sentence or bonded_cluster with scholarly function varying by context. The answer is the primary scholarly content. If a Q&A passage contains two or more sequential Q&A pairs, each pair is one atom.

**Tabular format** (structural_format: "tabular_masala"). Each table row or distinct scholarly position within the tabular structure is atomized separately. If the table has a header row, it becomes a heading atom. Individual cells within a row may become separate atoms if they contain independent scholarly assertions (e.g., in a khilaf table: each school's position is a separate opinion_statement atom).

**Dictionary format** (structural_format: "dictionary_entry"). The lemma/entry word is a heading atom. The definition body is atomized by scholarly function just like prose. Sense numbers create list_item structural types.

**Commentary format** (structural_format: "commentary_unit"). This is the most complex format because it contains interleaved text from different authors. The key rule: the matn quotation at the start of the passage is one atom with source_layer: "matn" and layer_author_id pointing to the matn author. The commentary that follows is atomized as separate atoms with source_layer: "sharh". Layer transitions marked by phrases like "قال المصنف" or "قوله" (his words) trigger layer attribution changes on subsequent atoms until the commentary resumes.

**Example:** (§4.A.7) Verse-format passage from ألفية ابن مالك with commentary (structural_format: "verse"):

> passage_text: "كلامُنا لفظٌ مفيدٌ كاستقِمْ *** واسمٌ وفعلٌ ثمّ حرفٌ الكَلِمْ\nواحِدُهُ كَلِمَةٌ والقَوْلُ عَمّ *** وكَلِمَةٌ بها كلامٌ قد يُؤَمّ"
> verse_info: {verse_lines: [{line_number: 1, sadr: "كلامُنا لفظٌ مفيدٌ كاستقِمْ", ajuz: "واسمٌ وفعلٌ ثمّ حرفٌ الكَلِمْ"}, {line_number: 2, sadr: "واحِدُهُ كَلِمَةٌ والقَوْلُ عَمّ", ajuz: "وكَلِمَةٌ بها كلامٌ قد يُؤَمّ"}]}

Atomization result: Two atoms (one per بيت, per Rule AB-7):
- Atom 1: "كلامُنا لفظٌ مفيدٌ كاستقِمْ *** واسمٌ وفعلٌ ثمّ حرفٌ الكَلِمْ" → structural_type: verse_line, scholarly_function: definition (defines الكلام). The verse_info confirms 2 verse lines; the LLM also identifies 2 → agreement, no conflict.
- Atom 2: "واحِدُهُ كَلِمَةٌ والقَوْلُ عَمّ *** وكَلِمَةٌ بها كلامٌ قد يُؤَمّ" → structural_type: verse_line, scholarly_function: definition (defines الكلمة and distinguishes it from الكلام and القول).

The hemistichs within each بيت are NOT split — the بيت is the atomic unit.

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

**Evidence type conflict reconciliation (ADV-5 defense).** After LLM classification, for each atom: if rule-based pre-detection (§4.A.4) identified a hadith marker, Quran marker, or other evidence type marker with confidence ≥ 0.90 targeting this atom's span, and the LLM assigned a scholarly_function that conflicts with the pre-detection (e.g., pre-detection says hadith evidence, LLM says evidence_rational), the engine sets review_flags: ["evidence_type_conflict"] on the atom and logs ATOM_EVIDENCE_TYPE_CONFLICT at info severity. The LLM's classification is preserved (it may have legitimate reasons for the override), but the conflict is made visible for human review.

**Example:** (§4.A.8) passage_text: "المبتدأُ هو الاسمُ المرفوعُ. نحو: زيدٌ قائمٌ." (length: 44 characters)

LLM returns two atoms:
- Atom 1: {start: 0, end: 30, atom_text: "المبتدأُ هو الاسمُ المرفوعُ."} → passage_text[0:30] = "المبتدأُ هو الاسمُ المرفوعُ." ✓ exact match.
- Atom 2: {start: 32, end: 44, atom_text: "نحو: زيدٌ قائمٌ."} → passage_text[32:44] = "نحو: زيدٌ قائمٌ." ✓ exact match.

Coverage check: atom 1 covers [0,30), atom 2 covers [32,44). Gap at [30,32) — these are " " (space + newline). Gap repair: extend atom 1's end from 30 → 32, update atom 1's atom_text to passage_text[0:32] = "المبتدأُ هو الاسمُ المرفوعُ. " (includes trailing whitespace). Log ATOM_COVERAGE_GAP_REPAIRED, set review_flag "offset_drift_corrected". Final coverage: [0,32) ∪ [32,44) = [0,44) ✓ exhaustive.

#### §4.A.9 — Footnote Atomization

Each footnote in the passage's footnotes array is processed as a separate atom or set of atoms appended after the main text atoms.

**Processing rules:**
1. Each footnote's text field is treated as an independent mini-passage. If a footnote's text is empty or whitespace-only, no atom is produced for it — the footnote_for relation on the referencing main text atom has linked_footnote_atom_id set to null.
2. If the footnote text contains a single assertion, it becomes one atom with source_layer: "footnote" and scholarly_function determined by its content (editorial_note for tahqiq footnotes; evidence_*, cross_reference, or the LLM-determined function for substantive footnotes).
3. If the footnote text contains two or more assertions, it is split into that many footnote atoms following the standard boundary rules.
4. Footnote atoms' anchor_span values are relative to the footnote's own text, NOT to passage_text. The footnote_source_index field (integer) records which footnote in the passage's footnotes array this atom references (zero-based index). The offset integrity invariant for footnote atoms is: atom_text == passage.footnotes[footnote_source_index].text[anchor_span.start : anchor_span.end]. This is a variant of the main text invariant, using the footnote text as the reference instead of passage_text.
5. Each footnote atom is linked to the main text atom that contains the ⌜N⌝ marker via an atom_relations entry with relation_type: "footnote_for".
6. If a footnote marker ⌜N⌝ in passage_text references an index N-1 beyond the footnotes array length (N > len(footnotes)), the marker remains within the containing atom's text (per AB-4). The footnote_refs entry for this marker records linked_footnote_atom_id: null and the atom receives review_flags: ["orphaned_footnote_marker"]. Log ATOM_FOOTNOTE_INDEX_OUT_OF_RANGE at warning severity with the passage_id, marker value, and footnotes array length.

**Footnote type classification.** The footnote_type from the passage's footnotes array guides classification:
- editor_footnote → default scholarly function editorial_note
- source_footnote → scholarly function determined by content (usually cross_reference or evidence_*)
- unknown → LLM determines scholarly function

**Example:** (§4.A.9) Input passage with one footnote:

> passage_text: "المبتدأ هو الاسم المرفوع العاري عن العوامل اللفظية⌜1⌝."
> footnotes: [{index: 0, text: "في نسخة: المجرد من العوامل اللفظية. والمعنى واحد.", footnote_type: "editor_footnote"}]

Main text atom: "المبتدأ هو الاسم المرفوع العاري عن العوامل اللفظية⌜1⌝." → structural_type: prose_sentence, scholarly_function: definition, source_layer: "matn". footnote_refs: [{ref_marker: "1", linked_footnote_atom_id: "atm_...00002"}]. The ⌜1⌝ marker stays within the main text atom (Rule AB-4).

Footnote atom: "في نسخة: المجرد من العوامل اللفظية. والمعنى واحد." → structural_type: prose_sentence, scholarly_function: editorial_note (because footnote_type is editor_footnote). source_layer: "footnote". footnote_source_index: 0. anchor_span: {start: 0, end: 50} (relative to the footnote's own text, NOT passage_text). atom_relations: [{relation_type: "footnote_for", target_atom_id: "atm_...00001"}]. Offset invariant: atom_text == footnotes[0].text[0:50] ✓.

#### §4.A.10 — Self-Validation

After atomization of each passage, the engine runs seven automated checks. Each check either passes, triggers auto-repair, or flags for human review.

**Check V-1: Exhaustive coverage.** Verify that the union of all main text atom (source_layer != "footnote" AND structural_type != "heading") [start, end) ranges equals [0, len(passage_text)). Heading atoms are excluded because their offsets reference heading_text, not passage_text. Footnote atoms are excluded because they cover their respective footnote texts, not passage_text. If a gap or overlap is found in main text atom coverage, apply the correction algorithm from §4.A.8. If correction fails, flag ATOM_COVERAGE_VIOLATION.

**Check V-2: Offset integrity.** Verify that for every main text atom (source_layer != "footnote", structural_type != "heading"), atom_text == passage_text[anchor_span.start : anchor_span.end]. For every heading atom (structural_type == "heading"), verify atom_text == heading_text[anchor_span.start : anchor_span.end]. For every footnote atom (source_layer == "footnote"), verify atom_text == passage.footnotes[footnote_source_index].text[anchor_span.start : anchor_span.end]. Any violation is a hard failure — see failure handling below.

**Check V-3: No empty atoms.** Verify that every atom has len(atom_text) > 0. Empty atoms are removed from the stream. This should not happen if coverage is exhaustive, but is checked independently.

**Check V-4: Ordering consistency.** Verify that main text atoms are ordered by anchor_span.start within each passage. Footnote atoms follow all main text atoms, ordered by footnote_source_index then by anchor_span.start within each footnote. Verify that sequence_in_passage values are zero-based and contiguous across all atoms (main text + footnotes). If ordering is violated, the engine sorts atoms by anchor_span.start (main text first, then footnotes by footnote_source_index), reassigns sequence_in_passage values, and sets review_flags: ["atom_reordering_applied"] on all affected atoms. After reordering, atom_relations entries are verified: any relation whose target_atom_id no longer corresponds to the expected target (checked via anchor_span) is flagged for review.

**Check V-5: Type completeness.** Verify that every atom has a structural_type. Verify that every atom except heading and whitespace_separator has a scholarly_function (which may be unclassified). Verify that every non-null scholarly_function has a function_confidence in [0.0, 1.0].

**Check V-6: Layer attribution.** For multi-layer passages, verify that every atom has a source_layer value and that the distribution of layers across atoms is plausible (e.g., a commentary passage should have both matn and sharh atoms; if all atoms are matn, flag ATOM_LAYER_DISTRIBUTION_SUSPICIOUS). Severity escalation: if the passage's structural_format is "commentary_unit" and 100% of atoms have the same source_layer, V-6 escalates from info to warning severity and sets review_flags: ["single_layer_in_commentary"] on all atoms in the passage. This catches the case where upstream text_layers is uniformly wrong for a passage that should contain multiple voices.

**Check V-7: Bonded cluster integrity.** Verify that every atom with structural_type: "bonded_cluster" has a non-null bonded_reason. Verify that no bonded cluster contains only a single sentence (it should be a prose_sentence instead).

**Check V-8: Word boundary integrity.** Verify that no main text atom's anchor_span.start or anchor_span.end falls in the middle of an Arabic word. Specifically: for each atom boundary offset (excluding offset 0 and offset len(passage_text)), the character immediately before the offset or immediately after the offset must be whitespace, punctuation, or a paragraph boundary. Exception: list_item and table_cell atoms may have boundaries adjacent to structural delimiters (e.g., "|" in tables) without whitespace. Violations are soft failures — set review_flags: ["mid_word_boundary"] and log a warning. This check catches LLM offset errors that split Arabic words, which would produce semantically corrupt atoms.

**Check V-9: Atom density.** Compute atoms_per_character = main_text_atom_count / len(passage_text). If atoms_per_character > 0.5 (more than one atom per 2 characters), flag the passage with ATOM_OVER_SEGMENTATION at warning severity and trigger re-atomization with an explicit instruction appended to the LLM prompt: "Previous attempt produced {count} atoms for {length} characters. A passage of this length typically produces 2-15 atoms. Revise segmentation to use one atom per scholarly assertion." If the retry also produces over-segmented output, write the atoms with review_flags: ["over_segmented"] on all atoms and flag the source for human review.

**On validation failure.** The engine distinguishes between hard failures and soft failures.

Hard failures (V-2: offset integrity): trigger re-atomization of the passage with the validation error included in the LLM prompt (up to 2 retries). If all retries fail, the passage is excluded from the atom stream — no atoms are written for this passage. The passage_id is recorded in the source's processing status with error ATOM_OFFSET_INTEGRITY_FAILURE, and the source is flagged for human review. An excluded passage is preferable to atoms with corrupt offsets, because corrupt offsets produce corrupt excerpts downstream (T-1 silent text corruption).

Hard failures (V-1: coverage): trigger re-atomization (up to 2 retries). If retries fail, the engine writes the atoms it has with a coverage gap marker. The gap regions are recorded as synthetic atoms with structural_type: "whitespace_separator", scholarly_function: null, and review_flags: ["coverage_gap_unresolved"]. This preserves what the LLM produced while making the gap visible. The source is flagged for human review.

Soft failures (V-3, V-5, V-6, V-7, V-8): produce review flags on the affected atoms but do not block the atom stream from being written.

Soft failures with auto-repair (V-4, V-9): V-4 ordering violations are auto-repaired by sorting and reassigning sequence numbers. V-9 over-segmentation triggers one retry with density feedback. Both produce review flags.

**Example:** (§4.A.10) Validation run on a 3-atom passage:

> Atom 1: anchor_span [0, 35), atom_text = "يجب الوضوء لكل صلاة مكتوبة." → passage_text[0:35] matches ✓ (V-2 pass). structural_type: prose_sentence, scholarly_function: rule_statement with confidence 0.91 ✓ (V-5 pass).
> Atom 2: anchor_span [35, 80), atom_text = "إذا نوى رفع الحدث واستباحة الصلاة أجزأه." → passage_text[35:80] matches ✓ (V-2 pass). structural_type: bonded_cluster, bonded_reason: "condition_with_result" ✓ (V-7 pass).
> Atom 3: anchor_span [82, 120), atom_text = "لقوله تعالى: إذا قمتم إلى الصلاة." → passage_text[82:120] = "لقوله تعالى: إذا قمتم إلى الصلاة." ✓ (V-2 pass).

V-1 coverage: [0,35) ∪ [35,80) ∪ [82,120). Gap at [80,82). Auto-repair: extend atom 2 end from 80 → 82, update atom_text to passage_text[35:82]. Log ATOM_COVERAGE_GAP_REPAIRED. Set review_flag "offset_drift_corrected" on atom 2. After repair: [0,35) ∪ [35,82) ∪ [82,120) = [0,120) = [0, len(passage_text)) ✓.
V-4 ordering: start offsets 0 < 35 < 82 ✓. sequence_in_passage: 0, 1, 2 ✓.
V-6 layer: single-layer passage, N/A ✓.
V-8 word boundaries: atom 1 ends at position 35 (after "."), atom 2 ends at position 82 (after whitespace), atom 3 ends at 120 (after ".") — all at word/punctuation boundaries ✓.
Result: all checks pass (one auto-repair applied). Atoms written to stream.

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

Explicit layer transitions are handled by §4.A.6 — phrases like "قال المصنف" make the layer change obvious. But scholarly texts frequently contain implicit transitions: the author shifts from their own commentary into paraphrasing the matn without any explicit marker. These implicit transitions are dangerous because they can cause misattribution: the matn author's position is credited to the commentator, or vice versa.

**Detection signals:** The LLM is trained to detect implicit layer transitions by watching for:
- **Register shifts:** Classical Arabic scholarly texts have distinctive register differences between matn (terse, definitional) and sharh (expansive, explanatory). A sudden shift from elaborate commentary to terse definitional language may indicate an unattributed matn quotation.
- **Terminological inconsistency:** If the matn author uses term A and the commentary author uses term B for the same concept, a switch from term B to term A mid-commentary may indicate an implicit quotation.
- **Pronoun shifts:** The commentator refers to the matn author in third person ("he said", "his position is"). A shift to first person ("I define X as") in the middle of third-person commentary may indicate an unattributed self-quotation.
- **Content that contradicts the commentary's stated position:** If the commentator has been arguing position X and suddenly text appears arguing position Y without an attribution marker, this may be an implicit quotation of the matn or of an opposing scholar.

**Output.** When the LLM detects a potential implicit layer transition, it marks the affected atom with review_flags: ["possible_misattribution"] and records the evidence in classification_notes (e.g., "Register shift from expansive sharh to terse definitional language; possible unattributed matn quotation"). The source_layer is set to the LLM's best guess, not to the passage-level default. The low-confidence flag ensures human review before the attribution enters the permanent record.

**Technical approach.** The LLM prompt for multi-layer passages includes specific instructions to watch for register shifts and terminological inconsistencies. This is LLM-native capability — the LLM's understanding of Arabic scholarly register is the detection mechanism. No specialized NLP model is needed; the general-purpose LLM with domain-specific prompting performs this detection as part of its atomization pass.

**Why this is transformative.** Implicit layer transitions are a major source of misattribution in Islamic scholarly tools. Existing tools either ignore layer structure entirely (treating everything as one author's words) or only handle explicit markers. Detecting implicit transitions prevents the most dangerous form of scholarly error: putting words in the wrong scholar's mouth. Even at moderate accuracy (60-70%), flagging potential misattributions for human review is vastly better than silent misattribution.

**Example:** (§4.B.2) Passage from شرح ابن عقيل (commentary_unit format, text_layers marks entire passage as sharh/ibn_aqil):

> passage_text: "وأما المفعول به فهو ما وقع عليه فعل الفاعل. والمفعول به منصوب أبداً. نحو: ضربتُ زيداً."

Analysis: The first sentence ("وأما المفعول به فهو ما وقع عليه فعل الفاعل") uses the terse definitional pattern "فهو ما" — a register hallmark of matn text, not sharh commentary. Ibn Aqil's typical register is expansive ("أقول: أراد بهذا أن..."). The second sentence ("والمفعول به منصوب أبداً") states a rule tersely. The third sentence ("نحو: ضربتُ زيداً") is a concise example. The entire sequence — terse definition, terse rule, minimal example — matches matn register, not sharh register.

LLM detection: The LLM detects a register shift (terse definitional language in a passage marked as sharh). It flags atoms 1 and 2 with review_flags: ["possible_misattribution"], sets source_layer to "matn" (best guess), and records in classification_notes: "Register shift: terse definitional pattern 'فهو ما' in passage marked as sharh. Possible unattributed matn quotation from ألفية ابن مالك's prose section or its related verse." The human gate reviews and confirms or corrects the attribution.

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

**Example:** (§4.B.3) Source: المقنع في فقه الإمام أحمد (compact fiqh manual), 50 passages atomized, 320 atoms total.

Per-source aggregate:
- structural_type distribution: prose_sentence 285 (89%), bonded_cluster 20 (6%), heading 10 (3%), list_item 5 (2%)
- scholarly_function distribution: rule_statement 140 (44%), condition_exception 55 (17%), definition 40 (12%), evidence_hadith 30 (9%), opinion_statement 20 (6%), example 15 (5%), evidence_quran 10 (3%), cross_reference 5 (2%), unclassified 5 (2%)
- evidence_density: 0.125 (40 evidence atoms / 320 total)
- illustration_density: 0.083 (15 examples / 180 definitions+rules)
- structural_profile: "primarily_rule_based" (rule_statement + condition_exception = 61% of scholarly functions)

Anomaly detection: Passage 37 has 8 evidence_hadith atoms in a 9-atom passage (evidence_density 0.89) vs. source mean evidence_density 0.125 — deviation > 2σ. This passage likely contains a concentrated hadith evidence discussion, possibly a chapter on the proofs for a major ruling. Flagged as an anomaly for the excerpting engine to consider as a natural excerpt boundary.

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

**Example:** (§4.B.4) Atom from المغني لابن قدامة (fiqh text, scholarly disagreement passage):

> atom_text: "قال الماوردي في الحاوي: وذهب أبو حنيفة إلى أن المضمضة والاستنشاق واجبتان في الغسل دون الوضوء."

LLM attribution extraction produces two entries:
1. attribution_type: "via_work", attributed_to: "الماوردي", work_reference: "الحاوي", marker_text: "قال الماوردي في الحاوي", confidence: 0.93. The text identifies al-Mawardi through his work al-Hawi.
2. attribution_type: "direct", attributed_to: "أبو حنيفة", marker_text: "ذهب أبو حنيفة إلى", confidence: 0.95. Abu Hanifa's position is being reported by al-Mawardi as transmitted by Ibn Qudamah.

The attribution chain has three scholarly layers: Ibn Qudamah (source author, writing in al-Mughni) reports al-Mawardi (intermediate transmitter, from al-Hawi) reporting Abu Hanifa's position (the original opinion holder). The synthesizer can trace: this Hanafi position reaches the library through two independent scholarly chains.

An atom may have zero attributions (e.g., a definition without attribution is the source author's own), one (the common case), or two or more (nested attribution: "قال الماوردي: قال الشافعي" produces two attribution entries, one for each layer).

**Attribution marker verification (ADV-3 defense).** During post-processing, for every attribution entry, the engine verifies that marker_text is non-empty and appears as a substring of atom_text. If marker_text is empty or does not appear in atom_text, the attribution entry is dropped, ATOM_ATTRIBUTION_MARKER_MISSING is logged at warning severity with the dropped attribution's details, and review_flags: ["low_attribution_confidence"] is set on the atom. This prevents LLM hallucination of attributions that have no textual basis. Exception: for attribution_type: "self" where the author's position is inferred from absence of explicit attribution (no "قال X" marker), marker_text may reference a general self-reference phrase ("والراجح عندي", "قلت") or the source_layer context rather than a specific substring. In this case, marker_text must still be non-empty but the substring check is relaxed: the engine verifies only that marker_text is non-empty.

**Interaction with text layers (§4.A.6).** In multi-layer texts, the attribution chain includes the layer structure. When a sharh author (Layer 2) quotes the matn author (Layer 1) using "قال المصنف," the atom's source_layer is set to "matn" AND an attribution entry records this as a Layer 2 → Layer 1 transition. When the sharh author then quotes a THIRD scholar within the commentary, that produces a separate attribution entry. The layer attribution and scholarly attribution are complementary, not redundant: layers tell you WHOSE TEXT this is physically; attributions tell you WHOSE POSITION is being described.

**Why this is transformative.** No existing Islamic studies tool structures the attribution within scholarly text. Current tools either ignore it entirely (treating all text as the source author's words) or capture it only at the book level (metadata says "the author is X"). KR's atom-level attribution enables the synthesizer to answer: "Show me all positions attributed to al-Shafi'i across the library" — gathering not just passages FROM al-Shafi'i's own books, but every time ANY author in the library QUOTES al-Shafi'i. This reconstructs a scholar's complete intellectual footprint across the entire corpus — including positions transmitted by later scholars that may not appear in the original works (because a large proportion of early works are lost, known only through quotation in later texts).

**Research validation.** IslamicLegalBench (2026) showed that even the best LLMs achieve only ~67% accuracy on Islamic legal reasoning tasks, with 21% hallucination. However, attribution detection is a much more constrained task than legal reasoning — it is pattern recognition over well-defined Arabic markers, not open-ended inference. The LLM is not being asked to evaluate the strength of a legal argument; it is being asked to detect "قال X" patterns and structure them. This is closer to NER (named entity recognition) than to legal reasoning, and LLMs perform significantly better on structured extraction tasks. Expected accuracy: 80-90% for direct attributions, 60-70% for anonymous/implicit attributions (the latter requiring human review flags).

[NOT YET IMPLEMENTED] — Full specification provided. Depends on: core atomization implementation (§4.A), and scholar authority model interface for downstream resolution of raw scholar names to canonical IDs (excerpting engine responsibility).

#### §4.B.5 — Atom-Level Semantic Fingerprinting

**Capability:** Generate a normalized canonical fingerprint for each content atom that enables downstream engines to detect when the same scholarly content (definition, rule, evidence citation) appears across different sources — even when the wording differs slightly.

The same definition of المبتدأ appears in dozens of grammar books across 14 centuries. Sometimes word-for-word identical (because later scholars quote earlier ones). Sometimes paraphrased. Sometimes compressed or expanded. When the excerpting engine produces excerpts from 20 sources that all define المبتدأ, the taxonomy engine places them all at the same leaf, and the synthesizer encounters 20 near-duplicate definitions. Without fingerprinting, the synthesizer must rely on its own LLM judgment to detect duplicates — error-prone and opaque. With fingerprints, the synthesizer can group semantically equivalent atoms BEFORE synthesis, producing cleaner entries.

**Fingerprint generation (three-tier):**

**Tier 1 — Normalized text hash (deterministic, fast).** The atom's text is normalized by: (a) stripping all diacritics (tashkil), (b) normalizing alef variants (أ/إ/آ → ا), taa marbuta (ة → ه for matching purposes only), and hamza forms, (c) removing common particles and connectives (و، ف، ثم، لكن) from the start, (d) sorting words by Unicode codepoint order (not Arabic alphabetical order — Unicode order is deterministic and locale-independent). The resulting normalized string is SHA-256 hashed. Exact textual duplicates (modulo diacritics and orthographic variants) produce identical hashes. This tier catches verbatim quotations across sources. Output: `fingerprint_text_hash` (string, 64 hex chars).

**Tier 2 — Key term extraction (LLM-assisted, medium cost).** During atomization, the LLM extracts 2-5 key Arabic terms from each atom — the conceptual core independent of phrasing. For a definition of المبتدأ, the key terms might be: [المبتدأ، اسم، مرفوع، عوامل، ابتداء]. These are stored as `fingerprint_key_terms` (array of strings, normalized). Two atoms sharing ≥70% of their key terms are candidate semantic duplicates even if their full text differs. This tier catches paraphrases and reformulations.

**Tier 3 — Semantic embedding (model-based, highest cost).** The atom text is embedded using an Arabic semantic model (Swan-Large or Arabic-STS-Matryoshka, per RESOURCES.md). The resulting vector (truncated to 256 dimensions via Matryoshka) is stored as `fingerprint_embedding` (array of floats). Cosine similarity ≥ 0.85 between embeddings indicates strong semantic overlap. This tier catches deep paraphrases where the same concept is expressed in completely different words. Embedding computation is deferred by default — Tier 3 runs only when `enable_semantic_fingerprinting` is true in configuration, because it requires a GPU-resident embedding model.

**Fingerprint is NOT identity.** Two atoms with matching fingerprints are CANDIDATES for deduplication — not confirmed duplicates. The synthesizer or excerpting engine makes the final deduplication decision because context matters: the same definition from a 2nd-century AH source and a 7th-century AH source may be textually identical but carry different scholarly weight. Fingerprints enable detection; downstream engines decide what to do with the detection.

**Storage and downstream consumption.** Fingerprint fields are part of the atom record (§3). They are metadata that flows forward (D-023). The excerpting engine uses them to detect when two or more atoms within an excerpt are redundant. The taxonomy engine uses them to pre-group atoms at a leaf before synthesis. The synthesizer uses them to present unique content once (citing the strongest source) rather than repeating near-identical definitions from 20 sources.

**Scalability consideration.** Tier 1 (text hash) is O(1) per atom — trivially fast. Tier 2 (key terms) is part of the existing LLM call — marginal cost. Tier 3 (embedding) adds one embedding model call per atom — significant at scale. For a 15-volume work producing ~50,000 atoms, Tier 3 adds ~50,000 embedding calls. At 1000 embeddings/second (batch processing with Swan-Large on a consumer GPU), this adds ~50 seconds. Acceptable.

**Why this is transformative.** No existing Islamic studies tool detects conceptual duplicates across sources at the sub-paragraph level. The KITAB project's text reuse detection operates at 300-word chunks — too coarse to detect that two books contain the same one-sentence definition. Islamic scholarly tradition is deeply intertextual: later scholars routinely reproduce earlier scholars' exact definitions, often without attribution. Atom-level fingerprinting reveals this intertextual web at the finest meaningful granularity. Over time, as the library grows, the fingerprint database becomes a map of how scholarly concepts are transmitted, transformed, and preserved across centuries — making visible the invisible "DNA" of the Islamic intellectual tradition.

**Cross-source fingerprint index.** After atomizing a source, the engine registers all fingerprints in a source-level fingerprint manifest (`library/sources/{source_id}/atoms/fingerprint_manifest.json`). When the library has two or more sources, a background process (or the taxonomy engine) can cross-reference fingerprints across sources to build a library-wide duplicate detection index. This index is a shared resource, not owned by the atomization engine — the atomization engine produces the fingerprints; consumption is downstream.

[NOT YET IMPLEMENTED] — Full specification provided. Depends on: Arabic text normalization utilities from CAMeL Tools (Tier 1), core LLM atomization producing key terms (Tier 2), Arabic embedding model deployment (Tier 3). Tier 1 and Tier 2 can be implemented immediately; Tier 3 requires embedding model infrastructure.

#### §4.B.6 — Argument Completeness Scoring

**Capability:** Detect structural gaps in scholarly argument patterns within a passage — positions stated without evidence, evidence presented without a clear claim, disagreements listed without tarjih (preference) — and score each passage's argumentative completeness.

Islamic scholarly texts follow conventionalized argument structures. In fiqh, the expected pattern for a khilaf (disagreement) discussion is: (1) state the masala (issue), (2) present position A, (3) present evidence for A, (4) present position B, (5) present evidence for B, (6) refute the weaker position or present counterarguments, (7) state the tarjih (preponderant opinion) with justification. In nahw, the pattern is: (1) define the concept, (2) state the rule, (3) give examples, (4) note exceptions, (5) cite authoritative position, (6) note disagreements if any. Passages that omit expected components are structurally incomplete — the omission may be intentional (the author assumes the reader knows the evidence) or may indicate that the source doesn't cover this aspect of the topic.

**Detection mechanism.** After §4.B.1 (rhetorical structure analysis) identifies the rhetorical pattern in a passage, the completeness scorer checks whether all expected components of that pattern are present. This is a post-processing step that runs AFTER atom type classification and rhetorical pattern matching.

**Expected components per pattern type:**

| Pattern | Required components | Optional components |
|---------|-------------------|---------------------|
| khilaf (disagreement) | ≥2 opinion_statement atoms, ≥1 evidence_* atom | refutation, tarjih (opinion_statement with self attribution + evidence) |
| single_ruling | 1 rule_statement atom, ≥1 evidence_* atom | example, condition_exception |
| definition_block | 1 definition atom | example, cross_reference |
| evidence_chain | ≥1 evidence_* atom, 1 opinion_statement or rule_statement atom (the claim being evidenced) | refutation of counter-evidence |

**Completeness score.** Each passage receives a completeness_score object:
- pattern_type: string or null. The detected rhetorical pattern (from §4.B.1). Null if no pattern detected.
- required_present: array of strings. Required components that ARE present.
- required_missing: array of strings. Required components that are ABSENT. Empty if complete.
- optional_present: array of strings. Optional components that are present.
- completeness_ratio: float, [0.0, 1.0]. |required_present| / |required_present ∪ required_missing|. 1.0 means all required components present.
- gap_description: string or null. Human-readable description of what's missing. Null if completeness_ratio is 1.0. Example: "Opinion of الحنفية stated without evidence; tarjih stated without justification."

**Output.** The completeness score is stored per passage in the distribution report (§4.B.3), NOT per atom. It is a passage-level analytical artifact. When completeness_ratio < 1.0, all atoms in the passage receive a review_flag: "incomplete_argument" (new flag value).

**Why this is transformative.** No existing tool tells a scholar "this source discusses topic X but only provides one side's evidence." The synthesizer uses completeness scores to produce entries like: "For the Hanafi position's evidence, see Source A (which provides it); Source B states the position but does not provide supporting evidence." This transforms a flat list of excerpts into a map of argumentative coverage — the scholar knows not just WHAT each source says, but HOW COMPLETELY it argues. Over the full library, completeness scores reveal which sources are best for which purposes: Source A is argumentatively thorough (high completeness), Source B is concise and assumes prior knowledge (low completeness but high authority).

**Dependency.** Requires §4.B.1 (rhetorical structure analysis) to identify the pattern type. If §4.B.1 is disabled or detects no pattern, completeness scoring is skipped for that passage (completeness_score is null).

**Example:** (§4.B.6) A khilaf passage about مسح الرأس في الوضوء containing 5 atoms:

> Atom 1: "ذهب الشافعي إلى أنه يكفي مسح بعض الرأس." → scholarly_function: opinion_statement (position A)
> Atom 2: "لقوله تعالى: ﴿وَامْسَحُوا بِرُءُوسِكُمْ﴾ والباء للتبعيض." → scholarly_function: evidence_quran (evidence for A)
> Atom 3: "وذهب أحمد إلى وجوب مسح الرأس كله." → scholarly_function: opinion_statement (position B)
> Atom 4: "لما رُوي أنه ﷺ مسح برأسه فأقبل بيديه وأدبر." → scholarly_function: evidence_hadith (evidence for B)
> Atom 5: "والراجح مذهب الإمام أحمد لصراحة الحديث." → scholarly_function: opinion_statement (tarjih)

§4.B.1 detects pattern: khilaf. Required components: ≥2 opinion_statement atoms (atoms 1, 3 ✓), ≥1 evidence_* atom (atoms 2, 4 ✓). Optional: refutation (absent), tarjih (atom 5, present ✓).

completeness_score: {pattern_type: "khilaf", required_present: ["opinion_A", "opinion_B", "evidence_A", "evidence_B"], required_missing: [], optional_present: ["tarjih"], completeness_ratio: 1.0, gap_description: null}. No "incomplete_argument" flag set — this passage is argumentatively complete.

Contrast: if atoms 2 and 4 were absent (opinions stated without evidence), completeness_ratio would be 0.5 (2 of 4 required components present), gap_description: "مذهب الشافعي stated without evidence; مذهب أحمد stated without evidence."

[NOT YET IMPLEMENTED] — Full specification provided. Depends on: §4.B.1 rhetorical pattern detection, atom scholarly function classification (§4.A).

#### §4.B.7 — Cross-Atom Terminological Concordance

**Capability:** Build a structured map of technical terms (mustalahaat) from definition atoms, identifying when different atoms define the same concept using different terminology, and producing a per-source terminological index that feeds downstream deduplication and cross-source linking.

Islamic sciences developed regionally distinct terminologies. Basran grammarians say المبتدأ; Kufan grammarians say المُسنَد إليه. Hanafi jurists say الفرض; Shafi'i jurists say الفرضية for the same concept. Early scholars use العلة (effective cause); later scholars use المناط (operative basis). Students moving between texts encounter the same concept under unfamiliar names — a major barrier to learning that existing tools do not address.

**Extraction mechanism.** During LLM atomization (§4.A.5), for every atom classified with scholarly_function: definition, the LLM extracts three additional fields:

- defined_term: string. The Arabic term being defined. Extracted from the definitional pattern (the term following "هو/هي", the subject of "يُعرَّف بأنه", or the heading term in a dictionary entry). Example: "المبتدأ".
- definition_genus: string or null. The broader category the term belongs to (the genus in the Aristotelian definition pattern). Extracted from the predicate of the definition. Example for "المبتدأ هو الاسم المرفوع": genus is "اسم" (noun). Null if the definition does not follow a genus-differentia pattern.
- definition_differentia: array of strings. The distinguishing features. Example: ["مرفوع", "مجرد من العوامل اللفظية"]. Empty array if extraction fails.

**Output per atom.** For definition atoms, a concordance_entry object is added to the atom record:
```
concordance_entry: {
  defined_term: "المبتدأ",
  definition_genus: "اسم",
  definition_differentia: ["مرفوع", "مجرد من العوامل اللفظية"],
  alternate_terms: ["المُسنَد إليه"],
  science_scope: "nahw"
}
```

The alternate_terms field is populated by the LLM when the definition text itself mentions synonyms (e.g., "المبتدأ، ويُسمى أيضاً المُسنَد إليه" — "the mubtada, also called al-musnad ilayh"). If the text does not mention alternates, alternate_terms is an empty array. Cross-source synonym detection (finding that Source A's المبتدأ and Source B's المُسنَد إليه refer to the same concept) is a DOWNSTREAM task for the taxonomy engine using fingerprint similarity (§4.B.5) + concordance genus overlap — the atomization engine produces the raw concordance data, not the cross-source links.

**Per-source terminological index.** After atomizing all passages for a source, the engine compiles a terminological index: `library/sources/{source_id}/atoms/term_index.json`. This is a JSON array of all concordance entries from definition atoms in the source, deduplicated by defined_term (if two passages define the same term, both entries are included with their atom_ids). The index includes the atom_id, passage_id, source_layer, and layer_author_id for each entry — so the downstream engines know who defined the term and in what context.

**Why this is transformative.** No Islamic studies tool provides a machine-readable terminological concordance extracted from the source texts themselves. Existing glossaries are manually compiled and incomplete. KR's concordance is AUTOMATICALLY generated from every definition atom in the library. As the library grows, it becomes the most comprehensive Arabic scholarly terminology map ever constructed — not by manual compilation, but by reading what scholars actually wrote. The synthesizer uses this to produce entries that explain: "This concept is called X by the Basran school and Y by the Kufan school" — cross-referencing terminology automatically rather than requiring the student to discover this through years of reading.

**Configuration.** `enable_concordance_extraction`: boolean, default true. When false, concordance_entry is null on all atoms and no term_index is produced.

**Example:** (§4.B.7) Definition atom from شرح ابن عقيل:

> atom_text: "المبتدأ هو الاسم المرفوع العاري عن العوامل اللفظية، ويُسمى أيضاً المُسنَد إليه."
> scholarly_function: definition

LLM extraction:
- defined_term: "المبتدأ" (the term preceding "هو" in the definitional pattern)
- definition_genus: "اسم" (the broader category — it IS a noun)
- definition_differentia: ["مرفوع", "عارٍ عن العوامل اللفظية"] (the distinguishing features)
- alternate_terms: ["المُسنَد إليه"] (extracted from "ويُسمى أيضاً")

Output concordance_entry:
```
{
  defined_term: "المبتدأ",
  definition_genus: "اسم",
  definition_differentia: ["مرفوع", "عارٍ عن العوامل اللفظية"],
  alternate_terms: ["المُسنَد إليه"],
  science_scope: "nahw"
}
```

If a later source (e.g., a Kufan grammar) defines "المُسنَد إليه" with genus "اسم" and similar differentia, the downstream taxonomy engine detects the overlap: same genus + overlapping differentia + one term appears in the other's alternate_terms → candidate cross-source synonym.

[NOT YET IMPLEMENTED] — Full specification provided. Depends on: core LLM atomization (§4.A.5) with concordance extraction in the prompt. No external dependencies beyond the LLM.

#### §4.B.8 — Evidence Quality Signal Detection

**Capability:** Detect and structure the author's own explicit evaluations of evidence strength within evidence atoms, surfacing how the source author assessed the reliability of the evidence they cited.

Arabic scholarly convention includes explicit quality markers embedded in or immediately adjacent to evidence citations. When a fiqh author writes "لقول النبي ﷺ — رواه البخاري ومسلم" (for the Prophet's saying — reported by al-Bukhari and Muslim), the authentication reference "رواه البخاري ومسلم" is the author's own quality signal: this hadith is in the two most trusted collections. When another author writes "رُوي أنه قال — وفي إسناده ضعف" (it is reported that he said — and in its chain is weakness), the phrase "وفي إسناده ضعف" is an explicit quality downgrade.

These signals are NOT the atomization engine's own evaluation of evidence quality — the engine has no competence to grade hadith authenticity or evaluate legal arguments. These are the SOURCE AUTHOR'S explicit textual markers that evaluate the evidence they cite. The engine extracts what the author said about evidence quality, not what the evidence quality actually is.

**Signal types detected:**

| Signal | Arabic markers | Quality direction |
|--------|---------------|-------------------|
| hadith_strong_collection | "رواه البخاري"، "في الصحيحين"، "رواه مسلم"، "أخرجه أحمد"، "في السنن" | positive |
| hadith_weakness_flag | "وفي إسناده ضعف"، "حديث ضعيف"، "لا يثبت"، "في إسناده فلان وهو ضعيف" | negative |
| hadith_chain_quality | "بإسناد صحيح"، "إسناده حسن"، "رجاله ثقات" | positive |
| evidence_explicit_strength | "وهو نص في الباب"، "دليل قاطع"، "لا معارض له" | positive |
| evidence_explicit_weakness | "وهذا الدليل لا يستقيم"، "وأُجيب عنه بأن"، "ولا حجة فيه" | negative |
| consensus_qualifier | "إجماع قطعي"، "إجماع سكوتي"، "لا نعلم فيه خلافاً" | varies (qat'i > sukuti > la na'lam) |
| author_tarjih_marker | "والراجح"، "والأظهر"، "والأصح"، "والمعتمد" | positive (author's preferred) |

**Detection approach.** Evidence quality signals are detected in two phases:

1. **Rule-based pre-detection (§4.A.4 extension).** The engine maintains a lexicon of quality signal phrases (the Arabic markers above). During pre-detection, when a quality signal phrase is found within or immediately after an evidence_* atom, the span is marked as a quality signal.

2. **LLM classification.** During atomization, the LLM confirms or rejects the pre-detected signals and may identify additional signals not in the lexicon (e.g., when the author uses an unusual phrasing to express evidence quality). The LLM also resolves ambiguous cases: "رواه أحمد" (reported by Ahmad) is a positive collection signal, but "رواه ابن أبي شيبة" may be positive or neutral depending on context.

**Output per evidence atom.** Evidence atoms (scholarly_function in {evidence_quran, evidence_hadith, evidence_ijma, evidence_qiyas, evidence_rational}) receive an evidence_quality_signals field:

```
evidence_quality_signals: [
  {
    signal_type: "hadith_strong_collection",
    signal_text: "رواه البخاري ومسلم",
    quality_direction: "positive",
    span_start: 45,
    span_end: 62,
    confidence: 0.95
  }
]
```

An evidence atom may have zero signals (no explicit quality evaluation by the author), one (the common case), or two or more (e.g., "رواه البخاري — وقال الترمذي: حسن صحيح" has two positive signals). Non-evidence atoms always have evidence_quality_signals as null (feature not applicable).

**Interaction with attribution (§4.B.4).** When an evidence atom has both an attribution chain (who transmitted this evidence) and quality signals (how the author evaluates this evidence), the synthesizer receives both perspectives. Example: the attribution chain says this hadith comes through a particular transmitter chain; the quality signal says the author considers the chain sound. This is richer than either alone.

**Why this is transformative.** No existing tool extracts the author's own evidence evaluations at the sub-paragraph level. Current Islamic studies tools present evidence citations without the author's quality assessment. But in scholarly practice, the author's assessment of their own evidence is crucial metadata: a scholar who KNOWS their evidence is weak but presents it anyway (with the weakness noted) is making a different scholarly move than one who presents evidence without qualification. The synthesizer uses these signals to produce entries that explain: "Source A considers this hadith strong (citing al-Bukhari); Source B considers the same hadith's chain questionable (noting weakness in one transmitter)." This reveals when scholars DISAGREE about evidence quality — a critical dimension of scholarly debate invisible in flat text presentation.

**Configuration.** `enable_evidence_quality_detection`: boolean, default true. When false, evidence_quality_signals is null on all atoms. `evidence_quality_lexicon_path`: string, default `engines/atomization/lexicons/evidence_quality.json`. Path to the quality signal phrase lexicon.

**Example:** (§4.B.8) Evidence atom from a fiqh text:

> atom_text: "لقول النبي ﷺ: لا ضرر ولا ضرار — رواه أحمد وابن ماجه بإسناد صحيح، وقال بعضهم: في إسناده عبد الرحمن بن أبي بكر وهو ضعيف."
> scholarly_function: evidence_hadith

Phase 1 (rule-based pre-detection): Lexicon matches "رواه أحمد وابن ماجه" → hadith_strong_collection candidate. "بإسناد صحيح" → hadith_chain_quality candidate. "وهو ضعيف" → hadith_weakness_flag candidate.

Phase 2 (LLM confirmation): LLM confirms all three signals and resolves context: the first two signals are the author's own positive assessment; the third signal is the author quoting a dissenting opinion about the chain.

Output evidence_quality_signals:
```
[
  {signal_type: "hadith_strong_collection", signal_text: "رواه أحمد وابن ماجه", quality_direction: "positive", span_start: 42, span_end: 60, confidence: 0.93},
  {signal_type: "hadith_chain_quality", signal_text: "بإسناد صحيح", quality_direction: "positive", span_start: 61, span_end: 72, confidence: 0.95},
  {signal_type: "hadith_weakness_flag", signal_text: "وهو ضعيف", quality_direction: "negative", span_start: 112, span_end: 121, confidence: 0.88}
]
```

Three signals on one atom: the author presents BOTH a positive authentication (Ahmad and Ibn Majah, with a sound chain) AND a dissenting weakness claim. The synthesizer surfaces this tension: "The author cites this hadith as evidence with positive authentication, but notes a dissenting view questioning one transmitter."

[NOT YET IMPLEMENTED] — Full specification provided. Depends on: core atomization (§4.A), quality signal lexicon file, LLM prompt integration.

---

## 5. Validation and Quality

The atomization engine's validation architecture has three layers, following the quality framework established in VISION.md §8.

**Layer 1: Self-validation (§4.A.10).** Automated checks run on every passage immediately after atomization. Seven checks covering offset integrity, coverage, typing, ordering, layer attribution, and bonded cluster integrity. This layer catches mechanical errors: wrong offsets, missing types, schema violations. Self-validation is mandatory and blocking — the atom stream is not written to disk until all hard checks pass.

**Layer 2: Cross-passage consistency checks.** After all passages for a source are atomized, the engine runs cross-passage validation:
- **Monotonic atom_id:** Verify that atom_id sequence numbers are globally monotonic across all passages.
- **Source-level layer plausibility:** If the source metadata declares the source as multi-layer (commentary), verify that at least one passage produced atoms with source_layer values from two or more distinct layers. If all atoms are matn, either the source metadata is wrong or the layer detection failed.
- **Type distribution sanity:** Using the distribution report (§4.B.3), flag anomalies that suggest systematic classification errors (e.g., 100% of atoms classified as prose_sentence with no scholarly function variety suggests the LLM prompt was ineffective).

**Layer 3: Human gate integration.** The atomization engine does not have a dedicated human gate. Instead, human review is triggered by review flags on individual atoms. The excerpting engine's human gate reviews flagged atoms as part of excerpt review — atoms are intermediate artifacts whose classification decisions are most meaningful in the context of the excerpts they form. However, two conditions trigger source-level human review escalation:
- More than 20% of atoms in a source have review flags → source-level atomization review.
- More than 5% of atoms have scholarly_function: "unclassified" → source-level atomization review with prompt improvement task.

**What prevents errors from propagating into the library (Criterion #21):** The offset integrity invariant ensures atoms accurately represent source text. The two-tier type system ensures both structural and semantic information is captured. The confidence scores on scholarly function prevent low-confidence classifications from being silently treated as established fact (D-033, confidence laundering prevention). The review flags on ambiguous layer attributions prevent misattribution from entering the library undetected. The exhaustive coverage check ensures no text is silently dropped.

### §5.1 — Adversarial Scenarios

Each scenario describes an attack vector (what goes wrong), the engine's expected behavior, and the knowledge impact if the defense fails.

**ADV-1: LLM returns offset that splits a multi-byte Arabic character.**
Attack vector: The LLM reports an atom boundary at a byte offset that falls between the bytes of a multi-byte Unicode codepoint (e.g., offset lands between the two UTF-8 bytes of an Arabic letter with a combining diacritic in NFD form). Alternatively, the LLM reports an offset that bisects a grapheme cluster (e.g., between a base Arabic letter and its combining shadda).
Engine behavior: §2 step 5 normalizes passage_text to NFC before processing, which collapses combining character sequences into single codepoints. After NFC normalization, all offsets are in Unicode codepoints, not bytes. The V-2 offset integrity check operates on Python string slicing (codepoint-based), so a mid-codepoint offset is impossible after NFC normalization. If the passage somehow bypasses NFC normalization (a code bug), the V-2 check would produce a mismatch because passage_text[start:end] would return corrupt text that doesn't match atom_text, triggering ATOM_OFFSET_INTEGRITY_FAILURE and passage exclusion.
Knowledge impact if defense fails: Corrupted atom_text enters the atom stream. The excerpting engine builds an excerpt containing garbled Arabic text. The synthesizer produces an entry citing text that doesn't exist in the source. T-1 silent text corruption — the most severe threat.
Defense depth: NFC normalization (primary), V-2 offset integrity (secondary), passage exclusion on persistent failure (tertiary).

**ADV-2: LLM classifies all commentary text as matn in a multi-layer source.**
Attack vector: In a sharh text with explicit matn quotations, the LLM ignores layer transition markers ("قال المصنف") and assigns source_layer: "matn" to every atom, including the commentator's own words.
Engine behavior: V-6 (layer attribution) detects that a source declared as multi-layer (commentary_unit format) has produced atoms with only one layer type. V-6 flags ATOM_LAYER_DISTRIBUTION_SUSPICIOUS at info severity. However, V-6 is a soft check — it flags but does not block. The real defense is the layer attribution algorithm in §4.A.6, which matches atom character ranges against the passage's text_layers. If text_layers correctly mark the sharh portions, the algorithm assigns sharh regardless of what the LLM says. The LLM override mechanism (§4.A.6) only changes layers when the LLM provides explicit evidence of an implicit transition — it cannot silently flatten all layers to matn.
Knowledge impact if defense fails: All commentary is attributed to the matn author. Ibn Aqil's explanations are credited to Ibn Malik. T-2 attribution error — a scholar's entire intellectual contribution is misattributed.
Defense depth: text_layers from passaging engine (primary), V-6 distribution check (secondary), possible_misattribution review flags (tertiary). Gap identified: V-6 flags only at info severity and does not trigger re-atomization. If text_layers themselves are wrong (upstream passaging error), the atomization engine has no independent way to detect all-matn misattribution beyond V-6's statistical check. **Mitigation:** Upgrade V-6 to warning severity when a commentary_unit passage produces 100% single-layer atoms. Add this to §4.A.10.

**ADV-3: LLM fabricates scholarly attributions not present in the text.**
Attack vector: The LLM adds an attribution entry with attributed_to: "الشافعي" to an atom whose text never mentions al-Shafi'i. The LLM hallucinates based on the surrounding context or its training data.
Engine behavior: §4.B.4 records attributions with a marker_text field — the Arabic text that triggered the detection. Post-processing can verify that marker_text actually appears within the atom's text. If marker_text is empty or does not appear in atom_text, the attribution is suspect. However, the current SPEC does not mandate this verification. **Fix required:** Add a post-processing rule to §4.B.4: "For every attribution entry, verify that marker_text is non-empty and appears as a substring of atom_text. If marker_text does not appear in atom_text, drop the attribution entry, log ATOM_ATTRIBUTION_MARKER_MISSING, and set review_flags: ['low_attribution_confidence']." This closes the hallucination vector for direct attributions. Anonymous and implicit attributions (where marker_text may be a general phrase like "قيل") are harder to verify but carry lower confidence by default.
Knowledge impact if defense fails: The synthesizer aggregates all atoms attributed to al-Shafi'i and produces an entry claiming "al-Shafi'i held position X" when no source actually says this. T-5 synthesis hallucination seeded by T-2 attribution error.
Defense depth: marker_text verification (primary, after fix), confidence thresholds (secondary), human review on low-confidence attributions (tertiary).

**ADV-4: Quran detector false positive on non-Quran text that resembles Quranic phrasing.**
Attack vector: A scholarly text uses phrases that happen to match 3+ consecutive words of a Quranic verse but in a non-Quranic context. For example, the common Arabic phrase "يا أيها الذين آمنوا" appears in a scholar's own exhortation, not as a Quran quotation.
Engine behavior: The Quran detector (§4.A.4) matches the phrase and produces a candidate with confidence based on match length. For short matches (3-4 words), confidence is typically 0.85-0.90 — above the quran_match_confidence_threshold but below the hard constraint threshold of 0.95. This means the match is a soft hint to the LLM, not a hard constraint. The LLM may override the scholarly_function default (evidence_quran) if the context makes clear this is not a Quran citation. However, the embedded_ref (quran_ayah) is harder to override — it records the matched text regardless of scholarly function. If the match exceeds 0.95 confidence (which requires 5+ consecutive matching words), it becomes a hard constraint.
Knowledge impact if defense fails: An atom is tagged with an embedded_ref pointing to a Quran verse when the text is not actually citing the Quran. The synthesizer may cite this atom as "Quranic evidence" when it is not. T-6 metadata poisoning of the embedded_ref.
Defense depth: Confidence thresholds with two-level constraint system (primary), LLM contextual override for scholarly_function (secondary). **Gap identified:** The embedded_ref is preserved even when the LLM overrides the scholarly_function. This is by design (the text DOES match the Quran, even if it's not being used as evidence). But the ref_detail should include the match_confidence so downstream consumers can distinguish high-confidence citations from borderline matches. The current SPEC already includes match_confidence in ref_detail — no fix needed.

**ADV-5: LLM systematically confuses evidence_hadith with evidence_rational.**
Attack vector: The LLM classifies rational arguments ("لأنه يلزم منه كذا") as evidence_hadith, and hadith citations ("لقول النبي ﷺ") as evidence_rational. This systematic confusion corrupts the evidence type metadata across an entire source.
Engine behavior: Rule-based pre-detection (§4.A.4) provides anchoring hints that distinguish hadith markers from rational markers. The evidence marker lexicon contains explicit patterns for each evidence type. If the LLM ignores these hints, post-processing does not force compliance (hints are advisory). V-5 checks that every evidence atom has a scholarly_function but does not verify that the function is CORRECT — correctness is an LLM judgment, not a deterministic check. The distribution report (§4.B.3) would show an anomalous ratio (e.g., 0% hadith in a hadith-heavy source), which could flag the issue at the source level.
Knowledge impact if defense fails: The synthesizer's evidence analysis is corrupted — entries say "the rational argument for this position" when the actual evidence is a hadith. The scholar loses the ability to filter by evidence type. T-6 metadata poisoning.
Defense depth: Pre-detection hints (primary), distribution anomaly detection (secondary). **Gap identified:** No rule forces the LLM to respect pre-detection hints for evidence type. **Mitigation:** Add a post-processing reconciliation rule: "When rule-based pre-detection identifies a hadith marker (§4.A.4) with confidence ≥ 0.90 and the LLM classifies the containing atom with a non-hadith scholarly_function, set review_flags: ['evidence_type_conflict'] and log ATOM_EVIDENCE_TYPE_CONFLICT. The LLM's classification is preserved (it may have legitimate reasons to override), but the conflict is visible." Add this to §4.A.8 post-processing and §7 error table.

**ADV-6: Passage text arrives in NFD form with combining diacritics despite NFC guarantee.**
Attack vector: A bug in the normalization engine produces passage_text in NFD (decomposed) form. Arabic text in NFD has base letters and diacritics as separate codepoints. The LLM receives the text as-is and returns offsets based on the NFD codepoint count, but the engine's offset calculations assume NFC.
Engine behavior: §2 step 5 explicitly checks whether passage_text is in NFC form and normalizes to NFC when the check fails, recomputing text_layers offsets. This is the safety net for exactly this scenario. After NFC normalization, the text length in codepoints may be shorter (combining sequences collapse), so the LLM receives a different text than the original passage_text. The engine must use the NFC-normalized text for all subsequent processing. The normalized text and its recomputed offsets become the authoritative reference for V-2 checks.
Knowledge impact if defense fails: If §2 step 5 is bypassed or buggy, NFD offsets produce misaligned atom boundaries. V-2 catches the misalignment because passage_text[start:end] won't match atom_text. The passage is excluded after retries. The defense chain holds.
Defense depth: NFC safety net in §2 (primary), V-2 offset integrity (secondary), passage exclusion (tertiary). No gap.

**ADV-7: Bonded cluster spans three text layers (matn → sharh → hashiyah).**
Attack vector: A bonded cluster (e.g., an isnad chain that begins in the matn, continues through the commentator's insertion, and ends with a super-commentator's note) spans three layers. The §4.A.6 rule for bonded clusters says "assign the layer of the FIRST segment" — but three layers means the conservative assignment (first = matn) would misattribute the sharh and hashiyah portions.
Engine behavior: The bonded cluster rule assigns layer: "matn" (first segment), sets review_flags: ["ambiguous_layer", "possible_misattribution"], and records in classification_notes which portions belong to which layers. The human gate catches the three-way split. The atom's bonded_reason explains why the text cannot be split. This is the correct conservative behavior — a bonded cluster that spans three layers is inherently complex and MUST be reviewed by a human.
Knowledge impact if defense fails: If the human gate is bypassed or the reviewer misses it, the hashiyah author's words are attributed to the matn author. T-2 attribution error across three scholars.
Defense depth: Conservative first-layer assignment (primary), dual review flags (secondary), human gate (tertiary). **Observation:** Three-layer bonded clusters are extremely rare in Islamic scholarly texts (they require an isnad chain that physically spans three annotation layers). The defense is adequate for the frequency of this scenario.

**ADV-8: Footnote marker ⌜N⌝ in passage_text but footnotes array is empty or missing that index.**
Attack vector: The passaging engine produces a passage_text containing ⌜1⌝ but the footnotes array is either empty or has no entry at index 0. The atomization engine tries to link the footnote marker to a footnote atom that doesn't exist.
Engine behavior: §4.A.9 rule 1 states: "If a footnote's text is empty or whitespace-only, no atom is produced for it — the footnote_for relation on the referencing main text atom has linked_footnote_atom_id set to null." This handles empty footnotes. However, the SPEC does not address the case where the footnotes array has fewer entries than the highest ⌜N⌝ marker in the text (e.g., ⌜3⌝ in text but only 2 footnotes). **Fix required:** Add to §4.A.9: "If a footnote marker ⌜N⌝ references an index beyond the footnotes array length (N > len(footnotes)), the marker remains in the atom's text (per AB-4) but footnote_refs records the marker with linked_footnote_atom_id: null and a review flag: 'orphaned_footnote_marker'. Log ATOM_FOOTNOTE_INDEX_OUT_OF_RANGE at warning severity."

**ADV-9: Mass low-confidence — LLM assigns function_confidence 0.31 to every atom.**
Attack vector: A poorly calibrated LLM or a very unusual text type produces atoms where every scholarly function confidence is just above the unclassified threshold (0.3) but below the low_function_confidence threshold (0.6). Every atom gets a review flag. Source-level review is triggered (>20% flagged atoms). But the atoms are still written to the stream with these low-confidence classifications.
Engine behavior: This is a designed and correct outcome. The atoms ARE written with their low-confidence classifications because they represent the best available result. The review flags ensure human review occurs before the classifications enter the permanent record. The risk is not that low-confidence atoms enter the stream — the risk is that downstream engines treat them as high-confidence. The excerpting engine must check function_confidence before using scholarly_function for grouping decisions. §3 documents the confidence field, and §5 (Layer 2) documents the 20% threshold for source-level review.
Knowledge impact if defense fails: If a downstream engine ignores confidence scores (confidence laundering — D-033), low-confidence classifications become treated as fact. The synthesizer might state "this is a definition" when the engine had only 31% confidence.
Defense depth: Confidence scores on every atom (primary), review flags at <0.6 (secondary), source-level review at >20% flagged (tertiary). **Gap identified:** The SPEC does not explicitly state that downstream engines MUST consult function_confidence before relying on scholarly_function. This is a downstream contract issue, not an atomization engine gap — but the output contract (§3) should note it. **Fix:** Add a note to §3 Guarantees: "Downstream consumers of the atom stream MUST respect function_confidence: atoms with function_confidence below the consuming engine's confidence threshold should be treated as unclassified for that consumer's purposes. Treating low-confidence classifications as authoritative is confidence laundering (D-033)."

**ADV-10: LLM returns atoms covering passage_text but in reverse order.**
Attack vector: The LLM returns atoms with anchor_span values [80,120), [35,80), [0,35) — correct coverage but wrong order.
Engine behavior: V-4 (ordering consistency) verifies that main text atoms are ordered by anchor_span.start. Reverse order is detected immediately. However, V-4 is a soft check — the SPEC says it verifies but does not specify the consequence. **Fix required:** Add explicit consequence to V-4: "If ordering is violated, the engine sorts atoms by anchor_span.start, reassigns sequence_in_passage values, and sets review_flags: ['atom_reordering_applied'] on all affected atoms. The atom_relations (which reference atom_ids) are rechecked after reordering to ensure they still point to the correct targets." Add a new review flag value to the §3 enum: "atom_reordering_applied".

**ADV-11: Coverage gap repair absorbs semantically significant content into adjacent atom.**
Attack vector: The LLM produces atoms [0,40) and [50,100) with a gap at [40,50) containing "والدليل" (the evidence marker). The gap repair extends atom 1's end from 40 to 50, absorbing "والدليل" into a definition atom. Now the definition atom ends with "والدليل" — text that semantically belongs with the following evidence atom.
Engine behavior: The coverage gap repair (§4.A.8) extends the preceding atom's boundary and updates its atom_text. The repair is mechanical — it does not re-evaluate scholarly_function after the text changes. The absorbed text "والدليل" does not change atom 1's classification (it's still a definition), but the atom now contains text that introduces the next scholarly assertion. This is suboptimal but not a correctness error — the text is preserved, the coverage is exhaustive, and the review flag "offset_drift_corrected" marks the atom for review.
Knowledge impact if defense fails: Minor — the atom boundary is slightly wrong but no text is lost or corrupted. The excerpting engine may produce a slightly awkward excerpt boundary, but the scholarly content is intact.
Defense depth: Gap repair preserves text (primary), review flag marks the adjustment (secondary). **Observation:** This scenario is expected and acceptable. The alternative (rejecting the passage entirely) loses more information than the suboptimal boundary placement.

**ADV-12: LLM returns 500 atoms for a 3-sentence passage.**
Attack vector: The LLM over-segments, producing hundreds of single-character or single-word atoms for a short passage. Each "atom" is technically valid (non-overlapping, exhaustive coverage, valid types) but semantically meaningless.
Engine behavior: V-3 (no empty atoms) catches zero-length atoms but not single-character atoms. V-7 (bonded cluster integrity) is irrelevant here. V-8 (word boundary integrity) catches atoms that split mid-word but not single-word atoms. No existing validation check detects over-segmentation. **Fix required:** Add a new validation check V-9: "Atom density check. Compute atoms_per_character = atom_count / len(passage_text). If atoms_per_character > 0.5 (more than one atom per 2 characters), flag the passage with ATOM_OVER_SEGMENTATION at warning severity and trigger re-atomization with an explicit instruction in the LLM prompt: 'Previous attempt produced {count} atoms for {length} characters. A passage of this length typically produces 2-10 atoms. Revise segmentation to use one atom per scholarly assertion.'" Add ATOM_OVER_SEGMENTATION to §7 error table.

### §5.2 — Failure Cascade Analyses

**CASCADE-1: Offset integrity failure → corrupt excerpts → fabricated library entries.**

Initial failure: A single atom's anchor_span is wrong — start is 45 instead of 47 (off by 2, within the tolerance of many checks). The atom_text field was set by the LLM and looks correct, but it doesn't match passage_text[45:end] because offsets 45-46 are part of a different word. The V-2 check catches this: atom_text != passage_text[45:end].

If V-2 passes (code bug in the check): The atom's atom_text contains text the LLM fabricated or recalled from training data, not the actual passage text. The excerpting engine trusts atom_text as ground truth and includes it in an excerpt's primary_text. The synthesizer cites this excerpt in an entry. The entry contains Arabic text that doesn't exist in the source.

Downstream propagation:
1. **Excerpting engine:** Builds an excerpt containing the fabricated atom_text. The excerpt's primary_text is wrong. Since the excerpting engine doesn't re-verify atom offsets (it trusts the atomization engine's V-2 guarantee), the error propagates silently.
2. **Taxonomy engine:** Places the excerpt normally — content-level errors don't affect placement.
3. **Synthesizer:** Incorporates the excerpt into an entry. The entry cites "Source A, vol. 2, p. 45" for text that doesn't appear on that page.
4. **Knowledge impact:** Rayane cites a fabricated scholarly position. The error is invisible because the entry reads naturally. This is T-1 (silent text corruption) at its worst — an error that LOOKS correct.

Why V-2 must be a hard invariant: V-2 is the single point of defense between "LLM said the text is X" and "the text is actually X." If V-2 is disabled, weakened, or buggy, the entire downstream chain trusts fabricated text. There is no second check anywhere in the pipeline that re-verifies atom_text against passage_text. The immutable frozen source exists, but no engine below the normalization boundary accesses it directly.

Prevention: V-2 runs on every atom of every passage. It is a deterministic string comparison, not a statistical check. It cannot have false negatives if implemented correctly. The only risk is an implementation bug in V-2 itself. **Test requirement:** Test V-2 with: correct offsets (pass), off-by-1 offsets (fail), LLM-fabricated text (fail), empty atom_text (fail). These tests are the highest priority in the entire test suite.

**CASCADE-2: Layer misattribution → wrong author propagation → scholarly credibility damage.**

Initial failure: In a sharh text, the passaging engine's text_layers incorrectly marks a 200-character sharh segment as matn. The atomization engine's §4.A.6 algorithm faithfully assigns source_layer: "matn" and layer_author_id: "ibn_malik" to atoms that are actually ibn_aqil's commentary.

If the LLM does not detect the implicit layer error (§4.B.2): The atoms are written with wrong source_layer. No review flag is set because text_layers was internally consistent — it just happened to be wrong.

Downstream propagation:
1. **Excerpting engine:** Groups the misattributed atoms into an excerpt. The excerpt's author metadata says "Ibn Malik" when the words are Ibn Aqil's.
2. **Taxonomy engine:** Places the excerpt under the topic. The topic now has an excerpt attributed to Ibn Malik that contains Ibn Aqil's analysis.
3. **Synthesizer:** Produces an entry that says "Ibn Malik argued X" when X is actually Ibn Aqil's commentary on Ibn Malik's verse. This is especially dangerous because the synthesizer's narrative structure treats matn and sharh differently — matn positions are presented as authoritative source text, while sharh positions are presented as interpretive commentary.
4. **Knowledge impact:** Rayane believes Ibn Malik made an argument that he never made. If Rayane cites this in his own scholarly work, his citation is wrong. This damages his scholarly credibility — T-2 at its worst.

Why layer attribution must be verified at multiple levels: The passaging engine's text_layers is the primary source of layer information, but it can be wrong (especially for implicit layer transitions). The atomization engine's §4.B.2 (implicit layer detection) is the secondary defense, but it depends on LLM pattern recognition and has 60-70% expected accuracy. The human gate on "possible_misattribution" review flags is the tertiary defense, but it only fires when the LLM DETECTS a potential issue.

Gap in the defense chain: When the passaging engine's text_layers is wrong AND the LLM doesn't detect the error, no review flag is set. The error propagates silently. **Mitigation:** Add a cross-validation rule to §4.A.6: "For multi-layer passages, if all atoms are assigned the same source_layer (100% matn or 100% sharh), and the passage's structural_format is commentary_unit, set review_flags: ['single_layer_in_commentary'] on all atoms. This catches the case where text_layers is uniformly wrong." This is the same check as V-6 but applied at the passage level with an explicit review flag that triggers human review.

### §5.3 — Knowledge Integrity Invariant Verification

Each invariant from KNOWLEDGE_INTEGRITY.md is verified against this SPEC.

**Invariant 1: Frozen sources are immutable.**
SPEC compliance: The atomization engine never accesses frozen sources. It operates on passage_text from the passaging engine, which is already downstream of the frozen source. No mechanism in this SPEC reads, writes, or modifies frozen source files. ✓ No gap.

**Invariant 2: Primary text is never modified.**
SPEC compliance: atom_text is "copied exactly from passage_text[anchor_span.start : anchor_span.end]" (§3). The engine never rewrites, corrects, or normalizes atom_text beyond what the passage_text already contains. The NFC normalization in §2 step 5 applies to passage_text BEFORE atomization — the engine normalizes the input, not the output. After atomization, atom_text is extracted from the (possibly NFC-normalized) passage_text by exact slicing. ✓ Partially verified. **Concern:** §2 step 5 says "the engine normalizes [passage_text] to NFC and recomputes text_layers offsets." This modifies passage_text before processing. Is this a violation of "primary text is never modified"? No — passage_text is an in-memory working copy, not the passage record on disk. The normalization engine's output (the passage file on disk) is not modified. The atomization engine modifies its own in-memory copy for safe processing. The atom_text produced from the NFC-normalized text accurately represents the text as processed. However, there is a subtle issue: if passage_text on disk is in NFD and atom_text is extracted from NFC-normalized text, the atom_text may differ from the on-disk passage_text in its Unicode form. **Fix:** Add clarification to §2 step 5: "NFC normalization is applied to the engine's in-memory copy of passage_text. The passage file on disk is not modified. If NFC normalization changes the text, the source is flagged with review_flags: ['nfc_normalization_applied'] to alert operators that atom_text and on-disk passage_text may differ in Unicode normalization form. The offset integrity invariant (V-2) is verified against the NFC-normalized in-memory text, not the on-disk text."

**Invariant 3: Every claim is traceable.**
SPEC compliance: Every atom carries source_id and passage_id (§3), linking it to a specific source and passage. The anchor_span links the atom to exact character positions in the passage. The source_layer and layer_author_id identify whose words the atom contains. The attributions field (§4.B.4) identifies whose positions are being described. This provides full traceability from any downstream claim back to: source → passage → character range → layer → author. ✓ No gap.

**Invariant 4: Errors fail loudly.**
SPEC compliance: The SPEC defines 17 error codes in §7, each with severity and recovery action. V-2 offset failures are fatal (passage excluded). V-1 coverage failures trigger re-atomization. Low-confidence decisions produce review flags. No error code has "silently ignore" as its recovery action. The "never lose data silently" principle is stated explicitly in §7. ✓ No gap, contingent on the fixes from ADV scenarios being applied (ADV-8 footnote index, ADV-10 reordering, ADV-12 over-segmentation add new error codes).

**Invariant 5: Human gates are not optional.**
SPEC compliance: §5 Layer 3 describes two conditions that trigger source-level human review: >20% flagged atoms and >5% unclassified atoms. Individual atoms with review flags are reviewed through the excerpting engine's human gate. The SPEC does not describe any mechanism to bypass or auto-approve these gates. ✓ No gap.

**Invariant 6: Metadata flows forward, never backward-deleted.**
SPEC compliance: §3 lists the D-023 metadata pass-through explicitly. source_id and passage_id are preserved from upstream. The atomization engine adds new metadata (atom types, attributions, fingerprints, concordance entries, evidence quality signals) but never deletes upstream fields. The atom schema inherits passage-level context by reference (passage_id) rather than by copying all passage fields — this is a design trade-off for storage efficiency, not metadata deletion. Any consumer needing passage-level metadata can look up the passage by passage_id. ✓ No gap.

---

## 6. Consensus Integration

The atomization engine does NOT use multi-model consensus for standard atomization. This is a conscious design decision.

**Rationale:** Atom boundaries and type classifications are judgments that benefit from a single consistent perspective rather than from averaging independent perspectives. Multi-model consensus is designed for decisions where agreement increases confidence (e.g., "is this excerpt correctly placed?"). Atom boundary placement is more analogous to annotation: different annotators may place valid boundaries in different positions, and averaging them produces worse results than letting one skilled annotator work consistently.

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
| ATOM_LAYER_DISTRIBUTION_SUSPICIOUS | Info (Warning for commentary_unit) | All atoms in a multi-layer passage have the same layer. Escalated to warning severity when structural_format is "commentary_unit" (ADV-2). | Log and flag source for review. For commentary_unit passages, set "single_layer_in_commentary" review flag on all atoms. Does not block processing. |
| ATOM_HIGH_UNCLASSIFIED_RATE | Warning | >5% of source atoms have scholarly_function: "unclassified" | Flag source for human review. Suggests prompt needs improvement for this source's content type. |
| ATOM_QURAN_REF_UNRESOLVED | Info | Quran fragment detected by pattern but could not match to specific ayah | Set unresolved_quran_ref review flag on the atom. Does not block processing. |
| ATOM_ATTRIBUTION_PARSE_FAILURE | Warning | The LLM returned an attribution entry that does not conform to the ScholarlyAttribution schema (§4.B.4) | Drop the malformed attribution entry. Log the raw LLM output for debugging. Set review_flags: ["low_attribution_confidence"] on the atom. |
| ATOM_ATTRIBUTION_MARKER_MISSING | Warning | An attribution entry's marker_text is empty or does not appear as a substring in atom_text (ADV-3). | Drop the attribution entry. Log the dropped attribution details (attributed_to, atom_id). Set review_flags: ["low_attribution_confidence"]. |
| ATOM_ATTRIBUTION_LOW_CONFIDENCE | Info | An attribution entry has confidence below attribution_confidence_threshold (§4.B.4) | Set review_flags: ["low_attribution_confidence"] on the atom. Does not block processing. |
| ATOM_EVIDENCE_TYPE_CONFLICT | Info | Rule-based pre-detection (≥0.90 confidence) and LLM classification disagree on evidence type (ADV-5). | Set review_flags: ["evidence_type_conflict"]. LLM classification preserved. Log both pre-detection type and LLM type. Does not block processing. |
| ATOM_FOOTNOTE_INDEX_OUT_OF_RANGE | Warning | A footnote marker ⌜N⌝ in passage_text references index N-1 beyond the footnotes array length (ADV-8). | Record footnote_ref with linked_footnote_atom_id: null. Set review_flags: ["orphaned_footnote_marker"]. Does not block processing. |
| ATOM_OVER_SEGMENTATION | Warning | V-9 density check: atoms_per_character > 0.5 (ADV-12). | Re-atomize with explicit density feedback in LLM prompt (1 retry). If retry also over-segments, write atoms with "over_segmented" review flag. Flag source for human review. |
| ATOM_FINGERPRINT_HASH_FAILURE | Warning | Text normalization for fingerprint hashing failed (e.g., CAMeL Tools error on malformed Unicode) (§4.B.5) | Set fingerprint_text_hash to null for this atom. Log the error. Does not block processing. |
| ATOM_FINGERPRINT_EMBEDDING_FAILURE | Warning | Embedding model call failed for Tier 3 fingerprinting (§4.B.5) | Set fingerprint_embedding to null for this atom. Log the error. Does not block processing — Tier 1 and Tier 2 fingerprints remain available. |
| ATOM_FINGERPRINT_KEY_TERMS_EMPTY | Info | The LLM returned zero key terms for an atom during Tier 2 fingerprinting (§4.B.5) | Set fingerprint_key_terms to empty array. Log a warning. Does not block processing. |
| ATOM_UNKNOWN_LAYER_TYPE | Warning | A text_layer segment has a layer_type value not in the mapping (§4.A.6) | Default to source_layer "matn". Set review_flags: ["ambiguous_layer"]. Log the unrecognized value. |
| ATOM_COMPLETENESS_PATTERN_MISMATCH | Info | §4.B.6 pattern matcher found a rhetorical pattern but expected components are missing | Record gap in completeness_score. Set "incomplete_argument" review flag on all passage atoms. Does not block processing. |
| ATOM_CONCORDANCE_EXTRACTION_FAILURE | Warning | LLM failed to extract defined_term from a definition atom during §4.B.7 | Set concordance_entry to null for this atom. Log the passage_id and atom text. Does not block processing. |
| ATOM_EVIDENCE_QUALITY_PARSE_FAILURE | Warning | LLM returned a quality signal entry that does not conform to the EvidenceQualitySignal schema (§4.B.8) | Drop the malformed signal entry. Log the raw LLM output. Does not block processing. |

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
| enable_completeness_scoring | true | true/false | Whether to run §4.B.6 argument completeness scoring. Requires §4.B.1 rhetorical pattern detection. |
| enable_concordance_extraction | true | true/false | Whether to extract terminological concordance entries from definition atoms (§4.B.7). |
| enable_evidence_quality_detection | true | true/false | Whether to detect evidence quality signals in evidence atoms (§4.B.8). |
| evidence_quality_lexicon_path | engines/atomization/lexicons/evidence_quality.json | Any path | Path to the quality signal phrase lexicon for §4.B.8. |

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
- [NOT YET IMPLEMENTED] Argument completeness scoring (§4.B.6). Depends on §4.B.1 rhetorical pattern detection.
- [NOT YET IMPLEMENTED] Cross-atom terminological concordance (§4.B.7). No external dependencies beyond the LLM.
- [NOT YET IMPLEMENTED] Evidence quality signal detection (§4.B.8). Requires quality signal lexicon file.

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
26. **Argument completeness scoring (§4.B.6).** Verify that a khilaf passage with two opinions and evidence for both scores completeness_ratio 1.0. Verify that a passage with two opinions but evidence for only one scores < 1.0 with the correct gap_description. Verify that a passage with no detected rhetorical pattern has completeness_score null. 3 test cases.
27. **Terminological concordance extraction (§4.B.7).** Verify that definition atoms produce concordance_entry with correct defined_term. Test with: a standard genus-differentia definition ("المبتدأ هو الاسم المرفوع"), a definition mentioning alternate terms ("ويُسمى أيضاً المُسنَد إليه"), and a definition without genus-differentia pattern. Verify alternate_terms is populated when the text mentions synonyms and empty otherwise. 3 test cases.
28. **Terminological index per source (§4.B.7).** Verify that the per-source term_index.json is produced after atomization, contains all definition atoms' concordance entries, and includes correct atom_id and passage_id references. 1 test case.
29. **Evidence quality signal detection (§4.B.8).** Verify that a hadith citation with "رواه البخاري ومسلم" produces a hadith_strong_collection signal with quality_direction "positive". Verify that "وفي إسناده ضعف" produces a hadith_weakness_flag signal with quality_direction "negative". Verify that non-evidence atoms have evidence_quality_signals null. 3 test cases.
30. **Evidence quality signal disabled (§4.B.8).** Verify that when enable_evidence_quality_detection is false, all atoms have evidence_quality_signals null. 1 test case.
31. **Attribution marker verification (ADV-3).** Verify that an attribution entry whose marker_text does not appear in atom_text is dropped and ATOM_ATTRIBUTION_MARKER_MISSING is logged. Verify that a "self" attribution type with valid but non-substring marker_text passes the relaxed check. 2 test cases.
32. **Evidence type conflict detection (ADV-5).** Verify that when rule-based pre-detection flags a span as hadith evidence (confidence ≥ 0.90) and the LLM classifies the atom as evidence_rational, the atom receives "evidence_type_conflict" review flag and ATOM_EVIDENCE_TYPE_CONFLICT is logged. 2 test cases.
33. **Orphaned footnote marker (ADV-8).** Verify that a passage_text containing ⌜3⌝ with a footnotes array of length 2 produces footnote_refs with linked_footnote_atom_id: null, "orphaned_footnote_marker" review flag, and ATOM_FOOTNOTE_INDEX_OUT_OF_RANGE is logged. 1 test case.
34. **Atom reordering (ADV-10).** Verify that when LLM returns atoms in reverse order, V-4 sorts them by anchor_span.start, reassigns sequence_in_passage, and sets "atom_reordering_applied" review flag on all atoms. 1 test case.
35. **Over-segmentation detection (ADV-12/V-9).** Verify that a passage of 50 characters producing 30 atoms triggers ATOM_OVER_SEGMENTATION and re-atomization with density feedback. Verify that if the retry also over-segments, atoms are written with "over_segmented" review flag. 2 test cases.
36. **Commentary V-6 escalation (ADV-2).** Verify that a commentary_unit passage where all atoms have source_layer "matn" triggers ATOM_LAYER_DISTRIBUTION_SUSPICIOUS at warning severity (not info) and sets "single_layer_in_commentary" review flag. 1 test case.
37. **NFC normalization flag (Invariant 2).** Verify that when §2 step 5 normalizes NFD text to NFC, the source receives "nfc_normalization_applied" review flag. Verify that NFC text does not trigger the flag. 2 test cases.
38. **Confidence laundering prevention (ADV-9).** Verify that atoms with function_confidence 0.31 (above 0.3 threshold) receive "low_function_confidence" review flag (since 0.31 < 0.6) and that a source where 100% of atoms have this flag triggers ATOM_HIGH_UNCLASSIFIED_RATE review. 1 test case.

**Regression testing strategy:** Gold baselines are never modified after initial creation (they are immutable ground truth). Any change to the atomization engine's code, prompts, or configuration triggers a full regression run against all gold baselines. If any gold baseline regresses (accuracy drops), the change is rejected until the regression is resolved.

**Integration test requirements:**
- **Upstream (passaging → atomization):** Read actual passage streams produced by the passaging engine and verify that the atomization engine can process them without input validation errors. Test with at least 3 real sources.
- **Downstream (atomization → excerpting):** Verify that the atom stream produced by the atomization engine conforms to the schema expected by the excerpting engine's input contract. This requires the excerpting engine SPEC to be written first; until then, verify against the atom schema.
