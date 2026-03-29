# Design: Creative Task Expansion for Overnight System

**Date:** 2026-03-29
**Status:** Draft
**Problem:** The overnight system only does hardening (bughunts, test gaps, SPEC audits). A manual research sprint showed that creative work (innovation research, adversarial generation, cross-pollination, architecture challenges) produces extremely high-value output (9,300 lines, 4 bugs found, 166 tests generated, 30+ actionable items). This creative work should happen autonomously alongside hardening.

**Approach:** Add a 10th scanner to the task generator that selects from a template library of creative tasks, instantiates them for the current project context, and dispatches to Claude/Codex/Gemini as primary executors. 30% creative / 70% hardening budget split.

---

## 1. Template Library

### 1.1 Directory Structure

```
overnight/creative_templates/
├── innovation/
│   ├── technology_survey.json
│   ├── architecture_challenge.json
│   ├── cost_efficiency.json
│   ├── domain_knowledge_gaps.json
│   ├── cross_pollination.json
│   └── radical_alternatives.json
├── adversarial/
│   ├── t1_text_corruption.json
│   ├── t2_attribution_error.json
│   ├── t3_taxonomic_misplacement.json
│   ├── t4_context_loss.json
│   ├── t5t6t7_combined.json
│   └── boundary_stress.json
├── spec_challenge/
│   ├── cross_provider_review.json
│   └── exhaustive_rule_audit.json
└── edge_testing/
    ├── arabic_extremes.json
    ├── state_machine.json
    └── concurrency.json
```

### 1.2 Template Schema

```json
{
  "template_id": "innovation/technology_survey",
  "name": "Technology Survey for {target}",
  "description": "Research tools/libraries for the {target} component",
  "category": "creative",
  "subcategory": "innovation",
  "execution_mode": "cli",
  "preferred_provider": "claude",
  "safety_level": "readonly",
  "model": "opus",
  "timeout_minutes": 30,
  "max_turns": 50,
  "cooldown_days": 14,
  "applicable_when": {
    "engine_exists": true,
    "last_run_older_than_days": 14
  },
  "variables": {
    "target": { "source": "active_engine", "fallback": "excerpting" },
    "domain": { "source": "literal", "value": "Arabic NLP" }
  },
  "prompt_template": "You are researching {domain} tools for the KR project's {target} engine...\n\n[full prompt here]\n\nWrite findings to: overnight/results/creative-{run_date}/{task_id}/report.md\n\nIf you find actionable items, also write:\novernight/results/creative-{run_date}/{task_id}/actionable.json",
  "output_dir": "overnight/results/creative-{run_date}/{task_id}"
}
```

### 1.3 Key Fields

| Field | Purpose |
|-------|---------|
| `preferred_provider` | `claude` for research (web search), `codex` for adversarial gen, `gemini` for SPEC challenges |
| `cooldown_days` | Prevents re-running same template+target within N days |
| `applicable_when` | Conditions checked by scanner (engine active, time elapsed, tracker items open) |
| `variables` | Template variables filled from project state |

### 1.4 Provider Assignment

| Creative Type | Provider | Rationale |
|---------------|----------|-----------|
| Innovation research | Claude | Needs web search, deep reasoning, project context |
| Architecture challenge | Claude | Needs to read all contracts.py files |
| Cost efficiency | Claude | Needs to read pipeline code |
| Domain knowledge gaps | Claude | Needs web search for Islamic scholarly patterns |
| Cross-pollination | Claude | Needs web search for peer projects |
| Radical alternatives | Claude | Needs full project context |
| T-1 through T-7 adversarial | Codex | Different training data = different blind spots (per AUTONOMOUS_QUALITY_SYSTEM.md D-F002) |
| Boundary stress | Codex | Same rationale |
| SPEC cross-provider review | Gemini | Different perspective on Arabic text handling |
| Arabic edge case tests | Claude | Needs to read existing code and write tests |
| State machine tests | Claude | Needs deep pipeline understanding |
| Concurrency analysis | Claude | Needs to trace shared state through code |

**Gemini quota guard:** Max 10 Gemini tasks per run. Scanner counts existing Gemini tasks and stops adding when limit reached.

---

## 2. Creative Scanner

### 2.1 Location

New function `creative_scanner()` added to `scripts/overnight_task_generator.py` as scanner #10.

### 2.2 Algorithm

```python
def creative_scanner(repo_state: RepoState, run_log: dict) -> list[Task]:
    templates = load_templates("overnight/creative_templates/")
    tasks = []

    for template in templates:
        # Check cooldown
        last_run_key = f"{template.template_id}:{repo_state.active_engine}"
        last_run = run_log.get(last_run_key)
        if last_run and days_since(last_run) < template.cooldown_days:
            continue

        # Check applicability conditions
        if not evaluate_conditions(template.applicable_when, repo_state):
            continue

        # Instantiate template
        variables = resolve_variables(template.variables, repo_state)
        task = instantiate_task(template, variables, run_date=today())
        tasks.append(task)

    # Enforce 30% budget cap
    hardening_count = count_hardening_tasks()
    max_creative = int(hardening_count * 0.43)  # 30/(100-30) = 0.43 ratio
    if len(tasks) > max_creative:
        tasks = prioritize_and_trim(tasks, max_creative)

    # Enforce Gemini quota
    gemini_tasks = [t for t in tasks if t.execution_mode == "gemini"]
    if len(gemini_tasks) > 10:
        tasks = cap_gemini(tasks, 10)

    return tasks
```

### 2.3 Variable Resolution

| Variable Source | How Resolved |
|----------------|-------------|
| `active_engine` | Parse NEXT.md first heading for engine name |
| `all_engines` | Glob `engines/*/SPEC.md` |
| `engine_pairs` | Adjacent pairs from pipeline order |
| `open_findings` | Parse FINDINGS_TRACKER.md checkboxes |
| `literal` | Static value from template |
| `run_date` | Today's date (YYYY-MM-DD) |

### 2.4 Run Log

File: `overnight/creative_run_log.json`

```json
{
  "runs": {
    "innovation/technology_survey:excerpting": "2026-03-28",
    "adversarial/t1_text_corruption:excerpting": "2026-03-28",
    "spec_challenge/cross_provider_review:taxonomy": "2026-03-29"
  }
}
```

Updated after each creative task completes (success or failure). Failed tasks still consume cooldown — re-running a broken template doesn't help.

---

## 3. Orchestrator Changes

### 3.1 Creative Task Execution

Creative tasks use the same dispatch mechanism as existing tasks. The `execution_mode` field already supports `cli`, `codex`, `gemini`. No new dispatch paths needed.

One change: the existing `_execute_gemini()` function is currently only called for L6 verification. It must also be callable as a primary task executor. This requires:
- Remove the L6-only guard (if any)
- Add output capture to `overnight/results/` (same as CLI tasks)
- Add creative-specific output parsing

### 3.2 Safety Prompt Expansion

Current safety prompt forbids all non-hardening work. Add an exception for creative tasks:

```python
CREATIVE_SAFETY_ADDENDUM = """
This is a CREATIVE RESEARCH task. You are permitted to:
- Produce research reports and recommendations
- Generate adversarial test data (JSON files)
- Write architectural analysis and challenge documents
- Propose alternative approaches

You are NOT permitted to:
- Modify any source code in engines/ or shared/
- Delete or rename any existing files
- Create files outside overnight/results/
- Make git commits
"""
```

Applied when `task.category == "creative"`.

### 3.3 Priority Interleaving

Creative tasks get `priority: 2` (between critical hardening at 1 and nice-to-have at 3). The existing `pick_next_ready()` algorithm already sorts by priority, so creative tasks naturally interleave between urgent bugs and routine hardening.

### 3.4 Budget Accounting

Creative tasks cost varies:
- Claude readonly: ~$2-5 per task (reading code + web search + writing report)
- Codex: $0 (subscription)
- Gemini: $0 (subscription, but quota-limited)

The global budget cap (`--max-cost-usd`) already handles this. No change needed.

---

## 4. Output and Tracking

### 4.1 Output Structure

```
overnight/results/
├── creative-2026-03-29/          # Creative output for this run
│   ├── innovation-technology-survey-excerpting/
│   │   ├── report.md             # Main research output
│   │   └── actionable.json       # Structured findings
│   ├── adversarial-t1-excerpting/
│   │   ├── t1_samples.json       # Arabic adversarial data
│   │   └── actionable.json
│   └── spec-challenge-taxonomy/
│       ├── review.md
│       └── actionable.json
├── bughunt-norm-shamela/         # Existing hardening output
│   └── ...
└── ...
```

### 4.2 Actionable Findings Format

Each creative task prompt instructs the LLM to write an `actionable.json` if it finds anything worth tracking:

```json
[
  {
    "id": "CREATIVE-2026-03-29-001",
    "category": "EXT",
    "summary": "GATE Arabic embeddings could reduce taxonomy LLM calls by 80%",
    "source_report": "innovation-technology-survey-excerpting/report.md",
    "effort": "M",
    "priority": "HIGH"
  }
]
```

### 4.3 Morning Report Integration

The morning report script gains a new section:

```markdown
## Creative Research Findings

### Innovation
- Technology Survey (excerpting): 19 tools ranked. Top: Tanzil, GATE, CAMeL. [report.md]
- Architecture Challenge: 5 issues found. Top: ghost engines (1,232 dead lines). [report.md]

### Adversarial Data Generated
- T-1 Text Corruption: 5 samples generated. [t1_samples.json]
- T-2 Attribution Error: 5 samples generated. [t2_samples.json]

### New Actionable Items (auto-appended to FINDINGS_TRACKER.md)
- EXT-006: GATE Arabic embeddings for taxonomy (M effort, HIGH priority)
- BUG-007: diacritic normalization gap in taxonomy matching
```

### 4.4 Auto-Append to FINDINGS_TRACKER

After all tasks complete, a post-run script reads all `actionable.json` files and appends new items to `FINDINGS_TRACKER.md` under the appropriate section. Items are deduplicated by summary text similarity (exact match or >90% overlap skips).

---

## 5. Files to Create/Modify

| File | Action | Lines |
|------|--------|-------|
| `overnight/creative_templates/*.json` | CREATE | ~15 files, 30-80 lines each |
| `scripts/overnight_task_generator.py` | MODIFY | +100 lines (creative_scanner function) |
| `scripts/overnight_orchestrator.py` | MODIFY | +30 lines (creative safety prompt, Gemini primary exec) |
| `scripts/append_creative_findings.py` | CREATE | ~60 lines (post-run FINDINGS_TRACKER append) |
| `overnight/creative_run_log.json` | CREATE | Auto-generated at runtime |
| `scripts/start_overnight.sh` | MODIFY | +5 lines (call append script after orchestrator) |

**Total new code:** ~250 lines Python + ~800 lines JSON templates.

---

## 6. Verification

1. **Template loading:** `python -c "from scripts.overnight_task_generator import creative_scanner; print(len(creative_scanner(...)))"`
2. **Dry run:** `python scripts/overnight_orchestrator.py --manifest overnight/manifest.json --dry-run` — verify creative tasks appear interleaved
3. **Single creative task:** Extract one creative task from manifest, run it manually: `claude -p "{prompt}" --output-format json --max-turns 50`
4. **Actionable extraction:** After a test run, verify `overnight/results/creative-*/*/actionable.json` files exist and are valid JSON
5. **FINDINGS_TRACKER append:** Run `python scripts/append_creative_findings.py` and verify new items appear in FINDINGS_TRACKER.md
6. **Cooldown enforcement:** Run task generator twice in same day — second run should produce 0 creative tasks for same targets
7. **Gemini quota:** Generate manifest with 20+ Gemini-preferred templates — verify max 10 selected
8. **Full overnight test:** Run for 2 hours with `--hours 2` and verify both hardening and creative tasks execute
