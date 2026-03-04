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
| W-009 | Cross-cutting VISION corrections | W-001–W-008 | Claude Chat | 2–3 |
| W-010 | Minimal إملاء SCIENCE.md | W-005 | Claude Chat | 1 |
| W-011 | Cross-SPEC consistency verification | W-009 | Claude Chat | 2 |
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

**MUST ATTACH:**
```
engines/source/src/intake.py                     (~20K tokens)
engines/source/src/enrich.py                     (~8K tokens)
engines/source/src/corpus_audit.py               (~3K tokens)
engines/source/reference/ABD_INTAKE_SPEC.md      (~16K tokens)
engines/source/reference/edge_cases.md           (~2K tokens)
schemas/source_metadata.json                     (~3.5K tokens)
```
VISION extracted sections — run and attach output:
```
python3 scripts/extract_vision_sections.py 7.1 7.4 2 > /tmp/vision_w001.md
```
(~17K tokens instead of ~82K for full file)

**HAVE AVAILABLE (only if Claude asks):**
```
schemas/SCHEMA_ANALYSIS.md
engines/source/tests/test_intake.py
```
For session 2+: also attach the SPEC draft from the previous session.

**Estimated context: ~77K tokens (budget: 200K)**

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

**Context budget warning:** The normalization engine has ~39K tokens of code in discover_structure.py alone. Sessions must be carefully structured to fit within 200K token limit.

**Session 1 — Code + boundary decision (focus: understand what the code does):**
```
engines/source/SPEC.md                                        (upstream, ~10K tokens)
engines/normalization/src/discover_structure.py                (~39K tokens — the key file)
engines/normalization/src/normalizers/normalize_shamela.py     (~15K tokens)
engines/normalization/src/validate_structure.py                (~4K tokens)
engines/normalization/reference/ABD_NORMALIZATION_SPEC.md      (~8.5K tokens — most important reference)
engines/normalization/reference/ABD_STRUCTURE_SPEC.md          (~7.3K tokens)
schemas/normalized_package.json                                (~5K tokens)
schemas/source_metadata.json                                   (~3.5K tokens)
```
VISION extracted:
```
python3 scripts/extract_vision_sections.py 7.5 7.6 2 > /tmp/vision_w002.md
```
(~20K tokens)

**Estimated session 1 context: ~112K tokens — fits with ~80K for conversation.**

**Session 2 — SPEC drafting (focus: write the spec, reference docs as needed):**
```
Session 1's SPEC draft so far
engines/source/SPEC.md
engines/normalization/reference/SHAMELA_HTML_REFERENCE.md      (~16K tokens — only if Shamela-specific details needed)
engines/normalization/reference/structure_edge_cases.md         (~2.6K tokens)
schemas/normalized_package.json
```
Plus VISION extracted (same as session 1).

**HAVE AVAILABLE (only if Claude asks):**
```
engines/normalization/reference/STRUCTURE_SPEC.md
engines/normalization/reference/STAGE2_GUIDELINES.md
engines/normalization/reference/prompts/pass3a_macro_v0.1.md
engines/normalization/reference/prompts/pass3b_deep_v0.1.md
```

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
engines/normalization/SPEC.md                    (immediate upstream — determines this engine's scope, ~10K tokens)
engines/passaging/src/scaffold_passage.py        (~3.5K tokens)
schemas/passage.json                             (~2.5K tokens)
schemas/normalized_package.json                  (~5K tokens)
```
VISION extracted:
```
python scripts/extract_vision_sections.py 2.2 > /tmp/vision_w003.md
```
(~3K tokens — only the passaging definition)

**HAVE AVAILABLE (only if Claude asks):**
```
engines/source/SPEC.md
```

**Estimated context: ~30K tokens — very light session**

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
engines/passaging/SPEC.md                        (immediate upstream, ~10K tokens)
engines/atomization/reference/ABD_ATOMIZATION_SPEC.md  (~4K tokens)
engines/atomization/reference/ABD_ZOOM_BRIEF.md        (~1.5K tokens)
engines/excerpting/src/extract_passages.py       (~31K tokens — atomization logic lives here)
schemas/atoms.json                               (~2.5K tokens)
schemas/passage.json                             (~2.5K tokens)
```
VISION extracted:
```
python scripts/extract_vision_sections.py 2.4 2.2 > /tmp/vision_w004.md
```
(~8K tokens — atom definition + engine definitions)

**HAVE AVAILABLE (only if Claude asks):**
```
engines/normalization/SPEC.md
engines/source/SPEC.md
```

**Estimated context: ~66K tokens — comfortable**

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

**Context budget warning:** ABD_EXCERPT_DEFINITION.md is 34K tokens alone. It CANNOT be loaded with all other files. The distilled knowledge is in BINDING_DECISIONS and EXCERPTING_SPEC.

**Session 1 — Code study + initial SPEC draft:**
```
engines/atomization/SPEC.md                                    (immediate upstream, ~10K tokens)
engines/excerpting/src/extract_passages.py                     (~31K tokens)
engines/excerpting/src/assemble_excerpts.py                    (~12K tokens)
engines/excerpting/reference/ABD_BINDING_DECISIONS.md          (~7.6K tokens — critical: distilled decisions)
engines/excerpting/reference/ABD_EXCERPTING_SPEC.md            (~4.3K tokens — critical: spec structure)
engines/excerpting/reference/edge_cases.md                     (~3K tokens)
schemas/excerpt.json                                           (~2.8K tokens)
schemas/atoms.json                                             (~2.5K tokens)
```
VISION extracted:
```
python3 scripts/extract_vision_sections.py 5 2 > /tmp/vision_w005.md
```
(~19K tokens)

**Estimated session 1 context: ~92K tokens — fits with ~100K for conversation.**

**Session 2 — Deep reference review + SPEC refinement:**
```
Session 1's SPEC draft
engines/excerpting/reference/ABD_EXTRACTION_PROTOCOL.md        (~6K tokens)
engines/excerpting/reference/ABD_RUNBOOK.md                    (~3.5K tokens)
engines/excerpting/reference/ABD_CHECKLISTS.md                 (~7.8K tokens)
```
Plus VISION extracted (same).

**Session 3 — If deeper context needed:**
```
engines/excerpting/reference/ABD_EXCERPT_DEFINITION.md         (~34K tokens — only load for this dedicated session)
Session 2's SPEC draft
```

**HAVE AVAILABLE (only if Claude asks):**
```
engines/excerpting/reference/ABD_ZOOM_BRIEF.md
engines/excerpting/reference/ABD_ATOMS_README.md
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
engines/excerpting/SPEC.md                       (immediate upstream, ~10K tokens)
engines/taxonomy/src/evolve_taxonomy.py           (~28K tokens)
engines/taxonomy/reference/ABD_TAXONOMY_SPEC.md   (~3K tokens)
schemas/excerpt.json                              (~2.8K tokens)
schemas/placed_excerpt.json                       (~2K tokens)
```
VISION extracted:
```
python scripts/extract_vision_sections.py 4 5.5 9.3 2 > /tmp/vision_w006.md
```
(~17K tokens — tree structure, one-per-source diagnostic, human gate locations, glossary)

**HAVE AVAILABLE (only if Claude asks):**
```
engines/atomization/SPEC.md
engines/passaging/SPEC.md
```

**Estimated context: ~69K tokens — comfortable**

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
engines/taxonomy/SPEC.md                          (immediate upstream, ~10K tokens)
library/sciences/imlaa/SCIENCE.md                 (from W-010, small)
schemas/placed_excerpt.json                       (~2K tokens)
schemas/entry.json                                (~2K tokens)
```
VISION extracted:
```
python scripts/extract_vision_sections.py 6 2 1.6 > /tmp/vision_w007.md
```
(~18K tokens — entry definition, glossary, entry as primary knowledge product)

**HAVE AVAILABLE (only if Claude asks):**
```
engines/excerpting/SPEC.md
```

**Estimated context: ~38K tokens — very comfortable. Deep conversation possible.**

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

### Session Structure (split by component — too large for one session)

**Session 1: Consensus component**
```
shared/consensus/src/consensus.py                (~22K tokens)
shared/consensus/tests/test_consensus.py          (~43K tokens)
```
VISION extracted:
```
python scripts/extract_vision_sections.py 8 2.2 > /tmp/vision_w008a.md
```
(~17K tokens)

**Estimated: ~88K tokens — fits.**

**Session 2: Human gate + validation components**
```
shared/human_gate/src/human_gate.py               (~10K tokens)
shared/human_gate/tests/test_human_gate.py         (~10K tokens)
shared/human_gate/SPEC.md                          (existing 32L stub)
shared/validation/src/cross_validate.py            (~9K tokens)
shared/validation/tests/test_cross_validate.py      (~10K tokens)
Session 1's consensus SPEC draft                   (~10K tokens)
```
VISION extracted:
```
python scripts/extract_vision_sections.py 8 9 > /tmp/vision_w008b.md
```
(~17K tokens)

**Estimated: ~76K tokens — comfortable.**

**Session 3: Feedback interface (no code) + self-audit all shared SPECs**
```
Session 1's consensus SPEC
Session 2's human_gate + validation SPECs
```
VISION extracted (same as session 2).

**HAVE AVAILABLE (only if Claude asks):**
```
Any engine SPEC that Claude needs to verify integration points
```

Do NOT attach all engine SPECs — Claude should request specific ones if needed.

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

**Executor:** Claude Chat (2–3 sessions, review mode)
**Depends on:** W-001 through W-008

### Context
Cannot load all 11 SPECs + full VISION simultaneously (~192K tokens = over limit). Sessions focus on specific VISION section groups with only the relevant SPECs.

### Session 1: §8 (Quality Architecture) + §9 (Human Gates)
```
shared/consensus/SPEC.md
shared/human_gate/SPEC.md
shared/validation/SPEC.md
shared/feedback/SPEC.md
engines/taxonomy/SPEC.md                         (primary human gate site)
engines/excerpting/SPEC.md                       (extraction review gate)
```
VISION extracted: `python scripts/extract_vision_sections.py 8 9 > /tmp/vision_w009a.md`
**Estimated: ~80K tokens.**

### Session 2: §10 + §11 + §12
```
engines/source/SPEC.md                           (for §10 codebase inventory)
engines/normalization/SPEC.md
Session 1's corrections
```
VISION extracted: `python scripts/extract_vision_sections.py 10 11 12 > /tmp/vision_w009b.md`
**Estimated: ~60K tokens.**

### Session 3 (if needed): Re-check §0–§4, §13
```
Session 1 + 2 corrections
Any SPECs Claude specifically requests
```
VISION extracted: `python scripts/extract_vision_sections.py 1 3 4 13 > /tmp/vision_w009c.md`
Targeted re-check, not full re-audit.

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
engines/excerpting/SPEC.md                        (~10K tokens)
engines/synthesis/CLAUDE.md                        (~1K tokens)
library/sciences/imlaa/tree.yaml                   (small)
library/sciences/imlaa/SCIENCE.md                  (current stub, small)
```
VISION extracted: `python scripts/extract_vision_sections.py 4 5.4 2 > /tmp/vision_w010.md`
(~22K tokens — science trees, metadata extensions, glossary)

**Estimated context: ~40K tokens — very light. Deep domain conversation possible.**

### Domain Questions (Ask Owner — this round is primarily domain)
- What are إملاء's scholarly conventions?
- Does إملاء have schools of thought?
- How is the subject organized (the tree structure)?
- What science-specific metadata does إملاء need?

---

## W-011: Cross-SPEC Consistency Verification

**Executor:** Claude Chat (2 sessions, review mode)

### Context
Loading all 11 SPECs + all schemas + VISION simultaneously (~210K tokens) exceeds the context window. Instead, verify boundary pairs in focused sessions. VISION is NOT needed — this is SPEC-to-SPEC and SPEC-to-schema verification.

### Session 1: Pipeline boundary pairs (source → … → taxonomy)
```
engines/source/SPEC.md
engines/normalization/SPEC.md
engines/passaging/SPEC.md
engines/atomization/SPEC.md
engines/excerpting/SPEC.md
engines/taxonomy/SPEC.md
All schemas (source_metadata.json through placed_excerpt.json)
```
For each consecutive pair: verify SPEC §3 (output) matches next SPEC §2 (input) matches shared schema.

**Estimated: ~80K tokens (6 SPECs × ~10K + 7 schemas × ~3K). Fits.**

### Session 2: Synthesizing + shared component integration
```
engines/taxonomy/SPEC.md                          (feeds synthesizing)
engines/synthesis/SPEC.md
shared/consensus/SPEC.md
shared/human_gate/SPEC.md
shared/validation/SPEC.md
shared/feedback/SPEC.md
schemas/placed_excerpt.json
schemas/entry.json
Session 1's boundary verification notes
```
Verify: synthesizing input contract, shared component integration points across all engine SPECs (Claude checks which engines reference each shared component).

**Estimated: ~80K tokens. Fits.**

### Task
For each boundary pair: does producing SPEC §3 match consuming SPEC §2 match shared schema? Spot-check 5 key concepts: self-containment, normalization boundary, content type, school, source-agnostic.

### Deliverable
`reference/spec_consistency_report.md`

---

## W-012: Schema Reconciliation

**Executor:** Claude Chat (1–2 sessions, review mode)

### Files to Attach

**Session 1: Schema-by-schema review against producing/consuming SPECs**
```
All 7 schema files from schemas/                  (~20K tokens total)
schemas/SCHEMA_ANALYSIS.md                        (~5K tokens)
reference/spec_consistency_report.md               (from W-011)
```
Load producing + consuming SPECs per schema as needed. Claude requests specific SPECs.

**Estimated: ~30K tokens base + SPECs on demand. Very comfortable.**

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
