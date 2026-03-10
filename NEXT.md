# NEXT — Source Engine Session 6

**Read:** `engines/source/session-6-next.md` — this is the complete build directive.

**Summary:** Build engine.py (pipeline orchestrator) and logger.py (structured logging), then run full pipeline integration on all 14 fixtures with real LLM calls (~$1-2). Resolve the two remaining Step 4 blocking conditions (confidence calibration, author complementarity).

**Pre-existing state:** 723 tests passing (22 skipped). All modules built except engine.py and logger.py. config.py is already complete (do NOT rebuild).

**API keys needed:** ANTHROPIC_API_KEY, OPENROUTER_API_KEY (from project knowledge files).
