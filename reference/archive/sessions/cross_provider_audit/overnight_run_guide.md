# Overnight Run — Execution Guide

## Pre-Run Checklist (ALL must pass)

- [ ] CC Phase 1 discovery completed — exact chunk counts known
- [ ] CC test suite passed (815+ tests, 0 failures)
- [ ] ChatGPT deep research report reviewed — no BLOCKING findings
- [ ] Windows power settings: **Never sleep** (Settings → System → Power → Sleep → Never)
- [ ] Network: Stable connection. Consider wired ethernet.
- [ ] Disk space: >1GB free for output artifacts
- [ ] Terminal: Keep open, do not close
- [ ] Claude CLI authenticated: `claude --version` works
- [ ] OAuth token fresh: run a quick `echo "test" | claude -p --bare` to verify

## Smoke Test (5 minutes — run this FIRST)

```powershell
cd C:\path\to\kr
python scripts/run_full_integration.py --backend cli --max-chunks 1 --output-dir integration_tests/smoke_20260329
```

This runs 1 chunk per package (5 total) to verify the full pipeline end-to-end.
Wait for it to complete. Check:
- All 5 packages show "COMPLETED"
- Total excerpts > 0
- No crashes

If the smoke test fails, DO NOT run the overnight. Report to architect.

## Overnight Run Command

```powershell
cd C:\path\to\kr

# Full run — all chunks, all packages
python scripts/run_full_integration.py --backend cli --output-dir integration_tests/full_run_20260329 --per-package-timeout 28800
```

Expected duration: **10-12 hours**
Expected output: **2000-3000 excerpts** across 5 packages

## While It Runs

- Do NOT close the terminal
- Do NOT let the machine sleep
- It's OK to use the machine for other tasks (browser, etc.)
- Console will print progress: `[1/5] ibn_aqil_v1`, `[2/5] ibn_aqil_v3`, etc.

## Morning Assessment

Run the analysis script CC prepared:

```powershell
python scripts/analyze_overnight_run.py --output-dir integration_tests/full_run_20260329
```

Then share the output with the architect for review.

## If Something Goes Wrong

- **Machine slept:** Results for completed packages are preserved. Re-run only the failed packages.
- **Python crashed:** Same — check which packages have results in the output directory.
- **Network error:** The pipeline uses local CLI tools. Network drops shouldn't affect it unless OAuth token needs refreshing.
- **All packages failed:** Run the smoke test again to diagnose. Report to architect.
