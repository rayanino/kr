# How to Start

## One-Time Setup (5 minutes)

In your Claude Chat KR project settings:

1. **Custom Instructions:** Copy everything below the `---` line from `reference/PROJECT_INSTRUCTIONS.md` into the project's custom instructions field.

2. **Project Knowledge Files:** Add exactly three files:
   - `STATUS.md`
   - `reference/DEEP_REASONING_PROTOCOL.md`
   - `reference/kr_decisions.md`

## Every Session (2 minutes + answering questions)

**Start a new conversation** (never continue old ones). Send:

```
Continue the project.
```

Attach the files listed in STATUS.md under "Files to Attach." If it says to run the VISION extraction script first:

```
cd /path/to/kr
python3 scripts/extract_vision_sections.py [sections] > /tmp/vision_excerpt.md
```

Then attach `/tmp/vision_excerpt.md` instead of the full VISION.md.

## After Each Session (5 minutes)

1. Save Claude's deliverables to the repo at the paths it specifies
2. Replace `STATUS.md` with Claude's updated version
3. Append new decisions to `reference/kr_decisions.md`
4. Add the session log entry to `reference/SESSION_LOG.md`
5. `git add -A && git commit -m "descriptive message"`
6. Update the 3 project knowledge files in Claude Chat settings (new STATUS.md and kr_decisions.md; protocol only changes rarely)

## If You Disagree With a Decision

Add your concern to STATUS.md under a new "Owner Feedback" section. The next session will read it and either explain the reasoning or revise.
