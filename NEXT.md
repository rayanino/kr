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

The preparatory phase has 8 work streams (see `PREPARATORY_ROADMAP.md`). This session does Stream 1 (source SPEC refinement). The owner is looking for scholarly source data to provide (any format).

## Files to Read — IN THIS ORDER

1. `CONTEXT_BUDGET.md` (~1,200 tokens)
2. `CREATIVE_MANDATE.md` (~1,200 tokens)
3. `SPEC_REFINEMENT.md` (~1,800 tokens)
4. `SILENT_FAILURES.md` (~1,500 tokens)
5. `KNOWLEDGE_INTEGRITY.md` (~1,600 tokens)
6. `.claude/skills/spec-examples/SKILL.md` (~950 tokens)
7. `engines/source/contracts.py` (~2,500 tokens)
8. `engines/source/SPEC.md` (~5,500 tokens)
9. `engines/normalization/SPEC.md` §2 only (~1,000 tokens)
10. `reference/ENTRY_EXAMPLE.md` (~1,600 tokens)
11. `reference/USER_SCENARIOS.md` (~2,700 tokens)

**Total: ~21,550 tokens. Budget remaining: ~133,000 tokens.**

## Files to NOT Read

VISION.md, DOMAIN.md, kr_decisions.md, STATUS.md, ORCHESTRATOR.md, other engine SPECs

## Known Issues

- Source SPEC written before full multi-layer detection was specified
- contracts.py derived from SPEC prose; mismatches likely
- Test fixtures exist but owner providing additional source data

## Progress Metrics

`python3 scripts/orient.py --brief` for full status.
SPEC Refinement: 0/14. Source Cycle 1 this session.

## What Last Session Did

Eighth hardening pass: GUI architecture (D-043, interface/GUI.md), autonomous orientation script (scripts/orient.py), updated PREPARATORY_ROADMAP with 8 streams and 10 completion criteria, updated requirements.txt with real dependencies, updated .env.template, added orient.py to startup procedure.

## Decisions Made

D-043: GUI technology (FastAPI + Tailwind + HTMX for MVP).

## Pending Owner Questions

- **Test data:** ✓ PROVIDED. 7 fixture sets covering PDF, Word, text, photos, owner-authored. See tests/fixtures/README.md.
- **API keys:** Fill in .env from .env.template when ready (OpenRouter or Anthropic + OpenAI).
