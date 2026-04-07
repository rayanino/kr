# DR24 Codex CLI Review — ExcerptRecord Rename Blast Radius

**Source:** Codex CLI (`codex exec`, GPT-5.4)
**Date:** 2026-04-07
**Dispatch:** /prompt-architect optimized, HR-23 compliant

## Q1 — Blast Radius: 148 total references

| Scope | Count |
|---|---:|
| `engines/excerpting/src/*.py` | 60 |
| `engines/excerpting/tests/*.py` | 27 |
| `tools/evaluate_excerpts.py` | 6 |
| `engines/excerpting/contracts.py` | 15 |
| `engines/excerpting/SPEC.md` | 40 |
| **Total** | **148** |

Target name: `TeachingUnitRecord` — cleanly separates from Phase 2 `TeachingUnit` (contracts.py:386) vs Phase 3 output `ExcerptRecord` (contracts.py:442).

## Q2 — Pydantic Alias Backward Compat

**Yes in principle, but not with current code as-is.**

- contracts.py has NO `model_config`, `ConfigDict`, `populate_by_name`, or `alias` entries
- writer.py serializes with `exc.model_dump(mode="json")` (line 73), NOT `by_alias=True`
- Resume path hardcodes JSON key `"excerpt_id"` (writer.py:60)

Two-tier safety:
- **Class rename only** (`ExcerptRecord` → `TeachingUnitRecord`): SAFE, no alias needed
- **Attr rename** (`excerpt_id` → `teaching_unit_id`): Only safe WITH aliases + alias-aware serialization changes

## Q3 — Timing: Choose B (code rename first, prompts later)

Reasoning (with line references):
1. Prompt already mostly "teaching unit" language (phase2_group.py:47), but remaining `excerpt` lexemes are behavior-bearing: `MENTION IS NOT EXCERPT` (phase2_group.py:95), "grouped into one excerpt" (phase2_group.py:105)
2. §4.11 already overloaded: GROUP_SYSTEM_PROMPT 1484/1500 + 36 blocked prompt atoms
3. DR24 itself recommends separating naming from prompt semantics (DR24:155, DR24:206)

**Recommendation:** Mechanical rename to `TeachingUnitRecord` in a dedicated low-risk pass. Keep JSON/file names stable (`excerpt_id`, `excerpts.jsonl`). Treat prompt wording as a SEPARATE evaluated change, not bundled with §4.11.
