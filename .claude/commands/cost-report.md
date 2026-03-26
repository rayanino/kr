---
description: Show API cost breakdown by model, phase, and date. Usage /cost-report [--detail]. Essential for budget tracking during LLM evaluation runs.
allowed-tools: Bash(python *), Bash(python3 *), Bash(cat *), Bash(jq *), Read, Glob, Grep
---
Generate an API cost report from the project's cost tracking data.

## Data Sources

1. **Primary:** `tests/results/source_engine/COST_LOG.json` — per-call cost records
2. **Budget:** `KR_BUDGET_LIMIT` environment variable (default: EUR 100)
3. **Session:** `.claude/session_state.json` — current session cost if available

## Report Structure

Read COST_LOG.json. If it doesn't exist, report "No API costs recorded yet" and exit.

Parse each entry for: timestamp, model, phase, input_tokens, output_tokens, cost_eur, book_ids.

Produce this report:

```
=== KR API Cost Report ===
Generated: [ISO 8601]

Budget:     EUR [limit]
Spent:      EUR [total] ([percent]%)
Remaining:  EUR [remaining]

--- By Model ---
  [model_name]:  EUR [cost] ([N] calls, [tokens] tokens)
  [model_name]:  EUR [cost] ([N] calls, [tokens] tokens)

--- By Phase ---
  Phase C:  EUR [cost] ([N] books)
  Phase D:  EUR [cost] ([N] books)
  Phase E:  EUR [cost] ([N] books)

--- By Date ---
  [date]:  EUR [cost] ([N] calls)
  [date]:  EUR [cost] ([N] calls)

--- Recent Calls (last 10) ---
  [timestamp] [model] [phase] [book_id] EUR [cost]
```

If `$ARGUMENTS` contains `--detail`, also show per-book cost breakdown.

## Budget Warnings

- If remaining < 20%: add `⚠️ Budget alert: less than 20% remaining`
- If remaining < 10%: add `🚨 Budget critical: less than 10% remaining`
- If remaining < 5%: add `🛑 Budget nearly exhausted — cost-guard hook will block further API calls`

## Rules

- If COST_LOG.json is missing or empty, check for alternative cost data in session_state.json.
- All amounts in EUR, 2 decimal places.
- Sort "By Date" most recent first.
- Calculate average cost per book for each phase.
