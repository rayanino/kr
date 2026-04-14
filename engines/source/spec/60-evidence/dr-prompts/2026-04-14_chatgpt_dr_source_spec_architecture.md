# ChatGPT DR Prompt — Source Spec Architecture

```text
You are doing deep research for the KR source-engine spec redesign.

Context:
- The source engine is in spec discovery.
- The spec is being redesigned as atomized YAML, not a monolithic prose document.
- Any archived v1 implementation is reference-only and non-authoritative.
- Do not assume the old folder structure, stage names, or control flow are correct.

Goal:
Recommend a behavior-first source-engine spec architecture and a clean stage decomposition for intake.

Focus on these boundaries:
- vision and goals
- vocabulary and terms
- pipeline stages
- contracts and schemas
- review evidence and validation artifacts

Specifically answer:
1. What should belong in each of those layers, and what should not?
2. What is the best behavior-first folder / atom layout for a source engine spec?
3. How should intake be separated from later normalization or processing stages?
4. Where should stage boundaries be hard, and where should they be soft?
5. What failure modes appear when the spec is organized around implementation instead of behavior?
6. What acceptance criteria would prove the architecture is well separated and testable?

Requirements for your answer:
- Give concrete recommendations, not generic advice.
- For every recommendation, state the failure mode it prevents.
- For every major boundary, give acceptance-criteria guidance.
- Include at least one proposed minimal spec structure.
- Call out any ambiguous areas where the spec should explicitly choose one interpretation.
- Do not treat the old implementation as authoritative.

Return:
- recommended architecture
- recommended stage decomposition
- failure modes
- acceptance criteria
- open questions that the spec still must resolve
```
