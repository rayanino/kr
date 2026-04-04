# Atom-by-Atom Hardening Protocol

> **Authority:** ABSOLUTE. Governs ALL future sessions working on excerpting foundations hardening. No session may deviate from this protocol.
> **Created:** 2026-04-04, session 1.
> **Why this exists:** The owner spent an ENTIRE WEEKEND (15+ hours) working with ChatGPT to produce 139 files of structured, machine-readable feedback across 8 collections (F1-F8). This is the highest-value owner input the project has EVER received. A previous Codex handoff session caused the first CC session to drift and nearly waste this data. THIS PROTOCOL PREVENTS THAT FROM HAPPENING AGAIN.

---

## STOP — READ THIS FIRST

**Before doing ANYTHING in a hardening session:**

1. Read this entire protocol
2. Read `.kr/HANDOFF.md`
3. Read `engines/excerpting/reference/FOUNDATIONS_HARDENING_LEDGER.md`
4. Read `engines/excerpting/reference/F1_F8_COMPLETE_ATOM_EXTRACTION.md`
5. Verify you are on branch `excerpting-foundations-hardening-20260404`
6. Run `python -m pytest engines/excerpting/tests/ -q --ignore=engines/excerpting/tests/test_phase2_integration.py --ignore=engines/excerpting/tests/test_phase3_integration.py` — must be 907+ pass
7. Run `python scripts/check_prompt_spec_sync.py` — must PASS

**Do NOT start implementing until all 7 checks pass.**

---

## The 139 Files — What They Are and Why They Matter

The owner filled in 8 foundation questions (F1-F8) about excerpting quality. For each question, the owner worked IN-DEPTH with ChatGPT to produce a structured collection:

| File Type | What It Contains | How to Use It |
|-----------|-----------------|---------------|
| `source_artifacts/*.txt` | **Raw owner text** — first-person reactions, notes, realizations. HIGHEST authority. | Read FIRST for every atom. This is the ground truth. |
| `01_questionnaire_answer.md` | Cleaned owner answer with confidence level | Read second. The owner's distilled position. |
| `02_*.md` / `02_*.yaml` | Case dossier / workflow notes — structured analysis | The analytical backbone. Contains layered assessment. |
| `03_terms.yaml` | Controlled vocabulary with dangerous competing meanings | Use to avoid term confusion in SPEC/prompt wording. |
| `04_decision_ladder.jsonl` | Step-by-step decision sequences | Shows HOW the owner reasoned about boundary decisions. |
| `05-08_*` | Domain-specific analysis (linking deps, function placement, granularity, proofs, variants, memorization) | Deep domain data. EVERY file has atoms. |
| `*_nonnegotiables.jsonl` | **ABSOLUTE CONSTRAINTS** — things that MUST NEVER happen | HIGHEST IMPLEMENTATION PRIORITY. These become hard SPEC rules. |
| `*_red_team_tests.jsonl` | **Adversarial test cases** — designed to break the engine | MUST become actual pytest cases. If a red-team test passes, the engine has a hole. |
| `*_priority_matrix.yaml` | Priority rankings for dimensions | Use to order implementation work. |
| `*_traceability.jsonl` | Links each claim back to owner signal | Use to verify that SPEC rules trace to real owner feedback. |
| `*_open_questions.jsonl` | Unresolved questions | Must be addressed or explicitly deferred with reasoning. |
| `*_hard_judgment.md` | Judgment calls that need validation | Dispatch to coworkers for independent assessment. |

**The 81 atoms extracted in `F1_F8_COMPLETE_ATOM_EXTRACTION.md` are a STARTING POINT, not a cap.** The next session may find additional atoms by reading files the extraction agent missed or summarized. Always go back to the original files.

---

## Per-Atom Loop — THE EXACT STEPS

### Step 0: Select the Next Atom
- Use the extraction document (`F1_F8_COMPLETE_ATOM_EXTRACTION.md`) as the queue
- Prioritize: nonnegotiable atoms > red-team test atoms > prompt-affecting atoms > SPEC-only atoms > deferred atoms
- Process ONE atom at a time. Never batch.

### Step 1: Read the Original Source (10 min)
- Go to the COLLECTION DIRECTORY (e.g., `chatgpt_f3_collection/`)
- Read the RAW OWNER SOURCE first (`source_artifacts/*.txt`)
- Read the cleaned answer (`01_questionnaire_answer.md`)
- Read the SPECIFIC FILE the atom came from (e.g., `09_nonnegotiables.jsonl` entry NN-003)
- Read the traceability entry for this atom (`*_traceability.jsonl`)
- Note the authority level: `owner_explicit` (do not weaken) / `owner_consistent_inference` (may refine) / `model_only` (must verify with owner)

### Step 2: Check Current State (5 min)
- Is it already captured in SPEC §1.1b (FP-1 through FP-18)?
- Is it already in the Phase 2b prompt (`phase2_group.py`)?
- Is it already tested?
- Run `python scripts/check_prompt_spec_sync.py`
- If fully captured AND correctly captured: verify, mark DONE, move to next atom
- If partially captured: identify the specific gap

### Step 3: Research (20 min)
Prepare THREE research prompts. The same three prompts go to ALL THREE coworkers (x3 research):

**Prompt A — Repo/Implementation Challenge:**
"Read [specific files]. Does the current implementation correctly handle [atom]? What would break if [atom] is wrong? What contracts/tests/prompts need to change?"

**Prompt B — Scholarly/Domain Challenge:**
"In Islamic scholarly texts, is [atom] correct? Give concrete Arabic examples where [atom] holds and where it fails. What Islamic science is most at risk if [atom] is wrong?"

**Prompt C — Adversarial/Failure Mode Challenge:**
"What is the WORST thing that happens if [atom] is implemented incorrectly? Give a concrete scenario where the engine produces a confidently wrong excerpt because of [atom]. What silent corruption path does [atom] open or close?"

### Step 4: Dispatch ALL THREE Coworkers — EACH GETS ALL THREE PROMPTS (mandatory)

**Codex CLI** — gets prompts A + B + C:
```
codex exec "PROMPT A: [repo challenge]
PROMPT B: [scholarly challenge]
PROMPT C: [adversarial challenge]
OUTPUT: Structured findings per prompt with file:line references."
```

**Gemini CLI** — gets prompts A + B + C:
```
gemini -p "PROMPT A: [repo challenge]
PROMPT B: [scholarly challenge]
PROMPT C: [adversarial challenge]
OUTPUT: Structured findings per prompt with Arabic examples."
```

**DR (relay to owner)** — gets prompts A + B + C:
Write the relay prompt with all three sub-prompts. Specify file paths for ChatGPT/Claude DR, or prepare a file bundle for Gemini DR.

**WAIT for ALL THREE to return before proceeding.** Do not implement with partial coworker coverage.

### Step 5: Synthesize Findings (15 min)
- Create a 3-column comparison: Codex | Gemini | DR
- Where do they AGREE? → high confidence
- Where do they DISAGREE? → needs resolution (owner Q&A or additional research)
- Where did they find things the atom MISSED? → expand the atom
- Record the synthesis in the ledger

### Step 6: Ask Owner (if needed)
- Only for: `model_only` atoms needing confirmation, coworker disagreements needing tiebreak, or concrete study-experience questions
- Questions must be non-technical, with examples
- Never ask "should we do X?" — decide and propose

### Step 7: Implement (varies)
- SPEC changes: add to §1.1b or relevant §6 subsection
- Prompt changes: update `phase2_group.py` GROUP_SYSTEM_PROMPT AND the SPEC §5.3.2 code block (BOTH — check sync)
- Contract changes: update `contracts.py` with backward-compatible additions
- Test additions: red-team test atoms → actual pytest cases in `test_phase2_group.py` or new test files
- Run `python scripts/check_prompt_spec_sync.py` after EVERY prompt change

### Step 8: Validate (5 min)
- `python -m pytest engines/excerpting/tests/ -q` (excluding LLM integration) — zero regressions
- `python -m pyright <modified_files>` — zero errors
- `python scripts/check_prompt_spec_sync.py` — PASSED
- If prompt-affecting: `python scripts/atom_test.py --package taysir --chunk 5` — empirical validation

### Step 9: Record and Close (5 min)
- Update `FOUNDATIONS_HARDENING_LEDGER.md`:
  - Atom name and source
  - Coworker reports (3 of 3 required)
  - Doctrine adopted
  - Implementation changes (files + lines)
  - Tests added
  - Unresolved risks
  - Final disposition: FINALIZED / DEFERRED (with reason) / REJECTED (with reason)
- Commit if a natural batch point (every 3-5 atoms, or after any high-impact atom)

---

## Hard Rules — Violations Are Session Failures

1. **Never finalize an atom with fewer than 3 coworker reports.** Period.
2. **Never read only the extraction summary.** Always go back to the original collection files.
3. **Never batch multiple atoms together.** One at a time.
4. **Never skip the raw owner source layer.** Read `source_artifacts/*.txt` before anything else.
5. **Never modify the prompt without updating the SPEC code block.** Use `check_prompt_spec_sync.py`.
6. **Never skip empirical validation for prompt-affecting atoms.** Use `atom_test.py`.
7. **Never let a prior session's atom inventory cap your scope.** The 81 atoms are a floor, not a ceiling.
8. **Never treat `model_only` atoms as confirmed without owner verification.**
9. **Never say "done" before the ledger is updated.**
10. **Never end a session without updating `.kr/HANDOFF.md`.**

---

## What Session 1 Accomplished (preserve and build on)

- FP-1 through FP-18 in SPEC §1.1b
- EE-1 empirically validated (taysir 2/2, ibn_aqil 32/32)
- MV-1 (25-word minimum viability) from DR consensus
- NC-1 (context resolution hierarchy)
- 5 DR reports archived
- atom_test.py + check_prompt_spec_sync.py tools
- 907/907 deterministic tests pass
- Source surroundings vision saved to memory

**Session 1's work is NOT wasted.** It established the foundation. Session 2+ builds on it by processing the 34 genuinely new atoms, strengthening the 16 partially captured atoms, and converting the 9 red-team tests into actual pytest cases.

---

## Priority Order for Session 2

From the extraction, sorted by impact:

**Tier 1 — Nonnegotiables (become hard SPEC rules):**
All entries from `*_nonnegotiables.jsonl` across F3-F8

**Tier 2 — Red-team tests (become actual pytest cases):**
All entries from `*_red_team_tests.jsonl` across F3-F8

**Tier 3 — Prompt-affecting atoms (need empirical validation):**
Surface-function misread, title-retention asymmetry, forgiving-rule limit, clipped tarjih, question-cluster methodology

**Tier 4 — SPEC-only atoms (doctrinal, no code change):**
Remaining atoms that add principles without changing prompt or contracts

**Tier 5 — Deferred atoms (future capability):**
Atoms that describe features not yet in the pipeline (fetched proofs, data analysis, variant comparison)
