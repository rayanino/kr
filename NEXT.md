# NEXT — Excerpting Engine: Implement Evaluation Findings + Re-run

## What Happened (2026-03-31 to 2026-04-01)

A comprehensive 6-reviewer evaluation of the excerpting engine's first outputs:
- **133-excerpt smoke run** (€2.93, GPT-5.4 primary) — evaluated by 5 reviewers
- **2,303-excerpt campaign** ($96.87, Opus primary, accidental) — full-book data preserved
- **8 Tier-1 prompt fixes** implemented and committed (H-1 through H-8)
- **3 Claude DR fixes** implemented (narrator role, المعنى الإجمالي, fawa'id)
- **Bug fixes**: consensus resolution, ZWNJ, LA-3 threshold, model defaults, CLAUDE.md
- **Owner reviewed 2 taysir excerpts** → triggered fundamental granularity question
- **6-reviewer architectural decision** on excerpt granularity (DR-1/DR-2/DR-3)
- **907 tests pass**, 0 pyright errors on all engine source files

## Current State

```
Source OK → Normalization OK --- boundary --- Excerpting [HARDENING] → Taxonomy → Synthesis
                                                ^^^^^^^^^^^^^ YOU ARE HERE
```

**What's committed:** 14 prompt/code fixes across 8 commits (ef8c7696..063ee4ab).
**What's NOT committed:** Some diagnostic reports in repo root, Gemini adversarial review.
**What's NOT implemented:** DR-1, DR-3, CrossReference extension, evidence_refs quality, SPEC amendments.

## Immediate Task: Implement DR-1 + DR-3 + Supporting Changes

**Read these files first (in order):**

1. `engines/excerpting/domain_rules/DR_DOMAIN_RULES.md` — the proposed rules (DR-1 adopted, DR-2 DEFERRED, DR-3 adopted)
2. `integration_tests/campaign_20260331/taysir/owner_feedback.jsonl` — the owner's 2 review comments that triggered everything
3. This file's "Implementation Checklist" section below
4. `engines/excerpting/SPEC.md` §5.3.2 (grouping rules) and §6.1 (decontextualization)
5. `engines/excerpting/contracts.py` — CrossReference model (lines ~140-155)

**Context on the 6-reviewer decision (read the memory file for full details):**
- **DR-1 (Definition Pairs):** ADOPTED (4-1). Split لغة/شرعا definitions when both substantive AND self-containment preserved.
- **DR-2 (Evidence Splitting):** DEFERRED (2-3 against). Do NOT implement. Improve evidence_refs metadata instead.
- **DR-3 (Khilaf Preservation):** ADOPTED (5-0). Keep scholarly disagreement passages together. Structural trigger, not word count.

## Implementation Checklist

### 1. Update DR_DOMAIN_RULES.md to reflect final decision
- Mark DR-2 as DEFERRED with rationale (3/5 reviewers rejected; VISION §1.2 tension unresolved)
- Update DR-1 to add self-containment condition: "MUST split... UNLESS splitting breaks self-containment"
- Update DR-3 to replace 800-word threshold with structural criteria

### 2. Add DR-1 to Phase 2b prompt (phase2_group.py)
Add DEFINITION PAIR SPLITTING rule to GROUP_SYSTEM_PROMPT:
```
DEFINITION PAIR SPLITTING (DR-1):
When a passage contains both a linguistic definition (تعريف لغوي) and a
legal/technical definition (تعريف شرعي / اصطلاحي) of the same term,
split them into separate teaching units IF:
- Both definitions are substantive (>3 words of definitional content)
- Each resulting unit achieves at least PARTIAL self-containment
- Brief glosses ("الطلاق لغة: الترك" — 1 word) stay together

Place relationship statements ("والتعريف الشرعي فرد من...") in the
شرعي/اصطلاحي unit. Add cross_references between the pair.

Detection markers: في اللغة... وفي الشرع... / لغةً... واصطلاحاً...
```

### 3. Add DR-3 to Phase 2b prompt (phase2_group.py)
Add KHILAF PRESERVATION rule:
```
KHILAF PRESERVATION (DR-3):
Scholarly disagreement passages (اختلاف العلماء) that present multiple
positions with evidence and refutations REMAIN as single teaching units
WHEN decomposition would lose argumentative structure — specifically:
- Refutations reference positions by pronouns (هذا القول, الأول)
- The tarjih depends on comparing all positions
- Evidence for one position simultaneously refutes another

Detection markers: فذهب... وذهب..., والصحيح/والأرجح/والراجح,
ورد عليه/وأجاب/فضعيف

DR-3 OVERRIDES other splitting rules for content within khilaf passages.
```

### 4. Extend CrossReference schema (contracts.py)
Add two optional fields to CrossReference:
```python
target_excerpt_id: Optional[str] = Field(None, description="Links to companion excerpt from same source passage")
relationship_type: Optional[str] = Field(None, description="Semantic relationship: companion_definition, evidence_for, ruling_proven_by, refutation_of, continuation")
```

### 5. Update Phase 3 enrichment for split companion detection
Add enrichment step that detects split companion units (adjacent units from same chunk that were split by DR-1) and populates cross-references between them.

### 6. Improve evidence_refs quality
Add to enrichment prompt: when a Quranic verse is cited, resolve to canonical (surah, ayah_start, ayah_end) wherever possible. When a hadith is cited with collector name, resolve to canonical collection + number. This enables synthesis-level evidence comparison WITHOUT needing DR-2 splitting.

### 7. SPEC amendments
- §5.3.2: Add DR-1 and DR-3 rules
- §6.1: Clarify that DP-4 remains the default (DR-2 deferred)
- §2.2.2: Update CrossReference schema with new fields

### 8. Update NEXT.md (after implementation)
After all above is done, rewrite NEXT.md to point to the re-run.

### 9. Re-run (~€3, ~33 min)
```bash
python scripts/run_full_integration.py --backend api --output-dir integration_tests/smoke_api_v2/
```
GPT-5.4 primary (defaults now correct). Compare against smoke_api v1 (133 excerpts, old prompts).

### 10. Evaluate v2 output
- Run structural validator: `python tools/evaluate_excerpts.py --root integration_tests/smoke_api_v2/`
- Owner reviews taysir via: `python tools/review.py integration_tests/smoke_api_v2/`
- Compare: author_id resolution, FULL rate, consensus coverage, ZWNJ count, definition splitting, khilaf handling

## Your Team

You have 5 coworkers — USE ALL OF THEM at every major milestone:
- **Codex** (`codex exec`): schema validation, cross-prompt consistency, stats
- **Gemini CLI** (`gemini -p`): Arabic scholarly accuracy, convention compliance
- **ChatGPT Pro** (deep research): independent cross-check, pattern analysis
- **Claude Chat** (deep research): scholarly review, boundary quality
- **Gemini Chat** (deep research): scholarly perspective

## Research Artifacts (DO NOT DELETE)

### Diagnostic Reports (repo root)
| File | Author | Content |
|------|--------|---------|
| `BOUNDARY_CONVENTION_DIAGNOSTIC.md` | Claude DR | Boundary errors + convention compliance at 133 scale |
| `chatgpt-report-diagnostic-analysis.md` | ChatGPT DR | Error patterns (first run, wrong repo) |
| `chatgpt-deep-research-opus_vs_gpt.md` | ChatGPT DR | Opus vs GPT-5.4 model comparison |
| `chatgpt-deep-research-granuality-synthesis.md` | ChatGPT DR | Synthesis engine solution analysis |
| `chatgpt-Adversarial Review of DR-1, DR-2, DR-3.md` | ChatGPT DR | Adversarial review of domain rules |

### Campaign Analysis (integration_tests/campaign_20260331/analysis/)
| File | Content |
|------|---------|
| `campaign_analysis.md` | Executive summary of 2,303 excerpts |
| `excerpt_catalog.jsonl` | Searchable index of all excerpts |
| `gold_candidates.jsonl` | 100 gold standard candidates (97 Tier A) |
| `gold_standard_20_scholarly_review.md` | 20 verified gold excerpts with full metadata |
| `taxonomy_readiness_flags.jsonl` | 54 flags for downstream risks |
| `arabic_fidelity_flags.jsonl` | 382 Arabic text quality flags |
| `convention_compliance_report.md` | 7-check convention audit (5 PASS, 1 MOSTLY PASS, 1 FAIL) |
| `taysir_scholarly_review.md` | Claude DR's 68-excerpt deep review |
| `scholarly_reality_check_intra_excerpt.md` | Why intra-excerpt annotation fails on Arabic |
| `gemini_adversarial_DR_review.md` | Gemini's adversarial review of DR rules |
| `trace_catalog.jsonl` | 1,100 LLM call cost/latency data |
| `function_summary.json` | Function distribution by package |
| `self_containment_summary.json` | FULL/PARTIAL/DEPENDENT rates |
| `package_summary.json` | Per-package statistics |
| `run_fingerprint.json` | Campaign metadata |

### Domain Rules
| File | Content |
|------|---------|
| `engines/excerpting/domain_rules/DR_DOMAIN_RULES.md` | DR-1/DR-2/DR-3 (DR-2 deferred) |
| `reference/handoffs/cross_provider_review_DR_rules.md` | Adversarial review brief |

### Owner Feedback
| File | Content |
|------|---------|
| `integration_tests/campaign_20260331/taysir/owner_feedback.jsonl` | 2 excerpt reviews — fundamental granularity feedback |

## Key Decisions (with rationale)

| Decision | Rationale | Reviewers |
|----------|-----------|-----------|
| GPT-5.4 as primary model | 3x cheaper, contract-stable, known errors are prompt-fixable | 3/5 agree (Codex, ChatGPT, my analysis) |
| DR-1 ADOPT (conditional) | Definition pairs are separate scholarly topics; self-containment gate prevents bad splits | 4/5 agree |
| DR-2 DEFER | 3/5 reject; "puzzle excerpts" risk; VISION §1.2 vs multi-leaf unresolved | 3/5 reject, deferred to taxonomy pilot |
| DR-3 ADOPT (structural) | Khilaf passages are the highest decontextualization risk | 5/5 unanimous |
| Keep medium excerpts as canonical unit | VISION §5.2 taxonomy-independence + §5.3 Rule 3 content integrity | Architecture-mandated |

## Budget

- Smoke v1: €2.93 (done)
- Campaign: $96.87 (done, accidental)
- Aborted v2: ~$3.15 (partial, killed)
- Remaining: ~€17 of original €120 budget
- Next re-run: ~€3

## Test Status

907 passed, 0 failures. 2 LLM integration tests skip when API key unavailable.
Pyright: 0 errors on all engine source files.
