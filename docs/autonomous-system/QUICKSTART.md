# KB Digestion System — Quick Start

## What This Does

Processes DR (Deep Research) response files into structured findings, detects contradictions between sources, and generates follow-up prompts for cross-model confirmation. All visible on a dashboard.

## Prerequisites

```bash
pip install fastapi uvicorn jinja2 pydantic
```

## The Core Loop

### 1. Drop a DR response file

Save any DR response as a `.md` file anywhere. Then:

```bash
python scripts/digest_dr.py path/to/response.md
```

This runs the full pipeline:
- Auto-detects the provider (ChatGPT/Claude/Gemini)
- Extracts findings (recommendations, questions)
- Cross-references with existing findings
- Runs quality gate (PASS/WARN/FAIL)
- Generates follow-up prompts

### 2. View the dashboard

```bash
python -m uvicorn scripts.autonomous_dashboard.app:app --port 8000
```

Open `http://localhost:8000`. Pages:

| Page | What it shows |
|------|--------------|
| **DR Relay Queue** (`/`) | Pending prompts to relay to DR coworkers. Copy-paste ready. |
| **Findings** (`/findings`) | All extracted findings, grouped by severity. |
| **Contradictions** (`/contradictions`) | Conflicts between DR sources. |
| **Digestion Log** (`/digestion`) | Processing status of each DR file. |
| **Ideas** (`/ideas`) | Idea quarry — submit and track ideas. |
| **Status** (`/status`) | Overall KB health stats. |

### 3. Relay follow-up prompts

On the Relay Queue page, each prompt has a copy button. Copy → paste into the appropriate DR session → save the response → drop it back as a `.md` file → run `digest_dr.py` again.

## Batch Processing

Process all `.md` files in a directory:

```bash
python scripts/digest_dr.py path/to/directory/ --batch
```

Re-run cross-referencing on existing data:

```bash
python scripts/digest_dr.py --reprocess
```

## Specifying the Provider

If auto-detection gets the provider wrong (e.g., Claude DR with heavy Arabic detected as Gemini):

```bash
python scripts/digest_dr.py response.md --source claude_dr
```

## Current KB State

- 32 DR responses digested
- 234 findings (45 critical, 77 high, 31 medium, 81 low)
- 47 contradictions
- 114 follow-up prompts in the relay queue
- 10 batch_2 Gemini DR scholarly answers (taxonomy tree decisions)

## File Locations

```
overnight_codex/autonomous/knowledge_base/
  findings.jsonl          — All extracted findings
  dr_responses.jsonl      — DR response metadata
  contradictions.jsonl    — Detected contradictions
  digestion_log.jsonl     — Processing log
  dr_prompts/
    batch_2.jsonl         — Original taxonomy DR prompts
    batch-full.jsonl      — Auto-generated follow-up prompts
```
