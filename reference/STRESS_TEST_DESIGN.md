# Pipeline Stress Testing Phase — Revised Design (v2)

Addresses 8 gaps found in the original design.

---

## Gap 1: Pipeline runs need API keys in Claude Chat's container

**Problem:** Each Claude Chat session starts fresh. The pipeline needs LLM API calls.

**Solution:** Owner creates an `API_KEYS` knowledge file in the Claude Chat project (same pattern as `Github_key`). Claude Chat writes them to `.env` at session start. Alternatively: engines 1-4 (source → atomization) need zero LLM calls and can be stress-tested without keys. Only engines 5-7 need them.

---

## Gap 2: Context window fills when reading 200+ excerpt reports

**Problem:** A source might produce 200 excerpts. Claude Chat can't deeply analyze all of them.

**Solution:** Layered analysis with smart sampling.

**Layer 1: Automated metrics** — Claude Chat reads summary numbers, not full text:
```
Excerpts: 247 total
Self-containment: 231 pass (93.5%), 16 flagged
Attribution confidence: mean 0.91, min 0.42
Taxonomy placement: 198 confident, 49 needs-review
```

**Layer 2: Targeted deep analysis** — Claude Chat reads Arabic text for the 16 flagged items only. Fits in context.

**Layer 3: Random sampling** — Owner spot-checks 5-10 random non-flagged excerpts directly.

Total context cost: ~23K tokens (metrics + flagged + samples). Manageable.

---

## Gap 3: Claude Chat → Claude Code feedback loop

**Problem:** How does a stress test finding become a Claude Code fix?

**Solution:** Structured findings file in the repo.

```markdown
# test_corpus/findings/OPEN.md

## F-047: Passaging breaks isnad chain in hadith text
- **Source:** sahih_bukhari_vol1
- **Stage:** passaging  
- **Severity:** CRITICAL
- **What happened:** Passage boundary placed between narrator chain and matn
- **Expected:** Isnad chain and its matn must be in the same passage
- **Root cause:** §4.A.3 boundary rules don't detect isnad patterns (حدثنا, أخبرنا, عن)
- **Fix needed:** Add isnad chain detection to passage boundary rules
- **SPEC section:** engines/passaging/SPEC.md §4.A.3
- **Status:** OPEN
```

Claude Code's NEXT.md references OPEN.md. After fixing, Claude Code marks findings RESOLVED with commit hash. Next stress test session verifies the fix.

---

## Gap 4: LLM non-determinism breaks regression testing

**Problem:** Engines 5-7 use LLMs. Same input → different output each run.

**Research finding:** Even temperature=0 with fixed seeds doesn't guarantee identical output. "Design your application to be robust to minor variations."

**Solution:** Two-tier testing.

**Tier 1 (deterministic engines 1-4):** Traditional regression. Assert output == gold baseline, field-for-field.

**Tier 2 (LLM engines 5-7):** Test PROPERTIES, not exact output:
```python
def test_excerpt_properties(excerpt):
    assert excerpt.self_containment_score >= 0.8
    assert excerpt.attribution.confidence >= 0.7
    assert excerpt.primary_text_preserved  # Arabic bytes unchanged
    assert len(excerpt.text) >= 50
```

**Stability test:** Run same source 3 times. Property tests must pass all 3 times. Exact text may differ but quality properties must be stable.

---

## Gap 5: 50+ sources can't live in git

**Solution:** Sources stored locally on owner's machine, referenced by manifest in git.

```json
// test_corpus/manifest.json (in git, small)
{
  "sources": [{
    "id": "ibn_aqil_sharh",
    "title_ar": "شرح ابن عقيل على ألفية ابن مالك",
    "format": "shamela_html",
    "genre": "sharh",
    "science": "nahw",
    "local_path": "~/kr-test-corpus/sources/ibn_aqil_sharh/",
    "status": "tested_v3",
    "finding_count": 2
  }]
}
```

Pipeline CLI resolves local paths. Owner copies sources into Claude Chat's container when needed.

---

## Gap 6: How does the owner actually participate?

**Solution:** Claude Chat presents Arabic text inline in the conversation.

```
Claude Chat: "شرح ابن عقيل produced 247 excerpts. 16 flagged. Here's the worst:"

   Excerpt #34 (self-containment: 0.3):
   النص: «وهذا القسم الثاني من أقسام المبتدأ وهو ما كان وصفاً...»
   المشكلة: Starts mid-argument. "القسم الثاني" references previous excerpt.

Owner: "You're right. Also check #35 — topic should be خبر المبتدأ not المبتدأ"
```

Arabic stays Arabic. English for system annotations only. Claude Chat reads and evaluates Arabic; owner brings scholarly judgment. Together they catch both mechanical and scholarly errors.

---

## Gap 7: Per-engine graduation criteria

**Solution:** Each engine has a trust scorecard with specific thresholds.

```
Source Engine:          47/50 tested, 100% author accuracy     → TRUSTED ✓
Normalization Engine:   47/50 tested, 80.9% layer detection    → NEEDS WORK
Passaging Engine:       42/50 tested, 97% boundary accuracy    → TRUSTED ✓  
Atomization Engine:     42/50 tested, 95% type accuracy        → TRUSTED ✓
Excerpting Engine:      35/50 tested, 89.3% attribution        → NEEDS WORK
Taxonomy Engine:        35/50 tested, 91% placement accuracy   → NEEDS WORK
Synthesis Engine:       30/50 tested, owner approved 18/20     → NEEDS WORK
```

An engine graduates when ALL metrics meet targets across ALL tested sources. Pipeline graduates when ALL engines are TRUSTED.

---

## Gap 8: Fix prioritization

**Severity classification:**

- **CRITICAL** (fix before testing next source): knowledge corruption, pipeline crash, data loss
- **HIGH** (fix before engine graduates): quality below threshold, systematic pattern (3+ sources), scholarly misleading
- **MEDIUM** (fix when convenient): edge cases, cosmetic quality, missing capability
- **LOW** (log for future): performance, minor metadata, enhancements

**Rule:** Never test next source until CRITICAL findings are fixed. HIGH findings batched every 5 sources.

---

## Revised Flow

```
Per source:
  1. Owner provides source file
  2. Claude Chat runs pipeline, reads summary metrics
  3. Claude Chat analyzes flagged items (Arabic in conversation)
  4. Owner spot-checks 5-10 random excerpts
  5. Log findings with severity
  6. CRITICAL → Claude Code fix → re-run
  7. Next source

Every 10 sources:
  - Review engine trust scorecards
  - Batch-fix HIGH findings  
  - Re-run all previous sources (deterministic engines only)
  - Stability test on LLM engines (3 runs, all properties pass)

After 50 sources:
  - All scorecards at TRUSTED
  - Owner has read 50+ entries, judges study-worthy
  - Full corpus re-run: zero CRITICAL/HIGH
  → PIPELINE TRUSTED → Phase 4 (application)
```
