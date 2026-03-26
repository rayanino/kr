---
description: "Test-driven development cycle for a SPEC behavioral rule"
allowed-tools: ["Bash(python *)", "Bash(python3 *)", "Bash(pytest *)", "Read", "Write", "Edit", "Grep", "Glob"]
---
Implement a SPEC behavioral rule using strict Red-Green-Refactor:

Arguments: $ARGUMENTS should be "<engine> <spec-section-or-rule>" (e.g., "excerpting §4.A.3 split oversized divisions")

## RED Phase — Write Failing Tests First

1. Read the specified SPEC section from `engines/<engine>/SPEC.md`
2. Extract testable behavioral rules with concrete examples
3. Write tests in `engines/<engine>/tests/` using REAL Arabic fixtures from `tests/fixtures/`
4. Tests MUST follow Arrange-Act-Assert structure
5. Run: `python -m pytest engines/<engine>/tests/ -x -q --tb=short`
6. **VERIFY tests FAIL.** If they pass, the behavior already exists — report and stop.

## GREEN Phase — Minimal Implementation

7. Implement the MINIMUM code to make all new tests pass
8. No optimization, no cleanup, no extra features beyond what the SPEC requires
9. Run tests again — ALL must pass (new AND existing)
10. If existing tests break, your implementation has a regression — fix it

## REFACTOR Phase — Clean Up

11. Refactor for clarity: extract helpers, improve naming, remove duplication
12. Run full engine test suite: `python -m pytest engines/<engine>/tests/ -v --tb=short`
13. Run pyright: `python -m pyright <modified-files>`
14. Verify Arabic safety and D-023 metadata preservation

## Rules

- Do NOT skip phases. Do NOT write implementation before tests fail.
- Every test must cite its SPEC rule in the docstring: `"""§4.A.3: [rule text]"""`
- Every test must use real Arabic text, never transliteration or English placeholders.
- If the SPEC rule is ambiguous, report it as `SPEC-AMBIGUITY: [description]` rather than guessing.
- If a test reveals a SPEC gap, create the test anyway with `@pytest.mark.skip(reason="SPEC gap: ...")`
