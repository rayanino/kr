# Purpose and scope

This artifact captures the F8 assessment as **collection material**, not promoted doctrine. It separates:
- the owner-faithful questionnaire answer
- the broader engineering / red-team expansion needed to reason about the failure surface

# Explicit layer separation

## Owner-faithful questionnaire layer
This layer answers the questionnaire honestly from the owner's point of view.

## Expanded engineering / red-team layer
This layer expands the comparison into stage analysis, guidance boundaries, failure families, scenarios, thresholds, and tests.

The two layers are intentionally not the same.

# Core assessment thesis

The real issue is not simply “premature structure” versus “structurelessness.” The deeper issue is **stage contamination**: where structure is permitted to guide the pipeline, and where it must be banned.

The owner’s hierarchy is:

1. Most dangerous overall: excerpt corruption / knowledge corruption.
2. Especially dangerous: taxonomy-biased excerpting.
3. Therefore excerpting must be invariant under tree granulation changes.
4. Only after excerpting is protected do placement failures get compared.
5. Within that narrower comparison, overgranulation is more dangerous than undergranulation.
6. Therefore the correct questionnaire choice is `C`.

# Why the question cannot be answered well without separating stages

If stages are collapsed together, the answer becomes flat and misleading.

## Excerpting stage
This is where the highest danger sits. If structure influences excerpt cuts, grouping, or atom integrity, the system becomes unsafe at the knowledge layer.

## Taxonomy-placement stage
This matters, but only after excerpting is frozen correctly. Here the question becomes which placement failure is more dangerous and more repairable.

## Study-use stage
This is where the user experiences the damage. At this stage, visible misplacement may still be repairable, while silent excerpt corruption may already have poisoned study and memory.

# Stage-by-stage analysis

## Excerpting stage

### Main danger
Taxonomy guidance contaminates excerpt integrity.

### Why this is worst
A silent corruption here poisons everything downstream:
- placement
- titles
- relationships
- study
- memorization
- future trust

### Engineering consequence
Excerpting must be source-governed, not taxonomy-governed.

## Taxonomy-placement stage

### Main danger once excerpting is protected
Overgranulated placement is more dangerous than undergranulated placement.

### Why
Undergranulation usually presents a detectable repair problem:
- the user sees multiple real topics living together
- the missing split is easier to imagine

Overgranulation presents a harder repair problem:
- the user must reconstruct the common denominator of fragments
- the science may look more fractured than it is
- cognitive repair is harder

## Study-use stage

### Main danger
Confusing visible structural awkwardness with invisible knowledge corruption.

### Why
A visible misplacement may irritate or mislead, but still leave excerpt truth recoverable.
Silent excerpt corruption may leave study smooth while poisoning the content itself.

# Choice analysis

## Strongest case for A
If prior structure enters too early, it can:
- force texts into the wrong boxes
- bias excerpt grouping
- import premature assumptions
- create tidy-looking but corrupted outputs

This is the strongest argument inside the question frame for worrying more about premature structure.

## Strongest case for B
If the system works blind, it can:
- become inconsistent
- miss real distinctions
- produce unstable boundaries across similar passages
- feel chaotic and under-disciplined

This is the strongest argument inside the question frame for worrying more about structurelessness.

## Strongest case for C
The real issue is not the mere existence of structure. The real issue is **where guidance may and may not be used**.
- guidance that helps placement and navigation can be beneficial
- guidance that influences excerpt truth is corrupting
- therefore the comparison must be stage-bounded

## Final judgment
`C` is the correct questionnaire choice.

Not because A and B are equally dangerous.
Not because the owner is undecided.
But because the real assessment is hierarchical:
- overall danger = excerpt corruption / stage contamination
- narrower placement danger = overgranulation > undergranulation

# Silent corruption vs visible misplacement doctrine

## Silent corruption
Harder to detect, more trust-destroying, and more globally poisonous.

## Visible misplacement
Still severe, but usually more detectable and more recoverable.

These two must not be treated as equivalent severity classes.

# Excerpting-independence doctrine

The rightful excerpt output should stay the same across:
- correctly granulated tree
- undergranulated tree
- overgranulated tree

If excerpt output changes merely because the tree changed, structure has entered the wrong stage.

# Guidance-boundary doctrine

Guidance may help:
- placement
- ranking inside the already-correct structure
- study navigation
- presentation

Guidance must not be allowed to:
- alter rightful excerpt boundaries
- rewrite excerpt grouping to fit current leaves
- suppress source-governed atoms because they do not fit the current tree

# Overgranulation vs undergranulation doctrine

## Why overgranulation may be harder to repair
- fragments force reassembly
- the common denominator becomes a puzzle
- the science can look falsely more divided than it is

## Why undergranulation may be easier to detect
- distinct topics remain visible in one place
- the user can see a missing split
- the repair direction is clearer: cut deeper

# What would be catastrophic
- taxonomy-guided excerpt corruption
- excerpt output changing across tree granularities
- silent corruption discovered after long study

# What would be severe but survivable
- visible wrong placement with excerpt truth intact
- blind inconsistency that is caught before trust fully transfers
- undergranulation that is annoying but still legible

# What would be disappointing but repairable
- undergranulated grouping where the missing split is obvious
- visible awkward placement that does not corrupt content

# What would be reckless to collapse together
- excerpt corruption vs wrong leaf placement
- overgranulation vs undergranulation
- guidance for placement vs guidance for excerpting
- visible errors vs silent errors
- repairable study friction vs knowledge corruption
