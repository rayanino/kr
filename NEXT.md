# NEXT — Engine Build Blueprint

## Current position: Source engine COMPLETE → Create repeatable build process
## What to do: Trace the entire source engine journey and distill it into a specific, repeatable blueprint
## Context: Source engine done (reference/SOURCE_ENGINE_COMPLETION.md). 6 engines remaining. Before building anything, we need the blueprint that makes every engine build systematic instead of improvised.
## Owner action needed: YES — This is a Claude Chat discussion session

**IMPORTANT — What to IGNORE:** `reference/ENGINE_FACTORY_PLAN.md` (~1,260
lines) is a previous attempt at this problem that was deemed too abstract
and over-engineered. It is DEFERRED. Do not incorporate its multi-agent
architecture, OpenClaw references, or elaborate quality gate system. The
Blueprint should be grounded in what actually worked, not in theoretical
infrastructure. Similarly, `skills/shared/ENGINE_PROTOCOL.md` is the
existing ABSTRACT 4-step process — the Blueprint is its CONCRETE
implementation, filled with specific actions learned from building the
source engine. ENGINE_PROTOCOL stays as the governing framework; the
Blueprint fills in "here's exactly how we do each step."

**NOTE on repo clutter:** The repo root has ~27 .md files, many from the
Phase D evaluation. This is expected — repo cleanup is deliverable #3.
Focus on the files listed below, not on making sense of everything at root.

---

## Deliverable sequence (strict order)

### 1. Blueprint (`reference/ENGINE_BUILD_BLUEPRINT.md`)

Trace the full source engine history and distill into a concrete,
step-by-step recipe for building any engine. The audience is both Claude
Code (which executes the build) and Claude Chat (which handles SPEC
design and knowledge verification). Each step must specify who does it.

**Specificity standard:** For every step, the Blueprint must answer:
what exact action is taken, what files are read/produced, what quality
check runs on the output, and what the self-review protocol is. If a
Claude Code session following the Blueprint would need to improvise, the
Blueprint isn't specific enough.

**Critical requirement — mandatory self-review on every output:**
The source engine's worst bugs were self-review failures. Every step that
produces output (SPEC text, code, evaluation verdicts, gold baselines)
must include a mandatory critical self-review protocol:
- Minimum 2 rounds of structured review
- Clear specification of what each round checks
- No output accepted without passing review
- See `PHASE_D_SESSION_A_REPORT.md` §"Self-Review Rounds" for a concrete
  example: 5 rounds checking checklist compliance, internal contradictions,
  web source verification, death date tracking, and post-review corrections.

**Structure hint:** The Blueprint should follow the engine lifecycle but
fill in concrete details: how SPEC work actually happens (comment batches,
research depth, kr-integrity audit), how the build is organized (modules,
tests, sessions), how evaluation works (the 4-layer methodology from Phase
D), how bugs are identified and fixed, and how the engine is proven done.
Each step should be self-contained enough that it could eventually be
assigned to an agent.

### 2. Decision Playbook (`reference/DECISION_PLAYBOOK.md`)

The institutional memory for all future sessions/agents. Captures every
pattern, heuristic, domain rule, and anti-pattern from the source engine.

**Audience:** The Oracle agent (`claude -p --effort max`), new Claude Chat
sessions in future projects, and eventually researcher agents that verify
knowledge output autonomously.

**Format:** NOT narrative prose. Structured as:
- Per-decision-type sections (author attribution, genre classification,
  trust evaluation, death dates, multi-layer detection, etc.)
- Explicit trigger→action pairs ("IF X → THEN Y")
- Anti-patterns with examples ("DO NOT do X because Y happened")
- Verification source hierarchy with reliability notes
- Arabic text handling rules

### 3. Repo cleanup

Remove stale files, archive completed work, ensure the repo is clean
and navigable for the normalization engine project. This is a Claude Code
task.

### After these three: discuss agent team architecture for autonomous building.

---

## Source material — read in this order

### Priority 1: Lessons learned (highest signal, read first)
- `engines/source/review/PHASE_A_LESSONS.md` (111 lines) — deterministic phase
- `tests/results/source_engine/phase_c/PHASE_C_LESSONS.md` (98 lines) — LLM phase
- `tests/results/source_engine/phase_d/PHASE_D_LESSONS.md` (91 lines) — calibration phase
- `SILENT_FAILURES.md` (176 lines) — failure modes discovered

### Priority 2: What the finished engine looks like
- `reference/SOURCE_ENGINE_COMPLETION.md` (105 lines) — completion report
- `engines/source/SPEC_CORE.md` (1820 lines) — what a finished SPEC looks like
- `KNOWLEDGE_INTEGRITY.md` (197 lines) — corruption threats the process must prevent
- `RESULT_PRESERVATION.md` (176 lines) — how results feed downstream

### Priority 3: How evaluation actually worked
- `PHASE_D_EVALUATION_PROTOCOL.md` (193 lines) — the 4-layer methodology
- `PHASE_D_AGGREGATION_REPORT.md` (173 lines) — aggregation methodology
- `PHASE_D_SESSION_A_REPORT.md` (327 lines) — **best example of self-review rounds**
- `PHASE_D_CRITICAL_REVIEW.md` (300 lines) — adversarial review of GO verdict
- `PHASE_D_PATTERN_ANALYSIS.md` (239 lines) — systematic patterns found

### Priority 4: How hardening and fixes worked
- `reference/PRE_BATCH_EXECUTION_PROTOCOL.md` (362 lines) — hardening process
- `reference/PRE_BATCH_VERIFICATION_PLAN.md` (257 lines) — verification methodology
- `CLAUDE_CODE_POST_EVAL_FIXES.md` (236 lines) — post-evaluation fixes
- `reference/archive/sessions/steps/STEP4_BUG_FIX_SPECS.md` — bug specification

### Priority 5: Earlier evaluation sessions (sample, don't exhaust)
- `reference/archive/sessions/phase_c/PHASE_C_EVALUATION_FRAMEWORK.md` (632 lines) — original framework
- Phase C session reports (7 files, ~2,700 lines total) — in `reference/archive/sessions/phase_c/`
- Phase D session reports B-D (~1,150 lines total) — at repo root

### Priority 6: The abstract protocol (for reference, not to replicate)
- `skills/shared/ENGINE_PROTOCOL.md` (331 lines) — the 4-step process
- Git log: `git log --oneline --reverse` — 160+ commits tracing the journey

### Context risk: The total source material is ~6,000+ lines. The new
chat should read Priority 1-3 fully (~1,600 lines), then sample from
Priority 4-6 as needed. If context runs tight, finish the build process
sections of the Blueprint before the evaluation methodology sections —
partial completion in priority order is better than shallow full coverage.

---

## Budget
- Spent: €30.60
- Remaining: ~€69.40
- Note: The Blueprint and Playbook are Claude Chat deliverables (zero API cost).
  Budget matters for Claude Code sessions later.
