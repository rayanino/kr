> Purpose: Define the single current frontier and the exact deliverable expected from the next serious work session.
> Authority: The only authoritative next-session task file.
> Update when: The active frontier changes, the deliverable changes, or the success criteria change.
> Must not contain: Session diary, multiple parallel frontiers, broad backlog, durable project law.

## Role Relationship
Owner = CLIENT (non-technical, minimum Islamic knowledge). All agents = ENGINEERING TEAM.
The owner provides reactions and preferences. Agents drive direction, identify gaps, propose next steps.
Never ask the owner engineering questions. Never wait for the owner to identify what's needed next.

# KR Active Frontier

Status: active — DR-1 integration mid-flight; Claude DR deep analysis + amendment pass queued for next session

## Current frontier — DR-1 (reading-level) integration, amendment phase

The source engine build is active. Spec frozen 2026-04-15 (108 atoms after commit f26997c4c; 102 confirmed, 1 deferred, 5 superseded). Tracer bullet through pipeline steps 10–60 implemented. Substantial Codex-authored code in engines/source/src/ and engines/source/contracts.py (so the engines/source/CLAUDE.md line "no production code exists yet" is stale and should be fixed during amendment).

Branch: `main`
Canonical engine state: `engines/source/CLAUDE.md`

### What happened in session 2026-04-16 (before this handoff)

- ChatGPT DR on reading-level inference integrated into 7 atoms (commit `f26997c4c`): DEC-SRC-0003 closed OPT-B; OQ-SRC-0001 superseded; REQ-SRC-0007 amended; new INV-SRC-0011, INV-SRC-0012, REQ-SRC-0046, REQ-SRC-0047.
- DR evidence file committed at `engines/source/spec/60-evidence/dr-reports/dr-chatgpt-level-detection-20260416.yaml` — contains 46-paragraph inventory, source-engine + cross-engine commitments, post-verification corrections from researcher, and the full 4-reviewer findings.
- HR-23 tracker bug fixed (commit `f0e995e5b`): the prompt-architect tracker was ignoring plugin-namespaced skill form. All subsequent Agent dispatches now work.
- 6 verifications ran during the session:
  - Explore agent: CLEAN — no level-inference in source engine code.
  - researcher agent: OPT-B scholarly claims verified (6V / 3PV / 1UV / 0D), 4 post-verification corrections recorded.
  - R1 spec-contract-architect (via Codex CLI): NEEDS_AMENDMENT — genre-enum gap, WorkLevel not pinned to an atom, error-code overlap, 10 of 17 ACs fail today.
  - R2 spec-domain-validator (via Gemini CLI): NEEDS_AMENDMENT — WorkLevel terminology wrong (mutaqaddim ≠ advanced; specialist has no classical anchor); non-applicable genre list under-inclusive; hadith_collection conflates pedagogical vs reference.
  - R3 spec-team-adversary (pre-mortem): **NEEDS_REWORK** — 2 BLOCKERS (genre enum mismatch makes 3/4 non-applicable values unreachable; deferred-validation surface undefined), plus 5 HIGH findings.
  - Gemini CLI source-commit review: TWO runs (automated bash + owner manual). Merged findings: 3 CRITICAL (composite metadata loss at handoff; deterministic fallbacks silently overwriting; **colophon-role verification gap — no architectural defense against copyist/author conflation, the #1-rank integrity failure per CLAUDE.md**), 2 HIGH (incomplete hadith taxonomy; undocumented .replace chain), 2 MEDIUM (synthetic placeholder Arabic; lowered_title Latin-script hallucination). Run A also flagged Taa Marbuta fold in tests/test_deterministic.py:29 and unshaped PDF Arabic — both VERIFY-before-acting because Run B didn't surface them. Full merged findings in the DR evidence file's `gemini_cli_source_code_review` section.

### Claude DR twin — ARRIVED, NOT YET INTEGRATED

Claude DR on the same level-detection question is in. Owner flagged it as "extremely thorough" and flagged that the previous session's context was too full to absorb it. This is the primary task for the next session.

Location: `C:\Users\Rayane\Downloads\compass_artifact_wf-93f303b5-e843-4c0b-99cb-7f4024d62b06_text_markdown (1).md`. The previous ChatGPT DR was at `Downloads/deep-research-report (33).md` (already integrated in commit f26997c4c). This Claude DR file is the twin to cross-check convergence against.

Integration pattern to follow (mirror what was done for ChatGPT DR):
1. Read the full Claude DR
2. Paragraph-by-paragraph inventory
3. Convergence check against the ChatGPT DR's 46 paragraphs (documented in `dr-chatgpt-level-detection-20260416.yaml` sections s1–s4d)
4. Append a new evidence atom at `engines/source/spec/60-evidence/dr-reports/dr-claude-level-detection-20260416.yaml`
5. Document convergence vs divergence in both files' cross-references

### Immediate deliverables for the next session (ordered)

1. **Read Claude DR completely and produce 46-equivalent paragraph inventory.**
2. **Convergence check vs ChatGPT DR.** If Claude DR also recommends OPT-B and agrees on science+layer conditioning, proceed. If it recommends OPT-A or OPT-C, halt and dispatch adjudication (Codex + Gemini + possibly a third DR).
3. **Execute the amendment pass (Track A + Track B + Track C + Track D).** The synthesized plan is in the DR evidence file under `amendment_plan_synthesized`. Key items:
   - **Track A (atom amendments):** 3 new atoms (REQ-SRC-0048 deferred-validation, CON-SRC-0011 WorkLevel enum, plus an INV-SRC-NEW for colophon-role verification) + 7 existing atom amendments covering all R1/R2/R3 findings
   - **Track B (code fixes):** contracts.py ErrorCode changes, plumb composite_work_type/sub_work_inventory/contains_isnad_chains through admission, replace silent defaults with fail-loud, expand _infer_hadith_subgenre with missing classical subgenres, remove the `lowered_title = title` Latin-script hallucination, document .replace chains, replace synthetic placeholder Arabic in tests, VERIFY-then-fix Taa Marbuta test + PyMuPDF Arabic (Run A-only findings)
   - **Track C (doc):** fix stale `engines/source/CLAUDE.md` "no production code exists yet" line
   - **Track D (architectural investigation):** colophon-role verification gap (is there currently NO architectural defense against كتبه/ألفه conflation?) + MetadataDeliberationInput production-pipeline-wiring gap (Explore agent followup)
4. **Re-dispatch reviewer wave on amended atoms** before declaring amendment pass complete.
5. **Then** (only then) close OQ-SRC-0005 via DR-2 on agent monitoring scope.

### Active DR dispatches

- **DR-1 (level detection)** — ChatGPT DR integrated (commit f26997c4c, findings flagged NEEDS_REWORK by reviewer wave, amendment pass queued). Claude DR arrived 2026-04-16; integration queued for next session.
- **DR-2 (agent monitoring scope)** — still deferred until DR-1 amendment pass complete. Monitor placement answer may depend on OPT-B specifics.

### Paused work
- Excerpting: frozen at 1008 pass / 0 fail / 4 xfail, budget EUR 36.70 / 100.00. Checkpoint: `reference/handoffs/excerpting_pause_checkpoint_2026-04-08.md`. Do NOT resume until source engine reaches Phase 5 agent-layer readiness.
- Owner-facing visual representations (mermaid diagrams, architecture maps): next-next focus after source engine solidifies.

### Allowed while source engine is active
- Reading Claude DR and producing paragraph inventory
- Running the amendment pass (Track A + B + C)
- Coworker dispatch via `/prompt-architect` (tracker now works correctly per commit f0e995e5b)
- Repo hygiene: Rule-17 pollution removal, stale doc fixes

### Disallowed while source engine is active
- Excerpting code changes
- Starting owner-facing visual representations work
- Building other engines (normalization, passaging, etc.) beyond minimal contracts
- Skipping `/prompt-architect` on any dispatch (HR-23 enforces this, tracker bug is fixed)

## Success criteria (updated)
1. All 3 deferred SPEC atoms closed with DR-backed decisions (DEC-SRC-0003 + OQ-SRC-0001 done; OQ-SRC-0005 pending DR-2).
2. **Amendment pass (Track A + B + C) committed**, with all R1/R2/R3/Gemini-CLI findings resolved, and Claude DR convergence documented.
3. Phase 5 (agent layer) planned and tracer-bullet-implemented.
4. Source engine ready for real-data production runs with full multi-model consensus.
5. All tests pass, pyright clean, tree clean, remote current.

## Budget
- Source engine build budget: TBD (first real-data runs not yet scheduled).
- Excerpting budget frozen at EUR 36.70 / 100.00.
- Session 2026-04-16 token usage: substantial (4 agent dispatches + 2 prompt-architect invocations + large DR evidence file); no API cost incurred.

## Session commits (2026-04-16)
- `852fc7376` chore: archive paused excerpting plan out of active plans dir
- `e624aca56` docs(source): record ChatGPT DR on level detection, 46 paragraphs
- `f0e995e5b` fix(hooks): track-prompt-architect accepts plugin-namespaced skill form
- `f26997c4c` feat(source): resolve DEC-SRC-0003 (OPT-B) + 4 new atoms from DR-1

## Relevant decisions
- OPS-DEC-001 through OPS-DEC-006 (still in force)
- D-023 metadata preservation — non-negotiable across all engines
- D-041 multi-model consensus — required for all content classification decisions

## Known follow-up items flagged for later
- **MetadataDeliberationInput is only instantiated in test code, never in production `pipeline.py`** (surfaced by Explore agent). Test coverage of the deliberation step is structural-only, not end-to-end. Investigate production wiring.
- **Gemini CLI 429 rate limits on gemini-3.1-pro-preview** — consider pinning a stable model with `-m` for future batch dispatches.
- **Hook observability gap** — `.kr/runtime/dispatch_log.jsonl` is populated by `enforce-prompt-architect-bash.sh` for shell-CLI dispatches (codex/gemini), NOT for Agent-tool dispatches. The "NO DISPATCH in 199h" session-start counter does not reflect CC subagent dispatches.

## Previous frontier (closed 2026-04-16)
Repo cleanup + owner-facing visual representations. Repo cleanup is largely complete (see Session 23). Visual representations deferred to post-source-engine phase.
