---
name: kr-integrity
description: Audits a KR engine SPEC for technical defects that domain review cannot catch. Activate after comment resolution is complete, when asked to audit a SPEC, or when verifying implementation-readiness. Checks against knowledge corruption threats, ambiguous rules, missing error paths, and silent failure patterns.
---

# KR Integrity — تدقيق سلامة المواصفات

You are auditing a KR engine SPEC for technical defects the owner could not catch during domain review. The owner caught domain issues — wrong author attribution logic, missing scholarly conventions, incorrect metadata fields. You catch engineering issues — ambiguous rules that would produce two valid implementations, error paths with no recovery defined, silent failure patterns where data gets corrupted without any alarm.

This audit is the quality gate between "all owner comments resolved" and "SPEC is implementation-ready." After this pass, the claim is: Claude Code can build from this SPEC with zero clarifying questions. That claim needs to be true.

---

## When to Run

After kr-spec-review has resolved all owner comments and the core SPEC is updated. Before moving to Step 2 (RESEARCH). This is the last check on the SPEC before assumptions get tested and the engine gets built.

Run the audit in chunks to avoid context degradation:
- Chat 1: §1-§3 (Purpose, Input Contract, Output Contract)
- Chat 2: §4.A (Core Processing — usually the longest section)
- Chat 3: §5-§7 (Validation, Consensus, Errors)
- Chat 4: §8-§10 (Configuration, Implementation State, Tests)

For smaller SPECs (after core extraction), two chats may suffice.

---

## The Seven Lenses

Apply each lens to every section being audited. Not every lens produces findings in every section — but skipping a lens means missing the defect it would have caught.

### Lens 1: Zero Ambiguity

For every behavioral rule, ask: could two competent developers read this and build different things?

Watch for: "the engine evaluates" (how?), "appropriate threshold" (what number?), "relevant metadata" (which fields?), "handles gracefully" (what specific behavior?). Every vague term must be replaced with a precise one, or flagged as a defect.

The test: can you write a function signature and 5-15 lines of pseudocode from this rule alone? If not, the rule is ambiguous.

### Lens 2: Knowledge Corruption Paths

Read `KNOWLEDGE_INTEGRITY.md`. For each of the 7 threats (silent text corruption, attribution error, taxonomic misplacement, context loss, synthesis hallucination, metadata poisoning, duplication), check: does this SPEC section have a mechanism that prevents this threat? If the section doesn't interact with a threat, note that and move on. If it does interact but has no prevention mechanism, that's a defect.

### Lens 3: Silent Failure Patterns

Read `SILENT_FAILURES.md`. For each of the 7 patterns, check: could this SPEC section produce output that looks correct but isn't? Pay special attention to: LLM calls that return plausible but wrong answers (no validation), metadata fields that default to a value instead of failing (masking missing data), error recovery that drops data silently.

### Lens 4: Error Path Completeness

For every error code defined in §7: is it reachable? Is there a code path in §4 that would trigger it? For every decision point in §4: what happens on failure? Is there an error code, a recovery action, and a logging requirement? Unreachable error codes and unhandled failure paths are both defects.

### Lens 5: Contract Consistency

Does §3 (Output Contract) actually match what §4 (Processing) produces? Does every field in the output schema get populated by a specific processing rule? Are there fields in §4's processing that never appear in §3? Does the output contract match the downstream engine's input contract (§2 of the next engine)?

### Lens 6: Assumption Identification

Find every place the SPEC makes an assumption that hasn't been empirically tested. Common assumptions: "the LLM can reliably do X," "this threshold separates good from bad," "this data structure carries enough information for downstream." Each assumption becomes a test case for Step 2 (RESEARCH). Mark them explicitly:

```
[ASSUMPTION — NEEDS STEP 2 TESTING] The LLM can identify the author
from the first 2000 characters of Arabic text with >85% accuracy.
```

### Lens 7: Implementer's Reading

Read the SPEC as if you are Claude Code, about to build. For each rule:
- Do you know what input you receive? (exact types, not "the metadata")
- Do you know what output you produce? (exact types, exact fields)
- Do you know the order of operations? (is step 3 before or after step 4?)
- Do you know what to do when something goes wrong? (exact error handling)

Any "I'd have to guess" moment is a defect.

---

## Output Format

For each section audited, produce a defect ledger:

```
## Integrity Audit — [Engine] §[sections]

### Defects Found: [N]

**Defect 1** [Lens: Zero Ambiguity] §4.A.3
Quote: "The engine evaluates relevance using content analysis"
Problem: "Content analysis" has no defined method. An implementer
would have to invent one.
Fix: Replace with: "The engine sends the first 2000 characters
to the LLM with the prompt in §4.A.3.1 and classifies the
response as relevant/partially_relevant/not_relevant."
Severity: HIGH — would cause implementation divergence

**Defect 2** [Lens: Assumption] §4.A.5
Quote: "Author identification uses multi-model consensus at ≥0.80"
Problem: No evidence that LLMs can identify classical Arabic
authors at this accuracy. This needs empirical testing.
Fix: Mark as [ASSUMPTION — NEEDS STEP 2 TESTING]
Severity: MEDIUM — design may need to change based on results

### Assumptions Needing Step 2 Testing: [N]
[List each with what to test and what changes if it fails]

### Summary
- HIGH defects: [N] — would cause wrong implementation
- MEDIUM defects: [N] — missing detail or untested assumption
- LOW defects: [N] — minor clarity improvements
- Assumptions for Step 2: [N]
```

---

## Quality Standard

A superficial audit finds only formatting issues and typos. A real audit finds at least one defect per section that would cause Claude Code to build the wrong thing. If you find zero HIGH-severity defects in a 200+ line core SPEC, you haven't looked hard enough — read it again with Lens 7 (Implementer's Reading).

After all defects are fixed and assumptions are marked, the SPEC is ready for Step 2.
