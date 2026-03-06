# Implementation Gate — بوابة التنفيذ

This document defines the EXACT conditions that must be met before Claude Code begins building. No implementation session should start until ALL gate criteria pass for the target engine.

---

## Per-Engine Gate (must pass for each engine before implementation)

### G-1: SPEC Quality
- [ ] `python3 scripts/check_spec_quality.py engines/<n>/SPEC.md` — ≤10 high-severity defects
- [ ] `python3 scripts/creative_verification.py engines/<n>/SPEC.md` — score ≥80/100
- [ ] Every §4.A rule has a concrete I/O example with real Arabic text
- [ ] Every §4.A rule passes mental pseudocode test (machine-readability)
- [ ] Every output field (§3) has an identified corruption risk and protection mechanism (§5)

### G-2: Machine-Readable Contracts
- [ ] `engines/<n>/contracts.py` exists with Pydantic models for all §2/§3 fields
- [ ] Every field in contracts.py matches SPEC prose exactly
- [ ] Downstream engine's contracts.py is compatible (boundary verified)

### G-3: Test Infrastructure
- [ ] Test fixtures exist in `tests/fixtures/` for this engine's input formats
- [ ] At least one gold baseline exists (hand-verified expected output)
- [ ] `engines/<n>/CLAUDE.md` accurately describes current implementation state

### G-4: Dependencies
- [ ] All external tools listed in RESOURCES.md with install commands
- [ ] `requirements.txt` includes all Python dependencies
- [ ] API keys documented in `.env.template` (keys themselves provided by owner when needed)

### G-5: Task Decomposition
- [ ] MILESTONES.md has atomic task list for this engine's first milestone
- [ ] Each task is one Claude Code session's work
- [ ] Each task has testable acceptance criteria

---

## Global Gate (must pass once before ANY implementation)

### G-6: Cross-SPEC Coherence
- [ ] `python3 scripts/verify_metadata_flow.py` — all boundaries clear
- [ ] Terminology consistent across all SPECs (verified in STATUS.md)
- [ ] kr_decisions.md consistent with all SPECs (no contradictions)

### G-7: Claude Code Environment
- [ ] `.claude/settings.json` — permissions and hooks configured
- [ ] `.claude/agents/` — code-reviewer and integrity-checker ready
- [ ] `.claude/skills/` — arabic-text and technology-survey ready
- [ ] `.claude/commands/` — essential commands working
- [ ] `CLAUDE.md` (root) — accurate, <60 lines, implementation-focused
- [ ] Engine CLAUDE.md files — accurate implementation state

### G-8: External Tools Verified
- [ ] Primary OCR tool tested with Arabic scholarly text
- [ ] Embedding model available and tested with Arabic text
- [ ] LLM consensus setup tested (at least 2 providers accessible)
- [ ] All tools in RESOURCES.md verified installable

### G-9: Owner Readiness
- [ ] API keys provided (Anthropic, OpenAI/OpenRouter, Mistral)
- [ ] At least one real scholarly source available for testing
- [ ] Owner understands human gate process (will review when asked)

---

## How to Check

Run this for a quick overview:
```bash
python3 scripts/orient.py --brief
python3 scripts/refinement_status.py
python3 scripts/check_spec_quality.py --all
```

For a specific engine:
```bash
python3 scripts/check_spec_quality.py engines/<n>/SPEC.md
python3 scripts/creative_verification.py engines/<n>/SPEC.md
python3 scripts/verify_metadata_flow.py --boundary <upstream> <downstream>
```

### G-10: Pipeline Test Harness
- [ ] `kr-pipeline` CLI tool specified (how engines chain, report format, regression support)
- [ ] `STRESS_TESTING.md` committed with communication protocol (Claude Code ↔ Claude Chat)
- [ ] `test_corpus/` directory structure defined
- [ ] Human-readable report format specified (Arabic content preserved, English labels)

---

## Implementation Order

Once gates pass, implementation follows dependency order:

```
Phase 1 (above normalization boundary):
  1. Source engine (M1.1 → M1.2 → M1.3)
  2. Normalization engine (M1.4 → M1.5)
  → Integration test: source output feeds normalization

Phase 2 (below normalization boundary):
  3. Passaging engine
  4. Atomization engine
  5. Excerpting engine
  → Integration test: full pipeline source → excerpts

Phase 3 (organization and synthesis):
  6. Taxonomy engine
  7. Synthesis engine
  → Integration test: full pipeline source → entries

Phase 4 (shared and interface):
  8. Shared components (consensus, validation, human_gate, feedback, user_model, scholar_authority)
  9. Scholar interface
  → End-to-end test: source → user-facing query
```
