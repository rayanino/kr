# Source Engine — محرك المصادر

**Phase:** Specification FROZEN — Ready for Build
**Branch:** `clean-start`

## Current State

The source engine spec is **frozen** (Session 3, 2026-04-15). 104 atoms, 97 confirmed, 3 deferred, 0 proposed. No production code exists yet. The previous implementation was archived to `reference/archive/v1/source_engine/` (reference-only, non-authoritative).

**Spec status:** 104 YAML atoms validated against `spec/schema.json`. Freeze gate complete across all 7 areas: vision, vocabulary, pipeline (steps 10-60), contracts, architecture, quality, questions. Contract architect review completed with all CRITICAL and HIGH findings resolved.

**3 deferred atoms (non-blocking):** DEC-SRC-0003 (level detection strategy), OQ-SRC-0001 (level detection ownership), OQ-SRC-0005 (agent monitoring scope). These can be resolved during build as design decisions emerge.

## Authoritative Files

| File | Role |
|------|------|
| `spec/INDEX.yaml` | Machine-readable registry of all spec atoms |
| `spec/schema.json` | JSON Schema validating all atom YAML files |
| `spec/README.md` | Canonical reader order for the source spec |
| `spec/00-vision/` | Purpose, scope, non-goals, and success criteria |
| `spec/01-vocabulary/` | Canonical terms and naming rules |
| `spec/10-pipeline/` | Ordered source-engine steps with collocated normative atoms |
| `spec/20-contracts/` | Output, dossier, registry, and handoff contract surfaces |
| `spec/30-architecture/` | Registry model, agent-team structure, and state decisions |
| `spec/40-quality/` | Cross-cutting invariants and quality rules |
| `spec/50-questions/` | Unresolved blockers only |
| `spec/60-evidence/` | Owner feedback, archive findings, coworker reviews, and DR evidence (non-normative) |

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

## Spec Format: Numbered Behavior-First Spec

The source spec uses a numbered reader spine. Engineers should understand the system in this order:

1. vision
2. vocabulary
3. pipeline
4. contracts
5. architecture
6. quality
7. open questions
8. evidence

Generated views are overlays for inspection. They are not canonical.

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

## Build Phase

The spec is frozen and ready for implementation. No production code exists yet.

**Pipeline steps in order:** upload_receipt → freeze_and_manifest → container_classification → intake_analysis → metadata_deliberation → source_admission_and_normalization_handoff

**Implementation approach:**
- Each atom's `behavior` field defines trigger/preconditions/postconditions/error_conditions — implement these directly.
- Each atom's `acceptance_criteria` define the test cases in given/when/then format — implement as pytest with `@pytest.mark.spec("REQ-SRC-XXXX", "AC-N")`.
- `depends_on` in each atom defines what must be implemented first.
- Start with steps 10-20 (upload receipt + freeze) as a tracer bullet — they're the simplest and validate the build infrastructure.
- Read `spec/views/by-step/` for human-readable summaries per pipeline step.

**Code layout:** `engines/source/src/` for implementation, `engines/source/tests/` for tests, `engines/source/contracts.py` for Pydantic data models.

**Key contracts to implement first (from atoms):**
- `RawUploadRecord` (REQ-SRC-0001)
- `FrozenSource` + `FrozenMemberManifest` (REQ-SRC-0018)
- `ContainerClassification` (REQ-SRC-0017/0020/0041)
- `IntakeDossier` (REQ-SRC-0019)
- `SourceMetadata` (CON-SRC-0004)
- `EditionGroup` / `EditionHolding` / `VolumeHolding` (DEC-SRC-0018, REQ-SRC-0044)

## Commands

```bash
python engines/source/scripts/validate_spec.py     # Validate all atoms against schema
python engines/source/scripts/generate_views.py     # Generate human-readable Markdown views
```

## Required Reading (ordered)

1. This file
2. `spec/README.md`
3. `spec/00-vision/README.md`
4. `spec/01-vocabulary/README.md`
5. `spec/10-pipeline/README.md`
6. `spec/20-contracts/README.md`
7. `spec/30-architecture/README.md`
8. `spec/40-quality/README.md`
9. `spec/INDEX.yaml` — current atom inventory
10. Root `CLAUDE.md` + `AGENTS.md` — project governance
11. `reference/KNOWLEDGE_INTEGRITY.md` — 7-threat model
12. Archive `ARCHIVE_INDEX.md` — what's recoverable from v1

## Owner Design Principles (from Session 1 interviews)

1. Agent-first, owner-validates. Owner hints are cross-validation, never primary data.
2. Library never refuses knowledge. Sciences are a growable registry.
3. Zero-tolerance for attribution errors. The #1 quality metric.
4. Minimal owner review. Agents resolve disagreements autonomously.
5. Truth-seeking, not consensus-forcing. Disputed metadata IS valid output.
6. No binding downstream contracts. All engines rebuilt from first principles.
