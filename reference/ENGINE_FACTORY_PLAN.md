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
| **Oracle** | Opus 4.6 via `claude -p --effort max` | Read, Glob, Grep, WebSearch, WebFetch | **Claude Chat equivalent.** Performs the same deep domain reasoning that Claude Chat does in the current workflow — web research, cross-referencing sources, evaluating scholarly claims. NOT an "owner proxy" — it's the automated version of what the owner already delegates to Claude Chat. Reads the Decision Playbook for accumulated project knowledge. Covered by Max subscription — zero API cost. |

### The Oracle — Claude Chat Equivalent via CLI

**What the Oracle actually is:** During source engine development, the owner never personally evaluated whether an author attribution was correct or a genre classification was right. Instead, the owner would come to Claude Chat, and Claude Chat would do web searches, cross-reference sources, read extraction data, and make the call. The owner would confirm the result made sense. The "domain expertise" was Claude Chat doing research and reasoning, with the owner as a sanity check.

The Oracle replicates this exact workflow programmatically. It's NOT "AI pretending to be the owner." It's "AI doing what Claude Chat already does, without the owner having to copy-paste between windows."

**Why `claude -p --effort max` works:** Claude Code's print mode provides the same Opus 4.6 model with the same extended thinking. Key properties:
- `claude -p` is fully automatable (called via shell command)
- `claude -p` reads CLAUDE.md and project context automatically
- `claude -p` is covered by Max 20x subscription (zero additional API cost)
- `claude -p --effort max` enables maximum reasoning depth
- `claude -p --output-format json` returns structured responses for programmatic processing

**The context gap and how to close it:** Claude Chat has accumulated memory across dozens of sessions — every lesson learned, every bug pattern, every domain correction. A `claude -p` call starts fresh. The solution is the **Decision Playbook** (`reference/DECISION_PLAYBOOK.md`), a document that captures every heuristic and pattern Claude Chat currently carries:

- Known bug patterns (tahqiq-note ML=true bias, death date hallucination, compiler-as-muhaqiq)
- Domain rules (Shamela-ecosystem sources count as one, "traditional" not "definitive" for attribution)
- Evaluation heuristics (when to trust consensus, when to override, what "flagged" really means)
- Arabic text handling patterns (diacritics, NFC normalization, punctuation in nasab chains)
- Scholarly verification sources and their reliability hierarchy

With the Decision Playbook + SPEC + engine context injected, the Oracle handles ~90% of what Claude Chat handles. The remaining ~10% are cases where the answer depends on obscure cross-session precedents.

**Three-tier gate model:**

| Tier | Who | When | Example |
|------|-----|------|---------|
| **Oracle (automated)** | `claude -p --effort max` | Most gates — factual verification, SPEC compliance, scholarly cross-referencing | "Is this author attribution correct?" → Oracle does web search, checks Usul.ai, cross-references |
| **Owner (sanity check)** | Rayane via Telegram notification | Quick "does this look right?" reviews, high-level direction | "Does this core/deferred classification match what you imagined?" |
| **Claude Chat (escalation)** | Rayane opens Claude Chat manually | Hard 10% — ambiguous cases, novel patterns, decisions requiring deep cross-session context | "This book has a structure we've never seen before — is it a compilation or a commentary?" |

**Oracle invocation:**
```bash
# Oracle handles a human gate decision
claude -p --effort max --model opus --agent oracle \
  --output-format json --permission-mode default \
  "HUMAN GATE G2 — Normalization Engine Gold Baseline Review

   Context: [SPEC_CORE.md excerpt + relevant test output injected here]

   Decision Playbook loaded from: reference/DECISION_PLAYBOOK.md
   Known patterns relevant to this gate: [auto-extracted from playbook]

   Task: Verify gold baseline for ibn_aqil_alfiyyah fixture.
   1. Is the author attribution correct? (Cross-reference via web search)
   2. Is the genre classification correct?
   3. Does the layer detection output match expected multi-layer structure?
   4. Are there any patterns from DECISION_PLAYBOOK that apply?

   Respond with: APPROVE, REJECT (with specific issues), or ESCALATE (with reasoning for why this needs Claude Chat)."
```

**Critical design choice — ESCALATE option:** The Oracle can recognize when it's out of its depth and explicitly escalate to Claude Chat. This prevents the failure mode where an LLM confidently approves something wrong. The Oracle should ESCALATE when:
- Confidence is below a threshold on a factual claim
- The pattern doesn't match anything in the Decision Playbook
- Two sources contradict each other and resolution requires domain judgment
- The decision would set a precedent not covered by existing rules

**What the Oracle replaces vs. what it doesn't:**

| Oracle handles autonomously | Owner sanity-checks | Escalate to Claude Chat |
|-----|-----|-----|
| Author attribution verification (web search + Usul.ai) | "Does this core/deferred split look right for my studies?" | Novel book structures not covered by Decision Playbook |
| Genre classification verification | "Does this entry read like a reference I would trust?" | Contradictory sources requiring experiential judgment |
| Death date cross-referencing | High-level direction on priorities | Patterns that might indicate a new systematic bug |
| SPEC compliance checking | | Disagreements the Oracle can't resolve |
| Scholarly source verification | | |

**Oracle agent definition** (`.claude/agents/oracle.md`):
```markdown
---
name: Oracle
description: Domain reasoning agent for KR Engine Factory — handles scholarly verification, factual cross-referencing, and gate decisions. Claude Chat equivalent via CLI.
model: opus
tools: Read, Glob, Grep, WebSearch, WebFetch
---
You are the Oracle for the KR Engine Factory. You perform the same role that
Claude Chat performs in the current manual workflow: deep domain reasoning,
web research, scholarly verification, and evidence-based decision making.

You are NOT pretending to be the owner. You are the research and reasoning
layer that the owner relies on for domain decisions.

Your protocol:
1. Read the Decision Playbook (reference/DECISION_PLAYBOOK.md) for accumulated project knowledge
2. Read the relevant engine's SPEC_CORE.md before making decisions
3. Cross-reference factual claims against web sources and Usul.ai
4. Apply known patterns from the Decision Playbook
5. Document your reasoning in full (all decisions are auditable)
6. When uncertain or when the situation doesn't match known patterns,
   respond with ESCALATE and explain why this needs Claude Chat review

The owner will sanity-check your decisions. If you're wrong, that becomes
a new entry in the Decision Playbook for future reference.
```

**Cost structure (all covered by Max 20x subscription):**
- Builder: Claude Code interactive session
- Reviewer: Claude Code subagent (read-only tools)
- Verifier: Claude Code subagent (read + exec for tests)
- Oracle: `claude -p --effort max` invoked by orchestration script
- Only multi-model consensus calls (Command A, GPT-4o) go through OpenRouter (API cost)

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

**Section F: Human Gate Schedule** — Three-tier gate model (Oracle automated / Owner sanity-check / Claude Chat escalation), with Telegram notification for Tier 2

**Section G: Scholarly Verification Protocol** — How Oracle cross-references gold baselines against Usul.ai and web sources

**Section H: Multi-Model Consensus Configuration** — Which models for which decisions, how to add/remove models

**Section I: Decision Playbook Reference** — Pointer to `reference/DECISION_PLAYBOOK.md`, protocol for updating it after each engine build

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

### 7. Multi-Agent Quality Setup — Two Architecture Options

The Builder/Reviewer/Verifier/Oracle roles can be implemented through two paths. Both achieve the same quality goal (independent review of every module). Choose based on setup complexity vs. feature richness.

#### Option A: Claude Code Native (Recommended for v1)

Uses Claude Code's built-in subagents and Agent Teams. Simpler setup, fully covered by Max subscription, no external infrastructure.

**Reviewer subagent** (`.claude/agents/reviewer.md`):
```markdown
---
name: reviewer
description: Reviews engine code against SPEC for compliance, Arabic safety, D-023 metadata flow, and knowledge integrity. Use for every module before commit.
model: opus
tools: Read, Grep, Glob
---
You are the KR Engine Reviewer. You review code against SPEC_CORE.md.

Checklist for every review:
1. Every SPEC rule in the relevant section has corresponding code
2. Arabic text handling follows NFC normalization, diacritics preserved
3. Metadata flows forward (D-023) — no field dropped
4. Error handling fails loud — no silent defaults
5. Type hints on all signatures, no `Any`
6. Knowledge integrity — check against DECISION_PLAYBOOK.md patterns

Respond: APPROVE or REJECT with specific file:line issues.
```

**Verifier subagent** (`.claude/agents/verifier.md`):
```markdown
---
name: verifier
description: Writes independent tests from SPEC without seeing Builder's implementation. Use after each module is built.
model: opus
tools: Read, Grep, Glob, Bash
---
You are the KR Engine Verifier. You write tests from SPEC behavioral rules ONLY.

Protocol:
1. Read SPEC_CORE.md for the relevant section
2. DO NOT read the Builder's implementation code
3. Write tests that verify SPEC behavior using only the public API
4. Run your tests against the Builder's code
5. If your tests fail, it means the Builder misinterpreted the SPEC

This is the highest-value quality check in the factory.
```

**Orchestration** via a simple bash/Python script (`scripts/engine_orchestrator.py`):
```bash
# Pseudocode — deterministic, no LLM deciding flow
for each module in SPEC_CORE:
    builder builds module + tests
    reviewer subagent reviews → APPROVE/REJECT
    if REJECT: builder fixes, re-review (max 3 rounds)
    verifier subagent writes independent tests
    run both test suites
    if all pass: commit
    else: builder fixes

# At step boundaries:
run quality gates (check_spec_quality.py, etc.)
invoke oracle for human gates (claude -p --effort max)
notify owner via Telegram for sanity check
```

**Advantages:** Zero external infrastructure. All covered by Max. No TOS concerns. Native Claude Code context management. Subagents can be upgraded to Agent Teams if inter-agent communication is needed.

**Limitation:** Subagents can't spawn other subagents. Orchestration must be driven by the main session or an external script.

#### Option B: OpenClaw + Lobster (Full autonomy)

Uses OpenClaw Gateway for multi-agent coordination with Lobster for deterministic workflow orchestration. More infrastructure, but supports true 24/7 autonomous operation.

**Important: Use Lobster for orchestration, not `sessions_spawn`.** `sessions_spawn` is non-deterministic (the LLM decides when to spawn children). Lobster provides deterministic YAML-driven pipelines with approval gates and resume tokens. The Builder→Reviewer→Verifier flow should be a Lobster workflow, not an LLM decision.

**`~/.openclaw/openclaw.json`** — Gateway configuration:
```json5
{
  agents: {
    list: [
      {
        id: "builder",
        model: "anthropic/claude-opus-4-6",
        tools: { profile: "coding", allow: ["sessions_send", "lobster"] }
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
  session: { agentToAgent: { maxPingPongTurns: 5 } },
  plugins: { entries: { "llm-task": { enabled: true } } }
}
```

**Lobster workflow** (`workflows/engine-module-build.lobster`):
```yaml
name: engine-module-build
args:
  module: {}
  spec_section: {}
steps:
  - id: build
    command: >
      openclaw.invoke --tool llm-task --action json
      --args-json '{"prompt": "Build module ${module} per SPEC ${spec_section}"}'
  - id: review
    command: >
      openclaw.invoke --agent reviewer --tool sessions_send
      --args-json '{"message": "Review module ${module} against SPEC ${spec_section}"}'
  - id: review_gate
    approval: "Reviewer approved? Check review output."
    condition: $review.json.verdict == "APPROVE"
  - id: verify
    command: >
      openclaw.invoke --agent verifier --tool sessions_send
      --args-json '{"message": "Write independent tests for SPEC ${spec_section}"}'
  - id: test
    command: python -m pytest engines/${engine}/tests/ -v
  - id: commit
    command: git add -A && git commit -m "feat(${engine}): implement ${module}"
    approval: "All tests pass. Commit?"
```

**Known issue:** There is a reported bug where `agentToAgent.enabled: true` breaks `sessions_spawn`. Since we use Lobster instead of `sessions_spawn`, this should not affect us, but verify during setup.

**Per-agent workspace setup:**
- `~/.openclaw/agents/builder/` — SOUL.md with ENGINE_PROTOCOL knowledge, access to all KR skills
- `~/.openclaw/agents/reviewer/` — SOUL.md with review checklist, READ-ONLY tool access
- `~/.openclaw/agents/verifier/` — SOUL.md with scholarly verification protocol, independent test methodology

**Telegram notifications** — configured via OpenClaw channels for Tier 2 owner sanity checks

**Advantages:** True 24/7 autonomous operation. Lobster handles deterministic orchestration. OpenClaw handles agent isolation and communication. Full audit trail via `provenance.kind = "inter_session"`.

**Limitation:** More infrastructure to set up and maintain. OpenClaw is young (launched January 2026) with known bugs. TOS situation around subscription tokens needs monitoring.

#### Recommendation

**Start with Option A** (Claude Code native). It's simpler, fully supported, and gets you the highest-value quality measure (independent Reviewer and Verifier) with zero infrastructure overhead. Graduate to Option B only if:
- You want true 24/7 unattended operation (Option A needs someone to kick off each session)
- You need more than 3 agents working in parallel
- The Lobster workflow model proves valuable for your specific patterns

### 8. Decision Playbook — `reference/DECISION_PLAYBOOK.md` (NEW — Critical for Oracle)

The Decision Playbook captures every heuristic, pattern, and domain rule that Claude Chat has accumulated across the source engine build. Without this document, the Oracle starts from zero on every invocation.

**Contents (seeded from source engine experience):**

```markdown
# Decision Playbook — خزانة ريان

## Known Bug Patterns
- Tahqiq-note ML=true bias: Opus systematically misclassifies editorial apparatus as commentary layers
- Death date hallucination: Opus infers specific dates 2-6 years off for modern scholars; CA fabricates years from century designations
- Compiler-as-muhaqiq: Shamela lists source authors in author_raw while placing actual compiler in muhaqiq_raw
- Genre enum silent fallback: validate_enum_value falls back to "other" without logging

## Domain Rules
- Shamela-ecosystem sources (shamela.ws, ketabonline.com, turath.io, waqfeya.net) count collectively as ONE source for VERIFIED threshold
- "Traditional" (not "definitive") is the correct default attribution status per SPEC §4.A.4
- "Flagged" means genuinely untrustworthy, not just incomplete metadata
- Classical primary text with unknown muhaqiq should be "verified" with absence noted

## Scholarly Verification Sources (reliability hierarchy)
1. ar.wikipedia.org — most reliable for well-known classical works
2. archive.org — good for edition verification
3. shamela.ws — good for cross-referencing but counts as Shamela ecosystem
4. noor-book.com, hindawi.org — supplementary
5. tarajm.com — biographical data

## Arabic Text Handling
- Diacritics must be preserved exactly
- NFC normalization only
- Arabic commas in nasab chains cause silent failures — handle explicitly
- Hash computation must precede dedup, which must precede freeze

## Confidence Calibration
- result.json author confidence is always 1.0 (engine bug) — real confidence from llm_responses
- consensus.agreed=true does not check is_multi_layer — must compare manually
- Scholar canonical IDs are not consistent across books (isolated temporary libraries)

## Evaluation Heuristics
- 5-verdict scale: VERIFIED / PLAUSIBLE / UNVERIFIABLE / FLAG / ESCALATE
- web_fetch required for framework-VERIFY books; search snippets sufficient for famous works only
- When one model provides data and the other abstains, treat the data as higher-risk
```

**Maintenance:** After each engine's build, add new patterns discovered during that engine's development. The Decision Playbook grows with each engine — it's the institutional memory of the factory.

### 9. Updates to existing files

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

### Three-Tier Gate Model

During source engine development, every "human gate" was actually handled by Claude Chat — the owner would bring the question to Claude Chat, Claude Chat would research and reason, and the owner would confirm "looks good." The factory formalizes this into three tiers:

**Tier 1 — Oracle (automated, no human needed):**
The Oracle (`claude -p --effort max`) handles the substantive domain reasoning that Claude Chat previously handled. It reads the Decision Playbook, does web research, cross-references sources, and makes evidence-based decisions. Most gates are handled here.

**Tier 2 — Owner sanity check (Telegram notification, ~5 min):**
The owner receives a summary of the Oracle's reasoning and confirms "does this look right?" or "is this what you imagined?" The owner is NOT expected to evaluate whether an author attribution is correct — the Oracle already did that. The owner evaluates whether the overall direction matches their vision for the library.

**Tier 3 — Claude Chat escalation (manual, ~30 min):**
For the ~10% of cases where the Oracle recognizes it's out of its depth — novel patterns, contradictory sources, decisions that would set new precedents — the system pauses and the owner brings the question to Claude Chat. Claude Chat has accumulated memory and cross-session context that `claude -p` lacks.

### Gate Schedule

| Gate | When | Tier 1 (Oracle) | Tier 2 (Owner) | Tier 3 (Claude Chat) |
|------|------|-----------------|----------------|---------------------|
| G1 x6 | Each engine Step 1 | Oracle evaluates SPEC classification against scholarly text structure | Owner confirms: "Is this what matters for my books?" | If Oracle ESCALATEs on novel classification |
| G2 x6 | Each engine Step 4 | Oracle verifies gold baselines via web search + Usul.ai | Owner confirms: "Does this look useful?" | If Oracle finds contradictory sources |
| G3 | Before Taxonomy Step 3 | Oracle generates nahw tree via multi-source research | Owner confirms: "Does this match how I learned nahw?" | Almost certainly — this requires experiential knowledge |
| G4 | Synthesis Step 4 | Oracle evaluates narrative quality against ENTRY_EXAMPLE.md | Owner confirms: "Does this read like a reference I'd trust?" | If narrative quality is ambiguous |

### What happens when owner is unavailable

Per ENGINE_PROTOCOL, after 3 days without Tier 2 response, the factory proceeds with Oracle-only decisions:
1. Decisions marked `[OWNER REVIEW PENDING]`
2. Oracle applies extra caution (ESCALATE threshold lowered)
3. **Extended multi-model verification** (4-model consensus on the pending decisions)
4. Owner can review retroactively at any point — if they disagree, roll back and redo
5. Any Oracle ESCALATE with no Claude Chat available → decision deferred, engine continues on non-blocked work

### Owner time commitment

Total: **~4-6 hours** across all 6 engines (reduced from 8-10 because Oracle handles substantive reasoning).
- G1 sanity checks: ~10 min each × 6 = ~1 hour
- G2 sanity checks: ~15 min each × 6 = ~1.5 hours
- G3 (nahw tree): ~1 hour (likely needs Claude Chat escalation)
- G4 (entry viewer): ~30 min
- Claude Chat escalations: ~1-2 hours total (estimated 3-5 escalations across all engines)

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

## Resources & Tools Integration

Evaluated from `reference/RESOURCES.md` (667 lines, 45+ tools), `reference/IDEAS.md` (3 ideas), and `reference/RESOURCE_INBOX.md` (131 inbox items). Each resource is mapped to the specific engine and step where it should be integrated.

### Cross-Cutting: Tools for ALL Engines

| Tool | Status | Where to Use | Impact |
|------|--------|-------------|--------|
| **DSPy** (Stanford/Databricks) | EVALUATED, not yet adopted | Step 2 Research for engines 4-7 (LLM-dependent). MIPROv2 optimizer can auto-tune prompts for scholarly classification tasks. | HIGH — could significantly improve LLM accuracy on atomization, excerpting, taxonomy, synthesis tasks. Evaluate in Engine 4 Step 2. |
| **desloppify** | IN INBOX, HIGH PRIORITY | Reviewer agent's toolkit. Run on every Builder output during Step 3. | MEDIUM — catches LLM-generated code quality issues. Evaluate before normalization build starts. |
| **DeepEval** (Apache 2.0) | EVALUATED | Step 4 (Prove) for all engines. GEval, correctness, bias metrics. pytest integration. | MEDIUM — supplements existing quality scripts with LLM-specific evaluation metrics. |
| **Swan-Large** (NYUAD) | EVALUATED, STEERING.md outdated | Any engine needing Arabic embeddings (taxonomy, synthesis, deduplication). SOTA on ArabicMTEB. | ACTION: Update STEERING.md from "arabic-e5-base" to "Swan-Large (recommended)". |
| **usul-data** (seemorg, MIT) | EVALUATED, ready to bundle | Verifier agent's scholarly verification. 40K+ scholars with multilingual names, Hijri death dates, book metadata. | HIGH — dramatically improves Verifier's ability to cross-reference scholarly claims. Bundle with KR. |
| **Instructor** | ADOPTED, in use | All engines — structured LLM output with Pydantic. Already integrated. | Already delivering value. |
| **LiteLLM** | ADOPTED, in use | All engines — provider abstraction. Already integrated. | Already delivering value. |

### Normalization Engine (Engine 2) — Specific Resources

| Tool | Status | Integration Point | Priority |
|------|--------|------------------|----------|
| **QARI-OCR** | EVALUATED, recommended | Core OCR for classical Arabic with diacritics. CER 0.061, WER 0.160. Runs locally with 8-bit quantization on user's GPU. | HIGH — primary OCR choice (already in STEERING.md). Stage 2 for photo/scan formats. |
| **Baseer** (Misraj AI) | EVALUATED | Secondary OCR for complex layouts (multi-column, tables, footnotes). MARS 68.13 SOTA. | MEDIUM — Stage 2 for complex formats. |
| **Mistral OCR 3** | EVALUATED, in STEERING.md | Fallback OCR. API-based, $2/1000 pages. Strong Arabic. | LOW for Stage 1 (Shamela HTML doesn't need OCR). Stage 2 fallback. |
| **PaddleOCR-VL 1.5** (Baidu) | EVALUATED | Fast first-pass OCR (0.9B model). Requires Flash Attention 2. | LOW — Stage 2 fast-pass option. |
| **Docling** (IBM) | EVALUATED | PDF/DOCX conversion. Arabic support experimental. | MEDIUM — evaluate for Word doc handling in Stage 2. |
| **Source format hunting** (IDEAS.md) | IDEA, not yet implemented | Before OCR on difficult format, check if source exists in better format (HTML, EPUB). Smart optimization for normalization pipeline. | HIGH IDEA — reduces OCR errors by finding better sources. Add to normalization SPEC as optional pre-processing step. |

**Unevaluated (need triage via /technology-survey):**
- Azure AI Vision, Amazon Textract, DeepSeek-OCR, Sakhr Software — OCR services
- OpenAI Whisper, Speechmatics, Kateb ASR — Speech-to-text (only relevant if audio input planned)

**Action:** Run `/technology-survey` on Azure AI Vision, Amazon Textract, and DeepSeek-OCR before normalization Step 2. The others are Stage 2 or irrelevant.

### Atomization Engine (Engine 4) — Specific Resources

| Tool | Status | Integration Point | Priority |
|------|--------|------------------|----------|
| **Quran_Detector** | EVALUATED | Atom classification — identifies Quranic verses in Arabic text. Handles typos, missing words. Returns surah/ayah. | HIGH — core capability for scholarly function classification. Integrate in Step 3. |
| **Quranic Arabic Corpus** | EVALUATED | Reference data — complete word-by-word morphology, syntactic treebank, semantic ontology. | HIGH — enriches Quranic citation atoms with precise reference information. |
| **Hadith Segmenter** (Altammami 2023) | EVALUATED | Atom classification — segments hadith into isnad (narrators) + matn (content). 92.5% accuracy. | HIGH — validates and assists hadith atom type classification. |
| **CANERCorpus** | EVALUATED | Reference — 7000+ hadiths with Islamic entity classes. Potential training data. | MEDIUM — reference for NER patterns in scholarly text. |
| **DSPy MIPROv2** | EVALUATED | Step 2 — auto-optimize classification prompts for scholarly function. Bayesian combination search. | HIGH — could push LLM classification accuracy above the 85% threshold. Evaluate in Step 2. |

### Excerpting Engine (Engine 5) — Specific Resources

| Tool | Status | Integration Point | Priority |
|------|--------|------------------|----------|
| **ContextGem** | EVALUATED | Reference for self-containment evaluation patterns. Document-level LLM extraction with context preservation. | MEDIUM — design reference for the highest-risk LLM task (T-4: Context Loss). Study during Step 1. |
| **LLM4IE papers** | EVALUATED | Research foundation for excerpt enrichment. NER, relation extraction, event extraction. | MEDIUM — research reference for Step 2. |

### Taxonomy Engine (Engine 6) — Specific Resources

| Tool | Status | Integration Point | Priority |
|------|--------|------------------|----------|
| **NetworkX** | ADOPTED | Tree validation, DAG operations, centrality scoring. Already in tech stack. | Already delivering value. |
| **nxontology** (Apache 2.0) | EVALUATED | Potential enhancement — semantic similarity, information content on taxonomy tree. | LOW — Stage 2 enhancement. NetworkX sufficient for core. |
| **Classical Islamic Pedagogical Resources** | EVALUATED | Nahw tree validation — madhab-specific learning progressions from islamclass.wordpress.com, SeekersGuidance curriculum. | HIGH — Oracle + Verifier should reference these when validating the nahw science tree (human gate G3). |
| **usul-data** | EVALUATED | Scholar metadata for taxonomy placement verification — confirms which scholars belong to which sciences. | HIGH — already recommended for cross-cutting use. |

### Synthesis Engine (Engine 7) — Specific Resources

| Tool | Status | Integration Point | Priority |
|------|--------|------------------|----------|
| **Attr-First** (Slobodkin et al., ACL 2024) | RESEARCH | Core design pattern — select source spans FIRST, then generate conditioned on them. Fine-grained attribution built-in. | CRITICAL — this validates KR's citation-grounded synthesis design. Step 1 SPEC should reference this approach. |
| **OpenScholar** (Asai et al., Nature 2025) | RESEARCH | Hallucination mitigation — 8B model outperforms GPT-4o by 6.1%. GPT-4o citation hallucination: 78-90%. | CRITICAL — quantifies the hallucination risk. Informs why KR needs multi-model verification for every claim. |
| **Belem et al. 2025** | RESEARCH | Risk quantification — 75% hallucination rate in LLM summaries, increasing toward end of output. | CRITICAL — informs synthesis quality bar and verification protocol. |
| **LAQuer** (ACL 2025) | RESEARCH | Verification technique — localized attribution queries with NLI verification. | HIGH — could be integrated into Verifier agent's synthesis review protocol. |
| **ContraDoc/ContraGen** (2024-2025) | RESEARCH | Self-contradiction detection — multi-agent framework. | MEDIUM — reference for synthesis self-consistency checking. |
| **NEXUSSUM** (ACL 2025) | RESEARCH | Alternative synthesis approach — hierarchical multi-agent (chunk→summarize→merge). 30% improvement. | MEDIUM — research reference. KR's approach is different but can learn from this. |

### Scholar Authority Enrichment (Cross-Engine)

| Source | Status | Integration | Priority |
|--------|--------|------------|----------|
| **usul-data** (seemorg, MIT) | READY TO BUNDLE | 40K+ scholars, multilingual names, Hijri death dates, book metadata. JSON format. | HIGH — integrate during Engine 2 setup. Enriches scholar_authority module. |
| **Muslim Scholars Database** (muslimscholars.info) | EVALUATED, access unclear | 40K+ records with Tahzeeb/Taqrib/Thiqat source data. Teacher-student links. | HIGH if accessible — explore during Engine 2 Step 1. Request from maintainers. |
| **OpenITI metadata** | EVALUATED | 7K+ integrated texts. CTS-compliant URIs encode author death dates. Dec 2025 release. | MEDIUM — bootstrapping reference for scholar registry. |
| **Wikidata Islamic Scholars** | EVALUATED | SPARQL queryable. Coverage incomplete for premodern scholars. CC0. | LOW — supplement when usul-data has gaps. |

### Unresolved Architectural Question (IDEAS.md)

> *"I just learned about RAG libraries. Is it still meaningful to continue developing this application the way we visualized it (7 engines)? Or would RAG libraries help achieve the goal?"*

**Resolution:** The 7-engine pipeline IS the correct architecture. RAG libraries (GraphRAG, StructRAG) are research references that inform specific engines (taxonomy, synthesis) but do NOT replace the pipeline. Here's why:

1. **RAG retrieves — KR transforms.** RAG finds relevant passages. KR's pipeline does something fundamentally different: it extracts scholarly structure (layers, atoms, excerpts), preserves attribution chains, and synthesizes multi-century scholarly narratives. RAG can't do this.

2. **RAG has no normalization boundary.** KR's critical insight is that source-specific processing (above the boundary) must be separated from source-agnostic scholarly processing (below). RAG flattens everything into vectors, losing structural information.

3. **RAG hallucinates citations.** OpenScholar (Nature 2025) found GPT-4o hallucinates 78-90% of citations. KR's grounding_type traceability (D-040) prevents this by requiring every claim to be tagged with its source.

4. **Where RAG DOES help:** Qdrant (already in tech stack) provides RAG-like semantic search for the Scholar Interface (Stage 2). GraphRAG patterns could inform the taxonomy engine's placement algorithm.

**Decision: 7-engine architecture confirmed. RAG libraries are supplementary tools for specific engines, not replacements.** This should be documented in IDEAS.md as resolved.

### Inbox Triage Action Items

**Before Engine 2 starts (evaluate via /technology-survey):**
1. **desloppify** — Code quality for LLM-generated code → Reviewer agent toolkit
2. **Azure AI Vision** — OCR service → compare with QARI-OCR
3. **Amazon Textract** — Document extraction → compare with Docling
4. **DeepSeek-OCR** — New OCR model → Arabic diacritics support?

**Before Engine 4 starts (evaluate via /technology-survey):**
5. **DSPy MIPROv2** — Prompt optimization → classification accuracy boost

**Defer or deprioritize (Stage 2 or low relevance):**
- Speech-to-text tools (Whisper, Speechmatics, Kateb ASR) — only if audio input planned
- Claude Code workflow tools (12 items) — evaluate as workflow needs arise
- AI Agent frameworks (13 items) — OpenClaw already selected as coordinator
- Social links, general tools — reference only

### STEERING.md Correction Required

**Current (wrong):** `Embeddings: arabic-e5-base or GTE-multilingual-base`
**Should be:** `Embeddings: Swan-Large (NYUAD SOTA on ArabicMTEB) or Arabic-STS-Matryoshka for efficiency`

This is a factual error that RESOURCES.md (March 2026 survey) already corrected but STEERING.md wasn't updated.

---

## Implementation Order

### Phase 0: Decision Playbook (before anything else)

0. **Write `reference/DECISION_PLAYBOOK.md`** — Claude Chat (in conversation with owner) captures all accumulated heuristics, patterns, and domain rules from the source engine build. This is the Oracle's institutional memory. Without it, the Oracle starts from zero. **This is the single most important deliverable for factory quality.**

### Phase 1: Core infrastructure (Option A — Claude Code native)

1. **Create `.claude/agents/reviewer.md`** — Read-only review subagent definition.

2. **Create `.claude/agents/verifier.md`** — Independent test-writing subagent definition.

3. **Create `.claude/agents/oracle.md`** — Claude Chat equivalent agent definition (reads Decision Playbook).

4. **Create `reference/ENGINE_FACTORY.md`** — The master blueprint with all sections (A through H). Updated to reference Decision Playbook, three-tier gate model, and Option A/B architecture.

5. **Create `.claude/commands/build-engine.md`** — Entry point command. Drives ENGINE_PROTOCOL, invokes reviewer/verifier subagents, calls `claude -p` for Oracle decisions.

6. **Create `.claude/commands/engine-handoff.md`** — Session end protocol.

7. **Create `.claude/commands/engine-status.md`** — Progress dashboard.

8. **Create `scripts/engine_orchestrator.py`** — Deterministic orchestration script. Drives the build→review→verify→test→commit cycle without LLM flow control.

9. **Create `scripts/engine_readiness.py`** — Step advancement gate.

10. **Create `scripts/cross_engine_regression.py`** — Regression test runner.

11. **Create `.pre-commit-config.yaml`** — Pre-commit hooks for black + mypy + quality scripts.

12. **Set up Telegram notifications** — Simple bot for Tier 2 owner sanity check notifications.

13. **Fix STEERING.md embedding recommendation** — Update from "arabic-e5-base" to "Swan-Large (NYUAD SOTA)".

14. **Resolve IDEAS.md RAG question** — Document the decision: 7-engine architecture confirmed, RAG is supplementary.

15. **Bundle usul-data** — Download and integrate the 40K+ scholar dataset (MIT licensed) for Oracle/Verifier scholarly verification.

16. **Test the factory** — Dry run on normalization Step 1: Builder extracts SPEC_CORE → reviewer subagent reviews → verifier subagent checks contracts → Oracle (`claude -p`) approves gate → owner sanity-checks via Telegram.

### Phase 2: OpenClaw upgrade (Option B — only if needed)

17. **Set up OpenClaw Gateway** — Only if Option A proves insufficient (need 24/7 unattended operation or more parallelism).

18. **Install and configure Lobster** — Deterministic workflow engine for the build pipeline.

19. **Migrate subagent definitions to OpenClaw agent SOUL.md files** — Reviewer and Verifier become full OpenClaw agents with inter-agent communication.

20. **Set up git hooks** — Post-commit triggers Reviewer on engine code changes.

### Critical files to create (Option A)
- `.claude/agents/reviewer.md` (NEW — SPEC compliance, Arabic safety, D-023, knowledge integrity review)
- `.claude/agents/verifier.md` (NEW — independent test writing from SPEC only)
- `.claude/agents/oracle.md` (NEW — Claude Chat equivalent for domain reasoning)
- `reference/DECISION_PLAYBOOK.md` (NEW — **CRITICAL** — Oracle's institutional memory, ~200-400 lines)
- `reference/ENGINE_FACTORY.md` (NEW — ~1000-1500 lines)
- `.claude/commands/build-engine.md` (NEW — ~150-200 lines)
- `.claude/commands/engine-handoff.md` (NEW — ~80-100 lines)
- `.claude/commands/engine-status.md` (NEW — ~60-80 lines)
- `scripts/engine_orchestrator.py` (NEW — ~200-300 lines, deterministic build cycle)
- `scripts/engine_readiness.py` (NEW — ~300-400 lines)
- `scripts/cross_engine_regression.py` (NEW — ~150-200 lines)
- `.pre-commit-config.yaml` (NEW — ~30-50 lines)

### Additional files for Option B (if upgrading)
- `~/.openclaw/openclaw.json` (gateway config with builder/reviewer/verifier agents)
- `~/.openclaw/agents/*/SOUL.md` (per-agent workspace files)
- `workflows/engine-module-build.lobster` (Lobster workflow definition)
- `.git/hooks/post-commit` (triggers Reviewer on engine code commits)

### Critical files to update
- `NEXT.md` (UPDATE — point to factory)
- `engines/*/CLAUDE.md` x6 (UPDATE — add factory status sections)
- `STEERING.md` (UPDATE — reference ENGINE_FACTORY.md, fix embedding recommendation)

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
- `reference/CLAUDE_CODE_MEMORY_PRINCIPLES.md` — 33 principles for Claude Code (feeds into Decision Playbook)

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

5. **Multi-agent quality verification (Option A — Claude Code native)**
   - Reviewer subagent invoked from main session, returns APPROVE/REJECT with specific issues
   - Verifier subagent writes independent tests without seeing Builder's code
   - Oracle (`claude -p --effort max`) makes evidence-based gate decisions with Decision Playbook context
   - Oracle correctly ESCALATEs when confidence is low or pattern is novel
   - Telegram notification fires when Tier 2 owner sanity check is needed
   - `engine_orchestrator.py` drives the build→review→verify→test→commit cycle deterministically

6. **End-to-end dry run (normalization Step 1)**
   - Builder extracts a small section of SPEC_CORE
   - Reviewer subagent reviews → responds with findings
   - Verifier subagent writes independent contract compatibility test → test passes
   - Oracle evaluates core/deferred classification → APPROVE with reasoning
   - Owner receives Telegram summary → confirms "looks right"
   - Decision Playbook is consulted and applied by Oracle during gate decision

7. **Pre-commit hooks**
   - `black` formats on commit
   - `mypy --strict` runs on changed engine files
   - Quality scripts run on relevant changes

### Success criteria for the full factory

- All 6 engines reach Step 4 COMPLETE with ALL exit criteria satisfied
- Cross-engine regression passes from source through synthesis
- `verify_metadata_flow.py` shows clean D-023 compliance across the FULL pipeline
- `run_pipeline.py` produces a knowledge entry from Shamela HTML → source → ... → synthesis
- Owner has sanity-checked all gold baselines (Tier 2)
- Scholarly verification completed on all gold baselines with no unresolved discrepancies
- mypy --strict passes across ALL engine code
- pytest-cov ≥90% on ALL core modules
- Each engine has LESSONS.md with forward-looking insights
- Backward lesson reviews completed after engines 2, 4, 6
- No known defects in any SPEC_CORE.md (0 HIGH across all engines)
- **Every module has Reviewer APPROVE in audit trail**
- **Every engine has Verifier's independent tests passing alongside Builder's tests**
- **Every gold baseline has Oracle verification log (web search + Usul.ai cross-reference)**
- **Decision Playbook updated after each engine build with new patterns discovered**
- **All Oracle ESCALATE decisions resolved via Claude Chat with resolution documented**
