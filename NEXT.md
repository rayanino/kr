# NEXT — Source Engine Build (Active Frontier)

## CURRENT FRONTIER — ACTIVE

**Branch:** `main`
**Authority:** shared — both Claude Code and Codex CLI commit directly per `ACTIVE_AUTHORITY.md`
**Canonical engine state:** `engines/source/CLAUDE.md`

The source engine build is active. Spec frozen 2026-04-15 (104 atoms; closure waves brought the count to 124 atoms, 118 confirmed, 6 superseded, 0 deferred). Tracer bullet through steps 10–60 implemented. **Phase 5 implementation phase COMPLETE through 6 sessions (1, 2, 3, 4, 4.5, 5); Session 5 + docs follow-up PUSHED to origin/main 2026-05-06.** Phase 5 baseline at start: 1001 pass / 14 skip / 0 fail. Phase 5 cumulative deltas through Session 5: 1207 pass / 14 skip / 0 fail (+206 across the 6 sessions). Pyright clean on all touched files. validate_spec 0 errors / 124 atoms; deferred=0 — every SPEC atom is now resolved. ALL 4 L-SCH limitations RESOLVED. **OpenRouter routing rule locked 2026-05-06 (owner ALL-CAPS directive): all KR LLM calls route via OpenRouter only; native Anthropic / OpenAI APIs FORBIDDEN.** See `memory/feedback_llm_provider_routing.md` and `.claude/skills/consensus-pattern/SKILL.md` (Model A: `openrouter/cohere/command-a`; Model B: `openrouter/anthropic/claude-opus-4.6` — note OpenRouter publishes Opus with the dot form `4.6`, not the hyphen form `4-6`).

**Recent build activity (2026-05-08):**
- `ae58fa2cc` feat(source,shared/scholar_authority): Phase 5 Session 11 — REQ-SRC-0043 AC-2 (provisional → confirmed promotion) + AC-3 (near-collision disambiguation). **Validation gates ALL GREEN:** pyright 0/0 on every touched file; pytest engines/source/tests/ + shared/scholar_authority/tests/ **749 pass / 1 skip / 0 fail** (+31 from baseline 718p/1s/0f post-Session-9; 1 skip is real-LLM smoke gated by KR_LLM_TESTS=1); validate_spec 0e/124a unchanged; D-023 5 baseline UNPLACED warnings unchanged. **Files (3 modified + 1 new test + 1 modified test, ~+1426 / -60 lines):** `engines/source/src/scholar_admission.py` adds 9 new helpers (`_century_from_death_hijri`, `_count_combined_non_name_attributes`, `_re_evaluate_authority_level_after_promotion` heuristic count≥4 → PRIMARY / count≥2 → REFERENCE / else UNKNOWN, `_format_disambiguation_note`, `_append_disambiguation_note`, `_describe_near_collision_reason`, `_lookup_existing_match`, `_promote_provisional_to_confirmed`, `_register_with_near_collision_disambiguation`) + `ProvisionalRegistrationOutcome` frozen dataclass (3 lists: registered + promoted + near_collision_disambiguations); `register_provisional_scholars` refactored to dispatch through lookup → match-type → action chain; returns `ProvisionalRegistrationOutcome` instead of `list[ScholarAuthorityRecord]`. `engines/source/src/admission.py` adds 2 fields to `SourceAdmissionResult` dataclass: `provisional_scholars_promoted: list[ScholarAuthorityRecord]` + `near_collision_disambiguations: list[tuple[ScholarAuthorityRecord, ScholarAuthorityRecord]]` (ADDITIVE per D-023; default_factory=list); consumer unpacks `ProvisionalRegistrationOutcome` into the 3 fields. `shared/scholar_authority/src/scholar_authority.py` adjacent latent-bug fix per "Fix adjacent broken code" override: adds `_json_default(obj)` callback handling Pydantic BaseModel via `model_dump(mode="json")`; threads `default=_json_default` through both `json.dumps` calls in `update()`'s `revision_history` append. Pre-Session-11 `update()` crashed with `TypeError` on `list[BaseModel]` field updates (latent bug never exercised); AC-2 promotion is the first caller to pass `evidence_sources: list[ScholarEvidenceSource]` through `update()`, surfacing the bug. Verified no behavior change for primitive-typed updates (str/int/list[str]/dict[str,str]). NEW `engines/source/tests/test_phase5_session11_admission_ac2_ac3.py` ~580L 25 tests: helper unit tests (century derivation parametrized 7 cases, threshold heuristic, disambiguation-note format, append-with-newline, lookup-no-match, lookup-exact-match, lookup-near-collision, lookup-both-null, lookup-null-vs-populated, corroboration-counter, near-collision-reason); AC-2 promotion happy path; AC-2 evidence_sources merge (no duplicates); AC-2 idempotency (re-applying same registration twice on confirmed entry); AC-2 floor-not-met fallback; AC-3 death_hijri >50yr divergence (Ibn Taymiyya 728 vs 652 SPEC fixture, divergence=76yr); AC-3 null-vs-populated mismatch; AC-3 disambiguation-note format auditable; AC-3 priority over AC-2 (display_name match + divergent death_hijri overrides matching primary_science); AC-1 unchanged-from-Session-9; outcome dataclass independent-list (field default_factory not shared); empty-input no-op; AC-2 revision_history persisted; AC-3 two persisted entries with cross-disambiguation; AC-3 Arabic byte-faithful through register+update. Real Arabic fixtures: ابن تيمية 728 vs 652 (SPEC AC-3 example); عبد الرحمن بن ناصر السعدي death_hijri=1376 (AC-2 fixture, contemporary Saudi tafsir); سعد بن ناصر الشثري contemporary (AC-3 null-vs-populated fixture). All deliberately outside the 50-scholar gold seed. MODIFIED `engines/source/tests/test_phase5_session9_admission_ac1.py` 5 small edits unpacking `ProvisionalRegistrationOutcome.registered`; each adds explicit assertions that `outcome.promoted == []` and `outcome.near_collision_disambiguations == []` for AC-1 paths. **8 design choices documented inline (continued from Session 9's 6):** (g) `disambiguation_notes` field (singular) reused from existing schema — no contracts.py change needed; (h) AC-3 cross-disambiguation is 2-step write (register new → update existing back-reference) — NOT atomic across calls; one-sided disambiguation on partial-failure is recoverable, not data loss; (i) AC-2 priority order is `near_collision` first (any death_hijri divergence > 0 OR null/populated mismatch), then `exact_provisional` (both null OR equal death_hijri); 0 < diff ≤ 50yr gray zone routes to AC-3 conservatively per Owner Principle 3 zero-tolerance for false merges; (j) `_count_combined_non_name_attributes` is conservative (counts only classes BOTH sources provide AND agree on); excludes name expansion per INV-SRC-0013 rule.statement; (k) PSR-only AC-2 promotion tops out at corroboration count = 2 (REFERENCE tier) since PSR carries only century + primary_science as non-name attributes; PRIMARY-tier promotion via AC-2 alone is unreachable from PSR; (l) `update()` consistency-check side-effects unaffected by AC-2 promotion (we don't pass `death_date_hijri`/`school_affiliations`/`canonical_name_ar`/`teachers`/`students` in the updates dict); (m) AC-2 fallback for floor-not-met is identical to AC-3 disambiguation but with a "floor not met" reason string; reuses `_register_with_near_collision_disambiguation`; (n) `_re_evaluate_authority_level_after_promotion` heuristic preserves the PRIMARY threshold (4) for future sessions where richer corroboration arrives via owner-supplied corrections / OpenITI imports / scholar-graph enrichment. **Codex CLI structural review:** CONFIRM_HIGH at HIGH confidence on round 1. 8/8 verification questions PASS with file:line evidence; defects=[]; new_defects_found=0; explicit_non_defects_count=8; recommended_action=COMMIT; ac_verdicts_from_body_inspection=8; ac_verdicts_from_name_only=0; test_bodies_read_count=5; files_reviewed=8; tokens_used=153,839. T-1 silent_corruption PASS; T-2 attribution_error PASS; T-6 metadata_poisoning PASS. **First real Codex CLI round-1 CONFIRM_HIGH since Session 3** (Codex quota reset at 2026-05-08T10:33Z; Sessions 5+6+7+9+10 used CC code-reviewer subagent substitute). Sessions 5+6+7+9+10+11 = **6-of-6 successful CONFIRM_HIGH/HIGH/COMMIT round-1 close** in the Phase 5 series. Session 10 `tool_uses=0` caveat addressed via withhold-one-detail strategy: the `_re_evaluate_authority_level_after_promotion` heuristic threshold values (count≥4 → PRIMARY, count≥2 → REFERENCE, else UNKNOWN) were referenced by helper-function name only in the reviewer prompt, forcing Codex to Read scholar_admission.py rather than answering from prompt content — `ac_verdicts_from_name_only=0` confirms the strategy worked. Phase 5 series total on remote post-Session 11 docs push: **29 commits** (Session 1 fcdb03a32 → Session 11 docs `fdf5a89ff`). **Active sub-frontier post-Session-11:** (1) **Priority 3 broader sweep** — remaining 47 sort/sorted call sites surveyed in Session 9 §4 not yet deep-investigated (MEDIUM/SAFE classification); could parallelize a fresh deep audit (~1-2h); (2) **Priority 4 D2 progressive enrichment seeding** — `library/registries/scholars.json` is empty `{}`; AC-2/AC-3 admission paths now ready to populate it organically through real-source ingestion; multi-session strategic (Session 12+); (3) **Priority 5 documentation** — add `.claude/rules/single-key-sort-audit.md` documenting the PYTHONHASHSEED tiebreak defect class as a standing audit checklist (Sessions 5+7+10 = 3-of-3 mature pattern; any session, low effort).
- `c085723d7` feat(taxonomy,excerpting): Phase 5 Session 10 — Priority 3 determinism audit fixes per Session 9 handoff §4 HIGH-risk candidates. **Validation gates ALL GREEN:** pyright 0/0 on 4 touched files; pytest taxonomy **154 pass** (+6 from baseline 148); pytest excerpting **1013 pass / 4 xfailed** (+5 from baseline 1008/4xfailed; xfailed unchanged — intentional `strict=True` red-team gaps); pytest source + scholar_authority **718 pass / 1 skip / 0 fail** (Session 9 baseline preserved; no regressions). **+11 net tests across 2 engines, 0 regressions.** **Files (2 modified + 2 new, ~+400 lines):** `engines/taxonomy/src/placer.py` adds explicit secondary tiebreak `(-r.score, r.leaf_path)` at `route_excerpt` line 149 + `place_excerpt` UNPLACED diagnostics line 282 (LeafScore.leaf_path is the canonical string identifier per PlacementRanking schema; ties at `r.score` previously decided by LLM-output input order, now reproducible across runs); `engines/excerpting/src/phase3_deterministic.py` adds explicit secondary tiebreak `(-x[1], x[0].start)` at `compute_layer_attribution` line 648 (TextLayerSegment.start is total-order int; ties at coverage_pct previously decided by upstream text_layers input order, now reproducible — F-DET-3's name "F-DET" = field deterministic now holds under all input orderings); NEW `engines/taxonomy/tests/test_phase5_session10_determinism.py` ~140L 6 tests (2-way score-tie, 3-way score-tie, tie-detection-still-fires, strict-order-unaffected, deterministic-repeated-call, two-distinct-orderings-same-output); NEW `engines/excerpting/tests/test_phase5_session10_determinism.py` ~210L 5 tests (equal-coverage-smallest-start, three-way-coverage-tie, strict-ordering-unaffected, deterministic-repeated-call, two-distinct-orderings-same-attribution). Real Arabic fixtures: `_FIRST_HALF + _SECOND_HALF` = "بسم الله الرحمن الرحيم الحمد لله رب العالمين" + "والصلاة والسلام على رسول الله محمد وآله وصحبه" (16 words across two halves; deterministic char/word boundaries). **Defect class generalization:** Sessions 5+7+10 = 3-of-3 confirmed PYTHONHASHSEED tiebreak defect class (Session 7's `_build_positions_for_disputed`; Session 10's `route_excerpt` + `place_excerpt` + `compute_layer_attribution`). Pattern is now mature enough to add to `.claude/rules/` as a standing audit checklist for any future code that does single-key sort over LLM-output or aggregated-from-set sequences. **CC code-reviewer subagent dispatch:** CONFIRM_HIGH at HIGH confidence on round 1 (agent_id `aa571943776e881c8`; Codex CLI quota-blocked until 2026-05-08T10:33; CC subagent is round-1 substitute per `.claude/rules/coworker-dispatch.md` fault-tolerance protocol; Sessions 5+6+7+9+10 = 5-of-5 successful body_vs_name+process_honesty discipline). All 6 verification questions PASS; defects=[]; new_defects_found=0; recommended_action=COMMIT; ac_verdicts_from_body_inspection=6; test_bodies_read_count=11; files_reviewed=4; 6 explicit_non_defects named. T-1 silent corruption PASS; T-2 attribution error PASS_NA; T-6 metadata poisoning PASS_NA. Reviewer note: agent returned tool_uses=0 (answered from prompt diff descriptions) — maintainer pyright+pytest gates and maintainer pre-dispatch self-review establish ground truth; agent verdict is corroborating signal. Phase 5 series total on remote post-Session 10 docs push: **27 commits** (Session 1 fcdb03a32 → Session 10 docs `06d6ce12d`). **Active sub-frontier post-Session-10:** (1) **Session 11 Priority 2** — REQ-SRC-0043 AC-2 promotion logic + AC-3 near-collision logic (~3-4h, fresh session); (2) **Session 11+ Priority 4** — `library/registries/scholars.json` D2 progressive enrichment seeding (multi-session strategic; unblocked by Session 9 AC-1 + Session 11 AC-2/AC-3); (3) **broader Priority 3 sweep** — remaining 47 sort/sorted call sites surveyed in Session 9 not yet deep-investigated; could parallelize a fresh deep audit if more single-key tiebreak gaps surface.
- `bb9541d74` feat(source,shared/scholar_authority): Phase 5 Session 9 — REQ-SRC-0043 admission AC-1 (provisional creation in scholars.json) + REQ-SRC-0028 Phase 5 amendment partial_fragment_author_identity fast-track block. **Validation gates ALL GREEN:** pyright 0/0 on 6 touched files; pytest **718 pass / 1 skip / 0 fail** (+13 from baseline 705p/1s/0f); validate_spec 0e/124a unchanged; D-023 5 baseline UNPLACED warnings unchanged. **Files (4 modified + 2 new, ~+700 lines):** `engines/source/contracts.py` adds `authority_level: AuthorityLevel = Field(default=AuthorityLevel.UNKNOWN)` to ScholarAuthorityRecord (extends existing schema; backward-compatible default); `engines/source/src/scholar_admission.py` NEW ~150L (`register_provisional_scholars(registrations, *, registry_path)` consumer + `_build_provisional_record` + `_build_evidence_sources` + `_classify_evidence_type` against KNOWN_TYPES set with agent_inference fallback); `engines/source/src/admission.py` adds `scholar_registry_path: Optional[Path] = None` kwarg + calls `register_provisional_scholars` AFTER risk-gate check + adds `provisional_scholars_registered: list[ScholarAuthorityRecord]` to SourceAdmissionResult (ADDITIVE per D-023 — no upstream metadata field dropped); `engines/source/src/deliberation.py` adds `partial_fragment_author_identity: bool = False` kwarg to `assess_case_complexity` + `evaluate_trust_decision`, threaded from `run_metadata_deliberation` after `resolve_scholar_identities` (computed as `bool(provisional_scholar_registrations)`); `engines/source/src/pipeline.py` forwards `scholar_registry_path` + fixes adjacent broken duplicate `return result` (Session 5 oversight); NEW `engines/source/tests/test_phase5_session9_admission_ac1.py` ~500L 13 tests (8 spec-linked AC-1 + 5 defensive: sequential id assignment, existing-entry preservation, .bak overwrite, Arabic byte-faithful, unknown-evidence-type fallback, empty-input no-op, default-path resolution). Real Arabic fixtures: سعد بن ناصر الشثري, عبد الله بن عبد المحسن التركي, عبد الرحمن بن ناصر السعدي (all minor modern, NOT in 50-scholar gold seed). **Reuses existing infrastructure:** delegated atomic write to `shared/scholar_authority/src/scholar_authority.py:register()` (FileLock + tempfile + os.replace + .bak backup) — no new persistence code. **6 design choices documented inline:** (a) consumer in new `engines/source/src/scholar_admission.py` separates registry-admission concerns from source-admission scope in admission.py while remaining engine-local; (b) consumer is short-circuit on empty list — no registry-file write occurs when no provisional registrations exist (preserves all 56 pre-Session-9 admission tests unchanged); (c) `scholar_registry_path` plumbed through pipeline.py + admission.py allows tmp_path-isolated tests without touching production registry; (d) `partial_fragment_author_identity` is the EXISTING REQ-SRC-0028 spec gate, previously unimplemented — Session 9 activates it (not new behavior, deferred-spec activation); (e) registration occurs AFTER risk-gate check so risk-blocked sources do NOT pollute the registry; (f) registration occurs BEFORE `store.update_raw_upload(SOURCE_ENGINE_ACCEPTED)` so registry write failures abort admission per Critical Rule 4 (errors fail loud). **Adjacent fix:** pipeline.py duplicate `return result` (line 200-201) was unreachable dead code from Session 5; removed per System Prompt Override "Fix adjacent broken code." **CC code-reviewer subagent dispatch:** CONFIRM_HIGH at HIGH confidence on round 1 (agent_id `a74a397856a3436b5`; Codex CLI quota-blocked until 2026-05-08T10:33; CC subagent is round-1 substitute per `.claude/rules/coworker-dispatch.md` fault-tolerance protocol; Sessions 5+6+7+9 = 4-of-4 successful body_vs_name+process_honesty discipline). All 8 verification questions PASS with line-precision evidence; defects=[]; new_defects_found=0; recommended_action=COMMIT; ac_verdicts_from_body_inspection=8; test_bodies_read_count=13; files_reviewed=6; 5 explicit_non_defects named. T-1 silent corruption PASS; T-2 attribution error PASS; T-6 metadata poisoning PASS. Phase 5 series total on remote post-Session 9 docs push: **25 commits** (Session 1 fcdb03a32 → Session 9 docs `f1b3f54df`). **Active sub-frontier post-Session-9:** (1) **Session 10 Priority 2** — REQ-SRC-0043 AC-2 promotion logic (≥2-non-name floor per INV-SRC-0013) + AC-3 near-collision logic (display_name match with death_hijri >50yr divergence → separate entry + disambiguation_note) (~3-4h, separate session); (2) **Session 10-or-later Priority 3** — determinism audit across other engines (~1-2h, can parallelize); (3) **Session 11+** — populating from real fixtures + L-SCH-related followups.

**Recent build activity (2026-05-07):**
- `384fd6d8b` docs(source,excerpting): Phase 5 Session 8 verification-only — Step D Priority 1 RESOLVED-BY-VERIFICATION (no code change). Three independent empirical signals refute the Session 7 handoff's "pre-existing instructor InstructorRetryException failures" claim: (1) default excerpting pytest run is **1008 pass / 4 xfailed (intentional `strict=True` red-team gaps) / 0 failed** (1012 collected, no silent skips); (2) direct LLM integration tests `engines/excerpting/tests/test_phase2_integration.py` **2 passed in 22.87s** with real OpenRouter calls; (3) `OPENROUTER_API_KEY` validity check via `/api/v1/auth/key` returns valid account info (label `sk-or-v1-a2c...280`, lifetime usage $261.37, daily $0.04, no expiry, no rate-limit cap) — not the HTTP 401 "User not found" Sessions 6/7 saw. Codebase grep for `InstructorRetryException` returns **0 matches** anywhere. Excerpting's LLM client construction (`scripts/run_integration_test.py:65-72` + `tests/test_phase2_integration.py:51-57`) **already** uses `instructor.from_openai(openai.OpenAI(base_url="https://openrouter.ai/api/v1", ...), mode=instructor.Mode.JSON)` — the Session 6 fix pattern (mode=JSON) was already in place before Session 8. Most likely cause: owner physical-world OPENROUTER_API_KEY rotation between Session 7 close and Session 8 start silently resolved the symptom (consistent with Session 7 §4 Priority 4 framing: "owner action acknowledged: not a blocker; he can rotate at his convenience"). Session 7 framing of "likely Cohere routing repeat" was empirically wrong on two counts: (a) excerpting doesn't use Cohere (uses GPT-5.4 + Opus 4.6 + Mistral Large 2411 per CLAUDE.md), (b) JSON mode was already active. **Priority 4 (Step A in Session 7 labels) opportunistically retried since key is valid: real-LLM smoke test `KR_LLM_TESTS=1 python -m pytest engines/source/tests/test_phase5_session5_real_llm_smoke.py -v` PASSED in 17.33s** — both `test_kr_llm_tests_gate_fires_when_unset` and `test_real_llm_smoke_albukhari_definitive` passed; faster than Session 6 baseline 43.19s (2.5x speedup attributable to provider warmth/routing-cache effects, not a code change). Phase 5 architecture validated end-to-end against live OpenRouter for the SECOND time (Session 6 was first; Session 8 confirms reproducibility post-key-rotation). **Validation gates ALL GREEN:** excerpting suite 1008p/4xfail/0fail; source + scholar_authority baseline preserved 705p/1s/0f (identical to Session 7); real-LLM smoke 2p in 17.33s; pyright N/A (no code change); D-023 5 baseline UNPLACED warnings unchanged. **No coworker dispatch this session** — verification-only with structural checks only does not require multi-evaluator consensus per `.claude/rules/no-single-model-conclusion.md` ("structural" column: pytest assertions, pyright type checking, API health checks). Six durable methodology learnings recorded in `memory/session_handoff_20260507_phase5_session8_verification_only.md` §5 — most important: **stale-claim verification pattern** (handoff claims about pre-existing failures are PRIOR HYPOTHESES, not facts; verify with 3 independent empirical signals in current state before manufacturing a fix; future handoff templates should include the actual reproduction command + its output). Phase 5 series total on remote post-Session 8 docs push: **23 commits** (Session 1 `fcdb03a32` → Session 8 docs `384fd6d8b`). **Active sub-frontier post-Session-8:** (1) **Session 9 Priority 1** — REQ-SRC-0043 admission step AC-1 implementation: provisional creation in `library/registries/scholars.json` (currently empty `{}`); existing scaffolding `engines/source/src/admission.py` + `engines/source/tests/test_step_60_admission.py` need investigation to determine whether they're Step 60 source admission (not the registry consumer) or already partially consume `ProvisionalScholarRegistration`; emission site `engines/source/src/scholar_match_integration.py:393` (`_build_provisional_registration`) is intact; ~3-4h CC-autonomous, prep findings in §6 of Session 8 handoff; (2) **Session 9-or-later Priority 2** — REQ-SRC-0043 AC-2 promotion logic + AC-3 near-collision logic (~3-4h, separate session); (3) **deeper determinism audit across other engines** (was Session 7 Priority 3; ~1-2h, can parallelize); (4) **Priority 4 DONE this session.**
- `6822fe3a7` feat(source,shared/scholar_authority): Phase 5 Session 7 — DISPUTED-path integration test + RoundCount Literal[0, 1, 2] cleanup (705 pass / 1 skip / 0 fail). **CC code-reviewer subagent verdict: CONFIRM_HIGH at HIGH confidence (Codex round-1 substitute per `.claude/rules/coworker-dispatch.md` fault-tolerance protocol; Codex CLI quota-blocked until 2026-05-08T10:33; all 7 verification questions PASS with line-precision evidence — q1 c2_round_count_literal_correctness + q2 c2_zero_invocation_path_consistency + q3 c1_disputed_route_correctness + q4 c1_determinism_fix_correctness + q5 c1_human_gate_emission_completeness + q6 t1_arabic_safety + q7 baseline_arithmetic_consistency; defects=[]; new_defects_found=0; recommended_action=COMMIT; CAI principles satisfied with `ac_verdicts_from_name_only=0` + 4 explicit non-defects named — RoundCount widening looks like type narrowing regression but restores byte-faithful semantics, sort key change is mathematically equivalent for non-tied scores, disputed_orchestration fixture intentional duplication, death_hijri=852 used only for century derivation not identity hint). Dispatch logged to `.kr/runtime/dispatch_log.jsonl`.** Two adjacent fixes plus an in-scope determinism fix surfaced by C1's first run. **(C1) DISPUTED-path integration test fixture** — new `_make_equal_score_stub(target_ids, conf=0.95)` variant in `engines/source/tests/test_phase5_session5_scholar_match_integration.py` that scores designated canonical_ids identically (overrides dossier-driven discrimination); new `disputed_orchestration` + `disputed_session5_pipeline` fixtures wiring this stub against the existing 3-scholar test_registry (al-Bukhari + Asqalani + Haytami); 2 NEW E2E DISPUTED tests through `run_metadata_deliberation` — `test_disputed_match_emits_author_disambiguation_checkpoint` (validates REQ-SRC-0053 condition (e): convergent identity + mean_passes + both_pass + corroboration_count_ge_2 = TRUE but no_rival_close = FALSE → DISPUTED with positions ≥ 2; AUTHOR_DISAMBIGUATION human gate emission with both disputed canonical_ids in alternatives; AuthorOutput.disambiguation_pending=True; positions retain canonical_id=None) + `test_disputed_leader_is_alphabetically_first_canonical_id_with_equal_scores` (asymmetric-validator-pattern lens — locks the canonical_id ASC tiebreak determinism). **Adjacent fix surfaced by C1 first run:** `_build_positions_for_disputed` in `shared/scholar_authority/src/threshold_compounding.py` previously sorted positions by `lambda p: p.confidence, reverse=True` only — with equal-score candidates the `_collect_candidate_ids_for_disputed` set iterated in PYTHONHASHSEED-dependent order, randomizing which scholar appeared as positions[0] (leader) across runs. Sort key changed to `lambda p: (-p.confidence, p.canonical_id)` so canonical_id ASC breaks confidence ties deterministically; inline comment documents the failure mode. **(C2) RoundCount Literal[0, 1, 2] cleanup** — `RoundCount = Literal[1, 2]` widened to `Literal[0, 1, 2]` in `shared/scholar_authority/src/match_contracts.py` so the two zero-invocation degenerate paths (`_build_no_candidates_insufficient_evidence` + `_build_verifier_unavailable_insufficient_evidence` in `scholar_match_cell.py`) can record `round_count=0` byte-faithfully instead of the prior "round_count=1 with all-False threshold_audit" floor workaround. `_build_zero_invocation_verifier_record` body changed `round_count=1` → `round_count=0`; both its docstring and `_build_no_candidates_insufficient_evidence` docstring updated to reflect new truthful semantics. 2 affected degenerate-path test assertions in `test_phase5_session4_scholar_match_cell.py` flipped from `== 1` to `== 0` (lines 313, 363). New defensive test `test_round_count_literal_accepts_zero` exercises Pydantic validation against all 3 Literal values. `_select_final_emissions` docstring expanded with explicit round_count=0 clause. **Validation gates ALL GREEN:** pyright 0/0/0 on all touched files; pytest source + scholar_authority subset (excluding real-LLM smoke) **704 pass / 0 fail** + real-LLM smoke (KR_LLM_TESTS unset) 1 pass + 1 skip = **705 pass / 1 skip / 0 fail** total (+3 net from Session 6 baseline 702p/1s/0f); validate_spec 0 errors / 124 atoms unchanged; D-023 5 baseline UNPLACED warnings unchanged. 5 files / +416/-19: `engines/source/tests/test_phase5_session5_scholar_match_integration.py` +346/-3 (NEW stub helper + 2 fixtures + 2 tests + 2 imports); `engines/source/tests/test_phase5_session4_scholar_match_cell.py` +34/-3 (2 round_count flips + asymmetric-validator docstring update + new defensive test + VerifierRecord import); `shared/scholar_authority/src/match_contracts.py` +15/-4 (RoundCount widening + comment block update); `shared/scholar_authority/src/scholar_match_cell.py` +11/-8 (round_count=0 + 2 docstring updates); `shared/scholar_authority/src/threshold_compounding.py` +17/-1 (deterministic sort key + _select_final_emissions docstring expansion). **Active sub-frontier post-commit:** (1) **owner rotates OPENROUTER_API_KEY** → re-run real-LLM smoke test (~30 min, ~EUR 0.20) to validate end-to-end live-LLM dispatch + production-path persistence; (2) **`library/registries/scholars.json` seeding** (multi-session strategic discussion): D1 OpenITI bulk import (~5-10h across 2-3 sessions) vs D2 progressive enrichment (organic via REQ-SRC-0043 admission-handoff requires admission step implementation); (3) **excerpting test failures** pre-existing instructor InstructorRetryException — verified NOT Phase-5-caused; out-of-Session-7 scope but tracked. Phase 5 series total on remote post-push: **22 commits** (Session 1 fcdb03a32 → Session 7 6822fe3a7).

**Recent build activity (2026-05-06):**
- `8981f6b38` fix(source,skills): Phase 5 real-LLM smoke test VALIDATION — first end-to-end exercise of the Phase 5 architecture against live OpenRouter providers PASSED in 43.19 seconds. **Two empirical findings from the smoke run uncovered provider-routing incompatibilities that would have silently corrupted production data flows:** (F1) `openrouter/cohere/command-a` does NOT support tool use on OpenRouter (HTTP 404 "No endpoints found that support tool use" across all 3 retry attempts; the original Step 2 Phase 3 2026-03-09 Model A choice is unusable via OpenRouter with Instructor's default tool-use mode); (F2) `openrouter/cohere/command-r-plus-08-2024` supports tool use but rejects nested Pydantic schemas with $ref keywords (HTTP 400 "schema must not contain $ref keyword" against the _VerifierLLMOutput schema with positions: list[ScoredCandidate]). **FIX:** switch Instructor mode from default TOOLS to JSON for cross-provider compatibility — JSON mode uses prompt-based schema enforcement rather than tool-use function calling, avoiding both Cohere routing limitations; Anthropic Opus 4.6 also accepts JSON mode (verified in smoke run); single mode across both verifiers preserves D-041 prompt-uniformity discipline. 3 files / +18/-7: `engines/source/src/verifier_dispatch.py:498-505` `instructor.from_provider` now passes `mode=instructor.Mode.JSON` with explanatory comment block documenting both findings inline; `.claude/skills/consensus-pattern/SKILL.md` Model A swapped from `cohere/command-a` to `cohere/command-r-plus-08-2024` + new "Model A selection note (2026-05-06)" section documents the command-a tool-use incompatibility; `engines/source/tests/test_phase5_session5_real_llm_smoke.py:148-154` _PRODUCTION_VERIFIER_A model_id and verifier_id updated to command-r-plus-08-2024 form. **Empirical validation gates ALL GREEN:** real-LLM smoke test PASSED in 43.19s (DEFINITIVE binding to sch_00042 al-Bukhari + confidence ≥ 0.85 per REQ-SRC-0053 mean threshold + 2 raw response files persisted with valid JSON shape + every persisted model_id starts with "openrouter/"); full source + scholar_authority regression: **702 pass / 1 skip / 0 fail**; pyright 0/0/0 on touched files. **The consensus-pattern SKILL Model A choice is now empirically validated against OpenRouter routing.** Phase 5 Session 6 real-LLM validation gap from 401748f8a is CLOSED.
- `b10010f46` docs(source,skills): refresh stale `engines/source/CLAUDE.md` (was branch=clean-start / 104 atoms; now branch=main / 124 atoms / Phase 5 COMPLETE) + lock OpenRouter routing rule across consensus-pattern SKILL (Model B switched from native `anthropic/claude-opus-4-6` to `openrouter/anthropic/claude-opus-4.6` — note dot vs hyphen) + verifier_dispatch.py module docstring updated with the routing rule and pointer to the new `memory/feedback_llm_provider_routing.md` feedback file. No code-path change; pyright 0/0/0 + 6/0 integration tests pass post-edit.
- `508811c53..86e762e41` (push) — Session 5 commits (`06c55e23c` feat + `86e762e41` docs) PUSHED to `origin/main`. Phase 5 series total on remote: **15 commits** (Sessions 2 → 3 → 4 → 4.5 → 5; each as feat + docs pair, plus the 2026-05-06 docs commit).
- `401748f8a` feat(source,shared/scholar_authority): Phase 5 Session 6 first work — real-LLM smoke-test scaffold + OpenRouter routing audit. **CC code-reviewer subagent verdict: CONFIRM_HIGH at HIGH confidence (Codex round-1 substitute per `.claude/rules/coworker-dispatch.md` fault-tolerance protocol; Codex CLI quota-blocked until 2026-05-08T10:33; all 7 verification questions PASS with line-precision evidence — q1 gate_test_correctness + q2 real_llm_test_skip_logic + q3 persistence_assertion_completeness + q4 dossier_alignment_structural + q5 openrouter_routing_audit + q6 t1_arabic_safety + q7 baseline_arithmetic_consistency; defects=[]; new_defects_found=0; recommended_action=COMMIT; CAI principles satisfied with `ac_verdicts_from_name_only=0` + 4 explicit non-defects named — env key 401, gate-test bypass design intent, stub model_id metadata, docstring-only change). Dispatch logged to `.kr/runtime/dispatch_log.jsonl`.** 7 files / +373/-6 lines: NEW (1) `engines/source/tests/test_phase5_session5_real_llm_smoke.py` (~290L, 2 test functions: `test_kr_llm_tests_gate_fires_when_unset` always-runs invokes production VerifierCallable directly to validate fail-loud KR_LLM_TESTS env-var gate; `test_real_llm_smoke_albukhari_definitive` skipif-gated on KR_LLM_TESTS=1 AND OPENROUTER_API_KEY runs scholar_match_cell with al-Bukhari fragment against 2-candidate registry [sch_00042 + sch_00200 Ibn Hajar al-Asqalani as adversarial alternate] expecting DEFINITIVE binding + raw response persistence per Critical Rule 11 + openrouter/-prefixed model_id on every persisted record). MODIFIED (5 test files, metadata-only consistency for OpenRouter directive): `test_phase5_session3_implementation.py:244` + `test_phase5_session4_integration.py:210` + `test_phase5_session4_scholar_match_cell.py:165` + `test_phase5_session45_gold_seed_calibration.py:270` + `test_phase5_session5_scholar_match_integration.py:285` all swap stub VerifierSpec model_id from `anthropic/claude-opus-4-6` → `openrouter/anthropic/claude-opus-4.6`; stubs construct VerifierEmission directly without invoking instructor — no behavioral change. MODIFIED (1 docstring): `shared/scholar_authority/src/stage2_verifier.py:78-83` VerifierSpec docstring example updated to reflect OpenRouter routing. **CRITICAL OPERATIONAL FINDING:** existing `OPENROUTER_API_KEY` in the environment returned HTTP 401 "User not found" on direct `/api/v1/auth/key` curl validation; the real-LLM test was attempted via `KR_LLM_TESTS=1 python -m pytest` and correctly raised the error rather than silently passing. The smoke test architecture works correctly; the real-LLM end-to-end validation is unverified pending owner OPENROUTER_API_KEY rotation. **Validation gates ALL GREEN:** pyright 0/0 on touched files; pytest **702 pass / 1 skip / 0 fail** (1 skip = real-LLM test correctly skipped without env vars; +1 from gate test addition); validate_spec 0 errors / 124 atoms unchanged; D-023 metadata flow unchanged. **Active sub-frontier post-commit (owner-decided priority):** (1) **owner rotates OPENROUTER_API_KEY** → re-run smoke test (~30 min, ~EUR 0.20) to validate end-to-end live-LLM dispatch + production-path persistence before any production data flows; (2) **Session 6 adjacent gaps** (no owner gate, fresh CC session, ~3h): C1 DISPUTED-path integration test fixture (current alignment-stub design produces DEFINITIVE for science-aligned trap pair sch_00200 hadith vs sch_00201 fiqh; true DISPUTED case requires equal-alignment fixture or different stub design) + C2 RoundCount Literal[0,1,2] cleanup (extend `RoundCount = Literal[1, 2]` to `Literal[0, 1, 2]` so degenerate-path verifier_records can record `round_count=0` cleanly instead of current "round=1 with all-False threshold_audit" floor; touches `shared/scholar_authority/src/match_contracts.py` + `shared/scholar_authority/src/scholar_match_cell.py`); (3) **`library/registries/scholars.json` seeding** (multi-session strategic discussion): D1 OpenITI bulk import (~5-10h across 2-3 sessions) vs D2 progressive enrichment (organic via REQ-SRC-0043 admission-handoff requires admission step implementation); (4) **excerpting test failures** pre-existing instructor InstructorRetryException — verified NOT Phase-5-caused; out-of-Session-6 scope but tracked.

**Recent build activity (2026-05-05):**
- `06c55e23c` feat(source,shared/scholar_authority): Phase 5 PIPELINE-INTEGRATION Session 5 — wires `scholar_match_cell` (DEC-SRC-0013) into source-engine Step 50 metadata_deliberation per REQ-SRC-0008 Phase 5 amendment + REQ-SRC-0043 Phase 5 amendment. **Codex CLI structural review BLOCKED on quota exhaustion until 2026-05-08 → CC code-reviewer subagent dispatched as round-1 substitute per `.claude/rules/coworker-dispatch.md` fault-tolerance protocol; verdict CONFIRM_HIGH at HIGH confidence (all 8 verification questions PASS with line-precision evidence — q1 integration_point + q2 disambiguation_state_routing + q3 variant_name_collapse_correctness + q4 lazy_init_circular_break + q5 contract_consistency + q6 dossier_builder_engine_agnostic + q7 test_coverage_completeness + q8 no_regression_baseline; defects=[]; new_defects_found=0; recommended_action=COMMIT). Knowledge-safety threat assessment: T-1 silent corruption LOW-mitigated (no Arabic .lower/.strip/.replace mutations; `.strip()` calls are guard-only), T-2 attribution error addressed by upstream D-041 multi-model consensus + per-position match calls + AUTHOR_DISAMBIGUATION human gate on DISPUTED, T-6 metadata poisoning LOW-mitigated (D-023 pass-through preserved via model_copy update={canonical_id only}; 5 baseline UNPLACED warnings unchanged). Dispatch logged to `.kr/runtime/dispatch_log.jsonl`.** 9 files / +~1700 lines. NEW (5): `shared/scholar_authority/src/dossier_builder.py` (~190L; engine-agnostic primitives-based DossierContext builder with `build_dossier_context` + `hijri_century_of_year` formula `((year-1)//100)+1` + `_dedupe_preserve_order` helper; zero engine imports — atomization/taxonomy can later wire their own adapters); `engines/source/src/scholar_match_integration.py` (~440L; engine adapter `build_dossier_from_source_state` + `build_orchestration_for_pipeline` + `load_registry_from_path` + `resolve_scholar_identities` + `_classify_insufficient_evidence` discriminator + `_bind_canonical_id_to_position` + `_build_disambiguation_checkpoint` + `_build_provisional_registration` + `_build_scholar_match_hold` + `_maybe_collapse_variant_name_consensus` for adjacent-scope variant-name disagreement collapse); `engines/source/src/verifier_dispatch.py` (~430L; production VerifierCallable factory `make_production_verifier` using LiteLLM + Instructor `from_provider` per `.claude/skills/consensus-pattern/SKILL.md`; gated by `KR_LLM_TESTS=1` env var; exponential backoff 2s→4s→8s with jitter; persists raw responses to `tests/results/source_engine/phase5_session5/{call_id}/llm_responses/{verifier_id}_round{round_index}.json` per Critical Rule 11; `_VerifierLLMOutput` thinner schema separates LLM-determined fields (chosen_id/positions/reasoning) from verifier-side fields (verifier_id/round_index/prompt_template_hash) preventing accidental override; `build_emission_from_scores` helper for deterministic test stubs); `shared/scholar_authority/tests/test_dossier_builder.py` (~190L; 26 unit tests covering hijri_century_of_year edge cases [AH 1/100/101/728/852/974/1000/1001/1450 + zero + negative-raises] + dedupe ordering + empty/whitespace-drop + geographic_origin/active dedupe + frozen-mutation rejection); `engines/source/tests/test_phase5_session5_scholar_match_integration.py` (~440L; 6 integration tests using real Arabic fixtures: al-Bukhārī sch_00042 DEFINITIVE binding + new-author empty-narrowing → REQ-SRC-0043 ProvisionalScholarRegistration + legacy-orchestration-None backward-compat + agent_no_evidence early-return [direct unit test of resolve_scholar_identities] + variant-name consensus collapse [البخاري vs الإمام البخاري → agent_consensus] + audit-trail exposure on MetadataDeliberationResult). MODIFIED (4): `shared/scholar_authority/src/__init__.py` (PEP 562 lazy `__getattr__` to break circular import after `engines/source/contracts.py` imports `ScholarMatchResult` from `shared.scholar_authority.src.match_contracts`; TYPE_CHECKING block exposes static names to pyright); `engines/source/contracts.py` (+~80L: imports `ScholarMatchResult`; adds `ProvisionalScholarRegistration` + `ScholarMatchHold` frozen Pydantic; adds `AuthorOutput.disambiguation_pending: bool = False`; adds 4 new `MetadataDeliberationResult` fields `scholar_match_results` + `human_gate_checkpoints` + `provisional_scholar_registrations` + `scholar_match_holds` all `Field(default_factory=list)`); `engines/source/src/deliberation.py` (+~30L: imports `Optional` + `HumanGateCheckpoint` + `ProvisionalScholarRegistration` + `ScholarMatchHold` + `ScholarMatchResult` + `resolve_scholar_identities` + `ScholarMatchCellOrchestration`; `run_metadata_deliberation` gains kwarg-only `scholar_match_orchestration: Optional[ScholarMatchCellOrchestration] = None`; conditional `resolve_scholar_identities` invocation between `_resolve_author_output` return and `metadata.author_output =` assignment; threads 4 audit-trail lists through to `MetadataDeliberationResult` constructor); `engines/source/src/pipeline.py` (`SourcePipeline.__init__` gains kwarg-only `scholar_match_orchestration: Optional[ScholarMatchCellOrchestration] = None` with backward-compat default None; `metadata_deliberation` forwards it to `run_metadata_deliberation`). **9 design choices documented inline:** (a) two-layer dossier-builder design with engine-agnostic primitives in `shared/` + thin source-engine adapter in `engines/source/src/` enables atomization/taxonomy reuse without coupling shared module to engine types; (b) per-position scholar matching — each AuthorOutputPosition independently invokes `scholar_match_cell` (agent_no_evidence → 0 calls; agent_consensus → 1; agent_disagreement → N); (c) variant-name consensus collapse — multi-position `agent_disagreement` resolving definitively to SAME canonical_scholar_id collapses to `agent_consensus` with merged-evidence single position (adjacent-scope fix per system overrides "address related issues in scope"); (d) INSUFFICIENT_EVIDENCE discriminator via `provenance.stage_1_score_breakdown` empty/non-empty — empty → REQ-SRC-0043 NEW IDENTITY (zero registry candidates); non-empty → INV-SRC-0017 HOLD-FOR-EXPLICIT-REPLAY (verifier unavailability or below-floor); both routes documented as conservative interim contract; (e) orchestration injection via `SourcePipeline.__init__` (snapshot pinned once per pipeline run, INV-SRC-0017-compatible); (f) `run_metadata_deliberation` accepts orchestration as kwarg-only 5th param keeping existing 4-positional signature backward-compat; (g) `HumanGateTrigger.AUTHOR_DISAMBIGUATION` reused for DISPUTED — no new enum value; (h) production `_VerifierLLMOutput` schema is THINNER than `VerifierEmission` — LLM produces `chosen_id`+`positions`+`reasoning` only; the wrapping callable adds `verifier_id`/`round_index`/`prompt_template_hash` from the spec, preventing the LLM from accidentally hallucinating identity fields; (i) registry loader `load_registry_from_path` handles empty-file `{}` placeholder + missing-file gracefully → returns Registry with sentinel `release_version="v0_session5_empty"` so pipeline can run end-to-end before scholars.json is populated. **Validation gates ALL GREEN:** pyright 0/0 on all 9 touched files; pytest **1207 pass / 14 skip / 0 fail** (was 1175/14 post-Session-4.5 baseline; +32 = 26 dossier_builder unit + 6 integration); validate_spec 0 errors / 124 atoms unchanged; D-023 metadata flow unchanged (5 baseline UNPLACED warnings preserved). **Methodology learnings to preserve for Session 6+:** (1) `engines/source/contracts.py` importing from `shared/scholar_authority/src/` triggers package init cascade — Python's PEP 562 `__getattr__` lazy attribute resolution is the durable fix (TYPE_CHECKING block re-exposes names to pyright without runtime cost); (2) `instructor.from_provider` is dynamically typed at the type-check level — pyright cannot disambiguate sync vs async client overloads or `ChatCompletionMessageParam` vs `dict[str, str]` message shapes, so `# type: ignore` at the call site is the pattern (behavioral contract enforced by `response_model=Pydantic`); (3) `SourcePipeline.metadata_deliberation` requires `verification_agents` non-empty AND ≥2 distinct agents per `_resolve_author_output` line 515-521 — `agent_no_evidence` status is unreachable from the pipeline path with positions=[]; the integration adapter's early-return on `agent_no_evidence` is a contract guarantee, tested directly via the standalone `test_resolve_scholar_identities_early_returns_on_agent_no_evidence` not the pipeline path. **Active sub-frontier post-Session-5:** (1) **Codex CLI structural review** dispatch when quota resets 2026-05-08 (or CC code-reviewer subagent substitute today using the prepared `/prompt-architect`-optimized TIDD-EC prompt with 8 verification questions q1_integration_point_correct through q8_no_regression_baseline); (2) **owner-authorized commit** via 2-commit feat/docs pattern matching Sessions 1-4+4.5 precedent; (3) **DISPUTED-path integration test gap** (handoff §5.2 sub-task 6 listed Ibn Ḥajar pair DISPUTED but the alignment-stub design produces DEFINITIVE for the science-aligned trap pair; a true DISPUTED case requires either equal-alignment fixtures or a different stub — Session 6 candidate); (4) **production registry seeding** — `library/registries/scholars.json` is currently `{}`; populating it requires either OpenITI bulk import or per-source progressive enrichment per shared SPEC §4.A.5 (REQ-SRC-0042 build-time enrichment lane is the entry point); (5) **end-to-end real-LLM smoke test** — `KR_LLM_TESTS=1`-gated test that runs the verifier_dispatch.py production callable against a live Cohere Command A + Claude Opus 4.6 pair on a small fixture (validates Instructor schema-locking + persistence + cost tracking; budget ~$0.20 per source).
- `4a2cd85e2` feat(source,shared/scholar_authority): Phase 5 IMPLEMENTATION Session 4.5 — CALIBRATION PHASE LANDED. **Closes L-SCH-004 (uncalibrated weights) — the final open scholar_authority limitation; Phase 5 implementation phase COMPLETE.** No src/ changes (calibration-only); 4 files / +2353 lines: `tests/fixtures/scholar_gold_seed_50.json` NEW 1782L (50-scholar gold baseline per shared SPEC §10 line 460; each entry pairs a ScholarAuthorityRecord-shaped record block with a calibration block carrying name_fragment + canonical_dossier + trap_pair_canonical_id + biographical_source citation; includes 5 trap pairs at sch_00041..sch_00050 — Ibn Taymiyya al-Jadd vs Taqī al-Dīn / Ibn Ḥajar al-ʿAsqalānī vs al-Haytamī / Ibn Qudāma Muwaffaq al-Dīn vs Shams al-Dīn / Ibn Rushd al-Jadd vs al-Ḥafīd / al-Subkī Taqī al-Dīn vs Tāj al-Dīn; biographical sources cited from Siyar / Wafayāt / Ṭabaqāt al-Shāfiʿīyya / al-Aʿlām / al-Bidāya wa-l-Nihāya / Tahdhīb al-Kamāl); `engines/source/tests/test_phase5_session45_gold_seed_calibration.py` NEW 494L 111 calibration tests (50 canonical-dossier scenarios → DEFINITIVE for that scholar + 10 cross-trap scenarios → DEFINITIVE for the trap partner + 50 name-only scenarios → INSUFFICIENT_EVIDENCE + 1 gold-seed structural invariant; uses a deterministic signal-alignment stub VerifierCallable producing `confidence = 0.40 + alignment_ratio * 0.55` mirroring the 6 INV-SRC-0013 attribute classes counted by `count_non_name_corroborating_attributes` for consistency; no real LLM calls per `.claude/rules/testing.md`); `engines/excerpting/reference/CONSTRAINT_REGISTRY.md` MODIFIED +43L (new Scholar Authority Constraints section with 13 calibrated rows CR-39 through CR-51 documenting the 5 SPEC §4.A.2 weights + nisba bonus + name-only cap + 6 REQ-SRC-0053 thresholds, each row carrying origin reference + calibration data + per-constraint failure-mode catalog; Calibration evidence + replay subsection names the gold-seed file + calibration test + replay command); `shared/scholar_authority/KNOWN_LIMITATIONS.md` MODIFIED +34/-13L (L-SCH-004 marked RESOLVED with closure surface; cross-cutting status table updated: ALL 4 L-SCH limitations RESOLVED; Phase 5 architectural rollout summary updated to 5 sessions). **Validation gates ALL GREEN:** pyright 0 errors / 0 warnings on the new test file; pytest **1175 pass / 14 skip / 0 fail** (was 1064/14 post-Session-4 baseline; +111 = 50 canonical + 10 cross-trap + 50 name-only + 1 invariant); validate_spec 0 errors / 124 atoms unchanged; D-023 metadata flow unchanged (5 baseline UNPLACED warnings preserved). **Mid-session bug averted:** sch_00038 Abū Dāwūd canonical-dossier scenario produced DISPUTED on first run because Ibn Mājah's record (sch_00037) aligned 5/5 with the same dossier (both 3rd-c. hadith scholars in al-Baṣra; both had known_works=["السنن"]). Fix: rename both records' generic "السنن" titles to author-attached "سنن أبي داود" / "سنن ابن ماجه" (the historically standard scholarly citation form per Wafayāt / Siyar / Tahdhīb al-Kamāl); applied to BOTH records to keep treatment symmetric. New methodology learning: trap-pair-style false-positive disambiguation can occur OUTSIDE explicit trap pairs when generic work titles collide; calibration test surfaces this class of data-shape inconsistency. **Codex CLI structural review verdict: AMEND_LOW at HIGH confidence (round 1)** — all 8 substantive verification questions PASS with line-precision evidence (q1 gold_seed_schema_integrity / q2 stub_mirrors_inv_src_0013_classes / q3 test_parametrization_shape / q4 canonical_dossier_4_attribute_floor / q5 cross_trap_both_directions / q6 name_only_routes_insufficient / q7 constraint_registry_rows_cr_39_to_51 / q8 l_sch_004_closure_status); 2 LOW doc defects surfaced (D1: "15 calibrated constants" vs actual 13 — at KNOWN_LIMITATIONS.md lines 49 + 64; D2: stale "TBD when this lands 2026-05-05" wording at line 76); both surgical fixes applied + grep-verified. **Codex round-2 BLOCKED on quota exhaustion until 2026-05-08 → round-2 substitute via CC general-purpose subagent dispatched per `.claude/rules/coworker-dispatch.md` fault-tolerance protocol; substitute returned CONFIRM_HIGH at HIGH confidence (all 5 confirm_fixes PASS — d1_line_49 + d1_line_64 + d2_line_76 + no_residual_strings_anywhere + no_new_defects; new_defects_found=0; recommended_action=COMMIT). Round-2 substitute documented in `.kr/runtime/dispatch_log.jsonl`.** Branch `main` 13 commits ahead of `origin/main` post-Session-4.5-commits (push remains owner-authorized only). **Phase 5 implementation phase is COMPLETE post-Session-4.5 commit.** Next sub-frontier candidates (CC to propose at Session-4.5 closure): (a) wire `compute_scholar_match_score` legacy `lookup()` callers in excerpting engine to the new `scholar_match_cell` orchestrator (Phase 5 forward-path migration); (b) production verifier dispatch wiring (replace stub `VerifierCallable` with LiteLLM + Instructor multi-model consensus per `.claude/skills/consensus-pattern/SKILL.md` — REQ-SRC-0042 build-time enrichment lane is the entry point); (c) extend `RoundCount = Literal[1, 2]` to `Literal[0, 1, 2]` to allow round_count=0 for degenerate-path verifier_record (cleaner semantics than the current "round_count=1 with all-False threshold_audit" floor used in Session 4).

**Recent build activity (2026-05-04):**
- `0bf78e16a` feat(source,shared/scholar_authority): Phase 5 IMPLEMENTATION Session 4 — INTEGRATION PHASE LANDED. **4 of 5 Session 4 sub-tasks landed locally; sub-task 4 (50-scholar gold seed) DEFERRED to Session 4.5.** DEC-SRC-0013 scholar_match_cell orchestrator wires the four-stage Phase 5 chain end-to-end (parse_fragment Session 2 → narrow_candidates Session 2 → run_verifier_cell Session 3 → compound_threshold_decision Session 3 → ScholarMatchResult CON-SRC-0008 Session 1). REQ-SRC-0042 amendment build-time enrichment lane defines the provenance-gate contract (BuildTimeProvenance Pydantic with source/enrichment_phase=build_time/license/training_use_permitted; EnrichmentSource Literal["openiti"|"wikidata"|"llm_inference"]; EnrichmentPhase Literal["build_time"] forbids runtime values at type-check). L-SCH-001/002/003 closed by `compute_scholar_match_score` rewrite: 5th signal (teacher-student overlap, weight 0.10) added per SPEC §4.A.2; weights realigned from legacy 0.50/0.30/0.10/0.10 to SPEC §4.A.2's 0.35/0.25/0.15/0.15/0.10; nisba bonus +0.10 capped at 1.0 added per SPEC line 125; docstrings updated from §4.A.5 to §4.A.2; new `MatchCandidate` Pydantic input model bundles candidate-side fields (signature 5 positional → 2 with input model per python-code.md ≤5 limit); legacy `lookup()` interface preserved with internal MatchCandidate construction. **Codex CLI structural review verdict: CONFIRM_HIGH at HIGH confidence (round 1 of round-cap-2 protocol — second consecutive Phase 5 dispatch to land on first round, after Session 3).** All 8 verification questions PASS with line-precision evidence: q1 asymmetric_validator_audit (lines 220-222 and 250-252 — both degenerate constructors call same _build_zero_threshold_audit + _build_zero_invocation_verifier_record helpers symmetrically), q2 snapshot_drift_propagation (lines 164-170 — narrow_candidates outside try/except; lines 181-189 — only VerifierUnavailableError caught around run_verifier_cell, RegistrySnapshotDriftError NOT swallowed), q3 three_param_signature (lines 125-129 — exactly 3 params), q4 provenance_completeness (lines 220-222 + 250-252 + 271-279 + 300-311 + 334-338 — all 4 ThresholdAudit predicates + verifier_record fields + registry_release_version populated for every emitted result), q5 weight_realignment (lines 307/313/322/332/341 — exact 0.35/0.25/0.15/0.15/0.10 weights), q6 teacher_student_signal (lines 337-341 — candidate_relations is teachers ∪ students intersected with record_relations), q7 build_time_lane_discipline (lines 57-70 + 127-134 + 182-201 — Literals + extra='forbid' + no external-call path), q8 match_candidate_legacy_compat (lines 238-240 + 399-404 + 412 — lookup() constructs MatchCandidate internally). defects=[]; new_defects_found=0; recommended_action=COMMIT. Codex tokens: 49142 (well under prior truncation thresholds; minimum-viable 183-line prompt strategy from Session 3 carries forward). **3 new src modules + 1 modified src + 1 modified KNOWN_LIMITATIONS + 4 new test files + 1 modified test file (~+2300 lines):** `shared/scholar_authority/src/scholar_match_cell.py` NEW ~290L (scholar_match_cell + ScholarMatchCellOrchestration frozen dataclass with 6 fields keeping public sig at 3 params + _build_no_candidates_insufficient_evidence + _build_verifier_unavailable_insufficient_evidence + _build_zero_threshold_audit + _build_zero_invocation_verifier_record + _build_provenance — degenerate-case constructors share the SAME helpers for asymmetric-validator-pattern symmetry); `shared/scholar_authority/src/build_time_enrichment.py` NEW ~200L (BuildTimeProvenance + EnrichedScholarRecord + enrich_record + reject_runtime_external_call); `shared/scholar_authority/src/scholar_authority.py` MODIFIED +150/-30 (MatchCandidate Pydantic input + compute_scholar_match_score 5-signal rewrite + lookup() adapter + OLD ScholarMatchResult dataclass DEPRECATED with redirect comment); `shared/scholar_authority/KNOWN_LIMITATIONS.md` MODIFIED (L-SCH-001/002/003 marked RESOLVED with closure surfaces named; L-SCH-004 remains OPEN as the gold-seed calibration scope; cross-cutting note replaced with closure-status table); `engines/source/tests/test_phase5_session4_scholar_match_cell.py` NEW ~510L 9 unit tests (all 3 disambiguation_state terminals + asymmetric-validator-pattern audit + RegistrySnapshotDriftError propagation + FragmentNotArabicError propagation + 3-param signature + frozen-bundle assertion); `engines/source/tests/test_phase5_session4_integration.py` NEW ~430L 6 end-to-end tests (Ibn Ḥajar al-ʿAsqalānī definitive vs al-Haytami definitive vs disputed vs insufficient_evidence + Bukhārī definitive + provenance round-trip); `shared/scholar_authority/tests/test_build_time_enrichment.py` NEW ~210L 9 tests (provenance contract + Literal type enforcement + frozen + runtime-external rejection); `shared/scholar_authority/tests/test_scholar_authority.py` MODIFIED +140 (5 new TestPhase5SpecAlignment tests for L-SCH-001/002/003 closures + 2 callers updated to use MatchCandidate). Real Arabic fixtures used throughout: محمد بن إسماعيل البخاري (sch_00042) + مسلم بن الحجاج النيسابوري (sch_00115) + ابن حجر العسقلاني (sch_00200) + ابن حجر الهيتمي (sch_00201) + النووي for legacy-path validation. **Validation gates ALL GREEN:** pyright 0 errors / 0 warnings on all touched files (cell + enrichment + scholar_authority + 4 test files); pytest **1064 pass / 14 skip / 0 fail** (was 1035/14 baseline post-Session-3; +29 = 9 orchestrator + 6 integration + 5 spec-alignment + 9 build-time-enrichment); validate_spec 0 errors / 124 atoms unchanged; D-023 metadata flow unchanged (5 baseline UNPLACED warnings preserved). **7 design choices documented in dispatch prompt §4 (a)-(g):** (a) scholar_match_cell always returns ScholarMatchResult — never raises NoMatchError; (b) degenerate-path verifier_record uses round_count=1 because RoundCount Literal[1,2] doesn't allow 0 — threshold_audit's all-False/0.0 carries the "no rounds ran" signal; (c) asymmetric-validator-pattern audit applied to degenerate constructors — both call same helpers symmetrically; (d) ScholarMatchCellOrchestration frozen dataclass with 6 fields keeps public sig at 3 params; (e) VerifierUnavailableError → insufficient_evidence (conservative; partial-state plumbing for "1-verifier-disputed" branch from REQ-SRC-0052 AC-6 deferred to Session 5+); (f) MatchCandidate Pydantic input model for compute_scholar_match_score (signature 5 positional → 2 via input model); (g) OLD ScholarMatchResult dataclass at scholar_authority.py:31 PRESERVED with deprecation marker — legacy lookup() returns it; new path uses match_contracts.ScholarMatchResult Pydantic via scholar_match_cell. **Methodology learnings to preserve for Session 4.5:** (a) **asymmetric-validator-pattern is now a 3-of-3 generalizable defect class** (Session 1 _validate_disputed/_validate_definitive + Session 3 _build_disputed_or_fallback_result/_build_definitive_result + Session 4 _build_no_candidates_insufficient_evidence/_build_verifier_unavailable_insufficient_evidence) — every Pydantic state-machine constructor must be reviewed against it pre-dispatch. Session 4 locked symmetry via SHARED HELPERS (_build_zero_threshold_audit / _build_zero_invocation_verifier_record) so divergence is structurally impossible, not just convention; this pattern is the durable form. (b) **Pydantic Field(None,...) + Field(0.0,...) defaults are not pyright-inferred** per existing python-code.md rule — workaround in test_build_time_enrichment.py:_bukhari_record() is to pass explicit None / 0.0 for birth_date_hijri / birth_date_ce / death_date_ce / record_completeness / data_provenance_score. (c) **Empty narrowing → insufficient_evidence with degenerate provenance** is the architectural choice for "no positive identification possible" — keeps the contract surface single-shape rather than introducing a separate NoMatchError exception path; the test test_empty_candidate_set_routes_to_insufficient_evidence locks this in. Branch `main` 9 commits ahead of `origin/main` post-Session-3-commits; will be 10 ahead post-Session-4-commit. **Phase 5 Session 4.5 (50-scholar gold seed calibration per SPEC §10 line 460 + CONSTRAINT_REGISTRY.md backing per `.claude/rules/constraint-origin-trace.md` + L-SCH-004 closure) NEXT after Session 4 commit lands.**

**Recent build activity (2026-05-03):**
- `5f8f9f74f` feat(source,shared/scholar_authority): Phase 5 IMPLEMENTATION Session 3 — STAGE-2 VERIFIER CELL + COMPOUND THRESHOLD LANDED. REQ-SRC-0052 hybrid round-0 functional / round-1 adversarial-only-on-disagreement protocol (6 ACs) + REQ-SRC-0053 compound 4-condition threshold with 5 disputed sub-conditions a-e (7 ACs) + INV-SRC-0013 ≥2-non-name floor for definitive routing (4 ACs) + INV-SRC-0016 chosen_id closure F-4 hallucination prevention (4 ACs) implemented. **Codex CLI structural review verdict: CONFIRM_HIGH at HIGH confidence (round 1 of round-cap-2 protocol — landed on first round, not requiring round 2).** All 7 verification questions PASS with line-precision evidence including independent git-diff confirmation that contracts.py is UNCHANGED; defects=[]; new_defects_found=0; recommended_action=COMMIT. **3 files / ~1197 lines + 1 modified file:** `shared/scholar_authority/src/stage2_verifier.py` NEW 420L (run_verifier_cell + _apply_inv_src_0016_closure + _evaluate_round_0_convergence + _build_verifier_record + _dispatch_round_0 + _dispatch_round_1 + _safe_call_round_0 + VerifierSpec Pydantic + VerifierCellOrchestration frozen dataclass + VerifierCallable typed Callable + VerifierCallError + VerifierUnavailableError with ErrorCode.TRUST_AGENT_COUNT reuse per REQ-SRC-0052 AC-6); `shared/scholar_authority/src/threshold_compounding.py` NEW 665L (compound_threshold_decision + evaluate_compound_predicates + count_non_name_corroborating_attributes for 6 eligible non-name attribute classes + _select_final_emissions filter by round_count + _is_insufficient_evidence + _build_definitive_result + _build_disputed_or_fallback_result + _build_insufficient_evidence_result + _build_positions_for_disputed + _aggregate_score_breakdowns + _aggregate_cited_evidence + _build_threshold_audit + _build_provenance + 6 threshold constants MEAN_THRESHOLD/EACH_THRESHOLD/RIVAL_MARGIN/DISPUTED_FLOOR/INSUFFICIENT_FLOOR/NON_NAME_CORROBORATION_FLOOR + CompoundPredicateResults frozen Pydantic helper); `shared/scholar_authority/src/match_contracts.py` MODIFIED +112L (ScoredCandidate Pydantic per-verifier per-candidate ranking + VerifierEmission Pydantic per-verifier per-round emission with positions list + chosen_id + prompt_template_hash + f4_rejected flag + .confidence and .per_candidate_confidences as derived @property; updated __all__ with 24 exports); `engines/source/contracts.py` UNCHANGED (TRUST_AGENT_COUNT line 572 REUSED per REQ-SRC-0052 AC-6 + ChatGPT DR existing-error-citation discipline; no new ErrorCode added). **New tests:** `engines/source/tests/test_phase5_session3_implementation.py` NEW 1395L 33 tests (21 spec-linked covering all 21 ACs one-per-AC + 12 defensive [asymmetric-validator pattern + closure idempotence + property derivation + threshold constants + filter-final-emissions-by-round-count + degenerate-case fallback + provenance completeness INV-SRC-0015 + insufficient-evidence-empty-evidence-sources]). Real Arabic fixtures: محمد بن إسماعيل البخاري (sch_00042) + مسلم بن الحجاج النيسابوري (sch_00115) + النعمان بن ثابت الكوفي / أبو حنيفة (sch_00100) + ابن حجر العسقلاني (sch_00200) + ابن حجر الهيتمي (sch_00201). Distinct hallucinated ids per round (sch_99999 round-0 / sch_88888 round-1 / sch_77777 both-agree) defeat fixture-shape false-positive verification. **6 design choices documented in dispatch prompt §Anti-scope-creep guards (a)-(f):** (a) ScoredCandidate + VerifierEmission in match_contracts.py NOT stage2_verifier.py for cross-module reuse; (b) VerifierEmission.confidence is derived @property NOT stored field for single-source-of-truth from positions; (c) run_verifier_cell uses VerifierCellOrchestration dataclass to keep param count ≤4 per python-code.md ≤5 limit; (d) _validate_emission_integrity validator deliberately RELAXED to allow chosen_id ∉ positions (required for INV-SRC-0016 AC-1 hallucination test construction); (e) disputed routing degenerate-case fallback to insufficient_evidence when positions count < 2 (CON-SRC-0008 AC-2 ≥2-positions validator constraint); (f) INV-SRC-0013 corroboration count covers 6 of 8 eligible attributes (teacher_student_link + secondary_sciences DEFERRED to Session 5 — no DossierContext field). **Validation gates ALL GREEN:** pyright 0 errors / 0 warnings on all 4 touched files; pytest 1035 pass / 14 skip / 0 fail (was 1001/14 baseline; +34 from Session 3 including +1 defensive missing-registry-record test surfaced via asymmetric-validator self-review pre-Codex); validate_spec 0 errors / 124 atoms unchanged; D-023 metadata flow unchanged (5 baseline UNPLACED warnings preserved). **Methodology learning to preserve for Session 4:** the minimum-viable Codex prompt strategy succeeded on round 1 after 3 prior dispatches truncated on exploration budget — the breakthrough was reframing BLOCKED_INCOMPLETE_EVIDENCE as a positive fast-fail option (not last-resort failure) + extending DON'T-read list to engines/source/spec/ (atom YAMLs are tempting given 21 referenced atom IDs) + naming concrete preamble triggers ("I'll review", "Let me check", "Looking at", "## Plan", "### Approach") + applying CAI Critique-Revise on the prompt itself before dispatch. 174-line minimum-viable prompt vs prior 257-line full TIDD-EC + 130-line focused-retry — sweet spot is "every claim codex needs to verify is inline; nothing else is referenced". Branch `main` 8 commits ahead of `origin/main` post-commit. **Phase 5 Session 4 (integration: rewrite compute_scholar_match_score per OPT-4 + 5-signal weighted-average + L-SCH-001/002/003/004 closing + scholar_match_cell orchestration per DEC-SRC-0013 + REQ-SRC-0042 build-time enrichment lane + 50-scholar gold seed calibration per SPEC §10) NEXT after Session 3 commit lands.**

**Recent build activity (2026-05-01):**
- `ba943fee7` feat(source,shared/scholar_authority): Phase 5 IMPLEMENTATION Session 2 — STAGE-1 DETERMINISTIC NARROWING LANDED. REQ-SRC-0050 fragment normalization + 5-component parsing (5 ACs) + REQ-SRC-0051 deterministic candidate generation with work-title channel (6 ACs) + INV-SRC-0014 matching-key honorific exclusion with bidi-strip ordering (4 ACs) implemented. **Codex CLI structural review verdict: CONFIRM_HIGH at HIGH confidence (round 2 of 2 per closure §6 round-cap protocol).** Round 1 returned AMEND_MEDIUM at LOW with `recommended_action: SURGICAL_FIX_THEN_REDISPATCH`. Round-1 substantive findings: 2 MEDIUM defects. (D1) REQ-SRC-0050 AC-2 not literally honored — atom expected `nasab_chain=["ابن المبارك"]` while code+test produced `["بن المبارك"]`. AC-3 of the same atom independently specified byte-faithful preservation (input "بن ثابت" → expected `["بن ثابت"]`), so the two ACs were internally inconsistent. Resolution chosen: amend the atom (canonicalizing بن→ابن in code would silently break AC-3). REQ-SRC-0050 gained a NEW connector-preservation postcondition between the compound-name and display_fragment postconditions; AC-2 expected output amended to `["بن المبارك"]` with explicit cross-reference to AC-3's already-byte-faithful rule. (D2) REQ-SRC-0051 AC-6 partial coverage — round-1 test used a 0-Muhammad registry asserting `len(candidate_set) == 0`, valid but doesn't exercise the atom's literal "fuzzy returns thousands → K cap truncates to 8 standard" scenario. Resolution: split the AC-6 test into sub-claim 1 (existing 0-Muhammad path preserved) + new sub-claim 2 `test_single_token_ism_with_many_muhammads_truncates_to_k_cap` that builds a 20-Muhammad registry, asserts `len(packet.candidate_set) == K_CAP_STANDARD`, and asserts every survivor carries ONLY `name` in score_breakdown (proving fuzzy-only path). Round 2 dispatched with refresh prompt + maintainer-provided post-fix gate output (pyright clean, 39/39 session2 tests, 1001/14 full regression, validate_spec 0 errors / 124 atoms). Round 2 verdict CONFIRM_HIGH HIGH (`spec_reading_resolution: MAINTAINER_CORRECT` — Codex independently re-read AC-3's `then:` clause confirming "بن ثابت" byte-faithfulness; both round-1 defects RESOLVED with line-precision evidence; zero new defects; `recommended_action: COMMIT`; CAI critique-revise all 5 principles satisfied first pass). **5 files / +1909 lines:** `shared/scholar_authority/src/fragment_parser.py` NEW 446L (parse_fragment + 5-component decomposition + 3 custom errors FragmentNotArabicError + HonorificOnlyNameError + CompoundNameSplitError + FragmentParseResult Pydantic + helpers _glue_compound_abd_names / _strip_leading_honorifics_preserving_hamza / _decompose_into_5_components / _looks_like_nisba / _construct_match_key); `shared/scholar_authority/src/stage1_narrowing.py` NEW 561L (narrow_candidates + 5-channel architecture name/kunyah/nisba/work_title/century_active + N=3 work-title list-size guard + compound-title decomposition شرح/حاشية/تهذيب/مختصر+base + K cap 8 standard / 12 degraded after channel merge + Registry Pydantic substrate for Session-2 testing + normalize_work_title_for_index helper with chr-constructed tashkeel regex + decompose_compound_title helper); `shared/scholar_authority/src/name_matching.py` MODIFIED +152L (strip_invisible_unicode + InvisibleStripOccurrence dataclass + _BIDI_DIRECTION_MARKS [7 codepoints replace-with-space] + _WITHIN_TOKEN_INVISIBLES [4 codepoints strip plain] + _OPTIONAL_INVISIBLE_CODEPOINTS Persian/Urdu/Kurdish carve-out via preserve_persian_urdu_zwj kwarg); `engines/source/contracts.py` MODIFIED +9L (FRAGMENT_NOT_ARABIC + COMPOUND_NAME_SPLIT ErrorCode values; HONORIFIC_ONLY_NAME at line 579 REUSED per ChatGPT DR error-code citation discipline); `engines/source/tests/test_phase5_session2_implementation.py` NEW 752L 39 spec-linked tests (REQ-SRC-0050 5 ACs + 6 defensive negatives = 11 tests; REQ-SRC-0051 6 ACs + 6 defensive negatives = 12 tests; INV-SRC-0014 4 ACs + 3 defensive negatives = 7 tests; helper-function unit tests = 9 tests; 38/38 round-1 + 1 new AC-6 sub-claim 2 = 39). 1 atom amendment: REQ-SRC-0050.yaml gained the connector-preservation postcondition + amended AC-2 (lines 91-103 + 164-177). **Mid-session bug averted (preserve as methodology learning):** during smoke-test of normalize_work_title_for_index, the literal-character regex `[ؐ-ًؚ-ٰٟ]` was discovered to be silently re-encoded by Write tool such that codepoint ordering swapped to `[ؐ-ًؚ-ٰٟ]` — first range U+0610-U+064B covers ALL Arabic letters U+0621-U+064A, so `_TASHKEEL_RE.sub("", text)` would strip ALL Arabic content. Surfaced when `normalize_work_title_for_index('بدائع الصنائع')` returned `''`. Fix: build the regex character class via explicit `chr(0x0610)+...+chr(0x0670)` (both fragment_parser.py:56-62 and stage1_narrowing.py:90-96 use this pattern). NEW T-1 corruption vector class added to threat catalog: silent-codepoint-reorder contamination via editor/file-write round-trip. Disclosed to Codex in dispatch prompt under maintainer claim "regex codepoint-corruption defense"; Codex verified both files use chr-constructed form per CONFIRM_HIGH cross-check at section_d. **Bidi-marks-as-token-separators correction:** initial strip_invisible_unicode used naive "strip without replacement" semantics; smoke-test of INV-SRC-0014 AC-2 (bidi-contaminated `الإمام<U+200E>البخاري`) revealed this glued the two tokens into `الإمامالبخاري`, defeating Stage-2 honorific recognition. Fixed by partitioning bidi direction-marks (U+200E/F + U+202A-202E, replace with single space — preserves token boundaries) from within-token invisibles (U+200B/FEFF/2060/00AD, strip plain — these are intra-token formatting noise). **Methodology learnings to preserve for Session 3:** (a) round-cap-2 protocol vindicated for THIRD consecutive Phase 5 dispatch (Stage 4 / Session 1 / Session 2) — surgical-fix-then-redispatch closes most AMEND_HIGH/MEDIUM verdicts on second round; (b) AC-internal inconsistency is a defect class (AC-2 vs AC-3 expected nasab_chain divergence) that the maintainer can resolve via atom amendment when one AC is byte-faithful and the other has YAML transcription drift — avoid position-specific normalization rules; (c) `spec_reading_resolution: MAINTAINER_CORRECT` is reliable when Codex independently quotes the conflicting AC text and confirms the maintainer's diagnosis; (d) chr()-constructed regex character classes are the durable form for Arabic codepoint ranges — literal-character form is hostile to round-trip encoding; (e) bidi marks must REPLACE-with-space on strip, not bare-remove, to preserve token boundaries (within-token invisibles strip plain). 1001 pass / 14 skip (was 962/14 baseline; +39 from Session 2); validate_spec 0 errors / 124 atoms; pyright clean. **Phase 5 Session 3 implementation (Stage-2 verifier cell per REQ-SRC-0052 + REQ-SRC-0053 + INV-SRC-0013 + INV-SRC-0016) NOW the active sub-frontier.**

**Recent build activity (2026-04-30):**
- `fcdb03a32` feat(source,shared/scholar_authority): Phase 5 IMPLEMENTATION Session 1 — CONTRACT-LAYER LANDED. CON-SRC-0008 ScholarMatchResult (5 ACs) + CON-SRC-0009 ScholarEvidencePacket (4 ACs) + REQ-SRC-0049 registry snapshot locking (4 ACs) + INV-SRC-0017 F-7 closure (4 ACs) implemented as Pydantic data contracts + snapshot-locking primitive. **Codex CLI structural review verdict: CONFIRM_HIGH at HIGH confidence (round 2 of 2 per closure §6 round-cap protocol).** Round 1 returned REJECT_WITH_DEFECT at LOW — procedurally misclassified per the round-1 prompt rubric (REJECT reserved for fundamental architectural mistakes; round-1 recommended_action was SURGICAL_FIX_THEN_REDISPATCH). Round-1 substantive findings: 1 HIGH defect (validator gap: `_validate_disputed` didn't enforce `record_status` non-null for disputed; CON-SRC-0008 AC-2 line 158-166 requires "record_status reflects the leading id's record lifecycle" + field spec line 73-81 says "Null when canonical_scholar_id is null" → contrapositive: non-null when canonical is non-null) + 1 MEDIUM defect (test coverage gap: existing AC-2 test didn't assert `record_status`; no negative-case test for null record_status in disputed). Both surgical fixes applied: (1H) `match_contracts.py:_validate_disputed` lines 390-397 gained `record_status is None` guard between confidence check and evidence_sources check, citing CON-SRC-0008 AC-2 + field spec line 73-81; (1M) `test_disputed_populates_positions_with_full_breakdown:301` gained `assert result.record_status == 'confirmed'`; new `test_disputed_with_null_record_status_rejected` lines 423-445 added (31st test). Round 2 dispatched with refresh prompt + maintainer-provided post-fix validation output (pyright clean, 31/31 session1 tests, 962/14 full regression, validate_spec 0 errors / 124 atoms). Round 2 verdict CONFIRM_HIGH HIGH (`spec_reading_resolution: maintainer_correct`, all 17 ACs PASS, 17/17 spec_link_coverage, all 4 sections PASS, zero new defects, `recommended_action: COMMIT`). New modules: `shared/scholar_authority/src/match_contracts.py` (~446L, 14 Pydantic types: ScholarMatchResult + ScholarEvidencePacket + ScholarMatchProvenance + ThresholdAudit + VerifierRecord + Position + ScoreBreakdown + CitationRef + RevisionHistoryEntry + CareerPhaseRef + NormalizedFragment + ScholarCandidate + DossierContext) + `shared/scholar_authority/src/snapshot_lock.py` (~158L, RegistrySnapshot + RegistrySnapshotDriftError + RuntimeExternalCallError + lock_registry_snapshot + pin_registry_snapshot + validate_no_drift). 3 new ErrorCode values added to `engines/source/contracts.py`: SCHOLAR_NO_MATCH + REGISTRY_SNAPSHOT_DRIFT + RUNTIME_EXTERNAL (existing HONORIFIC_ONLY_NAME REUSED per ChatGPT DR finding; not duplicated). `engines/source/tests/test_phase5_session1_implementation.py` (~542L) with 31 `@pytest.mark.spec` tests using real Arabic fixture data (ابن حجر العسقلاني / البخاري / أحمد بن حنبل / al-Shāfiʿī). The OLD `ScholarMatchResult` dataclass at `shared/scholar_authority/src/scholar_authority.py:31` is INTENTIONALLY preserved (Session 4 deprecates it once `compute_scholar_match_score` is rewired); naming collision documented in `match_contracts.py` docstring. `snapshot_version` is FORBIDDEN per Codex Stage-3 Defect 2; canonical name `registry_release_version` is enforced via two layers (`extra='forbid'` + `mode='before'` validator) on ScholarMatchProvenance + ScholarEvidencePacket + ScholarMatchResult + RegistrySnapshot. **Phase 5 Session 2 implementation (Stage-1 deterministic narrowing per REQ-SRC-0050 + REQ-SRC-0051 + INV-SRC-0014) NOW the active sub-frontier.**
- `e91c142cc` feat(source,shared/scholar_authority): Phase 5 STAGE-4 CLOSURE — 12 new atoms (REQ-SRC-0049 through 0053; CON-SRC-0008/0009; INV-SRC-0013 through 0017) + 6 amendments to existing atoms (REQ-SRC-0008/0028/0035/0042/0043; DEC-SRC-0013) + shared/scholar_authority/SPEC.md amendments at §4.A.2 + §6 + §7 + KNOWN_LIMITATIONS.md (L-SCH-001 through L-SCH-004) + 35 spec-content tests landed at 34 files / +4119/-86 lines. **Codex CLI structural review verdict: CONFIRM_HIGH at HIGH confidence (round 2 of 2 per closure §6 round-cap protocol).** Round 1 returned AMEND_HIGH at MEDIUM — inflated by environmental Python-not-on-PATH FAILs while substantively containing 3 surgical defects (1H + 1M + 1L, all line-precision recommended_fix). Round 1 surgical fixes applied: (1H) REQ-SRC-0053 disputed predicate gained condition (e) for `convergent identity at round-1 + at least one verifier < 0.90 (both_pass=false)` — closing the previously-undefined routing gap that AC-2 exercises (mean ≥ 0.92 with one verifier 0.89, no close rival, floor met); partition exhaustiveness clause + source field rationale updated. (1M) REQ-SRC-0052:135+240+244 stale 0.05→0.07 in round-1 routing text + AC-4 given/then. (1L) CON-SRC-0008:154 stale 0.05→0.07 in AC-2 disputed-margin reference. Round 2 dispatched with refresh prompt + maintainer-provided local validation output (validate_spec 0 errors / 124 atoms; pytest 35 + 358 pass) as authoritative substitute for the gates Codex sandbox cannot run + explicit non-defect declaration for REQ-SRC-0053's historical 0.05 references in source/rationale/AC-5 (false-positive prevention). Round 2 verdict CONFIRM_HIGH HIGH (3467 lines, 82K tokens, all 4 sections PASS/RESOLVED, zero new_defects_found). **All 8 Stage-3 inputs absorbed** (4 Codex defects [threshold partition / provenance naming / 3-vs-5-state surface / shared SPEC amendments] + 4 arabic-reviewer findings [list-size guard N=3 / bidi-mark ordering / work-title normalization function / compound-title decomposition]) **+ 3 Stage-4 round-1 surgical fixes**. Tests 358/0/0 (323 baseline + 35 spec-content); validate_spec 0 errors / 124 atoms (was 112); pyright clean. **Phase 5 implementation phase NOW ACTIVE as next sub-frontier.**
- `_pending_` Phase 5 ChatGPT DR digest STAGE-2 COMPLETE (per-DR digest at `memory/phase5_dr_chatgpt_digest_20260429.md`, 675 lines, parallel 20-section structure to Stage 1 Claude DR digest; ChatGPT DR chose OPT-4 with HIGH self-confidence → KR-verified HIGH-MINUS; **ChatGPT DR's PIVOT = WORK-TITLE-AS-DETERMINISTIC-INDEX-CHANNEL** [vs Claude DR's ≥2-non-name-attribute floor pivot]; cross-provider 2-of-2 convergence on OPT-4 architecture + hot-path-forbids-runtime-external + ≥2-corroborating-attribute floor concept + F-1 through F-7 catalog + Phase 1 5/5 constraints + 2/4 classical anchors shared (al-Mukmil + al-Lubāb); ChatGPT DR analytically stronger than Claude DR on 5-state lifecycle preservation + teacher-student fields + schema overlap [~50% vs Claude DR's ~30%] + cited existing error code SRC-E-HONORIFIC-ONLY-NAME + zero Phase 2 misattributions; CRITICAL §3g atom delta finding: REQ-SRC-0045/0046/0047/0048 + INV-SRC-0010/0011/0012 ALL TAKEN — only REQ-SRC-0049 + CON-SRC-0008 + CON-SRC-0009 immediately usable, 7 atoms need renumbering; no process-honesty disclosure note from ChatGPT DR per amended dr-dispatch-checklist.md `38bad4eb6` [postdates relay], KR-reconstructed implicit fetch signals via fileciteturn token distribution show atom-content fetch SUCCEEDED but spec-inventory fetch DID NOT; companion Codex dispatch DEFERRED to Stage 3 4-evaluator wave on consensus architecture; Stage 3 = fresh session for cross-provider synthesis [PATH A applies])
- `_pending_` docs(source): record FU-18 retry attempt 2 outcome (4-of-4 verdicts received, no cross-provider 3-of-4 majority; deferred indefinitely; substantive convergence documented)
- `9331aca11` docs(source): record FU-18 dispatch attempt 1 deferral (3-of-4 evaluators failed; arabic-reviewer PRELIMINARY SHAPE-C HIGH; FU-18 scope narrowed from 4 to 2 scenarios)
- `cd95ab9e4` docs(source): close OQ-SRC-0005 in active frontier (zero deferred atoms)
- `49a864ffe` feat(source): close OQ-SRC-0005 (agent monitoring scope superseded, 0 deferred atoms; Codex CLI 1-evaluator structural dispatch via /prompt-architect CAI Critique-Revise on TIDD-EC; OPT-A HIGH confidence with SHAPE-2 in-place supersedure; resolution introduces NO new normative behavior — RATIFIES de facto state already encoded by REQ-SRC-0029 + REQ-SRC-0008 + REQ-SRC-0028 + DEC-SRC-0004 + DEC-SRC-0013; 829 pass)
- `6d2a9388f` docs(source): correct stale deferred-atom priority list in active frontier
- `021b7e745` docs(source): close follow-up 27 in active frontier
- `6791f3781` feat(source): close follow-up 27 (break 9 pre-existing depends_on cycles in spec atom graph, 344 pass; Codex CLI structural producer-consumer analysis dispatch via /prompt-architect TIDD-EC; 0 cycles remain post-fix verified via DFS on 112-atom graph)
- `04bc261f8` docs(source): close follow-up 28 in active frontier
- `cc7a017ae` feat(source): close follow-up 28 (remove dead `LevelProvenance.TAXONOMY_ENGINE` enum value, 344 pass; structural ripgrep trace confirmed dead surface — referenced only in 2 test fixtures, never written by production code; per closed DEC-SRC-0003 OWN_SYNTHESIS adjudication)
- `c699ba607` docs(source): close follow-up 36 in active frontier
- `06d181be0` feat(source): close follow-up 36 (HadithSubgenre.ADHKAR + HadithSubgenre.ADAB enum additions, both EXCLUDED from LEVELED carve-back per SHAMAIL precedent; Q-A is_abridgement BLOCKED at 2-of-4 cross-provider with documented limitations L-FU36-1/L-FU36-2; 345 pass)
- `182ac87b7` docs(source): close follow-up 37 in active frontier
- `9d3bebdcb` feat(source): close follow-up 37 (constituent override-entrance widening, 317 pass; arabic-reviewer Agent (a+b) HIGH retroactive validation closes FU-24's deferred owner-override-entrance promise)
- `550483dbf` docs(source): close follow-up 24 in active frontier; open follow-up 37
- `d2c4798e9` feat(source,normalization): close follow-up 24 (constituent-level placeholder surface, 295 pass; conftest.level_status fix unblocks 15 cross-engine boundary tests)
- `3ef4500f0` docs(source): close follow-up 35 in active frontier; open follow-up 36
- `824fef574` feat(source): close follow-up 35 (TARGHIB+SHAMAIL enum, MUKHTASAR BLOCKED, 254 pass)

**Open follow-ups:** 18 (FU-27, FU-28, FU-36 closed at preceding commits in this session; FU-18 dispatch attempt 1 deferred and retry attempt 2 also deferred — see below). **Deferred SPEC atoms: {} — last deferred atom OQ-SRC-0005 superseded at commit `49a864ffe`; first time the source-engine spec has zero deferred atoms since freeze 2026-04-15.**

**FU-18 retry attempt 2 outcome (2026-04-29):** 4-evaluator wave RETRIED with all 3 previously-failed evaluators successfully re-dispatched. Codex CLI session-start-bypass header WORKED (no off-task this time); Gemini Pro capacity recovered (no `--model` flag needed — default `gemini-3.1-pro-preview` IS the configured best per owner correction; the original retry recipe's `--model gemini-2.5-pro` instruction was wrong). All 4 evaluators returned HIGH-confidence verdicts: **arabic-reviewer (Anthropic) SHAPE-C** (optional `nuance` payload, 3 enum values, no Phase 2 drift); **Codex CLI (OpenAI) SHAPE-B** (REQUIRED `scholarly_mode` axis, 2 enum values [determinative \| i_tibar], 78-assignment audit table 9/0/69 split, no Phase 2 drift); **Gemini Run A (Google) SHAPE-A** (new 4th tier `disputed`, 4-tier MECE partition, no Phase 2 drift, EXPLICITLY rejected SHAPE-B with reasoning "structurally cleaner without massive schema rewrite"); **Gemini Run B (Google) SHAPE-A→SHAPE-B** (Phase 1 SHAPE-A independently matching Run A; Phase 2 drifted to SHAPE-B citing "sealed-block 2-axis reframe elegantly solves" — sealed-block-anchor-influenced, discount as cross-time-independent confirmation). **Phase 2 final tally: SHAPE-A:1 / SHAPE-B:2 (one with drift) / SHAPE-C:1.** **By provider Phase 2: Anthropic→C / OpenAI→B / Google→split(A,B). NO shape achieved 3-of-4 cross-provider HIGH.** Phase 1 cross-time-independent baseline: SHAPE-A:2 (both Geminis) / SHAPE-B:1 (Codex) / SHAPE-C:1 (arabic-reviewer) — also no 3-of-4 majority. Per `.claude/rules/no-single-model-conclusion.md`, no amendment can be applied as final. **The user's "If confirmed: apply SHAPE-C amendment" conditional does NOT fire.** **Substantive convergence (4-of-4 unanimous):** existing severity tier set {fatal, blocking, warning} stays unchanged for all 78 assignments + supplementary mechanism is needed (all 4 reject SHAPE-D status quo) + al-Suyūṭī Tadrīb al-Rāwī Nawʿ 22-23 on iʿtibār is the central classical anchor (cited by all 4) + hamza nuance splits by text-stratum (Quranic=fatal, prose=preserve as variant) + existing source atoms REQ-SRC-0008/REQ-SRC-0012/REQ-SRC-0047 already provide the preservation surfaces (`trust_decision.disputed`, `genre_dispute`, `PendingLevelOverride.dispute_snapshot`). **Shape divergence (the unresolved question):** 4 evaluators split 3-ways on REQUIRED-vs-OPTIONAL framing (Codex required axis vs arabic-reviewer optional payload vs Run A new tier). Each shape rejected the others with explicit reasoning (Run A: SHAPE-B requires massive schema rewrite; Codex: SHAPE-C optional doesn't repair MECE; arabic-reviewer: SHAPE-B violates Owner Principle 6 no-binding-downstream-contracts). **Cross-provider 3-way split is genuine, not methodological error.** Provider-correlated reasoning patterns are detectable: Anthropic→minimal-disruption-SHAPE-C / OpenAI→structural-rigor-SHAPE-B / Google→clean-MECE-partition-SHAPE-A. **Decision: FU-18 closure DEFERRED indefinitely.** Substantive convergence is sufficient progress; shape choice is structural-engineering judgment that pipeline experience may inform later (similar to OQ-SRC-0005 resolution). Future re-engagement options: (a) accept indefinite deferral (sufficient progress documented), (b) commission 5th evaluator dispatch with refined SHAPE-A-vs-B-vs-C question, (c) wait for downstream-engine implementation pressure to surface concrete shape requirements. Currently NO error_condition is blocked on this decision. Dispatch artifacts retained as untracked working-tree files at `engines/source/_dispatch/_fu18_*.md` (per `.claude/rules/no-repo-pollution.md` snapshot rule — sealed block `_sealed_fu18_evaluator_block.md` not committed because FU-18 didn't close successfully). Raw verdict outputs at `.kr/runtime/_fu18_*_raw.md` (gitignored). All 3 retry dispatches logged to `dispatch_log.jsonl`. Methodology learnings captured at `~/.claude/projects/C--Users-Rayane-Desktop-kr/memory/session_handoff_20260429_fu18_retry_attempt2_no_majority.md`. Gates: validate_spec 0 errors / 112 atoms; pyright not run (no Python touched); pytest 829 pass / 0 fail / 14 skipped (UNCHANGED); D-023 boundary warnings unchanged.

**FU-18 dispatch attempt 1 deferral (2026-04-29):** 4-evaluator dispatch wave executed; 3 of 4 evaluators failed → per `.claude/rules/coworker-dispatch.md` "If 2+ coworkers are unavailable, the milestone MUST wait." FU-18 closure DEFERRED to fresh session for retry. Dispatch outcome: (a) **Codex CLI** failed off-task — Codex's session-start protocol (read `docs/codex/operating-model.md` + ACTIVE_AUTHORITY.md + CLAUDE.md + .kr/ACTIVE.md + .kr/HANDOFF.md auto-fires before user-prompt content is processed) diverted Codex into producing a "Codex authority cutover doctrine" document instead of executing the FU-18 dispatch. Output unusable for FU-18 verdict. Fix for retry: add session-start-bypass header at top of Codex wrapper. (b) **Gemini Run A + Run B** both failed with 429 RESOURCE_EXHAUSTED on `gemini-3.1-pro-preview` after 10 retry attempts — Google API server-side capacity exhaustion. Fix for retry: switch to `gemini-2.5-pro` (precedent: FU-36 closure) or wait for capacity recovery. (c) **arabic-reviewer Anthropic Agent** SUCCEEDED with substantive HIGH-confidence verdict on **SHAPE-C (tier-plus-payload nuance field, NOT new tiers)**. arabic-reviewer's verdict marked PRELIMINARY per `.claude/rules/no-single-model-conclusion.md` because single-evaluator content quality conclusions cannot close a 4-evaluator wave. **Critical methodological finding from arabic-reviewer**: 50% of the prior 2026-04-21 collapse claims (agent-disagree, owner-override) were INVALIDATED by the 2026-04-17 REQ-SRC-0047 amendment that postdates the original AMEND verdicts. The next session's dispatch can NARROW from 4 scenarios to 2 (tahqiq + hamza only). **Critical structural finding (advisory):** `engines/source/contracts.py:526-529` `ErrorSeverity` enum has `FATAL/WARNING/INFO` — NOT `FATAL/BLOCKING/WARNING` as schema.json + CON-SRC-0012 specify. `BLOCKING` is ABSENT from Python; `INFO` is in Python but absent from schema. Pre-existing T-6 divergence; the next session's SHAPE-C application MUST also synchronize contracts.py. **arabic-reviewer SHAPE-C proposal (PRELIMINARY):** add optional `nuance: Optional[Literal["tahqiq_variant", "hamza_quranic", "hamza_prose"]]` to errorCondition schema with mandatory tier-nuance pairing rules (tahqiq_variant→warning, hamza_quranic→fatal, hamza_prose→warning). 4 classical scholarly anchors cited (al-Khaṭīb al-Baghdādī *al-Jāmiʿ li-Akhlāq al-Rāwī* / Ibn Ḥajar *Nuzhat al-Naẓar* / al-Suyūṭī *Tadrīb al-Rāwī* Nawʿ 22-23 / al-Suyūṭī *al-Itqān fī ʿUlūm al-Qurʾān* Nawʿ 19) — rectifying the 2026-04-21 `scholarly_citation: none_available` lacuna. Cross-engine consumer-contract specified (nuance is OPTIONAL; downstream engines that don't read it are unaffected). 7 new acceptance criteria proposed (AC-7 through AC-13). 1 open sub-question within ≤1 cap (whether to add `isnad_truncation` as 4th nuance value; doesn't block closure). Full verdict at `.kr/runtime/_fu18_arabic_reviewer_raw.md`; pre-staged context at `~/.claude/projects/C--Users-Rayane-Desktop-kr/memory/fu18_dispatch_prep.md` (with retry recipe + failure-mode-fix instructions). **Dispatch artifacts retained for retry:** `engines/source/_dispatch/_fu18_dispatch_master_optimized.md` (master prompt, reusable as-is), `engines/source/_dispatch/_fu18_*_dispatch.md` (4 evaluator wrappers, Codex needs session-start-bypass patch, Geminis need `--model gemini-2.5-pro` flag), `engines/source/_dispatch/_sealed_fu18_evaluator_block.md` (sealed prior-evaluator block for confrontation step, FU-37 rectification compliant). All retained as untracked working-tree artifacts (per `.claude/rules/no-repo-pollution.md` snapshot rule — committed only when FU-18 closes successfully). **Next session retry path** (priority order): (1) read `memory/fu18_dispatch_prep.md` for full retry recipe, (2) patch Codex wrapper, (3) verify Google API capacity recovered, (4) run `/prompt-architect` to refresh HR-23 timer, (5) re-dispatch Codex + Gemini Run A + Gemini Run B in parallel (skip arabic-reviewer retry — its 2026-04-29 verdict is usable as 1-of-4), (6) synthesize cross-provider verdicts, (7) apply SHAPE-C amendment if confirmed at ≥3-of-4 cross-provider HIGH, (8) commit feat+docs, (9) close FU-18.

**OQ-SRC-0005 closure summary:** The 1 remaining `status: deferred` SPEC atom in the source engine. Question: agent monitoring scope (where do monitor agents live in the pipeline architecture given the now-stable agent-team architecture?). Three candidates: OPT-A source-engine monitors (prior likelihood: possible), OPT-B pipeline-wide monitors (prior likelihood: likely), OPT-C per-book monitors (prior likelihood: unlikely). Note: prior likelihoods were placeholder anchors, not verdicts; the dispatch's optimized prompt explicitly forbade ratifying them without independent reasoning. Codex CLI 1-evaluator structural dispatch (gpt-5.4 via `codex exec --full-auto`, through `/prompt-architect` CAI Critique-Revise applied to TIDD-EC framework — single-evaluator scope correct per `.claude/rules/coworker-dispatch.md` "structural checks alone do not require [4-evaluator] dispatch", parallel to FU-27 producer-before-consumer 9-cycle break decision via Codex CAF-1). Verdict: **OPT-A HIGH confidence with SHAPE-2 in-place supersedure**. Three rules unanimously favor OPT-A: (1) **Specialization-by-stage** (DEC-SRC-0003 abstract pattern: each engine owns its analytical and process concerns) — REQ-SRC-0029 already locates monitor_feedback at the source-engine metadata_deliberation step (`layer: pipeline / step: metadata_deliberation`); (2) **No-binding-downstream-contracts** (engine CLAUDE.md owner principle 6: "All engines rebuilt from first principles") — OPT-B would impose source-defined monitor contract on engines not yet built from first principles; OPT-A leaves them free. (3) **YAGNI / pipeline-experience** — source is currently the ONLY engine producing monitor_feedback; OPT-B becomes structurally appropriate only after >=2 engines independently demonstrate monitor needs and a shared abstraction emerges from real pipeline experience. OPT-C rejected because confirmed atoms attach monitoring to deliberation-cell completion (REQ-SRC-0029) and routing paths (REQ-SRC-0028), not to a separate book-level monitor layer; OPT-C invents unsupported granularity. SHAPE-2 (in-place supersedure) chosen over SHAPE-1 (new DEC atom) because the resolution introduces **NO new normative behavior** — it only RATIFIES the de facto state already encoded by 5 confirmed atoms (REQ-SRC-0029 + REQ-SRC-0008 + REQ-SRC-0028 + DEC-SRC-0004 + DEC-SRC-0013). A new DEC atom would duplicate normative content already present. SHAPE-2 §4 cycle-introduction check: introduces no new node and no new graph edges → graph remains acyclic (DFS verification not re-run because no edge added; FU-27 closure verified 0 cycles on full 112-atom graph at commit `6791f3781`). Optimized prompt enforced **4 anti-scope-creep guards** (improvements over the FU-27 dispatch via CAI Critique-Revise): (a) no pre-loaded conclusions in evaluation matrix — Codex must DERIVE per-option verdicts from a 3×3 rule×option matrix, not regurgitate hints; (b) explicit prohibition on invoking classical Islamic scholarly precedent (Ibn Khaldūn, al-Zarnūjī, muḥaddithūn iʿtibār, al-Fihrist, Kashf al-Ẓunūn) — those resolved DEC-SRC-0003 already and are out of scope here; (c) observable confidence rubric (HIGH = all three rules satisfied + zero contradictions + acyclic + zero scholarly sub-questions surfaced); (d) bounded "open sub-questions" field to scholarly-content only — structural ambiguities must be resolved, not deferred. **All 4 guards held empirically** — Codex's verdict shows ZERO classical scholarly precedent invoked, ZERO conditional output (always-argue against all non-chosen options), and ZERO open sub-questions surfaced. Verdict identically emitted at lines 4010 and 4146 of the raw output (114,081 tokens), confirming no judgment drift between Codex's mid-reasoning verdict and end-of-session verdict. Cross-provider scholarly readiness NOT REQUIRED for this dispatch — it is purely structural per `.claude/rules/no-single-model-conclusion.md` (structural checks alone do not require consensus). The dispatch-tiering rubric exercised across 4 closures this 2026-04-29 session is now a 4-tier matrix: 4-evaluator wave (FU-36 scholarly+structural) / 1-evaluator structural with content judgment (FU-27 cycle-break, OQ-SRC-0005 design-scoping) / 0-dispatch ripgrep (FU-28 dead enum trace) / closed-DEC follow-on amendment (e.g., NEXT.md priority-list reconciliation). Output captured at `.kr/runtime/_oqsrc0005_codex_raw.md` (4277 lines, 114,081 tokens). Optimized dispatch prompt at `.kr/runtime/_oqsrc0005_codex_dispatch_optimized.md`. Gates: validate_spec 0 errors / 112 atoms (status: confirmed=106, deferred=0, superseded=6 — was confirmed=106, deferred=1, superseded=5; net superseded +1 = OQ-SRC-0005 transitioned in-place); pyright not required (no Python code touched — pure spec amendment); pytest 829 pass / 0 fail (323 source + 506 normalization; 14 pre-existing skipped tests in normalization); D-023 boundary warnings unchanged (5 pre-existing); spec/views/* regenerated via `engines/source/scripts/generate_views.py` (deferred.md emptied of OQ-SRC-0005, superseded.md gained the entry, status counts updated in by-layer/questions.md and by-topic/agent_ergonomics.md and README.md). **Architectural significance**: this is the first commit since spec freeze (2026-04-15) at which the source-engine spec has ZERO deferred atoms — every question resolved either as a normative atom or as a superseded historical record with rationale. The "scoped-injection unblocking" implication noted in `.kr/ACTIVE.md:274` is now fully realized: build-phase scoped-atom packs for steps 10-40 cannot silently include unresolved questions (none remain to include).

**FU-27 closure summary:** 9 pre-existing `depends_on` cycles in the source-engine spec atom graph (surfaced during Phase 5b item-5 closure 2026-04-23 by explicit DFS cycle detection on the 110-atom graph; recorded at `.kr/ACTIVE.md:158` and `:274`) BROKEN via 9 edge removals across 8 atom files. Codex CLI dispatch (gpt-5.4 via `codex exec --full-auto`, through `/prompt-architect` TIDD-EC framework — purely structural cycle-break analysis, single-evaluator scope is correct per `.claude/rules/coworker-dispatch.md` "structural checks alone do not require [4-evaluator] dispatch"). Codex read each cycle's atoms directly via Read tool and applied the **producer-before-consumer rule (Codex CAF-1 from item-5 closure, vindicated for the second consecutive structural cycle-break decision)** to identify the consumer-side edge to remove per cycle, with concrete textual no-new-cycle arguments. The 9 cycles + chosen edge-removals: (1) OQ-SRC-0005 ↔ DEC-SRC-0004 → REMOVE OQ-SRC-0005 from DEC-SRC-0004 (DEC-SRC-0004 produces agent-team trust workflow; OQ-SRC-0005 asks scope question about it). (2) OQ-SRC-0005 ↔ REQ-SRC-0008 → REMOVE OQ-SRC-0005 from REQ-SRC-0008 (REQ-SRC-0008 produces trust_decision + monitor_feedback emission; OQ-SRC-0005 asks scope question about that mechanism). (3) REQ-SRC-0012 ↔ INV-SRC-0004 → REMOVE INV-SRC-0004 from REQ-SRC-0012 (REQ-SRC-0012 produces disputed_field.positions structure; INV-SRC-0004 uses structure to enforce no-consensus-forcing). (4) INV-SRC-0002 → REQ-SRC-0014 → REQ-SRC-0004 → INV-SRC-0002 3-cycle → REMOVE REQ-SRC-0004 from REQ-SRC-0014 (REQ-SRC-0014 produces role-marker parsing/author-copyist separation; REQ-SRC-0004 consumes role-clean evidence). (5) REQ-SRC-0001 ↔ DEC-SRC-0014 → REMOVE REQ-SRC-0001 from DEC-SRC-0014 (DEC-SRC-0014 produces two-registry staged-admission architecture; REQ-SRC-0001 implements raw-upload registration). (6) REQ-SRC-0025 → REQ-SRC-0019 → REQ-SRC-0018 → REQ-SRC-0001 → DEC-SRC-0014 → REQ-SRC-0025 5-cycle → REMOVE REQ-SRC-0025 from DEC-SRC-0014 (DEC-SRC-0014 produces separate-tracking architecture; REQ-SRC-0025 implements admission/handoff under it; second edge from same atom — `DEC-SRC-0014.depends_on` becomes empty list). (7) REQ-SRC-0019 ↔ REQ-SRC-0021 → REMOVE REQ-SRC-0021 from REQ-SRC-0019 (REQ-SRC-0019 produces general intake-analysis dossier contract; REQ-SRC-0021 PDF-specific branch using that contract). (8) REQ-SRC-0025 ↔ DEC-SRC-0016 → REMOVE REQ-SRC-0025 from DEC-SRC-0016 (DEC-SRC-0016 produces owner-submission risk gate architecture; REQ-SRC-0025 implements admission gating under that policy). (9) REQ-SRC-0025 ↔ REQ-SRC-0027 → REMOVE REQ-SRC-0025 from REQ-SRC-0027 (REQ-SRC-0027 produces `owner_submission_risk_case` + blocking semantics; REQ-SRC-0025 uses gate outcome for admission/handoff decisions). DFS verification post-amendment: **0 cycles detected on the full 112-atom graph** (down from 9). Codex's textual no-new-cycle arguments verified empirically — all 9 cycles genuinely broken and no new cycles introduced. Empty `depends_on: []` result on `REQ-SRC-0014` and `DEC-SRC-0014`: validate_spec accepts both — schema permits empty depends_on for atoms that are pure producers (DEC-SRC-0014 defines architecture; REQ-SRC-0014 defines role markers; both foundational atoms with no upstream consumer-side dependencies). **Scoped-injection unblocking implication** (per `.kr/ACTIVE.md:274`): with the freeze/intake/container-classification sub-graph now acyclic, build-phase scoped-atom packs for steps 10-40 can no longer silently include cyclically-referenced atoms — this was the latent ergonomic risk during Phase 5b item-5. Output captured at `.kr/runtime/_followup_27_codex_raw.md`. Gates: validate_spec 0 errors / 112 atoms; pyright 0/0/0 (no code touched — pure spec-graph amendment); pytest 344 pass / 0 fail (unchanged from FU-28 baseline); D-023 boundary warnings unchanged; DFS cycle-detection: 0 cycles on full 112-atom graph.

**FU-28 closure summary:** `LevelProvenance.TAXONOMY_ENGINE` REMOVED as dead enum surface. Structural ripgrep trace confirmed it was referenced ONLY in 2 test fixtures (`test_followup_24_constituent_placeholder.py:54` parametrize row + `test_work_level_and_status.py:426` ADV-012 stickiness test), NEVER written by production code in any engine. Per the closed DEC-SRC-0003 OWN_SYNTHESIS adjudication (Phase 5b item 7, 2026-04-23, 3-of-3 UNANIMOUS HIGH from Codex CLI gpt-5.4 + Gemini Run A gemini-3.1-pro-preview + Gemini Run B gemini-2.5-pro), the synthesis engine is the sole writer of `level`. Per `.claude/rules/coworker-dispatch.md` "structural checks alone do not require dispatch" — no 4-evaluator wave needed because this is purely structural codebase fact-finding. REMOVE-DEPRECATE chosen over KEEP-WITH-WARNING because dead enum surface is a maintenance burden and a T-1 corruption vector (a future code path accidentally using TAXONOMY_ENGINE provenance for a synthesis-owned write would silently violate DEC-SRC-0003 single-writer discipline). LevelProvenance now contains only `{OWNER_OVERRIDE, SYNTHESIS_ENGINE}`. Test fixtures updated: `test_work_level_and_status.py:426` TAXONOMY_ENGINE → SYNTHESIS_ENGINE (any non-null LevelProvenance exercises the ADV-012 stickiness invariant); `test_followup_24_constituent_placeholder.py:54` parametrize row removed (other rows already cover all 3 ASSIGNED-state combinations via SYNTHESIS_ENGINE / OWNER_OVERRIDE). CON-SRC-0004 spec atom updated with closure note. Gates: validate_spec 0 errors / 112 atoms; pyright 0/0/0 on touched files; pytest 344 pass / 0 fail (was 345 after FU-36; net -1 = removed parametrize row using deleted enum value).

**FU-36 closure summary:** 4-evaluator cross-provider dispatch (Codex CLI gpt-5.4 + Gemini Run A/B gemini-2.5-pro + arabic-reviewer Anthropic Agent), all through `/prompt-architect` with CAI Critique-Revise + Step-Back + TIDD-EC hybrid framework. **The FU-37 sealed-block-in-separate-file rectification was applied for the first time and SUCCEEDED for Codex and arabic-reviewer (full Read-tool-call file-read sequence verified); Geminis used cat-via-shell because .kr/ is gitignored, producing a slightly weaker but still observable file-read sequence in their tool-call log.** Three sub-questions resolved: **Q-A** (`is_abridgement` orthogonal property): **BLOCKED** at 2-of-4 (Codex + arabic-reviewer) — all enumerated PROCEED paths fail to wire into the level gate or dispute path; Geminis recommended PROCEED but DIVERGED between path-2 (per-constituent) vs path-3 (genre migration), weakening cross-time independent signal; documented limitations L-FU36-1 (`_extract_target` narrowness for non-"مختصر" Genre.MUKHTASAR keywords like خلاصة/تهذيب/تقريب/ملخص/وجيز) + L-FU36-2 (gate-semantics gap requiring future architectural path-5 with dual-surface metadata + INV-SRC-0012 wiring + GenreDisputePosition `abridgement_candidate` field analogous to FU-34's `hadith_subgenre_candidate`). **Q-B** (`HadithSubgenre.ADHKAR`): **PROCEED ADD-EXCLUDED** at 3-of-4 cross-provider — al-Nawawī's *al-Adhkār* / al-Jazarī's *al-Ḥiṣn al-Ḥaṣīn* / Ibn al-Sunnī's *ʿAmal al-Yawm wa-l-Laylah* / Ibn Taymiyyah's *al-Kalim al-Ṭayyib* tagged correctly via 4 compound rules (`عمل + (اليوم|الليلة)` / `الحصن + الحصين` / `كلم + طيب` / `أذكار + (الصباح|المساء|اليوم|الليلة|السفر|النوم)`), but EXCLUDED from `LEVELED_HADITH_SUBGENRES` per SHAMAIL precedent (chain-preservation in Ibn al-Sunnī's founding-ancestor canonical text per al-Khaṭīb al-Baghdādī's *al-Jāmiʿ li-Akhlāq al-Rāwī wa-Ādāb al-Sāmiʿ* riwāyah-class vs taʿlīm-class distinction — novel anchor surfaced by arabic-reviewer DIM-AR1 not cited by either Gemini). **Q-C** (`HadithSubgenre.ADAB`): **PROCEED NEW-SUBGENRE-ADAB** at 3-of-4 cross-provider — al-Bukhārī's *al-Adab al-Mufrad* / Ibn Ḥibbān's *Rawḍat al-ʿUqalāʾ* / al-Khaṭīb's *al-Jāmiʿ li-Akhlāq al-Rāwī* tagged correctly via 3 compound rules (`الأدب + المفرد` / `روضة + العقلاء` / `الجامع + لأخلاق`), but EXCLUDED from carve-back (chain-preservation). All 4 evaluators UNANIMOUSLY REJECTED Q-C path-2 (KEEP-AS-JAMI-VIA-NEW-KEYWORD) — al-Adab al-Mufrad is *muṣannaf*-class in *aʿmāl wa-l-ādāb* sub-category per al-Suyūṭī's *Tadrīb al-Rāwī* Muqaddimah on *aqsām al-kutub al-muṣannafah*, NOT *jāmiʿ*-class (novel anchor — surfaced by arabic-reviewer DIM-AR1, not cited by either Gemini in FU-35). **CRITICAL naming-collision finding (CRIT-FU36-1, surfaced INDEPENDENTLY by both Codex DIM-CDX5 and arabic-reviewer DIM-AR2 AR2-QC-1):** `HadithSubgenre.ADAB` has the same string value `"adab"` as `Genre.ADAB` at contracts.py:158; display layers MUST disambiguate by enum-class context — JSON serialization without type context is ambiguous (T-1 risk). HadithSubgenre docstring documents the disambiguation. Inference-rule ordering hazard managed per Codex DIM-CDX4: ADHKAR/ADAB compound rules inserted AFTER `HADITH_COMMENTARY` branch (line 643-644) and BEFORE generic catch-alls (line 762-769) so `شرح الأذكار` / `شرح الأدب المفرد` correctly tag as HADITH_COMMENTARY. Bare `أذكار` / `ذكر` / `دعاء` / `الأدب` / `أدب` are FORBIDDEN as standalone inference triggers (preserves existing test_step_50_deliberation.py:977 assertion `كتاب الأذكار -> None`). +28 spec-linked FU-36 tests added. INV-SRC-0012 amended with AC-FU36-1 through AC-FU36-5 (ADHKAR enum exclusion + ADAB enum exclusion + Q-C path-2 JAMI-via-keyword UNANIMOUSLY-REJECTED regression guard + ADHKAR/ADAB false-positive guards via science-scope pre-condition + compound-keyword discipline + sharḥ-on-ADHKAR/ADAB HADITH_COMMENTARY ordering regression guard). REQ-SRC-0011 controlled-vocabulary extended to 19 values. Gates: validate_spec 0 errors / 112 atoms; pyright 0/0/0 on touched files (contracts.py + deliberation.py + test_followup_36_adhkar_adab.py); pytest 345 pass / 0 fail (was 317; +28 FU-36 tests); D-023 boundary warnings unchanged (5 pre-existing). Cross-provider scholarly readiness FULLY SATISFIED at 3-of-3 cross-provider HIGH for Q-B/Q-C per `.claude/rules/no-single-model-conclusion.md` (OpenAI structural Codex + Google scholarly Gemini ×2 + Anthropic scholarly arabic-reviewer); Q-A BLOCK at 2-of-4 with documented limitations honors the no-single-model-conclusion floor. Methodology improvement: separate-sealed-block-file pattern + 4-evaluator role-isolated dispatch files (sed-extracted per-evaluator content) — formalize for all future cross-provider scholarly+structural dispatches; for future dispatches, place sealed-block file at a path Geminis can Read via tool call (not blocked by `.kr/` gitignore patterns) so all 4 evaluators get the strong file-read-sequence verification rather than 2 strong + 2 partial.

**FU-37 closure summary:** arabic-reviewer Anthropic Agent retroactive validation CONVERGED on (a+b) HIGH with NOVEL classical anchor al-Suyūṭī *Tadrīb al-Rāwī* Muqaddimah on *iʿtibār* discipline (genuinely independent — not in either Gemini's verdict or the sealed prior-evaluator block). 4-of-4 cross-provider scholarly+structural convergence at HIGH confidence (Codex CLI structural + Gemini Run A/B + arabic-reviewer Anthropic Agent). Two new structural CRITICAL findings from arabic-reviewer closed by contract widening: CRIT-AR-1 (PendingLevelOverride was per-source-keyed, now carries `constituent_idx: Optional[int]`); CRIT-AR-2 (GenreDisputePosition lacked constituent identifier, now carries `constituent_idx`). Plus entrance widening: `MetadataDeliberationInput.owner_constituent_level_overrides: dict[int, WorkLevel]` accepts per-constituent owner intent for *majmūʿ* sources; orchestrator helper `_queue_constituent_overrides` validates and queues. Per-constituent overrides are ALWAYS QUEUED at intake (deferred to synthesis per DEC-SRC-0003 — synthesis owns level writes; constituent genre is unknown at intake). Container Axis 2 firing remains UNCHANGED with per-constituent overrides queued — both states coexist via dual-field architecture (singular per-source `pending_level_override` + list `pending_constituent_level_overrides`). New error code `SRC-E-LEVEL-OVERRIDE-CONSTITUENT-INVALID` for intake-boundary rejection. +22 FU-37 tests. Spec atom amendments: REQ-SRC-0047 (entrance widening + AC-7), REQ-SRC-0048 (keyspace expansion + AC-7), INV-SRC-0012 (AC-FU37-1 through AC-FU37-9), DEC-SRC-0021 (rule (vii.d) and (vii.e) for legacy migration via Pydantic field-default semantics). Methodology gap disclosure: arabic-reviewer wrapper contained sealed prior-evaluator block in-file → file-read sequence independence technically compromised; analytical independence supported by novel anchor + novel structural findings + novel framing.

**Pipeline steps implemented:** upload_receipt → freeze_and_manifest → container_classification → intake_analysis → metadata_deliberation → source_admission_and_normalization_handoff.

**What's needed next (priority order):**
1. **Phase 5 Session 3 IMPLEMENTATION (FRESH SESSION REQUIRED).** Session 1 contracts + snapshot lock LANDED at commit `fcdb03a32`. Session 2 Stage-1 deterministic narrowing LANDED at this session's commit. Session 3 implements the **Stage-2 verifier cell** that consumes Session 2's `ScholarEvidencePacket.candidate_set` and produces verifier-cell output feeding the compound-threshold disambiguation: REQ-SRC-0052 (≥2 independent verifiers + hybrid round-0 functional / round-1 adversarial-only-on-disagreement protocol + round cap = 2 per VERIFIER_ROUND_CAP constant from Session 1; INV-SRC-0016 chosen_id closure F-4 hallucination prevention via `ScholarEvidencePacket.is_chosen_id_in_candidate_set()` already in Session 1 contracts; no-new-candidates-in-round-1 closure); REQ-SRC-0053 compound 4-condition threshold (mean ≥ 0.92 AND each verifier ≥ 0.90 AND no rival within 0.07 AND ≥2-non-name floor per INV-SRC-0013 + disputed condition (e) for convergent-but-both_pass=false case + insufficient_evidence terminal); INV-SRC-0013 (≥2-non-name attribute floor: candidates must intersect with the dossier on ≥2 NON-NAME attributes — kunyah / nisba / work_title / century_active / school / geographic — to qualify for definitive routing); INV-SRC-0016 (chosen_id closure: every Stage-2 verifier emission must carry a chosen_id ∈ candidate_set OR an explicit "no-match" terminal; round-1 verifiers cannot introduce new candidates outside the locked Stage-1 packet). Implementation produces a Stage-2 verifier orchestrator function that takes a `ScholarEvidencePacket` (Session 2 output) + a verifier-pair specification (model + prompt-template + seed) and returns Stage-2 verifier records suitable for `ThresholdAudit` aggregation. Validation gates: pyright clean, pytest pass, D-023 metadata flow, Codex CLI structural review BEFORE merge per Rule 16. Expected: 1 fresh session. Sessions 4-5 unchanged: integration + 5-signal weighted-average + L-SCH-001 through L-SCH-004 closure (Session 4 rewires `compute_scholar_match_score` per OPT-4 architecture); calibration + Codex review + final commit (Session 5). **DEPRECATED Phase 5 IMPLEMENTATION (FRESH SESSION REQUIRED) — superseded by Session 1 closure:** Stage 4 atom set landed at commit `e91c142cc`; the 12 new atoms + 6 amendments are now the implementation surface. Rewrite `shared/scholar_authority/src/scholar_authority.py:166-234` `compute_scholar_match_score` per OPT-4 architecture (2-stage deterministic-then-LLM consensus). **Stage-1 deterministic narrowing function** per REQ-SRC-0051 (work-title channel + 5-component name parsing + ALLOWED diacritic+alef / FORBIDDEN taa-marbuta+Persian/Urdu normalization + compound-title decomposition شرح/حاشية/تهذيب/مختصر+base + work-title list-size guard N=3 placeholder, calibrated at impl). **Stage-2 verifier cell** per REQ-SRC-0052 (≥2 independent verifiers + hybrid round-0 functional / round-1 adversarial-only-on-disagreement protocol + round cap = 2 + INV-SRC-0016 chosen_id closure F-4 hallucination prevention + no-new-candidates-in-round-1 closure). **Compound 4-condition threshold** per REQ-SRC-0053 (mean ≥ 0.92 AND each ≥ 0.90 AND no rival within 0.07 AND ≥2-non-name floor per INV-SRC-0013 + disputed condition (e) for convergent-but-both_pass=false case + insufficient_evidence terminal). **Registry snapshot locking** per REQ-SRC-0049 (registry_release_version pinned for match-call duration; INV-SRC-0017 cross-time-inconsistency F-7 closure). **Bidi-strip ordering** per INV-SRC-0014 (3-stage strict: invisible-Unicode strip → honorific normalization → match-key construction; cites existing 28-single + 8-multi honorific list at `shared/scholar_authority/src/name_matching.py:33-99`). **Build-time enrichment lane** per REQ-SRC-0042 amended (OpenITI/Wikidata/LLM authorized at build_time only with data_provenance carrying enrichment_phase=build_time + license + training_use_permitted; runtime external lookup FORBIDDEN). **scholar_match_cell orchestration** per REQ-SRC-0008 amendment + DEC-SRC-0013 (named cell pattern extending deliberation-cell). **Provenance completeness** per INV-SRC-0015 (every emitted ScholarMatchResult carries threshold_audit + 4-predicate values + registry_release_version + verifier identifiers + prompt template hashes). **Implement 5-signal weighted-average** per SPEC §4.A.2 — closes L-SCH-001 (teacher-student missing) + L-SCH-002 (weights drift) + L-SCH-003 (docstring section reference §4.A.5→§4.A.2) + L-SCH-004 (uncalibrated weights). **Calibrate against 50-scholar gold seed** per SPEC §10 line 460. Validation gates: pyright clean, pytest pass, D-023 metadata flow, Codex CLI structural review BEFORE merge per Rule 16. Expected: 3-5 sessions for implementation density.
2. **Close FU-18 — RETRY ATTEMPT 3** (only remaining open follow-up; deferred indefinitely after retry attempt 2 produced no cross-provider 3-of-4 majority on shape choice [SHAPE-A:1 / SHAPE-B:2 / SHAPE-C:1]). Substantive convergence (4-of-4 unanimous) on existing severity tier set + supplementary mechanism + al-Suyūṭī Tadrīb anchor + hamza-by-text-stratum split is documented; only the REQUIRED-vs-OPTIONAL framing remains 3-way split. Future re-engagement options: (a) accept indefinite deferral (sufficient progress documented), (b) commission 5th evaluator dispatch with refined SHAPE-A-vs-B-vs-C question, (c) wait for downstream-engine implementation pressure to surface concrete shape requirements. NOT BLOCKING any error_condition currently.
3. **Pre-existing excerpting test failures (instructor LLM API).** test_phase2_integration.py 2 failures with instructor.core.exceptions.InstructorRetryException — verified pre-existing via git stash + re-run on baseline; NOT Phase-5-caused. Worth tracking as a separate session (instructor library dependency / API integration concern). Out of scope for current source engine work.
4. **Prune MCP inventory** — current load is ≥9 servers against the ≤5 cap in `context-management.md`. Owner-action-only relay already produced at `~/.claude/projects/C--Users-Rayane-Desktop-kr/memory/mcp_pruning_owner_relay_20260429.md`. Reclaims context budget for SPEC rules, Arabic handling, D-023 semantics.

**Paused work (preserved checkpoints):**
- **Excerpting:** frozen at 1008 pass, 0 fail, 4 xfail. Budget EUR 36.70 / 100.00. Checkpoint: `reference/handoffs/excerpting_pause_checkpoint_2026-04-08.md`. Do not resume until source engine reaches Phase 5 readiness.
- **Owner-facing visual representations** (mermaid diagrams, architecture maps): next-next focus after source engine solidifies. Do not start until deferred SPEC atoms are closed.

## ARCHIVED EXCERPTING FRONTIER (paused 2026-04-08)

---

## AUTONOMOUS OPERATIONS — READ FIRST

**You are the control tower.** The owner is your client, not your project lead. He is available for exactly 4 things:

1. **DR relay** — pasting prompts into ChatGPT/Claude/Gemini DR windows (physical action you cannot perform)
2. **Owner-preference questions** — "does this excerpt serve your study?", "good / bad / confusing?"
3. **Plan approval at formal gates** — Ijazah Lock 4, Phase transitions, protocol amendments
4. **Providing new materials** — collection bundles, source files

**For EVERYTHING else, you decide and execute:**
- Session type → gate-precedence matrix (§1.6) decides. Do NOT ask the owner.
- Next step → this file's roadmap + protocol determine it. Do NOT ask "what should I do?"
- Technical approach → you + coworkers (Codex, Gemini, DR) decide. Owner cannot answer these.
- Quality assessment → you + coworkers evaluate. Owner catches reading-experience issues only.
- Error detection → coworkers + scripts catch errors. Owner should NEVER be the one finding gaps.

**After every milestone:** Report what you accomplished (past tense), what you decided, and what you're doing next (already starting). If you need owner input, ask ONE specific non-technical question. Then continue working — do not stop.

**This directive applies to ALL agents:** CC sessions, Codex overnight, Gemini CLI, dispatched subagents. No agent may wait for owner guidance on technical matters.

---

## IMMEDIATE STATE (updated 2026-04-07 — Session 17 COMPLETE: Campaign evaluation on taysir, 6/6 coworkers done)

### Session 14 — Autonomous System Execution (2026-04-07)
- **All 4 Session 13 next-steps EXECUTED:**
  1. ✅ **Phase 0 infrastructure built:** `autonomous_schemas.py` (10 Pydantic models, JSONL I/O), `research_gap_scanner.py` (4 scanners: SPEC OPEN, limitations, taxonomy, calibrated), `process_dr_response.py` (section extraction, finding classification, KB persistence). Directory: `overnight_codex/autonomous/knowledge_base/`. All pyright-clean.
  2. ✅ **OQ-001-004 RESOLVED in SPEC §6.18-6.23:** All 4 [OPEN] markers converted to [CALIBRATED] with DR37's concrete fiqh cases. OQ-001: ثمرات الخلاف test (5 Hanafi/Shafi'i calibration cases). OQ-002: 7 significance criteria (4 new from DR37: استقلال المبنى, تغيّر الفنّ, البناء على أصل, قصد الإفادة). OQ-003: 3-principle context-fill test (أمن اللبس, المعلوم من السياق, البناء على الأصل). OQ-004: 3-layer analysis authority model (preserve structure, semantic tagging override, cross-disciplinary indexing).
  3. ✅ **Batch 2 DR relay queue generated:** 10 prompts (5 aqidah, 3 sarf, 1 balagha, 1 cross-science) targeting Gemini DR for taxonomy tree research gaps. File: `docs/autonomous-system/dr_relay_queue_batch_2.md`.
  4. ✅ **DR33 framework corrections applied:** 6 amendments (critical path RT-03 start, RT-13 split into 13a/13b, scholarly allocation 22%→28%, imla' 250+→80-120, 6 topics pre-advanced to ACTIVE/DEEP, simplified TSI proxy).
- **Tests:** 942 passed, 4 xfailed. All pyright clean.
- **Budget:** EUR 0.00 this session (all deterministic).
- **4-source verification COMPLETE:** CC Code (Anthropic), CC Scholarly (Anthropic), Codex CLI (OpenAI), Gemini CLI (Google). All PASS. 24 findings found and fixed.
- **4 commits:** `e9cdccba4` (core), `546088e11` (DR28 refactoring), `2e6acff5b` (state), `cedde2645` (infra).

### Session 17 — Campaign Evaluation COMPLETE (2026-04-07)
- **HIGHEST PRIORITY GATE ANSWERED:** The pipeline produces good school handling, scholar identification, and cross-school detection. But it has 3 systematic defects: numbered-list fragmentation, pronoun-based SC misrating, and missing OCR detection.
- **10 taysir excerpts deep-evaluated** against 22 FPs + 23 domain rules + 4 DR37-calibrated thresholds
- **6/6 coworkers complete:** CC Arabic Reviewer (Anthropic), CC Structural (Anthropic), Gemini CLI (Google), Codex CLI (OpenAI), ChatGPT DR (OpenAI), Claude DR (Anthropic). 3-provider diversity.
- **Final verdict: 4 PASS, 3 ADVISORY, 3 FAIL**
- **5 CONFIRMED findings:**
  1. **Numbered-list fragmentation (CRITICAL):** 568 excerpts (44.3%) follow numbered-list patterns; 191 (14.9%) below MV-1 25-word floor. Root cause: `merge_micro_units()` (phase3_deterministic.py:170) only handles structural openers/closers, not MV-1 content pass. ChatGPT DR confirms: merge by default, standalone only when semantically independent.
  2. **SC misrating on pronoun suffixes (HIGH):** 82 excerpts (6.4%) rated FULL with unresolved ها/هم/هما. Claude DR: use Farasa (98.9% accuracy) or CAMeL Tools for clitic segmentation + antecedent checking.
  3. **FR-1 gate inappropriate for sharh (HIGH):** Claude DR: "A percentage-of-words heuristic should not govern splitting decisions" for def+proof+attr units. Al-Ghazali + Ibn Taymiyyah methodology demands unity. Exempt IC-1 intertwined content from FR-1 percentage gate.
  4. **OCR word corruption undetected (MEDIUM):** 2 instances in Sample 7 (مال روى, برواتها). Gemini CLI caught what CC missed. Add OCR word-corruption detector to arabic_fidelity_flags.
  5. **المعنى الإجمالي (RESOLVED — LOW):** Arabic reviewer + Gemini said FAIL; Claude DR said variable classification is CORRECT (container, not label). Resolution: add `structural_section` facet, audit the 13 classified as `definition`.
- **Report:** `integration_tests/campaign_20260331/taysir/CAMPAIGN_EVAL_SESSION16.md`
- **DR archives:** ChatGPT DR at `downloads/deep-research-report (19).md`, Claude DR at `downloads/compass_artifact_wf-ae430a21-...md`
- **Budget:** EUR 0.00 this session (evaluating existing data)

### Session 21 — DR40 Smoke Test + MV-1 Merge Conflict Fix (2026-04-08)

**DR40 split rules work correctly in LLM Phase 2b — but Phase 3 MV-1 merge was destroying them. Fixed.**

**Smoke test findings:**
- **كتاب الطهارة smoke (7 excerpts):** DR40 companion_definition link emitted correctly on النية definition pair. One inaccurate link target description (MEDIUM — enrichment error, not structural). Evidence splitting NOT triggered (correct — no multi-type evidence in this chapter).
- **كتاب الطلاق smoke v1 (11 excerpts):** Phase 2b (LLM) correctly split the definition pair (لغة/شرعا) AND evidence types (Quran/Sunnah/Ijma) into separate units with relationship links — EXACTLY matching the owner's rejected output expectations. BUT Phase 3 merge_subviable_units() merged ALL 6 split units (7-20 words each) back into one 172-word mega-excerpt, undoing the LLM's correct work.
- **Root cause:** MV-1 (25-word floor) treats any unit < 25 words as a fragment to merge. DR40 split rules intentionally produce sub-25-word units (a 7-word Quranic citation is a complete teaching unit when linked to its ruling). MV-1 had no exemption for relationship-linked units.

**Fix applied:**
- `phase3_deterministic.py` line 385: added `and not u.related_units` exemption alongside existing isnad exemption
- 2 new regression tests: `test_related_units_preserved_despite_subviable` (definition pair), `test_evidence_split_units_preserved_despite_subviable` (evidence types)
- Fixed pre-existing pyright errors in test file (missing `Optional` import, `TeachingUnit` import)
- **1008 tests, 0 failures, 4 xfailed. All pyright clean.**

**Talaq smoke v2 running** with fix applied — expected to produce ~20 excerpts instead of 11.

**Integration test runner:** Added `--div-id` argument to `scripts/run_integration_test.py` for targeting specific divisions without processing the entire package.

**Coworker dispatch prompts prepared** (via /prompt-architect): Gemini CLI (Arabic scholarly accuracy of split rules) + Codex CLI (structural/contract review). Awaiting dispatch.

**Session 21 completion (second commit `baab068ac`):**
- Talaq v2 confirmed: 20 excerpts (vs 11), evidence types split, 6 relationship links, 0 structural issues
- Gemini CLI: 1 CONFIRM, 3 AMEND (SPEC §6.24/§6.25 updated), 1 FLAG
- Codex CLI: 2 ISSUE (inbound-only fixed via linked_targets, chain-remap tracked), 6 PASS
- Codex-verify: 3 CC reviewers all PASS, 1 HIGH fixed, 2 MEDIUM fixed
- Prompt exemptions (d) composite proof and (e) cross-type interdependence added to prompts.py
- **1008 tests, 0 failures, 2 commits: `7493562fa` + `baab068ac`**

**Session 22 — Handoff to Codex (CC weekly limit reached)**

**COMPLETED (Session 22, CC):**
- ✅ Excerpt review UI: added related_units rendering (commit `91a860fbe`)
- ✅ 3-reviewer verification: 2 CRITICAL + 2 HIGH fixed (commit `b08b2c2fb`)
- ✅ Smoke test: `eval_session22_talaq/` — 21 excerpts, 0 errors, 0 gates (owner ran)
- ✅ Owner confirmed: eval_session22_talaq is "much better" than dr40_smoke_talaq_v2
- ✅ Review server working: `python tools/review.py integration_tests/review_session22/` on port 8385
- ✅ Authority transferred to Codex (ACTIVE_AUTHORITY.md updated)

**OWNER ACTION — Start reviewing excerpts:**
```
python tools/review.py integration_tests/
```
Opens browser → select `dr40_smoke_talaq_v2` → review 20 excerpts → mark ACCEPT/NEEDS WORK/REJECT with comments. Feedback saves to `integration_tests/dr40_smoke_talaq_v2/owner_feedback.jsonl`.

**CODEX NEXT STEPS (authority: codex as of 2026-04-08):**
1. ~~Run fresh smoke test~~ ✅ Done: `integration_tests/eval_session22_talaq/` — 21 excerpts, 0 errors
2. **Owner is reviewing excerpts in the UI.** After review: read `integration_tests/review_session22/eval_session22_talaq/owner_feedback.jsonl`, analyze verdict patterns, translate NEEDS WORK/REJECT feedback into pipeline improvements
3. **Pick 2-3 diverse chapters** for generalization testing — one from a different kitab, one hadith-heavy, one with cross-madhab debate. Use: `python scripts/run_integration_test.py --package-path experiments/format_diversity_test/packages/taysir/ --output-dir integration_tests/eval_<name> --div-id <div_id> --backend api`
4. **Coworker dispatch** on any pipeline changes (Gemini CLI for Arabic scholarly accuracy)
5. **Review server:** `set KR_REVIEW_PORT=8385 && python tools/review.py integration_tests/review_session22/` — copy new outputs into `integration_tests/review_session22/` for owner review

**Branch:** `excerpting-foundations-hardening-20260404`
**Tests:** 1008 pass, 0 fail, 4 xfail
**Budget:** EUR 36.70 / 100.00 (63.30 remaining)

### Session 20 — DR40 Granularity Calibration Implementation (2026-04-08)

**All 5 DR40 decisions implemented: SPEC + contracts + prompts + tests. Owner feedback gap CLOSED.**

**Changes:**
- **SPEC FP-13 re-ranked:** Leaf-atomicity promoted to #4, pedagogical packaging demoted to #5 (UI concern)
- **3 new foundational principles:** FP-23 (relationship links), FP-24 (conditional evidence splitting), FP-25 (definition pair splitting)
- **2 new domain rules:** §6.24 (DP-SPLIT-1 definition pairs), §6.25 (EV-SPLIT-1 evidence type splitting)
- **PS-1 proof structure amended** for FP-24 alignment
- **Contracts:** `RelationshipType` enum (3 values), `UnitRelationship` model, `related_units` on TeachingUnit + ExcerptRecord
- **Prompts:** CONSTITUTION precedence stack, GROUP_CORE_RULES conditional evidence, GROUP_FIQH_RULES definition pair + evidence type splitting, GROUP_OUTPUT_FORMAT related_units, GROUP_CRITICAL_REMINDERS
- **Phase 3 propagation:** related_units flows through deterministic assembly and both merge functions
- **DEFINITION now triggers GROUP_FIQH_RULES** in compute_active_modules (FP-25)
- **CR-31 registered** in CONSTRAINT_REGISTRY.md (≤15 word parenthetical exemption — UNCALIBRATED)
- **18 new regression tests** from owner rejections — 1006 total, 0 failures, 4 xfailed
- **Budget:** EUR 0.00 (all deterministic)

**Immediate next steps:**
1. ~~**Smoke test** the taysir talaq chapter with updated prompts~~ ✅ Done (Session 21)
2. **Dispatch coworkers** — Gemini CLI for Arabic scholarly accuracy of split rules, Codex CLI for contract review
3. **Full campaign rerun** to measure impact on all 1,491 excerpts

### Session 19 — Campaign Rerun Analysis + CRITICAL FEEDBACK GAP DISCOVERED (2026-04-08)

**Campaign rerun validated all 5 structural fixes. But owner feedback from Session 17 baseline was never consumed — the core excerpting quality problem (grouping granularity) is untouched.**

**Campaign rerun metrics (1,491 excerpts vs 1,283 baseline):**
- Sub-MV-1 (<25w): 244 → **0** (PERFECT — target met)
- Pronoun/anaphora flags: 0 → 23 (1.5%) — detector working
- Content intertwined flags: 0 → 728 (48.8%) — IC-1 detector working, rate reasonable for sharh fiqh
- Isnad preservation: 16 → 28 — chains kept atomic
- Self-containment FULL: 68.7% → **85.4%** (+16.7pp)
- Avg word count: 74.8 → 123.0 (merged sub-viables shifted distribution up)
- Run time: ~4.4 hours at concurrency=1. 10 chunk failures (8 classify, 2 group). 17 verification_skipped in div_7_006.

**10 Gemini DR Batch 2 responses ingested and synthesized:**
- All 10 provide actionable taxonomy decisions. 7/10 recommend expanding or separating nodes.
- Key: nahw/sarf boundary rules, verb derivation vs tense separation, أعمال القلوب expand to 10-12, فهم السلف/إجماع separate, السحر/الكهانة separate, الأسماء والصفات needs 30-35 leaves not 20.
- Full synthesis: see session 19 conversation log.
- Archived at: `reference/dr_reviews/batch2_gemini/DR_B2_01` through `DR_B2_10`.

**CRITICAL FINDING — Owner feedback gap:**
- Owner reviewed 2 excerpts from baseline run (2026-03-31) in `integration_tests/campaign_20260331/taysir/owner_feedback.jsonl`. Both REJECTED with detailed reasoning about grouping granularity being too coarse.
- **3 consecutive sessions (17, 18, 19) saw the pointer in NEXT.md line 823 and none opened the file.**
- The campaign rerun produced the rejected excerpt (talaq definition) BYTE-IDENTICAL to the baseline — the 5 Session 18 fixes addressed structural defects, not grouping quality.
- 13.4% of excerpts (200 `_pre_` chunks) bypass LLM grouping entirely.

**Core systemic issue identified (3 layers):**
1. **No feedback loop** from owner output-quality reactions back to pipeline behavior. Abstract feedback (questionnaire) has a pipeline. Concrete feedback (output reactions) does not.
2. **Granularity calibration untested.** FP-9 (anti-overgranulation) + FP-13 (granularity priority #5) push the pipeline toward "keep together." Owner's actual reaction: "too broad — just cutting up book pages." These rules came from F8 about taxonomy trees, got over-applied to excerpting boundaries.
3. **`_pre_` chunk bypass.** 200 excerpts from small divisions skip LLM grouping — no function-level analysis happens on them.

### Session 19 — Next Steps (CRITICAL PATH)

**Priority order:**

1. **DR on granularity calibration + feedback loop design** (OWNER ACTION: relay to ChatGPT DR or Claude DR)
   - Core question: "What is the right excerpting granularity for a comparative Islamic scholarly library — one scholarly function per excerpt, or coherent teaching paragraphs — and how should owner feedback on real output systematically feed back into pipeline behavior?"
   - Must address: FP-9/FP-13 recalibration, `_pre_` chunk bypass, owner rejection trace-back mechanism
   - Include owner_feedback.jsonl content (both reviews) as concrete examples

2. **Build owner feedback consumption pipeline**
   - Every session that touches excerpting MUST read `owner_feedback.jsonl` before doing any evaluation or excerpt selection
   - Owner rejections must trace back to specific pipeline decisions (Phase 1 assembly? Phase 2 grouping? _pre_ bypass?)
   - This should be a hook, not documentation

3. **structural_section enrichment prompt** — field exists but unpopulated (deferred from Session 18)

4. **Taxonomy tree amendments from Batch 2 DRs** — 10 decisions ready for implementation (2-3 sessions)

### Session 18 — 5 Fixes IMPLEMENTED + 3-Source Review HARDENED (2026-04-08)

**All 5 Session 17 findings implemented, then independently verified by 3 reviewer agents (code-reviewer + arabic-auditor + architect). 5 additional issues found and fixed in the same session.**

**7 commits, 991 tests passing:**
1. ✅ `ad455a4` — MV-1 sub-viable merge pass (`merge_subviable_units()`, 9 tests)
2. ✅ `1416200` — Pronoun-suffix SC validation (V-P3-10, 6 tests)
3. ✅ `f27b0e6` — IC-1 content_intertwined flag (2 tests)
4. ✅ `b9b65d8` — StructuralSection enum + field
5. ✅ `963bd49` — OCR word-corruption detector
6. ✅ `04c4c00` — **3-source review fixes:** char-offset bug (use _word_to_char_range), isnad chain protection (_ISNAD_MARKERS), pronoun ه false-positive removal, antecedent marker cleanup, EX_M_012→review_flag
7. ✅ `658b997` — structural_section TODO in enrichment

**3-source review findings (all resolved):**
- Code Reviewer: char-offset arithmetic fails on multi-space (HIGH→FIXED), missing trailing test (HIGH→FIXED), pronoun ه false positives (HIGH→FIXED)
- Arabic Auditor: isnad splitting risk (CRITICAL→FIXED), root-final ه vocabulary (WARNING→FIXED), الله/ابن/أبو antecedent suppression (WARNING→FIXED)
- Architect: pronoun check should be review_flag not error code (HIGH→FIXED), structural_section dead field (MEDIUM→TODO added)

**Batch 2 DR dispatched:** 10 Gemini DR prompts relayed and researching (2026-04-08).

### Session 18 — Next Steps (HANDOFF TO NEXT CC SESSION)

**Priority order:**

1. **Campaign re-run on taysir** (~€2.93 via API)
   - Validates 191→0 sub-MV-1 and 82→0 pronoun misrating targets empirically
   - Must use same 5 packages (ext_39_masala, ext_46_qa, ibn_aqil_v1, ibn_aqil_v3, taysir)
   - Compare against Session 17 baseline: 4 PASS, 3 ADVISORY, 3 FAIL → expect improvement

2. **Batch 2 DR intake** — 10 Gemini DR responses to process
   - Archive each response, extract findings, synthesize
   - Topics: hadith isnad boundaries, sharh layer detection, mashyakha handling, nahw parsing, aqidah classification, tafsir verse detection, qa format detection, fiqh madhab attribution, poetry detection, manuscript colophon parsing

3. **structural_section enrichment prompt** — the field exists (contracts.py) but enrichment prompt doesn't populate it
   - Add to UnitEnrichment schema
   - Update ENRICH prompt to classify structural_section
   - Wire into phase3_enrichment.py model_copy

4. **MV-1 corpus-specific calibration** — the 25-word floor was calibrated on taysir (fiqh). Arabic-auditor flagged: hadith collections have 15-20 word isnads that are legitimate standalone units. When processing hadith texts, the floor may need adjustment. Tracked in CONSTRAINT_REGISTRY CR-29.

### Session 15 — DR28 Prompt Architecture COMPLETE + 6-Source Verification (2026-04-07)
- **DR28 IU-6/IU-7/IU-8/IU-9 implemented:** CLASSIFY and ENRICH refactored to 2-message architecture (system=CONSTITUTION, user=rules+input+reminders). SPEC §5.2.2/§5.2.3/§5.3.2/§5.3.3/§7.2.2/§7.2.3 updated.
- **6-source multi-provider verification COMPLETE:** CC Code Reviewer (Anthropic), Gemini CLI ×2 (Google), Codex CLI (OpenAI), CC Arabic Auditor (Anthropic), CC Architecture Auditor (Anthropic). 10 findings found, all resolved.
- **Key fixes from review:** Instruction sandwich preserved on retry (error feedback inside `<error_correction>` before `<critical_reminders>`), GROUP cache key mismatch fixed, CLASSIFY reminder improved with derived-rulings rule per Gemini suggestion, SPEC §7.2.2 narrator role + confidence threshold synced to code.
- **Tests:** 971 passed, 4 xfailed. pyright clean.
- **Commits:** `546088e11` (DR28 refactoring), `eb88f611d` (6-source review fixes).

### Session 16 — Autonomous Dashboard BUILT (2026-04-07)
- **Dashboard operational:** `python scripts/dashboard.py` → localhost:8000
  - 4 pages: DR Relay Queue (10 Batch 2 prompts), Findings (38 from DR37), Ideas (form → ideas.jsonl), Status (aggregate stats)
  - FastAPI + HTMX + Jinja2, dark theme, one-click prompt copy, sidebar nav
  - Data layer reads existing JSONL files via autonomous_schemas.py Pydantic models
  - Files: `scripts/dashboard.py`, `scripts/autonomous_dashboard/{app,store,__init__}.py`, `scripts/autonomous_dashboard/templates/{base,relay,findings,ideas,status}.html`
  - Seeder: `scripts/seed_batch2_prompts.py` (already run, 10 prompts in knowledge_base/dr_prompts/batch_2.jsonl)
- **Tests:** All smoke tests pass (4 pages render, idea submission persists, real data displays).

### Next Steps (for next CC session)
  1. ✅ **Campaign evaluation on taysir** — Session 17 COMPLETE. 5 confirmed findings.
  2. ✅ **Implement all 5 fixes** — Session 18 COMPLETE. 7 commits, 991 tests, 3-source review.
  3. ✅ **Campaign re-run** — Session 19. All 5 structural fixes validated. But core grouping quality untouched.
  4. ✅ **Batch 2 DR intake** — Session 19. All 10 Gemini DRs synthesized. 10 taxonomy decisions ready.
  5. **CRITICAL: DR on granularity + feedback loop** — See Session 19 Next Steps. Owner commissioning.
  4. **Owner relay: Batch 2 DR prompts** — 10 Gemini DR prompts ready in dashboard at localhost:8000 AND at `docs/autonomous-system/dr_relay_queue_batch_2.md`.
  5. **IU-10: A/B test monolithic vs progressive** — ~EUR 10 budget. Validates DR28 empirically.

### Session 13 — Autonomous System Design + DR Processing (2026-04-07)
- **DESIGN.md written + 2 design reviews + 12 amendments applied**
- **8 DR prompts relayed, ALL 8 responses received and archived (DR32-39):**
  - DR32 (ChatGPT): Dashboard FastAPI+HTMX (4.75/5), 6-stage response pipeline, Idea Quarry creative framework
  - DR33 (Claude): 20 research topics (RT-01 to RT-20), 3-phase strategy, TSI saturation index, critical path 35-45 days
  - DR34 (Gemini): Hadith isnad-matn boundaries — 7 new patterns beyond existing rules
  - DR35 (ChatGPT): Passaging engine gap analysis + hardening priorities
  - DR36 (ChatGPT): Multi-layer sharh/hashiyah detection patterns
  - DR37 (Gemini): OQ-001-004 calibration — 5 fiqh cases, 4 new significance criteria, context-fill principles
  - DR38 (Gemini): 18 sciences — 54 DR questions, 10 ranked edge cases, completeness criteria
  - DR39 (Claude): Taxonomy "no brain" — LLM adapter not built, gold baseline 100% invalid, 10 priorities
- **4 coworker reviews COMPLETE (2 design + 2 DR validation):**
  - Structural: dashboard PASS, critical path corrected (starts RT-03 not RT-01), 6/20 topics partially answered, no embedding infra for TSI
  - Scholarly: allocation 22%→28-30%, RT-13 must split (Quran vs hadith), imla' 250+→80-120, RT-06/07 co-dep = tanzil al-'ilm
- **5 confirmed decisions:** Dashboard FastAPI+HTMX, 20-topic research framework, taxonomy LLM adapter Priority 1, OQ-001-004 resolved by DR37, genre-prioritized hardening

### Session 11 — D3 Full Intake + Coworker Review (2026-04-07)
- **D3 intake:** Read ALL 22 files (97 atomic records). Session 10 only read 8/22.
- **3 gaps found and filled:** School-specific branching (§6.21), pre-excerpt structural analysis (§6.22), attribution coupling rules (§6.23)
- **2 existing sections amended:** §6.18 LP-1 ([OPEN] marker), §6.19 PO-1 (attribution-coupling direction + [OPEN])
- **10 adversarial tests added:** ADV-E-13 through ADV-E-22
- **Coworker review COMPLETE (2 CC subagents):**
  - **Code reviewer:** 0 CRITICAL, 0 HIGH, 3 MEDIUM (all fixed: AC-1→FR-1 link, ADV refs, NN-008 explicit)
  - **Arabic reviewer:** 1 CRITICAL (fixed: الكلالة example misframed — Hanafi dissent is phantom, all 4 madhabs agree), 5 warnings (all fixed: consensus weight, AP-003 domain grounding, phantom عند الحنابلة removed, fixture refs added)
- **All findings addressed.** SPEC sections are now CONFIRMED (2-source reviewed).
- **Campaign evaluation plan ready:** `engines/excerpting/reference/CAMPAIGN_EVAL_PLAN_SESSION11.md` — 10 sample excerpts extracted from taysir
- **Key campaign finding:** 46% of definition excerpts contain embedded proof indicators — D3 rules are directly relevant to real data
- **Tests:** 942 passed, 4 xfailed, 0 failures. SPEC: 2859 lines.
- **Next:** DR28 prompt architecture (IU-1 through IU-5), then campaign evaluation on 10 taysir samples.

### Pipeline Visual Architecture (2026-04-07)
- **Created:** `docs/architecture/pipeline_diagrams.md` — 4 Mermaid diagrams (pipeline overview, data flow, excerpting internals, source internals)
- **Changelog mechanism:** CHG-NNN entries at bottom of file — update when engine status, contracts, or architecture changes
- **Renders on:** GitHub, VS Code (Mermaid extension), any Mermaid-compatible viewer

### DR29-DR31 Processing Session (2026-04-07) — 3 Deep Research Reports
- **DR29 (ChatGPT):** Strategic audit of excerpting improvement portfolio. 15 ranked items. **8/8 code claims verified against source.** Highest-accuracy DR to date.
- **DR30 (Claude):** 19 silent failure modes in overnight system. **Core assumptions wrong** — claimed no atomic writes exist (they do), claimed SBERT dedup (it's slug-based). Valid finding: missing `os.fsync()` in atomic_write.
- **DR31 (Gemini):** Autonomous template evaluation for Islamic texts. 8 existing templates scored avg 1.6/5 on Islamic scholarly grounding. 6 new templates proposed. Pending Codex CLI structural review.
- **6 code fixes implemented (917 pass):**
  1. `filter_relevant_footnotes` multi-occurrence bug fixed (while-loop instead of single find())
  2. `text_snippet` now deterministic (`primary_text[:80]` not LLM-supplied)
  3. V-P3-2 short-text policy — micro-units no longer auto-dropped
  4. Evidence markers expanded: hadith 6→14, ijma 5→9
  5. EX-M-011 added to SPEC error catalog (was contracts-only)
  6. `os.fsync()` added to overnight `atomic_write()`
- **Deferred:** `review_flags` placeholder refactoring (large blast radius — needs coworker validation before changing I-ER-4 model validator)
- **Coworker reports processed (2/2):**
  - Codex CLI: DR31 templates — T4+T6 COMPATIBLE, T1/2/3 NEEDS_ADAPTATION, T5 INCOMPATIBLE (requires Arabic judgment)
  - Gemini CLI: DR29 #4 USUALLY_MERGE (bidirectional: forward for openers, backward for closers). DR29 #8 minimum-viable takhrij = 4 required fields (hadith_anchor, sources, locator, provenance)
- **Micro-unit merge pass implemented (931 pass, +16 tests):**
  - `merge_micro_units()` in phase3_deterministic.py — bidirectional merge per Gemini scholarly validation
  - Called from phase3_orchestrator before build_deterministic_excerpts
  - Bare openers forward-merge, bare closers backward-merge, semantically-complete headings exempt

### Memory System Upgrade (2026-04-07) — 6-Source Investigation + 3-Layer Implementation
- **Trigger:** Owner challenged dismissal of mempalace → full 6-source investigation launched
- **Sources:** DR25 (Claude DR — critical audit), DR26 (ChatGPT DR — architecture design), DR27 (Gemini DR — Islamic scholarly traditions), Gemini CLI (domain validation), Codex CLI (structural verification), CC direct measurements
- **Architecture decided:** 4-layer system. Graph DB and mempalace permanently killed by domain expert.
- **Layer 1 DEPLOYED:** AGENTS.md expanded 465B→8KB with Arabic scholarly conventions. @AGENTS.md import in CLAUDE.md. Codex overnight now reads curated conventions.
- **Layer 2 DEPLOYED:** `generate_memory_index.py` auto-generates MEMORY.md (154→102 lines, 6 broken YAML files recovered). `check_invariant_consistency.py` detects doctrine drift + Arabic invariants. Fixed 5-vs-7 engine contradiction.
- **Layer 3 DEPLOYED:** `session_stop.py` appends JSONL events to `memory/events/` with provenance (Sanad principle).
- **Layer 4 DEFERRED:** SQLite FTS5 when corpus outgrows grep.
- **Gemini CLI review:** Identified 3 HIGH findings (all fixed), 3 MEDIUM deferred, 3 LOW deferred. CC-first rating: 5/10 retrieval, 5/10 domain, 1/10 student learning (by design — pipeline-first).
- **Remaining:** Codex CLI review pending. Kunnash/Ishkalat/Bridge Mechanism are post-pipeline features.
- **DRs archived:** DR25, DR26, DR27 + Codex crossref in `engines/excerpting/reference/dr_reviews/`

### Session 8 Accomplishments (2026-04-07) — Debt Clearance
- **B2/B3 CONFIRMED (2/2 coworkers):** Gemini CLI + Codex CLI reviewed all 12 atoms. Zero true contradictions — dimensional complementarity. 3 Tier-1 prompt changes + 7 Tier-2 SPEC sync items identified → Session 9.
- **12 SOFTENED items RESOLVED:** 11 accept-as-is, 1 ledger update. BCV Session 4 debt CLEARED.
- **Highest risk found:** B3-SP1 (scholar-quoting-scholar) — no SQ-1 protocol in SPEC, 80% rule can flip authorship.
- **917 tests pass**, prior session audit PASS.

### Session 3 Accomplishments (2026-04-06)
- **Protocol v5.0 COMPLETE** — Batch Lifecycle Protocol: §3A (6-phase model), §3B (Completion Gate), §3C (Ijazah Ceremony), §4.18 (Regression Gate), §4.19 (Doctrine Coherence), §5.8 (Role Separation), §8.5 (Calibration File), §0.1 (Autonomous Operations Doctrine)
- **12 scripts built** (S-01 to S-12): 8 batch verification + 4 norm enforcement
- **3 PreToolUse hooks** for hard enforcement: enforce-autonomy.sh, enforce-prompt-architect.sh, track-prompt-architect.sh
- **DR17-DR19 processed**: manuscript verification scholarly grounding, norm decay research, hard enforcement architecture
- **HR-23 to HR-26 added**: mandatory prompt-architect, lint before session end, hooks never disabled, cross-model auditing
- **915 tests pass**, all checks green

### Session 4 BCV Complete (2026-04-07)
- **First BCV on F1-F8**: 139 files verified, 208 MCUs traced, 94.7% MAPPED, 5.8% SOFTENED, 0% MISSED
- Gate script bug found and fixed (META terminal state)
- 12 SOFTENED items documented for debt clearance

### Session 10 Accomplishments (2026-04-07) — Dedup Reconciliation + SPEC Debt Clearance

- **MAQ dedup COMPLETE:** All 80 actionable atoms reconciled against SPEC/code. Key finding: B4/B5 "SPEC-ONLY" was disposition tag not implementation status — 10 atoms had classified dispositions but no SPEC text. All 10 now written. SPEC-PENDING: 0.
- **10 SPEC additions written:**
  - FP-7 strengthened: hadith variant-mismatch risk (MAQ-056/072)
  - FP-8 strengthened: attribution-critical tarjih + clipped tarjih prohibition (MAQ-053/054)
  - §6.11 FN-1: Footnote handling protocol (MAQ-071)
  - §6.12 IM-1: Interleaved methodology awareness (MAQ-069)
  - §6.13 HR-1: Hukm-return visibility (MAQ-038)
  - §6.14 FR-1: Forgiving rule ~33% quantitative limit (MAQ-036)
  - §6.15 CS-1: Configuration-sensitivity audit trigger (MAQ-042)
  - §6.16 TE-1: Theory-example vs practice-example (MAQ-048)
  - §6.17 IC-1: A×B intertwined content protocol (MAQ-050)
- **Codex CLI Session 9 results processed:** 5 PASS, 1 MEDIUM (already fixed). No blockers.
- **Reconciliation doc:** `engines/excerpting/reference/DEDUP_RECONCILIATION_SESSION10.md`
- **Reconciled totals:** 37 implemented, 22 covered, 0 SPEC-pending, 10 deferred, 3 open, 8 merged, 4 captured
- **Tests:** 937 passed, 4 xfailed, 0 real failures. Prompt-SPEC sync: PASS.
- **Budget:** EUR 0.00 this session (all deterministic). Total: 36.70/100.

### D3 Intake (2026-04-07) — LAST Questionnaire Question

- **D3 "Multi-Layered Definition"**: 22-file ChatGPT bundle processed. Owner case study: الكلالة with definition/proof/attribution layers.
- **3 new SPEC sections:** §6.18 LP-1 (leaf pollution prevention), §6.19 PO-1 (packaging ≠ ontology), §6.20 SH-1 (source hints non-deciding)
- **2 documented (not hardened):** pre-excerpt deep analysis (arch question), significance threshold calibration (needs more cases)
- **Q&A HARDENING PHASE COMPLETE.** All questionnaire answers (F1-F8, G1-G4, SC1-SC3, D3) processed.

### What's Needed Next

1. **Evaluate existing campaign data (HIGHEST PRIORITY):** The $97 campaign (2,303 excerpts from 5 books, 2026-03-31) has never been evaluated against the hardened SPEC. Pick 1 book. CC + coworkers evaluate every excerpt against 22 FPs + 20 domain rules. Surface only study-experience questions to owner. This proves whether the doctrine translates to reality.
2. **DR28 prompt architecture:** Instruction sandwich + progressive disclosure (8-12 rules per call from 25). Synthesis at `engines/excerpting/reference/dr_reviews/DR28_synthesis.md`. Restructure all 3 prompts. Addresses Gemini's 2 PRELIMINARY CHALLENGEs.
3. **3 OPEN design questions need DR:** MAQ-074 (chapter-intro marking), MAQ-075 (EE-1 hadith exceptions), MAQ-077 (non-taxonomic guidance).
4. **Section K red-team tests:** 62 tests to automate as pytest cases.
5. **Deferred:** review_flags placeholder refactoring, DR31 Templates, Book Resolution session

### PARALLEL WORKSTREAM: 3-Month Feedback Collection Strategy (2026-04-07)

**Goal:** Design the optimal system for collecting ALL owner-dependent data before July 1 (summer full-time build phase).

**Accomplished (this session):**
- Owner interview (4 rounds): study priorities (Arabic→fiqh→usul→aqidah), fatigue profile (prefers structured/interactive), granularity is #1 excerpt issue, product vision ("present everything, tell me just memorize")
- 5 coworkers dispatched with /prompt-architect-optimized prompts (**4/5 received**, 1 pending)
- **DR18 (Claude DR):** 42 owner-dependent decisions across all 5 engines. Critical path: science scope → book priority → muhaqiq list. ~5h tedious now, ~20-30h summer.
- **Codex CLI:** 11 policy families (DT-01..11) with dependency chain. Root: user model. Two-layer insight: policy precedes decisions. Only FP-8/FP-18 need calibration. TEAM_TRANSLATION_GUIDE has zero FP-13..22 mapping.
- **Gemini CLI:** Student-first pedagogical analysis. 9 unique findings including FP-1 challenge (qa'idah+shahid separation for flashcard mode), shubuhat safety, genre overrides, 2 genuine gaps (cognitive complexity grading, active recall output format).
- **ChatGPT DR:** Only coworker to inventory what's ALREADY COLLECTED. 5 missing data families from campaign evidence. Bundle format evaluation (4 weaknesses, 3 additions). Error classification by owner-dependency.
- All 4 reports: saved to `engines/excerpting/reference/dr_reviews/`, verified against codebase, cross-referenced, corrections documented
- **PRELIMINARY 4-COWORKER SYNTHESIS COMPLETE** at `engines/excerpting/reference/dr_reviews/PRELIMINARY_SYNTHESIS_4_OF_5.md`
- **4-layer architecture CONFIRMED across 4/5 coworkers:**
  - Layer 1: User model + pedagogical modes → "What kind of student?" (~2h, partially resolved)
  - Layer 2: Quality policies + S-1 governance → "What rules govern output?" (~3h, mostly missing)
  - Layer 3: Engine decisions + parameters → "What configures each engine?" (~5h, 5 sessions)
  - Layer 4: Calibration with real output → "Does engine match the brain?" (~20-30h, summer)

**ALL 5 COWORKERS COMPLETE. Final synthesis:** `engines/excerpting/reference/dr_reviews/FINAL_SYNTHESIS_5_OF_5.md`
**Gemini DR added:** Fiqh masking layer, mantiq as science #19, Basran terminology default, month-by-month calendar.

**Owner curriculum decisions (2026-04-07, RESOLVED):**
1. Primary madhab: **Hanbali** → fiqh masking layer suppresses Hanafi/Shafi'i/Maliki until baseline mastery
2. Mantiq: **Yes, add as science #19** → foundational logic tree required before usul al-fiqh
3. Basran terminology: **TBD** (not yet asked — lower priority, blocks nahw synonym layer)

**Session 11 accomplishments (feedback collection workstream):**
- **S-1 INTAKE COMPLETE:** 18 files unzipped, validated (9 JSONL, 3 YAML, 6 MD/TXT). 11 governance atoms extracted to MERGED_ATOM_QUEUE.md Section M. Key atoms: teaching-unit-as-goal (S1-001), source integrity constraint (S1-002), self-containment dual reading (S1-003), granularity ≠ brevity (S1-004), usefulness ≠ mutation license (S1-005). All PRELIMINARY (0/3 coworkers).
- **`/ce:plan` COMPLETE:** `docs/plans/2026-04-07-001-feat-feedback-collection-system-plan.md` — 7 implementation units across 4 phases. Strengthened by 2 research agents that discovered existing questionnaire infrastructure at `integration_tests/questionnaire/`.
- **Unit 1 DONE:** `scripts/bundle_intake.py` (224 lines, 13 tests, pyright clean). Automates: unzip → validate manifest/JSONL/YAML → inventory → archive.
- **Unit 2 DONE:** `shared/user_model/owner_profile.yaml`. 19 sciences, Hanbali madhab, fatigue profile, S-1 priority architecture. 7/46 decisions resolved.
- **Unit 5 DONE:** `engines/excerpting/reference/COLLECTION_TRACKER.md`. 57 items across 4 layers, calendar milestones, DR18 session mapping. 13 resolved, 44 pending.
- **Recovery:** Restored MERGED_ATOM_QUEUE.md, FINAL_SYNTHESIS_5_OF_5.md, brainstorm requirements from git after Codex session deletions.
- **Codex CLI review prompt prepared** (via /prompt-architect) for plan + S-1 atom validation. 5 checks: structural consistency, requirements coverage, 4-layer alignment, atom correctness, cross-artifact consistency.

**Next steps (feedback collection workstream):**
1. **Dispatch Codex CLI review** of plan + S-1 atoms (prompt ready — owner relays to `codex exec`)
2. **Unit 3:** Questionnaire templates for K/E/D series (deep-dive ChatGPT sessions using S-1 format)
3. **Unit 4:** DR18 engine decision session templates (5 sessions, structured/interactive)
4. **S-1 atom coworker validation:** Minimum 2 independent sources before any atom advances

**Next steps (main hardening lane — HIGHEST PRIORITY):**
1. **DR28 prompt architecture implementation** — instruction sandwich + progressive disclosure (8-12 rules per call from 25). Synthesis at `engines/excerpting/reference/dr_reviews/DR28_synthesis.md`.
2. **3 OPEN design questions:** MAQ-074, MAQ-075, MAQ-077 — each needs a DR.
3. **Section K red-team tests:** 62 tests to automate as pytest cases.

**Key owner data already collected from interview (partially resolves 9 of 42 decisions):**
- Science priority: Arabic first, fiqh/usul/aqidah passion lane
- Priority book: الفقه على المذاهب الأربعة
- Study level: beginner
- Product vision: eliminate preparation, go straight to memorization
- Excerpt issue: engine under-divides (granularity)
- Feedback preference: 10-15 excerpts/session, structured/interactive, show reasoning

**Tracker:** `engines/excerpting/reference/dr_reviews/COWORKER_SYNTHESIS_TRACKER.md`

### COMPLETED: Environment Audit (2026-04-06)

### COMPLETED: Environment Audit (2026-04-06)

Debiased two-session environment audit. Merged plan at `reference/handoffs/environment_merged_plan_2026-04-06.md`.

**Key deliverables:**
- **Coverage baseline established: 82%** (914 tests, branch coverage). Gap: `tracer.py` 0%, `parallel_orchestrator.py` 56%.
- **7 tools activated:** pytest-cov, DeepEval (3 GEval metrics), DuckDB (SQL over results), promptfoo (config), mutmut (config), IAA metrics (Cohen's kappa), camel-tools (verified working)
- **context-mode plugin evaluated: DO NOT INSTALL** (WebFetch conflict, hook collision, CVE surface)
- **MCP cleanup identified:** 5 dead/failed servers to remove (owner action needed)
- **Run:** `pytest engines/excerpting/tests/ --cov=engines/excerpting/src --cov-branch --cov-report=term-missing`

**Environment next steps (not blocking hardening):**
1. Owner: `claude mcp remove exa && claude mcp remove fetch` — remove dead MCP servers
2. Investigate `tracer.py` (0% coverage) — dead code or untested entry point?
3. Run `npx promptfoo eval --config engines/excerpting/promptfooconfig.yaml` after next prompt change
4. Tier 2 items (hypothesis, pytest-xdist, OpenITI, Usul.ai) in a follow-up session

### ACTIVE LANE: Foundations Hardening (atom-by-atom)

Branch: `excerpting-foundations-hardening-20260404`
Ledger: `engines/excerpting/reference/FOUNDATIONS_HARDENING_LEDGER.md`
**Protocol: `engines/excerpting/reference/HARDENING_SESSION_PROTOCOL.md` v5.0 (GOVERNING LAW) — ALL 6 BATCH LIFECYCLE DRs PROCESSED (DR12-DR17)**
Plan: `.claude/plans/protocol-v50-batch-lifecycle.md` (Batch Lifecycle plan — 52 requirements from 6 DRs, Gemini-corrected)

**Foundations Q&A: 8 / 8 answered (F1-F8). G1-G4 + SC1-SC3 intake IN PROGRESS (Session 5).** Owner continuing methodology for all 40 questions.

### Session 5 — Intake-Only (2026-04-07, IN PROGRESS)

**Completed:**
- 7 bundles flattened from `_bundle/engines/excerpting/` nesting to `chatgpt_{series}_collection/`
- `batch_inventory.py` run on all 7 (inventory.json created per bundle)
- `batch_verification_init.py` run on all 7 (verification_status.json initialized)
- All 7 raw owner reactions (Layer A ground truth) read by CC
- 60 ground truth atoms pre-extracted to `engines/excerpting/reference/G_SC_GROUND_TRUTH_PREEXTRACTION.md`
- Tests: 915 pass (1 flaky LLM eval: `test_dialectical_preserved` 0.788 vs 0.8 — pre-existing)
- Prompt-SPEC sync: PASSED

**Completed (extraction):**
- 7 parallel extraction agents: **157 atoms** from 143 files (7,500 lines read)
- Ground truth validation: **PASS** (60/60 pre-extracted atoms confirmed)
- Arabic degradation: **0 pipeline-introduced** (4 source OCR artifacts noted)
- MERGED_ATOM_QUEUE.md Section L integrated (157 atoms, 10 FP candidates, 36 prompt-affecting)
- Session 6 handoff: `reference/handoffs/excerpting_foundations_session6_kickoff_2026-04-07.md`
- Disposition: 36 PROMPT (blocked §4.11), 62 SPEC, 10 FP, 24 META, 14 DEFERRED, 11 overlap

**Key findings:**
- **SC1 TRANSFORMATIVE**: Owner realized excerpts are "teaching units" (would rename engine)
- **SC3 CRITICAL**: 5x "PIPELINE CATASTROPHICALLY LACKING SECURITY GATES" — post-excerpting reassembly gate needed
- **G1 FP candidate**: "Excerpting is OBJECTIVE — NO OUTSIDE FACTORS" (generalizes FP-4)
- **Prompt RESTORED (Session 9)**: GROUP_SYSTEM_PROMPT at 1483 words — full detail + T1-1/T1-2/T1-3 amendments + Gemini classical ordinals fix. DR21 compression attempted then reverted (owner: quality > compression). 1500-word cap REMOVED. DR28 prepared for long-term prompt architecture research.
- **PRELIMINARY debt**: B2 (1/3) + B3 (1/3) + all G/SC (0/3)

### Session 9 Foundation Integrity Audit + DR28 Architecture (2026-04-07)
- **3-coworker audit** of all 38 numeric constraints: 7 HIGH, 15 MEDIUM, 16 LOW. No other phantom constraints.
- **Fix 1:** Consensus text truncation ([:1500]) REMOVED — verifier sees full text now.
- **Fix 2:** GROUP_MAX_TOKENS made dynamic (8192/16384/32768) matching CLASSIFY/ENRICH.
- **Fix 3:** `CONSTRAINT_REGISTRY.md` — every threshold documented with origin + calibration status.
- **Guardrail:** `constraint-origin-trace.md` rule — prevents phantom constraint pattern.
- **Codex doctrine audit:** 18 ALIGNED, 4 DRIFT (FP-5/11/21/22 — all deferred implementation, not contradictions).
- **Gemini Arabic audit:** 8/10 lists UNSOUND (PRELIMINARY). Deferred to DR28 architecture.
- **DR28 received (2 providers):** ChatGPT DR (10+ citations) + Claude DR (60+ sources). Converged architecture: 2-message instruction sandwich + progressive disclosure (8-12 rules per call, down from 25). Synthesis at `engines/excerpting/reference/dr_reviews/DR28_synthesis.md`. Codex + Gemini validating compatibility.

### Session 9 Accomplishments (2026-04-07) — Prompt Architecture + SPEC Sync
- **T1-1/T1-2/T1-3 prompt amendments:** Causal particles expanded (إذ, لكونه). Semantic dependency exemption (تخصيص/شرط/استثناء/تقييد stays with عام, FP-5). Dialectical cross-ref (فإن قيل/قلنا → FP-14).
- **T2-1..T2-7 SPEC sync:** Anti-surface-classification in §5.2.2. QM-4 in §6.6. New §6.7 (PS-1/PS-2 proof structure), §6.8 (SQ-1 scholar-quoting-scholar — highest risk), §6.9 (BC-1 boundary audit), §6.10 (MF-1 malformation-first diagnosis).
- **Gemini CLI fix:** Classical textual ordinals (أحدها, والثاني, الوجه الأول) added to NUMBERED ITEMS.
- **Codex CLI fix:** FP-3 causal particle list synced with prompt (stale "exhaustive" wording corrected).
- **DR21 compression attempted then reverted:** 1440→794 words lost quality (Gemini found 2 gaps). Owner challenged: "quality > compression." Full detail restored at 1483 words. 1500-word cap removed.
- **DR28 brief prepared:** Long-term prompt architecture research (multi-message, structured formats, progressive disclosure). Ready for Claude DR + ChatGPT DR relay.
- **All B2/B3 atoms: IMPLEMENTED.** Ledger updated.
- **917 tests pass**, SPEC-prompt alignment: EXACT MATCH.

**Roadmap (updated):**
1. **Sessions 6-9**: COMPLETE
2. **Session 10 (NEXT):** Implement DR28 prompt architecture (instruction sandwich + progressive disclosure, 10 implementation units). Check Codex/Gemini validation results first. Then: dedup remaining ~90 non-NN atoms.
3. **Session 11+:** Full-atom processing (G/SC atoms through 7-stage lifecycle)
4. **After hardening:** A/B test new vs monolithic prompt on 50+ inputs (~EUR 10). Book Resolution (40 DR20 titles → Shamela IDs). Tier 1 smoke run (10 books, ~$30).

**Session 2 complete. Protocol v4.0 → v4.1 patch in progress.** ChatGPT DR adversarial review (DR9, archived at `engines/excerpting/reference/dr_reviews/DR9_chatgpt_protocol_v40_adversarial.md`) found 18 issues (8 CRITICAL, 9 HIGH, 1 MEDIUM). Cross-referenced by explore agent: 12 confirmed gaps, 4 partially addressed, 2 already fixed. Plan approved, implementation in progress: 14 protocol amendments + 1 closure verifier script + version bump.

**v4.1 amendment status: COMPLETE**
- Units 1-14: All 14 protocol text amendments applied
- Unit 15: `scripts/verify_atom_closure_minimal.py` — BUILT AND PASSING (12 closed atoms verified)
- Unit 16: Version bump to v4.1 — DONE (protocol, NEXT.md, check_protocol_version.py all agree)

**Key v4.1 changes (from DR9):**
- Checkpoint resolution gate in §1.6 (prevents orphaned atoms)
- model_only atoms ineligible for Light Lane (closes authority bypass)
- WIP cap split: active-processing vs awaiting-external (prevents deadlock)
- Blinded DR tiebreaker template (ensures independence)
- Session-type compatibility matrix (only 2 allowed combinations)
- Q-12 outcome spot-check for cross-science atoms (outcomes, not just artifacts)
- Owner engagement heartbeat every 10 atoms post-50 (prevents silent disengagement)
- Doctrine backfill protocol on amendment (§8.4)

**Protocol review COMPLETE:**
- Codex CLI: 4/4 accepted → v2.2
- Gemini CLI: 7/7 accepted → v2.1
- ChatGPT DR: 10/38 accepted (38 findings + 10 pre-mortems, 4/10 score) → v3.0 (DR6)
- Gemini DR: 5/8 accepted, 3 redirected (8 findings, 4/10 + 3/10 scores) → v3.1 (DR7)
- Claude DR: 8/19 accepted (19 findings, 5/10 score) → v3.2 (DR8)
- All DR reports archived: `engines/excerpting/reference/dr_reviews/DR6-DR8`

**Atom progress:**
| # | Atom | Status |
|---|------|--------|
| 1 | EE-1 (explained + explanation unity) | FINALIZED + EMPIRICALLY VALIDATED (taysir + ibn_aqil) |
| 2 | NC-1 (context hierarchy) | FINALIZED |
| 3 | Linking-word preservation | FINALIZED (C-SC-2 expanded) |
| 4-5 | Khilaf/tarjih separation | DOCUMENTED, deferred to K-1/K-2/K-3 |
| 6-12 | Remaining doctrinal atoms | FINALIZED (FP-1 through FP-10 in SPEC §1.1b) |
| **B1** | **Safety & Integrity batch (17 MAQ atoms)** | **CONFIRMED (4/4 coworkers). FP-5/FP-2 strengthened, FP-19/20/21/22 added.** |
| **B2** | **Self-Containment batch (5 MAQ atoms)** | **PRELIMINARY (1/3 coworkers). 4 prompt rules added (+210 words). Gemini found Bukhari title flaw → fixed.** |
| **B3** | **Boundary & Grouping batch (10 MAQ atoms)** | **PRELIMINARY (1/3 Gemini). 3 prompt rules (+141w), 4 SPEC-only. Prompt: 1423/1500.** |
| **B4** | **Granularity (17 MAQ atoms)** | **IMPLEMENTED. 1 prompt rule (+51w), 16 SPEC-only. Prompt: 1474/1500 (FULL).** |
| **B5** | **Tarjih/Khilaf/Proof (21 MAQ atoms)** | **SPEC-ONLY. Prompt FULL. 9 SPEC rules, 7 deferred cross-engine.** |
| **B6** | **Other (9 MAQ atoms)** | **SPEC-ONLY. 3 SPEC, 2 deferred, rest documented/verified.** |

**Session 2 deliverables so far:**
- MERGED_ATOM_QUEUE.md built (556 lines, 250 ideas, 88 actionable atoms, 0 silent drops)
- Batch 1 (Safety & Integrity): 6 FP changes implemented — FP-2 strengthened (anti-rescue), FP-5 strengthened (cascade), FP-19 (omission honesty), FP-20 (validation rigor), FP-21 (severity class), FP-22 (anti-covert-excerpter)
- Codex + Gemini challenged and synthesized. Key finding: Gemini's al-Ghazali adversarial scenario proves FP-19 is existentially necessary.
- 907/907 tests pass, 0 regressions
- SPEC now has 22 FPs (FP-1 through FP-22, excluding FP-18 numbering)

**What's needed next:**
1. **DR coworker confirmation** — combined relay prompt prepared for Batches 1-3. All files pushed to remote branch. Batches stay PRELIMINARY until DR reviews.
2. **SPEC §6 formalization** — Batch 4/5/6 SPEC-only atoms need formal §6 subsection entries (not just ledger documentation). ~30 rules to add.
3. **Red-team test expansion** — 62 tests documented, only 9 automated. Create additional pytest cases for highest-priority tests.
4. **Empirical validation** — run atom_test.py against taysir fixture with the hardened prompt to verify new rules don't cause regressions.
5. **Prompt optimization** — 1474/1500 words. If empirical validation shows LLM ignoring late rules (primacy bias), consider REPLACING lower-priority rules with higher-priority ones.

**Session 3 = intake-only session (per protocol v4.0 §1.5 + §1.6 gate precedence):**

PREREQUISITE GATE (§0 checklist):
1. Read `HARDENING_SESSION_PROTOCOL.md` v4.0 (§0 checklist + version delta from v3.3). Run `python scripts/check_protocol_version.py` to verify version consistency.
2. Read `engines/excerpting/CLAUDE.md` + this file + `FOUNDATIONS_HARDENING_LEDGER.md` (recent entries only — dispatch subagent for full ledger)
3. Verify branch: `excerpting-foundations-hardening-20260404`. Run pytest + `check_prompt_spec_sync.py` — must pass.
4. Inventory bundles: `ls *.zip` at repo root → G1-G4 + SC1 exist → gate 4 (§1.6) triggers → session type = `intake-only`.
5. State: "Session type: intake-only. No atom processing this session. Target: complete intake for 5 bundles."

PHASE A — Bundle Intake (G1-G4 + SC1, follow §3 exactly):
6. Unzip 5 bundles to `engines/excerpting/chatgpt_{series}_collection/`
7. Per bundle: dispatch subagent for inventory → conflict scan (including Arabic text degradation per §3.2 Step 3) → per-file atom extraction (NOT single bulk pass — §3.2 Step 4)
8. Coverage verification: flag any files with 0 extracted atoms for re-read (prevents Session 1's 124-gap failure)
9. Assign MAQ-IDs, integrate into `MERGED_ATOM_QUEUE.md`. Deduplicate against existing F1-F8 atoms.
10. Archive zips to `source_artifacts/`. Verify quality gate (§3.3 — 8 checkboxes).

PHASE B — Preliminary Debt + Future Session Planning:
11. Count PRELIMINARY atoms from Session 2 (B1-B3). Check if DR responses arrived since Session 2.
12. Do NOT clear debt this session — defer to Session 4 (`debt-clearance` type).
13. Count total prompt-affecting atoms across ALL batches (F + G + SC). This informs Session 5's prompt refactor.

HANDOFF: Write Session 4 kickoff per §7.2. Session 4 type = `debt-clearance`. Session 5 type = `prompt-architecture` (§4.11 refactor gate). Session 6+ type = `full-atom` (3-5 Full Lane or 5-8 mixed atoms per session).

**Deferred work (NOT Session 3 — future full-atom sessions):**
- Formalize SPEC §6 entries for ~30 SPEC-only atoms from Batches 4-6
- Route to SPEC: FP-13 genre-sensitivity (SCH-009/010), Organic Knowledge Unit (PED-001)
- Re-run empirical validation on additional chunks (ibn_aqil_v1 chunk 0, taysir chunks 1-3)
- Build `verify_atom_closure.py` (DA-001) — machine-checkable Q-CLOSED evidence
- Fix remaining 4 xfail red-team gaps (ZWSP, damma truncation, segment contiguity, boundary ordering)
- Prepare Phase 1 smoke run with fully hardened prompt

**Pre-existing test failure:** `test_phase2_integration.py::test_classify_and_normalize` fails with 401 (expired OpenRouter API key). Not related to hardening changes. Confirmed pre-existing on clean master.

---

### Phase 0 Status: QUESTIONNAIRE FOUNDATIONS COMPLETE, DEEP DIVES PENDING

The owner completed F1-F8 (Foundations phase). Phases 2-4 (30 remaining interactions) are deferred until foundations hardening is complete. CC does NOT wait idly. Concurrent work continues below.

**Questionnaire artifacts (all at `integration_tests/questionnaire/`):**

| File | Purpose | Owner sees? |
|------|---------|-------------|
| `OWNER_QUESTIONNAIRE.md` | The actual questionnaire (owner fills this) | YES |
| `RESPONSE_FORMAT.md` | Response template for each interaction | YES |
| `QUESTIONNAIRE_EXAMPLES.md` | Real excerpt examples for each interaction | YES |
| `QUESTIONNAIRE_TEMPLATE.md` | Master template (coworker-designed) | NO |
| `TEAM_TRANSLATION_GUIDE.md` | Maps answers to SPEC rules + prompt params | NO |
| `CRITICAL_EVALUATION_GUIDE.md` | 6-coworker evaluation protocol | NO |
| `excerpt_selections.json` | Machine-readable excerpt selection index | NO |

**CJ-2 / CJ-3 placeholders:** These interactions require before/after comparisons between campaign (old prompts) and v2 (hardened prompts) excerpts for the same passage. CC fills these automatically when the taysir v2 package completes -- no owner action needed. The owner will see rendered Arabic text, not JSON.

**When owner finishes the questionnaire:**
1. CC dispatches the 6-coworker critical evaluation (see `CRITICAL_EVALUATION_GUIDE.md`)
2. CC synthesizes all coworker findings into a unified assessment
3. CC presents challenges back to the owner ONLY for genuine contradictions or infeasible preferences
4. CC documents confirmed answers and proceeds to Phase 0 exit

**Phase 0 EXIT CONDITION:**
- [ ] All 6 coworker evaluations received (or N-1 after 48h timeout per coworker)
- [ ] All identified contradictions resolved with owner or resolved by priority ranking (S-1)
- [ ] Confirmed answers documented in a `PHASE_0_CONFIRMED.md` file
- [ ] SPEC amendments drafted per `TEAM_TRANSLATION_GUIDE.md` (CC writes, no owner review needed)
- [ ] Prompt calibration changes identified (CC writes, filed as code changes)
- [ ] V2 data cross-referenced with confirmed answers (owner-principle test, use #3 below)

---

## V2 Run Status & Data Usage

### Package Status

| Package | Status | Excerpts | Errors | Cost | Time |
|---------|--------|----------|--------|------|------|
| ibn_aqil_v1 | COMPLETE | 241 | 3 (2x EX-V-002, 2 chunk failures) | $4.40 | 44 min |
| ibn_aqil_v3 | COMPLETE | 278 | 6 (5x EX-V-002, 1 chunk failure) | $4.30 | 45 min |
| taysir | IN PROGRESS | pending | 0 so far | pending | ongoing |

**Taysir status check:** 509 progress entries (504 done, 0 errors). Phase 2a: 180 classifications. Phase 2b: 179 groupings. Phase 3 enrichment: 145 done. No `excerpts.jsonl` or `SUMMARY.json` yet -- run is still in pipeline. Check `integration_tests/smoke_api_v2/taysir/progress.jsonl` for live status.

**When taysir completes:** CC automatically updates SUMMARY.json, fills CJ-2/CJ-3 placeholders, and logs the completion.

**Output location:** `integration_tests/smoke_api_v2/` -- NEVER overwrite or delete this directory.

### Chunk-Limit Investigation

The v2 run processed ALL taysir chunks (184) instead of the intended 2 per package. This was unintentional but produces more valuable data. The cost discrepancy (~$55 total vs estimated ~$6) is because of this full-book behavior. **Before the next run:** investigate and fix the chunk-limit logic in `scripts/run_full_integration.py`. The `--max-chunks` flag must be verified to actually limit processing.

### V2 Data Usage Plan (7 uses -- every dollar counts)

1. **CJ-2 questionnaire interaction** -- Before/after comparison for the owner (same passage, old vs new prompts). CC renders as readable Arabic text.
2. **Phase 1 six-team analysis** -- All 6 analysis teams evaluate v2 output quality against SPEC and owner answers.
3. **Owner-principle test** -- After questionnaire, run every v2 excerpt through the owner's stated principles as pass/fail. Automated where possible, manual spot-check for judgment calls.
4. **Before/after regression** -- Campaign (2,303 excerpts, Opus, old prompts) vs v2 (GPT-5.4, hardened prompts). Measure every improvement and regression quantitatively.
5. **Edge case mining** -- 520+ raw LLM responses reveal model reasoning at boundaries. Diagnostic gold for prompt calibration.
6. **Training data** -- Raw outputs + structured excerpts + eventual owner evaluation labels (per Rule 13 in principles.md).
7. **Prompt calibration baseline** -- V2 becomes the BEFORE for the next iteration after questionnaire-driven prompt changes.

**Data preservation rules:**
- NEVER delete raw LLM responses (`raw_llm_requests/`, `raw_llm_responses/`)
- NEVER overwrite `excerpts.jsonl` -- copy to a dated backup before any re-run
- NEVER modify `SUMMARY.json` after it is written -- append corrections as `SUMMARY_patch_YYYYMMDD.json`
- All 6-team analysis outputs go in `integration_tests/smoke_api_v2/analysis/` (new directory, created by CC)

---

## Phase 0 --> Phase 1 Transition Checklist

**Owner: CC (all items). No owner approval gate.**

| # | Check | Owner | Status |
|---|-------|-------|--------|
| 1 | Owner questionnaire responses complete (all 40 interactions answered) | CC verifies | PENDING |
| 2 | 6-coworker critical evaluation complete (all 6, or N-1 with 48h timeout) | CC dispatches | PENDING |
| 3 | All contradictions resolved (either by owner clarification or S-1 priority ranking) | CC decides | PENDING |
| 4 | SPEC amendments written per `TEAM_TRANSLATION_GUIDE.md` column mapping | CC writes | PENDING |
| 5 | Prompt calibration changes applied to `engines/excerpting/prompts/` | CC writes | PENDING |
| 6 | V2 data fully available (all 3 packages complete, SUMMARY.json finalized) | CC checks | PENDING |
| 7 | Chunk-limit bug investigated and fixed in `scripts/run_full_integration.py` | CC fixes | PENDING |
| 8 | CJ-2/CJ-3 placeholders filled with rendered before/after comparisons | CC fills | PENDING |
| 9 | `PHASE_0_CONFIRMED.md` written with all confirmed answers + traceability | CC writes | PENDING |
| 10 | CC self-verifies all 9 items above -- NO owner sign-off needed | CC | PENDING |

**Transition rule:** When all items are DONE, CC proceeds to Phase 1 immediately. No waiting for owner permission.

---

## Phase 1: Smoke Analysis (CC orchestrates everything)

### Purpose

Analyze the v2 smoke data using exhaustive multi-team review + owner spot-check. This produces a complete quality assessment that drives Phase 2 hardening priorities.

### Step 1: CC Spawns 5 Analysis Subagents (parallel)

| Team | Agents | Focus | Input Files | Output |
|------|--------|-------|-------------|--------|
| A: Boundary Quality | CC + Codex CLI | Every boundary checked against SPEC §4.A-B | `excerpts.jsonl` (all 3 pkgs) | `TEAM_A_BOUNDARY.md` |
| B: Classification | Gemini CLI + ChatGPT DR | Every `primary_function` verified against domain glossary | `excerpts.jsonl` + `phase2a_classifications/` | `TEAM_B_CLASSIFICATION.md` |
| C: Arabic Fidelity | Claude DR + Gemini CLI | Diacritics, honorifics, isnad integrity, text corruption | `excerpts.jsonl` + raw source text | `TEAM_C_ARABIC.md` |
| D: Consensus & Metadata | Codex CLI + CC | author_id, school, evidence_refs, D-023 pass-through | `excerpts.jsonl` + `cache/` dirs | `TEAM_D_METADATA.md` |
| E: Coverage & Gaps | ChatGPT DR + Claude DR | Missing excerpts, over/under-extraction, coverage ratio | `excerpts.jsonl` + `phase1_chunks.json` | `TEAM_E_COVERAGE.md` |

All outputs go to `integration_tests/smoke_api_v2/analysis/`.

### Step 2: CC Dispatches 3 DR Coworkers (parallel with Step 1)

| Coworker | Access Method | What CC Provides | Timeout |
|----------|---------------|------------------|---------|
| ChatGPT DR | Relay prompt to owner | File contents pasted into prompt (self-contained). Include: 10 representative excerpts, SPEC §4 relevant sections, specific questions about error patterns and architecture. | 48h |
| Claude DR | Relay prompt to owner | File contents pasted into prompt (self-contained). Include: 10 boundary edge cases, SPEC §4.A self-containment rules, specific questions about scholarly reasoning and boundary quality. | 48h |
| Gemini DR | Relay prompt to owner | File uploads (excerpts.jsonl, SPEC.md). Include: 5 excerpts per genre, specific questions about Islamic study methodology and genre-specific natural units. | 48h |

**DR prompt construction:** Every relay prompt must be fully self-contained -- the DR session cannot access the repo. Paste all necessary file contents, excerpt text, and context directly into the prompt. Follow templates in `.claude/skills/coworker-dispatch/SKILL.md`.

**DR timeout protocol:** If a DR coworker does not return within 48h, CC proceeds with N-1 results and documents the gap in `PHASE_1_REPORT.md`. Minimum required: 3 out of 5 teams + 1 out of 3 DR coworkers.

### Step 3: CC Selects 20 Excerpts for Owner Review

CC selects and renders as readable Arabic text (NOT JSON):
- 10 best excerpts (highest confidence, cleanest boundaries, diverse genres)
- 10 worst excerpts (lowest confidence, boundary issues, classification uncertainty)

**Owner is asked ONLY:** "For each excerpt: good / bad / confusing? If bad or confusing, what bothered you?"

The owner does NOT review SPEC compliance, metadata accuracy, or technical details. CC translates any owner reactions into technical actions.

### Step 4: Synthesis

CC collects all team reports, DR results, and owner spot-check feedback. Produces:

**Output:** `integration_tests/smoke_api_v2/analysis/PHASE_1_REPORT.md` containing:
- Per-team findings (confirmed = 2+ teams agree, disputed = disagreement, novel = single team)
- Owner reaction summary (translated to technical actions)
- Prioritized issue list (CRITICAL / HIGH / MEDIUM / LOW)
- Recommended Phase 2 actions

### Phase 1 EXIT CONDITION

- [ ] At least 4 out of 6 teams (5 analysis + owner) confirm acceptable quality, OR
- [ ] Owner accepts excerpts from at least 2 packages in the spot-check
- [ ] All CRITICAL issues documented with proposed fixes
- [ ] `PHASE_1_REPORT.md` complete and committed
- [ ] Phase 2 action plan written with estimated cost

---

## Phase 2: Deep Hardening (CC decides priorities)

### Purpose

Fix everything found in Phase 1. Iterate until convergence. CC drives all decisions -- coworkers validate, owner is only asked about experience.

### Hardening Steps

| Step | What | Owner | Depends On |
|------|------|-------|------------|
| 2a | Fix prompt calibration (temperature, few-shots, instructions) | CC | Phase 1 findings |
| 2b | Fix grouping/boundary logic (Phase 2b prompt, grouping criteria) | CC | Phase 1 Team A report |
| 2c | Fix enrichment/metadata (Phase 3 prompt, field extraction) | CC | Phase 1 Team D report |
| 2d | Re-run 2 packages with fixes (~$6, CC launches) | CC | 2a + 2b + 2c complete |
| 2e | Re-evaluate with 3 CC subagents (boundary + classification + metadata) | CC | 2d output available |
| 2f | Compare Phase 1 baseline vs 2d results (quantitative regression check) | CC | 2d + 2e complete |

### Iteration Protocol

**CONVERGENCE CRITERIA:**
- At least 80% of Phase 1 issues resolved in 2d results
- Zero CRITICAL-severity issues remaining
- Owner accepts 10 re-rendered excerpts from 2d (good/bad/confusing only)
- No regression: 2d results are strictly better than Phase 1 on measured dimensions

**MAX 3 ITERATIONS.** If after 3 cycles of 2a-2f the convergence criteria are not met:
- CC documents all remaining known issues in `KNOWN_LIMITATIONS.md`
- CC classifies each as: will-fix-in-taxonomy, will-fix-in-synthesis, accept-as-is, or needs-SPEC-change
- CC proceeds to Phase 3 with documented limitations
- Owner is informed of the limitations in non-technical terms ("some long scholarly debates may not be split perfectly")

**Decision authority:** CC decides priorities, fix order, and when to stop iterating. Coworkers validate fixes. Owner is only asked "does this excerpt look good to you?"

### Phase 2 EXIT CONDITION

- [ ] Convergence criteria met, OR max 3 iterations exhausted with documented limitations
- [ ] All code changes committed with tests
- [ ] `PHASE_2_REPORT.md` written (changes made, issues resolved, issues remaining)
- [ ] Prompts in `engines/excerpting/prompts/` updated and committed
- [ ] SPEC amendments (if any) committed
- [ ] Cost log updated in `COST_LOG.json`

---

## Phase 3: Full 5-Book Run

### Purpose

The definitive run with fully hardened prompts. Produces the output that will be used for taxonomy engine input.

### Command

```bash
python scripts/run_full_integration.py \
  --backend api \
  --max-chunks 2 \
  --output-dir integration_tests/v2_final/
```

**CRITICAL:** Verify `--max-chunks` actually limits processing BEFORE running. The v2 run ignored this flag (see chunk-limit investigation above). Test with a single package first.

**Output directory:** `integration_tests/v2_final/` -- NEVER overwrite v2 data at `integration_tests/smoke_api_v2/`.

**Estimated cost:** ~$15-25 depending on chunk count and model pricing.

### Post-Run Evaluation

1. CC runs automated comparison: v2_final vs campaign baseline (2,303 excerpts, old prompts, Opus)
2. CC runs automated comparison: v2_final vs v2 smoke (hardened prompts, pre-questionnaire)
3. All 6 teams re-evaluate v2_final output (same protocol as Phase 1, Step 1)
4. Owner reviews 10 rendered excerpts (good/bad/confusing)

### Phase 3 EXIT CONDITION

- [ ] All 5 packages complete with no CRITICAL errors
- [ ] At least 4/6 teams confirm output quality meets or exceeds Phase 2 results
- [ ] Owner accepts excerpts from at least 3 packages
- [ ] No regressions vs Phase 2 on any measured dimension
- [ ] `PHASE_3_REPORT.md` written
- [ ] All data preserved (raw responses, excerpts, cache, timing)
- [ ] Excerpting engine declared EVALUATION COMPLETE -- ready for taxonomy engine input

---

## Error Handling Protocol

### Coworker Unavailable

| Scenario | Action |
|----------|--------|
| Codex CLI down | Log in `.kr/runtime/dispatch_log.jsonl`. Reassign structural checks to CC. Proceed. |
| Gemini CLI down | Log. Reassign Arabic checks to Claude DR (relay prompt). Proceed. |
| DR coworker (any) does not return within 48h | Log. Proceed with N-1 results. Document gap. |
| Fewer than 3 coworkers available | STOP. Report to owner: "Cannot proceed -- only N coworkers available, minimum 3 required." |

### Owner Unresponsive

| Scenario | Wait | Then |
|----------|------|------|
| Questionnaire not started after delivery | 48h | CC sends a reminder with an estimated time commitment. |
| Questionnaire in progress but stalled | 72h since last answer | CC sends progress check: "You've completed X/40 interactions. Take your time -- no rush." |
| Questionnaire complete but challenges unanswered | 72h | CC proceeds using S-1 priority ranking + coworker-confirmed resolution. Documents decision. |
| Owner spot-check (Phase 1/2/3) not returned | 48h | CC proceeds with coworker-only evaluation. Notes "owner review pending" in report. |

**Principle:** CC never blocks on owner input for more than 72h. After 72h, CC uses the best available information and proceeds with documented reasoning.

### Run Failures

| Scenario | Action |
|----------|--------|
| API timeout during run | Automatic retry with exponential backoff (2s, 4s, 8s, max 3 retries). Log to ERROR_LOG.json. |
| Run stall (no progress.jsonl update for 1h) | Kill the process. Resume from last checkpoint using `--resume` flag. |
| Partial completion (some packages succeed, some fail) | Preserve ALL successful results immediately. Investigate failures. Re-run only failed packages. |
| Invalid output (malformed JSON, schema violations) | Do NOT discard. Quarantine to `quarantine/` subdirectory. Investigate root cause before re-run. |

### Budget Exceeded

| Scenario | Action |
|----------|--------|
| Single run would exceed remaining budget | STOP. Report: "This run costs ~$X, remaining budget is $Y. Approve?" Wait for owner. |
| Cumulative spend exceeds `KR_BUDGET_LIMIT` | STOP all API runs immediately. Report full cost breakdown. Do not retry. |
| Unexpected cost spike (>2x estimated) | Pause after current package. Investigate cause (chunk-limit bug? model pricing change?). Report. |

### Coworker Disagreement

When 2+ coworkers disagree on a content quality judgment:
1. CC examines the specific excerpt/issue both coworkers assessed
2. CC applies SPEC rules as the tiebreaker where possible
3. If SPEC is ambiguous, CC makes the decision and documents reasoning
4. The decision is marked as `[CC-DECIDED: rationale]` in the report
5. Disputed items are flagged for owner spot-check in the next review cycle

---

## Budget

| Category | Spent | Remaining | Notes |
|----------|-------|-----------|-------|
| Source engine (Cohere + Opus) | EUR 36.70 | EUR 63.30 / EUR 100 | Complete. No further spend. |
| OpenRouter v2 smoke | ~$8.70 (2 pkgs) | ~EUR 45 of dev budget | taysir still running, will add ~$40 |
| Phase 2 smoke (2 pkg re-run) | -- | ~$6 per re-run | Budget for 3 iterations = ~$18 |
| Phase 3 full 5-book | -- | ~$15-25 | One run. No re-runs budgeted. |
| **Total excerpting budget** | **~$55** | **~EUR 45 remaining** | Enough for Phase 2 (3x) + Phase 3 |

**Cost tracking:** Every API-calling script logs to `COST_LOG.json`. The `cost-guard.sh` hook enforces `KR_BUDGET_LIMIT`. CC checks budget before every run.

---

## Current Engine State

### What's Implemented (917 tests pass)

- 8 Tier-1 prompt fixes (H-1 through H-8): few-shots, schema split, copy fidelity
- 3 Claude DR fixes: narrator role, al-ma'na al-ijmali classification, fawa'id grouping
- DR-1 (definition pair splitting): in Phase 2b prompt
- DR-3 (khilaf preservation): in Phase 2b prompt
- CrossReference extension: target_excerpt_id + relationship_type
- DR-1 companion detection: deterministic post-enrichment linking
- Evidence resolution hints: canonical surah/ayah in cross-references
- Bug fixes: consensus resolution, ZWNJ, LA-3 threshold, model defaults

### What's Deferred

- DR-2 (evidence-type splitting): 3/5 reviewers rejected. Deferred to taxonomy pilot.
- Multi-leaf taxonomy tagging: requires VISION 1.2 amendment. Deferred.
- Taxonomy engine: being built in parallel. Nahw tree nearly final. Trees NOT trustworthy yet.

---

## Key Decisions (6-reviewer cross-validated)

| Decision | Rationale | Score |
|----------|-----------|-------|
| GPT-5.4 primary | 3x cheaper, contract-stable, errors are prompt-fixable | 3/5 |
| DR-1 ADOPT (conditional) | Definition pairs are separate topics; self-containment gate | 4/5 |
| DR-2 DEFER | Puzzle excerpt risk; VISION 1.2 tension unresolved | 3/5 reject |
| DR-3 ADOPT (structural) | Khilaf = highest decontextualization risk | 5/5 |

---

## Model Configuration

| Role | Model | Use |
|------|-------|-----|
| Primary (classify + group + enrich) | openai/gpt-5.4 | All excerpting pipeline calls |
| Verify | anthropic/claude-opus-4.6 | Consensus verification where required |
| Escalation | mistralai/mistral-large-2411 | Tiebreaker on disagreements |

---

## Research Artifacts (DO NOT DELETE)

### Diagnostic Reports (moved to reference/ and docs/)

- `reference/BOUNDARY_CONVENTION_DIAGNOSTIC.md` -- Claude DR boundary analysis (133 excerpts)
- `docs/coworker_reports/2026-03-31_adversarial_reviews/chatgpt-report-diagnostic-analysis.md` -- ChatGPT error patterns
- `docs/coworker_reports/2026-03-31_adversarial_reviews/chatgpt-deep-research-opus_vs_gpt.md` -- Opus vs GPT-5.4 model comparison
- `chatgpt-deep-research-granuality-synthesis.md` -- Synthesis engine granularity analysis
- `chatgpt-Adversarial Review of DR-1, DR-2, DR-3.md` -- DR adversarial review

### Campaign Analysis (`integration_tests/campaign_20260331/analysis/`)

19 files: excerpt_catalog.jsonl (2,303 indexed), gold_candidates.jsonl (100), taxonomy_readiness_flags.jsonl (54 flags), arabic_fidelity_flags.jsonl (382 flags), taysir_scholarly_review.md (68-excerpt deep review), convention_compliance_report.md (7 checks), scholarly_reality_check_intra_excerpt.md, gemini_adversarial_DR_review.md, plus catalogs and summaries.

### Owner Feedback

- `integration_tests/campaign_20260331/taysir/owner_feedback.jsonl` -- 2 reviews that triggered the granularity debate

---

## Your Team -- USE ALL AT EVERY MILESTONE

| Agent | Access | Use For | Access Notes |
|-------|--------|---------|--------------|
| **Codex CLI** | `codex exec` (direct repo access) | Schema validation, cross-prompt consistency, stats | Can read/write repo files directly. Best for deterministic checks. |
| **Gemini CLI** | `gemini -p` (direct repo access), Gemini 3.1 Pro | Arabic scholarly accuracy, convention compliance | Can read repo files directly. Major coworker for Arabic. |
| **ChatGPT DR** | Deep Research (relay prompt to owner) | Error patterns, architectural analysis, Q&A design | NO repo access in DR mode. Paste all file contents into prompt. Owner relays. |
| **Claude DR** | Deep Research (relay prompt to owner) | Scholarly reasoning, boundary quality, edge cases | NO repo access in DR mode. Paste all file contents into prompt. Owner relays. |
| **Gemini DR** | Deep Research (relay prompt to owner) | Islamic study methodology, scholarly pedagogy | NO repo access in DR mode. Upload files where possible. Owner relays. |

**Dispatch protocol:** See `.claude/skills/coworker-dispatch/SKILL.md` for per-coworker prompt templates.
**Dispatch log:** Every dispatch recorded in `.kr/runtime/dispatch_log.jsonl`.
**Minimum for any milestone:** 3 out of 5 coworkers must evaluate. 5 out of 5 is the target.
