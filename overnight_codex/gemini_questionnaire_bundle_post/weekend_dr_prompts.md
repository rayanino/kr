# Weekend DR Prompts — Copy-Paste Ready

Dispatch these from your phone/browser. Each is self-contained — just paste into the respective DR session.

## Before You Paste

- Current questionnaire state: 40 core slots, 38 answerable right now, 2 comparison slots intentionally blocked (`CJ-2`, `CJ-3`), plus 6 optional supplemental owner questions.
- Owner-answer guardrail: the owner's responses are high-value signal, but never final authority. Treat them as feedback to be challenged, not as commands to obey literally.
- Remote-vs-local rule: ChatGPT DR and Claude DR usually see only what is available in the remote repo or what you paste into the chat. They do **not** automatically see current unpushed local files.
- If the current work has not been pushed, do **not** ask ChatGPT DR or Claude DR to review the "current repo state" by file path alone. Either:
  - push the relevant branch first, or
  - paste/upload the current local files you want reviewed.
- Gemini DR is the safest browser DR path for unpushed local work because it already expects explicit file uploads.
- ChatGPT DR: open ChatGPT, start a new chat, switch the tool/chat mode to `Deep Research`, then paste Prompt 1 exactly as written.
- Claude DR: open Claude, start a new chat, switch the chat mode to `Research` or `Deep Research` if that option is shown, then paste Prompt 2 exactly as written.
- Gemini DR: open Gemini, start a new chat, switch to `Deep Research` or the closest research mode shown in the UI, upload the listed files first, then paste Prompt 3.
- If any app asks to confirm web browsing, repository access, or file access, allow it for that session.
- Keep the repo file paths exactly as written. Do not paste file contents into ChatGPT DR or Claude DR.

---

## 1. ChatGPT DR (Pro Deep Research Mode)

> **Task: Pre-review the KR excerpting questionnaire before the owner fills it in.**
>
> First check whether the files you can access are the current intended state.
> If you only have GitHub remote access and the current local questionnaire work
> is unpushed, say that explicitly and do **not** pretend you reviewed the
> current local packet.
>
> Read these files from the `rayanino/kr` GitHub repository **only if they are
> the intended review target**, otherwise use the pasted/uploaded local files:
> - `integration_tests/questionnaire/interactions.json` — 40 structured questionnaire interactions
> - `integration_tests/questionnaire/OWNER_QUESTIONNAIRE.md` — the full questionnaire text
> - `integration_tests/questionnaire/CRITICAL_EVALUATION_GUIDE.md` — the post-completion evaluation plan
> - `NEXT.md` — the master plan for the excerpting hardening operation
>
> The owner will spend Thu-Sun answering these 40 interactions about what Islamic scholarly excerpts should look like. His answers will calibrate the excerpting engine's behavior.
>
> **Evaluate:**
> 1. Which interactions will produce the highest-signal answers? Which are likely to produce ambiguous or low-signal responses?
> 2. Are there any interactions where the multiple-choice options don't cover the real answer space?
> 3. Does the ordering create anchoring bias? (e.g., seeing a fiqh excerpt first anchors all later genre judgments)
> 4. Are the 7 [EDGE CASE] interactions targeting the right boundaries?
> 5. What should the owner know BEFORE starting that would improve his answer quality?
>
> **Output:** Per-interaction signal assessment + pre-start recommendations for the owner.

---

## 2. Claude DR (Deep Research Mode)

> **Task: Prepare your evaluation criteria for the owner's questionnaire responses.**
>
> First check whether the files you can access are the current intended state.
> If you only have GitHub remote access and the current local questionnaire work
> is unpushed, say that explicitly and do **not** pretend you reviewed the
> current local packet.
>
> Read these files from the `rayanino/kr` GitHub repository **only if they are
> the intended review target**, otherwise use the pasted/uploaded local files:
> - `integration_tests/questionnaire/interactions.json` — 40 questionnaire interactions
> - `integration_tests/questionnaire/CRITICAL_EVALUATION_GUIDE.md` — your role as one of 6 evaluators
> - `engines/excerpting/SPEC.md` — the excerpting SPEC (focus on §4 domain rules, §6 decontextualization prevention)
> - `integration_tests/campaign_20260331/taysir/owner_feedback.jsonl` — the owner's 2 prior feedback comments
>
> After the owner finishes the questionnaire, you (Claude DR) will evaluate his responses for scholarly reasoning soundness. To prepare NOW:
>
> 1. Which interactions do you expect the owner (described as having "minimum Islamic knowledge") to struggle with most?
> 2. What specific things should you watch for in his responses?
> 3. For each dimension (granularity, self-containment, definitions, evidence, khilaf, genre, layers): what is the scholarly-correct answer vs what a layperson might answer?
> 4. Where might the owner's intuition be RIGHT even though he lacks formal training?
> 5. Draft your evaluation rubric — what criteria will you use for CONFIRMED / CHALLENGED / CONTRADICTION?
>
> **Output:** Per-dimension evaluation rubric + predicted struggle points + draft criteria.

---

## 3. Gemini DR (Deep Research Mode)

**Upload these files to the Gemini session:**
- `integration_tests/questionnaire/interactions.json`
- `integration_tests/questionnaire/CRITICAL_EVALUATION_GUIDE.md`
- `integration_tests/questionnaire/TEAM_TRANSLATION_GUIDE.md`

> **Task: Prepare pedagogical evaluation criteria for the owner's questionnaire responses.**
>
> Context: KR (خزانة ريان) is an Islamic scholarly library. The owner (a Muslim student with minimum Islamic knowledge) will spend 3 days answering 40 questionnaire interactions about what excerpts should look like. After he finishes, you will be one of 6 evaluators checking his answers for pedagogical soundness.
>
> The uploaded files contain: the 40 interactions (interactions.json), the evaluation protocol (CRITICAL_EVALUATION_GUIDE.md), and how answers map to SPEC rules (TEAM_TRANSLATION_GUIDE.md).
>
> **Prepare now:**
> 1. For each dimension tested (granularity, self-containment, definitions, evidence, khilaf, genre, layers): what does Islamic study methodology say the correct approach should be?
> 2. Which interactions test concepts where a student without formal seminary training is likely to make mistakes?
> 3. Are there study workflows (I'dad al-durus, hifz, muraja'a, muthakara) that the questionnaire should have covered but didn't?
> 4. Draft your evaluation criteria: when will you CONFIRM vs CHALLENGE the owner's answers?
> 5. What is the single most important thing the owner should get right for the library to be useful?
>
> **Output:** Per-dimension pedagogical evaluation rubric + predicted mistakes + evaluation criteria + priority assessment.

---

## After The Owner Finishes The Questionnaire

Use these after the owner has completed the active core questionnaire, and again
after the supplementals if his thinking materially changed.

In all three post-completion prompts, assume this rule:
the owner's answers are valuable but non-authoritative, and must be stress-tested
for contradictions, scholarly risk, feasibility, and long-run product damage.

Also assume this access rule:
- if you only see the remote repo, you only see pushed state
- if the current questionnaire responses or packet edits are local and unpushed, do not claim to have reviewed them unless they were pasted or uploaded into the DR session

## 4. ChatGPT DR (Post-Completion Review)

> **Task: Critically review the owner's completed KR excerpting questionnaire responses.**
>
> First check whether the files you can access are the current intended state.
> If the owner's responses or questionnaire edits are local and unpushed, say
> explicitly that remote-only access is stale and review only the pasted/uploaded
> files instead.
>
> Read these files from the `rayanino/kr` GitHub repository **only if they are
> the intended review target**, otherwise use the pasted/uploaded local files:
> - `integration_tests/questionnaire/questionnaire_responses.jsonl` — the owner's saved responses
> - `integration_tests/questionnaire/OWNER_QUESTIONNAIRE.md` — the exact questions he answered
> - `integration_tests/questionnaire/SUPPLEMENTAL_OWNER_QUESTIONS.md` — optional follow-up questions, if any were answered
> - `integration_tests/questionnaire/TEAM_TRANSLATION_GUIDE.md` — how answers map to SPEC/prompt decisions
> - `integration_tests/questionnaire/CRITICAL_EVALUATION_GUIDE.md` — the 6-coworker evaluation protocol
>
> **Evaluate:**
> 1. Which answers are highest-signal and immediately translatable into SPEC rules?
> 2. Which answers are too vague, contradictory, or under-specified to implement safely?
> 3. Which follow-up questions are still missing?
> 4. Which answers imply UI/display policy only, versus excerpt-boundary/pipeline policy?
> 5. Where did the owner reveal a stable governing principle that should become a real constraint?
>
> **Output:** High-signal answer list + contradiction list + missing follow-ups + recommended SPEC-facing interpretations.

---

## 5. Claude DR (Post-Completion Scholarly Review)

> **Task: Evaluate the scholarly soundness of the owner's completed questionnaire responses.**
>
> First check whether the files you can access are the current intended state.
> If the owner's responses or questionnaire edits are local and unpushed, say
> explicitly that remote-only access is stale and review only the pasted/uploaded
> files instead.
>
> Read these files from the `rayanino/kr` GitHub repository **only if they are
> the intended review target**, otherwise use the pasted/uploaded local files:
> - `integration_tests/questionnaire/questionnaire_responses.jsonl`
> - `integration_tests/questionnaire/OWNER_QUESTIONNAIRE.md`
> - `integration_tests/questionnaire/CRITICAL_EVALUATION_GUIDE.md`
> - `engines/excerpting/SPEC.md` — focus on the domain rules relevant to the answered dimensions
> - `integration_tests/campaign_20260331/taysir/owner_feedback.jsonl`
>
> **Evaluate:**
> 1. Which owner answers are scholarly sound and should be CONFIRMED?
> 2. Which answers would create dangerous or misleading excerpts if implemented literally?
> 3. Where is the owner correctly perceiving a real scholarly boundary, even if he uses non-technical language?
> 4. Where do the answers fail to account for multi-layer texts, comparative fiqh, hadith apparatus, or referential structure?
> 5. What are the sharpest follow-up challenges the team should bring back to the owner?
>
> **Output:** CONFIRMED / CHALLENGED / CONTRADICTION candidate table with reasoning and concrete follow-up challenges.

---

## 6. Gemini DR (Post-Completion Pedagogical Review)

**Upload these files to the Gemini session:**
- `integration_tests/questionnaire/questionnaire_responses.jsonl`
- `integration_tests/questionnaire/OWNER_QUESTIONNAIRE.md`
- `integration_tests/questionnaire/SUPPLEMENTAL_OWNER_QUESTIONS.md`
- `integration_tests/questionnaire/TEAM_TRANSLATION_GUIDE.md`
- `integration_tests/questionnaire/CRITICAL_EVALUATION_GUIDE.md`

> **Task: Evaluate the owner's completed questionnaire responses for pedagogical usefulness.**
>
> Context: KR is a personal Islamic scholarly library for a student with minimum Islamic knowledge. The owner has now answered the questionnaire about how excerpts should look and behave.
>
> **Evaluate:**
> 1. Will these answers produce excerpts that are actually teachable and learnable across fiqh, nahw, and usul-style texts?
> 2. Which answers support quick lookup but harm serious study, or vice versa?
> 3. Which answers ignore real study workflows like lesson preparation, memorization, muraja'a, or comparison?
> 4. Which answers should be treated as local preference, and which as true pedagogical constraints?
> 5. What are the highest-value remaining questions if the team gets one more chance to ask the owner something?
>
> **Output:** Pedagogical verdicts per major dimension + workflow risks + remaining highest-value owner questions.
