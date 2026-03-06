# Human Gate (بوابة الإنسان)

Cross-engine component for human approval checkpoints.

## Role

The human gate manages checkpoint lifecycle for irreversible library changes. It creates, queries, resolves, and expires checkpoints that engines submit when they need owner decisions. It does NOT present checkpoints (that's the scholar interface) or analyze corrections (that's the feedback component).

## State

- **Status**: SPEC complete (413 lines, all 10 sections). Code: ABD-era legacy (D-019), needs complete rewrite.
- **Parent**: See shared/CLAUDE.md
- **Tests**: shared/human_gate/tests/test_human_gate.py (45 items, all ABD-era — need rewrite)

## Key Responsibilities

1. Checkpoint lifecycle (create → pending → approved/rejected/modified/expired)
2. Pre-approval policy management (auto-approve for routine decisions)
3. Bidirectional validation (verify owner decisions against library knowledge)
4. Owner confidence calibration per science (adjust gate conservatism)
5. Queue health monitoring and stale checkpoint detection

## Architecture

- Library (not a service) — engines import and call directly
- File-based storage: `library/gates/pending/`, `library/gates/resolved/`
- No external dependencies beyond Python stdlib + Pydantic v2 + shared/validation
- 18 gate types across all engines (source: 6, normalization: 3, excerpting: 1, taxonomy: 5, cross-engine: 1, meta: 1)
- Restricted gate types (never pre-approvable): tax_evolution_proposal, tax_rollback, source_trust_evaluation, gate_policy_suggestion

## Transformative Capabilities

- §4.B.1: Gate learning — suggests pre-approval policies from owner approval patterns
- §4.B.2: Review efficiency intelligence — behavioral metadata for scholar interface
- §4.B.3: Library consistency checking — deep semantic checks on owner decisions

## Integration Points

- All engines that create checkpoints (source, normalization, excerpting, taxonomy)
- shared/validation (schema validation, referential integrity)
- shared/feedback (receives audit trail for pattern analysis)
- interface/scholar (consumes checkpoint queue, presents to owner)

## Reference

- SPEC: shared/human_gate/SPEC.md
- VISION.md §9 (Human Gates), §8.1 (Layer 3: Judgment)

## SPEC Refinement Status
- Cycle 0 (not yet started)
- Implementation-ready: NO — refinement required before implementation
