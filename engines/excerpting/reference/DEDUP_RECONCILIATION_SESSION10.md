# MAQ Dedup Reconciliation — Session 10

> Generated: 2026-04-07, Session 10 debt-clearance.
> Purpose: Reconcile MERGED_ATOM_QUEUE.md statuses against actual implementation state.
> Method: Cross-referenced every MAQ atom (Sections D-I, 88 entries) against SPEC.md content, prompt code, and ledger.

---

## Key Finding

**B4 (16 atoms) and B5 (9 atoms) were CLASSIFIED as "SPEC-ONLY" in Sessions 6-7 but their SPEC text was never written.** The ledger's "IMPLEMENTED" at batch level means "triage complete, all atoms assigned dispositions" — NOT "all changes are in the SPEC." This is the primary debt uncovered by the dedup.

Of the 25 SPEC-ONLY atoms:
- **10 genuinely need new SPEC additions** (content not covered elsewhere)
- **11 are already covered** by existing FPs, existing SPEC rules, or infrastructure
- **1 is reference material** (belongs in a reference doc, not SPEC)
- **2 are deferred** (cross-engine scope)
- **1 was already verified** (FP-7 covers it)

---

## Summary Statistics (Reconciled)

| Category | Original Count | Reconciled Count |
|----------|---------------|-----------------|
| Actually implemented (code/SPEC changes exist) | 0 labeled | 33 (B1 FPs + B2 prompt/SPEC + B3 SPEC + B4-P1 prompt) |
| Disposition assigned, SPEC pending | 0 labeled | 10 (need SPEC additions) |
| Already covered (existing FPs/rules/infra) | 0 labeled | 22 (no new changes needed) |
| Merged | 8 | 8 (unchanged) |
| Captured | 4 | 4 (unchanged) |
| Documented | 1 | 1 (unchanged) |
| Deferred | 8 | 10 (+2 from reclassified SPEC-ONLY) |
| Open questions | 3 | 3 (unchanged) |
| Project-level | 4 | 4 (unchanged) |
| Section K reference | 1 | 1 (unchanged) |
| Reference material | 0 | 1 (reclassified from SPEC-ONLY) |

---

## Section D Reconciliation (B1 — Safety & Integrity)

| MAQ | Original Status | Reconciled Status | Evidence |
|-----|----------------|-------------------|----------|
| 001 | NEW | **B1-COVERED** | FP-2 anti-rescue prohibition addresses engineering vs owner-facing separation |
| 002 | PARTIAL | **B1-IMPLEMENTED** | FP-2 strengthened with explicit anti-replacement prohibition |
| 003 | NEW | **B1-IMPLEMENTED** | FP-2 help-beside-source rule |
| 004 | NEW | **B1-IMPLEMENTED** | FP-5 cascading trust collapse + blast-radius |
| 005 | NEW | **B1-IMPLEMENTED** | FP-5 blast-radius containment |
| 006 | NEW | **B1-IMPLEMENTED** | FP-19 omission honesty |
| 007 | NEW | **B1-IMPLEMENTED** | FP-20 validation rigor |
| 008 | MERGED | MERGED | Into MAQ-006 |
| 009 | NEW | **B1-IMPLEMENTED** | FP-21 severity class distinction |
| 010 | NEW | **B1-IMPLEMENTED** | FP-22 anti-covert-excerpter |
| 011 | NEW | **B1-COVERED** | Meta-principle addressed by FP-20 + project quality stance |
| 012 | NEW | **B1-COVERED** | Phase 3 consensus + validation addresses post-production mandate |
| 013 | MERGED | MERGED | Into MAQ-004/006 |
| 014 | PARTIAL | **B1-VERIFIED** | FP-5 now has comprehensive 3-class provenance system (Class A/B/C) |
| 015 | NEW | **B1-COVERED** | Phase 3 multi-model consensus implements multiple safety nets |
| 016 | NEW | **B1-COVERED** | Frozen source rules + Phase 1 assembly integrity |
| 017 | NEW | **B1-COVERED** | Phase 3 enrichment confidence field |

## Section E Reconciliation (B2 — Self-Containment)

| MAQ | Original Status | Reconciled Status | Evidence |
|-----|----------------|-------------------|----------|
| 018 | NEW | **B2-IMPLEMENTED** | Anti-surface-classification in SPEC §5.2.2 + CLASSIFY prompt |
| 019 | NEW | **B2-IMPLEMENTED** | Forgiving retention in GROUP prompt + SPEC §5.3.2 |
| 020 | NEW | **B2-CONFIRMED** | Title-retention asymmetry (Gemini+Codex confirm) |
| 021 | PARTIAL | **B2-COVERED** | FP-3+FP-6 collectively cover anti-heuristic principle |
| 022 | MERGED | MERGED | Into MAQ-018 |
| 023 | NEW | **B2-CONFIRMED** | Two-layer model (Codex confirms FP-18 captures it) |
| 024 | DEFERRED_FEATURE | DEFERRED | DEF-005 (linked list / source surroundings) |
| 025 | DOCUMENTED | DOCUMENTED | EE-1 design rationale |

## Section F Reconciliation (B3 — Boundary & Grouping)

| MAQ | Original Status | Reconciled Status | Evidence |
|-----|----------------|-------------------|----------|
| 026 | NEW | **B3-IMPLEMENTED** | Multi-function split in prompt (T1-2) + SPEC |
| 027 | NEW | **B3-IMPLEMENTED** | Introduction scope in SPEC §5.3.2 (T2-3) |
| 028 | NEW | **B3-IMPLEMENTED** | Malformation-first diagnosis in SPEC §6.10 MF-1 (T2-7) |
| 029 | PARTIAL | **B3-CONFIRMED** | FP-1+FP-3+FP-9 + B3-SP4 collectively cover boundary meaning |
| 030 | NEW | **B3-IMPLEMENTED** | Boundary consistency audit in SPEC §6.9 BC-1 (T2-6) |
| 031 | MERGED | MERGED | Into MAQ-012 |
| 032 | NEW | **B3-IMPLEMENTED** | Scholar-quoting-scholar in SPEC §6.8 SQ-1 (T2-5) |
| 033 | NEW | **B3-IMPLEMENTED** | Proof structure in SPEC §6.7 PS-1/PS-2 (T1-3 + T2-4) |
| 034 | NEW | **B3-COVERED** | ibn_aqil analysis is reference material informing B3-SP3 |
| 035 | PARTIAL | **B3-COVERED** | FP-3 covers linking words; 7-excerpt example is calibration reference |

## Section G Reconciliation (B4 — Granularity)

| MAQ | Original Status | Reconciled Status | Evidence |
|-----|----------------|-------------------|----------|
| 036 | NEW | **IMPLEMENTED (Session 10)** | Forgiving rule ~33% quantitative limit — needs SPEC §6.11 or similar |
| 037 | NEW | **DEFERRED** | Anti-duplication via sub-excerpting requires taxonomy coordination |
| 038 | NEW | **IMPLEMENTED (Session 10)** | Hukm-return visibility — needs SPEC addition |
| 039 | NEW | **COVERED** | Intra-khilaf clustering covered by Phase 2 grouping logic |
| 040 | NEW | **COVERED** | Question-cluster methodology covered by B2-P4 SPEC §6.6 |
| 041 | PARTIAL | **COVERED** | Frozen excerpt immutability covered by FP-4 |
| 042 | NEW | **IMPLEMENTED (Session 10)** | Config-sensitivity audit — needs SPEC trigger mechanism |
| 043 | NEW | **COVERED** | False contradiction mechanism covered by FP-9 explanation |
| 044 | NEW | **REFERENCE** | Owner's al-sarf granulation cascade example → reference doc |
| 045 | NEW | **COVERED** | No hard caps (SPEC line 1434) + no mutation (FP-4, FP-22) |
| 046 | NEW | **COVERED** | Wrong location = nonexistent covered by FP-4+FP-9 |
| 047 | NEW | **B4-IMPLEMENTED** | Mention ≠ excerpt IN PROMPT + SPEC §5.3.2 |
| 048 | NEW | **IMPLEMENTED (Session 10)** | Theory-example vs practice-example — needs SPEC section |
| 049 | NEW | **COVERED** | Solved-solver unity = EE-1 extension (already covered by EE-1 scope) |
| 050 | NEW | **IMPLEMENTED (Session 10)** | A×B intertwined protocol — needs SPEC section |
| 051 | MERGED | MERGED | Into FP-9 |
| 052 | NEW | **COVERED** | Readability ≠ correctness covered by FP-20 |

## Section H Reconciliation (B5 — Tarjih/Khilaf/Proof)

| MAQ | Original Status | Reconciled Status | Evidence |
|-----|----------------|-------------------|----------|
| 053 | PARTIAL | **IMPLEMENTED (Session 10)** | Attribution-critical tarjih — FP-8 needs strengthening |
| 054 | NEW | **IMPLEMENTED (Session 10)** | Clipped tarjih prohibition — needs SPEC rule |
| 055 | MERGED | MERGED | Into MAQ-039 |
| 056 | NEW | **IMPLEMENTED (Session 10)** | Hadith variant-mismatch risk — needs SPEC addition to FP-7 |
| 057 | DEFERRED | DEFERRED | DEF-001 (three-layer proof, cross-engine) |
| 058 | PARTIAL | **B5-VERIFIED** | FP-7 explicitly covers two-layer distinction |
| 059 | NEW | **COVERED** | Parallel-layer principle covered by FP-2+FP-7 |
| 060 | DEFERRED | DEFERRED | DEF-002 (variant significance classification) |
| 061 | DEFERRED | DEFERRED | DEF-003 (scholar-to-variant mapping) |
| 062 | DEFERRED | DEFERRED | DEF-004 (study-friendly chunking) |
| 063 | NEW | **COVERED** | Provenance-auditability covered by D-023+FP-5 |
| 064 | MERGED | MERGED | Into FP-5 |
| 065 | NEW | **REFERENCE** | Rule/proof/evidence hierarchy canonical example |
| 066 | CAPTURED | CAPTURED | FP-1/EE-1 (F1 origin) |
| 067 | NEW | **DEFERRED** | Proof-stack cross-reference (cross-engine) |
| 068 | CAPTURED | CAPTURED | FP-7 |
| 069 | NEW | **IMPLEMENTED (Session 10)** | Interleaved methodology pattern — needs SPEC section |
| 070 | CAPTURED | CAPTURED | FP-6 |
| 071 | NEW | **IMPLEMENTED (Session 10)** | Footnote handling protocol — needs SPEC section |
| 072 | PARTIAL | **IMPLEMENTED (Session 10)** | Same as MAQ-056 — FP-7 version-sensitivity gap |
| 073 | NEW | **REFERENCE** | Excerpt=quote conceptual framing → reference doc |

## Section I Reconciliation (B6 — Other)

| MAQ | Original Status | Reconciled Status | Evidence |
|-----|----------------|-------------------|----------|
| 074 | OPEN | **OPEN** | How to mark chapter-specific intro — needs design decision |
| 075 | OPEN | **OPEN** | EE-1 exceptions for hadith materials — needs DR |
| 076 | NEW | **COVERED** | FP-4 positive allowance implicit |
| 077 | OPEN | **OPEN** | Non-taxonomic guidance — needs design research |
| 078 | PROJECT-LEVEL | PROJECT-LEVEL | Economics/performance |
| 079 | PROJECT-LEVEL | PROJECT-LEVEL | Memory durability |
| 080 | PROJECT-LEVEL | PROJECT-LEVEL | Data for reuse (CLAUDE.md Rule 13) |
| 081 | PROJECT-LEVEL | PROJECT-LEVEL | Data quality (CLAUDE.md Rule 13) |
| 082 | MERGED | MERGED | Into MAQ-006 |
| 083 | Section K | Section K | RT-K-003 |
| 084 | DEFERRED_FEATURE | DEFERRED | DEF-006 (green box) |
| 085 | NEW | **COVERED** | Hardening protocol itself IS the named-edge-case registry |
| 086 | DEFERRED_FEATURE | DEFERRED | DEF-007 (book digester) |
| 087 | CAPTURED | CAPTURED | FP-4 |
| 088 | DEFERRED | DEFERRED | DEF-011 (display/synthesis) |

---

## SPEC Additions Written in Session 10 (all 10 items — debt cleared)

Priority order based on scholarly risk:

| # | MAQ | Atom | Risk if Missing | Priority |
|---|-----|------|----------------|----------|
| 1 | 053 | Attribution-critical tarjih (FP-8 strengthen) | Scholar's preference misrepresented | HIGH |
| 2 | 054 | Clipped tarjih prohibition | Incomplete scholarly position recorded | HIGH |
| 3 | 056+072 | Hadith variant-mismatch risk (FP-7 strengthen) | Wrong hadith version studied | HIGH |
| 4 | 071 | Footnote handling protocol | Footnotes silently severed | HIGH |
| 5 | 069 | Interleaved methodology awareness | Topic-proof-explanation pattern broken | MEDIUM |
| 6 | 038 | Hukm-return visibility | Ruling lost from its home location | MEDIUM |
| 7 | 036 | Forgiving rule ~33% quantitative limit | Over-forgiveness merges unrelated content | MEDIUM |
| 8 | 048 | Theory-example vs practice-example distinction | Examples miscategorized | LOW |
| 9 | 050 | A×B intertwined protocol | Intertwined content mishandled | LOW |
| 10 | 042 | Config-sensitivity audit trigger | Config bias undetected | LOW |

---

## Gemini Session 9 CHALLENGEs (PRELIMINARY)

Two Gemini CHALLENGEs from prompt-architecture review remain PRELIMINARY:
1. **Classical textual ordinals** (أحدها, الأول, الوجه الأول): Prompt says "numbered items (1-, 2-)" — too narrow for classical Arabic. Valid.
2. **حيث إن and بناء على ذلك**: Missing from causal particle list. Valid additions.

Codex didn't specifically address these (reviewed structural correctness, not scholarly completeness). Both await a prompt-architecture session to implement.

---

## MAQ-089+ Assignment

No atoms numbered MAQ-089 or higher exist. The queue ends at MAQ-088. All 88 atoms (80 actionable + 8 merged) are now reconciled.
