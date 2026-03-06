# Post-Preparatory Plan — الخطة بعد الإعداد

## What's Different From the Original Designs

Three key shifts based on research and analysis:

**Shift 1: Claude Code does BOTH building AND testing.**
The original design had Claude Chat testing and Claude Code fixing — a slow handoff loop. Research shows Claude Code's tight feedback loop (run test → see failure → fix → re-run) is 10x faster. Claude Code builds, tests with automated property checks, and self-fixes. You and Claude Chat review only what needs scholarly judgment (flagged excerpts, questionable attributions, entry quality).

**Shift 2: Build and test incrementally, not all-at-once.**
Don't build 7 engines then test. Build engines 1-2, test with 50+ sources, fix until trusted. Then build engines 3-4 on the trusted foundation, test, fix. Upstream bugs caught early don't cascade downstream.

**Shift 3: Your input comes from seeing real output, not reviewing specs.**
Instead of abstractly discussing each engine's SPEC, you see real Arabic text going through the pipeline and react: "this excerpt breaks the argument," "this attribution is wrong," "this entry would mislead a student." Your scholarly expertise is most valuable when applied to concrete output, not spec prose.

---

## The Phases

### Phase A: Owner Quality Criteria (1-2 sessions, Claude Chat + you, BEFORE any building)

Before Claude Code builds anything, you and Claude Chat define what "correct" means at each stage. Not technically — scholarly. This is the ONE thing that can't come from specs or testing.

**Session 1: Source + Normalization criteria**
Claude Chat shows you: "Here's what the source engine produces for شرح ابن عقيل (from the SPEC examples). Here's what normalization produces. Here are the edge cases."

You respond with domain knowledge:
- "When a book lists multiple authors, the convention is X"
- "For nahw books, diacritics matter more than for fiqh books because..."
- "A reliable tahqiq always has X, Y, Z in its muqaddimah"

**Session 2: Excerpting + Synthesis criteria**
This is the critical one. You define:
- What makes an excerpt "self-contained" in YOUR study?
- What makes a synthesized entry trustworthy?
- How should scholarly disagreements be presented?
- What metadata must be in every entry for it to be study-worthy?

These criteria become ACCEPTANCE TESTS — concrete, testable definitions of quality that Claude Code can check automatically AND that you verify on samples.

### Phase B: Incremental Build + Test (Claude Code, ~4-8 weeks)

Built in layers. Each layer is tested with real sources before the next layer begins.

#### Layer 1: Source + Normalization (~2 weeks)

**Build:** Claude Code implements engines 1-2 following SPEC + IMPLEMENTATION_ORDER.
**Test automatically:** 50+ sources through engines 1-2.
  - Source: author identified correctly? Genre correct? Trust score reasonable?
  - Normalization: text preserved? Layers detected? Diacritics intact?
**Property tests (run by Claude Code on every source):**
```
- assert source.metadata.author_name_ar is not None
- assert source.metadata.confidence >= 0.7
- assert normalization.text_fidelity >= 0.90
- assert all diacritics in input present in output
- assert footnotes separated from primary text
```
**Flags for human review:** Low-confidence identifications, unrecognized formats, text fidelity below threshold.

**Your role:** Review flagged items. Spot-check 10 random sources.
**Exit criteria:** 50+ sources, 0 misattributions, text fidelity ≥0.95 on all.

#### Layer 2: Passaging + Atomization (~1-2 weeks)

**Build:** Claude Code implements engines 3-4.
**Test:** Same 50+ sources, now running through engines 1-4.
**Property tests:**
```
- assert no passage splits an isnad chain
- assert no passage splits a Quran verse
- assert passage length between 200-5000 chars (configurable)
- assert atom types match expected distribution for genre
```
**Your role:** Read 20 passages from 5 different sources. Judge: "Is this a natural reading boundary?"
**Exit criteria:** Passage quality approved by you on 5 diverse sources.

#### Layer 3: Excerpting + Taxonomy (~2-3 weeks, hardest layer)

**Build:** Claude Code implements engines 5-6. These use LLMs — needs API keys.
**Test:** 50+ sources through full pipeline (1-6).
**Property tests:**
```
- assert excerpt.self_containment_score >= 0.8
- assert excerpt.attribution.confidence >= 0.7
- assert taxonomy_placement.leaf_id in valid_leaves
- assert every excerpt placed in at least one taxonomy leaf
```
**Your role:** This is where your expertise matters most.
  - Read 50 excerpts across 10 sources. Is each one self-contained?
  - Check 30 attributions. Is each scholar correctly identified?
  - Check 20 taxonomy placements. Is each excerpt in the right topic?
**Exit criteria:** Self-containment ≥95%, attribution ≥95%, placement ≥90% (your verification).

#### Layer 4: Synthesis (~2-3 weeks, most visible to you)

**Build:** Claude Code implements engine 7.
**Test:** Full pipeline end-to-end on 50+ sources.
**Property tests:**
```
- assert entry.language == "ar"
- assert entry.grounding_score >= 0.7
- assert all citations trace to real excerpts
- assert entry does not contain information not in any excerpt
```
**Your role:** READ THE ENTRIES. This is the product. 
  - Read 30 entries across 10 topics
  - Judge: "Would I trust this in my studies?"
  - Judge: "Does this read like scholarly text, not a chatbot summary?"
  - Judge: "Are the opinions correctly attributed to schools?"
**Exit criteria:** You approve 30 entries as study-worthy.

### Phase C: Scale Testing (Claude Code, ~2-4 weeks)

After all layers pass, test at scale:

**Corpus expansion:** 200-500 sources across all genres, sciences, formats.
Claude Code runs the full pipeline on all sources. Automated property tests catch regressions.

**Adversarial testing:** Deliberately difficult sources:
- Damaged OCR (low-quality photo scans)
- Ambiguous authorship (same title, different authors)
- Multi-layer hashiyah with 3+ text layers
- Very short works (pamphlets, single-chapter texts)
- Very long works (15-volume fiqh encyclopedias)
- Mixed-language works (Arabic + some Persian/Turkish)

**Stability testing:** Run LLM-dependent engines 3x on the same source. All property tests must pass all 3 times.

**Your role:** Periodic sampling. Read 10 entries per week from random sources. Flag anything wrong. Claude Code fixes.

**Exit criteria:** 
- 200+ sources processed with zero CRITICAL findings
- You've read 50+ entries and approved them
- All property tests pass on all sources
- 3-run stability test passes on 20 representative sources
- You say: "I trust this pipeline with my library"

### Phase D: Application (after pipeline is trusted)

Only now does the actual application get built. The trusted pipeline becomes a library that the application calls. The application adds:
- Scholar Interface (GUI for querying, browsing, learning)
- Human Gate interface (for your approval of decisions)
- Source acquisition interface (upload/discover sources)
- Spaced repetition / study features

This is a separate plan, designed after the pipeline is trusted.

---

## The Claude Code Setup

Claude Code needs to be configured for this workflow:

### Self-Testing Pattern

Claude Code builds an engine, then immediately tests it:
```bash
# Build task
claude -p "Implement source engine Task 3 (freezer). Read IMPLEMENTATION_ORDER.md."

# Test task (can be same session or new session for fresh context)
claude -p "Run all source engine tests. Fix any failures. 
           Then run the pipeline on test fixtures and verify output."
```

### Agent Team for Testing

```
.claude/agents/
  pipeline-runner.md    — runs sources through the pipeline, produces reports
  quality-checker.md    — analyzes pipeline output against property tests
  finding-tracker.md    — reads OPEN.md findings, verifies fixes, updates status
```

The `pipeline-runner` agent runs sources in batch:
```bash
# In Claude Code:
"Use the pipeline-runner agent to process all sources in test_corpus/sources/.
 Generate a summary report with per-source metrics and flagged items."
```

### Property Test Suite

Claude Code maintains a growing test suite:
```
tests/
  properties/
    test_source_properties.py      # Every source must pass these
    test_normalization_properties.py
    test_passaging_properties.py
    test_atomization_properties.py
    test_excerpting_properties.py
    test_taxonomy_properties.py
    test_synthesis_properties.py
  acceptance/
    test_owner_criteria.py          # Tests from Phase A sessions
  stability/
    test_llm_stability.py          # 3-run consistency check
  regression/
    test_deterministic_regression.py  # Engines 1-4 exact output match
```

### Findings Loop

```
1. Claude Code runs pipeline on source
2. Property tests flag issues → added to test_corpus/findings/OPEN.md
3. Claude Code reads OPEN.md, implements fix
4. Claude Code re-runs source, verifies fix
5. Claude Code marks finding RESOLVED
6. Periodically: re-runs ALL previous sources to check for regressions
```

For findings that need your input:
```
test_corpus/findings/NEEDS_OWNER.md

## F-089: Is this excerpt self-contained?
Excerpt from المغني, topic المبتدأ:
النص: «وهذا القسم الثاني من أقسام المبتدأ...»
Claude Code thinks: self-containment 0.6, unclear if sufficient
Owner: please read and judge — is this usable as a standalone excerpt?
```

You answer in a Claude Chat session. Claude Chat updates the finding.

---

## Timeline

```
Phase A: Owner quality criteria      1-2 sessions   (1 day)
Phase B Layer 1: Source + Norm        2 weeks
Phase B Layer 2: Passage + Atom       1-2 weeks  
Phase B Layer 3: Excerpt + Taxonomy   2-3 weeks
Phase B Layer 4: Synthesis            2-3 weeks
Phase C: Scale testing               2-4 weeks
                                     ─────────────
Total to trusted pipeline:            ~10-14 weeks
Phase D: Application                  ~4-8 weeks after
```

This is longer than the original estimate because it's honest: testing with 200-500 sources and iterating until trust is established takes time. But the result is a pipeline you can actually trust with your scholarship.

---

## What This Means for the Current Autonomous Sessions

The autonomous sessions should continue as-is through all engines. They produce valuable SPECs, contracts, and implementation plans. But after they finish:

1. **Don't do per-engine "zoom" sessions on every engine.** Only do Phase A (2 quality criteria sessions) where you define what "correct" means.

2. **Don't build the scholar interface yet.** Build the pipeline CLI first (engines 1-7 as a testable tool). The scholar interface comes in Phase D.

3. **Claude Code does the heavy lifting in Phase B.** Your involvement is periodic sampling, not every-source deep analysis. Claude Code handles the automated testing and self-fixing loop.

4. **Your scholarly expertise is concentrated where it matters:** defining quality criteria (Phase A), reviewing excerpts and entries (Layers 3-4), and the final "I trust this" judgment (Phase C exit).
