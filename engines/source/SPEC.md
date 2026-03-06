# Source Engine — محرك المصادر — Specification

## 1. Purpose and Scope

The source engine is the pipeline entry point. It accepts raw knowledge material from the outside world, establishes the identity model for every source, work, and scholar in the library, captures and infers the metadata that fuels every downstream engine, freezes original files for integrity, and maintains the registries that prevent duplication and track relationships.

**What this engine does:**
- Accepts source material through manual and autonomous acquisition paths
- Assigns canonical identifiers to sources, works, and scholars
- Extracts, infers, and validates source metadata
- Freezes raw source files with cryptographic integrity hashes
- Detects duplicates across acquisition paths and repositories
- Classifies source trustworthiness for default verified/flagged status
- Tracks work-to-work relationships (sharh→matn, mukhtasar→original, etc.)
- Creates and enriches scholar authority records
- Classifies source structural format, authority level, multi-layer composition, and science scope
- Produces the source metadata record consumed by the normalization engine and (through the pipeline) by every engine down to the synthesizer

**What is NOT this engine's responsibility:**
- Format-specific content parsing — that is the normalization engine's job. The source engine examines sources only enough to extract metadata, not to parse their full content.
- Structure discovery within source text (heading hierarchy, chapter divisions) — normalization engine.
- Passage segmentation, atomization, excerpting, placement, synthesis — all downstream engines.
- Scholar interface presentation of book briefings — the scholar interface assembles briefings from source metadata; the source engine provides the raw data.
- Science tree management — taxonomy engine.

**Phase classification:** Phase 1 (source-format-specific, above the normalization boundary).

**Normalization boundary relationship:** The source engine sits entirely above the normalization boundary. Its output (frozen source files + source metadata record) is consumed by the normalization engine, which is the only other Phase 1 engine. The source metadata record also flows downstream through the entire pipeline as metadata attached to the normalized package, passages, atoms, excerpts, and entries — no engine in the chain may strip metadata fields because the synthesizing engine is the ultimate consumer (D-023).

**User scenarios served:**
- **Scenario 1 (Day 1):** Source engine has already ingested the seed collection; its metadata enables the scholar interface to present the curriculum.
- **Scenario 2 (Day 30):** Autonomous discovery finds a new Shamela copy; source engine acquires it, identifies the work and author, detects it's a new source for an existing work, creates metadata.
- **Scenario 4 (Day 365):** Gap detection reveals missing Zahiri source → source engine searches repositories, presents candidate to owner.
- **Scenario 6 (New Book Briefing):** Owner uploads iPhone photos → source engine processes them, extracts/infers metadata, produces the structured record from which the scholar interface assembles the briefing.
- **Scenario 8 (Correction):** A correction may trace back to wrong source metadata (author misidentification, wrong genre classification) → source engine updates the record, triggering downstream reprocessing.

---

## 2. Input Contract

The source engine receives input from two paths.

**Manual acquisition.** The owner provides source material through the manual input interface. Manual input arrives as one of:

1. **Structured digital files.** A file or directory the owner places in the intake staging area. Supported file types: Shamela HTML export (single `.htm` file or numbered directory of `.htm` files), PDF (text-embedded or scanned), Word document (`.doc` or `.docx`), EPUB, plain text. The owner provides: the file(s), and optionally: a suggested book ID, edition notes, science scope hint, and any metadata hints (author name, work title, genre). Unrecognized file types are rejected with error `SRC_UNSUPPORTED_FORMAT` and a suggestion to convert or provide in a supported format.

2. **Photographic scans.** iPhone camera photos or other image files (JPEG, PNG, TIFF, HEIC) of physical book pages. These arrive as a directory of images representing sequential pages. The owner provides: the images, and required: the work title and author name (these cannot be reliably auto-extracted from photos alone). Optional: page number range, volume number, edition notes.

3. **Owner-authored content.** Text the owner writes directly: study notes, tarjih conclusions, research drafts, lesson transcriptions. These arrive as text files or structured input through the scholar interface. The owner provides: the text, an input type identifier (one of: `study_note`, `tarjih`, `research_draft`, `lesson_transcription`, `observation`), and optional metadata hints (related science, related taxonomy leaf, related source).

For all manual input: the source engine validates that the provided material is non-empty. Empty files are rejected with error `SRC_EMPTY_INPUT`. The source engine validates that the file type is recognized. If a required field is missing (e.g., author name for photographic scans), the source engine creates a human gate checkpoint requesting the information rather than rejecting outright — partial intake is always preferred over no intake.

**Autonomous discovery.** The source engine queries configured source repository modules for candidate sources. Each repository module returns candidate sources as structured search results: title, author (if available), repository identifier, a download handle, and any repository-specific metadata. The source engine does not access repositories directly — it delegates to repository interface modules that encapsulate connection, authentication, rate-limiting, and search logic. Adding a new repository requires only a new repository interface module; no source engine core logic changes.

Autonomous discovery is triggered by: (1) periodic scheduled scans of configured repositories, (2) gap-fill requests from the taxonomy engine or scholar interface ("the library needs a Maliki source on topic X"), (3) citation discovery from the excerpting engine ("this excerpt references al-Mughni — is it in the library?"). All autonomous discoveries pass through relevance evaluation (§4.A.6) before acquisition.

**Validation on input.** For manual structured files: the file must exist, be non-empty, and have a recognized extension. For manual photos: at least one image file must be present, and work title + author name must be provided or obtainable through a human gate prompt. For owner-authored content: the text payload must be non-empty and the input type must be one of the five recognized types. For autonomous discovery: the repository module must return a non-empty title and a valid download handle; candidates with empty titles are logged as warnings and skipped.

**Enrichment write-back input.** Downstream engines may write metadata enrichments back to source records. These arrive as structured update requests specifying: the source_id to update, the field(s) to update, the new value(s), and the engine that produced the enrichment. The source engine validates that the source_id exists and that the update does not violate any invariant (e.g., changing a frozen source hash). Invalid updates are rejected with error `SRC_INVALID_ENRICHMENT`.

---

## 3. Output Contract

The source engine produces two primary artifacts per acquired source, plus updates to three shared registries.

**Primary artifacts:**

1. **Frozen source file(s).** The raw source material, copied to `library/sources/{source_id}/frozen/` and set read-only. A SHA-256 hash is computed at freeze time and stored in the source metadata record. No component of the application — including the source engine during later enrichment — may modify frozen files. For multi-file sources (multi-volume directories, photo sets), each file is individually hashed and the composite hash is recorded.

2. **Source metadata record.** A structured JSON file written to `library/sources/{source_id}/metadata.json`, conforming to the source metadata schema. This record contains everything known about the source at intake time plus a mechanism for progressive enrichment. The required fields are specified throughout §3 (output guarantees) and §4.A.4 (inferred fields). The actual JSON schema file will be generated from these requirements during implementation.

**Guarantees about the metadata record:**
- Every required field has a non-null value. Optional fields may be null, but null is explicitly recorded (not absent).
- The `source_id` is globally unique across the library.
- The `work_id` correctly groups this source with other sources of the same abstract work (if any exist).
- The `author.canonical_id` links to a valid record in the scholar authority registry.
- The `trust_tier` reflects a conscious evaluation (not a default). If the evaluation is uncertain, `trust_tier` is `"flagged"` with a reason.
- The `text_fidelity` field reflects the quality of the text data, separate from scholarly trustworthiness.
- All metadata fields present at intake are preserved through enrichment — enrichment may add or update fields but never removes existing data. Overwritten values are preserved in `metadata_history`.

**Metadata pass-through (D-023):** The source metadata record is the origin point for the metadata chain that flows through the entire pipeline. The normalization engine embeds a reference to `source_id` in the normalized package. Every downstream engine can access the full source metadata record via this reference. The source engine adds the following metadata that downstream engines and the synthesizer consume:

- Author identity (canonical_id, biographical data, school affiliations, teachers, students)
- Work classification (genre, genre chain relationships, science scope, level, structural format)
- Edition quality (tahqiq editor, publisher, trustworthiness, text fidelity)
- Work relationships (sharh_of, mukhtasar_of, hashiyah_on, nazm_of — linking to other work_ids)
- Multi-layer composition (which text layers are present, who authored each layer)
- Source authority level (primary, reference, modern_compilation)

No metadata field in this list is "just for documentation" — each has a specific consumer in a downstream engine or the synthesizer. The ENTRY_EXAMPLE.md demonstrates how author death dates, teacher-student chains, school affiliations, and work genres transform flat compilations into scholarly narratives.

**Shared registry updates:**

3. **Source registry** (`library/registries/sources.json`). A catalog of all acquired sources with their source_id, work_id, title, author canonical_id, trust tier, processing status, and deduplication hashes. Used for duplicate detection, source lookup, and status tracking. Updated atomically on each acquisition.

4. **Work registry** (`library/registries/works.json`). A catalog of all known works with their work_id, canonical title, author canonical_id, genre, science scope, and the list of source_ids that are manifestations of this work. Includes the owner's preferred_source_id per work. Updated when a new source is linked to a work or when a new work is created.

5. **Scholar authority registry** (`library/registries/scholars.json`). The centralized record of every scholar encountered across all sources. Updated when the source engine creates or enriches a scholar record during intake. The structure and semantics of scholar authority records are defined in §4.A.5. This registry is a shared resource read by multiple engines — the source engine is the primary writer, the excerpting engine adds quoted-scholar references, and the synthesizing engine is the primary reader.

---

## 4. Processing Specification

### §4.A — Core Processing

#### §4.A.1 — Source Identity Model

The source identity model has three tiers: sources, works, and scholars.

**Source identity.** Every acquired source receives a `source_id` at registration time. The source_id is a permanent, globally unique identifier formatted as `src_{8_char_hash}` where the hash is derived from the frozen source's composite SHA-256 hash (first 8 hex characters). If a collision occurs (astronomically unlikely but handled), append a numeric suffix: `src_{hash}_2`. The source_id is assigned at freeze time and never changes.

The ABD-era `book_id` (user-assigned ASCII slug like `ibn_aqil`) is preserved as `human_label` — a human-readable shorthand for use in logs, CLI output, and owner-facing displays. The `human_label` is not a primary key and need not be unique across the library (though the source engine warns if a duplicate is detected). The `human_label` is assigned at intake: if the owner provides one, it is used; otherwise, the source engine generates one from the work title's distinctive words (transliterated, lowercased, underscored).

**Work identity.** A work (مؤلَّف) is the abstract intellectual creation — the book as a scholarly contribution, independent of any particular edition or format. "al-Mughni by Ibn Qudamah" is a work. Each work receives a `work_id` formatted as `wrk_{author_slug}_{title_slug}` where the slugs are derived from the canonical author name and canonical work title (transliterated, lowercased, underscored, max 40 characters total). Example: `wrk_ibn_qudamah_mughni`.

The same work may have multiple sources in the library: different tahqiq editions, different digital formats, different repository origins. All share the same `work_id`. A new source triggers work matching: the source engine checks whether a work record already exists for this author+title combination. Matching uses normalized title comparison (stripping definite articles, normalizing hamza/taa marbuta) and author canonical_id matching. If a match is found with confidence ≥ 0.85, the source is linked to the existing work. If confidence is between 0.50 and 0.85, a human gate checkpoint is created presenting the candidate match for owner confirmation. If confidence < 0.50, a new work record is created.

The work record tracks: the owner's preferred source for this work (`preferred_source_id`), which defaults to the first source acquired and can be changed by the owner. The preferred source is the one from which excerpts are primarily drawn; other sources serve as cross-references for variant readings and alternative commentary.

**Multi-volume works.** A multi-volume work (e.g., al-Mughni's 15 volumes) is ONE work with ONE `work_id`. Each volume may be a separate source (separate `source_id`) if acquired as separate files, or a single source if acquired as one package. The source metadata record includes a `volumes` field listing volume numbers and their file mappings. The work registry tracks which volumes are present and which are missing, enabling gap detection ("you have volumes 1-12 and 14 of al-Mughni — volume 13 and 15 are missing").

**Scholar identity.** Every author, editor (muhaqiq), and quoted scholar receives a canonical identity in the scholar authority registry. The scholar identity model is detailed in §4.A.5.

#### §4.A.2 — Acquisition Workflow

The acquisition workflow is intentionally minimal for v1 (D-020). The source engine accepts files the owner provides and performs basic automated discovery. Elaborate multi-repository crawling, format expansion, and proactive acquisition are designed but marked [NOT YET IMPLEMENTED].

**Step 1: Staging.** Source material arrives in the intake staging area (`library/staging/`). For manual acquisition, the owner places files there (or the scholar interface moves uploaded files there). For autonomous discovery, the repository module downloads to staging.

**Step 2: Format detection.** The source engine examines the staged material and determines its source type. Detection is based on file extension, content inspection (HTML structure for Shamela, PDF magic bytes, image EXIF headers), and directory structure (numbered `.htm` files → Shamela multi-volume). The detected source type determines which normalizer will later process it. If the format is unrecognized, the source is rejected with `SRC_UNSUPPORTED_FORMAT`.

**Step 3: Metadata extraction.** The source engine extracts metadata from the source material using format-specific extractors (§4.A.3). This is the only place in the source engine where format-specific logic exists — the extractors are modular, one per source type, analogous to normalizers.

**Step 4: Metadata inference.** The source engine uses LLM-assisted inference to fill metadata gaps and enrich the extracted data (§4.A.4). This step transforms sparse, format-specific metadata into the rich, structured record the pipeline needs.

**Step 5: Duplicate detection.** The source engine checks the source registry for duplicates using the deduplication criteria in §4.A.7.

**Step 6: Freezing.** The raw source files are copied to `library/sources/{source_id}/frozen/`, set read-only, and SHA-256 hashed. From this point, the frozen files are immutable.

**Step 7: Registration.** The source metadata record is written to `library/sources/{source_id}/metadata.json`. The source registry, work registry, and scholar authority registry are updated.

**Step 8: Trustworthiness evaluation.** The source engine assesses the source's reliability and assigns a trust tier (§4.A.8).

**Step 9: Handoff.** The source is marked as `status: "acquired"` and is available for the normalization engine to process. The normalization engine picks up sources with this status.

#### §4.A.3 — Format-Specific Metadata Extraction

Each source type has a metadata extractor — a module that knows how to pull metadata from that format's specific conventions. Extractors are kept minimal: they extract what the format provides, then hand off to the LLM inference step (§4.A.4) for enrichment.

**Shamela HTML extractor.** Parses the metadata card from the first `PageText` div. Extracts: title (from `<h1>` or title span), author (from المؤلف field), publisher, edition, page count (from `PageNumber` span count), volume structure (from numbered file stems). Shamela-specific fields (shamela_book_id, shamela_category) are preserved as `format_specific_metadata` — they are consumed only by the Shamela normalizer and do not enter the pipeline-wide metadata schema.

**PDF extractor.** Extracts document metadata from PDF properties (title, author, creation date). For scanned PDFs, performs limited OCR on the title page (first 1-3 pages) to extract title, author, publisher information. Uses Docling (see RESOURCES.md) for PDF parsing. Page count from PDF page count. For text-embedded PDFs, extracts table of contents if structured bookmarks exist.

**Image extractor.** For photographic scans: performs OCR on the first image (assumed to be title page or cover) to extract title and author. Uses Google Document AI or Docling for Arabic OCR. If OCR confidence is below 0.70 on critical fields (title, author), creates a human gate checkpoint requesting manual entry. Image count serves as page count.

**Plain text / EPUB extractor.** Minimal extraction: title from filename or first line, page count from character/word count estimation. Most metadata will come from LLM inference and owner input.

**Word document extractor.** For `.doc` and `.docx` files: uses Docling (see RESOURCES.md) to extract text and metadata. Document properties (title, author, creation date) are extracted from Word metadata fields. For collections of Word files in a directory (e.g., one file per chapter), the source engine treats the directory as a single multi-part source, ordering files by filename. Encoding detection is critical: Arabic filenames in ZIP archives often use CP1256 encoding (as seen in the mughni_comparative fixture). The extractor normalizes filenames to UTF-8 and preserves the original filename in metadata.

**Owner-authored content extractor.** No format-specific extraction needed — the owner provides the metadata directly through the input interface. The extractor validates the input type and captures any metadata hints.

#### §4.A.4 — LLM-Assisted Metadata Inference

After format-specific extraction produces a sparse metadata record, the source engine uses LLM inference to fill gaps, validate extracted data, and enrich the record with scholarly context. This is the step that transforms raw bibliographic data into the rich metadata that fuels synthesis.

**The inference prompt** receives: the extracted metadata (title, author name, any available fields), the first 2000 characters of source text (if available from format-specific extraction), the table of contents (if available), and the library's current state (existing works, existing scholar records for potential matches).

**The LLM infers the following fields when not already present:**

*Work classification:*
- `genre`: one of `matn`, `sharh`, `hashiyah`, `mukhtasar`, `nazm`, `risalah`, `taqrirat`, `mawsuah` (encyclopedia), `fatawa` (fatwa collection), `mu'jam` (dictionary), `tabaqat` (biographical dictionary), `other`. Inferred from title conventions (titles containing "شرح" → sharh, "مختصر" → mukhtasar, "حاشية" → hashiyah, etc.) and content inspection.
- `genre_chain`: if the work is a sharh, hashiyah, mukhtasar, or nazm, the LLM identifies the base work. Example: from title "شرح ابن عقيل على ألفية ابن مالك", infer: `{ "type": "sharh", "base_work_title": "ألفية ابن مالك", "base_work_author": "ابن مالك" }`. This creates a work relationship record (§4.A.9).
- `structural_format`: one of `prose`, `verse`, `qa_format`, `tabular_khilaf`, `dictionary`, `commentary`, `mixed`. Inferred from genre and content inspection.
- `multi_layer`: boolean. True if the work contains text from multiple authors (sharh quoting matn, hashiyah quoting sharh). When true, `layers` is populated with the author and type of each layer.
- `source_authority`: one of `primary`, `reference`, `modern_compilation`. Inferred from author period (pre-modern → likely primary or reference; modern → likely compilation) and genre (mawsuah → reference; matn/sharh → primary).

*Science scope:*
- `science_scope`: array of science identifiers. Inferred from title, author's known specializations, genre conventions (a sharh of a nahw matn → nahw), and content inspection.
- `level`: one of `beginner`, `intermediate`, `advanced`, `specialist`. Inferred from genre (matn → often beginner, sharh → intermediate/advanced, hashiyah → specialist) and the work's position in scholarly chains.

*Author identification:*
- The LLM resolves the author name to a canonical scholar identity. If the author is already in the scholar authority registry, the LLM matches by comparing: full name, known_as names, death date, school affiliations, known works. If no match is found, the LLM creates a new scholar record with whatever biographical data it can infer from the title page and its training knowledge.
- Author disambiguation: when the name is ambiguous (e.g., "ابن حجر" could be al-Asqalani or al-Haytami), the LLM uses context clues — science scope, genre, other metadata — to disambiguate. If disambiguation confidence < 0.80, a human gate checkpoint is created.

*Edition-specific fields:*
- `text_fidelity`: one of `high`, `medium`, `low`, `unknown`. Determined by source type: Shamela structured text → `high`. Text-embedded PDF → `high`. Professionally scanned PDF → `medium`. iPhone photos → `low`. Unknown provenance → `unknown`.
- `tahqiq_quality_estimate`: a qualitative assessment (when muhaqiq is known — the LLM checks if the muhaqiq is a recognized scholar with a reputation for rigorous tahqiq).

**Confidence scoring.** Every inferred field carries a confidence score between 0.0 and 1.0. Fields with confidence < 0.70 are flagged as `needs_review` in the metadata record. The human gate (§5) presents flagged fields to the owner for verification. Fields with confidence ≥ 0.70 are accepted provisionally — they can still be corrected later through enrichment.

**Multi-model consensus for critical fields.** Author identification and work matching — the two fields with the highest cascade risk if wrong — use multi-model consensus (§6). Two LLMs independently process the inference prompt. If they agree on author canonical_id and work_id, the result is accepted. If they disagree, a human gate checkpoint is created.

#### §4.A.5 — Scholar Authority Model

The scholar authority registry (`library/registries/scholars.json`) is a shared knowledge graph of every scholar encountered in the library. The source engine is the primary creator of records; other engines enrich them.

**Scholar record structure:**

```
{
  "canonical_id": "sch_{5_digit_sequence}",  // e.g., "sch_00001"
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
  "teachers": ["sch_00002"],  // al-Khalil ibn Ahmad
  "students": ["sch_00003"],  // al-Akhfash al-Awsat
  "known_works": ["wrk_sibawayhi_kitab"],
  "scholarly_standing": "founder of systematic Arabic grammar",
  "methodology_notes": null,
  "sources_encountered_in": ["src_a1b2c3d4"],
  "record_completeness": 0.85,  // how many fields are filled
  "record_sources": ["auto_inference", "openiti_metadata"],
  "last_updated": "2026-03-04T12:00:00Z"
}
```

**Record creation.** When the source engine processes a new source and identifies an author not already in the registry, it creates a new scholar record. The record is initially populated from: (1) metadata extracted from the source (author name, any biographical info on title page/introduction), (2) LLM inference from its training knowledge (death dates, school affiliations, teachers, students, known works, scholarly standing), (3) external enrichment sources when available (OpenITI author metadata, see §4.B.1).

**Record matching.** When the source engine encounters an author name that might match an existing record, it performs matching using: normalized name comparison (stripping diacritics, normalizing hamza/taa marbuta, comparing against all `name_variants`), death date comparison (if available), school affiliation comparison, and known works comparison. A match score ≥ 0.85 auto-links; 0.50–0.85 creates a human gate checkpoint; < 0.50 creates a new record.

**Progressive enrichment.** When the 50th source mentioning a scholar is processed, the source engine checks whether the new source provides information the existing record lacks (a teacher, a work, a corrected date). If so, the record is updated. Overwritten values are preserved in a `revision_history` array. This means scholar records become increasingly rich as the library grows — an early record with just a name and death date gains teachers, students, works, methodology notes, and standing assessments over time.

**Muhaqiq (editor) records.** Tahqiq editors are scholars in their own right. Each muhaqiq encountered gets a scholar authority record with the same structure. The source metadata links to both the original author's canonical_id and the muhaqiq's canonical_id.

**Disambiguation handling.** The most critical disambiguation case is when two different scholars share a commonly used name. The registry maintains a `disambiguation_notes` field per scholar: "When 'ابن حجر' appears in hadith context → likely sch_00042 (al-Asqalani d.852). When 'ابن حجر' appears in Shafi'i fiqh context → likely sch_00089 (al-Haytami d.974)." The excerpting engine uses these notes when it encounters scholar references in text.

#### §4.A.6 — Relevance Evaluation

During autonomous discovery, the source engine evaluates whether a candidate source is relevant to the library's knowledge scope.

**Evaluation method.** The source engine extracts the candidate's title, author, and any available metadata from the repository module's search results. It sends these to the LLM with: the library's current science inventory (which sciences are covered), the library's coverage map (which topics have thin coverage), and the owner's current study focus (from the user model).

**Relevance classification:**
- `relevant`: the source covers one or more of the library's sciences and adds knowledge not already well-covered. Action: proceed to acquisition.
- `partially_relevant`: the source touches the library's sciences but most of its content is outside scope (e.g., a history book with occasional fiqh discussions). Action: flag for owner decision.
- `not_relevant`: the source is outside the library's knowledge scope entirely. Action: skip, log for future reference.

**Gap-fill relevance.** When relevance evaluation is triggered by a gap-fill request (e.g., "find a Maliki source on topic X"), the evaluation additionally checks whether the candidate specifically addresses the gap. A source that is generally relevant to the science but doesn't cover the specific topic is classified as `partially_relevant`.

#### §4.A.7 — Deduplication

The source engine maintains deduplication at two levels: source-level (exact duplicate) and work-level (same work, different edition).

**Source-level deduplication.** Two sources are exact duplicates when their frozen file SHA-256 hashes match (for single-file sources) or when all individual file hashes match in the same order (for multi-file sources). When an exact duplicate is detected:
- If the duplicate is from a different repository: the new repository is recorded as an alternative availability in the existing source's metadata, and the duplicate is not acquired. Log: `SRC_DUPLICATE_EXACT`.
- If the owner forces re-acquisition (e.g., re-downloading after a corruption fix): the force flag bypasses deduplication.

**Work-level matching.** Two sources are editions of the same work when they share the same abstract author + title but differ in tahqiq, publisher, edition number, or format. This is NOT a duplicate — both sources are acquired and linked to the same `work_id`. The source engine detects this through work matching (§4.A.1) and records the relationship. The owner is notified: "This appears to be a different edition of {work_title}, which you already have as {existing_source_id}. Acquiring as a new source of the same work."

**Near-duplicate detection.** [NOT YET IMPLEMENTED] Two sources from different repositories may be the same content with minor differences (OCR artifacts, formatting differences). Detection would use text similarity on the first N pages. For v1, this is deferred — the owner is expected to recognize obvious duplicates.

#### §4.A.8 — Trustworthiness Evaluation

The source engine assesses each source's reliability to determine the default verified/flagged classification for its excerpts.

**Evaluation factors** (weighted by importance):

1. **Author scholarly standing** (weight: 0.30). Is the author a recognized scholar in the relevant science? Major classical scholars (those in the scholar authority registry with high `scholarly_standing`) increase trust. Unknown or contemporary popular authors decrease it.

2. **Tahqiq quality** (weight: 0.25). Is the muhaqiq a recognized editor? Major muhaqiqs (Shu'ayb al-Arna'ut, Ahmad Shakir, Abdul Salam Harun, etc.) significantly increase trust. No tahqiq or unknown muhaqiq is neutral (many classical works were published without modern tahqiq and are still scholarly).

3. **Publisher reputation** (weight: 0.15). Known scholarly publishers (Dar al-Risalah, Mu'assasat al-Risalah, Dar al-Kutub al-'Ilmiyyah for specific titles) increase trust. Unknown publishers are neutral. Publishers known for low-quality commercial prints decrease trust.

4. **Source authority level** (weight: 0.15). Primary sources (مصدر أصلي) receive higher baseline trust than modern compilations (معاصر). Reference works (مراجع) are neutral.

5. **Text fidelity** (weight: 0.15). High-fidelity sources (structured digital text) increase trust. Low-fidelity sources (poor OCR, iPhone photos) decrease trust — not because the scholarly content is unreliable, but because transcription errors may corrupt the text.

**Trust tiers:**
- `verified`: combined score ≥ 0.65. Excerpts default to verified knowledge.
- `flagged`: combined score < 0.65, or any individual factor is critically low (e.g., unknown author with no muhaqiq and unknown publisher). Excerpts default to flagged knowledge. The flag reason is recorded.
- `owner_override`: the owner has manually set the trust tier, overriding the engine's evaluation. The original evaluation is preserved in metadata.

**Conservative bias (§7.4).** When the evaluation is genuinely uncertain (e.g., a recognized author but unknown publisher and no muhaqiq), the source is flagged. Flagging a reliable source is correctable; verifying an unreliable source contaminates the library.

**Special cases:**
- Owner-authored content is always `verified` — the owner is a trusted source. However, intelligent validation still checks for detectable errors (attribution conflicts with established content).
- Quran text from canonical digital sources is always `verified` with maximum trust.
- Hadith collections from standard editions (Bukhari, Muslim, etc.) are always `verified` when from recognized tahqiq editions.

#### §4.A.9 — Work Relationship Tracking

The source engine maintains a graph of work-to-work relationships. These relationships are critical for the synthesizer's ability to trace scholarly chains and for the scholar interface's book briefing product.

**Relationship types:**
- `sharh_of(work_a, work_b)`: work_a is a commentary on work_b (the matn).
- `hashiyah_on(work_a, work_b)`: work_a is a marginal commentary on work_b (the sharh).
- `mukhtasar_of(work_a, work_b)`: work_a is an abridgment of work_b.
- `nazm_of(work_a, work_b)`: work_a is a versified summary of work_b.
- `taqrirat_on(work_a, work_b)`: work_a contains lecture notes on work_b.
- `cites(work_a, work_b)`: work_a references work_b (discovered during processing).
- `responds_to(work_a, work_b)`: work_a was written in response to or as a refutation of work_b.

**Relationship discovery.** Relationships are discovered at intake through LLM inference from the title and genre classification. A title like "شرح ابن عقيل على ألفية ابن مالك" explicitly declares a sharh_of relationship. The LLM identifies the base work and attempts to link it to an existing work_id in the work registry. If the base work is not in the library, a placeholder work record is created with `status: "referenced_not_acquired"` — it exists in the registry as a known work but has no source. This enables the citation network to grow even before all referenced works are acquired.

**Graph storage.** Relationships are stored in the work registry as edges: `{ "from": "wrk_...", "to": "wrk_...", "type": "sharh_of", "confidence": 0.95, "discovered_by": "source_engine" }`. The graph is queryable: "give me all commentaries on al-Ajurrumiyyah" returns a list of work_ids.

#### §4.A.10 — Processing Status Tracking

Each source has a processing status that tracks its progress through the pipeline:

- `staging`: material is in the staging area, not yet processed.
- `acquired`: source engine has completed intake. Frozen files exist. Metadata record exists. Ready for normalization.
- `normalizing`: normalization engine is processing this source.
- `normalized`: normalization complete. Normalized package exists. Ready for passaging.
- `processing`: downstream Phase 2 engines are working on this source.
- `complete`: all engines have processed this source. Excerpts are placed. Entries generated.
- `error`: processing failed at some stage. The `error_detail` field specifies where and why.
- `withdrawn`: source removed from active processing (owner decision or trust evaluation change). Frozen files and metadata preserved for audit.

Status transitions are logged with timestamps. The source engine owns `staging` → `acquired`. Other engines update status as they process. The source registry provides a dashboard view: how many sources are at each stage, which are blocked, what errors exist.

### §4.B — Transformative Capabilities

#### §4.B.1 — External Metadata Enrichment via OpenITI Corpus

**Capability:** When the source engine identifies a work during intake, it queries the OpenITI corpus metadata to enrich the scholar authority record and work record with data from the largest machine-actionable corpus of premodern Islamicate texts.

**Technical approach:** OpenITI organizes texts using CTS-compliant URIs that encode author death date and author/work slugs (e.g., `0505Ghazali.IhyaCulumDin`). The source engine maintains a local copy of the OpenITI metadata CSV (available from their GitHub releases) and queries it during intake. Matching uses normalized author name + approximate death date. When a match is found, the source engine extracts: confirmed death date, the set of other known works by this author in OpenITI, and any annotated metadata from the OpenITI YML files.

**What this enables:** A scholar authority record initially populated only from a title page ("الغزالي") is immediately enriched with: death date (505 AH), the full list of known works (Ihya, Tahafut, Mustasfa, etc.), and the CTS URIs that link to the OpenITI corpus. This bootstrapping means the synthesizer has rich biographical data from the very first source, not just after dozens of sources have been processed.

**Integration:** The enrichment is recorded as `record_source: "openiti_metadata"` in the scholar authority record. OpenITI data does not override owner-provided or source-extracted data — it supplements. Conflicts are flagged for owner review.

**Dependencies:** Requires downloading and locally caching the OpenITI metadata CSV (~50MB). The KITAB corpus metadata search application provides the data. Update frequency: quarterly, matching OpenITI's release cycle.

#### §4.B.2 — Bibliographic Intelligence from Minimal Input

**Capability:** Given only a title and author name — or even just a photograph of a title page — the source engine produces a comprehensive scholarly profile of the work and author that approaches what a human bibliographer would produce after hours of research.

**Technical approach:** The source engine sends the extracted title + author + any available metadata to an LLM with a specialized bibliographic prompt that instructs the model to: identify the work in the Islamic scholarly tradition, determine its genre and genre chain (is it a commentary on something? an abridgment?), identify the author with biographical details, assess the work's scholarly standing and its place in the classical curriculum, identify what sciences it covers and at what level, and determine known editions and their relative quality.

The LLM's training data includes substantial knowledge of the Islamic scholarly corpus — major works, major scholars, genre relationships, and curricular traditions are well-represented. This inference is not guesswork: for well-known works (which constitute the majority of what the owner will acquire first), the LLM produces highly accurate bibliographic profiles.

**What this enables:** Scenario 6 (New Book Briefing) becomes possible from intake alone. When the owner photographs حاشية ابن عابدين's title page, the source engine — before any content processing — can produce: "This is رد المحتار على الدر المختار, a hashiyah on الدر المختار (sharh of تنوير الأبصار). Author: ابن عابدين (d. 1252 AH). Hanafi fiqh. Advanced specialist level. The primary reference work of late Hanafi scholarship." This profile is stored as source metadata and serves as the foundation for the scholar interface's full book briefing.

**Confidence and verification:** The bibliographic profile carries per-field confidence scores. For well-known works and scholars, confidence is typically > 0.90. For obscure works or ambiguous authors, confidence drops and a human gate checkpoint is created. Multi-model consensus is used for author identification (the field with highest cascade risk).

**Limitations:** LLM training knowledge is not exhaustive. Very obscure works, regional scholars not widely discussed in available training data, and recently published contemporary works may have low-confidence or inaccurate profiles. The system is designed to be honest about uncertainty — a low-confidence field is flagged, not guessed at.

#### §4.B.3 — Citation Network Discovery

**Capability:** When the source engine processes a new source and downstream engines (particularly the excerpting engine) identify textual references to other works, the source engine receives discovery requests and builds a citation graph across the entire library — including references to works not yet acquired.

**Technical approach:** The excerpting engine, during its processing, detects patterns like "قال ابن قدامة في المغني" (Ibn Qudamah said in al-Mughni) or "ذكر في المغني" (it was mentioned in al-Mughni). It sends a citation discovery request to the source engine containing: the referenced author name (normalized), the referenced work title (normalized), and the citing excerpt ID.

The source engine queries the work registry for a match. Three outcomes:
1. **Work exists in library:** Record the citation relationship (`cites(citing_work, cited_work)`) and link the citing excerpt to the cited work_id.
2. **Work exists as a placeholder** (previously referenced but not acquired): Add another citation to the existing placeholder. The citation count on placeholder works serves as an acquisition priority signal — a work cited by 50 excerpts across 10 sources is more important to acquire than one cited once.
3. **Work is new:** Create a placeholder work record with `status: "referenced_not_acquired"`. If autonomous discovery is enabled, trigger a search in configured repositories with priority `citation_discovered`.

**What this enables:** Over time, the library develops a citation graph that reveals: which works are most influential (most cited), which scholarly conversations span multiple works (mutual citation chains), and which unacquired works would most enrich the library (highest citation count among placeholders). The scholar interface can show: "al-Mughni is cited by 47 excerpts across 12 sources in your library — it's the most-referenced unacquired work. Shall I find it?"

[NOT YET IMPLEMENTED] — Full specification provided above. Depends on: excerpting engine's reference detection capability and repository search interface modules.

#### §4.B.4 — Acquisition Gap Analysis

**Capability:** The source engine analyzes the library's current coverage and proactively identifies what sources would most improve scholarship across all dimensions: school coverage, science coverage, temporal coverage, and curricular completeness.

**Technical approach:** The source engine periodically (or on demand) computes a gap analysis by querying: (1) the taxonomy engine's coverage metrics (which leaves have thin school coverage), (2) the work registry's citation placeholders (which unacquired works are most referenced), (3) the scholar authority model's known works lists (which works by scholars already in the library are not yet acquired), and (4) classical curricular knowledge from its LLM capability (which works are considered essential for each science at each level).

The gap analysis produces a ranked acquisition priority list:
- "Your library has 0 Maliki sources on inheritance law (المواريث). Recommended: شرح الرحبية by السبط المارديني — available on Shamela."
- "ابن قدامة's المغني is referenced 47 times but not in your library. It's the primary Hanbali fiqh reference."
- "You have 3 beginner nahw sources but no intermediate ones. Recommended next: قطر الندى by ابن هشام."

**What this enables:** The library grows strategically rather than haphazardly. The owner doesn't have to know what books exist — KR tells him what he needs. This is how KR fills the role of scholarly guide (Scenario 1's curriculum design depends on the source engine knowing what's available and what's missing).

[NOT YET IMPLEMENTED] — Specification provided above. Depends on: taxonomy engine coverage metrics, work registry with citation counts, and repository search interface modules.

---

## 5. Validation and Quality

The source engine's output — source metadata — is the foundation upon which every downstream engine builds. An error here cascades through the entire pipeline. The validation architecture has three layers.

**Layer 1: Self-validation (automated, at intake time).**

The source engine validates its own output before writing the metadata record:

1. **Schema compliance.** The metadata record is validated against the source metadata JSON schema. Any missing required field, type mismatch, or constraint violation aborts the write with a structured error.

2. **Referential integrity.** The `author.canonical_id` must reference a valid record in the scholar authority registry. The `work_id` must reference a valid record in the work registry. Genre chain relationships must reference valid work_ids (or placeholder records). If any reference is invalid, the write aborts.

3. **Confidence threshold check.** If any critical field (author canonical_id, work_id, genre, science_scope) has confidence < 0.50, the metadata record is not written. Instead, a human gate checkpoint is created. The threshold is 0.50, not 0.70, because 0.50-0.70 fields are written with `needs_review` flags, and only truly low-confidence fields block writing.

4. **Duplicate re-check.** After metadata inference (which may have changed the title or author), deduplication is re-run. This catches cases where the raw metadata didn't match a duplicate but the inferred metadata does.

5. **Consistency cross-check.** The inferred genre must be consistent with the inferred structural_format (a `nazm` genre should have `verse` structural_format). The inferred level must be consistent with the genre (a `hashiyah` should not be `beginner`). The science_scope must be plausible for the identified author. Inconsistencies are flagged as warnings (not blocking) and trigger `needs_review` on the inconsistent fields.

**Layer 2: Human gate review.**

The following conditions trigger human gate checkpoints:

- Author disambiguation with confidence < 0.80
- Work matching with confidence between 0.50 and 0.85
- Any critical field with confidence < 0.70
- Trust evaluation that results in `flagged` (owner may override)
- Multi-model consensus disagreement on author or work identification
- Genre chain relationship where the base work is not in the library (owner confirms the relationship and may choose to acquire the base work)

Human gate reviews are batched — the owner reviews all pending checkpoints for a source at once, not one field at a time. The review interface presents: the inferred metadata with confidence scores, the specific fields that need review, and (where applicable) the alternatives considered.

**Layer 3: Progressive correction.**

Source metadata is living. As downstream engines process the source, they may discover corrections:
- The normalization engine discovers the volume structure is different from what the source engine extracted.
- The excerpting engine discovers the author is a different scholar than initially identified (e.g., the text's writing style and positions are inconsistent with the attributed author).
- The owner corrects a field during study.

All corrections are written back through the enrichment interface (§2, enrichment write-back input). Each correction is logged with the correcting agent, timestamp, old value, and new value. If a correction affects a field that downstream engines have already consumed (e.g., author canonical_id), the correction triggers a stale-marking cascade: all excerpts from this source are re-evaluated for the affected metadata.

**Scholarly integrity guarantee:** No source enters the library without: (1) a canonical author identity linked to the scholar authority model, (2) a work classification (genre, science scope), (3) a trustworthiness evaluation, and (4) frozen original files with integrity hashes. These four guarantees ensure that every excerpt derived from this source can be traced to a specific author, a specific work, a specific edition, and the original text — the foundation of scholarly citation.

---

## 6. Consensus Integration

Multi-model consensus is used for two decisions in the source engine:

1. **Author identification.** When the source engine identifies a source's author and needs to match to or create a scholar authority record, two LLMs independently process the same metadata. If they agree on the canonical_id (or both agree a new record is needed), the result is accepted. If they disagree, a human gate checkpoint is created. This is the highest-cascade-risk decision in the source engine — a wrong author identification propagates through every downstream engine.

2. **Work matching.** When the source engine determines whether a new source belongs to an existing work or is a new work, two LLMs independently evaluate the match. Agreement → accept. Disagreement → human gate.

Consensus is NOT used for: genre classification, science scope, structural format, or trust evaluation. These fields have lower cascade risk (they affect processing strategy but don't corrupt attribution) and their correctness is verifiable by downstream engines. Adding consensus to every field would multiply LLM costs without proportionate quality gain.

**Consensus configuration:** Two models (configured via OpenRouter or direct API). Agreement threshold: both models must select the same canonical_id or work_id. Models should be from different providers (e.g., Claude + GPT) to reduce correlated errors. If one model times out or fails, the surviving model's result is accepted with a `single_model_confidence` flag.

---

## 7. Error Handling

**Error taxonomy:**

| Code | Severity | Trigger | Recovery |
|------|----------|---------|----------|
| `SRC_UNSUPPORTED_FORMAT` | Fatal | Unrecognized file type | Reject with message. Owner converts or provides differently. |
| `SRC_EMPTY_INPUT` | Fatal | Empty file/directory | Reject with message. |
| `SRC_INVALID_ENRICHMENT` | Warning | Invalid enrichment write-back | Reject the enrichment. Log. Notify originating engine. |
| `SRC_DUPLICATE_EXACT` | Info | SHA-256 hash match | Log alternative availability. Do not acquire. |
| `SRC_DUPLICATE_WORK` | Info | Same work, different edition | Acquire as new source. Link to existing work_id. Notify owner. |
| `SRC_AUTHOR_AMBIGUOUS` | Warning | Author disambiguation failed | Create human gate checkpoint. Source waits for resolution. |
| `SRC_WORK_MATCH_UNCERTAIN` | Warning | Work matching confidence 0.50-0.85 | Create human gate checkpoint. Source waits for resolution. |
| `SRC_LOW_CONFIDENCE` | Warning | Critical field confidence < 0.50 | Block metadata write. Create human gate checkpoint. |
| `SRC_METADATA_INCONSISTENCY` | Warning | Genre/format/level inconsistency | Flag inconsistent fields. Write metadata with warnings. |
| `SRC_FREEZE_FAILED` | Fatal | File copy or hash computation failed | Abort intake. Log error. Source material remains in staging. |
| `SRC_REGISTRY_CONFLICT` | Fatal | Registry update would violate an invariant | Abort registry update. Log. Notify architect. |
| `SRC_OCR_LOW_QUALITY` | Warning | OCR confidence < 0.70 on critical fields | Create human gate for manual entry. Proceed with available data. |
| `SRC_REPO_UNAVAILABLE` | Warning | Repository module cannot connect | Log. Skip this repository for this scan. Retry next cycle. |
| `SRC_CONSENSUS_DISAGREEMENT` | Warning | Multi-model disagreement | Create human gate checkpoint. |

**Principle:** Never lose data silently. Every error is logged with: timestamp, source identifier (if known), error code, severity, human-readable message, and recovery action taken. Fatal errors stop processing for the affected source but do not affect other sources in the pipeline. Warning errors allow processing to continue with appropriate flags. Info errors are logged for audit.

**What gets logged:** Every intake attempt (success or failure), every duplicate detection, every human gate checkpoint creation, every enrichment write-back, every registry update. The log is append-only and stored at `library/logs/source_engine.jsonl`.

**What triggers alerts:** Fatal errors during batch processing, > 10% of sources in a batch hitting the same warning code (suggests a systematic issue), human gate queue growing beyond 20 items (suggests the owner needs to review).

---

## 8. Configuration

**Core parameters:**

| Parameter | Default | Valid Range | Description |
|-----------|---------|-------------|-------------|
| `staging_path` | `library/staging/` | Any writable path | Where source material is placed for intake |
| `confidence_threshold_auto_accept` | 0.70 | 0.50–0.95 | Fields with confidence ≥ this are accepted without review |
| `confidence_threshold_block` | 0.50 | 0.30–0.70 | Fields with confidence < this block metadata write |
| `trust_score_verified_threshold` | 0.65 | 0.50–0.80 | Combined trust score ≥ this → verified tier |
| `consensus_model_count` | 2 | 2–3 | Number of models for multi-model consensus |
| `consensus_model_providers` | `["anthropic", "openai"]` | Valid provider list | LLM providers for consensus |
| `max_ocr_pages_title` | 3 | 1–10 | Max pages to OCR for title page extraction |
| `openiti_metadata_path` | `library/external/openiti_metadata.csv` | File path | Path to cached OpenITI metadata |
| `dedup_hash_algorithm` | `sha256` | `sha256` only | Hash algorithm for deduplication |
| `human_gate_batch_size` | 20 | 5–50 | Max pending checkpoints before alert |

**Per-science configuration hooks (Level 3 / SCIENCE.md):**

Each science's Level 3 documentation may specify:
- Science-specific metadata fields the source engine should attempt to extract (e.g., for hadith collections: the collection type and numbering system).
- Science-specific trust evaluation adjustments (e.g., in tajwid, only sources from recognized qurra are trusted).
- Science-specific genre expectations (e.g., in nahw, versified texts are extremely common and the source engine should be especially good at detecting them).

**What is hardcoded and why:**
- The SHA-256 hash algorithm — changing algorithms would break deduplication and integrity verification across the library.
- The source_id format (`src_{8_char_hash}`) — changing this would require re-keying the entire library.
- The trust tier names (`verified`, `flagged`, `owner_override`) — these are referenced by downstream engines and the quality architecture.
- The freeze-before-process invariant — this is an architectural guarantee, not a configurable preference.

---

## 9. Current Implementation State

**Existing files:**
- `engines/source/src/intake.py` (1476 lines): ABD-era Shamela intake CLI tool. Works for Shamela HTML exports only. Handles: book ID validation, source validation (Shamela-specific HTML checks), duplicate detection (SHA-256), source freezing, metadata extraction (Shamela metadata card parsing), and registry updates (books_registry.yaml).
- `engines/source/src/enrich.py` (580 lines): ABD-era metadata enrichment tool. Uses LLM to infer scholarly context (death dates, school, geographic origin, book type). Single-model only (no consensus). Updates intake_metadata.json.
- `engines/source/src/corpus_audit.py` (228 lines): Validates corpus-wide metadata consistency. Checks: all books have metadata, all metadata conforms to schema, cross-reference integrity.
- `engines/source/tests/test_intake.py` + `engines/source/tests/test_enrich.py`: 112 tests total. Cover Shamela-specific intake flows and enrichment.

**What works today:**
- Shamela HTML intake with book ID validation, duplicate detection, freezing, and basic metadata extraction.
- LLM-based scholarly context enrichment (single model, Shamela only).
- Corpus audit for consistency checking.

**Known gaps between current code and this SPEC:**

1. **Identity model.** Code uses `book_id` (user-assigned slug). SPEC requires `source_id` (hash-based), `work_id` (abstract work grouping), and scholar `canonical_id` (authority model). [NOT YET IMPLEMENTED]

2. **Multi-format support.** Code handles Shamela HTML only. SPEC requires: PDF, image (iPhone photos), EPUB, plain text, owner-authored content. [NOT YET IMPLEMENTED]

3. **Scholar authority model.** Code stores author as a flat string in metadata. SPEC requires a centralized scholar authority registry with canonical identities, name variants, biographical data, teacher-student graph, and progressive enrichment. [NOT YET IMPLEMENTED]

4. **Work registry.** Code has no concept of works grouping multiple sources. SPEC requires a work registry tracking abstract works, their sources (editions), relationships (sharh→matn chains), and preferred editions. [NOT YET IMPLEMENTED]

5. **LLM-assisted metadata inference.** Code's `enrich.py` does basic LLM enrichment. SPEC requires comprehensive bibliographic intelligence: genre chain inference, multi-layer detection, structural format classification, science scope inference, and confidence scoring. [NOT YET IMPLEMENTED]

6. **Multi-model consensus.** Code uses single-model inference. SPEC requires two-model consensus for author identification and work matching. [NOT YET IMPLEMENTED]

7. **Work relationship graph.** Code has no relationship tracking. SPEC requires a queryable graph of sharh→matn, mukhtasar→original, and citation relationships. [NOT YET IMPLEMENTED]

8. **Trustworthiness evaluation.** Code has no trust assessment. SPEC requires a multi-factor evaluation producing verified/flagged tiers. [NOT YET IMPLEMENTED]

9. **OpenITI enrichment.** [NOT YET IMPLEMENTED]

10. **Citation network discovery.** [NOT YET IMPLEMENTED]

11. **Acquisition gap analysis.** [NOT YET IMPLEMENTED]

12. **Processing status tracking.** Code uses a simple registry. SPEC requires pipeline-wide status tracking with stage-specific timestamps. [NOT YET IMPLEMENTED]

**External tools and libraries:**
- **Docling** (IBM, Apache 2.0): PDF and image parsing for non-Shamela sources. The normalization engine will use Docling as its primary parser, but the source engine uses it for limited metadata extraction from PDFs and images during intake.
- **Google Document AI**: Premium Arabic OCR for iPhone photos and scanned PDFs. Used by the source engine's image metadata extractor.
- **OpenITI metadata CSV**: External enrichment data for scholar authority bootstrapping (§4.B.1).
- **CAMeL Tools** (NYU Abu Dhabi, MIT): Arabic text normalization utilities for name matching in deduplication and scholar authority matching.
- **OpenRouter / Anthropic API / OpenAI API**: LLM access for metadata inference and consensus.
- **sunnah.com API** (future): Hadith collection metadata for special source type handling.

---

## 10. Test Requirements

**What MUST be tested:**

1. **Source identity model correctness.** Given the same input, the source engine must produce the same source_id, work_id, and author canonical_id. Test: provide a Shamela export, verify IDs are deterministic. Provide the same work from a different repository, verify it links to the same work_id. Provide two different tahqiq editions, verify they get different source_ids but the same work_id.

2. **Deduplication accuracy.** Test: ingest the same file twice → second attempt is rejected with `SRC_DUPLICATE_EXACT`. Ingest two different editions of the same work → both are acquired, linked to the same work_id. Ingest two completely different works → no duplicate detected.

3. **Metadata completeness.** Test: after intake, the metadata record has non-null values for all required fields. Confidence scores are present for all inferred fields. The author canonical_id links to a valid scholar authority record.

4. **Trustworthiness evaluation consistency.** Test: a recognized classical work with known muhaqiq → verified. An unknown work with no muhaqiq and unknown publisher → flagged. Owner override → trust tier changes, original evaluation preserved.

5. **Scholar authority matching.** Test: provide two sources by the same author (spelled differently) → both link to the same canonical_id. Provide sources by two different scholars with similar names → they get different canonical_ids (with human gate if confidence is borderline).

6. **Work relationship detection.** Test: provide a sharh → the genre chain correctly identifies the base work and creates a relationship record. Provide a standalone matn → no genre chain relationship.

7. **Freeze integrity.** Test: after intake, the frozen files match the computed SHA-256 hashes. Attempt to modify a frozen file → operation is rejected or detected.

8. **Error handling completeness.** Test every error code in the taxonomy: provide an unsupported format → `SRC_UNSUPPORTED_FORMAT`. Provide an empty file → `SRC_EMPTY_INPUT`. Etc.

**Gold baseline usage:** No gold baselines exist for the source engine yet. The first gold baselines should be created from: (1) a well-known Shamela export (e.g., شرح ابن عقيل) with manually verified metadata, and (2) a scanned PDF with manually verified OCR and metadata extraction.

**Regression testing strategy:** After any change to the metadata inference prompt, re-run intake on the gold baseline sources and verify that metadata output matches expected values. After any change to the scholar authority matching logic, re-run on a test set of sources with known author matches/non-matches.

**Integration test requirements:**
- Source engine → normalization engine: verify that the metadata record produced by the source engine is correctly read by the normalization engine and that source_id references resolve correctly.
- Source engine → scholar authority registry: verify that scholar records created during intake are correctly queryable by the excerpting engine and synthesizing engine.
- Enrichment write-back: verify that a downstream engine's enrichment update is correctly applied to the source metadata record and that the update triggers appropriate stale-marking.
