# خزانة ريان — Project Status

**Last updated:** 2026-03-04 by Claude Chat (environment setup session)
**Current phase:** Phase 2 — Engine-by-Engine SPEC Writing
**Current work item:** W-001 (Source Engine SPEC)

## What Was Just Completed
- Phase 1 + Phase 1.5 complete. 903 tests pass, 37 skip, 1 fail (API key).
- Coordination infrastructure committed (b251810): STATUS.md, reference/ directory.

## Current Work Item: W-001 — Source Engine SPEC

### Objective
Write `engines/source/SPEC.md` — the first Level 2 specification. Then correct VISION.md §7.1–§7.4.

### Files to Attach This Session

**Prepare the VISION excerpt first** (saves 76% context):
```
make vision SECTIONS="2 7"
```
This creates `vision_excerpt.md` (~58KB instead of 244KB). Attach it instead of full VISION.md.

**Session 1 attachments** (~60K tokens total — well within budget):
1. `vision_excerpt.md` — §2 (glossary) and §7 (source pipeline)
2. `engines/source/src/intake.py` — main intake logic (1476L)
3. `engines/source/src/enrich.py` — metadata enrichment (580L)
4. `engines/source/src/corpus_audit.py` — audit tool (228L)
5. `engines/source/reference/ABD_INTAKE_SPEC.md` — ABD-era spec (795L)
6. `engines/source/reference/edge_cases.md` — known edge cases (127L)
7. `schemas/source_metadata.json` — current output schema
8. `schemas/SCHEMA_ANALYSIS.md` — pipeline data flow context

**Session 2 attachments** (add to above):
- The SPEC draft from session 1

### Protocol Mode
**Creation mode** — writing a new document. Skip Phase 1 (gap analysis). Follow: Intake → Research → Draft → Self-Audit → Revise → Present.

### Decisions Claude Makes This Round
- Source identity model: what is a "source"? Does `book_id` become `source_id`?
- Multi-volume representation: one source entity or many?
- Manual input representation within the source model
- Source registry format (`library/sources/registry.yaml`)
- Source engine output scope: what crosses the source→normalization boundary?
- ABD intake metadata evolution for KR
- `book_id` → `source_id` rename: now or deferred?

### Domain Questions to Ask Owner (Only If Needed)
- How do multi-volume works appear in the Shamela library?
- What does manual input look like in practice?

### Session Plan
**Session 1:** Read all materials. Build internal model. Make all architectural decisions. Draft SPEC §1–§5. If the response gets long, continue in next message (tell the owner "I'll continue in my next message").

**Session 2:** Draft SPEC §6–§10. Hostile self-audit (produce as visible deliverable — must find ≥3 defects). Revise. If time allows, begin VISION §7.1–§7.4 defect ledger.

**Session 3 (if needed):** Complete VISION §7.1–§7.4 defect ledger and corrected text.

### Completion Criteria
- [ ] SPEC.md complete (all 10 template sections, substantive)
- [ ] Every decision logged in kr_decisions.md format (D-016+)
- [ ] Perfection Standard Tier 1 + Tier 2 pass
- [ ] §9 (Current Implementation State) has accurate file paths and line counts
- [ ] Phase 4 self-audit visible deliverable with ≥3 defects found and resolved
- [ ] VISION §7.1–§7.4 defect ledger produced
- [ ] Corrected VISION §7.1–§7.4 text produced
- [ ] STATUS.md updated to point to W-002

### Schema Impact
`schemas/source_metadata.json` likely updated. Downstream renames documented but deferred.

## Context Budget Guide
Claude Chat works best with ≤80K tokens of input. Heavy sessions (W-002, W-005) MUST be split so each session stays under this budget. STATUS.md for those items will specify the split explicitly.

## Blocked Items
None

## Session Notes for Next Claude
- This is the first SPEC. No upstream SPECs exist. This establishes the quality bar.
- The authority model: Claude decides ALL technical/architectural matters. Ask owner ONLY for domain/usage questions (the owner has no technical background).
- If your response is getting long, split across multiple messages — tell the owner you're continuing.
- SCHEMA_ANALYSIS.md has the full pipeline data flow diagram — useful for orientation.

## Active Document Versions
- VISION.md: §0–§5, §13 previously audited. §6–§12 pending.
- Source SPEC: stub (3 lines) — this session writes it.
- All other SPECs: stubs.
