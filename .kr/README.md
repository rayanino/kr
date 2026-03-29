> Purpose: Explain what .kr is, how to enter the control plane, and how to use it correctly.
> Authority: Navigation and operating protocol only. This file does not set strategy.
> Update when: The control-plane structure or usage protocol changes.
> Must not contain: Current frontier, session summaries, decision content, repo strategy.

# KR Control Plane

## What this directory is
This directory is KR's canonical project-control layer. It is separate from engine specs, product docs, reports, and transient chat context. Its job is to let any serious new session enter the project correctly and continue work without guessing.

## Canonical read order
1. `README.md`
2. `CHARTER.md`
3. `ACTIVE.md`
4. `HANDOFF.md`
5. Only the explicitly referenced decision entries in `DECISIONS.md`, if needed

## File map
- `CHARTER.md` — durable project law, worker roles, and operating principles
- `ACTIVE.md` — the single current frontier and exact next-session deliverable
- `DECISIONS.md` — append-only durable decision ledger
- `HANDOFF.md` — recent execution context only

## Session start protocol
Read in canonical order. Treat `ACTIVE.md` as the only authoritative next-session task file. Use `HANDOFF.md` only as recent execution context. Use `DECISIONS.md` selectively by referenced ID, not as a default full read.

## Session end protocol
Update `HANDOFF.md` whenever a session materially advances work. Update `ACTIVE.md` when the frontier, deliverable, or completion criteria change. Append to `DECISIONS.md` when a real durable decision is made. Update `CHARTER.md` only when durable project law changes.

## Conflict rules
`CHARTER.md` governs durable rules. `ACTIVE.md` governs the current frontier. `HANDOFF.md` never overrides `ACTIVE.md`. `DECISIONS.md` records commitments but does not replace updating `CHARTER.md` or `ACTIVE.md`. Until root `NEXT.md` is retired, treat it as legacy residue rather than canonical project control.

## Non-goals
This directory is not a diary, a backlog dump, a product manual, or an engine specification.
