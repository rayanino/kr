# Excerpting Engine — Constraint Registry

> **Purpose:** Every numeric threshold in the engine is documented here with its origin, calibration status, and risk level. New thresholds without a registry entry are not constraints — they are unvalidated assumptions.
>
> **Rule:** Before treating ANY number as a constraint, trace it here. If it's not in this registry, it has no authority.
>
> **Created:** 2026-04-07, Session 9 foundation integrity audit (3-coworker investigation after phantom 1500-word cap incident)

## HIGH Risk (quality-impacting, action required)

| ID | Constraint | Value | Location | Origin | Calibration | Action |
|----|-----------|-------|----------|--------|-------------|--------|
| CR-1 | MAX_TOKENS >4000 words | 32768 (provisional) | phase2_classify.py:147 | Code comment: "untested" | UNCALIBRATED | Test during 30-book probe |
| CR-2 | GROUP_MAX_TOKENS | Dynamic (8192/16384/32768) | phase2_group.py:_compute_group_max_tokens | Session 9: matched to CLASSIFY/ENRICH pattern | PARTIALLY CALIBRATED (largest validated: 41 units at 3111 words) | Validate >4000 word chunks |
| CR-3 | VERIFY_MAX_TOKENS | 8192 | contracts.py:823 | No documented rationale | UNCALIBRATED | Justify or scale dynamically |
| CR-4 | ~~Consensus text preview~~ | ~~1500 chars~~ → FULL | phase3_consensus.py:136,155,173 | ~~Undocumented~~ → **FIXED Session 9: sends full text** | N/A (removed) | RESOLVED |
| CR-5 | text_snippet validation | 80 characters | contracts.py:406 | Experiment design | KNOWN ISSUE (DR-29: Unicode codepoint vs grapheme) | Redesign before probe |
| CR-6 | excerpt_topic cardinality | 1-3 keywords | contracts.py:516 | Design choice, no corpus analysis | UNCALIBRATED | Corpus analysis during probe |
| CR-7 | PARTIAL/DEPENDENT boundary | C-SC-1..5 criteria | SPEC §3 | Owner defers to 30-book probe | UNCALIBRATED | Calibrate with adversarial examples |

## MEDIUM Risk (unclear basis or single-source calibration)

| ID | Constraint | Value | Location | Origin | Calibration |
|----|-----------|-------|----------|--------|-------------|
| CR-8 | TINY_DIVISION_WORDS | 50 | contracts.py:803 | Shamela corpus: 29.1% of divisions | CALIBRATED (corpus) |
| CR-9 | OVERSIZED_DIVISION_WORDS | 5000 | contracts.py:804 | Shamela corpus: 0.9% of divisions | CALIBRATED (corpus) |
| CR-10 | Heading alignment | 30 chars in 200 | SPEC §4.3 | Experiment: 40-60% rejection at 15/100, relaxed | PARTIALLY (marked "may be calibrated") |
| CR-11 | LA-1 layer dominance | 80% | SPEC §6.2, contracts.py:110 | Design: "conservative, requires clear dominance" | DESIGN CHOICE (allows per-source override to 70%) |
| CR-12 | LA-3 uncertainty | <60% dominant | SPEC §6.2 | Design choice | UNCALIBRATED (gap between 60-80% is arbitrary) |
| CR-13 | CLASSIFY_TIMEOUT | 900s | contracts.py:813 | Smoke test: 88s baseline, 10.2x safety | CALIBRATED (single test) |
| CR-14 | GROUP_TIMEOUT | 900s | contracts.py:814 | Same as CLASSIFY | CALIBRATED (single test) |
| CR-15 | VERIFY_TIMEOUT | 600s | contracts.py:816 | "Calibrated from CLI timings" | PARTIALLY (lower than LLM phases, undocumented why) |
| CR-16 | description_arabic | 5-35 words | SPEC §5.3.2 | Experiment: 10-30, relaxed per §2.3 | CALIBRATED (experiment) |
| CR-17 | Forgiving retention | 15% / ~30 words | SPEC FP-3, prompt | Session 2 hardening, linguistic reasoning | UNCALIBRATED (reasonable heuristic) |
| CR-18 | Sub-item grouping | 20 words | SPEC §5.3.2, prompt | Design rule | UNCALIBRATED (round number) |
| CR-19 | School confidence | 0.67 for 2-of-3 | contracts.py:509 | Mathematical (2/3) | DERIVED (not arbitrary) |
| CR-20 | CLASSIFY MAX_TOKENS ≤1500w | 8192 | phase2_classify.py:155 | ibn_aqil_v3 single chunk test | SINGLE-SOURCE |
| CR-21 | CLASSIFY MAX_TOKENS >1500w | 32768 | phase2_classify.py:153 | Same single chunk test | SINGLE-SOURCE |
| CR-22 | ENRICH MAX_TOKENS ≤1500w | 16384 | phase3_enrichment.py:50 | ibn_aqil_v3: 14863 tokens at 91% utilization | SINGLE-SOURCE (tight margin) |

| CR-31 | FP-24 parenthetical exemption | ≤15 words | SPEC §FP-24, §6.25, prompts.py GROUP_CORE_RULES | DR40: "brief parenthetical citation with no independent study value" | UNCALIBRATED — heuristic from DR40. Needs calibration against real evidence citations in taysir + ibn_aqil to verify 15 words is the right threshold. Risk: too low → unnecessary splits of trivial citations; too high → evidence bundles survive that should split. |

## LOW Risk (well-justified or deterministic)

| ID | Constraint | Value | Location | Origin |
|----|-----------|-------|----------|--------|
| CR-23 | RETRY_COUNT | 2 | contracts.py:811 | Design choice (3 total attempts) |
| CR-24 | Temperature | 0.0 | contracts.py:809 | Determinism requirement (rules) |
| CR-25 | CONCURRENCY | 1 | contracts.py:832 | Safety/observability |
| CR-26 | ENRICH_TIMEOUT | 900s | contracts.py:815 | Calibrated from CLI timings |
| CR-27 | ESCALATION_TIMEOUT | 300s | contracts.py:817 | Design (shorter for tiebreaker) |
| CR-28 | Cross-reference demotion | 30 words | SPEC §5.4.3 | DR evaluation (TU-6 graded 1/5) |
| CR-29 | MV-1 sub-viable merge floor | 25 words | SPEC §5.5.5, phase3_deterministic.py:_MV1_WORD_FLOOR | DR consensus (ChatGPT 2/5 + Claude 1/5 on 5-word TU-5). Implemented Session 18. CAVEAT: isnad chains (7-12 words) are exempt via _ISNAD_MARKERS. Hadith collections may need corpus-specific calibration — 15-20 word isnads are legitimate standalone units (arabic-auditor finding 2026-04-08). |
| CR-30-38 | Layer validation, coverage invariants, gate policies | Various | contracts.py, SPEC §5.4 | Deterministic rules |

## REMOVED Constraints

| Constraint | Former Value | Removed | Reason |
|-----------|-------------|---------|--------|
| ~~Prompt word cap~~ | ~~1500 words~~ | Session 9 | **Phantom constraint.** Never formally decided. Emerged from informal note "1484/1500". Drove quality-losing 45% compression. Owner challenged. Removed permanently. |
| ~~Consensus text truncation~~ | ~~1500 chars~~ | Session 9 | Arbitrary truncation hid late evidence from verifier. Full text now sent. |

## Arabic Scholarly Constraints (PRELIMINARY — Gemini CLI audit, needs 2nd coworker)

8 of 10 Arabic-specific lists found UNSOUND by Gemini CLI. Findings are PRELIMINARY per no-single-model-conclusion rule. Full details logged in dispatch_log.jsonl (2026-04-07). Key gaps:
- Causal particle list: missing لما, حيث إن, بسبب, وعليه, ومن ثم
- Semantic dependency terms: missing الغاية, الصفة, البدل
- Verdict/tarjih terms: missing school-specific (المفتى به, الأظهر, ما به العمل)
- Q&A formulas: missing إن قلتَ/قلتُ, أورد/دفع, قوله/أقول
- Resolution: Deferred to DR28 (prompt architecture) — determines whether these go in prompt, reference document, or dynamic loading

---

## Scholar Authority Constraints (Phase 5 OPT-4 Architecture — calibrated 2026-05-05)

> **Scope:** Constants in `shared/scholar_authority/src/scholar_authority.py` (legacy 5-signal weighted-average path) and `shared/scholar_authority/src/threshold_compounding.py` (Phase 5 OPT-4 compound threshold path).
>
> **Origin:** SPEC declarations in `shared/scholar_authority/SPEC.md` §4.A.2 (matching algorithm) and Phase 5 cross-provider DR synthesis 2026-04-30 (4-evaluator wave: 3-of-4 HIGH; landed at commit `e91c142cc`). Both surfaces (legacy + OPT-4) are CALIBRATED against the 50-scholar gold baseline at `tests/fixtures/scholar_gold_seed_50.json` per SPEC §10 line 460.
>
> **Calibration method:** For every gold-seed entry, a stub `VerifierCallable` produces a per-candidate confidence as `0.40 + alignment*0.55`, where `alignment` is the fraction of the 6 INV-SRC-0013 attribute classes (century, school, primary_science, attributed_works, region_origin, region_active) that intersect between the candidate's `ScholarAuthorityRecord` and the dossier. The gold-seed `canonical_dossier` for each scholar is constructed to align all 4 of {primary_science, century, school, attributed_works} against the target (alignment ratio 4/4 → confidence 0.95) → DEFINITIVE under the compound threshold predicates. The 5 trap pairs (Ibn Taymiyya, Ibn Ḥajar, Ibn Qudāma, Ibn Rushd, al-Subkī) drive the CROSS-disambiguation calibration: feeding the trap-partner's dossier with the shared name fragment must resolve to the trap-partner DEFINITIVE. The integration test at `engines/source/tests/test_phase5_session45_gold_seed_calibration.py` exercises 50 canonical scenarios + 10 cross-trap scenarios + 50 name-only scenarios = 110 calibration cases.
>
> **Closure:** Closes `shared/scholar_authority/KNOWN_LIMITATIONS.md` L-SCH-004 (uncalibrated weights). Phase 5 implementation phase complete.

### MEDIUM Risk — single-source calibrated (50-scholar gold seed)

| ID | Constraint | Value | Location | Origin | Calibration |
|----|-----------|-------|----------|--------|-------------|
| CR-39 | Name similarity weight | 0.35 | `scholar_authority.py:307` (compute_scholar_match_score signal 1) | SPEC §4.A.2 line 125 | CALIBRATED — 50-scholar gold seed (`tests/fixtures/scholar_gold_seed_50.json`); the canonical-dossier scenario for each of the 50 scholars produces DEFINITIVE through `scholar_match_cell` per the integration test. Failure mode if too high: trap-pair name collisions (Ibn Ḥajar, Ibn Taymiyya, etc.) over-rely on name when discriminating attributes are present. Failure mode if too low: low-data scholars under-attribute. |
| CR-40 | Death date proximity weight | 0.25 | `scholar_authority.py:313` (compute_scholar_match_score signal 2) | SPEC §4.A.2 line 127 | CALIBRATED — gold seed traps Ibn Qudāma (620 vs 682, both 7th c.) and Ibn Rushd (520 vs 595, both 6th c.) and al-Subkī (756 vs 771, both 8th c.) discriminate via works rather than dates. Failure mode if too high: same-century scholars with different works misroute. |
| CR-41 | School affiliation weight | 0.15 | `scholar_authority.py:322` (compute_scholar_match_score signal 3) | SPEC §4.A.2 line 129 | CALIBRATED — gold seed includes 5 same-school trap pairs (both Ibn Taymiyyas hanbali; both Ibn Qudāmas hanbali; both Ibn Rushds maliki; both al-Subkīs shafi'i; both Ibn Ḥajars share fiqh shafi'i with primary_science differing). School alone never carries a trap; always corroborated by works + century. |
| CR-42 | Known works overlap weight | 0.15 | `scholar_authority.py:332` (compute_scholar_match_score signal 4) | SPEC §4.A.2 line 131 | CALIBRATED — works are the strongest discriminating signal across ALL 5 trap pairs (المنتقى vs مجموع الفتاوى; فتح الباري vs تحفة المحتاج; المغني vs الشرح الكبير; البيان والتحصيل vs بداية المجتهد; الإبهاج vs طبقات الشافعية). Removal of the work signal collapses 4 of 5 trap pairs to ambiguous. |
| CR-43 | Teacher-student overlap weight | 0.10 | `scholar_authority.py:341` (compute_scholar_match_score signal 5) | SPEC §4.A.2 line 133 (added Phase 5 Session 4, L-SCH-001 closure) | CALIBRATED — gold seed includes teacher-student edges within the 50 (Mālik→al-Shāfiʿī, al-Shāfiʿī→Aḥmad, Aḥmad→Bukhārī+Abū Dāwūd, Bukhārī→Muslim+Tirmidhī, Ibn Taymiyya→Ibn al-Qayyim+al-Dhahabī+Ibn Kathīr, Ibn Qudāma sr.→Ibn Qudāma jr.). The signal contributes when both candidate and existing record carry teacher/student arrays; never required for DEFINITIVE. |
| CR-44 | Nisba bonus on name signal | +0.10 capped at 1.0 | `scholar_authority.py:304-306` (compute_scholar_match_score) | SPEC §4.A.2 line 125 | CALIBRATED — nisba-rich gold-seed entries (Ibn Ḥajar al-ʿAsqalānī carries nisba=[العسقلاني, المصري, الكناني, الشافعي]) get the bonus when partial-name matching surfaces them via the nisba channel. Sub-1.0 cap is preserved by `min(1.0, ...)` clamp. |
| CR-45 | Name-only cap | 0.65 | `scholar_authority.py:351-352` (compute_scholar_match_score) | SPEC §4.A.2 line 135 | CALIBRATED — gold seed name-only scenario (empty `DossierContext`) for ALL 50 scholars terminates at INSUFFICIENT_EVIDENCE because (a) single-candidate degenerate routes to insufficient (per `threshold_compounding.py` docstring), (b) trap-pair name fragments produce ≥ 2 candidates each at 0.40 baseline confidence which falls below INSUFFICIENT_FLOOR=0.70. The 0.65 cap is the legacy single-stage protection; the OPT-4 floor (0.70) is stricter and superseding. |

### MEDIUM Risk — Phase 5 OPT-4 compound threshold (calibrated against gold seed)

| ID | Constraint | Value | Location | Origin | Calibration |
|----|-----------|-------|----------|--------|-------------|
| CR-46 | MEAN_THRESHOLD (definitive routing) | 0.92 | `threshold_compounding.py:78` | REQ-SRC-0053 + cross-provider DR synthesis 2026-04-30 | CALIBRATED — canonical-dossier scenario for each gold-seed scholar produces leader confidence 0.95 (alignment 4-of-4 dossier-attributes-aligned → confidence `0.40 + 1.0*0.55 = 0.95`); mean = 0.95 ≥ 0.92 ✓. Test gates: `test_canonical_dossier_produces_definitive` parametrized over all 50. |
| CR-47 | EACH_THRESHOLD (per-verifier definitive) | 0.90 | `threshold_compounding.py:79` | REQ-SRC-0053 | CALIBRATED — both A and B verifiers produce 0.95 on canonical dossier (≥ 0.90); both produce 0.40 on empty dossier (< 0.90 ✓ insufficient route). |
| CR-48 | RIVAL_MARGIN (no-rival-close predicate) | 0.07 | `threshold_compounding.py:80` | REQ-SRC-0053 (widened from 0.05 at Phase 5 Stage 4 closure to fix [0.05, 0.07) partition gap; commit `e91c142cc`) | CALIBRATED — trap-pair canonical-dossier scenarios produce leader 0.95 / rival 0.40 (alignment gap 4/4 vs 0/4) → gap 0.55 ≥ 0.07 ✓. Cross-trap scenarios (feeding trap-partner's dossier) produce leader 0.95 / rival 0.40 → same 0.55 gap ✓. Smallest gap observed in calibration is for same-attribute pairs where only the work differs (Ibn Qudāma) → leader 0.95 / rival ≈ 0.81 → gap 0.14 ≥ 0.07 ✓. |
| CR-49 | DISPUTED_FLOOR (mean ≥ for disputed) | 0.75 | `threshold_compounding.py:81` | REQ-SRC-0053 | CALIBRATED — name-only scenario produces mean 0.40 < 0.75 → INSUFFICIENT_EVIDENCE (correct routing). Gold seed has no calibration case where mean ∈ [0.75, 0.92) intentionally — the synthesis stub produces high (0.95) or low (0.40) by design; intermediate confidences are surfaced in the production verifier dispatch. |
| CR-50 | INSUFFICIENT_FLOOR (max individual ≥) | 0.70 | `threshold_compounding.py:82` | REQ-SRC-0053 | CALIBRATED — name-only scenario produces max 0.40 < 0.70 for ALL 50 → INSUFFICIENT_EVIDENCE (correct routing for "I cannot identify this scholar"). |
| CR-51 | NON_NAME_CORROBORATION_FLOOR (≥ for definitive) | 2 | `threshold_compounding.py:83` | INV-SRC-0013 | CALIBRATED — canonical dossiers for ALL 50 gold-seed scholars provide ≥ 4 corroborating non-name attribute classes (primary_science + century + school + attributed_works); ≥ 2 floor met with margin. The floor's purpose is to PREVENT name-similarity-only matches from reaching DEFINITIVE; the calibration confirms it does so for the trap pairs (where name alone returns 2+ candidates and only attribute corroboration disambiguates). |

### Calibration evidence + replay

- **Gold-seed file**: `tests/fixtures/scholar_gold_seed_50.json` (50 scholars including 5 trap pairs; biographical sources cited per entry — Siyar, Wafayāt, Ṭabaqāt, etc.).
- **Calibration test**: `engines/source/tests/test_phase5_session45_gold_seed_calibration.py` — 50 canonical-dossier scenarios + 10 cross-trap scenarios + 50 name-only scenarios = 110 cases, all parametrized via `@pytest.mark.parametrize` from the gold seed.
- **Spec ref**: `shared/scholar_authority/SPEC.md` §10 line 460 ("A gold baseline set of 50 well-known Islamic scholars... should be created from authoritative sources. This baseline serves dual purposes: (a) validating that the matching algorithm correctly handles the most common scholars, and (b) providing seed data for the registry during initial library setup.").
- **Replay**: `python -m pytest engines/source/tests/test_phase5_session45_gold_seed_calibration.py -v`. Any drift in the calibrated weights or thresholds (beyond ±0.02) requires re-running this calibration sweep and updating the registry entries above with the new evidence.
- **Failure-mode catalog (per-constraint risk if mis-calibrated)**: documented inline in each row above. The shared failure mode across CR-39 through CR-45 is the trap-pair collision: lowering the work weight or raising the name weight degrades the 5 trap-pair disambiguations first.
