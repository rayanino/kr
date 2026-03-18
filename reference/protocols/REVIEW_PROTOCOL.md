# KR Review Protocol — Mandatory Two-Pass Review

**Authority:** This protocol overrides single-pass reviews. Every CC review MUST follow both passes. Learned from Session 2 normalization engine review (March 2026): single-pass review read 1,900 lines of code, found one marginal test-input style issue, nearly blocked incorrectly. Deep second pass found the ضياء السالك commentary collision, verified `[0-9]` vs `\d` correctness, and confirmed Format B handling — real substantive findings the first pass missed entirely.

**SESSION 3 ADDENDUM (March 2026):** The architect approved Session 3 twice with unfixed findings. A SPEC inconsistency was labeled "architect action item" instead of a finding. A cross-engine contract break (passaging `DivisionPathEntry.heading_level ge=1` vs normalization's new `ge=0`) was missed entirely because the review never opened downstream engine contracts. The three rules below exist because of this failure.

**RULE 1: NO DEFERRED FINDINGS.** "Architect action item," "maintenance item," "future cleanup," and "next SPEC pass" are BANNED labels. They are "non-blocking finding" in disguise. If something is wrong, fix it now or classify it as a finding that blocks. There is no third option.

**RULE 2: FIX BEFORE VERDICT.** The verdict is the LAST thing in the review, after ALL fixes are committed and pushed. Never deliver a verdict with uncommitted fixes. Never deliver a verdict with a list of "things to fix after." The repo must be clean when the verdict is spoken.

**RULE 3: CROSS-ENGINE BOUNDARY CHECK.** When a CC session modifies any contract type (Pydantic model, enum, field constraint), the reviewer MUST open every file that imports or references that type across ALL engines. Run `grep -rn "TypeName\|field_name" engines/ --include="*.py"` and verify every consumer accepts the new shape. This is mandatory, not optional. The Session 3 `heading_level ge=1 → ge=0` change in normalization would have crashed passaging at runtime — discovered only because the owner forced a deeper review.

---

## Pass 1 (Structural): Read all code, run tests, check SPEC refs

1. Pull repo. Read commit diff. Inventory deliverables vs NEXT.md.
2. Open and read every file CC created or modified — full content, no skimming.
3. For each function: does it implement the SPEC rule it cites? Check error codes, data structures, field propagation.
4. Run the full test suite. Verify zero regressions on prior sessions.
5. Cross-reference against governing docs (SPEC, contracts, SHAMELA_HTML_REFERENCE, adversarial catalog).
6. **Cross-engine boundary check (RULE 3):** For every contract type or enum modified, grep across all engines. Open each consumer. Verify compatibility. This step is not "if time permits" — it is mandatory.

**Pass 1 produces:** A structural understanding of the code, a preliminary list of concerns, and a confirmed cross-engine compatibility report.

---

## Pass 2 (Adversarial): Construct probing inputs, run empirically

Pass 2 is mandatory. It cannot be skipped. Pass 2 tests what Pass 1 cannot see: the behavioral interactions BETWEEN functions.

### Mandatory probing categories (do ALL of these):

**A. Regex edge cases.** For EVERY regex in the new code, construct inputs at the exact boundary of what should/shouldn't match. Run them in Python. Print results. Example: Session 2's footnote separator regex `\d{2,3}` matches width=79 (out of range) — only a post-capture range check makes it safe. This was caught by probing, not by reading.

**B. Data flow tracing.** Pick 2-3 fields that flow through multiple processing stages. Construct inputs that exercise the full flow. Print intermediate values. Example: `known_fn_numbers` flows from Pass 2 → Pass 3 and gates which `(N)` markers get replaced. Tracing this through a page with orphan refs reveals whether the guard works.

**C. Corpus edge cases.** Identify the 2-3 trickiest real-world patterns from SHAMELA_HTML_REFERENCE or domain knowledge. Construct inputs simulating them. Run through the pipeline. Example: ضياء السالك's 3-layer structure with `<hr><s0>` commentary separator and overlapping `(N)` numbering between commentary and footnotes.

**D. Fixture spot-checks.** Pick 2-3 pages from DIFFERENT real fixtures. Run them through the pipeline. **Print actual output** — first 200-500 chars of `primary_text`, footnote texts, structural markers, warnings. Read the output as a HUMAN would. Does the text look correct? Are footnotes properly separated? Do headings appear where expected? This catches semantic errors that structural tests miss.

**E. Cross-engine data flow.** For data that flows to downstream engines (division_tree → passaging, StructuralMarkers → passaging, quality_report → passaging): construct a realistic output from the current session and verify it would deserialize into the downstream engine's contract types without error. This prevents the Session 3 failure where normalization produced `heading_level=0` but passaging's `DivisionPathEntry` rejected it.

### Pass 2 success criteria:

- At least 3 probing scripts run with concrete inputs
- At least 2 fixture pages spot-checked with printed output
- Cross-engine compatibility verified for every modified contract type
- If Pass 2 finds nothing after genuine probing, that is a valid outcome — do NOT manufacture findings
- If Pass 2 finds something, it blocks. No "non-blocking" classification.

---

## Verdict rules

**Two verdicts only: ACCEPT or BLOCKED.**

**ACCEPT means:** zero unfixed findings in the repo. All fixes committed and pushed. Cross-engine boundaries verified. The repo is clean RIGHT NOW.

**BLOCKED means:** at least one finding exists. State what must be fixed. Prepare a fix directive.

**Banned verdicts and labels:**
- "ACCEPT WITH FIXES" — banned. This is how real problems get rationalized away.
- "Non-blocking finding" — banned. If it was worth writing down, it blocks.
- "Architect action item" — banned. This is "non-blocking" in a different costume.
- "Maintenance item" / "future cleanup" / "next pass" — banned. Fix it now or it's a finding.

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
