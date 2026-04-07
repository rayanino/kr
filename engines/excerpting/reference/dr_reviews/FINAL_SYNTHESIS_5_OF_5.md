# FINAL 5-Coworker Synthesis — Owner Data Requirements

**Status:** FINAL (5/5 coworkers received, verified, cross-referenced)
**Date:** 2026-04-07
**Question:** "What data does the pipeline need from the owner that CANNOT be derived from code, text analysis, or LLM inference alone?"

---

## The 4-Layer Architecture (confirmed by all 5 coworkers)

```
┌────────────────────────────────────────────────────────────────┐
│  LAYER 1: USER MODEL + PEDAGOGICAL MODE                        │
│  "What kind of student am I? How do I study?"                  │
│  Sources: Codex DT-01, Gemini CLI, Gemini DR curriculum        │
│  Weeks 1-2 | ~3 hours | PARTIALLY RESOLVED from interview     │
│  NEW from Gemini DR: madhab choice, Basran default, mantiq     │
├────────────────────────────────────────────────────────────────┤
│  LAYER 2: QUALITY POLICIES + CONFLICT GOVERNANCE               │
│  "What rules govern output? Which quality dimension wins?"     │
│  Sources: Codex DT-02..09, ChatGPT DR S-1/S-2                 │
│  Weeks 2-4 | ~3 hours | MOSTLY MISSING (remaining questions)  │
│  NEW from Gemini DR: fiqh masking policy, science sequencing   │
├────────────────────────────────────────────────────────────────┤
│  LAYER 3: ENGINE DECISIONS + PARAMETERS                        │
│  "What configures each engine?"                                │
│  Sources: DR18 SRC/EXC/TAX/SYN-D-* decisions                  │
│  Weeks 1-3 | ~5 hours | MOSTLY MISSING (5 focused sessions)   │
│  NEW from Gemini DR: Kufan synonym layer, tree order grounded  │
├────────────────────────────────────────────────────────────────┤
│  LAYER 4: CALIBRATION                                          │
│  "Does the engine match the owner's brain?"                    │
│  Sources: All 5 coworkers converge (FP-18, EXC-D-001)         │
│  Weeks 4-12 + summer | ~20-30 hours | REQUIRES REAL OUTPUT     │
│  Unchanged by Gemini DR — all agree calibration is summer      │
└────────────────────────────────────────────────────────────────┘
```

## Universal Convergence (ALL 5 coworkers agree)

1. **S-1 / DT-02: Quality priority order is the critical governance gap.** "Not yet defined."
2. **FP-18 / DT-08 / EXC-D-002: Study-readiness calibration is the key calibration gap.** FULL conflates acceptable and study-ready.
3. **K-1..K-3 + E-1..E-3: Khilaf/evidence are the biggest semantic corruption risks.**
4. **Genre/layer policies must be defined before scaling beyond fiqh.**
5. **Only FP-8 and FP-18 need owner calibration among the 22 FPs.**
6. **The foundational doctrine IS already captured** in FP-1..22. Remaining work is calibration + special cases + pedagogical configuration.

## Gemini DR Additions (5th coworker, final)

### 3 New Architectural Requirements

1. **Fiqh Masking Layer** — الفقه على المذاهب الأربعة requires per-madhab filtering. The owner must designate a primary madhab; the system suppresses other schools' rulings until baseline mastery. Progressive unlock after verified competence. *Gemini DR calls introducing comparative fiqh to a beginner a "catastrophic pedagogical failure" backed by 6 academic citations.*

2. **Mantiq (Logic) = Science #19** — Classical logic is a non-negotiable prerequisite for Usul al-Fiqh and advanced Aqidah per the classical curriculum. Not in the current 18-science inventory. A foundational mantiq taxonomy tree must be built.

3. **Basran Terminology Default** — The nahw taxonomy must default to Basran grammatical nomenclature (logical deduction, universal rules = better for algorithms). A synonym-mapping layer translates Kufan variants to Basran taxonomy IDs.

### Month-by-Month Collection Calendar (Gemini DR, grounded in tadarruj)

| Month | Focus Sciences | Configuration Tasks |
|-------|---------------|-------------------|
| April 2026 | Imla + Sarf | Finalize morphological taxonomy. Lock sarf_v1_0. |
| May 2026 | Nahw + Balagha | Test FP-12/FP-3. Lock nahw_v2_0. Finalize FP-15 for balagha. |
| June 2026 | Fiqh + Mantiq | Configure single-madhab masking layer. Populate fiqh + logic trees. |
| July 1 2026 | Usul + Aqidah | Summer build begins. System links advanced theory to foundations. |

## Complete "What Exists vs What's Missing" Inventory

| Category | Already Exists | Missing | Source Coworker |
|----------|---------------|---------|----------------|
| Excerpt definition | F1 canon (3-level model) | S-2 ideal/worst examples | ChatGPT DR |
| Study workflow | F2 (narrative + YAML) | Formal user_model artifact | Codex DT-01 |
| Conflict resolution | — | **S-1 priority ranking (CRITICAL)** | ChatGPT DR |
| Study-readiness | FP-18 definition | **30-100 calibration labels** | All 5 |
| Granularity rules | G1-G4 (policy captured) | Calibration with output | Codex DT-03 |
| Self-containment | F3-F5, SC1 | SC2, SC3 remaining | Codex DT-04 |
| Proof handling | F6 (book vs fetched) | Architecture for fetched | Gemini CLI |
| Failure philosophy | F7 | Flag budget threshold | DR18 EXC-D-010 |
| Taxonomy independence | F8 | — (Done) | — |
| Khilaf/tarjih | Partial F4 | **K-1..K-3** | ChatGPT DR |
| Evidence organization | — | **E-1..E-3 (MISSING)** | ChatGPT DR |
| Definition splitting | — | **D-1..D-3 (MISSING)** | ChatGPT DR |
| Genre/layer policies | — | **GN-1/2, L-1/2** | ChatGPT DR |
| Study mode per science | — | **Madhhab, munazarah, shubuhat** | Gemini CLI |
| **Primary madhab** | — | **IMMEDIATE — blocks fiqh** | **Gemini DR** |
| **Basran default** | — | **Grammar school choice** | **Gemini DR** |
| **Mantiq (logic)** | — | **New science #19** | **Gemini DR** |
| **Science sequencing** | — | **imla→sarf→nahw→balagha→fiqh→usul** | **Gemini DR** |
| **Fiqh masking** | — | **Suppress other schools** | **Gemini DR** |
| Muhaqiq trust | — | SRC-D-001 binary list | DR18 |
| Science scope | Partial (interview) | 18+1 science ranking | DR18 |
| Book priority | 1 book (interview) | Full 2,519-book triage | DR18 |
| Tree reviews | — | 4 trees × 30 min | DR18 |
| Entry style | Signal (interview) | ENTRY_EXAMPLE.md feedback | DR18 |
| School lists/science | — | Per-science confirmation | DR18 |
| Complexity grading | — | **GENUINE GAP (no spec)** | Gemini CLI |
| Active recall format | FSRS scheduling | **Output SHAPE undefined** | Gemini CLI |

## Unified Collection Roadmap (FINAL)

### Phase A: Formalize User Model + Critical Curriculum Decisions (Weeks 1-2, ~3 hours)

**Owner questions (non-technical, study-focused):**
1. "Which madhab do you want to follow and memorize rulings from?" → Blocks fiqh processing
2. "When you study nahw, should the system use only Basran terms, or show both Basran and Kufan?" → Blocks nahw synonym layer
3. "Do you accept that you should study basic logic (mantiq) before usul al-fiqh?" → Blocks mantiq tree creation
4. "For each science: are you memorizing rules only, or also training dialectical reasoning?" → Blocks study mode config

**Formalization tasks (CC executes):**
- Create user_model artifact from interview + answers above
- Formal 19-science ranking (18 + mantiq)
- Per-science study mode configuration

### Phase B: Quality Governance + Semantic Safety (Weeks 2-4, ~3 hours)

**Remaining questionnaire items (existing ChatGPT workflow):**
- S-1 priority ranking — the universal conflict resolver
- S-2 ideal/worst excerpt definition
- K-1..K-3 khilaf/tarjih deep dive
- E-1..E-3 evidence organization
- D-1..D-3 definition splitting
- SC2, SC3 remaining self-containment
- GN-1/GN-2, L-1/L-2 genre/layer policies

### Phase C: Engine Parameters (Weeks 1-3 interleaved, ~5 hours)

**DR18's 5 focused sessions (can run in parallel with Phases A-B):**
- Session A: Science scope + study focus + tree order + expertise levels
- Session B: Muhaqiq trust + publisher reputation + watchlist
- Session C: Book processing priority (informed by Gemini DR calendar)
- Session D: Thresholds (breadth, error halt, flag budget, pre-approval)
- Session E: Entry style + school lists + hadith titles

### Phase D: Calibration (Weeks 4-12 + summer, ~20-30 hours)

**Requires real pipeline output (all 5 coworkers agree):**
- 100+ excerpt judgments (teaching unit quality)
- 30-100 study-readiness labels (FP-18 calibration)
- 30-book owner review gate (non-negotiable)
- DEPENDENT disposition rubrics
- Synthesis configuration (after seeing real entries)

## Corrections Applied Across All 5 Reports

| Coworker | Claim | Correction |
|----------|-------|-----------|
| DR18 | Muhaqiq list "hardcoded" | Configurable via muhaqiq_lists.json |
| DR18 | Sarf priority after nahw | No evidence — needs explicit ranking |
| Gemini CLI | Prerequisite sequencing absent | PARTIALLY WRONG — user_model SPEC has curriculum (not built) |
| Gemini CLI | Active recall absent | PARTIALLY — FSRS exists, output FORMAT undefined |
| Codex | DT-03 TEDIOUS vs DR18 SUMMER | Both right: policy now, calibration summer |
| Gemini DR | Comparative fiqh = "catastrophic failure" | SCHOLARLY CLAIM — owner must react, CC cannot judge |

## Total: ~31-41 hours over 3 months

- Layer 1: ~3 hours (weeks 1-2)
- Layer 2: ~3 hours (weeks 2-4)
- Layer 3: ~5 hours (weeks 1-3, interleaved)
- Layer 4: ~20-30 hours (weeks 4-12 + summer)
- **Average: ~20-30 min/day. Fits 2-3 hours/day budget easily.**
