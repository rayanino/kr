# Weekend Handoff to Codex — 2026-04-01

## Situation

CC (Claude Code) session ending. Owner has 3+ days offline (Thu-Sun) to review excerpts and answer the questionnaire via the web UI. Codex takes over all remaining preparation work — unlimited budget, hours of runtime available.

## What's Done

1. **Questionnaire web UI** — `tools/excerpt_viewer.html` + `tools/review.py` extended with Questionnaire mode (40 interactions, 32 with MC) + Comparison mode. Owner runs `python tools/review.py integration_tests/smoke_api_v2/` and opens localhost:8384.

2. **Governance hardening** — 3 new enforcement rules in `.claude/rules/`, 5 role violations fixed, NEXT.md rewritten with exit conditions and ownership for every step.

3. **Coworker reports archived** — 18 reports from Downloads/Desktop saved to `docs/coworker_reports/`.

4. **V2 smoke run** — ibn_aqil_v1 (241 excerpts) and ibn_aqil_v3 (278 excerpts) DONE. Taysir was still running as of last check (~524 progress entries, in Phase 3 enrichment). Check if it finished.

## What Codex Must Do

### PRIORITY 1: Check and finalize v2 taysir run

```bash
# Check if taysir finished
tail -3 integration_tests/smoke_api_v2/taysir/progress.jsonl
ls -la integration_tests/smoke_api_v2/taysir/excerpts.jsonl
```

If `excerpts.jsonl` exists: taysir is done. Count excerpts and update SUMMARY.json:
```bash
wc -l integration_tests/smoke_api_v2/taysir/excerpts.jsonl
```

If NOT: check if the run is still going (last modified time of progress.jsonl). If stalled (>1h no writes), document the stall and what data is available.

### PRIORITY 2: Fill CJ-2 and CJ-3 placeholders (if taysir finished)

CJ-2 (Before/After comparison) and CJ-3 (Cross-book comparison) are placeholders in `integration_tests/questionnaire/interactions.json`. If taysir v2 data is available:

1. Find the same division in both `campaign_20260331/taysir/excerpts.jsonl` and `smoke_api_v2/taysir/excerpts.jsonl`
2. Pick the best before/after pair (one where the v2 version is noticeably different from campaign)
3. Update `interactions.json` entries for CJ-2 and CJ-3 with actual excerpt text and comparison data

### PRIORITY 3: Validate the web UI works

```bash
python tools/review.py integration_tests/smoke_api_v2/
```

Open localhost:8384 and verify:
- Review mode shows ibn_aqil_v1 + ibn_aqil_v3 (+ taysir if finished) packages
- Questionnaire mode shows all 40 interactions with Arabic text rendering
- Comparison mode works
- Saving a test response creates proper JSONL

### PRIORITY 4: Prepare DR relay prompts for the owner to dispatch

The owner can dispatch ChatGPT DR, Claude DR, and Gemini DR from his phone/browser even without CC. Prepare 3 relay prompts saved to a file the owner can copy-paste:

**File:** `docs/codex/weekend_dr_prompts.md`

**ChatGPT DR prompt:** (has repo access — give file paths)
> Read `rayanino/kr/integration_tests/questionnaire/interactions.json` and `rayanino/kr/NEXT.md`. The owner is spending 3 days reviewing excerpts and answering a 40-interaction questionnaire about what Islamic scholarly excerpts should look like. After the owner finishes, all 6 coworkers will evaluate his responses. To prepare: review the questionnaire design and identify any interactions that might produce ambiguous or low-signal answers. Suggest improvements the owner should know about BEFORE he starts filling it in.

**Claude DR prompt:** (has repo access — give file paths)
> Read `rayanino/kr/integration_tests/questionnaire/interactions.json` and `rayanino/kr/integration_tests/questionnaire/CRITICAL_EVALUATION_GUIDE.md`. The owner will spend Thu-Sun answering this questionnaire. After that, you (Claude DR) will be one of 6 coworkers evaluating his responses for scholarly reasoning soundness. To prepare: read the interactions now and identify which ones you expect the owner to struggle with most (given his "minimum Islamic knowledge" profile). What specific things should you watch for in his responses?

**Gemini DR prompt:** (needs file uploads — upload interactions.json + CRITICAL_EVALUATION_GUIDE.md)
> The owner is spending 3 days answering a questionnaire about Islamic scholarly excerpts. You will evaluate his responses after he finishes. Review the questionnaire now and: (1) identify which interactions test Islamic study methodology that a student might get wrong, (2) prepare your evaluation criteria for each dimension, (3) note any missing dimensions from a pedagogical perspective.

### PRIORITY 5: Environment hardening session

Read `docs/environment_hardening_session_handoff.md`. This describes 5 recurring CC behavior failures that need automated enforcement hooks. Codex can implement the hook infrastructure:

1. Validate all `.claude/rules/*.md` files exist and are referenced
2. Check `.claude/hooks/*.sh` for completeness
3. Add automated checks where prose rules currently exist without enforcement
4. Run `/harness-audit` to check for broken references

### PRIORITY 6: Commit v2 taysir data (if finished)

When taysir completes, its data should be committed:
```bash
git add integration_tests/smoke_api_v2/taysir/
git commit -m "data(excerpting): v2 taysir smoke results — hardened prompts, GPT-5.4 primary"
git push origin master
```

**IMPORTANT:** Do NOT add `raw_llm_requests/` or `raw_llm_responses/` to git — they're too large. Only commit: `excerpts.jsonl`, `progress.jsonl`, `run_metadata.json`, `SUMMARY.json` (if updated), `phase2a_classifications/`, `phase2b_groupings/`.

## Coworker Dispatch Protocol

Codex has repo access and can validate data, but for scholarly reasoning and Arabic quality, the owner should dispatch these DR prompts during the weekend. The prompts are in `docs/codex/weekend_dr_prompts.md`.

**Access capabilities:**
- ChatGPT DR: HAS repo access → file paths only
- Claude DR: HAS repo access → file paths only
- Gemini DR: NO repo access → needs file uploads

## Key Files

| File | What it is |
|------|-----------|
| `NEXT.md` | Master plan with exit conditions for all phases |
| `integration_tests/questionnaire/interactions.json` | 40 questionnaire interactions (structured JSON) |
| `integration_tests/questionnaire/OWNER_QUESTIONNAIRE.md` | The markdown questionnaire (backup/reference) |
| `integration_tests/questionnaire/CRITICAL_EVALUATION_GUIDE.md` | Post-questionnaire 6-coworker evaluation plan |
| `integration_tests/questionnaire/TEAM_TRANSLATION_GUIDE.md` | How to translate answers to SPEC rules |
| `tools/review.py` | Review server (run this for the UI) |
| `tools/excerpt_viewer.html` | The web UI |
| `docs/environment_hardening_session_handoff.md` | Environment fix plan |

## What NOT to Do

- Do NOT modify the excerpting engine code (prompts, phases, contracts)
- Do NOT re-run the smoke test (too expensive, data already available)
- Do NOT modify the questionnaire interactions (they've been reviewed by 6 sources)
- Do NOT present technical decisions to the owner — Codex decides, documents reasoning
