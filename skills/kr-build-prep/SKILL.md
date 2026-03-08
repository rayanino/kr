---
name: kr-build-prep
description: Prepares a finalized core SPEC for Claude Code implementation. Activate when a SPEC is ready for building, when asked to prepare for implementation, or when setting up the Claude Code environment. Surveys technology first, then produces architecture, stubs, tests, and CLAUDE.md.
---

# KR Build Prep — تحضير البناء

You are preparing a finalized KR engine core SPEC for Claude Code implementation. This is the first session of the BUILD step — it bridges design (Claude Chat) to implementation (Claude Code).

The cardinal rule: technology survey FIRST, architecture SECOND, deliverables THIRD. Building custom code for something a library already handles is waste.

---

## Part 1: Technology Survey

For every significant capability in the core SPEC, search for existing tools before designing anything.

Search pattern per capability:
1. `python library [capability] arabic` — domain-specific tools
2. `[capability] NLP tool 2025 2026` — recent developments
3. Verify tools from `reference/RESOURCES.md` actually do what's claimed

Evaluation criteria: Arabic support? Diacritics handling? Actively maintained? License compatible? What it actually does vs. README claims? Read the docs, not just the tagline.

Output:

```
## Technology Inventory — [Engine Name]

### Use (existing tool handles it)
| Capability | Library | Arabic support evidence |
|-----------|---------|----------------------|

### Build (nothing suitable exists)
| Capability | Why build? | Closest alternative | Gap |
|-----------|-----------|-------------------|-----|

### Needs testing
| Capability | Candidate | Concern | How to test |
|-----------|-----------|---------|-------------|
```

---

## Part 2: Claude Code Environment

### CLAUDE.md (under 200 lines)

Research shows Claude Code follows ~150-200 instructions reliably. Its system prompt uses ~50. Your CLAUDE.md gets ~100-150 instruction slots before quality degrades.

What goes IN CLAUDE.md: build commands, project conventions Claude gets wrong without instruction, critical file paths, constraints (Arabic handling, D-023 metadata rule).

What goes in separate docs/ files: detailed SPEC rules, architecture overview, test patterns.

What goes nowhere (Claude already knows it): Python conventions, git workflow, how to use standard libraries.

```markdown
# [Engine Name] — Build Guide

## Commands
test: pytest engines/{engine}/tests/ -x
lint: ruff check engines/{engine}/

## Architecture
[3-5 lines, point to docs/architecture.md]

## Critical Constraints
- Arabic diacritics: preserve byte-for-byte
- Metadata: never delete upstream fields (D-023)
- Errors: fail loudly, use error codes from SPEC §7
- [Engine-specific constraints]

## Key Files
[SPEC, contracts, fixtures, plan]
```

### Dev Docs

```
engines/{engine}/
├── CLAUDE.md           # Under 200 lines
├── docs/
│   ├── architecture.md # Module structure, data flow
│   ├── spec-rules.md   # Key SPEC rules extracted
│   └── testing.md      # Test strategy and fixtures
└── session-1-plan.md   # First build session scope
```

### Session Scoping

The tracer bullet stub for this engine already exists from Step 0. The first BUILD session deepens it: replace placeholder logic with real implementation for one format, one fixture, schema validation passing. Not all formats, not all edge cases.

Each subsequent session adds one capability with its tests.

---

## Part 3: Deliverables

### Contracts Audit
Compare `contracts.py` against the finalized SPEC. The tracer bullet (Step 0) established the initial contracts — verify the SPEC hasn't introduced fields or constraints that conflict with the validated boundary contracts. Every field matches in name, type, and optionality. Enums for constrained fields. Metadata pass-through fields present (D-023). Boundary compatibility with upstream/downstream.

### Module Architecture
Per module: purpose, inputs/outputs, SPEC sections it implements. Keep it simple — core engines are narrow by design.

### Stub Files
Function signatures with type hints, docstrings quoting the SPEC rule, `raise NotImplementedError`. No function bodies — that's Claude Code's job.

### Test Infrastructure
5a deterministic: schema validation, text integrity, metadata preservation, boundary compliance.
5b LLM-worker: per LLM call — what it does, what correct output looks like, which fixture to use.
5c LLM-evaluator: per output type — what an independent LLM checks, prompt template, which models.

See `reference/TESTING_FRAMEWORK.md` for the full testing architecture.

### NEXT.md for Session 1
Narrow scope, clear definition of done:

```markdown
# NEXT — [Engine] Build Session 1

## Task
Build [specific module] for [specific format] using [specific fixture].

## Done When
- [ ] Module passes all 5a deterministic tests
- [ ] Error paths from SPEC §7 handled
- [ ] Metadata preserved (D-023)
```

---

## Common Mistakes to Avoid

**Building without surveying.** Designing a custom parser when PyMuPDF already does it.

**Bloated CLAUDE.md.** Over 200 lines means Claude ignores half your instructions. Put detail in docs/ files.

**Over-scoped first session.** The first NEXT.md should target ONE format, ONE fixture, schema validation. Narrow is better than broad.

**Vague stubs.** `def process(input): pass` tells Claude Code nothing. Every stub needs exact types and a docstring referencing the SPEC.
