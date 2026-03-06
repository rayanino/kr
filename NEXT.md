# NEXT SESSION

## Session Type
SPEC_REFINEMENT

## Immediate Task

Execute refinement cycle 1 on the **source engine SPEC** (`engines/source/SPEC.md`).

Follow `SPEC_REFINEMENT.md` Steps 0-10. Step 0 (Creative Exploration from `CREATIVE_MANDATE.md`) comes FIRST. Use `CONTEXT_BUDGET.md` to plan reads.

**New this session:** `engines/source/contracts.py` contains machine-readable Pydantic models for the source engine's output contract. Cross-reference the SPEC prose against these models during refinement — any mismatch is a defect.

## Definition of Done

**Creative (Step 0):**
1. At least 3 new capabilities for §4.B, each with named technology and concrete output example
2. Minimum 8 web searches during creative exploration
3. Invention Notes incorporated into the SPEC

**Correctness (Steps 1-8):**
4. Defect ledger with exact quotes and fixes
5. All 7 silent failure patterns checked (SILENT_FAILURES.md)
6. All 7 knowledge integrity threats addressed (KNOWLEDGE_INTEGRITY.md)
7. All §4.A subsections have concrete I/O examples with real Arabic text
8. contracts.py validated against SPEC §3 — any mismatches resolved
9. Boundary with normalization verified: `python3 scripts/verify_metadata_flow.py --boundary source normalization`
10. Two self-review rounds; Three Challenges each found at least one issue

**Final (Steps 9-10):**
11. Refined SPEC committed with defect count AND capability count
12. `engines/source/CLAUDE.md` updated with refinement status

## Context

The preparatory phase includes 7 work streams (see `PREPARATORY_ROADMAP.md`):
1. SPEC refinement — iterative hardening of all 14 SPECs
2. Machine-readable contracts — Pydantic models for engine boundaries
3. Resource survey — tools and technology landscape
4. Claude Code environment optimization
5. VISION.md structure optimization
6. Test data preparation
7. Architectural validation

This session does Stream 1 (source SPEC refinement) using the Stream 2 deliverable (contracts.py) as a cross-reference. Future sessions will interleave streams.

## Files to Read — IN THIS ORDER

**Budget and creative protocol (~2,400 tokens):**
1. `CONTEXT_BUDGET.md`
2. `CREATIVE_MANDATE.md`

**Refinement protocol and tools (~5,400 tokens):**
3. `SPEC_REFINEMENT.md`
4. `SILENT_FAILURES.md`
5. `KNOWLEDGE_INTEGRITY.md`
6. `.claude/skills/spec-examples/SKILL.md`

**The deliverables and references (~11,800 tokens):**
7. `engines/source/contracts.py` — machine-readable output contract
8. `engines/source/SPEC.md` — THE deliverable
9. `engines/normalization/SPEC.md` §2 only — downstream boundary
10. `reference/ENTRY_EXAMPLE.md` — quality target
11. `reference/USER_SCENARIOS.md` — user scenarios

**Total: ~19,600 tokens. Budget remaining: ~135,000 tokens.**

## Files to NOT Read

- VISION.md, DOMAIN.md, kr_decisions.md, STATUS.md, ORCHESTRATOR.md, MILESTONES.md, other engine SPECs

## Known Issues

- Source SPEC written before multi-layer detection was fully specified in DOMAIN.md
- VISION.md §7.2 "sufficient identifying information" — check if SPEC resolves
- contracts.py was derived from SPEC §3 prose; mismatches between the two are likely

## Progress Metrics

SPEC Refinement: 0/14 started. Source Cycle 1 this session.
Machine-readable contracts: source (DONE), normalization (not started).
Implementation: blocked until SPECs pass refinement.

## What Last Session Did

Fifth hardening pass: Compressed PROJECT_INSTRUCTIONS 312→101 lines (research showed instruction overload degrades performance). Created STEERING.md (concise project context for Claude Code). Created PREPARATORY_ROADMAP.md (7 work streams for the full preparatory phase, not just SPEC refinement). Created source engine contracts.py (Pydantic models for machine-readable output contract). Added gold standard before/after refinement example to SPEC_REFINEMENT.md.

## Decisions Made

None. Preparatory infrastructure.

## Pending Owner Questions

- **Test data:** Need sample Shamela directories committed to the repo for testing. Can you provide 2-3 Shamela exports of varying complexity?
