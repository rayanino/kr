- **Mandatory multi-coworker dispatch:** Every major milestone in the excerpting hardening operation (questionnaire design, smoke run analysis, hardening decision, full run evaluation) MUST dispatch ALL available coworkers before concluding. This is not optional — it is enforced by OPS-DEC-006.
- **Available coworkers (6 sources):**
  - Codex CLI (`codex exec`): schema validation, cross-prompt consistency, statistical analysis
  - Gemini CLI (`gemini -p`): Arabic scholarly accuracy, convention compliance
  - ChatGPT Deep Research: error pattern analysis, architectural analysis, Q&A design (relay prompt to owner)
  - Claude Deep Research: scholarly reasoning, boundary quality, edge cases (relay prompt to owner)
  - Gemini Deep Research: **strongest DR source when given correct files and prompt** (owner assessment 2026-04-01). Islamic study methodology, scholarly pedagogy, Arabic analysis. Needs file uploads or public repo — never treat as fallback or inferior.
- **Dispatch protocol:**
  1. Define the specific question/task for each coworker (do not send the same generic prompt to all — tailor to each coworker's strength)
  2. Each coworker receives: repo context or relevant files, real excerpt examples, a focused question
  3. Each coworker returns: a structured report (not freeform chat) with clear findings and recommendations
  4. Log every dispatch to `.kr/runtime/dispatch_log.jsonl`: timestamp, coworker, phase, task, result summary
  5. After all coworkers report, synthesize findings before making any conclusion
- **No single-model conclusions:** A content quality assessment (excerpt is good/bad, boundary is correct/wrong, classification is accurate/inaccurate) from a single coworker is marked PRELIMINARY until confirmed by at least one other coworker. See `.claude/rules/no-single-model-conclusion.md`.
- **Deep Research coworker access:**
  - **ChatGPT DR** CAN access the private GitHub repository during DR sessions (confirmed by owner 2026-04-01). Provide file paths — the DR session reads them directly.
  - **Claude DR** CAN access the private GitHub repository during DR sessions (confirmed by owner 2026-04-01). Provide file paths — the DR session reads them directly.
  - **Gemini DR** CANNOT access the repo directly. Requires specific files uploaded to the session. Prepare a file bundle with key files, excerpt samples, and specific questions.
  - **Gemini CLI** has repo access locally via `gemini -p`.
  - **ChatGPT non-research mode** CANNOT access the repo. Needs files pasted or uploaded.
- **Fault tolerance:** If a coworker is unavailable (quota exhausted, tool failure, owner unavailable for relay), log the unavailability in `dispatch_log.jsonl` with `status: unavailable` and reason. The milestone may proceed with N-1 coworkers IF: (a) at least 3 coworkers completed, (b) the unavailable coworker's specialty is partially covered by another coworker, and (c) the gap is documented in the synthesis report. If 2+ coworkers are unavailable, the milestone MUST wait.
- **Dispatch skill:** See `.claude/skills/coworker-dispatch/SKILL.md` for exact prompt templates for each coworker type.
- **Reference:** NEXT.md lines 147-153 (team table), OPS-DEC-006 in `.kr/DECISIONS.md`.
