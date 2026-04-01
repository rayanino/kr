# Weekend DR Prompts — Copy-Paste Ready

Dispatch these from your phone/browser. Each is self-contained — just paste into the respective DR session.

## Before You Paste

- ChatGPT DR: open ChatGPT, start a new chat, switch the tool/chat mode to `Deep Research`, then paste Prompt 1 exactly as written.
- Claude DR: open Claude, start a new chat, switch the chat mode to `Research` or `Deep Research` if that option is shown, then paste Prompt 2 exactly as written.
- Gemini DR: open Gemini, start a new chat, switch to `Deep Research` or the closest research mode shown in the UI, upload the listed files first, then paste Prompt 3.
- If any app asks to confirm web browsing, repository access, or file access, allow it for that session.
- Keep the repo file paths exactly as written. Do not paste file contents into ChatGPT DR or Claude DR.

---

## 1. ChatGPT DR (Pro Deep Research Mode)

> **Task: Pre-review the KR excerpting questionnaire before the owner fills it in.**
>
> Read these files from the `rayanino/kr` GitHub repository:
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
> Read these files from the `rayanino/kr` GitHub repository:
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
