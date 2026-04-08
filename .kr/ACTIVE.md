> Purpose: Define the single current frontier and the exact deliverable expected from the next serious work session.
> Authority: The only authoritative next-session task file.
> Update when: The active frontier changes, the deliverable changes, or the success criteria change.
> Must not contain: Session diary, multiple parallel frontiers, broad backlog, durable project law.

## Role Relationship
Owner = CLIENT (non-technical, minimum Islamic knowledge). All agents = ENGINEERING TEAM.
The owner provides reactions and preferences. Agents drive direction, identify gaps, propose next steps.
Never ask the owner engineering questions. Never wait for the owner to identify what's needed next.

# KR Active Frontier

Status: active

## Current frontier — Repo Cleanup + Owner-Facing Visual Representations

Pause excerpting engine builds at the Session 22 checkpoint. The active workstream is now repo cleanup, structure clarification, and owner-readable visual representations that help the owner react to the system without needing to inspect engine code directly.

### Immediate deliverable
Create a cleaner repo surface plus visual maps/diagrams that let the owner review:
- the 7-engine pipeline and handoff boundaries
- the excerpting phase flow and artifact outputs
- runtime, authority, and frontier control surfaces
- where owner insight is useful versus where engineering autonomy applies

### Excerpting freeze checkpoint
- Branch frozen for engine work: `excerpting-foundations-hardening-20260404`
- Tests at freeze: `1008` pass, `0` fail, `4` xfail
- Budget at freeze: `EUR 36.70 / 100.00`
- Review artifact: `integration_tests/review_session22/eval_session22_talaq/`
- Live feedback file: `integration_tests/review_session22/eval_session22_talaq/owner_feedback.jsonl`
- First analyzed owner verdict: Session 22 excerpt 1 is a Phase 2 granularity miss; the current pipeline split `لغة` vs `شرعا`, but still fused lexical definition with `اشتقاق`
- Deferred generalization candidates:
  - `div_src_test0001_7_006`
  - `div_src_test0001_4_000`
  - `div_src_test0001_6_076`

### Allowed while paused
- repo cleanup and archival reshaping
- owner-facing walkthrough docs
- mermaid diagrams and visual maps
- naming and navigation cleanup
- collecting owner review feedback into queued evidence

### Disallowed while paused
- excerpting code changes
- prompt or contract changes for excerpting
- new smoke runs, campaign reruns, or generalization runs
- coworker dispatch tied to excerpting fixes

### Resume trigger
Resume excerpting only after the cleanup/visual sessions are complete and the owner feedback collected during the pause has been consolidated into a single implementation brief.

## Success criteria
1. The repo surface is simpler to navigate for non-technical owner review.
2. Visual representations exist for the major architectural and workflow surfaces.
3. The owner can react to structure, flow, and information design without code-level interpretation.
4. The excerpting Session 22 checkpoint remains explicit and reproducible.

## Budget
- Excerpting budget remains frozen at the Session 22 checkpoint unless the frontier is explicitly switched back.

## Relevant decisions
- OPS-DEC-001 through OPS-DEC-006

## Previous frontier (paused 2026-04-08)
Excerpting Engine Deep Q&A + Exhaustive Hardening. See `reference/handoffs/excerpting_pause_checkpoint_2026-04-08.md` for the exact frozen state and resume protocol.
