- **Mandatory multi-coworker dispatch:** Every major milestone in the excerpting hardening operation (questionnaire design, smoke run analysis, hardening decision, full run evaluation) MUST dispatch ALL available coworkers before concluding. This is not optional — it is enforced by OPS-DEC-006.
- **Available coworkers (5):**
  - Codex CLI (`codex exec`): schema validation, cross-prompt consistency, statistical analysis
  - Gemini CLI (`gemini -p`): Arabic scholarly accuracy, convention compliance
  - ChatGPT Deep Research: error pattern analysis, architectural analysis, Q&A design (relay prompt to owner)
  - Claude Deep Research: scholarly reasoning, boundary quality, edge cases (relay prompt to owner)
  - Gemini Deep Research: Islamic study methodology, scholarly pedagogy (relay prompt to owner)
- **Dispatch protocol:**
  1. Define the specific question/task for each coworker (do not send the same generic prompt to all — tailor to each coworker's strength)
  2. Each coworker receives: repo context or relevant files, real excerpt examples, a focused question
  3. Each coworker returns: a structured report (not freeform chat) with clear findings and recommendations
  4. Log every dispatch to `.kr/runtime/dispatch_log.jsonl`: timestamp, coworker, phase, task, result summary
  5. After all coworkers report, synthesize findings before making any conclusion
- **No single-model conclusions:** A content quality assessment (excerpt is good/bad, boundary is correct/wrong, classification is accurate/inaccurate) from a single coworker is marked PRELIMINARY until confirmed by at least one other coworker. See `.claude/rules/no-single-model-conclusion.md`.
- **Deep Research coworkers require relay prompts:** ChatGPT DR, Claude DR, and Gemini DR cannot access the repo directly during deep research sessions. Provide the owner with a complete, self-contained prompt to relay. The prompt must include all necessary context (file contents, excerpt examples, specific questions) so the DR session can work without additional file access.
- **Dispatch skill:** See `.claude/skills/coworker-dispatch/SKILL.md` for exact prompt templates for each coworker type.
- **Reference:** NEXT.md lines 147-153 (team table), OPS-DEC-006 in `.kr/DECISIONS.md`.
