Show implementation status across all components.

Steps:
1. For each engine in engines/*/: count .py files in src/, count test files in tests/.
2. For each shared component in shared/*/: same counts.
3. For interface/scholar/: same counts.
4. Read each component's CLAUDE.md "Current State" section.
5. Present a table: Component | SPEC Lines | Code Files | Test Files | Status

This gives a quick view of what's specified vs. what's built.
