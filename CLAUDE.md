# خزانة ريان (KR) — Personal Intelligent Islamic Scholarly Library

**The library IS the user's knowledge. An error here is an error in his mind.**

Concise context: `STEERING.md`. Full spec: `VISION.md`. Quality target: `reference/ENTRY_EXAMPLE.md`.

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

## Pipeline

Source -> Normalization --- normalization boundary --- Passaging -> Atomization -> Excerpting -> Taxonomy -> Synthesis -> Scholar Interface

## Build and Test

```
python -m pytest engines/*/tests/ shared/*/tests/ -q
python -m pytest engines/<n>/tests/ -v --tb=short
python3 scripts/verify_metadata_flow.py
python3 scripts/check_compliance.py --all
python3 scripts/refinement_status.py
python3 scripts/extract_vision_sections.py --search keyword
```

## Repo Layout

engines/ — 7 engines: source, normalization, passaging, atomization, excerpting, taxonomy, synthesis
shared/ — consensus, validation, human_gate, feedback, user_model, scholar_authority
interface/scholar/ — user-facing intelligence layer
library/ — knowledge product (the user's knowledge)
schemas/ — data contracts; scripts/ — utilities; tests/integration/ — cross-engine tests
