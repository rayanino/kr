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

### OPS-DEC-006 — Adopt 4-phase excerpting hardening with mandatory multi-coworker evaluation
Status: active
Date: 2026-04-01

#### Decision
The excerpting engine's final hardening will follow a 4-phase protocol (Owner Q&A, Smoke Run + Analysis, Deep Hardening, Full 5-Book Run) with all 5 coworkers (Codex CLI, Gemini CLI, ChatGPT DR, Claude DR, Gemini DR) dispatched at every milestone. No phase may conclude without independent confirmation from all available coworkers.

#### Why
Two owner comments on campaign excerpts (2,303 excerpts, $96.87) triggered a complete rearchitecture (DR-1/DR-2/DR-3 debate, 6 reviewers, 2 days of analysis). The root cause: single-model evaluation missed quality problems that the owner immediately noticed. The excerpt definition in the SPEC was formally correct but did not capture what the owner WANTS to experience. Multi-coworker evaluation at every milestone prevents this class of failure.

#### Evidence basis
- Owner feedback at `integration_tests/campaign_20260331/taysir/owner_feedback.jsonl` (2 reviews)
- 6-reviewer cross-validation of DR-1/DR-2/DR-3 decisions
- Campaign analysis (19 files at `integration_tests/campaign_20260331/analysis/`)
- Prior single-model evaluations that passed but did not satisfy the owner

#### Consequences
1. Every major milestone requires all 5 coworkers before concluding.
2. No content quality conclusion from a single model's judgment (extends D-041 to workflow level).
3. Phase 0 (Q&A) must complete before any prompt tuning.
4. Budget allocation: ~EUR 50 remaining for ~3 smoke runs + 1 full run.

#### What would reverse this
Evidence that fewer evaluators catch the same issues at lower cost, or that the owner's quality expectations have been fully encoded in automated checks, making multi-coworker review redundant.

#### Related artifacts
- `NEXT.md`
- `.kr/ACTIVE.md`
- `.claude/rules/coworker-dispatch.md`
- `.claude/rules/no-single-model-conclusion.md`

### OPS-DEC-007 — Promote the excerpt-definition canon into the authoritative excerpting doctrine lane
Status: active
Date: 2026-04-03

#### Decision
KR will treat `engines/excerpting/reference/excerpt_definition_canon/` as the current authoritative excerpt-definition doctrine lane. The old ABD-era file `engines/excerpting/reference/ABD_EXCERPT_DEFINITION.md` remains historical reference only and no longer carries a single-source-of-truth claim.

#### Why
The owner-reviewed case cycle and canon backfill produced a materially stronger doctrine surface than the old ABD excerpt definition. The old file contains valuable historical reasoning, but it predates the owner hardening loop and does not encode the accepted/provisional/unresolved status model now needed for safe excerpting work.

#### Evidence basis
- Reviewed-case canon bundle preserved at `engines/excerpting/chatgpt_f1_collection/canon/excerpt_definition/`
- Promoted authoritative copy at `engines/excerpting/reference/excerpt_definition_canon/`
- Five reviewed cases: `ext_39_masala:3`, `ext_39_masala:6`, `ext_46_qa:9`, `ibn_aqil_v1:11`, `ibn_aqil_v3:13`
- Owner-driven pressure documented in the promoted canon dossier and hard judgment

#### Consequences
1. Future excerpt-definition work must start from `reference/excerpt_definition_canon/`, not from the ABD file.
2. The canon is authoritative even where it marks doctrine as provisional or unresolved; those bounds are part of the authority.
3. The `chatgpt_f1_collection` copy is preserved as provenance, not as the live doctrine lane.
4. F1 raw collection/backfill is preserved, but unresolved doctrine remains live work rather than silently treated as closed.

#### What would reverse this
Promotion of a newer excerpt-definition doctrine lane that clearly supersedes this canon with stronger evidence and explicit migration notes, or a deliberate decision to fully integrate the canon into `SPEC.md` with the same status discipline and traceability.

#### Related artifacts
- `engines/excerpting/reference/excerpt_definition_canon/README.md`
- `engines/excerpting/reference/excerpt_definition_canon/01_dossier.md`
- `engines/excerpting/reference/excerpt_definition_canon/11_hard_judgment.md`
- `engines/excerpting/reference/ABD_EXCERPT_DEFINITION.md`
