# Source Engine Test Plan — خطة الاختبار

Maps SPEC sections → test cases → fixtures → expected outcomes.
Claude Code reads this to know what tests to write and in what order.

---

## Test Infrastructure

**Test framework:** pytest
**Fixtures directory:** `tests/fixtures/`
**Gold baselines:** None exist yet. First baselines from ibn_aqil_alfiyyah (Shamela-like) and waraqat_usul (PDF).
**Mocking:** LLM calls are mocked with deterministic responses for unit tests. Integration tests use live LLMs.

---

## 1. Format Detection (SPEC §4.A.2 Step 2)

| Test Case | Fixture | Expected |
|-----------|---------|----------|
| Shamela HTML detection | html_export_minimal/ | SourceFormat.SHAMELA_HTML |
| PDF detection | waraqat_usul/ | SourceFormat.PDF_TEXT or PDF_SCANNED |
| Image scan detection | photo_scan_ilm/ | SourceFormat.IMAGE_SCAN |
| Plain text detection | alfiyyah_versified/ | SourceFormat.PLAIN_TEXT |
| Word doc detection | mughni_comparative/ | SourceFormat.WORD_DOC |
| Owner-authored detection | owner_note/ | SourceFormat.OWNER_AUTHORED |
| Unsupported format | synthetic: .xyz file | SRC_UNSUPPORTED_FORMAT error |
| Empty directory | synthetic: empty dir | SRC_EMPTY_INPUT error |

---

## 2. Metadata Extraction (SPEC §4.A.3)

### 2.1 Shamela Extractor
| Test Case | Fixture | Expected |
|-----------|---------|----------|
| Full metadata extraction | html_export_minimal/ | title, author, page_count populated |
| Missing info.html fallback | synthetic: Shamela dir without info.html | SRC_FORMAT_STRUCTURE_MISSING, partial extraction from PageText |
| Malformed info.html | synthetic: invalid HTML | Warning logged, partial extraction |
| Volume structure detection | html_export_minimal/ (multi-file) | volume_count, volumes list populated |
| Format-specific metadata preserved | html_export_minimal/ | shamela_book_id in format_specific_metadata |

### 2.2 PDF Extractor
| Test Case | Fixture | Expected |
|-----------|---------|----------|
| PDF text extraction | waraqat_usul/ | title from PDF properties or first page |
| Multi-volume PDF | ibn_aqil_alfiyyah/ (4 vols) | volume_count=4, volumes mapping |
| Missing PDF metadata | synthetic: PDF with no properties | Fallback to text extraction from first page |

### 2.3 Image Extractor
| Test Case | Fixture | Expected |
|-----------|---------|----------|
| Title page OCR | photo_scan_ilm/ | title, author extracted (if OCR quality sufficient) |
| Low OCR confidence | synthetic: blurry image | SRC_OCR_LOW_QUALITY, human gate created |
| Required fields missing | photo_scan_ilm/ without owner hints | Human gate for title+author |

### 2.4 Plain Text Extractor
| Test Case | Fixture | Expected |
|-----------|---------|----------|
| Title from first line | alfiyyah_versified/ | title extracted |
| Diacritic preservation | alfiyyah_versified/ | Arabic diacritics intact in extracted text |

### 2.5 Word Document Extractor
| Test Case | Fixture | Expected |
|-----------|---------|----------|
| Multi-file Word intake | mughni_comparative/ | Treated as single multi-part source |
| CP1256 filename encoding | mughni_comparative/ | Filenames decoded to UTF-8 correctly |

### 2.6 Owner-Authored Extractor
| Test Case | Fixture | Expected |
|-----------|---------|----------|
| Valid input type | owner_note/ | owner_authored_type=TARJIH |
| Invalid input type | synthetic: unknown type | Rejection |

---

## 3. Metadata Inference (SPEC §4.A.4)

| Test Case | Fixture | Expected |
|-----------|---------|----------|
| Genre inference from title | ibn_aqil_alfiyyah/ | genre=SHARH, confidence >= 0.85 |
| Genre chain detection | ibn_aqil_alfiyyah/ | genre_chain: sharh_of → ألفية ابن مالك |
| Science scope inference | waraqat_usul/ | science_scope=["usul_al_fiqh"] |
| Level inference | alfiyyah_versified/ | Matn → often beginner |
| Structural format: verse | alfiyyah_versified/ | structural_format=VERSE |
| Multi-layer detection | ibn_aqil_alfiyyah/ | is_multi_layer=True, layers=[matn, sharh] |
| Confidence scores populated | any fixture | All InferredFieldConfidence fields non-null |
| Low confidence → needs_review | synthetic: obscure work | Fields with conf < 0.70 in needs_review_fields |
| Confidence < 0.50 blocks write | synthetic: unidentifiable source | Metadata write blocked, human gate created |
| Single-LLM bio inference cap | any fixture | Biographical data confidence never > 0.85 |

---

## 4. Identity Model (SPEC §4.A.1)

| Test Case | Fixture | Expected |
|-----------|---------|----------|
| source_id deterministic | ibn_aqil_alfiyyah/ | Same input → same source_id |
| source_id format | any | Matches src_{8_char_hash} pattern |
| work_id format | any | Matches wrk_{author_slug}_{title_slug} pattern |
| human_label from owner | any + hint | Owner-provided label used |
| human_label auto-generated | any without hint | Generated from title words |
| Work matching: new work | waraqat_usul/ (first time) | New work record created |
| Work matching: existing work | duplicate edition | Linked to existing work_id |
| Work matching: uncertain | synthetic: ambiguous match | Human gate at 0.50-0.85 confidence |

---

## 5. Scholar Authority (SPEC §4.A.5)

| Test Case | Fixture | Expected |
|-----------|---------|----------|
| New scholar creation | waraqat_usul/ | Scholar record for الجويني created |
| Scholar matching: exact | second source by same author | Linked to existing canonical_id |
| Scholar matching: variant name | synthetic: different spelling | Matched via name_variants |
| Scholar matching: ambiguous | synthetic: "ابن حجر" without context | Human gate created |
| Muhaqiq as scholar | ibn_aqil_alfiyyah/ | محمد محيي الدين عبد الحميد gets scholar record |
| Consistency: death date drift | synthetic: update with +10yr | SRC_SCHOLAR_DATE_CONFLICT |
| Consistency: school change | synthetic: بصري→كوفي | SRC_SCHOLAR_SCHOOL_CONFLICT |
| Consistency: name immutable | synthetic: change canonical_name_ar | Blocked |
| Consistency: self-reference | synthetic: scholar as own teacher | Rejected |
| Consistency: temporal | synthetic: teacher died 50yr after student | SRC_SCHOLAR_TEMPORAL_INCONSISTENCY |

---

## 6. Deduplication (SPEC §4.A.7)

| Test Case | Fixture | Expected |
|-----------|---------|----------|
| Exact duplicate: same hash | ibn_aqil_alfiyyah/ twice | SRC_DUPLICATE_EXACT, not acquired |
| Work-level match | second edition of same work | SRC_DUPLICATE_WORK (info), both acquired |
| No duplicate | two different works | No duplicate detected |
| Force re-acquisition | duplicate + force flag | Bypass deduplication |
| Post-inference re-check | synthetic: raw metadata differs but inferred matches | Caught on re-check |

---

## 7. Freezing (SPEC §4.A.2 Step 6)

| Test Case | Fixture | Expected |
|-----------|---------|----------|
| Successful freeze | any fixture | Files copied, hashes match, read-only set |
| Hash verification | any fixture | frozen_hash == staging hash for each file |
| Copy corruption detection | synthetic: modify during copy | SRC_FREEZE_COPY_CORRUPT |
| Permission failure | synthetic: unwritable directory | SRC_FREEZE_PERMISSION_FAILED |
| TOCTOU detection | synthetic: modify file after detection | SRC_STAGING_MODIFIED |
| Staging lock | any fixture | .kr_processing lock file created and removed |
| Multi-file composite hash | ibn_aqil_alfiyyah/ | All files individually hashed, composite recorded |
| Staging cleanup | any successful intake | Original moved to .processed/ |

---

## 8. Trustworthiness Evaluation (SPEC §4.A.8)

| Test Case | Fixture | Expected |
|-----------|---------|----------|
| Classical work: verified | ibn_aqil_alfiyyah/ | trust_tier=VERIFIED, score >= 0.65 |
| Unknown modern: flagged | synthetic: unknown author, no muhaqiq | trust_tier=FLAGGED |
| Owner-authored: verified | owner_note/ | trust_tier=VERIFIED (always) |
| Owner override | any flagged + override | trust_tier=OWNER_OVERRIDE, original preserved |
| Factor weights sum to 1.0 | any | Sum of trust_factors weights == 1.0 |
| Conservative bias | synthetic: genuinely uncertain | Flagged, not verified |
| Recognized muhaqiq list | ibn_aqil_alfiyyah/ | محمد محيي الدين عبد الحميد recognized |
| Owner-authored validation | synthetic: tarjih referencing unknown source | SRC_METADATA_INCONSISTENCY warning |

---

## 9. Work Relationships (SPEC §4.A.9)

| Test Case | Fixture | Expected |
|-----------|---------|----------|
| Sharh detection | ibn_aqil_alfiyyah/ | sharh_of → ألفية ابن مالك |
| Placeholder creation | ibn_aqil_alfiyyah/ if ألفية not in library | Placeholder work record created |
| Multi-level chain | synthetic: حاشية الصبان | hashiyah_on → شرح الأشموني, sharh_of → ألفية |
| Graph queryable | after multiple intakes | "all commentaries on X" returns correct list |

---

## 10. Registration (SPEC §4.A.2 Step 7)

| Test Case | Fixture | Expected |
|-----------|---------|----------|
| Atomic write: success | any | All 3 registries updated consistently |
| Atomic write: interrupted | synthetic: kill during write | Orphaned pending file detected on startup |
| Write-ahead log | any | pending_registration file created then deleted |
| Backup restoration | synthetic: corrupted registry JSON | .bak copy restores successfully |
| Schema validation before write | synthetic: invalid data | Write aborted, error logged |

---

## 11. Processing Status (SPEC §4.A.10)

| Test Case | Fixture | Expected |
|-----------|---------|----------|
| Status transitions logged | any successful intake | staging → acquired with timestamps |
| Error status | synthetic: normalization failure | status=ERROR, error_detail populated |
| Dashboard counts | multiple intakes | Correct count per status |

---

## 12. Enrichment Write-Back (SPEC §2)

| Test Case | Fixture | Expected |
|-----------|---------|----------|
| Valid enrichment applied | any + valid update | Field updated, history preserved |
| Frozen file immutability | synthetic: update frozen_hash | SRC_INVALID_ENRICHMENT rejection |
| Identity immutability | synthetic: update source_id | SRC_INVALID_ENRICHMENT rejection |
| Critical field gate | synthetic: update work_id | SRC_ENRICHMENT_CRITICAL_FIELD, human gate |
| No field deletion | synthetic: set field to null | Rejected |
| Missing engine ID | synthetic: no requesting_engine | Rejected |
| Schema compliance after | synthetic: update that breaks schema | Rejected |
| Referential integrity | synthetic: update author to nonexistent sch_ | Rejected |

---

## 13. Consensus (SPEC §6)

| Test Case | Fixture | Expected |
|-----------|---------|----------|
| Agreement on author | any | Both models agree → accepted |
| Disagreement on author | synthetic: ambiguous author | Human gate created |
| One model fails: author | synthetic: timeout | Human gate (not single-model fallback) |
| One model fails: work match | synthetic: timeout | Single model accepted + needs_review |
| Different providers used | any | Config enforces different providers |

---

## 14. Error Handling (SPEC §7)

Test every error code at least once:

| Error Code | Synthetic Trigger | Expected Severity |
|-----------|-------------------|-------------------|
| SRC_UNSUPPORTED_FORMAT | Unknown file extension | Fatal |
| SRC_EMPTY_INPUT | Empty file | Fatal |
| SRC_INVALID_ENRICHMENT | Bad enrichment request | Warning |
| SRC_DUPLICATE_EXACT | Same hash | Info |
| SRC_DUPLICATE_WORK | Same work, different edition | Info |
| SRC_AUTHOR_AMBIGUOUS | "ابن حجر" without context | Warning |
| SRC_WORK_MATCH_UNCERTAIN | 0.60 confidence match | Warning |
| SRC_LOW_CONFIDENCE | Critical field < 0.50 | Warning |
| SRC_METADATA_INCONSISTENCY | Nazm genre + prose format | Warning |
| SRC_FREEZE_FAILED | Write to read-only path | Fatal |
| SRC_REGISTRY_CONFLICT | Invariant violation | Fatal |
| SRC_OCR_LOW_QUALITY | Blurry image OCR | Warning |
| SRC_REPO_UNAVAILABLE | Network timeout | Warning |
| SRC_CONSENSUS_DISAGREEMENT | Models disagree | Warning |
| SRC_FREEZE_COPY_CORRUPT | Hash mismatch | Fatal |
| SRC_FREEZE_PERMISSION_FAILED | chmod fails | Fatal |
| SRC_STAGING_MODIFIED | File changed | Fatal |
| SRC_REGISTRATION_INTERRUPTED | Orphaned pending file | Warning |
| SRC_ENRICHMENT_CRITICAL_FIELD | Update to author/work_id | Warning |
| SRC_SCHOLAR_DATE_CONFLICT | Death date +10yr | Warning |
| SRC_SCHOLAR_SCHOOL_CONFLICT | School affiliation change | Warning |
| SRC_SCHOLAR_TEMPORAL_INCONSISTENCY | Bad teacher-student dates | Warning |
| SRC_FORMAT_STRUCTURE_MISSING | Shamela without info.html | Warning |

---

## 15. Integration Tests

| Test | What it verifies |
|------|-----------------|
| Source → Normalization handoff | Metadata record readable by normalization engine; source_id resolves |
| Source → Scholar registry | Scholar records queryable by downstream engines |
| Enrichment round-trip | Downstream enrichment → source update → history preserved → stale cascade triggered |
| Full intake pipeline | Staging → acquired for each fixture (ibn_aqil, waraqat, mughni, alfiyyah, photo_scan, owner_note) |

---

## Gold Baseline Plan

**Baseline 1: ibn_aqil_alfiyyah** (Shamela-like multi-volume)
- Manually verified metadata: author, muhaqiq, genre=sharh, genre_chain, science=nahw, level=intermediate
- Use as regression baseline for metadata inference changes

**Baseline 2: waraqat_usul** (PDF)
- Manually verified: author=الجويني, genre=matn, science=usul_al_fiqh, level=beginner
- Use as regression baseline for PDF extraction changes

Create baselines after first successful end-to-end intake of each fixture.
