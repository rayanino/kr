This is a new KR session. The previous chat completed the CLI adapter review and first real integration test. Start the session protocol now.

<session_context>
**Where we are:** The CLI adapter is WORKING. First real integration test produced 23 excerpts from شرح ابن عقيل at $0 cost. All 800 tests pass. But large chunks (5K words) timeout at 120s, blocking the 5-book overnight run.

**What this session must accomplish (in order):**
1. ChatGPT 5.4 deep research on 5-book run risks (prompt is pre-written in NEXT.md — copy-paste it to ChatGPT and wait for the report before doing ANYTHING else)
2. Based on ChatGPT's report, design and delegate the timeout fix to CC
3. Prepare the 5-book overnight run command for my machine

**Previous session's last commit:** `e4233c7a` — all fixes pushed, repo clean.
</session_context>

<critical_rules>
- ChatGPT deep research is MANDATORY before any decision. The prompt is ready in NEXT.md Step 1. Do not skip it, do not summarize it, do not proceed without it.
- Do NOT implement code yourself — delegate to CC via NEXT.md.
- This is a fresh chat — do NOT rely on memory of what the repo looks like. Clone and read everything fresh.
- Read NEXT.md FIRST. It has the complete plan including the pre-written ChatGPT prompt.
</critical_rules>

Start with the session protocol: clone repo → read NEXT.md → git log → read relevant skills. Then tell me exactly what to send to ChatGPT.
