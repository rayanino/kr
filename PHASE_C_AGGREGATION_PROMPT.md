Phase C evaluation is complete. You are the aggregation session. 7 evaluation sessions assessed 73 pipeline books (76 verdicts total, 4 duplicates). Your job is to independently analyze the complete data set and produce the definitive Phase C aggregation report.

<what_exists>
Claude Code has already extracted all 76 verdicts into a structured JSON file:
  `phase_c_collection/PHASE_C_ALL_VERDICTS.json`

This file contains:
- 76 verdict entries with: book name, session, status, verdict, author, genre, ML, confidence scores, trust, key issues
- A `_statistics` section with counts by verdict, session, genre, status, confidence distributions
- A `_coverage_notes` section documenting 4 duplicate evaluations and 1 unevaluated book

The handoff document (NEXT.md) contains 9 systematic findings written by the Session 7 evaluator. These findings were synthesized incrementally — each session built on the prior one's handoff — and never received independent review. Your job is to verify them independently, not inherit them uncritically.
</what_exists>

<what_you_must_produce>
A single report: `PHASE_C_AGGREGATION_REPORT.md`

The report must contain these sections:

**Section 1 — Verdict Summary**
The complete verdict table (all 76 entries), organized by session. For duplicates, note both evaluations. Flag the 1 unevaluated book. Confirm the final counts: 59V / 17P / 0F / 0E (or correct them if the data says otherwise).

**Section 2 — Statistical Analysis**
Using the `_statistics` section from the JSON AND your own independent verification:
- Verdict distribution by genre: which genres are always VERIFIED? Which have PLAUSIBLE? Why?
- Verdict distribution by status: success vs gate_abort — does status correlate with verdict?
- Confidence calibration: do author/genre confidence scores discriminate between easy and hard cases? What is the lowest confidence that received VERIFIED? The highest that received PLAUSIBLE?
- Trust tier analysis: for the 22 success books, what drives flagged vs verified trust?
- ML disagreement analysis: the 4 ML disagreements — are they all the tahqiq_note pattern?

**Section 3 — Systematic Findings (independently derived)**
NEXT.md lists 9 findings. For each one:
- Verify it against the verdict data. Does the data support the claim?
- Check for findings the prior sessions might have missed. Look at the full 76-book data set for patterns that only emerge at scale.
- If you find a 10th (or 11th) pattern, document it.

**Section 4 — Engine Improvement Recommendations**
Prioritized list of what should be fixed before Step 4 (the 150-book calibration run at €20-30). For each recommendation:
- What is the problem?
- What is the evidence (with specific book examples)?
- What is the proposed fix?
- What is the priority (must-fix before Step 4 / should-fix / nice-to-have)?

**Section 5 — Ground Truth Candidates**
Which of the 59 VERIFIED books should become ground truth for calibration? Are there any VERIFIED books where the classification is technically correct but imprecise enough to be problematic as ground truth? (Example: genre=tabaqat for a jarh wa ta'dil work is correct but imprecise.)

**Section 6 — Phase C Conclusion**
Overall assessment: is the source engine ready for Step 4? What are the remaining risks? What confidence level do you have in the pipeline's output quality?
</what_you_must_produce>

<instructions>
1. Clone the repo: `git clone https://{token}@github.com/rayanino/kr.git`
   (The GitHub token is in project knowledge.)

2. Read these files in this order:
   a. NEXT.md — the aggregation handoff (contains systematic findings to verify)
   b. PHASE_C_ERRATA.md — corrections that override the evaluation framework
   c. phase_c_collection/PHASE_C_ALL_VERDICTS.json — the extracted verdict data
   d. PHASE_C_EVALUATION_FRAMEWORK.md — verdict scale definitions (skim)

3. For Section 3 (systematic findings verification), you MUST independently check each finding against the JSON data. Do not simply restate what NEXT.md says. Example: NEXT.md claims "0 author errors across 76 verdicts" — verify by checking that `author_correct` is true for all 76 entries in the JSON.

4. For Section 2 (statistical analysis), compute your own statistics from the JSON data. The `_statistics` section is a starting point, but verify it and add any analysis it doesn't cover.

5. Web search is NOT needed for this session. All data comes from the evaluated pipeline results and the session reports. This is a synthesis task, not a research task.

6. Commit the report when done.
</instructions>

<critical_corrections>
These corrections from PHASE_C_ERRATA.md affect how you interpret the data:

1. result.json author confidence is ALWAYS 1.0 — this is an engine bug. The JSON file uses the correct values from llm_responses/.

2. Consensus agreed=true does NOT mean models agree on everything. Consensus only checks author + genre + attribution. ML, authority_level, and science_scope are NOT checked.

3. Shamela-ecosystem sources (shamela.ws, ketabonline.com, turath.io, waqfeya.net) count as ONE source collectively for VERIFIED threshold. VERIFIED requires 2+ genuinely independent sources.

4. 6 books have consensus.agreed=false: 3 are name-format-only (not substantive), 3 are partially substantive. All are documented in the JSON.
</critical_corrections>

<quality_standards>
The owner values depth over speed. Take as long as needed.

This report determines whether a €20-30 calibration run proceeds. An overconfident "ready" assessment wastes budget on a broken engine. An overly cautious "not ready" delays progress unnecessarily. Be honest about what the data shows.

The 9 findings in NEXT.md were synthesized by a chain of Claude Chat sessions, each seeing only its own batch. You are the first session to see the full picture. If the chain introduced drift, you are the one who catches it.
</quality_standards>
