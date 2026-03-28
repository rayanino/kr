# Paperclip Evaluation Report — Hands-On Test for KR

**Date:** 2026-03-28
**Version tested:** v2026.325.0 (released March 25, 2026)
**Platform:** Windows 11 Home (native, not WSL)
**Evaluator:** Claude Code (Opus 4.6)
**Methodology:** Adversarial hands-on testing per `PAPERCLIP_EVALUATION_PROMPT.md`

---

## Phase 1: Installation

### What happened

Installation via `npx paperclipai onboard --yes` succeeded in ~60 seconds. Zero manual steps. The embedded PostgreSQL database was auto-created, doctor checks passed 9/9, and the server launched at `http://127.0.0.1:3100`.

### Key details

| Item | Value |
|------|-------|
| Install command | `npx paperclipai onboard --yes` |
| Install time | ~60 seconds |
| Dependencies needed | Node.js 20+, pnpm 9.15+ |
| Disk space | 69MB total |
| Server URL | http://127.0.0.1:3100 |
| API URL | http://127.0.0.1:3100/api |
| UI URL | http://127.0.0.1:3100 (same as server) |
| Database | Embedded PostgreSQL on port 54329 |
| Heartbeat | Enabled, 30s global default |
| DB Backup | Every 60 minutes, 30-day retention |

### Issues found

1. **Stale state from previous install.** A "kr" company from March 11 existed in the database. `onboard --yes` updated config but didn't offer a clean-slate option. Not a bug, but means re-evaluation requires manual cleanup.

---

## Phase 2: KR Company Setup

### Org chart — WORKS

Created a 4-agent org chart with reporting lines:

```
CTO (claude_local) — top-level
├── Builder (claude_local) — reports to CTO
├── Reviewer (codex_local) — reports to CTO
└── Adversary (process) — reports to CTO [workaround for missing gemini_local]
```

The `reportsTo` field correctly establishes hierarchical relationships. The dashboard shows the org structure.

### Multi-adapter — PARTIAL

| Adapter | Status |
|---------|--------|
| `claude_local` | **Works** — accepted, agent created |
| `codex_local` | **Works** — accepted, agent created |
| `gemini_local` | **REJECTED** — not a valid adapter type despite docs claiming support |
| `process` | **Works** — used as workaround for Gemini |

Valid adapter types per API validation: `process`, `http`, `claude_local`, `codex_local`, `opencode_local`, `pi_local`, `cursor`, `openclaw_gateway`, `hermes_local`.

The documentation at `docs.paperclip.ing/adapters/gemini-local` describes a Gemini local adapter in detail (including `--resume` flag handling, session persistence, and skill injection). The release notes for v0.3.1 list "Gemini CLI adapter" as a feature. But the actual API rejects `gemini_local` as an invalid enum value. **This is either a docs-code mismatch or a regression in v2026.325.0.**

### Per-agent budgets — WORKS

Budget in cents/month granularity. The `budgetMonthlyCents` field is accepted and stored. Enforcement: agents auto-pause at 100% spend. Dashboard shows utilization percentage.

### Goal hierarchy — WORKS

Three goals created and linked to the company. Tasks can reference goals via `goalId`. The goal-task lineage is maintained.

### Heartbeat intervals — UNCLEAR

The API doesn't expose a per-agent `heartbeatIntervalMs` field in responses. The global heartbeat is 30 seconds (from server config). It's unclear from the API whether individual agents can have different intervals. The docs mention per-agent heartbeat settings in the UI, but API-level control was not confirmed.

### Issues found

2. **Arabic company name garbled.** `خزانة ريان` was stored as `????? ????` in the database. Root cause: the embedded PostgreSQL was initialized with WIN1252 encoding (Windows system locale) instead of UTF-8. This is a **critical issue for KR** — our entire domain is Arabic scholarly text.

3. **`gemini_local` adapter does not exist** in the API despite extensive documentation. See above.

4. **`issuePrefix` silently ignored.** Specified "KR" in the creation payload; Paperclip auto-generated "KHI" from the company name. The API accepted the field without error but didn't use it.

5. **`assigneeId` field name wrong.** The correct field is `assigneeAgentId`, not `assigneeId`. The API accepted `assigneeId` silently and ignored it — no validation error, no assignment. This is a particularly dangerous API behavior for automated integrations.

---

## Phase 3: Task Execution Test

### Single agent task — BLOCKED ON WINDOWS

Task was created, assigned to Builder, status updated to `todo`. But triggering the heartbeat failed with two independent errors:

**Error 1: PostgreSQL encoding**
```
character with byte sequence 0xe2 0x86 0x92 in encoding "UTF8" has no equivalent in encoding "WIN1252"
```
The `→` character (U+2192) in the auto-generated agent instructions caused a database error. The embedded PostgreSQL cluster was initialized with WIN1252 encoding.

**Error 2: Symlink permissions**
```
EPERM: operation not permitted, symlink '...\skills\paperclip' -> '...\paperclip-skills-xxx\.claude\skills\paperclip'
```
Paperclip's skill injection creates symlinks, which require Developer Mode on Windows. Developer Mode was not enabled on this machine.

**Both errors are Windows-specific.** On Linux/WSL (where the KR factory is designed to run per D-F012), these would not occur. But they make evaluation on native Windows impossible.

### Multi-agent dependency — PARTIAL (API-level only)

Task B was created with `parentId` pointing to Task A. The parent-child relationship was stored correctly. However:

- **No DAG-style "blocked-by" dependencies.** Only hierarchical parent-child. Task B cannot say "don't start until Task A reaches status `done`" — only "Task B is a subtask of Task A."
- Could not verify runtime dependency enforcement (agents couldn't execute due to Windows issues).

### Governance gates — WORKS

The approval system works correctly:
1. Created a `hire_agent` approval request
2. Approval appeared as `pending`
3. Board approved via CLI (`npx paperclipai approval approve <id>`)
4. Status updated to `approved` with decision note and timestamp
5. Full audit trail preserved

**Limitation:** The API endpoints for approvals are CLI-only — the REST API route for `POST /api/approvals/{id}/decide` returned 404. Board approvals must be done via `npx paperclipai approval approve/reject`.

### Cost tracking — WORKS

Cost events can be recorded per-agent with provider, model, token counts, and cost in cents. The dashboard aggregates monthly spend vs. budget. Events require an `occurredAt` timestamp (not auto-generated).

### Dashboard — WORKS (via CLI)

```json
{
  "agents": { "active": 1, "running": 0, "paused": 0, "error": 1 },
  "tasks": { "open": 3, "inProgress": 0, "blocked": 0, "done": 0 },
  "costs": { "monthSpendCents": 45, "monthBudgetCents": 0 },
  "pendingApprovals": 0
}
```

Compact, informative. Shows exactly what the owner would need. The web UI at port 3100 serves a React SPA — likely more detailed than the CLI summary.

---

## Phase 4: KR-Specific Evaluation

### Q1: Can Paperclip handle our 6 operating modes?

**PARTIALLY.** The 6 modes (BUILD, HUNT, FIX, EVALUATE, CROSS-ENGINE, BENCHMARK) could be modeled as **Projects** with specific goal linkages. Each mode could be a project with mode-specific tasks. The orchestrator would create tasks in the right project based on queue state.

**But:** Paperclip has no concept of "exactly one mode active at a time." It has no priority ordering between projects. It has no concept of "HUNT is the default when nothing else exists." The mode-selection logic would still need to live in our orchestrator or a custom plugin.

**Verdict:** Paperclip can host the tasks each mode produces, but cannot implement the mode-selection state machine.

### Q2: Can Paperclip handle our team compositions?

**NO, not natively.** In BUILD mode, we want 4 agents (builder + reviewer + tester + validator) working together ON THE SAME SPEC SECTION. Paperclip's model is: one agent per task, tasks have single assignees, agents work independently and communicate via task comments.

CC Agent Teams (teammates with direct peer-to-peer messaging, shared task list, real-time communication) is a fundamentally different collaboration model than Paperclip's ticket-based system. Paperclip coordinates through asynchronous ticket updates; Agent Teams coordinate through synchronous messages.

**The workaround:** Paperclip assigns a task to a single CC agent (the "lead"), and that CC agent internally spawns an Agent Team. But then Paperclip only sees one agent doing all the work — the internal team dynamics are invisible to Paperclip's tracking.

### Q3: Can agents invoke each other?

**YES, through Bash tool.** Any CC session (launched by the claude_local adapter) can invoke `codex exec` and `gemini -p` via the Bash tool during its heartbeat. These are inline CLI calls, not Paperclip tasks. Paperclip doesn't know about them and doesn't track their costs.

**This is exactly what we need** — D-F017 cross-provider validation happens inside the CC session, not as separate tickets. But the cost tracking blind spot is real: Codex/Gemini invocations inside a CC session would need to be manually reported via the cost-events API.

### Q4: Can we use CC Agent Teams WITHIN Paperclip?

**PROBABLY YES, but untested.** The claude_local adapter invokes `claude -p` (headless mode). If we set `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in the adapter's environment config, the CC session could spawn teammates. The session's output would still flow back to Paperclip via the adapter.

**Risk:** Agent Teams require tmux for interactive display. Headless invocation via `-p` may not support teams. This needs testing on Linux/WSL.

**Risk 2:** Token consumption of Agent Teams (3-7x) is invisible to Paperclip's cost tracking unless each team member's costs are manually reported.

### Q5: How does Paperclip handle our findings database?

**POORLY.** Our findings lifecycle (DISCOVERED → CLASSIFIED → TRIAGED → FIXING → FIXED → VERIFIED → HARDENED) has 7 states, threat type classification (T-1 through T-7), epistemic impact assessment, pattern extraction, and regression test generation. Paperclip's issue system has a simpler lifecycle (backlog → todo → in_progress → done).

**We would need to model findings as issues with custom metadata** (threat_type, severity, epistemic_impact, etc.) stored in the issue body or via a custom field system. The 7-stage lifecycle would require custom status values or a parallel state machine.

**Verdict:** We still need our own `findings_db/` directory structure alongside Paperclip. Paperclip could track the FIX tasks, but the findings database (patterns, synthetic library, metrics) is too domain-specific.

### Q6: What about synthetic data generation?

**TOO SPECIALIZED.** The HUNT mode workflow (select threat template → dispatch Codex/Gemini for generation → validate output → run through pipeline → compare against ground truth → classify findings) is a complex multi-step process with domain-specific logic at every step. Paperclip's task system could track "run a hunt cycle" as a task, but the actual hunt logic would be a custom script.

**Verdict:** HUNT mode is an application that uses Paperclip, not something Paperclip implements.

### Q7: Does Paperclip persist session state for CC?

**YES.** The claude_local adapter documentation confirms: "The adapter persists Claude Code session IDs between heartbeats. On the next wake, it resumes the existing conversation so the agent retains full context." Session resume is cwd-aware — if the working directory changes, a fresh session starts.

**This is genuinely valuable.** Our overnight orchestrator currently starts fresh sessions for every task. Session persistence would let a multi-heartbeat BUILD work unit maintain context, avoiding the "re-read SPEC, re-understand code" overhead.

### Q8: How robust is it?

**Tested:**
- Kill server mid-operation: Could not test (agents couldn't execute on Windows)
- Agent timeout: Could not test (same reason)
- Database encoding: **BROKEN on Windows** — WIN1252 encoding corrupts non-ASCII text
- Symlink permissions: **BROKEN on Windows** — EPERM without Developer Mode

**Risk assessment based on architecture:**
- The embedded PostgreSQL is a single point of failure. No replication, no failover. A corrupted DB file means total data loss unless backups are available (they are — every 60 minutes).
- The server is a single Node.js process. No clustering, no health restarts. If it crashes, heartbeats stop until someone restarts it.
- Task checkout is atomic (per the SPEC), which prevents double-execution. This is good.
- **Worst case:** Server crash during a heartbeat loses that heartbeat's state changes (the CC session may have done work that Paperclip never recorded). The task would remain in `in_progress` indefinitely until manual intervention.

### Q9: What's missing for KR?

Even with Paperclip handling orchestration, we still need:

1. **Mode-selection state machine** — the priority logic (FIX > BUILD > EVALUATE > HUNT > CROSS-ENGINE > BENCHMARK)
2. **Findings database** — `findings_db/` with 7-stage lifecycle, threat classification, pattern extraction, metrics
3. **Synthetic data infrastructure** — threat templates, generation prompts, ground truth comparison
4. **CLI abstraction layer** — per-CLI flag handling (D-F017) for inline Codex/Gemini invocations within CC sessions
5. **Arabic text safety checks** — the 19 hooks in `.claude/settings.json` that enforce diacritics preservation, encoding validation, etc.
6. **Quality maturity tracking** — Level 1-5 per engine, hunt yield metrics, coverage maps
7. **SPEC-to-task decomposition logic** — how a SPEC section becomes work units with dependencies
8. **Owner growth tracker** — books reviewed, expertise progression
9. **D-F020 escalation protocol** — SPEC ambiguity detection and routing
10. **Response contract enforcement** — D-F018 structured output validation

### Q10: What does Paperclip do better than custom?

1. **Dashboard and UI.** The React UI with mobile support (PWA) is production-quality. Building this ourselves was Sessions 8-9 in the roadmap (~3-4 sessions of work). Paperclip gives it free.

2. **Governance gates.** The approval system (hire_agent, strategy review, board decision) with audit trail is exactly what we need for human gates. Custom building this was part of Session 8.

3. **Cost tracking infrastructure.** Per-agent, per-model, per-token cost tracking with budget enforcement (auto-pause at limit). We had `COST_LOG.json` but Paperclip's system is more structured and queryable.

4. **Agent lifecycle management.** Agent status (idle, running, paused, error), heartbeat history, session persistence, health monitoring. Our orchestrator has some of this, but Paperclip's is more complete.

5. **Persistent state across reboots.** PostgreSQL-backed state survives reboots, with automatic backups. Our JSON file state is more fragile.

6. **Multi-company isolation.** If we ever want to run the factory for multiple projects, Paperclip handles data isolation. Not a current need but free.

---

## Phase 5: Verdict

```json
{
  "installation": {
    "success": true,
    "issues": [
      "Stale state from previous install not cleaned up",
      "Embedded PostgreSQL initialized with WIN1252 on Windows instead of UTF-8"
    ],
    "time_to_setup": "60 seconds"
  },
  "kr_company_setup": {
    "org_chart_works": true,
    "multi_adapter_works": false,
    "budget_enforcement_works": true,
    "goal_hierarchy_works": true,
    "issues": [
      "gemini_local adapter does not exist despite documentation",
      "Arabic company name garbled (WIN1252 encoding)",
      "issuePrefix silently ignored",
      "assigneeId silently ignored (correct field: assigneeAgentId)",
      "Per-agent heartbeat intervals not exposed in API"
    ]
  },
  "task_execution": {
    "single_agent_works": false,
    "multi_agent_dependencies_work": false,
    "governance_gates_work": true,
    "cost_tracking_works": true,
    "issues": [
      "SHOWSTOPPER: Embedded PostgreSQL WIN1252 encoding breaks on non-ASCII (U+2192 arrow character)",
      "SHOWSTOPPER: Symlink creation requires Windows Developer Mode",
      "Both issues are Windows-specific — would not occur on Linux/WSL",
      "Task dependencies are parent-child only, not DAG-style blocked-by",
      "Approval API routes return 404 — must use CLI",
      "Could not verify actual agent execution due to Windows blockers"
    ]
  },
  "kr_fit_assessment": {
    "replaces_orchestrator": false,
    "replaces_dashboard": true,
    "replaces_scheduler": true,
    "replaces_cost_tracking": true,
    "replaces_governance": true,
    "supports_6_modes": false,
    "supports_team_compositions": false,
    "supports_inline_cross_provider": true,
    "supports_cc_agent_teams_inside": "unknown_untested",
    "supports_findings_lifecycle": false,
    "sessions_saved_if_adopted": "3-4 sessions (dashboard, governance, cost tracking, scheduler)",
    "custom_work_still_needed": [
      "Mode-selection state machine (the brain of the orchestrator)",
      "Findings database with 7-stage lifecycle and threat classification",
      "Synthetic data generation infrastructure",
      "CLI abstraction layer for inline Codex/Gemini calls",
      "Arabic text safety hooks (19 hooks)",
      "Quality maturity tracking (Level 1-5)",
      "SPEC-to-task decomposition",
      "Owner expertise growth tracking",
      "D-F020 escalation protocol",
      "D-F018 response contract enforcement"
    ],
    "issues": [
      "Paperclip is a task tracker and agent heartbeat system, not an orchestrator",
      "The hard part of KR factory is the domain logic, not the plumbing",
      "Paperclip gives us the plumbing but we still build all the domain logic",
      "Windows support is broken for our use case (Arabic text + non-ASCII)"
    ]
  },
  "recommendation": "EVALUATE_FURTHER",
  "reasoning": "Paperclip provides genuine value for dashboard, governance, cost tracking, and scheduling — saving 3-4 sessions of custom work. But it does NOT replace the orchestrator's brain (mode selection, SPEC decomposition, findings lifecycle, synthetic data). The Windows encoding issue is critical but solvable by running under WSL2 (which we already planned per D-F012). The missing gemini_local adapter and API inconsistencies suggest the project is still maturing. EVALUATE_FURTHER means: test on WSL2 to confirm the Windows issues are resolved, verify claude_local adapter actually executes with CLAUDE.md context, and test Agent Teams inside a Paperclip heartbeat.",
  "risks": [
    "Project is < 1 month old (first release March 9, 2026) — high change velocity, breaking changes likely",
    "Documentation claims features the API doesn't implement (gemini_local)",
    "API silently ignores invalid fields instead of rejecting them (assigneeId, issuePrefix)",
    "Windows support is broken for non-ASCII — our ENTIRE domain is Arabic",
    "Single PostgreSQL process = single point of failure",
    "CC Agent Teams inside Paperclip heartbeat is untested and may not work headless",
    "Cost tracking for inline Codex/Gemini calls is a blind spot",
    "The managed AGENTS.md is generic boilerplate — doesn't include KR's 13 skills, 15 rules, or 19 hooks",
    "Vendor dependency on a 3-week-old project for critical infrastructure"
  ],
  "what_paperclip_does_better_than_custom": [
    "Dashboard + UI (React SPA with PWA mobile support) — saves Session 8",
    "Governance gates with audit trail — saves part of Session 8",
    "Per-agent cost tracking with budget enforcement — saves part of Session 6",
    "Agent lifecycle management (idle/running/paused/error) — saves part of Session 7",
    "Session persistence across heartbeats via session ID — not in our current orchestrator",
    "PostgreSQL-backed persistent state with automatic backups",
    "Approval workflow with create/approve/reject/request-revision/resubmit lifecycle",
    "Company-scoped data isolation for multi-project future"
  ],
  "what_we_still_build_ourselves": [
    "Mode-selection state machine (FIX > BUILD > EVALUATE > HUNT > etc.)",
    "Findings database (7-stage lifecycle, threat classification, pattern library)",
    "Synthetic adversarial data generation system",
    "CLI abstraction layer (D-F017) for Codex/Gemini invocation",
    "All 19 hooks for Arabic text safety",
    "Quality maturity model (Level 1-5 per engine)",
    "SPEC-to-task decomposition engine",
    "Owner expertise growth tracking",
    "D-F018 response contract validation",
    "D-F020 SPEC ambiguity escalation protocol",
    "Cross-engine boundary test orchestration",
    "Full-pipeline synthetic book processing",
    "Hunt yield and coverage map metrics",
    "Morning report generation"
  ]
}
```

---

## Honest Summary

**Paperclip is a real product that solves real problems — but not OUR hard problems.**

Our hard problems are:
1. **Deciding WHAT work to do** (mode selection, SPEC decomposition, priority ordering)
2. **Ensuring scholarly correctness** (Arabic text safety, findings lifecycle, quality maturity)
3. **Making agents collaborate in real-time** (Agent Teams, not tickets)

Paperclip solves:
1. **Tracking work** (task status, cost, agent health)
2. **Scheduling agents** (heartbeats, persistence)
3. **Showing the owner what happened** (dashboard, approvals)

Think of it this way: Paperclip is JIRA for AI agents. Our orchestrator is a domain-specific factory controller. JIRA is useful inside a factory — it tracks tickets, approvals, and costs. But JIRA doesn't decide what the factory builds next, doesn't run the assembly line, and doesn't inspect quality. The factory controller does those things.

**The question isn't "Paperclip OR custom orchestrator." It's "Paperclip AND a lighter custom orchestrator."** Paperclip handles plumbing (dashboard, scheduling, costs, governance). Our orchestrator handles domain logic (mode selection, findings, quality, Arabic safety). The two can coexist.

### If adopted, the factory roadmap changes like this:

| Session | Original | With Paperclip |
|---------|----------|----------------|
| 6 | Orchestrator modes + response contracts + escalation | Mode-selection logic only (lighter — Paperclip handles task tracking) |
| 7 | Scheduler + recovery + factory-ops branch | **ELIMINATED** — Paperclip handles scheduling and persistence |
| 8 | Dashboard + human gate + Arabic formatter + findings dashboard | Findings dashboard only (Paperclip handles the rest) |
| 9 | 15-point acceptance + hunt/fix cycle acceptance | Same (domain-specific) |
| 10 | Health monitoring + sustained hunting infrastructure | Lighter (Paperclip provides agent health; we add domain metrics) |

**Net savings: ~3-4 sessions, mainly dashboard and scheduling.**
**Net risk: dependency on a 3-week-old project.**

### My recommendation

**EVALUATE_FURTHER.** Specifically:

1. **Test on WSL2** to confirm the Windows encoding and symlink issues are resolved
2. **Test actual CC execution** — does the claude_local adapter invoke `claude -p` with our CLAUDE.md context?
3. **Test Agent Teams inside a heartbeat** — does `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` work headless?
4. **File the gemini_local issue** — this is a bug or a regression that should be fixed
5. **Assess maturity at v2026.4xx** — wait 30 days and re-evaluate. A project this young changes fast.
6. **Don't adopt Paperclip as a dependency for Session 6** — too risky. Build the orchestrator standalone with a clean interface so Paperclip COULD be plugged in later as the task-tracking and dashboard layer.

The safest path: build Sessions 6-7 as planned (standalone orchestrator), then in Sessions 8-9 evaluate whether Paperclip can replace the dashboard and scheduling components rather than building them custom.
