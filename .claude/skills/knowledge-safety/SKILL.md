---
name: knowledge-safety
description: Audit any engine output, SPEC section, or code for knowledge integrity risks. Use when implementing processing logic, writing tests, reviewing data models, or any time Arabic text or scholarly metadata is involved. Checks against the 7-threat model in KNOWLEDGE_INTEGRITY.md.
---

# Knowledge Safety Review

You are reviewing KR code or design for knowledge integrity risks. The knowledge in this library IS the user's knowledge — an error here is an error in his mind. The knowledge cannot defend itself.

## Threat Checklist

For every piece of code or design you review, check against ALL seven threats:

### T-1: Silent Text Corruption
- Does this code transform Arabic text in any way? If yes: does it preserve the exact bytes?
- Is there any encoding conversion? (UTF-8 must be maintained throughout.)
- Is there any whitespace normalization that could remove meaningful Arabic characters?
- Does the code verify text integrity against the frozen source hash after any operation?

### T-2: Attribution Error
- Does this code assign authorship, school affiliation, or dates?
- If yes: does it use multi-model consensus (not a single LLM call)?
- Does it check the scholar authority registry for verified data?
- Does it handle multi-layer texts (matn/sharh/hashiyah) and attribute each layer to its correct author?
- Are confidence scores attached to every attribution decision?

### T-3: Taxonomic Misplacement
- Does this code place content under taxonomy nodes?
- If yes: does it use the two-stage placement algorithm?
- Does it trigger human gate for ambiguous placements?
- Is there a mechanism to detect and flag suspicious placements?

### T-4: Context Loss
- Does this code extract or split text?
- If yes: does it verify self-containment of each resulting unit?
- Does it add self_containment_context where needed?
- Would the extracted text be understandable to a scholar without access to the surrounding text?

### T-5: Synthesis Hallucination
- Does this code generate or compose text?
- If yes: is every claim tagged with grounding_type?
- Can every source_grounded claim be traced to a specific excerpt ID?
- Are analytical contributions explicitly marked?

### T-6: Metadata Poisoning
- Does this code set or modify metadata?
- If yes: are critical fields (author, school, science) validated against known sources?
- Does it use consensus for critical metadata decisions?
- Would incorrect metadata here propagate downstream?

### T-7: Duplication and Contradiction
- Does this code add content to the library?
- If yes: does it check for existing duplicates?
- Does it detect contradictions with existing content?

## Output Format

For each threat that applies to the code/design under review:

```
THREAT T-N: [threat name]
APPLIES: YES/NO
RISK LEVEL: HIGH/MEDIUM/LOW
CURRENT MITIGATION: [what's in place]
GAP: [what's missing]
RECOMMENDATION: [specific fix]
```

## Rules

- Never say "no risks found" without checking every threat.
- If you're unsure whether a threat applies, assume it does.
- Always recommend the conservative option — false alarms are cheap, undetected errors are catastrophic.
- Reference specific KNOWLEDGE_INTEGRITY.md sections in your recommendations.
