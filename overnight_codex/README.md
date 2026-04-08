# KR Autonomous System v1

The KR autonomous system runs unattended overnight to discover quality issues, generate research prompts, and maintain a structured knowledge base. It connects three layers: **task execution** (Codex CLI in worktrees), **knowledge digestion** (DR response processing + finding extraction), and a **web dashboard** for monitoring.

## Quick Start

```bash
# Start everything (dashboard + Codex tasks + KB bridge)
python scripts/launch_autonomous.py --hours 6

# Just view the dashboard (no tasks)
python scripts/launch_autonomous.py --dashboard-only

# Ingest existing results into KB without running new tasks
python scripts/launch_autonomous.py --ingest-only

# Process a Deep Research response
python scripts/digest_dr.py path/to/response.md --dr-id DR40
```

Dashboard at `http://localhost:8000` after launch.

## Architecture

```
                        launch_autonomous.py
                       /         |          \
              Dashboard    Codex Orchestrator    KB Bridge
             (FastAPI)     (worktree tasks)    (codex_kb_bridge.py)
                |                |                    |
           localhost:8000   results/            findings.jsonl
                             /    \             ideas.jsonl
                     final_response  creative   research_gaps.jsonl
                            |          |        contradictions.jsonl
                            v          v              |
                      KB Bridge ──────────────> backlog.json
                            |                   (auto-promote)
                     Cross-reference
                            |
                     Follow-up prompts ──> DR Relay Queue
                            |
                     Owner relays to DR ──> digest_dr.py ──> cycle
```

## Components

### Layer 1: Task Execution

| Script | Lines | Purpose |
|--------|-------|---------|
| `overnight_codex_orchestrator.py` | 2,652 | Runs Codex CLI tasks in isolated git worktrees with circuit breakers, timeouts, and quality gates |
| `overnight_codex_task_generator.py` | 732 | Generates task packets from backlog items and creative templates |
| `overnight_codex_common.py` | 574 | Shared constants, paths, utilities (RESULTS_DIR, repo_rel, safe_slug) |
| `overnight_codex_backlog.py` | 515 | Canonical backlog management (load/save/dedupe/sync/promote) |

**Worktree isolation:** Every task runs in a disposable git worktree (`overnight_codex/worktrees/`). Read-only tasks are discarded after results are copied. Write tasks are gated through the backlog approval system.

**Creative templates:** `overnight_codex/creative_templates/innovation/` contains task templates for architecture challenges, cost efficiency reviews, and failure mode analysis. Each has cooldown periods to prevent repetition.

### Layer 2: Knowledge Base Digestion

| Script | Lines | Purpose |
|--------|-------|---------|
| `autonomous_schemas.py` | 419 | Pydantic models: Finding, Idea, ResearchGap, DRPrompt, DRResponse, Contradiction, etc. |
| `codex_kb_bridge.py` | 1,072 | Converts Codex results to KB findings + runs 3 data bridges (see below) |
| `cross_reference_findings.py` | 386 | Detects related findings and contradictions across sources |
| `generate_followup_prompts.py` | 395 | Creates DR prompts from gaps and contradictions |
| `digest_dr.py` | 296 | Processes raw DR response files into structured findings |
| `process_dr_response.py` | 304 | Section extraction and finding parsing from DR markdown |
| `dr_format_detectors.py` | 271 | Auto-detects DR provider (ChatGPT/Claude/Gemini) from format |
| `digestion_quality_gate.py` | 351 | PASS/WARN/FAIL quality assessment on digestion runs |
| `analyze_overnight_run.py` | 336 | Post-run analysis and morning report generation |

### Layer 3: Dashboard

| File | Purpose |
|------|---------|
| `autonomous_dashboard/app.py` | FastAPI app with 7 pages |
| `autonomous_dashboard/store.py` | Data access layer for all KB JSONL files |
| `autonomous_dashboard/templates/` | Jinja2 templates (relay, findings, contradictions, ideas, digestion, status, error) |

### Unified Launcher

`launch_autonomous.py` (219 lines) starts all layers with one command. Options:

| Flag | Effect |
|------|--------|
| `--hours N` | Run duration (default: 4) |
| `--no-dashboard` | Headless mode |
| `--dashboard-only` | View-only, no tasks |
| `--ingest-only` | Bridge existing results, no new tasks |

## The Three Bridges

`codex_kb_bridge.py` runs three data-flow bridges after every ingestion:

### Bridge 1: Creative -> Ideas

Scans `results/creative-*/` for creative task output. Extracts ideas from `action_items` and `findings` fields. Persists as `Idea` records in `knowledge_base/ideas.jsonl`. Deduplicates by idea_id.

### Bridge 2: Gap Scanner -> Research Gaps

Greps all `engines/*/SPEC.md` files for `[OPEN: ...]` markers. Parses `KNOWN_LIMITATIONS.md` files for `L-NNN` entries. Creates `ResearchGap` records in `knowledge_base/research_gaps.jsonl`. Deduplicates by gap_id.

### Bridge 3: Findings -> Backlog Promotion

Reads CONFIRMED HIGH/CRITICAL findings that have a non-empty `action_required` field. Auto-promotes them to `overnight_codex/backlog.json` so the next Codex run can act on them. Uses the existing backlog dedupe and subsystem-inference logic.

## Cross-Model Verification (D-041)

All HIGH/CRITICAL findings start as `PRELIMINARY`. The bridge attempts verification via:
1. **Anthropic API** (preferred when `ANTHROPIC_API_KEY` is set) -- direct SDK call to `claude-sonnet-4-6`
2. **OpenRouter API** (fallback when `OPENROUTER_API_KEY` is set) -- Anthropic verifier model via `https://openrouter.ai/api/v1/chat/completions`

A finding becomes `CONFIRMED` (verifier agrees) or `DISPUTED` (verifier disagrees). Only CONFIRMED findings are eligible for backlog promotion.

## Data Layout

```
overnight_codex/
  backlog.json                          # Canonical backlog (5 items)
  state.json                            # Orchestrator state
  manifest.json                         # Task manifest
  events.jsonl                          # Event log
  creative_run_log.json                 # Creative task cooldown tracker
  MORNING_REPORT.md                     # Latest overnight summary
  progress.md                           # Human-readable progress
  results/                              # Per-task result directories
    spec-audit-excerpting/
      final_response.json               # Codex output
      audit.json                        # Task-specific artifacts
      packet.json                       # Input packet
  creative_templates/
    innovation/                         # Creative task templates
      local_architecture_challenge.json
      local_cost_efficiency.json
      local_failure_mode_review.json
  autonomous/
    knowledge_base/
      findings.jsonl                    # 244 findings (all sources)
      research_gaps.jsonl               # 13 gaps (from KNOWN_LIMITATIONS)
      ideas.jsonl                       # Idea quarry (created on first creative run)
      contradictions.jsonl              # 47 cross-source contradictions
      dr_responses.jsonl                # 35 processed DR responses
      digestion_log.jsonl               # 35 digestion records
      dr_prompts/                       # Generated relay prompts by batch
  worktrees/                            # Disposable task worktrees (gitignored)
```

## Operating Model

### Authority Boundaries

- **May do:** Bounded hardening, local structural analysis, test coverage checks, SPEC audits, creative challenges, KB management.
- **May NOT do:** Own architecture, roadmap, SPECs, or Claude-facing operational files. May not touch `.claude/`, `overnight/`, `docs/superpowers/`, `CLAUDE.md`, or `NEXT.md`.

### Safety Mechanisms

- **Worktree isolation:** Tasks cannot modify the main checkout directly.
- **Backlog gates:** Write tasks require `approved` status before execution.
- **Circuit breakers:** Orchestrator stops after repeated failures.
- **Live session detection:** If a Claude session is active, forces queue-only mode.
- **Dirty repo detection:** If main repo has uncommitted changes, write tasks queue as patches instead of auto-applying.
- **Budget enforcement:** `cost-guard.sh` hook blocks API calls when budget is exhausted.

### WSL Bootstrap

For running overnight on Windows via WSL:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/overnight_codex_wsl_resume.ps1 -RunShadowRehearsal
```

This calls `scripts/overnight_codex_wsl_bootstrap.sh` inside WSL, syncs the checkout to `~/kr-codex`, mirrors auth state, and launches a safe queue-only shadow rehearsal.

## Known Issues (v1)

1. **Verification credentials must exist somewhere:** the bridge is now API-only. If neither `ANTHROPIC_API_KEY` nor `OPENROUTER_API_KEY` is configured, HIGH/CRITICAL findings remain `PRELIMINARY`.
2. **No creative results yet:** No `creative-*` task directories exist because creative tasks haven't been scheduled. Bridge 1 is ready but has no input data.
3. **Backlog promotion still depends on confirmation throughput:** HIGH/CRITICAL findings only promote after a verifier returns `CONFIRMED`. If the verifier path is healthy, Bridge 3 will auto-promote confirmed findings to the backlog on the next ingest run.

## Development

```bash
# Type-check
python -m pyright scripts/codex_kb_bridge.py

# Run bridge manually
python scripts/codex_kb_bridge.py              # Full ingestion
python scripts/codex_kb_bridge.py --dry-run    # Report only

# Run dashboard standalone
python -m uvicorn scripts.autonomous_dashboard.app:app --port 8000 --reload
```

Total codebase: ~9,000 lines across 16 Python files + 8 HTML templates.
