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

Step 2: Follow the checklist sequentially. Do NOT skip ahead to the verdict.
  - Pull repo, read diff, inventory deliverables
  - Read EVERY file CC modified (full content, not skim)
  - Run ALL tests
  - CROSS-ENGINE: grep every modified contract type across ALL engines. Run tools/check_cross_engine_contracts.py
  - Pass 2 adversarial: 3+ probing scripts, 2+ fixture semantic spot-checks, cross-engine data flow test
  - Fix ALL findings — commit fixes to repo

Step 3: Fill the verdict line in the checklist ONLY after every checkbox is checked and every finding is fixed.

Step 4: Commit the filled checklist to the repo.

Step 5: Deliver the verdict to the owner.

CRITICAL: The kr-reviewing-cc-output skill offers "ACCEPT WITH FIXES" — that verdict DOES NOT EXIST. The only verdicts are ACCEPT (zero unfixed findings, repo clean) and BLOCKED. reference/protocols/REVIEW_PROTOCOL.md overrides the skill.
```

## 2. Update skill: kr-reviewing-cc-output

Replace the Step 5 verdict template with:

```
### Step 5: Verdict

**The REVIEW_PROTOCOL.md is the authority on verdicts, not this skill.**

Two verdicts only: ACCEPT or BLOCKED.

ACCEPT means: zero unfixed findings in the repo. All fixes committed and pushed.
The review checklist (reference/archive/sessions/reviews/review_session_N.md) is
filled and committed. The repo is clean RIGHT NOW.

BLOCKED means: at least one finding exists that couldn't be fixed. State what
must be fixed. Prepare a fix directive.

BANNED: "ACCEPT WITH FIXES", "non-blocking", "architect action item",
"maintenance item", "future cleanup". These are all the same pattern:
find problem → defer it → move on. Fix before verdict.
```

And replace the "After the review" section with:

```
## After the review

If ACCEPT: commit the filled review checklist, then invoke kr-gating-transitions.
If BLOCKED: tell the owner to send Claude Code the specific fixes, then re-review
  (start a fresh checklist for the re-review).
```

## 3. Why these changes matter

The Session 3 failure trace:
1. Owner says "it's done"
2. Architect pulls, reads code, runs tests → delivers ACCEPT
3. Owner pushes back → architect probes deeper → delivers ACCEPT again
4. Owner pushes back → architect finds L-003, still misses SPEC fix + contract break
5. Owner pushes back → architect fixes SPEC + passaging contract
6. Owner pushes back → architect adds rules
7. Owner: "are the rules even read?"

Root cause: the architect's first action after "it's done" was reading code.
It should have been: copy the checklist template.

The checklist changes the workflow from "read code → form impression → verdict"
to "open checklist → execute steps → fill evidence → fix findings → then verdict."

The system prompt change makes this the DEFINED workflow, not a document
the architect may or may not read from the repo.
