# NEXT — Source Engine Session 5b: Registries + Registration Orchestrator

**Session type:** BUILD — implement registry CRUD, registration orchestrator, work relationships, source-engine human gate wrapper
**Pipeline steps:** Step 7 (Registration), §4.A.9 (Work Relationships)
**Depends on:** Session 5a (447 tests passing: config, scholar authority, human gate, trust evaluator, validation)

---

## What to Read

Read these files in order before writing any code:

1. `engines/source/SPEC_CORE.md` §4.A.1 — Source Identity Model (source_id, work_id, human_label, slug generation, lines 141–210)
2. `engines/source/SPEC_CORE.md` §4.A.2 Step 7 — Registration (atomic WAL pattern, lines 442–449)
3. `engines/source/SPEC_CORE.md` §4.A.9 — Work Relationship Tracking (full section, lines 1366–1399)
4. `engines/source/SPEC_CORE.md` §3 — Output Contract (metadata.json, registry formats, lines 77–134)
5. `engines/source/contracts.py` — `SourceRegistryEntry`, `WorkRegistryEntry`, `WorkRelationshipEdge`, `GenreRelationType`, `RegistryPendingWrite`, `SourceMetadata`
6. `engines/source/docs/session5-architecture.md` — Module dependency graph and atomic write pattern
7. `library/config/transliteration.json` — Slug generation lookup tables (scholars + titles)

---

## What to Build (in dependency order)

### Module 1: `engines/source/src/text_utils.py` — extend with slug generation (~60 lines added)

The SPEC §4.A.1 defines `generate_slug()`, `strip_diacritics()`, `transliterate_chars()`, `TRANSLIT_MAP`, and `ARABIC_DIACRITICS`. These are currently specified in the SPEC but not implemented. The file already has `strip_tags()` — add the remaining utilities.

Implement:
- `ARABIC_DIACRITICS` constant (9 Unicode tashkeel marks from SPEC §4.A.1)
- `TRANSLIT_MAP` dict (28 Arabic → Latin mappings from SPEC §4.A.1)
- `strip_diacritics(text: str) -> str` — remove tashkeel
- `transliterate_chars(text: str) -> str` — map Arabic chars to Latin for slugs
- `generate_slug(arabic_text: str, table: dict) -> str` — SPEC algorithm:
  1. Check configurable table for exact or substring match (longest match first)
  2. If no match: strip diacritics, rule-based transliteration
  3. Truncate to max 20 chars per component
  4. If empty: use first 8 hex chars of MD5 hash
- `generate_work_id(author_name: str, title: str, transliteration_table: dict) -> str`
  - Format: `wrk_{author_slug}_{title_slug}`, max 50 characters total
  - Uses `generate_slug()` for each component with the appropriate sub-table ("scholars" for author, "titles" for title)
- `generate_human_label(title: str, transliteration_table: dict) -> str`
  - Transliterated, lowercased, underscored, max 30 characters

**Test:** `engines/source/tests/test_text_utils.py` — add tests for slug generation with Arabic text including diacritics, transliteration table lookups, fallback to rule-based, empty input → MD5 hash, max length truncation.

### Module 2: `engines/source/src/registries/source_registry.py` (~80 lines)
Replace the stub.

Implement:
- `build_entry(metadata: SourceMetadata) -> SourceRegistryEntry` — maps SourceMetadata fields to SourceRegistryEntry fields: source_id, work_id, human_label, title_arabic, author_canonical_id (from metadata.author.canonical_id), trust_tier, processing_status, frozen_hash, intake_timestamp, acquisition_path.
- `load(registry_path) -> dict[str, dict]` — load sources.json
- `save(registry_path, data)` — atomic JSON write with .bak
- `find_by_hash(frozen_hash, registry) -> Optional[str]` — used by dedup

**Test:** `engines/source/tests/test_registries.py`

### Module 3: `engines/source/src/registries/scholar_registry.py` (~80 lines)
Replace the stub. Thin wrapper around `shared/scholar_authority`.

Implement:
- `lookup_or_register_author(name, death_date, school, source_id, *, registry_path) -> tuple[ScholarReference, Optional[str]]`
  - Calls `shared.scholar_authority.src.lookup()`.
  - If auto_link: return existing record's canonical_id as ScholarReference, no gate.
  - If human_gate: return best match's canonical_id as ScholarReference, return gate checkpoint_id.
  - If new_record: create minimal ScholarAuthorityRecord, call `register()`, return new canonical_id.
  - The human gate is created by calling `shared.human_gate.src.human_gate.create_checkpoint()` with trigger=AUTHOR_DISAMBIGUATION.
- `lookup_or_register_muhaqiq(muhaqiq_name, source_id, *, registry_path) -> ScholarReference`
  - Same pattern but simpler — muhaqiqs have less data. Uses a higher tolerance for auto-linking (muhaqiq disambiguation is less critical).

**Test:** `engines/source/tests/test_registries.py`

### Module 4: `engines/source/src/registries/work_registry_store.py` (~150 lines)
Replace the stub.

Implement:
- `build_entry(metadata: SourceMetadata, transliteration_table: dict) -> WorkRegistryEntry`
  - Generates `work_id` using `generate_work_id()` from text_utils.
  - Maps: canonical_title (from metadata.title_arabic), author_canonical_id, genre, science_scope, source_ids=[metadata.source_id], preferred_source_id=metadata.source_id, status="acquired".
- `build_placeholder(title, author_canonical_id, work_id) -> WorkRegistryEntry`
  - SPEC §4.A.9: creates placeholder with `status: "referenced_not_acquired"`.
  - source_ids=[], preferred_source_id=None.
- `create_relationship_edge(from_work_id, to_work_id, relation_type, confidence, discovered_by) -> WorkRelationshipEdge`
- `process_genre_chain(metadata: SourceMetadata, work_registry: dict, scholar_registry_path: Path, transliteration_table: dict) -> list[WorkRelationshipEdge]`
  - SPEC §4.A.9 discovery mechanism:
    1. If metadata has genre_chain, extract base work title and author.
    2. Search work registry for matching work_id (by title + author).
    3. If found → create edge.
    4. If not found → create placeholder work + sparse scholar record for base work author → create edge to placeholder.
  - Returns list of edges to add to the work's relationships.
- `load(registry_path) -> dict[str, dict]`
- `save(registry_path, data)` — atomic write with .bak
- `find_by_title_author(title, author_canonical_id, registry) -> Optional[str]` — uses `normalized_name_similarity` for title comparison (threshold 0.80)

**Test:** `engines/source/tests/test_registries.py`

### Module 5: `engines/source/src/human_gate.py` (~60 lines)
Replace the stub. Source-engine convenience wrappers.

Implement 5 gate creation functions that map source-engine triggers to `shared.human_gate.src.human_gate.create_checkpoint()`:
- `gate_author_disambiguation(source_id, candidates, match_score, inferred_name)`
- `gate_consensus_disagreement(source_id, field, model_a_value, model_b_value, model_a_name, model_b_name)`
- `gate_low_confidence(source_id, field, value, confidence)`
- `gate_trust_flagged(source_id, trust_score, trust_factors)`
- `gate_scholar_conflict(source_id, canonical_id, conflict_type, existing_value, proposed_value)`

Each function constructs the appropriate `fields_to_review`, `current_values`, and `alternatives` for its trigger type, then delegates to `create_checkpoint()`.

**Test:** `engines/source/tests/test_registries.py` (or separate `test_human_gate_wrapper.py`)

### Module 6: `engines/source/src/registries/__init__.py` (~200 lines)
Replace the stub. Registration orchestrator.

Implement:
- `register_source(metadata: SourceMetadata, *, library_root, config) -> None`
  - SPEC §4.A.2 Step 7 atomic multi-registry write:
    1. Build all registry entries in memory (SourceRegistryEntry, WorkRegistryEntry updates, scholar records are already registered during Step 4).
    2. Process genre chain → create relationship edges and placeholder works if needed.
    3. Write `library/logs/pending_registration_{source_id}.json` with intended changes.
    4. Acquire file locks on sources.json, works.json (scholars.json already updated in Step 4).
    5. Apply changes: update sources.json (add entry), update works.json (add/update entry + relationships).
    6. Write `library/sources/{source_id}/metadata.json` (the full SourceMetadata as JSON).
    7. Delete pending registration file.
  - Each registry write creates .bak before overwriting.
  - If lock cannot be acquired within 30s → raise with retry signal.
- `check_orphaned_registrations(*, library_root) -> list[str]`
  - SPEC §4.A.2 Step 7: on startup, scan for `pending_registration_*.json`.
  - For each: check which registry files were already updated (by checking if source_id exists in registry).
  - If all updated → delete pending file (registration completed, pending cleanup failed).
  - If none updated → delete pending file (registration never started).
  - If partially updated → restore from .bak files, delete pending file (rollback).
  - A registry file with JSON parse failure → restore from .bak copy.

**Important:** Scholar records (author + muhaqiq) are already registered during Step 4 (metadata_inference.py calls scholar_authority.lookup/register). The registration orchestrator does NOT re-register scholars. It registers sources and works, and creates relationship edges.

**Test:** `engines/source/tests/test_registries.py`

---

## What NOT to Build

- **engine.py** (full pipeline orchestrator) — Session 6
- **logger.py** — Session 6
- **Error path testing** — Session 6
- **Plain text end-to-end** — Session 6

---

## Fixtures

All 13 existing fixtures can be used. For registration testing, construct SourceMetadata dicts from extraction output + GROUND_TRUTH.json + trust evaluation results (from Session 5a trust_evaluator). The registration orchestrator receives a fully populated SourceMetadata — it doesn't need to run extraction or inference.

For work relationship testing, use:
- Fixture 11 (همع الهوامع في شرح جمع الجوامع) — has genre_chain: sharh of جمع الجوامع

---

## Done When

- [ ] **text_utils:** `generate_slug()` produces correct Latin slugs from Arabic text (table lookup + fallback)
- [ ] **text_utils:** `generate_work_id()` produces `wrk_` format IDs, max 50 chars
- [ ] **text_utils:** Diacritics stripped, transliteration map applied, empty input → MD5 hash
- [ ] **source_registry:** `build_entry()` correctly maps all SourceMetadata → SourceRegistryEntry fields
- [ ] **source_registry:** Atomic write with .bak
- [ ] **scholar_registry:** `lookup_or_register_author()` routes auto_link / human_gate / new_record correctly
- [ ] **scholar_registry:** `lookup_or_register_muhaqiq()` creates scholar records for muhaqiqs
- [ ] **work_registry:** `build_entry()` generates work_id using transliteration table
- [ ] **work_registry:** `build_placeholder()` creates referenced_not_acquired records
- [ ] **work_registry:** `process_genre_chain()` creates edges and placeholder works
- [ ] **work_registry:** Placeholder works create sparse scholar records for referenced authors
- [ ] **human_gate wrapper:** All 5 gate functions create correct checkpoints
- [ ] **registration orchestrator:** `register_source()` writes pending → applies to registries → writes metadata.json → deletes pending
- [ ] **registration orchestrator:** metadata.json at `library/sources/{source_id}/metadata.json` is valid JSON matching SourceMetadata
- [ ] **registration orchestrator:** `check_orphaned_registrations()` handles all 3 cases (complete, none, partial)
- [ ] **registration orchestrator:** .bak files created before each registry write
- [ ] **All new tests pass** (target: ~30-40 new tests + 447 existing = ~480-490 total)

---

## API Keys

Not needed for Session 5b. All modules are deterministic.

---

## Build Tips

1. **Start with text_utils** (slug generation). The work registry depends on it for work_id generation.
2. **Then source_registry and scholar_registry** — simple modules, few dependencies.
3. **Then work_registry** — depends on scholar_registry for placeholder author records and text_utils for work_id.
4. **Then human_gate wrapper** — thin delegation, quick to build and test.
5. **Last: registration orchestrator** — composes everything. This is the most complex module; test it with a constructed SourceMetadata dict, not live pipeline output.
6. **Test each module before moving to the next.**
