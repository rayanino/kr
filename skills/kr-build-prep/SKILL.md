---
name: kr-build-prep
description: Prepare engine for Claude Code with tech survey, contracts, stubs, optimized CLAUDE.md. Use for "prepare for building", "implementation prep", or when a finalized SPEC is ready for coding.
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

## Build Orchestration: Single Session vs. Agent Teams

There are three ways to run Claude Code on a KR engine. Choose based on what you're building.

### Option A: Single Session (Default — Start Here)

One Claude Code instance, one task, one context window. Use for:
- First build session on any engine (get the basics working)
- Focused module implementation (one format, one capability)
- Bug fixes and small changes
- Any task where parallelism adds no value

This is always the starting point. Don't use agent teams until single sessions are working cleanly on the engine.

### Option B: Agent Teams (For Complex Build Sessions)

Multiple Claude Code instances working in parallel with built-in coordination. Requires Opus 4.6 and one-line setup.

**Setup (one-time):**
```bash
# Add to environment or Claude Code settings.json:
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1

# Recommended: install tmux for split-pane visibility
# macOS: brew install tmux
# Ubuntu: sudo apt install tmux

# Start tmux before launching Claude Code
tmux
```

**When to use for KR:**
- Building a full engine module end-to-end (builder + tester + reviewer)
- Processing a large batch of test fixtures in parallel
- Refactoring across multiple files that interact (contracts + engine + tests)
- Any session where you need 3+ specialized perspectives simultaneously

**KR-specific team templates:**

**Template 1: Builder-Tester-Reviewer (the standard KR team)**
```
Create an agent team to build [module name] for the [engine] engine.

Spawn three teammates:
- Builder: Implement [module] following engines/{engine}/docs/spec-rules.md. 
  Own all files in engines/{engine}/ except tests/.
- Tester: Write and run tests for [module] using fixture [fixture name].
  Own all files in engines/{engine}/tests/. Run pytest after each builder change.
  Flag any test failure immediately.
- Reviewer: Read the SPEC at [spec path] §4.A.[section]. After builder completes 
  each function, verify the implementation matches the SPEC rules. Check Arabic 
  text handling and metadata preservation (D-023). Do NOT write code — only review 
  and flag issues.

Coordinate through the shared task list. Builder implements, tester verifies, 
reviewer audits. No code merges until all three agree.
```

**Template 2: Multi-Format Expansion (after base works)**
```
Create an agent team to add [format] support to the [engine] engine.

Spawn three teammates:
- Format specialist: Implement the [format] handler in engines/{engine}/formats/.
  Reference the existing Shamela handler as the pattern to follow.
- Integration tester: Run the full pipeline on [format] test fixtures.
  Compare output schema against contracts.py. Flag any field that's missing 
  or wrong.
- Regression guard: Run ALL existing tests after each change. If any 
  previously-passing test breaks, halt and report immediately. Nothing 
  ships with regressions.
```

**Template 3: Evaluation Sprint (for kr-evaluate phase)**
```
Create an agent team to evaluate [engine] output on [fixture set].

Spawn three teammates:
- Deterministic checker (5a): Run schema validation, text integrity, metadata 
  completeness on all output files. Produce a structured report.
- LLM worker auditor (5b): For each LLM call the engine made, compare the 
  call's output against the expected result. Score accuracy per task type.
- Quality reviewer (5c): Run independent LLM evaluation on 10 sampled outputs.
  Use the rubric from the SPEC's §5. Flag anything the engine's self-validation 
  missed.

Each teammate produces an independent report. Lead synthesizes into a single 
assessment with the inter-engine gate decision.
```

**Cost and limits:**
- Each teammate is a full Opus 4.6 session. A 3-agent team costs ~3x a single session.
- On Pro plan (~5x free tier): budget for 1-2 team sessions per day.
- On Max plan ($100-200/month): budget for 8-10 team sessions per day.
- 3-5 teammates is optimal. Beyond 5, coordination overhead eats the gains (Google DeepMind research confirms diminishing returns).
- All teammates run Opus 4.6 — no per-role model selection yet.
- Agent teams are ephemeral. No memory between sessions. All state must be in files.

**What agent teams can NOT do:**
- They can't replace good SPEC design. Garbage in, garbage out — faster.
- They can't coordinate across engines (each team works on one codebase area).
- They don't persist. Every team is spawned fresh each session.
- Nested teams are not supported (a teammate can't spawn its own team).

### Option C: Git Worktrees (For Manual Parallelism)

If you want parallel sessions without the coordination overhead of agent teams:
```bash
claude -w feature-name    # Creates isolated worktree with its own branch
```

Use for: working on two independent features simultaneously, or running a long test suite in one worktree while coding in another. Lighter than agent teams, but no inter-session communication.

### Option D: The Bash Loop (For Autonomous Test Runs)

From the C compiler case study — simplest autonomous pattern:
```bash
while true; do claude -p "$(cat PROMPT.md)"; done
```

Use for: running a test-fix-retest cycle overnight. Claude reads the prompt, runs tests, fixes failures, commits, and the loop restarts with a fresh context. Good for regression grinding after the main implementation is done.

### Progression for Each Engine

```
Session 1-2:  Single session. Get basic module working. One format, one fixture.
Session 3-5:  Single session. Add formats, edge cases, error handling.
Session 6+:   Agent teams IF the engine is complex enough to benefit.
              (Source engine: yes. Passaging engine: probably not.)
Evaluation:   Agent teams for the evaluation sprint (Template 3).
Regression:   Bash loop for overnight test grinding.
```

### Other Tools (Optional, Not Required)

**Faber** (github.com/orecus/faber): Desktop GUI wrapping Claude Code with Kanban and multi-pane sessions. Adds visual task management but also adds complexity. Consider only if the terminal workflow feels limiting.

---

## Anti-Patterns

**Building without surveying.** Designing a custom parser before checking if PyMuPDF already does it.

**Bloated CLAUDE.md.** Over 200 lines → Claude ignores half your instructions. Prune ruthlessly. Put detail in docs/ files.

**Over-scoped first session.** First NEXT.md should target ONE format, ONE fixture, schema validation. Not all 6 formats.

**Vague stubs.** `def process(input): pass` tells Claude Code nothing. Every stub needs exact types and a docstring quoting the SPEC.
