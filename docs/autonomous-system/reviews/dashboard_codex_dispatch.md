# Codex CLI Dispatch — Dashboard Structural Verification

**Target:** Codex CLI (`codex exec`)
**Branch:** `excerpting-foundations-hardening-20260404`
**Date:** 2026-04-07
**Context:** Dashboard built and hardened after 3-reviewer CC audit. Need independent structural verification.

## Prompt

```
Review the KR autonomous dashboard implementation for structural correctness, type safety, and robustness.

FILES TO REVIEW:
- scripts/autonomous_dashboard/app.py (FastAPI routes, error handling, template globals)
- scripts/autonomous_dashboard/store.py (data access layer, JSONL reading with graceful degradation)
- scripts/autonomous_schemas.py (Pydantic models — focus on DRPrompt, Finding, Idea, append_jsonl, read_jsonl)
- scripts/dashboard.py (launcher)
- scripts/seed_batch2_prompts.py (one-time seeder)

CHECK FOR:
1. Type safety: run pyright on all 5 Python files. Report any errors.
2. Pydantic model correctness: Is DRPrompt.prompt_id pattern constraint correct? Does the model_validator on dedup_hash work?
3. Error handling: The _safe_read_jsonl in store.py catches parse errors gracefully. Is the except clause too broad (catches Exception)? Should it be narrower?
4. FastAPI patterns: Is response_model=None correct on the POST route? Is the global exception handler pattern correct?
5. File I/O on Windows: append_jsonl uses os.fsync() — is this correct on Windows NTFS? Does open(..., "a") guarantee append atomicity?
6. Path resolution: store.py uses Path(__file__).resolve().parent.parent.parent. Is this fragile? What happens under symlinks?
7. UUID-based idea IDs: submit_idea uses uuid4().hex[:8]. What is the collision probability over 3 months of use?
8. Template globals registration: templates.env.globals["target_label"] = _target_label — is this the correct Jinja2 pattern?

DO NOT REVIEW:
- Arabic text content or scholarly domain logic
- CSS or visual design
- HTMX or JavaScript behavior

OUTPUT FORMAT:
For each finding: severity (CRITICAL/HIGH/MEDIUM/LOW), file:line, issue description, recommended fix.
```
