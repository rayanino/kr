# NEXT SESSION

## Context

Deep research into Claude Chat optimization was completed (2026-03-07). Full findings are in:
`skills/handoffs/claude-chat-research-2026-03-07.md`

## Key Finding: Native GitHub Integration

Claude.ai projects have a **built-in GitHub integration** that can replace our clone-at-start approach. The owner can sync repo files directly into project knowledge. This eliminates the need for the GitHub token in project knowledge and the STARTUP PROCEDURE in custom instructions.

## Owner Actions Required (Before Starting SPEC Review)

### 1. Enable Prerequisites
- Settings > Capabilities > Enable **Code execution and file creation** (required for skills)
- Customize > Skills > Verify all 6 kr-* skills are uploaded and enabled

### 2. Set Up Source Engine Project with GitHub Integration
- Create a new project for the source engine
- Instead of uploading Github_key + STEERING.md as knowledge files:
  - Click "+" in project knowledge → **Add from GitHub**
  - Connect to `rayanino/kr` repo
  - Select these files/folders to sync:
    - `engines/source/` (the source engine SPEC and code)
    - `STEERING.md` (project overview)
    - `KNOWLEDGE_INTEGRITY.md` (corruption threats)
    - `reference/DOMAIN.md` (Islamic studies domain)
    - `reference/ENTRY_EXAMPLE.md` (target output quality)
    - `reference/DEEP_REASONING_PROTOCOL.md` (quality standard)
    - `skills/shared/COMMENT_TEMPLATE.md` (comment format)
    - `NEXT.md` (current task context)
  - Keep Github_key as a **fallback** knowledge file (only needed if GitHub sync fails)

### 3. Paste Custom Instructions
- Use the revised custom instructions from `skills/source-engine-project/custom_instructions_v2.md`
- The revision removes the STARTUP PROCEDURE and adds GitHub sync awareness

### 4. Test
- Open a chat in the source engine project
- Ask: "What files do you have access to in the project knowledge?"
- Verify Claude can see the repo files
- Ask: "use kr-spec-review" to verify the skill activates
- If GitHub sync fails, say "clone the repo" to use the fallback

## Open Design Questions (for owner to decide)
- **One project per engine** vs **one project per workflow phase**? Research confirms one-per-engine is better (each engine needs different files).
- **Should we version skills in the repo** and regenerate zips, or manage them manually? Manual is fine for 6 skills. Revisit if count grows.

## Owner Status
- Currently reading the source engine SPEC and writing numbered domain comments
- Has OpenRouter API key ready
- No rush — quality over speed
