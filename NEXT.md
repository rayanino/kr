# NEXT — Excerpting Engine: Deep Q&A + Exhaustive Hardening

## IMMEDIATE STATE (updated 2026-04-01)

**You are the Phase 0 orchestrator. Start here.**

### What's done
- Environment hardening: dispatch skill, questionnaire template, no-single-model rule, hooks — all committed
- Role definition: embedded in CLAUDE.md, `.claude/rules/role-definition.md`, `.kr/ACTIVE.md`, memory
- Prompt hardening: 8 Tier-1 fixes (H-1 through H-8), DR-1/DR-3 in prompts, model defaults fixed
- V2 smoke run: **in progress or recently completed** at `integration_tests/smoke_api_v2/`
  - 2 packages done: ibn_aqil_v1 (241 excerpts, €4.40), ibn_aqil_v3 (278 excerpts, €4.30)
  - **Cost per run is ~€12-15 total, NOT the original €3 estimate.** Hardened prompts produce 3-4x more excerpts per package.
  - Check SUMMARY.json for final status

### What's pending — YOUR FIRST TASK
Two coworker validation reports are incoming. The owner will paste them into this session:
1. **Claude Chat DR report**: stress-tested the dispatch protocol and no-single-model rule for failure modes
2. **ChatGPT Pro DR report**: optimized the questionnaire format (question types, ordering, scoring)

**When you receive both reports:**
1. Synthesize their feedback into a unified set of changes
2. Update `integration_tests/questionnaire/QUESTIONNAIRE_TEMPLATE.md` based on synthesis
3. Prepare the actual owner Q&A — select real excerpt examples from campaign data, render them as readable text (not JSON)
4. Present the Q&A to the owner section by section

### What NOT to do
- Do not re-run the smoke. Wait for v2 results first.
- Do not re-dispatch the same coworkers. Their reports are coming.
- Do not start Phase 1 analysis until Phase 0 (Q&A) is complete.

---

## What This Operation Does

This is the FINAL excerpting engine hardening operation. Four phases:

0. **Phase 0: Owner Q&A** — Design and conduct a structured questionnaire with the owner to nail down what excerpts should be. This comes FIRST, before any code.
1. **Phase 1: Smoke Run + Analysis** — Analyze v2 smoke results with exhaustive multi-team review.
2. **Phase 2: Deep Hardening** — Fix everything found in Phase 1 + Q&A, iterate until convergence.
3. **Phase 3: Full 5-Book Run** — The definitive run (~$15-20) with fully hardened prompts.

## Phase 0: Owner Q&A (DO THIS FIRST)

### Why This Matters
Two comments from the owner on campaign excerpts triggered a complete rearchitecture (DR-1/DR-2/DR-3 debate, 6 reviewers, 2 days). The excerpt definition in the SPEC is formally correct but doesn't fully capture what the owner WANTS to experience when using his library. This Q&A closes that gap.

### How To Do It
1. **All coworkers** (Codex, Gemini CLI, ChatGPT DR, Claude DR, Gemini DR) collaboratively design a questionnaire
2. The questionnaire uses REAL excerpts from the campaign (2,303 excerpts at `integration_tests/campaign_20260331/`) and previous smoke runs as examples
3. Questions are ONLY end-user questions — NOT domain/pipeline questions:
   - "When you read this excerpt, what's your reaction?"
   - "Is this too much? Too little? Just right?"
   - "What would you do next after reading this?"
   - "Show me your ideal version of this excerpt"
   - NOT: "Should DP-4 be modified?" (that's our problem to solve)
4. Owner fills in the form at his own pace
5. Team translates answers into SPEC rules and prompt calibrations
6. Every technical decision traces back to an owner answer

### Questionnaire Scope
Cover these dimensions (each with real excerpt examples):
- **Granularity**: too broad vs too narrow vs just right
- **Self-containment**: what context do you need alongside an excerpt?
- **Comparison experience**: show 3 excerpts from different sources on the same topic — is this useful?
- **Definition handling**: لغة/شرعا pairs — together or separate?
- **Evidence handling**: ruling+evidence together, or would you prefer them navigable separately?
- **Scholarly debate**: full khilaf passage vs individual positions?
- **Genre differences**: does a grammar excerpt feel different from a fiqh excerpt? Should it?
- **Navigation**: when you finish reading one excerpt, what do you want to see next?
- **The "no puzzle" rule**: show a PARTIAL excerpt with context_hint — is this acceptable or frustrating?
- **Study workflow**: walk through a typical study session — what do you open first, what do you compare?

### What NOT To Ask
- Pipeline architecture questions
- SPEC compliance questions  
- Arabic grammar analysis
- Technical tradeoff questions
- Anything a machine can answer by reading the repo

## V2 Run Data Usage Plan

The v2 smoke run at `integration_tests/smoke_api_v2/` cost ~$55 and produced a full-book taysir dataset with hardened prompts (GPT-5.4 primary, H-1 through H-8 fixes). This data MUST be fully used — no waste. Seven specific uses:

1. **CJ-2 questionnaire interaction** — Before/after comparison for the owner (same passage, old vs new prompts)
2. **Phase 1 six-team analysis** — All 6 analysis teams evaluate v2 output quality
3. **Owner-principle test** — After questionnaire, run every v2 excerpt through the owner's stated principles as pass/fail
4. **Before/after regression** — Campaign (1,283 excerpts, Opus) vs v2 (taysir, GPT-5.4). Measure every improvement and regression.
5. **Edge case mining** — 520 raw LLM responses reveal model reasoning at boundaries. Diagnostic gold.
6. **Training data** — Raw outputs + structured excerpts + eventual owner evaluation labels (Rule 13)
7. **Prompt calibration baseline** — V2 becomes the BEFORE for the next iteration after questionnaire-driven prompt changes

**NOTE:** The run processed ALL 184 taysir chunks (full book), not the intended 2 chunks per package. This was unintentional but produces more valuable data. The cost discrepancy (~$55 vs estimated €3) is because of this full-book behavior. Investigate and fix the chunk-limit logic in `scripts/run_full_integration.py` before the next run.

## Phase 1: Smoke Run + Exhaustive Analysis

After Q&A is complete and prompts are adjusted, the v2 data above serves as the Phase 1 input. No new run is needed unless prompts change significantly. Then:

### Analysis Teams (ALL in parallel)
| Team | Agents | Focus |
|------|--------|-------|
| A: Boundary Quality | CC + Codex | Every boundary checked against SPEC |
| B: Classification | Gemini + ChatGPT DR | Every primary_function verified |
| C: Arabic Fidelity | Claude DR + Gemini | Diacritics, honorifics, isnad integrity |
| D: Consensus & Metadata | Codex + CC | author_id, school, evidence_refs |
| E: Coverage & Gaps | ChatGPT DR + Claude DR | Missing excerpts, over/under-extraction |
| F: Owner Review | Owner + review tool | Real-user quality assessment |

### Exit Criteria for Phase 1
- Owner has reviewed excerpts from at least 2 packages and accepted them
- All 5 coworkers independently confirm output quality
- Zero known unaddressed error patterns
- All automated checks pass

## Phase 2: Deep Hardening

Based on Phase 1 findings:
- Fix every issue (prompt changes, SPEC amendments, code fixes)
- Re-run smoke (~€3)
- Re-evaluate with all teams
- Iterate until exit criteria met

## Phase 3: Full 5-Book Run

Only when Phase 2 converges:
```bash
python scripts/run_full_integration.py --backend api --output-dir integration_tests/v2_final/
```

~$15-20, full books. Compare against campaign (2,303 excerpts, old prompts, Opus).

---

## Current Engine State

### What's Implemented (917 tests pass)
- 8 Tier-1 prompt fixes (H-1 through H-8): few-shots, schema split, copy fidelity
- 3 Claude DR fixes: narrator role, المعنى الإجمالي classification, fawa'id grouping  
- DR-1 (definition pair splitting): in Phase 2b prompt
- DR-3 (khilaf preservation): in Phase 2b prompt
- CrossReference extension: target_excerpt_id + relationship_type
- DR-1 companion detection: deterministic post-enrichment linking
- Evidence resolution hints: canonical surah/ayah in cross-references
- Bug fixes: consensus resolution, ZWNJ, LA-3 threshold, model defaults

### What's Deferred
- DR-2 (evidence-type splitting): 3/5 reviewers rejected. Deferred to taxonomy pilot.
- Multi-leaf taxonomy tagging: requires VISION §1.2 amendment. Deferred.
- Taxonomy engine: being built in parallel. Nahw tree nearly final. Trees NOT trustworthy yet.

### Key Decisions (6-reviewer cross-validated)
| Decision | Rationale | Score |
|----------|-----------|-------|
| GPT-5.4 primary | 3x cheaper, contract-stable, errors are prompt-fixable | 3/5 |
| DR-1 ADOPT (conditional) | Definition pairs are separate topics; self-containment gate | 4/5 |
| DR-2 DEFER | Puzzle excerpt risk; VISION §1.2 tension unresolved | 3/5 reject |
| DR-3 ADOPT (structural) | Khilaf = highest decontextualization risk | 5/5 |

### Model Configuration
Primary (classify + group + enrich): openai/gpt-5.4  
Verify: anthropic/claude-opus-4.6  
Escalation: mistralai/mistral-large-2411

---

## Research Artifacts (DO NOT DELETE)

### Diagnostic Reports (repo root)
- `BOUNDARY_CONVENTION_DIAGNOSTIC.md` — Claude DR boundary analysis (133 excerpts)
- `chatgpt-report-diagnostic-analysis.md` — ChatGPT error patterns
- `chatgpt-deep-research-opus_vs_gpt.md` — Opus vs GPT-5.4 model comparison
- `chatgpt-deep-research-granuality-synthesis.md` — Synthesis engine granularity analysis
- `chatgpt-Adversarial Review of DR-1, DR-2, DR-3.md` — DR adversarial review

### Campaign Analysis (integration_tests/campaign_20260331/analysis/)
19 files: excerpt_catalog.jsonl (2,303 indexed), gold_candidates.jsonl (100), taxonomy_readiness_flags.jsonl (54 flags), arabic_fidelity_flags.jsonl (382 flags), taysir_scholarly_review.md (68-excerpt deep review), convention_compliance_report.md (7 checks), scholarly_reality_check_intra_excerpt.md, gemini_adversarial_DR_review.md, plus catalogs and summaries.

### Owner Feedback
- `integration_tests/campaign_20260331/taysir/owner_feedback.jsonl` — 2 reviews that triggered the granularity debate

---

## Your Team — USE ALL AT EVERY MILESTONE

| Agent | Access | Use For |
|-------|--------|---------|
| **Codex** | CLI (repo) | Schema validation, cross-prompt consistency, stats |
| **Gemini CLI** | CLI (repo), Gemini 3.1 Pro | Arabic scholarly accuracy, convention compliance |
| **ChatGPT DR** | Deep Research (repo) | Error patterns, architectural analysis, Q&A design |
| **Claude DR** | Deep Research (repo) | Scholarly reasoning, boundary quality, edge cases |
| **Gemini DR** | Deep Research | Islamic study methodology, scholarly pedagogy |

## Budget
- OpenRouter: ~€50 remaining
- Smoke run: ~€3 per run
- Full 5-book: ~$15-20
