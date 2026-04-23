> Purpose: Define the single current frontier and the exact deliverable expected from the next serious work session.
> Authority: The only authoritative next-session task file.
> Update when: The active frontier changes, the deliverable changes, or the success criteria change.
> Must not contain: Session diary, multiple parallel frontiers, broad backlog, durable project law.

## Role Relationship
Owner = CLIENT (non-technical, minimum Islamic knowledge). All agents = ENGINEERING TEAM.
The owner provides reactions and preferences. Agents drive direction, identify gaps, propose next steps.
Never ask the owner engineering questions. Never wait for the owner to identify what's needed next.

# KR Active Frontier

Status: active — Phase 5b items 1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 14, 15, 16 closed (commits `62647cb2b`, `ec8d82ca4`, `386685819`, `bf4354399`+`a4f2b2788` retroactive-review amendments, `f965aec7b`, `a1fabdd54`+`366463bcb` item-16, `b651b20eb`+`6ad0614eb` item-4 Option E-prime-final, `491e9f2ca` item-5 depends_on cycle break, `08cc94633` items 6+7 synthesis-owns-level + REQ-SRC-0048 deferred validation, `41f60c385` item-11 C7 multi-layer target_readership scope clause, `d95a24ea0` item-10 ADV-012 stickiness postcondition + AC-6). **2 Phase 5b work items remain (8, 9)** plus 3 follow-ups from 12-14 retroactive (17, 18 remain; 16 DONE) plus 2 from item-16 dispatch (19, 20) plus 6 from item-4 dispatch (21, 22, 23, 24, 25, 26) plus 1 from item-5 dispatch (27) plus 2 from item-7 dispatch (28 LevelProvenance cleanup, 29 REQ-SRC-0048 test authoring)

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
4. ~~Amend REQ-SRC-0030 genre enum to cover non-applicable set; reconcile non-applicable list across CON-SRC-0004/REQ-SRC-0047/INV-SRC-0012 to a single canonical source; sub-classify hadith_collection (remove unconditionally-non-applicable placement).~~ **DONE 2026-04-23 (Option E-prime-final).** Three pre-commit dispatch cycles across 2026-04-21 and 2026-04-22 (all through `/prompt-architect`, 3 evaluators per cycle: Codex CLI structural + Gemini CLI 2 independent scholarly runs) landed the final architecture: Genre.MUSHAF added; NON_APPLICABLE_GENRE_VALUES reconciled to 6-value frozenset `{mushaf, hadith_collection, mashyakhah, thabat, barnamaj, fahrasah}` — all six existing Genre enum members, all six fann-level archival/reference/revelation works; INV-SRC-0012 rewritten around a 3-axis gate (Axis 1 genre, Axis 2 composite_work_type=="majmu", Axis 3 HadithSubgenre-deferred-to-item-23); composite_work_type threaded from IntakeDossier through MetadataDeliberationInput into SourceMetadata; SourceMetadata.enforce_level_invariants accepts either Axis 1 or Axis 2 firing; INV-SRC-0012 AC-3/AC-4 rewritten around composite_work_type axis with exemplars رسائل ابن رجب and مجموع فتاوى ابن تيمية; CON-SRC-0004, REQ-SRC-0047, REQ-SRC-0030 aligned to the 3-axis gate and 6-value set. Gates: validate_spec.py 0 errors on 110 atoms; pyright 0 errors across engines/source/src/; pytest 160 pass / 0 skip (up from 156 pass / 1 skip — mushaf AC-1 unblocks + 3 new Axis-2 tests). Dispatch-cycle summary: (a) A/B/C/D cycle blocked unanimously by 2-run Gemini BLOCKER_PRESENT on classical-taxonomy category errors; (b) Option E cycle blocked unanimously on DIM4 archival-genre regression; (c) Option E-prime cycle returned unanimous AMEND_REQUIRED adding FAHRASAH (convergent from both runs). Codex E-prime PROCEED_WITH_AMENDMENTS confirmed `prior_must_fix_still_applies: true`, `classifier_emits_added_genres: no`. New follow-ups opened (items 24-26). Reviewer outputs: `.kr/runtime/structural_audit_codex_cli_item4eprime_precommit_20260422.md`, `.kr/runtime/domain_validation_gemini_cli_item4eprime_run_{A,B}_20260422.md`, plus the 6 prior-cycle outputs. Dispatch log in `.kr/runtime/dispatch_log.jsonl`.
5. ~~Break 4 depends_on cycles (DEC↔REQ-SRC-0007, CON-SRC-0004↔CON-SRC-0011, INV-SRC-0011↔CON-SRC-0011, CON-SRC-0011↔REQ-SRC-0047) by re-orienting to producer-before-consumer only.~~ **DONE 2026-04-23**. Cycles broken via producer-before-consumer re-orientation: (a) removed `REQ-SRC-0007` from DEC-SRC-0003.depends_on — DEC authorizes the downstream-owns-level architecture, REQ-SRC-0007 implements handoff preservation within it, so REQ consumes DEC not the reverse; (b) stripped CON-SRC-0011.depends_on from 4 entries down to 1 (DEC-SRC-0003 only) — CON-SRC-0011 is the WorkLevel enum PRODUCER, so it cannot depend on its consumers INV-SRC-0011 / CON-SRC-0004 / REQ-SRC-0047. Amendment notes added to both atoms' source fields citing Codex CAF-1. Verified via explicit DFS cycle detection on the full 110-atom graph: all 4 target cycles gone. 9 pre-existing cycles elsewhere in the graph (OQ-SRC-0005, REQ-SRC-0012, INV-SRC-0002, REQ-SRC-0001, REQ-SRC-0019, REQ-SRC-0025) detected as a side effect but OUT OF SCOPE for item 5 — recorded as item 27. Gates: validate_spec.py 0 errors on 110 atoms; pyright 0 errors; pytest 160 pass / 0 skip (unchanged).
6. ~~Create REQ-SRC-0048 for deferred validation surface (pending-override queue, re-validation trigger, genre_dispute tie-break).~~ **DONE 2026-04-23** (commit `08cc94633`). Landed as a source-engine atom at `engines/source/spec/10-pipeline/40-intake-analysis/REQ-SRC-0048.yaml` per `REQ-SRC-*` atom-naming convention. Resolves Phase 5a adversary finding ADV-005 (deferred-validation surface cited in prior atoms but nonexistent). Six acceptance criteria cover: AC-1 queue-on-intake when genre pending, AC-2 apply-on-resolution (leveled genre + no non-applicability axis), AC-3 reject-on-resolution (INV-SRC-0012 axis fires), AC-4 defer-to-synthesis on genre_dispute (D-041 consensus failure routes to OWN_SYNTHESIS tie-break authority), AC-5 standard REQ-SRC-0047 path bypasses queue when genre known at intake, AC-6 48-hour staleness warning. Three error conditions: SRC-E-OVERRIDE-QUEUE-ABANDONED, SRC-E-OVERRIDE-QUEUE-UNANIMOUSLY-NONAPPLICABLE, SRC-W-OVERRIDE-QUEUE-STALE. Status confirmed, confidence medium (content derived from item-7 3-evaluator scope_guidance rather than a dedicated atom-design dispatch; follow-up item 29 opened for test authoring + hardening review). Host location resolved via naming convention after evaluator divergence (Run A source / Codex cross-engine / Run B synthesis). Depends on REQ-SRC-0047, REQ-SRC-0030, CON-SRC-0004, CON-SRC-0011, INV-SRC-0012, DEC-SRC-0003. validate_spec.py 0 errors on 111 atoms.
7. ~~Resolve ownership story (synthesis vs taxonomy) — pick one; align DEC-SRC-0003 and CON-SRC-0004.~~ **DONE 2026-04-23** (commit `08cc94633`). 3-of-3 UNANIMOUS_OWN_SYNTHESIS HIGH-confidence verdict from Codex CLI gpt-5.4 (architectural-fit axis) + Gemini CLI Run A gemini-3.1-pro-preview + Gemini CLI Run B gemini-2.5-pro (classical-scholarly-defensibility axis, 2-run discipline per `.claude/rules/no-single-model-conclusion.md`). Cross-provider OpenAI+Google independence achieved despite Gemini 3.1-pro-preview 429 rate-limit that required Run B fallback to stable-tier model. Implementation edits: CON-SRC-0004 enum value `pending_taxonomy` → `pending_synthesis` throughout, "deferred to the taxonomy engine" → "synthesis engine", generic "a downstream engine" → "the synthesis engine" (Run B unique catch on rule.implication lines 74-78); INV-SRC-0011 AC-4 synchronized rename (rule.implication already named synthesis — no functional change needed, only AC reference); DEC-SRC-0003 amendment note re-confirming existing "synthesis" naming ratified by the 3-evaluator verdict (zero functional change); REQ-SRC-0007 + REQ-SRC-0047 synchronized renames; contracts.py `LevelStatus.PENDING_TAXONOMY` → `PENDING_SYNTHESIS`; src/deliberation.py updated; 5 test files renamed. Classical grounding cross-confirmed: al-Fihrist + Kashf al-Ẓunūn classify fann+nawʿ but omit martaba; Ibn Khaldūn Muqaddima VI anchors martaba in content density + tadarruj; al-Zarnūjī Taʿlīm al-Mutaʿallim IV distinguishes reader-martaba from text-martaba. Run B uniquely surfaced al-Kattānī al-Risāla al-Mustaṭrafah as OWN_TAXONOMY counter-argument (nawʿ-classification of ḥadīth books could extend to martaba) but weighed down by bibliographic-vs-pedagogical distinction. Gates: validate_spec 0 errors on 111 atoms; pyright 0 errors; pytest 160 pass / 0 skip (unchanged baseline). Reviewer outputs gitignored at `.kr/runtime/structural_audit_codex_cli_item7_retry_20260423.md`, `.kr/runtime/domain_validation_gemini_cli_item7_run_{A,B}_20260423.md`.
8. Add migration path for pre-Phase-5a sources (default-on-read or one-shot migration per genre).
9. Fix Shamela happy-path SRC-E-EVIDENCE-DROPPED abort — either amend REQ-SRC-0037 to emit null-keys for absent apparatus, or downgrade REQ-SRC-0046 error to distinguish "upstream did not produce" from "packaging omitted".
10. ~~Add `level_provenance` stickiness rule in REQ-SRC-0047 so owner override is not silently overwritten by downstream writes.~~ **DONE 2026-04-23**. ADV-012 proposed_fix had two halves: (1) mandatory level_provenance enum on the data model — LANDED in Phase 5b item 1 (commit `62647cb2b`, LevelProvenance enum + SourceMetadata.enforce_level_invariants model_validator); (2) stickiness postcondition in REQ-SRC-0047 — LANDED here. REQ-SRC-0047.behavior.postconditions now carries a block-scalar stickiness clause declaring the cross-engine contract: the (level, level_provenance) pair produced by an accepted override is ADV-012-sticky at the data-model layer via the Pydantic IFF invariant AND at the cross-engine layer as the "do not silently overwrite" beacon for any downstream level-writing authority (synthesis engine per DEC-SRC-0003 synthesis-owns-level). AC-6 added with `then` clause explicitly documenting the LAYERED DEFENSE discovered during test authoring: CON-SRC-0004 invariant 1 (level_status=assigned IFF level non-null) fires FIRST on attack path (a) "clear level alone" because it precedes ADV-012 stickiness in the validator ordering — stronger protection than single-invariant expected. ADV-012 stickiness remains sole defender for attack path (b) "clear provenance alone". AC-6 then-clause cites either invariant as acceptable because the outcome (assignment rejected, record unmutated) is identical under either layer. Two spec-linked tests authored in `engines/source/tests/test_work_level_and_status.py`: `test_req_src_0047_ac6_level_provenance_stickiness` (single-field attack paths a+b) and `test_req_src_0047_ac6_provenance_survives_handoff` (cross-engine signal preservation through handoff JSON byte-exact). Note on scope limit documented in both spec and test: the IFF invariants catch PAIR-CLEARING attacks but cannot catch the VALUE-SWAP attack (mubtadiʾ→muntahī while provenance stays OWNER_OVERRIDE) because (muntahī, OWNER_OVERRIDE) is a structurally valid pair — that enforcement is the cross-engine contract to be carried by synthesis engine spec when built. Gates: validate_spec.py 0 errors on 111 atoms, pyright 0 errors across engines/source/src/ + contracts.py + tests, pytest 163 pass / 0 skip (up from 161 via 2 new AC-6 tests). **Dispatch deferred to Phase 5b closure reviewer wave** per approved bundled cadence — the stickiness mandate is pre-existing multi-evaluator consensus from ADV-012, and the layered-defense discovery is structurally observable (test-run evidence). The closure wave MUST explicitly review: (a) the scope-limit note (can the value-swap be caught at the source-engine boundary via audit-trail cross-check?), (b) the block-scalar postcondition phrasing for downstream synthesis-engine spec consumption, (c) whether CON-SRC-0004 invariant 1 displacing ADV-012 as fires-first on path (a) warrants reordering the invariant block to make ADV-012 the primary error message.
11. ~~Add C7 multi-layer explicit interpretation clause to CON-SRC-0011 (scope: target_readership per Gemini B and Adversary consensus).~~ **DONE 2026-04-23**. Rule extended in CON-SRC-0011: `rule.statement` now includes the multi-layer scope clause — for a multi-layer work (matn+sharḥ, sharḥ+ḥāshiya, deeper nestings), the single scalar SourceMetadata.level refers to the TARGET READERSHIP of the composite work as a whole, NOT the contained layer's level, the author's own rank, or the matn's intrinsic density. `rule.implication` extended with the companion scope-error violation clause — populating level from author-rank or matn-density is a T-2 corruption vector at the scope-interpretation layer. AC-7 added with classical exemplar شرح الأصول الثلاثة of Ibn ʿUthaymīn (muntahī author, mubtadiʾ target readership → level="mubtadiʾ"). AC-7 includes contrapositive check confirming the validator accepts both mubtadiʾ and muntahī strings at enum layer — which is why the scope clause is load-bearing documentation for downstream writers (synthesis engine per DEC-SRC-0003), not runtime protection. Resolves Phase 5a adversary finding ADV-007 (HIGH, V3 attack vector, affected atoms REQ-SRC-0046, CON-SRC-0011, CON-SRC-0004) via the stronger target-readership interpretation rather than ADV-007's proposed "outer author's work only" fallback. Amendment note appended to atom `source` field citing both evidence locations (Gemini Run B:95-102, Adversary:242-252). Test authored in `engines/source/tests/test_work_level_and_status.py::test_con_src_0011_ac7_multi_layer_target_readership` including is_multi_layer=True metadata construction and contrapositive assertion. Gates: validate_spec.py 0 errors on 111 atoms, pyright 0 errors across engines/source/src/ + contracts.py, pytest 161 pass / 0 skip (up from 160 via new AC-7 test). **Dispatch deferred to Phase 5b closure reviewer wave** (Task #5) per approved bundled cadence — the scope decision (target_readership) is pre-existing multi-evaluator consensus from Phase 5a (Gemini B C7 CONFIRM + Adversary ADV-007), so item 11's atom-wording integration defers per-item dispatch to the closure sweep. The closure wave MUST explicitly review: (a) Ibn ʿUthaymīn exemplar vs alternate-madhhab exemplar, (b) rule.statement placement vs a dedicated `scope` subkey, (c) "target readership" phrasing consistency with existing INV-SRC-0011 terminology.
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

## Session commits (2026-04-21, Phase 5b item 16)
- `a1fabdd54` fix(source): Phase 5b 16 — HANDOFF_EVIDENCE_DROPPED enum + atom rename (156 pass, 1 skip)

## Session commits (2026-04-22, Phase 5b item 4 BLOCKED — no code/spec commit)
- (none) Pre-commit 3-evaluator dispatch on 4 drafted options surfaced unanimous scholarly BLOCKER_PRESENT from both Gemini runs on classical-taxonomy category errors. Item 4 re-scoped to Option E (MUSHAF-only + orthogonal gate redesign), requires fresh dispatch. Only ACTIVE.md + dispatch_log.jsonl updated.

## Session commits (2026-04-23, Phase 5b item 4 closure — Option E-prime-final)
- `b651b20eb` fix(source): Phase 5b 4 — Option E-prime-final 3-axis non-applicability gate (160 pass, 0 skip)
- `6ad0614eb` docs(source): ACTIVE.md — record Phase 5b item 4 commit hash b651b20eb

## Session commits (2026-04-23, Phase 5b item 5 — break 4 depends_on cycles)
- `491e9f2ca` fix(source): Phase 5b 5 — break 4 depends_on cycles (producer-before-consumer)

## Session commits (2026-04-23, Phase 5b items 6 + 7 — synthesis-owns-level + REQ-SRC-0048)
- `08cc94633` fix(source): Phase 5b 6+7 — synthesis owns level (160 pass, 0 skip)
- `48664c1ca` docs(source): ACTIVE.md — record Phase 5b items 6+7 commit hash 08cc94633

## Session commits (2026-04-23, Phase 5b item 11 — C7 multi-layer scope clause)
- `41f60c385` fix(source): Phase 5b 11 — C7 multi-layer target_readership scope (161 pass, 0 skip)
- `fa67e1464` docs(source): ACTIVE.md — record Phase 5b item 11 commit hash 41f60c385

## Session commits (2026-04-23, Phase 5b item 10 — ADV-012 stickiness postcondition)
- `d95a24ea0` fix(source): Phase 5b 10 — ADV-012 stickiness postcondition + AC-6 (163 pass, 0 skip)
- (pending) docs(source): ACTIVE.md — record Phase 5b item 10 commit hash d95a24ea0

## Retroactive review follow-ups (new Phase 5b items discovered 2026-04-21)

The 3-evaluator retroactive review of `bf4354399` (Codex CLI + Gemini CLI 2 runs) surfaced items that were addressed immediately (see `a4f2b2788`) AND items deferred for later:

16. ~~Pre-existing REQ-SRC-0046 paper-reconciliation — `SRC-E-EVIDENCE-DROPPED` and `SRC-E-EVIDENCE-DROPPED-NESTED` are cited in the atom but absent from `contracts.py` `ErrorCode` enum.~~ **DONE 2026-04-21**. Pre-commit 3-evaluator dispatch (Codex CLI structural + Gemini CLI 2 independent scholarly runs, all through `/prompt-architect`) reached unanimous PREFER_B verdict: chose Option B over Option A. Implementation: added `HANDOFF_EVIDENCE_DROPPED = "SRC-E-HANDOFF-EVIDENCE-DROPPED"` and `HANDOFF_EVIDENCE_DROPPED_NESTED = "SRC-E-HANDOFF-EVIDENCE-DROPPED-NESTED"` to `engines/source/contracts.py::ErrorCode` step-60 block; amended REQ-SRC-0046 at 5 reference sites (behavior.error_conditions @113/@116, AC-3/AC-6/AC-7 then-clauses) to use the HANDOFF_ prefix; appended Phase 5b item 16 amendment note to `source` field preserving historical context; regenerated views. Rationale: (a) step-40 PDF_TEXT_EVIDENCE_DROPPED protects PyMuPDF primary-text extraction (T-1 Silent Text Corruption) whereas step-60 handoff packaging omission maps to T-2 Attribution Error / T-6 Metadata Poisoning in reference/KNOWLEDGE_INTEGRITY.md — distinct threats deserve distinct code families; (b) ChatGPT DR 2026-04-16 advisory (dr-chatgpt-level-detection-20260416.yaml:950) had already recommended this rename but went unacted-on — item 16 was the bounded opportunity to act before any implementation raises; (c) translation safety — unadorned "إسقاط الدليل" (Option A gloss) risks conflation with hadith-science proof rejection (دليل شرعي / شاهد / قرينة), while "إسقاط دليل التسليم" (Option B) grounds the error cleanly in pipeline-logistics semantics for the non-technical Muslim student reading error surfaces. Gates: validate_spec.py 0 errors on 110 atoms, pyright 0 errors on contracts.py, pytest 156 pass / 1 skip (unchanged baseline). Reviewer outputs at `.kr/runtime/structural_audit_codex_cli_item16_precommit_20260421.md`, `.kr/runtime/domain_validation_gemini_cli_item16_run_A_20260421.md`, `.kr/runtime/domain_validation_gemini_cli_item16_run_B_20260421.md` (gitignored). Dispatch log entries appended to `.kr/runtime/dispatch_log.jsonl`.
17. Spec-linked tests for CON-SRC-0012 ACs (1-6) and REQ-SRC-0046 AC-7 — no `@pytest.mark.spec` tags exist for these new ACs. Codex S6-DIM6D. Test authoring with real-fixture data.
18. Taxonomy expansion for scholarly nuances — both Gemini runs (AMEND DIM1) independently flagged that the fatal/blocking/warning three-tier collapses scholarly distinctions (tahqiq uncertainty, hamza-family ambiguity, agent-disagreement resolvability, owner-override rejection). Either expand CON-SRC-0012 with additional guidance, add compound-severity metadata payloads, or introduce a fourth severity tier. Substantive design decision — requires DR or additional reviewer wave before atom amendment.
19. REQ-SRC-0046 severity reclassification for SRC-E-HANDOFF-EVIDENCE-DROPPED / SRC-E-HANDOFF-EVIDENCE-DROPPED-NESTED — surfaced by both Gemini runs during item-16 dispatch (DIM2 AMEND, cross-confirmed). CON-SRC-0012's operational taxonomy explicitly places "missing required-preserved evidence that upstream can re-emit" in the `blocking` tier (recoverable rejection with a correction path), not `fatal` (unrecoverable corruption). REQ-SRC-0046 currently declares both conditions `severity: fatal`. Gemini B DIM2 rationale: "Option B's 'HANDOFF' prefix makes it clear this is a recoverable boundary transmission failure rather than source corruption." This interacts with existing Phase 5b item 9 (Shamela happy-path SRC-E-HANDOFF-EVIDENCE-DROPPED abort) — resolving severity and item 9 together is the cleanest path. Deferred from item 16 per the bounded-scope principle; dispatch new reviewer wave before atom amendment.
20. REQ-SRC-0046 raise-site wiring in `engines/source/src/admission.py::_build_handoff_bundle` — surfaced by Codex item-16 DIM4 AMEND. Enum entries and spec references now align, but no implementation code raises SRC-E-HANDOFF-EVIDENCE-DROPPED[-NESTED] on dropped top-level or list-item D-023 signals yet. Codex evidence: admission.py:220-229 is the natural host. Must track the raise-site wiring as a distinct work item so enum+spec alignment is not mistaken for operational closure of REQ-SRC-0046. Test authoring for AC-3/AC-6/AC-7 (item 17) depends on this item landing first.
21. Genre naming-resolution follow-up — surfaced by Codex item-4 DIM3 + both Gemini runs DIM2 AMEND. When item 4 / Option E lands, a separate reviewed work stream should re-examine whether FATAWA↔FATWA_COMPILATION and MUJAM↔LEXICON naming should be reconciled. Both Gemini runs independently argue KEEP canonical Fatāwā and Muʿjam (the hadith muʿjam organizes by shuyūkh, distinct from lexicon/qāmūs — erasing the distinction is anachronism). Codex neutral structurally. If the naming-resolution is addressed at all, it must include classifier output templates and all raw-string consumers per `.claude/rules/shared-concept-changes.md`.
22. Gemini R2 non-applicable expansion — surfaced by Codex item-4 synthesis + both Gemini runs DIM4. Prior-art P2 recommended adding mawsūʿa, muʿjam, fihris to NON_APPLICABLE_GENRE_VALUES. Run A confirms P2; Run B amends P2 flagging classical-vs-modern mawsūʿa anachronism risk (modern al-Mawsūʿa al-Fiqhiyya al-Kuwaytiyya is clearly non-pedagogical, but applying `mawsūʿa` to classical works like Ibn al-Athīr's al-Nihāya is anachronistic). Requires scholarly review of (a) canonical enum value form (transliterated "mawsūʿa" vs existing ASCII "mawsuah"), (b) whether addition covers classical works or is modern-only. Substantive design decision — dispatch new reviewer wave before atom amendment.
23. HadithSubgenre-based level-applicability gate — surfaced by Codex item-4 DIM4 AMEND + both Gemini runs DIM3 CONFIRM P1. Redesign the non-applicability check so `hadith_collection` with `HadithSubgenre.ARBAIN` (pedagogical 40-hadith collections like al-Arbaʿīn al-Nawawī, Bulūgh al-Marām) IS level-applicable, while `HadithSubgenre.MUSANNAF/MUSNAD/JAMI` (transmission collections like Ṣaḥīḥ al-Bukhārī, Musnad Aḥmad) stay non-applicable. Codex DIM4 evidence: hadith_subgenre is currently an orthogonal field (contracts.py:935) with no invariant wiring. Requires new atom or amendment to REQ-SRC-0011 + deliberation.py gate logic redesign. Existing test `test_inv_src_0012_ac2_hadith_collection_rejects_override` (line 421) will become wrong under this redesign — rewrite required. The INV-SRC-0012 Axis 3 slot now exists in the 3-axis gate; implementation is what's deferred.
24. majmuʿ constituent-rasāʾil leveling architecture — surfaced by both Option E Gemini runs DIM1 AMEND convergent and reconfirmed by both E-prime runs DIM3. A majmuʿ container (composite_work_type="majmu") fires INV-SRC-0012 Axis 2 non-applicability at the container level, which is scholarly-correct for the aggregate, but the contained rasāʾil may individually carry pedagogical level. Example: مجموع رسائل ابن رجب contains specific rasāʾil like رسالة في فضل علم السلف, each of which has its own pedagogical tier when read independently. Requires an architectural decision: (a) emit constituent-level metadata in sub_work_inventory entries (REQ-SRC-0038 expansion); (b) defer all constituent leveling to taxonomy via sub-work decomposition; (c) treat the majmuʿ container as the only leveling unit (current default). No current atom addresses this. Substantive design decision — dispatch new reviewer wave before atom amendment.
25. MUJAM hadith-science sub-classification — PRELIMINARY, Run-A-only finding from Option E Gemini cycle 2026-04-22. Classical hadith muʿjam works (e.g. al-Muʿjam al-Kabīr of al-Ṭabarānī, organized by shuyūkh — the narrator's teachers) serve an archival/reference function distinct from a linguistic lexicon muʿjam (e.g. al-Qāmūs al-Muḥīṭ of al-Fīrūzābādī). Genre.MUJAM currently conflates these. Run A recommended distinguishing the hadith-science usage as non-applicable; Run B did not confirm. PRELIMINARY until second independent confirmation per `.claude/rules/no-single-model-conclusion.md`. Requires scholarly review to establish whether the distinction warrants a new Genre value, a HadithSubgenre.MUJAM carve-out (already exists at contracts.py:181), or a field on SourceMetadata.
26. TABAQAT non-applicability — PRELIMINARY, Run-A-only finding from E-prime Gemini cycle 2026-04-22. Run A argued TABAQAT (biographical layers / dictionaries, analogous to rijal_dictionary, cited via al-Kattānī's al-Risālah al-Mustaṭrafah) should be in the non-applicable set alongside mashyakhah/thabat/barnamaj/fahrasah; Run B did not raise this. PRELIMINARY until second independent confirmation per `.claude/rules/no-single-model-conclusion.md`. Scholarly tension: classical tabaqat works like Ibn Saʿd's al-Ṭabaqāt al-Kubrā are core reference literature, but some taught tabaqat texts (e.g. al-Nawawī's Tahdhīb al-Asmāʾ wa-al-Lughāt, used pedagogically in hadith-science curricula) may be leveled. Dispatch new reviewer wave before atom amendment.
27. Nine pre-existing depends_on cycles elsewhere in the spec graph — surfaced during item 5 verification via explicit DFS cycle detection on the 110-atom graph. Cycles found: `OQ-SRC-0005 ↔ DEC-SRC-0004`, `OQ-SRC-0005 ↔ REQ-SRC-0008`, `REQ-SRC-0012 ↔ INV-SRC-0004`, `INV-SRC-0002 → REQ-SRC-0014 → REQ-SRC-0004 → INV-SRC-0002`, `REQ-SRC-0001 ↔ DEC-SRC-0014`, `REQ-SRC-0025 → REQ-SRC-0019 → REQ-SRC-0018 → REQ-SRC-0001 → DEC-SRC-0014 → REQ-SRC-0025`, `REQ-SRC-0019 ↔ REQ-SRC-0021`, `REQ-SRC-0025 ↔ DEC-SRC-0016`, `REQ-SRC-0025 ↔ REQ-SRC-0027`. These cycles were NOT flagged by Codex CAF-1 (which only audited the 4 level-subsystem cycles targeted by item 5), so they pre-date the level-detection work. Fixing them requires producer-consumer analysis on the freeze/intake/container-classification sub-graph — substantive spec design work that requires `spec-contract-architect` dispatch (Codex CLI) before amendment. scoped-injection remains partially broken until this is resolved; build-phase scoped-atom packs for steps 10-40 could silently include cyclically-referenced atoms.
28. `LevelProvenance.TAXONOMY_ENGINE` architectural unreachability — surfaced during item 7 implementation. `engines/source/contracts.py::LevelProvenance` enum (~line 226-235) carries three values: `OWNER_OVERRIDE`, `TAXONOMY_ENGINE`, `SYNTHESIS_ENGINE`. Under OWN_SYNTHESIS ownership (item 7 closure), `TAXONOMY_ENGINE` is architecturally unreachable — taxonomy has no mandate to authoritatively write level, so that provenance value can never be legitimately emitted. The 3 item-7 evaluators did NOT examine LevelProvenance because it was not in their required reading list. Bounded-scope discipline kept this out of the item 7 commit. Cleanup options: (a) prune the enum to `{OWNER_OVERRIDE, SYNTHESIS_ENGINE}` (tighter, aligned with single-writer discipline); (b) keep `TAXONOMY_ENGINE` as reserved-for-future-contingency (softer, acknowledges possibility of later tax-authority split). Requires dedicated 3-evaluator dispatch (structural + scholarly) before amendment because the enum is consumed by ADV-012 stickiness invariant and by LevelAssessment history (ChatGPT DR SEC-7 design). Substantive design decision — dispatch new reviewer wave before atom/code amendment.
29. REQ-SRC-0048 test authoring — six ACs defined in the new atom (AC-1 queue-on-intake, AC-2 apply-on-resolution, AC-3 reject-on-resolution-axis-1, AC-4 defer-to-synthesis-on-dispute, AC-5 standard-path-bypass, AC-6 staleness-warning). Test fixtures for the pending-override queue surface do not yet exist in `engines/source/tests/`. Item 6 landed with atom content derived from item-7 scope_guidance rather than a dedicated atom-design dispatch; item 29 is the paired test-authoring follow-up that should include: (a) a focused 3-evaluator hardening review on REQ-SRC-0048 behavior semantics (especially genre_dispute tie-break routing — that's a novel contract surface crossing source→synthesis boundary and deserves scholarly defensibility review), (b) test fixtures exercising the six ACs with real Arabic sources, (c) implementation code in `src/deliberation.py` or a new `src/override_queue.py` module that realizes the queueing semantics. Depends on item 7 closure landing (DONE 2026-04-23 `08cc94633`).

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
