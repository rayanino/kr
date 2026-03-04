# خزانة ريان — Preparatory Phase Master Workplan

**Purpose:** Every work item needed to take the KR repo from current state to a fully documented, fully decided environment ready for Claude Code to build.

**How to use:** This is a reference document, NOT loaded in every session. STATUS.md embeds the current work item's full spec. This file is consulted when advancing to the next work item (to copy the next item's spec into STATUS.md).

**Authority model:** Claude Chat makes all technical decisions autonomously. Owner provides domain/usage input only. See `reference/DEEP_REASONING_PROTOCOL.md`.

---

## Context Budget Rules

Claude Chat works best with **≤80K tokens of input** (~320KB of text). Beyond this, attention degrades and reasoning quality drops. Every session must respect this budget.

**How to stay within budget:**
1. **Always extract VISION sections** instead of attaching full VISION.md (saves ~76%): `make vision SECTIONS="2 7"`
2. **Heavy rounds split into focused sessions**: Session A = read code + make decisions. Session B = draft SPEC using decisions.
3. **Reference docs prioritized**: MUST-ATTACH vs ATTACH-IF-ROOM vs SKIP (available in repo).
4. **Upstream SPECs grow** — by W-006, there are 5 upstream SPECs (~75KB). Only attach the immediate upstream SPEC + the one being written. Reference others by decision numbers in kr_decisions.md.

**Multi-message output:** If Claude's response is getting long, it should say "I'll continue in my next message" and continue. The owner should not interrupt — just let Claude finish.

**Revision protocol:** After any work item, the owner may request revision by setting STATUS.md to `W-XXX-R1` with feedback. See DEEP_REASONING_PROTOCOL.md.

---

## Work Item Index

| ID | Name | Depends on | Executor | Est. sessions |
|----|------|-----------|----------|---------------|
| W-001 | Source engine SPEC | — | Claude Chat | 2–3 |
| W-002 | Normalization engine SPEC | W-001 | Claude Chat | 3 (context-split) |
| W-003 | Passaging engine SPEC | W-002 | Claude Chat | 1 |
| W-004 | Atomization engine SPEC | W-003 | Claude Chat | 1–2 |
| W-005 | Excerpting engine SPEC | W-004 | Claude Chat | 3 (context-split) |
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

---

## W-001: Source Engine SPEC

**Executor:** Claude Chat (2–3 sessions, creation mode)
**Context budget:** ~60K tokens — well within budget

### Attachments
```
make vision SECTIONS="2 7"
```
1. `vision_excerpt.md` — §2 (glossary) and §7 (source pipeline)
2. `engines/source/src/intake.py` (1476L)
3. `engines/source/src/enrich.py` (580L)
4. `engines/source/src/corpus_audit.py` (228L)
5. `engines/source/reference/ABD_INTAKE_SPEC.md` (795L)
6. `engines/source/reference/edge_cases.md` (127L)
7. `schemas/source_metadata.json`
8. `schemas/SCHEMA_ANALYSIS.md`

For session 2+: also attach the SPEC draft from the previous session.

### Decisions Claude Makes (Research, Decide, Document)
- Source identity model: what is a "source"? Does `book_id` become `source_id`?
- Multi-volume representation: one source or many?
- Manual input representation within the source model
- Source registry format (`library/sources/registry.yaml`)
- Source engine output scope: what crosses the source→normalization boundary?
- ABD intake metadata evolution for KR
- `book_id` → `source_id` rename timing

### Domain Questions (Ask Owner Only If Needed)
- How do multi-volume works appear in the Shamela library?
- What does manual input look like in practice?

### VISION Sections to Correct
§7.1–§7.4 (pipeline overview, discovery, documentation, trustworthiness)

### Completion Criteria
- SPEC.md complete (all 10 template sections, substantive)
- All decisions logged in kr_decisions.md (D-016+)
- Perfection Standard Tier 1 + Tier 2 pass
- Phase 4 self-audit visible deliverable with ≥3 defects found and resolved
- VISION defect ledger produced
- STATUS.md updated with W-002 spec

---

## W-002: Normalization Engine SPEC

**Executor:** Claude Chat (3 sessions — context-split required)
**Context warning:** 175KB code + 141KB reference docs. MUST split into focused sessions.

### Session A: Code Study + Boundary Decision (~70K tokens)

**Attachments:**
```
make vision SECTIONS="2 7"
```
1. `vision_excerpt.md` — §2 + §7
2. `engines/normalization/src/discover_structure.py` — 2896L, THE critical file
3. `engines/normalization/src/normalizers/normalize_shamela.py` — 1123L
4. `engines/normalization/src/validate_structure.py` — 333L
5. `engines/normalization/reference/ABD_NORMALIZATION_SPEC.md` — MUST (25K)
6. `engines/normalization/reference/ABD_STRUCTURE_SPEC.md` — MUST (22K)
7. `schemas/normalized_package.json`
8. `schemas/source_metadata.json`
9. `engines/source/SPEC.md` — upstream

**Goal:** Read all code. Understand `build_passages()`. Make the boundary decision. Produce a **decisions document** (not the SPEC yet).

### Session B: SPEC Drafting (~55K tokens)

**Attachments:**
1. `vision_excerpt.md` — §2 + §7
2. Decisions document from Session A
3. `engines/normalization/reference/structure_edge_cases.md` (8K)
4. `engines/normalization/reference/STRUCTURE_SPEC.md` (15K)
5. `engines/normalization/reference/STAGE2_GUIDELINES.md` (8K)
6. `schemas/normalized_package.json`
7. `engines/source/SPEC.md`

**Goal:** Draft the complete SPEC using decisions from Session A.

### Session C: Self-Audit + VISION Corrections (~45K tokens)

**Attachments:**
1. `vision_excerpt.md` — §2 + §7
2. SPEC draft from Session B
3. `engines/source/SPEC.md`

**Goal:** Hostile self-audit. Revise. VISION §7.5–§7.6 defect ledger and corrections.

### Reference docs NOT loaded (available in repo)
- `SHAMELA_HTML_REFERENCE.md` (48K) — too large, format-specific
- `prompts/` (7K) — LLM prompts, low priority for SPEC writing
- `ABD_ZOOM_BRIEF.md`, `structure_ABD_ZOOM_BRIEF.md` — superseded by full specs

### Critical Decision: Normalization/Passaging Boundary
Does `discover_structure.py`'s `build_passages()` stay in normalization or move to passaging?

### Other Decisions
- Normalized package contents
- Normalizer-specific extension mechanism
- `library/sources/` internal structure evolution
- Source identity rename propagation

### VISION Sections to Correct
§7.5 (source normalization), §7.6 (normalization boundary)

---

## W-003: Passaging Engine SPEC

**Executor:** Claude Chat (1 session, creation mode)
**Context budget:** ~35K tokens — light round

### Attachments
```
make vision SECTIONS="2"
```
1. `vision_excerpt.md` — §2 only (passaging definition)
2. `engines/normalization/SPEC.md` — determines this engine's scope
3. `engines/passaging/src/scaffold_passage.py` (279L)
4. `schemas/passage.json`
5. `schemas/normalized_package.json`

### Decisions Claude Makes
- Given W-002's boundary decision: what does passaging actually do?
- Is the engine substantive or thin? (Honest answer — if thin, say so)
- Passage boundary determination algorithm

### VISION Sections to Correct
§2.2 passaging definition (if boundary decision changed its meaning)

---

## W-004: Atomization Engine SPEC

**Executor:** Claude Chat (1–2 sessions, creation mode)
**Context budget:** ~75K tokens — moderate

### Attachments
```
make vision SECTIONS="2"
```
1. `vision_excerpt.md` — §2 (atom definition in §2.4)
2. `engines/atomization/reference/ABD_ATOMIZATION_SPEC.md`
3. `engines/atomization/reference/ABD_ZOOM_BRIEF.md`
4. `engines/excerpting/src/extract_passages.py` — atomization logic lives here (2288L)
5. `schemas/atoms.json`
6. `schemas/passage.json`
7. `engines/passaging/SPEC.md` — upstream

Do NOT attach all upstream SPECs — reference prior decisions via kr_decisions.md.

### Critical Decision: Atomization/Excerpting Separation
Current code combines both. This SPEC defines the boundary.

### Other Decisions
- Atom type taxonomy: what types, what determines type
- Character offset implementation
- Consensus ownership: atomization or excerpting?

### VISION Sections to Correct
§2.4 (atom definition, content type)

---

## W-005: Excerpting Engine SPEC

**Executor:** Claude Chat (3 sessions — context-split required)
**Context warning:** 130KB code + 206KB reference docs. MUST split.

### Session A: Reference Study + Key Decisions (~75K tokens)

**Attachments:**
```
make vision SECTIONS="2 5"
```
1. `vision_excerpt.md` — §2 + §5 (the excerpt specification)
2. `engines/excerpting/reference/ABD_EXCERPT_DEFINITION.md` — MUST (101K, the core document)
3. `engines/excerpting/reference/ABD_BINDING_DECISIONS.md` — MUST (23K)
4. `engines/excerpting/reference/ABD_EXCERPTING_SPEC.md` — MUST (13K)
5. `schemas/excerpt.json`
6. `schemas/atoms.json`

**Goal:** Deep study of what an excerpt IS. Read the definition, the binding decisions, the spec. Produce a **decisions document** covering self-containment, metadata model, boundary rules.

### Session B: Code Study + SPEC Draft (~70K tokens)

**Attachments:**
1. Decisions document from Session A
2. `engines/excerpting/src/extract_passages.py` (2288L, 94K)
3. `engines/excerpting/src/assemble_excerpts.py` (1021L, 36K)
4. `engines/excerpting/reference/ABD_EXTRACTION_PROTOCOL.md` (18K)
5. `engines/excerpting/reference/edge_cases.md` (9K)
6. `engines/excerpting/reference/ABD_RUNBOOK.md` (10K)

**Goal:** Verify decisions against actual code. Draft the complete SPEC.

### Session C: Self-Audit + VISION §5 Corrections (~50K tokens)

**Attachments:**
1. `vision_excerpt.md` from `make vision SECTIONS="2 5"`
2. SPEC draft from Session B
3. `engines/atomization/SPEC.md` — upstream

**Goal:** Self-audit. Revise. VISION §5 defect ledger and corrections.

### Reference docs NOT loaded (available in repo)
- `ABD_CHECKLISTS.md` (23K) — operational checklists, low priority for SPEC
- `ABD_ATOMS_README.md` (1K) — minimal
- `ABD_ZOOM_BRIEF.md` (6K) — superseded

### Domain Questions (Ask Owner)
- What does "independently understandable" mean to you as the reader?

### VISION Sections to Correct
§5 in its entirety

---

## W-006: Taxonomy Engine SPEC

**Executor:** Claude Chat (2–3 sessions, creation mode)
**Context budget:** ~65K tokens per session

### Attachments
```
make vision SECTIONS="2 3 4 5 9"
```
1. `vision_excerpt.md` — §2, §3, §4, §5.5, §9.3
2. `engines/taxonomy/src/evolve_taxonomy.py` (2377L)
3. `engines/taxonomy/reference/ABD_TAXONOMY_SPEC.md`
4. `schemas/excerpt.json`
5. `schemas/placed_excerpt.json`
6. `engines/excerpting/SPEC.md` — upstream

### Decisions Claude Makes
- Placement algorithm design
- Tree versioning mechanism
- Excerpt lifecycle transitions (draft → reviewed → placed)
- Coverage tracking design

### Domain Questions (Ask Owner)
- What approval workflow for taxonomy evolution? Quick approve/reject? Detailed review?
- How much evolution detail do you want to see?

### VISION Sections to Correct
§4.4 (evolution governance), §5.5 (one-per-source diagnostic), §9.3 (human gate locations)

---

## W-007: Synthesizing Engine SPEC

**Executor:** Claude Chat (2 sessions, creation mode)
**Depends on:** W-006 AND W-010 (needs إملاء SCIENCE.md)
**Context budget:** ~40K tokens — light (no existing code)

### Attachments
```
make vision SECTIONS="2 6"
```
1. `vision_excerpt.md` — §2 + §6 (the entry)
2. `library/sciences/imlaa/SCIENCE.md` — concrete example from W-010
3. `schemas/placed_excerpt.json`
4. `schemas/entry.json`
5. `engines/taxonomy/SPEC.md` — upstream

### Decisions Claude Makes
- Entry structure and generation algorithm
- Staleness detection model
- Entry quality criteria
- SCIENCE.md interface definition

### Domain Questions (Ask Owner)
- When you open a leaf node, what do you want to see?
- What makes an entry useful vs. not useful for your study?
- For sciences with schools: how should positions be presented?

### VISION Sections to Correct
§6 in its entirety

---

## W-008: Shared Components SPECs

**Executor:** Claude Chat (2–3 sessions, creation mode)

### Components
| Component | Code | Key focus |
|-----------|------|-----------|
| shared/consensus | `consensus.py` (1749L) | API contract, model config, confidence, retry |
| shared/human_gate | `human_gate.py` (881L, 28 tests) | Checkpoint workflow, corrections, patterns |
| shared/validation | `cross_validate.py` (779L) | Validation layers, schema checks |
| shared/feedback | No code | Interface definition only |

### Session splits
Session 1: consensus + validation SPECs (load their code + tests)
Session 2: human_gate + feedback SPECs (load their code + tests)

Each session: attach the component's code + tests + any existing SPEC stub.

### Decisions Claude Makes
- LLM provider strategy (use **web search** for current best practices)
- Consensus threshold and agreement requirements
- Validation layer architecture
- Feedback loop architecture

### Domain Questions (Ask Owner)
- How do you want to interact with human gate approval requests?

### VISION Sections to Correct (after this round)
§8 (quality architecture), §9 (human gates)

---

## W-009: Cross-Cutting VISION Corrections

**Executor:** Claude Chat (1–2 sessions, review mode)

### Attachments
```
make vision SECTIONS="0 1 2 3 4 8 9 10 11 12 13"
```
Plus: all engine SPECs (by this point, attach only summaries or reference by decision numbers — full SPECs would overflow context).

**Practical approach:** Load VISION sections + kr_decisions.md (which now has 30+ decisions summarizing all SPEC work). Cross-reference against decisions, not against full SPECs.

### Sections to Examine
| Section | What to do |
|---------|-----------|
| §8 Quality Architecture | Verify against decisions from W-008 (shared SPECs) |
| §10 Implementation Strategy | Update codebase inventory, verify milestones |
| §11 Design Principles | Consistency check against decisions |
| §12 Codebase Relationship | Rewrite to past tense |
| §0–§4, §13 | Targeted re-check |

---

## W-010: Minimal إملاء SCIENCE.md

**Executor:** Claude Chat (1 session, creation mode)
**Context budget:** ~30K tokens — light

### Attachments
```
make vision SECTIONS="2 4 5 6"
```
1. `vision_excerpt.md` — §2, §4, §5, §6
2. `engines/excerpting/SPEC.md` — what SCIENCE.md must provide
3. `library/sciences/imlaa/tree.yaml`
4. `library/sciences/imlaa/SCIENCE.md` (current stub)

### Domain Questions (Ask Owner — this round is primarily domain)
- What are إملاء's scholarly conventions?
- Does إملاء have schools of thought?
- How is the subject organized?
- What science-specific metadata does إملاء need?

---

## W-011: Cross-SPEC Consistency Verification

**Executor:** Claude Chat (1 session, review mode)

### Practical approach
All 11 SPECs + 7 schemas would overflow context. Instead:
1. Build a **boundary checklist** from kr_decisions.md
2. For each boundary: load only the two adjacent SPECs + the shared schema
3. Verify agreement, move to next boundary

This means ~7 focused checks within one session, each loading ~20K tokens.

### Deliverable
`reference/spec_consistency_report.md`

---

## W-012: Schema Reconciliation

**Executor:** Claude Chat (1–2 sessions, review mode)

### Attachments
All 7 schemas + `schemas/SCHEMA_ANALYSIS.md` + kr_decisions.md (~60K total — fits)

### Decisions Claude Makes
- Final field names across all schemas
- Schema versioning strategy
- Runtime validation library choice (use **web search** for current options)

---

## W-013: Python Packaging Decision

**Executor:** Claude Chat (1 partial session)

### Attachments
`_paths.py`, `requirements.txt`, `Makefile`, any engine test file

### Decisions
Keep `_paths.py` or evolve to `pyproject.toml`? Use **web search** for current Python packaging best practices.

---

## W-014: CI/CD Design

**Executor:** Claude Chat (1 session)

### Decisions (use **web search** for current tools)
- CI platform, push/PR checks, pre-commit hooks, branch strategy

### Deliverable
Complete `.github/workflows/` configs + implementation instructions for Claude Code.

---

## W-015: Claude Code Agent Design

**Executor:** Claude Chat (1–2 sessions)

### Decisions (use **web search** for Claude Code agent YAML format)
- Subagent definitions, slash commands, hooks, MCP integrations, API key management

### Deliverable
Complete `.claude/` population specs.

---

## W-016: Testing Infrastructure Design

**Executor:** Claude Chat (1 session)

### Decisions
- Gold baseline strategy, integration tests, corpus data access, API key provision, skip resolution

### Deliverable
`reference/testing_strategy.md`

---

## W-017: Infrastructure Implementation

**Executor:** Claude Code (1–2 sessions)
**Depends on:** W-013, W-014, W-015, W-016

Execute all infrastructure decisions. Tests ≥ 903 after.

---

## W-018: Owner Review

**Executor:** Owner. Read everything. Sign off or produce feedback.

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
