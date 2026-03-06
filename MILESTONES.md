# KR Milestones — Implementation Task Decomposition

Each milestone is decomposed into atomic tasks. Each task is one session's work.
Tasks have dependencies (must be completed before starting) and acceptance criteria (how to know it's done).

Status markers: `[ ]` not started, `[~]` in progress, `[x]` complete, `[!]` blocked.

---

## Milestone 1: Source + Normalization End-to-End (Shamela Format)

**Goal:** One Shamela source in → normalized package out. Proves Phase 1 pipeline.

### M1.1 — Source Engine: Data Models and Identity
**Depends on:** Nothing.
**SPEC sections:** §2, §3, §4.A.1
**Tasks:**
- [ ] Define source metadata dataclass matching SPEC §3 output contract
- [ ] Define three-tier identity model: `source_id`, `work_id`, `canonical_id` (D-024)
- [ ] Implement ID generation: `{science}_{author_slug}_{title_slug}_{edition_hash}`
- [ ] Implement registry structures: `sources.json`, `works.json`, `scholars.json`
- [ ] Write tests: ID generation edge cases, registry CRUD, duplicate detection

**Acceptance:** `python -m pytest engines/source/tests/test_identity.py -v` passes.
All three registries can be created, read, updated. Duplicate source_id detected and rejected.

---

### M1.2 — Source Engine: Shamela Intake Path
**Depends on:** M1.1
**SPEC sections:** §2 (manual acquisition), §4.A.2 (Shamela metadata extraction)
**Tasks:**
- [ ] Implement Shamela directory detection and validation
- [ ] Implement `info.html` metadata extraction (title, author, category, description)
- [ ] Implement `content.html` structural analysis (volume/page organization, footnotes)
- [ ] Implement source freezing: copy to `library/sources/{source_id}/frozen/`, compute SHA-256
- [ ] Implement metadata record creation: write `metadata.json`
- [ ] Write tests: valid Shamela directory, malformed info.html, missing fields, freezing integrity

**Acceptance:** Given a sample Shamela directory, produces:
1. Frozen copy at correct path with correct hash
2. `metadata.json` with all extractable fields populated
3. Registry entries in `sources.json` and `works.json`

---

### M1.3 — Source Engine: Metadata Enrichment
**Depends on:** M1.2
**SPEC sections:** §4.A.3 (metadata enrichment), §4.A.5 (trustworthiness)
**Tasks:**
- [ ] Implement LLM-based metadata enrichment (science classification, school detection, date extraction)
- [ ] Implement enrichment via scholar authority lookup (if scholar exists)
- [ ] Implement 5-factor trustworthiness scoring
- [ ] Wire up consensus module for enrichment decisions
- [ ] Wire up human gate for low-confidence identifications
- [ ] Write tests: enrichment with mocked LLM, trustworthiness scoring, human gate trigger conditions

**Acceptance:** Source metadata enriched with science_scope, school_attribution, date estimates.
Trustworthiness score computed. Low-confidence cases create human gate checkpoints.

---

### M1.4 — Normalization Engine: Shamela Normalizer
**Depends on:** M1.2 (needs source engine output as input)
**SPEC sections:** §2, §3, §4.A.1 (format detection), §4.A.2 (Shamela-specific)
**Tasks:**
- [ ] Define normalized package dataclass matching SPEC §3
- [ ] Implement format detection (identify Shamela format from frozen files)
- [ ] Implement Shamela HTML parsing: extract text, headings, page breaks, footnotes
- [ ] Implement structure discovery: detect chapter/section hierarchy from HTML structure
- [ ] Implement multi-layer detection: identify matn vs sharh vs hashiyah (D-030)
- [ ] Implement footnote marker normalization (D-031)
- [ ] Write normalized package: `manifest.json` + `content.jsonl`
- [ ] Write tests: known Shamela structures, multi-layer texts, footnote edge cases

**Acceptance:** Given a frozen Shamela source + metadata.json, produces:
1. `manifest.json` with complete metadata (source metadata passed through + normalization additions)
2. `content.jsonl` with normalized text blocks, correct heading hierarchy, preserved page references
3. All source metadata from M1.2 present in output (D-023 verified)

---

### M1.5 — Integration: Source → Normalization End-to-End
**Depends on:** M1.3, M1.4
**SPEC sections:** Both engines' §2/§3 boundary
**Tasks:**
- [ ] Create integration test: Shamela directory → source engine → normalization engine → normalized package
- [ ] Verify metadata pass-through: every field from source metadata present in normalized package
- [ ] Verify schema conformance at the boundary
- [ ] Run full pipeline on 2-3 different Shamela sources (varying complexity)
- [ ] Create `tests/integration/test_source_normalization.py`

**Acceptance:** End-to-end test passes with real Shamela data.
`/trace-pipeline` command shows complete metadata flow.
No metadata lost between source and normalization output.

---

## Milestone 2: Phase 2 Pipeline — Passaging through Excerpting

**Goal:** Normalized package → passages → atoms → excerpts. Proves the content extraction chain.

### M2.1 — Passaging Engine: Core
**Depends on:** M1.4 (needs normalized package format)
**SPEC sections:** §2, §3, §4.A.1-§4.A.3
**Tasks:**
- [ ] Define passage dataclass matching SPEC §3
- [ ] Implement passage boundary detection (semantic + structural signals)
- [ ] Implement passage containment rule (D-011): every passage self-contained
- [ ] Implement overlap/context windows at boundaries
- [ ] Implement page reference preservation in passages
- [ ] Write tests: boundary detection on known texts, containment verification, edge cases

---

### M2.2 — Atomization Engine: Core
**Depends on:** M2.1 (needs passage format)
**SPEC sections:** §2, §3, §4.A.1-§4.A.3
**Tasks:**
- [ ] Define atom dataclass matching SPEC §3 (two-tier type system, D-034)
- [ ] Implement atom boundary detection within passages
- [ ] Implement structural type classification
- [ ] Implement scholarly function classification
- [ ] Implement atom relationship detection (D-034 atom_relations)
- [ ] Write tests: atom detection on known passages, type classification accuracy

---

### M2.3 — Excerpting Engine: Core
**Depends on:** M2.2 (needs atom format)
**SPEC sections:** §2, §3, §4.A.1-§4.A.3
**Tasks:**
- [ ] Define excerpt dataclass matching SPEC §3
- [ ] Implement three-phase pipeline (D-037): boundary → extraction → assembly
- [ ] Implement self-containment verification
- [ ] Wire up multi-model consensus (D-036)
- [ ] Implement excerpt metadata assembly (all upstream metadata + extraction metadata)
- [ ] Write tests: excerpt extraction on known texts, self-containment checks, consensus mock

---

### M2.4 — Integration: Passaging → Atomization → Excerpting
**Depends on:** M2.1, M2.2, M2.3
**Tasks:**
- [ ] End-to-end test: normalized package → passages → atoms → excerpts
- [ ] Verify metadata accumulation through the chain
- [ ] Verify no text corruption at any boundary
- [ ] Create `tests/integration/test_passaging_excerpting.py`

---

## Milestone 3: Taxonomy + Synthesis

**Goal:** Excerpts placed in taxonomy → entries synthesized. Proves the knowledge production chain.

### M3.1 — Taxonomy Engine: Core
### M3.2 — Synthesis Engine: Core
### M3.3 — Integration: Excerpting → Taxonomy → Synthesis

(Detailed decomposition deferred until Milestone 2 is closer to completion.)

---

## Milestone 4: Scholar Interface

**Goal:** Interactive access to the library. The user can query, browse, and learn.

### M4.1 — Retrieval Pipeline
### M4.2 — Query Interface
### M4.3 — Book Briefing
### M4.4 — Transformative Features

(Detailed decomposition deferred until Milestone 3 is closer to completion.)

---

## Milestone 5: Shared Components Hardening

**Goal:** All shared components production-ready.

### M5.1 — Consensus Module
### M5.2 — Human Gate
### M5.3 — Validation
### M5.4 — Feedback Loop
### M5.5 — User Model
### M5.6 — Scholar Authority

(Detailed decomposition deferred. These components are built incrementally alongside the engines that need them.)

---

## Cross-Milestone Tasks

These run in parallel with milestones:

- [ ] **Test data curation:** Assemble 5+ Shamela sources of varying complexity for testing
- [ ] **API key configuration:** Set up .env with LLM API keys
- [ ] **Python packaging:** Introduce pyproject.toml when import complexity demands it
- [ ] **CI/CD:** Set up GitHub Actions after Milestone 1 (test on push)
- [ ] **Gold baselines:** Create hand-verified reference outputs for each engine
