# SC2 Case Dossier

## Purpose and scope

This dossier records SC2 as a questionnaire-side edge-case collection. It is not promoted doctrine. Its job is to preserve two distinct layers:

- **Owner-faithful questionnaire layer**: the owner can partially benefit from the excerpt, but that still does not make the design acceptable.
- **Engineering / protocol layer**: the case reveals a major structural issue around explained↔explanation linkage, proof proximity, version mismatch, passage analysis, and self-containment without manhunt.

## Core assessment thesis

This is a classic explained↔explanation linkage failure. The current excerpt is not worthless, but it is unsafe as a study unit unless the previous hadith is recoverable in exact, low-friction, source-accurate form. The right answer is not “the excerpt teaches nothing,” but also not “it is fine because the owner can infer the earlier hadith.” The strongest owner-faithful reading is: **partial benefit exists, but that is still unacceptable design; the library must automatically recover and link the referenced hadith.**

## Partial benefit vs acceptable design

The excerpt can still teach isolated pieces of information. That is why answer B is too strong as the final questionnaire choice. But the case is still structurally bad enough that answer A is impossible. The crucial distinction is:

- **partial benefit** = some information can still be learned
- **acceptable design** = the owner can study with peace, certainty, and no manhunt

SC2 fails the second even if it partially satisfies the first.

## Why this is a classic explained↔explanation linkage failure

The current excerpt is commentary that repeatedly references “the previous hadith.” That means the explanation is not self-standing in the way a fresh independent text would be. It is built on an already-known proof context. In the original book, that is safe because the author expects sequential reading and immediate access to the earlier hadith. In an excerpt-library, that safety disappears unless the pipeline restores it.

## Exact linkage requirement doctrine

For this case, linkage must be:

- **exact**, not generic
- **version-aware**, not merely hadith-name aware
- **low-friction**, not a search task
- **nearby**, not permanently on screen but readily accessible
- **documented**, not left to owner memory

A weak linkage is not a small inconvenience. It changes what proof the explanation is perceived to be explaining.

## Study-chunk flow and proof proximity

The owner’s described study flow is:

1. skim the whole thing first
2. go chunk by chunk
3. read explanation
4. check the proof it is talking about
5. return to the explanation and master that chunk
6. repeat with active recall

That study flow directly depends on proof proximity. If the proof is not available nearby, the chunk-by-chunk process breaks or degrades into guesswork.

## Variant-mismatch catastrophe risk

The owner explicitly flags a severe danger: a scholar may be explaining one wording/version of a hadith while the owner, if forced to search manually, may retrieve another version under the same broad hadith identity. That can scramble knowledge because:

- the explanation becomes wrongly attached to the wrong wording
- subtle wording differences can change interpretation
- the owner may not realize the mismatch at all

This is not merely a reference convenience issue. It is a knowledge-integrity issue.

## Why “just note earlier material exists” is too weak

A bare note that earlier material exists still leaves the owner with the real problem:

- what exactly is the earlier material?
- which hadith is it?
- which wording/version is it?
- where is it?
- is it the exact version the scholar is explaining?

That means note-only support still causes manhunt, and manhunt is itself both a study-cost problem and an error-introduction risk.

## Passage-analysis-stage gap

The owner identifies a missing pipeline stage: after passage selection but before excerpting, the passage should be deeply scanned for:

- intra-passage and inter-passage dependencies
- reference-back targets
- exact proof/version binding
- places where explanation is unusable without linked proof access
- contexts where the engine should refuse to produce a “self-contained” excerpt without compensating linkage

Without that stage, the pipeline can produce locally readable fragments that are globally unsafe.

## Self-containment without manhunt

SC2 sharpens a stricter reading of self-containment:

- the owner should not need to leave the excerpt and search manually
- close-proximity reference is compatible with self-containment
- blind isolation is not the goal
- “I can probably figure it out” is not acceptable

So self-containment here means **the excerpt has everything needed in immediate reachable support**, not that the excerpt must be a blind text-only island.

## What would be reckless to flatten

It would be reckless to flatten SC2 into any of the following:

- “the excerpt is fine because it still teaches something”
- “the excerpt is unusable because it teaches nothing”
- “a note that earlier material exists is enough”
- “cross-reference is a nice-to-have”
- “owner memory can bridge the gap”

## What would be reckless to automate blindly

It would be reckless to automate any rule that:

- separates explanation from explained proof without exact linkage
- assumes hadith identity is obvious enough from broad labels
- uses note-only recovery where version-specific linkage is required
- skips passage-level dependency analysis
- treats partial benefit as sufficient evidence of safe design
