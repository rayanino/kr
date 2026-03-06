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
- `content_census` — (§4.B.5 of normalization SPEC) statistical profile of source content. If present, the passaging engine uses it for adaptive strategy selection (§4.B.5 of this SPEC). Fields used: `text_density_profile` (for passage size calibration), `layer_complexity` (for commentary strategy adaptation), `structural_depth` (for division-tree reliability estimation), `footnote_density` (for assembly complexity prediction), `vocabulary_profile.technical_term_density` (for semantic splitting threshold adjustment). If absent, the passaging engine uses default configuration values.
- `tahqiq_topology` — (§4.B.7 of normalization SPEC) manuscript witness network. If present and `has_tahqiq_apparatus` is true, the passaging engine records the variant reading density per division in passage metadata, enabling the excerpting engine to flag passages from high-variant regions for additional scrutiny. If absent, this metadata is simply not emitted.
- `quality_report` — normalization quality summary. The passaging engine uses `overall_confidence` to adjust boundary placement confidence thresholds: when normalization confidence is `low`, the engine lowers its expectations for division tree reliability and more aggressively applies implicit structure discovery (§4.B.2).

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

**Arabic-specific joining example.** Consider two adjacent content units at a page boundary:

Unit 47 ends with: `...وقد ذهب الإمام أحمد بن حنبل رحمه الله إلى أن الم`
Unit 48 begins with: `بتدأ هو الاسم المرفوع العاري عن العوامل اللفظية`

The last character of unit 47 is `م` (a letter) and the first character of unit 48 is `ب` (a letter) — this is a mid-word page break splitting `المبتدأ`. Rule 1 applies: join without separator, producing `...الم` + `بتدأ` → `...المبتدأ هو الاسم المرفوع العاري عن العوامل اللفظية`.

Another example — sentence-boundary page break:

Unit 47 ends with: `...والدليل على ذلك قوله تعالى: ﴿وَأَقِيمُوا الصَّلَاةَ﴾.`
Unit 48 begins with: `وأما المسألة الثانية فقد اختلف العلماء فيها`

The last character of unit 47 is `.` (sentence-terminal punctuation). Rule 4 applies: preserve the original whitespace pattern (newline), producing the two sentences on separate lines.

**Taa marbuta / hamza at page boundaries.** Arabic letters that change form at word boundaries require special attention during cross-page joining. When unit N ends with a standalone `ة` (taa marbuta) or `ء` (hamza) and unit N+1 begins with a space, the word is complete — these are word-final forms. The engine does NOT join them to the next word. This distinguishes mid-word breaks (Rule 1) from word-final characters that merely coincide with page boundaries.

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

**Arabic word count method.** Word counting uses whitespace tokenization on the assembled passage text after stripping footnote reference markers (`⌜N⌝`). Specifically: split the text on Unicode whitespace (`\s+`), filter out empty tokens and tokens that consist entirely of punctuation, count the remaining tokens. This is deliberately simple — Arabic morphological tokenization (via CAMeL Tools or similar) would give a different count (splitting clitics), but whitespace tokenization is standard in the Islamic studies literature (KITAB's passim uses 300-word milestones counted by whitespace) and matches how scholars estimate text length. The passage size parameters are calibrated against whitespace word counts.

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
2. **Scholarly keyword scan.** Within paragraphs, search for topic-transition indicators organized by type:

   - **Ordinal markers (ترقيم):** `أولاً` (firstly), `ثانياً` (secondly), `ثالثاً` (thirdly), `الأول` / `الثاني` / `الثالث` (the first / second / third), `الوجه الأول` (the first aspect).
   - **New-topic markers (انتقال):** `وأما` (as for...), `ومن ذلك` (and among that...), `وأما مسألة` (as for the question of...), `فصل:` (section:) when appearing inline without heading formatting, `ثم إن` (then verily).
   - **Contrastive markers (مقابلة):** `ولكن` (but), `وخالف` (and [he] differed), `واعترض` (and [it was] objected), `ورُدّ بأن` (and it was refuted by...).
   - **Evidence markers (استدلال):** `والدليل على ذلك` (and the evidence for that is), `لقوله تعالى` (due to His — the Exalted's — saying), `لقول النبي ﷺ` (due to the Prophet's ﷺ saying), `واحتج بـ` (and he argued with...), `واستدل بـ` (and he adduced evidence with...).
   - **Position markers (مذاهب):** `وذهب الحنفية إلى` (and the Hanafis held that), `وقال المالكية` (and the Malikis said), `القول الأول` / `القول الثاني` (the first position / the second position), `والراجح` (and the preponderant [view]).

   **Example.** In a prose division of 1,200 words from al-Mughni by Ibn Qudamah, the text might read:
   ```
   ...وقد اختلف العلماء في هذه المسألة على ثلاثة أقوال.
   القول الأول: ذهب الحنابلة والشافعية إلى أن... والدليل على ذلك قوله تعالى...
   القول الثاني: وذهب الحنفية إلى أن... واستدلوا بحديث...
   القول الثالث: وقال المالكية... واحتجوا بأن...
   والراجح: هو القول الأول لقوة دليله...
   ```
   The scholarly keyword scan identifies `القول الأول`, `القول الثاني`, `القول الثالث`, and `والراجح` as sub-topic boundaries. The engine splits between `القول الأول` and `القول الثاني` (approximately 400 words each) if the full division exceeds the hard maximum.

   **Boundary placement rule for keywords.** When a keyword marker is identified as a split point, the boundary is placed BEFORE the keyword (the keyword starts the new passage). The preceding passage ends at the last sentence boundary before the keyword.

3. **LLM-assisted splitting.** For divisions >1000 words where paragraph and keyword scans produce no satisfactory split point, the engine sends the text to an LLM with the prompt: "Identify the natural sub-topic boundaries in this Arabic scholarly text. Return the character offsets where one topic ends and another begins. Do NOT split within an evidence chain (دليل + استدلال), a narration chain (إسناد + متن), or a definition with its explanation." The LLM response provides candidate split points. Each LLM-identified boundary gets `confidence: 0.6–0.8` and generates a `review_flag: "implicit_boundary"`.
4. **Fallback: fixed-interval splitting.** If all else fails (no paragraphs, no keywords, LLM unavailable), split at sentence boundaries (`.` or `؟` or `!` followed by space, at approximately 500-word intervals). `sizing.action: "split"`, `review_flag: "low_confidence_boundary"`.

**Arabic sentence detection specification.** Sentence boundaries in Arabic are identified by the following markers, in priority order:

1. **Terminal punctuation followed by whitespace:** `.` (period), `؟` (Arabic question mark), `!` (exclamation), `؛` (Arabic semicolon when followed by a topic-shift keyword from the scholarly keyword list above). The `،` (Arabic comma) is NOT a sentence terminal — it is a clause separator.
2. **Paragraph breaks:** Double newline patterns are always sentence boundaries.
3. **Quran citation boundaries:** The closing bracket `﴾` of a Quran citation followed by a non-citation sentence is a sentence boundary (the engine does not split within `﴿...﴾` pairs).
4. **Heuristic: long comma-separated spans.** In classical Arabic texts with minimal punctuation, spans exceeding 200 characters between periods may contain multiple logical sentences separated only by `و` (wa/and). The engine does NOT attempt to split these — Arabic scholarly prose is characteristically paratactic (joined by `و`), and splitting at `و` would break more arguments than it preserves. These spans are treated as single long sentences.

**Isnad chain integrity.** In hadith and fiqh texts, isnad chains (narration chains) follow the pattern `حدثنا X عن Y عن Z قال: [matn]` or `أخبرنا X حدثنا Y عن Z أنه قال: [matn]`. An isnad chain plus its matn (narrated text) form an atomic unit. The passaging engine detects isnad openings (`حدثنا`, `أخبرنا`, `أنبأنا`, `عن`, `قال`) and does NOT place a passage boundary between an isnad chain and its matn. If a passage boundary candidate falls within an isnad-matn unit, the boundary is moved to the end of the matn (the next sentence boundary after the matn).

**Split passage identity.** When a division is split into N passages, each passage carries: `division_ids: [original_div_id]`, `heading_text: null` (except the first piece, which carries the original heading), and `sizing: { action: "split", notes: "Split N of M from division {div_id}" }`.

**Sentence integrity rule.** No passage boundary falls mid-sentence. When a boundary calculation lands within a sentence, the boundary moves to the nearest sentence end, using the Arabic sentence detection specification defined above. Sentence detection uses the four-tier priority system: terminal punctuation, paragraph breaks, Quran citation boundaries, and the heuristic for long comma-separated spans. The engine does NOT split within isnad-matn units (see isnad chain integrity rule above).

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

1. **Explicit markers:** `سُئل عن` (he was asked about), `مسألة:` (question:), `سؤال:` (question:), `جواب:` (answer:), `فأجاب` (and he answered), `الجواب:` (the answer:), `قيل له:` (it was said to him:), `فقال:` (and he said:), `وسأله` (and [someone] asked him). The question marker starts a new Q&A pair.
2. **Typographic signals:** If the normalization engine preserved bold or indented formatting (via structural markers), questions may be visually distinguished from answers.
3. **Pattern-based:** A new question marker after an answer section signals a new Q&A pair. Specifically: the sequence `جواب/فأجاب → [answer text] → سُئل/سؤال/مسألة` indicates a pair boundary between the answer text and the next question.

   **Example.** In مجموع الفتاوى by Ibn Taymiyyah:
   ```
   وسُئل رحمه الله تعالى عن رجل يصلي ولا يزكي هل تصح صلاته أم لا؟
   فأجاب: الحمد لله. أما الزكاة فهي أحد أركان الإسلام... [400 words of answer]
   وسُئل أيضاً عن رجل حلف بالطلاق ثلاثاً ثم ندم...
   ```
   The engine detects `وسُئل رحمه الله تعالى عن` as the first Q&A pair opening, `فأجاب:` as the start of the answer, and `وسُئل أيضاً` as the start of the next Q&A pair. The first pair (question + 400-word answer) becomes one passage.

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

2. **Topic shift detection via embeddings.** Using Sentence Transformers (specifically `intfloat/multilingual-e5-large` or `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`), the engine computes a sliding-window topic coherence score across the text. Significant drops in coherence (measured as cosine distance between adjacent sentence windows exceeding a threshold) indicate topic shifts. The threshold is calibrated per genre: sharh texts have more internal coherence variation than matn texts.

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

**Technical approach.** When the source engine's work registry indicates that multiple sources share the same `work_id`, the passaging engine can run a correspondence analysis using Smith-Waterman alignment (the same algorithm used by KITAB's passim tool):

1. **Text similarity matching.** For each passage in the new edition, compute its similarity to all passages in existing editions (using character n-gram overlap, not semantic similarity, because the text SHOULD be nearly identical). Matches with >80% character overlap are considered correspondences.
2. **Division tree alignment.** If both editions have division trees, align them by heading text similarity. Matching headings confirm passage correspondence.
3. **Sequential ordering.** Passages in both editions follow the same author's text in the same order. Sequential alignment (dynamic time warping) resolves cases where passage boundaries differ but content order is preserved.

**Output.** A correspondence record at `library/sources/{source_id}/passages/cross_edition_map.json`: an array of `{ this_passage_id, other_source_id, other_passage_id, overlap_score, alignment_method }`. This enables the excerpting engine to compare how the same text was edited across editions, and the synthesizer to note textual variants.

**Why this is transformative.** Edition comparison is a core activity in Islamic textual criticism (تحقيق). Scholars spend hours comparing different prints of the same work to identify variants, corrections, and editorial additions. KR automates the first step: aligning the editions at passage level so that the comparison can be done systematically. The KITAB project's passim algorithm (see RESOURCES.md) demonstrates that text reuse detection in Arabic is feasible at this scale.

[NOT YET IMPLEMENTED] — Full specification provided. Depends on: multiple editions of the same work in the library (requires the source engine's work registry to track `work_id` relationships). Technical approach: character n-gram matching is straightforward; the KITAB project uses Smith-Waterman alignment on 300-word chunks of Arabic text.

#### §4.B.5 — Content Census-Driven Adaptive Passaging

**Capability:** The normalization engine's content census (§4.B.5 of normalization SPEC) provides a statistical profile of each source: text density distribution, footnote density, layer complexity, structural depth, vocabulary profile, verse ratio, and fidelity distribution. The passaging engine uses this profile to AUTOMATICALLY adapt its strategy and parameters per-source, instead of relying on static configuration defaults. This means two sources with the same `structural_format` may receive different passage size targets, different splitting thresholds, and different quality expectations — because their content profiles are different.

**Technical approach.** When the normalization manifest includes a `content_census`, the passaging engine computes adapted parameters before processing begins:

1. **Passage size calibration from text density.** The content census reports `text_density_profile.mean_chars_per_page` and `vocabulary_profile.technical_term_density`. Sources with high technical term density (>0.15) contain more information per word — their passages should be smaller so each passage is topically focused. Adapted formula:
   - `adapted_target_high = config.target_passage_words_high × (1.0 - technical_term_density × 0.3)`
   - Example: a dense usul al-fiqh text with `technical_term_density: 0.22` gets `adapted_target_high = 800 × (1.0 - 0.22 × 0.3) = 800 × 0.934 = 747 words`, tighter than the default 800.
   - A narrative sira text with `technical_term_density: 0.05` gets `adapted_target_high = 800 × (1.0 - 0.05 × 0.3) = 800 × 0.985 = 788 words`, essentially unchanged.

2. **Splitting threshold from structural depth.** Sources with deep, well-structured division trees (high `structural_depth.division_count`, high `structural_depth.max_depth`) rarely need semantic splitting — their divisions are fine-grained enough. Sources with shallow trees need more aggressive splitting. Adapted formula:
   - If `structural_depth.mean_pages_per_leaf_division > 10`: lower `llm_splitting_threshold` by 20% (these divisions are large and likely need splitting)
   - If `structural_depth.mean_pages_per_leaf_division < 2`: raise `merge_threshold` by 30% (these divisions are small and likely need merging)

3. **Commentary strategy adaptation from layer complexity.** For commentary sources, the content census reports `layer_complexity.transition_density` (layer transitions per page) and `layer_complexity.matn_ratio`. Sources with frequent layer transitions (>3 per page) have fine-grained interleaving — the commentary-unit detection needs tighter sensitivity. Sources with rare transitions (<0.5 per page) have large blocks per layer — the engine can use broader boundary detection.
   - `adapted_commentary_sensitivity = "fine"` if `transition_density > 3.0`, `"normal"` if 0.5–3.0, `"coarse"` if `transition_density < 0.5`

4. **Footnote-aware passage assembly.** The content census reports `footnote_density.mean_footnotes_per_page`. Sources with high footnote density (>5 per page, common in well-edited tahqiq editions) produce passages with many footnotes. The engine adjusts: in high-footnote sources, passage size targets are reduced by 15% to prevent passages from becoming too complex for downstream processing. In low-footnote sources (<1 per page), this adjustment does not apply.

**Output.** Each passage record receives an `adaptive_params` field recording which parameters were adapted and why: `{ text_density_adjustment: float, structural_depth_adjustment: string, commentary_sensitivity: string, footnote_adjustment: float, adaptation_rationale: string }`. This transparency allows debugging and gold baseline calibration.

**Example.** شرح ابن عقيل على الألفية has: `technical_term_density: 0.18`, `structural_depth.mean_pages_per_leaf_division: 3.2`, `layer_complexity.transition_density: 2.1`, `footnote_density.mean_footnotes_per_page: 4.3`. The engine computes: passage size target reduced to ~757 words (from 800), structural splitting at normal thresholds, commentary sensitivity "normal", footnote adjustment -15% → effective target ~643 words. This smaller target produces more focused passages from this dense grammatical commentary — each passage covers one or two verse explanations rather than three or four.

**Why this is transformative.** No existing text segmentation tool adapts its chunking parameters based on statistical analysis of the document being processed. RAG systems use fixed chunk sizes (256, 512, 1024 tokens) regardless of content density. KITAB's passim uses a flat 300-word milestone regardless of text complexity. KR's passaging engine becomes the first system that READS the content profile and ADAPTS its strategy to match — producing optimally-sized passages for every source, from dense fiqh reference works to flowing sira narratives.

[NOT YET IMPLEMENTED] — Full specification provided. Depends on: content census data from the normalization engine (already designed in normalization SPEC §4.B.5). Computation uses NumPy for statistical parameter adaptation. No additional external tools required — adaptation logic is pure computation on census statistics.

#### §4.B.6 — Scholarly Argument Boundary Detection (حفظ حدود الحجج)

**Capability:** Islamic scholarly texts are organized around ARGUMENTS, not just topics. A scholarly argument has a recognizable structure: claim (مسألة/دعوى) → supporting evidence (دليل/حجة) → counter-evidence (اعتراض/نقض) → refutation (جواب/رد) → conclusion (ترجيح/خلاصة). The passaging engine detects these argument structures and ensures that passage boundaries NEVER split a complete argument in half. A passage that contains the claim and evidence but splits before the refutation forces the excerpting engine to produce an incomplete excerpt — the reader learns a position but not its defense.

**Technical approach.** The engine detects argument boundaries using a pattern-based state machine:

1. **Argument opening detection.** An argument begins when the text matches one of:
   - Explicit مسألة markers: `مسألة:`, `فرع:`, `تنبيه:`, `واختلفوا في`, `وقد اختلف العلماء في`
   - Position introduction: `ذهب ... إلى أن`, `القول الأول:`, `وقال ...:`
   - Question formulation: `هل ... أم ...؟`, `ما حكم ...؟`

2. **Argument body tracking.** Once an argument is open, the engine tracks the argumentative flow by detecting:
   - Evidence markers: `والدليل`, `واستدل بـ`, `لقوله تعالى`, `لقول النبي ﷺ`, `لما روى`
   - Counter-evidence markers: `واعتُرض`, `ونوقش`, `وأُجيب عن هذا`, `ولا يصح هذا لأن`
   - Response markers: `والجواب:`, `ورُدّ بأن`, `وأُجيب بأن`
   - Conclusion markers: `والراجح`, `والصحيح`, `والمعتمد`, `فتبين أن`, `فالحاصل`

3. **Argument closure detection.** An argument closes when:
   - A conclusion marker is found (ترجيح/خلاصة), followed by a sentence boundary
   - A new argument opening marker appears (new مسألة after the current one)
   - A structural division boundary is reached

**Boundary protection rule.** When the passaging engine's size-based boundary calculation (§4.A.4 Step 2) would place a boundary inside a detected argument, the engine adjusts:
- If the argument is ≤150% of the hard max: keep the argument intact as one passage, even though it exceeds the normal size target. Flag with `argument_preserved` review flag. The rationale: a slightly oversized passage with a complete argument is better for excerpting than two passages with a split argument.
- If the argument is >150% of the hard max: split at an internal sub-argument boundary (between `القول الأول` block and `القول الثاني` block, or between the evidence section and the response section). Each sub-argument still carries the parent argument's مسألة text in its `heading_text` field, so the excerpting engine knows they belong together.

**Example.** In المغني by Ibn Qudamah, a typical مسألة block reads:
```
مسألة: إذا نوى المسافر الإقامة أربعة أيام أتم.
وهذا قول أكثر أهل العلم. وبه قال مالك والشافعي وأبو حنيفة.
والدليل على ذلك: أن النبي ﷺ أقام بمكة أربعة أيام يقصر الصلاة.
واحتج من قال بخلاف ذلك بحديث: صلاة المسافر ركعتان...
والجواب عن هذا: أن الحديث محمول على من لم ينو الإقامة...
والراجح: قول الجمهور لقوة دليلهم.
```
This is a single argument (~180 words). The engine detects `مسألة:` as the opening, tracks through `والدليل`, `واحتج من قال بخلاف ذلك`, `والجواب عن هذا`, and `والراجح` as the closure. Even if surrounding passages are 400 words and this block would be below the merge threshold, the engine does NOT merge it with the next مسألة — it respects the argument boundary because merging two separate مسائل in one passage would confuse the excerpting engine.

**Output.** Each passage receives an `argument_structure` field when argument detection is active: `{ detected: bool, argument_markers_found: [string], completeness: "complete" | "partial_opening" | "partial_closing", protected_from_split: bool }`. The `completeness` field tells the excerpting engine whether this passage contains a complete argument or whether it was unavoidably split.

**Why this is transformative.** Topic segmentation systems (including all existing RAG chunking tools and KITAB's milestones) segment text by TOPIC shifts — they detect when the subject changes. Argument boundary detection goes deeper: it understands the RHETORICAL structure of scholarly discourse. Two passages might discuss the same topic (e.g., traveler's prayer ruling) but contain different arguments. The passaging engine ensures each argument is self-contained, producing passages that map directly to scholarly reasoning units rather than arbitrary text chunks. This is what enables the excerpting engine to produce excerpts that faithfully represent complete scholarly positions with their evidence — the fundamental building block of the KR entry format (see ENTRY_EXAMPLE.md).

[NOT YET IMPLEMENTED] — Full specification provided. The pattern-based state machine is implemented using Python regex matching on the keyword lists, with optional enhancement via OpenAI or Anthropic LLM APIs for ambiguous cases. Depends on: the scholarly keyword patterns defined in §4.A.4 Step 2 (shared resource).

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
| `PSG_ARGUMENT_OVERSIZED` | Warning | Argument preservation produced passage >150% of hard max | Log. Flag passage with `argument_preserved`. |
| `PSG_ADAPTATION_FAILED` | Info | Content census-driven adaptation computed but produced out-of-range values | Fall back to default parameters. Log adapted values. |
| `PSG_ISNAD_SPLIT` | Warning | An isnad-matn unit was split because it exceeded 3x hard max | Log. Flag both passages. This indicates an unusually long narration chain. |

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
| `enable_adaptive_passaging` | true | true/false | Whether to run §4.B.5 content census adaptation |
| `enable_argument_detection` | true | true/false | Whether to run §4.B.6 argument boundary detection |
| `argument_max_expansion` | 1.5 | 1.1–2.0 | Maximum factor by which argument preservation can exceed hard_max |

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
- All transformative capabilities (§4.B.1–§4.B.6) are [NOT YET IMPLEMENTED].
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

7. **Isnad chain preservation.** Verify that isnad-matn units are never split across passage boundaries. Test cases: a hadith text with short isnad chains (3 narrators + matn), long isnad chains (7+ narrators), nested isnad chains (`حدثنا X قال حدثنا Y` within a larger chain), and isnad that spans a page boundary. Minimum 4 test cases.

8. **Content census-driven adaptation (§4.B.5).** Verify that when content census is present, passage size targets are correctly adapted. Test cases: high technical term density source (should produce smaller passages), low structural depth source (should lower splitting threshold), high footnote density commentary (should reduce targets). Minimum 4 test cases.

9. **Argument boundary detection (§4.B.6).** Verify that scholarly arguments are correctly detected and preserved. Test cases: a standard مسألة block with claim/evidence/counter/response/conclusion; an oversized argument that needs internal splitting at position boundaries; two adjacent مسائل that should NOT be merged even if both are small. Minimum 5 test cases.

**Gold baseline usage.** Gold baselines should be created for:
- One prose source (شرح ابن عقيل or similar intermediate sharh): hand-verified passage boundaries.
- One verse source (ألفية ابن مالك or المنظومة البيقونية): hand-verified verse groupings.
- One Q&A source (from a fatwa collection): hand-verified Q&A pair boundaries.
- One minimal-structure source (a headingless text): hand-verified implicit topic boundaries.
- One masala-block source (المغني or similar): hand-verified argument boundaries showing مسألة opening, evidence chains, and conclusions.

Each gold baseline: the normalized package input, the expected passage stream output, and annotations explaining why each boundary was placed where it is.

**Regression testing.** After any change to passage boundary logic: re-run all gold baselines and verify output matches. After any change to size parameters: re-run size evaluation tests.

**Integration test requirements.** The passaging engine must verify with:
- **Upstream (normalization engine):** Read a normalization engine output and successfully produce passages. Verify that all manifest fields the passaging engine depends on are present. Verify that content unit ordering is correct.
- **Downstream (atomization engine):** The atomization engine can read passage records and access all fields it needs. Verify schema compatibility. Specifically: `passage_text`, `text_layers`, `footnotes`, and `content_flags` are in the format the atomization engine expects.
