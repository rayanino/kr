---
name: spec-examples
description: Generate concrete input/output examples for SPEC behavioral rules. Use when refining SPECs, when a rule lacks a testable example, or when Claude Code reports a SPEC-AMBIGUITY. Every example uses real Arabic text, not placeholders.
---

# SPEC Example Generation

Every behavioral rule in a SPEC's §4 must have at least one concrete, testable example. An example-less rule is an ambiguous rule.

## Example Structure

Each example must contain ALL of these:

```markdown
**Example ([subsection] — [rule description]):**

Input:
```json
{
  // Complete input data with all fields
  // Real Arabic text, not "sample text" or transliteration
  // Realistic values, not toy data
}
```

Processing:
1. [First thing the engine does with this input]
2. [Second thing — reference specific §4 rules]
3. [Decision points — what could go differently?]

Output:
```json
{
  // Complete output data with all fields
  // Show how input was transformed
  // Include metadata additions
}
```

Why this tests the rule:
[Explain what this example verifies — what would be wrong if the rule were implemented differently?]
```

## Quality Criteria for Examples

### Use Real Arabic Text
- Book titles: use actual titles like شرح ابن عقيل على ألفية ابن مالك
- Author names: use actual scholars like ابن قدامة المقدسي
- Text passages: use actual scholarly text, even if brief
- Science names: use actual sciences like أصول الفقه, النحو, التجويد

### Cover Edge Cases
For each rule, generate examples that test:
- The normal/happy path
- At least one edge case (what happens when a field is missing? when input is ambiguous? when two rules conflict?)
- The error path (what triggers the specified error code?)

### Be Self-Contained
Each example must be understandable without reading the rest of the SPEC. Include enough context that someone seeing only the example could understand the rule.

### Match the Schema
Input examples must match §2 (Input Contract) exactly.
Output examples must match §3 (Output Contract) exactly.
If the schema has changed since the example was written, the example is stale and must be updated.

## Per-Engine Example Priorities

### Source Engine
Priority examples needed:
- Shamela directory → source_id generation → metadata.json
- Manual photo upload → human gate for missing metadata
- Duplicate source detection → SRC_DUPLICATE_SOURCE
- Multi-layer text detection → layer→author mapping
- Trustworthiness scoring → verified vs flagged

### Normalization Engine  
Priority examples needed:
- Shamela HTML → normalized content.jsonl with heading hierarchy
- Multi-layer separation → matn vs sharh blocks
- Footnote marker conversion → universal format
- OCR text → text fidelity score calculation

### Passaging/Atomization/Excerpting
Priority examples needed:
- Passage boundary detection at a semantic break vs mid-sentence
- Atom type classification (structural type + scholarly function)
- Excerpt self-containment: one that passes, one that fails
- Three-phase excerpting pipeline: boundary → extraction → assembly

### Taxonomy/Synthesis
Priority examples needed:
- Two-stage placement: broad classification → leaf selection
- Entry generation from excerpts: show the grounding_type for each claim
- Temporal narrative construction: how metadata becomes narrative

## Anti-patterns

- **Toy data:** `{"title": "test book", "author": "test author"}` — NEVER. Use real data.
- **English-only:** Examples must contain Arabic where the real data would contain Arabic.
- **Happy path only:** Every subsection needs at least one error/edge case example.
- **Schema mismatch:** Example fields don't match the actual schema — update the example.
- **Stale examples:** Example references a field that was renamed or removed — update it.
