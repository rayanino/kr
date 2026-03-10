# NEXT — Phase C Evaluation (Phase 2)

Phase C implementation is COMPLETE. Claude Code ran the full pipeline on 73 books.
Results committed to tests/results/source_engine/phase_c/.

Calibration (Phase 1) is COMPLETE. 3 books evaluated, framework validated with corrections.

## Before starting Phase 2 evaluation, read these in order:
1. PHASE_C_EVALUATION_FRAMEWORK.md (632 lines — full protocol)
2. **PHASE_C_ERRATA.md** (CRITICAL — corrections to framework and LESSONS.md)
3. PHASE_C_CALIBRATION_BUGS.md (engine bugs found, with workarounds)
4. tests/results/source_engine/phase_c/PHASE_C_LESSONS.md (CC findings — BUT see errata for 3 factual errors)

## Key corrections from calibration:
- LLM filename is `claude_opus_4_6.json` NOT `opus_4_6.json`
- 6 books use `gpt_5_4.json` instead of `command_a.json` — check per-book
- 0/73 single-model fallback (LESSONS.md claim of 73/73 is false)
- result.json author confidence is always 1.0 (ENGINE BUG) — read from llm_responses/ instead
- Framework Section 7 (single-model) does not apply

## Session plan:
Follow the framework's session assignments (Sessions 1-7).
Each session = new conversation. Max 10 books per session.
Owner provides the handoff prompt with specific session instructions.
