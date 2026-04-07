# G/SC Ground Truth Pre-Extraction — Session 5

> CC pre-extracted atoms from raw owner text (Layer A ground truth) before agent reports arrive.
> Purpose: validation baseline for 7 parallel extraction agents.
> Every atom below MUST appear in the corresponding agent's extraction report.

---

## G1 — Added Benefit Rule

Owner chose: **A** (short entry has value as standalone)
Raw file: 43 lines | Topic: Does a short standalone excerpt have value?

### Ground Truth Atoms (MUST be in agent report)

| # | Atom | Verbatim Anchor | Disposition |
|---|------|-----------------|-------------|
| GT-G1-01 | **Rule of added benefit**: excerpts must add value; a useless excerpt wastes time and focus, and harms the potential of its parent content | "A useless excerpt is not only valueless but also takes away from the potential" | SPEC |
| GT-G1-02 | **Excerpting is OBJECTIVE**: no outside factors (length preference, style preference, owner taste) may affect excerpting rules | "IT DOESN'T FUCKING MATTER...EXCERPTING IS OBJECTIVE. NO OUTSIDE FACTORS AFFECT IT." | FP |
| GT-G1-03 | **Harmlessness gate**: retained overlap material must be HARMLESS; short is not sufficient alone — must be short AND harmless, or long and harmless | "HARMLESS + extra potential = DO IT" | SPEC |
| GT-G1-04 | **Overlap retention rule**: heading-like text (e.g., في الحديث ثلاثة مباحث) may appear in both excerpts when it's short, harmless, and provides orientation | "it's 1% vs 99%, and it DOES NOT HARM" | PROMPT |
| GT-G1-05 | **Catastrophe of misallocation**: if text belongs to the wrong excerpt, the right excerpt loses it, creating a false sense of completeness | "ESPECIALLY if the text where...would actually be needed...lacks this sentence now...this is just a catastrophe" | SPEC |
| GT-G1-06 | **Owner consciousness assumption**: owner knows he's reading excerpts, so minor structural artifacts are acceptable | "the owner knows he is dealing with excerpts" | META |
| GT-G1-07 | **Extensiveness love**: owner loves vast, encyclopedic, comprehensive excerpts — but this DOES NOT affect excerpting rules (subordinate to GT-G1-02) | "I'm in love with extensiveness...thousands...hundreds of thousands...everything" | META |

**Duplicate check**: GT-G1-02 strengthens FP-4 (taxonomy independence → broader "no outside factors"). GT-G1-05 relates to FP-5 (cascading trust).

---

## G2 — Hadith Chunking & Proof Relationships

Owner chose: **C** (both together with further granulation possible)
Raw file: 80 lines | Topic: Can explained-explanation pairs be further granulated?

### Ground Truth Atoms

| # | Atom | Verbatim Anchor | Disposition |
|---|------|-----------------|-------------|
| GT-G2-01 | **Chunk-by-chunk explanation methodology**: scholars explain hadiths chunk by chunk (stop, explain, next chunk). This is a universal scholarly pattern the library must recognize | "a common methodology between scholars is that when explaining a hadith they explain it chunk by chunk" | SPEC |
| GT-G2-02 | **Hadith sub-tree structure**: hadiths in library should branch into: raw (memorization-ready), full explanations (المعنى الإجمالي), chunk1→excerpts, chunk2→excerpts | Owner's tree diagram showing raw/full/chunk branches | DEFERRED |
| GT-G2-03 | **Chunking divergence tolerance**: different scholars chunk differently; library must decide its own chunking using scholars as inspiration, not blindly copying any one scholar's chunking | "we can focus on using their chunkings as inspiration and instead reason and make a decision" | SPEC |
| GT-G2-04 | **Proof relationship types**: proofs under same leaf have specific relationships (supporting, puzzle-pieces, seeming-contradictions). These must be identified and classified | "we should define and focus and research the different scenarios of 'relationships between proofs'" | DEFERRED |
| GT-G2-05 | **Cross-topic proof placement**: when same hadith applies to multiple topics (prayer + wudu), excerpts must be placed at ALL relevant locations, not limited to the original context | "it should answer the open general question: 'where does this excerpt fit within the islamic sciences'?" | DEFERRED |
| GT-G2-06 | **غريب الحديث branch**: word/grammar explanations form a separate branch from ruling-focused explanations | "غريب الحديث: is a form of explanation of a hadith, but just a specific form; explanations of words" | DEFERRED |
| GT-G2-07 | **Unique identifiers required**: branch names must be unique; narrator name alone is insufficient | "the mere name of the narrator is not enough as a unique identifier" | SPEC |
| GT-G2-08 | **Analytics beyond raw text**: library should provide unprecedented data — relationships, madhab, proof support networks — that no traditional student had | "EXCERPTS DO NOT ONLY PROVIDE RAW THEORY, BUT ALSO ANALYTICS" | META |
| GT-G2-09 | **Deep research mandate on proof types**: usul al-fiqh handles proof types and relationships; this requires prolonged deep research, not skimming | "this is something that requires deep and long research" | META |
| GT-G2-10 | **Lost potential principle**: text relevant to topic X appearing only under topic Y means owner loses potential; library must cross-place | "WHEN I STUDY WUDU WHILE THE PRAYER-TOPIC ALSO CONTAINS SOME TEXT THAT TOUCHES ON WUDU, THAT TEXT...IS LOST" | FP |

**Duplicate check**: GT-G2-01 extends EE-1. GT-G2-05/10 relate to FP-4 scope (taxonomy placement freedom). GT-G2-07 new.

---

## G3 — Multi-Function Excerpts & Numbered Points

Owner chose: **C** (depends on content; function determines treatment)
Raw file: 105 lines | Topic: Should numbered points each become own excerpts?

### Ground Truth Atoms

| # | Atom | Verbatim Anchor | Disposition |
|---|------|-----------------|-------------|
| GT-G3-01 | **Multi-function identification**: each excerpt may serve multiple topics/functions; ALL functions must be identified | "IDENTIFYING ALL FUNCTIONS OF AN EXCERPT!!!" | SPEC |
| GT-G3-02 | **Function determines placement, not structure**: whether text is bulleted, numbered, or inline should not individually affect excerpting or taxonomy placement | "a piece of text being bulleted or not should not individually affect its excerpting" | FP |
| GT-G3-03 | **Numbering-based excerpting prohibition**: excerpts must NEVER be driven by formatting structure (numbering, bullets); only knowledge content determines boundaries | "it is asking if excerpts should be based on a SUBJECTIVE thing the author puts down for structure...NO!!!" | FP |
| GT-G3-04 | **Context equally important as content**: excerpting must invest in context (what came before, what comes after, relationships between points) | "I DON'T THINK I WILL EVER STUDY AN EXCERPT WITH 100% assurance...without worry about lack of context" | SPEC |
| GT-G3-05 | **LLM creative freedom (5%)**: alongside 95% rules/protocols, 5% creative reasoning room where LLM receives context and reasons about optimal excerpting | "there should also be creative/room for reasoning (5%), in which the llm just receives all the context" | SPEC |
| GT-G3-06 | **Proximity-based harmless rule extension**: whether retained overlap is acceptable depends on branch proximity — closer branches = more acceptable | "a major part in the 'does the short and harmless rule apply' is whether the other not directly related part is or is not part of the same branch" | SPEC |
| GT-G3-07 | **Library value proposition fear**: if library doesn't provide enough benefit over traditional reading, owner will abandon it; benefit must be explicit | "ONE OF THE BIGGEST NIGHTMARES IS: the entire library being built, but the owner then deciding to just not use it" | META |
| GT-G3-08 | **Arabic-only library content**: ALL naming, titles, vocabulary inside the library must be Arabic | "THE LIBRARY AND EVERYTHING INSIDE OF IT SHOULD ONLY BE IN ARABIC" | SPEC |
| GT-G3-09 | **Vocabulary definition deficit**: project desperately needs clear, machine-readable vocabulary definitions for all terms (leaf, branch, excerpt, etc.) | "WE ARE SERIOUSLY LACKING IN VOCABULARY...WE NEED TO SPEND MORE TIME ON IT" | META |
| GT-G3-10 | **Scholar-quoting-opposition trap**: scholar may explain opposition's view as if it were his own — library must detect this context to prevent wrong attribution | "a scholar is deep into explaining the opposition's opinion that he talks about it as if it were his own" | SPEC |

**Duplicate check**: GT-G3-03 new (not same as FP-4 which is taxonomy-independence). GT-G3-10 relates to FP-14 (speaker-role inversion). GT-G3-06 extends GT-G1-03.

---

## G4 — Conditions Excerpting & Granularity

Owner chose: (detailed worked examples)
Raw file: 105 lines | Topic: How to excerpt legal conditions (shurut)

### Ground Truth Atoms

| # | Atom | Verbatim Anchor | Disposition |
|---|------|-----------------|-------------|
| GT-G4-01 | **Condition-per-excerpt rule**: each legal condition (shart) should have its own excerpt under a conditions branch | "every condition for cutting off the hand of a thief should have its own excerpt" | SPEC |
| GT-G4-02 | **Sub-condition branching**: conditions may have sub-branches (condition → method1, method2) for further granularity | Owner's worked tree: conditions → انتفاء الشبهة → excerpt:الشرط → excerpt:تطبيقات | SPEC |
| GT-G4-03 | **Mid-sentence cut indicator**: when excerpt starts mid-sentence, system must indicate this to the owner | "indicator that this is not a standalone text but that it got cut off mid sentence" | SPEC |
| GT-G4-04 | **Continued-topic detection**: when author splits a topic across non-adjacent sections, library must detect and inform owner | "it would be very nice...if the library can even detect things like this (cut-off topics getting continued)" | DEFERRED |
| GT-G4-05 | **Harmless retention worked example**: two shurut being together may cause "serious confusion" or "wrongfully linking" — NOT harmless | "it DOES NOT SEEM HARMLESS; it's a different شرط, and putting two شرط together may cause serious confusion" | SPEC |
| GT-G4-06 | **Dream granularity**: owner's ideal is extreme granularity (each example as its own sub-excerpt), but afraid of over-granulating | "I would want even further granulation, but I didn't mention it...because of how afraid I am of over-granulating" | META |
| GT-G4-07 | **Machine-readable format emphasis**: every file in the project must be in optimal format for agents, not humans | "IS THIS IN A MACHINE READABLE / OPTIMAL FORMAT??" | META |
| GT-G4-08 | **Naming protocols needed**: clear naming conventions for excerpt files, taxonomy leaf titles, etc. | "throughout the pipeline, we need to ESTABLISH CLEAR NAMING PROTOCOLS" | META |
| GT-G4-09 | **Intelligence over hard rules**: no hard-coded algorithms alone — dynamic sources need intelligent, contextual excerpting decisions | "we should never just rely on HARD-DEFINED / HARDCODED rules...BECAUSE WE ARE DEALING WITH DYNAMIC SOURCES" | SPEC |

**Duplicate check**: GT-G4-01 new (domain-specific). GT-G4-09 strengthens FP-6 scope. GT-G4-05 extends GT-G1-03 with concrete counterexample.

---

## SC1 — Teaching Units & Author Flow (TRANSFORMATIVE)

Owner chose: **B** (reference alone is NOT sufficient)
Raw file: 114 lines | Topic: How to handle author reference-backs in excerpts

### Ground Truth Atoms

| # | Atom | Verbatim Anchor | Disposition |
|---|------|-----------------|-------------|
| GT-SC1-01 | **EXCERPT = TEACHING UNIT** (transformative realization): excerpt is not a quote; it's a self-contained teaching unit with original text as the starting point | "I GENUINELY JUST REALIZED OUR SYSTEM IS ACTUALLY A SYSTEM OF 'TEACHING UNITS' rather than 'EXCERPTS'" | FP |
| GT-SC1-02 | **Author flow preservation**: author's intent, flow, chapter ordering, and reader-level assumptions must NEVER be lost | "the AUTHOR'S INTENT AND FLOW should NEVER BE LOST; instead, they are one of the major things to ALWAYS TAKE INTO ACCOUNT" | FP |
| GT-SC1-03 | **Zero pre-context principle**: owner opens each excerpt with 0 prior knowledge; excerpt must be fully self-contained | "ASSUME STUDY OF AN EXCERPT STARTS WITH 0 KNOWLEDGE AND CONTEXT BEFOREHAND" | FP |
| GT-SC1-04 | **Passage linkage**: each excerpt must have an openable view of its full surrounding passage from the original text | "THE PASSAGE NEVER GETS LOST AND IS ALWAYS VIEWABLE WITHIN AN EXCERPT" | SPEC |
| GT-SC1-05 | **Library replaces book-in-hand**: library must provide everything traditionally provided by having the physical book open (reference, flip-back, context) | "THE LIBRARY NEEDS TO PROVIDE THAT ENVIRONMENT FOR ME" | FP |
| GT-SC1-06 | **Reference-back handling**: when author says تقدم/سبق, library must identify and provide the referenced content | "the piece that is referred back to is very relevant...the library should make up for it" | SPEC |
| GT-SC1-07 | **LLM Context Notes**: AI-generated pre-reading context notes accompanying each excerpt | "LLM Context Notes: Additional context, summaries, or guiding questions" | DEFERRED |
| GT-SC1-08 | **Self-containment anti-manhunt**: self-containment means NOT sending the owner on a manhunt across excerpts | "YOU SEE HOW PART OF SELF-CONTAINMENT IS NOT SENDING THE OWNER ON A MANHUNT?" | SPEC |
| GT-SC1-09 | **Sky-is-the-limit expansion (within rules)**: teaching units can expand beyond raw text as much as beneficial, but protocols/rules still govern | "THE SKY IS THE LIMIT!!!! But this does not mean we should start disregarding...our protocols and rules" | META |
| GT-SC1-10 | **Reference-back orientation vs concept distinction**: purely orientational reference-backs need minimal extra context; concept-building reference-backs need extensive restoration | "not every 'reference back' per se needs additional context...It depends" | SPEC |

**Duplicate check**: GT-SC1-03 already partially in C-SC rules but owner states it as universal FP-level principle. GT-SC1-01 is genuinely new — vocabulary shift. GT-SC1-02 new FP candidate.

---

## SC2 — Quality Standards & Explained-Explanation Linkage

Owner chose: (detailed analysis, strong criticism)
Raw file: 66 lines | Topic: Do you need the explained text visible when studying explanation?

### Ground Truth Atoms

| # | Atom | Verbatim Anchor | Disposition |
|---|------|-----------------|-------------|
| GT-SC2-01 | **Explained-explanation linkage is critical**: separating them risks catastrophic knowledge errors from hadith version mismatch | "some hadiths differ in 'cosmetic' wordings...while MANY DIFFERING HADITHS VARY IN SIGNIFICANT WORDS" | FP |
| GT-SC2-02 | **Study technique: chunk-and-master**: owner studies in small chunks, mastering each, then next; first pass is always overview/skim | "my very first step...IS NEVER BLINDLY diving into one chunk...Instead...I start at the first branch but skim over it quickly" | META |
| GT-SC2-03 | **Manhunt prevention principle**: library must PREVENT owner from needing to search for related content; both for UX and error prevention | "PREVENT THE OWNER FROM NEEDING TO GO ON A MANHUNT AT ALL COSTS!!!" | FP |
| GT-SC2-04 | **Hadith version danger**: wrongly linking explanation to wrong hadith version leads to "EXTREME MISUNDERSTANDING AND EXTREME DEVIATION IN KNOWLEDGE" | "if I don't have the proof...referenceable EXACTLY FROM THE SOURCE TEXT, then I may look up the hadith myself...and stumble across a different version" | SPEC |
| GT-SC2-05 | **Pipeline gap: passaging-to-excerpting skip too big**: needs deeper pre-excerpting analysis of connections, context needs, per-atom dependency mapping | "I THINK THE SKIP FROM PASSAGING TO EXCERPTING IS TOO BIG" | DEFERRED |
| GT-SC2-06 | **Quality means MAX EFFORT**: "enough" and "good" in this library mean absolute max effort, not decent/acceptable | "'enough' and 'good'...mean: IT IS OF THE ABSOLUTE MAX EFFORT AND QUALITY" | META |
| GT-SC2-07 | **Self-containment measure**: owner should NEVER need to leave current excerpt to look for references | "A good measure of the self-containment principle is that the owner SHOULD NEVER need to leave the excerpt" | SPEC |
| GT-SC2-08 | **Atom-by-atom definition demanded**: owner demands every term/concept be defined as single atom, with AskUserQuestion until solid for decades | "divide all aspects and terminologies into single atoms...NOT MOVE ON UNTIL YOU HAVE IT DOWN" | META |

**Duplicate check**: GT-SC2-01 extends EE-1 with concrete hadith-version danger. GT-SC2-03 strengthens GT-SC1-08. GT-SC2-05 new pipeline architecture concern.

---

## SC3 — Zero-Context & Security Gates

Owner chose: (strong criticism of current pipeline)
Raw file: 33 lines | Topic: Can you benefit from excerpt that starts mid-instruction?

### Ground Truth Atoms

| # | Atom | Verbatim Anchor | Disposition |
|---|------|-----------------|-------------|
| GT-SC3-01 | **Zero-context starting assumption REINFORCED**: assumptions about owner's pre-knowledge violate core principles; abundance > ambiguity | "ASSUME STUDY OF AN EXCERPT STARTS WITH 0 KNOWLEDGE AND CONTEXT BEFOREHAND" | FP |
| GT-SC3-02 | **Reference scope danger**: هذه الأفعال والأقوال may reference more than what's in the excerpt; reader misattributes scope | "I would assume هذه الأفعال والأقوال refers only to the latter ones, while in reality it references the text that came before" | SPEC |
| GT-SC3-03 | **Cross-excerpt duplication for shared references**: when ruling (وافعل هذه...) applies to multiple preceding excerpts, it must be duplicated to all | "the excerpts from the previous texts may miss the part...if it is not identified and copied to there as well" | SPEC |
| GT-SC3-04 | **Post-excerpting verification gate**: after excerpting, reassemble excerpts and analyze from owner's POV — "IS THIS PASSAGE CORRECTLY EXCERPTED AND READY?" | "AFTER EXCERPTING, the excerpts are pieced back together temporarily...then analyzed and researched" | SPEC |
| GT-SC3-05 | **Pipeline CATASTROPHICALLY LACKING security gates**: 5x repeated. Pipeline needs correction gates, 100% pass/refuse gates, deeper structures | "THE CURRENT PIPELINE IS CATASTOPHICALLY LACKING IN SECURITY GATES" (5 repetitions) | FP |
| GT-SC3-06 | **Context layer identification**: system must identify what context each excerpt sits in — is this the author's opinion? A quote? A refutation setup? | "IS THIS EVEN HIS OPINION, OR IS HE QUOTING SOMEONE ELSE?" | SPEC |

**Duplicate check**: GT-SC3-01 = GT-SC1-03 (same principle, different evidence). GT-SC3-04 new pipeline gate. GT-SC3-05 may become new FP.

---

## Cross-Bundle Themes (expected deduplication targets)

| Theme | Bundles | FP Candidate? |
|-------|---------|---------------|
| Excerpting is objective / no outside factors | G1, G3 | FP (extends FP-4) |
| Harmlessness gate for retention | G1, G3, G4 | SPEC rule |
| Multi-function identification | G2, G3 | SPEC rule |
| Zero pre-context assumption | SC1, SC2, SC3 | FP (strong candidate) |
| Self-containment = no manhunt | SC1, SC2 | FP (extends C-SC rules) |
| Teaching unit vocabulary | SC1 | META (vocabulary) |
| More pipeline security gates | SC2, SC3 | FP (strong candidate) |
| Author flow preservation | SC1, SC3 | FP (strong candidate) |
| Cross-topic placement freedom | G2, G3 | DEFERRED (taxonomy) |

---

## Validation Checklist (for agent reports)

For EACH agent report, verify:
- [ ] Every GT atom above appears in their extraction
- [ ] No ground truth atoms were missed
- [ ] Additional atoms from structured files (02_-15_) are reasonable extensions
- [ ] Zero-atom files are correctly marked STRUCTURAL
- [ ] Arabic text degradation scan was performed
- [ ] Deduplication against F-series atoms is noted
