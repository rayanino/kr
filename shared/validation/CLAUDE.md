# validation — Data Quality Checks Subsystem

Implements structured validation of all artifacts throughout the pipeline.

## Purpose

Validation ensures every artifact meets KR schema requirements before being used downstream. Catches malformed data early, preventing garbage-in-garbage-out scenarios.

## Key Responsibilities

1. **Schema Validation** — Verify all artifacts conform to defined schemas
2. **Consistency Checks** — Cross-reference integrity (e.g., cited sources exist)
3. **Constraint Verification** — Enforce VISION.md properties (self-containment, etc.)
4. **Error Reporting** — Detailed diagnostics for debugging failures

## Input/Output

- **Input**: Artifact to validate + schema definition
- **Output**: Validation report (PASS, FAIL with details)

## Current Status

See SPEC.md for validation rules. Tests in `tests/` directory.

Tests: 34 items collected
## Notes

No source-format-specific logic here (normalization boundary already passed).

