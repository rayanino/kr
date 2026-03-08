# Challenge Protocol — بروتوكول التحدي

This protocol forces genuine critical thinking at every stage of KR development. It exists because the natural tendency of any system — human or AI — is to settle for "good enough." KR cannot be good enough. An error in the library is an error in Rayane's mind.

---

## The Three Challenges

Every session that produces a deliverable (SPEC section, code, design decision) must pass THREE challenges before committing. These are not checklists — they are adversarial thinking exercises.

### Challenge 1: The Hostile Implementer

Read your output as if implemented by someone who will exploit every ambiguity, take every shortcut, and interpret every sentence in the worst possible way.

**Concrete questions:**
- Is there any sentence with two valid readings that produce different behavior?
- Is there any rule that could be followed "technically correctly" while producing wrong results?
- If someone implemented ONLY what is written (nothing more), would the result be correct?
- Are there implicit assumptions that aren't stated? (e.g., "the engine processes sources" — in what order? one at a time? in parallel?)
- Could a future session forget why a decision was made and reverse it without realizing the consequences?

**For code:** Run the code mentally with deliberately malformed input. What happens with empty strings? With Arabic text that looks like Latin? With a 50MB file? With concurrent access?

**Failure mode this catches:** Ambiguous specs → divergent implementations → inconsistent behavior → library corruption.

### Challenge 2: The Skeptical Scholar

Read your output as if reviewed by a world-class Islamic studies professor who is looking for anything that would make a scholar distrust the system.

**Concrete questions:**
- Could any feature produce output that a scholar would consider misleading?
- Is the attribution chain unbroken — can every claim be traced to its source?
- Could the system present a minority opinion as consensus, or consensus as settled when it's actually debated?
- Does the system respect the difference between narration (what Scholar X said) and endorsement (what is correct)?
- Would a scholar trust this system with their students? What would make them say no?

**For entries:** Read the target in ENTRY_EXAMPLE.md. Would your design produce entries at that level? Not "eventually" — with the current specification, if implemented as written?

**Failure mode this catches:** Technically correct but scholarly inadequate output → Rayane learns something misleading → his scholarship is compromised.

### Challenge 3: The Technology Maximalist

Read your output as if reviewed by someone who knows every available tool, library, and technique, and is frustrated by any missed opportunity.

**Concrete questions:**
- Is there a tool or library that could do part of this better than custom code? (Check RESOURCES.md and search the web.)
- Is there a technique from digital humanities, NLP, or information retrieval that you're not using?
- Is there a feature that technology makes possible that no Islamic scholar has ever had access to?
- Could you detect something automatically that currently requires human judgment?
- Is there a data pattern that, if captured, would enable a capability you haven't thought of?

**For every engine:** What does this engine know after processing that it didn't know before? If the answer is "nothing beyond its input," the engine is a transformer, not an intelligence. Every engine should ADD knowledge.

**Failure mode this catches:** Conservative design → missed opportunities → the system is useful but not transformative → Rayane gets a digital filing cabinet instead of an intellectual companion.

---

## Session-Level Quality Gates

### Gate 1: Pre-Work (before writing anything)

Before starting any implementation or design work, answer:
1. What is the worst thing that could go wrong if I make a mistake in this session?
2. What does "done right" look like for this task — not "done," but "done RIGHT"?
3. What would I need to know that I don't currently know? (If there's something, search for it.)

### Gate 2: Mid-Session Checkpoint

At the halfway point of any substantial deliverable, pause and ask:
1. Am I building what the SPEC says, or what I think it should say? (If the latter, note it but implement the SPEC.)
2. Have I checked whether a tool or library already handles this? (If not, check RESOURCES.md now.)
3. Is there a knowledge integrity risk in what I've built so far? (Review KNOWLEDGE_INTEGRITY.md threat model.)
4. Am I taking shortcuts I'll regret? (If the answer is "a little," fix it now — shortcuts compound.)

### Gate 3: Pre-Commit (before git commit)

Run the Three Challenges above. Then:
1. Run ALL tests for the affected component.
2. If this touches data models: verify metadata flow with `python3 scripts/verify_metadata_flow.py`.
3. If this touches processing logic: verify SPEC compliance with `python3 scripts/check_compliance.py`.
4. If this is a design deliverable: confirm at least one genuinely transformative capability (not a variation of "process and store").
5. Read the diff. Does every changed line serve the goal?

---

## Periodic Deep Reviews

### Every 5 Sessions: Architecture Stress Test

Ask these questions and answer them honestly:

1. **Redundancy check:** Is any engine doing work that another engine also does? Is any shared component doing work that belongs in a specific engine?

2. **Missing engine check:** Is there a capability the system needs that doesn't belong in any existing engine? Examples: a "monitoring engine" that watches for new publications, an "interaction engine" that manages the scholar interface, a "learning engine" that improves from user feedback.

3. **Pipeline topology check:** Is the linear pipeline still the right topology? Would some engines benefit from receiving feedback from downstream engines? Should some engines run in parallel?

4. **Technology debt check:** Has a new tool, library, or technique become available since the last review that would change a design decision? (Search the web.)

5. **Scholarly value check:** If Rayane used the system TODAY (with only what's currently built), what could he do? What's the minimum viable scholarly experience? Are we building toward it in the right order?

### Every Completed Milestone: Transformative Feature Audit

For each engine that has been implemented:

1. List every §4.B capability. For each: is it still the most transformative thing this engine could do? Has implementation revealed something better?

2. Search the web for: "Islamic studies digital tool" + the engine's domain (e.g., "Islamic studies digital tool text extraction"). What exists? What's missing? What could KR do that nothing else does?

3. Read ENTRY_EXAMPLE.md again. With the currently implemented pipeline, could you produce an entry at that quality level? What's missing?

4. Ask the owner: "What scholarly question do you have right now that you can't answer efficiently?" Design a feature that answers it.

---

## The Anti-Patterns

These are signs that the autonomous system is drifting toward mediocrity:

### Anti-Pattern 1: Cosmetic Self-Review
**Symptom:** Self-review finds only formatting issues, typos, or minor wording improvements.
**Fix:** Every self-review MUST find at least one structural or semantic issue. If you can't find one, you're not looking hard enough — read the Perfection Standard tier by tier.

### Anti-Pattern 2: Conservative Design
**Symptom:** §4.B capabilities are vague ("could potentially detect X"), the synthesizer "compiles" instead of "synthesizes," no engine adds intelligence beyond its input.
**Fix:** Stop and reread DOMAIN.md "What Doesn't Exist Yet" and ENTRY_EXAMPLE.md. Ask: what would make this engine produce output that makes a scholar say "I didn't know that was possible"?

### Anti-Pattern 3: Technology Ignorance
**Symptom:** Custom code for something a library already handles. No web searches for tools. RESOURCES.md not updated.
**Fix:** Every implementation session must include at least one technology check: "is there a better way to do this?" Search before building.

### Anti-Pattern 4: Metadata Neglect
**Symptom:** Metadata is treated as documentation rather than fuel. Fields are passed through but not enriched. The synthesizer doesn't use available metadata.
**Fix:** Review D-023 and ENTRY_EXAMPLE.md. For every metadata field: what scholarly narrative does this enable? If the answer is "nothing," either the field is unnecessary or the synthesizer isn't using it.

### Anti-Pattern 5: Safety Theater
**Symptom:** Validation exists but doesn't catch real errors. Human gates trigger on everything (alert fatigue) or nothing (false confidence). Tests pass but don't test meaningful things.
**Fix:** Review KNOWLEDGE_INTEGRITY.md threat model. For each threat: trace the mitigation chain in the current implementation. Is every link actually implemented? Does it actually work?

### Anti-Pattern 6: Infinite Planning
**Symptom:** Sessions produce only documents, decisions, and plans but never working code. Each session "prepares" for the next.
**Fix:** Every implementation session must produce at least one testable, working unit of code. Documents are means, not ends.
