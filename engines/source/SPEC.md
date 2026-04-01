# ⚠ SUPERSEDED — DO NOT USE FOR IMPLEMENTATION

**This file is the pre-core-extraction full SPEC, kept as an archive of Stage 2 (deferred) capability descriptions. The authoritative specification is `SPEC_CORE.md`.**

Read `SPEC_CORE.md` instead. If you are looking for deferred feature descriptions (§4.B capabilities), see `CORE_VS_DEFERRED.md` for the classification.

---

# Source Engine — محرك المصادر — Specification (ARCHIVED)

## 1. Purpose and Scope

The source engine is the pipeline entry point. It accepts raw knowledge material from the outside world, establishes the identity model for every source, work, and scholar in the library, captures and infers the metadata that fuels every downstream engine, freezes original files for integrity, and maintains the registries that prevent duplication and track relationships.

**What this engine does:**
- Accepts source material through manual and autonomous acquisition paths
- Assigns canonical identifiers to sources, works, and scholars
- Extracts, infers, and validates source metadata
- Freezes raw source files with cryptographic integrity hashes
- Detects duplicates across acquisition paths and repositories
- Classifies source trustworthiness for default verified/flagged status
- Tracks work-to-work relationships (sharh→matn, hashiyah→sharh, mukhtasar→original, nazm→prose_original, taqrirat→base_work, responds_to, cites — the full taxonomy is defined in §4.A.9)
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

**Enrichment write-back input.** Downstream engines may write metadata enrichments back to source records. These arrive as structured update requests specifying: the source_id to update, the field(s) to update, the new value(s), and the engine that produced the enrichment. The source engine validates that the source_id exists and that the update does not violate the enrichment invariants enumerated below. Invalid updates are rejected with error `SRC_INVALID_ENRICHMENT`.

**Enrichment invariants (exhaustive list — an enrichment write is rejected if it violates ANY of these):**

1. **Frozen file immutability.** No enrichment may modify `frozen_hash`, `frozen_file_paths`, or any frozen file content.
2. **Identity immutability.** No enrichment may modify `source_id`. Changes to `work_id` or `author.canonical_id` require a human gate checkpoint (`SRC_ENRICHMENT_CRITICAL_FIELD`) — these are high-cascade fields where a wrong change corrupts all downstream products.
3. **No field deletion.** Enrichment may add new fields or update existing field values. No enrichment may set an existing non-null field to null or remove a field entirely.
4. **History preservation.** Every field update must record the previous value, the updating engine, and the timestamp in `metadata_history`. An enrichment that does not provide the updating engine identifier is rejected.
5. **Trust tier protection.** No enrichment may change `trust_tier` to `verified` directly — verified status can only be set through the trustworthiness evaluation algorithm (§4.A.8) or an explicit `owner_override`. An enrichment may request a trust re-evaluation by updating evaluation-relevant fields (e.g., correcting the muhaqiq name).
6. **Schema compliance.** The updated metadata record, after applying the enrichment, must still pass the SourceMetadata Pydantic model validation. An enrichment that would produce an invalid record is rejected.
7. **Referential integrity.** If the enrichment changes a reference field, the new reference must resolve to a valid record in its target registry: `author.canonical_id` must resolve in `scholars.json`, `work_id` must resolve in `works.json`, and genre chain work references must resolve in `works.json` (or exist as placeholder records).
The source engine must check each reference before accepting the enrichment. Unresolvable references cause the enrichment to be rejected.
8. **Re-processing depth limit.** When an enrichment triggers stale-marking and re-processing of downstream products, the re-processed output may generate at most one further enrichment request on the same source. If that second-generation enrichment would modify the same field that was changed by the first enrichment (forming a potential cycle), it is NOT auto-submitted. Instead, it is logged with both the original and proposed values, and a human gate checkpoint is created: "Field `{field}` was changed from A→B, re-processing now suggests reverting or changing further. Manual resolution required."
9. **Verification context for critical fields.** Enrichment requests that modify fields in the critical set (`author.canonical_id`, `work_id`, `genre`, `science_scope`) must include a `verification_context` containing the `work_id` and `author.canonical_id` that the requesting engine believes belong to this source. The source engine checks these against the actual source metadata before applying. If they don't match, the enrichment is rejected with `SRC_INVALID_ENRICHMENT` — this catches source_id targeting errors at the boundary.

**Critical field enrichment gate.** Enrichments to `author.canonical_id`, `work_id`, `genre`, or `science_scope` — regardless of originating engine — trigger additional validation: (a) the old and new values are logged at WARNING level, (b) a human gate checkpoint is created for owner confirmation before the enrichment is applied, and (c) if confirmed, a stale-marking cascade is triggered on all downstream products derived from this source.

---

## 3. Output Contract

The source engine produces two primary artifacts per acquired source, plus updates to three shared registries.

**Primary artifacts:**

1. **Frozen source file(s).** The raw source material, copied to `library/sources/{source_id}/frozen/` and set read-only. A SHA-256 hash is computed at freeze time and stored in the source metadata record. No component of the application — including the source engine during later enrichment — may modify frozen files. For multi-file sources (multi-volume directories, photo sets), each file is individually hashed and the composite hash is recorded.

2. **Source metadata record.** A structured JSON file at `library/sources/{source_id}/metadata.json`, conforming to the source metadata schema.
The engine must check the record against the SourceMetadata Pydantic model, verify referential integrity, and confirm confidence thresholds before persisting. Failures abort with a structured error (see section 5, Layer 1). This record contains everything known about the source at intake time plus a mechanism for progressive enrichment. The required fields are specified throughout §3 (output guarantees) and §4.A.4 (inferred fields). The actual JSON schema file will be generated from these requirements during implementation.

**Guarantees about the metadata record** (enforced by §5 Layer 1 validation before every write):
- Every required field has a non-null value. Optional fields may be null, but null is explicitly recorded (not absent).
- The `source_id` is globally unique across the library.
- The `work_id` correctly groups this source with other sources of the same abstract work (if any exist).
- The `author.canonical_id` references a confirmed entry in the scholar authority model (§5 checks ensure referential integrity).
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

**Shared registry updates** (all registry writes are validated against their Pydantic models and applied atomically — see §5):

3. **Source registry** (`library/registries/sources.json`). A catalog of all acquired sources with their source_id, work_id, title, author canonical_id, trust tier, processing status, and deduplication hashes. Each entry is validated against the SourceRegistryEntry model. Used for duplicate detection, source lookup, and status tracking. Updated atomically on each acquisition.

4. **Work registry** (`library/registries/works.json`). A catalog of all known works with their work_id, canonical title, author canonical_id, genre, science scope, and the list of source_ids that are manifestations of this work. Each entry is validated against the WorkRegistryEntry model. Includes the owner's preferred_source_id per work. Updated when a new source is linked to a work or when a new work is created.

5. **Scholar authority registry** (`library/registries/scholars.json`). The centralized record of every scholar encountered across all sources.
The engine must check each entry against the ScholarAuthorityRecord model before persisting it. Updated when the source engine creates or enriches a scholar record during intake. The structure and semantics of scholar authority records are defined in §4.A.5. This is a shared resource: the source engine is the primary writer, the excerpting engine adds quoted-scholar references, and the synthesizing engine is the primary reader.

---

## 4. Processing Specification

### §4.A — Core Processing

#### §4.A.1 — Source Identity Model

The source identity model has three tiers: sources, works, and scholars.

**Source identity.** Every acquired source receives a `source_id` at registration time. The source_id is a permanent, globally unique identifier formatted as `src_{8_char_hash}` where the hash is derived from the frozen source's composite SHA-256 hash (first 8 hex characters). If a collision occurs (astronomically unlikely but handled), append a numeric suffix: `src_{hash}_2`. The source_id is assigned at freeze time and never changes.

The ABD-era `book_id` (user-assigned ASCII slug like `ibn_aqil`) is preserved as `human_label` — a human-readable shorthand for use in logs, CLI output, and owner-facing displays. The `human_label` is not a primary key and need not be unique across the library (though the source engine warns if a duplicate is detected). The `human_label` is assigned at intake: if the owner provides one, it is used; otherwise, the source engine generates one from the work title's distinctive words (transliterated, lowercased, underscored).

**Work identity.** A work (مؤلَّف) is the abstract intellectual creation — the book as a scholarly contribution, independent of any particular edition or format. "al-Mughni by Ibn Qudamah" is a work. Each work receives a `work_id` formatted as `wrk_{author_slug}_{title_slug}` where the slugs are derived from the canonical author name and canonical work title (transliterated, lowercased, underscored, max 40 characters total). Example: `wrk_ibn_qudamah_mughni`.

The same work may have two or more sources in the library: different tahqiq editions, different digital formats, different repository origins. All share the same `work_id`. A new source triggers work matching: the source engine checks whether a work record already exists for this author+title combination. Matching uses normalized title comparison (stripping definite articles, normalizing hamza/taa marbuta) and author canonical_id matching. If a match is found with confidence ≥ 0.85, the source is linked to the existing work. If confidence is between 0.50 and 0.85, a human gate checkpoint is created presenting the candidate match for owner confirmation. If confidence < 0.50, a new work record is created.

The work record tracks: the owner's preferred source for this work (`preferred_source_id`), which defaults to the first source acquired and can be changed by the owner. The preferred source is the one from which excerpts are primarily drawn; other sources serve as cross-references for variant readings and alternative commentary.

**Multi-volume works.** A multi-volume work (e.g., al-Mughni's 15 volumes) is ONE work with ONE `work_id`. Each volume may be a separate source (separate `source_id`) if acquired as separate files, or a single source if acquired as one package. The source metadata record includes a `volumes` field listing volume numbers and their file mappings. The work registry tracks which volumes are present and which are missing, enabling gap detection ("you have volumes 1-12 and 14 of al-Mughni — volume 13 and 15 are missing").

**Scholar identity.** Every author, editor (muhaqiq), and quoted scholar receives a canonical identity in the scholar authority registry. The scholar identity model is detailed in §4.A.5.

**Worked example — Identity assignment for شرح ابن عقيل على ألفية ابن مالك:**

Input: Shamela HTML export directory containing numbered `.htm` files. Owner provides human_label hint: `ibn_aqil`.

1. **source_id assignment:** The frozen files produce SHA-256 composite hash `a7c3e91f...`. The source_id is `src_a7c3e91f`.
2. **work_id assignment:** The metadata extraction step identifies author = ابن عقيل and title = شرح ابن عقيل على ألفية ابن مالك. Transliterated slugs: `ibn_aqil` + `sharh_alfiyyah`. The work_id is `wrk_ibn_aqil_sharh_alfiyyah`.
3. **Work matching:** The source engine checks the work registry for `wrk_ibn_aqil_sharh_alfiyyah`. No match → new work record created.
4. **Scholar identity:** The LLM identifies the author as بهاء الدين عبد الله بن عقيل الهمداني المصري (d. 769 AH). The scholar authority registry is checked for a match on name + death date → no existing record → new record created: `sch_00312`. Confidence: 0.96 (well-known scholar, unambiguous title).
5. **human_label:** Owner provided `ibn_aqil` → used as-is.

#### §4.A.2 — Acquisition Workflow

The acquisition workflow is intentionally minimal for v1 (D-020). The source engine accepts files the owner provides and performs basic automated discovery. Elaborate multi-repository crawling, format expansion, and proactive acquisition are designed but marked [NOT YET IMPLEMENTED].

**Step 1: Staging.** Source material arrives in the intake staging area (`library/staging/`). For manual acquisition, the owner places files there (or the scholar interface moves uploaded files there). For autonomous discovery, the repository module downloads to staging.

**Step 2: Format detection.** The source engine examines the staged material and determines its source type. Detection is based on file extension, content inspection (HTML structure for Shamela, PDF magic bytes, image EXIF headers), and directory structure (numbered `.htm` files → Shamela multi-volume). The detected source type determines which normalizer will later process it. If the format is unrecognized, the source is rejected with `SRC_UNSUPPORTED_FORMAT`.

**Step 3: Metadata extraction.** The source engine extracts metadata from the source material using format-specific extractors (§4.A.3). This is the only place in the source engine where format-specific logic exists — the extractors are modular, one per source type, analogous to normalizers.

**Step 4: Metadata inference.** The source engine uses LLM-assisted inference to fill metadata gaps and enrich the extracted data (§4.A.4). This step transforms sparse, format-specific metadata into the rich, structured record the pipeline needs.

**Step 5: Duplicate detection.** The source engine checks the source registry for duplicates using the deduplication criteria in §4.A.7.

**Step 6: Freezing.** Before copying, the source engine computes a SHA-256 hash of each staged file (the "staging hash"). The staged files are then copied to `library/sources/{source_id}/frozen/`. After copying, the frozen files are hashed again (the "frozen hash"). The source engine verifies that each staging hash equals its corresponding frozen hash — if any mismatch is detected, the frozen directory is deleted and the intake aborts with `SRC_FREEZE_COPY_CORRUPT`. This post-freeze verification ensures no copy corruption occurs.

After verification, frozen files are set read-only using filesystem permissions (`chmod 0444`). If the permission change fails, the intake aborts with `SRC_FREEZE_PERMISSION_FAILED` — a file that cannot be made read-only is not safely frozen. From this point, the frozen files are immutable. The staging directory for this source is renamed to `library/staging/.processed/{source_id}/` (preserving the originals for audit) after successful registration. If the post-freeze hash verification fails (SRC_FREEZE_COPY_CORRUPT), the frozen directory is deleted. If deletion also fails (e.g., disk full), the engine logs `SRC_FREEZE_CLEANUP_FAILED` (severity: Fatal) and writes a marker file `library/sources/{source_id}/CORRUPT_FREEZE` containing the error details and timestamp. On startup, the engine checks for any `CORRUPT_FREEZE` markers and treats those source directories as requiring manual cleanup — they are not available for processing.

**Staging lock.** Between format detection (Step 2) and freezing (Step 6), the source engine places a lock file (`library/staging/{source_dir}/.kr_processing`) to signal that the staged material is being processed. If the staged files are modified after format detection (detected by comparing file modification timestamps at freeze time against those recorded at format detection time), the intake aborts with `SRC_STAGING_MODIFIED`. This prevents TOCTOU corruption where a file changes between analysis and freezing. **Orphaned lock cleanup:** On startup, the source engine scans `library/staging/` for directories containing `.kr_processing` lock files. For each lock file whose modification timestamp is older than `staging_lock_timeout` (§8, default: 3600 seconds), the lock is removed and the directory is made available for re-processing. A log entry records each cleanup.

**Step 7: Registration.** The source metadata record, source, work, and scholar registries are all updated atomically — all succeed or none are applied. Atomicity mechanism: the source engine prepares all registry updates in memory, validates them all (§5 Layer 1), then writes them using a write-ahead log pattern: (1) write the complete set of intended changes to `library/logs/pending_registration_{source_id}.json`, (2) apply changes to each registry file, (3) delete the pending registration file. On startup, the source engine checks for orphaned pending registration files — if one exists, it means a previous registration was interrupted, and the engine either completes or rolls back the registration based on which files were already updated. A registry file that was partially written (detected by JSON parse failure) is restored from its `.bak` copy, which is created before each write.

**Registry file locking.** All registry read-check-write operations (in Steps 4, 5, and 7) acquire an exclusive file lock on the target registry file before reading current state. Specifically: Step 4's scholar matching acquires a lock on `scholars.json` that is held through scholar record creation or match linkage. Step 5's work matching acquires a lock on `works.json` that is held through work record creation or match linkage. Step 7's atomic write phase re-verifies that no concurrent process has created the same `canonical_id` or `work_id` since the lock was acquired in Steps 4/5 — if a duplicate is found (due to a lock gap between Steps 5 and 7), Step 7 links to the existing record instead of creating a duplicate. If a lock cannot be acquired within 30 seconds, the intake for this source is deferred to `staging` status with a retry scheduled. This serializes registry mutation without blocking the entire intake pipeline.

The engine must check schema compliance, referential integrity, and confidence thresholds before persisting (section 5, Layer 1).

**Step 8: Trustworthiness evaluation.** The source engine assesses the source's reliability and assigns a trust tier (§4.A.8).

**Step 9: Handoff.** The source is marked as `status: "acquired"` and is available for the normalization engine to process. The normalization engine picks up sources with this status.

**Worked example — Acquisition of a Shamela export of قطر الندى by ابن هشام:**

Step 1 (Staging): Owner places `qatr_alnada/` directory in `library/staging/`. The directory contains `0.htm`, `1.htm`, ..., `12.htm` and an `info.html` file.
Step 2 (Format detection): File structure detected as Shamela multi-volume HTML export (numbered `.htm` files + `info.html`). Source type: `shamela_html`.
Step 3 (Metadata extraction): Shamela extractor parses `info.html` → title: "قطر الندى وبل الصدى", author: "ابن هشام الأنصاري", shamela_category: "النحو والصرف". Page count from `PageNumber` spans: 340 pages across 1 volume.
Step 4 (Metadata inference): LLM infers → genre: `matn` (confidence 0.92), genre_chain: null (this IS the matn), science_scope: `["nahw"]` (confidence 0.97), level: `intermediate` (confidence 0.88), structural_format: `prose`. Author identified as ابن هشام الأنصاري (d. 761 AH), matched to existing `sch_00198` with confidence 0.97.
Step 5 (Deduplication): SHA-256 computed. No hash match in registry. Work matching: `wrk_ibn_hisham_qatr_alnada` not in registry → new work.
Step 6 (Freezing): Files copied to `library/sources/src_b2d4f6a8/frozen/`. All 14 files individually hashed. Composite hash: `b2d4f6a8...`. Files set read-only.
Step 7 (Registration): `metadata.json` written. Source registry, work registry, scholar registry updated.
Step 8 (Trustworthiness): Author standing: 0.95 (major classical grammarian). Tahqiq: muhaqiq = محمد محيي الدين عبد الحميد, recognized → 0.90. Publisher: unknown Shamela digitization → 0.50. Authority: primary → 0.85. Text fidelity: Shamela structured → 0.90. Combined: 0.83 → `verified`.
Step 9 (Handoff): Status → `acquired`.

#### §4.A.3 — Format-Specific Metadata Extraction

Each source type has a metadata extractor — a module that knows how to pull metadata from that format's specific conventions. Extractors are kept minimal: they extract what the format provides, then hand off to the LLM inference step (§4.A.4) for enrichment.

**Shamela HTML extractor.** Parses the metadata card from the first `PageText` div. Extracts: title (from `<h1>` or title span), author (from المؤلف field), publisher, edition, page count (from `PageNumber` span count), volume structure (from numbered file stems). Shamela-specific fields (shamela_book_id, shamela_category) are preserved as `format_specific_metadata` — they are consumed only by the Shamela normalizer and do not enter the pipeline-wide metadata schema. If the `info.html` file is absent from an otherwise valid Shamela directory (numbered `.htm` files present but no metadata file), the extractor raises `SRC_FORMAT_STRUCTURE_MISSING`, extracts title and author from the first `PageText` div's content (first heading or first paragraph), and flags all extracted fields as `needs_review`. If `info.html` is present but malformed (not valid HTML, missing expected fields), the extractor logs a structured warning and extracts what it can — partial metadata is always preferred over no metadata.

**PDF extractor.** Extracts document metadata from PDF properties (title, author, creation date). For scanned PDFs, performs limited OCR on the title page (first 1-3 pages) to extract title, author, publisher information. Uses Docling (see RESOURCES.md) for PDF parsing. Page count from PDF page count. For text-embedded PDFs, extracts table of contents if structured bookmarks exist.

**Image extractor.** For photographic scans: performs OCR on the first image (assumed to be title page or cover) to extract title and author. Uses Google Document AI or Docling for Arabic OCR. If OCR confidence is below 0.70 on critical fields (title, author), creates a human gate checkpoint requesting manual entry. Image count serves as page count.

**Plain text / EPUB extractor.** Minimal extraction: title from filename or first line, page count from character/word count estimation. Most metadata will come from LLM inference and owner input.

**Word document extractor.** For `.doc` and `.docx` files: uses Docling (see RESOURCES.md) to extract text and metadata. Document properties (title, author, creation date) are extracted from Word metadata fields. For collections of Word files in a directory (e.g., one file per chapter), the source engine treats the directory as a single multi-part source, ordering files by filename. Encoding detection is critical: Arabic filenames in ZIP archives often use CP1256 encoding (as seen in the mughni_comparative fixture). The extractor normalizes filenames to UTF-8 and preserves the original filename in metadata.

**Owner-authored content extractor.** No format-specific extraction needed — the owner provides the metadata directly through the input interface. The extractor validates the input type and captures any metadata hints.

**Worked example — Shamela extraction for شرح ابن عقيل على ألفية ابن مالك:**

Input: Shamela HTML export with `info.html` containing:
```html
<h1>شرح ابن عقيل على ألفية ابن مالك</h1>
<div class="metadata">المؤلف: بهاء الدين عبد الله بن عقيل</div>
<div class="metadata">المحقق: محمد محيي الدين عبد الحميد</div>
<div class="metadata">الناشر: دار التراث</div>
```
Content directory: 22 numbered `.htm` files (volumes 1-2).

Extracted metadata record (before LLM inference):
- `title_arabic`: "شرح ابن عقيل على ألفية ابن مالك" (from `<h1>`)
- `author_name_raw`: "بهاء الدين عبد الله بن عقيل" (from المؤلف field)
- `muhaqiq`: "محمد محيي الدين عبد الحميد" (from المحقق field)
- `publisher`: "دار التراث" (from الناشر field)
- `page_count`: 648 (from `PageNumber` span count across all files)
- `volume_count`: 2 (from file stem grouping: files 0-11 = vol 1, files 12-22 = vol 2)
- `format_specific_metadata`: `{"shamela_book_id": "10803", "shamela_category": "النحو والصرف"}`

Fields left for LLM inference (§4.A.4): genre, genre_chain, science_scope, level, structural_format, author canonical_id, source_authority.

#### §4.A.4 — LLM-Assisted Metadata Inference

After format-specific extraction produces a sparse metadata record, the source engine uses LLM inference to fill gaps, validate extracted data, and enrich the record with scholarly context. This is the step that transforms raw bibliographic data into the rich metadata that fuels synthesis.

**The inference prompt** receives: the extracted metadata (title, author name, any available fields), the first 2000 characters of source text (if available from format-specific extraction), the table of contents (if available), and the library's current state (existing works, existing scholar records for potential matches).

**The LLM infers the following fields when not already present:**

*Work classification:*
- `genre`: one of `matn`, `sharh`, `hashiyah`, `mukhtasar`, `nazm`, `risalah`, `taqrirat`, `mawsuah` (encyclopedia), `fatawa` (fatwa collection), `mu'jam` (dictionary), `tabaqat` (biographical dictionary), `fiqh_comparative` (comparative fiqh like al-Mughni), `hadith_collection`, `tafsir`, `sirah`, `tarikh` (history), `adab` (literary works related to Islamic sciences), `other`. No additional genres may be added without updating this list and the corresponding `Genre` enum in contracts.py. Inferred from title conventions (titles containing "شرح" → sharh, "مختصر" → mukhtasar, "حاشية" → hashiyah, "نظم" or verse structure → nazm) and content inspection.
- `genre_chain`: if the work is a sharh, hashiyah, mukhtasar, or nazm, the LLM identifies the base work. Example: from title "شرح ابن عقيل على ألفية ابن مالك", infer: `{ "type": "sharh", "base_work_title": "ألفية ابن مالك", "base_work_author": "ابن مالك" }`. This creates a work relationship record (§4.A.9).
- `structural_format`: one of `prose`, `verse`, `qa_format`, `tabular_khilaf`, `dictionary`, `commentary`, `mixed`. Inferred from genre and content inspection.
- `multi_layer`: boolean. True if the work contains text from two or more authors (sharh quoting matn, hashiyah quoting sharh). When true, `layers` is populated with the author and type of each layer.
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
  "record_completeness": 0.85,  // fraction of the 22 defined fields that have non-null values
  "data_provenance_score": 0.65,  // fraction of non-null biographical fields corroborated by at least one non-LLM source
  "record_sources": ["auto_inference", "openiti_metadata"],
  "last_updated": "2026-03-04T12:00:00Z"
}
```

**Record creation.** When the source engine processes a new source and identifies an author not already in the registry, it creates a new scholar record. The record is validated against the ScholarAuthorityRecord Pydantic model before writing to the registry. The record is initially populated from: (1) metadata extracted from the source (author name, any biographical info on title page/introduction), (2) LLM inference from its training knowledge (death dates, school affiliations, teachers, students, known works, scholarly standing), (3) external enrichment sources when available (OpenITI author metadata, see §4.B.1).

**Record matching.** When the source engine encounters an author name that might match an existing record, it performs matching using: normalized name comparison (stripping diacritics, normalizing hamza/taa marbuta, comparing against all `name_variants`), death date comparison (if available), school affiliation comparison, and known works comparison. A match score ≥ 0.85 auto-links; 0.50–0.85 creates a human gate checkpoint; < 0.50 creates a new record.

**Progressive enrichment.** When the 50th source mentioning a scholar is processed, the source engine checks whether the new source provides information the existing record lacks (a teacher, a work, a corrected date). If so, the record is updated.
The engine must check no field invariant is broken before persisting. Overwritten values are preserved in a `revision_history` array. This means scholar records become increasingly rich as the library grows — an early record with just a name and death date gains teachers, students, works, methodology notes, and standing assessments over time.

**Data provenance tracking.** The `data_provenance_score` field (0.0–1.0) records the fraction of non-null biographical fields (excluding mechanical fields like `canonical_id`, `last_updated`, `record_sources`) whose values are corroborated by at least one non-LLM source (OpenITI metadata, Usul-Data, Wikidata, explicit source text extraction, or owner input). The score is recomputed on every scholar record update as part of §5 Layer 1 self-validation and must pass the ScholarAuthorityRecord Pydantic model constraint (0.0 ≤ value ≤ 1.0) before the record is persisted. A score of 0.0 means entirely LLM-inferred; 1.0 means every field has external corroboration. Records with `data_provenance_score` < 0.30 are flagged as `low_provenance` in the scholar registry dashboard. The synthesizer uses this score to qualify biographical claims: high-provenance records (≥ 0.50) produce direct statements; low-provenance records (< 0.30) produce hedged statements qualified with "attributed by biographical sources" or similar language.

**Scholar record consistency checks on update.** When an enrichment modifies an established scholar record field (one with a non-null value and confidence ≥ 0.70), the source engine performs consistency validation before applying the change:

1. **Death date drift.** If the existing `death_date_hijri` differs from the proposed new value by more than 5 years, this is suspicious (it may indicate a different scholar, not a correction). The update is blocked with `SRC_SCHOLAR_DATE_CONFLICT` and a human gate checkpoint is created presenting both dates with their sources.
2. **School affiliation change.** If an existing school affiliation (e.g., `nahw: "بصري"`) would be changed to a different school (e.g., `nahw: "كوفي"`), the update is blocked with `SRC_SCHOLAR_SCHOOL_CONFLICT`. A scholar's school affiliation is a stable biographical fact — a change suggests either the original or the new data is wrong.
3. **Name change.** If `canonical_name_ar` would be modified, the update is blocked. The canonical name is set at record creation; new name variants should be added to `known_as` instead.
4. **Teacher/student self-reference.** If an enrichment would add a scholar as their own teacher or student, the update is rejected as logically impossible.
5. **Temporal consistency.** If an enrichment adds a teacher whose death date is AFTER the student's death date, the relationship is flagged as suspicious (a person cannot study under someone who died after them — this usually indicates a misidentified scholar). Exception: if the dates are within 30 years, this is plausible (a teacher may outlive a student). Beyond 30 years, `SRC_SCHOLAR_TEMPORAL_INCONSISTENCY` is raised.

**Muhaqiq (editor) records.** Tahqiq editors are scholars in their own right. Each muhaqiq encountered gets a scholar authority record with the same structure. The source metadata links to both the original author's canonical_id and the muhaqiq's canonical_id.

**Disambiguation handling.** The most critical disambiguation case is when two different scholars share a commonly used name. The registry maintains a `disambiguation_notes` field per scholar: "When 'ابن حجر' appears in hadith context → likely sch_00042 (al-Asqalani d.852). When 'ابن حجر' appears in Shafi'i fiqh context → likely sch_00089 (al-Haytami d.974)." The excerpting engine uses these notes when it encounters scholar references in text.

#### §4.A.6 — Relevance Evaluation

During autonomous discovery, the source engine evaluates whether a candidate source is relevant to the library's knowledge scope.

**Evaluation method.** The source engine extracts the candidate's title, author, and any available metadata from the repository module's search results. It sends these to the LLM with: the library's current science inventory (which sciences are covered), the library's coverage map (which topics have thin coverage), and the owner's current study focus (from the user model).

**Relevance classification:**
- `relevant`: the source covers one or more of the library's sciences and adds knowledge not already well-covered. Action: proceed to acquisition.
- `partially_relevant`: the source touches the library's sciences but most of its content is outside scope (e.g., a history book with occasional fiqh discussions). Action: CC decides scope based on owner context ("Would including this help your studies?"). If uncertain, include with `trust_tier: flagged`.
- `not_relevant`: the source is outside the library's knowledge scope entirely. Action: skip, log for future reference.

**Gap-fill relevance.** When relevance evaluation is triggered by a gap-fill request (e.g., "find a Maliki source on topic X"), the evaluation additionally checks whether the candidate specifically addresses the gap. A source that is generally relevant to the science but doesn't cover the specific topic is classified as `partially_relevant`.

**Worked example — Relevance evaluation of an autonomous discovery:**

Input: Repository module finds candidate: title = "البداية والنهاية", author = "ابن كثير", repository = Shamela.
Library state: sciences covered = [fiqh, nahw, usul_al_fiqh, aqidah]. Owner's study focus: Hanbali fiqh.

LLM evaluation: "البداية والنهاية is a tarikh (history) work by Ibn Kathir (d. 774 AH). It is primarily a historical chronicle, not a fiqh or nahw text. However, it contains biographical entries for fuqaha and occasional fiqh discussions within historical events."

Classification: `partially_relevant`. Reason: "Primary content is history (outside current science scope), but contains secondary fiqh and biographical content relevant to Hanbali scholars." Action: include with `trust_tier: flagged`, scope limited to secondary scholarly content.

Contrasting case: If the candidate were "المغني" by ابن قدامة → classification: `relevant`. Reason: "Comparative Hanbali fiqh, directly covers owner's study focus with comprehensive school-by-school analysis." Action: proceed to acquisition.

#### §4.A.7 — Deduplication

The source engine maintains deduplication at two levels: source-level (exact duplicate) and work-level (same work, different edition).

**Source-level deduplication.** Two sources are exact duplicates when their frozen file SHA-256 hashes match (for single-file sources) or when all individual file hashes match in the same order (for multi-file sources). When an exact duplicate is detected:
- If the duplicate is from a different repository: the new repository is recorded as an alternative availability in the existing source's metadata, and the duplicate is not acquired. Log: `SRC_DUPLICATE_EXACT`.
- If the owner forces re-acquisition (e.g., re-downloading after a corruption fix): the force flag bypasses deduplication.

**Work-level matching.** Two sources are editions of the same work when they share the same abstract author + title but differ in tahqiq, publisher, edition number, or format. This is NOT a duplicate — both sources are acquired and linked to the same `work_id`. The source engine detects this through work matching (§4.A.1) and records the relationship. The owner is notified: "This appears to be a different edition of {work_title}, which you already have as {existing_source_id}. Acquiring as a new source of the same work."

**Near-duplicate detection.** [NOT YET IMPLEMENTED] Two sources from different repositories may be the same content with minor differences (OCR artifacts, formatting differences). Detection would use text similarity on the first 5,000 characters after normalization. For v1, this is deferred — the owner is expected to recognize obvious duplicates.

**Worked example — Deduplication scenarios for المغني by ابن قدامة:**

Scenario A (exact duplicate): Owner already has `src_a3f2b1c4` (المغني, Shamela export from 2024). Owner downloads the same Shamela export again. SHA-256 of new files matches `src_a3f2b1c4`'s frozen hashes exactly. Result: `SRC_DUPLICATE_EXACT`. New file is not acquired. Log records the duplicate detection.

Scenario B (work-level match): Owner has `src_a3f2b1c4` (المغني, تحقيق عبد الله التركي). Owner uploads a PDF of المغني تحقيق محمد شرف الدين خطاب. SHA-256 differs (different file entirely). Work matching: title "المغني" + author "ابن قدامة" → matches existing `wrk_ibn_qudamah_mughni` with confidence 0.97. Result: `SRC_DUPLICATE_WORK` (info). New source acquired as `src_d7e8f9a0`, linked to the same `work_id`. Owner notified: "This is a different edition of المغني, which you already have as src_a3f2b1c4 (تحقيق التركي). Acquiring as a second source."

Scenario C (false negative risk): Two Shamela exports of the same edition but downloaded at different times may have minor HTML formatting differences → SHA-256 differs → not caught as exact duplicates. Work matching catches this as a work-level match. The owner is notified and can merge or keep both.

#### §4.A.8 — Trustworthiness Evaluation

The source engine assesses each source's reliability to determine the default verified/flagged classification for its excerpts.

**Evaluation factors** (weighted by importance):

1. **Author scholarly standing** (weight: 0.30). Is the author a recognized scholar in the relevant science? Major classical scholars (those in the scholar authority registry with high `scholarly_standing`) increase trust. Unknown or contemporary popular authors decrease it.

2. **Tahqiq quality** (weight: 0.25). Is the muhaqiq a recognized editor? The source engine maintains a configurable list of recognized muhaqiqs (initial list: شعيب الأرناؤوط، أحمد شاكر، عبد السلام هارون، عبد الله التركي، محمد فؤاد عبد الباقي، عبد القادر الأرناؤوط، محمد ناصر الدين الألباني). Recognized muhaqiqs score 0.90. Unknown muhaqiqs score 0.50 (neutral). No muhaqiq is scored 0.40 for pre-modern works (common and acceptable) or 0.30 for modern works (expected to have tahqiq). The recognized muhaqiqs list is stored in configuration and can be extended by the owner.

3. **Publisher reputation** (weight: 0.15). Known scholarly publishers (Dar al-Risalah, Mu'assasat al-Risalah, Dar al-Kutub al-'Ilmiyyah for specific titles) increase trust. Unknown publishers are neutral. Publishers known for low-quality commercial prints decrease trust.

4. **Source authority level** (weight: 0.15). Primary sources (مصدر أصلي) receive higher baseline trust than modern compilations (معاصر). Reference works (مراجع) are neutral.

5. **Text fidelity** (weight: 0.15). High-fidelity sources (structured digital text) increase trust. Low-fidelity sources (poor OCR, iPhone photos) decrease trust — not because the scholarly content is unreliable, but because transcription errors may corrupt the text.

**Trust tiers:**
- `verified`: combined score ≥ 0.65. Excerpts default to verified knowledge.
- `flagged`: combined score < 0.65, or any individual factor is critically low (e.g., unknown author with no muhaqiq and unknown publisher). Excerpts default to flagged knowledge. The flag reason is recorded.
- `owner_override`: the owner has manually set the trust tier, overriding the engine's evaluation. The original evaluation is preserved in metadata.

**Conservative bias (§7.4).** When the evaluation is genuinely uncertain (e.g., a recognized author but unknown publisher and no muhaqiq), the source is flagged. Flagging a reliable source is correctable; verifying an unreliable source contaminates the library.

**Special cases:**
- Owner-authored content is always `verified` — the owner is a trusted source. However, the source engine must still check three things before writing the metadata record:
  (1) If the content references a scholar by name, the source engine verifies the reference is consistent with the scholar authority registry (e.g., if the owner writes "قال ابن حجر العسقلاني" in a note tagged as Hanafi fiqh, the engine notes that Ibn Hajar al-Asqalani is a Shafi'i hadith scholar, and flags this as `SRC_METADATA_INCONSISTENCY` for the owner's awareness — not blocking, since the owner may be intentionally cross-referencing).
  (2) If the content is tagged with a specific science scope, the engine must ensure the scope is recognized.
  (3) If the content is a `tarjih` (scholarly preference conclusion), the engine must check that the sources referenced in the tarjih are in the library.
- Quran text from canonical digital sources is always `verified` with maximum trust.
- Hadith collections from the canonical Six Books (الكتب الستة: صحيح البخاري، صحيح مسلم، سنن أبي داود، سنن الترمذي، سنن النسائي، سنن ابن ماجه) and the Muwatta of Imam Malik are always `verified` when from recognized tahqiq editions.

**Trust re-evaluation on enrichment.** When an enrichment modifies any of the five trust evaluation input fields (`author.canonical_id` which determines author_standing, `muhaqiq` which determines tahqiq_quality, `publisher` which determines publisher_reputation, `authority_level`, or `text_fidelity`), the source engine automatically re-runs the trustworthiness evaluation algorithm using the updated values. If the new trust tier differs from the current tier: (a) if upgrading from `flagged` to `verified`, a human gate checkpoint is created for owner confirmation — upgrading trust is a higher-risk action than flagging. (b) if downgrading from `verified` to `flagged`, the change is applied immediately (conservative direction) and a stale-marking cascade is triggered on all excerpts derived from this source. The `trust_factors` array in the metadata record is updated to reflect the re-evaluation, and the old trust evaluation is preserved in `metadata_history`.

**Worked example — Trustworthiness evaluation for two contrasting sources:**

Source A: شرح ابن عقيل على ألفية ابن مالك, تحقيق محمد محيي الدين عبد الحميد, دار التراث, Shamela HTML.
- Author standing (0.30 weight): ابن عقيل is a recognized classical grammarian → score 0.90. Weighted: 0.270.
- Tahqiq quality (0.25 weight): محمد محيي الدين عبد الحميد is in the recognized muhaqiqs list → score 0.90. Weighted: 0.225.
- Publisher reputation (0.15 weight): دار التراث is a known scholarly publisher → score 0.70. Weighted: 0.105.
- Source authority (0.15 weight): Classical sharh → primary → score 0.85. Weighted: 0.128.
- Text fidelity (0.15 weight): Shamela structured HTML → score 0.90. Weighted: 0.135.
- Combined: 0.863 → `verified`.

Source B: "ملخص النحو الميسر" by unknown contemporary author, no muhaqiq, unknown publisher, iPhone photo scan.
- Author standing: unknown contemporary author → score 0.20. Weighted: 0.060.
- Tahqiq quality: no muhaqiq on a modern work → score 0.30. Weighted: 0.075.
- Publisher reputation: unknown → score 0.40. Weighted: 0.060.
- Source authority: modern compilation → score 0.40. Weighted: 0.060.
- Text fidelity: iPhone photos → score 0.30. Weighted: 0.045.
- Combined: 0.300 → `flagged`. Reason: "Unknown author, no tahqiq, low text fidelity from photos."

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

**Relationship discovery.** Relationships are discovered at intake through LLM inference from the title and genre classification. A title like "شرح ابن عقيل على ألفية ابن مالك" explicitly declares a sharh_of relationship. The LLM identifies the base work and attempts to link it to an existing work_id in the work registry.
If the base work is not in the library, a placeholder work record is created with `status: "referenced_not_acquired"`.
The engine must check the placeholder conforms to the WorkRegistryEntry model before persisting. The placeholder exists as a known work but has no source. This enables the citation network to grow even before all referenced works are acquired.

**Graph storage.** Relationships are stored in the work registry as edges: `{ "from": "wrk_...", "to": "wrk_...", "type": "sharh_of", "confidence": 0.95, "discovered_by": "source_engine" }`. The graph is queryable: "give me all commentaries on al-Ajurrumiyyah" returns a list of work_ids.

**Worked example — Relationship discovery for حاشية الصبان على شرح الأشموني على ألفية ابن مالك:**

Input: Source title = "حاشية الصبان على شرح الأشموني على ألفية ابن مالك".

LLM analysis of title:
1. "حاشية" → genre = `hashiyah`. This work is a hashiyah on something.
2. "على شرح الأشموني" → `hashiyah_on(this_work, wrk_ashmuni_sharh_alfiyyah)`. Base work: شرح الأشموني على ألفية ابن مالك.
3. The base work شرح الأشموني is itself a sharh → `sharh_of(wrk_ashmuni_sharh_alfiyyah, wrk_ibn_malik_alfiyyah)`.

Registry operations:
- Check for `wrk_ashmuni_sharh_alfiyyah`: not in registry → create placeholder with `status: "referenced_not_acquired"`.
- Check for `wrk_ibn_malik_alfiyyah`: already exists → link.
- Record edges: `hashiyah_on(wrk_sabban_hashiyah, wrk_ashmuni_sharh_alfiyyah)` confidence 0.97, `sharh_of(wrk_ashmuni_sharh_alfiyyah, wrk_ibn_malik_alfiyyah)` confidence 0.95.

Result: The work graph now shows a three-level chain: ألفية ابن مالك ← شرح الأشموني ← حاشية الصبان. The scholar interface can display: "This is a third-level commentary on the ألفية — the most advanced layer of the nahw curriculum."

#### §4.A.10 — Processing Status Tracking

Each source has a processing status that tracks its progress through the pipeline:

- `staging`: material is in the staging area, not yet processed.
- `acquired`: source engine has completed intake. Frozen files exist. Metadata record exists. Ready for normalization.
- `normalizing`: normalization engine is processing this source.
- `normalized`: normalization complete. Normalized package exists. Ready for passaging.
- `processing`: downstream Phase 2 engines are working on this source.
- `complete`: all engines have processed this source. Excerpts are placed. Entries generated.
- `error`: processing failed. The `error_detail` field specifies the stage (staging, acquisition, normalization, passaging, atomization, excerpting, or synthesis), the error code from that engine's error taxonomy, and the failure reason.
- `withdrawn`: source removed from active processing (owner decision or trust evaluation change). Frozen files and metadata preserved for audit.

Status transitions are logged with timestamps. The source engine owns `staging` → `acquired`. Other engines update status as they process. The source registry provides a dashboard view: the count of sources at each stage, which are blocked, and what errors exist.

**Worked example — Status transitions for src_a7c3e91f (شرح ابن عقيل):**

Input: Source شرح ابن عقيل placed in staging directory at 10:00:00Z.
Output: Complete processing timeline with timestamps at each stage:

```
2026-03-06T10:00:00Z  staging    → source placed in library/staging/
2026-03-06T10:00:12Z  acquired   → source engine intake complete, frozen files written, metadata.json written
2026-03-06T10:05:00Z  normalizing → normalization engine picks up source
2026-03-06T10:08:30Z  normalized  → normalized package written
2026-03-06T10:09:00Z  processing  → passaging engine begins
2026-03-07T02:15:00Z  complete    → all engines have processed, excerpts placed, entries generated
```

Error case: If normalization fails mid-processing:
```
2026-03-06T10:07:22Z  error      → error_detail: "normalization/NORM_STRUCTURE_FAILED: unable to detect chapter boundaries in volume 2"
```
The source remains in `error` status. The dashboard shows it as blocked. The owner or architect investigates the normalization failure. The source can be retried after the issue is resolved — frozen files and metadata are intact.

### §4.B — Transformative Capabilities

#### §4.B.1 — External Metadata Enrichment via OpenITI Corpus

**Capability:** When the source engine identifies a work during intake, it queries the OpenITI corpus metadata to enrich the scholar authority record and work record with data from the largest machine-actionable corpus of premodern Islamicate texts.

**Technical approach:** OpenITI organizes texts using CTS-compliant URIs that encode author death date and author/work slugs (e.g., `0505Ghazali.IhyaCulumDin`). The source engine maintains a local copy of the OpenITI metadata CSV (available from their GitHub releases) and queries it during intake. Matching uses normalized author name + approximate death date. When a match is found, the source engine extracts: confirmed death date, the set of other known works by this author in OpenITI, and any annotated metadata from the OpenITI YML files.

**What this enables:** A scholar authority record initially populated only from a title page ("الغزالي") is immediately enriched with: death date (505 AH), the full list of known works as catalogued in OpenITI (إحياء علوم الدين، تهافت الفلاسفة، المستصفى، المنقذ من الضلال, and all other works in the corpus), and the CTS URIs that link to the OpenITI corpus. This bootstrapping means the synthesizer has rich biographical data from the very first source, not just after dozens of sources have been processed.

**Integration:** The enrichment is recorded as `record_source: "openiti_metadata"` in the scholar authority record. OpenITI data does not override owner-provided or source-extracted data — it supplements. Conflicts are flagged for owner review.

**Dependencies:** Requires downloading and locally caching the OpenITI metadata CSV (~50MB). The KITAB corpus metadata search application provides the data. Update frequency: quarterly, matching OpenITI's release cycle.

**Integrity verification.** Before the cached OpenITI CSV is used for enrichment, the engine verifies: (1) expected CSV column headers match the known schema, (2) spot-check 5 well-known scholars whose death dates and work counts are historically certain (configurable in `library/config/openiti_validation_samples.json`, initial entries: Sibawayhi d.180, Bukhari d.256, Ghazali d.505, Nawawi d.676, Ibn Taymiyyah d.728), (3) the file's SHA-256 hash matches the stored hash in `library/external/openiti_metadata/manifest.json`. If any verification step fails, the file is discarded with `SRC_OPENITI_CACHE_CORRUPT` (severity: Warning) and enrichment falls back to LLM-only inference. Death dates sourced solely from OpenITI (no corroboration from Usul-Data, Wikidata, source text, or LLM inference) carry a maximum confidence of 0.90 — excellent but not infallible.

**Worked example — OpenITI enrichment for ابن قدامة:**

Input: New scholar record `sch_00042` created during intake of المغني. Known data: name = "ابن قدامة المقدسي", death_date_hijri = 620.
OpenITI query: Search metadata CSV for authors with death date 620 ± 10 years and name containing "qudama" → match: `0620IbnQudworka` (confidence 0.95).
OpenITI data extracted: 7 known works in corpus (المغني، الكافي، المقنع، العمدة، روضة الناظر، لمعة الاعتقاد، ذم التأويل). Death date confirmed: 620 AH.
Scholar record updated: `known_works` populated with 7 work_ids (creating placeholder work records for any not yet in library). `record_sources` updated to include `"openiti_metadata"`. `record_completeness` increased from 0.45 → 0.72.
The engine must check all updated entries against their Pydantic models before persisting.

#### §4.B.2 — Bibliographic Intelligence from Minimal Input

**Capability:** Given only a title and author name — or even just a photograph of a title page — the source engine produces a comprehensive scholarly profile of the work and author that approaches what a human bibliographer would produce after hours of research.

**Technical approach:** The source engine sends the extracted title + author + any available metadata to an LLM with a specialized bibliographic prompt that instructs the model to: identify the work in the Islamic scholarly tradition, determine its genre and genre chain (is it a commentary on something? an abridgment?), identify the author with biographical details, assess the work's scholarly standing and its place in the classical curriculum, identify what sciences it covers and at what level, and determine known editions and their relative quality.

The LLM's training data includes substantial knowledge of the Islamic scholarly corpus — major works, major scholars, genre relationships, and curricular traditions are well-represented. This inference is not guesswork: for well-known works (which constitute the majority of what the owner will acquire first), the LLM produces highly accurate bibliographic profiles.

**What this enables:** Scenario 6 (New Book Briefing) becomes possible from intake alone. When the owner photographs حاشية ابن عابدين's title page, the source engine — before any content processing — can produce: "This is رد المحتار على الدر المختار, a hashiyah on الدر المختار (sharh of تنوير الأبصار). Author: ابن عابدين (d. 1252 AH). Hanafi fiqh. Advanced specialist level. The primary reference work of late Hanafi scholarship." This profile is stored as source metadata and serves as the foundation for the scholar interface's full book briefing.

**Confidence and verification:** The bibliographic profile carries per-field confidence scores. For well-known works and scholars, confidence is typically > 0.90. For obscure works or ambiguous authors, confidence drops and a human gate checkpoint is created. Multi-model consensus is used for author identification (the field with highest cascade risk).

**Limitations:** LLM training knowledge is not exhaustive. Very obscure works, regional scholars not widely discussed in available training data, and recently published contemporary works may have low-confidence or inaccurate profiles. The system is designed to be honest about uncertainty — a low-confidence field is flagged, not guessed at.

**Worked example — Bibliographic inference from iPhone photo:**

Input: OCR of title page photo → title: "الورقات" (confidence 0.92), author: "إمام الحرمين" (confidence 0.85). No other metadata available.
LLM inference output:
- Full identification: الورقات في أصول الفقه, by إمام الحرمين أبو المعالي عبد الملك الجويني (d. 478 AH). Confidence: 0.96.
- Genre: `matn` (0.95). Genre_chain: null (this is a standalone matn).
- Science_scope: `["usul_al_fiqh"]` (0.98).
- Level: `beginner` (0.92) — a foundational primer, traditionally the first usul text studied.
- Structural_format: `prose` (0.90).
- Source_authority: `primary` (0.94).
- Scholarly standing: "One of the most widely taught introductory texts in usul al-fiqh. Has over 20 commentaries including شرح المحلي and شرح الفوزان."
- Author disambiguation: "إمام الحرمين" uniquely refers to الجويني — no ambiguity. Consensus not triggered.

#### §4.B.3 — Citation Network Discovery

**Capability:** When the source engine processes a new source and downstream engines (particularly the excerpting engine) identify textual references to other works, the source engine receives discovery requests and builds a citation graph across the entire library — including references to works not yet acquired.

**Technical approach:** The excerpting engine, during its processing, detects patterns like "قال ابن قدامة في المغني" (Ibn Qudamah said in al-Mughni) or "ذكر في المغني" (it was mentioned in al-Mughni). It sends a citation discovery request to the source engine containing: the referenced author name (normalized), the referenced work title (normalized), and the citing excerpt ID.

The source engine queries the work registry for a match. Three outcomes:
1. **Work exists in library:** Record the citation relationship (`cites(citing_work, cited_work)`) and link the citing excerpt to the cited work_id.
2. **Work exists as a placeholder** (previously referenced but not acquired): Add another citation to the existing placeholder. The citation count on placeholder works serves as an acquisition priority signal — a work cited by 50 excerpts across 10 sources is more important to acquire than one cited once.
3. **Work is new:** Create a placeholder work record with `status: "referenced_not_acquired"`. If autonomous discovery is enabled, trigger a search in configured repositories with priority `citation_discovered`.

**What this enables:** Over time, the library develops a citation graph that reveals: which works are most influential (most cited), which scholarly conversations span two or more works (mutual citation chains), and which unacquired works would most enrich the library (highest citation count among placeholders). The scholar interface can show: "al-Mughni is cited by 47 excerpts across 12 sources in your library — it's the most-referenced unacquired work. Shall I find it?"

[NOT YET IMPLEMENTED] — Full specification provided above. Depends on: excerpting engine's reference detection capability and repository search interface modules.

**Worked example — Citation discovery from شرح ابن عقيل:**

Input: The excerpting engine processes شرح ابن عقيل (src_a7c3e91f) and detects in excerpt #347 the text "قال ابن مالك في التسهيل" (Ibn Malik said in al-Tashil). Citation discovery request: referenced_author = "ابن مالك", referenced_title = "التسهيل", citing_excerpt_id = "exc_347_a7c3e91f".

Source engine processing:
1. Work registry query: search for work by ابن مالك with title matching "التسهيل" → match: `wrk_ibn_malik_tashil` exists as placeholder (status: "referenced_not_acquired", created when the الألفية was processed and its relationship chain was traced).
2. Record citation: `cites(wrk_ibn_aqil_sharh_alfiyyah, wrk_ibn_malik_tashil)`, citing_excerpt = "exc_347_a7c3e91f".
3. Update placeholder: `wrk_ibn_malik_tashil.citation_count` incremented (now 12 citations across 4 sources).
4. No acquisition triggered (autonomous discovery not yet enabled).

Dashboard shows: "تسهيل الفوائد by ابن مالك — referenced 12 times across 4 sources, not yet in library."

#### §4.B.4 — Acquisition Gap Analysis

**Capability:** The source engine analyzes the library's current coverage and proactively identifies what sources would most improve scholarship across all dimensions: school coverage, science coverage, temporal coverage, and curricular completeness.

**Technical approach:** The source engine periodically (or on demand) computes a gap analysis by querying: (1) the taxonomy engine's coverage metrics (which leaves have thin school coverage), (2) the work registry's citation placeholders (which unacquired works are most referenced), (3) the scholar authority model's known works lists (which works by scholars already in the library are not yet acquired), and (4) classical curricular knowledge from its LLM capability (which works are considered essential for each science at each level).

The gap analysis produces a ranked acquisition priority list:
- "Your library has 0 Maliki sources on inheritance law (المواريث). Recommended: شرح الرحبية by السبط المارديني — available on Shamela."
- "ابن قدامة's المغني is referenced 47 times but not in your library. It's the primary Hanbali fiqh reference."
- "You have 3 beginner nahw sources but no intermediate ones. Recommended next: قطر الندى by ابن هشام."

**What this enables:** The library grows strategically rather than haphazardly. The owner doesn't have to know what books exist — KR tells him what he needs. This is how KR fills the role of scholarly guide (Scenario 1's curriculum design depends on the source engine knowing what's available and what's missing).

[NOT YET IMPLEMENTED] — Specification provided above. Depends on: taxonomy engine coverage metrics, work registry with citation counts, and repository search interface modules.

**Worked example — Gap analysis output:**

Library state: 15 sources, 12 works, sciences covered = [nahw (8 works), fiqh (3 works), usul_al_fiqh (1 work)].
Owner study focus: Hanbali fiqh, intermediate level.

Gap analysis output (ranked by priority):
1. **Citation priority:** "المغني by ابن قدامة — referenced 47 times across 8 sources but not in your library. It is the primary Hanbali comparative fiqh reference. Priority: CRITICAL." (Source: citation placeholder with highest count.)
2. **School coverage:** "Your library has 3 fiqh sources, all Hanbali. No Shafi'i, Maliki, or Hanafi fiqh source is present. For comparative study, recommended: المجموع شرح المهذب (Shafi'i), بداية المجتهد (comparative)." (Source: taxonomy coverage metrics.)
3. **Curricular gap:** "You have 2 beginner nahw sources and 3 advanced nahw sources but no intermediate. The standard curriculum sequence is: الآجرومية → قطر الندى → ألفية ابن مالك. قطر الندى is missing." (Source: LLM curricular knowledge + library inventory.)
4. **Author completeness:** "ابن قدامة is in your scholar registry with 7 known works. You have 0 of them. His المقنع and العمدة are foundational Hanbali matn texts." (Source: scholar authority registry known_works.)

#### §4.B.5 — KITAB Text Reuse Integration for Source Compositional Profiling

**Capability:** When a new source enters the library, the source engine queries the KITAB project's pre-computed text reuse dataset — which documents verbatim textual overlap between 4,300+ premodern Arabic works — to produce a "compositional profile" showing how this work relates to the entire classical Arabic corpus: what it borrows, who borrows from it, and how original its content is.

**Technology:** KITAB text reuse statistics CSV files (released on Zenodo, DOI: 10.5281/zenodo.4362369, latest release 2023.1.8+). Each CSV contains pairwise alignment data: book pairs, percentage of text shared, number of shared words, directionality. The source engine downloads and caches the statistics dataset (~1GB bidirectional, updated annually). Matching between KR sources and KITAB/OpenITI books uses the OpenITI CTS URN system (already leveraged in §4.B.1) — a source identified as al-Mughni by Ibn Qudamah maps to OpenITI URI `0620IbnQudworka.Mughni.*`.

**Input:** A source_id for a source whose work has been identified (author canonical_id resolved, work_id assigned). The source engine looks up this work in the local KITAB statistics cache using the OpenITI URI derived from the author's death date and the work's title slug.

**Output:** A `compositional_profile` record appended to the source metadata, containing:

```json
{
  "kitab_uri_match": "0620IbnQudworka.Mughni.Shamela0010803-ara1",
  "kitab_match_confidence": 0.95,
  "intertextual_metrics": {
    "reuse_as_source_count": 47,
    "reuse_as_source_top_5": [
      {"work": "0676Nawawi.MajmucSharh", "shared_words": 85420, "pct_of_target": 0.12},
      {"work": "0852IbnHaworkar.FathBari", "shared_words": 42100, "pct_of_target": 0.04},
      {"work": "0774IbnKathworkar.Bidaya", "shared_words": 31200, "pct_of_target": 0.03}
    ],
    "reuse_from_source_count": 12,
    "reuse_from_source_top_5": [
      {"work": "0204Shafici.Umm", "shared_words": 22300, "pct_of_this": 0.02}
    ],
    "originality_estimate": 0.89,
    "network_centrality_rank": 23
  }
}
```

**Concrete example with Arabic text:** When Rayane acquires المغني by ابن قدامة, the source engine reports: "المغني shares text with 47 later works — it is the 23rd most-cited work in the entire OpenITI corpus of 4,300+ Arabic texts. النووي's المجموع شرح المهذب borrows 85,420 words (12% of المجموع). ابن حجر's فتح الباري borrows 42,100 words. المغني itself borrows from الأم by الشافعي (22,300 words). 89% of المغني's text is original (not found verbatim in earlier works). This places it as a foundational fiqh text that created new scholarly content rather than compiling from predecessors."

**Scholar impact:** Before Rayane reads a single page, he knows the work's place in the entire classical Arabic scholarly network — which authors relied on it, which earlier works it drew from, and how original its contribution was. No Islamic studies student has ever had this view. A senior scholar might know from years of reading that al-Nawawi quotes al-Mughni frequently — but they cannot quantify "85,420 shared words across 12% of al-Majmu'" or rank originality across 4,300 texts.

**Implementation sketch:** At intake time (after work identification in Step 4 of §4.A.2), the source engine constructs the OpenITI URI from the author's death date (from scholar authority record) and the work's title slug (transliterated). It queries the local KITAB statistics cache for all pairwise records where this URI appears as either book1 or book2. It computes: (1) the count of other works sharing text with this source (reuse_as_source_count for later works, reuse_from_source_count for earlier works), (2) the top 5 in each direction sorted by shared word count, (3) an originality estimate = 1 - (sum of all text reused FROM earlier works / total word count), (4) network centrality as the rank of total shared words among all books in the dataset. If no KITAB match is found (obscure work or different edition), the profile records `kitab_match_confidence: 0.0` and the field is left for future enrichment.

**Failure handling:** If the KITAB statistics cache is missing or outdated, the source engine logs `SRC_KITAB_CACHE_MISSING` (severity: info) and skips this enrichment — it is not required for intake. If the work matches but with confidence below 0.70 (the OpenITI URI does not uniquely resolve — the same work may have variant editions in OpenITI), the engine records all candidate matches and uses the one with the longest text as the primary match.

**Dependencies:** Requires downloading KITAB statistics CSV (~1GB) from Zenodo. The cache is stored at the path configured in `kitab_stats_path` (default: `library/external/kitab_stats/`). The engine records the file's SHA-256 hash in `library/external/kitab_stats/manifest.json`.

Before the cache is used, the engine verifies integrity: (1) checks that the file is valid CSV with expected column headers (book1, book2, shared_words, pct_of_book1, pct_of_book2), (2) spot-checks 3 known entries (configurable in `library/config/kitab_validation_samples.json`) to confirm data integrity, (3) confirms the stored hash matches the file on disk. If verification fails, the download is discarded and `SRC_KITAB_CACHE_CORRUPT` is logged. Update frequency: annually, matching OpenITI release cycle. This enrichment is additive — it never blocks intake. Depends on: §4.B.1's OpenITI URI matching logic.

[NOT YET IMPLEMENTED] — Full specification provided. No code exists. Depends on: OpenITI URI matching from §4.B.1, local KITAB statistics cache download.

#### §4.B.6 — Edition Comparison Intelligence

**Capability:** When the library contains two or more sources (editions) of the same work, the source engine automatically detects substantive differences between editions and produces a structured comparison that identifies which edition is more complete, more accurate, and better tahqiq'd — and WHERE they diverge.

**Technology:** Text comparison uses a two-phase approach: (1) character-level diff via Python's `difflib.SequenceMatcher` (stdlib, no external dependency) on the normalized text of both editions to identify divergence regions, (2) LLM analysis of each divergence region to classify it as: `tahqiq_correction` (the muhaqiq fixed a scribal error), `variant_reading` (legitimate textual variant from different manuscript traditions), `ocr_artifact` (a difference caused by OCR quality rather than actual textual difference), `editorial_addition` (footnote, commentary, or apparatus not in the other edition), or `structural_difference` (different chapter ordering, included/excluded sections). The normalization engine provides the normalized text; this capability operates after both editions have been normalized.

**Input:** Two or more source_ids that share the same work_id (detected automatically when a second edition is acquired). The source engine retrieves the normalized text for each edition from the normalization engine's output.

**Output:** An `edition_comparison` record stored at `library/sources/{work_id}/edition_comparison.json`, containing:

```json
{
  "work_id": "wrk_ibn_qudamah_mughni",
  "editions_compared": ["src_a3f2b1c4", "src_d7e8f9a0"],
  "comparison_timestamp": "2026-03-06T12:00:00Z",
  "summary": {
    "total_divergence_regions": 342,
    "by_type": {
      "tahqiq_correction": 89,
      "variant_reading": 41,
      "ocr_artifact": 187,
      "editorial_addition": 22,
      "structural_difference": 3
    },
    "preferred_edition_recommendation": "src_a3f2b1c4",
    "preference_reason": "187 fewer OCR artifacts; muhaqiq (عبد الله التركي) is recognized for rigorous tahqiq; 22 additional editorial footnotes providing hadith takhrij"
  },
  "sample_divergences": [
    {
      "location": {"volume": 3, "page_approx": 412},
      "edition_a_text": "وقال أحمد في رواية المروذي",
      "edition_b_text": "وقال أحمد في رواية المروزي",
      "type": "variant_reading",
      "analysis": "المروذي vs المروزي — both are attested nisbas for أبو بكر أحمد بن محمد المروذي. Edition A uses the more common scholarly convention."
    }
  ]
}
```

**Concrete example with Arabic text:** Rayane has two Shamela editions of المغني. The source engine reports: "Compared 2 editions of المغني (src_a3f2b1c4: تحقيق عبد الله التركي, src_d7e8f9a0: تحقيق محمد شرف الدين). Found 342 divergence regions. 187 are OCR artifacts in the شرف الدين edition (lower text fidelity from Shamela scan quality). 89 are tahqiq corrections where التركي fixed scribal errors with manuscript evidence noted in footnotes. 41 are genuine variant readings from different manuscript traditions. Recommendation: التركي edition is preferred (fewer errors, better apparatus). However, the شرف الدين edition includes 3 additional chapters on المناسك that the التركي edition places in a separate volume."

**Scholar impact:** Rayane can make an informed edition choice — not based on reputation alone (which is how most students choose) but on quantified evidence. When he encounters a passage and wonders "is this text reliable?", the comparison tells him exactly where the editions diverge and why. No tool currently provides this — scholars who want to compare editions must read them in parallel, page by page.

**Implementation sketch:** When the source engine registers a new source and links it to an existing work_id that already has one or more sources, it enqueues an edition comparison job. The job waits until both editions have been normalized (status ≥ `normalized`). The comparison then: (1) aligns the normalized text of both editions by chapter/section structure, (2) runs character-level diff on each aligned section to identify divergence regions, (3) filters out divergences shorter than 3 characters (trivial whitespace/punctuation differences), (4) sends each non-trivial divergence region (the text from both editions plus 200 characters of surrounding context) to the LLM for classification, (5) aggregates the classifications into the summary statistics, (6) determines edition preference based on: fewer OCR artifacts, recognized muhaqiq, presence of scholarly apparatus. Multi-model consensus is NOT required because the comparison is non-destructive — it adds advisory metadata but does not change any source's trust tier or content.

**Failure handling:** If normalized text is not yet available for one or both editions, the comparison is deferred (logged as `SRC_COMPARISON_DEFERRED`). If the editions are so different in structure that chapter-level alignment fails (e.g., one edition is a 10-volume set and the other is a 15-volume set with different chapter boundaries), the engine falls back to whole-text alignment using the passim approach (300-word chunks). **Alignment sufficiency threshold:** If fewer than 20% of 300-word chunks from the shorter edition align with any chunk in the longer edition (alignment defined as SequenceMatcher ratio ≥ 0.60), the comparison is classified as `inconclusive` with reason `"editions_structurally_incomparable"` and logged as `SRC_COMPARISON_INCONCLUSIVE`. No preferred edition recommendation is produced — `preferred_edition_recommendation` is set to null and `preference_reason` reads: "Editions are too structurally divergent for automated comparison ({pct}% alignment). Manual review recommended." The owner is notified via a human gate checkpoint. Very large works (>500,000 words per edition) are compared in batches of 50,000 words to manage LLM context limits.

**Constraints:** This capability is advisory only. It produces a recommendation but does not automatically change the `preferred_source_id` on the work registry — that requires owner confirmation through a human gate checkpoint. The comparison metadata is shared with the excerpting engine: when an excerpt is drawn from a divergence region, the excerpting engine can note "this passage has a variant reading in the other edition."

[NOT YET IMPLEMENTED] — Full specification provided. No code exists. Depends on: normalization engine output, work registry tracking of source_ids per work_id. Triggered automatically on second-edition acquisition.

#### §4.B.7 — Scholarly Genealogy Auto-Construction

**Capability:** For every scholar encountered, the source engine automatically constructs a multi-generational teacher-student chain (silsila 'ilmiyya) by combining three data sources: (1) explicit teacher/student data from the scholar authority record, (2) OpenITI corpus metadata cross-references, and (3) LLM inference from the training knowledge of major Islamic biographical dictionaries (tabaqat). The result is a connected knowledge graph where Rayane can trace intellectual lineage across centuries.

**Technology:** Graph construction uses a combination of: the scholar authority registry as the primary store (§4.A.5), OpenITI author metadata as a bootstrapping source (§4.B.1), and LLM-assisted biographical inference using specialized prompts that instruct the model to recall teacher-student relationships from its training on works like سير أعلام النبلاء by الذهبي, طبقات الشافعية by السبكي, and الأعلام by الزركلي. The graph is stored as adjacency lists in the scholar authority registry (the existing `teachers` and `students` fields).

Before writing any teacher-student link, the engine must verify and check: (1) no self-referencing (a scholar cannot be their own teacher), (2) temporal plausibility (§4.A.5 consistency checks apply), (3) the ScholarAuthorityRecord Pydantic model passes §5 Layer 1 validation after the update. Graph analysis uses NetworkX (Python, BSD license, v3.2+) for centrality computation, path finding, and community detection.

**Input:** A scholar `canonical_id` — either newly created during intake or an existing record being enriched during progressive enrichment. The trigger is: (1) a new scholar record is created with empty `teachers`/`students` fields, or (2) a new source adds previously unknown biographical data about an existing scholar.

**Output:** Updated scholar authority records with populated `teachers` and `students` fields (as lists of `canonical_id` references), plus a `genealogy_metadata` record per scholar:

```json
{
  "canonical_id": "sch_00312",
  "genealogy_chain_upward": ["sch_00198", "sch_00155", "sch_00089"],
  "genealogy_chain_upward_names": ["ابن مالك", "ابن الحاجب", "الزمخشري"],
  "chain_confidence": 0.88,
  "chain_sources": ["llm_inference:siyar_alam", "openiti_metadata", "source_text:src_a3f2b1c4"],
  "scholarly_generation": 7,
  "genealogy_community": "basri_nahw_late",
  "centrality_score": 0.34,
  "bridges_to_communities": ["kufi_nahw", "shafii_fiqh"]
}
```

**Concrete example with Arabic text:** When the source engine processes شرح ابن عقيل على ألفية ابن مالك and creates a record for ابن عقيل (d. 769 AH), the engine:

1. Creates scholar record for ابن عقيل with death date 769 AH.
2. Queries OpenITI metadata: finds `0769IbnCaqworkkil` with known works list.
3. LLM inference prompt: "ابن عقيل بهاء الدين عبد الله الهمداني المصري (ت ٧٦٩ هـ). من هم أشهر شيوخه وتلاميذه في النحو والفقه؟" (Who are his most notable teachers and students in grammar and fiqh?)
4. LLM returns: Teachers include أبو حيان الأندلسي (d. 745 AH, sch_00287) and ابن جماعة (d. 767 AH). Students include بهرام الدميري (d. 805 AH).
5. The engine checks if أبو حيان is already in the registry. If yes, links bidirectionally. If no, creates a new scholar record for أبو حيان and populates it.
6. Traces upward from أبو حيان: his teacher was ابن النحاس (via OpenITI), whose teacher was ابن عصفور (d. 669 AH), whose teacher was ابن خروف (d. 609 AH) — a chain that reaches back to Sibawayhi within 6-8 generations.
7. Computes: ابن عقيل is in the "Egyptian Shafi'i nahw" community, with bridges to the Andalusian grammar tradition (through أبو حيان) and Hanbali fiqh (through his own fiqh teaching).

**Scholar impact:** When the synthesizer produces the entry on المبتدأ (as shown in ENTRY_EXAMPLE.md), it can now generate: "ابن عقيل (d. 769 AH), a student of أبو حيان الأندلسي who studied with ابن النحاس in the tradition descending from ابن مالك himself, explains that..." — the four-generation chain from Sibawayhi to Ibn al-Sarraj in the ENTRY_EXAMPLE is precisely what this capability produces AUTOMATICALLY. Without it, producing such chains requires the synthesizer to have training knowledge of Islamic biographical literature. With it, the chains are verified data in the scholar authority registry.

**Implementation sketch:** When a new scholar record is created with empty genealogy, the engine:
1. Queries OpenITI metadata for the author (using §4.B.1's matching logic). Extracts any teacher/student relationships encoded in the corpus metadata.
2. Sends a biographical inference prompt to the LLM: provides the scholar's name, death date, known works, school affiliations, and geographic activity. Asks for: (a) up to 5 known teachers with their names, death dates, and the science studied under them, (b) up to 5 known students with the same data. The prompt specifies: "Cite the biographical source for each relationship (e.g., 'ذكره الذهبي في السير' or 'ذكره السبكي في الطبقات')."
3. For each teacher/student returned, the engine checks the scholar authority registry for an existing match (using §4.A.5's matching logic). If found, creates bidirectional links. If not found, creates a stub record with the biographical data provided.
4. Multi-model consensus is used for this inference — two LLMs independently produce the teacher/student list. Only relationships that both models agree on are auto-accepted. Relationships claimed by only one model are flagged with `genealogy_confidence: "single_model"` and accepted provisionally.
5. After individual chain construction, NetworkX computes: (a) the shortest path length from each scholar to the earliest scholar in the registry (the "scholarly generation" number), (b) betweenness centrality (scholars who bridge between different intellectual communities), (c) community detection using the Louvain algorithm to identify scholarly clusters (e.g., "Basran nahw," "Hanbali fiqh," "Shafi'i usul").

**Depth limit:** Chain construction traces up to 4 generations upward and 2 generations downward from the trigger scholar. Beyond this, the diminishing confidence of LLM inference makes the data unreliable. Deeper chains build naturally as more sources are processed — each new source may add a scholar who extends an existing chain by one generation.

**LLM-only provenance limit:** Genealogy links supported ONLY by LLM inference (no corroboration from OpenITI, Usul-Data, Wikidata, or source text) receive a maximum confidence of 0.70 (regardless of LLM-reported confidence) and are tagged with `link_provenance: "llm_only"`. Links corroborated by at least one structured source receive confidence up to 0.90 and are tagged `link_provenance: "{source}_corroborated"`. Links confirmed by two or more structured sources receive confidence up to 0.95. The synthesizer uses link_provenance to qualify biographical claims in entries: corroborated links are stated as fact; LLM-only links are qualified with "attributed by scholarly tradition" or similar hedging.

**Failure handling:** If the LLM returns a teacher/student with an ambiguous name (e.g., "ابن حجر" without clarification), the engine does NOT create a link — it creates a `genealogy_ambiguous` flag on the scholar record with the unresolved name, for human gate review. If OpenITI metadata contradicts LLM inference (different death date for a teacher), the OpenITI data is preferred (it is more likely to be manually verified) and the discrepancy is logged.

[NOT YET IMPLEMENTED] — Full specification provided. No code exists. Depends on: §4.B.1's OpenITI matching, §4.A.5's scholar authority model, NetworkX library. Builds progressively — quality improves with each new source processed.

#### §4.B.8 — Cross-Validated Scholar Authority Bootstrapping via Usul-Data and Wikidata

**Capability:** When the source engine creates or enriches a scholar authority record, it queries not only OpenITI (§4.B.1) but also two additional structured datasets — Usul-Data (seemorg/usul-data, MIT license) and Wikidata (CC0) — and cross-validates across all three to produce scholar records with higher confidence than any single source can provide. Disagreements between sources are surfaced as research signals rather than discarded.

**Technology:** Usul-Data (`authors.json`, MIT license, ~50MB) provides: multilingual scholar names in 14 languages (Arabic, English, Persian, Urdu, Turkish, French, German, Indonesian, Malay, Bengali, Russian, Chinese, Spanish, and Japanese — the complete set as of the current Usul-Data schema), death dates (Hijri year), biographical descriptions, and author-book relationships linking to the Usul.ai book catalog. Wikidata provides: structured biographical data queryable via SPARQL endpoint (`query.wikidata.org`), including properties P1066 (student of), P802 (student), P569/P570 (birth/death dates), P140 (religion), school affiliations, and geographic data. Wikidata items for Islamic scholars are identifiable via occupation Q13200659 (Islamic scholar) or related classes.

**Input:** A scholar `canonical_id` — newly created or being enriched. The engine extracts the scholar's Arabic name, any known aliases, and death date (if available) from the scholar authority record.

**Output:** An enriched scholar authority record with `record_sources` including `"usul_data"` and/or `"wikidata"` alongside existing sources. For each field populated from these sources, the origin is recorded in `record_sources`. Cross-validation results are stored in a `cross_validation` field:

```json
{
  "canonical_id": "sch_00042",
  "cross_validation": {
    "death_date_agreement": {
      "openiti": 620,
      "usul_data": 620,
      "wikidata": 620,
      "status": "unanimous",
      "confidence_boost": 0.15
    },
    "known_works_union": {
      "openiti_only": ["wrk_ibn_qudamah_rawda"],
      "usul_data_only": ["wrk_ibn_qudamah_umda"],
      "wikidata_only": [],
      "all_three": ["wrk_ibn_qudamah_mughni", "wrk_ibn_qudamah_kafi", "wrk_ibn_qudamah_muqni"],
      "total_unique_works": 12
    },
    "teacher_student_wikidata": {
      "teachers_from_wikidata": ["sch_00089"],
      "students_from_wikidata": ["sch_00123"],
      "novel_links": 2
    },
    "discrepancies": []
  }
}
```

**Cross-validation logic:**

1. **Death date triangulation.** If all three sources agree on death date (within ±2 years for Hijri), confidence is boosted by 0.15 (capped at 0.99). If two agree and one disagrees, the majority value is used and the discrepancy is logged. If all three disagree, a human gate checkpoint is created with all three values and their sources.

2. **Known works union.** The engine takes the UNION of all works attributed to this scholar across all three sources. Works found in all three sources receive the highest confidence. Works found in only one source receive lower confidence and are marked `needs_verification`. This union directly feeds the gap analysis (§4.B.4) — a work attributed to a scholar in KR's registry but not yet in the library is a candidate for acquisition. **Zero-overlap detection:** If Wikidata returns a candidate match where NONE of its known works overlap with works from OpenITI or Usul-Data (zero intersection), the match is flagged as `wikidata_match_suspect` and a human gate checkpoint is created. The Wikidata data is NOT merged into the scholar record until the owner confirms the match — this catches cases where Wikidata resolved to a different scholar with a similar name and date.

3. **Teacher-student links from Wikidata.** Wikidata's P1066/P802 properties provide teacher-student relationships that may not be in OpenITI metadata or LLM inference. These are added to the scholar authority record with `source: "wikidata"`. Links found in both Wikidata AND LLM inference receive higher confidence than either alone.

4. **Multilingual name variants from Usul-Data.** The 14-language transliterations in Usul-Data provide name variants that improve future scholar matching — when the excerpting engine encounters a scholar name in a non-Arabic context (e.g., an Ottoman Turkish commentary), the multilingual variants help resolve the reference.

**Concrete example with Arabic text:** When the source engine processes المغني by ابن قدامة and creates scholar record `sch_00042`:
- OpenITI returns: death date 620, 7 known works, CTS URI `0620IbnQudworka`.
- Usul-Data returns: `{"year": 620, "primaryNameTranslations": [{"locale": "ar", "text": "ابن قدامة المقدسي"}, {"locale": "en", "text": "Ibn Qudama al-Maqdisi"}, ...], "id": "0620IbnQudworka"}`, plus 9 linked books in the Usul catalog.
- Wikidata SPARQL returns: Q315581, death date 1223 CE (= 620 AH confirmed), P1066 (student of) → Q6840279 (Abu al-Fath ibn al-Manni), P802 (student) → Q19863061 (Ibn Taymiyyah's grandfather), geographic_origin: نابلس.
- Cross-validation: death date unanimous (620 AH), 12 unique known works from union, 2 novel teacher-student links from Wikidata not in LLM inference, Arabic/English/Persian name variants from Usul-Data.

**Scholar impact:** The scholar authority record for Ibn Qudamah is now richer than what any single source provides. The synthesizer can produce: "ابن قدامة المقدسي (d. 620 AH), originally from Nablus, studied under أبو الفتح ابن المنّي in Baghdad..." — biographical detail confirmed across three independent sources, not inferred from a single LLM call.

**Implementation sketch:**
1. Usul-Data: download `authors.json` from GitHub (`https://raw.githubusercontent.com/seemorg/usul-data/main/authors.json`). Cache locally at `library/external/usul_data/authors.json`. Matching uses: normalized Arabic name comparison (using the same CAMeL Tools normalization applied in §4.A.5 scholar matching — strip diacritics, normalize hamza/taa marbuta, normalize alef variants) against `primaryNameTranslations[locale=ar].text` + death year comparison against `year` field. If the usul-data ID follows the OpenITI URI pattern (e.g., `0620IbnQudworka`), use exact URI match (highest confidence).
2. Wikidata: SPARQL query via HTTP GET to `query.wikidata.org/sparql`. Query template: find items with label matching the scholar's Arabic name AND death date within ±10 years of the known Hijri date (converted to CE). For matched items, fetch: P569, P570, P1066, P802, P27 (country of citizenship), sitelinks. Rate limit: max 5 queries per second (Wikidata policy). If rate-limited (HTTP 429), back off exponentially starting at 2 seconds, up to 3 retries. Cache query results for 30 days.
3. Cross-validation runs after all three sources return. Results stored atomically with the scholar record update.

**Failure handling:** If Usul-Data file is missing → log `SRC_USUL_DATA_MISSING` (info), skip this enrichment. If Wikidata query times out or returns no results → log `SRC_WIKIDATA_TIMEOUT` (info), proceed without Wikidata data. If Wikidata returns 2 or more candidate matches → present all candidates in a human gate checkpoint. Cross-validation disagreements on death date trigger human gate. This enrichment is additive and never blocks intake.

**Dependencies:** Usul-Data JSON (~50MB, MIT license). Wikidata SPARQL endpoint (free, CC0). Update frequency: Usul-Data quarterly (follow their releases), Wikidata cache refreshed monthly. Depends on: §4.B.1's OpenITI matching (shared URI format), §4.A.5's scholar authority model.

[NOT YET IMPLEMENTED] — Full specification provided. No code exists.

#### §4.B.9 — Source Difficulty Prediction

**Capability:** Before the normalization engine processes a source, the source engine analyzes the source's metadata and a sample of its content to predict how difficult the source will be to process through the entire pipeline, what the expected knowledge yield will be, and where human intervention will likely be needed. This prediction enables intelligent queue prioritization: easy, high-yield sources are processed first, producing immediate library value, while difficult sources are queued with predicted human gate counts and estimated processing time.

**Technology:** The prediction model uses a weighted combination of seven difficulty signals, each scored 0.0 (trivial) to 1.0 (maximum difficulty). The signals are computed from metadata already available at intake time (Steps 1-4 of §4.A.2) — no additional processing is required.

**Input:** A source_id with completed metadata extraction and inference (post-Step 4 of §4.A.2, pre-freezing). The prediction is computed before the source enters the pipeline.

**Difficulty signals:**

1. **Format complexity** (weight 0.20). Shamela structured HTML → 0.1. Text-embedded PDF → 0.2. Mixed-format Word docs → 0.4. Scanned PDF → 0.6. iPhone photos → 0.8. Multi-format directory → 0.7. Score derived from `source_format` field.

2. **Genre processing depth** (weight 0.20). `matn` or `risalah` (single-author, single-layer) → 0.1. `sharh` (two layers: matn + commentary) → 0.4. `hashiyah` (three layers) → 0.7. `taqrirat` (informal structure, often unpunctuated) → 0.6. `mawsuah` or `fatawa` (encyclopedic, covering 10+ distinct topics) → 0.5. `nazm` (verse — requires verse-aware processing) → 0.8. `mukhtasar` (abridgment — single-layer but dense) → 0.2. `mujam` or `tabaqat` (dictionary/biographical — structured entries, low narrative complexity) → 0.3. `fiqh_comparative` (comparative — tracks positions across schools) → 0.5. `hadith_collection` (hadith — requires isnad/matn parsing) → 0.4. `tafsir` (exegesis — verse-by-verse, often multi-layer) → 0.5. `sirah` or `tarikh` (narrative history — moderate structure) → 0.3. `adab` (literary — variable structure) → 0.3. `other` → 0.5 (default for unclassified genres). Score derived from `genre` field.

3. **Multi-layer complexity** (weight 0.15). `multi_layer: false` → 0.0. Two layers → 0.4. Three or more layers → 0.8. Each additional layer increases the difficulty of attributing text to the correct author — the normalization and excerpting engines must track which words belong to which scholar. Score derived from `multi_layer` and `layers` fields.

4. **Science scope breadth** (weight 0.10). Single science → 0.1. Two sciences → 0.3. Three or more → 0.6. Sources spanning 2+ sciences require excerpts to be placed across 2+ taxonomy trees, multiplying the classification and placement work. Score derived from `science_scope` array length.

5. **Text fidelity** (weight 0.15). `high` → 0.0. `medium` → 0.3. `low` → 0.7. `unknown` → 0.5. Low-fidelity text produces more OCR errors, more low-confidence atoms, and more human gate checkpoints downstream. Score derived from `text_fidelity` field.

6. **Source size** (weight 0.10). < 100 pages → 0.0. 100-500 pages → 0.2. 500-2000 pages → 0.5. > 2000 pages → 0.8. Multi-volume works (>5 volumes) → max(page-based score, 0.9) — the volume count overrides only when it produces a higher score than the page count alone. Larger sources consume more LLM tokens, produce more passages, and have higher probability of containing processing edge cases. Score derived from `page_count` and `volume_count`.

7. **Author disambiguation confidence** (weight 0.10). Author canonical_id confidence ≥ 0.90 → 0.0. 0.70-0.90 → 0.3. < 0.70 → 0.7. A weakly identified author means all downstream attribution is uncertain, cascading through every engine. Score derived from `author.canonical_id` confidence in metadata inference results.

**Output:** A `difficulty_prediction` record appended to the source metadata:

```json
{
  "source_id": "src_a7c3e91f",
  "difficulty_prediction": {
    "overall_score": 0.42,
    "difficulty_tier": "moderate",
    "signals": {
      "format_complexity": {"score": 0.1, "reason": "Shamela structured HTML"},
      "genre_processing_depth": {"score": 0.4, "reason": "sharh — two-layer text"},
      "multi_layer_complexity": {"score": 0.4, "reason": "matn + sharh layers"},
      "science_scope_breadth": {"score": 0.1, "reason": "single science: nahw"},
      "text_fidelity": {"score": 0.0, "reason": "high fidelity structured text"},
      "source_size": {"score": 0.5, "reason": "648 pages, 2 volumes"},
      "author_disambiguation": {"score": 0.0, "reason": "author confidence 0.96"}
    },
    "expected_human_gates": 2,
    "expected_processing_hours": 4.5,
    "priority_recommendation": "high",
    "priority_reason": "Moderate difficulty but high knowledge yield (sharh of major nahw text, well-identified author, high fidelity text)"
  }
}
```

**Difficulty tiers:** `easy` (0.0–0.25): single-layer, single-science, high-fidelity, under 500 pages, author confidence ≥ 0.90. `moderate` (0.25–0.50): 1–2 signals score above 0.3 while the rest remain low. `hard` (0.50–0.75): multi-layer, multi-science, or low-fidelity — at least 2 signals score above 0.5. `very_hard` (0.75–1.0): 3 or more signals score above 0.5, compounding difficulties across format, genre, and fidelity dimensions.

**Priority recommendation logic:** Priority is NOT simply inverse difficulty. Priority considers: (1) difficulty (lower is better), (2) expected knowledge yield (the estimated count of taxonomy leaves this source will populate, derived from science scope + source size + genre), (3) owner's current study focus (a source in the active study science is prioritized), (4) gap-fill potential (does this source fill a coverage gap identified by §4.B.4?). A hard source that fills a critical gap is higher priority than an easy source covering already-saturated topics.

**Concrete example contrasting two sources:**

Source A: شرح ابن عقيل على ألفية ابن مالك (Shamela HTML, nahw sharh, 2 volumes, well-known author) → overall 0.42, tier `moderate`, priority `high` (fills intermediate nahw gap).

Source B: حاشية الصبان على شرح الأشموني على ألفية ابن مالك (iPhone photos, nahw hashiyah, 3 layers, 4 volumes, low text fidelity) → overall 0.78, tier `very_hard`, priority `low` (advanced specialist content, low fidelity requires extensive human review, library already has intermediate nahw coverage).

**Scholar impact:** Rayane sees a dashboard: "12 sources ready to process. Recommended order: (1) قطر الندى — easy, fills your intermediate nahw gap. (2) شرح ابن عقيل — moderate, builds on الألفية. (3) حاشية الصبان — hard, needs 15+ human reviews, process after basics are covered." This strategic sequencing means the library grows in curricular order — beginner content first, specialist content later — matching how a student should actually study.

**Implementation sketch:** All signals are computed from fields already present in the source metadata record after Step 4 of §4.A.2. The computation is a simple weighted sum — no LLM call needed. The difficulty prediction is appended to the metadata record before freezing (Step 6). No external dependencies. `expected_human_gates` is computed as: 1 (baseline — every source gets at least one review) + 1 if author confidence < 0.80 + 1 if any critical field confidence < 0.70 + 1 if text_fidelity is `low` or `unknown` + 1 per additional layer beyond 1 (multi-layer sources need per-layer attribution review). Expected processing hours: before 10 sources have been processed, the engine uses a fixed estimate of 0.5 hours per 100 pages for easy sources, scaling up to 2.0 hours per 100 pages for very_hard sources. After 10 sources, the engine calibrates its time estimates against actual processing durations recorded in the processing status log.

**Failure handling:** If any signal's input field is missing (e.g., `genre` not yet inferred), that signal defaults to 0.5 (uncertain). The prediction is recomputed after metadata enrichment if any signal-relevant fields change. The prediction is advisory only — it does not block processing.

[NOT YET IMPLEMENTED] — Full specification provided. No code exists. No external dependencies — uses only metadata fields already available at intake.

#### §4.B.10 — Tahqiq Apparatus Fingerprinting

**Capability:** When a source claims to be a critical edition (tahqiq), the source engine analyzes the structure and content of its editorial apparatus — footnotes, variant reading notes, manuscript references, hadith takhrij — to produce a "tahqiq fingerprint" that distinguishes genuine critical editions from commercial reprints masquerading as tahqiq. This addresses a documented problem in Islamic publishing: a significant proportion of editions (estimated at 30–50% of commercially available prints) claim tahqiq on their cover but contain no actual critical apparatus, or contain formulaic apparatus copied from other editions.

**Technology:** Pattern analysis of the first 5,000 characters of footnote content (extracted during format-specific metadata extraction in Step 3 of §4.A.2), combined with LLM classification of apparatus quality. No external dependencies beyond the standard LLM inference already used in Step 4.

**Input:** A source_id where the metadata extraction step has identified footnotes or endnotes in the source material. Triggered only for sources where `muhaqiq` is non-null (i.e., the source claims to have a tahqiq editor).

**Apparatus analysis signals:**

1. **Manuscript reference density.** Genuine tahqiq references specific manuscripts by their library, collection number, and folio. The engine counts occurrences of patterns indicating manuscript references: "نسخة" (copy), "مخطوط" (manuscript), library names from a configurable list (initial entries: دار الكتب المصرية, المكتبة الأزهرية, مكتبة تشستر بيتي, المتحف البريطاني, مكتبة الأوقاف — stored in `library/config/manuscript_libraries.json`, extensible by the owner), folio references (ورقة, ق). Density = count per 1,000 words of footnote text. Genuine critical editions typically have density > 5.0. Commercial reprints have density < 1.0.

2. **Variant reading notation.** Genuine tahqiq notes where manuscripts disagree: "في نسخة أخرى" (in another copy), "وفي رواية" (in another reading), "والصواب" (the correct reading is). The engine counts these patterns. Genuine editions have variant readings density > 3.0 per 1,000 footnote words.

3. **Hadith takhrij presence.** For fiqh and hadith sources, genuine tahqiq includes hadith source tracing in footnotes: references to hadith collections by name (أخرجه البخاري, رواه مسلم), hadith numbers, grading terms (صحيح, حسن, ضعيف). Presence of takhrij is a strong signal of editorial rigor.

4. **Formulaic apparatus detection.** Commercial publishers often use templated footnotes: identical phrasing repeated across pages, generic biographical notes copied from reference works without original analysis. The engine checks for: (a) footnote text entropy — genuine apparatus has high entropy (diverse content), formulaic apparatus has low entropy (repetitive patterns). Entropy is computed as Shannon entropy of word unigrams in the footnote text, normalized to 0.0-1.0 by dividing by log2(vocabulary_size) (the maximum possible entropy for the observed vocabulary). A normalized entropy of 0.0 means all footnotes use the same word; 1.0 means perfectly uniform word distribution. Genuine critical editions typically score > 0.75; formulaic apparatus scores < 0.50. (b) proportion of footnotes that are purely biographical (> 80% biographical footnotes with no textual commentary suggests a commercial biographical compilation, not genuine tahqiq).

5. **Muhaqiq reputation cross-reference.** The engine checks the `muhaqiq` name against the recognized muhaqiqs list (§4.A.8 configuration) and also against a configurable watchlist of editors known for commercial, non-scholarly editions. The watchlist is informed by domain knowledge (e.g., the practices documented by Mufti Kadodia and other scholars regarding specific editors and publishers).

**Output:** A `tahqiq_fingerprint` record appended to the source metadata:

```json
{
  "source_id": "src_d7e8f9a0",
  "tahqiq_fingerprint": {
    "apparatus_present": true,
    "manuscript_reference_density": 8.3,
    "variant_reading_density": 5.1,
    "hadith_takhrij_present": true,
    "footnote_entropy": 0.87,
    "formulaic_ratio": 0.12,
    "muhaqiq_reputation": "recognized",
    "tahqiq_quality_classification": "genuine_critical",
    "classification_confidence": 0.91,
    "classification_evidence": "High manuscript reference density (8.3), variant readings present (5.1), muhaqiq محمد فؤاد عبد الباقي is on recognized list, high footnote entropy (0.87 — diverse editorial content)"
  }
}
```

**Tahqiq quality classifications:**

- `genuine_critical`: manuscript references present, variant readings noted, muhaqiq recognized or apparatus demonstrates scholarly rigor. This edition's text can be trusted as carefully verified against manuscripts.
- `scholarly_reprint`: no original manuscript work, but the edition is based on a recognized earlier tahqiq (the editor cites the earlier edition). The text is reliable but the apparatus is derivative.
- `commercial_reprint`: no manuscript references, no variant readings, or formulaic apparatus. The text may contain uncorrected errors. Trust tier impact: the source's tahqiq quality factor (§4.A.8, weight 0.25) is reduced from 0.90 to 0.30.
- `claimed_but_absent`: the source claims tahqiq on the cover but contains no footnotes or apparatus at all. Trust tier impact: tahqiq quality factor reduced to 0.20.
- `insufficient_data`: fewer than 500 words of footnote text available for analysis. Classification deferred pending normalization.

**Concrete example with Arabic text:** Rayane acquires two copies of صحيح البخاري:

Edition A (تحقيق محمد فؤاد عبد الباقي): Footnotes contain: "كذا في نسخة اليونينية ونسخة أبي ذر الهروي، وفي نسخة الأصيلي: بزيادة..." (manuscript-specific variant readings), hadith numbering cross-referenced with Fath al-Bari. Manuscript reference density: 12.4. Variant density: 8.7. Classification: `genuine_critical` (0.95).

Edition B (publisher: دار الكتب العلمية, muhaqiq: محمد حسن الشافعي): Footnotes contain generic biographical entries for narrators copied from Tahdhib al-Kamal, no variant readings, no manuscript references despite the cover claiming "تحقيق ومراجعة." Manuscript reference density: 0.2. Variant density: 0.0. Formulaic ratio: 0.91. Classification: `commercial_reprint` (0.88).

The source engine automatically adjusts the trust evaluation for Edition B: tahqiq quality factor drops from 0.90 (recognized muhaqiq) to 0.30 (commercial reprint), which may push the combined trust score below the verified threshold. The owner is notified: "Edition B of صحيح البخاري claims tahqiq but the apparatus analysis found no manuscript references and no variant readings. This appears to be a commercial reprint. Recommend using Edition A as the preferred source."

**Scholar impact:** Rayane no longer needs to manually evaluate whether a claimed tahqiq is genuine — a task that requires years of experience and side-by-side comparison of 2 or more editions. The source engine does this automatically, protecting the library from unreliable text that masquerades as critically edited. For a student who cannot yet distinguish good editions from bad ones, this is a scholarly mentor's judgment automated.

**Implementation sketch:** During metadata extraction (Step 3), format-specific extractors already parse footnotes for Shamela HTML (footnote divs) and PDFs (Docling footnote detection). The engine extracts up to 5,000 characters of footnote text. Pattern matching for manuscript references and variant readings uses regex patterns on Arabic text (library names, folio notation, variant reading formulae). Footnote entropy is computed as Shannon entropy of word unigrams in the footnote text. The LLM classifies the overall apparatus quality using a prompt that includes: the footnote sample, the pattern analysis scores, and the muhaqiq name. Multi-model consensus is NOT required because the classification is non-destructive (it adjusts a trust factor, not content or attribution). The classification is stored in the source metadata and feeds into the trustworthiness evaluation (§4.A.8).

**Failure handling:** If no footnotes are detected and the source claims a muhaqiq, the classification is `claimed_but_absent` with confidence 0.85. If footnote text is too short (< 500 words), classification is `insufficient_data` and the analysis is deferred until the normalization engine extracts more text. If pattern analysis and LLM classification disagree (e.g., patterns indicate genuine but LLM classifies as commercial), the higher-quality classification (the one with more evidence) is used and the disagreement is logged for human review.

**Configuration:** The recognized muhaqiqs list (§4.A.8) and the watchlist of commercial editors are both configurable. Initial watchlist entries are derived from domain knowledge sources. The owner can add or remove entries. Both lists are stored in `library/config/muhaqiq_lists.json`.

[NOT YET IMPLEMENTED] — Full specification provided. No code exists. Depends on: format-specific extractors (§4.A.3) for footnote text extraction, trustworthiness evaluation (§4.A.8) for trust factor integration.

---

## 5. Validation and Quality

The source engine's output — source metadata — is the foundation upon which every downstream engine builds. An error here cascades through the entire pipeline. The validation architecture has three layers.

**Layer 1: Self-validation (automated, at intake time).**

The source engine validates its own output before writing the metadata record:

1. **Schema compliance.** The metadata record is validated against the source metadata JSON schema. Any missing required field, type mismatch, or constraint violation aborts the write with a structured error.

2. **Referential integrity.** The `author.canonical_id` must reference a valid record in the scholar authority registry. The `work_id` must reference a valid record in the work registry. Genre chain relationships must reference valid work_ids (or placeholder records). If any reference is invalid, the write aborts.

3. **Confidence threshold check.** If any critical field (author canonical_id, work_id, genre, science_scope) has confidence < 0.50, the metadata record is not written. Instead, a human gate checkpoint is created. The threshold is 0.50, not 0.70, because 0.50-0.70 fields are written with `needs_review` flags, and only truly low-confidence fields block writing.

4. **Duplicate re-check.** After metadata inference (which may have changed the title or author), deduplication is re-run. This catches cases where the raw metadata didn't match a duplicate but the inferred metadata does.

5. **Consistency cross-check.** The inferred genre must be consistent with the inferred structural_format (a `nazm` genre should have `verse` structural_format). The inferred level must be consistent with the genre (a `hashiyah` should not be `beginner`). The science_scope must be plausible for the identified author. Inconsistencies are flagged as warnings (not blocking) and trigger `needs_review` on the inconsistent fields. **Author-science mismatch detection:** If the inferred `science_scope` does not overlap with any of the identified author's known science specializations (from the scholar authority record's `school_affiliations` keys, e.g., an author known only for nahw is identified as author of a fiqh work), this is flagged as `SRC_METADATA_INCONSISTENCY` with a human gate checkpoint — this specific inconsistency often indicates a misidentified author rather than a mere classification error.

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

Consensus is NOT used for: genre classification, science scope, structural format, trust evaluation, or scholar biographical details (death dates, school affiliations, teachers, students). These fields have lower cascade risk (they affect processing strategy but don't corrupt attribution) and their correctness is verifiable by downstream engines. Adding consensus to every field would multiply LLM costs without proportionate quality gain.

**Mitigation for single-LLM biographical inference.** Scholar biographical data (death dates, school affiliations, teacher-student links) inferred by a single LLM call is still critical for synthesis quality. Since consensus is not applied, the following mitigations apply: (1) All single-LLM biographical inferences carry a maximum confidence of 0.85 — never 0.90+ even if the LLM reports higher confidence. This ensures the data is always treated as provisional. (2) When OpenITI metadata is available (§4.B.1), it takes precedence over LLM inference for death dates and known works. (3) The scholar record consistency checks (§4.A.5) catch implausible LLM outputs (death date drift, temporal inconsistencies in teacher-student chains). (4) For scholars appearing in 3+ sources, the source engine cross-checks biographical data across all intake events — if two independent intakes produce different death dates for the same scholar, a human gate is created.

**Consensus configuration:** Two models (configured via OpenRouter or direct API). Agreement threshold: both models must select the same canonical_id or work_id. Models should be from different providers (e.g., Claude + GPT) to reduce correlated errors. If one model times out or fails, the fallback depends on the decision type: for author identification (the highest-cascade decision), a single model result is NOT accepted — a human gate checkpoint is created with the single model's suggestion and the reason the second model failed. For work matching, a single model's result is accepted provisionally with a `single_model_confidence` flag and `needs_review` on the `work_id` field. This asymmetry reflects the cascade risk: a wrong author ID corrupts every downstream product, while a wrong work match is detectable and correctable at the work level.

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
| `SRC_FREEZE_COPY_CORRUPT` | Fatal | Post-freeze hash mismatch (staging hash ≠ frozen hash) | Delete frozen directory. Abort intake. Source remains in staging for retry. |
| `SRC_FREEZE_PERMISSION_FAILED` | Fatal | Cannot set frozen files to read-only | Delete frozen directory. Abort intake. Log filesystem error. |
| `SRC_STAGING_MODIFIED` | Fatal | Staged files modified between format detection and freezing | Abort intake. Log modification timestamps. Owner must re-stage. |
| `SRC_REGISTRATION_INTERRUPTED` | Warning | Orphaned pending_registration file found on startup | Attempt to complete or roll back interrupted registration. Log outcome. |
| `SRC_ENRICHMENT_CRITICAL_FIELD` | Warning | Enrichment modifies author, work_id, genre, or science_scope | Create human gate checkpoint. Do not apply until confirmed. |
| `SRC_SCHOLAR_DATE_CONFLICT` | Warning | Scholar death date enrichment differs by >5 years from existing | Block update. Create human gate with both dates and sources. |
| `SRC_SCHOLAR_SCHOOL_CONFLICT` | Warning | Scholar school affiliation enrichment contradicts existing | Block update. Create human gate. |
| `SRC_SCHOLAR_TEMPORAL_INCONSISTENCY` | Warning | Teacher-student link with implausible death date gap (>30 years wrong direction) | Flag relationship. Create human gate. |
| `SRC_FORMAT_STRUCTURE_MISSING` | Warning | Detected format but expected structural file absent (e.g., Shamela without info.html) | Fall back to minimal extraction + LLM inference. Flag all extracted fields as `needs_review`. |
| `SRC_KITAB_CACHE_MISSING` | Info | KITAB statistics cache not found at configured path | Skip KITAB enrichment (§4.B.5). Log. Enrichment deferred until cache is downloaded. |
| `SRC_KITAB_CACHE_CORRUPT` | Warning | KITAB statistics cache downloaded but fails validation (bad CSV headers or spot-check mismatch) | Discard corrupted file. Log. Skip KITAB enrichment until valid cache is obtained. |
| `SRC_USUL_DATA_MISSING` | Info | Usul-Data `authors.json` not found at configured path | Skip Usul-Data enrichment (§4.B.8). Log. Proceed with OpenITI and Wikidata only. |
| `SRC_WIKIDATA_TIMEOUT` | Info | Wikidata SPARQL query timed out or returned HTTP error after 3 retries | Skip Wikidata enrichment (§4.B.8). Log. Proceed with OpenITI and Usul-Data only. |
| `SRC_COMPARISON_DEFERRED` | Info | Edition comparison requested but normalized text not yet available for 1+ editions | Defer comparison. Log. Re-attempt when both editions reach `normalized` status. |
| `SRC_FREEZE_CLEANUP_FAILED` | Fatal | Cannot delete corrupt frozen directory after SRC_FREEZE_COPY_CORRUPT | Write CORRUPT_FREEZE marker. Source stays in staging. Manual cleanup required. |
| `SRC_OPENITI_CACHE_CORRUPT` | Warning | OpenITI metadata CSV fails integrity verification (bad headers or spot-check mismatch) | Discard file. Skip OpenITI enrichment. Fall back to LLM-only inference. |
| `SRC_COMPARISON_INCONCLUSIVE` | Info | Edition comparison alignment below 20% sufficiency threshold | Write comparison record with null recommendation. Create human gate for manual review. |

**Principle:** Never lose data silently. Every error is logged with: timestamp, source identifier (if known), error code, severity, human-readable message, and the specific recovery action taken (one of: reject intake, create human gate, flag field for review, skip optional enrichment, retry on next cycle). Fatal errors stop processing for the affected source but do not affect other sources in the pipeline. Warning errors allow processing to continue with the affected fields marked as `needs_review`. Info errors are logged for audit with no processing impact.

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
| `staging_lock_timeout` | 3600 | 300–86400 | Seconds before orphaned staging locks are cleaned up on startup |

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

3. **Scholar authority model.** Current code represents the author as a flat string in metadata. SPEC requires a centralized scholar authority registry with canonical identities, name variants, biographical data, teacher-student graph, and progressive enrichment. [NOT YET IMPLEMENTED]

4. **Work registry.** Code has no concept of works grouping multiple sources. SPEC requires a work registry tracking abstract works, their sources (editions), relationships (sharh→matn chains), and preferred editions. [NOT YET IMPLEMENTED]

5. **LLM-assisted metadata inference.** Code's `enrich.py` does basic LLM enrichment. SPEC requires comprehensive bibliographic intelligence: genre chain inference, multi-layer detection, structural format classification, science scope inference, and confidence scoring. [NOT YET IMPLEMENTED]

6. **Multi-model consensus.** Code uses single-model inference. SPEC requires two-model consensus for author identification and work matching. [NOT YET IMPLEMENTED]

7. **Work relationship graph.** Code has no relationship tracking. SPEC requires a queryable graph of sharh→matn, mukhtasar→original, and citation relationships. [NOT YET IMPLEMENTED]

8. **Trustworthiness evaluation.** Code has no trust assessment. SPEC requires a multi-factor evaluation producing verified/flagged tiers. [NOT YET IMPLEMENTED]

9. **OpenITI enrichment.** [NOT YET IMPLEMENTED]

10. **Citation network discovery.** [NOT YET IMPLEMENTED]

11. **Acquisition gap analysis.** [NOT YET IMPLEMENTED]

12. **Processing status tracking.** Code uses a simple registry. SPEC requires pipeline-wide status tracking with stage-specific timestamps. [NOT YET IMPLEMENTED]

13. **Cross-validated scholar authority bootstrapping (§4.B.8).** SPEC requires querying Usul-Data and Wikidata in addition to OpenITI, with three-source cross-validation for death dates, known works union, and teacher-student links. [NOT YET IMPLEMENTED]

14. **Source difficulty prediction (§4.B.9).** SPEC requires a seven-signal weighted prediction model that computes difficulty tiers and priority recommendations before pipeline processing. [NOT YET IMPLEMENTED]

15. **Tahqiq apparatus fingerprinting (§4.B.10).** SPEC requires analysis of footnote content to classify tahqiq editions as genuine_critical, scholarly_reprint, commercial_reprint, claimed_but_absent, or insufficient_data. [NOT YET IMPLEMENTED]

16. **Edition comparison intelligence (§4.B.6).** SPEC requires automated comparison of 2+ editions of the same work, classifying divergences and recommending preferred edition. [NOT YET IMPLEMENTED]

17. **KITAB text reuse integration (§4.B.5).** SPEC requires local KITAB statistics cache download and compositional profiling of sources against the OpenITI corpus. [NOT YET IMPLEMENTED]

18. **Scholarly genealogy auto-construction (§4.B.7).** SPEC requires multi-generational teacher-student chain construction with NetworkX graph analysis. [NOT YET IMPLEMENTED]

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

8. **Error handling completeness.** Test every error code in the taxonomy: provide an unsupported format → `SRC_UNSUPPORTED_FORMAT`. Provide an empty file → `SRC_EMPTY_INPUT`. Provide a duplicate → `SRC_DUPLICATE_EXACT`. Provide an invalid enrichment → `SRC_INVALID_ENRICHMENT`. Trigger each of the 14 error codes defined in §7 at least once and verify the correct code, severity, and recovery action.

**Gold baseline usage:** No gold baselines exist for the source engine yet. The first gold baselines should be created from: (1) a well-known Shamela export (e.g., شرح ابن عقيل) with manually verified metadata, and (2) a scanned PDF with manually verified OCR and metadata extraction.

**Regression testing strategy:** After any change to the metadata inference prompt, re-run intake on the gold baseline sources and verify that metadata output matches expected values. After any change to the scholar authority matching logic, re-run on a test set of sources with known author matches/non-matches.

**Integration test requirements:**
- Source engine → normalization engine: verify that the metadata record produced by the source engine is correctly read by the normalization engine and that source_id references resolve correctly.
- Source engine → scholar authority registry: verify that scholar records created during intake are correctly queryable by the excerpting engine and synthesizing engine.
- Enrichment write-back: verify that a downstream engine's enrichment update is correctly applied to the source metadata record, that the old value is preserved in `metadata_history`, and that the update triggers stale-marking on all excerpts derived from this source when the changed field is one of: `author.canonical_id`, `work_id`, `genre`, `science_scope`, or `trust_tier`.

---

## Appendix A: Hardening Analysis (2026-03-07)

This appendix documents adversarial scenario testing, error cascade analysis, and invariant verification performed during the source engine hardening session. Each scenario identifies a concrete corruption path, evaluates existing defenses, and specifies any SPEC fixes applied.

### A.1 — Adversarial Scenarios

#### Scenario 1: Concurrent Intake Creates Duplicate Scholar Records

**Attack:** Two sources referencing the same scholar (e.g., ابن قدامة) are processed simultaneously. Source A creates `sch_00042` during Step 4. Source B begins Step 4 before A reaches Step 7, doesn't see `sch_00042` yet, and creates `sch_00043` for the same scholar.

**Existing defenses:** §4.A.2 Step 7 uses write-ahead log for atomic registry updates per source. §4.A.5 record matching checks the registry before creating new records.

**Gap:** The write-ahead log atomizes a single source's registration, but no cross-intake lock prevents two processes from reading the scholar registry at the same overlapping instant.

**Corruption path:** Same scholar gets two canonical_ids. All downstream products for Source A attribute to `sch_00042`; Source B to `sch_00043`. The synthesizer treats them as different scholars.

**Fix applied (§4.A.2 Step 7):** Registry write operations acquire an exclusive file lock on the target registry file before reading current state and writing updates. Specifically: before Step 4's scholar registry read-check-create sequence, the source engine acquires a lock on `scholars.json`. The lock is held through the scholar record creation or match, and released after the scholar record write completes. If the lock cannot be acquired within 30 seconds, the intake for this source is deferred with status `staging` and a retry scheduled. This serializes scholar record creation without blocking the entire intake pipeline — only the scholar registry critical section is locked. The same lock pattern applies to `works.json` for work matching (Step 5) and to all three registries during Step 7's atomic write.

#### Scenario 2: Wikidata Returns Plausible But Wrong Scholar

**Attack:** Source engine queries Wikidata for ابن قدامة (d. 620 AH). Wikidata returns a different scholar named ابن قدامة with a death date of 618 AH (within the ±2 year tolerance). The wrong scholar has entirely different known works.

**Existing defenses:** §4.B.8 death date triangulation with ±2 year tolerance. Known works union across three sources.

**Gap:** The cross-validation computes a known_works_union but doesn't flag zero overlap between Wikidata's works and OpenITI's works as a discrepancy. Death date passes within tolerance.

**Corruption path:** Wrong biographical data (teachers, students, geographic info) from Wikidata enters the scholar record. Genealogy chains built on this data are false.

**Fix applied (§4.B.8):** Added a known-works overlap check: if Wikidata returns a candidate match where NONE of the known works overlap with the works from OpenITI or Usul-Data (zero intersection between `wikidata_only` and `all_three`), the match is flagged as `wikidata_match_suspect` and a human gate checkpoint is created. The Wikidata data is NOT merged into the scholar record until the owner confirms the match. Additionally, when Wikidata returns two or more candidates, the candidate whose known works have the highest overlap with OpenITI is preferred (previously: human gate for all multi-match cases — this is now the first-pass filter before human gate).

#### Scenario 3: LLM Invents Plausible Teacher-Student Link

**Attack:** §4.B.7 genealogy inference prompt asks for teachers of ابن عقيل. Both LLMs confidently return a plausible but fabricated teacher: "درس على شمس الدين الأصفهاني" — a real scholar (d. 749 AH), correct era, correct geographic region, but no historical source confirms this student-teacher relationship.

**Existing defenses:** Multi-model consensus (both models must agree). Temporal consistency check (teacher death must precede student). Depth limit (4 generations up, 2 down). `chain_sources` field records provenance.

**Gap:** When both models hallucinate the same plausible relationship (same era, same field, plausible geographic overlap), all automated checks pass. The relationship enters the scholar authority record with `chain_sources: ["llm_inference"]` and no corroborating external data.

**Corruption path:** The synthesizer produces scholarly narratives citing a false intellectual lineage. Rayane's understanding of scholarly tradition includes a fabricated connection.

**Fix applied (§4.B.7):** Genealogy links supported ONLY by LLM inference (no corroboration from OpenITI, Usul-Data, Wikidata, or source text) receive a maximum confidence of 0.70 (regardless of LLM-reported confidence) and are flagged as `genealogy_source: "llm_only"` in the teacher/student link metadata. Links with `genealogy_source: "llm_only"` are displayed in synthesis outputs with an explicit qualifier: "attributed by scholarly tradition" rather than stated as fact. Links corroborated by at least one structured source (OpenITI, Wikidata P1066/P802) receive confidence up to 0.90 and are stated as confirmed relationships.

#### Scenario 4: Edition Comparison on Radically Divergent Editions

**Attack:** Two sources of المغني are acquired: one is the standard 15-volume print; the other is an abridged 3-volume digest marketed under the same title. Chapter-level alignment fails because the structures are completely different. The 300-word chunk fallback runs but only ~5% of text aligns.

**Existing defenses:** §4.B.6 falls back to whole-text alignment for divergent structures.

**Gap:** No threshold below which the comparison is abandoned. The engine produces a comparison record with 95% `structural_difference` divergences, which is meaningless noise rather than useful intelligence.

**Corruption path:** No data corruption (the comparison is advisory), but the preferred edition recommendation is unreliable — the engine might recommend the abridged version because it has "fewer OCR artifacts" (it has fewer artifacts because it has 80% less text).

**Fix applied (§4.B.6):** Added an alignment sufficiency threshold: if fewer than 20% of 300-word chunks from the shorter edition align with any chunk in the longer edition (alignment defined as SequenceMatcher ratio ≥ 0.60), the comparison is classified as `inconclusive` with reason `"editions_structurally_incomparable"`. No preferred edition recommendation is produced. The comparison record is still written (preserving whatever alignment was found) but the `summary.preferred_edition_recommendation` is set to `null` and `summary.preference_reason` reads: "Editions are too structurally divergent for automated comparison (X% alignment). Manual review recommended." The owner is notified via a human gate checkpoint.

#### Scenario 5: Enrichment Write-Back Loop

**Attack:** The excerpting engine discovers the actual author is different from the one initially identified. It sends an enrichment changing `author.canonical_id`. This triggers stale-marking cascade on all excerpts. Re-processing of those excerpts generates new metadata that contradicts the new author (e.g., the writing style analysis now disagrees). The excerpting engine sends another enrichment changing the author back. This triggers another stale-marking cascade...

**Existing defenses:** §2 enrichment invariant #4 (history preservation). Human gate for critical field changes. §5 Layer 3 progressive correction.

**Gap:** No explicit depth limit on enrichment-triggered re-processing. The human gate for author changes (invariant #2) prevents trivial loops, but if the owner approves each change, the loop continues with human-in-the-loop overhead.

**Fix applied (§2 enrichment invariants, new invariant #8):** Added: **8. Re-processing depth limit.** When an enrichment triggers stale-marking and re-processing, the re-processed output may generate at most one further enrichment request on the same source. If that second-generation enrichment would modify the same field that was changed by the first enrichment (forming a cycle), the second enrichment is NOT auto-submitted. Instead, it is logged with both values and a human gate checkpoint is created: "Field `{field}` was changed from A→B, re-processing now suggests B→C (or back to A). Manual resolution required." This prevents enrichment ping-pong while preserving the ability to cascade legitimate corrections (e.g., author change → genre change is allowed as a one-level cascade).

#### Scenario 6: Disk Full During Freezing — Cleanup Failure

**Attack:** Step 6 copies files to the frozen directory. Disk fills mid-copy. Post-freeze hash verification detects the mismatch (SRC_FREEZE_COPY_CORRUPT). The engine tries to delete the partially-written frozen directory, but the deletion also fails (disk truly full — no space even for directory operations).

**Existing defenses:** SRC_FREEZE_COPY_CORRUPT triggers frozen directory deletion.

**Gap:** If deletion fails, the partial frozen directory persists. On next startup, the engine might find a frozen directory with files that appear valid individually but are an incomplete set.

**Fix applied (§4.A.2 Step 6):** If frozen directory deletion fails after a SRC_FREEZE_COPY_CORRUPT, the engine logs `SRC_FREEZE_CLEANUP_FAILED` (new error code, severity: Fatal) and writes a marker file `library/sources/{source_id}/CORRUPT_FREEZE` containing the error details and timestamp. On startup, the engine checks for any `CORRUPT_FREEZE` markers and treats those source directories as requiring manual cleanup. The source remains in `staging` status and is not available for processing. Added `SRC_FREEZE_CLEANUP_FAILED` to §7 error taxonomy.

#### Scenario 7: Malformed Enrichment Targeting Wrong Source

**Attack:** The excerpting engine has a bug and sends an enrichment request with `source_id: "src_a3f2b1c4"` (a nahw source) but the enrichment data is for `src_d7e8f9a0` (a fiqh source). The enrichment changes `science_scope` from `["nahw"]` to `["fiqh"]`.

**Existing defenses:** §2 enrichment invariants check schema compliance and referential integrity. §5 consistency cross-check would flag genre/science mismatches when genre and science_scope are contradictory.

**Gap:** The enrichment is schema-valid (a science_scope of `["fiqh"]` is a valid value). The consistency cross-check catches `genre: sharh` (a nahw sharh) with `science_scope: ["fiqh"]` as a mismatch, but only as a warning that flags the field — it doesn't block the write.

**Fix applied (§2 enrichment invariants):** Enrichment requests for fields in the critical set (`author.canonical_id`, `work_id`, `genre`, `science_scope`) must include a `verification_context` field containing: the `work_id` and `author.canonical_id` that the requesting engine believes belong to this source. The source engine checks these against the actual source metadata before applying. If they don't match, the enrichment is rejected with `SRC_INVALID_ENRICHMENT` and the mismatch is logged at WARNING level. This catches source_id targeting errors at the boundary. Updated the EnrichmentRequest contract model accordingly.

#### Scenario 8: Orphaned Staging Lock After Crash

**Attack:** The source engine crashes during intake between Step 2 (format detection, where `.kr_processing` lock is placed) and Step 6 (freezing). The lock file remains. Subsequent intake attempts for the same staged material see the lock and refuse to process it. The source is permanently stuck.

**Existing defenses:** §4.A.2 defines the staging lock mechanism.

**Gap:** No orphan lock cleanup.

**Fix applied (§4.A.2):** On startup, the source engine scans `library/staging/` for directories containing `.kr_processing` lock files. For each lock file: if the file's modification timestamp is older than the configurable `staging_lock_timeout` (default: 1 hour), the lock is removed and the directory is made available for re-processing. A log entry records the cleanup. Added `staging_lock_timeout` to §8 configuration table.

#### Scenario 9: Scholar Record Entirely From Single LLM — No External Validation

**Attack:** An obscure scholar (a local Yemeni muhaddith from the 6th century Hijri) is not in OpenITI, Usul-Data, or Wikidata. The scholar record is 80% populated but every non-null field is from a single LLM inference call. The record looks complete but may contain hallucinated biographical data.

**Existing defenses:** §6 caps single-LLM biographical inference at 0.85 confidence. `record_sources` tracks provenance.

**Gap:** The `record_completeness` field (0.80) looks healthy, but it tracks fill rate, not data quality. No signal distinguishes "80% complete from verified sources" from "80% complete from one LLM call."

**Fix applied (§4.A.5):** Added a `data_provenance_score` field to ScholarAuthorityRecord: the fraction of non-null biographical fields (excluding mechanical fields like `canonical_id`, `last_updated`, `record_sources` themselves) whose values are corroborated by at least one non-LLM source (OpenITI metadata, Usul-Data, Wikidata, explicit source text extraction, or owner input). Score of 0.0 means entirely LLM-inferred; 1.0 means every field has external corroboration. Records with `data_provenance_score` < 0.30 are flagged as `low_provenance` in the scholar registry dashboard. The synthesizer uses this score to qualify biographical claims: high-provenance records produce direct statements ("ابن قدامة, d. 620 AH"); low-provenance records produce hedged statements ("ابن قدامة, reportedly d. 620 AH according to biographical sources").

#### Scenario 10: TOCTOU Between Metadata Inference and Registration

**Attack:** Between Step 4 (metadata inference) and Step 7 (registration), an external process or concurrent intake modifies the scholar registry (adds a new scholar that would have been a match). The source engine's dedup re-check (§5 Layer 1, item 4) catches title/author matches but not scholar matches that appeared between Steps 4 and 7.

**Existing defenses:** Step 5 re-runs deduplication after inference. Step 7 is atomic per-source.

**Gap:** Scholar matching is done in Step 4 but not re-checked in Step 7's pre-write validation. If another intake process created the scholar between Steps 4 and 7, a duplicate scholar record is created.

**Fix applied (§4.A.2 Step 7):** The registry file locking mechanism (added in Scenario 1's fix) resolves this: the lock acquired on `scholars.json` during Step 4's matching also covers Step 7's write. Since Step 4 through Step 7 holds the scholar registry lock, no concurrent process can create the same scholar in between. For the case where Steps 4-7 do NOT run as a continuous locked section (e.g., Step 5 deduplication releases and re-acquires locks), Step 7's atomic write phase re-checks that the `canonical_id` being created does not already exist in the registry. If it does (because a concurrent process created it during the lock gap), Step 7 links to the existing record instead of creating a duplicate.

#### Scenario 11: External Dataset Contains Intentionally Poisoned Data

**Attack:** A modified OpenITI metadata CSV is placed at the configured path — either by a supply-chain attack on the GitHub download or by filesystem compromise. The modified CSV contains altered death dates for 50 scholars.

**Existing defenses:** §4.B.5 (KITAB) has integrity verification: CSV header check, 3 spot-check entries, hash verification.

**Gap applied to §4.B.1 (OpenITI):** The OpenITI metadata enrichment (§4.B.1) doesn't specify integrity verification comparable to the KITAB cache verification.

**Fix applied (§4.B.1):** Added integrity verification for the OpenITI metadata CSV mirroring the KITAB cache approach: (1) verify expected CSV column headers match a known schema, (2) spot-check 5 well-known scholars whose death dates and work counts are historically certain (configurable in `library/config/openiti_validation_samples.json`, initial entries: Sibawayhi d.180, Bukhari d.256, Ghazali d.505, Nawawi d.676, Ibn Taymiyyah d.728), (3) store and verify the file's SHA-256 hash in `library/external/openiti_metadata/manifest.json`. If verification fails, the download is discarded with `SRC_OPENITI_CACHE_CORRUPT` (new error code, severity: Warning) and enrichment falls back to LLM-only inference. Additionally, the Usul-Data `authors.json` receives the same verification treatment: header structure check, 5 spot-check scholars, SHA-256 hash in `library/external/usul_data/manifest.json`.

#### Scenario 12: Enrichment Changes Trust-Relevant Field Without Re-Evaluation

**Attack:** An enrichment updates the `muhaqiq` field to a recognized editor. The trust evaluation (§4.A.8) used the original unknown muhaqiq, scoring 0.50. The new recognized muhaqiq would score 0.90. But the trust tier is not re-evaluated — the source stays `flagged` when it should be `verified`.

**Existing defenses:** §2 enrichment invariant #5 says no enrichment may change `trust_tier` directly. An enrichment may "request a trust re-evaluation by updating evaluation-relevant fields."

**Gap:** The SPEC says enrichments "may request" re-evaluation but doesn't specify the mechanism. How does updating `muhaqiq` trigger a re-evaluation?

**Fix applied (§4.A.8):** Explicitly specified: when an enrichment modifies any of the five trust evaluation input fields (`author.canonical_id`, `muhaqiq`, `publisher`, `authority_level`, `text_fidelity`), the source engine automatically re-runs the trustworthiness evaluation algorithm using the updated values. If the new trust tier differs from the old one, the change is logged and: (a) if the new tier is `verified` (upgrading from `flagged`), a human gate checkpoint is created for owner confirmation — upgrading trust is a higher-risk action than flagging. (b) if the new tier is `flagged` (downgrading from `verified`), the change is applied immediately and a stale-marking cascade is triggered on all excerpts (their verified/flagged status may need to change). The `trust_factors` array in the metadata record is updated to reflect the re-evaluation.

### A.2 — Error Cascade Traces

#### Cascade 1: Wrong Author at Intake → Corrupted Synthesis

**Origin:** §4.A.4 (LLM inference) — the LLM identifies author as "ابن حجر الهيتمي" (Shafi'i fiqh, d. 974) when the actual author is "ابن حجر العسقلاني" (hadith scholar, d. 852).

**Propagation path:**

1. **Source engine (§4.A.4):** Wrong canonical_id assigned. Both models agree (both are Shafi'i, the title "فتح الباري" is ambiguous to models that don't distinguish editions). Confidence: 0.85. No human gate triggered (≥ 0.80).
2. **Source engine (§4.A.5):** Scholar record for al-Haytami gains a work he didn't write. The record's `known_works` list is wrong.
3. **Source engine (§4.A.8):** Trust evaluation uses al-Haytami's scholarly standing. Trust tier may differ from correct evaluation (al-Asqalani is a higher-standing hadith scholar).
4. **Source engine (§4.A.9):** Work relationships are wrong — the genre chain links to al-Haytami's corpus instead of al-Asqalani's.
5. **Normalization engine:** Proceeds normally (doesn't use author for text processing). No catch.
6. **Excerpting engine:** Attributes all excerpts to al-Haytami. When excerpts reference "الحافظ" (a title for al-Asqalani), the system doesn't flag the inconsistency.
7. **Taxonomy engine:** Places excerpts in Shafi'i fiqh tree instead of hadith methodology tree (wrong science scope).
8. **Synthesizer:** Produces entries attributing فتح الباري to al-Haytami. Scholarly narratives cite wrong biographical data. Teacher-student chains are wrong.
9. **Rayane's knowledge:** Contains systematic misattribution of a major hadith commentary. Every citation to this source is wrong.

**Detection points (where the cascade could be caught):**

- **§4.A.5 disambiguation_notes:** The SPEC already contains: "When 'ابن حجر' appears in hadith context → likely al-Asqalani." If the title "فتح الباري" is in the disambiguation notes for al-Asqalani, the matching should favor him. **Verdict:** Partially effective — depends on disambiguation notes being populated before this intake.
- **§6 consensus:** Two models both got it wrong → consensus doesn't help. **Verdict:** Ineffective for correlated errors.
- **§4.B.8 cross-validation:** OpenITI would match `0852IbnHaworkar.FathBari` (al-Asqalani), not al-Haytami. If the intake's canonical_id points to al-Haytami but OpenITI matches al-Asqalani, this is a detectable discrepancy. **Verdict:** Effective if OpenITI enrichment runs and cross-references the canonical_id.
- **§5 consistency cross-check:** The inferred science_scope of `["hadith"]` (from title "فتح الباري" — a hadith commentary) would be inconsistent with al-Haytami's known specialization in Shafi'i fiqh. **Verdict:** Effective if the cross-check is implemented to compare author specialization against science scope.

**Fix applied:** Added to §5 Layer 1, consistency cross-check: "If the inferred `science_scope` does not overlap with any of the identified author's known science specializations (from the scholar authority record's `school_affiliations` keys), flag as `SRC_METADATA_INCONSISTENCY` with severity WARNING and create a human gate checkpoint. This catches misidentifications where the author is real but wrong for this work."

**Residual risk:** LOW after fix. The combination of disambiguation notes, OpenITI cross-validation, and science scope consistency check creates three independent detection layers. All three would need to fail simultaneously for the cascade to reach the synthesizer.

#### Cascade 2: Corrupt External Data → Poisoned Scholar Records → Fabricated Genealogy

**Origin:** §4.B.1 (OpenITI enrichment) — a corrupted local CSV has wrong death dates for 50 scholars.

**Propagation path:**

1. **Source engine (§4.B.1):** Wrong death dates enter scholar authority records. For scholars with no other source of death dates, these become the canonical dates.
2. **Source engine (§4.B.7):** Genealogy construction uses death dates for temporal consistency checks (§4.A.5 item 5: "teacher death > student death + 30yr"). Wrong dates make impossible relationships pass the check (a teacher who actually died 100 years before the student now appears to have died 10 years before — plausible).
3. **Source engine (§4.B.8):** Cross-validation with Usul-Data and Wikidata should catch discrepancies. But if the corrupted CSV contains dates that are only slightly wrong (off by 20-30 years), the ±2 year tolerance would flag them. **However**, if the corruption is exactly within ±2 years (targeted attack), cross-validation misses it.
4. **Scholar authority registry:** 50 scholars have wrong death dates. Every downstream product referencing these scholars carries wrong dates.
5. **Synthesizer:** Produces biographical statements with wrong dates. Scholarly narratives contain wrong temporal claims ("ابن عقيل (d. 790 AH)" instead of 769 AH).
6. **Rayane's knowledge:** Systematic biographical errors across 50 scholars.

**Detection points:**

- **§4.B.1 integrity verification (newly added in Scenario 11):** The 5 spot-check scholars catch the corruption IF any of the 5 are among the 50 corrupted entries. With 50/4300+ corrupted entries, the probability of catching at least one in 5 samples is ~5.7%. **Verdict:** Weak for targeted attacks on non-famous scholars.
- **§4.B.8 cross-validation:** Usul-Data and Wikidata provide independent death dates. If the corruption disagrees with both, it's caught. **Verdict:** Strong for scholars present in all three sources. Weak for scholars only in OpenITI.
- **§6 confidence cap:** Death dates from OpenITI are not single-LLM inferences, so the 0.85 cap doesn't apply. OpenITI is treated as a verified source.

**Fix applied:** OpenITI death dates are now treated with the same provenance tracking as any other data source. When a scholar's death date comes ONLY from OpenITI (no corroboration from Usul-Data, Wikidata, source text, or LLM inference), it carries a maximum confidence of 0.90 (not 0.99). When corroborated by at least one other source, confidence can reach 0.99. This ensures that purely-OpenITI data is still treated as excellent quality but not infallible, and the `data_provenance_score` (Scenario 9) correctly reflects single-source dependence.

**Residual risk:** MEDIUM. For scholars only present in OpenITI, the corruption is undetectable by automated means. Mitigation: the spot-check list should be expanded over time as the library grows, and periodic full cross-validation sweeps (Layer 3 integrity checks) compare all scholar dates against Wikidata.

### A.3 — KNOWLEDGE_INTEGRITY.md Invariant Verification

Every invariant verified against every §4.A and §4.B rule:

**Invariant 1: Frozen sources are immutable.**

| Rule | Protection | Verified? |
|------|-----------|-----------|
| §4.A.2 Step 6 | SHA-256 pre/post copy verification | ✓ Defect-free |
| §4.A.2 Step 6 | chmod 0444 after freezing | ✓ Defect-free |
| §4.A.2 Step 6 | SRC_FREEZE_COPY_CORRUPT on hash mismatch | ✓ Defect-free |
| §4.A.2 Step 6 | SRC_FREEZE_PERMISSION_FAILED if chmod fails | ✓ Defect-free |
| §4.A.2 Step 6 | SRC_STAGING_MODIFIED (TOCTOU) | ✓ Defect-free |
| §4.A.2 Step 6 | Cleanup failure (Scenario 6 fix) | ✓ Fixed this session |
| §2 enrichment invariant #1 | No enrichment may modify frozen_hash or frozen files | ✓ Defect-free |
| §4.B.6 edition comparison | Reads normalized text, never frozen files | ✓ Defect-free |

**Invariant 2: Primary text is never modified.**

| Rule | Protection | Verified? |
|------|-----------|-----------|
| §4.A.3 metadata extraction | Reads source for metadata only, does not modify | ✓ Defect-free |
| §4.A.4 LLM inference | Receives first 2000 chars as input, source unchanged | ✓ Defect-free |
| §4.B.10 tahqiq fingerprinting | Reads footnote text sample, does not modify | ✓ Defect-free |
| All §4.B capabilities | All operate on metadata or external data; none modify source text | ✓ Defect-free |

**Invariant 3: Every claim is traceable.**

| Rule | Protection | Verified? |
|------|-----------|-----------|
| §4.A.1 source identity | Every source has source_id, work_id, author canonical_id | ✓ Defect-free |
| §4.A.5 scholar authority | Every scholar linked to sources_encountered_in | ✓ Defect-free |
| §4.B.7 genealogy | chain_sources records provenance of every link | ✓ Improved: LLM-only links now qualified (Scenario 3 fix) |
| §4.B.8 cross-validation | record_sources tracks every external data source | ✓ Defect-free |
| §4.B.5 KITAB | kitab_uri_match and kitab_match_confidence recorded | ✓ Defect-free |

**Invariant 4: Errors fail loudly.**

| Rule | Protection | Verified? |
|------|-----------|-----------|
| §4.A.2 all steps | 26+ error codes in §7, every step has defined error handling | ✓ Defect-free |
| §4.A.2 Step 6 cleanup | SRC_FREEZE_CLEANUP_FAILED added (Scenario 6 fix) | ✓ Fixed this session |
| §4.B.1 OpenITI | SRC_OPENITI_CACHE_CORRUPT added (Scenario 11 fix) | ✓ Fixed this session |
| §4.A.2 Step 7 | Lock timeout logs and defers (Scenario 1 fix) | ✓ Fixed this session |
| §4.B.5 KITAB | SRC_KITAB_CACHE_MISSING, SRC_KITAB_CACHE_CORRUPT | ✓ Defect-free |
| §4.B.8 Wikidata | SRC_WIKIDATA_TIMEOUT | ✓ Defect-free |
| §4.B.8 Usul-Data | SRC_USUL_DATA_MISSING | ✓ Defect-free |
| §4.B.6 comparison | SRC_COMPARISON_DEFERRED | ✓ Improved: inconclusive threshold added (Scenario 4 fix) |
| §4.B.7 genealogy | Ambiguous names → genealogy_ambiguous flag | ✓ Defect-free |

**Invariant 5: Human gates are not optional.**

| Rule | Protection | Verified? |
|------|-----------|-----------|
| §5 Layer 2 | 9 human gate triggers defined | ✓ Defect-free |
| §2 invariant #2 | work_id and author changes require human gate | ✓ Defect-free |
| §2 invariant #5 | Trust upgrade requires human gate | ✓ Defect-free (Scenario 12 made explicit) |
| §4.A.8 trust downgrade | Downgrade applied immediately (conservative direction) | ✓ Defect-free |
| §4.B.6 edition preference | Advisory only — requires owner confirmation | ✓ Defect-free |
| §4.B.7 genealogy ambiguity | Ambiguous names create human gate | ✓ Defect-free |
| No bypass mechanism defined | Correct: the source engine has no human gate bypass | ✓ Defect-free |

**Invariant 6: Metadata flows forward, never backward-deleted.**

| Rule | Protection | Verified? |
|------|-----------|-----------|
| §2 invariant #3 | No enrichment may set non-null field to null | ✓ Defect-free |
| §2 invariant #4 | Every update records previous value in metadata_history | ✓ Defect-free |
| §3 D-023 | Source metadata record is origin of metadata chain | ✓ Defect-free |
| §4.A.5 scholar records | revision_history preserves all changes | ✓ Defect-free |
| §4.B capabilities | All add metadata, none remove | ✓ Defect-free |
| Stale-marking cascade | §5 Layer 3 — flags affected products, doesn't delete metadata | ✓ Defect-free |

### A.4 — External Data Integration Corruption Defenses

Summary of corruption defenses for each external data source:

| External Source | Integrity Check | Failure Mode | Fallback | Blocks Intake? |
|----------------|----------------|-------------|----------|----------------|
| OpenITI CSV | Header + 5 spot-checks + SHA-256 | SRC_OPENITI_CACHE_CORRUPT | LLM-only inference | No |
| KITAB CSV | Header + 3 spot-checks + SHA-256 | SRC_KITAB_CACHE_CORRUPT | Skip compositional profile | No |
| Usul-Data JSON | Structure + 5 spot-checks + SHA-256 | SRC_USUL_DATA_MISSING | OpenITI + Wikidata only | No |
| Wikidata SPARQL | HTTP response validation, 3 retries | SRC_WIKIDATA_TIMEOUT | OpenITI + Usul-Data only | No |

All external data integration is additive and non-blocking. No single external source failure prevents intake.

### A.5 — New Error Codes Added This Session

| Code | Severity | Trigger | Recovery |
|------|----------|---------|----------|
| `SRC_FREEZE_CLEANUP_FAILED` | Fatal | Cannot delete corrupt frozen directory | Log. Create CORRUPT_FREEZE marker. Source stays in staging. Manual cleanup required. |
| `SRC_OPENITI_CACHE_CORRUPT` | Warning | OpenITI CSV fails integrity verification | Discard file. Skip OpenITI enrichment. Fall back to LLM-only. |
| `SRC_COMPARISON_INCONCLUSIVE` | Info | Edition comparison alignment below 20% threshold | Write comparison record with null recommendation. Create human gate for manual review. |

### A.6 — Contracts.py Changes Required

The following contract model changes are required to support hardening fixes. Changes should be applied in the next PRECISION or IMPLEMENTATION_PREP session:

1. **EnrichmentRequest model:** Add `verification_context` field (optional dict with `expected_work_id` and `expected_author_canonical_id`). For critical field enrichments, this field is required.
2. **ScholarAuthorityRecord model:** Add `data_provenance_score` field (float, 0.0-1.0). Add to existing `cross_validation` or as a top-level field.
3. **ErrorCode enum:** Add `FREEZE_CLEANUP_FAILED`, `OPENITI_CACHE_CORRUPT`, `COMPARISON_INCONCLUSIVE`.
4. **EditionComparisonSummary model:** Make `preferred_edition_recommendation` Optional[str] (currently str) to support inconclusive comparisons.
5. **GenealogyMetadata model:** Add `link_provenance` field (dict mapping each teacher/student canonical_id to its source: "llm_only", "openiti_corroborated", "wikidata_corroborated", "source_text", "multi_source").
6. **Configuration (§8):** Add `staging_lock_timeout` parameter (default: 3600 seconds, valid range: 300-86400).
