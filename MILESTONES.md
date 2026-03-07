# KR Milestones — Implementation Task Decomposition

Each milestone is decomposed into atomic tasks. Each task is one session's work.
Tasks have dependencies and acceptance criteria.

Status markers: `[ ]` not started, `[~]` in progress, `[x]` complete, `[!]` blocked.

---

## Milestone 1: Source + Normalization End-to-End

**Goal:** One source in (any format) → normalized package out. Proves Phase 1 pipeline.

The source engine accepts ALL scholarly source types (D-019). Milestone 1 proves the pipeline with the most readily available test data, then expands to other formats. The architecture is format-agnostic from day one.

### M1.1 — Source Engine: Data Models and Identity
**Depends on:** Nothing.
**SPEC sections:** §2, §3, §4.A.1
**Tasks:**
- [ ] Define source metadata dataclass matching SPEC §3 (use contracts.py as reference)
- [ ] Define three-tier identity model: `source_id`, `work_id`, `canonical_id` (D-024)
- [ ] Implement ID generation: `src_{8_char_hash}` from frozen file SHA-256
- [ ] Implement registry structures: `sources.json`, `works.json`, `scholars.json`
- [ ] Write tests: ID generation edge cases, registry CRUD, duplicate detection
- [ ] Tests use real Arabic text from test fixtures

**Acceptance:** All three registries can be created, read, updated. Duplicate source_id detected and rejected.

---

### M1.2 — Source Engine: First Format Intake
**Depends on:** M1.1
**SPEC sections:** §2 (manual acquisition), §4.A.2, §4.A.3
**Tasks:**
- [ ] Implement format detection (recognize source type from file structure/content)
- [ ] Implement metadata extraction for the first available format
- [ ] Implement source freezing: copy to `library/sources/{source_id}/frozen/`, compute SHA-256
- [ ] Implement metadata record creation: write `metadata.json`
- [ ] Write tests with real source data from test fixtures

**Note:** The specific format depends on what test data the owner provides. The architecture handles any format — the format-specific logic is isolated in format modules per the SPEC.

**Acceptance:** Given a source directory/file, produces:
1. Frozen copy at correct path with correct hash
2. `metadata.json` with all extractable fields populated
3. Registry entries in `sources.json` and `works.json`

---

### M1.3 — Source Engine: Metadata Enrichment
**Depends on:** M1.2
**SPEC sections:** §4.A.4 (enrichment), §4.A.8 (trustworthiness)
**Tasks:**
- [ ] Implement LLM-based metadata enrichment (science classification, school detection, date extraction)
- [ ] Implement enrichment via scholar authority lookup
- [ ] Implement 5-factor trustworthiness scoring
- [ ] Wire up consensus module for enrichment decisions
- [ ] Wire up human gate for low-confidence identifications
- [ ] Write tests: enrichment with mocked LLM, trustworthiness scoring, human gate triggers

**Acceptance:** Source metadata enriched with science_scope, school_attribution, date estimates.
Trustworthiness score computed. Low-confidence cases create human gate checkpoints.

---

### M1.4 — Normalization Engine: First Format Normalizer
**Depends on:** M1.2 (needs source engine output as input)
**SPEC sections:** §2, §3, §4.A.1 (format detection), §4.A.2 (format-specific)
**Tasks:**
- [ ] Define normalized package dataclass matching SPEC §3
- [ ] Implement format detection (identify format from frozen files)
- [ ] Implement text extraction, heading detection, page break detection for first format
- [ ] Implement structure discovery: detect chapter/section hierarchy
- [ ] Implement multi-layer detection: identify matn vs sharh vs hashiyah (D-030)
- [ ] Implement footnote marker normalization (D-031)
- [ ] Write normalized package: `manifest.json` + `content.jsonl`
- [ ] Write tests with real source data

**Acceptance:** Given a frozen source + metadata.json, produces:
1. `manifest.json` with complete metadata (source metadata passed through + normalization additions)
2. `content.jsonl` with normalized text blocks, correct heading hierarchy, preserved page references
3. All source metadata from M1.2 present in output (D-023 verified)

---

### M1.5 — Integration: Source → Normalization End-to-End
**Depends on:** M1.3, M1.4
**Tasks:**
- [ ] Create integration test: source file → source engine → normalization engine → normalized package
- [ ] Verify metadata pass-through: every field from source metadata present in normalized package
- [ ] Verify schema conformance at the boundary
- [ ] Run full pipeline on multiple sources (varying complexity)
- [ ] Create `tests/integration/test_source_normalization.py`

**Acceptance:** End-to-end test passes. Metadata flow verified. No metadata lost.

---

## Milestone 2: Phase 2 Pipeline — Passaging through Excerpting

**Goal:** Normalized package → passages → atoms → excerpts. Proves the content extraction chain.
Source-format-agnostic — all input is normalized packages from Milestone 1.

### M2.1 — Passaging Engine: Foundation
**Depends on:** M1.2 (normalized package output exists to test against)
**SPEC sections:** §2, §7, §8
**Tasks:**
- [ ] Implement errors.py — PassagingError, PassagingFatalError, PassagingWarning classes
- [ ] Implement config.py — Load PassagingConfig defaults, stub per-science overrides
- [ ] Implement loader.py — Read manifest.json + content.jsonl, 6 input validation checks
- [ ] Write tests: all 6 validation checks (valid input, each failure mode)
- [ ] Tests use real normalized output from test fixtures

**Acceptance:** loader.py reads a normalized package, validates it, returns (manifest, content_units). Each of the 6 validation failures tested.

---

### M2.1.1 — Passaging Engine: Cross-Page Assembly
**Depends on:** M2.1
**SPEC sections:** §4.A.2
**Tasks:**
- [ ] Implement assembly.py — basic text joining (space concatenation)
- [ ] Add boundary_continuity signal integration
- [ ] Add character-level heuristics (final-form Arabic letter, tanwin handling)
- [ ] Add Quran citation bracket handling (﴿...﴾)
- [ ] Add footnote renumbering (sequential per passage)
- [ ] Add text layer rebasing (offsets relative to assembled text)
- [ ] Write 12 assembly test cases (TEST_PLAN §10.1)

**Acceptance:** All 12 §10.1 test cases pass. Character count invariant holds across all test inputs. Arabic text fragility verified (read arabic-text SKILL.md).

---

### M2.1.2 — Passaging Engine: Prose Strategy
**Depends on:** M2.1.1
**SPEC sections:** §4.A.3, §4.A.4
**Tasks:**
- [ ] Implement strategies/prose.py — Step 1 (division size classification)
- [ ] Add Step 2 (boundary refinement with boundary_continuity)
- [ ] Add Step 3 (paragraph splitting, then LLM-assisted above threshold)
- [ ] Implement sentence integrity enforcement
- [ ] Implement isnad chain preservation
- [ ] Implement strategy.py — route structural_format to strategy
- [ ] Write 15 prose sizing test cases (TEST_PLAN §10.2)
- [ ] Write 6 sentence integrity test cases (TEST_PLAN §10.6)
- [ ] Write 4 isnad preservation test cases (TEST_PLAN §10.7)

**Acceptance:** Prose strategy produces correctly sized passages. No mid-sentence boundaries. No split isnad chains.

---

### M2.1.3 — Passaging Engine: Emission and Validation
**Depends on:** M2.1.2
**SPEC sections:** §4.A.10, §5
**Tasks:**
- [ ] Implement emitter.py — PassageRecord assembly, predecessor/successor linking, JSONL output
- [ ] Implement validator.py — all 11 self-validation checks (fatal checks first)
- [ ] Write 9 self-validation test cases (TEST_PLAN §10.5)
- [ ] End-to-end test: loader → assembly → prose → emit → validate on ibn_aqil fixture

**Acceptance:** Self-validation catches all 9 injected defects. End-to-end produces valid passages.jsonl.

---

### M2.1.4 — Passaging Engine: Orchestrator
**Depends on:** M2.1.3
**SPEC sections:** §4.A.1
**Tasks:**
- [ ] Implement engine.py — wire six phases into pipeline
- [ ] Handle fatal errors (abort + log + source stays at normalized)
- [ ] Handle warnings (collect + continue + flag passages)
- [ ] Update source processing status on success
- [ ] Integration test: process_source() end-to-end on waraqat_usul fixture

**Acceptance:** `process_source(source_id)` succeeds. Output validates against PassageRecord schema.

---

### M2.1.5 — Passaging Engine: Additional Strategies
**Depends on:** M2.1.4
**SPEC sections:** §4.A.5–§4.A.9
**Tasks:**
- [ ] Implement strategies/verse.py — test with alfiyyah_versified (8 test cases)
- [ ] Implement strategies/masala.py — test with mughni_comparative
- [ ] Implement strategies/qa.py — stub tests (Q&A fixture needed)
- [ ] Implement strategies/commentary.py — test with ibn_aqil_alfiyyah
- [ ] Implement strategies/dictionary.py — stub tests (dictionary fixture needed)
- [ ] Update strategy.py to route all 6 formats + mixed
- [ ] Write 7 format selection test cases (TEST_PLAN §10.4)

**Acceptance:** Each strategy produces valid passages on its test fixture. Format selection routes correctly.

---

### M2.1.6 — Passaging Engine: Transformative Capabilities
**Depends on:** M2.1.5
**SPEC sections:** §4.B.5, §4.B.6, §4.B.7, §4.B.8
**Tasks:**
- [ ] Implement adaptive_passaging.py (§4.B.5) — 4 test cases
- [ ] Implement arguments.py (§4.B.6) — keyword state machine first, then discourse_flow — 7 test cases
- [ ] Implement discourse_optimization.py (§4.B.7) — 5 test cases
- [ ] Implement completeness_forecast.py (§4.B.8) — 6 test cases
- [ ] Wire capabilities into engine.py pipeline

**Acceptance:** §10.8–§10.11 test cases pass. Capabilities gated by config flags.

---

## Milestone 3: Taxonomy + Synthesis

**Goal:** Excerpts placed in taxonomy → entries synthesized. Proves the knowledge production chain.

### M3.1 — Taxonomy Engine: Core
### M3.2 — Synthesis Engine: Core
### M3.3 — Integration: Excerpting → Taxonomy → Synthesis

---

## Milestone 4: Scholar Interface + GUI

**Goal:** Interactive access to the library via web GUI (see interface/GUI.md, D-043).

### M4.1 — FastAPI skeleton + base templates (RTL, Amiri font)
### M4.2 — Source browser + entry reader
### M4.3 — Human gate interface
### M4.4 — Search interface
### M4.5 — Transformative features (debate simulation, gap detection, etc.)

---

## Milestone 5: Shared Components Hardening

Built incrementally alongside engines that need them.

---

## Milestone 6: Additional Source Formats

After Milestone 1 proves the pipeline with one format, add others:
- [ ] PDF (text-embedded) intake + normalization
- [ ] PDF (scanned) intake via OCR (Mistral OCR, D-028) + normalization
- [ ] Photo (iPhone) intake via OCR + normalization
- [ ] EPUB intake + normalization
- [ ] Owner-authored content (study notes, tarjih, etc.)
- [ ] Plain text intake + normalization

Each format requires: a source engine format module + a normalization engine normalizer module.
The rest of the pipeline (passaging through synthesis) is format-agnostic and requires no changes.

---

## Cross-Milestone Tasks

- [ ] **Test data curation:** Assemble source data of varying formats and complexity
- [ ] **API key configuration:** .env with LLM API keys
- [ ] **Python packaging:** pyproject.toml when import complexity demands it
- [ ] **CI/CD:** GitHub Actions after Milestone 1
- [ ] **Gold baselines:** Hand-verified reference outputs for each engine
