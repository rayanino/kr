---
description: Quick evaluation phase dashboard showing books processed, verdicts issued, cost spent, consensus stats, and pending work. Usage /eval-dashboard [phase].
allowed-tools: Bash(python *), Bash(python3 *), Bash(cat *), Bash(find *), Bash(grep *), Bash(wc *), Bash(ls *), Read, Glob, Grep
---
Show evaluation phase progress dashboard. Default: scan all phases. If `$ARGUMENTS` specifies a phase letter (C, D, E), show only that phase.

## Data Collection

Gather data from these sources:

### 1. Phase Manifests
For each phase (C, D, E):
```bash
# Check if manifest exists
ls tests/results/source_engine/PHASE_*_MANIFEST.json 2>/dev/null
```
Parse each manifest for:
- Total books listed
- Status breakdown: `completed`, `pending`, `api_error`, `needs_rerun`
- Last updated timestamp

### 2. Verdict Counts
```bash
# Count verdicts from session reports
grep -rh "Verdict:" tests/results/source_engine/PHASE_*_SESSION*_REPORT.md 2>/dev/null | sort | uniq -c
# Also check individual book results
find tests/results/source_engine/ -name "result.json" 2>/dev/null | wc -l
```

### 3. Consensus Statistics
```bash
# Check consensus files for agreement rates
find tests/results/source_engine/ -name "consensus.json" -exec cat {} \; 2>/dev/null
```
Calculate: agreement rate, disagreement count, flagged-for-human count.

### 4. Cost Data
Read `tests/results/source_engine/COST_LOG.json` for per-phase cost breakdown.

### 5. Error Tracking
Read `tests/results/source_engine/ERROR_LOG.json` for unresolved errors.

## Dashboard Format

```
╔══════════════════════════════════════════════╗
║          KR Evaluation Dashboard             ║
║          [ISO 8601 timestamp]                ║
╠══════════════════════════════════════════════╣
║                                              ║
║  Phase C (Source Analysis)                   ║
║  ─────────────────────                       ║
║  Books:     [completed]/[total] ([%])        ║
║  Verdicts:  VERIFIED [n] | REFUTED [n]       ║
║             UNCERTAIN [n] | PENDING [n]      ║
║  Consensus: [agree]% agreement               ║
║  Cost:      EUR [x.xx] (avg [y.yy]/book)    ║
║  Errors:    [n] unresolved                   ║
║                                              ║
║  Phase D (Normalization)                     ║
║  ─────────────────────                       ║
║  [same structure or "Not started"]           ║
║                                              ║
║  Phase E (Excerpting)                        ║
║  ─────────────────────                       ║
║  [same structure or "Not started"]           ║
║                                              ║
╠══════════════════════════════════════════════╣
║  Budget: EUR [spent]/[limit] ([%] used)      ║
║  Total verdicts: [n] across all phases       ║
║  Human gates pending: [n]                    ║
╚══════════════════════════════════════════════╝
```

### Next Actions
Based on the data, suggest:
- If a phase has pending books: "Run evaluation on N pending books in Phase X"
- If errors exist: "Resolve N API errors before continuing"
- If needs_rerun books: "N books need re-evaluation after bug fixes"
- If human gates pending: "N items await human review"

## Rules
- If no evaluation data exists yet, report "No evaluation data found. Run /orchestrate verify <engine> to start."
- Show actual data only — never estimate or fill in missing values.
- Keep the dashboard compact — it's meant for quick orientation, not deep analysis.
- If a specific phase is requested, show only that phase in detail.
