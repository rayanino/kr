# DR Prompt — Source Lifecycle Model: Submissions, Sources, Works, and Editions Over Time

**Target:** ChatGPT DR (has repo access)
**Purpose:** Design the data model for how the library tracks the relationship between submissions, sources, works, and editions as the collection grows over time — including incremental volume submissions, edition supersession, and progressive completeness.

---

## Prompt for the owner to paste into ChatGPT DR:

I am building a personal Islamic scholarly library (خزانة ريان / KR) that processes Arabic books through a 7-engine pipeline. The source engine is the first engine — it receives uploaded files, analyzes them, and admits them into the library's collection.

The source engine spec is at `engines/source/spec/` in the repository at https://github.com/rayanino/kr on branch `clean-start`. Read these files for context:

1. `engines/source/spec/01-vocabulary/README.md` — current vocabulary (submission, source, work, edition)
2. `engines/source/spec/INDEX.yaml` — full 96-atom inventory
3. `engines/source/spec/10-pipeline/40-intake-analysis/REQ-SRC-0019.yaml` — work identification
4. `engines/source/spec/10-pipeline/40-intake-analysis/REQ-SRC-0036.yaml` — completeness analysis
5. `engines/source/spec/10-pipeline/40-intake-analysis/REQ-SRC-0038.yaml` — composite work detection
6. `engines/source/spec/10-pipeline/50-metadata-deliberation/REQ-SRC-0026.yaml` — work identity output
7. `engines/source/spec/10-pipeline/50-metadata-deliberation/REQ-SRC-0039.yaml` — work-to-work relationships
8. `engines/source/spec/10-pipeline/60-source-admission-and-normalization-handoff/REQ-SRC-0025.yaml` — two-stage admission
9. `engines/source/spec/30-architecture/decisions/DEC-SRC-0014.yaml` — raw upload vs official collection
10. `engines/source/CLAUDE.md` — engine state

## The Problem

The current spec treats each submission as an isolated event: file arrives → analyze → admit → hand off. But a real library collection evolves over time. The spec has no model for:

### Edge Case 1: Incremental volume submission
The owner submits volume 1 of صحيح مسلم today. Next week, he submits volumes 2 and 3. The library now has 3 separate submissions that are ONE work. How should they merge into a single logical source? Who triggers the merge — the owner explicitly, or the library automatically when it detects that new submissions match an existing work? What happens to the completeness assessment (was "partial," now "less partial," eventually "complete")?

### Edge Case 2: Duplicate volume from a different edition
The library already has all volumes of سنن الترمذي from a concatenated PDF. The owner submits volume 5 separately — same work, but maybe a different tahqiq (critical edition). Is this a duplicate to reject? A parallel edition to keep alongside? A replacement? How does the library decide?

### Edge Case 3: Mixed-edition volumes
The owner submits volume 1 from تحقيق الأرناؤوط and volume 2 from تحقيق someone else. Same work, different muhaqiqs. Should the library warn? Accept both as separate editions? Refuse to merge them into one logical source?

### Edge Case 4: Supersession
The owner submits a low-quality PDF of a book. The library processes it through all 7 engines, generating teaching units. Later, the owner submits a better edition (better tahqiq, cleaner text). What happens? Does the new edition replace the old one? Are the teaching units regenerated? Do both editions coexist?

### Edge Case 5: Partial volume of an already-complete work
The library has the complete work (all volumes). The owner submits one volume from a different edition. This isn't completing a partial set — it's adding an alternative version of something already complete.

### Edge Case 6: Composite work evolution
The library has مجموع فتاوى ابن تيمية as a single 37-volume PDF. The owner later finds and submits individual risalahs from within the majmu' as separate, better-edited standalone editions. The library now has both the composite and individual components.

## What I Need

1. **A data model** that correctly represents the relationships between:
   - Submission (the upload event — ephemeral)
   - Source (the frozen file — immutable)
   - Volume (a physical unit within a multi-volume work)
   - Work (the bibliographic entity — abstract)
   - Edition (a specific realization of a work — tied to a publisher/muhaqiq)
   - Collection entry (the library's official record of what it holds)

2. **Lifecycle state machine** — How does a source's status evolve as related submissions arrive? What states exist (partial, complete, superseded, parallel-edition)?

3. **Merge and split rules** — When should the library automatically merge submissions into one work? When should it ask the owner? When should it keep them separate?

4. **Supersession model** — What happens to downstream pipeline artifacts when a source is superseded? Are teaching units regenerated? Is the old edition archived or deleted?

5. **Progressive completeness** — How does completeness_status evolve as volumes arrive over time? Where is this tracked — at the work level or the source level?

6. **Relevant models from library science** — How do FRBR (Functional Requirements for Bibliographic Records), IFLA LRM (Library Reference Model), and digital repository systems (Fedora, DSpace) handle these cases? What can we borrow? What doesn't apply to Islamic scholarly collections specifically?

7. **Islamic scholarly collection practices** — How do traditional Islamic libraries (مكتبات, خزائن) track multi-volume works, edition variants, and composite collections? What terminology and concepts from the Islamic bibliographic tradition (فهارس, ثبت, برنامج) apply?

Please provide: (a) a recommended data model with entity-relationship diagram, (b) a lifecycle state machine with transitions, (c) concrete resolution for each of the 6 edge cases above, and (d) what the source engine spec needs to add or change to support this model.
