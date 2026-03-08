Run the Three Challenges against the current session's work.

This is MANDATORY before every commit of substantial work. It is not optional.

Steps:
1. Identify the deliverable(s) from this session (code files, SPEC sections, design decisions).

3. **Challenge 1: The Hostile Implementer**
   - For each deliverable, find at least ONE sentence/line with two valid interpretations.
   - For code: identify at least ONE input that could produce wrong behavior.
   - Report what you found and how you fixed it.

4. **Challenge 2: The Skeptical Scholar**
   - For each deliverable, find at least ONE thing a scholar might distrust.
   - Check: is every claim traceable? Is every attribution verified? Could output mislead?
   - Report what you found and how you fixed it.

5. **Challenge 3: The Technology Maximalist**
   - For each deliverable, identify at least ONE place where an existing tool could replace custom code.
   - Check: did you search RESOURCES.md? Did you web search for alternatives?
   - Report what you found and whether you changed anything.

6. **Knowledge Integrity Check**
   - Trace through the 7 threats in KNOWLEDGE_INTEGRITY.md.
   - For each threat that applies: verify the mitigation is in place.
   - Report any gaps.

Output format:
```
## Three Challenges — Session [date]

### Challenge 1: Hostile Implementer
Found: [specific issue]
Fixed: [what was changed]

### Challenge 2: Skeptical Scholar
Found: [specific issue]
Fixed: [what was changed]

### Challenge 3: Technology Maximalist
Found: [specific issue]
Action: [what was changed or why no change]

### Knowledge Integrity
Applicable threats: [list]
All mitigations in place: YES/NO
Gaps: [if any]
```

If you cannot find at least one issue per challenge, you are not looking hard enough. Re-read the protocol and try again.
