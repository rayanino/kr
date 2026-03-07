# Source Engine Project — Knowledge Files to Upload

Upload these files to the project's "Project knowledge" section. They provide the context Claude needs for all source engine work.

## Essential (upload first)

1. **`engines/source/SPEC.md`** — The source engine specification. This is the primary working document.

2. **`engines/source/contracts.py`** — Pydantic data models for source engine input/output. Claude needs these to verify contract compliance.

3. **`STEERING.md`** — Concise project context (architecture, data flow, key decisions, tech stack). 78 lines.

4. **`KNOWLEDGE_INTEGRITY.md`** — The 7 corruption threats. Referenced by kr-integrity and kr-finalize skills.

5. **`SILENT_FAILURES.md`** — The 7 silent failure patterns. Referenced by kr-integrity and kr-finalize skills.

6. **`reference/DEEP_REASONING_PROTOCOL.md`** — The Perfection Standard (25 criteria) and SPEC template. Referenced by kr-finalize and kr-integrity skills.

## Source-Engine Specific Context

7. **`engines/normalization/contracts.py`** — The downstream engine's input contract. Needed to verify boundary compatibility (what the source engine must produce for normalization to consume).

8. **`reference/ENTRY_EXAMPLE.md`** — The target output quality. Helps Claude understand what the entire pipeline must ultimately produce.

9. **`CREATIVE_MANDATE.md`** — The creative protocol. Referenced by kr-research skill.

## Optional (add if context budget allows)

10. **`reference/RESOURCES.md`** — Technology inventory (tools, libraries, APIs). Useful during kr-build-prep and kr-research.

11. **`reference/DOMAIN.md`** — Deep domain context about Islamic scholarly traditions. Useful when handling domain comments.

12. **`reference/RESEARCH_LOG.md`** — Findings from the research phase. Useful for avoiding repeated research.

## DO NOT Upload

- VISION.md (too large — 47K tokens, STEERING.md has the summary)
- SESSION_LOG.md (history noise, not useful for current work)
- kr_decisions.md (long decision log, reference only when needed)
- Any engine SPECs except source and normalization contracts
- Any files from engines/ subdirectories except the two listed above
