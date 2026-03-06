# NEXT SESSION

## Session Type
SPEC_REFINEMENT

## Immediate Task

Execute refinement cycle 1 on the **source engine SPEC** (`engines/source/SPEC.md`).

Follow `SPEC_REFINEMENT.md` Steps 0-10 exactly. Step 0 (Creative Exploration) comes FIRST — before any review or correction. Use `CONTEXT_BUDGET.md` to plan your reads.

The source engine is the pipeline entry point. Its SPEC must be airtight before any implementation begins.

## Definition of Done

**Creative (from Step 0):**
1. At least 3 new capabilities invented for §4.B, each with named technology AND concrete output example
2. Minimum 8 web searches conducted during creative exploration
3. Invention Notes written and incorporated into the SPEC

**Correctness (from Steps 1-8):**
4. Defect ledger produced with exact quotes and specific fixes for every defect
5. All 7 silent failure patterns checked against §4 rules (SILENT_FAILURES.md)
6. All 7 knowledge integrity threats explicitly addressed in the SPEC
7. All §4.A subsections have at least one concrete I/O example with real Arabic text
8. Technology references verified with web searches; RESOURCES.md updated
9. Upstream/downstream boundary verified with `python3 scripts/verify_metadata_flow.py`
10. Two self-review rounds completed; Three Challenges each found at least one issue

**Final (from Steps 9-10):**
11. Silent failure check passed (no hollow examples, circular definitions, etc.)
12. Refined SPEC committed with defect count AND capability count in message
13. `engines/source/CLAUDE.md` updated with refinement status

## Context

All 14 SPECs are drafted but need iterative refinement before implementation. This is the first refinement session. The source engine goes first because all downstream engines depend on its output.

The autonomous system includes governance documents, skills, agents, commands, scripts, and hooks. Key documents for THIS session are listed in "Files to Read" below.

## Files to Read — IN THIS ORDER

**First (budget and creative protocol):**
1. `CONTEXT_BUDGET.md` — know your token budget before reading anything else (~1,200 tokens)
2. `CREATIVE_MANDATE.md` — invention protocol; creative exploration comes FIRST (~1,200 tokens)

**Then (refinement protocol and detection tools):**
3. `SPEC_REFINEMENT.md` — the 11-step cycle, follow precisely (~1,800 tokens)
4. `SILENT_FAILURES.md` — 7 patterns of "looks right but isn't" (~1,500 tokens)
5. `KNOWLEDGE_INTEGRITY.md` — threat model for Step 2 (~1,600 tokens)
6. `.claude/skills/spec-examples/SKILL.md` — example generation for Step 3 (~950 tokens)

**Then (the deliverable and reference material):**
7. `engines/source/SPEC.md` — THE deliverable (~5,500 tokens)
8. `engines/normalization/SPEC.md` §2 only — downstream boundary for Step 5 (~1,000 tokens)
9. `reference/ENTRY_EXAMPLE.md` — quality target for Step 6 (~1,600 tokens)
10. `reference/USER_SCENARIOS.md` — user scenarios for Step 6 (~2,700 tokens)

**Total reading cost: ~19,050 tokens. Budget remaining for work: ~129,000 tokens. Comfortable.**

## Files to NOT Read

- VISION.md (47K tokens — never read whole; use extract_vision_sections.py if needed)
- DOMAIN.md (7K tokens — already incorporated into the SPEC)
- kr_decisions.md (9.5K tokens — decisions already in the SPEC)
- STATUS.md, ORCHESTRATOR.md, MILESTONES.md (not needed for refinement)
- Other engine SPECs except normalization §2

## Known Issues

- VISION.md §7.2 still says "sufficient identifying information" (vague). Check if source SPEC resolves this.
- Source SPEC was written before full multi-layer detection was added to DOMAIN.md. Verify coverage.
- Source SPEC's §4.B capabilities may need refresh — they were written before KNOWLEDGE_INTEGRITY.md existed.

## Progress Metrics

SPEC Refinement: 0/14 engines started. Source engine Cycle 0 (this session starts Cycle 1).
Implementation: blocked until source + normalization SPECs pass refinement.
Milestone 1: 0/5 tasks complete.

## What Last Session Did

Fourth hardening pass: Created CREATIVE_MANDATE.md (invention-first protocol with Creative Exploration Protocol and Anti-Secretary Test), CONTEXT_BUDGET.md (concrete token costs for every file), SILENT_FAILURES.md (7 detection patterns for output that looks right but isn't). Updated SPEC_REFINEMENT.md with Step 0 (Creative Exploration), Step 9 (Silent Failure Check), context budget reference, and creative success criteria. Updated PROJECT_INSTRUCTIONS.md self-review with anti-sycophancy checks, creative mandate, and silent failure detection. Updated session workflow with 12-point SPEC refinement step.

## Decisions Made

None. Infrastructure hardening.

## Pending Owner Questions

None currently. Creative exploration and SPEC refinement may surface domain questions.
