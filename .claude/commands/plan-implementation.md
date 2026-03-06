Decompose a SPEC section into implementation tasks.

Component and section: $ARGUMENTS (e.g., "source 4.A.2" or "normalization 4.A")

Steps:
1. Read the component's SPEC.md, focusing on the specified section.
2. Read existing code in `src/` to understand what's already built.
3. Read existing tests in `tests/` to understand what's tested.
4. For each behavioral rule in the section:
   a. Identify the concrete implementation task.
   b. Identify test cases needed.
   c. Identify dependencies (other tasks, shared components, external tools).
5. Order tasks by dependencies: data models → core logic → error handling → validation → integration.
6. Estimate complexity: LOW (pure logic, no LLM), MEDIUM (LLM calls, edge cases), HIGH (consensus, human gate, multi-format).

Output a numbered task list following the format in ORCHESTRATOR.md §Phase 2.
