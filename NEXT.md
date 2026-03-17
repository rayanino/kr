# NEXT — Architect re-review of fix session, then Probe 2 transition gate

## Current position: All 15 review findings fixed (14 applied, 1 skipped — Fix Group N model strings invalid for short-name-only field). Pending Architect re-verification.
## What to do: Architect re-runs the review checklist and transition gate.
## Owner action needed: YES — start a new Claude Chat session for Architect review.

---

## Read First (in this order)

1. `reference/AGENT_ARCHITECTURE.md` (334L) — The governing architecture. You will modify §4.1 (quality gate table). Study §2.3 "Adaptation per engine type" to understand the 3 engine profiles (structural/knowledge/hybrid).
2. `reference/SPEC_ADVERSARY_NORMALIZATION.md` (731L) — The adversarial test catalog. You will replace 1 weak case, add ~9 new cases, fix 2 existing cases, and add annotations.
3. `KNOWLEDGE_INTEGRITY.md` (at repo root) — The 7 corruption threats (T-1 through T-7). You need this to expand Build Team agents with threat awareness.
4. `SILENT_FAILURES.md` (at repo root) — The 7 silent failure patterns. Build Team agents need to reference these.
5. `engines/normalization/SPEC.md` (2049L) — You will fix one inconsistency in §5 check 3 (the 70% Arabic character threshold).
6. `reference/DECISION_PLAYBOOK.md` (870L) — You will add name-matching criteria to §1 from scholarly-verifier.md material.
7. All agent files in `.claude/agents/` — You will modify 8 agents and archive 3.

## Fixes — Organized by File

### FIX GROUP A: Architecture (reference/AGENT_ARCHITECTURE.md)

**A1. Fix §4.1 quality gate Sources check for engine type adaptation.**

Current (line ~196):
```
| Sources | Verifier B: web_fetch count ≥ 1 per item | Halt, escalate to Architect |
```

The Sources check assumes knowledge engine behavior (web search). For structural engines (normalization, passaging), Verifier B inspects raw source files, not web pages. This would cause the quality gate to HALT every normalization verification batch because B didn't do web_fetch.

Replace with engine-type-adapted check:
```
| Sources | **Structural engines:** Verifier B raw source pages inspected ≥ 3 per item. **Knowledge engines:** Verifier B web_fetch count ≥ 1 per item. **Hybrid engines:** Both conditions. | Halt, escalate to Architect |
```

### FIX GROUP B: Consolidator (.claude/agents/consolidator.md)

**B1. Update quality gate Sources check to match A1.**

Replace the Sources row in the quality gate table (currently line ~94) with the same engine-type-adapted version from A1.

**B2. Add UNVERIFIABLE to the comparison table.**

Current comparison table (lines ~26-37) handles 4 verdicts: VERIFIED, PLAUSIBLE, FLAG, ESCALATE. Add UNVERIFIABLE as a 5th verdict.

Add these rows to the comparison table:
```
| UNVERIFIABLE | UNVERIFIABLE | **AGREEMENT_UNVERIFIABLE** — consistent lack of evidence |
| VERIFIED | UNVERIFIABLE | **SOFT_DISAGREEMENT** — investigate |
| UNVERIFIABLE | VERIFIED | **SOFT_DISAGREEMENT** — investigate |
| PLAUSIBLE | UNVERIFIABLE | **AGREEMENT_UNCERTAIN** — both lack strong evidence |
| UNVERIFIABLE | PLAUSIBLE | **AGREEMENT_UNCERTAIN** — both lack strong evidence |
| FLAG | UNVERIFIABLE | **SOFT_DISAGREEMENT** — investigate |
| UNVERIFIABLE | FLAG | **SOFT_DISAGREEMENT** — investigate |
```

Add to Step 2 (Handle Agreements):
```
**AGREEMENT_UNVERIFIABLE:** Final verdict = UNVERIFIABLE. Neither verifier found evidence. Not an error — it means the item cannot be independently confirmed.
**AGREEMENT_UNCERTAIN:** Final verdict = PLAUSIBLE. When one says PLAUSIBLE and the other says UNVERIFIABLE, upgrade to PLAUSIBLE (some evidence > no evidence).
```

### FIX GROUP C: Verifier A (.claude/agents/verifier-a.md)

**C1. Add UNVERIFIABLE verdict.**

In the "Produce Verdict" section (Step 4, currently lines ~89-93), add between PLAUSIBLE and FLAG:
```
- **UNVERIFIABLE**: No evidence found either for or against. Cannot confirm or deny. This is distinct from PLAUSIBLE — PLAUSIBLE means weak positive evidence, UNVERIFIABLE means no evidence at all.
```

### FIX GROUP D: Verifier B (.claude/agents/verifier-b.md)

**D1. Add UNVERIFIABLE verdict.**

Same as C1 — add UNVERIFIABLE between PLAUSIBLE and FLAG in Step 4 (currently lines ~86-91):
```
- **UNVERIFIABLE**: Your independent investigation found no evidence either way. No sources confirm, no sources contradict. This is NOT a failure — some items genuinely cannot be independently verified.
```

### FIX GROUP E: Triage Analyst (.claude/agents/triage-analyst.md)

**E1. Add engine-specific check selection guard.**

At the start of Check Group 5 (currently line ~75), add:
```
**IMPORTANT:** Apply ONLY the checks under the engine name matching your current task. Ignore all other engine-specific subsections. If the engine you are triaging does not have a subsection below, skip Check Group 5 entirely — engine-specific checks will be added when that engine is built.
```

**E2. Update model string in frontmatter.**

Change `model: sonnet` to `model: claude-sonnet-4-6`.

### FIX GROUP F: Build-Prober (.claude/agents/build-prober.md)

**F1. Add shared/ to diff scope.**

In Step 1 (lines ~23-35), change the git diff commands to include shared/:
```bash
# If git ref range provided:
git diff $REF_RANGE -- engines/<engine>/ shared/

# If not provided, find session boundary:
git log --oneline engines/<engine>/ shared/ | head -20
# Identify the session's commits, then:
git diff <first_commit>^..<last_commit> -- engines/<engine>/ shared/
```

Also change the file listing commands:
```
- New files created: `git diff --name-status $REF_RANGE -- engines/<engine>/ shared/`
- Test files modified: `git diff --name-status $REF_RANGE -- engines/<engine>/tests/ shared/*/tests/`
```

**F2. Add a CROSS-ENGINE classification.**

In Step 4 (Classify Findings), after the OMISSION classification (lines ~62-64), add:
```
- **CROSS-ENGINE**: Code modifies a file in `shared/` that is consumed by other engines. This requires extra scrutiny: check whether the change is backward-compatible. If the change alters a function signature, return type, or behavior that other engines depend on, it is HIGH severity regardless of whether the normalization engine works correctly.
  - Example: Modifying `shared/human_gate/src/human_gate.py` to add a new parameter that the source engine doesn't pass.
  - Example: Changing validation logic in `shared/validation/` that the source engine tests depend on.
```

**F3. Add adversarial catalog cross-reference.**

In Step 3 (Map Code to SPEC), after item 3 (currently line ~50), add:
```
4. Check adversarial catalog: for this SPEC rule, does `reference/SPEC_ADVERSARY_{engine}.md` have an ADV-NNN case? If yes, verify the implementation would pass it. Quote the ADV case ID.
```

**F4. Update model string in frontmatter.**

Change `model: opus` to `model: claude-opus-4-6`.

### FIX GROUP G: Test Engineer (.claude/agents/test-engineer.md)

This agent is 46 lines — dangerously thin. Expand it to ~120-150 lines. Keep the existing structure but add the missing sections.

**G1. Add threat awareness section.** After "## Principles" (line ~14), add:

```
## Threat Awareness

Before writing tests for any engine, read `KNOWLEDGE_INTEGRITY.md` (at repo root) and identify the 2-3 highest threats for THIS engine. For each identified threat, write at least one test that specifically defends against it.

For the normalization engine:
- T-1 (Silent Text Corruption): Write tests that compare diacritics (tashkeel) between source and output character by character. Test that no Unicode normalization is applied. Test ZWNJ preservation.
- T-2 (Attribution Error): Write tests for layer detection edge cases — bold threshold at exactly 5% and 60%, transition markers inside bold spans, entire-page-bold.
- T-4 (Context Loss): Write tests for footnote separator boundary values (width 79, 80, 100, 101), orphan footnote references, division tree containment.

For other engines: read the engine's SPEC §1 "Purpose" and KNOWLEDGE_INTEGRITY.md to identify which threats apply.
```

**G2. Add adversarial catalog requirement.** After the new threat awareness section, add:

```
## Adversarial Test Cases

Read `reference/SPEC_ADVERSARY_{engine}.md` before writing any tests. Every ADV-NNN case with a "Detection" assertion should have a corresponding pytest test. These cases were specifically designed to catch naive implementations — they are higher priority than generic happy-path tests.

When writing a test from an ADV case, include the ADV ID in the test docstring:
```python
def test_footnote_separator_lower_boundary(self):
    """§4.A.2 Pass 2: ADV-001 — hr width=79 is NOT a footnote separator."""
```
```

**G3. Add Arabic text safety requirements.** Add to Principles:

```
6. **Arabic text safety**: Every test involving Arabic text must explicitly verify diacritics preservation. Use byte-level comparison for texts where preservation is critical. Never use `.lower()`, `.upper()`, or `.strip()` on Arabic text in test assertions. Import and verify NFC normalization is NOT applied.
```

**G4. Add self-review protocol.** Add at the end:

```
## Self-Review (2 rounds)

After writing all tests for a session:
- **Round 1 — SPEC traceability:** For each test function, verify the docstring cites a specific §4 rule AND the test actually exercises that rule (not a different one).
- **Round 2 — Adversarial coverage:** Count how many ADV-NNN cases from the adversarial catalog have corresponding tests. If <50% of applicable ADV cases are covered, write more tests before committing.
```

**G5. Update model string.**

Change `model: sonnet` to `model: claude-sonnet-4-6`.

### FIX GROUP H: Code Reviewer (.claude/agents/code-reviewer.md)

This agent is 72 lines. Expand to ~120-150 lines.

**H1. Add threat awareness.** After "## Workflow" (line ~10), add:

```
## Threat Awareness

Before reviewing code for any engine, read `KNOWLEDGE_INTEGRITY.md` (at repo root). For each reviewed function, identify which corruption threats it defends against (if any). If a function handles Arabic text or metadata and has no threat defense, flag it.

For the normalization engine, the primary threats are:
- T-1 (Silent Text Corruption): Any function that processes Arabic text. Check for: accidental Unicode normalization, `.strip()` on Arabic strings, diacritic-lossy operations, encoding conversions.
- T-2 (Attribution Error): Any function that assigns or detects text layers. Check for: correct threshold values, correct precedence rules, correct enum values.
- T-6 (Metadata Poisoning): Any function that writes metadata downstream. Check for: D-023 compliance (no fields dropped), correct field types, no unvalidated data pass-through.
```

**H2. Add adversarial catalog checklist item.** In "### Test Quality" checklist (line ~39), add:

```
- [ ] Adversarial cases from `reference/SPEC_ADVERSARY_{engine}.md` each have a corresponding test.
- [ ] Each test from an ADV case cites the ADV ID in its docstring.
```

**H3. Add Arabic safety checklist item.** In "### Code Quality" checklist (line ~27), add:

```
- [ ] No `.lower()`, `.upper()`, or `.strip()` called on Arabic text variables.
- [ ] No Unicode normalization (NFC/NFD/NFKC/NFKD) applied to Arabic text.
- [ ] ZWNJ (U+200C) is preserved, not stripped as whitespace.
- [ ] Diacritics in the Unicode Arabic range (U+064B–U+0652, U+0670, U+0640) are never removed.
```

**H4. Add self-review protocol.** Add at the end:

```
## Self-Review

After completing a code review:
- Re-read your findings with the question: "Would a different reviewer, reading the same code, reach the same conclusions?"
- For each finding marked HIGH: verify the SPEC quote is exact (read the SPEC section, don't quote from memory).
- Count: how many SPEC rules were implemented vs how many have tests? If test coverage is below 80%, flag it.
```

**H5. Update model string.**

Change `model: opus` to `model: claude-opus-4-6`.

### FIX GROUP I: Boundary Validator (.claude/agents/boundary-validator.md)

This agent is 52 lines. Expand to ~90-110 lines.

**I1. Add Arabic text integrity check.** In "## What You Check" (after "### Text Integrity" line ~26), add:

```
### Arabic Text Integrity (T-1 defense)
1. For Arabic text that passes between engines: compare Arabic character count between input and output.
2. Compare diacritic character count (U+064B–U+0652, U+0670) between input and output. If counts differ, the boundary has a text corruption bug.
3. Verify ZWNJ (U+200C) characters are preserved across the boundary.
4. Verify no Unicode normalization form change occurred (bytes should be identical for Arabic text that is declared as pass-through).
```

**I2. Add enum compatibility detail.** In "### Contract Compatibility" (after line ~17), add:

```
6. Verify enum string values match exactly. Example: if engine N produces `layer_type: "matn"` and engine N+1 expects `LayerType.MATN = "matn"`, these match. But if engine N produces `"Matn"` (capitalized), it's a silent failure — Pydantic validation will reject it, but only at runtime.
7. For Optional fields: if engine N never produces a field (always None) but engine N+1 requires it (not Optional), that's a latent contract violation — it works until engine N starts producing the field.
```

**I3. Add self-review protocol.** Add at the end:

```
## Self-Review

After completing boundary validation:
- For each PASS verdict: ask "could this boundary silently corrupt Arabic text?" If you haven't explicitly checked Arabic characters, downgrade to INCONCLUSIVE and add the Arabic check.
- For each FAIL verdict: verify the field names are spelled correctly in your report (field name typos in the report itself are confusing).
```

**I4. Update model string.**

Change `model: sonnet` to `model: claude-sonnet-4-6`.

### FIX GROUP J: SPEC Adversary Catalog (reference/SPEC_ADVERSARY_NORMALIZATION.md)

**J1. Replace ADV-022 with a concrete adversarial case.**

Current ADV-022 ("Python str.strip() removing diacritics at string edges") is weak — it explicitly admits its own input doesn't trigger the trap.

Replace the entire ADV-022 entry with:

```
### ADV-022 arabic_trap — Custom whitespace cleanup removing trailing diacritics

**SPEC rule:** "Preserve all diacritics exactly." (§4.A.8) + "Leading/trailing line whitespace trimmed" (§4.A.8)
**Adversarial input:**
```python
# A text-cleaning function that tries to strip "non-letter" characters at string edges:
import re
text = "بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ"
# The last codepoint is kasra (U+0650), a combining character
# A naive cleanup might use:
cleaned = re.sub(r'[^\w\s]+$', '', text)  # Strips "non-word" chars at end
# But \w in Python regex does NOT reliably match Arabic combining marks
# depending on regex flags and locale, this could strip the trailing kasra
```

**Correct behavior:** The trailing kasra on مِ is preserved. The text is byte-identical after whitespace trimming. Only ASCII whitespace (spaces, tabs, newlines) is removed.
**Wrong behavior (naive impl):** A regex-based cleanup function, a custom strip function, or a call to `.rstrip()` with a character class that includes Arabic combining marks, removes the trailing kasra. The text LOOKS identical in many display fonts (kasra is small and often invisible) but the bytes differ.
**Why it matters:** T-1 (Silent Text Corruption). Diacritics at string boundaries are especially vulnerable because they're the characters most likely to be caught by edge-trimming functions. In Quranic text, every diacritic is critical.
**Detection:** Assert byte-level equality: `source_bytes == output_bytes` for all Arabic text after whitespace trimming. Specifically assert U+0650 (kasra) is present as the final combining character.
```

**J2. Fix ADV-023 — remove unsourced 30% statistic.**

In ADV-023 "Why it matters" section, change:
```
Shamela exports sometimes mix digit forms. Missing Arabic-Indic markers means ~30% of footnote references could be orphaned.
```
to:
```
Shamela exports sometimes mix digit forms within the same source. Missing Arabic-Indic markers means an unknown but potentially significant fraction of footnote references could be orphaned — the actual frequency needs corpus measurement.
```

**J3. Fix ADV-025 — correct the analysis and flag SPEC inconsistency.**

In ADV-025, update three sections:

Change "Correct behavior" to:
```
**Correct behavior:** The SPEC originally said `>70%` for the pass condition and `<70%` for the flag condition, leaving exactly 70% undefined — a SPEC gap. After the fix (see K1), the threshold is `≥70%` pass / `<70%` flag. At exactly 70.0%, the page passes.
```

Change "Wrong behavior" to:
```
**Wrong behavior (naive impl):** (a) Uses `> 70%` strictly, leaving exactly 70% in an undefined state. (b) Uses `>= 70%` without updating the flag condition, creating overlap at 70%. (c) Doesn't strip whitespace/punctuation from the denominator.
```

Change "Detection" to:
```
**Detection:** Assert page at 70.0% passes (≥70%). Assert page at 69.9% is flagged (<70%). Assert page at 70.1% passes.
```

**J4. Add T-3 adversarial cases (structural format misclassification).**

Add 2 new cases. Place them after the §4.B section heading (before the existing ADV-035). Add a new section header:

```
## §4.B.2 — Structural Format Auto-Detection (T-3 defense)

### ADV-043 boundary_value — Q&A format detection at exactly 30% threshold

**SPEC rule (§4.B.2):** "Q&A pattern markers (سُئل + فأجاب or مسألة + الجواب) found on 30% or more of sampled pages triggers qa_format classification."
**Adversarial input:** A 20-page sample where exactly 6 pages (30.0%) contain Q&A markers.
**Correct behavior:** 30.0% meets the "30% or more" threshold → classified as qa_format. `structural_format_proposed: "qa_format"`.
**Wrong behavior (naive impl):** Uses `> 30%` (strictly greater than) → 30.0% doesn't trigger → source stays classified as prose, losing the Q&A structure signal.
**Why it matters:** T-3 (Taxonomic Misplacement). Q&A format affects how the taxonomy engine places the source. Missing the classification means fiqh fatwa collections are treated as prose, losing their question-answer structure for downstream processing.
**Detection:** Assert qa_format classification at 30.0%. Assert NO classification at 29.9%.

---

### ADV-044 multi_signal_conflict — Commentary markers and Q&A markers co-occurring

**SPEC rule (§4.B.2):** Structural format auto-detection with precedence rules.
**Adversarial input:** A source where: 35% of pages have Q&A markers (سُئل/فأجاب) AND 25% of pages have commentary markers (bold matn + unbold sharh pattern). The source engine classified it as `commentary`.
**Correct behavior:** Q&A markers exceed the threshold but the source engine's consensus classification is authoritative. The normalizer proposes qa_format but does NOT override. Human gate created. `structural_format_proposed: "qa_format"`, `structural_format: "commentary"` (unchanged per M-31 fix).
**Wrong behavior (naive impl):** (a) Auto-overrides to qa_format without human gate. (b) Ignores Q&A markers because commentary was already classified. (c) Creates two simultaneous proposals.
**Why it matters:** Mixed-format sources exist — a commentary can use Q&A format. Overriding multi-model consensus with a single-engine heuristic is exactly the M-31 bug that Probe 1 caught.
**Detection:** Assert `structural_format` unchanged. Assert `structural_format_proposed` is set. Assert human gate created.
```

**J5. Add adversarial cases for critical uncovered error codes.**

Add 4 new cases. Place them in the appropriate SPEC sections:

After ADV-021 (in §4.A.8 section), add:
```
### ADV-045 silent_corruption — Diacritics drift from Python JSON serializer (NORM_DIACRITICS_DRIFT)

**SPEC rule (§5 check 8):** "Extract all Unicode characters in the Arabic diacritics range (U+064B–U+0652, U+0670, U+0640) from both source and output for each page. If the diacritic character counts differ by even one character, the page fails with NORM_DIACRITICS_DRIFT (fatal)."
**Adversarial input:** Source text:
```
بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ
```
Contains 14 diacritics. A Python JSON library applies NFC normalization during json.dumps(), or a file write utility applies it transparently.
**Correct behavior:** §5 check 8 detects the diacritic count mismatch between source (14) and output (e.g., 13 after NFC drops the superscript alef). NORM_DIACRITICS_DRIFT (fatal) is raised. Normalization aborts.
**Wrong behavior (naive impl):** (a) §5 check 8 is not implemented — diacritics drift goes undetected. (b) Check compares total character count instead of diacritic-specific count — NFC changes can be count-neutral. (c) Check runs but uses NFKC-normalized text for comparison (defeats purpose).
**Why it matters:** T-1 (Silent Text Corruption). This is the primary defense against silent diacritics loss. If check 8 doesn't work, every downstream engine receives corrupted text.
**Detection:** Assert NORM_DIACRITICS_DRIFT is raised when even 1 diacritic differs. Assert normalization aborts (no output written).
```

After ADV-015 (in §4.A.5 section), add:
```
### ADV-046 silent_corruption — Layer fingerprint inversion (NORM_LAYER_FINGERPRINT_INVERSION)

**SPEC rule (§4.B.9):** "If the 'matn' fingerprint has sentence_length.mean > 22 AND connective_frequency > 0.08 AND the 'sharh' layer has sentence_length.mean < 16 AND connective_frequency < 0.06, the inversion signal is strong — trigger human gate review."
**Adversarial input:** Multi-layer source where the layer detection assigned labels backwards. The "matn" layer fingerprint: sentence_length.mean = 28, connective_frequency = 0.11. The "sharh" layer fingerprint: sentence_length.mean = 12, connective_frequency = 0.04.
**Correct behavior:** §4.B.9 detects the inversion signal (matn has sharh-like properties, sharh has matn-like properties). NORM_LAYER_FINGERPRINT_INVERSION (warning) logged. Human gate triggered. Labels NOT auto-corrected.
**Wrong behavior (naive impl):** (a) Fingerprint validation not implemented. (b) Only checks one direction (matn has high values) but not both conditions simultaneously. (c) Auto-corrects labels without human gate.
**Why it matters:** T-2 (Attribution Error). Full layer inversion means EVERY matn excerpt is attributed to the commentator and vice versa. The single highest-impact T-2 failure — corrupts the entire source.
**Detection:** Assert NORM_LAYER_FINGERPRINT_INVERSION is raised. Assert human gate triggered. Assert labels NOT swapped.
```

After ADV-032 (in §7 section), add:
```
### ADV-047 format_edge_case — Atomic write failure and recovery (NORM_WRITE_FAILED / NORM_WRITE_RECOVERY)

**SPEC rule (§4.A.2 Atomic write / Interrupted write recovery):** "If multiple normalized_prev_* directories exist, select the one with the LATEST timestamp."
**Adversarial input:** Simulated state on disk:
- `normalized_tmp_20260317T120000/` exists (contains manifest.json only, no content.jsonl)
- `normalized_prev_20260317T115500/` exists (contains both files, valid)
- `normalized_prev_20260317T110000/` exists (contains both files, valid, older)
- No `normalized/` directory exists.
**Correct behavior:** Recovery validates temp → fails (content.jsonl missing). Selects LATEST prev (T115500, not T110000). Restores from T115500 → `normalized/`. Cleans up temp and all prev directories. Logs NORM_WRITE_RECOVERY (info).
**Wrong behavior (naive impl):** (a) Selects first prev alphabetically or by creation time instead of latest timestamp. (b) Promotes incomplete temp to normalized/. (c) Restores but doesn't clean up — orphaned state remains. (d) Crashes on multiple prev directories.
**Why it matters:** Incorrect recovery promotes a partial package or restores from an older backup.
**Detection:** Assert restored from T115500. Assert temp and both prev cleaned up. Assert NORM_WRITE_RECOVERY logged.

---

### ADV-048 format_edge_case — Windows-1256 encoded Shamela export (NORM_ENCODING_ERROR)

**SPEC rule (§7):** "NORM_ENCODING_ERROR (Warning) — Source uses unrecognized or corrupted encoding. Convert what is possible. Flag affected pages as text_fidelity: 'low'."
**Adversarial input:** A Shamela .htm file saved in Windows-1256 encoding instead of UTF-8. Opening as UTF-8 produces mojibake.
**Correct behavior:** Normalizer detects encoding mismatch. Attempts Windows-1256 → UTF-8 conversion. If successful: NORM_ENCODING_ERROR (warning), affected pages get text_fidelity: "low". If conversion fails: NORM_ENCODING_ERROR with details, human gate triggered.
**Wrong behavior (naive impl):** (a) Opens with encoding='utf-8' and crashes. (b) Opens with errors='ignore' — silently drops non-ASCII. (c) Opens with errors='replace' — replaces Arabic with U+FFFD.
**Why it matters:** T-1 (Silent Text Corruption). Windows-1256 is a real encoding used by older Shamela versions.
**Detection:** Assert NORM_ENCODING_ERROR logged. Assert Arabic text correctly converted. Assert text_fidelity downgraded.
```

**J6. Add cases for §4.A.7 and §4.A.9 to reach 3-case minimum.**

After ADV-020 (in §4.A.7 section), add:
```
### ADV-049 boundary_value — Page number integer overflow from corrupt Shamela HTML

**SPEC rule (§4.A.7):** "Extract page numbers from `<span class='PageNumber'>(ص: N)</span>`."
**Adversarial input:**
```html
<div class='PageText'>
<span class='PageNumber'>(ص: 999999999999999999999)</span>
حدثنا أبو بكر
</div>
```
**Correct behavior:** Page number stored as string in page_number_display. page_number_int may be null (unparseable for downstream) or the large integer if supported. Content unit created with valid unit_index. No crash.
**Wrong behavior (naive impl):** JSON schema uses 32-bit integer causing overflow. Or page number used in arithmetic that overflows.
**Why it matters:** Corrupt Shamela HTML exists. The normalizer must never crash on unexpected page number values.
**Detection:** Assert content unit created. Assert no crash. Assert unit_index valid.
```

After ADV-024 (in §4.A.9 section), add:
```
### ADV-050 arabic_trap — Hadith citation with non-standard introduction

**SPEC rule (§4.A.9):** "Hadith citation markers detected."
**Adversarial input:**
```
أخبرنا أبو بكر محمد بن الحسين عن عبد الله بن مسعود رضي الله عنه قال: قال رسول الله ﷺ: «إنما الأعمال بالنيات»
```
**Correct behavior:** The isnad chain (أخبرنا...عن...قال: قال رسول الله) detected as hadith citation. has_hadith_citation: true.
**Wrong behavior (naive impl):** Only detects "حدثنا" as hadith marker, misses "أخبرنا" (both are hadith transmission verbs with identical function).
**Why it matters:** Hadith citations need special downstream treatment. Missing them means hadith text is treated as the author's own words.
**Detection:** Assert has_hadith_citation: true. Assert detection covers أخبرنا, حدثنا, أنبأنا transmission forms.

---

### ADV-051 format_edge_case — Table of contents page detection

**SPEC rule (§4.A.9):** Content flags include is_toc_page.
**Adversarial input:**
```
فهرس الكتاب
باب الطهارة ............... ١٢
باب الصلاة ............... ٤٥
باب الزكاة ............... ٨٩
باب الصيام ............... ١٢٣
```
**Correct behavior:** Page flagged as is_toc_page: true. Leader dots + page numbers + "فهرس" keyword identify it as TOC.
**Wrong behavior (naive impl):** (a) Only checks "فهرس" keyword without leader-dots pattern — false positive on pages mentioning "فهرس". (b) Detects as TOC but also detects structural headings (باب) from TOC entries, creating phantom divisions.
**Why it matters:** TOC pages should not generate structural divisions — they're metadata about the structure, not structure itself. Phantom divisions from TOC entries double every entry in the division tree.
**Detection:** Assert is_toc_page: true. Assert no structural heading detections from TOC entry text.
```

**J7. Add deferred annotation for §4.B cases.**

Add a blockquote before ADV-035 (around current line ~609):
```
> **NOTE:** §4.B test cases (ADV-035 through ADV-042) target transformative capabilities that are deferred from core build. Implement these tests when the corresponding §4.B capabilities are built. They are included here for completeness and to guide future build sessions.
```

**J8. Add coverage gap documentation.**

After the header metadata (after line 9, before the first section), add:
```
**Coverage gaps (deferred normalizers):** Sections §4.A.3 (PDF text normalizer), §4.A.4 (scanned PDF/image normalizer), §4.A.4a–§4.A.4d (EPUB, Word, plain text, owner content normalizers) are marked [NOT YET IMPLEMENTED] in the SPEC. No adversarial cases are provided for these sections. Write adversarial cases when each normalizer is implemented.
```

**J9. Update the Summary by Threat table and header counts.**

Replace the Summary by Threat table with:
```
| Threat | Adversarial Cases | Key Tests |
|--------|------------------|-----------|
| T-1 (Silent Text Corruption) | ADV-006, ADV-007, ADV-021, ADV-022, ADV-039, ADV-045, ADV-048 | Diacritics, ZWNJ, NFC, entity corruption, semantic confusion, drift detection, encoding |
| T-2 (Attribution Error) | ADV-011, ADV-012, ADV-013, ADV-014, ADV-015, ADV-046 | Bold threshold, multi-signal, layer coverage, metadata override, fingerprint inversion |
| T-3 (Taxonomic Misplacement) | ADV-043, ADV-044 | Format detection threshold, competing format signals |
| T-4 (Context Loss) | ADV-001, ADV-002, ADV-017, ADV-019 | Footnote separator, division tree, unit_index gaps |
| T-5 (Synthesis Hallucination) | ADV-010, ADV-030 | PageHead leak, OCR empty-success |
| T-6 (Metadata Poisoning) | ADV-033, ADV-034, ADV-035 | Manifest count, marker format, cross-validation |
| T-7 (Duplication) | ADV-018, ADV-020 | Duplicate headings, duplicate page numbers |
```

Update header counts to match actual totals after all additions. Verify by counting `### ADV-` lines.

### FIX GROUP K: Normalization SPEC (engines/normalization/SPEC.md)

**K1. Fix §5 check 3 threshold inconsistency.**

In §5 check 3 (line 1483), change:
```
Character distribution must be plausible for Arabic text: >70% Arabic characters (excluding whitespace and punctuation). A page with <70% Arabic characters is flagged as potentially corrupted.
```
to:
```
Character distribution must be plausible for Arabic text: ≥70% Arabic characters (excluding whitespace and punctuation). A page with <70% Arabic characters is flagged as potentially corrupted.
```

This closes the gap at exactly 70%: ≥70% passes, <70% is flagged.

### FIX GROUP L: Decision Playbook (reference/DECISION_PLAYBOOK.md)

**L1. Add Arabic name matching criteria to §1.**

After the existing content in §1 (Author Attribution), before §2, add:

```
### 1.5 Arabic Name Matching Criteria

These rules define when two Arabic names refer to the same person vs. different people. Used during evaluation and verification.

**MATCH (same person):**
- Shorter/longer form of the same name (e.g., "ابن تيمية" vs "أحمد بن عبد الحليم بن تيمية")
- Kunyah vs ism (e.g., "أبو حنيفة" vs "النعمان بن ثابت")
- With/without nisbah or laqab (e.g., "الشافعي" vs "محمد بن إدريس")
- Death date differs by ≤10 years (allows for hijri/miladi conversion uncertainty and source disagreement)

**MISMATCH (different person):**
- Completely different person sharing a common element (e.g., two scholars both called "ابن عبد البر")
- Compiler confused with author (e.g., modern editor listed as author of a classical text)
- Sharh author confused with matn author (e.g., النووي listed as author of صحيح مسلم)
- Father confused with son (e.g., ابن حجر العسقلاني vs his father)
- Death date differs by >30 years (strong signal of different person, unless one date is known to be disputed)

**Source:** Extracted from scholarly-verifier.md evaluation criteria, validated across 204 source engine evaluations.
```

### FIX GROUP M: Legacy Agent Cleanup

**M1. Create archive directory and move legacy agents.**

```bash
mkdir -p .claude/agents/archived
mv .claude/agents/researcher.md .claude/agents/archived/researcher.md
mv .claude/agents/result-analyst.md .claude/agents/archived/result-analyst.md
mv .claude/agents/scholarly-verifier.md .claude/agents/archived/scholarly-verifier.md
```

**M2. Rename integrity-checker.md.**

```bash
mv .claude/agents/integrity-checker.md .claude/agents/library-integrity-checker.md
```

Then update the `name:` field in the frontmatter from `integrity-checker` to `library-integrity-checker`.

### FIX GROUP N: Model Strings (batch update all remaining agent frontmatters)

Update every remaining agent file:
- Every `model: opus` → `model: claude-opus-4-6`
- Every `model: sonnet` → `model: claude-sonnet-4-6`

Files to update (excluding those already changed in E2/G5/H5/I4/F4): spec-auditor-a.md, spec-auditor-b.md, audit-comparator.md, deep-researcher.md, spec-writer.md, integrity-auditor.md, spec-adversary.md, verdict-adversary.md, verifier-a.md, verifier-b.md, consolidator.md, library-integrity-checker.md (after M2 rename).

### FIX GROUP O: Track "14 required fields" for Probe 3

Add to the bottom of `reference/AGENT_ARCHITECTURE.md`, after §9:

```
---

## 10. Open Items

### 10.1 Verdict Field Enumeration (MUST-FIX before Probe 3)

The quality gate (§4.1) references "14 required fields" in each verdict but does not enumerate them. Before Probe 3 (Verification Team), define these fields explicitly. Proposed list (to be validated against actual verification output during Probe 2):

1. item_id
2. verdict (VERIFIED / PLAUSIBLE / UNVERIFIABLE / FLAG / ESCALATE)
3. confidence (0.0–1.0)
4. evidence (array of specific evidence points)
5. source_pages_inspected (array of unit_index values, for structural engines)
6. web_sources (array of URLs, for knowledge engines)
7. reasoning_chain (array of reasoning steps)
8. playbook_rules_applied (Verifier A only; null for Verifier B)
9. playbook_influence (Verifier A only; null for Verifier B)
10. novel_observations (Verifier B only; null for Verifier A)
11. triage_risk (LOW / MEDIUM / HIGH, from Triage Analyst)
12. engine_name
13. batch_number
14. verifier_id (verifier_a or verifier_b)

This list is a PROPOSAL. Finalize during Probe 2 build prep, before Probe 3 begins.
```

---

## Do NOT Do

- Do NOT start building the normalization engine. This session is fixes only.
- Do NOT modify any engine source code (engines/*/src/). Only agent definitions, reference docs, and SPEC text.
- Do NOT modify engines/normalization/contracts.py. The §9.1 contract alignment items are for the build session.
- Do NOT renumber existing ADV cases. New cases get new numbers (ADV-043 through ADV-051).
- Do NOT modify the Playbook beyond adding §1.5 (name matching). The Playbook is well-established and should not be restructured.
- Do NOT merge or restructure agents. The architecture's 18-agent count is intentional per P5.

## Verification

After all fixes, run these 13 checks. ALL must pass.

```bash
# 1. All architecture agents exist (16 architecture + library-integrity-checker = 17)
ls .claude/agents/*.md | wc -l
# Expected: 17

# 2. No legacy agents remain in main directory
ls .claude/agents/researcher.md .claude/agents/result-analyst.md .claude/agents/scholarly-verifier.md 2>/dev/null
# Expected: "No such file" errors only

# 3. Archived agents exist
ls .claude/agents/archived/
# Expected: researcher.md, result-analyst.md, scholarly-verifier.md

# 4. Model strings updated — no plain "opus" or "sonnet" remaining
grep -l "^model: opus$\|^model: sonnet$" .claude/agents/*.md
# Expected: no output (empty)

# 5. Adversarial catalog case count
grep -c "^### ADV-" reference/SPEC_ADVERSARY_NORMALIZATION.md
# Expected: 51

# 6. SPEC 70% fix applied
grep "≥70%" engines/normalization/SPEC.md
# Expected: 1 line containing the fixed threshold

# 7. Playbook §1.5 exists
grep "### 1.5 Arabic Name Matching" reference/DECISION_PLAYBOOK.md
# Expected: 1 line

# 8. Architecture §10 exists
grep "## 10. Open Items" reference/AGENT_ARCHITECTURE.md
# Expected: 1 line

# 9. Build-prober includes shared/ in scope
grep "shared/" .claude/agents/build-prober.md
# Expected: multiple lines

# 10. Consolidator has UNVERIFIABLE in comparison table
grep "UNVERIFIABLE" .claude/agents/consolidator.md
# Expected: multiple lines

# 11. Quality gate has engine-type-adapted Sources check
grep "Structural engines" .claude/agents/consolidator.md
grep "Structural engines" reference/AGENT_ARCHITECTURE.md
# Expected: 1+ lines each

# 12. Test engineer references adversarial catalog
grep "SPEC_ADVERSARY" .claude/agents/test-engineer.md
# Expected: 1+ lines

# 13. Code reviewer has Arabic safety checklist
grep "U+064B" .claude/agents/code-reviewer.md
# Expected: 1+ lines
```

Run ALL 13 checks. If any fails, investigate and fix before committing.

## Self-Review Protocol

After completing all fixes, do a 3-round self-review:

**Round 1 — Completeness:** Re-read this NEXT.md. For each fix group (A through O), verify you did it. Check off each one.

**Round 2 — Consistency:** Read the modified agents as a SET. Do verifier-a and verifier-b verdict scales match? Does the consolidator's comparison table handle all verdict combinations? Does the quality gate in the architecture match the quality gate in the consolidator? Does the build-prober's scope match what it claims to check?

**Round 3 — Adversarial catalog integrity:** Read the full adversarial catalog from top to bottom. Do the new cases (ADV-043 through ADV-051) follow the same format as existing cases? Are the ADV numbers sequential with no gaps? Are the category tags correct? Does the Summary by Threat table include all new cases? Do the header counts match the actual case count?

## Commit Message

```
fix: 15 architect review findings — quality gate, Build Team agents, adversarial catalog, SPEC threshold

Architecture: engine-type-adapted Sources quality gate (structural/knowledge/hybrid)
Agents: expanded test-engineer, code-reviewer, boundary-validator with threat awareness
  + adversarial catalog connection. Added UNVERIFIABLE verdict to verifiers + consolidator.
  Build-prober scope includes shared/. Model strings updated to exact versions.
Adversarial catalog: replaced weak ADV-022, added ADV-043—051 (9 new cases, 51 total).
  Added T-3 coverage, critical error code coverage, deferred annotations.
SPEC: fixed §5 check 3 threshold gap (>70% → ≥70%).
Playbook: added §1.5 Arabic name matching criteria.
Legacy agents: archived 3, renamed integrity-checker → library-integrity-checker.
Tracked: 14 required verdict fields as MUST-FIX for Probe 3 (§10).
```

## After This

Update NEXT.md to:
```
# NEXT — Architect re-review of fix session, then Probe 2 transition gate

## Current position: All 15 review findings fixed. Pending Architect re-verification.
## What to do: Architect re-runs the review checklist and transition gate.
## Owner action needed: YES — start a new Claude Chat session for Architect review.
```

The Architect will then re-verify every finding is fixed, re-run the transition gate, and write the actual Probe 2 build directive.
