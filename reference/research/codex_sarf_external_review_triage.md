# Sarf External Review Triage

## Current Sarf Review State

- The current architect draft exists at `reference/research/sarf_v2_0_draft.yaml`.
- ChatGPT Phase 2 comparison is complete and was integrated into the draft through the architect post-Phase-2 revision pass.
- Gemini clean interim adversarial review is complete and has now been triaged against the current post-Phase-2 draft.
- Claude return review is still pending and remains mandatory before any final merge or installation step.

## ChatGPT Phase 2 — Accepted Corrections

The following ChatGPT Phase 2 corrections were accepted and already integrated into `reference/research/sarf_v2_0_draft.yaml`:

- made `الإلحاق` explicit as a topic-family
- tightened hamza-family scoping
- enforced formation-only framing on the high-risk noun-transformation topics
- reduced over-granulation in `معاني صيغ الزيادة`
- added `الزيادة بالتضعيف`
- added `أحكام الإسناد في المعتل والمضعف`
- resolved the `قياسي/سماعي` modeling question by adding a compact apparatus-side family rather than a full new top-level branch
- extended `عدد الأصول في الكلمة` to include `الثنائي`

The following ChatGPT suggestions were not accepted as direct tree changes:

- splitting `التقاء الساكنين`
- adding `التذكير والتأنيث`
- adding `السداسي`

## Gemini Clean Review — Triage

### Already Addressed

- make `الإلحاق` explicit as a topic-family
- tighten hamza-family scoping
- enforce formation-only policy on the high-risk noun-transformation topics
- reduce over-granulation in `معاني صيغ الزيادة`
- add `الزيادة بالتضعيف`
- add `أحكام الإسناد في المعتل والمضعف`
- resolve the `قياس/سماع` modeling question
- extend `عدد الأصول في الكلمة` to include `الثنائي`

### Actionable Later

- `أبنية الأسماء > الاسم المزيد` may still be too broad and may need splitting into finer noun-pattern subfamilies
- `التقاء الساكنين` may later deserve one more internal split if the Claude return review finds that the current leaf is still too coarse
- `الإلحاق` may still be slightly under-specified even after its explicit recovery
- `القياسي والسماعي في الصرف` may still need a final judgment on whether its current compact modeling is sufficient

### Overreaching / Rejected

- the claim that the current draft still contains broad fatal nahw leakage in `اللزوم والتعدية` and the derived-noun families
- the claim that the current draft still contains broad imlaa leakage through `الهمزة المتوسطة/المتطرفة` and `قوة الحركات`
- the demand to explode `أبنية الأسماء` into exhaustive `10/5/4` terminal pattern leaves
- the proposal to re-architect the tree around a root-based universal parent model to resolve the `المصدر` vs `الفعل` theoretical dispute
- the claim that the current sound-plural branch logic remains structurally invalid as written

### Caution Only

- possible future reconsideration of `التذكير والتأنيث`
- possible future addition of `السداسي`
- continued monitoring of the hamza zone as the most boundary-sensitive morphophonemic area
- continued monitoring of `التقاء الساكنين` as a narrow but boundary-fragile topic

## Current Blocking Status

At the architect triage stage, no blocking issue remains that must be patched **before** the Claude return review.

This does **not** mean the sarf tree is final.
It means the current draft is stable enough to proceed to the mandatory Claude return review without another pre-review patch cycle.

## Outstanding Question For Claude

Claude must explicitly judge the following unresolved question:

- should `أبنية الأسماء > الاسم المزيد` remain one leaf
- or should it split into finer noun-pattern subfamilies without over-granulating the noun-pattern branch

This is the main live structural question carried forward from the Gemini triage.

## Protocol Status

- Sarf is paused pending the mandatory Claude return review.
- Gemini did not replace Claude authority and did not replace the required Claude return review.
- No installation into `library/sciences/sarf/tree.yaml` has occurred.
- No final merge claim has been made.

