# Source Engine — Core vs Deferred Classification

**Date:** 2026-03-09
**Basis:** ENGINE_PROTOCOL Step 1, NEXT.md directives, CORE_CONTRACT_CLASSIFICATION.md
**Core formats:** `shamela_html`, `plain_text` only

---

## §1 — Purpose and Scope

| Capability | Classification | Reason |
|-----------|---------------|--------|
| Accept source material from manual path | CORE | Pipeline entry point — without this, nothing enters the library |
| Assign canonical identifiers (source, work, scholar) | CORE | Identity model is the foundation every downstream engine references |
| Extract, infer, validate metadata | CORE | Metadata fuels every downstream engine |
| Freeze raw source files with integrity hashes | CORE | Immutable baseline prevents T-1 (Silent Text Corruption) |
| Detect duplicates | CORE | Prevents T-7 (Duplication and Contradiction) |
| Classify trustworthiness | CORE | Default verified/flagged status for all excerpts |
| Track work-to-work relationships | CORE | Genre chain discovery is part of metadata inference; synthesis needs this for scholarly chains |
| Create and enrich scholar authority records | CORE | Author identification is the highest-cascade-risk decision |
| Classify structural format, authority level, multi-layer composition, science scope | CORE | These fields are consumed by normalization (multi-layer), passaging (structural format), and synthesis |
| Accept source material from autonomous discovery path | DEFERRED | Requires repository interface modules not yet built; owner manual intake is sufficient for Stage 1 |
| Scenario 2 (Day 30) autonomous discovery | DEFERRED | Depends on autonomous acquisition |
| Scenario 4 (Day 365) gap detection | DEFERRED | Depends on gap analysis (§4.B.4) |
| Scenario 6 (iPhone photos) | DEFERRED | Image format not in core |

## §2 — Input Contract

| Capability | Classification | Reason |
|-----------|---------------|--------|
| Manual acquisition: Shamela HTML | CORE | Primary structured format |
| Manual acquisition: Plain text | CORE | Simplest format; second core format |
| Manual acquisition: PDF | DEFERRED | Format not in core set |
| Manual acquisition: Image scans | DEFERRED | Format not in core set; requires OCR infrastructure |
| Manual acquisition: EPUB | DEFERRED | Format not in core set |
| Manual acquisition: Word document | DEFERRED | Format not in core set |
| Manual acquisition: Owner-authored content | DEFERRED | Separate input type with its own metadata model; pipeline works without it |
| Autonomous discovery (all triggers) | DEFERRED | Repository modules don't exist; core validates with manual intake |
| Enrichment write-back input | CORE | Downstream engines need to correct metadata; prevents cascading errors |
| 9 enrichment invariants | CORE | Each invariant prevents a specific corruption path |
| Critical field enrichment gate | CORE | Prevents silent metadata poisoning (T-6) |
| Input validation (empty, format check) | CORE | First line of defense |

## §3 — Output Contract

| Capability | Classification | Reason |
|-----------|---------------|--------|
| Frozen source files with SHA-256 | CORE | Immutability guarantee; T-1 mitigation |
| Source metadata record (metadata.json) | CORE | Primary output consumed by all downstream engines |
| All 7 metadata guarantees (§3) | CORE | Each guarantee prevents a specific downstream failure |
| Metadata pass-through (D-023) | CORE | Synthesis engine is the ultimate consumer; no field may be lost |
| Source registry updates | CORE | Duplicate detection and status tracking |
| Work registry updates | CORE | Work grouping and relationship tracking |
| Scholar authority registry updates | CORE | Author identity is the foundation |

## §4.A.1 — Source Identity Model

| Capability | Classification | Reason |
|-----------|---------------|--------|
| source_id assignment (hash-based) | CORE | Permanent unique identifier; referenced by every downstream product |
| human_label (readable shorthand) | CORE | Low cost, high usability; needed for logs and owner interaction |
| work_id assignment (slug-based) | CORE | Groups editions of same work; consumed by synthesis |
| Work matching (link source to existing work) | CORE | Prevents duplicate work records; synthesis needs correct grouping |
| Multi-volume work tracking | CORE | Real test fixtures are multi-volume (Ibn Aqil = 2 vols); must handle correctly |
| Scholar identity via scholar authority | CORE | Author identification is highest-cascade field |

## §4.A.2 — Acquisition Workflow

| Capability | Classification | Reason |
|-----------|---------------|--------|
| Step 1: Staging (accept files to staging area) | CORE | Entry point for all intake |
| Step 2: Format detection | CORE | Determines which extractor runs; gates unsupported formats |
| Step 3: Metadata extraction (format-specific) | CORE | Produces the raw metadata that inference enriches |
| Step 4: Metadata inference (LLM) | CORE | Fills gaps; produces the rich metadata the pipeline needs |
| Step 5: Duplicate detection | CORE | Prevents T-7 |
| Step 6: Freezing (copy, hash, verify, chmod) | CORE | T-1 mitigation; immutability guarantee |
| Step 7: Registration (atomic write to all registries) | CORE | Makes the source visible to the rest of the pipeline |
| Step 8: Trustworthiness evaluation | CORE | Determines default verified/flagged status |
| Step 9: Handoff | CORE | Sets status to `acquired`; normalization picks up |
| Write-ahead log for atomic registration | CORE | Prevents corrupted registries on crash |
| Registry file locking | CORE | Prevents duplicate records from concurrent intake |
| Staging lock (TOCTOU protection) | CORE | Prevents freeze corruption |
| Post-freeze hash verification | CORE | Catches copy corruption |

## §4.A.3 — Format-Specific Metadata Extraction

| Capability | Classification | Reason |
|-----------|---------------|--------|
| Shamela HTML extractor | CORE | Primary format |
| Plain text extractor | CORE | Second core format |
| PDF extractor | DEFERRED | Format not in core |
| Image extractor | DEFERRED | Format not in core |
| EPUB extractor | DEFERRED | Format not in core |
| Word document extractor | DEFERRED | Format not in core |
| Owner-authored content extractor | DEFERRED | Input type not in core |
| Fallback when info.html is missing (SRC_FORMAT_STRUCTURE_MISSING) | CORE | Real-world Shamela exports sometimes lack this file |

## §4.A.4 — LLM-Assisted Metadata Inference

| Capability | Classification | Reason |
|-----------|---------------|--------|
| Genre inference | CORE | Consumed by normalization (structural strategy), passaging, synthesis |
| Genre chain inference (sharh→matn relationship) | CORE | Creates work relationships; synthesis needs this for scholarly chains |
| Structural format inference | CORE | Normalization and passaging consume this |
| Multi-layer detection | CORE | Without this, downstream engines can't attribute text to correct author (T-2) |
| Science scope inference | CORE | Taxonomy engine needs this; synthesis uses it |
| Level inference | CORE | Low cost; useful for synthesis narrative |
| Author identification and resolution | CORE | Highest-cascade-risk decision |
| Author disambiguation | CORE | Critical for T-2 mitigation |
| Text fidelity assessment | CORE | Part of trust evaluation input |
| Tahqiq quality estimate (when muhaqiq known) | CORE | Part of trust evaluation input |
| Source authority level inference | CORE | Part of trust evaluation and metadata record |
| Confidence scoring on all inferred fields | CORE | Drives human gate triggers; prevents silent acceptance of wrong data |
| Multi-model consensus for author ID and work matching | CORE | Highest-cascade mitigation; defined in §6 |
| Inference prompt construction | CORE | The actual mechanism that drives inference quality |

## §4.A.5 — Scholar Authority Model

| Capability | Classification | Reason |
|-----------|---------------|--------|
| Scholar record structure (22 fields) | CORE | Registry consumed by all downstream engines |
| Record creation from source metadata + LLM inference | CORE | Without this, no author identity exists |
| Record matching (name + death date + school + works) | CORE | Prevents duplicate scholar records |
| Match thresholds (≥0.85 auto, 0.50-0.85 human gate, <0.50 new) | CORE | Defines the decision logic |
| Progressive enrichment (records get richer over time) | CORE | Mechanism is needed; the "50th source" trigger is implementation detail |
| Data provenance score | CORE | Synthesizer uses this to qualify claims; it's in the contract |
| Scholar record consistency checks (5 checks) | CORE | Prevents T-2 and T-6 corruption |
| Muhaqiq records as scholars | CORE | Trust evaluation needs muhaqiq identity |
| Disambiguation handling + notes | CORE | Critical for excerpting engine's scholar reference resolution |
| OpenITI enrichment of scholar records | DEFERRED | External data integration; core works without it |
| Usul-Data enrichment | DEFERRED | External data integration |
| Wikidata enrichment | DEFERRED | External data integration |
| Cross-validation across 3 sources | DEFERRED | Enhancement of provenance scoring; §4.B.8 |

## §4.A.6 — Relevance Evaluation

| Capability | Classification | Reason |
|-----------|---------------|--------|
| Relevance evaluation for autonomous discovery | DEFERRED | Only applies to autonomous discovery, which is deferred |
| Gap-fill relevance | DEFERRED | Depends on gap analysis (§4.B.4) |

## §4.A.7 — Deduplication

| Capability | Classification | Reason |
|-----------|---------------|--------|
| Source-level dedup (SHA-256 hash match) | CORE | Prevents exact duplicates |
| Work-level matching (same work, different edition) | CORE | Links editions to same work_id |
| Force re-acquisition flag | CORE | Low cost; needed for corruption recovery |
| Near-duplicate detection (text similarity) | DEFERRED | Already marked [NOT YET IMPLEMENTED] in SPEC |

## §4.A.8 — Trustworthiness Evaluation

| Capability | Classification | Reason |
|-----------|---------------|--------|
| 5-factor weighted evaluation | CORE | Mechanism that produces verified/flagged tier |
| Trust tiers: verified, flagged, owner_override | CORE | Consumed by excerpting engine for default verification status |
| Conservative bias (flag when uncertain) | CORE | Architectural principle; prevents T-6 |
| Special cases (owner-authored, Quran, canonical hadith) | CORE | These are real sources the owner will ingest |
| Trust re-evaluation on enrichment | CORE | Prevents stale trust after metadata correction |
| Specific factor weights (0.30, 0.25, 0.15, 0.15, 0.15) | CORE | But marked [ASSUMPTION — NEEDS STEP 2 TESTING] |
| Specific verified threshold (0.65) | CORE | But marked [ASSUMPTION — NEEDS STEP 2 TESTING] |

## §4.A.9 — Work Relationship Tracking

| Capability | Classification | Reason |
|-----------|---------------|--------|
| Relationship types (7 types: sharh_of through cites) | CORE | Genre chain discovery needs these; synthesis consumes them |
| Relationship discovery from title via LLM | CORE | This IS the genre chain inference from §4.A.4 |
| Placeholder work records for referenced works | CORE | Enables the relationship graph even when base work isn't acquired yet |
| Graph storage as edges in work registry | CORE | Needed for synthesis "three-level chain" narratives |
| Citation discovery from excerpting engine | DEFERRED | Depends on §4.B.3 |

## §4.A.10 — Processing Status Tracking

| Capability | Classification | Reason |
|-----------|---------------|--------|
| Status enum (staging through complete/error/withdrawn) | CORE | Pipeline coordination; normalization picks up `acquired` sources |
| Status transitions with timestamps | CORE | Audit trail; debugging |
| Dashboard view (counts per status, blocked sources) | DEFERRED | Nice-to-have; not needed for pipeline correctness |

## §4.B — Transformative Capabilities (ALL DEFERRED)

| Capability | Classification | Reason |
|-----------|---------------|--------|
| §4.B.1 — OpenITI Enrichment | DEFERRED | External data integration; core works without it |
| §4.B.2 — Bibliographic Intelligence from Minimal Input | DEFERRED | The core capability is already in §4.A.4; this section is the "what it enables" framing |
| §4.B.3 — Citation Network Discovery | DEFERRED | Cross-engine feature; depends on excerpting engine |
| §4.B.4 — Acquisition Gap Analysis | DEFERRED | Requires citation network and coverage analysis |
| §4.B.5 — KITAB Text Reuse Integration | DEFERRED | External data integration |
| §4.B.6 — Edition Comparison Intelligence | DEFERRED | Requires normalization output from 2+ editions |
| §4.B.7 — Scholarly Genealogy Auto-Construction | DEFERRED | Enhancement built on scholar authority core |
| §4.B.8 — Cross-Validated Scholar Authority Bootstrapping | DEFERRED | External data integration (Usul-Data, Wikidata) |
| §4.B.9 — Source Difficulty Prediction | DEFERRED | Optimization; pipeline works without it |
| §4.B.10 — Tahqiq Apparatus Fingerprinting | DEFERRED | Requires footnote parsing (normalization-level feature) |

## §5 — Validation and Quality

| Capability | Classification | Reason |
|-----------|---------------|--------|
| Layer 1: Self-validation (schema, referential integrity, confidence, dedup re-check, consistency) | CORE | Prevents every write of corrupt data |
| Layer 2: Human gate review (all 6 trigger conditions) | CORE | Owner-in-the-loop for uncertain decisions |
| Layer 3: Progressive correction via enrichment | CORE | Mechanism for downstream engines to fix upstream metadata |
| Scholarly integrity guarantee (4 requirements) | CORE | Non-negotiable quality bar |

## §6 — Consensus Integration

| Capability | Classification | Reason |
|-----------|---------------|--------|
| Multi-model consensus for author ID | CORE | Highest-cascade-risk mitigation |
| Multi-model consensus for work matching | CORE | Second-highest-cascade-risk mitigation |
| Single-LLM confidence cap at 0.85 | CORE | Prevents over-confidence in unverified biographical data |
| Cross-source biographical check (3+ sources) | CORE | Low-cost cross-check for multiply-mentioned scholars |
| Consensus failure handling (asymmetric by decision type) | CORE | Author ID failure → human gate; work match failure → provisional accept |

## §7 — Error Handling

| Capability | Classification | Reason |
|-----------|---------------|--------|
| Core error codes (SRC_UNSUPPORTED_FORMAT through SRC_REGISTRATION_INTERRUPTED) | CORE | Every error in the core processing path needs a defined code |
| Deferred error codes (SRC_KITAB_*, SRC_USUL_DATA_*, SRC_WIKIDATA_*, SRC_COMPARISON_*, SRC_OPENITI_*) | DEFERRED | These only fire from deferred capabilities |
| Logging to source_engine.jsonl | CORE | Audit trail |
| Alert triggers (fatal errors, >10% same warning, queue > 20) | CORE | Low cost; prevents silent failure buildup |

## §8 — Configuration

| Capability | Classification | Reason |
|-----------|---------------|--------|
| Core parameters (staging_path, confidence thresholds, trust threshold, consensus config) | CORE | Needed for the core to run |
| openiti_metadata_path | DEFERRED | Only used by §4.B.1 |
| Per-science configuration hooks | DEFERRED | Enhancement; core works with default behavior |

---

## Summary

- **Core capabilities:** 68
- **Deferred capabilities:** 32
- **Core input formats:** shamela_html, plain_text
- **Deferred input formats:** pdf_text, pdf_scanned, image_scan, epub, word_doc, owner_authored

## Extension Hooks

| Deferred Capability | Core Must Not Assume |
|---------------------|---------------------|
| Additional input formats (PDF, image, EPUB, Word, owner-authored) | Format detection and metadata extraction must use pluggable extractor modules — not hardcode Shamela/plain-text logic into the main flow |
| Autonomous discovery | Acquisition workflow must accept sources from any path, not assume manual-only; `acquisition_path` field already accommodates this |
| Owner-authored content | The identity model must not assume every source has an external author — `owner_authored` SourceFormat and OwnerAuthoredType enum already exist in contracts |
| OpenITI / Usul-Data / Wikidata enrichment | Scholar authority record creation must not assume LLM is the only data source — `record_sources` list and `data_provenance_score` already accommodate external sources |
| Citation network discovery | Work registry `relationships` list must accept edges from any `discovered_by` source, not just `source_engine` |
| Edition comparison | Work registry must track multiple `source_ids` per work — already does |
| Scholarly genealogy | Scholar record `teachers`/`students` fields must remain lists of canonical_ids — no structural changes needed |
| Near-duplicate detection | Deduplication must not assume only exact-hash matching — the modular check structure allows adding similarity-based checks |
| Source difficulty prediction | SourceMetadata must preserve the `difficulty_prediction` Optional field (already in contracts) |
| Tahqiq apparatus fingerprinting | SourceMetadata must preserve the `tahqiq_fingerprint` Optional field (already in contracts) |
| Relevance evaluation | The core must not embed relevance logic in the main acquisition flow — it only applies to autonomous discovery candidates |
| Processing status dashboard | Status tracking must log enough data (timestamps per transition) to build a dashboard later |

## Items I'm Uncertain About

**1. Owner-authored content — Core or Deferred?**
I classified it as DEFERRED because ENGINE_PROTOCOL explicitly limits core to shamela_html and plain_text. However, owner-authored content (study notes, tarjih conclusions) could be argued as core since the owner produces these and they're simple text input. **My recommendation: DEFERRED.** The owner's study notes can enter as plain_text for Stage 1. The specialized metadata (input_type, related_science, related_taxonomy_leaf) can wait.

**2. Relevance evaluation — should the mechanism exist even if autonomous discovery is deferred?**
I classified the entire §4.A.6 as DEFERRED because its only trigger is autonomous discovery. If someone wanted relevance evaluation for manually provided sources, that would be a different feature. **My recommendation: DEFERRED.** The owner makes manual relevance decisions implicitly by choosing what to upload.

**3. Special-case trust handling (Quran, hadith canonical collections) — is this really core?**
These are hardcoded trust overrides for specific source types. The owner IS likely to ingest Quran text and hadith collections early. But these could also be implemented as owner_override decisions. **My recommendation: CORE.** The cost is minimal (a few if-statements), the benefit is correctness for the most important sources in Islamic scholarship, and getting them wrong would be a visible embarrassment.
