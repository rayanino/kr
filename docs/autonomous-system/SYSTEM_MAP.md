# Autonomous System Map

Read this when you come back confused about what all the overnight/autonomous scripts are.

## The Three Systems

### System 0 — "Overnight v2" (Claude Code CLI)

**What:** Scans the repo for quality work (test gaps, SPEC issues, Arabic edge cases, creative challenges) and runs each task using Claude Code CLI.

**Run:** `python scripts/overnight_orchestrator.py --hours 7.5`

**Output:** `overnight/` directory — morning reports, task results, manifests.

**Code:** `scripts/overnight_orchestrator.py` (1,844 lines), `scripts/overnight_task_generator.py` (1,060 lines).

**Status:** Original system. Still functional but System 1 supersedes it.

---

### System 1 — "Overnight Codex" (Codex CLI in worktrees)

**What:** Same purpose as System 0 but uses Codex CLI in isolated git worktrees. Has a backlog system, creative templates, quality gates, and circuit breakers.

**Run:** `python scripts/overnight_codex_orchestrator.py --hours 8`

**Output:** `overnight_codex/` directory — results, backlog, patches, morning reports, events.

**Code:** `scripts/overnight_codex_orchestrator.py` (2,638 lines), `scripts/overnight_codex_task_generator.py` (732 lines), `scripts/overnight_codex_common.py` (574 lines), `scripts/overnight_codex_backlog.py` (515 lines).

**Status:** The replacement for System 0. More sophisticated (worktree isolation, backlog tracking, creative task cooldowns). This is what the unified launcher uses.

---

### System 2 — "KB Digestion" (DR response processing + dashboard)

**What:** Processes Deep Research responses into structured findings. Detects contradictions between sources. Generates follow-up prompts routed to different providers for cross-model confirmation. Shows everything on a web dashboard.

**Run:** `python scripts/digest_dr.py response.md --dr-id DR40` (single file) or `python scripts/dashboard.py` (web UI)

**Output:** `overnight_codex/autonomous/knowledge_base/` — findings.jsonl, contradictions.jsonl, dr_prompts/, digestion_log.jsonl.

**Code:** `scripts/digest_dr.py`, `scripts/process_dr_response.py`, `scripts/dr_format_detectors.py`, `scripts/cross_reference_findings.py`, `scripts/generate_followup_prompts.py`, `scripts/digestion_quality_gate.py`, `scripts/autonomous_schemas.py`, `scripts/autonomous_dashboard/`.

**Status:** Complete. Dashboard at localhost:8000.

---

## The Unified Launcher

**Run:** `python scripts/launch_autonomous.py --hours 6`

This starts everything with one command:

```
Dashboard starts (localhost:8000)
    |
Codex runs research tasks in worktrees (System 1)
    |
Results are bridged into KB findings (codex_kb_bridge.py)
    |
Cross-referencing finds contradictions
    |
Follow-up DR prompts generated and shown on dashboard
    |
You copy prompts, relay to DR sessions
    |
DR responses come back --> digest_dr.py --> more findings --> cycle continues
```

**Options:**
- `--hours N` — how long to run (default: 4)
- `--no-dashboard` — headless, no web UI
- `--dashboard-only` — just view dashboard, no tasks
- `--ingest-only` — bridge existing results without running new tasks

---

## Where Data Lives

| Data | Location |
|------|----------|
| System 0 results | `overnight/` |
| System 1 results | `overnight_codex/results/` |
| System 1 backlog | `overnight_codex/backlog.json` |
| System 1 morning reports | `overnight_codex/MORNING_REPORT.md` |
| KB findings | `overnight_codex/autonomous/knowledge_base/findings.jsonl` |
| KB contradictions | `overnight_codex/autonomous/knowledge_base/contradictions.jsonl` |
| DR relay prompts | `overnight_codex/autonomous/knowledge_base/dr_prompts/` |
| Digestion log | `overnight_codex/autonomous/knowledge_base/digestion_log.jsonl` |
| Dashboard | `scripts/autonomous_dashboard/` (FastAPI + Jinja2 templates) |

## Quick Reference

| I want to... | Run |
|---|---|
| Start everything | `python scripts/launch_autonomous.py --hours 6` |
| Just view the dashboard | `python scripts/launch_autonomous.py --dashboard-only` |
| Process a DR response | `python scripts/digest_dr.py response.md --dr-id DR40` |
| Process a batch of DR responses | `python scripts/digest_dr.py responses/ --batch` |
| Run Codex tasks only (no dashboard) | `python scripts/overnight_codex_orchestrator.py --hours 4` |
| Ingest existing Codex results into KB | `python scripts/launch_autonomous.py --ingest-only` |
