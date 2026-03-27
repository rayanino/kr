# Factory Roadmap — Amendments

**Date:** 2026-03-27
**Authority:** These amendments modify `FACTORY_ROADMAP.md` based on adversarial review findings.
**Severity key:** Each amendment references the finding it addresses.

---

## New Design Decisions

### D-F012: WSL Is the Mandatory Execution Environment

**Addresses:** F-001, F-004
**Rationale:** Codex CLI's Windows support is experimental. Task Scheduler's PATH doesn't include npm globals. Running CLIs natively on Windows is fragile. WSL (Windows Subsystem for Linux) is the proven path — both OpenAI and the community recommend it for Windows Codex users.

**Add to Architecture section:**
> The entire factory runs inside WSL2 (Ubuntu). All three CLIs are installed and authenticated within WSL. The orchestrator runs within WSL. Windows Task Scheduler invokes `wsl.exe python3 /path/to/kr_orchestrator.py` — this is the ONLY Windows-native component. This eliminates PATH issues, sandbox fragility, and platform-specific bugs across all three CLIs.

**Modify Session 3 OWNER ACTION REQUIRED:**
> 1. Ensure WSL2 is installed: `wsl --install` (PowerShell as admin)
> 2. Inside WSL Ubuntu: install Node.js (`nvm install --lts`), Python 3.11+, and Git
> 3. Install Claude Code: `npm i -g @anthropic-ai/claude-code`
> 4. Install Codex CLI: `npm i -g @openai/codex`
> 5. Install Gemini CLI: `npm i -g @google/gemini-cli`
> 6. Authenticate all three inside WSL (tokens persist in WSL filesystem)
> 7. Clone the KR repo inside WSL (`~/kr`, NOT `/mnt/c/...`)
> 8. Verify all three: `claude -p "echo hello" --output-format json`, `codex exec "echo hello" --json`, `gemini -p "echo hello" --output-format json`

### D-F013: Degraded Operation Modes Are Mandatory

**Addresses:** F-002, F-005, F-013
**Rationale:** The factory cannot assume all three CLIs are always available. Rate limits, token expiration, and CLI bugs are normal operating conditions, not edge cases.

**Add to Architecture section:**
> The orchestrator implements three operating modes:
> - **Full (3/3 CLIs):** Normal operation. CC builds, Codex reviews, Gemini challenges.
> - **Reduced (2/3 CLIs):** One CLI unavailable. Factory continues with available CLIs. All work units completed in reduced mode are flagged `reduced_confidence: true` in ops_manifest.json. Owner receives a batch notification.
> - **Minimal (1/3 CLIs — CC only):** Build-only mode. All review is deferred to a review queue. No work unit is auto-approved. Factory alerts owner.
> - **Halted (0/3 CLIs):** Factory writes a halt record to `factory_logs/halt.jsonl` and stops scheduling. Owner must manually restart after fixing the issue.
>
> Mode transitions are logged as artifacts. The dashboard shows current mode prominently.

### D-F014: CLI Version Pinning Is Required

**Addresses:** F-003, F-023
**Rationale:** CLI JSON output schemas change between versions without deprecation periods (documented for Codex CLI). Unpinned CLIs will break the orchestrator's JSON parsing.

**Add to Architecture section:**
> All three CLIs are pinned to specific versions in `factory_config.json`:
> ```json
> {
>   "cli_versions": {
>     "claude_code": "1.x.y",
>     "codex_cli": "0.x.y",
>     "gemini_cli": "0.x.y"
>   }
> }
> ```
> The orchestrator validates CLI versions on startup. Version upgrades are a deliberate operation: update config → run benchmark subset → verify JSON parsing → commit.

### D-F015: PID-Based Lock Files, Not Presence-Based

**Addresses:** F-008
**Rationale:** Presence-based lock files are a known failure mode. If the process crashes, the lock remains, and the factory stops permanently.

**Modify Session 7 deliverable 1:**
> Lock file contains the PID of the running orchestrator. On startup, check if the PID is alive (via `os.kill(pid, 0)` on Linux/WSL). If the PID is dead, remove the stale lock and proceed. Log the recovery.

### D-F016: Factory Operates Intermittently, Not 24/7

**Addresses:** F-014
**Rationale:** The owner is a student. His PC will sleep, restart for updates, and be carried to campus. The factory must be designed for intermittent operation, not 24/7 uptime.

**Add to Architecture section:**
> The factory is designed for **opportunistic execution**, not continuous operation. It runs when the PC is on and WSL is available. It recovers gracefully from any interruption. No work unit depends on completing within a single wake period. The orchestrator's first action on every run is a health check: are CLIs authenticated? Is git clean? Are there stuck work units? The factory makes progress whenever the PC is available and waits patiently when it isn't.
>
> Windows Task Scheduler trigger: "At user logon" + "Every 30 minutes while logged in." NOT "At startup regardless of login."

---

## Session-Specific Amendments

### Session 3 — Additional Exit Criteria

**Add:**
- `wsl codex exec "echo 2+2" --json | jq '.item'` — succeeds from within WSL
- `wsl gemini -p "echo 2+2" --output-format json | jq '.response'` — succeeds from within WSL  
- `wsl claude -p "echo 2+2" --output-format json | jq '.result'` — succeeds from within WSL
- JSON output schemas for all 3 CLIs are documented in `factory_config.json` with example responses
- AGENTS.md total size is under 32 KiB (or `project_doc_max_bytes` is raised in Codex config)
- GEMINI.md Playbook exclusion is verified: dispatch a prompt asking "What does the Decision Playbook say about X?" — Gemini should say it doesn't have access

**Add new deliverable:**
> 6. Create `scripts/cli_health_check.py` — tests all 3 CLIs: auth valid, version matches pinned version, JSON output parseable, response within timeout. Returns structured JSON health report. This is called by the orchestrator on every startup.

### Session 4 — Benchmark Redesign

**Addresses:** F-006, F-020

**Replace "≥5 test cases including ≥1 adversarial case" with:**
> Each task has **≥20 test cases** including ≥5 adversarial cases. Ground truth is hand-verified from multiple independent sources. Adversarial cases are drawn from documented KR failure patterns: compiler-as-muhaqiq (source engine BUG-03), tahqiq-as-commentary, separated refutation-from-position (T-2), silent data loss (T-4), over-confident calibration.

**Add new deliverable to Session 4:**
> 10. Create `benchmarks/cli_confound_test.py` — tests whether benchmark results are measuring the model or the CLI wrapper. Method: for 5 test cases, dispatch the SAME prompt to both the CLI and the raw API (via OpenRouter). Compare results. If they differ significantly, the benchmark is measuring the wrapper, not the model.

**Add to Session 4 exit criteria:**
> - Each task has ≥20 test cases (total ≥180)
> - cli_confound_test.py shows <10% divergence between CLI and API results
> - Confidence intervals for per-task scores are <±15% at 95% confidence

### Session 5 — Routing Table Caveats

**Add to Session 5 deliverables:**
> 4. `RESULTS_ANALYSIS.md` must include: confidence intervals for all scores, explicit acknowledgment of sample size limitations, and a section on "Tasks where all three models agree but ground truth is uncertain" (correlated blindness indicator).

**Add to Session 5 exit criteria:**
> - routing_table.json includes a `confidence` field per task per model (not just a score)
> - Any task where all three models score identically is flagged for human review
> - A `correlated_failure_cases` section lists any test cases where all three models gave the same wrong answer

### Session 6 — Orchestrator Hardening

**Addresses:** F-011, F-013

**Add to Session 6 deliverables:**
> 4. `scripts/context_budget.py` — estimates token count for a work unit's required files. The orchestrator calls this before dispatch. If estimated tokens > 80% of CLI context limit, the work unit is split or pruned.
> 5. The orchestrator implements degraded operation modes (D-F013). Each CLI dispatch is wrapped in a `CLIAvailability` check. Mode transitions are logged.
> 6. The orchestrator validates JSON output against a stored schema (per CLI, per version). Schema mismatches are logged as CRITICAL, not silently retried.

**Modify Session 6 exit criteria:**
> - Orchestrator handles CLI unavailability: simulate Codex timeout → orchestrator transitions to reduced mode → work unit marked `reduced_confidence: true`
> - Context budget check prevents dispatch of over-sized work units

### Session 7 — Scheduling for Intermittent Operation

**Addresses:** F-008, F-009, F-014

**Replace Session 7 deliverable 1 with:**
> 1. `scripts/factory_scheduler.py` — creates Windows Task Scheduler entry via `schtasks /create` that runs `wsl python3 /home/{user}/kr/scripts/kr_orchestrator.py`. Triggers: "At user logon" + "Every 30 minutes while logged in." PID-based lock file prevents concurrent runs. Heartbeat logging to `factory_logs/heartbeat.jsonl`. The scheduler DOES NOT require the PC to be on 24/7 — it runs opportunistically.

**Replace Session 7 deliverable 3 with:**
> 3. `scripts/factory_start.py` — one command from Windows: `wsl python3 ~/kr/scripts/factory_start.py`. Checks prerequisites (Python, Node, 3 CLIs installed and authed in WSL). Creates scheduled task (via PowerShell call to schtasks). Runs initial health check via `cli_health_check.py`. Prints status.

**Add to Session 7 deliverables:**
> 5. The orchestrator uses a separate `factory-ops` branch for auto-commits. Code changes go to working branches. Only human-reviewed work gets merged to main. This prevents git history pollution (F-009).

### Session 9 — Acceptance Test Additions

**Add to the 10-point acceptance test:**
> 11. **Degraded mode operation:** Simulate Codex auth failure → factory transitions to reduced mode → builds continue → review queue grows → Codex auth restored → queued reviews execute
> 12. **Intermittent operation:** Factory runs cycle 1 → kill WSL (simulating PC sleep) → restart WSL → factory recovers and continues from last state
> 13. **CLI version mismatch:** Update Codex CLI to wrong version → factory detects mismatch → refuses to dispatch → alerts owner

---

## New Session: Session 2.5 — WSL Environment Setup

**Insert between Session 2 and Session 3.**

**Type:** Owner setup session (no CC involvement)
**Goal:** WSL2 environment is fully configured and verified.

**Owner does (with architect guidance from Claude Chat):**
1. Install WSL2 with Ubuntu: `wsl --install`
2. Inside WSL: install nvm, Node.js LTS, Python 3.11+, Git
3. Clone KR repo to WSL filesystem: `git clone ... ~/kr`
4. Install all three CLIs inside WSL
5. Authenticate all three CLIs inside WSL
6. Verify all three produce valid JSON output
7. Verify Windows Task Scheduler can invoke `wsl python3 ~/kr/scripts/test_hello.py` and it runs correctly
8. Document all installed versions in `factory_config.json`

**Exit criteria:**
- All 3 CLIs respond to headless prompts from within WSL
- `schtasks` can trigger a WSL Python script successfully
- `factory_config.json` committed with pinned CLI versions

---

## Correlated Blindness Mitigation (F-007)

This is the hardest finding to fix because it's structural — you can't easily detect when all models share a blind spot. The best mitigations are:

1. **Owner Arabic review remains NON-NEGOTIABLE.** The 30-book probe for excerpting, and equivalent probes for each subsequent engine, are the only defense against correlated model errors. The factory can never auto-approve scholarly content, no matter how many models agree.

2. **Add an "uncertainty" signal.** When all three models agree with high confidence on a scholarly claim (author attribution, school classification), AND the claim cannot be verified against a structured reference database, flag it as `correlated_agreement_unverified`. This doesn't detect errors, but it identifies where errors would be undetectable.

3. **Build a reference database over time.** As the owner reviews and approves scholarly output, those verified facts become ground truth. Future factory output is compared against this growing database. Disagreements with verified facts trigger immediate alerts.

4. **Rotate model providers periodically.** When new models launch (Llama 4, Mistral Large, etc.), run a subset of the benchmark to check if they disagree with the current routing. Disagreements are valuable — they reveal potential blind spots in the current roster.
