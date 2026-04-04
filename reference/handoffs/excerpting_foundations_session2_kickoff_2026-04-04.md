# Excerpting Foundations Hardening — Session 2 Kickoff

**You are taking over the KR excerpting foundations hardening lane, session 2.**

Session 1 set up the infrastructure. Your job is the actual work: processing every single atom from the owner's weekend feedback into hardened doctrine, implementation, tests, and safeguards. This is the highest-stakes work in the entire project. The owner is available 24/7 and has Codex CLI, Gemini CLI, ChatGPT DR, Claude DR, and Gemini DR all ready to receive dispatch prompts.

---

## STOP — Read these files in this exact order before doing ANYTHING

1. `engines/excerpting/reference/ATOM_PROTOCOL.md` — the governing law. Every rule is mandatory.
2. `engines/excerpting/reference/QUEUE_AUDIT_RAW_VS_EXTRACTION.md` — 124 gaps between the owner's raw text and the ChatGPT-structured extraction. These gaps are atoms that were MISSED or SOFTENED. They include the owner's foundational vision, emotional stakes, and architectural directives.
3. `engines/excerpting/reference/F1_F8_COMPLETE_ATOM_EXTRACTION.md` — 81 atoms extracted from F3-F8 structured files. This is a STARTING POINT, not a cap. The queue audit shows 124 additional gaps.
4. `engines/excerpting/reference/CRITICAL_ATOMS_NONNEGOTIABLES_AND_REDTEAM.md` — 63 nonnegotiables + 62 red-team tests. Nonnegotiables become hard SPEC rules. Red-team tests become actual pytest cases.
5. `engines/excerpting/reference/THEMATIC_BATCHES.md` — 7 pre-grouped batches ordered by impact. Process in this order.
6. `engines/excerpting/reference/FOUNDATIONS_HARDENING_LEDGER.md` — what session 1 already did (18 FPs, EE-1, MV-1, NC-1).
7. `engines/excerpting/SPEC.md` §1.1b — the 18 foundational principles already in the SPEC. Some are preliminary and need revision based on the full data.
8. `.kr/HANDOFF.md` — session context.

---

## What session 1 accomplished (DON'T redo)

- 18 foundational principles (FP-1 through FP-18) in SPEC §1.1b
- EE-1 (explained+explanation unity) empirically validated on taysir and ibn_aqil
- MV-1 (25-word minimum viability) from DR consensus
- NC-1 (context resolution hierarchy: structural unity → source surroundings → generated hint)
- 5 DR reports archived with findings
- Tools: atom_test.py, check_prompt_spec_sync.py, promptfoo, pytest-xdist, hypothesis

## What session 1 got WRONG (DON'T repeat)

1. **Only read 15 of 139 files.** The F1-F8 collections have 12-17 files each. Session 1 read only the raw source + cleaned answer, missing decision ladders, nonnegotiables, red-team tests, linking dependencies, and more. READ EVERY FILE.
2. **Skipped DR coworkers for most atoms.** Only atoms 1 and the FP set got DR review. Session 1 had CLI coworkers but underused DR models (ChatGPT, Claude, Gemini in deep research mode).
3. **Batched atoms 3-12 into one shallow SPEC edit.** One principle per paragraph is not hardening — it's documenting. Real hardening means coworker-challenged, empirically-validated, counterexample-searched doctrine.
4. **Followed Codex's predefined atom inventory.** The atoms should come from YOUR independent reading of the raw feedback, not from a prior session's frame.
5. **FP-1 through FP-18 were written before reading the full data.** They may need revision or expansion based on the queue audit findings.

---

## The 139 golden files

The owner spent an entire weekend working with ChatGPT to produce these. They are in `engines/excerpting/chatgpt_f{1-8}_collection/`. Each collection contains:

- `source_artifacts/*.txt` — RAW OWNER TEXT. Highest authority. Read FIRST.
- `*_nonnegotiables.jsonl` — ABSOLUTE CONSTRAINTS. Become hard SPEC rules.
- `*_red_team_tests.jsonl` — ADVERSARIAL TEST CASES. Must become actual pytest cases.
- `*_decision_ladder.jsonl` — Step-by-step boundary reasoning.
- `*_linking_dependencies.jsonl` — Specific Arabic words with referents and failure modes.
- `*_terms.yaml` — Controlled vocabulary with dangerous competing meanings.
- And 5-8 more domain-specific analysis files per collection.

**If you skip any file, you are losing the owner's work.** The owner said: "if any potential is lost because of this, I will burn down your servers."

---

## The coworker mandate

**Every thematic batch gets ALL THREE coworkers before finalization:**

| Coworker | Role | How to dispatch |
|----------|------|-----------------|
| **Codex CLI** | Contract Guardian — what breaks, what regresses | `codex exec "..."` (direct) |
| **Gemini CLI** | Scholarly Auditor — Arabic correctness, cross-science validity | `gemini -p "..."` (direct) |
| **DR (relay)** | Adversarial Reasoner — what did CLI coworkers miss, failure scenarios | Write prompt → owner relays to ChatGPT/Claude/Gemini DR |

Each coworker gets their SPECIALIZED primary prompt plus the adversarial cross-check. Codex gets the repo challenge. Gemini gets the scholarly challenge. DR gets the "what did they miss" challenge.

**Do NOT implement without waiting for all three to return.** Partial coworker coverage produces partial confidence.

---

## The tools

| Tool | When to use | Command |
|------|------------|---------|
| `atom_test.py` | After any prompt change | `python scripts/atom_test.py --package taysir --chunk 5` |
| `check_prompt_spec_sync.py` | After any prompt OR SPEC change | `python scripts/check_prompt_spec_sync.py` |
| `promptfoo` | For batch-level prompt regression testing | `promptfoo eval` (configure per batch) |
| `pytest -n 4` | For fast test runs | `pytest -n 4 engines/excerpting/tests/` |

---

## The conflict resolution rule

**If a structured collection file (YAML/JSONL) contradicts the raw owner text (.txt), the raw text WINS.** ChatGPT may have softened, dropped, or distorted the owner's intent. The queue audit found 6 instances of ALL-CAPS urgency being normalized to neutral prose.

---

## Processing sequence

1. Run the session start checklist from ATOM_PROTOCOL.md (7 checks)
2. Read the queue audit (124 gaps) and merge new atoms into thematic batches
3. Start with Batch 1 (Safety & Integrity, 13 atoms) — this is foundational
4. For each batch: read original files → research → dispatch ALL THREE coworkers → synthesize → implement → validate → record
5. Commit after each batch with descriptive message
6. Update FOUNDATIONS_HARDENING_LEDGER.md after each batch
7. If context fills up: use /smart-compact, re-read SPEC §1.1b and the active batch, continue

---

## What the owner expects

The owner is available 24/7 to:
- Relay DR prompts
- Answer non-technical study-experience questions
- Enable/top up API keys

The owner is NOT available to:
- Drive technical direction (that's your job)
- Identify the next atom (that's your job)
- Catch gaps in the plan (that's what coworkers are for)

**Take full authority. Make decisions. Execute. Report results. Never ask "should we do X or Y?" — decide and do.**

The owner said: "you are the strict 250 IQ boss with his business on the line." Act like it.

---

## The ultimate standard

An atom is NOT finalized unless:
- The raw owner source was read
- The structured collection files were read
- Counterexamples were searched
- Codex CLI reviewed and reported
- Gemini CLI reviewed and reported
- At least one DR reviewed and reported
- Implementation was made (SPEC/prompt/contract/test)
- Tests pass (pytest + pyright + sync check)
- Empirical validation passed (if prompt-affecting)
- The ledger was updated with full disposition and residual risks
- Cross-atom regression was checked

There is no "soft finalized." There is no "good enough." There is no "we'll come back later."

**The engine either handles this atom correctly in every excerpt, or it doesn't. Prove which one.**
