# S-1 case dossier

## 1. Owner-faithful questionnaire judgment

### Current best owner-faithful ranking
1. making the excerpt useful to study from  
2. keeping the exact original text untouched  
3. making the excerpt understandable on its own  
4. making the excerpt the right size  

Status: **partly settled, partly conditional**

- `4 > 1` is strongly anchored in the raw reaction.  
  `(source_basis: explicit_draft; owner_relation: owner_explicit)`
- `2 > 3` is the strongest current forced ordering **under the ordinary reading of (2)**.  
  `(source_basis: explicit_draft; owner_relation: owner_explicit)`
- The tail is not fully clean because item (2) changes character if it means damaged text rather than recoverable context loss.  
  `(source_basis: explicit_draft; owner_relation: owner_explicit)`

### Strongest case for `4 > 1`
The raw reaction does not treat excerpts as ends in themselves. It treats them as parts of **teaching units**. That makes study usefulness the top-level objective.  
But the same raw reaction also treats source corruption and false attribution as catastrophic. So the correct reading is not “usefulness can override integrity.” The stronger reading is: **the system exists for study usefulness, but it must achieve that within the non-negotiable boundary of source integrity.**  
`(source_basis: explicit_draft; owner_relation: owner_explicit)`

## 2. Structural problem in the question itself

The four items are not clean peer criteria.

- Item **(4)** behaves like a **goal-level objective**.
- Item **(1)** behaves like a **hard integrity constraint**.
- Item **(2)** behaves like an interpretation-sensitive **self-containment / context pressure**.
- Item **(3)** behaves like a **granularity-fitness pressure**.

So the question forces a linear ranking over an architecture that is not naturally linear.  
`(source_basis: inferred_from_prior_chat; owner_relation: owner_consistent_inference)`

## 3. What is certain

- The owner clearly prioritizes **study usefulness** first.  
  `(source_basis: explicit_draft; owner_relation: owner_explicit)`
- The owner clearly treats **silent mutation / false attribution** as catastrophic.  
  `(source_basis: explicit_draft; owner_relation: owner_explicit)`
- The owner clearly distinguishes missing-context inconvenience from silent corruption.  
  `(source_basis: explicit_draft; owner_relation: owner_explicit)`
- The owner clearly sees oversized, poorly granulated excerpts as mentally scrambling.  
  `(source_basis: explicit_draft; owner_relation: owner_explicit)`

## 4. What is tentative

- Whether the final forced tail should remain `2 > 3` in all readings.  
  `(source_basis: explicit_draft; owner_relation: owner_explicit)`
- Whether the ranking is best represented as a pure list or as a conditional / mixed architecture.  
  `(source_basis: inferred_from_prior_chat; owner_relation: owner_consistent_inference)`

## 5. What is unresolved

- If item **(2)** is interpreted as actual destructive cutting or mutilation of meaning, should it leap above item **(1)**, merge with it, or remain below it?  
  `(source_basis: explicit_draft; owner_relation: owner_explicit)`
- Whether a production-facing spec should encode this as a **lexicographic system** (“maximize 4 within the hard boundary of 1”) rather than a plain ranking.  
  `(source_basis: model_expansion; owner_relation: model_only)`

## 6. Key distinctions that must not be flattened

### Raw source integrity vs external add-ons
The raw reaction only condemns corrupting or mutating the **source wording itself**. It does not condemn clearly separated metadata, context blocks, or other external aids.  
`(source_basis: inferred_from_prior_chat; owner_relation: owner_consistent_inference)`

### Understandable on its own: two readings
1. **Ordinary reading:** enough local completeness that the owner does not need to hunt manually.
2. **Dangerous reading:** pieces were cut out or meaning was damaged.

Those two readings do not deserve the same rank treatment.  
`(source_basis: explicit_draft; owner_relation: owner_explicit)`

### Right size
The raw reaction does not mean “small.” It means correct granularity, non-mixed topics, and non-scrambling presentation.  
`(source_basis: explicit_draft; owner_relation: owner_explicit)`

## 7. What would be reckless to flatten

- Flattening the question into four symmetric sliders.
- Interpreting “useful to study from” as permission to rewrite source wording.
- Treating “understandable on its own” as one stable category.
- Reducing “right size” to brevity.
- Pretending the last two ranks are as strongly fixed as the first two positions.

## 8. What would be reckless to automate blindly

- Any optimization pass that silently rewrites source text in the name of readability or usefulness.
- Any spec that fails to distinguish raw excerpt text from external support layers.
- Any evaluator that scores item (2) without disambiguating its reading.
- Any granularity metric based only on length rather than topic mixing and cognitive scrambling.
