> Purpose: Define the single current frontier and the exact deliverable expected from the next serious work session.
> Authority: The only authoritative next-session task file.
> Update when: The active frontier changes, the deliverable changes, or the success criteria change.
> Must not contain: Session diary, multiple parallel frontiers, broad backlog, durable project law.

## Role Relationship
Owner = CLIENT (non-technical, minimum Islamic knowledge). All agents = ENGINEERING TEAM.
The owner provides reactions and preferences. Agents drive direction, identify gaps, propose next steps.
Never ask the owner engineering questions. Never wait for the owner to identify what's needed next.

# KR Active Frontier

Status: active

## Current frontier — Excerpting Engine Deep Q&A + Exhaustive Hardening

A 4-phase operation to finalize the excerpting engine's prompt quality and output calibration using owner feedback and 5-coworker evaluation.

### Phase 0: Owner Q&A
Design and conduct a structured questionnaire with the owner using real campaign excerpts (2,303 at `integration_tests/campaign_20260331/`). All 5 coworkers collaboratively design the questionnaire. Questions are end-user only — what the owner wants to experience when using his library.

### Phase 1: Smoke Run + 6-Team Analysis
Run `scripts/run_full_integration.py --backend api --output-dir integration_tests/smoke_api_v2/` (~130 excerpts, ~EUR 3, ~30 min). Then 6 parallel analysis teams evaluate output:
- A: Boundary Quality (CC + Codex)
- B: Classification (Gemini + ChatGPT DR)
- C: Arabic Fidelity (Claude DR + Gemini)
- D: Consensus & Metadata (Codex + CC)
- E: Coverage & Gaps (ChatGPT DR + Claude DR)
- F: Owner Review (Owner + review tool)

### Phase 2: Deep Hardening
Fix everything from Phase 1 + Q&A. Re-run smoke (~EUR 3). Re-evaluate. Iterate until convergence.

### Phase 3: Full 5-Book Run
Definitive run with fully hardened prompts (~$15-20). Compare against campaign baseline (2,303 excerpts, old prompts).

## Success criteria
1. Owner has reviewed excerpts from at least 2 packages and accepted them
2. All 5 coworkers independently confirm output quality
3. Zero known unaddressed error patterns
4. All automated checks pass (pyright, pytest, Arabic safety, boundary validation)

## Budget
- OpenRouter: ~EUR 50 remaining
- Smoke run: ~EUR 3 per run
- Full 5-book: ~$15-20

## Relevant decisions
- OPS-DEC-001 through OPS-DEC-006

## Previous frontier (completed 2026-03-29)
Build the excerpting evaluation layer v1 (analyzer, campaign aggregator, review-packet exporter) and patch all 6 observability gaps in the runner.
