> Purpose: Define the single current frontier and the exact deliverable expected from the next serious work session.
> Authority: The only authoritative next-session task file.
> Update when: The active frontier changes, the deliverable changes, or the success criteria change.
> Must not contain: Session diary, multiple parallel frontiers, broad backlog, durable project law.

## Role Relationship
Owner = CLIENT (non-technical, minimum Islamic knowledge). All agents = ENGINEERING TEAM.
The owner provides reactions and preferences. Agents drive direction, identify gaps, propose next steps.
Never ask the owner engineering questions. Never wait for the owner to identify what's needed next.

# KR Active Frontier

Status: active — DR-1 adjudication RESOLVED 3-0 OPT-B with Gemini DR middle-path amendment; Phase 5a amendment pass executed 2026-04-17; reviewer wave pending

## Current frontier — DR-1 (reading-level) integration, POST-PHASE-5A

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

### Claude DR twin — INTEGRATED 2026-04-17, DIVERGENT on 2 of 8 dimensions

Claude DR has been fully read, inventoried (37 paragraphs across 9 sections), and recorded as an evidence atom at `engines/source/spec/60-evidence/dr-reports/dr-claude-level-detection-20260416.yaml`. Cross-references populated in both DR evidence files. Run-A-only Gemini CLI findings verified by direct inspection.

**Headline:** Claude DR recommends OPT-C-asymmetric (source emits `level_candidate` with confidence=low; taxonomy emits authoritative `level_authoritative`; both persist). This DIRECTLY CONTRADICTS two committed atoms — DEC-SRC-0003 (which rejects OPT-C) and INV-SRC-0011 (which forbids the exact source-level inference OPT-C requires). Reversal, not amendment.

**8-dimension convergence table (documented in both evidence files):**
- CONVERGE (6): level-as-history, matn→sharh→hashiya ladder conditioning, title-tokens-unreliable, non-applicable-genres-null (Claude expands list), multi-layer per-constituent level, correction mechanism (4 triggers, no upstream re-run)
- DIVERGE (2): (a) source engine role — null-unless-override vs low-confidence-candidate-emission, (b) authoritative downstream owner — synthesis vs taxonomy

**Run-A-only Gemini CLI findings — both VERIFIED during plan-phase direct inspection:**
- Taa Marbuta fold at `tests/test_deterministic.py:29` → FALSE POSITIVE. Actual file is at repo-root `tests/test_deterministic.py:33`, tests legacy scholar-name matching function (`normalize_arabic_name`), not source-engine text. Taa Marbuta folding in name-matching is legitimate per AGENTS.md "strip for matching, preserve in display" pattern. No code fix.
- PyMuPDF unshaped Arabic at `engines/source/tests/test_step_60_admission.py:140` → VALID, line number wrong. Actual issue is at `_write_pdf` helper (lines 155-163) invoked at line 767 with Arabic Bismillah. Fix deferred to post-adjudication Track B.

### Adjudication resolved 2026-04-17 — 3-0 OPT-B with middle-path amendment

All three adjudicators returned high-confidence OPT-B verdicts:

| Adjudicator | Dimension | Verdict | Output file |
|---|---|---|---|
| Codex CLI | architectural fit | OPT-B (high) | `.kr/runtime/adjudication_codex_20260417.md` |
| Gemini CLI run 1 | classical scholarly defensibility | OPT-B (high; 6-0 branch win count) | `.kr/runtime/adjudication_gemini_cli_run1_20260417.md` |
| Gemini CLI run 2 | classical scholarly defensibility (independent) | OPT-B (high; 6-0 branch win count) | `.kr/runtime/adjudication_gemini_cli_run2_20260417.md` |
| Gemini DR | T-2 threat model tie-breaker | OPT-B with middle-path enhancement (high) | `.kr/runtime/adjudication_gemini_dr_20260417.md` |

**Gemini DR middle-path decision** (evaluated in-session plan mode 2026-04-17, plan at `C:\Users\Rayane\.claude\plans\agile-tinkering-gizmo.md`): **ADOPT.** Claude DR's null-conflation critique is architecturally valid; the middle-path adds a `level_status` enum field to CON-SRC-0004 that explicitly disambiguates the three operational states (pending_taxonomy / non_applicable_reference / unprocessable_error / assigned) without reversing the OPT-B shallow-signal prohibition. Zero reversal cost, aligns with Critical Rule #4 (errors fail loudly).

### Phase 5a amendment pass — EXECUTED 2026-04-17

Seven atoms amended/created this session:

| Atom | Change |
|---|---|
| `DEC-SRC-0003` | Strengthened OPT-A/OPT-C rejection with Gemini CLI *malakah*-formation reasoning; reframed cascade as `fann → nawʿ/layer → martaba`; cited 3-0 adjudication; closed status in INDEX.yaml (was still `deferred`) |
| `INV-SRC-0011` | ALA-LC transliteration; added AC-4 positive-assertion test (`level_status` populated when level is null); added clarifying clause that `level_status` is NOT governed by this invariant |
| `REQ-SRC-0007` | Added precondition on owner_level_override validation via CON-SRC-0011 whitelist; handoff preservation now covers BOTH level and level_status; added AC-4, AC-5 for non-applicable and cross-field invariant violations |
| `REQ-SRC-0047` | Fatal→blocking severity downgrade; distinguished absent/empty/invalid override cases (AC-4 empty-string, AC-5 absent-field); enriched audit-trail (raw token, verdict, whitelist snapshot) |
| `REQ-SRC-0046` | Nested Optional serialization rule added (recursive D-023); genre_dispute added to preserved set; AC-4 and AC-5 exercise genre_dispute + isnad_chains; AC-6 exercises nested-field omission |
| `CON-SRC-0011` | NEW atom — WorkLevel enum `mubtadiʾ → mutawassiṭ → muntahī` (per Gemini R2; mutaqaddim rejected as historiographic, not pedagogical); 6 acceptance criteria |
| `CON-SRC-0004` | Middle-path `level_status` enum added as MANDATORY field; 4 cross-field invariants encoded; source-engine emission restricted to pending_taxonomy / non_applicable_reference / assigned (unprocessable_error reserved for downstream); AC-3 through AC-7 |

INDEX.yaml bumped to 2026-04-17, DEC-SRC-0003 status corrected, CON-SRC-0011 registered. `python engines/source/scripts/validate_spec.py` reports **0 validation errors on 109 atoms** (103 confirmed, 1 deferred, 5 superseded).

### Immediate deliverables for the next session (ordered)

1. **Dispatch reviewer wave on amended atoms** per mandatory-coworker-dispatch. Three prompts, each through `/prompt-architect` first:
   - `spec-contract-architect` (Codex CLI) — structural consistency of the 7-atom amendment set, cross-field invariants in CON-SRC-0004, CON-SRC-0011 dependency graph
   - `spec-domain-validator` (Gemini CLI, 2 runs merged) — Arabic scholarly accuracy of `mubtadiʾ / mutawassiṭ / muntahī` glosses, *malakah*-formation rationale, ALA-LC transliteration correctness
   - `spec-team-adversary` (CC subagent) — gaps, contradictions, edge cases introduced by level_status + WorkLevel enum
2. **Execute Track B code fixes** while reviewer wave runs in parallel:
   - Metadata plumbing composite-metadata-loss fix (CRITICAL from Gemini CLI source-commit review)
   - PyMuPDF Arabic shaping fix in `tests/test_step_60_admission.py:155-163` (`_write_pdf` helper — add `arabic_reshaper.reshape(...)` + `bidi.algorithm.get_display(...)`)
   - Deterministic fallback documentation and review per Gemini CLI finding
   - Hadith taxonomy completeness fix per Gemini CLI R2 finding
3. **Execute Track C doc fix** — `engines/source/CLAUDE.md` stale "no production code exists yet" line.
4. **Orthogonal amendments** deferred earlier: colophon-defense INV (CRITICAL from Gemini CLI source-commit review), REQ-SRC-0048 deferred-validation surface (R3 adversary BLOCKER), REQ-SRC-0030 genre expansion, INV-SRC-0012 refinement.
5. **Then** close OQ-SRC-0005 via DR-2 on agent monitoring scope.
6. **Then** move to Phase 5 (agent layer) tracer bullet.

### Active DR dispatches

- **DR-1 (level detection)** — adjudication complete 3-0 OPT-B + middle-path; Phase 5a executed. Phase 5a reviewer wave is the next active dispatch.
- **DR-2 (agent monitoring scope)** — still deferred until reviewer wave closes + orthogonal amendments clear.

### Paused work
- Excerpting: frozen at 1008 pass / 0 fail / 4 xfail, budget EUR 36.70 / 100.00. Checkpoint: `reference/handoffs/excerpting_pause_checkpoint_2026-04-08.md`. Do NOT resume until source engine reaches Phase 5 agent-layer readiness.
- Owner-facing visual representations (mermaid diagrams, architecture maps): next-next focus after source engine solidifies.

### Allowed now
- Reviewer-wave dispatches via `/prompt-architect` (required per Rule 14)
- Track B code fixes (PyMuPDF shaping, composite metadata plumbing, deterministic fallback documentation, hadith taxonomy)
- Track C doc fix (stale CLAUDE.md line)
- Orthogonal atom amendments (colophon-defense INV, REQ-SRC-0048, REQ-SRC-0030, INV-SRC-0012)

### Disallowed
- Reversing DEC-SRC-0003 (unanimous 3-0 OPT-B is binding)
- Excerpting code changes (source engine build has priority)
- Starting owner-facing visual representations (next-next focus)
- Skipping `/prompt-architect` on any dispatch (Rule 14)

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

## Session commits (2026-04-17) — pending
- (queued) docs(source): record Claude DR twin on level detection + cross-reference ChatGPT DR + Run-A verification outcomes (DIVERGENT — adjudication dispatched)
- (queued) docs(source): Phase 5a amendments — 3-0 OPT-B adjudication + Gemini DR middle-path level_status enum + CON-SRC-0011 WorkLevel + malakah-formation rationale

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
