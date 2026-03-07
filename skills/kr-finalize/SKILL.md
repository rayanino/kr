---
name: kr-finalize
description: Consolidate SPEC changes and run full quality/integrity audit. Use for "finalize", "all comments done", "wrap up", "final review", or when comment resolution is complete.
---

# KR Finalize — إنهاء المواصفات

You are finalizing a KR engine SPEC after comment resolution. This is not a formatting pass. This is the equivalent of a hardening session: you consolidate all changes, audit every section against the Perfection Standard, check for knowledge integrity threats, scan for silent failure patterns, and produce the complete updated SPEC text.

The standard: when you finish, the SPEC must be implementable by Claude Code with zero clarifying questions, every rule must be testable, every error path must be defined, and no second valid reading may exist under hostile interpretation.

---

## Procedure

### Phase 1: Consolidation (gather everything)

1. **Collect all comment resolutions** from the conversation. Build a complete change manifest:

```
| # | SPEC Section | Change Type | Summary |
|---|-------------|-------------|---------|
| 1 | §4.A.2      | Modified    | Added sharh/matn layer detection |
| 2 | §7          | Added       | New error code NORM_LAYER_AMBIGUOUS |
| 3 | §2          | Modified    | Expanded manual input types |
```

2. **Check for interactions.** Do any changes conflict with each other? Does change #3 invalidate the assumption behind change #1? Read the changes as a SET, not individually.

3. **Check cross-section consistency.** If §4 processing rules changed, does §2 (input contract) still feed the right data? Does §3 (output contract) still describe what §4 produces? Does §7 (error handling) cover the new failure modes?

4. **Check cross-SPEC consistency.** If this SPEC's output changed, does the downstream engine's input contract still match? If this SPEC's input expectations changed, does the upstream engine's output still satisfy them?

### Phase 2: Full Quality Audit

Run every check below. Do not skip sections because they "look fine." The silent failures are in the sections that look fine.

#### Tier 1 — Structural Soundness

Read every section of the SPEC and check:

| # | Check | What to look for |
|---|-------|-----------------|
| 1 | Zero ambiguity | Could Claude Code implement this with zero clarifying questions? Flag any sentence where the answer is "maybe." |
| 2 | Binary sentences | Every sentence must be a binding rule OR a marked open question. Flag filler, aspirational language, or vague intentions. |
| 3 | No contradictions | Does any sentence contradict any other sentence in THIS SPEC or any other KR document you have access to? |
| 4 | No premature constraints | Does anything constrain a decision that hasn't been made yet? |
| 5 | No unbounded universals | Every "always/never/all" — is it actually guaranteed? |
| 6 | Glossary compliance | Are terms used consistently with VISION.md §2 definitions? |
| 7 | No duplication | Is any rule stated in two places? If so, one must go. |
| 8 | Accurate state | Does §9 (Implementation State) match what actually exists in the code? |
| 9 | Adversarial-proof | Read each rule as if you're a hostile implementer looking for loopholes. |

#### Tier 2 — Content Completeness

| # | Check | What to look for |
|---|-------|-----------------|
| 10 | Full input coverage | Can every legitimate input this engine receives be processed? |
| 11 | Exhaustive error handling | For every processing step: what happens when it fails? |
| 12 | Enumerated edge cases | Each edge case must have: trigger condition, response, justification. |
| 13 | Testable rules | Can every behavioral rule produce a clear pass/fail test? |
| 14 | Both-sides integration | At every boundary: what this engine expects AND what it promises. |

#### Tier 3 — Design Quality

| # | Check | What to look for |
|---|-------|-----------------|
| 15 | Best-known design | Were alternatives considered? Is this the best, with reasoning? |
| 16 | Earned complexity | Does every element justify its existence? Remove anything that doesn't. |
| 17 | Scale-graceful | Works at 1 source and 1000 sources? Limitations stated? |
| 18 | Vendor-neutral | No unjustified lock-in to specific tools or platforms? |
| 19 | Forward-compatible | Extension points identified for future capabilities? |
| 20 | Transformative ambition | At least one §4.B capability that makes impossible scholarship possible? |
| 21 | Scholarly integrity | Every knowledge product verifiable, every claim traceable? |

#### Tier 4 — Communication Quality

| # | Check | What to look for |
|---|-------|-----------------|
| 22 | Parseable structure | Consistent numbering, exact cross-references? |
| 23 | Necessary and sufficient | Would removing any sentence cause a wrong implementation? |
| 24 | Clean dependencies | External dependencies explicit and minimal? |
| 25 | Operational clarity | A new agent with no KR context can follow this document alone? |

### Phase 3: Integrity Threat Scan

For each of the 7 threats in KNOWLEDGE_INTEGRITY.md (which should be in the project knowledge), check whether this SPEC's changes increase or decrease risk:

- **T-1 Silent Text Corruption:** Do the changes affect text handling? Is the mitigation chain intact?
- **T-2 Attribution Error:** Do the changes affect who-said-what? Is consensus still required?
- **T-3 Taxonomic Misplacement:** Do the changes affect topic classification?
- **T-4 Context Loss:** Do the changes affect excerpt boundaries or self-containment?
- **T-5 Synthesis Hallucination:** Do the changes affect grounding requirements?
- **T-6 Metadata Poisoning:** Do the changes affect metadata extraction or propagation?
- **T-7 Duplication/Contradiction:** Do the changes affect deduplication or cross-source checks?

For each threat that applies: state the specific risk and verify the SPEC addresses it.

### Phase 4: Silent Failure Scan

Read through the SPEC looking for each of the 7 patterns in SILENT_FAILURES.md:

1. **Hollow Examples** — For each example: if you implemented the rule WRONG, would this example still pass?
2. **Circular Definitions** — Replace every defined term with its definition. Does content remain?
3. **Hand-Waving Tech References** — For every named technology: does it actually support Arabic? Does it do what the SPEC claims?
4. **Phantom Metadata** — At every boundary: are field names, types, and optionality identical?
5. **Untestable Rules** — Can you write a pass/fail test for every rule?
6. **Missing Error Paths** — For every processing step: what happens when it fails?
7. **Scope Creep Disguise** — Every §4.B capability: can it be implemented with ONLY this engine's inputs?

### Phase 5: The Anti-Secretary Test

Answer honestly:

1. **Did the comment resolution make the SPEC RICHER, not just CLEANER?** If the SPEC only got cleaner (fixed typos, clarified wording, removed contradictions) but didn't gain new capabilities or deeper handling of edge cases, the session was secretarial.

2. **Did any comment resolution ORIGINATE a new capability?** Not just fix what was broken — but see an opportunity the owner's comment revealed and design something new.

3. **Would a world-class Islamic scholar reading this SPEC say "I didn't know technology could do that"?** If not, the §4.B section needs work.

---

## Output Format

Produce your finalization as:

```
# Finalization Report — [Engine Name]

## Change Manifest
[Table of all changes from Phase 1]

## Audit Results

### Structural Soundness (Tier 1)
[For each criterion: PASS or DEFECT with quoted text and fix]

### Content Completeness (Tier 2)
[Same format]

### Design Quality (Tier 3)
[Same format]

### Communication Quality (Tier 4)
[Same format]

## Integrity Assessment
[For each applicable threat: risk level and SPEC coverage]

## Silent Failure Scan
[For each pattern: findings]

## Anti-Secretary Test
[Honest answers to the 3 questions]

## Complete Updated SPEC
[The full SPEC text with all changes applied — not diffs, the complete document]
```

---

## Critical Reminders

- **Produce the COMPLETE updated SPEC text.** Not diffs. Not "change X to Y." The full document with all changes applied. This is what gets committed to the repo.
- **Every defect needs a fix, not just a flag.** Don't say "§4.A.3 is ambiguous" without providing the unambiguous replacement text.
- **At least one defect must be structural or semantic.** If your audit only finds formatting issues, you didn't look hard enough. Cosmetic-only audits indicate the audit was superficial.
- **Be brutally honest in the Anti-Secretary Test.** If the session was secretarial, say so. That's feedback the owner needs.
