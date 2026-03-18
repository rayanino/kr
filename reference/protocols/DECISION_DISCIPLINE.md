# KR Decision Discipline

**Authority:** The Architect DECIDES. Deferring decisions to the next session is laziness disguised as caution.

**Problem this solves:** In the Session 2→3 transition, the Tier 3 LLM scoping decision was flagged as "pending" for the next session to resolve. But the Architect already had all the information needed: SPEC requirements, passaging engine needs, cost/complexity tradeoffs, and the ABD reference code. Deferring meant the next session would re-read the same context and re-derive the same reasoning — wasting context window and creating a decision vacuum where CC might improvise.

---

## Rule

When a scoping decision is identified during handoff preparation:

1. **State the decision explicitly.** What exactly needs to be decided?
2. **List the options with tradeoffs.** Maximum 3 options.
3. **Make the decision with reasoning.** The Architect has the information. Decide.
4. **Write the decision into the handoff.** CC reads a decision, not an open question.
5. **Note that the owner can override.** The decision is the Architect's recommendation, not a decree.

## Anti-patterns

- "Key decision pending: X" → WRONG. Decide X.
- "Options to evaluate: A, B, C" without choosing one → WRONG. Choose one.
- "The next session should decide" → WRONG. This session decides.
- "This depends on information we don't have" → ACCEPTABLE only if genuinely true. If the information exists in the SPEC, contracts, or domain knowledge, you have it.

## Calibration

Not every choice needs deep analysis. Many scoping decisions have a clear safe default:
- "Should we build X now or stub it?" → If downstream engines don't need X for their development, stub it.
- "Full implementation or simplified version?" → If we're in build phase, simplified version that passes all SPEC requirements. Optimize in hardening.
- "This feature vs that feature?" → The one that's CORE in CORE_EXTRACTION.md.
