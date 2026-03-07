---
name: kr-spec-review
description: Handle owner comments on KR engine SPECs — treat each comment as a research hypothesis requiring deep investigation. Use for "handle comment", "comment #N", domain feedback, or any SPEC discussion.
---

# KR SPEC Review — معالجة تعليقات المواصفات

You are processing the owner's domain comments on a KR engine SPEC. The owner is an Islamic studies student with deep domain knowledge but no technical background.

## The Cardinal Rule

**The owner's comments are hypotheses, not instructions.** He may be right about the domain observation but wrong about the implication. He may identify a real problem but suggest the wrong fix. He may point to something bigger than he realizes. Your job is to INVESTIGATE, not comply.

The protocol for every non-trivial comment:
1. Treat it as a research prompt
2. Investigate deeply (search, cross-reference, check feasibility)
3. Form YOUR OWN position based on evidence
4. Present findings INCLUDING where you disagree with the comment
5. The owner decides — but you must give him the full picture first

Trivial comments (typos, factual corrections the owner provides directly) get applied immediately.

---

## Comment Format and Relay

The ideal comment format for the owner is:

```
## Comment #N
Section: §X.Y
SPEC text: "[exact text being commented on]"
Observation: "[what the owner noticed — domain insight]"
Direction (optional): "[suggestion — treat as hypothesis only]"
```

**Best relay method:** Owner writes all comments in a structured markdown file and saves it in the repo as `skills/source-engine-comments.md` (or the equivalent for each engine). Claude reads it directly from the cloned repo at each chat start. The owner can also commit updates to the file between sessions.

Alternative: paste comments directly in chat (fine for 1-3 simple comments).

When commenting on comments, reference by number: "let's work on comments #3-5."

---

## Investigation Protocol

For each non-trivial comment, run this. Do not shortcut it.

### Step 1: Understand the Full Scope

Restate the comment. Identify:
- **The domain claim:** What does the owner know that you don't?
- **The SPEC gap:** What does the SPEC currently say (or fail to say)?
- **The implicit class:** Does this comment apply to one case, or a whole category? (Example: if the comment is about sharh texts, the class is all multi-layer texts.)

### Step 2: Deep Investigation

Scale your research to the comment's complexity. This is NOT "always 3 searches."

**For domain claims** (owner says "scholars do X"):
- Search for evidence and counterexamples across schools/periods
- Search for how digital projects handle it (OpenITI, KITAB, Shamela, HathiTrust Arabic)
- If you can't verify, ASK THE OWNER for a specific example

**For technical implications:**
- Search for specific tools. Verify they work for Arabic. Find accuracy benchmarks, not just feature claims.
- Check failure modes and limitations.

**For design challenges:**
- Search for at least 2 alternative approaches in other systems
- Assess trade-offs explicitly

**For scope questions:**
- List the full class of similar cases
- Check if the SPEC handles ANY of them

### Step 3: Form Your Position

Based on evidence, decide:
- **Agree:** domain claim is right, implied change is correct
- **Agree with observation, disagree with direction:** there's a better solution
- **Partially agree:** specific case is real, scope is different
- **Disagree:** comment is based on unusual case or misunderstanding
- **Escalate:** need more domain context to decide

### Step 4: Present Findings

```
## Comment #N: [Title]

**What you said:** [Restate]
**What I found:** [Research with sources]
**My position:** [Agree/disagree/partial, with reasoning]

**Proposed SPEC change (if any):**
[Exact replacement text for the SPEC — or explanation of why no change is needed]

**What this opens up:** [Creative opportunity, if any]
**Downstream impact:** [Does this change affect the next engine's expectations?]
**Open questions:** [What you need from the owner]
```

### Step 5: Track Resolution

```
| # | Section | Status | Position | Key Change |
|---|---------|--------|----------|------------|
| 1 | §4.A.2  | Resolved | Agreed | Added layer detection |
| 2 | §2      | Open | Partial | Need example from owner |
| 3 | §7      | Resolved | Disagreed | No change (current design correct) |
```

---

## Session Management

Claude Chat has a 200K token context window. Long comment sessions degrade quality. When context gets heavy:

1. Produce a **handoff summary**: what's resolved, pending, key decisions
2. Commit it to the repo at `skills/handoffs/{engine}-{date}.md`
3. Push the changes
4. Tell the owner: "We should continue in a fresh chat. I've committed the handoff."
5. The next chat picks it up automatically from the repo after cloning

---

## Handling Batches

Multiple comments at once:
1. Read ALL before responding — they may interact
2. Group by SPEC section
3. Flag conflicts between comments
4. Process groups together, not one-by-one

---

## Anti-Patterns

**The Eager Agree.** You validate the comment because the owner knows the domain. STOP. Research first — the SPEC change may have technical implications he can't see.

**The Surface Fix.** Adding a case to the input contract without updating processing rules, output contract, and error handling. Changes must be end-to-end.

**The Confidence Bluff.** Claiming a library handles something without verifying. If you haven't checked, say so.

**The Formulaic Research.** Running exactly 3 generic searches regardless of comment complexity. Simple comments need 1-2 targeted searches. Complex comments need 8+. Scale to the problem.
