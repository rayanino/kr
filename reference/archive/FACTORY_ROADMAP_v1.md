# KR Factory Roadmap — الخطة التشغيلية للمصنع

**Authority:** GOVERNING. Supersedes `reference/ENGINE_FACTORY_PLAN.md` (archived).
**Written:** 2026-03-27
**Sources:** Claude Chat analysis, CC environment inventory (verified 2026-03-26), GPT-5.4 independent review, three-CLI capability research (verified against official docs), CC capabilities report (partially fabricated — verified claims only adopted)
**Verification note:** CC's Technical Capabilities Report claimed GSD orchestration system (doesn't exist), 97 agents (actual: 20), CronCreate (no evidence), Agent Teams enabled (not set). This roadmap uses only tool-verified facts. See QUALITY_AXIOM.md §Standing Order 2.

---

## Goal

Build a deterministic control plane that autonomously builds, tests, evaluates, and hardens KR engines on the owner's 24/7 Windows PC. Quality is enforced by machinery. The owner intervenes only for: reading Arabic scholarly output, making priority/preference decisions, and periodic audit sampling.

**"Done" means:** The factory receives a new engine SPEC → decomposes it into work units → builds the engine across multiple CC sessions (each starting fresh from disk state) → verifies output using cross-provider CLI review → runs benchmark-routed Arabic domain verification → presents the owner with formatted evidence packets for genuine human decisions → produces a proven engine. No message relaying. No protocol memorization. No willpower.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CONTROL PLANE                           │
│                                                             │
│  ops_manifest.json          ← single source of truth        │
│  work_queue/                ← typed work units              │
│  policies/                  ← machine-enforced rules        │
│  artifacts/                 ← immutable provenance bundles  │
│  benchmarks/                ← KR-specific model scores      │
│  routing_table.json         ← benchmark-driven model routes │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              ORCHESTRATOR (Python)                    │   │
│  │  Reads state → picks work unit → dispatches CLI      │   │
│  │  → captures JSON → runs gates → dispatches review    │   │
│  │  → captures review → persists state → commits        │   │
│  │  → schedules next run via Windows Task Scheduler     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ CLAUDE CODE  │  │  CODEX CLI   │  │  GEMINI CLI  │     │
│  │ (builder)    │  │  (reviewer)  │  │  (adversary) │     │
│  │              │  │              │  │              │     │
│  │ claude -p    │  │  codex exec  │  │  gemini -p   │     │
│  │ --output-    │  │  --output-   │  │  --output-   │     │
│  │ format json  │  │  format json │  │  format json │     │
│  │              │  │              │  │              │     │
│  │ Opus 4.6     │  │  GPT-5.4    │  │  Gemini 3.1  │     │
│  │ $0/call      │  │  $0/call    │  │  $0/call     │     │
│  │              │  │              │  │              │     │
│  │ CLAUDE.md    │  │  AGENTS.md  │  │  GEMINI.md   │     │
│  │ 13 hooks     │  │  KR context │  │  KR context  │     │
│  │ 13 skills    │  │  + Playbook │  │  NO Playbook │     │
│  │ 15 rules     │  │             │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                             │
│  All three read the same git repo.                          │
│  All produce structured JSON to stdout.                     │
│  The orchestrator makes every transition decision.          │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              DETERMINISTIC LAYER                      │   │
│  │  13 tested hooks + CI/CD + policy engine              │   │
│  │  pytest · pyright · ruff · D-023 · contracts · gates  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  OPTIONAL / SUPPLEMENTARY                                   │
│  ┌────────────┐  ┌───────────┐  ┌────────────────────┐    │
│  │ OpenClaw   │  │ MacBook   │  │ OpenRouter API     │    │
│  │ for alerts │  │ Air for   │  │ fallback for       │    │
│  │ (Telegram) │  │ Computer  │  │ Instructor/Pydantic│    │
│  │            │  │ Use (macOS│  │ structured output  │    │
│  │            │  │ only)     │  │                    │    │
│  └────────────┘  └───────────┘  └────────────────────┘    │
└──────────────────────────────┬──────────────────────────────┘
                               │ structured files in git
┌──────────────────────────────▼──────────────────────────────┐
│                      OWNER LAYER                            │
│  Dashboard (GitHub Pages)   — read-only, auto-refreshed     │
│  Human gate queue           — batched evidence packets      │
│  Arabic output reviewer     — formatted RTL with Amiri font │
│  Telegram alerts (optional) — "factory needs you"           │
└─────────────────────────────────────────────────────────────┘
```

### Design decisions

**D-F001: Deterministic control plane, not agent orchestration.**
The factory is software that dispatches models, not models coordinating with each other. The orchestrator (a Python script) owns all state, work decomposition, policy enforcement, and transitions. This eliminates the fragility of session-dependent logic and prompt choreography. (Source: GPT-5.4 independent review, March 2026.)

**D-F002: Cross-provider review is structural, not optional.**
Policy: the builder's provider CANNOT be the sole reviewer for any decision that affects scholarly content. Different providers = different training data = different blind spots. This is the knowledge-diversity principle implemented with genuine model diversity, not same-model prompt isolation.

**D-F003: Three independent coding CLIs at zero marginal cost.**
All three frontier providers ship terminal coding agents included in existing subscriptions: Claude Code (`claude -p`), Codex CLI (`codex exec`), Gemini CLI (`gemini -p`). All support headless mode with structured JSON output. All read the full repo. This eliminates per-token API costs for review and adversarial tasks. (Verified against official docs: Anthropic Claude Code docs, OpenAI Codex CLI docs, Google Gemini CLI docs, March 2026.)

**D-F004: Benchmark-routed model assignment.**
No model role for Arabic scholarly tasks is frozen until the KR benchmark harness provides empirical scores. The routing table is a configuration file updated by benchmark results, not hardcoded assumptions.

**D-F005: Deterministic checks first, models on top.**
Everything that CAN be a script MUST be a script. Models sit on top only for tasks requiring judgment.

**D-F006: State lives in machine-readable files, not prose.**
`ops_manifest.json` is the single operational truth. NEXT.md and CLAUDE.md are informational, never authoritative for operational state.

**D-F007: Every nontrivial action produces an immutable artifact bundle.**
Prompt, CLI/model/version, inputs, outputs, tests run, review results, commit SHA, disposition. This is scholarly provenance for the factory itself.

**D-F008: Playbook rules have provenance and expiration.**
Every rule in DECISION_PLAYBOOK.md must have: `created_at`, `justified_by`, `scope`, `revalidate_by`, `invalidated_by`. Prevents playbook ossification (GPT-5.4's predicted 6-month failure mode).

**D-F009: Claude Code is the sole code modifier.**
The entire KR codebase was built by CC with 13 hooks, 13 skills, 15 rules configured for its conventions. Codex CLI and Gemini CLI REVIEW and CHALLENGE only — they never modify KR code. This is enforced by the orchestrator (read-only dispatches) and by their project context files (explicit instructions).

**D-F010: Claude Chat has no role in the autonomous loop.**
Claude Chat requires the owner's presence. The autonomous factory cannot depend on it. Architectural reasoning is handled by CC subagents (verified: 18 active agents including architect-level auditors and reviewers) plus cross-provider CLI review. Claude Chat is for strategic planning sessions initiated by the owner when desired — not part of daily factory operation.

**D-F011: Never trust CC self-reports without tool verification.**
CC fabricated capabilities in this planning phase (GSD system, 97 agents, CronCreate, Agent Teams enabled). Every CC claim about its own capabilities must be verified by running tools against the actual repo before the roadmap depends on it. This is Standing Order 2 from QUALITY_AXIOM.md applied to the factory itself.

### Model assignments

| Role | Tool | Model | Cost | Locked? |
|------|------|-------|------|---------|
| **Builder** | Claude Code | Opus 4.6 | $0 (Max sub) | **YES** — 13 hooks, 13 skills, 15 rules |
| **Architecture reviewer** | Codex CLI | GPT-5.4 | $0 (ChatGPT sub) | **PROVISIONAL** — pending KR benchmark |
| **Adversarial challenger** | Gemini CLI | Gemini 3.1 Pro | $0 (free/paid tier) | **PROVISIONAL** — pending KR benchmark |
| **Arabic domain verifier** | Benchmark winner | Best scorer per task | $0 (CLI) | **BLOCKED** on Session 5 |
| **Deterministic checks** | Software | N/A | $0 | **YES** |
| **API fallback** | OpenRouter | Any model | Per-token | Fallback only |

### Knowledge-diversity implementation

The strongest idea from the 18-agent architecture (verified valuable by GPT-5.4 review):

- **Codex CLI reviews WITH the Decision Playbook.** Its `AGENTS.md` includes Playbook rules as context. This is the guided, institutional-memory path.
- **Gemini CLI challenges WITHOUT the Decision Playbook.** Its `GEMINI.md` explicitly excludes Playbook access and instructs first-principles reasoning only. This is the unguided path.
- **When they disagree,** the disagreement is the strongest signal — it reveals either a Playbook error (institutional bias) or a genuine edge case the Playbook doesn't cover.
- **When they agree,** confidence is high — two different model families with different context independently reached the same conclusion.

### What the owner does (and nothing else)

| Task | When | Time |
|------|------|------|
| Priority decisions | Per engine transition | ~15 min |
| Arabic domain adjudication | When models disagree on scholarly content | ~20 min/batch |
| Arabic output utility review | Per engine evaluation | ~1 hour |
| Audit sampling | Monthly | ~30 min |

---

## Verified Existing Infrastructure

Built on tool-verified facts from the CC inventory (2026-03-26), not on CC's capabilities report.

**Working and tested (evidence in git):**
- 13 hooks (7 PreToolUse, 7 PostToolUse, 2 SessionStart, 1 Stop) — most tested
- 13 domain skills in `.claude/skills/` (arabic-text, knowledge-safety, scholarly-attribution, etc.)
- 15 rules in `.claude/rules/` (quality-workflow, testing, python-code, arabic-conventions, etc.)
- 18 active agent definitions (6 SPEC team, 3 Build team, 4 Verification team, 3 Red team, 2 specialized) — 7 tested, 11 untested
- 15 commands (7 tested: /catchup, /commit, /quality-gate, /smart-compact, /build-fix, /tdd, /check-spec, /research, /read-vision, /verify-boundaries)
- `/orchestrate` command — chains code-reviewer → build-prober with structured handoffs
- GitHub Actions CI — runs pytest + metadata flow + contract validation on push
- 3 MCP servers (Context7, Tavily, Memory)
- Pre-push test gate (blocks push on test failure)
- Arabic safety hook (catches `.lower()/.upper()` on Arabic text)
- Pyright type checking hook
- Ruff + black formatting hook

**Broken or untested (needs fixing in Session 2):**
- `circuit-breaker.sh` — uses `/tmp/` (fragile on Windows)
- `cost-guard.sh` — never triggered by real API calls
- `no-ask-human.sh` — overnight mode untested
- `auto-test.sh` — noisy during rapid iteration
- 11 of 18 agents never dispatched
- 8 of 15 commands never used
- No branch protection on GitHub
- No ruff/black/pyright in CI (only in hooks)
- No `.pre-commit-config.yaml`

---

## Session-by-Session Roadmap

### Phase 1: Operational Foundation (Sessions 1-3)

**Objective:** Single source of truth exists. CI catches everything deterministic. All three CLIs are installed and verified. Cross-provider review works.

---

#### Session 1 — Operational Truth + Document Reconciliation

**Type:** CC builder session
**Goal:** Create `ops_manifest.json` as the single machine-readable source of truth. Reconcile every stale document with the 5-engine pipeline reality.

**Why first:** GPT-5.4 found that `reference/AGENT_ARCHITECTURE.md` already describes a stale 7-engine pipeline while the actual repo has 5 engines. Without fixing this, every subsequent session reads wrong context. The factory cannot be built on a fractured foundation.

**CC prompt (ready to paste):**

> Read `reference/FACTORY_ROADMAP.md` (the governing roadmap for the factory setup). Execute Session 1 exactly as specified. Your deliverables are:
>
> 1. Create `ops_manifest.json` with schema: engine_graph, active_engine, current_phase, work_items[], model_routing{}, policies{}, playbook_rules[] (each rule gets created_at, scope, revalidate_by fields), benchmark_status{}, human_gate_backlog[], last_updated.
> 2. Create `scripts/validate_manifest.py` — schema validation.
> 3. Update `reference/AGENT_ARCHITECTURE.md` — 5-engine pipeline, mark as non-authoritative for ops state.
> 4. Move `reference/ENGINE_FACTORY_PLAN.md` to `reference/archive/`.
> 5. Update `CLAUDE.md` — correct test counts, reference ops_manifest.json.
> 6. Verify every `engines/*/CLAUDE.md` matches actual state.
> 7. Add provenance fields to every rule in `DECISION_PLAYBOOK.md`.
>
> Exit criteria: validate_manifest.py passes. No file references "7 engines." Every Playbook rule has provenance. Git clean and pushed.
>
> Do NOT implement anything beyond these deliverables. Do NOT proceed to Session 2. Commit and push when complete.

**Exit criteria (machine-verifiable):**
- `python scripts/validate_manifest.py` exits 0
- `grep -rn "7 engines\|6 remaining\|six remaining" reference/ engines/ CLAUDE.md` returns nothing
- `grep -c "revalidate_by" reference/DECISION_PLAYBOOK.md` ≥ number of rules
- Git status clean, pushed to origin

---

#### Session 2 — CI/CD Hardening + Policy Engine + Hook Fixes

**Type:** CC builder session
**Goal:** Expand CI to catch everything deterministic. Create machine-enforceable policies. Fix the four broken hooks.

**CC prompt:**

> Read `reference/FACTORY_ROADMAP.md` Session 2. Execute exactly as specified.
>
> Deliverables:
> 1. Expand `.github/workflows/test.yml`: add ruff check, black --check, pyright, test stratification with `@pytest.mark.expensive`, cross-engine tests when `shared/` changes, `scripts/validate_manifest.py` as CI step.
> 2. Create `.github/workflows/nightly.yml`: expensive LLM tests on schedule.
> 3. Create `.pre-commit-config.yaml`: ruff, black, pyright, conventional-commits.
> 4. Enable GitHub branch protection on master via gh CLI.
> 5. Create `policies/` directory with JSON policy files: `no_self_approve.json`, `cross_provider_scholarly.json`, `no_merge_without_gates.json`, `playbook_provenance.json`.
> 6. Create `scripts/check_policies.py` — validates work unit dispositions against policies.
> 7. Fix `circuit-breaker.sh` — use project-local `.circuit_breaker` file, not `/tmp/`.
> 8. Fix `auto-test.sh` — use `CLAUDE_RAPID_MODE=1` env var to suppress during rapid iteration. Default to suppressed; explicit opt-in to auto-test.
> 9. Fix `cost-guard.sh` — add a test that simulates an API call path and verifies the guard triggers.
> 10. Fix `no-ask-human.sh` — verify it works when `KR_OVERNIGHT=1` is set.
>
> Exit criteria: Push to branch → CI runs full suite → green. Pre-commit blocks bad formatting. Branch protection verified via `gh api`. All 4 hooks fixed and tested. `python scripts/check_policies.py --test` passes.
>
> Do NOT proceed to Session 3.

**Exit criteria:**
- CI workflow includes ruff + black + pyright + pytest + manifest validation + contracts
- `.pre-commit-config.yaml` exists and `pre-commit run --all-files` passes
- `gh api /repos/rayanino/kr/branches/master/protection` returns protection rules
- `python scripts/check_policies.py --test` exits 0
- Each of the 4 fixed hooks has a test demonstrating it works

---

#### Session 3 — Three-CLI Setup + Cross-Provider Dispatch Layer

**Type:** CC builder session + owner assists with Codex/Gemini authentication
**Goal:** Install Codex CLI and Gemini CLI. Create project context files for each. Build the dispatch layer. Verify cross-provider review works end-to-end.

**OWNER ACTION REQUIRED before this session:**
1. Install Codex CLI: `npm i -g @openai/codex` (or via WSL if Windows native is unstable)
2. Authenticate Codex: `codex login` (use ChatGPT account)
3. Install Gemini CLI: `npx @google/gemini-cli` (or `npm i -g @google/gemini-cli`)
4. Authenticate Gemini: follow Google account prompt on first run
5. Verify both work: `codex exec "echo hello" --output-format json` and `gemini -p "echo hello" --output-format json`

**CC prompt:**

> Read `reference/FACTORY_ROADMAP.md` Session 3. Execute exactly as specified.
>
> PREREQUISITE: Owner has installed and authenticated Codex CLI and Gemini CLI. Verify by running:
> - `codex exec "What is 2+2?" --output-format json`
> - `gemini -p "What is 2+2?" --output-format json`
> If either fails, STOP and report to owner.
>
> Deliverables:
> 1. Create `AGENTS.md` (Codex CLI project context): KR overview, 7 corruption threats, quality axiom, SPEC conventions, review protocol, Decision Playbook reference, explicit instruction "You are a REVIEWER — never modify code — report findings as structured JSON."
> 2. Create `GEMINI.md` (Gemini CLI project context): same KR overview and corruption threats, but NO Decision Playbook access, explicit instruction "You are an ADVERSARIAL CHALLENGER — reason from first principles only — try to break the design — find what builder and reviewer missed."
> 3. Create `scripts/cli_dispatch.py`: functions `dispatch_claude(prompt, cwd, timeout)`, `dispatch_codex(prompt, cwd, timeout)`, `dispatch_gemini(prompt, cwd, timeout)`. Each calls the CLI headlessly, captures stdout, parses JSON, writes artifact bundle to `artifacts/`. Error handling: timeout, non-zero exit, invalid JSON → retry once → log failure.
> 4. Create `shared/external/artifact_ledger.py`: writes immutable bundles to `artifacts/YYYY-MM-DD/` as JSON. Each bundle: cli_used, prompt_hash, model_inferred, inputs, outputs, git_sha, timestamp, disposition.
> 5. Create `scripts/test_cli_dispatch.py`: integration test that (a) dispatches a KR-relevant prompt to each CLI, (b) verifies JSON parses, (c) verifies artifact bundle written, (d) runs a mini cross-provider cycle: CC makes a trivial code change → Codex reviews the diff → Gemini challenges the review → all captured as artifacts.
>
> Exit criteria: All 3 CLIs respond to headless prompts. test_cli_dispatch.py passes. A real cross-provider cycle completes. AGENTS.md and GEMINI.md committed. Knowledge diversity verified: AGENTS.md includes Playbook, GEMINI.md excludes it.
>
> Do NOT proceed to Session 4.

**Exit criteria:**
- `python scripts/test_cli_dispatch.py` exits 0
- `artifacts/` directory contains at least 3 artifact bundles (one per CLI)
- Cross-provider cycle artifact shows: CC output → Codex review → Gemini challenge
- `grep "Decision Playbook\|DECISION_PLAYBOOK" AGENTS.md` finds references
- `grep "Decision Playbook\|DECISION_PLAYBOOK" GEMINI.md` finds NO references (or explicit exclusion)

---

### Phase 2: Benchmark Harness (Sessions 4-5)

**Objective:** Empirical Arabic scholarly benchmark exists. Model routing is evidence-based.

---

#### Session 4 — KR Arabic Benchmark Design + Construction

**Type:** CC builder session (2 sessions expected)
**Goal:** Build the KR-specific benchmark suite for 9 Arabic scholarly tasks.

**Why this matters:** GPT-5.4: "Do not finalize long-term model role assignment before the KR benchmark harness exists. This is the most important missing component." The repo's own NEXT.md already blocks on model-role assignment research. No benchmark = no evidence = model roles stay assumed.

**CC prompt:**

> Read `reference/FACTORY_ROADMAP.md` Session 4. Execute exactly as specified.
>
> Build a benchmark harness in `benchmarks/` with 9 task types. Each task has ≥5 test cases including ≥1 adversarial case. All ground truth must be hand-verified (use web search to verify author attributions, death dates, genre classifications against multiple sources). Use known failure patterns from `reference/DECISION_PLAYBOOK.md` to craft adversarial cases.
>
> Task types:
> 1. layer_attribution — identify matn/sharh/hashiyah layers and their authors
> 2. school_classification — classify madhab/school
> 3. author_identification — identify author (include compiler-as-muhaqiq adversarial case)
> 4. genre_detection — classify genre
> 5. scholarly_function — classify by 16-type scholarly function taxonomy (SPEC §5)
> 6. self_containment — judge if excerpt is understandable alone
> 7. decontextualization — detect separated refutation/position (T-2 threat)
> 8. tahqiq_discrimination — distinguish editorial apparatus from scholarly commentary (BUG-03)
> 9. death_date_verification — verify death dates Hijri + Gregorian
>
> Also create: `benchmarks/scorer.py` (per-task scoring with confidence intervals), `benchmarks/run_benchmark.py` (dispatches to any CLI via `scripts/cli_dispatch.py`, scores, writes results).
>
> Exit criteria: Dry run parses all tasks. All ground truth verified via web search. Adversarial cases exist for decontextualization, tahqiq, compiler-as-muhaqiq. Scorer produces breakdown.
>
> Do NOT proceed to Session 5.

---

#### Session 5 — Run Benchmark + Establish Routing Table

**Type:** CC session (runs benchmark script)
**Goal:** Score all three CLIs on all 9 tasks. Produce empirical routing table.

**CC prompt:**

> Read `reference/FACTORY_ROADMAP.md` Session 5. Execute exactly.
>
> Run `python benchmarks/run_benchmark.py --cli claude` then `--cli codex` then `--cli gemini`.
> Analyze results. Write `benchmarks/RESULTS_ANALYSIS.md` with per-task comparison and confidence intervals.
> Create `routing_table.json` with benchmark-backed routing per task.
> Update `ops_manifest.json` with benchmark results and routing.
>
> Exit criteria: All 3 CLIs scored on all 9 tasks. routing_table.json committed with evidence. Total cost: $0.
>
> Do NOT proceed to Session 6.

---

### Phase 3: Orchestration (Sessions 6-7)

**Objective:** The factory runs autonomously. Work units flow through the control plane without human intervention.

---

#### Session 6 — Work-Unit System + Orchestrator

**Type:** CC builder session (2 sessions expected)
**Goal:** Build the typed work-unit queue and the Python orchestrator.

**Key design: the orchestrator is a Python script, not a CC session.** It runs independently of CC. It calls CC (and Codex and Gemini) as external processes via `cli_dispatch.py`. When the orchestrator runs, it:

1. Reads `ops_manifest.json` for current state
2. Picks the next unblocked work unit from `work_queue/`
3. Dispatches to appropriate CLI based on work unit type:
   - `implement` → `dispatch_claude()`
   - `review` → `dispatch_codex()`
   - `challenge` → `dispatch_gemini()`
4. Captures structured JSON output
5. Runs deterministic gates (pytest, pyright, policy checks)
6. If gates pass and work unit type is `implement`: dispatches `review` work unit
7. If review passes and risk is high: dispatches `challenge` work unit
8. Writes artifact bundle
9. Transitions work unit status
10. Updates `ops_manifest.json`
11. Commits to git

**CC prompt:**

> Read `reference/FACTORY_ROADMAP.md` Session 6. Execute exactly.
>
> Build:
> 1. `work_queue/schema.json` — work unit definition (id, type, engine, spec_section, inputs[], expected_outputs[], success_criteria[], assigned_cli, status, blocked_by[], policy, artifact_ids[], created_at, completed_at).
> 2. `scripts/kr_orchestrator.py` — the control plane script. Uses `scripts/cli_dispatch.py` for all model interactions. Uses `scripts/check_policies.py` for policy enforcement. Reads `routing_table.json` for Arabic domain routing. MUST be runnable as `python scripts/kr_orchestrator.py` — no interactive input.
> 3. `scripts/kr_orchestrator_test.py` — integration test: create a trivial work unit → orchestrator dispatches CC → captures output → runs gates → dispatches Codex review → dispatches Gemini challenge → all artifacts saved → state updated.
>
> Exit criteria: Orchestrator drives a trivial work unit through full cycle. Artifacts have complete provenance. ops_manifest.json updated. Policy violations blocked.
>
> Do NOT proceed to Session 7.

---

#### Session 7 — Scheduled Execution + Crash Recovery

**Type:** CC builder session + owner runs initial setup
**Goal:** The factory runs on a timer, recovers from crashes, needs no human to start it.

**CC prompt:**

> Read `reference/FACTORY_ROADMAP.md` Session 7. Execute exactly.
>
> Build:
> 1. `scripts/factory_scheduler.py` — creates Windows Task Scheduler entry via `schtasks /create`. Runs `scripts/kr_orchestrator.py` every 30 minutes. Lock file prevents concurrent runs. Heartbeat logging to `factory_logs/heartbeat.jsonl`.
> 2. `scripts/factory_recovery.py` — on startup, checks for work units stuck in `in_progress` (no completion after the process that started them is gone). Rolls back to `pending`. Logs recovery to `factory_logs/recovery.jsonl`.
> 3. `scripts/factory_start.py` — one command: `python scripts/factory_start.py`. Checks prerequisites (Python, Node, 3 CLIs installed and authed). Creates scheduled task. Runs initial health check. Prints status.
> 4. Update `reference/OWNER_INSTALL_GUIDE.md` — complete factory setup: install CLIs, auth, run factory_start.py.
>
> Exit criteria: `python scripts/factory_start.py` creates scheduled task (verify via `schtasks /query`). Factory wakes on schedule. Kill orchestrator mid-work → next run detects and recovers. Lock prevents concurrent runs.
>
> Do NOT proceed to Session 8.

**OWNER ACTION after this session:**
- Run `python scripts/factory_start.py` once
- Verify the factory wakes up on its own and does work
- The factory is now autonomous — you're done being the mailman

---

### Phase 4: Owner Interface (Session 8)

---

#### Session 8 — Dashboard + Human Gate + Arabic Formatter

**Type:** CC builder session (2 sessions expected)
**Goal:** Owner sees everything at a glance. Arabic text is readable. Decisions arrive as formatted packets.

**CC prompt:**

> Read `reference/FACTORY_ROADMAP.md` Session 8. Execute exactly.
>
> Build:
> 1. `scripts/generate_dashboard.py` — generates static HTML from ops_manifest + test results + work queue + benchmarks + heartbeat logs. Sections: current engine, work queue, test counts, quality gates, benchmark routing, pending gates, factory health, costs.
> 2. `.github/workflows/dashboard.yml` — deploys to GitHub Pages on every push.
> 3. `human_gate/` directory — `pending/`, `completed/`, `templates/`. Each pending gate is a JSON + rendered markdown with: the Arabic excerpt (RTL formatted), competing interpretations, evidence, specific question, options.
> 4. `scripts/compile_gate_packet.py` — takes a scholarly ambiguity → produces a readable evidence packet. NOT raw model transcripts.
> 5. `scripts/format_arabic_output.py` — pipeline JSON → HTML with RTL layout, Amiri font, diacritics preserved, side-by-side metadata.
>
> Exit criteria: Dashboard renders and deploys to GitHub Pages. Sample gate packet compiles with readable Arabic. Owner can resolve a gate by editing a file in `human_gate/completed/`.
>
> Do NOT proceed to Session 9.

---

### Phase 5: Hardening (Sessions 9-10)

---

#### Session 9 — Factory Acceptance Test

**Type:** CC builder session
**Goal:** Prove every component works, including deliberate failure injection.

**10-point acceptance test:**
1. Autonomous wake-up: scheduled trigger → orchestrator → work unit → CLI dispatch
2. Quality gate enforcement: deliberately failing test → gate blocks
3. Cross-provider review: CC builds → Codex reviews → Gemini challenges (all $0)
4. Policy enforcement: attempt same-provider-only approval → blocked
5. Human gate: ambiguous content → writes to `pending/` → continues other work
6. Dashboard: push → dashboard updates on GitHub Pages
7. Crash recovery: kill orchestrator mid-work → next run recovers
8. Benchmark routing: routing_table.json → correct CLI per task
9. Artifact provenance: every action from tests 1-8 has complete artifact bundle
10. End-to-end: work unit → build → test → gate → review → challenge → complete

---

#### Session 10 — Sustainability + Health Monitoring

**Type:** CC builder session
**Goal:** The factory monitors itself. Degradation is detected before it causes harm.

**Deliverables:**
- `scripts/factory_health.py` — test trends, coverage, costs, routing freshness, Playbook rule expiration, skill freshness, hook integrity, gate queue depth
- `scripts/playbook_revalidation.py` — detects expired rules → generates revalidation work units
- `scripts/factory_self_test.py` — lightweight weekly subset of acceptance test
- `.github/workflows/weekly_health.yml` — scheduled health check

---

## Summary

| Session | Phase | Goal | Effort |
|---------|-------|------|--------|
| 1 | Foundation | Operational truth + doc reconciliation | 1 session |
| 2 | Foundation | CI/CD + policies + hook fixes | 1 session |
| 3 | Foundation | Three-CLI setup + dispatch layer | 1-2 sessions |
| 4 | Benchmark | Arabic benchmark design + construction | 2 sessions |
| 5 | Benchmark | Run benchmark + routing table | 1 session |
| 6 | Orchestration | Work-unit system + orchestrator | 2 sessions |
| 7 | Orchestration | Scheduled execution + recovery | 1 session |
| 8 | Interface | Dashboard + gates + Arabic formatter | 2 sessions |
| 9 | Hardening | 10-point acceptance test | 1 session |
| 10 | Hardening | Health monitoring + sustainability | 1 session |
| **Total** | | | **~14 sessions, $0 incremental** |

### Interleaving with engine work

- After Session 2: resume excerpting with CI protection
- After Session 3: excerpting model research uses all 3 CLIs
- After Session 5: evaluation uses benchmark-routed models
- After Session 7: new engines build through the orchestrator
- After Session 8: owner reviews Arabic through formatted interface

### Revalidation schedule

| Component | Trigger |
|---|---|
| Routing table | New model release OR 90 days |
| Playbook rules | Per-rule `revalidate_by` (max 180 days) |
| Skills | 60-day freshness flag |
| Benchmark | New fixture OR new task type |
| CLI versions | Monthly update check |
| Acceptance test | After any major factory change |

---

## What this plan does NOT include (and why)

1. **No agent society.** Models are bounded workers dispatched by software.
2. **No Claude Chat in the loop.** Requires owner presence → can't be autonomous.
3. **No frozen Arabic model roles.** Blocked on benchmark (Session 5).
4. **No database.** File-based state suffices for single-user.
5. **No speculative integrations.** Usul.ai, KITAB, Swan triggered by evaluation gaps only.
6. **No GSD system.** CC claimed this exists — it doesn't. The orchestrator is built from scratch.
7. **No Agent Teams.** CC claimed these are enabled — they're not. May be added later after verification.
8. **No features CC claimed but couldn't verify.** Every capability in this roadmap was verified against official docs or the actual repo.
