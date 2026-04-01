# START HERE — Owner Questionnaire Guide

## What is this?

This is your personal evaluation session for the KR library. You will read excerpts from your books and tell us what you think about them. Your answers shape how the pipeline works — this is the most important feedback you can give.

There are **40 questions** split into 4 phases. You do not need to answer all of them in one sitting. Your progress is saved automatically after each question.

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

- **Left sidebar** — all 40 questions with a coloured dot showing which ones you have answered (green dot = answered, no dot = not yet answered)
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

You can also browse and rate individual excerpts. Click a package name (like "ibn_aqil_v1" or "taysir") on the home screen. Use Accept / Needs Work / Reject to rate each excerpt.

---

## Comparison Mode

After finishing (or any time), try **Comparison Mode**. This shows the same excerpt produced by two different versions of the pipeline side by side, and asks you: which one is better?

Click **"Comparison Mode"** on the home screen, or use the tab bar at the top of the page.

If Comparison Mode says it is unavailable because the weekend `taysir` v2 run failed, that is expected for the current dataset. Continue with Questionnaire Mode and Review Mode; the comparison pairs will be restored once a valid `taysir` output exists.

---

## Tips

- There are no wrong answers. Your gut reaction is valuable.
- If an excerpt feels wrong, say so. That is the most useful feedback.
- You can close the browser and come back later — progress is always saved.
- The questions in Phase 1 have no excerpts — they ask about your study habits and expectations. Answer in your own words.
- Questions marked **Edge Case** are specifically tricky situations. Take a little more time with those.
- Write in Arabic or English — whichever feels more natural for each answer.

---

## Dispatching Deep Research Prompts

During the weekend, you can also dispatch 3 prompts to ChatGPT, Claude, and Gemini for their opinions. The prompts are ready at:
```
docs/codex/weekend_dr_prompts.md
```

**For ChatGPT:** Open chat.openai.com → New chat → Paste the ChatGPT prompt
**For Claude:** Open claude.ai → New conversation → Paste the Claude prompt
**For Gemini:** Open gemini.google.com → Upload the 3 files listed in the prompt → Paste the Gemini prompt

When you get a response: **save it as a file** in `docs/coworker_reports/2026-04-01_phase0_hardening/` with a name like `chatgpt_dr_weekend_review.md`. Or just paste it into a text file anywhere — we'll find it Monday.

---

## When you are done

When you have answered all 40 questions (or as many as you can):

1. **Your answers are already saved** in `questionnaire_responses.jsonl` — no need to do anything special
2. **Close the browser tab** and close the terminal (Ctrl+C or just close the window)
3. **Save your work to the repository** by opening a terminal and typing:
   ```
   cd Desktop\kr
   git add -A
   git commit -m "owner feedback: questionnaire responses + excerpt reviews"
   git push
   ```
   If this doesn't work, don't worry — your answers are saved locally and we'll commit them Monday.
4. **Any DR responses** you received: save them somewhere on your Desktop. We'll integrate them Monday.

---

## If something goes wrong

- **"python is not recognized"**: Make sure Python is installed. Open Microsoft Store → search "Python" → install Python 3.13.
- **The page shows an error**: Make sure the terminal is still running (you should see `KR Excerpt Reviewer` text). If it closed, run the start command again from Step 3.
- **The browser did not open**: Manually go to `http://127.0.0.1:8384` in Chrome or Edge.
- **Arabic text looks broken**: Make sure you have internet access — the fonts load from Google. If offline, the text may look less polished but should still be readable.
- **You closed the terminal by accident**: Run the start command again — your saved answers are still there.
- **You want to change a previous answer**: Click on any question in the left sidebar to go back to it. Save again to overwrite.
- **You want to restart from the beginning**: Delete `integration_tests/questionnaire/questionnaire_responses.jsonl` and start fresh.
