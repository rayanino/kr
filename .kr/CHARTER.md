> Purpose: Define KR’s durable mission, operating principles, worker roles, and quality law.
> Authority: Highest durable control document in .kr.
> Update when: Project constitution, worker model, or durable operating principles change.
> Must not contain: Current frontier, transient blockers, session results, speculative idea queues.

# KR Charter

## Mission
KR (خزانة ريان) exists to build a high-integrity Islamic knowledge library from source texts. Its purpose is not merely to extract text fragments, but to preserve and organize teachable scholarly units with enough attribution, structure, and auditability that the resulting library can be trusted as a serious study system rather than a loose corpus of quotations.

## Current scope of the project
KR is currently in the pipeline-building stage. The working pipeline is source -> normalization -> excerpting -> taxonomy -> synthesis. Source and normalization already exist as substantive layers. Excerpting is the current operational bottleneck and is at the threshold between fixture-scale validation and full-book testing. Taxonomy and synthesis remain downstream responsibilities but are not the active frontier. The immediate strategic need is to turn the upcoming full-book excerpting campaign into decision-grade evidence rather than a pile of outputs.

## Durable strategic principles
1. Bottleneck first. Work should concentrate on the steepest constraint on trustworthy progress, not on whichever local improvement is easiest to imagine.
2. Evidence before architectural churn. Once a subsystem reaches pre-scale testing, prefer evaluation infrastructure and diagnostic clarity over further prompt micro-tuning until larger evidence arrives.
3. Durable and volatile truths must stay separate. Long-lived project law, the current frontier, recent context, and decision history must not be mixed into one note.
4. One live frontier. The project may have many valid future threads, but only one may be authoritative as the current frontier at a time.
5. Auditability matters. Any important strategic or methodological commitment should be recoverable from the repo-local control plane, not trapped in chat memory.
6. Partial progress is acceptable; silent drift is not. If a session cannot complete its main deliverable, it should still leave the project in a cleaner and better-directed state.

## Worker roles
- The owner is the final authority on acceptance, priorities, and irreversible project choices.
- The primary reasoning session is the control tower. It interprets the frontier, synthesizes evidence, decides whether specialists are needed, and authoritatively updates the control plane.
- Deep research is an evidence specialist. It answers bounded external-research questions and returns memos or evidence syntheses. It does not redefine project law or the active frontier on its own.
- Codex is a bounded repo-execution specialist. It is used for sharply specified implementation tasks, file edits, scripts, and refactors when acceptance criteria are already clear. It does not govern strategy.
- Claude Code is a repo worker for larger implementation and review tasks when available. Like Codex, it is subordinate to the primary session’s direction rather than an independent strategic authority.

## Quality bar
Work is good only if it improves the project’s real probability of trustworthy progress. That means reasoning should be decision-grade, repo-native, and explicit about uncertainty. Reports and memos should help the next worker act better, not merely sound intelligent. Implementation work should be acceptance-criteria driven. Research should be bounded and actually feed a live frontier. Any change that increases confusion, duplicates authority, or leaves project state harder to recover than before is low-quality work even if it looks sophisticated.

## Control-plane laws
1. `.kr/` is KR’s canonical project-control namespace.
2. No file outside `.kr/` may function as a live control directive once this control plane is in use.
3. `ACTIVE.md` is the only authoritative next-session task file.
4. `HANDOFF.md` preserves recent execution context but never overrides `ACTIVE.md`.
5. `DECISIONS.md` records durable commitments but does not replace updating `CHARTER.md` or `ACTIVE.md` when those commitments change durable law or the active frontier.
6. Specialist sessions are subordinate to a primary session. They may produce artifacts or draft changes, but they do not authoritatively steer the project.
7. Same-session propagation is mandatory: if durable law, the active frontier, or decision state changes, the corresponding control-plane file must be updated before the session ends.
8. Bounded read burden is part of the design. A serious new session should enter through `README.md`, then read `CHARTER.md`, `ACTIVE.md`, `HANDOFF.md`, and only referenced decisions.

## Change policy
Change this file rarely. Update it only when KR’s durable operating law actually changes: mission, worker model, quality bar, or control-plane law. Do not edit it to reflect ordinary session outcomes, temporary blockers, or the latest tactical idea. When in doubt, prefer updating `ACTIVE.md`, `HANDOFF.md`, or `DECISIONS.md` instead.
