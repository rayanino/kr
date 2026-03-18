---
name: kr-session-retrospective
description: Mandatory end-of-session quality audit. Activate at the end of every substantial KR session — before requesting a new chat or signing off. Catches process failures, identifies resource gaps, and ensures lessons are encoded into memory and skills. If you are about to end a KR session without running this, you are skipping a quality gate.
---

# KR Session Retrospective — مراجعة الجلسة

Every substantial KR session ends with a structured retrospective. This is not optional reflection — it is a quality gate that catches process failures before they repeat. The architect twice delivered unreviewed output in the same session (the normalization build prep). Both times, the owner had to ask for a review. Both times, the review found real errors. This skill ensures that pattern cannot recur.

## When this skill activates

At the END of every KR session where the architect produced substantial work (a NEXT.md, a review verdict, a SPEC classification, a design decision, a research conclusion). The trigger is: the architect is about to request a new chat, or the owner signals the session is ending, or the architect has completed all tasks in NEXT.md.

Do NOT skip this because the session "went well." The normalization build prep session produced correct final output — after two forced review rounds. "Correct after being told to check" is not the same as "correct process."

## Protocol

### 1. Errors caught late

List every error that was caught in review (yours or the owner's) that should have been caught during production.

Template:
```
## Errors caught late

| Error | When caught | When it should have been caught | Root cause |
|-------|------------|--------------------------------|------------|
| [description] | [review round N / owner feedback] | [during production / first review] | [skipped quality pipeline / didn't read downstream / guessed instead of verified] |
```

If the table is empty, either the session was trivial or you're not looking hard enough. For sessions with >200 lines of output, zero late-caught errors is implausible.

### 2. Quality pipeline compliance

For each substantial output produced in this session, check: did you follow the quality pipeline (RESEARCH → THINK → PRODUCE → VERIFY → REVISE)?

Template:
```
## Quality pipeline audit

| Output | Research done? | Multi-angle thinking? | Verified before delivery? | Revised before delivery? |
|--------|---------------|----------------------|--------------------------|------------------------|
| [output name] | [yes: N searches / no] | [yes: N perspectives / no] | [yes: tool-grounded / no: introspection only / no: skipped] | [yes / no: delivered first draft] |
```

Any "no" in the Verified or Revised columns is a process failure. Note it and state what you'll do differently.

### 3. Resources I should have asked for

List anything that would have improved the session's output quality — test data, real samples, CC relay, a new chat, tool access — that you didn't ask for.

```
## Resources not requested

| Resource | Why it would have helped | Why I didn't ask |
|----------|------------------------|-----------------|
| [resource] | [specific improvement] | [honest reason — forgot? didn't think of it? tried to work around it?] |
```

### 4. Skills invoked vs. should have invoked

```
## Skill audit

| Skill | Invoked? | Should have been invoked? | Impact of gap |
|-------|----------|--------------------------|---------------|
| critical-review | [yes/no] | [yes — before every delivery] | [errors reached owner] |
| kr-research | [yes/no] | [yes/no — with reason] | [shallow tech survey] |
| ... | | | |
```

### 5. Context health assessment

Answer honestly:
- Can I still recall the specifics of every file I read this session without re-reading?
- Have I produced >3 substantial outputs in this session?
- Is my next task complex enough that degraded context could cause errors?

If any answer suggests degradation: **request a new chat NOW.** Do not push through. State what the new session needs to know.

### 6. Memory and skill updates needed

Based on findings from steps 1-5, list concrete updates:

```
## Required updates

Memory entries to add/modify: [list]
Skills to update: [list with specific changes]
Repo artifacts to commit: [list]
```

Then EXECUTE the updates. Do not just list them. If a memory entry needs adding, add it. If a skill needs updating, produce the updated file. If a repo artifact needs committing, commit it.

## Calibration

This retrospective should take 5-10 minutes of honest assessment, not 30 minutes of performative self-reflection. The goal is catching concrete process failures and closing them — not producing a beautiful document about lessons learned.

If you find yourself writing "I should be more careful" or "I will pay more attention" — stop. Those are not fixes. A fix is: "Add X to memory," "Update skill Y to include check Z," "Request resource W at session start."
