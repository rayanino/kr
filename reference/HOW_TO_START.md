# How to Start — خزانة ريان Autonomous Sessions

## One-Time Setup

Create a new Claude Chat project. Name it whatever you want (e.g., "KR Autonomous").

### 1. Enable features (two toggles)

In the project's feature settings, enable:
- **Code Execution and File Creation** — required, Claude works in the repo directly
- **Web Search** — required, Claude does mandatory research during SPEC writing

### 2. Custom Instructions

Go to this URL in your browser:
```
https://github.com/rayanino/kr/blob/master/reference/PROJECT_INSTRUCTIONS.md
```

Click the "Raw" button (top right of the file). Select all text from line 5 (starting with "You are the architect") to the end. Copy it.

In the project's Custom Instructions field, paste the copied text.

Then find `$KR_REPO_URL` in the pasted text (use Ctrl+F) and replace it with:
```
https://rayanino:YOUR_TOKEN_HERE@github.com/rayanino/kr.git
```
Replace `YOUR_TOKEN_HERE` with the token from your `Github_key` project file (the long string starting with `ghp_`).

### 3. Project Knowledge Files

Download this file and add it as a project knowledge file:
```
https://github.com/rayanino/kr/blob/master/reference/DEEP_REASONING_PROTOCOL.md
```
(Click "Raw" → Save As → upload to the project as a knowledge file)

### 4. Project Files

Add one project file:
- A text file containing your GitHub token (the same `Github_key` file from the current project, or create a new text file with the token)

Name it `Github_key`.

Do NOT add any other project files. No roadmap, no repo links. The repo contains everything Claude needs.

### Verification

Your project should have:
- Custom Instructions: ~190 lines starting with "You are the architect"
- 1 knowledge file: `DEEP_REASONING_PROTOCOL.md`
- 1 project file: `Github_key`
- Code Execution: enabled
- Web Search: enabled

## Every Session

Open a new conversation in the project. Send:

```
Continue the project.
```

Claude will clone the repo, read NEXT.md for its task, do the work, commit, and push. You may be asked domain questions about Islamic scholarship — answer from your experience.

## If You Disagree With a Decision

Open a new conversation and say:

```
I have feedback on your last session: [describe your concern].
```

Claude will pull the repo, find the relevant decision, and address your concern.

## If Something Breaks

If Claude says it can't clone or push, check:
1. Is the GitHub token still valid? (Tokens can expire)
2. Is the repo URL correct in the Custom Instructions?
3. Is Code Execution enabled?

If Claude says it can't search the web, check:
1. Is Web Search enabled in the project settings?
