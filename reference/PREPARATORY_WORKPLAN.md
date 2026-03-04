# خزانة ريان — Preparatory Phase Master Workplan

**Purpose:** Every work item needed to take the KR repo from current state to a fully documented, fully decided environment ready for Claude Code to build.

**How to use:** This is a reference document, NOT loaded in every session. STATUS.md embeds the current work item's full spec. This file is consulted when advancing to the next work item (to copy the next item's spec into STATUS.md).

**Authority model:** Claude Chat makes all technical decisions autonomously. Owner provides domain/usage input only. See `reference/DEEP_REASONING_PROTOCOL.md`.

---

## Work Item Index

| ID | Name | Depends on | Executor | Est. sessions |
|----|------|-----------|----------|---------------|
| W-001 | Source engine SPEC | — | Claude Chat | 2–3 |
| W-002 | Normalization engine SPEC | W-001 | Claude Chat | 3–4 |
| W-003 | Passaging engine SPEC | W-002 | Claude Chat | 1 |
| W-004 | Atomization engine SPEC | W-003 | Claude Chat | 1–2 |
| W-005 | Excerpting engine SPEC | W-004 | Claude Chat | 3–4 |
| W-006 | Taxonomy engine SPEC | W-005 | Claude Chat | 2–3 |
| W-007 | Synthesizing engine SPEC | W-006, W-010 | Claude Chat | 2 |
| W-008 | Shared components SPECs | W-006 | Claude Chat | 2–3 |
| W-009 | Cross-cutting VISION corrections | W-001–W-008 | Claude Chat | 1–2 |
| W-010 | Minimal إملاء SCIENCE.md | W-005 | Claude Chat | 1 |
| W-011 | Cross-SPEC consistency verification | W-009 | Claude Chat | 1 |
| W-012 | Schema reconciliation | W-011 | Claude Chat | 1–2 |
| W-013 | Python packaging decision | W-001 | Claude Chat | 1 partial |
| W-014 | CI/CD design | W-012 | Claude Chat | 1 |
| W-015 | Claude Code agent design | W-011 | Claude Chat | 1–2 |
| W-016 | Testing infrastructure design | W-012 | Claude Chat | 1 |
| W-017 | Infrastructure implementation | W-013–W-016 | Claude Code | 1–2 |
| W-018 | Owner review | W-017 | Owner | As needed |

**Revision protocol:** After any work item, the owner may request revision. See DEEP_REASONING_PROTOCOL.md "Revision Protocol" section. Revision rounds are labeled W-XXX-R1, W-XXX-R2, etc.

**Multi-session continuity:** When a work item spans multiple sessions, the previous session's output MUST be attached as input to the next session. STATUS.md lists this explicitly in "Files to Attach."

---

## W-001: Source Engine SPEC

**Executor:** Claude Chat (2–3 sessions, creation mode)

### Files to Attach
```
engines/source/src/intake.py
engines/source/src/enrich.py
engines/source/src/corpus_audit.py
engines/source/reference/ABD_INTAKE_SPEC.md
engines/source/reference/edge_cases.md
schemas/source_metadata.json
VISION.md
```
For session 2+: also attach the SPEC draft from the previous session.

### Decisions Claude Makes (Research, Decide, Document)
- Source identity model: what is a "source"? Does `book_id` become `source_id`?
- Multi-volume representation: one source or many?
- Manual input representation: how does it fit the source model?
- Source registry format: what goes in `library/sources/registry.yaml`?
- Source engine output scope: what crosses the source→normalization boundary?
- ABD intake metadata evolution: what changes for KR?
- `book_id` → `source_id` rename timing

### Domain Questions (Ask Owner Only If Needed)
- How do multi-volume works appear in the Shamela library?
- What does manual input look like in practice?

### VISION Sections to Correct
§7.1 (pipeline overview), §7.2 (discovery/acquisition), §7.3 (documentation/metadata), §7.4 (trustworthiness)

### Schema Impact
`schemas/source_metadata.json` likely updated. Downstream renames documented but deferred.

### Completion Criteria
- SPEC.md complete (all 10 template sections, substantive)
- All decisions logged in kr_decisions.md
- Perfection Standard Tier 1 + Tier 2 pass
- §9 has accurate file paths and line counts
- Phase 4 self-audit deliverable with ≥3 defects found and resolved
- VISION defect ledger produced
- STATUS.md updated with W-002 spec

---

## W-002: Normalization Engine SPEC

**Executor:** Claude Chat (3–4 sessions, creation mode — heaviest round)

### Files to Attach
```
engines/source/SPEC.md                          (upstream, now real)
engines/normalization/src/normalizers/normalize_shamela.py
engines/normalization/src/discover_structure.py
engines/normalization/src/validate_structure.py
engines/normalization/reference/                 (all 10 files)
schemas/normalized_package.json
schemas/source_metadata.json
VISION.md
```
For session 2+: also attach the SPEC draft from the previous session.

### Critical Decision: Normalization/Passaging Boundary
Does `discover_structure.py`'s `build_passages()` stay in normalization or move to passaging? Claude must read the code deeply, evaluate both options, and decide. This cascades into W-003.

### Other Decisions Claude Makes
- Normalized package contents: division tree? Passage boundaries? Just pages?
- Normalizer-specific extension mechanism
- `library/sources/` internal structure evolution
- Source identity rename propagation

### Domain Questions (Ask Owner Only If Needed)
- None anticipated — this is purely technical

### VISION Sections to Correct
§7.5 (source normalization), §7.6 (normalization boundary)

### Completion Criteria
- SPEC.md complete
- Boundary decision resolved, documented, and justified
- Input contract matches source engine's output contract (cross-verified)
- STATUS.md updated with W-003 spec

---

## W-003: Passaging Engine SPEC

**Executor:** Claude Chat (1 session, creation mode — may be thin)

### Files to Attach
```
engines/source/SPEC.md
engines/normalization/SPEC.md                   (determines this engine's scope)
engines/passaging/src/scaffold_passage.py
schemas/passage.json
schemas/normalized_package.json
VISION.md
```

### Decisions Claude Makes
- Given W-002's boundary decision: what does passaging actually do?
- Is the engine substantive or thin? (Honest answer required — if thin, say so)
- Passage boundary determination algorithm

### VISION Sections to Correct
§2.2 passaging definition (if boundary decision changed its meaning)

---

## W-004: Atomization Engine SPEC

**Executor:** Claude Chat (1–2 sessions, creation mode)

### Files to Attach
```
engines/source/SPEC.md
engines/normalization/SPEC.md
engines/passaging/SPEC.md
engines/atomization/reference/ABD_ATOMIZATION_SPEC.md
engines/atomization/reference/ABD_ZOOM_BRIEF.md
engines/excerpting/src/extract_passages.py      (atomization logic lives here)
schemas/atoms.json
schemas/passage.json
VISION.md
```

### Critical Decision: Atomization/Excerpting Separation
Current code combines both. This SPEC defines where atomization ends and excerpting begins.

### Other Decisions
- Atom type taxonomy: what types, what determines type
- Character offset implementation
- Consensus ownership: atomization or excerpting?

### VISION Sections to Correct
§2.4 (atom definition, content type) if SPEC reveals refinements

---

## W-005: Excerpting Engine SPEC

**Executor:** Claude Chat (3–4 sessions, creation mode — most complex round)

### Files to Attach
```
All upstream SPECs (source, normalization, passaging, atomization)
engines/excerpting/reference/                    (all 9 files — ABD specs, binding decisions, runbook, edge cases)
engines/excerpting/src/extract_passages.py
engines/excerpting/src/assemble_excerpts.py
schemas/excerpt.json
schemas/atoms.json
VISION.md
```

### Decisions Claude Makes
- Self-containment definition completeness
- Metadata model: §5.1 categories → schema 30+ fields mapping
- Excerpt boundary rules accuracy
- Taxonomy-independence enforcement
- Science-specific metadata extension mechanism

### Domain Questions (Ask Owner)
- What does "independently understandable" mean to you as the reader of an excerpt?

### VISION Sections to Correct
§5 in its entirety

---

## W-006: Taxonomy Engine SPEC

**Executor:** Claude Chat (2–3 sessions, creation mode)

### Files to Attach
```
All upstream SPECs
engines/taxonomy/src/evolve_taxonomy.py
engines/taxonomy/reference/ABD_TAXONOMY_SPEC.md
schemas/excerpt.json
schemas/placed_excerpt.json
VISION.md
```

### Decisions Claude Makes
- Placement algorithm design
- Tree versioning mechanism
- Excerpt lifecycle transitions (draft → reviewed → placed)
- Coverage tracking design

### Domain Questions (Ask Owner)
- What approval workflow do you want for taxonomy evolution? (Quick approve/reject? Detailed review?)
- How much evolution detail do you want to see when approving?

### VISION Sections to Correct
§4.4 (evolution governance), §5.5 (one-per-source diagnostic), §9.3 (human gate locations)

---

## W-007: Synthesizing Engine SPEC

**Executor:** Claude Chat (2 sessions, creation mode)
**Depends on:** W-006 AND W-010 (needs إملاء SCIENCE.md as concrete example)

### Files to Attach
```
All upstream SPECs
library/sciences/imlaa/SCIENCE.md               (from W-010)
schemas/placed_excerpt.json
schemas/entry.json
VISION.md
```

### Decisions Claude Makes
- Entry structure and generation algorithm
- Staleness detection model
- Entry quality criteria (technical definition)
- Level 3 (SCIENCE.md) interface definition

### Domain Questions (Ask Owner)
- When you open a leaf node, what do you want to see? Walk me through your ideal reading experience.
- What makes an entry useful vs. not useful for your study?
- For a science with schools (like Fiqh): how do you want school positions presented?

### VISION Sections to Correct
§6 in its entirety

---

## W-008: Shared Components SPECs

**Executor:** Claude Chat (2–3 sessions, creation mode)

### Components and Files
| Component | Code | Files to attach |
|-----------|------|----------------|
| shared/consensus | `shared/consensus/src/consensus.py` (1749L) | + its tests |
| shared/human_gate | `shared/human_gate/src/human_gate.py` (881L) | + its tests + existing 32L SPEC |
| shared/validation | `shared/validation/src/cross_validate.py` (779L) | + its tests |
| shared/feedback | No code | Interface definition only |

Also attach: All engine SPECs (they reference shared components)

### Decisions Claude Makes
- LLM provider strategy (models, configuration, fallback)
- Consensus threshold and agreement requirements
- Validation layer architecture (algorithmic vs LLM)
- Feedback loop architecture
- Correction data format and persistence

### Domain Questions (Ask Owner)
- How do you want to interact with approval requests from the human gate?

### VISION Sections to Correct (after this round)
§8 (quality architecture), §9 (human gates)

---

## W-009: Cross-Cutting VISION Corrections

**Executor:** Claude Chat (1–2 sessions, review mode)

### Files to Attach
All engine SPECs, all shared SPECs, VISION.md (full)

### Sections to Examine
| Section | What to do |
|---------|-----------|
| §8 Quality Architecture (~71L) | Verify against full SPEC set |
| §10 Implementation Strategy (~133L) | Update codebase inventory, verify milestones |
| §11 Design Principles (~59L) | Consistency check against all SPECs |
| §12 Codebase Relationship (~53L) | Rewrite to past tense (migration complete) |
| §0–§4, §13 | Targeted re-check with engine expertise |

---

## W-010: Minimal إملاء SCIENCE.md

**Executor:** Claude Chat (1 session, creation mode)
**Depends on:** W-005 (excerpting SPEC defines what SCIENCE.md must provide)

### Files to Attach
```
engines/excerpting/SPEC.md
engines/synthesis/CLAUDE.md
library/sciences/imlaa/tree.yaml
library/sciences/imlaa/SCIENCE.md               (current stub)
VISION.md
```

### Domain Questions (Ask Owner — this round is primarily domain)
- What are إملاء's scholarly conventions?
- Does إملاء have schools of thought?
- How is the subject organized (the tree structure)?
- What science-specific metadata does إملاء need?

---

## W-011: Cross-SPEC Consistency Verification

**Executor:** Claude Chat (1 session, review mode)

### Files to Attach
All 7 engine SPECs, all 4 shared component SPECs, all schemas, VISION.md

### Task
For each engine boundary: verify producing SPEC §3, consuming SPEC §2, and shared schema all agree. Verify shared component integration from both sides. Spot-check 5 key concepts across all SPECs.

### Deliverable
`reference/spec_consistency_report.md`

---

## W-012: Schema Reconciliation

**Executor:** Claude Chat (1–2 sessions, review mode)

### Files to Attach
All schemas, all SPECs, `schemas/SCHEMA_ANALYSIS.md`

### Decisions Claude Makes
- Final field names across all schemas
- Schema versioning strategy
- Runtime validation library choice

### Deliverable
Updated schemas + updated SCHEMA_ANALYSIS.md

---

## W-013: Python Packaging Decision

**Executor:** Claude Chat (1 partial session)

### Files to Attach
`_paths.py`, `requirements.txt`, `Makefile`, any engine's test file (for import pattern)

### Decisions Claude Makes
- Keep `_paths.py` or evolve to `pyproject.toml`?
- If pyproject.toml: exact content and migration steps

---

## W-014: CI/CD Design

**Executor:** Claude Chat (1 session)

### Decisions Claude Makes
- CI platform selection
- What runs on push vs PR
- Pre-commit hooks
- Branch strategy

### Deliverable
Complete `.github/workflows/` configs, `.pre-commit-config.yaml` if applicable, implementation instructions for Claude Code.

---

## W-015: Claude Code Agent Design

**Executor:** Claude Chat (1–2 sessions)

### Files to Attach
All SPECs, current `.claude/` directory contents, `CLAUDE.md`

### Decisions Claude Makes
- Subagent definitions (what each does, tool permissions)
- Slash commands (`/test`, `/validate-schema`, `/spec-check`, etc.)
- Hooks (automated checks after code changes)
- MCP integrations (GitHub, possibly others)
- API key management strategy

### Deliverable
Complete `.claude/agents/*.yaml`, `.claude/commands/*.md`, updated `.claude/settings.json`

---

## W-016: Testing Infrastructure Design

**Executor:** Claude Chat (1 session)

### Decisions Claude Makes
- Gold baseline creation and maintenance strategy
- Integration test strategy (end-to-end: source → entry)
- Corpus data accessibility (Git LFS? download script?)
- API key provision for consensus tests
- Resolution for 37 skipping tests

### Deliverable
`reference/testing_strategy.md` + implementation instructions

---

## W-017: Infrastructure Implementation

**Executor:** Claude Code (1–2 sessions)
**Depends on:** W-013, W-014, W-015, W-016

### Task
Execute all infrastructure decisions. Set up pyproject.toml (if decided), CI/CD, `.claude/` population, testing infrastructure.

### Completion Criteria
- All infrastructure committed
- Tests ≥ 903 (no regressions)
- CI runs successfully

---

## W-018: Owner Review

**Executor:** Owner

### Task
Read complete documentation stack. Either sign off or produce feedback (triggers revision rounds).

---

## Dependency Graph

```
W-001 (source) ──────────────────────────────┐
  │                                           │
  ▼                                           ▼
W-002 (normalization)                    W-013 (packaging)
  │
  ▼
W-003 (passaging)
  │
  ▼
W-004 (atomization)
  │
  ▼
W-005 (excerpting) ──────────────────────┐
  │                                       │
  ▼                                       ▼
W-006 (taxonomy) ────────────┐      W-010 (إملاء SCIENCE.md)
  │                           │           │
  ▼                           ▼           │
W-008 (shared)          W-007 (synthesis) ◄┘
  │                           │
  └────────┬──────────────────┘
           ▼
     W-009 (cross-cutting VISION)
           │
           ▼
     W-011 (cross-SPEC verify)
           │
           ▼
     W-012 (schema reconciliation)
           │
     ┌─────┼──────┬──────────┐
     ▼     ▼      ▼          ▼
  W-014  W-015  W-016     W-013
     │     │      │          │
     └─────┴──────┴──────────┘
                  │
                  ▼
           W-017 (implementation)
                  │
                  ▼
           W-018 (owner review)
```
