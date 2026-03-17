# Probe 1 Results — SPEC Team on Normalization SPEC

**Date:** 2026-03-17
**Engine:** Normalization
**SPEC size:** ~2,007 lines (pre-audit), ~2,090 lines (post-audit)
**Probe objective:** Test the dual-audit SPEC team architecture on a real deliverable

---

## 1. Probe Metrics

### 1.1 Defect Detection

| Metric | Value |
|--------|-------|
| Auditor A findings | 19 (14 CORRECTNESS, 5 STYLE) |
| Auditor B findings | 27 (22 CORRECTNESS, 5 STYLE) |
| Total raw findings | 46 |
| After merge (deduplicated) | 35 |
| Confirmed real defects | 31 |
| False positives | 4 (9% FP rate) |
| BOTH_FOUND (independent agreement) | 8 (23% of confirmed) |
| A_ONLY confirmed | 9 (26%) |
| B_ONLY confirmed | 14 (40%) |

### 1.2 Value of Dual Audit

| Scenario | Defects Found | % of Total |
|----------|---------------|------------|
| Single auditor (patterns 1-4 only) | 17 | 55% |
| Single auditor (patterns 5-7 + T-threats only) | 22 | 71% |
| **Dual audit** | **31** | **100%** |

- Dual audit found **41% more defects** than the best single auditor (B)
- Dual audit found **82% more defects** than the worst single auditor (A)
- The AGENT_ARCHITECTURE.md threshold was "if dual audit adds <20% more findings than single audit, consider merging." The dual audit adds **41%** — well above threshold.

**Important caveat:** The 41% figure reflects the complementary non-overlapping pattern sets (1-4 vs 5-7+T). 20 of 23 one-sided findings were scope-limited — the other auditor couldn't have found them because their checklist doesn't cover that defect type. A hypothetical single auditor with ALL 14 checks would likely find ~28-30 of 31 defects. The dual audit's primary value is: (1) parallel execution speed (~8 min each vs ~16 min sequential), (2) independent confirmation on the 8 BOTH_FOUND items, and (3) catching the 3 genuine misses that depth-of-focus enables.

### 1.3 CORRECTNESS vs STYLE

| Auditor | CORRECTNESS | STYLE | CORRECTNESS % |
|---------|-------------|-------|---------------|
| A | 14 | 5 | 74% |
| B | 22 | 5 | 81% |
| Merged | 28 | 3 | 90% |

Target was >40% CORRECTNESS. Both auditors exceeded this substantially, indicating thorough reviews rather than surface-level style picks.

### 1.4 One-Sided Finding Analysis

| Classification | A_ONLY | B_ONLY |
|----------------|--------|--------|
| Confirmed (scope-limited) | 8 | 12 |
| Confirmed (other auditor could have found) | 1 | 2 |
| False positive | 2 | 2 |

**Key finding:** 20 of 23 one-sided findings were **scope-limited** — the other auditor couldn't have found them because the defect falls outside their assigned pattern set. This validates the non-overlapping checklist design. Only 3 one-sided findings represent genuine "misses" by the other auditor.

### 1.5 Research Validation

| Defects researched | 10 |
|---|---|
| Auditor criticism validated | 10/10 (100%) |
| Technologies found to be broken/unsuitable | 2 (Docling Arabic, PaddleOCR Arabic) |
| Technologies confirmed with caveats | 3 (CAMeL Tools, QARI-OCR, Baseer) |
| No published method exists | 2 (matn/sharh detection, footnote classification) |
| Web searches conducted | 21 (below the 8-per-defect protocol target; each Tavily search returned 5 results = ~105 individual results examined) |

---

## 2. Defect Categories

### 2.1 By Pattern Type

| Pattern | Count | Build Impact |
|---------|-------|-------------|
| P4: Phantom Metadata (contract ≠ SPEC) | 10 | BUILD-BLOCKING — code would fail Pydantic validation |
| P6: Missing Error Paths | 8 | HIGH — undefined failure behavior |
| P7: Scope Creep | 6 | HIGH — engine doing other engines' jobs |
| P3: Hand-Waving Technology | 4 | HIGH — named tools don't work for Arabic |
| P5: Untestable Rules | 4 | MEDIUM — implementer ambiguity |
| P1: Hollow Examples | 3 | MEDIUM — wrong implementations pass examples |
| P2: Circular Definitions | 2 | LOW — misleading but not blocking |

### 2.2 By Threat Type

| Threat | Count | Highest Risk Finding |
|--------|-------|---------------------|
| T-1: Silent Text Corruption | 5 | Docling produces reversed Arabic (M-21) |
| T-2: Attribution Error | 4 | Layer detection "قال" ambiguity (M-04) |
| T-6: Metadata Poisoning | 4 | Discourse school_hint leaking downstream (M-08) |
| T-3: Taxonomic Misplacement | 2 | Format auto-detection overrides consensus (M-31) |
| T-4: Context Loss | 2 | Plain text null continuity (M-28) |
| T-7: Duplication/Contradiction | 2 | Volume number parsing failure (M-25) |
| T-5: Synthesis Hallucination | 1 | Morphological validation creating false corrections (M-27) |

### 2.3 Highest-Impact Findings

1. **Docling Arabic PDF extraction is actively broken** (M-21). GitHub issues #1938, #2179 show reversed words/characters. Without this audit, the build would have used Docling as primary PDF backend and produced garbled Arabic text for every PDF source. **Fix:** Switched to PyMuPDF+bidi.

2. **10 phantom metadata fields** (M-09 through M-14, M-18, M-20). The SPEC references fields that don't exist in contracts.py. An implementer following the SPEC would write code that immediately fails. **Fix:** Added §9.1 contract alignment section.

3. **PaddleOCR CER 0.79 on Arabic** (M-17). The SPEC cited OmniDocBench (English-focused) score. ACL 2025 Arabic benchmark shows dramatically worse performance. **Fix:** Deprioritized PaddleOCR, added KR-internal benchmarking requirement.

4. **Discourse flow performing taxonomic pre-classification** (M-08). school_hint and attribution_hint in normalization output would poison downstream engines. **Fix:** Removed, marked as ADVISORY.

5. **Format auto-detection overriding consensus** (M-31). Single-engine heuristic overwriting multi-model consensus classification. **Fix:** Changed to PROPOSE, human gate required.

---

## 3. Post-Audit SPEC Status

### Integrity Audit Verdict: CONDITIONAL PASS

| Category | Count |
|----------|-------|
| MUST-FIX (blocks build) | 3 — all contract alignment, resolvable during build |
| SHOULD-FIX (fix during build) | 9 — specification precision, missing glossary, etc. |
| New gaps found by integrity auditor | 2 — missing error code + missing manifest field |

The 3 MUST-FIX items are:
1. DivisionNode 7-vs-14 field decision (M-14)
2. LayerMapEntry field name alignment with passaging SPEC (M-13)
3. §5 check 14 vocalization_level field doesn't exist upstream (M-09)

All are resolvable at build time without SPEC redesign.

### Deferred Defects (7 SPEC text defects not fixed in this probe)

Of 31 confirmed defects, 22 were fixed in the SPEC, 6 were deferred to §9.1 (contract alignment), and 5 remain as SHOULD-FIX items to be addressed during the build. Two additional defects (M-01, M-05) were fixed in the self-review pass.

| Defect | Status | Rationale |
|--------|--------|-----------|
| M-01 | **Fixed (self-review)** | Whitespace Unicode enumeration — trivial, applied post-review |
| M-02 | Deferred to build | Hadith detection patterns need domain expertise to define correctly |
| M-05 | **Fixed (self-review)** | "trains" → "uses via in-context learning" — one-word fix |
| M-07 | Deferred to build | KR technical glossary is a prerequisite that doesn't exist yet |
| M-28 | Deferred to build | Plain text continuity needs a design decision on fallback algorithm |
| M-35 | Deferred to build | Upstream author_canonical_id trust is a cross-engine concern (Layer 3) |
| M-36 | Deferred to build | Heading text fidelity field — straightforward but needs contract coordination |

**Self-criticism:** The initial deferral of these 7 defects was implicit — they were omitted from the SPEC Writer's prompt without explicit triage. The integrity auditor caught all 7 as SHOULD-FIX items, preventing silent loss. Three (M-01, M-05, _note artifacts) should have been fixed in the first pass.

### Defects Neither Auditor Found (2)

The integrity auditor discovered 2 gaps that both auditors missed:
1. Missing `NORM_FOOTNOTE_CLASSIFICATION_FAILED` error code for §4.B.4 LLM fallback failure (Pattern 6 — Auditor B's territory)
2. `structural_format_proposed` manifest field (created by M-31 fix) not in §3 or contracts.py (Pattern 4 — but the field didn't exist during the audit)

---

## 4. Architecture Assessment

### 4.1 Does the Dual Audit Add Value?

**YES.** The dual audit found 31 defects vs. 22 from the best single auditor (41% raw improvement). As noted in §1.2, most of this improvement comes from the complementary non-overlapping pattern sets rather than independent discovery. The real value proposition is threefold: parallel speed (8 min each vs ~16 min serial), independent confirmation on BOTH_FOUND items, and depth-of-focus enabling the 3 genuine-miss catches. Combined with only 9% false positive rate:

- A's strengths: contract verification, technology feasibility, example quality
- B's strengths: error path completeness, scope enforcement, corruption tracing
- Only 3 of 23 one-sided findings were genuine misses (87% scope-limited)

### 4.2 Should the Auditors Be Merged?

**NO.** The >20% threshold (AGENT_ARCHITECTURE.md §5 Probe 1) is exceeded at 41% raw improvement. Even accounting for non-overlapping design (a single auditor with all 14 checks would find ~28-30), the architecture offers parallel execution speed and depth-of-focus benefits. Merging would require one auditor to hold 7 patterns + 7 threats (14 checks per rule), risking shallow coverage — Auditor B's 27 findings vs. a combined checklist would likely produce fewer findings per pattern.

### 4.3 Comparator Value

The Comparator identified 4 false positives (9%) and correctly classified all 8 BOTH_FOUND items. It provided the critical "dual-audit value assessment" that enables this measurement. The Comparator is essential — without it, the dual audit produces two unreconciled lists.

### 4.4 Deep Researcher Value

All 10 researched criticisms were validated, with 2 showstopper findings (Docling, PaddleOCR). The research converted vague "this technology might not work" concerns into specific evidence with URLs, version numbers, and benchmarks. The 21 web searches produced actionable SPEC fix text.

### 4.5 Agent Costs

| Agent | Tokens | Duration | Searches |
|-------|--------|----------|----------|
| Auditor A | ~116K | 7.3 min | 0 |
| Auditor B | ~113K | 8.1 min | 0 |
| Comparator | ~78K | 5.8 min | 0 |
| Deep Researcher | ~107K | 8.9 min | 21 |
| SPEC Writer | ~116K | 16.2 min | 0 |
| Integrity Auditor | ~151K | 4.9 min | 0 |
| **Total** | **~681K** | **~51 min** | **21** |

The full SPEC team pipeline processed a 2,007-line SPEC in ~51 minutes of agent time (much of it parallel), finding 31 real defects including 2 showstoppers. For comparison, the source engine SPEC went through 4 manual refinement passes by the Architect.

---

## 5. Recommendations for Probe 2

1. **Proceed with Build Team probe** on the audited normalization SPEC. The CONDITIONAL PASS means build can start while resolving the 3 MUST-FIX items.

2. **Resolve the 3 MUST-FIX items** at the start of the build (they're all contract alignment — first build session should align contracts.py with SPEC).

3. **Keep the dual-audit architecture** for all remaining engines. The parallel speed, independent confirmation, and depth-of-focus benefits justify the overhead. Consider testing a single-auditor-with-all-patterns baseline on one future engine to empirically measure the depth-of-focus effect.

4. **Add Docling Arabic status** to the project's technology watch list. If Docling fixes issues #1938/#2179, it may become viable again for Arabic PDFs.

5. **Create the KR-internal OCR benchmark** before building the OCR pipeline (M-17 fix requires it).

---

## 6. Artifacts Produced

| File | Description |
|------|-------------|
| `.claude/agents/spec-auditor-a.md` | Auditor A agent definition |
| `.claude/agents/spec-auditor-b.md` | Auditor B agent definition |
| `.claude/agents/audit-comparator.md` | Comparator agent definition |
| `.claude/agents/deep-researcher.md` | Deep Researcher agent definition |
| `.claude/agents/integrity-auditor.md` | Integrity Auditor agent definition |
| `reference/SPEC_AUDIT_A_NORMALIZATION.md` | Auditor A inventory (19 defects) |
| `reference/SPEC_AUDIT_B_NORMALIZATION.md` | Auditor B inventory (27 defects) |
| `reference/SPEC_AUDIT_COMPARISON_NORMALIZATION.md` | Merged comparison (31 confirmed) |
| `reference/SPEC_RESEARCH_NORMALIZATION.md` | Research findings (10 defects, 21 searches) |
| `reference/SPEC_INTEGRITY_AUDIT_NORMALIZATION.md` | Final integrity check (CONDITIONAL PASS) |
| `reference/PROBE_1_RESULTS.md` | This document |
| `engines/normalization/SPEC.md` | Revised SPEC (22 fixes applied) |
