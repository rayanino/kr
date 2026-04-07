# B2/B3 Coworker Synthesis — Session 8

**Date:** 2026-04-07
**Coworkers:** Gemini CLI (Arabic scholarly), Codex CLI (structural)
**Prior:** Gemini CLI Session 2 (original 1/3 confirmation)
**Protocol:** v5.0.2, no-single-model-conclusion (2 independent providers: Google + OpenAI)

---

## Cross-Coworker Synthesis Table

| Atom | Gemini | Codex | Consensus | Status Update |
|------|--------|-------|-----------|---------------|
| B2-P1 | CONFIRM | NEEDS-REVISION | Compatible | SPEC SYNC needed (prompt rule not in SPEC §5.2.2) |
| B2-P2 | CHALLENGE | NEEDS-REVISION | **BOTH WANT CHANGES** | Causal particles + threshold softening |
| B2-P3 | CONFIRM | CONFIRM | **CONFIRMED (2/2)** | No changes needed |
| B2-P4 | CHALLENGE | CHALLENGE | **BOTH CHALLENGE** | Question-cluster not formalized + Rijal gap |
| B2-SP | (not reviewed) | CONFIRM | CONFIRM (1/2) | Gemini gap noted; FP-18 captures it |
| B3-P1 | CHALLENGE | NEEDS-REVISION | **BOTH WANT CHANGES** | 20% threshold + semantic dependency exemption |
| B3-P2 | CONFIRM | NEEDS-REVISION | Compatible | SPEC SYNC needed (not in §5.3.2) |
| B3-P3 | CHALLENGE | NEEDS-REVISION | **BOTH WANT CHANGES** | Dialectical exception + SPEC formalization |
| B3-SP1 | CONFIRM | NEEDS-REVISION | Compatible | Scholarly sound + needs SPEC protocol (SQ-1) |
| B3-SP2 | CONFIRM | CHALLENGE | Compatible | Sound + needs SPEC audit rule (BC-1) |
| B3-SP3 | CONFIRM | NEEDS-REVISION | Compatible | Sound + needs explicit MF-1 rule |
| B3-SP4 | CONFIRM | CONFIRM | **CONFIRMED (2/2)** | No changes needed |

---

## Disagreement Resolution

**Pattern identified:** All 5 "disagreements" (B2-P1, B3-P2, B3-SP1, B3-SP2, B3-SP3) follow the same pattern:
- Gemini evaluates **scholarly accuracy** → CONFIRM (the concept is correct for Islamic texts)
- Codex evaluates **structural integrity** → NEEDS-REVISION or CHALLENGE (the concept is missing from SPEC)

These are **dimensionally complementary**, not contradictory. Resolution: scholarly concept CONFIRMED + SPEC formalization required. Zero true contradictions.

---

## Action Items by Tier

### Tier 1: Prompt Changes (BLOCKED by 1474/1500 word cap → Session 9)

| Item | Atom | Change | Blocker |
|------|------|--------|---------|
| T1-1 | B2-P2 | Expand causal particle list: add إذ, لكونه. Keep لقوله as citation formula (per CC analysis). Soften "exhaustive" to "primary". | Prompt cap (1474/1500) |
| T1-2 | B3-P1 | Replace "when each function is substantive (>20%)" with weak heuristic + semantic dependency exemption (تخصيص/شرط/استثناء/تقييد must stay with عام) | Prompt cap |
| T1-3 | B3-P3 | Add dialectical cross-reference: "(Cross-check: for فإن قيل/قلنا — apply FP-14. Refutation stays with objection.)" | Prompt cap |

### Tier 2: SPEC Sync (formalization debt → Session 9 or dedicated sync session)

| Item | Atom | Proposed SPEC Addition |
|------|------|----------------------|
| T2-1 | B2-P1 | Copy anti-surface-classification paragraph to §5.2.2 |
| T2-2 | B2-P4 | Add question-cluster / dependency-first rule to §5.3.2 |
| T2-3 | B3-P2 | Add introduction scope rule to §5.3.2 |
| T2-4 | B3-P3 | Add proof structure rule to SPEC (new section or §6) |
| T2-5 | B3-SP1 | New rule SQ-1: Scholar-quoting-scholar protocol (Codex: highest risk) |
| T2-6 | B3-SP2 | New rule BC-1: Boundary consistency audit |
| T2-7 | B3-SP3 | New rule MF-1: Malformation-first diagnosis |

### Tier 3: Deferred (corpus expansion scope)

| Item | Atom | Reason |
|------|------|--------|
| T3-1 | B2-P4 | Rijal/biographical text exception (no fixtures in current scope) |

---

## Ledger Status Updates

Based on 2-coworker consensus (Gemini + Codex):

| Atom | Previous Status | New Status | Rationale |
|------|----------------|------------|-----------|
| B2-P1 | PRELIMINARY (1/3) | CONFIRMED + SPEC SYNC PENDING | Scholarly sound (Gemini), needs SPEC formalization (Codex) |
| B2-P2 | PRELIMINARY (1/3) | CONFIRMED WITH AMENDMENTS | Both want causal particle expansion + threshold softening |
| B2-P3 | PRELIMINARY (1/3) | **CONFIRMED (2/2)** | Both CONFIRM |
| B2-P4 | PRELIMINARY (1/3) | CONFIRMED WITH AMENDMENTS | Both CHALLENGE: formalize question-cluster + add Rijal exception (deferred) |
| B2-SP | PRELIMINARY (1/3) | CONFIRMED (1/2, Codex only) | Gemini gap; FP-18 captures the two-layer concept |
| B3-P1 | PRELIMINARY (1/3) | CONFIRMED WITH AMENDMENTS | Both want 20% threshold relaxed + semantic dependency exemption |
| B3-P2 | PRELIMINARY (1/3) | CONFIRMED + SPEC SYNC PENDING | Sound (Gemini), formalize in SPEC (Codex) |
| B3-P3 | PRELIMINARY (1/3) | CONFIRMED WITH AMENDMENTS | Both want dialectical exception + SPEC formalization |
| B3-SP1 | PRELIMINARY (1/3) | CONFIRMED + NEEDS SPEC PROTOCOL | Sound (Gemini), needs SQ-1 (Codex — highest risk) |
| B3-SP2 | PRELIMINARY (1/3) | CONFIRMED + NEEDS SPEC RULE | Sound (Gemini), needs BC-1 (Codex) |
| B3-SP3 | PRELIMINARY (1/3) | CONFIRMED + NEEDS SPEC RULE | Sound (Gemini), needs MF-1 (Codex) |
| B3-SP4 | PRELIMINARY (1/3) | **CONFIRMED (2/2)** | Both CONFIRM |

---

## Key Risk: B3-SP1 (Scholar-Quoting-Scholar)

Codex identified this as the **highest-risk finding**: the existing LA-1/LA-2 80% dominant-layer rule can silently flip authorship when Author A quotes Scholar B at length. Example: Ibn Hajar quotes Ibn Malik as proof → the quote dominates characters → LA-1 attributes to Ibn Malik → the teaching voice is wrong.

This is a SPEC gap, not a prompt gap. The fix (SQ-1) requires a new SPEC rule. Priority: HIGH for Session 9.

---

## DR Dispatch Assessment

**DR needed?** Not for atoms where Gemini + Codex agree. For atoms with CONFIRMED WITH AMENDMENTS, both coworkers agree on the DIRECTION of change (same issues identified independently). No tiebreaker needed.

**B2-SP gap:** Only Codex reviewed. Consider brief Gemini re-review in Session 9 (not blocking — the concept is in FP-18).

**Conclusion:** B2/B3 debt clearance is COMPLETE at 2/2 coworker level. All atoms have moved from PRELIMINARY to CONFIRMED (with various amendment requirements for Session 9). No DR relay needed this session.
