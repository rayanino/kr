# START HERE — Owner Questionnaire Guide

## What is this?

This is your personal evaluation session for the KR library. You will read excerpts from your books and tell us what you think about them. Your answers shape how the pipeline works — this is the most important feedback you can give.

There are **40 questions** split into 4 phases. You do not need to answer all of them in one sitting. Your progress is saved automatically after each question.

---

## How to start

**Step 1.** Open a terminal and run:

```
python tools/review.py integration_tests/smoke_api
```

**Step 2.** Your browser opens automatically at `http://127.0.0.1:8384`

**Step 3.** Click **"Questionnaire Mode"** on the home screen.

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

## Comparison Mode

After finishing (or any time), you can also try **Comparison Mode**. This shows the same excerpt produced by two different versions of the pipeline side by side, and asks you: which one is better?

Click **"Comparison Mode"** on the home screen, or use the tab bar at the top of the page.

---

## Tips

- There are no wrong answers. Your gut reaction is valuable.
- If an excerpt feels wrong, say so. That is the most useful feedback.
- You can close the browser and come back later — progress is always saved.
- The questions in Phase 1 have no excerpts — they ask about your study habits and expectations. Answer in your own words.
- Questions marked **Edge Case** are specifically tricky situations. Take a little more time with those.

---

## If something goes wrong

- If the page shows an error, make sure the server is still running (the terminal should show `KR Excerpt Reviewer`).
- If you close the terminal by accident, run the start command again — your saved answers will still be there.
- If you want to restart from the beginning, delete `questionnaire_responses.jsonl` and start fresh.
