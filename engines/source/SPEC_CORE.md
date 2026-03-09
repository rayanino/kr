# Source Engine — محرك المصادر — Core Specification

**Stage:** 1 (Core Pipeline v0.0.1)
**Core formats:** `shamela_html`, `plain_text`
**Classification basis:** CORE_VS_DEFERRED.md

---

## 1. Purpose and Scope

The source engine is the pipeline entry point. It accepts raw knowledge material from the owner, establishes the identity model for every source, work, and scholar in the library, captures and infers metadata, freezes original files for integrity, detects duplicates, evaluates trustworthiness, and produces the metadata record that every downstream engine consumes.

**Core scope (Stage 1):**
- Accept Shamela HTML exports and plain text files through manual acquisition
- Assign canonical identifiers to sources, works, and scholars
- Extract metadata from format-specific structure (Shamela info.html, plain text first line)
- Infer missing metadata via LLM (genre, science, author identity, structural format, multi-layer composition)
- Verify author identification and work matching via multi-model consensus
- Freeze raw source files with SHA-256 integrity hashes
- Detect duplicates at source level (exact hash) and work level (same work, different edition)
- Evaluate trustworthiness and assign verified/flagged tier
- Track work-to-work relationships (sharh→matn, hashiyah→sharh, etc.)
- Create and maintain scholar authority records
- Accept enrichment write-backs from downstream engines with invariant enforcement
- Produce the source metadata record consumed by the normalization engine and all downstream engines

**Not in scope for Stage 1:**
- PDF, EPUB, Word, image, or owner-authored content intake (formats deferred to Stage 2)
- Autonomous discovery from repositories
- External enrichment (OpenITI, Usul-Data, Wikidata)
- Citation network discovery, edition comparison, gap analysis
- Scholarly genealogy, source difficulty prediction, tahqiq fingerprinting
- Dashboard views, per-science configuration hooks

**Normalization boundary:** The source engine sits entirely above the normalization boundary. Its output (frozen files + metadata record) is consumed by the normalization engine. The source metadata record flows downstream through the entire pipeline — no engine may strip metadata fields (D-023).

---

## 2. Input Contract

### 2.1 Manual Acquisition

The owner places source material in the intake staging area (`library/staging/`).

**Supported formats (Stage 1):**

1. **Shamela HTML export.** A directory containing either (a) a single `.htm` or `.html` content file plus an `info.html` metadata file, or (b) numbered `.htm` files (multi-volume) plus an `info.html` metadata file. The `info.html` file contains a metadata table with author, title, publisher, muhaqiq, and category information. The content files contain `<div class="page">` elements with `<span class="vol">` and `<span class="pg">` page markers, and CSS classes (`matn`, `sharh`, `hashiyah`, `footnote`) indicating text layers. Detection criteria: directory containing at least one `.htm` or `.html` file, with either an `info.html` present OR page-structured HTML content (containing `class="page"` divs).

2. **Plain text.** A single `.txt` file containing Arabic text. Metadata is minimal: title from the first non-empty line, author unknown. Most metadata comes from LLM inference (§4.A.4). Detection criteria: file with `.txt` extension.

All other file types are rejected with `SRC_UNSUPPORTED_FORMAT`.

**Input validation:** The source material must exist and be non-empty. Empty files or directories are rejected with `SRC_EMPTY_INPUT`. File encoding must be UTF-8 or a detectable Arabic encoding (CP1256, ISO-8859-6); if encoding detection fails, the intake aborts with `SRC_UNSUPPORTED_FORMAT` and a message suggesting the owner verify the file encoding.

### 2.2 Enrichment Write-Back

Downstream engines write metadata corrections back to source records via structured `EnrichmentRequest` objects specifying: `source_id`, `updates` (field→value mapping), `requesting_engine`, `timestamp`, and optionally `reason`.

**Enrichment invariants (exhaustive — an enrichment is rejected with `SRC_INVALID_ENRICHMENT` if it violates ANY):**

1. **Frozen file immutability.** No enrichment may modify `frozen_hash`, `frozen_path`, `frozen_file_hashes`, or any frozen file content.
2. **Identity immutability.** No enrichment may modify `source_id`. Changes to `work_id` or `author.canonical_id` require a human gate checkpoint (`SRC_ENRICHMENT_CRITICAL_FIELD`).
3. **No field deletion.** Enrichment may add new fields or update existing values. No enrichment may set an existing non-null field to null.
4. **History preservation.** Every field update must record the previous value, the updating engine, and the timestamp in `metadata_history`. An enrichment without `requesting_engine` is rejected.
5. **Trust tier protection.** No enrichment may set `trust_tier` to `verified` directly — only the trust evaluation algorithm (§4.A.8) or an explicit `owner_override` can do this. Enrichment may trigger trust re-evaluation by updating evaluation-relevant fields.
6. **Schema compliance.** The updated record must pass SourceMetadata Pydantic validation after the enrichment is applied.
7. **Referential integrity.** `author.canonical_id` must resolve in `scholars.json`, `work_id` must resolve in `works.json`.
8. **Re-processing depth limit.** When enrichment triggers downstream re-processing and the re-processed output generates a further enrichment on the same source field that was just changed, the second enrichment is NOT auto-submitted. A human gate checkpoint is created instead.
9. **Verification context for critical fields.** Enrichments to `author.canonical_id`, `work_id`, `genre`, or `science_scope` must include a `verification_context` with `expected_work_id` and `expected_author_canonical_id` matching the actual source. Mismatches cause rejection (catches source_id targeting errors).

**Critical field enrichment gate.** Enrichments to `author.canonical_id`, `work_id`, `genre`, or `science_scope` — regardless of source — trigger: (a) WARNING-level logging of old and new values, (b) human gate checkpoint for owner confirmation before applying, (c) stale-marking cascade on all downstream products from this source if confirmed.

---

## 3. Output Contract

### 3.1 Primary Artifacts

**Frozen source files.** The raw source material, copied to `library/sources/{source_id}/frozen/` and set read-only (`chmod 0444`). A SHA-256 hash is computed per file, and a composite hash is recorded. No component may modify frozen files after creation. For multi-file sources, each file is individually hashed.

**Source metadata record.** A JSON file at `library/sources/{source_id}/metadata.json`, conforming to the `SourceMetadata` Pydantic model in `contracts.py`. The engine validates the record against the model, verifies referential integrity, and confirms confidence thresholds before every write. Validation failure aborts the write with a structured error.

**Guarantees about the metadata record** (enforced by §5 Layer 1 before every write):
- Every required field has a non-null value. Optional fields may be null but are explicitly present (not absent).
- `source_id` is globally unique.
- `work_id` correctly groups this source with other sources of the same abstract work.
- `author.canonical_id` references a confirmed entry in the scholar authority registry.
- `trust_tier` reflects a conscious evaluation, not a default.
- `text_fidelity` reflects text data quality, separate from scholarly trustworthiness.
- All fields present at intake are preserved through enrichment. Overwritten values preserved in `metadata_history`.

### 3.2 Registry Updates

All registry writes are validated against their Pydantic models and applied atomically (§4.A.2 Step 7).

**Source registry** (`library/registries/sources.json`). Each entry conforms to `SourceRegistryEntry`: `source_id`, `work_id`, `human_label`, `title_arabic`, `author_canonical_id`, `trust_tier`, `processing_status`, `frozen_hash`, `intake_timestamp`, `acquisition_path`, `error_detail`.

**Work registry** (`library/registries/works.json`). Each entry conforms to `WorkRegistryEntry`: `work_id`, `canonical_title`, `author_canonical_id`, `genre`, `science_scope`, `source_ids`, `preferred_source_id`, `relationships`, `status`, `volumes_present`, `volumes_missing`.

**Scholar authority registry** (`library/registries/scholars.json`). Each entry conforms to `ScholarAuthorityRecord` (22 defined fields). The source engine is the primary writer. Structure and semantics defined in §4.A.5.

### 3.3 Metadata Pass-Through (D-023)

The source metadata record is the origin point for the metadata chain. The normalization engine embeds `source_id` in the normalized package. Every downstream engine accesses the full source metadata via this reference. Fields consumed downstream include:

- Author identity (`canonical_id`, biographical data, school affiliations)
- Work classification (`genre`, `genre_chain`, `science_scope`, `level`, `structural_format`)
- Edition quality (`muhaqiq`, `publisher`, `trust_tier`, `text_fidelity`)
- Work relationships (sharh_of, hashiyah_on, etc.)
- Multi-layer composition (`is_multi_layer`, `text_layers` with per-layer author)
- Source authority level

No field is "just for documentation" — each has a specific downstream consumer.

---

## 4. Processing Specification

### §4.A — Core Processing

#### §4.A.1 — Source Identity Model

The source identity model has three tiers: sources, works, and scholars.

**Source identity.** Every acquired source receives a `source_id` formatted as `src_{8_char_hex}` where the hex string is the first 8 characters of the frozen source's composite SHA-256 hash. If a collision occurs (checked against the source registry), append `_2`, `_3`, etc. The `source_id` is assigned at freeze time and never changes.

The `human_label` field preserves a human-readable shorthand for logs and owner interaction. It is NOT a primary key and need not be unique (warn on duplicates). Assignment: if the owner provides one, use it; otherwise generate from the work title's distinctive words via transliteration, lowercased, underscored, max 30 characters.

**Work identity.** A work (مؤلَّف) is the abstract intellectual creation independent of any particular edition. Format: `wrk_{author_slug}_{title_slug}`, max 50 characters total. Slugs are generated as follows:

```
def generate_slug(arabic_text: str, table: dict) -> str:
    """Generate a Latin slug from Arabic text.
    
    1. Check configurable table for exact or substring match (longest match first).
    2. If no match: apply rule-based transliteration.
    3. Truncate to max 20 characters per component.
    4. If result is empty: use first 8 hex chars of MD5 hash.
    """
    # Check table (sorted by key length descending for longest-match-first)
    for arabic, latin in sorted(table.items(), key=lambda kv: len(kv[0]), reverse=True):
        if arabic in arabic_text:
            return latin
    
    # Rule-based fallback: strip diacritics, map common patterns
    result = strip_diacritics(arabic_text)
    result = result.replace("ال", "al_").replace(" ", "_")
    result = transliterate_chars(result)  # ب→b, ت→t, etc.
    result = re.sub(r'[^a-z0-9_]', '', result.lower())
    result = re.sub(r'_+', '_', result).strip('_')
    
    if not result:
        return hashlib.md5(arabic_text.encode()).hexdigest()[:8]
    return result[:20]
```

**Initial transliteration table** (stored at `library/config/transliteration.json`):
```json
{
  "scholars": {
    "ابن عقيل": "ibn_aqil",
    "ابن مالك": "ibn_malik",
    "ابن قدامة": "ibn_qudamah",
    "سيبويه": "sibawayhi",
    "الجويني": "juwayni",
    "ابن هشام": "ibn_hisham",
    "الأشموني": "ashmuni",
    "الصبان": "sabban",
    "ابن حجر": "ibn_hajar",
    "النووي": "nawawi",
    "الغزالي": "ghazali",
    "ابن تيمية": "ibn_taymiyyah",
    "ابن كثير": "ibn_kathir"
  },
  "titles": {
    "ألفية": "alfiyyah",
    "المغني": "mughni",
    "الورقات": "waraqat",
    "الكتاب": "kitab",
    "قطر الندى": "qatr_alnada",
    "شرح": "sharh",
    "حاشية": "hashiyah",
    "مختصر": "mukhtasar"
  }
}
```

The table is extensible by the owner. Slug generation checks `scholars` and `titles` tables separately for author and title components.

The same work may have multiple sources (different tahqiq editions, different formats). When a new source is processed, the engine checks the work registry for an existing match. Matching uses normalized title comparison (strip definite articles, normalize hamza forms and taa marbuta) combined with author `canonical_id` matching:
- Confidence ≥ 0.85 → auto-link to existing work
- Confidence 0.50–0.85 → human gate checkpoint for owner confirmation
- Confidence < 0.50 → create new work record

The work record tracks `preferred_source_id` (defaults to first source acquired, changeable by owner).

**Multi-volume works.** A multi-volume work is ONE work with ONE `work_id`. Each volume may be a separate source or a single source depending on how it was acquired. `SourceMetadata.volumes` lists volume numbers and file mappings. The work registry tracks `volumes_present` and `volumes_missing`.

**Scholar identity.** Every author and muhaqiq receives a canonical identity in the scholar authority registry (§4.A.5).

**Worked example — Identity assignment for شرح ابن عقيل على ألفية ابن مالك:**

1. Frozen files produce SHA-256 composite hash `a7c3e91f...` → `source_id: "src_a7c3e91f"`.
2. Author slug: `ibn_aqil`. Title slug: `sharh_alfiyyah`. → `work_id: "wrk_ibn_aqil_sharh_alfiyyah"`.
3. Work registry check: no match → new work record created.
4. Scholar authority check: LLM identifies author as ابن عقيل (d. 769 AH). No existing record → new record `sch_00001`. Confidence: 0.96.
5. Owner provided `human_label: "ibn_aqil"` → used as-is.

#### §4.A.2 — Acquisition Workflow

Nine sequential steps. Each step has defined inputs, outputs, and error handling.

**Step 1: Staging.** Source material arrives in `library/staging/`. The owner places files there directly.

**Step 2: Format detection.** The engine examines staged material and determines `source_format`. Detection logic:

```
def detect_format(path: Path) -> SourceFormat:
    if path.is_dir():
        files = list(path.iterdir())
        htm_files = [f for f in files if f.suffix.lower() in ('.htm', '.html') and f.name != 'info.html']
        has_info = (path / 'info.html').exists()
        if htm_files and (has_info or _has_page_structure(htm_files[0])):
            return SourceFormat.SHAMELA_HTML
        # Check for single text file in directory
        txt_files = [f for f in files if f.suffix.lower() == '.txt']
        if len(txt_files) == 1:
            return SourceFormat.PLAIN_TEXT
    elif path.is_file():
        if path.suffix.lower() == '.txt':
            return SourceFormat.PLAIN_TEXT
        if path.suffix.lower() in ('.htm', '.html'):
            if _has_page_structure(path) or (path.parent / 'info.html').exists():
                return SourceFormat.SHAMELA_HTML
    raise SourceError(ErrorCode.UNSUPPORTED_FORMAT, f"Cannot detect format of {path}")
```

`_has_page_structure(html_file)` checks whether the file contains `<div` elements with `class="page"` — the defining marker of Shamela HTML content.

**Step 3: Metadata extraction.** Format-specific extractor runs (§4.A.3). Produces a sparse `dict` of extracted fields.

**Step 4: Metadata inference.** LLM enriches the sparse metadata (§4.A.4). Author identification and work matching use multi-model consensus (§6).

**Step 5: Duplicate detection.** Deduplication checks run (§4.A.7).

**Step 6: Freezing.** Exact sequence:
1. Compute SHA-256 hash of each staged file ("staging hashes").
2. Copy staged files to `library/sources/{source_id}/frozen/`.
3. Compute SHA-256 hash of each frozen file ("frozen hashes").
4. Compare: if any staging hash ≠ corresponding frozen hash → delete frozen directory → abort with `SRC_FREEZE_COPY_CORRUPT`.
5. Set frozen files read-only: `chmod 0444`. If permission change fails → delete frozen directory → abort with `SRC_FREEZE_PERMISSION_FAILED`.
6. If frozen directory deletion also fails (e.g., disk full): log `SRC_FREEZE_CLEANUP_FAILED` (Fatal) → write marker file `library/sources/{source_id}/CORRUPT_FREEZE` → on startup, engine treats these as requiring manual cleanup.

**Staging lock.** Between Step 2 and Step 6, the engine places a lock file (`library/staging/{source_dir}/.kr_processing`). At freeze time, file modification timestamps are compared against those recorded at format detection. If any file changed → abort with `SRC_STAGING_MODIFIED`. Orphaned locks older than `staging_lock_timeout` (default: 3600s) are cleaned up on startup.

**Step 7: Registration.** All registry updates are prepared in memory, validated (§5 Layer 1), then written atomically:
1. Write intended changes to `library/logs/pending_registration_{source_id}.json`.
2. Apply changes to each registry file (sources.json, works.json, scholars.json). Before each write, create a `.bak` copy.
3. Delete the pending registration file.

On startup, check for orphaned pending registration files. If one exists, the previous registration was interrupted: complete or roll back based on which files were already updated. A registry file with JSON parse failure is restored from its `.bak` copy.

**Registry file locking.** Steps 4, 5, and 7 acquire an exclusive file lock on the target registry file before reading. Step 4's scholar matching holds the lock on `scholars.json` through record creation. Step 5's work matching holds the lock on `works.json` through record creation. Step 7 re-verifies that no concurrent process created the same `canonical_id` or `work_id` since the lock was acquired. If lock cannot be acquired within 30 seconds → defer intake to `staging` status with retry scheduled.

**Step 8: Trustworthiness evaluation.** Runs the trust evaluation algorithm (§4.A.8).

**Step 9: Handoff.** Source marked `status: "acquired"`, available for normalization engine.

After successful registration, the staging directory is renamed to `library/staging/.processed/{source_id}/` (preserving originals for audit).

#### §4.A.3 — Format-Specific Metadata Extraction

Each source format has a dedicated extractor module. Extractors are minimal: they pull what the format provides, then hand off to LLM inference (§4.A.4) for enrichment.

**Shamela HTML extractor.** Parses `info.html` to extract metadata fields. Concrete extraction rules:

```
def extract_shamela_metadata(source_dir: Path) -> dict:
    info_path = source_dir / "info.html"
    result = {}
    
    if not info_path.exists():
        # Fallback: extract from first content file
        raise SourceError(ErrorCode.FORMAT_STRUCTURE_MISSING, 
            "info.html absent; will extract from content")
    
    html = info_path.read_text(encoding="utf-8")
    
    # Title: from <h1> tag
    h1_match = re.search(r"<h1>(.*?)</h1>", html, re.DOTALL)
    if h1_match:
        result["title_arabic"] = strip_tags(h1_match.group(1)).strip()
    
    # Table fields: each <tr> has <td>key</td><td>value</td>
    field_map = {
        "المؤلف": "author_name_raw",
        "المحقق": "muhaqiq_name_raw",
        "الناشر": "publisher",
        "الطبعة": "edition_raw",
        "عدد الأجزاء": "volume_count_raw",
        "التصنيف": "shamela_category",
        "الوصف": "description",
    }
    for tr_match in re.finditer(
        r"<tr>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*</tr>", html, re.DOTALL
    ):
        key = strip_tags(tr_match.group(1)).strip()
        value = strip_tags(tr_match.group(2)).strip()
        if key in field_map:
            result[field_map[key]] = value
    
    # Parse volume count from content files
    content_files = sorted(
        [f for f in source_dir.iterdir() 
         if f.suffix.lower() in ('.htm', '.html') and f.name != 'info.html'],
        key=lambda f: f.stem
    )
    result["content_file_count"] = len(content_files)
    
    # Count pages from <span class="pg"> markers in content files
    page_count = 0
    for cf in content_files:
        content = cf.read_text(encoding="utf-8")
        page_count += len(re.findall(r'class="pg"', content))
    result["page_count"] = page_count if page_count > 0 else None
    
    # Detect multi-layer from CSS classes in content
    if content_files:
        sample_content = content_files[0].read_text(encoding="utf-8")
        result["has_matn_class"] = 'class="matn"' in sample_content
        result["has_sharh_class"] = 'class="sharh"' in sample_content
        result["has_hashiyah_class"] = 'class="hashiyah"' in sample_content
    
    # Store format-specific metadata
    result["format_specific_metadata"] = {}
    if "shamela_category" in result:
        result["format_specific_metadata"]["shamela_category"] = result["shamela_category"]
    if "description" in result:
        result["format_specific_metadata"]["shamela_description"] = result["description"]
    
    return result
```

If `info.html` is absent but content files exist (numbered `.htm` files with page structure), the extractor: raises `SRC_FORMAT_STRUCTURE_MISSING`, extracts title from the first `<div class="title">` or `<h1>` in the first content file, extracts author from any `المؤلف` text in the first content file, flags all extracted fields as `needs_review`.

If `info.html` exists but the table parsing extracts zero fields (empty or malformed table), the extractor treats this as equivalent to missing `info.html`: logs `SRC_FORMAT_STRUCTURE_MISSING`, flags all fields as `needs_review`. Specifically, if `author_name_raw` is absent after parsing, the source is treated as having no format-extracted author — all author identification relies entirely on LLM inference, and the owner is notified via `needs_review_fields` including `"author"`.

**Plain text extractor.** Minimal extraction from a `.txt` file:

```
def extract_plaintext_metadata(file_path: Path) -> dict:
    text = file_path.read_text(encoding="utf-8")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    
    result = {
        "title_arabic": lines[0] if lines else file_path.stem,
        "page_count": None,  # Not meaningful for plain text
        "format_specific_metadata": {
            "char_count": len(text),
            "line_count": len(lines),
        },
    }
    return result
```

All other metadata (author, genre, science, structural format) comes from LLM inference (§4.A.4). The plain text extractor produces the sparsest metadata of any format — the LLM must fill almost everything.

#### §4.A.4 — LLM-Assisted Metadata Inference

After format-specific extraction produces a sparse metadata record, the engine uses LLM inference to fill gaps, validate extracted data, and enrich with scholarly context.

**Inference input.** The LLM receives a structured prompt containing:
- Extracted metadata (title, author name if available, publisher, category)
- First 2000 characters of source text (from the first content file for Shamela, from the text file for plain text)
- Table of contents if available (chapter headings from Shamela content)
- Library context: list of existing work_ids and scholar canonical_ids for matching

**Required prompt elements** (exact wording is an implementation detail refined in Step 2, but the prompt MUST include all of these):
1. A system message establishing the LLM as an Islamic bibliographic specialist with knowledge of classical Arabic scholarship, genre conventions, scholarly chains, and science classifications.
2. The extracted metadata fields formatted as key-value pairs.
3. The first 2000 characters of source text, or an explicit note that no text sample is available.
4. For Shamela sources: whether CSS layer classes (matn, sharh, hashiyah) were detected in the content.
5. The JSON output schema with field descriptions and enum values for each constrained field.
6. An instruction to return ONLY the JSON object with no preamble, explanation, or markdown formatting.
7. An instruction to set confidence to 0.50 for any field the LLM is genuinely uncertain about rather than guessing.

**Inference output schema.** The LLM must return a JSON object conforming to this structure:

```json
{
  "genre": "sharh",                          // Genre enum value
  "genre_confidence": 0.95,
  "genre_chain": {                           // null if standalone work
    "relation_type": "sharh_of",
    "base_work_title": "ألفية ابن مالك",
    "base_work_author": "ابن مالك"
  },
  "genre_chain_confidence": 0.93,
  "structural_format": "commentary",         // StructuralFormat enum value
  "structural_format_confidence": 0.90,
  "is_multi_layer": true,
  "multi_layer_confidence": 0.95,
  "layers": [                                // Only when is_multi_layer = true
    {"layer_type": "matn", "author_name": "ابن مالك"},
    {"layer_type": "sharh", "author_name": "ابن عقيل"}
  ],
  "science_scope": ["nahw"],
  "science_scope_confidence": 0.97,
  "level": "intermediate",                   // WorkLevel enum value
  "level_confidence": 0.88,
  "authority_level": "primary",              // AuthorityLevel enum value
  "authority_level_confidence": 0.90,
  "author_identification": {
    "canonical_name_ar": "بهاء الدين عبد الله بن عقيل الهمداني المصري",
    "known_as": ["ابن عقيل"],
    "death_date_hijri": 769,
    "school_affiliations": {"nahw": null, "fiqh": null},
    "scholarly_standing": "Classical grammarian, author of the most widely taught sharh of the Alfiyyah"
  },
  "author_identification_confidence": 0.96
}
```

Note: `text_fidelity` is NOT part of the LLM output. It is set deterministically by the engine after inference, based on `source_format`:
- `shamela_html` → `"high"` (structured digital text)
- `plain_text` → `"medium"` (no structural markup, but text is digital)

[ASSUMPTION — NEEDS STEP 2 TESTING] The LLM can produce this structured JSON reliably for well-known Islamic scholarly works. Testing should cover: (1) works with unambiguous titles like "شرح ابن عقيل", (2) works with ambiguous titles, (3) plain text with no metadata beyond a title line.

**Confidence scoring.** Every inferred field carries a confidence score 0.0–1.0. Fields with confidence < 0.70 are added to `needs_review_fields`. Fields with confidence < 0.50 block the metadata write entirely (§5 Layer 1) and create a human gate checkpoint.

**LLM response validation.** After parsing the LLM JSON response, validate each enum-constrained field: `genre` against `Genre` enum, `structural_format` against `StructuralFormat` enum, `authority_level` against `AuthorityLevel` enum, `level` against `WorkLevel` enum. If a field value is not in its enum: (1) check a configurable synonym table (e.g., `"منظومة"` → `"nazm"`, `"commentary"` → `"sharh"`) stored at `library/config/genre_synonyms.json`; (2) if no synonym match, set the field to the most conservative value (`"other"` for genre, `"mixed"` for structural_format) with confidence 0.50 and add to `needs_review_fields`; (3) log a WARNING with the invalid value for debugging prompt quality.

**Single-LLM biographical inference cap.** Scholar biographical data (death dates, school affiliations, teacher-student links) inferred by a single LLM are capped at confidence 0.85, regardless of what the LLM reports. This ensures single-model biographical data is always treated as provisional (§6).

**Multi-model consensus for critical fields.** Author identification and work matching use two-model consensus (§6). The consensus mechanism runs independently from the single-model inference above: two LLMs independently process the same prompt, and their results are compared.

**Genre inference rules.** The LLM infers genre from title conventions and content:
- `genre` must be one of the `Genre` enum values in contracts.py (18 values: `matn`, `sharh`, `hashiyah`, `mukhtasar`, `nazm`, `risalah`, `taqrirat`, `mawsuah`, `fatawa`, `mujam`, `tabaqat`, `fiqh_comparative`, `hadith_collection`, `tafsir`, `sirah`, `tarikh`, `adab`, `other`)
- Title keywords are strong signals: "شرح" → `sharh`, "مختصر" → `mukhtasar`, "حاشية" → `hashiyah`, "نظم" → `nazm`, "رسالة" → `risalah`
- No additional genres may be added without updating both the SPEC and the `Genre` enum

**Multi-layer detection.** The engine must determine whether a source contains text from multiple authors (e.g., a sharh quoting the matn). Detection uses two signals:
1. **CSS class detection (Shamela):** If the Shamela extractor found `has_matn_class` AND (`has_sharh_class` OR `has_hashiyah_class`), the source is multi-layer with high confidence (≥ 0.90).
2. **LLM inference:** The LLM infers `is_multi_layer` from genre (a sharh is always multi-layer by definition), title conventions, and content inspection.

When `is_multi_layer` is true, the `text_layers` field is populated with the type and author of each layer. The layer authors must be resolved to scholar authority records (creating new records if needed). This is critical because the normalization engine's layer detection depends on knowing which layers to expect (T-2 mitigation).

**Author disambiguation.** When the author name is ambiguous (e.g., "ابن حجر" could be al-Asqalani d. 852 or al-Haytami d. 974), the LLM uses context clues: science scope, genre, death date, other metadata. If disambiguation confidence < 0.80, a human gate checkpoint is created with the candidate identities presented.

**Worked example — LLM inference for plain text file "متن الفية ابن مالك فى علم النحو والصرف":**

Input: title = "متن الفية ابن مالك فى علم النحو والصرف", first 2000 chars = Arabic verse text with ¤ separators.

LLM output:
```json
{
  "genre": "matn",
  "genre_confidence": 0.95,
  "genre_chain": null,
  "structural_format": "verse",
  "structural_format_confidence": 0.97,
  "is_multi_layer": false,
  "science_scope": ["nahw", "sarf"],
  "science_scope_confidence": 0.98,
  "level": "intermediate",
  "level_confidence": 0.85,
  "authority_level": "primary",
  "authority_level_confidence": 0.95,
  "author_identification": {
    "canonical_name_ar": "محمد بن عبد الله بن مالك الطائي الجياني",
    "known_as": ["ابن مالك"],
    "death_date_hijri": 672,
    "school_affiliations": {"nahw": null},
    "scholarly_standing": "Author of the Alfiyyah, the most famous didactic poem in Arabic grammar"
  },
  "author_identification_confidence": 0.99
}
```

#### §4.A.5 — Scholar Authority Model

The scholar authority registry (`library/registries/scholars.json`) stores every scholar encountered. The source engine creates records; other engines enrich them.

**Scholar record structure.** Each record conforms to `ScholarAuthorityRecord` in contracts.py (22 defined fields):

- **Identity:** `canonical_id` (format: `sch_{5_digit_sequence}`), `canonical_name_ar` (full Arabic name, immutable after creation), `known_as` (common names), `name_variants`, `kunya`, `laqab`, `nisba`
- **Dates:** `birth_date_hijri`, `birth_date_ce`, `death_date_hijri`, `death_date_ce`, `death_date_approximate`, `era_century_hijri`
- **Geography:** `geographic_origin`, `geographic_active`
- **Scholarship:** `school_affiliations` (dict: science → school), `teachers` (list of canonical_ids), `students` (list of canonical_ids), `known_works` (list of work_ids), `scholarly_standing`, `methodology_notes`
- **Disambiguation:** `disambiguation_notes` (e.g., "When 'ابن حجر' appears in hadith → likely sch_00042")
- **Metadata:** `sources_encountered_in`, `record_completeness` (fraction of 22 fields with non-null values), `data_provenance_score` (fraction of biographical fields corroborated by non-LLM sources; 0.0 for Stage 1 since no external sources), `record_sources`, `revision_history`, `last_updated`

The `canonical_id` sequence is monotonically increasing: `sch_00001`, `sch_00002`, etc. The next available ID is determined by scanning the registry for the highest existing ID.

**Record creation.** When the engine encounters an author not in the registry, it creates a new record populated from: (1) metadata extracted from the source, (2) LLM inference. The record is validated against `ScholarAuthorityRecord` before writing.

**Record matching.** When the engine encounters an author name that might match an existing record, matching uses:
- Normalized name comparison: strip diacritics, normalize hamza/taa marbuta, compare against all `name_variants` and `known_as`
- Death date comparison (if available): match within ±10 years
- School affiliation comparison (if available)
- Known works comparison (if available)

Match score computation (weighted average of available signals):

```
def compute_scholar_match_score(candidate_name, candidate_death_date, 
                                 candidate_school, candidate_known_work,
                                 existing_record) -> float:
    signals = []
    
    # Name match (weight 0.50): compare normalized candidate against 
    # all name_variants + known_as + canonical_name_ar
    all_names = [existing_record.canonical_name_ar] + existing_record.known_as + existing_record.name_variants
    best_name_sim = max(
        normalized_name_similarity(candidate_name, variant) 
        for variant in all_names
    )
    signals.append((best_name_sim, 0.50))
    
    # Death date match (weight 0.30): if both have dates
    if candidate_death_date and existing_record.death_date_hijri:
        diff = abs(candidate_death_date - existing_record.death_date_hijri)
        date_score = 1.0 if diff == 0 else max(0.0, 1.0 - diff / 50.0)
        signals.append((date_score, 0.30))
    
    # School match (weight 0.10): if both have school affiliations
    if candidate_school and existing_record.school_affiliations:
        school_match = candidate_school in existing_record.school_affiliations.values()
        signals.append((1.0 if school_match else 0.0, 0.10))
    
    # Known works match (weight 0.10): if candidate has a known work title
    if candidate_known_work and existing_record.known_works:
        works_match = any(
            normalized_title_similarity(candidate_known_work, w) > 0.80
            for w in existing_record.known_works
        )
        signals.append((1.0 if works_match else 0.0, 0.10))
    
    # Weighted average of available signals
    total_weight = sum(w for _, w in signals)
    return sum(s * w for s, w in signals) / total_weight if total_weight > 0 else 0.0
```

`normalized_name_similarity(a, b)`: strip diacritics, normalize hamza forms (أ إ آ → ا) and taa marbuta (ة → ه), strip definite article (ال), then compute character-level similarity ratio. Two names that are identical after normalization score 1.0. Names sharing a distinctive component (e.g., both contain "ابن عقيل") but differing in patronymic details score 0.70–0.90 depending on overlap.

Scoring thresholds: ≥ 0.85 → auto-link; 0.50–0.85 → human gate; < 0.50 → new record.

[ASSUMPTION — NEEDS STEP 2 TESTING] The name normalization and similarity scoring produce accurate matches. Test with: (1) exact match ("ابن عقيل" vs "ابن عقيل"), (2) variant spelling ("ابن عقيل الهمداني" vs "بهاء الدين ابن عقيل"), (3) different scholars with similar names ("ابن حجر العسقلاني" vs "ابن حجر الهيتمي").

**Progressive enrichment.** Each time a source mentions an existing scholar, the engine checks whether the new source provides information the existing record lacks. If so, the record is updated (with all overwritten values preserved in `revision_history`).

**Scholar record consistency checks on update.** Five checks run before any enrichment is applied:

1. **Death date drift.** If existing `death_date_hijri` differs from proposed value by > 5 years → `SRC_SCHOLAR_DATE_CONFLICT` → human gate.
2. **School affiliation change.** If existing school affiliation would change to a different school → `SRC_SCHOLAR_SCHOOL_CONFLICT` → human gate. (A scholar's school is a stable biographical fact.)
3. **Name change.** If `canonical_name_ar` would be modified → blocked. New name variants go to `known_as`.
4. **Teacher/student self-reference.** If a scholar would be added as their own teacher/student → rejected.
5. **Temporal consistency.** If a proposed teacher's death date is AFTER the student's death date by more than 30 years → `SRC_SCHOLAR_TEMPORAL_INCONSISTENCY` → human gate. (Within 30 years is plausible — a teacher may outlive a student.)

**Muhaqiq records.** Tahqiq editors are scholars. Each muhaqiq gets a full `ScholarAuthorityRecord`. The source metadata links to both the original author's `canonical_id` and the muhaqiq's `canonical_id`.

**Data provenance score.** In Stage 1 (no external enrichment sources), the `data_provenance_score` will be 0.0 for all records (everything is LLM-inferred). The field exists as an extension hook for Stage 2. The synthesizer uses this score to qualify biographical claims: ≥ 0.50 → direct statements; < 0.30 → hedged statements.

[EXTENSION HOOK] Core must not assume LLM is the only data source for scholar records. The `record_sources` list and `data_provenance_score` accommodate external sources (OpenITI, Usul-Data, Wikidata) in Stage 2.

#### §4.A.6 — Relevance Evaluation

[DEFERRED TO STAGE 2] — Relevance evaluation for autonomous discovery candidates.
[EXTENSION HOOK] — Core must not embed relevance logic in the main acquisition flow; it only applies to autonomous discovery, which has a separate entry point.

#### §4.A.7 — Deduplication

Two levels of deduplication.

**Source-level deduplication (exact duplicate).** After freezing (Step 6), the composite SHA-256 hash is compared against all `frozen_hash` values in the source registry.

If match found:
- Log `SRC_DUPLICATE_EXACT` with the matching `source_id`.
- Do NOT acquire. Delete the frozen directory just created.
- Record the alternative repository/path in a log entry for reference.
- Exception: if the owner sets a `force_reacquire` flag, bypass deduplication (used for corruption recovery).

**Work-level matching (same work, different edition).** Two sources represent the same abstract work when they share author + title but differ in tahqiq, publisher, edition, or format. This is NOT a duplicate — both sources are acquired and linked to the same `work_id`. Detection happens during work identity assignment (§4.A.1): the work matching algorithm identifies this case. The engine logs `SRC_DUPLICATE_WORK` (Info) and notifies the owner: "This appears to be a different edition of {work_title}, which you already have as {existing_source_id}. Acquiring as a new source of the same work."

[DEFERRED TO STAGE 2] — Near-duplicate detection using text similarity.
[EXTENSION HOOK] — Deduplication must not assume only exact-hash matching. The modular structure allows adding similarity-based checks without changing the core flow.

#### §4.A.8 — Trustworthiness Evaluation

The engine assesses each source's reliability to determine the default verified/flagged classification.

**Five evaluation factors** with weights:

| Factor | Weight | Input Source | Scoring Rules |
|--------|--------|-------------|---------------|
| Author scholarly standing | 0.30 | Scholar authority record | Classical scholar (death_date_hijri ≤ 900 AH AND scholarly_standing non-null AND record existed before this intake): **0.90**. Known scholar (record exists in registry): **0.70**. Unknown (record just created from this intake with no prior sources): **0.30**. |
| Tahqiq quality | 0.25 | Muhaqiq name | Recognized muhaqiq (in configurable list, §8): **0.90**. Unknown muhaqiq: **0.50**. No muhaqiq, pre-modern work (author death_date_hijri ≤ 1300): **0.40**. No muhaqiq, modern work: **0.30**. |
| Publisher reputation | 0.15 | Publisher name | Known scholarly publisher (in configurable list, §8): **0.80**. Unknown/absent: **0.40**. |
| Source authority | 0.15 | `authority_level` | `primary`: **0.85**. `reference`: **0.60**. `modern_compilation`: **0.40**. |
| Text fidelity | 0.15 | `text_fidelity` | `high`: **0.90**. `medium`: **0.60**. `low`: **0.30**. `unknown`: **0.40**. |

**Combined score:** weighted sum of (factor_weight × factor_score).

**Trust tiers:**
- `verified`: combined score ≥ 0.65. Excerpts default to verified knowledge.
- `flagged`: combined score < 0.65, OR any individual factor scores critically low (author_standing < 0.30 AND muhaqiq score < 0.40). Flag reason is recorded.
- `owner_override`: owner has manually set the tier. Original evaluation preserved in metadata.

[ASSUMPTION — NEEDS STEP 2 TESTING] The weights (0.30, 0.25, 0.15, 0.15, 0.15) and threshold (0.65) produce sensible results. Test with: (1) Ibn Aqil/Abd al-Hamid → expect verified, (2) unknown modern author/no muhaqiq/photos → expect flagged, (3) borderline cases.

**Conservative bias.** When evaluation is genuinely uncertain, the source is flagged. Flagging a reliable source is correctable; verifying an unreliable source contaminates the library.

**Special cases:**
- Owner-authored content: always `verified`. [Note: owner-authored intake is deferred, but when it becomes core, the trust rule is pre-defined.]
- Quran text from canonical digital sources: always `verified` with maximum trust.
- Hadith canonical collections (الكتب الستة + Muwatta) from recognized tahqiq: always `verified`.

**Trust evaluation output.** Stored in `SourceMetadata` as:
- `trust_tier`: TrustTier enum value
- `trust_score`: float (the combined weighted score)
- `trust_factors`: list of `TrustworthinessFactor` objects (one per factor, each with `name`, `weight`, `score`, `reason`)
- `trust_reason`: human-readable summary

**Trust re-evaluation on enrichment.** When enrichment modifies any of the five trust input fields (`author.canonical_id`, `muhaqiq`, `publisher`, `authority_level`, `text_fidelity`), the engine re-runs the trust evaluation with updated values.
- If upgrade `flagged` → `verified`: human gate checkpoint (upgrading trust is high-risk).
- If downgrade `verified` → `flagged`: applied immediately (conservative direction) + stale-marking cascade on all excerpts from this source.
- Updated `trust_factors` recorded; old evaluation preserved in `metadata_history`.

**Worked example — Trust evaluation for شرح ابن عقيل:**

| Factor | Weight | Score | Reason | Weighted |
|--------|--------|-------|--------|----------|
| author_standing | 0.30 | 0.90 | Classical grammarian, widely recognized | 0.270 |
| tahqiq_quality | 0.25 | 0.90 | محمد محيي الدين عبد الحميد in recognized list | 0.225 |
| publisher_reputation | 0.15 | 0.70 | دار التراث — known scholarly publisher | 0.105 |
| source_authority | 0.15 | 0.85 | Primary source (classical sharh) | 0.128 |
| text_fidelity | 0.15 | 0.90 | Shamela structured HTML → high | 0.135 |

Combined: 0.863 → `verified`.

#### §4.A.9 — Work Relationship Tracking

The engine maintains a graph of work-to-work relationships.

**Relationship types** (matching `GenreRelationType` enum):
- `sharh_of(work_a, work_b)`: work_a is a commentary on work_b
- `hashiyah_on(work_a, work_b)`: work_a is a marginal commentary on work_b
- `mukhtasar_of(work_a, work_b)`: work_a is an abridgment of work_b
- `nazm_of(work_a, work_b)`: work_a is a versified summary of work_b
- `taqrirat_on(work_a, work_b)`: work_a contains lecture notes on work_b
- `responds_to(work_a, work_b)`: work_a is a response/refutation of work_b
- `cites(work_a, work_b)`: work_a references work_b (discovered during processing)

**Discovery mechanism.** Relationships are discovered at intake through LLM inference from the title and genre chain. When the LLM infers a `genre_chain` (§4.A.4), the engine:
1. Identifies the base work title and author.
2. Searches the work registry for a matching `work_id`.
3. If found → creates a `WorkRelationshipEdge` linking the two works.
4. If not found → creates a placeholder work record with `status: "referenced_not_acquired"` and creates the edge to the placeholder. The placeholder must conform to `WorkRegistryEntry` before persisting.

**Storage.** Relationships are stored as `WorkRelationshipEdge` objects in the work registry entry's `relationships` list. Each edge has: `from_work_id`, `to_work_id`, `relation_type`, `confidence`, `discovered_by`.

**Worked example — حاشية الصبان على شرح الأشموني على ألفية ابن مالك:**

LLM analysis: "حاشية" → `hashiyah`. "على شرح الأشموني" → base work is شرح الأشموني على ألفية ابن مالك. That base work is itself a sharh of ألفية ابن مالك.

Registry operations:
- Search for شرح الأشموني → not found → create placeholder `wrk_ashmuni_sharh_alfiyyah` with `status: "referenced_not_acquired"`.
- Search for ألفية ابن مالك → found as `wrk_ibn_malik_alfiyyah`.
- Create edges: `hashiyah_on(wrk_sabban, wrk_ashmuni)` confidence 0.97; `sharh_of(wrk_ashmuni, wrk_ibn_malik_alfiyyah)` confidence 0.95.

[DEFERRED TO STAGE 2] — Citation discovery from excerpting engine (`cites` relationship type populated by downstream).
[EXTENSION HOOK] — The `discovered_by` field on edges must accept values beyond `"source_engine"` to accommodate citation discovery.

#### §4.A.10 — Processing Status Tracking

Each source has a `processing_status` from the `ProcessingStatus` enum:
- `staging` → `acquired` → `normalizing` → `normalized` → `processing` → `complete`
- Any stage → `error` (with `error_detail` specifying stage + error code + reason)
- Owner decision → `withdrawn` (frozen files and metadata preserved for audit)

The source engine owns the `staging` → `acquired` transition. Other engines update status as they process. All transitions are logged with timestamps in `library/logs/source_engine.jsonl`.

[DEFERRED TO STAGE 2] — Dashboard view (counts per status, blocked sources).
[EXTENSION HOOK] — Status transition logging must include enough data (timestamps, stage, error codes) to build a dashboard later.

---

### §4.B — Deferred Capabilities

All §4.B capabilities are deferred to Stage 2. Each is preserved as a placeholder with its extension hook.

**§4.B.1 — External Metadata Enrichment via OpenITI Corpus.** [DEFERRED] Enriches scholar records with OpenITI metadata (death dates, known works). [EXTENSION HOOK] Scholar `record_sources` list must accommodate `"openiti_metadata"`.

**§4.B.2 — Bibliographic Intelligence from Minimal Input.** [DEFERRED] Extended bibliographic profiling beyond §4.A.4's core inference. Core §4.A.4 already provides the fundamental capability.

**§4.B.3 — Citation Network Discovery.** [DEFERRED] Cross-engine citation graph from excerpting engine discoveries. [EXTENSION HOOK] Work registry `relationships` list accepts edges from any `discovered_by` source.

**§4.B.4 — Acquisition Gap Analysis.** [DEFERRED] Coverage gap detection and acquisition recommendations. [EXTENSION HOOK] Work registry `status: "referenced_not_acquired"` records serve as gap seeds.

**§4.B.5 — KITAB Text Reuse Integration.** [DEFERRED] Compositional profiling from KITAB corpus data. [EXTENSION HOOK] `SourceMetadata.compositional_profile` Optional field preserved.

**§4.B.6 — Edition Comparison Intelligence.** [DEFERRED] Automated comparison of 2+ editions. [EXTENSION HOOK] Work registry tracks multiple `source_ids` per work.

**§4.B.7 — Scholarly Genealogy Auto-Construction.** [DEFERRED] Multi-generational teacher-student chain construction. [EXTENSION HOOK] Scholar record `teachers`/`students` are lists of canonical_ids; `genealogy_metadata` Optional field preserved.

**§4.B.8 — Cross-Validated Scholar Authority Bootstrapping.** [DEFERRED] Three-source cross-validation (OpenITI, Usul-Data, Wikidata). [EXTENSION HOOK] Scholar record `cross_validation` Optional field preserved; `data_provenance_score` already accommodates external sources.

**§4.B.9 — Source Difficulty Prediction.** [DEFERRED] Pipeline difficulty prediction before processing. [EXTENSION HOOK] `SourceMetadata.difficulty_prediction` Optional field preserved.

**§4.B.10 — Tahqiq Apparatus Fingerprinting.** [DEFERRED] Footnote analysis to classify tahqiq quality. [EXTENSION HOOK] `SourceMetadata.tahqiq_fingerprint` Optional field preserved.

---

## 5. Validation and Quality

### Layer 1: Self-Validation (automated, before every metadata write)

Five checks run in order. Any failure aborts the write.

1. **Schema compliance.** Validate the metadata record against `SourceMetadata` Pydantic model. Missing required field, type mismatch, or constraint violation → abort with structured error.

2. **Referential integrity.** `author.canonical_id` must resolve in `scholars.json`. `work_id` must resolve in `works.json`. Genre chain work references must resolve (or exist as placeholder records). Invalid reference → abort.

3. **Confidence threshold check.** If any critical field (`author.canonical_id`, `work_id`, `genre`, `science_scope`) has confidence < 0.50 → abort write → create human gate checkpoint. (0.50–0.70 fields are written with `needs_review` flags; < 0.50 blocks entirely.)

4. **Duplicate re-check.** After inference (which may have changed title or author), re-run deduplication. This catches cases where raw metadata didn't match but inferred metadata does.

5. **Consistency cross-check.** Inferred fields are checked for mutual consistency:
   - Genre vs. structural_format: `nazm` → should be `verse`; `sharh` → should be `commentary` or `prose`.
   - Level vs. genre: `hashiyah` → should not be `beginner`.
   - Science scope vs. author: if `science_scope` doesn't overlap with the author's known specializations (from `school_affiliations`), flag `SRC_METADATA_INCONSISTENCY` with human gate (author-science mismatch often indicates misidentified author).
   - Inconsistencies are flagged as warnings (not blocking) and trigger `needs_review` on the inconsistent fields, EXCEPT author-science mismatch which triggers a human gate.

### Layer 2: Human Gate Review

The following conditions trigger human gate checkpoints (stored as `HumanGateCheckpoint` objects):

- Author disambiguation with confidence < 0.80
- Work matching with confidence between 0.50 and 0.85
- Any critical field with confidence < 0.70
- Trust evaluation resulting in `flagged` (owner may override)
- Multi-model consensus disagreement on author or work identification
- Genre chain relationship where the base work is not in the library
- Author-science mismatch from consistency cross-check

Human gate reviews are batched: the owner reviews all pending checkpoints for a source at once, not one field at a time. The review interface presents: inferred metadata with confidence scores, specific fields needing review, alternatives considered.

### Layer 3: Progressive Correction

Source metadata is living. Downstream engines discover corrections via the enrichment write-back (§2.2). Every correction is logged with: correcting agent, timestamp, old value, new value. Corrections to fields already consumed downstream trigger stale-marking cascades.

**Scholarly integrity guarantee.** No source enters the library without:
1. A canonical author identity linked to the scholar authority model
2. A work classification (genre, science scope)
3. A trustworthiness evaluation
4. Frozen original files with integrity hashes

---

## 6. Consensus Integration

Multi-model consensus is used for exactly two decisions.

**1. Author identification.** Two LLMs from different providers (configured in §8, default: Anthropic + OpenAI) independently process the metadata inference prompt. Agreement is defined as:
- **Existing scholar match:** Both models return the same `canonical_id` from the registry.
- **New scholar (neither finds a match):** Both models agree no existing record matches, AND both models' author identification metadata agrees on (a) the canonical Arabic name after normalization (normalized_name_similarity ≥ 0.90), and (b) the death date within ±10 years (or both return null for death date).
- **Disagreement:** One model matches an existing record, the other says "new" — OR both match different existing records — OR both say "new" but disagree on name/death date.

Agreement → accept. For the "new scholar" case, the engine creates a new record using merged metadata from both models (prefer the model with higher stated confidence for any disagreeing biographical fields). Disagreement → human gate checkpoint (`SRC_CONSENSUS_DISAGREEMENT`).

**2. Work matching.** Two LLMs independently evaluate whether the new source belongs to an existing work. Agreement → accept. Disagreement → human gate.

**Consensus is NOT used for:** genre, science scope, structural format, trust evaluation, scholar biographical details. These have lower cascade risk and their correctness is verifiable by downstream engines.

**Consensus failure handling (asymmetric by cascade risk):**
- Author identification (highest cascade risk): if one model times out or fails, a single-model result is NOT accepted. Human gate checkpoint with the single model's suggestion.
- Work matching (lower cascade risk): if one model fails, the single model's result is accepted provisionally with `single_model_confidence` flag and `needs_review` on `work_id`.

**Implementation.** The consensus module exposes:
```python
async def evaluate(task: str, prompt: str, models: list[str], 
                   threshold: str = "agreement") -> ConsensusResult:
    """Run the same prompt through multiple models, compare results.
    
    Returns: ConsensusResult with agreed (bool), result (the agreed value 
    or None), per_model_results (dict), and reason (str).
    """
```

The source engine calls `evaluate` twice during Step 4: once for author identification, once for work matching. Each call sends the same structured prompt to both models and parses the JSON output.

[ASSUMPTION — NEEDS STEP 2 TESTING] Two-model consensus catches most attribution errors. Test: run the same prompt through Claude and GPT on 10+ fixtures. Measure agreement rate and accuracy of each model independently.

---

## 7. Error Handling

### Core Error Codes

| Code | Severity | Trigger | Recovery |
|------|----------|---------|----------|
| `SRC_UNSUPPORTED_FORMAT` | Fatal | Unrecognized file type (not shamela_html or plain_text) | Reject. Owner converts or provides differently. |
| `SRC_EMPTY_INPUT` | Fatal | Empty file or directory | Reject. |
| `SRC_INVALID_ENRICHMENT` | Warning | Enrichment violates any of the 9 invariants | Reject enrichment. Log. Notify originating engine. |
| `SRC_DUPLICATE_EXACT` | Info | SHA-256 match in registry | Do not acquire. Log alternative availability. |
| `SRC_DUPLICATE_WORK` | Info | Same work, different edition | Acquire. Link to existing work_id. Notify owner. |
| `SRC_AUTHOR_AMBIGUOUS` | Warning | Author disambiguation confidence < 0.80 | Human gate checkpoint. Source waits. |
| `SRC_WORK_MATCH_UNCERTAIN` | Warning | Work matching confidence 0.50–0.85 | Human gate checkpoint. Source waits. |
| `SRC_LOW_CONFIDENCE` | Warning | Critical field confidence < 0.50 | Block metadata write. Human gate checkpoint. |
| `SRC_METADATA_INCONSISTENCY` | Warning | Genre/format/level inconsistency or author-science mismatch | Flag fields. Write metadata with warnings (or human gate for author-science mismatch). |
| `SRC_FREEZE_FAILED` | Fatal | File copy or hash computation failed | Abort. Source remains in staging. |
| `SRC_FREEZE_COPY_CORRUPT` | Fatal | Post-freeze hash mismatch | Delete frozen dir. Abort. |
| `SRC_FREEZE_PERMISSION_FAILED` | Fatal | Cannot chmod frozen files | Delete frozen dir. Abort. |
| `SRC_FREEZE_CLEANUP_FAILED` | Fatal | Cannot delete corrupt frozen dir | Write CORRUPT_FREEZE marker. Manual cleanup. |
| `SRC_STAGING_MODIFIED` | Fatal | Files changed between detection and freezing | Abort. Owner re-stages. |
| `SRC_REGISTRY_CONFLICT` | Fatal | Registry write violates invariant | Abort registration. Log. |
| `SRC_REGISTRATION_INTERRUPTED` | Warning | Orphaned pending_registration on startup | Complete or roll back. Log outcome. |
| `SRC_CONSENSUS_DISAGREEMENT` | Warning | Two models disagree on author or work | Human gate checkpoint. |
| `SRC_ENRICHMENT_CRITICAL_FIELD` | Warning | Enrichment modifies high-cascade field | Human gate. Do not apply until confirmed. |
| `SRC_SCHOLAR_DATE_CONFLICT` | Warning | Death date enrichment differs > 5 years | Block update. Human gate. |
| `SRC_SCHOLAR_SCHOOL_CONFLICT` | Warning | School affiliation enrichment contradicts | Block update. Human gate. |
| `SRC_SCHOLAR_TEMPORAL_INCONSISTENCY` | Warning | Teacher-student death date gap > 30 years wrong direction | Flag. Human gate. |
| `SRC_FORMAT_STRUCTURE_MISSING` | Warning | Expected structural file absent (e.g., Shamela without info.html) | Fall back to minimal extraction + LLM inference. Flag all fields `needs_review`. |

**Deferred error codes** (only fire from deferred capabilities, not implemented in Stage 1): `SRC_OCR_LOW_QUALITY`, `SRC_REPO_UNAVAILABLE`, `SRC_KITAB_CACHE_MISSING`, `SRC_KITAB_CACHE_CORRUPT`, `SRC_USUL_DATA_MISSING`, `SRC_WIKIDATA_TIMEOUT`, `SRC_COMPARISON_DEFERRED`, `SRC_OPENITI_CACHE_CORRUPT`, `SRC_COMPARISON_INCONCLUSIVE`.

**Logging principle.** Every error is logged to `library/logs/source_engine.jsonl` as a `SourceError` object with: `timestamp`, `source_id` (if known), `error_code`, `severity`, `message`, `recovery_action` (one of: `rejected`, `human_gate_created`, `field_flagged`, `skipped`, `retry_scheduled`), and optional `context` dict. Fatal errors stop processing for the affected source but do not affect other sources. Warning errors allow processing to continue with affected fields marked `needs_review`. Info errors are logged only.

**Alert triggers.** Fatal error during batch processing. > 10% of sources in a batch hitting the same warning code. Human gate queue > 20 items.

**LLM call failure handling.** When an LLM call fails (timeout, API error, or response that does not parse as valid JSON):
1. First retry: same model, fresh request.
2. Second retry: same model, fresh request with simplified prompt (remove library context to reduce token count).
3. Both retries failed: log error, create human gate checkpoint with the source_id and inference step, mark source as `needs_manual_classification` in `needs_review_fields`.

For consensus calls (§6), failure handling is defined in the consensus section.

---

## 8. Configuration

### Core Parameters

| Parameter | Default | Valid Range | Description |
|-----------|---------|-------------|-------------|
| `staging_path` | `library/staging/` | Writable path | Intake staging area |
| `confidence_threshold_auto_accept` | 0.70 | 0.50–0.95 | Fields ≥ this accepted without review |
| `confidence_threshold_block` | 0.50 | 0.30–0.70 | Fields < this block metadata write |
| `trust_score_verified_threshold` | 0.65 | 0.50–0.80 | Combined trust score ≥ this → verified |
| `consensus_model_count` | 2 | 2–3 | Models for consensus |
| `consensus_model_providers` | `["anthropic", "openai"]` | Valid provider list | Must be different providers |
| `dedup_hash_algorithm` | `sha256` | `sha256` only | Hardcoded; changing breaks dedup |
| `human_gate_batch_size` | 20 | 5–50 | Max pending checkpoints before alert |
| `staging_lock_timeout` | 3600 | 300–86400 | Seconds before orphaned locks cleaned |

### Configurable Reference Lists

**Recognized muhaqiqs** (initial list):
شعيب الأرناؤوط, أحمد شاكر, عبد السلام هارون, عبد الله التركي, محمد فؤاد عبد الباقي, عبد القادر الأرناؤوط, محمد ناصر الدين الألباني, محمد محيي الدين عبد الحميد

Stored in `library/config/recognized_muhaqiqs.json`. Owner can extend.

**Known scholarly publishers** (initial list):
دار الرسالة, مؤسسة الرسالة, دار التراث, دار الكتب العلمية, المكتب الإسلامي, دار ابن حزم, دار ابن الجوزي

Stored in `library/config/known_publishers.json`. Owner can extend.

**Arabic transliteration table** for slug generation:
Stored in `library/config/transliteration.json`. Maps common Arabic scholar names and work titles to Latin slugs. Initial entries defined in §4.A.1. Extensible by the owner.

**Genre synonym table** for LLM response normalization:
Stored in `library/config/genre_synonyms.json`. Maps common non-standard genre values to valid `Genre` enum values. Initial entries:
```json
{
  "منظومة": "nazm", "نظم": "nazm", "commentary": "sharh",
  "مقالة": "risalah", "مجموع": "mawsuah"
}
```

### Hardcoded Values

- SHA-256 hash algorithm — changing breaks dedup and integrity.
- `source_id` format (`src_{8_char_hash}`) — changing requires re-keying.
- Trust tier names (`verified`, `flagged`, `owner_override`) — referenced by downstream engines.
- Freeze-before-process invariant — architectural guarantee.
- Enrichment invariant set (9 invariants) — removing any opens a corruption path.

---

## 9. Current Implementation State

**Existing code:**
- `engines/source/src/tracer.py` (253 lines): Tracer bullet Shamela intake. Parses `info.html`, freezes files, writes SourceMetadata JSON. Works for the `html_export_minimal` fixture. Hardcoded genre/structural_format (no LLM inference yet). No consensus, no trust evaluation, no scholar authority registry.
- `engines/source/src/extractors/` directory: Module stubs for each format. Only `shamela.py` and `plaintext.py` needed for Stage 1.
- `engines/source/src/engine.py`, `format_detector.py`, `trust_evaluator.py`, etc.: Module stubs.
- `engines/source/contracts.py` (825 lines): Full Pydantic models, validated by tracer bullet.

**Known gaps between tracer and this SPEC:**
1. Identity model: tracer uses ad-hoc IDs, not hash-based `source_id` or slug-based `work_id`.
2. Scholar authority: tracer has no registry, just inline `ScholarReference` dicts.
3. LLM inference: tracer hardcodes genre/format/science — no LLM calls.
4. Consensus: none.
5. Trust evaluation: tracer hardcodes `verified` with a single trust factor — no 5-factor algorithm.
6. Registry atomicity: tracer writes a single JSON file — no write-ahead log or locking.
7. Deduplication: tracer has no dedup logic.
8. Plain text: tracer only handles Shamela HTML.

---

## 10. Test Requirements

### Deterministic Tests (5a)

1. **Identity determinism.** Same input → same `source_id`, `work_id`, `human_label`. Verify on `html_export_minimal` and `alfiyyah_versified`.
2. **Deduplication.** Ingest same file twice → second rejected with `SRC_DUPLICATE_EXACT`. Ingest two editions of same work → both acquired, same `work_id`.
3. **Metadata completeness.** After intake, all required fields non-null. Confidence scores present for all inferred fields. `author.canonical_id` resolves in scholars.json.
4. **Trust consistency.** Classical work + known muhaqiq → `verified`. Unknown modern + no muhaqiq → `flagged`. Owner override → tier changes, original preserved.
5. **Scholar matching.** Same author (different spelling) → same `canonical_id`. Different scholars (similar names) → different `canonical_id`s.
6. **Work relationships.** Sharh title → genre chain + relationship edge. Standalone matn → no genre chain.
7. **Freeze integrity.** Frozen files match computed SHA-256. Attempt to modify frozen file → detected.
8. **Error codes.** Each of the 22 core error codes triggered at least once with correct code, severity, and recovery.

### LLM-Worker Tests (5b)

9. **Genre inference accuracy.** Run inference on ≥5 fixtures with known genres. ≥90% accuracy.
10. **Author identification accuracy.** Run inference on ≥5 fixtures. ≥85% accuracy.
11. **Consensus agreement rate.** Run consensus on ≥5 fixtures. Measure agreement rate and per-model accuracy.
12. **Multi-layer detection.** Run on multi-layer fixture (html_export_minimal) and single-layer fixture (alfiyyah_versified). Correct in both cases.

### Integration Tests

13. **Source → Normalization boundary.** Metadata record validates against normalization engine's input contract.
14. **Scholar authority → downstream.** Scholar records created during intake are queryable by synthesis engine.
15. **Enrichment write-back.** Downstream enrichment correctly applied, old value in `metadata_history`, stale-marking triggered for critical fields.

### Gold Baselines

No gold baselines exist yet. Create from: (1) `html_export_minimal` with manually verified metadata, (2) `alfiyyah_versified` with manually verified metadata.

---

## Appendix: Contract Field Alignment

Verified field names between this SPEC and `contracts.py`:

| SPEC Reference | contracts.py Model | Field | Match |
|----------------|-------------------|-------|-------|
| §4.A.5 ScholarReference | `ScholarReference` | `canonical_id`, `name_arabic`, `confidence`, `source_of_identification` | ✓ |
| §4.A.4 TextLayer | `TextLayer` | `layer_type`, `author` (ScholarReference) | ✓ |
| §4.A.8 TrustworthinessFactor | `TrustworthinessFactor` | `name`, `weight`, `score`, `reason` | ✓ |
| §4.A.4 InferredFieldConfidence | `InferredFieldConfidence` | `genre`, `science_scope`, `structural_format`, `authority_level`, `level`, `multi_layer`, `genre_chain` | ✓ |
| §3 MetadataHistoryEntry | `MetadataHistoryEntry` | `field`, `old_value`, `new_value`, `changed_by`, `timestamp` | ✓ |
| §4.A.9 WorkRelationshipEdge | `WorkRelationshipEdge` | `from_work_id`, `to_work_id`, `relation_type`, `confidence`, `discovered_by` | ✓ |
| §4.A.7 GenreChain | `GenreChain` | `relation_type`, `base_work_title`, `base_work_author`, `base_work_id`, `confidence` | ✓ |

All tracer findings from `TRACER_FINDINGS.md` §1 (15 field-level mismatches) are addressed: the SPEC now uses the exact field names from contracts.py (`name_arabic` not `display_name`, `source_of_identification` not omitted, `name` not `factor` for trust factors, etc.).
