# Session 11 Kickoff — Excerpting Foundations Hardening

## STOP — Read in this exact order:
1. `engines/excerpting/reference/HARDENING_SESSION_PROTOCOL.md` (§0 + §0.1 Autonomous Doctrine)
2. This handoff document
3. `engines/excerpting/CLAUDE.md`
4. `engines/excerpting/reference/dr_reviews/DR28_synthesis.md` (the implementation blueprint)
5. Continue from the NEXT SESSION DIRECTIVE below

## NEXT SESSION DIRECTIVE (v5.0.2 — autonomous)
- **Session type:** `prompt-architecture` — implement DR28 converged prompt architecture
- **First action:** Read `DR28_synthesis.md`, then implement IU-1 through IU-5 (GROUP prompt refactor). Start with IU-1: extract shared constitution into `prompts.py`.
- **Decision framework:** DR28 synthesis is the governing blueprint. Protocol §4.11 (prompt refactor gate) applies.
- **Owner involvement needed:** NONE unless A/B testing needs budget approval (IU-10, ~EUR 10).

BEGIN IMMEDIATELY after reading. Do not wait for owner confirmation.

## Session 10 Accomplishments

### MAQ Dedup Reconciliation — COMPLETE
- **All 80 actionable MAQ atoms reconciled** against actual SPEC/code content
- **Key finding:** B4/B5 "SPEC-ONLY" was disposition tag, not implementation status — 10 atoms had classified dispositions but no SPEC text written
- **All 10 written:** SPEC-PENDING went from 10 → 0

### 10 SPEC Additions Written
- FP-7 strengthened: hadith variant-mismatch risk (MAQ-056/072)
- FP-8 strengthened: attribution-critical tarjih + clipped tarjih prohibition (MAQ-053/054)
- §6.11 FN-1: Footnote handling protocol (MAQ-071)
- §6.12 IM-1: Interleaved methodology awareness (MAQ-069)
- §6.13 HR-1: Hukm-return visibility (MAQ-038)
- §6.14 FR-1: Forgiving rule ~33% quantitative limit (MAQ-036)
- §6.15 CS-1: Configuration-sensitivity audit trigger (MAQ-042)
- §6.16 TE-1: Theory-example vs practice-example (MAQ-048)
- §6.17 IC-1: A×B intertwined content protocol (MAQ-050)

### Codex CLI Results (Session 9 pending → processed)
- 5 PASS, 1 MEDIUM (FP-3 stale wording — already fixed)
- No blockers for prompt architecture work

### Gemini CHALLENGEs (PRELIMINARY — still open)
1. **Classical textual ordinals** (أحدها, الأول, الوجه الأول): Prompt "numbered items (1-, 2-)" is too narrow for classical Arabic. Valid. Should be addressed during DR28 implementation (when GROUP prompt is restructured).
2. **حيث إن and بناء على ذلك**: Missing from causal particle list. Valid. Fold into DR28 implementation.

### DR28 Dependencies — ALL CLEARED
- Gemini CLI: English-instruction safety **CONFIRMED** ("All 5 items SAFE")
- Codex CLI: Instructor+XML is a non-issue (XML in prompt text, Instructor handles output schema)
- Both providers converged on 2-message instruction sandwich + progressive disclosure

## Session 11 Action Items
1. **IU-1:** Extract shared constitution from GROUP/CLASSIFY/ENRICH → new `prompts.py` with CONSTITUTION constant
2. **IU-2:** Add XML tags to constitution
3. **IU-3:** Split GROUP rules into core + 5 conditional modules (HADITH, VERSE, FIQH, DIALECTICAL, INTRO)
4. **IU-4:** Implement flag computation from chunk metadata (has_hadith_content, has_verse_content, etc.)
5. **IU-5:** Compose dynamic user message with active_rules + critical_reminders
6. **Fold in Gemini CHALLENGEs:** Classical ordinals → CORE module or FIQH module. حيث إن → causal particle list.
7. **Run prompt-SPEC sync** after each IU to verify alignment
8. **Dispatch Codex + Gemini** for post-implementation review (mandatory per protocol)

## What Session 10 Got RIGHT
1. **Evidence-based reconciliation** — every atom verified against actual SPEC content, not ledger claims
2. **Exposed the SPEC-ONLY ambiguity** — documented the disposition-vs-implementation distinction
3. **Efficient SPEC writing** — 10 sections written with proper scholarly grounding in one session
4. **Hook compliance** — updated NEXT.md when flagged (post-milestone protocol)

## What Session 10 Got WRONG
1. **Initial undercount** — first estimated ~90 non-NN atoms needed processing, actual count was 80 actionable with 10 SPEC-pending
2. **No coworker dispatch for SPEC additions** — the 10 new SPEC sections were written by CC alone. Per no-single-model-conclusion rule, these are PRELIMINARY until at least Codex reviews them. This is a known gap — Session 11 should dispatch Codex for SPEC §6.11-6.17 review.

## Uncommitted Work
- None — all Session 10 work committed in 3 commits on `excerpting-foundations-hardening-20260404`

## Roadmap
1. **Session 11 (NEXT):** DR28 prompt architecture (IU-1 through IU-5)
2. **Session 12:** Apply architecture to CLASSIFY and ENRICH (IU-6, IU-7)
3. **Session 13:** A/B test monolithic vs progressive on 50+ inputs (IU-10, ~EUR 10)
4. **Post-hardening:** Book Resolution → Tier 1 smoke run (10 books, ~$30)

## Budget
- EUR spent Session 10: 0.00 (all deterministic)
- EUR total: 36.70 / 100
- Budget remaining: 63.30

## Branch
`excerpting-foundations-hardening-20260404`

## Tests
937 passed (0 real failures), 4 xfailed

## Prompt Coherence Counter
- GROUP_SYSTEM_PROMPT: 1483 words (unchanged from Session 9 — DR28 will restructure)
- CLASSIFY_SYSTEM_PROMPT: ~450 words (unchanged)
- ENRICH_SYSTEM_PROMPT: ~300 words (unchanged)
- Total prompt budget: ~2233 words across 3 prompts
