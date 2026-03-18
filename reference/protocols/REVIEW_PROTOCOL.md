# KR Review Protocol — Mandatory Two-Pass Review

**Authority:** This protocol overrides single-pass reviews. Every CC review MUST follow both passes. Learned from Session 2 normalization engine review (March 2026): single-pass review read 1,900 lines of code, found one marginal test-input style issue, nearly blocked incorrectly. Deep second pass found the ضياء السالك commentary collision, verified `[0-9]` vs `\d` correctness, and confirmed Format B handling — real substantive findings the first pass missed entirely.

---

## Pass 1 (Structural): Read all code, run tests, check SPEC refs

1. Pull repo. Read commit diff. Inventory deliverables vs NEXT.md.
2. Open and read every file CC created or modified — full content, no skimming.
3. For each function: does it implement the SPEC rule it cites? Check error codes, data structures, field propagation.
4. Run the full test suite. Verify zero regressions on prior sessions.
5. Cross-reference against governing docs (SPEC, contracts, SHAMELA_HTML_REFERENCE, adversarial catalog).

**Pass 1 produces:** A structural understanding of the code and a preliminary list of concerns.

---

## Pass 2 (Adversarial): Construct probing inputs, run empirically

Pass 2 is mandatory. It cannot be skipped. Pass 2 tests what Pass 1 cannot see: the behavioral interactions BETWEEN functions.

### Mandatory probing categories (do ALL of these):

**A. Regex edge cases.** For EVERY regex in the new code, construct inputs at the exact boundary of what should/shouldn't match. Run them in Python. Print results. Example: Session 2's footnote separator regex `\d{2,3}` matches width=79 (out of range) — only a post-capture range check makes it safe. This was caught by probing, not by reading.

**B. Data flow tracing.** Pick 2-3 fields that flow through multiple processing stages. Construct inputs that exercise the full flow. Print intermediate values. Example: `known_fn_numbers` flows from Pass 2 → Pass 3 and gates which `(N)` markers get replaced. Tracing this through a page with orphan refs reveals whether the guard works.

**C. Corpus edge cases.** Identify the 2-3 trickiest real-world patterns from SHAMELA_HTML_REFERENCE or domain knowledge. Construct inputs simulating them. Run through the pipeline. Example: ضياء السالك's 3-layer structure with `<hr><s0>` commentary separator and overlapping `(N)` numbering between commentary and footnotes.

**D. Fixture spot-checks.** Pick 2-3 pages from DIFFERENT real fixtures. Run them through the pipeline. **Print actual output** — first 200-500 chars of `primary_text`, footnote texts, structural markers, warnings. Read the output as a HUMAN would. Does the text look correct? Are footnotes properly separated? Do headings appear where expected? This catches semantic errors that structural tests miss.

### Pass 2 success criteria:

- At least 3 probing scripts run with concrete inputs
- At least 2 fixture pages spot-checked with printed output
- If Pass 2 finds nothing after genuine probing, that is a valid outcome — do NOT manufacture findings
- If Pass 2 finds something, it blocks. No "non-blocking" classification.

---

## Verdict calibration

**Two verdicts only: ACCEPT or BLOCKED.**

After a genuine two-pass review:
- Finding nothing material IS valid — rigor comes from depth of probing, not number of findings
- Finding something marginal and elevating it to blocking to look thorough is DISHONEST — it's "blocking manufacture," the inverse of the "non-blocking rationalization" failure
- Finding a real behavioral interaction bug is the expected outcome — bugs hide between functions, not inside them

---

## Cumulative build metrics (report in every review)

```
Total implementation lines: [N] (this session added [M])
Total test count: [N] (this session added [M])
Test-to-code ratio: [N tests per 100 lines]
SPEC sections implemented: [list]
SPEC sections remaining: [list]  
Adversarial cases covered: [N/51]
```

Flag drift: >200 new lines with <10 new tests = problem. Ratio dropping below 0.5 tests per 100 lines = problem.
