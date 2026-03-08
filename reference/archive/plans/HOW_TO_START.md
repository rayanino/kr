# How to Start — خزانة ريان Autonomous Sessions

## Create a New Project

1. Go to claude.ai → Projects → Create new project
2. Name it anything (e.g., "KR" or "خزانة ريان")

## Configure (4 things)

### 1. Custom Instructions

Go to: `https://github.com/rayanino/kr/blob/master/reference/PROJECT_INSTRUCTIONS.md`

Click "Raw." Copy everything from line 5 ("You are the architect...") to the end. Paste into the project's Custom Instructions field.

### 2. Knowledge File: DEEP_REASONING_PROTOCOL.md

Download from: `https://github.com/rayanino/kr/raw/master/reference/DEEP_REASONING_PROTOCOL.md`

Upload as a project knowledge file.

### 3. Knowledge File: Github_key

Create a plain text file named `Github_key` containing only:
```
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
```
Upload as a project knowledge file.

### 4. Enable Features

In project settings, enable:
- **Code Execution and File Creation** (required)
- **Web Search** (required)

## Verify

Your project has:
- Custom Instructions: ~120 lines starting with "You are the architect"
- 2 knowledge files: DEEP_REASONING_PROTOCOL.md, Github_key
- Code Execution: enabled
- Web Search: enabled

## Start Working

Open a new conversation. Type:

```
Continue the project.
```

Claude will clone the repo, read NEXT.md, and begin the current task (source engine creative session). It will research, invent capabilities, write them into the SPEC, commit, and push — all autonomously.

## Session Flow

Each "Continue the project" triggers one focused session. The repo's NEXT.md file tells Claude exactly what to do. At the end of each session, Claude writes a new NEXT.md for the next session.

Expected workflow for the preparatory phase:
- ~35-40 sessions over 3-5 weeks
- Each session: 1 focused task (creative OR precision OR hardening)
- Progress tracked in STATUS.md
- All work committed to the repo

## If Something Goes Wrong

- **Can't clone:** GitHub token expired → regenerate and update Github_key
- **Can't search:** Web Search not enabled in project settings
- **Session seems unfocused:** NEXT.md may be stale → Claude will run orient.py to recover
- **Want to give feedback:** Start a conversation with "I have feedback on your last session: [concern]"
- **Want a design review:** "Run a design review on [component]"
