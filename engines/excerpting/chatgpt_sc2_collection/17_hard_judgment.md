# Hard Judgment

## Owner-faithful judgment

**Final questionnaire choice: C.**

This is the strongest owner-faithful answer because:

- **A** is too weak. The owner does not consider this safe just because some information can still be extracted.
- **B** is too strong in a narrow literal sense, because the owner explicitly admits that partial benefit is still possible in some cases.
- **C** best preserves the tension: yes, partial following is possible, but the library should automatically show the linked hadith.

The deepest tension in the raw comments is this: **partial benefit exists, but partial benefit is still unacceptable design**.

The strongest owner-faithful interpretation is therefore:
- I can sometimes follow some of it.
- That does not make it good.
- I need the previous hadith in exact, close, reliable reach.
- Simply noting that earlier material exists is not enough.

### Most important explained↔explanation linkage insight
The explanation and the proof it explains must remain tightly linked, especially when the explanation is tailored to one particular hadith wording/version.

### Most important proof-proximity insight
The owner does not need the proof to block vision permanently, but he does need it in low-friction, nearby, exact reach.

### Most important variant-mismatch insight
If the owner is forced to look up a different version of the hadith than the one the scholar was explaining, knowledge can scramble catastrophically.

### Most important pipeline-gap insight
The pipeline is missing a passage-analysis stage that should detect reference-back dependencies and required linkage before excerpting.

### What would be reckless to ignore
- owner memory is not a safe reference mechanism
- note-only support is not enough
- partial benefit is not acceptable design
- version mismatch can be catastrophic

### What would be reckless to automate blindly
- separating explanation from proof without exact binding
- generic hadith links instead of exact linked versions
- skipping dependency analysis and hoping the owner compensates manually

## Broader engineering / protocol judgment

SC2 is not a minor cross-reference convenience issue. It is a structural failure mode. A pipeline that produces commentary excerpts with repeated reference-back language but without exact proof linkage is building in:

- manhunt
- undocumented mental recovery
- version mismatch
- false confidence
- study-flow breakage

That combination is severe enough that it should be treated as a first-class protocol risk, not as optional UX improvement.
