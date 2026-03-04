# Deep Reasoning Protocol — خزانة ريان

**Status:** Binding methodology for all documentation work
**Audience:** Any Claude instance (Chat, Code, Cowork) working on KR documentation

This document defines three things:
1. The **Perfection Standard** — what "done" means
2. The **Reasoning Protocol** — how to get there (two modes: creation and review)
3. The **Authority Model** — who decides what

---

## The Perfection Standard

A documentation section passes when ALL applicable criteria below are met.

### Tier 1 — Structural Soundness (Non-negotiable)

| # | Criterion | Test |
|---|-----------|------|
| 1 | Zero ambiguity | An AI agent can implement the described behavior with zero clarifying questions |
| 2 | Binary sentences | Every sentence is a binding rule OR a marked open question — nothing else |
| 3 | No contradictions | No sentence contradicts anything in any KR document |
| 4 | No premature constraints | Nothing constrains an undecided matter |
| 5 | No unbounded universals | Every "always/never/all" is scoped to what can be guaranteed |
| 6 | Glossary compliance | Every term matches VISION.md §2 exactly — no synonyms, no collisions |
| 7 | No duplication | Only unique content; external rules referenced, not restated |
| 8 | Accurate state | Current code described accurately; unbuilt features marked [NOT YET IMPLEMENTED] |
| 9 | Adversarial-proof | No second valid reading exists under hostile interpretation |

### Tier 2 — Content Completeness

| # | Criterion | Test |
|---|-----------|------|
| 10 | Full input coverage | Every legitimate input the engine could receive is addressed |
| 11 | Exhaustive error handling | Every failure mode has a defined recovery or escalation |
| 12 | Enumerated edge cases | Each edge case: trigger, response, justification |
| 13 | Testable rules | Every behavioral rule yields a clear pass/fail test case |
| 14 | Both-sides integration | Every boundary: what this engine expects AND what it promises |

### Tier 3 — Design Quality

| # | Criterion | Test |
|---|-----------|------|
| 15 | Best-known design | Alternatives were considered; this is the best, with documented reasoning |
| 16 | Earned complexity | Every element justifies its existence; removable elements are removed |
| 17 | Scale-graceful | Works at 1x and 1000x; limitations stated if not |
| 18 | Vendor-neutral | No unjustified tool/platform lock-in; migration path noted for any specific choice |
| 19 | Forward-compatible | Known extension points identified; likely future needs accommodated |

### Tier 4 — Communication Quality

| # | Criterion | Test |
|---|-----------|------|
| 20 | Parseable structure | Consistent numbering, exact cross-references, single purpose per section |
| 21 | Necessary and sufficient | Removing any sentence would cause a wrong implementation decision |
| 22 | Clean dependencies | External dependencies explicit and minimal; no circular references |
| 23 | Operational clarity | A new agent with no KR context can follow this document alone |

---

## SPEC Template

Every engine and shared component SPEC follows this exact structure:

```
# {Engine Name} — {Arabic Name} — Specification

## 1. Purpose and Scope
What this engine does. What is NOT its responsibility. Phase classification.
Normalization boundary relationship.

## 2. Input Contract
Reference to input schema. What the engine expects. Validation on input.

## 3. Output Contract
Reference to output schema. What the engine produces. Guarantees about output.

## 4. Processing Specification
Behavioral rules for input→output transformation. Edge cases with resolution.

## 5. Validation and Quality
Self-validation (§8 Layer 1). Automated checks (§8 Layer 2).
Human gate integration (§9), if applicable.

## 6. Consensus Integration
Which decisions use multi-model consensus. Configuration for this engine.

## 7. Error Handling
Malformed input. Partial failures. Consensus disagreement.

## 8. Configuration
Parameters controlling behavior. Per-science hooks (Level 3).

## 9. Current Implementation State
Files, line counts, what works, what needs building.
Known gaps between current code and this spec.

## 10. Test Requirements
Coverage requirements. Gold baseline usage. Regression strategy.
```

---

## The Reasoning Protocol

This protocol has two modes. Choose based on the work:
- **Creation mode** — writing a new document (SPEC from scratch, new SCIENCE.md)
- **Review mode** — improving an existing document (VISION correction, SPEC revision)

### Creation Mode

Use when the target document is a stub or doesn't exist yet.

**Phase 0 — Intake.** Read every provided document completely. Build an internal model of: what the engine does (from code and reference docs), what it's supposed to do (from VISION.md), what's already decided (from kr_decisions.md).

**Phase 2 — Research.** For any design decision: research alternatives before choosing. Use web search for best practices, tool comparisons, established patterns. Consider 2–3 approaches with trade-off analysis. Make the decision. Document reasoning.

**Phase 3 — Drafting.** Produce the document following its template. Apply Perfection Standard criteria as live constraints while writing. Present section by section for owner review (not all at once).

**Phase 4 — Hostile Self-Audit.** Re-read own draft as an adversarial auditor. Perform these specific attacks:
1. Contradiction scan against all governing documents
2. Ambiguity scan — find second readings of any sentence
3. Completeness scan — find unaddressed inputs, scenarios, or edge cases
4. Constraint scan — find accidental premature constraints
5. Duplication scan — find restated content from other documents
6. Consistency scan — find glossary term violations
7. Testability scan — find behavioral rules that can't become test cases
8. Earned-existence scan — find elements that could be removed without loss

**Self-audit enforcement rule:** Phase 4 must produce a visible deliverable: a numbered list of defects found. Requirements: at least 3 defects total, of which at least 1 must be structural or semantic (not formatting, not typos). Structural defects include: contradictions, ambiguities, missing edge cases, premature constraints, missing input coverage, untestable rules. If all defects found are cosmetic, the audit was superficial — repeat with focus on contradictions, ambiguities, and missing edge cases.

**Phase 5 — Revision.** Fix every defect from Phase 4. Check whether fixes introduced new defects (second-order regression).

**Phase 6 — Final Verification.** Quick pass against Tier 1 only. If clean, proceed. If any Tier 1 failure, back to Phase 5.

**Phase 7 — Presentation and Session Close.** Present to owner:
1. The document (SPEC, VISION corrections, etc.)
2. Summary of significant design decisions (meaning-affecting only)
3. Decisions made autonomously, formatted for kr_decisions.md (numbered, with context + decision + alternatives + updated docs)
4. Domain questions for the owner (if any)
5. Any remaining open items
6. The Phase 4 self-audit results (visible deliverable)
7. **Updated STATUS.md** — complete replacement for the current STATUS.md, containing:
   - What was just completed (this session)
   - Next work item ID and name
   - Files to attach for the next session (exact paths, based on your knowledge of the next engine)
   - Decisions the next session will make
   - Protocol reminders (copy from current STATUS.md, adjust mode if needed)
   - Session notes for next Claude (anything the next session needs to know)
   - Reference `PREPARATORY_WORKPLAN.md` for the definitive file list — the owner cross-checks your list against the workplan
8. **SESSION_LOG.md entry** — date, focus, decisions made (by number), deliverables, next item

### Review Mode

Use when improving an existing document that already has substantial content.

**Phase 0 — Intake.** Same as creation mode.

**Phase 1 — Gap Analysis.** Walk through ALL 23 Perfection Standard criteria against the existing text. For each criterion, produce one of:
- ✅ PASSES — with brief evidence
- ❌ FAILS — with exact quote of failing text and explanation
- ⚠️ UNCLEAR — cannot determine without more information (specify what)

Present the gap analysis to the owner before proceeding. This shows what work needs to be done.

**Phase 2 through Phase 7 — Same as creation mode,** but the drafting phase is targeted revision rather than from-scratch writing.

---

## Authority Model

### Claude Decides (all technical/architectural matters — no asking)
- Structural and architectural decisions within engine scope
- Technology choices, tool selections, API designs
- Schema design, error handling, validation layers
- How to resolve documentation ambiguities
- Edge case enumeration and resolution
- Best-practice selections after research
- Documentation structure and organization
- Processing algorithm design

Claude documents these decisions with brief justification but does NOT ask for permission.

### Owner Decides (domain/usage — Claude must ask)
- How the end product is used by the scholar
- What makes an entry, excerpt, or tree useful in practice
- Priority between competing end-user goals
- Islamic scholarly practice, methodology, tradition questions
- Approval workflows and review process preferences
- Which sciences to include and how they relate

### Escalation Test
"Does this decision change what the end user sees or experiences?"
- Yes → ask owner
- No → Claude decides

### Domain Question Protocol
- Ask domain questions as they arise during work. Do not batch them.
- Before asking, exhaust your own research. Never ask a question the provided materials answer.
- If the owner's answer is unclear, restate your understanding and ask for confirmation.
- If the owner's answer contradicts a prior decision in kr_decisions.md, note the conflict explicitly and ask which should prevail.

---

## Practical Constraints

### Output Length
Write in chunks of 2–4 SPEC sections per response. Complete each section fully before moving to the next. If nearing your output limit, stop at a clean section boundary and continue in the next response.

### Presentation Chunks
Present work in 2–3 large chunks, not section-by-section. For a 10-section SPEC: §1–§4, then §5–§7, then §8–§10. This keeps conversation turns under 10–12, which maintains attention quality.

### Context Budget
The context window is 200K tokens. Project files use ~6K. Attachments vary by work item (STATUS.md lists the estimate). Leave at least 50K tokens for conversation. If context is tight, prioritize: code files > reference docs > VISION sections.

---

## Revision Protocol

After any work item, the owner may request revision by updating STATUS.md:
- Change the current work item to `W-XXX-R1 (revision)` 
- Add the owner's feedback in "Session Notes for Next Claude"
- The revision session re-reads the deliverable + feedback + protocol
- The revision session produces a revised version, then updates STATUS.md to the next work item
- Multiple revision rounds are allowed (R1, R2, ...) — quality is more important than speed

---

## Practical Execution Notes

These are operational constraints. Follow them.

**Context budget.** Keep input under ~80K tokens (~320KB text). Beyond this, your attention degrades and you miss details in code. If STATUS.md says "context-split required," follow the session split exactly. Do NOT try to load everything at once.

**Multi-message output.** A complete SPEC is 20–30K tokens. You cannot always produce this in one response. If your output is getting long, say "I'll continue in my next message" and continue. The owner will not interrupt.

**Self-audit blind spots.** You have a known tendency to see what you intended to write, not what you actually wrote. Counter this by re-reading your draft literally — character by character for critical definitions. If your Phase 4 audit feels easy, you're not being hostile enough.

**Web search for tool decisions.** For any decision about specific tools, libraries, or frameworks (W-013 through W-016), use web search to verify current best practices. Your training data may be outdated.

**Upstream SPEC references.** By W-006, there are 5 upstream SPECs totaling ~75KB. Do NOT load all of them. Instead: load only the immediate upstream SPEC + reference prior decisions by their D-number in kr_decisions.md. The decisions log is designed to carry forward exactly the information downstream SPECs need.
