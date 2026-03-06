Generate a test plan from a SPEC's behavioral rules.

Component: $ARGUMENTS (e.g., "source" or "normalization")

Steps:
1. Read the component's SPEC.md fully.
2. Extract every behavioral rule from §4 (Processing Specification).
3. Extract every error code from §7 (Error Handling).
4. Extract every validation check from §5 (Validation and Quality).
5. For each rule/code/check, generate a test case description:
   - Test name (following pattern: `test_{section}_{behavior}`)
   - Input setup (what test data is needed)
   - Expected behavior (what the test asserts)
   - Edge case variants (from SPEC edge case descriptions)

Output format:
```
# Test Plan: [Engine Name]
# Generated from: SPEC.md
# Total test cases: [N]

## §4.A.1 — [Section Title]
- test_4a1_basic_identification: Given [input], expect [output]
- test_4a1_missing_author: Given [input without author], expect [human gate checkpoint]
- test_4a1_duplicate_source: Given [existing source_id], expect [SRC_DUPLICATE_SOURCE error]

## §4.A.2 — [Section Title]
...

## §7 — Error Handling
- test_error_SRC_EMPTY_INPUT: Given empty file, expect error code SRC_EMPTY_INPUT
...
```

This plan is a blueprint for the test-runner, not executable code.
Read existing tests first — don't duplicate what already exists.
