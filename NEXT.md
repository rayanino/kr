# NEXT -- Excerpting Engine: Deep Q&A + Exhaustive Hardening

---

## IMMEDIATE STATE (updated 2026-04-01)

### Phase 0 Status: QUESTIONNAIRE DELIVERED

The owner is filling in `integration_tests/questionnaire/OWNER_QUESTIONNAIRE.md` (~40 interactions, 15-25 hours across multiple sessions). CC does NOT wait idly. Concurrent work continues below.

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

### Diagnostic Reports (repo root)

- `BOUNDARY_CONVENTION_DIAGNOSTIC.md` -- Claude DR boundary analysis (133 excerpts)
- `chatgpt-report-diagnostic-analysis.md` -- ChatGPT error patterns
- `chatgpt-deep-research-opus_vs_gpt.md` -- Opus vs GPT-5.4 model comparison
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
