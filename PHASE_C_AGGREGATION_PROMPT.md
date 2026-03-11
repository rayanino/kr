Phase C evaluation is complete. You are the aggregation session.

The pipeline processed 73 books. 72 were manually evaluated across 7 sessions (76 verdicts total — 4 books were evaluated twice for cross-edition checks). 1 book (أمالي المحاملي) was never selected for evaluation. Your job is to independently analyze the complete data set and produce the definitive Phase C aggregation report.

<what_exists>
Claude Code has already extracted all 76 verdicts into a structured JSON file:
  `phase_c_collection/PHASE_C_ALL_VERDICTS.json`

This file contains:
- `verdicts`: 76 entries, each with 22 fields (book, session, status, verdict, author_correct, author_confidence_opus, genre, genre_correct, genre_confidence_opus, is_multi_layer, ml_correct, ml_disagreement, death_date, death_source, science_scope, trust_tier, trust_score, consensus_agreed, models, key_issues, duplicate_of)
- `_statistics`: precomputed counts by verdict, session, genre, status, plus confidence distributions
- `_coverage_notes`: documents the 4 duplicates and 1 unevaluated book

The handoff document (NEXT.md) contains 9 systematic findings written by the Session 7 evaluator. These were synthesized incrementally — each session built on the prior one's handoff — and never received independent review. Your job is to verify them independently against the JSON data, not inherit them uncritically.

**Verdict scale (5 levels):**
- VERIFIED — 2+ independent web sources confirm pipeline output. Ground truth candidate.
- PLAUSIBLE — 1 source or cross-check consistent. No red flags but not fully confirmed.
- UNVERIFIABLE — No independent sources found. Reasonable output but unconfirmed.
- FLAG — Evidence suggests output may be wrong.
- ESCALATE — Contradictory evidence. Requires owner domain expertise.
</what_exists>

<what_you_must_produce>
A single report: `PHASE_C_AGGREGATION_REPORT.md`

**Section 1 — Verdict Summary**
Summary table with per-session counts (not all 76 rows — the JSON already has the full data). Confirm the final counts: 59V / 17P / 0F / 0E (or correct them if the data says otherwise). Note the 4 duplicate evaluations and 1 unevaluated book.

**Section 2 — Statistical Analysis**
Compute your own statistics from the JSON data (use Python — do not manually count). The `_statistics` section is a starting point, but verify it and add analysis it doesn't cover:
- Verdict distribution by genre: which genres are always VERIFIED? Which have PLAUSIBLE? Why?
- Verdict distribution by status: success vs gate_abort — does status correlate with verdict? (Careful: this might be selection bias — famous books tend to gate_abort on the author-science mismatch bug)
- Confidence calibration: do author/genre confidence scores discriminate between easy and hard cases? What is the lowest confidence that received VERIFIED? The highest that received PLAUSIBLE?
- Trust tier analysis: for the 22 success books, what drives flagged (12) vs verified (10)?
- ML disagreement analysis: the 4 ML disagreements — are they all the tahqiq_note pattern?

**Section 3 — Systematic Findings (independently derived)**
NEXT.md lists 9 findings. For each one:
- Verify it against the JSON data with actual queries (e.g., `all(v['author_correct'] for v in verdicts)`). Do not simply restate NEXT.md.
- Check for findings the prior sessions might have missed. Look at the full 76-book data set for patterns that only emerge at scale. Specific queries to try:
  - Do books with higher author confidence always get VERIFIED? What's the threshold?
  - Do GPT-5.4 books (6 verdicts) behave differently from Command A books (70 verdicts)?
  - Is Session 5 (6 PLAUSIBLE) genuinely harder books, or was the evaluator more conservative?
  - Do books with pass-through death dates have higher confidence than those without?
  - What's the correlation between genre confidence and verdict?
- If you find a 10th (or 11th) pattern, document it.

**Section 4 — Engine Improvement Recommendations**
Prioritized list of what should be fixed before Step 4 (the 150-book calibration run at €20-30). For each:
- What is the problem?
- What is the evidence (specific book examples)?
- What is the proposed fix (specific enough for Claude Code to implement)?
- Priority: must-fix before Step 4 / should-fix / nice-to-have

**Section 5 — Ground Truth Candidates**
Which of the 59 VERIFIED books should become ground truth for calibration? Flag any VERIFIED books where classification is technically correct but imprecise enough to be problematic as ground truth. (Example: genre=tabaqat for a jarh wa ta'dil work is correct but imprecise — using it as ground truth trains the pipeline to prefer the imprecise label.)

**Section 6 — Phase C Conclusion**
Overall assessment: is the source engine ready for Step 4? What are the remaining risks? What confidence level do you have in the pipeline's output quality?
</what_you_must_produce>

<instructions>
1. Clone the repo: `git clone https://{token}@github.com/rayanino/kr.git`
   (The GitHub token is in project knowledge.)

2. Read these files in this order:
   a. NEXT.md — the aggregation handoff (contains 9 findings to verify, session totals, engine bugs)
   b. PHASE_C_ERRATA.md — corrections that override the evaluation framework
   c. phase_c_collection/PHASE_C_ALL_VERDICTS.json — the verdict data (READ VIA PYTHON, not cat — the file is 73KB)

3. You do NOT need to read the individual session reports (PHASE_C_SESSION1_REPORT.md through SESSION7_REPORT.md). The JSON contains all the verdict data. NEXT.md contains all the findings. Only read a session report if you find a specific discrepancy you need to trace.

4. You do NOT need to read PHASE_C_EVALUATION_FRAMEWORK.md. The verdict scale is defined above. The framework was for evaluators, not aggregators.

5. Use Python to query the JSON. Do not dump the entire file into context. Example:
   ```python
   import json
   with open('phase_c_collection/PHASE_C_ALL_VERDICTS.json') as f:
       d = json.load(f)
   verdicts = d['verdicts']
   # Query what you need
   ```

6. Web search is NOT needed. All data comes from the JSON and NEXT.md.

7. Commit the report when done.
</instructions>

<critical_corrections>
These corrections from PHASE_C_ERRATA.md affect how you interpret the data:

1. result.json author confidence is ALWAYS 1.0 — this is an engine bug. The JSON file already uses the correct values from llm_responses/.

2. Consensus agreed=true does NOT mean models agree on everything. Consensus only checks author + genre + attribution. ML, authority_level, and science_scope are NOT checked. This means ML disagreements coexist with consensus=agreed.

3. Shamela-ecosystem sources (shamela.ws, ketabonline.com, turath.io, waqfeya.net) count as ONE source collectively for VERIFIED threshold. VERIFIED requires 2+ genuinely independent sources.

4. 6 books have consensus.agreed=false: 3 are name-format-only (not substantive), 3 are partially substantive. All are documented in the JSON.
</critical_corrections>

<quality_standards>
The owner values depth over speed. Take as long as needed.

This report determines whether a €20-30 calibration run proceeds on 150 books. An overconfident "ready" assessment wastes budget on a broken engine. An overly cautious "not ready" delays progress unnecessarily. Be honest about what the data shows.

The 9 findings in NEXT.md were synthesized by a chain of Claude Chat sessions, each seeing only its own batch. You are the first session to see all 76 books together. If the chain introduced drift or missed patterns, you are the one who catches it.
</quality_standards>
