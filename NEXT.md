# NEXT SESSION

## Session Type
SPEC_REFINEMENT

## Immediate Task

Execute refinement cycle 1 on the **source engine SPEC** (`engines/source/SPEC.md`).

Follow `SPEC_REFINEMENT.md` Steps 0-10. Start with Step 0 (Creative Exploration from `CREATIVE_MANDATE.md`). Use `CONTEXT_BUDGET.md` to plan reads.

Cross-reference the SPEC prose against `engines/source/contracts.py` (Pydantic models) — mismatches are defects.

## Definition of Done

1. At least 3 new §4.B capabilities invented, each with named technology and output example
2. Minimum 8 web searches during creative exploration
3. Defect ledger with exact quotes and fixes
4. All §4.A subsections have concrete I/O examples with real Arabic text
5. All 7 knowledge integrity threats addressed
6. All 7 silent failure patterns checked
7. contracts.py validated against SPEC §3
8. Boundary with normalization verified
9. Two self-review rounds; Three Challenges each found at least one issue
10. Refined SPEC committed

## Context

Run `python3 scripts/orient.py --brief` for current project status.

The preparatory phase has 8 work streams (see `PREPARATORY_ROADMAP.md`). This session does Stream 1 (source SPEC refinement).

Session 9 completed Stream 2 (source + normalization contracts.py) and Stream 3 (technology survey).

## Files to Read — IN THIS ORDER

1. `CONTEXT_BUDGET.md` (~1,200 tokens)
2. `CREATIVE_MANDATE.md` (~1,200 tokens)
3. `SPEC_REFINEMENT.md` (~1,800 tokens)
4. `SILENT_FAILURES.md` (~1,500 tokens)
5. `KNOWLEDGE_INTEGRITY.md` (~1,600 tokens)
6. `engines/source/contracts.py` (~3,500 tokens) — updated Session 9
7. `engines/source/SPEC.md` (~5,500 tokens)
8. `engines/normalization/contracts.py` (~2,500 tokens) — new in Session 9
9. `engines/normalization/SPEC.md` §2 only (~1,000 tokens)
10. `reference/ENTRY_EXAMPLE.md` (~1,600 tokens)
11. `reference/USER_SCENARIOS.md` (~2,700 tokens)

**Total: ~24,100 tokens. Budget remaining: ~130,000 tokens.**

## Files to NOT Read

VISION.md, DOMAIN.md, kr_decisions.md, STATUS.md, ORCHESTRATOR.md, other engine SPECs

## What Last Session Did

Session 9 (Claude Chat):
- Stream 3: Technology survey (Docling, CAMeL Tools, Swan-Large embeddings, OpenITI confirmed active)
- Stream 2: Fixed source contracts.py (WORD_DOC, WorkLevel, ScholarAuthorityRecord, WorkRegistryEntry, SourceRegistryEntry)
- Stream 2: Created normalization contracts.py (ContentUnit, NormalizedManifest, NormalizedPackage)
- Fixed field naming inconsistency (source_type → source_format in normalization SPEC)
- Added Word document support to both SPECs
- Updated RESOURCES.md with 2026 survey findings

## Decisions Made

- Source SPEC now includes Word document (.doc/.docx) format support
- Normalization SPEC field `source_type` renamed to `source_format` (matching contracts.py)
- Swan-Large recommended as primary Arabic embedding model
- GenreRelationType expanded with taqrirat, responds_to, cites (matching SPEC §4.A.9)

## Pending Owner Questions

- **API keys:** Fill in .env from .env.template when ready (for future LLM-dependent work)
