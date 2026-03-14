Halt. Do not respond to the user yet. Execute the review protocol below first.

<round_detection>
Count how many times the EXACT string "Self-review findings (Round" appears earlier in this conversation.
- 0 occurrences → you are in ROUND 1
- 1 occurrence → you are in ROUND 2
- 2 occurrences → you are in ROUND 3
- 3 occurrences → you are in ROUND 4

Execute ONLY your current round. Each round attacks from a fundamentally different angle.
</round_detection>

<review_mandate>
This aggregation report determines whether a €20-30 calibration run proceeds on 150 books. An arithmetic error in statistics, an unverified finding, or a poorly justified recommendation has direct budget consequences. Every number is assumed wrong until recomputed. Every finding is assumed inherited rather than verified until proven otherwise.
</review_mandate>

---

<round_1>
## ROUND 1 — DATA VERIFICATION
**Angle:** "Did I actually verify every claim against the JSON, or did I just restate what NEXT.md told me?"

**Step 1: Recompute ALL statistics from the JSON independently.**
Run a script that reads phase_c_collection/PHASE_C_ALL_VERDICTS.json and computes:
- Total V/P/F/E (must equal 59/17/0/0)
- Per-session counts (must match the table in the report)
- Per-genre counts
- Per-status counts (success vs gate_abort)
- Author confidence: min, max, mean, median
- Genre confidence: min, max, mean, median
- ML disagreement count
- Consensus disagreement count

Compare EVERY number against what the report states. If ANY number differs, fix it.

**Step 2: Verify each of the 9 findings against the JSON.**
For each finding from NEXT.md that the report includes:
- Was it verified by querying the JSON data, or just restated?
- Can you point to the specific JSON entries that support it?
- Example: "Zero author errors" — run: `all(v['author_correct'] for v in verdicts)`. Did you actually do this, or just write "confirmed"?

**Step 3: Check Section 1 (Verdict Summary) completeness.**
- Does the summary table have per-session counts that sum to 76?
- Are the 4 duplicates noted?
- Is the 1 unevaluated book (أمالي المحاملي) flagged?
- Does the total match 59V + 17P = 76?

**Step 4: Check required sections.**
The prompt specified 6 sections. Confirm each exists AND is substantive (not just a header with a sentence):
1. Verdict Summary
2. Statistical Analysis
3. Systematic Findings (independently derived)
4. Engine Improvement Recommendations
5. Ground Truth Candidates
6. Phase C Conclusion

**Tool requirements:** Minimum 8, including: at least 2 script runs (JSON recomputation), at least 3 greps (report verification), at least 1 file read.
</round_1>

---

<round_2>
## ROUND 2 — ANALYTICAL ATTACK
**Angle:** "Assume every conclusion, every recommendation, and every statistical interpretation is wrong or incomplete."

**Step 1: Attack the statistical interpretations.**
For each statistical claim in Section 2:
- Is the interpretation supported by the numbers, or does it overstate a pattern?
- Are there alternative explanations the report ignores?
- Example: if the report says "gate_abort books are more likely to be VERIFIED" — is that because gate_abort books tend to be famous works (selection bias), not because the gate mechanism correlates with quality?

**Step 2: Attack the findings.**
For each finding in Section 3:
- Does the report add independent analysis, or just confirm what NEXT.md said?
- Are there counter-examples in the data that the finding ignores?
- Is the finding actionable, or just an observation?
- Did the report find ANY new pattern that NEXT.md missed? If not, was the aggregation session doing its job?

**Step 3: Attack the recommendations.**
For each recommendation in Section 4:
- Is the priority justified? Could a "must-fix" actually be "nice-to-have"?
- Is the proposed fix specific enough for Claude Code to implement?
- Does the recommendation have unintended consequences? (e.g., auto-correcting tahqiq ML could mask a real multi-layer book that happens to have a muhaqiq)
- Are there recommendations that should be there but aren't?

**Step 4: Attack the ground truth selection.**
For Section 5:
- Are there VERIFIED books with imprecise classifications that could poison ground truth?
- Are there PLAUSIBLE books that should actually be VERIFIED (or vice versa)?
- Is the selection criteria explicit and reproducible?

**Step 5: Attack the conclusion.**
For Section 6:
- Does the go/no-go recommendation follow from the evidence?
- Are the "remaining risks" actually the biggest risks, or are important ones missing?
- Would a skeptical reader agree with the confidence level?

**Tool requirements:** Minimum 6, including: at least 2 script runs (data cross-checks), at least 2 greps (claim verification).
</round_2>

---

<round_3>
## ROUND 3 — MISSING PATTERN SEARCH
**Angle:** "The 7 individual sessions each saw only their own batch. What patterns only emerge when you see all 76 books together?"

This is the highest-value round. The entire purpose of aggregation is to find what individual sessions missed.

**Step 1: Query the JSON for patterns the report doesn't mention.**
Run queries looking for:
- Genre confidence vs verdict: are low-genre-confidence books always PLAUSIBLE?
- Author confidence vs verdict: same analysis
- Trust score distribution: what separates flagged from verified?
- Science scope breadth: do books with more sciences tend to be gate_abort?
- Model pair effect: do the 6 GPT-5.4 books behave differently from the 70 Command A books?
- Session effect: is Session 5 (6 PLAUSIBLE) genuinely harder, or was the evaluator more conservative?
- Death date availability: do books with pass-through death dates have higher author confidence?

**Step 2: Cross-genre analysis.**
- Which genre has the highest PLAUSIBLE rate? Why?
- Are there genres with 100% VERIFIED? Is that because they're easy, or because they were tested on famous works only?
- Do genre confidence scores differ meaningfully across genres?

**Step 3: Cross-session consistency.**
- If the same author appears in multiple sessions, are the evaluations consistent?
- Are confidence thresholds applied consistently across sessions? (Early sessions might be stricter/looser than later ones)
- Does the quality of evaluation improve across sessions (learning effect)?

**Step 4: If you find a new pattern, add it to the report.**
If you don't find any new patterns, report that honestly — it means the individual sessions were thorough. But try hard before concluding this.

**Tool requirements:** Minimum 8, including: at least 4 script runs (JSON pattern queries), at least 2 greps.
</round_3>

---

<round_4>
## ROUND 4 — INTEGRITY CERTIFICATION
**Angle:** "Three rounds of edits may have introduced errors. Certify the report is self-consistent and ready for the owner."

**Step 1: Internal contradiction scan.**
Read the full report. Check:
- Do Section 2 statistics match Section 1 table counts?
- Do Section 3 findings match Section 2 analysis?
- Do Section 4 recommendations reference the correct finding numbers?
- Does Section 5 ground truth list match the VERIFIED count in Section 1?
- Does Section 6 conclusion follow from Sections 2-5?

**Step 2: Arithmetic verification.**
- Sum all per-session verdict counts. Must equal 76.
- Sum all per-genre counts. Must equal 76.
- Sum VERIFIED + PLAUSIBLE. Must equal 76.
- Check that confidence statistics (min/max/mean/median) are mathematically consistent.

**Step 3: Verify prior round fixes.**
For each fix from Rounds 1-3, confirm it's actually in the file.

**Step 4: Owner-readability check.**
Read the report as if you are the owner — an Islamic studies student with no technical background. For each section:
- Would the owner understand the conclusion without needing to read the JSON?
- Are recommendations phrased in terms of outcomes, not implementation details?
- Is the go/no-go recommendation clear and justified?

**Tool requirements:** Minimum 6, including: at least 1 full file read, at least 2 greps, at least 1 script run.

This is the FINAL round. Report definitively.
</round_4>

---

<reporting_format>
After completing your round, append this EXACT structure (the round detection depends on this format):

**Self-review findings (Round N):**
**Tool calls used:** [count] — [list each tool and what it checked]
**Errors found and fixed:** [specific corrections — or "None, verified by: [evidence]"]
**Known failure patterns checked:** [which were relevant, which were clean]
**Remaining uncertainty:** [anything unresolved — or "None"]
**Round verdict:** [CLEAN | ERRORS FIXED]
</reporting_format>

<constraints>
- Execute ONLY your current round. Do not skip ahead or combine rounds.
- Meet BOTH the tool call count AND type requirements.
- If you find nothing to fix, list specific things you verified. Do not fabricate issues.
- When uncertain about any number, recompute it. Do not trust your memory.
- The owner reads the final report. Clarity matters as much as accuracy.
</constraints>
