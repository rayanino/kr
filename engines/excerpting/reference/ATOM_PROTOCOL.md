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

## Coworker Roles — Specific, Non-Overlapping

| Coworker | Primary Role | Unique Strength | Prompt Focus |
|----------|-------------|-----------------|--------------|
| **Codex CLI** | Contract Guardian | Reads full codebase structurally. Traces contracts, tests, regressions. | "What breaks? What contracts change? What tests fail? Implementation cost?" |
| **Gemini CLI** | Scholarly Auditor + System Architect | Arabic language depth, Islamic methodology, cross-engine impact mapping. | "Is this correct across all sciences? Give Arabic examples. Map cross-engine blast radius." |
| **DR (ChatGPT/Claude/Gemini)** | Adversarial Reasoner | Extended thinking, web research, failure scenario construction. | "What did the CLI coworkers miss? What catastrophic scenario looks correct but is wrong?" |
| **CC (Claude Code)** | Orchestrator | Owns context, makes decisions, writes code, synthesizes findings. | Does NOT self-review. Always dispatches at least 2 coworkers. |

---

## Pre-Loop: Step -1 — Queue Audit (Gemini critique finding #6)

Before starting the atom loop, deploy an agent to:
1. Read ALL `source_artifacts/*.txt` files from F1-F8
2. Compare against the 81-atom extraction
3. List any owner directives, pain points, or rules that the extraction MISSED
4. Append discovered atoms to the queue

This prevents the extraction agent's blind spots from becoming the session's blind spots.

---

## Pre-Loop: Thematic Grouping (Gemini critique finding #7 — CRITICAL)

**Do NOT process 81 atoms as 81 isolated edits.** This causes prompt thrashing — the Phase 2b prompt becomes a patched-together list of contradictory instructions by atom 30.

Instead, group atoms into THEMATIC BATCHES by the subsystem they affect:
- **Batch: Self-containment** — all atoms about C-SC-1 through C-SC-5, linking words, taqdir, backward hunting
- **Batch: Boundary/grouping** — all atoms about split/merge, EE-1, sibling topics, function mixing
- **Batch: Tarjih/khilaf** — all atoms about disagreement handling, tarjih separation, dialectical coupling
- **Batch: Proof/evidence** — all atoms about fetched proofs, variant analysis, isnad handling
- **Batch: Granularity** — all atoms about overgranulation, forgiving rule, mention vs topic, minimum viability
- **Batch: Safety/integrity** — all atoms about trust poisoning, deceptive cleanliness, omission honesty

Within each batch, process atoms together so the prompt/SPEC changes are COHERENT. The batch is the unit of coworker dispatch — one dispatch per batch, not per atom.

---

## Conflict Resolution Rule (Gemini critique finding #3 — CRITICAL)

**If a structured collection file (YAML/JSONL/MD) contradicts or omits nuance from the `source_artifacts/*.txt` raw owner text, the raw .txt ABSOLUTELY WINS.**

The structured files were produced by ChatGPT interpreting the owner's words. ChatGPT may have:
- Softened strong owner statements
- Added qualifications the owner didn't express
- Missed sarcasm, emphasis, or conditional reasoning
- Expanded into areas the owner didn't authorize (`model_only` authority)

When a conflict is detected: document it in the ledger as "ChatGPT drift from owner intent at [file:line]" and proceed using ONLY the owner's raw text.

---

## Constraint Feasibility Check (Gemini critique finding #4 — HIGH)

Even nonnegotiables MUST be checked for:
1. **Self-contradiction:** Do two nonnegotiables from different collections conflict?
2. **Technical impossibility:** Is this nonnegotiable implementable within the current architecture?
3. **Regression risk:** Does implementing this nonnegotiable break a previously finalized atom?

If a contradiction or impossibility is found: do NOT implement. Escalate to owner Q&A with the specific conflict. The owner resolves the deadlock, not the engineer.

---

## Per-Atom Loop — THE EXACT STEPS

### Step 0: Select the Next Thematic Batch
- Group related atoms from the extraction into thematic batches (see above)
- Within each batch, prioritize: nonnegotiable > red-team test > prompt-affecting > SPEC-only > deferred
- The batch is the unit of work. Individual atoms within a batch are processed sequentially but their SPEC/prompt changes are designed together for coherence.

### Step 1: Read the Original Source (10 min per atom)
- Go to the COLLECTION DIRECTORY (e.g., `chatgpt_f3_collection/`)
- Read the RAW OWNER SOURCE first (`source_artifacts/*.txt`) — this is GROUND TRUTH
- Read the cleaned answer (`01_questionnaire_answer.md`)
- Read the SPECIFIC FILE the atom came from
- Read the traceability entry (`*_traceability.jsonl`)
- **Conflict check:** Does the structured file match the raw source? If not, raw wins (see Conflict Resolution Rule above)
- Note authority level: `owner_explicit` > `owner_consistent_inference` > `model_only`

### Step 1b: Blast Radius Check (Gemini critique finding #1)
- Read the FOUNDATIONS_HARDENING_LEDGER.md
- For each previously finalized atom: would this new atom CHANGE, WEAKEN, or CONTRADICT it?
- If yes: the atom cannot be implemented in isolation — it must reopen the conflicting atom

### Step 2: Check Current State (5 min)
- Is it already captured in SPEC §1.1b (FP-1 through FP-18)?
- Is it already in the Phase 2b prompt (`phase2_group.py`)?
- Is it already tested?
- Run `python scripts/check_prompt_spec_sync.py`
- If fully captured AND correctly captured: verify, mark DONE, move to next atom
- If partially captured: identify the specific gap

### Step 3: Research (20 min)
Prepare THREE research prompts — each coworker gets their SPECIALIZED prompt plus the adversarial prompt (per Gemini critique finding #2):

**Prompt A — Repo/Implementation Challenge:**
"Read [specific files]. Does the current implementation correctly handle [atom]? What would break if [atom] is wrong? What contracts/tests/prompts need to change?"

**Prompt B — Scholarly/Domain Challenge:**
"In Islamic scholarly texts, is [atom] correct? Give concrete Arabic examples where [atom] holds and where it fails. What Islamic science is most at risk if [atom] is wrong?"

**Prompt C — Adversarial/Failure Mode Challenge:**
"What is the WORST thing that happens if [atom] is implemented incorrectly? Give a concrete scenario where the engine produces a confidently wrong excerpt because of [atom]. What silent corruption path does [atom] open or close?"

### Step 4: Dispatch Coworkers — SPECIALIZED ROLES + ADVERSARIAL CROSS-CHECK (mandatory)

**Codex CLI** — Primary: Prompt A (repo/implementation) + Prompt C (adversarial):
```
codex exec "PRIMARY (repo challenge): [what breaks, what contracts change, what tests fail]
ADVERSARIAL: [worst failure scenario from implementation perspective]
OUTPUT: file:line references, contract impact, regression risk rated HIGH/MEDIUM/LOW."
```

**Gemini CLI** — Primary: Prompt B (scholarly/domain) + Prompt C (adversarial):
```
gemini -p "PRIMARY (scholarly challenge): [is this correct across all Islamic sciences, give Arabic examples]
SYSTEM IMPACT: [map blast radius across engines/contracts/taxonomy]
ADVERSARIAL: [worst failure scenario from scholarly perspective]
OUTPUT: per-science assessment, Arabic examples, cross-engine impact map."
```

**DR (relay to owner)** — Primary: Prompt C (adversarial) + synthesis of Codex/Gemini gaps:
"Here are the Codex and Gemini findings for [atom/batch]. What did they MISS? What catastrophic scenario looks correct but is wrong? Research external sources if needed."

**WAIT for ALL THREE to return before proceeding.** If one coworker is unavailable: log the gap, proceed with 2/3, but mark the atom as PRELIMINARY until the third coworker reviews.

**Dispatch is per THEMATIC BATCH, not per individual atom.** One dispatch covers all atoms in the batch.

### Step 5: Synthesize + Decide AUTONOMOUSLY (15 min)
- Create a 3-column comparison: Codex | Gemini | DR
- Where do they AGREE? → high confidence, proceed
- Where do they DISAGREE? → **CC decides based on which argument is stronger.** Write the reasoning in the ledger. Do NOT escalate to owner for technical tiebreaks.
- Where did they find things the atom MISSED? → expand the atom
- **Decision mechanism when ambiguous:**
  1. If 2/3 coworkers agree → go with the majority
  2. If all 3 disagree → CC decides based on FP-13 precedence stack (attribution > dialogue > grammar > self-containment > granularity)
  3. If the decision affects the owner's STUDY EXPERIENCE (not technical architecture) → ask the owner a concrete, non-technical question
  4. If the decision is purely technical/architectural → CC decides, period
- **The owner is NOT a tiebreaker for technical decisions.** The owner provides study-experience signal. CC + coworkers own every technical/scholarly/architectural decision.
- Record the synthesis AND the decision reasoning in the ledger

### Step 5b: Proactive Discovery (after each batch)
After processing all atoms in a batch, ask: "What did the owner NOT think of that would improve this subsystem?" Dispatch Codex + Gemini with an open-ended research prompt. The engine should be BETTER than what the owner asked for, not just compliant with it. Remember: **the library is the MIND OF A SCHOLAR put on a screen** — a scholar's mind has insights beyond any individual student's questions.

### Step 5c: FP Revision Check
If reading the full collection data reveals that an existing FP (FP-1 through FP-18) is WRONG or needs refinement:
- REVISE IT. FPs are living doctrine, not frozen law.
- Document the revision in the ledger: what changed, why, which evidence forced the revision.
- Update both the SPEC §1.1b AND the prompt (if the FP is prompt-enforced).

### Step 6: Ask Owner (LAST RESORT — study-experience questions ONLY)
- The owner is asked ONLY when:
  - The question is about personal study habits that only the owner can answer (e.g., "when you study fiqh, do you read proofs before or after the ruling?")
  - A `model_only` atom needs owner confirmation of intent
  - The owner's raw text is genuinely ambiguous and no amount of coworker research can resolve it
- The owner is NEVER asked:
  - "Should we implement this?" — CC decides
  - "Which approach do you prefer?" — CC + coworkers decide
  - "Is this good enough?" — coworker consensus decides
  - "What should we do next?" — the protocol defines the sequence
- Questions must be concrete with examples, never abstract
- The owner's answer is SIGNAL, not a directive (per OWNER_FEEDBACK_GUARDRAIL.md)

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

## Context Compaction Survival Guide

When the session fills up and compaction happens, IMMEDIATELY re-read:
1. The active batch's atoms (from the extraction doc)
2. SPEC §1.1b (all FPs)
3. The current GROUP_SYSTEM_PROMPT (from phase2_group.py lines 43-170)
4. Any unprocessed coworker findings for the current batch
5. The ledger's most recent entries

Everything else can be re-derived from files. These 5 things cannot.

## The North Star

**THE LIBRARY IS THE MIND OF A SCHOLAR PUT ON A SCREEN.**

A scholar's mind doesn't:
- Leave knowledge disconnected
- Misattribute positions to the wrong scholar
- Lose the reasoning behind a ruling
- Require "hunting" for context
- Present fragments without connections

Every excerpt must be as clear as if a scholar is explaining it to you. Every boundary must reflect how a scholar mentally organizes knowledge. If the library requires the reader to "figure things out," it has failed.

The owner's only remaining job after the library is complete: **memorize.** Everything else — gathering, analyzing, organizing, cross-referencing, attributing — is the library's job.

## NOTHING CAN BE LOST

The F1-F8 collections contain ideas spanning MULTIPLE scopes: excerpting rules, LLM directives, architectural visions, study workflows, tool suggestions, failure fears, quality standards, and more. Some belong in the SPEC. Some belong in the prompt. Some belong in contracts. Some belong in future-capability docs. Some belong in the owner-model.

**Every single idea must receive dedicated attention.** Even if an idea doesn't fit the excerpting engine directly, it must be DOCUMENTED in the appropriate location — never silently dropped. Use `engines/excerpting/reference/DEFERRED_IDEAS.md` (create if needed) for ideas that belong to future capabilities.

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
