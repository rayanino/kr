# خزانة ريان (KR) — Personal Intelligent Islamic Scholarly Library

**The library IS the user's knowledge. An error here is an error in his mind.**

Concise context: `STEERING.md`. Development process: `skills/shared/ENGINE_PROTOCOL.md`. Test architecture: `reference/TESTING_FRAMEWORK.md`. Quality target: `reference/ENTRY_EXAMPLE.md`. Full spec: `VISION.md` (47K tokens — never read whole, use `scripts/extract_vision_sections.py`).

## Critical Rules

1. Frozen sources are immutable. Bytes never change after freezing.
2. Primary text is never modified. No correction, no cleanup.
3. Every claim is traceable — to source excerpt or explicit analytical tag.
4. Errors fail loudly. Never silently drop data or default on uncertainty.
5. Human gates are not optional. No irreversible change without owner approval.
6. Metadata flows forward, never deleted (D-023). Pass through ALL upstream metadata.
7. Multi-model consensus for content decisions. Never single LLM call for attribution.
8. Arabic text is fragile. Read `.claude/skills/arabic-text/SKILL.md` before text processing.
9. Technology first. Check `.claude/skills/technology-survey/SKILL.md` before custom code.
10. ABD legacy has zero authority (D-019). SPECs define what to build.

## Before Starting Work

Read `NEXT.md` — it tells you what to do and what files to read.
Read this engine's `CLAUDE.md` in `engines/<n>/CLAUDE.md` — it tells you the current state.

## Pipeline

Source → Normalization ─── normalization boundary ─── Passaging → Atomization → Excerpting → Taxonomy → Synthesis

## Build and Test

```
python3 scripts/run_pipeline.py                           # Run full pipeline (after tracer bullet)
python -m pytest engines/<n>/tests/ -v --tb=short         # Per-engine tests
python -m pytest engines/*/tests/ shared/*/tests/ -q      # All tests
python3 scripts/verify_metadata_flow.py                   # D-023 metadata pass-through check
python3 scripts/check_spec_quality.py engines/<n>/SPEC.md # SPEC defect detection
python3 scripts/check_compliance.py --all                 # Code-to-SPEC compliance
python3 scripts/session_quality_gate.py                   # Pre-commit quality check
python3 scripts/extract_vision_sections.py 2 7            # Read VISION.md sections
```

## Repo Layout

```
engines/          — 7 engines: source, normalization, passaging, atomization, excerpting, taxonomy, synthesis
shared/           — consensus, validation, human_gate, feedback, user_model, scholar_authority
library/          — knowledge product (the user's knowledge): science trees, source registry
skills/           — Claude.ai uploadable skills (kr-*) + engine project templates + shared protocol
tests/fixtures/   — 7 real Arabic scholarly test sources
reference/        — domain docs, testing framework, decisions, resources
scripts/          — quality checks, pipeline runner, VISION.md extractor
.claude/          — Claude Code skills, agents, commands, hooks
```
