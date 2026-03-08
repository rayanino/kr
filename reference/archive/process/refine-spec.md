Execute one refinement cycle on an engine SPEC, following SPEC_REFINEMENT.md precisely.

Engine: $ARGUMENTS (e.g., "source" or "normalization")

This command executes ALL 9 steps of the refinement cycle in order. Do not skip steps.

## Step 1: Cold Read
Read `engines/$ARGUMENTS/SPEC.md` from top to bottom. Write down every ambiguity, gap, and confusion.

## Step 2: Threat Analysis  
Read `KNOWLEDGE_INTEGRITY.md`. For each of the 7 threats, check: does this SPEC explicitly address it?

## Step 3: Example Audit
For each behavioral rule in §4: is there a concrete input/output example with real Arabic text?
Count: rules with examples vs rules without.

## Step 4: Technology Review
For each processing step: is the tool named? Is it still the best? Search the web for alternatives.
Minimum 3 web searches. Update `reference/RESOURCES.md` with findings.

## Step 5: Cross-SPEC Boundary Verification
Read upstream §3 and downstream §2. Run: `python3 scripts/verify_metadata_flow.py --boundary <upstream> <downstream>`

## Step 6: Scholarly Value Check
Read `reference/ENTRY_EXAMPLE.md` and `reference/USER_SCENARIOS.md`. Does this engine contribute to the target entry quality?

## Step 7: Self-Review (Two Rounds)
Fix all defects found. Re-read the fixed SPEC. Run `/challenge` mentally.

## Step 8: Research Round 2
Search for state-of-the-art in this engine's domain. Minimum 3 more web searches.

## Step 9: Commit and Document
Commit with: "Refine [engine] SPEC: [N defects found, N fixed, research conducted]"
Update engine's CLAUDE.md with refinement status.

## Output: Defect Ledger

Before fixing, produce a numbered ledger:

```
### SPEC Refinement Defect Ledger: [Engine] — Cycle [N]

**Total defects found:** [N]
**By category:** [N ambiguities, N missing examples, N missing threats, N technology gaps, N boundary mismatches, N scholarly value gaps]

1. [STEP-N] [SEVERITY: HIGH/MEDIUM/LOW] §[section]:
   Quote: "[exact text]"
   Problem: [what's wrong]
   Fix: [specific correction]

2. ...
```

A refinement cycle that finds 0 defects is suspicious — re-read more carefully.
