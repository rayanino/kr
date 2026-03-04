# خزانة ريان — Project Status

**Last updated:** 2026-03-04
**Repo commit:** 5c3fe83 on master
**Tests:** 903 pass, 37 skip, 1 fail (API key)

---

## What Exists (current state of every component)

### Documents
| Document | State | Detail |
|----------|-------|--------|
| VISION.md | Partially audited | §0–§5, §13 correct. §6–§12 NOT yet corrected. 1585 lines. |
| 7 engine SPECs | All stubs | 3 lines each. None written. |
| 4 shared SPECs | 3 stubs + partial | human_gate has 32L partial. Others are 3-line stubs. |
| 7 schemas | Exist from ABD era | ABD-era designs for Shamela-only pipeline. Need redesign for KR's multi-format scope. |
| root CLAUDE.md | Exists | Mostly accurate. |
| 7 engine CLAUDE.md | Exist | Enriched with domain knowledge, D-023 metadata pass-through, scholarly integrity constraints. |
| kr_decisions.md | 23 decisions | D-001 to D-023. |
| SCHEMA_ANALYSIS.md | Exists | ABD-era pipeline overview + D-019/D-023 warnings. |
| DOMAIN.md | Complete (~470L) | Core identity, scholarly domain knowledge, evidence hierarchy, integrity risks, design implications. |
| USER_SCENARIOS.md | Complete (8 scenarios) | Day 1 through Year 3 + book briefing + science map + error correction. |
| ENTRY_EXAMPLE.md | Complete (~130L) | Calibration target for synthesis quality + metadata-to-synthesis mapping. |
| PIPELINE_TRACE.md | Complete (~165L) | Full 7-stage trace showing metadata accumulation. |
| RESOURCES.md | Partial (~230L) | Arabic NLP, OCR, and related tool catalog. |

### Code (legacy from ABD — functional but not designed for KR)

ABD (Arabic Book Digester) was a narrow Shamela-only tool. Its code works but its design decisions have zero authority in KR (D-019). Line counts below describe what EXISTS, not what KR needs.

| Engine | Source lines | Tests | Reference docs |
|--------|-------------|-------|----------------|
| source | 2,284L (intake.py, enrich.py, corpus_audit.py) | 112 | 2 files |
| normalization | 4,352L (normalize_shamela.py, discover_structure.py, validate_structure.py) | 292 | 15 files |
| passaging | 279L (scaffold only) | 0 | 0 |
| atomization | 0L (logic lives in excerpting/extract_passages.py) | 0 | 2 files |
| excerpting | 3,309L (extract_passages.py, assemble_excerpts.py) | 258 | 9 files |
| taxonomy | 2,377L (evolve_taxonomy.py) | 109 | 1 file |
| synthesis | 0L | 0 | 0 |
| shared/consensus | 1,749L | passing | — |
| shared/human_gate | 881L | 28 | — |
| shared/validation | 779L | passing | — |
| shared/feedback | 0L | 0 | — |
| shared/user_model | 0L | 0 | — |
| shared/scholar_authority | 0L | 0 | — |
| interface/scholar | 0L | 0 | — |

### Infrastructure
| Component | State |
|-----------|-------|
| `.claude/` | Exists but empty |
| CI/CD | None |
| Python packaging | `_paths.py` only |
| Integration tests | None |
| External resources catalog | `reference/RESOURCES.md` — maps tools to engines |
| API keys | `.env.template` exists. Owner provides keys on request. |

---

## What Must Be Done (Definition of Done)

The preparatory phase is complete when:
- VISION.md has zero defects (§6–§12 corrected, all sections pass Perfection Standard), plus any new sections added for concepts VISION.md currently lacks
- All 7 engine SPECs are complete and pass Tier 1+2
- All 5 shared component SPECs are complete (consensus, human_gate, validation, feedback, user_model)
- Scholar interface SPEC is complete (interface/scholar)
- All schemas verified (producing SPEC output = schema = consuming SPEC input)
- All CLAUDE.md files accurate
- All architectural decisions documented in kr_decisions.md
- Tool choices made (CI/CD, packaging, API keys, testing strategy)
- `.claude/` directory populated for Claude Code
- إملاء SCIENCE.md exists (minimal, for synthesis engine example)
- Cross-document consistency verified

---

## Key Unresolved Decisions

1. **Source identity model** — What is a "source"? `book_id` → `source_id`? Multi-volume works?
2. **Normalization/passaging boundary** — Does `discover_structure.py`'s `build_passages()` stay in normalization? (~2900L depend on this)
3. **Atomization/excerpting separation** — Logic combined in `extract_passages.py`. Where's the boundary?
4. **LLM provider strategy** — Which models for consensus, fallback, configuration
5. **Entry generation** — How entries are structured, staleness model, quality criteria

---

## Previous Sessions

1. **Phase 1** (Claude Code): Directory restructure, taxonomy registry fix, test path fixes → 903 tests pass.
2. **Phase 1.5** (Claude Code): Repo cleanup, Makefile, .gitignore.
3. **Coordination setup** (Claude Chat, 8 sub-sessions): Decision log (15 decisions), protocol with examples, repo-direct workflow, resource catalog, session handoff system, hostile coordination audit.

No SPECs written yet. No VISION corrections since the §0–§5/§13 audit.

---

## Session Handoff

The next session's task, context, and file list are in `NEXT.md` at the repo root. Session-end procedures are defined in the project instructions (the system prompt).
