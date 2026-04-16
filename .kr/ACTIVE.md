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

## Current frontier — Source Engine Build

The source engine build is active. Spec frozen 2026-04-15 (104 atoms, 97 confirmed, 3 deferred). Tracer bullet through pipeline steps 10–60 implemented. 115 tests pass, 0 fail, pyright clean. Build is on `main` branch with shared commit authority (CC + Codex).

Branch: `main`
Canonical engine state: `engines/source/CLAUDE.md`
Pipeline steps implemented: upload_receipt → freeze_and_manifest → container_classification → intake_analysis → metadata_deliberation → source_admission_and_normalization_handoff

### Immediate deliverable
Close the 3 deferred SPEC atoms blocking source engine completion:
- `DEC-SRC-0003` — level detection strategy (DR-1 in flight 2026-04-16)
- `OQ-SRC-0001` — level detection ownership (collapses with DEC-SRC-0003)
- `OQ-SRC-0005` — agent monitoring scope (DR-2 queued after DR-1 returns)

### Active DR dispatches
- **DR-1 (level detection)** — dispatched 2026-04-16 to ChatGPT DR + Claude DR. Both models have private repo access; they read `engines/source/spec/50-questions/OQ-SRC-0001.yaml`, `engines/source/spec/30-architecture/decisions/DEC-SRC-0003.yaml`, `engines/source/spec/60-evidence/owner-feedback/OF-SRC-0007.yaml`. Owner is relaying results.
- **DR-2 (agent monitoring scope)** — deferred until DR-1 returns. Monitor placement may depend on whether level inference is single-engine (source-only or downstream-only) or cross-engine (dual inference + reconciliation).

### Paused work
- Excerpting: frozen at 1008 pass / 0 fail / 4 xfail, budget EUR 36.70 / 100.00. Checkpoint: `reference/handoffs/excerpting_pause_checkpoint_2026-04-08.md`. Do NOT resume until source engine reaches Phase 5 agent-layer readiness.
- Owner-facing visual representations (mermaid diagrams, architecture maps): next-next focus after source engine solidifies.

### Allowed while source engine is active
- source engine spec/code/test work
- DR drafting via `/prompt-architect` for deferred atoms
- coworker dispatch (Codex CLI, Gemini CLI) on source engine questions
- repo hygiene: removing Rule-17 pollution, pruning MCP inventory, updating stale docs

### Disallowed while source engine is active
- excerpting code changes
- starting owner-facing visual representations work
- building other engines (normalization, passaging, etc.) beyond minimal contracts

## Success criteria
1. All 3 deferred SPEC atoms closed with DR-backed decisions.
2. Phase 5 (agent layer) planned and tracer-bullet-implemented.
3. Source engine ready for real-data production runs with full multi-model consensus.
4. All 115+ tests pass, pyright clean, tree clean, remote current.

## Budget
- Source engine build budget: TBD (first real-data runs not yet scheduled).
- Excerpting budget frozen at EUR 36.70 / 100.00.

## Relevant decisions
- OPS-DEC-001 through OPS-DEC-006 (still in force)
- D-023 metadata preservation — non-negotiable across all engines
- D-041 multi-model consensus — required for all content classification decisions

## Previous frontier (closed 2026-04-16)
Repo cleanup + owner-facing visual representations. Repo cleanup is largely complete (see Session 23). Visual representations deferred to post-source-engine phase.
