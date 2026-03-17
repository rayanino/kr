# NEXT — Probe 2: Build Team on Normalization Engine

## Current position: Probe 1 COMPLETE (31 defects found, 22 fixed, CONDITIONAL PASS) → Build
## What to do: Build the normalization engine from the audited SPEC
## Context: SPEC audited by dual audit (reference/PROBE_1_RESULTS.md). 3 MUST-FIX items
  remain (all contract alignment — resolve in Session 1). 279 source engine results available
  as real input data. This probe tests the Build team agents AND produces the normalization engine.
## Owner action needed: NO — this is a Claude Code task.

---

## Read First (in this order)

1. `reference/AGENT_ARCHITECTURE.md` §2.2 — the Build team (3 subagents + main)
2. `reference/ENGINE_BUILD_BLUEPRINT.md` §Step 2 — the proven build methodology
3. `reference/PROBE_1_RESULTS.md` — what was found and fixed in the SPEC
4. `reference/SPEC_INTEGRITY_AUDIT_NORMALIZATION.md` — the 3 MUST-FIX items
5. `engines/normalization/SPEC.md` — the audited SPEC (2,047 lines, governing authority)
6. `engines/normalization/contracts.py` — current Pydantic schemas (698 lines)
7. `engines/normalization/CLAUDE.md` — engine orientation
8. `engines/normalization/src/` — existing stubs (9 files, 567 lines)
9. `engines/source/contracts.py` — upstream output contract
10. `engines/passaging/contracts.py` — downstream input contract
11. `KNOWLEDGE_INTEGRITY.md` — especially T-1 (silent text corruption)
12. `RESULT_PRESERVATION.md` — every API call persists full output

## The 3 MUST-FIX Items (resolve FIRST, Session 1)

From SPEC_INTEGRITY_AUDIT_NORMALIZATION.md:
1. DivisionNode: SPEC defines 14 fields, contracts.py has 7 — decide which fields are core
2. LayerMapEntry: field names must align with passaging SPEC expectations
3. §5 check 14 vocalization_level: field doesn't exist upstream — redesign the check

## Build Session Sequence

Follow Blueprint §2c (incremental build order, adapted for normalization):

### Session 1: Contracts + MUST-FIX resolution
- Resolve the 3 MUST-FIX items (align contracts.py with audited SPEC)
- Update all Pydantic models to match post-audit SPEC §2, §3
- Run boundary-validator on source→normalization and normalization→passaging
- Tests: contract serialization, import compatibility

### Session 2: Shamela HTML normalizer (deterministic)
- This is the CORE of the engine — Shamela is the only format for Stage 1
- Adapt ABD normalizer (~1,123 lines in reference/archive/abd_code/)
- Implement Pass 1 (structure extraction), Pass 2 (content/footnote separation),
  Pass 3 (HTML stripping), Pass 4 (page assembly), Pass 5 (division tree)
- All deterministic — no LLM calls
- Tests: Arabic adversarial inputs, diacritic preservation, NFC normalization

### Session 3: Multi-layer detection + text fidelity
- CSS-based layer detection (bold tags, font size, brackets)
- The two-factor bold test (>=80 chars AND no transition marker) per audit fix M-03
- Text fidelity scoring (character-level diff vs frozen source)
- Tests: the 20 multi-layer books from source engine Phase D output

### Session 4: LLM fallback + structure discovery
- LLM-based layer classifier for ambiguous cases (§4.B.1)
- Structure discovery from division keywords when headings are absent
- Consensus requirement for content-based layer inference (D-041)
- Tests: books where CSS detection is insufficient

### Session 5: Orchestrator + validation + integration
- Wire all modules into engine.py
- All §5 validation checks (with positive + negative tests)
- Integration test on 5 diverse real books (multi-layer, single-layer, verse, prose, multi-volume)
- mypy clean
- boundary-validator PASS on both sides

## Build Team Agents to Use

Per AGENT_ARCHITECTURE.md §2.2:
- **Test engineer** (existing `.claude/agents/test-engineer.md`) — invoke as Task after each module
- **Code reviewer** (existing `.claude/agents/code-reviewer.md`) — invoke at end of each session
- **Boundary validator** (existing `.claude/agents/boundary-validator.md`) — invoke after contracts changes

Additionally, per AGENT_ARCHITECTURE.md §2.4:
- **Build prober** (Red Team) — after each session, review cumulative diff vs SPEC
  NOTE: This agent does not exist yet. Write `.claude/agents/build-prober.md` before Session 1.

## Test Requirements (from Blueprint §2d)

1. Deterministic tests — no LLM, run in CI, cost €0
2. Arabic text tests — mixed diacritics, NFC vs NFD, Arabic comma, ZWNJ, truncated UTF-8
3. Gold baselines — 10 hand-verified books (5 from source engine Phase D, 5 new)
4. Negative tests — invalid input rejected, low confidence triggers human gate
5. Every §4.A capability has ≥1 test
6. Every §5 validation check has positive AND negative test

## Tier 1 Development Books (50)

Select 50 books from the 279 source engine results for development testing:
- 10 multi-layer (sharh, hashiyah — test layer detection)
- 10 single-layer prose (risalah, matn — test basic extraction)
- 5 verse/nazm (test verse detection)
- 5 multi-volume (test volume assembly)
- 5 with tahqiq apparatus (test footnote separation)
- 5 with known quality issues from source engine evaluation
- 10 random from remaining (diversity)

The selection should be committed as `engines/normalization/tests/TIER1_BOOKS.json`
before processing begins.

## Do NOT Do

- Do NOT build PDF, OCR, EPUB, or image normalizers — Shamela HTML ONLY for Stage 1
- Do NOT implement §4.B capabilities (deferred) unless they are referenced by §4.A
- Do NOT modify source engine code or contracts
- Do NOT skip the Build Prober agent — it catches SPEC deviations during build
- Do NOT auto-approve any human gate checkpoints

## Verification

After Session 5:
- All deterministic tests pass
- mypy reports 0 errors
- 10 gold baselines exist with documented sources
- 5 real books process end-to-end without error
- boundary-validator PASS on source→norm and norm→passaging
- Build Prober has reviewed all 5 session diffs (report committed)

## After This

Architect (Claude Chat) performs code audit (Blueprint §2e) — reads every module
against SPEC §4.A. Then Probe 3 begins (Verification team on 50 Tier 1 books).

## Probe 2 Measurement

Report in `reference/PROBE_2_RESULTS.md`:
- Test count per session
- Bugs found by test-engineer vs code-reviewer vs Build Prober
- Did the Build Prober catch any SPEC deviations?
- Session count and lines of code produced
- Any handoff prompt deficiencies (where Claude Code had to improvise)
