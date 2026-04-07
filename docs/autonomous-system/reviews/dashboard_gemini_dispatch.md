# Gemini CLI Dispatch — Dashboard Arabic Safety + Architecture Verification

**Target:** Gemini CLI (`gemini -p`)
**Branch:** `excerpting-foundations-hardening-20260404`
**Date:** 2026-04-07
**Context:** Dashboard built and hardened after 3-reviewer CC audit. Need Arabic safety and architecture verification.

## Prompt

```
Review the KR autonomous dashboard for Arabic text safety and architectural soundness.

FILES TO REVIEW:
- scripts/autonomous_dashboard/templates/base.html (layout, CSS, JavaScript)
- scripts/autonomous_dashboard/templates/relay.html (DR relay queue page — displays Arabic text in prompts)
- scripts/autonomous_dashboard/templates/findings.html (findings page — displays Arabic text in finding descriptions)
- scripts/autonomous_dashboard/store.py (data access layer — reads JSONL with Arabic content)
- scripts/autonomous_schemas.py (Pydantic models — DRPrompt contains Arabic text in topic and prompt_text fields)
- overnight_codex/autonomous/knowledge_base/dr_prompts/batch_2.jsonl (real data with Arabic text)
- overnight_codex/autonomous/knowledge_base/findings.jsonl (real data with Arabic text)

ARABIC TEXT SAFETY CHECKS:
1. The prompt text blocks contain mixed Arabic/English. Template uses dir="auto" on the prompt-block div. Is this correct for bidirectional text with Arabic scholarly terms (حجية فهم السلف, إجماع السلف, etc.)?
2. The JSONL files are read with encoding="utf-8-sig" (store.py _safe_read_jsonl). Is utf-8-sig correct for files that contain Arabic text? Does it strip BOM safely without affecting Arabic characters?
3. The finding titles and descriptions contain Arabic terms. Jinja2 autoescape is ON. Does autoescape damage Arabic characters or diacritics (tashkeel)?
4. The copy-to-clipboard JavaScript copies block.innerText. When the user pastes into Gemini DR, will Arabic text survive the copy-paste round trip?
5. Are there any cases where the CSS white-space: pre-wrap could break Arabic text layout?
6. The Pydantic DRPrompt model stores Arabic text in topic and prompt_text fields as plain str. Is there any implicit normalization (NFC/NFD) happening in Pydantic or FastAPI that could alter Arabic diacritics?

ARCHITECTURE CHECKS:
7. The dashboard implements 4 of 7 DESIGN.md §7.2 sections. For the MVP, is this sufficient? Which missing section should be added first?
8. The store layer reads JSONL on every request (no caching). For a single-user dashboard over 3 months, will this become a performance problem?
9. The _safe_read_jsonl function catches all exceptions during parsing and continues. Does this risk hiding real data corruption?

OUTPUT FORMAT:
For each finding: severity (CRITICAL/HIGH/MEDIUM/LOW), file:line, issue description, recommended fix.
Focus on Arabic text safety above all else — this is an Islamic scholarly system where text corruption is existential.
```
