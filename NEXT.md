# NEXT — Excerpting Engine Evaluation

## Current State

The excerpting engine has produced its first full API run (2026-03-31):
- **133 excerpts** across 5 packages, **€2.93 total**, 33 minutes
- 5/5 packages succeeded, 4 validation drops (appropriate)
- Backend: GPT-5.4 primary, Claude Opus verify, Gemini escalation via OpenRouter

## Immediate Task: Multi-Model Evaluation

**Read `integration_tests/smoke_api/EVALUATION_PROTOCOL.md` for full instructions.**

The evaluation team:
- **Owner** reviews via `python tools/review.py integration_tests/smoke_api/`
- **Claude Code** evaluates SPEC compliance + metadata integrity
- **Codex / Gemini** provide independent structural review
- **Claude Chat / ChatGPT Pro** provide deep scholarly content review

### What to evaluate (5 dimensions):
1. Excerpt quality (teaching unit boundaries, function labels)
2. Structural integrity (D-023 metadata, word offsets, segment indices)
3. Consensus quality (enrichment vs verify agreement)
4. Coverage (are we extracting enough? missing anything?)
5. Arabic text fidelity (diacritics, honorifics, RTL)

### Quality gates before next run:
- Owner has reviewed >= 1 full package
- >= 2 LLM reviewers on the same package
- Disagreements investigated
- Pipeline bugs fixed
- Cost projection documented

## Context

- Pre-production hardening committed: `509cfd5c` (958 tests, 6 fixes)
- Review viewer: `tools/review.py` + `tools/excerpt_viewer.html`
- API costs are negligible: ~€3 per full 5-package run
- Budget: €120 allocated for testing (~40 full runs)
- Full engine test suite: 958 tests, 0 failures

## Files to Read

1. `integration_tests/smoke_api/EVALUATION_PROTOCOL.md` — evaluation instructions
2. `integration_tests/smoke_api/SUMMARY.json` — run results
3. `engines/excerpting/CLAUDE.md` — engine context
4. `docs/superpowers/specs/2026-03-31-excerpt-viewer-design.md` — viewer design
