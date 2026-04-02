# START HERE — Owner Questionnaire Guide

## What is this?

This is your personal evaluation session for the KR library. You will read excerpts from your books and tell us what you think about them. Your answers are one of the highest-value feedback sources the team has, but they are still feedback to be challenged and interpreted — not direct instructions.

There are **40 core questionnaire slots** split into 4 phases. Right now, **38 are answerable** and **2 comparison slots are intentionally locked** because the weekend `taysir` v2 run failed before valid comparison material existed. After the core packet, there is also a small optional supplemental packet in markdown.

**Critical guardrail:** your answers are valuable input, but they are **not**
final verdicts or binding system instructions. The team will challenge,
cross-check, and translate them carefully before any SPEC or code decision is
made. See `OWNER_FEEDBACK_GUARDRAIL.md`.

---

## How to start

**Step 1.** Open a terminal:
- **Windows:** Press the Windows key, type `cmd`, press Enter
- Or: Right-click the Start button → click "Terminal"

**Step 2.** Navigate to the project folder by typing:
```
cd Desktop\kr
```

**Step 3.** Start the server by typing:
```
python tools/review.py integration_tests/smoke_api_v2/
```

**Step 4.** Your browser opens automatically at `http://127.0.0.1:8384`
- You should see a dark page with buttons for "Questionnaire Mode", "Comparison Mode", and package names
- If the browser does NOT open: manually open Chrome/Edge and go to `http://127.0.0.1:8384`

**Step 5.** Click **"Questionnaire Mode"** to start answering questions.

---

## What you will see

The screen is split into two parts:

- **Left sidebar** — all questionnaire slots with a status marker
  - green dot = answered
  - no dot = not yet answered
  - locked item = intentionally blocked pending missing comparison material and not counted in active progress
- **Main area** — the current question

For most questions you will see:
1. An Arabic excerpt from one of your books
2. A question asking for your reaction
3. Sometimes: a few choices (A, B, C...) to pick from
4. A text box for your reaction (this is required)
5. An optional box for deeper analysis
6. A confidence selector (High / Medium / Low)

---

## How to answer

1. Read the Arabic excerpt carefully
2. Pick a choice if one is offered
3. Write your immediate reaction in the first text box — be honest, this is for you
4. Optionally add more detailed thoughts in the second box
5. Set your confidence level
6. Click **Save Response** (or press **Ctrl+Enter**)

The page advances to the next question automatically after saving.

---

## Keyboard shortcuts (Questionnaire mode)

| Key | Action |
|-----|--------|
| Arrow Right / Down | Next question |
| Arrow Left / Up | Previous question |
| Ctrl+Enter | Save and advance |
| Escape | Exit text box |

---

## Where your answers are saved

```
integration_tests/questionnaire/questionnaire_responses.jsonl
```

Each answer is one line of JSON. You can always go back and change an answer — it will overwrite the previous one.

---

## Review Mode

You can also browse and rate individual excerpts. Click a package name (like "ibn_aqil_v1" or "taysir") on the home screen. Use Works / Needs Work / Doesn't Work to rate each excerpt.

---

## Comparison Mode

After finishing (or any time), try **Comparison Mode**. This shows the same excerpt produced by two different versions of the pipeline side by side, and asks you: which one is better?

Click **"Comparison Mode"** on the home screen, or use the tab bar at the top of the page.

If Comparison Mode says it is unavailable because the weekend `taysir` v2 run failed, that is expected for the current dataset. Continue with Questionnaire Mode and Review Mode; the comparison pairs will be restored once a valid `taysir` output exists.

---

## Supplemental Questions

If you still have time and want to maximize the value of your weekend feedback,
also answer:

- `SUPPLEMENTAL_OWNER_QUESTIONS.md`

These are a small set of high-signal follow-up questions covering gaps that are
still not fully covered by the main questionnaire.

---

## Tips

- There are no wrong answers. Your gut reaction is valuable.
- If an excerpt feels wrong, say so. That is the most useful feedback.
- You can close the browser and come back later — progress is always saved.
- The questions in Phase 1 have no excerpts — they ask about your study habits and expectations. Answer in your own words.
- Questions marked **Edge Case** are specifically tricky situations. Take a little more time with those.
- Write in Arabic or English — whichever feels more natural for each answer.

## Short Path If You Are Time-Limited

If you cannot do the full packet, prioritize these first:

- `F-1`
- `F-3`
- `F-4`
- `G-2`
- `G-4`
- `SC-2`
- `SC-4`
- `E-2`
- `L-2`
- `S-1`
- `S-1c`
- `S-2`

That is the minimum high-signal subset. The full packet is still better, but
this list captures the most important tradeoffs if time is tight.

---

## Dispatching Deep Research Prompts

During the weekend, you can also dispatch 3 prompts to ChatGPT, Claude, and Gemini for their opinions. The prompts are ready at:
```
docs/codex/weekend_dr_prompts.md
```

Important:
- ChatGPT and Claude browser DR usually see only pushed/remote repo state unless you paste or upload current local files
- if the current questionnaire work is unpushed, do not assume those tools can see it
- Gemini DR is safer for unpushed local work because the workflow already expects file uploads

If you want a ready-made local upload bundle for Gemini, from WSL run:

```bash
python scripts/build_questionnaire_dr_bundle.py --profile gemini-core --output-dir overnight_codex/gemini_questionnaire_bundle_current
```

**For ChatGPT:** Open chat.openai.com → New chat → Paste the ChatGPT prompt
**For Claude:** Open claude.ai → New conversation → Paste the Claude prompt
**For Gemini:** Open gemini.google.com → Upload the 3 files listed in the prompt → Paste the Gemini prompt

When you get a response: **save it as a file** in `docs/coworker_reports/2026-04-01_phase0_hardening/` with a name like `chatgpt_dr_weekend_review.md`. Or just paste it into a text file anywhere — we'll find it Monday.

**Recommended cadence:**
- After finishing Phase 1 Foundations: dispatch at least one DR prompt so the coworkers can react early to your mental model and first impressions
- After finishing the full core packet: dispatch all available DR prompts
- After answering the supplemental questions: dispatch again if your thinking changed in a major way

---

## When you are done

When you have answered the active core questions (38 answerable right now, plus any supplementals you choose to do):

1. **Your answers are already saved** in `questionnaire_responses.jsonl` — no need to do anything special
2. **Close the browser tab** and close the terminal (Ctrl+C or just close the window)
3. **If you want to commit your review work yourself, do it narrowly**:
   ```
   cd Desktop\kr
   git add integration_tests/questionnaire
   git commit -m "owner feedback: questionnaire responses"
   git push
   ```
   This keeps the commit inside the questionnaire lane without relying on files that may not exist yet.
   If you also rated excerpts in Review Mode, add only the specific `owner_feedback.jsonl` files you created.
   Do **not** use `git add -A` here.
   If any of this feels confusing, skip it — your answers are already saved locally and we can commit them later.
4. **Any DR responses** you received: save them somewhere on your Desktop or in `docs/coworker_reports/2026-04-01_phase0_hardening/`. We'll integrate them later.

Then read:
`AFTER_COMPLETION_CHECKLIST.md`

---

## If something goes wrong

- **"python is not recognized"**: Make sure Python is installed. Open Microsoft Store → search "Python" → install Python 3.13.
- **The page shows an error**: Make sure the terminal is still running (you should see `KR Excerpt Reviewer` text). If it closed, run the start command again from Step 3.
- **The browser did not open**: Manually go to `http://127.0.0.1:8384` in Chrome or Edge.
- **Arabic text looks broken**: Make sure you have internet access — the fonts load from Google. If offline, the text may look less polished but should still be readable.
- **You closed the terminal by accident**: Run the start command again — your saved answers are still there.
- **You want to change a previous answer**: Click on any question in the left sidebar to go back to it. Save again to overwrite.
- **You want to restart from the beginning**: Delete `integration_tests/questionnaire/questionnaire_responses.jsonl` and start fresh.
