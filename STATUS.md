# خزانة ريان — Project Status

**Last updated:** 2026-03-04 by Claude Chat (coordination system redesign)
**Repo:** `github.com/rayanino/kr` at commit 79edbab
**Tests:** 903 pass, 37 skip, 1 fail (API key)

---

## Your Role

You are the architect and designer of this entire application. You own every technical decision — the data models, the engine designs, the schemas, the documentation, the tooling, the infrastructure. The owner is an Islamic studies student with no technical background. He provides domain input (how scholars study, what makes excerpts useful, what sciences exist) when you ask. Everything else is yours.

Your goal: bring this project to a state where Claude Code can build every engine from clear, complete, consistent specifications. That means VISION.md is perfect, every SPEC.md is real, every schema is correct, every CLAUDE.md is accurate, every architectural decision is made and documented, and every tool choice is finalized.

You have full authority to modify, add, discard, or restructure anything in this project. The workplan in `reference/PREPARATORY_WORKPLAN.md` is advisory — follow it, deviate from it, or replace it based on what you judge best.

---

## Definition of Done (Preparatory Phase)

The project is ready for Claude Code when ALL of these are true:

- [ ] **VISION.md** — Zero defects. Every sentence correct, unambiguous, consistent. §0–§5, §13 were previously audited; §6–§12 pending. All sections must pass the Perfection Standard.
- [ ] **Engine SPECs** (7) — Each complete, follows template, passes Perfection Standard Tier 1+2. An AI agent can implement each engine from its SPEC alone.
- [ ] **Shared component SPECs** (4) — Same standard. consensus, human_gate, validation, feedback.
- [ ] **Schemas** (7) — Every field justified. Producing SPEC output contract = schema = consuming SPEC input contract. All cross-references consistent (e.g., source_id naming).
- [ ] **CLAUDE.md files** (root + 7 engines + shared + 4 components) — Accurate current state. Correct file paths and line counts.
- [ ] **Decisions** — Every architectural decision documented in `reference/kr_decisions.md`.
- [ ] **Data models** — All data structures designed and documented (schemas + SPEC contracts).
- [ ] **Tool choices** — CI/CD, Python packaging, API key management, testing strategy — all decided and documented.
- [ ] **`.claude/` directory** — Agents, commands, hooks designed for Claude Code.
- [ ] **إملاء SCIENCE.md** — Minimal Level 3 doc so synthesis engine has a concrete example.
- [ ] **Cross-consistency** — All documents agree. No SPEC contradicts VISION. No schema contradicts its SPEC.

---

## Current State: What Exists

### Documents
| Document | Status | Notes |
|----------|--------|-------|
| VISION.md (1585L) | §0–§5, §13 audited in earlier sessions. §6–§12 NOT yet corrected. | Authoritative but partially stale |
| Engine SPECs (7) | ALL stubs (3 lines each) | None written yet |
| Shared SPECs (4) | 3 stubs + human_gate has 32L partial | None complete |
| Schemas (7) | All exist from ABD era. Plausible but unverified against VISION. | Need reconciliation with SPECs |
| CLAUDE.md (root) | Exists, mostly accurate | Needs update after SPECs written |
| Engine CLAUDE.md (7) | All exist, reasonable quality | Need update after SPECs written |
| kr_decisions.md | 15 decisions (D-001 to D-015) | Healthy |
| SCHEMA_ANALYSIS.md | Exists, good pipeline overview | From ABD era, needs verification |

### Code (all migrated from ABD — works but not yet matched to KR specs)
| Engine | Source lines | Test count | Reference docs |
|--------|-------------|------------|----------------|
| source | 2,284L (intake, enrich, audit) | 112 | 2 files |
| normalization | 4,352L (shamela, discover, validate) | 292 | 10 files (largest set) |
| passaging | 279L (scaffold only) | 0 | 0 |
| atomization | 0L (logic in excerpting/) | 0 | 2 files |
| excerpting | 3,309L (extract, assemble) | 258 | 9 files (critical knowledge) |
| taxonomy | 2,377L (evolve) | 109 | 1 file |
| synthesis | 0L (not started) | 0 | 0 |
| **shared/consensus** | 1,749L | passing | — |
| **shared/human_gate** | 881L | 28 | — |
| **shared/validation** | 779L | passing | — |
| **shared/feedback** | 0L | 0 | — |

### Infrastructure
| Component | Status |
|-----------|--------|
| `.claude/` directory | Exists but empty (no agents, no commands, empty settings.json) |
| CI/CD | None (no GitHub Actions, no pre-commit) |
| Python packaging | `_paths.py` only (no pyproject.toml) |
| Testing | pytest works. No integration tests. 1 test needs API key. |

### Key Unresolved Decisions
These are the major architectural decisions that must be made (during or before SPEC writing):

1. **Source identity model** — What is a "source"? Does `book_id` become `source_id`? How are multi-volume works modeled?
2. **Normalization/passaging boundary** — Does `discover_structure.py`'s `build_passages()` stay in normalization or move to passaging? (~2900 lines of code depend on this answer)
3. **Atomization/excerpting separation** — The logic is combined in `extract_passages.py`. Where does one end and the other begin?
4. **LLM provider strategy** — Which models, what fallback, how to configure consensus
5. **Entry structure** — How entries are generated, what makes a good one, staleness model

---

## Suggested Work Order

The workplan in `reference/PREPARATORY_WORKPLAN.md` suggests pipeline order: source → normalization → passaging → atomization → excerpting → taxonomy → synthesis → shared → cross-cutting. This makes sense because each engine's output is the next engine's input. But you decide the actual order.

**VISION extraction script:** `scripts/extract_vision_sections.py` lets you tell the owner which sections to extract. Usage: `python3 scripts/extract_vision_sections.py 7.1 7.4 2` extracts §7.1–§7.4 and §2. Or: `make vision SECTIONS="7.1 7.4 2"` produces `vision_excerpt.md`.

---

## What Happened in Previous Sessions

1. **Phase 1** (Claude Code): Structural cleanup — directory restructure, taxonomy registry fix, test path fixes. Exit: 903 tests pass.
2. **Phase 1.5** (Claude Code): Repo cleanup — removed ABD-era artifacts, added Makefile, fixed .gitignore.
3. **Coordination setup** (Claude Chat): Built coordination system, decision log (15 decisions), reasoning protocol, workplan. Commits b251810 + 79edbab.

No engine SPECs have been written yet. No VISION corrections since the earlier §0–§5/§13 audit.

---

## Session Mechanics

**At the end of every session, produce:**
1. Your deliverables (SPEC drafts, VISION corrections, schema changes, design decisions, etc.)
2. New decisions formatted for kr_decisions.md (D-016+)
3. An updated STATUS.md — update state tables, record what was done, specify what to attach next session
4. A SESSION_LOG.md entry (date, focus, decisions, deliverables, next focus)

**The owner will:** save your outputs to the repo, commit, update project knowledge files, start a new conversation.

**Context management:** Tell the owner exactly what files to attach. Use the extraction script for VISION.md sections. If you need something not listed, ask.

**Output length:** Write in chunks. If continuing, say "I'll continue in my next message."

---

## Files to Attach Next Session

Based on pipeline-order starting point (source engine SPEC first):
1. `engines/source/src/intake.py`
2. `engines/source/src/enrich.py`
3. `engines/source/src/corpus_audit.py`
4. `engines/source/reference/ABD_INTAKE_SPEC.md`
5. `engines/source/reference/edge_cases.md`
6. `schemas/source_metadata.json`
7. `schemas/SCHEMA_ANALYSIS.md`
8. VISION excerpt — run: `python3 scripts/extract_vision_sections.py 7.1 7.4 2 > /tmp/vision_excerpt.md`

If you (the next Claude) determine a different starting point is better, say so and tell the owner what to attach instead.
