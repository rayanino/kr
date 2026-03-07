---
name: kr-build-prep
description: ALWAYS activate when a finalized SPEC needs Claude Code prep. Triggers: "prepare for building", "build prep", "implementation prep". Do not write stubs or CLAUDE.md without tech survey first.
---

# KR Build Prep — تحضير البناء

You are preparing a finalized KR engine SPEC for Claude Code implementation. This skill has two responsibilities: (1) the technology survey and architecture design, and (2) optimizing the Claude Code environment for maximum build quality. Both are research-heavy.

**Cardinal rule:** Technology survey FIRST, Claude Code optimization SECOND, then produce deliverables.

---

## Part 1: Technology Survey (MANDATORY FIRST)

For every significant capability in the SPEC, search for existing tools BEFORE designing anything.

### Search Pattern Per Capability

1. `python library [capability] arabic` (specific to our domain)
2. `[capability] NLP tool 2025 2026` (recent developments)
3. Verify tools from RESOURCES.md actually do what we claim

### Evaluation Criteria

For each tool: Arabic support? Diacritics handling? Actively maintained? License compatible? What it ACTUALLY does vs. README claims? (Read the docs, not just the tagline.)

### Technology Inventory Output

```
## Technology Inventory — [Engine Name]

### Use (don't build)
| Capability | Library | Arabic? | Diacritics? | Evidence |
|-----------|---------|---------|-------------|----------|

### Build (nothing suitable exists)
| Capability | Why build? | Closest available | Gap |
|-----------|-----------|-------------------|-----|

### Uncertain (needs testing)
| Capability | Candidate | Concern | How to test |
|-----------|-----------|---------|-------------|
```

---

## Part 2: Claude Code Environment Optimization

This is where most build-prep skills fail. Research shows the environment around Claude Code matters more than the code itself. The C compiler case study: "Most of my effort went into designing the environment around Claude."

### CLAUDE.md Design (CRITICAL — Under 200 Lines)

Research confirms: frontier models follow ~150-200 instructions reliably. Claude Code's system prompt already uses ~50. Your CLAUDE.md gets ~100-150 instruction slots before quality degrades.

**What goes IN CLAUDE.md:**
- Build commands (test, lint, type-check)
- Project-specific conventions Claude gets wrong without instruction
- File paths that Claude needs repeatedly
- Critical constraints (Arabic text handling, D-023 metadata rule)

**What goes in SEPARATE files** (Claude reads on demand):
- Detailed SPEC rules → `docs/spec-rules.md`
- Architecture overview → `docs/architecture.md`
- Test patterns → `docs/testing.md`

**What goes NOWHERE** (Claude already knows it):
- Python syntax conventions
- General git workflow
- How to use standard libraries

### Dev Docs Pattern

For each build session, create a task directory:
```
engines/{engine}/
├── CLAUDE.md              # Under 200 lines, always loaded
├── docs/
│   ├── architecture.md    # Module structure, data flow
│   ├── spec-rules.md      # Key SPEC rules for this engine
│   └── testing.md         # Test strategy and fixtures
├── {session}-plan.md      # Accepted plan for this session
├── {session}-context.md   # Key files, decisions from this session
└── {session}-tasks.md     # Checklist of work items
```

Claude Code performs best when it has a written plan to follow and a checklist to track progress. The plan file is created at session start (in plan mode) and the tasks file tracks completion.

### Session Scoping

**First session for any engine:** Target the SIMPLEST end-to-end path.
- One format (e.g., Shamela HTML for the source engine)
- One test fixture
- Schema validation passing
- NOT all formats, NOT all edge cases

**Subsequent sessions:** Add one format or capability at a time.

Each session's NEXT.md should be narrow enough that Claude Code can complete it without running out of context.

---

## Part 3: Produce Deliverables

### 3a: Contracts Audit

Compare existing `contracts.py` against the finalized SPEC:
- Every field matches in name, type, and optionality
- Enums/Literals for constrained fields
- Metadata pass-through fields present (D-023)
- Upstream/downstream boundary compatibility

### 3b: Module Architecture

```
engines/{engine}/
├── __init__.py
├── contracts.py        # Pydantic models
├── engine.py           # Entry point
├── [module_1].py       # Processing modules
└── tests/
    ├── test_[module_1].py
    └── test_integration.py
```

Per module: purpose, input/output, dependencies, SPEC sections it implements, complexity estimate.

### 3c: Stub Files

Function signatures with type hints, docstrings quoting the SPEC rule, and `raise NotImplementedError`. NO function bodies — that's Claude Code's job.

### 3d: Test Infrastructure

**5a Deterministic:**
```
- Schema validation (Pydantic)
- Text integrity (Arabic character/diacritic preservation)
- Metadata preservation (D-023)
- Boundary contract compliance
```

**5b LLM-Worker:** Per LLM call: what it does, what correct output looks like, which fixture to use, how to judge.

**5c LLM-Evaluator:** Per output type: what an independent LLM checks, prompt template, scoring rubric, which models.

### 3e: CLAUDE.md (Under 200 Lines)

Write the engine-specific CLAUDE.md:
```markdown
# [Engine Name] — Build Guide

## Commands
test: pytest engines/{engine}/tests/ -x
lint: ruff check engines/{engine}/
typecheck: pyright engines/{engine}/

## Architecture
[3-5 line summary, point to docs/architecture.md for detail]

## Critical Constraints
- Arabic diacritics: preserve byte-for-byte. NFC normalization only.
- Metadata: never delete upstream fields (D-023). Add, don't remove.
- Errors: fail loudly. No silent data loss. Use error codes from SPEC §7.
- Consensus: all content decisions require multi-model agreement.
- [Engine-specific constraints]

## Key Files
- SPEC: reference/[engine]-spec.md
- Contracts: engines/{engine}/contracts.py
- Fixtures: tests/fixtures/[relevant files]
- Plan: engines/{engine}/{session}-plan.md

## Don'ts
- Don't modify contracts.py without approval
- Don't implement §4.B yet — start with §4.A
- Don't optimize for speed — optimize for correctness
```

### 3f: NEXT.md

Write the first build session directive — narrow scope, clear definition of done:
```markdown
# NEXT — [Engine] Build Session 1

## Task
Build [specific module] for [specific format] using [specific fixture].

## Definition of Done
- [ ] [Module] passes deterministic tests
- [ ] Error paths from SPEC §7 handled
- [ ] Metadata preserved (D-023)
- [ ] Integration test with upstream passes

## Read First
- engines/{engine}/CLAUDE.md
- engines/{engine}/docs/architecture.md
- engines/{engine}/{session}-plan.md
```

---

## Build Orchestration

**Default: single Claude Code session.** Start every engine with one session, one format, one fixture. Agent teams, worktrees, and autonomous loops are options for later sessions.

For the full orchestration guide — agent team templates, cost estimates, progression per engine, worktree and bash loop patterns — consult `BUILD_ORCHESTRATION.md` in this skill's directory.

---

## Anti-Patterns

**Building without surveying.** Designing a custom parser before checking if PyMuPDF already does it.

**Bloated CLAUDE.md.** Over 200 lines → Claude ignores half your instructions. Prune ruthlessly. Put detail in docs/ files.

**Over-scoped first session.** First NEXT.md should target ONE format, ONE fixture, schema validation. Not all 6 formats.

**Vague stubs.** `def process(input): pass` tells Claude Code nothing. Every stub needs exact types and a docstring quoting the SPEC.
