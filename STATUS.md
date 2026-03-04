# خزانة ريان — Project Status

**Last updated:** 2026-03-04 by Claude Chat (environment setup session)
**Current phase:** Phase 2 — Engine-by-Engine SPEC Writing
**Current work item:** W-001 (Source Engine SPEC)

## What Was Just Completed
- Phase 1 (Structural Cleanup) and Phase 1.5 (Repository Cleanup): COMPLETE
- KR repo at commit e8010ca on master. 903 tests pass, 37 skip, 1 fail (API key).
- Coordination infrastructure added: STATUS.md, kr_decisions.md, DEEP_REASONING_PROTOCOL.md, PREPARATORY_WORKPLAN.md, SESSION_LOG.md

## Current Work Item: W-001 — Source Engine SPEC

### Objective
Produce `engines/source/SPEC.md` — the first real Level 2 specification. Then produce a VISION.md §7.1–§7.4 defect ledger with corrections.

This is the first SPEC. It establishes the quality bar and patterns all subsequent SPECs follow.

### Files to Attach This Session
1. `engines/source/src/intake.py` (1476L)
2. `engines/source/src/enrich.py` (580L)
3. `engines/source/src/corpus_audit.py` (228L)
4. `engines/source/reference/ABD_INTAKE_SPEC.md` (795L)
5. `engines/source/reference/edge_cases.md` (127L)
6. `schemas/source_metadata.json` (234L)
7. `VISION.md` — focus on §7.1–§7.4 (source engine architecture) and §2 (glossary for term compliance)

### Decisions Claude Makes This Round (Research, Decide, Document)
- Source identity model: what is a "source"? Does `book_id` become `source_id`?
- Multi-volume representation: one source or many?
- Manual input representation: how does it fit the source model?
- Source registry format: what goes in `library/sources/registry.yaml`?
- Source engine output: just `source_metadata.json` + frozen file, or more?
- ABD intake metadata evolution: what changes for KR?
- `book_id` → `source_id` rename: do it now or defer?

### Domain Questions to Ask Owner (Only If Needed)
- How do multi-volume works appear in the Shamela library and in the owner's study practice?
- What does manual input look like in practice — notes during a lesson, typed passages, something else?

### Session Plan
- **Session 1:** Deep study of all source engine materials. Draft SPEC §1–§5. Make and document all decisions. Pause for owner review if domain questions arise.
- **Session 2:** Draft SPEC §6–§10. Hostile self-audit of complete SPEC (produce audit as visible deliverable). Revise.
- **Session 3 (if needed):** VISION §7.1–§7.4 defect ledger and corrected text.

### Completion Criteria
- [ ] SPEC.md follows template exactly (all 10 sections present and substantive)
- [ ] Every decision logged in kr_decisions.md format
- [ ] Passes Tier 1 + Tier 2 of Perfection Standard
- [ ] §9 (Current Implementation State) has accurate file paths and line counts
- [ ] Phase 4 hostile self-audit produced as visible deliverable with ≥3 defects found and resolved
- [ ] VISION §7.1–§7.4 defect ledger produced
- [ ] STATUS.md updated to point to W-002

### Schema Impact
`source_metadata.json` will likely be updated. Any field renames documented but only applied to this schema; downstream schemas note the pending rename.

## Blocked Items
None

## Session Notes for Next Claude
- This is the first SPEC being written. No upstream SPECs exist to reference.
- The Deep Reasoning Protocol is in creation mode for this work item (writing a new document, not reviewing existing). Skip Phase 1 (gap analysis). Go: Intake → Research → Draft → Self-Audit → Revise → Present.
- The authority model: Claude makes ALL technical/architectural decisions autonomously. Ask the owner ONLY for domain/usage questions. The owner has no technical background.
- SCHEMA_ANALYSIS.md in `schemas/` has useful context about the data flow between engines — read it if you need orientation on the pipeline.

## Active Document Versions
- VISION.md: §0–§5, §13 previously audited. §6–§12 pending correction.
- Source SPEC: stub (3 lines) — this session writes it
- All other SPECs: stubs
