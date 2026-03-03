# consensus — Multi-Model Agreement Subsystem

Implements VISION.md §2.2 constraint: multi-model consensus for content decisions.

## Purpose

Consensus coordinates independent LLM evaluation to verify knowledge claims before they are finalized in the library. This ensures accuracy through agreement rather than relying on a single model's judgment.

## Key Responsibilities

1. **Agreement Protocol** — Collect independent evaluations from multiple models
2. **Threshold Enforcement** — Require N-of-M agreement before accepting decisions
3. **Conflict Resolution** — Log and escalate disagreements for human review
4. **Audit Trail** — Maintain full record of consensus deliberations

## Input/Output

- **Input**: Decisions to validate (excerpts, entries, placements)
- **Output**: Consensus verdict (APPROVED, NEEDS_REVIEW, REJECTED)

## Current Status

See SPEC.md for detailed interface. Tests in `tests/` directory.

Tests: 174 items collected
## Notes

No source-format-specific logic here (normalization boundary already passed).

