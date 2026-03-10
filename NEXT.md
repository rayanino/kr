# NEXT — Prepare Source Engine Session 6

**Status:** Sessions 1–5b COMPLETE. 503 tests passing. All modules built except engine.py (orchestrator) and logger.py.

**Task:** Use kr-build-prep to produce the Session 6 NEXT.md for Claude Code.

## What Exists

- `engines/source/session-6-plan.md` — Session 6 scope (written before Sessions 5a/5b — some items are now stale, see below)
- `engines/source/TESTING_PROTOCOL.md` — post-build validation plan (Phase A–E, for after Session 6)
- `engines/source/docs/session5-contracts-audit.md` — known SPEC defects (4 misalignments, all resolved in code)
- 503 passing tests across 14 test files

## What Session 6 Actually Builds

**Two modules:**
1. `engine.py` — full pipeline orchestrator (Steps 1→9). Currently a docstring-only stub (18 lines).
2. `logger.py` — structured JSONL logging with SourceError serialization. Currently a docstring-only stub (10 lines).

**NOT config.py** — already fully built in Session 5a (102 lines, tested). The session-6-plan.md says "Replace stub" for config.py but that's stale.

**Plus testing and verification:**
3. Error path testing — exercise every §7 error code that can fire in Stage 1
4. Full pipeline run on ALL 13 fixtures (requires LLM calls — ~$1-2)
5. Plain text end-to-end (alfiyyah_versified fixture)
6. Source → Normalization boundary verification (metadata.json validates against normalization input contract)
7. Step 4 blocking conditions — see status below

## Step 4 Blocking Conditions — Current Status

These three conditions must be met before declaring the source engine complete.

**Condition 1 — Confidence calibration (CG-1): NOT DONE.**
Requires extracting confidence scores from Step 2 phase results to check whether models produce >0.90 confidence on wrong answers. The results files (`tests/results/phase1_*.json`, `phase2_*.json`) are gitignored and lost from the Session 3 environment reset. Only `tests/results/STEP2_SUMMARY.md` survived.
**Resolution path:** Session 6's full pipeline run on 13 fixtures will produce fresh confidence scores from real Instructor calls. Analyze those to verify the 0.50/0.70 thresholds. No need to re-run Phase 2 separately — piggyback on the integration test.

**Condition 2 — A3-1 name matching fix: DONE.**
Token-based `normalized_name_similarity()` is in production at `shared/scholar_authority/src/name_matching.py`. Two tests confirm short-vs-long name handling: `test_04_short_vs_long_name_with_date` (scholar_authority) and `test_a3_1_edge_case_short_vs_long` (name_matching).

**Condition 3 — Author-specific consensus complementarity (CG-5): NOT VERIFIED.**
The consensus pair (Command A + Opus 4.6) was selected across all 7 scored fields equally. The STEP2_EVALUATION.md notes: "What I cannot verify without per-field data: Whether the selected pair has complementary error profiles specifically on author identification." The per-field results files are lost.
**Resolution path:** During Session 6's full pipeline run, compare the two models' author identification outputs across 13 fixtures. If they agree on every author, complementarity is low but correctness is high (still acceptable). If they disagree on any author, check who was right — that validates complementarity.

## Known Issues the Next Chat Must Account For

1. **Trust evaluator uses validated formula, not SPEC text.** SPEC §4.A.8 author_standing requires "prior sources" for 0.90 classical tier, but the validated formula (13/13 correct) uses only death_date. See trust_evaluator.py module docstring and session5-contracts-audit.md Misalignment 3. Do not "fix" the trust evaluator to match SPEC.

2. **TRANSLIT_MAP SPEC defect.** SPEC §4.A.1 says إ → 'a'. Implementation correctly uses إ → 'i' (phonetically correct). Do not "fix" to match SPEC.

3. **session-6-plan.md is partially stale.** config.py is already complete. The plan's "Modules to Build" table lists 3 modules but only 2 need building. The plan's carry-forward section about blocking conditions needs the updated status above.

4. **LLM calls needed.** Session 6 runs the full pipeline including Step 4 (inference + consensus). Environment needs: `ANTHROPIC_API_KEY`, `OPENROUTER_API_KEY`. Cost: ~$1-2 for 13 fixtures × 2 models.

## Build-Prep Deliverables Expected

Per the kr-build-prep skill: technology survey (any new deps for engine.py/logger.py?), contracts audit (engine.py input/output matches contracts?), NEXT.md for Claude Code with accurate module list and test specifications.
