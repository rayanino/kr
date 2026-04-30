# Scholar Authority — Known Limitations

Tracked limitations discovered during build. Not bugs (code matches its current shape consistently), but drifts between SPEC.md and implementation that the architect and future sessions should be aware of. Format mirrors `engines/normalization/KNOWN_LIMITATIONS.md`.

## L-SCH-001: SPEC §4.A.2 declares 5 matching signals; implementation has 4 (teacher-student missing)

**Discovered:** 2026-04-29 Phase 5 scholar-matching DR Stage-1 verification (Claude DR digest §6 + Stage-2 verification ChatGPT DR digest §6).
**SPEC reference:** `shared/scholar_authority/SPEC.md` §4.A.2 lines 117-129 — declares 5 signals: name similarity (0.35), death date proximity (0.25), school affiliation overlap (0.15), known works overlap (0.15), **teacher-student overlap (0.10)** + nisba bonus +0.10 on component-wise match.
**Implementation reference:** `shared/scholar_authority/src/scholar_authority.py:166-234` `compute_scholar_match_score` — uses 4 signals: name similarity (weight 0.50), death date (0.30), school (0.10), known works (0.10). The teacher-student signal is entirely absent from the function signature (`candidate_name`, `candidate_death_date`, `candidate_school`, `candidate_known_work`, `existing_record`) and from the scoring computation.
**Behavior:** `compute_scholar_match_score` cannot incorporate teacher-student-overlap as a corroborating signal. The `existing_record.teachers` and `existing_record.students` fields exist on `ScholarAuthorityRecord` (contracts.py:712-713) but are never consulted during matching.
**Impact:** Two distinct scholars with the same name + similar death date + same school + same known works COULD theoretically be distinguished by teacher-student-overlap (the existing record's known teachers vs the candidate's known teachers from the source dossier). The current implementation cannot exploit this signal. Adversarial cases involving father-son scholar pairs or master-student scholar pairs in the same generation are at higher false-merge risk than they would be with 5 signals.
**SPEC compliance:** Drift — implementation does not match SPEC §4.A.2 declared signal set. The implementation's docstring (line 175 "SPEC §4.A.5 weighted average of available signals") cites the WRONG SPEC section as well — §4.A.5 is "External Enrichment Sources" (OpenITI/Wikidata/LLM), not the matching algorithm. The matching algorithm lives at §4.A.2 "Record Matching and Disambiguation."
**Fix point:** Phase 5 implementation. The Phase 5 architectural decision (currently in cross-provider DR synthesis — Stage 3 pending) will rewrite this matching algorithm under OPT-4 (2-stage deterministic-then-LLM). ChatGPT DR's §3b score breakdown EXPLICITLY includes `teacher_student_network_match` as one of 9 sub-scores in disputed-position structures (see `memory/phase5_dr_chatgpt_digest_20260429.md` §6). Whatever Stage 3 chooses, the rewritten matching algorithm must include teacher-student-overlap as a first-class signal. The current implementation drift is captured here so that the Phase 5 implementation does not inadvertently reproduce the omission.

## L-SCH-002: SPEC §4.A.2 weight values differ from implementation weights

**Discovered:** Same as L-SCH-001.
**SPEC reference:** SPEC.md §4.A.2 — name 0.35 / death_date 0.25 / school 0.15 / known_works 0.15 / teacher-student 0.10 + nisba bonus +0.10. Sum = 1.00.
**Implementation reference:** scholar_authority.py:184-221 — name 0.50 / death_date 0.30 / school 0.10 / known_works 0.10. Sum = 1.00 across 4 signals.
**Behavior:** Implementation over-weights name (0.50 vs SPEC 0.35) and death_date (0.30 vs SPEC 0.25), under-weights school (0.10 vs 0.15) and known_works (0.10 vs 0.15), and omits teacher-student entirely. The 0.65 name-only cap (line 230-232) is preserved on both sides; `auto_match_threshold=0.85` (lines 277-279) is preserved on both sides.
**Impact:** The implementation's heavier name+death-date weighting biases the matching algorithm toward classifications that depend on name string similarity + death date proximity even when school/works data could be informative. For two candidates with identical names + close death dates but different known_works, the implementation gives works only 0.10 weight (10% of the score) vs the SPEC's 0.15 (15%), making it harder for known_works overlap to override a name+date match. There is no calibration data justifying either weight set — both are round-number assertions per `.claude/rules/constraint-origin-trace.md`.
**SPEC compliance:** Drift — implementation weight set is uncalibrated and differs from SPEC's also-uncalibrated weight set. Per the constraint-origin-trace rule, NEITHER weight set is currently a "calibrated" constraint; both are unvalidated assumptions.
**Fix point:** Phase 5 implementation + calibration. The Phase 5 architectural rewrite is the right time to either (a) align with SPEC §4.A.2 weights, or (b) redesign the weights with empirical calibration on a known-collisions test set (e.g., the disambiguation traps documented in `tests/fixtures/` or a new dedicated calibration corpus per `.claude/rules/constraint-origin-trace.md` "Round numbers (50, 100, 500, 1000, 5000) are suspect until calibrated"). Whichever path is chosen, the calibration data source and rationale MUST be documented in a new CONSTRAINT_REGISTRY.md entry per the constraint-origin-trace rule.

## L-SCH-003: Implementation docstring cites SPEC §4.A.5 instead of §4.A.2 for the matching algorithm

**Discovered:** Same as L-SCH-001.
**SPEC reference:** SPEC.md §4.A.2 lines 113-132 = "Record Matching and Disambiguation" — defines the matching algorithm. SPEC.md §4.A.5 lines 166-188 = "External Enrichment Sources" — OpenITI/Wikidata/LLM enrichment, NOT matching.
**Implementation reference:** `compute_scholar_match_score` docstring at scholar_authority.py:175 reads `"SPEC §4.A.5 weighted average of available signals"`. ScholarMatchResult docstring at line 34 reads `"SPEC §4.A.5 scoring thresholds"`. The `lookup` function docstring at line 247 reads `"SPEC §4.A.5 thresholds"`. All three citations are wrong — the correct section is §4.A.2.
**Behavior:** Reading the code suggests that the matching algorithm is implementing the External Enrichment Sources section, which it is not. A reader following the docstring reference would be misled.
**Impact:** Code-reading and architectural-review confusion. Coworkers and reviewers tracing implementation back to spec section will land on the wrong section. This drift was a contributing factor to Claude DR's Phase 2 misattribution (Claude DR's `tabaqat_genre` reasoning landed on the right concept — century axis — but cited INV-SRC-0007 incorrectly).
**SPEC compliance:** Documentation drift — code behavior is not affected, but documentation pointers are wrong.
**Fix point:** Trivial fix. Edit the three docstrings to reference §4.A.2. Can be done as a docs-only change in any session, no test impact. Should be bundled with L-SCH-002 weight-alignment when Phase 5 rewrite happens.

## L-SCH-004: 4-signal weighted-average is uncalibrated and unjustified at SPEC level

**Discovered:** Same as L-SCH-001.
**SPEC reference:** SPEC.md §4.A.2 lines 121-127 — declares 5 signals with specific weights but provides NO calibration data ("These weights are designed to..." appears nowhere; weights appear without rationale or empirical anchor).
**Implementation reference:** scholar_authority.py:175-182 docstring — declares 4 signals with specific weights, also without calibration data.
**Behavior:** Both SPEC and implementation present specific weight numbers as if they are designed quantities, but neither has calibration data documented. The constraint-origin-trace rule (`.claude/rules/constraint-origin-trace.md`) flags such numbers as "round numbers... suspect until calibrated." 0.35/0.25/0.15/0.15/0.10 (SPEC) and 0.50/0.30/0.10/0.10 (impl) are BOTH round-number sets without empirical justification.
**Impact:** Future calibration work has no reference baseline. Comparing "is the new calibration better?" requires comparing against a known-state, which requires the known-state to be empirically grounded in the first place. Currently neither side provides that grounding.
**SPEC compliance:** Per the constraint-origin-trace rule: "Every numeric threshold in engine code or SPEC must have an entry in `engines/excerpting/reference/CONSTRAINT_REGISTRY.md`. New thresholds without a registry entry are unvalidated assumptions, not constraints." The matching weights have no CONSTRAINT_REGISTRY.md entry. Compliance gap.
**Fix point:** Phase 5 implementation must establish a calibration corpus (proposed: 50-scholar gold set per SPEC §10 line 460 "Gold baselines: A gold baseline set of 50 well-known Islamic scholars... should be created from authoritative sources") with known-correct match labels for representative ambiguous cases (ابن حجر العسقلاني vs ابن حجر الهيتمي, ابن تيمية death-year ambiguity, etc.). Calibrated weights must be documented with their data source in a new CONSTRAINT_REGISTRY.md entry. Until calibration exists, neither weight set should be treated as authoritative.

---

## Cross-cutting note: Phase 5 architectural decision will likely obsolete L-SCH-001 through L-SCH-004

**Status as of 2026-04-29:** Phase 5 cross-provider DR has returned both per-DR digests. Stage 3 cross-provider synthesis is pending in a fresh session (per `memory/phase5_dr_chatgpt_digest_20260429.md` Stage 3 trigger). Both DRs converged on OPT-4 (2-stage deterministic-then-LLM consensus). When Stage 3 + Stage 4 produce SPEC atom amendments, the matching-algorithm rewrite will likely:
- Replace `compute_scholar_match_score` with a Stage-1 deterministic narrowing function + Stage-2 verifier scoring
- Re-weight signals based on Stage 3's adjudication of work-title-as-deterministic-index (ChatGPT DR pivot) vs work-title-as-Stage-2-scoring (Claude DR + existing)
- Adopt teacher-student-overlap as either a Stage-1 narrowing channel or a Stage-2 scoring signal (per ChatGPT DR §3b line 117 — `teacher_student_network_match` as 1 of 9 sub-scores)
- Calibrate against a 50-scholar gold seed per SPEC §10 line 460
- Possibly add work-title-to-canonical-id index (ChatGPT DR §3a Stage 5 + §3d line 191)

When Stage 4 lands, this KNOWN_LIMITATIONS.md should be re-evaluated:
- L-SCH-001 (missing teacher-student): likely RESOLVED by Phase 5 implementation
- L-SCH-002 (weight drift): likely RESOLVED by Phase 5 calibration; the new weights must be CONSTRAINT_REGISTRY.md-backed
- L-SCH-003 (docstring section reference): likely RESOLVED by code rewrite (new docstrings reference new SPEC structure)
- L-SCH-004 (uncalibrated weights): likely RESOLVED by gold-seed calibration

The fix point for all four limitations is therefore "Phase 5 Stage 4 implementation," not a standalone fix session.

**Why document now if Phase 5 will obsolete:** Visibility insurance. If Phase 5 implementation forgets to address one of these (e.g., implements OPT-4 but reuses the existing 4-signal weighted-average for Stage-2 scoring), this file ensures the gap is caught at Phase 5 review time. Without this file, the drift would be invisible and likely re-introduced.
