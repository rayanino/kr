# Source Engine Spec Discovery — Handoff to Codex

**Date:** 2026-04-14
**From:** Claude Code (Session 1 — spec discovery planning + orchestration)
**To:** Codex CLI (taking over as orchestrator + executor)
**Branch:** `clean-start` (pushed to remote)

---

## Current State

75 spec atoms in `engines/source/spec/`, all validating (`validate_spec.py` exits 0).

| Status | Count |
|--------|-------|
| confirmed | 19 (all 16 OF atoms + 3 CON atoms) |
| proposed | 49 (includes the new front-of-pipeline redesign atoms) |
| deferred | 3 (OQ-SRC-0001, OQ-SRC-0005, DEC-SRC-0003) |
| superseded | 2 (OQ-SRC-0004, OQ-SRC-0006) |
| draft | 2 (OQ-SRC-0003, OQ-SRC-0007 — awaiting DR results) |

**Atom types:** 26 REQ, 8 INV, 14 DEC, 5 CON, 6 OQ, 16 OF

The spec now uses a numbered, behavior-first layout:

- `00-vision/`
- `01-vocabulary/`
- `10-pipeline/`
- `20-contracts/`
- `30-architecture/`
- `40-quality/`
- `50-questions/`
- `60-evidence/`

Normative YAML atoms live under behavior/layer folders. `views/` remains generated and non-canonical.

## What Was Accomplished

1. Owner interviewed (4 batches, 16 answers) — captured as OF-SRC-0001 through 0016
2. Spec infrastructure: schema.json, validate_spec.py, generate_views.py, INDEX.yaml
3. 6 spec team agents in `.claude/agents/spec-*.md`
4. Engine CLAUDE.md at `engines/source/CLAUDE.md`
5. Contract Architect review (Codex): structural gaps found and incorporated
6. Domain Validator review (Gemini CLI): Arabic scholarly gaps found and incorporated
7. Adversary review (CC): 12 findings found and incorporated
8. PDF added as first-class format (REQ-SRC-0021 through 0024, INV-SRC-0008)
9. 2 OQs resolved → DEC-SRC-0011, DEC-SRC-0012
10. 2 OQs deferred (implementation choices)

## What's In Flight

Two DR prompts dispatched by the owner. Results pending:

1. **ChatGPT DR → OQ-SRC-0003:** Agent-team architecture design (roles, escalation, monitoring)
2. **Gemini DR → OQ-SRC-0007:** Islamic scholarly research source inventory

When DRs return, incorporate findings into atoms:
- OQ-SRC-0003 → should become DEC-SRC-0013 or similar
- OQ-SRC-0007 → should amend REQ-SRC-0013 and DEC-SRC-0009

## What Went Wrong — Errors to Avoid

### ERROR 1: PDF atoms were originally written without examining real data
The 5 PDF atoms (REQ-SRC-0021 through 0024, INV-SRC-0008) were originally written from abstract knowledge. The empirical fix is now in place, and the remaining lesson is to keep future PDF changes grounded in real fixtures. The observed realities were:

- **`waraqat_usul/waraqat.pdf`** (13 pages): Has a text layer but it's CORRUPT. Broken ligatures, scrambled Arabic. `منت الورقات إلماـ احلرمني` should be `متن الورقات للإمام الحرمين`. The text layer looks extractable but produces garbage.
- **`ibn_aqil_alfiyyah/vol6.pdf`** (398 pages): Pure scanned images, ZERO text layer. This is the dominant case for classical Islamic scholarly PDFs.

**What this means for the PDF atoms:**
- The PDF model must preserve three cases: absent text layer, corrupt text layer, and clean text layer.
- PDF text-layer sampling is allowed only as intake-time diagnostic evidence, not as normalization work.
- OCR-primary normalization remains the default handoff route for PDFs.

**Remaining action:** Keep future PDF amendments calibrated against fixtures and any newly supplied owner PDFs before changing the routing logic again.

### ERROR 2: Insufficient empirical grounding throughout
More broadly, many atoms were designed from principles rather than from examining real data. The Shamela HTML atoms were better grounded (v1 archive had extensive empirical data from 2,519 books), but the PDF atoms and the agent-team atoms are theory-heavy. Before building, the implementer should examine actual inputs.

### ERROR 3: Format-first instead of team-first
The plan was revised to be "team-first" but execution still went format-first — infrastructure and atoms were produced before the spec team was fully deployed. The agents exist but were underutilized. The Adversary had to be run manually after the CC agent failed on Windows paths.

## Remaining Work (Prioritized)

### P0: Fix the PDF atoms with empirical evidence
1. Run PyMuPDF on both fixtures (`waraqat.pdf` and `ibn_aqil/vol6.pdf`)
2. Understand the three-case model: pure scan, corrupt text, clean text
3. Rewrite REQ-SRC-0021 (format detection) with text quality validation
4. Amend REQ-SRC-0022 (OCR quality) and REQ-SRC-0023 (diacritics) based on what the fixtures actually show
5. Consider: does the owner have MORE PDF examples beyond these 2? If so, examine those too.

### P1: Incorporate DR results
When the owner provides ChatGPT DR and Gemini DR results:
- OQ-SRC-0003 → formalize into a decision atom with concrete agent-team roles
- OQ-SRC-0007 → amend REQ-SRC-0013 and DEC-SRC-0009 with the research source inventory

### P2: Owner gate on critical atoms
Present the critical-priority atoms to the owner for confirmation:
- REQ-SRC-0001 (autonomous intake)
- REQ-SRC-0004 (multi-model author attribution)
- REQ-SRC-0008 (agent-team trust)
- REQ-SRC-0009 (agent self-resolution)
- INV-SRC-0002 (author attribution role separation)
- INV-SRC-0003 (library never refuses knowledge)
- CON-SRC-0004 (SourceMetadata output schema)

Owner gate = show the atom, ask "does this match what you want?", record confirmation.

### P3: Spec freeze
- Move all confirmed atoms from `proposed` to `confirmed`
- Generate final views
- Validate one last time

### P4: Contract derivation
- Derive `contracts.py` (Pydantic models) from the confirmed spec atoms
- The SourceMetadata schema should come directly from CON-SRC-0004 + all REQ postconditions
- Cross-validate with test fixtures

### P5: Archive miner pass (optional but valuable)
The v1 archive at `engines/source/reference/archive/v1/source_engine/` has more to give:
- Edge cases from `reference/edge_cases.md` (12 documented)
- Bug patterns from `LESSONS.md`
- Extraction patterns from `src/extractors/shamela_html.py`
- Test patterns from `tests/test_deterministic.py`

Use the `spec-archive-miner` agent to extract additional atoms.

## Owner Design Principles (Non-Negotiable)

These came from the owner interviews. Do not override them:

1. **Agent-first, owner-validates.** Owner hints are cross-validation signals, never primary data, never biasing.
2. **Library never refuses knowledge.** Sciences are a growable registry.
3. **Zero-tolerance for attribution errors.** The #1 quality metric. Errors are devastating.
4. **Minimal owner review.** Auto-decide aggressively. Only genuinely unresolvable cases reach the owner.
5. **Agent teams for trust.** Replace numeric algorithms with agent-team deliberation.
6. **No human gates for metadata.** Agents resolve disagreements autonomously with failure analysis.
7. **Hadith is primary focus.** 48.7% of collection. Fine-grained hadith classification is critical.
8. **Truth-seeking, not consensus-forcing.** Disputed metadata is valid. Record all positions with evidence.
9. **No binding downstream contracts.** All engines rebuilt. Design from first principles.
10. **Specialized research agents.** Dedicated agents for specific scholarly databases, not generic web search.

## Key Files

| File | Purpose |
|------|---------|
| `engines/source/CLAUDE.md` | Engine-local agent instructions |
| `engines/source/spec/INDEX.yaml` | Atom registry (75 entries) |
| `engines/source/spec/schema.json` | JSON Schema for atom validation |
| `engines/source/scripts/validate_spec.py` | Schema + consistency validator |
| `engines/source/scripts/generate_views.py` | YAML → Markdown view generator |
| `engines/source/scripts/spec_common.py` | Shared utilities for spec scripts |
| `engines/source/spec/10-pipeline/` | Canonical ordered source-engine steps |
| `engines/source/spec/20-contracts/` | Contract surfaces for upload, dossier, metadata, and handoff |
| `engines/source/spec/30-architecture/` | Registry and agent-team decisions |
| `engines/source/spec/60-evidence/reviews/` | Review evidence (contract-architect, domain-validator, adversary) |
| `.claude/agents/spec-*.md` | 6 spec team agent definitions |
| `tests/fixtures/waraqat_usul/waraqat.pdf` | PDF fixture: corrupt text layer, 13 pages |
| `tests/fixtures/ibn_aqil_alfiyyah/vol6-9.pdf` | PDF fixture: pure scans, ~400 pages each |

## Commits (9 total, all on clean-start)

```
4efcf2e3b feat(source): resolve 2 OQs, defer 2, add DEC-SRC-0011/0012
f2bb395dd feat(source): add PDF as first-class production format
afbfaa3c7 feat(source): incorporate adversary review — 4 new atoms, 8 amended
f5dc30b3f docs(source): add adversary review — 12 findings, 2 critical gaps
b79a0ba38 feat(source): incorporate coworker reviews - amend 21 atoms, add 4 new
20d36b6e0 chore(source): fix validator exclusions, add coworker review reports
f78997a95 feat(source): add spec team agents and engine CLAUDE.md
4ad0fee19 feat(source): create spec infrastructure with 53 atoms
e0148cd20 refactor: archive first reset source engine
```
