# Session 14 — Coworker Verification Prompts

**Date:** 2026-04-07
**Purpose:** Independent verification of all Session 14 deliverables before building further.
**Sources:** Codex CLI (structural) + Gemini CLI (scholarly) + 2 CC agents (preliminary)

---

## Codex CLI Verification Prompt

**Run with:** `codex exec` (from repo root on branch `excerpting-foundations-hardening-20260404`)

**Focus:** Structural soundness of 3 new Python scripts + SPEC edit consistency

```
You are verifying 3 new Python scripts and 2 document edits from Session 14 of the KR project. Your role is structural verification ONLY — you have no Arabic text understanding.

FILES TO REVIEW:

1. scripts/autonomous_schemas.py — Pydantic data models for JSONL persistence
2. scripts/research_gap_scanner.py — codebase scanner for research gaps
3. scripts/process_dr_response.py — DR response parser + finding extractor
4. engines/excerpting/SPEC.md — diff only (git diff engines/excerpting/SPEC.md)
5. docs/autonomous-system/reviews/DR33_claude_research_prioritization_strategy.md — diff only

STRUCTURAL CHECKS (do ALL of these):

A. Schema Design (autonomous_schemas.py):
   - Are the 10 Pydantic models internally consistent? (e.g., DRPrompt.status enum matches DRPromptStatus values)
   - Is the model_validator on DRPrompt safe? (what if prompt_text is empty?)
   - Does read_jsonl handle: empty file, file with only whitespace lines, file doesn't exist?
   - Does append_jsonl create parent dirs atomically? (concurrent writes?)
   - Is load_dr_index's isinstance filter correct after model_validate_json?

B. Gap Scanner (research_gap_scanner.py):
   - Regex for [OPEN: ...] — does it handle: nested brackets? multiple [OPEN] on one line? [OPEN] without colon?
   - Regex for L-XXX — does it match L-001 but not L-1 or L-0001?
   - scan_taxonomy_gaps — is checking for "_v0_" or "_v1_" in filename reliable? What about "v10"?
   - What happens if ENGINES_DIR doesn't exist?
   - Does the scanner overwrite or append to output file?

C. Response Processor (process_dr_response.py):
   - extract_sections — what happens with ### headings (h3)? Are they nested under the last ##?
   - detect_actionable_findings — splitting on [.!?]\s+ fails for: abbreviations (e.g., "Dr. Smith"), numbered lists (1.), URLs
   - classify_severity — is the keyword order deterministic? (what if text contains both "critical" and "should"?)
   - Is finding_id guaranteed unique across multiple runs?

D. SPEC Edits (diff):
   - Are all [OPEN] → [CALIBRATED] changes self-contained? (no dangling references to old markers elsewhere)
   - Does the anti-premature-hardening preamble still accurately describe the state?
   - Are the table formats consistent with existing SPEC tables?

E. DR33 Amendments:
   - Do the Python code blocks in AMD-1 through AMD-6 parse correctly?
   - Are the amended allocation percentages (35+18+28+12+7) equal to 100%?
   - Is the dependency chain in AMD-1 consistent with the original DEPENDENCIES list?

OUTPUT FORMAT:
For each finding:
- SEVERITY: CRITICAL / HIGH / MEDIUM / LOW
- FILE: path
- FINDING: description
- FIX: what to change

End with: VERDICT (PASS / PASS_WITH_ISSUES / FAIL) and confidence level.
```

---

## Gemini CLI Verification Prompt

**Run with:** `gemini -p` (from repo root on branch `excerpting-foundations-hardening-20260404`)

**Focus:** Scholarly accuracy of OQ calibrations + Batch 2 DR prompt quality

```
You are an expert in classical Islamic jurisprudence (fiqh), Arabic rhetoric (balagha), and Islamic scholarly methodology. You are verifying the scholarly accuracy of changes made to a text excerpting engine's specification.

READ THESE FILES:
1. engines/excerpting/SPEC.md — sections §6.18 through §6.23 (search for "§6.18" to find the start)
2. docs/autonomous-system/dr_relay_queue_batch_2.md — 10 DR prompts for taxonomy tree research
3. .claude/rules/arabic-scholarly-conventions.md — existing scholarly rules (for consistency check)

VERIFICATION TASK 1: OQ Calibration Accuracy (SPEC §6.18-6.23)

Each [CALIBRATED] marker claims to resolve an open question using cases from classical Islamic legal texts. Verify each claim:

§6.21 [CALIBRATED: Distinction threshold — DR37]
- Is the ثمرات الخلاف test a recognized methodology in usul al-fiqh for distinguishing real from nominal disagreement?
- Case 1 (الغصب): Is it accurate that Hanafis restrict to tangible movable property while Shafi'is extend to intangible rights?
- Case 2 (السفاهة): Is it accurate that Shafi'is include moral corruption in civil interdiction criteria while Hanafis limit to financial?
- Case 3 (النكاح): Is ملك المتعة vs ملك وطء genuinely a خلاف لفظي per classical commentators?
- Case 5 (الفقير/المسكين): Is the "total semantic inversion" characterization correct? Do all four madhabs agree on the union while disagreeing on the labels?

§6.18 [CALIBRATED: Significance threshold — DR37]
- Are the 4 new Arabic criteria (استقلال المبنى والمعنى, تغيّر الفنّ, البناء على أصل مستقلّ, قصد الإفادة والتنبيه) real classical concepts or modern inventions?
- Is the verdict on تنبيه "هذا السناد كله كوفيون" being "parasitic metadata" scholarly sound? Could a hadith specialist argue this IS independently valuable?

§6.19 [CALIBRATED: Context-fill threshold — DR37]
- Are أمن اللبس, المعلوم من السياق, البناء على الأصل real pedagogical principles from Islamic scholarly tradition?
- Is the claim about حذف being "a mark of eloquence" accurate in Arabic rhetoric?

§6.22 [CALIBRATED: Analysis authority boundary — DR37]
- Is العبرة بالمقاصد والمعاني لا بالألفاظ والمباني a real Islamic legal maxim? What is its source?
- Is the الإمامة الكبرى example (placed under كتاب الصلاة) historically accurate? Did Ibn Abidin really re-classify it?
- Is the claim about الإتلاف being independent from الغصب correct per classical fiqh?

VERIFICATION TASK 2: Batch 2 DR Prompts

For each of the 10 prompts in dr_relay_queue_batch_2.md:
- Are the Arabic terms used correctly?
- Are the scholarly references (textbook names, author names) accurate?
- Is the question well-formed for a Gemini DR session?
- Are there any factual errors in the context provided?

Pay special attention to:
- RQ-B2-001: Is the distinction between حجية فهم السلف and إجماع السلف a real scholarly debate?
- RQ-B2-009: Is the السكاكي vs القزويني framing of المجاز العقلي placement accurate?
- RQ-B2-010: Are the listed overlap topics (المبني والمعرب, التعريف والتنكير, etc.) genuinely contested between nahw and sarf?

OUTPUT FORMAT:
For each finding:
- SEVERITY: CRITICAL (scholarly error that would corrupt knowledge) / HIGH (misleading but not corrupting) / MEDIUM (imprecise but directionally correct) / LOW (style/completeness)
- SECTION: §6.XX or RQ-B2-XXX
- FINDING: what is wrong or questionable
- SCHOLARLY BASIS: cite the classical source or principle that supports your judgment
- CORRECTION: what the text should say instead (if applicable)

End with: SCHOLARLY VERDICT — are these calibrations solid enough to build the excerpting engine on?
```

---

## Dispatch Status

| Coworker | Prompt Ready | Dispatched | Response | Verdict |
|----------|-------------|------------|----------|---------|
| CC Code Reviewer | ✅ | ✅ (running) | pending | — |
| CC Scholarly Reviewer | ✅ | ✅ | **COMPLETE** | **SCHOLARLY SOUND** — 0 CRITICAL, 0 HIGH, 3 MEDIUM (all fixed) |
| Codex CLI | ✅ (above) | ⬜ owner relay | pending | — |
| Gemini CLI | ✅ (above) | ⬜ owner relay | pending | — |

### CC Scholarly Reviewer Findings (COMPLETE)

**Verdict: SCHOLARLY SOUND.** All 4 OQ calibrations correctly grounded in Islamic scholarly tradition. All 10 DR prompts well-formed.

3 MEDIUM findings — ALL FIXED:
1. §6.21 Case 5: Added Quranic hermeneutic dimension (Surah al-Kahf vs linguistic root analysis)
2. §6.22 Example 3: Added source citations (al-Asl/al-Mabsut, al-Kasani's Bada'i)
3. RQ-B2-003: Expanded scope beyond Kitab al-Tawhid to include al-Ghazali, al-Qurtubi, Ibn Qudamah

**After all 4 responses:** Synthesize findings. If any CRITICAL findings → fix before proceeding. If all PASS → Session 14 work is confirmed for building on.
