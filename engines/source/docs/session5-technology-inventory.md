# Technology Inventory — Source Engine Session 5

**Capabilities:** Scholar authority, human gate, validation, trust evaluation, registries (source/work/scholar), config loading, work relationship tracking.

## Use (existing tool handles it)

| Capability | Library | Evidence / Notes |
|-----------|---------|-----------------|
| File locking for registry atomicity | `filelock` 3.25.1 (already installed) | Platform-independent, context manager support, timeout support. Used for `scholars.json`, `works.json`, `sources.json` file locks during Step 7 registration. `FileLock("path.lock", timeout=30)`. |
| Atomic JSON writes | `tempfile` + `os.fsync` + `os.replace` (stdlib) | Standard pattern: write to `NamedTemporaryFile(dir=same_dir)`, fsync, then `os.replace(tmp, target)`. `os.replace` is atomic on POSIX (same filesystem). No external dependency needed. |
| Pydantic schema validation | `pydantic` 2.x (already installed) | `ScholarAuthorityRecord.model_validate(data)` for Check 1. `model_dump()` for serialization. Already used throughout the codebase. |
| JSON storage | `json` (stdlib) | All registries use JSON files. `json.dumps(data, ensure_ascii=False, indent=2)` for Arabic text. Already used in freezer, staging. |
| UUID generation for checkpoint IDs | `uuid` (stdlib) | `uuid.uuid4().hex[:8]` for `hg_` prefix checkpoint IDs. Already used in tracer stub. |
| Arabic name matching | `shared/scholar_authority/src/name_matching.py` (already built, 88 lines, 22 tests passing) | Token-based approach handles A3-1 (short-vs-long names). `normalize_arabic_name()`, `normalized_name_similarity()`. Copied from eval_harness.py in Session 3. |
| ISO 8601 timestamps | `datetime` (stdlib) | `datetime.now(timezone.utc).isoformat()` for all timestamp fields. Already used in human_gate stub. |
| Path manipulation | `pathlib` (stdlib) | All file paths use `Path` objects. Already established convention. |
| Deep copy for revision history | `copy.deepcopy` (stdlib) | For preserving old values in `revision_history` before updates. |

## Build (nothing suitable exists)

| Capability | Why build? | Closest alternative | Gap |
|-----------|-----------|-------------------|-----|
| Scholar match scoring (§4.A.5) | Domain-specific composite algorithm: name (0.50) + death date (0.30) + school (0.10) + known works (0.10). No existing library implements weighted Islamic scholar disambiguation. | Generic fuzzy matching libraries (fuzzywuzzy, thefuzz) | No concept of death-date signal, school affiliation, or weighted multi-signal composite. Our `name_matching.py` already handles the name signal correctly. |
| Trust evaluation (§4.A.8) | Domain-specific 5-factor weighted algorithm with Islamic-scholarship-specific scoring rules (classical cutpoint 1000 AH, recognized muhaqiqs, publisher reputation). | No equivalent exists. | Unique to KR. |
| Human gate persistence and workflow | Pipeline-specific approval workflow with auto-approve mode, batching per source, `unsure` → elevated consensus. | Generic approval workflow libraries are overkill — this is JSON file CRUD with domain logic. | ~150 lines of custom code. |
| Registry CRUD with write-ahead log | Atomic multi-file updates (sources.json + works.json + scholars.json in one transaction). | SQLite WAL mode could do this, but SPEC mandates JSON-file architecture (no database for v1). | Write-ahead log pattern: write pending file → apply changes → delete pending. ~100 lines per registry. |
| Validation Layer 1 (6 checks) | Domain-specific cross-checks: genre↔format, author↔science, multi-layer coherence. | Pydantic handles Check 1 (schema). Everything else is domain logic. | ~200 lines of source-engine-specific validation. |
| Config loading | Simple JSON loading with validation. | `pydantic-settings` could work but is overkill for loading 4 JSON config files. | ~50 lines. |

## Needs testing

| Capability | Candidate | Concern | How to test |
|-----------|-----------|---------|-------------|
| `filelock` timeout behavior | `filelock` 3.25.1 | Need to verify timeout=30 raises `Timeout` correctly when lock held by another process. Also verify lock cleanup on process crash. | Unit test: acquire lock in subprocess, attempt acquire in main with timeout=2, verify `Timeout` raised. |
| `os.replace` atomicity on the test environment | stdlib | Should be atomic on Linux (same filesystem), but worth a quick smoke test. | Write 100 concurrent replacements, verify no corruption. |
| Pydantic `model_validate` with Arabic text | pydantic 2.x | Arabic diacritics in `canonical_name_ar` must survive round-trip through `model_dump()` → JSON → `model_validate()`. | Fixture test: create ScholarAuthorityRecord with full tashkeel, serialize, deserialize, compare byte-for-byte. |

## Dependencies to Add

```
# Add to requirements.txt:
filelock>=3.0  # Already installed (3.25.1), but not in requirements.txt
```

No new dependencies required. Everything needed is either stdlib or already installed.
