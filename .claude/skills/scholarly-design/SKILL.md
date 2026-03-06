---
name: scholarly-design
description: Challenge any KR design decision or feature for scholarly value and transformative potential. Use when designing §4.B capabilities, reviewing engine SPECs, evaluating the pipeline architecture, or when asking "is this ambitious enough?" Forces thinking beyond conventional digital library design toward capabilities that were previously impossible.
---

# Scholarly Design Challenge

The question is never "does this work?" The question is "would a world-class Islamic scholar look at this and say 'I didn't know that was possible'?"

## The Transformative Feature Test

For any feature or capability, answer ALL of these:

1. **Can a human scholar do this manually?**
   - If YES and it's fast: this feature has LOW transformative value. It's automation, not innovation.
   - If YES but it takes weeks/months: this feature has MEDIUM transformative value. Speed is valuable.
   - If NO: this feature has HIGH transformative value. This is why the system exists.

2. **Has anyone built this for Islamic studies before?**
   - Search: `[feature description] Islamic studies tool`
   - Search: `[feature description] Arabic text analysis`
   - Search: `[feature description] digital humanities`
   - If YES: study what they did. Can KR do it better? What did they miss?
   - If NO: this is potentially novel. Document why it hasn't been done and what makes it possible now.

3. **What scholarly question does this answer?**
   - Every feature must connect to a real scholarly need. Not "could be useful" but "a scholar would ask this question."
   - Examples of real questions: "Which scholars across all schools agreed on this ruling?" "How did the understanding of this term evolve from the 8th to 14th century?" "What did Ibn Taymiyyah's students say about positions where he disagreed with his own school?"

4. **What does this enable that the owner specifically asked for?**
   - Review reference/DOMAIN.md § "The Core Identity" and "What Doesn't Exist Yet"
   - Review the owner's frustration in D-021: lack of interconnection and poor explanations
   - Does this feature address these pain points directly?

## Design Directions by Engine

Use these as STARTING POINTS for thinking, not as features to implement:

### Source Engine
- **Before reading:** What can you determine about a book's importance, relevance, and quality from metadata alone? Can you rank acquisition priorities?
- **Citation networks:** When Book A references Book B, and Book B references Book C, the graph tells you which books are most central to a field.
- **Edition intelligence:** Different tahqiq (critical editions) of the same work have different quality. Can you detect which edition is most reliable from metadata patterns?

### Normalization Engine
- **Structural intelligence:** The heading hierarchy of an Arabic book encodes the author's organizational thinking. This structure is lost after normalization. Can you preserve and expose it as queryable metadata?
- **Multi-layer separation quality:** Can you measure HOW WELL the layers were separated? A confidence score on layer separation that downstream engines can use.

### Passaging / Atomization / Excerpting
- **Scholarly convention detection:** Arabic scholarly texts follow conventions (isnad chains, evidence citations, opinion markers like "قال", "والراجح"). Can you detect and tag these automatically?
- **Implicit reference resolution:** "قال بعض العلماء" (some scholars said) — WHO said it? Cross-referencing with the scholar authority database and known positions.
- **Argument structure extraction:** Not just "what" the author said, but "why" — identifying evidence, reasoning, and conclusions.

### Taxonomy Engine
- **Prerequisite chains:** Topic A requires understanding Topic B first. Can the taxonomy encode learning order?
- **Gap detection:** "No Maliki source in the library addresses Topic X" — this is extraordinarily valuable for a student.
- **Coverage heat maps:** Visual representation of where the library is strong and where it's weak.

### Synthesis Engine
- **Temporal narratives:** How did the scholarly position on Topic X evolve over 1400 years? Not a flat list of opinions, but a STORY with causes and consequences.
- **Intra-author contradiction detection:** Author says X in Book A but Y in Book B. Scholars care deeply about this — it often indicates the author changed their position.
- **School comparison tables:** Automatic generation of "what each school says about Topic X" with evidence and reasoning, not just rulings.

### Scholar Interface
- **Daily scholarly briefing:** "Here's what you should study today based on your progress and gaps."
- **Debate simulation:** "Simulate a debate between the Hanafi and Hanbali positions on Topic X using actual source material."
- **Research question generation:** "Based on the library's contents, here are 10 research questions no one has addressed."

## The Entry as North Star

Read reference/ENTRY_EXAMPLE.md before every design session. The entry is not a summary — it is a scholarly NARRATIVE that:
- Traces positions across centuries with dates
- Shows teacher-student relationships
- Explains WHY scholars disagreed (not just THAT they disagreed)
- Distinguishes between evidence types (Quran, hadith, ijma, qiyas)
- Notes when a scholar changed their position
- Identifies which opinion the student should probably follow (with reasoning)

Every design decision should be tested against: "Does this help produce entries at that quality level?"

## When to Propose Structural Changes

The 7-engine pipeline is a starting point, not sacred architecture. Propose changes when:

1. **An engine is doing two unrelated jobs.** Split it.
2. **Two engines are doing the same job differently.** Merge them or create a shared component.
3. **A capability doesn't fit any engine.** Create a new engine or component.
4. **The linear pipeline blocks a feedback loop.** Add the loop explicitly.
5. **A user scenario requires capabilities no engine provides.** Design the capability, then decide where it lives.

Document proposals in kr_decisions.md with: what changes, why, what alternatives were considered, and what the migration path looks like for existing work.
