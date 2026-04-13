# Session 4 Plan: Hashing + Dedup + Freezing

**Pipeline steps:** Steps 5–6 (Hashing + Dedup, Freezing)
**Depends on:** Session 3 (LLM inference + consensus)

---

## Read First

1. `engines/source/SPEC_CORE.md` §4.A.2 Steps 5–6 (Hashing, Freezing, Staging lock)
2. `engines/source/SPEC_CORE.md` §4.A.1 (source_id derivation from composite hash)
3. `engines/source/SPEC_CORE.md` §4.A.7 (Deduplication — both levels)
4. `engines/source/contracts.py` — `SourceRegistryEntry.frozen_hash`, `SourceMetadata.frozen_hash`, `SourceMetadata.frozen_file_hashes`
5. `engines/source/SPEC_CORE.md` §7 — error codes: `SRC_DUPLICATE_EXACT`, `SRC_DUPLICATE_WORK`, `SRC_FREEZE_COPY_CORRUPT`, `SRC_FREEZE_PERMISSION_FAILED`, `SRC_FREEZE_CLEANUP_FAILED`, `SRC_STAGING_MODIFIED`

## Modules to Build

| File | Purpose |
|------|---------|
| `engines/source/src/freezer.py` | Replace stub. SHA-256 per-file + composite hash computation, source_id derivation, file copy to `library/sources/{source_id}/frozen/`, post-copy hash verification, chmod 0444, staging lock verification, corruption handling |
| `engines/source/src/deduplication.py` | Replace stub. Source-level exact dedup (composite hash vs registry). Work-level semantic dedup (after inference — title + author match). |

## Fixtures to Test Against

- `tests/fixtures/shamela_real/01_nahw_simple/book.htm` — single file hashing
- `tests/fixtures/shamela_real/11_multi_small/` — multi-file hashing (3 .htm files)
- `tests/fixtures/shamela_real/12_multi_muq/` — multi-file with المقدمة.htm (included in hash, excluded from volumes)
- `tests/fixtures/alfiyyah_versified/` — plain text file hashing
- **Dedup test:** Ingest the same fixture twice → second should be rejected with `SRC_DUPLICATE_EXACT`
- **Uniqueness test:** Hash different fixtures → all produce different source_ids

## Carry-Forward Tasks

1. **Name matching A3-1 fix.** The token-based `normalized_name_similarity()` was copied to `shared/scholar_authority/src/name_matching.py` in Session 3. Verify it handles the A3-1 edge case: "النووي" vs "أبو زكريا يحيى بن شرف النووي" should score ≥ 0.85. Write a unit test for this specific case. If Session 3 did not complete this copy, do it now.

## Build Steps

1. **Implement `freezer.py`.** Three sub-operations:
   - `compute_file_hash(path) → str` — SHA-256 of a single file
   - `compute_composite_hash(file_hashes: dict[str, str]) → str` — SHA-256 of sorted JSON of per-file hashes
   - `derive_source_id(composite_hash: str) → str` — `src_{first_8_chars}` with collision check
   - `freeze_source(staged_path, source_id) → FreezeResult` — copy, verify, chmod
   - Staging lock check: compare file modification times against those recorded at format detection

2. **Implement `deduplication.py`.** Two checks:
   - `check_exact_duplicate(composite_hash, source_registry) → Optional[str]` — returns existing source_id if match
   - `check_work_duplicate(title, author_id, work_registry) → Optional[str]` — returns existing work_id if semantic match (post-inference)

3. **Error path testing.** Verify all freeze-related error codes fire correctly:
   - `SRC_FREEZE_COPY_CORRUPT` — tamper with a frozen file after copy, re-verify
   - `SRC_FREEZE_PERMISSION_FAILED` — mock chmod failure
   - `SRC_STAGING_MODIFIED` — modify a staged file between detection and freeze
   - `SRC_DUPLICATE_EXACT` — ingest same fixture twice

## Done When

- [ ] SHA-256 hashing produces deterministic results for all fixture types
- [ ] Composite hash is computed from sorted JSON of per-file hashes
- [ ] `source_id` derived correctly: `src_{first 8 chars of composite hash}`
- [ ] Collision detection works (append `_2`, `_3` if needed)
- [ ] Frozen files are byte-identical to originals (verified by post-copy hash)
- [ ] Frozen files are read-only (chmod 0444)
- [ ] Staging lock detects file modification between Steps 2 and 6
- [ ] Exact duplicate detection works (same file → rejected)
- [ ] Work-level duplicate detection works (same title+author → linked to existing work)
- [ ] All freeze error codes tested: COPY_CORRUPT, PERMISSION_FAILED, STAGING_MODIFIED, CLEANUP_FAILED
- [ ] A3-1 name matching unit test passes
- [ ] المقدمة.htm included in hash but excluded from volume numbering
