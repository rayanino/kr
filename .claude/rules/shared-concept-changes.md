When modifying a shared concept (enum, verdict, status, classification, error code) that appears across multiple files:

1. **Grep first**: Search for the concept name across ALL agent definitions (`.claude/agents/`), reference docs (`reference/`), SPEC files (`engines/*/SPEC.md`), and source code (`engines/*/src/`, `shared/*/src/`).
2. **Check every consumer**: For each file found, verify the new/changed value appears in ALL relevant contexts: definitions, comparison tables, output format templates, validation logic, documentation, test expectations.
3. **Output templates are high-risk**: When adding a new enum value, output format templates and summary tables are the most commonly missed consumers. Check these FIRST.
4. **Self-review is insufficient**: After updating all consumers, dispatch at least one independent reviewer. Self-review has blind spots for ripple-effect changes because the same mental model that produced the work reviews it.
