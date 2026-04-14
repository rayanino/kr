# Gemini DR Prompt — Intake Methodology

```text
You are doing deep research for the KR source-engine intake methodology.

Context:
- The source engine handles uploaded Islamic library sources before normalization.
- The spec is being redesigned from first principles.
- Any old implementation or prior pipeline is reference-only and non-authoritative.
- Focus on intake analysis, not downstream extraction or synthesis.

Goal:
Define a robust intake methodology for uploaded sources so the system can decide what a file actually is before normalization.

Specifically answer:
1. How should the system determine exact work identity?
2. How should it determine edition, volume, part, chunk, or partial-upload status?
3. How should it decide whether an upload is complete, incomplete, mixed, duplicated, or stitched from multiple sources?
4. What are the strongest corruption signs to check before normalization?
5. What should a specialized intake-analysis agent team verify, and in what order?
6. What acceptance criteria or stop/go gates should exist before a source is allowed into normalization?

Requirements for your answer:
- Give concrete recommendations, not general principles.
- For each recommendation, state the failure mode it prevents.
- For each gate, provide acceptance-criteria guidance.
- Include a practical checklist for the intake-analysis agent team.
- Distinguish evidence that is sufficient, suggestive, or insufficient.
- Do not assume the old implementation is correct.

Return:
- intake methodology
- evidence hierarchy
- corruption indicators
- specialized agent-team checks
- acceptance criteria and stop/go gates
- open questions the source spec must answer
```
