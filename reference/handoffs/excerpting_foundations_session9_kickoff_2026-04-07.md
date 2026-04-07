# Session 9 Kickoff — Excerpting Foundations Hardening

## STOP — Read in this exact order:
1. `engines/excerpting/reference/HARDENING_SESSION_PROTOCOL.md` (§0 + §0.1 Autonomous Doctrine)
2. This handoff document
3. `engines/excerpting/CLAUDE.md`
4. `engines/excerpting/reference/B2_B3_COWORKER_SYNTHESIS_SESSION8.md` (action items T1-1..T2-7)
5. Continue from the NEXT SESSION DIRECTIVE below

## NEXT SESSION DIRECTIVE (v5.0.2 — autonomous)
- **Session type:** `prompt-architecture` — prompt refactor (§4.11 gate) + SPEC sync
- **First action:** Read DR21 prompt compression recipe (`dr_reviews/DR21_claude_prompt_compression_recipe.md`), then execute Tier 1 prompt changes + Tier 2 SPEC sync from the synthesis report.
- **Decision framework:** Protocol §4.11 (prompt refactor gate), DR21 7-step recipe, synthesis report action items
- **Owner involvement needed:** NONE unless DR relay is needed for prompt validation.

BEGIN IMMEDIATELY after reading. Do not wait for owner confirmation.

## Session 8 Accomplishments

### B2/B3 Debt Clearance — COMPLETE
- **Gemini CLI dispatched:** 11 atoms reviewed. 7 CONFIRM, 4 CHALLENGE (causal particles, Rijal texts, 20% threshold, dialectical structure). All challenges are scholarly-grounded in rational sciences.
- **Codex CLI dispatched:** 12 atoms reviewed. 3 CONFIRM, 6 NEEDS-REVISION, 3 CHALLENGE. Key finding: B3-SP1 (scholar-quoting-scholar) has no SPEC protocol — 80% dominant-layer rule can flip authorship.
- **Cross-coworker synthesis:** Zero true contradictions. Gemini evaluates scholarly accuracy, Codex evaluates structural integrity — dimensionally complementary. All atoms moved from PRELIMINARY to CONFIRMED.
- **Ledger updated:** All B2/B3 entries now show CONFIRMED status with specific amendment requirements.

### 12 SOFTENED Items — RESOLVED
- 11 ACCEPT-AS-IS: principles captured in FPs/META/MAQ, raw Layer A preserves ALL-CAPS urgency
- 1 ledger update: Atom 1 (EE-1) credited F1 as chronological origin alongside F5
- Resolution report: `SOFTENED_RESOLUTION_SESSION8.md`
- Process improvement noted: emphasis preservation protocol for future intake batches

### Prior Session Audit
- `audit_prior_session.py`: PASS (zero discrepancies)
- Tests: 917 passed, 0 failures, 4 xfailed

## What Session 8 Got RIGHT
1. **Parallel dispatch strategy** — Codex ran in background while SOFTENED items were resolved
2. **Dimensional complementarity analysis** — recognized Gemini/Codex "disagreements" as compatible evaluations
3. **/prompt-architect for both dispatches** — HR-23 compliant

## What Session 8 Got WRONG
1. **Codex CLI sandbox issues** — `python` not on PATH in Codex's PowerShell sandbox (Windows). Source-based review succeeded but script-based checks were blocked. Consider adding `python3` path to Codex config.
2. **B2-SP Gemini gap** — Gemini didn't review B2-SP (two-layer model). Only 1/2 confirmation. Low risk (FP-18 captures the concept) but noted.

## Uncommitted Work
- None. All Session 8 work committed.

## Session 9 Action Items (from B2_B3_COWORKER_SYNTHESIS_SESSION8.md)

### Tier 1: Prompt Changes (critical — prompt at 1474/1500 words)

**T1-1 (B2-P2):** Expand FORGIVING RETENTION causal particle list:
- ADD: إذ (causal in kalam/usul), لكونه (lam al-ta'lil)
- DO NOT ADD: لقوله (citation formula, different semantics)
- Soften "this list is exhaustive" → "primary causal particles for forgiving retention"
- Soften hard 15% cutoff to heuristic per Codex recommendation

**T1-2 (B3-P1):** Fix MULTI-FUNCTION SPLIT:
- Replace ">20% of text" automatic cutoff with weak heuristic
- ADD exemption: semantic dependencies (تخصيص/شرط/استثناء/تقييد) must stay with عام regardless of percentage
- Rationale: splitting عام from مخصص creates false absolutes (FP-5 silent corruption)

**T1-3 (B3-P3):** Add dialectical cross-reference to PROOF STRUCTURE:
- ADD: "(Cross-check: for dialectical structures فإن قيل/قلنا — apply FP-14. Refutation always stays with the objection it answers.)"

**BUDGET:** These 3 changes must FIT within 1500 words or the prompt needs refactoring per DR21 recipe. The prompt is at 1474/1500. Net change estimate: T1-1 adds ~10 words, T1-2 adds ~15 words, T1-3 adds ~15 words = ~40 words over cap. Prompt compression needed.

### Tier 2: SPEC Sync (7 items)

| # | Item | New SPEC Content |
|---|------|-----------------|
| T2-1 | B2-P1 | Copy anti-surface-classification to §5.2.2 |
| T2-2 | B2-P4 | Add question-cluster/dependency-first rule to §5.3.2 |
| T2-3 | B3-P2 | Add introduction scope to §5.3.2 |
| T2-4 | B3-P3 | Add proof structure to SPEC (new section or §6) |
| T2-5 | B3-SP1 | New rule SQ-1: Scholar-quoting-scholar protocol (**highest risk**) |
| T2-6 | B3-SP2 | New rule BC-1: Boundary consistency audit |
| T2-7 | B3-SP3 | New rule MF-1: Malformation-first diagnosis |

### Tier 3: Deferred
| # | Item | Reason |
|---|------|--------|
| T3-1 | B2-P4 | Rijal/biographical text exception (no fixtures) |

## Roadmap
1. **Session 9 (NEXT):** Prompt refactor + SPEC sync (T1-1..T1-3, T2-1..T2-7)
2. **Session 10:** Complete dedup (remaining 90 non-NN atoms) + MAQ-089+ assignment
3. **Session 11+:** Full-atom processing through 7-stage lifecycle

## Budget
- EUR spent Session 8: 0.00 (all work deterministic)
- EUR total: 36.70 / 100
- Budget remaining: 63.30

## Branch
`excerpting-foundations-hardening-20260404`

## Tests
917 passed, 4 xfailed, 0 failures
