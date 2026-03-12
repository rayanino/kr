Clone the repo, then read NEXT.md.

<session_context>
We are mid-Step-3 of source engine validation. The pipeline ran 73 books. 7 evaluation sessions reviewed the results. An aggregation session compiled 13 findings and 7 bug recommendations. That aggregation was done by a context-heavy session that may have missed things.

Your job is the last quality gate before Claude Code touches the engine: produce the definitive, exhaustive bug list. Every bug you miss ships into Step 4 and wastes €15-25 of API budget on a broken engine. Every bug you catch now gets fixed for free.
</session_context>

<task>
Find every bug in the source engine. Not just the 7 already documented — those are your starting point, not your finish line.

Work in three phases:

PHASE 1 — Absorb what's known.
Read NEXT.md, then PHASE_C_AGGREGATION_REPORT.md (especially Sections 3 and 4), then PHASE_C_ERRATA.md. Understand the 7 documented bugs and 13 findings. Do not start looking for new bugs until you can explain every known bug from memory.

PHASE 2 — Hunt in the data.
Load phase_c_collection/PHASE_C_ALL_VERDICTS.json via Python. Query it for anomalies the aggregation may have missed. Then read actual per-book result files in tests/results/source_engine/phase_c/ — pick 10-15 books across the confidence spectrum (high-confidence successes, low-confidence, gate_aborts, ML disagreements, consensus disagreements) and read their result.json, consensus.json, and llm_responses/ files. Look for fields that are wrong, missing, inconsistent, or silently defaulted.

PHASE 3 — Hunt in the code.
Read the engine source code in engines/source/src/. Trace the pipeline path that a book follows through engine.py → metadata_inference.py → consensus.py → validation.py → registries/. Look for:
- Silent failures (errors caught and swallowed without logging)
- Fields computed but never written to output
- Validation rules that can be bypassed
- Edge cases in Arabic text handling
- Assumptions that hold for 73 books but break at 200+
- Anything that contradicts SPEC_CORE.md

Cross-reference code findings against the Phase C results. A code bug that happens to produce correct output on these 73 books is still a bug.
</task>

<output>
Produce a single document: STEP3_FINAL_BUG_LIST.md

For each bug:
- ID (BUG-001, BUG-002, ...)
- Summary (one line)
- Evidence (specific books, specific code lines, specific JSON fields)
- Severity (must-fix / should-fix / nice-to-have)
- Proposed fix (specific enough for Claude Code to implement without ambiguity)

Include the 7 known bugs (verified or updated with your own analysis) plus every new bug you find. If you find zero new bugs beyond the 7, state that explicitly with evidence of what you checked.

End the document with a GO/NO-GO verdict: is this bug list complete enough to hand to Claude Code?
</output>

<constraints>
- Do NOT plan Step 4. Do NOT discuss the normalization engine. You are finishing Step 3.
- Do NOT assume the 7 documented bugs are correctly described. Verify each one against the code.
- Do NOT read every file in the repo. Read strategically: NEXT.md tells you what to read.
- When checking the engine code, always cite file and line number for every finding.
- Escalate domain questions to the owner — do not guess on Islamic bibliography.
</constraints>
