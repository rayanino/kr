# How to Start

## One-Time Setup (5 minutes)

In Claude Chat, create a project called "KR" and configure:

**1. Enable "Code Execution and File Creation"** in the project's feature settings. This is required — Claude works directly in the repo using bash commands. Without it, nothing works.

**2. Enable "Web Search"** in the project's feature settings. Claude needs web search for mandatory research during SPEC writing. Without it, research steps will block.

**3. Custom Instructions:**
Go to https://github.com/rayanino/kr and open `reference/PROJECT_INSTRUCTIONS.md`. Copy everything from line 5 onward (starting with "You are the architect"). Paste into the project's Custom Instructions field.

Then replace `$KR_REPO_URL` with:
```
https://rayanino:YOUR_TOKEN_HERE@github.com/rayanino/kr.git
```
(The token is in the project file `Github_key`.)

**4. Project Knowledge Files:** From the same GitHub repo, download `reference/DEEP_REASONING_PROTOCOL.md` and add it as a project knowledge file.

**5. Project Files:** The following should be attached as project files:
- `Github_key`

Remove any other project files (including the roadmap, ABD repo link, KR repo link if they were previously attached). The repo contains everything Claude needs.

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

## Recommended: Peer Review After Major SPECs

After each engine SPEC is completed, consider opening a SEPARATE new conversation and saying:

```
Review the source engine SPEC (engines/source/SPEC.md) against the Perfection Standard. Be a hostile auditor — find every defect.
```

A fresh Claude with no authorship bias will catch things the writing session missed. This is optional but strongly recommended for the first 2-3 SPECs (which set the quality bar for everything after).

## When All SPECs Are Done

NEXT.md will guide the session to do cross-SPEC consistency verification and full coherence review. But you can also trigger this manually:

```
All engine and component SPECs are complete. Do a full coherence review of the entire documentation stack.
```
