Scope note: the ledger explicitly labels 12 B2/B3 atoms, not 15. Its `B3 = 10 MAQ atoms` count includes `1 merged` and `2 deferred` MAQs that are not given `B3-*` IDs in the register, so I am reviewing the 12 explicitly named atoms rather than inventing IDs.

ATOM: B2-P1  
VERDICT: NEEDS-REVISION  
EVIDENCE: Prompt: “Do not classify by surface language alone… genuinely introductory … only when it (a) contains no independent ruling, definition, or evidence” [phase2_classify.py](/C:/Users/Rayane/Desktop/kr/engines/excerpting/src/phase2_classify.py#L61C1). SPEC §5.2.2 still presents “The full prompt text” without this rule [SPEC.md](/C:/Users/Rayane/Desktop/kr/engines/excerpting/SPEC.md#L893C1).  
CROSS-RULE RISK: Mixed intro+ruling openings can trigger both B2-P1 and B3-P2, but no tie-breaker says whether the passage is a scoped introduction or a substantive rule unit.  
EDGE CASE: `مقدمة` or `فصل` followed immediately by `الأصل في الأبضاع التحريم`.  
RECOMMENDATION: Copy the exact B2-P1 paragraph from [phase2_classify.py](/C:/Users/Rayane/Desktop/kr/engines/excerpting/src/phase2_classify.py#L61C1) into SPEC §5.2.2 after the segment-boundary rules.

ATOM: B2-P2  
VERDICT: NEEDS-REVISION  
EVIDENCE: Prompt and FP-3 align on “≤15% of the unit, maximum ~30 words” and “Apply at most once per teaching unit” [phase2_group.py](/C:/Users/Rayane/Desktop/kr/engines/excerpting/src/phase2_group.py#L69C1), [SPEC.md](/C:/Users/Rayane/Desktop/kr/engines/excerpting/SPEC.md#L38C1). The rule is coherent, but unlike MV-1, the threshold is not empirically justified in the SPEC.  
CROSS-RULE RISK: Direct collision with B3-P1: a 14% carryover at a real function boundary is retained by B2-P2 but split by B3-P1.  
EDGE CASE: A new refutation unit opening with `فإن قيل` or `لأنه` after a genuine boundary.  
RECOMMENDATION: Replace the hard cutoff with: “FORGIVING RETENTION: … Normally this is ≤15% of the unit and roughly ≤30 Arabic words, but these are heuristics, not override conditions. Preserve only the minimum carryover needed to avoid an orphaned causal start.”

ATOM: B2-P3  
VERDICT: CONFIRM  
EVIDENCE: Prompt: “Retain the chapter/section title … when … the title carries scholarly content the text does not repeat” [phase2_group.py](/C:/Users/Rayane/Desktop/kr/engines/excerpting/src/phase2_group.py#L77C1). FP-3 matches this almost verbatim and explicitly cites Bukhari tarajim as the counterexample [SPEC.md](/C:/Users/Rayane/Desktop/kr/engines/excerpting/SPEC.md#L38C1).  
CROSS-RULE RISK: Minor duplication pressure if the same fiqhi title must anchor multiple units, but “per-unit, not global” is the correct limiter.  
EDGE CASE: Nested generic headings like `فصل` inside a meaningful `باب`, where `هذا الباب` may refer to the nearer or farther title.  
RECOMMENDATION: None.

ATOM: B2-P4  
VERDICT: CHALLENGE  
EVIDENCE: Ledger disposition says “Question-cluster methodology: ‘what question does each segment answer?’” [FOUNDATIONS_HARDENING_LEDGER.md](/C:/Users/Rayane/Desktop/kr/engines/excerpting/reference/FOUNDATIONS_HARDENING_LEDGER.md#L56C1), but the live prompt only says phase 3 “MAY be a separate unit when it answers a different question” [phase2_group.py](/C:/Users/Rayane/Desktop/kr/engines/excerpting/src/phase2_group.py#L91C1); there is no general dependency-first/question-cluster rule in SPEC §5.3.2.  
CROSS-RULE RISK: Without an explicit question-cluster tie-breaker, B3-P1 can split multi-function passages that still answer one scholarly question.  
EDGE CASE: An usul passage defining `العام`, stating its ruling, and giving its operative example in one reasoning arc.  
RECOMMENDATION: Add this exact rule to prompt and SPEC: “DEPENDENCY-FIRST / QUESTION-CLUSTER: Before splitting, ask what question each segment answers. Segments that jointly answer one scholarly question stay together even if their surface functions differ. Split only when a segment begins answering a genuinely different question.”

ATOM: B2-SP  
VERDICT: CONFIRM  
EVIDENCE: FP-18 explicitly distinguishes “acceptable excerpt” from “directly study-ready excerpt” and says “A teaching unit can carry usable theory while still failing direct study-readiness” [SPEC.md](/C:/Users/Rayane/Desktop/kr/engines/excerpting/SPEC.md#L69C1). That matches the ledger’s “two-layer model (theory + context) … documented” disposition [FOUNDATIONS_HARDENING_LEDGER.md](/C:/Users/Rayane/Desktop/kr/engines/excerpting/reference/FOUNDATIONS_HARDENING_LEDGER.md#L57C1).  
CROSS-RULE RISK: The current `FULL/PARTIAL/DEPENDENT` contract still conflates “acceptable” and “study-ready,” so downstream readers may over-trust `FULL`.  
EDGE CASE: Units like `الشرط الثالث` or `وهو الصحيح` that are coherent enough to be usable but not clean entry points.  
RECOMMENDATION: None.

ATOM: B3-P1  
VERDICT: NEEDS-REVISION  
EVIDENCE: Prompt: “when each function is substantive (>20% of text), they are separate teaching units” [phase2_group.py](/C:/Users/Rayane/Desktop/kr/engines/excerpting/src/phase2_group.py#L82C1). But FP-13 says granularity is lowest priority, and FP-9 warns overgranulation is more dangerous than undergranulation [SPEC.md](/C:/Users/Rayane/Desktop/kr/engines/excerpting/SPEC.md#L58C1), [SPEC.md](/C:/Users/Rayane/Desktop/kr/engines/excerpting/SPEC.md#L50C1).  
CROSS-RULE RISK: Conflicts with EE-1, B2-P4, and B2-P2 whenever a single reasoning arc contains multiple substantive functions.  
EDGE CASE: `الأصل` + ruling + proof-overview in one tightly coupled usul paragraph, where each function exceeds 20% but none stands well alone.  
RECOMMENDATION: Replace the cutoff sentence with: “MULTI-FUNCTION SPLIT: A passage containing multiple functions should be split only when the functions are each developed enough to teach independently. Treat ‘>20% of text’ as a weak heuristic, not an automatic cutoff. If the segments still answer one scholarly question, keep them together.”

ATOM: B3-P2  
VERDICT: NEEDS-REVISION  
EVIDENCE: Prompt: “A chapter-specific intro applies only to this source’s chapter; treating it as a universal topic introduction creates scope mismatch” [phase2_group.py](/C:/Users/Rayane/Desktop/kr/engines/excerpting/src/phase2_group.py#L87C1). I found no formal SPEC section encoding that rule.  
CROSS-RULE RISK: Overlaps with B2-P1 on mixed openings that are both an intro and a substantive rule statement.  
EDGE CASE: `هذا الباب يذكر فيه التيمم، وهو بدل عن الوضوء عند فقد الماء` where the intro frame and ruling are fused.  
RECOMMENDATION: Add to SPEC §5.3.2 and §6: “INTRODUCTION SCOPE: Distinguish chapter-specific introductions from full-topic introductions. A chapter-specific introduction applies only to this source’s chapter and must not be treated as a universal introduction unless the text itself defines the topic at that broader level.”

ATOM: B3-P3  
VERDICT: NEEDS-REVISION  
EVIDENCE: Prompt: “Phases 1+2 belong together … Phase 3 (refutations/ردود) MAY be a separate unit when it answers a different question” [phase2_group.py](/C:/Users/Rayane/Desktop/kr/engines/excerpting/src/phase2_group.py#L91C1). FP-8 supports function distinction, but there is no formal SPEC section governing this proof-structure split [SPEC.md](/C:/Users/Rayane/Desktop/kr/engines/excerpting/SPEC.md#L48C1).  
CROSS-RULE RISK: Can collide with FP-14/15 if the “phase 3” material is actually the answer that keeps the objection from being misattributed.  
EDGE CASE: `احتجوا بحديث ... والجواب عنه ...` where explanation and refutation are inseparable in one dialectical chain.  
RECOMMENDATION: Add: “PROOF STRUCTURE: When a scholar presents (1) proof, (2) explanation, (3) defense/refutation, phases 1+2 stay together by default. Phase 3 is separate only when it answers a distinct scholarly question and can stand without hiding speaker role, quoted voice, or the objection being answered.”

ATOM: B3-SP1  
VERDICT: CHALLENGE  
EVIDENCE: Ledger says this is “SPEC-ONLY” and “Links to FP-14/15” [FOUNDATIONS_HARDENING_LEDGER.md](/C:/Users/Rayane/Desktop/kr/engines/excerpting/reference/FOUNDATIONS_HARDENING_LEDGER.md#L62C1). The closest SPEC text is LA-1/LA-2 plus `quoted_scholars`, e.g. “If ≥80% … attribute the unit to that layer’s author” and relation labels like `quoted_opinion` / `refuted_position` [SPEC.md](/C:/Users/Rayane/Desktop/kr/engines/excerpting/SPEC.md#L1401C1), [SPEC.md](/C:/Users/Rayane/Desktop/kr/engines/excerpting/SPEC.md#L1409C1). That is not a scholar-quoting-scholar protocol.  
CROSS-RULE RISK: High. LA-1’s 80% dominant-layer rule can flip authorship to the quoted scholar even when the outer author is doing the teaching.  
EDGE CASE: Ibn Hajar quotes Ibn Malik at length as proof, then gives a short gloss; the quote could dominate characters but should not become the teaching voice.  
RECOMMENDATION: Add a new SPEC rule: “SQ-1 (Scholar-quoting-scholar): When Author A quotes Scholar B, the excerpt must preserve both voices and the relation between them. Attribute the unit to the active teaching voice, record B in `quoted_scholars` with relation type (`quoted_proof`, `quoted_emphasis`, `refuted_position`, `classification_frame`), and never let quote length alone flip authorship.”

ATOM: B3-SP2  
VERDICT: CHALLENGE  
EVIDENCE: Ledger says “Cross-passage comparison tests needed. Design deferred to evaluation phase” [FOUNDATIONS_HARDENING_LEDGER.md](/C:/Users/Rayane/Desktop/kr/engines/excerpting/reference/FOUNDATIONS_HARDENING_LEDGER.md#L63C1). I found no SPEC section that requires family-level boundary consistency audits; FP-20 is only a general hard-cases principle [SPEC.md](/C:/Users/Rayane/Desktop/kr/engines/excerpting/SPEC.md#L79C1).  
CROSS-RULE RISK: Without this audit, B2-P2 and B3-P1 can produce opposite boundary behavior on parallel passages with no release blocker.  
EDGE CASE: Repeated `ما يؤخذ من الحديث` sections across one sharh family where similar numbered benefits are split in one chapter and merged in another.  
RECOMMENDATION: Add: “BC-1 (Boundary consistency audit): Comparable passage families must be compared for boundary consistency. If similar scholarly patterns receive materially different unit boundaries without source-driven cause, flag the family for review and block release until the difference is explained.”

ATOM: B3-SP3  
VERDICT: NEEDS-REVISION  
EVIDENCE: Ledger says “malformation-first diagnosis … Phase 3 note-handling” [FOUNDATIONS_HARDENING_LEDGER.md](/C:/Users/Rayane/Desktop/kr/engines/excerpting/reference/FOUNDATIONS_HARDENING_LEDGER.md#L64C1). FP-2 does say notes must never “silently ‘rescue’” a defective excerpt [SPEC.md](/C:/Users/Rayane/Desktop/kr/engines/excerpting/SPEC.md#L36C1), but there is no explicit malformation-first rule.  
CROSS-RULE RISK: FP-2/NC-1 helps, but in the absence of an explicit rule, `context_hint` can still function as a cosmetic patch for a bad boundary.  
EDGE CASE: A unit starting `وأما الثاني` or `ولهذا` that gets a helpful note instead of being diagnosed as wrongly split.  
RECOMMENDATION: Add: “MF-1 (Malformation-first diagnosis): When a unit is structurally malformed, diagnose and flag the boundary error first. `context_hint` or note visibility may describe the defect but must not be treated as sufficient repair or used to upgrade the unit’s verdict.”

ATOM: B3-SP4  
VERDICT: CONFIRM  
EVIDENCE: The ledger says FP-1+3+9 collectively cover it [FOUNDATIONS_HARDENING_LEDGER.md](/C:/Users/Rayane/Desktop/kr/engines/excerpting/reference/FOUNDATIONS_HARDENING_LEDGER.md#L65C1). That is defensible: FP-1 preserves explained/explanation unity, FP-3 protects anchoring dependencies, FP-9 warns against overgranulation, and FP-13 explicitly subordinates granularity to correctness [SPEC.md](/C:/Users/Rayane/Desktop/kr/engines/excerpting/SPEC.md#L34C1), [SPEC.md](/C:/Users/Rayane/Desktop/kr/engines/excerpting/SPEC.md#L38C1), [SPEC.md](/C:/Users/Rayane/Desktop/kr/engines/excerpting/SPEC.md#L50C1), [SPEC.md](/C:/Users/Rayane/Desktop/kr/engines/excerpting/SPEC.md#L58C1).  
CROSS-RULE RISK: None material; FP-13 already defines the tie-breaker stack.  
EDGE CASE: Splitting a rule from its `إلا` or `لكن` qualifier, which the current DP/C-SC rules already treat as misleading.  
RECOMMENDATION: None.

SUMMARY: 4 CONFIRM, 3 CHALLENGE, 5 NEEDS-REVISION across the 12 explicitly labeled B2/B3 atoms. Highest-risk finding: B3-SP1, because there is no real scholar-quoting-scholar protocol in the SPEC yet, and the existing 80% dominant-layer rule can silently flip authorship on long quotations.

Verification note: WSL `make quality-gate` was blocked by `Wsl/Service/CreateInstance/E_ACCESSDENIED`, and this shell has neither `python` nor `py`, so I could not run the repo’s local sync/spec checks.