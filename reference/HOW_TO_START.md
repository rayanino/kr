# How to Start — خزانة ريان Autonomous Sessions

## One-Time Setup

Create a new Claude Chat project. Name it whatever you want (e.g., "KR").

### 1. Enable features

In the project's feature settings, enable:
- **Code Execution and File Creation** — required, Claude works in the repo directly
- **Web Search** — required, Claude does mandatory research during SPEC refinement

### 2. Custom Instructions

Go to this URL in your browser:
```
https://github.com/rayanino/kr/blob/master/reference/PROJECT_INSTRUCTIONS.md
```

Click the "Raw" button (top right of the file). Select all text from line 5 (starting with "You are the architect") to the end. Copy it.

In the project's Custom Instructions field, paste the copied text.

No variables to replace — Claude reads the GitHub token from the `Github_key` project knowledge file automatically.

### 3. Project Knowledge Files

Add TWO project knowledge files:

**File 1: `DEEP_REASONING_PROTOCOL.md`**
Download from: `https://github.com/rayanino/kr/blob/master/reference/DEEP_REASONING_PROTOCOL.md`
(Click "Raw" → Save As → upload as project knowledge)

**File 2: `Github_key`**
Create a plain text file containing only your GitHub personal access token (the string starting with `ghp_`). Name it `Github_key`.

### Verification

Your project should have:
- Custom Instructions: ~110 lines starting with "You are the architect"
- 2 knowledge files: `DEEP_REASONING_PROTOCOL.md` and `Github_key`
- Code Execution: enabled
- Web Search: enabled

## Every Session

Open a new conversation in the project. Send:

```
Continue the project.
```

Claude will clone the repo, read NEXT.md for its task, do the work, commit, and push. You may be asked domain questions about Islamic scholarship — answer from your experience.

### If You Want a Specific Type of Session

- **Design review:** "Run a design review on [component or 'the full system']."
- **Feedback:** "I have feedback on your last session: [describe your concern]."
- **Normal work:** "Continue the project." — NEXT.md directs Claude to the right task.

## If Something Breaks

If Claude says it can't clone or push:
1. Is the GitHub token still valid? (Tokens expire — generate a new one and update the `Github_key` knowledge file)
2. Is Code Execution enabled in project settings?

If Claude says it can't search the web:
1. Is Web Search enabled in project settings?
