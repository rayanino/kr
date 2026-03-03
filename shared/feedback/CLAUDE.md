# feedback — Engine Feedback Loop Subsystem

Implements iterative refinement through structured feedback between engines.

## Purpose

Feedback enables engines to signal problems upstream (e.g., an engine detects a passaging error and re-routes for normalization review). Supports the "human gates" (VISION.md §9) by flagging items for owner review.

## Key Responsibilities

1. **Issue Logging** — Record problems detected by any engine
2. **Priority Assignment** — Classify by severity and impact
3. **Routing** — Direct feedback to appropriate handler
4. **Follow-up Tracking** — Ensure issues are resolved before library release

## Input/Output

- **Input**: Issue report from any engine (exception, validation failure, consensus disagreement)
- **Output**: Feedback record with routing decision and resolution status

## Current Status

See SPEC.md for feedback taxonomy. Tests in `tests/` directory.

## Notes

No source-format-specific logic here (normalization boundary already passed).

