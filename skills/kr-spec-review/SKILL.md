---
name: kr-spec-review
description: Handle owner domain comments on KR engine SPECs with mandatory research. Use for "handle comment", "comment #N", numbered feedback, or any SPEC domain correction.
---

# KR SPEC Review — معالجة تعليقات المواصفات

You are processing the owner's domain comments on a KR engine SPEC. The owner is an Islamic studies student with deep domain knowledge but no technical background. His comments are domain corrections: "this doesn't match how scholars actually do X" or "you're missing Y." Your job is to translate his domain insight into precise SPEC changes — with research.

## The Core Rule

**Every non-trivial comment gets research before you respond.** Do not rely on your training data for Islamic scholarly conventions, Arabic text processing, or existing tool capabilities. Search first. The owner's comment is a signal that your training data may be wrong.

Trivial = typo, formatting, or a factual correction the owner provides directly (e.g., "Ibn Aqil died in 769 AH, not 772 AH"). For trivial comments, apply directly and move on.

Non-trivial = anything about behavior, design, edge cases, scholarly conventions, or capabilities. These get the full treatment below.

---

## Procedure

### Step 1: Understand the Comment

Read the comment. Restate it in your own words. Identify:
- **What the owner is saying:** The domain claim or correction
- **What SPEC text it affects:** Quote the specific section and lines
- **What category it is:** One of:
  - DOMAIN CORRECTION — the SPEC contradicts how Islamic scholarship actually works
  - MISSING CASE — the SPEC doesn't handle something the owner knows exists
  - DESIGN CHALLENGE — the owner questions whether the approach will work
  - PRIORITY/SCOPE — the owner says something is more/less important than the SPEC implies
  - CLARIFICATION — the owner doesn't understand what the SPEC means (this is a SPEC clarity failure, not a user failure)

### Step 2: Research (Mandatory for Non-Trivial)

Before forming an opinion, conduct at minimum 3 searches:

**Search 1 — Domain verification:** Verify the owner's domain claim. Search for the specific Islamic scholarly convention, text type, or practice the comment references. You are not the domain expert — confirm what the owner says is standard practice.

**Search 2 — Existing solutions:** Search for how other Arabic text systems or digital humanities projects handle this case. Prioritize: OpenITI, KITAB, Shamela, HathiTrust Arabic, Perseus Digital Library (for analogous classical text problems).

**Search 3 — Technical feasibility:** If the comment implies a capability (detection, classification, extraction), search for whether existing tools or models can do it. Name specific libraries, models, or techniques.

For complex comments, do more searches. The minimum is 3, not the target.

### Step 3: Analyze Impact

Before proposing changes, assess:

1. **Downstream cascade:** If this SPEC section changes, what breaks downstream? Check the output contract — does the change affect what downstream engines expect?
2. **Edge case expansion:** Does the owner's comment reveal a class of similar issues? Example: if the comment is "sharh texts have two authors," the class is "all multi-layer texts" (hashiya, ta'liq, taqrir).
3. **The creative question:** What could this change ENABLE? Don't just fix the defect — ask whether the fix opens a door to something transformative. If the owner says "you need to detect isnads," the fix is isnad detection, but the opportunity is automatic hadith chain analysis.

### Step 4: Propose Resolution

Present your response as:

```
## Comment #N: [Brief Title]

**Owner says:** [Restate the comment]
**Research findings:** [What you learned from searches, with sources]
**Impact analysis:** [Downstream effects, edge cases, opportunities]

**Proposed change:**
[The exact replacement SPEC text — not a description of what to change,
but the actual words that should go into the SPEC]

**What this enables:** [The creative opportunity, if any]

**Open questions for owner:** [If the domain implications aren't clear to you]
```

### Step 5: Track for Finalization

After each comment resolution, maintain a running summary:

```
### Comment Resolution Log
| # | Section | Category | Status | Key Change |
|---|---------|----------|--------|------------|
| 1 | §4.A.2  | DOMAIN   | Resolved | Added sharh/matn layer detection |
| 2 | §2      | MISSING  | Open — needs owner input on scope |
```

This log feeds directly into the kr-finalize skill.

---

## Handling Batches of Comments

When the owner provides multiple comments at once:

1. **Read ALL comments first** before responding to any. Comments may interact — one comment may answer another, or two comments may point to the same underlying issue.
2. **Group related comments** that affect the same SPEC section or the same conceptual issue. Resolve them together.
3. **Flag conflicts** if two comments suggest contradictory changes. Present both to the owner with your analysis of the trade-off.
4. **Prioritize** domain corrections over design challenges. Get the domain facts right first; then assess design implications.

---

## Anti-Patterns to Avoid

**The Eager Agree.** The owner says "X should work differently." You immediately say "Great point! I'll change X." STOP. Research first. The owner might be right about the domain but wrong about the implication. Or there might be a better solution than the one the comment implies.

**The Scope Dodge.** The owner raises a hard problem. You say "That's a great observation, we can address it in a future version." NO. If the comment reveals a flaw in the SPEC, the SPEC needs fixing now. Deferral is only acceptable if the fix requires capabilities from a different engine.

**The Surface Fix.** The owner says "you're missing case X." You add case X to the list. But you don't check whether the SPEC's processing rules actually HANDLE case X — you just added it to the input contract. The fix must be end-to-end: if a new input type is recognized, the processing rules must handle it, the output must include it, and the error handling must cover its failure modes.

**The Confidence Bluff.** You don't actually know whether a library supports Arabic. You write "CAMeL Tools handles this." STOP. Search and verify. If you can't find evidence it works, say so.

---

## When You Need More Context

If the owner's comment references something you need to understand better:
- **SPEC context:** Read the relevant SPEC section in the project knowledge files
- **Domain context:** ASK THE OWNER. You are not an Islamic scholar. Questions like "Is this convention specific to Hanafi fiqh or universal?" are exactly right.
- **Architectural context:** Read STEERING.md or the relevant decision in kr_decisions.md
- **Cross-engine impact:** Read the upstream/downstream engine's input/output contract

---

## Quality Check Before Responding

Before sending your response, verify:

- [ ] Every non-trivial comment has at least 3 searches documented
- [ ] Research findings cite specific sources, not vague claims
- [ ] Proposed SPEC text is precise enough for Claude Code to implement (Criterion #1 from the Perfection Standard: zero ambiguity)
- [ ] Every sentence in the proposed text is a binding rule or a marked open question (Criterion #2)
- [ ] Edge cases from the same class as the comment are addressed, not just the specific case
- [ ] Downstream impact is assessed — no silent contract breaks
- [ ] The creative opportunity question was asked, even if the answer is "none"
- [ ] Open questions for the owner are clear and specific
