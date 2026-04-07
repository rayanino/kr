# Session 12 Kickoff — Excerpting Foundations Hardening

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

## Session 11 Accomplishments

### D3 Full Intake — COMPLETE + REVIEWED
- **Problem corrected:** Session 10 wrote §6.18-6.20 from only 8 of 22 D3 files
- **All 22 files read**, 97 atomic records extracted, intake validation PASS
- **3 gaps filled:** §6.21 SSB-1 (school-specific branching), §6.22 PA-1 (pre-excerpt analysis), §6.23 AC-1 (attribution coupling)
- **10 adversarial tests added:** ADV-E-13 through ADV-E-22
- **Coworker review (2 CC subagents):**
  - Arabic reviewer: 1 CRITICAL fixed (الكلالة phantom Hanafi dissent), 5 warnings fixed
  - Code reviewer: 0 CRITICAL, 3 MEDIUM fixed, 3 LOW fixed
- **All findings resolved.** D3 SPEC additions CONFIRMED.

### Campaign Evaluation Plan Ready
- `engines/excerpting/reference/CAMPAIGN_EVAL_PLAN_SESSION11.md` — 10 taysir sample excerpts
- Key finding: 46% of definition excerpts contain embedded proof indicators
- Evaluation should happen AFTER DR28 prompt refactor (measures improvement)

### Gemini CHALLENGEs (still open from Session 10)
1. Classical textual ordinals (أحدها, الأول, الوجه الأول) — fold into DR28 CORE/FIQH module
2. حيث إن and بناء على ذلك — fold into DR28 causal particle list

## Session 12 Action Items
1. **IU-1:** Extract shared constitution from GROUP/CLASSIFY/ENRICH → new `prompts.py` with CONSTITUTION constant
2. **IU-2:** Add XML tags to constitution
3. **IU-3:** Split GROUP rules into core + 5 conditional modules (HADITH, VERSE, FIQH, DIALECTICAL, INTRO)
4. **IU-4:** Implement flag computation from chunk metadata (has_hadith_content, has_verse_content, etc.)
5. **IU-5:** Compose dynamic user message with active_rules + critical_reminders
6. **Fold in Gemini CHALLENGEs:** Classical ordinals → CORE or FIQH module. حيث إن → causal particle list.
7. **Run prompt-SPEC sync** after each IU to verify alignment
8. **Dispatch Codex + Gemini** for post-implementation review (mandatory per protocol)

## What Session 11 Got RIGHT
1. Corrected the session discipline violation systematically (read all 22 files, not just the 14 missed)
2. Full atom lifecycle extraction with catalog
3. Arabic reviewer caught a CRITICAL scholarly error that would have propagated
4. Honest [OPEN] markers on all 4 unresolved questions

## Uncommitted Work
- None — all Session 11 work committed

## Budget
- EUR spent Session 11: 0.00 (all deterministic + CC subagent review)
- EUR total: 36.70 / 100
- Budget remaining: 63.30

## Branch
`excerpting-foundations-hardening-20260404`

## Tests
942 passed (0 failures), 4 xfailed

## Prompt Coherence Counter
- GROUP_SYSTEM_PROMPT: 1483 words (unchanged — DR28 will restructure)
- CLASSIFY_SYSTEM_PROMPT: ~450 words (unchanged)
- ENRICH_SYSTEM_PROMPT: ~300 words (unchanged)
- Total prompt budget: ~2233 words across 3 prompts
- SPEC: 2859 lines (was 2530 at Session 10 start)
