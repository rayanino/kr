# Source Engine — Architecture

**Purpose:** Map the 9-step acquisition pipeline (SPEC §4.A.2) to code modules, showing what exists (Sessions 1–2) and what remains (Sessions 3–6).

---

## Pipeline Overview

```
library/staging/{source}
  │
  ▼
Step 1: Staging ──────────────────── engines/source/src/staging.py
  │
  ▼
Step 2: Format Detection ────────── engines/source/src/format_detector.py
  │
  ▼
Step 3: Encoding + Extraction ───── engines/source/src/extractors/shamela.py
  │                                  engines/source/src/extractors/plaintext.py
  ▼
Step 4: LLM Inference + Consensus ─ engines/source/src/metadata_inference.py
  │                                  engines/source/src/consensus.py  [→ shared/consensus]
  │                                  engines/source/prompts/inference_v1.py
  ▼
Step 5: Hashing + Dedup ─────────── engines/source/src/freezer.py (hash computation)
  │                                  engines/source/src/deduplication.py
  ▼
Step 6: Freezing ────────────────── engines/source/src/freezer.py (copy + verify + chmod)
  │
  ▼
Step 7: Registration ────────────── engines/source/src/registries/source_registry.py
  │                                  engines/source/src/registries/work_registry_store.py
  │                                  engines/source/src/registries/scholar_registry.py [→ shared/scholar_authority]
  ▼
Step 8: Trust Evaluation ────────── engines/source/src/trust_evaluator.py
  │
  ▼
Step 9: Handoff ─────────────────── engines/source/src/engine.py (status → acquired)
  │
  ▼
library/sources/{source_id}/metadata.json + frozen/
```

---

## Module Inventory

### Built (Sessions 1–2: 217 tests passing)

| Module | SPEC Section | What it does |
|--------|-------------|-------------|
| `src/staging.py` | §4.A.2 Step 1 | Discovers staged material, validates existence, creates staging lock. |
| `src/format_detector.py` | §4.A.2 Step 2 | Examines files, returns `SourceFormat` enum. Detects `shamela_html` and `plain_text`. |
| `src/extractors/shamela.py` | §4.A.3 | Full Shamela HTML metadata extraction: card parsing, FIELD_MAP, death date extraction, quality inspection, body text sampling, VolumeInfo construction. |
| `src/extractors/plaintext.py` | §4.A.3 | Plain text extraction: title from first line (with preamble skip), text sample, char/line counts. |
| `src/extractors/__init__.py` | — | Extractor registry: maps `SourceFormat` → extractor function. |

### To Build (Sessions 3–6)

| Module | Session | SPEC Section | What it does |
|--------|---------|-------------|-------------|
| `src/inference_models.py` | 3 | §4.A.4 | `InferenceOutput` Pydantic model (and sub-models) used as Instructor's `response_model`. Matches the LLM output JSON schema. Intermediate representation — mapped to SourceMetadata by metadata_inference.py. |
| `src/metadata_inference.py` | 3 | §4.A.4 | Constructs the inference prompt, calls LLMs via Instructor, maps LLM output to SourceMetadata fields, handles confidence scoring and attribution status caps. |
| `src/consensus.py` | 3 | §6 | Source-engine consensus integration: wraps `shared/consensus/evaluate()`, implements author identification agreement function, work matching agreement function, directed attribution_status comparison. |
| `src/freezer.py` | 4 | §4.A.2 Steps 5–6 | SHA-256 hashing (per-file + composite), staging hash comparison, file copy to `library/sources/{source_id}/frozen/`, post-copy verification, chmod 0444, corruption handling. |
| `src/deduplication.py` | 4 | §4.A.7 | Source-level exact dedup (composite hash vs registry). Work-level semantic dedup (title+author after inference). |
| `src/registries/source_registry.py` | 5 | §4.A.2 Step 7, §3.2 | Source registry CRUD. Atomic write with pending file + backup. `SourceRegistryEntry` validation. |
| `src/registries/work_registry_store.py` | 5 | §4.A.2 Step 7, §3.2 | Work registry CRUD. Work matching, preferred source tracking, relationship edge management. |
| `src/registries/scholar_registry.py` | 5 | §4.A.5 | Source-engine wrapper around `shared/scholar_authority/`. Handles progressive enrichment, consistency checks. |
| `src/trust_evaluator.py` | 5 | §4.A.8 | 5-factor weighted trust evaluation. Configurable muhaqiq and publisher lists. Trust re-evaluation on enrichment. |
| `src/validation.py` | 5 | §5 Layer 1 | Source-specific validation: 6 checks + D-023. Uses `shared/validation/` for generic checks. |
| `src/human_gate.py` | 5 | §5 Layer 2 | Source-engine wrapper around `shared/human_gate/`. Batches checkpoints per source. |
| `src/engine.py` | 6 | §4.A.2, §4.A.10 | Pipeline orchestrator: coordinates all 9 steps in sequence. Error handling, status tracking, staging lock management, handoff. |
| `src/config.py` | 6 | §8 | Configuration loading: consensus models, thresholds, file paths. Reads from `library/config/`. |
| `src/logger.py` | 6 | §7 | Structured logging to `library/logs/source_engine.jsonl`. SourceError serialization. Alert triggers. |

### Shared Components (built incrementally across Sessions 3–5)

| Component | Session | Interface |
|-----------|---------|-----------|
| `shared/consensus/src/consensus.py` | 3 | `evaluate()` — multi-model inference + comparison |
| `shared/scholar_authority/src/scholar_authority.py` | 5 | `lookup()`, `register()`, `update()` |
| `shared/scholar_authority/src/name_matching.py` | 3 | `normalize_arabic_name()`, `_extract_name_tokens()`, `normalized_name_similarity()` |
| `shared/human_gate/src/human_gate.py` | 5 | `create_checkpoint()`, `resolve()`, `get_pending()` |
| `shared/validation/src/validation.py` | 5 | `validate_output()`, `validate_enrichment_passthrough()` |

### Deferred (in `src/_deferred/`, not built in Stage 1)

| Module | Why deferred |
|--------|-------------|
| `src/_deferred/extractors/pdf.py` | PDF format not in Stage 1 scope |
| `src/_deferred/extractors/image.py` | Image/OCR format not in Stage 1 scope |
| `src/_deferred/extractors/word.py` | Word format not in Stage 1 scope |
| `src/_deferred/extractors/owner_authored.py` | Owner-authored content not in Stage 1 scope |
| `src/_deferred/citation_discovery.py` | §4.B.3 — cross-engine citation graph |
| `src/_deferred/gap_analysis.py` | §4.B.4 — acquisition gap detection |
| `src/_deferred/openiti_enrichment.py` | §4.B.1 — external metadata enrichment |
| `src/_deferred/enrichment.py` | §2.2 enrichment write-back (Stage 2 complexity) |
| `src/_deferred/tracer.py` | Step 0 artifact — superseded by real modules |

---

## Data Flow

```
Staged source files
    │
    ├──→ Format detection → SourceFormat enum
    │
    ├──→ Extractor → sparse metadata dict
    │       │
    │       └──→ text_sample (first 2000 chars of body)
    │
    ├──→ LLM Inference (Instructor + response_model)
    │       │
    │       ├──→ Single-model inference → InferenceOutput
    │       │
    │       └──→ Consensus (2 models) → author_identification + work_matching
    │               │
    │               └──→ Attribution status directed comparison
    │
    ├──→ SourceMetadata assembly (merge extractor + LLM outputs)
    │       │
    │       ├──→ Confidence scoring + caps (biographical cap 0.85, attribution cap 0.70)
    │       ├──→ text_fidelity (deterministic from format + quality issues)
    │       └──→ needs_review_fields (fields with confidence < 0.70)
    │
    ├──→ Validation (6 Layer 1 checks)
    │       │
    │       ├──→ [PASS] → proceed to hashing
    │       └──→ [FAIL] → abort or human gate
    │
    ├──→ Hashing (SHA-256 per-file + composite)
    │       │
    │       ├──→ source_id derivation (first 8 chars of composite hash)
    │       └──→ Deduplication check (composite hash vs source registry)
    │
    ├──→ Freezing (copy + verify + chmod 0444)
    │
    ├──→ Registration (atomic write to 3 registries)
    │       │
    │       ├──→ Source registry (SourceRegistryEntry)
    │       ├──→ Work registry (WorkRegistryEntry + relationships)
    │       └──→ Scholar registry (ScholarAuthorityRecord)
    │
    ├──→ Trust evaluation (5-factor weighted algorithm)
    │
    └──→ Handoff (status → acquired, metadata.json written)
```

---

## File System Layout

```
library/
├── staging/                    # Owner places files here
│   └── .processed/             # Completed intakes moved here
├── sources/
│   └── {source_id}/
│       ├── frozen/             # Immutable source files (chmod 0444)
│       └── metadata.json       # SourceMetadata record
├── registries/
│   ├── sources.json            # Source registry (SourceRegistryEntry)
│   ├── works.json              # Work registry (WorkRegistryEntry)
│   └── scholars.json           # Scholar authority (ScholarAuthorityRecord)
├── config/
│   ├── recognized_muhaqiqs.json
│   ├── known_publishers.json
│   ├── transliteration.json
│   └── genre_synonyms.json
├── gates/
│   ├── pending/                # Unresolved human gate checkpoints
│   ├── resolved/               # Resolved checkpoints (audit trail)
│   └── index.json
└── logs/
    ├── source_engine.jsonl     # Structured engine log
    ├── consensus.jsonl         # Consensus call log
    └── pending_registration_{source_id}.json  # Write-ahead log
```
