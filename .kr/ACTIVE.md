> Purpose: Define the single current frontier and the exact deliverable expected from the next serious work session.
> Authority: The only authoritative next-session task file.
> Update when: The active frontier changes, the deliverable changes, or the success criteria change.
> Must not contain: Session diary, multiple parallel frontiers, broad backlog, durable project law.

## Role Relationship
Owner = CLIENT (non-technical, minimum Islamic knowledge). All agents = ENGINEERING TEAM.
The owner provides reactions and preferences. Agents drive direction, identify gaps, propose next steps.
Never ask the owner engineering questions. Never wait for the owner to identify what's needed next.

# KR Active Frontier

Status: active — Phase 5b items 1, 2, 3, 12, 13, 14, 15, 16 closed (commits `62647cb2b`, `ec8d82ca4`, `386685819`, `bf4354399`+`a4f2b2788` retroactive-review amendments, `f965aec7b`, and item-16 commit pending); **8 Phase 5b work items remain (4, 5, 6, 7, 8, 9, 10, 11)** plus 3 new follow-up items from the retroactive review (16 DONE; 17, 18 remain) plus 2 new items surfaced during item-16 dispatch (19, 20)

## ⟶ FRESH-SESSION START HERE (Phase 5b)

A new session starting on this frontier should:
1. Read this file end-to-end (you are here).
2. Read the four reviewer outputs in `.kr/runtime/` (listed below under "Active DR dispatches") — they are the evidence base for every Phase 5b work item.
3. Read `engines/source/CLAUDE.md` (engine-specific state). The line "no production code exists yet" is stale; ignore.
4. Read `engines/source/spec/INDEX.yaml` for atom inventory.
5. Jump to the **"Phase 5b work items (ordered)"** section below and execute in the listed dependency order. Item 1 (contracts.py alignment) unblocks item 2 (AC rewrites). Items 3, 12, 13 are independent and can be done any time. Items 5, 6, 7 are architectural and should land together.
6. End Phase 5b with a second 4-reviewer wave. Gate closure on test-run evidence (pytest output), not just `validate_spec.py` passing. This is the lesson Phase 5a's paper-reconciliation teaches.

Key memories for context: `project_source_engine_phase_5b_pending.md`, `feedback_multi_evaluator_catches_paper_reconciliation.md`, `feedback_gemini_2run_independence_catches_unique.md`.

## Current frontier — DR-1 (reading-level) integration, Phase 5b pending

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
   - Metadata plumbing composite-metadata-loss fix (CRITICAL from Gemini CLI source-commit review) — **PENDING**
   - ~~PyMuPDF Arabic shaping fix in `tests/test_step_60_admission.py:155-163`~~ — **DONE 2026-04-17 (commit 4c2e023c2)**. Track B investigation rejected the ACTIVE.md proposed `arabic_reshaper + bidi.get_display` fix as an empirical semantic no-op: PyMuPDF's Arial ToUnicode CMap produces visual-order presentation-form extraction regardless of whether input is pre-shaped, and tests already tolerate this via `pdf_text_layer_status in {"clean", "presentation_forms"}`. insert_htmlbox was also tested and produces WORSE extraction (Latin/Hebrew pollution from broken OpenType CMap). Resolution: docstring-only on both `_write_pdf` helpers documenting the semantics; no dependencies added. All 8 PDF tests pass unchanged.
   - Deterministic fallback documentation and review per Gemini CLI finding — **PENDING**
   - Hadith taxonomy completeness fix per Gemini CLI R2 finding — **PENDING (overlaps Phase 5a reviewer wave; defer amendment until wave returns)**
3. **Execute Track C doc fix** — `engines/source/CLAUDE.md` stale "no production code exists yet" line.
4. **Orthogonal amendments** deferred earlier: colophon-defense INV (CRITICAL from Gemini CLI source-commit review), REQ-SRC-0048 deferred-validation surface (R3 adversary BLOCKER), REQ-SRC-0030 genre expansion, INV-SRC-0012 refinement.
5. **Then** close OQ-SRC-0005 via DR-2 on agent monitoring scope.
6. **Then** move to Phase 5 (agent layer) tracer bullet.

### Active DR dispatches

- **DR-1 (level detection)** — adjudication 3-0 OPT-B closed. Phase 5a "executed" but **reviewer wave CLOSED 4 of 4 with convergent finding that Phase 5a is structurally paper-reconciled, not operationally landed**. Summary:
  - Codex CLI (structural, BLOCKER_PRESENT): 4 BLOCKERS + 7 AMEND — S1/S2/S4/S5/S6/S8/S9/S10 FAIL. Key code-level finding: contracts.py:197-201 still has English WorkLevel enum; SourceMetadata has no level_status field.
  - Gemini CLI Run A (scholarly, AMEND_REQUIRED): 1 BLOCKER + 1 HIGH + 4 AMEND. English enum leakage BLOCKER; hadith_collection conflation HIGH.
  - Gemini CLI Run B (scholarly, AMEND_REQUIRED): 0 BLOCKER + 2 HIGH + 1 MEDIUM + 5 AMEND + 1 CONFIRM. Run B UNIQUELY caught `wāsiṭ → wasīṭ` in INV-SRC-0011:30 rationale (مُدَرِك/city vs intermediate-text-type, as in al-Ghazālī's al-Wasīṭ). 2-run independence protocol validated.
  - CC adversary (pre-mortem, BLOCKER_PRESENT): 3 BLOCKERS + 9 HIGH + 1 MEDIUM. Adversary UNIQUELY caught non-applicable genre set divergence and 4/7 values unreachable from REQ-SRC-0030 (ADV-001, verified).
  - Outputs: `.kr/runtime/structural_audit_codex_cli_20260417.md`, `domain_validation_gemini_cli_run_A_20260417.md`, `domain_validation_gemini_cli_run_B_20260417.md`, `adversary_phase5a_20260417.md`.
- **DR-2 (agent monitoring scope)** — still deferred until Phase 5b closes.

### Phase 5a reviewer wave — consolidated findings (4 of 4 evaluators, wave CLOSED)

**4-of-4 confirmed BLOCKER** (all evaluators):
1. **English WorkLevel enum leakage** (Gemini A DVF-1 + Gemini B DVF-2 + Codex CAF-3 + Adversary ADV-002). INV-SRC-0011 AC-3, REQ-SRC-0007 AC-1/AC-3/AC-5, INV-SRC-0012 AC-1-4 use English values rejected by CON-SRC-0011. `engines/source/contracts.py:197-201` still defines `WorkLevel = {BEGINNER, INTERMEDIATE, ADVANCED, SPECIALIST}`, and `SourceMetadata` (line 860+) has NO `level_status` field. Code never followed the spec.

**3-of-4 confirmed:**
2. **Pedagogical hadith_collection conflation** (Gemini A DVF-2 + Gemini B DVF-1 + Adversary ADV-009). al-Arbaʿīn al-Nawawī, Bulūgh al-Marām, ʿUmdat al-Aḥkām are pedagogically graduated; unconditional non-applicable placement corrupts library.
3. **ALA-LC `muta'akhirūn` → `mutaʾakhkhirūn`** (Gemini A C1 + Gemini B C1 + Gemini B DVF-3). Apostrophe → right-half-ring; single kh → geminate khkh.

**2-of-4 confirmed (structural):**
4. **Ownership inconsistency** (Codex CAF-2 + Adversary ADV-003). DEC-SRC-0003 names synthesis as authoritative owner; CON-SRC-0004 pending_taxonomy binds to taxonomy. Generic "a downstream engine" paper-reconciles without resolving.
5. **Non-applicable list inclusiveness** (Gemini A C8 + Gemini B C8). Both suggest adding mawsūʿa; Run A also suggests muʿjam and fihris.

**Unique BLOCKER — single evaluator, structurally verified:**
6. **Non-applicable genre set divergent and unreachable** (Adversary ADV-001, verified by direct inspection). CON-SRC-0004 and REQ-SRC-0047 list 7 values; INV-SRC-0012 lists 4; REQ-SRC-0030 canonical genre enum contains only `hadith_collection` cleanly. 4 of 7 values (mushaf, rijal_dictionary, majmu, biographical_dictionary) are structurally unreachable; 2 are naming-mismatched (fatwa_compilation vs fatawa; lexicon vs mujam). Invariant 3 is untriggerable for 4/7 values.

**Unique HIGH scholarly finding — Run B only, verified by direct inspection:**
7. **`wāsiṭ → wasīṭ` in INV-SRC-0011:30 rationale** (Gemini B DVF-3). `wāsiṭ` (واسط, mediator/city) ≠ `wasīṭ` (وسيط, intermediate text type, as in al-Ghazālī's al-Wasīṭ fī al-Madhhab). Classical category error; Run A missed this.

**Unique BLOCKERS from single evaluator (structural, verifiable)**:
5. **Depends-on DAG broken** (Codex CAF-1): 4 cycles in the amendment set's depends_on graph (DEC↔REQ-SRC-0007, CON-SRC-0004↔CON-SRC-0011, INV-SRC-0011↔CON-SRC-0011, CON-SRC-0011↔REQ-SRC-0047). Breaks scoped injection.
6. **Deferred-validation surface undefined + REQ-SRC-0048 nonexistent** (Adversary ADV-005). Claimed resolution per ACTIVE.md; REQ-SRC-0048 atom does not exist.
7. **Prior R1 blockers paper-reconciled, not closed** (Codex CAF-6). Tests still pass because they assert the pre-Phase-5a surface; `level_status` never exercised.

**Unique HIGH findings from single evaluator (structural, verifiable)**:
- Nested-Optional depth-2 gap (Adversary ADV-011): positions[0].death_date unexercised.
- Shamela happy-path aborts with SRC-E-EVIDENCE-DROPPED (Adversary ADV-010): REQ-SRC-0037 doesn't mandate null-key emission for absent edition_info.
- level_provenance missing; owner override non-sticky (Adversary ADV-012).
- Pre-Phase-5a migration path undefined (Adversary ADV-013).
- ALA-LC `muta'akhirūn` → `mutaʾakhkhirūn` transliteration AMEND (Gemini C1).
- INDEX.yaml stale counts (Codex CAF-5): OQ-SRC-0001 deferred in INDEX but superseded in atom file.
- Severity taxonomy missing (Codex S7): schema enum `{fatal, blocking, warning}` has no operational definition anywhere.

**Verdict:** Phase 5a is structurally paper-reconciled. Phase 5b is required.

### Phase 5b work items (ordered)
1. ~~Align `engines/source/contracts.py`: WorkLevel enum values to Arabic (mubtadiʾ/mutawassiṭ/muntahī); add `level_status` field with 4-value enum; add `level_provenance` field.~~ **DONE 2026-04-17 (commit `62647cb2b`)**. pyright 0 errors across 6 live-code files; pytest 134/134 pass (from 75p/59f baseline — the paper-reconciliation gap made visible). Production code in `src/deliberation.py` now computes the (level, level_status, level_provenance) triple. ADV-012 stickiness enforced IFF-style via `model_validator`. Mandatory `level_status` field (no default); 4 cross-field invariants raise `ValueError` citing the CON-SRC-0004 invariant number on violation. See commit body for detail.
2. ~~Rewrite English-value ACs in INV-SRC-0011 (AC-3), REQ-SRC-0007 (AC-1/AC-3/AC-5), INV-SRC-0012 (AC-1-4) to use CON-SRC-0011 enum.~~ **DONE 2026-04-17 (commit `ec8d82ca4`)**. All 8 AC rewrites landed: INV-SRC-0011 AC-3 → mutawassiṭ; REQ-SRC-0007 AC-1 → mutawassiṭ, AC-3 → muntahī, AC-5 → mubtadiʾ (cross-field invariant violation); INV-SRC-0012 AC-1 → mubtadiʾ, AC-2 → muntahī, AC-3 → mutawassiṭ, AC-4 → muntahī (semantic replacement for "specialist"; 3-tier enum has no 4th tier). INV-SRC-0012 rationale also aligned with CON-SRC-0011 corrected enum (removed stale mutaqaddim reference). Gates clean: validate_spec.py 0 errors on 109 atoms, generate_views.py clean regeneration, pytest 134 passed (unchanged baseline).
3. ~~Fix transliteration errors: `muta'akhirūn` → `mutaʾakhkhirūn` (CON-SRC-0011); `wāsiṭ` → `wasīṭ` (INV-SRC-0011:30).~~ **DONE 2026-04-17 (commit `386685819`)**. ALA-LC apostrophe → right-half-ring (U+02BE) + geminate khkh; `wāsiṭ`/`wasīṭ` category fix per Gemini Run B finding. Spec views regenerated (picks up Phase 5a atom drift).
4. Amend REQ-SRC-0030 genre enum to cover non-applicable set; reconcile non-applicable list across CON-SRC-0004/REQ-SRC-0047/INV-SRC-0012 to a single canonical source; sub-classify hadith_collection (remove unconditionally-non-applicable placement).
5. Break 4 depends_on cycles (DEC↔REQ-SRC-0007, CON-SRC-0004↔CON-SRC-0011, INV-SRC-0011↔CON-SRC-0011, CON-SRC-0011↔REQ-SRC-0047) by re-orienting to producer-before-consumer only.
6. Create REQ-SRC-0048 for deferred validation surface (pending-override queue, re-validation trigger, genre_dispute tie-break).
7. Resolve ownership story (synthesis vs taxonomy) — pick one; align DEC-SRC-0003 and CON-SRC-0004.
8. Add migration path for pre-Phase-5a sources (default-on-read or one-shot migration per genre).
9. Fix Shamela happy-path SRC-E-EVIDENCE-DROPPED abort — either amend REQ-SRC-0037 to emit null-keys for absent apparatus, or downgrade REQ-SRC-0046 error to distinguish "upstream did not produce" from "packaging omitted".
10. Add `level_provenance` stickiness rule in REQ-SRC-0047 so owner override is not silently overwritten by downstream writes.
11. Add C7 multi-layer explicit interpretation clause to CON-SRC-0011 (scope: target_readership per Gemini B and Adversary consensus).
12. ~~Fix INDEX.yaml stale status (OQ-SRC-0001 → superseded; recount deferred/superseded).~~ **DONE 2026-04-21**. OQ-SRC-0001 atom file already said `superseded` since 2026-04-16; INDEX.yaml still said `deferred`. Reconciled to `superseded`, bumped INDEX `updated` to 2026-04-21. validate_spec.py counts now match atom files: 103 confirmed, 1 deferred (OQ-SRC-0005 only), 5 superseded (OQ-SRC-0001/0003/0004/0006/0007) on 109 atoms pre-item-13.
13. ~~Add severity taxonomy definition (fatal = unrecoverable data corruption; blocking = recoverable rejection; warning = advisory).~~ **DONE 2026-04-21**. Created `CON-SRC-0012` (topic: validation, layer: contracts, priority: high) in `engines/source/spec/20-contracts/constraints/CON-SRC-0012.yaml` with the three prescribed definitions. Six acceptance criteria: AC-1/2/3 accept correctly-labeled conditions (fatal for unrecoverable corruption, blocking for recoverable rejection, warning for advisory); AC-4/5/6 reject cross-category mismatches (correction-path → fatal mislabel, non-halting action → blocking mislabel, frozen-source mutation → warning mislabel). schema.json `/$defs/severity` extended with a `description` field cross-referencing CON-SRC-0012 so schema consumers find the semantic home. New topic `validation` registered. validate_spec.py 0 errors on 110 atoms (104 confirmed, 1 deferred, 5 superseded).
14. ~~Add REQ-SRC-0046 AC-7 for depth-2 nested optional serialization (positions[0].death_date).~~ **DONE 2026-04-21**. AC-7 added to REQ-SRC-0046 mirroring AC-6's SRC-E-EVIDENCE-DROPPED-NESTED error-path pattern but targeting `muhaqiq_output.positions[0].death_date` — the list-item sub-field case that Pydantic `exclude_unset` can silently drop when traversing list elements (AC-6 covers the scalar direct-child case only). Closes Adversary ADV-011. `updated` bumped to 2026-04-21, amendment rationale appended to `source` field explaining the AC-6 vs AC-7 structural distinction. No code surface exists yet for list-item D-023 enforcement — implementation deferred to a later Phase 5b surface item. validate_spec.py 0 errors; pytest engines/source/tests/ 156 pass / 1 skip (unchanged baseline).
15. ~~Write spec-linked tests that exercise `level_status`, the Arabic enum values, and the new error codes BEFORE declaring Phase 5b closure.~~ **DONE 2026-04-17 (commit `f965aec7b`)**. New `engines/source/tests/test_work_level_and_status.py` contains 22 passing tests + 1 documented skip, tagged `@pytest.mark.spec(atom_id, ac_id)` across CON-SRC-0011 AC-1..AC-6, CON-SRC-0004 invariants 1..4, ADV-012 stickiness (both directions), INV-SRC-0011 AC-1..AC-4, INV-SRC-0012 AC-2 (AC-1/AC-3/AC-4 skipped pending item 4 Genre enum expansion), REQ-SRC-0007 AC-3..AC-5. Item 15 required a small production-code change: `_resolve_level_fields` previously accepted override+non-applicable-genre silently (spec violation vs INV-SRC-0012); added `ErrorCode.LEVEL_OVERRIDE_NONAPPLICABLE = "SRC-E-LEVEL-OVERRIDE-NONAPPLICABLE"` and corresponding `SourceEngineError` raise at override boundary. Gates: validate_spec.py 0 errors, pyright 0 errors across prod+new tests, pytest 156 passed / 1 skipped (up from 134).

Phase 5b should end with a second reviewer wave to verify closure, with explicit test-run evidence this time (not just `validate_spec.py` passing).

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

## Session commits (2026-04-17, Phase 5b items 1 + 3)
- `62647cb2b` feat(source): Phase 5b item 1 — Arabic WorkLevel, level_status, provenance
- `386685819` fix(source): Phase 5b item 3 — ALA-LC transliteration corrections in spec

## Session commits (2026-04-17, Phase 5b items 2 + 15)
- `ec8d82ca4` fix(source): Phase 5b item 2 — Arabic WorkLevel enum in acceptance criteria
- `f965aec7b` test(source): Phase 5b item 15 — spec-linked tests for level triple (156 pass)

## Session commits (2026-04-21, Phase 5b items 12 + 13 + 14)
- `bf4354399` fix(source): Phase 5b 12-14 — INDEX drift, severity taxonomy, AC-7
- `a4f2b2788` fix(source): Phase 5b 12-14 retroactive review — 2 BLOCKERs + 1 3-way AMEND

## Retroactive review follow-ups (new Phase 5b items discovered 2026-04-21)

The 3-evaluator retroactive review of `bf4354399` (Codex CLI + Gemini CLI 2 runs) surfaced items that were addressed immediately (see `a4f2b2788`) AND items deferred for later:

16. ~~Pre-existing REQ-SRC-0046 paper-reconciliation — `SRC-E-EVIDENCE-DROPPED` and `SRC-E-EVIDENCE-DROPPED-NESTED` are cited in the atom but absent from `contracts.py` `ErrorCode` enum.~~ **DONE 2026-04-21**. Pre-commit 3-evaluator dispatch (Codex CLI structural + Gemini CLI 2 independent scholarly runs, all through `/prompt-architect`) reached unanimous PREFER_B verdict: chose Option B over Option A. Implementation: added `HANDOFF_EVIDENCE_DROPPED = "SRC-E-HANDOFF-EVIDENCE-DROPPED"` and `HANDOFF_EVIDENCE_DROPPED_NESTED = "SRC-E-HANDOFF-EVIDENCE-DROPPED-NESTED"` to `engines/source/contracts.py::ErrorCode` step-60 block; amended REQ-SRC-0046 at 5 reference sites (behavior.error_conditions @113/@116, AC-3/AC-6/AC-7 then-clauses) to use the HANDOFF_ prefix; appended Phase 5b item 16 amendment note to `source` field preserving historical context; regenerated views. Rationale: (a) step-40 PDF_TEXT_EVIDENCE_DROPPED protects PyMuPDF primary-text extraction (T-1 Silent Text Corruption) whereas step-60 handoff packaging omission maps to T-2 Attribution Error / T-6 Metadata Poisoning in reference/KNOWLEDGE_INTEGRITY.md — distinct threats deserve distinct code families; (b) ChatGPT DR 2026-04-16 advisory (dr-chatgpt-level-detection-20260416.yaml:950) had already recommended this rename but went unacted-on — item 16 was the bounded opportunity to act before any implementation raises; (c) translation safety — unadorned "إسقاط الدليل" (Option A gloss) risks conflation with hadith-science proof rejection (دليل شرعي / شاهد / قرينة), while "إسقاط دليل التسليم" (Option B) grounds the error cleanly in pipeline-logistics semantics for the non-technical Muslim student reading error surfaces. Gates: validate_spec.py 0 errors on 110 atoms, pyright 0 errors on contracts.py, pytest 156 pass / 1 skip (unchanged baseline). Reviewer outputs at `.kr/runtime/structural_audit_codex_cli_item16_precommit_20260421.md`, `.kr/runtime/domain_validation_gemini_cli_item16_run_A_20260421.md`, `.kr/runtime/domain_validation_gemini_cli_item16_run_B_20260421.md` (gitignored). Dispatch log entries appended to `.kr/runtime/dispatch_log.jsonl`.
17. Spec-linked tests for CON-SRC-0012 ACs (1-6) and REQ-SRC-0046 AC-7 — no `@pytest.mark.spec` tags exist for these new ACs. Codex S6-DIM6D. Test authoring with real-fixture data.
18. Taxonomy expansion for scholarly nuances — both Gemini runs (AMEND DIM1) independently flagged that the fatal/blocking/warning three-tier collapses scholarly distinctions (tahqiq uncertainty, hamza-family ambiguity, agent-disagreement resolvability, owner-override rejection). Either expand CON-SRC-0012 with additional guidance, add compound-severity metadata payloads, or introduce a fourth severity tier. Substantive design decision — requires DR or additional reviewer wave before atom amendment.
19. REQ-SRC-0046 severity reclassification for SRC-E-HANDOFF-EVIDENCE-DROPPED / SRC-E-HANDOFF-EVIDENCE-DROPPED-NESTED — surfaced by both Gemini runs during item-16 dispatch (DIM2 AMEND, cross-confirmed). CON-SRC-0012's operational taxonomy explicitly places "missing required-preserved evidence that upstream can re-emit" in the `blocking` tier (recoverable rejection with a correction path), not `fatal` (unrecoverable corruption). REQ-SRC-0046 currently declares both conditions `severity: fatal`. Gemini B DIM2 rationale: "Option B's 'HANDOFF' prefix makes it clear this is a recoverable boundary transmission failure rather than source corruption." This interacts with existing Phase 5b item 9 (Shamela happy-path SRC-E-HANDOFF-EVIDENCE-DROPPED abort) — resolving severity and item 9 together is the cleanest path. Deferred from item 16 per the bounded-scope principle; dispatch new reviewer wave before atom amendment.
20. REQ-SRC-0046 raise-site wiring in `engines/source/src/admission.py::_build_handoff_bundle` — surfaced by Codex item-16 DIM4 AMEND. Enum entries and spec references now align, but no implementation code raises SRC-E-HANDOFF-EVIDENCE-DROPPED[-NESTED] on dropped top-level or list-item D-023 signals yet. Codex evidence: admission.py:220-229 is the natural host. Must track the raise-site wiring as a distinct work item so enum+spec alignment is not mistaken for operational closure of REQ-SRC-0046. Test authoring for AC-3/AC-6/AC-7 (item 17) depends on this item landing first.

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
