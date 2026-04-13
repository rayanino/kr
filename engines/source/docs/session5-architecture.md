# Session 5 Architecture — Registration + Scholar Authority + Trust + Validation

## Module Dependency Graph

```
                    shared/validation/src/validation.py
                              │ (generic: schema, referential integrity, D-023)
                              ▼
engines/source/src/validation.py ◄── engines/source/contracts.py
    │ (source-specific: 6 Layer 1 checks)
    │
    ├── uses ──► shared/scholar_authority/src/scholar_authority.py
    │                 │ (lookup, register, update)
    │                 │ uses ──► shared/scholar_authority/src/name_matching.py (ALREADY BUILT)
    │                 │ reads/writes ──► library/registries/scholars.json
    │                 │
    ├── uses ──► engines/source/src/trust_evaluator.py
    │                 │ reads ──► library/config/recognized_muhaqiqs.json
    │                 │ reads ──► library/config/known_publishers.json
    │                 │
    ├── uses ──► shared/human_gate/src/human_gate.py
    │                 │ reads/writes ──► library/gates/pending/*.json
    │                 │ reads/writes ──► library/gates/resolved/*.json
    │                 │
    └── uses ──► engines/source/src/registries/
                      ├── source_registry.py ──► library/registries/sources.json
                      ├── work_registry_store.py ──► library/registries/works.json
                      └── scholar_registry.py ──► (wrapper for shared/scholar_authority)

engines/source/src/human_gate.py
    │ (source-engine wrapper: batches per source, maps triggers)
    └── uses ──► shared/human_gate/src/human_gate.py

engines/source/src/config.py
    │ (loads all config files)
    └── reads ──► library/config/*.json
```

## Data Flow for Registration (Step 7)

```
SourceMetadata (in memory, fully populated from Steps 1-6)
    │
    ▼
validation.py: Run 6 Layer 1 checks
    │ If fatal → abort
    │ If gate → create HumanGateCheckpoint, halt
    │ If warning → add to needs_review_fields, continue
    │
    ▼
trust_evaluator.py: Compute 5-factor weighted score
    │ → trust_tier, trust_score, trust_factors, trust_reason
    │ If flagged → optional human gate (TRUST_FLAGGED)
    │
    ▼
registries/__init__.py: Atomic multi-registry write
    │
    ├── 1. Write pending_registration_{source_id}.json (WAL)
    │
    ├── 2a. scholar_registry.py → scholars.json
    │       (lookup or register author + muhaqiq)
    │
    ├── 2b. work_registry_store.py → works.json
    │       (register work, create relationship edges)
    │
    ├── 2c. source_registry.py → sources.json
    │       (register source entry)
    │
    ├── 3. Write metadata.json to library/sources/{source_id}/
    │
    └── 4. Delete pending_registration file
```

## Atomic Write Pattern (all registries)

```python
from filelock import FileLock
import tempfile, os, json, shutil
from pathlib import Path

def atomic_json_write(path: Path, data: dict) -> None:
    """Write JSON atomically: temp file → fsync → os.replace."""
    # Backup current version
    if path.exists():
        shutil.copy2(path, path.with_suffix('.json.bak'))
    # Write to temp file in same directory (same filesystem = atomic rename)
    with tempfile.NamedTemporaryFile(
        mode='w', dir=path.parent, suffix='.tmp', delete=False
    ) as tmp:
        json.dump(data, tmp, ensure_ascii=False, indent=2)
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp_path = Path(tmp.name)
    # Atomic replace
    os.replace(tmp_path, path)

def locked_registry_read(path: Path, lock_path: Path, timeout: int = 30) -> dict:
    """Read a registry file under file lock."""
    with FileLock(lock_path, timeout=timeout):
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding='utf-8'))

def locked_registry_write(path: Path, lock_path: Path, data: dict, timeout: int = 30) -> None:
    """Write a registry file under file lock with atomic write."""
    with FileLock(lock_path, timeout=timeout):
        atomic_json_write(path, data)
```

## Module Specifications

### `shared/scholar_authority/src/scholar_authority.py`
- **Purpose:** Scholar identity registry with lookup, register, update.
- **Inputs:** Scholar name (Arabic), optional death date, optional school, optional known work title.
- **Outputs:** `ScholarMatchResult` dataclass with action (auto_link / human_gate / new_record).
- **SPEC:** §4.A.5 (full section).
- **Key logic:** `compute_scholar_match_score()` with weighted signals. `register()` assigns sequential IDs. `update()` runs 5 consistency checks.
- **Storage:** `library/registries/scholars.json` under `FileLock`.

### `shared/human_gate/src/human_gate.py`
- **Purpose:** Checkpoint creation, persistence, retrieval, resolution.
- **Inputs:** source_id, trigger, detail, context fields.
- **Outputs:** `HumanGateCheckpoint` (from contracts.py).
- **SPEC:** §5 Layer 2, reference/KNOWLEDGE_INTEGRITY.md Layer 4.
- **Key logic:** Auto-approve mode for build/test. Persistence in `library/gates/`. Batching by source_id.
- **Storage:** JSON files in `library/gates/pending/` and `library/gates/resolved/`.

### `shared/validation/src/validation.py`
- **Purpose:** Generic validation: Pydantic schema check, referential integrity, D-023 pass-through.
- **Inputs:** Data dict, Pydantic model class, optional registries dict.
- **Outputs:** `list[ValidationError]` (dataclass).
- **SPEC:** §5 Layer 1 (checks 1, 2, partial).

### `engines/source/src/validation.py`
- **Purpose:** Source-engine-specific 6 Layer 1 checks.
- **Inputs:** SourceMetadata dict, registries, prior sources for same work.
- **Outputs:** `list[ValidationError]`.
- **SPEC:** §5 Layer 1 (all 6 checks + D-023).
- **Key logic:** Confidence threshold (Check 3), consistency cross-checks (Check 5a-5e), multi-layer coherence (Check 6a-6c). Auto-correction for genre↔multi-layer (5e → 6).

### `engines/source/src/trust_evaluator.py`
- **Purpose:** 5-factor weighted trust score computation.
- **Inputs:** SourceMetadata (partially populated: author, muhaqiq, publisher, authority_level, text_fidelity), scholar registry, config (muhaqiqs, publishers).
- **Outputs:** trust_tier, trust_score, trust_factors list, trust_reason string.
- **SPEC:** §4.A.8 (full section). Validated in Step 2: 13/13 correct at threshold 0.65.

### `engines/source/src/registries/` (3 files)
- **Purpose:** CRUD for sources.json, works.json, scholars.json with atomic write-ahead log.
- **Key pattern:** All three use `locked_registry_write()`. Registration orchestrator writes pending file first, applies to all three, deletes pending.
- **SPEC:** §4.A.2 Step 7, §3.

### `engines/source/src/human_gate.py`
- **Purpose:** Source-engine wrapper. Maps source-specific triggers to shared human gate. Batches per source.
- **Key logic:** Thin wrapper — translates engine-specific context into `create_checkpoint()` calls.

### `engines/source/src/config.py`
- **Purpose:** Load all config files, provide typed access.
- **Reads:** `library/config/recognized_muhaqiqs.json`, `known_publishers.json`, `transliteration.json`, `genre_synonyms.json`.
- **SPEC:** §8.

## Session Split Recommendation

**Session 5a (blocking for Session 6):**
1. Config loading
2. Shared scholar authority (full: lookup, register, update + 5 checks)
3. Shared human gate (full with persistence)
4. Shared validation (generic checks)
5. Trust evaluator
6. Source-engine validation (6 Layer 1 checks)

**Session 5b (can overlap with Session 6 prep):**
7. Source registry CRUD
8. Work registry CRUD + relationship edges
9. Scholar registry wrapper
10. Registration orchestrator (__init__.py)
11. Config files creation (muhaqiqs, publishers, transliteration)

Session 5a produces the shared components that Session 6 (integration) needs. Session 5b produces the registry infrastructure. If time is tight, Session 6 can start on the orchestrator (`engine.py`) while 5b finishes registries.
