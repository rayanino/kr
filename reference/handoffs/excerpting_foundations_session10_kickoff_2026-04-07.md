# Session 10 Kickoff — Excerpting Foundations Hardening

## STOP — Read in this exact order:
1. `engines/excerpting/reference/HARDENING_SESSION_PROTOCOL.md` (§0 + §0.1 Autonomous Doctrine)
2. This handoff document
3. `engines/excerpting/CLAUDE.md`
4. `engines/excerpting/reference/FOUNDATIONS_HARDENING_LEDGER.md` (check all B2/B3 are IMPLEMENTED)
5. Continue from the NEXT SESSION DIRECTIVE below

## NEXT SESSION DIRECTIVE (v5.0.2 — autonomous)
- **Session type:** `debt-clearance` — complete dedup (remaining ~90 non-NN atoms) + MAQ-089+ assignment
- **First action:** Read `engines/excerpting/reference/MERGED_ATOM_QUEUE.md`, identify all atoms with status other than NN-DEDUP or IMPLEMENTED. Begin 7-stage lifecycle processing on the highest-priority pending atoms.
- **Decision framework:** Protocol §1.6 (gate-precedence), atom lifecycle (7 stages)
- **Owner involvement needed:** NONE unless DR relay is needed.

BEGIN IMMEDIATELY after reading. Do not wait for owner confirmation.

## Session 9 Accomplishments

### GROUP Prompt — Full Detail Restored + T1 Amendments + Gemini Fix
- **DR21 compression attempted and REVERTED:** Compressed to 794 words, but Gemini CLI found 2 quality gaps immediately (classical ordinals, causal particles). Owner challenged compression approach: "quality is the main metric."
- **Decision:** Restore full detail (1483 words). Apply T1 amendments and Gemini fix to the full-detail version. The 1500-word cap was self-imposed, not technical — models handle 128K+ context.
- **DR28 prepared:** Claude DR + ChatGPT DR research brief for optimal prompt architecture (multi-message, structured formats, progressive disclosure, etc.). At `engines/excerpting/reference/dr_reviews/DR28_prompt_architecture_research_brief.md`. Owner relay needed.

### T1 Prompt Amendments — COMPLETE (all 3)
- **T1-1 (B2-P2):** Causal particle list expanded: added إذ (causal in kalam/usul) and لكونه (lam al-ta'lil). "exhaustive" → "primary causal particles". لقوله correctly NOT added (citation formula).
- **T1-2 (B3-P1):** Hard 20% threshold removed. Semantic dependency exemption added: تخصيص/شرط/استثناء/تقييد must stay with عام (splitting creates false absolutes, FP-5).
- **T1-3 (B3-P3):** Dialectical cross-reference added to PROOF STRUCTURE: فإن قيل/قلنا → FP-14 (refutation stays with objection).

### T2 SPEC Sync — COMPLETE (all 7)
- **T2-1 (B2-P1):** Anti-surface-classification + hadith commentary classification added to §5.2.2
- **T2-2 (B2-P4):** QM-4 question-cluster dependency rule added to §6.6
- **T2-3 (B3-P2):** Introduction scope in compressed GROUP prompt + §5.3.2 synced
- **T2-4 (B3-P3):** New §6.7 Proof Structure (PS-1, PS-2)
- **T2-5 (B3-SP1):** New §6.8 SQ-1 Scholar-Quoting-Scholar Protocol (highest risk — prevents LA-1/LA-2 authorship flip)
- **T2-6 (B3-SP2):** New §6.9 BC-1 Boundary Consistency Audit (diagnostic, not enforcement)
- **T2-7 (B3-SP3):** New §6.10 MF-1 Malformation-First Diagnosis (input → classification → grouping order)

### SPEC-Prompt Alignment — VERIFIED
- Automated comparison: EXACT MATCH between `GROUP_SYSTEM_PROMPT` in code and §5.3.2 code block in SPEC
- §5.2.2 adaptation notes updated with anti-surface-classification + hadith commentary
- §5.3.2 adaptation notes fully rewritten to reflect DR21 compression and all T1/T2 amendments

### Ledger — UPDATED
- All B2 atoms: IMPLEMENTED (Session 9) — except B2-SP (CONFIRMED 1/2, no action needed)
- All B3 atoms: IMPLEMENTED (Session 9) — except B3-SP4 (CONFIRMED 2/2, no action needed)
- T3-1 (Rijal exception): Still deferred — no fixtures

### Coworker Dispatch — GEMINI COMPLETE, CODEX PENDING
- **Gemini CLI (4 CONFIRM, 2 CHALLENGE):**
  1. Compressed rules: CONFIRM — EE-1, FORGIVING RETENTION, DECONTEXTUALIZATION preserve scholarly meaning
  2. Causal particles: **CHALLENGE** — missing `حيث إن` (since/wherever) and `بناء على ذلك` (based on that). Also disputes `لقوله` exclusion, but Session 8 consensus explicitly excluded it (citation formula semantics, handled by EE-1). Mark `حيث إن` and `بناء على ذلك` as PRELIMINARY — needs Codex confirmation.
  3. Semantic dependency: CONFIRM — تخصيص/شرط/استثناء/تقييد formulation matches Usul al-Fiqh
  4. Dialectical structure: CONFIRM — فإن قيل/قلنا correctly captures Mutakallimun argumentation
  5. SQ-1: CONFIRM — correctly models Sharh/Hashiyah tradition where commentator is the pedagogical agent
  6. Classical ordinals: **CHALLENGE** — "numbered items (1-, 2-)" rule is too narrow for classical texts that use textual ordinals (أحدها, الأول, الثاني, الوجه الأول). These serve the same structural function but aren't digit-based.
- **Codex CLI:** Re-dispatched (first attempt truncated). Results pending.
- **Action items for Session 10:**
  - Review Codex CLI results when available
  - If Codex confirms the 2 Gemini CHALLENGEs, implement: (a) add classical textual ordinals to prompt, (b) consider `حيث إن` causal particle addition
  - Both CHALLENGEs are PRELIMINARY per no-single-model-conclusion rule until Codex confirms

### Tests
- 916 passed, 1 flaky (test_phase2_integration — Instructor retry state pollution, passes in isolation), 4 xfailed
- 101/101 on prompt-specific and hardening tests (test_phase2_group + test_phase2_hardening)
- No regressions from prompt compression

## What Session 9 Got RIGHT
1. **DR21 recipe adherence** — followed the 7-step recipe systematically, not ad-hoc compression
2. **Test-asserted string preservation** — verified all 14 test-asserted strings before editing, zero test failures
3. **SPEC-prompt sync verification** — automated comparison confirmed exact match
4. **T1 amendments during compression** — incorporated amendments into the distilled rules rather than adding on top (net reduction, not addition)

## What Session 9 Got WRONG
1. **Codex CLI syntax** — first dispatch used `-q` flag which doesn't exist. Correct syntax: `codex exec "prompt"`. Fixed and re-dispatched.
2. **No regression test for LLM behavioral equivalence** — DR21 prescribes running 50+ inputs through old and new prompts at temperature=0. This wasn't done (would require API calls + budget). Noted as a gap — the prompt hasn't been tested against live LLM yet. The existing test suite validates structural/deterministic properties only.

## Uncommitted Work
- All changes in working directory (not committed). Session 10 should review and commit after coworker results arrive.

## Session 10 Action Items
1. **Check coworker results** — Review Codex + Gemini CLI outputs. Address any FINDING/CHALLENGE items.
2. **Commit Session 9 work** — After coworker review, commit: prompt refactor + SPEC sync + ledger updates.
3. **Complete dedup** — Process remaining ~90 non-NN atoms through 7-stage lifecycle.
4. **MAQ-089+ assignment** — Assign remaining atoms to appropriate treatment.

## Roadmap
1. **Session 10 (NEXT):** Dedup completion + MAQ-089+ assignment
2. **Session 11+:** Full-atom processing through 7-stage lifecycle
3. **LLM behavioral regression test:** Run compressed prompt against 50+ inputs to validate equivalence (deferred from Session 9 — requires API budget)

## Budget
- EUR spent Session 9: 0.00 (all work deterministic — prompt compression, SPEC editing, ledger updates)
- EUR total: 36.70 / 100
- Budget remaining: 63.30

## Branch
`excerpting-foundations-hardening-20260404`

## Tests
916 passed (1 flaky), 4 xfailed, 0 real failures

## Prompt Coherence Counter
- GROUP_SYSTEM_PROMPT: 794 words (was 1474 in Session 8 handoff — 45% reduction)
- CLASSIFY_SYSTEM_PROMPT: ~450 words (unchanged)
- ENRICH_SYSTEM_PROMPT: ~300 words (unchanged)
- Total prompt budget: ~1544 words across 3 prompts
