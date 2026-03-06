# Pipeline Stress Testing — اختبار الأنبوب

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌───────────────┐
│ Claude Code  │ builds  │   Pipeline   │ writes  │  test_corpus/  │
│ (persistent) │────────>│   CLI tool   │────────>│   results/     │
│              │ fixes   │              │         │   findings/    │
│              │<────────│              │         │                │
└─────────────┘         └──────────────┘         └───────┬───────┘
                                                         │ git push
                                                         │
                                                    ┌────┴────────┐
                                                    │    GitHub    │
                                                    │     repo    │
                                                    └────┬────────┘
                                                         │ git pull
                                                         │
┌─────────────┐  reads results  ┌───────────────┐       │
│   Owner     │<───────────────>│  Claude Chat   │<──────┘
│ (scholar)   │  discusses      │  (ephemeral)   │
│             │  judges quality │  reads reports  │
│             │                 │  writes findings│──> git push
└─────────────┘                 └───────────────┘
```

**Claude Code** runs the pipeline (persistent environment, has filesystem, runs for hours).
**Claude Chat** reads results and analyzes with the owner (ephemeral, reads from repo).
**The repo** is the communication channel between them.

---

## The Communication Protocol

### Claude Code → Claude Chat (results)

After running a source through the pipeline, Claude Code commits:

```
test_corpus/
└── results/
    └── {source_slug}/
        └── {run_id}/
            ├── meta.json           # Run metadata
            ├── source_report.md    # Human-readable, Arabic content preserved
            ├── normalization_report.md
            ├── passaging_report.md
            ├── atomization_report.md
            ├── excerpting_report.md
            ├── taxonomy_report.md
            ├── synthesis_report.md
            ├── summary.md          # One-page overview of all stages
            └── machine/            # Raw JSON (for regression testing)
                ├── source.json
                ├── normalization/
                ├── excerpts.jsonl
                └── ...
```

Reports are **markdown files with Arabic text preserved**. Field labels in English, scholarly content in Arabic. Example:

```markdown
## المصدر: شرح ابن عقيل على ألفية ابن مالك

### المؤلف (Author)
ابن عقيل — بهاء الدين عبد الله بن عقيل الهمداني المصري (ت ٧٦٩ هـ)
Confidence: 0.95 ✓

### النوع (Genre)
شرح (sharh) — commentary on ألفية ابن مالك by ابن مالك
Confidence: 0.97 ✓

### العلم (Science)
نحو (nahw — Arabic grammar)

### مقتطف رقم ٤٧ (Excerpt #47)
#### الموضوع: المبتدأ والخبر

قال ابن مالك: والمبتدأ اسم ابتداءً وُضِعا ... لفاعل كزيدُ عُدْ ومُخبَراً عنه كـ «زيد ذو جلا»

قال ابن عقيل: المبتدأ في الاصطلاح: هو الاسم المجرد عن العوامل اللفظية
غير الزائدة، المسند إليه خبر أو وصف رافع لمستغنى به.

**Layer:** شرح (commentary by ابن عقيل on متن by ابن مالك)
**Self-containment:** ✓ PASS
**Evidence type:** قاعدة نحوية (grammatical rule)
```

### Claude Chat → Claude Code (findings)

Claude Chat (with the owner) writes findings as structured markdown committed to the repo:

```
test_corpus/
└── findings/
    └── {source_slug}/
        ├── status.json             # Which findings are open/fixed
        ├── F001_wrong_author.md
        ├── F002_broken_isnad.md
        └── ...
```

Each finding follows a template:

```markdown
# Finding F001: Wrong author identification

**Source:** شرح ابن عقيل على ألفية ابن مالك
**Stage:** source
**Severity:** critical
**Status:** open

## What happened
The source engine identified the author as ابن مالك instead of ابن عقيل.
The title contains both names — the engine picked the wrong one.

## Expected
Author should be ابن عقيل (the commentator), not ابن مالك (the original author).
ابن مالك wrote the ألفية; ابن عقيل wrote the شرح.

## Root cause
§4.A.4 metadata inference: the LLM prompt doesn't distinguish between
the author of a sharh and the author of the underlying matn.

## Suggested fix
The metadata inference prompt needs to be aware of genre_chain.
When the genre is "sharh", the author is the commentator, not the matn author.
The matn author goes into work_relationships as the base_work_author.

## Reproduction
Run: kr-pipeline run test_corpus/sources/ibn_aqil_sharh/
Check: source_report.md → المؤلف section
```

Claude Code reads these findings and implements fixes. After fixing, it re-runs the source and commits updated results. Claude Chat verifies the fix in the next analysis session.

---

## Session Types

### PIPELINE_RUN (Claude Code)

Claude Code runs one or more sources through the pipeline:

```bash
# Single source
kr-pipeline run test_corpus/sources/ibn_aqil_sharh/ \
  --output test_corpus/results/ibn_aqil_sharh/run_001/

# Regression: re-run all previously tested sources
kr-pipeline regression --compare-with-previous

# Fix findings then re-run
kr-pipeline run test_corpus/sources/ibn_aqil_sharh/ \
  --output test_corpus/results/ibn_aqil_sharh/run_002/
```

Then commits results and pushes.

### STRESS_TEST (Claude Chat + Owner)

Claude Chat pulls the repo, reads the reports, and analyzes with the owner:

1. **Pull:** `git pull` to get latest results
2. **Read summary:** `test_corpus/results/{source}/latest/summary.md`
3. **Stage-by-stage analysis** (together with owner):
   - Source: Is the author correct? Genre? Trust evaluation?
   - Normalization: Is text preserved? Layers detected? Footnotes separated?
   - Excerpting: Are excerpts self-contained? Attributions correct?
   - Synthesis: Would you trust this entry in your studies?
4. **Write findings:** For each issue found, create a finding file
5. **Commit findings:** Push to repo for Claude Code to read

### FIX_CYCLE (Claude Code)

Claude Code reads open findings and implements fixes:

1. Read `test_corpus/findings/{source}/status.json` for open findings
2. Read each finding's `.md` file for root cause and suggested fix
3. Implement the fix in the engine code
4. Re-run the source: `kr-pipeline run ...`
5. Verify the finding is resolved in the new results
6. Run regression: `kr-pipeline regression` to ensure no other sources broke
7. Update `status.json`: mark finding as `fixed`
8. Commit and push

---

## Regression Testing

Runs entirely in Claude Code's environment (persistent, can handle hours-long jobs).

```bash
# After every fix, verify nothing broke
kr-pipeline regression

# Output:
# ✓ ibn_aqil_sharh: 47 excerpts, 0 regressions
# ✓ mughni_ibn_qudamah: 312 excerpts, 0 regressions
# ✗ waraqat_juwayni: REGRESSION — excerpt #12 self-containment dropped 0.95→0.71
#   Diff: test_corpus/results/waraqat/run_003/vs_run_002.diff
```

Regression is checked by comparing machine output (JSON) between runs. A regression is: any field value that changed when it shouldn't have, any new error that didn't exist before, any quality metric that decreased.

---

## Source Files

Test sources live in `test_corpus/sources/` in the repo (or in a separate `kr-test-data` repo if files are too large for the main repo).

For large sources (PDFs, photo sets), the owner provides them and Claude Code places them in the correct directory. For Shamela HTML exports, they can live directly in the repo (small text files).

```
test_corpus/
├── sources/
│   ├── ibn_aqil_sharh/          # Shamela HTML export
│   │   └── shamela_export/
│   ├── mughni_ibn_qudamah/      # PDF
│   │   └── mughni_v1.pdf
│   ├── waraqat_juwayni/         # Photo scans
│   │   └── photos/
│   └── registry.json            # Master list of all test sources
├── results/                     # Pipeline output (committed by Claude Code)
├── findings/                    # Issues found (committed by Claude Chat)
└── README.md                    # How to add sources, run tests, read results
```

---

## The Owner's Role

You are the scholarly quality gate. Claude Chat can check structural things (schema compliance, metadata preservation, self-containment scores). But ONLY you can judge:

- Is this attribution correct? (ابن عقيل vs ابن مالك)
- Is this excerpt self-contained enough to study from?
- Does this synthesized entry read like scholarly text?
- Would you trust this in your actual studies?
- Is this the right taxonomy placement for this content?

Your input is the most valuable signal in the entire system. A pipeline that passes all automated checks but produces entries you wouldn't study from is a failed pipeline.

---

## What "Done" Looks Like

### Pipeline Trust Criteria

The stress testing phase ends when ALL of these are true:

**Correctness (0 tolerance for errors in user's knowledge):**
- [ ] 50+ sources processed without fatal errors
- [ ] 0 author misattributions across all tested sources
- [ ] 0 text corruptions detected (Arabic text byte-for-byte correct)
- [ ] 0 school misclassifications (Hanbali opinion never attributed to Shafi'i)

**Quality (owner-verified):**
- [ ] Owner has read 20+ synthesized entries and considers them study-worthy
- [ ] Owner has verified 50+ excerpt attributions and found 0 errors
- [ ] Multi-layer detection correct for sharh/matn/hashiyah in 10+ test cases

**Robustness (automated):**
- [ ] Full regression passes on all 50+ sources after any code change
- [ ] Deliberately malformed input produces clear errors, not silent corruption
- [ ] Pipeline produces deterministic output (same input → same output)

**Owner trust (the ultimate gate):**
- [ ] Owner says: "I would trust this pipeline with my actual study library"
