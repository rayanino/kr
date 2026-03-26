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

## Implementation Patterns Per Threat

### T-1 Defense: Text Integrity Verification
```python
# After ANY text transformation, verify:
assert len([c for c in output if '\u0600' <= c <= '\u06FF']) >= \
       len([c for c in input if '\u0600' <= c <= '\u06FF']), \
       "Arabic letter count decreased — possible corruption"

# Diacritic preservation check:
DIACRITICS = set(range(0x064B, 0x0654)) | {0x0670}
input_diacritics = sum(1 for c in input if ord(c) in DIACRITICS)
output_diacritics = sum(1 for c in output if ord(c) in DIACRITICS)
assert output_diacritics == input_diacritics, "Diacritic count changed"
```
**Test pattern**: For every function that touches Arabic text, write a test with fully diacritized input and verify byte-identical output where no transformation is intended.

### T-2 Defense: Attribution Verification
```python
# Multi-model consensus for attribution (D-041):
results = [model.classify(text) for model in consensus_models]
if all(r.author == results[0].author for r in results):
    confidence = min(r.confidence for r in results)
else:
    confidence = 0.0  # Disagreement → human gate
    flag_for_review(reason="Model disagreement on attribution")
```
**Test pattern**: Create test cases with known authors (from test fixtures) and verify the pipeline attributes correctly. Include adversarial cases: same-name scholars, unknown authors, multi-author compilations.

### T-3 Defense: Taxonomy Placement Validation
**Test pattern**: Place a well-known text (e.g., صحيح البخاري) and verify it lands under hadith, not fiqh. Place a comparative fiqh text and verify it doesn't land under a single school. Create edge cases: a text that discusses both nahw and fiqh.

### T-4 Defense: Self-Containment Check
**Test pattern**: For every excerpt, verify a domain expert could understand it WITHOUT reading the surrounding text. If the excerpt starts with "وكذلك" (and likewise) or references "المذكور أعلاه" (mentioned above) without context, it fails self-containment.

### T-5 Defense: Grounding Verification
**Test pattern**: For every synthesis output, verify every claim has a grounding_type tag. Verify every source_grounded claim maps to a real excerpt ID. Create a test with a fabricated excerpt ID and verify the system rejects it.

### T-6 Defense: Metadata Integrity
```python
# D-023: Verify no metadata fields are dropped
input_fields = set(input_metadata.model_fields_set)
output_fields = set(output_metadata.model_fields_set)
assert input_fields.issubset(output_fields), \
    f"Metadata fields lost: {input_fields - output_fields}"
```
**Test pattern**: Pass metadata through every engine boundary and verify no fields are dropped. Include edge cases: empty optional fields, very long values, Arabic text in metadata.

### T-7 Defense: Deduplication Check
**Test pattern**: Process the same book twice and verify the system detects the duplicate. Process two different editions of the same work and verify they are linked, not duplicated.

## Rules

- Never say "no risks found" without checking every threat.
- If you're unsure whether a threat applies, assume it does.
- Always recommend the conservative option — false alarms are cheap, undetected errors are catastrophic.
- Reference specific KNOWLEDGE_INTEGRITY.md sections in your recommendations.
- For each threat, suggest at least one CONCRETE test case, not just a review checkbox.
