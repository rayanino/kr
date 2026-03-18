# KR Pre-Handoff Foundation Verification

**Authority:** This protocol is mandatory before committing ANY CC handoff (NEXT.md). Learned from Session 2 normalization engine handoff (March 2026): the initial handoff was committed without verification. Pre-commit critical review found 4 real issues — regex range check, metadata page detection conflation, missing field on CleanedPage, image-only pages dropped from pipeline. All 4 would have caused CC to build on a broken foundation. CC implemented all 4 fixes correctly BECAUSE they were caught before handoff.

**Rule:** Write handoff → verify foundation with tools → fix handoff → THEN commit. Never commit an unverified handoff.

---

## Mandatory verification steps

### 1. Regex verification

For every regex mentioned in the handoff, construct test inputs and run them in Python:
- Inputs that SHOULD match
- Inputs that should NOT match (boundary values)
- Inputs with edge cases (no quotes, extra attributes, self-closing, etc.)

Print results. Fix the handoff if the regex behavior doesn't match what you described.

### 2. Data flow tracing

For every intermediate data structure defined in the handoff:
- Trace what each downstream pass needs from it
- Verify every needed field is present
- Check for fields that exist in one structure but are lost in the transition to the next

The Session 2 review found `has_footnote_separator` was lost between `SeparatedPage` and `CleanedPage` — Pass 6 needed it but it wasn't carried through. This was invisible from reading the handoff; only tracing the data flow caught it.

### 3. Parser/library empirical verification

For every external library or parser the handoff relies on (BS4, lxml, regex engines):
- Write a test script that exercises the exact use case with Arabic text
- Verify diacritics preservation, entity handling, Unicode behavior
- Run it. Don't assume it works from documentation.

The Session 2 review ran 6 empirical BS4+lxml tests with Arabic diacritics. All passed — but if they hadn't, we'd have caught it before CC wasted a session building on a broken parser.

### 4. Adversarial read (already in handoff skill, but now AFTER verification)

Re-read the handoff as CC would. The 4 questions:
1. Is there any judgment call not covered by the SPEC?
2. Is there any file I'd need that isn't in "Read First"?
3. Is there any ambiguity about what "done" means?
4. Could I follow these instructions and produce something wrong that passes verification?

This step now runs AFTER the foundation checks, so you can answer question 4 with empirical evidence, not intuition.

---

## Anti-pattern: "commit now, verify later"

The handoff skill's adversarial read (question 4) is insufficient alone. It's an introspective check — you're asking yourself "could this go wrong?" after writing the handoff. The Session 2 experience proved that introspective review misses concrete technical issues that 5 minutes of tool-based verification catches. The regex range check, the metadata page conflation, the missing CleanedPage field — none of these were found by the adversarial read. All were found by running code.

**The protocol is: tools first, introspection second, commit third.**
