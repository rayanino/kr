# How to Start

## One-Time Setup (5 minutes)

In Claude Chat, create a project called "KR" and configure:

**1. Enable "Code Execution and File Creation"** in the project's feature settings. This is required — Claude works directly in the repo using bash commands. Without it, nothing works.

**2. Custom Instructions:**
Open `reference/PROJECT_INSTRUCTIONS.md`. Copy everything from line 5 onward (starting with "You are the architect"). Paste into the project's Custom Instructions field.

Then replace `$KR_REPO_URL` with:
```
https://rayanino:YOUR_TOKEN_HERE@github.com/rayanino/kr.git
```
(The token is in the project file `Github_key`.)

**3. Project Knowledge Files:** Add one file:
- `reference/DEEP_REASONING_PROTOCOL.md`

**4. Project Files:** The following should be attached as project files:
- `Github_key`

Remove any other project files (including the roadmap if it was previously attached — it's now archived in the repo at `reference/archive/`). The repo contains everything Claude needs.

That's it. Claude clones the repo and reads everything else directly.

## Every Session

Open a new conversation in the KR project. Send:

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
