# خزانة ريان — Project Status

**Last updated:** 2026-03-04
**Repo commit:** 79edbab on master
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
| root CLAUDE.md | Exists | Mostly accurate. Needs update after SPECs. |
| 7 engine CLAUDE.md | Exist | Reasonable quality. Need update after SPECs. |
| kr_decisions.md | 15 decisions | D-001 to D-015. Healthy. |
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
2. **Normalization/passaging boundary** — Does `discover_structure.py`'s `build_passages()` stay in normalization? (~2900L of code depend on this)
3. **Atomization/excerpting separation** — Logic is combined in `extract_passages.py`. Where's the boundary?
4. **LLM provider strategy** — Which models for consensus, fallback behavior, configuration
5. **Entry generation** — How entries are structured, staleness model, what makes a good entry

---

## Previous Sessions

1. **Phase 1** (Claude Code): Directory restructure, taxonomy registry fix, test path fixes → 903 tests pass.
2. **Phase 1.5** (Claude Code): Repo cleanup, Makefile, .gitignore.
3. **Coordination setup** (Claude Chat): Decision log (15 decisions), protocol, workplan. Commits b251810, 79edbab.

No SPECs written yet. No VISION corrections since the §0–§5/§13 audit.

---

## Suggested Starting Point and Files to Attach

The advisory workplan (`reference/PREPARATORY_WORKPLAN.md`) suggests pipeline order starting with the source engine. You may override this if you judge something else is more impactful.

**For the source engine SPEC (suggested first session):**

Prepare VISION excerpt first (saves 76% context):
```
python3 scripts/extract_vision_sections.py 7.1 7.4 2 > /tmp/vision_excerpt.md
```

Attach these files:
1. `/tmp/vision_excerpt.md` (~17K tokens — §7.1-§7.4 + §2 glossary)
2. `engines/source/src/intake.py` (~20K tokens)
3. `engines/source/src/enrich.py` (~8K tokens)
4. `engines/source/src/corpus_audit.py` (~3K tokens)
5. `engines/source/reference/ABD_INTAKE_SPEC.md` (~16K tokens)
6. `engines/source/reference/edge_cases.md` (~2K tokens)
7. `schemas/source_metadata.json` (~3.5K tokens)
8. `schemas/SCHEMA_ANALYSIS.md` (~4K tokens)

Estimated total with project files: ~84K tokens. Leaves ~116K for conversation.

---

## Session End Checklist

At session end, produce:
- [ ] Deliverables (SPEC sections, VISION corrections, schema changes)
- [ ] New decisions formatted for kr_decisions.md
- [ ] Updated STATUS.md (update state tables, add to "Previous Sessions", set next file list)
- [ ] One-line SESSION_LOG.md entry
