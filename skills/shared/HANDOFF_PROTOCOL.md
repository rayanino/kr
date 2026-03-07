# Session Handoff Protocol

When a Claude Chat conversation gets long, context quality degrades. This protocol ensures clean transitions between chats.

## When to Handoff

- After resolving 5+ complex comments in one chat
- When the conversation exceeds ~30 back-and-forth turns
- When you notice Claude repeating information or losing track of earlier decisions
- Before starting a new phase (e.g., from comment resolution to finalization)

## How to Handoff

### Step 1: Claude produces a handoff document

```markdown
# Handoff — [Task] [Engine Name] [Date]

## What Was Done
- [Bullet list of completed work]
- [Key decisions made, with reasoning]

## What Remains
- [Bullet list of pending work]
- [Specific next steps]

## Key Decisions
| Decision | Reasoning | Affects |
|----------|-----------|---------|
| [What was decided] | [Why] | [Which SPEC sections or downstream] |

## Files Changed
- [List of SPEC sections modified, with summary of changes]

## Context for Next Chat
[2-3 paragraph summary of the current state — what the next chat needs to know to continue without re-reading everything]
```

### Step 2: Owner saves the handoff

Copy the handoff into a file and upload it to the project knowledge as `HANDOFF_[date].md`. Or paste it at the start of the next chat.

### Step 3: Start new chat

Begin the new chat with: "Continuing from handoff [date]. [specific task for this chat]."

## What NOT to Carry Forward

- Full conversation history (that's what the handoff summarizes)
- Research findings already incorporated into SPEC changes
- Resolved comments (they're in the change manifest)
