# Weekend Handoff to Codex -- 2026-04-01 (DEFINITIVE)

> **Codex operates autonomously for hours. No human guidance available.**
> **Every decision Codex makes here directly affects the owner's Islamic study tool.**
> **Read this document in full before starting any work.**

---

## SECTION 1: CURRENT STATE (exact numbers, verified 2026-04-01 ~17:00 UTC)

### V2 Smoke Run Status

| Package | Status | Excerpts | Errors | Cost | Time |
|---------|--------|----------|--------|------|------|
| ibn_aqil_v1 | COMPLETE | 241 | 3 (2x EX-V-002 + 2 chunk failures) | $4.40 | 44 min |
| ibn_aqil_v3 | COMPLETE | 278 | 6 (5x EX-V-002 + 1 chunk failure) | $4.30 | 45 min |
| taysir | RUNNING | pending | 0 so far | ~$46 est | ongoing |

**Taysir live status (as of handoff):**
- `progress.jsonl`: 564 entries total
- Phase 2a classifications: 180 files (all 184 chunks done, minus failures)
- Phase 2b groupings: 179 files
- Phase 3 consensus: 21 of ~184 chunks done (last entry at 14:53 UTC)
- Phase 2a failures: `phase2a_failures.jsonl` exists (small, expected)
- Phase 2b failures: `phase2b_failures.jsonl` exists (1 line)
- No `excerpts.jsonl` yet -- run still in Phase 3 enrichment pipeline
- No `run_metadata.json` yet
- No `SUMMARY.json` for taysir yet
- Estimated time remaining: 2-4 hours (163 chunks left in phase3 at ~2 min/chunk)
- Raw LLM data accumulating in `raw_llm_requests/` and `raw_llm_responses/` (large, do NOT commit)

**Completed packages already have:** `excerpts.jsonl`, `run_metadata.json`, `processing_log.jsonl`, `progress.jsonl`, `timing.json`, `phase1_chunks.json`, `phase2a_classifications/`, `phase2b_groupings/`, `cache/`, `raw_llm_requests/`, `raw_llm_responses/`

### Campaign Baseline (for comparison)

| Package | Campaign Excerpts | V2 Excerpts | Delta |
|---------|-------------------|-------------|-------|
| ibn_aqil_v1 | 241 | 241 | 0 |
| ibn_aqil_v3 | 282 | 278 | -4 |
| taysir | 1,283 | pending | pending |

Campaign total: 2,303 excerpts across 5 packages. Cost: $96.87. Model: Claude Opus (old prompts).
V2 uses: GPT-5.4 primary (hardened prompts H-1 through H-8).

### Questionnaire Status

- `interactions.json`: 40 interactions (verified, JSON array with 40 objects)
- Phases: foundations (F-1 through F-8), deep_dives (G-1 through G-4, SC-1 through SC-4, D-1 through D-3, E-1 through E-3, K-1 through K-3, GN-1 through GN-2, L-1 through L-3, QA-1), comparative (CJ-1 through CJ-4), synthesis (S-1 through S-3)
- CJ-2 (Before/After) and CJ-3 (Cross-Book) are PLACEHOLDERS -- `excerpt_text` is null, `context_note` has placeholder descriptions
- Web UI: `tools/excerpt_viewer.html` served by `tools/review.py` at localhost:8384
- Review modes: Review (browse excerpts), Questionnaire (40 interactions), Comparison (before/after)
- Existing review artifacts: `V2_BEFORE_AFTER_COMPARISON.md` and `V2_EXCERPT_REVIEW_PACKAGE.md` already created (ibn_aqil data only)

### Environment Status

- 3 enforcement rules added in `.claude/rules/` (mandatory-coworker-dispatch, dr-dispatch-checklist, post-milestone-protocol)
- 5 role violations fixed in this session
- NEXT.md rewritten: 382 lines with exit conditions and ownership for every step
- All changes committed and pushed to remote (commit `e63c1511`, plus `092c1aa2` fix for false positives)
- `.kr/runtime/dispatch_log.jsonl` exists (empty -- Codex should populate as it works)

---

## SECTION 2: CODEX'S MISSION

The owner has a 3-day offline window (Thu-Sun). During this time the owner will:

1. **Answer 40 questionnaire interactions** via the web UI (estimated 10-15 hours)
2. **Review v2 excerpts** in Review mode (3-5 hours)
3. **Judge before/after comparisons** between campaign and v2 data (1-2 hours)
4. **Dispatch DR prompts** to ChatGPT/Claude/Gemini from his phone (owner relays prompts prepared by Codex)

**Codex's job: ensure the owner's time is NOT wasted.** Every hour the owner spends reviewing must produce maximum signal. That means:

- All data is ready and accessible before the owner starts
- The web UI works end-to-end with real data
- CJ-2/CJ-3 placeholders are filled with real Arabic text (not JSON blobs)
- DR prompts are written so the owner can copy-paste them without editing
- Taysir-specific review materials exist (taysir is the book the owner already gave feedback on -- highest signal)
- Before/after regression analysis is computed so the teams have Phase 1 data ready

**Codex is the SENIOR ENGINEER. The owner is the CLIENT.**
- Codex decides what to do and in what order
- Codex never asks the owner technical questions
- Codex documents all decisions with reasoning
- Codex logs every coworker dispatch to `.kr/runtime/dispatch_log.jsonl`

---

## SECTION 3: PRIORITY TASKS (numbered, sequential)

### Task 1: Monitor taysir v2 completion

**Goal:** Detect when taysir finishes and commit its output.

**Steps:**

1. Check completion status (run ONCE — do not loop/poll):
   ```bash
   ls integration_tests/smoke_api_v2/taysir/excerpts.jsonl 2>/dev/null && echo "DONE" || echo "NOT DONE"
   ```
   - If `excerpts.jsonl` exists: taysir is DONE. Proceed to step 3.
   - If NOT: check progress with:
     ```bash
     python3 -c "import json; lines=[json.loads(l) for l in open('integration_tests/smoke_api_v2/taysir/progress.jsonl') if l.strip()]; p3=[l for l in lines if l.get('phase')=='phase3_consensus' and l.get('status')=='done']; print(f'{len(p3)}/184 phase3 done, {len(lines)} total entries')"
     ```
   - If NOT done: **skip Tasks 2, 4, 5** (they depend on taysir) and proceed to Tasks 3, 6, 7 with ibn_aqil data only. Document: "Taysir was still running. CJ-2/CJ-3 remain placeholders. Taysir review package deferred."
   - The run was at ~31/184 phase3_consensus as of handoff. It should finish within 2-4 hours on its own.
   
2. **Completion indicators** (all must exist):
   - `integration_tests/smoke_api_v2/taysir/excerpts.jsonl` -- the final output
   - File size > 0 and valid JSONL (each line parses as JSON)
   
3. When `excerpts.jsonl` appears:
   - Count lines: `wc -l integration_tests/smoke_api_v2/taysir/excerpts.jsonl`
   - Expected range: 800-1,500 excerpts (campaign produced 1,283 with old prompts + Opus)
   - Update `integration_tests/smoke_api_v2/SUMMARY.json` with taysir stats (see ibn_aqil entries for format)
   - Verify `run_metadata.json` exists

4. **Commit the completion data:**
   ```bash
   git add integration_tests/smoke_api_v2/taysir/excerpts.jsonl
   git add integration_tests/smoke_api_v2/taysir/progress.jsonl
   git add integration_tests/smoke_api_v2/taysir/run_metadata.json  # if exists
   git add integration_tests/smoke_api_v2/taysir/phase2a_classifications/
   git add integration_tests/smoke_api_v2/taysir/phase2a_failures.jsonl
   git add integration_tests/smoke_api_v2/taysir/phase2b_groupings/
   git add integration_tests/smoke_api_v2/taysir/phase2b_failures.jsonl
   git add integration_tests/smoke_api_v2/SUMMARY.json
   git commit -m "data(excerpting): v2 taysir smoke results -- hardened prompts, GPT-5.4 primary"
   git push origin master
   ```
   **NEVER add `raw_llm_requests/` or `raw_llm_responses/` to git.** They are too large.
   **NEVER add `cache/` to git.** It contains intermediate LLM cache data.

5. **If taysir stalls** (no new progress.jsonl entry for >1 hour):
   - Document the stall: last timestamp, last chunk ID, phase reached
   - Check if the process is still running (look for active writes to `raw_llm_responses/`)
   - Do NOT restart the run -- document and proceed with available data
   - Create `integration_tests/smoke_api_v2/taysir/STALL_REPORT.md` with findings

### Task 2: Fill CJ-2 and CJ-3 in interactions.json

**Depends on:** Task 1 (taysir must be complete)

**Goal:** Turn the CJ-2 and CJ-3 placeholder interactions into real before/after and cross-book comparisons with actual Arabic text.

**BEFORE MODIFYING: Back up the validated file:**
```bash
cp integration_tests/questionnaire/interactions.json integration_tests/questionnaire/interactions.json.bak
```

**CJ-2 (Before/After Comparison):**

1. Load both files:
   - Campaign (old): `integration_tests/campaign_20260331/taysir/excerpts.jsonl` (1,283 lines)
   - V2 (new): `integration_tests/smoke_api_v2/taysir/excerpts.jsonl` (pending)

2. Find excerpts from the SAME division (match on `div_id` field in the excerpt JSON). If `div_id` is not present, match on `chunk_id` or the division path component of the `excerpt_id` string.

3. Pick 1-2 pairs where the v2 version is noticeably different from campaign:
   - Different boundaries (excerpt covers more or less text)
   - Different classification (`primary_function` changed)
   - Different self-containment rating
   - Different excerpt count for the same division

4. Update the CJ-2 entry in `interactions.json`:
   - Set `excerpt_text` to the v2 excerpt's Arabic text
   - Set `context_note` to describe what changed, including the campaign version's text
   - Keep `question` and `multiple_choice` as-is (they are already correct)

**CJ-3 (Cross-Book Comparison):**

1. Load excerpts from at least 2 books in the campaign data:
   - `integration_tests/campaign_20260331/taysir/excerpts.jsonl` (fiqh/hadith)
   - `integration_tests/campaign_20260331/ibn_aqil_v1/excerpts.jsonl` (nahw/grammar)
   
2. Find topics that appear in both books (if any). Look for:
   - Shared terminology (e.g., both discuss definitions, both discuss scholarly disagreement)
   - Both books have excerpts classified with the same `primary_function`

3. If no natural cross-book match exists between taysir (fiqh) and ibn_aqil (nahw), use the `context_note` to describe the comparison conceptually and leave `excerpt_text` null with a note explaining why.

4. Update the CJ-3 entry in `interactions.json` with the best match found.

**Validation after update:**
- `python -c "import json; d=json.load(open('integration_tests/questionnaire/interactions.json','r',encoding='utf-8')); print(len(d), 'interactions'); print([x['id'] for x in d if x['excerpt_text'] is None])"` -- verify CJ-2/CJ-3 are filled (or documented as unfillable)

### Task 3: Create DR relay prompts

**Goal:** `docs/codex/weekend_dr_prompts.md` ALREADY EXISTS with 3 prompts (created by CC this session). Do NOT overwrite it. Review the existing file — if the prompts are complete and have step-by-step instructions for the owner, SKIP this task. If missing tool-opening instructions (how to access Deep Research mode in each app), add them.

**ChatGPT DR** (HAS private repo access via GitHub -- give FILE PATHS only, NEVER paste content):

```
Read the following files in the repository rayanino/kr:
- integration_tests/questionnaire/interactions.json
- NEXT.md (lines 1-100 for Phase 0 context)

CONTEXT: The KR project owner is spending Thu-Sun answering a 40-interaction questionnaire about what Islamic scholarly excerpts should look like. After completion, 6 coworkers (including you) will evaluate his responses using the protocol in integration_tests/questionnaire/CRITICAL_EVALUATION_GUIDE.md.

TASK: Review the questionnaire design and prepare for your evaluation role.

SPECIFIC QUESTIONS:
1. Which interactions will produce the highest-signal answers for calibrating an excerpting pipeline?
2. Which interactions might produce ambiguous answers that are hard to translate into concrete rules?
3. Are there any interactions where the multiple-choice options do not cover the most likely answer?
4. The owner has "minimum Islamic knowledge" -- which interactions risk confusing him?
5. Suggest any last-minute improvements the owner should know about BEFORE starting.

OUTPUT: Structured report with per-interaction assessment where relevant.
```

**Claude DR** (HAS private repo access via GitHub -- give FILE PATHS only, NEVER paste content):

```
Read the following files in the repository rayanino/kr:
- integration_tests/questionnaire/interactions.json
- integration_tests/questionnaire/CRITICAL_EVALUATION_GUIDE.md

CONTEXT: The KR project owner will spend Thu-Sun answering this questionnaire about Islamic scholarly excerpts. You (Claude DR) will be one of 6 coworkers evaluating his responses for scholarly reasoning soundness.

TASK: Prepare for your evaluation role by reviewing the questionnaire now.

SPECIFIC QUESTIONS:
1. Which interactions do you expect the owner (minimum Islamic knowledge, Muslim student) to struggle with most?
2. For the edge-case interactions (marked is_edge_case: true -- SC-1, SC-2, D-1, D-2, E-1, E-2, E-3), what specific things should you watch for in his responses?
3. What contradictions might naturally emerge between his answers to different interactions?
4. Which dimensions (granularity, self-containment, definition handling, evidence handling, khilaf, genre, layers) do you expect the owner to have the strongest vs weakest intuition about?
5. What evaluation criteria will you use for each dimension?

OUTPUT: Structured evaluation preparation report, organized by dimension.
```

**Gemini DR** (CANNOT access the repo -- needs FILE UPLOADS):

Owner instructions: Upload these 2 files to the Gemini session:
- `integration_tests/questionnaire/interactions.json` (40 interactions, ~16KB)
- `integration_tests/questionnaire/CRITICAL_EVALUATION_GUIDE.md` (~4KB)

Prompt:
```
I am uploading two files from the KR project -- a questionnaire about Islamic scholarly excerpts and the evaluation guide for assessing the owner's responses.

CONTEXT: A Muslim student with minimum Islamic knowledge is spending 3 days answering this questionnaire. After completion, 6 coworkers will evaluate his responses. You are one of the evaluators, focusing on pedagogical alignment.

TASK: Prepare for your pedagogical evaluation role.

SPECIFIC QUESTIONS:
1. Which interactions test Islamic study methodology (manhaj) that a student might get wrong?
2. For interactions about genre differences (GN-1, GN-2): does the questionnaire adequately test whether the owner understands how different Islamic sciences structure knowledge differently?
3. For interactions about scholarly disagreement (K-1, K-2, K-3): does the questionnaire test whether the owner understands classical dialectical structure (munadhara) or only modern listed formats?
4. What evaluation criteria will you use for each dimension from a pedagogical perspective?
5. Are there study workflow patterns (مراجعة, مذاكرة, تحقيق) that the excerpts should support but the questionnaire does not cover?

OUTPUT: Pedagogical evaluation preparation report with specific criteria per interaction type.
```

### Task 4: Generate taysir-specific review package

**Depends on:** Task 1 (taysir must be complete)

**Goal:** Create `integration_tests/questionnaire/V2_TAYSIR_REVIEW.md` -- a focused review package for the owner.

**Why taysir is high-value:** Taysir is the book the owner already gave feedback on (`integration_tests/campaign_20260331/taysir/owner_feedback.jsonl` -- 2 reviews that triggered the entire granularity debate). Reviewing taysir v2 excerpts gives the highest signal because the owner has context.

**Steps:**

1. Load `integration_tests/smoke_api_v2/taysir/excerpts.jsonl`

2. Select 30 diverse excerpts:
   - 10 short (< 200 characters of `primary_text`)
   - 10 medium (200-800 characters)
   - 10 long (> 800 characters)
   - Include any with `self_containment: "PARTIAL"` (boundary quality signal)
   - Prefer diversity in `primary_function` (ruling_explanation, evidence_citation, definition, scholarly_disagreement, etc.)

3. Render as markdown with this template per excerpt:

   ```markdown
   ## Excerpt N (SHORT/MEDIUM/LONG) -- taysir v2

   **Type:** {primary_function} | **Self-contained:** {self_containment} | **Length:** {char_count} chars

   > {primary_text in Arabic}

   **Quick rating:** [ ] Good  [ ] Acceptable  [ ] Needs work  [ ] Bad

   **Why:**
   >

   **What would you change?**
   >
   ```

4. Save to `integration_tests/questionnaire/V2_TAYSIR_REVIEW.md`

5. Commit:
   ```bash
   git add integration_tests/questionnaire/V2_TAYSIR_REVIEW.md
   git commit -m "docs(excerpting): taysir v2 review package -- 30 diverse excerpts for owner review"
   ```

### Task 5: Before/After regression analysis

**Depends on:** Task 1 (taysir must be complete)

**Goal:** Quantitative comparison of campaign (old prompts, Opus) vs v2 (hardened prompts, GPT-5.4).

**Steps:**

1. Create the analysis directory: `mkdir -p integration_tests/smoke_api_v2/analysis/`

2. For each book that exists in both campaign and v2 (ibn_aqil_v1, ibn_aqil_v3, taysir), compute:
   - **Excerpt count change:** campaign count vs v2 count (absolute and percentage)
   - **Average excerpt length change:** mean character count of `primary_text`
   - **Self-containment distribution:** count of FULL vs PARTIAL vs NONE in each run
   - **Function distribution:** count per `primary_function` value in each run
   - **Error count change:** campaign errors vs v2 errors
   - **Cost change:** campaign cost vs v2 cost per package

3. For ibn_aqil books specifically (same model ecosystem, same data):
   - Identify excerpts that changed between runs (different text, different boundaries)
   - Count how many are identical vs changed

4. Save as `integration_tests/smoke_api_v2/analysis/BEFORE_AFTER_REGRESSION.md` with:
   - Summary table (all books)
   - Per-book detailed comparison
   - Key observations (improvements, regressions, surprises)
   - Recommendation for Phase 1 focus areas

5. Commit:
   ```bash
   git add integration_tests/smoke_api_v2/analysis/
   git commit -m "docs(excerpting): before/after regression analysis -- campaign vs v2 hardened"
   ```

### Task 6: Validate web UI end-to-end

**Goal:** Verify the owner can actually use the review system without hitting errors.

**Steps:**

1. Start the server:
   ```bash
   python tools/review.py integration_tests/smoke_api_v2/
   ```

2. Test each API endpoint:
   - `GET /api/packages` -- should return `["ibn_aqil_v1", "ibn_aqil_v3", "taysir"]` (taysir only if finished)
   - `GET /api/excerpts/ibn_aqil_v1` -- should return 241 excerpt objects
   - `GET /api/excerpts/ibn_aqil_v3` -- should return 278 excerpt objects
   - `GET /api/questionnaire` -- should return 40 interaction objects
   - `GET /api/questionnaire/responses` -- should return empty dict (no responses yet)
   - `GET /api/comparisons` -- should return comparison data (may be empty if CJ-2/CJ-3 not filled)
   - `POST /api/questionnaire/response` -- submit a test response, verify JSONL is created
   - `POST /api/feedback/ibn_aqil_v1` -- submit a test feedback entry, verify JSONL is created

3. After submitting test data:
   - Verify `integration_tests/questionnaire/responses.jsonl` (or similar) was created
   - Verify the response can be read back via `GET /api/questionnaire/responses`
   - **Delete the test response data** so the owner starts clean

4. Check for common issues:
   - Arabic text rendering (RTL, diacritics)
   - JSON encoding (`ensure_ascii=False` in responses)
   - Path traversal protection (`_safe_pkg_path` function)
   - CORS headers (if the owner opens the UI from a different origin)

5. If issues found: fix them, run tests, commit:
   ```bash
   git add tools/review.py tools/excerpt_viewer.html
   git commit -m "fix(tools): web UI issues found during end-to-end validation"
   ```

### Excerpt JSONL Schema Reference

Every line in `excerpts.jsonl` is a JSON object with these key fields (use for Tasks 2, 4, 5):

| Field | Type | Use for matching/analysis |
|-------|------|--------------------------|
| `excerpt_id` | str | Unique ID (NOT stable across runs — do NOT match on this) |
| `div_id` | str | Division ID — use for MATCHING across campaign vs v2 |
| `primary_text` | str | Full Arabic text of the excerpt |
| `primary_function` | str | Classification (definition, rule_statement, evidence_hadith, etc.) |
| `self_containment` | str | FULL / PARTIAL / DEPENDENT |
| `context_hint` | str/null | Context note for PARTIAL excerpts |
| `excerpt_topic` | list[str] | Topic keywords |
| `school` | str/null | School attribution if detected |
| `div_path` | list[str] | Structural path in the book |
| `start_word` / `end_word` | int | Word offsets in the chunk |

**Matching campaign vs v2:** Use `div_id` to find excerpts from the same book division across both runs.
**"Noticeably different" criteria for Task 2:** Use mechanical checks: `primary_function` differs, OR `len(primary_text)` ratio > 1.3 or < 0.7, OR `self_containment` differs.

---

### Task 7: Environment hardening (if time allows)

**Depends on:** Tasks 1-6 complete or blocked

**Context:** Read `docs/environment_hardening_session_handoff.md` for the full problem description.

**Focus on these 2 highest-value items:**

1. **Stale reference detection:**
   - Check all files in `.claude/rules/` for references to files that do not exist
   - Check all files in `.claude/agents/` for references to nonexistent files
   - Check `CLAUDE.md` references
   - Report findings but do not auto-fix (references may be intentionally forward-looking)

2. **Dispatch log population:**
   - `.kr/runtime/dispatch_log.jsonl` exists but is empty
   - As Codex works through Tasks 1-6, log every significant action to this file
   - Format per entry: `{"timestamp": "ISO8601", "agent": "codex", "phase": "weekend_handoff", "task": "...", "action": "...", "result_summary": "..."}`

---

## SECTION 4: WHAT NOT TO DO

| Forbidden Action | Why |
|------------------|-----|
| Modify excerpting engine code (prompts, phases, contracts) | Pipeline code is frozen during evaluation |
| Re-run the smoke test | Too expensive (~$50), data is already being produced |
| Modify questionnaire interactions (except CJ-2/CJ-3 placeholders) | Reviewed and validated by 6 sources |
| Present technical decisions to the owner | Owner is the CLIENT, not the engineer |
| Add `raw_llm_requests/` or `raw_llm_responses/` to git | Too large (hundreds of MB) |
| Add `cache/` directories to git | Intermediate LLM cache, too large |
| Delete ANY data (raw responses, excerpts, logs) | All data is future training material (Rule 13) |
| Kill or restart the taysir run | It is progressing; interruption would lose partial progress |
| Modify `SUMMARY.json` after writing it | Append corrections as `SUMMARY_patch_YYYYMMDD.json` |
| Overwrite `integration_tests/smoke_api_v2/` | This directory is the v2 data source -- never overwrite |

---

## SECTION 5: KEY RULES

### Coworker Access Model

| Coworker | Repo Access | How to Provide Data |
|----------|-------------|---------------------|
| ChatGPT DR | YES (private repo via GitHub) | Give FILE PATHS only: `rayanino/kr/path/to/file` |
| Claude DR | YES (private repo via GitHub) | Give FILE PATHS only: `rayanino/kr/path/to/file` |
| Gemini DR | NO | Prepare FILE UPLOADS for the owner to attach |
| ChatGPT (non-DR/Thinking) | NO | Paste content or upload files |
| Gemini CLI | YES (local repo) | Direct file access via `gemini -p` |
| Codex CLI | YES (local repo) | Direct file access via `codex exec` |

**NEVER paste full file contents into ChatGPT DR or Claude DR prompts.** The owner explicitly said (2026-04-01): "NEVER make this mistake again."

### Data Rules

- All data is future LLM training material (CLAUDE.md Rule 13) -- NEVER delete data
- Every excerpt, API response, evaluation trace, owner feedback entry is preserved with provenance
- Raw LLM responses stay on disk but not in git (too large)
- `excerpts.jsonl` is the canonical output -- never overwrite, copy to dated backup before any re-run

### Role Rules

- Codex is the SENIOR ENGINEER and PRODUCT LEAD
- The owner is the CLIENT with minimum Islamic knowledge and zero technology skills
- Ask experience questions ("How does this feel?"), never technical questions ("Should we modify the SPEC?")
- After every task: identify what was accomplished, what it reveals, and propose next steps
- Never end with "standing by" or "waiting for your input"

### Dispatch Logging

Every significant action logged to `.kr/runtime/dispatch_log.jsonl`:
```json
{"timestamp": "2026-04-01T18:00:00Z", "agent": "codex", "phase": "weekend_handoff", "task": "task_1_monitor_taysir", "action": "polled progress.jsonl", "result_summary": "25/184 phase3 done"}
```

---

## SECTION 6: FILES REFERENCE TABLE

### Critical Files (Codex reads/writes these)

| File | Purpose | Read/Write |
|------|---------|------------|
| `integration_tests/smoke_api_v2/taysir/progress.jsonl` | Live run progress (poll this) | READ |
| `integration_tests/smoke_api_v2/taysir/excerpts.jsonl` | Final taysir v2 output (appears when done) | READ |
| `integration_tests/smoke_api_v2/SUMMARY.json` | Aggregate stats for v2 run (update when taysir finishes) | READ+WRITE |
| `integration_tests/questionnaire/interactions.json` | 40 questionnaire interactions (update CJ-2/CJ-3 only) | READ+WRITE |
| `integration_tests/questionnaire/V2_TAYSIR_REVIEW.md` | Taysir review package (Codex creates) | WRITE |
| `integration_tests/smoke_api_v2/analysis/BEFORE_AFTER_REGRESSION.md` | Regression analysis (Codex creates) | WRITE |
| `docs/codex/weekend_dr_prompts.md` | DR relay prompts for owner (Codex creates) | WRITE |
| `.kr/runtime/dispatch_log.jsonl` | Dispatch log (Codex populates) | WRITE |
| `tools/review.py` | Review server (fix if broken) | READ+WRITE |
| `tools/excerpt_viewer.html` | Web UI (fix if broken) | READ+WRITE |

### Reference Files (Codex reads these for context)

| File | Purpose |
|------|---------|
| `NEXT.md` | Master plan with exit conditions for all phases |
| `CLAUDE.md` | Project rules and pipeline description |
| `integration_tests/questionnaire/CRITICAL_EVALUATION_GUIDE.md` | Post-questionnaire 6-coworker evaluation protocol |
| `integration_tests/questionnaire/TEAM_TRANSLATION_GUIDE.md` | How to translate owner answers to SPEC rules |
| `integration_tests/questionnaire/OWNER_QUESTIONNAIRE.md` | The markdown questionnaire (backup/reference) |
| `integration_tests/questionnaire/RESPONSE_FORMAT.md` | Response template for each interaction |
| `integration_tests/questionnaire/QUESTIONNAIRE_EXAMPLES.md` | Real excerpt examples for each interaction |
| `integration_tests/questionnaire/excerpt_selections.json` | Machine-readable excerpt selection index |
| `integration_tests/questionnaire/V2_BEFORE_AFTER_COMPARISON.md` | Existing ibn_aqil before/after comparison |
| `integration_tests/questionnaire/V2_EXCERPT_REVIEW_PACKAGE.md` | Existing ibn_aqil review package (19 excerpts) |
| `integration_tests/questionnaire/START_HERE.md` | Owner-facing start guide |
| `docs/environment_hardening_session_handoff.md` | Environment fix plan (5 failure patterns) |
| `docs/codex/dispatch-templates.md` | Codex dispatch templates for agents |

### Campaign Data (read-only, for comparison)

| File | Purpose |
|------|---------|
| `integration_tests/campaign_20260331/taysir/excerpts.jsonl` | 1,283 taysir excerpts (old prompts, Opus) |
| `integration_tests/campaign_20260331/ibn_aqil_v1/excerpts.jsonl` | 241 excerpts (old prompts, Opus) |
| `integration_tests/campaign_20260331/ibn_aqil_v3/excerpts.jsonl` | 282 excerpts (old prompts, Opus) |
| `integration_tests/campaign_20260331/taysir/owner_feedback.jsonl` | 2 owner reviews that triggered granularity debate |
| `integration_tests/campaign_20260331/SUMMARY.json` | Campaign aggregate stats (5 pkgs, 2,303 excerpts, $96.87) |
| `integration_tests/campaign_20260331/analysis/` | 19 analysis files (catalog, gold candidates, fidelity flags, etc.) |

### V2 Smoke Data (read + update SUMMARY.json)

| File | Purpose |
|------|---------|
| `integration_tests/smoke_api_v2/ibn_aqil_v1/excerpts.jsonl` | 241 v2 excerpts |
| `integration_tests/smoke_api_v2/ibn_aqil_v3/excerpts.jsonl` | 278 v2 excerpts |
| `integration_tests/smoke_api_v2/taysir/` | In-progress taysir v2 run |
| `integration_tests/smoke_api_v2/SUMMARY.json` | Partial summary (2 packages, needs taysir added) |

### Infrastructure

| File | Purpose |
|------|---------|
| `.claude/rules/mandatory-coworker-dispatch.md` | Dispatch enforcement rule |
| `.claude/rules/dr-dispatch-checklist.md` | DR access rules (who has repo access) |
| `.claude/rules/no-single-model-conclusion.md` | No single-model content conclusions |
| `.claude/skills/coworker-dispatch/SKILL.md` | Master coworker dispatch protocol |
| `scripts/run_full_integration.py` | Integration runner (do NOT run -- just reference) |

---

## SECTION 7: TASK DEPENDENCY GRAPH

```
Task 1 (Monitor taysir) ──────┬──> Task 2 (Fill CJ-2/CJ-3)
                               ├──> Task 4 (Taysir review package)
                               └──> Task 5 (Regression analysis)

Task 3 (DR prompts) ──────────── independent, do immediately

Task 6 (Validate web UI) ─────── independent, do after Task 2

Task 7 (Environment hardening) ── lowest priority, fill time
```

**Execution order:**
1. Start Task 3 immediately (no dependencies)
2. Start polling for Task 1 (check every 10-15 minutes)
3. While waiting for taysir: do Task 6 (with ibn_aqil data) and Task 7
4. When taysir finishes: Task 2 then Task 4 then Task 5
5. Re-run Task 6 validation after Task 2 updates interactions.json

---

## SECTION 8: SUCCESS CRITERIA

When Codex is done, the owner should be able to:

1. Run `python tools/review.py integration_tests/smoke_api_v2/` and see all 3 packages
2. Open the Questionnaire tab and see 40 interactions with Arabic text (including CJ-2/CJ-3 with real data)
3. Open the Comparison tab and see before/after pairs
4. Copy-paste 3 DR prompts from `docs/codex/weekend_dr_prompts.md` to his phone
5. Read `integration_tests/questionnaire/V2_TAYSIR_REVIEW.md` offline and rate 30 excerpts
6. The engineering team can read `integration_tests/smoke_api_v2/analysis/BEFORE_AFTER_REGRESSION.md` for Phase 1 data

All artifacts committed and pushed to `master`. Dispatch log populated. No uncommitted changes.
