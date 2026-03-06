# NEXT SESSION

## Session Type
SPEC_REFINEMENT

## Immediate Task

Execute refinement cycle 1 on the **source engine SPEC** (`engines/source/SPEC.md`), following `SPEC_REFINEMENT.md` Steps 1-9 exactly.

The source engine is the pipeline entry point. Its SPEC must be airtight before any implementation begins.

## Definition of Done

1. Defect ledger produced with exact quotes and fixes for every defect found
2. All §4.A subsections have at least one concrete I/O example with real Arabic text
3. All 7 knowledge integrity threats explicitly addressed in the SPEC
4. Technology references verified with at least 3 web searches; RESOURCES.md updated
5. Upstream/downstream boundary verified with `python3 scripts/verify_metadata_flow.py`
6. Two self-review rounds completed; Three Challenges passed
7. Second research round completed (3+ additional web searches)
8. Refined SPEC committed with defect count in commit message
9. `engines/source/CLAUDE.md` updated with refinement status

## Context

All 14 SPECs are written but were drafted BEFORE `KNOWLEDGE_INTEGRITY.md`, `CHALLENGE_PROTOCOL.md`, and the skills were created. They need refinement against these new standards before implementation can begin.

**This is the first SPEC refinement session.** The source engine goes first because it's the pipeline entry point — all downstream engines depend on its output contract.

The autonomous system now includes:
- `SPEC_REFINEMENT.md` — 9-step iterative refinement cycle
- `SESSION_CONTINUITY.md` — bulletproof session handoff protocol
- `KNOWLEDGE_INTEGRITY.md` — 7-threat model for knowledge safety
- `CHALLENGE_PROTOCOL.md` — Three Challenges + quality gates + anti-patterns
- 5 skills: knowledge-safety, arabic-text, technology-survey, scholarly-design, spec-examples
- 7 agents, 14 commands, 4 scripts

## Files to Read — IN THIS ORDER

1. `SPEC_REFINEMENT.md` — the refinement protocol (follow this step by step)
2. `KNOWLEDGE_INTEGRITY.md` — threat model (needed for Step 2)
3. `.claude/skills/spec-examples/SKILL.md` — example generation guide (needed for Step 3)
4. `engines/source/SPEC.md` — the SPEC being refined (THE deliverable)
5. `engines/normalization/SPEC.md` §2 only — downstream boundary check (needed for Step 5)
6. `reference/ENTRY_EXAMPLE.md` — quality target (needed for Step 6)
7. `reference/USER_SCENARIOS.md` — user scenarios (needed for Step 6)

## Files to NOT Read

- VISION.md (too large, not needed for SPEC refinement)
- DOMAIN.md (already incorporated into the SPEC)
- Other engine SPECs (not needed except normalization §2)
- kr_decisions.md (decisions already in the SPEC)
- STATUS.md (not needed)
- ORCHESTRATOR.md (that's for implementation sessions, not refinement)

## Known Issues

- `vision_defects_s7.md` (now in archive) noted that VISION.md §7.2 still says "sufficient identifying information" which is vague. Check whether the source SPEC resolves this.
- The source SPEC was written before multi-layer detection details were added to DOMAIN.md. Verify §4.A.3 covers the full multi-layer model.

## Progress Metrics

SPEC Refinement:
- Source engine: Cycle 0 (not yet started)
- All other engines: Cycle 0 (not yet started)
- Implementation: blocked until source + normalization SPECs pass refinement

Milestone 1: 0/5 tasks complete (blocked by SPEC refinement)

## What Last Session Did

Hardened the autonomous system with SPEC refinement protocol, session continuity protocol, spec-examples skill, refine-spec command, repo cleanup (archived vision_defects_s7.md), rewrote CLAUDE.md for maximum effectiveness, and redirected NEXT.md from premature implementation to SPEC refinement.

## Decisions Made

None. Infrastructure hardening, not architectural decisions.

## Pending Owner Questions

None currently. SPEC refinement may surface domain questions.
