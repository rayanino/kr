# Owner Feedback Guardrail

## Non-Negotiable Interpretation Rule

The owner's questionnaire answers are **high-value signal** and **zero-authority implementation commands**.

That means:

- They are feedback, not verdicts.
- They are preferences, not final rules.
- They are suggestions, not binding conclusions.
- They are stakeholder expectations, not validated requirements.
- They may reveal real needs, but they may also be mistaken, contradictory, locally appealing but globally harmful, technically infeasible, or scholastically unsafe.

## Why This Rule Exists

The owner has explicitly said he has minimum Islamic knowledge and does **not**
want his answers treated as final truth.

So the engineering team must never read:

- "the owner said X"

as meaning:

- "therefore the system must do X"

That would be a category error.

## Required Handling Of Owner Answers

Every owner answer must pass through critical evaluation before it becomes any
of the following:

- a SPEC rule
- a prompt rule
- a code change
- a default UI behavior
- a calibration threshold
- a permanent product decision

Accepted owner signal must become a **bounded rule**, not an absolute law.

That means every translated rule should have:

- scope
- non-goals
- fallback behavior
- verification method
- reversibility / rollback path

## Scholarly Invariants Outrank Preference

If a literal owner preference conflicts with scholarly integrity, attribution
integrity, disagreement preservation, or other knowledge-safety invariants, the
invariant wins.

The team must preserve the owner's underlying intent where possible, but never
by violating the scholarly constraints that keep the system honest.

## Failure Modes We Must Assume

Any owner answer may be:

- **scholastically wrong**
- **internally contradictory**
- **too vague to implement**
- **too rigid to generalize**
- **too expensive to support**
- **good for one excerpt but harmful across the corpus**
- **good for short-term comfort but bad for long-term study quality**
- **actually pointing at a deeper need than the literal answer states**

If any of those are true, the team must challenge, reinterpret, narrow, defer,
or reject the literal answer while still trying to preserve the owner's actual
intent.

## Evidence Beats Confidence

The owner's confidence is useful metadata, not proof.

High confidence does not make an answer correct.
Low confidence does not make an answer useless.

Confidence helps us judge where interpretation is fragile, but it never replaces:

- reviewer evidence
- feasibility analysis
- scholarly-risk analysis
- corpus-wide validation

## Correct Team Posture

The team's job is **not** to obey the owner's literal wording.

The team's job is to:

1. understand what the owner is reacting to
2. identify the real need underneath the reaction
3. test that need against scholarship, feasibility, scale, and system integrity
4. convert only the defensible part into product/spec behavior
5. bring unresolved conflicts back as concrete follow-up questions

## Separation Of Duties

No single person should:

1. collect the owner's feedback
2. decide what it "really means"
3. approve the translation
4. ship the resulting rule

without independent challenge.

Owner feedback translation must pass through a multi-reviewer loop so it cannot
quietly become a self-confirming interpretation.

## Hard Rule

No single questionnaire answer is ever self-justifying.

No answer becomes product truth merely because the owner said it.

No answer bypasses:

- coworker critique
- contradiction checks
- feasibility review
- scholarship/integrity review
- long-run system judgment

## Translation Rule

The only safe translation is:

> owner answer -> evaluated signal -> challenged/refined interpretation -> bounded rule

Never:

> owner answer -> direct implementation

## If There Is Any Doubt

Bias toward:

- slower interpretation
- stronger challenge
- narrower translation
- explicit uncertainty
- follow-up questions

Undershooting is recoverable.
Blind obedience is not.
