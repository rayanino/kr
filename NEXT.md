# NEXT -- Owner-Facing Visual Representations

## CURRENT FRONTIER — ACTIVE

**Branch:** `clean-start` (the only branch — repo cleaned 2026-04-13)
**Repo state:** 6,339 tracked files, 18 root files, 1 branch, clean git status

Repo cleanup is COMPLETE (Session 23). Active work now:
- owner-facing visual representations: mermaid diagrams, architecture maps, pipeline flow diagrams
- documentation reshaping that helps the owner inspect system structure and give non-technical reactions

Paused work:
- excerpting code changes (frozen at 1008 pass, 0 fail, 4 xfail)
- new excerpting smoke runs or generalization runs
- prompt/contract/spec changes tied to excerpting fixes

Excerpting freeze state:
- frozen test state: `1008` pass, `0` fail, `4` xfail
- frozen budget state: `EUR 36.70 / 100.00`
- exact checkpoint note: `reference/handoffs/excerpting_pause_checkpoint_2026-04-08.md`

Current deliverable:
- produce visual representations that let the owner inspect the pipeline, control surfaces, and information flow and then give informed non-technical reactions

## ARCHIVED EXCERPTING FRONTIER (paused 2026-04-08)

---

## AUTONOMOUS OPERATIONS — READ FIRST

**You are the control tower.** The owner is your client, not your project lead. He is available for exactly 4 things:

1. **DR relay** — pasting prompts into ChatGPT/Claude/Gemini DR windows (physical action you cannot perform)
2. **Owner-preference questions** — "does this excerpt serve your study?", "good / bad / confusing?"
3. **Plan approval at formal gates** — Ijazah Lock 4, Phase transitions, protocol amendments
4. **Providing new materials** — collection bundles, source files

**For EVERYTHING else, you decide and execute:**
- Session type → gate-precedence matrix (§1.6) decides. Do NOT ask the owner.
- Next step → this file's roadmap + protocol determine it. Do NOT ask "what should I do?"
- Technical approach → you + coworkers (Codex, Gemini, DR) decide. Owner cannot answer these.
- Quality assessment → you + coworkers evaluate. Owner catches reading-experience issues only.
- Error detection → coworkers + scripts catch errors. Owner should NEVER be the one finding gaps.

**After every milestone:** Report what you accomplished (past tense), what you decided, and what you're doing next (already starting). If you need owner input, ask ONE specific non-technical question. Then continue working — do not stop.

**This directive applies to ALL agents:** CC sessions, Codex overnight, Gemini CLI, dispatched subagents. No agent may wait for owner guidance on technical matters.

---

## IMMEDIATE STATE (updated 2026-04-07 — Session 17 COMPLETE: Campaign evaluation on taysir, 6/6 coworkers done)

### Session 14 — Autonomous System Execution (2026-04-07)
- **All 4 Session 13 next-steps EXECUTED:**
  1. ✅ **Phase 0 infrastructure built:** `autonomous_schemas.py` (10 Pydantic models, JSONL I/O), `research_gap_scanner.py` (4 scanners: SPEC OPEN, limitations, taxonomy, calibrated), `process_dr_response.py` (section extraction, finding classification, KB persistence). Directory: `overnight_codex/autonomous/knowledge_base/`. All pyright-clean.
  2. ✅ **OQ-001-004 RESOLVED in SPEC §6.18-6.23:** All 4 [OPEN] markers converted to [CALIBRATED] with DR37's concrete fiqh cases. OQ-001: ثمرات الخلاف test (5 Hanafi/Shafi'i calibration cases). OQ-002: 7 significance criteria (4 new from DR37: استقلال المبنى, تغيّر الفنّ, البناء على أصل, قصد الإفادة). OQ-003: 3-principle context-fill test (أمن اللبس, المعلوم من السياق, البناء على الأصل). OQ-004: 3-layer analysis authority model (preserve structure, semantic tagging override, cross-disciplinary indexing).
  3. ✅ **Batch 2 DR relay queue generated:** 10 prompts (5 aqidah, 3 sarf, 1 balagha, 1 cross-science) targeting Gemini DR for taxonomy tree research gaps. File: `docs/autonomous-system/dr_relay_queue_batch_2.md`.
  4. ✅ **DR33 framework corrections applied:** 6 amendments (critical path RT-03 start, RT-13 split into 13a/13b, scholarly allocation 22%→28%, imla' 250+→80-120, 6 topics pre-advanced to ACTIVE/DEEP, simplified TSI proxy).
- **Tests:** 942 passed, 4 xfailed. All pyright clean.
- **Budget:** EUR 0.00 this session (all deterministic).
- **4-source verification COMPLETE:** CC Code (Anthropic), CC Scholarly (Anthropic), Codex CLI (OpenAI), Gemini CLI (Google). All PASS. 24 findings found and fixed.
- **4 commits:** `e9cdccba4` (core), `546088e11` (DR28 refactoring), `2e6acff5b` (state), `cedde2645` (infra).

### Session 17 — Campaign Evaluation COMPLETE (2026-04-07)
- **HIGHEST PRIORITY GATE ANSWERED:** The pipeline produces good school handling, scholar identification, and cross-school detection. But it has 3 systematic defects: numbered-list fragmentation, pronoun-based SC misrating, and missing OCR detection.
- **10 taysir excerpts deep-evaluated** against 22 FPs + 23 domain rules + 4 DR37-calibrated thresholds
- **6/6 coworkers complete:** CC Arabic Reviewer (Anthropic), CC Structural (Anthropic), Gemini CLI (Google), Codex CLI (OpenAI), ChatGPT DR (OpenAI), Claude DR (Anthropic). 3-provider diversity.
- **Final verdict: 4 PASS, 3 ADVISORY, 3 FAIL**
- **5 CONFIRMED findings:**
  1. **Numbered-list fragmentation (CRITICAL):** 568 excerpts (44.3%) follow numbered-list patterns; 191 (14.9%) below MV-1 25-word floor. Root cause: `merge_micro_units()` (phase3_deterministic.py:170) only handles structural openers/closers, not MV-1 content pass. ChatGPT DR confirms: merge by default, standalone only when semantically independent.
  2. **SC misrating on pronoun suffixes (HIGH):** 82 excerpts (6.4%) rated FULL with unresolved ها/هم/هما. Claude DR: use Farasa (98.9% accuracy) or CAMeL Tools for clitic segmentation + antecedent checking.
  3. **FR-1 gate inappropriate for sharh (HIGH):** Claude DR: "A percentage-of-words heuristic should not govern splitting decisions" for def+proof+attr units. Al-Ghazali + Ibn Taymiyyah methodology demands unity. Exempt IC-1 intertwined content from FR-1 percentage gate.
  4. **OCR word corruption undetected (MEDIUM):** 2 instances in Sample 7 (مال روى, برواتها). Gemini CLI caught what CC missed. Add OCR word-corruption detector to arabic_fidelity_flags.
  5. **المعنى الإجمالي (RESOLVED — LOW):** Arabic reviewer + Gemini said FAIL; Claude DR said variable classification is CORRECT (container, not label). Resolution: add `structural_section` facet, audit the 13 classified as `definition`.
- **Report:** `integration_tests/campaign_20260331/taysir/CAMPAIGN_EVAL_SESSION16.md`
- **DR archives:** ChatGPT DR at `downloads/deep-research-report (19).md`, Claude DR at `downloads/compass_artifact_wf-ae430a21-...md`
- **Budget:** EUR 0.00 this session (evaluating existing data)

### Session 21 — DR40 Smoke Test + MV-1 Merge Conflict Fix (2026-04-08)

**DR40 split rules work correctly in LLM Phase 2b — but Phase 3 MV-1 merge was destroying them. Fixed.**

**Smoke test findings:**
- **كتاب الطهارة smoke (7 excerpts):** DR40 companion_definition link emitted correctly on النية definition pair. One inaccurate link target description (MEDIUM — enrichment error, not structural). Evidence splitting NOT triggered (correct — no multi-type evidence in this chapter).
- **كتاب الطلاق smoke v1 (11 excerpts):** Phase 2b (LLM) correctly split the definition pair (لغة/شرعا) AND evidence types (Quran/Sunnah/Ijma) into separate units with relationship links — EXACTLY matching the owner's rejected output expectations. BUT Phase 3 merge_subviable_units() merged ALL 6 split units (7-20 words each) back into one 172-word mega-excerpt, undoing the LLM's correct work.
- **Root cause:** MV-1 (25-word floor) treats any unit < 25 words as a fragment to merge. DR40 split rules intentionally produce sub-25-word units (a 7-word Quranic citation is a complete teaching unit when linked to its ruling). MV-1 had no exemption for relationship-linked units.

**Fix applied:**
- `phase3_deterministic.py` line 385: added `and not u.related_units` exemption alongside existing isnad exemption
- 2 new regression tests: `test_related_units_preserved_despite_subviable` (definition pair), `test_evidence_split_units_preserved_despite_subviable` (evidence types)
- Fixed pre-existing pyright errors in test file (missing `Optional` import, `TeachingUnit` import)
- **1008 tests, 0 failures, 4 xfailed. All pyright clean.**

**Talaq smoke v2 running** with fix applied — expected to produce ~20 excerpts instead of 11.

**Integration test runner:** Added `--div-id` argument to `scripts/run_integration_test.py` for targeting specific divisions without processing the entire package.

**Coworker dispatch prompts prepared** (via /prompt-architect): Gemini CLI (Arabic scholarly accuracy of split rules) + Codex CLI (structural/contract review). Awaiting dispatch.

**Session 21 completion (second commit `baab068ac`):**
- Talaq v2 confirmed: 20 excerpts (vs 11), evidence types split, 6 relationship links, 0 structural issues
- Gemini CLI: 1 CONFIRM, 3 AMEND (SPEC §6.24/§6.25 updated), 1 FLAG
- Codex CLI: 2 ISSUE (inbound-only fixed via linked_targets, chain-remap tracked), 6 PASS
- Codex-verify: 3 CC reviewers all PASS, 1 HIGH fixed, 2 MEDIUM fixed
- Prompt exemptions (d) composite proof and (e) cross-type interdependence added to prompts.py
- **1008 tests, 0 failures, 2 commits: `7493562fa` + `baab068ac`**

**Session 22 — Handoff to Codex (CC weekly limit reached)**

**COMPLETED (Session 22, CC):**
- ✅ Excerpt review UI: added related_units rendering (commit `91a860fbe`)
- ✅ 3-reviewer verification: 2 CRITICAL + 2 HIGH fixed (commit `b08b2c2fb`)
- ✅ Smoke test: `eval_session22_talaq/` — 21 excerpts, 0 errors, 0 gates (owner ran)
- ✅ Owner confirmed: eval_session22_talaq is "much better" than dr40_smoke_talaq_v2
- ✅ Review server working: `python tools/review.py integration_tests/review_session22/` on port 8385
- ✅ Authority transferred to Codex (ACTIVE_AUTHORITY.md updated)

**OWNER ACTION — Start reviewing excerpts:**
```
python tools/review.py integration_tests/
```
Opens browser → select `dr40_smoke_talaq_v2` → review 20 excerpts → mark ACCEPT/NEEDS WORK/REJECT with comments. Feedback saves to `integration_tests/dr40_smoke_talaq_v2/owner_feedback.jsonl`.

**CODEX NEXT STEPS (authority: codex as of 2026-04-08):**
1. ~~Run fresh smoke test~~ ✅ Done: `integration_tests/eval_session22_talaq/` — 21 excerpts, 0 errors
2. **Owner is reviewing excerpts in the UI.** After review: read `integration_tests/review_session22/eval_session22_talaq/owner_feedback.jsonl`, analyze verdict patterns, translate NEEDS WORK/REJECT feedback into pipeline improvements
3. **Pick 2-3 diverse chapters** for generalization testing — one from a different kitab, one hadith-heavy, one with cross-madhab debate. Use: `python scripts/run_integration_test.py --package-path experiments/format_diversity_test/packages/taysir/ --output-dir integration_tests/eval_<name> --div-id <div_id> --backend api`
4. **Coworker dispatch** on any pipeline changes (Gemini CLI for Arabic scholarly accuracy)
5. **Review server:** `set KR_REVIEW_PORT=8385 && python tools/review.py integration_tests/review_session22/` — copy new outputs into `integration_tests/review_session22/` for owner review

**Branch:** `excerpting-foundations-hardening-20260404`
**Tests:** 1008 pass, 0 fail, 4 xfail
**Budget:** EUR 36.70 / 100.00 (63.30 remaining)

### Session 20 — DR40 Granularity Calibration Implementation (2026-04-08)

**All 5 DR40 decisions implemented: SPEC + contracts + prompts + tests. Owner feedback gap CLOSED.**

**Changes:**
- **SPEC FP-13 re-ranked:** Leaf-atomicity promoted to #4, pedagogical packaging demoted to #5 (UI concern)
- **3 new foundational principles:** FP-23 (relationship links), FP-24 (conditional evidence splitting), FP-25 (definition pair splitting)
- **2 new domain rules:** §6.24 (DP-SPLIT-1 definition pairs), §6.25 (EV-SPLIT-1 evidence type splitting)
- **PS-1 proof structure amended** for FP-24 alignment
- **Contracts:** `RelationshipType` enum (3 values), `UnitRelationship` model, `related_units` on TeachingUnit + ExcerptRecord
- **Prompts:** CONSTITUTION precedence stack, GROUP_CORE_RULES conditional evidence, GROUP_FIQH_RULES definition pair + evidence type splitting, GROUP_OUTPUT_FORMAT related_units, GROUP_CRITICAL_REMINDERS
- **Phase 3 propagation:** related_units flows through deterministic assembly and both merge functions
- **DEFINITION now triggers GROUP_FIQH_RULES** in compute_active_modules (FP-25)
- **CR-31 registered** in CONSTRAINT_REGISTRY.md (≤15 word parenthetical exemption — UNCALIBRATED)
- **18 new regression tests** from owner rejections — 1006 total, 0 failures, 4 xfailed
- **Budget:** EUR 0.00 (all deterministic)

**Immediate next steps:**
1. ~~**Smoke test** the taysir talaq chapter with updated prompts~~ ✅ Done (Session 21)
2. **Dispatch coworkers** — Gemini CLI for Arabic scholarly accuracy of split rules, Codex CLI for contract review
3. **Full campaign rerun** to measure impact on all 1,491 excerpts

### Session 19 — Campaign Rerun Analysis + CRITICAL FEEDBACK GAP DISCOVERED (2026-04-08)

**Campaign rerun validated all 5 structural fixes. But owner feedback from Session 17 baseline was never consumed — the core excerpting quality problem (grouping granularity) is untouched.**

**Campaign rerun metrics (1,491 excerpts vs 1,283 baseline):**
- Sub-MV-1 (<25w): 244 → **0** (PERFECT — target met)
- Pronoun/anaphora flags: 0 → 23 (1.5%) — detector working
- Content intertwined flags: 0 → 728 (48.8%) — IC-1 detector working, rate reasonable for sharh fiqh
- Isnad preservation: 16 → 28 — chains kept atomic
- Self-containment FULL: 68.7% → **85.4%** (+16.7pp)
- Avg word count: 74.8 → 123.0 (merged sub-viables shifted distribution up)
- Run time: ~4.4 hours at concurrency=1. 10 chunk failures (8 classify, 2 group). 17 verification_skipped in div_7_006.

**10 Gemini DR Batch 2 responses ingested and synthesized:**
- All 10 provide actionable taxonomy decisions. 7/10 recommend expanding or separating nodes.
- Key: nahw/sarf boundary rules, verb derivation vs tense separation, أعمال القلوب expand to 10-12, فهم السلف/إجماع separate, السحر/الكهانة separate, الأسماء والصفات needs 30-35 leaves not 20.
- Full synthesis: see session 19 conversation log.
- Archived at: `reference/dr_reviews/batch2_gemini/DR_B2_01` through `DR_B2_10`.

**CRITICAL FINDING — Owner feedback gap:**
- Owner reviewed 2 excerpts from baseline run (2026-03-31) in `integration_tests/campaign_20260331/taysir/owner_feedback.jsonl`. Both REJECTED with detailed reasoning about grouping granularity being too coarse.
- **3 consecutive sessions (17, 18, 19) saw the pointer in NEXT.md line 823 and none opened the file.**
- The campaign rerun produced the rejected excerpt (talaq definition) BYTE-IDENTICAL to the baseline — the 5 Session 18 fixes addressed structural defects, not grouping quality.
- 13.4% of excerpts (200 `_pre_` chunks) bypass LLM grouping entirely.

**Core systemic issue identified (3 layers):**
1. **No feedback loop** from owner output-quality reactions back to pipeline behavior. Abstract feedback (questionnaire) has a pipeline. Concrete feedback (output reactions) does not.
2. **Granularity calibration untested.** FP-9 (anti-overgranulation) + FP-13 (granularity priority #5) push the pipeline toward "keep together." Owner's actual reaction: "too broad — just cutting up book pages." These rules came from F8 about taxonomy trees, got over-applied to excerpting boundaries.
3. **`_pre_` chunk bypass.** 200 excerpts from small divisions skip LLM grouping — no function-level analysis happens on them.

### Session 19 — Next Steps (CRITICAL PATH)

**Priority order:**

1. **DR on granularity calibration + feedback loop design** (OWNER ACTION: relay to ChatGPT DR or Claude DR)
   - Core question: "What is the right excerpting granularity for a comparative Islamic scholarly library — one scholarly function per excerpt, or coherent teaching paragraphs — and how should owner feedback on real output systematically feed back into pipeline behavior?"
   - Must address: FP-9/FP-13 recalibration, `_pre_` chunk bypass, owner rejection trace-back mechanism
   - Include owner_feedback.jsonl content (both reviews) as concrete examples

2. **Build owner feedback consumption pipeline**
   - Every session that touches excerpting MUST read `owner_feedback.jsonl` before doing any evaluation or excerpt selection
   - Owner rejections must trace back to specific pipeline decisions (Phase 1 assembly? Phase 2 grouping? _pre_ bypass?)
   - This should be a hook, not documentation

3. **structural_section enrichment prompt** — field exists but unpopulated (deferred from Session 18)

4. **Taxonomy tree amendments from Batch 2 DRs** — 10 decisions ready for implementation (2-3 sessions)

### Session 18 — 5 Fixes IMPLEMENTED + 3-Source Review HARDENED (2026-04-08)

**All 5 Session 17 findings implemented, then independently verified by 3 reviewer agents (code-reviewer + arabic-auditor + architect). 5 additional issues found and fixed in the same session.**

**7 commits, 991 tests passing:**
1. ✅ `ad455a4` — MV-1 sub-viable merge pass (`merge_subviable_units()`, 9 tests)
2. ✅ `1416200` — Pronoun-suffix SC validation (V-P3-10, 6 tests)
3. ✅ `f27b0e6` — IC-1 content_intertwined flag (2 tests)
4. ✅ `b9b65d8` — StructuralSection enum + field
5. ✅ `963bd49` — OCR word-corruption detector
6. ✅ `04c4c00` — **3-source review fixes:** char-offset bug (use _word_to_char_range), isnad chain protection (_ISNAD_MARKERS), pronoun ه false-positive removal, antecedent marker cleanup, EX_M_012→review_flag
7. ✅ `658b997` — structural_section TODO in enrichment

**3-source review findings (all resolved):**
- Code Reviewer: char-offset arithmetic fails on multi-space (HIGH→FIXED), missing trailing test (HIGH→FIXED), pronoun ه false positives (HIGH→FIXED)
- Arabic Auditor: isnad splitting risk (CRITICAL→FIXED), root-final ه vocabulary (WARNING→FIXED), الله/ابن/أبو antecedent suppression (WARNING→FIXED)
- Architect: pronoun check should be review_flag not error code (HIGH→FIXED), structural_section dead field (MEDIUM→TODO added)

**Batch 2 DR dispatched:** 10 Gemini DR prompts relayed and researching (2026-04-08).

### Session 18 — Next Steps (HANDOFF TO NEXT CC SESSION)

**Priority order:**

1. **Campaign re-run on taysir** (~€2.93 via API)
   - Validates 191→0 sub-MV-1 and 82→0 pronoun misrating targets empirically
   - Must use same 5 packages (ext_39_masala, ext_46_qa, ibn_aqil_v1, ibn_aqil_v3, taysir)
   - Compare against Session 17 baseline: 4 PASS, 3 ADVISORY, 3 FAIL → expect improvement

2. **Batch 2 DR intake** — 10 Gemini DR responses to process
   - Archive each response, extract findings, synthesize
   - Topics: hadith isnad boundaries, sharh layer detection, mashyakha handling, nahw parsing, aqidah classification, tafsir verse detection, qa format detection, fiqh madhab attribution, poetry detection, manuscript colophon parsing

3. **structural_section enrichment prompt** — the field exists (contracts.py) but enrichment prompt doesn't populate it
   - Add to UnitEnrichment schema
   - Update ENRICH prompt to classify structural_section
   - Wire into phase3_enrichment.py model_copy

4. **MV-1 corpus-specific calibration** — the 25-word floor was calibrated on taysir (fiqh). Arabic-auditor flagged: hadith collections have 15-20 word isnads that are legitimate standalone units. When processing hadith texts, the floor may need adjustment. Tracked in CONSTRAINT_REGISTRY CR-29.

### Session 15 — DR28 Prompt Architecture COMPLETE + 6-Source Verification (2026-04-07)
- **DR28 IU-6/IU-7/IU-8/IU-9 implemented:** CLASSIFY and ENRICH refactored to 2-message architecture (system=CONSTITUTION, user=rules+input+reminders). SPEC §5.2.2/§5.2.3/§5.3.2/§5.3.3/§7.2.2/§7.2.3 updated.
- **6-source multi-provider verification COMPLETE:** CC Code Reviewer (Anthropic), Gemini CLI ×2 (Google), Codex CLI (OpenAI), CC Arabic Auditor (Anthropic), CC Architecture Auditor (Anthropic). 10 findings found, all resolved.
- **Key fixes from review:** Instruction sandwich preserved on retry (error feedback inside `<error_correction>` before `<critical_reminders>`), GROUP cache key mismatch fixed, CLASSIFY reminder improved with derived-rulings rule per Gemini suggestion, SPEC §7.2.2 narrator role + confidence threshold synced to code.
- **Tests:** 971 passed, 4 xfailed. pyright clean.
- **Commits:** `546088e11` (DR28 refactoring), `eb88f611d` (6-source review fixes).

### Session 16 — Autonomous Dashboard BUILT (2026-04-07)
- **Dashboard operational:** `python scripts/dashboard.py` → localhost:8000
  - 4 pages: DR Relay Queue (10 Batch 2 prompts), Findings (38 from DR37), Ideas (form → ideas.jsonl), Status (aggregate stats)
  - FastAPI + HTMX + Jinja2, dark theme, one-click prompt copy, sidebar nav
  - Data layer reads existing JSONL files via autonomous_schemas.py Pydantic models
  - Files: `scripts/dashboard.py`, `scripts/autonomous_dashboard/{app,store,__init__}.py`, `scripts/autonomous_dashboard/templates/{base,relay,findings,ideas,status}.html`
  - Seeder: `scripts/seed_batch2_prompts.py` (already run, 10 prompts in knowledge_base/dr_prompts/batch_2.jsonl)
- **Tests:** All smoke tests pass (4 pages render, idea submission persists, real data displays).

### Next Steps (for next CC session)
  1. ✅ **Campaign evaluation on taysir** — Session 17 COMPLETE. 5 confirmed findings.
  2. ✅ **Implement all 5 fixes** — Session 18 COMPLETE. 7 commits, 991 tests, 3-source review.
  3. ✅ **Campaign re-run** — Session 19. All 5 structural fixes validated. But core grouping quality untouched.
  4. ✅ **Batch 2 DR intake** — Session 19. All 10 Gemini DRs synthesized. 10 taxonomy decisions ready.
  5. **CRITICAL: DR on granularity + feedback loop** — See Session 19 Next Steps. Owner commissioning.
  4. **Owner relay: Batch 2 DR prompts** — 10 Gemini DR prompts ready in dashboard at localhost:8000 AND at `docs/autonomous-system/dr_relay_queue_batch_2.md`.
  5. **IU-10: A/B test monolithic vs progressive** — ~EUR 10 budget. Validates DR28 empirically.

### Session 13 — Autonomous System Design + DR Processing (2026-04-07)
- **DESIGN.md written + 2 design reviews + 12 amendments applied**
- **8 DR prompts relayed, ALL 8 responses received and archived (DR32-39):**
  - DR32 (ChatGPT): Dashboard FastAPI+HTMX (4.75/5), 6-stage response pipeline, Idea Quarry creative framework
  - DR33 (Claude): 20 research topics (RT-01 to RT-20), 3-phase strategy, TSI saturation index, critical path 35-45 days
  - DR34 (Gemini): Hadith isnad-matn boundaries — 7 new patterns beyond existing rules
  - DR35 (ChatGPT): Passaging engine gap analysis + hardening priorities
  - DR36 (ChatGPT): Multi-layer sharh/hashiyah detection patterns
  - DR37 (Gemini): OQ-001-004 calibration — 5 fiqh cases, 4 new significance criteria, context-fill principles
  - DR38 (Gemini): 18 sciences — 54 DR questions, 10 ranked edge cases, completeness criteria
  - DR39 (Claude): Taxonomy "no brain" — LLM adapter not built, gold baseline 100% invalid, 10 priorities
- **4 coworker reviews COMPLETE (2 design + 2 DR validation):**
  - Structural: dashboard PASS, critical path corrected (starts RT-03 not RT-01), 6/20 topics partially answered, no embedding infra for TSI
  - Scholarly: allocation 22%→28-30%, RT-13 must split (Quran vs hadith), imla' 250+→80-120, RT-06/07 co-dep = tanzil al-'ilm
- **5 confirmed decisions:** Dashboard FastAPI+HTMX, 20-topic research framework, taxonomy LLM adapter Priority 1, OQ-001-004 resolved by DR37, genre-prioritized hardening

### Session 11 — D3 Full Intake + Coworker Review (2026-04-07)
- **D3 intake:** Read ALL 22 files (97 atomic records). Session 10 only read 8/22.
- **3 gaps found and filled:** School-specific branching (§6.21), pre-excerpt structural analysis (§6.22), attribution coupling rules (§6.23)
- **2 existing sections amended:** §6.18 LP-1 ([OPEN] marker), §6.19 PO-1 (attribution-coupling direction + [OPEN])
- **10 adversarial tests added:** ADV-E-13 through ADV-E-22
- **Coworker review COMPLETE (2 CC subagents):**
  - **Code reviewer:** 0 CRITICAL, 0 HIGH, 3 MEDIUM (all fixed: AC-1→FR-1 link, ADV refs, NN-008 explicit)
  - **Arabic reviewer:** 1 CRITICAL (fixed: الكلالة example misframed — Hanafi dissent is phantom, all 4 madhabs agree), 5 warnings (all fixed: consensus weight, AP-003 domain grounding, phantom عند الحنابلة removed, fixture refs added)
- **All findings addressed.** SPEC sections are now CONFIRMED (2-source reviewed).
- **Campaign evaluation plan ready:** `engines/excerpting/reference/CAMPAIGN_EVAL_PLAN_SESSION11.md` — 10 sample excerpts extracted from taysir
- **Key campaign finding:** 46% of definition excerpts contain embedded proof indicators — D3 rules are directly relevant to real data
- **Tests:** 942 passed, 4 xfailed, 0 failures. SPEC: 2859 lines.
- **Next:** DR28 prompt architecture (IU-1 through IU-5), then campaign evaluation on 10 taysir samples.

### Pipeline Visual Architecture (2026-04-07)
- **Created:** `docs/architecture/pipeline_diagrams.md` — 4 Mermaid diagrams (pipeline overview, data flow, excerpting internals, source internals)
- **Changelog mechanism:** CHG-NNN entries at bottom of file — update when engine status, contracts, or architecture changes
- **Renders on:** GitHub, VS Code (Mermaid extension), any Mermaid-compatible viewer

### DR29-DR31 Processing Session (2026-04-07) — 3 Deep Research Reports
- **DR29 (ChatGPT):** Strategic audit of excerpting improvement portfolio. 15 ranked items. **8/8 code claims verified against source.** Highest-accuracy DR to date.
- **DR30 (Claude):** 19 silent failure modes in overnight system. **Core assumptions wrong** — claimed no atomic writes exist (they do), claimed SBERT dedup (it's slug-based). Valid finding: missing `os.fsync()` in atomic_write.
- **DR31 (Gemini):** Autonomous template evaluation for Islamic texts. 8 existing templates scored avg 1.6/5 on Islamic scholarly grounding. 6 new templates proposed. Pending Codex CLI structural review.
- **6 code fixes implemented (917 pass):**
  1. `filter_relevant_footnotes` multi-occurrence bug fixed (while-loop instead of single find())
  2. `text_snippet` now deterministic (`primary_text[:80]` not LLM-supplied)
  3. V-P3-2 short-text policy — micro-units no longer auto-dropped
  4. Evidence markers expanded: hadith 6→14, ijma 5→9
  5. EX-M-011 added to SPEC error catalog (was contracts-only)
  6. `os.fsync()` added to overnight `atomic_write()`
- **Deferred:** `review_flags` placeholder refactoring (large blast radius — needs coworker validation before changing I-ER-4 model validator)
- **Coworker reports processed (2/2):**
  - Codex CLI: DR31 templates — T4+T6 COMPATIBLE, T1/2/3 NEEDS_ADAPTATION, T5 INCOMPATIBLE (requires Arabic judgment)
  - Gemini CLI: DR29 #4 USUALLY_MERGE (bidirectional: forward for openers, backward for closers). DR29 #8 minimum-viable takhrij = 4 required fields (hadith_anchor, sources, locator, provenance)
- **Micro-unit merge pass implemented (931 pass, +16 tests):**
  - `merge_micro_units()` in phase3_deterministic.py — bidirectional merge per Gemini scholarly validation
  - Called from phase3_orchestrator before build_deterministic_excerpts
  - Bare openers forward-merge, bare closers backward-merge, semantically-complete headings exempt

### Memory System Upgrade (2026-04-07) — 6-Source Investigation + 3-Layer Implementation
- **Trigger:** Owner challenged dismissal of mempalace → full 6-source investigation launched
- **Sources:** DR25 (Claude DR — critical audit), DR26 (ChatGPT DR — architecture design), DR27 (Gemini DR — Islamic scholarly traditions), Gemini CLI (domain validation), Codex CLI (structural verification), CC direct measurements
- **Architecture decided:** 4-layer system. Graph DB and mempalace permanently killed by domain expert.
- **Layer 1 DEPLOYED:** AGENTS.md expanded 465B→8KB with Arabic scholarly conventions. @AGENTS.md import in CLAUDE.md. Codex overnight now reads curated conventions.
- **Layer 2 DEPLOYED:** `generate_memory_index.py` auto-generates MEMORY.md (154→102 lines, 6 broken YAML files recovered). `check_invariant_consistency.py` detects doctrine drift + Arabic invariants. Fixed 5-vs-7 engine contradiction.
- **Layer 3 DEPLOYED:** `session_stop.py` appends JSONL events to `memory/events/` with provenance (Sanad principle).
- **Layer 4 DEFERRED:** SQLite FTS5 when corpus outgrows grep.
- **Gemini CLI review:** Identified 3 HIGH findings (all fixed), 3 MEDIUM deferred, 3 LOW deferred. CC-first rating: 5/10 retrieval, 5/10 domain, 1/10 student learning (by design — pipeline-first).
- **Remaining:** Codex CLI review pending. Kunnash/Ishkalat/Bridge Mechanism are post-pipeline features.
- **DRs archived:** DR25, DR26, DR27 + Codex crossref in `engines/excerpting/reference/dr_reviews/`

### Session 8 Accomplishments (2026-04-07) — Debt Clearance
- **B2/B3 CONFIRMED (2/2 coworkers):** Gemini CLI + Codex CLI reviewed all 12 atoms. Zero true contradictions — dimensional complementarity. 3 Tier-1 prompt changes + 7 Tier-2 SPEC sync items identified → Session 9.
- **12 SOFTENED items RESOLVED:** 11 accept-as-is, 1 ledger update. BCV Session 4 debt CLEARED.
- **Highest risk found:** B3-SP1 (scholar-quoting-scholar) — no SQ-1 protocol in SPEC, 80% rule can flip authorship.
- **917 tests pass**, prior session audit PASS.

### Session 3 Accomplishments (2026-04-06)
- **Protocol v5.0 COMPLETE** — Batch Lifecycle Protocol: §3A (6-phase model), §3B (Completion Gate), §3C (Ijazah Ceremony), §4.18 (Regression Gate), §4.19 (Doctrine Coherence), §5.8 (Role Separation), §8.5 (Calibration File), §0.1 (Autonomous Operations Doctrine)
- **12 scripts built** (S-01 to S-12): 8 batch verification + 4 norm enforcement
- **3 PreToolUse hooks** for hard enforcement: enforce-autonomy.sh, enforce-prompt-architect.sh, track-prompt-architect.sh
- **DR17-DR19 processed**: manuscript verification scholarly grounding, norm decay research, hard enforcement architecture
- **HR-23 to HR-26 added**: mandatory prompt-architect, lint before session end, hooks never disabled, cross-model auditing
- **915 tests pass**, all checks green

### Session 4 BCV Complete (2026-04-07)
- **First BCV on F1-F8**: 139 files verified, 208 MCUs traced, 94.7% MAPPED, 5.8% SOFTENED, 0% MISSED
- Gate script bug found and fixed (META terminal state)
- 12 SOFTENED items documented for debt clearance

### Session 10 Accomplishments (2026-04-07) — Dedup Reconciliation + SPEC Debt Clearance

- **MAQ dedup COMPLETE:** All 80 actionable atoms reconciled against SPEC/code. Key finding: B4/B5 "SPEC-ONLY" was disposition tag not implementation status — 10 atoms had classified dispositions but no SPEC text. All 10 now written. SPEC-PENDING: 0.
- **10 SPEC additions written:**
  - FP-7 strengthened: hadith variant-mismatch risk (MAQ-056/072)
  - FP-8 strengthened: attribution-critical tarjih + clipped tarjih prohibition (MAQ-053/054)
  - §6.11 FN-1: Footnote handling protocol (MAQ-071)
  - §6.12 IM-1: Interleaved methodology awareness (MAQ-069)
  - §6.13 HR-1: Hukm-return visibility (MAQ-038)
  - §6.14 FR-1: Forgiving rule ~33% quantitative limit (MAQ-036)
  - §6.15 CS-1: Configuration-sensitivity audit trigger (MAQ-042)
  - §6.16 TE-1: Theory-example vs practice-example (MAQ-048)
  - §6.17 IC-1: A×B intertwined content protocol (MAQ-050)
- **Codex CLI Session 9 results processed:** 5 PASS, 1 MEDIUM (already fixed). No blockers.
- **Reconciliation doc:** `engines/excerpting/reference/DEDUP_RECONCILIATION_SESSION10.md`
- **Reconciled totals:** 37 implemented, 22 covered, 0 SPEC-pending, 10 deferred, 3 open, 8 merged, 4 captured
- **Tests:** 937 passed, 4 xfailed, 0 real failures. Prompt-SPEC sync: PASS.
- **Budget:** EUR 0.00 this session (all deterministic). Total: 36.70/100.

### D3 Intake (2026-04-07) — LAST Questionnaire Question

- **D3 "Multi-Layered Definition"**: 22-file ChatGPT bundle processed. Owner case study: الكلالة with definition/proof/attribution layers.
- **3 new SPEC sections:** §6.18 LP-1 (leaf pollution prevention), §6.19 PO-1 (packaging ≠ ontology), §6.20 SH-1 (source hints non-deciding)
- **2 documented (not hardened):** pre-excerpt deep analysis (arch question), significance threshold calibration (needs more cases)
- **Q&A HARDENING PHASE COMPLETE.** All questionnaire answers (F1-F8, G1-G4, SC1-SC3, D3) processed.

### What's Needed Next

1. **Evaluate existing campaign data (HIGHEST PRIORITY):** The $97 campaign (2,303 excerpts from 5 books, 2026-03-31) has never been evaluated against the hardened SPEC. Pick 1 book. CC + coworkers evaluate every excerpt against 22 FPs + 20 domain rules. Surface only study-experience questions to owner. This proves whether the doctrine translates to reality.
2. **DR28 prompt architecture:** Instruction sandwich + progressive disclosure (8-12 rules per call from 25). Synthesis at `engines/excerpting/reference/dr_reviews/DR28_synthesis.md`. Restructure all 3 prompts. Addresses Gemini's 2 PRELIMINARY CHALLENGEs.
3. **3 OPEN design questions need DR:** MAQ-074 (chapter-intro marking), MAQ-075 (EE-1 hadith exceptions), MAQ-077 (non-taxonomic guidance).
4. **Section K red-team tests:** 62 tests to automate as pytest cases.
5. **Deferred:** review_flags placeholder refactoring, DR31 Templates, Book Resolution session

### PARALLEL WORKSTREAM: 3-Month Feedback Collection Strategy (2026-04-07)

**Goal:** Design the optimal system for collecting ALL owner-dependent data before July 1 (summer full-time build phase).

**Accomplished (this session):**
- Owner interview (4 rounds): study priorities (Arabic→fiqh→usul→aqidah), fatigue profile (prefers structured/interactive), granularity is #1 excerpt issue, product vision ("present everything, tell me just memorize")
- 5 coworkers dispatched with /prompt-architect-optimized prompts (**4/5 received**, 1 pending)
- **DR18 (Claude DR):** 42 owner-dependent decisions across all 5 engines. Critical path: science scope → book priority → muhaqiq list. ~5h tedious now, ~20-30h summer.
- **Codex CLI:** 11 policy families (DT-01..11) with dependency chain. Root: user model. Two-layer insight: policy precedes decisions. Only FP-8/FP-18 need calibration. TEAM_TRANSLATION_GUIDE has zero FP-13..22 mapping.
- **Gemini CLI:** Student-first pedagogical analysis. 9 unique findings including FP-1 challenge (qa'idah+shahid separation for flashcard mode), shubuhat safety, genre overrides, 2 genuine gaps (cognitive complexity grading, active recall output format).
- **ChatGPT DR:** Only coworker to inventory what's ALREADY COLLECTED. 5 missing data families from campaign evidence. Bundle format evaluation (4 weaknesses, 3 additions). Error classification by owner-dependency.
- All 4 reports: saved to `engines/excerpting/reference/dr_reviews/`, verified against codebase, cross-referenced, corrections documented
- **PRELIMINARY 4-COWORKER SYNTHESIS COMPLETE** at `engines/excerpting/reference/dr_reviews/PRELIMINARY_SYNTHESIS_4_OF_5.md`
- **4-layer architecture CONFIRMED across 4/5 coworkers:**
  - Layer 1: User model + pedagogical modes → "What kind of student?" (~2h, partially resolved)
  - Layer 2: Quality policies + S-1 governance → "What rules govern output?" (~3h, mostly missing)
  - Layer 3: Engine decisions + parameters → "What configures each engine?" (~5h, 5 sessions)
  - Layer 4: Calibration with real output → "Does engine match the brain?" (~20-30h, summer)

**ALL 5 COWORKERS COMPLETE. Final synthesis:** `engines/excerpting/reference/dr_reviews/FINAL_SYNTHESIS_5_OF_5.md`
**Gemini DR added:** Fiqh masking layer, mantiq as science #19, Basran terminology default, month-by-month calendar.

**Owner curriculum decisions (2026-04-07, RESOLVED):**
1. Primary madhab: **Hanbali** → fiqh masking layer suppresses Hanafi/Shafi'i/Maliki until baseline mastery
2. Mantiq: **Yes, add as science #19** → foundational logic tree required before usul al-fiqh
3. Basran terminology: **TBD** (not yet asked — lower priority, blocks nahw synonym layer)

**Session 11 accomplishments (feedback collection workstream):**
- **S-1 INTAKE COMPLETE:** 18 files unzipped, validated (9 JSONL, 3 YAML, 6 MD/TXT). 11 governance atoms extracted to MERGED_ATOM_QUEUE.md Section M. Key atoms: teaching-unit-as-goal (S1-001), source integrity constraint (S1-002), self-containment dual reading (S1-003), granularity ≠ brevity (S1-004), usefulness ≠ mutation license (S1-005). All PRELIMINARY (0/3 coworkers).
- **`/ce:plan` COMPLETE:** `docs/plans/2026-04-07-001-feat-feedback-collection-system-plan.md` — 7 implementation units across 4 phases. Strengthened by 2 research agents that discovered existing questionnaire infrastructure at `integration_tests/questionnaire/`.
- **Unit 1 DONE:** `scripts/bundle_intake.py` (224 lines, 13 tests, pyright clean). Automates: unzip → validate manifest/JSONL/YAML → inventory → archive.
- **Unit 2 DONE:** `shared/user_model/owner_profile.yaml`. 19 sciences, Hanbali madhab, fatigue profile, S-1 priority architecture. 7/46 decisions resolved.
- **Unit 5 DONE:** `engines/excerpting/reference/COLLECTION_TRACKER.md`. 57 items across 4 layers, calendar milestones, DR18 session mapping. 13 resolved, 44 pending.
- **Recovery:** Restored MERGED_ATOM_QUEUE.md, FINAL_SYNTHESIS_5_OF_5.md, brainstorm requirements from git after Codex session deletions.
- **Codex CLI review prompt prepared** (via /prompt-architect) for plan + S-1 atom validation. 5 checks: structural consistency, requirements coverage, 4-layer alignment, atom correctness, cross-artifact consistency.

**Next steps (feedback collection workstream):**
1. **Dispatch Codex CLI review** of plan + S-1 atoms (prompt ready — owner relays to `codex exec`)
2. **Unit 3:** Questionnaire templates for K/E/D series (deep-dive ChatGPT sessions using S-1 format)
3. **Unit 4:** DR18 engine decision session templates (5 sessions, structured/interactive)
4. **S-1 atom coworker validation:** Minimum 2 independent sources before any atom advances

**Next steps (main hardening lane — HIGHEST PRIORITY):**
1. **DR28 prompt architecture implementation** — instruction sandwich + progressive disclosure (8-12 rules per call from 25). Synthesis at `engines/excerpting/reference/dr_reviews/DR28_synthesis.md`.
2. **3 OPEN design questions:** MAQ-074, MAQ-075, MAQ-077 — each needs a DR.
3. **Section K red-team tests:** 62 tests to automate as pytest cases.

**Key owner data already collected from interview (partially resolves 9 of 42 decisions):**
- Science priority: Arabic first, fiqh/usul/aqidah passion lane
- Priority book: الفقه على المذاهب الأربعة
- Study level: beginner
- Product vision: eliminate preparation, go straight to memorization
- Excerpt issue: engine under-divides (granularity)
- Feedback preference: 10-15 excerpts/session, structured/interactive, show reasoning

**Tracker:** `engines/excerpting/reference/dr_reviews/COWORKER_SYNTHESIS_TRACKER.md`

### COMPLETED: Environment Audit (2026-04-06)

### COMPLETED: Environment Audit (2026-04-06)

Debiased two-session environment audit. Merged plan at `reference/handoffs/environment_merged_plan_2026-04-06.md`.

**Key deliverables:**
- **Coverage baseline established: 82%** (914 tests, branch coverage). Gap: `tracer.py` 0%, `parallel_orchestrator.py` 56%.
- **7 tools activated:** pytest-cov, DeepEval (3 GEval metrics), DuckDB (SQL over results), promptfoo (config), mutmut (config), IAA metrics (Cohen's kappa), camel-tools (verified working)
- **context-mode plugin evaluated: DO NOT INSTALL** (WebFetch conflict, hook collision, CVE surface)
- **MCP cleanup identified:** 5 dead/failed servers to remove (owner action needed)
- **Run:** `pytest engines/excerpting/tests/ --cov=engines/excerpting/src --cov-branch --cov-report=term-missing`

**Environment next steps (not blocking hardening):**
1. Owner: `claude mcp remove exa && claude mcp remove fetch` — remove dead MCP servers
2. Investigate `tracer.py` (0% coverage) — dead code or untested entry point?
3. Run `npx promptfoo eval --config engines/excerpting/promptfooconfig.yaml` after next prompt change
4. Tier 2 items (hypothesis, pytest-xdist, OpenITI, Usul.ai) in a follow-up session

### ACTIVE LANE: Foundations Hardening (atom-by-atom)

Branch: `excerpting-foundations-hardening-20260404`
Ledger: `engines/excerpting/reference/FOUNDATIONS_HARDENING_LEDGER.md`
**Protocol: `engines/excerpting/reference/HARDENING_SESSION_PROTOCOL.md` v5.0 (GOVERNING LAW) — ALL 6 BATCH LIFECYCLE DRs PROCESSED (DR12-DR17)**
Plan: `.claude/plans/protocol-v50-batch-lifecycle.md` (Batch Lifecycle plan — 52 requirements from 6 DRs, Gemini-corrected)

**Foundations Q&A: 8 / 8 answered (F1-F8). G1-G4 + SC1-SC3 intake IN PROGRESS (Session 5).** Owner continuing methodology for all 40 questions.

### Session 5 — Intake-Only (2026-04-07, IN PROGRESS)

**Completed:**
- 7 bundles flattened from `_bundle/engines/excerpting/` nesting to `chatgpt_{series}_collection/`
- `batch_inventory.py` run on all 7 (inventory.json created per bundle)
- `batch_verification_init.py` run on all 7 (verification_status.json initialized)
- All 7 raw owner reactions (Layer A ground truth) read by CC
- 60 ground truth atoms pre-extracted to `engines/excerpting/reference/G_SC_GROUND_TRUTH_PREEXTRACTION.md`
- Tests: 915 pass (1 flaky LLM eval: `test_dialectical_preserved` 0.788 vs 0.8 — pre-existing)
- Prompt-SPEC sync: PASSED

**Completed (extraction):**
- 7 parallel extraction agents: **157 atoms** from 143 files (7,500 lines read)
- Ground truth validation: **PASS** (60/60 pre-extracted atoms confirmed)
- Arabic degradation: **0 pipeline-introduced** (4 source OCR artifacts noted)
- MERGED_ATOM_QUEUE.md Section L integrated (157 atoms, 10 FP candidates, 36 prompt-affecting)
- Session 6 handoff: `reference/handoffs/excerpting_foundations_session6_kickoff_2026-04-07.md`
- Disposition: 36 PROMPT (blocked §4.11), 62 SPEC, 10 FP, 24 META, 14 DEFERRED, 11 overlap

**Key findings:**
- **SC1 TRANSFORMATIVE**: Owner realized excerpts are "teaching units" (would rename engine)
- **SC3 CRITICAL**: 5x "PIPELINE CATASTROPHICALLY LACKING SECURITY GATES" — post-excerpting reassembly gate needed
- **G1 FP candidate**: "Excerpting is OBJECTIVE — NO OUTSIDE FACTORS" (generalizes FP-4)
- **Prompt RESTORED (Session 9)**: GROUP_SYSTEM_PROMPT at 1483 words — full detail + T1-1/T1-2/T1-3 amendments + Gemini classical ordinals fix. DR21 compression attempted then reverted (owner: quality > compression). 1500-word cap REMOVED. DR28 prepared for long-term prompt architecture research.
- **PRELIMINARY debt**: B2 (1/3) + B3 (1/3) + all G/SC (0/3)

### Session 9 Foundation Integrity Audit + DR28 Architecture (2026-04-07)
- **3-coworker audit** of all 38 numeric constraints: 7 HIGH, 15 MEDIUM, 16 LOW. No other phantom constraints.
- **Fix 1:** Consensus text truncation ([:1500]) REMOVED — verifier sees full text now.
- **Fix 2:** GROUP_MAX_TOKENS made dynamic (8192/16384/32768) matching CLASSIFY/ENRICH.
- **Fix 3:** `CONSTRAINT_REGISTRY.md` — every threshold documented with origin + calibration status.
- **Guardrail:** `constraint-origin-trace.md` rule — prevents phantom constraint pattern.
- **Codex doctrine audit:** 18 ALIGNED, 4 DRIFT (FP-5/11/21/22 — all deferred implementation, not contradictions).
- **Gemini Arabic audit:** 8/10 lists UNSOUND (PRELIMINARY). Deferred to DR28 architecture.
- **DR28 received (2 providers):** ChatGPT DR (10+ citations) + Claude DR (60+ sources). Converged architecture: 2-message instruction sandwich + progressive disclosure (8-12 rules per call, down from 25). Synthesis at `engines/excerpting/reference/dr_reviews/DR28_synthesis.md`. Codex + Gemini validating compatibility.

### Session 9 Accomplishments (2026-04-07) — Prompt Architecture + SPEC Sync
- **T1-1/T1-2/T1-3 prompt amendments:** Causal particles expanded (إذ, لكونه). Semantic dependency exemption (تخصيص/شرط/استثناء/تقييد stays with عام, FP-5). Dialectical cross-ref (فإن قيل/قلنا → FP-14).
- **T2-1..T2-7 SPEC sync:** Anti-surface-classification in §5.2.2. QM-4 in §6.6. New §6.7 (PS-1/PS-2 proof structure), §6.8 (SQ-1 scholar-quoting-scholar — highest risk), §6.9 (BC-1 boundary audit), §6.10 (MF-1 malformation-first diagnosis).
- **Gemini CLI fix:** Classical textual ordinals (أحدها, والثاني, الوجه الأول) added to NUMBERED ITEMS.
- **Codex CLI fix:** FP-3 causal particle list synced with prompt (stale "exhaustive" wording corrected).
- **DR21 compression attempted then reverted:** 1440→794 words lost quality (Gemini found 2 gaps). Owner challenged: "quality > compression." Full detail restored at 1483 words. 1500-word cap removed.
- **DR28 brief prepared:** Long-term prompt architecture research (multi-message, structured formats, progressive disclosure). Ready for Claude DR + ChatGPT DR relay.
- **All B2/B3 atoms: IMPLEMENTED.** Ledger updated.
- **917 tests pass**, SPEC-prompt alignment: EXACT MATCH.

**Roadmap (updated):**
1. **Sessions 6-9**: COMPLETE
2. **Session 10 (NEXT):** Implement DR28 prompt architecture (instruction sandwich + progressive disclosure, 10 implementation units). Check Codex/Gemini validation results first. Then: dedup remaining ~90 non-NN atoms.
3. **Session 11+:** Full-atom processing (G/SC atoms through 7-stage lifecycle)
4. **After hardening:** A/B test new vs monolithic prompt on 50+ inputs (~EUR 10). Book Resolution (40 DR20 titles → Shamela IDs). Tier 1 smoke run (10 books, ~$30).

**Session 2 complete. Protocol v4.0 → v4.1 patch in progress.** ChatGPT DR adversarial review (DR9, archived at `engines/excerpting/reference/dr_reviews/DR9_chatgpt_protocol_v40_adversarial.md`) found 18 issues (8 CRITICAL, 9 HIGH, 1 MEDIUM). Cross-referenced by explore agent: 12 confirmed gaps, 4 partially addressed, 2 already fixed. Plan approved, implementation in progress: 14 protocol amendments + 1 closure verifier script + version bump.

**v4.1 amendment status: COMPLETE**
- Units 1-14: All 14 protocol text amendments applied
- Unit 15: `scripts/verify_atom_closure_minimal.py` — BUILT AND PASSING (12 closed atoms verified)
- Unit 16: Version bump to v4.1 — DONE (protocol, NEXT.md, check_protocol_version.py all agree)

**Key v4.1 changes (from DR9):**
- Checkpoint resolution gate in §1.6 (prevents orphaned atoms)
- model_only atoms ineligible for Light Lane (closes authority bypass)
- WIP cap split: active-processing vs awaiting-external (prevents deadlock)
- Blinded DR tiebreaker template (ensures independence)
- Session-type compatibility matrix (only 2 allowed combinations)
- Q-12 outcome spot-check for cross-science atoms (outcomes, not just artifacts)
- Owner engagement heartbeat every 10 atoms post-50 (prevents silent disengagement)
- Doctrine backfill protocol on amendment (§8.4)

**Protocol review COMPLETE:**
- Codex CLI: 4/4 accepted → v2.2
- Gemini CLI: 7/7 accepted → v2.1
- ChatGPT DR: 10/38 accepted (38 findings + 10 pre-mortems, 4/10 score) → v3.0 (DR6)
- Gemini DR: 5/8 accepted, 3 redirected (8 findings, 4/10 + 3/10 scores) → v3.1 (DR7)
- Claude DR: 8/19 accepted (19 findings, 5/10 score) → v3.2 (DR8)
- All DR reports archived: `engines/excerpting/reference/dr_reviews/DR6-DR8`

**Atom progress:**
| # | Atom | Status |
|---|------|--------|
| 1 | EE-1 (explained + explanation unity) | FINALIZED + EMPIRICALLY VALIDATED (taysir + ibn_aqil) |
| 2 | NC-1 (context hierarchy) | FINALIZED |
| 3 | Linking-word preservation | FINALIZED (C-SC-2 expanded) |
| 4-5 | Khilaf/tarjih separation | DOCUMENTED, deferred to K-1/K-2/K-3 |
| 6-12 | Remaining doctrinal atoms | FINALIZED (FP-1 through FP-10 in SPEC §1.1b) |
| **B1** | **Safety & Integrity batch (17 MAQ atoms)** | **CONFIRMED (4/4 coworkers). FP-5/FP-2 strengthened, FP-19/20/21/22 added.** |
| **B2** | **Self-Containment batch (5 MAQ atoms)** | **PRELIMINARY (1/3 coworkers). 4 prompt rules added (+210 words). Gemini found Bukhari title flaw → fixed.** |
| **B3** | **Boundary & Grouping batch (10 MAQ atoms)** | **PRELIMINARY (1/3 Gemini). 3 prompt rules (+141w), 4 SPEC-only. Prompt: 1423/1500.** |
| **B4** | **Granularity (17 MAQ atoms)** | **IMPLEMENTED. 1 prompt rule (+51w), 16 SPEC-only. Prompt: 1474/1500 (FULL).** |
| **B5** | **Tarjih/Khilaf/Proof (21 MAQ atoms)** | **SPEC-ONLY. Prompt FULL. 9 SPEC rules, 7 deferred cross-engine.** |
| **B6** | **Other (9 MAQ atoms)** | **SPEC-ONLY. 3 SPEC, 2 deferred, rest documented/verified.** |

**Session 2 deliverables so far:**
- MERGED_ATOM_QUEUE.md built (556 lines, 250 ideas, 88 actionable atoms, 0 silent drops)
- Batch 1 (Safety & Integrity): 6 FP changes implemented — FP-2 strengthened (anti-rescue), FP-5 strengthened (cascade), FP-19 (omission honesty), FP-20 (validation rigor), FP-21 (severity class), FP-22 (anti-covert-excerpter)
- Codex + Gemini challenged and synthesized. Key finding: Gemini's al-Ghazali adversarial scenario proves FP-19 is existentially necessary.
- 907/907 tests pass, 0 regressions
- SPEC now has 22 FPs (FP-1 through FP-22, excluding FP-18 numbering)

**What's needed next:**
1. **DR coworker confirmation** — combined relay prompt prepared for Batches 1-3. All files pushed to remote branch. Batches stay PRELIMINARY until DR reviews.
2. **SPEC §6 formalization** — Batch 4/5/6 SPEC-only atoms need formal §6 subsection entries (not just ledger documentation). ~30 rules to add.
3. **Red-team test expansion** — 62 tests documented, only 9 automated. Create additional pytest cases for highest-priority tests.
4. **Empirical validation** — run atom_test.py against taysir fixture with the hardened prompt to verify new rules don't cause regressions.
5. **Prompt optimization** — 1474/1500 words. If empirical validation shows LLM ignoring late rules (primacy bias), consider REPLACING lower-priority rules with higher-priority ones.

**Session 3 = intake-only session (per protocol v4.0 §1.5 + §1.6 gate precedence):**

PREREQUISITE GATE (§0 checklist):
1. Read `HARDENING_SESSION_PROTOCOL.md` v4.0 (§0 checklist + version delta from v3.3). Run `python scripts/check_protocol_version.py` to verify version consistency.
2. Read `engines/excerpting/CLAUDE.md` + this file + `FOUNDATIONS_HARDENING_LEDGER.md` (recent entries only — dispatch subagent for full ledger)
3. Verify branch: `excerpting-foundations-hardening-20260404`. Run pytest + `check_prompt_spec_sync.py` — must pass.
4. Inventory bundles: `ls *.zip` at repo root → G1-G4 + SC1 exist → gate 4 (§1.6) triggers → session type = `intake-only`.
5. State: "Session type: intake-only. No atom processing this session. Target: complete intake for 5 bundles."

PHASE A — Bundle Intake (G1-G4 + SC1, follow §3 exactly):
6. Unzip 5 bundles to `engines/excerpting/chatgpt_{series}_collection/`
7. Per bundle: dispatch subagent for inventory → conflict scan (including Arabic text degradation per §3.2 Step 3) → per-file atom extraction (NOT single bulk pass — §3.2 Step 4)
8. Coverage verification: flag any files with 0 extracted atoms for re-read (prevents Session 1's 124-gap failure)
9. Assign MAQ-IDs, integrate into `MERGED_ATOM_QUEUE.md`. Deduplicate against existing F1-F8 atoms.
10. Archive zips to `source_artifacts/`. Verify quality gate (§3.3 — 8 checkboxes).

PHASE B — Preliminary Debt + Future Session Planning:
11. Count PRELIMINARY atoms from Session 2 (B1-B3). Check if DR responses arrived since Session 2.
12. Do NOT clear debt this session — defer to Session 4 (`debt-clearance` type).
13. Count total prompt-affecting atoms across ALL batches (F + G + SC). This informs Session 5's prompt refactor.

HANDOFF: Write Session 4 kickoff per §7.2. Session 4 type = `debt-clearance`. Session 5 type = `prompt-architecture` (§4.11 refactor gate). Session 6+ type = `full-atom` (3-5 Full Lane or 5-8 mixed atoms per session).

**Deferred work (NOT Session 3 — future full-atom sessions):**
- Formalize SPEC §6 entries for ~30 SPEC-only atoms from Batches 4-6
- Route to SPEC: FP-13 genre-sensitivity (SCH-009/010), Organic Knowledge Unit (PED-001)
- Re-run empirical validation on additional chunks (ibn_aqil_v1 chunk 0, taysir chunks 1-3)
- Build `verify_atom_closure.py` (DA-001) — machine-checkable Q-CLOSED evidence
- Fix remaining 4 xfail red-team gaps (ZWSP, damma truncation, segment contiguity, boundary ordering)
- Prepare Phase 1 smoke run with fully hardened prompt

**Pre-existing test failure:** `test_phase2_integration.py::test_classify_and_normalize` fails with 401 (expired OpenRouter API key). Not related to hardening changes. Confirmed pre-existing on clean master.

---

### Phase 0 Status: QUESTIONNAIRE FOUNDATIONS COMPLETE, DEEP DIVES PENDING

The owner completed F1-F8 (Foundations phase). Phases 2-4 (30 remaining interactions) are deferred until foundations hardening is complete. CC does NOT wait idly. Concurrent work continues below.

**Questionnaire artifacts (all at `integration_tests/questionnaire/`):**

| File | Purpose | Owner sees? |
|------|---------|-------------|
| `OWNER_QUESTIONNAIRE.md` | The actual questionnaire (owner fills this) | YES |
| `RESPONSE_FORMAT.md` | Response template for each interaction | YES |
| `QUESTIONNAIRE_EXAMPLES.md` | Real excerpt examples for each interaction | YES |
| `QUESTIONNAIRE_TEMPLATE.md` | Master template (coworker-designed) | NO |
| `TEAM_TRANSLATION_GUIDE.md` | Maps answers to SPEC rules + prompt params | NO |
| `CRITICAL_EVALUATION_GUIDE.md` | 6-coworker evaluation protocol | NO |
| `excerpt_selections.json` | Machine-readable excerpt selection index | NO |

**CJ-2 / CJ-3 placeholders:** These interactions require before/after comparisons between campaign (old prompts) and v2 (hardened prompts) excerpts for the same passage. CC fills these automatically when the taysir v2 package completes -- no owner action needed. The owner will see rendered Arabic text, not JSON.

**When owner finishes the questionnaire:**
1. CC dispatches the 6-coworker critical evaluation (see `CRITICAL_EVALUATION_GUIDE.md`)
2. CC synthesizes all coworker findings into a unified assessment
3. CC presents challenges back to the owner ONLY for genuine contradictions or infeasible preferences
4. CC documents confirmed answers and proceeds to Phase 0 exit

**Phase 0 EXIT CONDITION:**
- [ ] All 6 coworker evaluations received (or N-1 after 48h timeout per coworker)
- [ ] All identified contradictions resolved with owner or resolved by priority ranking (S-1)
- [ ] Confirmed answers documented in a `PHASE_0_CONFIRMED.md` file
- [ ] SPEC amendments drafted per `TEAM_TRANSLATION_GUIDE.md` (CC writes, no owner review needed)
- [ ] Prompt calibration changes identified (CC writes, filed as code changes)
- [ ] V2 data cross-referenced with confirmed answers (owner-principle test, use #3 below)

---

## V2 Run Status & Data Usage

### Package Status

| Package | Status | Excerpts | Errors | Cost | Time |
|---------|--------|----------|--------|------|------|
| ibn_aqil_v1 | COMPLETE | 241 | 3 (2x EX-V-002, 2 chunk failures) | $4.40 | 44 min |
| ibn_aqil_v3 | COMPLETE | 278 | 6 (5x EX-V-002, 1 chunk failure) | $4.30 | 45 min |
| taysir | IN PROGRESS | pending | 0 so far | pending | ongoing |

**Taysir status check:** 509 progress entries (504 done, 0 errors). Phase 2a: 180 classifications. Phase 2b: 179 groupings. Phase 3 enrichment: 145 done. No `excerpts.jsonl` or `SUMMARY.json` yet -- run is still in pipeline. Check `integration_tests/smoke_api_v2/taysir/progress.jsonl` for live status.

**When taysir completes:** CC automatically updates SUMMARY.json, fills CJ-2/CJ-3 placeholders, and logs the completion.

**Output location:** `integration_tests/smoke_api_v2/` -- NEVER overwrite or delete this directory.

### Chunk-Limit Investigation

The v2 run processed ALL taysir chunks (184) instead of the intended 2 per package. This was unintentional but produces more valuable data. The cost discrepancy (~$55 total vs estimated ~$6) is because of this full-book behavior. **Before the next run:** investigate and fix the chunk-limit logic in `scripts/run_full_integration.py`. The `--max-chunks` flag must be verified to actually limit processing.

### V2 Data Usage Plan (7 uses -- every dollar counts)

1. **CJ-2 questionnaire interaction** -- Before/after comparison for the owner (same passage, old vs new prompts). CC renders as readable Arabic text.
2. **Phase 1 six-team analysis** -- All 6 analysis teams evaluate v2 output quality against SPEC and owner answers.
3. **Owner-principle test** -- After questionnaire, run every v2 excerpt through the owner's stated principles as pass/fail. Automated where possible, manual spot-check for judgment calls.
4. **Before/after regression** -- Campaign (2,303 excerpts, Opus, old prompts) vs v2 (GPT-5.4, hardened prompts). Measure every improvement and regression quantitatively.
5. **Edge case mining** -- 520+ raw LLM responses reveal model reasoning at boundaries. Diagnostic gold for prompt calibration.
6. **Training data** -- Raw outputs + structured excerpts + eventual owner evaluation labels (per Rule 13 in principles.md).
7. **Prompt calibration baseline** -- V2 becomes the BEFORE for the next iteration after questionnaire-driven prompt changes.

**Data preservation rules:**
- NEVER delete raw LLM responses (`raw_llm_requests/`, `raw_llm_responses/`)
- NEVER overwrite `excerpts.jsonl` -- copy to a dated backup before any re-run
- NEVER modify `SUMMARY.json` after it is written -- append corrections as `SUMMARY_patch_YYYYMMDD.json`
- All 6-team analysis outputs go in `integration_tests/smoke_api_v2/analysis/` (new directory, created by CC)

---

## Phase 0 --> Phase 1 Transition Checklist

**Owner: CC (all items). No owner approval gate.**

| # | Check | Owner | Status |
|---|-------|-------|--------|
| 1 | Owner questionnaire responses complete (all 40 interactions answered) | CC verifies | PENDING |
| 2 | 6-coworker critical evaluation complete (all 6, or N-1 with 48h timeout) | CC dispatches | PENDING |
| 3 | All contradictions resolved (either by owner clarification or S-1 priority ranking) | CC decides | PENDING |
| 4 | SPEC amendments written per `TEAM_TRANSLATION_GUIDE.md` column mapping | CC writes | PENDING |
| 5 | Prompt calibration changes applied to `engines/excerpting/prompts/` | CC writes | PENDING |
| 6 | V2 data fully available (all 3 packages complete, SUMMARY.json finalized) | CC checks | PENDING |
| 7 | Chunk-limit bug investigated and fixed in `scripts/run_full_integration.py` | CC fixes | PENDING |
| 8 | CJ-2/CJ-3 placeholders filled with rendered before/after comparisons | CC fills | PENDING |
| 9 | `PHASE_0_CONFIRMED.md` written with all confirmed answers + traceability | CC writes | PENDING |
| 10 | CC self-verifies all 9 items above -- NO owner sign-off needed | CC | PENDING |

**Transition rule:** When all items are DONE, CC proceeds to Phase 1 immediately. No waiting for owner permission.

---

## Phase 1: Smoke Analysis (CC orchestrates everything)

### Purpose

Analyze the v2 smoke data using exhaustive multi-team review + owner spot-check. This produces a complete quality assessment that drives Phase 2 hardening priorities.

### Step 1: CC Spawns 5 Analysis Subagents (parallel)

| Team | Agents | Focus | Input Files | Output |
|------|--------|-------|-------------|--------|
| A: Boundary Quality | CC + Codex CLI | Every boundary checked against SPEC §4.A-B | `excerpts.jsonl` (all 3 pkgs) | `TEAM_A_BOUNDARY.md` |
| B: Classification | Gemini CLI + ChatGPT DR | Every `primary_function` verified against domain glossary | `excerpts.jsonl` + `phase2a_classifications/` | `TEAM_B_CLASSIFICATION.md` |
| C: Arabic Fidelity | Claude DR + Gemini CLI | Diacritics, honorifics, isnad integrity, text corruption | `excerpts.jsonl` + raw source text | `TEAM_C_ARABIC.md` |
| D: Consensus & Metadata | Codex CLI + CC | author_id, school, evidence_refs, D-023 pass-through | `excerpts.jsonl` + `cache/` dirs | `TEAM_D_METADATA.md` |
| E: Coverage & Gaps | ChatGPT DR + Claude DR | Missing excerpts, over/under-extraction, coverage ratio | `excerpts.jsonl` + `phase1_chunks.json` | `TEAM_E_COVERAGE.md` |

All outputs go to `integration_tests/smoke_api_v2/analysis/`.

### Step 2: CC Dispatches 3 DR Coworkers (parallel with Step 1)

| Coworker | Access Method | What CC Provides | Timeout |
|----------|---------------|------------------|---------|
| ChatGPT DR | Relay prompt to owner | File contents pasted into prompt (self-contained). Include: 10 representative excerpts, SPEC §4 relevant sections, specific questions about error patterns and architecture. | 48h |
| Claude DR | Relay prompt to owner | File contents pasted into prompt (self-contained). Include: 10 boundary edge cases, SPEC §4.A self-containment rules, specific questions about scholarly reasoning and boundary quality. | 48h |
| Gemini DR | Relay prompt to owner | File uploads (excerpts.jsonl, SPEC.md). Include: 5 excerpts per genre, specific questions about Islamic study methodology and genre-specific natural units. | 48h |

**DR prompt construction:** Every relay prompt must be fully self-contained -- the DR session cannot access the repo. Paste all necessary file contents, excerpt text, and context directly into the prompt. Follow templates in `.claude/skills/coworker-dispatch/SKILL.md`.

**DR timeout protocol:** If a DR coworker does not return within 48h, CC proceeds with N-1 results and documents the gap in `PHASE_1_REPORT.md`. Minimum required: 3 out of 5 teams + 1 out of 3 DR coworkers.

### Step 3: CC Selects 20 Excerpts for Owner Review

CC selects and renders as readable Arabic text (NOT JSON):
- 10 best excerpts (highest confidence, cleanest boundaries, diverse genres)
- 10 worst excerpts (lowest confidence, boundary issues, classification uncertainty)

**Owner is asked ONLY:** "For each excerpt: good / bad / confusing? If bad or confusing, what bothered you?"

The owner does NOT review SPEC compliance, metadata accuracy, or technical details. CC translates any owner reactions into technical actions.

### Step 4: Synthesis

CC collects all team reports, DR results, and owner spot-check feedback. Produces:

**Output:** `integration_tests/smoke_api_v2/analysis/PHASE_1_REPORT.md` containing:
- Per-team findings (confirmed = 2+ teams agree, disputed = disagreement, novel = single team)
- Owner reaction summary (translated to technical actions)
- Prioritized issue list (CRITICAL / HIGH / MEDIUM / LOW)
- Recommended Phase 2 actions

### Phase 1 EXIT CONDITION

- [ ] At least 4 out of 6 teams (5 analysis + owner) confirm acceptable quality, OR
- [ ] Owner accepts excerpts from at least 2 packages in the spot-check
- [ ] All CRITICAL issues documented with proposed fixes
- [ ] `PHASE_1_REPORT.md` complete and committed
- [ ] Phase 2 action plan written with estimated cost

---

## Phase 2: Deep Hardening (CC decides priorities)

### Purpose

Fix everything found in Phase 1. Iterate until convergence. CC drives all decisions -- coworkers validate, owner is only asked about experience.

### Hardening Steps

| Step | What | Owner | Depends On |
|------|------|-------|------------|
| 2a | Fix prompt calibration (temperature, few-shots, instructions) | CC | Phase 1 findings |
| 2b | Fix grouping/boundary logic (Phase 2b prompt, grouping criteria) | CC | Phase 1 Team A report |
| 2c | Fix enrichment/metadata (Phase 3 prompt, field extraction) | CC | Phase 1 Team D report |
| 2d | Re-run 2 packages with fixes (~$6, CC launches) | CC | 2a + 2b + 2c complete |
| 2e | Re-evaluate with 3 CC subagents (boundary + classification + metadata) | CC | 2d output available |
| 2f | Compare Phase 1 baseline vs 2d results (quantitative regression check) | CC | 2d + 2e complete |

### Iteration Protocol

**CONVERGENCE CRITERIA:**
- At least 80% of Phase 1 issues resolved in 2d results
- Zero CRITICAL-severity issues remaining
- Owner accepts 10 re-rendered excerpts from 2d (good/bad/confusing only)
- No regression: 2d results are strictly better than Phase 1 on measured dimensions

**MAX 3 ITERATIONS.** If after 3 cycles of 2a-2f the convergence criteria are not met:
- CC documents all remaining known issues in `KNOWN_LIMITATIONS.md`
- CC classifies each as: will-fix-in-taxonomy, will-fix-in-synthesis, accept-as-is, or needs-SPEC-change
- CC proceeds to Phase 3 with documented limitations
- Owner is informed of the limitations in non-technical terms ("some long scholarly debates may not be split perfectly")

**Decision authority:** CC decides priorities, fix order, and when to stop iterating. Coworkers validate fixes. Owner is only asked "does this excerpt look good to you?"

### Phase 2 EXIT CONDITION

- [ ] Convergence criteria met, OR max 3 iterations exhausted with documented limitations
- [ ] All code changes committed with tests
- [ ] `PHASE_2_REPORT.md` written (changes made, issues resolved, issues remaining)
- [ ] Prompts in `engines/excerpting/prompts/` updated and committed
- [ ] SPEC amendments (if any) committed
- [ ] Cost log updated in `COST_LOG.json`

---

## Phase 3: Full 5-Book Run

### Purpose

The definitive run with fully hardened prompts. Produces the output that will be used for taxonomy engine input.

### Command

```bash
python scripts/run_full_integration.py \
  --backend api \
  --max-chunks 2 \
  --output-dir integration_tests/v2_final/
```

**CRITICAL:** Verify `--max-chunks` actually limits processing BEFORE running. The v2 run ignored this flag (see chunk-limit investigation above). Test with a single package first.

**Output directory:** `integration_tests/v2_final/` -- NEVER overwrite v2 data at `integration_tests/smoke_api_v2/`.

**Estimated cost:** ~$15-25 depending on chunk count and model pricing.

### Post-Run Evaluation

1. CC runs automated comparison: v2_final vs campaign baseline (2,303 excerpts, old prompts, Opus)
2. CC runs automated comparison: v2_final vs v2 smoke (hardened prompts, pre-questionnaire)
3. All 6 teams re-evaluate v2_final output (same protocol as Phase 1, Step 1)
4. Owner reviews 10 rendered excerpts (good/bad/confusing)

### Phase 3 EXIT CONDITION

- [ ] All 5 packages complete with no CRITICAL errors
- [ ] At least 4/6 teams confirm output quality meets or exceeds Phase 2 results
- [ ] Owner accepts excerpts from at least 3 packages
- [ ] No regressions vs Phase 2 on any measured dimension
- [ ] `PHASE_3_REPORT.md` written
- [ ] All data preserved (raw responses, excerpts, cache, timing)
- [ ] Excerpting engine declared EVALUATION COMPLETE -- ready for taxonomy engine input

---

## Error Handling Protocol

### Coworker Unavailable

| Scenario | Action |
|----------|--------|
| Codex CLI down | Log in `.kr/runtime/dispatch_log.jsonl`. Reassign structural checks to CC. Proceed. |
| Gemini CLI down | Log. Reassign Arabic checks to Claude DR (relay prompt). Proceed. |
| DR coworker (any) does not return within 48h | Log. Proceed with N-1 results. Document gap. |
| Fewer than 3 coworkers available | STOP. Report to owner: "Cannot proceed -- only N coworkers available, minimum 3 required." |

### Owner Unresponsive

| Scenario | Wait | Then |
|----------|------|------|
| Questionnaire not started after delivery | 48h | CC sends a reminder with an estimated time commitment. |
| Questionnaire in progress but stalled | 72h since last answer | CC sends progress check: "You've completed X/40 interactions. Take your time -- no rush." |
| Questionnaire complete but challenges unanswered | 72h | CC proceeds using S-1 priority ranking + coworker-confirmed resolution. Documents decision. |
| Owner spot-check (Phase 1/2/3) not returned | 48h | CC proceeds with coworker-only evaluation. Notes "owner review pending" in report. |

**Principle:** CC never blocks on owner input for more than 72h. After 72h, CC uses the best available information and proceeds with documented reasoning.

### Run Failures

| Scenario | Action |
|----------|--------|
| API timeout during run | Automatic retry with exponential backoff (2s, 4s, 8s, max 3 retries). Log to ERROR_LOG.json. |
| Run stall (no progress.jsonl update for 1h) | Kill the process. Resume from last checkpoint using `--resume` flag. |
| Partial completion (some packages succeed, some fail) | Preserve ALL successful results immediately. Investigate failures. Re-run only failed packages. |
| Invalid output (malformed JSON, schema violations) | Do NOT discard. Quarantine to `quarantine/` subdirectory. Investigate root cause before re-run. |

### Budget Exceeded

| Scenario | Action |
|----------|--------|
| Single run would exceed remaining budget | STOP. Report: "This run costs ~$X, remaining budget is $Y. Approve?" Wait for owner. |
| Cumulative spend exceeds `KR_BUDGET_LIMIT` | STOP all API runs immediately. Report full cost breakdown. Do not retry. |
| Unexpected cost spike (>2x estimated) | Pause after current package. Investigate cause (chunk-limit bug? model pricing change?). Report. |

### Coworker Disagreement

When 2+ coworkers disagree on a content quality judgment:
1. CC examines the specific excerpt/issue both coworkers assessed
2. CC applies SPEC rules as the tiebreaker where possible
3. If SPEC is ambiguous, CC makes the decision and documents reasoning
4. The decision is marked as `[CC-DECIDED: rationale]` in the report
5. Disputed items are flagged for owner spot-check in the next review cycle

---

## Budget

| Category | Spent | Remaining | Notes |
|----------|-------|-----------|-------|
| Source engine (Cohere + Opus) | EUR 36.70 | EUR 63.30 / EUR 100 | Complete. No further spend. |
| OpenRouter v2 smoke | ~$8.70 (2 pkgs) | ~EUR 45 of dev budget | taysir still running, will add ~$40 |
| Phase 2 smoke (2 pkg re-run) | -- | ~$6 per re-run | Budget for 3 iterations = ~$18 |
| Phase 3 full 5-book | -- | ~$15-25 | One run. No re-runs budgeted. |
| **Total excerpting budget** | **~$55** | **~EUR 45 remaining** | Enough for Phase 2 (3x) + Phase 3 |

**Cost tracking:** Every API-calling script logs to `COST_LOG.json`. The `cost-guard.sh` hook enforces `KR_BUDGET_LIMIT`. CC checks budget before every run.

---

## Current Engine State

### What's Implemented (917 tests pass)

- 8 Tier-1 prompt fixes (H-1 through H-8): few-shots, schema split, copy fidelity
- 3 Claude DR fixes: narrator role, al-ma'na al-ijmali classification, fawa'id grouping
- DR-1 (definition pair splitting): in Phase 2b prompt
- DR-3 (khilaf preservation): in Phase 2b prompt
- CrossReference extension: target_excerpt_id + relationship_type
- DR-1 companion detection: deterministic post-enrichment linking
- Evidence resolution hints: canonical surah/ayah in cross-references
- Bug fixes: consensus resolution, ZWNJ, LA-3 threshold, model defaults

### What's Deferred

- DR-2 (evidence-type splitting): 3/5 reviewers rejected. Deferred to taxonomy pilot.
- Multi-leaf taxonomy tagging: requires VISION 1.2 amendment. Deferred.
- Taxonomy engine: being built in parallel. Nahw tree nearly final. Trees NOT trustworthy yet.

---

## Key Decisions (6-reviewer cross-validated)

| Decision | Rationale | Score |
|----------|-----------|-------|
| GPT-5.4 primary | 3x cheaper, contract-stable, errors are prompt-fixable | 3/5 |
| DR-1 ADOPT (conditional) | Definition pairs are separate topics; self-containment gate | 4/5 |
| DR-2 DEFER | Puzzle excerpt risk; VISION 1.2 tension unresolved | 3/5 reject |
| DR-3 ADOPT (structural) | Khilaf = highest decontextualization risk | 5/5 |

---

## Model Configuration

| Role | Model | Use |
|------|-------|-----|
| Primary (classify + group + enrich) | openai/gpt-5.4 | All excerpting pipeline calls |
| Verify | anthropic/claude-opus-4.6 | Consensus verification where required |
| Escalation | mistralai/mistral-large-2411 | Tiebreaker on disagreements |

---

## Research Artifacts (DO NOT DELETE)

### Diagnostic Reports (moved to reference/ and docs/)

- `reference/BOUNDARY_CONVENTION_DIAGNOSTIC.md` -- Claude DR boundary analysis (133 excerpts)
- `docs/coworker_reports/2026-03-31_adversarial_reviews/chatgpt-report-diagnostic-analysis.md` -- ChatGPT error patterns
- `docs/coworker_reports/2026-03-31_adversarial_reviews/chatgpt-deep-research-opus_vs_gpt.md` -- Opus vs GPT-5.4 model comparison
- `chatgpt-deep-research-granuality-synthesis.md` -- Synthesis engine granularity analysis
- `chatgpt-Adversarial Review of DR-1, DR-2, DR-3.md` -- DR adversarial review

### Campaign Analysis (`integration_tests/campaign_20260331/analysis/`)

19 files: excerpt_catalog.jsonl (2,303 indexed), gold_candidates.jsonl (100), taxonomy_readiness_flags.jsonl (54 flags), arabic_fidelity_flags.jsonl (382 flags), taysir_scholarly_review.md (68-excerpt deep review), convention_compliance_report.md (7 checks), scholarly_reality_check_intra_excerpt.md, gemini_adversarial_DR_review.md, plus catalogs and summaries.

### Owner Feedback

- `integration_tests/campaign_20260331/taysir/owner_feedback.jsonl` -- 2 reviews that triggered the granularity debate

---

## Your Team -- USE ALL AT EVERY MILESTONE

| Agent | Access | Use For | Access Notes |
|-------|--------|---------|--------------|
| **Codex CLI** | `codex exec` (direct repo access) | Schema validation, cross-prompt consistency, stats | Can read/write repo files directly. Best for deterministic checks. |
| **Gemini CLI** | `gemini -p` (direct repo access), Gemini 3.1 Pro | Arabic scholarly accuracy, convention compliance | Can read repo files directly. Major coworker for Arabic. |
| **ChatGPT DR** | Deep Research (relay prompt to owner) | Error patterns, architectural analysis, Q&A design | NO repo access in DR mode. Paste all file contents into prompt. Owner relays. |
| **Claude DR** | Deep Research (relay prompt to owner) | Scholarly reasoning, boundary quality, edge cases | NO repo access in DR mode. Paste all file contents into prompt. Owner relays. |
| **Gemini DR** | Deep Research (relay prompt to owner) | Islamic study methodology, scholarly pedagogy | NO repo access in DR mode. Upload files where possible. Owner relays. |

**Dispatch protocol:** See `.claude/skills/coworker-dispatch/SKILL.md` for per-coworker prompt templates.
**Dispatch log:** Every dispatch recorded in `.kr/runtime/dispatch_log.jsonl`.
**Minimum for any milestone:** 3 out of 5 coworkers must evaluate. 5 out of 5 is the target.
