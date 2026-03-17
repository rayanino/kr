# NEXT — Probe 1 Complete → Architect Review → Probe 2

## Current position: Probe 1 COMPLETE. Normalization SPEC audited, fixed, integrity-checked.
## What to do: Architect (Claude Chat) reviews Probe 1 results and the audited SPEC.
## Context: 31 defects found by dual audit (41% more than best single auditor).
  2 showstoppers caught: Docling Arabic broken, PaddleOCR CER 0.79.
  SPEC revised with 22 fixes. Integrity audit: CONDITIONAL PASS (3 MUST-FIX, all contract alignment).
## Owner action needed: NO — next step is Architect review.

---

## Probe 1 Summary

**Full results:** `reference/PROBE_1_RESULTS.md`

### What Was Done
1. Wrote 5 new agent definitions (spec-auditor-a, spec-auditor-b, audit-comparator, deep-researcher, integrity-auditor)
2. Ran dual audit on normalization SPEC (~2,007 lines): Auditor A (patterns 1-4) and B (patterns 5-7 + T1-T7) in parallel
3. Comparator merged inventories: 31 confirmed defects, 4 false positives, 8 BOTH_FOUND
4. Deep Researcher investigated 10 technology/domain defects with 21 web searches — all criticisms validated
5. SPEC Writer applied 22 targeted fixes (81 insertions, 38 deletions)
6. Integrity Auditor: CONDITIONAL PASS (3 MUST-FIX contract alignment, 9 SHOULD-FIX)

### Key Findings
- Dual audit adds **41% more defects** than best single auditor → validates the architecture
- **Docling Arabic PDF extraction actively broken** (GitHub #1938, #2179) → switched to PyMuPDF+bidi
- **PaddleOCR CER 0.79 on Arabic** (ACL 2025 benchmark) → deprioritized
- **10 phantom metadata defects** (SPEC fields not in contracts.py) → §9.1 alignment section added
- **Discourse flow was doing taxonomy's job** (school_hint, attribution_hint) → removed

### Verification Status
- [x] PROBE_1_RESULTS.md documents all metrics (with honest caveats on 41% figure and search count)
- [~] Most §4.A rules have testable criteria; 3 SHOULD-FIX exceptions remain: hadith pattern precision (M-02), KR glossary prerequisite (M-07), plain text continuity (M-28)
- [x] Every processing step has a defined error path (7 new error codes added to §7; 1 gap found by integrity auditor: NORM_FOOTNOTE_CLASSIFICATION_FAILED)
- [ ] 3 MUST-FIX contract alignment items remain (resolvable at build start, not redesign)
- [ ] 4 SHOULD-FIX defects deferred to build: M-02, M-07, M-28, M-36

## Artifacts

| File | What |
|------|------|
| `reference/PROBE_1_RESULTS.md` | Full probe metrics and architecture assessment |
| `reference/SPEC_AUDIT_A_NORMALIZATION.md` | Auditor A inventory (19 defects) |
| `reference/SPEC_AUDIT_B_NORMALIZATION.md` | Auditor B inventory (27 defects) |
| `reference/SPEC_AUDIT_COMPARISON_NORMALIZATION.md` | Merged comparison (31 confirmed) |
| `reference/SPEC_RESEARCH_NORMALIZATION.md` | Research findings (21 searches) |
| `reference/SPEC_INTEGRITY_AUDIT_NORMALIZATION.md` | Final integrity check |
| `engines/normalization/SPEC.md` | Revised SPEC (24 fixes applied, 4 deferred to build) |
| `.claude/agents/spec-auditor-a.md` | Agent definition |
| `.claude/agents/spec-auditor-b.md` | Agent definition |
| `.claude/agents/audit-comparator.md` | Agent definition |
| `.claude/agents/deep-researcher.md` | Agent definition |
| `.claude/agents/integrity-auditor.md` | Agent definition |

## After This

Architect (Claude Chat) reviews:
1. `reference/PROBE_1_RESULTS.md` — are the metrics satisfactory?
2. `engines/normalization/SPEC.md` — is the revised SPEC ready for build?
3. `reference/SPEC_INTEGRITY_AUDIT_NORMALIZATION.md` — are the 3 MUST-FIX items acceptable?

If satisfactory: Probe 2 (Build team on normalization engine).
