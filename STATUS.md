# خزانة ريان — Project Status

**Last updated:** 2026-03-04
**Repo commit:** 04f01dc on master
**Tests:** 903 pass, 37 skip, 1 fail (API key)

---

## What Exists (current state of every component)

### Documents
| Document | State | Detail |
|----------|-------|--------|
| VISION.md | Partially audited | §0–§5, §13 correct. §6–§12 NOT yet corrected. 1585 lines. |
| 7 engine SPECs | All stubs | 3 lines each. None written. |
| 4 shared SPECs | 3 stubs + partial | human_gate has 32L partial. Others are 3-line stubs. |
| 7 schemas | Exist from ABD era | Plausible but unverified against VISION. Need reconciliation. |
| root CLAUDE.md | Exists | Mostly accurate. |
| 7 engine CLAUDE.md | Exist | Reasonable quality. Need update after SPECs. |
| kr_decisions.md | 15 decisions | D-001 to D-015. |
| SCHEMA_ANALYSIS.md | Exists | Good pipeline overview. ABD era, needs verification. |

### Code (migrated from ABD — works but not matched to KR specs)
| Engine | Source lines | Tests | Reference docs |
|--------|-------------|-------|----------------|
| source | 2,284L (intake.py, enrich.py, corpus_audit.py) | 112 | 2 files |
| normalization | 4,352L (normalize_shamela.py, discover_structure.py, validate_structure.py) | 292 | 10 files |
| passaging | 279L (scaffold only) | 0 | 0 |
| atomization | 0L (logic lives in excerpting/extract_passages.py) | 0 | 2 files |
| excerpting | 3,309L (extract_passages.py, assemble_excerpts.py) | 258 | 9 files |
| taxonomy | 2,377L (evolve_taxonomy.py) | 109 | 1 file |
| synthesis | 0L | 0 | 0 |
| shared/consensus | 1,749L | passing | — |
| shared/human_gate | 881L | 28 | — |
| shared/validation | 779L | passing | — |
| shared/feedback | 0L | 0 | — |

### Infrastructure
| Component | State |
|-----------|-------|
| `.claude/` | Exists but empty |
| CI/CD | None |
| Python packaging | `_paths.py` only |
| Integration tests | None |

---

## What Must Be Done (Definition of Done)

The preparatory phase is complete when:
- VISION.md has zero defects (§6–§12 corrected, all sections pass Perfection Standard)
- All 7 engine SPECs are complete and pass Tier 1+2
- All 4 shared component SPECs are complete
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
3. **Coordination setup** (Claude Chat, 3 sub-sessions): Decision log (15 decisions), protocol with examples, workplan, repo-direct workflow.

No SPECs written yet. No VISION corrections since the §0–§5/§13 audit.

---

## Suggested Starting Point

The advisory workplan (`reference/PREPARATORY_WORKPLAN.md`) suggests pipeline order starting with the source engine. You may override this.

**For the source engine SPEC, read these files from the repo:**
- `VISION.md` §7.1–§7.4 and §2 (use `python3 scripts/extract_vision_sections.py 7 2` or read directly)
- `engines/source/src/intake.py` (1476L)
- `engines/source/src/enrich.py` (580L)
- `engines/source/src/corpus_audit.py` (228L)
- `engines/source/reference/ABD_INTAKE_SPEC.md` (795L)
- `engines/source/reference/edge_cases.md` (127L)
- `schemas/source_metadata.json` (234L)
- `schemas/SCHEMA_ANALYSIS.md` (329L)

**Context budget note:** VISION.md is 1585 lines (~82K tokens). Do not read the whole file at once. Read only the sections relevant to the engine you're working on. Use the extraction script or read line ranges.

---

## Session End Checklist

At session end:
- [ ] All deliverables written to repo files
- [ ] New decisions appended to `reference/kr_decisions.md`
- [ ] `STATUS.md` updated (state tables, "Previous Sessions", suggested next starting point)
- [ ] Session log entry appended to `reference/SESSION_LOG.md`
- [ ] All changes committed and pushed to master
- [ ] Tell the owner: what was done, what decisions were made, any domain questions for next session
