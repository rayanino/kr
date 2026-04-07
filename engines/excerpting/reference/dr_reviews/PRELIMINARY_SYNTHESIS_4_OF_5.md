# Preliminary 4-Coworker Synthesis — Owner Data Requirements

**Status:** PRELIMINARY (4/5 coworkers. Gemini DR pending — may refine details.)
**Date:** 2026-04-07
**Question:** "What data does the pipeline need from the owner that CANNOT be derived from code, text analysis, or LLM inference alone?"

---

## The 4-Layer Architecture

Every coworker independently found different pieces of the same structure. Together they form 4 hierarchical layers, each dependent on the one above:

```
┌────────────────────────────────────────────────────────────────┐
│  LAYER 1: USER MODEL + PEDAGOGICAL MODE                        │
│  "What kind of student am I? How do I study?"                  │
│  Sources: Codex DT-01, Gemini CLI per-science data, interview  │
│  Weeks 1-2 | ~2 hours | PARTIALLY RESOLVED from interview     │
├────────────────────────────────────────────────────────────────┤
│  LAYER 2: QUALITY POLICIES + CONFLICT GOVERNANCE               │
│  "What rules govern output? Which quality dimension wins?"     │
│  Sources: Codex DT-02..09, ChatGPT DR S-1/S-2                 │
│  Weeks 2-4 | ~3 hours | MOSTLY MISSING (remaining questions)  │
├────────────────────────────────────────────────────────────────┤
│  LAYER 3: ENGINE DECISIONS + PARAMETERS                        │
│  "What configures each engine?"                                │
│  Sources: DR18 SRC/EXC/TAX/SYN-D-* decisions                  │
│  Weeks 1-3 | ~5 hours | MOSTLY MISSING (5 focused sessions)   │
├────────────────────────────────────────────────────────────────┤
│  LAYER 4: CALIBRATION                                          │
│  "Does the engine match the owner's brain?"                    │
│  Sources: All 4 coworkers converge (FP-18, EXC-D-001)         │
│  Weeks 4-12 + summer | ~20-30 hours | REQUIRES REAL OUTPUT     │
└────────────────────────────────────────────────────────────────┘
```

## Universal Convergence (ALL 4 coworkers agree)

These findings are HIGH CONFIDENCE — independently discovered by multiple coworkers:

1. **S-1 / DT-02: Quality dimension priority order is the critical governance gap.** When fidelity, self-containment, granularity, and study value conflict — which wins? Currently "Not yet defined." (ChatGPT DR + Codex)

2. **FP-18 / DT-08 / EXC-D-002: Study-readiness calibration is the key calibration gap.** FULL conflates "acceptable" and "study-ready." The boundary needs ~30-100 empirical judgments. (All 4 coworkers)

3. **K-1..K-3 + E-1..E-3: Khilaf/tarjih and evidence organization are the biggest semantic corruption risks.** Speaker-role inversion and orphaned fragments. (ChatGPT DR + Codex + DR18 indirectly)

4. **Genre/layer policies must be defined before scaling beyond fiqh.** Rules optimized for fiqh will break in nahw/balagha/usul/aqidah. (ChatGPT DR + Codex + Gemini CLI)

5. **Only FP-8 and FP-18 need owner calibration among the 22 FPs.** The rest are specified enough to implement. (Codex, confirmed by CC verification)

## What's Already Collected vs What's Missing

| Category | Already Exists | Missing | Priority |
|----------|---------------|---------|----------|
| **Excerpt definition** | F1 canon (3-level quality model) | S-2 ideal/worst examples | Tier 1 |
| **Study workflow** | F2 narrative + YAML | Formal user_model artifact | Tier 1 |
| **Conflict resolution** | — | **S-1 priority ranking (CRITICAL)** | Tier 1 |
| **Study-readiness** | FP-18 definition exists | **30-100 empirical calibration labels** | Tier 1 (summer) |
| **Granularity rules** | G1-G4 bundles (policy captured) | Calibration with real output | Tier 2 (summer) |
| **Self-containment** | F3-F5, SC1 (policy captured) | SC2, SC3 remaining questions | Tier 2 |
| **Proof handling** | F6 (policy captured) | Architecture decision for fetched proofs | Tier 2 |
| **Failure philosophy** | F7 (corruption intolerance) | Flag budget threshold number | Tier 3 |
| **Taxonomy independence** | F8 (fully captured) | — | Done |
| **Khilaf/tarjih** | Partial in F4 | **K-1..K-3 (SPEC defers)** | Tier 1 |
| **Evidence organization** | — | **E-1..E-3 (MISSING)** | Tier 1 |
| **Definition splitting** | — | **D-1..D-3 (MISSING)** | Tier 1 |
| **Genre/layer policies** | — | **GN-1/GN-2, L-1/L-2 (MISSING)** | Tier 2 |
| **Study mode per science** | — | **Madhhab, munazarah, shubuhat** | Tier 1 (Gemini) |
| **Muhaqiq trust list** | — | **SRC-D-001 (binary choices)** | Tier 2 |
| **Science scope ranking** | Partial (interview) | **18-science formal ranking** | Tier 1 |
| **Book processing priority** | 1 book (interview) | **Full 2,519-book triage** | Tier 2 |
| **Tree reviews** | — | **4 trees × 30 min each** | Tier 2 (as trees mature) |
| **Entry style** | Signal from interview | **Read ENTRY_EXAMPLE.md + feedback** | Tier 3 |
| **School lists per science** | — | **Per-science confirmation** | Tier 3 |
| **Cognitive complexity grading** | — | **GENUINE GAP (no spec exists)** | Future |
| **Active recall output format** | FSRS scheduling in user_model | **Output SHAPE undefined** | Future |

## Unified Collection Roadmap (3-Month Window)

### Phase A: Formalize + Foundational Governance (Weeks 1-2, ~3 hours)

**Layer 1 items (user model):**
- Formalize user_model artifact from interview data: study mode, Arabic-first priority, "just memorize" posture
- Per-science study mode decisions (Gemini CLI findings): madhhab target for fiqh, munazarah vs qawa'id for usul, shubuhat policy for aqidah, qa'idah+shahid atomicity for nahw
- Science scope: formal 18-science ranking (DR18 SRC-D-004)

**Layer 2 items (governance):**
- **S-1 priority ranking** — the universal conflict resolver (ChatGPT DR Tier 1)
- **S-2 ideal/worst excerpt** — concrete quality definition (ChatGPT DR Tier 1)
- Proof sourcing architecture decision (Gemini CLI FP-7): book-preserved vs fetched proofs

### Phase B: Semantic Safety Policies (Weeks 2-4, ~3 hours)

**Remaining questionnaire items:**
- K-1..K-3 (khilaf/tarjih deep dive) — speaker-role inversion risk
- E-1..E-3 (evidence organization) — linguistic cohesion vs granularity
- D-1..D-3 (definition splitting) — orphaned conjunction risk
- SC2, SC3 (remaining self-containment questions)

**Genre/layer policies:**
- GN-1/GN-2 (per-genre behavior + shaahid handling)
- L-1/L-2 (editor notes + sharh/matn packaging)

### Phase C: Engine Parameters (Weeks 1-3 interleaved, ~5 hours)

**DR18's 5 focused sessions:**
- Session A: Science scope ranking + study focus + tree order + expertise levels (45 min)
- Session B: Muhaqiq trust list + publisher reputation + watchlist (50 min)
- Session C: Book processing priority (60 min)
- Session D: Thresholds — breadth, error halt, flag budget, pre-approval policies (30 min)
- Session E: Entry style + school lists + hadith title retention (30 min)

### Phase D: Calibration (Weeks 4-12 + summer, ~20-30 hours)

**Requires real pipeline output:**
- 100+ excerpt judgments for teaching unit quality (EXC-D-001 / DT-03 calibration)
- 30-100 study-readiness labels splitting FULL into acceptable vs study-ready (FP-18 / DT-08)
- 30-book owner review gate (EXC-D-005 — non-negotiable before engine completion)
- DEPENDENT disposition rubrics (20-30 decisions, ongoing)
- Synthesis configuration after seeing real entries (SYN-D-001/D-003)

## Bundle Format Recommendations (from ChatGPT DR)

For remaining bundles (SC2, SC3, and any future series):

1. **Standardize manifest schema:** Use consistent field names (`final_choice`, not variants). Add `bundle_type` discriminator (canon/questionnaire/lightweight/calibration).
2. **Add `final_decisions.jsonl`:** Machine-readable key/value for resolved owner choices, separate from narrative.
3. **Add `integrity_manifest.json`:** SHA-256 per file, matching BCV §3B format.
4. **Standardize evidence tagging:** Per-atom `authority_level` field (owner_explicit / owner_inferred / model_expansion).

## Corrections Applied Across All Reports

| Coworker | Claim | Correction |
|----------|-------|-----------|
| DR18 | Muhaqiq list "hardcoded" | Configurable via `library/config/muhaqiq_lists.json` |
| DR18 | Sarf priority after nahw | No evidence — needs explicit owner confirmation |
| Gemini CLI | Prerequisite sequencing absent | PARTIALLY WRONG — user_model SPEC has curriculum infrastructure (not built) |
| Gemini CLI | Active recall absent | PARTIALLY — FSRS scheduling exists; output FORMAT undefined |
| Codex | DT-03 TEDIOUS vs DR18 EXC-D-001 SUMMER | Both right: POLICY now, CALIBRATION summer |

## Disagreement Register

| Topic | Coworkers | Resolution |
|-------|-----------|-----------|
| #1 priority | All 4 differ | 4 levels of one hierarchy (Layer 1→2→3→4) |
| Granularity timing | Codex (NOW) vs DR18 (SUMMER) | Two-phase: policy now, calibration summer |
| Study-readiness | Codex (separate) vs DR18 (conflated) | Codex correct — FP-18 explicitly separates |
| Tedious count | Codex (4 items) vs DR18 (13 items) | Different thresholds — both valid |

## Pending: Gemini DR

Gemini DR report has not yet arrived. Expected contribution: Islamic madrasa curriculum perspective — what minimum data does a student need per science for the library to function as a self-study tool? Grounded in tadarruj/mulazamah/takrar/murajaa methodology.

When received, expected impact on synthesis:
- May add Layer 1 items (curriculum prerequisites, learning sequences)
- May refine Phase A timing (which per-science decisions are most urgent)
- Unlikely to change the 4-layer architecture or the convergence findings
