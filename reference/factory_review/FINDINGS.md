# Factory Roadmap — Adversarial Findings

**Date:** 2026-03-27
**Reviewer:** Claude Chat (Architect), adversarial mode
**Subject:** `FACTORY_ROADMAP.md` stress-test across 5 lenses
**Methodology:** Pre-mortem, implementation walk-through, CLI capability research, benchmark validity audit

---

## Summary

The Factory Roadmap contains a sound high-level architecture — deterministic control plane, cross-provider review, benchmark-routed model assignment — but has **7 CRITICAL** and **9 HIGH** findings that would cause failure within 2-4 months of deployment. The most dangerous cluster is around the three-CLI integration layer (Sessions 3, 6, 7), where the roadmap assumes capabilities that are either experimental, rate-limited, or absent on the owner's Windows platform.

---

## CRITICAL Findings (Roadmap will fail without addressing)

### F-001: Codex CLI Windows Support Is Experimental — Not Production-Ready

**Lens:** Implementation walk-through (Session 3)
**Evidence:** OpenAI's own documentation states: *"The Codex CLI is available on macOS and Linux. Windows support is experimental."* The Windows sandbox has two modes (elevated and unelevated), both with documented failure modes: error 1385 (logon type denied), enterprise policy blocks, missing writable roots. The Codex desktop app launched Mac-only in February 2026; Windows users are on a waitlist.
**Source:** https://developers.openai.com/codex/cli, https://developers.openai.com/codex/windows
**Impact:** The factory's cross-provider review depends on Codex CLI running reliably on the owner's Windows PC at 3 AM unattended. An "experimental" platform cannot serve as infrastructure for an autonomous factory. Any Windows-specific sandbox failure silently blocks the review pipeline.
**Current mitigation in roadmap:** None. Session 3 says "owner assists with Codex/Gemini authentication" but doesn't acknowledge the experimental status.

### F-002: Gemini CLI Free Tier Has Rate Limits That Will Throttle the Factory

**Lens:** Implementation walk-through (Session 3, 6)
**Evidence:** Gemini CLI free tier allows 60 requests/minute and 1,000 requests/day. The factory runs every 30 minutes. If a single orchestration cycle dispatches 3-5 Gemini calls (challenge + sub-challenges), that's 144-240 calls/day minimum. Add benchmark runs, re-challenges on disagreements, and the factory will hit the daily cap within the first week of real operation.
**Source:** https://codelabs.developers.google.com/gemini-cli-hands-on (authentication section)
**Impact:** The roadmap claims "$0/call" for Gemini CLI. This is true only if you never hit rate limits. Once throttled, the adversarial challenger goes silent — and the factory doesn't know the difference between "Gemini found no issues" and "Gemini was rate-limited."
**Current mitigation in roadmap:** None. No rate limit handling anywhere.

### F-003: Codex CLI JSON Output Schema Is Unstable — Already Broke Once

**Lens:** Implementation walk-through (Session 6)
**Evidence:** GitHub issue #4776 (October 2025): the `codex exec --json` output changed field names from `item_type` to `type` and `assistant_message` to `agent_message` between versions, without a deprecation period. The issue author called this a "contract break." Additionally, issue #4219 (September 2025) reported that Codex CLI "either panics or blocks" in non-TTY headless environments.
**Source:** https://github.com/openai/codex/issues/4776, https://github.com/openai/codex/issues/4219
**Impact:** The orchestrator's JSON parsing layer (`cli_dispatch.py`) will break on Codex CLI updates. Since the factory auto-updates CLIs (or the owner updates manually), a single Codex update can silently break the entire review pipeline. The orchestrator will see parse failures, retry once (per roadmap), then log failure — but the work unit is stuck.
**Current mitigation in roadmap:** "Error handling: timeout, non-zero exit, invalid JSON → retry once → log failure." This handles the symptom but not the cause. No version pinning. No schema validation.

### F-004: Windows Task Scheduler Cannot Find npm-Installed CLIs

**Lens:** Implementation walk-through (Session 7)
**Evidence:** Windows Task Scheduler runs tasks in a different user context with a different PATH environment. npm global installs go to `%APPDATA%\npm`, which is user-specific and NOT in the system PATH. When Task Scheduler runs `python scripts/kr_orchestrator.py`, the orchestrator calls `claude`, `codex`, and `gemini` — but these commands are npm-installed and their paths aren't available in the scheduler's execution context. This is a well-documented Windows problem — the Node-RED docs, multiple Stack Overflow threads, and the ESRI Python scheduling guide all describe it.
**Source:** https://nodered.org/docs/getting-started/windows, https://joshuatz.com/posts/2020/using-windows-task-scheduler-to-automate-nodejs-scripts/
**Impact:** The factory starts, creates the scheduled task, and... nothing happens. The orchestrator launches, tries to call `codex exec`, gets "command not found," logs a failure, and exits. Every 30 minutes. Forever. The owner sees nothing because there's no alerting system yet (Session 8).
**Current mitigation in roadmap:** None. Session 7 says "factory_start.py checks prerequisites (Python, Node, 3 CLIs installed and authed)" but checking them in the user's interactive shell doesn't verify they work in the scheduler's context.

### F-005: Authentication Tokens Expire — No Refresh Mechanism

**Lens:** Pre-mortem + Implementation walk-through
**Evidence:** All three CLIs use OAuth/API-key authentication:
- Claude Code: Anthropic Max subscription token (refreshes via browser?)
- Codex CLI: ChatGPT OAuth token (documented: `codex login` uses device auth; tokens stored in `~/.codex/auth.json` — "Treat auth.json like a password")
- Gemini CLI: Google OAuth token (via browser-based auth flow on first run)

OAuth tokens expire (typically 1 hour for access tokens, longer for refresh tokens, but refresh tokens also expire eventually or get revoked). When the factory runs at 3 AM and a token expires, the CLI returns an auth error. The orchestrator sees a failure, retries once, logs it, and moves on. The factory is now partially blind.
**Source:** Codex non-interactive mode docs (https://developers.openai.com/codex/noninteractive) explicitly notes: "CODEX_API_KEY is only supported in codex exec. For interactive sessions, use codex login."
**Impact:** The factory degrades silently. No cross-provider review means CC self-approves its own work. This is the exact failure mode D-F002 was designed to prevent.
**Current mitigation in roadmap:** None. No token refresh mechanism, no auth health check, no degradation handling.

### F-006: The Benchmark Measures CLI Wrappers, Not Models — And 5 Cases Per Task Is Statistically Meaningless

**Lens:** Benchmark validity audit
**Evidence:** Session 4 designs a benchmark with 9 tasks, ≥5 test cases each, dispatched via `cli_dispatch.py` to each CLI. But each CLI adds its own system prompt, tool-use patterns, context management, and output formatting on top of the base model. The benchmark scores the CLI+model compound, not the model. If Codex CLI's system prompt happens to emphasize code review patterns that help with layer_attribution, the benchmark credits GPT-5.4 — but the real cause is Codex's system prompt, which could change with any CLI update. Additionally, 5 test cases per task gives wide confidence intervals. For a binary classification task with 5 samples, even a perfect score has a 95% CI of [57%, 100%] by the Clopper-Pearson method.
**Source:** Statistical reasoning; Arabic NLP benchmark survey (https://arxiv.org/abs/2510.13430) shows established benchmarks use hundreds to thousands of test cases.
**Impact:** The routing table (Session 5) is built on noise, not signal. Model role assignments based on 45 total test cases (9 tasks × 5 cases) have almost no statistical power. The factory routes Arabic scholarly tasks to models based on essentially random variation.
**Current mitigation in roadmap:** Session 4 exit criteria says "All ground truth verified via web search" — but doesn't address sample size or the CLI-wrapper confound.

### F-007: No Detection of Correlated Model Blindness (Same Wrong Answer From All Three)

**Lens:** Pre-mortem + Implementation walk-through (Session 6)
**Evidence:** The factory's quality model assumes cross-provider review catches errors because different providers have different blind spots (D-F002). But frontier models are increasingly trained on similar data (web text, code, academic papers). For Arabic scholarly text — a low-resource domain — all three models may share the same training data gaps. If Opus, GPT-5.4, and Gemini 3.1 all incorrectly attribute a text to the same author because they all learned from the same incorrect Wikipedia article, the factory's three-way agreement registers as high confidence.
**Impact:** The most dangerous errors are the ones all three models agree on. The factory has no mechanism to detect this. The owner, who cannot validate domain content independently, trusts the factory's "all three agree" signal — and learns a false belief.
**Current mitigation in roadmap:** D-F002 says "Different providers = different training data = different blind spots." This is an assumption, not a verified property, and it's weakest exactly where KR needs it most: low-resource classical Arabic scholarly content.

---

## HIGH Findings (Significant risk that should be mitigated)

### F-008: Lock File Stale After Crash — Classic Windows Problem

**Lens:** Implementation walk-through (Session 7)
**Evidence:** Session 7 uses a lock file to prevent concurrent orchestrator runs. If the orchestrator crashes (Python exception, OOM, power loss), the lock file remains. The next scheduled run sees the lock and skips. Every subsequent run skips. The factory is permanently stopped until someone manually deletes the lock file.
**Impact:** Silent factory death. No alerting exists until Session 8.
**Fix:** Use PID-based locking: write the PID to the lock file, and on startup check if that PID is still running. This is standard practice.

### F-009: Git History Pollution — 1,000+ Auto-Commits in 20 Days

**Lens:** Implementation walk-through (Session 7)
**Evidence:** The orchestrator commits to git after every cycle. At 30-minute intervals, that's 48 commits/day, 1,440/month. After 3 months: 4,320 commits. The git history becomes unnavigable. `git log` is useless. `git blame` points to orchestrator commits, not meaningful changes. Bisecting regressions becomes impractical.
**Impact:** The factory's own provenance trail destroys the repo's usability for human review and debugging.
**Fix:** Use a separate `factory-ops` branch for orchestrator state commits. Squash-merge into main only on meaningful milestones. Or use the artifact ledger for provenance and only commit code changes.

### F-010: Codex CLI Default Sandbox Is Read-Only — Can't Review Code That Requires Execution

**Lens:** Implementation walk-through (Session 3, 6)
**Evidence:** `codex exec` defaults to a read-only sandbox. The orchestrator dispatches review tasks to Codex. But a meaningful code review often requires running tests, executing the code, or inspecting runtime behavior. In read-only mode, Codex can only do static analysis. The roadmap doesn't specify what sandbox mode the orchestrator should use for Codex.
**Impact:** Code reviews are shallow — Codex reads the code but can't verify it works. This defeats the purpose of cross-provider review for implementation correctness.
**Fix:** Specify `--sandbox workspace-write` or `--full-auto` in the Codex dispatch for review tasks that require test execution. Add this to the orchestrator's dispatch configuration.

### F-011: The Orchestrator's Context Budget Is Unplanned

**Lens:** Implementation walk-through (Session 6)
**Evidence:** When the orchestrator dispatches a work unit to CC via `claude -p`, it must include: the prompt, relevant SPEC sections, the code being reviewed, test results, and context files (CLAUDE.md). A single SPEC is 2,387 lines. The full engine code is ~4,850 lines. CLAUDE.md + contracts + test output can easily add 3,000+ lines. Total: 10,000+ lines = ~40K+ tokens just for input. CC headless mode retains ~200K tokens, but the response budget, thinking budget, and tool-use budget all compete for that space.
**Impact:** Large work units may silently exceed context limits. CC truncates input or produces shallow responses without explicit failure. The orchestrator sees a "completed" work unit with a degraded response.
**Fix:** Add context budgeting to work unit design. Each work unit specifies required files and their token estimates. The orchestrator validates total context before dispatch.

### F-012: `project_doc_max_bytes` Limits AGENTS.md to 32 KiB by Default

**Lens:** Implementation walk-through (Session 3)
**Evidence:** Codex CLI limits project instruction loading to 32 KiB by default (`project_doc_max_bytes`). The roadmap plans to put KR overview, 7 corruption threats, quality axiom, SPEC conventions, review protocol, and Decision Playbook reference into AGENTS.md. The current CLAUDE.md alone is ~4 KiB, but a proper KR context file with all the above would easily exceed 32 KiB.
**Source:** https://developers.openai.com/codex/guides/agents-md
**Impact:** Codex silently truncates the project instructions. It reviews code without knowing about corruption threats T-1 through T-7. It misses the very domain knowledge that makes cross-provider review valuable.
**Fix:** Either raise `project_doc_max_bytes` in Codex config, or split AGENTS.md into a root file + subdirectory files that Codex loads hierarchically.

### F-013: No Degraded-Mode Operation — Factory Is All-Or-Nothing

**Lens:** Pre-mortem
**Evidence:** If one CLI is down (auth expired, rate limited, broken update), the factory has no fallback. It can't say "Gemini is unavailable, proceeding with CC + Codex only, flagging for human review." It simply logs a failure and the work unit stalls.
**Impact:** Single-CLI failures cascade into full factory stalls. The factory's uptime is the MINIMUM of all three CLIs' uptimes — which, given experimental Windows support (F-001) and rate limits (F-002), could be quite low.
**Fix:** Define degraded operation modes: 2-of-3 CLIs → proceed with reduced confidence + flag. 1-of-3 → implement only, queue all review for next cycle. 0-of-3 → halt and alert owner.

### F-014: The Owner's Windows PC Must Stay On 24/7

**Lens:** Pre-mortem
**Evidence:** The factory runs via Windows Task Scheduler on the owner's personal Windows PC. This means: the PC must never sleep, never restart for updates (Windows Update is aggressive), never lose network. The owner is a student — PCs get closed, carried to campus, put to sleep. Windows 10/11 forces restarts for updates.
**Impact:** The "autonomous 24/7 factory" requires the owner to manage infrastructure (keep PC running, disable auto-sleep, manage Windows Update). This contradicts the roadmap's promise that "the owner intervenes only for: reading Arabic scholarly output, making priority/preference decisions, and periodic audit sampling."
**Fix:** Either: (a) acknowledge this limitation and add "keep PC running" to owner tasks, (b) use a cloud VM ($5-10/month), or (c) design the factory for intermittent operation (resumes gracefully after PC wake).

### F-015: Playbook Revalidation Creates Infinite Work

**Lens:** Pre-mortem
**Evidence:** D-F008 requires every Playbook rule to have `revalidate_by` (max 180 days). Session 10 builds `playbook_revalidation.py` to detect expired rules and generate revalidation work units. But who revalidates? The factory dispatches revalidation to CLIs. CLIs don't have the context to know if a rule is still valid — they'd need empirical testing or domain expertise. The revalidation work unit either gets auto-approved (defeating the purpose) or stalls in the human gate queue.
**Impact:** The Playbook accumulates expired rules that nobody reviews. Or the factory generates a growing backlog of revalidation work units that consume CLI budget without producing value.
**Fix:** Revalidation should be a human task, not a CLI task. Flag expired rules on the dashboard. Let the owner + architect review them during planning sessions.

### F-016: No Rollback Mechanism When Factory Produces Bad Output

**Lens:** Pre-mortem
**Evidence:** The factory builds engines autonomously. If it ships a bad engine (passes all automated gates but produces wrong scholarly output), there's no rollback to the last known-good state. The orchestrator commits continuously. The owner discovers the problem days or weeks later during Arabic review. By then, the factory has built on top of the bad engine.
**Impact:** A single undetected quality failure cascades forward through all subsequent work. The factory optimizes for gate-passing, not for actual scholarly quality.
**Fix:** Tag known-good states as git tags after owner review. The factory always builds from the latest owner-approved tag, not from HEAD.

---

## MEDIUM Findings (Worth addressing but not blocking)

### F-017: Session Ordering Blocks Engine Work for ~14 Sessions

The roadmap says "After Session 2: resume excerpting with CI protection" but Sessions 1-3 are prerequisites for Sessions 4-5, which are prerequisites for 6-7. In practice, the factory isn't usable until Session 7. That's ~7-10 sessions (2-3 weeks of daily work) before the factory does anything useful. Meanwhile, the excerpting engine is blocked on model role research (NEXT.md Task 1).

### F-018: GEMINI.md Exclusion of Playbook May Not Work in Headless Mode

The roadmap says GEMINI.md "explicitly excludes Playbook access." But Gemini CLI loads ALL GEMINI.md files from the directory hierarchy. If DECISION_PLAYBOOK.md exists in the repo, Gemini can still read it via file tools during its session. The exclusion is instructional ("don't use the Playbook") not mechanical ("can't access the Playbook").

### F-019: No Cost Tracking for CLI Operations

The roadmap claims "$0/call" for all three CLIs. But: Claude Code Max has usage limits (not unlimited), ChatGPT Plus has Codex limits, and Gemini free tier has daily caps. None of these are truly unlimited. The factory should track usage against these soft limits.

### F-020: The 9 Benchmark Tasks Miss Key KR Failure Modes

The benchmark includes decontextualization (T-2) but doesn't include: silent data loss (T-4), over-confidence calibration, multi-chunk boundary detection, or the specific failure of treating editorial footnotes as scholarly commentary (BUG-03 from source engine). The benchmark tests the tasks the architect thought of, not the tasks that have historically caused failures.

---

## LOW Findings (Nice to have)

### F-021: Dashboard on GitHub Pages Exposes Factory State Publicly

Unless the repo is private, the dashboard exposes work queue state, test results, benchmark scores, and potentially Arabic scholarly content to the public internet.

### F-022: Artifact Bundles Will Consume Significant Disk Space

Every CLI dispatch produces an artifact bundle with full prompt, output, and metadata. At 48 dispatches/day, with average bundle size of 50-100 KiB, that's 2.4-4.8 MB/day, 72-144 MB/month. Git doesn't handle large binary-like JSON well.

### F-023: No Mechanism to Detect When a CLI's Base Model Changes

If OpenAI silently updates GPT-5.4 (e.g., a safety patch that changes Arabic handling), the routing table becomes stale. The benchmark scores were measured against the old model. The factory continues routing based on outdated scores.

---

## Lens Survival Assessment

For each roadmap section that survived the attack, here's WHY it's robust:

**D-F001 (Deterministic control plane):** Robust. The alternative — agent orchestration — is demonstrably worse. GPT-5.4's independent review confirmed this. The Python orchestrator is the right architecture.

**D-F005 (Deterministic checks first):** Robust. The existing 13 hooks + CI pipeline is proven infrastructure. The factory layers on top of this, it doesn't replace it.

**D-F006 (State in machine-readable files):** Robust. ops_manifest.json as single source of truth is correct. File-based state for single-user is appropriate.

**D-F009 (CC sole code modifier):** Robust. The KR codebase was built with CC's conventions. Letting other CLIs modify code would create style conflicts and break hooks.

**D-F010 (No Claude Chat in autonomous loop):** Robust. This is a genuine constraint — Claude Chat requires the owner's presence. Removing it from the loop is the right call.

**D-F011 (Never trust CC self-reports):** Robust. Empirically validated — CC fabricated capabilities in this very planning phase.

**Session 1 (Operational truth):** Robust. Document reconciliation is the right first step. The deliverables are concrete and verifiable.

**Session 2 (CI/CD hardening):** Robust. Expanding CI is high-value, zero-risk work.

**Session 8 (Dashboard + Arabic formatter):** Design is sound. RTL formatting with Amiri font is the right approach for the owner.
