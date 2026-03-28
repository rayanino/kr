# KR Factory Roadmap v2 — الخطة التشغيلية للمصنع

**Authority:** GOVERNING. Supersedes `reference/FACTORY_ROADMAP.md` (v1, archived).
**Companion document:** `reference/AUTONOMOUS_QUALITY_SYSTEM.md` — defines what the factory does with every minute of runtime (hunting, fixing, evaluating, cross-engine testing). This document covers SETUP. AQS covers OPERATION.
**Version:** 2.0 — Post-adversarial-review
**Written:** 2026-03-27
**Inputs:** Claude Chat adversarial review (7 CRITICAL, 9 HIGH), Claude Code self-critique (21 findings including 3 will-cause-failure), GPT-5.4 independent review (10 failure modes, alternative architecture, benchmark critique, blind-spot analysis). All findings cross-referenced and verified against repo state and official CLI documentation.
**Verification standard:** Every claim about CLI behavior is backed by either `--help` output, official docs, or the existing `scripts/overnight_orchestrator.py` (1,287 lines of battle-tested code). Every claim about repo state is backed by tool execution.

---

## Goal

Build a control plane that autonomously builds, tests, evaluates, and hardens KR engines on the owner's Windows PC. The factory enforces quality through **two independent pillars**:

1. **Process integrity:** Deterministic gates, cross-provider review, policy enforcement, artifact provenance.
2. **Epistemic integrity:** Benchmark-validated model routing, synthesis-level evaluation, structured escalation of ambiguities, and a non-negotiable owner review gate where the owner's growing scholarly expertise is the final arbiter.

**The factory cannot automate past the owner's ability to verify.** Process rigor catches code bugs and policy violations. Only human scholarly judgment catches meaning corruption — flattened disagreements, misread negation, confused quotation-vs-endorsement, and confident-sounding entries that are doctrinally wrong. Both pillars are load-bearing. Neither substitutes for the other.

**"Done" means:** The factory receives a SPEC (written by the architect in Claude Chat) → decomposes it into work units → builds across multiple CC sessions (each fresh from disk state) → verifies via cross-provider CLI review → routes Arabic domain tasks to benchmark-validated models → **escalates ambiguities rather than silently resolving them** → presents the owner with formatted evidence packets for genuine human decisions → produces a proven engine. No message relaying. No protocol memorization. No silent design decisions.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CONTROL PLANE                           │
│  All execution inside WSL2 (Ubuntu). Windows only invokes   │
│  WSL via Task Scheduler. (D-F012)                           │
│                                                             │
│  ops_manifest.json          ← single source of truth        │
│  work_queue/                ← typed work units              │
│  policies/                  ← machine-enforced rules        │
│  artifacts/                 ← immutable provenance bundles  │
│  benchmarks/                ← KR-specific model scores      │
│  routing_table.json         ← benchmark-driven model routes │
│  escalation_queue/          ← unresolved ambiguities (D-F020)│
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │     ORCHESTRATOR (Python — extends overnight v2)      │   │
│  │  Reads state → picks work unit → dispatches CLI       │   │
│  │  → parses per-CLI JSON → runs gates → dispatches      │   │
│  │  review → captures review → persists state            │   │
│  │  → commits to factory-ops branch → schedules next     │   │
│  │  Existing: 1,287 lines, PID locks, heartbeat,         │   │
│  │  5-level gates, circuit breaker, morning report        │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ CLAUDE CODE  │  │  CODEX CLI   │  │  GEMINI CLI  │     │
│  │ (builder)    │  │  (reviewer)  │  │  (adversary) │     │
│  │              │  │              │  │              │     │
│  │ claude -p    │  │ codex exec   │  │ gemini -p    │     │
│  │ --output-    │  │ --full-auto  │  │ --output-    │     │
│  │ format json  │  │ --output-    │  │ format json  │     │
│  │              │  │ last-message │  │              │     │
│  │ Opus 4.6     │  │ GPT-5.4     │  │ Gemini 3.1   │     │
│  │              │  │              │  │              │     │
│  │ CLAUDE.md    │  │ AGENTS.md   │  │ GEMINI.md    │     │
│  │ 19 hooks     │  │ ≤32KiB ctx  │  │ Hierarchical │     │
│  │ 13 skills    │  │ +review cmd │  │ ctx loading  │     │
│  │ 15 rules     │  │             │  │ NO Playbook  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                             │
│  CLI ABSTRACTION LAYER (per-CLI adapter) (D-F017)          │
│  Handles: flag differences, JSON parsing, timeout,          │
│  auth health, version validation, degraded fallback         │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              DETERMINISTIC LAYER                      │   │
│  │  19 hooks + CI/CD + policy engine + contracts         │   │
│  │  pytest · pyright · ruff · D-023 · gates              │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              EPISTEMIC SAFETY LAYER (NEW)             │   │
│  │  Synthesis evaluation tasks · Escalation queue        │   │
│  │  Correlated-agreement detector · Reference DB         │   │
│  │  Owner growth tracking · Known-good state tags        │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                      OWNER LAYER                            │
│  Dashboard (GitHub Pages)   — read-only, auto-refreshed     │
│  Human gate queue           — batched evidence packets      │
│  Escalation queue           — technical decisions (D-F020)  │
│  Arabic output reviewer     — formatted RTL with Amiri font │
│  Growth tracker             — books reviewed, expertise log  │
└─────────────────────────────────────────────────────────────┘
```

---

## Design Decisions

### Retained from v1 (verified robust by all three reviews)

**D-F001: Deterministic control plane, not agent orchestration.** The orchestrator is software that dispatches models. All three reviews confirmed this is correct.

**D-F002: Cross-provider review is structural, not optional.** The builder's provider CANNOT be the sole reviewer. **CAVEAT (GPT review):** Cross-provider review catches implementation errors but does NOT guarantee epistemic correctness. Different providers may share the same training-data blind spots on low-resource Arabic scholarly content. Cross-provider review is a useful heuristic, not a safety guarantee.

**D-F003: Three CLIs at zero marginal cost.** Verified: all three exist with headless JSON output. **CAVEAT:** Each CLI has different flags, output schemas, and platform maturity. The "$0/call" claim depends on subscription terms that can change. Rate limits exist on all three.

**D-F005: Deterministic checks first, models on top.**

**D-F006: State lives in machine-readable files.**

**D-F007: Every nontrivial action produces an immutable artifact bundle.** **AMENDED:** Artifacts are capped at 500KB per bundle. Bundles older than 90 days are archived to `artifacts/archive/` (outside git tracking). The `factory-ops` branch is pruned monthly.

**D-F008: Playbook rules have provenance and expiration.** Revalidation is a human task (owner + architect), not a CLI task.

**D-F009: Claude Code is the sole code modifier.**

**D-F010: Claude Chat has no role in the autonomous loop.** **CLARIFIED:** SPEC writing remains a Claude Chat task (architect + owner). The factory builds FROM SPECs, it does not write them. Design decisions are escalated, not auto-resolved.

**D-F011: Never trust CC self-reports without tool verification.**

### New from v2 (addressing adversarial review findings)

**D-F012: WSL2 is the mandatory execution environment.** (Addresses: Claude F-001, F-004)
Codex CLI Windows support is officially "experimental." Task Scheduler's PATH doesn't include npm globals. All three CLIs are installed, authenticated, and executed within WSL2. Windows Task Scheduler invokes `wsl.exe python3 ~/kr/scripts/kr_orchestrator.py`. This is the ONLY Windows-native component.

**D-F013: Degraded operation modes are mandatory.** (Addresses: Claude F-002, F-005, F-013)
- **Full (3/3 CLIs):** Normal operation.
- **Reduced (2/3 CLIs):** Proceed with available CLIs. Flag all output `reduced_confidence: true`.
- **Minimal (CC only):** Build-only. All review deferred.
- **Halted (0/3):** Stop, alert owner.
Mode transitions are logged. Dashboard shows current mode prominently.

**D-F014: CLI version pinning is required.** (Addresses: Claude F-003, CC JSON schema instability)
Pinned versions in `factory_config.json`. Upgrades are deliberate: update config → run benchmark subset → verify JSON parsing → commit. The orchestrator validates CLI versions on startup.

**D-F015: PID-based lock files.** Already implemented in the existing `overnight_orchestrator.py` lines 344-370. The factory inherits this.

**D-F016: Intermittent operation, not 24/7.** (Addresses: Claude F-014)
The factory runs opportunistically when the PC is on. No work unit depends on completing within a single wake period. Task Scheduler trigger: "Every 30 minutes while logged in." Recovery on wake is automatic.

**D-F017: CLI abstraction layer with verified per-CLI adapters.** (Addresses: CC findings on fabricated flags)
The existing orchestrator already has separate `_execute_cli()` and `_execute_codex()` functions with correct per-CLI flag handling. Verified differences:
| Feature | Claude Code | Codex CLI | Gemini CLI |
|---------|-------------|-----------|------------|
| Headless flag | `-p` | `exec` | `-p` |
| JSON output | `--output-format json` | `--json` (JSONL) or `--output-last-message <FILE>` | `--output-format json` |
| Permissions bypass | `--dangerously-skip-permissions` | `--dangerously-bypass-approvals-and-sandbox` | `--yolo` |
| Structured schema | `--json-schema <inline>` | `--output-schema <FILE>` | N/A (prompt-based) |
| Project context | `CLAUDE.md` (auto) | `AGENTS.md` (auto, ≤32KiB) | `GEMINI.md` (auto, hierarchical) |
| Code review | generic prompt | `codex exec review --base --uncommitted` | generic prompt |
| Context disable | `--bare` (NEVER USE for KR) | N/A | N/A |
The `cli_dispatch.py` module wraps these differences. Callers use a uniform interface.

**MCP server configuration (CC finding #8):** Claude Code headless invocations that need web search must include `--mcp-config` pointing to a JSON config with tavily/context7 servers. Without this, work units requiring web verification silently lack the capability. The CLI adapter handles MCP config injection for work unit types that require it.

**D-F018: Structured response contract between CC and orchestrator.** (Addresses: CC missing requirement #2)
Every work unit defines an expected response schema. CC's output within the `result` field must include:
```json
{
  "status": "complete|partial|blocked|spec_issue",
  "assumptions_made": ["list of ambiguities resolved by inference"],
  "tests_run": 0,
  "tests_passed": 0,
  "files_modified": [],
  "decisions_made": ["list of technical decisions"],
  "needs_escalation": false,
  "escalation_reason": null
}
```
If `assumptions_made` is non-empty OR `needs_escalation` is true, the orchestrator routes to the escalation queue instead of auto-advancing. This is enforced via `--json-schema` where supported, or parsed from the `result` field with validation.

**D-F019: Hook overhead budget and management.** (Addresses: CC finding on 225s worst-case)
The 9 PostToolUse hooks have a cumulative worst-case of 225 seconds per file edit. For build work units, the orchestrator:
- Sets `--allowedTools "Read,Write,Edit,Bash,Grep,Glob"` to control which tools fire
- Uses generous timeouts: `estimated_edits × 120s + base_thinking_time`
- The auto-test hook (`auto-test.sh`, 120s timeout) is the biggest offender — for factory work units, it is conditionally disabled via `CLAUDE_RAPID_MODE=1` env var, with a single full test run at the END of the work unit instead of after every edit

**D-F020: SPEC ambiguity escalation protocol.** (Addresses: CC missing requirement #3, GPT "silent design decisions")
When CC encounters a SPEC ambiguity during autonomous work:
1. CC writes an escalation artifact to `escalation_queue/pending/`
2. CC implements its best interpretation but marks the code with `# ESCALATION: {artifact_id}`
3. The orchestrator detects the escalation, pauses the work unit's review pipeline
4. Codex and Gemini independently evaluate: "Was this the right interpretation?"
5. If all three agree → auto-resolve with artifact record
6. If any disagree → route to owner via human gate
7. The owner resolves with architect guidance in Claude Chat
This prevents silent design decisions from accumulating. GPT correctly identified this as the "confident-wrong" failure mode scaled by automation.

**D-F021: Benchmark independence — CC must not build what CC is evaluated by.** (Addresses: GPT "benchmark self-contamination")
The benchmark (Session 4) is designed by Codex CLI + Gemini CLI, NOT by Claude Code. CC is the evaluated subject, not the evaluator. Ground truth is verified by the owner reading actual Arabic text (with architect guidance), not by model-assisted web search. This eliminates the circular validation loop.

**D-F022: Synthesis-level evaluation tasks in the benchmark.** (Addresses: GPT "ecological validity")
The benchmark must include tasks that test the actual downstream danger: synthesis fidelity. Minimum 3 synthesis tasks: "Given these excerpts, does the synthesis preserve disagreement?" / "Does it distinguish quotation from endorsement?" / "Does it maintain attribution?" These cannot be auto-scored — they require owner judgment, which is the point.

**D-F023: Git state hygiene between work units.** (Addresses: CC missing requirement #5)
The existing orchestrator's `git_is_clean()` + `git_rollback()` pattern is inherited. Between work units: `git reset --hard && git clean -fd` if dirty state is detected. The auto-staging hook (which runs `git add` on every CC file write) is neutralized between work units by the reset.

**D-F024: Owner growth path is a prerequisite, not a side effect.** (Addresses: GPT "owner expertise gap")
The owner's growing scholarly expertise is a LOAD-BEARING component of the factory. The factory cannot produce engines the owner cannot verify. Concretely:
- The owner reviews source engine + normalization output NOW (these engines are done)
- The owner reviews excerpting output during excerpting completion (30-book probe)
- Each review session builds intuition for "what correct output looks like"
- By the time the factory builds taxonomy, the owner has months of reading experience
- The factory tracks owner reviews completed, books reviewed, and escalations resolved in the dashboard
- **No engine is factory-approved without the owner's Arabic review gate.** This is not a bottleneck to be minimized — it is the epistemic safety guarantee.

**D-F025: Known-good state tags for rollback.** (Addresses: Claude F-016)
After every owner-approved review, the repo is tagged `owner-approved-{engine}-{date}`. The factory always builds from the latest owner-approved tag, not from HEAD. If the factory produces bad output, rollback to the last tagged state is a single `git checkout` command.

---

## Model Assignments

| Role | Tool | Model | Cost | Status |
|------|------|-------|------|--------|
| **Builder** | Claude Code | Opus 4.6 | $0 (Max sub) | **LOCKED** — 19 hooks, 13 skills, 15 rules |
| **Architecture reviewer** | Codex CLI | GPT-5.4 | $0 (ChatGPT sub) | **PROVISIONAL** — pending benchmark |
| **Adversarial challenger** | Gemini CLI | Gemini 3.1 Pro | $0 (free tier, rate-limited) | **PROVISIONAL** — pending benchmark |
| **Arabic domain tasks** | Benchmark winner | Per-task routing | $0 (CLI) | **BLOCKED** on benchmark |
| **Deterministic checks** | Software | N/A | $0 | **LOCKED** |
| **Benchmark design** | Codex + Gemini | NOT Claude Code | $0 | **D-F021** |

**Cost model caveat (D-F003, GPT finding):** The "$0/call" depends on subscription terms. Claude Max, ChatGPT Plus/Pro, and Gemini free tier all have usage limits (requests/minute, tokens/day). These are not infinite. The orchestrator tracks usage and implements exponential backoff. If subscription terms change, the fallback is OpenRouter API calls (per-token cost).

---

## Knowledge-Diversity Implementation

- **Codex CLI reviews WITH the Decision Playbook.** AGENTS.md includes Playbook rules. Guided path.
- **Gemini CLI challenges WITHOUT the Decision Playbook.** GEMINI.md excludes Playbook and instructs first-principles reasoning. **STRUCTURAL ENFORCEMENT (CC finding B3):** Gemini's `--disallowedTools` restricts file read access to exclude `reference/DECISION_PLAYBOOK.md`. Instructional exclusion alone is insufficient — capable models override instructions when they decide the Playbook is relevant.
- **Disagreement = strongest signal.** Agreement = higher confidence, but NOT certainty (D-F002 caveat).
- **Correlated agreement on unverifiable claims = flag for human review.** (D-F007 mitigation)

---

## What the Owner Does (Honest Version)

### Setup (one-time, ~2-4 hours with architect guidance)
| Task | Difficulty | Help available |
|------|-----------|---------------|
| Install WSL2 | Run one PowerShell command | Architect provides exact command |
| Install Node.js + Python in WSL | Follow 5-step guide | Architect provides script |
| Install + authenticate 3 CLIs | Run commands, click through OAuth | Architect provides commands + screenshots |
| Verify all 3 CLIs work | Run test commands | Architect provides exact verification commands |
| Set up Task Scheduler | Run setup script | `factory_start.py` automates this |

### Ongoing
| Task | When | Time | Expertise needed |
|------|------|------|-----------------|
| Priority decisions | Per engine transition | ~15 min | None — architect presents options |
| Arabic domain adjudication | When models disagree on scholarly content | ~20 min/batch | Growing — the owner builds expertise over time |
| Arabic output review | Per engine evaluation | ~1-2 hours | Growing — this IS the owner's study process |
| Escalation queue | When factory encounters ambiguities | ~30 min/week | Architect presents context; owner decides |
| Auth refresh | When CLIs report auth failure (~monthly) | ~5 min | Re-run `cli_health_check.py` |
| Factory health check | When dashboard shows warnings | ~10 min | Follow troubleshooting guide |

### The expertise bootstrap problem (GPT finding, addressed honestly)
The owner is an Islamic studies student who hasn't yet studied Islamic texts. KR exists to CREATE that study environment. The factory's quality depends on the owner's judgment, which the owner is still developing. This is a genuine tension. The mitigation:
- **Early engines (source, normalization) have low epistemic risk.** The owner reviews metadata (author, title, edition) — verifiable against book covers.
- **Excerpting has high epistemic risk.** The 30-book probe is where the owner's expertise grows fastest — reading actual scholarly excerpts, judging self-containment, detecting decontextualization. This is both QA and study.
- **Later engines (taxonomy, synthesis) require the expertise built during excerpting review.** The factory does NOT build these until the owner has reviewed excerpting output.

---

## Verified Existing Infrastructure

**Corrected from v1 using CC self-critique (tool-verified):**

**Working and tested:**
- **19 hook entries** (7 PreToolUse, 9 PostToolUse, 2 SessionStart, 1 Stop) — not 13 as v1 claimed
- 13 domain skills in `.claude/skills/`
- 15 rules in `.claude/rules/`
- 21 active agent definitions — not 18 as v1 claimed (CC verified)
- **`scripts/overnight_orchestrator.py` (1,287 lines)** — PID locking, heartbeat, 5-level quality gates (L1-L5), circuit breaker (3 consecutive failures), Codex cross-verification, morning report, graceful SIGINT/SIGBREAK shutdown, PYTHONIOENCODING=utf-8 for Windows, automatic git rollback on gate failure, task recycling
- **`scripts/overnight_task_generator.py` (763 lines)** — task manifest generation
- Correct per-CLI flag handling: `_execute_cli()` for Claude Code, `_execute_codex()` for Codex (different flags)
- GitHub Actions CI — runs pytest + metadata flow + contract validation
- Pre-push test gate (blocks push on test failure)
- Pre-commit conventional commit check

**Broken or needs extension:**
- `circuit-breaker.sh` — uses `/tmp/` (fragile on Windows; moot under WSL but should be project-local)
- `cost-guard.sh` — monitors source engine cost only, not factory operations
- `no-ask-human.sh` — untested in WSL context
- `auto-test.sh` — runs full test suite after every edit (needs CLAUDE_RAPID_MODE suppression)
- No Gemini CLI dispatch function (only Claude + Codex exist in overnight_orchestrator.py)
- No structured response contract (CC returns free text in `result` field)
- No escalation queue for ambiguities
- No benchmark infrastructure
- No factory-ops branch separation

---

## Session-by-Session Roadmap

### Phase 1: Foundation (Sessions 1-3)

#### Session 1 — Operational Truth + Document Reconciliation

**Type:** CC builder session
**Goal:** Create `ops_manifest.json`. Reconcile stale documents with 5-engine pipeline reality.
**Unchanged from v1** except: update hook count to 19, reference `overnight_orchestrator.py` as existing infrastructure.

**CC prompt:** [Same as v1 Session 1, with corrected hook count and orchestrator reference]

**Exit criteria:**
- `python scripts/validate_manifest.py` exits 0
- `grep -rn "7 engines\|6 remaining\|13 hooks" reference/ engines/ CLAUDE.md` returns nothing
- Every Playbook rule has provenance fields
- Git clean, pushed

---

#### Session 2 — CI/CD Hardening + Policy Engine + Hook Fixes

**Type:** CC builder session
**Goal:** Expand CI. Create machine-enforceable policies. Fix broken hooks. Add hook overhead management.

**CC prompt:**

> Read `reference/FACTORY_ROADMAP_v2.md` Session 2. Execute exactly as specified.
>
> Deliverables:
> 1. Expand `.github/workflows/test.yml`: add ruff, black --check, pyright, test stratification with `@pytest.mark.expensive`, cross-engine tests, `validate_manifest.py` as CI step.
> 2. Create `.pre-commit-config.yaml`: ruff, black, pyright, conventional-commits.
> 3. Create `policies/` with JSON policy files: `no_self_approve.json`, `cross_provider_scholarly.json`, `playbook_provenance.json`.
> 4. Create `scripts/check_policies.py` — validates dispositions against policies.
> 5. Fix `circuit-breaker.sh` — use project-local file, not `/tmp/`.
> 6. Fix `auto-test.sh` — respect `CLAUDE_RAPID_MODE=1` to suppress during rapid iteration. Add a single full test run mode for end-of-work-unit.
> 7. Fix `cost-guard.sh` — add factory operations tracking (not just source engine).
> 8. Fix `no-ask-human.sh` — verify under WSL with `KR_OVERNIGHT=1`.
> 9. Document hook overhead budget: create `reference/HOOK_OVERHEAD.md` with per-hook timeout, cumulative worst-case, and recommended `--allowedTools` configurations for different work unit types.
>
> Exit criteria: CI includes ruff + black + pyright + pytest + manifest + contracts. Pre-commit works. All 4 hooks fixed. Hook overhead documented.
>
> Do NOT implement anything beyond these deliverables. Commit and push when complete.

---

#### Session 2.5 — WSL Environment Setup (OWNER ACTION)

**Type:** Owner setup with architect guidance (Claude Chat)
**Goal:** WSL2 fully configured, all three CLIs installed and authenticated.

**The architect provides the owner with:**
1. Exact PowerShell command: `wsl --install`
2. WSL setup script that installs nvm, Node.js LTS, Python 3.11+, Git
3. Exact npm install commands for all three CLIs
4. Authentication walkthrough with screenshots
5. Verification commands with expected output
6. `factory_config.json` template with pinned CLI versions
7. Windows Task Scheduler test: `schtasks /create` that runs `wsl python3 ~/kr/scripts/test_hello.py`

**Exit criteria:**
- All 3 CLIs respond to headless JSON prompts from WSL
- `schtasks` triggers a WSL Python script successfully
- `factory_config.json` committed with pinned versions
- Owner can run `python3 scripts/cli_health_check.py` and all checks pass

---

#### Session 3 — CLI Abstraction Layer + Extend Orchestrator

**Type:** CC builder session
**Goal:** Add Gemini dispatch to existing orchestrator. Build CLI abstraction layer. Create project context files.

**CRITICAL CHANGE FROM v1:** This session EXTENDS `scripts/overnight_orchestrator.py`, not builds from scratch. The existing code has correct Claude + Codex flag handling, PID locking, heartbeat, 5-level gates, circuit breaker, and morning report. The factory adds Gemini dispatch and cross-provider review orchestration on top.

**CC prompt:**

> Read `reference/FACTORY_ROADMAP_v2.md` Session 3. Execute exactly as specified.
>
> CRITICAL: You are EXTENDING `scripts/overnight_orchestrator.py` and `scripts/overnight_task_generator.py`, NOT replacing them. These contain 2,050 lines of battle-tested code with correct per-CLI flag handling, PID locking, heartbeat, quality gates, and circuit breaker. Your job is to add new capabilities, not rewrite existing ones.
>
> Deliverables:
> 1. Add `_execute_gemini()` to the orchestrator, following the same pattern as `_execute_cli()` and `_execute_codex()`. Gemini uses `-p` for headless, `--output-format json` for structured output. Parse the `response` field (not `result` — Gemini's JSON schema differs). Handle `--yolo` for auto-approve.
> 2. Create `shared/factory/cli_adapter.py` — uniform interface: `dispatch(cli: str, prompt: str, cwd: Path, timeout: int, schema: dict | None) -> CLIResult`. Internally delegates to the correct `_execute_*` function. Validates CLI version against `factory_config.json`. Returns structured `CLIResult(status, output, cost, duration, errors, raw_json)`.
> 3. Create `AGENTS.md` (Codex project context): KR overview, 7 corruption threats, quality axiom, SPEC conventions, review protocol, Decision Playbook reference. **MUST be under 32 KiB** (Codex's `project_doc_max_bytes` default). Explicit instruction: "You are a REVIEWER — never modify code."
> 4. Create `GEMINI.md` (Gemini project context): Same KR overview and corruption threats, NO Decision Playbook, explicit first-principles instruction. Configure `--disallowedTools` to structurally prevent reading `reference/DECISION_PLAYBOOK.md`.
> 5. Create `scripts/cli_health_check.py` — tests all 3 CLIs: auth valid, version matches pin, JSON parseable, response within timeout. Returns structured JSON report.
> 6. Create `scripts/test_cross_provider.py` — integration test: CC makes a trivial change → Codex reviews via `codex exec review --base HEAD~1 --uncommitted` → Gemini challenges → all captured as artifacts with full provenance.
>
> Exit criteria: All 3 CLIs respond to headless prompts from within WSL. `test_cross_provider.py` passes. AGENTS.md < 32KiB. GEMINI.md excludes Playbook (verified by grep). Codex `review` subcommand used for review tasks.
>
> Do NOT implement anything beyond these deliverables. Commit and push when complete.

---

### Phase 2: Benchmark (Sessions 4-5)

**CRITICAL CHANGE FROM v1:** The benchmark is designed by Codex + Gemini, NOT by Claude Code. Claude Code is the evaluated subject, not the evaluator. Ground truth requires the owner reading actual Arabic text.

#### Session 4 — Benchmark Design + Construction

**Type:** Multi-CLI session (Codex designs, Gemini challenges, CC implements infrastructure only)
**Goal:** Build a benchmark suite that is independent, statistically meaningful, and tests synthesis fidelity.

**Prerequisite:** Excerpting engine must have produced real output on ≥5 books. The owner must have reviewed at least some of this output. This ensures the benchmark tests real KR tasks, not hypothetical ones.

**Process (NOT a single CC prompt — this is a multi-step process):**

**Step 4a:** The architect (Claude Chat) defines the task taxonomy and minimum case counts. The 12 task types:
1-9: Same as v1 (layer_attribution, school_classification, author_identification, genre_detection, scholarly_function, self_containment, decontextualization, tahqiq_discrimination, death_date_verification)
10. **synthesis_disagreement_preservation** — Given excerpts with opposing views, does the model preserve both sides?
11. **synthesis_quotation_vs_endorsement** — Does the model distinguish "Scholar A quoted Scholar B" from "Scholar A agrees with Scholar B"?
12. **synthesis_attribution_accuracy** — Does a multi-source synthesis correctly attribute each position to its author?

Minimum: **20 test cases per task**, including ≥5 adversarial. Total: ≥240 cases.

**Step 4b:** Owner + architect select test cases from REAL excerpting output (not hypothetical examples). For synthesis tasks, the architect constructs scenarios from actual excerpting results.

**Step 4c:** Codex CLI designs the adversarial cases and ground truth verification methodology. Dispatch via orchestrator:
```
codex exec "Read benchmarks/TASK_SPEC.md. Design adversarial test cases for each task type. 
For each case: provide the input, expected output, and the reasoning for why this is adversarial. 
Do NOT design cases for tasks you will later be evaluated on — design cases that test the OTHER models." 
--output-last-message benchmarks/adversarial_cases.md
```

**Step 4d:** Gemini CLI independently reviews the adversarial cases and proposes additions:
```
gemini -p "Read benchmarks/adversarial_cases.md. Are these cases actually adversarial? 
What failure modes do they miss? Propose 3 additional cases per task that Codex missed." 
--output-format json
```

**Step 4e:** The owner verifies ALL ground truth by reading actual Arabic text. For each case: "Is this ground truth correct?" Model-assisted web verification is a supplement, not a substitute.

**Step 4f:** CC builds the benchmark infrastructure ONLY (scorer, runner, reporting). CC does NOT design test cases or verify ground truth.

**Exit criteria:**
- ≥240 test cases across 12 tasks (≥20 per task)
- ≥3 synthesis-level evaluation tasks
- All ground truth verified by owner reading Arabic (documented in sign-off file)
- CLI confound test exists: `benchmarks/cli_confound_test.py` compares CLI vs raw API for 10 cases
- No test case was designed by the same CLI that will be evaluated on it
- Scorer produces per-task breakdown with confidence intervals

---

#### Session 4.5 — Synthetic Adversarial Data Infrastructure

**Type:** CC builder session
**Goal:** Build the hunting infrastructure described in `reference/AUTONOMOUS_QUALITY_SYSTEM.md`.

**CC prompt:**

> Read `reference/AUTONOMOUS_QUALITY_SYSTEM.md` in full. Execute Session 4.5 exactly as specified.
>
> Deliverables:
> 1. `synthetic_tests/` directory structure per AQS spec.
> 2. `scripts/synthetic_generator.py` — dispatches Codex/Gemini CLI with threat templates via cli_adapter, validates output JSON, stores in synthetic_library.
> 3. `scripts/synthetic_runner.py` — takes a synthetic case, formats it as pipeline input, runs through target engine, compares output against ground truth, produces PASS/FAIL with divergence details.
> 4. `scripts/finding_classifier.py` — auto-classifies findings by threat type (from template), severity (from divergence type), engine, and SPEC section.
> 5. `findings_db/` directory structure: pending/, in_progress/, resolved/, patterns/, metrics/, synthetic_library/ (with T-1/ through T-7/ subdirs + cross-engine/ + full-pipeline/).
> 6. `findings_db/templates/` — one JSON template per threat type (T-1 through T-7), plus one cross-engine template for normalization→excerpting, plus one full-pipeline template. Total: 9 templates. Use the exact specifications from AQS Section "Threat templates."
> 7. Integration test: generate one synthetic T-2 case via Codex → run through excerpting → compare → produce finding → classify → store in findings_db.
>
> Exit criteria: End-to-end hunt cycle works (generate → run → compare → classify → store). All 9 templates exist and are valid JSON. findings_db structure matches AQS spec.
>
> Do NOT implement anything beyond these deliverables. Commit and push when complete.

---

#### Session 5 — Run Benchmark + Routing Table

**Type:** CC runs benchmark script, architect analyzes
**Goal:** Score all three CLIs. Produce routing table with confidence intervals and caveats.

**Exit criteria:**
- All 3 CLIs scored on all 12 tasks
- Confidence intervals computed (must be ≤±15% at 95% for any routing decision)
- `routing_table.json` includes `confidence` field per task per model
- `correlated_agreement_cases` documented: any case where all 3 gave the same wrong answer
- CLI confound test shows <10% divergence (or routing table notes the confound)
- `RESULTS_ANALYSIS.md` explicitly states what the benchmark DOES and DOES NOT prove

---

### Phase 3: Orchestration (Sessions 6-7)

#### Session 6 — Extend Orchestrator + Response Contracts + Escalation

**Type:** CC builder session
**Goal:** Add work-unit decomposition, response contracts, escalation queue, and degraded modes to the EXISTING orchestrator.

**CC prompt:**

> Read `reference/FACTORY_ROADMAP_v2.md` Session 6. Execute exactly as specified.
>
> You are EXTENDING `scripts/overnight_orchestrator.py`. The existing code handles: CLI dispatch (Claude + Codex + now Gemini from Session 3), PID locking, heartbeat, 5-level quality gates, circuit breaker, morning report, git rollback. You are adding NEW capabilities on top.
>
> Deliverables:
> 1. `work_queue/schema.json` — work unit definition with fields: id, type (implement|review|challenge|benchmark|escalation), engine, spec_section, inputs[], expected_outputs[], response_schema (the D-F018 contract), assigned_cli, status, blocked_by[], policy, artifact_ids[], created_at, completed_at.
> 2. Add work-unit dispatch to the orchestrator: reads `work_queue/`, picks next unblocked unit, dispatches via `cli_adapter.py`, validates response against D-F018 contract, checks for escalations.
> 3. Create `escalation_queue/` directory with `pending/`, `resolved/`. When CC's response has `assumptions_made` or `needs_escalation`, the orchestrator writes an escalation artifact and pauses the pipeline for that work unit.
> 4. Implement degraded operation modes (D-F013) in the orchestrator: health-check each CLI before dispatch, transition modes on failure, log transitions.
> 5. Add context budget check: estimate tokens for work unit inputs, warn if >500K.
> 6. Add hook overhead budget: for work units with many expected edits, set `CLAUDE_RAPID_MODE=1` and run tests once at end.
> 7. Integration test: create a trivial work unit → orchestrator dispatches CC → validates response contract → dispatches Codex review → dispatches Gemini challenge → escalation detection works → all artifacts saved.
>
> Exit criteria: Work unit flows through full cycle. Response contract validated. Escalation detection works. Degraded mode transitions work. Context budget check prevents oversized dispatches.
>
> Do NOT implement anything beyond these deliverables. Commit and push when complete.

---

#### Session 7 — Scheduled Execution + Recovery

**Type:** CC builder session + owner runs setup
**Goal:** Factory runs on a timer, recovers from interruptions, operates intermittently.

**CC prompt:**

> Read `reference/FACTORY_ROADMAP_v2.md` Session 7. Execute exactly.
>
> Deliverables:
> 1. `scripts/factory_scheduler.py` — creates Windows Task Scheduler entry: `schtasks /create` runs `wsl python3 ~/kr/scripts/kr_orchestrator.py` every 30 minutes while user is logged in. NOT "at startup regardless of login."
> 2. `scripts/factory_recovery.py` — on startup: check for stuck work units (in_progress with dead PID), roll back to pending, log recovery.
> 3. `scripts/factory_start.py` — owner runs from Windows: `wsl python3 ~/kr/scripts/factory_start.py`. Checks prerequisites, creates scheduled task, runs health check, prints status.
> 4. The orchestrator uses a `factory-ops` branch for auto-commits. Code changes go to working branches. Only owner-reviewed work merges to main via `owner-approved-*` tags (D-F025).
> 5. Artifact pruning: bundles older than 90 days → `artifacts/archive/` (outside git).
>
> Exit criteria: `factory_start.py` creates scheduled task (verify via `schtasks /query`). Factory wakes, runs, commits to factory-ops. Kill mid-work → next run recovers. Lock prevents concurrent runs. Artifact pruning works.
>
> Do NOT implement anything beyond these deliverables. Commit and push when complete.

---

### Phase 4: Interface (Session 8)

#### Session 8 — Dashboard + Human Gate + Arabic Formatter + Growth Tracker

**Type:** CC builder session
**Goal:** Owner sees everything. Arabic is readable. Escalations arrive as evidence packets. Owner growth is tracked.

**Deliverables (same as v1 plus):**
1-5: Same as v1 (dashboard, GitHub Pages, human gate, gate packet compiler, Arabic formatter)
6. `scripts/generate_escalation_packet.py` — takes a technical escalation → produces a readable evidence packet: the ambiguity, CC's interpretation, Codex's assessment, Gemini's assessment, recommended resolution, specific question for the owner.
7. Owner growth tracker in the dashboard: books reviewed, escalations resolved, review sessions completed, months of Arabic reading.
8. Correlated-agreement detector in dashboard: highlights cases where all 3 models agreed on a claim that couldn't be independently verified.

---

### Phase 5: Hardening (Sessions 9-10)

#### Session 9 — Factory Acceptance Test

**15-point acceptance test** (expanded from v1's 10):
1. Autonomous wake-up from Task Scheduler
2. Quality gate enforcement (failing test → blocked)
3. Cross-provider review cycle (CC → Codex → Gemini)
4. Policy enforcement (same-provider-only → blocked)
5. Human gate (ambiguous content → pending/)
6. **Escalation queue (SPEC ambiguity → escalation artifact → paused pipeline)**
7. Dashboard deploys on push
8. Crash recovery (kill mid-work → next run recovers)
9. **Degraded mode (simulate Codex auth failure → reduced mode → builds continue → review queued)**
10. Benchmark routing (routing_table.json → correct CLI)
11. Artifact provenance (every action has bundle)
12. **Intermittent operation (kill WSL → restart → factory recovers)**
13. **CLI version mismatch detection**
14. **Context budget rejection (oversized work unit → rejected before dispatch)**
15. End-to-end: work unit → build → test → gate → review → challenge → complete

---

#### Session 10 — Health Monitoring + Sustainability

Same as v1 plus:
- `scripts/factory_health.py` includes: CLI auth freshness, rate limit proximity, hook overhead trends, escalation queue depth, owner growth metrics, correlated-agreement count
- Playbook revalidation generates dashboard alerts, NOT automated work units (revalidation is a human task)
- Weekly health subset of acceptance test

---

## Interleaving With Engine Work

**The factory does NOT delay engine work. It runs alongside it.**

| Timeline | Engine work | Factory work |
|----------|------------|--------------|
| Now | Excerpting: model role research (NEXT.md Task 1) | Sessions 1-2 (safe, independent) |
| Week 1-2 | Excerpting: 5-book LLM integration test | Owner: WSL setup (Session 2.5) |
| Week 3-4 | Excerpting: 30-book owner probe | Session 3 (CLI setup) |
| Week 5-6 | Excerpting: completion + owner review | Sessions 4, 4.5 (benchmark + synthetic infra) |
| Week 7-8 | — | Sessions 5, 6 (benchmark run + orchestrator modes) |
| Week 9-10 | Factory hunts excerpting 24/7 | Session 7 (scheduler) |
| Week 11-12 | Factory hunts excerpting to Level 3+ | Sessions 8-10 (interface + hardening) |
| Week 13+ | Taxonomy: SPEC design (Claude Chat) | Factory hunts excerpting continuously |
| Week 15+ | Taxonomy: factory-built (first real job) | Factory hunts BOTH engines |

**The critical insight:** After excerpting is complete, the factory spends weeks hunting it before taxonomy even starts. By the time taxonomy SPEC design begins, excerpting has been stress-tested against hundreds of synthetic adversarial cases. The owner has been reading excerpting output. The factory has been fixing bugs. This is the quality-first sequencing GPT-5.4 called for.

---

## What This Plan Does NOT Include (and Why)

1. **No agent society.** Models are workers dispatched by software.
2. **No Claude Chat in the autonomous loop.** Requires owner presence.
3. **No frozen Arabic model roles.** Blocked on benchmark (Session 5).
4. **No database.** File-based state suffices for single-user.
5. **No 24/7 operation.** Designed for intermittent use by a student.
6. **No automated SPEC writing.** SPECs are written by the architect (Claude Chat) with the owner. The factory builds FROM SPECs.
7. **No automated scholarly approval.** Cross-provider review catches code bugs. Only the owner catches meaning corruption. This is by design.
8. **No CC-designed benchmark.** The evaluated model family does not design its own test bed.
9. **No "ACCEPT WITH FIXES" on factory output.** The factory's quality gates produce PASS or FAIL. Failed work units are retried or escalated, never hand-waved.
10. **No confidence without evidence.** Model agreement is a heuristic, not a guarantee. The routing table includes confidence intervals, not just scores.

### Why three CLIs instead of one CLI + API judges (GPT alternative)

GPT-5.4 proposed: one code-modifying tool (CC), one orchestrator, API-level judges for review, human merge gate, staging branch. This is simpler and more stable.

We keep three CLIs because: (a) CLI-based review reads the full repo context automatically (AGENTS.md, GEMINI.md), which API-level judges would need manually constructed prompts for; (b) Codex's `codex exec review` subcommand is purpose-built for code review and more capable than generic API prompting; (c) the existing orchestrator already handles Claude + Codex dispatch. However, the v2 adopts GPT's recommendations for: staging branch (factory-ops), human merge gate (owner-approved tags), and the principle of benchmarking models separately from CLI wrappers (confound test).

**If the three-CLI approach proves too fragile in practice (auth failures, rate limits, breaking updates), the fallback is exactly GPT's architecture:** CC as sole builder, OpenRouter API calls for cross-provider review (using Instructor + Pydantic for structured output), human merge gate. This fallback uses the project's existing OpenRouter infrastructure and requires no CLI dependencies beyond Claude Code.

---

## Revalidation Schedule

| Component | Trigger |
|---|---|
| Routing table | New model release OR 90 days |
| Playbook rules | Per-rule `revalidate_by` (max 180 days) — HUMAN review |
| CLI versions | Monthly version check in `factory_health.py` |
| Benchmark | New fixture OR new task type OR new model |
| Acceptance test | After any major factory change |
| Owner growth | Tracked continuously in dashboard |

---

## Risk Register (NEW — all three reviews)

| Risk | Likelihood | Impact | Mitigation | Residual risk |
|------|-----------|--------|------------|--------------|
| Correlated model blindness on Arabic content | HIGH | CRITICAL | Owner review gate + reference DB over time + model rotation | Medium — owner expertise is still growing |
| CLI subscription terms change | MEDIUM | HIGH | OpenRouter API fallback + cost tracking | Low |
| SPEC ambiguities silently resolved | HIGH | CRITICAL | D-F018 response contract + D-F020 escalation | Low — structurally prevented |
| Benchmark doesn't predict real quality | MEDIUM | CRITICAL | Synthesis tasks + owner verification + ecological validity check | Medium — synthesis eval is inherently hard |
| Owner doesn't review output deeply enough | MEDIUM | CRITICAL | Growth tracking + escalation packets + study integration | Medium — depends on owner engagement |
| Auth tokens expire overnight | HIGH | MEDIUM | D-F013 degraded modes + health check on wake | Low |
| Hook overhead kills work unit productivity | HIGH | HIGH | D-F019 budget + RAPID_MODE + end-of-unit testing | Low |
| Factory produces engines faster than owner can verify | LOW | HIGH | Factory paces to owner review capacity; never auto-approves scholarly content | Low |
