---
globs: ["scripts/run_*.py", "engines/*/src/**/*.py"]
---
- Every pipeline run that makes LLM calls MUST capture traces via recursive-improve when the `--traces` flag is available.
- Default traces directory: `eval/traces/{engine}/{date}/`.
- After any pipeline run producing traces, note in the session summary: "Traces written to {path}. Run `recursive-improve eval {path}` for analysis."
- When reviewing ri improvement proposals (`eval/action_plan.md`), run `python scripts/ri_review.py` to auto-reject content-affecting changes before manual review.
- The `/ratchet` command is NEVER used for content classification prompts (genre, author, science scope, school attribution). Only for JSON formatting directives, error recovery instructions, and schema compliance.
