# NEXT SESSION

## Session Type
SPEC_REFINEMENT

## Immediate Task

Execute refinement cycle 1 on the **source engine SPEC** (`engines/source/SPEC.md`).

Follow `SPEC_REFINEMENT.md` Steps 0-10. Start with Step 0 (Creative Exploration from `CREATIVE_MANDATE.md`). Use `CONTEXT_BUDGET.md` to plan reads.

**NEW in this cycle:** Three new refinement steps were added:
- Step 1.5: Run `python3 scripts/check_spec_quality.py engines/source/SPEC.md --verbose` for automated defect baseline
- Step 2.5: Corruption Risk Assessment — for each output field, what if it's wrong?
- Step 3.5: Machine-Readability Test — can you write pseudocode for each §4.A rule?

Cross-reference the SPEC prose against `engines/source/contracts.py` (Pydantic models) — mismatches are defects.

## Definition of Done

1. At least 3 new §4.B capabilities invented, each with named technology and output example
2. Minimum 8 web searches during creative exploration
3. Defect ledger with exact quotes and fixes
4. All §4.A subsections have concrete I/O examples with real Arabic text
5. All 7 knowledge integrity threats addressed
6. All 7 silent failure patterns checked
7. contracts.py validated against SPEC §3
8. Boundary with normalization verified
9. Two self-review rounds; Three Challenges each found at least one issue
10. Refined SPEC committed
11. **NEW:** `check_spec_quality.py` high-severity defects reduced by ≥50% from baseline
12. **NEW:** Every output field has an identified corruption risk and protection mechanism
13. **NEW:** Every §4.A rule passes mental pseudocode test (machine-readability)

## Context

Run `python3 scripts/orient.py --brief` for current project status.

The preparatory phase has 8 work streams (see `PREPARATORY_ROADMAP.md`). This session does Stream 1 (source SPEC refinement).

Session 9 completed Stream 2 (source + normalization contracts.py) and Stream 3 (technology survey).

The autonomous system hardening round added:
- `scripts/check_spec_quality.py` — automated SPEC defect detector (526 defects across 14 SPECs; source SPEC has 35 high-severity)
- Three new steps to SPEC_REFINEMENT.md (1.5, 2.5, 3.5)
- Anti-sycophancy gate in Step 7
- Quality verification gate in Step 10
- QARI-OCR discovery — new open-source SOTA for Arabic OCR with diacritics (evaluate for source engine)

## Files to Read — IN THIS ORDER

1. `CONTEXT_BUDGET.md` (~1,200 tokens)
2. `CREATIVE_MANDATE.md` (~1,200 tokens)
3. `SPEC_REFINEMENT.md` (~2,200 tokens — updated with 3 new steps)
4. `SILENT_FAILURES.md` (~1,500 tokens)
5. `KNOWLEDGE_INTEGRITY.md` (~1,600 tokens)
6. `engines/source/contracts.py` (~3,500 tokens) — updated Session 9
7. `engines/source/SPEC.md` (~5,500 tokens)
8. `engines/normalization/contracts.py` (~2,500 tokens) — new in Session 9
9. `engines/normalization/SPEC.md` §2 only (~1,000 tokens)
10. `reference/ENTRY_EXAMPLE.md` (~1,600 tokens)
11. `reference/USER_SCENARIOS.md` (~2,700 tokens)

**Total: ~24,500 tokens. Budget remaining: ~130,000 tokens.**

## Files to NOT Read

VISION.md, DOMAIN.md, kr_decisions.md, STATUS.md, ORCHESTRATOR.md, other engine SPECs

## What Last Session Did

Autonomous system hardening round:
- Created `scripts/check_spec_quality.py` — automated SPEC quality checker detecting vague language, missing examples, hand-waving tech, unvalidated writes, missing thresholds (526 defects found across 14 SPECs)
- Added 3 new steps to SPEC_REFINEMENT.md: automated quality scan (1.5), corruption risk assessment (2.5), machine-readability test (3.5)
- Added anti-sycophancy gate to Step 7 and quality verification gate to Step 10
- Fixed PROJECT_INSTRUCTIONS.md: GitHub token from knowledge file, "continue the project" trigger, SESSION_LOG.md in commit checklist
- Fixed STATUS.md: corrected misleading "preparatory phase complete" language
- Rewrote HOW_TO_START.md for clean setup
- Discovered QARI-OCR — new open-source Arabic OCR SOTA (CER 0.061 on diacritized text)
- Confirmed Swan-Large as Arabic embedding SOTA (NAACL 2025)
- Confirmed OpenITI v0.1.6 active (Nov 2025)

## Decisions Made

None — all changes are operational improvements to the autonomous system, not architectural decisions.

## Pending Owner Questions

- **API keys:** Fill in .env from .env.template when ready (for future LLM-dependent work)
