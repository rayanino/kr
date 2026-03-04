# Human Gate (بوابة الإنسان)

Cross-engine component for human approval and feedback loops.

## Role

The human gate controls irreversible library changes. All modifications that could affect the public knowledge product require human approval or pre-approved policies.

## State

- **Status**: Stub (implementation from ABD tools/human_gate.py)
- **Parent**: See shared/CLAUDE.md
- **Tests**: shared/human_gate/tests/test_human_gate.py

## Key Responsibilities

1. Gate all irreversible library changes
2. Enforce approval workflows
3. Log approval decisions
4. Support appeal and override workflows
5. Validate pre-approval policies

## Constraints

- **Human gates.** No irreversible library change without owner approval or pre-approval policy. (VISION.md §9)

## Integration Points

- All engines that modify library/
- Consensus on safety-critical decisions

## Reference

## Current State

Tests: 45 items collected

