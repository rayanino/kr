# SPEC Refinement Protocol — بروتوكول تنقيح المواصفات

This protocol defines the iterative cycle for hardening each engine SPEC before implementation begins. No engine should be implemented until its SPEC has passed through at least ONE full refinement cycle.

The 14 SPECs were written in the preparatory phase. They are drafts — competent drafts, but they were written before `KNOWLEDGE_INTEGRITY.md`, `CHALLENGE_PROTOCOL.md`, and the skills existed. Every SPEC must be reviewed against these new standards.

---

## The Refinement Cycle

Each SPEC goes through this cycle. One cycle per session (refer to `CONTEXT_BUDGET.md` for token planning). A SPEC may need 1-3 cycles depending on how many issues are found.

### Step 0: Creative Exploration (BEFORE any review)

Follow the Creative Exploration Protocol in `CREATIVE_MANDATE.md`. This step comes FIRST — before reading the SPEC critically, before finding defects, before fixing anything. The goal is to INVENT capabilities, not just review existing ones.

Deliverable: Invention Notes with at least 3 new capabilities, each with named technology and concrete output example.

Minimum research: 8 web searches (3 for problem space mapping, 3 for possibility exploration, 2 for validation).

### Step 1: Cold Read (no code, no other docs)

Read the SPEC as if you have never seen it before. Also read `SILENT_FAILURES.md` — the 7 patterns of "looks right but isn't." Check each §4 rule against these patterns. You are a new Claude Code instance that must implement this engine from this document alone.

Questions to ask during cold read:
- Can I implement this without asking a single clarifying question?
- Is there any sentence I could interpret two different ways?
- Are there any terms I don't understand or that seem inconsistent?
- If I gave this to a different Claude instance, would they build the same system?

**Write down every ambiguity, gap, and confusion.** These are defects.

### Step 1.5: Automated Quality Scan

Run the automated SPEC quality checker to get a concrete defect baseline:

```bash
python3 scripts/check_spec_quality.py engines/<name>/SPEC.md --verbose
```

This detects: vague quantifiers ("multiple", "several", "appropriate"), unbounded lists ("etc."), hand-waving technology references ("using LLM"), missing thresholds ("high confidence"), missing examples in §4 subsections, undefined error codes, and unvalidated writes to the library.

**These are YOUR defect targets.** Every high-severity hit must be evaluated: genuine defect (fix it) or false positive (add context that makes the intent unambiguous). Do not dismiss hits without reasoning.

Output: defect count baseline (e.g., "Source SPEC: 35 high, 6 medium before refinement → target: ≤5 high, ≤3 medium after").

### Step 2: Threat Analysis (KNOWLEDGE_INTEGRITY.md)

Read `KNOWLEDGE_INTEGRITY.md` with this SPEC's domain in mind:

For each of the 7 threats:
1. Does this SPEC explicitly address this threat?
2. Is the mitigation specific enough to implement?
3. Could this engine's output contribute to this threat downstream?
4. Is there a failure mode in this engine that could silently corrupt the library?

**Write down every unaddressed threat.** These are defects.

### Step 2.5: Corruption Risk Assessment

For each data field this engine WRITES to the library (§3 Output Contract):

1. **If this field is wrong, what happens to the user's knowledge?** Categorize:
   - SILENT corruption: the user incorporates wrong information without noticing (e.g., wrong author attribution → Rayane cites wrong scholar for years)
   - VISIBLE corruption: the user will notice something is off (e.g., garbled text → obviously unreadable)

2. **For every SILENT corruption path:** Specify the validation that prevents it in §5. If no validation exists, that's the highest-severity defect — add one.

3. **For every field that enters downstream engines:** What compound errors can it cause? (E.g., wrong `science` classification → wrong taxonomy tree → all excerpts from this source misplaced.)

The goal: for each output field, an implementer can point to the specific validation rule that protects it. "We validate the output" is not enough — WHICH validation catches WHICH corruption?

**Write down every unprotected corruption path.** These are the most critical defects.

### Step 3: Example Audit

For each behavioral rule in §4 (both §4.A and §4.B):
- Is there a concrete input/output example?
- Could an implementer test this rule with the given information?
- Is the example in Arabic (not transliterated, not placeholder text)?

A rule without an example is a rule that will be implemented inconsistently. The SPEC should contain:

```
**Example:**
Input: [concrete input data with real Arabic text]
Processing: [what the engine does, step by step]
Output: [concrete output data with all fields shown]
```

At minimum, every §4.A subsection needs ONE worked example showing the complete transformation from input to output. §4.B capabilities need examples of what the transformative output looks like.

**Write down every rule without a testable example.** These are defects.

### Step 3.5: Machine-Readability Test

For each §4.A rule (core processing rules that Claude Code will implement):

1. Try to write a **function signature** for the rule: what are the inputs (with types), what is the output (with type), what exceptions can it raise?

2. Try to write **pseudocode** for the rule in 5-15 lines. If you need to write `# ???` or `# unclear` or `# assumption:` at ANY point, the rule fails machine-readability.

3. Try to write a **test assertion**: given specific input X, assert output Y. If you can't write a concrete assertion, the rule is untestable.

You don't need to write actual code. You need to VERIFY that code COULD be written without interpretation. Write the pseudocode mentally or in scratch notes. The deliverable is: a list of §4.A rules that fail and WHY.

**Example of a rule that PASSES:**
> "The source engine computes trustworthiness as a weighted sum of 5 factors..."
→ Function: `compute_trust(metadata: SourceMetadata) -> float`
→ Pseudocode: clear formula with defined weights and thresholds
→ Test: `assert compute_trust(metadata_with_no_author) == flagged`

**Example of a rule that FAILS:**
> "The source engine evaluates relevance using content analysis."
→ Function: `evaluate_relevance(???) -> ???`  — what input? what output type?
→ Pseudocode: impossible — "content analysis" is undefined
→ Test: impossible — no criteria for pass/fail

**Write down every rule that fails machine-readability.** These are defects.

### Step 4: Technology Review

For each processing step in §4:
- Does it name the specific tool, library, or technique?
- Is this still the best available tool? (Search the web — tools evolve.)
- Could a newer tool do this better? (Search: `[capability] Arabic 2025 2026`)
- Is there a tool the SPEC misses entirely?

Update `reference/RESOURCES.md` with any new findings.

**Write down every missing or outdated technology reference.** These are defects.

### Step 4.5: Machine-Readable Contract Verification

If the engine has a `contracts.py` file (machine-readable Pydantic models):
- Compare every field in the Pydantic model against the SPEC §3 prose. Mismatches are defects.
- Check: does the Pydantic model have fields the SPEC doesn't mention? (Model is wrong.)
- Check: does the SPEC mention fields the Pydantic model doesn't have? (Model is incomplete.)
- Update the model if the SPEC is authoritative and the model is wrong.
- Update the SPEC if the model reveals a field that should be documented.

If no `contracts.py` exists yet, note this as a gap. Stream 2 of `PREPARATORY_ROADMAP.md` addresses it.

### Step 5: Cross-SPEC Boundary Verification

Read the upstream engine's §3 (Output Contract) and the downstream engine's §2 (Input Contract):
- Does every field this engine expects actually exist in the upstream output?
- Does every field this engine produces match what the downstream expects?
- Is metadata pass-through (D-023) explicitly addressed?
- Run `python3 scripts/verify_metadata_flow.py --boundary <upstream> <downstream>`

**Write down every boundary mismatch.** These are defects.

### Step 6: Scholarly Value Check

Read `reference/ENTRY_EXAMPLE.md` and `reference/USER_SCENARIOS.md`:
- Does this engine contribute to producing entries at the target quality?
- Which user scenarios does this engine serve? Are all of them listed in §1?
- Is there a scholarly capability this engine SHOULD have but doesn't?
- Would a world-class Islamic scholar see anything here that makes them say "I didn't know that was possible"?

**Write down every scholarly value gap.** These are defects.

### Step 7: Self-Review (Two Rounds + Anti-Sycophancy Gate)

**Round 1: Fix all defects found in Steps 1-6.**
Apply the fixes directly to the SPEC. For each fix, verify it doesn't introduce new inconsistencies.

**Round 2: Re-read the fixed SPEC from the top.**
This time, read specifically for:
- Did the fixes introduce new ambiguities?
- Is the SPEC still internally consistent?
- Are the cross-references (§N.N, D-NNN) still correct?
- Run the Three Challenges from CHALLENGE_PROTOCOL.md.

**Anti-Sycophancy Gate (mandatory):**
After Round 2, you will feel the SPEC is good. That feeling is the signal to do this:
1. Pick the §4 subsection you are MOST confident about. Read it as if written by someone else. List 3 specific defects. If you genuinely cannot find 3, the section may be good — but be honest about whether you're not finding defects or not looking hard enough.
2. Count your total defects for this cycle. If the count is <5, re-run Steps 1.5-3.5 on the sections you changed. Low defect counts in a first refinement cycle almost always mean the review was superficial, not that the SPEC is perfect.
3. Run the quality checker AGAIN: `python3 scripts/check_spec_quality.py engines/<n>/SPEC.md`. Compare high-severity count to baseline from Step 1.5. If it didn't decrease by at least 50%, the refinement was cosmetic.

### Step 8: Research Round 2

After fixing all defects, do a second research pass:
- Search for state-of-the-art techniques in this engine's domain
- Search for tools released in the last 6 months
- Search for academic papers on the core algorithms
- Search for what digital humanities projects have done for similar tasks

This second research round often reveals opportunities that the first round missed, because you now understand the SPEC deeply enough to know what to search for.

### Step 9: Silent Failure Check

Read `SILENT_FAILURES.md`. For each of the 7 patterns, check: does any rule in the refined SPEC exhibit this pattern? This is the LAST check before committing — it catches things that the other steps miss because they LOOK correct.

### Step 10: Commit and Document

**Pre-commit quality gate:** Run `python3 scripts/check_spec_quality.py engines/<n>/SPEC.md`. Record the final defect counts. A refined SPEC should have:
- High-severity defects: ≤10 (down from typical draft baseline of 25-40)
- No UNVALIDATED_WRITE defects (every library write must have nearby validation)
- No MISSING_EXAMPLE defects in §4.A (every processing rule has an example)

If these thresholds aren't met, the refinement cycle is incomplete.

Commit the refined SPEC with a message including:
- Defect counts: before → after (from Step 1.5 baseline → Step 10 final)
- How many new capabilities were invented (from Step 0)
- What research was conducted (search count and key findings)
- Whether another refinement cycle is needed

If >5 structural defects remain, another cycle is needed. Schedule it in NEXT.md.
If 0 new capabilities were invented, the session failed the Creative Mandate — schedule a creative-focused session.

---



---

## Gold Standard: Before and After Refinement

This shows what refinement ACTUALLY produces — not just cleaner prose, but fundamentally more implementable rules.

### BEFORE (draft SPEC rule — looks fine, silently fails Pattern #5: Untestable Rule):

> The source engine evaluates the source's trustworthiness using multiple factors including edition quality, author reputation, and publisher reliability, and assigns a trust score.

Problems: "multiple factors" is vague. "Including" means the list is incomplete. "Edition quality" and "author reputation" have no definition. An implementer would guess.

### AFTER (refined rule — concrete, testable, every path defined):

> The source engine computes a trustworthiness score as a weighted sum of five factors, each scored 0.0–1.0:
>
> (1) `author_verified` (weight 0.30): 1.0 if the author's `canonical_id` matches a verified record in the scholar authority registry; 0.5 if matched with confidence ≥0.80 but unverified; 0.0 if unmatched. Example: ابن قدامة المقدسي matches `sch_00042` → 1.0.
>
> (2) `muhaqiq_present` (weight 0.25): 1.0 if a tahqiq editor is named in the source metadata; 0.0 if absent. Example: تحقيق: عبد الله التركي → 1.0.
>
> (3) `publisher_known` (weight 0.20): 1.0 if the publisher appears in the known-publishers list (`reference/known_publishers.json`); 0.5 if the publisher field is present but not in the list; 0.0 if absent.
>
> (4) `edition_indicator` (weight 0.15): 1.0 if edition number ≥2 (reprints indicate demand); 0.5 if edition 1; 0.0 if unknown.
>
> (5) `text_completeness` (weight 0.10): 1.0 if all expected volumes are present; proportional if partial (e.g., 12/15 volumes → 0.8); 0.0 if unknown.
>
> Combined score = Σ(weight × factor). Sources scoring ≥0.65 are `verified` (excerpts default to trusted). Sources scoring <0.65 are `flagged` (excerpts default to flagged, requiring human review). If ANY individual factor is 0.0, the source is `flagged` regardless of combined score — a single missing critical signal overrides the aggregate.
>
> Error: if factor computation fails (e.g., scholar authority lookup timeout), that factor defaults to 0.0 and a warning `SRC_TRUST_FACTOR_FAILED` is logged with the factor name. The remaining factors are still computed.

Notice: every factor has a name, weight, range, and concrete example. The aggregation formula is explicit. The error path is defined. The threshold is a number, not "low" or "high." An implementer can write this function and its test suite without asking a single question.

### What Changed

| Aspect | Before | After |
|--------|--------|-------|
| Factors | "multiple" (unknown count) | 5 named factors with weights |
| Scoring | "assigns a trust score" | Weighted sum formula with range |
| Thresholds | Absent | ≥0.65 verified, <0.65 flagged |
| Examples | None | Arabic text examples for each factor |
| Error handling | Absent | Factor failure → 0.0 + warning |
| Testability | Untestable | Write test in 5 minutes |

## Refinement Tracking

Track refinement status in each engine's CLAUDE.md:

```
## SPEC Refinement Status
- Cycle 1: [date] — [N defects found, N fixed, research: Y/N]
- Cycle 2: [date] — [N defects found, N fixed, research: Y/N]
- Implementation-ready: YES/NO
```

A SPEC is implementation-ready when a refinement cycle finds ≤2 minor defects.

---

## When to Trigger Refinement

- **Before implementation:** Every SPEC must pass at least one refinement cycle.
- **After implementation reveals issues:** If Claude Code reports SPEC ambiguities (via `# SPEC-AMBIGUITY` comments), the SPEC needs another cycle.
- **After new protocols are added:** If KNOWLEDGE_INTEGRITY.md or CHALLENGE_PROTOCOL.md gain new threats or challenges, all SPECs should be spot-checked.
- **After technology changes:** If RESOURCES.md is updated with a tool that affects an engine, that SPEC should be reviewed.

---

## Priority Order for Refinement

Refine in pipeline order (upstream first), because upstream SPECs define the data that downstream SPECs consume:

1. Source engine SPEC
2. Normalization engine SPEC
3. Shared components (consensus, validation, human_gate) — used by all engines
4. Passaging engine SPEC
5. Atomization engine SPEC
6. Excerpting engine SPEC
7. Taxonomy engine SPEC
8. Synthesis engine SPEC
9. Remaining shared components (feedback, user_model, scholar_authority)
10. Scholar interface SPEC
