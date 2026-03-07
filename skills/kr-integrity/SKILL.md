---
name: kr-integrity
description: Deep audit against Perfection Standard, 7 corruption threats, 7 silent failure patterns. Use for "audit", "integrity check", "verify", "quality check", or when something feels off.
---

# KR Integrity — تدقيق السلامة

You are running a deep integrity audit on a KR artifact. This skill exists because the most dangerous errors are the ones that look correct. A SPEC section that reads fluently but would produce wrong behavior. An engine output that passes schema validation but contains a misattributed quote. A metadata field that's technically present but semantically wrong.

**The foundational axiom:** The library IS the owner's knowledge. An error in the pipeline becomes an error in his mind. The knowledge cannot defend itself.

---

## What Can Be Audited

This skill works on three types of artifacts:

1. **A SPEC** — audit the specification document for quality and completeness
2. **Engine output** — audit actual output files for correctness and integrity
3. **Pipeline state** — audit cross-engine consistency and metadata flow

The procedure adapts based on what you're auditing, but the threats and patterns always apply.

---

## Procedure for SPEC Audit

### Pass 1: Perfection Standard (25 Criteria)

Read the SPEC section by section. For EACH section, check every applicable criterion. The full Perfection Standard is in `reference/DEEP_REASONING_PROTOCOL.md` in the project knowledge. Here is the condensed checklist:

**Structural Soundness (Criteria 1-9):**
1. Zero ambiguity — could Claude Code implement with zero questions?
2. Binary sentences — every sentence is a binding rule or marked open question?
3. No contradictions — internal or with other KR documents?
4. No premature constraints — constraining undecided matters?
5. No unbounded universals — every "always/never" scoped to guarantees?
6. Glossary compliance — terms match VISION.md §2?
7. No duplication — unique content only?
8. Accurate state — §9 matches actual code?
9. Adversarial-proof — no second valid reading under hostile interpretation?

**Content Completeness (Criteria 10-14):**
10. Full input coverage — every legitimate input addressed?
11. Exhaustive error handling — every failure mode has recovery?
12. Enumerated edge cases — trigger, response, justification for each?
13. Testable rules — clear pass/fail for every rule?
14. Both-sides integration — expectations AND promises at every boundary?

**Design Quality (Criteria 15-21):**
15. Best-known design — alternatives considered with reasoning?
16. Earned complexity — every element justifies its existence?
17. Scale-graceful — works at 1x and 1000x?
18. Vendor-neutral — no unjustified lock-in?
19. Forward-compatible — extension points identified?
20. Transformative ambition — at least one impossible-made-possible capability?
21. Scholarly integrity — every claim traceable, no undetectable error propagation?

**Communication Quality (Criteria 22-25):**
22. Parseable structure — consistent numbering, exact cross-references?
23. Necessary and sufficient — removing any sentence causes wrong implementation?
24. Clean dependencies — external dependencies explicit and minimal?
25. Operational clarity — new agent with no KR context can follow alone?

**For each defect found:**
```
**Defect N (Tier X — Criterion #Y):**
Section: §Z.W
Failing text: "[exact quote]"
Problem: [Why it fails the criterion]
Fix: [Exact replacement text]
```

### Pass 2: Knowledge Integrity Threats

The 7 threats are defined in KNOWLEDGE_INTEGRITY.md (project knowledge). For each threat, assess this SPEC:

**T-1 Silent Text Corruption**
- Does this engine handle Arabic text? If yes: are diacritics preserved? Is text immutability enforced? What's the mitigation chain?
- Per-field analysis: for every output field containing Arabic text, what prevents corruption?

**T-2 Attribution Error**
- Does this engine make attribution decisions (who said what)? If yes: is consensus required? Is the scholar authority registry consulted?
- Specific risk: multi-layer texts (sharh, hashiya) where the wrong author gets credit.

**T-3 Taxonomic Misplacement**
- Does this engine affect topic classification? If yes: is two-stage placement used? Are ambiguous cases handled?

**T-4 Context Loss**
- Does this engine extract or segment text? If yes: is self-containment checked? Can the output be understood without its original context?

**T-5 Synthesis Hallucination**
- Does this engine generate text that could contain ungrounded claims? If yes: is grounding_type (D-040) enforced? Is every claim traceable?

**T-6 Metadata Poisoning**
- Does this engine produce or modify metadata? If yes: is consensus used for critical fields? Is cross-source consistency checked?

**T-7 Duplication/Contradiction**
- Does this engine handle content that could be duplicated across sources? If yes: is deduplication addressed?

**For each applicable threat:**
```
**T-N: [Threat Name]**
Applies: YES / NO / PARTIALLY
Risk level: HIGH / MEDIUM / LOW
Current mitigation in SPEC: [what the SPEC does about it]
Gap: [what's missing, if anything]
Recommendation: [specific fix]
```

### Pass 3: Silent Failure Patterns

The 7 patterns are defined in SILENT_FAILURES.md (project knowledge). Scan the SPEC for each:

**Pattern 1: Hollow Examples**
Read every example in the SPEC. For each: if you implemented the rule WRONG, would this example still pass? If yes → hollow.

**Pattern 2: Circular Definitions**
For every defined term: replace it with its definition. Does meaning remain? Or is it "X is done by doing X"?

**Pattern 3: Hand-Waving Technology References**
For every named technology: does it actually support Arabic? Does it actually do what the SPEC claims? If uncertain, search and verify.

**Pattern 4: Phantom Metadata**
At every boundary: are field names identical upstream and downstream? Are types identical? Is optionality consistent?

**Pattern 5: Untestable Rules**
For every behavioral rule: can you write a concrete pass/fail test? If the test requires human judgment to determine pass/fail, the rule is undertestable.

**Pattern 6: Missing Error Paths**
For every processing step: what happens when it fails? If the answer isn't in the SPEC, it's missing.

**Pattern 7: Scope Creep Disguise**
For every §4.B capability: can it be implemented using ONLY this engine's inputs and tools? If it needs another engine's data or capabilities, it belongs there, not here.

**For each pattern found:**
```
**Pattern N: [Pattern Name]**
Location: §X.Y
Instance: "[description of what triggers the pattern]"
Fix: [specific correction]
```

### Pass 4: Per-Field Corruption Analysis

This is the deepest check. For every field in the output contract:

```
Field: [field name]
Type: [data type]
If this field is WRONG, what happens to the owner's knowledge?
  → [Specific consequence, e.g., "Wrong author means misattributed quotes in entries"]
How does the SPEC prevent this field from being wrong?
  → [Specific mitigation, e.g., "Multi-model consensus + scholar authority check"]
Is the prevention sufficient?
  → [YES / NO — if NO, what's missing]
```

This is where the most important defects surface. A field that can be wrong with no prevention is a direct threat to the owner's knowledge.

---

## Procedure for Engine Output Audit

When auditing actual engine output (not a SPEC):

1. **Schema check:** Does every output file validate against the contracts?
2. **Text integrity:** Sample 10 Arabic text fields. Compare against frozen source. Any character differences?
3. **Metadata completeness:** Are all required metadata fields populated with non-trivial values?
4. **Metadata consistency:** Does metadata across multiple outputs for the same source agree?
5. **Confidence calibration:** Are confidence scores meaningful? (Are high-confidence items actually correct? Are low-confidence items actually uncertain?)
6. **Cross-reference resolution:** Do all ID references resolve to real entities?
7. **Domain spot-check:** Flag 5 items for owner review with specific questions.

---

## Procedure for Pipeline State Audit

When auditing cross-engine consistency:

1. **Metadata flow:** Run the D-023 check: trace every metadata field from source engine through to the latest engine's output. Is anything lost?
2. **Text integrity chain:** Pick 3 random excerpts. Trace their text back to the frozen source byte-by-byte. Any differences?
3. **ID chain:** Pick 3 random taxonomy placements. Trace back: placed_excerpt → excerpt → passage → normalized content → source. Does the chain resolve?
4. **Consistency check:** Pick an author who appears in multiple sources. Is the author's metadata consistent across all sources? Same name normalization, same dates, same school?

---

## Output Format

```
# Integrity Audit — [Artifact Name]

## Summary
- Total defects found: N
- By severity: N critical, N major, N minor
- By category: N structural, N completeness, N design, N communication
- Threats with gaps: [list]
- Silent failure patterns found: [list]

## Defect Ledger
[All defects in order of severity, with exact fixes]

## Threat Assessment
[Per-threat analysis]

## Silent Failure Findings
[Per-pattern analysis]

## Per-Field Corruption Analysis
[For critical fields only — those where corruption affects the owner's knowledge]

## Overall Assessment
- Is this artifact safe to proceed with? YES / YES WITH FIXES / NO
- What must be fixed before proceeding? [list]
- What should be fixed but isn't blocking? [list]
```

---

## When to Run This Skill

- **Always** before kr-finalize: run integrity first, fix defects, THEN finalize
- **Always** after a major SPEC change: changes can introduce new threats
- **Periodically** on pipeline output: especially after processing new source types
- **On demand** when something feels off: trust your instincts — if it looks too clean, audit it
