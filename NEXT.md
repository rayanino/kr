# NEXT — Fix Windows cp1252 Crash + Launch Overnight Run

## What's Wrong

`run_integration_test.py` prints Arabic source metadata with `ensure_ascii=False`.
On Windows, the console encoding is cp1252, which can't encode Arabic. This crashes
4 of 5 packages (only `ext_39_masala` with null metadata survives).

Error at line ~1018:
```
UnicodeEncodeError: 'charmap' codec can't encode characters in position 0-5
```

## What to Do

### Fix 1: Add UTF-8 stdout reconfiguration to `run_integration_test.py`

After the imports (around line 25), add:

```python
import sys

# Ensure stdout/stderr can handle Arabic text on Windows (cp1252 default)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
```

Note: `sys` is probably already imported. Check first — if so, just add the reconfigure lines.

### Fix 2: Pass PYTHONIOENCODING in `run_full_integration.py`

At line ~195 where `subprocess.run(cmd, timeout=per_package_timeout)` is called, add
the env parameter:

```python
import os
env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
proc = subprocess.run(cmd, timeout=per_package_timeout, env=env)
```

### Fix 3: Verify

Run the CLI smoke test on ALL 5 packages:

```bash
python scripts/run_full_integration.py --backend cli --output-dir integration_tests/smoke_final_20260329 --max-chunks 1
```

All 5 must succeed (status "success"). At least 1 package should produce excerpts.

### Then: Launch the overnight run

```bash
python scripts/run_full_integration.py --backend cli --output-dir integration_tests/full_cli_20260329
```

No `--max-chunks` flag — this runs ALL 280 chunks. Estimated 15-20 hours at ~6 min/chunk.

## Do NOT Do

- Do NOT change cli_adapter.py — it's fixed
- Do NOT change any engine code
- Do NOT implement anything beyond the encoding fix and the two runs
- After launching the overnight run, commit, push, and STOP
