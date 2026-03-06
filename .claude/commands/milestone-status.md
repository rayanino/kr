Show detailed progress on the current milestone.

Steps:
1. Read MILESTONES.md to identify the current milestone and its tasks.
2. For each task in the current milestone:
   a. Check if the referenced files exist.
   b. Run tests if they exist.
   c. Determine status: [ ] not started, [~] in progress, [x] complete, [!] blocked.
3. Read NEXT.md for any blocked items or pending questions.
4. Calculate progress: tasks completed / total tasks.

Output:
```
Milestone: [name]
Progress: [N] / [M] tasks complete ([percentage]%)

[x] M1.1 — Data Models and Identity (tests: 12 pass, 0 fail)
[~] M1.2 — Shamela Intake Path (tests: 5 pass, 2 fail)
[ ] M1.3 — Metadata Enrichment (not started)
[ ] M1.4 — Normalization Shamela (not started)
[!] M1.5 — Integration (blocked by: M1.3, M1.4)

Blockers: [list from NEXT.md]
Next task: [what should be worked on next]
```

Also run `python3 scripts/check_compliance.py --all` for a quick compliance overview.
