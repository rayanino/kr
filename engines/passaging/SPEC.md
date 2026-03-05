# Passaging Engine — محرك التقطيع — Specification

## 1. Purpose and Scope

The passaging engine is the first Phase 2 engine. It receives normalized packages from the normalization engine and divides them into passages — the processing units that all downstream engines operate on. It is source-agnostic: it sees only the universal normalized schema, never raw source files.

**What this engine does.** It assembles cross-page text from per-page content units, uses the division tree and structural format metadata to determine intelligent passage boundaries, calibrates passage size for downstream processing quality, and outputs a passage stream that preserves all upstream metadata while adding positional context.

**What this engine does NOT do.** It does not identify atom types within passages (atomization engine). It does not determine self-contained teaching units (excerpting engine). It does not assign topics or place content in the taxonomy (taxonomy engine). It does not modify, correct, or enrich the text content — it segments it.

**Phase classification.** Phase 2 — source-agnostic, below the normalization boundary. No source-format-specific logic, identifiers, or assumptions appear in this engine.

**Normalization boundary relationship.** The normalization engine provides structure discovery (division tree, heading hierarchy) and per-page content. The passaging engine uses that structure to create processing units. The distinction: the normalization engine discovers the source's OWN organizational hierarchy; the passaging engine creates right-sized segments FOR processing. These often align (a small فصل becomes one passage) but need not (a 40-page باب is split into multiple passages; three tiny adjacent تنبيه sections are merged into one passage).

**User scenarios served.** All scenarios in USER_SCENARIOS.md depend on passage quality because passages constrain excerpts (D-011: passage containment rule). Specifically: Scenario 1–2 (study workflow depends on excerpt quality, which depends on passage quality), Scenario 6 (new source processing), Scenario 7 (science map completeness depends on correct passage→excerpt→placement chain), Scenario 8 (correction tracing back through passages).

**What this engine must produce for each scenario to work.** Each passage must be: topically coherent (a human reader would agree the content belongs together), appropriately sized (large enough for meaningful extraction, small enough for focused processing), boundary-clean (never splitting a definition, evidence chain, verse, or argument mid-sentence), and metadata-complete (carrying all information downstream engines need without re-reading the normalized package).

---

## 2. Input Contract

The passaging engine receives a single input artifact: a normalized package at `library/sources/{source_id}/normalized/`.

**Manifest (`manifest.json`).** The passaging engine reads these manifest fields:

- `source_id` — links to the source metadata record for all upstream metadata.
- `division_tree` — the structural hierarchy. Array of division nodes, each with: `div_id`, `type`, `title`, `level`, `detection_method`, `confidence`, `start_unit_index`, `end_unit_index`, `parent_div_id`, `child_div_ids`, `digestible`, `editor_inserted`. This is the primary boundary guidance signal.
- `structural_format` — one of: `prose`, `verse`, `qa_format`, `tabular_khilaf`, `dictionary`, `commentary`, `mixed`. Selects the passaging strategy.
- `layer_map` — detected text layers for multi-layer sources. Each entry: `layer_type`, `author_canonical_id`, `markers`, `confidence`.
- `verse_detection` — whether versified text was found and the numbering scheme.
- `total_content_units` — expected number of records in the content stream.
- `text_fidelity_summary` — aggregate fidelity metrics.

**Content stream (`content.jsonl`).** One record per physical page, ordered by `unit_index`. The passaging engine reads all fields defined in the normalization engine SPEC §3.

**Source metadata (via `source_id` reference).** The passaging engine accesses source metadata for:
- `science_scope` — science classification (array). For multi-science sources, passages may carry per-passage science hints.
- `genre` / `genre_chain` — work genre relationships (sharh_of, etc.).
- `structural_format` — source-level classification (the normalization engine's may override this).
- `multi_layer` — whether the source has multiple text layers.

**Validation on input.**

The passaging engine validates before processing:

1. The manifest file exists and is valid JSON. Failure: `PSG_MANIFEST_INVALID` (fatal).
2. `schema_version` is a recognized version. Failure: `PSG_SCHEMA_UNSUPPORTED` (fatal).
3. The content stream file exists. Failure: `PSG_CONTENT_MISSING` (fatal).
4. `total_content_units` matches the actual record count in the content stream. Mismatch: `PSG_CONTENT_COUNT_MISMATCH` (warning — process with actual count, log discrepancy).
5. Content units are ordered by `unit_index` with no gaps. Out-of-order: `PSG_CONTENT_UNORDERED` (fatal). Gap detected: `PSG_CONTENT_GAP` (warning — skip missing indices, flag affected passages).
6. The division tree, if non-empty, has consistent `start_unit_index`/`end_unit_index` ranges that cover the content stream without overlap. Inconsistency: `PSG_DIVISION_INCONSISTENT` (warning — fall back to flat passaging for affected regions).

Validation failures at `fatal` severity abort processing. Warnings are logged and processing continues with degraded behavior.

---

## 3. Output Contract

The passaging engine produces one primary artifact per source: a passage stream.

**Primary artifact: the passage stream.**

Written to `library/sources/{source_id}/passages/passages.jsonl`. One JSONL record per passage. Each record conforms to the passage schema:

- `schema_version`: string, format `passage_v{major}.{minor}`. Current: `passage_v2.0`.
- `passage_id`: string, format `psg_{source_id}_{zero_padded_sequence}` (e.g., `psg_src_00147_0003`). Globally unique. Monotonically increasing within a source, following document order.
- `source_id`: string. The source's canonical identifier. Primary link to all upstream metadata.
- `sequence_index`: zero-based integer. Position of this passage within this source's passage stream. Authoritative ordering identifier.
- `passage_text`: string. The complete assembled text for this passage. Produced by concatenating `primary_text` from the constituent content units, with cross-page joining applied (§4.A.2). Footnote reference markers (`⌜N⌝`) preserved inline. Diacritics preserved exactly. Minimum length: 1 character (a passage is never empty; empty divisions produce no passage).
- `text_layers`: array. For multi-layer sources, the merged layer segments covering this passage's text, with character offsets rebased to `passage_text` (not to individual content unit texts). Each segment: `layer_type`, `author_canonical_id`, `start`, `end`, `confidence`. For single-layer sources, one segment covering the full text.
- `footnotes`: array. All footnotes from the constituent content units that are referenced within this passage's text range. Each footnote: `ref_marker`, `text`, `footnote_type`, `confidence`, `source_unit_index` (which content unit the footnote originated from).
- `division_path`: array of objects. The path from the division tree root to this passage's position. Each object: `div_id`, `type`, `title`, `level`. Provides full hierarchical context (e.g., `[{root}, {كتاب الصلاة}, {باب صلاة الجماعة}, {فصل في أحكام الإمامة}]`).
- `division_ids`: array of strings. The `div_id`(s) of the leaf division(s) this passage covers. Usually one. Multiple if small sibling divisions were merged.
- `heading_text`: string or null. The heading text for this passage's primary division. Null if the passage was created by splitting a larger division (the split pieces share the parent heading, but only the first piece carries it directly).
- `unit_range`: object with `start` (int) and `end` (int, inclusive). The `unit_index` range of content units that contribute text to this passage.
- `physical_pages`: object. `volume` (int or null), `start_page_display` (string or null), `end_page_display` (string or null), `start_page_int` (int or null), `end_page_int` (int or null), `page_count` (int). Human-readable page range for citation purposes.
- `structural_format`: string. The format strategy applied to this passage (prose/verse/qa_pair/tabular_masala/dictionary_entry/commentary_unit). May differ from the source-level `structural_format` if the source is `mixed`.
- `verse_info`: object or null. For verse passages: `verse_lines` (array of verse objects with `verse_number`, `first_hemistich`, `second_hemistich`), `verse_count` (int). Verse numbering preserved from the normalization engine.
- `content_flags`: object. Aggregated from constituent content units: `has_verse`, `has_table`, `has_quran_citation`, `has_hadith_citation`. True if ANY constituent unit has the flag.
- `text_fidelity`: object. `min_score` (lowest fidelity among constituent units), `mean_score` (average), `pages_with_warnings` (int).
- `sizing`: object. `action` (one of: `direct`, `merged`, `split`), `word_count` (int — Arabic word count), `char_count` (int — character count of `passage_text`), `notes` (string or null — explanation of merge/split).
- `predecessor_id`: string or null. `passage_id` of the preceding passage. Null for the first passage.
- `successor_id`: string or null. `passage_id` of the following passage. Null for the last passage.
- `review_flags`: array of strings. Machine-generated flags for human review. Possible values: `low_confidence_boundary` (boundary placed by heuristic with <0.7 confidence), `cross_volume` (passage spans a volume boundary), `very_short` (<50 Arabic words after assembly), `very_long` (>2000 Arabic words), `low_fidelity_content` (any constituent page has fidelity `very_low`), `split_from_large` (passage was created by splitting an oversized division), `merged_siblings` (passage merges multiple small divisions), `mixed_layers` (multi-layer source with uncertain layer boundaries in this passage), `implicit_boundary` (passage boundary placed at an inferred topic shift, not at a heading).

**Guarantees about the passage stream:**

- **Source-agnostic.** The passage schema is identical regardless of source type.
- **Ordering.** Passages are ordered by document order. `sequence_index` is zero-based, monotonically increasing, gapless.
- **Complete coverage.** Every content unit with `digestible: true` in the division tree is covered by exactly one passage. No text from digestible divisions is lost. Content units with `is_toc_page: true`, `is_index_page: true`, or `is_blank: true` are excluded unless they fall within a digestible division that contains substantive text.
- **Non-overlapping.** No content unit contributes to more than one passage. Passage text ranges partition the source content without overlap.
- **Boundary integrity.** No passage boundary falls mid-sentence. Cross-page sentence joining (§4.A.2) ensures that sentences are never split by page breaks. Verse lines (بيت) are never split across passages.
- **Metadata completeness (D-023).** Every passage carries `source_id` for upstream metadata access, `division_path` for structural context, `physical_pages` for citation, `text_layers` for authorship attribution, `content_flags` for downstream hints, and `text_fidelity` for quality awareness. No upstream metadata is stripped.
- **Passage self-sufficiency.** Each passage record contains all text and metadata needed for atomization and excerpting. Downstream engines do not need to access the normalized package, only the passage stream and the source metadata record (via `source_id`).

**Metadata pass-through (D-023).** The passaging engine preserves all upstream metadata by reference (`source_id`) and adds:
- Passage boundaries and sequence ordering
- Division path (hierarchical structural context)
- Physical page ranges (citation metadata)
- Assembled passage text (cross-page joined)
- Rebased text layer segments
- Aggregated content flags and fidelity
- Sizing metadata (merge/split/direct)
- Review flags for quality gating

**Source registry update.** Upon successful passaging, the source's processing status is updated from `normalized` to `passaged`. The passage stream path is recorded.

---

## 4. Processing Specification

### §4.A — Core Processing

#### §4.A.1 — Processing Overview

Passaging proceeds in five sequential phases:

1. **Load and validate** (§2): Read manifest and content stream, validate input contract.
2. **Assemble text** (§4.A.2): Join cross-page text, produce continuous text blocks aligned to division boundaries.
3. **Select strategy** (§4.A.3): Choose passaging strategy based on `structural_format`.
4. **Create passages** (§4.A.4–§4.A.9): Apply the selected strategy to produce passage boundaries.
5. **Emit and validate** (§4.A.10): Write passage records, run self-validation.

The engine processes one source at a time. Batch processing of multiple sources is an orchestration concern outside this SPEC.

#### §4.A.2 — Cross-Page Text Assembly

The normalization engine outputs per-page content units with text that ends at page boundaries — it does not join text across pages (normalization SPEC §4.A.7). The passaging engine is responsible for cross-page text assembly.

**Assembly process.** For a contiguous range of content units (as defined by a division or passage boundary), the engine concatenates the `primary_text` fields in `unit_index` order. Between adjacent units, the engine applies joining logic:

1. If the last unit's text ends mid-word (no terminal whitespace or punctuation) and the next unit's text starts with a word continuation, the two are joined without separator. Detection: the last character of unit N is a letter (Arabic or Latin) AND the first character of unit N+1 is a letter, with no whitespace between them.
2. If the last unit's text ends with a complete word (followed by whitespace or punctuation) and the next unit starts a new sentence or paragraph, a single newline separates them.
3. If the last unit's text ends mid-sentence (no sentence-terminal punctuation: `.`, `؟`, `!`, `،` at a natural clause boundary) and the next unit continues the sentence, a single space joins them.
4. If both units end and start cleanly (sentence boundary to new sentence), the original whitespace pattern is preserved.

**Cross-page footnote renumbering.** When assembling text across pages, footnote reference markers (`⌜N⌝`) may collide if two pages both have a footnote `⌜1⌝`. The passaging engine renumbers footnotes within the assembled passage text to be sequentially unique. The renumbering maps old markers to new ones, and the `footnotes` array in the passage record uses the new markers. The mapping is deterministic: footnotes are numbered in order of appearance in the assembled text.

**Text layer rebasing.** When assembling text from multiple content units, `text_layers` segments from each unit must be rebased to the assembled passage text. Character offsets from per-unit segments are recalculated relative to the start of the assembled text. Adjacent segments from the same layer and author are merged into a single segment.

**Handling non-digestible content units.** Content units flagged as `is_toc_page`, `is_index_page`, or `is_blank` within a division marked `digestible: false` are skipped entirely — they produce no passage text. If such units appear WITHIN a digestible division (e.g., a blank page in the middle of a chapter), they are skipped during assembly but their `unit_index` is recorded so the page range remains accurate for citation.

#### §4.A.3 — Strategy Selection

The passaging engine selects a strategy based on the manifest's `structural_format` field. Each strategy implements the same interface (input: assembled text blocks + division tree; output: passage boundary decisions) but uses different logic for boundary placement.

| `structural_format` | Strategy | Primary reference |
|---|---|---|
| `prose` | Division-guided with semantic splitting | §4.A.4 |
| `verse` | Verse-group passaging | §4.A.5 |
| `qa_format` | Q&A pair passaging | §4.A.6 |
| `tabular_khilaf` | Masala-block passaging | §4.A.7 |
| `dictionary` | Entry-boundary passaging | §4.A.8 |
| `commentary` | Commentary-unit passaging | §4.A.9 |
| `mixed` | Per-division strategy selection | §4.A.3.1 |

**§4.A.3.1 — Mixed-format sources.** When `structural_format` is `mixed`, the engine examines each leaf division individually. It uses the division's `content_flags` and the text content to classify each division into one of the specific format types. A division with `has_verse: true` on all its pages gets the verse strategy. A division whose text matches Q&A patterns gets the `qa_format` strategy. Divisions that don't match a specific format default to the prose strategy. Each division is passaged independently using its assigned strategy.

#### §4.A.4 — Prose Strategy (Division-Guided with Semantic Splitting)

This is the default and most common strategy. It handles standard scholarly prose — the majority of the Islamic scholarly corpus.

**Passage size targets.** Arabic text is morphologically denser than English. A single Arabic word may encode a full clause. Empirical calibration: a passage of 200–800 Arabic words (measured by whitespace tokenization) is the target range. This yields passages that typically contain one or two complete scholarly arguments, with enough context for self-contained excerpts but not so much that the excerpting engine must pick through unrelated material.

- **Minimum passage size:** 50 Arabic words. Passages below this threshold are merged with an adjacent sibling or, if no sibling exists, with the nearest preceding passage.
- **Target passage size:** 200–800 Arabic words. Divisions in this range become passages directly with `sizing.action: "direct"`.
- **Maximum passage size (soft):** 800 Arabic words. Divisions exceeding this are candidates for splitting but are not automatically split — the engine first checks whether the content is a single coherent argument that should not be divided.
- **Maximum passage size (hard):** 2000 Arabic words. Divisions exceeding this are always split. Even a single coherent argument of 2000+ words is too large for focused excerpting.

**Step 1: Map divisions to candidate passages.** Walk the division tree to its leaf divisions (divisions with no children). Each leaf division is a candidate passage. Leaf divisions with `digestible: false` are skipped.

**Step 2: Size evaluation and boundary adjustment.** For each candidate passage:

- **In range (50–800 words):** Accept as-is. `sizing.action: "direct"`.
- **Below minimum (<50 words):** Merge with the next sibling division (or previous sibling if this is the last child). The merged passage lists all merged `division_ids` in its `division_ids` array. `sizing.action: "merged"`. If the merged result is still below minimum (and there are more siblings), continue merging. If all siblings of a parent are below minimum and their combined total is still below minimum, flag with `very_short`.
- **Above soft max (800–2000 words):** Attempt semantic splitting (Step 3). If no good split point is found (the entire division is a single coherent argument), accept as-is with `sizing.action: "direct"` and flag `very_long` if >1500 words.
- **Above hard max (>2000 words):** Force split (Step 3). If semantic splitting fails, fall back to paragraph-boundary splitting. If no paragraph boundaries exist, split at sentence boundaries aiming for ~500-word segments.

**Step 3: Semantic splitting for oversized divisions.** When a division must be split, the engine identifies natural sub-topic boundaries within the text:

1. **Paragraph boundary scan.** Identify paragraph breaks (double newline patterns). These are the preferred split points because they typically align with topic shifts in scholarly prose.
2. **Scholarly keyword scan.** Within paragraphs, search for topic-transition indicators: ordinal markers (أولاً، ثانياً، ثالثاً), contrastive markers (وأما، ولكن), new-topic markers (ومن ذلك، وأما مسألة), evidence markers (والدليل على ذلك، لقوله تعالى). These indicate sub-topic boundaries within a larger division.
3. **LLM-assisted splitting.** For divisions >1000 words where paragraph and keyword scans produce no satisfactory split point, the engine sends the text to an LLM with the prompt: "Identify the natural sub-topic boundaries in this Arabic scholarly text. Return the character offsets where one topic ends and another begins." The LLM response provides candidate split points. Each LLM-identified boundary gets `confidence: 0.6–0.8` and generates a `review_flag: "implicit_boundary"`.
4. **Fallback: fixed-interval splitting.** If all else fails (no paragraphs, no keywords, LLM unavailable), split at sentence boundaries (`.` or `؟` or `!` followed by space, at approximately 500-word intervals). `sizing.action: "split"`, `review_flag: "low_confidence_boundary"`.

**Split passage identity.** When a division is split into N passages, each passage carries: `division_ids: [original_div_id]`, `heading_text: null` (except the first piece, which carries the original heading), and `sizing: { action: "split", notes: "Split N of M from division {div_id}" }`.

**Sentence integrity rule.** No passage boundary falls mid-sentence. When a boundary calculation lands within a sentence, the boundary moves to the nearest sentence end (`.`, `؟`, `!`, or paragraph break). Sentence detection in Arabic uses: terminal punctuation marks, paragraph breaks, and a set of Arabic sentence-terminal patterns (subject to refinement against gold baselines).

#### §4.A.5 — Verse Strategy

Versified texts (منظومات) have fundamentally different structure than prose. Each بيت (verse couplet) is a self-contained unit. The verse strategy respects this structure absolutely.

**Verse detection.** The normalization engine provides `verse_detection` in the manifest and `verse_info` per content unit. The passaging engine uses these signals. A passage in verse mode contains one or more verse lines plus any associated commentary.

**Pure verse sources (no commentary).** For sources that are entirely نظم (e.g., a standalone copy of ألفية ابن مالك):

- Each passage contains a group of consecutive verses that form a topical unit. The division tree typically provides heading-based groupings (each باب in the ألفية is a division containing 5–50 verses).
- If a division contains ≤20 verses, the entire division is one passage.
- If a division contains >20 verses, split at verse group boundaries. The engine identifies topical shifts between verses using: explicit topic markers in the verse text, changes in the grammatical subject being discussed, and (if available) LLM classification of verse themes. Split at verse boundaries only — never mid-بيت.
- **Absolute rule:** A بيت is never split across passage boundaries. Both hemistichs of a verse always remain in the same passage.

**Commentary on verse (sharh on nazm).** This is the most common format for versified text processing (e.g., شرح ابن عقيل on الألفية). Each page contains: quoted verses from the matn (Layer 1) interspersed with prose commentary (Layer 2).

- A passage in this format is a **commentary unit**: one or more quoted verses plus all the commentary that explains them.
- The boundary between commentary units is defined by the transition from one verse group's commentary to the next verse's quotation. This transition is signaled by: the appearance of a new verse quotation (typically introduced by "قوله:" or "ومنه قول الناظم:"), a heading, or a shift in the verse number sequence.
- The passaging engine uses `verse_info` from content units and `text_layers` to identify where verse quotations appear and where commentary spans between them.
- Size targets: same as prose (200–800 words), but the minimum is lower (100 words) because a single verse + brief commentary may be shorter yet still form a coherent unit.

**Verse numbering preservation.** Each verse passage records the verse number range in `verse_info.verse_lines`. Verse numbers from the normalization engine are passed through exactly. If numbering is unavailable, the passaging engine assigns sequential numbers within each division (starting from 1), flagged as `inferred_numbering`.

#### §4.A.6 — Q&A Pair Strategy

Q&A-format sources (fatwa collections like مجموع الفتاوى, مسائل compilations) are structured as question-answer pairs.

**Q&A boundary detection.** The engine detects Q&A pairs using these signals:

1. **Explicit markers:** "سُئل عن" (he was asked about), "مسألة:" (question:), "سؤال:" (question:), "جواب:" (answer:). The question marker starts a new Q&A pair.
2. **Typographic signals:** If the normalization engine preserved bold or indented formatting (via structural markers), questions may be visually distinguished from answers.
3. **Pattern-based:** A new question marker after an answer section signals a new Q&A pair.

**Passage formation.** Each Q&A pair forms one passage. The passage includes: the question text, the answer text, and any footnotes within the pair.

- If a Q&A pair exceeds the hard maximum (2000 words), the answer is split at paragraph boundaries while keeping the question with the first split.
- If a Q&A pair is below the minimum (50 words), it is merged with the next Q&A pair, with `sizing.action: "merged"`.

**Fallback.** If Q&A detection fails (no recognizable question markers in a division classified as `qa_format`), the engine falls back to the prose strategy for that division and flags `review_flag: "format_detection_failed"`.

#### §4.A.7 — Masala-Block Strategy

Tabular khilaf works (disagreement catalogs like المغني, الإنصاف) are organized by مسألة (scholarly question). Each مسألة block is a natural passage unit.

**Masala boundary detection.** The engine detects مسألة blocks using:

1. **Heading markers:** "مسألة:", "فرع:", "تنبيه:" — explicit structural markers that typically begin a new scholarly question.
2. **Division tree alignment:** The division tree often has مسألة-level divisions if the source has fine-grained headings.
3. **Pattern-based:** In works with consistent structure (المسألة الأولى, المسألة الثانية, or ordinal numbering), sequential masala blocks are detected by ordinal patterns.

**Passage formation.** Each مسألة block is one passage. The block includes: the question formulation, all scholarly positions, evidence, and the author's conclusion (ترجيح) if present.

- If a مسألة exceeds the hard maximum, split at position boundaries (القول الأول / القول الثاني markers).
- If a مسألة is below minimum, merge with the next مسألة, flagged as `merged_siblings`.

#### §4.A.8 — Dictionary Entry Strategy

Lexicographic works (لسان العرب, القاموس المحيط) are organized by root or headword.

**Entry boundary detection.** Dictionary entries are typically marked by: the root word in a distinctive format (bold, parenthesized, or with a specific marker), alphabetical ordering, and conventional entry-start patterns.

The engine detects entries using: root word markers from the normalization engine's structural discovery, bold/emphasized text patterns at entry starts, and alphabetical sequencing of headwords.

**Passage formation.** Each dictionary entry is one passage. Entries that exceed the hard maximum (rare but possible for roots with many derivatives) are split at sub-entry boundaries (typically marked by derivative headwords within the root entry).

#### §4.A.9 — Commentary-Unit Strategy

This strategy applies when `structural_format` is `commentary` and the source has multi-layer text (matn + sharh, or sharh + hashiyah).

**Core principle: keep the commented-upon text and its commentary together.** A passage in commentary mode is a commentary unit: a segment of the commented-upon text (matn or sharh) plus all the commentary that explains it.

**Commentary unit detection.** The engine identifies commentary units using text layer information from the normalized package:

1. **Layer transition tracking.** Using `text_layers` segments, the engine tracks transitions from Layer 1 (matn) to Layer 2 (sharh) and back. Each matn segment plus its following sharh segment(s) form a candidate commentary unit.
2. **Matn quotation markers.** In sharh texts, the commentator quotes the matn with markers like "قوله:" (his [the matn author's] saying:), "قال المصنف:" (the author said:), or simply with typographic distinction (brackets, bold). Each new matn quotation starts a new commentary unit.
3. **Division alignment.** The division tree may have divisions that correspond to commentary units (common in well-structured tahqiq editions).

**Passage formation.** Each commentary unit is one passage. The passage text contains both the matn segment and its commentary, with `text_layers` providing character-level attribution of which text belongs to which author.

- If a commentary unit exceeds the hard maximum (common when brief matn text receives lengthy commentary), split the commentary portion at paragraph boundaries while keeping the matn segment with the first split.
- Absolute rule: A matn segment is never split across passages. The matn segment always appears in full in one passage.
- If matn segments are very long (e.g., the commented-upon text quotes an entire chapter of the original), split at sentence boundaries within the matn, creating multiple commentary units each containing a portion of the matn plus whatever commentary covers that portion.
- For three-layer texts (matn/sharh/hashiyah), the passage contains all three layers' text for the same segment. Layer attribution in `text_layers` distinguishes them.

**Single-layer commentary sources.** If a source is classified as `commentary` but `layer_map` indicates only one layer (the normalization engine could not detect layer transitions), the engine falls back to the prose strategy. `review_flag: "commentary_layers_undetected"`.

#### §4.A.10 — Passage Emission and Self-Validation

After creating all passage boundaries, the engine produces the output passage stream.

**Emission process.** Passages are emitted in document order. Each passage receives: a `passage_id` and `sequence_index` (assigned sequentially), the assembled text with rebased layers and renumbered footnotes, the division path, physical pages, and all metadata fields defined in §3.

**Predecessor/successor linking.** After all passages are emitted, the engine sets `predecessor_id` and `successor_id` fields by iterating through the passage list. This creates a doubly-linked chain that downstream engines can traverse.

**Self-validation (§8 Layer 1).** The engine validates its own output before declaring success:

1. **Coverage check.** Every content unit in a digestible division must be covered by exactly one passage. `assert sum(passage_unit_ranges) == set(all_digestible_unit_indices)`.
2. **Non-overlap check.** No content unit appears in multiple passages.
3. **Ordering check.** Passages are strictly ordered by `sequence_index`, and their `unit_range.start` values are monotonically increasing.
4. **Text integrity check.** For each passage, verify that `passage_text` matches the concatenated `primary_text` of its constituent content units (after cross-page joining). Hash comparison.
5. **Layer coverage check.** For multi-layer sources, every character in `passage_text` is covered by exactly one `text_layers` segment.
6. **Size sanity.** No passage exceeds 3x the hard maximum (6000 words) — this would indicate a splitting failure. Flag and log if found.
7. **Footnote reference integrity.** Every `⌜N⌝` marker in `passage_text` has a corresponding entry in the `footnotes` array.

Validation failures at self-validation produce `PSG_VALIDATION_*` errors. Coverage or overlap failures are fatal (the passage stream is not written). Size and footnote issues are warnings (the passage stream is written but flagged).

### §4.B — Transformative Capabilities

#### §4.B.1 — Passage Quality Prediction

**Capability:** Before downstream engines process passages, the passaging engine predicts which passages are likely to produce high-quality excerpts and which are likely to cause problems. This prediction is metadata on each passage that helps the excerpting engine prioritize and the human gate focus review.

**Technical approach.** A quality prediction model (LLM-based, with future option to train a lightweight classifier on accumulated data) scores each passage on three dimensions:

- **Topical coherence (0.0–1.0):** Does this passage discuss a single clear topic, or does it wander across multiple subjects? Measured by: semantic similarity of the passage's sentences (computed via sentence embeddings — use a multilingual model like `intfloat/multilingual-e5-large` or `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`). High variance in sentence embeddings within a passage suggests low coherence.
- **Boundary quality (0.0–1.0):** Do the passage boundaries fall at natural topic transitions? Measured by: the semantic distance between the last sentence of this passage and the first sentence of the next passage. High distance = good boundary (different topics). Low distance = bad boundary (the boundary split a continuous topic).
- **Extractability (0.0–1.0):** Does the passage contain content that can produce self-contained excerpts? Measured by: presence of definitional patterns, scholarly position markers, evidence citations, or other extractable content types. A passage that is pure transitional text has low extractability.

**Output.** Each passage record receives a `quality_prediction` field: `{ coherence: float, boundary_quality: float, extractability: float, overall: float }`. The `overall` score is a weighted average (coherence 0.4, boundary_quality 0.3, extractability 0.3).

**Why this is transformative.** No existing text chunking system predicts downstream processing quality. Passage quality prediction enables: prioritized processing (excerpt high-quality passages first), targeted human review (focus on low-quality passages), and iterative improvement (the excerpting engine feeds back actual excerpt quality, which the passaging engine uses to refine its predictions over time).

[NOT YET IMPLEMENTED] — Full specification provided. Depends on: a sentence embedding model with good Arabic support, and feedback data from the excerpting engine to calibrate predictions.

#### §4.B.2 — Implicit Structure Discovery

**Capability:** Many scholarly texts have minimal or no headings — the author wrote continuous prose without فصل or باب markers. The normalization engine reports these as `structure_confidence: "minimal"`. The passaging engine detects implicit scholarly structure within these headingless texts, producing passage boundaries that align with the author's unstated topic organization.

**Technical approach.** The engine analyzes the text using three complementary signals:

1. **مسألة boundary detection.** Islamic scholarly texts, even without headings, are organized around مسائل (scholarly questions). The engine detects implicit مسألة boundaries by looking for patterns: "وأما" (as for...) introducing a new sub-topic, "ومنها" (and among them...) listing items, "واختلفوا في" (they disagreed about...) introducing a new point of disagreement, "والمسألة الثانية" (the second question) with ordinal numbering even without heading formatting.

2. **Topic shift detection via embeddings.** Using a multilingual sentence embedding model, the engine computes a sliding-window topic coherence score across the text. Significant drops in coherence (measured as cosine distance between adjacent sentence windows exceeding a threshold) indicate topic shifts. The threshold is calibrated per genre: sharh texts have more internal coherence variation than matn texts.

3. **LLM-based structural analysis.** For texts where signal 1 and 2 disagree or are ambiguous, the engine sends a 2000-word window to an LLM with the prompt: "This Arabic scholarly text has no headings. Identify where one scholarly topic ends and another begins. For each boundary, provide: the character offset and a brief title describing the new topic." The LLM response produces candidate divisions with generated titles. These generated titles are stored as `heading_text` on the passage with `heading_source: "llm_inferred"`, clearly distinguished from author-original headings.

**Integration with the division tree.** When the normalization engine reports `structure_confidence: "minimal"`, the passaging engine runs implicit structure discovery BEFORE applying the prose strategy. The discovered structure is treated as a supplementary division tree that guides passage boundary placement. This supplementary tree is stored alongside the passage stream (not written back to the normalization engine's output — the normalization boundary is not violated).

**Why this is transformative.** Many important early Islamic texts (particularly pre-5th century AH works) have no chapter structure. Scholars navigate them by memorization and familiarity. KR makes these texts structurally navigable for the first time — producing passage boundaries and generated topic headings that make a headingless text as browsable as a well-organized modern edition. This is a capability that even printed tahqiq editions do not provide.

[NOT YET IMPLEMENTED] — Full specification provided. Depends on: Arabic sentence embedding model, LLM API access. Feasibility verified: LLMs demonstrably identify topic boundaries in Arabic text; sentence transformers have Arabic support via multilingual models.

#### §4.B.3 — Commentary-Matn Precision Alignment

**Capability:** For commentary sources (sharh on matn), the passaging engine produces a precise mapping between each matn segment and the exact commentary text that explains it. This goes beyond basic passage creation: it creates a structured alignment that downstream engines use to understand WHAT the commentator is explaining WHERE.

**Technical approach.** The engine processes commentary sources in two phases:

1. **Matn segment extraction.** Using `text_layers` and matn quotation markers, extract every discrete matn segment quoted in the commentary. Each segment: the matn text, its character offsets in the passage, the matn verse/line number (if the matn is versified), and the matn author's canonical ID.

2. **Commentary span mapping.** For each matn segment, identify the span of commentary text that directly explains it. The commentary span starts after the matn quotation and ends just before the next matn quotation (or at the passage boundary). The engine produces an alignment record: `{ matn_segment: {text, start, end, verse_number?}, commentary_span: {start, end}, alignment_confidence: float }`.

**Output.** Each commentary-type passage receives a `commentary_alignment` field: an array of alignment records. This structured data enables the excerpting engine to create excerpts that pair specific matn text with its specific commentary — not just "a passage from the sharh" but "the commentator's explanation of this specific verse."

**Why this is transformative.** Classical Islamic scholarship is built on commentary chains (matn→sharh→hashiyah). Understanding WHICH part of the matn is being explained by WHICH commentary text is fundamental to reading these works. No existing digital tool provides this alignment — readers must track it mentally. KR makes it explicit and machine-readable. This enables the synthesizing engine to compare how DIFFERENT commentators explain the SAME matn segment — a comparison that is extremely labor-intensive to do manually across multiple commentary editions.

[NOT YET IMPLEMENTED] — Full specification provided. Depends on: text layer data from the normalization engine, matn quotation marker detection. Technical feasibility: high — the signals (quotation markers, layer transitions) are well-defined.

#### §4.B.4 — Cross-Edition Passage Correspondence

**Capability:** When the library contains multiple editions of the same work (different tahqiq editions with different pagination, footnotes, and sometimes different text variants), the passaging engine establishes passage-level correspondence between them. Passage N in edition A corresponds to passage M in edition B — they cover the same content from the same author, even though page numbers differ.

**Technical approach.** When the source engine's work registry indicates that multiple sources share the same `work_id`, the passaging engine can run a correspondence analysis:

1. **Text similarity matching.** For each passage in the new edition, compute its similarity to all passages in existing editions (using character n-gram overlap, not semantic similarity, because the text SHOULD be nearly identical). Matches with >80% character overlap are considered correspondences.
2. **Division tree alignment.** If both editions have division trees, align them by heading text similarity. Matching headings confirm passage correspondence.
3. **Sequential ordering.** Passages in both editions follow the same author's text in the same order. Sequential alignment (dynamic time warping) resolves cases where passage boundaries differ but content order is preserved.

**Output.** A correspondence record at `library/sources/{source_id}/passages/cross_edition_map.json`: an array of `{ this_passage_id, other_source_id, other_passage_id, overlap_score, alignment_method }`. This enables the excerpting engine to compare how the same text was edited across editions, and the synthesizer to note textual variants.

**Why this is transformative.** Edition comparison is a core activity in Islamic textual criticism (تحقيق). Scholars spend hours comparing different prints of the same work to identify variants, corrections, and editorial additions. KR automates the first step: aligning the editions at passage level so that the comparison can be done systematically. The KITAB project's passim algorithm (see RESOURCES.md) demonstrates that text reuse detection in Arabic is feasible at this scale.

[NOT YET IMPLEMENTED] — Full specification provided. Depends on: multiple editions of the same work in the library (requires the source engine's work registry to track `work_id` relationships). Technical approach: character n-gram matching is straightforward; the KITAB project uses Smith-Waterman alignment on 300-word chunks of Arabic text.

---

## 5. Validation and Quality

**Self-validation (Layer 1).** The passaging engine runs the seven self-validation checks defined in §4.A.10 on every output. These are automated, deterministic, and mandatory.

**Automated checks (Layer 2).** The following automated quality checks run after passaging completes:

1. **Size distribution analysis.** Compute the distribution of passage word counts. If >20% of passages are below the minimum or above the hard maximum, flag the source for review (`PSG_SIZE_DISTRIBUTION_SKEWED`). This may indicate that the structural format classification is wrong or that the division tree is poorly structured.
2. **Coherence spot-check.** For a random sample of 10% of passages (minimum 5, maximum 50), compute the topical coherence score (§4.B.1 method, if available). If the mean coherence is below 0.5, flag the source (`PSG_LOW_COHERENCE`).
3. **Boundary quality spot-check.** For a random sample of passage boundaries, check that the semantic distance between the last sentence of one passage and the first sentence of the next is above a threshold. If >30% of sampled boundaries have low semantic distance, flag (`PSG_WEAK_BOUNDARIES`).

**Human gate integration.** The passaging engine does not have its own dedicated human gate. Instead, passages flagged with `review_flags` are surfaced at the excerpting engine's human gate — the owner reviews problematic passages when they produce questionable excerpts. The passaging engine contributes to human review by: producing clear `review_flags` with descriptions, providing `sizing.notes` for merge/split explanations, and recording `quality_prediction` scores when available.

**What prevents errors from reaching the library.** A passaging error (bad boundary) produces a bad excerpt (broken argument, split definition). The passage containment rule (D-011) ensures that the error is contained: the bad passage produces bad excerpts that are caught at the excerpting engine's quality checks or the human gate. The passaging engine's contribution to error prevention is: self-validation that guarantees structural correctness (no missing content, no overlaps), and quality signals that direct attention to likely problems.

---

## 6. Consensus Integration

The passaging engine does NOT use multi-model consensus for its core processing. The reasoning:

1. **Passage boundaries are primarily structural, not interpretive.** Most boundaries follow the division tree, which is deterministic. The normalization engine (which IS interpretation-heavy in structure discovery) already applied consensus where needed.
2. **The few interpretive decisions (semantic splitting, implicit structure discovery) are flagged rather than consensus-validated.** When the engine places a boundary at an inferred topic shift rather than a heading, it flags it as `implicit_boundary` for human review. The human gate provides the validation that consensus would.
3. **Cost-benefit.** Running multiple LLM models on every passage boundary would multiply processing cost for marginal quality improvement. The downstream engines (excerpting, taxonomy) provide correction opportunities for any passaging errors.

**Exception:** The §4.B.2 implicit structure discovery capability, when implemented, may benefit from multi-model consensus for LLM-generated topic boundaries. If the normalization engine reports `structure_confidence: "minimal"` AND the source is a high-value scholarly text, running two LLMs independently and comparing their topic boundary proposals would reduce the risk of bad passage boundaries in headingless texts. This is a future design decision to be revisited when §4.B.2 is implemented.

---

## 7. Error Handling

| Error Code | Severity | Trigger | Recovery Action |
|---|---|---|---|
| `PSG_MANIFEST_INVALID` | Fatal | Manifest missing or invalid JSON | Abort. Log error. Source stays at `normalized` status. |
| `PSG_SCHEMA_UNSUPPORTED` | Fatal | Unrecognized schema version | Abort. Log error with version string. |
| `PSG_CONTENT_MISSING` | Fatal | Content stream file missing | Abort. Log error. |
| `PSG_CONTENT_COUNT_MISMATCH` | Warning | Manifest count ≠ actual count | Process with actual count. Log discrepancy. |
| `PSG_CONTENT_UNORDERED` | Fatal | Content units not in unit_index order | Abort. This indicates normalization corruption. |
| `PSG_CONTENT_GAP` | Warning | Gap in unit_index sequence | Skip missing indices. Flag affected passages with `low_confidence_boundary`. |
| `PSG_DIVISION_INCONSISTENT` | Warning | Division tree ranges inconsistent with content | Fall back to flat passaging for affected regions. Log specifics. |
| `PSG_FORMAT_DETECTION_FAILED` | Warning | Format-specific detection failed | Fall back to prose strategy. Flag with `format_detection_failed`. |
| `PSG_SPLIT_FALLBACK` | Info | Semantic splitting fell back to fixed-interval | Log. Flag passage with `low_confidence_boundary`. |
| `PSG_LLM_UNAVAILABLE` | Warning | LLM call failed (timeout, error) | Fall back to non-LLM splitting methods. Flag with `low_confidence_boundary`. |
| `PSG_VALIDATION_COVERAGE` | Fatal | Self-validation: content units missing from passages | Abort. Do not write passage stream. |
| `PSG_VALIDATION_OVERLAP` | Fatal | Self-validation: content unit in multiple passages | Abort. Do not write passage stream. |
| `PSG_VALIDATION_SIZE` | Warning | Self-validation: passage exceeds 3x hard max | Write passage stream. Flag passage. Log error. |
| `PSG_VALIDATION_FOOTNOTE` | Warning | Self-validation: orphaned footnote reference | Write passage stream. Log. Downstream engines may ignore orphaned markers. |
| `PSG_SIZE_DISTRIBUTION_SKEWED` | Warning | >20% of passages outside target range | Log. Flag source for structural review. |
| `PSG_LOW_COHERENCE` | Warning | Mean coherence below threshold | Log. Flag source. |
| `PSG_WEAK_BOUNDARIES` | Warning | >30% of boundaries have low semantic distance | Log. Flag source. |

**Error logging.** All errors are logged with: error code, severity, source_id, timestamp, affected passage_ids (if applicable), and a human-readable description. Warning-level and above are included in the source's processing status record.

**Principle: never lose data silently.** If an error prevents correct passaging of a region, the region's content units are still included in a passage (possibly an oversized one with a flag) rather than silently dropped. An over-large flagged passage is better than lost content.

---

## 8. Configuration

| Parameter | Default | Valid Range | Description |
|---|---|---|---|
| `min_passage_words` | 50 | 20–200 | Minimum Arabic word count for a passage |
| `target_passage_words_low` | 200 | 50–500 | Lower bound of target passage size |
| `target_passage_words_high` | 800 | 300–3000 | Upper bound of target passage size |
| `hard_max_passage_words` | 2000 | 500–5000 | Absolute maximum before forced splitting |
| `verse_min_passage_words` | 100 | 20–200 | Minimum for verse-format passages |
| `merge_threshold` | 50 | 20–200 | Below this word count, merge with sibling |
| `coherence_threshold` | 0.5 | 0.2–0.9 | Minimum coherence score for quality checks |
| `boundary_distance_threshold` | 0.3 | 0.1–0.7 | Minimum semantic distance for good boundaries |
| `llm_splitting_threshold` | 1000 | 500–2000 | Word count above which LLM-assisted splitting is attempted |
| `cross_edition_overlap_threshold` | 0.8 | 0.5–1.0 | Minimum character overlap for edition correspondence |
| `enable_quality_prediction` | false | true/false | Whether to run §4.B.1 quality prediction |
| `enable_implicit_structure` | true | true/false | Whether to run §4.B.2 for minimal-structure sources |
| `enable_commentary_alignment` | true | true/false | Whether to run §4.B.3 for commentary sources |

**Per-science configuration hooks (Level 3).** SCIENCE.md files may override:
- Passage size parameters (some sciences have characteristically shorter or longer scholarly arguments).
- Format-specific detection patterns (Q&A markers vary by scholarly tradition).
- LLM prompts for implicit structure discovery (science-specific topic boundary indicators).

**Hardcoded vs. configurable.** The self-validation checks (§4.A.10) are hardcoded — they enforce structural invariants that must always hold. The size parameters and quality thresholds are configurable because optimal values depend on the corpus and may need tuning against gold baselines.

---

## 9. Current Implementation State

**Existing code:**
- `engines/passaging/src/scaffold_passage.py` (279 lines): ABD-era scaffolding tool for creating baseline passage folders. This code has zero relevance to the KR passaging engine design. It operates on ABD's directory structure, uses ABD's `book_id` identifiers, and creates manual baselines — none of which apply to KR's automated passaging pipeline. **This file should be replaced entirely.**

**Existing schema:**
- `schemas/passage.json`: ABD-era passage schema. Uses `book_id`, ABD-specific enums (`teaching`/`exercise`/`mixed`/`introduction` for `content_type`), and ABD-era fields. **This schema must be rewritten** to match §3 of this SPEC. Key changes: `book_id` → `source_id` (D-024), `content_type` → `structural_format`, new fields (`text_layers`, `quality_prediction`, `commentary_alignment`), passage_id format change.

**What works today:** Nothing. There is no automated passaging logic. The ABD-era scaffold creates manual baselines that a human fills in. KR's passaging engine is entirely new construction.

**Known gaps between this SPEC and current code:**
- The entire processing pipeline (§4.A.1–§4.A.10) is [NOT YET IMPLEMENTED].
- All format-specific strategies (§4.A.4–§4.A.9) are [NOT YET IMPLEMENTED].
- Cross-page text assembly (§4.A.2) is [NOT YET IMPLEMENTED].
- All transformative capabilities (§4.B.1–§4.B.4) are [NOT YET IMPLEMENTED].
- The passage schema (§3) needs to be created as a new JSON Schema file.

**External tools and libraries:**
- **Sentence embedding model** (for §4.B.1 quality prediction, §4.B.2 implicit structure discovery): `intfloat/multilingual-e5-large` or `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`. Arabic support via multilingual training. **Custom code:** sliding-window coherence computation, boundary quality scoring, threshold-based split decisions.
- **LLM API** (via OpenRouter): Used for semantic splitting (§4.A.4 Step 3), implicit structure discovery (§4.B.2), and quality prediction (§4.B.1). **Custom code:** all prompt engineering, response parsing, boundary placement logic.
- **CAMeL Tools** (`camel_tools`): Arabic text tokenization for word counting. Arabic word tokenization is non-trivial due to clitics and morphological complexity. **Custom code:** passage size evaluation, merge/split decisions.
- No document parsing libraries needed — the engine operates on already-normalized JSON data.

---

## 10. Test Requirements

**What MUST be tested:**

1. **Cross-page text assembly correctness.** Given content units with known text, verify that assembly produces the expected joined text. Test cases: mid-word page break, mid-sentence page break, clean paragraph break, footnote renumbering across pages, layer rebasing across pages. Minimum 10 test cases covering all joining rules.

2. **Prose strategy sizing decisions.** Given division trees with known word counts, verify that merge, direct, and split decisions match expectations. Test cases: division exactly at minimum (50 words), division exactly at soft max (800 words), division just over hard max (2001 words), nested divisions requiring recursive merge, multi-level split with paragraph boundaries. Minimum 15 test cases.

3. **Verse strategy integrity.** Verify that no بيت is ever split across passage boundaries. Test cases: a verse source with 100 verses across divisions, a commentary-on-verse source with interleaved matn/sharh, a verse passage at the boundary between two divisions. Minimum 8 test cases.

4. **Format-specific strategy selection.** Given manifest structural_format values, verify that the correct strategy is selected. Test cases: each format type, mixed format with per-division selection. 7 test cases.

5. **Self-validation.** Verify that self-validation catches: a coverage gap (missing content unit), an overlap (unit in two passages), a size violation, an ordering violation. 4 test cases minimum.

6. **Sentence integrity.** Verify that no passage boundary falls mid-sentence in Arabic text. Test cases: text with only Arabic punctuation, text with mixed Arabic/Latin punctuation, text with no punctuation (requires heuristic sentence detection). Minimum 5 test cases.

**Gold baseline usage.** Gold baselines should be created for:
- One prose source (شرح ابن عقيل or similar intermediate sharh): hand-verified passage boundaries.
- One verse source (ألفية ابن مالك or المنظومة البيقونية): hand-verified verse groupings.
- One Q&A source (from a fatwa collection): hand-verified Q&A pair boundaries.
- One minimal-structure source (a headingless text): hand-verified implicit topic boundaries.

Each gold baseline: the normalized package input, the expected passage stream output, and annotations explaining why each boundary was placed where it is.

**Regression testing.** After any change to passage boundary logic: re-run all gold baselines and verify output matches. After any change to size parameters: re-run size evaluation tests.

**Integration test requirements.** The passaging engine must verify with:
- **Upstream (normalization engine):** Read a normalization engine output and successfully produce passages. Verify that all manifest fields the passaging engine depends on are present. Verify that content unit ordering is correct.
- **Downstream (atomization engine):** The atomization engine can read passage records and access all fields it needs. Verify schema compatibility. Specifically: `passage_text`, `text_layers`, `footnotes`, and `content_flags` are in the format the atomization engine expects.
