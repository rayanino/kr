# Source Engine Project — Knowledge Files

Upload these to the project's "Project knowledge" section.

## Essential (upload first)

1. **`engines/source/SPEC.md`** — The source engine specification.
   *Consider splitting into sections for finalization phase:*
   - `spec_sections_1-3.md` (Purpose, Input, Output contracts)
   - `spec_section_4.md` (Processing — the core, longest section)
   - `spec_sections_5-7.md` (Validation, Consensus, Errors)
   - `spec_sections_8-10.md` (Config, State, Tests)
   *Use the full file during comment review. Use split files during finalization audits.*

2. **`engines/source/contracts.py`** — Pydantic data models.

3. **`STEERING.md`** — Concise project context (78 lines).

4. **`KNOWLEDGE_INTEGRITY.md`** — The 7 corruption threats.

5. **`SILENT_FAILURES.md`** — The 7 silent failure patterns.

6. **`reference/DEEP_REASONING_PROTOCOL.md`** — Perfection Standard (25 criteria).

## Source-Engine Specific

7. **`engines/normalization/contracts.py`** — Downstream engine's input contract.

8. **`reference/ENTRY_EXAMPLE.md`** — Target output quality.

9. **`CREATIVE_MANDATE.md`** — Creative protocol for kr-research.

## Session-Specific (add as needed)

10. **Your comments file** (e.g., `COMMENTS_SOURCE.md`) — Use the template from `skills/shared/COMMENT_TEMPLATE.md`. Upload when your comments are ready.

11. **Handoff documents** — When a chat produces a handoff summary, upload it for the next chat.

## Optional

12. **`reference/RESOURCES.md`** — Tool inventory (useful during kr-build-prep and kr-research).

13. **`reference/DOMAIN.md`** — Domain context (useful for complex domain comments).

## Context Budget Warning

Claude Chat has a 200K token context window. Project knowledge files consume part of this. With all essential files loaded (~50K tokens estimated), you have ~150K tokens for conversation. Monitor this:
- If chats feel "forgetful," you may have too many knowledge files loaded
- Remove files not needed for the current task
- The split SPEC sections help: load only the section being audited

## DO NOT Upload

- VISION.md (47K tokens — too large, STEERING.md has the summary)
- SESSION_LOG.md (history noise)
- kr_decisions.md (reference only when needed)
- Engine SPECs other than source + normalization contracts
