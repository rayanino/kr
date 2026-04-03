# Sarf Architect Post-Phase-2 Revision

Source: raw SARF_ARCHITECT response after integrating ChatGPT Phase 2 corrections, relayed by the owner.

Modified reference/research/sarf_v2_0_draft.yaml and integrated the accepted Phase 2 corrections. I did a focused verification pass after the edits rather than a full new Step 9:

- YAML parses cleanly
- leaf_count now matches computed total
- no duplicate IDs
- no invalid IDs
- no direct grep hits for blocked nahw/imlaa topic labels beyond benign occurrences like اسم الفاعل

## Phase 2 Assessment

| Recommendation | Disposition | Reason |
|---|---|---|
| Make الإلحاق explicit as a topic-family | accept | The draft was under-explicit here, and the external comparison is right that scattered mentions were not enough. |
| Tighten hamza-family scoping | accept | The draft had two plausible hamza destinations; consolidating scoping reduces duplicate encyclopedic paths and imlaa drift risk. |
| Enforce formation-only policy on the high-risk noun-transformation leaves | accept | This is a boundary safeguard, not optional styling. |
| Reduce over-granulation in معاني صيغ الزيادة | accept | The external comparison is right that the seven-leaf split was too knowledge-heavy relative to sparse corpus support. |
| Add الزيادة بالتضعيف | accept | It improves the apparatus layer without causing bleed. |
| Add أحكام الإسناد في المعتل والمضعف | accept | This stabilizes الإسناد الصرفي and prevents exception material from being scattered ad hoc. |
| Resolve the قياس/سماع modeling question | partially accept | I added a compact L2 family under the apparatus branch, but not a full top-level branch. |
| Extend عدد الأصول في الكلمة to include الثنائي (and maybe السداسي) | partially accept | I added الثنائي; I did not add السداسي because the evidence is weaker and it risks over-extending the branch. |
| Optionally split التقاء الساكنين | reject | Corpus support is thin and the boundary risk toward phonetics / performance remains too high for further splitting. |
| Consider التذكير والتأنيث | reject | Still too weakly grounded in the retained corpus and too liable to drift into semantic / syntactic territory. |

## Post-Phase-2 Revision Report

### A. Accepted Phase 2 Corrections

- Added an explicit L2 family الإلحاق under الأبنية والأصول والميزان with:
    - تعريف الإلحاق
    - الإلحاق في الأبنية
    - الفرق بين الإلحاق والزيادة
- Replaced the old الزيادة للإلحاق leaf under الأصل والزائد with الزيادة بالتضعيف.
- Added a compact L2 family القياسي والسماعي في الصرف with:
    - القياسي في الصرف
    - السماعي في الصرف
    - الشاذ في الصرف
- Extended عدد الأصول في الكلمة by adding الكلمة الثنائية.
- Compressed معاني صيغ الزيادة from a seven-leaf container into one stable leaf.
- Added أحكام الإسناد في المعتل والمضعف under الإسناد الصرفي.
- Tightened the high-risk noun-transformation titles to:
    - المثنى من جهة الصياغة
    - جمع المذكر السالم من جهة الصياغة
    - جمع المؤنث السالم من جهة الصياغة
- Tightened the hamza family by:
    - removing إبدال الهمزة from الإبدال
    - renaming the broad hamza leaf to أحكام الهمزة في البنية الصرفية

### B. Rejected Or Partially Rejected Corrections

- Resolve the قياس/سماع modeling question
    - partially accept
    - Reason: a compact apparatus-side family is enough; a full principles branch would over-correct the architecture.
- Extend عدد الأصول ... and maybe السداسي
    - partially accept
    - Reason: الثنائي is defensible; السداسي remains too peripheral for this draft state.
- Optionally split التقاء الساكنين
    - reject
    - Reason: thin corpus signal plus elevated phonetics/performance bleed risk.
- Consider التذكير والتأنيث
    - reject
    - Reason: not strong enough in the sparse retained corpus and still too drift-prone.

### C. Revised Draft Summary

- Total leaf count: 152
- Per-Level-1 branch leaf counts:
    - مدخل علم الصرف وحدوده: 8
    - الأبنية والأصول والميزان: 26
    - تصريف الأفعال وأبنيتها: 40
    - المصادر والمشتقات والأسماء المأخوذة من الأفعال: 32
    - التحويلات والأصناف الاسمية الصرفية: 32
    - التغيرات الصرفية الداخلية: 14
- Branches whose architecture materially changed:
    - الأبنية والأصول والميزان
        - added الإلحاق
        - added القياسي والسماعي في الصرف
        - added الكلمة الثنائية
        - replaced الزيادة للإلحاق with الزيادة بالتضعيف
    - تصريف الأفعال وأبنيتها
        - compressed معاني صيغ الزيادة
        - expanded الإسناد الصرفي
    - التحويلات والأصناف الاسمية الصرفية
        - tightened boundary-facing L2 wording
    - التغيرات الصرفية الداخلية
        - consolidated hamza handling

### D. Remaining Risk Register

- القياسي والسماعي في الصرف may still be challenged in review as either too small or still too implicit.
- الإلحاق is now explicit, but Fresh Claude should test whether the three-leaf treatment is sufficient or still under-specified.
- معاني صيغ الزيادة is now intentionally compressed; adversarial review should test whether this is correctly disciplined or slightly under-granulated.
- أحكام الهمزة في البنية الصرفية remains the most boundary-sensitive morphophonemic topic.
- التقاء الساكنين remains a fragile narrowed leaf because it sits close to phonetics / recitation bleed.
- The narrowed noun-transformation topics remain the main nahw-collision zone even after retitling.

### E. Phase 3 Readiness Verdict

READY FOR EXTERNAL ADVERSARIAL REVIEW

The accepted Phase 2 corrections are now integrated into the draft, and the focused post-patch verification passed. I did not run a full new Step 9 because the edits were targeted and did not reopen the core branch architecture.
