# Hardening Session Protocol v5.0

---
governing_version: "5.0"
---

> **Authority:** ABSOLUTE. Governs ALL future hardening sessions for ALL batch types (F, G, SC, and any future series). No session may deviate from this protocol without a protocol amendment (see §8).
> **Supersedes:** `ATOM_PROTOCOL.md` v1.0 (2026-04-04) for process governance. ATOM_PROTOCOL.md's Hard Rules (§Hard Rules) remain in force and are incorporated here.
> **Created:** 2026-04-06, derived from Session 1 experience + 6-agent design + 3-agent Plan synthesis.
> **Version history:**
> - v1.0 (2026-04-04): ATOM_PROTOCOL.md — Session 1 protocol. Batch-centric, no per-atom gates, no context management.
> - v2.0 (2026-04-06): This document — Per-atom lifecycle, formal consensus voting, dispatch-first context strategy, self-improvement mechanism.
> - v2.1 (2026-04-06): Gemini CLI review — arabic-scholarly-conventions.md in bootstrap, cross-science variation in expansion, distinct DR templates, expanded science list, attribution safety clarification, Arabic text degradation in bundle intake.
> - v2.2 (2026-04-06): Codex CLI review — reopen protocol for finalized atoms, CC voting role clarification, G-RAW made checkable, word budget running tracker.
> - v3.0 (2026-04-06): ChatGPT DR adversarial review (38 findings, 10 pre-mortems) → 10 accepted via Codex+Gemini consensus: terminal state split, MODIFY→DISPUTED escalation, preliminary debt ceiling, prompt refactor gate, verbatim span extraction, scholarly integrity arbitration, scoped NEEDS RESEARCH blocking, prompt coherence reviews, owner objection mechanism, closure verification script (to build).
> - v3.1 (2026-04-06): Gemini DR pedagogical review (8 findings, 4/10 + 3/10 scores) → 5 accepted via Codex+Gemini consensus: Natural Teaching Unit field, Graduated Learning Level field, atom complexity triage (Full/Light lane), owner briefing optimization (exception-based after 50 atoms), DR budget per session (max 5/session). 3 redirected to engine SPEC/downstream engines.
> - v3.2 (2026-04-06): Claude DR scholarly review (19 findings, 5/10 score) → 8 accepted via Codex consensus: science list expanded 8→12 with structural families, indivisible units expanded 5→17 in 3 tiers (always/usually/conditionally), mandatory pre-expansion genre classification (3 decisions), scholarly uncertainty flags, sharḥ-matn pair as critical indivisible unit, multi-layer text awareness, honorific+transmission formula preservation, suʾāl-jawāb+radd+qiyās+taqsīm structures. FP-13 genre-sensitivity (SCH-009/010) redirected to SPEC.
> - v3.3 (2026-04-06): Owner concern — guarantee every note is captured. Layer B upgraded from "reference" to "critically important source." Extraction changed from single bulk pass to per-file extraction with mandatory coverage verification table, red-flag re-reads, and density checks. Prevents Session 1 failure (15/139 files read).
> - v4.0 (2026-04-06): Session 2 empirical amendments — Codex + Gemini CLI consensus review of 12 proposed changes. Key: (1) lane-based context budgets (bootstrap 52K→150K, Full Lane 50K/atom, target 5-8 not 25-30), (2) 5 session types (intake-only, debt-clearance, prompt-architecture, full-atom, validation-only), (3) gate-precedence matrix, (4) WIP cap (max 1 Full Lane in Stages 3-5), (5) science list 12→16 (+Qirāʾāt/Tajwīd, +Fatāwā/Nawāzil, +Takhrīj/Rijāl, +Adab/Shiʿr), (6) indivisible units 17→23 (+Nāsikh/Mansūkh, +Qāʿidah/Farʿ, +Sabab al-Nuzūl, +Mafhūm/Manṭūq, +Muqsam), (7) checkpoint states for emergency handoff, (8) §4.15 contradiction resolved, (9) DR relay classes, (10) core+delta bootstrap, (11) grouped-implementation briefing enforcement, (12) scholarly sections 8-13 stay CC-local (Gemini: "dispatching severs cognitive link"). Based on Session 2 actual experience (96% context exhaustion at ~20 atoms).
> - v4.1 (2026-04-06): ChatGPT DR adversarial review (DR9, 18 findings: 8 CRITICAL, 9 HIGH, 1 MEDIUM). Pre-mortem analysis of July 2026 "40% CLOSED atoms have errors" scenario. Key patches: (1) checkpoint resolution gate in §1.6 (prevents orphaned atoms), (2) model_only ineligible for Light Lane (closes authority bypass), (3) WIP cap split into active-processing vs awaiting-external (prevents deadlock), (4) DR deadlock fallback in §4.9 (>7 days → downgrade to REOPENED), (5) document-precedence: Protocol > NEXT.md > handoffs (§0), (6) atom-review-sampled DR class (§4.16), (7) coverage-tier-specific G-CHALLENGED gate (not just "2/3"), (8) blinded DR tiebreaker template (§5.4), (9) session-type compatibility matrix (only 2 allowed pairs), (10) expansion evidence minimums + per-atom attention isolation (anti-checkbox-theater), (11) owner engagement heartbeat every 10 atoms post-50 (§4.15), (12) prompt coherence counter in handoff template, (13) refactor safety checklist (§4.11), (14) §8.4 doctrine backfill protocol, (15) Q-12 outcome spot-check for cross-science/ALWAYS-INDIVISIBLE atoms, (16) verify_atom_closure_minimal.py (DA-001 implemented). Stage 7 wording fixed: "post-decision + safety-critical veto" replaces "informational."
> - v4.2 (2026-04-06): Claude DR scholarly review (DR10, 5 findings: 3 CRITICAL, 2 HIGH). Grounded in Islamic textual traditions (taḥqīq, isnād methodology, madrasa pedagogy). Key changes: (1) science list 16→19: +ʿIlm al-Kalām [ARG] (dialectical shubhah-radd, distinct from ʿaqīdah), +ʿIlm al-Farāʾiḍ [ARG+RUL] (computationally structured inheritance), +Taṣawwuf [SEQ] (sequential-progressive maqāmāt with prerequisite-chain tracking). (2) New [SEQ] structural family. (3) [COM] REMOVED as peer family → replaced with 2-dimensional taxonomy (Family × Layer). Ḥadīth collections moved to [ENT]. Text Layer dimension: [M] Matn, [S] Sharḥ, [H] Ḥāshiyah, [T] Taʿlīqah with 3 interleaving types. (4) Indivisible units 23→30: +Mujmal/Mubayyan, +Dalīl/Wajh al-Dalālah, +Tarjīḥ block, +Istidrāk/Tanbīh, +Waqf markers [ALWAYS]; +Ijāzah chain [USUALLY]; +Taḥqīq apparatus [CONDITIONALLY]; Qiyās expanded with taʿlīl 3-stage manāṭ. (5) §4.13: madhhab-context parameter, edition metadata, authorship-confidence, genre-flexibility. (6) §4.15: theme-based cross-science batching (Gemini amended: discipline-homogeneous rejected for hardening), Tier 1 reversion, rubber-stamping detection. Gemini validation: AGREE on 3/4 scholarly findings, DISAGREE on discipline-homogeneous batching (synthesized into hybrid approach).
> - v4.3 (2026-04-06): Gemini DR pedagogical evaluation (DR11, 6 findings: 4 "FUNDAMENTALLY FLAWED", 2 "PROBLEMATIC"). Evaluated through Islamic curricula traditions (Waḥdat al-ʿUlūm, Mulāzamah, Tadarruj, ʿArḍ). **3 findings ADOPTED:** (1) Fatāwā/Nawāzil demoted from peer science to fiqh sub-clause (sciences 19→18), (2) NTU/GLL fields made CONDITIONAL (mandatory for CONTENT atoms, auto-bypass for STRUCTURAL), (3) Applied Visual ʿArḍ added to §4.15 (before/after Arabic text examples in batched summaries). **2 kernels EXTRACTED:** (4) cross-science dependency note added to expansion template (preserves waḥdat al-ʿulūm across sessions), (5) §0 persistent axiom reference to SPEC §1.1b as LIBRARY_USUL. **3 findings REJECTED:** session type abolition (would reproduce Session 2 context exhaustion), protocol decimation to 200 lines (ignores 34+ documented failures), Q-CLOSED reduction to 3 gates (covered by existing FPs + mechanisms). **FINAL DR REPORT — all 3 DRs (DR9 ChatGPT, DR10 Claude, DR11 Gemini) fully processed.**
> - v5.0 (2026-04-06): **Batch Lifecycle Protocol** — synthesized from 6 DR reports (DR12 ChatGPT batch completeness, DR13 Gemini pedagogical lifecycle, DR14 Claude tahqiq framework, DR15 Gemini operational verification, DR16 ChatGPT traceability/integrity, DR17 Claude manuscript verification scholarly reference). 52 implementation units. Gemini CLI validated scholarly grounding (5 corrections accepted). Key additions:
>   - **NEW §3A: Batch Lifecycle** — 6-phase model (Intake→Extraction→Challenge→Verification→Briefing→Finalization) grounded in Islamic madrasa pedagogy. MCU (Minimum Content Unit) definition with verbatim anchors. MCU classification (MISSED/SOFTENED/DISTORTED-tashif/DISTORTED-tahrif/SKIPPED-FILE). Bifurcated Hafiz/Faqih standard extended to 4-factor threshold matrix (genre, collator competence, text status, exemplar availability). ALL-CAPS = semantic content (fatal lahn if stripped). Fan-in threshold. Lahn severity framework (science-specific: fatal/tolerable varies by Islamic science).
>   - **NEW §3B: Batch Completion Gate** — 5-condition script-enforced gate. Batch status DERIVED not DECLARED. 9 hard rules (HR-13 through HR-22). Hash-bound inventory with drift detection.
>   - **NEW §3C: Batch Finalization (Ijazah)** — 4-lock ceremony + 9-field shahadah certificate anatomy (DR17 classical structure). Partial certification (ijazah mu'ayyanah). Revocation policy (Sijill al-Istidrак).
>   - **§1.5/§1.6 amended:** verification-only session type added. Gate-precedence: BCV gate after bundle intake, before prompt refactor.
>   - **§4.3 amended:** Anchor-bound expansion (R-09). Expansion fidelity indicator (R-20, او كما قال convention): exact/paraphrased/interpreted with mandatory-exact enforcement for devotional formulae and jawami' al-kalim.
>   - **§4.6 amended:** Absolute Reopen Authority (Haqq al-Istidrак). Istidrak remediation chain with generation indexing (R-21).
>   - **§4.8 amended:** Behavior-change evidence for Q-CLOSED (R-11). Model-environment equivalence contract (R-15). Coverage-claim validation (R-14).
>   - **NEW §4.18: Regression Gate** — Mandatory sweep after prompt/SPEC change (R-10).
>   - **NEW §4.19: Doctrine Coherence Gate** — Cross-batch lint (R-12).
>   - **§5 amended:** Variant preservation with authority-ordered provenance sigla (R-22, DR17). Role separation formalization: 5 classical roles mapped to protocol agents (R-26). Scholarly grounding note for authority hierarchy.
>   - **NEW §8.5: Calibration File** — Nuskha mi'yariyyah for drift detection (R-16). Dabt deficiency linkage from lahn framework (R-25).
>   - **8 new scripts:** batch_inventory.py, batch_verification_init.py, batch_compute_coverage.py, batch_generate_trace_report.py, verify_batch_completion_gate.py, run_regression_suite.py, prompt_coherence_lint.py, atom_impact_diff.py.

---

## §0 — STOP. READ THIS FIRST.

**This protocol is the law.** Every hardening session — whether on F1-F8, G1-G4, SC1-SC3, or any future batch — follows this document exactly. Before doing ANYTHING:

1. Read this entire protocol (use the Quick Reference Card at §9 for subsequent sessions after the first full read)

**AUTHORITATIVE TASK ORDER (v4.1):** If NEXT.md conflicts with any handoff document about session type or primary objective, NEXT.md wins. Handoff docs may ONLY specify resume point within the session type chosen by §1.6 gate-precedence. When protocol, NEXT.md, and handoffs disagree: Protocol > NEXT.md > handoffs. This prevents governance drift from handoff documents accumulating de-facto authority.

**PERSISTENT AXIOM REFERENCE (v4.3 DR11, LIBRARY_USUL):** SPEC §1.1b (Foundational Principles FP-1 through FP-22) is the persistent axiom set that survives all session boundaries. Unlike handoff documents (which decay across sessions) or ledger entries (which accumulate into unreadable bulk), the FPs are stable doctrine that every session must internalize. When in doubt about a rule established in a prior session, check the FPs first — if it was important enough to survive, it's there. This is the modern equivalent of the classical *matn* (core text) that preserves knowledge through concise foundational statements.

### §0.1 Autonomous Operations Doctrine (v5.0)

**You are the control tower. The owner is available for relay, preferences, and gate approval ONLY.**

| CC Decides Autonomously | Owner Involved |
|---|---|
| Session type (§1.6 gate-precedence) | DR relay (paste prompt into DR window) |
| Next step (roadmap in NEXT.md) | Owner-preference: "good / bad / confusing?" |
| Technical approach (CC + coworkers) | Formal gate approval (Ijazah Lock 4, phase transitions) |
| Implementation details | Providing new collection bundles |
| Quality assessment (CC + coworkers) | |
| Error detection (coworkers + scripts) | |
| Priority ordering (protocol determines) | |

**Autonomous session flow:** Read §0 checklist → determine session type from §1.6 → state session type → **begin work immediately**. Do NOT wait for owner to confirm session type or approve the first action. The protocol decides, not the owner.

**After every milestone:** State what was accomplished → what was decided → what you're doing next (already starting). If owner input is needed, ask ONE specific non-technical question, then continue working on other items while waiting.

**Decision escalation (when genuinely uncertain):** (1) dispatch coworkers, (2) apply SPEC FP precedence stack, (3) CC decides with documented reasoning. Owner is LAST resort, and ONLY for study-experience questions a non-technical user can answer.

**CC NEVER says:** "What should I do next?", "Should I proceed?", "Want me to continue?", "Standing by", "Waiting for your input", "Let me know how to proceed." These phrases indicate a failure of autonomous operation.

**MANDATORY VERBAL COMMITMENTS (v5.0 — state these BEFORE proceeding to item 2):**
> "I will operate autonomously per §0.1. I will not ask the owner for technical guidance. I will use /prompt-architect for every dispatch per HR-23."

If a session cannot produce this statement, it has not internalized the two governing doctrines and must re-read §0.1 and HR-23 before any work.

2. Read `.kr/HANDOFF.md` for current resume point
3. Read `engines/excerpting/CLAUDE.md` for engine state
4. Read `engines/excerpting/reference/FOUNDATIONS_HARDENING_LEDGER.md` for atom status
5. Read the active batch's atom queue section in `MERGED_ATOM_QUEUE.md` (dispatch a subagent for this — do NOT read the full 63KB file)
6. Verify you are on the correct branch
7. Run `python -m pytest engines/excerpting/tests/ -q --ignore=engines/excerpting/tests/test_phase2_integration.py --ignore=engines/excerpting/tests/test_phase3_integration.py` — must pass
8. Run `python scripts/check_prompt_spec_sync.py` — must PASS
9. Estimate your context budget: `bootstrap (~150K tokens) + full_atoms × 50K + light_atoms × 15K = ?` — plan your atom count target
10. Inventory any new collection bundles at the repo root (see §3)

**Bootstrap optimization for returning sessions (v4.0):** After your first full read of this protocol, subsequent sessions use a core + delta model:
1. Read version frontmatter (governing_version field) — verify it matches NEXT.md
2. Read §0 checklist directly (this section — always authoritative)
3. Read version delta: scan version history for entries AFTER the version you last read
4. Read §9 Quick Reference Card
5. Read any §-sections that changed in the delta
A subagent may assist reading §1-§8 and summarizing changes, but CC reads §0 and the version delta directly. Summary-only bootstrap causes law drift — the core sections must be read authoritatively.

**Do NOT process any atoms until all 10 checks pass.**

---

## §1 — Scope, Principles, and Relationships

### 1.1 Scope

This protocol governs the **hardening session lifecycle** — the process by which a CC (Claude Code) session transforms raw owner feedback (from collection bundles) into finalized, consensus-approved, implemented engine changes.

It applies to:
- All batch types: F (foundational), G (generalization), SC (scholarly context), and any future question series
- All CC sessions working on excerpting foundations hardening
- All coworker dispatches made during hardening sessions

### 1.2 Core Principles

These principles resolve ALL ambiguity in the protocol. When a rule is unclear, apply these in order:

1. **Per-atom rigor over throughput.** Processing 5 atoms perfectly is infinitely more valuable than processing 50 atoms shallowly. Even if it means 300 atomic sessions per batch.
2. **Owner feedback is the starting point, not the endpoint.** Each atom is extracted from owner signal, then EXPANDED into a complete, edge-cased specification. The expansion is the real work.
3. **No single-model conclusions.** Every content quality judgment requires CC + at least one coworker (Codex minimum, Gemini preferred). No exceptions.
4. **Context window preservation.** CC's context is the scarcest resource. Dispatch aggressively. Read locally only when CC must make a judgment call.
5. **Fail loud, not silent.** If a gate cannot be passed, the atom stays at its current stage. It does not advance with a "we'll fix it later" note.
6. **Raw owner text is ground truth.** When structured files (YAML/JSONL/MD) contradict the raw `.txt` source artifacts, raw text wins absolutely.
7. **The library is the mind of a scholar put on a screen.** Every boundary, every classification, every excerpt must be as clear as if a scholar is explaining it to you.

### 1.3 Relationship to Other Documents

| Document | Relationship |
|----------|-------------|
| `ATOM_PROTOCOL.md` | Superseded for process. Its Hard Rules (§Hard Rules) are preserved verbatim below. Historical reference. |
| `CLAUDE.md` (project root) | Overarching project rules. This protocol operates within those rules. |
| `engines/excerpting/CLAUDE.md` | Engine-specific context. Read at session start for current state. |
| `.claude/rules/mandatory-coworker-dispatch.md` | Operationalized by §5 of this protocol. |
| `.claude/rules/no-single-model-conclusion.md` | Operationalized by §5 of this protocol. |
| `.claude/rules/context-management.md` | Extended and made concrete by §6 of this protocol. |
| `.claude/skills/coworker-dispatch/SKILL.md` | Prompt templates updated by §5 of this protocol. |
| `MERGED_ATOM_QUEUE.md` | The atom queue this protocol processes. |
| `FOUNDATIONS_HARDENING_LEDGER.md` | The ledger where all stage artifacts are recorded. |

### 1.4 Hard Rules (Preserved from ATOM_PROTOCOL.md — Violations Are Session Failures)

1. **Never finalize an atom with fewer than 2 coworker reports** (CC + at least 1 external). Period.
2. **Never read only the extraction summary.** Always go back to the original collection files.
3. **Never skip the raw owner source layer.** Read `source_artifacts/*.txt` before anything else.
4. **Never modify the prompt without updating the SPEC code block.** Use `check_prompt_spec_sync.py`.
5. **Never skip empirical validation for prompt-affecting atoms.** Use `atom_test.py`.
6. **Never let a prior session's atom inventory cap your scope.** Extractions are a floor, not a ceiling.
7. **Never treat `model_only` atoms as confirmed without owner verification.**
8. **Never say "done" before Q-CLOSED gate passes** (see §4.8).
9. **Never end a session without writing a handoff** (see §7).
10. **Never read files >10KB directly** when a subagent can summarize them (see §6).
11. **ADDED v2.0: Never bulk atoms.** Each atom is analyzed, expanded, challenged, and briefed individually.
12. **ADDED v2.0, AMENDED v4.0: Never skip per-atom ledger brief artifact.** Owner is briefed after EVERY atom closure (ledger artifact mandatory). Owner-facing DELIVERY may be batched after 50 atoms per §4.15, but the ledger artifact is always per-atom.

### 1.5 Session Types (v4.0)

Each session declares its type at start. The type determines what work is done and how context is budgeted.

| Type | Purpose | Atom Processing? | Context Strategy |
|------|---------|-------------------|------------------|
| `intake-only` | Unzip, inventory, extract atoms from new bundles, integrate into queue | NO | 100% for bundle reads + subagent dispatches |
| `debt-clearance` | Re-dispatch missing coworkers for PRELIMINARY atoms, upgrade or re-open | Only PRELIMINARY atoms | Budget for N re-dispatches |
| `prompt-architecture` | Review and refactor prompt(s). Triggered by §4.11 prompt refactor gate | NO | Full prompt + SPEC §5.3.2 in context |
| `full-atom` | Per-atom 7-stage lifecycle. The core hardening work | YES: 3-5 Full Lane or 5-8 mixed | Per-atom budgets from §2.1 |
| `validation-only` | Run smoke tests, dispatch analysis teams, evaluate results | NO | Budget for test runs + team dispatches |
| `batch-verification` | **v5.0:** Batch Completeness Verification (§3A). Muqabalah bi-l-asl against raw .txt source files. SINGLE-PURPOSE — FORBIDDEN to combine with any other type. | NO (verification only) | 100% for file-by-file collation + MCU tracing |

**Rules:**
- A session MUST declare its type before processing the first work item.
- **Session-type compatibility matrix (v4.1):**

  | | intake-only | debt-clearance | prompt-architecture | full-atom | validation-only | batch-verification |
  |---|---|---|---|---|---|---|
  | intake-only | — | FORBIDDEN | FORBIDDEN | FORBIDDEN | FORBIDDEN | FORBIDDEN |
  | debt-clearance | FORBIDDEN | — | ALLOWED | FORBIDDEN | ALLOWED | FORBIDDEN |
  | prompt-architecture | FORBIDDEN | ALLOWED | — | FORBIDDEN | FORBIDDEN | FORBIDDEN |
  | full-atom | FORBIDDEN | FORBIDDEN | FORBIDDEN | — | FORBIDDEN | FORBIDDEN |
  | validation-only | FORBIDDEN | ALLOWED | FORBIDDEN | FORBIDDEN | — | FORBIDDEN |
  | batch-verification | FORBIDDEN | FORBIDDEN | FORBIDDEN | FORBIDDEN | FORBIDDEN | — |

  Only 2 combinations are ALLOWED: (`debt-clearance` + `prompt-architecture`) and (`validation-only` + `debt-clearance`). ALL other combinations are FORBIDDEN. When in doubt: single-type session. New atoms from intake are never processed in the same session as the intake.
- If a session discovers mid-work that it should be a different type (e.g., started `full-atom` but found new bundles at repo root), it STOPS, writes a handoff, and the next session handles the discovered work.
- Given infinite session availability, prefer SMALLER, CLEANER sessions over overloaded ones. 5 atoms done perfectly in a focused session is worth more than 15 atoms crammed into an exhausted context.

### 1.6 Gate-Precedence Matrix (v4.0)

When multiple gates trigger simultaneously at session start, resolve in this strict order:

```
1. VERSION RECONCILIATION — verify protocol title, frontmatter governing_version,
   and NEXT.md all agree (run scripts/check_protocol_version.py)
2. PREREQUISITE GATE — §0 checklist (10 items, all must pass)
3. CHECKPOINT RESOLUTION GATE — If ANY atom is in a checkpoint state
   (PAUSED-*, IMPLEMENTED-*), session type MUST be validation-only
   (if IMPLEMENTED-*) or debt-clearance (if PAUSED-*) until all
   checkpointed atoms are resolved to a terminal state or demoted
   to REOPENED with written rationale. Checkpoints are globally blocking.
4. PRELIMINARY DEBT CHECK — §4.9. If debt > threshold → session type = debt-clearance
5. BUNDLE INTAKE INVENTORY — if new .zip bundles at repo root → session type = intake-only
5A. BATCH COMPLETENESS VERIFICATION (v5.0) — If any batch has completed intake
    (§3 Step 7) but has NOT passed the Batch Completion Gate (§3B), session type
    MUST be batch-verification. Run scripts/verify_batch_completion_gate.py —
    if exit code ≠ 0, BCV session required. This gate blocks ALL downstream
    processing (prompt refactor, per-atom) until every batch source file is
    verified at its designated standard (Ḥāfiẓ for F1/F2 raw text, Faqīh
    for F3-F8 structured files — see §3A.4). See §3A-3C.
6. PROMPT REFACTOR GATE — §4.11. If triggered → session type = prompt-architecture
7. PER-ATOM PROCESSING — only reachable if gates 4-6 all clear → session type = full-atom
```

A higher-numbered gate CANNOT be evaluated until all lower-numbered gates are cleared. This prevents: processing new atoms while checkpoint debt or preliminary debt exceeds threshold, refactoring prompt before inventorying new bundles, **verifying batch completeness before starting atom work (v5.0)**, or starting atom work before version consistency is verified.

---

## §2 — Pre-Session Checklist

Before processing any atoms, complete this 10-item checklist. Items 1-8 are in §0. Items 9-10 are detailed here.

### 2.1 Context Budget Estimation

At session start, estimate your total budget:

```
Session-type caps (see §1.5):
  intake-only:         Budget 100% for bundle intake. 0 atoms processed.
  debt-clearance:      Budget for re-dispatching N preliminary atoms. 0 new RAW atoms.
  prompt-architecture: Budget for full prompt review + refactor. 0 atoms processed.
  full-atom:           3-5 Full Lane atoms OR 5-8 mixed (Full + Light) atoms.
  validation-only:     Budget for smoke run + analysis dispatch. 0 atoms processed.

Per-atom budgets:
  Full Lane:   ~50K tokens (expansion + 2-3 coworker dispatches + synthesis + implementation)
  Light Lane:  ~15K tokens (abbreviated expansion + 1 spot-check + implementation)

Bootstrap reading:    ~150K tokens (protocol summary + handoff + ledger recent + CLAUDE.md + queue section + prompt)
Safety reserve:       ~100K tokens (Zone 3-5 buffer, never touch)
```

State session type and budget explicitly before any work: "Session type: [type]. Budget: [full-atom: 5-8 atoms | intake-only: N bundles | etc.]. Handoff trigger: [Zone 3 at 75%]."

### 2.2 New Bundle Inventory

Check the repo root for new `.zip` bundles:

```bash
ls *.zip 2>/dev/null
```

For each new bundle:
1. Record: filename, size, modified date
2. Do NOT unzip yet — that happens during Bundle Intake (§3)
3. Check if the bundle's series (G1, G2, SC1, etc.) has a corresponding extracted atom queue section in MERGED_ATOM_QUEUE.md
4. If not: this bundle needs full intake processing

### 2.3 Resume From Handoff

If this is a continuation session (not the first session for this batch):
1. Read the previous session's handoff document
2. Identify the exact atom to resume at and its current stage
3. Verify all PRELIMINARY atoms from the previous session are still marked correctly in the ledger
4. Check if any coworker reports arrived since the last session (owner may have relayed DR responses)

---

## §3 — Collection Bundle Intake Protocol

This section governs how new collection bundles are received, verified, and prepared for atom extraction.

### 3.1 Bundle Structure Reference

All bundles follow a two-layer separation model:

**Layer A — Owner-Faithful Source (GROUND TRUTH):**
- `source_artifacts/*.txt` — raw owner text, verbatim, unmodified
- `01_questionnaire_answer.md` — cleaned owner answer with confidence level
- Authority: `owner_explicit`

**Layer B — Structured Analysis (CRITICALLY IMPORTANT SOURCE — equal attention to Layer A):**
- `02_*` through `14_*` — structured analysis files (case dossiers, decision ladders, nonnegotiables, red-team tests, priority matrices, traceability, open questions, hard judgments)
- Authority: varies (`owner_explicit`, `owner_consistent_inference`, `model_only`)
- **BOTH Layer A AND Layer B are critically important sources.** Layer B contains extensive ChatGPT research and expansion that the owner considers valuable structured analysis — NOT disposable metadata. Every note in every file must be extracted and processed.
- **CONFLICT RULE (unchanged):** When Layer B contradicts Layer A on the same point, Layer A (raw owner text) wins. But Layer B notes that ADD new insights, research, or analysis beyond what Layer A covers are INDEPENDENTLY VALUABLE and must not be discarded.

**Bundle variants:**
- **Standard full-expansion** (F3-F6, F8, G-series, SC-series): 14-16 numbered files + README + source_artifacts/
- **Failure package** (F7): Same core structure, files 05-07 are failure-specific
- **Lightweight workflow** (F2): Only 4 main files + source artifacts
- **Early-stage** (F1): Minimal structure (manifest + README only)

### 3.2 Intake Steps (Per Bundle)

**Step 1: Unzip and verify structure.**
```bash
mkdir -p engines/excerpting/chatgpt_{series}_collection
unzip -o chatgpt_{series}_collection_bundle.zip -d engines/excerpting/chatgpt_{series}_collection/
```
Verify: source_artifacts/ directory exists, README.md exists, manifest present.

**Step 2: Dispatch a subagent to inventory the bundle.**
Do NOT read the files yourself. Dispatch:
> "Read all files in `engines/excerpting/chatgpt_{series}_collection/`. Return: (a) file count and names, (b) which variant this is (standard/failure/lightweight/early-stage), (c) source_artifacts filenames and sizes, (d) authority level breakdown from manifest, (e) any red flags (missing source_artifacts, empty files, unrecognized structure)."

CC reads only the 2-4KB summary returned by the subagent.

**Step 3: Conflict detection scan (including Arabic text degradation).**
Dispatch a subagent:
> "Read `source_artifacts/*.txt` and `01_questionnaire_answer.md` from `engines/excerpting/chatgpt_{series}_collection/`. Compare the raw owner text against the cleaned answer. Report:
> (a) Contradictions, softened statements, added qualifications, or ALL-CAPS emphasis normalized to neutral.
> (b) **Arabic text degradation:** ligature normalization (e.g., ﷺ expanded to صلى الله عليه وسلم), honorific stripping (الإمام, الحافظ, شيخ الإسلام removed), diacritic loss, scholarly abbreviation changes (per `.claude/rules/arabic-scholarly-conventions.md`).
> (c) **Structural unit splitting:** muqaddimah preamble blocks (بسم الله + حمدلة + أما بعد) separated, colophon elements fragmented, isnad chains broken.
> Return: list of conflicts with file:line references, or 'no conflicts detected'."

**Step 4: Extract atoms — PER FILE, not per bundle.**
Do NOT dispatch a single subagent for the entire bundle. Extract FILE BY FILE to ensure nothing is missed:

For EACH file in the bundle (source_artifacts/*.txt, 01_*.md, 02_* through 14_*):
> Dispatch a subagent: "Read ONLY `engines/excerpting/chatgpt_{series}_collection/{FILENAME}`. Extract EVERY discrete note, directive, pain point, nonnegotiable, red-team test, preference, research finding, and analytical insight. Include BOTH owner statements AND ChatGPT's analysis/expansion — both are critically important. For each note, provide: (a) verbatim quote or close paraphrase, (b) file name and line number, (c) authority level (owner_explicit / owner_consistent_inference / model_only), (d) category (nonnegotiable / red-team / directive / preference / research / meta). Return as a numbered list. At the end, state the TOTAL note count for this file."

This produces one extraction per file. CC collects all per-file extractions.

**Step 5: Coverage verification (MANDATORY — the Session 1 failure prevention step).**
After all per-file extractions complete:
1. CC (or a subagent) produces a **coverage table**: one row per file, showing: filename, file size, notes extracted, categories found.
2. **Red flag check:** Any file with 0 notes extracted → re-read that file manually or with a second subagent using a different extraction prompt. A non-empty structured file with 0 notes is almost certainly a missed extraction.
3. **Density check:** Compare note counts to file sizes. A 30KB file with only 2 notes is suspicious — dispatch a second extraction pass with: "The first pass found only 2 notes in this 30KB file. Read it again carefully and extract ANY note that was missed."
4. **Cross-file deduplication:** Some notes appear in multiple files (e.g., a nonnegotiable in the raw text AND in the nonnegotiables JSONL). Deduplicate, but keep both source references for traceability.
5. CC records the coverage table in the ledger with totals: "Bundle {series}: {N} files read, {M} total notes extracted, {K} unique atoms after deduplication."

**Step 6: Assign MAQ-IDs and integrate into the queue.**
CC reviews the deduplicated extraction, assigns MAQ-IDs following the existing numbering scheme in MERGED_ATOM_QUEUE.md, and appends the new atoms to the appropriate section.

**Step 7: Move the zip to the collection directory.**
```bash
mv chatgpt_{series}_collection_bundle.zip engines/excerpting/chatgpt_{series}_collection/source_artifacts/
```

### 3.3 Intake Quality Gate

Before processing any atoms from a new bundle:
- [ ] Bundle unzipped and structure verified
- [ ] Subagent inventory completed
- [ ] Conflict scan completed (conflicts documented or "none" confirmed)
- [ ] **Per-file extraction completed (EVERY file, not a single bulk pass)**
- [ ] **Coverage table produced (file count, note counts, red flags addressed)**
- [ ] **No file has 0 notes unless it is genuinely empty (verified)**
- [ ] Atoms deduplicated, assigned MAQ-IDs
- [ ] MERGED_ATOM_QUEUE.md updated with new atoms + coverage totals
- [ ] Zip archived in source_artifacts/

---

## §3A — Batch Lifecycle Protocol (v5.0)

> **Grounding:** This section implements the classical Islamic muqābalah (collation) framework as described in DR17. The 6-phase model maps to: Muṭālaʿah (reading), Fahm (comprehension), Mudhākarah (peer discussion), Murājaʿah (revision/collation), ʿArḍ (presentation), Ijāzah (certification). Each phase prevents a distinct anti-pattern documented in DR13.

### 3A.1 Purpose and Scope

The per-atom lifecycle (§4) ensures each atom is correctly processed. But it does NOT prevent batch-level omissions — processing the *wrong set* of atoms perfectly. Session 1 proved this: 124 owner feedback atoms were silently dropped; entire files (F1/F2) were never read; ALL-CAPS urgency was systematically stripped.

§3A-3C close this gap. After bundle intake (§3) and BEFORE any per-atom processing (§4), every batch MUST pass through the Batch Lifecycle Protocol: a structural guarantee that every word of owner feedback is captured, verified, and traced from raw .txt source to the atom queue.

**Architecture: Serial Muqābalah (DR15 Architecture D, DR17 §1).** A primary agent extracts; a secondary agent (the muḥaqqiq) performs muqābalah bi-l-aṣl — side-by-side collation against the author's original — hunting for gaps left by the first agent. This matches the classical gold standard for written texts. Parallel independent extraction (Architecture A) is REJECTED — it produces non-comparable outputs with endless false positives.

### 3A.2 Minimum Content Unit (MCU) Definition

An **MCU** is the smallest span of owner source text that expresses a single: directive, definition, risk, rule-example, severity signal, or meta-instruction.

**Required fields for every MCU:**
- `mcu_id`: unique identifier within the batch
- `file_path`: source file containing the MCU
- `start_line`, `end_line`: exact line range in the source file
- `verbatim_anchor`: minimum 15 characters of exact source text (no paraphrase)
- `severity`: CRITICAL / HIGH / MEDIUM / LOW
- `classification`: see §3A.3

MCUs are identified during the Extraction phase (Phase 2) and verified during the Verification phase (Phase 4). The denominator for coverage calculations is ALWAYS total MCUs across all inventory files.

### 3A.3 MCU Classification System

Every MCU must be classified into exactly one category:

| Classification | Definition | Example | Remediation |
|---|---|---|---|
| **MAPPED** | MCU has a corresponding MAQ entry, META entry, or explicit REJECT entry | Owner says "mention is not a reason to excerpt" → MAQ-045 | None — this is the target state |
| **MISSED** (nuqṣān) | MCU has no MAQ/META/REJECT mapping | Entire directive silently dropped during extraction | Must create MAQ entry or explicit REJECT with justification |
| **SOFTENED** (takhfīf) | Direction preserved but urgency/force reduced | "NEVER allow this" → "Try to avoid this" | Strength restoration required. CRITICAL/HIGH cannot close without restoration or owner acknowledgment |
| **DISTORTED-tashif** (تصحيف, v5.0 DR17) | Surface corruption: diacritical/presentation error, recoverable by context. Sub-types: tashif al-baṣar (visual misreading), tashif al-samʿ (auditory mishearing). | Diacritic placed wrong, producing different but contextually detectable wrong word | Restore correct reading from source context |
| **DISTORTED-tahrif** (تحريف, v5.0 DR17) | Structural corruption: meaning altered, requires re-extraction from original. | "permissible" extracted as "impermissible"; isnad attribution swapped | Full re-extraction from raw .txt source; escalate to owner if ambiguous |
| **SKIPPED-FILE** | Entire file not processed during extraction | F1 source_artifacts/raw_notes.txt never read | Session failure. BCV gate CANNOT pass. |

**Location qualifier (v5.0 DR17):** MCU errors in the body text (matn) carry standard weight. MCU errors in the transmission chain (isnād) or attribution metadata carry ELEVATED weight because they affect provenance, not just content.

**Emphasis as semantic content (v5.0 DR13/DR14):** ALL-CAPS, exclamation marks, "PLEASE", and emotional intensity markers are SEMANTIC CONTENT, not formatting. Stripping them is MISSED or SOFTENED at the emphasis level — fatal laḥn when the emphasis changes the import of the directive.

**Three priority tiers for emphasis:**
- **Tier 1 (Immediate):** ALL-CAPS directives, "PLEASE" statements, emotional markers → must map to corresponding atom with force preserved
- **Tier 2 (Standard):** Normal directives without emphasis → standard MCU processing
- **Tier 3 (Deferred):** Observations, tentative suggestions → may be deferred with justification

### 3A.4 Verification Standard: 4-Factor Threshold Matrix (v5.0 DR17)

The classical Ḥāfiẓ-Faqīh spectrum determines how rigorously each file is verified. The threshold is selected per-file using 4 factors:

| Factor | Ḥāfiẓ Standard (lafẓī, word-for-word) | Faqīh Standard (maʿnawī, meaning-based) |
|---|---|---|
| **1. Genre/content type** | Devotional formulae, jawāmiʿ al-kalim, foundational vision statements, core rules | Implementation details, research analysis, structured expansions |
| **2. Collator competence** | Only an agent with deep domain understanding (ʿālim bi-l-lugha) may perform maʿnawī verification | Any qualified agent may perform lafẓī verification (it's mechanical) |
| **3. Text status** | Foundational (F1/F2), nonnegotiables, owner ALL-CAPS directives | Supplementary analysis (F3-F8 structured files), model-only expansions |
| **4. Exemplar availability** | Clear, unambiguous source text → stricter threshold | Ambiguous, handwritten, or fragmentary source → may require interpretation |

**Default assignments:**
- **F1/F2 source_artifacts/*.txt** → Ḥāfiẓ standard (100% sentence-by-sentence, verbatim collation)
- **F3-F8 01_questionnaire_answer.md** → Ḥāfiẓ standard (owner's cleaned answer is still owner text)
- **F3-F8 02-14_*.md/.jsonl** → Faqīh standard (15% random sample + all files flagged for SOFTENED/DISTORTED, 100% coverage for any file with CRITICAL-severity MCUs)
- **G-series, SC-series** → Apply 4-factor matrix per-file at intake time

**Mandatory-exact constraints (v5.0 DR17, Gemini-corrected):** Regardless of file classification, the following text types ALWAYS require Ḥāfiẓ (exact) verification:
- Devotional formulae (dhikr, duʿāʾ, shahāda) — exact wording carries ritual weight
- Jawāmiʿ al-kalim (concise prophetic sayings) — precise wording is integral to meaning
- Any directive where the owner's exact phrasing carries legal/doctrinal weight
- The classical 5 conditions for meaning-based transmission (riwāyah bi-l-maʿnā) must ALL hold before Faqīh standard is applied: (1) collator has deep domain knowledge, (2) no change to legal implications, (3) not devotional text, (4) not jawāmiʿ al-kalim, (5) if doubtful, append hedging marker per R-20

### 3A.5 Fan-In Threshold

When many MCUs map to a single MAQ entry:
- If a single MAQ maps to **>5 MCUs** OR **>1 CRITICAL-severity MCU**: the verifier MUST either:
  - Split the MAQ entry into sub-atoms, OR
  - Add a **Sub-Claim Table** showing 1:1 mapping from each MCU to a specific clause in the EXPANDED doctrine
- The Batch Completion Gate (§3B) FAILS if fan-in violations are unresolved
- This prevents semantic compression loss: all MCUs "accounted for" but a single downstream atom cannot faithfully implement all distinct constraints

### 3A.6 Laḥn Severity Framework (v5.0 DR17, Gemini-corrected)

Errors discovered during verification are classified by consequence, not just type:

**Fatal laḥn (HALT + escalate + correct before proceeding):**
- Changes a legal ruling, doctrinal position, or scholarly attribution
- Alters the owner's intent substantively (not just phrasing)
- Occurs in devotional text, jawāmiʿ al-kalim, or nonnegotiable directives
- Indicates lack of ḍabṭ (precision) by the extraction/verification agent

**Tolerable laḥn (LOG with variant notation + continue):**
- Minor phrasing variations that preserve meaning and intent
- Dialect-level or stylistic differences not affecting substance
- Errors in supplementary analysis (not core owner directives)

**Science-specific severity (Gemini CLI correction):**
- In **Qirāʾāt/Tajwīd:** No cosmetic errors. Errors are jalī (obvious, fatal — invalidates prayer) or khafī (hidden, but graded). All are at minimum HIGH severity.
- In **Naḥw:** A single vowel change can destroy the structural purpose of a grammatical evidence (shāhid). Treat as HIGH minimum.
- In **ʿAqīdah:** Doctrinal sensitivity means almost all textual alterations are CRITICAL.
- In **Ḥadīth faḍāʾil al-aʿmāl:** Tolerable laḥn applies — minor errors in narrations about virtues (not legal rulings) are logged but do not block.
- In **Fiqh implementation details:** Standard tolerable/fatal classification applies.

**Ḍabṭ deficiency detection:** If the same agent produces tolerable laḥn at a rate exceeding 15% of verified MCUs across 3+ verification sessions, flag for ḍabṭ deficiency. Trigger recalibration via the Calibration File (§8.5, R-16): the agent must independently re-extract the calibration file and achieve <5% error rate before continuing verification work.

---

## §3B — Batch Completion Gate (v5.0)

### 3B.1 Gate Conditions

A batch's Completion Gate passes if and only if ALL 5 conditions are TRUE:

| # | Condition | How Verified |
|---|-----------|-------------|
| G-B-1 | **100% file coverage:** Every file in the inventory (§3 Step 2) has state VERIFIED in verification_status.json | `scripts/verify_batch_completion_gate.py` checks all file states |
| G-B-2 | **MCU mapping completeness:** Every MCU in mcu_trace.jsonl has classification ≠ MISSED at CRITICAL or HIGH severity | `scripts/batch_compute_coverage.py` reports zero CRITICAL/HIGH MISSED |
| G-B-3 | **Zero SKIPPED-FILE:** No file has state SKIPPED-FILE | `scripts/verify_batch_completion_gate.py` checks |
| G-B-4 | **Queue terminality:** Every MCU maps to a MAQ entry (status ≠ NEW), META entry, or explicit REJECT with justification | `scripts/batch_compute_coverage.py` checks mapping completeness |
| G-B-5 | **Script attestation:** `scripts/verify_batch_completion_gate.py` exits 0 with coverage summary | Deterministic — no human judgment |

**Batch status is DERIVED, not DECLARED.** The gate passes when the script says it passes. No session may manually mark a batch as "verification complete." The script reads the artifact files (inventory.json, verification_status.json, mcu_trace.jsonl, coverage.json) and computes the verdict.

### 3B.2 Hard Rules for Batch Verification

HR-13: Never begin per-atom processing on a batch until BCV session complete and Batch Completion Gate passes.
HR-14: Never mark a file VERIFIED without MCU trace records containing verbatim anchors + line ranges.
HR-15: Never verify Layer B without first verifying Layer A (raw owner source).
HR-16: Never strip ALL-CAPS, exclamation marks, or emphasis markers from owner text — they are semantic content.
HR-17: Never self-audit — the session that performed extraction CANNOT perform verification (muqābil ≠ qāriʾ, DR17 §4).
HR-18: Never post-edit the queue after verification without rolling back the affected file's status to DRIFTED.
HR-19: Never disposition MCU as "ALREADY COVERED" without citing the exact FP clause + writing a minimal counterexample.
HR-20: Never close Q-CLOSED for a prompt-affecting atom without behavior-change evidence (atom_test output required — no waivers for prompt-affecting atoms, per §1.4 Rule 5).
HR-21: Never merge prompt changes without `scripts/run_regression_suite.py` passing.
HR-22: Never combine extraction and verification roles in the same session/agent — the extractor cannot be the verifier (DR17 role separation, muqābil ≠ nāsikh).
HR-23: **Never dispatch a prompt to ANY target (Codex CLI, Gemini CLI, DR relay, CC subagent) without first passing it through `/prompt-architect`.** The optimized version is what gets dispatched. Draft prompts are NEVER sent directly. Speed is not a constraint; quality is. Owner ALL-CAPS directive 2026-04-06. Session 3 evidence: raw Gemini prompt missed 6 real issues; prompt-architect RCoT version found all 6.

### 3B.3 Artifact Suite

Each batch-verification session produces:

| Artifact | Path | Schema |
|----------|------|--------|
| `inventory.json` | `engines/excerpting/{batch}_collection/verification/` | `{files: [{path, sha256, size_bytes, line_count, layer: A|B}], batch_id, created_at}` |
| `verification_status.json` | same | `{files: [{path, state: UNVERIFIED|IN_PROGRESS|VERIFIED|DRIFTED, mcu_count, verifier, timestamp}], batch_verification_run_id}` |
| `mcu_trace.jsonl` | same | Per-line: `{mcu_id, file_path, start_line, end_line, verbatim_anchor, classification, maq_id?, severity, confidence, fidelity_level}` |
| `coverage.json` | same | `{total_files, verified_files, total_mcus, mapped_mcus, missed_count, softened_count, distorted_tashif_count, distorted_tahrif_count, coverage_pct}` |
| `verification_report.md` | same | Human-readable: coverage table, gap inventory, adversarial sample results, recommendations |
| `gap_remediation_tracker.jsonl` | same | Per-line: `{asl_ref: {file, line, text}, state: 1|2|3, atom_id?, spec_section?, date_changed, responsible}` — tracks Aṣl-only → Established → Implemented |
| `collation_register.jsonl` | same | Per-line: `{file_path, mcu_id, collation_mode: lafzi|ma'nawi, finding: sahh|saqt|ziyada|tashif|tahrif, correction?, checkpoint_position, session_id}` — the Sijill al-Muqābalah |

**Hash-bound integrity:** `inventory.json` records SHA-256 per file at intake time. If a file changes after inventory (editing the raw source), its state automatically becomes DRIFTED and the Completion Gate fails until re-verified.

---

## §3C — Batch Finalization: Ijāzah Ceremony (v5.0)

### 3C.1 4-Lock Gate

A batch receives its Ijāzah (certification of completeness) if and only if all 4 locks are satisfied:

| Lock | Name | Condition |
|------|------|-----------|
| 1 | **Mulāzamah Proof** | Cryptographic proof (SHA-256) that 100% of inventory files were ingested and mapped |
| 2 | **Taḥqīq Clearance** | Zero SOFTENED at CRITICAL/HIGH severity remaining + count of remediated gaps documented |
| 3 | **Mudhākarah Consensus** | At least 2 independent coworker reviews of the verification report. Coworker signatures recorded |
| 4 | **ʿArḍ Validation** | Owner approval: Full (all files) or Partial (specific files). For F1/F2: 15-20 min exhaustive ʿArḍ (Ḥāfiẓ). For F3-F8: 20-30 min spot-check (Faqīh) |

### 3C.2 Shahādat al-Muqābalah: 9-Field Certificate (v5.0 DR17)

Upon Ijāzah, produce a formal verification certificate with these 9 fields (grounded in classical manuscript attestation, DR17 §2):

1. **Statement of completion:** "بلغ مقابلة بأصله" — "Collation against its original has been completed"
2. **Exemplar description:** Which aṣl (raw .txt files) was used, identified by file path and SHA-256
3. **Collator identity:** Which agent/session performed the verification, with session ID
4. **Method statement:** Collation mode per file (lafẓī or maʿnawī), individual or assembly (solo agent or coworker team)
5. **Date:** ISO 8601 timestamp
6. **Completeness statement:** "100% file coverage" or "على حسب الإمكان" (as well as possible) with explicit limitations
7. **Variant notation key:** Mapping of provenance sigla used in the collation register (e.g., "خ O2 = owner feedback version 2")
8. **Exemplar pagination reference:** File:line references preserved for traceability
9. **Integrity closing:** "All MCUs verified. Coverage: X%. This certificate is revocable per §3C.3."

**Lock-to-certificate field mapping (v5.0, Gemini-corrected):**
- Lock 1 (Mulāzamah) → Field 2 (exemplar description with SHA-256) + Field 6 (completeness: "100% file coverage")
- Lock 2 (Taḥqīq) → Field 6 (completeness: "zero SOFTENED at CRITICAL/HIGH; N gaps remediated") + Field 9 (closing attestation)
- Lock 3 (Mudhākarah) → Field 3 (collator identity: list all coworkers who reviewed) + Field 4 (method: "assembly" if multiple reviewers)
- Lock 4 (ʿArḍ) → Field 9 (closing: "Owner approval: Full/Partial. Caveats: [if any]")

### 3C.3 Partial Certification and Revocation

**Partial certification (Ijāzah muʿayyanah):** When the owner approves F3-F8 but challenges F1 interpretation, F3-F8 atoms may be FINALIZED while F1 atoms remain CHALLENGED. This prevents bottlenecks while maintaining rigor.

**Revocation (Rujūʿ):** If the owner discovers a flaw after Ijāzah — or a future verification session invokes Absolute Reopen Authority (§4.6, R-08) — the existing certificate is archived (never deleted), affected atoms are demoted, and the full 4-lock gate must be re-executed. Record in Sijill al-Istidrāk (remediation journal) with: revocation date, reason, affected atoms, new certificate ID.

---

## §4 — Atom Lifecycle: 7 Stages

Every atom passes through exactly 7 stages. No stage can be skipped. No atom advances without passing the exit gate. The stages are:

**WIP Cap (v4.0, amended v4.1):** Maximum 1 Full Lane atom in Stages 3 and 5 (EXPANDED or SYNTHESIS-IN-PROGRESS) at any time. Stage 4 (AWAITING COWORKERS) is tracked separately: max 3 Full Lane atoms may be in AWAITING COWORKERS concurrently, provided no more than 1 is actively being expanded or synthesized. Maximum 3 atoms total in any non-terminal state. Exceeding any WIP sub-cap is a session failure. This split prevents the "no legal moves" deadlock where async coworker latency blocks all progress.

```
RAW ──→ SOURCED ──→ EXPANDED ──→ CHALLENGED ──→ SYNTHESIZED ──→ IMPLEMENTED ──→ CLOSED
 (1)      (2)         (3)          (4)            (5)             (6)           (7)
```

### 4.1 Stage 1: RAW

**Entry:** Atom appears in MERGED_ATOM_QUEUE.md or is discovered during queue audit / bundle intake.

**What exists:** MAQ-ID, 1-2 sentence summary, source reference, authority classification, status: NEW.

**Selection priority:** nonnegotiable > red-team test > prompt-affecting > SPEC-only > deferred.

**Exit gate (G-RAW):**
- [ ] CC has marked this atom's status as `IN_PROGRESS` in MERGED_ATOM_QUEUE.md
- [ ] The atom's MAQ-ID and source collection are recorded in the ledger as a new entry

### 4.2 Stage 2: SOURCED

**Entry:** G-RAW passed.
**Actor:** CC orchestrator. For files >10KB, dispatch a subagent to read and summarize; CC reads the summary.
**Duration:** 10-15 minutes.

**Process:**
1. Read the RAW OWNER SOURCE first — `source_artifacts/*.txt` from the relevant collection. This is ground truth. CC MUST quote at least one exact owner sentence in the ledger entry.
2. Read the cleaned answer — `01_questionnaire_answer.md`.
3. Read the SPECIFIC structured file the atom came from (the nonnegotiable JSONL, red-team test, decision ladder, etc.). Record file path and entry ID.
4. Read the traceability entry if it exists.
5. **Conflict check:** Does the structured file match the raw source? If not, raw wins. Document the drift: "ChatGPT drift at [file:line]: structured says X, raw says Y, proceeding with raw."
6. **Authority verification:** If `model_only`, flag that owner confirmation is required before Stage 5 synthesis.

**Artifacts produced:**
- Ledger section: "Raw owner artifacts used" (file paths + exact quotes)
- Ledger section: "Owner signal reconstruction" (what the owner meant, in CC's words)
- Ledger section: "Owner tensions" (contradictions within owner's own statements, if any)
- Ledger section: "Authority level" (with justification)
- Conflict notes (if any)

**Exit gate (G-SOURCED):**
- [ ] At least one raw `.txt` file read and owner quote recorded
- [ ] Structured collection file read
- [ ] Authority level classified and justified
- [ ] Conflict check performed (even if "no conflicts" — recorded)

### 4.3 Stage 3: EXPANDED

**Entry:** G-SOURCED passed.
**Actor:** CC orchestrator. May dispatch subagents for interaction mapping or blast-radius checks.
**Duration:** 15-20 minutes.

**This is the stage Session 1 skipped entirely.** A raw atom like "mention is NOT a reason to excerpt" must become a COMPLETE SPECIFICATION before coworkers can meaningfully review it.

**MANDATORY pre-expansion read:** Before drafting any expansion, CC (or a subagent) must read `.claude/rules/arabic-scholarly-conventions.md` to avoid proposing rules that violate Islamic scholarly text structure (e.g., splitting muqaddimah preamble blocks, breaking isnad chains, mishandling colophon attribution). This prevents guaranteed REJECT votes from Gemini in Stage 4.

**MANDATORY pre-expansion classification (SCH-013, 3 decisions before drafting):**
Before CC writes ANY expansion content, CC must record three classification decisions:
1. **Science category:** From the expanded list in Cross-Science Variation below. If uncertain: `[SCHOLARLY_CHECK_NEEDED]`.
2. **Structural family:** `[ARG]` argument-based (fiqh, uṣūl, ʿaqīdah, manṭiq) / `[NAR]` narrative-based (tārīkh, sīrah) / `[ENT]` entry-based (ṭabaqāt, muṣṭalaḥ) / `[RUL]` rule-based (naḥw, ṣarf) / `[COM]` commentary-structured (sharḥ/ḥāshiya/taʿlīqa). If uncertain: `[SCHOLARLY_CHECK_NEEDED]`.
3. **Text layer position:** matn / sharḥ / ḥāshiya / taʿlīqa / single-layer. If uncertain: `[SCHOLARLY_CHECK_NEEDED]`.

Any `[SCHOLARLY_CHECK_NEEDED]` flag means CC must explicitly state what it does not know. Example: "This appears to be a single ḥadīth + commentary, but I cannot verify whether the bāb heading is semantically integral. [SCHOLARLY_CHECK_NEEDED: Is the bāb the correct atomic unit in this genre?]" Gemini reviews these flags FIRST in Stage 4.

**Expansion process:**
1. **Scope definition:** What does this atom govern? What is IN scope, OUT of scope? Be precise about pipeline phase, text type, scholarly context.
2. **Exception analysis:** When does this NOT apply? CC generates at least 2 candidate exceptions and evaluates each.
3. **Interaction mapping:** Which FPs, prompt rules, and existing atoms interact? Check: SPEC §1.1b (all FPs), current GROUP_SYSTEM_PROMPT, current CLASSIFY_SYSTEM_PROMPT, other atoms in same thematic area, previously finalized atoms.
4. **Concrete examples:** At least one Arabic text scenario where the atom works correctly, and one where misapplication causes damage.
5. **Implementation hypothesis:** WHERE will this land? New FP? Strengthen existing FP? Prompt addition (+ word budget check)? Contract change? Test case? SPEC-only? Deferred?
6. **Blast-radius assessment:** Does implementing this conflict with any finalized atom? Does it require reopening a closed atom?

**Expansion Template (MANDATORY format):**

```markdown
## ATOM [MAQ-ID]: [Name]

### Raw Signal
[Exact owner quote(s) from source_artifacts/*.txt, with file:line references]
Authority: [owner_explicit | owner_consistent_inference | model_only]

### Scope
IN SCOPE: [precise list]
OUT OF SCOPE: [precise list]

### Rule Statement
[The atom expressed as a testable, falsifiable rule]

### Exceptions
1. [Exception scenario] → [ACCEPTED / REJECTED] because [reasoning]
2. [Exception scenario] → [ACCEPTED / REJECTED] because [reasoning]

### Interaction Map
- FP-X: [compatible / tension / conflict — explain]
- Prompt rule Y: [compatible / tension / conflict — explain]
- Atom MAQ-ZZZ: [compatible / tension / conflict — explain]

### Correct Application Example
[Concrete scenario, ideally with Arabic text reference from fixtures]

### Incorrect Application Example
[Concrete scenario showing damage from misapplication — seeds coworker adversarial prompts]

### Cross-Science Variation
[How does this rule apply differently across sciences? Check ALL 19 categories grouped by structural family.

**CLASSIFICATION IS TWO-DIMENSIONAL (v4.2):**
- **Dimension 1 — Structural Family** (determines content-level organization): 7 families below
- **Dimension 2 — Text Layer** (determines commentary relationship): [M] Matn, [S] Sharḥ, [H] Ḥāshiyah, [T] Taʿlīqah/Taqrīr
- **Interleaving type** (for [S]/[H]/[T]): Type 1 = qāla/aqūlu full embedding; Type 2 = qawluhu-marked partial embedding; Type 3 = sequential mīm/shīn alternation
- Every text gets BOTH dimensions: *Fatḥ al-Bārī* = [ENT]+[S] Type 2. *Ḥāshiyat al-Bājūrī* = [ARG]+[H] Type 3. *Ṣaḥīḥ al-Bukhārī* standalone = [ENT]+[M]. Commentary-layer awareness applies to ALL families, not just ḥadīth (v4.2 DR10 fix: [COM] was misclassified as a peer family when it is an orthogonal layer dimension).

**[ARG] Argument-based:**
- Fiqh (madhab attribution, masʾalah structure). *Fatāwā/Nawāzil sub-clause (v4.3 DR11):* If the text is applied fiqh (fatāwā or nawāzil), strictly enforce the Suʾāl-Jawāb indivisible unit to preserve questioner context fused to the ruling. Fatāwā is NOT a separate science — it uses identical epistemological tools as fiqh, merely formatted as dialogue (v4.3 Gemini DR correction).
- Uṣūl al-fiqh (evidence methodology, qiyās chains). *Maqāṣid note:* inductive-cumulative arguments (istiqrāʾ maʿnawī) require preservation of full evidence base — extend Qāʿidah/Farʿ indivisible unit to cover principle-hierarchy structures.
- ʿAqīdah (creedal positions, dalīl cascades — linear, declarative architecture)
- ʿIlm al-Kalām (عِلْم الكَلَام) — dialectical architecture: thesis → shubhah (objection) → radd (refutation), often multi-level nested. DISTINCT from ʿaqīdah: shubhah-radd pair is the atomic unit; nested refutations create boundary-detection requirements absent from declarative ʿaqīdah. Test: al-Juwaynī's *al-Irshād*, 4-level nested refutation of Aristotelian eternalism. (v4.2 DR10)
- ʿIlm al-Farāʾiḍ (عِلْم الفَرَائِض) — computationally structured inheritance: fractional share tables (jadāwil), proportional reduction (ʿawl), surplus redistribution (radd), problem rectification (taṣḥīḥ al-masāʾil) via LCM. A worked inheritance problem is a mathematical procedure, not prose — splitting mid-calculation produces a legally useless fragment. Special named cases (al-gharrāwayn, al-akdariyyah, al-mushārakah) are complete units. [ARG+RUL] hybrid. (v4.2 DR10)
- Manṭiq (syllogistic chains: premise-premise-conclusion)

**[NAR] Narrative-based:**
- Tārīkh/sīrah (chronological narrative)
- Tafsīr (verse-by-verse or thematic commentary)
<!-- Fatāwā/Nawāzil REMOVED as peer science in v4.3 (DR11) — demoted to fiqh sub-clause under [ARG]. See Fiqh entry. -->

**[ENT] Entry-based:**
- Ṭabaqāt/tarājim (biographical dictionaries — each tarjamah is atomic)
- Muṣṭalaḥ al-ḥadīth (definition→criteria→examples structure, NO isnāds)
- Takhrīj/Rijāl (chain variations, narrator critiques, jarḥ wa taʿdīl grading matrices — structurally distinct from standard matn)
- Ḥadīth collections (isnād-matn pairs; bāb = natural atom in Bukhārī) — moved from former [COM] family to [ENT] where it structurally belongs (v4.2 DR10)

**[RUL] Rule-based:**
- Naḥw (grammatical rules + shawāhid)
- Ṣarf (morphological paradigm tables — tabular, not prose)
- Lughah/balāghah (lexicography/rhetoric)
- Qirāʾāt/Tajwīd (recitation variants, pausing symbols waqf/ibtidāʾ, phonetic transmission chains — highly specialized structural rules)

**[ART] Artistic/literary:**
- Adab/Shiʿr (meter-bound wazn + rhyme qāfiyah — qaṣīdah structure means bayt is atomic unit; extracting single bayt from thematic section destroys semantic intent)

**[SEQ] Sequential-progressive (v4.2 DR10):**
- Taṣawwuf / ʿIlm al-Sulūk (تَصَوُّف / عِلْم السُّلُوك) — spiritual development organized as progression through stations (maqāmāt) with explicit prerequisites: tawbah → inābah, ṣabr → tawakkul. Excerpting a later station without its prerequisite corrupts the spiritual pedagogy — the tradition considers this not merely incomplete but potentially harmful. Test: al-Qushayrī's *al-Risālah*, chapter on tawakkul building on prior ṣabr and riḍā. Mandatory prerequisite-chain tracking.

Mark each as: APPLIES UNCHANGED / APPLIES WITH EXCEPTION / DOES NOT APPLY / SCOPED / NEEDS RESEARCH.
**DA-027 rule:** NEEDS RESEARCH on a shared cross-science structural element → blocks finalization for prompt-affecting atoms until scholarly coworker resolves. Domain-specific NEEDS RESEARCH may be tagged SCOPED and finalized.]

### Atomic Integrity Risk
[Does this rule risk splitting indivisible textual units? Check against ALL tiers:

**ALWAYS INDIVISIBLE (splitting is always corruption):**
- Isnād-matn chains (حدثنا...أخبرنا — transmission formula + narrated text)
- **Sharḥ-matn pair (THE MOST CRITICAL — majority of corpus):** Commentary snippet + the base text it explains. In all forms (interleaved, "قوله... أي...", or ص/ش markers), the sharḥ uses anaphoric references requiring the matn. In multi-layer texts: matn segment + sharḥ passage + ḥāshiya passage for that segment are ALL inseparable.
- **Suʾāl-jawāb:** Fatwā question + answer. The jawāb's referential context ("this is permissible") is meaningless without the suʾāl specifying what "this" is.
- **Radd/iʿtirāḍ-jawāb:** Opponent's position (فإن قيل / قال) + author's refutation (قلنا / والجواب). Refutation without stated position is unintelligible.
- **Qiyās (analogical reasoning):** The four arkān — aṣl, farʿ, ʿillah, ḥukm. Removing any one invalidates the argument. Includes the full taʿlīl reasoning chain: takhrīj al-manāṭ → tanqīḥ al-manāṭ → taḥqīq al-manāṭ (the three-stage legal-cause validation process). (expanded v4.2 DR10)
- Muqaddimah preamble blocks (بسم الله + حمدلة + أما بعد)
- Manuscript colophons (تم الكتاب...كتبه)
- Quranic citation blocks (قال تعالى ﴿...﴾)
- Istishhād (poetic evidence: verse + grammatical explanation + attribution)
- Takhrīj (ḥadīth text + source list + grading — separating a ḥadīth from its grading is catastrophic)
- Paradigm tables (jadāwil al-taṣrīf — partial conjugation tables are misleading)
- Nāsikh and Mansūkh (الناسخ والمنسوخ) — abrogating and abrogated texts. If a scholar cites both, separating them is a catastrophic theological and legal failure.
- Qāʿidah and Farʿ/Ḍābiṭ (القاعدة والفرع / الضابط) — legal maxim + illustrative application. A branch excerpted without its governing maxim, or a maxim without example, is incomplete.
- Muṭlaq and Muqayyad (المطلق والمقيد) — unrestricted ruling + its restriction. Separating the restriction from the base ruling makes the reader apply a ruling without its legally binding condition (Gemini v4.0 uṣūlī gap).
- ʿĀmm and Khāṣṣ (العام والخاص) — general ruling + its specification. Presenting only the general without the specific exception misrepresents the law (Gemini v4.0 uṣūlī gap).
- Mujmal and Mubayyan (المُجْمَل والمُبَيَّن) — text in semantic suspension (tawaqquf) until clarification. Structurally STRONGER than Muṭlaq/Muqayyad: the mujmal literally cannot be understood or acted upon without its bayān. The entire uṣūl tradition unanimously holds the mujmal-without-bayān to be inactionable. Test: al-Ghazālī's *al-Mustaṣfā*, "وَآتُوا الزَّكَاةَ" — mujmal until Sunnah specifies amounts. (v4.2 DR10)
- Dalīl + Wajh al-Dalālah (الدَّلِيل ووَجْه الدَّلَالَة) — evidence + the specific hermeneutic angle through which it yields its legal conclusion. Distinct from Qāʿidah/Farʿ: the dalīl is raw text, the wajh is the interpretive key. Same verse can be dalīl for different rulings depending on wajh. Test: al-Rāzī's *al-Maḥṣūl*, "لَا ضَرَرَ وَلَا ضِرَارَ" used for 4+ different rulings. (v4.2 DR10)
- Tarjīḥ block (التَّرْجِيح) — 5-part structure: masʾalah → competing views with madhhab attribution → evidence for each → systematic weighing → verdict. DISTINCT from Khilāf register (which presents without resolving). The verdict derives authority exclusively from the displayed reasoning; a verdict without its chain is a bare assertion. Test: *al-Mughnī*, basmala in al-Fātiḥah — 4 positions, 7 ḥadīth, 3 rational arguments, Ḥanbalī tarjīḥ. (v4.2 DR10)
- Istidrāk/Tanbīh (الاسْتِدْرَاك / التَّنْبِيه) + referent — backward-pointing correction/qualifier that modifies a preceding statement. The istidrāk without its referent is meaningless; the referent without its istidrāk propagates the error the author intended to correct. Test: al-Nawawī's *al-Majmūʿ* tanbīh notes restricting general fiqh rulings to specific conditions. (v4.2 DR10)
- Waqf markers (عَلَامَات الوَقْف) in Qirāʾāt/Tajwīd texts + textual context — the Quranic tradition's own indivisibility annotations. وقف لازم (م) = mandatory stop (continuing corrupts theological meaning); لا = stopping forbidden (pausing creates doctrinal error, e.g., "لا إله" without "إلا الله"); muʿānaqah (∴) = paired alternatives. Applies to [RUL] Qirāʾāt/Tajwīd specifically. Test: Quran 6:36 waqf after "yasmaʿūn". (v4.2 DR10)

**USUALLY INDIVISIBLE (split only when exceeding maximum excerpt size with natural sub-boundaries):**
- **Khilāf register:** Complete disagreement survey for one masʾalah. Presenting only one madhhab misrepresents the law.
- **Taqsīm (taxonomy trees):** "X is of three types..." — splitting after type 2 means the reader has an incomplete taxonomy and may not know it (FP-5 silent corruption).
- Internal cross-references (كما تقدم → target)
- Sabab al-Nuzūl / Sabab al-Wurūd (سبب النزول / سبب الورود) — historical context paired with the verse/hadith. Removing the sabab decontextualizes the text.
- Ijāzah chain (سِلْسِلَة الإِجَازَة) — distinct from isnād: authorizes transmission rights for entire texts, not specific content. In ṭabaqāt works, integral to biographical entries. Must not be split internally. "Usually" rather than "always" because prefatory ijāzah wrappers can sometimes be separable metadata, while embedded biographical ijāzah is integral. Test: al-Dhahabī's *Siyar*, ijāzah chain establishing a scholar's authority from al-Bukhārī. (v4.2 DR10)

**CONDITIONALLY INDIVISIBLE (context-dependent):**
- Ijmāʿ + noted dissent. Separating the exception transforms a qualified consensus into an absolute one.
- Sharṭ-jawāb (conditional-consequence). Presenting only the condition leaves the ruling incomplete.
- Mafhūm and Manṭūq (مفهوم ومنطوق) — when an author explicitly states the contrary implication (mafhūm al-mukhālafah) immediately following the stated ruling (manṭūq), they must be kept together to preserve the author's precise intent.
- Al-Muqsam bih wa al-Muqsam ʿalayh (المقسم به والمقسم عليه) — the oath and the subject of the oath; separating them corrupts the rhetorical and legal force.
- Taḥqīq apparatus (الجِهَاز التَّحْقِيقِي) — critical edition apparatus containing variant readings, ḥadīth takhrīj notes, and editorial corrections. Indivisible when variant readings alter legal or doctrinal meaning (e.g., "يجوز" vs "لا يجوز"); separable for orthographic-only variants. Condition: does the variant change the ruling or doctrine? Test: Shuʿayb al-Arnaʾūṭ's *Musnad Aḥmad* where a footnote records a legal ruling reversal between manuscripts. (v4.2 DR10)

If any risk: document the safeguard. If uncertain whether a unit is indivisible in this context: `[SCHOLARLY_CHECK_NEEDED]`.]

### Multi-Layer Text Awareness (SCH-016)
[If the source text has multiple layers (matn/sharḥ/ḥāshiya/taʿlīqa): (a) Which layer is the TARGET of this atom? (b) Which LOWER layers must be included for the target to be intelligible? (c) Does the atom's boundary in the target layer align with natural boundaries in lower layers? An excerpt at layer N MUST include corresponding text at all layers below N, down to the matn segment that anchors the discussion. If single-layer text: "N/A — single layer."]

### Honorific & Transmission Formula Preservation (SCH-017, SCH-019)
[When this atom mentions any scholar, prophet, or companion: verify honorifics in source text are preserved exactly (ﷺ, رضي الله عنه, رحمه الله). Honorifics are integral text, NOT optional metadata. When the atom touches ḥadīth content (identifiable by: حدّثنا / أخبرنا / سمعت / عن / قال): invoke FP-11 isnād-matn integrity. Transmission formulas indicate strength — they CANNOT be removed, altered, or truncated.]

### Implementation Hypothesis
Target: [new FP / strengthen FP-X / prompt addition (+N words) / contract change / test case / SPEC-only / deferred]
Word budget impact: [current GROUP: N/1500, CLASSIFY: M/~1000. After change: N+K/1500]

### Expansion Fidelity Indicator (v5.0 DR17, او كما قال convention)

For EACH claim in the expansion, CC MUST declare the fidelity level:

| Level | Marker | Meaning | Verification Threshold |
|-------|--------|---------|----------------------|
| `exact` | (none) | Verbatim owner quote — CC reproduces the owner's exact words | Ḥāfiẓ (lafẓī): word-for-word match required |
| `paraphrased` | او كما قال | CC rephrases the owner's statement preserving intent | Faqīh (maʿnawī): meaning match required; hedging marker preserved in all downstream artifacts |
| `interpreted` | او نحو هذا | CC infers owner's intent from context, not direct statement | Faqīh (maʿnawī): meaning match; coworker MUST audit fidelity ("What in the anchors proves this claim?") |

**Rules:**
- Every claim in the Rule Statement section MUST have a fidelity level
- `exact` claims MUST include the file:line reference to the verbatim source
- `paraphrased` and `interpreted` claims MUST include the nearest verbatim anchor from source_artifacts/*.txt
- The fidelity marker TRAVELS through all lifecycle stages — coworkers see it at Stage 4, synthesis preserves it at Stage 5, the ledger records it at Stage 7
- **Mandatory-exact text types (Gemini CLI correction):** Devotional formulae (dhikr, duʿāʾ), jawāmiʿ al-kalim (concise prophetic sayings), and any directive where exact phrasing carries legal/doctrinal weight MUST be `exact` — `paraphrased` or `interpreted` is FORBIDDEN for these text types regardless of context
- **The 5 conditions for meaning-based expansion (riwāyah bi-l-maʿnā):** Before using `paraphrased` or `interpreted`, verify: (1) CC has deep domain understanding, (2) no change to legal implications, (3) text is not devotional, (4) text is not jawāmiʿ al-kalim, (5) if doubtful, append the hedging marker. If ANY condition fails → `exact` required.

**Anchor-bound expansion (v5.0 DR16):** The EXPANDED→CHALLENGED stages MUST maintain verbatim source anchors. G-CHALLENGED (§4.4 exit gate) CANNOT pass unless at least one challenger audits fidelity: "What in the anchors proves this claim?" This prevents interpretation drift during expansion.

### Natural Teaching Unit (الوحدة التعليمية الطبيعية) — CONDITIONAL (v4.3 DR11)
**Trigger:** MANDATORY for CONTENT atoms (dealing with scholarly texts, legal definitions, or substance of Islamic sciences). For STRUCTURAL or ENGINEERING atoms (formatting, boundary logic, tagging, relay constraints), auto-fill "N/A — System Logic" and skip evaluation.

[What is the organic knowledge unit for THIS specific text's genre? (mas'alah in fiqh, tarjamah+hadith+commentary in hadith encyclopedias, bayt+qa'idah+shawahid in nahw, thematic verse group + athar in tafsir, attribute + evidence cascade in aqidah). Would the proposed rule PRESERVE or FRAGMENT this natural unit?]

### Graduated Learning Level (مستوى التدرج) — CONDITIONAL (v4.3 DR11)
**Trigger:** Same as NTU above — CONTENT atoms only. Classical texts already encode their own tadarruj level (Mukhtaṣar = beginner, Sharḥ = intermediate, Mabsūṭ = advanced); re-deriving this for every atom wastes context without adding information.

[Is the source text beginner (مختصر/مبتدئ — memorize rulings only), intermediate (متن مع شرح/متوسط — understand evidences), or advanced (مبسوط/منتهي — master comparative analysis)? The proposed rule MUST respect the text's intended depth: do not inject complexity into beginner texts or truncate analysis in advanced texts.]

### Blast-Radius Assessment
[No conflicts with finalized atoms | Conflicts with ATOM-X: resolution plan]
[Cross-reference orphaning check: would this atom's boundary orphan any كما تقدم / سيأتي references from their targets?]

### Cross-Science Dependencies (v4.3 DR11)
[If this atom establishes a rule that could interact with atoms from OTHER structural families (e.g., a ḥadīth boundary rule affecting how fiqh texts cite the same ḥadīth, or a naḥw grammar rule affecting how tafsīr citations are bounded), list the dependency explicitly: "This atom interacts with [family] because [reason]. Future atoms in [family] must reference this rule." This preserves holistic scholarly connections (waḥdat al-ʿulūm) across sessions without requiring all related atoms in the same session. If no cross-science dependencies: "None identified."]
```

**Template section requirements by atom lane (v4.0):**
- **Full Lane (prompt/contract-affecting):** Sections 1-13 ALL mandatory. CC writes all sections locally. Subagents may GATHER evidence (e.g., "find a nahw text where this rule fails") but CC WRITES the final scholarly judgment. Dispatching ownership of sections 8-13 is FORBIDDEN — Gemini CLI review confirmed this "severs the orchestrator's cognitive link to cross-rule implications."
- **Full Lane (SPEC-structural):** Sections 1-13 ALL mandatory. CC writes sections 1-7 and the final verdicts for 8-13. Subagents may draft evidence for sections 8-13 which CC reviews and edits.
- **Light Lane:** Sections 1-5 mandatory (scope, rule, exceptions, hypothesis, blast-radius). Sections 8-13 are EVALUATED but may be abbreviated: "No cross-science risk identified. Checked: [list 18 sciences]. No atomic integrity risk. Checked: [30 indivisible units]." Sections 6-7 (correct/incorrect examples) optional for Light Lane. NOTE: Gemini CLI confirmed "there is no such thing as purely editorial in classical Arabic" — even Light Lane atoms must evaluate sections 8-13 to prove no hidden cross-science risk.

**Evidence minimum (v4.1, anti-checkbox-theater):** For Cross-Science Variation and Atomic Integrity Risk, marking "checked" or "APPLIES UNCHANGED" is INVALID without evidence. Minimum: (a) 2 sciences from 2 DIFFERENT Structural Families (e.g., one [ARG] + one [NAR]) with concrete Arabic counterexamples demonstrating the rule holds, OR (b) 1 science with a named classical-genre exemplar AND an explicit non-applicability rationale for 2 sciences from different families. Cross-family validation is required because rules safe within one family (e.g., [ARG] fiqh) can corrupt a different family (e.g., [ENT] ṭabaqāt) — Gemini v4.1 finding. "No cross-science risk identified. Checked: [18 sciences]." is ONLY valid for Light Lane after per-science evaluation.

**Per-atom attention isolation (v4.1):** Expansion MUST be per-atom. Grouped expansion is FORBIDDEN. Each atom gets a distinct Stage 3 document and distinct coworker prompts (no shared "combined prompt" except in `research` DR class). If atoms interact, expand each separately then document interactions in the Interaction Map section. Evidence: each atom must have a unique expansion document identifier in the ledger.

**Exit gate (G-EXPANDED):**
- [ ] Scope defined with IN/OUT boundaries
- [ ] At least 2 exceptions evaluated
- [ ] Interaction mapping completed against FPs and current prompt
- [ ] At least 1 correct-application and 1 incorrect-application example
- [ ] Implementation hypothesis stated
- [ ] Blast-radius check passed (no unresolvable conflicts)
- [ ] If prompt-affecting: word budget has headroom or compression strategy proposed

### 4.4 Stage 4: CHALLENGED

**Entry:** G-EXPANDED passed.
**Actor:** CC dispatches to coworkers. CC waits for returns.
**Duration:** Variable (depends on coworker availability; up to 48h per DR timeout).

CC prepares specialized prompts tailored to each coworker's strength. Each prompt includes the expansion document from Stage 3.

**Codex CLI dispatch (Contract Guardian):**
```
codex exec "
ATOM: [MAQ-ID] — [Name]
EXPANSION: [paste expansion document]

PRIMARY (contract guardian):
1. Read: contracts.py, phase2_group.py GROUP_SYSTEM_PROMPT, SPEC.md §1.1b, ledger recent entries
2. What contracts change? What validators need updating? What tests are affected?
3. Does check_prompt_spec_sync.py still pass?
4. Implementation cost: files, lines, test count

ADVERSARIAL:
5. Worst runtime failure if implemented naively?
6. Subtle regression deterministic tests would miss?

OUTPUT: Per-atom verdict (ACCEPT/MODIFY/ITERATE/REJECT), contract impact, regression risk (HIGH/MEDIUM/LOW)
"
```

**Gemini CLI dispatch (Scholarly Auditor):**
```
gemini -p "
ATOM: [MAQ-ID] — [Name]
EXPANSION: [paste expansion document]

PRIMARY (scholarly auditor):
1. Read: SPEC.md §1.1b, arabic-scholarly-conventions.md, ledger recent entries
2. Is this correct across fiqh, hadith, nahw, tafsir, usul, aqidah, lughah/balaghah, tarikh/sirah? Arabic examples per science.
3. Find a counterexample: real Arabic text where this rule fails.
4. Blast radius across normalization, taxonomy, synthesis engines?

ADVERSARIAL:
5. Worst scholarly failure? Name a specific book/passage.
6. Which genre is most at risk?

OUTPUT: Per-atom verdict (ACCEPT/MODIFY/ITERATE/REJECT), per-science assessment, counterexample, blast radius
"
```

**ChatGPT DR dispatch (Architecture + Error Patterns — relay via owner):**
```
Read these files from the rayanino/kr repository:
- engines/excerpting/SPEC.md §1.1b
- engines/excerpting/reference/FOUNDATIONS_HARDENING_LEDGER.md (recent entries)
- engines/excerpting/src/phase2_group.py (lines 43-209)

ATOM: [MAQ-ID] — [Name]
EXPANSION: [paste expansion document]
Codex found: [summary]. Gemini found: [summary].

QUESTIONS:
1. What did Codex and Gemini MISS?
2. Construct a catastrophic scenario: named book, specific passage, confidently wrong excerpt.
3. Does this + other recent atoms create an emergent compound failure?
4. Silent corruption paths (T-1 through T-7) opened or closed?
5. ARCHITECTURAL: Is the current prompt structure optimal for this atom? What refactoring prevents the issue?

OUTPUT per atom: verdict, findings, missed-by-CLIs, catastrophic scenario, architectural recommendations, confidence
```

**Claude DR dispatch (Scholarly Reasoning + Boundary Quality — relay via owner):**
```
Read these files from the rayanino/kr repository:
- engines/excerpting/SPEC.md §1.1b
- engines/excerpting/reference/FOUNDATIONS_HARDENING_LEDGER.md (recent entries)
- .claude/rules/arabic-scholarly-conventions.md

ATOM: [MAQ-ID] — [Name]
EXPANSION: [paste expansion document]
Codex found: [summary]. Gemini found: [summary].

QUESTIONS:
1. What did Codex and Gemini MISS from a scholarly reasoning perspective?
2. Does the proposed boundary risk DECONTEXTUALIZATION — stripping a passage from the argument chain that gives it meaning?
3. Would a student of [relevant Islamic science] understand this excerpt as a standalone study unit?
4. Does this atom preserve the author's dialectical structure (claim → evidence → rebuttal → synthesis)?
5. Attribution safety: does this risk confusing copyist (ناسخ) with author (مؤلف), or editorial (محقق) with original text?

OUTPUT per atom: verdict, scholarly findings, decontextualization risk, study-unit assessment, confidence
```

**Gemini DR dispatch (Islamic Pedagogy + Genre Validation — relay via owner, FILE UPLOADS REQUIRED):**
```
[Owner: upload these files to the Gemini session: SPEC.md §1.1b, FOUNDATIONS_HARDENING_LEDGER.md recent entries, arabic-scholarly-conventions.md]

ATOM: [MAQ-ID] — [Name]
EXPANSION: [paste expansion document]
Codex found: [summary]. Gemini found: [summary].

QUESTIONS:
1. As a study unit, does the excerpt this atom would produce match how [specific Islamic science] is ACTUALLY TAUGHT and STUDIED?
2. What is the "natural atom" of knowledge in this genre? Does the proposed rule align with it?
3. Would a traditional Islamic teacher (شيخ) consider this excerpt boundary natural, or would they object?
4. Does this atom respect the graduated learning methodology (متدرج) — from basic to advanced within the science?
5. Genre-specific check: for this specific text type (شرح/حاشية/متن/رسالة), is the proposed rule appropriate?

OUTPUT per atom: verdict, pedagogical assessment, natural-atom alignment, genre suitability, confidence
```

**BLINDED TIEBREAK DR template (use ONLY for §5.4 step 5 escalation):**
```
[DR source — relay via owner]:
ATOM: [MAQ-ID] — [Name]
EXPANSION: [paste expansion document]
RAW SOURCE: [paste relevant owner quotes from source_artifacts/*.txt]

You are an INDEPENDENT evaluator. Do NOT seek consensus with other reviewers.

QUESTIONS:
1. Is the proposed rule correct for this Islamic science and text genre?
2. Find a concrete counterexample: real Arabic text where this rule fails.
3. Does this rule risk splitting any indivisible textual unit?
4. Would a student of this science understand an excerpt governed by this rule?

OUTPUT: Independent verdict (ACCEPT/MODIFY/ITERATE/REJECT), counterexample, risk assessment, confidence.
```

**Dispatch rules:**
- **MANDATORY (HR-23):** Every dispatch prompt — Codex, Gemini, DR, subagent — MUST pass through `/prompt-architect` before sending. Draft the prompt, optimize it, send the optimized version. No exceptions.
- Codex and Gemini dispatch SIMULTANEOUSLY (independent)
- DR dispatch can happen simultaneously OR after CLI returns (CC decides based on whether CLI findings should feed DR)
- CC does NOT proceed to Stage 5 until at least 2/3 coworker reports received
- If one coworker unavailable after 48h: proceed with 2/3, mark atom PRELIMINARY, document gap
- If 2+ coworkers unavailable: STOP. Report to owner.

**Exit gate (G-CHALLENGED):**
- [ ] Received the minimum coverage tier required by §5.1 for this atom's change type — NOT merely "2 of 3 reports." If a required specialty reviewer is missing (e.g., Gemini for Arabic scholarly on a prompt-affecting atom), atom MUST remain PAUSED-CHALLENGED, not PRELIMINARY.
- [ ] Each report is structured (verdict + findings, not freeform)
- [ ] Reports recorded in ledger
- [ ] If fewer than 3 reports: gap documented with reason

### 4.5 Stage 5: SYNTHESIZED

**Entry:** G-CHALLENGED passed.
**Actor:** CC orchestrator. This is CC's core intellectual work — deciding doctrine.
**Duration:** 10-15 minutes.

**Process:**

1. **3-column comparison table:**

| Dimension | Codex | Gemini | DR |
|-----------|-------|--------|----|
| Scope correct? | [finding] | [finding] | [finding] |
| Exceptions valid? | [finding] | [finding] | [finding] |
| Implementation safe? | [finding] | [finding] | [finding] |
| Adversarial scenario | [scenario] | [scenario] | [scenario] |
| Verdict | [ACCEPT/MODIFY/ITERATE/REJECT] | [same] | [same] |

2. **Consensus determination (see §5 for full voting rules):**
   - 2+ ACCEPT/MODIFY (with accepted modifications) and 0 REJECT = **CONFIRMED**
   - Any single REJECT = **BLOCKED** — must address the finding
   - Split vote = **DISPUTED** — apply resolution hierarchy (§5.4)
   - <2 reports = **INSUFFICIENT** — stays PRELIMINARY

3. **Expansion refinement:** Update the expansion document with coworker-discovered exceptions, scope tightening, or new interactions.

4. **Implementation decision:** Finalize what changes to which files. Must be specific: file path + what changes, not "update the SPEC."

5. **Owner question (if needed):** If synthesis reveals a study-experience question only the owner can answer, formulate ONE concrete question with examples. Ask NOW, not deferred.

**Exit gate (G-SYNTHESIZED):**
- [ ] 3-column table exists in ledger
- [ ] All coworker disagreements resolved with recorded reasoning
- [ ] Implementation decision is specific (file paths + exact change description)
- [ ] If owner question needed: question asked and answer received
- [ ] If `model_only` authority: owner has confirmed intent

### 4.6 Stage 6: IMPLEMENTED

**Entry:** G-SYNTHESIZED passed.
**Actor:** CC orchestrator (writes code/docs).
**Duration:** 5-30 minutes depending on change scope.

**Process:**
1. Make the changes:
   - SPEC: add to §1.1b (new FP) or relevant §6 subsection
   - Prompt: update `phase2_group.py` AND SPEC §5.3.2 code block (BOTH — check sync)
   - Contract: update `contracts.py` with backward-compatible additions
   - Tests: red-team atoms → actual pytest cases
   - Deferred: entry in `DEFERRED_IDEAS.md` with full expansion and reason

2. Run validation suite:
   - `python -m pytest engines/excerpting/tests/ -q` (excluding LLM integration) — zero regressions
   - `python -m pyright <modified_files>` — zero errors
   - `python scripts/check_prompt_spec_sync.py` — PASSED
   - If prompt-affecting: `python scripts/atom_test.py --package taysir --chunk 0` — empirical validation

3. If validation fails: fix, re-run. Do not proceed until green.

**Note on grouped implementation:** When 2-3 atoms affect the same SPEC section or prompt, their implementations MAY be designed together for coherence. But each atom MUST have been individually analyzed through Stages 2-5 before grouping. The group is never more than 3 atoms. Each atom is briefed to the owner individually (Stage 7).

**Word budget tracking (MANDATORY for prompt-affecting atoms):** After every prompt edit, record in the ledger: `GROUP before: N words → delta: +K → after: N+K → remaining: 1500-(N+K)`. Same for CLASSIFY. This running ledger prevents word-budget exhaustion across grouped implementations.

**Reopen Protocol (when implementation forces changes to a FINALIZED atom):**
If validation failure at Stage 6 requires modifying a previously FINALIZED atom:
1. The current atom HALTS at Stage 6 (does not proceed to CLOSED).
2. The previously FINALIZED atom's status is demoted to **REOPENED** in the ledger with: reason for reopening, which current atom triggered it, what specific change is needed.
3. The REOPENED atom re-enters the lifecycle at Stage 3 (EXPANDED) with the proposed modification. It does NOT need to re-source (Stage 2) since the original sourcing is still valid.
4. The REOPENED atom must pass through Stages 3-7 again, including coworker challenge (Stage 4). Minimum coverage: same tier as the original finalization. If the original was FINALIZED with 3/3 coworkers, the reopen must also get 3/3.
5. Only after the REOPENED atom passes Q-CLOSED again can the HALTED atom resume at Stage 6.
6. Both atoms' ledger entries are linked: "REOPENED by MAQ-XXX" and "Triggered reopen of MAQ-YYY".

**Absolute Reopen Authority — Ḥaqq al-Istidrāk (v5.0 DR15/DR17):**
Batch-verification sessions (§3A) are granted authority to reopen ANY finalized atom — regardless of coworker consensus, owner approval, or Q-CLOSED status — if that atom violates an F1/F2 foundational directive discovered during muqābalah bi-l-aṣl. Every reopened atom requires a formal **Istidrāk justification** citing the specific forensic audit gap. This mirrors the classical mustadrak tradition (al-Dāraquṭnī's corrections to al-Bukhārī/Muslim).

**Istidrāk Remediation Chain (v5.0 DR17):**
Every atom reopening MUST create a formal istidrāk entry in the ledger:
- `istidrак_id`: unique identifier
- `references`: the prior version (atom ID + generation number)
- `generation`: integer (0 = original, 1+ = correction level)
- `gap_type`: nuqṣān (omission) / takhfīf (softening) / taḥrīf (distortion) / idrāj (interpolation)
- `evidence`: what forensic audit finding motivated the correction
- `correction`: the revised content
- `genre_label`: mustadrak (supplements omission) / takmila (completes) / ṣila (continues) / istidrāk (corrects)

The chain is indexed by generation: original → istidrāk-1 → istidrāk-2 → ... This ensures that across a 15-30 session campaign, the full correction genealogy is reconstructable. Al-Dāraquṭnī → al-Ḥākim → al-Dhahabī → Ibn al-Mulaqqin spans 5 centuries of traceable corrections. Our chain must do the same across 5 months.

**Exit gate (G-IMPLEMENTED):**
- [ ] All targeted files changed
- [ ] pytest passes with zero regressions
- [ ] pyright clean on modified files
- [ ] prompt-SPEC sync passes
- [ ] If prompt-affecting: empirical validation shows no degradation

### 4.7 Stage 7: CLOSED

**Entry:** G-IMPLEMENTED passed.
**Actor:** CC orchestrator.
**Duration:** 5-10 minutes.

**Process:**

1. **Owner brief (MANDATORY, per-atom):**
   Present to the owner:
   - What the atom IS (1-2 sentences, non-technical language)
   - What changed (which principle added/strengthened, which rule added to prompt)
   - What was REJECTED from coworker findings, and why
   - What residual risks remain
   - Any question for the owner (if deferred from Stage 5)
   
   The brief is post-decision (owner does not vote on consensus), but owner objections on content quality and reading experience are safety-critical and trigger automatic reopening per §4.10. The owner's reaction is both signal for future atoms AND a potential veto — "feels off" from the owner must be investigated, not dismissed as "future signal."

   NOTE: The 4-element brief artifact above is ALWAYS per-atom in the ledger. Owner-facing delivery follows §4.15 (per-atom for first 50, batchable after).

2. **Ledger update (MANDATORY):**
   Full disposition entry with:
   - Atom name and MAQ-ID
   - Sources read (file paths + exact quotes)
   - Authority level
   - Expansion summary
   - Coworker reports (all received, key findings per coworker)
   - Synthesis decision and reasoning
   - Implementation changes (file:line)
   - Tests added/run
   - Empirical validation result (if applicable)
   - Residual risks
   - Final status (mutually exclusive terminal states):
     - **CLOSED-IMPLEMENTED**: Q-CLOSED passed, implementation artifact exists in code/SPEC/prompt/tests
     - **CLOSED-VERIFIED**: Atom was already correctly captured in existing FPs/rules; verification-only, no new change needed
     - **CLOSED-PRELIMINARY**: Q-CLOSED passed but with <3 coworker reports (subject to Preliminary Debt Ceiling, see §4.9)
     - **DEFERRED-RECORDED**: NOT Q-CLOSED eligible. Atom is documented but not implemented. Cannot be counted as "atoms closed." Tracked as debt with explicit revisit condition. Must remain visible in queue with status DEFERRED.
     - **REJECTED**: Atom evaluated and explicitly rejected with coworker-supported reasoning

3. **Blast-radius forward check:** Now that this atom is implemented, does it affect the NEXT atoms in the queue? Check for cascade effects.

4. **Queue status update:** Mark the atom's status in MERGED_ATOM_QUEUE.md.

### 4.8 Q-CLOSED Gate (Definition of "Done")

An atom is CLOSED if and only if ALL 11 criteria are TRUE:

| # | Criterion | How Verified |
|---|-----------|-------------|
| Q-1 | Raw owner source text was read and quoted | Ledger has exact owner quotes with file:line |
| Q-2 | Authority level classified | Ledger has authority field; model_only confirmed by owner |
| Q-3 | Atom EXPANDED into complete specification | Expansion document exists with scope, exceptions, examples |
| Q-4 | Minimum 2 coworker reports received (CC + 1 external minimum) | Dispatch log entries exist; reports structured |
| Q-5 | Coworker findings synthesized in 3-column table | Synthesis table in ledger |
| Q-6 | Implementation artifact produced (CLOSED-IMPLEMENTED only; DEFERRED-RECORDED is NOT Q-CLOSED eligible) | Git diff or ledger records file:line change |
| Q-7 | No regression: pytest pass, pyright clean, sync pass | Test run output recorded |
| Q-8 | Empirical validation IF prompt-affecting | atom_test.py output or "SPEC-only, no empirical needed" |
| Q-9 | Blast-radius check: no conflict with finalized atoms | Explicit check recorded |
| Q-10 | Per-atom brief artifact in ledger with 4 required elements | Ledger entry contains what/changed/rejected/risks for THIS atom |
| Q-11 | Ledger fully updated | Complete entry per the template above |
| Q-12 | Outcome spot-check (for any atom tagged 'cross-science' OR touching any ALWAYS INDIVISIBLE unit OR scoped to structurally rigid sciences: Naḥw, Ṣarf, Qirāʾāt/Tajwīd, Adab/Shiʿr): run mini-fixture through relevant pipeline step, record observed vs expected behavior | atom_test.py output on representative Arabic passage, or written analysis with specific Arabic example |
| Q-13 | **Regression gate passed (v5.0 §4.18):** If this atom changed the prompt or SPEC, `scripts/run_regression_suite.py` must have exited 0 AFTER the change. If no prompt/SPEC change: "N/A — no prompt/SPEC modification." | regression_runs/<run_id>/summary.json with exit 0, or "N/A" with justification |
| Q-14 | **Doctrine coherence verified (v5.0 §4.19):** If this atom introduces or modifies a MUST/NEVER/ALWAYS rule, `scripts/prompt_coherence_lint.py` must have exited 0 confirming no conflicting quantifiers with existing rules. If no rule change: "N/A — no rule modification." | coherence_report.md with exit 0, or "N/A" with justification |

If ANY criterion is FALSE, the atom is NOT CLOSED. It stays at the relevant earlier stage.

**Machine verification (DA-001):** Build `scripts/verify_atom_closure.py` to check objective Q-CLOSED signals: ledger entry exists with required fields, queue status matches, referenced files exist in git, pytest/pyright/sync outputs recorded, prompt word counts recomputed deterministically. This script should be run before each commit. Human-judgment criteria (Q-1 faithfulness, Q-10 comprehension) remain ledger-attested but should include specific evidence (exact quotes, brief timestamps).

### 4.9 Preliminary Debt Ceiling (DA-008)

CLOSED-PRELIMINARY atoms (missing full coworker coverage) accumulate debt. Uncontrolled debt becomes permanent-by-neglect.

**Rules:**
- At session start, count PRELIMINARY atoms older than 2 sessions or totaling >5.
- If debt exceeds either threshold: session MUST spend its first phase clearing preliminaries (getting missing coworker votes) before processing any new RAW atoms.
- Clearing means: re-dispatch to the missing coworker with the original expansion. If coworker returns ACCEPT/MODIFY → upgrade to CLOSED-IMPLEMENTED. If ITERATE/REJECT → demote to REOPENED.
- Exception: if the missing coworker is DR and owner relay is unavailable, the session may process up to 3 new atoms while waiting, but must attempt DR dispatch within the session.

**Hard fallback (v4.1):** If the missing coworker is DR and owner relay is unavailable for >2 consecutive sessions OR >7 calendar days, the atom MUST be downgraded from CLOSED-PRELIMINARY to REOPENED and re-enter Stage 4 using only available coworkers (Codex+Gemini), with the DR slot explicitly waived as 'UNAVAILABLE' and logged as a risk in the ledger. Preliminary is not a parking lot — debt that cannot be cleared must be resolved by downgrade, not deferred indefinitely.

### 4.10 Owner Objection Mechanism (DA-012)

When the owner reads an atom brief (Stage 7) and says "this is wrong" or "that's not what I meant":

1. The atom is automatically demoted to **REOPENED** regardless of coworker consensus.
2. CC must surface the specific conflict between the atom's implementation and the owner's objection.
3. The atom re-enters at Stage 3 (EXPANDED) with the owner's objection as new input.
4. Minimum 2 coworkers must re-review the revised expansion.
5. For excerpt-definition or khilaf/tarjih atoms: escalate to ALL 6 sources.

Owner objection on **content quality and intent** overrides all coworker consensus. Owner objection on **technical implementation** is treated as signal (per existing rule) — CC + coworkers resolve.

### 4.11 Prompt Refactor Gate (DA-015/DA-028)

The GROUP prompt has a 1500-word hard cap. The CLASSIFY prompt has a ~1000-word soft cap.

**Trigger:** When either prompt exceeds 80% capacity (GROUP >1200 words, CLASSIFY >800 words):
1. **FREEZE** new prompt-affecting atoms until refactor completes.
2. **Refactor pass:** CC + Codex review the entire prompt for: redundant rules (merge), low-priority rules (move to deterministic validators or Phase 3 gates), verbose rules (compress), rules that can become structured rubrics.
3. **Gemini validates** that refactored prompt preserves scholarly meaning.
4. After refactor: record new word count, log what was removed/compressed, resume atom processing.

**Medium-term strategy:** Move structural rules that can be checked deterministically (e.g., minimum word count, segment contiguity, boundary ordering) out of the LLM prompt into deterministic validators/tests. Reserve prompt space for rules that REQUIRE LLM judgment (scholarly boundaries, self-containment, attribution).

**Refactor Safety Checklist (v4.1, MANDATORY):**
1. For every removed/merged rule: record destination (kept in prompt / moved to validator / moved to tests / deprecated) in a "Rule Migration Map" artifact.
2. Run `atom_test.py` on at least 3 fixtures spanning 3 different Islamic sciences (not just taysir).
3. Gemini CLI must supply at least 1 counterexample check for each removed rule class.
4. If any fixture shows regression: HALT refactor, restore previous prompt, investigate.

### 4.12 Prompt Coherence Review (DA-029)

**Trigger:** After every 5 prompt-affecting atoms, OR immediately when the Prompt Refactor Gate (§4.11) trips.

**Review checks (from Gemini's Islamic scholarly framework):**
1. **Contradictions (تعارض):** Do any two rules demand opposite behaviors on the same text boundary?
2. **Hierarchy/Priority:** Is the fallback resolution explicitly defined when rules conflict? (e.g., "Structural Integrity > Word Count Limit")
3. **Overfitting (إفراط في التخصيص):** Is the prompt accumulating micro-fixes that should be refactored into a single robust heuristic?

**Process:** CC reads the FULL prompt, dispatches Codex (structural coherence) + Gemini (scholarly coherence). Both review the prompt AS A WHOLE, not per-atom diffs. Findings are implemented before the next atom proceeds.

### 4.13 Scholarly Integrity Arbitration (DA-018)

When owner intent conflicts with scholarly correctness (e.g., owner requests a heuristic that would split an indivisible textual unit):

**Rule: Scholarly Integrity > Owner Intent when the implementation would corrupt text structure.**

1. CC **blocks** implementation of the owner-conflicting directive.
2. CC **surfaces** the specific conflict to the owner with concrete Arabic examples showing what would break.
3. CC proposes two options: (a) intent-faithful implementation with documented scholarly risk, (b) scholar-faithful implementation with explanation of how it differs from the owner's request.
4. Owner chooses. If owner insists on the intent-faithful option despite documented risk, CC implements with an explicit `SCHOLARLY_RISK_ACCEPTED` tag in the ledger.

This does NOT apply to preference-level decisions (granularity, formatting). It applies ONLY when implementation would damage: isnad chains, attribution integrity, indivisible textual units, Quranic citation boundaries, **madhhab-specific structural norms, edition integrity, or authorship provenance**.

**Additional coverage domains (v4.2 DR10):**

5. **Madhhab-context rule:** When structural templates admit variant definitions across legitimate schools (e.g., qiyās arkān count differs between Ḥanafī and Shāfiʿī traditions), identify the madhhab context via attribution signals (وَعِنْدَنَا, وَالمَذْهَب, وَالرَّاجِح per `arabic-scholarly-conventions.md`) and apply that school's norms. When madhhab is undetermined: flag ambiguity, NEVER default to any single school's framework.
6. **Edition metadata:** Track publisher, editor (muḥaqqiq), edition year. Flag known-problematic publishers (e.g., Dār al-Kutub al-ʿIlmiyyah). When editions disagree on content: preserve variant as Class B provenance note per FP-5, never silently choose one reading.
7. **Authorship-confidence:** Classify as: verified / attributed-with-scholarly-consensus / attributed-with-dispute / compiled-posthumous. Never present contested attributions (e.g., al-Ghazālī's "several hundred attributed works, many spurious") as settled facts.
8. **Genre-flexibility:** When a text's genre classification is ambiguous or multi-layered (e.g., *al-Mughnī* is both sharḥ and independent encyclopedia), apply the structural rules of the MOST RESTRICTIVE applicable genre to prevent under-protection of indivisible units.

### 4.14 Atom Complexity Triage (PROC-004)

Not all atoms require the full 7-stage lifecycle. After Stage 1 (RAW), CC classifies each atom into one of two lanes:

**FULL LANE (default):** All 7 stages, all coworker minimums. Required for:
- Prompt-affecting atoms
- Contract-affecting atoms
- SPEC-structural atoms (new/modified FPs)
- Cross-science or cross-engine atoms
- Any atom where the owner's raw text contains ALL-CAPS, conditional reasoning, or expressed uncertainty

**ABSOLUTE PROHIBITION:** No `model_only` atom is eligible for Light Lane. Owner confirmation is REQUIRED before ANY implementation or closure outcome (including CLOSED-VERIFIED), regardless of lane. model_only atoms MUST use Full Lane to ensure Stage 5 owner confirmation gate is reached.

**LIGHT LANE:** Stages 2-3-6-7 only (skip CHALLENGED + SYNTHESIZED). Requires 1 external coworker spot-check (Codex or Gemini). Eligible ONLY for:
- Editorial/typographical corrections to existing SPEC text
- Verification-only atoms (confirming existing FPs already cover the atom)
- SPEC-doctrinal atoms that add no behavioral change (no prompt/contract/test)
- Zero semantic change to any MUST/NEVER/ALWAYS rule

**Safeguards:** Light Lane atoms must still read raw source (Stage 2), produce an expansion (Stage 3, abbreviated), and be briefed to the owner (Stage 7). Any doubt about eligibility → Full Lane. Misclassification into Light Lane is a session failure if discovered later.

### 4.15 Owner Briefing Optimization (PROC-001)

At 600 atoms, per-atom owner briefing causes checkbox fatigue. After the first 50 CLOSED atoms establish trust:

**Phase A (atoms 1-50): Full per-atom briefing.** Every atom gets an individual brief as described in Stage 7.

**Phase B (atoms 51+): Batched DELIVERY, per-atom LEDGER artifact.** The ledger ALWAYS contains a per-atom brief artifact with the 4 required elements (what, changed, rejected, risks) — this is non-negotiable regardless of atom count. Owner-facing DELIVERY may be batched:
- A **batch summary** after every 5 atoms (1-2 sentences per atom, highlighting only what changed)
- **Full individual delivery** only for: atoms where coworkers disagreed, atoms touching the owner's core concerns (self-containment, loose knowledge, attribution), atoms where the expansion revealed tensions in the owner's own raw text, atoms where CC exercised the Scholarly Integrity override (§4.13), and any atom the owner specifically requests full delivery for.

The owner can request full per-atom delivery for any batch at any time. The distinction is: ledger artifact = always per-atom; owner delivery = batchable after trust established. This resolves the v3.2 contradiction between §4.7 (mandatory per-atom) and §4.15 (exception-based).

**Owner Engagement Heartbeat (v4.1):** Every 10 CLOSED atoms post-50, the owner MUST review 2 full per-atom briefs chosen by CC (1 'lowest confidence / most disputed' atom, 1 'highest systemic impact' — e.g., most prompt words altered, most cross-science boundaries affected, or required Scholarly Integrity Arbitration). If owner does not respond to the heartbeat within 7 calendar days, session type MUST switch to `validation-only` and produce a 10-atom retrospective before any more closures. This prevents silent disengagement from neutralizing the owner objection safety valve (§4.10).

**Batch composition rules (v4.2 DR10, Gemini-amended):**
1. **Theme-based cross-science batches (DEFAULT for hardening):** Group atoms by structural theme (e.g., "boundary rules", "indivisibility checks") across diverse structural families. This forces cross-science validation and prevents overfitting prompt rules to one family (Gemini v4.2: "discipline-homogeneous batching risks overfitting to [ARG] structures").
2. **Discipline-focused batches (OPTIONAL):** When 5+ atoms are from the same discipline, CC MAY group them for owner clarity. But at least 1 in 3 batches MUST be cross-science.
3. **Graduated complexity:** Within batches, present lower-risk decisions first, higher-risk last (tadarruj principle).
4. **Tier 1 reversion:** Any atom involving an ALWAYS INDIVISIBLE unit reverts to Phase A per-atom briefing regardless of sequence position. The tradition's own approach — ʿarḍ of the Quran required word-level verification — supports risk-tiered verification granularity.
5. **Rubber-stamping detection:** If owner approval rate exceeds 95% across 3+ consecutive batches, flag for possible rubber-stamping. Trigger a competence-check prompt with one deliberately challenging atom.
6. **Applied Visual ʿArḍ (v4.3 DR11):** Every batched summary MUST include at least 1 concrete before/after Arabic text example showing the rule's effect on a real excerpt. Instead of abstract descriptions ("Refined boundary rules for fiqh extraction"), show: "If we apply this rule, your study card from *al-Hidāyah* will look like [example A]. Without this rule, it would look like [example B]. Which serves your study better?" This engages the owner with scholarly outcomes, not engineering process — the modern equivalent of taḥqīq al-fahm (verification of comprehension).

### 4.16 DR Budget Per Session (PROC-003)

At ~600 atoms requiring ~200 DR relays, owner relay fatigue is unsustainable.

**Rule:** Maximum 5 DR relay dispatches per 25-atom session. Reserve DR for:
- Prompt-affecting atoms in the Full Lane
- Atoms where Codex and Gemini DISAGREE
- Atoms touching khilaf/tarjih, attribution, or excerpt definition
- Phase gates

**Exempt from DR:** Light Lane atoms, verification-only atoms, SPEC-only doctrinal additions with Codex+Gemini agreement.

**DR relay classes (v4.0):**
| Class | Scope | Budget Count | Format |
|-------|-------|-------------|--------|
| `atom-review` | Exactly 1 MAQ-ID per relay | Each counts as 1 against budget | Per-atom expansion + coworker findings |
| `research` | Topic-based, may span multiple atoms | Counts as 1 regardless of atoms touched | Research question + context files |
| `phase-gate` | Covers entire phase transition | Counts as 1 | Phase summary + evidence + gate criteria |
| `atom-review-sampled` | 1 atom deep review + 3 atoms red-flag scan (max 10 min each) | Counts as 1 | Deep review: full expansion + questions. Scan: expansion summary + "any red flags?" |

Use `atom-review-sampled` when DR budget is tight and >4 atoms need review. Output MUST clearly separate 'deep review findings' from 'scan findings.' Scan findings marked with [SCAN] prefix.

Combined "review these 3 atoms together" relays are FORBIDDEN for `atom-review` class — they produce shallow per-atom feedback (Session 2 finding). Research and phase-gate relays may legitimately span multiple atoms.

### 4.17 Redirected Findings (Valid but Not Protocol Scope)

The following Gemini DR findings are valid scholarly insights but belong in engine SPEC or downstream engines, not in the hardening protocol:

| Finding | Redirect Target | Action |
|---|---|---|
| PED-001 (Organic Knowledge Unit) | SPEC §5/§6 — Phase 2 grouping doctrine | Create a SPEC amendment ticket: genre-aware teaching unit boundaries (mas'alah, tarjamah, bayt, etc.) |
| PED-003 (Knowledge dependency mapping) | Taxonomy + Synthesis engines | Document as a cross-engine design requirement for the knowledge graph layer |
| PED-004 (Study Path Reconstruction Test) | Evaluation layer / campaign review tools | Integrate into `tools/evaluate_excerpts.py` as a multi-text coherence check |

### 4.18 Regression Gate (v5.0 DR16)

**Trigger:** After ANY prompt or SPEC change that affects excerpting behavior.

**Process:**
1. Run `scripts/run_regression_suite.py --profile production_validation_profile.json`
2. The script re-executes all previously validated atom checks (from `validation/` directory)
3. Input: prompt.txt hash, SPEC.md hash, per-atom validation artifacts
4. Output: `regression_runs/<run_id>/summary.json` + junit-style report
5. Exit 0 = pass (no regressions). Exit 1 = regression detected.

**Rules:**
- Q-CLOSED CANNOT be granted for any atom if the regression suite has not passed after the most recent prompt/SPEC change
- Merge to branch is BLOCKED if regression suite fails (HR-21)
- Run after every prompt refactor (§4.11) and after every 5th prompt-affecting atom (§4.12)
- Regression suite is mandatory in `validation-only` sessions and before closing any IMPLEMENTED atom

### 4.19 Cross-Batch Doctrine Coherence Gate (v5.0 DR16)

**Trigger:** Before G-batch hardening begins AND before any SC-batch atom enters Stage 5 (SYNTHESIZED).

**Process:**
1. Run `scripts/prompt_coherence_lint.py` on the current prompt + SPEC doctrine
2. The script performs static analysis for:
   - Duplicate clause detection (string + semantic similarity)
   - Conflicting modal/quantifier detection ("always" vs "never" on same concept)
   - Unreachable conditions (rule A makes rule B impossible)
   - Token budget accounting by section
3. If two Q-CLOSED atoms assert conflicting constraints on the same concept, the gate FAILS
4. Resolution: CC must explicitly mark one as overriding with "OVERRIDE of MAQ-XXX" or reconcile the conflict

**Cross-batch scope:** Later batch generalizations (G-series) can override previously finalized foundation atoms (F-series) ONLY with explicit override marking. Without it, the coherence gate catches the contradiction. This prevents silent doctrine drift across the 15-30 session campaign.

---

## §5 — Coworker Consensus Protocol

### 5.1 Coverage Tiers

| Change Type | Minimum Coverage | Target Coverage |
|-------------|-----------------|-----------------|
| **Prompt-affecting** (adds/changes words in GROUP or CLASSIFY prompt) | CC + Codex + Gemini | + 1 DR |
| **SPEC-structural** (adds/modifies FPs, changes §4-7 behavioral rules) | CC + Codex + Gemini | + 2 DR |
| **Contract-affecting** (modifies contracts.py types, enums, validators) | CC + Codex | + Gemini |
| **SPEC-doctrinal** (adds principles without code/prompt change) | CC + Gemini | + 1 DR |
| **Phase gates** (transition from one phase to next) | All 6 sources | All 6 sources |

**Absolute floor:** No atom finalized with fewer than 2 independent confirmations (CC + at least 1 external).

### 5.2 Voting System

Each **external** coworker (Codex, Gemini, DR) votes per atom. **CC does NOT vote** — CC is the decision-maker that synthesizes votes, not a voter. The coverage tier counts (e.g., "CC + Codex + Gemini") mean CC orchestrated the process AND Codex + Gemini each cast a formal vote. Consensus is determined by external coworker votes only.

| Vote | Meaning | Consensus Effect |
|------|---------|-----------------|
| **ACCEPT** | Correct as proposed | +1 |
| **MODIFY** | Right intent, needs specific changes (coworker provides exact change) | +1 if CC accepts modification. If CC rejects: atom enters **DISPUTED** state requiring escalation (see §5.4) — CC cannot unilaterally dismiss a MODIFY. |
| **ITERATE** | Needs significant rework | -1 (atom stays PRELIMINARY) |
| **REJECT** | Fundamentally wrong or dangerous | BLOCK (atom cannot proceed regardless of other votes) |

**Clarification on tie votes:** With 2 external coworkers (Codex + Gemini) and a 1-1 split (one ACCEPT, one ITERATE): this is a **tie** → stays PRELIMINARY → escalate to DR as tiebreaker per §5.4 Step 5. With 3 external coworkers and a 2-1 split: **majority** FINALIZED with documented dissent.

### 5.3 Consensus Thresholds

| Scenario | Result |
|----------|--------|
| All ACCEPT/MODIFY (accepted) and 0 REJECT | **FINALIZED** |
| Majority ACCEPT/MODIFY, minority ITERATE | **FINALIZED** with documented dissent |
| Split (equal ACCEPT and ITERATE) | **PRELIMINARY** — escalate per §5.4 |
| Any single REJECT | **BLOCKED** — must address the finding |
| Fewer than minimum coworkers reported | **PRELIMINARY** regardless of votes |

### 5.4 Disagreement Resolution Hierarchy

When coworkers disagree, resolve in this strict sequence:

1. **SPEC as tiebreaker.** If an existing FP governs the case, apply it. The aligned position wins.
2. **FP-13 precedence stack.** Attribution safety > dialogue preservation > grammatical integrity > self-containment > granularity. **Attribution safety specifically includes:** guarding against copyist (ناسخ, كتبه العبد الفقير) being confused with author (مؤلف, فرغ من تأليفه), editorial apparatus (محقق, حاشية, في الأصل) leaking into author-attributed content, and `layer_type: editorial` manuscript marginalia being misattributed.
3. **Evidence weight.** Concrete Arabic example beats abstract principle. Cross-science generalization beats single-science claim. Empirical data beats theory.
4. **CC decides with documented reasoning.** The losing position is preserved as a formal **variant reading** (v5.0 DR17): with provenance sigla (خ notation) identifying which coworker holds each position. The winning position enters the body text (the aṣl reading); losing positions are preserved in the ledger as **authority-ordered variants** — not flat-egalitarian alternatives, but hierarchically ordered with the aṣl (closest to owner's original intent) as primary and others as marginal readings. This mirrors classical taḥqīq practice where the editor chooses the primary reading but preserves all variants with identified exemplar provenance.
5. **Escalation to additional coworker.** For SPEC-structural atoms, dispatch a DR coworker as BLINDED tiebreaker (does not see other positions before forming assessment).

   **BLINDED means (v4.1):** DR prompt MUST include ONLY the expansion document and raw source excerpts. It MUST NOT include Codex/Gemini verdicts, summaries, or any indication of their positions. Use the BLINDED TIEBREAK template (§4.4), NOT the standard DR templates that include "Codex found / Gemini found."

6. **Owner involvement (LAST RESORT).** Only for study-experience questions. Concrete with examples, never abstract.

### 5.5 Async DR Relay Protocol

1. CC drafts the DR prompt following templates in §4.4.
1A. **CC runs the draft through `/prompt-architect` (HR-23, MANDATORY).** The optimized version replaces the draft. This applies to ALL targets: DR relay, Codex CLI, Gemini CLI, CC subagents.
2. CC presents the OPTIMIZED prompt to owner: "Please paste this into [ChatGPT DR / Claude DR / Gemini DR]."
3. CC records dispatch in `dispatch_log.jsonl` with `status: dispatched`.
4. CC does NOT block. Continues with CLI coworker work.
5. When owner returns DR response, CC records with `status: completed`.

**Timeouts:**
| Elapsed | Action |
|---------|--------|
| 0-24h | Normal. CC works on CLI coworker tasks. |
| 24-48h | Gentle check to owner: "DR relay is waiting when you have a moment." |
| 48h | Proceed with N-1. Document gap. Atom: PRELIMINARY (N-1). |

**DR access reminders:**
- ChatGPT DR: HAS repo access. Give FILE PATHS.
- Claude DR: HAS repo access. Give FILE PATHS.
- Gemini DR: CANNOT access repo. Prepare FILE UPLOADS.

### 5.6 Coworker Review Scope

| Coworker | Reviews | Does NOT Review |
|----------|---------|-----------------|
| **Codex CLI** | Contract impact, test regression, cross-prompt consistency, implementation cost, implementation adversarial | Arabic text quality, scholarly accuracy, pedagogy |
| **Gemini CLI** | Cross-science validity, counterexamples, convention compliance, cross-engine blast radius, scholarly adversarial | Code structure, test coverage, implementation cost |
| **ChatGPT DR** | Gap detection, silent corruption paths, architectural analysis, error patterns | (Overlap with Claude DR on adversarial) |
| **Claude DR** | Scholarly reasoning depth, boundary quality, decontextualization risk | (Overlap with ChatGPT DR on adversarial) |
| **Gemini DR** | Islamic pedagogy, study-unit validity, genre-specific "natural atom" validation | (Requires file uploads, no direct repo access) |

### 5.7 Escalation Triggers (Require ALL 6 Sources)

- Phase gates (always)
- Modifying the excerpt definition
- Changing khilaf/tarjih handling (owner's most sensitive domain — triggered OPS-DEC-006)
- Any coworker REJECT vote needing resolution
- Any regression in empirical validation
- Any silent corruption path (T-1 through T-7) found by any coworker
- Owner explicitly flags something as "wrong" or "confusing"

### 5.8 Role Separation Formalization (v5.0 DR17)

The protocol's coworker roles map to the 5 classical roles of the Islamic verification assembly (majlis al-muʿāraḍah):

| Classical Role | Protocol Role | Responsibility | Cannot Do |
|---|---|---|---|
| **Musammiʿ** (presiding authority) | CC orchestrator | Final decision-making, active real-time correction during synthesis, granting ijāzah (certification). NOT passive — CC actively corrects during the process. | Vote (§5.2 — CC decides, doesn't vote) |
| **Qāriʾ** (reader) | Extraction subagent | Read source files, extract MCUs, produce per-file inventories | Judge correctness, approve variants |
| **Mustamiʿūn** (witnesses with veto) | Coworker reviewers (Codex, Gemini, DR) | Challenge expansions, cast votes, exercise veto via REJECT | Make final decisions; that's CC's role |
| **Muqābil** (collator) | Verification agent (in batch-verification sessions) | Compare extraction against raw source (muqābalah bi-l-aṣl), mark gaps | Approve final text or close atoms |
| **Kātib** (certificate writer) | Script artifacts + ledger entries | Record session details, produce certificates, maintain audit trail | Interpret meaning or judge variants |

**Key constraint (HR-22):** The extraction agent (Qāriʾ) CANNOT be the verification agent (Muqābil). The session that performed extraction CANNOT perform verification. This prevents the "self-audit" conflict of interest where the same mental model that produced the work reviews it.

### 5.9 Scholarly Grounding: Authority Hierarchy (v5.0 DR17)

The protocol's consensus mechanism (§5.1-5.4) is validated by the classical Islamic N-version verification tradition (DR17 §4). The key classical principle: **a single authoritative copy outweighs multiple copies of uncertain provenance**. In KR terms:

- The owner's raw .txt files (= nuskhat al-muʾallif, the author's autograph) have SUPREME authority
- Supervised extractions (= copies made under author's supervision) = `owner_explicit` authority atoms
- Model-only expansions (= copies of uncertain provenance) = `model_only` atoms requiring owner confirmation

This authority hierarchy is already implemented: Rule 6 ("Raw owner text is ground truth"), §4.10 (owner objection overrides all consensus), and the authority classification system (§4.2, Appendix A). Coworker votes within §5 are scope-weighted (§5.6) rather than provenance-weighted because coworkers have complementary, non-overlapping expertise — each is authoritative in their domain.

---

## §6 — Context Window Management

### 6.1 Budget Zones

```
Zone 0: SYSTEM       [0% - 3%]      ~30K tokens    Fixed (rules, skills, MCP)
Zone 1: BOOTSTRAP    [3% - 15%]     ~150K tokens   One-time session init
Zone 2: WORKING      [15% - 75%]   ~600K tokens    Active atom processing
Zone 3: BUFFER       [75% - 85%]   ~100K tokens    Handoff zone (MANDATORY handoff begins)
Zone 4: EMERGENCY    [85% - 96%]   ~110K tokens    Compact + minimal recovery
Zone 5: FORBIDDEN    [96% - 100%]   ~40K tokens    NEVER ENTER (hallucination zone)
```

**Hard rules:**
- Zone 3 entry → stop new atoms, begin Session Handoff (§7)
- Zone 4 without handoff started → immediate `/smart-compact`, then finish current atom only, then handoff
- Zone 5 → refuse all work, write emergency handoff only

### 6.2 Dispatch-vs-Local Decision Matrix

**Verbatim Span Extraction Rule (DA-005/DA-026):** When dispatching subagents to summarize owner files or Arabic scholarly texts, the subagent prompt MUST include: *"When summarizing, you MUST extract and quote the exact, verbatim Arabic text span (with surrounding context) that contains the ruling, condition, or conflict. Never translate or paraphrase the core Arabic qualifier. Preserve: particles of restriction (إنما, لو, لولا), qualifiers (السائمة, تنزيهاً, تحريماً), epistemic weight indicators (passive قيل vs active قال), and exception chains (إلا, سوى, غير)."* This prevents summarization from collapsing critical scholarly distinctions.

**ALWAYS DISPATCH (to subagent or coworker — never read locally):**

| Task | Target | Savings |
|------|--------|---------|
| Reading collection source_artifacts/*.txt | CC Subagent → 2-4KB summary | Saves 20-60KB per file |
| Reading structured JSONL/YAML/MD files | CC Subagent → 2-4KB summary | Saves 10-30KB per file |
| Codex CLI challenge | codex exec (external process) | Zero CC context for coworker reasoning |
| Gemini CLI review | gemini -p (external process) | Zero CC context for coworker reasoning |
| SPEC section reading (full section) | CC Subagent → 2-3KB summary | Saves 10-30KB per section |
| DR report summarization | CC Subagent (if report >10KB) | Saves 10-50KB per report |
| Cross-atom regression check | CC Subagent reads ledger | Saves 25KB |

**ALWAYS LOCAL (CC's own context):**

| Task | Rationale |
|------|-----------|
| Synthesis decision-making (Stage 5) | Core intellectual work requiring judgment |
| Implementation edits | CC must see code to edit it (but edits are small, <5KB) |
| Ledger updates | Small writes, requires decision context |
| Owner briefing composition | Requires CC judgment |
| Test execution + result interpretation | Tool calls with structured output |
| Commit message composition | Requires session context |

**CONDITIONAL (dispatch if >60% context):**
- Blast-radius checks → dispatch subagent
- Test execution → run via Bash with -q flag, read only failures

### 6.3 Per-Atom Context Tracking

After every 3rd atom, CC MUST state:
> "Context estimate: ~X% used. Remaining capacity: ~Y atoms. Handoff planned after atom Z."

**Rough formula:**
```
estimated_tokens ≈ 150K + (full_atoms × 50K) + (light_atoms × 15K) + (response_turns × 10K)
```

The practical rule: **hand off after ~5-8 atoms (full-atom session) or when entering Zone 3.** Session 2's failure at 96% happened around atom 20 with the LESS efficient non-dispatch approach; v4.0 budgets are calibrated to prevent that.

### 6.4 Compaction Recovery Protocol

When `/smart-compact` runs, IMMEDIATELY re-read (in this order):

1. Session state from memory/handoff (batch progress, FP changes, decisions, next action)
2. `engines/excerpting/CLAUDE.md` (~8KB)
3. SPEC §1.1b only (FPs, ~6KB) — dispatch subagent if needed
4. Current prompt from `phase2_group.py` lines 43-209 (~7KB)
5. Ledger: ONLY last 5 entries (~5KB)
6. Current batch atoms from MERGED_ATOM_QUEUE (~3-5KB)

**Total recovery cost: ~35KB (~10K tokens).** Compare with full bootstrap at ~150K.

**What can be re-derived (do NOT re-read):**
- Collection file contents (dispatch subagent again if needed)
- Coworker reports from completed atoms (summarized in ledger)
- NEXT.md (doesn't change during session)
- ATOM_PROTOCOL.md (behavioral rules internalized)

### 6.5 Checkpoint States for Emergency Handoff (v4.0)

When context emergency forces mid-atom handoff, use these checkpoint states instead of fake terminal states. PRELIMINARY is a coworker-coverage state, NOT an emergency-exit state — do not misuse it.

| Checkpoint State | Meaning | Resume Point |
|------------------|---------|-------------|
| `PAUSED-EXPANDED` | Expansion complete, not yet challenged | Resume at Stage 4 (dispatch coworkers) |
| `PAUSED-CHALLENGED` | Some coworker reports received, waiting for rest | Resume at Stage 4 (wait) or Stage 5 (if minimum met) |
| `PAUSED-SYNTHESIS` | Synthesis in progress, context emergency | Resume at Stage 5 (complete synthesis) |
| `IMPLEMENTED-UNVERIFIED` | Code written, tests not yet run | Resume at Stage 6 (run validation suite) |
| `IMPLEMENTED-AWAITING-BRIEF` | Tests pass, owner not yet briefed | Resume at Stage 7 (compose and deliver brief) |

**Rules:**
- NEVER attempt Stage 7 (owner brief) during a context emergency — brief quality suffers under context pressure.
- Checkpoint states are NOT terminal. They MUST be resolved in the next session.
- Handoff document MUST list each checkpointed atom with its state and exact resume instructions.

---

## §7 — Session Handoff Protocol

### 7.1 Handoff Triggers

| Trigger | Action |
|---------|--------|
| **Planned:** Last atom that fits in Zone 2 budget | Begin handoff |
| **Triggered:** Entering Zone 3 (75% context) | Stop new atoms, begin handoff |
| **Emergency:** Zone 4 (85%) without handoff started | Compact → finish current atom → handoff |

### 7.2 Handoff Document Template

Create at `reference/handoffs/excerpting_foundations_sessionN+1_kickoff_YYYY-MM-DD.md`:

```markdown
# Session [N+1] Kickoff — Excerpting Foundations Hardening

## STOP — Read in this exact order:
1. `engines/excerpting/reference/HARDENING_SESSION_PROTOCOL.md` (§0 + §0.1 Autonomous Doctrine)
2. This handoff document
3. `engines/excerpting/CLAUDE.md`
4. `engines/excerpting/reference/FOUNDATIONS_HARDENING_LEDGER.md` (recent entries only)
5. Continue from the NEXT SESSION DIRECTIVE below

## NEXT SESSION DIRECTIVE (v5.0 — autonomous)
- **Session type:** [determined by §1.6 gate-precedence — DO NOT ask owner to confirm]
- **First action:** [exact action to take immediately after reading]
- **Decision framework:** [which SPEC/FP rules govern decisions this session]
- **Owner involvement needed:** [NONE / DR relay for X / preference question about Y]
- **Estimated scope:** [N atoms / N files / N bundles]

BEGIN IMMEDIATELY after reading. Do not wait for owner confirmation.

## Session [N] Accomplishments
- **Atoms processed:** [N] ([list MAQ-IDs])
- **Atoms CLOSED:** [N] (fully closed, Q-CLOSED passed)
- **Atoms PRELIMINARY:** [N] (awaiting coworker confirmation — list which coworker)
- **FPs added/modified:** [list FP numbers + 1-line each]
- **Prompt changes:** GROUP [current]/1500 words, CLASSIFY [current]/~1000 words. Prompt-affecting atoms since last coherence review: [N]. Last coherence review: Session [X], date [Y]. (§4.12 triggers at every 5th prompt-affecting atom.)
- **Test count:** [N] pass, [N] xfail, [N] skip
- **Coworker dispatch summary:** Codex [N] dispatches, Gemini [N], DR [N] (list pending)

## What Session [N] Got RIGHT (keep these patterns)
1. [pattern]
2. [pattern]
3. [pattern]

## What Session [N] Got WRONG (avoid these)
1. [anti-pattern]
2. [anti-pattern]
3. [anti-pattern]

## Context Management Report
- Peak context estimate: ~[N]%
- Compactions: [N]
- Dispatch efficiency: [N]% of reads delegated
- Atoms per session achieved: [N] (target was [M])

## What Remains
- **Next atom to process:** MAQ-[ID] at Stage [N] — [description]
- **Unstarted atoms:** [N] ([list batch/series])
- **PRELIMINARY atoms:** [list MAQ-IDs with missing coworker]
- **Pending DR responses:** [list, with dispatch date]
- **Unresolved risks:** [list]

## Budget Update
- EUR spent this session: [N]
- EUR total: [N] / 100
- Budget remaining: [N]

## Doctrine Compliance Self-Audit (v5.0 — MANDATORY)
- **Autonomous violations:** [count of times CC asked owner for technical guidance this session. Target: 0]
- **Prompt-architect skips:** [count of dispatches sent without /prompt-architect. Target: 0]
- **Total dispatches:** [count]. Each logged in dispatch_log.jsonl with `prompt_architect_used` field.

## Process Improvements Discovered (for protocol §8)
1. [improvement]
2. [improvement]
3. [improvement]
```

### 7.3 State Files to Update Before Session End

- [ ] Handoff document written at `reference/handoffs/`
- [ ] `.kr/HANDOFF.md` updated with resume point
- [ ] `FOUNDATIONS_HARDENING_LEDGER.md` — all atom dispositions current
- [ ] `MERGED_ATOM_QUEUE.md` — all atom statuses updated
- [ ] All changes committed with descriptive messages

---

## §8 — Self-Improvement Mechanism

### 8.1 Per-Session Retrospective

Every session records (in the handoff document, §7.2):
- 3 things that WORKED (keep these patterns)
- 3 things that DIDN'T WORK (avoid these anti-patterns)
- 3 proposed PROTOCOL IMPROVEMENTS

### 8.2 Protocol Amendment Process

After every 3 sessions, CC + Codex perform a protocol review:
1. Read all retrospectives from the last 3 sessions
2. Identify recurring patterns (good and bad)
3. Propose specific protocol amendments
4. Gemini reviews scholarly-impact amendments
5. Amendments require: CC + Codex agreement minimum; Gemini for scholarly aspects

**Amendment format:** Added to the version history in §0, with the change description, reasoning, and session that discovered the need.

### 8.3 Living Document Principle

This protocol is LIVING DOCTRINE, not frozen law. If a session discovers that a rule is counterproductive, it:
1. Documents the issue in the retrospective
2. Proposes the amendment with evidence
3. Gets coworker confirmation
4. Updates this document with version bump

### 8.4 Doctrine Backfill Protocol (v4.1)

Any amendment that changes (a) Cross-Science Variation categories, (b) Atomic Integrity Risk units, or (c) a prompt rule MUST trigger a backfill audit:

1. Identify all previously CLOSED atoms impacted by the changed rule (check ledger Cross-Science Variation and Atomic Integrity Risk sections).
2. Sample impacted atoms using dimension-based selection: at least 1 per Structural Family ([ARG], [NAR], [ENT], [RUL], [ART], [COM]) affected by the change, minimum 5 total (prioritize: prompt-affecting > SPEC-structural > SPEC-doctrinal). A flat sample of 5 from the same family is INSUFFICIENT — drift in unsampled families goes undetected (Gemini v4.1 finding).
3. Re-evaluate each sampled atom against the new rule version.
4. If ≥1 sampled atom fails the new rule: escalate to a targeted reopening campaign for all impacted atoms.
5. If all 5 pass: record "backfill audit passed" in the amendment's version history entry.

This prevents "silent drift accumulation" where newer doctrine invalidates older closures without detection.

### 8.5 Calibration File — Nuskha Miʿyāriyyah (v5.0 DR15/DR17)

**Purpose:** Detect standards degradation across a 15-30 session campaign. The classical tradition tested a narrator's ḍabṭ (precision/retention) periodically; this is the digital equivalent.

**Designation:** Designate one moderately complex file (e.g., an F4 segment with mixed directives, nonnegotiables, and research analysis) as the **Calibration File**. Record its path and SHA-256 in the protocol's configuration section.

**Calibration check (every 5th batch-verification session):**
1. The incoming verification agent independently extracts MCUs from the Calibration File WITHOUT access to the baseline extraction
2. Compare: does the agent miss ALL-CAPS directives? Soften nuance? Extract unstructured paragraphs incorrectly?
3. If the agent's extraction differs from baseline in >3 MCUs OR misses any CRITICAL-severity MCU: flag for **ḍabṭ deficiency** (Sūʾ al-Ḥifẓ — "poor retention")
4. On ḍabṭ flag: HALT verification work. Recalibrate system prompts/agent configuration. Re-test on Calibration File. Resume only after <5% error rate achieved.

**Linkage to Laḥn Framework (§3A.6):** The Calibration File check is the operational mechanism for detecting habitual tolerable laḥn. If an agent consistently produces tolerable errors, the calibration check catches the pattern before it accumulates into systemic drift.

---

## §9 — Quick Reference Card

**Read this in 30 seconds at any point during a session for orientation.**

### Atom Lifecycle

```
RAW → SOURCED → EXPANDED → CHALLENGED → SYNTHESIZED → IMPLEMENTED → CLOSED
       read raw    scope+      coworkers     3-column      code+test    brief owner
       + quote    exceptions   vote          decide                    + ledger
```

### Per-Stage Cheat Sheet

| Stage | Who | Gate | Duration |
|-------|-----|------|----------|
| 1 RAW | CC selects | Atom chosen by priority | 0 min |
| 2 SOURCED | CC (dispatch for >10KB) | Raw quoted, authority set, conflicts checked | 10-15 min |
| 3 EXPANDED | CC | Scope, 2 exceptions, examples, hypothesis, blast-radius | 15-20 min |
| 4 CHALLENGED | Codex + Gemini + DR | 2/3 reports received, structured | Variable |
| 5 SYNTHESIZED | CC decides | 3-column table, disagreements resolved, decision specific | 10-15 min |
| 6 IMPLEMENTED | CC codes | Tests green, pyright clean, sync passes | 5-30 min |
| 7 CLOSED | CC briefs owner | Q-CLOSED: all 12 criteria TRUE | 5-10 min |

### Dispatch Decision Tree

```
Is the file >10KB?  ──YES──→  Dispatch subagent, read summary
        │
        NO
        │
Is it a judgment call?  ──YES──→  Do locally (synthesis, implementation)
        │
        NO
        │
Can a coworker do it better?  ──YES──→  Dispatch to Codex/Gemini/DR
        │
        NO ──→ Do locally
```

### Context Checkpoints

```
After atom 2:    State context estimate. Verify session type still correct.
After atom 4:    State estimate. If >50%, increase dispatch ratio.
After atom 6:    State estimate. If >60%, /smart-compact.
At 70%:          Plan handoff. Complete current atom only.
At 75%:          STOP new atoms. Begin handoff (Zone 3).
At 85%:          EMERGENCY. Compact → finish current → handoff.
At 96%:          FORBIDDEN. Emergency handoff only.
```

### Coworker Minimums

```
Prompt change  = CC + Codex + Gemini (+ DR if disagreement)
SPEC change    = CC + Codex + Gemini (+ DR for structural)
Contract       = CC + Codex (+ Gemini preferred)
SPEC-doctrine  = CC + Gemini (+ DR for scholarly)
Phase gate     = ALL 6 sources, NO exceptions
Session type  = Declare at start per §1.5. Never combine intake + full-atom.
WIP cap       = Max 1 Full Lane in Stages 3-5. Max 3 open atoms total.
```

### Anti-Patterns (Session Failures)

```
NEVER bulk atoms (analyze individually, implement in small groups max 3)
NEVER read raw files >10KB locally (dispatch subagent — use Verbatim Span Extraction)
NEVER skip per-atom LEDGER brief artifact (owner DELIVERY may batch after 50 atoms per §4.15)
NEVER say "done" without Q-CLOSED (11 criteria ALL true)
NEVER finalize with <2 coworker reports
NEVER skip raw owner .txt source
NEVER modify prompt without SPEC sync check
NEVER push past 75% context without starting handoff
NEVER count DEFERRED-RECORDED as "atoms closed" (DA-002)
NEVER dismiss a coworker MODIFY without escalation (DA-009 → DISPUTED)
NEVER let >5 PRELIMINARY atoms accumulate without clearing (DA-008)
NEVER skip Prompt Coherence Review after 5 prompt-affecting atoms (DA-029)
NEVER implement owner directive that would corrupt text structure (DA-018 → block + surface)
NEVER begin atom processing before Batch Completion Gate passes (v5.0 §3B, HR-13)
NEVER strip ALL-CAPS / emphasis — they are semantic content (v5.0 §3A.3, HR-16)
NEVER self-audit: extractor ≠ verifier (v5.0 §5.8, HR-17/HR-22)
NEVER merge prompt changes without regression suite passing (v5.0 §4.18, HR-21)
NEVER expand without fidelity indicator: exact / paraphrased / interpreted (v5.0 §4.3)
NEVER dispatch a prompt without /prompt-architect optimization first (v5.0 §3B.2, HR-23)
```

---

## Appendix A: Collection File Authority Reference

| Authority Level | Meaning | Protocol Handling |
|----------------|---------|-------------------|
| `owner_explicit` | Owner directly stated this | Treat as high-confidence input to expansion |
| `owner_consistent_inference` | Consistent with owner's known standards | Treat as medium-confidence; verify against raw text |
| `model_only` | ChatGPT engineering expansion only | Owner confirmation REQUIRED before Stage 5 synthesis |

## Appendix B: Session 1 Failure → Protocol Fix Mapping

| Session 1 Failure | Protocol Section | Specific Fix |
|-------------------|-----------------|-------------|
| Atoms bulked | §4 (lifecycle), §1.4 rule 11 | Per-atom lifecycle; max group of 3 for implementation only |
| Owner not briefed per-atom | §4.7 (Stage 7), §1.4 rule 12 | Mandatory per-atom owner brief at closure |
| Context hit 96% | §6 (context management) | Dispatch-first strategy; hard handoff at 75% |
| Only 15/139 files read | §3 (bundle intake), §4.2 (SOURCED) | Subagent-based complete inventory; raw source mandatory |
| Inconsistent coworker coverage | §5 (consensus protocol) | Per-atom minimum 2 coworkers; formal voting |
| Premature "done" | §4.8 (Q-CLOSED) | 11-criterion gate; mechanically checkable |
| No atom expansion | §4.3 (EXPANDED stage) | Mandatory expansion template with 7 sections |
| DR not executed | §5.5 (async relay) | Timeout protocol; parallel work during wait |
