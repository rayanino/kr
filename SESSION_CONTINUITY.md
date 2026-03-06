# Session Continuity Protocol — بروتوكول استمرارية الجلسات

This protocol ensures no work is lost, no context is forgotten, and no session starts confused. The core insight: "generic handoffs are worse than no handoffs" (Blake Link). Every handoff must be specific, quantifiable, and immediately actionable.

---

## The Problem

Claude Code sessions are stateless. Each new session starts with zero memory of the previous one. The ONLY persistent state is:
1. The git repository (code, docs, SPECs)
2. `NEXT.md` (session handoff file)
3. `STATUS.md` (project-wide state)
4. `reference/SESSION_LOG.md` (history)
5. `reference/kr_decisions.md` (decisions)

Everything else — the reasoning, the context, the "why" behind decisions — is lost unless explicitly written down.

## Session Types

Each session type has different handoff needs:

### Type A: SPEC Refinement Session
**What persists:** The refined SPEC (committed), NEXT.md, decisions.
**What's lost:** The reasoning behind why specific wording was chosen, the search results that influenced a design decision, the alternative designs that were considered.
**Handoff must include:** Which SPEC, which cycle number, what defects were found, what remains unresolved.

### Type B: Implementation Session
**What persists:** Code (committed), tests (committed), NEXT.md.
**What's lost:** Why a particular implementation approach was chosen over alternatives, what the SPEC said that led to this implementation, any SPEC ambiguities discovered.
**Handoff must include:** Which SPEC section was implemented, how many tests pass/fail, what SPEC ambiguities were found, what's blocked.

### Type C: Design Review Session
**What persists:** Improvements committed, NEXT.md.
**What's lost:** The analysis that led to the improvements, alternatives considered.
**Handoff must include:** What was reviewed, what was found, what was changed, what needs further work.

### Type D: Research Session
**What persists:** RESOURCES.md updates, NEXT.md.
**What's lost:** The search queries used, the results evaluated, why certain tools were chosen.
**Handoff must include:** What was researched, what was found, what decisions were made, what needs further investigation.

---

## NEXT.md Structure (Mandatory)

Every NEXT.md must follow this EXACT structure. No section may be omitted.

```markdown
# NEXT SESSION

## Session Type
[SPEC_REFINEMENT | IMPLEMENTATION | DESIGN_REVIEW | RESEARCH | MIXED]

## Immediate Task
[ONE specific task. Not "work on source engine" but "Refine source engine SPEC §4.A.2, refinement cycle 1, Step 3 (Example Audit)."]

## Definition of Done
[Numbered list of TESTABLE criteria. Include counts where possible:
"1. All 15 rules in §4.A.2 have concrete I/O examples"
"2. Tests: 12 pass, 0 fail, 0 skip"
Not: "SPEC is better" or "code works"]

## Context
[WHY this task. What happened before. What decisions affect this task.
Include: session type of the previous session, what it accomplished, what it couldn't finish.]

## Files to Read — IN THIS ORDER
[Exact paths. If partial read suffices, include line ranges.
ALWAYS start with the deliverable being worked on (the SPEC, the code file).
NEVER include files not needed for this specific task.]

## Files to NOT Read
[Explicit list of files that might seem relevant but are NOT needed.
This prevents wasting context on unnecessary reads.]

## Known Issues
[Anything discovered in previous sessions that affects this task:
- SPEC ambiguities found during implementation
- Test failures not yet resolved
- Boundary mismatches discovered
- Owner questions pending]

## Progress Metrics
[Quantifiable progress on the current milestone:
"M1.1: 3/5 tasks complete. M1.2: 0/6 tasks complete."
"Source SPEC: Cycle 1 refinement in progress (Steps 1-4 done, Steps 5-9 remain)."
"Tests: 912 pass, 37 skip, 1 fail (API key)."]

## What Last Session Did
[Factual, quantifiable. Not "worked on the SPEC" but:
"Refined source SPEC §4.A.1-§4.A.4. Found 7 defects: 3 ambiguities, 2 missing examples, 1 outdated tool reference, 1 boundary mismatch. Fixed 6, deferred 1 (requires owner input on hadith collection handling)."]

## Decisions Made
[New decision numbers: "D-043, D-044"
Quick one-line summary of each. Full details in kr_decisions.md.]

## Pending Owner Questions
[Questions waiting for answers. Include: when asked, what it blocks.]
```

---

## Compaction Recovery

When Claude Code's context window fills and compaction occurs, critical information is lost. The `SessionStart(compact)` hook in `.claude/settings.json` injects essential context, but it cannot capture session-specific state.

**Rule:** If you sense you're running low on context (responses getting slower, forgetting earlier decisions):
1. STOP working on the current task.
2. Write NEXT.md with full detail (more detail than usual).
3. Commit and push immediately.
4. Write in NEXT.md: "Previous session ended due to context pressure. May need to re-read [specific files] to recover context."

**Rule:** After compaction, ALWAYS re-read NEXT.md. The compaction summary may have lost task-specific details.

---

## Crash Recovery

If a session ends without writing NEXT.md (crash, timeout, error):

The next session will find NEXT.md from the PREVIOUS good session. It should:
1. Check `git log --oneline -5` for any uncommitted work.
2. Check `git stash list` for stashed changes.
3. Check `reference/SESSION_LOG.md` for the last recorded session.
4. If the git log shows commits since NEXT.md was written but NEXT.md wasn't updated: read the commit messages and diffs to reconstruct context.
5. Write a corrected NEXT.md before proceeding.

---

## Parallel Session Prevention

Two Claude sessions should never run simultaneously on the same branch. But if it happens:

1. The second session will get a merge conflict on `git pull`.
2. If this happens: STOP. Tell the owner. Do NOT force-push.
3. The owner must resolve: close one session, or put one on a branch.

---

## Owner Intervention Handling

If the owner makes changes between sessions (edits files, provides data, answers questions):

1. Check `git log --oneline -5` at session start.
2. If there are commits not from "KR Architect": read the diffs.
3. Check if the changes affect the current task.
4. If they do: incorporate them before proceeding.
5. If they're owner answers to pending questions: update NEXT.md to remove the question from "Pending Owner Questions" and note the answer in "Context."
