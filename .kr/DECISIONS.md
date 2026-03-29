> Purpose: Preserve durable decisions, their rationale, and their reversal conditions.
> Authority: Audit trail of project commitments. This file records decisions but does not replace updating CHARTER.md or ACTIVE.md.
> Update when: A real decision is made, reversed, or superseded.
> Must not contain: Open brainstorming, unresolved questions, session narrative, vague preferences without commitment.

# KR Decisions Log

## ID scheme and rules
Use IDs of the form `OPS-DEC-001`, `OPS-DEC-002`, and so on. Do not rewrite old decisions except for status updates, typo fixes, or cross-reference additions. If a decision changes durable law, update `CHARTER.md` in the same session. If it changes the current frontier, update `ACTIVE.md` in the same session.

## Decision entries

### OPS-DEC-001 — Adopt `.kr/` as KR's canonical control plane
Status: active
Date: 2026-03-29

#### Decision
KR will use a repo-local, quarantined control plane under `.kr/` as the canonical project-control layer.

#### Why
The project needs a control system that is versioned with the repo, visible to all workers, inspectable, and not dependent on one chat surface or one person's memory.

#### Evidence basis
Control-plane design review across location, authority, and failure-mode questions during the 2026-03-29 session.

#### Consequences
Project-control truth should live in `.kr/` rather than in ad hoc chats, external notes, or repo-root transient directives.

#### What would reverse this
A clearly better repo-native control mechanism that preserves the same visibility, auditability, and worker interoperability with lower maintenance cost.

#### Related artifacts
- `.kr/README.md`
- `.kr/CHARTER.md`

### OPS-DEC-002 — Use an orchestrated primary/specialist session model
Status: active
Date: 2026-03-29

#### Decision
KR sessions will use one primary reasoning session as control tower, with deep research and repo-execution workers used as bounded specialists rather than co-governors.

#### Why
Strategy, synthesis, and durable project law should not be silently redefined by research or implementation sessions. Specialist outputs are highest-value when bounded and then integrated by a primary session.

#### Evidence basis
Session-architecture review covering freeform, symmetric, and orchestrated multi-session models.

#### Consequences
Deep research gathers external evidence. Codex and Claude Code perform bounded repo work. Authoritative control-plane updates belong to the primary session.

#### What would reverse this
Evidence that a different session-governance model yields lower confusion, lower maintenance cost, and better strategic coherence across repeated work.

#### Related artifacts
- `.kr/CHARTER.md`
- `.kr/HANDOFF.md`

### OPS-DEC-003 — Enforce single-frontier and anti-shadow-surface laws
Status: active
Date: 2026-03-29

#### Decision
`ACTIVE.md` is the only authoritative next-session task file, and no file outside `.kr/` should function as a live control directive once the control plane is in use.

#### Why
The biggest control-plane risks are authority leakage, duplicated truths, stale active directives, and shadow governance.

#### Evidence basis
Failure-mode review focused on stale state, shadow command surfaces, and frontier fragmentation.

#### Consequences
`HANDOFF.md` may preserve context but cannot override `ACTIVE.md`. Legacy root-level control notes should be retired or reduced to non-authoritative residue.

#### What would reverse this
A demonstrated need for an additional live control surface that does not increase ambiguity, stale state risk, or duplicated authority.

#### Related artifacts
- `.kr/README.md`
- `.kr/CHARTER.md`
- `.kr/ACTIVE.md`

### OPS-DEC-004 — Prefer evaluation-layer work over further excerpting tuning before the 5-book campaign
Status: active
Date: 2026-03-29

#### Decision
Until full-book evidence is available, KR should prioritize the evaluation layer around the upcoming 5-book excerpting campaign over further speculative prompt or engine tuning.

#### Why
The repo already emits rich run artifacts, and the next large execution step is a full-book campaign. Sharper measurement is more valuable now than additional local tuning without scale evidence.

#### Evidence basis
Repo inspection plus strategic review of the excerpting engine's current stage and existing integration artifacts.

#### Consequences
Near-term work should focus on analyzer design, review-packet design, and full-book testing protocol rather than new excerpting features or prompt rewrites.

#### What would reverse this
A newly discovered blocking defect that prevents meaningful full-book evaluation, or new evidence showing that a specific engine change has clearly higher leverage than evaluation infrastructure.

#### Related artifacts
- `.kr/ACTIVE.md`
- `.kr/HANDOFF.md`

### OPS-DEC-005 — Adopt an analyzer-first evaluation architecture for excerpting full-book campaigns
Status: active
Date: 2026-03-29

#### Decision
KR will treat the run analyzer as the authoritative first interpretation layer for excerpting evaluation, and will derive human review packets from analyzer output rather than from ad hoc artifact browsing.

#### Why
The current repo already emits rich artifacts, but the recent historical run demonstrates that raw artifacts alone are not a trustworthy evaluation surface. `taysir` shows grouped-unit loss between Phase 2b and final excerpts, while `ibn_aqil_v3` shows a silent zero-output run with a truncated LLM response and no logged errors. A disciplined analyzer-first layer is therefore the shortest path from raw run folders to decision-grade evidence.

#### Evidence basis
Primary-session review of `engines/excerpting/SPEC.md`, the integration runners, and `integration_tests/run_20260328/`, including the observed `taysir` accounting break and `ibn_aqil_v3` silent-zero/truncation failure.

#### Consequences
Evaluation work should first build lineage/accounting, metrics, anomaly flags, and campaign summaries, then build review-packet export on top of that layer. Manual browsing is still allowed for debugging, but it is not the primary evaluation method and must not become a shadow evaluation surface.

#### What would reverse this
Evidence that analyzer-first evaluation adds more maintenance cost than interpretive value, or that a different evaluation architecture catches structural and silent failures more reliably with less operational complexity.

#### Related artifacts
- `reference/EXCERPTING_FULL_BOOK_EVALUATION_BRIEF.md`
- `.kr/ACTIVE.md`
- `.kr/HANDOFF.md`
