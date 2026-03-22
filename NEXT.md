# NEXT — Excerpting Engine: Validate Then Design

## Start Here

Read `reference/archive/sessions/architecture_decision_handoff.md` FIRST. It contains everything the previous session decided, the evidence behind it, and — critically — the 4 empirical gaps that remain open.

## The Decision You Must Make

The architecture (5 engines, 3 remaining, passaging absorbed into excerpting) is committed at `experiments/architecture_test/ARCHITECTURE_DECISION.md`. The evidence for the pipeline shape is strong (2M divisions, 96.8% need no splitting).

But the excerpting engine's INTERNAL design has 4 unvalidated assumptions:
1. Zero non-prose texts tested (verse, QA, commentary, dictionary)
2. Max tested division was 1040 words (3.2% of real divisions are 2000-5000w)
3. Same model evaluated its own output
4. Books with empty division trees not tested

**Option A:** Run an expanded experiment covering gaps 1-2 first, THEN write the SPEC.
**Option B:** Write the SPEC with explicit validation flags, test during engine evaluation.

Read the handoff, read the evidence, make the call. Use `thinking-frameworks` at DEEP tier — this affects how we spend the next weeks.

## Skills to Use

- `thinking-frameworks` (decide Option A vs B)
- `kr-research` (if Option A: design the expanded experiment)
- `kr-integrity` (if Option B: audit the SPEC for gaps)
- `critical-review` (always)

## Read First

1. `reference/archive/sessions/architecture_decision_handoff.md` — COMPLETE session summary
2. `experiments/architecture_test/ARCHITECTURE_DECISION.md` — the committed architecture
3. `experiments/architecture_test/EVALUATION_WORKBOOK.md` — what was actually tested
4. `experiments/architecture_test/SHAMELA_DIVISION_ANALYSIS.md` — full-scale division data
5. `KNOWLEDGE_INTEGRITY.md` — corruption threats
6. `reference/protocols/QUALITY_AXIOM.md` — quality standards
