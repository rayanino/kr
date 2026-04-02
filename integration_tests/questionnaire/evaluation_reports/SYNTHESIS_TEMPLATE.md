# Questionnaire Synthesis Template

- Date:
- Synthesizer:
- Owner response set:
- Access mode of source reviews:
- Missing coworkers / degraded capacity:

## Inputs Collected

List every report used:

- 

## Summary Judgment

- Is the response set strong enough to translate now?
- What remains blocked?
- Which areas need owner follow-up?

## Category Ledger

### CONFIRMED

For each item:

- Interaction ID:
- Short answer summary:
- Why it survived challenge:
- Supporting reviewers:
- Translation target:
- Bounded implementation note:

### CHALLENGED

For each item:

- Interaction ID:
- Owner answer summary:
- Why challenged:
- Which reviewers challenged it:
- What evidence they used:
- Best narrowed interpretation if the literal answer is unsafe:
- Does this require owner follow-up: yes/no

### CONTRADICTION

For each item:

- Interaction IDs in tension:
- Nature of contradiction:
- Does `S-1` / `S-1b` / `S-1c` resolve it:
- If not, exact follow-up needed:

### INFEASIBLE

For each item:

- Interaction ID:
- Literal owner preference:
- Why infeasible:
- Closest safe alternative:
- Owner follow-up needed: yes/no

### LOCAL_PREFERENCE

For each item:

- Interaction ID:
- Owner preference summary:
- Why it should not become a global default:
- Safest scope (setting / display option / local workflow only):
- What was explicitly kept out of canonical translation:

### DEEPER_NEED

For each item:

- Interaction ID:
- Literal owner answer:
- Why the literal wording is not the real requirement:
- Suspected deeper pain / need:
- Candidate bounded interpretations:
- Did the rewritten need survive independent challenge: yes/no
- Follow-up needed: yes/no

### MISSING

For each item:

- Missing theme:
- Which reviewer surfaced it:
- Is it already covered by supplementals:
- If not, should a follow-up question be asked:

### PENDING_SOURCE

For each item:

- Interaction ID:
- Missing source artifact:
- What unblocks it:
- Should it be ignored for current synthesis or carried forward:

## Translation Decisions

Only include items that actually survive challenge.

For each translated item:

- Interaction ID:
- Final interpreted rule:
- Resolution layer: boundary / display / workflow
- SPEC / prompt / UI target:
- If boundary: why display/workflow was insufficient:
- What was intentionally NOT translated:
- Residual risk:

## Owner Follow-Up Packet Needed?

- yes / no

If yes, list only the narrowest necessary follow-ups:

- 

## Things Explicitly Rejected

List any literal owner answers that were intentionally not adopted.

- 

## Final Guardrail Check

State explicitly:

- No owner answer was translated directly into implementation without critical review.
- No remote-only DR report was treated as current-local review unless the files were actually pushed or provided.
- Scholarly invariants were not traded away merely because a preference was strongly stated.
- Owner confidence was treated as metadata, not proof.
