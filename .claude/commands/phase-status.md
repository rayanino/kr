---
description: Instant dashboard of current phase progress — books processed, verdicts issued, cost, pending work.
allowed-tools: Bash(cat:*), Bash(ls:*), Bash(wc:*), Bash(find:*), Bash(grep:*), Read, Glob, Grep
---

Produce a compact Phase C status dashboard. Do ALL of these:

1. Read `tests/results/source_engine/COST_LOG.json` — report per-phase cost and total vs 100 EUR budget ceiling.
2. Count book directories in `tests/results/source_engine/phase_c/` — exclude files that are NOT book directories (PHASE_C_SUMMARY.json, PHASE_C_MANIFEST.json, PHASE_C_LESSONS.md, and any other non-directory items).
3. Read `tests/results/source_engine/phase_c/PHASE_C_SUMMARY.json` — report success/gate_abort/error breakdown.
4. List existing session reports: glob for `PHASE_C_SESSION*_REPORT.md` in the project root.
5. Count verdicts: grep for lines starting with `Verdict:` across all session reports found in step 4.
6. Break down verdicts by type: count VERIFIED, PLAUSIBLE, FLAG, ESCALATE, UNVERIFIABLE separately.
7. Read first 20 lines of `NEXT.md` — show current session assignment and pre-identified risks.

Output this format:

```
=== PHASE C STATUS ===

| Metric | Value |
|--------|-------|
| Books processed | [N] |
| Success | [N] ([%]) |
| Gate abort | [N] ([%]) |
| Error | [N] |
| Budget | [X] / 100.0 EUR ([%]) |
| Sessions complete | [N] / 7 |
| Verdicts issued | [N] total |
| - VERIFIED | [N] |
| - PLAUSIBLE | [N] |
| - FLAG | [N] |
| - ESCALATE | [N] |

Current: Session [N] — [book count] books
Risks: [list from NEXT.md]
```

If any file is missing, note it as "[not found]" and continue with available data.
