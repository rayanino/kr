# Where The Owner Touches The System

This page does not show code or internal architecture. It shows the places where the owner matters in the life of one book.

```mermaid
flowchart LR
    source["Source"]
    normalization["Normalization"]
    passaging["Passaging"]
    atomization["Atomization"]
    excerpting["Excerpting"]
    taxonomy["Taxonomy"]
    synthesis["Synthesis"]

    source --> normalization --> passaging --> atomization --> excerpting --> taxonomy --> synthesis

    gate_source["Human gate<br/>Owner approval for serious source-level decisions"]
    gate_norm["Human gate<br/>Owner approval if normalization reaches a decision that should not be forced"]
    gate_excerpt["Owner review<br/>Excerpt reviewer opens and records accept / needs work / reject"]
    gate_tax["Human gate<br/>Owner review when taxonomy placement or tree-level judgment should not be forced"]

    quality_checks["Quality gates<br/>System checks for structure, integrity, coverage, and obvious mechanical errors"]
    feedback_loop["Owner feedback loop<br/>Feedback is saved and later used to improve future runs"]

    gate_source -.-> source
    gate_norm -.-> normalization
    gate_excerpt -.-> excerpting
    gate_tax -.-> taxonomy

    quality_checks -.-> normalization
    quality_checks -.-> excerpting
    quality_checks -.-> taxonomy

    gate_excerpt --> feedback_loop
    feedback_loop -.-> excerpting
```

## What these touchpoints mean

- `Human gates` are approval checkpoints. KR uses them when a decision is too important to auto-accept.
- `Owner review` is the practical touchpoint the owner is most likely to feel: the excerpt reviewer opens, the owner reacts to individual excerpts, and those reactions are saved.
- `Quality gates` are system-side review points. They are not owner decisions. They are the system checking whether structure, references, and outputs still make sense before moving on.

## The owner's most direct interaction

Today, the clearest owner-facing surface is excerpt review:

- KR opens the excerpt reviewer.
- The owner reads one excerpt at a time.
- The owner marks it as `accept`, `needs work`, or `reject`.
- KR saves that reaction as feedback for future improvement.

## A useful mental model

- The owner is not expected to debug the system.
- The owner is expected to react when KR asks, "Does this result make sense to you?"
- KR should use those reactions at the touchpoints above instead of making irreversible decisions silently.

## Where these touchpoints live in the repo

- Human gate records live under `library/gates/`.
- Owner excerpt feedback is written by the review tool into `owner_feedback.jsonl`.
- Quality checks are run by validation and evaluation tools before work is treated as trustworthy.
