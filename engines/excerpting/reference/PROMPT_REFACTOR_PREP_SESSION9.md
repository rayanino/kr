# Prompt Refactor Preparation — Session 9

**Prepared by:** CC Session 8 (post-debt-clearance)
**Recipe:** DR21 Claude prompt compression recipe (7-step)
**Target:** GROUP_SYSTEM_PROMPT from 1474 → 800-1000 words + incorporate T1-1..T1-3

---

## Current Prompt Inventory

| Prompt | Location | Approx. Words | Rules |
|--------|----------|--------------|-------|
| CLASSIFY_SYSTEM_PROMPT | phase2_classify.py:41 | ~450 | ~8 rules + 2 examples |
| GROUP_SYSTEM_PROMPT | phase2_group.py:42 | ~1474 | ~25 rules (THE bottleneck) |
| ENRICH_SYSTEM_PROMPT | phase3_enrichment.py:59 | ~300 | ~6 rules |

## Shared Content Analysis (DR21 Step 1)

**Role definition (IDENTICAL across all 3 prompts):**
```
You are an expert in classical Islamic scholarly text analysis (تحليل النصوص العلمية الإسلامية).
```
- This line appears verbatim in CLASSIFY (line 42), GROUP (line 43), and ENRICH (line 60).
- Extract to a shared system prompt: ~15 words saved from GROUP.

**Self-containment criteria (C-SC-1 through C-SC-5):**
- GROUP lines 154-187 (~200 words): Full self-containment evaluation with 5 criteria
- Phase 3 enrichment also uses self-containment (verify call)
- Could extract to shared system prompt with minor adaptation
- Estimated savings: ~180 words from GROUP

**Total Step 1 savings estimate:** ~195-200 words. Gets prompt to ~1275 words.

## GROUP Prompt Rule Categorization (DR21 Step 2 prep)

Preliminary categorization based on reading. Session 9 should verify each.

### Category A — Must stay in prompt (behavioral/semantic)
1. EE-1 General Principle (lines 52-58)
2. FORGIVING RETENTION (lines 69-76) — *needs T1-1 amendment*
3. TITLE RETENTION (lines 77-81)
4. MULTI-FUNCTION SPLIT (lines 82-86) — *needs T1-2 amendment*
5. INTRODUCTION SCOPE (lines 87-90)
6. PROOF STRUCTURE (lines 91-94) — *needs T1-3 amendment*
7. MENTION IS NOT EXCERPT (lines 95-98)
8. DECONTEXTUALIZATION rules (lines 133-152) — 8 sub-rules, some may merge
9. CONFLICT RESOLUTION precedence (lines 123-131) — critical ordering

### Category B — Move to validator (keep one-line reminder)
10. segment_indices contiguous ascending (line 192) — checkable by code
11. text_snippet COPY FIDELITY (lines 197-199) — checkable by hash
12. C-SC criteria (lines 157-187) — partially checkable post-hoc

### Category C — Move to pre-processing
13. Input format validation — already in code (contracts.py)

### Category D — Candidates for removal
14. Specific pattern groupings (lines 59-65): "position + evidence = one unit", "definition + examples = one unit", etc. — potentially subsumed by EE-1
15. The structural_transition grouping option (line 67-68) — very weak signal

### Merging Candidates
- Rules 59-65 (6 specific grouping patterns) could merge into EE-1 as examples
- DERIVED BENEFITS + NUMBERED ITEMS could merge into one rule with exceptions
- DECONTEXTUALIZATION sub-rules 133-152 could compress significantly (many restate FP-14)

## Session 9 Tier-1 Changes to Incorporate During Refactor

| ID | Change | Words Added | Where |
|----|--------|-------------|-------|
| T1-1 | Add إذ, لكونه to causal particle list; soften "exhaustive" | +5 net | FORGIVING RETENTION |
| T1-2 | Soften 20% to heuristic + add semantic dependency exemption | +15 net | MULTI-FUNCTION SPLIT |
| T1-3 | Add dialectical cross-ref to FP-14 | +12 net | PROOF STRUCTURE |
| **Total** | | **+32 net** | |

## Session 9 Execution Plan

1. **Build regression test suite** (DR21 prerequisite): Use existing 917 test suite + 50 diverse Arabic inputs from fixtures
2. **Step 1:** Extract shared system prompt (role + self-containment criteria)
3. **Step 2:** Categorize all rules (verify the prep above)
4. **Step 3:** Distill Category A rules (rewrite concisely)
5. **Step 4:** Merge related rules (DERIVED BENEFITS + NUMBERED ITEMS; DECONTEXTUALIZATION compression)
6. **Steps 5-7:** Category D testing, example compression, reordering
7. **Incorporate T1-1..T1-3** during Step 3 (amend while distilling)
8. **Test at each gate** (existing test suite)
9. **Execute T2-1..T2-7** SPEC sync additions
10. **Dispatch Codex + Gemini** for refactored prompt review

## Critical Warnings (from DR21)
- **Never merge rules from different hardening sessions** — they address distinct edge cases
- **FORGIVING RETENTION was added Session 2** (hardening); MULTI-FUNCTION SPLIT also Session 2
- **DERIVED BENEFITS/NUMBERED ITEMS were added Session 1** (initial build)
- **DECONTEXTUALIZATION was added Session 1** (initial build)
- Merging within the same session is safer than across sessions
