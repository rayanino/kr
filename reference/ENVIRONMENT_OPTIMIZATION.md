# Environment Optimization — Changes for Owner to Make

This file contains exact text for the owner to paste into project settings.
These changes address the root cause of Session 3 failures: rules in repo files
are aspirational; rules in the system prompt (project instructions) are behavioral.

---

## 1. Add to `<instructions>` — WORKFLOW SEQUENCING section

Replace the current WORKFLOW SEQUENCING block with this:

```
WORKFLOW SEQUENCING (when CC completes work):

Step 1: Copy checklist.
  cp reference/protocols/REVIEW_CHECKLIST_TEMPLATE.md reference/archive/sessions/reviews/review_session_N.md
  Open the copy. Fill each section as you complete it. This is your working document.

Step 2: ROUND 1 — Pass 1 (Structural). Do NOT skip ahead to probing or verdict.
  - Pull repo, read diff, inventory deliverables
  - Read EVERY file CC modified (FULL content — if view truncates, request the rest)
  - After reading each file, state function/pattern count. Verify by grep.
  - Run ALL tests
  - CROSS-ENGINE: grep every modified contract type across ALL engines. Run tools/check_cross_engine_contracts.py
  - Deliver Pass 1 findings. End the response. (Context switch forces fresh eyes.)

Step 3: ROUND 2 — Pass 2 (Adversarial). After owner says "continue."
  - 3+ probing scripts with constructed inputs
  - 2+ fixture semantic spot-checks with printed Arabic text
  - SPEC CONCRETE EXAMPLE TRACE: for every SPEC section with a worked example, trace it through the implementation. Print actual output. Compare field-by-field.
  - Cross-engine data flow test
  - Deliver Pass 2 findings. End the response. Verdict is NEVER here.

Step 4: ROUND 3 — Pass 3 (Self-Verification + Verdict). After owner says "continue."
  - Verify every factual claim from Passes 1-2 (grep counts, existence checks, re-read functions)
  - Check for rationalization patterns in your own conclusions
  - Draft Notes — each verified against code before writing
  - Fill the checklist. Commit. Push.
  - Deliver verdict ONLY now.

CRITICAL: The architect drives the quality — the owner just says "continue."
Each round uses a structurally different verification method. The context break
between rounds forces the architect to re-enter fresh. The verdict is NEVER
in the same response as Pass 2 probes.
The kr-reviewing-cc-output skill offers "ACCEPT WITH FIXES" — that verdict DOES NOT EXIST.
The only verdicts are ACCEPT (zero unfixed findings, repo clean) and BLOCKED.
reference/protocols/REVIEW_PROTOCOL.md overrides the skill.
```

## 2. Update skill: kr-reviewing-cc-output

Replace the ENTIRE skill content with the file at:
`reference/skill_updates/kr-reviewing-cc-output_SKILL_v3.md`

This is v3 of the skill. Changes from v2: enforces 3-pass multi-round structure,
mandatory SPEC example trace, self-verification pass, no truncated file reads.

## 3. Why these changes matter

The Session 3 failure trace:
1. Owner says "it's done"
2. Architect pulls, reads code, runs tests → delivers ACCEPT
3. Owner pushes back → architect probes deeper → delivers ACCEPT again
4. Owner pushes back → architect finds L-003, still misses SPEC fix + contract break
5. Owner pushes back → architect fixes SPEC + passaging contract
6. Owner pushes back → architect adds rules
7. Owner: "are the rules even read?"

The Session 4 failure trace:
1. Owner says "review Session 4"
2. Architect runs 16 probes in one response → "ACCEPT, zero findings"
3. Owner says "do a critical review" → architect finds 3 real gaps (factual error, missed SPEC trace, undocumented L-007)
4. Owner: "your review quality is pretty bad, fix the environment"

**Pattern:** The architect produces thorough-LOOKING work that doesn't withstand scrutiny. Multi-round structure (Rule 8) forces the architect to use structurally different verification in each round. The context break between rounds prevents momentum from overriding rigor. The owner says "continue" — the quality comes from the architect's mandatory self-verification in Round 3, not from owner intervention. The architect is the quality gate, not the owner.

Root cause: the architect's first action after "it's done" was reading code.
It should have been: copy the checklist template.

The checklist changes the workflow from "read code → form impression → verdict"
to "open checklist → execute steps → fill evidence → fix findings → then verdict."

The system prompt change makes this the DEFINED workflow, not a document
the architect may or may not read from the repo.

## 4. QUALITY_AXIOM.md — new governing document

A new protocol document `reference/protocols/QUALITY_AXIOM.md` establishes the foundational principle:
the architect is the sole quality gate, the owner is not a safety net. It defines what mechanisms
actually work (tool-based verification, context breaks, checklists, failure documentation) and what
doesn't (aspirational "be careful," introspective self-review, owner-dependent checks).

The QUALITY_AXIOM is referenced by: REVIEW_PROTOCOL.md, kr-reviewing-cc-output skill v3,
kr-preparing-cc-handoffs skill v2, kr-gating-transitions skill v2.

**Add to `<quality_standards>` in project instructions:**
```
When reviewing any output, first read reference/protocols/QUALITY_AXIOM.md — the architect is
the sole quality gate. The owner says "continue" and does not check output. Every error the
architect makes reaches the pipeline. Quality enforcement must be tool-based and structural,
never aspirational or owner-dependent.
```
