# Protocol v5.0 Plan — Batch Lifecycle & Verification

**Status:** ALL 6 DRs PROCESSED — READY FOR IMPLEMENTATION.
**Source:** DR12 (ChatGPT), DR13 (Gemini), DR14 (Claude), DR15 (Gemini), DR16 (ChatGPT), DR17 (Claude, scholarly methodology)
**Created:** 2026-04-06
**Target:** Amend HARDENING_SESSION_PROTOCOL.md v4.3 → v5.0

---

## Problem Statement

Session 1 silently dropped 124 owner feedback atoms — entire files (F1/F2) never read, ALL-CAPS
urgency systematically stripped, structured analysis notes missed. The per-atom lifecycle (v4.0-v4.3)
prevents per-atom errors but does NOT prevent batch-level omissions. v5.0 adds the Batch Lifecycle
Protocol: a structural guarantee that every word of owner feedback is captured, verified, and traced
from raw .txt source to implemented doctrine.

## Architecture Decision

**Serial Muqabalah (DR15 Architecture D)** — NOT parallel independent extraction.
Primary agent extracts using strict checklist; secondary agent (muhaddiq) performs collation
against the original hunting for gaps left by the first agent. This matches the classical
muqabala bi-l-asl (side-by-side collation against the author's original), which is the gold
standard for written texts.

---

## Synthesized Requirements (52 units from 6 DR reports)

### TIER 1 — Structural Amendments to Protocol (18 units)

These modify §-sections of the protocol itself.

| ID | Requirement | Source | Target §  | Priority |
|----|-------------|--------|-----------|----------|
| R-01 | **Batch Lifecycle: 6-phase model** — Intake (Mutala'ah) → Extraction (Fahm) → Adversarial Challenge (Mudhakarah) → Exhaustive Verification (Muraja'ah) → Owner Briefing (Reverse 'Ard) → Batch Finalization (Ijazah). Each phase prevents a distinct anti-pattern. | DR13 | NEW §3A | CRITICAL |
| R-02 | **Session type: `verification-only` (single-purpose)** — Batch Completeness Verification session. Forbidden to combine with intake, full-atom, or prompt-architecture. Positioned in gate-precedence matrix AFTER bundle intake, BEFORE prompt refactor gate. | DR12 | §1.5, §1.6 | CRITICAL |
| R-03 | **Batch Completion Gate** — 5 pass conditions: (1) 100% file coverage, (2) MCU mapping completeness, (3) zero MISSED at CRITICAL/HIGH, (4) queue terminality, (5) script attestation. Batch status is DERIVED (from script output), not DECLARED. | DR12, DR14 | NEW §3B | CRITICAL |
| R-04 | **MCU definition** — Minimum Content Unit = smallest span expressing directive, definition, risk, rule-example, severity signal, or meta-instruction. Requires (start_line, end_line, verbatim_anchor). Verbatim anchor minimum: 15+ chars of exact source text. | DR12, DR14 | NEW §3A.2 | CRITICAL |
| R-05 | **MCU classification system** — MISSED (no MAQ/META/REJECT mapping), SOFTENED (direction preserved but urgency reduced), DISTORTED (meaning changed), SKIPPED-FILE (structural gate-fail). SOFTENED at CRITICAL/HIGH cannot close without strength restoration or owner ack. | DR12, DR14 | NEW §3A.3 | CRITICAL |
| R-06 | **Bifurcated verification standard** — F1/F2: Hafiz standard (verbatim, per-sentence, 100% review). F3-F8: Faqih standard (per-concept, 15% random sample + all flagged items). Different file types demand different rigor levels. | DR13, DR14, DR15 | NEW §3A.4 | CRITICAL |
| R-07 | **ALL-CAPS / emphasis = semantic content** — Stripping ALL-CAPS, exclamation marks, or emphasis markers is nuqsan (omission), not formatting cleanup. Emphasis vocabulary registry must remain distinct. Three priority tiers: Tier 1 = ALL-CAPS/"PLEASE"/emotional markers, Tier 2 = normal directives, Tier 3 = observations/tentative. | DR13, DR14 | §3.2 Step 3 | CRITICAL |
| R-08 | **Absolute Reopen Authority (Haqq al-Istidrак)** — Verification sessions can reopen ANY finalized atom if it violates an F1/F2 foundational directive. Every reopened atom requires formal Istidrак justification citing specific forensic audit gap. | DR15 | §4.6 amend | CRITICAL |
| R-09 | **Anchor-bound expansion** — EXPANDED→DECIDED stages must maintain verbatim source anchors. G-CHALLENGED cannot pass unless at least one challenger audits fidelity: "What in the anchors proves this claim?" Prevents interpretation drift during expansion. | DR16 [Q1]-4 | §4.3 amend | CRITICAL |
| R-10 | **Regression gate** — After ANY prompt/SPEC change, mandatory regression sweep before Q-CLOSED or merge. Re-runs all previously validated atom checks. Silent regression after later prompt changes is not structurally blocked in v4.3. | DR16 [Q1]-2 | NEW §4.18 | CRITICAL |
| R-11 | **Behavior-change evidence for Q-CLOSED** — Atoms cannot reach IMPLEMENTED/Q-CLOSED without empirical confirmation that engine output differs in the intended way. Link to atom_test evidence or waiver with scheduled validation debt. Q-12 strengthened. | DR16 [Q1]-1 | §4.8 amend | CRITICAL |
| R-12 | **Cross-batch doctrine coherence gate** — Rule-level lint pass over SPEC+prompt+doctrine before G-batch hardening + before any SC-batch atom enters DECIDED. Gate fails if two Q-CLOSED atoms assert conflicting constraints on same concept. | DR16 [Q1]-5 | NEW §4.19 | CRITICAL |
| R-13 | **Fan-in threshold for MCU→MAQ mapping** — If single MAQ maps to >5 MCUs OR >1 CRITICAL MCU, verifier must split atom OR add Sub-Claim Table showing 1:1 MCU→clause mapping. Prevents semantic compression loss. | DR16 [Q1]-6 | §3A.5 amend | HIGH |
| R-14 | **Coverage-claim validation** — MCU dispositioned as "ALREADY COVERED" only if: (1) exact FP clause cited, (2) minimal counterexample written, (3) empirical test demonstrates coverage OR new micro-test added. Prevents false "already covered." | DR16 [Q1]-3 | §4.8 amend | HIGH |
| R-15 | **Model-environment equivalence contract** — All empirical validations MUST record (model_provider, model_id, model_version) + (sampling params) + (prompt_hash, spec_hash). Q-CLOSED validation INVALID if contract doesn't match production profile. | DR16 [Q1]-7 | §4.8 amend | HIGH |
| R-16 | **Calibration File (Nuskha Mi'yariyyah)** — Designate one moderately complex file (e.g., F4 segment) as drift detector. Every 5th verification session, agent independently extracts without baseline access. Detects standards degradation across 15-30 session campaign. | DR15 | NEW §8.5 | HIGH |
| R-17 | **Ijazah ceremony with 4 locks + revocation** — Lock 1: cryptographic proof 100% files ingested. Lock 2: zero-softening attestation. Lock 3: coworker consensus signatures. Lock 4: owner approval (Full/Partial). Revocable via Sijill al-Istidrак. Partial certification (Ijazah mu'ayyanah) allowed. | DR13, DR15 | NEW §3C | HIGH |
| R-18 | **Owner briefing: Reverse 'Ard with Tadarruj** — Visual side-by-side (Matn Reflection), question-based inquiry (Tahqiq Clarification), omission confession (Amanah Checklist). 250-word hard limit. No technical identifiers. Color-coded: Green=exact match, Yellow=expansion, Red=flagged ambiguity. | DR13, DR15 | §4.15 amend | HIGH |
| R-19 | **Tashif/Tahrif sub-classification** — Split DISTORTED into: tashif (surface corruption: diacritical/presentation, recoverable by context) vs tahrif (structural corruption: meaning altered, requires re-extraction). Sub-types: tashif al-basar (visual misreading) vs tashif al-sam' (auditory mishearing); location: matn (body) vs isnad (chain) carry different weights. [Gemini-corrected] | DR17 §5 | §3A.3 amend | HIGH |
| R-20 | **Expansion fidelity indicator (او كما قال)** — CC declares fidelity level: `exact` (verbatim), `paraphrased` (او كما قال), `interpreted` (او نحو هذا). Marker travels through all lifecycle stages. **MANDATORY EXACT CONSTRAINTS [Gemini-corrected]:** Devotional formulae (dhikr/du'a), jawami' al-kalim (concise prophetic sayings), and text whose exact wording carries legal weight MUST be exact regardless — the system enforces text-type-based mandatory exact matching, not just declares levels. 5 classical conditions for meaning-based transmission must all hold. | DR17 §1 | §4.3 amend | CRITICAL |
| R-21 | **Istidrak remediation chain** — Every atom reopening creates formal istidrak entry: references prior version by ID, declares gap type (nuqsan/takhfif/tahrif), records evidence, produces corrected version. Chain indexed by generation. | DR17 §3 | §4.6 amend | HIGH |
| R-22 | **Variant preservation for DISPUTED atoms** — Preserve ALL coworker positions with provenance sigla (خ notation). Authority-ordered [Gemini-corrected]: asl (closest to owner's original) is body text, other readings are marginal variants. NOT flat egalitarian — hierarchy mirrors classical tahqiq practice. | DR17 §4 | §5.4 amend | HIGH |
| R-23 | **4-factor threshold matrix** — Extend R-06 with: (1) genre/content type, (2) collator competence, (3) text status (foundational vs supplementary), (4) exemplar availability. Dynamic per-file selection. | DR17 §1 | §3A.4 amend | HIGH |
| R-24 | **Shahadah certificate 9-field anatomy** — Extend R-17: (1) completion statement, (2) exemplar description, (3) collator identity, (4) method statement, (5) date, (6) completeness with honest limitation, (7) variant notation key, (8) exemplar pagination, (9) integrity closing. | DR17 §2 | §3C amend | HIGH |
| R-25 | **Lahn severity framework** — Fatal lahn (changes ruling → HALT) vs tolerable lahn (→ LOG+CONTINUE). **Science-specific [Gemini-corrected]:** "tolerable = cosmetic" applies to hadith fada'il/fiqh implementation details ONLY. In Qira'at/Tajwid: no cosmetic errors (jali = fatal invalidating prayer, khafi = hidden but graded). In Nahw: single vowel change destroys structural purpose. In Aqidah: doctrinal sensitivity means almost all errors are fatal. Framework MUST be science-aware. Habitual tolerable lahn → flag dabt deficiency → recalibration (R-16). | DR17 §1 | NEW §3A.6 | HIGH |
| R-26 | **Role separation formalization** — Map 5 classical roles: Musammi'=CC (ACTIVE: real-time correction + ijazah granting, not passive [Gemini-corrected]), Qari'=extraction agent, Mustami'un=coworker reviewers (with veto), Muqabil=verification agent, Katib=script artifacts. No role combination allowed. | DR17 §4 | §5 amend | MEDIUM |

### TIER 2 — New Scripts (8 units)

| ID | Script | Purpose | Source | Priority |
|----|--------|---------|--------|----------|
| S-01 | `scripts/batch_inventory.py` | Hash-bound file inventory with SHA-256 per file. Manifest-derived vs filesystem-derived inventory; mismatch blocks gate. | DR12 | CRITICAL |
| S-02 | `scripts/batch_verification_init.py` | Initialize verification session: create inventory.json, verification_status.json (per-file states: UNVERIFIED→IN_PROGRESS→VERIFIED→DRIFTED). | DR12 | CRITICAL |
| S-03 | `scripts/batch_compute_coverage.py` | Compute MCU mapping completeness. Denominator = inventory files + total MCUs. Reports MISSED/SOFTENED/DISTORTED/SKIPPED-FILE counts. | DR12 | CRITICAL |
| S-04 | `scripts/batch_generate_trace_report.py` | Generate verification_report.md + delta_queue_patch.md. Stratified sampling for adversarial review. | DR12 | CRITICAL |
| S-05 | `scripts/verify_batch_completion_gate.py` | 5-condition gate check. Exit 0 on pass, 1 on fail. Cannot pass if: any DRIFTED files, unresolved gaps, Layer A unverified. | DR12 | CRITICAL |
| S-06 | `scripts/run_regression_suite.py` | Re-execute all previously validated atom checks after prompt/SPEC change. Reads validation/, fixtures, prompt hashes. Output: regression_runs/<run_id>/. | DR16 [Q2]-2 | CRITICAL |
| S-07 | `scripts/prompt_coherence_lint.py` | Static analysis for prompt internal coherence: duplicate clauses, conflicting quantifiers, unreachable conditions, token budget by section. | DR16 [Q2]-3 | HIGH |
| S-08 | `scripts/atom_impact_diff.py` | Compute with/without-atom behavior delta. Feature-flag atom's prompt/SPEC contribution, compare outputs. Mandatory for prompt-affecting Q-CLOSED. | DR16 [Q2]-4 | HIGH |

### TIER 3 — Anti-Pattern Tests (8 units, from DR15)

| ID | Test | What It Detects | Automation Level |
|----|------|-----------------|-----------------|
| T-01 | Total Ingestion Validation | File hash vs atom database mismatch | Full (cryptographic) |
| T-02 | Semantic Density Check | Technical terms to contextual explanations ratio too low | Semi (heuristic) |
| T-03 | Unstructured Text Ratio | Byte-coverage mapping <80% for narrative text | Full (script) |
| T-04 | Absolute Retention Scanner | ALL-CAPS, absolute modifiers not in atoms | Full (regex + verify) |
| T-05 | Gate Integrity Enforcement | State transition with unresolved gaps >0 | Full (script gate) |
| T-06 | Source Grounding Traceability | Atom missing byte_range_start/end mapping | Full (schema check) |
| T-07 | Briefing Load Limit | Owner briefing >250 words or contains MAQ-IDs | Full (lint) |
| T-08 | Cross-Batch Continuity | F3-F8 rule contradicts F1 meta-directive | Hybrid (LLM + owner) |

### TIER 4 — Artifact Specifications (6 units)

| ID | Artifact | Schema | Source |
|----|----------|--------|--------|
| A-01 | `inventory.json` | {files: [{path, sha256, size_bytes, line_count, layer}], batch_id, created_at} | DR12 |
| A-02 | `verification_status.json` | {files: [{path, state: UNVERIFIED|IN_PROGRESS|VERIFIED|DRIFTED, mcu_count, verifier, timestamp}], batch_verification_run_id} | DR12 |
| A-03 | `mcu_trace.jsonl` | Per-line: {mcu_id, file_path, start_line, end_line, verbatim_anchor, classification: MISSED|SOFTENED|DISTORTED|MAPPED, maq_id?, severity, confidence} | DR12, DR14 |
| A-04 | `coverage.json` | {total_files, verified_files, total_mcus, mapped_mcus, missed_count, softened_count, distorted_count, coverage_pct} | DR12 |
| A-05 | `verification_report.md` | Human-readable summary of verification session: coverage table, gap inventory, adversarial sample results, recommendations | DR12 |
| A-06 | `gap_remediation_tracker.jsonl` | Per-line: {asl_ref: {file, line, text}, state: 1|2|3, atom_id?, spec_section?, date_changed, responsible} — tracks Asl-only → Established → Implemented | DR14 |
| A-07 | `collation_register.jsonl` | Per-line: {file_path, mcu_id, collation_mode: lafzi|ma'nawi, finding: sahh|saqt|ziyada|tashif|tahrif, correction?, checkpoint_position, session_id} — the Sijill al-Muqabalah | DR17 |

### TIER 4B — Fixture Strategy (4 units, from DR16)

| ID | Requirement | Priority |
|----|-------------|----------|
| F-01 | Designate `taysir` as canonical regression fixture. Every prompt-affecting atom MUST have at least one canonical regression run. | CRITICAL |
| F-02 | Category-matched fixture mapping: boundary→ibn_aqil_v3, nahw→ibn_aqil_v3, fiqh→ext_39_masala, Q&A→ext_46_qa, tarjih→taysir+ext_39_masala. | HIGH |
| F-03 | Add ENT family fixture (hadith collection: Riyad al-Salihin or Taqrib al-Tahdhib). | HIGH (debt) |
| F-04 | Add SEQ family fixture (tasawwuf: al-Risala al-Qushayriyya). | HIGH (debt) |

---

## Hard Rules for v5.0 (new additions)

HR-13: Never begin per-atom processing on a batch until BCV (Batch Completeness Verification) session complete and Batch Completion Gate passes.
HR-14: Never mark a file VERIFIED without MCU trace records containing verbatim anchors + line ranges.
HR-15: Never verify Layer B without first verifying Layer A.
HR-16: Never strip ALL-CAPS, exclamation marks, or emphasis markers from owner text — they are semantic content.
HR-17: Never self-audit — the session that performed extraction cannot perform verification.
HR-18: Never post-edit queue after verification without rolling back file status to DRIFTED.
HR-19: Never disposition MCU as "ALREADY COVERED" without citing exact FP clause + counterexample.
HR-20: Never close Q-CLOSED for prompt-affecting atom without behavior-change evidence.
HR-21: Never merge prompt changes without regression suite passing.
HR-22: Never combine extraction and verification roles in the same session/agent — the extractor cannot be the verifier (DR17 role separation).

---

## Implementation Sequence

```
Phase 1 (Protocol Text):  R-01 through R-18 — Amend HARDENING_SESSION_PROTOCOL.md
Phase 2 (Scripts):         S-01 through S-08 — Build and test all 8 scripts
Phase 3 (Anti-Patterns):   T-01 through T-08 — Integrate into CI/validation
Phase 4 (Artifacts):       A-01 through A-06 — Define schemas, create templates
Phase 5 (Fixtures):        F-01 through F-04 — Fixture strategy + debt tracking
Phase 6 (Verification):    Version bump, cross-checks, NEXT.md update, commit+push
```

Phase 1 is the critical path. Phases 2-5 can partially overlap. Phase 6 is the gate.

---

## DR17 Integration — COMPLETE

**STATUS: INTEGRATED** — DR17 (Claude DR, "Classical Islamic manuscript verification: a complete technical reference") fully analyzed 2026-04-06.
**Archive:** `engines/excerpting/reference/dr_reviews/DR17_claude_manuscript_verification_scholarly.md`

DR17 validated 11 existing requirements with 1000-year scholarly precedent and added 8 new requirements (R-19 through R-26) + 1 artifact (A-07) + 1 hard rule (HR-22). Total plan: **52 implementation units** (up from 44).

Key additions: R-20 (expansion fidelity indicator / او كما قال — CRITICAL), R-19 (tashif/tahrif sub-classification), R-21 (istidrak remediation chain), R-25 (lahn severity framework).

Full analysis: `.claude/plans/replicated-drifting-candle.md` (Part 1).

---

## Coworker Validation Plan

After protocol amendment (Phase 1), before committing:
1. **Codex CLI**: Structural consistency, gate logic, script specs
2. **Gemini CLI**: Scholarly grounding, Arabic convention compliance
3. (Optional) DR dispatch for final v5.0 review if time/budget permits

---

## Success Criteria

- [ ] check_protocol_version.py says v5.0
- [ ] check_prompt_spec_sync.py passes
- [ ] verify_atom_closure_minimal.py passes
- [ ] All 8 scripts exist and are syntactically valid
- [ ] All tests pass (915+)
- [ ] NEXT.md updated with v5.0 status
- [ ] Changes committed and pushed to remote branch
- [ ] DR17 findings integrated (or explicitly waived by owner)
