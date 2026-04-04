# Atom-by-Atom Hardening Protocol

> Authority: Governs all future sessions working on excerpting foundations hardening.
> Created: 2026-04-04, session 1.
> Purpose: Ensures every feedback atom from the owner's F1-F8 weekend work is processed to completion, not skipped or summarized.

## Mandate

**No atom is finalized without dedicated reports from ALL THREE coworker tiers:**
1. Codex CLI (`codex exec "..."`) — repo-state challenge, contract pressure, regression risk
2. Gemini CLI (`gemini -p "..."`) — scholarly accuracy, methodology diversity, blind spots
3. At least one DR (ChatGPT DR, Claude DR, or Gemini DR) — deep reasoning, failure modes, architectural implications

**No atom is finalized without empirical validation** where the atom affects prompt behavior. Use `python scripts/atom_test.py --package <pkg> --chunk <n>` for repeatable LLM validation.

## Source Material

The owner's F1-F8 feedback exists in 139 files across 8 collection directories:
- `engines/excerpting/chatgpt_f1_collection/` (16 files + canon)
- `engines/excerpting/chatgpt_f2_collection/` (8 files)
- `engines/excerpting/chatgpt_f3_collection/` (19 files)
- `engines/excerpting/chatgpt_f4_collection/` (19 files)
- `engines/excerpting/chatgpt_f5_collection/` (20 files)
- `engines/excerpting/chatgpt_f6_collection/` (22 files)
- `engines/excerpting/chatgpt_f7_collection/` (17 files)
- `engines/excerpting/chatgpt_f8_collection/` (18 files)

**EVERY FILE must be read.** The collections contain:
- `source_artifacts/` — raw owner text (highest authority)
- `01_questionnaire_answer.md` — cleaned owner answer
- `02_case_dossier.md` / `02_workflow_notes.yaml` — structured analysis
- `03_terms.yaml` — controlled vocabulary
- `04_decision_ladder.jsonl` — step-by-step decision sequences
- `05-08_*` — domain-specific analysis (linking deps, function placement, granularity, etc.)
- `*_nonnegotiables.jsonl` — absolute constraints (HIGHEST IMPLEMENTATION PRIORITY)
- `*_red_team_tests.jsonl` — adversarial test cases (MUST become actual tests)
- `*_priority_matrix.yaml` — priority rankings
- `*_traceability.jsonl` — traces each claim back to owner signal
- `*_open_questions.jsonl` — unresolved questions (must be addressed or explicitly deferred)
- `*_hard_judgment.md` — judgment calls that need human/coworker validation

## Extraction Documents

- `engines/excerpting/reference/F1_F8_COMPLETE_ATOM_EXTRACTION.md` — full extraction (from agent)
- `engines/excerpting/reference/CRITICAL_ATOMS_NONNEGOTIABLES_AND_REDTEAM.md` — highest-priority atoms

## Per-Atom Loop

For each atom from the extraction:

### 1. Identify
- Read the source file and specific entry
- Note the authority level: `owner_explicit` > `owner_consistent_inference` > `model_only`
- `model_only` atoms need owner confirmation before hardening

### 2. Check
- Is it already captured in SPEC §1.1b (FP-1 through FP-18)?
- Is it already in the Phase 2b prompt?
- Is it already tested?
- If fully captured: verify and mark DONE
- If partially captured: identify the gap

### 3. Research
- Search repo for all related prior art (SPEC rules, prompts, contracts, tests)
- Search for counterexamples that pressure the atom
- Search for adjacent engine / contract consequences
- Use `scripts/check_prompt_spec_sync.py` to verify prompt-SPEC alignment

### 4. Dispatch Coworkers (MANDATORY for every atom that affects prompt/SPEC/contracts)
- Codex CLI: structural challenge
- Gemini CLI: scholarly validation
- DR (relay): deep reasoning + failure modes
- Wait for ALL THREE before finalizing

### 5. Implement
- SPEC changes (if doctrinal)
- Prompt changes (if behavioral)
- Contract changes (if structural)
- Test additions (red-team tests from collections become actual pytest cases)

### 6. Validate
- `python -m pytest engines/excerpting/tests/ -q` — zero regressions
- `python -m pyright <modified_files>` — zero errors
- `python scripts/check_prompt_spec_sync.py` — PASSED
- `python scripts/atom_test.py` — empirical validation if prompt-affecting

### 7. Record
- Update `FOUNDATIONS_HARDENING_LEDGER.md` with atom disposition
- Note coworker reports used
- Note unresolved risks

## Session Learnings (from session 1, 2026-04-04)

### Mistakes to avoid:
1. **Never read only the raw source + cleaned answer.** The collections have 12-17 files each. Read ALL of them.
2. **Never skip DR coworkers.** CLI coworkers find structural issues; DR models find reasoning/scholarly issues. Both are needed.
3. **Never batch atoms for shallow processing.** One atom at a time, hours if needed.
4. **Never let Codex or any previous session cap the atom inventory.** The atoms come from the owner's raw feedback, not from prior session definitions.
5. **Check prompt-SPEC sync after every prompt change.** Use `scripts/check_prompt_spec_sync.py`.

### What worked well:
1. Empirical validation (`atom_test.py`) proved more than theoretical analysis
2. Coworker challenges found real issues (Codex: 3 findings, Gemini: 2 gaps, DR: micro-fragment failure)
3. The DR reports (ChatGPT + Claude + Gemini) were the highest-value artifacts of the session
4. The source-surroundings vision came from a live owner Q&A — always ask targeted questions
