# Source Engine — محرك المصادر

**Phase:** Specification Discovery (pre-build)
**Branch:** `clean-start`

## Current State

The source engine is in spec discovery. No production code exists yet. The previous implementation was archived to `reference/archive/v1/source_engine/` (reference-only, non-authoritative).

**Spec infrastructure:** Being created by Codex (schema.json, validate_spec.py, generate_views.py, initial atoms).

## Authoritative Files

| File | Role |
|------|------|
| `spec/INDEX.yaml` | Machine-readable registry of all spec atoms |
| `spec/schema.json` | JSON Schema validating all atom YAML files |
| `spec/requirements/*.yaml` | Behavioral requirements (structured YAML, not prose) |
| `spec/invariants/*.yaml` | Invariant rules |
| `spec/decisions/*.yaml` | Architectural decisions with options and rationale |
| `spec/constraints/*.yaml` | Hard limits from domain/upstream/downstream |
| `spec/questions/*.yaml` | Open questions awaiting resolution |
| `spec/owner-feedback/*.yaml` | Structured owner responses (one topic per atom) |

**There is no SPEC.md.** The specification is the collection of YAML atoms in `spec/`. Agents consume individual atoms, never a monolithic document.

## Spec Team

Six agents handle all spec work. No single agent produces AND reviews atoms.

| Agent | File | Role |
|-------|------|------|
| Spec Coordinator | `.claude/agents/spec-coordinator.md` | Orchestrates team, maintains INDEX, resolves conflicts |
| Archive Miner | `.claude/agents/spec-archive-miner.md` | Extracts draft atoms from v1 archive |
| Atom Writer | `.claude/agents/spec-atom-writer.md` | Produces final-form schema-valid YAML atoms |
| Domain Validator | `.claude/agents/spec-domain-validator.md` | Arabic/scholarly accuracy review (dispatch to Gemini CLI) |
| Contract Architect | `.claude/agents/spec-contract-architect.md` | Structural consistency, testability (dispatch to Codex CLI) |
| Team Adversary | `.claude/agents/spec-team-adversary.md` | Finds contradictions, gaps, edge cases |

## Spec Format: Specs-as-Data

All atoms are **pure structured YAML** — NOT markdown with frontmatter. Behavioral rules, acceptance criteria, and error conditions are structured fields that agents PARSE, not prose that agents INTERPRET.

Key principle: if a build agent needs to interpret natural language to know what to do, the atom is not ready.

## Archive Usage Rules

The archive at `reference/archive/v1/source_engine/` is reference-only:
- **Mine it** for corpus facts, validated heuristics, failure modes, and lessons learned
- **Never treat it** as authoritative for the new engine
- **Tag provenance** on every atom derived from archive material (archive_tier_a or archive_tier_b)
- Archive Miner agent handles all archive extraction

## Agent Consumption Protocol

Three guarantees that prevent spec drift during build phase:

1. **Scoped injection:** Build agents receive ONLY task-relevant atoms + their dependencies. Never the full spec.
2. **Coverage reports:** Build agents output a map: `{atom_id: {ac_id: {file, line, test}}}`. Validation checks completeness.
3. **Spec-linked tests:** Tests tagged with `@pytest.mark.spec("REQ-SRC-0001", "AC-1")`. Failures identify exact spec violations.

## Commands

```bash
python engines/source/scripts/validate_spec.py     # Validate all atoms against schema
python engines/source/scripts/generate_views.py     # Generate human-readable Markdown views
```

## Required Reading (ordered)

1. This file
2. `spec/INDEX.yaml` — current atom inventory
3. Root `CLAUDE.md` + `AGENTS.md` — project governance
4. `reference/KNOWLEDGE_INTEGRITY.md` — 7-threat model
5. Archive `ARCHIVE_INDEX.md` — what's recoverable from v1

## Owner Design Principles (from Session 1 interviews)

1. Agent-first, owner-validates. Owner hints are cross-validation, never primary data.
2. Library never refuses knowledge. Sciences are a growable registry.
3. Zero-tolerance for attribution errors. The #1 quality metric.
4. Minimal owner review. Agents resolve disagreements autonomously.
5. Truth-seeking, not consensus-forcing. Disputed metadata IS valid output.
6. No binding downstream contracts. All engines rebuilt from first principles.
