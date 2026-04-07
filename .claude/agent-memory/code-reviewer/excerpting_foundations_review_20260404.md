---
name: excerpting_foundations_hardening_review
description: Review findings from 2026-04-04 foundations hardening session - SPEC-code prompt drift is the primary pattern
type: project
---

Reviewed the excerpting foundations hardening change set (FP-1 through FP-10, EE-1, NC-1, C-SC-2 expansion).

**Primary finding: SPEC §5.3.2 code block is stale relative to actual code prompt.**
The comment in phase2_group.py says "VERBATIM from SPEC §5.3.2" but the code has at least 5 areas of drift:
1. 3 extra decontextualization rules in code (tarjih, qualifications, Q&A)
2. C-SC-2 expanded in code and §3.2 but NOT in §5.3.2 code block
3. COPY FIDELITY instruction in code only
4. Derived Benefits / Numbered Items more detailed in code
5. Hadith inseparable core rule in code only

**Why:** Each improvement was added to the code prompt during different sessions but the SPEC code block (which claims to be the canonical prompt text) was not updated simultaneously.

**How to apply:** In future reviews, always diff the SPEC code block against the actual code prompt string. The "VERBATIM" comment is a flag to verify character-for-character identity.

**Secondary patterns:**
- Test coverage for prompt content changes is thin (only checks string presence of rule name, not rule content)
- NC-1 hierarchy is architecturally placed under PARTIAL heading but applies to all levels
- Arabic examples in C-SC-2 expansion are linguistically correct (verified)
- 909/909 tests pass with zero regressions
