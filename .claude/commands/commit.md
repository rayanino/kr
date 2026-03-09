---
description: Review all changes, group them logically, and create conventional commits.
allowed-tools: Bash(git add:*), Bash(git commit:*), Bash(git diff:*), Bash(git status:*)
model: haiku
---
Review all uncommitted changes in the repository.

Steps:
1. Run `git status` and `git diff --stat` to see what's changed.
2. Group related changes into logical units (one commit per logical change).
3. For each group, stage the files and create a conventional commit:
   - `feat(engine): description` — new capability
   - `fix(engine): description` — bug fix
   - `refactor(engine): description` — code restructure without behavior change
   - `docs(scope): description` — documentation only
   - `test(engine): description` — adding or fixing tests
   - `chore(scope): description` — tooling, config, dependency changes
4. Commit messages must be specific. BAD: "Update source engine". GOOD: "feat(source): add Shamela HTML format detection via magic-byte sniffing"

If $ARGUMENTS is provided, use it as guidance for the commit scope/message.
