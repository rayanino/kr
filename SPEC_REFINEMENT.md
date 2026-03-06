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

### Step 2: Threat Analysis (KNOWLEDGE_INTEGRITY.md)

Read `KNOWLEDGE_INTEGRITY.md` with this SPEC's domain in mind:

For each of the 7 threats:
1. Does this SPEC explicitly address this threat?
2. Is the mitigation specific enough to implement?
3. Could this engine's output contribute to this threat downstream?
4. Is there a failure mode in this engine that could silently corrupt the library?

**Write down every unaddressed threat.** These are defects.

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

### Step 4: Technology Review

For each processing step in §4:
- Does it name the specific tool, library, or technique?
- Is this still the best available tool? (Search the web — tools evolve.)
- Could a newer tool do this better? (Search: `[capability] Arabic 2025 2026`)
- Is there a tool the SPEC misses entirely?

Update `reference/RESOURCES.md` with any new findings.

**Write down every missing or outdated technology reference.** These are defects.

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

### Step 7: Self-Review (Two Rounds)

**Round 1: Fix all defects found in Steps 1-6.**
Apply the fixes directly to the SPEC. For each fix, verify it doesn't introduce new inconsistencies.

**Round 2: Re-read the fixed SPEC from the top.**
This time, read specifically for:
- Did the fixes introduce new ambiguities?
- Is the SPEC still internally consistent?
- Are the cross-references (§N.N, D-NNN) still correct?
- Run the Three Challenges from CHALLENGE_PROTOCOL.md.

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

Commit the refined SPEC with a message describing:
- How many defects were found and fixed
- How many new capabilities were invented (from Step 0)
- What research was conducted (search count and key findings)
- Whether another refinement cycle is needed

If >5 structural defects were found, another cycle is needed. Schedule it in NEXT.md.
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
