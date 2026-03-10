# NEXT — Source Engine Validation, Step 0

**Governing document:** `engines/source/VALIDATION_PLAN.md` — read this first in every new session.

**Current step:** Step 0 — 14-fixture integration run with real LLM calls.

**What to do:**
```bash
export ANTHROPIC_API_KEY="..."
export OPENROUTER_API_KEY="..."
python scripts/run_session6_integration.py
```

**After Step 0 completes:** Push results. Owner reviews in Claude Chat with kr-evaluate. Then proceed to Step 1 (Code Audit) per the validation plan.

**Pre-existing state:** 758 tests passing. Engine fully built and reviewed. No real LLM calls made yet.
