# Owner Action Required — Environment Install

**Time needed:** ~10 minutes. Do all 4 steps. Order doesn't matter.

---

## Step 1: Update project instructions

Open Claude project settings → Instructions.

Find the WORKFLOW SEQUENCING section (starts with "WORKFLOW SEQUENCING (when CC completes work)").

**Delete** the entire section from "WORKFLOW SEQUENCING" through the end of the block.

**Paste** the replacement from `reference/SYSTEM_PROMPT_UPDATE.md` — everything between the `===START===` and `===END===` markers.

This gives the system prompt the quality axiom, skill invocation rule, and all three workflow procedures (review, handoff, transition). Self-contained — works even if skills don't load.

---

## Step 2: Replace 3 skills

In Claude project settings → Skills:

**A.** Find `kr-reviewing-cc-output` → Edit → replace ALL content with:
   `reference/skill_updates/kr-reviewing-cc-output_SKILL_v3.md`

**B.** Find `kr-preparing-cc-handoffs` → Edit → replace ALL content with:
   `reference/skill_updates/kr-preparing-cc-handoffs_SKILL_v2.md`

**C.** Find `kr-gating-transitions` → Edit → replace ALL content with:
   `reference/skill_updates/kr-gating-transitions_SKILL_v2.md`

---

## Step 3: Replace 2 more skills (from prior session, never installed)

**D.** Find `kr-core-extract` → Edit → replace ALL content with:
   `reference/skill_updates/kr-core-extract_SKILL.md`

**E.** Find `kr-spec-review` → Edit → replace ALL content with:
   `reference/skill_updates/kr-spec-review_SKILL.md`

---

## Step 4: Create 1 new skill

**F.** Create new skill → name it `kr-session-retrospective` → paste content from:
   `reference/skill_updates/kr-session-retrospective_SKILL.md`

---

## Verification

After installing, start a new chat and say: "What does your system prompt say about CC reviews?"
The response should mention: 3 rounds, SPEC example trace, grep-verify claims, NEVER verdict in same response as probes.

## After verification

Delete `reference/skill_updates/` directory (files archived in git history).
Delete `reference/ENVIRONMENT_OPTIMIZATION.md` (superseded by this file + SYSTEM_PROMPT_UPDATE.md).
