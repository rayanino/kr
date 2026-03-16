# Engine Factory — Autonomous Pipeline Build System

## Context

The source engine took ~1 week of ad-hoc, manually-driven work across 6+ build sessions, growing far beyond the initial plan. The user wants an **autonomous, repeatable factory** for the remaining 6 engines that prioritizes one thing above all else: **accuracy and flawless engines.** Time and money are explicitly not constraints. The factory should take as long as needed, use whatever resources are needed, and never cut corners.

The project has strong foundations: ENGINE_PROTOCOL.md defines the 4-step process, 9 domain skills encode KR-specific knowledge, 4 quality gate scripts catch errors, and the source engine provides a proven reference pattern. What's missing is the **orchestration layer** that turns these ingredients into a self-driving factory with uncompromising quality standards.

### Governing Principle

**Every decision in this plan optimizes for correctness, never for speed.** If a quality measure adds work but catches even one error that would corrupt the pipeline, it is worth it. The library IS the user's knowledge — an error here is an error in his mind.

---

## Technology Decision

### Primary Stack

| Tool | Role | Reasoning |
|------|------|-----------|
| **Claude Code (Opus 4.6, 1M context)** | PRIMARY BUILD ENVIRONMENT | Proven (source engine built successfully), domain-aware (9 KR skills), quality infra in place (4 scripts, 8 agents), 1M context window holds entire engine context without compaction risk |
| **OpenClaw (v2026.3.13)** | MULTI-AGENT QUALITY COORDINATION | `sessions_send` for Builder→Reviewer review loops, `sessions_spawn` for independent verification, agent isolation for separate roles, Telegram notifications for human gates |
| **OpenRouter** | MULTI-MODEL CONSENSUS | Expanded consensus pool: Command A + Opus 4.6 (existing 92.3% pair) + GPT-4o + Gemini 2.5 Pro. 4 models for critical content decisions, 2-model minimum for non-critical |
| **Codex Plus** | PARALLEL RESEARCH | Fire-and-forget Step 2 experiments running independently. Supplements the primary Claude Code research |

### Why OpenClaw as quality coordinator (not just monitoring)

The source engine's post-Phase-C bugs (FIX-C04 through C08) were all **self-review failures** — the single builder agent missed its own errors. The same principle KR applies to LLM decisions applies to the build process itself:

> **D-041: Never trust a single LLM for content decisions → Multi-model consensus**
> **Corollary: Never trust a single agent for engine building → Multi-agent quality assurance**

OpenClaw provides the primitives for structured multi-agent review:

- **`sessions_send`** — Builder sends work to Reviewer, blocks for response. Up to 5 ping-pong turns for discussion. Messages tagged with `provenance.kind = "inter_session"` for auditability.
- **`sessions_spawn`** — Builder spawns independent verification task on Verifier agent. Non-blocking. Results posted back when complete.
- **Agent isolation** — Each agent has separate workspace, session store, tool permissions. Reviewer is read-only (can't modify code). Verifier has web search + `exec` (for Usul.ai queries).
- **Hooks** — Event-driven scripts fire on session events. Git post-commit hooks can trigger review cycles.
- **Telegram notifications** — Human gates trigger owner notification immediately.

**Why this improves accuracy:** Within each ENGINE_PROTOCOL step, every sub-step gets independent review before proceeding. No code is committed without a second agent verifying SPEC compliance, Arabic safety, D-023 metadata flow, and knowledge integrity. No gold baseline is accepted without independent scholarly verification.

### Three Agent Roles

```
┌─────────────────────────────────────────────────────┐
│  OpenClaw Gateway (24/7, coordinates all agents)    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────┐   sessions_send    ┌───────────┐ │
│  │   BUILDER    │ ───────────────→   │ REVIEWER  │ │
│  │              │ ←───────────────   │           │ │
│  │ Claude Code  │   review feedback  │ Read-only │ │
│  │ Full tools   │                    │ SPEC+code │ │
│  │ 1M context   │   sessions_spawn   │ Arabic    │ │
│  │ All skills   │ ──────────────→    │ safety    │ │
│  └──────────────┘                    │ D-023     │ │
│         │                            │ Knowledge │ │
│         │ sessions_spawn             │ integrity │ │
│         ▼                            └───────────┘ │
│  ┌──────────────┐                                  │
│  │  VERIFIER    │                                  │
│  │              │                                  │
│  │ Web search   │                                  │
│  │ Usul.ai      │                                  │
│  │ Independent  │                                  │
│  │ test writing │                                  │
│  │ Scholarly    │                                  │
│  │ verification │                                  │
│  └──────────────┘                                  │
└─────────────────────────────────────────────────────┘
```

| Agent | Model | Tools | Responsibility |
|-------|-------|-------|----------------|
| **Builder** | Opus 4.6 (1M) via Claude Code | Full tool access (edit, exec, MCP, skills) | Writes code, runs tests, manages state, drives ENGINE_PROTOCOL |
| **Reviewer** | Opus 4.6 | Read-only file access, quality scripts (`exec`), `sessions_send` | Reviews every output against SPEC, Arabic safety (skill), D-023 compliance, knowledge integrity (skill). Can REJECT work. |
| **Verifier** | Opus 4.6 | Web search, `exec` (for scripts), file read, `sessions_send` | Writes independent tests from SPEC (without seeing Builder's implementation), scholarly verification (Usul.ai + web search), cross-references factual claims |
| **Oracle** | Opus 4.6 via `claude -p --effort max` | Read, Glob, Grep, WebSearch, WebFetch | **Owner proxy.** Handles ALL human gate decisions. Deep reasoning on SPEC design, scholarly questions, disagreement arbitration. Covered by Max subscription — zero API cost. |

### The Oracle — True Autonomy via Owner Proxy

**Why Claude Chat can't be automated:** Claude Chat (web and desktop) has no programmatic API. You cannot send it a message and get a response without human interaction. There's no way around this.

**Why `claude -p --effort max` is the equivalent:** Claude Code's print mode provides the exact same Opus 4.6 model with the same extended thinking capabilities as Claude Chat. The key differences:
- `claude -p` is fully automatable (called via shell command)
- `claude -p` reads CLAUDE.md and project context automatically
- `claude -p` is covered by Max 20x subscription (zero additional API cost)
- `claude -p --effort max` enables maximum reasoning depth (same as Chat's extended thinking)
- `claude -p --output-format json` returns structured responses for programmatic processing

**How OpenClaw invokes the Oracle:**
```bash
# Oracle handles a human gate decision
claude -p --effort max --model opus --agent oracle \
  --output-format json --permission-mode default \
  "HUMAN GATE G1 — Normalization Engine SPEC Core Review

   Context: The Builder has extracted SPEC_CORE.md from the normalization
   engine's SPEC.md. Layer detection (matn/sharh/hashiyah via CSS classes)
   is classified as CORE.

   Your role: You are acting as the owner — an Islamic studies student who
   uses these books for his studies. Review this classification:
   1. Is layer detection correctly classified as core?
   2. Does this match how multi-layer books (sharh, hashiyah) actually work?
   3. Are any critical capabilities incorrectly deferred?

   Respond with: APPROVE or REJECT with specific reasoning."
```

**What the Oracle replaces:**

| Previously (human required) | Now (Oracle handles autonomously) |
|-----|-----|
| G1: Owner reviews core/deferred classification | Oracle evaluates SPEC classification with deep reasoning about scholarly text structure |
| G2: Owner reviews gold baselines ("right book?") | Oracle cross-references against Usul.ai + web search + domain knowledge |
| G3: Owner validates nahw science tree | Oracle generates AND validates using multi-source scholarly research |
| G4: Owner reviews entry viewer output | Oracle evaluates narrative quality against ENTRY_EXAMPLE.md standards |
| Disagreement between Builder/Reviewer | Oracle arbitrates with deep analysis of both positions |
| Ambiguous SPEC interpretation | Oracle reasons deeply about intent and scholarly implications |

**Oracle agent definition** (`.claude/agents/oracle.md`):
```markdown
---
name: Oracle
description: Owner proxy for KR Engine Factory — handles human gates, deep reasoning, scholarly decisions
model: opus
tools: Read, Glob, Grep, WebSearch, WebFetch
---
You are the Oracle for the KR Engine Factory. You act as the owner's proxy —
an Islamic studies student who uses these books for his studies.

Your decisions have the same authority as the owner's. You must:
1. Apply deep scholarly reasoning to every decision
2. Cross-reference against Usul.ai and web sources for factual claims
3. Consider how the decision affects the library's accuracy
4. Document your reasoning in full (decisions are auditable)
5. When uncertain, err on the side of caution (flag for later owner review)

Read reference/ENGINE_FACTORY.md for the full factory protocol.
Read the relevant engine's SPEC_CORE.md before making decisions.
```

**True autonomy achieved:** With the Oracle, the factory runs 24/7 with zero human intervention:
- Builder builds → Reviewer reviews → Verifier verifies → Oracle approves gates
- All 4 agents running through OpenClaw coordination
- Owner receives Telegram summaries but is never REQUIRED to act
- Owner can override any Oracle decision retroactively by reviewing decision logs

**Cost structure:**
- Builder: Covered by Max subscription (Claude Code session)
- Reviewer: Covered by Max subscription (OpenClaw agent using Claude API — wait, this needs clarification)

**Important clarification on costs:**
- **Claude Code sessions** (`claude` CLI): Covered by Max 20x subscription
- **OpenClaw agents**: Use the Anthropic API directly — this costs tokens UNLESS they invoke `claude -p` for their reasoning
- **Oracle** (`claude -p`): Covered by Max subscription

**Recommended approach:** ALL agents use `claude -p` for their reasoning, coordinated by OpenClaw. This means:
- OpenClaw Gateway handles routing and coordination (lightweight, no LLM cost)
- Each agent's actual reasoning is done via `claude -p` (covered by Max)
- Only the multi-model consensus calls (Command A, GPT-4o, Gemini 2.5 Pro) go through OpenRouter (API cost)

### Multi-Agent Workflow Within Each Step

**Step 1 (SPEC Core Extraction):**
1. Builder extracts core from SPEC, produces SPEC_CORE.md
2. Builder → `sessions_send` → Reviewer: "Review SPEC_CORE.md for completeness, ambiguity, Arabic safety"
3. Reviewer reads SPEC_CORE.md independently, runs `check_spec_quality.py`, checks contract compatibility
4. Reviewer replies with findings (APPROVE / REJECT with specific issues)
5. If REJECT: Builder fixes → re-sends for review (up to 5 ping-pong turns)
6. Builder → `sessions_spawn` → Verifier: "Independently verify contract compatibility with upstream/downstream"
7. Builder invokes Oracle for human gate G1: "Review core/deferred classification"
8. Oracle reasons deeply, cross-references scholarly sources, returns APPROVE/REJECT with reasoning
9. Reviewer AND Verifier AND Oracle must all APPROVE before Step 1 exits

**Step 2 (Research):**
1. Builder designs experiments and runs them
2. Builder → `sessions_send` → Reviewer: "Review experiment design and results"
3. Reviewer checks: Are the right fixtures used? Are the accuracy thresholds correctly applied? Are findings correctly translated to SPEC changes?
4. Builder → `sessions_spawn` → Verifier: "Independently replicate key experiments on different fixtures"
5. Verifier runs same LLM tasks on fixtures Builder didn't test → confirms or contradicts findings
6. All three must agree on findings before Step 2 exits

**Step 3 (Build) — Sub-step level review:**
1. Builder writes module N + tests
2. Builder → `sessions_send` → Reviewer: "Review module N against SPEC §4.X, check Arabic safety and D-023"
3. Reviewer reads code, checks:
   - Every SPEC rule in §4.X has corresponding code
   - Arabic text handling follows `.claude/skills/arabic-text/SKILL.md`
   - Metadata flows forward (D-023) — no field dropped
   - Type hints on all signatures, no `Any`
   - Error handling fails loud (no silent defaults)
4. Reviewer replies: APPROVE or REJECT with specific line-level issues
5. Builder → `sessions_spawn` → Verifier: "Write independent tests for SPEC §4.X without reading Builder's implementation"
6. Verifier writes tests from SPEC behavioral rules only → tests committed alongside Builder's tests
7. **Both test suites must pass against Builder's code.** If Verifier's tests fail, it means Builder misinterpreted the SPEC — this is the highest-value catch.
8. No module is committed without Reviewer APPROVE + Verifier tests passing

**Step 4 (Prove):**
1. Builder runs full 5a/5b/5c evaluation
2. Builder → `sessions_send` → Reviewer: "Review gold baselines against SPEC and source data"
3. Reviewer checks every gold baseline field: Is this the right author? Right genre? Right death date? Does the output match the SPEC's quality bar?
4. Builder → `sessions_spawn` → Verifier: "Scholarly verification of all gold baselines — Usul.ai + web search"
5. Verifier independently checks every factual claim in every gold baseline
6. Verifier produces `verification_log.json` with per-claim evidence
7. All three must agree + cross-engine regression passes before engine is marked COMPLETE

### Why GSD is available but not default

GSD's milestone/phase model adds abstraction over ENGINE_PROTOCOL. Since ENGINE_PROTOCOL already defines the 4-step process with precision, GSD's discuss→plan→execute cycle would re-discover decisions that ENGINE_FACTORY.md already pre-computes. The `/build-engine` command codifies ENGINE_PROTOCOL directly. However, GSD's `/gsd:verify-work` could supplement OpenClaw's verification as an additional quality layer if desired.

### Expanded Consensus Pool

The source engine used 2 models (Command A + Opus 4.6) at 92.3% "at-least-one-right." For engines 2-7, expand to **4 models for critical content decisions:**

| Model | Provider | Role |
|-------|----------|------|
| Command A (Cohere) | OpenRouter | Primary consensus member |
| Claude Opus 4.6 | Anthropic direct | Primary consensus member |
| GPT-4o | OpenRouter | Verification member |
| Gemini 2.5 Pro | OpenRouter | Verification member |

**Why 4 models:** LLM-dependent engines (atomization, excerpting, taxonomy, synthesis) make critical content decisions. A 4-model consensus catches errors that 2-model consensus misses. The cost increase (~2x per consensus call) is negligible given uncapped budget. The additional diversity (different training data, different biases) provides genuinely independent verification.

**When to use 4 vs 2 models:**
- **4-model consensus:** Genre classification, scholarly function classification, self-containment evaluation, taxonomy placement, synthesis grounding — any decision that would corrupt the knowledge base if wrong
- **2-model consensus:** Author name extraction (mostly extractive), structural type classification (mostly pattern-matching), death date extraction (mostly extractive)

### Additional Quality Tools

| Tool | Purpose | Value |
|------|---------|-------|
| **mypy --strict** | Type checking across all engine code | Catches type errors that tests miss. Every engine's code must pass mypy strict. |
| **pytest-cov** | Test coverage tracking | Enforces minimum 90% line coverage on core modules. No engine advances from Step 3 without meeting threshold. |
| **Usul.ai** | Scholarly claim verification | Cross-reference author attributions, death dates, genre classifications against this authoritative Islamic scholarly database. Already referenced in testing.md. |
| **Pre-commit hooks** | Automated quality enforcement | Run black, mypy, and relevant quality scripts before every commit. No commit bypasses quality checks. |

### GPU Utilization

The user's desktop GPU enables:
- **Local embedding models** (arabic-e5-base via sentence-transformers) for fast similarity checks during development — useful for deduplication, title matching, author name matching
- **Local inference for rapid iteration** during Step 3 development (Ollama with Arabic-capable models) — for quick feedback loops, NOT for final quality judgments
- **Fast test execution** — embedding-dependent tests run locally instead of hitting API

**Critical rule:** Local models are NEVER used for final quality judgments. All production consensus decisions use the cloud consensus pool. Local models are development acceleration tools only.

---

## Architecture Overview

```
USER runs /build-engine normalization
         │
         ▼
┌──────────────────────────────────────────────────────────────┐
│  OpenClaw Gateway (24/7)                                     │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  BUILDER (Claude Code, Opus 4.6, 1M context)        │    │
│  │  /build-engine command drives ENGINE_PROTOCOL        │    │
│  └──────────┬───────────────────────┬───────────────────┘    │
│             │ sessions_send          │ sessions_spawn         │
│             ▼                        ▼                        │
│  ┌──────────────────┐    ┌──────────────────────┐            │
│  │  REVIEWER         │    │  VERIFIER             │            │
│  │  Read-only access │    │  Independent tests    │            │
│  │  SPEC compliance  │    │  Scholarly verify     │            │
│  │  Arabic safety    │    │  Usul.ai + web search │            │
│  │  D-023 check      │    │  Experiment replicate │            │
│  │  Knowledge integ. │    │  Factual claims       │            │
│  └──────────────────┘    └──────────────────────┘            │
│             │                        │                        │
│             └────── ALL APPROVE ─────┘                        │
│                         │                                     │
│                    Step advances                              │
└──────────────────────────────────────────────────────────────┘
         │
    ┌────┴────┐────────┐────────┐
    ▼         ▼        ▼        ▼
 Step 1    Step 2   Step 3   Step 4
  SPEC    Research   Build    Prove
    │         │        │        │
    ▼         ▼        ▼        ▼
 Builder   Builder  Builder  Builder
 writes    runs     writes   runs
 SPEC_CORE exper.   code     eval
    │         │        │        │
    ▼         ▼        ▼        ▼
 Reviewer  Reviewer Reviewer Reviewer
 audits    checks   reviews  checks
 SPEC      design   each     gold
 quality   +results module   baselines
    │         │        │        │
    ▼         ▼        ▼        ▼
 Verifier  Verifier Verifier Verifier
 checks    replicates writes  scholarly
 contracts experiments indep.  verify
                     tests   (Usul.ai)
    │         │        │        │
    ▼         ▼        ▼        ▼
 ALL MUST   ALL MUST ALL MUST ALL MUST
 APPROVE    AGREE    PASS     APPROVE
    │         │        │        │
    ▼         ▼        ▼        ▼
 HUMAN     (auto)    mypy +  HUMAN
 GATE #1             cov≥90% GATE #2
                        │
                        ▼
                   Cross-Engine
                   Regression
```

**State lives in:**
- `ENGINE_FACTORY.md` — coarse state (which engine, which step, blockers)
- `engines/{engine}/CLAUDE.md` — engine-specific state (updated each session)
- `engines/{engine}/docs/HANDOFF_{date}.md` — fine-grained session state
- `NEXT.md` — always points to the current task

All committed to git. Any Claude session can reconstruct full state from these files.

---

## Quality Standards — Non-Negotiable

These quality standards apply to EVERY engine. They are not guidelines — they are hard gates that block advancement.

### Step 1 (SPEC) Exit Criteria
- `check_spec_quality.py` → **0 HIGH defects** in SPEC_CORE.md
- kr-integrity audit passes with **0 HIGH findings**
- Every §4.A rule has at least one **concrete testable example with real Arabic text**
- Contract compatibility verified with **both** upstream and downstream engines
- **Reviewer APPROVE** on SPEC_CORE.md (SPEC compliance, Arabic safety, completeness)
- **Verifier APPROVE** on contract compatibility (independent check)
- Owner has reviewed core/deferred classification (or 3-day timeout with extended verification)

### Step 2 (Research) Exit Criteria
- **Every** `[ASSUMPTION]` marker in SPEC_CORE is resolved or marked `[BUILD-PHASE VALIDATION]` with a specific test plan
- LLM reliability tested on **minimum 3 fixtures** per task (not 1-2)
- For engines with heavy LLM dependence (atomization, excerpting, taxonomy, synthesis): test on **ALL available fixtures**
- Results documented in `engines/{engine}/research/` with full reproducibility information
- SPEC_CORE.md updated with findings — no assumption left unaddressed
- **Reviewer APPROVE** on experiment design and interpretation of results
- **Verifier** has independently replicated at least 1 key experiment → results consistent

### Step 3 (Build) Exit Criteria
- All `pytest` tests pass (`python -m pytest engines/{engine}/tests/ -v --tb=short`)
- `verify_metadata_flow.py` shows **clean D-023 compliance** (no missing fields)
- `check_compliance.py` shows **full coverage** of core SPEC rules
- `mypy --strict` passes on all engine code
- `pytest-cov` shows **≥90% line coverage** on core modules
- Every function tested against **at least one real Arabic fixture** from `tests/fixtures/`
- Contract changes synced with neighbors via `run_pipeline.py`
- `session_quality_gate.py` passes
- **Reviewer APPROVE** on every module (SPEC compliance, Arabic safety, D-023, knowledge integrity)
- **Verifier's independent tests** pass against Builder's code (SPEC interpretation cross-check)

### Step 4 (Prove) Exit Criteria
- Full **5a/5b/5c evaluation** on ALL 8 test fixtures (not just core-format ones)
- 5b LLM-worker accuracy **≥90%** on every task
- Gold baselines created with **dual verification**: (a) cross-provider automated check, (b) owner sanity check
- **Cross-engine regression**: ALL previous engines' test suites pass after this engine's build
- Pipeline integration test passes from **source through this engine** (not just this engine + next stub)
- **Scholarly verification**: Usul.ai + web search cross-reference on author attributions and genre classifications in gold baselines
- LESSONS.md written with findings that feed forward
- All 4 quality scripts pass simultaneously

### Zero-Tolerance Rules
- **No fast-tracking.** Every engine gets the full 4-step treatment at full depth, regardless of SPEC maturity.
- **No session limits.** A step continues until its exit criteria are met, not until a session budget is exhausted.
- **No compressed steps.** Step 2 is never merged into Step 1. Each step is a separate, focused effort.
- **No skipping fixtures.** Step 4 tests ALL 8 fixtures, including edge cases (photos, multi-volume, owner notes).
- **No advancing with known defects.** If a quality gate fails, fix before proceeding.
- **No single-agent approval.** Every sub-step requires Reviewer APPROVE. No code is committed without independent review.
- **No skipping Verifier tests.** Verifier's independent tests are as authoritative as Builder's tests. Both must pass.

---

## Deliverables

### 1. `reference/ENGINE_FACTORY.md` — The Master Blueprint (~1000-1500 lines)

The single authoritative document that drives the factory. Contains:

**Section A: Engine Queue** — 6 engines with current step, quality state, blockers. No session estimates (they create pressure to rush).

**Section B: Per-Step Protocol** — Exact session protocol for each step type:
- Step 1 Protocol (11-step checklist — includes kr-integrity audit AND contract verification)
- Step 2 Protocol (10-step checklist — includes full fixture testing AND reproducibility documentation)
- Step 3 Protocol (9-step checklist — includes mypy strict AND coverage threshold AND real fixture testing)
- Step 4 Protocol (11-step checklist — includes cross-engine regression AND scholarly verification AND double-blind evaluation)

**Section C: Engine Briefs** — Pre-computed context for each engine:
- Current state (SPEC lines, defect count, existing code)
- Input contract (from upstream) and output contract (to downstream)
- LLM dependency level (none / light / heavy) and consensus model count (2 or 4)
- Shared components needed
- Known risks and blockers
- ENGINE_PROTOCOL engine-specific notes
- Full fixture list with expected behavior for this engine

**Section D: Quality Gates** — Automated checks at each step boundary:
```
Step 1 exit: check_spec_quality.py → 0 HIGH | kr-integrity → 0 HIGH | contract compat verified
Step 2 exit: All [ASSUMPTION] resolved on ≥3 fixtures | SPEC updated with findings
Step 3 exit: pytest pass | mypy strict | coverage ≥90% | metadata flow clean | compliance full
Step 4 exit: All 4 scripts pass | cross-engine regression | gold baselines + scholarly verification
```

**Section E: Cross-Engine Regression Protocol** — After each engine's Step 4:
- Run `python -m pytest engines/*/tests/ shared/*/tests/ -q` (ALL tests, ALL engines)
- Run `verify_metadata_flow.py --verbose` (full pipeline D-023 check)
- Run `run_pipeline.py` from source through this engine (real data, real contracts)
- Any failure blocks advancement to next engine

**Section F: Human Gate Schedule** — When owner reviews what, with clear notification mechanism

**Section G: Scholarly Verification Protocol** — How to cross-reference gold baselines against Usul.ai and web sources

**Section H: Multi-Model Consensus Configuration** — Which models for which decisions, how to add/remove models

### 2. `.claude/commands/build-engine.md` — Entry Point Command (~150-200 lines)

```
/build-engine normalization
/build-engine passaging --step 2        (resume at specific step)
/build-engine --status                  (show all engine progress)
```

The command:
1. Reads `reference/ENGINE_FACTORY.md` for the blueprint
2. Reads `engines/{engine}/CLAUDE.md` for current state
3. Reads `engines/{engine}/SPEC.md` (or `SPEC_CORE.md` if exists)
4. Reads the most recent `HANDOFF_{date}.md` if resuming
5. Determines current step by checking exit criteria (not assumptions)
6. Drives through the step's protocol checklist with **zero shortcuts**
7. Runs quality gates at step boundaries — **blocks on failure**
8. Pauses at human gates with clear instructions for the owner
9. Invokes relevant skills by name (arabic-text, consensus-pattern, knowledge-safety, etc.)
10. Runs cross-engine regression after Step 4
11. Writes detailed handoff at session end
12. Updates ENGINE_FACTORY.md status and NEXT.md

### 3. `.claude/commands/engine-handoff.md` — Session End Protocol (~80-100 lines)

Enforces clean session endings:
1. Writes `engines/{engine}/docs/HANDOFF_{date}.md` with:
   - What was built (modules, tests, findings)
   - What decisions were made (with reasoning)
   - What is next (specific task)
   - Known issues discovered but not fixed
   - Context that would be lost to compaction (Arabic handling specifics, enum values, thresholds)
   - Quality gate results from this session
2. Updates ENGINE_FACTORY.md status markers
3. Updates NEXT.md to point to the next action
4. Runs all 4 quality gate scripts
5. Runs mypy --strict on changed files
6. Commits with conventional format

### 4. `.claude/commands/engine-status.md` — Progress Dashboard (~60-80 lines)

Shows comprehensive quality state:
```
/engine-status

ENGINE FACTORY STATUS — Stage 1 Pipeline Build
═══════════════════════════════════════════════════════════════
                    Step  Tests  Coverage  SPEC Defects  mypy
✅ Source          DONE    503    94%       0 HIGH        PASS
🔨 Normalization  BUILD    47    87%       0 HIGH        PASS
⏳ Passaging      SPEC      0     —       25 HIGH          —
⬚  Atomization    WAIT      0     —        9 HIGH          —
⬚  Excerpting     WAIT      0     —        0 HIGH          —
⬚  Taxonomy       WAIT      0     —        0 HIGH        BLOCKED: nahw tree
⬚  Synthesis      WAIT      0     —        6 HIGH          —

Cross-engine regression: PASSING (503/503)
D-023 metadata flow: CLEAN
Budget spent: €32.50 (uncapped)
Consensus pool: Command A | Opus 4.6 | GPT-4o | Gemini 2.5 Pro
Agents: Builder ● | Reviewer ● | Verifier ● | Oracle ●
```

### 5. `scripts/engine_readiness.py` — Step Advancement Gate (~300-400 lines)

Programmatic, zero-tolerance check for step advancement:

**Step 1 → Step 2 readiness:**
- SPEC_CORE.md exists
- `check_spec_quality.py` → 0 HIGH defects
- Contract compatibility confirmed with upstream AND downstream
- Owner approval recorded (or 3-day timeout with `[OWNER REVIEW PENDING]` markers)

**Step 2 → Step 3 readiness:**
- All `[ASSUMPTION]` markers in SPEC_CORE are resolved
- Research results documented in `engines/{engine}/research/`
- SPEC_CORE updated with findings
- No unresolved `<70%` accuracy findings (would require redesign first)

**Step 3 → Step 4 readiness:**
- ALL pytest tests pass
- mypy --strict passes
- pytest-cov ≥ 90% on core modules
- verify_metadata_flow.py clean
- check_compliance.py full coverage
- Every core module tested with real Arabic fixture

**Step 4 → COMPLETE readiness:**
- All 4 quality scripts pass
- Cross-engine regression passes (ALL prior engine tests)
- Gold baselines exist with dual verification
- Pipeline integration test passes (source through this engine)
- Scholarly verification completed on gold baselines
- LESSONS.md written

### 6. `scripts/cross_engine_regression.py` — Regression Test Runner (~150-200 lines)

After each engine's Step 4:
```bash
python scripts/cross_engine_regression.py --through normalization
```
Runs:
- All test suites for completed engines
- Full D-023 metadata flow check
- Pipeline runner from source through specified engine
- Contract boundary validation at every junction
- Reports any regression introduced by the latest engine build

### 7. OpenClaw Multi-Agent Quality Setup

Configure OpenClaw Gateway with 3 agents for quality coordination:

**`~/.openclaw/openclaw.json`** — Gateway configuration:
```json5
{
  agents: {
    list: [
      {
        id: "builder",
        model: "anthropic/claude-opus-4-6",
        tools: { profile: "coding", allow: ["sessions_send", "sessions_spawn"] }
      },
      {
        id: "reviewer",
        model: "anthropic/claude-opus-4-6",
        tools: { profile: "coding", deny: ["apply_patch", "write"] }  // READ-ONLY
      },
      {
        id: "verifier",
        model: "anthropic/claude-opus-4-6",
        tools: { profile: "coding", allow: ["sessions_send", "exec", "browser"] }
      }
    ]
  },
  tools: {
    agentToAgent: { enabled: true, allow: ["builder", "reviewer", "verifier", "oracle"] },
    sessions: { visibility: "agent" }
  },
  session: { agentToAgent: { maxPingPongTurns: 5 } }
}
```

**Per-agent workspace setup:**
- `~/.openclaw/agents/builder/` — SOUL.md with ENGINE_PROTOCOL knowledge, access to all KR skills
- `~/.openclaw/agents/reviewer/` — SOUL.md with review checklist (SPEC compliance, Arabic safety, D-023, knowledge integrity), READ-ONLY tool access
- `~/.openclaw/agents/verifier/` — SOUL.md with scholarly verification protocol, Usul.ai instructions, independent test-writing methodology

**Git integration** (`.git/hooks/post-commit`):
```bash
#!/bin/bash
# Trigger Reviewer after engine code commits
if git diff --name-only HEAD~1 | grep -q "engines/"; then
  openclaw agent --agent reviewer \
    --message "Review latest commit to engine code. Check SPEC, Arabic safety, D-023." \
    --thinking high
fi
```

**Telegram notifications** — configured via OpenClaw channels for human gate alerts

**What this enables:**
- Builder writes code → Reviewer automatically reviews every commit
- Builder requests scholarly verification → Verifier independently checks via Usul.ai + web
- Verifier writes independent tests → Builder's code must pass both test suites
- Disagreements trigger ping-pong discussion (up to 5 turns) → resolved or escalated to human gate
- All agent interactions logged with `provenance.kind = "inter_session"` for auditability

### 8. Updates to existing files

- `NEXT.md` — Point to ENGINE_FACTORY.md as the starting point
- Each engine's `CLAUDE.md` — Add factory-compatible status section
- `STEERING.md` — Add reference to ENGINE_FACTORY.md
- `.pre-commit-config.yaml` (NEW) — black + mypy + quality scripts

---

## Per-Engine Strategy

**Note:** Session estimates below are MINIMUMS for orientation, not targets or budgets. Each step continues until its exit criteria are met, regardless of how many sessions it takes.

### Engine 2: Normalization (minimum ~8 sessions)

**Why it's first:** Direct downstream of source engine. No blockers.

**SPEC state:** Most mature (2,006 lines, 4 refinement passes). Core extraction is surgical — move §4.B to deferred, verify §4.A implementation-ready. DO NOT rewrite refined §4.A content.

**Core architecture:** Shamela HTML normalizer → layer detection (matn/sharh/hashiyah via CSS classes) → manifest.json + content.jsonl in universal format. Layer detection is CORE (without it, passaging can't align commentary to base text, and the entire downstream pipeline loses layer attribution).

**LLM dependency:** Light. Layer detection uses CSS class patterns (deterministic). Consensus model count: 2 (standard pair).

**Key risk:** Layer detection accuracy on multi-layer texts with inconsistent CSS markup. Step 2 MUST test on Ibn Aqil fixture (multi-layer sharh with 4 volumes).

**Fixtures to test (Step 4):** ALL 8, with special attention to:
- `ibn_aqil_alfiyyah` — multi-layer sharh, the core test case
- `waraqat_usul` — single-layer prose, must not falsely detect layers
- `html_export_minimal` — Shamela HTML structure
- `alfiyyah_versified` — versified text, tests edge cases

**Shared components needed:** Existing validation module (already built). No new shared components.

### Engine 3: Passaging (minimum ~8 sessions)

**SPEC state:** 25 HIGH defects (worst in repo). Step 1 needs substantive rewrite, not surgical extraction. This is the main effort — the actual building is simpler.

**Core architecture:** Two strategies only — prose (heading-based splitting) and commentary-with-layers. Existing 6 strategy variants in stubs MUST be pruned to core-only during Step 3. Target: 200-800 Arabic words per passage, preserving heading hierarchy and page boundaries.

**LLM dependency:** None to light. Text segmentation is primarily deterministic. Consensus model count: 2 if needed.

**Key risk:** The 25 HIGH SPEC defects are the main challenge. Some may reveal architectural issues requiring redesign, not just rewording.

**Critical constraint:** Step 3 cannot begin until normalization Step 3 is complete (passaging needs normalization's output format).

### Engine 4: Atomization (minimum ~10 sessions — HIGHEST RISK ENGINE)

**SPEC state:** 9 HIGH defects. Advanced features (fingerprinting, distribution analytics) must be removed from core.

**Core architecture:** Segment passages into non-overlapping atoms. Classify on 2 dimensions: structural type + scholarly function. **LLM does the primary work** — this is the first engine where LLM accuracy determines success.

**LLM dependency:** HEAVY. Scholarly function classification is the core task. Consensus model count: **4 (full pool)** for function classification.

**Key risk:** If LLM scholarly function classification accuracy < 85% on 4-model consensus, fundamental redesign is needed. Step 2 research is CRITICAL and should test on ALL fixtures, not just 3.

**Step 2 research protocol (expanded):**
1. Test structural type classification on all 8 fixtures → expect ≥90% (mostly pattern-based)
2. Test scholarly function classification on all 8 fixtures → need ≥85% with 4-model consensus
3. If 85-94%: proceed with enhanced verification layer (cross-check each classification with contextual analysis)
4. If 70-84%: add human gate for low-confidence classifications + fallback to broader categories
5. If <70%: STOP. Redesign approach before building. Options: simplified taxonomy, human-assisted classification, rule-based pre-filtering

### Engine 5: Excerpting (minimum ~8 sessions)

**SPEC state:** Cleanest (0 HIGH defects). Surgical extraction.

**Core architecture:** Group atoms into self-contained excerpts. Evaluate self-containment ("can reader understand without context?"). **Highest-risk LLM task in pipeline** (T-4: Context Loss — the threat where pipeline processing strips context that makes text meaningful).

**LLM dependency:** HEAVY for self-containment evaluation. Consensus model count: **4 (full pool)**.

**Key risk:** Self-containment evaluation reliability. If LLMs can't reliably judge "can a reader understand this alone?", the SPEC must be redesigned toward larger excerpts with guaranteed surrounding context rather than precise self-containment judgments.

**Step 2 research protocol (expanded):**
- Test self-containment judgment on excerpts of varying sizes (3 atoms, 5 atoms, 10 atoms)
- Test on commentary text (harder — references base text) AND prose (easier — mostly self-contained)
- If accuracy varies by excerpt size, the SPEC should mandate minimum sizes per text type
- If accuracy varies by text layer, different strategies needed for matn vs sharh vs hashiyah

### Engine 6: Taxonomy (minimum ~8 sessions — HAS BLOCKER)

**SPEC state:** 0 HIGH defects. Clean.

**BLOCKER:** Needs validated science tree before Step 3. The 5 existing tree.yaml files in `library/sciences/` were created without owner validation. **The nahw tree must be generated via multi-source AI research and owner-validated** before taxonomy Step 3.

**Blocker mitigation timeline:** Start nahw tree generation during atomization build (engine 4 Step 3). Use multi-source AI research to generate the tree structure (cross-referencing standard curricula, textbook tables of contents, established nahw reference works). Present to owner for experiential validation ("does this match how I learned nahw?"). This removes the blocker before taxonomy reaches Step 3.

**LLM dependency:** Moderate. Two-stage placement (LLM proposes + rules refine). Consensus model count: **4 (full pool)** for ambiguous placements, 2 for clear placements.

### Engine 7: Synthesis (minimum ~9 sessions)

**SPEC state:** 6 HIGH defects. Moderate rewrite needed.

**Core architecture:** Compile placed excerpts into scholarly entries with temporal ordering, school attribution, grounding traceability. Cross-provider verification (different model for generation vs. verification). **Must build entry viewer** (`scripts/render_entry.py`) at Step 4.

**LLM dependency:** HEAVY. Narrative generation is the core task. Consensus model count: **4 (full pool)** for grounding verification. Cross-provider architecture: one provider generates, a DIFFERENT provider verifies.

**Quality bar:** Structured narrative, NOT flat bullets. The full scholarly narrative from ENTRY_EXAMPLE.md (intellectual genealogy, "why scholars disagreed") can start basic but flat compilations are **unacceptable** even for core v0.0.1. Every claim tagged with grounding_type (source_grounded | metadata_derived | analytical).

**Step 4 special requirement:** Owner reviews entry viewer output (HUMAN GATE). This is the most important quality judgment in the entire pipeline — "does this read like a scholarly reference I would trust?"

---

## Parallelization Strategy

### Principle: Overlap for thoroughness, not speed

Pipeline ordering requires sequential engine building. The allowed overlap (Steps 1-2 of engine N+1 during Steps 3-4 of engine N) is not for speed — it's because early SPEC work and research on the next engine IMPROVES quality by giving more time for deep thinking before building.

### What overlaps and what doesn't

| Overlapping (safe) | Sequential (mandatory) |
|---------------------|----------------------|
| Engine N+1 Step 1 during Engine N Step 3-4 | Engine N+1 Step 3 waits for Engine N Step 3 completion |
| Phase D evaluation alongside any engine work | Cross-engine regression waits for Step 4 completion |
| Nahw tree generation alongside engines 4-5 | Step 4 gold baselines wait for Step 3 code freeze |
| Codex research experiments alongside build | Any contract change cascades to all affected engines |

### What the 20 conversations are used for

- **3 slots for engine building** (Builder + Reviewer + Verifier agents via OpenClaw)
- **1-2 slots for next engine** (early Steps 1-2 overlapping current engine Steps 3-4)
- **1 slot for Phase D evaluation** (remaining Sessions B, C, D, Layer 4)
- **1 slot for Codex research** (Step 2 experiments)
- **1 slot for nahw tree research** (starting during engine 4 work)
- **12+ slots reserved** — available for deep research, additional verification agents, or when an engine needs multiple research threads explored simultaneously

### 24/7 Operation Model

With the PC running continuously:
- Sessions run uninterrupted through full steps (no artificial session breaks for "end of day")
- Opus 4.6 with 1M context can hold an entire step's work without compaction
- Human gates trigger OpenClaw notifications → owner reviews when available → session resumes
- Background regression tests can run in separate terminal while build continues
- No time pressure — a session runs until the step's exit criteria are met

---

## Human Gate Schedule

### Mandatory Gates

| Gate | When | What Owner Does | Notification |
|------|------|-----------------|-------------|
| G1 x6 | Each engine Step 1 | Review core/deferred classification: "Is this what matters for my books?" | OpenClaw → Telegram |
| G2 x6 | Each engine Step 4 | Review gold baselines: "Is this the right book? Right author? Does this look useful?" | OpenClaw → Telegram |
| G3 | Before Taxonomy Step 3 | Validate nahw science tree: "Does this match how I learned nahw?" | OpenClaw → Telegram |
| G4 | Synthesis Step 4 | Review entry viewer output: "Does this read like a reference I would trust?" | OpenClaw → Telegram |

### What happens when owner is unavailable

Per ENGINE_PROTOCOL, after 3 days without response, Claude proceeds — BUT with additional safeguards:
1. Decisions marked `[OWNER REVIEW PENDING]`
2. **Extended multi-model verification** (4-model consensus on the pending decisions)
3. **Scholarly verification** via Usul.ai + web search for factual claims
4. Owner can review retroactively at any point — if they disagree, roll back and redo

### Owner time commitment

Total: **~8-10 hours** across all 6 engines, spread over the full build period.
- G1 reviews: ~20 min each × 6 = ~2 hours
- G2 reviews: ~30 min each × 6 = ~3 hours
- G3 (nahw tree): ~1 hour
- G4 (entry viewer): ~1 hour
- Ad-hoc questions: ~1-2 hours total

---

## Cross-Engine Regression Protocol

This is the quality layer that prevents engine N from breaking engine N-1.

### After each engine's Step 4 completion:

```bash
# 1. Run ALL tests across ALL completed engines
python -m pytest engines/*/tests/ shared/*/tests/ -v --tb=short

# 2. Verify D-023 metadata flow across full pipeline
python scripts/verify_metadata_flow.py --verbose

# 3. Run pipeline from source through this engine with real data
python scripts/run_pipeline.py --through {engine} --fixture html_export_minimal

# 4. Check contract compatibility at every boundary
python scripts/engine_readiness.py --check-contracts --all

# 5. Run cross-engine regression script
python scripts/cross_engine_regression.py --through {engine}
```

### If regression is found:

1. Identify which engine introduced the regression
2. Fix in the causing engine (not the detecting engine)
3. Re-run full regression suite
4. Document the regression and fix in LESSONS.md
5. Update SPEC if the regression reveals a design flaw

**No engine advances to "COMPLETE" until cross-engine regression passes.**

---

## Scholarly Verification Protocol

For gold baselines (Step 4) and any claim verification:

1. **Usul.ai cross-reference** — Check author name, death date, primary science, major works against Usul.ai's database. Flag any discrepancy for investigation.
2. **Web search verification** — For each author attribution, search for `"{book_title}" "{author_name}"` and verify the attribution appears in reputable sources.
3. **Genre classification check** — Verify genre matches the book's actual content by checking descriptions from scholarly databases.
4. **Death date verification** — Cross-reference death dates (Hijri and Gregorian) against multiple sources.
5. **Document all findings** in `engines/{engine}/tests/gold_baselines/verification_log.json`

This protocol catches the silent errors that automated tests cannot: wrong author attributed, wrong genre classified, wrong death date inferred.

---

## Implementation Order

1. **Set up OpenClaw Gateway with 3 agents** — `~/.openclaw/openclaw.json` with builder/reviewer/verifier roles, `agentToAgent` enabled, per-agent SOUL.md files with KR domain knowledge. This is the foundation — all subsequent work runs through the multi-agent quality loop.

2. **Create `reference/ENGINE_FACTORY.md`** — The master blueprint with all sections (A through H). Must include multi-agent review protocols for each step, expanded quality standards, consensus configuration, and scholarly verification protocol.

3. **Create `.claude/commands/build-engine.md`** — Entry point command. Integrates with OpenClaw: Builder drives ENGINE_PROTOCOL, sends review requests to Reviewer, spawns verification tasks on Verifier.

4. **Create `.claude/commands/engine-handoff.md`** — Session end protocol.

5. **Create `.claude/commands/engine-status.md`** — Progress dashboard.

6. **Create `scripts/engine_readiness.py`** — Step advancement gate. Checks include: Reviewer APPROVE status, Verifier tests passing, all automated quality gates.

7. **Create `scripts/cross_engine_regression.py`** — Regression test runner.

8. **Create `.pre-commit-config.yaml`** — Pre-commit hooks for black + mypy + quality scripts.

9. **Set up git hooks for OpenClaw** — `.git/hooks/post-commit` triggers Reviewer on engine code changes.

10. **Set up Telegram notifications** — OpenClaw channel integration for human gate alerts.

11. **Update `NEXT.md`** — Point to ENGINE_FACTORY.md and `/build-engine normalization`.

12. **Update each engine's `CLAUDE.md`** — Add factory-compatible status section.

13. **Create `.claude/agents/oracle.md`** — Oracle agent definition with owner proxy prompt, scholarly reasoning instructions, and decision audit requirements.

14. **Test the factory** — Full 4-agent dry run on normalization Step 1: Builder extracts SPEC_CORE → Reviewer reviews → Verifier checks contracts → Oracle approves human gate → all four must agree.

### Critical files to create
- `~/.openclaw/openclaw.json` (NEW — gateway config with 4 agents: builder, reviewer, verifier, oracle)
- `~/.openclaw/agents/builder/SOUL.md` (NEW — ENGINE_PROTOCOL knowledge + KR skills)
- `~/.openclaw/agents/reviewer/SOUL.md` (NEW — review checklist: SPEC, Arabic safety, D-023, knowledge integrity)
- `~/.openclaw/agents/verifier/SOUL.md` (NEW — scholarly verification protocol, independent test methodology)
- `.claude/agents/oracle.md` (NEW — owner proxy agent: deep reasoning, human gate decisions, scholarly expertise)
- `reference/ENGINE_FACTORY.md` (NEW — ~1000-1500 lines)
- `.claude/commands/build-engine.md` (NEW — ~150-200 lines)
- `.claude/commands/engine-handoff.md` (NEW — ~80-100 lines)
- `.claude/commands/engine-status.md` (NEW — ~60-80 lines)
- `scripts/engine_readiness.py` (NEW — ~300-400 lines)
- `scripts/cross_engine_regression.py` (NEW — ~150-200 lines)
- `.pre-commit-config.yaml` (NEW — ~30-50 lines)
- `.git/hooks/post-commit` (NEW — triggers Reviewer on engine code commits)

### Critical files to update
- `NEXT.md` (UPDATE — point to factory)
- `engines/*/CLAUDE.md` x6 (UPDATE — add factory status sections)
- `STEERING.md` (UPDATE — reference ENGINE_FACTORY.md)

### Existing files to reuse (not modify)
- `skills/shared/ENGINE_PROTOCOL.md` — The authoritative process (factory codifies this)
- `scripts/check_spec_quality.py` — SPEC defect scanner
- `scripts/check_compliance.py` — Code-to-SPEC compliance
- `scripts/verify_metadata_flow.py` — D-023 enforcement
- `scripts/session_quality_gate.py` — Pre-commit gate
- `.claude/skills/*/SKILL.md` — All 9 KR skills
- `reference/CORE_CONTRACT_CLASSIFICATION.md` — Core vs deferred models
- `reference/TRACER_FINDINGS.md` — Boundary validation baseline
- `reference/TESTING_FRAMEWORK.md` — Test architecture

---

## Verification of the Factory Itself

Before running on normalization, verify:

1. **ENGINE_FACTORY.md completeness**
   - Every engine has a brief with ALL fields populated
   - Every step has a complete protocol checklist (no shortcuts)
   - Quality gate commands are correct and runnable
   - Human gate schedule matches ENGINE_PROTOCOL
   - Scholarly verification protocol is concrete and actionable
   - Cross-engine regression protocol has specific commands

2. **`/build-engine` command functionality**
   - Dry run: `/build-engine normalization` correctly identifies Step 1 as current
   - Reads ENGINE_FACTORY.md, engine CLAUDE.md, and SPEC.md
   - Generates correct session protocol for Step 1
   - Invokes skills by name (not relying on auto-triggering)

3. **Quality gate enforcement**
   - `engine_readiness.py` returns NOT_READY for normalization Step 2 (SPEC_CORE doesn't exist yet)
   - `engine_readiness.py` returns NOT_READY for passaging Step 3 (normalization not complete)
   - `engine_readiness.py` returns READY for normalization Step 1 (source engine complete)
   - Quality gates are blocking, not advisory

4. **Cross-engine regression baseline**
   - `cross_engine_regression.py --through source` passes (source engine is the baseline)
   - All 503 source engine tests pass
   - D-023 metadata flow is clean through source

5. **OpenClaw multi-agent coordination**
   - Gateway starts with 3 agents (builder, reviewer, verifier)
   - `sessions_send` from builder to reviewer delivers message and gets response
   - `sessions_spawn` from builder to verifier creates independent task
   - Reviewer can REJECT work (Builder receives rejection and must address it)
   - Telegram notification fires when human gate is reached
   - Git post-commit hook triggers Reviewer on engine code changes

6. **Multi-agent dry run (normalization Step 1)**
   - Builder extracts a small section of SPEC_CORE
   - Builder sends to Reviewer for review → Reviewer responds with findings
   - Builder spawns Verifier to check contract compatibility → Verifier responds
   - All three agree → sub-step advances
   - Disagreement triggers ping-pong discussion → resolution or escalation

7. **Pre-commit hooks**
   - `black` formats on commit
   - `mypy --strict` runs on changed engine files
   - Quality scripts run on relevant changes

### Success criteria for the full factory

- All 6 engines reach Step 4 COMPLETE with ALL exit criteria satisfied
- Cross-engine regression passes from source through synthesis
- `verify_metadata_flow.py` shows clean D-023 compliance across the FULL pipeline
- `run_pipeline.py` produces a knowledge entry from Shamela HTML → source → ... → synthesis
- Owner has approved all gold baselines
- Scholarly verification completed on all gold baselines with no unresolved discrepancies
- mypy --strict passes across ALL engine code
- pytest-cov ≥90% on ALL core modules
- Each engine has LESSONS.md with forward-looking insights
- Backward lesson reviews completed after engines 2, 4, 6
- No known defects in any SPEC_CORE.md (0 HIGH across all engines)
- **Every module has Reviewer APPROVE in audit trail**
- **Every engine has Verifier's independent tests passing alongside Builder's tests**
- **Every gold baseline has Verifier's scholarly verification log**
